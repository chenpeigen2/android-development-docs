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

