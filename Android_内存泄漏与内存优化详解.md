# Android 内存泄漏与内存优化详解

> 作者：OpenClaw | 日期：2026-03-09

---

## 目录

1. [概述](#1-概述)
2. [内存管理基础](#2-内存管理基础)
   - 2.1 [Java 内存模型](#21-java-内存模型)
   - 2.2 [Android 内存分配](#22-android-内存分配)
   - 2.3 [垃圾回收机制](#23-垃圾回收机制)
3. [内存泄漏原理](#3-内存泄漏原理)
   - 3.1 [什么是内存泄漏](#31-什么是内存泄漏)
   - 3.2 [内存泄漏 vs 内存溢出](#32-内存泄漏-vs-内存溢出)
   - 3.3 [GC Root 与引用链](#33-gc-root-与引用链)
4. [常见内存泄漏场景](#4-常见内存泄漏场景)
   - 4.1 [Activity 泄漏](#41-activity-泄漏)
   - 4.2 [Handler 泄漏](#42-handler-泄漏)
   - 4.3 [单例模式泄漏](#43-单例模式泄漏)
   - 4.4 [匿名内部类泄漏](#44-匿名内部类泄漏)
   - 4.5 [静态变量泄漏](#45-静态变量泄漏)
   - 4.6 [注册未取消泄漏](#46-注册未取消泄漏)
   - 4.7 [Bitmap 泄漏](#47-bitmap-泄漏)
   - 4.8 [WebView 泄漏](#48-webview-泄漏)
5. [内存泄漏检测工具](#5-内存泄漏检测工具)
   - 5.1 [LeakCanary](#51-leakcanary)
   - 5.2 [Android Studio Profiler](#52-android-studio-profiler)
   - 5.3 [MAT](#53-mat)
   - 5.4 [dumpsys meminfo](#54-dumpsys-meminfo)
6. [内存优化策略](#6-内存优化策略)
   - 6.1 [Bitmap 优化](#61-bitmap-优化)
   - 6.2 [数据结构优化](#62-数据结构优化)
   - 6.3 [缓存策略](#63-缓存策略)
   - 6.4 [对象池优化](#64-对象池优化)
7. [OOM 处理](#7-oom-处理)
   - 7.1 [OOM 类型](#71-oom-类型)
   - 7.2 [OOM 预防](#72-oom-预防)
   - 7.3 [大图加载方案](#73-大图加载方案)
8. [常见问题](#8-常见问题)
9. [知识体系总结](#9-知识体系总结)

---

## 1. 概述

内存管理是 Android 开发中最重要的技能之一。不当的内存使用会导致内存泄漏、内存溢出（OOM），最终造成应用崩溃。理解内存泄漏的原理、掌握检测工具和优化技巧，是每个 Android 开发者的必修课。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         内存问题影响                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  内存泄漏 → 内存占用增加 → GC 频繁 → 卡顿 → OOM 崩溃

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  内存泄漏（Memory Leak）                                                │
  │  - 不再使用的对象无法被回收                                              │
  │  - 内存占用持续增长                                                      │
  │  - 长期运行后导致 OOM                                                    │
  │                                                                         │
  │  内存溢出（OOM）                                                         │
  │  - 申请的内存超过可用内存                                                │
  │  - 应用直接崩溃                                                          │
  │  - 用户体验极差                                                          │
  │                                                                         │
  │  内存抖动（Memory Churn）                                               │
  │  - 频繁创建和销毁对象                                                    │
  │  - GC 频繁触发                                                           │
  │  - 导致卡顿                                                              │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 内存管理基础

### 2.1 Java 内存模型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Java 内存模型                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                           JVM 运行时数据区                               │
  │                                                                         │
  │  线程私有区域：                                                          │
  │  - 程序计数器：当前执行的字节码行号                                      │
  │  - 虚拟机栈（Stack）：方法调用的栈帧、局部变量表                         │
  │  - 本地方法栈：Native 方法                                               │
  │                                                                         │
  │  线程共享区域：                                                          │
  │  - 堆（Heap）：对象实例                                                  │
  │    - 年轻代（Young Gen）：Eden + S0 + S1                                │
  │    - 老年代（Old Gen）：长期存活的对象                                   │
  │  - 方法区：类信息、常量、静态变量                                        │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Android 内存分配

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 内存分配                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  Android 应用堆内存限制（因设备而异）：

  ┌─────────────────────┬───────────────────────────────────────────────────┐
  │       设备类型       │              堆内存限制                            │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 低内存设备（小）     │  32 MB                                            │
  │ 低内存设备（大）     │  64 MB                                            │
  │ 普通设备（小）       │  128 MB                                           │
  │ 普通设备（大）       │  256 MB                                           │
  │ 大内存设备           │  512 MB+                                          │
  └─────────────────────┴───────────────────────────────────────────────────┘

  查看设备内存限制：

  ActivityManager am = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
  int memoryClass = am.getMemoryClass();        // 标准内存限制（MB）
  int largeMemoryClass = am.getLargeMemoryClass(); // 大堆内存限制（MB）

  // 在 AndroidManifest.xml 中申请大堆内存
  <application android:largeHeap="true" ... >
```

### 2.3 垃圾回收机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 垃圾回收机制                                │
└─────────────────────────────────────────────────────────────────────────────┘

  Android GC 演进：

  Dalvik GC（Android 4.4 及之前）
  - 标记-清除（Mark-Sweep）算法
  - 会暂停所有线程（Stop-The-World）
  - GC 期间应用卡顿

  ART GC（Android 5.0+）
  - 多种 GC 策略：
    - Sticky GC：年轻代 GC，频率高但速度快
    - Partial GC：部分 GC，不包括 Zygote 堆
    - Full GC：完整 GC，包括 Zygote 堆
  - 并发 GC，减少暂停时间
  - 压缩 GC，减少内存碎片

  GC 触发条件：
  1. 内存不足时 - 分配新对象时内存不够
  2. 手动调用 - System.gc()（不建议频繁调用）
  3. 系统内存压力大时 - 触发 onTrimMemory() 回调
```

---

## 3. 内存泄漏原理

### 3.1 什么是内存泄漏

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         什么是内存泄漏                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：不再使用的对象无法被垃圾回收器回收，持续占用内存

  正常情况：
  对象不再使用 → 无引用指向 → GC 回收 → 内存释放

  内存泄漏：
  对象不再使用 → 仍有引用指向 → GC 无法回收 → 内存持续占用

  内存泄漏的后果：
  1. 可用内存减少 - 泄漏的对象占用内存
  2. GC 频繁触发 - 导致卡顿
  3. 最终 OOM 崩溃 - 应用崩溃
```

### 3.2 内存泄漏 vs 内存溢出

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    内存泄漏 vs 内存溢出                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────┬───────────────────────────────────────────────────┐
  │       对比项         │              区别                                  │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 内存泄漏             │ 对象无法被回收，内存逐渐减少                       │
  │ (Memory Leak)       │ 渐进式问题，长期运行后出现                         │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 内存溢出             │ 申请的内存超过可用内存                             │
  │ (OutOfMemory)       │ 瞬时问题，直接崩溃                                 │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 关系                 │ 内存泄漏是内存溢出的主要原因之一                   │
  │                     │ 长期泄漏最终导致 OOM                               │
  └─────────────────────┴───────────────────────────────────────────────────┘
```

### 3.3 GC Root 与引用链

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GC Root 与引用链                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  GC Roots（根节点）：
  1. 虚拟机栈中引用的对象（局部变量）
  2. 方法区中静态属性引用的对象
  3. 方法区中常量引用的对象
  4. 本地方法栈中 JNI 引用的对象
  5. 同步锁持有的对象

  四种引用类型：

  ┌─────────────────────┬───────────────────────────────────────────────────┐
  │       引用类型       │              说明                                  │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 强引用               │ Object obj = new Object();                        │
  │ (Strong Reference)  │ 永不回收，除非引用失效                             │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 软引用               │ SoftReference<Object>                             │
  │ (Soft Reference)    │ 内存不足时回收，适合缓存                           │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 弱引用               │ WeakReference<Object>                             │
  │ (Weak Reference)    │ 下次 GC 时回收                                     │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 虚引用               │ PhantomReference<Object>                          │
  │ (Phantom Reference) │ 无法通过引用获取对象，用于跟踪回收                 │
  └─────────────────────┴───────────────────────────────────────────────────┘
```

---

## 4. 常见内存泄漏场景

### 4.1 Activity 泄漏

```java
// 错误写法：静态变量持有 Activity
public class MainActivity extends Activity {
    private static MainActivity instance; // 静态变量持有 Activity

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        instance = this; // 泄漏！Activity 无法被回收
    }
}

// 正确写法：使用 WeakReference
private WeakReference<MainActivity> activityRef;
```

### 4.2 Handler 泄漏

```java
// 错误写法：非静态内部类 Handler
public class MainActivity extends Activity {
    private final Handler mHandler = new Handler() {
        @Override
        public void handleMessage(Message msg) {
            // 隐式持有外部 Activity 引用
        }
    };
}

// 正确写法：静态内部类 + WeakReference
private static class SafeHandler extends Handler {
    private final WeakReference<MainActivity> activityRef;

    SafeHandler(MainActivity activity) {
        activityRef = new WeakReference<>(activity);
    }

    @Override
    public void handleMessage(Message msg) {
        MainActivity activity = activityRef.get();
        if (activity != null && !activity.isFinishing()) {
            activity.updateUI();
        }
    }
}

// 在 onDestroy 中移除消息
@Override
protected void onDestroy() {
    super.onDestroy();
    mHandler.removeCallbacksAndMessages(null);
}
```

### 4.3 单例模式泄漏

```java
// 错误写法：单例持有 Activity Context
public class Singleton {
    private static Singleton instance;
    private Context context;

    private Singleton(Context context) {
        this.context = context; // 如果传入 Activity，泄漏！
    }
}

// 正确写法：使用 ApplicationContext
private Singleton(Context context) {
    this.context = context.getApplicationContext();
}
```

### 4.4 匿名内部类泄漏

```java
// 错误写法：匿名 Runnable 持有 Activity 引用
new Thread(new Runnable() {
    @Override
    public void run() {
        // 匿名 Runnable 持有 Activity 引用
    }
}).start();

// 正确写法：静态内部类
private static class SafeRunnable implements Runnable {
    private WeakReference<MainActivity> activityRef;

    @Override
    public void run() {
        MainActivity activity = activityRef.get();
        if (activity == null) return;
        // 执行任务
    }
}
```

### 4.5 静态变量泄漏

```java
// 错误写法：静态集合持有 View
public class Utils {
    private static List<View> views = new ArrayList<>();

    public static void addView(View view) {
        views.add(view); // View 持有 Activity，导致泄漏
    }
}

// 解决方案：
// 1. 使用 WeakHashMap 或 WeakReference
// 2. 及时从静态集合中移除不再需要的对象
// 3. 避免在静态变量中持有 Activity/View
```

### 4.6 注册未取消泄漏

```java
// 正确写法：及时取消注册
public class MainActivity extends Activity {
    private BroadcastReceiver receiver;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        receiver = new BroadcastReceiver() { ... };
        registerReceiver(receiver, filter);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        unregisterReceiver(receiver); // 必须取消注册
    }
}

// 常见需要取消注册的：
// - BroadcastReceiver
// - EventBus
// - SensorManager
// - LocationManager
// - ContentObserver
```

### 4.7 Bitmap 泄漏

```java
// Bitmap 占用大量内存，必须及时回收

// 错误写法：Bitmap 使用后不回收
Bitmap bitmap = BitmapFactory.decodeResource(getResources(), R.drawable.large);
imageView.setImageBitmap(bitmap);
// 没有回收 bitmap

// 正确写法：
@Override
protected void onDestroy() {
    super.onDestroy();
    if (bitmap != null && !bitmap.isRecycled()) {
        bitmap.recycle();
        bitmap = null;
    }
}

// 更好的方案：使用 Glide/Picasso 等图片加载库
Glide.with(context).load(url).into(imageView);
```

### 4.8 WebView 泄漏

```java
// WebView 泄漏比较特殊，需要单独处理

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.loadDataWithBaseURL(null, "", "text/html", "utf-8", null);
            webView.clearHistory();
            
            ViewGroup parent = (ViewGroup) webView.getParent();
            if (parent != null) {
                parent.removeView(webView);
            }
            
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
```

---

## 5. 内存泄漏检测工具

### 5.1 LeakCanary

```gradle
// 添加依赖
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LeakCanary 使用                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  特点：
  - 自动检测 Activity/Fragment 泄漏
  - 自动生成泄漏链路
  - 通知栏提示

  使用方式：
  1. 添加依赖后自动生效
  2. 泄漏时发送通知
  3. 点击通知查看泄漏详情

  泄漏报告示例：
  ───────────────────────────────────────────────────────────────────────
  * MainActivity has leaked:
  * GC ROOT static MainActivity.instance
  * leaks MainActivity instance
  ───────────────────────────────────────────────────────────────────────
```

### 5.2 Android Studio Profiler

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Android Studio Profiler                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  使用步骤：
  1. 打开 Profiler（View → Tool Windows → Profiler）
  2. 选择应用进程
  3. 点击 Memory 区域
  4. 操作应用触发泄漏
  5. 点击 "Capture heap dump"
  6. 分析内存快照

  功能：
  - 实时内存监控
  - 内存快照对比
  - 对象分配追踪
  - GC 触发
```

### 5.3 MAT

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MAT (Memory Analyzer Tool)                              │
└─────────────────────────────────────────────────────────────────────────────┘

  使用步骤：
  1. 在 Android Studio 中 Dump Heap
  2. 导出 .hprof 文件
  3. 使用 MAT 打开文件
  4. 执行 Leak Suspects Report

  常用功能：
  - Histogram：查看对象数量和大小
  - Dominator Tree：查看对象支配树
  - OQL：对象查询语言

  分析技巧：
  - 搜索 Activity 类，查看实例数量
  - 查看 GC Roots 路径
  - 找出占用内存最大的对象
```

### 5.4 dumpsys meminfo

```bash
# 查看应用内存信息
adb shell dumpsys meminfo <package_name>

# 输出示例：
# Applications Memory Usage (kB):
# Uptime: 12345 Realtime: 67890
# 
# ** MEMINFO in pid 12345 [com.example.app] **
#                    Pss  Private  Private  Swapped     Heap     Heap     Heap
#                  Total    Dirty    Clean    Dirty     Size    Alloc     Free
#                  ------   ------   ------   ------   ------   ------   ------
#   Native Heap     2048     2048        0        0     4096     2048     2048
#   Dalvik Heap     4096     4096        0        0     8192     4096     4096
#   ...
```

---

## 6. 内存优化策略

### 6.1 Bitmap 优化

```java
// 1. 采样率压缩
BitmapFactory.Options options = new BitmapFactory.Options();
options.inSampleSize = 4; // 宽高各缩小 4 倍，内存减少 16 倍
Bitmap bitmap = BitmapFactory.decodeResource(getResources(), R.id.image, options);

// 2. RGB_565 格式（不需要透明度时）
options.inPreferredConfig = Bitmap.Config.RGB_565; // 每像素 2 字节

// 3. 使用 inBitmap 复用内存
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
    options.inBitmap = reusedBitmap;
}

// 4. 使用图片加载库（推荐）
Glide.with(context)
    .load(url)
    .override(800, 600) // 指定目标尺寸
    .into(imageView);
```

### 6.2 数据结构优化

```java
// 1. 使用 SparseArray 替代 HashMap<Integer, Object>
SparseArray<String> sparseArray = new SparseArray<>();
// 内存占用更小，避免自动装箱

// 2. 使用 ArrayMap 替代 HashMap
ArrayMap<String, String> arrayMap = new ArrayMap<>();
// 数据量小时更省内存

// 3. 避免使用 Enum（Android 中 Enum 占用内存较大）
// 错误：
enum Status { IDLE, RUNNING, STOPPED }
// 正确：
@IntDef({IDLE, RUNNING, STOPPED})
@Retention(RetentionPolicy.SOURCE)
public @interface Status {}
```

### 6.3 缓存策略

```java
// 1. LruCache 内存缓存
int maxMemory = (int) (Runtime.getRuntime().maxMemory() / 1024);
int cacheSize = maxMemory / 8; // 使用 1/8 内存作为缓存

LruCache<String, Bitmap> cache = new LruCache<String, Bitmap>(cacheSize) {
    @Override
    protected int sizeOf(String key, Bitmap value) {
        return value.getByteCount() / 1024;
    }
};

// 2. DiskLruCache 磁盘缓存
// 3. Glide 自动管理缓存
```

### 6.4 对象池优化

```java
// 1. Message.obtain() 复用 Message
Message msg = Message.obtain(); // 从对象池获取
handler.sendMessage(msg);

// 2. 自定义对象池
public class ObjectPool<T> {
    private final Queue<T> pool = new LinkedList<>();
    
    public T obtain() {
        T obj = pool.poll();
        return obj != null ? obj : createNew();
    }
    
    public void recycle(T obj) {
        pool.offer(obj);
    }
}
```

---

## 7. OOM 处理

### 7.1 OOM 类型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OOM 类型                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  1. Java OOM
     - java.lang.OutOfMemoryError
     - 堆内存不足

  2. Native OOM
     - native 内存不足
     - Bitmap、JNI 分配的内存

  3. FD 耗尽
     - 文件描述符不足
     - 打开太多文件/Socket

  4. 线程数耗尽
     - 创建太多线程
     - Thread 数量达到上限
```

### 7.2 OOM 预防

```java
// 1. 大图加载前检查内存
public static boolean hasEnoughMemory(int width, int height) {
    long required = width * height * 4L; // ARGB_8888
    long available = Runtime.getRuntime().maxMemory() - 
                     Runtime.getRuntime().totalMemory() + 
                     Runtime.getRuntime().freeMemory();
    return required < available;
}

// 2. onTrimMemory 回调
@Override
public void onTrimMemory(int level) {
    super.onTrimMemory(level);
    switch (level) {
        case TRIM_MEMORY_RUNNING_LOW:
            // 释放部分缓存
            break;
        case TRIM_MEMORY_UI_HIDDEN:
            // UI 不可见，释放更多资源
            break;
    }
}

// 3. onLowMemory 回调
@Override
public void onLowMemory() {
    super.onLowMemory();
    // 系统内存不足，释放所有可释放的资源
}
```

### 7.3 大图加载方案

```java
// 方案1：分块加载（大图局部加载）
BitmapRegionDecoder decoder = BitmapRegionDecoder.newInstance(inputStream, false);
Rect rect = new Rect(0, 0, width, height);
Bitmap bitmap = decoder.decodeRegion(rect, options);

// 方案2：使用 SubsamplingScaleImageView 库
// 方案3：使用 Glide 的 thumbnail() 缩略图
Glide.with(context)
    .load(url)
    .thumbnail(0.1f) // 先加载 10% 缩略图
    .into(imageView);
```

---

## 8. 常见问题

### 8.1 如何判断是否存在内存泄漏？

```
1. 使用 LeakCanary 自动检测
2. 反复进出 Activity，观察内存是否持续增长
3. 使用 Profiler 对比内存快照
4. 查看 Activity 实例数量是否异常
```

### 8.2 内存优化的一般原则？

```
1. 对象复用，减少创建
2. 及时释放不再使用的资源
3. 使用弱引用/软引用
4. 避免在循环中创建对象
5. 合理使用缓存
```

### 8.3 如何处理 Bitmap OOM？

```
1. 使用 inSampleSize 采样
2. 使用 RGB_565 格式
3. 使用图片加载库（Glide/Picasso）
4. 及时 recycle 不用的 Bitmap
5. 使用 inBitmap 复用内存
```

---

## 9. 知识体系总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         内存优化知识体系                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   内存管理      │
                           └────────┬────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            │                                               │
            ▼                                               ▼
    ┌───────────────┐                               ┌───────────────┐
    │  内存泄漏检测  │                               │  内存优化     │
    │               │                               │               │
    │  - LeakCanary │                               │  - Bitmap     │
    │  - Profiler   │                               │  - 数据结构   │
    │  - MAT        │                               │  - 缓存策略   │
    │  - dumpsys    │                               │  - 对象池     │
    └───────────────┘                               └───────────────┘
            │
            ▼
    ┌───────────────┐
    │  泄漏场景     │
    │               │
    │  - Activity   │
    │  - Handler    │
    │  - 单例       │
    │  - 匿名类     │
    │  - 静态变量   │
    │  - 注册未取消 │
    │  - Bitmap     │
    │  - WebView    │
    └───────────────┘
```

**核心知识点：**

1. **内存泄漏本质**：对象不再使用但仍被引用，无法被 GC 回收
2. **常见泄漏场景**：Activity、Handler、单例、匿名内部类、静态变量
3. **检测工具**：LeakCanary（推荐）、Profiler、MAT、dumpsys
4. **优化策略**：Bitmap 优化、数据结构选择、缓存策略、对象复用
5. **OOM 预防**：大图检查、onTrimMemory 回调、合理使用内存

---

> 作者：OpenClaw | 日期：2026-03-09
