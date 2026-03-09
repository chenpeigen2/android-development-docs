# Android ANR 详解

> 作者：OpenClaw | 日期：2026-03-09

---

## 目录

1. [概述](#1-概述)
2. [ANR 原理](#2-anr-原理)
   - 2.1 [什么是 ANR](#21-什么是-anr)
   - 2.2 [ANR 触发机制](#22-anr-触发机制)
   - 2.3 [ANR 超时时间](#23-anr-超时时间)
3. [ANR 类型](#3-anr-类型)
   - 3.1 [KeyDispatchTimeout](#31-keydispatchtimeout)
   - 3.2 [BroadcastTimeout](#32-broadcasttimeout)
   - 3.3 [ServiceTimeout](#33-servicetimeout)
   - 3.4 [ContentProviderTimeout](#34-contentprovidertimeout)
4. [ANR 常见原因](#4-anr-常见原因)
   - 4.1 [主线程阻塞](#41-主线程阻塞)
   - 4.2 [CPU 负载过高](#42-cpu-负载过高)
   - 4.3 [死锁](#43-死锁)
   - 4.4 [Binder 调用阻塞](#44-binder-调用阻塞)
   - 4.5 [SP 导致 ANR](#45-sp-导致-anr)
5. [ANR 分析方法](#5-anr-分析方法)
   - 5.1 [traces.txt 分析](#51-tracestxt-分析)
   - 5.2 [ANR traces 位置](#52-anr-traces-位置)
   - 5.3 [分析流程](#53-分析流程)
   - 5.4 [ANR Info 关键字段](#54-anr-info-关键字段)
6. [ANR 监控方案](#6-anr-监控方案)
   - 6.1 [FileObserver 监控](#61-fileobserver-监控)
   - 6.2 [WatchDog 机制](#62-watchdog-机制)
   - 6.3 [ANR-WatchDog 库](#63-anr-watchdog-库)
   - 6.4 [Matrix ANR 检测](#64-matrix-anr-检测)
7. [ANR 优化策略](#7-anr-优化策略)
   - 7.1 [避免主线程耗时操作](#71-避免主线程耗时操作)
   - 7.2 [优化 BroadcastReceiver](#72-优化-broadcastreceiver)
   - 7.3 [优化 Service](#73-优化-service)
   - 7.4 [优化 SP](#74-优化-sp)
   - 7.5 [优化 Binder 调用](#75-优化-binder-调用)
8. [StrictMode 严格模式](#8-strictmode-严格模式)
9. [常见问题](#9-常见问题)
10. [知识体系总结](#10-知识体系总结)

---

## 1. 概述

ANR（Application Not Responding）是 Android 系统的一种保护机制。当主线程被阻塞超过一定时间，系统会弹出 ANR 对话框，提示用户应用无响应。理解 ANR 的原理、掌握分析和优化方法，是每个 Android 开发者的必备技能。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 影响分析                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  用户体验：
  - 应用卡顿，无法交互
  - 弹出 ANR 对话框
  - 用户可能选择强制关闭应用
  - 严重影响应用评分

  系统影响：
  - 系统资源被占用
  - 可能触发 Low Memory Killer
  - 影响其他应用运行

  开发影响：
  - 崩溃率上升
  - 应用商店排名下降
  - 用户流失
```

---

## 2. ANR 原理

### 2.1 什么是 ANR

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         什么是 ANR                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：Application Not Responding（应用无响应）

  触发条件：
  1. 主线程在规定时间内没有处理完输入事件（按键、触摸等）
  2. BroadcastReceiver 在规定时间内没有执行完
  3. Service 在规定时间内没有执行完生命周期方法
  4. ContentProvider 在规定时间内没有完成发布

  本质：
  - 主线程被阻塞，无法响应消息
  - 系统检测到超时，触发 ANR
  - 弹出对话框供用户选择
```

### 2.2 ANR 触发机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 触发机制                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  核心组件：
  - ActivityManagerService（AMS）：负责 ANR 检测
  - Handler：消息调度机制
  - Looper：主线程消息循环
  - InputDispatching：输入事件分发

  触发流程：

  1. 事件发生
     - 用户按键/触摸
     - 发送广播
     - 启动 Service
     - 发布 ContentProvider

  2. AMS 记录时间戳
     - 记录事件开始时间
     - 设置超时定时器

  3. 定时检查
     - 超时时间到，检查是否完成
     - 未完成 → 触发 ANR

  4. ANR 处理
     - dump 堆栈信息到 traces.txt
     - 弹出 ANR 对话框
     - 记录 ANR 日志
```

### 2.3 ANR 超时时间

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 超时时间                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────┬───────────────────────────────────────────────────┐
  │       ANR 类型       │              超时时间（默认）                       │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 输入事件分发          │  5 秒                                            │
  │ (KeyDispatchTimeout) │  Activity.java: KEY_DISPATCHING_TIMEOUT = 5000  │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 前台广播              │  10 秒                                           │
  │ (BroadcastTimeout)   │  ActivityManagerService: BROADCAST_FG_TIMEOUT   │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 后台广播              │  60 秒                                           │
  │ (BroadcastTimeout)   │  ActivityManagerService: BROADCAST_BG_TIMEOUT   │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 前台 Service          │  20 秒                                           │
  │ (ServiceTimeout)     │  ActiveServices: SERVICE_TIMEOUT                │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 后台 Service          │  200 秒                                          │
  │ (ServiceTimeout)     │  ActiveServices: SERVICE_BACKGROUND_TIMEOUT     │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ ContentProvider      │  10 秒                                           │
  │ (ProviderTimeout)    │  ActivityManagerService: CONTENT_PROVIDER_TIMEOUT│
  └─────────────────────┴───────────────────────────────────────────────────┘

  源码位置：

  // frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java
  static final int BROADCAST_FG_TIMEOUT = 10 * 1000;  // 前台广播 10 秒
  static final int BROADCAST_BG_TIMEOUT = 60 * 1000;  // 后台广播 60 秒
  static final int CONTENT_PROVIDER_TIMEOUT = 10 * 1000; // ContentProvider 10 秒

  // frameworks/base/core/java/android/app/Activity.java
  static final int KEY_DISPATCHING_TIMEOUT = 5 * 1000; // 输入事件 5 秒

  // frameworks/base/services/core/java/com/android/server/am/ActiveServices.java
  static final int SERVICE_TIMEOUT = 20 * 1000;      // 前台 Service 20 秒
  static final int SERVICE_BACKGROUND_TIMEOUT = 200 * 1000; // 后台 Service 200 秒
```

---

## 3. ANR 类型

### 3.1 KeyDispatchTimeout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KeyDispatchTimeout（输入事件超时）                        │
└─────────────────────────────────────────────────────────────────────────────┘

  触发条件：主线程在 5 秒内没有处理完输入事件

  常见原因：
  1. 主线程执行耗时操作
     - 网络请求
     - 文件 I/O
     - 数据库操作
     - 复杂计算

  2. 主线程被锁阻塞
     - synchronized 锁等待
     - ReentrantLock 阻塞
     - 死锁

  3. Binder 调用阻塞
     - 同步 Binder 调用
     - 跨进程通信慢

  4. 系统 CPU 负载过高
     - 进程调度延迟
     - 系统资源紧张

  输入事件分发流程：

  InputEvent → InputDispatcher → InputChannel → ViewRootImpl
       │                                      │
       ▼                                      ▼
  AMS 检测超时                        DecorView.dispatchTouchEvent
       │                                      │
       ▼                                      ▼
  通知 AMS                            Activity.dispatchTouchEvent
       │                                      │
       ▼                                      ▼
  触发 ANR                            View.onTouchEvent
```

### 3.2 BroadcastTimeout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BroadcastTimeout（广播超时）                              │
└─────────────────────────────────────────────────────────────────────────────┘

  触发条件：
  - 前台广播：10 秒
  - 后台广播：60 秒

  常见原因：
  1. onReceive() 执行耗时操作
     - 网络请求
     - 文件 I/O
     - 数据库操作

  2. 有序广播阻塞
     - 前一个接收者处理慢
     - 等待后续接收者

  3. 静态广播启动进程
     - 进程启动耗时
     - 资源初始化

  // 错误示例
  public class MyReceiver extends BroadcastReceiver {
      @Override
      public void onReceive(Context context, Intent intent) {
          // 网络请求 - 耗时操作！
          String result = NetworkUtil.get("http://example.com");
      }
  }

  // 正确示例
  public class MyReceiver extends BroadcastReceiver {
      @Override
      public void onReceive(Context context, Intent intent) {
          // 启动 Service 处理
          Intent service = new Intent(context, MyService.class);
          context.startService(service);
      }
  }
```

### 3.3 ServiceTimeout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ServiceTimeout（Service 超时）                            │
└─────────────────────────────────────────────────────────────────────────────┘

  触发条件：
  - 前台 Service：20 秒
  - 后台 Service：200 秒

  涉及方法：
  - onCreate()
  - onStartCommand()
  - onBind()
  - onUnbind()
  - onDestroy()

  // 错误示例
  public class MyService extends Service {
      @Override
      public void onCreate() {
          super.onCreate();
          // 耗时操作！
          for (int i = 0; i < 100000; i++) {
              // 复杂计算
          }
      }
  }

  // 正确示例
  public class MyService extends Service {
      @Override
      public void onCreate() {
          super.onCreate();
          // 启动子线程处理
          new Thread(() -> {
              // 耗时操作
          }).start();
      }
  }

  // 使用 IntentService（已废弃，推荐使用 JobIntentService）
  public class MyIntentService extends IntentService {
      public MyIntentService() {
          super("MyIntentService");
      }

      @Override
      protected void onHandleIntent(Intent intent) {
          // 在子线程执行，不会 ANR
      }
  }
```

### 3.4 ContentProviderTimeout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                ContentProviderTimeout（ContentProvider 超时）                │
└─────────────────────────────────────────────────────────────────────────────┘

  触发条件：10 秒

  涉及方法：
  - onCreate()
  - query()
  - insert()
  - update()
  - delete()
  - getType()

  // 错误示例
  public class MyProvider extends ContentProvider {
      @Override
      public boolean onCreate() {
          // 耗时操作！
          initDatabase(); // 可能很慢
          return true;
      }

      @Override
      public Cursor query(Uri uri, String[] projection, ...) {
          // 网络请求 - 耗时！
          return networkQuery(uri);
      }
  }

  // 正确示例
  public class MyProvider extends ContentProvider {
      @Override
      public boolean onCreate() {
          // 延迟初始化
          return true;
      }

      @Override
      public Cursor query(Uri uri, String[] projection, ...) {
          // 只做本地查询
          return localQuery(uri);
      }
  }
```

---

## 4. ANR 常见原因

### 4.1 主线程阻塞

```java
// 错误示例：主线程执行耗时操作

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 1. 网络请求
        String result = NetworkUtil.get("http://example.com"); // ANR!
        
        // 2. 文件 I/O
        String content = readFile("/sdcard/large_file.txt"); // ANR!
        
        // 3. 数据库操作
        List<User> users = database.getAllUsers(); // ANR!
        
        // 4. 复杂计算
        for (int i = 0; i < 10000000; i++) {
            Math.sqrt(i); // ANR!
        }
        
        // 5. Thread.sleep()
        Thread.sleep(10000); // ANR!
    }
}

// 正确示例：使用子线程

// 1. 使用 Thread
new Thread(() -> {
    String result = NetworkUtil.get("http://example.com");
    runOnUiThread(() -> updateUI(result));
}).start();

// 2. 使用 AsyncTask
new AsyncTask<Void, Void, String>() {
    @Override
    protected String doInBackground(Void... voids) {
        return NetworkUtil.get("http://example.com");
    }
    @Override
    protected void onPostExecute(String result) {
        updateUI(result);
    }
}.execute();

// 3. 使用 ExecutorService
ExecutorService executor = Executors.newCachedThreadPool();
executor.execute(() -> {
    String result = NetworkUtil.get("http://example.com");
    runOnUiThread(() -> updateUI(result));
});

// 4. 使用 Kotlin Coroutines（推荐）
lifecycleScope.launch(Dispatchers.IO) {
    val result = NetworkUtil.get("http://example.com")
    withContext(Dispatchers.Main) {
        updateUI(result)
    }
}
```

### 4.2 CPU 负载过高

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CPU 负载过高                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  问题：即使主线程没有耗时操作，CPU 负载过高也可能导致 ANR

  原因：
  1. 后台线程占用大量 CPU
  2. 多个进程同时高负载
  3. 系统进程资源紧张
  4. GC 频繁触发

  症状：
  - traces.txt 显示主线程在处理其他消息
  - CPU 使用率持续很高
  - 多个线程处于 RUNNABLE 状态

  解决方案：
  1. 优化后台任务，降低优先级
  2. 使用 Process.setThreadPriority() 降低子线程优先级
  3. 减少后台线程数量
  4. 使用 JobScheduler 在合适时机执行

  // 降低线程优先级
  new Thread(() -> {
    Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);
    // 后台任务
  }).start();
```

### 4.3 死锁

```java
// 死锁示例

public class DeadlockExample {
    private final Object lock1 = new Object();
    private final Object lock2 = new Object();

    public void method1() {
        synchronized (lock1) {
            // 主线程持有 lock1，等待 lock2
            synchronized (lock2) {
                // 永远无法到达这里
            }
        }
    }

    public void method2() {
        synchronized (lock2) {
            // 子线程持有 lock2，等待 lock1
            synchronized (lock1) {
                // 永远无法到达这里
            }
        }
    }
}

// ANR traces.txt 会显示：
// "main" prio=5 tid=1 Blocked
//   - waiting to lock <0x12345678> (a java.lang.Object)
//   - locked <0x87654321> (a java.lang.Object)

// 避免死锁：
// 1. 固定锁顺序
// 2. 使用 tryLock() 超时
// 3. 减少锁粒度
// 4. 使用无锁数据结构
```

### 4.4 Binder 调用阻塞

```java
// Binder 调用阻塞示例

// 1. 系统 Service 调用
public void onClick(View v) {
    // PackageManager 调用可能阻塞
    PackageInfo info = getPackageManager().getPackageInfo(
        getPackageName(), PackageManager.GET_ACTIVITIES);
}

// 2. AMS 调用
public void onClick(View v) {
    // 获取运行中的任务可能阻塞
    List<ActivityManager.RunningTaskInfo> tasks = 
        ((ActivityManager) getSystemService(Context.ACTIVITY_SERVICE))
            .getRunningTasks(10);
}

// 3. 自定义 AIDL 调用
public void onClick(View v) {
    // 同步 Binder 调用
    String result = myAidlService.getData(); // 可能阻塞
}

// 解决方案：
// 1. 缓存结果，避免频繁调用
// 2. 使用异步调用
// 3. 在子线程调用
```

### 4.5 SP 导致 ANR

```java
// SharedPreferences 导致 ANR

// 错误示例：
public void onClick(View v) {
    SharedPreferences sp = getSharedPreferences("config", MODE_PRIVATE);
    
    // 1. getSharedPreferences() 可能阻塞（首次加载）
    // 2. commit() 同步写入，阻塞主线程
    sp.edit().putString("key", "value").commit(); // ANR!
}

// 正确示例：
// 1. 使用 apply() 异步写入
sp.edit().putString("key", "value").apply(); // 异步，不阻塞

// 2. 预加载 SP
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    // 在 Application 中预加载
    SharedPreferencesConfig.preload(this);
}

// 3. 使用 MMKV 替代（腾讯出品，性能更好）
MMKV.defaultMMKV().encode("key", "value");
```

---

## 5. ANR 分析方法

### 5.1 traces.txt 分析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         traces.txt 文件格式                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  // ANR 发生时间
  ----- pid 12345 at 2024-01-01 12:34:56 -----

  // 线程信息
  Cmd line: com.example.app

  // 主线程堆栈
  "main" prio=5 tid=1 Sleeping
    | group="main" sCount=1 dsCount=0 flags=1 obj=0x12345678
    | sysTid=12345 nice=0 cgrp=default sched=0/0 handle=0x12345678
    | state=S schedstat=( 123456789 12345678 12345 ) utm=12 stm=34
    | core=0 HZ=100
    | stack=0x12345678-0x12345678 stackSize=8192KB
    | held mutexes=
    at java.lang.Thread.sleep(Native Method)
    - sleeping on <0x12345678> (a java.lang.Object)
    at java.lang.Thread.sleep(Thread.java:373)
    at java.lang.Thread.sleep(Thread.java:314)
    at com.example.app.MainActivity$1.run(MainActivity.java:42)
    at android.os.Handler.handleCallback(Handler.java:883)
    at android.os.Handler.dispatchMessage(Handler.java:100)
    at android.os.Looper.loop(Looper.java:214)
    at android.app.ActivityThread.main(ActivityThread.java:7356)
    at java.lang.reflect.Method.invoke(Native Method)
    at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run
    at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:950)
```

### 5.2 ANR traces 位置

```bash
# Android 10 及以下
/data/anr/traces.txt

# Android 11+（需要 root）
/data/anr/anr_*

# 通过 adb 获取
adb pull /data/anr/traces.txt ./

# 通过 bugreport 获取
adb bugreport ./bugreport.zip
# 解压后在 FS/data/anr/ 目录下

# 通过 dropbox 获取（系统应用）
adb shell dumpsys dropbox --print 0 app_anr
```

### 5.3 分析流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 分析流程                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  Step 1: 获取 traces.txt
  ─────────────────────────────────────────────────────────────────────────
  - adb pull /data/anr/traces.txt
  - 或从 bugreport 中提取

  Step 2: 找到主线程
  ─────────────────────────────────────────────────────────────────────────
  - 搜索 "main" prio=5 tid=1
  - 查看主线程状态（Sleeping/Blocked/Runnable）

  Step 3: 分析主线程堆栈
  ─────────────────────────────────────────────────────────────────────────
  - 从上往下看调用栈
  - 找到业务代码位置
  - 确定阻塞原因

  Step 4: 检查其他线程
  ─────────────────────────────────────────────────────────────────────────
  - 查看是否有死锁
  - 检查 Binder 调用
  - 查看锁持有情况

  Step 5: 结合 ANR Info
  ─────────────────────────────────────────────────────────────────────────
  - 查看 ANR 类型
  - 检查 CPU 使用率
  - 分析进程状态
```

### 5.4 ANR Info 关键字段

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR Info 关键字段                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  // ANR 类型
  Reason: Input dispatching timed out (Waiting because no window has focus)

  // 进程信息
  PID: 12345
  Reason: executing service com.example.app/.MyService

  // CPU 使用情况
  Load: 8.5 / 7.2 / 5.1   // 1/5/15 分钟负载
  CPU usage from 0ms to 12345ms later (2024-01-01 12:34:56.123):
    50% 12345/com.example.app: 25% user + 25% kernel
    30% 567/system_server: 20% user + 10% kernel
    10% 890/com.android.systemui: 8% user + 2% kernel

  关键分析点：
  1. Reason - ANR 原因
  2. Load - 系统负载
  3. CPU usage - 各进程 CPU 使用率
  4. 主线程状态 - Sleeping/Blocked/Runnable
```

---

## 6. ANR 监控方案

### 6.1 FileObserver 监控

```java
/**
 * 监控 /data/anr/ 目录变化
 * 需要 root 权限或 debuggable 应用
 */
public class ANRFileObserver extends FileObserver {
    private static final String ANR_PATH = "/data/anr/";
    
    public ANRFileObserver() {
        super(ANR_PATH, FileObserver.CREATE | FileObserver.MODIFY);
    }
    
    @Override
    public void onEvent(int event, String path) {
        if (path != null && path.startsWith("anr_")) {
            // 检测到 ANR 文件
            Log.e("ANR", "ANR detected: " + path);
            // 上传或分析 traces
            analyzeANRFile(ANR_PATH + path);
        }
    }
}
```

### 6.2 WatchDog 机制

```java
/**
 * 自定义 WatchDog 检测主线程卡顿
 */
public class ANRWatchDog extends Thread {
    private static final int ANR_TIMEOUT = 5000; // 5 秒
    
    private volatile int tick = 0;
    private volatile boolean reported = false;
    
    private final Runnable ticker = new Runnable() {
        @Override
        public void run() {
            tick = 0;
            reported = false;
        }
    };
    
    @Override
    public void run() {
        setName("ANR-WatchDog");
        
        while (true) {
            boolean needPost = tick == 0;
            tick++;
            
            if (tick == 1 && !reported) {
                if (needPost) {
                    new Handler(Looper.getMainLooper()).post(ticker);
                }
            }
            
            try {
                Thread.sleep(ANR_TIMEOUT);
            } catch (InterruptedException e) {
                break;
            }
            
            // 如果 tick > 1，说明主线程没有响应
            if (tick >= 2 && !reported) {
                reported = true;
                onANRDetect();
            }
        }
    }
    
    private void onANRDetect() {
        Log.e("ANRWatchDog", "ANR detected!");
        // 打印主线程堆栈
        StackTraceElement[] stackTrace = Looper.getMainLooper()
            .getThread().getStackTrace();
        Log.e("ANRWatchDog", Arrays.toString(stackTrace));
    }
}
```

### 6.3 ANR-WatchDog 库

```gradle
// 添加依赖
dependencies {
    implementation 'com.github.anrwatchdog:anrwatchdog:1.4.0'
}
```

```java
// 在 Application 中初始化
public class MyApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        
        new ANRWatchDog()
            .setReportMainThreadOnly()
            .setANRListener(error -> {
                // 自定义处理
                Log.e("ANR", error.getMessage());
            })
            .start();
    }
}
```

### 6.4 Matrix ANR 检测

```gradle
// 添加 Matrix 依赖
dependencies {
    implementation 'com.tencent.matrix:matrix-android-lib:0.8.0'
    implementation 'com.tencent.matrix:matrix-android-commons:0.8.0'
    implementation 'com.tencent.matrix:matrix-trace-canary:0.8.0'
}
```

```java
// 初始化 Matrix
public class MyApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        
        Matrix.Builder builder = new Matrix.Builder(this);
        
        // ANR 检测
        builder.plugin(new TracePlugin(new TraceConfig.Builder()
            .setEnableAnrTrace(true)
            .build()));
        
        Matrix.init(builder.build());
        Matrix.with().startAllPlugins();
    }
}
```

---

## 7. ANR 优化策略

### 7.1 避免主线程耗时操作

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    避免主线程耗时操作                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 网络请求
  ─────────────────────────────────────────────────────────────────────────
  - 使用 OkHttp/Retrofit 异步请求
  - 使用 Coroutines/Okio 异步

  2. 文件 I/O
  ─────────────────────────────────────────────────────────────────────────
  - 使用子线程
  - 使用 Okio 优化

  3. 数据库操作
  ─────────────────────────────────────────────────────────────────────────
  - 使用 Room + Coroutines
  - 使用 WorkManager

  4. 复杂计算
  ─────────────────────────────────────────────────────────────────────────
  - 使用子线程
  - 使用 RenderScript（图像处理）
  - 使用 NDK（复杂计算）
```

### 7.2 优化 BroadcastReceiver

```java
// 1. 避免在 onReceive() 中执行耗时操作
public class MyReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        // 启动 Service 处理
        Intent service = new Intent(context, MyService.class);
        context.startService(service);
    }
}

// 2. 使用 goAsync() 延长处理时间
public class MyReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        final PendingResult pendingResult = goAsync();
        new Thread(() -> {
            try {
                // 耗时操作
            } finally {
                pendingResult.finish();
            }
        }).start();
    }
}

// 3. 动态注册替代静态注册（减少进程启动）
```

### 7.3 优化 Service

```java
// 1. 使用 JobService 替代普通 Service
public class MyJobService extends JobService {
    @Override
    public boolean onStartJob(JobParameters params) {
        // 在子线程执行
        new Thread(() -> {
            // 耗时操作
            jobFinished(params, false);
        }).start();
        return true;
    }
    
    @Override
    public boolean onStopJob(JobParameters params) {
        return false;
    }
}

// 2. 使用 WorkManager
public class MyWorker extends Worker {
    public MyWorker(Context context, WorkerParameters params) {
        super(context, params);
    }
    
    @Override
    public Result doWork() {
        // 后台任务
        return Result.success();
    }
}

// 3. 前台 Service（延长超时时间到 20 秒）
public class MyForegroundService extends Service {
    @Override
    public void onCreate() {
        super.onCreate();
        
        Notification notification = new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Service Running")
            .build();
            
        startForeground(1, notification);
    }
}
```

### 7.4 优化 SP

```java
// 1. 使用 apply() 替代 commit()
SharedPreferences sp = getSharedPreferences("config", MODE_PRIVATE);
sp.edit().putString("key", "value").apply(); // 异步

// 2. 预加载 SP
public class App extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        // 预加载常用 SP
        SharedPreferences preLoad = getSharedPreferences("preload", MODE_PRIVATE);
    }
}

// 3. 使用 MMKV 替代
MMKV kv = MMKV.defaultMMKV();
kv.encode("key", "value"); // 同步但极快
String value = kv.decodeString("key", null);
```

### 7.5 优化 Binder 调用

```java
// 1. 缓存结果
private PackageInfo cachedPackageInfo;

public PackageInfo getPackageInfo() {
    if (cachedPackageInfo == null) {
        cachedPackageInfo = getPackageManager().getPackageInfo(
            getPackageName(), PackageManager.GET_ACTIVITIES);
    }
    return cachedPackageInfo;
}

// 2. 异步调用
new Thread(() -> {
    PackageInfo info = getPackageManager().getPackageInfo(...);
    runOnUiThread(() -> updateUI(info));
}).start();

// 3. 减少调用频率
// 避免频繁调用系统服务
```

---

## 8. StrictMode 严格模式

```java
/**
 * StrictMode 用于检测主线程的磁盘和网络操作
 * 仅在 Debug 模式启用
 */
public class MyApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(new StrictMode.ThreadPolicy.Builder()
                .detectDiskReads()      // 检测磁盘读
                .detectDiskWrites()     // 检测磁盘写
                .detectNetwork()        // 检测网络操作
                .penaltyLog()           // 打印日志
                .penaltyDialog()        // 弹出对话框
                .build());
                
            StrictMode.setVmPolicy(new StrictMode.VmPolicy.Builder()
                .detectActivityLeaks()  // 检测 Activity 泄漏
                .detectLeakedSqlLiteObjects()  // 检测 SQLite 泄漏
                .penaltyLog()
                .build());
        }
    }
}
```

---

## 9. 常见问题

### 9.1 如何快速定位 ANR？

```
1. 获取 traces.txt
2. 找到 "main" 线程
3. 看堆栈最顶部的业务代码
4. 检查是否有锁等待
```

### 9.2 如何预防 ANR？

```
1. 主线程只做 UI 操作
2. 耗时操作放到子线程
3. 使用 StrictMode 检测
4. 使用 ANR 监控库
```

### 9.3 traces.txt 显示 "native" 方法？

```
可能是：
1. Native 代码阻塞
2. 等待锁
3. Binder 调用
4. I/O 操作
```

---

## 10. 知识体系总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 知识体系                                        │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   ANR 检测      │
                           └────────┬────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            │                                               │
            ▼                                               ▼
    ┌───────────────┐                               ┌───────────────┐
    │  分析方法     │                               │  监控方案     │
    │               │                               │               │
    │  - traces.txt │                               │  - FileObserver│
    │  - ANR Info   │                               │  - WatchDog   │
    │  - bugreport  │                               │  - Matrix     │
    └───────────────┘                               └───────────────┘
            │
            ▼
    ┌───────────────┐
    │  ANR 类型     │
    │               │
    │  - Input      │
    │  - Broadcast  │
    │  - Service    │
    │  - Provider   │
    └───────────────┘
```

**核心知识点：**

1. **ANR 本质**：主线程被阻塞超过超时时间
2. **四种类型**：Input（5s）、Broadcast（10s/60s）、Service（20s/200s）、Provider（10s）
3. **常见原因**：主线程耗时操作、死锁、Binder 阻塞、CPU 负载高
4. **分析方法**：traces.txt 堆栈分析
5. **监控方案**：FileObserver、WatchDog、Matrix
6. **优化策略**：耗时操作子线程化、使用 apply() 替代 commit()

---

> 作者：OpenClaw | 日期：2026-03-09