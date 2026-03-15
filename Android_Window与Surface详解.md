# Android Window 与 Surface 详解

> 作者：OpenClaw  
> 日期：2026-03-15

---

## 目录

1. [概述](#1-概述)
2. [核心概念](#2-核心概念)
3. [Window 与 Surface 的关系](#3-window-与-surface-的关系)
4. [WindowManager.addView 详解](#4-windowmanageraddview-详解)
5. [SurfaceView 与 TextureView](#5-surfaceview-与-textureview)
6. [Dialog 与 PopupWindow](#6-dialog-与-popupwindow)
7. [源码分析](#7-源码分析)
8. [验证方法](#8-验证方法)
9. [常见问题](#9-常见问题)
10. [总结](#10-总结)

---

## 1. 概述

Window 和 Surface 是 Android 显示系统的核心概念。理解它们的关系对于深入掌握 Android 渲染机制、性能优化和自定义 View 开发至关重要。

```
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Window 定义                                         │
└─────────────────────────────────────────────────────────────────────────────┘

Window 是一个抽象的概念，代表一个"显示区域"。

特点：
1. Window 是 View 的容器
2. Window 由 WindowManagerService (WMS) 管理
3. 每个 Window 有对应的 WindowToken
4. Window 有类型和层级 (z-order)

Window 类型：
┌─────────────────────────────────────┬─────────────────────────────────────┐
│           类型                       │              说明                   │
├─────────────────────────────────────┼─────────────────────────────────────┤
│  TYPE_APPLICATION (2)               │  普通 Activity 窗口                 │
│  TYPE_APPLICATION_PANEL (1000)      │  面板窗口 (PopupWindow)            │
│  TYPE_APPLICATION_OVERLAY (2038)    │  悬浮窗 (需要 SYSTEM_ALERT_WINDOW) │
│  TYPE_STATUS_BAR (2000)             │  状态栏                             │
│  TYPE_NAVIGATION_BAR (2019)         │  导航栏                             │
└─────────────────────────────────────┴─────────────────────────────────────┘

Window 相关类：
- Window: 抽象类，PhoneWindow 是唯一实现
- WindowManager: 管理 Window 的接口
- WindowManagerImpl: WindowManager 的实现
- WindowManagerGlobal: 全局 Window 管理
- ViewRootImpl: Window 与 View 的桥梁
```

### 2.2 Surface (绘图表面)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Surface 定义                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Surface 是一个"绘图表面"，是真正用于绘制内容的缓冲区。

特点：
1. Surface 持有 BufferQueue
2. Canvas 绑定到 Surface 上绘制
3. Surface 由 SurfaceFlinger 管理
4. 每个 Surface 对应一个图层 (Layer)

Surface 相关类：
- Surface: 绘图表面
- SurfaceControl: Surface 的控制器
- SurfaceHolder: Surface 的持有者接口
- SurfaceTexture: 将 Surface 内容转为纹理

Surface 内部结构：
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                          Surface                                     │ │
│   │                                                                      │ │
│   │   ┌─────────────────┐    ┌─────────────────┐                       │ │
│   │   │   Canvas        │    │  BufferQueue    │                       │ │
│   │   │   (绘图接口)    │───►│  (图形缓冲区)   │                       │ │
│   │   └─────────────────┘    └─────────────────┘                       │ │
│   │                                   │                                 │ │
│   │                                   │ dequeue / queue                 │ │
│   │                                   ▼                                 │ │
│   │                          ┌─────────────────┐                       │ │
│   │                          │  GraphicBuffer  │                       │ │
│   │                          │  (显存缓冲区)   │                       │ │
│   │                          └─────────────────┘                       │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 ViewRootImpl

```
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Window 与 Surface 的对应规则                              │
└─────────────────────────────────────────────────────────────────────────────┘

核心规则：
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   每个 ViewRootImpl 对应一个 Surface                                        │
│                                                                             │
│   - ViewRootImpl 是连接 View 和 Window 的桥梁                               │
│   - 每个 ViewRootImpl 在 WMS 中有一个 WindowState                           │
│   - 每个 WindowState 对应一个 Surface (Layer)                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

对应关系表：
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   添加方式              ViewRootImpl    Window       Surface               │
│   ────────────────────────────────────────────────────────────────────────  │
│   Activity              1              1            1                      │
│   WM.addView            1              1            1                      │
│   Dialog.show()         1              1            1                      │
│   PopupWindow.show()    0 (共享)       0 (共享)     0 (共享)               │
│   SurfaceView           2              2            2                      │
│   TextureView           0 (共享)       0 (共享)     0 (共享)               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

说明：
- "1" 表示创建新的
- "0 (共享)" 表示共享宿主的
- "2" 表示创建额外的
```

### 3.2 架构图

```
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WindowManager.addView 完整流程                           │
└─────────────────────────────────────────────────────────────────────────────┘

应用进程                              系统进程 (WMS)
     │                                      │
     │  WindowManager.addView()             │
     │         │                            │
     │         ▼                            │
     │  WindowManagerImpl.addView()         │
     │         │                            │
     │         ▼                            │
     │  WindowManagerGlobal.addView()       │
     │         │                            │
     │         │  1. 创建 ViewRootImpl      │
     │         │                            │
     │         │  2. view.setLayoutParams() │
     │         │                            │
     │         │  3. root.setView(view)     │
     │         │         │                  │
     │         │         ▼                  │
     │         │  ViewRootImpl.setView()    │
     │         │         │                  │
     │         │         │  requestLayout() │
     │         │         │                  │
     │         │         │  Session.addToDisplay()
     │         │         ├─────────────────►│
     │         │         │                  │
     │         │         │                  ▼
     │         │         │         WMS.addWindow()
     │         │         │                  │
     │         │         │                  ▼
     │         │         │         创建 WindowState
     │         │         │         分配 SurfaceControl
     │         │         │         创建 Surface (Layer)
     │         │         │                  │
     │         │         │◄─────────────────┤
     │         │         │   返回 Surface   │
     │         │         │                  │
     │         │         ▼                  │
     │         │  relayoutWindow()          │
     │         │         │                  │
     │         │         │  Session.relayout()
     │         │         ├─────────────────►│
     │         │         │                  │
     │         │         │                  ▼
     │         │         │         WMS.relayoutWindow()
     │         │         │         填充 Surface
     │         │         │                  │
     │         │         │◄─────────────────┤
     │         │         │                  │
     │         │         ▼                  │
     │         │  Surface 创建完成          │
     │         │         │                  │
     │         │         ▼                  │
     │         │  performTraversals()       │
     │         │  measure/layout/draw       │
     │         │                            │
     │         ▼                            │
     │  View 显示完成                       │
     │                                      │

总结：
- 每次 WM.addView 都会创建一个新的 ViewRootImpl
- 每个 ViewRootImpl 对应一个新的 Window
- 每个 Window 对应一个新的 Surface
```

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
        // - 新的 Surface
        windowManager.addView(view, params)
        
        floatingView = view
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SurfaceView 架构                                     │
└─────────────────────────────────────────────────────────────────────────────┘

SurfaceView 会创建两个 Surface：
1. 宿主 Activity 的 Surface (SurfaceView 本身只是占位)
2. SurfaceView 的独立 Surface (真正的绘制表面)

     ┌─────────────────────────────────────────────────────────────────────┐
     │                        Window (窗口层)                               │
     │                                                                      │
     │   ┌───────────────────────────────────────────────────────────────┐ │
     │   │                    DecorView (View 层级)                       │ │
     │   │                                                                │ │
     │   │   ┌─────────────────────────────────────────────────────────┐ │ │
     │   │   │                     ContentView                         │ │ │
     │   │   │                                                          │ │ │
     │   │   │   ┌────────────────┐                                    │ │ │
     │   │   │   │  其他 View     │                                    │ │ │
     │   │   │   └────────────────┘                                    │ │ │
     │   │   │                                                          │ │ │
     │   │   │        ┌──────────────────────┐                         │ │ │
     │   │   │        │   SurfaceView        │  ← ViewRootImpl #1      │ │ │
     │   │   │        │   (占位/透明区域)    │    Surface #1 (共享)     │ │ │
     │   │   │        └──────────────────────┘                         │ │ │
     │   │   │                                                          │ │ │
     │   │   └─────────────────────────────────────────────────────────┘ │ │
     │   └───────────────────────────────────────────────────────────────┘ │
     │                                                                       │
     │   ┌───────────────────────────────────────────────────────────────┐ │
     │   │                  Surface (独立图层)                            │ │
     │   │                                                                │ │
     │   │         ┌────────────────────────────────────┐                │ │
     │   │         │     SurfaceView 的独立 Surface     │  ← ViewRootImpl #2
     │   │         │                                    │    Surface #2 (独立)
     │   │         │   • 由 SurfaceFlinger 直接管理     │                │ │
     │   │         │   • 可在子线程绘制                 │                │ │
     │   │         │   • 独立的 BufferQueue            │                │ │
     │   │         │                                    │                │ │
     │   │         └────────────────────────────────────┘                │ │
     │   │                                                                │ │
     │   └───────────────────────────────────────────────────────────────┘ │
     │                                                                       │
     └───────────────────────────────────────────────────────────────────────┘

特点：
- 拥有独立的 Surface
- 可以在子线程绘制
- 不支持动画、变换、透明度
- 性能最优
```

### 5.2 TextureView

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TextureView 架构                                     │
└─────────────────────────────────────────────────────────────────────────────┘

TextureView 不创建新的 Surface，共享宿主的 Surface。
内容渲染到 OpenGL Texture，然后合成到宿主 Surface。

     ┌─────────────────────────────────────────────────────────────────────┐
     │                        Window (窗口层)                               │
     │                                                                      │
     │   ┌───────────────────────────────────────────────────────────────┐ │
     │   │                    DecorView (View 层级)                       │ │
     │   │                                                                │ │
     │   │   ┌─────────────────────────────────────────────────────────┐ │ │
     │   │   │                     ContentView                         │ │ │
     │   │   │                                                          │ │ │
     │   │   │   ┌────────────────┐                                    │ │ │
     │   │   │   │  其他 View     │                                    │ │ │
     │   │   │   └────────────────┘                                    │ │ │
     │   │   │                                                          │ │ │
     │   │   │        ┌──────────────────────────────────────┐         │ │ │
     │   │   │        │       TextureView                    │         │ │ │
     │   │   │        │                                      │         │ │ │
     │   │   │        │   • 使用 HardwareTexture             │         │ │ │
     │   │   │        │   • 内容渲染到 GL Texture            │  ← 共享 Surface
     │   │   │        │   • 与 View 层级一起合成             │         │ │ │
     │   │   │        │   • 支持动画/变换/透明               │         │ │ │
     │   │   │        │                                      │         │ │ │
     │   │   │        └──────────────────────────────────────┘         │ │ │
     │   │   │                                                          │ │ │
     │   │   └─────────────────────────────────────────────────────────┘ │ │
     │   │                                                                │ │
     │   │            共享 Activity 的 Surface                           │ │
     │   │                                                                │ │
     │   └───────────────────────────────────────────────────────────────┘ │
     │                                                                       │
     └───────────────────────────────────────────────────────────────────────┘

特点：
- 共享宿主的 Surface
- 内容渲染到 GL Texture
- 支持动画、变换、透明度
- 可以 getBitmap() 截图
- 性能略低于 SurfaceView
```

### 5.3 对比表

| 特性 | SurfaceView | TextureView |
|------|-------------|-------------|
| Surface | 独立 Surface (2个) | 共享宿主 Surface (1个) |
| ViewRootImpl | 2 个 | 1 个 (共享) |
| 渲染线程 | 可在任意线程 | 必须主线程创建，子线程渲染 |
| 透明度 | ❌ 不支持 | ✅ 支持 |
| 动画 | ❌ 不支持 | ✅ 支持 |
| 截图 | ❌ 不支持 | ✅ getBitmap() |
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 适用场景 | 视频、相机、游戏 | 视频滤镜、动画、截图 |

---

## 6. Dialog 与 PopupWindow

### 6.1 Dialog

```
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
// - 新的 Surface
```

### 6.2 PopupWindow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PopupWindow 架构                                     │
└─────────────────────────────────────────────────────────────────────────────┘

PopupWindow 不创建新的 Window 和 Surface，而是共享宿主的。

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    Activity Window                                   │ │
│   │                                                                      │ │
│   │   ViewRootImpl #1  →  Surface #1                                    │ │
│   │                                                                      │ │
│   │   ┌─────────────────────────────────────────────────────────────┐   │ │
│   │   │                    PopupWindow                              │   │ │
│   │   │                                                             │   │ │
│   │   │   • 共享宿主的 ViewRootImpl                                 │   │ │
│   │   │   • 共享宿主的 Surface                                      │   │ │
│   │   │   • 使用独立的 ViewRootImpl (但是依附于宿主)                │   │ │
│   │   │                                                             │   │ │
│   │   └─────────────────────────────────────────────────────────────┘   │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

代码示例：
val popup = PopupWindow(this)
popup.contentView = LayoutInflater.from(this).inflate(R.layout.popup, null)
popup.showAsDropDown(anchorView)

// PopupWindow 的实现：
// - 通过 WindowManager.addView() 添加到宿主 Window
// - 但是使用特殊的 TYPE_APPLICATION_PANEL 类型
// - 实际上会创建新的 ViewRootImpl，但共享一些状态
```

**更正**：PopupWindow 实际上也会创建 ViewRootImpl 和 Surface，但它的生命周期和宿主绑定。

---

## 7. 源码分析

### 7.1 ViewRootImpl 创建 Surface

```java
// ViewRootImpl.java
public final class ViewRootImpl {
    
    // Surface 成员变量
    private final Surface mSurface = new Surface();
    
    // 在 relayoutWindow 时从 WMS 获取 Surface
    private int relayoutWindow(WindowManager.LayoutParams params, 
                               int viewVisibility, 
                               boolean insetsPending) {
        
        // 通过 Binder 调用 WMS 的 relayout
        int relayoutResult = mWindowSession.relayout(
            mWindow,                    // IWindow
            params,                     // WindowManager.LayoutParams
            (int) (mView.getMeasuredWidth() * appScale + 0.5f),
            (int) (mView.getMeasuredHeight() * appScale + 0.5f),
            viewVisibility,
            insetsPending ? WindowManagerGlobal.RELAYOUT_INSETS_PENDING : 0,
            mWinFrame,                  // out: frame
            mPendingOverscanInsets,     // out: overscanInsets
            mPendingContentInsets,      // out: contentInsets
            mPendingVisibleInsets,      // out: visibleInsets
            mPendingStableInsets,       // out: stableInsets
            mPendingOutsets,            // out: outsets
            mPendingBackDropFrame,      // out: backdropFrame
            mPendingMergedConfiguration,// out: mergedConfiguration
            mSurface                    // out: Surface ← WMS 会填充这个 Surface
        );
        
        return relayoutResult;
    }
}
```

### 7.2 WMS 分配 Surface

```java
// WindowManagerService.java
public int relayoutWindow(Session session, IWindow window, 
                          WindowManager.LayoutParams attrs,
                          int requestedWidth, int requestedHeight,
                          int viewVisibility, int flags,
                          Rect outFrame, Rect outOverscanInsets,
                          Rect outContentInsets, Rect outVisibleInsets,
                          Rect outStableInsets, Rect outOutsets,
                          Rect outBackdropFrame,
                          MergedConfiguration outMergedConfiguration,
                          Surface outSurface) {
    
    synchronized (mWindowMap) {
        // 获取 WindowState
        WindowState win = windowForClientLocked(session, window, false);
        
        if (win != null) {
            // 创建或更新 SurfaceControl
            SurfaceControl surfaceControl = win.createSurfaceControl();
            
            // 将 SurfaceControl 复制到 outSurface
            outSurface.copyFrom(surfaceControl);
        }
    }
    
    return relayoutResult;
}

// WindowState.java
SurfaceControl createSurfaceControl() {
    // 通过 SurfaceSession 创建 SurfaceControl
    return mWmService.makeSurfaceBuilder(mSession.mSurfaceSession)
            .setName(mAttrs.getTitle().toString())
            .setBufferSize(mFrame.width(), mFrame.height())
            .setFormat(mAttrs.format)
            .build();
}
```

### 7.3 WindowManagerGlobal 管理 ViewRootImpl

```java
// WindowManagerGlobal.java
public final class WindowManagerGlobal {
    
    // 存储所有 ViewRootImpl
    private final ArrayList<ViewRootImpl> mRoots = new ArrayList<>();
    
    // 存储所有 View
    private final ArrayList<View> mViews = new ArrayList<>();
    
    // 存储所有 LayoutParams
    private final ArrayList<WindowManager.LayoutParams> mParams = new ArrayList<>();
    
    public void addView(View view, ViewGroup.LayoutParams params,
                        Display display, Window parentWindow) {
        
        // 1. 创建 ViewRootImpl
        ViewRootImpl root = new ViewRootImpl(view.getContext(), display);
        
        // 2. 添加到列表
        mViews.add(view);
        mRoots.add(root);
        mParams.add(wparams);
        
        // 3. 设置 View
        root.setView(view, wparams, panelParentView);
    }
    
    public void removeView(View view, boolean immediate) {
        synchronized (mLock) {
            int index = findViewLocked(view, true);
            View viewToRemove = mViews.get(index);
            ViewRootImpl root = mRoots.get(index);
            
            // 移除
            mViews.remove(index);
            mRoots.remove(index);
            mParams.remove(index);
            
            // 销毁
            root.die(immediate);
        }
    }
}
```

---

## 8. 验证方法

### 8.1 打印 ViewRootImpl 数量

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
            val mView = root.javaClass.getDeclaredField("mView").apply {
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

```kotlin
// 在 ViewRootImpl 的子类中重写（仅用于调试）
class DebugViewRootImpl(context: Context, display: Display) : ViewRootImpl(context, display) {
    
    override fun dispatchResized(...) {
        Log.d("SurfaceDebug", "Surface resized")
        super.dispatchResized(...)
    }
}
```

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

```
Android Studio → View → Tool Windows → Layout Inspector

可以看到：
- View 层级结构
- 每个 View 的属性
- 但看不到 Surface 信息（需要 dumpsys）
```

---

## 9. 常见问题

### 9.1 Q: 一个 Activity 有几个 Surface？

```
A: 通常 1 个，但如果有 SurfaceView 则会多 1 个。

Activity 本身:
- 1 个 ViewRootImpl
- 1 个 Window
- 1 个 Surface

如果包含 SurfaceView:
- 2 个 ViewRootImpl (Activity + SurfaceView)
- 2 个 Surface (Activity 的 + SurfaceView 的独立 Surface)
```

### 9.2 Q: WM.addView 添加悬浮窗会创建 Surface 吗？

```
A: 是的，会创建新的 Surface。

流程：
1. 创建新的 ViewRootImpl
2. 创建新的 Window
3. WMS 分配新的 Surface
4. SurfaceFlinger 创建新的 Layer

这就是为什么悬浮窗需要 SYSTEM_ALERT_WINDOW 权限。
```

### 9.3 Q: PopupWindow 和 Dialog 的区别？

```
Dialog:
- 创建新的 Window
- 创建新的 ViewRootImpl
- 创建新的 Surface
- 生命周期独立管理

PopupWindow:
- 创建新的 ViewRootImpl（但依附于宿主）
- 共享宿主 Window 的一些属性
- 实际上也会创建 Surface
- 生命周期与宿主绑定
- 销毁宿主时 PopupWindow 也会销毁
```

### 9.4 Q: TextureView 为什么没有独立 Surface？

```
TextureView 的设计目标：
- 支持动画、变换、透明度
- 这些需要与 View 层级一起参与绘制
- 如果有独立 Surface，就无法参与 View 层级的变换

实现方式：
- 内容渲染到 OpenGL Texture
- Texture 作为 View 层级的一部分参与绘制
- 最终一起合成到宿主 Surface
```

### 9.5 Q: SurfaceView 为什么黑屏？

```
原因：
SurfaceView 的 Surface 位于 View 层级的"下方"
初始化时 Surface 还未准备好，显示为黑色

解决方案：
1. 设置背景色（但会影响透明度）
2. 使用 TextureView 替代
3. 等待 surfaceCreated 后再显示
```

---

##