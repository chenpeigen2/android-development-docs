# Android 后台任务详解

> 作者：OpenClaw | 日期：2026-03-09

---

## 目录

1. [概述](#1-概述)
2. [后台任务分类](#2-后台任务分类)
   - 2.1 [即时任务](#21-即时任务)
   - 2.2 [延迟任务](#22-延迟任务)
   - 2.3 [定时任务](#23-定时任务)
3. [线程基础](#3-线程基础)
   - 3.1 [Thread](#31-thread)
   - 3.2 [Handler + Looper](#32-handler--looper)
   - 3.3 [HandlerThread](#33-handlerthread)
   - 3.4 [线程池 Executor](#34-线程池-executor)
4. [异步任务方案](#4-异步任务方案)
   - 4.1 [AsyncTask（已废弃）](#41-asynctask已废弃)
   - 4.2 [Loader（已废弃）](#42-loader已废弃)
   - 4.3 [IntentService（已废弃）](#43-intentservice已废弃)
5. [现代后台任务方案](#5-现代后台任务方案)
   - 5.1 [JobScheduler](#51-jobscheduler)
   - 5.2 [JobService](#52-jobservice)
   - 5.3 [WorkManager](#53-workmanager)
   - 5.4 [WorkManager 进阶](#54-workmanager-进阶)
6. [Kotlin 协程](#6-kotlin-协程)
   - 6.1 [协程基础](#61-协程基础)
   - 6.2 [协程调度器](#62-协程调度器)
   - 6.3 [协程作用域](#63-协程作用域)
   - 6.4 [协程异常处理](#64-协程异常处理)
   - 6.5 [Flow 数据流](#65-flow-数据流)
7. [前台服务](#7-前台服务)
   - 7.1 [ForegroundService](#71-foregroundservice)
   - 7.2 [前台服务限制](#72-前台服务限制)
8. [后台执行限制](#8-后台执行限制)
   - 8.1 [Android 8.0 后台限制](#81-android-80-后台限制)
   - 8.2 [Android 9+ 限制](#82-android-9-限制)
   - 8.3 [Android 12+ 前台服务限制](#83-android-12-前台服务限制)
9. [方案选择指南](#9-方案选择指南)
10. [常见问题](#10-常见问题)
11. [知识体系总结](#11-知识体系总结)

---

## 1. 概述

Android 后台任务是开发中的核心问题。从早期的 Thread、AsyncTask 到现代的 WorkManager、Kotlin Coroutines，Android 提供了多种后台任务方案。理解各种方案的适用场景、优缺点和限制，是每个 Android 开发者的必备技能。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         后台任务演进历程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  时间线：
  ─────────────────────────────────────────────────────────────────────────
  
  2008  Android 1.0    Thread、Handler
  2009  Android 1.5    AsyncTask
  2011  Android 3.0    Loader、IntentService
  2014  Android 5.0    JobScheduler
  2017  Android 8.0    后台执行限制
  2018  Android 9.0    更严格的限制
  2018  Jetpack        WorkManager、Coroutines
  2021  Android 12     前台服务限制

  废弃情况：
  ─────────────────────────────────────────────────────────────────────────
  - AsyncTask        → Android 11 废弃，用 Coroutines 替代
  - Loader           → Android 28 废弃，用 ViewModel + LiveData 替代
  - IntentService    → Android 30 废弃，用 JobIntentService 或 WorkManager 替代
  - JobIntentService → Android 30 废弃，用 WorkManager 替代
```

---

## 2. 后台任务分类

### 2.1 即时任务

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         即时任务（Immediate）                                │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：需要立即执行的后台任务

  特点：
  - 用户触发，需要快速响应
  - 执行时间短（几秒内）
  - 需要更新 UI

  适用场景：
  - 网络请求
  - 数据库操作
  - 文件读写
  - 图片处理

  推荐方案：
  ─────────────────────────────────────────────────────────────────────────
  - Kotlin Coroutines（首选）
  - Thread + Handler
  - ExecutorService
```

### 2.2 延迟任务

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         延迟任务（Deferred）                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：可以延迟执行的后台任务

  特点：
  - 不需要立即执行
  - 可以在系统空闲时执行
  - 需要保证执行

  适用场景：
  - 数据同步
  - 日志上传
  - 缓存清理
  - 预加载资源

  推荐方案：
  ─────────────────────────────────────────────────────────────────────────
  - WorkManager（首选）
  - JobScheduler（Android 5.0+）
```

### 2.3 定时任务

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         定时任务（Periodic）                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：需要周期性执行的后台任务

  特点：
  - 固定间隔执行
  - 可能在应用退出后执行
  - 受系统 Doze 模式影响

  适用场景：
  - 定时同步数据
  - 定时检查更新
  - 定时备份数据

  推荐方案：
  ─────────────────────────────────────────────────────────────────────────
  - WorkManager（PeriodicWorkRequest）
  - AlarmManager（精确时间）
```

---

## 3. 线程基础

### 3.1 Thread

```java
/**
 * 最基础的线程使用方式
 */
public class ThreadExample {
    
    // 方式1：继承 Thread
    class MyThread extends Thread {
        @Override
        public void run() {
            // 后台任务
            String result = doWork();
            
            // 切换到主线程更新 UI
            runOnUiThread(() -> updateUI(result));
        }
    }
    
    // 方式2：实现 Runnable
    class MyRunnable implements Runnable {
        @Override
        public void run() {
            String result = doWork();
            runOnUiThread(() -> updateUI(result));
        }
    }
    
    // 使用
    public void startThread() {
        new MyThread().start();
        new Thread(new MyRunnable()).start();
        
        // Lambda 简写
        new Thread(() -> {
            String result = doWork();
            runOnUiThread(() -> updateUI(result));
        }).start();
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Thread 优缺点                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  优点：
  - 简单直接，易于理解
  - 完全控制线程生命周期

  缺点：
  - 每次创建新线程，开销大
  - 无法复用线程
  - 无法控制并发数量
  - 需要手动处理线程切换
  - 容易导致内存泄漏

  最佳实践：
  - 使用线程池替代直接创建 Thread
  - 注意内存泄漏（持有 Activity 引用）
```

### 3.2 Handler + Looper

```java
/**
 * Handler + Looper 消息机制
 */
public class HandlerExample {
    
    private Handler mainHandler;
    private Handler backgroundHandler;
    
    public void init() {
        // 主线程 Handler
        mainHandler = new Handler(Looper.getMainLooper());
        
        // 后台线程 Handler
        HandlerThread handlerThread = new HandlerThread("BackgroundThread");
        handlerThread.start();
        backgroundHandler = new Handler(handlerThread.getLooper());
    }
    
    public void doBackgroundWork() {
        // 发送任务到后台线程
        backgroundHandler.post(() -> {
            // 后台任务
            String result = doWork();
            
            // 切换到主线程
            mainHandler.post(() -> updateUI(result));
        });
    }
    
    // 延迟执行
    public void delayWork() {
        backgroundHandler.postDelayed(() -> {
            // 3 秒后执行
        }, 3000);
    }
    
    // 消息处理
    public void messageExample() {
        backgroundHandler.sendMessage(Message.obtain(backgroundHandler, msg -> {
            // 处理消息
        }));
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Handler 消息机制原理                                │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  Thread          Looper           MessageQueue        Handler          │
  │    │               │                   │                 │              │
  │    ▼               ▼                   ▼                 ▼              │
  │  ┌─────┐      ┌─────────┐        ┌─────────┐       ┌─────────┐         │
  │  │     │      │         │        │         │       │         │         │
  │  │Thread│◄────│ Looper  │◄───────│MessageQ │◄──────│Handler  │         │
  │  │     │      │ loop()  │        │         │       │ post()  │         │
  │  └─────┘      └─────────┘        └─────────┘       └─────────┘         │
  │                                                                         │
  │  流程：                                                                 │
  │  1. Handler.post(Runnable) 发送消息到 MessageQueue                     │
  │  2. Looper.loop() 不断从 MessageQueue 取出消息                          │
  │  3. 消息被分发到对应的 Handler 处理                                      │
  │  4. Handler.handleMessage() 执行任务                                    │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 HandlerThread

```java
/**
 * HandlerThread：自带 Looper 的线程
 */
public class HandlerThreadExample {
    
    private HandlerThread handlerThread;
    private Handler handler;
    
    public void init() {
        handlerThread = new HandlerThread("WorkerThread");
        handlerThread.start();
        
        // 获取 Looper 并创建 Handler
        handler = new Handler(handlerThread.getLooper()) {
            @Override
            public void handleMessage(@NonNull Message msg) {
                switch (msg.what) {
                    case 1:
                        // 处理任务1
                        break;
                    case 2:
                        // 处理任务2
                        break;
                }
            }
        };
    }
    
    public void sendTask() {
        // 发送消息
        Message msg = handler.obtainMessage(1);
        msg.obj = "data";
        handler.sendMessage(msg);
        
        // 或直接 post
        handler.post(() -> {
            // 后台任务
        });
    }
    
    public void release() {
        // 释放资源
        handlerThread.quit();
    }
}
```

### 3.4 线程池 Executor

```java
/**
 * 线程池 Executor
 */
public class ExecutorExample {
    
    // 固定大小线程池
    private ExecutorService fixedExecutor = Executors.newFixedThreadPool(4);
    
    // 缓存线程池（按需创建，60s 回收）
    private ExecutorService cachedExecutor = Executors.newCachedThreadPool();
    
    // 单线程池（顺序执行）
    private ExecutorService singleExecutor = Executors.newSingleThreadExecutor();
    
    // 定时任务线程池
    private ScheduledExecutorService scheduledExecutor = Executors.newScheduledThreadPool(2);
    
    public void execute() {
        // 提交任务
        fixedExecutor.execute(() -> {
            // 后台任务
        });
        
        // 提交有返回值的任务
        Future<String> future = fixedExecutor.submit(() -> {
            return "result";
        });
        
        try {
            String result = future.get(5, TimeUnit.SECONDS);
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        // 定时任务
        scheduledExecutor.scheduleAtFixedRate(() -> {
            // 每隔 5 秒执行
        }, 0, 5, TimeUnit.SECONDS);
    }
    
    public void shutdown() {
        fixedExecutor.shutdown();
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         线程池类型对比                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────┬─────────────────────────────────────────────────────┐
  │       线程池类型      │                      说明                            │
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │ FixedThreadPool     │ 固定线程数，适用于负载较重的场景                      │
  │                     │ corePoolSize = maxPoolSize = n                      │
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │ CachedThreadPool    │ 按需创建，60s 空闲后回收                              │
  │                     │ corePoolSize = 0, maxPoolSize = Integer.MAX_VALUE   │
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │ SingleThreadPool    │ 单线程，顺序执行                                      │
  │                     │ corePoolSize = maxPoolSize = 1                      │
  ├─────────────────────┼─────────────────────────────────────────────────────┤
  │ ScheduledThreadPool │ 定时任务，支持延迟和周期执行                          │
  │                     │ 使用 DelayedWorkQueue                               │
  └─────────────────────┴─────────────────────────────────────────────────────┘

  自定义线程池：
  ─────────────────────────────────────────────────────────────────────────
  
  ThreadPoolExecutor executor = new ThreadPoolExecutor(
      4,                      // corePoolSize 核心线程数
      10,                     // maxPoolSize 最大线程数
      60L,                    // keepAliveTime 空闲线程存活时间
      TimeUnit.SECONDS,       // 时间单位
      new LinkedBlockingQueue<>(100),  // 任务队列
      Executors.defaultThreadFactory(), // 线程工厂
      new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
  );
```

---

## 4. 异步任务方案（已废弃）

### 4.1 AsyncTask（已废弃）

```java
/**
 * AsyncTask（Android 11 废弃）
 * 了解即可，新项目使用 Coroutines
 */
@Deprecated
public class MyAsyncTask extends AsyncTask<String, Integer, String> {
    
    private WeakReference<Activity> activityRef;
    
    public MyAsyncTask(Activity activity) {
        activityRef = new WeakReference<>(activity);
    }
    
    // 在主线程执行，任务开始前
    @Override
    protected void onPreExecute() {
        super.onPreExecute();
        Activity activity = activityRef.get();
        if (activity != null) {
            // 显示进度条
        }
    }
    
    // 在子线程执行，耗时操作
    @Override
    protected String doInBackground(String... params) {
        String url = params[0];
        
        for (int i = 0; i <= 100; i++) {
            // 发布进度
            publishProgress(i);
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        
        return "result";
    }
    
    // 在主线程执行，更新进度
    @Override
    protected void onProgressUpdate(Integer... values) {
        super.onProgressUpdate(values);
        // 更新进度条
    }
    
    // 在主线程执行，任务完成后
    @Override
    protected void onPostExecute(String result) {
        super.onPostExecute(result);
        Activity activity = activityRef.get();
        if (activity != null) {
            // 更新 UI
        }
    }
    
    // 任务取消
    @Override
    protected void onCancelled(String result) {
        super.onCancelled(result);
        // 清理资源
    }
}

// 使用
new MyAsyncTask(activity).execute("http://example.com");
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AsyncTask 废弃原因                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  问题：
  1. 内存泄漏：持有 Activity 引用
  2. 屏幕旋转：配置变化导致任务丢失
  3. 线程池问题：默认串行执行
  4. 异常处理：无法正确处理异常
  5. 生命周期：与 Activity 生命周期不绑定

  替代方案：
  - Kotlin Coroutines（首选）
  - RxJava
  - Executor + LiveData
```

### 4.2 Loader（已废弃）

```java
/**
 * Loader（Android 28 废弃）
 * 使用 ViewModel + LiveData 替代
 */
@Deprecated
public class MyLoader extends AsyncTaskLoader<String> {
    
    public MyLoader(@NonNull Context context) {
        super(context);
    }
    
    @Override
    protected void onStartLoading() {
        forceLoad();
    }
    
    @Override
    public String loadInBackground() {
        return "result";
    }
}

// 使用
getLoaderManager().initLoader(0, null, new LoaderCallbacks<String>() {
    @Override
    public Loader<String> onCreateLoader(int id, Bundle args) {
        return new MyLoader(MainActivity.this);
    }
    
    @Override
    public void onLoadFinished(Loader<String> loader, String data) {
        // 更新 UI
    }
    
    @Override
    public void onLoaderReset(Loader<String> loader) {
        // 清理
    }
});
```

### 4.3 IntentService（已废弃）

```java
/**
 * IntentService（Android 30 废弃）
 * 使用 JobIntentService 或 WorkManager 替代
 */
@Deprecated
public class MyIntentService extends IntentService {
    
    public MyIntentService() {
        super("MyIntentService");
    }
    
    @Override
    protected void onHandleIntent(@Nullable Intent intent) {
        // 在子线程执行，任务完成后自动停止
        if (intent != null) {
            String action = intent.getAction();
            if ("ACTION_SYNC".equals(action)) {
                syncData();
            }
        }
    }
}

// 使用
Intent intent = new Intent(context, MyIntentService.class);
intent.setAction("ACTION_SYNC");
startService(intent);
```

---

## 5. 现代后台任务方案

### 5.1 JobScheduler

```java
/**
 * JobScheduler（Android 5.0+）
 * 系统级任务调度，适合延迟任务
 */
public class JobSchedulerExample {
    
    public void scheduleJob(Context context) {
        JobScheduler jobScheduler = (JobScheduler) 
            context.getSystemService(Context.JOB_SCHEDULER_SERVICE);
        
        ComponentName service = new ComponentName(context, MyJobService.class);
        
        JobInfo jobInfo = new JobInfo.Builder(1, service)
            // 设置条件
            .setRequiredNetworkType(JobInfo.NETWORK_TYPE_UNMETERED) // WiFi
            .setRequiresCharging(true)      // 充电时
            .setRequiresDeviceIdle(false)   // 不需要空闲
            .setRequiresBatteryNotLow(true) // 电量不低
            .setPersisted(true)             // 重启后保留
            
            // 设置时间
            .setMinimumLatency(1000)        // 最小延迟 1 秒
            .setOverrideDeadline(60000)     // 最大延迟 60 秒
            
            // 设置周期（Android 7.0+ 限制最小 15 分钟）
            .setPeriodic(15 * 60 * 1000)    // 15 分钟周期
            
            // 设置回退策略
            .setBackoffCriteria(30000, JobInfo.BACKOFF_POLICY_LINEAR)
            
            .build();
        
        int result = jobScheduler.schedule(jobInfo);
        if (result == JobScheduler.RESULT_SUCCESS) {
            Log.d("JobScheduler", "Job scheduled successfully");
        }
    }
    
    public void cancelJob(Context context, int jobId) {
        JobScheduler jobScheduler = (JobScheduler) 
            context.getSystemService(Context.JOB_SCHEDULER_SERVICE);
        jobScheduler.cancel(jobId);
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         JobScheduler 触发条件                               │
└─────────────────────────────────────────────────────────────────────────────┘

  网络条件：
  - NETWORK_TYPE_NONE        不需要网络
  - NETWORK_TYPE_ANY         任意网络
  - NETWORK_TYPE_UNMETERED   不计费网络（WiFi）
  - NETWORK_TYPE_NOT_ROAMING 非漫游网络

  设备状态：
  - setRequiresCharging()         充电时
  - setRequiresDeviceIdle()       设备空闲时
  - setRequiresBatteryNotLow()    电量不低
  - setRequiresStorageNotLow()    存储不低

  时间条件：
  - setMinimumLatency()     最小延迟
  - setOverrideDeadline()   最大延迟
  - setPeriodic()           周期执行

  存储条件：
  - setPersisted()  重启后保留（需要 RECEIVE_BOOT_COMPLETED 权限）
```

### 5.2 JobService

```java
/**
 * JobService：JobScheduler 的执行服务
 */
@RequiresApi(api = Build.VERSION_CODES.LOLLIPOP)
public class MyJobService extends JobService {
    
    @Override
    public boolean onStartJob(JobParameters params) {
        // 返回 true 表示在子线程执行，需要手动调用 jobFinished
        // 返回 false 表示任务已完成
        
        int jobId = params.getJobId();
        Log.d("MyJobService", "Job started: " + jobId);
        
        // 在子线程执行
        new Thread(() -> {
            try {
                // 执行任务
                doWork();
            } finally {
                // 任务完成，通知系统
                // false 表示不需要重试
                jobFinished(params, false);
            }
        }).start();
        
        return true;  // 任务在子线程执行
    }
    
    @Override
    public boolean onStopJob(JobParameters params) {
        // 任务被中断（如条件不再满足）
        // 返回 true 表示需要重试
        // 返回 false 表示放弃任务
        
        Log.d("MyJobService", "Job stopped: " + params.getJobId());
        return true;  // 需要重试
    }
    
    private void doWork() {
        // 耗时操作
    }
}

// 注册 Service
// AndroidManifest.xml
<service
    android:name=".MyJobService"
    android:permission="android.permission.BIND_JOB_SERVICE" />
```

### 5.3 WorkManager

```gradle
// 添加依赖
dependencies {
    def work_version = "2.9.0"
    implementation "androidx.work:work-runtime:$work_version"
    implementation "androidx.work:work-runtime-ktx:$work_version"  // Kotlin
}
```

```kotlin
/**
 * WorkManager：Jetpack 推荐的后台任务方案
 */
class MyWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    
    override fun doWork(): Result {
        return try {
            // 执行任务
            val inputData = inputData.getString("key")
            doWork(inputData)
            
            // 返回结果
            val outputData = workDataOf("result" to "success")
            Result.success(outputData)
            
        } catch (e: Exception) {
            // 失败，可以重试
            Result.failure()
        }
    }
}

// 使用
class MainActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 一次性任务
        val workRequest = OneTimeWorkRequestBuilder<MyWorker>()
            .setInputData(workDataOf("key" to "value"))
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .setRequiresCharging(true)
                    .build()
            )
            .setInitialDelay(10, TimeUnit.MINUTES)
            .setBackoffCriteria(
                BackoffPolicy.LINEAR,
                30,
                TimeUnit.SECONDS
            )
            .addTag("my_work")
            .build()
        
        // 提交任务
        WorkManager.getInstance(this).enqueue(workRequest)
        
        // 观察任务状态
        WorkManager.getInstance(this)
            .getWorkInfoByIdLiveData(workRequest.id)
            .observe(this) { workInfo ->
                when (workInfo?.state) {
                    WorkInfo.State.SUCCEEDED -> {
                        val result = workInfo.outputData.getString("result")
                    }
                    WorkInfo.State.FAILED -> {
                        // 任务失败
                    }
                    else -> {}
                }
            }
    }
}
```

### 5.4 WorkManager 进阶

```kotlin
/**
 * WorkManager 进阶用法
 */
class AdvancedWorkManager {
    
    // 1. 周期性任务（最小间隔 15 分钟）
    fun schedulePeriodicWork() {
        val periodicWork = PeriodicWorkRequestBuilder<MyWorker>(
            1, TimeUnit.HOURS,      // 重复间隔
            15, TimeUnit.MINUTES    // 灵活窗口
        )
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()
        
        WorkManager.getInstance().enqueueUniquePeriodicWork(
            "periodic_work",
            ExistingPeriodicWorkPolicy.KEEP,  // 或 REPLACE
            periodicWork
        )
    }
    
    // 2. 任务链
    fun chainWork() {
        val workA = OneTimeWorkRequestBuilder<WorkA>().build()
        val workB = OneTimeWorkRequestBuilder<WorkB>().build()
        val workC = OneTimeWorkRequestBuilder<WorkC>().build()
        
        // 顺序执行：A -> B -> C
        WorkManager.getInstance()
            .beginWith(workA)
            .then(workB)
            .then(workC)
            .enqueue()
        
        // 并行执行后合并
        WorkManager.getInstance()
            .beginWith(listOf(workA, workB))
            .then(workC)
            .enqueue()
    }
    
    // 3. 唯一任务
    fun uniqueWork() {
        val workRequest = OneTimeWorkRequestBuilder<MyWorker>().build()
        
        WorkManager.getInstance().enqueueUniqueWork(
            "unique_work",
            ExistingWorkPolicy.KEEP,     // 已存在则保留
            // ExistingWorkPolicy.REPLACE, // 已存在则替换
            // ExistingWorkPolicy.APPEND,  // 追加到已有任务后
            workRequest
        )
    }
    
    // 4. 监听所有任务
    fun observeAllWork() {
        WorkManager.getInstance()
            .getWorkInfosByTagLiveData("my_work")
            .observe(lifecycleOwner) { workInfos ->
                workInfos.forEach { info ->
                    when (info.state) {
                        WorkInfo.State.ENQUEUED -> {}
                        WorkInfo.State.RUNNING -> {}
                        WorkInfo.State.SUCCEEDED -> {}
                        WorkInfo.State.FAILED -> {}
                        WorkInfo.State.BLOCKED -> {}
                        WorkInfo.State.CANCELLED -> {}
                    }
                }
            }
    }
    
    // 5. 取消任务
    fun cancelWork() {
        // 取消单个任务
        WorkManager.getInstance().cancelWorkById(workId)
        
        // 取消标签下所有任务
        WorkManager.getInstance().cancelAllWorkByTag("my_work")
        
        // 取消唯一任务
        WorkManager.getInstance().cancelUniqueWork("unique_work")
        
        // 取消所有任务
        WorkManager.getInstance().cancelAllWork()
    }
    
    // 6. CoroutineWorker（协程支持）
    class MyCoroutineWorker(
        context: Context,
        params: WorkerParameters
    ) : CoroutineWorker(context, params) {
        
        override suspend fun doWork(): Result {
            return try {
                // 可以使用协程
                val result = withContext(Dispatchers.IO) {
                    fetchData()
                }
                Result.success()
            } catch (e: Exception) {
                Result.failure()
            }
        }
    }
    
    // 7. RxWorker（RxJava 支持）
    class MyRxWorker(
        context: Context,
        params: WorkerParameters
    ) : RxWorker(context, params) {
        
        override fun createWork(): Single<Result> {
            return doAsyncWork()
                .map { Result.success() }
                .onErrorReturnItem(Result.failure())
        }
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WorkManager 特点                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  优点：
  - 兼容 Android 4.0+（内部自动选择 JobScheduler/AlarmManager）
  - 保证任务执行（重启后恢复）
  - 支持约束条件
  - 支持任务链
  - 支持周期任务
  - 与 LiveData 集成

  限制：
  - 不能用于精确时间的任务
  - 周期任务最小间隔 15 分钟
  - 不适合需要立即执行的任务

  适用场景：
  - 数据同步
  - 日志上传
  - 缓存清理
  - 定期检查更新
```

---

## 6. Kotlin 协程

### 6.1 协程基础

```kotlin
/**
 * Kotlin 协程基础
 */

// 1. 启动协程
fun startCoroutine() {
    // GlobalScope（不推荐，生命周期不受控）
    GlobalScope.launch {
        delay(1000)
        println("GlobalScope")
    }
    
    // CoroutineScope（推荐）
    lifecycleScope.launch {
        delay(1000)
        println("CoroutineScope")
    }
    
    // viewModelScope（推荐）
    viewModelScope.launch {
        delay(1000)
        println("viewModelScope")
    }
}

// 2. suspend 函数
suspend fun fetchData(): String {
    return withContext(Dispatchers.IO) {
        // 网络请求
        delay(1000)
        "result"
    }
}

// 3. launch vs async
fun launchVsAsync() {
    lifecycleScope.launch {
        // launch：不返回结果
        launch {
            delay(1000)
            println("launch")
        }
        
        // async：返回 Deferred
        val deferred = async {
            delay(1000)
            "async result"
        }
        
        // await 获取结果
        val result = deferred.await()
        println(result)
    }
}

// 4. 并发执行
fun concurrent() {
    lifecycleScope.launch {
        val deferred1 = async { task1() }
        val deferred2 = async { task2() }
        
        // 并行执行，等待结果
        val result1 = deferred1.await()
        val result2 = deferred2.await()
        
        // 或使用 zip
        val results = awaitAll(deferred1, deferred2)
    }
}
```

### 6.2 协程调度器

```kotlin
/**
 * 协程调度器
 */
fun dispatchers() {
    lifecycleScope.launch {
        // Default：CPU 密集型任务
        launch(Dispatchers.Default) {
            // 计算密集型
            val result = heavyCalculation()
        }
        
        // IO：网络、文件、数据库
        launch(Dispatchers.IO) {
            // 网络请求
            val data = apiService.getData()
            
            // 切换到主线程
            withContext(Dispatchers.Main) {
                updateUI(data)
            }
        }
        
        // Main：主线程
        launch(Dispatchers.Main) {
            // UI 操作
            updateUI()
        }
        
        // Unconfined：不限制，不推荐使用
        launch(Dispatchers.Unconfined) {
            // 不推荐
        }
    }
}

// 自定义线程池
val myDispatcher = Executors.newFixedThreadPool(4).asCoroutineDispatcher()

lifecycleScope.launch(myDispatcher) {
    // 使用自定义线程池
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         协程调度器选择                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────────────────────────────────────────────────┐
  │     调度器       │                      适用场景                            │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ Dispatchers.Main │ 主线程，用于 UI 操作                                   │
  │                  │ 生命周期与 Activity/Fragment 绑定                       │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ Dispatchers.IO   │ 网络、文件、数据库操作                                  │
  │                  │ 内部使用线程池，可扩展                                   │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ Dispatchers.Default │ CPU 密集型任务（排序、解析、计算）                    │
  │                     │ 线程数 = CPU 核心数                                  │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ Dispatchers.Unconfined │ 不推荐使用                                        │
  └─────────────────┴─────────────────────────────────────────────────────────┘
```

### 6.3 协程作用域

```kotlin
/**
 * 协程作用域
 */

// 1. lifecycleScope（Activity/Fragment）
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 生命周期感知
        lifecycleScope.launch {
            // Activity 销毁时自动取消
        }
        
        // 生命周期状态感知
        lifecycleScope.launchWhenResumed {
            // 只有在 resumed 状态才执行
        }
        
        lifecycleScope.launchWhenStarted {
            // 只有在 started 状态才执行
        }
    }
}

// 2. viewModelScope（ViewModel）
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            // ViewModel 清除时自动取消
            val data = repository.getData()
            _data.value = data
        }
    }
}

// 3. 自定义 CoroutineScope
class MyManager : CoroutineScope {
    private val job = SupervisorJob()
    override val coroutineContext = Dispatchers.Main + job
    
    fun doWork() {
        launch {
            // 任务
        }
    }
    
    fun release() {
        job.cancel()  // 取消所有协程
    }
}

// 4. coroutineScope 函数
suspend fun loadData() = coroutineScope {
    // 创建新的作用域，等待所有子协程完成
    val deferred1 = async { task1() }
    val deferred2 = async { task2() }
    
    deferred1.await() + deferred2.await()
}

// 5. supervisorScope
suspend fun supervisedWork() = supervisorScope {
    // 子协程失败不影响其他协程
    launch {
        throw Exception("Error")
    }
    
    launch {
        // 仍会执行
    }
}
```

### 6.4 协程异常处理

```kotlin
/**
 * 协程异常处理
 */

// 1. try-catch
fun tryCatch() {
    lifecycleScope.launch {
        try {
            val data = fetchData()
        } catch (e: Exception) {
            handleError(e)
        }
    }
}

// 2. CoroutineExceptionHandler
val handler = CoroutineExceptionHandler { _, exception ->
    Log.e("Coroutine", "Caught $exception")
}

lifecycleScope.launch(handler) {
    throw Exception("Error")
}

// 3. async 异常处理
fun asyncException() {
    lifecycleScope.launch {
        val deferred = async {
            throw Exception("Error")
        }
        
        try {
            deferred.await()  // 异常在这里抛出
        } catch (e: Exception) {
            handleError(e)
        }
    }
}

// 4. SupervisorJob
fun supervisorJob() {
    val supervisor = SupervisorJob()
    val scope = CoroutineScope(Dispatchers.Main + supervisor)
    
    scope.launch {
        // 子协程失败不影响其他
    }
}
```

### 6.5 Flow 数据流

```kotlin
/**
 * Flow 数据流
 */

// 1. 创建 Flow
fun createFlow(): Flow<Int> = flow {
    for (i in 1..10) {
        delay(100)
        emit(i)  // 发射数据
    }
}

// 2. 收集 Flow
fun collectFlow() {
    lifecycleScope.launch {
        createFlow()
            .collect { value ->
                println(value)
            }
    }
}

// 3. Flow 操作符
fun flowOperators() {
    lifecycleScope.launch {
        flow {
            for (i in 1..10) {
                emit(i)
            }
        }
            .map { it * 2 }           // 转换
            .filter { it > 5 }        // 过滤
            .take(3)                  // 取前3个
            .onEach { println(it) }   // 每个元素执行
            .catch { e -> handleError(e) }  // 异常处理
            .flowOn(Dispatchers.IO)   // 指定上游线程
            .collect { value ->
                updateUI(value)
            }
    }
}

// 4. StateFlow（状态流）
class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow(0)
    val state: StateFlow<Int> = _state.asStateFlow()
    
    fun updateState(value: Int) {
        _state.value = value
    }
}

// Activity 中观察
lifecycleScope.launch {
    viewModel.state.collect { value ->
        updateUI(value)
    }
}

// 5. SharedFlow（共享流）
class MyViewModel : ViewModel() {
    private val _events = MutableSharedFlow<String>()
    val events: SharedFlow<String> = _events.asSharedFlow()
    
    fun sendEvent(message: String) {
        viewModelScope.launch {
            _events.emit(message)
        }
    }
}

// 6. cold Flow 转 hot Flow
fun coldToHot() {
    val coldFlow = flow { emit(1) }
    
    // shareIn 转为 SharedFlow
    val sharedFlow = coldFlow.shareIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        replay = 1
    )
    
    // stateIn 转为 StateFlow
    val stateFlow = coldFlow.stateIn(
        viewModelScope,
        SharingStarted.Lazily,
        initialValue = 0
    )
}
```

---

## 7. 前台服务

### 7.1 ForegroundService

```java
/**
 * 前台服务：长时间运行的后台任务
 */
public class MyForegroundService extends Service {
    
    private static final int NOTIFICATION_ID = 1;
    private static final String CHANNEL_ID = "foreground_service";
    
    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // 创建通知
        Notification notification = new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("正在下载")
            .setContentText("下载进度：0%")
            .setSmallIcon(R.drawable.ic_download)
            .setProgress(100, 0, false)
            .build();
        
        // 启动前台服务
        startForeground(NOTIFICATION_ID, notification);
        
        // 执行后台任务
        new Thread(() -> {
            for (int i = 0; i <= 100; i++) {
                try {
                    Thread.sleep(100);
                    updateProgress(i);
                } catch (InterruptedException e) {
                    break;
                }
            }
            stopForeground(true);
            stopSelf();
        }).start();
        
        return START_NOT_STICKY;
    }
    
    private void updateProgress(int progress) {
        Notification notification = new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("正在下载")
            .setContentText("下载进度：" + progress + "%")
            .setSmallIcon(R.drawable.ic_download)
            .setProgress(100, progress, false)
            .build();
        
        NotificationManager manager = 
            (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        manager.notify(NOTIFICATION_ID, notification);
    }
    
    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "前台服务",
                NotificationManager.IMPORTANCE_LOW
            );
            NotificationManager manager = getSystemService(NotificationManager.class);
            manager.createNotificationChannel(channel);
        }
    }
    
    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}

// 启动前台服务
Intent intent = new Intent(context, MyForegroundService.class);
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    startForegroundService(intent);
} else {
    startService(intent);
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         前台服务特点                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  特点：
  - 必须显示通知
  - 优先级高，不易被杀死
  - 可以长时间运行
  - 不受后台限制影响

  适用场景：
  - 音乐播放
  - 文件下载
  - GPS 定位
  - VoIP 通话

  权限：
  <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
  <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
```

### 7.2 前台服务限制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 12+ 前台服务限制                            │
└─────────────────────────────────────────────────────────────────────────────┘

  Android 14+ 需要声明服务类型：

  <service
      android:name=".MyForegroundService"
      android:foregroundServiceType="dataSync" />

  服务类型：
  ─────────────────────────────────────────────────────────────────────────
  - camera             相机
  - dataSync           数据同步
  - health             健康（Android 14+）
  - location           位置
  - mediaPlayback      媒体播放
  - mediaProjection    媒体投影
  - microphone         麦克风
  - phoneCall          电话
  - remoteMessaging    远程消息
  - shortService       短时服务（Android 14+）
  - specialUse         特殊用途（Android 14+）
  - systemExempted     系统豁免

  后台启动限制：
  ─────────────────────────────────────────────────────────────────────────
  Android 10+ 后台启动前台服务需要权限：
  <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
```

---

## 8. 后台执行限制

### 8.1 Android 8.0 后台限制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Android 8.0（API 26）后台限制                            │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 后台服务限制：
  ─────────────────────────────────────────────────────────────────────────
  - 后台应用无法创建后台服务
  - 只能创建前台服务
  - 后台应用：没有可见 Activity 且不在前台服务白名单

  2. 广播限制：
  ─────────────────────────────────────────────────────────────────────────
  - 静态注册的隐式广播不再生效
  - 需要使用动态注册或显式广播

  3. 影响的广播：
  ─────────────────────────────────────────────────────────────────────────
  - ACTION_PACKAGE_CHANGED
  - ACTION_POWER_CONNECTED/DISCONNECTED
  - CONNECTIVITY_ACTION
  - 等等

  解决方案：
  ─────────────────────────────────────────────────────────────────────────
  - 使用 JobScheduler/WorkManager
  - 动态注册广播
  - 使用前台服务
```

### 8.2 Android 9+ 限制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Android 9+ 后台限制                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 后台位置限制：
  ─────────────────────────────────────────────────────────────────────────
  - 后台应用只能获取几次位置
  - 需要前台服务 + 前台位置权限

  2. 电源管理：
  ─────────────────────────────────────────────────────────────────────────
  - Doze 模式更激进
  - 应用待机分组

  3. 网络安全：
  ─────────────────────────────────────────────────────────────────────────
  - 默认禁止明文流量
```

### 8.3 Android 12+ 前台服务限制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Android 12+ 前台服务限制                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 通知变更：
  ─────────────────────────────────────────────────────────────────────────
  - 前台服务通知可以关闭
  - 关闭通知会停止服务

  2. 后台启动限制：
  ─────────────────────────────────────────────────────────────────────────
  - 后台应用需要特殊权限才能启动前台服务
  - 需要声明 foregroundServiceType

  3. 精确闹钟限制：
  ─────────────────────────────────────────────────────────────────────────
  - 需要申请 SCHEDULE_EXACT_ALARM 权限
```

---

## 9. 方案选择指南

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         后台任务方案选择                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  问题1：任务需要立即执行吗？                                             │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  是 ──► 使用 Kotlin Coroutines                                          │
  │       - 网络请求：withContext(Dispatchers.IO)                           │
  │       - 数据库：Room + Coroutines                                       │
  │       - UI 更新：withContext(Dispatchers.Main)                          │
  │                                                                         │
  │  否 ──► 问题2：任务需要保证执行吗？                                      │
  │                                                                         │
  │  └─────────────────────────────────────────────────────────────────────┘
  │                                                                         │
  │  问题2：任务需要保证执行吗？                                             │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  是 ──► 使用 WorkManager                                                │
  │       - 数据同步                                                        │
  │       - 日志上传                                                        │
  │       - 周期性任务                                                      │
  │                                                                         │
  │  否 ──► 问题3：任务需要精确时间吗？                                      │
  │                                                                         │
  │  └─────────────────────────────────────────────────────────────────────┘
  │                                                                         │
  │  问题3：任务需要精确时间吗？                                             │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  是 ──► 使用 AlarmManager                                               │
  │       - 闹钟                                                            │
  │       - 日程提醒                                                        │
  │                                                                         │
  │  否 ──► 使用 WorkManager                                                │
  │                                                                         │
  │  └─────────────────────────────────────────────────────────────────────┘
  │                                                                         │
  │  问题4：任务需要长时间运行吗？                                           │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  是 ──► 使用 ForegroundService                                          │
  │       - 音乐播放                                                        │
  │       - 文件下载                                                        │
  │       - GPS 定位                                                        │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         方案对比表                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
  │       方案       │   即时执行   │   保证执行   │   精确时间   │   长时间    │
  ├─────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
  │ Thread          │ ✓           │ ✗           │ ✗           │ ✗           │
  │ Executor        │ ✓           │ ✗           │ ✗           │ ✗           │
  │ Coroutines      │ ✓（推荐）    │ ✗           │ ✗           │ ✗           │
  │ WorkManager     │ ✗           │ ✓（推荐）    │ ✗           │ △           │
  │ JobScheduler    │ ✗           │ ✓           │ ✗           │ △           │
  │ AlarmManager    │ ✗           │ △           │ ✓（推荐）    │ ✗           │
  │ ForegroundService│ △          │ ✓           │ ✗           │ ✓（推荐）    │
  └─────────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## 10. 常见问题

### 10.1 如何选择后台任务方案？

```
1. 立即执行，短时间 → Kotlin Coroutines
2. 延迟执行，保证执行 → WorkManager
3. 精确时间 → AlarmManager
4. 长时间运行 → ForegroundService
5. 周期性任务 → WorkManager（最小15分钟）
```

### 10.2 AsyncTask 废弃后怎么办？

```
使用 Kotlin Coroutines 替代：

// 之前
class MyTask extends AsyncTask<Void, Void, String> {
    protected String doInBackground(Void... voids) {
        return fetchData();
    }
    protected void onPostExecute(String result) {
        updateUI(result);
    }
}

// 现在
lifecycleScope.launch {
    val result = withContext(Dispatchers.IO) { fetchData() }
    updateUI(result)
}
```

### 10.3 IntentService 废弃后怎么办？

```
使用 WorkManager 或 JobIntentService 替代：

// WorkManager
class MyWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        // 任务
        return Result.success()
    }
}

// 或 JobIntentService（Android 11+ 也废弃）
class MyService : JobIntentService() {
    override fun onHandleWork(intent: Intent) {
        // 任务
    }
}
```

### 10.4 如何处理应用退出后的任务？

```
1. 使用 WorkManager（推荐）
   - 重启后自动恢复
   - 系统管理生命周期

2. 使用前台服务
   - 用户可见
   - 不会被杀死

3. 使用 AlarmManager
   - 精确时间
   - 需要处理重启
```

---

## 11. 知识体系总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         后台任务知识体系                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   后台任务      │
                           └────────┬────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
  ┌───────────┐              ┌───────────┐              ┌───────────┐
  │  即时任务  │              │  延迟任务  │              │  长时任务  │
  │           │              │           │              │           │
  │ Coroutines│              │WorkManager│              │Foreground│
  │ Executor  │              │JobScheduler│             │ Service  │
  │ Thread    │              │AlarmManager│             │          │
  └───────────┘              └───────────┘              └───────────┘
        │                           │                           │
        ▼                           ▼                           ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │                                                                       │
  │  废弃方案：                                                            │
  │  - AsyncTask（Android 11）→ Coroutines                               │
  │  - IntentService（Android 30）→ WorkManager                          │
  │  - Loader（Android 28）→ ViewModel + LiveData                        │
  │                                                                       │
  │  推荐方案：                                                            │
  │  - 即时任务：Kotlin Coroutines                                        │
  │  - 延迟任务：WorkManager                                              │
  │  - 长时任务：ForegroundService                                        │
  │  - 精确时间：AlarmManager                                             │
  │                                                                       │
  └───────────────────────────────────────────────────────────────────────┘
```

**核心知识点：**

1. **即时任务**：使用 Kotlin Coroutines，支持生命周期感知
2. **延迟任务**：使用 WorkManager，保证执行，支持约束条件
3. **周期任务**：使用 WorkManager（最小15分钟）或 AlarmManager（精确时间）
4. **长时任务**：使用 ForegroundService，需要显示通知
5. **废弃方案**：AsyncTask、IntentService、Loader 已废弃
6. **后台限制**：Android 8.0+ 后台服务限制，Android 12+ 前台服务限制

---

> 作者：OpenClaw | 日期：2026-03-09
