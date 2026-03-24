# Android 多线程与并发详解

> 作者：依葫芦画瓢 | 日期：2026-03-24
> 定位：Android 资深工程师 | 专注系统底层、架构设计、性能优化

---

## 目录

1. [概述](#1-概述)
2. [Java 线程基础](#2-java-线程基础)
   - 2.1 [Thread 创建与启动](#21-thread-创建与启动)
   - 2.2 [线程状态与生命周期](#22-线程状态与生命周期)
   - 2.3 [线程优先级](#23-线程优先级)
   - 2.4 [守护线程](#24-守护线程)
3. [线程同步机制](#3-线程同步机制)
   - 3.1 [synchronized](#31-synchronized)
   - 3.2 [volatile](#32-volatile)
   - 3.3 [wait/notify/notifyAll](#33-waitnotifynotifyall)
   - 3.4 [Lock 与 ReentrantLock](#34-lock-与-reentrantlock)
   - 3.5 [ReadWriteLock](#35-readwritelock)
   - 3.6 [Condition](#36-condition)
   - 3.7 [StampedLock](#37-stampedlock)
4. [Java 并发工具类](#4-java-并发工具类)
   - 4.1 [CountDownLatch](#41-countdownlatch)
   - 4.2 [CyclicBarrier](#42-cyclicbarrier)
   - 4.3 [Semaphore](#43-semaphore)
   - 4.4 [Exchanger](#44-exchanger)
   - 4.5 [Phaser](#45-phaser)
5. [原子类与 CAS](#5-原子类与-cas)
   - 5.1 [AtomicInteger/AtomicLong](#51-atomicintegeratomiclong)
   - 5.2 [AtomicReference](#52-atomicreference)
   - 5.3 [AtomicIntegerFieldUpdater](#53-atomicintegerfieldupdater)
   - 5.4 [LongAdder（高并发场景）](#54-longadder高并发场景)
   - 5.5 [CAS 原理](#55-cas-原理)
6. [并发集合](#6-并发集合)
   - 6.1 [ConcurrentHashMap](#61-concurrenthashmap)
   - 6.2 [CopyOnWriteArrayList](#62-copyonwritearraylist)
   - 6.3 [BlockingQueue](#63-blockingqueue)
   - 6.4 [ConcurrentLinkedQueue/Deque](#64-concurrentlinkedqueuedeque)
   - 6.5 [ThreadLocalMap](#65-threadlocalmap)
7. [线程池](#7-线程池)
   - 7.1 [ThreadPoolExecutor 核心参数](#71-threadpoolexecutor-核心参数)
   - 7.2 [线程池执行流程](#72-线程池执行流程)
   - 7.3 [线程池分类](#73-线程池分类)
   - 7.4 [线程池饱和策略](#74-线程池饱和策略)
   - 7.5 [线程池参数配置](#75-线程池参数配置)
8. [Kotlin 协程原理](#8-kotlin-协程原理)
   - 8.1 [协程是什么](#81-协程是什么)
   - 8.2 [协程调度器](#82-协程调度器-dispatchers)
   - 8.3 [协程上下文与作用域](#83-协程上下文与作用域)
   - 8.4 [suspend 原理](#84-suspend-原理)
   - 8.5 [协程构建器](#85-协程构建器)
   - 8.6 [协程取消](#86-协程取消)
   - 8.7 [协程异常处理](#87-协程异常处理)
   - 8.8 [Flow 异步数据流](#88-flow-异步数据流)
9. [Android 线程模型](#9-android-线程模型)
   - 9.1 [主线程职责](#91-主线程职责)
   - 9.2 [Binder 线程池](#92-binder-线程池)
   - 9.3 [Android 特有的线程优先级](#93-android-特有的线程优先级)
10. [并发设计模式](#10-并发设计模式)
    - 10.1 [Thread-Per-Message](#101-thread-per-message)
    - 10.2 [Worker Thread](#102-worker-thread)
    - 10.3 [Producer-Consumer](#103-producer-consumer)
    - 10.4 [Pipeline](#104-pipeline)
    - 10.5 [Actor 模型](#105-actor-模型)
11. [性能与反模式](#11-性能与反模式)
    - 11.1 [常见性能问题](#111-常见性能问题)
    - 11.2 [并发反模式](#112-并发反模式)
12. [面试高频问题](#12-面试高频问题)
13. [Android 并发专题](#13-android-并发专题)
    - 13.1 [Handler 与线程](#131-handler-与线程)
    - 13.2 [runOnUiThread vs post vs View.post](#132-runonuithread-vs-post-vs-viewpost)
    - 13.3 [IntentService vs JobIntentService](#133-intentservice-vs-jobintentservice)
    - 13.4 [AsyncTask 废弃原因](#134-asyncTask-废弃原因)
    - 13.5 [WorkManager 并发模型](#135-workmanager-并发模型)
    - 13.6 [子线程操作 Android UI 的正确方式](#136-子线程操作-android-ui-的正确方式)

---

## 1. 概述

多线程与并发是 Android 开发中最核心的能力之一，也是面试的重点难点。本质问题是：**如何让多个任务在同一时间段内"同时执行"，同时保证数据安全、线程安全。**

现代 Android 开发虽然已经进入 Kotlin 协程时代，但理解底层原理、掌握 Java 并发工具类，对于写出高效正确的并发代码至关重要。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         并发 vs 并行                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  并发（Concurrent）：
  ─────────────────────────────────────────────────────────────────────────
  多个任务在同一时间段内交替执行
  CPU 快速切换，给用户"同时运行"的感觉
  关键词：交替执行、CPU 调度、时间片

  并行（Parallel）：
  ─────────────────────────────────────────────────────────────────────────
  多个任务在同一时刻真正同时执行
  需要多核 CPU 才能实现
  关键词：同时执行、多核、物理并行

  ┌─────────────────────────────────────────────────────────────────────┐
  │  单核 CPU：只能并发，不能并行                                       │
  │  多核 CPU：可以并发 + 并行                                          │
  └─────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │  时间轴：                                                          │
  │  单核：| A区 | B区 | A区 | C区 | B区 | A区 | ...                   │
  │        └────┘ └────┘ └────┘ └────┘ └────┘                        │
  │  多核：| A区 | A区 |    ← 核心1                                    │
  │        | B区 | C区 |    ← 核心2（真正同时！）                      │
  └─────────────────────────────────────────────────────────────────────┘
```

### 为什么需要多线程

1. **防止阻塞**：耗时操作（网络、IO）在独立线程执行，不阻塞主线程
2. **充分利用多核**：计算密集型任务可分配到多核并行执行
3. **提高吞吐量**：单核 CPU 通过交替执行 IO 密集型任务，提高资源利用率
4. **用户体验**：UI 线程专门处理渲染和交互，保证流畅

### Android 并发技术演进

```
2008  Android 1.0    Thread / Handler / Runnable
2009  Android 1.5    AsyncTask（2017 废弃）
2011  Android 3.0    Loader / IntentService
2014  Android 5.0    JobScheduler
2017  Android 8.0    后台执行限制
2019  Kotlin 1.3    Coroutines 稳定版
2020  Jetpack       WorkManager / Lifecycle + Coroutines
现在    Kotlin 协程 + Flow 主导一切
```

---

## 2. Java 线程基础

### 2.1 Thread 创建与启动

Java 中创建线程有 3 种方式：

```java
// 方式1：继承 Thread
class MyThread extends Thread {
    @Override
    public void run() {
        // 业务逻辑在子线程执行
        String result = doNetworkRequest();
        updateUI(result);
    }
}
new MyThread().start();  // 注意是 start()，不是 run()

// 方式2：实现 Runnable（推荐，解除单继承限制）
class MyRunnable implements Runnable {
    @Override
    public void run() {
        // 业务逻辑
    }
}
new Thread(new MyRunnable()).start();

// 方式3：Lambda 简化（实际开发中最常用）
new Thread(() -> {
    // 业务逻辑
}).start();

// 方式4：实现 Callable（有返回值，可抛异常）
class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        String result = doNetworkRequest();
        return result;  // 有返回值
    }
}
FutureTask<String> task = new FutureTask<>(new MyCallable());
new Thread(task).start();
String result = task.get();  // 阻塞等待返回值
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         start() vs run()                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  start()：
  - 创建新线程（分配系统资源）
  - 调用 run() 在新线程执行
  - 每个线程只能调用一次 start()

  run()：
  - 普通方法调用
  - 在当前线程执行
  - 可以多次调用
```

### 2.2 线程状态与生命周期

线程有 6 种状态，通过 `Thread.getState()` 可查看：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         线程状态转换图                                       │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │      NEW         │ ← new Thread()，未启动
                              │ (创建，未运行)    │
                              └────────┬────────┘
                                       │ start()
                                       ▼
                              ┌─────────────────┐
                              │    RUNNABLE      │ ← 运行中或等待 CPU 时间片
                              │  (就绪/运行中)   │
                              └────────┬────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           │                           │                           │
     ┌─────┴─────┐              ┌─────┴─────┐              ┌─────┴─────┐
     │  BLOCKED  │              │  WAITING  │              │TIMED_WAIT│
     │(等待锁)   │              │(无限期等待)│              │ (限时等待)│
     └─────┬─────┘              └─────┬─────┘              └─────┬─────┘
           │获得synchronized锁         │被唤醒/notify           │超时/notify
           └───────────────────────────┼───────────────────────────┘
                                       ▼
                              ┌─────────────────┐
                              │   TERMINATED    │ ← run() 执行完毕，线程结束
                              │   (已终止)       │
                              └─────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  状态详解：                                                             │
  │                                                                         │
  │  NEW         → 创建了 Thread 对象，但未调用 start()                      │
  │  RUNNABLE    → JVM 执行中，或等待 CPU 时间片                            │
  │  BLOCKED     → 等待获取 synchronized 监视器锁                           │
  │  WAITING     → 调用 Object.wait() / Thread.join() / LockSupport.park()  │
  │  TIMED_WAITING → 调用 Thread.sleep() / Object.wait(timeout) 等          │
  │  TERMINATED  → run() 正常返回或抛出未捕获异常，线程结束                 │
  └─────────────────────────────────────────────────────────────────────────┘
```

**状态转换示例：**

```java
public class ThreadStateDemo {
    public static void main(String[] args) throws Exception {
        Thread thread = new Thread(() -> {
            synchronized (ThreadStateDemo.class) {
                try {
                    Thread.sleep(2000);  // TIMED_WAITING
                    ThreadStateDemo.class.wait();  // WAITING
                } catch (InterruptedException e) { }
            }
        });

        System.out.println(thread.getState());  // NEW
        thread.start();
        System.out.println(thread.getState());  // RUNNABLE
        Thread.sleep(100);
        System.out.println(thread.getState());  // TIMED_WAITING（sleep）
        Thread.sleep(2100);
        System.out.println(thread.getState());  // WAITING（wait）
    }
}
```

### 2.3 线程优先级

Java 线程优先级 1-10，默认为 5。**优先级只是提示，不保证严格按优先级执行。**

```java
thread.setPriority(Thread.MAX_PRIORITY);   // 10，最高优先级
thread.setPriority(Thread.NORM_PRIORITY);  // 5， 默认优先级
thread.setPriority(Thread.MIN_PRIORITY);   // 1， 最低优先级

// 也可以直接设置数值
thread.setPriority(7);
```

#### Android 特有优先级

Android 用 nice 值控制线程优先级，范围 -20（最高）到 +19（最低）：

```java
// 设置线程优先级（nice 值）
Process.setThreadPriority(Process.THREAD_PRIORITY_DEFAULT);    // 0，主线程默认
Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);  // 10，后台线程
Process.setThreadPriority(Process.THREAD_PRIORITY_FOREGROUND); // -2，提高到前台
Process.setThreadPriority(Process.THREAD_PRIORITY_DISPLAY);    // -4，显示相关
Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_DISPLAY); // -8，紧急显示
Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO);      // -16，音频播放
Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_AUDIO); // -19，实时音频

// 获取当前线程优先级（nice 值）
int nice = Process.getThreadPriority(android.os.Process.myTid());

// 设置为后台线程
Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);
// 或用简写（当前线程）
android.os.Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);
```

nice 值映射到 Linux 优先级：Linux 优先级 = 120 + nice 值（所以 nice=-20 对应 Linux 优先级 100，nice=+19 对应 Linux 优先级 139）。

### 2.4 守护线程

JVM 中所有非守护线程结束时，守护线程被 JVM 自动强制终止。

```java
Thread daemon = new Thread(() -> {
    while (true) {
        // 守护任务，例如定期清理缓存
        cleanCache();
        try {
            Thread.sleep(60000);  // 1分钟
        } catch (InterruptedException e) { }
    }
});
daemon.setDaemon(true);  // 必须在 start() 前设置
daemon.start();

// 主线程（非守护）结束 → JVM 退出 → daemon 线程被强制终止
```

守护线程特点：
- setDaemon(true) 必须在 start() 之前调用
- 守护线程中 finally 代码块可能不执行
- 典型用途：垃圾回收（GC 线程）、日志刷新、缓存清理、监控上报

---

## 3. 线程同步机制

### 3.1 synchronized

synchronized 是 JVM 内置的管程（Monitor）实现，自动获取/释放锁，可重入。

```java
// 用法1：同步实例方法（锁对象是 this）
public synchronized void method() {
    // 原子操作，整个方法体被保护
}

// 等价于
public void method() {
    synchronized (this) {
        // 原子操作
    }
}

// 用法2：同步静态方法（锁对象是类对象 Class）
public static synchronized void staticMethod() {
    // 原子操作，锁对象是 MyClass.class
}

// 等价于
public static void staticMethod() {
    synchronized (MyClass.class) {
        // 原子操作
    }
}

// 用法3：同步代码块（锁对象是指定的任意对象）
public void method() {
    // 前面的代码不需要同步
    synchronized (lockObject) {  // 推荐用专门的对象，减少锁粒度
        // 原子操作，只保护这一小块
    }
    // 后面的代码不需要同步
}
```

#### synchronized 的三大特性

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         synchronized 三大特性                                │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 原子性（Atomicity）
  ─────────────────────────────────────────────────────────────────────────
  一组操作不可中断，要么全部执行，要么全部不执行
  synchronized 修饰的方法或代码块是原子的

  2. 可见性（Visibility）
  ─────────────────────────────────────────────────────────────────────────
  线程 A 获取锁进入 synchronized 代码块，
  退出时强制刷新共享变量到主内存；
  线程 B 进入同一 synchronized 代码块时，
  强制从主内存读取最新值。

  3. 有序性（Ordering）
  ─────────────────────────────────────────────────────────────────────────
  synchronized 块内的代码不会被指令重排序。
  保证了"进入时可见其他线程的修改，退出时可见自己的修改"。

  ┌─────────────────────────────────────────────────────────────────────┐
  │  可见性示例：                                                        │
  │                                                                      │
  │  class VisibilityDemo {                                              │
  │      boolean flag = false;                                          │
  │                                                                      │
  │      synchronized void writer() {                                    │
  │          flag = true;           // 退出时强制刷主存                  │
  │      }                                                               │
  │                                                                      │
  │      synchronized void reader() {                                    │
  │          while (!flag) {        // 进入时强制读主存                  │
  │              // wait                                                    │
  │          }                                                           │
  │          System.out.println("done");                                 │
  │      }                                                               │
  │  }                                                                   │
  └─────────────────────────────────────────────────────────────────────┘
```

#### 可重入性（Reentrant）

synchronized 是可重入锁，同一个线程可以反复进入：

```java
public class ReentrantDemo {
    public synchronized void methodA() {
        System.out.println("methodA");
        methodB();  // 可以进入，因为是同一个线程
    }

    public synchronized void methodB() {
        System.out.println("methodB");
        methodC();
    }

    public synchronized void methodC() {
        System.out.println("methodC");
    }

    public static void main(String[] args) {
        new ReentrantDemo().methodA();
        // 输出：methodA → methodB → methodC
    }
}
```

可重入实现：JVM 为每个锁维护一个计数器 + 持有线程 ID。同一线程进入，计数器 +1；退出，计数器 -1；计数器归零时锁释放。

#### 锁的升级（偏向锁 → 轻量级锁 → 重量级锁）

JVM 对 synchronized 做了优化，锁会逐步升级：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         锁升级过程（不可逆）                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  无竞争状态（单线程）：
  ─────────────────────────────────────────────────────────────────────────
  偏向锁：
  - 第一次获取锁时，CAS 设置偏向模式
  - 记录持有锁的线程 ID
  - 同一线程再次进入，只需检查线程 ID，几乎无开销
  - 对象头记录偏向线程 ID

  轻度竞争（多线程交替执行，轻量级自旋）：
  ─────────────────────────────────────────────────────────────────────────
  轻量级锁：
  - 偏向锁被访问，撤销偏向，膨胀为轻量级锁
  - 线程在栈帧中创建锁记录（Lock Record）
  - CAS 将对象头指向锁记录，成功则获得锁
  - 失败则自旋等待（空转重试）

  激烈竞争（大量线程同时抢锁）：
  ─────────────────────────────────────────────────────────────────────────
  重量级锁：
  - 自旋超过阈值（默认 10 次），膨胀为重量级锁
  - 未抢到锁的线程进入阻塞（park）
  - 需要 OS 调度，有用户态到内核态的切换
  - 开销最大，但不会空转浪费 CPU

  ┌─────────────────────────────────────────────────────────────────────┐
  │  性能对比：                                                          │
  │  偏向锁 < 轻量级锁 < 重量级锁（开销递增）                             │
  │  偏向锁：几乎无额外开销（单线程最优）                                  │
  │  轻量级锁：少量自旋开销                                              │
  │  重量级锁：线程阻塞 + 系统调用（最重）                                │
  └─────────────────────────────────────────────────────────────────────┘
```

### 3.2 volatile

volatile 是轻量级同步机制，不加锁，只保证**可见性**和**有序性**，**不保证原子性**。

#### volatile 适用场景

```java
// 场景1：状态标志位
public class VolatileFlag {
    private volatile boolean running = true;  // volatile 必须！

    public void stop() {
        running = false;  // 写入对所有线程立即可见
    }

    public void run() {
        while (running) {  // 读取总是看到最新值
            // 执行业务逻辑
        }
    }
}

// 场景2：DCL 单例模式
public class Singleton {
    private static volatile Singleton instance;  // 防止指令重排序！

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

#### volatile 的内存语义

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         volatile 内存语义                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  写操作（Store Barrier）：
  ─────────────────────────────────────────────────────────────────────────
  volatile 写操作会插入 Store Barrier，
  强制将工作内存中的值刷新到主内存。

  读操作（Load Barrier）：
  ─────────────────────────────────────────────────────────────────────────
  volatile 读操作会插入 Load Barrier，
  强制从主内存读取最新值到工作内存。

  工作内存（CPU Cache）←→ 主内存（RAM）

  ┌─────────────────────────────────────────────────────────────────────┐
  │  普通变量读写：                                                      │
  │  线程A: 写变量 → 工作内存 → (可能不同步) → 主内存                   │
  │  线程B: 读变量 ← 工作内存 ← (可能过期) ← 主内存                     │
  │                                                                      │
  │  volatile 变量读写：                                                  │
  │  线程A: 写变量 → 强制刷主内存                                        │
  │  线程B: 读变量 → 强制读主内存                                        │
  └─────────────────────────────────────────────────────────────────────┘
```

#### 防止指令重排序

volatile 通过插入内存屏障（Memory Barrier）防止指令重排序：

```java
// 示例：DCL 单例为什么要 volatile
instance = new Singleton();
// 上面这行可能被重排序为：
// 1. 分配内存
// 2. 调用构造方法初始化
// 3. 将引用指向内存

// 如果 2 和 3 重排序：
// 线程A: 执行了 1 → 3（instance != null，但未初始化）
// 线程B: 检查 instance != null，直接使用（使用到未初始化的对象！）
// 线程B 可能崩溃或读到未知数据

// volatile 禁止 2 和 3 重排序，所以必须加 volatile
```

#### synchronized vs volatile 详细对比

| 特性 | synchronized | volatile |
|------|-------------|----------|
| 原子性 | 保证 | 不保证 |
| 可见性 | 保证 | 保证 |
| 有序性 | 保证（块内） | 保证（单个变量） |
| 锁机制 | 隐式管程锁 | 无锁 |
| 阻塞线程 | 会（重量级锁时） | 不会 |
| 性能开销 | 较重 | 极轻 |
| 可重入 | 是 | 不适用 |
| 典型用法 | 复合操作代码块 | 状态标志位、单例 |

#### 什么情况下 i++ 需要 synchronized

```java
// 演示 volatile 不保证原子性
public class AtomicDemo {
    private volatile int count = 0;

    public void increment() {
        count++;  // 不安全！++ 操作分三步：读取、+1、写入
    }

    public int get() {
        return count;
    }
}

// 问题演示：
// 线程A: 读取 count=0
// 线程A: count+1 = 1
// 线程B: 读取 count=0（线程A还没写入！）
// 线程A: 写入 count=1
// 线程B: count+1 = 1
// 线程B: 写入 count=1
// 结果：count=1，但实际应该=2！

// 解决方案1：synchronized
private int count = 0;
public synchronized void increment() {
    count++;
}

// 解决方案2：AtomicInteger（推荐）
private final AtomicInteger count = new AtomicInteger(0);
public void increment() {
    count.incrementAndGet();
}
```

### 3.3 wait/notify/notifyAll

Object 的等待通知机制，**必须在 synchronized 内使用**。线程间通信的基础方式。

```java
synchronized (lock) {
    while (condition不满足) {
        lock.wait();  // 释放锁，进入 WAITING 状态
    }
    // 业务逻辑（此时已持有锁）
    lock.notify();      // 通知一个等待线程（随机）
    // 或 lock.notifyAll();  // 通知所有等待线程
}
// 退出 synchronized 时释放锁
```

#### wait/notifyAll 经典模式：生产者-消费者

```java
public class ProducerConsumer {
    private final Object lock = new Object();
    private String data;
    private boolean hasData = false;

    // 消费者
    public void consume() throws InterruptedException {
        synchronized (lock) {
            while (!hasData) {
                lock.wait();  // 等待数据，释放锁
            }
            // 有数据了，消费它
            System.out.println("Consumed: " + data);
            hasData = false;
            lock.notifyAll();  // 通知所有等待中的生产者
        }
    }

    // 生产者
    public void produce(String newData) throws InterruptedException {
        synchronized (lock) {
            while (hasData) {
                lock.wait();  // 数据还没被消费，等待
            }
            data = newData;
            hasData = true;
            lock.notifyAll();  // 通知所有等待中的消费者
        }
    }
}
```

#### 为什么必须用 while 不用 if

```java
// 错误示例（用 if）：
synchronized (lock) {
    if (!condition) {
        lock.wait();  // 虚假唤醒！被唤醒时条件可能仍不满足
    }
    // 继续执行（可能出问题）
}

// 正确示例（用 while）：
synchronized (lock) {
    while (!condition) {
        lock.wait();  // 醒来后重新检查条件
    }
    // 此时条件一定满足
}

// 虚假唤醒（Spurious Wakeup）：
// JVM 实现中，wait() 有可能无故返回，
// 所以必须用 while 循环包裹，防止虚假唤醒后继续执行
```

#### notify vs notifyAll

| 方法 | 行为 | 风险 |
|------|------|------|
| notify() | 随机唤醒一个等待线程 | 可能导致只有某些线程被唤醒，其他线程永久等待（饥饿） |
| notifyAll() | 唤醒所有等待线程 | 所有线程被唤醒后竞争锁，开销稍大，但更安全 |

推荐用 notifyAll()，除非明确知道只有一个线程在等待。

### 3.4 Lock 与 ReentrantLock

ReentrantLock 是 JUC 提供的显式锁，比 synchronized 更灵活。

```java
private final ReentrantLock lock = new ReentrantLock();

public void method() {
    lock.lock();  // 获取锁
    try {
        // 业务逻辑
    } finally {
        lock.unlock();  // 必须在 finally 释放！
    }
}

// tryLock()：非阻塞尝试获取
public void tryLockDemo() {
    if (lock.tryLock()) {  // 获取成功返回 true
        try {
            // 业务逻辑
        } finally {
            lock.unlock();
        }
    } else {
        // 获取失败，走其他逻辑
    }
}

// tryLock(timeout)：带超时
public void tryLockWithTimeout() throws InterruptedException {
    if (lock.tryLock(5, TimeUnit.SECONDS)) {
        try {
            // 业务逻辑
        } finally {
            lock.unlock();
        }
    } else {
        // 等待超时，走其他逻辑
    }
}

// lockInterruptibly()：可中断获取
public void lockInterruptiblyDemo() throws InterruptedException {
    lock.lockInterruptibly();  // 可被中断
    try {
        // 业务逻辑
    } finally {
        lock.unlock();
    }
}

// 公平锁：按等待顺序获取锁
ReentrantLock fairLock = new ReentrantLock(true);  // 公平锁

// 查询状态
public void queryState() {
    System.out.println("是否锁定: " + lock.isLocked());
    System.out.println("是否当前线程持有: " + lock.isHeldByCurrentThread());
    System.out.println("等待线程数: " + lock.getQueueLength());
}
```

#### synchronized vs ReentrantLock 全面对比

| 特性 | synchronized | ReentrantLock |
|------|-------------|--------------|
| 响应中断 | ✗ | ✓ |
| 尝试获取 | ✗ | ✓ |
| 超时获取 | ✗ | ✓ |
| 公平锁 | ✗（非公平） | ✓ |
| 多条件变量 | ✗（一个等待队列） | ✓（多个 Condition） |
| 锁释放 | 自动（出 synchronized 块） | 必须手动 |
| 性能 | JVM 优化后相近 | 稍灵活 |
| 异常处理 | 自动释放 | 必须 finally |

### 3.5 ReadWriteLock

读写分离锁，读操作可以并发，写操作独占。

```java
private final ReadWriteLock rwLock = new ReentrantReadWriteLock();

// 读操作（多线程可并发）
public V get(K key) {
    rwLock.readLock().lock();
    try {
        return cache.get(key);
    } finally {
        rwLock.readLock().unlock();
    }
}

// 写操作（独占）
public void put(K key, V value) {
    rwLock.writeLock().lock();
    try {
        cache.put(key, value);
    } finally {
        rwLock.writeLock().unlock();
    }
}
```

#### 读写锁的规则

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         读写锁访问规则                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  读-读：可以并发（多个线程同时读）
  读-写：互斥（读的时候不能写，写的时候不能读）
  写-写：互斥（同一时刻只能一个线程写）

  注意：ReentrantReadWriteLock 允许从写锁降级为读锁：
  rwLock.writeLock().lock();
  try {
      // 写操作
      rwLock.readLock().lock();  // 同一个线程可以再次获取读锁
      try {
          // 读操作（降级后可以读）
      } finally {
          rwLock.readLock().unlock();  // 先释放读锁
      }
  } finally {
      rwLock.writeLock().unlock();  // 最后释放写锁
  }
```

### 3.6 Condition

Condition（条件变量）是比 wait/notify 更强大的等待机制，**必须和 ReentrantLock 配合使用**。

```java
private final ReentrantLock lock = new ReentrantLock();
private final Condition notEmpty = lock.newCondition();  // 队列非空条件
private final Condition notFull = lock.newCondition();   // 队列非满条件

public void put(T item) throws InterruptedException {
    lock.lock();
    try {
        while (count == items.length) {
            notFull.await();  // 队列满，等待
        }
        items[putIndex] = item;
        if (++putIndex == items.length) putIndex = 0;
        count++;
        notEmpty.signal();  // 通知队列非空
    } finally {
        lock.unlock();
    }
}

public T take() throws InterruptedException {
    lock.lock();
    try {
        while (count == 0) {
            notEmpty.await();  // 队列空，等待
        }
        @SuppressWarnings("unchecked")
        T item = (T) items[takeIndex];
        items[takeIndex] = null;
        if (++takeIndex == items.length) takeIndex = 0;
        count--;
        notFull.signal();  // 通知队列非满
        return item;
    } finally {
        lock.unlock();
    }
}
```

#### Object.wait/notify vs Condition

| 特性 | Object.wait/notify | Condition |
|------|-------------------|----------|
| 锁 | synchronized | ReentrantLock |
| 条件队列数 | 1个（Object 的等待集） | 多个（可创建多个 Condition） |
| 虚假唤醒 | 可能（需用 while） | 可能（需用 while） |
| 中断响应 | 可中断 | 可中断 |
| 超时等待 | wait(timeout) | await(timeout) |
| 公平锁 | ✗ | ✓（可配合公平锁） |

### 3.7 StampedLock

StampedLock 是 JDK 8 引入的改进版读写锁，支持乐观读，性能更好。

```java
private final StampedLock sl = new StampedLock();
private double x, y;

// 悲观读（和 ReadWriteLock 类似）
public double distance() {
    long stamp = sl.readLock();
    try {
        return Math.sqrt(x * x + y * y);
    } finally {
        sl.unlockRead(stamp);
    }
}

// 乐观读（不阻塞，写入少时性能最好）
public double optimisticDistance() {
    long stamp = sl.tryOptimisticRead();  // 获取乐观读戳（不阻塞）

    // 读取数据（此时可能正在被写入，是快照）
    double currentX = x;
    double currentY = y;

    // 验证戳是否有效（中间是否有写操作）
    if (!sl.validate(stamp)) {
        // 戳无效，说明有写操作发生过，升级为悲观读
        stamp = sl.readLock();
        try {
            currentX = x;
            currentY = y;
        } finally {
            sl.unlockRead(stamp);
        }
    }
    return Math.sqrt(currentX * currentX + currentY * currentY);
}

// 写锁
public void move(double deltaX, double deltaY) {
    long stamp = sl.writeLock();
    try {
        x += deltaX;
        y += deltaY;
    } finally {
        sl.unlockWrite(stamp);
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    StampedLock 三种模式                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  writeLock()：独占写锁，和 ReadWriteLock 写锁类似
  readLock()：悲观读锁，和 ReadWriteLock 读锁类似
  tryOptimisticRead()：乐观读，不阻塞，直接返回戳

  乐观读流程：
  1. tryOptimisticRead() 获取戳（此时无锁）
  2. 读取数据（快照）
  3. validate(stamp) 检查戳是否有效
     - 有效（无写操作）→ 使用快照数据
     - 无效（有写操作）→ 升级为悲观读，重新读取

  适用场景：
  - 读多写少
  - 读操作远多于写操作
  - 写操作时间很短
```

---

## 4. Java 并发工具类

### 4.1 CountDownLatch

倒数计数器，让一个或多个线程等待，直到一组操作完成。

```java
// 场景：主线程等待多个子线程执行完毕
public class GameServer {
    public void startGame() throws InterruptedException {
        int playerCount = 5;
        CountDownLatch startSignal = new CountDownLatch(1);  // 主控信号
        CountDownLatch doneSignal = new CountDownLatch(playerCount);  // 完成信号

        // 创建玩家线程
        for (int i = 0; i < playerCount; i++) {
            new Thread(() -> {
                try {
                    System.out.println("Player " + Thread.currentThread().getId() + " ready");
                    startSignal.await();  // 等待开始信号

                    // 执行游戏逻辑
                    Thread.sleep((long) (Math.random() * 1000));
                    System.out.println("Player " + Thread.currentThread().getId() + " finished");

                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    doneSignal.countDown();  // 完成，计数减一
                }
            }).start();
        }

        Thread.sleep(500);  // 等待所有玩家准备
        System.out.println("Game starting!");
        startSignal.countDown();  // 主线程发出开始信号

        doneSignal.await();  // 等待所有玩家完成
        System.out.println("All players finished, game over!");
    }
}
```

#### CountDownLatch 核心方法

| 方法 | 说明 |
|------|------|
| `CountDownLatch(int count)` | 构造函数，计数初始值 |
| `await()` | 等待计数归零，阻塞 |
| `await(timeout, unit)` | 等待超时，返回是否成功 |
| `countDown()` | 计数减一，不能重置 |
| `getCount()` | 获取当前计数值 |

**注意**：CountDownLatch 不能重置，计数到 0 后不能再用。

### 4.2 CyclicBarrier

循环栅栏，让一组线程互相等待，到达某点后一起恢复执行。**可以重置后重用**。

```java
// 场景：多线程执行，分阶段同步
public class MatrixSolver {
    public void solve() {
        int n = 4;
        CyclicBarrier barrier = new CyclicBarrier(n, () -> {
            System.out.println("阶段完成，进入下一阶段...");
        });

        for (int i = 0; i < n; i++) {
            final int row = i;
            new Thread(() -> {
                try {
                    // 阶段1：行归一化
                    System.out.println("Thread-" + row + " 阶段1");
                    barrier.await();

                    // 阶段2：列归一化
                    System.out.println("Thread-" + row + " 阶段2");
                    barrier.await();

                    // 阶段3：对角化
                    System.out.println("Thread-" + row + " 阶段3");
                    barrier.await();

                } catch (InterruptedException | BrokenBarrierException e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }
    }
}
```

#### CountDownLatch vs CyclicBarrier

| 特性 | CountDownLatch | CyclicBarrier |
|------|--------------|--------------|
| 用途 | 一组线程等待某个事件 | 一组线程互相等待 |
| 计数方向 | 倒减（countDown） | 正加（await） |
| 重置 | 不能重置 | 可重置（Cyclic） |
| 完成后状态 | 不可逆 | 可重复使用 |
| 典型场景 | "等N个线程完成后..." | "N个线程都到达后..." |

### 4.3 Semaphore

信号量，控制同时访问某资源的线程数量。

```java
// 场景：连接池，限制同时使用连接的线程数
class ConnectionPool {
    private final Semaphore available;
    private final Object[] connections;

    public ConnectionPool(int poolSize) {
        available = new Semaphore(poolSize);
        connections = new Object[poolSize];
        for (int i = 0; i < poolSize; i++) {
            connections[i] = new Object();
        }
    }

    public Object getConnection(long timeout, TimeUnit unit)
            throws InterruptedException {
        if (!available.tryAcquire(timeout, unit)) {
            throw new InterruptedException("Timeout waiting for connection");
        }
        return acquireConnection();
    }

    private Object acquireConnection() {
        synchronized (connections) {
            for (int i = 0; i < connections.length; i++) {
                if (connections[i] != null) {
                    Object conn = connections[i];
                    connections[i] = null;  // 标记为已借出
                    return conn;
                }
            }
            return null;
        }
    }

    public void releaseConnection(Object conn) {
        synchronized (connections) {
            for (int i = 0; i < connections.length; i++) {
                if (connections[i] == null) {
                    connections[i] = conn;  // 归还
                    break;
                }
            }
        }
        available.release();  // 信号量加一
    }
}
```

#### Semaphore 核心方法

| 方法 | 说明 |
|------|------|
| `Semaphore(int permits)` | 构造函数，设置许可数 |
| `acquire()` | 获取一个许可，阻塞 |
| `acquire(int permits)` | 获取多个许可，阻塞 |
| `tryAcquire()` | 尝试获取，非阻塞 |
| `tryAcquire(timeout, unit)` | 尝试获取，带超时 |
| `release()` | 释放一个许可 |
| `release(int permits)` | 释放多个许可 |
| `availablePermits()` | 查询可用许可数 |

### 4.4 Exchanger

两个线程交换数据。

```java
// 场景：生产者-消费者之间的数据缓冲区交换
class DataProcessor {
    private final Exchanger<DataBuffer> exchanger = new Exchanger<>();

    // 生产者线程
    public void producer() throws InterruptedException {
        DataBuffer emptyBuffer = new DataBuffer();
        DataBuffer fullBuffer = new DataBuffer(100);

        while (true) {
            // 用空缓冲区换取已填充的缓冲区
            fullBuffer = exchanger.exchange(fullBuffer);
            fullBuffer.fill();  // 填充数据
        }
    }

    // 消费者线程
    public void consumer() throws InterruptedException {
        DataBuffer emptyBuffer = new DataBuffer();
        DataBuffer fullBuffer = new DataBuffer();

        while (true) {
            // 用已填充的缓冲区换取空缓冲区
            fullBuffer = exchanger.exchange(fullBuffer);
            fullBuffer.process();  // 处理数据
            fullBuffer.clear();     // 清空，准备交换回去
        }
    }

    static class DataBuffer {
        int[] data;
        int size;
        DataBuffer() { data = new int[1024]; }
        DataBuffer(int size) { this.size = size; }
        void fill() { /* 填充数据 */ }
        void process() { /* 处理数据 */ }
        void clear() { size = 0; }
    }
}
```

### 4.5 Phaser

多阶段同步器，比 CyclicBarrier 更灵活，支持动态注册 participants。

```java
// 场景：多阶段任务，每阶段需全部完成后才能进入下一阶段
public class PhaserDemo {
    public void execute() throws InterruptedException {
        Phaser phaser = new Phaser(3);  // 3 个参与线程

        for (int i = 0; i < 3; i++) {
            final int threadId = i;
            new Thread(() -> {
                try {
                    // 阶段0：初始化
                    System.out.println("Thread-" + threadId + " 阶段0 初始化");
                    phaser.arriveAndAwaitAdvance();  // 到达，等待其他线程

                    // 阶段1：执行
                    System.out.println("Thread-" + threadId + " 阶段1 执行");
                    phaser.arriveAndAwaitAdvance();

                    // 阶段2：收尾
                    System.out.println("Thread-" + threadId + " 阶段2 收尾");
                    phaser.arriveAndAwaitAdvance();

                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }

        // 主线程等待所有阶段完成
        phaser.awaitAdvance(phaser.getPhase());
        System.out.println("所有阶段完成");
    }
}
```

#### Phaser 核心方法

| 方法 | 说明 |
|------|------|
| `Phaser(int parties)` | 构造函数，注册 parties 个参与线程 |
| `arriveAndAwaitAdvance()` | 到达并等待其他线程 |
| `arrive()` | 到达（不等待），返回当前 phase |
| `arriveAndDeregister()` | 到达并退出 Phaser |
| `bulkRegister(int parties)` | 批量注册 |
| `awaitAdvance(int phase)` | 等待 phase 前进 |

---

## 5. 原子类与 CAS

### 5.1 AtomicInteger/AtomicLong

无锁的原子整数操作，比 synchronized 更轻量，基于 CAS 实现。

```java
private final AtomicInteger count = new AtomicInteger(0);

// 基本操作
count.incrementAndGet();         // ++i，返回新值
count.getAndIncrement();         // i++，返回旧值
count.decrementAndGet();         // --i
count.getAndDecrement();         // i--

// 算术操作
count.addAndGet(delta);          // += delta
count.getAndAdd(delta);          // 返回旧值后 += delta

// CAS 操作
count.compareAndSet(expected, newValue);  // 如果当前值==expected，则设置为newValue

// 原子更新（lambda）
count.updateAndGet(current -> current + delta);  // 返回新值
count.getAndUpdate(current -> current + delta);   // 返回旧值

// 获取并设置
count.getAndSet(newValue);       // 返回旧值，设置为新值

// 演示
public class AtomicCounter {
    private final AtomicInteger counter = new AtomicInteger(0);

    public void increment() {
        counter.incrementAndGet();
    }

    public int get() {
        return counter.get();
    }

    // CAS 演示：实现自旋锁
    public void casIncrement() {
        int expected;
        do {
            expected = counter.get();
        } while (!counter.compareAndSet(expected, expected + 1));
    }
}
```

### 5.2 AtomicReference

无锁实现对象的原子更新，用于替代需要加锁的对象引用操作。

```java
// 无锁栈实现
class AtomicStack<T> {
    private final AtomicReference<Node<T>> top = new AtomicReference<>();

    public void push(T item) {
        Node<T> newHead = new Node<>(item);
        Node<T> oldHead;
        do {
            oldHead = top.get();
            newHead.next = oldHead;
        } while (!top.compareAndSet(oldHead, newHead));
    }

    public T pop() {
        Node<T> oldHead;
        Node<T> newHead;
        do {
            oldHead = top.get();
            if (oldHead == null) return null;
            newHead = oldHead.next;
        } while (!top.compareAndSet(oldHead, newHead));
        return oldHead.item;
    }

    private static class Node<T> {
        final T item;
        Node<T> next;
        Node(T item) { this.item = item; }
    }
}

// 无锁单例
class Singleton {
    private static final AtomicReference<Singleton> instance =
        new AtomicReference<>();

    private Singleton() { }

    public static Singleton getInstance() {
        while (true) {
            Singleton current = instance.get();
            if (current != null) return current;

            Singleton newInstance = new Singleton();
            if (instance.compareAndSet(null, newInstance)) {
                return newInstance;
            }
            // CAS 失败，说明其他线程已经创建，循环重试
        }
    }
}
```

### 5.3 AtomicIntegerFieldUpdater

对普通字段的原子更新，节省内存（不用每个对象创建一个 AtomicInteger）。

```java
class Student {
    volatile int score;  // 必须是 volatile，不能是 private
}

class ScoreTracker {
    // 注意：字段必须是 volatile，不能是 private
    private final AtomicIntegerFieldUpdater<Student> scoreUpdater =
        AtomicIntegerFieldUpdater.newUpdater(Student.class, "score");

    public void incrementScore(Student student) {
        scoreUpdater.incrementAndGet(student);
    }

    public void addScore(Student student, int delta) {
        scoreUpdater.addAndGet(student, delta);
    }

    public int getScore(Student student) {
        return scoreUpdater.get(student);
    }
}

// 使用示例
public class UpdaterDemo {
    public static void main(String[] args) {
        Student[] students = new Student[100];
        for (int i = 0; i < 100; i++) {
            students[i] = new Student();
        }

        ScoreTracker tracker = new ScoreTracker();
        for (Student s : students) {
            tracker.incrementScore(s);
        }

        // 节省了大量 AtomicInteger 对象！
    }
}
```

### 5.4 LongAdder（高并发场景）

高并发计数器，比 AtomicLong 性能更好。热点数据分段，多线程更新不同单元，最后汇总。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AtomicLong vs LongAdder 原理对比                          │
└─────────────────────────────────────────────────────────────────────────────┘

  AtomicLong：
  ─────────────────────────────────────────────────────────────────────────
  多个线程竞争同一个变量
  CAS 失败 → 自旋重试 → 激烈竞争时性能急剧下降

  LongAdder：
  ─────────────────────────────────────────────────────────────────────────
  分段思想：热点数据分成多个单元
  每个线程更新自己的单元（无竞争）
  sum() 时汇总所有单元

  ┌─────────────────────────────────────────────────────────────────────┐
  │  LongAdder 内部结构：                                                 │
  │                                                                     │
  │  base：一个基础值（普通 volatile long）                              │
  │  cells：分段数组（懒加载，初始为 null）                              │
  │                                                                     │
  │  更新逻辑：                                                          │
  │  1. 先 CAS 更新 base（无竞争时）                                     │
  │  2. 有竞争 → 懒创建 cells 数组                                       │
  │  3. 取 cell 索引 = threadId % cells.length                          │
  │  4. CAS 更新对应的 cell（无竞争）                                     │
  │  5. 再次失败 → 自旋重试                                              │
  │                                                                     │
  │  sum() 汇总：base + sum(cells[])                                    │
  └─────────────────────────────────────────────────────────────────────┘
```

```java
// 场景：高并发计数（如 Analytics）
class Analytics {
    private final LongAdder totalClicks = new LongAdder();
    private final LongAdder totalViews = new LongAdder();

    public void recordClick() {
        totalClicks.increment();  // 比 AtomicLong 快很多（无竞争时用 base）
    }

    public void recordView() {
        totalViews.increment();
    }

    public long getTotalClicks() {
        return totalClicks.sum();
    }

    public long getTotalViews() {
        return totalViews.sum();
    }
}

// LongAccumulator：更通用的累加器
class ScoreAccumulator {
    private final LongAccumulator maxScore = new LongAccumulator(
        Long::max,  // 累加规则（可以是任意二元运算）
        0           // 初始值
    );

    public void recordScore(long score) {
        maxScore.accumulate(score);  // 记录最大值
    }

    public long getMaxScore() {
        return maxScore.get();
    }
}
```

### 5.5 CAS 原理

CAS（Compare-And-Swap）是硬件级别的原子操作，CPU 提供支持。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAS 原理                                            │
└─────────────────────────────────────────────────────────────────────────────┘

  三个操作数：
  - V（Memory）：内存位置
  - A（Expected）：预期原值
  - B（New）：新值

  操作语义：
  如果 V == A，将 V 设为 B，返回 true
  否则什么都不做，返回 false

  CPU 指令：
  - x86: CMPXCHG（单核）
  - x86: LOCK CMPXCHG（多核，锁总线）
  - ARM: LDREX/STREX（加载exclusive/存储exclusive）

  Java 实现（Unsafe 类）：
  public final int getAndAddInt(Object o, long offset, int delta) {
      int expected;
      do {
          expected = getIntVolatile(o, offset);  // 读取当前值
      } while (!compareAndSwapInt(o, offset, expected, expected + delta));
      // CAS 失败则循环重试
      return expected;
  }

  ┌─────────────────────────────────────────────────────────────────────┐
  │  CAS 的问题：                                                        │
  │                                                                     │
  │  1. ABA 问题：                                                       │
  │     线程A: 读取 V=A                                                 │
  │     线程B: 把 A 改成 B，又把 B 改成 A                               │
  │     线程A: CAS(V, A, B) 成功！                                      │
  │     但实际上值已被修改过！                                           │
  │                                                                     │
  │  2. 自旋开销：                                                       │
  │     竞争激烈时，CAS 失败率高，循环重试浪费 CPU                      │
  │                                                                     │
  │  3. 只能保证单个变量原子性：                                        │
  │     多个变量需要 synchronized               │
  └─────────────────────────────────────────────────────────────────────┘
```

#### ABA 问题及解决方案

```java
// ABA 问题示例
AtomicInteger ref = new AtomicInteger(100);
Thread t1 = new Thread(() -> {
    ref.compareAndSet(100, 200);  // 成功
    ref.compareAndSet(200, 100);  // 成功
});
Thread t2 = new Thread(() -> {
    boolean success = ref.compareAndSet(100, 300);  // true！
    // t2 以为值没变，实际已被 t1 修改过
});

// 解决方案：AtomicStampedReference（带版本号）
AtomicStampedReference<Integer> stampedRef =
    new AtomicStampedReference<>(100, 1);

Thread t1 = new Thread(() -> {
    int[] stamp = new int[1];
    Integer value = stampedRef.get(stamp);  // 获取值和版本
    stampedRef.compareAndSet(100, 200, stamp[0], stamp[0] + 1);  // 同时比较版本
    stampedRef.compareAndSet(200, 100, stamp[0] + 1, stamp[0] + 2);
});

Thread t2 = new Thread(() -> {
    int[] stamp = new int[1];
    Integer value = stampedRef.get(stamp);  // 获取值和版本
    // stamp[0] 已变化，CAS 失败！
    stampedRef.compareAndSet(100, 300, stamp[0], stamp[0] + 1);
});
```

---

## 6. 并发集合

### 6.1 ConcurrentHashMap

高性能并发哈希映射，JDK 8+ 用 CAS + synchronized 实现。

```java
ConcurrentHashMap<String, Object> map = new ConcurrentHashMap<>();

// 基本操作（线程安全）
map.put("key", "value");
map.get("key");
map.remove("key");
map.containsKey("key");
map.size();

// 原子操作
map.putIfAbsent("key", "newValue");  // 不存在才插入，返回旧值
map.remove("key", "expectedValue");  // 值匹配才删除，返回是否删除
map.replace("key", "oldValue", "newValue");  // 值匹配才替换，返回是否替换
map.replace("key", "newValue");  // 直接替换，返回旧值

// compute 原子更新
map.compute("counter", (k, v) -> v == null ? "1" : String.valueOf(Integer.parseInt(v) + 1));
map.computeIfAbsent("key", k -> createExpensiveObject(k));  // 不存在才计算
map.computeIfPresent("key", (k, v) -> v + "x");  // 存在才计算

// merge 合并
map.merge("key", "value", (oldVal, newVal) -> oldVal + newVal);

// 批量操作
map.forEach((k, v) -> System.out.println(k + ":" + v));
map.forEach(3, (k, v) -> System.out.println(k + ":" + v));  // 并行度3

// search 搜索
String result = map.search(3, (k, v) -> k.startsWith("a") ? k : null);
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ConcurrentHashMap JDK 8+ 实现原理                        │
└─────────────────────────────────────────────────────────────────────────────┘

  结构：数组 + 链表 + 红黑树
  ─────────────────────────────────────────────────────────────────────────
  - 数组（Node[] table）：每个元素是一个桶
  - 链表：桶内元素少时（<8）用链表
  - 红黑树：桶内元素多时（>8）链表转红黑树

  线程安全机制：
  ─────────────────────────────────────────────────────────────────────────
  读操作：
  - volatile 读，保证可见性
  - 无锁，极快

  写操作：
  - CAS + synchronized
  - 锁粒度细化到单个桶（头节点）
  - 减少锁竞争

  扩容：
  - 支持并发扩容
  - 多个线程一起搬数据
  - 减少扩容阻塞
```

### 6.2 CopyOnWriteArrayList

写时复制列表。读操作完全无锁，写操作复制全量数组。

```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();

// 读操作（无锁，极快）
list.get(index);         // 无锁，返回快照
list.contains(item);     // 无锁
list.isEmpty();
list.size();             // 返回估算值（写入可能进行中）
list.iterator();         // 返回快照迭代器

// 遍历（安全，写操作不影响读者）
for (String item : list) {
    // 遍历的是快照
}

// 写操作（复制全量数组）
list.add(item);          // 复制整个数组
list.add(index, item);   // 指定位置插入
list.remove(item);       // 复制整个数组
list.set(index, item);   // 复制整个数组

// 批量写
list.addIfAbsent(item);  // 不存在才添加
list.removeAll(otherList);
list.retainAll(otherList);
```

### 6.3 BlockingQueue

阻塞队列，生产者-消费者模式核心实现。

```java
// 场景：线程安全的有界队列
BlockingQueue<String> queue = new LinkedBlockingQueue<>(100);  // 有界
BlockingQueue<String> unbounded = new LinkedBlockingQueue<>();  // 无界（自动扩容）
BlockingQueue<String> arrayQueue = new ArrayBlockingQueue<>(100);  // 数组实现

// 阻塞方法
void put(E e)    // 队列满则阻塞
E take()         // 队列空则阻塞

// 非阻塞方法
boolean offer(E e)          // 队列满返回 false
boolean offer(E e, timeout) // 超时返回 false
E poll()                   // 队列空返回 null
E poll(timeout)            // 超时返回 null

// 抛异常方法
void add(E e)      // 队列满抛 IllegalStateException
boolean remove(Object o)  // 不存在返回 false
E element()         // 队列空抛 NoSuchElementException
```

```java
// 生产者-消费者完整示例
class ProducerConsumerDemo {
    private final BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);

    public void start() {
        // 启动生产者
        for (int i = 0; i < 4; i++) {
            final int id = i;
            new Thread(() -> {
                try {
                    while (true) {
                        Task task = produce(id);
                        queue.put(task);  // 满则阻塞
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Producer-" + id).start();
        }

        // 启动消费者
        for (int i = 0; i < 2; i++) {
            new Thread(() -> {
                try {
                    while (true) {
                        Task task = queue.take();  // 空则阻塞
                        consume(task);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Consumer-" + i).start();
        }
    }

    private Task produce(int id) { return new Task(); }
    private void consume(Task task) { }

    static class Task { }
}
```

### 6.4 ConcurrentLinkedQueue/Deque

无界非阻塞队列，FIFO，适合高并发场景。

```java
ConcurrentLinkedQueue<Task> queue = new ConcurrentLinkedQueue<>();

queue.offer(task);        // 入队
Task t = queue.poll();   // 出队，空则返回 null
Task peek = queue.peek(); // 窥视，空则返回 null

// 双端队列
ConcurrentLinkedDeque<Task> deque = new ConcurrentLinkedDeque<>();
deque.addFirst(task);    // 头插
deque.addLast(task);     // 尾插
deque.pollFirst();       // 头出
deque.pollLast();        // 尾出
```

### 6.5 ThreadLocalMap

ThreadLocal 的内部实现，使用弱引用 key 防止内存泄漏。

```java
// 基本使用
ThreadLocal<String> tl = ThreadLocal.withInitial(() -> "default");
tl.set("value");
String v = tl.get();      // 获取当前线程的值
tl.remove();              // 清理

// Android 中的应用：Looper 保存
// Looper.myLooper() → sThreadLocal.get() → 获取当前线程的 Looper

// 内存泄漏场景演示
class LeakDemo {
    private final ThreadLocal<byte[]> largeData = ThreadLocal.withInitial(
        () -> new byte[1024 * 1024 * 10]  // 10MB
    );

    public void wrongUsage(ExecutorService executor) {
        // 问题：线程池复用线程，ThreadLocal 不会被清理
        executor.submit(() -> {
            largeData.set(new byte[1024 * 1024 * 10]);
            // 任务结束，线程归还，但 ThreadLocal.value 仍在！
            // 如果不手动 remove()，10MB 内存泄漏
        });
    }

    public void correctUsage(ExecutorService executor) {
        executor.submit(() -> {
            try {
                largeData.set(new byte[1024 * 1024 * 10]);
                // 业务逻辑
            } finally {
                largeData.remove();  // 清理！
            }
        });
    }
}
```

---

## 7. 线程池

### 7.1 ThreadPoolExecutor 核心参数

```java
public ThreadPoolExecutor(
    int corePoolSize,           // 核心线程数
    int maximumPoolSize,         // 最大线程数
    long keepAliveTime,          // 非核心线程空闲存活时间
    TimeUnit unit,               // 时间单位
    BlockingQueue<Runnable> workQueue,   // 任务队列
    ThreadFactory threadFactory,          // 线程工厂
    RejectedExecutionHandler handler      // 拒绝策略
)
```

参数详解：

| 参数 | 说明 | 注意点 |
|------|------|--------|
| corePoolSize | 核心线程数，即使空闲也不回收 | allowCoreThreadTimeOut=true 时可被回收 |
| maximumPoolSize | 最大线程数 | corePoolSize ≤ maximumPoolSize |
| keepAliveTime | 非核心线程空闲存活时间 | 超过这个时间会被回收 |
| workQueue | 任务队列 | 有界队列可防止 OOM |
| threadFactory | 创建线程的工厂 | 可设置线程名、优先级、是否为守护线程 |
| handler | 拒绝策略 | 队列满 + 线程满时触发 |

### 7.2 线程池执行流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ThreadPoolExecutor 执行流程                               │
└─────────────────────────────────────────────────────────────────────────────┘

  execute(Runnable command)

  ① 检查线程数 < corePoolSize？
     是 ──► 创建核心线程，执行任务
     否 ──► ②

  ② 队列未满？
     是 ──► 任务入队列等待（核心线程空闲时取执行）
     否 ──► ③

  ③ 线程数 < maximumPoolSize？
     是 ──► 创建非核心线程，执行任务
     否 ──► ④

  ④ 执行拒绝策略

  ┌─────────────────────────────────────────────────────────────────────┐
  │  示例：                                                              │
  │  corePoolSize = 4, maxPoolSize = 8, queue = LinkedBlockingQueue(100)  │
  │                                                                      │
  │  任务1-4   → 4个核心线程执行                                         │
  │  任务5-104 → 队列（100个）                                          │
  │  任务105-108 → 4个非核心线程执行                                    │
  │  任务109+  → 拒绝策略                                               │
  └─────────────────────────────────────────────────────────────────────┘
```

### 7.3 线程池分类

```java
// 1. 固定大小线程池（队列无界）
ExecutorService fixedPool = Executors.newFixedThreadPool(4);
// corePoolSize = maxPoolSize = n
// 无界队列，风险：任务过多时内存暴涨

// 2. 缓存线程池（按需创建）
ExecutorService cachedPool = Executors.newCachedThreadPool();
// corePoolSize = 0
// maxPoolSize = Integer.MAX_VALUE
// 60秒回收
// 适合短时任务，但线程可能爆炸

// 3. 单线程池
ExecutorService singlePool = Executors.newSingleThreadExecutor();
// 保证任务顺序执行
// 内部用 LinkedBlockingQueue

// 4. 定时任务线程池
ScheduledExecutorService scheduledPool = Executors.newScheduledThreadPool(4);
scheduledPool.schedule(task, 3, TimeUnit.SECONDS);  // 延迟执行
scheduledPool.scheduleAtFixedRate(task, 1, 5, TimeUnit.SECONDS);  // 固定周期
scheduledPool.scheduleWithFixedDelay(task, 1, 5, TimeUnit.SECONDS);  // 固定间隔

// 5. 工作窃取线程池（ForkJoinPool）
ExecutorService workStealingPool = Executors.newWorkStealingPool(4);
// ForkJoinPool 实现
// 空闲线程从其他线程队列偷任务
// 适合大量小任务的并行计算

// 6. 自定义线程池（推荐）
ThreadPoolExecutor customPool = new ThreadPoolExecutor(
    4,                                      // corePoolSize
    8,                                      // maxPoolSize
    60L,                                    // keepAliveTime
    TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(200),          // 有界队列
    new ThreadFactory() {                    // 自定义线程工厂
        private int count = 0;
        @Override
        public Thread newThread(Runnable r) {
            Thread t = new Thread(r);
            t.setName("Worker-" + count++);
            t.setPriority(Thread.NORM_PRIORITY);
            return t;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy()  // 拒绝策略：调用者执行
);
```

### 7.4 线程池饱和策略

队列满 + 线程数达最大值时触发：

```java
// 四种饱和策略
// 1. AbortPolicy（默认）：抛异常
new ThreadPoolExecutor.AbortPolicy()
// 抛出 RejectedExecutionException

// 2. CallerRunsPolicy：用调用者线程执行
new ThreadPoolExecutor.CallerRunsPolicy()
// 任务由提交任务的线程执行
// 优点：防止任务丢失，且有减速效果（调用者线程被占用）
// 缺点：提交任务的线程被阻塞

// 3. DiscardPolicy：丢弃任务
new ThreadPoolExecutor.DiscardPolicy()
// 静默丢弃，不抛异常

// 4. DiscardOldestPolicy：丢弃最老的任务
new ThreadPoolExecutor.DiscardOldestPolicy()
// 丢弃队列中最老的任务，然后重试被拒绝的任务
// 注意：不是丢弃当前任务！
```

### 7.5 线程池参数配置

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    线程池参数配置公式                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  CPU 密集型任务（计算、排序、加密等）：
  ─────────────────────────────────────────────────────────────────────────
  线程数 = CPU 核心数 + 1

  IO 密集型任务（网络请求、文件读写、数据库等）：
  ─────────────────────────────────────────────────────────────────────────
  线程数 = CPU 核心数 × (1 + 等待时间 / 计算时间)

  混合型任务：
  ─────────────────────────────────────────────────────────────────────────
  线程数 = CPU 核心数 × CPU 利用率 × (1 + 等待时间 / 计算时间)

  获取 CPU 核心数：
  int cpuCores = Runtime.getRuntime().availableProcessors();

  实际配置建议：
  ─────────────────────────────────────────────────────────────────────────
  1. 不要写死核心线程数
  2. 使用有界队列，防止 OOM
  3. 拒绝策略用 CallerRunsPolicy，防止任务丢失
  4. 合理设置 keepAliveTime
  5. 监控队列大小和拒绝次数
  6. 线程池数量不宜过多（CPU 核心数 * 1.5 到 2 倍）

  ┌─────────────────────────────────────────────────────────────────────┐
  │  Android 主线程池（系统管理，不要自己创建）：                        │
  │  - IntentService：单线程 + Handler                                  │
  │  - AsyncTask：SERIAL_EXECUTOR（串行）/ THREAD_POOL_EXECUTOR（并行）│
  │  - Coroutines：Dispatchers.Main/IO/Default                        │
  └─────────────────────────────────────────────────────────────────────┘
```

---

## 8. Kotlin 协程原理

### 8.1 协程是什么

协程是用户态调度的轻量级线程。与线程的区别：

| 对比项 | 线程 | 协程 |
|--------|------|------|
| 调度者 | 操作系统 | 用户态（协程库） |
| 切换开销 | 大（1-2KB 栈，CPU 上下文切换） | 极小（状态机，寄存器保存） |
| 阻塞 | 阻塞线程 | 挂起协程，线程可执行其他任务 |
| 数量 | 受系统限制（千级） | 可轻松创建百万级 |
| 并发模型 | 抢占式 | 协作式（主动让出） |

```kotlin
// 线程模型：每个任务一个线程
fun threadModel() {
    thread { doWorkA() }  // 线程1
    thread { doWorkB() }  // 线程2
    // 两个线程同时运行
}

// 协程模型：单线程内交替执行
suspend fun coroutineModel() {
    launch { doWorkA() }   // 协程A
    launch { doWorkB() }   // 协程B
    // 在同一个线程内交替执行
}
```

### 8.2 协程调度器 Dispatchers

```kotlin
// Dispatchers.Main：主线程（Android UI线程）
launch(Dispatchers.Main) {
    textView.text = "更新UI"  // 安全更新UI
}

// Dispatchers.IO：IO操作线程池（异步）
launch(Dispatchers.IO) {
    val data = api.fetch()       // 网络请求
    val content = readFile()     // 文件读写
    val users = db.query()       // 数据库操作
    // 自动切换到主线程更新UI
    withContext(Dispatchers.Main) {
        textView.text = data
    }
}

// Dispatchers.Default：CPU密集型线程池
launch(Dispatchers.Default) {
    val sorted = bigList.sorted()  // 排序
    val result = processData(data)  // 计算
}

// Dispatchers.Unconfined：不限制线程（不推荐）
launch(Dispatchers.Unconfined) {
    // 启动时在主线程，恢复时在哪个线程就在哪个
}

// 自定义调度器（限制并发数）
val singleThread = Dispatchers.Default.limitedParallelism(1)
launch(singleThread) {
    // 所有协程在这个单线程执行，可保证线程安全
}
```

线程池大小：

- `Dispatchers.IO`：max(2, CPU 核心数 × 2)
- `Dispatchers.Default`：max(2, CPU 核心数)

### 8.3 协程上下文与作用域

```kotlin
// 上下文（CoroutineContext）
val ctx = Dispatchers.Default + CoroutineName("MyCoroutine") + CoroutineExceptionHandler { _, e ->
    println("Error: $e")
}

// 作用域（CoroutineScope）—— 管理协程生命周期
// 1. viewModelScope（ViewModel 推荐）
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {  // ViewModel 清除时自动取消
            val data = repository.getData()
        }
    }
}

// 2. lifecycleScope（Activity/Fragment 推荐）
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            val data = api.fetch()
        }
    }
}

// 3. 自定义作用域
val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
scope.launch { /* 需要手动 cancel */ }
scope.cancel()

// 结构化并发
viewModelScope.launch {
    val user = async { fetchUser() }    // 并发执行
    val posts = async { fetchPosts() }  // 并发执行
    display(user.await(), posts.await())  // 都完成后才进入
}
```

### 8.4 suspend 原理

suspend 函数被 Kotlin 编译器转换为状态机：

```kotlin
// 源代码
suspend fun fetchData(): String {
    val r1 = request1()     // 挂起点
    val r2 = request2(r1)  // 挂起点
    return process(r2)
}
```

编译后变成 Continuation 状态机：

```kotlin
// 编译后近似代码（状态机）
class FetchDataContinuation : Continuation<String> {
    var label = 0          // 状态：0=开始，1=request1后，2=request2后
    var result: String? = null
    var r1: String? = null
    var r2: String? = null

    override fun resumeWith(result: Result<String>) { /* 恢复执行 */ }

    fun doResume() {
        when (label) {
            0 -> {
                r1 = request1 { res ->  // 异步回调
                    r1 = res
                    label = 1
                    doResume()           // 恢复执行
                }
            }
            1 -> {
                r2 = request2(r1!!) { res ->
                    r2 = res
                    label = 2
                    doResume()
                }
            }
            2 -> {
                val finalResult = process(r2!!)
                continuation.resume(finalResult)  // 返回结果
            }
        }
    }
}
```

挂起原理：

```
挂起点 = 状态机的状态保存点
恢复 = 从保存的状态继续执行

suspend 函数不创建新线程
挂起时让出线程，让其他协程执行
恢复时可能回到原线程，也可能换线程（取决于调度器）
```

### 8.5 协程构建器

```kotlin
// launch：fire and forget，不返回结果
val job = viewModelScope.launch {
    val data = api.fetch()  // 不返回结果
}

// async：返回结果（Deferred）
val deferred = viewModelScope.async { api.fetch() }
val result = deferred.await()  // 等待结果

// awaitAll：并发等待多个
viewModelScope.launch {
    val (user, posts) = awaitAll(
        async { api.fetchUser() },
        async { api.fetchPosts() }
    )
}

// withContext：切换上下文并返回结果
viewModelScope.launch {
    val data = withContext(Dispatchers.IO) {
        api.fetch()  // 在 IO 线程执行
    }
    // 自动回到主线程
    textView.text = data
}

// withTimeout / withTimeoutOrNull：超时控制
viewModelScope.launch {
    try {
        withTimeout(3000L) {
            delay(4000L)  // 会超时
        }
    } catch (e: TimeoutCancellationException) {
        // 超时处理
    }

    val result = withTimeoutOrNull(3000L) {
        delay(2000L)
        "success"  // 不超时
    }  // result = null（超时）
}

// runBlocking（测试用，阻塞当前线程）
fun test() = runBlocking {
    val result = withContext(Dispatchers.IO) {
        "result"
    }
}

// channelFlow / flow：Flow Producer
fun channelFlowDemo(): Flow<Int> = channelFlow {
    for (i in 1..5) {
        send(i)
    }
}
```

### 8.6 协程取消

```kotlin
// 取消协程
val job = viewModelScope.launch {
    repeat(1000) { i ->
        delay(500L)  // 挂起点，会检查取消
    }
}
job.cancel()          // 取消
job.cancelAndJoin()   // 取消并等待完成

// 协程取消的检查点
viewModelScope.launch {
    try {
        repeat(10000) { i ->
            delay(1)  // delay() 是检查点，会响应取消
        }
    } catch (e: CancellationException) {
        // 协程被取消
    }
}

// CPU 密集型任务不会检查取消！
viewModelScope.launch {
    for (i in 0..1000000000) {
        compute(i)  // 没有挂起点，不会响应取消！
    }
    // 解决：定期 yield()
    for (i in 0..1000000000) {
        if (i % 1000 == 0) yield()  // 让出 CPU，让取消检查有机会执行
    }
}

// 取消传播
viewModelScope.launch {  // 父协程
    launch {  // 子协程1
        launch {
            delay(1000L)
        }
    }
    launch {  // 子协程2
        launch {
            delay(1000L)
        }
    }
    // 任一子协程失败 → 父协程失败 → 所有子协程取消
}

// SupervisorJob：子协程失败不影响父和兄弟
viewModelScope.launch(SupervisorJob()) {  // 父协程
    launch { throw Exception("Child 1 failed") }  // 失败
    launch { delay(1000L) }  // 仍然执行
}

// 清理资源
viewModelScope.launch {
    try {
        val resource = acquireResource()
        // 使用资源
    } finally {
        releaseResource()  // 取消时也会执行
    }
}
```

### 8.7 协程异常处理

```kotlin
// try-catch
viewModelScope.launch {
    try {
        val data = api.fetch()
    } catch (e: Exception) {
        handleError(e)
    }
}

// CoroutineExceptionHandler
val handler = CoroutineExceptionHandler { ctx, e ->
    println("Error in $ctx: $e")
}

// 全局作用域
GlobalScope.launch(handler) { throw Exception("error") }

// 自定义作用域
val scope = CoroutineScope(SupervisorJob() + handler)
scope.launch { throw Exception("error") }

// async 的异常在 await() 时抛出
viewModelScope.launch {
    val deferred = async {
        throw Exception("async error")
    }
    try {
        deferred.await()  // 异常在这里抛出
    } catch (e: Exception) {
        handleError(e)
    }
}

// 推荐：runCatching
val result = runCatching { api.fetch() }
result.onSuccess { data -> /* 处理成功 */ }
result.onFailure { e -> handleError(e) }

// 异常与结构化并发
viewModelScope.launch {
    // launch：子协程异常会直接传播给父协程
    // async：子协程异常在 await() 时才抛出
}

// 避免异常吞掉
viewModelScope.launch {
    supervisorScope {  // 用 supervisorScope 让子协程失败不影响父
        launch { throw Exception("error") }
        launch { /* 仍然执行 */ }
    }
}
```

### 8.8 Flow 异步数据流

Flow 是冷异步数据流，替代 RxJava。

```kotlin
// 创建 Flow
fun createFlow(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(100)
        emit(i)  // 发射值
    }
}.flowOn(Dispatchers.IO)

// 收集 Flow
viewModelScope.launch {
    createFlow().collect { value ->
        println("Received: $value")
    }
}

// Flow 操作符
viewModelScope.launch {
    flowOf(1, 2, 3, 4, 5)
        .map { it * 2 }                    // 转换
        .filter { it > 5 }                // 过滤
        .take(3)                          // 取前3个
        .onEach { println(it) }           // 副作用
        .catch { e -> emit(-1) }          // 异常处理
        .flowOn(Dispatchers.IO)           // 上游在 IO 线程
        .collect { /* 主线程接收 */ }
}

// StateFlow：状态流（类似 LiveData）
class StateFlowViewModel : ViewModel() {
    private val _state = MutableStateFlow(0)
    val state: StateFlow<Int> = _state.asReadOnlyStateFlow()

    fun update(value: Int) {
        _state.value = value
    }
}

// 在 Activity 中使用
lifecycleScope.launch {
    viewModel.state.collect { value ->
        textView.text = value.toString()
    }
}

// SharedFlow：共享流（事件总线）
class SharedFlowViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun sendEvent(event: Event) {
        viewModelScope.launch {
            _events.emit(event)  // 所有订阅者收到
        }
    }
}

// Channel：协程间通信（热流）
fun channelDemo() {
    val channel = Channel<Int>(Channel.BUFFERED)  // 带缓冲

    // 生产者
    viewModelScope.launch {
        for (i in 1..10) {
            channel.send(i)  // 挂起直到消费者接收
        }
        channel.close()
    }

    // 消费者
    viewModelScope.launch {
        for (value in channel) {  // 或 channel.consumeEach { }
            println(value)
        }
    }
}

// Flow 的背压处理
val flow = MutableSharedFlow<Int>(
    replay = 0,                  // 重放几个旧值给新订阅者
    extraBufferCapacity = 0,     // 额外缓冲容量
    onBufferOverflow = BufferOverflow.SUSPEND  // 背压策略
)

flow.onBufferOverflow(BufferOverflow.DROP_OLDEST)  // 丢弃旧值
flow.onBufferOverflow(BufferOverflow.DROP_LATEST)   // 丢弃新值
flow.onBufferOverflow(BufferOverflow.SUSPEND)       // 挂起（默认）
```

---

## 9. Android 线程模型

### 9.1 主线程职责

Android 主线程（UI 线程）职责：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 主线程职责                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  主线程不能做的事情：
  ─────────────────────────────────────────────────────────────────────────
  1. 网络请求（NetworkOnMainThreadException）
  2. 耗时数据库操作
  3. 耗时的文件操作
  4. 大量的计算
  5. 任何超过 16ms 的操作（导致卡顿）

  主线程的职责：
  ─────────────────────────────────────────────────────────────────────────
  1. 接收用户输入事件
  2. 更新 UI（Views）
  3. 分发事件给合适的 View
  4. 执行短时动画
  5. 调用 Choreographer 进行帧渲染
  6. 处理 View 树的测量、布局、绘制

  主线程消息循环：
  ─────────────────────────────────────────────────────────────────────────
  ActivityThread.main()
      └── Looper.prepareMainLooper()
          └── new Handler(Looper.getMainLooper())
          └── Looper.loop()  // 永不退出
              └── MessageQueue.next()  // 有消息则处理，无消息则阻塞（epoll_wait）
```

### 9.2 Binder 线程池

Binder 是 Android IPC（进程间通信）核心机制，Binder 线程池处理 IPC 调用。

```java
// 位置：frameworks/native/libs/binder/ProcessState.cpp
static constexpr int kMaxThreadPoolSize = 16;

// Binder 线程池特点：
// 1. 最大 16 个线程
// 2. 按需创建（第一个客户端调用时创建）
// 3. 空闲回收
// 4. 处理来自其他进程的 IPC 请求

// 常见错误：在 Binder 线程中执行耗时操作
// AIDL 示例
class MyAidlImpl extends IMyAidlInterface.Stub {
    @Override
    public String getData() throws RemoteException {
        // 错误：Binder 线程执行耗时操作
        return doNetworkRequest();  // 会阻塞其他 IPC 调用！

        // 正确：转发到工作线程
        // ...
    }
}
```

### 9.3 Android 特有的线程优先级

```java
// Android 用 nice 值控制线程优先级：范围 -20（最高）到 +19（最低）
// nice 值越低，优先级越高

// Java 线程优先级 1-10 映射：
// Thread.MIN_PRIORITY(1) = nice +19（最低）
// Thread.NORM_PRIORITY(5) = nice 0（默认）
// Thread.MAX_PRIORITY(10) = nice -20（最高）

// Android 专用优先级常量
Process.setThreadPriority(Process.THREAD_PRIORITY_DEFAULT);      // 0，主线程默认
Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);   // 10，后台线程
Process.setThreadPriority(Process.THREAD_PRIORITY_FOREGROUND);   // -2，提高优先级
Process.setThreadPriority(Process.THREAD_PRIORITY_DISPLAY);      // -4，显示相关
Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_DISPLAY); // -8，紧急显示
Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO);        // -16，音频
Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_AUDIO); // -19，实时音频

// 设置当前线程为后台
Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);

// 设置其他线程优先级
Thread otherThread = thread;
Process.setThreadPriority(otherThread, Process.THREAD_PRIORITY_FOREGROUND);

// 注意：nice 值范围是 -20 到 +19
// Android Process.setThreadPriority 接受的是 Android 优先级常量，不是 Java 优先级
```

---

## 10. 并发设计模式

### 10.1 Thread-Per-Message

每个请求一个线程，简单但不适合高并发。

```java
// 不推荐：每个请求一个线程，开销大
public void handleRequest(Request request) {
    new Thread(() -> handleRequest(request)).start();
}

// 推荐：使用线程池
public class ThreadPoolDemo {
    private final ExecutorService executor = Executors.newFixedThreadPool(10);

    public void handleRequest(Request request) {
        executor.execute(() -> handleRequest(request));
    }

    private void handleRequest(Request request) {
        // 业务逻辑
    }
}
```

### 10.2 Worker Thread

预先创建线程池，复用线程，配合任务队列使用。

```java
// Worker Thread 模式
class WorkerThreadDemo {
    private final BlockingQueue<Task> taskQueue = new LinkedBlockingQueue<>(100);
    private final ExecutorService workers = Executors.newFixedThreadPool(4);

    public WorkerThreadDemo() {
        // 预创建工作线程
        for (int i = 0; i < 4; i++) {
            workers.submit(this::processTasks);
        }
    }

    private void processTasks() {
        while (true) {
            try {
                Task task = taskQueue.take();  // 阻塞等待
                task.execute();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    public void submit(Task task) {
        taskQueue.offer(task);
    }

    interface Task {
        void execute();
    }
}
```

### 10.3 Producer-Consumer

解耦生产者和消费者，BlockingQueue 是核心实现。

```java
// 生产者-消费者模式
class ProducerConsumerPattern {
    private final BlockingQueue<Item> queue = new LinkedBlockingQueue<>(100);

    public void start() {
        // 4个生产者
        IntStream.range(0, 4).forEach(i ->
            new Thread(() -> {
                while (true) {
                    Item item = produce();
                    try {
                        queue.put(item);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }, "Producer-" + i).start()
        );

        // 2个消费者
        IntStream.range(0, 2).forEach(i ->
            new Thread(() -> {
                while (true) {
                    try {
                        Item item = queue.take();
                        consume(item);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }, "Consumer-" + i).start()
        );
    }

    private Item produce() { return new Item(); }
    private void consume(Item item) { }

    static class Item { }
}
```

### 10.4 Pipeline

流水线处理，每阶段可并行，用 BlockingQueue 连接各阶段。

```java
// Pipeline 模式
class PipelineDemo {
    private final BlockingQueue<Data> q1 = new LinkedBlockingQueue<>(50);
    private final BlockingQueue<Data> q2 = new LinkedBlockingQueue<>(50);
    private final BlockingQueue<Data> q3 = new LinkedBlockingQueue<>(50);

    public void pipeline() {
        startStage("Reader", () -> {
            while (true) {
                Data d = readData();
                if (!q1.offer(d)) {
                    // 处理满的情况
                }
            }
        });

        startStage("Processor", () -> {
            while (true) {
                Data d = q1.poll();
                if (d != null) {
                    Data processed = process(d);
                    q2.offer(processed);
                }
            }
        });

        startStage("Writer", () -> {
            while (true) {
                Data d = q2.poll();
                if (d != null) {
                    writeData(d);
                }
            }
        });
    }

    private void startStage(String name, Runnable task) {
        new Thread(() -> {
            Thread.currentThread().setName(name);
            task.run();
        }).start();
    }

    private Data readData() { return new Data(); }
    private Data process(Data d) { return d; }
    private void writeData(Data d) { }

    static class Data { }
}
```

### 10.5 Actor 模型

每个 Actor 独占自己的状态，通过消息传递通信。Kotlin 可用 Channel + Coroutine 实现。

```kotlin
// 用 Channel 模拟 Actor
class CounterActor {
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private val channel = Channel<Msg>(Channel.UNLIMITED)

    private var count = 0

    init {
        scope.launch {
            channel.consumeEach { msg ->
                when (msg) {
                    is Increment -> count++
                    is GetCount -> msg.reply.complete(count)
                }
            }
        }
    }

    suspend fun increment() {
        channel.send(Increment)
    }

    suspend fun getCount(): Int {
        val reply = CompletableDeferred<Int>()
        channel.send(GetCount(reply))
        return reply.await()
    }

    fun close() {
        scope.cancel()
    }

    sealed class Msg
    object Increment : Msg()
    class GetCount(val reply: CompletableDeferred<Int>) : Msg()
}

// 使用
val actor = CounterActor()
actor.increment()
actor.increment()
val count = runBlocking { actor.getCount() }  // count = 2
```

---

## 11. 性能与反模式

### 11.1 常见性能问题

#### 锁竞争激烈

```java
// 问题：锁粒度太大
class BadLock {
    private final Object lock = new Object();
    private final Map<String, Object> cache = new HashMap<>();

    public Object get(String key) {
        synchronized (lock) {  // 整个 cache 被锁
            return cache.get(key);
        }
    }

    // 优化：使用 ConcurrentHashMap
    private final ConcurrentHashMap<String, Object> betterCache =
        new ConcurrentHashMap<>();

    public Object getBetter(String key) {
        return betterCache.get(key);  // 无锁
    }
}
```

#### 线程过多

```java
// 问题：每个任务创建一个线程
for (int i = 0; i < 10000; i++) {
    new Thread(() -> doWork()).start();  // 创建10000个线程！
}

// 解决：使用线程池
ExecutorService pool = Executors.newFixedThreadPool(100);
for (int i = 0; i < 10000; i++) {
    pool.execute(() -> doWork());
}
```

#### 伪共享（False Sharing）

```java
// 问题：多个线程修改同一缓存行的不同变量
class FalseSharingDemo {
    static class Counter {
        volatile long value1 = 0;
        volatile long value2 = 0;
        volatile long value3 = 0;
        volatile long value4 = 0;
    }

    public static void main(String[] args) throws Exception {
        Counter c = new Counter();

        // 4个线程各修改一个变量，但都在同一缓存行
        // 修改任意一个，整个缓存行失效
    }
}

// 解决：缓存行填充（LongAdder 已经做了）
```

### 11.2 并发反模式

#### 反模式1：在锁内执行耗时操作

```java
// 错误
public void wrong() {
    synchronized (lock) {
        networkCall();  // 阻塞其他线程！
    }
}

// 正确
public void right() {
    Object cached;
    synchronized (lock) {
        cached = cachedData;  // 只锁快速操作
    }
    processData(cached);  // 耗时操作放外面
}
```

#### 反模式2：省略 finally 中的 unlock

```java
// 错误
public void wrong() {
    lock.lock();
    if (condition()) {
        return;  // 锁未释放！
    }
    lock.unlock();
}

// 正确
public void right() {
    lock.lock();
    try {
        if (condition()) {
            return;
        }
    } finally {
        lock.unlock();  // 始终释放
    }
}
```

#### 反模式3：使用 Thread.sleep 等待条件

```java
// 错误：浪费 CPU，不精确，响应差
public void wrong() {
    while (!condition) {
        Thread.sleep(1000);  // 一直睡1秒
    }
}

// 正确：用 wait/notify 或 Condition
public void right() {
    synchronized (lock) {
        while (!condition) {
            lock.wait();  // 高效，精确
        }
    }
}
```

#### 反模式4：混淆线程和协程

```kotlin
// 错误：在协程里用 Thread.sleep
suspend fun wrong() {
    Thread.sleep(1000)  // 阻塞协程所在线程！整个线程被卡住
}

// 正确：用 delay（挂起协程，不阻塞线程）
suspend fun right() {
    delay(1000)  // 挂起协程，线程可以执行其他协程
}
```

---

## 12. 面试高频问题

**Q1: synchronized 和 Lock 的区别？**

| 特性 | synchronized | Lock |
|------|-------------|------|
| 响应中断 | 不能 | 可以（lockInterruptibly） |
| 尝试获取锁 | 不能 | 可以（tryLock） |
| 超时获取 | 不能 | 可以（tryLock(timeout)） |
| 公平锁 | 不支持（非公平） | 支持（fair=true） |
| 多条件 | 不能 | 可以（多个 Condition） |
| 锁释放 | 自动（出块） | 必须手动 |
| 性能 | JVM 优化后相近 | 稍灵活 |

**Q2: volatile 和 synchronized 的区别？**

volatile 只保证可见性和有序性，不保证原子性；synchronized 保证原子性、可见性和有序性。volatile 是轻量级的，不阻塞线程。

**Q3: 线程池的核心参数有哪些？**

corePoolSize（核心线程数）、maximumPoolSize（最大线程数）、keepAliveTime（空闲存活时间）、unit（时间单位）、workQueue（任务队列）、threadFactory（线程工厂）、handler（拒绝策略）。

**Q4: 线程池的执行流程？**

线程数 < corePoolSize → 创建核心线程执行；队列满 → 创建非核心线程执行；达 maxPoolSize → 拒绝策略。

**Q5: ConcurrentHashMap 如何实现线程安全？**

JDK 7 分段锁（Segment 分段）；JDK 8+ 用 CAS + synchronized，读操作无锁（volatile 读取），写操作锁粒度细化到单个桶，链表超过 8 个节点转红黑树。

**Q6: 什么是 CAS？有什么问题？**

Compare-And-Swap，硬件级原子操作。三个操作数：内存位置、预期原值、新值。问题是：ABA 问题（用 AtomicStampedReference）、自旋开销（激烈竞争时性能下降）、只能保证单个变量原子性。

**Q7: Coroutine 和线程的区别？**

协程是用户态调度，切换开销极小（状态机），挂起不阻塞线程；线程由 OS 调度，上下文切换开销大。线程是抢占式的，协程是协作式的（主动让出）。

**Q8: 如何避免死锁？**

避免嵌套锁、按固定顺序获取锁、使用带超时的锁（tryLock）、减少锁持有时间、用 tryLock() 探测。

**Q9: 生产者-消费者模式如何实现？**

用 BlockingQueue：put() 满则阻塞，take() 空则阻塞。或者用 wait/notify 配合 synchronized。

**Q10: 什么是线程安全？如何实现？**

多线程访问时始终表现正确。实现方式：synchronized、Lock、volatile（单变量）、原子变量、并发容器、不可变对象、ThreadLocal。

**Q11: 什么是伪共享？如何避免？**

CPU 缓存行 64 字节，多线程访问同一缓存行的不同变量，一个修改导致整个缓存行失效。避免方式：LongAdder 分段设计、使用 @Contended 注解（JDK 8+）、手动 padding。

**Q12: Coroutine 的 suspend 原理？**

suspend 函数被编译器转换为状态机，用 Continuation 对象保存状态。挂起点是状态转换点，恢复时从上次挂起点继续执行，不创建新线程。

---

## 13. Android 并发专题

### 13.1 Handler 与线程

Handler 是 Android 消息机制的核心，关联线程的 Looper 和 MessageQueue。

```java
// 主线程：系统已创建 Looper，直接使用
class MainActivity extends AppCompatActivity {
    private Handler handler = new Handler(Looper.getMainLooper());

    public void onClick(View v) {
        // 1. post(Runnable)
        handler.post(() -> {
            // 在主线程执行
            textView.setText("updated");
        });

        // 2. sendMessage
        Message msg = handler.obtainMessage(MSG_WHAT, data);
        handler.sendMessage(msg);

        // 3. postDelayed 延迟
        handler.postDelayed(() -> {
            // 3秒后执行
        }, 3000);

        // 4. removeCallbacks 取消
        handler.removeCallbacks(runnable);
        handler.removeMessages(MSG_WHAT);
    }

    @Override
    public boolean handleMessage(Message msg) {
        switch (msg.what) {
            case MSG_WHAT:
                // 处理消息
                return true;
        }
        return false;
    }
}

// 子线程创建 Handler（必须先创建 Looper）
class MyThread extends Thread {
    private Handler handler;

    @Override
    public void run() {
        Looper.prepare();  // 创建 Looper 和 MessageQueue

        handler = new Handler(Looper.myLooper()) {
            @Override
            public boolean handleMessage(Message msg) {
                // 处理消息
                return true;
            }
        };

        Looper.loop();  // 进入消息循环
    }
}
```

#### 子线程创建 Handler 的坑

```java
// 错误：在没有 Looper 的子线程创建 Handler
class BadDemo extends Thread {
    private Handler handler;

    @Override
    public void run() {
        // RuntimeException: Can't create handler inside thread that has not called Looper.prepare()
        handler = new Handler();  // 没有 Looper，崩溃！

        // 正确
        Looper.prepare();
        handler = new Handler(Looper.myLooper());
        Looper.loop();
    }
}

// 常见错误：子线程更新 UI
class BadUIUpdate extends Thread {
    @Override
    public void run() {
        // 崩溃：Only the original thread that created a View hierarchy can touch its views
        textView.setText("更新UI");  // 在子线程更新 UI！
    }
}
```

### 13.2 runOnUiThread vs post vs View.post

```java
// Activity 中的方法
class UiThreadDemo extends AppCompatActivity {

    // 方式1：runOnUiThread
    // 如果当前是主线程，直接执行；否则切换到主线程执行
    public void method1() {
        runOnUiThread(() -> {
            textView.setText("updated");
        });
    }

    // 方式2：Handler.post
    // 总是切换到关联的 Looper 所在线程
    public void method2() {
        Handler handler = new Handler(getMainLooper());
        handler.post(() -> {
            textView.setText("updated");
        });
    }

    // 方式3：View.post
    // 当 View 已经 attached 到窗口时，Runnable 在主线程执行
    // 比 runOnUiThread 更可靠（Activity 未完全创建时也能用）
    public void method3() {
        textView.post(() -> {
            textView.setText("updated");
        });
    }

    // View.post 的可靠性演示
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 此时 View 已 attached，post 肯定在主线程执行
        textView.post(() -> {
            // 此时肯定可以获取到宽高
            int width = textView.getWidth();
            int height = textView.getHeight();
        });
    }
}
```

三者对比：

| 方法 | 线程判断 | 可靠性 | 典型场景 |
|------|---------|--------|---------|
| runOnUiThread | 检查当前线程 | 一般 | Activity 内通用 |
| Handler.post | 固定线程 | 高 | 明确知道目标线程 |
| View.post | View 已 attached | 最高 | onCreate/onResume 中获取 View 尺寸 |

### 13.3 IntentService vs JobIntentService

```java
// IntentService（已废弃，Android 11+）
// 特点：串行执行，自销毁，是 Service 在独立线程处理任务
public class MyIntentService extends IntentService {
    public MyIntentService() {
        super("MyIntentService");
    }

    @Override
    protected void onHandleIntent(Intent intent) {
        // 运行在独立工作线程
        // 所有任务串行执行，一个执行完才执行下一个
        String data = intent.getStringExtra("data");
        process(data);
    }
}

// 问题：IntentService 是半废弃的
// Android 11 开始系统不再bind到未声明 exported 的 IntentService

// 推荐：JobIntentService（支持 Android 8.0+）
public class MyJobIntentService extends JobIntentService {

    public static void enqueueWork(Context context, Intent work) {
        enqueueWork(context, MyJobIntentService.class, JOB_ID, work);
    }

    @Override
    protected void onHandleWork(Intent intent) {
        // 运行在独立工作线程
        String data = intent.getStringExtra("data");
        process(data);
    }

    @Override
    public boolean onStopCurrentWork() {
        // 是否停止当前任务
        return super.onStopCurrentWork();
    }
}
```

### 13.4 AsyncTask 废弃原因

AsyncTask 在 Android 11 正式废弃，以下是原因：

```java
// AsyncTask 的问题
class AsyncTaskDemo extends AsyncTask<Void, Integer, String> {

    // 问题1：生命周期不同步
    // Activity 销毁后，AsyncTask 仍在运行，可能导致内存泄漏
    public void badUsage(Activity activity) {
        new AsyncTask<Void, Void, String>() {
            @Override
            protected String doInBackground(Void... voids) {
                return doNetworkRequest();  // 耗时操作
            }

            @Override
            protected void onPostExecute(String result) {
                // Activity 已销毁，更新已无效
                // 甚至崩溃：Activity has been destroyed
                activity.updateUI(result);  // 可能 NPE
            }
        }.execute();
    }

    // 问题2：并行/串行行为不一致
    // Android 1.6 之前：串行
    // Android 1.6 - 3.0：并行（SERIAL_EXECUTOR 内部是线程池）
    // Android 3.0+：默认串行（用 SERIAL_EXECUTOR）
    // Android 4.1+：如果 TARGETING_HONEYCOMB，则串行

    // 问题3：内存顺序问题
    // 使用 AsyncTask<Void, Void, String> 时，泛型参数容易混淆

    // 问题4：配置变更时数据丢失
    // Activity 旋转时重建，AsyncTask 持有旧 Activity 引用
}

// 正确替代方案
class CorrectUsage extends AppCompatActivity {
    private ViewModel viewModel;

    public void correct() {
        // 方案1：ViewModel + Coroutines（推荐）
        viewModelScope.launch {
            String result = repository.fetchData();
            // ViewModelScope 自动取消
        }

        // 方案2：LiveData + Coroutines
        viewModel.data.observe(this, data -> {
            textView.setText(data);
        });
    }
}
```

### 13.5 WorkManager 并发模型

WorkManager 是 Android 后台任务推荐方案，支持延迟、周期、约束条件。

```java
// WorkManager 基本使用
class WorkManagerDemo {

    public void simpleWork() {
        OneTimeWorkRequest work = new OneTimeWorkRequestBuilder<MyWorker>()
            .build();

        WorkManager.getInstance(context).enqueue(work);
    }

    // 带约束的工作
    public void constrainedWork() {
        Constraints constraints = new Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)  // 网络连接
            .setRequiresBatteryNotLow(true)                // 电量不低
            .setRequiresCharging(true)                     // 充电中
            .build();

        OneTimeWorkRequest work = new OneTimeWorkRequestBuilder<MyWorker>()
            .setConstraints(constraints)
            .setInitialDelay(10, TimeUnit.SECONDS)         // 延迟
            .addTag("myWork")                              // 标签
            .build();

        WorkManager.getInstance(context).enqueue(work);
    }

    // PeriodicWorkRequest：周期任务（最小15分钟）
    public void periodicWork() {
        PeriodicWorkRequest periodicWork = new PeriodicWorkRequestBuilder<MyWorker>(
            15, TimeUnit.MINUTES,  // 重复间隔
            5, TimeUnit.MINUTES     // 弹性间隔
        ).build();

        WorkManager.getInstance(context)
            .enqueueUniquePeriodicWork(
                "periodicSync",
                ExistingPeriodicWorkPolicy.KEEP,
                periodicWork
            );
    }

    // 观察工作状态
    public void observeWork() {
        WorkManager.getInstance(context)
            .getWorkInfoByIdLiveData(workRequest.getId())
            .observe(this, workInfo -> {
                if (workInfo.getState() == WorkInfo.State.SUCCEEDED) {
                    // 成功
                } else if (workInfo.getState() == WorkInfo.State.FAILED) {
                    // 失败
                }
            });
    }
}

// Worker 实现
public class MyWorker extends Worker {

    public MyWorker(@NonNull Context context, @NonNull WorkerParameters params) {
        super(context, params);
    }

    @NonNull
    @Override
    public Result doWork() {
        try {
            // 运行在工作线程（不是主线程！）
            String data = doNetworkRequest();
            saveToDatabase(data);
            return Result.success();  // 成功
        } catch (Exception e) {
            if (retry()) {
                return Result.retry();  // 重试
            }
            return Result.failure();  // 失败
        }
    }
}
```

WorkManager 并发特点：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WorkManager 特性                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 后台任务保障：
  ─────────────────────────────────────────────────────────────────────────
  - 应用退出后任务继续执行（除非被系统杀死）
  - 设备重启后自动恢复（如果满足条件）
  - 不保证精确时间（系统会合并优化）

  2. 线程模型：
  ─────────────────────────────────────────────────────────────────────────
  - doWork() 运行在独立后台线程
  - 默认使用 ExecutorService（非主线程）
  - 支持 ListenableWorker 自定义线程

  3. 约束条件：
  ─────────────────────────────────────────────────────────────────────────
  - 网络状态
  - 电池状态
  - 存储空间
  - 设备空闲（Doze）状态

  4. vs 其他方案：
  ─────────────────────────────────────────────────────────────────────────
  IntentService：需要 Service，简单但功能有限
  JobScheduler：API 21+，系统级
  WorkManager：API 14+，Google 推荐，支持约束、重试、周期
```

### 13.6 子线程操作 Android UI 的正确方式

```java
// 原则：所有 UI 操作必须在主线程

// 场景1：网络回调后更新 UI
public class NetworkCallbackDemo extends AppCompatActivity {
    private TextView textView;

    public void fetchData() {
        new Thread(() -> {
            String result = networkRequest();
            // 错误：子线程更新 UI
            // textView.setText(result);  // 崩溃！

            // 正确1：runOnUiThread
            runOnUiThread(() -> textView.setText(result));

            // 正确2：Handler
            new Handler(Looper.getMainLooper()).post(() ->
                textView.setText(result)
            );

            // 正确3：View.post
            textView.post(() -> textView.setText(result));

            // 正确4：LiveData/ViewModel（推荐）
            viewModel.data.observe(this, data ->
                textView.setText(data)
            );
        }).start();
    }
}

// 场景2：定时刷新 UI
public class TimerDemo extends AppCompatActivity {
    private Handler handler = new Handler(Looper.getMainLooper());
    private Runnable refreshRunnable;

    public void startTimer() {
        refreshRunnable = new Runnable() {
            @Override
            public void run() {
                // 更新 UI
                updateUI();
                // 继续定时
                handler.postDelayed(this, 1000);
            }
        };
        handler.post(refreshRunnable);
    }

    public void stopTimer() {
        // 停止时必须移除
        if (refreshRunnable != null) {
            handler.removeCallbacks(refreshRunnable);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stopTimer();  // Activity 销毁时移除，防止泄漏
    }
}

// 场景3：避免内存泄漏
public class LeakDemo extends AppCompatActivity {
    private Handler handler = new Handler(Looper.getMainLooper());

    public void delayedAction() {
        // 错误：Handler 持有 Activity 引用，延迟任务会导致泄漏
        handler.postDelayed(() -> {
            // 如果 Activity 已销毁，这里仍会执行
            // 可能 NPE 或更新已销毁的 UI
        }, 5000);
    }

    // 正确：使用弱引用或 Lifecycle-aware 组件
    public void correctAction() {
        // 方案1：Lifecycle-aware Handler
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            if (!isFinishing() && !isDestroyed()) {
                // Activity 仍然存活
            }
        }, 5000);

        // 方案2：ViewModel + Coroutines（推荐）
        viewModelScope.launch {
            delay(5000);
            // ViewModelScope 会在 onCleared 时取消
        }

        // 方案3：LifecycleScope
        lifecycleScope.launch {
            delay(5000);
        }
    }
}
```

---

## 总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 并发知识体系                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  Java 基础层：
  Thread / Runnable / Callable → 线程创建
  线程状态 → 生命周期理解

  同步机制层：
  synchronized → 基础同步，管程实现
  volatile → 可见性/有序性，不保证原子性
  Lock/Condition → 高级同步
  ReadWriteLock/StampedLock → 读写分离

  并发工具层：
  CountDownLatch → 倒数等待
  CyclicBarrier → 循环栅栏
  Semaphore → 资源限制
  Phaser → 多阶段同步

  原子操作层：
  AtomicInteger/Long → 原子整数
  AtomicReference → 原子引用
  LongAdder → 高并发计数
  CAS → 硬件级原子操作

  并发集合层：
  ConcurrentHashMap → 并发哈希
  CopyOnWriteArrayList → 读多写少
  BlockingQueue → 生产者-消费者
  ThreadLocalMap → 线程局部存储

  线程池层：
  ThreadPoolExecutor → 核心
  Executors → 快速创建
  饱和策略 → 拒绝处理

  Kotlin 协程层：
  Dispatchers → 调度器
  suspend → 挂起原理
  Scope/Context → 生命周期
  Flow/Channel → 异步数据流

  Android 特有层：
  主线程职责 → 不能做的事
  Binder 线程池 → IPC
  Process 优先级 → Android 特有

  设计模式层：
  Thread-Per-Message / Worker Thread / Producer-Consumer / Pipeline / Actor
```

掌握以上内容，就具备了扎实的 Android 并发编程能力，可以自信应对面试和实际开发中的各种并发问题。

---

*文档更新时间: 2026-03-24*
