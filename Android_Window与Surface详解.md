# Android Window 与 Surface 详解

> 审阅基线：AOSP `android-17.0.0_r1`；审阅日期：2026-09-10。正文中的调用链为固定 tag 的关键路径分析，省略代码不是可独立编译的完整 AOSP 类；产品开关、权限和设备结果另行验证。


> 作者：OpenClaw  
> 日期：2026-03-15

---

## 目录

- [1. 概述](#1-概述)
- [2. 核心概念](#2-核心概念)
  - [2.1 Window (窗口)](#21-window-窗口)
  - [2.2 Surface (绘图表面)](#22-surface-绘图表面)
  - [2.3 ViewRootImpl](#23-viewrootimpl)
- [3. Window 与 Surface 的关系](#3-window-与-surface-的关系)
  - [3.1 核心规则](#31-核心规则)
  - [3.2 架构图](#32-架构图)
- [4. WindowManager.addView 详解](#4-windowmanageraddview-详解)
  - [4.1 添加流程](#41-添加流程)
  - [4.2 代码示例](#42-代码示例)
- [5. SurfaceView 与 TextureView](#5-surfaceview-与-textureview)
  - [5.1 SurfaceView](#51-surfaceview)
  - [5.2 TextureView](#52-textureview)
  - [5.3 对比表](#53-对比表)
  - [5.4 TextureView 应用场景详解](#54-textureview-应用场景详解)
    - [场景 1：视频滤镜/特效](#场景-1视频滤镜特效)
    - [场景 2：视频弹幕](#场景-2视频弹幕)
    - [场景 3：应用内视频小窗](#场景-3应用内视频小窗)
    - [场景 4：视频截图](#场景-4视频截图)
    - [场景 5：直播推流](#场景-5直播推流)
    - [场景 6：视频转场](#场景-6视频转场)
    - [场景 7：相机预览与滤镜](#场景-7相机预览与滤镜)
    - [场景 8：系统画中画](#场景-8系统画中画)
  - [5.5 场景选择速查表](#55-场景选择速查表)
  - [5.6 核心差异总结](#56-核心差异总结)
- [6. Dialog 与 PopupWindow](#6-dialog-与-popupwindow)
  - [6.1 Dialog](#61-dialog)
  - [6.2 PopupWindow](#62-popupwindow)
- [7. 源码分析](#7-源码分析)
  - [7.1 ViewRootImpl 创建 Surface：client-surface 路径](#71-viewrootimpl-创建-surfaceclient-surface-路径)
  - [7.2 WMS 分配 Surface：仍存在的 server-surface 分支](#72-wms-分配-surface仍存在的-server-surface-分支)
  - [7.3 WindowManagerGlobal 管理 ViewRootImpl](#73-windowmanagerglobal-管理-viewrootimpl)
- [8. 验证方法](#8-验证方法)
  - [8.1 打印 ViewRootImpl 数量](#81-打印-viewrootimpl-数量)
  - [8.2 监控 Surface 创建](#82-监控-surface-创建)
  - [8.3 使用 dumpsys 查看](#83-使用-dumpsys-查看)
  - [8.4 使用 Layout Inspector](#84-使用-layout-inspector)
- [9. 常见问题](#9-常见问题)
  - [9.1 Q: 一个 Activity 有几个 Surface？](#91-q-一个-activity-有几个-surface)
  - [9.2 Q: WM.addView 添加悬浮窗会创建 Surface 吗？](#92-q-wmaddview-添加悬浮窗会创建-surface-吗)
  - [9.3 Q: PopupWindow 和 Dialog 的区别？](#93-q-popupwindow-和-dialog-的区别)
  - [9.4 Q: TextureView 为什么没有独立 Surface？](#94-q-textureview-为什么没有独立-surface)
  - [9.5 Q: SurfaceView 为什么黑屏？](#95-q-surfaceview-为什么黑屏)

---

## 1. 概述

Window 和 Surface 是 Android 显示系统的核心概念。理解它们的关系对于深入掌握 Android 渲染机制、性能优化和自定义 View 开发至关重要。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         显示系统层次                                        │
└─────────────────────────────────────────────────────────────────────────────┘

   应用层          Window / View / ViewRootImpl
       │
       │  Binder IPC
       ▼
   框架层          WindowManagerService (WMS)
       │
       │
       ▼
   系统层          SurfaceFlinger
       │
       │
       ▼
   硬件层          Hardware Composer (HWC) → 显示器

核心问题：
- Window 是什么？
- Surface 是什么？
- 它们是什么关系？
- 一个 Window 对应一个 Surface 吗？
```

---

## 2. 核心概念

### 2.1 Window (窗口)

`android.view.Window` 是应用侧窗口策略和装饰视图的抽象，Activity/Dialog 通常采用 `PhoneWindow`。WMS 管理的是服务端 `WindowState`、窗口 token 和窗口层级，不是把应用的 Window Java 对象直接放到 system_server 中。

`WindowManager.addView()` 也可以直接添加普通 View，并不要求先创建一个 PhoneWindow。PopupWindow 是典型例子：它有自己的窗口根，但自身不是 Window 子类。

| 类型 | 值 | 说明 |
|---|---|---|
| TYPE_APPLICATION | 2 | 应用窗口 |
| TYPE_APPLICATION_PANEL | 1000 | 依附父窗口的面板，PopupWindow 默认类型 |
| TYPE_APPLICATION_OVERLAY | 2038 | 特殊访问授权的应用悬浮窗 |
| TYPE_STATUS_BAR | 2000 | 系统状态栏 |
| TYPE_NAVIGATION_BAR | 2019 | 系统导航栏 |

窗口 token 用于分组、权限及生命周期关联，不应写成“每个 Window 独占一个 WindowToken”。Activity 的多个窗口可以关联同一应用 token，子窗口还涉及父窗口 IWindow/token。窗口类型、父子关系和 z-order 是另一维关系。

### 2.2 Surface (绘图表面)

Surface 是对图像缓冲生产端的句柄封装，不是“一块显存缓冲区”，也不是 SurfaceFlinger Layer 的同义词。Canvas、EGL、解码器或相机可向生产端提交 GraphicBuffer；BufferQueue 管理缓冲的取得、提交、获取与归还。

```text
producer: Canvas / EGL / decoder / camera
    -> Surface (producer-side handle)
    -> BufferQueue
        -> consumer: BLAST -> SurfaceControl.Transaction -> compositor
        or consumer: SurfaceTexture -> HWUI -> host window buffer
```

`SurfaceControl` 控制合成树节点及其几何、可见性、层级和缓冲事务。节点也可能只是 container/effect layer，没有应用直接绘制的 Surface。一个窗口可能同时有窗口容器、BLAST 内容、SurfaceView 内容、动画 leash、快照等节点。

因此 Surface、SurfaceControl、BufferQueue、WindowState、Layer 之间不是固定一对一。Java 对象释放、服务端节点移除和 BufferQueue producer 失效也不是同一个事件；排查泄漏/黑屏需要分别看生命周期和句柄是否仍有效。

### 2.3 ViewRootImpl

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ViewRootImpl                                        │
└─────────────────────────────────────────────────────────────────────────────┘

ViewRootImpl 是 View 系统的核心，连接 View 和 Window。

职责：
1. 管理 View 树的绘制 (measure/layout/draw)
2. 与 WMS 通信，管理 Window
3. 获取和管理 Surface
4. 处理输入事件
5. 管理 Choreographer，调度 VSync

关键成员：
- mView: View 树的根节点 (DecorView)
- mSurface: 绑定的 Surface
- mWindowSession: 与 WMS 的 Binder 通道
- mWindow: Window 的 IBinder 标识

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                       ViewRootImpl                                   │ │
│   │                                                                      │ │
│   │   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐   │ │
│   │   │   View    │   │  Surface  │   │  Window   │   │Choreographer│  │ │
│   │   │  (Decor)  │   │           │   │  Session  │   │           │   │ │
│   │   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘   │ │
│   │         │               │               │               │          │ │
│   │         └───────────────┴───────────────┴───────────────┘          │ │
│   │                                │                                    │ │
│   └────────────────────────────────┼────────────────────────────────────┘ │
│                                    │                                      │
│                                    ▼                                      │
│                          WindowManagerService                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Window 与 Surface 的关系

### 3.1 核心规则

对通常的非嵌入式应用窗口，一次成功的新 `WindowManagerGlobal.addView()` 会建立一个 ViewRootImpl，并通过 IWindow 与 WMS 的窗口记录关联。重复添加同一 View 会失败，token/权限失败会回滚，且在不可见或尚未遍历时不保证已经有有效绘制 Surface。

| 添加方式 | 新增 ViewRootImpl | 窗口关系 | 绘制/合成关系 |
|---|---:|---|---|
| Activity 首次显示主 DecorView | 1 | Activity 主窗口 | 可见后建立或取得窗口内容 Surface |
| 新 View 的 WM.addView | 1 | 按类型建立独立窗口记录 | 内容 surface 的创建取决于可见性与分支 |
| Dialog.show | 1 | 通常另一个应用窗口，有 PhoneWindow | 独立窗口内容 |
| PopupWindow.showAsDropDown/showAtLocation | 1 | 通常为依附宿主的子窗口，无需 PhoneWindow | 独立窗口根和窗口内容 |
| 宿主中的 SurfaceView | 0 | 仍在宿主 View 树中 | 额外内容 Surface/BLAST 子图层，不新增 WindowState |
| 宿主中的 TextureView | 0 | 仍在宿主 View 树中 | 独立 SurfaceTexture 输入，最终绘入宿主窗口 |

上表统计的是“相对已经存在的宿主新增什么”，不是宣称 Activity 永远只有一个 Layer。SurfaceView 和 TextureView 都不能按“一个 View 等于一个窗口”理解。

### 3.2 架构图

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    多 Window / 多 Surface 架构                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          应用进程                                           │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    Activity Window                                   │  │
│   │                                                                      │  │
│   │   ┌───────────────────────────────────────────────────────────────┐ │  │
│   │   │                     DecorView                                  │ │  │
│   │   │                           │                                    │ │  │
│   │   │                           ▼                                    │ │  │
│   │   │                    ┌───────────────┐                           │ │  │
│   │   │                    │  View Hierarchy│                          │ │  │
│   │   │                    │               │                           │ │  │
│   │   │                    │  ┌─────────┐  │                           │ │  │
│   │   │                    │  │TextView │  │                           │ │  │
│   │   │                    │  └─────────┘  │                           │ │  │
│   │   │                    └───────┬───────┘                           │ │  │
│   │   │                            │                                    │ │  │
│   │   └────────────────────────────┼────────────────────────────────────┘ │  │
│   │                                │                                      │  │
│   │                     ViewRootImpl #1                                   │  │
│   │                                │                                      │  │
│   └────────────────────────────────┼──────────────────────────────────────┘  │
│                                    │                                        │
│                                    │ Surface #1                             │
│                                    │ (Activity 的 Surface)                  │
│                                    │                                        │
│   ┌────────────────────────────────┼──────────────────────────────────────┐  │
│   │                 悬浮窗 Window (WM.addView)                             │  │
│   │                                │                                      │  │
│   │   ┌────────────────────────────┼────────────────────────────────────┐ │  │
│   │   │                       View  │                                    │ │  │
│   │   │                     ┌───────▼───────┐                           │ │  │
│   │   │                     │   TextView    │                           │ │  │
│   │   │                     │  "悬浮窗"     │                           │ │  │
│   │   │                     └───────────────┘                           │ │  │
│   │   │                           │                                    │ │  │
│   │   └───────────────────────────┼─────────────────────────────────────┘ │  │
│   │                               │                                       │  │
│   │                    ViewRootImpl #2                                    │  │
│   │                               │                                       │  │
│   └───────────────────────────────┼───────────────────────────────────────┘  │
│                                   │                                         │
│                                   │ Surface #2                              │
│                                   │ (悬浮窗的独立 Surface)                  │
│                                   │                                         │
└───────────────────────────────────┼─────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SurfaceFlinger                                     │
│                                                                             │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                      │
│   │  Surface #1 │   │  Surface #2 │   │  Surface #3 │   ...                │
│   │ (Activity)  │   │ (悬浮窗)    │   │ (StatusBar) │                      │
│   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                      │
│          │                 │                 │                              │
│          └─────────────────┼─────────────────┘                              │
│                            │                                                │
│                            ▼                                                │
│                    ┌─────────────┐                                         │
│                    │ 图层合成    │                                         │
│                    │ (HWC)       │                                         │
│                    └──────┬──────┘                                         │
│                           │                                                 │
│                           ▼                                                 │
│                       显示器                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. WindowManager.addView 详解

### 4.1 添加流程

```text
WindowManagerImpl.addView(view, params)
  -> WindowManagerGlobal.addView(...)
       -> validate params / duplicate view / parent window
       -> new ViewRootImpl(...)
       -> maintain mViews / mRoots / mParams
       -> root.setView(...)
            -> requestLayout(): schedule traversal
            -> IWindowSession.addToDisplayAsUser(...)
                 -> Session -> WindowManagerService.addWindow(...)
                 -> token/type/permission checks; WindowState/input setup

Choreographer traversal
  -> ViewRootImpl.performTraversals()
       -> relayoutWindow(...)
       -> client-surface or server-surface branch (section 7)
       -> updateBlastSurfaceIfNeeded()
       -> measure/layout/draw -> submit buffer
```

`addWindow()` 不是“立即把最终 Surface 返回应用”的统一步骤。窗口登记、布局协商、内容 Surface 创建及首次缓冲提交是不同阶段；WMS 的窗口容器不能与内容 BLAST layer 混淆。第 7 章分别展开 Android 17 的 client/server 分支。

`requestLayout()` 安排未来遍历，并不在当前调用栈完成绘制。首次窗口添加失败时 `WindowManagerGlobal` 会清理已建立的 root，故应观察成功添加后的状态，而不是按 addView 调用次数计数。

### 4.2 代码示例

```kotlin
// WindowManager.addView 示例
class FloatingWindowService : Service() {
    
    private lateinit var windowManager: WindowManager
    private var floatingView: View? = null
    
    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    fun showFloatingWindow() {
        if (floatingView != null) return
        check(Settings.canDrawOverlays(this)) { "需要先取得悬浮窗授权" }
        // 1. 创建 View
        val view = TextView(this).apply {
            text = "悬浮窗"
            setBackgroundColor(Color.RED)
        }
        
        // 2. 配置 LayoutParams
        val params = WindowManager.LayoutParams(
            200,  // width
            200,  // height
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,  // type
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,  // flags
            PixelFormat.TRANSLUCENT  // format
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 100
            y = 100
        }
        
        // 3. 添加到 WindowManager
        // 此时会创建：
        // - 新的 ViewRootImpl
        // - 新的 Window
        // - 可见遍历时准备窗口内容 Surface
        windowManager.addView(view, params)
        
        floatingView = view
    }
    
    override fun onDestroy() {
        hideFloatingWindow()
        super.onDestroy()
    }

    fun hideFloatingWindow() {
        floatingView?.let {
            windowManager.removeView(it)
            floatingView = null
        }
    }
}
```

---

## 5. SurfaceView 与 TextureView

### 5.1 SurfaceView

SurfaceView 是宿主 View 树里的一个 View，不调用 WindowManager.addView 创建第二个 ViewRootImpl。其 `updateSurface()` 根据窗口可见性、大小、格式和 Surface 生命周期更新子层；`createBlastSurfaceControls()` 等逻辑通过宿主 ViewRoot 的 SurfaceControl 建立子内容并使用 BLASTBufferQueue。

```text
Activity root / ViewRootImpl (one root)
  + normal View tree
  |    + SurfaceView: layout, transparent region, holder callbacks
  + window SurfaceControl subtree
       + window content
       + SurfaceView container/content/background layers as needed
            -> BLASTBufferQueue -> producer Surface
```

默认常见模式是将 SurfaceView 内容放在宿主内容下方，并在宿主相应区域“挖洞”；`setZOrderOnTop()`、media overlay 及透明度策略会改变合成关系，不能概括为永远在下方。普通 View 可覆盖默认层级的 SurfaceView，弹幕并不因此只能用 TextureView。

生产线程可独立于 UI 线程，但必须受 `surfaceCreated()` / `surfaceChanged()` / `surfaceDestroyed()` 约束。destroyed 返回前要确保生产者不再访问即将失效的 Surface；Activity 未销毁不代表该 Surface 没被重建。

Android 17 不能沿用早期“不支持动画/变换/alpha”的表格。SurfaceView 支持随宿主布局同步更新位置和变换，现代实现也处理 alpha；具体效果受子层顺序、合成方式和内容保护限制。截图可考虑 PixelCopy，安全内容仍受限制。性能需根据设备、内容格式、刷新率、HWC 合成和 GPU 带宽测量。

### 5.2 TextureView

TextureView 不新增 WMS 窗口或独立合成窗口层，但这不等于“没有自己的 Surface”。它内部有 SurfaceTexture 及对应生产接口，应用可用 `Surface(surfaceTexture)` 接解码器/相机，或通过受支持的 Canvas API 写入；消费者把内容作为纹理交给 HWUI，最后与普通 View 一起绘入宿主窗口。

```text
decoder/camera/EGL -> Surface -> SurfaceTexture input queue
                                    |
                               HWUI texture layer
                                    |
                    host ViewRootImpl window buffer -> SurfaceFlinger
```

与 View 树一起合成让裁剪、旋转、alpha 和 `getBitmap()` 等操作易于集成，但可能增加采样与 GPU 合成开销。TextureView 依赖硬件加速；不能同时让多个生产者连接同一 BufferQueue。使用 SurfaceTextureListener 管理可用、尺寸变化、更新和销毁，不要覆盖内部帧回调来抢占消费权。

### 5.3 对比表

| 特性 | SurfaceView | TextureView |
|---|---|---|
| 新增 ViewRootImpl | 不新增 | 不新增 |
| 内容路径 | 独立 Surface/BLAST 子层，可由 HWC/GPU 合成 | SurfaceTexture -> HWUI -> 宿主窗口 |
| View 叠加 | 支持，关注 z-order/透明区域 | 普通 View 树叠加 |
| 动画与 alpha | 现代实现支持，需检查合成/层级语义 | 按普通 View 变换和 alpha 集成 |
| 截图 | PixelCopy 等，受安全内容限制 | getBitmap()，可能返回 null，受内容限制 |
| 渲染线程 | 独立生产者线程，遵守 holder 生命周期 | UI 管理 View，生产者与渲染线程按管线安排 |
| 功耗/延迟 | 常适合直出视频，但不是无条件最快 | 更易集成 View 特效，额外合成需测量 |

### 5.4 TextureView 应用场景详解

#### 场景 1：视频滤镜/特效

`getBitmap()` 是截图接口，不是实时滤镜管线。每帧把纹理读回 Bitmap、CPU 处理再上传可能引入同步等待、内存分配和带宽开销。实时滤镜通常使用独立 GL/Vulkan 管线：从相机或解码器输入获取纹理，执行 shader，再输出到预览 Surface 或编码器 input Surface。

TextureView 可以作为最终预览控件，却不会自动获得滤镜功能。若只需要单张缩略图，可以在其可用时取 Bitmap，且处理 null 与尺寸无效：

```kotlin
fun capturePreview(texture: TextureView): Bitmap? {
    if (!texture.isAvailable || texture.width <= 0 || texture.height <= 0) return null
    return texture.bitmap
}
```

#### 场景 2：视频弹幕

默认 SurfaceView 层级也允许普通 View 弹幕覆盖；应根据 transform、裁剪和合成成本选择。下面是有效 XML 结构，而非把注释放在开始标签内部：

```xml
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <TextureView
        android:id="@+id/videoView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
    <TextView
        android:id="@+id/danmaku"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="弹幕示例" />
</FrameLayout>
```

将 TextureView 换成默认 z-order 的 SurfaceView 后，覆盖的 TextView 不会因“独立 Surface”必然消失。若设置 SurfaceView on-top，则需重新分析其与窗口内容的层级。

#### 场景 3：应用内视频小窗

普通 View 动画可以改变 TextureView 的位置、缩放和透明度。坐标应相对容器实际范围计算，避免把 `translationX` 设为自身宽度后整个移出可见区：

```kotlin
fun animateMiniPlayer(view: TextureView, parent: ViewGroup) {
    val scale = 0.3f
    view.pivotX = 0f
    view.pivotY = 0f
    view.animate()
        .scaleX(scale).scaleY(scale)
        .translationX((parent.width - view.width * scale).coerceAtLeast(0f))
        .translationY((parent.height - view.height * scale).coerceAtLeast(0f))
        .alpha(0.9f)
        .setDuration(300)
        .start()
}
```

隐藏或移除控件时同步停止动画、播放器和 Surface 引用。此示例只是应用内小窗，不是系统 PiP，也不是跨应用悬浮窗。

#### 场景 4：视频截图

截图是“当前纹理内容副本”，不保证是解码器精确帧时间戳。截图后文件编码写入应在工作线程处理，并限制尺寸、处理 I/O 失败。受保护的视频不能通过更换控件绕过截图策略。

```kotlin
// 在工作线程调用；bitmap 来自前面的捕获步骤。
fun writeThumbnail(bitmap: Bitmap, target: File): Boolean = runCatching {
    FileOutputStream(target).use { output ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, output)
    }
}.getOrDefault(false)
```

SurfaceView 截图应研究 PixelCopy 或生产管线自身的截图能力，不能据无 `getBitmap()` 方法推断不可截图。

#### 场景 5：直播推流

编码器的 Surface 通常是**输入生产目标**，而 TextureView 的 SurfaceTexture 是其预览消费端；把 SurfaceTexture 直接“传给编码器”并不构成 Android MediaCodec 标准编码管线。常见结构是一个渲染器把帧输出到两个目标：预览 Surface 和编码器 input Surface。两者的时间戳、背压和生命周期需要协调。

```text
camera / decoder input
  -> render/filter pipeline
       + EGL target A -> preview SurfaceView or TextureView
       + EGL target B -> MediaCodec input Surface -> encoded stream
```

SurfaceView 同样可以承担预览，控件类型并不决定能否推流。网络协议封装、音视频同步和编码器配置不由 TextureView 负责。

#### 场景 6：视频转场

淡出、换源、淡入不是真正的两个视频交叉溶解。真正 cross-fade 需要同时保留两个已准备好的内容源，并处理解码器数量、首帧到达及合成成本。单控件方案应在新源首帧回调后淡入，不能在异步 `playVideo()` 刚返回时认为新画面已准备好。

#### 场景 7：相机预览与滤镜

在 `SurfaceTextureListener.onSurfaceTextureAvailable()` 后创建预览 Surface，在尺寸变化时重建合适的相机会话/流配置。停止会话与关闭 producer 后再释放 Surface。不要在 View 中直接重设内部 SurfaceTexture 的 OnFrameAvailableListener 去读取每帧 Bitmap，这会干扰 TextureView 自身的更新职责。

要做实时滤镜，应让独立渲染器拥有输入 SurfaceTexture 和 GL 上下文，并明确在哪个线程调用 `updateTexImage()`。TextureView 只是其输出目标之一；相机 Camera2/CameraX 的具体会话流程需单独对照所用版本。

#### 场景 8：系统画中画

系统 PiP 是 Activity 的窗口模式，不等于把子 View 缩放到 0.25 倍。满足 manifest 与设备要求后，通过 Activity 的 `enterPictureInPictureMode(PictureInPictureParams)` 请求进入，并响应 PiP/可见性生命周期。SurfaceView 与 TextureView 都可用于视频 PiP。

### 5.5 场景选择速查表

| 场景 | 考虑因素 | 不应使用的绝对结论 |
|---|---|---|
| 长视频/相机预览 | 解码直出、色彩/HDR、功耗、HWC 支持 | SurfaceView 永远最快 |
| 弹幕与按钮 | 默认 z-order、普通 View 覆盖 | SurfaceView 无法叠加 |
| 复杂裁剪/转场 | View transform 或专用渲染器 | 有滤镜就必须 TextureView |
| 截图 | getBitmap/PixelCopy、保护内容、帧时序 | SurfaceView 不能截图 |
| 推流 | 编码器输入与预览双目标 | TextureView 能直接编码 |
| PiP | Activity 窗口模式和生命周期 | 缩放 View 等于系统 PiP |

### 5.6 核心差异总结

选择时先问：内容由谁生产、由谁消费、最终在哪一层合成、需要什么色彩和保护能力，以及销毁/重建时谁负责停止 producer。ViewRootImpl 数量不是两者性能差异的原因，两者均复用宿主 ViewRoot。

TextureView 更自然地参与 HWUI 的 View 合成；SurfaceView 将内容作为窗口子层交给合成器。两种方案都应测量首帧、帧率、延迟、功耗和 resize/旋转正确性，不能用未经测量的星级表替代选择依据。

## 6. Dialog 与 PopupWindow

### 6.1 Dialog

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Dialog 架构                                       │
└─────────────────────────────────────────────────────────────────────────────┘

Dialog 创建自己的 Window 和 ViewRootImpl，因此也有自己的 Surface。

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    Activity Window                                   │ │
│   │                                                                      │ │
│   │   ViewRootImpl #1  →  Surface #1                                    │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    Dialog Window                                     │ │
│   │                                                                      │ │
│   │   ViewRootImpl #2  →  Surface #2                                    │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

代码示例：
val dialog = Dialog(this)
dialog.setContentView(R.layout.dialog)
dialog.show()

// 此时创建了：
// - 新的 PhoneWindow
// - 新的 ViewRootImpl
// - 可见遍历时准备窗口内容 Surface
```

### 6.2 PopupWindow

`PopupWindow.invokePopup()` 最终调用 `mWindowManager.addView(mDecorView, p)`，所以显示成功时有自己的 ViewRootImpl 和 WMS 窗口记录。通常它用 `TYPE_APPLICATION_PANEL` 及宿主 token 形成子窗口关系，但“依附宿主”不等于“共享宿主 root 或内容 Surface”。

```text
Activity main window: DecorView -> ViewRootImpl A -> window content A
Popup child window: PopupDecorView -> ViewRootImpl B -> window content B
                      parent token / anchor / layout relationship -> Activity
```

```kotlin
val popup = PopupWindow(this).apply {
    contentView = layoutInflater.inflate(R.layout.popup, null)
    width = ViewGroup.LayoutParams.WRAP_CONTENT
    height = ViewGroup.LayoutParams.WRAP_CONTENT
    isFocusable = true
}
popup.showAsDropDown(anchorView)
// 不再需要时（包括宿主退出）显式 popup.dismiss()，清理相关监听器。
```

PopupWindow 不持有 PhoneWindow 与“不是真窗口”是两回事。Dialog 与 PopupWindow 都要管理 show/dismiss 及宿主失效；不要依赖系统清理 token 来替代应用撤销 listener 和持有的 View 引用。

## 7. 源码分析

### 7.1 ViewRootImpl 创建 Surface：client-surface 路径

Android 17 的 `ViewRootImpl.relayoutWindow()` 必须分支阅读。`WindowManager.useClientSurface()` 为真且不是 locally managed 窗口时，会先调用 `updateSurfaceControl(viewVisibility)`。这不是 WMS 先把 Surface 写回应用：

```text
relayoutWindow()
  -> useClientSurface && !locallyManaged
       -> updateSurfaceControl(visibility)
            VISIBLE + invalid handle:
              use valid cached handle OR createSurfaceControl()
            INVISIBLE:
              cache valid handle, release current reference
            other non-visible:
              release current reference
  -> getSurfaceControlForRelayout(visibility)
  -> IWindowSession.relayout2(..., surfaceControl, outResult)
       or relayoutAsync2(..., surfaceControl)
  -> Session -> WMS.relayoutWindow(...)
       -> WindowState.setClientSurface(surfaceControl)
```

`createSurfaceControl()` 创建名为 `VRI-...` 的 BLAST layer；`NOT_ADD_TO_ROOT` 防止它在尚未交给服务端组织层级时直接挂成 root。同步/异步 relayout 的选择另受 frame、configuration、sync sequence 等条件影响，不能写成始终使用异步接口。

`WindowState.setClientSurface()` 接收并校验客户端句柄，通过 transaction 将内容 reparent 到该 WindowState 的窗口容器，更新 animator 的 SurfaceControl、draw state、has-surface 和输入标记。服务端仍控制窗口层级、输入与可见性；“client surface”不是绕过 WMS 管理。

真正为 renderer 准备生产 Surface 的逻辑在 `updateBlastSurfaceIfNeeded()`：

```text
已有 BLAST queue 且关联同一 SurfaceControl:
  -> update(control, width, height, format)
否则:
  -> destroy old queue
  -> new BLASTBufferQueue(tag, updateDestinationFrame=true)
  -> setApplyToken(mBbqApplyToken)
  -> update(control, dimensions, format)
  -> createSurfaceWithHandle()
  -> mSurface.transferFrom(blastSurface)
```

`Surface` Java 对象可以早已存在而 native producer 尚未有效。SurfaceControl 与 BLAST queue 重建也可能改变 generation，影响 EGL 资源是否需要重建。排查 resize/黑屏时需观察生产端有效性和缓冲提交，不能只看 `mSurface != null`。

### 7.2 WMS 分配 Surface：仍存在的 server-surface 分支

当 `WindowManager.useClientSurface()` 为假时，该 tag 仍保留服务端创建内容层的路径：

```text
ViewRootImpl.relayoutWindow()
  -> IWindowSession.relayout(..., mRelayoutResult, mSurfaceControl)
  -> Session.relayout(...)
  -> WMS.relayoutWindow(...)
       -> shouldRelayout && outSurfaceControl != null && !useClientSurface
       -> WMS.createSurfaceControl(...)
       -> WindowStateAnimator.createSurfaceLocked()
            -> mWin.makeSurface()
                 .setParent(mWin.mSurfaceControl)
                 ...
                 .setCallsite("WindowSurfaceController")
                 .setBLASTLayer().build()
       -> copy SurfaceControl to caller result
  -> client BLAST queue creates renderer-facing Surface
```

这里返回的是 SurfaceControl/relayout 结果，不是旧版 `outOverscanInsets` 等长参数列表加 `Surface outSurface` 的接口。普通客户端仍需要 BLAST 生产路径，不能用 `outSurface.copyFrom(win.createSurfaceControl())` 冒充 17 实现。

**`WindowSurfaceController` 是遗留字符串，不是当前独立类。** 固定 tag 的 `services/core/java/com/android/server/wm/` 目录没有 `WindowSurfaceController.java`；实现持有者是 WindowStateAnimator。`setCallsite("WindowSurfaceController")` 以及同名 proto/debug 标记是诊断元数据，不会定义或实例化一个 Java 类。

这两个分支都是真实存在的 Android 17 源码，不应将 server 分支删除成“17 已不存在”，也不应把它说成唯一主链。源代码包含开关只能证明存在分支；某台 user/userdebug/OEM 设备实际采用哪条路径，还需核对产品 flag 和日志。

### 7.3 WindowManagerGlobal 管理 ViewRootImpl

`WindowManagerGlobal` 用 mViews/mRoots/mParams 维护已添加窗口根。`addView()` 在锁中检查重复、查找 panel parent、构造 root、记录集合并调用 `root.setView()`，异常时有清理逻辑。这是管理结构，不是允许应用随意修改的公开列表。

移除也不是立刻删除三个数组然后 `die()` 的固定顺序：

```text
removeView(view, immediate)
  -> findViewLocked()
  -> removeViewLocked(index, immediate)
       -> root.die(immediate)
       -> deferred ? record in mDyingViews
       -> detach view parent reference
  -> root.doDie()/dispatchDetachedFromWindow()
  -> WindowManagerGlobal.doRemoveView(root)
       -> remove matching roots/views/params/dying entries
```

是否延后与正在遍历、绘制和 immediate 条件有关。`removeView()` 返回、View detach、窗口 IPC 移除和 Surface 最后一次引用释放不能被合并成一个原子事件。输入通道、渲染器和 BLAST queue 都各有清理过程。

## 8. 验证方法

### 8.1 打印 ViewRootImpl 数量

以下仅供可访问 hidden API 的平台调试环境。普通 SDK 应用不能把反射 `WindowManagerGlobal.mRoots` 当稳定能力；Android 17 的非 SDK 限制可能拒绝访问。优先使用公开生命周期回调和 adb dumpsys。

```kotlin
fun printViewRootImplCount() {
    try {
        val clazz = Class.forName("android.view.WindowManagerGlobal")
        val getInstance = clazz.getDeclaredMethod("getInstance")
        val global = getInstance.invoke(null)
        
        val mRoots = clazz.getDeclaredField("mRoots").apply { 
            isAccessible = true 
        }
        val roots = mRoots.get(global) as ArrayList<*>
        
        Log.d("WindowSurface", "ViewRootImpl count: ${roots.size}")
        
        // 打印每个 ViewRootImpl 的信息
        for ((index, root) in roots.withIndex()) {
            val mView = root!!.javaClass.getDeclaredField("mView").apply {
                isAccessible = true
            }.get(root) as? View
            
            Log.d("WindowSurface", "[$index] View: ${mView?.javaClass?.simpleName}")
        }
        
    } catch (e: Exception) {
        e.printStackTrace()
    }
}
```

### 8.2 监控 Surface 创建

ViewRootImpl 是框架内部类，不能在普通应用中继承并把 `dispatchResized(...)` 占位方法作为可运行调试方案。SurfaceView 应使用公开 SurfaceHolder.Callback，记录 generation 与 valid；TextureView 使用 SurfaceTextureListener。

```kotlin
val callback = object : SurfaceHolder.Callback {
    override fun surfaceCreated(holder: SurfaceHolder) {
        Log.d("SurfaceDebug", "created valid=${holder.surface.isValid}")
        // 此后允许 producer 连接；不要在回调中做阻塞初始化。
    }
    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {
        Log.d("SurfaceDebug", "changed ${width}x${height}, format=$format")
    }
    override fun surfaceDestroyed(holder: SurfaceHolder) {
        // 协调 producer 停止使用 Surface；回调返回后不能继续访问。
        Log.d("SurfaceDebug", "destroyed")
    }
}
surfaceView.holder.addCallback(callback)
// 按拥有者生命周期移除 callback，并独立关闭 producer。
```

要核对窗口内容路径，则在平台调试版本给 VRI 的 create/update 和 WMS/WindowState 的 setClientSurface 加日志，关联窗口名、SurfaceControl id 与时间；只记录 resized 不等于看到了创建事件。

### 8.3 使用 dumpsys 查看

```bash
# 查看所有 Window
adb shell dumpsys window windows

# 查看所有 Surface
adb shell dumpsys SurfaceFlinger

# 查看特定应用的 Window
adb shell dumpsys window windows | grep com.example

# 输出示例：
#   Window #0 Window{abc123 com.example/com.example.MainActivity}:
#     mOwnerUid=10123
#     mPackage=com.example
#     mAttrs=WM.LayoutParams{(0,0)(fillxfill) sim=#120 ty=1 fl=#81810100}
```

### 8.4 使用 Layout Inspector

```text
Android Studio → View → Tool Windows → Layout Inspector

可以看到：
- View 层级结构
- 每个 View 的属性
- 但看不到 Surface 信息（需要 dumpsys）
```

---

## 9. 常见问题

### 9.1 Q: 一个 Activity 有几个 Surface？

没有固定总数。普通主窗口通常有一个 ViewRootImpl；添加 Dialog/PopupWindow 会新增窗口根，宿主中的 SurfaceView 不新增 root，却可新增内容子层。TextureView 也有输入 SurfaceTexture，但最终内容进入宿主窗口。动画 leash、系统启动快照和 Surface 重建会让 dumpsys 中的节点数继续变化。

### 9.2 Q: WM.addView 添加悬浮窗会创建 Surface 吗？

成功添加一个新窗口根并变为可绘制可见状态后，会按 client/server 分支准备内容 Surface。悬浮窗特殊授权来自 `TYPE_APPLICATION_OVERLAY` 的跨应用显示和安全策略，不是“因为创建 Surface 所以要权限”；普通 Activity 和 SurfaceView 同样使用 Surface，却不是同一种权限模型。

### 9.3 Q: PopupWindow 和 Dialog 的区别？

Dialog 通常持有 PhoneWindow，PopupWindow 直接管理 popup decor 并调用 WindowManager.addView。二者显示时都有独立窗口根；PopupWindow 通常使用父窗口 token、anchor 及子窗口坐标，生命周期与宿主有关联。调用方仍应显式 dismiss 并清理引用，不能把宿主销毁后的服务端兜底当成完整资源管理。

### 9.4 Q: TextureView 为什么没有独立 Surface？

问题的前提不准确。它没有独立 WMS 窗口和直接作为窗口内容的合成层，但有自己的输入缓冲管线和可封装成 Surface 的 SurfaceTexture。与 SurfaceView 的关键区别是“纹理由 HWUI 绘入宿主”而非“有无 Surface”。

### 9.5 Q: SurfaceView 为什么黑屏？

先确认 `surfaceCreated/Changed` 已到达、Surface 有效、producer 已连接并提交首帧，再检查尺寸、格式、窗口可见性、z-order、裁剪和保护内容。旋转/后台返回时要检查旧 Surface 是否已被销毁，而解码器仍在向旧句柄提交。

黑色可能是无首帧、透明区域、遮挡或无有效缓冲，不能统一用“换成 TextureView”解决。应以生命周期日志、SurfaceFlinger layer/transaction 信息和 producer 错误联合判断。本文未进行真机、模拟器或 Perfetto 采集。



**固定 tag 源码证据：**

- [Window：应用侧抽象](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/Window.java)
- [relayoutWindow / updateSurfaceControl / createSurfaceControl / updateBlastSurfaceIfNeeded](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)
- [relayout / relayout2 / relayoutAsync2](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/IWindowSession.aidl)
- [Session relayout delegation](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/Session.java)
- [relayoutWindow / createSurfaceControl](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowManagerService.java)
- [setClientSurface](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowState.java)
- [createSurfaceLocked](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowStateAnimator.java)
- [wm 目录：无 WindowSurfaceController.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/)
- [addView / removeViewLocked / doRemoveView](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/WindowManagerGlobal.java)
- [updateSurface / createBlastSurfaceControls](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/SurfaceView.java)
- [SurfaceTexture / getBitmap](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/TextureView.java)
- [invokePopup](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/widget/PopupWindow.java)
- [show / dismiss](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Dialog.java)
