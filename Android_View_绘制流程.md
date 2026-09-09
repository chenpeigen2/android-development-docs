# Android View 绘制流程完全指南

> 作者：OpenClaw | 日期：2026-03-08

---

## 目录

- [1. 概述](#1-概述)
    - [1.1 核心三阶段](#11-核心三阶段)
    - [1.2 整体架构图](#12-整体架构图)
- [2. ViewRootImpl 核心机制](#2-viewrootimpl-核心机制)
    - [2.1 ViewRootImpl 概述](#21-viewrootimpl-概述)
    - [2.2 ViewRootImpl 创建流程](#22-viewrootimpl-创建流程)
    - [2.3 setView 完整流程](#23-setview-完整流程)
    - [2.4 requestLayout 流程](#24-requestlayout-流程)
    - [2.5 scheduleTraversals 流程](#25-scheduletraversals-流程)
    - [2.6 performTraversals 完整流程](#26-performtraversals-完整流程)
    - [2.7 完整帧绘制流程](#27-完整帧绘制流程)
    - [2.8 Choreographer 详解](#28-choreographer-详解)
        - [2.8.1 Choreographer 架构总览](#281-choreographer-架构总览)
        - [2.8.2 VSync 信号产生与传递](#282-vsync-信号产生与传递)
        - [2.8.3 FrameDisplayEventReceiver 底层实现](#283-framedisplayeventreceiver-底层实现)
        - [2.8.4 Choreographer.doFrame() 源码详解](#284-choreographerdoframe-源码详解)
        - [2.8.5 postCallback() 流程](#285-postcallback-流程)
        - [2.8.6 CallbackQueue 详解](#286-callbackqueue-详解)
        - [2.8.7 同步屏障与异步消息](#287-同步屏障与异步消息)
        - [2.8.8 掉帧检测与分析](#288-掉帧检测与分析)
        - [2.8.9 Choreographer 与 SurfaceFlinger 关系](#289-choreographer-与-surfaceflinger-关系)
    - [2.9 BufferQueue 与双缓冲机制](#29-bufferqueue-与双缓冲机制)
    - [2.10 渲染合成流程](#210-渲染合成流程)
    - [2.11 Canvas 到 Surface 调用详解](#211-canvas-到-surface-调用详解)
        - [2.11.1 Canvas 与 Surface 关系](#2111-canvas-与-surface-关系)
        - [2.11.2 View 绘制到 Canvas 流程](#2112-view-绘制到-canvas-流程)
        - [2.11.3 软件绘制流程 (drawSoftware)](#2113-软件绘制流程-drawsoftware)
        - [2.11.4 Canvas 如何绑定到 Surface](#2114-canvas-如何绑定到-surface)
        - [2.11.5 硬件加速绘制流程 (ThreadedRenderer)](#2115-硬件加速绘制流程-threadedrenderer)
    - [2.12 Surface 到 SurfaceFlinger 调用详解](#212-surface-到-surfaceflinger-调用详解)
        - [2.12.1 Surface 创建流程：useClientSurface 决定协议](#2121-surface-创建流程useclientsurface-决定协议)
        - [2.12.2 BufferQueue 创建与组件：BLAST 建立生产端](#2122-bufferqueue-创建与组件blast-建立生产端)
        - [2.12.3 应用绘制到 SurfaceFlinger 完整流程](#2123-应用绘制到-surfaceflinger-完整流程)
        - [2.12.4 跨进程通信方式与职责边界](#2124-跨进程通信方式与职责边界)
    - [2.13 View 绘制多层级架构](#213-view-绘制多层级架构)
    - [2.14 层级调用完整流程](#214-层级调用完整流程)
        - [2.14.1 软件绘制完整流程](#2141-软件绘制完整流程)
        - [2.14.2 硬件加速绘制完整流程](#2142-硬件加速绘制完整流程)
        - [2.14.3 两种模式对比流程图](#2143-两种模式对比流程图)
    - [2.15 层级总结表](#215-层级总结表)
        - [2.15.1 软件绘制 vs 硬件加速 层级差异](#2151-软件绘制-vs-硬件加速-层级差异)
        - [2.15.2 关键类差异](#2152-关键类差异)
        - [2.15.3 跨层通信方式](#2153-跨层通信方式)
- [3. WindowManager 架构](#3-windowmanager-架构)
- [4. Measure 测量流程](#4-measure-测量流程)
    - [4.1 Measure 流程图](#41-measure-流程图)
    - [4.2 MeasureSpec 详解](#42-measurespec-详解)
    - [4.3 onMeasure 标准实现](#43-onmeasure-标准实现)
- [5. Layout 布局流程](#5-layout-布局流程)
    - [5.1 Layout 流程图](#51-layout-流程图)
    - [5.2 onLayout 标准实现](#52-onlayout-标准实现)
- [6. Draw 绘制流程](#6-draw-绘制流程)
    - [6.1 Draw 流程图](#61-draw-流程图)
    - [6.2 onDraw 实现](#62-ondraw-实现)
- [7. 常见问题](#7-常见问题)
    - [7.1 为什么子线程不能更新 UI？](#71-为什么子线程不能更新-ui)
    - [7.2 invalidate() vs requestLayout()](#72-invalidate-vs-requestlayout)
    - [7.3 View.post() 为什么可以获取宽高？](#73-viewpost-为什么可以获取宽高)
- [8. 软件渲染 vs 硬件渲染 全面对比](#8-软件渲染-vs-硬件渲染-全面对比)
    - [8.1 阶段 1: 触发更新 (相同)](#81-阶段-1-触发更新-相同)
    - [8.2 阶段 2: VSync 处理 (相同)](#82-阶段-2-vsync-处理-相同)
    - [8.3 阶段 3: 测量与布局 (相同)](#83-阶段-3-测量与布局-相同)
    - [8.4 阶段 4: 绘制入口 (分叉点)](#84-阶段-4-绘制入口-分叉点)
    - [8.5 阶段 5: Canvas 获取 (重大差异)](#85-阶段-5-canvas-获取-重大差异)
    - [8.6 阶段 6: 执行绘制 (重大差异)](#86-阶段-6-执行绘制-重大差异)
    - [8.7 阶段 7: 提交结果 (重大差异)](#87-阶段-7-提交结果-重大差异)
    - [8.8 阶段 8: SurfaceFlinger 合成 (相同)](#88-阶段-8-surfaceflinger-合成-相同)
    - [8.9 完整对比总结图](#89-完整对比总结图)
    - [8.10 关键类对比表](#810-关键类对比表)
    - [8.11 性能对比](#811-性能对比)
- [9. 总结](#9-总结)
    - [9.1 核心流程图](#91-核心流程图)
    - [9.2 关键类总结](#92-关键类总结)

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

### 2.11 Canvas 到 Surface 调用详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Canvas 到 Surface 调用详解                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.11.1 Canvas 与 Surface 关系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Canvas 与 Surface 关系                              │
└─────────────────────────────────────────────────────────────────────────────┘

  Canvas 是绘图的 API 接口，Surface 是图形缓冲区的抽象:

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ┌─────────────────┐         ┌─────────────────┐                       │
  │  │     Canvas      │ ──────► │     Surface     │                       │
  │  │   (绘图 API)    │         │  (缓冲区抽象)   │                       │
  │  │                 │         │                 │                       │
  │  │  drawRect()     │         │  lockCanvas()   │                       │
  │  │  drawCircle()   │         │  unlockCanvas() │                       │
  │  │  drawText()     │         │                 │                       │
  │  │  drawBitmap()   │         └────────┬────────┘                       │
  │  │  ...            │                  │                                 │
  │  └─────────────────┘                  ▼                                 │
  │                              ┌─────────────────┐                       │
  │                              │  BufferQueue    │                       │
  │                              │  (缓冲队列)     │                       │
  │                              └─────────────────┘                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  Canvas 类型:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  1. 软件 Canvas (Skia)                                                  │
  │     - 使用 CPU 绘制                                                     │
  │     - Bitmap 作为底层存储                                               │
  │     - new Canvas(bitmap)                                                │
  │                                                                         │
  │  2. 硬件 Canvas (HWUI)                                                  │
  │     - 使用 GPU 绘制 (OpenGL ES / Vulkan)                               │
  │     - RenderNode 作为底层                                               │
  │     - View.getHardwareCanvas() / RecordingCanvas                        │
  │                                                                         │
  │  Android 4.0+ 默认硬件加速，使用 HWUI                                   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 2.11.2 View 绘制到 Canvas 流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 绘制到 Canvas 流程                             │
│  源码: frameworks/base/core/java/android/view/ViewRootImpl.java            │
└─────────────────────────────────────────────────────────────────────────────┘

  ViewRootImpl.performDraw()
              │
              ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ViewRootImpl.draw()                                                    │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  private void draw(boolean fullRedrawNeeded) {                          │
  │      Surface surface = mSurface;                                        │
  │      if (surface == null || !surface.isValid()) {                       │
  │          return;                                                        │
  │      }                                                                  │
  │                                                                         │
  │      // 1. 检查是否使用硬件加速                                         │
  │      if (mAttachInfo.mThreadedRenderer != null                          │
  │              && mAttachInfo.mThreadedRenderer.isEnabled()) {            │
  │          // ★★★ 硬件加速绘制 ★★★                                        │
  │          mAttachInfo.mThreadedRenderer.draw(mView, mAttachInfo,        │
  │                  this, mHandler, (mHardwareDrawCallback != null));      │
  │      } else {                                                           │
  │          // ★★★ 软件绘制 ★★★                                            │
  │          if (!drawSoftware(surface, mAttachInfo, xOffset, yOffset,      │
  │                  scalingRequired, dirty, path)) {                       │
  │              return;                                                    │
  │          }                                                              │
  │      }                                                                  │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
              │
              ├──────────────────┬──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       硬件加速绘制         软件绘制            (详情如下)
```

#### 2.11.3 软件绘制流程 (drawSoftware)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         软件绘制流程 (drawSoftware)                         │
│  源码: frameworks/base/core/java/android/view/ViewRootImpl.java            │
└─────────────────────────────────────────────────────────────────────────────┘

  ViewRootImpl.draw()
              │
              ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ViewRootImpl.drawSoftware()                                            │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  private boolean drawSoftware(Surface surface, AttachInfo attachInfo,  │
  │          int xoff, int yoff, boolean scalingRequired, Rect dirty,      │
  │          Path clip) {                                                   │
  │                                                                         │
  │      // 1. 锁定 Canvas ★★★                                              │
  │      Canvas canvas;                                                     │
  │      try {                                                              │
  │          final Rect dirtyRect = mDirty;                                 │
  │          // 调用 Surface.lockCanvas()                                   │
  │          canvas = mSurface.lockCanvas(dirtyRect);                       │
  │      } catch (Surface.OutOfResourcesException e) {                      │
  │          return false;                                                  │
  │      }                                                                  │
  │                                                                         │
  │      try {                                                              │
  │          // 2. 设置 Canvas 属性                                         │
  │          canvas.translate(-xoff, -yoff);                                │
  │          if (mTranslator != null) {                                     │
  │              mTranslator.translateCanvas(canvas);                       │
  │          }                                                              │
  │          canvas.setScreenDensity(scalingRequired ? mNoncompatDensity : 0);│
  │                                                                         │
  │          // 3. 执行 View 树绘制 ★★★                                     │
  │          mView.draw(canvas);                                            │
  │                                                                         │
  │      } finally {                                                        │
  │          // 4. 解锁并提交 Canvas ★★★                                    │
  │          surface.unlockCanvasAndPost(canvas);                           │
  │      }                                                                  │
  │      return true;                                                       │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 2.11.4 Canvas 如何绑定到 Surface

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Canvas 如何绑定到 Surface                           │
│  核心原理: Canvas 的底层内存指向 Surface 中的 GraphicBuffer               │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  关键问题: Canvas.drawRect() 等绘制操作如何写入 Surface？               │
  │                                                                         │
  │  答案: Canvas 持有一个指向 Surface 缓冲区的内存指针                     │
  │        所有绘制操作直接写入这块共享内存                                 │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  详细绑定流程:
  ─────────────────────────────────────────────────────────────────────────────

  Step 1: Surface.lockCanvas() 请求缓冲区
  ─────────────────────────────────────────────────────────────────────────────
  Java:  Surface.lockCanvas() → lockCanvasNative()
  JNI:   nativeLockCanvas()
         │
         ▼
  Native (android_view_Surface.cpp):
         // 1. 获取 Surface
         sp<Surface> surface = ...;
         
         // 2. ★★★ 锁定缓冲区 ★★★
         ANativeWindowBuffer* buffer;
         surface->lock(&buffer, dirtyRect);
         // 内部: dequeueBuffer() → 获取 GraphicBuffer
         
         // 3. buffer->bits 就是缓冲区的内存地址!
         void* pixels = buffer->bits;
         
         // 4. ★★★ 创建 Canvas，绑定到这块内存 ★★★
         SkBitmap bitmap;
         bitmap.setPixels(pixels);  // 关键: 绑定内存
         
         Canvas* canvas = new SkiaCanvas(bitmap);
         return canvas;

  Step 2: Canvas 绘制直接写入内存
  ─────────────────────────────────────────────────────────────────────────────
  canvas.drawRect(0, 0, 100, 100, paint);
         │
         ▼
  SkiaCanvas::drawRect()
         │
         ▼
  Skia 引擎直接写入 pixels 内存
         │  for (y = top; y < bottom; y++) {
         │      for (x = left; x < right; x++) {
         │          pixels[x + y * stride] = color;
         │      }
         │  }
         ▼
  GraphicBuffer (共享内存)

  Step 3: Surface.unlockCanvasAndPost() 提交缓冲区
  ─────────────────────────────────────────────────────────────────────────────
  Java:  Surface.unlockCanvasAndPost(canvas)
  JNI:   nativeUnlockCanvasAndPost()
         │
         ▼
  Native: surface->unlockAndPost()
         │
         ▼
  queueBuffer() → 提交给 BufferQueue → SurfaceFlinger 可消费


┌─────────────────────────────────────────────────────────────────────────────┐
│                         Canvas 与 Surface 内存关系图                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ┌─────────────────┐      指向        ┌────────────────────────────┐   │
  │  │     Canvas      │ ───────────────► │   GraphicBuffer (共享内存) │   │
  │  │  (绘图 API)     │                  │                            │   │
  │  │                 │                  │  pixels (void*):           │   │
  │  │  drawRect()  ───┼──────┐           │  ┌──────────────────────┐  │   │
  │  │  drawCircle()───┼───┐  │           │  │ 像素数据 (RGBA)      │  │   │
  │  │  drawText()  ───┼─┐ │  │           │  │ [0,0][1,0][2,0]...   │  │   │
  │  │                 │ │ │  │  直接写入 │  │ [0,1][1,1][2,1]...   │  │   │
  │  └─────────────────┘ │ │  └─────────►│  │ ...                  │  │   │
  │                      │ │             │  └──────────────────────┘  │   │
  │                      │ │             │                            │   │
  │                      │ │             │  属于: Surface → BufferQueue│   │
  │                      │ │             └────────────────────────────┘   │
  │                      │ │                                                │
  │                      ▼ ▼                                                │
  │  所有绘制操作直接修改这块内存，SurfaceFlinger 可以直接读取            │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         硬件加速模式的 Canvas 绑定                          │
└─────────────────────────────────────────────────────────────────────────────┘

  硬件加速模式下，Canvas 不直接绑定内存，而是记录绘制命令:

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ┌─────────────────┐                                                   │
  │  │ RecordingCanvas │     不绑定实际内存                                │
  │  │                 │                                                   │
  │  │  drawRect()     │ ──► 记录命令: { type: DRAW_RECT, rect, paint }   │
  │  │  drawCircle()   │ ──► 记录命令: { type: DRAW_CIRCLE, cx, cy, r }   │
  │  │  drawText()     │ ──► 记录命令: { type: DRAW_TEXT, text, x, y }    │
  │  └────────┬────────┘                                                   │
  │           │                                                             │
  │           ▼                                                             │
  │  ┌─────────────────┐                                                   │
  │  │   DisplayList   │     存储所有绘制命令                              │
  │  │   (命令列表)    │     [cmd1, cmd2, cmd3, ...]                       │
  │  └────────┬────────┘                                                   │
  │           │                                                             │
  │           ▼ RenderThread (异步)                                         │
  │  ┌─────────────────┐                                                   │
  │  │  OpenGL ES /    │     GPU 执行命令，渲染到 FBO                      │
  │  │  Vulkan         │     FBO 绑定到 GraphicBuffer                      │
  │  └────────┬────────┘                                                   │
  │           │                                                             │
  │           ▼                                                             │
  │  ┌─────────────────┐                                                   │
  │  │ GraphicBuffer   │     最终像素数据                                  │
  │  └─────────────────┘                                                   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  对比总结:
  ┌─────────────────┬─────────────────────────┬───────────────────────────────┐
  │                 │  软件绘制 (Skia)        │  硬件加速 (HWUI)              │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  Canvas 类型    │  SkiaCanvas             │  RecordingCanvas              │
  │  绑定方式       │  直接绑定内存指针       │  不绑定，记录命令             │
  │  绘制时机       │  draw() 立即写入内存    │  RenderThread 异步执行        │
  │  内存写入       │  CPU 逐像素写入         │  GPU 并行渲染                 │
  │  缓冲区         │  GraphicBuffer.bits     │  FBO → GraphicBuffer          │
  └─────────────────┴─────────────────────────┴───────────────────────────────┘
```

#### 2.11.5 硬件加速绘制流程 (ThreadedRenderer)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         硬件加速绘制流程 (ThreadedRenderer)                 │
│  源码: frameworks/base/core/java/android/view/ThreadedRenderer.java        │
└─────────────────────────────────────────────────────────────────────────────┘
```

##### 2.11.5.1 ThreadedRenderer 架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ThreadedRenderer 架构                               │
└─────────────────────────────────────────────────────────────────────────────┘

  ThreadedRenderer 是 Android 硬件加速渲染的核心:

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │                    ThreadedRenderer                              │   │
  │  │  源码: frameworks/base/core/java/android/view/ThreadedRenderer.java│  │
  │  ├─────────────────────────────────────────────────────────────────┤   │
  │  │                                                                 │   │
  │  │  核心组件:                                                      │   │
  │  │                                                                 │   │
  │  │  1. RenderNode (渲染节点)                                       │   │
  │  │     - 每个 View 对应一个 RenderNode                             │   │
  │  │     - 存储 View 的绘制命令 (DisplayList)                        │   │
  │  │     - 存储属性: 位移、旋转、缩放、透明度等                       │   │
  │  │                                                                 │   │
  │  │  2. RecordingCanvas (录制画布)                                  │   │
  │  │     - 记录 draw* 绘制命令，不立即执行                           │   │
  │  │     - 命令存储到 DisplayList                                    │   │
  │  │                                                                 │   │
  │  │  3. RenderThread (渲染线程)                                     │   │
  │  │     - 独立线程，执行 GPU 渲染                                   │   │
  │  │     - 使用 OpenGL ES 或 Vulkan                                  │   │
  │  │     - 异步执行，不阻塞 UI 线程                                  │   │
  │  │                                                                 │   │
  │  │  4. DisplayList (显示列表)                                      │   │
  │  │     - 存储一系列绘制命令                                        │   │
  │  │     - 可重用、可合并优化                                        │   │
  │  │                                                                 │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

##### 2.11.5.2 ThreadedRenderer.draw() 完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ThreadedRenderer.draw() 完整流程                    │
│  源码: frameworks/base/core/java/android/view/ThreadedRenderer.java        │
└─────────────────────────────────────────────────────────────────────────────┘

  ViewRootImpl.draw()
              │
              │  mAttachInfo.mThreadedRenderer.draw()
              ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ThreadedRenderer.draw()                                                │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  void draw(View view, AttachInfo attachInfo, DrawCallbacks callbacks,  │
  │          Handler handler, boolean hasCallbacks) {                       │
  │                                                                         │
  │      // 1. 准备帧信息                                                  │
  │      final FrameInfo frameInfo = attachInfo.mFrameInfo;                 │
  │      frameInfo.setVsync(...);                                           │
  │                                                                         │
  │      // 2. 更新 View 树的 DisplayList ★★★                              │
  │      updateHierarchyDisplayList(view);                                  │
  │                                                                         │
  │      // 3. 注册动画回调                                                │
  │      if (callbacks != null) {                                           │
  │          callbacks.onFrameDrawn(this);                                  │
  │      }                                                                  │
  │                                                                         │
  │      // 4. 同步 DisplayList 到 RenderThread 并请求渲染 ★★★             │
  │      int syncResult = syncAndDrawFrame(frameInfo);                      │
  │                                                                         │
  │      // 5. RenderThread 异步执行 GPU 渲染                              │
  │      // (不阻塞 UI 线程，UI 线程可以继续处理下一帧)                     │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  updateHierarchyDisplayList() 详解:
  ─────────────────────────────────────────────────────────────────────────────

  private void updateHierarchyDisplayList(View view) {
      // 从根 View 开始递归更新
      view.updateDisplayListIfDirty();
  }
```

##### 2.11.5.3 View.updateDisplayListIfDirty() 详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View.updateDisplayListIfDirty() 详解                │
│  源码: frameworks/base/core/java/android/view/View.java                    │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  public RenderNode updateDisplayListIfDirty() {                         │
  │      final RenderNode renderNode = mRenderNode;                         │
  │                                                                         │
  │      // 检查是否需要重建 DisplayList                                   │
  │      if ((mPrivateFlags & PFLAG_DRAWING_CACHE_VALID) == 0 ||           │
  │              renderNode == null ||                                      │
  │              (mPrivateFlags & PFLAG_DIRTY_MASK) != 0) {                 │
  │                                                                         │
  │          // ★★★ 1. 开始记录 DisplayList ★★★                            │
  │          final RecordingCanvas canvas = renderNode.beginRecording(     │
  │                  getWidth(), getHeight());                              │
  │                                                                         │
  │          try {                                                          │
  │              // ★★★ 2. 执行绘制 (记录命令，不实际绘制) ★★★             │
  │              if (mLayerType == LAYER_TYPE_SOFTWARE) {                   │
  │                  // 软件层: 使用 Bitmap 缓存                            │
  │                  buildDrawingCache(true);                               │
  │                  Bitmap cache = getDrawingCache(true);                  │
  │                  if (cache != null) {                                   │
  │                      canvas.drawBitmap(cache, 0, 0, mLayerPaint);       │
  │                  }                                                      │
  │              } else {                                                   │
  │                  // 硬件层: 直接记录绘制命令                            │
  │                  // dispatchDraw() 会递归调用子 View                    │
  │                  dispatchDraw(canvas);                                  │
  │                  onDraw(canvas);                                        │
  │              }                                                          │
  │          } finally {                                                    │
  │              // ★★★ 3. 结束记录 ★★★                                    │
  │              renderNode.endRecording();                                 │
  │          }                                                              │
  │      }                                                                  │
  │                                                                         │
  │      return renderNode;                                                 │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  关键点:
  ─────────────────────────────────────────────────────────────────────────────

  1. RecordingCanvas 是 "录制" 画布
     - canvas.drawRect() 不会立即绘制
     - 而是将命令记录到 DisplayList 中
     - 类似于录制视频，先记录，后播放

  2. RenderNode 存储 DisplayList
     - 每个 View 有一个 RenderNode
     - RenderNode 包含该 View 的所有绘制命令
     - 形成一个 RenderNode 树 (与 View 树对应)

  3. 命令录制完成后，交给 RenderThread 执行
```

##### 2.11.5.4 硬件加速 Canvas 获取详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         硬件加速 Canvas 获取详解                            │
│  RecordingCanvas 与 SkiaCanvas 的区别                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

###### 2.11.5.4.1 硬件加速模式不调用 Surface.lockCanvas()

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 硬件加速模式 vs 软件绘制模式 Canvas 获取对比                 │
└─────────────────────────────────────────────────────────────────────────────┘

  软件绘制模式:
  ─────────────────────────────────────────────────────────────────────────────
  ViewRootImpl.drawSoftware()
       │
       │  canvas = surface.lockCanvas()  // ★★★ 从 Surface 获取 Canvas
       │  // 此时 Canvas 绑定到 GraphicBuffer 内存
       │
       ▼
  mView.draw(canvas)  // 直接写入内存
       │
       ▼
  surface.unlockCanvasAndPost(canvas)


  硬件加速模式:
  ─────────────────────────────────────────────────────────────────────────────
  ThreadedRenderer.draw()
       │
       │  // ★★★ 不调用 Surface.lockCanvas() ★★★
       │  // Canvas 从 RenderNode 获取，不是从 Surface
       │
       ▼
  view.updateDisplayListIfDirty()
       │
       │  canvas = renderNode.beginRecording()  // ★★★ 从 RenderNode 获取 Canvas
       │  // 此时 Canvas 不绑定任何内存，只是命令记录器
       │
       ▼
  view.draw(canvas)  // 只记录命令
       │
       ▼
  renderNode.endRecording()


  关键区别:
  ┌─────────────────┬─────────────────────────┬───────────────────────────────┐
  │                 │  软件绘制               │  硬件加速                     │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  Canvas 来源    │  Surface.lockCanvas()   │  RenderNode.beginRecording() │
  │  Canvas 类型    │  SkiaCanvas             │  RecordingCanvas              │
  │  是否绑定内存   │  是 (GraphicBuffer)     │  否 (只是命令记录器)          │
  │  绘制时机       │  立即写入内存           │  记录命令，稍后执行           │
  │  绘制线程       │  UI 线程                │  RenderThread                 │
  └─────────────────┴─────────────────────────┴───────────────────────────────┘
```

###### 2.11.5.4.2 RenderNode.beginRecording() 源码分析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RenderNode.beginRecording() 源码分析                │
│  源码: frameworks/base/core/java/android/view/RenderNode.java              │
│  Native: frameworks/base/libs/hwui/RenderNode.cpp                          │
└─────────────────────────────────────────────────────────────────────────────┘

  Java 层:
  ─────────────────────────────────────────────────────────────────────────────

  // RenderNode.java
  public RecordingCanvas beginRecording(int width, int height) {
      // 调用 Native 方法获取 RecordingCanvas
      return RecordingCanvas.obtain(this, width, height);
  }


  // RecordingCanvas.java
  public final class RecordingCanvas extends BaseRecordingCanvas {
      
      // 从对象池获取 RecordingCanvas
      static RecordingCanvas obtain(@NonNull RenderNode node, int width, int height) {
          // 1. 从对象池获取或创建
          RecordingCanvas canvas = sPool.acquire();
          if (canvas == null) {
              canvas = new RecordingCanvas();
          }
          
          // 2. 初始化
          canvas.mNode = node;
          canvas.setWidth(width);
          canvas.setHeight(height);
          
          // 3. 调用 Native 初始化
          nInitializeDisplayListCanvas(canvas.mNativeCanvasWrapper, 
                  node.mNativeRenderNode, width, height);
          
          return canvas;
      }
  }


  Native 层:
  ─────────────────────────────────────────────────────────────────────────────

  // android_graphics_DisplayListCanvas.cpp
  static void nInitializeDisplayListCanvas(JNIEnv* env, jobject clazz,
          jlong canvasPtr, jlong nodePtr, jint width, jint height) {
      
      // 1. 获取 RenderNode
      RenderNode* renderNode = reinterpret_cast<RenderNode*>(nodePtr);
      
      // 2. 获取或创建 DisplayList
      DisplayList* displayList = renderNode->getDisplayList();
      if (displayList == nullptr) {
          displayList = new DisplayList();
      }
      
      // 3. 创建 RecordingCanvas (C++ 层)
      // 这个 Canvas 不绑定内存，只记录命令到 DisplayList
      RecordingCanvas* canvas = new RecordingCanvas(displayList);
      
      // 4. 设置画布大小
      canvas->setBounds(width, height);
  }


  RecordingCanvas (C++) 的实现:
  ─────────────────────────────────────────────────────────────────────────────

  // frameworks/base/libs/hwui/RecordingCanvas.cpp
  
  class RecordingCanvas : public Canvas {
  private:
      DisplayList* mDisplayList;  // 存储绘制命令的列表
      
  public:
      // 绘制矩形 - 记录命令，不实际绘制
      void drawRect(float left, float top, float right, float bottom, 
              const SkPaint& paint) override {
          
          // 创建绘制命令
          DrawRectOp* op = new DrawRectOp(left, top, right, bottom, paint);
          
          // ★★★ 只记录命令，不执行 ★★★
          mDisplayList->addDrawOp(op);
      }
      
      // 绘制圆形 - 记录命令
      void drawCircle(float cx, float cy, float radius, const SkPaint& paint) {
          DrawCircleOp* op = new DrawCircleOp(cx, cy, radius, paint);
          mDisplayList->addDrawOp(op);
      }
      
      // 绘制文字 - 记录命令
      void drawText(const char* text, float x, float y, const SkPaint& paint) {
          DrawTextOp* op = new DrawTextOp(text, x, y, paint);
          mDisplayList->addDrawOp(op);
      }
  };
```

###### 2.11.5.4.3 RecordingCanvas 与 SkiaCanvas 内部结构对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RecordingCanvas vs SkiaCanvas 内部结构              │
└─────────────────────────────────────────────────────────────────────────────┘

  SkiaCanvas (软件绘制):
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  SkiaCanvas                                                             │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  成员变量:                                                              │
  │  - SkBitmap mBitmap;        // 位图，存储像素数据                      │
  │  - SkCanvas* mCanvas;       // Skia 画布                               │
  │  - void* mPixels;           // ★★★ 指向 GraphicBuffer 内存 ★★★        │
  │                                                                         │
  │  drawRect() 执行:                                                       │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │ void drawRect(left, top, right, bottom, paint) {                │   │
  │  │     // 直接写入内存                                             │   │
  │  │     for (y = top; y < bottom; y++) {                            │   │
  │  │         for (x = left; x < right; x++) {                        │   │
  │  │             mPixels[x + y * stride] = paint.getColor();         │   │
  │  │         }                                                       │   │
  │  │     }                                                           │   │
  │  │ }                                                               │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  RecordingCanvas (硬件加速):
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  RecordingCanvas                                                        │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  成员变量:                                                              │
  │  - DisplayList* mDisplayList;    // 存储绘制命令的列表                 │
  │  - RenderNode* mNode;           // 所属的 RenderNode                   │
  │  - int mWidth, mHeight;         // 画布大小                            │
  │  // ★★★ 没有 mPixels，不绑定内存 ★★★                                  │
  │                                                                         │
  │  drawRect() 执行:                                                       │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │ void drawRect(left, top, right, bottom, paint) {                │   │
  │  │     // 创建命令对象                                             │   │
  │  │     DrawRectOp* op = new DrawRectOp();                          │   │
  │  │     op->left = left;                                            │   │
  │  │     op->top = top;                                              │   │
  │  │     op->right = right;                                          │   │
  │  │     op->bottom = bottom;                                        │   │
  │  │     op->paint = paint;                                          │   │
  │  │                                                                 │   │
  │  │     // ★★★ 只添加到列表，不执行 ★★★                             │   │
  │  │     mDisplayList->addDrawOp(op);                                │   │
  │  │ }                                                               │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  DisplayList 结构:
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  DisplayList                                                            │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  class DisplayList {                                                    │
  │      std::vector<DrawOp*> mDrawOps;    // 绘制命令列表                 │
  │                                                                         │
  │      void addDrawOp(DrawOp* op) {                                       │
  │          mDrawOps.push_back(op);                                        │
  │      }                                                                  │
  │  };                                                                     │
  │                                                                         │
  │  // 命令类型 (DrawOp 子类):                                             │
  │  - DrawRectOp        // 矩形                                           │
  │  - DrawCircleOp      // 圆形                                           │
  │  - DrawPathOp        // 路径                                           │
  │  - DrawTextOp        // 文字                                           │
  │  - DrawBitmapOp      // 位图                                           │
  │  - SaveOp            // 保存状态                                       │
  │  - RestoreOp         // 恢复状态                                       │
  │  - ClipRectOp        // 裁剪矩形                                       │
  │  - ConcatMatrixOp    // 矩阵变换                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

###### 2.11.5.4.4 硬件加速绘制完整流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         硬件加速绘制完整流程图                               │
└─────────────────────────────────────────────────────────────────────────────┘

  UI 线程                                    RenderThread
  ──────────                                 ────────────
       │                                           │
       │  ViewRootImpl.performDraw()               │
       │         │                                 │
       │         ▼                                 │
       │  ThreadedRenderer.draw()                  │
       │         │                                 │
       │         ▼                                 │
       │  ┌─────────────────────────────┐         │
       │  │ view.updateDisplayListIfDirty()       │
       │  │         │                    │         │
       │  │         ▼                    │         │
       │  │ canvas = renderNode.        │         │
       │  │     beginRecording()        │         │
       │  │         │                    │         │
       │  │         │ ★★★ Canvas 从     │         │
       │  │         │ RenderNode 获取   │         │
       │  │         │ 不涉及 Surface    │         │
       │  │         ▼                    │         │
       │  │ view.draw(canvas)           │         │
       │  │         │                    │         │
       │  │         │ 只记录命令        │         │
       │  │         │ 不写入内存        │         │
       │  │         ▼                    │         │
       │  │ renderNode.endRecording()   │         │
       │  │         │                    │         │
       │  │         ▼                    │         │
       │  │ DisplayList 已构建完成      │         │
       │  └──────────┬──────────────────┘         │
       │             │                             │
       │             │ syncAndDrawFrame()          │
       │             │ ★★★ 同步到 RenderThread ★★★ │
       │             └────────────────────────────►│
       │                                           │
       │  (UI 线程继续)                            ▼
       │                                ┌─────────────────────┐
       │                                │ 获取 Surface 缓冲区 │
       │                                │ dequeueBuffer()     │
       │                                │         │           │
       │                                │         ▼           │
       │                                │ 遍历 DisplayList    │
       │                                │ 执行 OpenGL ES 命令 │
       │                                │         │           │
       │                                │         ▼           │
       │                                │ GPU 渲染到 FBO      │
       │                                │ FBO → GraphicBuffer │
       │                                │         │           │
       │                                │         ▼           │
       │                                │ queueBuffer()       │
       │                                │ 提交给 SurfaceFlinger│
       │                                └─────────────────────┘
       │                                           │
       │                                           ▼
       │                                   SurfaceFlinger 合成
       │                                           │
       │                                           ▼
       │                                      显示到屏幕


  关键点总结:
  ─────────────────────────────────────────────────────────────────────────────

  1. 硬件加速模式下，Canvas 从 RenderNode.beginRecording() 获取
     - 不是从 Surface.lockCanvas() 获取
     - RecordingCanvas 不绑定任何内存

  2. 所有 draw* 操作只是记录命令
     - 命令存储在 DisplayList 中
     - 不立即执行，不写入内存

  3. RenderThread 真正执行绘制
     - 从 Surface 获取缓冲区 (dequeueBuffer)
     - 执行 OpenGL ES 命令
     - GPU 渲染到 GraphicBuffer
     - 提交给 SurfaceFlinger

  4. Surface 的作用
     - 软件绘制: 提供绑定了内存的 Canvas
     - 硬件加速: 只提供 GraphicBuffer，Canvas 从 RenderNode 获取
```

##### 2.11.5.5 RenderThread 渲染流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RenderThread 渲染流程                               │
│  源码: frameworks/base/libs/hwui/renderthread/RenderThread.cpp              │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  RenderThread 是独立的渲染线程:                                         │
  │                                                                         │
  │  ┌───────────────────────────────────────────────────────────────────┐ │
  │  │                    RenderThread                                    │ │
  │  │  源码: frameworks/base/libs/hwui/renderthread/RenderThread.cpp     │ │
  │  ├───────────────────────────────────────────────────────────────────┤ │
  │  │                                                                   │ │
  │  │  核心职责:                                                        │ │
  │  │  1. 从 UI 线程接收 DisplayList                                   │ │
  │  │  2. 优化 DisplayList (合并、剔除)                                 │ │
  │  │  3. 执行 OpenGL ES / Vulkan 渲染命令                              │ │
  │  │  4. 交换缓冲区 (swapBuffers)                                      │ │
  │  │  5. 提交给 SurfaceFlinger                                         │ │
  │  │                                                                   │ │
  │  └───────────────────────────────────────────────────────────────────┘ │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  RenderThread 渲染流程:
  ─────────────────────────────────────────────────────────────────────────────

  UI 线程                              RenderThread
  ──────────                           ────────────
       │                                     │
       │  syncAndDrawFrame()                 │
       │  ─────────────────────────────────► │
       │  (同步 DisplayList)                 │
       │                                     │
       │                                     ▼
       │                          ┌─────────────────────┐
       │                          │ 1. 处理同步消息     │
       │                          │ 2. 优化 DisplayList │
       │                          │    - 合并相同操作   │
       │                          │    - 剔除不可见项   │
       │                          │    - 重排序         │
       │                          └──────────┬──────────┘
       │                                     │
       │  (UI 线程可以继续)                  ▼
       │  处理其他消息             ┌─────────────────────┐
       │                          │ 3. 执行 GPU 渲染    │
       │                          │    OpenGL ES /      │
       │                          │    Vulkan           │
       │                          │                     │
       │                          │  glDrawArrays()     │
       │                          │  glDrawElements()   │
       │                          └──────────┬──────────┘
       │                                     │
       │                                     ▼
       │                          ┌─────────────────────┐
       │                          │ 4. 交换缓冲区       │
       │                          │    eglSwapBuffers() │
       │                          │                     │
       │                          │  提交给 Surface     │
       │                          │  → BufferQueue      │
       │                          └─────────────────────┘
       │                                     │
       │                                     ▼
       │                          SurfaceFlinger 合成
       │


  CanvasContext::draw() 源码:
  ─────────────────────────────────────────────────────────────────────────────

  // frameworks/base/libs/hwui/renderthread/CanvasContext.cpp
  void CanvasContext::draw() {
      // 1. 获取 Surface 缓冲区
      status_t err = mRenderPipeline->setSurface(mSurface);
      
      // 2. 开始帧
      mRenderPipeline->onStartFrame();
      
      // 3. 执行渲染
      mRenderPipeline->draw(...);
      
      // 4. 交换缓冲区
      mRenderPipeline->swapBuffers(frameInfo);
  }
```

##### 2.11.5.6 OpenGL ES 渲染流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OpenGL ES 渲染流程                                  │
│  源码: frameworks/base/libs/hwui/                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  HWUI 使用 OpenGL ES 执行渲染:                                          │
  │                                                                         │
  │  1. DisplayList → OpenGL 命令转换                                       │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │     DisplayList 命令              OpenGL ES 命令                        │
  │     ┌─────────────────┐          ┌─────────────────┐                   │
  │     │ drawRect()      │    →     │ glDrawArrays()  │                   │
  │     │ drawCircle()    │    →     │ glDrawArrays()  │                   │
  │     │ drawPath()      │    →     │ 多边形三角化    │                   │
  │     │ drawBitmap()    │    →     │ 纹理绑定 + 绘制 │                   │
  │     │ drawText()      │    →     │ 文字纹理缓存    │                   │
  │     └─────────────────┘          └─────────────────┘                   │
  │                                                                         │
  │  2. GPU 渲染到 FBO (FrameBuffer Object)                                │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │     FBO 绑定到 GraphicBuffer:                                          │
  │                                                                         │
  │     ┌─────────────────────────────────────────────────────────────┐    │
  │     │                      GPU                                     │    │
  │     │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │    │
  │     │  │ Vertex      │    │ Fragment    │    │ FBO         │    │    │
  │     │  │ Shader      │ ─► │ Shader      │ ─► │ (帧缓冲)    │    │    │
  │     │  │ (顶点处理)  │    │ (像素处理)  │    │             │    │    │
  │     │  └─────────────┘    └─────────────┘    └──────┬──────┘    │    │
  │     │                                               │           │    │
  │     └───────────────────────────────────────────────┼───────────┘    │
  │                                                     │                 │
  │                                                     ▼                 │
  │                                         ┌─────────────────┐          │
  │                                         │ GraphicBuffer   │          │
  │                                         │ (共享内存)      │          │
  │                                         └─────────────────┘          │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  eglSwapBuffers() 流程:
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  eglSwapBuffers()                                                       │
  │       │                                                                 │
  │       ▼                                                                 │
  │  1. 等待 GPU 渲染完成 (glFinish 或 fence)                              │
  │       │                                                                 │
  │       ▼                                                                 │
  │  2. queueBuffer() - 将缓冲区提交到 BufferQueue                         │
  │       │                                                                 │
  │       ▼                                                                 │
  │  3. dequeueBuffer() - 获取新的缓冲区用于下一帧                         │
  │       │                                                                 │
  │       ▼                                                                 │
  │  4. 通知 SurfaceFlinger 有新帧可用                                     │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

##### 2.11.5.7 RenderNode 与 DisplayList 详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RenderNode 与 DisplayList 详解                      │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  View 树与 RenderNode 树的关系:                                         │
  │                                                                         │
  │  View 树                        RenderNode 树                           │
  │  ─────────────────────────────────────────────────────────────────────  │
  │                                                                         │
  │  DecorView                     RenderNode (DecorView)                   │
  │     │                               │                                   │
  │     ├── LinearLayout               ├── RenderNode (LinearLayout)        │
  │     │     ├── TextView             │     ├── RenderNode (TextView)      │
  │     │     │                        │     │   └── DisplayList           │
  │     │     │                        │     │       [drawText cmd]        │
  │     │     │                        │     │                             │
  │     │     └── ImageView            │     └── RenderNode (ImageView)    │
  │     │                              │         └── DisplayList           │
  │     │                              │             [drawBitmap cmd]      │
  │     │                              │                                   │
  │     └── FrameLayout                └── RenderNode (FrameLayout)        │
  │           │                              │                             │
  │           └── Button                     └── RenderNode (Button)       │
  │                                                └── DisplayList         │
  │                                                    [drawRect cmd]      │
  │                                                    [drawText cmd]      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  DisplayList 优化:
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  1. 合并优化 (Merge)                                                    │
  │     - 相邻的相同类型绘制操作可以合并                                    │
  │     - 减少 OpenGL draw call 数量                                        │
  │                                                                         │
  │  2. 剔除优化 (Culling)                                                  │
  │     - 完全被遮挡的 View 不渲染                                          │
  │     - 屏幕外的 View 不渲染                                              │
  │                                                                         │
  │  3. 缓存优化 (Caching)                                                  │
  │     - 未变化的 View 复用上次的 DisplayList                              │
  │     - 只更新变化的 View                                                 │
  │                                                                         │
  │  4. 批处理 (Batching)                                                   │
  │     - 相同纹理的绘制操作批处理                                          │
  │     - 减少 GPU 状态切换                                                 │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

##### 2.11.5.8 软件绘制 vs 硬件加速对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         软件绘制 vs 硬件加速对比                            │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────────────────┬───────────────────────────────┐
  │                 │  软件绘制 (Software)    │  硬件加速 (Hardware)          │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  渲染引擎       │  Skia (CPU)             │  OpenGL ES / Vulkan (GPU)     │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  绘制方式       │  直接绘制到缓冲区       │  记录 DisplayList，异步渲染   │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  Canvas 类型    │  SkiaCanvas             │  RecordingCanvas              │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  线程           │  UI 线程 (同步)         │  RenderThread (异步)          │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  性能           │  慢，CPU 计算           │  快，GPU 并行                 │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  内存占用       │  少                     │  多 (DisplayList 缓存)        │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  适用场景       │  兼容模式、截图         │  正常应用                     │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  开启方式       │  view.setLayerType(     │  默认开启                     │
  │                 │    LAYER_TYPE_SOFTWARE) │  AndroidManifest:             │
  │                 │                         │  android:hardwareAccelerated  │
  └─────────────────┴─────────────────────────┴───────────────────────────────┘


  硬件加速的优势:
  ─────────────────────────────────────────────────────────────────────────────

  1. UI 线程不被阻塞
     - 绘制命令录制很快 (只是记录，不执行)
     - GPU 渲染在 RenderThread 进行
     - UI 线程可以快速响应用户操作

  2. GPU 并行计算
     - GPU 擅长并行处理大量像素
     - 复杂动画、渐变、阴影等效果好

  3. DisplayList 复用
     - 未变化的 View 不需要重新录制
     - 只更新变化的部分

  4. 优化空间大
     - 合并、剔除、批处理等优化
     - 减少不必要的绘制
```

### 2.12 Surface 到 SurfaceFlinger 调用详解

绘制链路必须区分三个对象：`SurfaceControl` 是合成层句柄，`Surface` 是应用提交内容的生产端，`GraphicBuffer` 才是某一帧的图形缓冲。创建层、建立生产端和提交首帧是不同步骤。Android 17 普通窗口的内容层还存在客户端创建与服务端创建两条路径。

#### 2.12.1 Surface 创建流程：useClientSurface 决定协议

源码精简节选（[WindowManager.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/WindowManager.java)）：

```java
static boolean useClientSurface() {
    return com.android.window.flags.Flags.useClientSurface();
}
```

该入口读取 window flags，不是根据 targetSdk 直接判断，也不能仅因运行 Android 17 就断言 flag 必定开启。下表限定普通、非 locally managed 窗口；windowless/嵌入场景由自己的 WindowLayout 与 session 协调。

| 条件 | 内容 SurfaceControl 的创建者 | 同步调用 | 异步调用 |
|---|---|---|---|
| `useClientSurface() == true` | ViewRootImpl.updateSurfaceControl / createSurfaceControl | relayout2，传入客户端层句柄 | relayoutAsync2，传入客户端层句柄 |
| `useClientSurface() == false` | WMS → WindowStateAnimator.createSurfaceLocked | relayout，通过 out SurfaceControl 返回句柄 | relayoutAsync，不返回新句柄，受适用条件限制 |

```text
窗口注册：ViewRootImpl.setView -> IWindowSession.addToDisplayAsUser -> WMS.addWindow
随后按需遍历 / relayoutWindow：
  client surface 开启，且不是 locally managed
    updateSurfaceControl(viewVisibility)
      缓存可用 -> 复用内容 SurfaceControl
      无可用层 -> createSurfaceControl -> Builder.setBLASTLayer().build()
    getSurfaceControlForRelayout
      -> relayout2 / relayoutAsync2（SurfaceControl：客户端 -> WMS）
      -> WMS.relayoutWindow -> WindowState.setClientSurface
         将内容层挂到窗口层，更新绘制 / 输入状态
  client surface 关闭
    relayout（out SurfaceControl：WMS -> 客户端）
      -> WMS.createSurfaceControl
      -> WindowStateAnimator.createSurfaceLocked -> setBLASTLayer().build()
共同的应用内容生产链：
  有效内容 SurfaceControl -> updateBlastSurfaceIfNeeded
    -> BLASTBufferQueue -> createSurfaceWithHandle -> mSurface.transferFrom
    -> 软件 Canvas 或硬件渲染器产生 buffer
```

`addWindow` 注册窗口及其管理关系，不应画成其中必定立即创建内容 buffer layer 并返回生产者接口。新路径的 relayout 传入层句柄，旧路径的 relayout 输出层句柄；这正是参数方向上的区别。

##### 2.12.1.1 客户端的创建、缓存与可见性状态

| 字段 | 作用 |
|---|---|
| `mSurfaceControl` | 当前内容层句柄，保持对象不等于句柄始终有效 |
| `mCachedSurfaceControl` | INVISIBLE 分支保留的可复用内容层引用 |
| `mSurface` | 渲染器使用的 Java Surface，底层生产端可经 transferFrom 更换 |
| `mBlastBufferQueue` | 将本窗口生产的 buffer 送到内容层事务路径 |
| `mBbqApplyToken` | 同一个 ViewRootImpl 重建 BLAST 队列时保持提交排序关系 |

源码精简节选（[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
private SurfaceControl createSurfaceControl() {
    int surfaceFlags = SurfaceControl.NOT_ADD_TO_ROOT;
    if ((mWindowAttributes.privateFlags
            & WindowManager.LayoutParams.PRIVATE_FLAG_IS_ROUNDED_CORNERS_OVERLAY) != 0) {
        surfaceFlags |= SurfaceControl.SKIP_SCREENSHOT;
    }
    final SurfaceControl.Builder builder = new SurfaceControl.Builder()
            .setCallsite("ViewRootImpl.createSurfaceControl")
            .setName("VRI-" + getTitle())
            .setFlags(surfaceFlags)
            .setFormat((mWindowAttributes.flags
                    & WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED) != 0
                    ? PixelFormat.TRANSLUCENT : mWindowAttributes.format)
            .setMetadata(SurfaceControl.METADATA_WINDOW_TYPE, mWindowAttributes.type)
            .setBLASTLayer();
    try {
        return builder.build();
    } catch (OutOfResourcesException e) {
        Slog.w(mTag, "OutOfResourcesException creating surface", e);
        return new SurfaceControl();
    }
}
```

源码精简节选（[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
private int updateSurfaceControl(int viewVisibility) {
    int relayoutResult = 0;
    if (viewVisibility == View.VISIBLE) {
        if (!mSurfaceControl.isValid()) {
            final SurfaceControl cachedSurfaceControl = mCachedSurfaceControl;
            mCachedSurfaceControl = null;
            if (cachedSurfaceControl == null || !cachedSurfaceControl.isValid()) {
                Trace.traceBegin(Trace.TRACE_TAG_VIEW, "createSurfaceControl");
                final SurfaceControl newSc = createSurfaceControl();
                mSurfaceControl.copyFrom(newSc, "VRI-new");
                newSc.release();
                Trace.traceEnd(Trace.TRACE_TAG_VIEW);
            } else {
                mSurfaceControl.copyFrom(cachedSurfaceControl, "VRI-from-cache");
                mPendingTransaction.setBackgroundBlurRadius(mSurfaceControl, 0);
                cachedSurfaceControl.release();
            }
            relayoutResult |= RELAYOUT_RES_SURFACE_CHANGED | RELAYOUT_RES_FIRST_TIME;
        }
    } else if (mSurfaceControl.isValid()) {
        if (viewVisibility == View.INVISIBLE) {
            mCachedSurfaceControl = new SurfaceControl(mSurfaceControl, "VRI-cache");
        }
        mSurfaceControl.release();
    }
    return relayoutResult;
}
```

创建器使用 `NOT_ADD_TO_ROOT`，再设窗口类型 metadata、像素格式与 BLAST layer 类型；硬件加速分支使用 TRANSLUCENT 格式。它不直接把新层加进显示根层级，所以“客户端已经 build 成功”并不等于层已经可见或已经通过完整窗口策略处理。

VISIBLE 且当前句柄无效时，先检查缓存再新建；缓存复用时清 background blur radius。INVISIBLE 时复制一份引用到缓存并 release 当前引用，其他不可见状态不执行这一缓存赋值。这里的 release 是释放当前句柄持有的引用，不可直接理解成“系统层和全部 GPU buffer 此刻已经被销毁”。

创建失败返回无效 SurfaceControl，绘制路径因此可以跳过不可用输出，而不是继续在一个假定有效的 Surface 上画首帧。

##### 2.12.1.2 relayout2 与 relayoutAsync2：句柄如何传给 WMS

源码精简节选（[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
private SurfaceControl getSurfaceControlForRelayout(int viewVisibility) {
    if (mWindowLayout.isLocallyManaged()) {
        return mSurfaceControl;
    }
    return viewVisibility == View.VISIBLE && mSurfaceControl.isValid() ? mSurfaceControl : null;
}
```

普通窗口只在 VISIBLE 且句柄有效时传出 mSurfaceControl；locally managed 窗口走自身返回分支，而前面的客户端创建也明确排除了它，不能套用普通根窗口创建逻辑。

以下是 `relayoutWindow()` 的分支节选：先在入口更新客户端层，再在已有布局计算结果上选择同步/异步协议。省略中间的窗口 frame 计算、坐标兼容转换与结果处理。

源码精简节选（[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
if (WindowManager.useClientSurface() && !mWindowLayout.isLocallyManaged()) {
    relayoutResult = updateSurfaceControl(viewVisibility);
}

// ... 计算布局、requestedWidth/Height、relayoutAsync、seqId
if (relayoutAsync) {
    if (WindowManager.useClientSurface()) {
        final SurfaceControl surfaceControl = getSurfaceControlForRelayout(viewVisibility);
        mWindowSession.relayoutAsync2(mWindow, params,
                requestedWidth, requestedHeight, viewVisibility,
                insetsPending ? WindowManagerGlobal.RELAYOUT_INSETS_PENDING : 0,
                mRelayoutSeq, seqId, surfaceControl);
        if (surfaceControl != null
                && (mViewFrameInfo.flags & FrameInfo.FLAG_WINDOW_VISIBILITY_CHANGED) != 0
                && !mWindowLayout.isLocallyManaged()) {
            relayoutResult |= RELAYOUT_RES_FIRST_TIME;
        }
    } else {
        mWindowSession.relayoutAsync(mWindow, params,
                requestedWidth, requestedHeight, viewVisibility,
                insetsPending ? WindowManagerGlobal.RELAYOUT_INSETS_PENDING : 0,
                mRelayoutSeq, seqId);
    }
} else {
    if (WindowManager.useClientSurface()) {
        final SurfaceControl surfaceControl = getSurfaceControlForRelayout(viewVisibility);
        relayoutResult |= mWindowSession.relayout2(mWindow, params,
                requestedWidth, requestedHeight, viewVisibility,
                insetsPending ? WindowManagerGlobal.RELAYOUT_INSETS_PENDING : 0,
                mRelayoutSeq, seqId, surfaceControl, mRelayoutResult);
    } else {
        relayoutResult |= mWindowSession.relayout(mWindow, params,
                requestedWidth, requestedHeight, viewVisibility,
                insetsPending ? WindowManagerGlobal.RELAYOUT_INSETS_PENDING : 0,
                mRelayoutSeq, seqId, mRelayoutResult, mSurfaceControl);
    }
    // ... 同步 relayout 返回结果处理
}
```

协议签名直接表达了方向差异，两个 Async 入口都是 oneway；同步 relayout2 仍会返回 frame、Insets、配置等 WindowRelayoutResult，不能写成“启用 client surface 后不再需要 WMS 返回任何结果”。

源码精简节选（[IWindowSession.aidl](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/IWindowSession.aidl)）：

```aidl
int relayout(IWindow window, in WindowManager.LayoutParams attrs, int requestedWidth,
        int requestedHeight, int viewVisibility, int flags, int seq, int lastSyncSeqId,
        out @nullable WindowRelayoutResult outRelayoutResult, out SurfaceControl outSurface);
int relayout2(IWindow window, in WindowManager.LayoutParams attrs, int requestedWidth,
        int requestedHeight, int viewVisibility, int flags, int seq, int lastSyncSeqId,
        in SurfaceControl surface, out @nullable WindowRelayoutResult outRelayoutResult);

oneway void relayoutAsync(IWindow window, in WindowManager.LayoutParams attrs,
        int requestedWidth, int requestedHeight, int viewVisibility, int flags, int seq,
        int lastSyncSeqId);

oneway void relayoutAsync2(IWindow window, in WindowManager.LayoutParams attrs,
        int requestedWidth, int requestedHeight, int viewVisibility, int flags, int seq,
        int lastSyncSeqId, in SurfaceControl surface);
```

`canRelayoutAsync()` 检查窗口可见性变化、starting window、待完成同步序列和配置差异；本地计算后若几何变化还需要 BLAST 同步序列，也可能回到同步调用。尤其旧服务端模式在可见性变化时可能需要取回新层句柄，不能不加条件地改走 oneway。

##### 2.12.1.3 WMS 绑定客户端层与旧服务端创建分支

WMS.relayoutWindow 对新路径调用 setClientSurface。内部参数仍名为 outSurfaceControl，是复用内部处理接口留下的命名；不要从这个变量名推断 relayout2 的 AIDL 参数也是 out。

源码精简节选（[WindowManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowManagerService.java)）：

```java
if (WindowManager.useClientSurface() && viewVisibility == View.VISIBLE
        && outSurfaceControl != null) {
    win.setClientSurface(outSurfaceControl);
}
```

源码精简节选（[WindowState.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowState.java)）：

```java
void setClientSurface(@NonNull SurfaceControl surface) {
    if (mWinAnimator.mSurfaceControl == surface) {
        return;
    }
    if (mWinAnimator.mSurfaceControl != null
            && mWinAnimator.mSurfaceControl.isSameSurface(surface)) {
        if (!isClientLocal()) {
            surface.release();
        }
        return;
    }
    Slog.d(TAG, "setClientSurface " + surface + " for " + mName);
    if (!surface.isValid()) {
        return;
    }
    if (mWinAnimator.mSurfaceControl != null) {
        getPendingTransaction().remove(mWinAnimator.mSurfaceControl);
    }
    mWinAnimator.mSurfaceControl = isClientLocal()
            ? new SurfaceControl(surface, "setClientSurface") : surface;
    getPendingTransaction().reparent(surface, mSurfaceControl);
    mWinAnimator.resetDrawState();
    setHasSurface(true);
    mInputWindowHandle.forceChange();
    if (mStartingData instanceof SnapshotStartingData) {
        mLastConfigReportedToClient = true;
        if (mSyncState != SYNC_STATE_NONE) {
            getSyncTransaction().reparent(surface, mSurfaceControl);
        }
    }
}
```

`WindowState.mSurfaceControl` 是系统维护的窗口层，而 `mWinAnimator.mSurfaceControl` 记录内容层。setClientSurface 将传入内容层 reparent 到窗口层，并重置 draw state、标记已有 Surface、更新输入信息。复用同一个底层层句柄时还需释放不再需要的反序列化引用。

层的创建位置变了，不代表窗口层级、可见性、输入和权限策略从 WMS 移交给应用。客户端不能凭 build 一个 SurfaceControl 就绕过窗口管理。

服务端创建函数只属于 flag 关闭的分支：

源码精简节选（[WindowStateAnimator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowStateAnimator.java)）：

```java
SurfaceControl createSurfaceLocked() {
    if (WindowManager.useClientSurface()) {
        Slog.e(TAG, "No longer create client surfaces on the server side", new Throwable());
        return null;
    }
    final WindowState w = mWin;

    if (mSurfaceControl != null) {
        return mSurfaceControl;
    }

    w.setHasSurface(false);

    ProtoLog.i(WM_DEBUG_ANIM, "createSurface %s: mDrawState=DRAW_PENDING", this);

    resetDrawState();

    int flags = SurfaceControl.HIDDEN;
    final WindowManager.LayoutParams attrs = w.mAttrs;

    if ((mWin.mAttrs.privateFlags & PRIVATE_FLAG_IS_ROUNDED_CORNERS_OVERLAY) != 0) {
        flags |= SurfaceControl.SKIP_SCREENSHOT;
    }

    if (DEBUG_VISIBILITY) {
        Slog.v(TAG, "Creating surface " + this
                + " format=" + attrs.format + " flags=" + flags);
    }
    try {
        final boolean isHwAccelerated = (attrs.flags & FLAG_HARDWARE_ACCELERATED) != 0;
        final int format = isHwAccelerated ? PixelFormat.TRANSLUCENT : attrs.format;

        mTitle = attrs.getTitle().toString();
        Trace.traceBegin(TRACE_TAG_WINDOW_MANAGER, "new SurfaceControl");
        mSurfaceControl = mWin.makeSurface()
                .setParent(mWin.mSurfaceControl)
                .setName(mTitle)
                .setFormat(format)
                .setFlags(flags)
                .setMetadata(METADATA_WINDOW_TYPE, attrs.type)
                .setMetadata(METADATA_OWNER_UID, mSession.mUid)
                .setMetadata(METADATA_OWNER_PID, mSession.mPid)
                .setCallsite("WindowSurfaceController")
                .setBLASTLayer().build();
        Trace.traceEnd(TRACE_TAG_WINDOW_MANAGER);

        w.setHasSurface(true);
        w.mInputWindowHandle.forceChange();

        ProtoLog.i(WM_SHOW_SURFACE_ALLOC,
                "  CREATE SURFACE %s: pid=%d format=%d flags=0x%x / %s",
                mSurfaceControl, mSession.mPid, attrs.format, flags, this);
    } catch (OutOfResourcesException e) {
        Slog.w(TAG, "OutOfResourcesException creating surface");
        mService.mRoot.reclaimSomeSurfaceMemory(this, "create", true);
        mDrawState = NO_SURFACE;
        return null;
    } catch (Exception e) {
        Slog.e(TAG, "Exception creating surface (parent dead?)", e);
        mDrawState = NO_SURFACE;
        return null;
    }
    // ... 后续日志及返回 mSurfaceControl
}
```

该 tag 的 `WindowStateAnimator` 直接保存 `SurfaceControl mSurfaceControl`，没有独立的 `WindowSurfaceController.java` 类。上面 `setCallsite("WindowSurfaceController")` 是调试来源字符串，不能据此在类图中继续画出旧类。新旧分支创建的内容层都使用 BLAST layer，区别不等于“新路径用 BLAST，旧路径完全不用 BLAST”。

#### 2.12.2 BufferQueue 创建与组件：BLAST 建立生产端

ViewRootImpl 有有效的内容层后，通过 updateBlastSurfaceIfNeeded 建立或更新生产端。这一步与“内容 SurfaceControl 由谁创建”正交：即使 flag 关闭、内容层来自服务端，应用仍可以通过自身 BLASTBufferQueue 生产并提交内容。

源码精简节选（[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
void updateBlastSurfaceIfNeeded() {
    if (mBlastBufferQueue != null && mBlastBufferQueue.isSameSurfaceControl(mSurfaceControl)) {
        mBlastBufferQueue.update(mSurfaceControl,
            mSurfaceSize.x, mSurfaceSize.y,
            mWindowAttributes.format);
        return;
    }
    if (mBlastBufferQueue != null) {
        mBlastBufferQueue.destroy();
    }
    mBlastBufferQueue = new BLASTBufferQueue(mTag, true );
    mBlastBufferQueue.setApplyToken(mBbqApplyToken);
    mBlastBufferQueue.update(mSurfaceControl, mSurfaceSize.x, mSurfaceSize.y,
            mWindowAttributes.format);
    mBlastBufferQueue.setTransactionHangCallback(sTransactionHangCallback);

    Surface blastSurface;

    blastSurface = mBlastBufferQueue.createSurfaceWithHandle();
    mSurface.transferFrom(blastSurface);
    mTransaction.setRecoverableFromBufferStuffing(mSurfaceControl).applyAsyncUnsafe();
}
```

源码精简节选（[BLASTBufferQueue.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/graphics/java/android/graphics/BLASTBufferQueue.java)）：

```java
public Surface createSurfaceWithHandle() {
    return nativeGetSurface(mNativeObject, true );
}
```

同一个内容层只需 update 队列尺寸/格式并直接返回；层改变时销毁旧队列、重新创建队列，并复用 mBbqApplyToken，防止旧新队列以不同 apply token 交错提交。只有生产端真的变化时才 transferFrom，避免无意义地增加 Surface generation ID 并触发 EGL 资源重建。

Native BLASTBufferQueue 创建 BufferQueue 的两个端点，消费者由 BLAST 侧持有。队列核心是进程内的队列对象，不是一个由两个进程直接共享的 ASHMEM 控制结构。

源码精简节选（[BLASTBufferQueue.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/gui/BLASTBufferQueue.cpp)）：

```cpp
void BLASTBufferQueue::createBufferQueue(sp<IGraphicBufferProducer>* outProducer,
                                         sp<IGraphicBufferConsumer>* outConsumer) {
    LOG_ALWAYS_FATAL_IF(outProducer == nullptr, "BLASTBufferQueue: outProducer must not be NULL");
    LOG_ALWAYS_FATAL_IF(outConsumer == nullptr, "BLASTBufferQueue: outConsumer must not be NULL");

    std::unique_ptr<gui::BufferReleaseChannel::ConsumerEndpoint> bufferReleaseConsumer;
    gui::BufferReleaseChannel::open(mName, bufferReleaseConsumer, mBufferReleaseProducer);
    mBufferReleaseReader = std::make_shared<BufferReleaseReader>(std::move(bufferReleaseConsumer));

    auto core = sp<BBQBufferQueueCore>::make(mBufferReleaseReader);
    LOG_ALWAYS_FATAL_IF(core == nullptr, "BLASTBufferQueue: failed to create BufferQueueCore");

    auto producer = sp<BBQBufferQueueProducer>::make(core, wp<BLASTBufferQueue>::fromExisting(this),
                                                     mBufferReleaseReader);
    LOG_ALWAYS_FATAL_IF(producer == nullptr,
                        "BLASTBufferQueue: failed to create BBQBufferQueueProducer");

    auto consumer = sp<BufferQueueConsumer>::make(core);
    consumer->setAllowExtraAcquire(true);
    LOG_ALWAYS_FATAL_IF(consumer == nullptr,
                        "BLASTBufferQueue: failed to create BufferQueueConsumer");

    *outProducer = producer;
    *outConsumer = consumer;
}
```

```text
应用进程
  Surface / NativeWindow
    -> BufferQueueProducer -- queueBuffer --> BufferQueueCore
                                             |
                          BLASTBufferItemConsumer / BufferQueueConsumer
                                             |
                                    BLASTBufferQueue
                                      取得 buffer 与 fence
                                      放入 SurfaceControl.Transaction
                                             |
                       Binder 事务（buffer handle + fence + layer 状态）
                                             v
SurfaceFlinger 进程
  接收目标 BLAST layer 的事务 -> 合成调度 -> HWC / GPU -> 显示
```

`GraphicBuffer` 的底层分配通过图形缓冲句柄被相关进程导入；同步靠 fence 和 buffer 生命周期协议，而不是把像素数组逐帧复制到 Binder。生产/消费两端可以在同进程，这与图形缓冲本身被跨进程使用是两个问题。

#### 2.12.3 应用绘制到 SurfaceFlinger 完整流程

| 阶段 | 软件绘制 | 硬件绘制 | 共同结果 |
|---|---|---|---|
| UI 内容 | drawSoftware 中直接执行 View.draw | 录制/更新 RenderNode 显示列表 | 本帧要显示的内容 |
| 获取输出 | Surface.lockCanvas → Native Surface | RenderThread/HWUI 从 NativeWindow 获取输出 | 获得可写 GraphicBuffer，处理相应 fence |
| 栅格化 | CPU/Skia 写入缓冲 | HWUI 的 GPU 后端渲染 | 产生本帧像素 |
| 生产端提交 | unlockCanvasAndPost | 后端 present，例如 GLES 的 eglSwapBuffers | buffer 进入生产端队列 |
| BLAST 消费 | 接收 frame available、取得 buffer | 同左 | 把 buffer/fence 与 layer 更新组成事务 |
| 合成与释放 | SurfaceFlinger / HWC / GPU | 同左 | 合成与释放同步，使 buffer 后续能被重用 |

BLAST 的 buffer 事务可直接提交，也可以交给同步回调与其他窗口事务合并。特别是 resize：测量得到新大小、层几何改变和新大小内容 buffer 需要协调，不能仅因 onLayout 返回就认为新尺寸已经显示。

此处的 BufferQueue 消费者是应用侧 BLAST，不是让 SurfaceFlinger 通过旧 `BufferLayer::onFrameAvailable()` 直接消费同一个队列。SurfaceFlinger 接收的是目标层的 buffer 事务；queueBuffer 完成、事务到达合成器、GPU 完成与显示呈现也不是同一时刻。

来源：[BLASTBufferQueue.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/gui/BLASTBufferQueue.cpp) 的 onFrameAvailable、buffer 获取及 Transaction.setBuffer 路径。

#### 2.12.4 跨进程通信方式与职责边界

| 通道 | 传输内容 | 不能混淆的概念 |
|---|---|---|
| IWindowSession Binder | 窗口注册、relayout、绘制完成与同步事务 | 不是每一笔 Canvas 绘图调用都经过 WMS |
| relayout2 / relayoutAsync2 | 客户端 SurfaceControl 句柄作为输入 | 不是服务端输出一个新的 Surface 生产者 |
| relayout（旧分支） | 输出服务端创建的内容 SurfaceControl | 不等于把全部图形 buffer 都在 WMS 分配 |
| SurfaceControl.Transaction | 层状态、buffer handle、fence 等提交到合成器 | 提交句柄不等于通过 Binder 复制整帧像素 |
| JNI | Java Surface / BLASTBufferQueue 与 native 对象互调 | Java→native 不意味着跨进程 |
| BufferQueue 协议 | dequeue/queue/acquire/release 与同步 | BufferQueueCore 对象不是跨进程共享内存 |

完整窗口策略和其他窗口类型的差异见 [Window 与 Surface 详解](Android_Window与Surface详解.md#7-android-17-的-surface-建立与-relayout)。

### 2.13 View 绘制多层级架构

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
│                         层级 3: WMS 层 (Window Manager Service，管理窗口关系与策略)             │
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
│  │       │  6. 管理窗口层与内容层挂接，协调 Surface 路径             │   │
│  │       │                                                             │   │
│  │       ├── WindowState (窗口状态)                                    │   │
│  │       ├── WindowToken (窗口令牌)                                    │   │
│  │       ├── Session (会话管理)                                        │   │
│  │       ├── DisplayContent (显示内容)                                 │   │
│  │       ├── client surface: ViewRootImpl 创建 BLAST SurfaceControl     │   │
│  │       └── legacy: WindowStateAnimator.createSurfaceLocked             │   │
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
│  │  BufferQueue / BLASTBufferQueue (生产-消费协议)                       │   │
│  │       │                                                             │   │
│  │       │  生产者-消费者模型:                                         │   │
│  │       │  - 生产者: Surface / NativeWindow (应用端)                   │   │
│  │       │  - BLAST 消费: 获取 buffer 并写入 layer Transaction           │   │
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
                                       │ Buffer / fence / SurfaceControl.Transaction
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

### 2.14 层级调用完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         层级调用完整流程                                     │
│  软件绘制 vs 硬件加速 两条路径                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.14.1 软件绘制完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         软件绘制完整流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 用户触发更新                                                        │
  │     点击/滑动 → View.invalidate() / requestLayout()                     │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. 请求 VSync                                                          │
  │     ViewRootImpl.scheduleTraversals()                                   │
  │         → Choreographer.postCallback()                                  │
  │         → 等待 VSync 信号                                               │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. VSync 到来，执行遍历                                                │
  │     Choreographer.doFrame()                                             │
  │         → ViewRootImpl.doTraversal()                                    │
  │         → performTraversals()                                           │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  4. 测量和布局                                                          │
  │     performMeasure() → measure() → onMeasure()                          │
  │     performLayout()  → layout()  → onLayout()                           │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  5. ★★★ 软件绘制特有步骤 ★★★                                           │
  │     performDraw() → draw() → drawSoftware()                             │
  │                                                                         │
  │     // 5.1 从 Surface 获取 Canvas (绑定内存)                            │
  │     canvas = Surface.lockCanvas(dirtyRect)                              │
  │         → JNI → Native: Surface::lock()                                 │
  │         → BufferQueueProducer::dequeueBuffer()                          │
  │         → 返回 GraphicBuffer，Canvas 绑定到这块内存                     │
  │                                                                         │
  │     // 5.2 执行 View 树绘制 (CPU 直接写入内存)                          │
  │     mView.draw(canvas)                                                  │
  │         → onDraw(canvas)                                                │
  │         → Skia 引擎直接写入 GraphicBuffer 内存                          │
  │                                                                         │
  │     // 5.3 提交缓冲区                                                   │
  │     Surface.unlockCanvasAndPost(canvas)                                 │
  │         → Native: Surface::unlockAndPost()                              │
  │         → BufferQueueProducer::queueBuffer()                            │
  │         → 通知 SurfaceFlinger 有新帧                                   │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  6. SurfaceFlinger 合成                                                 │
  │     VSync 到来时:                                                       │
  │     BufferQueueConsumer::acquireBuffer()                                │
  │         → SurfaceFlinger 合成所有 Layer                                 │
  │         → BufferQueueConsumer::releaseBuffer()                          │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  7. 显示到屏幕                                                          │
  │     SurfaceFlinger → FrameBuffer → DRM/KMS → Display Controller → Panel│
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 2.14.2 硬件加速绘制完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         硬件加速绘制完整流程                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 用户触发更新                                                        │
  │     点击/滑动 → View.invalidate() / requestLayout()                     │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. 请求 VSync                                                          │
  │     ViewRootImpl.scheduleTraversals()                                   │
  │         → Choreographer.postCallback()                                  │
  │         → 等待 VSync 信号                                               │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. VSync 到来，执行遍历                                                │
  │     Choreographer.doFrame()                                             │
  │         → ViewRootImpl.doTraversal()                                    │
  │         → performTraversals()                                           │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  4. 测量和布局 (与软件绘制相同)                                          │
  │     performMeasure() → measure() → onMeasure()                          │
  │     performLayout()  → layout()  → onLayout()                           │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  5. ★★★ 硬件加速绘制特有步骤 ★★★                                       │
  │     performDraw() → draw() → ThreadedRenderer.draw()                    │
  │                                                                         │
  │     // 5.1 构建 DisplayList (UI 线程)                                   │
  │     updateHierarchyDisplayList(view)                                    │
  │         → view.updateDisplayListIfDirty()                               │
  │         → canvas = renderNode.beginRecording()  // ★★★ 从 RenderNode  │
  │         → view.draw(canvas)  // 只记录命令，不执行                      │
  │         → renderNode.endRecording()                                     │
  │     // 此时 Canvas 不绑定任何内存，只记录绘制命令                        │
  │                                                                         │
  │     // 5.2 同步并请求渲染                                               │
  │     syncAndDrawFrame(frameInfo)                                         │
  │         → 同步 DisplayList 到 RenderThread                              │
  │     // UI 线程可以继续处理其他事情                                      │
  │                                                                         │
  │     // 5.3 RenderThread 执行 GPU 渲染 (独立线程)                        │
  │     RenderThread::draw()                                                │
  │         → 获取 Surface 缓冲区 (dequeueBuffer)                           │
  │         → 遍历 DisplayList，执行 OpenGL ES 命令                         │
  │         → GPU 渲染到 FBO → GraphicBuffer                                │
  │         → eglSwapBuffers() → queueBuffer()                              │
  │         → 通知 SurfaceFlinger 有新帧                                   │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  6. SurfaceFlinger 合成 (与软件绘制相同)                                 │
  │     VSync 到来时:                                                       │
  │     BufferQueueConsumer::acquireBuffer()                                │
  │         → SurfaceFlinger 合成所有 Layer                                 │
  │         → BufferQueueConsumer::releaseBuffer()                          │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  7. 显示到屏幕 (与软件绘制相同)                                          │
  │     SurfaceFlinger → FrameBuffer → DRM/KMS → Display Controller → Panel│
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 2.14.3 两种模式对比流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         软件绘制 vs 硬件加速 流程对比                        │
└─────────────────────────────────────────────────────────────────────────────┘

                              触发更新
                                 │
                                 ▼
                          请求 VSync
                                 │
                                 ▼
                          VSync 到来
                                 │
                                 ▼
                     performMeasure / performLayout
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
              软件绘制                    硬件加速
              ──────────                  ──────────
                    │                         │
                    ▼                         ▼
    ┌───────────────────────────┐  ┌───────────────────────────┐
    │ Surface.lockCanvas()      │  │ renderNode.beginRecording()│
    │ (从 Surface 获取 Canvas)  │  │ (从 RenderNode 获取 Canvas)│
    │                           │  │                           │
    │ Canvas 绑定到内存         │  │ Canvas 不绑定内存          │
    │ (GraphicBuffer)           │  │ 只是命令记录器             │
    └───────────┬───────────────┘  └───────────┬───────────────┘
                │                              │
                ▼                              ▼
    ┌───────────────────────────┐  ┌───────────────────────────┐
    │ view.draw(canvas)         │  │ view.draw(canvas)         │
    │                           │  │                           │
    │ CPU 直接写入内存          │  │ 只记录命令到 DisplayList  │
    │ (Skia 引擎)               │  │ 不执行实际绘制            │
    │                           │  │                           │
    │ ★ UI 线程阻塞 ★          │  │ ★ UI 线程很快返回 ★       │
    └───────────┬───────────────┘  └───────────┬───────────────┘
                │                              │
                ▼                              ▼
    ┌───────────────────────────┐  ┌───────────────────────────┐
    │ Surface.unlockCanvasAndPost│  │ syncAndDrawFrame()        │
    │                           │  │ 同步到 RenderThread       │
    │ queueBuffer()             │  │                           │
    └───────────┬───────────────┘  │ (UI 线程可以继续)         │
                │                  └───────────┬───────────────┘
                │                              │
                │                              ▼
                │                  ┌───────────────────────────┐
                │                  │ RenderThread (独立线程)   │
                │                  │                           │
                │                  │ dequeueBuffer()           │
                │                  │ 执行 OpenGL ES 命令       │
                │                  │ GPU 渲染到 GraphicBuffer  │
                │                  │ eglSwapBuffers()          │
                │                  │ queueBuffer()             │
                │                  └───────────┬───────────────┘
                │                              │
                └──────────────┬───────────────┘
                               │
                               ▼
                    SurfaceFlinger 合成
                               │
                               ▼
                         显示到屏幕
```

### 2.15 层级总结表

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
```

#### 2.15.1 软件绘制 vs 硬件加速 层级差异

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         软件绘制 vs 硬件加速 层级差异                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┬─────────────────────────────┬─────────────────────────────┐
│  层级/阶段       │  软件绘制                   │  硬件加速                   │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  Canvas 来源     │  Surface.lockCanvas()       │  RenderNode.beginRecording()│
│                 │  (从 Surface 获取)          │  (从 RenderNode 获取)       │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  Canvas 类型     │  SkiaCanvas                 │  RecordingCanvas            │
│                 │  (绑定内存)                 │  (不绑定内存)               │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  渲染引擎        │  Skia (CPU)                 │  OpenGL ES / Vulkan (GPU)   │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  绘制线程        │  UI 线程 (同步)             │  RenderThread (异步)        │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  绘制时机        │  draw() 立即写入内存        │  draw() 只记录命令          │
│                 │  UI 线程阻塞                │  UI 线程快速返回            │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  缓冲区获取      │  lockCanvas 时 dequeue      │  RenderThread 中 dequeue    │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  缓冲区提交      │  unlockCanvasAndPost       │  eglSwapBuffers             │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  内存写入方式    │  CPU 逐像素写入             │  GPU 并行渲染到 FBO         │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  Surface 的作用  │  提供绑定了内存的 Canvas    │  只提供 GraphicBuffer       │
│                 │  + 提供 GraphicBuffer       │  (Canvas 从 RenderNode 获取)│
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  性能特点        │  慢，CPU 计算               │  快，GPU 并行               │
│                 │  适合简单界面               │  适合复杂动画               │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  内存占用        │  少                         │  多 (DisplayList 缓存)      │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│  适用场景        │  兼容模式、截图、           │  正常应用、复杂动画、       │
│                 │  view.setLayerType(SOFTWARE)│  默认开启                   │
└─────────────────┴─────────────────────────────┴─────────────────────────────┘
```

#### 2.15.2 关键类差异

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         软件绘制 vs 硬件加速 关键类差异                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬─────────────────────────┬─────────────────────────────┐
│  功能                │  软件绘制               │  硬件加速                   │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  渲染器              │  (无专用类)             │  ThreadedRenderer           │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  Canvas 实现         │  SkiaCanvas             │  RecordingCanvas            │
│  (Java)             │  (frameworks/base/...)  │  (frameworks/base/...)      │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  Canvas 实现         │  SkiaCanvas (C++)       │  RecordingCanvas (C++)      │
│  (Native)           │  (frameworks/base/libs/ │  (frameworks/base/libs/hwui)│
│                     │   libs/hwui)            │                             │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  绘制命令存储        │  (无，直接执行)         │  DisplayList                │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  渲染节点            │  (无)                   │  RenderNode                 │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  渲染线程            │  (无，UI 线程执行)      │  RenderThread               │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  GPU 接口           │  (无)                   │  OpenGL ES / Vulkan         │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  绘制入口方法        │  drawSoftware()         │  ThreadedRenderer.draw()    │
│                     │  (ViewRootImpl)         │                             │
└─────────────────────┴─────────────────────────┴─────────────────────────────┘
```

#### 2.15.3 跨层通信方式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         跨层通信方式                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬───────────────────────────────────────────────────────┐
│  通信方式            │  使用场景                                             │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Binder IPC         │  应用进程 ↔ System Server (WMS)                       │
│                     │  IWindowSession.addToDisplayAsUser()                 │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  JNI                │  Java ↔ Native 层                                     │
│                     │  Choreographer ↔ DisplayEventReceiver                 │
│                     │  Surface.lockCanvas() ↔ nativeLockCanvas()            │
│                     │  RenderNode.beginRecording() ↔ Native                 │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Buffer / fence     │  GraphicBuffer 句柄与同步协议                       │
│                     │  不等于通过共享内存逐帧复制 BufferQueueCore               │
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

### 4.4 View.measure()：缓存、强制布局与测量状态

父容器调用的是 final 方法 `measure()`，不是直接调用子项的 `onMeasure()`。外层协议统一管理测量缓存、RTL 属性解析、测量状态检查及布局标志；子类只实现尺寸计算。

| 字段 / 标志 | 含义 |
|---|---|
| `mOldWidthMeasureSpec` / `mOldHeightMeasureSpec` | 上次传入的完整约束，包含 mode 和 size |
| `mMeasureCache` | 以两个 MeasureSpec 组合成的 long 为键缓存宽高结果 |
| `PFLAG_FORCE_LAYOUT` | 本次需要重新处理测量/布局；requestLayout、forceLayout 均会设置 |
| `PFLAG_MEASURED_DIMENSION_SET` | onMeasure 必须通过 setMeasuredDimension 建立的完成标记 |
| `PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT` | 命中测量缓存后，在 layout 前可能仍需补调 onMeasure |
| `PFLAG_LAYOUT_REQUIRED` | 本次测量处理后需要进入布局回调 |

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public final void measure(int widthMeasureSpec, int heightMeasureSpec) {
    boolean optical = isLayoutModeOptical(this);
    if (optical != isLayoutModeOptical(mParent)) {
        Insets insets = getOpticalInsets();
        int oWidth  = insets.left + insets.right;
        int oHeight = insets.top  + insets.bottom;
        widthMeasureSpec  = MeasureSpec.adjust(widthMeasureSpec,  optical ? -oWidth  : oWidth);
        heightMeasureSpec = MeasureSpec.adjust(heightMeasureSpec, optical ? -oHeight : oHeight);
    }
    long key = (long) widthMeasureSpec << 32 | (long) heightMeasureSpec & 0xffffffffL;
    if (mMeasureCache == null) mMeasureCache = new LongSparseLongArray(2);

    final boolean forceLayout = (mPrivateFlags & PFLAG_FORCE_LAYOUT) == PFLAG_FORCE_LAYOUT;
    final boolean specChanged = widthMeasureSpec != mOldWidthMeasureSpec
            || heightMeasureSpec != mOldHeightMeasureSpec;
    final boolean isSpecExactly = MeasureSpec.getMode(widthMeasureSpec) == MeasureSpec.EXACTLY
            && MeasureSpec.getMode(heightMeasureSpec) == MeasureSpec.EXACTLY;
    final boolean matchesSpecSize = getMeasuredWidth() == MeasureSpec.getSize(widthMeasureSpec)
            && getMeasuredHeight() == MeasureSpec.getSize(heightMeasureSpec);
    final boolean needsLayout = specChanged
            && (sAlwaysRemeasureExactly || !isSpecExactly || !matchesSpecSize);

    if (forceLayout || needsLayout) {
        mPrivateFlags &= ~PFLAG_MEASURED_DIMENSION_SET;

        resolveRtlPropertiesIfNeeded();

        int cacheIndex;
        if (sUseMeasureCacheDuringForceLayoutFlagValue) {
            cacheIndex =  mMeasureCache.indexOfKey(key);
        } else {
            cacheIndex = forceLayout ? -1 : mMeasureCache.indexOfKey(key);
        }

        if (cacheIndex < 0) {
            if (isTraversalTracingEnabled()) {
                Trace.beginSection(mTracingStrings.onMeasure);
            }
            if (android.os.Flags.adpfMeasureDuringInputEventBoost()) {
                final boolean notifyRenderer = hasExpensiveMeasuresDuringInputEvent();
                if (notifyRenderer) {
                    getViewRootImpl().notifyRendererOfExpensiveFrame(
                            "ADPF_SendHint: hasExpensiveMeasuresDuringInputEvent");
                }
            }
            onMeasure(widthMeasureSpec, heightMeasureSpec);
            if (isTraversalTracingEnabled()) {
                Trace.endSection();
            }
            mPrivateFlags3 &= ~PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT;
        } else {
            long value = mMeasureCache.valueAt(cacheIndex);
            setMeasuredDimensionRaw((int) (value >> 32), (int) value);
            mPrivateFlags3 |= PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT;
        }
        if ((mPrivateFlags & PFLAG_MEASURED_DIMENSION_SET) != PFLAG_MEASURED_DIMENSION_SET) {
            throw new IllegalStateException("View with id " + getId() + ": "
                    + getClass().getName() + "#onMeasure() did not set the"
                    + " measured dimension by calling"
                    + " setMeasuredDimension()");
        }

        mPrivateFlags |= PFLAG_LAYOUT_REQUIRED;
    }

    mOldWidthMeasureSpec = widthMeasureSpec;
    mOldHeightMeasureSpec = heightMeasureSpec;

    mMeasureCache.put(key, ((long) mMeasuredWidth) << 32 |
            (long) mMeasuredHeight & 0xffffffffL); // suppress sign extension
}
```

这个实现解释了三个常见现象：

1. **调用 measure 不等于调用 onMeasure**。约束相同且没有强制布局时可以跳过；命中缓存也可以恢复测量值。
2. **缓存不只是按宽高数值判断**。键包含完整 MeasureSpec，相同 size、不同 mode 不同义。强制布局期间是否使用缓存还取决于源码中的特性开关，而 `requestLayout()` 本身会清空本节点缓存。
3. **测量可以发生多次**。ViewRootImpl 可能因窗口大小改变重新测量，父容器也可能为权重或 MATCH_PARENT 补测；不要在 onMeasure 中发请求、加载图片或累计不可逆状态。

### 4.5 默认尺寸与 resolveSizeAndState

基类 View 的默认实现使用 `getDefaultSize(getSuggestedMinimumWidth(), widthMeasureSpec)`；AT_MOST 下它会取 spec 上限。因此简单继承 View 却不重写 onMeasure，wrap_content 常常表现为填满可用区域，而不是按自绘图形自动包裹。

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
    setMeasuredDimension(getDefaultSize(getSuggestedMinimumWidth(), widthMeasureSpec),
            getDefaultSize(getSuggestedMinimumHeight(), heightMeasureSpec));
}
```

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public static int resolveSizeAndState(int size, int measureSpec, int childMeasuredState) {
    final int specMode = MeasureSpec.getMode(measureSpec);
    final int specSize = MeasureSpec.getSize(measureSpec);
    final int result;
    switch (specMode) {
        case MeasureSpec.AT_MOST:
            if (specSize < size) {
                result = specSize | MEASURED_STATE_TOO_SMALL;
            } else {
                result = size;
            }
            break;
        case MeasureSpec.EXACTLY:
            result = specSize;
            break;
        case MeasureSpec.UNSPECIFIED:
        default:
            result = size;
    }
    return result | (childMeasuredState & MEASURED_STATE_MASK);
}
```

`resolveSizeAndState()` 把期望尺寸与父约束合并：EXACTLY 服从父指定值；AT_MOST 下超限时截断并置 `MEASURED_STATE_TOO_SMALL`；UNSPECIFIED 使用期望值。返回值同时含尺寸位和状态位，不能把它当普通像素值继续做几何运算。

例如圆形仪表盘内容希望占 120dp，左右 padding 各 16dp，则期望宽度是 152dp。父 AT_MOST 100dp 时得到 100dp 并带 TOO_SMALL；父 EXACTLY 200dp 时得到 200dp。圆形绘制可以在最终矩形内部取短边，但不能擅自把父要求的 200×100 改为 100×100。


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

### 5.3 View.layout()：边界变化不等于测量尺寸变化

`mLeft/mTop/mRight/mBottom` 是相对父坐标的布局边界；`mMeasuredWidth/mMeasuredHeight` 是测量结果。`layout(l,t,r,b)` 先更新边界，必要时执行 onLayout，然后通知布局监听器、清理布局标志。

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public void layout(int l, int t, int r, int b) {
    if ((mPrivateFlags3 & PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT) != 0) {
        if (isTraversalTracingEnabled()) {
            Trace.beginSection(mTracingStrings.onMeasureBeforeLayout);
        }
        onMeasure(mOldWidthMeasureSpec, mOldHeightMeasureSpec);
        if (isTraversalTracingEnabled()) {
            Trace.endSection();
        }
        mPrivateFlags3 &= ~PFLAG3_MEASURE_NEEDED_BEFORE_LAYOUT;
    }

    int oldL = mLeft;
    int oldT = mTop;
    int oldB = mBottom;
    int oldR = mRight;

    boolean changed = isLayoutModeOptical(mParent) ?
            setOpticalFrame(l, t, r, b) : setFrame(l, t, r, b);

    if (changed || (mPrivateFlags & PFLAG_LAYOUT_REQUIRED) == PFLAG_LAYOUT_REQUIRED) {
        if (isTraversalTracingEnabled()) {
            Trace.beginSection(mTracingStrings.onLayout);
        }
        onLayout(changed, l, t, r, b);
        if (isTraversalTracingEnabled()) {
            Trace.endSection();
        }

        if (shouldDrawRoundScrollbar()) {
            if(mRoundScrollbarRenderer == null) {
                mRoundScrollbarRenderer = new RoundScrollbarRenderer(this);
            }
        } else {
            mRoundScrollbarRenderer = null;
        }

        mPrivateFlags &= ~PFLAG_LAYOUT_REQUIRED;

        ListenerInfo li = mListenerInfo;
        if (li != null && li.mOnLayoutChangeListeners != null) {
            ArrayList<OnLayoutChangeListener> listenersCopy =
                    (ArrayList<OnLayoutChangeListener>)li.mOnLayoutChangeListeners.clone();
            int numListeners = listenersCopy.size();
            for (int i = 0; i < numListeners; ++i) {
                listenersCopy.get(i).onLayoutChange(this, l, t, r, b, oldL, oldT, oldR, oldB);
            }
        }
    }
    // ... 后续处理焦点与布局完成标志
}
```

`setFrame()` 在尺寸改变时进入 `sizeChange()` / `onSizeChanged()`。所以缓存 Path、Shader 或文字排版结果时，`onSizeChanged()` 是合适入口；它不是每次 layout 都调用。位置变化但宽高不变，仍可能执行 onLayout，却不需要重建尺寸相关缓存。

若 `changed == false` 但存在 `PFLAG_LAYOUT_REQUIRED`，框架仍执行 onLayout。反过来，仅修改 `translationX` 不改变这四个布局边界；它通过 RenderNode 参与显示和坐标变换，不要求重新排列兄弟节点。

### 5.4 父子坐标与布局案例

假设父容器在祖父中的 left 为 30，子 View 在父中 layout(10,20,110,70)：子 `width=100`、`height=50`、`left=10`；它在祖父坐标的水平位置至少要加上父的 30，还要考虑 scroll 和变换。不要把屏幕绝对位置直接传给 child.layout。

自定义 ViewGroup 通常先用 `measureChildWithMargins()` 测量，累积子项占用空间，再用 `child.layout()` 放置。GONE 不占普通布局空间，INVISIBLE 通常仍占；margin 由父容器消费，padding 属于容器自己的内部留白。完整容器示例见 [自定义 View 指南](Android_自定义View_绘制完全指南.md#35-实战支持-margin-的纵向容器)。


## 6. Draw 绘制流程

### 6.1 View.draw() 顺序

基类 `draw(Canvas)` 先更新脏标记，再按背景、内容、子项、装饰的顺序组织绘制。下面保留常见的无 fading edge 分支；有 fading edge 时会额外保存图层、绘制渐隐边缘并恢复，但内容前后关系不变。

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public void draw(@NonNull Canvas canvas) {
    final int privateFlags = mPrivateFlags;
    mPrivateFlags = (privateFlags & ~PFLAG_DIRTY_MASK) | PFLAG_DRAWN;
    int saveCount;

    drawBackground(canvas);
    final int viewFlags = mViewFlags;
    boolean horizontalEdges = (viewFlags & FADING_EDGE_HORIZONTAL) != 0;
    boolean verticalEdges = (viewFlags & FADING_EDGE_VERTICAL) != 0;
    if (!verticalEdges && !horizontalEdges) {
        onDraw(canvas);
        dispatchDraw(canvas);

        drawAutofilledHighlight(canvas);
        if (mOverlay != null && !mOverlay.isEmpty()) {
            mOverlay.getOverlayView().dispatchDraw(canvas);
        }
        onDrawForeground(canvas);
        drawDefaultFocusHighlight(canvas);

        if (isShowingLayoutBounds()) {
            debugDrawFocus(canvas);
        }
        return;
    }

    boolean drawTop = false;
    boolean drawBottom = false;
    boolean drawLeft = false;
    boolean drawRight = false;

    float topFadeStrength = 0.0f;
    float bottomFadeStrength = 0.0f;
    float leftFadeStrength = 0.0f;
    float rightFadeStrength = 0.0f;
```

从代码可直接读出：`onDraw()` 不是绘制全部内容的唯一入口。子项在 `dispatchDraw()` 中绘制；autofill highlight 在子项之后；Overlay 在 foreground 之前；最后还可能有默认焦点高亮和布局边界调试绘制。重写 `draw()` 后不调用 super，会同时绕过这些框架行为。

### 6.2 ViewGroup.drawChild() 与硬件显示列表

源码精简节选（省略注释；[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)）：

```java
protected boolean drawChild(@NonNull Canvas canvas, View child, long drawingTime) {
    return child.draw(canvas, this, drawingTime);
}
```

`drawChild()` 委托给 View 面向父容器的 draw 重载。该重载处理滚动、矩阵、alpha、裁剪、传统 Animation 与硬件 RenderNode；并不是在每一帧都直接执行 `child.onDraw()`。硬件路径可以引用未失效子树的显示列表，只更新节点属性或重录真正变脏的部分。

| 扩展点 | 应承担的职责 | 典型例子 |
|---|---|---|
| `onDraw(Canvas)` | 自己的内容 | 仪表盘刻度、进度弧、文字 |
| `dispatchDraw(Canvas)` | 子 View 绘制前后的附加内容 | 子项背后的连线、子项上方的选择框 |
| `onDrawForeground(Canvas)` | 前景、滚动条等装饰层 | 覆盖内容的边框；调用 super 保留默认装饰 |
| `drawChild(Canvas, View, long)` | 单个子项绘制包装 | 配合 save/restore 的逐项裁剪 |

只在 dispatchDraw 的 super 调用之后画内容，会盖住子项，但仍可能在 foreground 和 Overlay 相关层次之下；需要跨层覆盖时应先确定要覆盖哪一层，而不是不断提高 elevation。

### 6.3 属性失效与内容重录的区别

`setTranslationX()` 走的是 RenderNode 属性更新，通常无需执行 onMeasure 或重录该 View 的静态绘制命令；`setText()`、更改自绘 Path 则可能改变内容显示列表，有时还改变期望尺寸。

```kotlin
// 自定义 View 内的应用代码：绘制内容变化与几何变化分别处理。
var lineColor: Int = Color.BLACK
    set(value) {
        if (field == value) return
        field = value
        paint.color = value
        invalidate()
    }

var preferredRadiusPx: Float = 60f
    set(value) {
        require(value.isFinite() && value >= 0f)
        if (field == value) return
        field = value
        requestLayout() // onMeasure 的期望尺寸依赖此值
        invalidate()    // onDraw 的内容也依赖此值
    }
```

`invalidate()` 表示“已有内容不再有效”，不是“立即调用 onDraw”；`requestLayout()` 表示“布局约束需要重新求解”，也不是“此树所有节点必定重测”。外层遍历仍会合并请求并复用可用结果。

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

## 8. 软件渲染 vs 硬件渲染 全面对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│             软件渲染 vs 硬件渲染 - 各阶段详细差异                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.1 阶段 1: 触发更新 (相同)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         阶段 1: 触发更新                                    │
│  软件渲染和硬件渲染在此阶段完全相同                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  用户操作 (点击/滑动)
        │
        ▼
  View.invalidate() / requestLayout()
        │
        ▼
  ViewRootImpl.scheduleTraversals()
        │
        ▼
  Choreographer.postCallback(CALLBACK_TRAVERSAL)
        │
        ▼
  等待 VSync 信号

  ★ 两者完全相同，无差异 ★
```

### 8.2 阶段 2: VSync 处理 (相同)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         阶段 2: VSync 处理                                  │
│  软件渲染和硬件渲染在此阶段完全相同                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  VSync 信号到达
        │
        ▼
  Choreographer.doFrame()
        │
        ├──► doCallbacks(CALLBACK_INPUT)
        ├──► doCallbacks(CALLBACK_ANIMATION)
        ├──► doCallbacks(CALLBACK_TRAVERSAL)  ← ★ View 绘制入口
        └──► doCallbacks(CALLBACK_COMMIT)
        │
        ▼
  ViewRootImpl.doTraversal()
        │
        ▼
  performTraversals()

  ★ 两者完全相同，无差异 ★
```

### 8.3 阶段 3: 测量与布局 (相同)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         阶段 3: 测量与布局                                  │
│  软件渲染和硬件渲染在此阶段完全相同                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  performTraversals()
        │
        ├──► performMeasure()
        │        │
        │        ▼
        │     View.measure() → onMeasure()
        │        │
        │        ▼
        │     setMeasuredDimension()
        │
        ├──► performLayout()
        │        │
        │        ▼
        │     View.layout() → onLayout()
        │        │
        │        ▼
        │     设置子 View 位置
        │
        └──► performDraw()  ← ★★★ 从这里开始分叉 ★★★

  ★ 测量和布局阶段完全相同，无差异 ★
```

### 8.4 阶段 4: 绘制入口 (分叉点)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         阶段 4: 绘制入口 (分叉点)                           │
└─────────────────────────────────────────────────────────────────────────────┘

  performDraw()
        │
        ▼
  ViewRootImpl.draw(fullRedrawNeeded)
        │
        │  判断是否使用硬件加速
        │
        ├─────────────────────────────────────────────────────┐
        │                                                     │
        ▼                                                     ▼
  ┌─────────────────────────────┐          ┌─────────────────────────────┐
  │     软件渲染路径             │          │     硬件渲染路径             │
  │                             │          │                             │
  │  条件:                      │          │  条件:                      │
  │  !mAttachInfo.mThreadedRenderer  │    │  mAttachInfo.mThreadedRenderer  │
  │    .isEnabled()             │          │    .isEnabled()             │
  │                             │          │                             │
  │  或者 View 设置了           │          │  默认开启 (Android 4.0+)    │
  │  LAYER_TYPE_SOFTWARE        │          │                             │
  └──────────────┬──────────────┘          └──────────────┬──────────────┘
                 │                                        │
                 ▼                                        ▼
          drawSoftware()                          ThreadedRenderer.draw()
```

### 8.5 阶段 5: Canvas 获取 (重大差异)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         阶段 5: Canvas 获取 (重大差异)                      │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
  │          软件渲染                    │    │          硬件渲染                    │
  ├─────────────────────────────────────┤    ├─────────────────────────────────────┤
  │                                     │    │                                     │
  │  drawSoftware()                     │    │  ThreadedRenderer.draw()            │
  │        │                            │    │        │                            │
  │        ▼                            │    │        ▼                            │
  │  ★★★ 从 Surface 获取 Canvas ★★★   │    │  ★★★ 从 RenderNode 获取 Canvas ★★★│
  │                                     │    │                                     │
  │  canvas = Surface.lockCanvas(      │    │  updateHierarchyDisplayList(view)   │
  │          dirtyRect);               │    │        │                            │
  │                                     │    │        ▼                            │
  │  调用链:                            │    │  view.updateDisplayListIfDirty()    │
  │  Java → JNI → Native               │    │        │                            │
  │                                     │    │        ▼                            │
  │  Native:                            │    │  ★★★ 关键步骤 ★★★                 │
  │  surface->lock(&buffer)            │    │                                     │
  │      → dequeueBuffer()             │    │  canvas = renderNode               │
  │      → 获取 GraphicBuffer          │    │          .beginRecording(w, h);    │
  │                                     │    │                                     │
  │  bitmap.setPixels(buffer->bits)    │    │  调用链:                            │
  │      → Canvas 绑定到内存           │    │  Java → JNI → Native               │
  │                                     │    │                                     │
  │  ★★★ Canvas 类型: SkiaCanvas ★★★  │    │  Native:                            │
  │  ★★★ 绑定了 GraphicBuffer 内存 ★★★│    │  RecordingCanvas* canvas =         │
  │                                     │    │      new RecordingCanvas(          │
  │                                     │    │          displayList);             │
  │                                     │    │                                     │
  │                                     │    │  ★★★ Canvas 类型: RecordingCanvas │
  │                                     │    │  ★★★ 不绑定任何内存 ★★★           │
  │                                     │    │  ★★★ 只是命令记录器 ★★★           │
  │                                     │    │                                     │
  └─────────────────────────────────────┘    └─────────────────────────────────────┘

  关键差异:
  ┌─────────────────┬─────────────────────────┬───────────────────────────────┐
  │                 │  软件渲染               │  硬件渲染                     │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  Canvas 来源    │  Surface.lockCanvas()   │  RenderNode.beginRecording() │
  │  Canvas 类型    │  SkiaCanvas             │  RecordingCanvas              │
  │  是否绑定内存   │  是 (GraphicBuffer)     │  否                           │
  │  内存获取时机   │  绘制前 (同步)          │  RenderThread 中 (异步)       │
  │  是否阻塞 UI    │  是                     │  否                           │
  └─────────────────┴─────────────────────────┴───────────────────────────────┘
```

### 8.6 阶段 6: 执行绘制 (重大差异)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         阶段 6: 执行绘制 (重大差异)                         │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
  │          软件渲染                    │    │          硬件渲染                    │
  ├─────────────────────────────────────┤    ├─────────────────────────────────────┤
  │                                     │    │                                     │
  │  mView.draw(canvas)                 │    │  view.draw(canvas)                  │
  │        │                            │    │        │                            │
  │        ▼                            │    │        ▼                            │
  │  onDraw(canvas)                     │    │  onDraw(canvas)                     │
  │        │                            │    │        │                            │
  │        ▼                            │    │        ▼                            │
  │  canvas.drawRect()                  │    │  canvas.drawRect()                  │
  │  canvas.drawCircle()                │    │  canvas.drawCircle()                │
  │  canvas.drawText()                  │    │  canvas.drawText()                  │
  │        │                            │    │        │                            │
  │        ▼                            │    │        ▼                            │
  │  ★★★ SkiaCanvas 执行 ★★★          │    │  ★★★ RecordingCanvas 执行 ★★★    │
  │                                     │    │                                     │
  │  SkiaCanvas::drawRect() {           │    │  RecordingCanvas::drawRect() {      │
  │      // 直接写入内存                │    │      // 创建命令对象                │
  │      for (y = top; y < bottom; y++)│    │      DrawRectOp* op =               │
  │          for (x = left; x < right; │    │          new DrawRectOp(...);      │
  │              x++)                   │    │                                     │
  │              pixels[x+y*stride] =   │    │      // 添加到命令列表              │
  │                  color;             │    │      displayList->add(op);          │
  │  }                                  │    │  }                                  │
  │                                     │    │                                     │
  │  ★★★ CPU 逐像素写入 ★★★           │    │  ★★★ 只记录命令，不执行 ★★★     │
  │  ★★★ UI 线程阻塞 ★★★              │    │  ★★★ UI 线程快速返回 ★★★        │
  │                                     │    │                                     │
  └─────────────────────────────────────┘    └─────────────────────────────────────┘

  性能差异:
  ┌─────────────────┬─────────────────────────┬───────────────────────────────┐
  │                 │  软件渲染               │  硬件渲染                     │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  执行方式       │  立即执行               │  记录命令，稍后执行           │
  │  执行线程       │  UI 线程                │  RenderThread                 │
  │  CPU 使用       │  高 (逐像素计算)        │  低 (只记录命令)              │
  │  GPU 使用       │  无                     │  高 (并行渲染)                │
  │  UI 线程阻塞    │  是                     │  否                           │
  │  复杂界面性能   │  差                     │  好                           │
  └─────────────────┴─────────────────────────┴───────────────────────────────┘
```

### 8.7 阶段 7: 提交结果 (重大差异)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         阶段 7: 提交结果 (重大差异)                         │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────┐    ┌─────────────────────────────────────┐
  │          软件渲染                    │    │          硬件渲染                    │
  ├─────────────────────────────────────┤    ├─────────────────────────────────────┤
  │                                     │    │                                     │
  │  // 绘制完成后立即提交               │    │  // 录制完成后同步到 RenderThread   │
  │  surface.unlockCanvasAndPost(       │    │  syncAndDrawFrame(frameInfo);       │
  │          canvas);                   │    │        │                            │
  │        │                            │    │        │                            │
  │        ▼                            │    │        ▼                            │
  │  Native:                            │    │  // UI 线程可以继续了!             │
  │  surface->unlockAndPost()           │    │  // RenderThread 异步执行          │
  │        │                            │    │        │                            │
  │        ▼                            │    │        │ (跨线程)                   │
  │  BufferQueueProducer::              │    │        ▼                            │
  │      queueBuffer()                  │    │  RenderThread::draw()               │
  │        │                            │    │        │                            │
  │        ▼                            │    │        ▼                            │
  │  状态变化:                          │    │  // ★★★ 独立线程执行 ★★★        │
  │  DEQUEUED → QUEUED                  │    │                                     │
  │                                     │    │  // 1. 获取缓冲区                  │
  │  通知 SurfaceFlinger 有新帧         │    │  dequeueBuffer()                    │
  │                                     │    │        │                            │
  │                                     │    │        ▼                            │
  │                                     │    │  // 2. 执行 OpenGL ES 命令         │
  │                                     │    │  遍历 DisplayList                   │
  │                                     │    │      → glDrawArrays()               │
  │                                     │    │      → GPU 渲染到 FBO               │
  │                                     │    │        │                            │
  │                                     │    │        ▼                            │
  │                                     │    │  // 3. 交换缓冲区                  │
  │                                     │    │  eglSwapBuffers()                   │
  │                                     │    │        │                            │
  │                                     │    │        ▼                            │
  │                                     │    │  queueBuffer()                      │
  │                                     │    │        │                            │
  │                                     │    │        ▼                            │
  │                                     │    │  通知 SurfaceFlinger 有新帧        │
  │                                     │    │                                     │
  └─────────────────────────────────────┘    └─────────────────────────────────────┘

  线程模型差异:
  ┌─────────────────┬─────────────────────────┬───────────────────────────────┐
  │                 │  软件渲染               │  硬件渲染                     │
  ├─────────────────┼─────────────────────────┼───────────────────────────────┤
  │  执行线程       │  UI 线程 (同步)         │  UI 线程 + RenderThread       │
  │  UI 线程工作    │  全部绘制工作           │  只录制命令                   │
  │  RenderThread   │  不存在                 │  执行 GPU 渲染                │
  │  UI 线程阻塞    │  是 (整个绘制过程)      │  否 (快速返回)                │
  │  并行能力       │  无                     │  UI 线程和渲染并行            │
  └─────────────────┴─────────────────────────┴───────────────────────────────┘
```

### 8.8 阶段 8: SurfaceFlinger 合成 (相同)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         阶段 8: SurfaceFlinger 合成                         │
│  软件渲染和硬件渲染在此阶段完全相同                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  VSync 到来时:
        │
        ▼
  SurfaceFlinger::handleMessageRefresh()
        │
        ▼
  Layer::latchBuffer()
        │
        ▼
  BufferQueueConsumer::acquireBuffer()
        │
        │  状态: QUEUED → ACQUIRED
        │
        ▼
  合成所有 Layer (GLES 或 HWC)
        │
        ▼
  提交到 FrameBuffer
        │
        ▼
  BufferQueueConsumer::releaseBuffer()
        │
        │  状态: ACQUIRED → FREE
        │
        ▼
  显示到屏幕

  ★ 两者完全相同，无差异 ★
  ★ 无论是 CPU 写入还是 GPU 渲染，最终都是 GraphicBuffer ★
  ★ SurfaceFlinger 不关心缓冲区内容是如何产生的 ★
```

### 8.9 完整对比总结图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         软件渲染 vs 硬件渲染 完整对比                        │
└─────────────────────────────────────────────────────────────────────────────┘

  阶段                         软件渲染              硬件渲染
  ─────────────────────────────────────────────────────────────────────────────

  1. 触发更新                   相同 ✓               相同 ✓
     invalidate/requestLayout

  2. VSync 处理                 相同 ✓               相同 ✓
     Choreographer.doFrame

  3. 测量布局                   相同 ✓               相同 ✓
     measure/layout

  4. 绘制入口                   ──────────────── 分叉点 ─────────────────
     performDraw                drawSoftware()       ThreadedRenderer.draw()

  5. Canvas 获取                Surface              RenderNode
     ★★★ 重大差异 ★★★         .lockCanvas()        .beginRecording()
                                绑定内存              不绑定内存
                                SkiaCanvas           RecordingCanvas

  6. 执行绘制                   CPU 立即执行         只记录命令
     ★★★ 重大差异 ★★★         逐像素写入           DisplayList
                                UI 线程阻塞          UI 线程快速返回

  7. 提交结果                   unlockCanvasAndPost  syncAndDrawFrame
     ★★★ 重大差异 ★★★         同步提交             → RenderThread 异步执行
                                                     → GPU 渲染
                                                     → eglSwapBuffers

  8. SurfaceFlinger 合成        相同 ✓               相同 ✓
     合成所有 Layer

  9. 显示到屏幕                 相同 ✓               相同 ✓


  差异总结:
  ─────────────────────────────────────────────────────────────────────────────

  相同阶段: 1, 2, 3, 8, 9 (共 5 个阶段)
  差异阶段: 4, 5, 6, 7 (共 4 个阶段)

  核心差异:
  1. Canvas 来源不同 (Surface vs RenderNode)
  2. Canvas 类型不同 (SkiaCanvas vs RecordingCanvas)
  3. 执行方式不同 (CPU 立即执行 vs 记录命令)
  4. 渲染引擎不同 (Skia vs OpenGL ES/Vulkan)
  5. 线程模型不同 (UI 线程同步 vs RenderThread 异步)
```

### 8.10 关键类对比表

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         关键类对比表                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬─────────────────────────┬─────────────────────────────┐
│  功能/阶段           │  软件渲染               │  硬件渲染                   │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  渲染决策            │  ViewRootImpl           │  ViewRootImpl               │
│  (判断使用哪种模式)  │  .draw() 中判断         │  .draw() 中判断             │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  渲染入口类          │  ViewRootImpl           │  ThreadedRenderer           │
│                     │  .drawSoftware()        │  .draw()                    │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  Canvas 类型 (Java) │  Canvas (底层 SkiaCanvas)│ RecordingCanvas             │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  Canvas 类型 (C++)  │  SkiaCanvas             │  RecordingCanvas            │
│                     │  (libs/hwui)            │  (libs/hwui)                │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  命令存储            │  (无，直接执行)         │  DisplayList                │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  渲染节点            │  (无)                   │  RenderNode                 │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  渲染线程            │  (无，UI 线程执行)      │  RenderThread               │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  渲染引擎            │  Skia (CPU)             │  OpenGL ES / Vulkan (GPU)   │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  Surface 交互        │  lockCanvas()           │  dequeueBuffer()            │
│                     │  unlockCanvasAndPost()  │  queueBuffer()              │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  内存写入            │  Skia 直接写入          │  GPU 通过 FBO 写入          │
│                     │  GraphicBuffer          │  GraphicBuffer              │
└─────────────────────┴─────────────────────────┴─────────────────────────────┘
```

### 8.11 性能对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         性能对比                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬─────────────────────────┬─────────────────────────────┐
│  性能指标            │  软件渲染               │  硬件渲染                   │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  简单界面            │  可接受                 │  更好                       │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  复杂界面            │  慢，可能卡顿           │  流畅                       │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  动画效果            │  有限                   │  丰富                       │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  渐变/阴影           │  CPU 计算慢             │  GPU 并行快                 │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  UI 响应性           │  绘制时阻塞             │  始终流畅                   │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  内存占用            │  少                     │  多 (DisplayList 缓存)      │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  电量消耗            │  CPU 高负载耗电         │  GPU 高效省电               │
├─────────────────────┼─────────────────────────┼─────────────────────────────┤
│  兼容性              │  最好                   │  好 (少数设备可能有问题)    │
└─────────────────────┴─────────────────────────┴─────────────────────────────┘


  何时使用软件渲染:
  ─────────────────────────────────────────────────────────────────────────────
  1. 调试绘制问题
  2. 截图功能
  3. 特殊 View 需要软件渲染
  4. 设备 GPU 兼容性问题

  // 强制使用软件渲染
  view.setLayerType(View.LAYER_TYPE_SOFTWARE, null);


  何时使用硬件渲染 (默认):
  ─────────────────────────────────────────────────────────────────────────────
  1. 正常应用开发 (默认)
  2. 复杂动画
  3. 大量绘制操作
  4. 追求流畅体验
```

---

## 9. 总结

### 9.1 核心流程图

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

### 9.2 关键类总结

| 类 | 职责 |
|---|---|
| ViewRootImpl | View 树根，连接 WMS，触发绘制 |
| Choreographer | VSync 调度，帧同步 |
| WindowManager | 窗口管理 |
| DecorView | 顶级 View |
| MeasureSpec | 测量规格 (Mode + Size) |

---

*本文档由 OpenClaw 生成*
