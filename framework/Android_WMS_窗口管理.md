# Android WMS 窗口管理深度解析

> 作者：OpenClaw | 日期：2026-03-12  
> 基于源码：Android 16 (API 36) AOSP

## 目录

1. [概述](#1-概述)
2. [WMS 架构总览](#2-wms-架构总览)
3. [WindowToken 与 WindowState](#3-windowtoken-与-windowstate)
4. [Surface 与 SurfaceFlinger](#4-surface-与-surfaceflinger)
5. [ViewRootImpl 绘制调度](#5-viewrootimpl-绘制调度)
6. [Choreographer 编舞者](#6-choreographer-编舞者)
7. [VSync 信号机制](#7-vsync-信号机制)
8. [窗口动画系统](#8-窗口动画系统)
9. [源码路径](#9-源码路径)
10. [面试常见问题](#10-面试常见问题)

---

## 1. 概述

**WindowManagerService (WMS)** 是 Android 系统的核心服务之一，负责管理所有窗口的创建、显示、更新、销毁，以及窗口的层级、动画和输入事件分发。

### 1.1 WMS 的核心职责

```
┌─────────────────────────────────────────────────────────────────┐
│                    WMS 核心职责                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  1. 窗口管理 (Window Management)                         │  │
│  │     • 窗口的创建、显示、更新、销毁                       │  │
│  │     • 窗口层级 (Z-order) 管理                           │  │
│  │     • 窗口 Token 验证                                   │  │
│  │     • 窗口尺寸计算                                      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  2. Surface 管理                                         │  │
│  │     • Surface 分配与释放                                 │  │
│  │     • SurfaceFlinger 交互                               │  │
│  │     • 图层合成协调                                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  3. 动画管理 (Animation)                                 │  │
│  │     • 窗口切换动画                                       │  │
│  │     • 转场动画                                           │  │
│  │     • 系统动画                                           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  4. 输入事件分发 (Input Event Dispatch)                  │  │
│  │     • 触摸事件分发                                       │  │
│  │     • 按键事件分发                                       │  │
│  │     • 与 IMS 协作                                        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  5. 显示管理 (Display Management)                        │  │
│  │     • 多显示器支持                                       │  │
│  │     • 显示模式切换                                       │  │
│  │     • DPI 管理                                          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 WMS 在系统中的位置

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Android 图形系统架构                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    应用层 (Application Layer)                        │ │
│   │                                                                      │ │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│   │   │   Activity   │  │  Dialog      │  │  PopupWindow │            │ │
│   │   │   Window     │  │  Window      │  │  Toast       │            │ │
│   │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │ │
│   │          │                 │                 │                      │ │
│   │          └─────────────────┼─────────────────┘                      │ │
│   │                            │                                        │ │
│   │                            ▼                                        │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                    WindowManager                              │ │ │
│   │   │                    (PhoneWindow)                              │ │ │
│   │   └──────────────────────────┬───────────────────────────────────┘ │ │
│   │                               │                                     │ │
│   └───────────────────────────────┼─────────────────────────────────────┘ │
│                                   │ Binder IPC                            │
│                                   ▼                                       │
│   ┌───────────────────────────────────────────────────────────────────────┐│
│   │                    系统服务层 (System Server)                          ││
│   │                                                                        ││
│   │   ┌────────────────────────────────────────────────────────────────┐ ││
│   │   │                    WindowManagerService                         │ ││
│   │   │                                                                 │ ││
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │ ││
│   │   │   │ WindowToken  │  │ WindowState  │  │DisplayContent│       │ ││
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘       │ ││
│   │   │                                                                 │ ││
│   │   └──────────────────────────┬─────────────────────────────────────┘ ││
│   │                               │                                       ││
│   └───────────────────────────────┼───────────────────────────────────────┘│
│                                   │                                        │
│                                   ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────────┐│
│   │                    Native 层 (SurfaceFlinger)                         ││
│   │                                                                        ││
│   │   ┌────────────────────────────────────────────────────────────────┐ ││
│   │   │                    SurfaceFlinger                               │ ││
│   │   │                                                                 │ ││
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │ ││
│   │   │   │   Surface    │  │    Layer     │  │     HWC      │       │ ││
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘       │ ││
│   │   │                                                                 │ ││
│   │   └──────────────────────────┬─────────────────────────────────────┘ ││
│   │                               │                                       ││
│   └───────────────────────────────┼───────────────────────────────────────┘│
│                                   │                                        │
│                                   ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────────┐│
│   │                    内核层 (Kernel)                                     ││
│   │                                                                        ││
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              ││
│   │   │   Framebuffer│  │     DRM      │  │    GPU       │              ││
│   │   └──────────────┘  └──────────────┘  └──────────────┘              ││
│   │                                                                        ││
│   └────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. WMS 架构总览

### 2.1 WMS 内部架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WMS 内部架构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    WindowManagerService                              │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                  核心组件                                     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │RootWindowContainer│DisplayContent│WindowToken    │     │ │ │
│   │   │   │ (根窗口容器) │  │ (显示内容)   │  │ (窗口令牌)   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │WindowState   │  │WindowStateAnimator│WindowContainer│   │ │ │
│   │   │   │ (窗口状态)   │  │ (窗口动画)   │  │(窗口容器)    │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                  辅助组件                                     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │SurfaceControl│  │InputMonitor  │  │WindowPlacer  │     │ │ │
│   │   │   │ (Surface控制)│  │ (输入监控)   │  │ (窗口布局)   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │WindowAnimator│  │TaskStackContainers│DisplayPolicy│    │ │ │
│   │   │   │ (动画管理)   │  │ (任务栈容器) │  │ (显示策略)   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 窗口层级结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          窗口层级结构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

窗口层级 (Z-order) 从下到上：

Layer 0: Wallpaper Layer (壁纸层)
Layer 1-2: Application Layer (应用层)
Layer 3-4: System Error Layer (系统错误层)
Layer 5: System Alert Layer (系统警告层)
Layer 6-7: Input Method Layer (输入法层)
Layer 8: Status Bar Layer (状态栏层)
Layer 9: Toast Layer (Toast 层)
Layer 10: Cursor Layer (光标层)

层级越高，窗口越在上层显示。
```

---

## 3. WindowToken 与 WindowState

### 3.1 WindowToken

```java
/**
 * WindowToken - 窗口令牌
 * 位置：frameworks/base/services/core/java/com/android/server/wm/WindowToken.java
 * 
 * 作用：
 * 1. 权限验证 - 确保有权限的客户端才能操作窗口
 * 2. 归属标识 - 标识窗口属于哪个应用或系统组件
 * 3. 窗口分组 - 相同 Token 的窗口可以一起管理
 * 4. 生命周期 - Token 销毁时关联窗口也会销毁
 */
class WindowToken {
    // Token 标识
    final IBinder token;              // 唯一标识
    final int windowType;             // 窗口类型
    final boolean ownerCanManageAppTokens; // 是否可以管理应用 Token
    
    // 关联的窗口
    final WindowList<WindowState> windows; // WindowState 列表
    
    // 状态
    boolean paused;                   // 是否暂停
    boolean hidden;                   // 是否隐藏
    boolean waitingToShow;            // 等待显示
    boolean clientHidden;             // 客户端隐藏
}

/**
 * AppWindowToken - 应用窗口令牌
 * 位置：frameworks/base/services/core/java/com/android/server/wm/AppWindowToken.java
 */
class AppWindowToken extends WindowToken {
    // 关联的 Activity
    final ActivityRecord activity;    // Activity 记录
    
    // 状态
    boolean lastAllWindowsHidden;     // 上次所有窗口隐藏
    boolean allDrawn;                 // 所有窗口已绘制
    boolean startingDisplayed;        // 启动窗口已显示
    
    // 动画
    boolean hasAnimation;             // 是否有动画
    boolean animating;                // 是否在动画中
}
```

### 3.2 WindowState

```java
/**
 * WindowState - 窗口状态
 * 位置：frameworks/base/services/core/java/com/android/server/wm/WindowState.java
 */
class WindowState {
    // 基本信息
    final Session mSession;                    // 会话
    final IWindow mClient;                     // 客户端接口
    final WindowManager.LayoutParams mAttrs;   // 窗口参数
    
    // 窗口尺寸
    int mFrameLeft, mFrameTop, mFrameRight, mFrameBottom;
    
    // 窗口状态
    boolean mHasSurface;                       // 是否有 Surface
    boolean mVisible;                          // 是否可见
    boolean mDrawPending;                      // 绘制等待中
    boolean mHasDrawn;                         // 已绘制
    
    // 动画
    WindowStateAnimator mWinAnimator;          // 窗口动画器
    
    // 层级
    int mBaseLayer;                            // 基础层级
    int mSubLayer;                             // 子层级
    
    // Surface
    SurfaceControl mSurfaceControl;            // Surface 控制
    
    // 关联
    WindowToken mToken;                        // 所属 Token
    AppWindowToken mAppToken;                  // 所属 AppToken
}
```

---

## 4. Surface 与 SurfaceFlinger

### 4.1 Surface 架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Surface 架构                                         │
└─────────────────────────────────────────────────────────────────────────────┘

应用层 (Java)
    │
    ▼
Surface (Java API)
    │
    │ JNI
    ▼
android::Surface (Native C++)
    │
    ▼
SurfaceControl (Native)
    │
    ▼
BufferQueue (图形缓冲队列)
    │
    │ Binder IPC
    ▼
SurfaceFlinger
    │
    ├─► Layer (图层)
    ├─► Texture (纹理)
    └─► Display (显示设备)
```

### 4.2 Surface 创建流程

```
1. 应用调用 addView()
   └─► WindowManager.addView()
       └─► ViewRootImpl.setView()

2. ViewRootImpl 请求 WMS
   └─► Session.addToDisplay()
       └─► WMS.addWindow()

3. WMS 创建 WindowState
   └─► 创建 WindowToken (如果需要)
   └─► 分配窗口层级

4. WMS 创建 Surface
   └─► relayoutWindow()
       └─► WindowStateAnimator.createSurfaceLocked()
           └─► SurfaceControl.Builder.build()

5. SurfaceControl 与 SurfaceFlinger 通信
   └─► SurfaceFlinger.createLayer()
       └─► 创建 Layer 和 BufferQueue

6. 返回 Surface 给应用
   └─► 应用获得 Surface
       └─► 可以通过 Canvas 绘制
```

### 4.3 SurfaceFlinger 合成

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SurfaceFlinger 合成流程                              │
└─────────────────────────────────────────────────────────────────────────────┘

SurfaceFlinger 职责：
1. 接收各应用的 Surface (Layer)
2. 按层级顺序合成
3. 交给 HWC (Hardware Composer) 或 GPU 合成
4. 输出到 Display

合成类型：
• Device Composition (HWC) - 硬件合成，省电
• Client Composition (GPU) - GPU 合成，耗电

合成流程：
Layer 1 (App A) ──┐
Layer 2 (App B) ──┼──► SurfaceFlinger ──► HWC/GPU ──► Display
Layer 3 (Status) ─┘
```

---

## 5. ViewRootImpl 绘制调度

### 5.1 ViewRootImpl 概述

```java
/**
 * ViewRootImpl - View 树的根
 * 位置：frameworks/base/core/java/android/view/ViewRootImpl.java
 * 
 * 职责：
 * 1. 管理 DecorView
 * 2. 与 WMS 通信
 * 3. 调度 measure/layout/draw
 * 4. 处理输入事件
 * 5. 管理窗口尺寸
 */
class ViewRootImpl {
    // View 树
    final View mRoot;                         // DecorView
    
    // 窗口
    final IWindow mWindow;                    // 窗口接口
    final Surface mSurface;                   // Surface
    
    // 布局参数
    WindowManager.LayoutParams mWindowAttributes;
    
    // 尺寸
    int mWidth, mHeight;                      // 窗口尺寸
    
    // 状态
    boolean mFirst;                           // 第一次
    boolean mLayoutRequested;                 // 请求布局
    boolean mFullRedrawNeeded;                // 需要完全重绘
    
    // Handler
    final Choreographer mChoreographer;       // 编舞者
    
    // 关键方法
    void setView(View view, WindowManager.LayoutParams attrs);
    void performTraversals();                 // 核心：执行遍历
}
```

### 5.2 performTraversals() 流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        performTraversals() 流程                             │
└─────────────────────────────────────────────────────────────────────────────┘

performTraversals() {
    
    1. 预测量 (Predictive Measurement)
       └─► getRootMeasureSpec()
           └─► 根据 WindowManager.LayoutParams 计算MeasureSpec
    
    2. 测量 (Measure)
       └─► measureHierarchy()
           ├─► performMeasure() → onMeasure()
           └─► 可能多次测量以优化
    
    3. 布局 (Layout)
       └─► performLayout()
           └─► layout() → onLayout()
    
    4. 绘制 (Draw)
       └─► performDraw()
           └─► draw() → onDraw()
               ├─► 绘制背景
               ├─► 绘制内容
               ├─► 绘制子 View
               └─► 绘制装饰
    
    5. 与 WMS 通信
       └─► relayoutWindow()
           └─► 更新 Surface
}

触发时机：
• requestLayout() → 调度 performTraversals()
• invalidate() → 调度 performDraw()
• requestFocus() → 调度 performTraversals()
```

---

## 6. Choreographer 编舞者

### 6.1 Choreographer 概述

```java
/**
 * Choreographer - 编舞者
 * 位置：frameworks/base/core/java/android/view/Choreographer.java
 * 
 * 职责：
 * 1. 协调动画、输入、绘制的时序
 * 2. 接收 VSync 信号
 * 3. 调度回调执行
 * 4. 保证流畅的 60fps 显示
 */
class Choreographer {
    // VSync 接收器
    private final FrameDisplayEventReceiver mDisplayEventReceiver;
    
    // 回调队列
    private final CallbackQueue[] mCallbackQueues; // 回调队列数组
    
    // 回调类型
    static final int CALLBACK_INPUT = 0;      // 输入
    static final int CALLBACK_ANIMATION = 1;  // 动画
    static final int CALLBACK_TRAVERSAL = 2;  // 绘制
    static final int CALLBACK_COMMIT = 3;     // 提交
    
    // 关键方法
    public static Choreographer getInstance();
    public void postCallback(int callbackType, Runnable action, Object token);
    public void postFrameCallback(FrameCallback callback);
}
```

### 6.2 Choreographer 工作流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Choreographer 工作流程                               │
└─────────────────────────────────────────────────────────────────────────────┘

                VSync 信号 (16.6ms @ 60Hz)
                       │
                       ▼
              ┌─────────────────┐
              │  Choreographer  │
              │  (编舞者)       │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
   ┌─────────────┐┌─────────────┐┌─────────────┐
   │   INPUT     ││  ANIMATION  ││  TRAVERSAL  │
   │   输入      ││   动画      ││  绘制       │
   │             ││             ││             │
   │ 处理触摸    ││ 更新动画    ││ measure/    │
   │ 处理按键    ││ 计算属性    ││ layout/draw │
   └─────────────┘└─────────────┘└─────────────┘

执行顺序：
1. CALLBACK_INPUT - 处理输入事件
2. CALLBACK_ANIMATION - 执行动画
3. CALLBACK_TRAVERSAL - 执行绘制
4. CALLBACK_COMMIT - 提交帧

时间控制：
• 每 16.6ms 一个 VSync 信号
• 所有回调必须在 16.6ms 内完成
• 超时 = 掉帧 = 卡顿
```

---

## 7. VSync 信号机制

### 7.1 VSync 概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VSync 信号机制                                       │
└─────────────────────────────────────────────────────────────────────────────┘

VSync (Vertical Synchronization) - 垂直同步信号

作用：
1. 同步显示刷新
2. 防止画面撕裂
3. 提供绘制时序

频率：
• 60Hz 显示器: 16.6ms/帧
• 90Hz 显示器: 11.1ms/帧
• 120Hz 显示器: 8.3ms/帧

流程：
Display (显示器)
    │
    │ 发出 VSync 信号
    ▼
SurfaceFlinger
    │
    │ 分发 VSync
    ▼
Choreographer
    │
    │ 调度回调
    ▼
应用线程
    │
    ├─► 处理输入
    ├─► 执行动画
    └─► 执行绘制
        │
        ▼
    Surface (绘制完成)
        │
        ▼
    SurfaceFlinger (合成)
        │
        ▼
    Display (显示)
```

### 7.2 三缓冲机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        三缓冲机制                                           │
└─────────────────────────────────────────────────────────────────────────────┘

缓冲区：
• Buffer A - 正在显示
• Buffer B - 准备显示
• Buffer C - 正在绘制

流程：
Frame 1: App 绘制到 Buffer A → Display 显示 Buffer A
Frame 2: App 绘制到 Buffer B → Display 显示 Buffer B
Frame 3: App 绘制到 Buffer C → Display 显示 Buffer C

优势：
1. 减少等待时间
2. 提高流畅度
3. 允许一定程度的延迟

劣势：
1. 增加内存占用
2. 增加延迟 (最多 2 帧)
```

---

## 8. 窗口动画系统

### 8.1 窗口动画类型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        窗口动画类型                                         │
└─────────────────────────────────────────────────────────────────────────────┘

1. Activity 转场动画
   • overridePendingTransition()
   • ActivityOptions.makeCustomAnimation()
   • 共享元素转场 (Shared Element)

2. 窗口动画
   • WindowAnimation
   • AppTransition
   • AppTransitionAnimationSpec

3. 系统动画
   • 启动动画 (Splash Screen)
   • 旋转动画 (Rotation Animation)
   • 分屏动画 (Split Screen)
```

### 8.2 动画执行流程

```
1. 动画启动
   └─► AppTransition.notifyAppTransitionStartingLocked()

2. WMS 准备动画
   └─► WindowStateAnimator.prepareAnimationLocked()
       └─► 创建 Animation 对象

3. 动画更新
   └─► WindowAnimator.animate()
       └─► 每帧更新窗口位置/透明度/缩放

4. 动画结束
   └─► WindowStateAnimator.onAnimationFinished()
       └─► 清理动画状态
```

---

## 9. 源码路径

### 9.1 WMS 源码

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WMS 源码路径                                         │
└─────────────────────────────────────────────────────────────────────────────┘

frameworks/base/services/core/java/com/android/server/wm/
├── WindowManagerService.java          # WMS 主类
├── RootWindowContainer.java           # 根窗口容器
├── DisplayContent.java                # 显示内容
├── WindowToken.java                   # 窗口令牌
├── AppWindowToken.java                # 应用窗口令牌
├── WindowState.java                   # 窗口状态
├── WindowStateAnimator.java           # 窗口动画器
├── WindowAnimator.java                # 动画管理器
├── WindowContainer.java               # 窗口容器基类
├── SurfaceControl.java                # Surface 控制
├── InputMonitor.java                  # 输入监控
├── DisplayPolicy.java                 # 显示策略
└── AppTransition.java                 # 应用转场
```

### 9.2 客户端源码

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        客户端源码路径                                       │
└─────────────────────────────────────────────────────────────────────────────┘

frameworks/base/core/java/android/view/
├── ViewRootImpl.java                  # View 树根
├── Choreographer.java                 # 编舞者
├── Surface.java                       # Surface (Java)
├── SurfaceControl.java                # Surface 控制
├── WindowManager.java                 # WindowManager 接口
├── WindowManagerImpl.java             # WindowManager 实现
├── WindowManagerGlobal.java           # WindowManager 全局
├── IWindow.aidl                       # 窗口 AIDL 接口
└── IWindowSession.aidl                # 窗口会话 AIDL

frameworks/base/core/java/android/app/
├── Activity.java                      # Activity
├── Dialog.java                        # Dialog
└── ProgressDialog.java                # ProgressDialog
```

---

## 10. 面试常见问题

### 10.1 基础问题

**Q1: WMS 的职责是什么？**

```
1. 窗口管理 - 创建/显示/更新/销毁窗口
2. Surface 管理 - 分配和释放 Surface
3. 动画管理 - 窗口切换/转场动画
4. 输入事件分发 - 触摸/按键事件分发
5. 显示管理 - 多显示器/显示模式
```

**Q2: WindowToken 的作用？**

```
1. 权限验证 - 确保有权限的客户端才能操作窗口
2. 归属标识 - 标识窗口属于哪个应用或系统组件
3. 窗口分组 - 相同 Token 的窗口可以一起管理
4. 生命周期 - Token 销毁时关联窗口也会销毁
```

**Q3: Surface 和 SurfaceFlinger 的关系？**

```
Surface:
• 应用层的绘图表面
• 提供 Canvas 给应用绘制
• 通过 BufferQueue 与 SurfaceFlinger 通信

SurfaceFlinger:
• 系统服务，负责合成所有 Layer
• 接收各应用的 Surface
• 按层级合成后交给 HWC/GPU
• 输出到 Display
```

### 10.2 进阶问题

**Q4: performTraversals() 的执行流程？**

```
1. 预测量 - 计算MeasureSpec
2. 测量 - measureHierarchy() → performMeasure()
3. 布局 - performLayout()
4. 绘制 - performDraw()
5. 通信 - relayoutWindow() 与 WMS 通信

触发时机：
• requestLayout() → 调度 performTraversals()
• invalidate() → 调度 performDraw()
```

**Q5: Choreographer 的作用？**

```
职责：
1. 协调动画、输入、绘制的时序
2. 接收 VSync 信号
3. 调度回调执行

回调顺序：
1. CALLBACK_INPUT - 处理输入事件
2. CALLBACK_ANIMATION - 执行动画
3. CALLBACK_TRAVERSAL - 执行绘制
4. CALLBACK_COMMIT - 提交帧

时间限制：
• 必须在 16.6ms 内完成 (60Hz)
• 超时 = 掉帧 = 卡顿
```

**Q6: VSync 信号机制？**

```
VSync (垂直同步信号):
• 由显示器发出
• 60Hz: 16.6ms/帧
• 90Hz: 11.1ms/帧
• 120Hz: 8.3ms/帧

流程：
Display → SurfaceFlinger → Choreographer → 应用

作用：
1. 同步显示刷新
2. 防止画面撕裂
3. 提供绘制时序
```

### 10.3 高级问题

**Q7: 为什么 requestLayout() 不会立即执行？**

```
原因：
1. requestLayout() 只是标记需要布局
2. 通过 Choreographer 调度到下一个 VSync 执行
3. 避免频繁布局造成性能问题

流程：
requestLayout() 
  → scheduleTraversals()
    → mChoreographer.postCallback()
      → 等待 VSync
        → performTraversals()
```

**Q8: 如何优化 UI 卡顿？**

```
1. 减少 overdraw (过度绘制)
   • 使用 ConstraintLayout 减少层级
   • 移除不必要的背景
   
2. 优化布局
   • 使用 <ViewStub> 延迟加载
   • 使用 <merge> 减少层级
   • 使用 <include> 复用布局
   
3. 避免主线程阻塞
   • 耗时操作放子线程
   • 使用 AsyncTask/Coroutines
   
4. 使用 Systrace 分析
   • 定位卡顿原因
   • 优化关键路径
   
5. 开启硬件加速
   • GPU 加速绘制
   • 减少CPU负担
```

---

## 总结

本文详细讲解了 Android WMS (WindowManagerService) 的核心知识点，包括：

1. **WMS 架构** - 窗口管理核心服务
2. **WindowToken/WindowState** - 窗口标识与状态
3. **Surface/SurfaceFlinger** - 图形系统架构
4. **ViewRootImpl** - View 树绘制调度
5. **Choreographer** - 编舞者与 VSync
6. **窗口动画** - 转场动画系统

掌握这些知识点对于 Android 面试和性能优化都至关重要。

---

*文档更新时间: 2026-03-12*