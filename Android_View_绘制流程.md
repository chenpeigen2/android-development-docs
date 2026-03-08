# Android View 绘制流程完全指南

> 作者：OpenClaw | 日期：2026-03-08

---

## 目录

1. [概述](#1-概述)
2. [ViewRootImpl 核心机制](#2-viewrootimpl-核心机制)
   - 2.1 [ViewRootImpl 概述](#21-viewrootimpl-概述)
   - 2.2 [ViewRootImpl 创建流程](#22-viewrootimpl-创建流程)
   - 2.3 [setView 完整流程](#23-setview-完整流程)
   - 2.4 [requestLayout 流程](#24-requestlayout-流程)
   - 2.5 [scheduleTraversals 流程](#25-scheduletraversals-流程)
   - 2.6 [performTraversals 完整流程](#26-performtraversals-完整流程)
   - 2.7 [完整帧绘制流程](#27-完整帧绘制流程)
   - 2.8 [Choreographer 详解](#28-choreographer-详解)
   - 2.9 [BufferQueue 与双缓冲机制](#29-bufferqueue-与双缓冲机制)
   - 2.10 [渲染合成流程](#210-渲染合成流程)
   - 2.11 [View 绘制多层级架构](#211-view-绘制多层级架构)
   - 2.12 [层级调用完整流程](#212-层级调用完整流程)
   - 2.13 [层级总结表](#213-层级总结表)
3. [WindowManager 架构](#3-windowmanager-架构)
4. [Measure 测量流程](#4-measure-测量流程)
5. [Layout 布局流程](#5-layout-布局流程)
6. [Draw 绘制流程](#6-draw-绘制流程)
7. [常见问题](#7-常见问题)
8. [总结](#8-总结)

---

## 1. 概述

View 绘制流程是 Android UI 的核心机制，理解它对于性能优化和自定义 View 至关重要。

### 1.1 核心三阶段

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 绘制三阶段                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
  │    Measure     │ ──►│     Layout     │ ──►│      Draw      │
  │    测量阶段     │    │    布局阶段    │    │    绘制阶段    │
  └────────────────┘    └────────────────┘    └────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
    计算View尺寸          确定View位置          绘制View内容
    onMeasure()          onLayout()           onDraw()
```

### 1.2 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 绘制整体架构                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              应用进程                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  Activity ──► PhoneWindow ──► DecorView ──► ViewRootImpl                   │
│                                                       │                      │
│                    performTraversals() ───────────────┘                      │
│                           │                                                  │
│              ┌────────────┼────────────┐                                    │
│              ▼            ▼            ▼                                    │
│        performMeasure  performLayout  performDraw                           │
│              │            │            │                                    │
│              ▼            ▼            ▼                                    │
│           measure()    layout()     draw()                                  │
│              │            │            │                                    │
│              ▼            ▼            ▼                                    │
│         onMeasure()  onLayout()   onDraw()                                  │
│                                                                              │
│                    Choreographer (VSync 调度)                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ Binder IPC
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           System Server                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  WindowManagerService (WMS) ──► SurfaceFlinger                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. ViewRootImpl 核心机制

### 2.1 ViewRootImpl 概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ViewRootImpl 职责                                   │
│  源码位置: frameworks/base/core/java/android/view/ViewRootImpl.java        │
└─────────────────────────────────────────────────────────────────────────────┘

ViewRootImpl 是 View 树的根，是连接 WindowManager 和 DecorView 的桥梁:

核心职责:
1. View 树管理 - 持有 DecorView，管理测量、布局、绘制
2. 与 WMS 通信 - 通过 IWindowSession 与 WMS 交互
3. 输入事件分发 - 接收并分发输入事件到 View 树
4. Surface 管理 - 管理绘制 Surface
5. VSync 同步 - 通过 Choreographer 接收 VSync 信号
```

### 2.2 ViewRootImpl 创建流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ViewRootImpl 创建流程                               │
└─────────────────────────────────────────────────────────────────────────────┘

ActivityThread.handleResumeActivity()
              │
              ▼
Activity.makeVisible()
              │
              │  void makeVisible() {
              │      if (!mWindowAdded) {
              │          mWindowManager.addView(mDecor, mWindowAttributes);
              │          mWindowAdded = true;
              │      }
              │      mDecor.setVisibility(View.VISIBLE);
              │  }
              │
              ▼
WindowManagerImpl.addView()
              │
              │  public void addView(View view, ViewGroup.LayoutParams params) {
              │      mGlobal.addView(view, params, mContext.getDisplay(), mParentWindow);
              │  }
              │
              ▼
WindowManagerGlobal.addView()
              │
              │  public void addView(View view, LayoutParams params, 
              │          Display display, Window parentWindow) {
              │      
              │      // ★★★ 创建 ViewRootImpl ★★★
              │      ViewRootImpl root = new ViewRootImpl(view.getContext(), display);
              │      
              │      mViews.add(view);
              │      mRoots.add(root);
              │      mParams.add(params);
              │      
              │      // ★★★ 调用 setView ★★★
              │      root.setView(view, params, panelParentView);
              │  }
              │
              ▼
ViewRootImpl.setView()
```

### 2.3 setView 完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ViewRootImpl.setView() 完整流程                     │
│  源码位置: frameworks/base/core/java/android/view/ViewRootImpl.java        │
└─────────────────────────────────────────────────────────────────────────────┘

public void setView(View view, LayoutParams attrs, View panelParentView) {
    synchronized (this) {
        if (mView == null) {
            
            // 1. 保存 View 引用
            mView = view;
            mView.setLayoutParams(attrs);
            
            // 2. 创建 InputChannel
            mInputChannel = new InputChannel();
            
            // 3. 通过 Binder 调用 WMS 添加窗口
            res = mWindowSession.addToDisplay(
                    mWindow, mSeq, mWindowAttributes,
                    getHostVisibility(), mDisplay.getDisplayId(),
                    mTmpFrame, mAttachInfo.mContentInsets,
                    mInputChannel);
            
            // 4. 设置 View 的 parent
            view.assignParent(this);
            
            // 5. ★★★ 请求首次布局 ★★★
            requestLayout();
            
            // 6. 设置输入事件接收器
            mInputEventReceiver = new WindowInputEventReceiver(
                    mInputChannel, Looper.myLooper());
        }
    }
}
```

### 2.4 requestLayout 流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ViewRootImpl.requestLayout() 流程                   │
│  源码位置: frameworks/base/core/java/android/view/ViewRootImpl.java        │
└─────────────────────────────────────────────────────────────────────────────┘

@Override
public void requestLayout() {
    if (!mHandlingLayoutInLayoutRequest) {
        // ★★★ 检查线程 - 必须在主线程调用 ★★★
        checkThread();
        mLayoutRequested = true;
        // ★★★ 调度遍历 ★★★
        scheduleTraversals();
    }
}

void checkThread() {
    if (mThread != Thread.currentThread()) {
        throw new CalledFromWrongThreadException(
            "Only the original thread that created a view hierarchy "
            + "can touch its views.");
    }
}
```

### 2.5 scheduleTraversals 流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ViewRootImpl.scheduleTraversals() 流程              │
│  源码位置: frameworks/base/core/java/android/view/ViewRootImpl.java        │
└─────────────────────────────────────────────────────────────────────────────┘

void scheduleTraversals() {
    if (!mTraversalScheduled) {
        mTraversalScheduled = true;
        
        // 1. 添加同步屏障 (确保 VSync 回调优先执行)
        mTraversalBarrier = mHandler.getLooper().getQueue().postSyncBarrier();
        
        // 2. ★★★ 通过 Choreographer 注册 VSync 回调 ★★★
        mChoreographer.postCallback(
                Choreographer.CALLBACK_TRAVERSAL,
                mTraversalRunnable,  // → doTraversal() → performTraversals()
                null);
    }
}

// TraversalRunnable
final class TraversalRunnable implements Runnable {
    @Override
    public void run() {
        doTraversal();
    }
}

void doTraversal() {
    if (mTraversalScheduled) {
        mTraversalScheduled = false;
        // 移除同步屏障
        mHandler.getLooper().getQueue().removeSyncBarrier(mTraversalBarrier);
        // ★★★ 执行遍历 ★★★
        performTraversals();
    }
}
```

### 2.6 performTraversals 完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ViewRootImpl.performTraversals() 完整流程           │
│  源码位置: frameworks/base/core/java/android/view/ViewRootImpl.java        │
│  这是 View 绘制的核心方法！约 800+ 行代码                                   │
└─────────────────────────────────────────────────────────────────────────────┘

private void performTraversals() {
    
    // ========== 阶段 1: 获取窗口尺寸 ==========
    int desiredWindowWidth = mWinFrame.width();
    int desiredWindowHeight = mWinFrame.height();
    
    // ========== 阶段 2: 询问 WMS 是否需要重新布局 ==========
    if (mFirst || mWidth != host.getMeasuredWidth() 
            || mHeight != host.getMeasuredHeight()) {
        relayoutWindow(params, viewVisibility, insetsPending);
    }
    
    // ========== 阶段 3: 测量 (performMeasure) ==========
    if (!mStopped) {
        int childWidthMeasureSpec = getRootMeasureSpec(mWidth, lp.width);
        int childHeightMeasureSpec = getRootMeasureSpec(mHeight, lp.height);
        
        // ★★★ 执行测量 ★★★
        performMeasure(childWidthMeasureSpec, childHeightMeasureSpec);
    }
    
    // ========== 阶段 4: 布局 (performLayout) ==========
    if (didLayout) {
        // ★★★ 执行布局 ★★★
        performLayout(lp, mWidth, mHeight);
    }
    
    // ========== 阶段 5: 绘制 (performDraw) ==========
    if (!cancelDraw) {
        // ★★★ 执行绘制 ★★★
        performDraw();
    }
}


// ========== performMeasure ==========
private void performMeasure(int childWidthMeasureSpec, int childHeightMeasureSpec) {
    mView.measure(childWidthMeasureSpec, childHeightMeasureSpec);
}

// ========== performLayout ==========
private void performLayout(LayoutParams lp, int desiredWindowWidth, int desiredWindowHeight) {
    host.layout(0, 0, host.getMeasuredWidth(), host.getMeasuredHeight());
}

// ========== performDraw ==========
private void performDraw() {
    draw(fullRedrawNeeded);
}
```

### 2.7 完整帧绘制流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         完整帧绘制流程 (invalidate/requestLayout → 上屏)    │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 触发更新                                                            │
  │     View.invalidate() / View.requestLayout()                           │
  │     - 标记视图为"脏区" (Dirty Area)                                     │
  │     - 调用 ViewRootImpl.scheduleTraversals()                           │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. ViewRootImpl.scheduleTraversals()                                   │
  │     - 插入同步屏障 (SyncBarrier)                                        │
  │     - 通过 Choreographer 注册 CALLBACK_TRAVERSAL 回调                   │
  │     - 请求下一个 VSync 信号                                             │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. 等待 VSync 信号                                                     │
  │     - 屏幕硬件每 16.67ms (60Hz) 产生一个 VSync 信号                     │
  │     - VSync 通知系统开启新一帧的绘制周期                                │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  4. Choreographer.doFrame()                                             │
  │     - FrameDisplayEventReceiver 接收 VSync                             │
  │     - 按优先级执行回调:                                                 │
  │       1) CALLBACK_INPUT      - 输入事件处理                            │
  │       2) CALLBACK_ANIMATION  - 动画更新                                │
  │       3) CALLBACK_TRAVERSAL  - View 绘制 ★★★                          │
  │       4) CALLBACK_COMMIT     - 提交                                    │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  5. doTraversal()                                                       │
  │     - 移除同步屏障                                                      │
  │     - 调用 performTraversals()                                         │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  6. performTraversals()                                                 │
  │     - performMeasure() → measure() → onMeasure()                       │
  │     - performLayout()  → layout()  → onLayout()                        │
  │     - performDraw()    → draw()    → onDraw()                          │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  7. 渲染合成 & 上屏                                                     │
  │     - 绘制内容写入 Surface (BufferQueue)                               │
  │     - SurfaceFlinger 合成所有图层                                      │
  │     - 提交到显示屏                                                     │
  └─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         帧绘制流程时序图                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  时间轴 →

  T0          T1          T2          T3          T4          T5
  │           │           │           │           │           │
  │  VSync    │           │   VSync   │           │   VSync   │
  │    │      │           │     │     │           │     │     │
  ▼    ▼      │           ▼     ▼     │           ▼     ▼     │
  ┌─────────┐ │           ┌─────────┐ │           ┌─────────┐ │
  │ Frame 1 │ │           │ Frame 2 │ │           │ Frame 3 │ │
  │ measure │ │           │ measure │ │           │ measure │ │
  │ layout  │ │           │ layout  │ │           │ layout  │ │
  │ draw    │ │           │ draw    │ │           │ draw    │ │
  └────┬────┘ │           └────┬────┘ │           └────┬────┘ │
       │      │                │      │                │      │
       │      │  GPU合成       │      │  GPU合成       │      │
       │      ▼                │      ▼                │      ▼
       │  ┌─────────┐         │  ┌─────────┐         │  ┌─────────┐
       │  │上屏显示  │         │  │上屏显示  │         │  │上屏显示  │
       │  │ Frame 1 │         │  │ Frame 2 │         │  │ Frame 3 │
       │  └─────────┘         │  └─────────┘         │  └─────────┘
       │                      │                      │
       └──────────────────────┴──────────────────────┘
                    16.67ms (60fps)
```

### 2.8 Choreographer 详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Choreographer 详解                                  │
│  源码位置: frameworks/base/core/java/android/view/Choreographer.java       │
└─────────────────────────────────────────────────────────────────────────────┘

Choreographer 是 Android 帧调度的核心，负责:
1. 接收 VSync 信号
2. 协调 UI 线程的绘制时机
3. 确保动画、输入、绘制的时序正确
```

#### 2.8.1 Choreographer 架构总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Choreographer 完整架构                              │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                           应用层 (Java)                                  │
  ├─────────────────────────────────────────────────────────────────────────┤
  │                                                                         │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │                      Choreographer                               │   │
  │  │  源码: frameworks/base/core/java/android/view/Choreographer.java │   │
  │  ├─────────────────────────────────────────────────────────────────┤   │
  │  │                                                                 │   │
  │  │  核心组件:                                                      │   │
  │  │  ┌─────────────────────────────────────────────────────────────┐│   │
  │  │  │ 1. FrameDisplayEventReceiver                                ││   │
  │  │  │    - 继承 DisplayEventReceiver                              ││   │
  │  │  │    - 接收 VSync 信号                                        ││   │
  │  │  │    - 触发 onVsync() → doFrame()                            ││   │
  │  │  └─────────────────────────────────────────────────────────────┘│   │
  │  │  ┌─────────────────────────────────────────────────────────────┐│   │
  │  │  │ 2. CallbackQueue[] (4个回调队列)                            ││   │
  │  │  │    - CALLBACK_INPUT      (0) - 输入事件                    ││   │
  │  │  │    - CALLBACK_ANIMATION  (1) - 动画                        ││   │
  │  │  │    - CALLBACK_TRAVERSAL  (2) - View 遍历 ★★★              ││   │
  │  │  │    - CALLBACK_COMMIT     (3) - 提交                        ││   │
  │  │  └─────────────────────────────────────────────────────────────┘│   │
  │  │  ┌─────────────────────────────────────────────────────────────┐│   │
  │  │  │ 3. FrameHandler                                             ││   │
  │  │  │    - 处理 MSG_DO_FRAME 消息                                 ││   │
  │  │  │    - 帧延迟检测                                             ││   │
  │  │  └─────────────────────────────────────────────────────────────┘│   │
  │  │  ┌─────────────────────────────────────────────────────────────┐│   │
  │  │  │ 4. FrameInfo                                                ││   │
  │  │  │    - 记录每帧的时间戳信息                                    ││   │
  │  │  │    - 用于性能分析                                           ││   │
  │  │  └─────────────────────────────────────────────────────────────┘│   │
  │  │                                                                 │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                    │                                    │
  │                                    ▼                                    │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ JNI
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         Native 层 (C++)                                  │
  ├─────────────────────────────────────────────────────────────────────────┤
  │                                                                         │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │                 android.view.DisplayEventReceiver                │   │
  │  │  源码: frameworks/base/core/jni/android_view_DisplayEventReceiver.cpp│
  │  ├─────────────────────────────────────────────────────────────────┤   │
  │  │                                                                 │   │
  │  │  NativeDisplayEventReceiver                                    │   │
  │  │  - 通过 Looper 监听 VSync fd                                   │   │
  │  │  - 调用 nativeScheduleVsync() 请求 VSync                       │   │
  │  │                                                                 │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                    │                                    │
  │                                    ▼                                    │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │                     Looper (Native)                              │   │
  │  │  源码: system/core/libutils/Looper.cpp                          │   │
  │  ├─────────────────────────────────────────────────────────────────┤   │
  │  │                                                                 │   │
  │  │  - addFd() 监听 VSync fd                                       │   │
  │  │  - pollOnce() 等待事件                                         │   │
  │  │  - 使用 epoll 机制监听多个 fd                                  │   │
  │  │                                                                 │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                    │                                    │
  │                                    ▼                                    │
  └─────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ /dev/... (设备文件)
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         HAL / 内核层                                     │
  ├─────────────────────────────────────────────────────────────────────────┤
  │                                                                         │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │                   VSync 信号源                                   │   │
  │  ├─────────────────────────────────────────────────────────────────┤   │
  │  │                                                                 │   │
  │  │  硬件 VSync (HWComposer)                                        │   │
  │  │  - 显示硬件每 16.67ms (60Hz) 产生一个 VSync 信号                │   │
  │  │  - 通过 /dev/graphics/fb0 或 /dev/dri/card0 传递               │   │
  │  │                                                                 │   │
  │  │  软件 VSync (DispSync)                                          │   │
  │  │  - 模拟 VSync 信号                                              │   │
  │  │  - 用于没有硬件 VSync 的设备                                    │   │
  │  │                                                                 │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                    │                                    │
  │                                    ▼                                    │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │                   SurfaceFlinger                                 │   │
  │  │  源码: frameworks/native/services/surfaceflinger/               │   │
  │  ├─────────────────────────────────────────────────────────────────┤   │
  │  │                                                                 │   │
  │  │  - 接收硬件 VSync 信号                                         │   │
  │  │  - 分发 VSync 到所有连接的 Surface                             │   │
  │  │  - 触发图层合成                                                 │   │
  │  │                                                                 │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 2.8.2 VSync 信号产生与传递

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VSync 信号产生与传递流程                             │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 硬件层 - VSync 产生                                                 │
  │                                                                         │
  │     显示器硬件 (60Hz = 16.67ms/帧)                                      │
  │         │                                                               │
  │         │  垂直同步信号 (VSync)                                         │
  │         │  - 表示一帧扫描完成，开始下一帧                               │
  │         │  - 由显示控制器 (Display Controller) 产生                     │
  │         ▼                                                               │
  │     内核驱动 (DRM/KMS 或 Framebuffer)                                   │
  │         │                                                               │
  │         │  /dev/dri/card0 或 /dev/graphics/fb0                         │
  │         ▼                                                               │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. SurfaceFlinger - VSync 分发                                         │
  │                                                                         │
  │     SurfaceFlinger                                                      │
  │         │                                                               │
  │         │  onVSyncReceived()                                            │
  │         │                                                               │
  │         ├──► 分发给所有 EventThread                                     │
  │         │         │                                                     │
  │         │         ▼                                                     │
  │         │    BitTube (Socket 通信)                                      │
  │         │         │                                                     │
  │         │         ▼                                                     │
  │         │    应用进程的 DisplayEventReceiver                            │
  │         │                                                               │
  │         └──► 触发 SurfaceFlinger 合成                                   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. 应用进程 - VSync 接收                                               │
  │                                                                         │
  │     NativeDisplayEventReceiver                                          │
  │         │                                                               │
  │         │  监听 mReceiverFd (通过 Looper.addFd)                        │
  │         │                                                               │
  │         ▼                                                               │
  │     Looper.pollOnce() 返回                                              │
  │         │                                                               │
  │         │  有数据可读 (VSync 信号到达)                                  │
  │         │                                                               │
  │         ▼                                                               │
  │     handleEvent()                                                       │
  │         │                                                               │
  │         │  读取 VSync 时间戳                                            │
  │         │                                                               │
  │         ▼                                                               │
  │     Java 层 DisplayEventReceiver.onVsync()                             │
  │         │                                                               │
  │         ▼                                                               │
  │     FrameDisplayEventReceiver.onVsync()                                │
  │         │                                                               │
  │         ▼                                                               │
  │     Choreographer.doFrame()                                            │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         VSync 时序图                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  时间轴 (ms) →

  0         16.67     33.33     50        66.67     83.33
  │          │         │         │         │         │
  │  VSync   │  VSync  │  VSync  │  VSync  │  VSync  │
  │    │     │    │    │    │    │    │    │    │    │
  ▼    ▼     ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼
  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
  │Frame 1│  │Frame 2│  │Frame 3│  │Frame 4│  │Frame 5│
  │       │  │       │  │       │  │       │  │       │
  │ INPUT │  │ INPUT │  │ INPUT │  │ INPUT │  │ INPUT │
  │ ANIM  │  │ ANIM  │  │ ANIM  │  │ ANIM  │  │ ANIM  │
  │TRAVERS│  │TRAVERS│  │TRAVERS│  │TRAVERS│  │TRAVERS│
  │COMMIT │  │COMMIT │  │COMMIT │  │COMMIT │  │COMMIT │
  └───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘
      │          │          │          │          │
      │ 合成     │ 合成     │ 合成     │ 合成     │ 合成
      │ 上屏     │ 上屏     │ 上屏     │ 上屏     │ 上屏
      ▼          ▼          ▼          ▼          ▼
   ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
   │显示1│    │显示2│    │显示3│    │显示4│    │显示5│
   └─────┘    └─────┘    └─────┘    └─────┘    └─────┘

  理想情况: 每帧在 16.67ms 内完成 INPUT → ANIM → TRAVERSAL → COMMIT
  掉帧情况: 某帧超过 16.67ms，跳过后续帧
```

#### 2.8.3 FrameDisplayEventReceiver 底层实现

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FrameDisplayEventReceiver 完整流程                  │
│  源码: frameworks/base/core/java/android/view/Choreographer.java           │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Java 层: FrameDisplayEventReceiver                                     │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  private final class FrameDisplayEventReceiver                          │
  │          extends DisplayEventReceiver                                   │
  │          implements Runnable {                                          │
  │                                                                         │
  │      private boolean mHavePendingVsync;                                 │
  │      private long mTimestampNanos;                                      │
  │                                                                         │
  │      // ★★★ VSync 信号到达时调用 ★★★                                    │
  │      @Override                                                          │
  │      public void onVsync(long timestampNanos, int frame,                │
  │              int vsyncSource) {                                         │
  │          // 1. 保存时间戳                                               │
  │          mTimestampNanos = timestampNanos;                              │
  │          mHavePendingVsync = true;                                      │
  │                                                                         │
  │          // 2. 将自己作为 Runnable post 到主线程                        │
  │          Message msg = Message.obtain(mHandler, this);                  │
  │          msg.setAsynchronous(true);  // 异步消息，不受同步屏障影响      │
  │          mHandler.sendMessageAtFrontOfQueue(msg);                       │
  │      }                                                                  │
  │                                                                         │
  │      // ★★★ Runnable.run() 在主线程执行 ★★★                            │
  │      @Override                                                          │
  │      public void run() {                                                │
  │          mHavePendingVsync = false;                                     │
  │          // 执行帧处理                                                  │
  │          doFrame(mTimestampNanos, mFrame);                              │
  │      }                                                                  │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ JNI 调用
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Native 层: android_view_DisplayEventReceiver.cpp                       │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  class NativeDisplayEventReceiver : public DisplayEventReceiver {       │
  │                                                                         │
  │      // 请求 VSync 信号                                                 │
  │      status_t NativeDisplayEventReceiver::scheduleVsync() {             │
  │          // 调用 DisplayEventReceiver::scheduleVsync()                  │
  │          return DisplayEventReceiver::scheduleVsync();                  │
  │      }                                                                  │
  │                                                                         │
  │      // VSync 信号到达时的回调                                          │
  │      void NativeDisplayEventReceiver::onVsync(                          │
  │              nsecs_t timestamp, int32_t id, uint32_t count) {           │
  │          // 通过 JNI 回调 Java 层的 onVsync 方法                        │
  │          JNIEnv* env = AndroidRuntime::getJNIEnv();                     │
  │          env->CallVoidMethod(mReceiverObjGlobal,                        │
  │                  gDisplayEventReceiverClassInfo.onVsync,                │
  │                  timestamp, id, count);                                 │
  │      }                                                                  │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Native 层: DisplayEventReceiver (libs/gui)                             │
  │  源码: frameworks/native/libs/gui/DisplayEventReceiver.cpp              │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  status_t DisplayEventReceiver::scheduleVsync() {                       │
  │      if (mConnection == NULL) {                                         │
  │          // 创建与 SurfaceFlinger 的连接                                │
  │          mConnection = SurfaceFlinger::createConnection();              │
  │      }                                                                  │
  │      // 发送请求到 SurfaceFlinger                                       │
  │      return mConnection->requestNextVsync();                            │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 2.8.4 Choreographer.doFrame() 源码详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Choreographer.doFrame() 源码详解                    │
│  源码: frameworks/base/core/java/android/view/Choreographer.java           │
└─────────────────────────────────────────────────────────────────────────────┘

  void doFrame(long frameTimeNanos, int frame) {
      final long startNanos;
      synchronized (mLock) {
          if (!mFrameScheduled) {
              return;  // 没有调度的帧，直接返回
          }
          
          startNanos = System.nanoTime();
          
          // ★★★ 计算帧延迟 (jitter) ★★★
          final long jitterNanos = startNanos - frameTimeNanos;
          
          // ★★★ 掉帧检测 ★★★
          if (jitterNanos >= mFrameIntervalNanos) {
              // 计算跳过了多少帧
              final long skippedFrames = jitterNanos / mFrameIntervalNanos;
              if (skippedFrames >= SKIPPED_FRAME_WARNING_LIMIT) {
                  // 默认 SKIPPED_FRAME_WARNING_LIMIT = 30
                  // 打印掉帧警告
                  Log.i(TAG, "Skipped " + skippedFrames + " frames!  "
                          + "The application may be doing too much work on its main thread.");
              }
              
              // 计算帧偏移，用于校正后续帧的时间
              final long lastFrameOffset = jitterNanos % mFrameIntervalNanos;
              frameTimeNanos = startNanos - lastFrameOffset;
          }
          
          mFrameScheduled = false;
      }
      
      try {
          Trace.traceBegin(Trace.TRACE_TAG_VIEW, "Choreographer#doFrame");
          AnimationUtils.lockAnimationClock(frameTimeNanos / TimeUtils.NANOS_PER_MS);
          
          // ★★★ 阶段 1: 处理输入事件 ★★★
          mFrameInfo.markInputHandlingStart();
          doCallbacks(Choreographer.CALLBACK_INPUT, frameTimeNanos);
          
          // ★★★ 阶段 2: 处理动画 ★★★
          mFrameInfo.markAnimationsStart();
          doCallbacks(Choreographer.CALLBACK_ANIMATION, frameTimeNanos);
          
          // ★★★ 阶段 3: 处理 View 遍历 (measure/layout/draw) ★★★
          mFrameInfo.markPerformTraversalsStart();
          doCallbacks(Choreographer.CALLBACK_TRAVERSAL, frameTimeNanos);
          
          // ★★★ 阶段 4: 提交 ★★★
          doCallbacks(Choreographer.CALLBACK_COMMIT, frameTimeNanos);
          
      } finally {
          AnimationUtils.unlockAnimationClock();
          Trace.traceEnd(Trace.TRACE_TAG_VIEW);
      }
  }


  // doCallbacks() - 执行指定类型的回调
  void doCallbacks(int callbackType, long frameTimeNanos) {
      CallbackRecord callbacks;
      synchronized (mLock) {
          // 1. 从队列中取出到期的回调
          final long now = System.nanoTime();
          callbacks = mCallbackQueues[callbackType].extractDueCallbacksLocked(now);
          if (callbacks == null) {
              return;
          }
          mCallbacksRunning = true;
          
          // 2. 检查是否需要延迟
          // ...
      }
      
      try {
          // 3. 执行所有回调
          CallbackRecord nextCallback;
          while (callbacks != null) {
              nextCallback = callbacks.next;
              callbacks.next = null;
              
              // 执行回调
              callbacks.run(frameTimeNanos);
              
              callbacks = nextCallback;
          }
      } finally {
          synchronized (mLock) {
              mCallbacksRunning = false;
          }
      }
  }
```

#### 2.8.5 postCallback() 流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Choreographer.postCallback() 流程                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ViewRootImpl.scheduleTraversals()
              │
              │  mChoreographer.postCallback(CALLBACK_TRAVERSAL, runnable, null)
              ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Choreographer.postCallback()                                           │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  public void postCallback(int callbackType, Runnable action,           │
  │          Object token) {                                                │
  │      postCallbackDelayed(callbackType, action, token, 0);              │
  │  }                                                                      │
  │                                                                         │
  │  public void postCallbackDelayed(int callbackType, Runnable action,    │
  │          Object token, long delayMillis) {                              │
  │      // 1. 参数校验                                                    │
  │      if (action == null) {                                              │
  │          throw new IllegalArgumentException("action must not be null");│
  │      }                                                                  │
  │      if (callbackType < 0 || callbackType > CALLBACK_LAST) {           │
  │          throw new IllegalArgumentException("callbackType is invalid");│
  │      }                                                                  │
  │                                                                         │
  │      // 2. 加入回调队列                                                │
  │      synchronized (mLock) {                                             │
  │          final long now = SystemClock.uptimeMillis();                   │
  │          final long dueTime = now + delayMillis;                        │
  │          mCallbackQueues[callbackType].addCallbackLocked(              │
  │                  dueTime, action, token);                               │
  │                                                                         │
  │          // 3. 如果是立即执行，请求 VSync                              │
  │          if (dueTime <= now) {                                          │
  │              scheduleFrameLocked(now);                                  │
  │          }                                                              │
  │      }                                                                  │
  │  }                                                                      │
  │                                                                         │
  │  // 请求 VSync 信号                                                     │
  │  private void scheduleFrameLocked(long now) {                           │
  │      if (!mFrameScheduled) {                                            │
  │          mFrameScheduled = true;                                        │
  │          if (USE_VSYNC) {                                               │
  │              // 使用 VSync                                              │
  │              if (isRunningOnLooperThreadLocked()) {                     │
  │                  // 在主线程，直接请求                                  │
  │                  scheduleVsyncLocked();                                 │
  │              } else {                                                   │
  │                  // 不在主线程，发送消息到主线程                        │
  │                  Message msg = mHandler.obtainMessage(MSG_DO_SCHEDULE_VSYNC);│
  │                  msg.setAsynchronous(true);                             │
  │                  mHandler.sendMessageAtFrontOfQueue(msg);               │
  │              }                                                          │
  │          } else {                                                       │
  │              // 不使用 VSync，直接延迟 16ms 执行                        │
  │              final long nextFrameTime = Math.max(                       │
  │                      mLastFrameTimeNanos / TimeUtils.NANOS_PER_MS +     │
  │                              mFrameIntervalMillis, now);                │
  │              Message msg = mHandler.obtainMessage(MSG_DO_FRAME);        │
  │              msg.setAsynchronous(true);                                 │
  │              mHandler.sendMessageAtTime(msg, nextFrameTime);            │
  │          }                                                              │
  │      }                                                                  │
  │  }                                                                      │
  │                                                                         │
  │  // 请求 VSync                                                          │
  │  private void scheduleVsyncLocked() {                                   │
  │      mDisplayEventReceiver.scheduleVsync();                             │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
              │
              ▼
         FrameDisplayEventReceiver.scheduleVsync()
              │
              │  JNI
              ▼
         NativeDisplayEventReceiver.scheduleVsync()
              │
              │  通过 BitTube 请求 SurfaceFlinger
              ▼
         SurfaceFlinger 分发 VSync 信号
```

#### 2.8.6 CallbackQueue 详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CallbackQueue 数据结构                              │
└─────────────────────────────────────────────────────────────────────────────┘

  // 回调记录
  private static final class CallbackRecord {
      public CallbackRecord next;       // 下一个回调
      public long dueTime;              // 到期时间
      public Object action;             // Runnable 或 FrameCallback
      public Object token;              // 用于取消回调
  }

  // 回调队列
  private final class CallbackQueue {
      private CallbackRecord mHead;     // 队列头
      
      // 添加回调 (按到期时间排序)
      public void addCallbackLocked(long dueTime, Object action, Object token) {
          CallbackRecord callback = obtainCallbackLocked(dueTime, action, token);
          CallbackRecord entry = mHead;
          if (entry == null) {
              mHead = callback;
              return;
          }
          if (dueTime < entry.dueTime) {
              callback.next = entry;
              mHead = callback;
              return;
          }
          while (entry.next != null) {
              if (dueTime < entry.next.dueTime) {
                  callback.next = entry.next;
                  entry.next = callback;
                  return;
              }
              entry = entry.next;
          }
          entry.next = callback;
      }
      
      // 提取到期的回调
      public CallbackRecord extractDueCallbacksLocked(long now) {
          CallbackRecord callbacks = mHead;
          if (callbacks == null || callbacks.dueTime > now) {
              return null;
          }
          CallbackRecord last = callbacks;
          CallbackRecord next = last.next;
          while (next != null) {
              if (next.dueTime > now) {
                  last.next = null;
                  break;
              }
              last = next;
              next = next.next;
          }
          mHead = next;
          return callbacks;
      }
  }


┌─────────────────────────────────────────────────────────────────────────────┐
│                         四种回调队列执行顺序                                │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  CallbackQueue[0]: CALLBACK_INPUT                                       │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │  InputEvent → InputEventReceiver → onInputEvent                 │   │
  │  │  优先级最高，确保用户交互响应                                    │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                    │                                    │
  │                                    ▼                                    │
  │  CallbackQueue[1]: CALLBACK_ANIMATION                                   │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │  ValueAnimator → AnimationHandler → Choreographer               │   │
  │  │  动画更新，计算下一帧的属性值                                    │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                    │                                    │
  │                                    ▼                                    │
  │  CallbackQueue[2]: CALLBACK_TRAVERSAL                                   │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │  ViewRootImpl → scheduleTraversals → performTraversals          │   │
  │  │  View 的 measure、layout、draw                                   │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                    │                                    │
  │                                    ▼                                    │
  │  CallbackQueue[3]: CALLBACK_COMMIT                                      │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │  帧提交后的回调                                                  │   │
  │  │  用于延迟操作 (如 postOnAnimation)                               │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  执行顺序保证:
  1. INPUT 先执行 - 确保触摸事件及时响应
  2. ANIMATION 其次 - 计算动画属性
  3. TRAVERSAL 再次 - 根据动画结果布局绘制
  4. COMMIT 最后 - 帧提交完成后的操作
```

#### 2.8.7 同步屏障与异步消息

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         同步屏障 (Sync Barrier) 机制                        │
└─────────────────────────────────────────────────────────────────────────────┘

  在 scheduleTraversals() 中会插入同步屏障:

  void scheduleTraversals() {
      if (!mTraversalScheduled) {
          mTraversalScheduled = true;
          
          // ★★★ 插入同步屏障 ★★★
          mTraversalBarrier = mHandler.getLooper().getQueue().postSyncBarrier();
          
          // 注册 VSync 回调
          mChoreographer.postCallback(...);
      }
  }

  同步屏障的作用:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  MessageQueue (主线程)                                                  │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │  Message 1 (同步)                                                │   │
  │  │  Message 2 (同步)                                                │   │
  │  │  ══════════════════════════════════════════════════════════════  │   │
  │  │  ★ 同步屏障 (SyncBarrier) ★                                      │   │
  │  │  ══════════════════════════════════════════════════════════════  │   │
  │  │  Message 3 (同步) ← 被屏障阻挡，不会执行                         │   │
  │  │  Message 4 (同步) ← 被屏障阻挡，不会执行                         │   │
  │  │  Message 5 (异步) ← 可以执行，绕过屏障 ★★★                       │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                                                         │
  │  同步屏障确保:                                                          │
  │  - VSync 相关的异步消息优先执行                                        │
  │  - 普通同步消息等待 VSync 处理完成                                    │
  │  - 防止普通消息阻塞绘制                                                │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  VSync 消息是异步消息:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  // FrameDisplayEventReceiver.onVsync()                                │
  │  Message msg = Message.obtain(mHandler, this);                          │
  │  msg.setAsynchronous(true);  // ★★★ 设置为异步消息 ★★★               │
  │  mHandler.sendMessageAtFrontOfQueue(msg);                               │
  │                                                                         │
  │  异步消息可以绕过同步屏障，优先执行                                     │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  移除同步屏障:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  void doTraversal() {                                                   │
  │      if (mTraversalScheduled) {                                         │
  │          mTraversalScheduled = false;                                   │
  │          // ★★★ 移除同步屏障 ★★★                                      │
  │          mHandler.getLooper().getQueue().removeSyncBarrier(            │
  │                  mTraversalBarrier);                                    │
  │          // 执行遍历                                                    │
  │          performTraversals();                                           │
  │      }                                                                  │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 2.8.8 掉帧检测与分析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         掉帧检测与分析                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  掉帧日志:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  I/Choreographer: Skipped 60 frames! The application may be doing       │
  │                   too much work on its main thread.                     │
  │                                                                         │
  │  含义:                                                                  │
  │  - 主线程执行时间超过 60 × 16.67ms ≈ 1秒                               │
  │  - 跳过了 60 帧的绘制                                                   │
  │  - 用户体验到约 1 秒的卡顿                                              │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  掉帧原因分析:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  1. 主线程执行耗时操作                                                  │
  │     - 网络 I/O                                                          │
  │     - 文件 I/O                                                          │
  │     - 数据库操作                                                        │
  │     - 复杂计算                                                          │
  │                                                                         │
  │  2. 布局过于复杂                                                        │
  │     - View 层级过深                                                     │
  │     - measure/layout 耗时过长                                          │
  │                                                                         │
  │  3. 绘制过于复杂                                                        │
  │     - onDraw() 中创建对象                                               │
  │     - 过度绘制 (Overdraw)                                               │
  │                                                                         │
  │  4. 内存频繁 GC                                                         │
  │     - 内存泄漏导致频繁 GC                                               │
  │     - GC 会暂停所有线程                                                 │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  性能分析工具:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  1. GPU Overdraw (开发者选项)                                           │
  │     - 显示过度绘制区域                                                  │
  │     - 蓝色(1x) → 绿色(2x) → 粉色(3x) → 红色(4x+)                       │
  │                                                                         │
  │  2. Profile GPU Rendering (开发者选项)                                  │
  │     - 显示每帧渲染时间                                                  │
  │     - 绿线 = 16ms 阈值                                                  │
  │                                                                         │
  │  3. Systrace / Perfetto                                                 │
  │     - 系统级性能追踪                                                    │
  │     - 可以看到 Choreographer、SurfaceFlinger 的时间线                   │
  │                                                                         │
  │  4. Choreographer#addFrameCallback                                      │
  │     - 自定义帧回调，测量帧间隔                                          │
  │     - 可以检测掉帧                                                      │
  │                                                                         │
  │  Choreographer.getInstance().postFrameCallback(new FrameCallback() {   │
  │      @Override                                                          │
  │      public void doFrame(long frameTimeNanos) {                        │
  │          // 计算帧间隔                                                  │
  │          long frameInterval = frameTimeNanos - lastFrameTime;          │
  │          if (frameInterval > 16_666_667) {  // 超过 16.67ms            │
  │              // 掉帧检测                                                │
  │          }                                                              │
  │          lastFrameTime = frameTimeNanos;                               │
  │          // 继续监听下一帧                                              │
  │          Choreographer.getInstance().postFrameCallback(this);          │
  │      }                                                                  │
  │  });                                                                    │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 2.8.9 Choreographer 与 SurfaceFlinger 关系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Choreographer 与 SurfaceFlinger 关系                │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │                    VSync 信号源 (硬件/软件模拟)                          │
  │                              │                                          │
  │                              │ VSync (16.67ms)                          │
  │                              ▼                                          │
  │  ┌───────────────────────────────────────────────────────────────────┐ │
  │  │                      SurfaceFlinger                                │ │
  │  │  frameworks/native/services/surfaceflinger/                        │ │
  │  │                                                                    │ │
  │  │  职责:                                                             │ │
  │  │  1. 接收硬件 VSync 信号                                           │ │
  │  │  2. 分发 VSync 到所有连接的应用进程                               │ │
  │  │  3. 合成所有 Surface (Layer)                                      │ │
  │  │  4. 提交到显示屏                                                  │ │
  │  └───────────────────────────────┬───────────────────────────────────┘ │
  │                                  │                                      │
  │                    ┌─────────────┴─────────────┐                       │
  │                    │                           │                       │
  │                    ▼                           ▼                       │
  │  ┌─────────────────────────┐   ┌─────────────────────────┐            │
  │  │   应用进程 1            │   │   应用进程 2            │            │
  │  │                         │   │                         │            │
  │  │  Choreographer          │   │  Choreographer          │            │
  │  │       │                 │   │       │                 │            │
  │  │       ▼                 │   │       ▼                 │            │
  │  │  doFrame()              │   │  doFrame()              │            │
  │  │       │                 │   │       │                 │            │
  │  │       ▼                 │   │       ▼                 │            │
  │  │  View 绘制              │   │  View 绘制              │            │
  │  │       │                 │   │       │                 │            │
  │  │       ▼                 │   │       ▼                 │            │
  │  │  Surface (BufferQueue)  │   │  Surface (BufferQueue)  │            │
  │  └───────────┬─────────────┘   └───────────┬─────────────┘            │
  │              │                             │                          │
  │              └──────────────┬──────────────┘                          │
  │                             │                                          │
  │                             ▼                                          │
  │  ┌───────────────────────────────────────────────────────────────────┐ │
  │  │                      SurfaceFlinger                                │ │
  │  │                                                                    │ │
  │  │  合成 Layer 1 + Layer 2 + ... → FrameBuffer → 显示屏              │ │
  │  └───────────────────────────────────────────────────────────────────┘ │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  关键点:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  1. SurfaceFlinger 是系统服务，所有应用共享                            │
  │  2. 每个 VSync 周期，SurfaceFlinger 通知所有应用开始绘制               │
  │  3. 应用完成后，将 Surface 提交给 SurfaceFlinger                       │
  │  4. SurfaceFlinger 在下一个 VSync 合成并显示                           │
  │                                                                         │
  │  时序:                                                                  │
  │  VSync N:   SurfaceFlinger 通知应用                                    │
  │  VSync N+1: 应用完成绘制，SurfaceFlinger 合成上一帧                    │
  │  VSync N+2: 显示 N 帧的内容                                            │
  │                                                                         │
  │  这就是为什么有 2-3 帧的延迟                                           │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 2.9 BufferQueue 与双缓冲机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BufferQueue 架构                                    │
│  源码位置: frameworks/native/libs/gui/BufferQueue.cpp                      │
└─────────────────────────────────────────────────────────────────────────────┘

Android 图形系统采用 生产者-消费者 模型:

┌─────────────────────────────────────────────────────────────────────────────┐
│                         生产者-消费者模型                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
  │    生产者        │         │   BufferQueue   │         │    消费者        │
  │   (Producer)    │ ──────► │   (缓冲队列)     │ ──────► │   (Consumer)    │
  │                 │         │                 │         │                 │
  │  应用 UI 线程    │         │  GraphicBuffer  │         │  SurfaceFlinger │
  │  Surface/Canvas │         │  双缓冲/三缓冲   │         │  显示合成       │
  │  OpenGL ES      │         │                 │         │                 │
  └─────────────────┘         └─────────────────┘         └─────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         缓冲区状态流转                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────┐
  │                                                                          │
  │      ┌──────────┐                    ┌──────────┐                       │
  │      │   FREE   │ ──── dequeue ────► │ DEQUEUED │                       │
  │      │  (空闲)   │                    │  (出队)   │                       │
  │      └────▲─────┘                    └─────┬────┘                       │
  │           │                                │                             │
  │           │                         生产者绘制                             │
  │           │                         (Canvas/OpenGL)                      │
  │           │                                │                             │
  │           │                                ▼                             │
  │      ┌────┴─────┐                    ┌──────────┐                       │
  │      │ ACQUIRED │ ◄──── acquire ──── │  QUEUED  │                       │
  │      │  (获取)   │                    │  (入队)   │                       │
  │      └──────────┘                    └─────┬────┘                       │
  │           │                                │                             │
  │     消费者使用                          queue                             │
  │     (SurfaceFlinger)               (提交到队列)                          │
  │           │                                │                             │
  │           │                                ▼                             │
  │           │                          生产者调用                          │
  │           │                          Surface.unlockCanvasAndPost()       │
  │           │                                                              │
  │     release (释放)                                                       │
  │           │                                                              │
  └───────────┴──────────────────────────────────────────────────────────────┘

  状态说明:
  ┌────────────┬──────────────────────────────────────────────────────────────┐
  │  状态       │  说明                                                       │
  ├────────────┼──────────────────────────────────────────────────────────────┤
  │  FREE      │  空闲，可被生产者 dequeue 获取                              │
  │  DEQUEUED  │  已被生产者获取，正在绘制                                   │
  │  QUEUED    │  已绘制完成，在队列中等待消费者获取                         │
  │  ACQUIRED  │  已被消费者 (SurfaceFlinger) 获取，正在合成显示             │
  └────────────┴──────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         双缓冲 vs 三缓冲                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  双缓冲 (Double Buffering):
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │   Buffer A          Buffer B                                           │
  │  ┌─────────┐       ┌─────────┐                                        │
  │  │ 显示中   │       │ 绘制中   │                                        │
  │  │ (Front) │       │ (Back)  │                                        │
  │  └─────────┘       └─────────┘                                        │
  │       │                 │                                              │
  │       │    VSync 时     │                                              │
  │       │    交换缓冲     │                                              │
  │       ▼                 ▼                                              │
  │  ┌─────────┐       ┌─────────┐                                        │
  │  │ 绘制中   │       │ 显示中   │                                        │
  │  │ (Back)  │       │ (Front) │                                        │
  │  └─────────┘       └─────────┘                                        │
  │                                                                         │
  │  优点: 内存占用小                                                       │
  │  缺点: 如果绘制超时，会等待下一帧 VSync (掉帧)                          │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  三缓冲 (Triple Buffering):
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │   Buffer A          Buffer B          Buffer C                         │
  │  ┌─────────┐       ┌─────────┐       ┌─────────┐                      │
  │  │ 显示中   │       │ 就绪     │       │ 绘制中   │                      │
  │  │ (Front) │       │ (Ready) │       │ (Back)  │                      │
  │  └─────────┘       └─────────┘       └─────────┘                      │
  │                                                                         │
  │  优点: 即使一帧绘制慢，也有备用缓冲，减少掉帧                           │
  │  缺点: 内存占用更大，增加一帧延迟                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  Android 默认: 双缓冲，可通过调试选项开启三缓冲


┌─────────────────────────────────────────────────────────────────────────────┐
│                         Surface 与 BufferQueue 关系                         │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ViewRootImpl                                                           │
  │       │                                                                 │
  │       ▼                                                                 │
  │  Surface (生产者端)                                                      │
  │       │                                                                 │
  │       │  lockCanvas() → dequeueBuffer()                                │
  │       │  解锁画布 → queueBuffer()                                       │
  │       ▼                                                                 │
  │  BufferQueue                                                            │
  │       │                                                                 │
  │       │  acquireBuffer() → 消费者获取                                   │
  │       │  releaseBuffer() → 消费者释放                                   │
  │       ▼                                                                 │
  │  SurfaceFlinger (消费者)                                                │
  │       │                                                                 │
  │       │  合成所有 Layer                                                 │
  │       │  提交到 Display                                                 │
  │       ▼                                                                 │
  │  屏幕                                                                   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 2.10 渲染合成流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         渲染合成完整流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 应用进程绘制                                                        │
  │     performDraw()                                                       │
  │         │                                                               │
  │         ▼                                                               │
  │     draw() → Canvas 绘制                                                │
  │         │                                                               │
  │         ▼                                                               │
  │     Surface.lockCanvas()                                                │
  │         │  - dequeueBuffer() 获取缓冲区                                │
  │         │  - 返回 Canvas 对象                                           │
  │         ▼                                                               │
  │     Canvas 绘制操作                                                     │
  │         │  - drawRect/drawCircle/drawText...                           │
  │         ▼                                                               │
  │     Surface.unlockCanvasAndPost()                                       │
  │         │  - queueBuffer() 提交缓冲区                                  │
  │         │  - 通知 SurfaceFlinger 有新帧                                │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. SurfaceFlinger 合成                                                 │
  │                                                                         │
  │     ┌─────────────────────────────────────────────────────────────┐    │
  │     │                     SurfaceFlinger                           │    │
  │     │                                                               │    │
  │     │  Layer 1 (App UI)      Layer 2 (StatusBar)   Layer 3 (Nav)  │    │
  │     │  ┌─────────────┐       ┌─────────────┐      ┌─────────────┐ │    │
  │     │  │  App 窗口    │       │  状态栏     │      │  导航栏     │ │    │
  │     │  └─────────────┘       └─────────────┘      └─────────────┘ │    │
  │     │         │                    │                    │         │    │
  │     │         └────────────────────┼────────────────────┘         │    │
  │     │                              │                              │    │
  │     │                              ▼                              │    │
  │     │                    ┌─────────────────┐                      │    │
  │     │                    │  合成 (Composer) │                      │    │
  │     │                    │  - GLES/HWC     │                      │    │
  │     │                    └────────┬────────┘                      │    │
  │     │                             │                               │    │
  │     │                             ▼                               │    │
  │     │                    ┌─────────────────┐                      │    │
  │     │                    │   FrameBuffer   │                      │    │
  │     │                    │    (显示屏)     │                      │    │
  │     │                    └─────────────────┘                      │    │
  │     │                                                               │    │
  │     └─────────────────────────────────────────────────────────────┘    │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. 显示到屏幕                                                          │
  │                                                                         │
  │     SurfaceFlinger ──► Display Hardware ──► 屏幕                        │
  │                                                                         │
  │     在 VSync 信号到来时，将合成后的帧提交到显示屏                        │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 2.11 View 绘制多层级架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 绘制多层级架构                                 │
│  从应用层到硬件层的完整调用链                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级 1: 应用层 (Application Layer)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Activity / Dialog / PopupWindow / Toast                                   │
│       │                                                                     │
│       ▼                                                                     │
│  PhoneWindow                                                               │
│       │                                                                     │
│       ▼                                                                     │
│  DecorView (继承 FrameLayout)                                              │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  View 树 (View Hierarchy)                                           │   │
│  │                                                                     │   │
│  │  ViewGroup                                                          │   │
│  │     ├── View                                                        │   │
│  │     ├── ViewGroup                                                   │   │
│  │     │     ├── View                                                  │   │
│  │     │     └── View                                                  │   │
│  │     └── View                                                        │   │
│  │                                                                     │   │
│  │  绘制方法:                                                          │   │
│  │  - onMeasure()  计算尺寸                                           │   │
│  │  - onLayout()   确定位置                                           │   │
│  │  - onDraw()     绘制内容 (使用 Canvas)                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  关键类: Activity, Window, DecorView, View, ViewGroup                      │
│  源码: frameworks/base/core/java/android/view/                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ WindowManager.addView()
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级 2: WindowManager 层                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  应用进程                                                            │   │
│  │                                                                     │   │
│  │  WindowManagerImpl                                                  │   │
│  │       │                                                             │   │
│  │       ▼                                                             │   │
│  │  WindowManagerGlobal                                                │   │
│  │       │                                                             │   │
│  │       │  管理所有 Window:                                           │   │
│  │       │  - mViews: 所有 View                                        │   │
│  │       │  - mRoots: 所有 ViewRootImpl                                │   │
│  │       │  - mParams: 所有 LayoutParams                               │   │
│  │       │                                                             │   │
│  │       ▼                                                             │   │
│  │  ViewRootImpl                                                       │   │
│  │       │                                                             │   │
│  │       │  核心职责:                                                  │   │
│  │       │  1. 管理 View 树的测量、布局、绘制                          │   │
│  │       │  2. 与 WMS 通信                                             │   │
│  │       │  3. 接收 VSync 信号                                         │   │
│  │       │  4. 管理输入事件                                            │   │
│  │       │                                                             │   │
│  │       └──► IWindowSession (Binder 客户端)                           │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  关键类: WindowManagerImpl, WindowManagerGlobal, ViewRootImpl              │
│  源码: frameworks/base/core/java/android/view/                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ Binder IPC (IWindowSession)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级 3: WMS 层 (Window Manager Service)             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  System Server 进程                                                 │   │
│  │                                                                     │   │
│  │  WindowManagerService (WMS)                                         │   │
│  │       │                                                             │   │
│  │       │  核心职责:                                                  │   │
│  │       │  1. 窗口管理 (添加/移除/更新)                               │   │
│  │       │  2. 窗口布局计算                                            │   │
│  │       │  3. 窗口层级 (Z-Order) 管理                                 │   │
│  │       │  4. 窗口动画                                                │   │
│  │       │  5. 输入事件分发                                            │   │
│  │       │  6. 分配 Surface                                            │   │
│  │       │                                                             │   │
│  │       ├── WindowState (窗口状态)                                    │   │
│  │       ├── WindowToken (窗口令牌)                                    │   │
│  │       ├── Session (会话管理)                                        │   │
│  │       ├── DisplayContent (显示内容)                                 │   │
│  │       └── WindowSurfaceController (Surface 控制)                    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  关键类: WindowManagerService, WindowState, WindowToken                    │
│  源码: frameworks/base/services/core/java/com/android/server/wm/           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ SurfaceControl / Surface
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级 4: Surface 层 (图形缓冲区)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Surface (应用端)                                                   │   │
│  │       │                                                             │   │
│  │       │  绘制接口:                                                  │   │
│  │       │  - lockCanvas()     获取画布                               │   │
│  │       │  - unlockCanvasAndPost()  提交绘制结果                      │   │
│  │       │                                                             │   │
│  │       ▼                                                             │   │
│  │  BufferQueue (缓冲队列)                                             │   │
│  │       │                                                             │   │
│  │       │  生产者-消费者模型:                                         │   │
│  │       │  - 生产者: Surface (应用 UI 线程)                           │   │
│  │       │  - 消费者: SurfaceFlinger                                   │   │
│  │       │  - 缓冲区: GraphicBuffer (双缓冲/三缓冲)                    │   │
│  │       │                                                             │   │
│  │       │  状态流转:                                                  │   │
│  │       │  FREE → DEQUEUED → QUEUED → ACQUIRED → FREE                │   │
│  │       │                                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  关键类: Surface, SurfaceControl, BufferQueue, GraphicBuffer               │
│  源码: frameworks/native/libs/gui/                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ BufferQueue (共享内存)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级 5: SurfaceFlinger 层 (合成服务)                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  SurfaceFlinger (独立进程)                                          │   │
│  │                                                                     │   │
│  │  核心职责:                                                          │   │
│  │  1. 接收硬件 VSync 信号                                             │   │
│  │  2. 管理所有 Layer (图层)                                           │   │
│  │  3. 合成所有 Layer 到 FrameBuffer                                   │   │
│  │  4. 提交到显示屏                                                    │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  Layer 合成                                                  │   │   │
│  │  │                                                             │   │   │
│  │  │  Layer 1 (App UI)      Layer 2 (StatusBar)   Layer 3 (Nav) │   │   │
│  │  │  ┌─────────────┐       ┌─────────────┐      ┌─────────────┐│   │   │
│  │  │  │  应用窗口    │       │  状态栏     │      │  导航栏     ││   │   │
│  │  │  └─────────────┘       └─────────────┘      └─────────────┘│   │   │
│  │  │         │                    │                    │        │   │   │
│  │  │         └────────────────────┼────────────────────┘        │   │   │
│  │  │                              │                             │   │   │
│  │  │                              ▼                             │   │   │
│  │  │                    ┌─────────────────┐                    │   │   │
│  │  │                    │     合成器       │                    │   │   │
│  │  │                    │  GLES / HWC     │                    │   │   │
│  │  │                    └─────────────────┘                    │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  关键类: SurfaceFlinger, Layer, HWComposer                                  │
│  源码: frameworks/native/services/surfaceflinger/                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ FrameBuffer
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级 6: HAL 层 (硬件抽象层)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Hardware Composer (HWC)                                            │   │
│  │                                                                     │   │
│  │  职责:                                                              │   │
│  │  - 硬件合成 (比 GPU 合成更省电)                                     │   │
│  │  - VSync 信号产生                                                   │   │
│  │  - 管理显示屏                                                       │   │
│  │                                                                     │   │
│  │  接口:                                                              │   │
│  │  - HWC2 (Android 8.0+)                                             │   │
│  │  - Gralloc (图形缓冲区分配)                                         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  关键类: HWComposer, ComposerHal                                            │
│  源码: hardware/interfaces/graphics/                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ /dev/dri/card0 / /dev/graphics/fb0
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级 7: 内核层 (Kernel Layer)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Linux Kernel                                                       │   │
│  │                                                                     │   │
│  │  DRM/KMS (Direct Rendering Manager)                                │   │
│  │  - 显示驱动                                                         │   │
│  │  - VSync 信号产生                                                   │   │
│  │  - FrameBuffer 管理                                                 │   │
│  │                                                                     │   │
│  │  GPU 驱动                                                          │   │
│  │  - Adreno (Qualcomm)                                               │   │
│  │  - Mali (ARM)                                                      │   │
│  │  - PowerVR (Imagination)                                           │   │
│  │                                                                     │   │
│  │  ION/DMA-BUF (内存管理)                                            │   │
│  │  - 图形缓冲区分配                                                   │   │
│  │  - 零拷贝共享                                                       │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  关键模块: DRM/KMS, GPU Driver, ION/DMA-BUF                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级 8: 硬件层 (Hardware Layer)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  显示硬件                                                           │   │
│  │                                                                     │   │
│  │  Display Controller (显示控制器)                                    │   │
│  │  - 产生 VSync 信号 (60Hz = 16.67ms)                                 │   │
│  │  - 扫描 FrameBuffer                                                 │   │
│  │                                                                     │   │
│  │  Panel (显示屏)                                                     │   │
│  │  - LCD / OLED                                                       │   │
│  │  - 分辨率、刷新率                                                   │   │
│  │                                                                     │   │
│  │  GPU (图形处理器)                                                   │   │
│  │  - 3D 渲染                                                          │   │
│  │  - 合成加速                                                         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.12 层级调用完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级调用完整流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 用户点击屏幕                                                        │
  │     硬件层 → 内核层 → InputReader → InputDispatcher → 应用进程        │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. 应用响应点击                                                        │
  │     Activity → View.onTouchEvent() → View.invalidate()                │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. 请求重绘                                                            │
  │     ViewRootImpl.scheduleTraversals()                                  │
  │         → Choreographer.postCallback()                                 │
  │         → 等待 VSync                                                    │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  4. VSync 信号到达                                                      │
  │     硬件 → 内核 DRM → SurfaceFlinger → EventThread                     │
  │         → BitTube → NativeDisplayEventReceiver                         │
  │         → FrameDisplayEventReceiver.onVsync()                          │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  5. 执行绘制                                                            │
  │     Choreographer.doFrame()                                            │
  │         → doCallbacks(CALLBACK_TRAVERSAL)                              │
  │         → ViewRootImpl.doTraversal()                                   │
  │         → performTraversals()                                          │
  │             → performMeasure() → performLayout() → performDraw()       │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  6. 绘制到 Surface                                                      │
  │     Canvas 绘制操作                                                     │
  │         → Surface.lockCanvas() → dequeueBuffer()                       │
  │         → 绘制到 GraphicBuffer                                         │
  │         → Surface.unlockCanvasAndPost() → queueBuffer()                │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  7. SurfaceFlinger 合成                                                 │
  │     acquireBuffer() → 读取所有 Layer                                   │
  │         → GLES/HWC 合成 → FrameBuffer                                  │
  │         → releaseBuffer()                                              │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  8. 显示到屏幕                                                          │
  │     FrameBuffer → DRM/KMS → Display Controller → Panel                 │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 2.13 层级总结表

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 绘制层级总结                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────┬───────────────────────┬───────────────────────────────────────────┐
│  层级    │  名称                  │  关键组件                                 │
├─────────┼───────────────────────┼───────────────────────────────────────────┤
│  1      │  应用层                │  Activity, Window, DecorView, View       │
│         │  Application Layer    │  onMeasure/onLayout/onDraw               │
├─────────┼───────────────────────┼───────────────────────────────────────────┤
│  2      │  WindowManager 层     │  WindowManagerImpl, ViewRootImpl         │
│         │                       │  IWindowSession                          │
├─────────┼───────────────────────┼───────────────────────────────────────────┤
│  3      │  WMS 层               │  WindowManagerService, WindowState       │
│         │  System Server        │  WindowToken, Session                    │
├─────────┼───────────────────────┼───────────────────────────────────────────┤
│  4      │  Surface 层           │  Surface, BufferQueue, GraphicBuffer     │
│         │  Graphics Buffer      │  生产者-消费者模型                        │
├─────────┼───────────────────────┼───────────────────────────────────────────┤
│  5      │  SurfaceFlinger 层    │  SurfaceFlinger, Layer, HWComposer       │
│         │  Composition Service  │  GLES/HWC 合成                           │
├─────────┼───────────────────────┼───────────────────────────────────────────┤
│  6      │  HAL 层               │  Hardware Composer, Gralloc              │
│         │  Hardware Abstraction │  HWC2 接口                               │
├─────────┼───────────────────────┼───────────────────────────────────────────┤
│  7      │  内核层               │  DRM/KMS, GPU Driver, ION/DMA-BUF        │
│         │  Linux Kernel         │  VSync 信号产生                          │
├─────────┼───────────────────────┼───────────────────────────────────────────┤
│  8      │  硬件层               │  Display Controller, GPU, Panel          │
│         │  Hardware             │  LCD/OLED 显示屏                         │
└─────────┴───────────────────────┴───────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         跨层通信方式                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬───────────────────────────────────────────────────────┐
│  通信方式            │  使用场景                                             │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Binder IPC         │  应用进程 ↔ System Server (WMS)                       │
│                     │  IWindowSession.addToDisplay()                        │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  JNI                │  Java ↔ Native 层                                     │
│                     │  Choreographer ↔ DisplayEventReceiver                 │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  共享内存 (ASHMEM)   │  BufferQueue (GraphicBuffer 共享)                    │
│                     │  应用进程 ↔ SurfaceFlinger                            │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Socket (BitTube)   │  SurfaceFlinger ↔ 应用进程 VSync 通知                 │
│                     │  EventThread ↔ DisplayEventReceiver                   │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  /dev/... 设备文件   │  内核 ↔ HAL 层                                        │
│                     │  /dev/dri/card0, /dev/graphics/fb0                   │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  系统调用 (ioctl)   │  HAL ↔ 内核                                           │
│                     │  DRM ioctl, GPU ioctl                                 │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 3. WindowManager 架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WindowManager 架构                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         应用进程                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  WindowManager (接口)                                                       │
│       │                                                                     │
│       ▼                                                                     │
│  WindowManagerImpl                                                         │
│       │                                                                     │
│       ▼                                                                     │
│  WindowManagerGlobal                                                       │
│       │                                                                     │
│       ├── mViews: ArrayList<View>         // 所有 View                     │
│       ├── mRoots: ArrayList<ViewRootImpl> // 所有 ViewRootImpl             │
│       └── mParams: ArrayList<LayoutParams> // 所有 LayoutParams            │
│                                                                             │
│       │                                                                     │
│       ▼                                                                     │
│  ViewRootImpl                                                              │
│       │                                                                     │
│       │  IWindowSession (Binder 客户端)                                    │
│       │                                                                     │
└───────┼─────────────────────────────────────────────────────────────────────┘
        │
        │ Binder IPC
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         System Server                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  WindowManagerService (WMS)                                                │
│       │                                                                     │
│       ├── WindowState - 窗口状态                                           │
│       ├── WindowToken - 窗口令牌                                           │
│       └── Session - 会话管理                                               │
│                                                                             │
│       │                                                                     │
│       ▼                                                                     │
│  SurfaceFlinger (显示合成)                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Measure 测量流程

### 4.1 Measure 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Measure 测量流程                                    │
└─────────────────────────────────────────────────────────────────────────────┘

ViewRootImpl.performMeasure()
        │
        ▼
View.measure(widthMeasureSpec, heightMeasureSpec)
        │  - final 方法，不可重写
        │  - 内部调用 onMeasure()
        ▼
View.onMeasure(widthMeasureSpec, heightMeasureSpec)
        │  - 可重写，自定义测量逻辑
        │  - 必须调用 setMeasuredDimension()
        ▼
ViewGroup (如果是 ViewGroup)
        │
        ├── measureChildren() - 遍历子 View
        │       │
        │       ▼
        │   measureChild() - 获取子 View 的 MeasureSpec
        │       │
        │       ▼
        │   child.measure() - 递归调用子 View
        │
        └── setMeasuredDimension() - 保存测量结果
```

### 4.2 MeasureSpec 详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MeasureSpec 详解                                    │
└─────────────────────────────────────────────────────────────────────────────┘

MeasureSpec = Mode (高2位) + Size (低30位)

┌────────────────┬───────────────────────────────────────────────────────────┐
│  Mode          │  说明                                                     │
├────────────────┼───────────────────────────────────────────────────────────┤
│  EXACTLY       │  精确模式: match_parent 或 具体数值 (100dp)              │
│                │  View 尺寸 = MeasureSpec.getSize()                       │
├────────────────┼───────────────────────────────────────────────────────────┤
│  AT_MOST       │  最大模式: wrap_content                                  │
│                │  View 尺寸 <= MeasureSpec.getSize()                      │
├────────────────┼───────────────────────────────────────────────────────────┤
│  UNSPECIFIED   │  未指定模式: 无限制                                       │
│                │  用于 ScrollView、ListView 内部                          │
└────────────────┴───────────────────────────────────────────────────────────┘


// MeasureSpec 生成规则
┌─────────────────────────────────────────────────────────────────────────────┐
│  Parent Spec      │  Child LayoutParams   │  Child MeasureSpec             │
├───────────────────┼────────────────────────┼────────────────────────────────┤
│  EXACTLY          │  match_parent          │  EXACTLY (parentSize)          │
│  EXACTLY          │  wrap_content          │  AT_MOST (parentSize)          │
│  EXACTLY          │  100dp                 │  EXACTLY (100dp)               │
│  AT_MOST          │  match_parent          │  AT_MOST (parentSize)          │
│  AT_MOST          │  wrap_content          │  AT_MOST (parentSize)          │
│  UNSPECIFIED      │  match_parent          │  UNSPECIFIED (0)               │
└───────────────────┴────────────────────────┴────────────────────────────────┘
```

### 4.3 onMeasure 标准实现

```java
// View.onMeasure() 默认实现
protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
    setMeasuredDimension(
            getDefaultSize(getSuggestedMinimumWidth(), widthMeasureSpec),
            getDefaultSize(getSuggestedMinimumHeight(), heightMeasureSpec));
}

// 自定义 View 的标准写法
@Override
protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
    int widthMode = MeasureSpec.getMode(widthMeasureSpec);
    int widthSize = MeasureSpec.getSize(widthMeasureSpec);
    int heightMode = MeasureSpec.getMode(heightMeasureSpec);
    int heightSize = MeasureSpec.getSize(heightMeasureSpec);
    
    int desiredWidth = 200;  // 期望宽度
    int desiredHeight = 200; // 期望高度
    
    int width, height;
    
    // 处理宽度
    if (widthMode == MeasureSpec.EXACTLY) {
        width = widthSize;
    } else if (widthMode == MeasureSpec.AT_MOST) {
        width = Math.min(desiredWidth, widthSize);
    } else {
        width = desiredWidth;
    }
    
    // 处理高度
    if (heightMode == MeasureSpec.EXACTLY) {
        height = heightSize;
    } else if (heightMode == MeasureSpec.AT_MOST) {
        height = Math.min(desiredHeight, heightSize);
    } else {
        height = desiredHeight;
    }
    
    // ★★★ 必须调用 ★★★
    setMeasuredDimension(width, height);
}
```

---

## 5. Layout 布局流程

### 5.1 Layout 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Layout 布局流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

ViewRootImpl.performLayout()
        │
        ▼
View.layout(l, t, r, b)
        │  - 设置 View 的四个顶点位置
        │  - 调用 onLayout()
        ▼
View.onLayout(changed, l, t, r, b)
        │  - View: 空实现
        │  - ViewGroup: 抽象方法，必须实现
        ▼
ViewGroup.onLayout()
        │
        ├── 计算每个子 View 的位置
        │
        └── 调用 child.layout() 设置子 View 位置
```

### 5.2 onLayout 标准实现

```java
// ViewGroup 必须实现 onLayout
@Override
protected void onLayout(boolean changed, int left, int top, int right, int bottom) {
    int childLeft = getPaddingLeft();
    int childTop = getPaddingTop();
    
    final int count = getChildCount();
    for (int i = 0; i < count; i++) {
        View child = getChildAt(i);
        if (child.getVisibility() != View.GONE) {
            int childWidth = child.getMeasuredWidth();
            int childHeight = child.getMeasuredHeight();
            
            // 设置子 View 位置
            child.layout(childLeft, childTop,
                    childLeft + childWidth, childTop + childHeight);
            
            // 更新下一个子 View 的起始位置
            childTop += childHeight;
        }
    }
}
```

---

## 6. Draw 绘制流程

### 6.1 Draw 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Draw 绘制流程                                       │
└─────────────────────────────────────────────────────────────────────────────┘

ViewRootImpl.performDraw()
        │
        ▼
ViewRootImpl.draw()
        │
        ▼
DecorView.draw(Canvas)
        │
        │  public void draw(Canvas canvas) {
        │      // 1. 绘制背景
        │      drawBackground(canvas);
        │      
        │      // 2. 绘制内容 (自定义 View 重写此方法)
        │      onDraw(canvas);
        │      
        │      // 3. 绘制子 View (ViewGroup 实现)
        │      dispatchDraw(canvas);
        │      
        │      // 4. 绘制装饰 (滚动条、前景)
        │      onDrawForeground(canvas);
        │  }
        ▼
绘制完成
```

### 6.2 onDraw 实现

```java
@Override
protected void onDraw(Canvas canvas) {
    super.onDraw(canvas);
    
    // 绘制背景
    canvas.drawColor(Color.WHITE);
    
    // 绘制圆形
    Paint paint = new Paint();
    paint.setColor(Color.RED);
    paint.setAntiAlias(true);
    canvas.drawCircle(getWidth() / 2, getHeight() / 2, 100, paint);
    
    // 绘制文字
    paint.setColor(Color.BLACK);
    paint.setTextSize(40);
    canvas.drawText("Hello", 100, 100, paint);
}
```

---

## 7. 常见问题

### 7.1 为什么子线程不能更新 UI？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         为什么子线程不能更新 UI？                            │
└─────────────────────────────────────────────────────────────────────────────┘

原因: ViewRootImpl.checkThread() 检查线程

void checkThread() {
    if (mThread != Thread.currentThread()) {
        throw new CalledFromWrongThreadException(
            "Only the original thread that created a view hierarchy "
            + "can touch its views.");
    }
}

mThread 是创建 ViewRootImpl 的线程 (主线程)

解决方案:
1. Activity.runOnUiThread()
2. View.post()
3. Handler.post()
4. 使用 LiveData / RxJava / Flow
```

### 7.2 invalidate() vs requestLayout()

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                invalidate() vs requestLayout()                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┬───────────────────────────────────────────────────────────┐
│  方法           │  作用                                                     │
├─────────────────┼───────────────────────────────────────────────────────────┤
│  invalidate()   │  只触发 onDraw()，重绘 View                               │
│                 │  不改变尺寸和位置                                         │
│                 │  用于: 改变颜色、文字等                                   │
├─────────────────┼───────────────────────────────────────────────────────────┤
│  requestLayout()│  触发 onMeasure() → onLayout() → onDraw()                │
│                 │  重新测量、布局、绘制                                     │
│                 │  用于: 改变尺寸、位置                                     │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

### 7.3 View.post() 为什么可以获取宽高？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│          View.post() 为什么可以获取宽高？                                    │
└─────────────────────────────────────────────────────────────────────────────┘

View.post() 将 Runnable 放入队列，在 View 的测量完成后执行:

public boolean post(Runnable action) {
    final AttachInfo attachInfo = mAttachInfo;
    if (attachInfo != null) {
        return attachInfo.mHandler.post(action);
    }
    // 保存到队列，attach 后执行
    getRunQueue().post(action);
    return true;
}

执行时机: ViewRootImpl.performTraversals() 后
         此时 View 已经完成测量，可以获取宽高
```

---

## 8. 总结

### 8.1 核心流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 绘制完整流程                                   │
└─────────────────────────────────────────────────────────────────────────────┘

Activity.onCreate()
        │
        ▼
setContentView() → 创建 DecorView
        │
        ▼
Activity.onResume()
        │
        ▼
WindowManager.addView(mDecor)
        │
        ▼
WindowManagerGlobal.addView()
        │
        │  ViewRootImpl root = new ViewRootImpl();
        │  root.setView(view);
        ▼
ViewRootImpl.requestLayout()
        │
        ▼
scheduleTraversals()
        │
        │  等待 VSync 信号
        ▼
performTraversals()
        │
        ├──► performMeasure() → measure() → onMeasure()
        │
        ├──► performLayout() → layout() → onLayout()
        │
        └──► performDraw() → draw() → onDraw()
                │
                ▼
          SurfaceFlinger 合成显示
```

### 8.2 关键类总结

| 类 | 职责 |
|---|---|
| ViewRootImpl | View 树根，连接 WMS，触发绘制 |
| Choreographer | VSync 调度，帧同步 |
| WindowManager | 窗口管理 |
| DecorView | 顶级 View |
| MeasureSpec | 测量规格 (Mode + Size) |

---

*本文档由 OpenClaw 生成*
