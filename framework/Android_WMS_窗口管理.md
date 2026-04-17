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

### 2.3 Z-order 详细计算逻辑

窗口的层级由 `mBaseLayer` 和 `mSubLayer` 决定，计算公式如下：

```java
// 位于 WindowState.java
int getBaseLayer() {
    // mBaseLayer 由窗口类型决定
    // WindowManager.LayoutParams.Type 决定了基础层级
    // 类型值越大，层级越高

    // 应用窗口: TYPE_APPLICATION (2) → mBaseLayer = 2000
    // 子窗口:   TYPE_SUB_WAY (1000) → mBaseLayer = 1000_0000
    // 系统窗口: TYPE_SYSTEM_ALERT (3000) → mBaseLayer = 3000_0000

    return mBaseLayer;
}

int getSubLayer() {
    // mSubLayer 决定同一窗口容器内的相对顺序
    // 正数: 在容器之上
    // 负数: 在容器之下
    // 例如 PopupWindow 的 mSubLayer 控制其在父窗口的上方还是下方

    return mSubLayer;
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Z-order 计算公式                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Z = mBaseLayer * 10000 + mSubLayer

示例：
• 主 Activity Window: Z = 2 * 10000 + 0 = 20000
• PopupWindow:          Z = 2 * 10000 + 1 = 20001 (在 Activity 之上)
• Dialog:               Z = 2 * 10000 + 2 = 20002 (在 Popup 之上)
• 系统 Alert:           Z = 3 * 10000 + 0 = 30000 (在所有应用窗口之上)
• 输入法:               Z = 6 * 10000 + 0 = 60000 (在 Alert 之上)

比较规则（WindowState.compareTo()）：
1. 先比较 mBaseLayer（窗口类型决定）
2. 再比较 mSubLayer（同一容器内相对位置）
3. 最后比较 mSeq（序列号，处理同一类型的多个窗口）
```

### 2.4 DisplayContent 多显示器架构

```java
/**
 * DisplayContent - 显示内容
 * 位置：frameworks/base/services/core/java/com/android/server/wm/DisplayContent.java
 *
 * 作用：
 * 1. 管理特定显示器上的所有窗口
 * 2. 维护显示器的配置信息
 * 3. 管理多显示器场景下的窗口分发
 */
class DisplayContent {
    final int mDisplayId;                           // 显示器 ID
    final Display mDisplay;                          // Display 对象
    final WindowList<WindowState> mWindows;          // 该显示器上的所有窗口
    final RootWindowContainer mRoot;                 // 根窗口容器

    // 层级根节点
    final TaskStackContainers mStackContainers;     // 任务栈容器
    final WindowToken mWallpaper;                    // 壁纸窗口
    final WindowToken mSplashscreen;                 // 启动窗口

    // 显示信息
    int mBaseDisplayWidth;                           // 基础宽度
    int mBaseDisplayHeight;                          // 基础高度
    int mRotation;                                  // 旋转角度
    int mDensity;                                    // 密度

    // 挖孔屏/刘海屏
    DisplayCutout getDisplayCutout();                // 获取挖孔区域
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DisplayContent 层级树                                   │
└─────────────────────────────────────────────────────────────────────────────┘

RootWindowContainer
    │
    └── DisplayContent 0 (内置显示器)
    │       │
    │       ├── Wallpaper (壁纸)
    │       │
    │       ├── TaskStackContainers
    │       │       ├── TaskStack (Home Stack)
    │       │       ├── TaskStack (Fullscreen Stack)
    │       │       └── TaskStack (Pinned Stack / 画中画)
    │       │
    │       ├── System Alert (系统警告)
    │       ├── Input Method (输入法)
    │       ├── Status Bar (状态栏)
    │       ├── Navigation Bar (导航栏)
    │       └── Toast (Toast)
    │
    └── DisplayContent 1..N (外接显示器)
            └── (类似结构)

显示器类型：
• 0: 内置显示器 (手机/平板)
• 1+: 外接显示器 (HDMI/USB-C/投屏)

DisplayCutout (挖孔屏)：
• left:     左侧刘海宽度
• top:      顶部刘海高度
• right:    右侧刘海宽度
• bottom:   底部刘海高度
• safeInset: 安全区域边距
```

### 2.5 DisplayPolicy 显示策略

```java
/**
 * DisplayPolicy - 显示策略
 * 位置：frameworks/base/services/core/java/com/android/server/wm/DisplayPolicy.java
 *
 * 职责：
 * 1. 窗口类型判断 - 决定窗口是否系统窗口
 * 2. 窗口动画 - 系统窗口的特殊动画
 * 3. 状态栏/导航栏 - 显示/隐藏策略
 * 4. 卷轴/分屏 - 系统 UI 的显示控制
 */
class DisplayPolicy {
    // 导航栏
    boolean isNavBarAllowedForWindow(WindowState win);
    int getNavBarPosition(int displayHeight);

    // 系统窗口
    boolean isSystemWindow(int type);
    boolean canAddInternalWindow();

    // 卷轴模式
    boolean isExpandedWindow(WindowState win);
    boolean isFloatingWindow(WindowState win);
}
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

### 4.4 HWC 硬件合成详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HWC (Hardware Composer) 硬件合成                        │
└─────────────────────────────────────────────────────────────────────────────┘

HWC 是显示硬件的抽象层，由硬件厂商实现（通常是 GPU/DSP/显示控制器）

工作流程：
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   App 1      │      │   App 2      │      │   System UI  │
│  Surface     │      │  Surface     │      │   Surface    │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────────┐
│                    SurfaceFlinger                             │
│                                                              │
│  1. 收集所有 Layer                                            │
│  2. 调用 HWC.validate() 获取合成策略                          │
│  3. HWC 返回：哪些 Layer用硬件合成，哪些用GPU                 │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              HWC Composer                              │ │
│  │                                                        │ │
│  │  Client Layers (GPU 合成):                             │ │
│  │  • 需要旋转/缩放的 Layer                               │ │
│  │  • 有透明度的 Layer                                     │ │
│  │  • HWC 不支持的格式                                     │ │
│  │    ↓ GPU 合成到临时 Buffer                              │ │
│  │                                                        │ │
│  │  Device Layers (HWC 合成):                             │ │
│  │  • 普通不透明 Layer                                     │ │
│  │  • 无需变换的 Layer                                     │ │
│  │  • 平面合成                                              │ │
│  │    ↓ 直接提交给显示控制器                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                    │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Display Controller (显示控制器)             │ │
│  │  • 接收 HWC 合成后的 Framebuffer                        │ │
│  │  • 扫描到屏幕                                             │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌──────────────┐
  │   Display    │
  │   (屏幕)     │
  └──────────────┘
```

**HWC 优势：**
- 节省 GPU 资源（GPU 不参与合成）
- 省电（专用硬件）
- 低延迟

**Client Composition 场景：**
- Layer 需要旋转/镜像
- Layer 有透明度混合
- Layer 跨显示器
- YUV 格式不支持
- PixelFormat 不支持

**合成策略选择：**
```
HWC 优先策略：
1. SurfaceFlinger 调用 HWC.validate()
2. HWC 分析所有 Layer，计算最优合成方式
3. HWC 返回合成类型标记
4. 混合场景：部分 GPU + 部分 HWC
```

### 4.5 Layer 创建与管理

```java
/**
 * Layer - SurfaceFlinger 中的图层
 * 位置：frameworks/native/services/surfaceflinger/Layer.h
 */
class Layer {
    // 缓冲区
    sp<GraphicBuffer> mBuffer;
    sp<BufferQueue> mBufferQueue;

    // 属性
    float mXPos, mYPos;           // 位置
    float mWidth, mHeight;         // 尺寸
    uint32_t mAlpha;              // 透明度 (0-255)
    uint32_t mFlags;              // 标志

    // 混合模式
    uint32_t mPremultipliedAlpha;  // 是否预乘 Alpha
    BlendMode mBlendMode;         // 混合模式

    // 变换
    uint32_t mTransform;          // 旋转/镜像
    uint32_t mCrop;               // 裁剪区域
}
```

```
Layer 创建流程：
1. WMS.relayoutWindow()
   └─► SurfaceControl.Builder.build()
       └─► SurfaceFlinger.createLayer()

2. SurfaceFlinger 分配 Layer
   └─► GraphicBufferProducer (GBP) 分配 BufferQueue
   └─► 创建 BufferLayer

3. 应用端获取 IGraphicBufferProducer
   └─► 通过 Binder 传递到应用进程
   └─► 应用通过 dequeueBuffer/queueBuffer 交换数据
```

### 4.6 BufferQueue 缓冲队列

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BufferQueue 工作流程                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐                    ┌─────────────────┐                  ┌─────────────┐
│   应用      │                    │   BufferQueue   │                  │ SurfaceFlinger│
│  (Producer) │                    │   (共享队列)    │                  │ (Consumer)   │
└──────┬──────┘                    └────────┬────────┘                  └──────┬──────┘
       │                                  │                                  │
       │ dequeueBuffer()                  │                                  │
       │ ───────────────────────────────► │                                  │
       │                                  │  分配 GraphicBuffer               │
       │ ◄─────────────────────────────── │                                  │
       │                                  │                                  │
       │ lockCanvas() / draw()            │                                  │
       │ ◄─────────────────────────────── │                                  │
       │                                  │                                  │
       │ queueBuffer()                    │                                  │
       │ ───────────────────────────────► │                                  │
       │                                  │  Buffer 可用                      │
       │                                  │ ────────────────────────────────►│
       │                                  │                                  │
       │                                  │  acquireBuffer()                  │
       │                                  │ ◄────────────────────────────────│
       │                                  │                                  │
       │                                  │  releaseBuffer()                  │
       │                                  │ ◄────────────────────────────────│
       │                                  │  (Buffer 归还队列)                │
       │                                  │                                  │
       │                                  │  dequeueBuffer()                  │
       │                                  │ ◄────────────────────────────────│
       └──────────────────────────────────┘                                  │

默认 Buffer 数量：2 (双缓冲) / 3 (三缓冲)
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

### 8.3 多窗口模式

Android 多窗口模式分为三种：分屏模式、自由窗口模式、画中画模式。

#### 8.3.1 分屏模式 (Split Screen)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        分屏模式架构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

用户进入分屏：
• 长按 Recent 键 / 启动分屏按钮
• 上半屏：Activity A
• 下半屏：Activity B
• 中间可拖动调整大小

┌─────────────────────────────────────────────────────────────────────────────┐
│                    分屏模式显示                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────┐                                  │
│  │           Activity A               │                                  │
│  │         (上半屏)                   │                                  │
│  │                                     │                                  │
│  │                                     │                                  │
│  ├─────────────────────────────────────┤  ← 拖动条 (Divider)             │
│  │           Activity B               │                                  │
│  │         (下半屏)                   │                                  │
│  │                                     │                                  │
│  └─────────────────────────────────────┘                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

分屏实现：
1. 创建两个 Task
   └─► ActivityRecord 分别属于不同的 Task
   └─► 两个 Task 在同一个 TaskStack

2. 调整 WindowContainer 布局
   └─► DisplayContent.onConfigurationChange()
   └─► 分发新配置给两个 Task

3. 焦点管理
   └─► 当前激活的 Task 接收输入事件
   └─► 非焦点 Task 收到 onPause()
```

#### 8.3.2 自由窗口模式 (Freeform)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        自由窗口模式                                          │
└─────────────────────────────────────────────────────────────────────────────┘

主要在平板/折叠屏/桌面设备上使用：
• 窗口可自由缩放
• 窗口可自由拖动
• 可叠加（类似桌面窗口）

┌─────────────────────────────────────────────────────────────────────────────┐
│                    自由窗口显示                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────────┐                                          │
│   │      Window A             │                                          │
│   │  (可拖动/缩放)            │                                          │
│   └───────────────────────────┘                                          │
│                                                                             │
│           ┌───────────────────────────┐                                  │
│           │      Window B             │                                  │
│           │                          │                                  │
│           │                          │                                  │
│           └───────────────────────────┘                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

关键参数：
• WindowManager.LayoutParams.FLAG_RESIZEABLE
• minWidth / minHeight 最小尺寸限制
• resizeDragScale 拖拽缩放系数
```

#### 8.3.3 画中画模式 (Picture-in-Picture, PiP)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        画中画模式                                           │
└─────────────────────────────────────────────────────────────────────────────┘

用户切换到其他应用时，原应用以小窗口继续播放视频

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌──────────────┐                                                        │
│   │              │                                                        │
│   │   Video      │  ← 小窗口悬浮在其他应用之上                            │
│   │   Player     │                                                        │
│   │   (PiP)      │                                                        │
│   │              │                                                        │
│   └──────────────┘                                                        │
│                                                                             │
│   其他应用 (Activity B)                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

PiP 实现：
1. 进入 PiP
   └─► Activity.enterPictureInPictureMode()
   └─► WMS 创建 Pinned TaskStack

2. 窗口参数
   └─► TYPE_PIP_APP_CONTAINER
   └─► mAspectRatio 设置宽高比

3. 交互
   └─► 触摸展开/关闭
   └─► 拖动位置
```

#### 8.3.4 多窗口模式切换流程

```java
// 进入多窗口模式
public void onMultiWindowModeChanged(boolean isInMultiWindowMode, Configuration newConfig) {
    super.onMultiWindowModeChanged(isInMultiWindowMode, newConfig);
    if (isInMultiWindowMode) {
        // 进入多窗口
    } else {
        // 退出多窗口
    }
}

// 进入分屏
Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_SETTINGS);
intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
startActivity(intent);
```

```
多窗口模式切换流程：

1. 用户触发切换（长按 Home / 按钮 / PiP）
   └─► SystemUI 发送广播或调用 API

2. ActivityTaskManagerService 处理
   └─► 判断目标模式（分屏/自由/PiP）
   └─► 修改 TaskStack 配置

3. WMS 执行窗口重排
   └─► WindowSurfacePlacer 重新布局
   └─► relayoutWindow() 更新 Surface 大小
   └─► 发送配置变更给应用

4. 应用处理
   └─► onConfigurationChanged()
   └─► onMultiWindowModeChanged()
   └─► onPictureInPictureModeChanged()
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

**Q9: Z-order 是如何计算的？**

```
Z = mBaseLayer * 10000 + mSubLayer

计算规则：
1. mBaseLayer 由窗口类型决定（TYPE_APPLICATION=2 → 基础层级 2000）
2. mSubLayer 决定同一容器内的相对顺序（正数在上，负数在下）
3. 窗口类型越大，层级越高

层级顺序（从低到高）：
壁纸 → 应用窗口 → 系统错误 → 系统警告 → 输入法 → 状态栏 → Toast
```

**Q10: HWC 和 GPU 合成的区别？**

```
┌──────────────┬────────────────────────┬────────────────────────┐
│     维度     │     HWC 硬件合成       │     GPU 客户端合成      │
├──────────────┼────────────────────────┼────────────────────────┤
│ 执行者       │ 显示控制器硬件         │ GPU (图形处理器)        │
│ 资源消耗     │ 低（专用硬件）         │ 高（GPU 参与）         │
│ 能耗         │ 低                    │ 高                     │
│ 延迟         │ 低                    │ 较高                   │
│ 适用场景     │ 简单平面合成           │ 需要变换/透明度的 Layer │
│ 灵活性       │ 低（硬件决定）         │ 高（软件可编程）        │
└──────────────┴────────────────────────┴────────────────────────┘

SurfaceFlinger 策略：
• 优先使用 HWC（省电高性能）
• 复杂 Layer 用 GPU 合成
• 混合模式：部分 HWC + 部分 GPU
```

**Q11: BufferQueue 的工作原理？**

```
BufferQueue 连接应用（Producer）和 SurfaceFlinger（Consumer）

流程：
1. dequeueBuffer() - 应用从队列获取 Buffer 绘制
2. queueBuffer() - 绘制完成后归还 Buffer
3. acquireBuffer() - SurfaceFlinger 获取 Buffer 进行合成
4. releaseBuffer() - 合成完毕后归还 Buffer 给应用

缓冲数量：
• 双缓冲（2 Buffer）：最常见，防止撕裂
• 三缓冲（3 Buffer）：减少等待，提高流畅度
```

**Q12: SurfaceFlinger 合成时机？**

```
SurfaceFlinger 在以下时机触发合成：

1. 定时刷新（VSync）
   • 60Hz/90Hz/120Hz 显示器有固定刷新周期
   • VSync 信号到来时触发合成

2. 内容更新
   • 应用提交了新 Buffer
   • 调用 eglSwapBuffers() / Surface.unlockCanvas()

3. 合成流程
   • 接收所有 Layer 的新 Buffer
   • 计算最优合成策略（HWC vs GPU）
   • 执行合成并输出到显示控制器
```

**Q13: 多窗口模式下 Activity 的生命周期？**

```
分屏模式：
• 当前 Activity：onPause()（失去焦点，但仍可见）
• 后台 Activity：onStop()

退出分屏：
• 当前 Activity：onResume()
• 后台 Activity：onStart() → onRestart() → onResume()

PiP 模式：
• 进入 PiP：onPause() → onPictureInPictureModeChanged()
• 退出 PiP：onPictureInPictureModeChanged() → onResume()

关键 API：
• onMultiWindowModeChanged() - 多窗口模式变化
• onPictureInPictureModeChanged() - PiP 模式变化
• isInMultiWindowMode() - 判断是否在多窗口模式
```

**Q14: DisplayContent 和 Display 的区别？**

```
Display：
• 应用层 API（android.view.Display）
• 获取分辨率、刷新率、密度等显示信息
• 可获取 DisplayCutout（挖孔屏信息）

DisplayContent：
• WMS 内部数据结构
• 管理特定显示器上的所有窗口
• 维护该显示器的 WindowContainer 树

关系：
DisplayContent（系统内部）
    ↓ 引用
Display（应用 API）

一个物理显示器对应一个 DisplayContent
• 内置显示器：displayId = 0
• 外接显示器：displayId = 1, 2, ...
```

**Q15: 为什么 Toast 使用 Handler 而不是直接显示 Window？**

```
Toast 的特殊性：
1. Toast 不是普通窗口
   • TYPE_TOAST（浮动窗口）
   • 需要 SYSTEM_ALERT_WINDOW 权限
   • 但系统特殊处理，不需要用户授权

2. 使用 Handler 的原因：
   • Toast 的显示和隐藏需要按顺序执行
   • 避免多个 Toast 叠加
   • 通过 Binder 异步通信，Handler 等待回调

3. 显示流程：
   Toast.show()
     └─► TN Handler.post(show())
         └─► WMS.addView() 添加 Window
             └─► 设置延时（TN.WINDOW_SHOW_TIME）
                 └─► TN Handler.post(hide())
                     └─► WMS.removeView() 移除 Window

4. 权限问题：
   • Android 4.4 以前：不需要权限
   • Android 4.4+：需要 SYSTEM_ALERT_WINDOW 权限
   • Android 6.0+：需要额外弹框授权
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
7. **多窗口模式** - 分屏/自由窗口/PiP
8. **DisplayContent** - 多显示器架构
9. **HWC 合成** - 硬件与 GPU 合成策略

掌握这些知识点对于 Android 面试和性能优化都至关重要。

---

*文档更新时间: 2026-04-17*