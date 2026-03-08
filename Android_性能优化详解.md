# Android 性能优化详解

_作者：OpenClaw_  
_日期：2026-03-08_

---

## 目录

1. [性能优化概述](#1-性能优化概述)
2. [启动优化](#2-启动优化)
3. [UI 渲染优化](#3-ui-渲染优化)
4. [内存优化](#4-内存优化)
5. [电量优化](#5-电量优化)
6. [网络优化](#6-网络优化)
7. [APK 体积优化](#7-apk-体积优化)
8. [性能分析工具](#8-性能分析工具)
9. [总结](#9-总结)

---

## 1. 性能优化概述

### 1.1 优化维度

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 性能优化维度                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────┬───────────────────────────────────────────────────────┐
│     优化维度       │                      关键指标                        │
├───────────────────┼───────────────────────────────────────────────────────┤
│     启动优化       │ 冷启动 < 5s，热启动 < 1.5s，温启动 < 2s             │
├───────────────────┼───────────────────────────────────────────────────────┤
│   UI 渲染优化      │ 60fps (16.6ms/帧)，避免卡顿                         │
├───────────────────┼───────────────────────────────────────────────────────┤
│     内存优化       │ OOM 率 < 0.1%，内存泄漏率 = 0                        │
├───────────────────┼───────────────────────────────────────────────────────┤
│     电量优化       │ 待机功耗 < 50mAh/天，后台功耗最小化                  │
├───────────────────┼───────────────────────────────────────────────────────┤
│     网络优化       │ 请求成功率 > 99%，响应时间 < 500ms                   │
├───────────────────┼───────────────────────────────────────────────────────┤
│   APK 体积优化     │ 体积 < 20MB (普通应用)，< 50MB (大型应用)           │
└───────────────────┴───────────────────────────────────────────────────────┘
```

### 1.2 性能金字塔

```
                        ┌───────────┐
                        │  用户体验  │
                        └─────┬─────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
          ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
          │   流畅    │ │   稳定    │ │   省电    │
          └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
                        ┌─────▼─────┐
                        │   启动快   │
                        └───────────┘
```

---

## 2. 启动优化

### 2.1 启动类型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         启动类型                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────┬───────────────────────────────────────────────────────┐
│     启动类型       │                      说明                            │
├───────────────────┼───────────────────────────────────────────────────────┤
│     冷启动        │ 进程不存在，需创建进程 + 初始化 Application + 启动 Activity │
│                   │ 最慢，耗时最长                                      │
├───────────────────┼───────────────────────────────────────────────────────┤
│     温启动        │ 进程存在但 Activity 被销毁，需重新创建 Activity       │
│                   │ 中等耗时                                            │
├───────────────────┼───────────────────────────────────────────────────────┤
│     热启动        │ 进程和 Activity 都存在，只需将 Activity 切换到前台    │
│                   │ 最快                                                │
└───────────────────┴───────────────────────────────────────────────────────┘
```

### 2.2 冷启动流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         冷启动流程                                          │
└─────────────────────────────────────────────────────────────────────────────┘

Launcher 点击图标
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. 启动进程 (Zygote fork)                                                  │
│     - 创建进程                                                              │
│     - 创建 ActivityThread                                                   │
│     - 创建 Application                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Application.onCreate()                                                 │
│     - 初始化第三方 SDK                                                      │
│     - 全局配置                                                              │
│     ⚠️ 耗时操作会延迟启动                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Activity 启动                                                           │
│     - 创建 Activity                                                         │
│     - onCreate() → onStart() → onResume()                                  │
│     - setContentView()                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. 首帧渲染                                                                │
│     - View 测量、布局、绘制                                                 │
│     - 第一帧显示                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 启动优化策略

```kotlin
/**
 * 启动优化策略
 */

// 1. 异步初始化
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        // 主线程：只初始化必要的组件
        initEssentialComponents()
        
        // 子线程：异步初始化非必要组件
        Thread {
            initNonEssentialComponents()
        }.start()
    }
}

// 2. 使用启动器 (TaskDispatcher)
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        TaskDispatcher.create(this)
            .addTask(InitCrashTask())      // 崩溃监控
            .addTask(InitNetworkTask())    // 网络库
            .addTask(InitImageTask())     // 图片库
            .addTask(InitDatabaseTask())   // 数据库
            .start()
    }
}

// 3. 延迟初始化
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // 使用 IdleHandler 在空闲时初始化
        Looper.myQueue().addIdleHandler {
            initNonUrgentComponents()
            false
        }
        
        // 或使用 postDelayed
        Handler(Looper.getMainLooper()).postDelayed({
            initDelayedComponents()
        }, 1000)
    }
}

// 4. 预加载
object PreloadManager {
    fun preload() {
        // 预加载类
        Class.forName("com.example.HeavyClass")
        
        // 预加载布局
        LayoutInflater.from(context).inflate(R.layout.heavy_layout, null)
        
        // 预热 WebView
        WebView(context)
    }
}
```

### 2.4 启动时间测量

```kotlin
/**
 * 启动时间测量
 */

// 1. adb 命令
// adb shell am start -W [packageName]/[activityName]
// ThisTime: 最后一个 Activity 启动时间
// TotalTime: 所有 Activity 启动时间
// WaitTime: AMS 启动时间

// 2. 代码埋点
object StartupTimer {
    private var startTime = 0L
    
    fun recordStart() {
        startTime = System.currentTimeMillis()
    }
    
    fun recordEnd(): Long {
        return System.currentTimeMillis() - startTime
    }
}

// Application.attach()
override fun attachBaseContext(base: Context) {
    super.attachBaseContext(base)
    StartupTimer.recordStart()
}

// Activity.onResume()
override fun onResume() {
    super.onResume()
    Log.d("Startup", "Cold start: ${StartupTimer.recordEnd()}ms")
}
```

---

## 3. UI 渲染优化

### 3.1 渲染流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 渲染流程                                    │
└─────────────────────────────────────────────────────────────────────────────┘

CPU (计算)                          GPU (光栅化)                    Display
   │                                    │                              │
   │  measure/layout/draw              │                              │
   │         │                         │                              │
   ▼         ▼                         │                              │
┌─────────────────────┐               │                              │
│  CPU 计算           │               │                              │
│  - Measure          │               │                              │
│  - Layout           │               │                              │
│  - Draw (生成DisplayList)          │                              │
└─────────┬───────────┘               │                              │
          │                           │                              │
          ▼                           │                              │
┌─────────────────────┐               │                              │
│  GPU 光栅化         │               │                              │
│  - 将 DisplayList   │               │                              │
│    转换为纹理       │               │                              │
└─────────┬───────────┘               │                              │
          │                           │                              │
          ▼                           ▼                              │
┌─────────────────────────────────────────────────────────────────┐          │
│  SurfaceFlinger (合成)                                          │          │
│  - 合成各层                                                      │          │
│  - 交给 Display                                                  │          │
└─────────────────────────────────────────────────────────────────┬──────────┘
                                                                  │
                                                                  ▼
                                                            屏幕显示
```

### 3.2 16ms 黄金法则

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         16ms 黄金法则                                       │
└─────────────────────────────────────────────────────────────────────────────┘

60fps = 每秒 60 帧 = 每帧 16.6ms

┌─────────────────────────────────────────────────────────────────────────────┐
│  帧时间线                                                                    │
│                                                                             │
│  帧1: │────16.6ms────│────16.6ms────│────16.6ms────│                       │
│        │    CPU+GPU   │    CPU+GPU   │    CPU+GPU   │                       │
│                                                                             │
│  如果某一帧超过 16.6ms:                                                     │
│                                                                             │
│  帧1: │─────20ms─────│                                                  │
│        │    CPU+GPU   │  ← 丢帧！屏幕显示上一帧                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 渲染优化策略

```kotlin
/**
 * 渲染优化策略
 */

// 1. 减少布局层级
// ❌ 冗余嵌套
<LinearLayout>
    <LinearLayout>
        <LinearLayout>
            <TextView />
        </LinearLayout>
    </LinearLayout>
</LinearLayout>

// ✅ 扁平化布局
<ConstraintLayout>
    <TextView />
</ConstraintLayout>

// 2. 使用 ConstraintLayout
// - 减少嵌套层级
// - 提高测量效率

// 3. 使用 merge 标签
<merge xmlns:android="...">
    <ImageView />
    <TextView />
</merge>

// 4. 使用 ViewStub 延迟加载
<ViewStub
    android:id="@+id/stub_loading"
    android:layout="@layout/loading_layout"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

// 按需加载
findViewById<ViewStub>(R.id.stub_loading).inflate()

// 5. 避免过度绘制
// 开发者选项 → 调试 GPU 过度绘制
// 4x 过度绘制 = 红色 = 需要优化

// 优化方法:
// - 移除不必要的背景
// - 使用 clipRect 限制绘制区域
// - 减少透明度混合

// 6. 自定义 View 优化
class CustomView : View {
    
    private val paint = Paint()  // 预创建，避免在 onDraw 中创建
    
    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        
        // ❌ 不要在 onDraw 中创建对象
        // val paint = Paint()
        
        // ✅ 使用预创建的对象
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
    }
}

// 7. 使用硬件加速
// Android 4.0+ 默认开启
// 在 AndroidManifest 中:
<application android:hardwareAccelerated="true">
```

### 3.4 渲染检测

```kotlin
/**
 * 渲染检测工具
 */

// 1. GPU 呈现模式分析
// 开发者选项 → GPU 呈现模式分析
// 绿线 = 16ms 阈值
// 超过绿线 = 卡顿

// 2. Systrace (Perfetto)
// 记录系统活动
// 分析帧渲染时间

// 3. Choreographer
Choreographer.getInstance().postFrameCallback(object : Choreographer.FrameCallback {
    override fun doFrame(frameTimeNanos: Long) {
        // 计算帧间隔
        val frameInterval = frameTimeNanos - lastFrameTime
        if (frameInterval > 16_666_666) {  // 16.6ms
            Log.d("Frame", "Jank detected: ${frameInterval / 1_000_000}ms")
        }
        lastFrameTime = frameTimeNanos
        
        Choreographer.getInstance().postFrameCallback(this)
    }
})
```

---

## 4. 内存优化

### 4.1 内存泄漏常见场景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         常见内存泄漏场景                                    │
└─────────────────────────────────────────────────────────────────────────────┘

1. Activity 泄漏
   - 静态变量持有 Activity
   - 单例持有 Activity
   - Handler 持有 Activity
   - 匿名内部类持有 Activity
   - 注册监听器未取消

2. 集合泄漏
   - static Map/List 持续增长
   - 未清理的缓存

3. 资源未关闭
   - Cursor 未关闭
   - Stream 未关闭
   - Bitmap 未回收

4. WebView 泄漏
   - 单独进程处理
   - 及时销毁
```

### 4.2 内存优化策略

```kotlin
/**
 * 内存优化策略
 */

// 1. 避免静态变量持有 Context
// ❌ 错误
companion object {
    private var context: Context? = null  // 泄漏！
}

// ✅ 正确
companion object {
    private var context: WeakReference<Context>? = null
}

// 2. Handler 正确使用
// ❌ 错误：持有外部类引用
class MainActivity : AppCompatActivity() {
    private val handler = Handler()
    
    private val runnable = Runnable {
        // 持有 Activity 引用
    }
}

// ✅ 正确：静态内部类 + 弱引用
class MainActivity : AppCompatActivity() {
    
    private static class SafeHandler(activity: MainActivity) : Handler(Looper.getMainLooper()) {
        private val ref: WeakReference<MainActivity> = WeakReference(activity)
        
        override fun handleMessage(msg: Message) {
            ref.get()?.let { activity ->
                // 处理消息
            }
        }
    }
    
    override fun onDestroy() {
        handler.removeCallbacksAndMessages(null)  // 清理消息
    }
}

// 3. 使用 WeakReference
class MyListener(activity: Activity) {
    private val activityRef = WeakReference(activity)
    
    fun onEvent() {
        activityRef.get()?.doSomething()
    }
}

// 4. 及时注销监听器
class MainActivity : AppCompatActivity() {
    private val broadcastReceiver = MyBroadcastReceiver()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        registerReceiver(broadcastReceiver, IntentFilter("ACTION"))
    }
    
    override fun onDestroy() {
        unregisterReceiver(broadcastReceiver)  // 必须注销
        super.onDestroy()
    }
}

// 5. Bitmap 优化
// 加载时压缩
val options = BitmapFactory.Options().apply {
    inSampleSize = 2  // 缩放比例
    inPreferredConfig = Bitmap.Config.RGB_565  // 减少内存
}
val bitmap = BitmapFactory.decodeFile(path, options)

// 及时回收
bitmap?.recycle()

// 6. 使用 AutoCloseable
Cursor::class.java.let { cursor ->
    cursor.use {
        // 使用完毕自动关闭
    }
}

// 7. 避免内存抖动
// ❌ 在循环中创建对象
for (i in 0..1000) {
    val str = "item_$i"  // 创建大量临时对象
}

// ✅ 重用对象
val sb = StringBuilder()
for (i in 0..1000) {
    sb.clear()
    sb.append("item_").append(i)
    val str = sb.toString()
}
```

### 4.3 内存分析工具

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         内存分析工具                                        │
└─────────────────────────────────────────────────────────────────────────────┘

1. Android Profiler
   - 实时内存监控
   - 内存快照 (Heap Dump)
   - 内存分配跟踪

2. LeakCanary
   - 自动检测内存泄漏
   - 显示泄漏路径

3. MAT (Memory Analyzer Tool)
   - 分析 Heap Dump
   - 查找内存泄漏

4. adb 命令
   // 查看内存信息
   adb shell dumpsys meminfo <package_name>
   
   // 触发 GC
   adb shell am broadcast -a com.android.debug.TRIGGER_GC
```

---

## 5. 电量优化

### 5.1 耗电因素

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         耗电因素排名                                        │
└─────────────────────────────────────────────────────────────────────────────┘

排名  │  因素              │  说明
─────┼────────────────────┼──────────────────────────────────────
  1  │  屏幕              │  亮度、常亮时间
  2  │  CPU               │  计算、后台任务
  3  │  网络              │  数据传输、唤醒
  4  │  GPS               │  定位
  5  │  传感器            │  加速度、陀螺仪
  6  │  唤醒锁            │  WakeLock
```

### 5.2 电量优化策略

```kotlin
/**
 * 电量优化策略
 */

// 1. 使用 JobScheduler / WorkManager
// ✅ 系统调度，合并任务
val workRequest = PeriodicWorkRequestBuilder<MyWorker>(
    15, TimeUnit.MINUTES  // 最小间隔 15 分钟
).setConstraints(
    Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .setRequiresBatteryNotLow(true)
        .build()
).build()

WorkManager.getInstance(context).enqueue(workRequest)

// 2. 使用 AlarmManager 精确唤醒
val alarmManager = getSystemService(Context.ALARM_SERVICE) as AlarmManager
val intent = Intent(this, MyReceiver::class.java)
val pendingIntent = PendingIntent.getBroadcast(this, 0, intent, PendingIntent.FLAG_IMMUTABLE)

// 使用 setAndAllowWhileIdle 或 setExactAndAllowWhileIdle
alarmManager.setAndAllowWhileIdle(
    AlarmManager.ELAPSED_REALTIME_WAKEUP,
    SystemClock.elapsedRealtime() + interval,
    pendingIntent
)

// 3. 网络批量请求
// ❌ 多次小请求
for (url in urls) {
    networkClient.get(url)  // 每次唤醒无线模块
}

// ✅ 批量请求
networkClient.batchGet(urls)  // 一次唤醒

// 4. 使用 Doze 模式
// Android 6.0+ 自动进入 Doze 模式
// 应用需要适配 Doze

// 5. 减少 WakeLock 时间
// ❌ 长时间持有
val wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "MyTag")
wakeLock.acquire()
Thread.sleep(60000)  // 60 秒
wakeLock.release()

// ✅ 设置超时
wakeLock.acquire(10 * 60 * 1000L)  // 最多 10 分钟

// 6. 定位优化
// 使用 fused location provider
val locationRequest = LocationRequest.create().apply {
    interval = 60000  // 更新间隔
    fastestInterval = 30000
    priority = LocationRequest.PRIORITY_BALANCED_POWER_ACCURACY  // 平衡精度和功耗
}

// 7. 传感器优化
// 降低采样率
sensorManager.registerListener(
    listener,
    sensor,
    SensorManager.SENSOR_DELAY_NORMAL  // 不是 SENSOR_DELAY_FASTEST
)
```

---

## 6. 网络优化

### 6.1 网络优化策略

```kotlin
/**
 * 网络优化策略
 */

// 1. 使用连接池
val client = OkHttpClient.Builder()
    .connectionPool(ConnectionPool(5, 5, TimeUnit.MINUTES))
    .build()

// 2. 开启 HTTP/2
// OkHttp 默认支持

// 3. 启用 Gzip 压缩
val client = OkHttpClient.Builder()
    .addInterceptor(GzipRequestInterceptor())
    .build()

// 4. 使用缓存
val cache = Cache(cacheDir, 10 * 1024 * 1024)  // 10MB
val client = OkHttpClient.Builder()
    .cache(cache)
    .build()

// 5. 批量请求
suspend fun fetchAllData(ids: List<Int>): List<Data> {
    return coroutineScope {
        ids.map { id ->
            async { apiService.getData(id) }
        }.awaitAll()
    }
}

// 6. 请求去重
class RequestDeduplicator {
    private val pendingRequests = mutableMapOf<String, Deferred<*>>()
    
    @Suppress("UNCHECKED_CAST")
    suspend fun <T> execute(key: String, block: suspend () -> T): T {
        return (pendingRequests.getOrPut(key) {
            GlobalScope.async { block() }
        } as Deferred<T>).await()
    }
}

// 7. 弱网优化
val client = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .writeTimeout(30, TimeUnit.SECONDS)
    .retryOnConnectionFailure(true)
    .build()
```

---

## 7. APK 体积优化

### 7.1 体积优化策略

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APK 体积优化                                        │
└─────────────────────────────────────────────────────────────────────────────┘

1. 代码优化
   - ProGuard/R8 混淆压缩
   - 移除无用代码
   - 使用 Kotlin 冗余函数

2. 资源优化
   - 压缩图片 (WebP)
   - 移除无用资源
   - 资源混淆

3. so 库优化
   - 只保留必要 ABI
   - 使用 NDK 优化

4. 使用 App Bundle
   - 动态交付
   - 按需下载
```

### 7.2 优化配置

```groovy
// build.gradle

android {
    // 开启 R8
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    
    // 只保留必要 ABI
    ndk {
        abiFilters 'armeabi-v7a', 'arm64-v8a'
    }
    
    // 资源压缩
    aaptOptions {
        cruncherEnabled = true
    }
    
    // 开启 App Bundle
    bundle {
        language {
            enableSplit = true
        }
        density {
            enableSplit = true
        }
        abi {
            enableSplit = true
        }
    }
}
```

---

## 8. 性能分析工具

### 8.1 工具列表

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         性能分析工具                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────┬───────────────────────────────────────────────────────┐
│      工具         │                      用途                            │
├───────────────────┼───────────────────────────────────────────────────────┤
│ Android Profiler  │ CPU、内存、网络、电量实时监控                        │
├───────────────────┼───────────────────────────────────────────────────────┤
│ Systrace/Perfetto │ 系统级性能分析，查看帧渲染                          │
├───────────────────┼───────────────────────────────────────────────────────┤
│ Layout Inspector  │ 查看布局层级                                         │
├───────────────────┼───────────────────────────────────────────────────────┤
│ LeakCanary        │ 内存泄漏检测                                         │
├───────────────────┼───────────────────────────────────────────────────────┤
│ StrictMode        │ 检测主线程 IO 和网络操作                             │
├───────────────────┼───────────────────────────────────────────────────────┤
│ GPU Overdraw      │ 检测过度绘制                                         │
├───────────────────┼───────────────────────────────────────────────────────┤
│ Lint              │ 静态代码分析                                         │
└───────────────────┴───────────────────────────────────────────────────────┘
```

### 8.2 StrictMode 使用

```kotlin
/**
 * StrictMode 检测主线程耗时操作
 */
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectDiskReads()
                    .detectDiskWrites()
                    .detectNetwork()
                    .penaltyLog()
                    .penaltyDeath()
                    .build()
            )
            
            StrictMode.setVmPolicy(
                StrictMode.VmPolicy.Builder()
                    .detectLeakedSqlLiteObjects()
                    .detectLeakedClosableObjects()
                    .penaltyLog()
                    .penaltyDeath()
                    .build()
            )
        }
    }
}
```

---

## 9. 总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         性能优化总结                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  启动优化:                                                                  │
│  - 异步初始化、延迟加载、预加载、启动器                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  UI 渲染优化:                                                               │
│  - 减少布局层级、避免过度绘制、16ms 法则、硬件加速                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  内存优化:                                                                  │
│  - 避免泄漏、及时回收、Bitmap 优化、弱引用                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  电量优化:                                                                  │
│  - JobScheduler/WorkManager、批量请求、WakeLock 管理                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  网络优化:                                                                  │
│  - 连接池、HTTP/2、缓存、批量请求、弱网适配                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  APK 体积优化:                                                              │
│  - R8 混淆、资源压缩、App Bundle                                            │
└─────────────────────────────────────────────────────────────────────────────┘

面试要点:
1. 启动优化策略
2. 16ms 法则与渲染流程
3. 内存泄漏常见场景与解决方案
4. 电量优化策略
5. 性能分析工具使用
```

---

*本文档由 OpenClaw 生成*
