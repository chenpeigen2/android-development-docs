# Android 屏幕适配详解

> 源码版本：AOSP Android 17（API 37），`android-17.0.0_r1`。


> 作者：OpenClaw | 初稿日期：2026-03-09

---

## 目录

- [1. 概述](#1-概述)
- [2. 屏幕基础知识](#2-屏幕基础知识)
  - [2.1 核心概念](#21-核心概念)
  - [2.2 屏幕参数获取](#22-屏幕参数获取)
  - [2.3 屏幕尺寸计算示例](#23-屏幕尺寸计算示例)
- [3. dp/sp 原理](#3-dpsp-原理)
  - [3.1 dp 转换原理](#31-dp-转换原理)
  - [3.2 sp 与字体缩放](#32-sp-与字体缩放)
  - [3.3 dp 适配的局限性](#33-dp-适配的局限性)
- [4. Android 屏幕适配机制](#4-android-屏幕适配机制)
  - [4.1 资源限定符](#41-资源限定符)
  - [4.2 屏幕密度匹配规则](#42-屏幕密度匹配规则)
- [5. 传统适配方案](#5-传统适配方案)
  - [5.1 多 dimens 文件](#51-多-dimens-文件)
  - [5.2 多 layout 文件](#52-多-layout-文件)
  - [5.3 ConstraintLayout 百分比布局](#53-constraintlayout-百分比布局)
- [6. 头条方案（今日头条）](#6-头条方案今日头条)
  - [6.1 原理](#61-原理)
  - [6.2 实现](#62-实现)
  - [6.3 头条方案的问题](#63-头条方案的问题)
  - [6.4 优化版本](#64-优化版本)
  - [6.5 AutoDensity 库](#65-autodensity-库)
  - [6.6 头条方案 vs AutoDensity](#66-头条方案-vs-autodensity)
- [7. smallestWidth 方案](#7-smallestwidth-方案)
  - [7.1 原理](#71-原理)
  - [7.2 使用方法](#72-使用方法)
  - [7.3 自动生成工具](#73-自动生成工具)
- [8. 适配方案对比](#8-适配方案对比)
  - [8.1 Android 17 大屏行为边界](#81-android-17-大屏行为边界)
- [9. 状态栏与导航栏适配](#9-状态栏与导航栏适配)
  - [9.1 沉浸式状态栏](#91-沉浸式状态栏)
  - [9.2 全面屏适配](#92-全面屏适配)
  - [9.3 导航栏适配](#93-导航栏适配)
- [10. 常见问题](#10-常见问题)
  - [10.1 为什么设置 dp 后在不同手机上大小不一样？](#101-为什么设置-dp-后在不同手机上大小不一样)
  - [10.2 1px 边框在某些设备上消失？](#102-1px-边框在某些设备上消失)
  - [10.3 平板适配问题？](#103-平板适配问题)
  - [10.4 图片模糊问题？](#104-图片模糊问题)
- [11. 知识体系总结](#11-知识体系总结)

---

## 1. 概述

Android 屏幕碎片化严重，不同设备的屏幕尺寸、像素密度、宽高比各不相同。屏幕适配是 Android 开发中的重要课题，理解 dp/sp 原理和各种适配方案，是写出兼容性良好应用的基础。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 屏幕碎片化                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  屏幕尺寸：
  ─────────────────────────────────────────────────────────────────────────
  - 手机：4.5" ~ 7"
  - 平板：7" ~ 13"
  - 折叠屏：展开前后尺寸变化
  - 电视、车载：各种尺寸

  屏幕分辨率：
  ─────────────────────────────────────────────────────────────────────────
  - 720p (1280×720)
  - 1080p (1920×1080)
  - 2K (2560×1440)
  - 4K (3840×2160)

  像素密度（DPI）：
  ─────────────────────────────────────────────────────────────────────────
  - ldpi：120 dpi
  - mdpi：160 dpi（基准）
  - hdpi：240 dpi
  - xhdpi：320 dpi
  - xxhdpi：480 dpi
  - xxxhdpi：640 dpi

  宽高比：
  ─────────────────────────────────────────────────────────────────────────
  - 16:9（传统手机）
  - 18:9、19:9、20:9（全面屏）
  - 21:9、22:9（超长屏）
```

---

## 2. 屏幕基础知识

### 2.1 核心概念

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         屏幕核心概念                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  px（Pixel）：
  ─────────────────────────────────────────────────────────────────────────
  - 屏幕上的物理像素点
  - 最小显示单位
  - 不同设备 1px 代表的物理尺寸不同

  dpi（Dots Per Inch）：
  ─────────────────────────────────────────────────────────────────────────
  - 每英寸像素数
  - 屏幕像素密度
  - dpi 越高，屏幕越清晰

  density（密度）：
  ─────────────────────────────────────────────────────────────────────────
  - 密度比值 = dpi / 160
  - 160 dpi 是 Android 基准密度（mdpi）
  - density = 1 表示 mdpi，density = 3 表示 xxhdpi

  dp/dip（Density-independent Pixel）：
  ─────────────────────────────────────────────────────────────────────────
  - 密度无关像素
  - 1 dp = 1 px（在 160 dpi 屏幕上）
  - 会根据屏幕密度自动转换

  sp（Scale-independent Pixel）：
  ─────────────────────────────────────────────────────────────────────────
  - 缩放无关像素
  - 用于字体大小
  - 会受用户字体设置影响
```

### 2.2 屏幕参数获取

布局应依据**当前 Activity 窗口**，不是把 `Resources.displayMetrics.widthPixels` 或 `defaultDisplay.getRealSize()` 当成应用永远可用的屏幕尺寸。API 30+ 的 `currentWindowMetrics.bounds` 包含窗口边界，内容安全区还需结合系统栏、cutout、IME 等 Insets。依据：[WindowManager.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/WindowManager.java)、[窗口尺寸分类指南](https://developer.android.com/develop/ui/views/layout/use-window-size-classes)。

```kotlin
// API 30+；从 Activity 的 WindowManager 获取，不缓存为进程级固定宽高。
@RequiresApi(30)
fun currentWindowBounds(activity: Activity): Rect =
    Rect(activity.windowManager.currentWindowMetrics.bounds)

fun dpToPx(context: Context, dp: Float): Float =
    TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, dp, context.resources.displayMetrics)

fun spToPx(context: Context, sp: Float): Float =
    TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_SP, sp, context.resources.displayMetrics)

@Suppress("DEPRECATION")
fun pxToSp(context: Context, px: Float): Float {
    val metrics = context.resources.displayMetrics
    return if (Build.VERSION.SDK_INT >= 34) {
        TypedValue.deriveDimension(TypedValue.COMPLEX_UNIT_SP, px, metrics)
    } else {
        px / metrics.scaledDensity // 仅保留 API 33 及以下的线性兼容分支
    }
}
```

低版本可使用项目已引入的 Jetpack WindowManager 兼容能力；不在此猜测依赖版本。窗口拖动、折叠、旋转和显示密度改变后重新获取度量，勿保存启动时的值长期复用。转换依据：[TypedValue.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/util/TypedValue.java)。

物理英寸只是诊断参考，不用于选择布局。若确实有可靠的整块显示面板像素和 xdpi/ydpi，公式为 `hypot(widthPx / xdpi, heightPx / ydpi)`；原来的“像素对角线除以 dpi 对角线”是错误的。厂商报告的物理 dpi 可能不准确，且窗口边界不是整块面板尺寸。

### 2.3 屏幕尺寸计算示例

1080 × 1920、5 英寸面板的对角线像素约 2203，计算得到物理像素密度约 440 ppi。**不能据此认定 Android 的 density 必为 440 / 160**：逻辑密度由系统配置决定，还会受用户显示大小及兼容模式影响。

若当前资源实际报告 density=3，则 100dp=300px；若报告 density=2.75，才是 275px。设备物理密度估计与 UI 单位换算应分开。

| 当前逻辑 density | 100dp 的 px |
|---:|---:|
| 1 | 100 |
| 2 | 200 |
| 3 | 300 |
| 4 | 400 |

dp 旨在提供密度无关的逻辑尺寸，但不保证每台设备都有严格相同的物理毫米数。换算使用当前 Resources 的度量，依据：[TypedValue.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/util/TypedValue.java)。

## 3. dp/sp 原理

### 3.1 dp 转换原理

`px = dp × density`，反向为 `dp = px / density`。这里用当前配置的逻辑密度，不把它等同于面板物理 dpi。使用所属 View/Activity 的 Resources，避免全局 `Resources.getSystem()` 与当前窗口配置不一致。

```text
伪代码（TypedValue.applyDimension 的相关分支，省略其他单位）：
DIP -> value * metrics.density
SP  -> 若 fontScaleConverter 存在：convertSpToDp(value) 后再转换 DIP
       否则使用 value * metrics.scaledDensity 的兼容分支
```

`fontScaleConverter` 为实现细节，不是应用反射或替换的扩展点。应用统一调用 `TypedValue.applyDimension`。依据：[TypedValue.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/util/TypedValue.java)。

### 3.2 sp 与字体缩放

Android 14 起支持最高 200% 的非线性字体缩放，因此原文 `sp = dp × fontScale` 不成立，`px = sp × scaledDensity` 也不再是通用公式。不同字号缩放比例可能不同，`4sp + 20sp` 转成 px 的和也不一定等于 `24sp` 的结果。

- XML 文字大小继续用 sp，`TextView.setTextSize(COMPLEX_UNIT_SP, value)` 让系统负责转换。
- 手动 Canvas 绘字用 `TypedValue.applyDimension(COMPLEX_UNIT_SP, value, metrics)` 设置 `Paint.textSize`。
- px 反推 sp 在 API 34+ 用 `deriveDimension`，不能一律除 scaledDensity。
- `Configuration.fontScale` 只作配置描述，不是通用乘数；不要通过 dp 字体或改 scaledDensity 绕过可访问性设置。
- 字体改变后重新计算文字测量、换行与布局；让默认配置重建处理，或自行完整处理相关配置，而不是只改一个字体字段。

```kotlin
textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 18f)
paint.textSize = TypedValue.applyDimension(
    TypedValue.COMPLEX_UNIT_SP, 18f, view.resources.displayMetrics
)
```

必须回归最大字体下的换行、按钮触摸区及容器高度，避免按字体的固定倍数写死高度。依据：[Android 14 非线性字体缩放](https://developer.android.com/about/versions/14/features#non-linear-font-scaling)、[TypedValue.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/util/TypedValue.java)。

### 3.3 dp 适配的局限性

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         dp 适配的局限性                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  问题1：相同 dp 在不同屏幕尺寸上比例不同
  ─────────────────────────────────────────────────────────────────────────

  1080p 手机（5 英寸）：
  - 宽度：1080 / 3 = 360 dp
  - 100 dp 占屏幕宽度：100 / 360 = 27.8%

  1080p 手机（6.5 英寸）：
  - 宽度：1080 / 2.75 ≈ 393 dp（假设 density = 2.75）
  - 100 dp 占屏幕宽度：100 / 393 = 25.4%

  问题2：平板设备
  ─────────────────────────────────────────────────────────────────────────

  10 英寸平板（2560×1600）：
  - density ≈ 2（假设）
  - 宽度：2560 / 2 = 1280 dp
  - 100 dp 占屏幕宽度：100 / 1280 = 7.8%

  结果：手机上看起来很大的按钮，平板上变得很小！

  问题3：非标准密度设备
  ─────────────────────────────────────────────────────────────────────────

  某些设备 density 不是整数（如 2.75、3.5）
  - 可能导致 1px 边框消失
  - 图标尺寸不匹配

  解决方案：
  ─────────────────────────────────────────────────────────────────────────
  1. 使用百分比布局（ConstraintLayout）
  2. 使用 smallestWidth 限定符
  3. 使用今日头条方案（动态修改 density）
```

---

### 3.4 TypedValue：dp/sp 转换的实际分支

资源尺寸最终都要变成像素，但 dp 和 sp 不再只是两个不同的线性系数。Android 17 的 DisplayMetrics 可以携带 `fontScaleConverter`；SP 分支先把字号映射到 dp，再乘 density。

源码精简节选（省略注释；[TypedValue.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/util/TypedValue.java)）：

```java
public static float applyDimension(@ComplexDimensionUnit int unit, float value,
                                   DisplayMetrics metrics)
{
    switch (unit) {
        case COMPLEX_UNIT_PX:
            return value;
        case COMPLEX_UNIT_DIP:
            return value * metrics.density;
        case COMPLEX_UNIT_SP:
            if (metrics.fontScaleConverter != null) {
                return applyDimension(
                        COMPLEX_UNIT_DIP,
                        metrics.fontScaleConverter.convertSpToDp(value),
                        metrics);
            } else {
                return value * metrics.scaledDensity;
            }
        case COMPLEX_UNIT_PT:
            return value * metrics.xdpi * INCHES_PER_PT;
        case COMPLEX_UNIT_IN:
            return value * metrics.xdpi;
        case COMPLEX_UNIT_MM:
            return value * metrics.xdpi * INCHES_PER_MM;
    }
    return 0;
}
```

源码精简节选（省略注释；[TypedValue.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/util/TypedValue.java)）：

```java
public static float deriveDimension(
        @ComplexDimensionUnit int unitToConvertTo,
        float pixelValue,
        @NonNull DisplayMetrics metrics) {
    switch (unitToConvertTo) {
        case COMPLEX_UNIT_PX:
            return pixelValue;
        case COMPLEX_UNIT_DIP: {
            if (metrics.density == 0) {
                return 0;
            }
            return pixelValue / metrics.density;
        }
        case COMPLEX_UNIT_SP:
            if (metrics.fontScaleConverter != null) {
                final float dpValue = deriveDimension(COMPLEX_UNIT_DIP, pixelValue, metrics);
                return metrics.fontScaleConverter.convertDpToSp(dpValue);
            } else {
                if (metrics.scaledDensity == 0) {
                    return 0;
                }
                return pixelValue / metrics.scaledDensity;
            }
        case COMPLEX_UNIT_PT: {
            if (metrics.xdpi == 0) {
                return 0;
            }
            return pixelValue / metrics.xdpi / INCHES_PER_PT;
        }
        case COMPLEX_UNIT_IN: {
            if (metrics.xdpi == 0) {
                return 0;
            }
            return pixelValue / metrics.xdpi;
        }
        case COMPLEX_UNIT_MM: {
            if (metrics.xdpi == 0) {
                return 0;
            }
            return pixelValue / metrics.xdpi / INCHES_PER_MM;
        }
        default:
            throw new IllegalArgumentException("Invalid unitToConvertTo " + unitToConvertTo);
    }
}
```

`deriveDimension()` 是逆向换算：SP 有 converter 时先 px→dp，再 convertDpToSp。直接用 `px / scaledDensity` 只覆盖没有 converter 的旧分支。API 34 起可调用 deriveDimension；旧系统使用其支持的线性转换路径。

```kotlin
fun spToPx(resources: android.content.res.Resources, sp: Float): Float =
    android.util.TypedValue.applyDimension(
        android.util.TypedValue.COMPLEX_UNIT_SP, sp, resources.displayMetrics)

fun pxToSp(resources: android.content.res.Resources, px: Float): Float {
    val dm = resources.displayMetrics
    return if (android.os.Build.VERSION.SDK_INT >= 34) {
        android.util.TypedValue.deriveDimension(
            android.util.TypedValue.COMPLEX_UNIT_SP, px, dm)
    } else {
        px / dm.scaledDensity
    }
}
```

这也是不应在全局强改 scaledDensity 来“锁定字号”的源码原因：非线性 converter 与资源 Configuration/fontScale 是一套协同状态，单改某个字段既可能破坏一致性，也不能替用户保留可访问的字体缩放。

Canvas 的 Paint.textSize 接收 px，TextView.setTextSize(float) 默认接收 sp。若把已经 spToPx 的结果再传给默认 setTextSize，就会重复转换；需要像素重载时明确使用 COMPLEX_UNIT_PX。


## 4. Android 屏幕适配机制

### 4.1 资源限定符

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         资源限定符                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  屏幕尺寸限定符：
  ─────────────────────────────────────────────────────────────────────────
  - small：小于 3.0 英寸
  - normal：3.0 ~ 5.0 英寸
  - large：5.0 ~ 7.0 英寸
  - xlarge：大于 7.0 英寸

  屏幕密度限定符：
  ─────────────────────────────────────────────────────────────────────────
  - ldpi：≤ 120 dpi
  - mdpi：120 ~ 160 dpi
  - hdpi：160 ~ 240 dpi
  - xhdpi：240 ~ 320 dpi
  - xxhdpi：320 ~ 480 dpi
  - xxxhdpi：480 ~ 640 dpi
  - nodpi：不缩放
  - anydpi：任意密度（矢量图）

  最小宽度限定符（smallestWidth）：
  ─────────────────────────────────────────────────────────────────────────
  - sw320dp：最小宽度 ≥ 320 dp
  - sw360dp：最小宽度 ≥ 360 dp
  - sw480dp：最小宽度 ≥ 480 dp
  - sw600dp：最小宽度 ≥ 600 dp（7 英寸平板）
  - sw720dp：最小宽度 ≥ 720 dp（10 英寸平板）

  可用宽度/高度限定符：
  ─────────────────────────────────────────────────────────────────────────
  - w720dp：可用宽度 ≥ 720 dp
  - h1024dp：可用高度 ≥ 1024 dp

  屏幕方向限定符：
  ─────────────────────────────────────────────────────────────────────────
  - port：竖屏
  - land：横屏
```

```text
  目录结构示例：
  ─────────────────────────────────────────────────────────────────────────

  res/
  ├── values/                    # 默认
  ├── values-hdpi/              # 高密度
  ├── values-xhdpi/             # 超高密度
  ├── values-xxhdpi/            # 超超高密度
  ├── values-sw320dp/           # 最小宽度 320dp
  ├── values-sw360dp/           # 最小宽度 360dp
  ├── values-sw600dp/           # 7英寸平板
  ├── values-sw720dp/           # 10英寸平板
  ├── values-w820dp/            # 宽度 ≥ 820dp
  ├── values-land/              # 横屏
  └── values-port/              # 竖屏
```

### 4.2 屏幕密度匹配规则

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         密度匹配规则                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  密度匹配优先级：
  ─────────────────────────────────────────────────────────────────────────
  1. 精确匹配（如 xxhdpi）
  2. 向上匹配（没有 xxhdpi 时找 xxxhdpi）
  3. 向下匹配（没有 xxhdpi 时找 xhdpi）
  4. 默认

  图片资源缩放：
  ─────────────────────────────────────────────────────────────────────────

  假设设备是 xxhdpi（480 dpi）：

  资源情况                     实际显示
  ─────────────────────────────────────────────────────────────────────────
  只有 mdpi 图片              放大 3 倍（模糊）
  只有 hdpi 图片              放大 2 倍（模糊）
  只有 xhdpi 图片             放大 1.5 倍（略模糊）
  有 xxhdpi 图片              原始大小（清晰）
  有 xxxhdpi 图片             缩小 0.75 倍（清晰）
  没有 drawable 文件夹        使用 drawable

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  最佳实践：                                                             │
  │  ─────────────────────────────────────────────────────────────────────── │
  │  1. 优先使用 VectorDrawable（矢量图，任意密度都清晰）                    │
  │  2. 位图资源提供 xhdpi、xxhdpi 两个密度即可                             │
  │  3. 图标使用 anydpi（矢量图）                                           │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. 传统适配方案

### 5.1 多 dimens 文件

```xml
<!-- ==================== values/dimens.xml ==================== -->
<resources>
    <dimen name="padding_standard">16dp</dimen>
    <dimen name="text_size_title">18sp</dimen>
    <dimen name="button_height">48dp</dimen>
</resources>

<!-- ==================== values-sw320dp/dimens.xml ==================== -->
<resources>
    <dimen name="padding_standard">14dp</dimen>
    <dimen name="text_size_title">16sp</dimen>
    <dimen name="button_height">44dp</dimen>
</resources>

<!-- ==================== values-sw360dp/dimens.xml ==================== -->
<resources>
    <dimen name="padding_standard">16dp</dimen>
    <dimen name="text_size_title">18sp</dimen>
    <dimen name="button_height">48dp</dimen>
</resources>

<!-- ==================== values-sw600dp/dimens.xml（平板）==================== -->
<resources>
    <dimen name="padding_standard">24dp</dimen>
    <dimen name="text_size_title">24sp</dimen>
    <dimen name="button_height">64dp</dimen>
</resources>

<!-- 使用 -->
<TextView
    android:layout_width="wrap_content"
    android:layout_height="@dimen/button_height"
    android:textSize="@dimen/text_size_title"
    android:padding="@dimen/padding_standard" />
```

### 5.2 多 layout 文件

```text
res/
├── layout/                     # 默认布局
│   └── activity_main.xml
├── layout-sw600dp/            # 7英寸平板
│   └── activity_main.xml
├── layout-sw720dp/            # 10英寸平板
│   └── activity_main.xml
├── layout-land/               # 横屏
│   └── activity_main.xml
└── layout-w600dp/             # 宽度≥600dp
    └── activity_main.xml
```

### 5.3 ConstraintLayout 百分比布局

```xml
<!-- ==================== 使用百分比 ==================== -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- 宽度占屏幕 50% -->
    <View
        android:layout_width="0dp"
        android:layout_height="100dp"
        app:layout_constraintWidth_percent="0.5"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent" />

    <!-- 高度占屏幕 30% -->
    <View
        android:layout_width="100dp"
        android:layout_height="0dp"
        app:layout_constraintHeight_percent="0.3"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toBottomOf="parent" />

    <!-- 偏移 30% -->
    <View
        app:layout_constraintHorizontal_bias="0.3"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

---

## 6. 头条方案（今日头条）

### 6.1 数学模型：改变 density 等价于改变逻辑视口

历史 density 适配把设计稿宽度作为一个新的 dp 视口。例如选定宽度 1080px、设计稿 360dp，目标 density=3；同一设计稿在 1440px 下得到 density=4。它改变的是每个 dp 对应多少像素，而不是根据内容决定单栏或双栏。

```kotlin
// 只计算历史方案参数，不修改 Application 或 Activity 的共享 Resources。
data class DesignViewport(val density: Float, val densityDpi: Int)

fun calculateDesignViewport(widthPx: Int, designWidthDp: Float): DesignViewport {
    require(widthPx > 0 && designWidthDp.isFinite() && designWidthDp > 0f)
    val density = widthPx / designWidthDp
    return DesignViewport(density, (density * 160f + 0.5f).toInt())
}
```

固定设计稿模型适合解释旧代码的缩放效果，但把 900dp 的大屏仍映射成 360dp 视口，只是把手机 UI 放大，无法产生适合大屏的双栏信息结构。

### 6.2 旧实现修改的状态及相互影响

| 旧实现动作 | 直接影响 | 隐含问题 |
|---|---|---|
| 写 Resources.displayMetrics.density | 后续 dp→px 计算 | 已加载的尺寸/Drawable 缓存不一定同步重算 |
| 写 densityDpi | 描述目标逻辑密度 | Configuration 的资源选择与 metrics 可能不一致 |
| 按比例写 scaledDensity | 线性字体路径 | Android 17 的 fontScaleConverter 分支不由此单值完全决定 |
| 同时写 Application 和 Activity | 扩大注入覆盖面 | 多个窗口、第三方 UI、不同 Context 共享状态相互影响 |
| 用 widthPixels / 设计宽度 | 决定缩放比例 | 若使用显示尺寸而非当前窗口可用尺寸，多窗口下选错基准 |

框架标准转换见第 3.4 节的 TypedValue 源码。它读的不只是 density，一个“同时改三个字段”的函数并不能建立完整、持续一致的资源配置。

### 6.3 窗口变化为何打破一次性初始化

假设平板完整窗口宽 1200px，分屏后只剩 700px。若只在 Application.onCreate 注入一次 density，两个同时存在的窗口会共享第一次计算的比例；若每个 Activity 创建时覆盖全局密度，又会让后创建窗口反过来影响前一个窗口。

此外，窗口 bounds 包含窗口区域，并不等于内容可以无障碍占用的区域。IME、caption bar、display cutout 需要单独的 Insets 策略，不能先改 density 就认为系统栏高度自然正确。

### 6.4 迁移为局部设计坐标：只缩放自绘内容

对于海报、走势图等确需保持设计比例的画布，可以只在该 Canvas 中变换，不污染资源密度：

```kotlin
// 自定义 View 的 onDraw 内；designPath 已在 360×200 设计坐标系构造。
val designWidth = 360f
val designHeight = 200f
val availableWidth = (width - paddingLeft - paddingRight).coerceAtLeast(0).toFloat()
val availableHeight = (height - paddingTop - paddingBottom).coerceAtLeast(0).toFloat()
val scale = minOf(availableWidth / designWidth, availableHeight / designHeight)
if (scale > 0f) {
    val save = canvas.save()
    canvas.translate(
        paddingLeft + (availableWidth - designWidth * scale) / 2f,
        paddingTop + (availableHeight - designHeight * scale) / 2f)
    canvas.scale(scale, scale)
    canvas.drawPath(designPath, paint)
    canvas.restoreToCount(save)
}
```

该局部模型只适用于画布图形，交互命中要应用对应逆变换；正文和表单仍应使用 sp 字号、真实 dp 间距与正常布局。不要把整页可访问文本画成一张等比缩放位图来规避重排。

### 6.5 AutoDensity 类方案的技术定位

“自动密度”描述的是一类资源映射方案，不是 Android Framework API。不同实现可能采用共享 metrics 改写、独立资源 Context 或配置拦截，不能仅凭名称推断其隔离性。判断实现时要看它改变了哪个 Resources、是否与 Configuration 一致、是否处理字体 converter、以及多个窗口能否各自保持正确配置。

系统本身已经提供 dp/sp、资源限定符、窗口配置与 Insets。依赖库即便封装 density 更新，也不会自动提供折叠铰链避让、列表到详情的布局结构和状态保存；这些仍是页面设计职责。

### 6.6 方案取舍

| 页面类型 | 适配粒度 | 实现方向 |
|---|---|---|
| 表单、列表、设置页 | 内容与窗口宽度 | 正常 dp/sp + 布局约束 + 必要的资源变体 |
| 邮箱、文件管理、详情页 | 窗口决定结构 | 单栏/双栏切换，状态独立于 View 位置 |
| 海报预览、图表画布 | 局部坐标 | Canvas 变换，单独处理文本与触摸 |
| 已采用全局 density 的旧页面 | 分模块迁移 | 明确注入边界，逐步恢复系统资源语义 |

## 7. smallestWidth 方案

`sw<N>dp` 是资源选择限定符，不等于把每个尺寸按设计稿等比放大的官方布局方案。需要按**当前可用宽度**切换单/双栏时，结合 `w<N>dp` 或窗口尺寸分类；配置变化时重新评估。保留默认资源作为回退，勿用密集生成的 dimens 文件掩盖真正的布局断点需求。依据：[窗口尺寸分类指南](https://developer.android.com/develop/ui/views/layout/use-window-size-classes)。


### 7.1 原理

Configuration.smallestScreenWidthDp 对应 smallest-width 资源限定符，描述应用正常运行时横竖方向可见尺寸的最小值。不能用物理面板像素除 density 后取 min 来替代配置。单纯旋转通常不改变该值，但窗口、显示配置或折叠形态改变后不能假设它永久不变。

```kotlin
// 读取当前资源配置，在配置变化后按需要重新评估。
val smallestWidthDp = resources.configuration.smallestScreenWidthDp
val availableWidthDp = resources.configuration.screenWidthDp
```

配置报告 smallestWidthDp=600 时可选 values-sw600dp 资源，并非某型号平板必定 sw600。限定符不修改密度，但错误断点、缺少默认资源和固定高度仍会造成适配问题，不能称整体方案无副作用。依据：[Configuration.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/content/res/Configuration.java)。

### 7.2 使用方法

```text
  目录结构：
  ─────────────────────────────────────────────────────────────────────────

  res/
  ├── values/                    # 默认（sw < 360）
  │   └── dimens.xml
  ├── values-sw320dp/           # sw ≥ 320
  │   └── dimens.xml
  ├── values-sw360dp/           # sw ≥ 360
  │   └── dimens.xml
  ├── values-sw384dp/           # sw ≥ 384
  │   └── dimens.xml
  ├── values-sw392dp/           # sw ≥ 392
  │   └── dimens.xml
  ├── values-sw411dp/           # sw ≥ 411（Pixel 等）
  │   └── dimens.xml
  └── values-sw600dp/           # sw ≥ 600（平板）
      └── dimens.xml
```

```xml
<!-- ==================== values/dimens.xml ==================== -->
<resources>
    <!-- 基准：sw < 360 -->
    <dimen name="dp_1">1dp</dimen>
    <dimen name="dp_2">2dp</dimen>
    <dimen name="dp_10">10dp</dimen>
    <dimen name="dp_100">100dp</dimen>
    <dimen name="dp_360">360dp</dimen>
</resources>

<!-- ==================== values-sw360dp/dimens.xml ==================== -->
<resources>
    <!-- sw = 360，系数 = 360 / 360 = 1.0 -->
    <dimen name="dp_1">1dp</dimen>
    <dimen name="dp_2">2dp</dimen>
    <dimen name="dp_10">10dp</dimen>
    <dimen name="dp_100">100dp</dimen>
    <dimen name="dp_360">360dp</dimen>
</resources>

<!-- ==================== values-sw384dp/dimens.xml ==================== -->
<resources>
    <!-- sw = 384，系数 = 384 / 360 = 1.067 -->
    <dimen name="dp_1">1.07dp</dimen>
    <dimen name="dp_2">2.13dp</dimen>
    <dimen name="dp_10">10.67dp</dimen>
    <dimen name="dp_100">106.67dp</dimen>
    <dimen name="dp_360">384dp</dimen>
</resources>

<!-- ==================== values-sw411dp/dimens.xml ==================== -->
<resources>
    <!-- sw = 411，系数 = 411 / 360 = 1.142 -->
    <dimen name="dp_1">1.14dp</dimen>
    <dimen name="dp_2">2.28dp</dimen>
    <dimen name="dp_10">11.42dp</dimen>
    <dimen name="dp_100">114.17dp</dimen>
    <dimen name="dp_360">411dp</dimen>
</resources>
```

### 7.3 自动生成工具

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成 dimens 文件
根据设计稿宽度（360 dp）生成不同 sw 的 dimens 文件
"""

import os

# 基准设计稿宽度
BASE_WIDTH = 360

# 需要适配的 sw 值
SW_VALUES = [320, 360, 384, 392, 400, 411, 480, 533, 592, 600, 640, 720, 768, 800, 820, 960, 1024, 1280]

# dimens 值范围
DIMENS_RANGE = range(1, 361)

def generate_dimens(sw):
    """生成指定 sw 的 dimens.xml"""
    scale = sw / BASE_WIDTH
    lines = ['<?xml version="1.0" encoding="utf-8"?>']
    lines.append('<resources>')
    lines.append(f'    <!-- sw = {sw}, scale = {scale:.4f} -->')

    for i in DIMENS_RANGE:
        value = i * scale
        lines.append(f'    <dimen name="dp_{i}">{value:.2f}dp</dimen>')

    lines.append('</resources>')
    return '\n'.join(lines)

def main():
    base_dir = 'res'

    for sw in SW_VALUES:
        dir_name = f'values-sw{sw}dp'
        dir_path = os.path.join(base_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        content = generate_dimens(sw)
        file_path = os.path.join(dir_path, 'dimens.xml')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Generated: {file_path}')

if __name__ == '__main__':
    main()

```

```kotlin
// ==================== Kotlin 版本生成工具 ====================
object DimensGenerator {

    private const val BASE_WIDTH = 360

    private val SW_VALUES = listOf(
        320, 360, 384, 392, 400, 411, 480, 533, 592, 600,
        640, 720, 768, 800, 820, 960, 1024, 1280
    )

    fun generate(outputDir: File) {
        SW_VALUES.forEach { sw ->
            val scale = sw.toFloat() / BASE_WIDTH
            val content = buildString {
                appendLine("<?xml version=\"1.0\" encoding=\"utf-8\"?>")
                appendLine("<resources>")
                appendLine("    <!-- sw = $sw, scale = ${"%.4f".format(scale)} -->")

                for (i in 1..360) {
                    val value = i * scale
                    appendLine("    <dimen name=\"dp_$i\">${"%.2f".format(value)}dp</dimen>")
                }

                appendLine("</resources>")
            }

            val dir = File(outputDir, "values-sw${sw}dp")
            dir.mkdirs()
            File(dir, "dimens.xml").writeText(content)
            println("Generated: ${dir.path}")
        }
    }
}

// 使用
fun main() {
    DimensGenerator.generate(File("res"))
}
```

---

## 8. 适配方案对比

| 方案 | 适用方式 | 边界 |
|---|---|---|
| dp/sp + 约束布局 | 基础方式，尊重系统度量和字体 | 仍须处理窗口变化、断点和最大字体 |
| `w` / `sw` 资源限定符 | 适合资源与布局分级 | 不是物理设备型号识别器，也不是全屏缩放器 |
| 窗口尺寸分类 | 按可用空间选择单/多栏 | 窗口改变时重新评估，折叠姿态另行处理 |
| 历史 density 注入 | 作为迁移风险评估 | 不作为 Android 17 新项目默认方案 |

### 8.1 Android 17 大屏行为：系统版本与 target 条件

标准大屏规则从 Android 16 / targetSdk 36 开始：对于符合条件的大屏，固定方向、宽高比、不可调整大小等限制可被忽略。Android 16 提供的 `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` 临时退出，在 Android 17 / targetSdk 37 起失效。

| 运行系统 | targetSdk | 标准大屏行为 |
|---|---|---|
| Android 15 及以下 | 任意可运行 target | 不能套用 Android 16 引入的这条规则 |
| Android 16 | 36+ | 符合大屏条件时启用；该版本仍有临时退出属性 |
| Android 17 | <=35 | 不因 Android 16 的 target 门槛自动启用；系统/OEM配置仍可能影响行为 |
| Android 17 | 36 | 大屏规则启用，临时退出仍取决于兼容条件 |
| Android 17 | >=37 | 禁用临时退出，不能依赖该 property 保持不可调整大小 |

“target 37”不是无条件把所有应用强制旋转。固定 tag 在 ActivityRecord 中还检查游戏类别、显示配置、用户兼容偏好以及窗口管理配置。

### 8.2 源码门槛：兼容变更、大屏与退出属性

源码精简节选（省略注释；[ActivityInfo.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/content/pm/ActivityInfo.java)）：

```java
@ChangeId
@Overridable
@TestApi
@SuppressLint("UnflaggedApi")
@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)
public static final long UNIVERSAL_RESIZABLE_BY_DEFAULT = 357141415L;
```

源码精简节选（省略注释；[AppCompatResizeOverrides.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/AppCompatResizeOverrides.java)）：

```java
@ChangeId
@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)
static final long DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT = 447301631L;

static boolean allowRestrictedResizability(@NonNull PackageManager pm,
        @NonNull ApplicationInfo appInfo, boolean hasCheckedDisableOptOut) {
    if (!hasCheckedDisableOptOut && appInfo.isChangeEnabled(
            DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT)) {
        return false;
    }
    try {
        return pm.getPropertyAsUser(PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY,
                appInfo.packageName, null ,
                UserHandle.getUserId(appInfo.uid)).getBoolean();
    } catch (PackageManager.NameNotFoundException e) {
        return false;
    }
}
```

两个 `EnabledAfter` 分别指 target 高于 API 35 和高于 API 36，不是“运行在 Android 17 就忽略所有旧 target”。Activity 级属性也由构造器中的 `mAllowRestrictedResizability` 先检查禁用变更，禁用时不再读取退出属性。

源码精简节选（省略注释；[ActivityRecord.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityRecord.java)）：

```java
boolean isUniversalResizeable() {
    final boolean isLargeScreen = mDisplayContent != null && mDisplayContent.isLargeScreen()
            && mDisplayContent.getIgnoreOrientationRequest();
    if (!canBeUniversalResizeable(info.applicationInfo, mWmService, isLargeScreen,
            true )) {
        return false;
    }
    if (mAppCompatController.getResizeOverrides().allowRestrictedResizability()) {
        return false;
    }
    return mAppCompatController.getAspectRatioOverrides()
            .userPreferenceCompatibleWithNonResizability();
}

static boolean canBeUniversalResizeable(@NonNull ApplicationInfo appInfo,
        WindowManagerService wms, boolean isLargeScreen, boolean forActivity) {
    if (appInfo.category == ApplicationInfo.CATEGORY_GAME) {
        return false;
    }
    final boolean compatEnabled = isLargeScreen
            && appInfo.isChangeEnabled(ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT);
    final boolean configEnabled = (isLargeScreen
            ? wms.mConstants.mIgnoreActivityOrientationRequestLargeScreen
            : wms.mConstants.mIgnoreActivityOrientationRequestSmallScreen)
            && !wms.mConstants.isPackageOptOutIgnoreActivityOrientationRequest(
                    appInfo.packageName);
    if (!compatEnabled && !configEnabled) {
        return false;
    }
    if (forActivity) {
        return true;
    }
    return !AppCompatResizeOverrides.allowRestrictedResizability(
            wms.mContext.getPackageManager(), appInfo, false );
}
```

源码精简节选（省略注释；[DisplayContent.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/DisplayContent.java)）：

```java
boolean isLargeScreen() {
    return getConfiguration().smallestScreenWidthDp
            >= WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP;
}
```

`WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` 在该 tag 为 600。此处读取的是 **DisplayContent 的 Configuration.smallestScreenWidthDp**，是窗口管理的大屏策略条件；页面自己当前可用宽度、Activity 资源的 sw 限定符和这个显示级判断不是同一个测量对象。

游戏应用 `ApplicationInfo.CATEGORY_GAME` 在上述方法直接返回 false；显示的 ignoreOrientationRequest 状态、用户对兼容宽高比/可调整大小的偏好，以及 WMS 对不同屏幕的配置也参与后续判断。因此标准行为表不能被简化成一个只检查 `screenWidthDp >= 600` 的应用函数。

### 8.3 布局应按当前可用空间选择，而非按设备标签

一台满足大屏策略的平板仍可能把应用放进很窄的窗口。大屏策略决定系统是否接受应用的方向/尺寸限制，页面断点则决定当前容器能放几列。下面的断点 840dp 是示例页面的产品选择，不是 AOSP 全局双栏阈值。

```kotlin
// 位于 Activity 内，示例视图均已创建。
// body 是横向 LinearLayout；listPane/detailPane 是它的两个直接子项。
// 详细页选择状态应保存在 ViewModel 或 savedInstanceState，而不是靠可见性保存。
var twoPane: Boolean? = null
fun updatePaneMode(body: android.widget.LinearLayout,
                   listPane: android.view.View, detailPane: android.view.View) {
    val contentWidth = body.width - body.paddingLeft - body.paddingRight
    val widthDp = contentWidth / body.resources.displayMetrics.density
    val next = widthDp >= 840f
    if (twoPane == next) return
    twoPane = next
    listPane.layoutParams = android.widget.LinearLayout.LayoutParams(
        if (next) 0 else android.view.ViewGroup.LayoutParams.MATCH_PARENT,
        android.view.ViewGroup.LayoutParams.MATCH_PARENT,
        if (next) 1f else 0f)
    detailPane.layoutParams = android.widget.LinearLayout.LayoutParams(
        0, android.view.ViewGroup.LayoutParams.MATCH_PARENT, 2f)
    detailPane.visibility = if (next) android.view.View.VISIBLE else android.view.View.GONE
}
```

在 body 布局尺寸变化以及本层 Insets padding 更新后调用它。窄屏的详情导航需要独立的页面路由，切回双栏时仍恢复已选条目；不能把 GONE 的 detailPane 误当作业务选择已经清空。折叠屏铰链还需姿态/遮挡信息，两个平分的矩形并不总能覆盖可使用区域。

## 9. 状态栏与导航栏适配

### 9.1 沉浸式状态栏

**edge-to-edge 不等于隐藏系统栏**。Android 15 / targetSdk >= 35 开始强制 edge-to-edge；Android 16+ / targetSdk >= 36 已禁用 `windowOptOutEdgeToEdgeEnforcement` 退出机制。Android 17 不能继续把旧 `systemUiVisibility` 标志和 `status_bar_height` 私有资源当主要适配方案。依据：[官方 edge-to-edge 指南](https://developer.android.com/develop/ui/views/layout/edge-to-edge)、[Android 16 行为变化](https://developer.android.com/about/versions/16/behavior-changes-16#edge-to-edge)。

```kotlin
// 示例需要项目现有 AndroidX Activity/Core/AppCompat；不在此固定依赖版本。
// imports: androidx.activity.enableEdgeToEdge
//          androidx.core.view.ViewCompat, WindowInsetsCompat, doOnAttach
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)
        val content = findViewById<View>(R.id.root)
        val left = content.paddingLeft
        val top = content.paddingTop
        val right = content.paddingRight
        val bottom = content.paddingBottom
        ViewCompat.setOnApplyWindowInsetsListener(content) { v, insets ->
            val safe = insets.getInsets(
                WindowInsetsCompat.Type.systemBars() or
                    WindowInsetsCompat.Type.displayCutout() or
                    WindowInsetsCompat.Type.ime()
            )
            v.setPadding(left + safe.left, top + safe.top,
                right + safe.right, bottom + safe.bottom)
            insets // 不无条件消费；子项如另行应用，须避免重复避让同一区域。
        }
        content.doOnAttach { ViewCompat.requestApplyInsets(it) }
    }
}
```

保存初始 padding，不能在每次回调中基于上次 padding 累加。此示例为整个内容区避让；如果列表要滚动到系统栏下，需按控件拆分 padding/clipToPadding 策略，而不是重复给所有层加 Insets。IME 动画需另配 WindowInsetsAnimation，不能认为静态 padding 已保证动画平滑。

### 9.2 全面屏适配

cutout 安全区来自 `WindowInsets`，不靠刘海型号或固定高度。Android 15+ 且 targetSdk >= 35 时，非浮动窗口的 DEFAULT/SHORT_EDGES/NEVER 会按 ALWAYS 解释；因此旧 `shortEdges/never` 配置不再是保持黑边的可靠退出方案。Insets 变化、旋转和窗口重建时重新应用安全区。依据：[edge-to-edge 官方指南](https://developer.android.com/develop/ui/views/layout/edge-to-edge)。

### 9.3 导航栏适配

手势导航和三键导航有不同可见区域及对比度保护，不要用 `hasPermanentMenuKey()` / `deviceHasKey(KEYCODE_BACK)` 推断有无导航栏，也不要读取内部 `navigation_bar_height` 资源当实时高度。读取 `WindowInsetsCompat.Type.navigationBars()` 的 insets 和可见性。

```kotlin
val controller = WindowCompat.getInsetsController(window, window.decorView)
// 仅全屏内容场景隐藏系统栏；普通 edge-to-edge 页面不需要 hide。
controller.systemBarsBehavior =
    WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
controller.hide(WindowInsetsCompat.Type.systemBars())
// 离开全屏状态时恢复：controller.show(WindowInsetsCompat.Type.systemBars())
```

不要自动取消三键导航的对比度保护，除非应用自己确保足够对比度。需测试三键/手势导航、IME 显隐、横屏、桌面窗口 caption bar 和辅助功能。依据：[edge-to-edge 官方指南](https://developer.android.com/develop/ui/views/layout/edge-to-edge)。

### 9.4 WindowInsets 的数据模型：类型集合取最大值

WindowInsets 按类型维护当前 Insets、忽略可见性的最大 Insets 和可见性信息。系统栏不只有 statusBars/navigationBars，桌面窗口的 captionBar 也要纳入页面策略；IME、cutout、systemGestures 则表达不同用途。

源码精简节选（省略注释；[WindowInsets.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/WindowInsets.java)）：

```java
public Insets getInsets(@InsetsType int typeMask) {
    return getInsets(mTypeInsetsMap, typeMask);
}

static Insets getInsets(@NonNull Insets[] typeInsetsMap, @InsetsType int typeMask) {
    Insets result = null;
    for (@InsetsType int type : TYPES) {
        if ((typeMask & type) == 0) {
            continue;
        }
        Insets insets = typeInsetsMap[indexOf(type)];
        if (insets == null) {
            continue;
        }
        if (result == null) {
            result = insets;
        } else {
            result = Insets.max(result, insets);
        }
    }
    return result == null ? Insets.NONE : result;
}

public Insets getInsetsIgnoringVisibility(@InsetsType int typeMask) {
    if ((typeMask & IME) != 0) {
        throw new IllegalArgumentException("Unable to query the maximum insets for IME");
    }
    return getInsets(mTypeMaxInsetsMap, typeMask);
}
```

对多个 type 做 OR 后，getInsets 逐边取最大值，不把这些高度相加。例如 navigationBars.bottom=24、ime.bottom=300，则组合结果 bottom=300，而不是 324。手工把两者求和通常会重复避让底部重叠区域。

getInsetsIgnoringVisibility 不支持 IME，传入包含 IME 的 mask 会抛 IllegalArgumentException：输入法的尺寸与编辑器/输入法状态相关，不能当作一个固定“最大键盘高度”。可见性则通过 isVisible(type) 判断，不能简单由某一边是否大于零反推。

### 9.5 分发链：ViewRootImpl → View → ViewGroup

源码精简节选（省略注释；[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
public void dispatchApplyInsets(View host) {
    Trace.traceBegin(Trace.TRACE_TAG_VIEW, "dispatchApplyInsets");
    mApplyInsetsRequested = false;
    WindowInsets insets = getWindowInsets(true );
    if (!shouldDispatchCutout()) {
        insets = insets.consumeDisplayCutout();
    }
    host.dispatchApplyWindowInsets(insets);
    mAttachInfo.delayNotifyContentCaptureInsetsEvent(insets.getInsets(Type.all()));
    Trace.traceEnd(Trace.TRACE_TAG_VIEW);
}
```

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public WindowInsets dispatchApplyWindowInsets(WindowInsets insets) {
    try {
        mPrivateFlags3 |= PFLAG3_APPLYING_INSETS;
        if (mListenerInfo != null && mListenerInfo.mOnApplyWindowInsetsListener != null) {
            return mListenerInfo.mOnApplyWindowInsetsListener.onApplyWindowInsets(this, insets);
        } else {
            return onApplyWindowInsets(insets);
        }
    } finally {
        mPrivateFlags3 &= ~PFLAG3_APPLYING_INSETS;
    }
}
```

源码精简节选（省略注释；[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)）：

```java
public WindowInsets dispatchApplyWindowInsets(WindowInsets insets) {
    insets = super.dispatchApplyWindowInsets(insets);
    if (insets.isConsumed()) {
        return insets;
    }
    if (View.sBrokenInsetsDispatch) {
        return brokenDispatchApplyWindowInsets(insets);
    } else {
        return newDispatchApplyWindowInsets(insets);
    }
}

private WindowInsets newDispatchApplyWindowInsets(WindowInsets insets) {
    final int count = getChildCount();
    for (int i = 0; i < count; i++) {
        getChildAt(i).dispatchApplyWindowInsets(insets);
    }
    return insets;
}
```

View 优先调用已安装的 OnApplyWindowInsetsListener，否则进入 onApplyWindowInsets。ViewGroup 先应用自身逻辑，返回值若已经 consumed 就不再下发。新分发路径对各个子项传递同一份父处理结果，不把一个兄弟的消费结果依次扣给后面的兄弟；历史兼容分支仍由 sBrokenInsetsDispatch 控制。

因此根 listener 返回 insets 的含义是继续分发，不是“根加了 padding，子项就自动知道不要再加”。空间避让属于布局职责，消费属于数据分发职责，两者应分开设计：根负责顶部与左右，底部输入区域负责 IME，或由根统一避让而子项只观察不再重复加同一类型。

### 9.6 edge-to-edge 的源码判定

源码精简节选（省略注释；[PhoneWindow.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/policy/PhoneWindow.java)）：

```java
public static boolean isEdgeToEdgeEnforced(ApplicationInfo info, boolean local,
        TypedArray windowStyle) {
    return !isOptingOutEdgeToEdgeEnforcement(info, local, windowStyle)
            && (info.targetSdkVersion >= ENFORCE_EDGE_TO_EDGE_SDK_VERSION
                    || (local
                            ? CompatChanges.isChangeEnabled(ENFORCE_EDGE_TO_EDGE)
                            : info.isChangeEnabled(ENFORCE_EDGE_TO_EDGE)));
}

public static boolean isOptOutEdgeToEdgeEnabled(ApplicationInfo info, boolean local) {
    final boolean disabled = local
            ? CompatChanges.isChangeEnabled(DISABLE_OPT_OUT_EDGE_TO_EDGE)
            : info.isChangeEnabled(DISABLE_OPT_OUT_EDGE_TO_EDGE);
    return !disabled;
}

public static boolean isOptingOutEdgeToEdgeEnforcement(ApplicationInfo info, boolean local,
        TypedArray windowStyle) {
    return isOptOutEdgeToEdgeEnabled(info, local) && windowStyle.getBoolean(
            R.styleable.Window_windowOptOutEdgeToEdgeEnforcement, false );

}
```

该类把“强制 edge-to-edge”和“是否允许退出”分开判断：前者包含 targetSdk>=35 与兼容变更，后者受 DISABLE_OPT_OUT_EDGE_TO_EDGE 控制，该变更从 targetSdk 36 启用。主题里的退出属性必须先获得“允许退出”资格才有效，单在 styles.xml 写 true 不足以覆盖系统 target 行为。

edge-to-edge 让窗口内容可以绘制到系统栏后面，不等于隐藏栏，也不等于取消安全区。背景可以延伸到底，而按钮、文本、滚动列表末项仍应按交互需求避让对应 Insets。

### 9.7 IME 动画为什么有独立帧阶段

InsetsController 的 Host 要求把 Insets 动画回调投递到 Choreographer.CALLBACK_INSETS_ANIMATION。每帧先应用动画的 Insets 状态，再分发 WindowInsetsAnimation 的 progress；它位于普通动画之后、View 遍历之前，便于本次布局/绘制使用当前系统栏或 IME 位置。

源码精简节选（省略注释；[InsetsController.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/InsetsController.java)）：

```java
mAnimCallback = () -> {
    mAnimCallbackScheduled = false;
    if (mRunningAnimations.isEmpty()) {
        return;
    }

    final var runningAnimations = new ArrayList<WindowInsetsAnimation>();
    final var finishedRunners = new ArrayList<InsetsAnimationControlRunner>();
    final var state = new InsetsState(mState, true );
    boolean hasUserAnimation = false;
    boolean hasResizeAnimation = false;
    boolean hasAnimationCallback = false;
    @InsetsType int hidingTypes = 0;
    for (int i = mRunningAnimations.size() - 1; i >= 0; i--) {
        RunningAnimation runningAnimation = mRunningAnimations.get(i);
        if (DEBUG) {
            Log.d(TAG, "Running animation type: " + runningAnimation.mType);
        }
        final InsetsAnimationControlRunner runner = runningAnimation.mRunner;
        if (com.android.window.flags.Flags.syncedInsetsAnimation()
                && runningAnimation.mType == ANIMATION_TYPE_HIDE) {
            hidingTypes |= runner.getControllingTypes();
        }
        hasUserAnimation |= runner.getAnimationType() == ANIMATION_TYPE_USER;
        hasResizeAnimation |= runner.getAnimationType() == ANIMATION_TYPE_RESIZE;
        hasAnimationCallback |= runner.hasAnimationCallback();
        if (runner instanceof WindowInsetsAnimationController) {
            if (runningAnimation.mStartDispatched) {
                runningAnimations.add(runner.getAnimation());
            }

            if (((InternalInsetsAnimationController) runner).applyChangeInsets(state)) {
                finishedRunners.add(runner);
            }
        }
    }

    final WindowInsets insets = state.calculateInsets(mFrame,
            mBounds, mState , mScreenRound,
            mLegacySoftInputMode, mLegacyWindowFlags, mLegacySystemUiFlags,
            mWindowType, mActivityType, null );
    mHost.dispatchWindowInsetsAnimationProgress(insets, state,
            Collections.unmodifiableList(runningAnimations), hasUserAnimation,
            hasResizeAnimation, hasAnimationCallback, hidingTypes);
    if (DEBUG) {
        for (WindowInsetsAnimation anim : runningAnimations) {
            Log.d(TAG, String.format("Running animation on insets type: %s, progress: %f",
                    Type.toString(anim.getTypeMask()), anim.getInterpolatedFraction()));
        }
    }

    for (int i = finishedRunners.size() - 1; i >= 0; i--) {
        final var runner = finishedRunners.get(i);
        dispatchAnimationEnd(
                runner.getAnimation(),
                runner.getAnimationType() == ANIMATION_TYPE_USER,
                runner.getAnimationType() == ANIMATION_TYPE_RESIZE,
                runner.hasAnimationCallback());
    }
};
```

静态 OnApplyWindowInsetsListener 决定最终安全区，动画 callback 决定中间帧如何展示。若既在静态 listener 中立刻把底部 padding 改为最终值，又在 progress 中追加同样的 translation，就会双重移动；应明确唯一的视觉补偿策略。

平台 API 30+ 的简单跟随方式是直接使用进度回调给出的当前 Insets 更新目标容器 padding，基准值只捕获一次：

```kotlin
// content 为唯一负责底部避让的容器；API 30+。
val baseLeft = content.paddingLeft
val baseTop = content.paddingTop
val baseRight = content.paddingRight
val baseBottom = content.paddingBottom
val mask = android.view.WindowInsets.Type.systemBars() or
    android.view.WindowInsets.Type.displayCutout() or android.view.WindowInsets.Type.ime()

fun applySafeArea(insets: android.view.WindowInsets) {
    val safe = insets.getInsets(mask)
    content.setPadding(baseLeft + safe.left, baseTop + safe.top,
        baseRight + safe.right, baseBottom + safe.bottom)
}

content.setOnApplyWindowInsetsListener { _, insets ->
    applySafeArea(insets)
    insets
}
content.setWindowInsetsAnimationCallback(object : android.view.WindowInsetsAnimation.Callback(
    DISPATCH_MODE_CONTINUE_ON_SUBTREE
) {
    override fun onProgress(insets: android.view.WindowInsets,
                            runningAnimations: MutableList<android.view.WindowInsetsAnimation>)
        : android.view.WindowInsets {
        applySafeArea(insets)
        return insets
    }
})
content.requestApplyInsets() // 应在已附着后请求；初次附着也会参与系统分发。
```

该方式会随着 padding 改变触发布局，适合结构简单的内容区。复杂列表可先完成最终布局，再在 onPrepare/onStart 计算位置差，用 translation 在 onProgress 中消除差值，以减少逐帧重排；关键是静态和动画路径采用同一份安全区责任划分。


## 10. 常见问题

### 10.1 为什么设置 dp 后在不同手机上大小不一样？

```text
原因：
─────────────────────────────────────────────────────────────────────────
dp 只保证在相同物理尺寸的屏幕上显示大小一致
不同屏幕尺寸（如 5 英寸和 6.5 英寸），dp 占屏幕的比例不同

解决：
─────────────────────────────────────────────────────────────────────────
1. 使用百分比布局（ConstraintLayout）
2. 使用 smallestWidth 方案
3. 使用头条方案
```

### 10.2 1px 边框在某些设备上消失？

```text
原因：
─────────────────────────────────────────────────────────────────────────
density 不是整数时，1dp 可能小于 1px

解决：
─────────────────────────────────────────────────────────────────────────
// 使用 px 而不是 dp
<View
    android:layout_width="match_parent"
    android:layout_height="1px" />

// 或代码中处理
fun dp2px(dp: Float): Int {
    return (dp * density + 0.5f).toInt()  // 四舍五入
}
```

### 10.3 平板适配问题？

```text
问题：
─────────────────────────────────────────────────────────────────────────
手机应用在平板上显示太大或太小

解决：
─────────────────────────────────────────────────────────────────────────
1. 使用 sw600dp、sw720dp 限定符
2. 使用 Fragment 在手机和平板上展示不同布局
3. 考虑使用两栏布局（列表 + 详情）
```

### 10.4 图片模糊问题？

```text
原因：
─────────────────────────────────────────────────────────────────────────
使用了低密度图片，在高密度设备上放大导致模糊

解决：
─────────────────────────────────────────────────────────────────────────
1. 使用 VectorDrawable（矢量图）
2. 提供 xxhdpi 或 xxxhdpi 图片
3. 使用 Glide/Coil 等图片加载库
```

---

## 11. 知识体系总结

1. 布局依据当前窗口，不依据固定物理屏幕宽度或启动时缓存。
2. dp 使用当前资源密度；sp 交给 TypedValue/TextView 处理非线性字体缩放。
3. `w`/`sw` 和窗口尺寸分类用于选布局断点，不是密集生成尺寸表就能覆盖所有设备。
4. 历史 density 注入与第三方 AutoDensity 不能视为 Android 17 已验证方案。
5. 使用 Insets 处理系统栏、cutout 和 IME，避免硬编码高度及重复 padding。
6. targetSdk >= 37 的大屏行为需要真实可调整布局，不能依赖旧临时退出属性。


---

> 作者：OpenClaw | 初稿日期：2026-03-09
