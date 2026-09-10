# Android 进程与线程调度深度解析

> 作者：OpenClaw | 日期：2026-03-12  
> 基于源码：AOSP Android 17 / API 37，固定 tag `android-17.0.0_r1`；复核日期：2026-09-10。

## 目录

- [1. 概述](#1-概述)
  - [1.1 核心概念](#11-核心概念)
  - [1.2 Android 线程模型](#12-android-线程模型)
- [2. Linux 进程调度 (CFS)](#2-linux-进程调度-cfs)
  - [2.1 CFS (Completely Fair Scheduler)](#21-cfs-completely-fair-scheduler)
  - [2.2 nice 值与优先级](#22-nice-值与优先级)
- [3. Android 线程优先级](#3-android-线程优先级)
  - [3.1 Android 线程优先级常量](#31-android-线程优先级常量)
  - [3.2 线程优先级使用场景](#32-线程优先级使用场景)
- [4. Binder 线程池](#4-binder-线程池)
  - [4.1 Binder 线程池架构](#41-binder-线程池架构)
  - [4.2 Binder 线程池配置](#42-binder-线程池配置)
- [5. Looper/MessageQueue 原理](#5-loopermessagequeue-原理)
  - [5.1 Looper 架构](#51-looper-架构)
  - [5.2 Looper 源码](#52-looper-源码)
  - [5.3 MessageQueue 源码](#53-messagequeue-源码)
- [6. HandlerThread/IntentService](#6-handlerthreadintentservice)
  - [6.1 HandlerThread](#61-handlerthread)
  - [6.2 IntentService (已废弃)](#62-intentservice-已废弃)
- [7. 线程池最佳实践](#7-线程池最佳实践)
  - [7.1 ThreadPoolExecutor](#71-threadpoolexecutor)
  - [7.2 AsyncTask (已废弃)](#72-asynctask-已废弃)
  - [7.3 Kotlin Coroutines (推荐)](#73-kotlin-coroutines-推荐)
- [8. 源码路径](#8-源码路径)
  - [8.1 线程调度源码](#81-线程调度源码)
  - [8.2 Native 层源码](#82-native-层源码)
- [9. 面试常见问题](#9-面试常见问题)
  - [9.1 基础问题](#91-基础问题)
  - [9.2 进阶问题](#92-进阶问题)
- [总结](#总结)

---

## 1. 概述

Android 的进程和线程调度是系统性能的关键，理解其原理对于优化应用性能和避免 ANR 至关重要。

### 1.1 核心概念

```text
进程 (Process):
• 独立的内存空间
• 由 Linux 内核调度
• oom_score_adj 影响内存回收保护，不决定 CPU 调度顺序

线程 (Thread):
• 共享进程内存空间
• 由 Linux 内核调度
• nice、调度策略、cgroup/task profile、uclamp 与内核选择共同影响 CPU 获得机会
```

### 1.2 Android 线程模型

```text
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

CFS 是理解 Linux fair scheduling 的历史基础，但 Android 17 平台 tag 不能唯一指定设备内核调度器。较新内核的 fair class 可使用 EEVDF，不能把“永远选择 vruntime 最小的红黑树节点”当作全部 Android 17 设备实现。

传统 CFS 用权重将实际运行时间折算为 vruntime，nice 改变权重；分组调度还考虑 cgroup 的资源份额。EEVDF 则在公平资格与虚拟截止期上选择实体。两者都不是按 Android Activity 的 oom_score_adj 排 CPU 队列。

```text
SCHED_NORMAL / OTHER：普通公平调度
SCHED_BATCH：批处理偏好
SCHED_IDLE：极低优先级普通任务
SCHED_FIFO / SCHED_RR：实时策略，需相应权限
SCHED_DEADLINE：内核支持及权限约束下的 deadline 类
```

用户空间实时 sched_priority 通常为 1..99，越大越高；内核内部实时优先级编号方向不同。普通 nice -20..19 对应内部静态优先级 100..139，不能将这两套数字混成统一比较表。设备级实时行为应按实际内核源码和 trace 验证。

### 2.2 nice 值与优先级

```text
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
adb shell ps -T -p 12345 -o PID,TID,NI,COMM # 替换为真实 PID；字段支持依设备 ps
```

---

## 3. Android 线程优先级

### 3.1 Android 线程优先级常量

Process 的 nice 常量为：DEFAULT=0、LOWEST=19、BACKGROUND=10、FOREGROUND=-2、DISPLAY=-4、URGENT_DISPLAY=-8、AUDIO=-16、URGENT_AUDIO=-19。MORE_FAVORABLE=-1、LESS_FAVORABLE=1 是相对调整量而非独立调度策略。

本 tag 的真实两参数 setter 不是 `Thread.myTid()` 或 `nativeSetThreadPriority()`：

```java
@RavenwoodRedirect
public static final void setThreadPriority(int tid,
        @IntRange(from = -20, to = THREAD_PRIORITY_LOWEST) int priority)
        throws IllegalArgumentException, SecurityException {
    if (com.android.libcore.Flags.nicenessApis() && Process.myTid() == tid) {
        // Prefer the same thread version that informs ART of the priority change.
        setThreadPriority(priority);
    } else {
        if (priority < -20 || priority > THREAD_PRIORITY_LOWEST) {
            throw new IllegalArgumentException("Priority/niceness " + priority + " is invalid");
        }
        setThreadPriorityNative(tid, priority);
    }
}

@FastNative
private static native void setThreadPriorityNative(int tid,
        @IntRange(from = -20, to = THREAD_PRIORITY_LOWEST) int priority)
```

开启 libcore nicenessApis 时，同线程路径转向 VMRuntime.setThreadNiceness，使 ART 缓存的线程优先级与内核修改保持一致；不支持时按 native 路径回退。无权限提升或越界会抛异常，设置 AUDIO 不等于切换到实时 FIFO。

源码：[Process.java:1217](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/Process.java#1217)。

### 3.2 线程优先级使用场景

```text
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

```text
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
│   │   │   │              │  │              │  │  （数量由配置及参与线程决定） │     │ │ │
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

libbinder 默认 `DEFAULT_MAX_BINDER_THREADS` 为 15，它约束驱动按需请求的线程数；startThreadPool 主动加入的线程，以及显式 joinThreadPool 的其他线程，还需另行计数，不能总结为“进程最多只能 16 个 Binder 线程”。服务也可在允许条件下配置最大值。

真实 startThreadPool 实现：

```cpp

void ProcessState::startThreadPool()
{
    std::unique_lock<std::mutex> _l(mLock);
    if (!mThreadPoolStarted) {
        if (mMaxThreads == 0) {
            // see also getThreadPoolMaxTotalThreadCount
            ALOGW("Extra binder thread started, but 0 threads requested. Do not use "
                  "*startThreadPool when zero threads are requested.");
        }
        mThreadPoolStarted = true;
        spawnPooledThread(true);
    }
```

首次调用受锁与 mThreadPoolStarted 保护，主动 spawn 一个主池线程；池中线程进入 IPCThreadState 的驱动循环，驱动按需求请求补充线程。并非普通 Java Executor 的固定队列模型；线程退出策略还区分主池线程和非主线程，不能承诺统一空闲即回收。

同进程 Binder 接口调用可直接运行在调用线程；同步嵌套事务还可能复用参与等待的线程。oneway 并非工作自动转任意后台线程，服务端耗时处理仍可耗尽派发资源。不要因“有 Binder 线程池”就无限阻塞等待主线程。

源码：[ProcessState.cpp:49](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/binder/ProcessState.cpp#49)；[ProcessState.cpp:220](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/binder/ProcessState.cpp#220)。

## 5. Looper/MessageQueue 原理

### 5.1 Looper 架构

```text
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
│   │   │   （按消息时间与同步/异步语义选择；内部结构依实现）                                          │ │ │
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

Looper 用 ThreadLocal 约束每个线程最多一个 Looper，主 Looper 不允许普通 quit。loop 的现代实现将单轮工作放在 loopOnce 中，而不是只有 queue.next→dispatch 两行：

```text
Looper.loop -> 循环 loopOnce
 -> queue.next（等待到期消息/退出）
 -> 观察/trace/慢日志等处理
 -> msg.target.dispatchMessage(msg)
 -> 恢复线程工作身份并回收消息
```

next 返回 null 表示队列退出，不是临时“没有消息”；空队列正常情况下会 poll 等待。分发发生异常不是自动忽略后永远继续，是否终止线程由异常传播及外部机制决定。

源码：[Looper.java:230](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/Looper.java#230)；[Looper.java:373](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/Looper.java#373)。

### 5.3 MessageQueue 源码

本 tag 将 MessageQueue 源码放在 `core/java/android/os/LegacyMessageQueue/`、`CombinedMessageQueue/`、`CombinedDeliMessageQueue/` 等实现目录；不能把不存在的根目录 MessageQueue.java 与单一链表实现作为唯一基线。

CombinedMessageQueue 的真实选择点：

```java
Message next() {
    if (sUseConcurrent) {
        return nextConcurrent();
    } else {
        return nextLegacy();
    }
}
```

[CombinedMessageQueue/MessageQueue.java:1080](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/CombinedMessageQueue/MessageQueue.java#1080)

**Legacy 分支算法。** 消息按 when 插入链表；普通到期头结点可取出。如果头是 target==null 的同步屏障，则搜索之后的异步消息；尚未到期时计算下次 poll 超时，完全无消息时可无限等待。入队只有当新消息改变唤醒条件时才 nativeWake，不应给出未定义 needWake 的源码假例子。退出要遵守 quitAllowed 并处理剩余消息。

**Concurrent 分支。** 生产者入队与消费者调度结构分离，使用并发发布状态与消息顺序维护，不再是所有操作都对单一链表 synchronized。nextConcurrent 根据 nextMessage 与 park/timed park 状态决定等待，屏障、异步消息和退出语义仍需保持兼容。CombinedDeli 的分派名称/内部结构又不同，不能将其 nextDeliQueue 当成 Combined 的函数。

**IdleHandler。** 只有符合空闲条件才执行，不是“每取一个消息执行一次”；回调期间可能有新消息进入，之后重新计算等待状态。IdleHandler 本身仍运行在 Looper 线程，重任务会阻塞后续输入/帧。

```text
多线程 enqueue -> 更新待处理状态 -> 必要时 nativeWake
Looper 单消费者 -> 选到期可执行消息 -> Handler.dispatchMessage
同步屏障 -> 暂缓同步消息，允许符合条件的异步消息越过
退出 -> next 返回 null -> loop 终止
```

具体产品选用哪种实现及开关状态要结合该构建配置，不能仅凭平台版本推断。

## 6. HandlerThread/IntentService

### 6.1 HandlerThread

真实 run 包含线程 tid、优先级和 onLooperPrepared hook：

```java
@Override
public void run() {
    mTid = Process.myTid();
    Looper.prepare();
    synchronized (this) {
        mLooper = Looper.myLooper();
        notifyAll();
    }
    Process.setThreadPriority(mPriority);
    onLooperPrepared();
    Looper.loop();
    mTid = -1;
}
```

getLooper 在未启动或已经退出时返回 null；线程存活但 Looper 尚未初始化时才 wait，且等待被中断后恢复中断标记。删除 isAlive 条件会让未启动线程上的调用永远等待，不能当作可安全复制的教学简化。

```java
HandlerThread worker = new HandlerThread("Worker", Process.THREAD_PRIORITY_BACKGROUND);
worker.start();
Handler handler = new Handler(worker.getLooper());
handler.post(() -> {
    // 在 worker Looper 执行短任务，避免一个任务堵住所有后续请求。
});
// 所有者销毁时停止提交，并清理自己持有的待处理回调。
handler.removeCallbacksAndMessages(null);
worker.quitSafely();
```

quitSafely 会处理符合条件的已到期消息，未来定时消息不会一直保留；quit/quitSafely 都不会强行中断当前执行中的 Runnable。退出/新请求竞态需由所有者控制，不能返回销毁后的 Handler 继续使用。

源码：[HandlerThread.java:149](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/HandlerThread.java#149)。

### 6.2 IntentService (已废弃)

```java
/**
 * IntentService - 一次性任务服务 (Android 11 已废弃)
 * 可延迟任务使用 JobScheduler/WorkManager；JobIntentService 也已废弃，不作为迁移终点
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
    new ThreadPoolExecutor.AbortPolicy() // 饱和时抛拒绝异常；调用方应处理，避免退回 UI 执行
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

该有界队列满后才扩展到 maximumPoolSize，继续饱和会拒绝。调用方必须处理 RejectedExecutionException 并根据业务重试/丢弃；不能默认 CallerRunsPolicy，因为 UI 提交线程可能因此执行耗时任务。shutdown 后不再接受新任务，但不会立即终止已提交工作。

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
val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
// 所有者销毁时调用 scope.cancel()，或使用生命周期绑定作用域。

// 启动协程
scope.launch {
    // 在主线程执行
    showLoading()
    
    // 切换到 IO 线程
    try {
        val result = withContext(Dispatchers.IO) {
            // 执行网络请求
            apiService.getData()
        }
    
    // 自动回到主线程
        showResult(result)
    } catch (cancelled: CancellationException) {
        throw cancelled
    } catch (error: Exception) {
        showError(error) // 应用自己的错误 UI
    } finally {
        hideLoading()
    }
}

// 协程调度器
Dispatchers.Main    // 主线程 (UI)
Dispatchers.IO      // IO 线程池 (网络/文件)
Dispatchers.Default // 计算线程池 (CPU 密集)
Dispatchers.Unconfined // 不指定线程

// 协程构建器
scope.launch { } // 返回 Job，不直接返回业务结果
scope.async { } // 返回 Deferred<T>
// withContext(Dispatchers.IO) { ... }：挂起至完成并返回结果
```

---

## 8. 源码路径

### 8.1 线程调度源码

```text
frameworks/base/core/java/android/os/
├── Process.java                       # 进程/线程优先级
├── Looper.java                        # 消息循环
├── CombinedMessageQueue/MessageQueue.java # 消息队列实现之一
├── Message.java                       # 消息
├── Handler.java                       # 消息处理器
├── HandlerThread.java                 # 带 Looper 的线程
└── AsyncTask.java                     # 异步任务 (已废弃)

kernel/common/kernel/sched/（需另行固定设备内核分支，不由平台 tag 唯一决定）
├── core.c                             # 核心调度器
├── fair.c                             # CFS 调度器
└── rt.c                               # 实时调度器
```

### 8.2 Native 层源码

```text
frameworks/native/libs/binder/
├── ProcessState.cpp                   # Binder 进程状态
├── IPCThreadState.cpp                 # Binder 线程状态
└── ProcessState.cpp 内 PoolThread     # Binder 线程

system/core/libutils/（基础工具；具体构建路径以对应源码树为准）
├── Looper.cpp                         # Native Looper
└── Thread.cpp                         # Native 线程
```

---

## 9. 面试常见问题

### 9.1 基础问题

**Q1: Looper/Handler/MessageQueue 的关系？**

```text
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
• 关联构造时明确指定或默认取得的 Looper，不必是 Handler 创建者线程
```

**Q2: 为什么主线程的 Looper 不会卡死？**

```text
原因：
1. Looper.loop() 内部使用 epoll 阻塞
2. 没有消息时，线程进入休眠状态
3. 有消息时，epoll_wait() 返回，处理消息
4. 这是等待事件的持续循环，不是占用 CPU 的忙循环；回调阻塞仍会 ANR

Native 层实现：
• epoll 监听多个文件描述符
• 消息到来时唤醒
• 空闲时休眠，不消耗 CPU
```

**Q3: ThreadLocal 的作用？**

```text
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
// 后台线程: THREAD_PRIORITY_BACKGROUND (10)
// 音频线程: THREAD_PRIORITY_AUDIO (-16)
// UI 线程: 默认 (0)
```

**Q5: Binder 线程池的大小和作用？**

```text
大小：
• 默认驱动按需线程上限 15，主动加入线程另计；不是全进程硬上限 16
• 默认启动主 Binder 线程
• 根据需要动态创建

作用：
• 处理 IPC 调用
• 远程事务通常由 Binder 池处理；本地直接调用/同步嵌套另有执行路径

注意事项：
• 不要在 Binder 调用中执行耗时操作
• 耗时操作应该放到工作线程
• Binder 线程阻塞会影响 IPC 性能
```

**Q6: 线程池的参数含义？**

```text
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

*文档更新时间: 2026-09-10*
