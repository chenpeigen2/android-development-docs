# Android 自定义 View 绘制完全指南

> 作者：OpenClaw | 日期：2026-03-08

---

## 目录

1. [概述](#1-概述)
2. [Drawable 资源体系](#2-drawable-资源体系)
   - 2.1 [Drawable 体系概述](#21-drawable-体系概述)
   - 2.2 [ShapeDrawable 形状绘制](#22-shapedrawable-形状绘制)
   - 2.3 [LayerListDrawable 层叠绘制](#23-layerlistdrawable-层叠绘制)
   - 2.4 [SelectorDrawable 状态选择器](#24-selectordrawable-状态选择器)
   - 2.5 [VectorDrawable 矢量图形](#25-vectordrawable-矢量图形)
   - 2.6 [代码中创建 Drawable](#26-代码中创建-drawable)
3. [View 绘制三大流程](#3-view-绘制三大流程)
   - 3.1 [流程概述](#31-流程概述)
   - 3.2 [Measure 测量阶段](#32-measure-测量阶段)
   - 3.3 [Layout 布局阶段](#33-layout-布局阶段)
   - 3.4 [Draw 绘制阶段](#34-draw-绘制阶段)
4. [Canvas 画布详解](#4-canvas-画布详解)
   - 4.1 [Canvas 核心功能](#41-canvas-核心功能)
   - 4.2 [Canvas 基础绘制](#42-canvas-基础绘制)
   - 4.3 [Canvas 变换操作](#43-canvas-变换操作)
   - 4.4 [Canvas 裁剪操作](#44-canvas-裁剪操作)
   - 4.5 [Path 高级绘制](#45-path-高级绘制)
5. [Paint 画笔与效果](#5-paint-画笔与效果)
   - 5.1 [Paint 核心属性](#51-paint-核心属性)
   - 5.2 [Paint 高级效果](#52-paint-高级效果)
   - 5.3 [Xfermode 混合模式](#53-xfermode-混合模式)
   - 5.4 [PathEffect 路径效果](#54-patheffect-路径效果)
6. [渐变与色彩](#6-渐变与色彩)
   - 6.1 [渐变类型详解](#61-渐变类型详解)
   - 6.2 [颜色工具](#62-颜色工具)
7. [自定义 View 实战](#7-自定义-view-实战)
   - 7.1 [自定义属性](#71-自定义属性)
   - 7.2 [完整示例：圆形进度条](#72-完整示例圆形进度条)
8. [性能优化](#8-性能优化)
   - 8.1 [绘制优化原则](#81-绘制优化原则)
   - 8.2 [最佳实践](#82-最佳实践)
9. [LayoutInflater 流程](#9-layoutinflater-流程)
   - 9.1 [Inflation 完整流程](#91-inflation-完整流程)
   - 9.2 [inflate() 方法解析](#92-inflate-方法解析)
   - 9.3 [注意事项](#93-注意事项)
10. [Merge、Include 与 ViewStub](#10-mergeinclude-与-viewstub)
    - 10.1 [merge 标签](#101-merge-标签)
    - 10.2 [include 标签](#102-include-标签)
    - 10.3 [ViewStub 标签](#103-viewstub-标签)
11. [Invalidate 与 RequestLayout](#11-invalidate-与-requestlayout)
    - 11.1 [Invalidate - 重绘](#111-invalidate---重绘)
    - 11.2 [RequestLayout - 重新布局](#112-requestlayout---重新布局)
    - 11.3 [两者对比与选择](#113-两者对比与选择)
    - 11.4 [forceLayout()](#114-forcelayout)
12. [Draw 流程源码解析](#12-draw-流程源码解析)
    - 12.1 [View.draw() 源码流程](#121-viewdraw-源码流程)
    - 12.2 [DecorView.draw() 特殊流程](#122-decorviewdraw-特殊流程)
    - 12.3 [ViewGroup.drawChild() 源码详解](#123-viewgroupdrawchild-源码详解)
    - 12.4 [绘制顺序控制](#124-绘制顺序控制)
13. [Canvas 高级用法](#13-canvas-高级用法)
    - 13.1 [Canvas Save/Restore 详解](#131-canvas-saverestore-详解)
    - 13.2 [Canvas saveLayer 详解](#132-canvas-savelayer-详解)
    - 13.3 [Canvas 裁剪高级用法](#133-canvas-裁剪高级用法)
    - 13.4 [PorterDuff 混合模式](#134-porterduff-混合模式)
14. [View 与 ViewGroup 区别](#14-view-与-viewgroup-区别)
    - 14.1 [核心区别](#141-核心区别)
    - 14.2 [setWillNotDraw()](#142-setwillnotdraw)
    - 14.3 [ViewGroup 绘制相关方法](#143-viewgroup-绘制相关方法)
15. [wrap_content 不生效问题](#15-wrap_content-不生效问题)
    - 15.1 [问题原因](#151-问题原因)
    - 15.2 [解决方案](#152-解决方案)
16. [获取 View 宽高的正确时机](#16-获取-view-宽高的正确时机)
    - 16.1 [onResume 中获取宽高返回 0](#161-onresume-中获取宽高返回-0)
    - 16.2 [View.post() 原理详解](#162-viewpost-原理详解)
    - 16.3 [其他正确方式](#163-其他正确方式)
17. [线程与 UI 更新](#17-线程与-ui-更新)
    - 17.1 [子线程不能更新 UI 的原因](#171-子线程不能更新-ui-的原因)
    - 17.2 [更新 UI 的正确方式](#172-更新-ui-的正确方式)
    - 17.3 [SurfaceView 特殊情况](#173-surfaceview-特殊情况)
18. [width/height 区别](#18-widthheight-区别)
    - 18.1 [区别](#181-区别)
    - 18.2 [两者不一致的情况](#182-两者不一致的情况)
19. [根视图的多次 Measure](#19-根视图的多次-measure)
    - 19.1 [多次 Measure 的原因](#191-多次-measure-的原因)
    - 19.2 [源码流程](#192-源码流程)
    - 19.3 [避免重复 Measure](#193-避免重复-measure)
20. [自定义 View 类型与分类](#20-自定义-view-类型与分类)
    - 20.1 [自定义 View 类型](#201-自定义-view-类型)
21. [核心生命周期方法详解](#21-核心生命周期方法详解)
    - 21.1 [三大方法对比](#211-三大方法对比)
    - 21.2 [MeasureSpec 三种模式处理](#212-measurespec-三种模式处理)
    - 21.3 [处理 wrap_content 和 padding](#213-处理-wrap_content-和-padding)
22. [自定义属性详解](#22-自定义属性详解)
    - 22.1 [属性声明](#221-属性声明)
    - 22.2 [属性解析](#222-属性解析)
    - 22.3 [属性优先级](#223-属性优先级)
    - 22.4 [在 XML 中使用](#224-在-xml-中使用)
23. [事件处理与交互](#23-事件处理与交互)
    - 23.1 [onTouchEvent](#231-ontouchevent)
    - 23.2 [GestureDetector 手势处理](#232-gesturedetector-手势处理)
    - 23.3 [滑动冲突解决](#233-滑动冲突解决)
    - 23.4 [多点触控](#234-多点触控)
24. [实战案例](#24-实战案例)
    - 24.1 [圆形进度条](#241-圆形进度条)
    - 24.2 [组合标题栏](#242-组合标题栏)
    - 24.3 [钢琴键盘（多点触控）](#243-钢琴键盘多点触控)
25. [完整知识体系总结](#25-完整知识体系总结)
   - 3.4 [Draw 绘制阶段](#34-draw-绘制阶段)
4. [Canvas 画布详解](#4-canvas-画布详解)
   - 4.1 [Canvas 核心功能](#41-canvas-核心功能)
   - 4.2 [Canvas 基础绘制](#42-canvas-基础绘制)
   - 4.3 [Canvas 变换操作](#43-canvas-变换操作)
   - 4.4 [Canvas 裁剪操作](#44-canvas-裁剪操作)
   - 4.5 [Path 高级绘制](#45-path-高级绘制)
5. [Paint 画笔与效果](#5-paint-画笔与效果)
   - 5.1 [Paint 核心属性](#51-paint-核心属性)
   - 5.2 [Paint 高级效果](#52-paint-高级效果)
   - 5.3 [Xfermode 混合模式](#53-xfermode-混合模式)
   - 5.4 [PathEffect 路径效果](#54-patheffect-路径效果)
6. [渐变与色彩](#6-渐变与色彩)
   - 6.1 [渐变类型详解](#61-渐变类型详解)
   - 6.2 [颜色工具](#62-颜色工具)
7. [自定义 View 实战](#7-自定义-view-实战)
   - 7.1 [自定义属性](#71-自定义属性)
   - 7.2 [完整示例：圆形进度条](#72-完整示例圆形进度条)
8. [性能优化](#8-性能优化)
   - 8.1 [绘制优化原则](#81-绘制优化原则)
   - 8.2 [最佳实践](#82-最佳实践)
9. [LayoutInflater 流程](#9-layoutinflater-流程)
   - 9.1 [Inflation 完整流程](#91-inflation-完整流程)
   - 9.2 [inflate() 方法解析](#92-inflate-方法解析)
   - 9.3 [注意事项](#93-注意事项)
10. [Merge、Include 与 ViewStub](#10-mergeinclude-与-viewstub)
    - 10.1 [merge 标签](#101-merge-标签)
    - 10.2 [include 标签](#102-include-标签)
    - 10.3 [ViewStub 标签](#103-viewstub-标签)
11. [Invalidate 与 RequestLayout](#11-invalidate-与-requestlayout)
    - 11.1 [Invalidate - 重绘](#111-invalidate---重绘)
    - 11.2 [RequestLayout - 重新布局](#112-requestlayout---重新布局)
    - 11.3 [两者对比与选择](#113-两者对比与选择)
    - 11.4 [forceLayout()](#114-forcelayout)
12. [Draw 流程源码解析](#12-draw-流程源码解析)
    - 12.1 [View.draw() 源码流程](#121-viewdraw-源码流程)
    - 12.2 [DecorView.draw() 特殊流程](#122-decorviewdraw-特殊流程)
    - 12.3 [ViewGroup.drawChild() 源码详解](#123-viewgroupdrawchild-源码详解)
    - 12.4 [绘制顺序控制](#124-绘制顺序控制)
13. [Canvas 高级用法](#13-canvas-高级用法)
    - 13.1 [Canvas Save/Restore 详解](#131-canvas-saverestore-详解)
    - 13.2 [Canvas saveLayer 详解](#132-canvas-savelayer-详解)
    - 13.3 [Canvas 裁剪高级用法](#133-canvas-裁剪高级用法)
    - 13.4 [PorterDuff 混合模式](#134-porterduff-混合模式)
14. [View 与 ViewGroup 区别](#14-view-与-viewgroup-区别)
    - 14.1 [核心区别](#141-核心区别)
    - 14.2 [setWillNotDraw()](#142-setwillnotdraw)
    - 14.3 [ViewGroup 绘制相关方法](#143-viewgroup-绘制相关方法)
15. [wrap_content 不生效问题](#15-wrap_content-不生效问题)
    - 15.1 [问题原因](#151-问题原因)
    - 15.2 [解决方案](#152-解决方案)
16. [获取 View 宽高的正确时机](#16-获取-view-宽高的正确时机)
    - 16.1 [onResume 中获取宽高返回 0](#161-onresume-中获取宽高返回-0)
    - 16.2 [View.post() 原理详解](#162-viewpost-原理详解)
    - 16.3 [其他正确方式](#163-其他正确方式)
17. [线程与 UI 更新](#17-线程与-ui-更新)
    - 17.1 [子线程不能更新 UI 的原因](#171-子线程不能更新-ui-的原因)
    - 17.2 [更新 UI 的正确方式](#172-更新-ui-的正确方式)
    - 17.3 [SurfaceView 特殊情况](#173-surfaceview-特殊情况)
18. [width/height 与 measuredWidth/measuredHeight](#18-widthheight-与-measuredwidthmeasuredheight)
    - 18.1 [区别](#181-区别)
    - 18.2 [两者不一致的情况](#182-两者不一致的情况)
19. [根视图的多次 Measure](#19-根视图的多次-measure)
    - 19.1 [多次 Measure 的原因](#191-的原因)
   -多次-measure - 19.2 [源码流程](#192-源码流程)
    - 19.3 [避免重复 Measure](#193-避免重复-measure)
20. [自定义 View 类型与分类](#20-自定义-view-类型与分类)
    - 20.1 [继承 View 类](#201-继承-view-类)
    - 20.2 [组合控件](#202-组合控件)
    - 20.3 [继承 ViewGroup](#203-继承-viewgroup)
21. [核心生命周期方法详解](#21-核心生命周期方法详解)
    - 21.1 [三大方法对比](#211-三大方法对比)
    - 21.2 [MeasureSpec 三种模式处理](#212-measurespec-三种模式处理)
    - 21.3 [处理 wrap_content 和 padding](#213-处理-wrap_content-和-padding)
22. [自定义属性详解](#22-自定义属性详解)
    - 22.1 [属性声明](#221-属性声明)
    - 22.2 [属性解析](#222-属性解析)
    - 22.3 [属性优先级](#223-属性优先级)
    - 22.4 [在 XML 中使用](#224-在-xml-中使用)
23. [事件处理与交互](#23-事件处理与交互)
    - 23.1 [onTouchEvent](#231-ontouchevent)
    - 23.2 [GestureDetector 手势处理](#232-gesturedetector-手势处理)
    - 23.3 [滑动冲突解决](#233-滑动冲突解决)
    - 23.4 [多点触控](#234-多点触控)
24. [实战案例](#24-实战案例)
    - 24.1 [圆形进度条](#241-圆形进度条)
    - 24.2 [组合标题栏](#242-组合标题栏)
    - 24.3 [钢琴键盘（多点触控）](#243-钢琴键盘多点触控)
25. [完整知识体系总结](#25-完整知识体系总结)
26. [总结](#总结)

---

## 1. 概述

自定义 View 是 Android 开发的核心技能之一。一个优秀的自定义 View 需要掌握以下知识体系：

```
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

```
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

```
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
| requestLayout() | Measure + Layout |
| invalidate() | Draw |
| requestFocus() | Draw |

### 3.2 Measure 测量阶段

#### 3.2.1 MeasureSpec 测量规格

```kotlin
/**
 * MeasureSpec = MeasureSpec.makeMeasureSpec(size, mode)
 *
 * 模式 (Mode):
 * - EXACTLY: 精确值 (match_parent, 固定值)
 * - AT_MOST: 最大值 (wrap_content)
 * - UNSPECIFIED: 无限制
 */
object MeasureSpec {
    const val UNSPECIFIED = 0
    const val EXACTLY = 1
    const val AT_MOST = 2
}
```

**测量模式速查：**

| 父容器属性 | MeasureSpec |
|-----------|-------------|
| `match_parent` | EXACTLY + parentSize |
| `wrap_content` | AT_MOST + parentSize |
| 固定 `100dp` | EXACTLY + 100dp |

#### 3.2.2 onMeasure 核心逻辑

```kotlin
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val DEFAULT_WIDTH = 200.dp2px()
    private val DEFAULT_HEIGHT = 200.dp2px()

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)

        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)
        val heightMode = MeasureSpec.getMode(heightMeasureSpec)
        val heightSize = MeasureSpec.getSize(heightMeasureSpec)

        var resultWidth = DEFAULT_WIDTH
        var resultHeight = DEFAULT_HEIGHT

        when (widthMode) {
            MeasureSpec.EXACTLY -> resultWidth = widthSize
            MeasureSpec.AT_MOST -> resultWidth = minOf(DEFAULT_WIDTH, widthSize)
            MeasureSpec.UNSPECIFIED -> resultWidth = DEFAULT_WIDTH
        }

        when (heightMode) {
            MeasureSpec.EXACTLY -> resultHeight = heightSize
            MeasureSpec.AT_MOST -> resultHeight = minOf(DEFAULT_HEIGHT, heightSize)
            MeasureSpec.UNSPECIFIED -> resultHeight = DEFAULT_HEIGHT
        }

        setMeasuredDimension(resultWidth, resultHeight)
    }

    private fun Int.dp2px(): Int = (this * resources.displayMetrics.density).toInt()
}
```

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

// ✅ 正确：使用 post
view.post { val w = width }
```

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

```kotlin
/**
 * View 绘制流程
 */
class CustomView : View {

    override fun draw(canvas: Canvas) {
        // 1. 绘制背景
        super.draw(canvas)

        // 2. 绘制内容
        onDraw(canvas)

        // 3. 分发绘制给子 View (仅 ViewGroup)
        dispatchDraw(canvas)

        // 4. 绘制装饰
        onDrawForeground(canvas)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // 在这里绘制自定义内容
    }
}
```

---

## 4. Canvas 画布详解

### 4.1 Canvas 核心功能

```
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

```
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

  1. 需要关闭硬件加速
     ─────────────────────────────────────────────────────────────────────────
     setLayerType(LAYER_TYPE_SOFTWARE, null);
     // 或者在 AndroidManifest 中关闭硬件加速

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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BlurMaskFilter 详解                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  BlurMaskFilter 提供更多模糊效果，是 setShadowLayer 的更强大版本

  模糊类型：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────┬─────────────────────────────────────────────────┐
  │ 类型                 │ 效果                                           │
  ├─────────────────────┼─────────────────────────────────────────────────┤
  │ Blur.NORMAL         │ 内外都模糊                                       │
  │ Blur.SOLID          │ 内部正常，外部模糊（类似浮雕）                    │
  │ Blur.OUTER          │ 仅外部模糊，内部透明                              │
  │ Blur.INNER          │ 仅内部模糊                                       │
  └─────────────────────┴─────────────────────────────────────────────────┘

  使用示例：
  ─────────────────────────────────────────────────────────────────────────────

  val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
      color = Color.BLUE
      // 创建模糊遮罩
      maskFilter = BlurMaskFilter(20f, BlurMaskFilter.Blur.NORMAL)
  }

  // 绘制文字
  paint.textSize = 60f
  canvas.drawText("发光文字", 100f, 200f, paint)

  // 绘制图形
  canvas.drawCircle(200f, 300f, 80f, paint)

  结合 setShadowLayer：
  ─────────────────────────────────────────────────────────────────────────────

  val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
      // 阴影（需要关闭硬件加速）
      setShadowLayer(10f, 5f, 5f, Color.parseColor("#40000000"))
      
      // 模糊效果（不需要关闭硬件加速）
      maskFilter = BlurMaskFilter(15f, BlurMaskFilter.Blur.NORMAL)
  }

  注意：setShadowLayer 和 maskFilter 不能同时使用！后设置的有效
```

#### 5.2.3 View 的 elevation 和 translationZ

```
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

```
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
  ─────────────────────────────────────────────────────────────────────────────
  推荐：translationZ + 属性动画
  
  view.animate()
      .translationZ(20f)
      .setDuration(150)
      .withEndAction {
          view.translationZ = 0f  // 恢复
      }
      .start()

  场景 5：拖拽时提升层级
  ─────────────────────────────────────────────────────────────────────────────
  推荐：translationZ
  
  // 拖拽开始
  draggedView.translationZ = 50f
  
  // 拖拽结束
  draggedView.translationZ = 0f

  场景 6：复杂形状阴影
  ─────────────────────────────────────────────────────────────────────────────
  推荐：ViewOutlineProvider + elevation
  
  outline.setRoundRect(...)  // 自定义阴影形状
```

### 5.4 PathEffect 路径效果

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

### 5.5 PathEffect 路径效果

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

### 8.1 绘制优化原则

```
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
   - 使用硬件层 (setLayerType)
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

```
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

```
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

```
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

```
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

### 11.1 Invalidate - 重绘

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Invalidate 流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │  invalidate()   │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │  View.invalidate()       │
                    │  (带参数: dirty 区域)    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │  invalidate(true/false) │
                    │  - true: 整个 View      │
                    │  - false: 仅 dirty 区域 │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │  mParent.invalidateChild │
                    │  (递归向上直到 ViewRoot) │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │  ViewRootImpl             │
                    │  .invalidateChildInParent│
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │  scheduleTraversals()    │
                    │  (请求 VSync 信号)       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │  Choreographer           │
                    │  .postCallback()        │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │      VSync 信号触发      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │  doTraversal()           │
                    │  → performDraw()         │
                    │  → draw()                │
                    │  → onDraw()              │
                    └───────────────────────────┘
```

**源码详解：**

```kotlin
// View.invalidate() 核心实现
public void invalidate() {
    invalidate(true);
}

public void invalidate(boolean invalidateCache) {
    // 1. 检查是否在主线程
    if (ViewDebug.DEBUG_INVARIANT_LEVELS) {
        checkThread();
    }

    // 2. 只有可见的 View 才重绘
    if ((mPrivateFlags & (DRAWN | DRAWN_MASK)) == 0 ||
        (mPrivateFlags & DRAWING_CACHE_VALID) == 0 ||
        (invalidateCache && mCachingFailed)) {

        // 3. 设置标志位
        mPrivateFlags |= DRAWN;
        mPrivateFlags &= ~DRAWING_CACHE_VALID;
        mPrivateFlags |= mCachingFailed ? 0 : DRAWN_MASK;

        // 4. 递归向上通知父 View
        if (mParent != null) {
            mParent.invalidateChild(this, dirty);
        }
    }
}

// ViewGroup.invalidateChild()
public final void invalidateChild(View child, final DirtyRect dirty) {
    final AttachInfo attachInfo = mAttachInfo;
    if (attachInfo != null && mViewFlags != VISIBLE) {
        return; // 不可见直接返回
    }

    // 转换 dirty 坐标到父容器坐标系
    final int[] location = attachInfo.mInvalidateChildLocation;
    location[CHILD_LEFT_INDEX] = child.mLeft;
    location[CHILD_TOP_INDEX] = child.mTop;

    // 递归向上
    if ((child.mPrivateFlags & DRAWN) == 0) {
        child.mPrivateFlags |= DRAWN;
    }

    do {
        View parent = this;
        // 坐标变换
        dirty.offset(location[CHILD_LEFT_INDEX], location[CHILD_TOP_INDEX]);

        // 父容器也需要重绘
        if ((parent.mViewFlags & FADING_EDGE_MASK) != 0 ||
            parent.mCacheBitmap != null) {
            parent.mPrivateFlags |= DRAWN;
        }

        parent = parent.mParent;
    } while (parent != null);

    // 最终通知 ViewRootImpl
    attachInfo.mViewRootImpl.invalidate();
}
```

**Invalidate 注意事项：**

```kotlin
// 1. 在主线程调用
// ❌ 子线程调用会崩溃
Thread {
    view.invalidate() // 抛出异常
}.start()

// 2. View 必须可见且已 attached
// ❌ 不可见时不生效
view.visibility = View.INVISIBLE
view.invalidate() // 无效

// 3. 可以指定重绘区域（局部刷新）
view.post {
    // 只重绘左侧区域
    view.invalidate(0, 0, view.width / 2, view.height)
}

// 4. 设置标志位组合
// DRAWN: 已绘制
// DRAWING_CACHE_VALID: 缓存有效
// DRAWN_MASK: 绘制掩码
```

**特点：**
- 只触发 **Draw** 流程（不重新 Measure 和 Layout）
- 效率较高，支持局部刷新
- 必须在主线程调用

```kotlin
// invalidate() 使用场景
// 1. 修改了需要绘制的数据
// 2. 颜色、状态变化
// 3. 动画过程中
// 4. 自定义 View 更新显示内容

fun updateProgress(progress: Int) {
    this.progress = progress
    invalidate() // 只重绘，不需要重新测量布局
}
```

### 11.2 RequestLayout - 重新布局

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RequestLayout 流程                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────────┐
                         │   requestLayout()   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │  View.requestLayout()          │
                    │  1. 检查线程                    │
                    │  2. 清除布局缓存                 │
                    │  3. 向上递归                    │
                    └────────────┬────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────────┐
                    │  mParent.requestLayout()        │
                    │  (递归向上直到 ViewRoot)        │
                    └────────────┬────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────────┐
                    │  ViewRootImpl.requestLayout()   │
                    │  mLayoutRequested = true        │
                    └────────────┬────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────────┐
                    │  scheduleTraversals()           │
                    │  (请求 VSync，触发完整遍历)    │
                    └────────────┬────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │      VSync 信号触发      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────────┐
                    │  doTraversal()                 │
                    │                                 │
                    │  ┌───────────────────────────┐ │
                    │  │ performMeasure()          │ │
                    │  │   重新测量所有 View       │ │
                    │  └────────────┬──────────────┘ │
                    │               │                │
                    │               ▼                │
                    │  ┌───────────────────────────┐ │
                    │  │ performLayout()          │ │
                    │  │   重新布局所有 View      │ │
                    │  └────────────┬──────────────┘ │
                    │               │                │
                    │               ▼                │
                    │  ┌───────────────────────────┐ │
                    │  │ performDraw()            │ │
                    │  │   重新绘制所有 View      │ │
                    │  └───────────────────────────┘ │
                    └─────────────────────────────────┘
```

**源码详解：**

```kotlin
// View.requestLayout() 核心实现
public void requestLayout() {
    // 1. 检查线程
    if (ViewDebug.DEBUG_INVARIANT_LEVELS) {
        checkThread();
    }

    // 2. 清除布局缓存标志
    mPrivateFlags &= ~DRAWN;
    mPrivateFlags |= DRAWN_MASK;

    // 3. 标记需要重新布局
    mPrivateFlags |= FORCE_LAYOUT;
    mPrivateFlags |= INVALIDATED;

    // 4. 向上递归通知父容器
    if (mParent != null) {
        mParent.requestLayout();
    }
}

// ViewRootImpl.requestLayout()
public void requestLayout() {
    if (!mHandlingLayoutInEditMode) {
        // 检查是否在主线程
        if (Thread.currentThread() == mThread) {
            // 直接调度遍历
            scheduleTraversals();
        } else {
            // 发送到主线程
            mHandler.post(mTraversalRunnable);
        }
    }
}

// mTraversalRunnable
final TraversalRunnable mTraversalRunnable = new TraversalRunnable();

class TraversalRunnable implements Runnable {
    @Override
    public void run() {
        doTraversal();
    }
}

void doTraversal() {
    // 完整的三流程
    performMeasure(mWidth, mHeight);
    performLayout(lp, mWidth, mHeight);
    performDraw();
}
```

**触发 RequestLayout 的场景：**

```kotlin
// 1. 尺寸变化
textView.text = "很长很长的文本..." // 高度可能变化
imageView.setImageBitmap(bitmap) // 尺寸变化

// 2. 布局参数变化
val params = view.layoutParams as ViewGroup.MarginLayoutParams
params.width = ViewGroup.LayoutParams.MATCH_PARENT
view.layoutParams = params // 会触发 requestLayout

// 3. 添加/移除子 View
parentView.addView(childView)
parentView.removeView(childView)

// 4. 调用 setLayoutParams()
view.setLayoutParams(newLayoutParams)

// 5. View.forceLayout() 强制重新布局
view.forceLayout()
view.requestLayout()
```

**⚠️ 注意事项：**

```kotlin
// ❌ 错误：onDraw 中调用 requestLayout
override fun onDraw(canvas: Canvas) {
    requestLayout() // 会导致无限循环！每次 draw 都会 requestLayout
}

// ✅ 正确：在数据变化时调用
fun setNewData(newData: List<String>) {
    this.data = newData
    requestLayout() // 尺寸可能变化
    invalidate()   // 内容也变化
}

// ⚠️ 连锁反应
// requestLayout() 会触发整个 View 树的重新 measure + layout + draw
// 性能开销较大，频繁调用会影响性能
```

### 11.3 两者对比与选择

| 对比项 | invalidate() | requestLayout() |
|--------|-------------|-----------------|
| **触发流程** | Draw | Measure + Layout + Draw |
| **性能** | 高（只重绘） | 低（完整遍历） |
| **使用场景** | 内容/颜色/动画变化 | 尺寸/布局参数变化 |
| **调用频率** | 可高频调用 | 避免频繁调用 |
| **局部刷新** | 支持（dirty region） | 不支持（全树） |

**选择原则：**

```kotlin
// ✅ 用 invalidate() 的场景
fun updateColor(color: Int) {
    this.color = color
    invalidate() // 颜色变化，只需要重绘
}

fun animateProgress(progress: Float) {
    this.progress = progress
    invalidate() // 动画过程中持续重绘
}

// ✅ 用 requestLayout() 的场景
fun setNewImage(bitmap: Bitmap) {
    this.bitmap = bitmap
    requestLayout() // 图片尺寸变化，需要重新测量
    invalidate()   // 也需要重绘内容
}

fun updateMargin(leftMargin: Int) {
    val params = layoutParams as ViewGroup.MarginLayoutParams
    params.leftMargin = leftMargin
    layoutParams = params // 自动触发 requestLayout
}

// ⚠️ 两者都需要的场景
fun updateContent(newContent: String, newWidth: Int) {
    this.content = newContent
    requestLayout() // 文本变化，宽度变化
    invalidate()   // 内容变化，需要重绘
}
```

### 11.4 forceLayout() 强制重新布局

```kotlin
/**
 * forceLayout() - 强制标记 View 需要重新布局
 *
 * 与 requestLayout() 的区别：
 * - requestLayout(): 向上递归，通知父容器重新布局
 * - forceLayout(): 只标记当前 View，强制在下次布局时重新测量
 */

// 使用场景：已知尺寸需要变化
view.forceLayout()
view.requestLayout() // 两者配合使用

// 或者只标记，依赖父容器的 requestLayout 触发
view.forceLayout()
parent.requestLayout() // 父容器触发时会强制测量子 View
```

---

## 12. Draw 流程源码解析

### 12.1 View.draw() 源码流程

```kotlin
/**
 * View.draw() 完整流程
 */
public void draw(Canvas canvas) {
    // Step 1: 绘制背景
    // 绘制 View 的背景（通常在 onDraw 之前）
    drawBackground(canvas);

    // Step 2: 绘制主体内容
    // 子类重写此方法实现自定义绘制
    onDraw(canvas);

    // Step 3: 绘制子 View (仅 ViewGroup)
    // ViewGroup 重写，分发给子 View 绘制
    dispatchDraw(canvas);

    // Step 4: 绘制装饰
    // 滚动条、前景等
    onDrawForeground(canvas);
}

// draw() 完整源码简化
public void draw(Canvas canvas) {
    // 1. 绘制背景
    if (!dirtyOpaque) {
        drawBackground(canvas);
    }

    // 2. 绘制内容
    if (!dirtyOpaque) {
        onDraw(canvas);
    }

    // 3. 绘制滚动条等装饰
    onDrawForeground(canvas);

    // 4. 对于 ViewGroup，分发绘制子 View
    // (由 ViewGroup 重写)
}
```

### 12.2 DecorView.draw() 特殊流程

```kotlin
/**
 * DecorView 是 Activity 的根 View，继承自 FrameLayout
 * 绘制流程有特殊处理
 */
public class DecorView extends FrameLayout {

    private Drawable mWindowBackground;

    @Override
    public void draw(Canvas canvas) {
        // 1. 先调用父类 FrameLayout 的 draw
        super.draw(canvas);

        // 2. 额外绘制：Window 背景
        // 这是 Activity 窗口背景，通常是一张图片或颜色
        if (mWindowBackground != null) {
            mWindowBackground.draw(canvas);
        }
    }
}

/**
 * Activity 窗口背景设置流程
 */
public void setContentView(int resId) {
    // 1. 创建 DecorView
    // 2. 设置窗口背景
    getWindow().setBackgroundDrawable(new BitmapDrawable());
}
```

### 12.3 ViewGroup.drawChild() 源码详解

```kotlin
/**
 * ViewGroup.drawChild() - 绘制子 View
 *
 * 这是 ViewGroup 绘制子 View 的核心方法
 * 控制每个子 View 的绘制时机和方式
 */
protected boolean drawChild(Canvas canvas, View child, long drawingTime) {
    // 1. 保存当前 Canvas 状态
    // 每个子 View 都有独立的 Canvas 状态
    final int clipLeft = canvas.getSaveCount();

    // 2. 计算子 View 的渲染时间
    // 用于动画等基于时间的绘制
    child.mPrivateFlags |= DRAW_ANIMATION;

    // 3. 获取子 View 之前是否已计算过
    final boolean childDrawDone = child.mPrivateFlags & DRAW_COMPLETE;

    // 4. 清理子 View 的缓存标志
    child.mPrivateFlags &= ~DRAWING_CACHE_VALID;

    // 5. 执行子 View 的 draw() 方法
    // 传递 drawingTime 用于动画时间计算
    final boolean more = child.draw(canvas, drawingTime, true);

    // 6. 恢复 Canvas 状态
    // 确保子 View 的绘制不影响后续绘制
    canvas.restoreToCount(clipLeft);

    // 7. 如果子 View 正在动画，继续后续处理
    if (more) {
        // 动画相关处理
    }

    return more;
}

/**
 * drawChild 完整流程图
 */
┌─────────────────────────────────────────────────────────────────────────────┐
│                     drawChild 流程                                          │
└─────────────────────────────────────────────────────────────────────────────┘

     ViewGroup.drawChild(canvas, child, drawingTime)
                    │
                    ▼
     ┌─────────────────────────────────────────┐
     │ canvas.save()                           │
     │   保存当前 Canvas 状态                  │
     └────────────────┬────────────────────────┘
                    │
                    ▼
     ┌─────────────────────────────────────────┐
     │ 计算子 View 渲染参数                     │
     │   - drawingTime (动画时间)             │
     │   - mPrivateFlags 标志位               │
     └────────────────┬────────────────────────┘
                    │
                    ▼
     ┌─────────────────────────────────────────┐
     │ child.draw(canvas, drawingTime)         │
     │   调用子 View 的 draw 方法              │
     │   ├─ drawBackground()                  │
     │   ├─ onDraw()                          │
     │   ├─ dispatchDraw() (如果是 ViewGroup)│
     │   └─ onDrawForeground()                │
     └────────────────┬────────────────────────┘
                    │
                    ▼
     ┌─────────────────────────────────────────┐
     │ canvas.restoreToCount(clipLeft)         │
     │   恢复 Canvas 状态                      │
     └────────────────┬────────────────────────┘
                    │
                    ▼
               返回是否需要继续绘制
```

### 12.4 绘制顺序控制

```kotlin
/**
 * ViewGroup 默认绘制顺序：先添加的先绘制（底层）
 *
 * 控制绘制顺序的方式：
 */

// 方式1：复写 getChildDrawingOrder()
class CustomViewGroup : ViewGroup {

    // 启用自定义绘制顺序
    init {
        childrenDrawingOrderEnabled = true
    }

    override fun getChildDrawingOrder(childCount: Int, i: Int): Int {
        // 逆序绘制：最后面的先绘制
        return childCount - 1 - i
    }
}

// 方式2：使用 bringToFront() 改变 Z 轴顺序
childView1.bringToFront() // 移到最上层

// 方式3：控制子 View 添加顺序
// 先添加的在下面，后添加的在上面

// XML 中的控制
android:childrenDrawingOrderEnabled="true"
```

```xml
<!-- android:childrenDrawingOrderEnabled="true" -->
<!-- 复写 getChildDrawingOrder() 控制绘制顺序 -->

<!-- z-order 控制 -->
<!-- 1. 先添加的 View 在后面 (底层) -->
<!-- 2. bringToFront() 移到最前 -->
```

---

## 13. Canvas 高级用法

### 13.1 Canvas Save/Restore 详解 详解

```
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

```kotlin
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

```
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

```
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

```
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

```
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

```
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

```
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

```kotlin
class CustomViewGroup : ViewGroup {

    // 1. 绘制背景（默认会调用）
    override fun drawBackground(canvas: Canvas) {
        super.drawBackground(canvas)
    }

    // 2. 绘制自身内容
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        // ViewGroup 默认不执行这里，除非 setWillNotDraw(false)
    }

    // 3. 分发给子 View 绘制
    override fun dispatchDraw(canvas: Canvas) {
        super.dispatchDraw(canvas)
        // 在这里可以绘制子 View 上层的内容
    }

    // 4. 绘制前景
    override fun onDrawForeground(canvas: Canvas) {
        super.onDrawForeground(canvas)
    }
}
```

---

## 15. wrap_content 不生效问题

### 15.1 问题原因

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

### 15.2 解决方案

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

## 16. 获取 View 宽高的正确时机

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

```kotlin
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

## 17. 线程与 UI 更新

### 17.1 子线程不能更新 UI 的原因

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      为什么子线程不能更新 UI                                 │
└─────────────────────────────────────────────────────────────────────────────┘

1. View 不是线程安全的
   - UI 操作涉及复杂的状态管理
   - 并发访问会导致状态不一致

2. ViewRootImpl 检查线程
   - ViewRootImpl 在构造时绑定创建线程
   - 所有 UI 操作都会验证线程身份

3. Surface 不是线程安全的
   - UI 最终绘制到 Surface
   - 多线程绘制会导致画面撕裂

// ViewRootImpl 线程检查
void checkThread() {
    if (mThread != Thread.currentThread()) {
        throw new CalledFromWrongThreadException(
            "Only the original thread that created ViewRootImpl can touch its views"
        );
    }
}
```

### 17.2 更新 UI 的正确方式

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
    textView.text = "Crash!" // 会崩溃
}.start()
```

### 17.3 特殊情况：SurfaceView

```kotlin
/**
 * SurfaceView 可以在子线程绘制
 *
 * 原因：
 * 1. SurfaceView 有独立的 Surface
 * 2. Surface 在子线程创建和管理
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

## 18. width/height 区别

### 18.1 区别

```
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

### 18.2 两者不一致的情况

```kotlin
/**
 * 常见不一致场景：
 * 1. 父容器强制调整子 View 尺寸
 * 2. 自定义 ViewGroup 限制子 View
 * 3. 使用 MATCH_PARENT 但父容器空间不足
 */

class MyViewGroup : ViewGroup {

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // 强制限制子 View 尺寸
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            // 强制使用固定尺寸，不管子 View 的测量结果
            measureChild(child,
                MeasureSpec.makeMeasureSpec(100, MeasureSpec.EXACTLY),
                MeasureSpec.makeMeasureSpec(100, MeasureSpec.EXACTLY)
            )
        }
        setMeasuredDimension(500, 500)
    }
}

// 结果：child.measuredWidth = 子View计算的尺寸
//      child.width = 100 (被强制修改)
```

---

## 19. 根视图的多次 Measure

### 19.1 多次 Measure 的原因

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         根视图多次 Measure                                   │
└─────────────────────────────────────────────────────────────────────────────┘

为什么 ViewRootImpl 会多次 measure？

1. 第一次：获取初步尺寸
   - 尝试使用期望的尺寸进行布局

2. 第二次：根据布局结果调整
   - 如果子 View 使用 MATCH_PARENT
   - 需要根据可用空间重新计算

3. 特殊场景：
   - ScrollView 中的内容高度不确定
   - ConstraintLayout 的自动约束计算
   - 动态添加/删除子 View
```

### 19.2 源码流程

```kotlin
// ViewRootImpl.performMeasure() 简化流程

void performMeasure(int widthMeasureSpec, int heightMeasureSpec) {
    // 第一次 Measure
    mView.measure(widthMeasureSpec, heightMeasureSpec);

    // 检查是否需要重新 Measure
    // (例如：LayoutParams 变化)
    if (measureInvalidated) {
        // 第二次 Measure
        mView.measure(widthMeasureSpec, heightMeasureSpec);
    }
}

// 常见触发场景
// 1. TextView 内容变化 -> 重新测量
// 2. ViewStub 展开 -> 重新测量
// 3. 动态添加 View -> 父容器重新测量
```

### 19.3 避免重复 Measure

```kotlin
/**
 * 优化技巧：
 * 1. 在 onMeasure 中做缓存
 * 2. 使用 setMeasuredDimension 避免重复
 * 3. 合理使用 ViewGroup 的 children 缓存
 */

class OptimizedView : View {

    private var cachedWidth = 0
    private var cachedHeight = 0
    private var cacheValid = false

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // 检查是否可以使用缓存
        if (cacheValid) {
            setMeasuredDimension(cachedWidth, cachedHeight)
            return
        }

        // 实际测量
        // ... 测量逻辑 ...

        // 缓存结果
        cachedWidth = resultWidth
        cachedHeight = resultHeight
        cacheValid = true

        setMeasuredDimension(cachedWidth, cachedHeight)
    }

    // 数据变化时清除缓存
    fun setNewData(data: Any) {
        cacheValid = false
        requestLayout()
    }
}
```

---

## 20. 自定义 View 类型与分类

### 20.1 自定义 View 类型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         自定义 View 类型                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬─────────────────────────────────────────────────────┐
│       类型           │                      说明                           │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 继承 View 类        │ 用于基础绘制（如圆形、图表、刻度盘）                │
│                     │ 需要重写 onDraw() 实现自定义绘制                    │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 组合控件            │ 复用现有控件（如标题栏、搜索栏）                    │
│                     │ 通过 LayoutInflater 加载 XML 布局                  │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ 继承 ViewGroup      │ 管理子 View 布局（如流式布局、瀑布流）              │
│                     │ 需要处理 onMeasure() 和 onLayout()                │
└─────────────────────┴─────────────────────────────────────────────────────┘
```

#### 20.1.1 继承 View 类

```kotlin
/**
 * 场景：需要自定义绘制（如圆形、图表、刻度盘）
 * 关键：重写 onDraw() 使用 Canvas 绘制
 */
class CircleView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawCircle(width / 2f, height / 2f, minOf(width, height) / 2f, paint)
    }
}
```

#### 20.1.2 组合控件

```kotlin
/**
 * 场景：复用现有控件（如标题栏、搜索栏）
 * 关键：使用 LayoutInflater 加载 XML
 */
class TitleBarView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    init {
        LayoutInflater.from(context).inflate(R.layout.title_bar, this, true)
        findViewById<ImageView>(R.id.btn_back).setOnClickListener {
            // 返回按钮事件
        }
    }
}

// XML 布局
// <com.app.TitleBarView ... />
```

#### 20.1.3 继承 ViewGroup

```kotlin
/**
 * 场景：管理子 View 布局（如流式布局、瀑布流）
 * 关键：重写 onMeasure() 和 onLayout()
 */
class FlowLayout @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : ViewGroup(context, attrs) {

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        // 测量所有子 View
        measureChildren(widthMeasureSpec, heightMeasureSpec)
        // 计算自身尺寸
        setMeasuredDimension(...)
    }

    override fun onLayout(changed: Boolean, l: Int, t: Int, r: Int, b: Int) {
        // 布局所有子 View
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            child.layout(...)
        }
    }
}
```

---

## 21. 核心生命周期方法详解

### 21.1 三大方法对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    核心生命周期方法                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┬─────────────────────────────────────────────────────────┐
│     方法         │                      说明                              │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ onMeasure()     │ 确定 View 尺寸                                           │
│                 │ 处理 MeasureSpec 三种模式                                │
│                 │ EXACTLY / AT_MOST / UNSPECIFIED                         │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ onLayout()      │ 确定子 View 位置（仅 ViewGroup）                        │
│                 │ 调用 child.layout() 设置子 View 位置                    │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ onDraw()        │ 绘制 View 内容                                          │
│                 │ 使用 Canvas 和 Paint 绘制                                │
└─────────────────┴─────────────────────────────────────────────────────────┘

// 完整流程
onMeasure() -> onLayout() -> onDraw()
   │              │              │
   ▼              ▼              ▼
 测量尺寸      确定位置        绘制内容
```

### 21.2 MeasureSpec 三种模式处理

```kotlin
override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
    val widthMode = MeasureSpec.getMode(widthMeasureSpec)
    val widthSize = MeasureSpec.getSize(widthMeasureSpec)

    var resultWidth = 0

    when (widthMode) {
        // match_parent 或具体数值 (如 100dp)
        MeasureSpec.EXACTLY -> {
            resultWidth = widthSize
        }

        // wrap_content
        MeasureSpec.AT_MOST -> {
            // 取内容和父容器允许值的较小者
            resultWidth = minOf(contentWidth, widthSize)
        }

        // ScrollView 中使用
        MeasureSpec.UNSPECIFIED -> {
            resultWidth = contentWidth // 使用内容尺寸
        }
    }

    // ⚠️ 必须调用
    setMeasuredDimension(resultWidth, resultHeight)
}
```

### 21.3 处理 wrap_content 和 padding

```kotlin
class CustomView : View {

    private val DEFAULT_SIZE = 200
    private val MIN_SIZE = 100

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        super.onMeasure(widthMeasureSpec, heightMeasureSpec)

        // 考虑 padding 的影响
        val paddingH = paddingLeft + paddingRight
        val paddingV = paddingTop + paddingBottom

        val widthMode = MeasureSpec.getMode(widthMeasureSpec)
        val widthSize = MeasureSpec.getSize(widthMeasureSpec)

        var measuredWidth = when (widthMode) {
            MeasureSpec.EXACTLY -> widthSize
            MeasureSpec.AT_MOST -> {
                // wrap_content: 内容尺寸 + padding
                minOf(DEFAULT_SIZE + paddingH, widthSize)
            }
            else -> DEFAULT_SIZE + paddingH
        }

        // 设置最小尺寸限制
        measuredWidth = maxOf(measuredWidth, MIN_SIZE + paddingH)

        setMeasuredDimension(measuredWidth, measuredHeight)
    }
}
```

---

## 22. 自定义属性详解

### 22.1 属性声明

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

### 22.2 属性解析

```kotlin
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

### 22.3 属性优先级

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         属性优先级                                          │
└─────────────────────────────────────────────────────────────────────────────┘

优先级（从高到低）：
1. XML 直接设置     <com.app.CustomView app:cv_color="#FF0000" />
2. Style 设置       android:style="@style/CustomStyle"
3. 主题属性        <item name="cv_color">#00FF00</item>
4. 默认值          代码中设置的值
```

### 22.4 在 XML 中使用

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

## 23. 事件处理与交互

### 23.1 onTouchEvent

```kotlin
class TouchView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var lastX = 0f
    private var lastY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                lastX = event.x
                lastY = event.y
                return true // 消费事件
            }
            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastX
                val dy = event.y - lastY
                // 处理移动逻辑
                lastX = event.x
                lastY = event.y
            }
            MotionEvent.ACTION_UP -> {
                // 处理点击
                performClick() // 触发 onClick
            }
            MotionEvent.ACTION_CANCEL -> {
                // 处理取消
            }
        }
        return super.onTouchEvent(event)
    }

    // 必须实现以支持 onClick
    override fun performClick(): Boolean {
        super.performClick()
        // 处理点击事件
        return true
    }
}
```

### 23.2 GestureDetector 手势处理

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

### 23.3 滑动冲突解决

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
        when (event.action) {
            MotionEvent.ACTION_MOVE -> {
                // 请求父 View 不要拦截
                parent.requestDisallowInterceptTouchEvent(true)
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### 23.4 多点触控

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

## 24. 实战案例

### 24.1 圆形进度条

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

### 24.2 组合标题栏

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

### 24.3 钢琴键盘（多点触控）

```kotlin
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
        val pointerId = event.getPointerId(event.actionIndex)

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
                pressedKeys.clear()
                for (i in 0 until event.pointerCount) {
                    val keyIndex = getKeyIndex(event.getX(i), event.getY(i))
                    if (keyIndex >= 0) pressedKeys.add(keyIndex)
                }
                invalidate()
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_POINTER_UP -> {
                val pointerIndex = event.actionIndex
                val upPointerId = event.getPointerId(pointerIndex)
                pressedKeys.removeIf { it == upPointerId }

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

## 25. 完整知识体系总结

```
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
