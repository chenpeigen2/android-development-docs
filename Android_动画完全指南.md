# Android 动画完全指南

> 源码版本：AOSP Android 17（API 37），`android-17.0.0_r1`。


_作者：OpenClaw_
_初稿日期：2026-03-08_

---

## 目录

- [概述](#概述)
- [View 动画 (Animation)](#view-动画-animation)
  - [什么是 View 动画](#什么是-view-动画)
  - [支持的动画类型](#支持的动画类型)
  - [在代码中使用 View Animation](#在代码中使用-view-animation)
  - [Interpolator（插值器）](#interpolator插值器)
  - [View 动画的局限性](#view-动画的局限性)
  - [View 动画底层原理：与 ViewRootImpl 的结合](#view-动画底层原理与-viewrootimpl-的结合)
    - [startAnimation：把 Animation 挂到 View，并请求后续绘制](#startanimation把-animation-挂到-view并请求后续绘制)
    - [applyLegacyAnimation：绘制侧求变换并传播失效](#applylegacyanimation绘制侧求变换并传播失效)
    - [Animation.getTransformation：时间、填充与重复](#animationgettransformation时间填充与重复)
    - [与属性动画的选择](#与属性动画的选择)
- [属性动画 (Property Animation)](#属性动画-property-animation)
  - [什么是属性动画](#什么是属性动画)
  - [核心类](#核心类)
  - [ValueAnimator 使用](#valueanimator-使用)
  - [ObjectAnimator 使用](#objectanimator-使用)
  - [多属性组合动画](#多属性组合动画)
  - [Interpolator（插值器）](#interpolator插值器-1)
    - [基础使用](#基础使用)
    - [内置插值器](#内置插值器)
    - [插值器底层原理](#插值器底层原理)
    - [自定义插值器](#自定义插值器)
    - [PathInterpolator（API 21+）](#pathinterpolatorapi-21)
  - [TypeEvaluator（类型估值器）](#typeevaluator类型估值器)
    - [内置 TypeEvaluator](#内置-typeevaluator)
    - [TypeEvaluator 底层原理](#typeevaluator-底层原理)
    - [插值器 + TypeEvaluator 完整流程](#插值器--typeevaluator-完整流程)
    - [自定义 TypeEvaluator](#自定义-typeevaluator)
    - [自定义复杂 TypeEvaluator：颜色渐变中间色](#自定义复杂-typeevaluator颜色渐变中间色)
    - [Interpolator vs TypeEvaluator 总结](#interpolator-vs-typeevaluator-总结)
  - [自定义估值器的使用](#自定义估值器的使用)
  - [动画监听器](#动画监听器)
  - [属性动画与 ViewRootImpl 的结合](#属性动画与-viewrootimpl-的结合)
    - [1. ValueAnimator 的播放状态](#1-valueanimator-的播放状态)
    - [2. AnimationHandler：线程内共享的帧来源](#2-animationhandler线程内共享的帧来源)
    - [3. doAnimationFrame：建立时间原点、暂停与 seek](#3-doanimationframe建立时间原点暂停与-seek)
    - [4. duration 与 repeat：按时间推进，而不是按帧计数](#4-duration-与-repeat按时间推进而不是按帧计数)
    - [5. AnimatorSet：父 pulse 与子动画禁止双重注册](#5-animatorset父-pulse-与子动画禁止双重注册)
    - [6. 求值与赋值：Interpolator、PropertyValuesHolder、setter](#6-求值与赋值interpolatorpropertyvaluesholdersetter)
    - [7. 与 Choreographer 五阶段和遍历回调衔接](#7-与-choreographer-五阶段和遍历回调衔接)
    - [8. end、cancel 与结束监听的时机](#8-endcancel-与结束监听的时机)
    - [9. 实战：可反复重定向且在 detach 取消的动画属性](#9-实战可反复重定向且在-detach-取消的动画属性)
- [帧动画 (Drawable Animation)](#帧动画-drawable-animation)
  - [什么是帧动画](#什么是帧动画)
  - [使用方式](#使用方式)
  - [注意事项](#注意事项)
- [转场动画 (Transition API)](#转场动画-transition-api)
  - [Activity 转场动画](#activity-转场动画)
  - [Fragment 转场动画](#fragment-转场动画)
- [Material Design 动画](#material-design-动画)
  - [Ripple Effect（波纹效果）](#ripple-effect波纹效果)
  - [State List Animator](#state-list-animator)
  - [Circular Reveal（圆形揭示）](#circular-reveal圆形揭示)
  - [MotionLayout 动画](#motionlayout-动画)
- [动画性能优化](#动画性能优化)
  - [1. 使用硬件加速](#1-使用硬件加速)
  - [2. 减少重绘](#2-减少重绘)
  - [3. 使用 RecyclerView ItemAnimator](#3-使用-recyclerview-itemanimator)
  - [4. 动画优化技巧](#4-动画优化技巧)
  - [5. 监控动画性能](#5-监控动画性能)
- [实战技巧](#实战技巧)
  - [1. 避免动画中的内存泄漏](#1-避免动画中的内存泄漏)
  - [2. 在 XML 中定义动画，然后在代码中应用](#2-在-xml-中定义动画然后在代码中应用)
  - [3. 组合复杂动画](#3-组合复杂动画)
  - [4. 使用动画集合管理器](#4-使用动画集合管理器)
  - [5. 跨 Activity 共享元素](#5-跨-activity-共享元素)
- [总结](#总结)
- [参考资料](#参考资料)

---

## 概述

本文以 Android 17 / API 37 为平台基线。下表区分各动画体系的引入版本，不把旧 API 的引入时间改写为 Android 17 新特性：

| 动画类型 | 引入版本 | 特点 |
|---------|---------|------|
| View 动画 | API 1 | 简单易用，但只改变视觉效果，不改变实际属性 |
| 属性动画 | API 11 | 真正改变对象属性，功能强大 |
| 帧动画 | API 1 | 播放一系列 Drawable 帧 |
| Transition 框架 | API 19 | 场景与布局变化；Activity 内容/共享元素转场为 API 21+，AndroidX Fragment 单独演进 |

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

#### startAnimation：把 Animation 挂到 View，并请求后续绘制

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public void startAnimation(Animation animation) {
    animation.setStartTime(Animation.START_ON_FIRST_FRAME);
    setAnimation(animation);
    invalidateParentCaches();
    invalidate(true);
}
```

它没有每帧 requestLayout。`START_ON_FIRST_FRAME` 使 Animation 在第一次真正求取 Transformation 时建立起始时间，避免把挂载到 View 与首次绘制之间的等待算进正常播放进度。

#### applyLegacyAnimation：绘制侧求变换并传播失效

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
private boolean applyLegacyAnimation(ViewGroup parent, long drawingTime,
        Animation a, boolean scalingRequired) {
    Transformation invalidationTransform;
    final int flags = parent.mGroupFlags;
    final boolean initialized = a.isInitialized();
    if (!initialized) {
        a.initialize(mRight - mLeft, mBottom - mTop, parent.getWidth(), parent.getHeight());
        a.initializeInvalidateRegion(0, 0, mRight - mLeft, mBottom - mTop);
        if (mAttachInfo != null) a.setListenerHandler(mAttachInfo.mHandler);
        onAnimationStart();
    }

    final Transformation t = parent.getChildTransformation();
    boolean more = a.getTransformation(drawingTime, t, 1f);
    if (scalingRequired && mAttachInfo.mApplicationScale != 1f) {
        if (parent.mInvalidationTransformation == null) {
            parent.mInvalidationTransformation = new Transformation();
        }
        invalidationTransform = parent.mInvalidationTransformation;
        a.getTransformation(drawingTime, invalidationTransform, 1f);
    } else {
        invalidationTransform = t;
    }
    if ((t.getTransformationType() & Transformation.TYPE_MATRIX) != 0) {
        mPrivateFlags4 |= PFLAG4_HAS_VIEW_PROPERTY_INVALIDATION;
        mPrivateFlags4 |= PFLAG4_HAS_MOVED;
    }

    if (more) {
        if (!a.willChangeBounds()) {
            if ((flags & (ViewGroup.FLAG_OPTIMIZE_INVALIDATE | ViewGroup.FLAG_ANIMATION_DONE)) ==
                    ViewGroup.FLAG_OPTIMIZE_INVALIDATE) {
                parent.mGroupFlags |= ViewGroup.FLAG_INVALIDATE_REQUIRED;
            } else if ((flags & ViewGroup.FLAG_INVALIDATE_REQUIRED) == 0) {
                parent.mPrivateFlags |= PFLAG_DRAW_ANIMATION;
                parent.invalidate(mLeft, mTop, mRight, mBottom);
            }
        } else {
            if (parent.mInvalidateRegion == null) {
                parent.mInvalidateRegion = new RectF();
            }
            final RectF region = parent.mInvalidateRegion;
            a.getInvalidateRegion(0, 0, mRight - mLeft, mBottom - mTop, region,
                    invalidationTransform);
            parent.mPrivateFlags |= PFLAG_DRAW_ANIMATION;

            final int left = mLeft + (int) region.left;
            final int top = mTop + (int) region.top;
            parent.invalidate(left, top, left + (int) (region.width() + .5f),
                    top + (int) (region.height() + .5f));
        }
    }
    return more;
}
```

返回的 more 来自 Animation 是否需要继续运行。若动画只改变 alpha 等不改变边界的效果，可按已有范围失效；若变换影响绘制范围，则计算 invalidate region 以覆盖旧位置与新位置。软件绘制把 Transformation 应用到 Canvas，硬件绘制还涉及 RenderNode 的动画矩阵，不能把两者都写成一个空的 saveLayerAlpha/restore。

#### Animation.getTransformation：时间、填充与重复

源码精简节选（省略注释；[Animation.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/animation/Animation.java)）：

```java
public boolean getTransformation(long currentTime, Transformation outTransformation) {
    if (mStartTime == -1) {
        mStartTime = currentTime;
    }

    final long startOffset = getStartOffset();
    final long duration = mDuration;
    float normalizedTime;
    if (duration != 0) {
        normalizedTime = ((float) (currentTime - (mStartTime + startOffset))) /
                (float) duration;
    } else {
        normalizedTime = currentTime < mStartTime ? 0.0f : 1.0f;
    }

    final boolean expired = normalizedTime >= 1.0f || isCanceled();
    mMore = !expired;

    if (!mFillEnabled) normalizedTime = Math.max(Math.min(normalizedTime, 1.0f), 0.0f);

    if ((normalizedTime >= 0.0f || mFillBefore) && (normalizedTime <= 1.0f || mFillAfter)) {
        if (!mStarted) {
            fireAnimationStart();
            mStarted = true;
            if (NoImagePreloadHolder.USE_CLOSEGUARD) {
                guard.open("cancel or detach or getTransformation");
            }
        }

        if (mFillEnabled) normalizedTime = Math.max(Math.min(normalizedTime, 1.0f), 0.0f);

        if (mCycleFlip) {
            normalizedTime = 1.0f - normalizedTime;
        }

        getTransformationAt(normalizedTime, outTransformation);
    }

    if (expired) {
        if (mRepeatCount == mRepeated || isCanceled()) {
            if (!mEnded) {
                mEnded = true;
                guard.close();
                fireAnimationEnd();
            }
        } else {
            if (mRepeatCount > 0) {
                mRepeated++;
            }

            if (mRepeatMode == REVERSE) {
                mCycleFlip = !mCycleFlip;
            }

            mStartTime = -1;
            mMore = true;

            fireAnimationRepeat();
        }
    }

    if (!mMore && mOneMoreTime) {
        mOneMoreTime = false;
        return true;
    }

    return mMore;
}
```

该方法使用 currentTime、mStartTime、mStartOffset、mDuration 计算规范化时间，处理 fillEnabled/fillBefore/fillAfter，再通过插值器和 applyTransformation 产生矩阵或 alpha。repeatCount、repeatMode 与 cycle flip 决定下一轮方向。duration=0 有自己的完成分支，不能除以零，也不能用“插值后的 fraction 小于 1”判断是否继续。

fillAfter 保留的是绘制变换，不会把终点写入 left/top。传统平移动画把按钮画到新位置后，常规触摸分配仍使用 View 的布局与属性矩阵，不使用这套 Animation 的临时绘制矩阵。

#### 与属性动画的选择

| 需求 | 更合适的实现 | 原因 |
|---|---|---|
| 对旧界面做一次视觉进入/退出 | View Animation | 绘制变换足以表达，不承担布局状态 |
| 移动后继续接受点击与拖动 | translation/scale 等属性动画 | View 属性矩阵参与显示与逆矩阵命中 |
| 改变兄弟占位、宽高或文字排版 | 明确修改布局状态 | translation 不会为兄弟重新分配空间 |
| 自绘进度、颜色、曲线参数 | ValueAnimator + 自定义 setter | 把连续数值写入绘制模型并按需 invalidate |

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

### Interpolator（插值器）

插值器定义动画值的变化速度曲线，决定动画是匀速、加速、减速还是弹跳等效果。

#### 基础使用

```java
// 设置内置插值器
ObjectAnimator animator = ObjectAnimator.ofFloat(view, "translationX", 0, 500);
animator.setDuration(1000);
animator.setInterpolator(new AccelerateDecelerateInterpolator()); // 先加速后减速
animator.start();

// 或者在 XML 中定义
android:interpolator="@android:anim/accelerate_decelerate_interpolator"
```

#### 内置插值器

| 插值器 | 效果 | 公式 |
|-------|------|------|
| `LinearInterpolator` | 匀速 | `fraction` |
| `AccelerateInterpolator` | 持续加速 | `fraction^2` |
| `DecelerateInterpolator` | 持续减速 | `1 - (1 - fraction)^2` |
| `AccelerateDecelerateInterpolator` | 先加速后减速 | `cos((fraction + 1) * PI) / 2 + 0.5` |
| `BounceInterpolator` | 弹跳效果 | 物理弹跳公式 |
| `OvershootInterpolator` | 超过目标值后回弹 | `1 + c * sin(fraction * PI * overshoot)` |
| `AnticipateInterpolator` | 开始时向后一点再前进 | `fraction^2 * (3 * fraction - 2)` |
| `CycleInterpolator` | 循环动画 | `sin(fraction * 2 * PI * cycles)` |
| `AnticipateOvershootInterpolator` | 向后+回弹 | 组合 |
| `PathInterpolator` | 自定义路径 | 贝塞尔曲线 |

#### 插值器底层原理

插值器的核心是 `getInterpolation(float input)` 方法：

```java
// Interpolator.java
public interface Interpolator extends TimeInterpolator {
    // input: 0-1 之间的动画进度
    // 返回: 修改后的进度值（可以超出 0-1 范围）
    float getInterpolation(float input);
}
```

**插值器 vs TypeEvaluator 的区别：**

```text
动画时间轴：
0.0 ---- 0.5 ---- 1.0 (时间)
   ↑
   │
   │ Interpolator 变换
   │
   ↓
0.0 ---- 0.8 ---- 1.0 (进度)  ← 这里的变化是"非线性的"
   ↑
   │
   │ TypeEvaluator 计算
   │
   ↓
0 ---- 100 ---- 200 (属性值)  ← 最终的属性值
```

**举例：**

```java
// 使用 AccelerateDecelerateInterpolator 的流程：
// 时间 0.0 → 插值 → 0.0   → 估值 → 0
// 时间 0.5 → 插值 → 0.5   → 估值 → 100  (匀速的话是100，但这里稍微不同)
// 时间 1.0 → 插值 → 1.0   → 估值 → 200
```

#### 自定义插值器

```java
// 自定义加速插值器
public class CustomAccelerateInterpolator implements Interpolator {
    private final float mFactor;

    public CustomAccelerateInterpolator(float factor) {
        mFactor = factor;
    }

    @Override
    public float getInterpolation(float input) {
        // 指数加速: input^factor
        if (mFactor == 1.0f) {
            return input * input;
        } else {
            return (float) Math.pow(input, mFactor);
        }
    }
}

// 使用
animator.setInterpolator(new CustomAccelerateInterpolator(2.0f));

// 或者继承 BaseInterpolator
public class CustomInterpolator extends BaseInterpolator {
    @Override
    public float getInterpolation(float input) {
        // 自定义曲线
        return input * input * (3 - 2 * input); // 平滑step
    }
}
```

#### PathInterpolator（API 21+）

使用贝塞尔曲线定义插值器：

```java
// 方式一：代码创建
Path path = new Path();
path.moveTo(0, 0);
path.quadTo(0.5f, 1f, 1f, 1f); // 贝塞尔曲线
Interpolator interpolator = PathInterpolatorCompat.create(path, duration);

// 方式二：XML 定义
<!-- res/animator/fast_out_slow_in.xml -->
<?xml version="1.0" encoding="utf-8"?>
<pathInterpolator xmlns:android="http://schemas.android.com/apk/res/android"
    android:pathData="M0,0 C0.4,0 0.2,1 1,1"/>

// 使用
animator.setInterpolator(AnimationUtils.loadInterpolator(this, R.animator.fast_out_slow_in));
```

### TypeEvaluator（类型估值器）

TypeEvaluator 负责根据插值后的进度，计算出**最终的属性值**。

```java
// TypeEvaluator 接口
public interface TypeEvaluator<T> {
    // fraction: 经过插值器变换后的进度 (0-1)
    // startValue: 起始值
    // endValue: 结束值
    // 返回: 计算后的属性值
    T evaluate(float fraction, T startValue, T endValue);
}
```

#### 内置 TypeEvaluator

| TypeEvaluator | 适用类型 | 说明 |
|--------------|---------|------|
| `IntEvaluator` | Integer | 整数值估值 |
| `FloatEvaluator` | Float | 浮点值估值 |
| `ArgbEvaluator` | Integer (颜色) | 颜色渐变 |
| `PointEvaluator` | Point | 点坐标估值 |
| `PointFEvaluator` | PointF | 浮点坐标估值 |
| `RectEvaluator` | Rect | 矩形估值 |

#### TypeEvaluator 底层原理

数值估值可理解为 start + fraction * (end - start)。原文逐字节线性插值 ARGB 并非 Android 17 的 int 颜色实现：固定 tag 的 ArgbEvaluator.evaluate 将 RGB 按 2.2 次幂转换到线性空间插值，再按 1/2.2 次幂转回；alpha 直接插值。应用使用 ArgbEvaluator / ObjectAnimator.ofArgb，不把旧公式当成平台逐字源码。依据：[ArgbEvaluator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/ArgbEvaluator.java)。

#### 插值器 + TypeEvaluator 完整流程

```text
伪代码（单次求值阶段，不是 ValueAnimator.start 实现）：
动画时间 -> 原始 fraction -> TimeInterpolator
  -> PropertyValuesHolder / TypeEvaluator -> 当前值
  -> 更新监听器；ObjectAnimator 再应用目标属性
```

start() 负责状态初始化和注册后续帧回调，不是在 start 内一次算完动画。重复、反向、延迟、时长缩放和 seek 另有状态处理；超调插值器结果不保证始终在 0..1。依据：[ValueAnimator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/ValueAnimator.java)。

#### 自定义 TypeEvaluator

```java
// 自定义 PointF 估值器
public class PointFEvaluator implements TypeEvaluator<PointF> {

    private PointF mPoint;

    public PointFEvaluator() {
        // 复用对象，减少 GC
    }

    public PointFEvaluator(PointF reuse) {
        mPoint = reuse;
    }

    @Override
    public PointF evaluate(float fraction, PointF startValue, PointF endValue) {
        float x = startValue.x + fraction * (endValue.x - startValue.x);
        float y = startValue.y + fraction * (endValue.y - startValue.y);

        // 复用对象
        if (mPoint != null) {
            mPoint.set(x, y);
            return mPoint;
        } else {
            return new PointF(x, y);
        }
    }
}

// 使用自定义估值器
ValueAnimator animator = ValueAnimator.ofObject(new PointFEvaluator(),
    new PointF(0, 0), new PointF(300, 500));
animator.setDuration(1000);
animator.start();
```

#### 自定义复杂 TypeEvaluator：颜色渐变中间色

```java
// 自定义只改变色相的估值器
public class HueEvaluator implements TypeEvaluator<Integer> {
    @Override
    public Integer evaluate(float fraction, Integer startValue, Integer endValue) {
        float[] hsv = new float[3];
        Color.colorToHSV(startValue, hsv);

        float[] hsvEnd = new float[3];
        Color.colorToHSV(endValue, hsvEnd);

        // 只改变色相
        hsv[0] = hsv[0] + fraction * (hsvEnd[0] - hsv[0]);

        return Color.HSVToColor(hsv);
    }
}

// 使用
ValueAnimator animator = ValueAnimator.ofObject(new HueEvaluator(),
    Color.RED, Color.BLUE);
```

#### Interpolator vs TypeEvaluator 总结

| 概念 | 作用 | 修改的是 |
|-----|------|---------|
| **Interpolator** | 控制动画**进度**的变化速度 | 时间进度映射后的 fraction，可超调 |
| **TypeEvaluator** | 根据进度**计算属性值** | 实际的属性值 |

```text
时间 → Interpolator → TypeEvaluator → 属性值
0.0  →    0.0      →     0        →  0px
0.5  →    0.5      →    100       →  100px (匀速)
0.5  →    0.8      →    160       →  160px (加速后)
1.0  →    1.0      →    200       →  200px
```

### 自定义估值器的使用

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

#### 1. ValueAnimator 的播放状态

ValueAnimator 实现的是 `AnimationHandler.AnimationFrameCallback`，不是 Choreographer.FrameCallback。它可以自行注册 pulse，也可以由 AnimatorSet 统一推进。

| 字段 | 作用 |
|---|---|
| `mStarted` / `mRunning` | 已启动与已进入实际播放；有 startDelay 时二者可不同 |
| `mSelfPulse` | 是否自己向 AnimationHandler 注册帧回调 |
| `mStartTime` / `mLastFrameTime` | 动画时间原点与最后一帧时间，单位毫秒 |
| `mStartDelay` / `mDuration` | 未经系统缩放的启动延迟和单轮时长 |
| `mOverallFraction` | 包含重复轮数的总进度，不局限于 0..1 |
| `mCurrentFraction` | 当前轮经过插值器处理后的进度 |
| `mSeekFraction` | 显式 seek 的进度，在首次 pulse 时修正时间原点 |
| `mPaused` / `mResumed` / `mPauseTime` | 暂停恢复时修正播放时间，避免把暂停间隔计入进度 |

源码精简节选（省略注释；[ValueAnimator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/ValueAnimator.java)）：

```java
private void start(boolean playBackwards) {
    if (Looper.myLooper() == null) {
        throw new AndroidRuntimeException("Animators may only be run on Looper threads");
    }
    mReversing = playBackwards;
    mSelfPulse = !mSuppressSelfPulseRequested;
    if (playBackwards && mSeekFraction != -1 && mSeekFraction != 0) {
        if (mRepeatCount == INFINITE) {
            float fraction = (float) (mSeekFraction - Math.floor(mSeekFraction));
            mSeekFraction = 1 - fraction;
        } else {
            mSeekFraction = 1 + mRepeatCount - mSeekFraction;
        }
    }
    mStarted = true;
    mPaused = false;
    mRunning = false;
    mAnimationEndRequested = false;
    mLastFrameTime = -1;
    mFirstFrameTime = -1;
    mStartTime = -1;
    addAnimationCallback(0);

    if (mStartDelay == 0 || mSeekFraction >= 0 || mReversing) {
        startAnimation();
        if (mSeekFraction == -1) {
            setCurrentPlayTime(0);
        } else {
            setCurrentFraction(mSeekFraction);
        }
    }
}
```

启动首先检查当前线程有 Looper。涉及 View 的动画还必须在该 View 所属线程操作；“有 Looper”不代表任意后台 HandlerThread 都可修改 Activity 的 View。

无 startDelay、已有 seek 或反向启动时，start 会立即初始化并设置当前播放值；正常零延迟动画的第一次 update 因而不必等到下一次 Vsync。后续连续推进才由帧 pulse 驱动。

#### 2. AnimationHandler：线程内共享的帧来源

源码精简节选（省略注释；[AnimationHandler.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/AnimationHandler.java)）：

```java
private final Choreographer.FrameCallback mFrameCallback = new Choreographer.FrameCallback() {
    @Override
    public void doFrame(long frameTimeNanos) {
        doAnimationFrame(frameTimeNanos / TimeUtils.NANOS_PER_MS);
        if (mAnimationCallbacks.size() > 0) {
            getProvider().postFrameCallback(this);
        }
    }
};

public void addAnimationFrameCallback(final AnimationFrameCallback callback, long delay) {
    if (mAnimationCallbacks.size() == 0) {
        getProvider().postFrameCallback(mFrameCallback);
    }
    if (!mAnimationCallbacks.contains(callback)) {
        mAnimationCallbacks.add(callback);
    }

    if (delay > 0) {
        mDelayedCallbackStartTime.put(callback, (SystemClock.uptimeMillis() + delay));
    }
}

private void doAnimationFrame(long frameTime) {
    long currentTime = SystemClock.uptimeMillis();
    final int size = mAnimationCallbacks.size();
    for (int i = 0; i < size; i++) {
        final AnimationFrameCallback callback = mAnimationCallbacks.get(i);
        if (callback == null) {
            continue;
        }
        if (isCallbackDue(callback, currentTime)) {
            callback.doAnimationFrame(frameTime);
        }
    }
    cleanUpList();
}

private class MyFrameCallbackProvider implements AnimationFrameCallbackProvider {

    final Choreographer mChoreographer = Choreographer.getInstance();

    @Override
    public void postFrameCallback(Choreographer.FrameCallback callback) {
        mChoreographer.postFrameCallback(callback);
    }

    @Override
    public long getFrameDelay() {
        return Choreographer.getFrameDelay();
    }

    @Override
    public void setFrameDelay(long delay) {
        Choreographer.setFrameDelay(delay);
    }
}
```

默认 handler 存在 ThreadLocal 中。同线程的多个 animator 共享一次 Choreographer 帧回调，handler 在帧内依次推进它们；只要列表还有回调就重发下一帧。纳秒在桥接点除以 `NANOS_PER_MS`，所以 ValueAnimator.doAnimationFrame 接收毫秒，不能再把输入按纳秒计算 duration。

列表删除采用先置 null、帧末清理的策略，避免动画在回调中 cancel 导致遍历索引立即错位。延迟回调的到期判断与动画自己的 startDelay 是两个层次，不应把所有延迟都写成一个 Handler.postDelayed。

#### 3. doAnimationFrame：建立时间原点、暂停与 seek

源码精简节选（省略注释；[ValueAnimator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/ValueAnimator.java)）：

```java
public final boolean doAnimationFrame(long frameTime) {
    if (mStartTime < 0) {
        mStartTime = mReversing
                ? frameTime
                : frameTime + (long) (mStartDelay * resolveDurationScale());
    }
    if (mPaused) {
        mPauseTime = frameTime;
        removeAnimationCallback();
        return false;
    } else if (mResumed) {
        mResumed = false;
        if (mPauseTime > 0) {
            mStartTime += (frameTime - mPauseTime);
        }
    }

    if (!mRunning) {
        if (mStartTime > frameTime && mSeekFraction == -1) {
            return false;
        } else {
            mRunning = true;
            startAnimation();
        }
    }

    if (mLastFrameTime < 0) {
        if (mSeekFraction >= 0) {
            long seekTime = (long) (getScaledDuration() * mSeekFraction);
            mStartTime = frameTime - seekTime;
            mSeekFraction = -1;
        }
    }
    mLastFrameTime = frameTime;
    final long currentTime = Math.max(frameTime, mStartTime);
    boolean finished = animateBasedOnTime(currentTime);

    if (finished) {
        endAnimation(true );
    }
    return finished;
}
```

第一次 pulse 建立 mStartTime，正向播放将按缩放后的 startDelay 推后；尚未到开始时间则直接返回。恢复时把暂停间隔加到 mStartTime，令动画从暂停处继续。seek 则反推时间原点，使下一帧的时间公式与指定 fraction 连续。

#### 4. duration 与 repeat：按时间推进，而不是按帧计数

源码精简节选（省略注释；[ValueAnimator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/ValueAnimator.java)）：

```java
private float resolveDurationScale() {
    return mDurationScale >= 0f ? mDurationScale : sDurationScale;
}

private long getScaledDuration() {
    return (long)(mDuration * resolveDurationScale());
}

public long getTotalDuration() {
    if (mRepeatCount == INFINITE) {
        return DURATION_INFINITE;
    } else {
        return mStartDelay + (mDuration * (mRepeatCount + 1));
    }
}

boolean animateBasedOnTime(long currentTime) {
    boolean done = false;
    if (mRunning) {
        final long scaledDuration = getScaledDuration();
        final float fraction = scaledDuration > 0 ?
                (float)(currentTime - mStartTime) / scaledDuration : 1f;
        final float lastFraction = mOverallFraction;
        final boolean newIteration = (int) fraction > (int) lastFraction;
        final boolean lastIterationFinished = (fraction >= mRepeatCount + 1) &&
                (mRepeatCount != INFINITE);
        if (scaledDuration == 0) {
            done = true;
        } else if (newIteration && !lastIterationFinished) {
            notifyListeners(AnimatorCaller.ON_REPEAT, false);
        } else if (lastIterationFinished) {
            done = true;
        }
        mOverallFraction = clampFraction(fraction);
        float currentIterationFraction = getCurrentIterationFraction(
                mOverallFraction, mReversing);
        animateValue(currentIterationFraction);
    }
    return done;
}
```

`setDuration(300)` 表示单轮名义时长 300ms。实际播放用 `scaledDuration = (long)(mDuration * resolveDurationScale())`，正向 startDelay 同样缩放。有限重复的 getTotalDuration 返回 `startDelay + duration * (repeatCount + 1)`，是名义总时长，不把系统动画缩放乘进去；INFINITE 返回 DURATION_INFINITE。

例：startDelay=100ms、duration=300ms、repeatCount=1，名义总时长是 700ms；系统 scale=2 时，按时间公式对应的延迟与两轮播放合计约 1400ms，实际回调发生在帧边界。120Hz 只会比 60Hz 有更多采样机会，不会把同一个 300ms 动画自动缩短到 150ms。

若丢帧，下一次 pulse 依据当前时间跳到正确进度，不通过补发所有遗漏帧来追赶。源码只在观察到跨轮且尚未整体结束时通知 repeat，不能依赖每一个理论轮次都在卡顿后补发一次回调。

`REVERSE` 模式在奇偶轮间反转单轮 fraction；最终值需同时考虑 repeatCount 与 reversing。插值器可超调，mCurrentFraction 和最终值可能暂时超出 0..1 或起终点范围，业务 setter 应明确是否允许这种效果。

#### 5. AnimatorSet：父 pulse 与子动画禁止双重注册

源码精简节选（省略注释；[ValueAnimator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/ValueAnimator.java)）：

```java
boolean pulseAnimationFrame(long frameTime) {
    if (mSelfPulse) {
        return false;
    }
    return doAnimationFrame(frameTime);
}

private void addAnimationCallback(long delay) {
    if (!mSelfPulse) {
        return;
    }
    getAnimationHandler().addAnimationFrameCallback(this, delay);
}
```

源码精简节选（省略注释；[AnimatorSet.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/AnimatorSet.java)）：

```java
private void pulseFrame(Node node, long animPlayTime) {
    if (!node.mEnded) {
        float durationScale = ValueAnimator.getDurationScale();
        durationScale = durationScale == 0  ? 1 : durationScale;
        if (node.mAnimation.pulseAnimationFrame((long) (animPlayTime * durationScale))) {
            node.mEnded = true;
        }
    }
}
```

AnimatorSet 按依赖节点计算每个子动画的播放时间，子项通过 startWithoutPulsing 启动，由父调用 pulseAnimationFrame。mSelfPulse 防止子项又向 handler 注册一套时钟，否则同一帧可能推进两次且破坏集合的时序。

集合中的子动画可以有不同 delay/duration；不要一边让集合持有它，一边又单独 start 同一个实例。重用配置可以 clone 或重新创建动画，但运行实例的归属应明确。

#### 6. 求值与赋值：Interpolator、PropertyValuesHolder、setter

源码精简节选（省略注释；[ValueAnimator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/ValueAnimator.java)）：

```java
void animateValue(float fraction) {
    if (TRACE_ANIMATION_FRACTION) {
        Trace.traceCounter(Trace.TRACE_TAG_VIEW, getNameForTrace() + hashCode(),
                (int) (fraction * 1000));
    }
    if (mValues == null) {
        return;
    }
    fraction = mInterpolator.getInterpolation(fraction);
    mCurrentFraction = fraction;
    int numValues = mValues.length;
    for (int i = 0; i < numValues; ++i) {
        mValues[i].calculateValue(fraction);
    }
    if (mSeekFraction >= 0 || mStartListenersCalled) {
        callOnList(mUpdateListeners, AnimatorCaller.ON_UPDATE, this, false);
    }
}
```

源码精简节选（省略注释；[ObjectAnimator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/ObjectAnimator.java)）：

```java
void animateValue(float fraction) {
    final Object target = getTarget();
    super.animateValue(fraction);
    int numValues = mValues.length;
    for (int i = 0; i < numValues; ++i) {
        mValues[i].setAnimatedValue(target);
    }
}
```

源码精简节选（省略注释；[PropertyValuesHolder.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/PropertyValuesHolder.java)）：

```java
void calculateValue(float fraction) {
    Object value = mKeyframes.getValue(fraction);
    mAnimatedValue = mConverter == null ? value : mConverter.convert(value);
}
```

源码精简节选（省略注释；[PropertyValuesHolder.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/PropertyValuesHolder.java)）：

```java
void setAnimatedValue(Object target) {
    if (mProperty != null) {
        mProperty.set(target, getAnimatedValue());
    }
    if (mSetter != null) {
        try {
            mTmpValueArray[0] = getAnimatedValue();
            mSetter.invoke(target, mTmpValueArray);
        } catch (InvocationTargetException e) {
            Log.e("PropertyValuesHolder", e.toString());
        } catch (IllegalAccessException e) {
            Log.e("PropertyValuesHolder", e.toString());
        }
    }
}
```

ValueAnimator 先通过 Interpolator 改变 fraction，再让各 PropertyValuesHolder 根据 keyframe/evaluator 算值，最后通知 update listener。ObjectAnimator 的重载在 super 返回之后才逐个赋给 target，因此 **ObjectAnimator 的 update listener 可以读到当前计算值，但不应假定目标所有 setter 已在本帧执行完**。

PropertyValuesHolder 可以使用 Property 对象，也可以调用已解析的 setter；具体 float/int 专用 holder 还有优化路径，不能概括为“所有属性每帧都重新反射查找方法”。普通业务对象的 setter 不自动刷新 View。

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public void setTranslationX(float translationX) {
    if (translationX != getTranslationX()) {
        mPrivateFlags4 |= PFLAG4_HAS_MOVED;
        invalidateViewProperty(true, false);
        mRenderNode.setTranslationX(translationX);
        invalidateViewProperty(false, true);

        invalidateParentIfNeededAndWasQuickRejected();
        notifySubtreeAccessibilityStateChangedIfNeeded();
    }
}
```

translationX 更新 RenderNode 属性，并走 View 自带的属性失效流程。它改变 View 的显示与变换命中，不改变 left/right；动画宽高、边距时则需 setter 自己修改布局参数并 requestLayout，成本模型完全不同。

#### 7. 与 Choreographer 五阶段和遍历回调衔接

```text
INPUT(0)
ANIMATION(1)
  AnimationHandler -> ValueAnimator / AnimatorSet pulse
    插值、求值 -> ObjectAnimator setter 或 update listener
      View 属性失效 / 自绘 invalidate / 尺寸 requestLayout
INSETS_ANIMATION(2)
TRAVERSAL(3)
  TraversalCallback.onVsync(FrameData)
    doTraversal(frameTimeNanos) -> performTraversals(frameTimeNanos)
COMMIT(4)
```

ViewRootImpl 使用 `postVsyncCallback(CALLBACK_TRAVERSAL, mTraversalCallback)`。TraversalCallback 的接口类型是 VsyncCallback，队列类型仍是 TRAVERSAL；不能误写成公共 postFrameCallback 的 ANIMATION 阶段。图中顺序是 CPU 回调顺序，RenderThread、GPU 和 SurfaceFlinger 还有各自的执行与同步时间线。

#### 8. end、cancel 与结束监听的时机

源码精简节选（省略注释；[ValueAnimator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/animation/ValueAnimator.java)）：

```java
public void cancel() {
    if (Looper.myLooper() == null) {
        throw new AndroidRuntimeException("Animators may only be run on Looper threads");
    }
    if (mAnimationEndRequested) {
        if (consumePendingEndListeners(false )) {
            if (mRunning) {
                notifyListeners(AnimatorCaller.ON_CANCEL, false );
            }
            completeEndAnimation(false , "notifyAnimEndByCancel");
        }
        return;
    }
    if ((mStarted || mRunning || mStartListenersCalled) && mListeners != null) {
        if (!mRunning) {
            notifyStartListeners(mReversing);
        }
        notifyListeners(AnimatorCaller.ON_CANCEL, false);
    }
    endAnimation();
}

public void end() {
    if (Looper.myLooper() == null) {
        throw new AndroidRuntimeException("Animators may only be run on Looper threads");
    }
    if (!mRunning) {
        startAnimation();
        mStarted = true;
    } else if (!mInitialized) {
        initAnimation();
    }
    animateValue(shouldPlayBackward(mRepeatCount, mReversing) ? 0f : 1f);
    if (mAnimationEndRequested) {
        consumePendingEndListeners(true );
        return;
    }
    endAnimation();
}

private void endAnimation(boolean fromLastFrame) {
    if (mAnimationEndRequested) {
        return;
    }
    final boolean postNotifyEndListener = sPostNotifyEndListenerEnabled && mListeners != null
            && fromLastFrame && getScaledDuration() > 0;
    removeAnimationCallback();

    mAnimationEndRequested = true;
    mPaused = false;
    boolean notify = (mStarted || mRunning) && mListeners != null;
    if (notify && !mRunning) {
        notifyStartListeners(mReversing);
    }
    mLastFrameTime = -1;
    mFirstFrameTime = -1;
    mStartTime = -1;
    notifyEndListenersFromEndAnimation(mReversing, postNotifyEndListener);
    if (Trace.isTagEnabled(Trace.TRACE_TAG_VIEW)) {
        Trace.asyncTraceEnd(Trace.TRACE_TAG_VIEW, getNameForTrace(),
                System.identityHashCode(this));
    }
}
```

`cancel()` 不负责把属性推进终值，已启动动画通常先通知 cancel 再结束；`end()` 先按方向推进到结束值。取消也会走结束通知，不能在 onAnimationEnd 无条件提交“操作成功”。

该 tag 还有 `sPostNotifyEndListenerEnabled` 控制的路径：正常最后一帧结束、存在监听器、有效时长大于零等条件满足时，结束通知可以延后发布。源码另行处理已挂起结束回调期间的 cancel/end。业务既不能把 onAnimationEnd 当作 GPU 已呈现最后一帧的信号，也不应依赖它必定与最后一次 setter 同步栈内执行。

#### 9. 实战：可反复重定向且在 detach 取消的动画属性

以下是独立应用 View 示例。调用 animateTo 可以从当前显示值转向新目标；先清旧动画引用再 cancel，避免旧 onAnimationEnd 误清新实例。系统关闭动画时直接写终态。

```kotlin
import android.animation.Animator
import android.animation.AnimatorListenerAdapter
import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View

class AnimatedMeter @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.BLUE }
    private var value = 0f
    private var running: ValueAnimator? = null

    fun animateTo(target: Float, durationMs: Long = 300L) {
        require(target.isFinite() && target in 0f..1f)
        require(durationMs >= 0L)
        val old = running
        running = null
        old?.cancel()
        if (durationMs == 0L ||
            (android.os.Build.VERSION.SDK_INT >= 26 && !ValueAnimator.areAnimatorsEnabled())) {
            value = target
            invalidate()
            return
        }
        val next = ValueAnimator.ofFloat(value, target).apply {
            duration = durationMs
            addUpdateListener {
                value = it.animatedValue as Float
                invalidate()
            }
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    if (running === animation) running = null
                }
            })
        }
        running = next
        next.start()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val available = (width - paddingLeft - paddingRight).coerceAtLeast(0)
        canvas.drawRect(paddingLeft.toFloat(), paddingTop.toFloat(),
            paddingLeft + available * value, (height - paddingBottom).toFloat(), paint)
    }

    override fun onDetachedFromWindow() {
        val old = running
        running = null
        old?.cancel()
        super.onDetachedFromWindow()
    }
}
```

调用方应在 UI 线程使用，并给此示例 View 设置明确尺寸。若页面需要保存目标进度，应把业务目标存在 ViewModel/状态模型里，视图重建后恢复；动画瞬时值只是显示状态，不应承担业务数据持久化。

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

`overridePendingTransition()` 自 API 34 起废弃。Android 17 优先使用 API 34+ 的 `overrideActivityTransition()`，配置应放在参与转场的目标 Activity，而不是机械替换旧调用位置。

```kotlin
// 在 Activity B 的 onCreate 中配置；A 负责启动 B。
if (Build.VERSION.SDK_INT >= 34) {
    overrideActivityTransition(
        Activity.OVERRIDE_TRANSITION_OPEN, R.anim.fade_in, R.anim.fade_out
    )
    overrideActivityTransition(
        Activity.OVERRIDE_TRANSITION_CLOSE, R.anim.fade_in, R.anim.fade_out
    )
}
```

API 33 及以下的历史兼容路径仍可在 `startActivity` / `finish` 后紧接旧 `overridePendingTransition`。内容/共享元素转场是另一套机制；`ActivityOptions.makeSceneTransitionAnimation` 自 API 21 提供，不应和 API 19 的场景 Transition 混为一谈。依据：[Activity.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Activity.java)（转场 API 及优先级注释）。

在 Android 16+ 且 targetSdk >= 36 时，预测返回系统动画默认启用；这也是 Android 17 升级必须回归的既有变化，而非 Android 17 新增。不要仅依赖旧 onBackPressed/KEYCODE_BACK 拦截实现返回动画，应用应采用支持的返回分发机制并测试手势取消。依据：[Android 16 target 行为变化](https://developer.android.com/about/versions/16/behavior-changes-16)。

### Fragment 转场动画

新代码使用 AndroidX Fragment，不把旧 `getFragmentManager()` 与 AndroidX transition 内部类混用。`FragmentTransitionSupport.beginDelayedTransition(...)` 不是应用应调用的公开入口。

```kotlin
// 位于 FragmentActivity/AppCompatActivity；fragment 为 AndroidX Fragment。
supportFragmentManager.beginTransaction()
    .setReorderingAllowed(true)
    .setCustomAnimations(
        R.anim.slide_in_right, R.anim.slide_out_left,
        R.anim.slide_in_left, R.anim.slide_out_right
    )
    .replace(R.id.container, fragment)
    .addToBackStack(null)
    .commit()
```

Fragment 的 enter/exit/shared-element transition 与普通 ViewGroup 的 `androidx.transition.TransitionManager.beginDelayedTransition(sceneRoot)` 不同；后者不是通用的 Fragment 转场启动器。预测返回支持取决于 AndroidX 版本和动画类型，本文不追改依赖号。依据：[官方 Fragment 动画指南](https://developer.android.com/guide/fragments/animate)。

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
int cx = view.getWidth() / 2; // 目标 View 局部坐标，不加父坐标偏移
int cy = view.getHeight() / 2;
float finalRadius = (float) Math.hypot(
    Math.max(cx, view.getWidth() - cx), Math.max(cy, view.getHeight() - cy));

Animator revealAnimator = ViewAnimationUtils.createCircularReveal(
    view, cx, cy, 0, finalRadius);
revealAnimator.setDuration(500);
view.setVisibility(View.VISIBLE);
revealAnimator.start();

// 隐藏 View（在另外一次业务动作中执行，不与 revealAnimator 同时 start）
Animator hideAnimator = ViewAnimationUtils.createCircularReveal(
    view, cx, cy, finalRadius, 0);
hideAnimator.setDuration(500);
hideAnimator.addListener(new AnimatorListenerAdapter() {
    private boolean cancelled;
    @Override public void onAnimationCancel(Animator animation) { cancelled = true; }
    @Override public void onAnimationEnd(Animator animation) {
        if (!cancelled) view.setVisibility(View.INVISIBLE);
    }
});
hideAnimator.start();
```

圆心必须使用目标 View 的局部坐标。上述显示和隐藏片段分别在业务事件中使用，不能一次性连续启动。创建 reveal 前须确认 View 已 attach 且完成布局；页面退出时取消旧 animator。每次创建新 animator，不能暂停/恢复复用这个一次性动画；旧 hide 被取消时不应在 onAnimationEnd 隐藏新显示的页面。依据：[AOSP 17 ViewAnimationUtils.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewAnimationUtils.java)。

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
<?xml version="1.0" encoding="utf-8"?>
<!-- res/xml/scene.xml -->
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

`setLayerType(LAYER_TYPE_HARDWARE)` 是在已有硬件加速窗口中缓存 View 的离屏层，不是开启窗口硬件加速。窗口级配置在 manifest 中；不要把 XML 写进 Java 代码块。临时属性动画可按需使用：

```kotlin
view.animate().alpha(0f).setDuration(300L).withLayer().start()
```

`withLayer()` 会在动画结束后恢复先前层类型，仍应避免无测量依据地给所有 View 建层。频繁变更内容会使缓存失效并增加显存成本。依据：[官方硬件加速指南](https://developer.android.com/develop/ui/views/graphics/hardware-accel)。

### 2. 减少重绘

- `canvas.save()` / `restore()` 仅保存恢复矩阵和裁剪状态；限制区域需要配合 `clipRect()` 等操作
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
// NineOldAndroids 仅属早期 API < 11 的历史兼容方案，不作为 Android 17 新项目建议。
// 平台属性动画与 AndroidX 库按实际功能选择，不在此追改依赖版本。

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

`Choreographer.postFrameCallback` 时间间隔只能观察应用回调节奏，不等于屏幕真实呈现帧率；单次回调耗时也不包含全部 RenderThread/GPU/合成耗时。自注册循环回调时必须持有引用并在页面停止时 `removeFrameCallback`，否则会持续调度。

分析动画应分清 UI、渲染和合成阶段，并在 60/90/120 Hz、关闭动画、后台切换及取消交互时分别回归。依据：[属性动画官方指南](https://developer.android.com/develop/ui/views/animations/prop-animation)。

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
        List<Animator> snapshot = new ArrayList<>(animators);
        animators.clear(); // cancel/end 回调可能回入管理器，先清理原列表
        for (Animator animator : snapshot) {
            animator.cancel();
        }
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
