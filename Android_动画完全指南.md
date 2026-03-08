# Android 动画完全指南

_作者：OpenClaw_  
_日期：2026-03-08_

---

## 目录

1. [概述](#概述)
2. [View 动画 (Animation)](#view-动画-animation)
3. [属性动画 (Property Animation)](#属性动画-property-animation)
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
