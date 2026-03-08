# View 动画底层原理：深入理解动画接入 ViewRootImpl

_作者：OpenClaw_  
_日期：2026-03-08_

---

## 概述

本文档详细讲解 **View 动画（补间动画）** 是如何从 `View.startAnimation()` 一路接入到 `ViewRootImpl`，最终通过 **VSYNC 信号** 驱动绘制的完整流程。

---

## 核心流程概览

```
View.startAnimation()
    ↓
Animation.attach()
    ↓
ViewParent.requestLayout()/invalidate()
    ↓
ViewRootImpl.scheduleTraversals()
    ↓
Choreographer.postCallback()
    ↓
VSYNC 信号到来
    ↓
ViewRootImpl.doTraversal()
    ↓
ViewRootImpl.performTraversals()
    ↓
View.draw()
    ↓
View.applyLegacyAnimation()
    ↓
Canvas 变换完成
```

---

## 第一步：View.startAnimation()

```java
// View.java
public void startAnimation(Animation animation) {
    animation.setStartTime(Animation.START_ON_FIRST_FRAME);
    // 1. 将动画设置到 View
    mCurrentAnimation = animation;
    
    // 2. 如果动画还没有 attach，先 attach
    if (mAttachInfo != null) {
        animation.attach(this);
    }
    
    // 3. 刷新父View，触发重新布局/绘制
    invalidate(true);
    
    // 4. 请求父 View 调度动画
    if (mParent != null) {
        mParent.requestChildAnimation(this);
    }
}
```

关键点：
- `mCurrentAnimation` 保存当前动画
- `animation.attach(this)` 将动画绑定到 View
- `invalidate(true)` 触发重绘
- `requestChildAnimation()` 通知父 View 调度动画

---

## 第二步：Animation.attach()

```java
// Animation.java
void attach(View view) {
    // 保存 View 的上下文信息
    mContext = view.getContext();
    mView = view;
    
    // 获取 View 的参数，用于计算动画
    mViewWidth = view.getWidth();
    mViewHeight = view.getHeight();
    
    // 获取动画所需的 Transformation 矩阵
    if (mTransformation == null) {
        mTransformation = new Transformation();
    }
    
    // 初始化动画插值器等
    initializeInterpolator();
}
```

---

## 第三步：requestChildAnimation()

```java
// View.java
public void requestChildAnimation(View child) {
    // 递归向上通知父 View
    if (mParent != null) {
        mParent.requestChildAnimation(this);
    }
}

// ViewGroup.java
@Override
public void requestChildAnimation(View child) {
    // 标记需要动画更新
    mChildRequestedTransition = true;
    
    // 请求 ViewRootImpl 调度遍历
    if (mParent != null) {
        mParent.requestLayout();
    }
}
```

---

## 第四步：ViewRootImpl.scheduleTraversals()

这是关键的一步！所有动画最终都会汇聚到 `ViewRootImpl`：

```java
// ViewRootImpl.java
public void requestLayout() {
    if (!mHandlingLayoutInLayoutRequest) {
        // 检查是否在主线程
        checkThread();
        mLayoutRequested = true;
        
        // 调度遍历
        scheduleTraversals();
    }
}

void scheduleTraversals() {
    // 避免重复调度
    if (!mTraversalScheduled) {
        mTraversalScheduled = true;
        
        // 1. 通过 Choreographer 注册下一帧的回调
        mChoreographer.postCallback(
            Choreographer.CALLBACK_TRAVERSAL, 
            mTraversalRunnable,  // 真正的遍历任务
            null
        );
        
        // 2. 同步屏障（可选），确保动画优先执行
        mChoreographer.postCallback(
            Choreographer.CALLBACK_SYNC,
            null,
            null
        );
    }
}

// 遍历任务
final TraversalRunnable mTraversalRunnable = new TraversalRunnable();

class TraversalRunnable implements Runnable {
    @Override
    public void run() {
        doTraversal();
    }
}
```

---

## 第五步：Choreographer 与 VSYNC

### 什么是 Choreographer？

`Choreographer`（ choreographer [kɔːrɪˈɑːɡrəfər] n. 舞蹈编导）是 Android 系统的**帧率控制器**，它：

1. 接收 **VSYNC 信号**（垂直同步信号）
2. 协调 UI 线程的绘制工作
3. 确保动画在正确的时机执行

### Choreographer 原理

```java
// Choreographer.java
public static Choreographer getInstance() {
    // 单例模式
    if (sInstance == null) {
        sInstance = new Choreographer();
    }
    return sInstance;
}

private Choreographer() {
    // 创建消息队列
    mLooper = Looper.myLooper();
    mHandler = new FrameHandler(mLooper);
    
    // 注册 VSYNC 监听
    mDisplayEventReceiver = new FrameDisplayEventReceiver(mLooper);
    
    // 回调队列
    mCallbackQueues = new CallbackQueue[CALLBACK_LAST + 1];
}
```

### VSYNC 信号接收

```java
// FrameDisplayEventReceiver.java
private final class FrameDisplayEventReceiver extends DisplayEventReceiver {
    
    @Override
    public void onVsync(long timestampNanos, int builtInDisplayId, int frame) {
        // 1. 投递消息到主线程
        Message msg = mHandler.obtainMessage(MSG_DO_FRAME);
        msg.arg1 = frame;
        mHandler.sendMessageAtTime(msg, timestampNanos / 1000000);
    }
}

// FrameHandler 处理 DO_FRAME 消息
private static final int MSG_DO_FRAME = 0;

private final class FrameHandler extends Handler {
    @Override
    public void handleMessage(Message msg) {
        switch (msg.what) {
            case MSG_DO_FRAME:
                doFrame(frameTimeNanos, 0);
                break;
        }
    }
}
```

### doFrame 执行

```java
// Choreographer.java
void doFrame(long frameTimeNanos, int frame) {
    synchronized (mLock) {
        long intendedFrameTimeNanos = frameTimeNanos;
        
        // 计算帧时间
        long lastFrameTimeNanos = frameTimeNanos;
        
        // 依次执行各类型的回调
        doCallbacks(Choreographer.CALLBACK_INPUT, frameTimeNanos);
        doCallbacks(Choreographer.CALLBACK_ANIMATION, frameTimeNanos);
        doCallbacks(Choreographer.CALLBACK_TRAVERSAL, frameTimeNanos);
    }
}
```

**注意：** `CALLBACK_ANIMATION` 在 `CALLBACK_TRAVERSAL` 之前执行！

```java
void doCallbacks(int callbackType, long frameTimeNanos) {
    CallbackRecord callbacks;
    synchronized (mLock) {
        // 从队列取出回调
        callbacks = mCallbackQueues[callbackType].extractDueCallbacksLocked(
            frameTimeNanos / 1000000);
    }
    
    // 执行回调
    for (CallbackRecord callback = callbacks; callback != null; callback = callback.next) {
        callback.run(frameTimeNanos);
    }
}
```

---

## 第六步：ViewRootImpl.doTraversal()

VSYNC 信号触发后，执行遍历：

```java
// ViewRootImpl.java
void doTraversal() {
    if (mTraversalScheduled) {
        mTraversalScheduled = false;
        
        // 移除同步屏障
        mHandler.getLooper().getQueue().removeSyncBarrier(mSyncBarrierId);
        
        // 执行真正的遍历
        performTraversals();
    }
}
```

---

## 第七步：performTraversals()

这是 View 树绘制的核心方法：

```java
// ViewRootImpl.java
private void performTraversals() {
    // 1. 如果有动画，先更新动画
    if (mLayoutRequested) {
        // 执行布局
        performMeasure();
        performLayout();
    }
    
    // 2. 执行绘制
    if (mDirty != null || !mIsInTraversal) {
        performDraw();
    }
}
```

---

## 第八步：performDraw() 与 draw()

```java
// ViewRootImpl.java
private void performDraw() {
    // 省略部分代码...
    
    // 调用 draw() 方法
    draw(fullRect);
}

private void draw(boolean fullRedrawNeeded) {
    // 1. 滚动动画
    if (!dirty.isEmpty() || mIsAnimating) {
        // 获取画布
        Canvas canvas;
        if (attachInfo.mHardwareAccelerationEnabled) {
            canvas = surface.lockCanvas(dirty);
        } else {
            canvas = mSurface.lockCanvas(dirty);
        }
        
        try {
            // 2. 调用 View 树的 draw
            if (mView != null) {
                mView.draw(canvas);
            }
        } finally {
            // 3. 解锁并提交画布
            surface.unlockCanvasAndPost(canvas);
        }
    }
}
```

---

## 第九步：View.draw() 中应用动画

这是动画真正起作用的地方！

```java
// View.java
public void draw(Canvas canvas) {
    // 1. 保存画布初始状态
    final int saveCount = canvas.save();
    
    // 2. 应用动画变换（核心！）
    if (mCurrentAnimation != null) {
        applyLegacyAnimation(canvas);
    }
    
    // 3. 绘制 View 内容
    dispatchDraw(canvas);
    
    // 4. 恢复画布
    canvas.restoreToCount(saveCount);
    
    // 5. 绘制装饰（滚动条等）
    onDrawScrollBars(canvas);
}
```

---

## 第十步：applyLegacyAnimation()

这是 View 动画应用的核心方法：

```java
// View.java
boolean applyLegacyAnimation(Canvas canvas) {
    boolean more = false;
    final Transformation attachedToWindow = attachInfo.mEnterTransformation;
    
    if (mCurrentAnimation != null) {
        // 1. 获取或创建 Transformation 对象
        final Transformation t = getChildTransformation();
        
        // 2. 获取当前动画时间
        long curTime = AnimationUtils.currentAnimationTimeMillis();
        
        // 3. 计算动画的变换矩阵
        more = mCurrentAnimation.getTransformation(
            curTime,  // 当前时间
            t         // 输出：变换矩阵
        );
        
        // 4. 如果有变换，应用到 Canvas
        if (more) {
            // 将动画的矩阵应用到 Canvas
            canvas.concat(t.getMatrix());
            
            // 如果有透明度，也应用
            float alpha = t.getAlpha();
            if (alpha != 1.0f) {
                canvas.saveLayerAlpha(
                    canvas.getClipBounds(), 
                    (int) (alpha * 255)
                );
                canvas.restore();
            }
        }
        
        // 5. 如果动画没结束，继续请求下一帧
        if (more && !mAttachInfo.mHardwareAccelerated) {
            // 软件渲染时需要 invalidate
            invalidate(true);
        }
    }
    
    return more;
}
```

### Transformation 类

```java
// Transformation.java
public class Transformation {
    private Matrix mMatrix = new Matrix();
    private float mAlpha = 1.0f;
    
    // 获取变换矩阵
    public Matrix getMatrix() {
        return mMatrix;
    }
    
    // 获取透明度
    public float getAlpha() {
        return mAlpha;
    }
    
    // 设置变换类型
    public void setTransformationType(int type) {
        mTransformationType = type;
    }
}
```

---

## Animation.getTransformation() 详解

这个方法计算某一时刻的动画状态：

```java
// Animation.java
public boolean getTransformation(long currentTime, Transformation outTransform) {
    // 1. 如果是第一次运行，初始化开始时间
    if (mStartTime < 0) {
        mStartTime = currentTime;
    }
    
    // 2. 计算动画进度 (0.0 到 1.0)
    long deltaTime = currentTime - mStartTime;
    float normalizedTime = deltaTime / (float) mDuration;
    
    // 3. 如果动画结束
    if (normalizedTime >= 1.0f) {
        if (mRepeatCount != INFINITE) {
            outTransform.clear();
            return false; // 动画结束
        }
    }
    
    // 4. 应用插值器
    if (mInterpolator != null) {
        normalizedTime = mInterpolator.getInterpolation(normalizedTime);
    }
    
    // 5. 限制在 0-1 范围
    normalizedTime = Math.max(0.0f, Math.min(1.0f, normalizedTime));
    
    // 6. 应用动画效果到 Transformation
    applyTransformation(normalizedTime, outTransform);
    
    return true; // 动画继续
}
```

### applyTransformation() 实现

```java
// Animation.java
protected void applyTransformation(float interpolatedTime, Transformation t) {
    final float fromX = mFromXScale;
    final float toX = mToXScale;
    final float fromY = mFromYScale;
    final float toY = mToYScale;
    
    // 计算当前的缩放比例
    float scaleX = fromX + (toX - fromX) * interpolatedTime;
    float scaleY = fromY + (toY - fromY) * interpolatedTime;
    
    // 计算缩放中心
    final float pivotX = getPivotX();
    final float pivotY = getPivotY();
    
    // 构建变换矩阵
    Matrix matrix = t.getMatrix();
    
    // 1. 先移动到中心点
    matrix.setTranslate(pivotX, pivotY);
    // 2. 缩放
    matrix.preScale(scaleX, scaleY);
    // 3. 旋转
    if (mFromDegrees != mToDegrees) {
        float rot = mFromDegrees + (mToDegrees - mFromDegrees) * interpolatedTime;
        matrix.preRotate(rot);
    }
    // 4. 透明度
    if (mFromAlpha != mToAlpha) {
        float alpha = mFromAlpha + (mToAlpha - mFromAlpha) * interpolatedTime;
        t.setAlpha(alpha);
    }
    // 5. 移回原位置
    matrix.preTranslate(-pivotX, -pivotY);
}
```

---

## 完整流程时序图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           VSYNC 信号                                     │
│                              ↓                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │              Choreographer.doFrame()                               │  │
│  │                              ↓                                      │  │
│  │  1. CALLBACK_INPUT    (输入事件处理)                                │  │
│  │  2. CALLBACK_ANIMATION (动画更新) ← 在这里更新动画状态！            │  │
│  │  3. CALLBACK_TRAVERSAL (View 遍历) ← 在这里执行 draw()             │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                              ↓                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │            ViewRootImpl.doTraversal()                              │  │
│  │            ViewRootImpl.performTraversals()                         │  │
│  │            ViewRootImpl.performDraw()                               │  │
│  │                              ↓                                      │  │
│  │  View.draw(canvas)  ← 在这里应用动画到 Canvas                       │  │
│  │         ↓                                                            │  │
│  │  applyLegacyAnimation(canvas)                                      │  │
│  │         ↓                                                            │  │
│  │  mCurrentAnimation.getTransformation()                             │  │
│  │         ↓                                                            │  │
│  │  canvas.concat(t.getMatrix()) ← Canvas 变换完成！                  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                              ↓                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │            SurfaceFlinger 合成渲染到屏幕                             │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 动画循环是如何持续的？

### 关键：invalidate() 循环

```java
// View.java - applyLegacyAnimation 末尾
if (more && !mAttachInfo.mHardwareAccelerated) {
    // 软件渲染时需要手动请求下一帧
    invalidate(true);
}
```

### 硬件渲染时

```java
// ViewRootImpl.java
void scheduleTraversals() {
    // 使用 Choreographer 确保每一帧都执行
    mChoreographer.postCallback(
        Choreographer.CALLBACK_TRAVERSAL,
        mTraversalRunnable,
        null
    );
}
```

由于 `CALLBACK_TRAVERSAL` 每次 `doTraversal()` 都会被重新注册，只要动画没结束，就会持续请求下一帧。

---

## 总结：View 动画的关键点

| 层级 | 关键类/方法 | 作用 |
|-----|------------|------|
| 用户层 | `View.startAnimation()` | 启动动画 |
| View 层 | `Animation.attach()` | 绑定动画到 View |
| ViewGroup 层 | `requestChildAnimation()` | 向上传递动画请求 |
| ViewRootImpl 层 | `scheduleTraversals()` | 调度下一帧绘制 |
| Choreographer 层 | `postCallback()` | 注册 VSYNC 回调 |
| VSYNC | `DisplayEventReceiver` | 垂直同步信号 |
| 绘制层 | `View.draw()` | 执行绘制 |
| 动画应用 | `applyLegacyAnimation()` | 将动画应用到 Canvas |
| 变换计算 | `Animation.getTransformation()` | 计算当前帧的变换 |

---

## 为什么 View 动画不会改变实际属性？

通过上面的分析，我们现在明白了：

1. **动画只作用于 Canvas**：动画的变换是通过 `canvas.concat(matrix)` 实现的
2. **Canvas 只是绘图上下文**：它不影响 View 的 `mLeft`、`mTop`、`mTranslationX` 等属性
3. **View 实际位置不变**：View 在 View 树中的位置由 `mLeft`、`mTop` 决定，这些从未被修改
4. **点击区域不变**：因为 `mTouchDelegate` 等仍然基于原始位置计算

这就是为什么动画后 `view.getX()` 返回的是原始位置，而不是动画后的位置。

---

_本文档由 OpenClaw 自动生成_
