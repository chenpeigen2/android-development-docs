# Android WMS 窗口管理深度解析

> 作者：OpenClaw | 日期：2026-03-12  
> 基于源码：AOSP Android 17 / API 37，固定 tag `android-17.0.0_r1`；复核日期：2026-09-10。

## 目录

- [1. 概述](#1-概述)
  - [1.1 WMS 的核心职责](#11-wms-的核心职责)
  - [1.2 WMS 在系统中的位置](#12-wms-在系统中的位置)
- [2. WMS 架构总览](#2-wms-架构总览)
  - [2.1 WMS 内部架构](#21-wms-内部架构)
  - [2.2 窗口层级结构](#22-窗口层级结构)
  - [2.3 Z-order 详细计算逻辑](#23-z-order-详细计算逻辑)
  - [2.4 DisplayContent 多显示器架构](#24-displaycontent-多显示器架构)
  - [2.5 DisplayPolicy 显示策略](#25-displaypolicy-显示策略)
- [3. WindowToken 与 WindowState](#3-windowtoken-与-windowstate)
  - [3.1 WindowToken](#31-windowtoken)
  - [3.2 WindowState](#32-windowstate)
- [4. Surface 与 SurfaceFlinger](#4-surface-与-surfaceflinger)
  - [4.1 Surface 架构](#41-surface-架构)
  - [4.2 Surface 创建流程](#42-surface-创建流程)
  - [4.3 SurfaceFlinger 合成](#43-surfaceflinger-合成)
  - [4.4 HWC 硬件合成详解](#44-hwc-硬件合成详解)
  - [4.5 Layer 创建与管理](#45-layer-创建与管理)
  - [4.6 BufferQueue 缓冲队列](#46-bufferqueue-缓冲队列)
- [5. ViewRootImpl 绘制调度](#5-viewrootimpl-绘制调度)
  - [5.1 ViewRootImpl 概述](#51-viewrootimpl-概述)
  - [5.2 performTraversals() 流程](#52-performtraversals-流程)
- [6. Choreographer 编舞者](#6-choreographer-编舞者)
  - [6.1 Choreographer 概述](#61-choreographer-概述)
  - [6.2 Choreographer 工作流程](#62-choreographer-工作流程)
- [7. VSync 信号机制](#7-vsync-信号机制)
  - [7.1 VSync 概述](#71-vsync-概述)
  - [7.2 三缓冲机制](#72-三缓冲机制)
- [8. 窗口动画系统](#8-窗口动画系统)
  - [8.1 窗口动画类型](#81-窗口动画类型)
  - [8.2 动画执行流程](#82-动画执行流程)
  - [8.3 多窗口模式](#83-多窗口模式)
    - [8.3.1 分屏模式 (Split Screen)](#831-分屏模式-split-screen)
    - [8.3.2 自由窗口模式 (Freeform)](#832-自由窗口模式-freeform)
    - [8.3.3 画中画模式 (Picture-in-Picture, PiP)](#833-画中画模式-picture-in-picture-pip)
    - [8.3.4 多窗口模式切换流程](#834-多窗口模式切换流程)
- [9. 源码路径](#9-源码路径)
  - [9.1 WMS 源码](#91-wms-源码)
  - [9.2 客户端源码](#92-客户端源码)
- [10. 面试常见问题](#10-面试常见问题)
  - [10.1 基础问题](#101-基础问题)
  - [10.2 进阶问题](#102-进阶问题)
  - [10.3 高级问题](#103-高级问题)
- [总结](#总结)

---

## 1. 概述

**WindowManagerService (WMS)** 是 Android 系统的核心服务之一，负责管理所有窗口的创建、显示、更新、销毁，以及窗口的层级、动画和输入事件分发。

### 1.1 WMS 的核心职责

```text
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
│  │     • 提供输入窗口/触摸区域                                       │  │
│  │     • 协调焦点；实际派发由 InputDispatcher 执行                                       │  │
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

```text
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
│   │   │                    (WindowManagerImpl)                              │ │ │
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

```text
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
│   │   │   │SurfaceControl│  │InputMonitor  │  │WindowSurfacePlacer  │     │ │ │
│   │   │   │ (Surface控制)│  │ (输入监控)   │  │ (窗口布局)   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │WindowAnimator│  │TaskDisplayArea│DisplayPolicy│    │ │ │
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

窗口按照显示区域与容器树组织，而不是全局固定 Layer 0..10：壁纸区域、应用任务区域、IME 容器、系统栏/overlay 等由 DisplayArea policy 和窗口策略放置。

同一 display 中窗口的 type、token 和父子关系只是部分输入；动画过程中还可能 reparent 到 leash。层级分析应从 WindowContainer 树和实际 SurfaceControl transaction 入手，不使用历史静态十层表。

源码：[WindowManagerPolicy.java:502](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/policy/WindowManagerPolicy.java#502)。

### 2.3 Z-order 详细计算逻辑

窗口 type 的整数值不是最终 Z-order，不能用 `Z = mBaseLayer * 10000 + mSubLayer` 排序所有窗口。WindowState 构造时通过 WindowManagerPolicy 将窗口类型映射到策略层，乘 TYPE_LAYER_MULTIPLIER 并加 TYPE_LAYER_OFFSET；子窗口还由 getSubWindowLayerFromTypeLw 得到相对子层。

```text
LayoutParams.type -> WindowManagerPolicy.getWindowLayerLw
 -> WindowState.mBaseLayer（策略分区基准）
子窗口类型 -> getSubWindowLayerFromTypeLw -> mSubLayer
WindowContainer 树序 / DisplayArea policy / task / token / transition leash
 -> assignChildLayers / assignLayer / assignRelativeLayer
 -> SurfaceControl.Transaction 的层级关系 -> SurfaceFlinger 合成顺序
```

Dialog、PopupWindow、IME、系统栏的相对顺序还受所属 token、父子关系、IME target、相对层和转场 leash 影响，没有固定“Dialog 总在 Popup 之上”的数值公式。`TYPE_SUB_WAY` 不存在，TYPE_SYSTEM_ALERT 也不是 3000。

源码：[WindowState.java:1108](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowState.java#1108)；[WindowManagerPolicy.java:659](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/policy/WindowManagerPolicy.java#659)；[WindowContainer.java:2687](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowContainer.java#2687)。

### 2.4 DisplayContent 多显示器架构

```text
RootWindowContainer
  DisplayContent（一个逻辑显示）
    DisplayArea policy 构造的显示区域
      TaskDisplayArea -> root Task -> Task/TaskFragment -> ActivityRecord -> WindowState
      其他 Tokens 区域 -> WindowToken -> WindowState
      IME container -> 输入法 token / windows
```

DisplayContent 维护 DisplayInfo、显示策略、旋转、输入监控和容器布局等；不存在简单 `mWindows` 总列表加 TaskStackContainers 的现代结构。Task 的全屏/自由窗口/画中画模式与显示区域关系独立，不能把所有窗口硬塞到同一种线性树中。

`displayId=0` 是默认显示，非零显示也可能是虚拟显示或其他内置显示；ID 不编码“HDMI/外接”类型。DisplayCutout 包含 safe insets 与 bounding rects，边上的 safeInset 不等同于刘海矩形宽度。

源码：[DisplayContent.java:299](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/DisplayContent.java#299)；[DisplayArea.java:73](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/DisplayArea.java#73)。

### 2.5 DisplayPolicy 显示策略

DisplayPolicy 负责某个显示的系统栏、Insets 和窗口策略协作，例如窗口加入校验/参数调整、系统栏外观与控制目标等。它不是由 `isExpandedWindow`、`isFloatingWindow`、`isSystemWindow` 组成的通用 API 集合。

层级映射入口属于 WindowManagerPolicy；实际显示布局由 DisplayContent、WindowLayout/Insets 与容器协调。多窗口/桌面行为另有 Task、Shell 和组织器参与，不能将厂商“卷轴模式”虚构为本 tag 的 DisplayPolicy 方法。

源码：[DisplayPolicy.java:183](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/DisplayPolicy.java#183)；[WindowManagerPolicy.java:502](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/policy/WindowManagerPolicy.java#502)。

## 3. WindowToken 与 WindowState

### 3.1 WindowToken

WindowToken 是服务端 WindowContainer，持有 token 身份与窗口类型，组织其窗口。WMS 在 addWindow 时结合 session/caller 权限、窗口类型、token 的存在/归属/状态进行校验；知道一个 token 不等于拥有任意窗口管理权限。

```text
WindowToken extends WindowContainer<WindowState>
ActivityRecord extends WindowToken
```

`AppWindowToken.java` 是历史类，不是本 tag 独立当前实现。Activity 的窗口状态和绘制完成信息并入 ActivityRecord 等对象，不能保留一个虚构 AppWindowToken.activity 再与 ActivityRecord 双向解释。移除 token 涉及窗口移除和动画/同步清理，不应理解为释放一个 Java 对象就自动销毁所有 SF layer。

源码：[WindowToken.java:63](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowToken.java#63)；[ActivityRecord.java:372](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityRecord.java#372)。

### 3.2 WindowState

```text
WindowState
  mSession / mClient / mAttrs：调用会话、IWindow 回调与布局参数
  mWindowFrames 等：frame、父区域和布局状态
  mToken / mActivityRecord：窗口 token 与 Activity 归属
  mWinAnimator：服务端 surface / 绘制状态协作
  mBaseLayer / mSubLayer：策略层级信息
  WindowContainer 的 SurfaceControl：容器层控制
  client surface：客户端提交的内容层，受 useClientSurface 分支控制
```

WindowState 是系统侧窗口记录，Surface 是生产者绘图端点，SurfaceControl 是 layer 控制句柄。一个容器可以管理多个内容/效果层，三者与 compositor Layer 不形成固定一一对应。

源码：[WindowState.java:277](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowState.java#277)；[WindowState.java:3412](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowState.java#3412)。

## 4. Surface 与 SurfaceFlinger

### 4.1 Surface 架构

```text
应用渲染器 -> Surface（native ANativeWindow / producer 端点）
  -> 本地 BufferQueue -> BLASTBufferQueue（consumer）
  -> SurfaceControl.Transaction.setBuffer + fence / frame 信息
  -> SurfaceFlinger buffer layer -> HWC / GPU -> Display

WMS / Shell / 应用 SurfaceControl.Transaction
  -> 控制 layer 的 parent、可见性、裁剪、位置、alpha、Z-order 等
```

SurfaceControl 不是 Surface 绘制路径中固定夹在 native Surface 与 BufferQueue 之间的生产者；它承载 layer 控制身份。这里描述 BLAST 窗口路径，其他生产者/消费者场景可采用不同队列连接。源码：[ViewRootImpl.java:3065](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#3065)；[BLASTBufferQueue.cpp:779](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/gui/BLASTBufferQueue.cpp#779)。

### 4.2 Surface 创建流程

窗口注册与内容 surface 建立分开，并显式区分 client/server 两条路径：

```text
WindowManagerGlobal.addView -> ViewRootImpl.setView
 -> IWindowSession.addToDisplay* -> WMS.addWindow -> WindowState / input channel

WindowManager.useClientSurface() == true（普通非 locally-managed 窗口）
 ViewRootImpl.relayoutWindow -> updateSurfaceControl -> createSurfaceControl
 -> 客户端创建/复用内容 SurfaceControl，更新本地 BLAST/Surface
 -> Session.relayout2 / relayoutAsync2 携带客户端 SurfaceControl
 -> WMS.relayoutWindow -> WindowState.setClientSurface
 -> 服务端 reparent、维护绘制状态与窗口容器关系

useClientSurface() == false（保留的服务端路径）
 ViewRootImpl.relayoutWindow -> Session.relayout / relayoutAsync
 -> WMS.relayoutWindow -> createSurfaceControl
 -> WindowStateAnimator.createSurfaceLocked -> 返回 SurfaceControl
 -> 客户端依据控制句柄建立/更新 BLASTBufferQueue 与 Surface
```

同步/异步 relayout 的选择另由 canRelayoutAsync 等条件决定；不能写成所有窗口固定经过两个方法。client-surface 分支不是 WMS.createSurfaceLocked 的同义名称，WMS 仍负责窗口容器、token、布局与权限，不等于“客户端任意摆放系统窗口”。隐藏/销毁时还要释放/缓存内容层、移除 layer 或等待动画/同步清理。

源码：[ViewRootImpl.java:10083](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#10083)；[ViewRootImpl.java:10108](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#10108)；[ViewRootImpl.java:10191](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#10191)；[WindowManagerService.java:2768](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowManagerService.java#2768)；[WindowState.java:3412](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowState.java#3412)；[WindowStateAnimator.java:287](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowStateAnimator.java#287)。

### 4.3 SurfaceFlinger 合成

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SurfaceFlinger 合成流程                              │
└─────────────────────────────────────────────────────────────────────────────┘

SurfaceFlinger 职责：
1. 接收 layer 的 buffer 与 transaction
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

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HWC (Hardware Composer) 硬件合成                        │
└─────────────────────────────────────────────────────────────────────────────┘

HWC 是厂商提供的显示合成 HAL；device composition 的能力取决于显示管线实现

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
│  │  • 当前硬件/组合不支持的变换或资源超限的 Layer                               │ │
│  │  • 当前硬件不支持的混合组合                                     │ │
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
- 节省 GPU 资源（device 部分不要求 SF 客户端 GPU 合成；应用绘制仍可能使用 GPU）
- 省电（专用硬件）
- 低延迟

**Client Composition 场景：**
- 当前设备对相关旋转/镜像组合不支持
- 当前设备对相关透明混合组合不支持
- Layer 跨显示器
- YUV 格式不支持
- PixelFormat 不支持

**合成策略选择：**
```text
HWC 优先策略：
1. SurfaceFlinger 调用 HWC.validate()
2. HWC 分析所有 Layer，计算最优合成方式
3. HWC 返回合成类型标记
4. 混合场景：部分 GPU + 部分 HWC
```

### 4.5 Layer 创建与管理

Layer 管理应区分容器层、带 buffer 的内容层和动画 leash；不是一个包含 `mBufferQueue`、0..255 整数 alpha 与宽高字段的固定 Java 类。SurfaceControl alpha API 使用 0..1 浮点值，父子变换和 crop 决定实际显示范围。

创建窗口内容层时，VRI 或 WMS（按 4.2 分支）经 SurfaceControl.Builder 建立控制句柄。BLAST 使用本地 BufferQueue 接收渲染结果，再通过事务提交 buffer；因此“SurfaceFlinger 为每个窗口分配 BufferQueue 后把 IGraphicBufferProducer 返回应用”的旧图不能解释本 tag 普通窗口路径。

layer 身份的建立不等于有内容可显示：还要有有效 buffer、满足 acquire fence、可见 parent、正确 crop 和提交时序。排查黑屏应逐一检查这些边界。

源码：[ViewRootImpl.java:10083](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#10083)；[BLASTBufferQueue.cpp:779](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/gui/BLASTBufferQueue.cpp#779)。

### 4.6 BufferQueue 缓冲队列

```text
Producer（应用渲染）           BLASTBufferQueue（本地 consumer）          SF
 dequeueBuffer -> 获取可写 buffer
 渲染 -> queueBuffer --------> onFrameAvailable / acquireBuffer
                              Transaction.setBuffer -----------------> 接收 buffer/fence
                              <------- release callback/fence -------- 使用结束
                              releaseBuffer -> 后续可再次 dequeue
```

buffer 的可复用性受 producer/consumer 状态、fence 和最大在途数量约束；不能只按“显示完立即返回”理解。普通窗口 BLAST 路径中消费者是 BLAST，不是 SF 直接调用该本地队列的 acquireBuffer。队列数量由协商与管线决定，不保证全设备固定 2 或 3。

源码：[BLASTBufferQueue.cpp:779](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/gui/BLASTBufferQueue.cpp#779)。

## 5. ViewRootImpl 绘制调度

### 5.1 ViewRootImpl 概述

ViewRootImpl 是连接一棵应用 View 树、窗口 session、Surface 与输入通道的客户端对象，不是 View 子类。其顶层 View 字段是 mView，窗口回调由内部 W 实现；setView 真实签名包含 panelParentView 等参数，不能将两参数示意签名作为源码。

```text
mView / mWindowAttributes：顶层 View 与窗口参数
mWindow / mWindowSession：IWindow 回调与 IWindowSession 请求
mSurface / mSurfaceControl / BLASTBufferQueue：渲染端点与图层
mChoreographer / mHandler：帧回调与线程消息
输入 receiver / stage 链：事件派发与完成确认
```

每个独立添加的普通窗口通常有自己的 VRI；Activity 中 SurfaceView 不等于新增一个 VRI。源码：[ViewRootImpl.java:1642](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#1642)。

### 5.2 performTraversals() 流程

```text
requestLayout / invalidate 等 -> scheduleTraversals（同一轮合并）
 -> Choreographer CALLBACK_TRAVERSAL -> doTraversal -> performTraversals
 -> 按需预测量 / measureHierarchy
 -> 按需 relayoutWindow，与 WMS 协调 frame、Insets、配置及 Surface
 -> 按最终窗口尺寸再测量（需要时）-> performLayout
 -> pre-draw 检查 / 同步协调 -> performDraw
```

relayout 不是必然放在 draw 之后；没有有效 Surface 就不能完成正常绘制。invalidate 标记脏区域并调度 traversal，不是直接安排一个绕过 traversal 的 performDraw 调用。并非每次 traversal 都重新 measure/layout/draw，取决于 dirty、layoutRequested、可见性和同步状态。

源码：[ViewRootImpl.java:3924](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#3924)。

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
 * 4. 按选定帧时间线调度，不保证固定 60fps
 */
class Choreographer {
    // VSync 接收器
    private final FrameDisplayEventReceiver mDisplayEventReceiver;
    
    // 回调队列
    private final CallbackQueue[] mCallbackQueues; // 回调队列数组
    
    // 回调类型
    static final int CALLBACK_INPUT = 0;      // 输入
    static final int CALLBACK_ANIMATION = 1;  // 动画
    static final int CALLBACK_INSETS_ANIMATION = 2; // Insets 动画
    static final int CALLBACK_TRAVERSAL = 3;  // 绘制
    static final int CALLBACK_COMMIT = 4;     // 提交
    
    // 关键方法
    public static Choreographer getInstance();
    public void postCallback(int callbackType, Runnable action, Object token);
    public void postFrameCallback(FrameCallback callback);
}
```

### 6.2 Choreographer 工作流程

```text
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
3. CALLBACK_INSETS_ANIMATION - 执行 Insets 动画
4. CALLBACK_TRAVERSAL - 执行遍历
5. CALLBACK_COMMIT - 提交阶段回调，不等于 SF 已显示

时间控制：
• 16.6ms 是 60Hz 示例；实际由刷新率和所选 frame timeline 决定
• 主线程、RenderThread、GPU 与合成共享帧预算，不能把整个刷新周期都当作主线程预算
• 超时 = 掉帧 = 卡顿
```

---

## 7. VSync 信号机制

### 7.1 VSync 概述

```text
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

```text
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
2. 可能增加排队延迟；总延迟并非无条件最多 2 帧
```

---

## 8. 窗口动画系统

### 8.1 窗口动画类型

```text
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

```text
ATMS/WMS 收集 transition 参与的 Task/Activity/WindowContainer
 -> TransitionController / Transition：同步窗口状态与起止事务
 -> 向 Shell transition player 提交 TransitionInfo、start/finish transaction
 -> Shell 选择 handler/remote transition，逐帧更新 leash 的 SurfaceControl
 -> 完成回调与 finish transaction，恢复层级并清理状态
```

这是现代 Shell transitions 主线；本 tag 仍有 AppTransition/WindowAnimator 等兼容及局部窗口动画路径，不能把所有转场画成不存在的 WindowStateAnimator.prepareAnimationLocked。动画不是应用 View 重绘，每帧 SurfaceControl 变换可复用已有 buffer。

核心服务入口：[ActivityStarter.java:1770](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#1770)。

### 8.3 多窗口模式

Android 多窗口模式分为三种：分屏模式、自由窗口模式、画中画模式。

#### 8.3.1 分屏模式 (Split Screen)

```text
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
   └─► Shell task organizer 组织 stage/root task；子任务以容器关系布局

2. 调整 WindowContainer 布局
   └─► Task/WindowContainer 配置更新
   └─► 分发新配置给两个 Task

3. 焦点管理
   └─► 当前激活的 Task 接收输入事件
   └─► 多个 Activity 可同时 resumed；焦点及 top-resumed 另行切换
```

#### 8.3.2 自由窗口模式 (Freeform)

```text
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
• Manifest android:resizeableActivity / Task windowingMode（不存在 FLAG_RESIZEABLE）
• minWidth / minHeight 最小尺寸限制
• Shell bounds/resize 策略（不是通用 LayoutParams 字段）
```

#### 8.3.3 画中画模式 (Picture-in-Picture, PiP)

```text
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
   └─► ATMS/Shell 协作进入 pinned Task 模式

2. 窗口参数
   └─► WINDOWING_MODE_PINNED（不是窗口 type）
   └─► PictureInPictureParams.Builder.setAspectRatio 设置请求宽高比

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

// 请求相邻启动；只在支持的多窗口上下文生效，不保证强制进入分屏。
Intent intent = new Intent(this, TargetActivity.class);
intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_LAUNCH_ADJACENT);
startActivity(intent);
// ACTION_MANAGE_OVERLAY_SETTINGS 是悬浮窗权限设置，与进入分屏无关。
```

```text
多窗口模式切换流程：

1. 用户触发切换（长按 Home / 按钮 / PiP）
   └─► SystemUI 发送广播或调用 API

2. ActivityTaskManagerService 处理
   └─► 判断目标模式（分屏/自由/PiP）
   └─► 更新 Task 的窗口模式与 bounds

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

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WMS 源码路径                                         │
└─────────────────────────────────────────────────────────────────────────────┘

frameworks/base/services/core/java/com/android/server/wm/
├── WindowManagerService.java          # WMS 主类
├── RootWindowContainer.java           # 根窗口容器
├── DisplayContent.java                # 显示内容
├── WindowToken.java                   # 窗口令牌
├── ActivityRecord.java                # Activity 窗口令牌与状态
├── WindowState.java                   # 窗口状态
├── WindowStateAnimator.java           # 窗口动画器
├── WindowAnimator.java                # 动画管理器
├── WindowContainer.java               # 窗口容器基类
├── TransitionController.java          # 转场协调
├── InputMonitor.java                  # 输入监控
├── DisplayPolicy.java                 # 显示策略
└── AppTransition.java                 # 应用转场
```

### 9.2 客户端源码

```text
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

```text
1. 窗口管理 - 创建/显示/更新/销毁窗口
2. Surface 管理 - 分配和释放 Surface
3. 动画管理 - 窗口切换/转场动画
4. 输入事件分发 - 触摸/按键事件分发
5. 显示管理 - 多显示器/显示模式
```

**Q2: WindowToken 的作用？**

```text
1. 权限验证 - 确保有权限的客户端才能操作窗口
2. 归属标识 - 标识窗口属于哪个应用或系统组件
3. 窗口分组 - 相同 Token 的窗口可以一起管理
4. 生命周期 - Token 销毁时关联窗口也会销毁
```

**Q3: Surface 和 SurfaceFlinger 的关系？**

```text
Surface:
• 应用层的绘图表面
• 提供 Canvas 给应用绘制
• 通过 BufferQueue 与 SurfaceFlinger 通信

SurfaceFlinger:
• 系统服务，负责合成所有 Layer
• 接收 layer 的 buffer、fence 与状态事务
• 按层级合成后交给 HWC/GPU
• 输出到 Display
```

### 10.2 进阶问题

**Q4: performTraversals() 的执行流程？**

```text
requestLayout / invalidate 等 -> scheduleTraversals（同一轮合并）
 -> Choreographer CALLBACK_TRAVERSAL -> doTraversal -> performTraversals
 -> 按需预测量 / measureHierarchy
 -> 按需 relayoutWindow，与 WMS 协调 frame、Insets、配置及 Surface
 -> 按最终窗口尺寸再测量（需要时）-> performLayout
 -> pre-draw 检查 / 同步协调 -> performDraw
```

relayout 不是必然放在 draw 之后；没有有效 Surface 就不能完成正常绘制。invalidate 标记脏区域并调度 traversal，不是直接安排一个绕过 traversal 的 performDraw 调用。并非每次 traversal 都重新 measure/layout/draw，取决于 dirty、layoutRequested、可见性和同步状态。

源码：[ViewRootImpl.java:3924](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#3924)。

**Q5: Choreographer 的作用？**

```text
职责：
1. 协调动画、输入、绘制的时序
2. 接收 VSync 信号
3. 调度回调执行

回调顺序：
1. CALLBACK_INPUT - 处理输入事件
2. CALLBACK_ANIMATION - 执行动画
3. CALLBACK_INSETS_ANIMATION - 执行 Insets 动画
4. CALLBACK_TRAVERSAL - 执行遍历
5. CALLBACK_COMMIT - 提交阶段回调，不等于 SF 已显示

时间限制：
• 按所选 timeline 的 deadline 评估，60Hz 周期约 16.6ms 不是通用执行预算
• 超时 = 掉帧 = 卡顿
```

**Q6: VSync 信号机制？**

```text
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

```text
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

```text
1. 减少 overdraw (过度绘制)
   • 使用 ConstraintLayout 减少层级
   • 移除不必要的背景

2. 优化布局
   • 使用 <ViewStub> 延迟加载
   • 使用 <merge> 减少层级
   • 使用 <include> 复用布局

3. 避免主线程阻塞
   • 耗时操作放子线程
   • 使用后台 Executor/dispatcher；AsyncTask 已废弃

4. 使用 Systrace 分析
   • 定位卡顿原因
   • 优化关键路径

5. 开启硬件加速
   • GPU 加速绘制
   • 减少CPU负担
```

**Q9: Z-order 是如何计算的？**

窗口 type 的整数值不是最终 Z-order，不能用 `Z = mBaseLayer * 10000 + mSubLayer` 排序所有窗口。WindowState 构造时通过 WindowManagerPolicy 将窗口类型映射到策略层，乘 TYPE_LAYER_MULTIPLIER 并加 TYPE_LAYER_OFFSET；子窗口还由 getSubWindowLayerFromTypeLw 得到相对子层。

```text
LayoutParams.type -> WindowManagerPolicy.getWindowLayerLw
 -> WindowState.mBaseLayer（策略分区基准）
子窗口类型 -> getSubWindowLayerFromTypeLw -> mSubLayer
WindowContainer 树序 / DisplayArea policy / task / token / transition leash
 -> assignChildLayers / assignLayer / assignRelativeLayer
 -> SurfaceControl.Transaction 的层级关系 -> SurfaceFlinger 合成顺序
```

Dialog、PopupWindow、IME、系统栏的相对顺序还受所属 token、父子关系、IME target、相对层和转场 leash 影响，没有固定“Dialog 总在 Popup 之上”的数值公式。`TYPE_SUB_WAY` 不存在，TYPE_SYSTEM_ALERT 也不是 3000。

源码：[WindowState.java:1108](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowState.java#1108)；[WindowManagerPolicy.java:659](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/policy/WindowManagerPolicy.java#659)；[WindowContainer.java:2687](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowContainer.java#2687)。

**Q10: HWC 和 GPU 合成的区别？**

```text
┌──────────────┬────────────────────────┬────────────────────────┐
│     维度     │     HWC 硬件合成       │     GPU 客户端合成      │
├──────────────┼────────────────────────┼────────────────────────┤
│ 执行者       │ 显示控制器硬件         │ GPU (图形处理器)        │
│ 资源消耗     │ 低（专用硬件）         │ 高（GPU 参与）         │
│ 能耗         │ 低                    │ 高                     │
│ 延迟         │ 低                    │ 较高                   │
│ 适用场景     │ 简单平面合成           │ 当前硬件无法承载的组合（变换/透明不必然要求 GPU） │
│ 灵活性       │ 低（硬件决定）         │ 高（软件可编程）        │
└──────────────┴────────────────────────┴────────────────────────┘

SurfaceFlinger 策略：
• 优先使用 HWC（省电高性能）
• 复杂 Layer 用 GPU 合成
• 混合模式：部分 HWC + 部分 GPU
```

**Q11: BufferQueue 的工作原理？**

dequeue/queue 是生产者接口，acquire/release 是消费者接口。普通窗口的 BLASTBufferQueue 是本地消费者，再用 SurfaceControl transaction 将 buffer/fence 交给 SF；不能仍把 SF 画为直接消费同一个应用本地队列。队列数与回压策略协商，详见 4.6。

**Q12: SurfaceFlinger 合成时机？**

```text
SurfaceFlinger 在以下时机触发合成：

1. 定时刷新（VSync）
   • 60Hz/90Hz/120Hz 显示器有固定刷新周期
   • VSync 信号到来时触发合成

2. 内容更新
   • 应用提交了新 Buffer
   • 调用 eglSwapBuffers() / Surface.unlockCanvasAndPost()

3. 合成流程
   • 接收所有 Layer 的新 Buffer
   • 计算最优合成策略（HWC vs GPU）
   • 执行合成并输出到显示控制器
```

**Q13: 多窗口模式下 Activity 的生命周期？**

多窗口支持 multi-resume，非焦点不必 onPause；top-resumed 与输入焦点分别管理。仅当停止后重新显示才走 onRestart → onStart → onResume，不能写成 onStart → onRestart。PiP 的 onPictureInPictureModeChanged 描述模式变化，是否 pause/stop 及顺序受当前状态与过渡影响，不作为固定二回调公式。

**Q14: DisplayContent 和 Display 的区别？**

```text
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

一个逻辑 display 对应相应 DisplayContent；也包括虚拟显示
• 内置显示器：displayId = 0
• 其他显示器：ID 动态分配，非零不等于物理外接
```

**Q15: 为什么 Toast 使用 Handler 而不是直接显示 Window？**

普通 Toast 不要求 SYSTEM_ALERT_WINDOW，不能把 TYPE_TOAST 与悬浮窗权限混为一谈。Toast.show 经 INotificationManager 请求，现代文本 Toast 通常由 SystemUI 渲染；自定义 Toast 仍可能使用应用 TN/ToastPresenter，受后台与 target 等限制。TN Handler 将 Binder 回调切到所属 Looper 后操作 View，不是通过 WMS.addView 这一不存在的客户端 API。源码：[Toast.java:198](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/widget/Toast.java#198)。

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

*文档更新时间: 2026-09-10*
