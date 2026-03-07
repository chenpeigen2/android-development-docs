# Android View 绘制流程完全指南

> 作者：OpenClaw | 日期：2026-03-07

## 目录

1. [概述](#1-概述)
2. [整体架构](#2-整体架构)
3. [View 绘制流程详解](#3-view-绘制流程详解)
4. [Measure 测量流程](#4-measure-测量流程)
5. [Layout 布局流程](#5-layout-布局流程)
6. [Draw 绘制流程](#6-draw-绘制流程)
7. [事件分发机制](#7-事件分发机制)
8. [自定义 View](#8-自定义-view)
9. [性能优化](#9-性能优化)
10. [总结](#10-总结)

---

## 1. 概述

View 是 Android UI 的基本构建块，理解 View 的绘制流程对于创建高性能、流畅的用户界面至关重要。

本文详细讲解从 View 创建到最终显示在屏幕上的完整流程。

---

## 2. 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          View 绘制整体架构                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         应用进程                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Activity                                                                  │
│     │                                                                       │
│     ▼                                                                       │
│  Window (PhoneWindow)                                                     │
│     │                                                                       │
│     ▼                                                                       │
│  DecorView (ViewGroup)                                                    │
│     │                                                                       │
│     ├───► LinearLayout/RelativeLayout/ConstraintLayout (ViewGroup)        │
│     │         │                                                            │
│     │         ▼                                                            │
│     │     TextView, ImageView, Button (View)                             │
│     │                                                                       │
│     ▼                                                                       │
│  WindowManager                                                             │
│     │                                                                       │
│     ▼                                                                       │
│  WindowManagerGlobal                                                       │
│     │                                                                       │
│     ▼                                                                       │
│  ViewRootImpl                                                             │
│     │                                                                       │
│     ├───► performTraversals()                                             │
│     │         │                                                            │
│     │         ├───► performMeasure() ──► measure() ──► onMeasure()      │
│     │         │                                                            │
│     │         ├───► performLayout() ──► layout() ──► onLayout()          │
│     │         │                                                            │
│     │         └───► performDraw() ──► draw() ──► onDraw()               │
│     │                                                                       │
│     ▼                                                                       │
│  Choreographer (帧率调度)                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ WindowManager.addView()
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         系统 (System Server)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  WindowManagerService (WMS)                                               │
│     │                                                                       │
│     │ 1. 创建 WindowState                                                  │
│     │ 2. 分配 Surface                                                     │
│     │ 3. 管理窗口层级                                                     │
│     │                                                                       │
│     ▼                                                                       │
│  SurfaceFlinger (显示合成)                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. WindowManager 核心作用

### 2.1 WindowManager 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WindowManager 架构                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         应用进程                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────┐                │
│  │                  WindowManager                        │                │
│  │                                                      │                │
│  │  public interface WindowManager {                   │                │
│  │      void addView(View view, ViewGroup.LayoutParams params);       │                │
│  │      void updateViewLayout(View view, ViewGroup.LayoutParams params); │            │
│  │      void removeView(View view);                  │                │
│  │  }                                               │                │
│  └───────────────────────┬───────────────────────────┘                │
│                          │                                               │
│                          ▼                                               │
│  ┌─────────────────────────────────────────────────────┐                │
│  │              WindowManagerImpl                       │                │
│  │                                                      │                │
│  │  - 实现 WindowManager 接口                         │                │
│  │  - 持有 WindowManagerGlobal 单例                   │                │
│  └───────────────────────┬───────────────────────────┘                │
│                          │                                               │
│                          ▼                                               │
│  ┌─────────────────────────────────────────────────────┐                │
│  │              WindowManagerGlobal                    │                │
│  │                                                      │                │
│  │  - 管理所有 Window 的 View                         │                │
│  │  - 创建 ViewRootImpl                              │                │
│  │  - 与 WMS 通信                                   │                │
│  └───────────────────────┬───────────────────────────┘                │
└──────────────────────────┼──────────────────────────────────────────────┘
                           │
                           │ Binder IPC
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      System Server 进程                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────┐                │
│  │           WindowManagerService (WMS)                 │                │
│  │                                                      │                │
│  │  主要职责:                                          │                │
│  │  1. 窗口管理 - 添加/移除/更新窗口                   │                │
│  │  2. 窗口布局 - 计算窗口位置和大小                   │                │
│  │  3. 窗口动画 - 管理窗口切换动画                     │                │
│  │  4. 输入事件 - 分发输入事件到窗口                   │                │
│  │  5. 窗口层级 - 维护 Z 轴顺序                       │                │
│  │                                                      │                │
│  │  核心类:                                            │                │
│  │  - WindowState - 窗口状态                          │                │
│  │  - WindowToken - 窗口令牌                          │                │
│  │  - LayoutParams - 布局参数                        │                │
│  └───────────────────────┬───────────────────────────┘                │
└──────────────────────────┼──────────────────────────────────────────────┘
                           │
                           │ Surface Flinger
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         硬件/显示层                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────┐                │
│  │              SurfaceFlinger                         │                │
│  │                                                      │                │
│  │  - 合成所有 Surface 到帧缓冲区                       │                │
│  │  - 管理显示硬件                                      │                │
│  │  - VSync 信号产生                                   │                │
│  └─────────────────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 WindowManager 与 View 绘制关系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WindowManager 与 View 绘制关系                            │
└─────────────────────────────────────────────────────────────────────────────┘

1. Activity 创建
       │
       ▼
2. setContentView()
       │  ┌──────────────────────────────────────────┐
       └──►│ 创建 DecorView                         │
            │ - PhoneWindow.installDecor()          │
            │ - generateDecor()                     │
            └────────────────┬─────────────────────┘
                             │
                             ▼
3. Activity.onResume()
       │  ┌──────────────────────────────────────────┐
       └──►│ makeVisible()                         │
            │ - WindowManager.addView(mDecor)       │
            └────────────────┬─────────────────────┘
                             │
                             ▼
4. WindowManager.addView()
       │  ┌──────────────────────────────────────────┐
       └──►│ WindowManagerGlobal.addView()          │
            │ - 检查参数                            │
            │ - 创建 ViewRootImpl                   │
            │ - 调用 root.setView()                 │
            └────────────────┬─────────────────────┘
                             │
                             ▼
5. ViewRootImpl.setView()
       │  ┌──────────────────────────────────────────┐
       └──►│ - 保存 DecorView                       │
            │ - requestLayout()                    │
            │ - 通过 WMS 请求 Surface              │
            └────────────────┬─────────────────────┘
                             │
                             ▼
6. WMS 处理
       │  ┌──────────────────────────────────────────┐
       └──►│ - 创建 WindowState                     │
            │ - 分配 Surface                        │
            │ - 通知 SurfaceFlinger                 │
            └────────────────┬─────────────────────┘
                             │
                             ▼
7. 屏幕显示
       │
       ▼
   Choreographer 调度绘制
       │
       ├──► performMeasure()
       ├──► performLayout()
       └──► performDraw()
```

### 2.3 Activity.onResume() 详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Activity.onResume() 详解                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Activity.onResume() 做了以下事情:

┌─────────────────────────────────────────────────────────────────────────────┐
│  Activity.onResume() 完整流程                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. ActivityThread.handleResumeActivity()                               │
│       │                                                                │
│       ▼                                                                │
│  2. r.activity.makeVisible()                                           │
│       │                                                                │
│       ▼                                                                │
│  3. WindowManager.addView()                                           │
│       │  ┌──────────────────────────────────────────────────────────┐   │
│       └──►│ WindowManagerGlobal.addView(mDecor, params)           │   │
│            │                                                           │   │
│            │ 1. 创建 ViewRootImpl                                  │   │
│            │ 2. root.setView(view, params, parentView)            │   │
│            │ 3. ViewRootImpl.requestLayout()                     │   │
│            │                                                           │   │
│            │ 4. mWindowSession.addToDisplay()                     │   │
│            │    (通过 Binder 通知 WMS)                             │   │
│            └──────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  makeVisible() 源码流程                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  void makeVisible() {                                                  │
│      if (mWindowAdded) {                                               │
│          mWindowManager.addView(mDecor, mWindowAttributes);            │
│      }                                                                  │
│                                                                         │
│      mDecor.setVisibility(View.VISIBLE);                                │
│  }                                                                     │
│                                                                         │
│  关键点:                                                               │
│  1. mWindowAdded 标志位确保只 addView 一次                          │
│  2. 调用 WindowManager.addView() 将 DecorView 添加到窗口管理           │
│  3. 设置 DecorView 为可见                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 WindowManager.addView() 完整链条

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WindowManager.addView() 完整调用链                           │
└─────────────────────────────────────────────────────────────────────────────┘

Activity.makeVisible()
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Context.getSystemService(Context.WINDOW_SERVICE)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  获取 WindowManager 服务:                                                │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ WindowManager wm = (WindowManager) getSystemService(WINDOW_SERVICE);  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  内部实现:                                                             │
│  return (WindowManager) context.getSystemServiceName(WindowManager.class);  │
│                                                                         │
│  实际返回: WindowManagerImpl                                          │
│                                                                         │
└────────────────────────────────────────────────────────────────────┬───────┘
                                                                             │
                                                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. WindowManager.addView()                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  WindowManagerImpl.addView():                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  public void addView(View view, ViewGroup.LayoutParams params) { │  │
│  │      mGlobal.addView(view, params, mContext.getDisplay(),        │  │
│  │              mContext.getApplicationToken());                  │  │
│  │  }                                                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└────────────────────────────────────────────────────────────────────┬───────┘
                                                                             │
                                                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. WindowManagerGlobal.addView()                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  public void addView(View view, ViewGroup.LayoutParams params,         │
│          Display display, Window parentWindow) {                         │
│                                                                         │
│      // 1. 参数校验                                                    │
│      if (view == null) {                                               │
│          throw new IllegalArgumentException("View cannot be null");     │
│      }                                                                  │
│                                                                         │
│      // 2. 创建 ViewRootImpl                                           │
│      ViewRootImpl root = new ViewRootImpl(view.getContext(), display);  │
│                                                                         │
│      // 3. 保存 View 和 Root                                           │
│      mViews.add(view);                                                 │
│      mRoots.add(root);                                                 │
│      mParams.add(params);                                              │
│                                                                         │
│      // 4. 调用 setView                                               │
│      root.setView(view, wparams, parentWindow);                        │
│                                                                         │
│      // 5. 请求布局                                                    │
│      root.requestLayout();                                              │
│  }                                                                      │
│                                                                         │
└────────────────────────────────────────────────────────────────────┬───────┘
                                                                             │
                                                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. ViewRootImpl.setView()                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  public void setView(View view, LayoutParams attrs,                    │
│          View panelParentView) {                                        │
│      synchronized (this) {                                              │
│          if (mView == null) {                                          │
│              mView = view;                                              │
│                                                                         │
│              // 1. 注册输入通道                                         │
│              res = mWindowInputChannel = new InputChannel();          │
│              mWindowSession.addToDisplay(...);                         │
│                                                                         │
│              // 2. 请求首次布局                                         │
│              requestLayout();                                          │
│                                                                         │
│              // 3. 设置会话回调                                        │
│              mWindowSession.setInsets(...);                           │
│          }                                                              │
│      }                                                                  │
│                                                                         │
└────────────────────────────────────────────────────────────────────┬───────┘
                                                                             │
                                                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. ViewRootImpl.requestLayout()                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  public void requestLayout() {                                          │
│      if (!mHandlingLayoutInEditMode) {                                 │
│          if (Thread.currentThread() == mThread) {                      │
│              // 主线程: 立即调度遍历                                    │
│              scheduleTraversals();                                       │
│          } else {                                                       │
│              // 非主线程: 发送到主线程                                  │
│              mHandler.post(mTraversalRunnable);                         │
│          }                                                              │
│      }                                                                  │
│  }                                                                      │
│                                                                         │
└────────────────────────────────────────────────────────────────────┬───────┘
                                                                             │
                                                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. scheduleTraversals()                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  void scheduleTraversals() {                                            │
│      // 1. 移除之前的回调                                               │
│      mChoreographer.removeCallbacks(..., mTraversalRunnable, ...);    │
│                                                                         │
│      // 2. 注册 VSync 回调                                              │
│      mChoreographer.postCallback(                                       │
│          Choreographer.CALLBACK_TRAVERSAL,                             │
│          mTraversalRunnable,                                           │
│          null);                                                        │
│  }                                                                      │
│                                                                         │
│  等待 VSync 信号后执行 mTraversalRunnable                              │
│                                                                         │
└────────────────────────────────────────────────────────────────────┬───────┘
                                                                             │
                                                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. performTraversals() (真正的绘制入口)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  void doTraversal() {                                                  │
│      performTraversals();                                              │
│  }                                                                      │
│                                                                         │
│  void performTraversals() {                                            │
│      // Phase 1: Measure                                                │
│      performMeasure(mWidth, mHeight);                                  │
│                                                                         │
│      // Phase 2: Layout                                                 │
│      performLayout();                                                  │
│                                                                         │
│      // Phase 3: Draw                                                  │
│      performDraw();                                                    │
│  }                                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.5 非 Activity 场景的 View 绘制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    非 Activity 场景的 View 绘制                              │
└─────────────────────────────────────────────────────────────────────────────┘

除了 Activity，还有以下场景会触发 View 绘制:

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Dialog 绘制                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Dialog 构造函数                                                         │
│       │                                                                │
│       ▼                                                                │
│  WindowManagerGlobal.addView() (相同流程!)                              │
│       │                                                                │
│       ▼                                                                │
│  ViewRootImpl.setView()                                                │
│       │                                                                │
│       ▼                                                                │
│  performTraversals()                                                    │
│                                                                         │
│  关键点:                                                               │
│  - Dialog 使用独立的 Window (PhoneWindow)                              │
│  - 需要设置 TYPE_APPLICATION 的 WindowManager.LayoutParams             │
│  - 同样通过 WindowManagerGlobal.addView()                              │
│                                                                         │
└───────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. PopupWindow 绘制                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PopupWindow.showAtLocation() / showAsDropDown()                       │
│       │                                                                │
│       ▼                                                                │
│  WindowManagerImpl.addView() (相同流程!)                                │
│                                                                         │
│  关键点:                                                               │
│  - PopupWindow 使用 PopupWindow.PopupViewContainer                      │
│  - 设置 TYPE_APPLICATION_PANEL 的 LayoutParams                          │
│  - 父窗口销毁时自动销毁                                                │
│                                                                         │
└───────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. Toast 绘制                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Toast.show()                                                          │
│       │                                                                │
│       ▼                                                                │
│  INotificationManagerService.enqueueToast()                            │
│       │  (Binder 调用)                                                 │
│       ▼                                                                │
│  TN.show() (运行在 Binder 线程)                                        │
│       │                                                                │
│       ▼                                                                │
│  WindowManagerGlobal.addView() (相同流程!)                             │
│                                                                         │
│  关键点:                                                               │
│  - Toast 使用 TYPE_TOAST 的 WindowManager.LayoutParams                 │
│  - 有超时机制 (约 3.5 秒)                                              │
│  - 属于系统级 Window，不需要 Activity                                  │
│                                                                         │
└───────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. System Window (系统窗口)                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  类型:                                                                  │
│  - TYPE_STATUS_BAR - 状态栏                                             │
│  - TYPE_NAVIGATION_BAR - 导航栏                                         │
│  - TYPE_KEYGUARD - 锁屏                                                 │
│  - TYPE_INPUT_METHOD - 输入法                                            │
│                                                                         │
│  绘制流程:                                                              │
│  - 直接通过 WindowManagerGlobal.addView() 添加                         │
│  - 需要 SYSTEM_ALERT_WINDOW 权限                                        │
│  - WindowType 决定了 Z 轴顺序                                           │
│                                                                         │
└───────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. WindowManager.LayoutParams type 汇总                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────┬────────────────────────────────────────────┐    │
│  │ Type                │ 说明                                       │    │
│  ├─────────────────────┼────────────────────────────────────────────┤    │
│  │ APPLICATION        │ 普通应用窗口                               │    │
│  │ APPLICATION_PANEL │ 应用窗口的面板                             │    │
│  │ TOAST             │ Toast 通知                                │    │
│  │ PHONE             │ 电话                                       │    │
│  │ SYSTEM_ALERT      │ 系统弹窗                                   │    │
│  │ KEYGUARD          │ 锁屏                                       │    │
│  │ NAVIGATION_BAR    │ 导航栏                                     │    │
│  │ STATUS_BAR        │ 状态栏                                     │    │
│  │ INPUT_METHOD      │ 输入法                                       │    │
│  └─────────────────────┴────────────────────────────────────────────┘    │
│                                                                         │
│  Z 轴顺序: 值越大越靠上                                                 │
│                                                                         │
└───────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. 统一绘制流程图                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    统一入口: WindowManager.addView()            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                   │                                    │
│                    ┌──────────────┼──────────────┐                     │
│                    ▼              ▼              ▼                      │
│              ┌───────────┐ ┌───────────┐ ┌───────────┐               │
│              │  Activity │ │   Dialog  │ │PopupWindow│               │
│              │   窗口    │ │   窗口    │ │   窗口    │               │
│              └─────┬─────┘ └─────┬─────┘ └─────┬─────┘               │
│                    │              │              │                      │
│                    └──────────────┼──────────────┘                     │
│                                   ▼                                    │
│              ┌───────────────────────────────────────────┐             │
│              │        WindowManagerGlobal.addView()       │             │
│              └───────────────────┬───────────────────────┘             │
│                                  ▼                                    │
│              ┌───────────────────────────────────────────┐             │
│              │              ViewRootImpl.setView()       │             │
│              └───────────────────┬───────────────────────┘             │
│                                  ▼                                    │
│              ┌───────────────────────────────────────────┐             │
│              │           requestLayout()                  │             │
│              │    (measure → layout → draw)              │             │
│              └───────────────────────────────────────────┘             │
│                                                                         │
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.3 WindowManager 核心代码流程

```java
// 1. Activity 中调用
WindowManager wm = getWindowManager();
wm.addView(mDecor, mWindowAttributes);

// 2. WindowManagerGlobal.addView()
public void addView(View view, ViewGroup.LayoutParams params,
        Display display, Window parentWindow) {
    
    // 创建 ViewRootImpl
    ViewRootImpl root = new ViewRootImpl(view.getContext(), display);
    
    // 设置布局参数
    view.setLayoutParams(wparams);
    
    // 保存到列表
    mViews.add(view);
    mRoots.add(root);
    mParams.add(wparams);
    
    // 关键：调用 setView
    root.setView(view, wparams, panelParentView);
}

// 3. ViewRootImpl.setView()
public void setView(View view, LayoutParams attrs, View panelParentView) {
    synchronized (this) {
        if (mView == null) {
            mView = view;
            
            // 请求布局（触发首次绘制）
            requestLayout();
            
            // 通过 Binder 通知 WMS
            mWindowSession.addToDisplay(mWindow, mSeq, mWindowAttributes,
                    getHostVisibility(), mDisplay.getDisplayId(), uId,
                    mInputChannel);
        }
    }
}

// 4. ViewRootImpl.requestLayout()
public void requestLayout() {
    if (!mHandlingLayoutInEditMode) {
        if (Thread.currentThread() == mThread) {
            // 立即执行布局
            scheduleTraversals();
        } else {
            // 发送到主线程执行
            mHandler.post(mTraversalRunnable);
        }
    }
}
```

### 2.4 WMS 核心流程

```java
// WindowManagerService.addWindow()
public int addWindow(Session session, IWindow client,
        LayoutParams attrs, int viewVisibility, int displayId,
        Rect outContentInsets, Rect outStableInsets,
        InputChannel outInputChannel) {
    
    // 1. 创建 WindowState
    WindowState window = new WindowState(this, session, client,
            attrs, viewVisibility, displayId);
    
    // 2. 添加到窗口列表
    addWindowToListInOrderLocked(window, true);
    
    // 3. 分配 Surface
    window.openSurfaceLocked();
    
    // 4. 通知客户端 Surface 已创建
    client.windowAddedReady();
    
    return WindowManagerImpl.ADD_OKAY;
}

void openSurfaceLocked() {
    // 创建 Surface (通过 SurfaceFlinger)
    mSurface = new Surface(surfaceSession, mAttrs.token,
            mAttrs.getTitle().toString(),
            0, mWidth, mHeight, mCurLayoutFlags, mWindowId,
            new SurfaceControl.Builder(surfaceSession));
}
```

### 2.5 ViewRootImpl 与 WMS 通信

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ViewRootImpl 与 WMS 通信                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────────────────┐                    ┌────────────────────┐
│   ViewRootImpl     │                    │        WMS          │
│   (客户端)          │                    │    (服务端)         │
├────────────────────┤                    ├────────────────────┤
│                    │                    │                    │
│ IWindowSession    │◄─────────────────►│ WindowState        │
│ (客户端代理)       │    Binder       │ (服务端)           │
│                    │                    │                    │
├────────────────────┤                    ├────────────────────┤
│                    │                    │                    │
│ IWindow           │◄─────────────────►│ Window Token      │
│ (View 的 Binder)  │    Binder        │ (标识 Window)     │
│                    │                    │                    │
├────────────────────┤                    ├────────────────────┤
│                    │                    │                    │
│ Surface           │◄─────────────────►│ SurfaceControl    │
│ (图形缓冲区)      │    共享内存        │ (图形控制)       │
│                    │                    │                    │
└────────────────────┘                    └────────────────────┘

通信流程:

1. ViewRootImpl 创建 IWindow (匿名 Binder 对象)
2. ViewRootImpl 通过 IWindowSession.addToDisplay() 注册窗口
3. WMS 创建 WindowState 与 IWindow 关联
4. WMS 通过 IWindow 回调窗口事件 (resize, layout, dispatchInput)
5. ViewRootImpl 更新 Surface，提交到 SurfaceFlinger
```
├─────────────────────────────────────────────────────────────────────────────┤
│  WindowManagerService (WMS)                                                │
│     │                                                                       │
│     ▼                                                                       │
│  SurfaceFlinger (显示合成)                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         硬件层 (Hardware)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Display / GPU / Hardware Composer                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. View 绘制流程详解

### 3.1 完整流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 绘制完整流程图                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Activity.onCreate()
       │
       ▼
setContentView(R.layout.xxx)
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  DecorView 创建                                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 1. 创建 PhoneWindow                              │ │
│  │ 2. 安装 DecorView                               │ │
│  │ 3. setContentView() 将布局添加到 ContentParent  │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────┘
                        │
                        ▼
Activity.onStart()
       │
       ▼
Activity.onResume()
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  ViewRootImpl.performTraversals()                      │
│  ─────────────────────────────────────────────────────── │
│  这是 View 绘制的入口方法！                            │
└──────────────────────┬───────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │  Measure  │ │   Layout  │ │   Draw    │
    │  测量阶段 │ │ 布局阶段  │ │ 绘制阶段 │
    └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
          │              │              │
          ▼              ▼              ▼
    ┌──────────────────────────────────────────────┐
    │           三个阶段完成                         │
    └──────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│  Choreographer 帧回调                                 │
│  - 等待 VSync 信号                                   │
│  - 执行 draw()                                        │
│  - 16ms 内完成一帧                                   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 ViewRootImpl 核心代码

```java
// ViewRootImpl.java - 核心绘制方法
private void performTraversals() {
    // ========== 第一阶段：Measure ==========
    if (mLayoutRequested) {
        // 测量所有 View
        performMeasure(mWidth, mHeight);
    }
    
    // ========== 第二阶段：Layout ==========
    if (layoutRequested) {
        // 布局所有 View
        performLayout(lp, mWidth, mHeight);
    }
    
    // ========== 第三阶段：Draw ==========
    if (mFirst || mDirty != null) {
        // 绘制所有 View
        performDraw();
    }
}

private void performMeasure(int childWidthMeasureSpec, int childHeightMeasureSpec) {
    // 触发 View 树的测量
    mView.measure(childWidthMeasureSpec, childHeightMeasureSpec);
    // 最终测量结果
    mView.setMeasuredDimension(width, height);
}

private void performLayout(LayoutParams lp, int desiredWindowWidth, int desiredWindowHeight) {
    // 触发 View 树的布局
    mView.layout(0, 0, mView.getMeasuredWidth(), mView.getMeasuredHeight());
}

private void performDraw() {
    // 触发 View 树的绘制
    mView.draw(canvas);
}
```

---

## 4. Measure 测量流程

### 4.1 Measure 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Measure 测量流程图                                  │
└─────────────────────────────────────────────────────────────────────────────┘

ViewRootImpl.performMeasure()
        │
        ▼
    ┌─────────────────────────────────────────────┐
    │  measure(widthMeasureSpec, heightMeasureSpec) │
    │  - final 方法，不可重写                       │
    │  - 调用 onMeasure()                          │
    └────────────────────┬────────────────────────┘
                        │
                        ▼
    ┌─────────────────────────────────────────────┐
    │  onMeasure(widthMeasureSpec, heightMeasureSpec) │
    │  - 可重写，自定义测量逻辑                      │
    │  - 必须调用 setMeasuredDimension()            │
    └────────────────────┬────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ViewGroup │  │ViewGroup │  │   View   │
   │ 处理MeasureSpec  │  继续传递  │  计算尺寸  │
   │ 给子 View   │  给子 View  │           │
   └─────┬──────┘  └─────┬──────┘  └────┬─────┘
         │                │              │
         └────────────────┼──────────────┘
                          ▼
                   ┌────────────────┐
                   │ setMeasured   │
                   │ Dimension()   │
                   │ 保存测量宽高   │
                   └────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    MeasureSpec 详解                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  MeasureSpec = Mode + Size                                              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Mode (测量模式)                              │    │
│  ├──────────────┬────────────────────────────────────────────────┤    │
│  │ EXACTLY       │  精确模式                                      │    │
│  │               │  - match_parent                               │    │
│  │               │  - 具体数值                                     │    │
│  ├──────────────┼────────────────────────────────────────────────┤    │
│  │ AT_MOST       │  最大模式                                      │    │
│  │               │  - wrap_content                               │    │
│  │               │  - 不能超过父 View 尺寸                        │    │
│  ├──────────────┼────────────────────────────────────────────────┤    │
│  │ UNSPECIFIED  │  未指定模式                                     │    │
│  │               │  - 不受限制                                     │    │
│  │               │  - ListView/ScrollView 内部使用               │    │
│  └──────────────┴────────────────────────────────────────────────┘    │
│                                                                         │
│  示例:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ parentSize = 500                                                │    │
│  │                                                                         │
│  │ child: match_parent  → MeasureSpec = EXACTLY + 500           │    │
│  │ child: wrap_content  → MeasureSpec = AT_MOST + 500            │    │
│  │ child: 200dp       → MeasureSpec = EXACTLY + 200(换算)       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 onMeasure 标准写法

```java
@Override
protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
    // 1. 获取测量模式和尺寸
    int widthMode = MeasureSpec.getMode(widthMeasureSpec);
    int widthSize = MeasureSpec.getSize(widthMeasureSpec);
    int heightMode = MeasureSpec.getMode(heightMeasureSpec);
    int heightSize = MeasureSpec.getSize(heightMeasureSpec);
    
    // 2. 计算期望的宽高
    int desiredWidth = 0;
    int desiredHeight = 0;
    
    // 3. 根据模式计算最终尺寸
    if (widthMode == MeasureSpec.EXACTLY) {
        desiredWidth = widthSize;
    } else if (widthMode == MeasureSpec.AT_MOST) {
        desiredWidth = Math.min(desiredWidth, widthSize);
    } else {
        desiredWidth = desiredWidth; // UNSPECIFIED
    }
    
    if (heightMode == MeasureSpec.EXACTLY) {
        desiredHeight = heightSize;
    } else if (heightMode == MeasureSpec.AT_MOST) {
        desiredHeight = Math.min(desiredHeight, heightSize);
    } else {
        desiredHeight = desiredHeight;
    }
    
    // 4. 必须调用此方法保存测量结果！
    setMeasuredDimension(desiredWidth, desiredHeight);
}
```

### 4.3 ViewGroup 测量子 View

```java
// ViewGroup 中测量子 View
protected void measureChildren(int widthMeasureSpec, int heightMeasureSpec) {
    final int size = mChildrenCount;
    final View[] children = mChildren;
    
    for (int i = 0; i < size; ++i) {
        final View child = children[i];
        // 跳过 GONE 的 View
        if ((child.mViewFlags & VISIBILITY_MASK) != GONE) {
            // 获取子 View 的 MeasureSpec
            measureChild(child, widthMeasureSpec, heightMeasureSpec);
        }
    }
}

protected void measureChild(View child, int parentWidthMeasureSpec, int parentHeightMeasureSpec) {
    // 获取子 View 的 LayoutParams
    final LayoutParams lp = child.getLayoutParams();
    
    // 计算子 View 的 MeasureSpec
    final int childWidthMeasureSpec = getChildMeasureSpec(
        parentWidthMeasureSpec, mPaddingLeft + mPaddingRight, lp.width);
    final int childHeightMeasureSpec = getChildMeasureSpec(
        parentHeightMeasureSpec, mPaddingTop + mPaddingBottom, lp.height);
    
    // 调用子 View 的 measure()
    child.measure(childWidthMeasureSpec, childHeightMeasureSpec);
}
```

---

## 5. Layout 布局流程

### 5.1 Layout 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Layout 布局流程图                                   │
└─────────────────────────────────────────────────────────────────────────────┘

ViewRootImpl.performLayout()
        │
        ▼
┌─────────────────────────────────────────────┐
│  layout(l, t, r, b)                       │
│  - final 方法，不可重写                      │
│  - 调用 onLayout()                         │
└────────────────────┬────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  onLayout(changed, l, t, r, b)            │
│  - 可重写，实现自定义布局                    │
│  - 遍历子 View，调用 child.layout()        │
└────────────────────┬────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   ┌──────────┐          ┌──────────┐
   │ViewGroup │          │   View   │
   │计算子View│          │  无子View │
   │位置并调用│          │  无需实现 │
   │child.layout()      │  onLayout │
   └─────┬────┘          └───────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  setFrame()                                │
│  - 保存四个顶点位置                         │
│  - 判断位置是否发生变化                     │
│  - 返回 true 表示位置改变，需要重绘         │
└─────────────────────────────────────────────┘
```

### 5.2 onLayout 标准写法 (LinearLayout 为例)

```java
@Override
protected void onLayout(boolean changed, int l, int t, int r, int b) {
    if (mOrientation == VERTICAL) {
        layoutVertical();
    } else {
        layoutHorizontal();
    }
}

private void layoutVertical() {
    int childTop = mPaddingTop;
    int childLeft = mPaddingLeft;
    
    final int count = getChildCount();
    for (int i = 0; i < count; i++) {
        final View child = getChildAt(i);
        
        if (child.getVisibility() != View.GONE) {
            // 获取子 View 的测量宽高
            final int childWidth = child.getMeasuredWidth();
            final int childHeight = child.getMeasuredHeight();
            
            // 计算子 View 的位置 (这里简化了 gravity 处理)
            int childLeft = childLeft + mPaddingLeft;
            int childTop = childTop + mPaddingTop;
            
            // 调用子 View 的 layout()
            child.layout(childLeft, childTop, 
                        childLeft + childWidth, 
                        childTop + childHeight);
            
            // 更新下一个子 View 的位置
            childTop += childHeight + lp.topMargin + lp.bottomMargin;
        }
    }
}
```

---

## 6. Draw 绘制流程

### 6.1 Draw 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Draw 绘制流程图                                     │
└─────────────────────────────────────────────────────────────────────────────┘

ViewRootImpl.performDraw()
        │
        ▼
┌─────────────────────────────────────────────┐
│  draw(canvas) - final 方法                  │
│  - 不可重写，按固定流程绘制                   │
└────────────────────┬────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│  1.     │   │  2.     │   │  3.     │
│  draw   │   │  onDraw │   │ draw    │
│ Back-   │   │  绘制   │   │  Chil-  │
│  ground  │   │  内容   │   │  dren   │
└─────┬────┘   └────┬────┘   └────┬────┘
      │              │              │
      ▼              ▼              ▼
   绘制背景       绘制主体        绘制子 View
   (通常透明)    (自定义绘制)    (递归调用)
      │              │              │
      └──────────────┴──────────────┘
                     │
                     ▼
              ┌────────────────┐
              │ 4. onDraw()   │
              │ 绘制装饰      │
              │ (滚动条等)   │
              └────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         draw() 完整代码流程                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  public void draw(Canvas canvas) {                                      │
│      // 1. 绘制背景                                                     │
│      if (!dirtyOpaque) {                                               │
│          drawBackground(canvas);                                         │
│      }                                                                  │
│                                                                         │
│      // 2. 绘制内容 (自定义 View 主要重写这个)                          │
│      if (!dirtyOpaque) {                                               │
│          onDraw(canvas);                                                │
│      }                                                                  │
│                                                                         │
│      // 3. 绘制子 View                                                 │
│      dispatchDraw(canvas);                                              │
│                                                                         │
│      // 4. 绘制装饰 (滚动条、前景等)                                    │
│      onDrawForeground(canvas);                                           │
│  }                                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 自定义 View onDraw 示例

```java
@Override
protected void onDraw(Canvas canvas) {
    super.onDraw(canvas); // 调用父类绘制（如果有背景等）
    
    // 1. 绘制背景（可选）
    // canvas.drawColor(color) 或使用 Paint
    
    // 2. 绘制内容
    // 绘制文字
    canvas.drawText("Hello", x, y, textPaint);
    
    // 绘制图形
    canvas.drawCircle(cx, cy, radius, circlePaint);
    canvas.drawRect(left, top, right, bottom, rectPaint);
    canvas.drawLine(x1, y1, x2, y2, linePaint);
    
    // 绘制路径
    Path path = new Path();
    path.moveTo(0, 0);
    path.lineTo(100, 100);
    canvas.drawPath(path, pathPaint);
    
    // 3. 绘制装饰
    // 如滚动条等，通常在 onDrawForeground() 中
}
```

---

## 7. 事件分发机制

### 7.1 事件分发流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Touch 事件分发流程图                                │
└─────────────────────────────────────────────────────────────────────────────┘

用户触摸屏幕
        │
        ▼
┌─────────────────────────────────────────────┐
│  Activity.dispatchTouchEvent()              │
│  - 传递给 Window                             │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│  DecorView.dispatchTouchEvent()             │
│  - 传递给根 ViewGroup                       │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│  ViewGroup.dispatchTouchEvent()            │
│  - onInterceptTouchEvent() 判断是否拦截      │
│  - 遍历子 View，调用 child.dispatchTouchEvent()│
└────────────────────┬────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
   拦截 (返回 true)        不拦截 (返回 false)
         │                       │
         ▼                       ▼
┌─────────────────┐      ┌─────────────────────────┐
│  ViewGroup.on   │      │  子 View.dispatch       │
│  TouchEvent()   │      │  TouchEvent()          │
└─────────────────┘      └────────────┬────────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │  View.onTouchEvent() │
                          │  处理点击事件         │
                          └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         事件分发方法解析                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  public boolean dispatchTouchEvent(MotionEvent ev) {                    │
│      boolean consume = false;                                           │
│                                                                         │
│      // 1. 判断是否需要拦截                                              │
│      if (onInterceptTouchEvent(ev)) {                                   │
│          // 拦截事件，自己处理                                            │
│          consume = onTouchEvent(ev);                                    │
│      } else {                                                          │
│          // 不拦截，传递给子 View                                        │
│          consume = child.dispatchTouchEvent(ev);                        │
│      }                                                                 │
│                                                                         │
│      return consume;                                                    │
│  }                                                                      │
│                                                                         │
│  // ViewGroup 特有方法                                                 │
│  public boolean onInterceptTouchEvent(MotionEvent ev) {                │
│      return false; // 默认不拦截                                         │
│  }                                                                      │
│                                                                         │
│  // View 处理触摸事件                                                   │
│  public boolean onTouchEvent(MotionEvent ev) {                        │
│      // 处理点击、长按、滑动等                                           │
│      return true; // 消耗了事件                                          │
│  }                                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 事件分发经典案例

```java
// 自定义 ViewGroup 处理事件分发
public class MyViewGroup extends ViewGroup {
    
    private int mLastX;
    private int mLastY;
    
    @Override
    public boolean onInterceptTouchEvent(MotionEvent ev) {
        // 根据条件判断是否拦截
        switch (ev.getAction()) {
            case MotionEvent.ACTION_DOWN:
                mLastX = (int) ev.getX();
                mLastY = (int) ev.getY();
                break;
                
            case MotionEvent.ACTION_MOVE:
                int dx = Math.abs((int) ev.getX() - mLastX);
                int dy = Math.abs((int) ev.getY() - mLastY);
                
                // 水平滑动超过阈值，拦截事件
                if (dx > dy && dx > ViewConfiguration.getTouchSlop()) {
                    return true; // 拦截，交给自己的 onTouchEvent 处理
                }
                break;
        }
        
        return super.onInterceptTouchEvent(ev); // 默认不拦截
    }
    
    @Override
    public boolean onTouchEvent(MotionEvent ev) {
        // 处理滑动事件
        switch (ev.getAction()) {
            case MotionEvent.ACTION_MOVE:
                // 实现自己的滑动逻辑
                break;
        }
        
        return true; // 消耗事件
    }
}
```

---

## 8. 自定义 View

### 8.1 自定义 View 步骤

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         自定义 View 步骤                                    │
└─────────────────────────────────────────────────────────────────────────────┘

1. 构造函数
   ├── View(Context context)
   ├── View(Context context, AttributeSet attrs)
   └── View(Context context, AttributeSet attrs, int defStyleAttr)

2. onMeasure()
   ├── 计算 View 的宽高
   ├── 处理 match_parent / wrap_content / 具体数值
   └── 调用 setMeasuredDimension()

3. onLayout()
   ├── (可选) ViewGroup 需要实现
   └── 计算并设置子 View 的位置

4. onDraw()
   ├── 绘制 View 的内容
   └── 使用 Canvas 和 Paint

5. 事件处理
   ├── onTouchEvent()
   └── 其他交互方法

6. 常用方法
   ├── invalidate() - 请求重绘
   ├── requestLayout() - 请求重新布局
   └── setVisibility() - 控制可见性
```

### 8.2 完整自定义 View 示例

```java
public class CircleView extends View {
    
    private Paint mPaint;
    private int mColor = Color.RED;
    private int mRadius = 100;
    
    // 1. 构造函数
    public CircleView(Context context) {
        this(context, null);
    }
    
    public CircleView(Context context, AttributeSet attrs) {
        this(context, attrs, 0);
    }
    
    public CircleView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
        
        // 解析自定义属性
        if (attrs != null) {
            TypedArray a = context.obtainStyledAttributes(attrs, R.styleable.CircleView);
            mColor = a.getColor(R.styleable.CircleView_circleColor, Color.RED);
            mRadius = a.getDimensionPixelSize(R.styleable.CircleView_circleRadius, 100);
            a.recycle();
        }
        
        // 初始化 Paint
        mPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
        mPaint.setColor(mColor);
        mPaint.setStyle(Paint.Style.FILL);
    }
    
    // 2. 测量
    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        int widthMode = MeasureSpec.getMode(widthMeasureSpec);
        int widthSize = MeasureSpec.getSize(widthMeasureSpec);
        int heightMode = MeasureSpec.getMode(heightMeasureSpec);
        int heightSize = MeasureSpec.getSize(heightMeasureSpec);
        
        int desiredWidth = mRadius * 2 + getPaddingLeft() + getPaddingRight();
        int desiredHeight = mRadius * 2 + getPaddingTop() + getPaddingBottom();
        
        int width = resolveSize(desiredWidth, widthMeasureSpec);
        int height = resolveSize(desiredHeight, heightMeasureSpec);
        
        setMeasuredDimension(width, height);
    }
    
    // 3. 绘制
    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        
        int cx = getWidth() / 2;
        int cy = getHeight() / 2;
        
        canvas.drawCircle(cx, cy, mRadius, mPaint);
    }
    
    // 4. 事件处理
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                // 处理按下
                return true;
            case MotionEvent.ACTION_MOVE:
                // 处理移动
                return true;
            case MotionEvent.ACTION_UP:
                // 处理抬起
                return true;
        }
        return super.onTouchEvent(event);
    }
}
```

---

## 9. 性能优化

### 9.1 绘制优化原则

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 绘制优化原则                                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. 减少 overdraw (过度绘制)
   ┌─────────────────────────────────────────────────────────────────┐
   │  检测方法: Developer Options → Debug GPU Overdraw              │
   │  颜色含义:                                                      │
   │  - 蓝色: 1次绘制 (理想)                                        │
   │  - 绿色: 2次绘制 (可接受)                                       │
   │  - 粉色: 3次绘制 (需要优化)                                     │
   │  - 红色: 4+次绘制 (严重问题)                                    │
   │                                                                  │
   │  优化方法:                                                      │
   │  - 移除不必要的背景                                              │
   │  - 使用 ViewStub 延迟加载                                       │
   │  - 减少嵌套层级                                                  │
   └─────────────────────────────────────────────────────────────────┘

2. 减少 layout/measure 次数
   ┌─────────────────────────────────────────────────────────────────┐
   │  优化方法:                                                      │
   │  - 使用 ConstrainLayout 减少嵌套                                │
   │  - 避免在 onMeasure() 中进行复杂计算                            │
   │  - 使用 view.post() 延迟操作                                   │
   │  - 复用 View (ViewHolder 模式)                                 │
   └─────────────────────────────────────────────────────────────────┘

3. 优化自定义 View
   ┌─────────────────────────────────────────────────────────────────┐
   │  优化方法:                                                      │
   │  - 避免在 onDraw() 中创建对象 (Canvas 除外)                    │
   │  - 使用 Hardware加速                                             │
   │  - 减少 draw() 调用次数                                          │
   │  - 使用 Canvas.save() / restore() 谨慎                         │
   └─────────────────────────────────────────────────────────────────┘
```

### 9.2 性能优化示例

```java
// ❌ 错误：在 onDraw() 中创建对象
@Override
protected void onDraw(Canvas canvas) {
    Paint paint = new Paint(); // 每次绘制都创建！
    paint.setColor(Color.RED);
    canvas.drawCircle(x, y, radius, paint);
}

// ✅ 正确：在构造函数中创建
public class CircleView extends View {
    private Paint mPaint;
    
    public CircleView(Context context) {
        super(context);
        mPaint = new Paint(); // 只创建一次
        mPaint.setColor(Color.RED);
    }
    
    @Override
    protected void onDraw(Canvas canvas) {
        canvas.drawCircle(x, y, radius, mPaint);
    }
}

// ✅ 正确：使用 view.post() 延迟操作
view.post(new Runnable() {
    @Override
    public void run() {
        // 在 View 测量完成后执行
    }
});
```

---

## 10. 总结

### 10.1 核心要点

| 阶段 | 关键方法 | 职责 |
|------|----------|------|
| Measure | `onMeasure()` | 计算 View 尺寸 |
| Layout | `onLayout()` | 确定 View 位置 |
| Draw | `onDraw()` | 绘制 View 内容 |

### 10.2 调用时机

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 绘制时机                                       │
└─────────────────────────────────────────────────────────────────────────────┘

requestLayout()  →  onMeasure() → onLayout() → onDraw()
                         │              │
                         │              └── 只调用 measure/layout
                         │
                         └────────────── 可能会重新绘制

invalidate()     →  onDraw() (只重绘)
                         │
                         └── 不改变布局，只重绘

setVisibility()  →  从不可见变为可见时触发完整绘制
```

### 10.3 流程图总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    View 完整生命周期流程图                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │  View 创建      │
                         │ (构造函数)      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  onMeasure()   │
                         │  测量尺寸       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  onLayout()    │
                         │  确定位置       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  onDraw()       │
                         │  绘制内容       │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │      等待用户交互            │
                    │   (onTouchEvent 等)         │
                    └──────────────┬──────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
     ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
     │ invalidate() │    │requestLayout│    │ setVisibility │
     │  重绘        │    │ 重新布局     │    │  显示/隐藏    │
     └──────┬───────┘    └──────┬───────┘    └──────────────┘
            │                     │                    │
            ▼                     ▼                    ▼
     onDraw() 重新绘制    onMeasure() 重新测量    从不可见变为可见时
                      onLayout() 重新布局    触发完整绘制
                      onDraw() 可能重绘
                                   │
                                   ▼
                         ┌─────────────────┐
                         │  View 销毁     │
                         │ (onDetachedFromWindow)│
                         └─────────────────┘

---

*本文档由 OpenClaw 自动生成*
