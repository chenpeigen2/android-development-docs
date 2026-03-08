# Android 动画完全指南

_作者：OpenClaw_  
_日期：2026-03-08_

---

## 目录

1. [概述](#概述)
2. [View 动画 (Animation)](#view-动画-animation)
   - [View 动画底层原理：与 ViewRootImpl 的结合](#view-动画底层原理与-viewrootimpl-的结合)
3. [属性动画 (Property Animation)](#属性动画-property-animation)
   - [属性动画与 ViewRootImpl 的结合](#属性动画与-viewrootimpl-的结合)
4. [帧动画 (Drawable Animation)](#帧动画-drawable-animation)
5. [转场动画 (Transition API)](#转场动画-transition-api)
6. [Material Design 动画](#material-design-动画)
7. [动画性能优化](#动画性能优化)
8. [实战技巧](#实战技巧)

---

## 概述

Android 动画是提升用户体验的关键技术之一。从 API 1 到现在的 API 34，Android 提供了多种动画框架：

| 动画类型 | 引入版本 | 特点 |
|---------|---------|------|
| View 动画 | API 1 | 简单易用，但只改变视觉效果，不改变实际属性 |
| 属性动画 | API 11 | 真正改变对象属性，功能强大 |
| 帧动画 | API 1 | 播放一系列 Drawable 帧 |
| 转场动画 | API 19 | Activity/Fragment 切换动画 |

---

## View 动画 (Animation)

### 什么是 View 动画

View 动画，也称为补间动画（Tween Animation），通过对 View 进行一系列的变换（平移、缩放、旋转、透明度）来实现动画效果。**重要特点：View 动画只改变 View 的绘制位置和外观，不会改变 View 的实际属性（如点击区域）。**

### 支持的动画类型

```xml
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android"
    android:interpolator="@android:anim/accelerate_decelerate_interpolator"
    android:fillAfter="true">

    <!-- 平移 -->
    <translate
        android:fromXDelta="0"
        android:toXDelta="100"
        android:fromYDelta="0"
        android:toYDelta="200"
        android:duration="300"/>

    <!-- 缩放 -->
    <scale
        android:fromXScale="1.0"
        android:toXScale="1.5"
        android:fromYScale="1.0"
        android:toYScale="1.5"
        android:pivotX="50%"
        android:pivotY="50%"
        android:duration="300"/>

    <!-- 旋转 -->
    <rotate
        android:fromDegrees="0"
        android:toDegrees="360"
        android:pivotX="50%"
        android:pivotY="50%"
        android:duration="500"/>

    <!-- 透明度 -->
    <alpha
        android:fromAlpha="1.0"
        android:toAlpha="0.5"
        android:duration="300"/>

</set>
```

### 在代码中使用 View Animation

```java
// 方式一：从 XML 加载
Animation animation = AnimationUtils.loadAnimation(this, R.anim.fade_in);
view.startAnimation(animation);

// 方式二：代码创建
Animation fadeIn = new AlphaAnimation(1.0f, 0.0f);
fadeIn.setDuration(300);
view.startAnimation(fadeIn);

// 监听动画状态
animation.setAnimationListener(new Animation.AnimationListener() {
    @Override
    public void onAnimationStart(Animation animation) {}

    @Override
    public void onAnimationEnd(Animation animation) {
        // 动画结束
    }

    @Override
    public void onAnimationRepeat(Animation animation) {}
});
```

### Interpolator（插值器）

插值器定义了动画变化的速度曲线：

| 插值器 | 效果 |
|-------|------|
| `LinearInterpolator` | 匀速 |
| `AccelerateInterpolator` | 加速 |
| `DecelerateInterpolator` | 减速 |
| `AccelerateDecelerateInterpolator` | 先加速后减速 |
| `BounceInterpolator` | 弹跳效果 |
| `OvershootInterpolator` | 超过目标值后回弹 |
| `AnticipateInterpolator` | 开始时向后一点 |
| `CycleInterpolator` | 循环动画 |

```xml
<set android:interpolator="@android:anim/accelerate_decelerate_interpolator">
```

### View 动画的局限性

1. **不改变实际属性**：动画后 View 的 `getX()`、`getY()` 等方法返回值不变
2. **点击区域不变**：即使 View 移动了，点击区域仍停留在原位置
3. **功能有限**：只能做有限的几种变换

### View 动画底层原理：与 ViewRootImpl 的结合

View 动画虽然不改变实际属性，但它同样需要通过 ViewRootImpl 和 Choreographer 来驱动绘制。

#### 完整流程

```
View.startAnimation()
    ↓
Animation.attach()
    ↓
View.invalidate() + requestChildAnimation()
    ↓
ViewParent.requestLayout()
    ↓
ViewRootImpl.scheduleTraversals()
    ↓
Choreographer.postCallback(CALLBACK_TRAVERSAL)
    ↓
VSYNC 信号
    ↓
ViewRootImpl.doTraversal()
    ↓
ViewRootImpl.performTraversals()
    ↓
View.draw(canvas)
    ↓
applyLegacyAnimation(canvas) ← 动画在这里生效
    ↓
canvas.concat(t.getMatrix()) ← Canvas 矩阵变换
```

#### 关键：applyLegacyAnimation()

```java
// View.java
boolean applyLegacyAnimation(Canvas canvas) {
    boolean more = false;
    
    if (mCurrentAnimation != null) {
        final Transformation t = getChildTransformation();
        
        // 计算当前帧的动画变换
        more = mCurrentAnimation.getTransformation(
            AnimationUtils.currentAnimationTimeMillis(), 
            t
        );
        
        // 关键：将动画的矩阵应用到 Canvas
        if (more) {
            canvas.concat(t.getMatrix());
            
            // 如果有透明度变化
            float alpha = t.getAlpha();
            if (alpha != 1.0f) {
                canvas.saveLayerAlpha(canvas.getClipBounds(), (int) (alpha * 255));
                canvas.restore();
            }
        }
        
        // 动画未结束时继续请求重绘
        if (more && !mAttachInfo.mHardwareAccelerated) {
            invalidate(true);
        }
    }
    
    return more;
}
```

#### Animation.getTransformation()

```java
// Animation.java
public boolean getTransformation(long currentTime, Transformation outTransform) {
    // 1. 初始化开始时间
    if (mStartTime < 0) {
        mStartTime = currentTime;
    }
    
    // 2. 计算进度
    long deltaTime = currentTime - mStartTime;
    float normalizedTime = deltaTime / (float) mDuration;
    
    // 3. 应用插值器
    if (mInterpolator != null) {
        normalizedTime = mInterpolator.getInterpolation(normalizedTime);
    }
    
    // 4. 计算变换矩阵
    applyTransformation(normalizedTime, outTransform);
    
    return normalizedTime < 1.0f; // 动画是否继续
}

protected void applyTransformation(float interpolatedTime, Transformation t) {
    // 根据动画类型（平移、缩放、旋转、透明度）计算矩阵
    // ...
}
```

#### View 动画 vs 属性动画：核心区别

| 特性 | View 动画 | 属性动画 |
|-----|----------|---------|
| **作用对象** | Canvas 画布 | View 属性成员 |
| **实际位置** | 不变 | 真正改变 |
| **点击区域** | 不变 | 跟随移动 |
| **实现方式** | `canvas.concat(matrix)` | `setXXX()` 方法 |
| **触发绘制** | 在 `draw()` 中 | 在 `onAnimationUpdate()` 中 |
| **性能** | 较高 | 较低 |

#### 总结

View 动画的流程可以总结为：
1. **启动**：调用 `startAnimation()`，设置 `mCurrentAnimation`
2. **触发**：调用 `invalidate()` 触发 `ViewRootImpl.scheduleTraversals()`
3. **绘制**：在 `View.draw()` 中通过 `applyLegacyAnimation()` 应用动画
4. **变换**：通过 `canvas.concat(matrix)` 改变绘制位置
5. **循环**：动画未结束时再次调用 `invalidate()` 继续下一帧

这就是为什么 View 动画"看起来"移动了，但 `getX()` / `getY()` 返回的还是原始位置。

---

## 属性动画 (Property Animation)

### 什么是属性动画

属性动画是 Android 3.0 (API 11) 引入的强大动画系统。它通过直接改变对象的属性值来实现动画，**真正改变了对象的实际属性**。

### 核心类

- **ValueAnimator**：属性动画的核心类，负责计算属性值
- **ObjectAnimator**：ValueAnimator 的子类，直接对对象的属性进行动画
- **AnimatorSet**：组合多个动画

### ValueAnimator 使用

```java
// 创建 ValueAnimator
ValueAnimator animator = ValueAnimator.ofFloat(0f, 1f);
animator.setDuration(1000);
animator.setInterpolator(new AccelerateDecelerateInterpolator());

// 设置值监听器
animator.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
    @Override
    public void onAnimationUpdate(ValueAnimator animation) {
        float value = (float) animation.getAnimatedValue();
        // 使用 value 更新 View
        view.setAlpha(value);
    }
});

animator.start();
```

### ObjectAnimator 使用

```java
// 直接对属性进行动画
ObjectAnimator alphaAnimator = ObjectAnimator.ofFloat(view, "alpha", 1f, 0f);
alphaAnimator.setDuration(300);
alphaAnimator.start();

// 平移
ObjectAnimator translationX = ObjectAnimator.ofFloat(view, "translationX", 0f, 100f);
translationX.setDuration(300);
translationX.start();

// 旋转
ObjectAnimator rotate = ObjectAnimator.ofFloat(view, "rotation", 0f, 360f);
rotate.setDuration(500);
rotate.start();

// 缩放
ObjectAnimator scaleX = ObjectAnimator.ofFloat(view, "scaleX", 1f, 1.5f);
ObjectAnimator scaleY = ObjectAnimator.ofFloat(view, "scaleY", 1f, 1.5f);
scaleX.setDuration(300);
scaleY.setDuration(300);
scaleX.start();
scaleY.start();
```

### 多属性组合动画

```java
// 使用 AnimatorSet
AnimatorSet set = new AnimatorSet();

ObjectAnimator alpha = ObjectAnimator.ofFloat(view, "alpha", 1f, 0f);
ObjectAnimator translationX = ObjectAnimator.ofFloat(view, "translationX", 0f, 100f);
ObjectAnimator rotation = ObjectAnimator.ofFloat(view, "rotation", 0f, 360f);

// 一起播放
set.playTogether(alpha, translationX, rotation);
set.setDuration(500);
set.start();

// 或者按顺序播放
AnimatorSet sequentialSet = new AnimatorSet();
sequentialSet.playSequentially(alpha, translationX, rotation);
sequentialSet.setDuration(1500);
sequentialSet.start();

// 更精细的控制
AnimatorSet builderSet = new AnimatorSet();
builderSet.play(alpha).with(translationX);
builderSet.play(rotation).after(alpha);
builderSet.setDuration(1000);
builderSet.start();
```

### TypeEvaluator（类型估值器）

自定义属性变化的计算方式：

```java
// 颜色动画
ValueAnimator colorAnimator = ValueAnimator.ofObject(new ArgbEvaluator(), 
    Color.RED, Color.BLUE);
colorAnimator.setDuration(1000);
colorAnimator.addUpdateListener(animation -> {
    int color = (int) animation.getAnimatedValue();
    view.setBackgroundColor(color);
});
colorAnimator.start();

// 自定义 TypeEvaluator
public class PointEvaluator implements TypeEvaluator<PointF> {
    @Override
    public PointF evaluate(float fraction, PointF startValue, PointF endValue) {
        float x = startValue.x + fraction * (endValue.x - startValue.x);
        float y = startValue.y + fraction * (endValue.y - startValue.y);
        return new PointF(x, y);
    }
}

// 使用自定义Evaluator
ValueAnimator pointAnimator = ValueAnimator.ofObject(new PointEvaluator(),
    new PointF(0, 0), new PointF(100, 200));
pointAnimator.setDuration(1000);
pointAnimator.start();
```

### 动画监听器

```java
animator.addListener(new AnimatorListenerAdapter() {
    @Override
    public void onAnimationStart(Animator animation) {
        // 开始
    }

    @Override
    public void onAnimationEnd(Animator animation) {
        // 结束
    }

    @Override
    public void onAnimationCancel(Animator animation) {
        // 取消
    }

    @Override
    public void onAnimationRepeat(Animator animation) {
        // 重复
    }
});
```

### 属性动画与 ViewRootImpl 的结合

属性动画之所以能**真正改变 View 的实际属性**（如 `translationX`、`alpha`、`rotation`），是因为它在动画过程中会持续触发 ViewRootImpl 的绘制流程。

#### 核心流程

```
ObjectAnimator.start()
    ↓
ValueAnimator.start()
    ↓
AnimationHandler.scheduleAnimation()
    ↓
Choreographer.postCallback(CALLBACK_ANIMATION, ...)
    ↓
VSYNC 信号触发
    ↓
AnimationFrameCallback.doFrame()
    ↓
ValueAnimator.doAnimationFrame()
    ↓
onAnimationUpdate() 回调
    ↓
View.setProperty() 直接修改属性
    ↓
View.invalidate() / requestLayout()
    ↓
ViewRootImpl.scheduleTraversals()
    ↓
performTraversals() 重新绘制
```

#### 1. 动画启动：ValueAnimator.start()

```java
// ValueAnimator.java
public void start() {
    // 确保在主线程
    if (Looper.myLooper() == null) {
        throw new AndroidRuntimeException("Animators may only be run on the main thread");
    }
    
    // 标记正在运行
    mRunning = true;
    mPlayingBackwards = false;
    mCurrentIteration = 0;
    mLastIteration = 0;
    
    // 设置开始时间
    long startTime = AnimationUtils.currentAnimationTimeMillis();
    mStartTime = startTime;
    
    // 添加到 AnimationHandler
    sAnimationHandler.addAnimationFrameCallback(this, 0);
}
```

#### 2. AnimationHandler：管理所有属性动画

属性动画通过 `AnimationHandler` 统一管理，它是一个单例：

```java
// ValueAnimator.java - 内部类
public static final AnimationHandler sAnimationHandler = new AnimationHandler();

private static class AnimationHandler extends Handler {
    // 保存所有正在运行的动画
    private final ArrayList<WeakReference<FrameCallback>> mAnimations = 
        new ArrayList<>();
    
    // 通过 Choreographer 接收 VSYNC 回调
    public void addAnimationFrameCallback(FrameCallback callback, int priority) {
        // 添加到回调列表
    }
    
    // Choreographer 回调
    private final Choreographer.FrameCallback mFrameCallback = new Choreographer.FrameCallback() {
        @Override
        public void doFrame(long frameTimeNanos) {
            // 遍历所有动画，调用它们的 doAnimationFrame
            doAnimationFrame(frameTimeNanos);
            // 继续注册下一帧
            postFrameCallback();
        }
    };
    
    void doAnimationFrame(long frameTimeNanos) {
        // 遍历所有动画
        for (int i = 0; i < callbacks.size(); i++) {
            FrameCallback callback = callbacks.get(i);
            if (callback != null) {
                // 关键：调用动画的 doAnimationFrame
                callback.doAnimationFrame(frameTimeNanos);
            }
        }
    }
}
```

#### 3. Choreographer：帧调度中心

```java
// ValueAnimator 实现了 FrameCallback 接口
public boolean doAnimationFrame(long frameTime) {
    // 1. 计算当前帧的动画值
    final long now = AnimationUtils.currentAnimationTimeMillis();
    final long remaining = (mStartTime + mDuration) - now;
    
    // 2. 计算动画进度
    float fraction = mDuration > 0 ? (float) (now - mStartTime) / mDuration : 1f;
    
    // 3. 应用插值
    if (mInterpolator != null) {
        fraction = mInterpolator.getInterpolation(fraction);
    }
    
    // 4. 设置动画值
    if (mEvaluator != null) {
        Object value = mEvaluator.evaluate(fraction, mStartValue, mEndValue);
        setAnimatedValue(value);
    }
    
    // 5. 通知监听器
    if (mUpdateListeners != null) {
        for (int i = 0; i < mUpdateListeners.size(); i++) {
            mUpdateListeners.get(i).onAnimationUpdate(this);
        }
    }
    
    return mRunning;
}
```

#### 4. setAnimatedValue：真正改变属性

```java
// ObjectAnimator.java
@Override
public void setAnimatedValue(Object target) {
    // 逐个设置每个属性的值
    for (int i = 0; i < mPropertyValues.length; i++) {
        PropertyValuesHolder pvh = mPropertyValues[i];
        pvh.setAnimatedValue(target);
    }
}

// PropertyValuesHolder.java
void setAnimatedValue(Object target) {
    if (mProperty != null) {
        // 通过 Property 直接设置值
        mProperty.set(target, getAnimatedValue());
    } else if (mSetter != null) {
        // 通过反射调用 setter 方法
        mSetter.invoke(target, getAnimatedValue());
    }
}
```

#### 5. 触发 ViewRootImpl 重绘

当属性值改变后，View 需要重新绘制。属性动画有两种方式触发绘制：

**方式一：通过 View.setProperty() 自动触发**

```java
// View.java
public void setTranslationX(float translationX) {
    // 1. 直接修改属性值
    mTranslationX = translationX;
    
    // 2.  invalidate 触发重绘
    invalidate();
    
    // 3.  invalidate 无效时，请求重新布局
    invalidateParentCaches();
}
```

**方式二：通过 onAnimationUpdate 手动触发**

```java
ObjectAnimator animator = ObjectAnimator.ofFloat(view, "translationX", 0, 100);
animator.addUpdateListener(new ValueAnimator.AnimatorUpdateListener() {
    @Override
    public void onAnimationUpdate(ValueAnimator animation) {
        // 这里修改属性后，View.invalidate() 会被自动调用
        // 但如果需要更强制刷新，可以手动调用：
        // view.setTranslationX(...);
        // view.getParent().requestLayout(); // 如果改变了布局参数
    }
});
animator.start();
```

#### 6. ViewRootImpl.scheduleTraversals()

无论哪种方式触发，最终都会汇聚到 `ViewRootImpl.scheduleTraversals()`：

```java
// ViewRootImpl.java
void scheduleTraversals() {
    if (!mTraversalScheduled) {
        mTraversalScheduled = true;
        
        // 通过 Choreographer 注册下一帧的绘制任务
        mChoreographer.postCallback(
            Choreographer.CALLBACK_TRAVERSAL,
            mTraversalRunnable,
            null
        );
    }
}
```

#### 7. Choreographer 的回调顺序

```java
// Choreographer.java
void doFrame(long frameTimeNanos, int frame) {
    // 按优先级顺序执行回调
    // 1. CALLBACK_INPUT - 输入事件
    // 2. CALLBACK_ANIMATION - 动画更新 ← 属性动画在这里更新值
    // 3. CALLBACK_TRAVERSAL - View 遍历/绘制 ← ViewRootImpl 在这里重绘
    
    doCallbacks(Choreographer.CALLBACK_INPUT, frameTimeNanos);
    doCallbacks(Choreographer.CALLBACK_ANIMATION, frameTimeNanos);
    doCallbacks(Choreographer.CALLBACK_TRAVERSAL, frameTimeNanos);
}
```

这意味着：
- **CALLBACK_ANIMATION** 阶段：属性动画计算新值，更新 View 属性
- **CALLBACK_TRAVERSAL** 阶段：ViewRootImpl 执行 performTraversals()，重新绘制整个 View 树

#### 属性动画 vs View 动画：与 ViewRootImpl 的区别

| 特性 | View 动画 | 属性动画 |
|-----|----------|---------|
| 触发方式 | `View.startAnimation()` | `ObjectAnimator.start()` |
| 回调机制 | 直接调用 `invalidate()` | 通过 AnimationHandler + Choreographer |
| 属性变化 | 只改变 Canvas 矩阵 | **真正改变 View 的成员变量** |
| 触发重绘 | 在 `applyLegacyAnimation()` 中 | 在 `setAnimatedValue()` 中 |
| 与 ViewRootImpl | 通过 `scheduleTraversals()` | 同样通过 `scheduleTraversals()` |
| 性能 | 较高（只重绘一次） | 较低（每帧都计算+重绘） |

#### 完整的帧流程时序图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         VSYNC 信号                                    │
│                              ↓                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │              Choreographer.doFrame()                            │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │ │
│  │  │ CALLBACK_INPUT  │  │ CALLBACK_ANIM   │  │CALLBACK_TRAV   │  │ │
│  │  │   输入事件       │→ │  属性动画更新值  │→ │  View 重绘     │  │ │
│  │  │                 │  │                 │  │                │  │ │
│  │  │                 │  │ ValueAnimator   │  │ performTraver  │  │ │
│  │  │                 │  │ .doAnimationFram│  │ sals()         │  │ │
│  │  │                 │  │                 │  │                │  │ │
│  │  │                 │  │ setAnimatedValue│  │ View.draw()    │  │ │
│  │  │                 │  │ setTranslationX │  │                │  │ │
│  │  │                 │  │ View.mTranslatio│  │                │  │ │
│  │  │                 │  │ nX = newValue    │  │                │  │ │
│  │  └─────────────────┘  └─────────────────┘  └────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                              ↓                                       │
│  屏幕刷新                                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

#### 为什么属性动画能改变实际属性？

通过上面的分析，答案很清楚了：

1. **直接修改成员变量**：`setTranslationX()` 会直接修改 `View.mTranslationX`
2. **属性反射机制**：`PropertyValuesHolder` 通过反射调用 `setTranslationX()` 方法
3. **自动触发重绘**：每个 setter 方法内部都调用了 `invalidate()` 或 `requestLayout()`
4. **ViewRootImpl 调度**：`invalidate()` 最终会调用 `ViewRootImpl.scheduleTraversals()`
5. **Choreographer 驱动**：每帧的更新由 Choreographer 的 VSYNC 信号统一驱动

这与 View 动画完全不同：View 动画只在 `draw()` 阶段通过 `canvas.concat(matrix)` 临时改变绘制位置，而不修改任何成员变量。

#### 属性动画的帧更新时机

属性动画是基于 VSYNC 信号驱动的，帧更新的时机如下：

```
VSYNC 信号触发
    ↓
Choreographer.doFrame()
    ↓
CALLBACK_ANIMATION 阶段（计算新值）
    ↓
setAnimatedValue() 更新属性
    ↓
View.setter() 触发 invalidate()
    ↓
CALLBACK_TRAVERSAL 阶段（重绘生效）
    ↓
屏幕刷新
```

**结论：属性动画设置的参数在下一帧才生效。**

| 操作 | 生效时机 |
|-----|---------|
| `animator.start()` | 立即注册到下一帧 |
| `animator.setDuration(1000)` | **不影响已启动的动画** |
| `animator.cancel()` | 立即停止，但当前帧可能已更新 |
| `animator.pause()` | 暂停，恢复后从当前位置继续 |
| 修改动画目标值 | 需要**重新创建动画实例** |

#### 动态修改动画参数

如果在动画运行过程中需要修改参数（如动态改变目标位置），**必须重新创建动画实例**：

```java
// ❌ 错误：动态修改参数无效
ObjectAnimator animator = ObjectAnimator.ofFloat(view, "translationX", 0, 100);
animator.start();
// 这里的修改不会影响正在运行的动画
animator.setFloatValues(0, 200); 

// ✅ 正确：重新创建动画
private ObjectAnimator currentAnimator;

private void animateTo(float targetX) {
    // 先取消之前的动画
    if (currentAnimator != null) {
        currentAnimator.cancel();
    }
    
    // 从当前位置开始动画
    float startX = view.getTranslationX();
    currentAnimator = ObjectAnimator.ofFloat(view, "translationX", startX, targetX);
    currentAnimator.setDuration(300);
    currentAnimator.start();
}
```

或者使用 `ValueAnimator` 手动控制：

```java
// 使用 ValueAnimator 手动控制进度
ValueAnimator animator = ValueAnimator.ofFloat(0, 1);
animator.addUpdateListener(animation -> {
    float fraction = (float) animation.getAnimatedValue();
    // 动态计算当前值
    float currentValue = startValue + (targetValue - startValue) * fraction;
    view.setTranslationX(currentValue);
});
```

#### 动画的 lifecycle 回调

```java
animator.addListener(new AnimatorListenerAdapter() {
    @Override
    public void onAnimationStart(Animator animation) {
        // 动画开始（重新开始时也会调用）
    }

    @Override
    public void onAnimationEnd(Animator animation) {
        // 动画结束
    }

    @Override
    public void onAnimationPause(Animator animation) {
        // 动画暂停
    }

    @Override
    public void onAnimationResume(Animator animation) {
        // 动画恢复
    }

    @Override
    public void onAnimationCancel(Animator animation) {
        // 动画取消（也会触发 onAnimationEnd）
    }
});
```

---

## 帧动画 (Drawable Animation)

### 什么是帧动画

帧动画（Frame Animation）按顺序播放一系列 Drawable 图像，类似于传统动画的播放方式。

### 使用方式

**XML 定义：**

```xml
<?xml version="1.0" encoding="utf-8"?>
<animation-list xmlns:android="http://schemas.android.com/apk/res/android"
    android:oneshot="false">

    <item android:drawable="@drawable/frame1" android:duration="100"/>
    <item android:drawable="@drawable/frame2" android:duration="100"/>
    <item android:drawable="@drawable/frame3" android:duration="100"/>
    <item android:drawable="@drawable/frame4" android:duration="100"/>

</animation-list>
```

**代码控制：**

```java
ImageView imageView = findViewById(R.id.imageView);
AnimationDrawable animationDrawable = (AnimationDrawable) imageView.getDrawable();

// 开始动画
animationDrawable.start();

// 停止动画
animationDrawable.stop();

// 判断是否正在运行
boolean isRunning = animationDrawable.isRunning();
```

### 注意事项

1. 帧动画会占用较多内存，注意图片大小
2. 使用 `android:oneshot="true"` 只播放一次
3. 在 Activity/Fragment 的 `onResume()` 中启动，`onPause()` 中停止

---

## 转场动画 (Transition API)

### Activity 转场动画

**方式一：overridePendingTransition**

```java
// 启动 Activity 时
startActivity(new Intent(this, SecondActivity.class));
overridePendingTransition(R.anim.fade_in, R.anim.fade_out);

// 关闭 Activity 时
finish();
overridePendingTransition(R.anim.fade_in, R.anim.fade_out);
```

**方式二：Theme 定义（API 21+）**

```xml
<!-- styles.xml -->
<style name="AppTheme" parent="Theme.MaterialComponents.Light.NoActionBar">
    <item name="android:windowActivityTransitions">true</item>
    <item name="android:windowContentTransitions">true</item>
    <item name="android:windowEnterTransition">@android:transition/fade</item>
    <item name="android:windowExitTransition">@android:transition/fade</item>
    <item name="android:windowSharedElementEnterTransition">@transition/shared_element</item>
    <item name="android:windowSharedElementExitTransition">@transition/shared_element</item>
</style>
```

**共享元素动画：**

```java
// 启动Activity
ActivityOptions options = ActivityOptions.makeSceneTransitionAnimation(
    this,
    sharedView, // 共享的 View
    "sharedName" // 共享元素名称
);
startActivity(new Intent(this, SecondActivity.class), options.toBundle());

// SecondActivity 中
getWindow().setSharedElementEnterTransition(...);
```

### Fragment 转场动画

```java
// 设置自定义动画
getFragmentManager().beginTransaction()
    .setCustomAnimations(
        R.anim.slide_in_right,
        R.anim.slide_out_left,
        R.anim.slide_in_left,
        R.anim.slide_out_right
    )
    .replace(R.id.container, fragment)
    .commit();

// 使用 FragmentTransitions (API 28+)
FragmentTransitionSupport.beginDelayedTransition(fragmentContainer);
```

---

## Material Design 动画

### Ripple Effect（波纹效果）

```xml
<!-- 普通波纹 -->
<Button
    android:background="?attr/selectableItemBackground"
    .../>

<!-- 有边界的波纹 -->
<Button
    android:background="?attr/selectableItemBackgroundBorderless"
    .../>
```

### State List Animator

```xml
<!-- res/animator/button_state.xml -->
<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_pressed="true">
        <set>
            <objectAnimator
                android:propertyName="translationZ"
                android:duration="100"
                android:valueTo="4dp"
                android:valueType="floatType"/>
        </set>
    </item>
    <item>
        <set>
            <objectAnimator
                android:propertyName="translationZ"
                android:duration="100"
                android:valueTo="0dp"
                android:valueType="floatType"/>
        </set>
    </item>
</selector>
```

```java
button.setStateListAnimator(AnimatorInflater.loadStateListAnimator(this, R.animator.button_state));
```

### Circular Reveal（圆形揭示）

```java
// 显示 View
View view = findViewById(R.id.revealView);
int cx = (view.getLeft() + view.getRight()) / 2;
int cy = (view.getTop() + view.getBottom()) / 2;
float finalRadius = (float) Math.hypot(view.getWidth(), view.getHeight());

Animator revealAnimator = ViewAnimationUtils.createCircularReveal(
    view, cx, cy, 0, finalRadius);
revealAnimator.setDuration(500);
view.setVisibility(View.VISIBLE);
revealAnimator.start();

// 隐藏 View
Animator hideAnimator = ViewAnimationUtils.createCircularReveal(
    view, cx, cy, finalRadius, 0);
hideAnimator.setDuration(500);
hideAnimator.addListener(new AnimatorListenerAdapter() {
    @Override
    public void onAnimationEnd(Animator animation) {
        view.setVisibility(View.INVISIBLE);
    }
});
hideAnimator.start();
```

### MotionLayout 动画

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.motion.widget.MotionLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/motionLayout"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    app:layoutDescription="@xml/scene">

    <View
        android:id="@+id/button"
        android:layout_width="64dp"
        android:layout_height="64dp"
        android:background="@color/purple_500"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintBottom_toBottomOf="parent"/>

</androidx.constraintlayout.motion.widget.MotionLayout>
```

```xml
<!-- res/xml/scene.xml -->
<?xml version="1.0" encoding="utf-8"?>
<MotionScene xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:motion="http://schemas.android.com/apk/res-auto">

    <Transition
        motion:constraintSetStart="@id/start"
        motion:constraintSetEnd="@id/end"
        motion:duration="1000">

        <OnSwipe
            motion:touchAnchorId="@+id/button"
            motion:touchAnchorSide="right"
            motion:dragDirection="dragRight"/>

        <KeyFrameSet>
            <KeyAttribute
                motion:motionTarget="@+id/button"
                motion:framePosition="50"
                android:rotation="45"/>
        </KeyFrameSet>

    </Transition>

    <ConstraintSet android:id="@+id/start">
        <Constraint
            android:id="@+id/button"
            android:layout_width="64dp"
            android:layout_height="64dp"
            android:rotation="0"/>
    </ConstraintSet>

    <ConstraintSet android:id="@+id/end">
        <Constraint
            android:id="@+id/button"
            android:layout_width="100dp"
            android:layout_height="100dp"
            android:rotation="180"/>
    </ConstraintSet>

</MotionScene>
```

---

## 动画性能优化

### 1. 使用硬件加速

```java
// 在 View 上启用硬件加速
view.setLayerType(View.LAYER_TYPE_HARDWARE, null);

// 或者在 Activity/Application 级别
<application android:hardwareAccelerated="true">
```

### 2. 减少重绘

- 使用 `canvas.save()` 和 `canvas.restore()` 限制绘制区域
- 避免在 `onDraw()` 中创建对象
- 使用 `clipRect()` 减少绘制区域

### 3. 使用 RecyclerView ItemAnimator

```java
// 自定义 Item 动画
RecyclerView.ItemAnimator itemAnimator = new DefaultItemAnimator();
itemAnimator.setAddDuration(300);
itemAnimator.setRemoveDuration(300);
recyclerView.setItemAnimator(itemAnimator);
```

### 4. 动画优化技巧

```java
// 使用nineoldandroids兼容库操作属性动画（在旧版本API）
// 替代方案：使用 AndroidX 动画库

// 避免在动画中触发过度绘制
// 使用 ViewPropertyAnimator（简洁的API）
view.animate()
    .alpha(0f)
    .translationX(100f)
    .setDuration(300)
    .setInterpolator(new AccelerateDecelerateInterpolator())
    .withStartAction(() -> {})
    .withEndAction(() -> {})
    .start();
```

### 5. 监控动画性能

```java
// 使用 Choreographer 监控帧率
Choreographer.getInstance().postFrameCallback(new Choreographer.FrameCallback() {
    @Override
    public void doFrame(long frameTimeNanos) {
        // 每一帧的回调
        // 计算帧率：1000000000L / (frameTimeNanos - lastFrameTime)
        Choreographer.getInstance().postFrameCallback(this);
    }
});
```

---

## 实战技巧

### 1. 避免动画中的内存泄漏

```java
// 正确做法：使用弱引用或在 onDestroy 中取消
public class MyActivity extends AppCompatActivity {
    private ObjectAnimator animator;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        animator = ObjectAnimator.ofFloat(view, "alpha", 1f, 0f);
        animator.start();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (animator != null) {
            animator.cancel(); // 取消动画
        }
    }
}
```

### 2. 在 XML 中定义动画，然后在代码中应用

```xml
<!-- res/anim/zoom_in.xml -->
<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android"
    android:interpolator="@android:anim/overshoot_interpolator">
    <scale
        android:fromXScale="0.0"
        android:toXScale="1.0"
        android:fromYScale="0.0"
        android:toYScale="1.0"
        android:pivotX="50%"
        android:pivotY="50%"
        android:duration="300"/>
    <alpha
        android:fromAlpha="0.0"
        android:toAlpha="1.0"
        android:duration="300"/>
</set>
```

```java
Animation animation = AnimationUtils.loadAnimation(context, R.anim.zoom_in);
view.startAnimation(animation);
```

### 3. 组合复杂动画

```java
// 实现点赞心跳效果
private void showHeartAnimation(View view) {
    // 放大出现
    view.setScaleX(0f);
    view.setScaleY(0f);
    view.setVisibility(View.VISIBLE);
    
    AnimatorSet set = new AnimatorSet();
    
    ObjectAnimator scaleUpX = ObjectAnimator.ofFloat(view, "scaleX", 0f, 1.2f, 1f);
    ObjectAnimator scaleUpY = ObjectAnimator.ofFloat(view, "scaleY", 0f, 1.2f, 1f);
    ObjectAnimator alpha = ObjectAnimator.ofFloat(view, "alpha", 0f, 1f);
    
    set.playTogether(scaleUpX, scaleUpY, alpha);
    set.setDuration(400);
    set.setInterpolator(new OvershootInterpolator());
    set.start();
}
```

### 4. 使用动画集合管理器

```java
// 管理所有动画，便于统一取消
public class AnimationManager {
    private final List<Animator> animators = new ArrayList<>();
    
    public void addAnimator(Animator animator) {
        animators.add(animator);
    }
    
    public void cancelAll() {
        for (Animator animator : animators) {
            animator.cancel();
        }
        animators.clear();
    }
}
```

### 5. 跨 Activity 共享元素

```java
// Activity A
ActivityOptions options = ActivityOptions.makeSceneTransitionAnimation(
    this,
    Pair.create(view1, "shared1"),
    Pair.create(view2, "shared2")
);
startActivity(intent, options.toBundle());

// Activity B
getWindow().setSharedElementEnterTransition(new ChangeTransform());
getWindow().setSharedElementReturnTransition(new ChangeTransform());
```

---

## 总结

| 动画类型 | 适用场景 | 优点 | 缺点 |
|---------|---------|------|------|
| View 动画 | 简单视觉效果 | 简单、性能好 | 不改变实际属性 |
| 属性动画 | 复杂动画、交互 | 功能强大、真改变属性 | 需 API 11+ |
| 帧动画 | 图片序列播放 | 简单直观 | 内存占用大 |
| Transition | 页面切换 | 流畅的转场效果 | 需 API 19+ |

**最佳实践：**
1. 简单动画用 View 动画，复杂动画用属性动画
2. 使用硬件加速提升性能
3. 记得在 onDestroy 中取消动画防止内存泄漏
4. Material Design 动画提升用户体验
5. 使用 AndroidX 动画库保证兼容性

---

## 参考资料

- [Android Developer - Property Animation](https://developer.android.com/guide/topics/graphics/prop-animation)
- [Android Developer - View Animation](https://developer.android.com/guide/topics/graphics/view-animation)
- [Material Design - Motion](https://material.io/design/motion/)

---

_本文档由 OpenClaw 自动生成_
