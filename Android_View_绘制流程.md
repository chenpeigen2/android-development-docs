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
   - 2.7 [Choreographer 与 VSync](#27-choreographer-与-vsync)
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

### 2.7 Choreographer 与 VSync

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Choreographer 与 VSync                              │
│  源码位置: frameworks/base/core/java/android/view/Choreographer.java       │
└─────────────────────────────────────────────────────────────────────────────┘

Choreographer 是帧调度器，接收 VSync 信号并触发 UI 绘制:

┌─────────────────────────────────────────────────────────────────────────────┐
│                         VSync 信号流程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  SurfaceFlinger
       │
       │  VSync 信号 (16.6ms / 60fps)
       ▼
  Choreographer
       │
       │  doFrame()
       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  回调类型 (按优先级):                                                   │
  │                                                                         │
  │  1. CALLBACK_INPUT      - 输入事件处理                                 │
  │  2. CALLBACK_ANIMATION   - 动画更新                                    │
  │  3. CALLBACK_TRAVERSAL   - View 绘制 ★★★                               │
  │  4. CALLBACK_COMMIT      - 提交                                        │
  └─────────────────────────────────────────────────────────────────────────┘


// Choreographer.doFrame()
void doFrame(long frameTimeNanos, int frame) {
    // 1. 处理输入
    doCallbacks(Choreographer.CALLBACK_INPUT, frameTimeNanos);
    
    // 2. 处理动画
    doCallbacks(Choreographer.CALLBACK_ANIMATION, frameTimeNanos);
    
    // 3. ★★★ 处理 View 遍历 ★★★
    doCallbacks(Choreographer.CALLBACK_TRAVERSAL, frameTimeNanos);
    
    // 4. 提交
    doCallbacks(Choreographer.CALLBACK_COMMIT, frameTimeNanos);
}
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
