# Android 屏幕适配详解

> 作者：OpenClaw | 日期：2026-03-09

---

## 目录

1. [概述](#1-概述)
2. [屏幕基础知识](#2-屏幕基础知识)
3. [dp/sp 原理](#3-dpsp-原理)
4. [Android 屏幕适配机制](#4-android-屏幕适配机制)
5. [传统适配方案](#5-传统适配方案)
6. [头条方案（今日头条）](#6-头条方案今日头条)
7. [smallestWidth 方案](#7-smallestwidth-方案)
8. [适配方案对比](#8-适配方案对比)
9. [状态栏与导航栏适配](#9-状态栏与导航栏适配)
10. [常见问题](#10-常见问题)
11. [知识体系总结](#11-知识体系总结)

---

## 1. 概述

Android 屏幕碎片化严重，不同设备的屏幕尺寸、像素密度、宽高比各不相同。屏幕适配是 Android 开发中的重要课题，理解 dp/sp 原理和各种适配方案，是写出兼容性良好应用的基础。

```
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

```
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

```kotlin
// ==================== 获取屏幕信息 ====================
class ScreenUtils(context: Context) {
    
    private val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
    private val displayMetrics = context.resources.displayMetrics
    
    // 屏幕宽度（px）
    fun getWidthPx(): Int = displayMetrics.widthPixels
    
    // 屏幕高度（px）
    fun getHeightPx(): Int = displayMetrics.heightPixels
    
    // 屏幕密度（dpi）
    fun getDensityDpi(): Int = displayMetrics.densityDpi
    
    // 密度比值
    fun getDensity(): Float = displayMetrics.density
    
    // 缩放密度（sp 用）
    fun getScaledDensity(): Float = displayMetrics.scaledDensity
    
    // dp 转 px
    fun dp2px(dp: Float): Int = (dp * displayMetrics.density + 0.5f).toInt()
    
    // px 转 dp
    fun px2dp(px: Int): Float = px / displayMetrics.density
    
    // sp 转 px
    fun sp2px(sp: Float): Int = (sp * displayMetrics.scaledDensity + 0.5f).toInt()
    
    // px 转 sp
    fun px2sp(px: Int): Float = px / displayMetrics.scaledDensity
    
    // 屏幕对角线尺寸（英寸）
    fun getScreenInch(): Double {
        val point = Point()
        windowManager.defaultDisplay.getRealSize(point)
        val width = point.x
        val height = point.y
        val xdpi = displayMetrics.xdpi
        val ydpi = displayMetrics.ydpi
        
        // 对角线像素
        val diagonalPixels = sqrt((width * width + height * height).toDouble())
        // 对角线 dpi
        val diagonalDpi = sqrt((xdpi * xdpi + ydpi * ydpi).toDouble())
        
        return diagonalPixels / diagonalDpi
    }
}

// ==================== 使用示例 ====================
val screenUtils = ScreenUtils(context)
Log.d("Screen", "宽度: ${screenUtils.getWidthPx()} px")
Log.d("Screen", "高度: ${screenUtils.getHeightPx()} px")
Log.d("Screen", "密度: ${screenUtils.getDensityDpi()} dpi")
Log.d("Screen", "density: ${screenUtils.getDensity()}")
Log.d("Screen", "屏幕尺寸: ${screenUtils.getScreenInch()} 英寸")
```

### 2.3 屏幕尺寸计算示例

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         屏幕尺寸计算示例                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  设备信息：
  ─────────────────────────────────────────────────────────────────────────
  - 分辨率：1080 × 1920
  - 屏幕尺寸：5 英寸
  - 计算对角线像素：√(1080² + 1920²) ≈ 2203 px
  - dpi = 2203 / 5 ≈ 440 dpi
  - density = 440 / 160 ≈ 2.75

  dp 与 px 转换：
  ─────────────────────────────────────────────────────────────────────────
  - 100 dp = 100 × 2.75 = 275 px
  - 1080 px = 1080 / 2.75 ≈ 392 dp

  不同设备上的 100 dp：
  ─────────────────────────────────────────────────────────────────────────
  - mdpi (160 dpi, density=1)：100 dp = 100 px
  - xhdpi (320 dpi, density=2)：100 dp = 200 px
  - xxhdpi (480 dpi, density=3)：100 dp = 300 px
  - xxxhdpi (640 dpi, density=4)：100 dp = 400 px

  结论：100 dp 在不同设备上显示的物理尺寸大致相同！
```

---

## 3. dp/sp 原理

### 3.1 dp 转换原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         dp 转换原理                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  公式：
  ─────────────────────────────────────────────────────────────────────────
  px = dp × (dpi / 160)
  px = dp × density

  dp = px / (dpi / 160)
  dp = px / density

  源码分析：
  ─────────────────────────────────────────────────────────────────────────
```

```java
// TypedValue.java
public static float applyDimension(int unit, float value, DisplayMetrics metrics) {
    switch (unit) {
        case COMPLEX_UNIT_PX:
            return value;
        case COMPLEX_UNIT_DIP:
            return value * metrics.density;  // dp × density
        case COMPLEX_UNIT_SP:
            return value * metrics.scaledDensity;  // sp × scaledDensity
        case COMPLEX_UNIT_PT:
            return value * metrics.xdpi * (1.0f / 72);
        case COMPLEX_UNIT_IN:
            return value * metrics.xdpi;
        case COMPLEX_UNIT_MM:
            return value * metrics.xdpi * (1.0f / 25.4f);
    }
    return 0;
}

// Resources.java
// XML 中的 dp 最终会调用 applyDimension 转换
```

### 3.2 sp 与字体缩放

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         sp 与字体缩放                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  sp = dp × fontScale
  ─────────────────────────────────────────────────────────────────────────
  - fontScale = 用户设置的字体缩放比例
  - 默认 fontScale = 1.0
  - 用户可在 设置 → 显示 → 字体大小 中调整

  scaledDensity = density × fontScale
  ─────────────────────────────────────────────────────────────────────────

  示例：
  ─────────────────────────────────────────────────────────────────────────
  设备 density = 3（xxhdpi）
  
  用户字体设置：小（0.85）
  - scaledDensity = 3 × 0.85 = 2.55
  - 14 sp = 14 × 2.55 = 35.7 px

  用户字体设置：正常（1.0）
  - scaledDensity = 3 × 1.0 = 3.0
  - 14 sp = 14 × 3 = 42 px

  用户字体设置：超大（1.3）
  - scaledDensity = 3 × 1.3 = 3.9
  - 14 sp = 14 × 3.9 = 54.6 px

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  重要：                                                                 │
  │  ─────────────────────────────────────────────────────────────────────── │
  │  - 字体大小应该使用 sp，尊重用户设置                                    │
  │  - 固定尺寸的控件使用 dp                                                │
  │  - 如果需要固定字体大小（不随用户设置变化），使用 dp                     │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

```kotlin
// ==================== 监听字体设置变化 ====================
class MainActivity : AppCompatActivity() {
    
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        
        // 字体设置变化
        val fontScale = newConfig.fontScale
        Log.d("Font", "fontScale: $fontScale")
        
        // 更新 UI
        updateTextSize()
    }
    
    // 在 AndroidManifest.xml 中声明
    // android:configChanges="fontScale|density|screenLayout"
}

// ==================== 获取当前字体缩放 ====================
fun getFontScale(context: Context): Float {
    return context.resources.configuration.fontScale
}

// ==================== 强制使用特定字体大小 ====================
// 方式1：使用 dp 而不是 sp
<TextView
    android:textSize="14dp" />  <!-- 不会随用户设置变化 -->

// 方式2：代码中动态设置
fun setTextSizeInDp(textView: TextView, dp: Float) {
    val px = dp * Resources.getSystem().displayMetrics.density
    textView.textSize = px / textView.resources.displayMetrics.scaledDensity
}
```

### 3.3 dp 适配的局限性

```
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

## 4. Android 屏幕适配机制

### 4.1 资源限定符

```
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

```
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

```
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

```
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

### 6.1 原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         头条方案原理                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  核心思想：
  ─────────────────────────────────────────────────────────────────────────
  动态修改 DisplayMetrics 中的 density、densityDpi、scaledDensity
  使所有设备的屏幕宽度都等于同一个 dp 值（如 360 dp）

  原理：
  ─────────────────────────────────────────────────────────────────────────
  
  假设设计稿宽度 = 360 dp
  设备实际宽度 = 1080 px
  
  我们需要：
  density = 1080 / 360 = 3.0
  
  这样：
  - 180 dp = 180 × 3.0 = 540 px（正好是屏幕宽度的一半）
  - 360 dp = 360 × 3.0 = 1080 px（正好是整个屏幕宽度）

  对于宽度 1440 px 的设备：
  density = 1440 / 360 = 4.0
  
  这样：
  - 180 dp = 180 × 4.0 = 720 px（也是屏幕宽度的一半）
  - 360 dp = 360 × 4.0 = 1440 px（也是整个屏幕宽度）

  结论：
  ─────────────────────────────────────────────────────────────────────────
  - 所有设备都按照 360 dp 宽度设计
  - 修改 density 后，1 dp 在不同设备上占屏幕的比例相同
  - 无需创建多套 dimens 文件
```

### 6.2 实现

```kotlin
/**
 * 头条屏幕适配方案
 * 
 * 使用方法：
 * 1. 在 Application.onCreate() 中调用 init()
 * 2. 在 Activity.onCreate() 的 super.onCreate() 之前调用 adapt()
 */
object ScreenAdapt {
    
    // 设计稿宽度（dp）
    private const val DESIGN_WIDTH = 360f
    
    // 系统原始 density
    private var systemDensity: Float = 0f
    private var systemDensityDpi: Int = 0
    private var systemScaledDensity: Float = 0f
    
    // 应用自定义的 density
    private var appDensity: Float = 0f
    private var appDensityDpi: Int = 0
    private var appScaledDensity: Float = 0f
    
    /**
     * 初始化，在 Application.onCreate() 中调用
     */
    fun init(application: Application) {
        val displayMetrics = application.resources.displayMetrics
        
        // 保存系统原始值
        systemDensity = displayMetrics.density
        systemDensityDpi = displayMetrics.densityDpi
        systemScaledDensity = displayMetrics.scaledDensity
        
        // 计算应用 density
        appDensity = displayMetrics.widthPixels / DESIGN_WIDTH
        appDensityDpi = (160 * appDensity).toInt()
        appScaledDensity = appDensity * (systemScaledDensity / systemDensity)
        
        // 注册 Activity 生命周期回调
        application.registerActivityLifecycleCallbacks(object : ActivityLifecycleCallbacks {
            override fun onActivityCreated(activity: Activity, savedInstanceState: Bundle?) {
                // 在 Activity 创建时适配
                adapt(activity)
            }
            
            override fun onActivityStarted(activity: Activity) {}
            override fun onActivityResumed(activity: Activity) {}
            override fun onActivityPaused(activity: Activity) {}
            override fun onActivityStopped(activity: Activity) {}
            override fun onActivitySaveInstanceState(activity: Activity, outState: Bundle) {}
            override fun onActivityDestroyed(activity: Activity) {}
        })
    }
    
    /**
     * 适配单个 Activity
     */
    fun adapt(activity: Activity) {
        val displayMetrics = activity.resources.displayMetrics
        
        displayMetrics.density = appDensity
        displayMetrics.densityDpi = appDensityDpi
        displayMetrics.scaledDensity = appScaledDensity
        
        // 也需要修改 Application 的 DisplayMetrics
        val appDisplayMetrics = activity.application.resources.displayMetrics
        appDisplayMetrics.density = appDensity
        appDisplayMetrics.densityDpi = appDensityDpi
        appDisplayMetrics.scaledDensity = appScaledDensity
    }
    
    /**
     * 适配自定义宽度
     */
    fun adapt(activity: Activity, designWidth: Float) {
        val displayMetrics = activity.resources.displayMetrics
        val targetDensity = displayMetrics.widthPixels / designWidth
        val targetDensityDpi = (160 * targetDensity).toInt()
        val targetScaledDensity = targetDensity * (systemScaledDensity / systemDensity)
        
        displayMetrics.density = targetDensity
        displayMetrics.densityDpi = targetDensityDpi
        displayMetrics.scaledDensity = targetScaledDensity
        
        val appDisplayMetrics = activity.application.resources.displayMetrics
        appDisplayMetrics.density = targetDensity
        appDisplayMetrics.densityDpi = targetDensityDpi
        appDisplayMetrics.scaledDensity = targetScaledDensity
    }
    
    /**
     * 恢复系统默认
     */
    fun reset(activity: Activity) {
        val displayMetrics = activity.resources.displayMetrics
        
        displayMetrics.density = systemDensity
        displayMetrics.densityDpi = systemDensityDpi
        displayMetrics.scaledDensity = systemScaledDensity
        
        val appDisplayMetrics = activity.application.resources.displayMetrics
        appDisplayMetrics.density = systemDensity
        appDisplayMetrics.densityDpi = systemDensityDpi
        appDisplayMetrics.scaledDensity = systemScaledDensity
    }
}
```

```kotlin
// ==================== Application 中使用 ====================
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // 初始化屏幕适配
        ScreenAdapt.init(this)
    }
}

// ==================== 或者手动适配单个 Activity ====================
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // 在 super.onCreate() 之前调用
        ScreenAdapt.adapt(this)
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

### 6.3 头条方案的问题

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         头条方案问题                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 影响系统控件
  ─────────────────────────────────────────────────────────────────────────
  - 修改 density 会影响所有使用 dp 的系统控件
  - 系统弹窗、Toast 等也会被缩放
  - 可能导致系统控件显示异常

  2. 影响第三方库
  ─────────────────────────────────────────────────────────────────────────
  - 第三方库可能也依赖系统的 density
  - 可能导致第三方库界面异常

  3. 字体问题
  ─────────────────────────────────────────────────────────────────────────
  - scaledDensity 的修改可能影响字体显示
  - 需要正确处理字体缩放

  4. Activity 切换问题
  ─────────────────────────────────────────────────────────────────────────
  - 每个 Activity 都需要调用适配方法
  - 可以通过 ActivityLifecycleCallbacks 自动处理

  5. WebView 问题
  ─────────────────────────────────────────────────────────────────────────
  - WebView 内部的渲染不受影响
  - 可能需要单独处理

  解决方案：
  ─────────────────────────────────────────────────────────────────────────
  1. 只在特定 Activity 中使用
  2. 使用 Base Activity 统一处理
  3. 对系统弹窗等场景调用 reset() 恢复
```

### 6.4 优化版本

```kotlin
/**
 * 优化版头条方案
 * 只修改 Activity 的 DisplayMetrics，不影响 Application
 */
object ScreenAdaptOptimized {
    
    private const val DESIGN_WIDTH = 360f
    
    fun adapt(activity: Activity, designWidth: Float = DESIGN_WIDTH) {
        val activityMetrics = activity.resources.displayMetrics
        
        // 计算目标 density
        val targetDensity = activityMetrics.widthPixels / designWidth
        val targetDensityDpi = (160 * targetDensity).toInt()
        val targetScaledDensity = targetDensity * 
            (activityMetrics.scaledDensity / activityMetrics.density)
        
        // 只修改 Activity 的 DisplayMetrics
        activityMetrics.density = targetDensity
        activityMetrics.densityDpi = targetDensityDpi
        activityMetrics.scaledDensity = targetScaledDensity
        
        // 同时修改 Activity 的 Configuration
        val config = Configuration(activity.resources.configuration)
        config.densityDpi = targetDensityDpi
        activity.resources.updateConfiguration(config, activityMetrics)
    }
    
    /**
     * 获取未适配的 dp 值
     * 用于需要原始 dp 的场景
     */
    fun getOriginalDp(activity: Activity, px: Float): Float {
        val systemDensity = activity.resources.displayMetrics.widthPixels / DESIGN_WIDTH
        return px / systemDensity
    }
}

// ==================== BaseActivity ====================
abstract class BaseActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        ScreenAdaptOptimized.adapt(this)
        super.onCreate(savedInstanceState)
    }
}
```

---

## 7. smallestWidth 方案

### 7.1 原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         smallestWidth 原理                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  smallestWidth（最小宽度）是屏幕可用宽度和高度中较小的一个
  无论屏幕如何旋转，sw 值不变

  计算：
  ─────────────────────────────────────────────────────────────────────────
  1080×1920，density=3
  - 宽度 dp = 1080 / 3 = 360 dp
  - 高度 dp = 1920 / 3 = 640 dp
  - sw = min(360, 640) = 360 dp
  - 适配文件：values-sw360dp

  1440×2560，density=4
  - 宽度 dp = 1440 / 4 = 360 dp
  - 高度 dp = 2560 / 4 = 640 dp
  - sw = min(360, 640) = 360 dp
  - 适配文件：values-sw360dp

  768×1024（平板），density=1.33
  - 宽度 dp = 768 / 1.33 ≈ 577 dp
  - 高度 dp = 1024 / 1.33 ≈ 770 dp
  - sw = min(577, 770) = 577 dp
  - 适配文件：values-sw577dp（或 values-sw480dp）

  优势：
  ─────────────────────────────────────────────────────────────────────────
  - 系统原生支持，稳定可靠
  - 不修改系统参数，无副作用
  - 支持平板和手机
```

### 7.2 使用方法

```
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         适配方案对比表                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────────┬─────────────────┬─────────────────────┐
  │     方案         │     优点        │     缺点        │      推荐场景        │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
  │ dp 原生适配      │ 简单、官方支持  │ 宽高比问题      │ 简单应用            │
  │                 │ 无副作用        │ 平板显示问题    │                     │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
  │ 多 dimens       │ 灵活控制        │ 维护成本高      │ 需要精细控制        │
  │                 │ 无副作用        │ 文件数量多      │                     │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
  │ 头条方案        │ 一次配置        │ 修改系统参数    │ 手机应用            │
  │                 │ 适配精确        │ 可能有副作用    │ 界面统一            │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
  │ smallestWidth   │ 官方支持        │ 需要生成文件    │ 推荐！              │
  │                 │ 无副作用        │ 维护成本        │ 各种设备            │
  │                 │ 支持平板        │                 │                     │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────────┤
  │ ConstraintLayout│ 原生支持        │ 学习成本        │ 布局复杂场景        │
  │ 百分比          │ 无副作用        │ 不适合所有场景  │                     │
  └─────────────────┴─────────────────┴─────────────────┴─────────────────────┘
```

---

## 9. 状态栏与导航栏适配

### 9.1 沉浸式状态栏

```kotlin
// ==================== 沉浸式状态栏 ====================
class MainActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 方式1：Android 5.0+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            window.apply {
                clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS)
                decorView.systemUiVisibility = (
                    View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN or
                    View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                )
                addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
                statusBarColor = Color.TRANSPARENT
            }
        }
        
        // 方式2：Android 10+ 深色状态栏图标
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            window.insetsController?.setSystemBarsAppearance(
                WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS,
                WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS
            )
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            window.decorView.systemUiVisibility = 
                window.decorView.systemUiVisibility or 
                View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR
        }
        
        setContentView(R.layout.activity_main)
        
        // 给根布局添加 paddingTop
        val rootView = findViewById<View>(R.id.root)
        rootView.setPadding(0, getStatusBarHeight(), 0, 0)
    }
    
    // 获取状态栏高度
    private fun getStatusBarHeight(): Int {
        val resourceId = resources.getIdentifier("status_bar_height", "dimen", "android")
        return if (resourceId > 0) resources.getDimensionPixelSize(resourceId) else 0
    }
}
```

### 9.2 全面屏适配

```xml
<!-- ==================== values-v28/styles.xml ==================== -->
<!-- Android 9.0+ 刘海屏 -->
<style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">
    <!-- 允许内容延伸到刘海区域 -->
    <item name="android:windowLayoutInDisplayCutoutMode">shortEdges</item>
</style>

<!-- 三种模式：
  - default：默认，刘海区域显示黑边
  - shortEdges：内容延伸到刘海区域
  - never：永远不允许内容延伸到刘海区域
-->
```

```kotlin
// ==================== 代码设置 ====================
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
    window.attributes.layoutInDisplayCutoutMode = 
        WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
}

// ==================== 获取刘海区域信息 ====================
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
    val displayCutout = window.decorView.rootWindowInsets?.displayCutout
    displayCutout?.let {
        val safeInsetTop = it.safeInsetTop
        val safeInsetBottom = it.safeInsetBottom
        val safeInsetLeft = it.safeInsetLeft
        val safeInsetRight = it.safeInsetRight
        
        // 调整布局避开刘海区域
        binding.root.setPadding(
            safeInsetLeft, safeInsetTop, 
            safeInsetRight, safeInsetBottom
        )
    }
}
```

### 9.3 导航栏适配

```kotlin
// ==================== 隐藏导航栏 ====================
// 方式1：隐藏导航栏（滑动可恢复）
window.decorView.systemUiVisibility = (
    View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or
    View.SYSTEM_UI_FLAG_IMMERSIVE
)

// 方式2：沉浸式模式（全屏）
window.decorView.systemUiVisibility = (
    View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or
    View.SYSTEM_UI_FLAG_FULLSCREEN or
    View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or
    View.SYSTEM_UI_FLAG_LAYOUT_STABLE or
    View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION or
    View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
)

// 方式3：Android 11+
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
    window.setDecorFitsSystemWindows(false)
    window.insetsController?.let { controller ->
        controller.hide(WindowInsets.Type.systemBars())
        controller.systemBarsBehavior = 
            WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
    }
}

// ==================== 获取导航栏高度 ====================
fun getNavigationBarHeight(context: Context): Int {
    val resourceId = context.resources.getIdentifier(
        "navigation_bar_height", "dimen", "android"
    )
    return if (resourceId > 0) context.resources.getDimensionPixelSize(resourceId) else 0
}

// ==================== 判断是否有导航栏 ====================
fun hasNavigationBar(context: Context): Boolean {
    val hasMenuKey = ViewConfiguration.get(context).hasPermanentMenuKey()
    val hasBackKey = KeyCharacterMap.deviceHasKey(KeyEvent.KEYCODE_BACK)
    return !hasMenuKey && !hasBackKey
}
```

---

## 10. 常见问题

### 10.1 为什么设置 dp 后在不同手机上大小不一样？

```
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

```
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

```
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

```
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         屏幕适配知识体系                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   屏幕适配      │
                           └────────┬────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
  ┌───────────┐              ┌───────────┐              ┌───────────┐
  │ dp/sp 原理│              │ 适配方案  │              │ 特殊适配  │
  │           │              │           │              │           │
  │ dp=density│              │ 多dimens  │              │ 状态栏    │
  │ sp=font   │              │ 头条方案  │              │ 刘海屏    │
  │ 转换公式  │              │ sw方案    │              │ 导航栏    │
  └───────────┘              └───────────┘              └───────────┘

  核心要点：
  ─────────────────────────────────────────────────────────────────────────
  1. dp/sp 原理：px = dp × density
  2. 头条方案：动态修改 density，适配精确但有副作用
  3. smallestWidth：官方支持，无副作用，推荐使用
  4. ConstraintLayout：百分比布局，灵活适配
  5. 刘海屏/全面屏：windowLayoutInDisplayCutoutMode
  6. 状态栏/导航栏：WindowInsets API

  推荐方案：
  ─────────────────────────────────────────────────────────────────────────
  - 简单应用：dp + ConstraintLayout
  - 中等应用：smallestWidth 方案
  - 复杂应用：头条方案 + smallestWidth 结合
```

---

> 作者：OpenClaw | 日期：2026-03-09
