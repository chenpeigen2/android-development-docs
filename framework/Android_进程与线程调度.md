# Android 进程与线程调度深度解析

> 作者：OpenClaw | 日期：2026-03-12  
> 基于源码：Android 16 (API 36) AOSP

## 目录

1. [概述](#1-概述)
2. [Linux 进程调度 (CFS)](#2-linux-进程调度-cfs)
3. [Android 线程优先级](#3-android-线程优先级)
4. [Binder 线程池](#4-binder-线程池)
5. [Looper/MessageQueue 原理](#5-loopermessagequeue-原理)
6. [HandlerThread/IntentService](#6-handlerthreadintentservice)
7. [线程池最佳实践](#7-线程池最佳实践)
8. [源码路径](#8-源码路径)
9. [面试常见问题](#9-面试常见问题)

---

## 1. 概述

Android 的进程和线程调度是系统性能的关键，理解其原理对于优化应用性能和避免 ANR 至关重要。

### 1.1 核心概念

```
进程 (Process):
• 独立的内存空间
• 由 Linux 内核调度
• 通过 oom_adj 决定优先级

线程 (Thread):
• 共享进程内存空间
• 由 Linux 内核调度
• 通过 nice 值决定优先级
```

### 1.2 Android 线程模型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Android 线程模型                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    应用进程 (Application Process)                    │ │
│   │                                                                      │ │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│   │   │  主线程      │  │ Binder 线程  │  │  工作线程    │            │ │
│   │   │  (UI 线程)   │  │  (IPC 线程)  │  │  (Worker)    │            │ │
│   │   │              │  │              │  │              │            │ │
│   │   │  Looper      │  │  Binder      │  │  ThreadPool  │            │ │
│   │   │  Handler     │  │  IPC         │  │  AsyncTask   │            │ │
│   │   │  Choreographer│  │              │  │  Coroutines  │            │ │
│   │   └──────────────┘  └──────────────┘  └──────────────┘            │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Linux 进程调度 (CFS)

### 2.1 CFS (Completely Fair Scheduler)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CFS 调度器                                           │
└─────────────────────────────────────────────────────────────────────────────┘

CFS 特点：
• 完全公平调度器
• 红黑树实现
• 按虚拟运行时间 (vruntime) 排序
• 优先选择 vruntime 最小的进程

调度策略：
• SCHED_NORMAL (0): 普通进程
• SCHED_FIFO (1): 实时 FIFO
• SCHED_RR (2): 实时轮转
• SCHED_BATCH (3): 批处理
• SCHED_IDLE (5): 空闲进程

优先级：
• 实时优先级: 0-99 (数值越大优先级越高)
• 普通优先级: 100-139 (数值越小优先级越高)
• nice 值: -20 到 +19 (映射到 100-139)
```

### 2.2 nice 值与优先级

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        nice 值与优先级对应                                   │
└─────────────────────────────────────────────────────────────────────────────┘

nice 值范围: -20 (最高) 到 +19 (最低)

┌─────────────┬──────────────┬────────────────────────────────────────┐
│  nice 值    │  静态优先级  │              说明                      │
├─────────────┼──────────────┼────────────────────────────────────────┤
│  -20        │  100         │  最高优先级 (很少使用)                 │
│  -10        │  110         │  高优先级                              │
│  0          │  120         │  默认优先级                            │
│  10         │  130         │  低优先级                              │
│  19         │  139         │  最低优先级                            │
└─────────────┴──────────────┴────────────────────────────────────────┘

Android 默认 nice 值：
• 主线程: 0 (默认)
• 后台线程: 10-19 (通过 Process.setThreadPriority() 设置)

命令：
# 查看进程优先级
adb shell ps -p [pid] -o pid,comm,nice

# 设置进程优先级
adb shell renice -n 10 -p [pid]

# 查看线程优先级
adb shell getprop | grep nice
```

---

## 3. Android 线程优先级

### 3.1 Android 线程优先级常量

```java
/**
 * Android 线程优先级
 * 位置：frameworks/base/core/java/android/os/Process.java
 */
class Process {
    // 线程优先级常量
    public static final int THREAD_PRIORITY_DEFAULT = 0;           // 默认
    public static final int THREAD_PRIORITY_LOWEST = 19;           // 最低
    public static final int THREAD_PRIORITY_BACKGROUND = 10;       // 后台
    public static final int THREAD_PRIORITY_FOREGROUND = -2;       // 前台
    public static final int THREAD_PRIORITY_DISPLAY = -4;          // 显示
    public static final int THREAD_PRIORITY_URGENT_DISPLAY = -8;   // 紧急显示
    public static final int THREAD_PRIORITY_AUDIO = -16;           // 音频
    public static final int THREAD_PRIORITY_URGENT_AUDIO = -19;    // 紧急音频
    public static final int THREAD_PRIORITY_MORE_FAVORABLE = -1;   // 更高优先级
    public static final int THREAD_PRIORITY_LESS_FAVORABLE = +1;   // 更低优先级
    
    // 设置线程优先级
    public static final void setThreadPriority(int priority) {
        setThreadPriority(Thread.myTid(), priority);
    }
    
    public static final void setThreadPriority(int tid, int priority) {
        // 调用 native 方法
        nativeSetThreadPriority(tid, priority);
    }
    
    // 获取线程优先级
    public static final int getThreadPriority(int tid) {
        return nativeGetThreadPriority(tid);
    }
}
```

### 3.2 线程优先级使用场景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        线程优先级使用场景                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────────┬────────────────────────────────────────┐
│  优先级      │  值              │              使用场景                  │
├──────────────┼──────────────────┼────────────────────────────────────────┤
│  默认        │  0               │  普通工作线程                          │
│  后台        │  10              │  后台任务、缓存、预加载                │
│  最低        │  19              │  不重要的后台任务                      │
│  前台        │  -2              │  用户可感知的任务                      │
│  显示        │  -4              │  UI 相关任务                           │
│  紧急显示    │  -8              │  动画、渲染                            │
│  音频        │  -16             │  音频播放                              │
│  紧急音频    │  -19             │  实时音频处理                          │
└──────────────┴──────────────────┴────────────────────────────────────────┘

示例：
// 后台线程设置低优先级
new Thread(() -> {
    Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);
    // 执行后台任务
}).start();

// 音频线程设置高优先级
new Thread(() -> {
    Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO);
    // 执行音频处理
}).start();
```

---

## 4. Binder 线程池

### 4.1 Binder 线程池架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Binder 线程池架构                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    应用进程 (Application Process)                    │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                    Binder 线程池                              │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │ Binder 线程 1│  │ Binder 线程 2│  │ Binder 线程 N│     │ │ │
│   │   │   │              │  │              │  │  (最大 16 个) │     │ │ │
│   │   │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │ │ │
│   │   │          │                 │                 │              │ │ │
│   │   │          └─────────────────┼─────────────────┘              │ │ │
│   │   │                            │                                │ │ │
│   │   │                            ▼                                │ │ │
│   │   │   ┌────────────────────────────────────────────────────┐   │ │ │
│   │   │   │              IPC Thread State                       │   │ │ │
│   │   │   │              (Binder 驱动交互)                      │   │ │ │
│   │   │   └────────────────────────────────────────────────────┘   │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Binder 线程池配置

```java
/**
 * Binder 线程池配置
 * 位置：frameworks/native/libs/binder/ProcessState.cpp
 */
class ProcessState {
    // 最大 Binder 线程数
    static constexpr int kMaxThreadPoolSize = 16;  // 最大 16 个线程
    
    // 启动线程池
    void ProcessState::startThreadPool() {
        // 启动 Binder 线程池
        mThreadPoolStarted = true;
        spawnPooledThread(true);
    }
    
    // 生成 Binder 线程
    void ProcessState::spawnPooledThread(bool isMain) {
        if (mThreadPoolStarted) {
            String8 name = isMain ? String8("Binder:main") 
                                  : String8("Binder:%1$d");
            sp<Thread> t = new PoolThread(isMain);
            t->run(name.string());
        }
    }
}

/**
 * Binder 线程池特点
 * 
 * 1. 默认启动时创建主 Binder 线程
 * 2. 根据需要动态创建线程 (最多 16 个)
 * 3. 空闲线程会被回收
 * 4. 所有 Binder 调用在 Binder 线程中执行
 * 
 * 注意：
 * • 不要在 Binder 调用中执行耗时操作
 * • 耗时操作应该放到工作线程
 * • Binder 线程阻塞会导致 IPC 性能下降
 */
```

---

## 5. Looper/MessageQueue 原理

### 5.1 Looper 架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Looper 架构                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    Looper                                            │ │
│   │                                                                      │ │
│   │   ┌──────────────┐                                                  │ │
│   │   │  ThreadLocal │  ← 每个线程一个 Looper                           │ │
│   │   │  <Looper>    │                                                  │ │
│   │   └──────────────┘                                                  │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                    MessageQueue                               │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │  Message 1   │  │  Message 2   │  │  Message N   │     │ │ │
│   │   │   │  (when=100)  │  │  (when=200)  │  │  (when=300)  │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   │   (按时间排序的链表)                                          │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                    Native 层                                  │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │  epoll       │  │  eventfd     │  │  pipe        │     │ │ │
│   │   │   │  (IO 多路复用)│  │  (唤醒机制)  │  │  (信号)      │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Looper 源码

```java
/**
 * Looper - 消息循环
 * 位置：frameworks/base/core/java/android/os/Looper.java
 */
class Looper {
    // ThreadLocal 存储
    static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<>();
    
    // 主线程 Looper
    private static Looper sMainLooper;
    
    // 消息队列
    final MessageQueue mQueue;
    
    // 线程
    final Thread mThread;
    
    /**
     * 准备 Looper
     */
    public static void prepare() {
        prepare(true);
    }
    
    private static void prepare(boolean quitAllowed) {
        if (sThreadLocal.get() != null) {
            throw new RuntimeException(
                    "Only one Looper may be created per thread");
        }
        sThreadLocal.set(new Looper(quitAllowed));
    }
    
    /**
     * 准备主线程 Looper
     */
    public static void prepareMainLooper() {
        prepare(false);
        synchronized (Looper.class) {
            if (sMainLooper != null) {
                throw new IllegalStateException(
                        "The main Looper has already been prepared.");
            }
            sMainLooper = myLooper();
        }
    }
    
    /**
     * 消息循环
     */
    public static void loop() {
        final Looper me = myLooper();
        final MessageQueue queue = me.mQueue;
        
        for (;;) {
            // 1. 从队列取消息 (可能阻塞)
            Message msg = queue.next();
            
            if (msg == null) {
                // 没有消息，退出循环
                return;
            }
            
            // 2. 分发消息
            msg.target.dispatchMessage(msg);
            
            // 3. 回收消息
            msg.recycleUnchecked();
        }
    }
}
```

### 5.3 MessageQueue 源码

```java
/**
 * MessageQueue - 消息队列
 * 位置：frameworks/base/core/java/android/os/MessageQueue.java
 */
class MessageQueue {
    // Native 指针
    private long mPtr;
    
    // 消息链表头
    Message mMessages;
    
    /**
     * 取下一个消息
     */
    Message next() {
        int pendingIdleHandlerCount = -1;
        int nextPollTimeoutMillis = 0;
        
        for (;;) {
            if (nextPollTimeoutMillis != 0) {
                Binder.flushPendingCommands();
            }
            
            // Native 层阻塞等待
            nativePollOnce(mPtr, nextPollTimeoutMillis);
            
            synchronized (this) {
                // 获取当前时间
                final long now = SystemClock.uptimeMillis();
                Message prevMsg = null;
                Message msg = mMessages;
                
                // 遍历消息链表
                if (msg != null && msg.target == null) {
                    // 同步屏障，找第一个异步消息
                    do {
                        prevMsg = msg;
                        msg = msg.next;
                    } while (msg != null && !msg.isAsynchronous());
                }
                
                if (msg != null) {
                    if (now < msg.when) {
                        // 消息未到，计算等待时间
                        nextPollTimeoutMillis = (int) Math.min(
                                msg.when - now, Integer.MAX_VALUE);
                    } else {
                        // 消息已到，取出消息
                        if (prevMsg != null) {
                            prevMsg.next = msg.next;
                        } else {
                            mMessages = msg.next;
                        }
                        msg.next = null;
                        msg.markInUse();
                        return msg;
                    }
                } else {
                    // 没有消息，无限等待
                    nextPollTimeoutMillis = -1;
                }
                
                // 处理 IdleHandler
                if (pendingIdleHandlerCount < 0
                        && (mMessages == null || now < mMessages.when)) {
                    pendingIdleHandlerCount = mIdleHandlers.size();
                }
                
                if (pendingIdleHandlerCount <= 0) {
                    // 没有 IdleHandler，继续循环
                    mBlocked = true;
                    continue;
                }
                
                // 执行 IdleHandler
                // ...
            }
        }
    }
    
    /**
     * 入队消息
     */
    boolean enqueueMessage(Message msg, long when) {
        synchronized (this) {
            msg.when = when;
            Message p = mMessages;
            
            if (p == null || when == 0 || when < p.when) {
                // 插入队头
                msg.next = p;
                mMessages = msg;
            } else {
                // 插入链表中间
                Message prev;
                for (;;) {
                    prev = p;
                    p = p.next;
                    if (p == null || when < p.when) {
                        break;
                    }
                }
                msg.next = p;
                prev.next = msg;
            }
            
            // 唤醒 Native 层
            if (needWake) {
                nativeWake(mPtr);
            }
        }
        return true;
    }
}
```

---

## 6. HandlerThread/IntentService

### 6.1 HandlerThread

```java
/**
 * HandlerThread - 带 Looper 的线程
 * 位置：frameworks/base/core/java/android/os/HandlerThread.java
 */
class HandlerThread extends Thread {
    Looper mLooper;
    
    public HandlerThread(String name) {
        super(name);
    }
    
    @Override
    public void run() {
        // 1. 创建 Looper
        Looper.prepare();
        
        synchronized (this) {
            mLooper = Looper.myLooper();
            notifyAll(); // 通知 getLooper()
        }
        
        // 2. 进入消息循环
        Looper.loop();
    }
    
    public Looper getLooper() {
        synchronized (this) {
            while (mLooper == null) {
                try {
                    wait();
                } catch (InterruptedException e) {
                }
            }
        }
        return mLooper;
    }
    
    public boolean quit() {
        Looper looper = getLooper();
        if (looper != null) {
            looper.quit();
            return true;
        }
        return false;
    }
}

// 使用示例
HandlerThread handlerThread = new HandlerThread("WorkerThread");
handlerThread.start();

Handler handler = new Handler(handlerThread.getLooper()) {
    @Override
    public void handleMessage(Message msg) {
        // 在工作线程执行
    }
};

// 发送消息
handler.sendMessage(Message.obtain());

// 退出
handlerThread.quit();
```

### 6.2 IntentService (已废弃)

```java
/**
 * IntentService - 一次性任务服务 (Android 11 已废弃)
 * 推荐使用: JobIntentService / WorkManager
 * 
 * 位置：frameworks/base/core/java/android/app/IntentService.java
 */
@Deprecated
abstract class IntentService extends Service {
    private Looper mServiceLooper;
    private ServiceHandler mServiceHandler;
    
    @Override
    public void onCreate() {
        super.onCreate();
        HandlerThread thread = new HandlerThread("IntentService[" + mName + "]");
        thread.start();
        mServiceLooper = thread.getLooper();
        mServiceHandler = new ServiceHandler(mServiceLooper);
    }
    
    @Override
    public void onStart(Intent intent, int startId) {
        Message msg = mServiceHandler.obtainMessage();
        msg.arg1 = startId;
        msg.obj = intent;
        mServiceHandler.sendMessage(msg);
    }
    
    private final class ServiceHandler extends Handler {
        public ServiceHandler(Looper looper) {
            super(looper);
        }
        
        @Override
        public void handleMessage(Message msg) {
            onHandleIntent((Intent) msg.obj);
            stopSelf(msg.arg1);
        }
    }
    
    protected abstract void onHandleIntent(Intent intent);
}
```

---

## 7. 线程池最佳实践

### 7.1 ThreadPoolExecutor

```java
/**
 * ThreadPoolExecutor - 线程池
 * 位置：java/util/concurrent/ThreadPoolExecutor.java
 */
class ThreadPoolExecutor {
    /**
     * 构造函数
     */
    public ThreadPoolExecutor(
            int corePoolSize,           // 核心线程数
            int maximumPoolSize,        // 最大线程数
            long keepAliveTime,         // 空闲线程存活时间
            TimeUnit unit,              // 时间单位
            BlockingQueue<Runnable> workQueue, // 任务队列
            ThreadFactory threadFactory,        // 线程工厂
            RejectedExecutionHandler handler    // 拒绝策略
    ) {
        // ...
    }
}

// 使用示例
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    4,                              // 核心线程数
    8,                              // 最大线程数
    60,                             // 空闲时间
    TimeUnit.SECONDS,               // 时间单位
    new LinkedBlockingQueue<>(128), // 任务队列
    Executors.defaultThreadFactory(), // 线程工厂
    new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
);

// 提交任务
executor.execute(() -> {
    // 执行任务
});

// 提交有返回值的任务
Future<String> future = executor.submit(() -> {
    return "result";
});

// 关闭线程池
executor.shutdown();
```

### 7.2 AsyncTask (已废弃)

```java
/**
 * AsyncTask - 异步任务 (Android 11 已废弃)
 * 推荐使用: Kotlin Coroutines / ExecutorService
 * 
 * 位置：frameworks/base/core/java/android/os/AsyncTask.java
 */
@Deprecated
abstract class AsyncTask<Params, Progress, Result> {
    // 在主线程执行
    protected void onPreExecute() {}
    
    // 在工作线程执行
    protected abstract Result doInBackground(Params... params);
    
    // 在主线程执行
    protected void onPostExecute(Result result) {}
    
    // 发布进度
    protected final void publishProgress(Progress... values) {
        // 调用 onProgressUpdate()
    }
    
    // 在主线程执行
    protected void onProgressUpdate(Progress... values) {}
}

// 使用示例 (已废弃)
new AsyncTask<String, Integer, String>() {
    @Override
    protected void onPreExecute() {
        // 准备工作
    }
    
    @Override
    protected String doInBackground(String... params) {
        // 后台任务
        for (int i = 0; i < 100; i++) {
            publishProgress(i);
        }
        return "done";
    }
    
    @Override
    protected void onProgressUpdate(Integer... values) {
        // 更新进度
    }
    
    @Override
    protected void onPostExecute(String result) {
        // 完成回调
    }
}.execute("param");
```

### 7.3 Kotlin Coroutines (推荐)

```kotlin
/**
 * Kotlin Coroutines - 协程 (推荐)
 */

// 创建协程作用域
val scope = CoroutineScope(Dispatchers.Main)

// 启动协程
scope.launch {
    // 在主线程执行
    showLoading()
    
    // 切换到 IO 线程
    val result = withContext(Dispatchers.IO) {
        // 执行网络请求
        apiService.getData()
    }
    
    // 自动回到主线程
    hideLoading()
    showResult(result)
}

// 协程调度器
Dispatchers.Main    // 主线程 (UI)
Dispatchers.IO      // IO 线程池 (网络/文件)
Dispatchers.Default // 计算线程池 (CPU 密集)
Dispatchers.Unconfined // 不指定线程

// 协程构建器
launch { }      // 启动协程，不返回结果
async { }       // 启动协程，返回 Deferred<T>
withContext()   // 切换调度器
```

---

## 8. 源码路径

### 8.1 线程调度源码

```
frameworks/base/core/java/android/os/
├── Process.java                       # 进程/线程优先级
├── Looper.java                        # 消息循环
├── MessageQueue.java                  # 消息队列
├── Message.java                       # 消息
├── Handler.java                       # 消息处理器
├── HandlerThread.java                 # 带 Looper 的线程
└── AsyncTask.java                     # 异步任务 (已废弃)

kernel/sched/
├── core.c                             # 核心调度器
├── fair.c                             # CFS 调度器
└── rt.c                               # 实时调度器
```

### 8.2 Native 层源码

```
frameworks/native/libs/binder/
├── ProcessState.cpp                   # Binder 进程状态
├── IPCThreadState.cpp                 # Binder 线程状态
└── ThreadPool.cpp                     # 线程池

system/core/libutils/
├── Looper.cpp                         # Native Looper
└── Thread.cpp                         # Native 线程
```

---

## 9. 面试常见问题

### 9.1 基础问题

**Q1: Looper/Handler/MessageQueue 的关系？**

```
Looper:
• 消息循环，每个线程一个
• 内部持有 MessageQueue
• loop() 方法无限循环

MessageQueue:
• 消息队列，按时间排序
• 通过 epoll 实现阻塞等待
• next() 方法取消息

Handler:
• 发送消息到 MessageQueue
• 处理消息 (handleMessage)
• 关联到创建它的线程的 Looper
```

**Q2: 为什么主线程的 Looper 不会卡死？**

```
原因：
1. Looper.loop() 内部使用 epoll 阻塞
2. 没有消息时，线程进入休眠状态
3. 有消息时，epoll_wait() 返回，处理消息
4. 这是事件驱动模型，不是死循环

Native 层实现：
• epoll 监听多个文件描述符
• 消息到来时唤醒
• 空闲时休眠，不消耗 CPU
```

**Q3: ThreadLocal 的作用？**

```
作用：
• 线程局部变量
• 每个线程独立存储
• 用于存储线程特有的数据

Looper 使用 ThreadLocal：
• 保证每个线程只有一个 Looper
• 通过 ThreadLocal.get() 获取当前线程的 Looper
• 通过 ThreadLocal.set() 设置当前线程的 Looper
```

### 9.2 进阶问题

**Q4: Android 线程优先级如何设置？**

```java
// 设置线程优先级
Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);

// 优先级常量
THREAD_PRIORITY_DEFAULT = 0;      // 默认
THREAD_PRIORITY_BACKGROUND = 10;  // 后台
THREAD_PRIORITY_FOREGROUND = -2;  // 前台
THREAD_PRIORITY_AUDIO = -16;      // 音频

// 使用场景
• 后台线程: THREAD_PRIORITY_BACKGROUND (10)
• 音频线程: THREAD_PRIORITY_AUDIO (-16)
• UI 线程: 默认 (0)
```

**Q5: Binder 线程池的大小和作用？**

```
大小：
• 最大 16 个线程
• 默认启动主 Binder 线程
• 根据需要动态创建

作用：
• 处理 IPC 调用
• 所有 Binder 事务在 Binder 线程执行

注意事项：
• 不要在 Binder 调用中执行耗时操作
• 耗时操作应该放到工作线程
• Binder 线程阻塞会影响 IPC 性能
```

**Q6: 线程池的参数含义？**

```java
ThreadPoolExecutor(
    int corePoolSize,        // 核心线程数 (一直存在)
    int maximumPoolSize,     // 最大线程数 (任务多时创建)
    long keepAliveTime,      // 空闲线程存活时间
    TimeUnit unit,           // 时间单位
    BlockingQueue workQueue, // 任务队列
    ThreadFactory factory,   // 线程工厂
    RejectedExecutionHandler // 拒绝策略
)

任务执行流程：
1. 核心线程数未满 → 创建新线程
2. 核心线程数已满 → 加入队列
3. 队列已满 → 创建非核心线程 (最多 maximumPoolSize)
4. 线程数已达最大 → 执行拒绝策略
```

---

## 总结

本文详细讲解了 Android 进程与线程调度的核心知识点，包括：

1. **Linux CFS** - 进程调度原理
2. **线程优先级** - nice 值和优先级设置
3. **Binder 线程池** - IPC 线程管理
4. **Looper/MessageQueue** - 消息机制
5. **HandlerThread** - 带 Looper 的线程
6. **线程池** - 最佳实践

掌握这些知识点对于 Android 面试和性能优化都至关重要。

---

*文档更新时间: 2026-03-12*