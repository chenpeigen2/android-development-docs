# Android 自定义 View 绘制完全指南

> 源码版本：AOSP Android 17（API 37），`android-17.0.0_r1`。


> 作者：OpenClaw | 初稿日期：2026-03-08

---

## 目录

- [1. 概述](#1-概述)
- [2. Drawable 资源体系](#2-drawable-资源体系)
  - [2.1 Drawable 体系概述](#21-drawable-体系概述)
  - [2.2 ShapeDrawable 形状绘制](#22-shapedrawable-形状绘制)
    - [2.2.1 矩形 (Rectangle) - 最常用](#221-矩形-rectangle---最常用)
    - [2.2.2 渐变矩形](#222-渐变矩形)
    - [2.2.3 椭圆 (Oval)](#223-椭圆-oval)
    - [2.2.4 环形 (Ring)](#224-环形-ring)
  - [2.3 LayerListDrawable 层叠绘制](#23-layerlistdrawable-层叠绘制)
    - [2.3.1 卡片阴影效果](#231-卡片阴影效果)
  - [2.4 SelectorDrawable 状态选择器](#24-selectordrawable-状态选择器)
  - [2.5 VectorDrawable 矢量图形](#25-vectordrawable-矢量图形)
  - [2.6 Drawable 常用场景速查](#26-drawable-常用场景速查)
  - [2.7 代码中创建 Drawable](#27-代码中创建-drawable)
- [3. View 绘制三大流程](#3-view-绘制三大流程)
  - [3.1 流程概述](#31-流程概述)
  - [3.2 Measure 测量阶段](#32-measure-测量阶段)
    - [3.2.1 MeasureSpec 测量规格](#321-measurespec-测量规格)
    - [3.2.2 onMeasure 核心逻辑](#322-onmeasure-核心逻辑)
    - [3.2.3 获取 View 尺寸的正确方式](#323-获取-view-尺寸的正确方式)
    - [3.2.1 View.measure() 的外层协议](#321-viewmeasure-的外层协议)
    - [3.2.2 默认尺寸与 resolveSizeAndState](#322-默认尺寸与-resolvesizeandstate)
  - [3.3 Layout 布局阶段](#33-layout-布局阶段)
  - [3.4 Draw 绘制阶段](#34-draw-绘制阶段)
  - [3.5 实战：支持 margin 的纵向容器](#35-实战支持-margin-的纵向容器)
- [4. Canvas 画布详解](#4-canvas-画布详解)
  - [4.1 Canvas 核心功能](#41-canvas-核心功能)
  - [4.2 Canvas 基础绘制](#42-canvas-基础绘制)
  - [4.3 Canvas 变换操作](#43-canvas-变换操作)
  - [4.4 Canvas 裁剪操作](#44-canvas-裁剪操作)
  - [4.5 Path 高级绘制](#45-path-高级绘制)
- [5. Paint 画笔与效果](#5-paint-画笔与效果)
  - [5.1 Paint 核心属性](#51-paint-核心属性)
  - [5.2 Paint 高级效果](#52-paint-高级效果)
    - [5.2.1 阴影详解：setShadowLayer](#521-阴影详解setshadowlayer)
    - [5.2.2 BlurMaskFilter 模糊遮罩](#522-blurmaskfilter-模糊遮罩)
    - [5.2.3 View 的 elevation 和 translationZ](#523-view-的-elevation-和-translationz)
    - [5.2.4 阴影颜色设置](#524-阴影颜色设置)
  - [5.3 Xfermode 混合模式](#53-xfermode-混合模式)
  - [5.4 PathEffect 路径效果](#54-patheffect-路径效果)
- [6. 渐变与色彩](#6-渐变与色彩)
  - [6.1 渐变类型详解](#61-渐变类型详解)
  - [6.2 颜色工具](#62-颜色工具)
- [7. 自定义 View 实战](#7-自定义-view-实战)
  - [7.1 自定义属性](#71-自定义属性)
  - [7.2 完整示例：圆形进度条](#72-完整示例圆形进度条)
- [8. 性能优化](#8-性能优化)
  - [8.1 绘制优化原则](#81-绘制优化原则)
  - [8.2 最佳实践](#82-最佳实践)
- [9. LayoutInflater 流程](#9-layoutinflater-流程)
  - [9.1 Inflation 完整流程](#91-inflation-完整流程)
  - [9.2 inflate() 方法解析](#92-inflate-方法解析)
  - [9.3 注意事项](#93-注意事项)
- [10. Merge、Include 与 ViewStub](#10-mergeinclude-与-viewstub)
  - [10.1 \<merge\> 标签](#101--标签)
  - [10.2 \<include\> 标签](#102--标签)
  - [10.3 \<ViewStub\> 标签](#103--标签)
- [11. Invalidate 与 RequestLayout](#11-invalidate-与-requestlayout)
  - [11.1 invalidate：从本地脏标记传播到根](#111-invalidate从本地脏标记传播到根)
  - [11.2 requestLayout：尺寸依赖沿父链传播](#112-requestlayout尺寸依赖沿父链传播)
  - [11.3 两者对比与选择](#113-两者对比与选择)
  - [11.4 forceLayout：只标本节点，不向上排程](#114-forcelayout只标本节点不向上排程)
- [12. Draw 流程源码解析](#12-draw-流程源码解析)
  - [12.1 View.draw() 顺序](#121-viewdraw-顺序)
  - [12.2 ViewGroup.drawChild() 与硬件显示列表](#122-viewgroupdrawchild-与硬件显示列表)
  - [12.3 属性失效与内容重录的区别](#123-属性失效与内容重录的区别)
  - [12.4 DecorView 与子项绘制顺序](#124-decorview-与子项绘制顺序)
- [13. Canvas 高级用法](#13-canvas-高级用法)
  - [13.1 Canvas Save/Restore 详解](#131-canvas-saverestore-详解)
  - [13.2 Canvas saveLayer/RestoreToCount 详解](#132-canvas-savelayerrestoretocount-详解)
  - [13.3 Canvas 裁剪高级用法](#133-canvas-裁剪高级用法)
  - [13.4 混合模式 (PorterDuff) 详细解析](#134-混合模式-porterduff-详细解析)
- [14. View 与 ViewGroup 区别](#14-view-与-viewgroup-区别)
  - [14.1 核心区别](#141-核心区别)
  - [14.2 setWillNotDraw()](#142-setwillnotdraw)
  - [14.3 ViewGroup 绘制相关方法](#143-viewgroup-绘制相关方法)
- [15. 常见问题](#15-常见问题)
  - [15.1 wrap_content 不生效问题](#151-wrap_content-不生效问题)
    - [15.1.1 问题原因](#1511-问题原因)
    - [15.1.2 解决方案](#1512-解决方案)
  - [15.2 获取 View 宽高的正确时机](#152-获取-view-宽高的正确时机)
  - [16.1 为什么 onResume 中获取宽高返回 0](#161-为什么-onresume-中获取宽高返回-0)
  - [16.2 View.post() 原理详解](#162-viewpost-原理详解)
  - [16.3 其他获取宽高的正确方式](#163-其他获取宽高的正确方式)
- [16. 线程与 UI 更新](#16-线程与-ui-更新)
  - [16.1 子线程不能更新 UI 的原因](#161-子线程不能更新-ui-的原因)
  - [16.2 更新 UI 的正确方式](#162-更新-ui-的正确方式)
  - [16.3 特殊情况：SurfaceView](#163-特殊情况surfaceview)
  - [15.3 width/height 区别](#153-widthheight-区别)
  - [18.1 区别](#181-区别)
  - [18.2 MeasureSpec 不能与 LayoutParams 一对一等同](#182-measurespec-不能与-layoutparams-一对一等同)
  - [18.3 处理 wrap_content、padding 和最小尺寸](#183-处理-wrap_contentpadding-和最小尺寸)
- [19. 自定义属性详解](#19-自定义属性详解)
  - [19.1 属性声明](#191-属性声明)
  - [19.2 属性解析](#192-属性解析)
  - [19.3 属性优先级](#193-属性优先级)
  - [19.4 在 XML 中使用](#194-在-xml-中使用)
- [20. 事件处理与交互](#20-事件处理与交互)
  - [20.1 onTouchEvent](#201-ontouchevent)
  - [20.2 GestureDetector 手势处理](#202-gesturedetector-手势处理)
  - [20.3 滑动冲突解决](#203-滑动冲突解决)
  - [20.4 多点触控](#204-多点触控)
- [21. 实战案例](#21-实战案例)
  - [21.1 圆形进度条](#211-圆形进度条)
  - [21.2 组合标题栏](#212-组合标题栏)
  - [21.3 钢琴键盘（多点触控）](#213-钢琴键盘多点触控)
- [22. 完整知识体系总结](#22-完整知识体系总结)
- [总结](#总结)

---

## 1. 概述

自定义 View 是 Android 开发的核心技能之一。一个优秀的自定义 View 需要掌握以下知识体系：

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         自定义 View 知识体系                                 │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   自定义 View    │
                           └────────┬────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
    │   Drawable    │      │  绘制流程     │      │  图形变换     │
    │   资源体系    │      │ Measure/Layout/Draw │ (Canvas/Paint) │
    └───────────────┘      └───────────────┘      └───────────────┘
            │                       │                       │
            ▼                       ▼                       ▼
    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
    │ ShapeDrawable │      │ onMeasure()   │      │  渐变 Shader  │
    │ LayerList     │      │ onLayout()    │      │  混合 Xfermode│
    │ Selector      │      │ onDraw()      │      │  PathEffect   │
    │ VectorDrawable│      │                │      │               │
    └───────────────┘      └───────────────┘      └───────────────┘
```

---

## 2. Drawable 资源体系

### 2.1 Drawable 体系概述

Drawable 是 Android 中可绘制图形的抽象基类，用于描述可渲染的视觉元素。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Drawable 分类体系                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │  Drawable    │  (基类)
                        └──────┬───────┘
                               │
        ┌──────────┬───────────┼───────────┬──────────┐
        ▼          ▼           ▼           ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │ Color  │ │ Shape  │ │ Image  │ │ State  │ │ Layer  │
   │Drawable│ │Drawable│ │Drawable│ │  List  │ │  List  │
   └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

### 2.2 ShapeDrawable 形状绘制

#### 2.2.1 矩形 (Rectangle) - 最常用

```xml
<!-- res/drawable/bg_button.xml -->
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">

    <!-- 背景色 -->
    <solid android:color="#FFFFFF" />

    <!-- 边框 -->
    <stroke
        android:width="2dp"
        android:color="#E0E0E0"
        android:dashWidth="4dp"
        android:dashGap="2dp" />

    <!-- 圆角 -->
    <corners
        android:topLeftRadius="8dp"
        android:topRightRadius="8dp"
        android:bottomLeftRadius="0dp"
        android:bottomRightRadius="0dp" />

    <!-- 内边距 -->
    <padding
        android:left="16dp"
        android:top="8dp"
        android:right="16dp"
        android:bottom="8dp" />
</shape>
```

#### 2.2.2 渐变矩形

```xml
<shape android:shape="rectangle">
    <gradient
        android:startColor="#FF5722"
        android:endColor="#FFC107"
        android:centerColor="#FF9800"
        android:angle="45"
        android:type="linear" />
    <corners android:radius="16dp" />
</shape>
```

**渐变类型说明：**

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| linear | 线性渐变 | 按钮背景、卡片 |
| radial | 径向/放射渐变 | 圆形徽标、光晕效果 |
| sweep | 扫描/旋转渐变 | 加载动画 |

#### 2.2.3 椭圆 (Oval)

```xml
<shape android:shape="oval">
    <solid android:color="#2196F3" />
    <size android:width="100dp" android:height="100dp" />
</shape>
```

#### 2.2.4 环形 (Ring)

```xml
<shape android:shape="ring"
    android:innerRadius="20dp"
    android:thickness="8dp"
    android:useLevel="false">
    <solid android:color="#4CAF50" />
</shape>
```

### 2.3 LayerListDrawable 层叠绘制

#### 2.3.1 卡片阴影效果

```xml
<!-- res/drawable/bg_card_shadow.xml -->
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- 阴影层 -->
    <item android:bottom="0dp" android:left="2dp" android:right="0dp" android:top="2dp">
        <shape android:shape="rectangle">
            <solid android:color="#20000000" />
            <corners android:radius="12dp" />
        </shape>
    </item>
    <!-- 主体层 -->
    <item android:bottom="2dp" android:left="0dp" android:right="2dp" android:top="0dp">
        <shape android:shape="rectangle">
            <solid android:color="#FFFFFF" />
            <corners android:radius="12dp" />
        </shape>
    </item>
</layer-list>
```

### 2.4 SelectorDrawable 状态选择器

```xml
<!-- res/drawable/selector_button.xml -->
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- 按下状态 -->
    <item android:state_pressed="true">
        <shape android:shape="rectangle">
            <solid android:color="#E3F2FD" />
            <corners android:radius="8dp" />
        </shape>
    </item>
    <!-- 默认状态 - 放最后 -->
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#FFFFFF" />
            <corners android:radius="8dp" />
            <stroke android:width="1dp" android:color="#E0E0E0" />
        </shape>
    </item>
</selector>
```

**常用状态属性：**

| 状态 | 说明 |
|------|------|
| android:state_pressed | 按下 |
| android:state_focused | 获得焦点 |
| android:state_selected | 选中 |
| android:state_checked | 勾选 |

**⚠️ 重要：状态顺序很重要！具体状态在前，通配状态在后。**

### 2.5 VectorDrawable 矢量图形

```xml
<!-- res/drawable/ic_arrow.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FF000000"
        android:pathData="M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10 10,-4.48 10,-10S17.52,2 12,2z" />
</vector>
```

**pathData 命令说明：**

| 命令 | 说明 | 示例 |
|------|------|------|
| M/m | 移动到 | M 10 10 |
| L/l | 直线 | L 20 20 |
| C/c | 三次贝塞尔曲线 | C 10 10, 20 20, 30 10 |
| Q/q | 二次贝塞尔曲线 | Q 20 20, 30 10 |
| Z/z | 闭合路径 | Z |

### 2.6 Drawable 常用场景速查

| 场景 | 推荐 Drawable |
|------|---------------|
| 按钮背景 | shape (rectangle) + selector |
| 卡片阴影 | layer-list |
| 分割线 | shape (line) |
| 图标 | vector drawable |
| 圆形头像 | shape (oval) |
| 渐变背景 | gradient drawable |

### 2.7 代码中创建 Drawable

```kotlin
// 动态创建渐变背景
fun createGradientBackground(): Drawable {
    val gradientDrawable = GradientDrawable().apply {
        shape = GradientDrawable.RECTANGLE
        gradientType = GradientDrawable.LINEAR_GRADIENT
        orientation = GradientDrawable.TOP_TO_BOTTOM
        setColor(Color.parseColor("#FF5722"))
        setStroke(2, Color.parseColor("#E0E0E0"))
        cornerRadius = 16f
    }
    return gradientDrawable
}
```

---

## 3. View 绘制三大流程

### 3.1 流程概述

View 的渲染分为三个核心阶段：Measure(测量) → Layout(布局) → Draw(绘制)。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 渲染三大流程                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐    ┌──────────┐    ┌──────────┐
│  Measure │ -> │  Layout  | -> │   Draw   │
│  测量    │    │  布局    │    │  绘制    │
└──────────┘    └──────────┘    └──────────┘
     │               │               │
     ▼               ▼               ▼
onMeasure()    onLayout()     onDraw()
     │               │               │
     ▼               ▼               ▼
确定宽高          确定位置        绘制内容
```

**触发场景：**

| 方法 | 触发流程 |
|------|----------|
| requestLayout() | 请求布局遍历；重测和重画取决于标志及尺寸 |
| invalidate() | 标记内容失效，安排后续绘制，不同步重画 |
| requestFocus() | 请求焦点；不是通用绘制调度 API |

### 3.2 Measure 测量阶段

#### 3.2.1 MeasureSpec 测量规格

`MeasureSpec` 的 mode 在高两位，size 在低 30 位；不能自定义一个 `EXACTLY=1`、`AT_MOST=2` 的同名对象代替 SDK 类型。

```kotlin
val spec = View.MeasureSpec.makeMeasureSpec(300, View.MeasureSpec.AT_MOST)
val mode = View.MeasureSpec.getMode(spec)
val maxWidthPx = View.MeasureSpec.getSize(spec)
```

| 子 View LayoutParams | 父 EXACTLY（扣除 padding/margin 后） | 父 AT_MOST |
|---|---|---|
| 固定非负 px | EXACTLY，指定尺寸 | EXACTLY，指定尺寸 |
| `MATCH_PARENT` | EXACTLY，可用尺寸 | AT_MOST，可用尺寸 |
| `WRAP_CONTENT` | AT_MOST，可用尺寸 | AT_MOST，可用尺寸 |

父 UNSPECIFIED 的 size 还有兼容分支，不能把 `wrap_content` 永远等同于 AT_MOST。约束来自父容器生成的 spec；自定义测量还需考虑 padding、suggestedMinimumWidth/Height 和测量状态。依据：[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)（`MeasureSpec`、`resolveSizeAndState`）、[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)（`getChildMeasureSpec`）。

#### 3.2.2 onMeasure 核心逻辑

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {
    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val contentPx = (200f * resources.displayMetrics.density).toInt()
        val desiredWidth = maxOf(suggestedMinimumWidth, contentPx + paddingLeft + paddingRight)
        val desiredHeight = maxOf(suggestedMinimumHeight, contentPx + paddingTop + paddingBottom)
        setMeasuredDimension(
            resolveSizeAndState(desiredWidth, widthMeasureSpec, 0),
            resolveSizeAndState(desiredHeight, heightMeasureSpec, 0)
        )
    }
}
```

这是普通 View 示例。自定义 ViewGroup 还应测量子 View、处理 margin，并通过 `combineMeasuredStates` 汇总子项测量状态。

#### 3.2.3 获取 View 尺寸的正确方式

```kotlin
// ❌ 错误：在构造函数中获取尺寸
class MyView(context: Context) : View(context) {
    init {
        val w = width  // 0
    }
}

// ✅ 正确：在 onSizeChanged 中获取
override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
    super.onSizeChanged(w, h, oldw, oldh)
}

// 等待布局使用 AndroidX Core doOnLayout，不把任意 post 当作布局完成保证
view.doOnLayout { laidOutView -> val w = laidOutView.width }
```

#### 3.2.1 View.measure() 的外层协议

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

#### 3.2.2 默认尺寸与 resolveSizeAndState

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


### 3.3 Layout 布局阶段

```kotlin
override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
    var childTop = paddingTop
    val availableWidth = width - paddingLeft - paddingRight

    for (i in 0 until childCount) {
        val child = getChildAt(i)
        if (child.visibility != GONE) {
            val childWidth = child.measuredWidth
            val childHeight = child.measuredHeight

            val childLeft = paddingLeft + (availableWidth - childWidth) / 2
            val childRight = childLeft + childWidth
            val childBottom = childTop + childHeight

            child.layout(childLeft, childTop, childRight, childBottom)
            childTop += childHeight
        }
    }
}
```

### 3.4 Draw 绘制阶段

不要在自定义 `draw()` 内手动调用私有 `drawBackground()`，或重复分发整个框架流程。通常只重写内容回调：

```kotlin
class ContentView(context: Context) : View(context) {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.BLUE }
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawCircle(width / 2f, height / 2f, minOf(width, height) / 4f, paint)
    }
}
```

背景、子项、Overlay、前景和焦点高亮由框架组织，见第 12 节。依据：[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)。

### 3.5 实战：支持 margin 的纵向容器

下面容器按添加顺序纵向放置非 GONE 子项，处理 padding、margin、最小尺寸和测量状态；不实现 weight、gravity、RTL start/end gravity 或滚动。INVISIBLE 子项仍保留空间。例子使用 ViewGroup 标准测量 API，而不是在 onLayout 中调用 measure。

```kotlin
class MarginColumn @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : ViewGroup(context, attrs) {
    override fun generateDefaultLayoutParams(): LayoutParams =
        MarginLayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT)

    override fun generateLayoutParams(attrs: AttributeSet): LayoutParams =
        MarginLayoutParams(context, attrs)

    override fun generateLayoutParams(source: LayoutParams): LayoutParams =
        if (source is MarginLayoutParams) MarginLayoutParams(source)
        else MarginLayoutParams(source)

    override fun checkLayoutParams(params: LayoutParams): Boolean =
        params is MarginLayoutParams

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        var usedHeight = 0
        var widestChild = 0
        var childState = 0
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue
            val lp = child.layoutParams as MarginLayoutParams
            measureChildWithMargins(child, widthMeasureSpec, 0,
                heightMeasureSpec, usedHeight)
            widestChild = maxOf(widestChild,
                child.measuredWidth + lp.leftMargin + lp.rightMargin)
            usedHeight += child.measuredHeight + lp.topMargin + lp.bottomMargin
            childState = combineMeasuredStates(childState, child.measuredState)
        }
        setMeasuredDimension(
            resolveSizeAndState(maxOf(suggestedMinimumWidth,
                widestChild + paddingLeft + paddingRight), widthMeasureSpec, childState),
            resolveSizeAndState(maxOf(suggestedMinimumHeight,
                usedHeight + paddingTop + paddingBottom), heightMeasureSpec,
                childState shl MEASURED_HEIGHT_STATE_SHIFT)
        )

        // 父宽不是 EXACTLY 时，MATCH_PARENT 子项第一轮可能只得到 AT_MOST。
        // 根容器宽度确定后再统一其宽；保留第一轮测得的子项高度。
        if (MeasureSpec.getMode(widthMeasureSpec) != MeasureSpec.EXACTLY) {
            for (i in 0 until childCount) {
                val child = getChildAt(i)
                if (child.visibility == GONE) continue
                val lp = child.layoutParams as MarginLayoutParams
                if (lp.width == LayoutParams.MATCH_PARENT) {
                    val width = (measuredWidth - paddingLeft - paddingRight -
                        lp.leftMargin - lp.rightMargin).coerceAtLeast(0)
                    child.measure(MeasureSpec.makeMeasureSpec(width, MeasureSpec.EXACTLY),
                        MeasureSpec.makeMeasureSpec(child.measuredHeight, MeasureSpec.EXACTLY))
                }
            }
        }
    }

    override fun onLayout(changed: Boolean, left: Int, top: Int, right: Int, bottom: Int) {
        var y = paddingTop
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child.visibility == GONE) continue
            val lp = child.layoutParams as MarginLayoutParams
            y += lp.topMargin
            val x = paddingLeft + lp.leftMargin
            child.layout(x, y, x + child.measuredWidth, y + child.measuredHeight)
            y += child.measuredHeight + lp.bottomMargin
        }
    }
}
```

heightUsed 只包含已经测过的子项及其 margin，measureChildWithMargins 自己会扣父 padding，不能重复扣除。布局传入的 child 坐标相对当前容器，不能再加父的 left/top。父约束不足时容器仍服从 EXACTLY/AT_MOST；它不是滚动容器，不会自动让超出内容可滚动。

二次统一宽保留第一轮高度，适合固定内容/常规纵向布局；若业务需要宽变化后重新排版并重新计算整列高度，应增加完整二次测量策略，或使用 LinearLayout/ConstraintLayout。此处明确示例能力边界，不声称是通用 LinearLayout 替代。源码依据：[AOSP 17 ViewGroup.measureChildWithMargins / getChildMeasureSpec](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)。

## 4. Canvas 画布详解

### 4.1 Canvas 核心功能

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Canvas API 分类                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┬─────────────────────────────────────────┐
│         形状绘制                 │           变换操作                      │
├─────────────────────────────────┼─────────────────────────────────────────┤
│ drawArc()      绘制弧形         │ save()/restore()     状态保存/恢复      │
│ drawBitmap()   绘制位图         │ translate()          平移               │
│ drawCircle()   绘制圆形         │ rotate()             旋转               │
│ drawLine()     绘制直线         │ scale()              缩放               │
│ drawOval()     绘制椭圆         │ skew()               倾斜               │
│ drawPath()     绘制路径         │ concat()             矩阵连接           │
│ drawPoint()    绘制点           │                      │
│ drawRect()     绘制矩形         │           裁剪操作                      │
│ drawRoundRect()绘制圆角矩形     ├─────────────────────────────────────────┤
│ drawText()     绘制文本         │ clipPath()           路径裁剪           │
│                                 │ clipRect()           矩形裁剪           │
└─────────────────────────────────┴─────────────────────────────────────────┘
```

### 4.2 Canvas 基础绘制

```kotlin
class CanvasBasicView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.RED
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // 绘制圆形
        canvas.drawCircle(100f, 100f, 50f, paint)

        // 绘制矩形
        canvas.drawRect(200f, 50f, 350f, 150f, paint)

        // 绘制圆角矩形
        val rect = RectF(400f, 50f, 500f, 150f)
        canvas.drawRoundRect(rect, 16f, 16f, paint)

        // 绘制椭圆
        val oval = RectF(550f, 50f, 650f, 120f)
        canvas.drawOval(oval, paint)

        // 绘制直线
        canvas.drawLine(50f, 200f, 200f, 200f, paint.apply { strokeWidth = 4f })

        // 绘制弧形
        val arcRect = RectF(350f, 170f, 450f, 270f)
        canvas.drawArc(arcRect, 0f, 90f, false, paint)
    }
}
```

### 4.3 Canvas 变换操作

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // 1. 平移
    canvas.save()
    canvas.translate(100f, 0f)
    canvas.drawCircle(50f, 50f, 40f, paint)
    canvas.restore()

    // 2. 旋转
    canvas.save()
    canvas.rotate(45f, 100f, 100f)
    canvas.drawRect(50f, 50f, 150f, 150f, paint)
    canvas.restore()

    // 3. 缩放
    canvas.save()
    canvas.scale(1.5f, 1.5f, 100f, 100f)
    canvas.drawCircle(100f, 100f, 40f, paint)
    canvas.restore()

    // 4. 倾斜
    canvas.save()
    canvas.skew(0.5f, 0f)
    canvas.drawRect(200f, 50f, 300f, 150f, paint)
    canvas.restore()
}
```

### 4.4 Canvas 裁剪操作

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // 裁剪矩形
    canvas.save()
    canvas.clipRect(50f, 50f, 200f, 200f)
    canvas.drawColor(Color.RED)
    canvas.restore()

    // 裁剪路径
    canvas.save()
    val path = Path().apply {
        addCircle(350f, 125f, 75f, Path.Direction.CW)
    }
    canvas.clipPath(path)
    canvas.drawColor(Color.BLUE)
    canvas.restore()
}
```

### 4.5 Path 高级绘制

```kotlin
private val path = Path()

override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // 基础 Path
    path.reset()
    path.moveTo(50f, 200f)
    path.lineTo(100f, 100f)
    path.lineTo(150f, 200f)
    path.lineTo(200f, 100f)
    path.close()
    canvas.drawPath(path, paint)

    // 二次贝塞尔曲线
    path.reset()
    path.moveTo(250f, 200f)
    path.quadTo(300f, 50f, 350f, 200f)
    canvas.drawPath(path, paint)

    // 三次贝塞尔曲线
    path.reset()
    path.moveTo(400f, 200f)
    path.cubicTo(420f, 50f, 480f, 50f, 500f, 200f)
    canvas.drawPath(path, paint)

    // 组合 Path (挖空效果)
    path.reset()
    path.addCircle(600f, 150f, 50f, Path.Direction.CW)
    path.addCircle(640f, 150f, 30f, Path.Direction.CCW)
    canvas.drawPath(path, fillPaint)
}
```

---

## 5. Paint 画笔与效果

### 5.1 Paint 核心属性

```kotlin
/**
 * Paint 主要属性
 *
 * Style (样式): FILL / STROKE / FILL_AND_STROKE
 * Cap (端点): BUTT / ROUND / SQUARE
 * Join (拐角): MITER / ROUND / BEVEL
 */
val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
    // 基础样式
    style = Paint.Style.FILL
    color = Color.RED

    // 抗锯齿
    isAntiAlias = true

    // 描边属性
    strokeWidth = 4f
    strokeCap = Paint.Cap.ROUND
    strokeJoin = Paint.Join.ROUND

    // 文本属性
    textSize = 48f
    typeface = Typeface.DEFAULT
}
```

### 5.2 Paint 高级效果

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // 1. 阴影效果
    val shadowPaint = Paint(basePaint).apply {
        setShadowLayer(8f, 4f, 4f, Color.parseColor("#40000000"))
    }
    setLayerType(LAYER_TYPE_SOFTWARE, null)
    canvas.drawCircle(80f, 80f, 50f, shadowPaint)

    // 2. 渐变填充
    val gradient = LinearGradient(
        200f, 50f, 300f, 150f,
        Color.parseColor("#FF5722"),
        Color.parseColor("#FFC107"),
        Shader.TileMode.CLAMP
    )
    basePaint.shader = gradient
    canvas.drawCircle(250f, 100f, 50f, basePaint)

    // 3. 颜色过滤器 - 变灰
    val grayPaint = Paint(basePaint).apply {
        colorFilter = ColorMatrixColorFilter(ColorMatrix().apply { setSaturation(0f) })
    }
    canvas.drawCircle(80f, 220f, 50f, grayPaint)

    // 4. 亮度提升
    val brightPaint = Paint(basePaint).apply {
        colorFilter = ColorMatrixColorFilter(ColorMatrix(floatArrayOf(
            1.5f, 0f, 0f, 0f, 50f,
            0f, 1.5f, 0f, 0f, 50f,
            0f, 0f, 1.5f, 0f, 50f,
            0f, 0f, 0f, 1f, 0f
        )))
    }
    canvas.drawCircle(200f, 220f, 50f, brightPaint)
}
```

#### 5.2.1 阴影详解：setShadowLayer




```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Paint.setShadowLayer() 详解                              │
└─────────────────────────────────────────────────────────────────────────────┘

  方法签名：
  ─────────────────────────────────────────────────────────────────────────────
  public void setShadowLayer(float radius, float dx, float dy, int shadowColor)

  参数说明：
  - radius: 阴影模糊半径（越大越模糊）
  - dx: 阴影水平偏移
  - dy: 阴影垂直偏移
  - shadowColor: 阴影颜色（通常带透明度）

  关键点：
  ─────────────────────────────────────────────────────────────────────────────

  1. 按 API 和操作区分支持范围
     ─────────────────────────────────────────────────────────────────────────
     // 官方表：非文字 setShadowLayer 自 API 28 支持硬件加速
     // 不能为 Android 17 的所有阴影无条件关闭窗口硬件加速

  2. 阴影颜色建议使用带透明度的颜色
     ─────────────────────────────────────────────────────────────────────────
     Color.parseColor("#40000000")  // 25% 黑色
     Color.parseColor("#80FF0000")  // 50% 红色

  3. 性能问题
     ─────────────────────────────────────────────────────────────────────────
     - 软件渲染，每个 View 都会离屏渲染
     - 避免在大量 View 上使用
     - 优先考虑 elevation（硬件加速）

  4. 与 elevation 的区别
     ─────────────────────────────────────────────────────────────────────────
     ┌─────────────────┬────────────────────┬─────────────────────┐
     │                 │ setShadowLayer      │ elevation          │
     ├─────────────────┼────────────────────┼─────────────────────┤
     │ 硬件加速        │ 需要关闭             │ 支持               │
     │ 性能            │ 较差                 │ 好                 │
     │ 模糊半径        │ 可自定义             │ 系统设定           │
     │ 颜色            │ 可自定义             │ 黑色               │
     │ 兼容性          │ API 21+             │ API 21+            │
     └─────────────────┴────────────────────┴─────────────────────┘
```

#### 5.2.2 BlurMaskFilter 模糊遮罩

BlurMaskFilter 作用于 alpha 遮罩，不是 setShadowLayer 的更强版本。官方表将 Paint.setMaskFilter() 列为硬件渲染不支持；原文声称不需要软件路径的注释已纠正。

| 类型 | 效果 |
|---|---|
| NORMAL | 内外模糊 |
| SOLID | 内部保留，外部模糊 |
| OUTER | 仅外侧模糊 |
| INNER | 仅内部模糊 |

```kotlin
// 仅示范软件 Canvas / 经验证的软件层路径。
val blurPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
    color = Color.BLUE
    maskFilter = BlurMaskFilter(20f, BlurMaskFilter.Blur.NORMAL)
}
canvas.drawCircle(200f, 300f, 80f, blurPaint)
```

只对确有需要的控件评估软件层，不关闭整个应用硬件加速。shadowLayer 与 maskFilter 后设置者覆盖前设置者并不是可依赖的通用契约，原断言已删除，组合效果需按后端验证。依据：[官方硬件加速表](https://developer.android.com/develop/ui/views/graphics/hardware-accel)。

#### 5.2.3 View 的 elevation 和 translationZ

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    View 阴影：elevation vs translationZ                    │
└─────────────────────────────────────────────────────────────────────────────┘

  两者都是 Material Design 中的阴影实现方式，硬件加速支持

  ────────────────────────────────────────────────────────────────────────────

  1. elevation（海拔）
     ───────────────────────────────────────────────────────────────────────
     // XML 中
     android:elevation="8dp"

     // 代码中
     view.elevation = 8f * resources.displayMetrics.density

     特点：
     - 静态设定，创建后不变
     - 硬件加速，性能好
     - 自动产生阴影效果
     - 在 ViewOutlineProvider 中可自定义阴影形状

  2. translationZ
     ───────────────────────────────────────────────────────────────────────
     // 代码中
     view.translationZ = 20f

     特点：
     - 动态设定，可随动画变化
     - 临时提升 View 层级
     - 动画结束后应恢复为 0
     - 常用于点击反馈、拖拽提升

  3. 两者叠加
     ───────────────────────────────────────────────────────────────────────
     // 实际 Z = elevation + translationZ
     view.elevation = 4f
     view.translationZ = 8f  // 动画中临时提升
     // 当前 Z = 12

  4. 自定义阴影形状
     ───────────────────────────────────────────────────────────────────────

     // 方式一：OutlineProvider
     view.outlineProvider = object : ViewOutlineProvider() {
         override fun getOutline(view: View, outline: Outline) {
             // 圆形阴影
             outline.setOval(0, 0, view.width, view.height)

             // 或者圆角矩形
             outline.setRoundRect(0, 0, view.width, view.height, 20f)
         }
     }

     // 方式二：clipToOutline
     view.clipToOutline = true

  5. 注意事项
     ───────────────────────────────────────────────────────────────────────
     - elevation 和 translationZ 只影响视觉（绘制）
     - 不影响事件分发（事件只按 mChildren 数组顺序）
     - translationZ 动画结束后必须恢复为 0，否则影响后续事件分发

  6. 性能对比
     ───────────────────────────────────────────────────────────────────────
     ┌─────────────────────┬────────────────┬────────────────┐
     │                     │ 性能           │ 硬件加速       │
     ├─────────────────────┼────────────────┼────────────────┤
     │ setShadowLayer      │ 较差           │ 需关闭         │
     │ BlurMaskFilter      │ 中等           │ 支持           │
     │ elevation           │ 好             │ 自动           │
     │ translationZ        │ 好             │ 自动           │
     └─────────────────────┴────────────────┴────────────────┘
```

#### 5.2.4 阴影颜色设置

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    elevation 阴影颜色设置                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  使用 outlineAmbientShadowColor 和 outlineSpotShadowColor 设置阴影颜色

  代码示例：
  ─────────────────────────────────────────────────────────────────────────────

  // 设置环境光阴影颜色
  view.outlineAmbientShadowColor = Color.RED

  // 设置投影阴影颜色
  view.outlineSpotShadowColor = Color.RED

  // 同时设置
  view.outlineAmbientShadowColor = Color.parseColor("#FF5722")
  view.outlineSpotShadowColor = Color.parseColor("#FF5722")

  效果：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  默认阴影（黑色）              自定义阴影（红色）                        │
  │                                                                         │
  │       ████                      ████                                   │
  │     ██      ██                ██      ██                              │
  │   ██          ██            ██          ██                            │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  区别：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────┬─────────────────────────────────────────────────┐
  │ 属性                 │ 说明                                           │
  ├─────────────────────┼─────────────────────────────────────────────────┤
  │ outlineAmbientShadowColor │ 环境光阴影（四周均匀）                      │
  │ outlineSpotShadowColor   │ 点光源投影阴影（有方向性）                 │
  └─────────────────────┴─────────────────────────────────────────────────┘

  注意事项：
  ─────────────────────────────────────────────────────────────────────────────

  1. 只对 elevation 产生的阴影有效
  2. 不需要关闭硬件加速
  3. Material Design 建议阴影颜色为黑色或主色调的暗色
  4. API 21+ 支持

  ────────────────────────────────────────────────────────────────────────────

  现代阴影方案推荐：
  ─────────────────────────────────────────────────────────────────────────────

  1. elevation（最简单）
     android:elevation="8dp"

  2. MaterialShapeDrawable（推荐）
     MaterialShapeDrawable().apply {
         cornerSize = 16f
         setShadowColor(Color.parseColor("#40000000"))
     }

  3. CardView
     <CardView
         app:cardCornerRadius="16dp"
         app:cardElevation="4dp" />

  4. 自定义颜色阴影
     view.elevation = 8f
     view.outlineSpotShadowColor = Color.parseColor("#40000000")
```

### 5.3 Xfermode 混合模式

```kotlin
/**
 * PorterDuff 混合模式速查
 *
 * 常用组合:
 * - 圆形头像: DST_IN + 圆形 Bitmap
 * - 圆角图片: DST_IN + 圆角矩形
 * - 指纹擦除: CLEAR
 */

// 圆形图片示例
fun createCircularBitmap(src: Bitmap): Bitmap {
    val output = Bitmap.createBitmap(src.width, src.height, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(output)

    val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    canvas.drawCircle(src.width / 2f, src.height / 2f, src.width / 2f, paint)

    paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.SRC_IN)
    canvas.drawBitmap(src, 0f, 0f, paint)

    return output
}
```

### 5.4 PathEffect 路径效果

```kotlin
val pathPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
    style = Paint.Style.STROKE
    strokeWidth = 6f
}

val path = Path().apply { moveTo(50f, 50f); lineTo(150f, 150f) }

// 虚线
pathPaint.pathEffect = DashPathEffect(floatArrayOf(20f, 10f), 0f)
canvas.drawPath(path, pathPaint)

// 圆角虚线
pathPaint.pathEffect = CornerPathEffect(20f)

// 组合效果
pathPaint.pathEffect = ComposePathEffect(
    DashPathEffect(floatArrayOf(20f, 10f), 0f),
    CornerPathEffect(15f)
)
```

---

## 6. 渐变与色彩

### 6.1 渐变类型详解

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // 1. 线性渐变
    val linearGradient = LinearGradient(
        0f, 0f, width.toFloat(), height.toFloat(),
        intArrayOf(
            Color.parseColor("#FF5722"),
            Color.parseColor("#FFC107"),
            Color.parseColor("#4CAF50")
        ),
        floatArrayOf(0f, 0.5f, 1f),
        Shader.TileMode.CLAMP
    )

    val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply { shader = linearGradient }
    canvas.drawRect(0f, 0f, 300f, 200f, paint)

    // 2. 径向渐变
    val radialGradient = RadialGradient(
        150f, 300f, 100f,
        Color.parseColor("#FF5722"),
        Color.parseColor("#4CAF50"),
        Shader.TileMode.CLAMP
    )
    paint.shader = radialGradient
    canvas.drawCircle(150f, 300f, 100f, paint)

    // 3. 扫描渐变
    val sweepGradient = SweepGradient(
        450f, 150f,
        intArrayOf(
            Color.parseColor("#FF5722"),
            Color.parseColor("#FFC107"),
            Color.parseColor("#4CAF50"),
            Color.parseColor("#FF5722")
        ),
        null
    )
    paint.shader = sweepGradient
    canvas.drawCircle(450f, 150f, 100f, paint)
}
```

### 6.2 颜色工具

```kotlin
object ColorUtils {

    fun darken(color: Int, factor: Float = 0.8f): Int {
        val a = Color.alpha(color)
        val r = (Color.red(color) * factor).toInt()
        val g = (Color.green(color) * factor).toInt()
        val b = (Color.blue(color) * factor).toInt()
        return Color.argb(a, r.coerceIn(0, 255), g.coerceIn(0, 255), b.coerceIn(0, 255))
    }

    fun lighten(color: Int, factor: Float = 0.2f): Int {
        return Color.argb(
            Color.alpha(color),
            (Color.red(color) + (255 - Color.red(color)) * factor).toInt(),
            (Color.green(color) + (255 - Color.green(color)) * factor).toInt(),
            (Color.blue(color) + (255 - Color.blue(color)) * factor).toInt()
        )
    }

    fun withAlpha(color: Int, alpha: Int): Int {
        return Color.argb(alpha, Color.red(color), Color.green(color), Color.blue(color))
    }
}
```

---

## 7. 自定义 View 实战

### 7.1 自定义属性

```xml
<!-- res/values/attrs.xml -->
<declare-styleable name="CustomView">
    <attr name="cv_color" format="color" />
    <attr name="cv_size" format="dimension" />
    <attr name="cv_text" format="string" />
</declare-styleable>
```

### 7.2 完整示例：圆形进度条

```kotlin
class CircleProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress: Float = 0f
    private var maxProgress: Float = 100f
    private var progressColor: Int = Color.parseColor("#2196F3")
    private var backgroundColor: Int = Color.parseColor("#E0E0E0")
    private var strokeWidth: Float = 20f.dp2px()

    private val backgroundPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
    }

    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
    }

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textAlign = Paint.Align.CENTER
    }

    init {
        // 读取自定义属性
        context.obtainStyledAttributes(attrs, R.styleable.CircleProgressView).apply {
            try {
                progressColor = getColor(R.styleable.CircleProgressView_cv_color, progressColor)
                strokeWidth = getDimension(R.styleable.CircleProgressView_cv_size, strokeWidth)
            } finally {
                recycle()
            }
        }

        backgroundPaint.color = backgroundColor
        backgroundPaint.strokeWidth = strokeWidth
        progressPaint.color = progressColor
        progressPaint.strokeWidth = strokeWidth
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        textPaint.textSize = minOf(w, h) / 4f
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val centerX = width / 2f
        val centerY = height / 2f
        val radius = minOf(centerX, centerY) - strokeWidth / 2

        // 绘制背景圆
        canvas.drawCircle(centerX, centerY, radius, backgroundPaint)

        // 绘制进度
        val sweepAngle = (progress / maxProgress) * 360f
        canvas.drawArc(
            RectF(
                centerX - radius,
                centerY - radius,
                centerX + radius,
                centerY + radius
            ),
            -90f,
            sweepAngle,
            false,
            progressPaint
        )

        // 绘制文字
        val percent = (progress / maxProgress * 100).toInt()
        canvas.drawText(
            "$percent%",
            centerX,
            centerY + textPaint.textSize / 3,
            textPaint
        )
    }

    fun setProgress(value: Float) {
        progress = value.coerceIn(0f, maxProgress)
        invalidate()
    }

    private fun Float.dp2px(): Float = this * resources.displayMetrics.density
}
```

---

## 8. 性能优化

**硬件层不等于开启硬件加速**：`LAYER_TYPE_HARDWARE` 只在已硬件加速的 View 树中提供离屏层缓存，不能把软件窗口切换为硬件窗口。缓存适合内容稳定、仅变换属性的场景；频繁改变内容则可能反复重建并增加显存开销。用 `Canvas.isHardwareAccelerated` 判断当前画布，不能只看 View 标志。`save()` 保存矩阵/裁剪；`saveLayer()` 才涉及离屏合成成本。依据：[官方硬件加速指南](https://developer.android.com/develop/ui/views/graphics/hardware-accel)。


### 8.1 绘制优化原则

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         绘制优化原则                                         │
└─────────────────────────────────────────────────────────────────────────────┘

1. 减少 onDraw 中的对象创建
   - 预创建 Paint、Path 等对象
   - 避免在 onDraw 中 new 对象

2. 使用硬件加速
   - 开启硬件加速提升绘制性能
   - 注意兼容性问题

3. 避免过度绘制
   - 使用 clipRect 限制绘制区域
   - 合理使用 View 背景

4. 优化动画
   - 仅在内容稳定且测量证明收益时使用临时硬件层 (setLayerType)
   - 使用 ValueAnimator 替代 ObjectAnimator
   - 开启硬件加速

5. 缓存策略
   - 使用 Bitmap 缓存复杂图形
   - 考虑 Canvas.saveLayer() 缓存
```

### 8.2 最佳实践

```kotlin
// ✅ 正确：预创建对象
class OptimizedView(context: Context) : View(context) {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
    }

    override fun onDraw(canvas: Canvas) {
        // 复用 paint，不要 new
        canvas.drawCircle(100f, 100f, 50f, paint)
    }
}

// ❌ 错误：每次绘制创建对象
override fun onDraw(canvas: Canvas) {
    val paint = Paint() // 每次都创建，GC 压力大
    canvas.drawCircle(100f, 100f, 50f, paint)
}
```

---

## 9. LayoutInflater 流程

### 9.1 Inflation 完整流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LayoutInflater 流程                                 │
└─────────────────────────────────────────────────────────────────────────────┘

setContentView(R.layout.xxx)
       │
       ▼
LayoutInflater.from(context).inflate()
       │
       ▼
inflate(XmlPullParser, ViewGroup, boolean)
       │
       ├─► createViewFromTag()  创建 View
       │       │
       │       ▼
       │   Factory.onCreateView() / onCreateView()
       │       │
       │       ▼
       │   View 对象创建
       │
       └─► rInflateChildren()  递归解析子 View
               │
               ▼
           完整 View 树构建
```

### 9.2 inflate() 方法解析

```kotlin
// LayoutInflater.inflate() 重载方法
public View inflate(int resource, ViewGroup root, boolean attachToRoot)

// resource: 布局资源 ID
// root: 父 ViewGroup
// attachToRoot: 是否添加到 root

// 场景1: root != null, attachToRoot = true
// 布局的根 View 会被添加到 root 中，并返回 root
val view = inflater.inflate(R.layout.xxx, parent, true)
// 等价于: parent.addView(inflater.inflate(R.layout.xxx, parent, false))

// 场景2: root != null, attachToRoot = false
// 只解析布局，不添加到 root，返回解析出的根 View
val view = inflater.inflate(R.layout.xxx, parent, false)
// 常用于 RecyclerView ViewHolder

// 场景3: root == null
// 忽略布局中的 layout_xxx 属性，返回解析出的根 View
val view = inflater.inflate(R.layout.xxx, null, false)
```

### 9.3 注意事项

```kotlin
// ❌ 错误：root 为 null，丢失布局参数
val view = inflater.inflate(R.layout.xxx, null)
view.layoutParams = null // 宽高参数丢失

// ✅ 正确：传入正确的 parent
val view = inflater.inflate(R.layout.xxx, parent, false)

// ✅ 正确：attachToRoot = true
val view = inflater.inflate(R.layout.xxx, parent, true)
```

---

## 10. Merge、Include 与 ViewStub

### 10.1 \<merge\> 标签

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         \<merge\> 标签                                      │
└─────────────────────────────────────────────────────────────────────────────┘

merge 标签用于减少布局层级，将子 View 直接添加到目标父容器中。

使用场景：
- 根布局是 FrameLayout/RelativeLayout 且会被 include 替换时
- 避免多余的父容器层级
```

```xml
<!-- layout_header.xml -->
<!-- 注意：merge 必须是根元素 -->
<merge xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">

    <ImageView
        android:layout_width="48dp"
        android:layout_height="48dp"
        android:src="@drawable/ic_logo" />

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Title" />

</merge>
```

```kotlin
// 解析后，子 View 会直接添加到父容器中
// 不再创建 merge 节点作为父容器
```

**注意事项：**

```kotlin
/**
 * merge 使用限制：
 *
 * 1. 必须是布局文件的根元素
 * 2. 父容器类型必须匹配
 *    - <merge> 父容器必须是 FrameLayout 或其子类
 *    - 或继承自 include 布局的根容器
 * 3. 不能设置 android:xxx 属性（会无效）
 *    - 如 android:layout_width、android:layout_height
 * 4. 可以设置 tools 属性用于预览
 */

class CustomFrameLayout : FrameLayout {
    init {
        // 包含 merge 的布局 inflate 后
        // 子 View 会直接添加到此 FrameLayout 中
    }
}
```

**merge 原理：**

```kotlin
// LayoutInflater 对 merge 的处理
View rInflate(XmlPullParser parser, ViewGroup parent, Context context, AttributeSet attrs, boolean finishInflate) {

    if (parser.getName().equals("merge")) {
        // 直接解析子 View，添加到 parent 中
        // 不创建 merge View
        rInflateChildren(parser, parent, attrs, true);
    } else {
        // 正常创建 View
    }
}
```

---

### 10.2 \<include\> 标签

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         \<include\> 标签                                    │
└─────────────────────────────────────────────────────────────────────────────┘

include 标签用于复用布局，提高代码复用性。
```

**基本用法：**

```xml
<!-- main_layout.xml -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- 包含头部布局 -->
    <include
        android:id="@+id/header"
        layout="@layout/layout_header" />

    <!-- 包含内容布局 -->
    <include
        android:id="@+id/content"
        layout="@layout/layout_content" />

</LinearLayout>
```

**覆盖布局属性：**

```xml
<!-- include 可以覆盖被包含布局的某些属性 -->
<include
    android:id="@+id/header"
    layout="@layout/layout_header"
    android:layout_width="match_parent"
    android:layout_height="48dp"
    <!-- 注意：layout 属性需要与原始布局根元素类型兼容 -->
/>
```

**注意事项：**

```kotlin
/**
 * include 注意事项：
 *
 * 1. id 覆盖
 *    - 如果 include 和原布局都有 id，以 include 的 id 为准
 *    - 可以通过 include.findViewById() 访问
 *
 * 2. layout 属性覆盖
 *    - 只能覆盖根元素的 android:layout_* 属性
 *    - 其他属性（如 android:padding）无效
 *
 * 3. 合并多个 include
 *    - 需要为每个 include 设置唯一 id
 */

// 访问 include 的 View
val headerView = findViewById<View>(R.id.header)
val headerText = headerView?.findViewById<TextView>(R.id.tv_title)
```

---

### 10.3 \<ViewStub\> 标签

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         \<ViewStub\> 标签                                   │
└─────────────────────────────────────────────────────────────────────────────┘

ViewStub 是一个轻量级的占位 View，延迟加载 inflate 时不占用资源。
```

**基本用法：**

```xml
<!-- layout.xml -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- ViewStub：按需加载 -->
    <ViewStub
        android:id="@+id/stub_view"
        android:layout="@layout/layout_loading"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

</LinearLayout>
```

```kotlin
// 方式1: 通过 findViewById 获取后 inflate
val stub = findViewById<ViewStub>(R.id.stub_view)
stub?.inflate()  // 展开 ViewStub，返回加载的 View

// 方式2: 通过 setVisibility 触发 inflate
val stub = findViewById<ViewStub>(R.id.stub_view)
stub?.visibility = View.VISIBLE  // 自动 inflate 并显示

// 加载后的 View
val loadedView = findViewById<View>(R.id.stub_view)  // 或通过 inflate 返回值
```

**ViewStub 特点：**

```kotlin
/**
 * ViewStub 特点：
 *
 * 1. 初始不占用资源
 *    - ViewStub 本身非常小（约 24 字节）
 *    - 不绘制，不参与布局
 *
 * 2. 只能 inflate 一次
 *    - inflate 后，ViewStub 会从视图树中移除
 *    - 替换为实际的布局
 *
 * 3. 无法动态修改布局
 *    - android:layout 属性必须在 XML 中定义
 *
 * 4. 适合场景
 *    - 加载状态、空状态、错误状态
 *    - 不常用的复杂布局
 */

// 错误：多次 inflate
val stub = findViewById<ViewStub>(R.id.stub)
val view1 = stub.inflate()  // 第一次
// stub 已经从视图中移除！
val view2 = stub.inflate()  // 会抛出异常
```

**实战案例：**

```kotlin
/**
 * 实战：多状态视图
 */
class StateView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : LinearLayout(context, attrs) {

    private val contentView: View
    private val loadingView: ViewStub
    private val emptyView: ViewStub
    private val errorView: ViewStub

    enum class State { CONTENT, LOADING, EMPTY, ERROR }

    init {
        orientation = VERTICAL
        // inflate 布局
        inflate(context, R.layout.state_view, this)

        contentView = findViewById(R.id.content)
        loadingView = findViewById(R.id.stub_loading)
        emptyView = findViewById(R.id.stub_empty)
        errorView = findViewById(R.id.stub_error)

        showState(State.CONTENT)
    }

    fun showState(state: State) {
        // 先隐藏所有
        contentView.visibility = GONE
        loadingView.visibility = GONE
        emptyView.visibility = GONE
        errorView.visibility = GONE

        when (state) {
            State.CONTENT -> contentView.visibility = VISIBLE
            State.LOADING -> loadingView.visibility = VISIBLE
            State.EMPTY -> emptyView.visibility = VISIBLE
            State.ERROR -> errorView.visibility = VISIBLE
        }
    }
}
```

**ViewStub vs View.GONE：**

| 对比 | ViewStub | View.GONE |
|------|----------|-----------|
| 内存占用 | 极小（约24字节） | 正常 |
| 布局耗时 | 首次加载时 | 布局时 |
| 可复用 | 只能 inflate 一次 | 可反复显示 |
| 适用场景 | 少用的大型布局 | 频繁切换的布局 |

---

## 11. Invalidate 与 RequestLayout

### 11.1 invalidate：从本地脏标记传播到根

`invalidate()` 从 View 的内容失效开始。`invalidateInternal()` 处理 skipInvalidate、缓存有效性、dirty/invalidated 标记及父节点通知；根节点收到失效区域后安排遍历。它不直接递归调用每个子 View 的 onDraw。

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
void invalidateInternal(int l, int t, int r, int b, boolean invalidateCache,
        boolean fullInvalidate) {
    if (mGhostView != null) {
        mGhostView.invalidate(true);
        return;
    }

    if (skipInvalidate()) {
        return;
    }
    mPrivateFlags4 &= ~PFLAG4_CONTENT_CAPTURE_IMPORTANCE_MASK;
    mContentCaptureSessionCached = false;

    if ((mPrivateFlags & (PFLAG_DRAWN | PFLAG_HAS_BOUNDS)) == (PFLAG_DRAWN | PFLAG_HAS_BOUNDS)
            || (invalidateCache && (mPrivateFlags & PFLAG_DRAWING_CACHE_VALID) == PFLAG_DRAWING_CACHE_VALID)
            || (mPrivateFlags & PFLAG_INVALIDATED) != PFLAG_INVALIDATED
            || (fullInvalidate && isOpaque() != mLastIsOpaque)) {
        if (fullInvalidate) {
            mLastIsOpaque = isOpaque();
            mPrivateFlags &= ~PFLAG_DRAWN;
        }

        mPrivateFlags |= PFLAG_DIRTY;

        if (invalidateCache) {
            mPrivateFlags |= PFLAG_INVALIDATED;
            mPrivateFlags &= ~PFLAG_DRAWING_CACHE_VALID;
        }
        final AttachInfo ai = mAttachInfo;
        final ViewParent p = mParent;
        if (p != null && ai != null && l < r && t < b) {
            final Rect damage = ai.mTmpInvalRect;
            damage.set(l, t, r, b);
            p.invalidateChild(this, damage);
        }
        if (mBackground != null && mBackground.isProjected()) {
            final View receiver = getProjectionReceiver();
            if (receiver != null) {
                receiver.damageInParent();
            }
        }
    }
}
```

硬件加速下，ViewGroup 的 `invalidateChild()` 会转入 `onDescendantInvalidated()`，传播内容/动画脏状态；软件路径还会逐级处理矩形坐标和裁剪。因而不能把“逐层累加一个 dirty Rect”当成所有渲染模式共用的完整协议。

源码精简节选（省略注释；[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)）：

```java
public void onDescendantInvalidated(@NonNull View child, @NonNull View target) {
    mPrivateFlags |= (target.mPrivateFlags & PFLAG_DRAW_ANIMATION);

    if ((target.mPrivateFlags & ~PFLAG_DIRTY_MASK) != 0) {
        mPrivateFlags = (mPrivateFlags & ~PFLAG_DIRTY_MASK) | PFLAG_DIRTY;
        mPrivateFlags &= ~PFLAG_DRAWING_CACHE_VALID;
    }
    if (mLayerType == LAYER_TYPE_SOFTWARE) {
        mPrivateFlags |= PFLAG_INVALIDATED | PFLAG_DIRTY;
        target = this;
    }

    if (mParent != null) {
        mParent.onDescendantInvalidated(this, target);
    }
}
```

软件 layer 特别把自己标记为需要更新，因为子内容变化意味着该 layer 的位图内容需要重建。普通硬件 RenderNode 则可以让未变化的兄弟显示列表继续复用。绘制中的对象分配应尽量移到初始化或尺寸变化时，避免把失效频率和分配频率绑在一起。

### 11.2 requestLayout：尺寸依赖沿父链传播

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public void requestLayout() {
    if (isRelayoutTracingEnabled()) {
        Trace.instantForTrack(TRACE_TAG_APP, "requestLayoutTracing",
                mTracingStrings.classSimpleName);
        printStackStrace(mTracingStrings.requestLayoutStacktracePrefix);
    }

    if (mMeasureCache != null) mMeasureCache.clear();

    if (mAttachInfo != null && mAttachInfo.mViewRequestingLayout == null) {
        ViewRootImpl viewRoot = getViewRootImpl();
        if (viewRoot != null && viewRoot.isInLayout()) {
            if (!viewRoot.requestLayoutDuringLayout(this)) {
                return;
            }
        }
        mAttachInfo.mViewRequestingLayout = this;
    }

    mPrivateFlags |= PFLAG_FORCE_LAYOUT;
    mPrivateFlags |= PFLAG_INVALIDATED;

    if (mParent != null && !mParent.isLayoutRequested()) {
        mParent.requestLayout();
    }
    if (mAttachInfo != null && mAttachInfo.mViewRequestingLayout == this) {
        mAttachInfo.mViewRequestingLayout = null;
    }
}
```

`requestLayout()` 清空本节点测量缓存，置 `PFLAG_FORCE_LAYOUT` 和 `PFLAG_INVALIDATED`，再向尚未请求布局的父节点传播。父节点已置位时停止向上传播是合并请求，不代表子节点自己的标记没有设置。

布局过程中发起请求，会通过 `ViewRootImpl.requestLayoutDuringLayout()` 参与额外一轮布局与后续调度控制，而非立即递归测量。对于文本长度、padding、子项数变化，应在修改数据时调用 requestLayout；不要在 onDraw 内改变 LayoutParams。

### 11.3 两者对比与选择

| 状态变化 | 处理 | 原因 |
|---|---|---|
| 颜色、进度比例、选择高亮 | invalidate | 内容变了，期望大小未变 |
| 字体大小、固有图片大小、标签集合 | requestLayout，必要时 invalidate | 期望尺寸与内容都可能变化 |
| translation、scale、alpha | 优先使用 View 属性 setter | setter 已封装对应 RenderNode 属性失效 |
| 多个子项约束同时改变 | 更新后请求布局，由框架合并 | 不手动对整棵树反复 measure/layout |

例如进度条每帧只更新进度值即可重绘，不能每帧申请一个新的 LayoutParams 并 requestLayout。若进度文字变长会改变 wrap_content 大小，可以使用固定标签区，或只在期望大小真正改变时请求布局。

### 11.4 forceLayout：只标本节点，不向上排程

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public void forceLayout() {
    if (mMeasureCache != null) mMeasureCache.clear();

    mPrivateFlags |= PFLAG_FORCE_LAYOUT;
    mPrivateFlags |= PFLAG_INVALIDATED;
}
```

它与 requestLayout 都会清缓存和置位，但没有 `mParent.requestLayout()`。因此单独调用 forceLayout 不保证下一帧出现遍历；适合父容器已经控制测量周期时强制某个子节点参与，而不是业务层刷新 View 的替代品。

## 12. Draw 流程源码解析

### 12.1 View.draw() 顺序

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

### 12.2 ViewGroup.drawChild() 与硬件显示列表

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

### 12.3 属性失效与内容重录的区别

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

### 12.4 DecorView 与子项绘制顺序

DecorView 是窗口装饰根节点。其 draw 会在 super.draw 之后绘制菜单背景等窗口装饰；它不是直接跳过 View.draw 的特殊渲染器。

源码精简节选（省略注释；[DecorView.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/policy/DecorView.java)）：

```java
public void draw(Canvas canvas) {
    super.draw(canvas);

    if (mMenuBackground != null) {
        mMenuBackground.draw(canvas);
    }
}
```

ViewGroup 的子项顺序还考虑 Z 与自定义 drawing order。`setChildrenDrawingOrderEnabled(true)` 只开启自定义索引能力；存在非零 Z 时还会由有序列表处理叠放关系。硬件路径的 RenderNode 重排与触摸路径的命中排序也应共同考虑，不能只凭数组下标判断“最上层”。

在自定义容器的 onDraw 中画背景性内容时，记得 `setWillNotDraw(false)`。若只重写 dispatchDraw 增加子项之间的连线，则应把每次坐标变换限制在 save/restore 范围内，防止污染后续子项。

## 13. Canvas 高级用法

### 13.1 Canvas Save/Restore 详解

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Canvas 状态管理                                          │
└─────────────────────────────────────────────────────────────────────────────┘

Canvas 维护一个状态栈，save() 入栈，restore() 出栈。

┌─────────────────────────────────────────────────────────────────────────────┐
│                         Canvas 状态栈                                        │
└─────────────────────────────────────────────────────────────────────────────┘

状态栈内容（从栈底到栈顶）：

┌─────────────────────────────────────────────────────────────────────────────┐
│  Level 3  ──► canvas.save() 第3次调用                                      │
│  ─────────────────────────────────────                                      │
│  Level 2  ──► canvas.save() 第2次调用                                      │
│  ─────────────────────────────────────                                      │
│  Level 1  ──► canvas.save() 第1次调用                                      │
│  ─────────────────────────────────────                                      │
│  Level 0  ──► 初始状态（Canvas 创建时）                                    │
└─────────────────────────────────────────────────────────────────────────────┘

       canvas.restore()  ──► 恢复到 Level 2
       canvas.restore()  ──► 恢复到 Level 1
       canvas.restore()  ──► 恢复到 Level 0
```

**save() 保存的状态：**

```kotlin
/**
 * Canvas.save() 保存的内容：
 *
 * 1. 矩阵变换 (Matrix)
 *    - translate() 平移
 *    - rotate() 旋转
 *    - scale() 缩放
 *    - skew() 倾斜
 *    - setMatrix() 直接设置
 *
 * 2. 裁剪区域 (Clip)
 *    - clipRect()
 *    - clipPath()
 *    - clipRegion()
 *    - clipBounds()
 *
 * 3. Canvas 特有状态
 *    - 当前 save 点的位置
 *    - 离屏渲染目标 (saveLayer)
 *
 * ⚠️ 注意：save() 不保存 Paint 对象！
 */
```

**restore() 恢复的状态：**

```text
/**
 * Canvas.restore() 恢复的内容：
 *
 * - 恢复到最近一次 save() 前的状态
 * - 包括：矩阵、裁剪区域、离屏渲染目标
 *
 * ⚠️ 注意：Paint 属性不会恢复！
 *       如果需要保存 Paint 状态，需要手动保存/恢复
 */

// ❌ 错误理解：Paint 状态不会自动恢复
canvas.save()
paint.color = Color.RED
canvas.drawRect(...)
canvas.restore() // Paint 颜色不会恢复！

// ✅ 正确做法
val originalColor = paint.color
canvas.save()
paint.color = Color.RED
canvas.drawRect(...)
paint.color = originalColor // 手动恢复
canvas.restore()
```

**常见用法与场景：**

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // ========== 场景1: 隔离变换操作 ==========
    // 旋转只影响圆形，不影响矩形
    canvas.drawRect(10f, 10f, 100f, 100f, paint) // 正常

    canvas.save()
    canvas.rotate(45f, 55f, 55f) // 围绕中心旋转
    canvas.drawCircle(55f, 55f, 40f, paint)
    canvas.restore()

    canvas.drawRect(120f, 10f, 210f, 100f, paint) // 不受影响

    // ========== 场景2: 多次变换叠加 ==========
    canvas.save()
    canvas.translate(100f, 0f)
    canvas.rotate(30f)
    canvas.scale(1.5f, 1.5f)
    drawComplexContent(canvas)
    canvas.restore()

    // ========== 场景3: 嵌套使用 ==========
    canvas.save() // Level 1
    canvas.translate(x1, y1)
    drawPart1(canvas)
        canvas.save() // Level 2
        canvas.translate(x2, y2)
        drawPart2(canvas)
        canvas.restore() // 恢复到 Level 1
    drawPart3(canvas)
    canvas.restore() // 恢复到 Level 0

    // ========== 场景4: restoreToCount 指定恢复 ==========
    val saveCount = canvas.save()
    canvas.translate(100f, 100f)
    drawContent(canvas)
    // 恢复到指定层级
    canvas.restoreToCount(saveCount)
}
```

### 13.2 Canvas saveLayer/RestoreToCount 详解

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Canvas 离屏渲染                                          │
└─────────────────────────────────────────────────────────────────────────────┘

saveLayer() 与 save() 的区别：

┌────────────────────┬─────────────────────────┬─────────────────────────────┐
│       特性          │        save()          │       saveLayer()           │
├────────────────────┼─────────────────────────┼─────────────────────────────┤
│ 性能              │ 快                     │ 较慢                        │
│ 用途              │ 保存/恢复状态          │ 创建离屏渲染目标            │
│ 内存              │ 不分配额外内存         │ 分配 Bitmap 内存            │
│ 效果              │ 纯状态保存             │ 可实现图层混合/缓存        │
│ 恢复方式          │ restore()              │ restoreToCount()           │
└────────────────────┴─────────────────────────┴─────────────────────────────┘
```

**saveLayer() 详解：**

```kotlin
/**
 * saveLayer() 创建一个新的离屏渲染层（Off-screen Buffer）
 *
 * 原理：
 * 1. 创建一个与指定区域大小相同的 Bitmap
 * 2. 所有后续绘制先画到这个 Bitmap 上
 * 3. restoreToCount() 时将结果合并回原 Canvas
 *
 * 应用场景：
 * 1. 复杂效果需要完整图层
 * 2. 临时缓存绘制结果
 * 3. 实现遮罩/挖空效果
 * 4. 防止子绘制影响背景
 */

// 方式1: 完整参数
public int saveLayer(RectF bounds, Paint paint, int saveFlags)

// 方式2: 简单参数
public int saveLayer(float left, float top, float right, float bottom, Paint paint)

// 方式3: 无 Paint 参数
public int saveLayer(float left, float top, float right, float bottom, null)

// 方式4: 使用 SaveFlags
public int saveLayer(float left, float top, float right, float bottom, Paint paint, int saveFlags)

// SaveFlags 可选值：
// - ALL_SAVE_FLAG: 保存所有状态
// - CLIP_SAVE_FLAG: 仅保存裁剪区域
// - CLIP_TO_LAYER_SAVE_FLAG: 裁剪到层
// - FULL_COLOR_LAYER_SAVE_FLAG: 全色层
// - MATRIX_SAVE_FLAG: 仅保存矩阵
```

**saveLayer 详细使用：**

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // ========== 场景1: 基础离屏渲染 ==========
    // 绘制到一个新的层，最后合并
    val layerId = canvas.saveLayer(0f, 0f, width.toFloat(), height.toFloat(), null)

    // 在这个层上绘制
    canvas.drawColor(Color.RED) // 整个层变红
    canvas.drawCircle(100f, 100f, 50f, paint)

    // 恢复到原 Canvas，结果会合并
    canvas.restoreToCount(layerId)

    // ========== 场景2: 带 Paint 的离屏渲染 ==========
    // Paint 可以设置混合模式、透明度等
    val layerPaint = Paint().apply {
        alpha = 128 // 整个层半透明
        xfermode = PorterDuffXfermode(PorterDuff.Mode.DST_OVER)
    }
    val layerId2 = canvas.saveLayer(0f, 0f, width.toFloat(), height.toFloat(), layerPaint)
    canvas.drawBitmap(bitmap, 0f, 0f, paint)
    canvas.restoreToCount(layerId2)

    // ========== 场景3: 圆形遮罩效果 ==========
    // 创建圆形 Bitmap
    val maskBitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
    val maskCanvas = Canvas(maskBitmap)
    maskCanvas.drawCircle(width/2f, height/2f, width/3f, Paint().apply { color = Color.WHITE })

    // 绘制内容到离屏层
    val saved = canvas.saveLayer(0f, 0f, width.toFloat(), height.toFloat(), null)
    canvas.drawBitmap(contentBitmap, 0f, 0f, paint) // 绘制原始内容

    // 使用 DST_IN 混合模式实现遮罩
    paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.DST_IN)
    canvas.drawBitmap(maskBitmap, 0f, 0f, paint) // 只保留交集

    paint.xfermode = null
    canvas.restoreToCount(saved)

    // ========== 场景4: 抗锯齿处理 ==========
    // 某些效果需要离屏渲染才能正确实现抗锯齿
    val antiAliasLayer = canvas.saveLayer(0f, 0f, width.toFloat(), height.toFloat(),
        Paint(Paint.ANTI_ALIAS_FLAG))
    canvas.drawCircle(cx, cy, radius, paint)
    canvas.restoreToCount(antiAliasLayer)
}

/**
 * restoreToCount() 详解
 */

// save() 返回的 saveCount 用于后续恢复
val count1 = canvas.save()
canvas.translate(100f, 0f)
canvas.rotate(30f)

val count2 = canvas.save()
canvas.scale(1.5f, 1.5f)

// 恢复到 count2 之前的状态（只恢复 scale，保留 translate 和 rotate）
canvas.restoreToCount(count2)

// 恢复到 count1 之前的状态（全部恢复）
canvas.restoreToCount(count1)

// 或者直接 restore()（恢复到最近一次 save）
canvas.restore() // 恢复到 count1
canvas.restore() // 恢复到初始状态

// ⚠️ 注意：restore 次数不能超过 save 次数！
// 否则会抛出异常：IllegalStateException: Underflow in restore
```

**save() vs saveLayer() 区别总结：**

| 特性 | save() | saveLayer() |
|------|--------|------------|
| **性能** | 快（微秒级） | 较慢（毫秒级，分配内存） |
| **内存** | 无额外分配 | 分配 Bitmap |
| **用途** | 状态保存/恢复 | 离屏渲染/图层效果 |
| **场景** | 简单变换 | 混合模式、遮罩、缓存 |

### 13.3 Canvas 裁剪高级用法

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Canvas 裁剪操作                                          │
└─────────────────────────────────────────────────────────────────────────────┘

裁剪 (Clipping) 用于限制绘制区域，只在裁剪区域内绘制内容。

┌─────────────────────────────────────────────────────────────────────────────┐
│                         裁剪类型                                             │
└─────────────────────────────────────────────────────────────────────────────┘

1. clipRect()   - 矩形裁剪
2. clipPath()   - 路径裁剪
3. clipRegion() - 区域裁剪
4. clipBounds() - 边界裁剪
```

**裁剪操作详解：**

```kotlin
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // ========== 1. 矩形裁剪 ==========
    canvas.save()
    // 裁剪左上区域
    canvas.clipRect(0f, 0f, 200f, 200f)
    // 超出裁剪区域的内容不会绘制
    canvas.drawColor(Color.RED)
    canvas.restore()

    // ========== 2. 路径裁剪 ==========
    canvas.save()
    // 创建圆形路径
    val path = Path().apply {
        addCircle(350f, 150f, 80f, Path.Direction.CW)
    }
    canvas.clipPath(path)
    canvas.drawColor(Color.BLUE)
    canvas.restore()

    // ========== 3. 复杂形状裁剪 ==========
    canvas.save()
    val complexPath = Path().apply {
        // 绘制一个心形
        moveTo(200f, 100f)
        cubicTo(150f, 50f, 100f, 100f, 200f, 180f)
        cubicTo(300f, 100f, 250f, 50f, 200f, 100f)
    }
    canvas.clipPath(complexPath)
    canvas.drawColor(Color.GREEN)
    canvas.restore()
}
```

**Region Op 组合裁剪：**

```kotlin
/**
 * Region.Op - 裁剪区域的集合运算
 *
 * 用于实现复杂的裁剪效果
 */
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // 裁剪区域 A
    val regionA = Region(100, 100, 300, 300)
    // 裁剪区域 B
    val regionB = Region(200, 200, 400, 400)

    // ========== 1. DIFFERENCE - A 减去 B ==========
    // A - B = A 中减去 B 的部分
    canvas.save()
    val diffRegion = Region(regionA)
    diffRegion.op(regionB, Region.Op.DIFFERENCE)
    drawRegion(canvas, diffRegion, Color.RED)
    canvas.restore()

    // ========== 2. INTERSECT - A 和 B 的交集 ==========
    canvas.save()
    val intersectRegion = Region(regionA)
    intersectRegion.op(regionB, Region.Op.INTERSECT)
    drawRegion(canvas, intersectRegion, Color.GREEN)
    canvas.restore()

    // ========== 3. UNION - A 和 B 的并集 ==========
    canvas.save()
    val unionRegion = Region(regionA)
    unionRegion.op(regionB, Region.Op.UNION)
    drawRegion(canvas, unionRegion, Color.BLUE)
    canvas.restore()

    // ========== 4. XOR - A 和 B 的异或 ==========
    // 只保留不重叠的部分
    canvas.save()
    val xorRegion = Region(regionA)
    xorRegion.op(regionB, Region.Op.XOR)
    drawRegion(canvas, xorRegion, Color.YELLOW)
    canvas.restore()

    // ========== 5. REPLACE - 只保留 B ==========
    canvas.save()
    val replaceRegion = Region(regionA)
    replaceRegion.op(regionB, Region.Op.REPLACE)
    drawRegion(canvas, replaceRegion, Color.MAGENTA)
    canvas.restore()
}

private fun drawRegion(canvas: Canvas, region: Region, color: Int) {
    val bounds = Rect()
    // 获取区域边界
    if (region.getBounds(bounds)) {
        // 遍历区域中的每个矩形并绘制
        val iterator = RegionIterator(region)
        val rect = Rect()
        while (iterator.next(rect)) {
            canvas.drawRect(rect, Paint().apply { this.color = color })
        }
    }
}
```

**Region Op 图解：**

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Region.Op 效果图解                                      │
└─────────────────────────────────────────────────────────────────────────────┘

   区域 A (红色)          区域 B (蓝色)         结果
   ┌──────────┐          ┌──────────┐      ┌──────────┐
   │          │          │          │      │ ▓▓▓▓▓▓▓▓│
   │   A      │          │   B      │      │ ▓▓   ▓▓▓▓│
   │          │◄────────►│          │      │ ▓▓ B ▓▓▓▓│
   │          │  重叠    │          │      │ ▓▓▓▓▓▓▓▓│
   └──────────┘          └──────────┘      └──────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                     Op 效果说明                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ DIFFERENCE (A-B): A 减去 B 的部分                                          │
│     ┌──────────┐                                                        │
│     │ ▓▓▓▓▓   │                                                        │
│     │ ▓▓      │                                                        │
│     └──────────┘                                                        │
│                                                                         │
│ INTERSECT: A 和 B 的交集                                                  │
│         ┌──┐                                                           │
│         │▓▓│                                                            │
│         └──┘                                                            │
│                                                                         │
│ UNION (A|B): A 和 B 的并集                                                │
│     ┌──────────┐                                                        │
│     │▓▓▓▓▓▓▓▓│                                                        │
│     │▓▓▓▓▓▓▓▓│                                                        │
│     └──────────┘                                                        │
│                                                                         │
│ XOR (A^B): A 和 B 的异或（不重叠部分）                                     │
│     ┌──────────┐                                                        │
│     │ ▓▓    ▓▓│                                                        │
│     │ ▓▓    ▓▓│                                                        │
│     └──────────┘                                                        │
│                                                                         │
│ REPLACE: 只保留 B                                                        │
│         ┌──┐                                                           │
│         │▓▓│                                                            │
│         └──┘                                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 13.4 混合模式 (PorterDuff) 详细解析

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PorterDuff 混合模式                                      │
└─────────────────────────────────────────────────────────────────────────────┘

PorterDuff 混合模式描述了：源图像（Src）如何与目标图像（Dst）混合

公式：Dst = Dst OP Src
- Dst: 已绘制的内容（目标/底图）
- Src: 新绘制的内容（源/前景）
- OP: 混合操作
```

**混合模式分类：**

```kotlin
/**
 * PorterDuff.Mode 所有模式
 */
enum class Mode {
    // 清除类
    CLEAR,      // 清除目标（全部透明）

    // 替换类
    SRC,        // 只显示源
    DST,        // 只显示目标
    SRC_OVER,   // 源覆盖在目标上
    DST_OVER,   // 目标覆盖在源上
    SRC_IN,     // 源与目标交集
    DST_IN,     // 目标与源交集
    SRC_OUT,    // 源与目标差集
    DST_OUT,    // 目标与源差集

    // 特殊类
    SRC_ATOP,   // 目标内显示源
    DST_ATOP,   // 源内显示目标
    XOR,        // 异或（不重叠部分）

    // 组合类
    MULTIPLY,   // 源乘以目标（变暗）
    SCREEN,     // 源+目标-源*目标（变亮）
    ADD,        // 源+目标（ saturate）
    OVERLAY,    // 叠加（保留对比度）
    DARKEN,     // 变暗（取较暗）
    LIGHTEN,    // 变亮（取较亮）
    COLOR_DODGE,// 颜色减淡
    COLOR_BURN, // 颜色加深
    HARD_LIGHT, // 强光
    SOFT_LIGHT, // 柔光
    DIFFERENCE, // 差值
    EXCLUSION   // 排除
}
```

**视觉效果图解：**

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     混合模式视觉效果                                          │
└─────────────────────────────────────────────────────────────────────────────┘

                    源 (圆形)           目标 (方形)           结果

┌─────────────────┬─────────────────┬─────────────────┬─────────────────────┐
│     模式        │     Src         │     Dst         │      结果           │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│   CLEAR         │                 │                 │                     │
│                 │       ◯        │    ▢            │   (透明)            │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│   SRC           │                 │                 │                     │
│                 │       ◯        │    ▢            │       ◯            │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│   DST           │                 │                 │                     │
│                 │       ◯        │    ▢            │       ▢            │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│   SRC_OVER      │                 │                 │      ◯▢            │
│                 │       ◯        │    ▢            │    (源覆盖目标)    │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│   DST_OVER      │                 │                 │      ▢◯           │
│                 │       ◯        │    ▢            │    (目标覆盖源)    │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│   SRC_IN        │                 │                 │                     │
│                 │       ◯        │    ▢            │       ◯            │
│                 │                 │                 │   (交集=圆形)       │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│   DST_IN        │                 │                 │                     │
│                 │       ◯        │    ▢            │       ▢            │
│                 │                 │                 │   (交集=方形)       │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│   MULTIPLY     │                 │                 │                     │
│                 │       ◯        │    ▢            │    (变暗效果)       │
│                 │                 │                 │                     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│   SCREEN       │                 │                 │                     │
│                 │       ◯        │    ▢            │    (变亮效果)       │
│                 │                 │                 │                     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
│   ADD          │                 │                 │                     │
│                 │       ◯        │    ▢            │   (颜色叠加)        │
│                 │                 │                 │                     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
```

**实际应用示例：**

```kotlin
/**
 * 混合模式实际应用
 */

// 应用1: 圆形头像
fun createCircularBitmap(src: Bitmap): Bitmap {
    val output = Bitmap.createBitmap(src.width, src.height, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(output)

    val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    // 1. 绘制圆形遮罩（作为目标）
    val rect = RectF(0f, 0f, src.width.toFloat(), src.height.toFloat())
    canvas.drawOval(rect, paint) // DST

    // 2. 设置混合模式
    paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.SRC_IN)

    // 3. 绘制源图像（只保留与圆形交集的部分）
    canvas.drawBitmap(src, 0f, 0f, paint)

    return output
}

// 应用2: 圆角图片
fun createRoundedBitmap(src: Bitmap, cornerRadius: Float): Bitmap {
    val output = Bitmap.createBitmap(src.width, src.height, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(output)

    val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    val rect = RectF(0f, 0f, src.width.toFloat(), src.height.toFloat())

    // 1. 绘制圆角矩形
    canvas.drawRoundRect(rect, cornerRadius, cornerRadius, paint)

    // 2. 裁剪
    paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.SRC_IN)

    // 3. 绘制源
    canvas.drawBitmap(src, 0f, 0f, paint)

    return output
}

// 应用3: 颜色叠加
fun overlayColor(src: Bitmap, overlayColor: Int): Bitmap {
    val output = Bitmap.createBitmap(src.width, src.height, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(output)

    // 1. 绘制原图
    canvas.drawBitmap(src, 0f, 0f, null)

    // 2. 设置叠加颜色
    val paint = Paint()
    paint.color = overlayColor
    paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.ADD)

    // 3. 叠加颜色
    canvas.drawRect(0f, 0f, src.width.toFloat(), src.height.toFloat(), paint)

    return output
}

// 应用4: 擦除效果（去除水印）
fun eraseWatermark(bitmap: Bitmap, watermarkRegion: RectF): Bitmap {
    val output = Bitmap.createBitmap(bitmap.width, bitmap.height, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(output)

    // 1. 绘制原图
    canvas.drawBitmap(bitmap, 0f, 0f, null)

    // 2. 设置清除模式
    val paint = Paint()
    paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.CLEAR)

    // 3. 擦除指定区域
    canvas.drawRect(watermarkRegion, paint)

    return output
}

// 应用5: 淡入效果
fun fadeIn(bitmap: Bitmap, progress: Float): Bitmap {
    val output = Bitmap.createBitmap(bitmap.width, bitmap.height, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(output)

    // 绘制源
    canvas.drawBitmap(bitmap, 0f, 0f, null)

    // 叠加白色淡入
    val paint = Paint()
    paint.color = Color.WHITE
    paint.alpha = (progress * 255).toInt()
    paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.DST_OVER)

    canvas.drawRect(0f, 0f, bitmap.width.toFloat(), bitmap.height.toFloat(), paint)

    return output
}
```

**使用离屏渲染避免问题：**

```kotlin
/**
 * ⚠️ 重要：使用 Xfermode 时最好配合 saveLayer
 *
 * 原因：某些模式需要完整的层才能正确计算
 *       否则可能出现不可预期的边缘效果
 */

// ❌ 错误：可能产生边缘问题
val paint = Paint()
paint.xfermode = PorterDuffXfermode(PorterDuff.Mode.SRC_IN)
canvas.drawBitmap(src, 0f, 0f, paint) // 没有创建层

// ✅ 正确：使用 saveLayer
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // 创建离屏层
    val saveCount = canvas.saveLayer(0f, 0f, width.toFloat(), height.toFloat(), null)

    // 绘制目标
    canvas.drawOval(rect, dstPaint)

    // 设置混合模式并绘制源
    srcPaint.xfermode = PorterDuffXfermode(PorterDuff.Mode.SRC_IN)
    canvas.drawBitmap(src, 0f, 0f, srcPaint)
    srcPaint.xfermode = null

    // 恢复
    canvas.restoreToCount(saveCount)
}
```

---

## 14. View 与 ViewGroup 区别

### 14.1 核心区别

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      View vs ViewGroup 区别                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬─────────────────────┬─────────────────────────────────┐
│       特性          │       View          │        ViewGroup               │
├─────────────────────┼─────────────────────┼─────────────────────────────────┤
│ 父类                │ Object              │ View                            │
│ onDraw()            │ 有（需重写）        │ 默认不绘制（WILL_NOT_DRAW=true） │
│ dispatchDraw()      │ 无                  │ 有（分发绘制给子 View）         │
│ children            │ 无                  │ 有（管理子 View）               │
│ layout 流程         │ 无                  │ 有（布局子 View）               │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘
```

### 14.2 setWillNotDraw()

```kotlin
/**
 * ViewGroup 默认 WILL_NOT_DRAW = true
 *
 * 原因：ViewGroup 主要负责布局，自身通常不需要绘制
 *
 * 如果需要在 ViewGroup 中绘制内容：
 * 1. 必须调用 setWillNotDraw(false)
 * 2. 重写 onDraw() 方法
 */

class CustomViewGroup @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : ViewGroup(context, attrs) {

    init {
        // 开启绘制
        setWillNotDraw(false)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // 在这里绘制背景、分隔线等
        canvas.drawColor(Color.parseColor("#F5F5F5"))
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        // 布局子 View
    }
}
```

### 14.3 ViewGroup 绘制相关方法

`View.drawBackground(Canvas)` 是私有实现，应用不能 override 或调用 `super.drawBackground()`。设置背景用 `background` / `setBackgroundColor()`，绘制扩展使用公开或 protected 回调。

```kotlin
// 由 FrameLayout 负责测量和布局，避免缺少测量实现的裸 ViewGroup 示例。
class DecoratedContainer(context: Context) : FrameLayout(context) {
    private val linePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.GRAY }
    init { setWillNotDraw(false) }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // 自身内容，位于子项之前。
    }

    override fun dispatchDraw(canvas: Canvas) {
        super.dispatchDraw(canvas)
        canvas.drawLine(0f, 0f, width.toFloat(), 0f, linePaint)
    }
}
```

依据：[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)、[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)。

## 15. 常见问题

### 15.1 wrap_content 不生效问题

#### 15.1.1 问题原因

```kotlin
/**
 * 问题：自定义 View 设置 wrap_content 时，效果和 match_parent 一样
 *
 * 原因：View 的默认 onMeasure() 使用 getDefaultSize()
 *       对于 AT_MOST 和 EXACTLY 模式，都返回父容器允许的尺寸
 */

public static int getDefaultSize(int size, int measureSpec) {
    int result = size;
    int specMode = MeasureSpec.getMode(measureSpec);
    int specSize = MeasureSpec.getSize(measureSpec);

    switch (specMode) {
        case MeasureSpec.UNSPECIFIED:
            result = size; // 使用默认尺寸
            break;
        case MeasureSpec.AT_MOST:
        case MeasureSpec.EXACTLY:
            result = specSize; // 都返回父容器尺寸！
            break;
    }
    return result;
}
```

#### 15.1.2 解决方案

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // 自定义的默认尺寸
    private val DEFAULT_WIDTH = 200.dp2px()
    private val DEFAULT_HEIGHT = 150.dp2px()
    private val MIN_WIDTH = 50.dp2px()
    private val MIN_HEIGHT = 50.dp2px()

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)

        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)
        val heightMode = MeasureSpec.getMode(heightMeasureSpec)
        val heightSize = MeasureSpec.getSize(heightMeasureSpec)

        var resultWidth = DEFAULT_WIDTH
        var resultHeight = DEFAULT_HEIGHT

        // 处理 AT_MOST 模式 - 使用内容尺寸限制
        when (widthMode) {
            MeasureSpec.EXACTLY -> {
                resultWidth = widthSize // match_parent 或固定值
            }
            MeasureSpec.AT_MOST -> {
                // wrap_content：取默认值和父容器允许值的较小者
                resultWidth = minOf(DEFAULT_WIDTH, widthSize)
            }
            MeasureSpec.UNSPECIFIED -> {
                resultWidth = DEFAULT_WIDTH
            }
        }

        when (heightMode) {
            MeasureSpec.EXACTLY -> resultHeight = heightSize
            MeasureSpec.AT_MOST -> resultHeight = minOf(DEFAULT_HEIGHT, heightSize)
            MeasureSpec.UNSPECIFIED -> resultHeight = DEFAULT_HEIGHT
        }

        // 设置最小尺寸限制
        resultWidth = maxOf(resultWidth, MIN_WIDTH)
        resultHeight = maxOf(resultHeight, MIN_HEIGHT)

        setMeasuredDimension(resultWidth, resultHeight)
    }

    private fun Int.dp2px(): Int = (this * resources.displayMetrics.density).toInt()
}
```

---

### 15.2 获取 View 宽高的正确时机

### 16.1 为什么 onResume 中获取宽高返回 0

```kotlin
/**
 * 问题：onResume 中获取 View 宽高返回 0
 *
 * 原因：handleResumeActivity() 流程
 * 1. performResumeActivity() -> onResume()
 * 2. WindowManager.addView() -> 才开始首次测量/布局
 *
 * 所以 onResume() 执行时，View 尚未测量！
 */

class MainActivity : AppCompatActivity() {

    override fun onResume() {
        super.onResume()

        // ❌ 错误：返回 0
        val width = findViewById<View>(R.id.xxx).width // 0
    }
}
```

### 16.2 View.post() 原理详解

```text
/**
 * View.post(Runnable) 为什么能获取到宽高？
 *
 * 原理：
 * 1. 如果 View 已附加到窗口 (attachedToWindow=true)
 *    -> 通过 mAttachInfo.mHandler 发送到主线程消息队列
 *    -> 在 performTraversals() 之后执行
 *
 * 2. 如果 View 未附加到窗口
 *    -> 缓存到 HandlerActionQueue
 *    -> 等 dispatchAttachedToWindow() 时再执行
 */

class MainActivity : AppCompatActivity() {

    override fun onResume() {
        super.onResume()

        // ✅ 正确：使用 post
        findViewById<View>(R.id.xxx).post {
            val width = it.width // 有效！
            val height = it.height // 有效！
        }
    }
}

// View.post 源码简化
public void post(Runnable action) {
    if (mAttachInfo != null) {
        // 已附加到窗口，直接发送到 Handler
        mAttachInfo.mHandler.post(action);
    } else {
        // 未附加，缓存起来
        getRunQueue().post(action);
    }
}
```

### 16.3 其他获取宽高的正确方式

```kotlin
// 方式1: ViewTreeObserver
view.viewTreeObserver.addOnGlobalLayoutListener(object : OnGlobalLayoutListener {
    override fun onGlobalLayout() {
        // View 布局完成后回调
        val width = view.width
        val height = view.height

        // 记得移除监听
        view.viewTreeObserver.removeOnGlobalLayoutListener(this)
    }
})

// 方式2: OnLayoutChangeListener
view.addOnLayoutChangeListener { v, left, top, right, bottom ->
    val width = v.width
    val height = v.height
}

// 方式3: onSizeChanged()
override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
    super.onSizeChanged(w, h, oldw, oldh)
    // 首次布局和尺寸变化时回调
}
```

---

## 16. 线程与 UI 更新

### 16.1 子线程不能更新 UI 的原因

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      为什么子线程不能更新 UI                                 │
└─────────────────────────────────────────────────────────────────────────────┘

1. View 不是线程安全的
   - UI 操作涉及复杂的状态管理
   - 并发访问会导致状态不一致

2. ViewRootImpl 检查线程
   - ViewRootImpl 在构造时绑定创建线程
   - 部分关键路径会检查线程；不是所有 setter 都同步抛异常

3. Surface 绘制有独立协议
   - SurfaceHolder 的锁定、提交和生命周期必须协调
   - 它不能作为后台线程任意修改 View 树的许可

// ViewRootImpl 线程检查
void checkThread() {
    if (mThread != Thread.currentThread()) {
        throw new CalledFromWrongThreadException(
            "Only the original thread that created ViewRootImpl can touch its views"
        );
    }
}
```

### 16.2 更新 UI 的正确方式

```kotlin
class MyActivity : AppCompatActivity() {

    // 方式1: runOnUiThread()
    private fun updateFromThread() {
        runOnUiThread {
            textView.text = "Updated from thread"
        }
    }

    // 方式2: View.post()
    private fun updateFromThread2() {
        Thread {
            // 子线程中
            textView.post {
                textView.text = "Updated"
            }
        }.start()
    }

    // 方式3: Handler
    private val handler = Handler(Looper.getMainLooper())

    private fun updateFromThread3() {
        Thread {
            handler.post {
                textView.text = "Updated"
            }
        }.start()
    }
}

// ❌ 错误：子线程直接更新 UI
Thread {
    textView.text = "Unsafe" // 非线程安全；是否当场抛异常取决于调用路径
}.start()
```

### 16.3 特殊情况：SurfaceView

```kotlin
/**
 * SurfaceView 可以在子线程绘制
 *
 * 原因：
 * 1. SurfaceView 有独立的 Surface
 * 2. 工作线程绘制需与 surfaceCreated/surfaceDestroyed 生命周期协调
 * 3. 通过 lockCanvas/unlockCanvasAndPost 绘制
 */

class MySurfaceView : SurfaceView, Runnable {

    private var isRunning = false
    private val paint = Paint()

    fun start() {
        isRunning = true
        Thread(this).start()
    }

    override fun run() {
        while (isRunning) {
            val canvas = holder.lockCanvas() // 获取 Canvas
            if (canvas != null) {
                // 子线程绘制
                canvas.drawColor(Color.BLACK)
                canvas.drawCircle(100f, 100f, 50f, paint)
                holder.unlockCanvasAndPost(canvas) // 提交绘制
            }
            Thread.sleep(16) // ~60fps
        }
    }
}
```

---

### 15.3 width/height 区别

### 18.1 区别

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│              width/height vs measuredWidth/measuredHeight                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┬─────────────────────────────────────────────────┐
│     measuredDimension   │              dimension                            │
├─────────────────────────┼─────────────────────────────────────────────────┤
│ 测量阶段 (Measure)     │ 布局阶段 (Layout)                                │
│                         │                                                 │
│ onMeasure() 中设置     │ layout() 中最终确定                              │
│                         │                                                 │
│ 期望的尺寸              │ 实际的尺寸                                      │
│                         │                                                 │
│ 可能被父容器调整        │ 最终生效的尺寸                                  │
└─────────────────────────┴─────────────────────────────────────────────────┘

// 获取方式
val measuredW = view.measuredWidth   // 测量宽度
val measuredH = view.measuredHeight  // 测量高度

val actualW = view.width            // 实际宽度
val actualH = view.height           // 实际高度
```

### 18.2 MeasureSpec 不能与 LayoutParams 一对一等同

MeasureSpec 是父容器结合自身约束、padding/margin 和子项 LayoutParams 计算的结果。EXACTLY 不只是 match_parent，AT_MOST 也不是看到 wrap_content 就无条件成立；例如父 UNSPECIFIED 的分支有独立处理。

| mode | 对自定义测量的约束 |
|---|---|
| EXACTLY | 使用 specSize，不因自定义最小尺寸再扩大 |
| AT_MOST | 期望尺寸不能突破 specSize，可返回 TOO_SMALL 测量状态 |
| UNSPECIFIED | 根据内容、padding、建议最小尺寸决定期望值 |

宽和高都必须计算并传给 setMeasuredDimension。只计算 resultWidth 却使用未定义 resultHeight 的代码不能作为完整示例。固定实现见 [ViewGroup.getChildMeasureSpec](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java) 和 [View.resolveSizeAndState](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)。

### 18.3 处理 wrap_content、padding 和最小尺寸

```kotlin
class SizedContentView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {
    private val contentSizePx = TypedValue.applyDimension(
        TypedValue.COMPLEX_UNIT_DIP, 100f, resources.displayMetrics
    ).roundToInt() // import kotlin.math.roundToInt

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val desiredWidth = maxOf(suggestedMinimumWidth,
            contentSizePx + paddingLeft + paddingRight)
        val desiredHeight = maxOf(suggestedMinimumHeight,
            contentSizePx + paddingTop + paddingBottom)
        setMeasuredDimension(
            resolveSizeAndState(desiredWidth, widthMeasureSpec, 0),
            resolveSizeAndState(desiredHeight, heightMeasureSpec, 0)
        )
    }
}
```

最小尺寸约束先进入期望值，再与父约束合并，不能在解析 EXACTLY/AT_MOST 后用 maxOf 强行撑大结果。父 EXACTLY 40px 时，即便内容期望 100px，也必须测量为 40px；AT_MOST 40px 则受限并可标 TOO_SMALL。绘制内容应裁剪/缩放或重排以适应最终空间，而不是篡改父容器约束。

---

## 19. 自定义属性详解

### 19.1 属性声明

```xml
<!-- res/values/attrs.xml -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- 方式1: 单独声明 -->
    <attr name="custom_color" format="color" />
    <attr name="custom_size" format="dimension" />
    <attr name="custom_text" format="string" />
    <attr name="custom_boolean" format="boolean" />
    <attr name="custom_float" format="float" />
    <attr name="custom_integer" format="integer" />
    <attr name="custom_enum" format="enum">
        <enum name="normal" value="0" />
        <enum name="custom" value="1" />
        <enum name="special" value="2" />
    </attr>
    <attr name="custom_flags" format="flags">
        <flag name="horizontal" value="0x01" />
        <flag name="vertical" value="0x02" />
    </attr>

    <!-- 方式2: 声明 styleable -->
    <declare-styleable name="CustomView">
        <attr name="cv_color" />
        <attr name="cv_size" />
        <attr name="cv_text" />
        <attr name="cv_mode" />
        <attr name="cv_showIcon" format="boolean" />
    </declare-styleable>

    <!-- 继承已有属性 -->
    <declare-styleable name="CustomTextView" parent="TextView">
        <attr name="custom_border" format="color" />
    </declare-styleable>
</resources>
```

### 19.2 属性解析

```text
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    // 属性变量
    private var mColor: Int = Color.RED
    private var mSize: Float = 50f.dp2px()
    private var mText: String = ""
    private var mMode: Int = 0
    private var mShowIcon: Boolean = true

    init {
        // 方式1: 直接获取单个属性
        attrs?.let {
            val typedArray = context.obtainStyledAttributes(it, R.styleable.CustomView)
            try {
                mColor = typedArray.getColor(R.styleable.CustomView_cv_color, mColor)
                mSize = typedArray.getDimension(R.styleable.CustomView_cv_size, mSize)
                mText = typedArray.getString(R.styleable.CustomView_cv_text) ?: ""
                mMode = typedArray.getInt(R.styleable.CustomView_cv_mode, mMode)
                mShowIcon = typedArray.getBoolean(R.styleable.CustomView_cv_showIcon, mShowIcon)
            } finally {
                typedArray.recycle()
            }
        }

        // 方式2: 获取主题属性
        val typedArray2 = context.obtainStyledAttributes(R.styleable.CustomView)
        // ...
        typedArray2.recycle()
    }

    private fun Float.dp2px(): Float = this * resources.displayMetrics.density
}
```

### 19.3 属性优先级

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         属性优先级                                          │
└─────────────────────────────────────────────────────────────────────────────┘

优先级（从高到低）：
1. XML 直接设置     <com.app.CustomView app:cv_color="#FF0000" />
2. Style 设置       android:style="@style/CustomStyle"
3. 主题属性        <item name="cv_color">#00FF00</item>
4. 默认值          代码中设置的值
```

### 19.4 在 XML 中使用

```xml
<!-- 布局中使用 -->
<com.app.CustomView
    android:id="@+id/custom_view"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    app:cv_color="@color/red"
    app:cv_size="48dp"
    app:cv_text="Hello"
    app:cv_mode="normal"
    app:cv_showIcon="true" />

<!-- 定义 Style -->
<style name="CustomViewStyle">
    <item name="cv_color">@color/blue</item>
    <item name="cv_size">32dp</item>
</style>

<!-- 应用 Style -->
<com.app.CustomView
    style="@style/CustomViewStyle"
    ... />
```

---

## 20. 事件处理与交互

### 20.1 onTouchEvent

点击与拖动不能仅通过 UP 区分：超出 touchSlop、多指参与、CANCEL 都应取消本次点击资格。以下单指点击示例始终消费自己已接受的流，只在未拖动的有效 UP 调用 performClick：

```kotlin
class TouchView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {
    private val slop = ViewConfiguration.get(context).scaledTouchSlop
    private var downX = 0f
    private var downY = 0f
    private var clickCandidate = false

    init { isClickable = true }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (!isEnabled) return super.onTouchEvent(event)
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                downX = event.x
                downY = event.y
                clickCandidate = true
                isPressed = true
            }
            MotionEvent.ACTION_POINTER_DOWN -> {
                clickCandidate = false
                isPressed = false
            }
            MotionEvent.ACTION_MOVE -> {
                if (kotlin.math.abs(event.x - downX) > slop ||
                    kotlin.math.abs(event.y - downY) > slop) {
                    clickCandidate = false
                    isPressed = false
                }
            }
            MotionEvent.ACTION_UP -> {
                val click = clickCandidate && event.x >= 0 && event.x < width &&
                    event.y >= 0 && event.y < height
                clickCandidate = false
                isPressed = false
                if (click) performClick()
            }
            MotionEvent.ACTION_CANCEL -> {
                clickCandidate = false
                isPressed = false
            }
        }
        return true
    }

    override fun performClick(): Boolean {
        super.performClick() // 保留 OnClickListener 与无障碍点击事件
        return true
    }
}
```

原生 View 的 onTouchEvent 还实现长按、工具类型、按压反馈等分支；无需自定义手势时优先使用原生点击行为。依据：[AOSP 17 View.onTouchEvent / performClick](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)。

### 20.2 GestureDetector 手势处理

```kotlin
class GestureView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val gestureDetector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {

        // 单击
        override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
            // 处理单击
            return true
        }

        // 双击
        override fun onDoubleTap(e: MotionEvent): Boolean {
            // 处理双击
            return true
        }

        // 长按
        override fun onLongPress(e: MotionEvent) {
            // 处理长按
        }

        // 滑动
        override fun onScroll(e1: MotionEvent?, e2: MotionEvent, distanceX: Float, distanceY: Float): Boolean {
            // 处理滑动
            return true
        }

        // 快速滑动
        override fun onFling(e1: MotionEvent?, e2: MotionEvent, velocityX: Float, velocityY: Float): Boolean {
            // 处理快速滑动
            return true
        }
    })

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

### 20.3 滑动冲突解决

```kotlin
/**
 * 方式1: onInterceptTouchEvent() 拦截
 */
class CustomViewGroup @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : ViewGroup(context, attrs) {

    private var lastX = 0f
    private var lastY = 0f

    override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
        when (ev.action) {
            MotionEvent.ACTION_DOWN -> {
                lastX = ev.x
                lastY = ev.y
            }
            MotionEvent.ACTION_MOVE -> {
                val dx = abs(ev.x - lastX)
                val dy = abs(ev.y - lastY)
                // 横向滑动时拦截
                return dx > dy && dx > ViewConfiguration.get(context).scaledTouchSlop
            }
        }
        return super.onInterceptTouchEvent(ev)
    }
}

/**
 * 方式2: requestDisallowInterceptTouchEvent()
 */
class ChildView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                parent?.requestDisallowInterceptTouchEvent(true)
                return true // 接受 DOWN，否则后续请求可能根本没有机会执行
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL ->
                parent?.requestDisallowInterceptTouchEvent(false)
        }
        return true // 示例仅演示手势所有权；业务点击/滚动需独立实现
    }
}
```

### 20.4 多点触控

```kotlin
class MultiTouchView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    // 记录多个手指
    private val pointers = mutableMapOf<Int, Pair<Float, Float>>()

    override fun onTouchEvent(event: MotionEvent): Boolean {
        val actionIndex = event.actionIndex
        val pointerId = event.getPointerId(actionIndex)

        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                pointers[pointerId] = Pair(event.getX(actionIndex), event.getY(actionIndex))
            }
            MotionEvent.ACTION_POINTER_DOWN -> {
                pointers[pointerId] = Pair(event.getX(actionIndex), event.getY(actionIndex))
            }
            MotionEvent.ACTION_MOVE -> {
                for (i in 0 until event.pointerCount) {
                    val id = event.getPointerId(i)
                    val x = event.getX(i)
                    val y = event.getY(i)
                    pointers[id] = Pair(x, y)
                }
            }
            MotionEvent.ACTION_POINTER_UP -> {
                pointers.remove(pointerId)
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                pointers.clear()
            }
        }

        // 处理多点触控逻辑（如钢琴键盘）
        processMultiTouch()
        return true
    }

    private fun processMultiTouch() {
        // 处理每个手指的位置
    }
}
```

---

## 21. 实战案例

### 21.1 圆形进度条

```kotlin
class CircleProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress: Float = 0f
    private var maxProgress: Float = 100f
    private var progressColor: Int = Color.parseColor("#2196F3")
    private var backgroundColor: Int = Color.parseColor("#E0E0E0")
    private var strokeWidth: Float = 20f.dp2px()
    private var showText: Boolean = true

    private val backgroundPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
    }

    private val progressPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
    }

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textAlign = Paint.Align.CENTER
    }

    init {
        context.obtainStyledAttributes(attrs, R.styleable.CircleProgressView).apply {
            try {
                progressColor = getColor(R.styleable.CircleProgressView_cv_color, progressColor)
                strokeWidth = getDimension(R.styleable.CircleProgressView_cv_size, strokeWidth)
                showText = getBoolean(R.styleable.CircleProgressView_cv_showText, showText)
            } finally { recycle() }
        }

        backgroundPaint.color = backgroundColor
        backgroundPaint.strokeWidth = strokeWidth
        progressPaint.color = progressColor
        progressPaint.strokeWidth = strokeWidth
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        textPaint.textSize = minOf(w, h) / 4f
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val centerX = width / 2f
        val centerY = height / 2f
        val radius = minOf(centerX, centerY) - strokeWidth / 2

        // 绘制背景圆
        canvas.drawCircle(centerX, centerY, radius, backgroundPaint)

        // 绘制进度
        val sweepAngle = (progress / maxProgress) * 360f
        canvas.drawArc(
            RectF(centerX - radius, centerY - radius, centerX + radius, centerY + radius),
            -90f, sweepAngle, false, progressPaint
        )

        // 绘制文字
        if (showText) {
            val percent = (progress / maxProgress * 100).toInt()
            canvas.drawText("$percent%", centerX, centerY + textPaint.textSize / 3, textPaint)
        }
    }

    fun setProgress(value: Float) {
        progress = value.coerceIn(0f, maxProgress)
        invalidate()
    }

    // 结合 ValueAnimator 实现动画
    fun animateProgress(targetProgress: Float, duration: Long = 1000L) {
        ValueAnimator.ofFloat(progress, targetProgress).apply {
            this.duration = duration
            interpolator = AccelerateDecelerateInterpolator()
            addUpdateListener { animation ->
                progress = animation.animatedValue as Float
                invalidate()
            }
            start()
        }
    }

    private fun Float.dp2px(): Float = this * resources.displayMetrics.density
}
```

### 21.2 组合标题栏

```xml
<!-- res/layout/title_bar.xml -->
<merge xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="56dp"
    android:background="@color/primary"
    android:gravity="center_vertical"
    android:paddingHorizontal="16dp">

    <ImageView
        android:id="@+id/btn_back"
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:src="@drawable/ic_back"
        app:tint="@color/white" />

    <TextView
        android:id="@+id/tv_title"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:gravity="center"
        android:textColor="@color/white"
        android:textSize="18sp" />

    <ImageView
        android:id="@+id/btn_right"
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:src="@drawable/ic_more"
        android:visibility="gone" />

</merge>
```

```kotlin
class TitleBarView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private val btnBack: ImageView
    private val tvTitle: TextView
    private val btnRight: ImageView

    var onBackClick: (() -> Unit)? = null
    var onRightClick: (() -> Unit)? = null

    init {
        LayoutInflater.from(context).inflate(R.layout.title_bar, this, true)

        btnBack = findViewById(R.id.btn_back)
        tvTitle = findViewById(R.id.tv_title)
        btnRight = findViewById(R.id.btn_right)

        btnBack.setOnClickListener { onBackClick?.invoke() }
        btnRight.setOnClickListener { onRightClick?.invoke() }
    }

    fun setTitle(title: String) {
        tvTitle.text = title
    }

    fun setRightIcon(resId: Int) {
        btnRight.setImageResource(resId)
        btnRight.visibility = View.VISIBLE
    }
}
```

### 21.3 钢琴键盘（多点触控）

```text
class PianoView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    // 琴键区域
    private val whiteKeys = mutableListOf<RectF>()
    private val blackKeys = mutableListOf<RectF>()

    // 按键状态
    private val pressedKeys = mutableSetOf<Int>()

    // 音效相关（需配合 SoundPool）
    // private val soundPool: SoundPool = ...
    // private val keySounds = IntArray(14)

    private val whiteKeyPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.WHITE
    }

    private val blackKeyPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.BLACK
    }

    private val pressedPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.FILL
        color = Color.parseColor("#FF5722")
    }

    private val strokePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        color = Color.BLACK
        strokeWidth = 2f
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        initKeys(w, h)
    }

    private fun initKeys(w: Int, h: Int) {
        whiteKeys.clear()
        blackKeys.clear()

        val whiteKeyWidth = w / 7f
        val whiteKeyHeight = h.toFloat()

        // 7 个白键
        for (i in 0..6) {
            whiteKeys.add(RectF(
                i * whiteKeyWidth, 0f,
                (i + 1) * whiteKeyWidth, whiteKeyHeight
            ))
        }

        // 5 个黑键
        val blackKeyWidth = whiteKeyWidth * 0.6f
        val blackKeyHeight = h * 0.6f
        val blackKeyPositions = listOf(0, 1, 3, 4, 5) // 黑键位置

        for (i in blackKeyPositions) {
            blackKeys.add(RectF(
                i * whiteKeyWidth + whiteKeyWidth - blackKeyWidth / 2,
                0f,
                i * whiteKeyWidth + whiteKeyWidth + blackKeyWidth / 2,
                blackKeyHeight
            ))
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN, MotionEvent.ACTION_POINTER_DOWN -> {
                val keyIndex = getKeyIndex(event.getX(event.actionIndex), event.getY(event.actionIndex))
                if (keyIndex >= 0) {
                    pressedKeys.add(keyIndex)
                    playSound(keyIndex)
                    invalidate()
                }
            }
            MotionEvent.ACTION_MOVE -> {
                val nextKeys = mutableSetOf<Int>()
                for (i in 0 until event.pointerCount) {
                    val keyIndex = getKeyIndex(event.getX(i), event.getY(i))
                    if (keyIndex >= 0) nextKeys.add(keyIndex)
                }
                (nextKeys - pressedKeys).forEach { playSound(it) }
                pressedKeys.clear()
                pressedKeys.addAll(nextKeys)
                invalidate()
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_POINTER_UP -> {
                val pointerIndex = event.actionIndex
                // pointerIndex 指示离开的指针，不是琴键编号；不与 pressedKeys 比较。
                // 检查其他手指是否按在其他键上
                pressedKeys.clear()
                for (i in 0 until event.pointerCount) {
                    if (i != pointerIndex) {
                        val keyIndex = getKeyIndex(event.getX(i), event.getY(i))
                        if (keyIndex >= 0) pressedKeys.add(keyIndex)
                    }
                }
                invalidate()
            }
            MotionEvent.ACTION_CANCEL -> {
                pressedKeys.clear()
                invalidate()
            }
        }
        return true
    }

    private fun getKeyIndex(x: Float, y: Float): Int {
        // 先检查黑键（上层）
        for (i in blackKeys.indices) {
            if (blackKeys[i].contains(x, y)) return i + 7
        }
        // 再检查白键（下层）
        for (i in whiteKeys.indices) {
            if (whiteKeys[i].contains(x, y)) return i
        }
        return -1
    }

    private fun playSound(keyIndex: Int) {
        // soundPool.play(keySounds[keyIndex], 1f, 1f, 1, 0, 1f)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        // 绘制白键
        for (i in whiteKeys.indices) {
            val rect = whiteKeys[i]
            val paint = if (i in pressedKeys) pressedPaint else whiteKeyPaint
            canvas.drawRect(rect, paint)
            canvas.drawRect(rect, strokePaint)
        }

        // 绘制黑键
        for (i in blackKeys.indices) {
            val rect = blackKeys[i]
            val paint = if ((i + 7) in pressedKeys) pressedPaint else blackKeyPaint
            canvas.drawRect(rect, paint)
        }
    }
}
```

---

## 22. 完整知识体系总结

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    自定义 View 完整知识体系                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. 基础绘制                                                               │
│   - Drawable 资源 (Shape, Layer, Selector, Vector)                       │
│   - Canvas 绘制 (drawCircle, drawRect, drawPath)                         │
│   - Paint 画笔 (样式、效果、渐变)                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. 绘制流程                                                               │
│   - Measure (MeasureSpec, onMeasure, wrap_content)                        │
│   - Layout (onLayout, 子 View 定位)                                       │
│   - Draw (draw, onDraw, dispatchDraw)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. 进阶技能                                                               │
│   - Canvas 变换 (translate, rotate, scale, clip)                         │
│   - 混合模式 (PorterDuff Xfermode)                                        │
│   - 自定义属性 (attrs.xml, obtainStyledAttributes)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. 事件处理                                                               │
│   - onTouchEvent, GestureDetector                                        │
│   - 滑动冲突 (onInterceptTouchEvent, requestDisallowInterceptTouchEvent) │
│   - 多点触控                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. 原理机制                                                               │
│   - Invalidate vs RequestLayout                                           │
│   - View.post() 获取宽高                                                  │
│   - 线程与 UI 更新                                                        │
│   - ViewGroup vs View                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 6. 性能优化                                                               │
│   - 减少 onDraw 中对象创建                                                │
│   - 硬件加速                                                              │
│   - clipRect 减少过度绘制                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 总结

本文档涵盖了 Android 自定义 View 的完整知识体系，包括：

1. **Drawable 资源** - ShapeDrawable、LayerList、Selector、VectorDrawable
2. **View 绘制流程** - Measure、Layout、Draw 三大流程
3. **Canvas 画布** - 绘制、变换、裁剪、混合模式
4. **Paint 画笔** - 阴影、渐变、路径效果
5. **LayoutInflater** - 布局解析流程
6. **核心方法** - onMeasure、onLayout、onDraw
7. **自定义属性** - 声明、解析、使用
8. **事件处理** - TouchEvent、GestureDetector、多点触控
9. **实战案例** - 圆形进度条、组合标题栏、钢琴键盘
10. **性能优化** - 减少创建、硬件加速、防过度绘制
