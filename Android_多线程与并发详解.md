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
   - 5.4 [LongAdder](#54-longadder高并发场景)
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

---

## 1. 概述

多线程与并发是 Android 开发中最核心的能力之一，也是面试的重点难点。现代 Android 开发虽然已经进入 Kotlin 协程时代，但理解底层原理、掌握 Java 并发工具类，对于写出高效正确的并发代码至关重要。

---

## 2. Java 线程基础

### 2.1 Thread 创建与启动

Java 中创建线程有 3 种方式：

```java
// 方式1：继承 Thread
class MyThread extends Thread {
    @Override
    public void run() {
        // 业务逻辑
    }
}
new MyThread().start();  // 注意是 start()，不是 run()

// 方式2：实现 Runnable
class MyRunnable implements Runnable {
    @Override
    public void run() {
        // 业务逻辑
    }
}
new Thread(new MyRunnable()).start();

// 方式3：实现 Callable（有返回值）
class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        return "result";
    }
}
FutureTask<String> task = new FutureTask<>(new MyCallable());
new Thread(task).start();
String result = task.get();
```

注意：`start()` 创建新线程执行 `run()`，`run()` 只是普通方法调用。

### 2.2 线程状态与生命周期

线程有 6 种状态：NEW、RUNNABLE、BLOCKED、WAITING、TIMED_WAITING、TERMINATED。

```
NEW → RUNNABLE：start() 调用后
RUNNABLE → BLOCKED：等待 synchronized 锁
RUNNABLE → WAITING：调用 wait()/join()/LockSupport.park()
RUNNABLE → TIMED_WAITING：调用 sleep()/wait(timeout)/join(timeout)
BLOCKED/WAITING/TIMED_WAITING → RUNNABLE：被唤醒或获得锁
任意 → TERMINATED：run() 执行完毕
```

### 2.3 线程优先级

Java 线程优先级 1-10，默认为 5。优先级只是提示，不保证严格按优先级执行。

```java
thread.setPriority(Thread.MAX_PRIORITY);   // 10
thread.setPriority(Thread.NORM_PRIORITY);  // 5
thread.setPriority(Thread.MIN_PRIORITY);   // 1

// Android 特有优先级
Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);  // 10
Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO);       // -16
```

### 2.4 守护线程

JVM 中所有非守护线程结束时，守护线程被强制终止。典型用途：垃圾回收线程。

```java
Thread daemon = new Thread(() -> { /* 守护任务 */ });
daemon.setDaemon(true);
daemon.start();
```

---

## 3. 线程同步机制

### 3.1 synchronized

synchronized 是 JVM 内置的管程实现，自动获取/释放锁，可重入。

```java
// 同步实例方法（锁对象是 this）
public synchronized void method() { }

// 同步静态方法（锁对象是类对象）
public static synchronized void staticMethod() { }

// 同步代码块（锁对象是指定对象）
public void method() {
    synchronized (lockObject) {
        // 原子操作
    }
}
```

特性：可重入、保证原子性+可见性+有序性。锁升级：偏斜锁 → 轻量级锁 → 重量级锁。

### 3.2 volatile

volatile 是轻量级同步机制，不加锁，只保证可见性和有序性，不保证原子性。

```java
private volatile boolean running = true;

public void stop() {
    running = false;  // 写入对所有线程立即可见
}

public void run() {
    while (running) {  // 读取总是最新值
        // 业务逻辑
    }
}
```

#### volatile 的内存语义

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         volatile 内存语义                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  写操作：
  ┌───────────────────┐      ┌───────────────────┐
  │   写 volatile 变量  │ ───► │  Store 屏障      │
  └───────────────────┘      └───────────────────┘
                                     │
                                     ▼
                          刷新到主内存

  读操作：
  ┌───────────────────┐      ┌───────────────────┐
  │   读 volatile 变量  │ ───► │  Load 屏障      │
  └───────────────────┘      └───────────────────┘
                                     │
                                     ▼
                          从主内存读取

  ─────────────────────────────────────────────────────────────────────────
  写屏障：确保写操作之前的所有修改对其他线程可见
  读屏障：确保读操作之后的所有读取使用最新值
```

#### synchronized vs volatile 详细对比

| 特性 | synchronized | volatile |
|------|-------------|----------|
| 原子性 | ✓ 保证 | ✗ 不保证 |
| 可见性 | ✓ 保证 | ✓ 保证 |
| 有序性 | ✓ 保证 | ✓ 保证 |
| 锁机制 | 隐式锁（管程） | 无锁 |
| 阻塞线程 | 会阻塞 | 不会阻塞 |
| 适用场景 | 复合操作 | 单变量读写 |
| 性能开销 | 较重 | 轻量 |

#### 为什么有了 synchronized 还需要 volatile？

```java
// DCL 单例模式示例
public class Singleton {
    private static volatile Singleton instance;  // 必须加 volatile！
    
    public static Singleton getInstance() {
        if (instance == null) {  // 第一次检查（无锁）
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

关键点：第一次检查 `instance == null` 在 synchronized 块之外！

- synchronized 只能保证块内的有序性
- 第一次检查在块外，不受 synchronized 保护
- volatile 防止 `instance = new Singleton()` 的指令重排序

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    挲止重排序，线程 B 可能获取到未完全初始化的对象！
  线程A: instance = new Singleton();
           ├── 1. 分配内存
           ├── 2. 初始化字段
           ├── 3. 将引用指向内存
           
  如果 2 和 3 重排序：
  线程A: 1 → 3 → 2
  线程B: 检查 instance != null → 使用对象（但字段未初始化！）
```

#### volatile 适用场景

1. 状态标志位：`volatile boolean running`
2. 单例双重检查：DCL 模式
3. 一次性初始化：延迟初始化
4. 独立观察：一个线程写，多个线程读

不适用场景：
- `i++` 等复合操作（需要用 AtomicInteger 或 synchronized）
- 多个变量的原子更新

### 3.3 wait/notify/notifyAll

Object 的等待通知机制，必须在 synchronized 内使用。

```java
synchronized (lock) {
    while (condition不满足) {
        lock.wait();  // 释放锁，进入 WAITING
    }
    // 业务逻辑
    lock.notify();  // 通知一个等待线程
    // 或 lock.notifyAll(); 通知所有等待线程
}
```

必须用 while 循环防止虚假唤醒。

### 3.4 Lock 与 ReentrantLock

ReentrantLock 比 synchronized 更灵活，支持中断、超时、公平锁。

```java
private final ReentrantLock lock = new ReentrantLock();

public void method() {
    lock.lock();
    try {
        // 业务逻辑
    } finally {
        lock.unlock();  // 必须 finally 释放
    }
}

// 尝试获取（非阻塞）
if (lock.tryLock()) { /* ... */ }

// 带超时
lock.tryLock(5, TimeUnit.SECONDS);

// 公平锁
ReentrantLock fairLock = new ReentrantLock(true);
```

### 3.5 ReadWriteLock

读写分离锁，读操作可以并发，写操作独占。

```java
private final ReadWriteLock rwLock = new ReentrantReadWriteLock();

public V get(K key) {
    rwLock.readLock().lock();
    try { return cache.get(key); }
    finally { rwLock.readLock().unlock(); }
}

public void put(K key, V value) {
    rwLock.writeLock().lock();
    try { cache.put(key, value); }
    finally { rwLock.writeLock().unlock(); }
}
```

### 3.6 Condition

多条件等待，比 wait/notify 更灵活。

```java
private final Condition notEmpty = lock.newCondition();
private final Condition notFull = lock.newCondition();

public void put(T item) throws InterruptedException {
    lock.lock();
    try {
        while (count == items.length) notFull.await();
        items[putIndex++] = item;
        count++;
        notEmpty.signal();
    } finally { lock.unlock(); }
}
```

### 3.7 StampedLock

比 ReadWriteLock 更进一步的乐观读，三种模式：写、读、乐观读。

```java
private final StampedLock sl = new StampedLock();

// 悲观读
public double distance() {
    long stamp = sl.readLock();
    try { return Math.sqrt(x*x + y*y); }
    finally { sl.unlockRead(stamp); }
}

// 乐观读（性能最好，写入少时）
public double optimisticDistance() {
    long stamp = sl.tryOptimisticRead();
    double sx = x, sy = y;
    if (!sl.validate(stamp)) {  // 检查戳是否有效
        stamp = sl.readLock();
        try { sx = x; sy = y; }
        finally { sl.unlockRead(stamp); }
    }
    return Math.sqrt(sx*sx + sy*sy);
}
```

---

## 4. Java 并发工具类

### 4.1 CountDownLatch

倒数计数器，等待一组线程完成。

```java
CountDownLatch doneSignal = new CountDownLatch(5);

new Thread(() -> {
    // 任务完成
    doneSignal.countDown();
}).start();

doneSignal.await();  // 等待所有线程完成
```

典型场景：主线程等待多个子线程执行完毕。

### 4.2 CyclicBarrier

循环栅栏，让一组线程互相等待，到达某点后一起恢复执行。

```java
CyclicBarrier barrier = new CyclicBarrier(3, () -> {
    System.out.println("阶段完成!");
});

for (int i = 0; i < 3; i++) {
    new Thread(() -> {
        // 阶段1
        barrier.await();
        // 阶段2
        barrier.await();
    }).start();
}
```

CountDownLatch 是一次性的，CyclicBarrier 可重置后重用。

### 4.3 Semaphore

信号量，控制同时访问某资源的线程数量。

```java
Semaphore available = new Semaphore(5);

available.acquire();  // 获取许可
try {
    // 使用资源
} finally {
    available.release();  // 释放许可
}

// 尝试获取
if (available.tryAcquire()) { /* ... */ }
```

典型场景：连接池、令牌桶、限流。

### 4.4 Exchanger

两个线程交换数据。

```java
Exchanger<DataBuffer> exchanger = new Exchanger<>();

// 线程1
new Thread(() -> {
    DataBuffer empty = new DataBuffer();
    DataBuffer full = exchanger.exchange(empty);  // 用空换满
    process(full);
}).start();

// 线程2
new Thread(() -> {
    DataBuffer full = new DataBuffer(fill());
    DataBuffer empty = exchanger.exchange(full);  // 用满换空
    empty.fill();
}).start();
```

### 4.5 Phaser

多阶段同步器，比 CyclicBarrier 更灵活。

```java
Phaser phaser = new Phaser(3);

for (int i = 0; i < 3; i++) {
    new Thread(() -> {
        // 阶段1
        phaser.arriveAndAwaitAdvance();
        // 阶段2
        phaser.arriveAndAwaitAdvance();
    }).start();
}
```

---

## 5. 原子类与 CAS

### 5.1 AtomicInteger/AtomicLong

无锁的原子整数操作，比 synchronized 更轻量。

```java
private final AtomicInteger count = new AtomicInteger(0);

count.incrementAndGet();         // i++
count.getAndIncrement();         // 返回旧值后++
count.compareAndSet(expected, newValue);  // CAS
count.updateAndGet(current -> current + delta);  // 原子更新
```

### 5.2 AtomicReference

无锁实现对象的原子更新。

```java
private final AtomicReference<Node> top = new AtomicReference<>();

public void push(T item) {
    Node newHead = new Node(item);
    Node oldHead;
    do {
        oldHead = top.get();
        newHead.next = oldHead;
    } while (!top.compareAndSet(oldHead, newHead));
}
```

### 5.3 AtomicIntegerFieldUpdater

对普通字段的原子更新，节省内存。

```java
class Student {
    volatile int score;  // 必须是 volatile，不能是 private
}

AtomicIntegerFieldUpdater<Student> updater =
    AtomicIntegerFieldUpdater.newUpdater(Student.class, "score");

updater.incrementAndGet(student);  // 原子更新
```

### 5.4 LongAdder（高并发场景）

高并发计数器，比 AtomicLong 性能更好。热点数据分段，多线程更新不同单元。

```java
private final LongAdder clicks = new LongAdder();

clicks.increment();
clicks.add(delta);
long total = clicks.sum();

// LongAccumulator：更通用的累加器
LongAccumulator maxScore = new LongAccumulator(Long::max, 0);
maxScore.accumulate(score);
```

### 5.5 CAS 原理

CAS（Compare-And-Swap）是硬件级别的原子操作。

```
三个操作数：内存位置(V)、预期原值(A)、新值(B)
如果 V == A，将 V 设为 B，返回 true
否则什么都不做，返回 false
```

Java 的 CAS 由 CPU 的 cmpxchg 指令支持。ABA 问题用 AtomicStampedReference 解决（带版本号）。

## 6. 并发集合

### 6.1 ConcurrentHashMap

高性能并发哈希映射。JDK 8 前分段锁，JDK 8 后 CAS + synchronized。

```java
ConcurrentHashMap<String, Object> map = new ConcurrentHashMap<>();

map.putIfAbsent("key", "value");  // 不存在才插入
map.remove("key", expectedValue);  // 值匹配才删除
map.replace("key", oldValue, newValue);  // 值匹配才替换
map.compute("counter", (k, v) -> v == null ? "1" : String.valueOf(Integer.parseInt(v) + 1));
```

读操作无锁（volatile 读取），写操作锁粒度细化到单个桶。

### 6.2 CopyOnWriteArrayList

写时复制列表。读操作无锁，写操作复制全量数组。

```java
CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();

list.get(index);        // 无锁，极快
list.contains(item);    // 无锁
list.add(item);         // 复制全量数组
list.forEach(action);   // 遍历快照，写操作不影响读者
```

适用：读多写少（95% 读 5% 写）、不需要实时数据。不适用：写操作频繁、内存敏感。

### 6.3 BlockingQueue

阻塞队列，生产者-消费者模式核心。

```java
BlockingQueue<String> queue = new LinkedBlockingQueue<>(100);

// 阻塞组
queue.put(item);   // 队列满则阻塞
String item = queue.take();  // 队列空则阻塞

// 非阻塞组
queue.offer(item, 5, TimeUnit.SECONDS);  // 超时返回 false
String item = queue.poll(5, TimeUnit.SECONDS);  // 超时返回 null
```

常用实现：LinkedBlockingQueue（无界/有界）、ArrayBlockingQueue（有界）、SynchronousQueue（直接交接）。

### 6.4 ConcurrentLinkedQueue/Deque

无界非阻塞队列。

```java
ConcurrentLinkedQueue<Task> queue = new ConcurrentLinkedQueue<>();
queue.offer(task);
Task t = queue.poll();  // 无则返回 null

ConcurrentLinkedDeque<Task> deque = new ConcurrentLinkedDeque<>();
deque.addFirst(task);
deque.addLast(task);
deque.pollFirst();
deque.pollLast();
```

### 6.5 ThreadLocalMap

ThreadLocal 的内部实现，使用弱引用 key 防止内存泄漏。

```java
ThreadLocal<String> tl = ThreadLocal.withInitial(() -> "default");

tl.set("value");          // 设置
String v = tl.get();      // 获取
tl.remove();              // 清理，防止内存泄漏
```

内存泄漏场景：线程池中线程复用，如果不在 finally 中 remove()，value 仍会留在 ThreadLocalMap 中。

## 7. 线程池

### 7.1 ThreadPoolExecutor 核心参数

```java
new ThreadPoolExecutor(
    int corePoolSize,        // 核心线程数
    int maximumPoolSize,     // 最大线程数
    long keepAliveTime,      // 非核心线程空闲存活时间
    TimeUnit unit,           // 时间单位
    BlockingQueue<Runnable> workQueue,    // 任务队列
    ThreadFactory threadFactory,          // 线程工厂
    RejectedExecutionHandler handler     // 拒绝策略
);
```

### 7.2 线程池执行流程

```
提交任务 → 线程数 < corePoolSize？ → 创建核心线程执行
         → 否 → 队列未满？ → 入队列等待
         → 否 → 线程数 < maximumPoolSize？ → 创建非核心线程执行
         → 否 → 执行拒绝策略
```

### 7.3 线程池分类

```java
// 固定大小线程池
Executors.newFixedThreadPool(4);  // core=max=n，队列无界

// 缓存线程池
Executors.newCachedThreadPool();  // core=0，max=INT_MAX，60秒回收

// 单线程池
Executors.newSingleThreadExecutor();  // 保证顺序执行

// 定时任务线程池
Executors.newScheduledThreadPool(4);
pool.schedule(task, 3, TimeUnit.SECONDS);
pool.scheduleAtFixedRate(task, 1, 5, TimeUnit.SECONDS);

// 工作窃取线程池
Executors.newWorkStealingPool(4);  // ForkJoinPool 实现
```

### 7.4 线程池饱和策略

队列满 + 线程数达最大值时触发：

- **AbortPolicy**（默认）：抛 RejectedExecutionException
- **CallerRunsPolicy**：用调用者线程执行（减速效果）
- **DiscardPolicy**：静默丢弃
- **DiscardOldestPolicy**：丢弃最老任务

### 7.5 线程池参数配置

- CPU 密集型：线程数 = CPU 核心数 + 1
- IO 密集型：线程数 = CPU 核心数 × (1 + 等待时间 / 计算时间)

不要用无界队列 + 固定线程池，推荐用 CallerRunsPolicy 拒绝策略。

## 8. Kotlin 协程原理

### 8.1 协程是什么

协程是用户态调度的轻量级线程。切换开销极小，挂起不阻塞线程。

| 对比 | 线程 | 协程 |
|------|------|------|
| 切换开销 | 大（1-2KB 栈） | 极小（状态机） |
| 调度 | 操作系统 | 用户态 |
| 阻塞 | 阻塞线程 | 挂起协程 |
| 并发 | 受线程数限制 | 单线程可并发多个 |

### 8.2 协程调度器 Dispatchers

```kotlin
launch(Dispatchers.Main) { /* 主线程，UI操作 */ }
launch(Dispatchers.IO) { /* IO线程池，网络/文件/数据库 */ }
launch(Dispatchers.Default) { /* CPU密集型，核心数线程 */ }
```

Dispatchers.IO：max(2, CPU核心数 × 2) 个线程。Dispatchers.Default：max(2, CPU核心数) 个线程。

### 8.3 协程上下文与作用域

```kotlin
// viewModelScope：ViewModel 推荐，ViewModel 清除时自动取消
viewModelScope.launch { /* ... */ }

// lifecycleScope：Activity/Fragment 推荐
lifecycleScope.launch { /* ... */ }

// 自定义作用域
val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
scope.launch { /* 需要手动 cancel */ }
```

结构化并发：父协程取消，子协程全部取消；子协程失败默认取消父协程和所有兄弟。用 SupervisorJob 可让子协程失败不影响父和兄弟。

### 8.4 suspend 原理

suspend 函数被编译器转换为状态机：

```kotlin
suspend fun fetchData(): String {
    val r1 = request1()  // 状态0
    val r2 = request2(r1)  // 状态1
    return process(r2)  // 状态2
}
```

编译后变成带有 Continuation 参数的状态机，每次 await/suspend 调用都是一次状态转换。

### 8.5 协程构建器

```kotlin
// launch：fire and forget，不返回结果
viewModelScope.launch { /* ... */ }

// async：返回 Deferred
val deferred = async { api.fetchUser() }
val user = deferred.await()

// withContext：切换上下文并返回结果
val data = withContext(Dispatchers.IO) { api.fetch() }

// withTimeout：超时控制
withTimeout(3000L) { /* 超时抛异常 */ }
val result = withTimeoutOrNull(3000L) { /* 超时返回 null */ }
```

### 8.6 协程取消

```kotlin
val job = viewModelScope.launch {
    repeat(1000) { i ->
        delay(500L)  // 挂起点，会检查取消
    }
}
job.cancel()
job.cancelAndJoin()
```

注意：delay() 是检查点会响应取消；CPU 密集型任务不会检查取消，需要定期 yield()。

### 8.7 协程异常处理

```kotlin
// try-catch
try {
    val data = api.fetch()
} catch (e: Exception) {
    handleError(e)
}

// CoroutineExceptionHandler
val handler = CoroutineExceptionHandler { _, e -> println("Error: $e") }
CoroutineScope(SupervisorJob() + handler).launch { /* ... */ }

// async 异常在 await() 时抛出
val deferred = async { throw Exception("error") }
try { deferred.await() } catch (e: Exception) { /* ... */ }

// runCatching
val result = runCatching { api.fetch() }
result.onSuccess { }.onFailure { }
```

### 8.8 Flow 异步数据流

Flow 是冷异步数据流，替代 RxJava。

```kotlin
// 创建 Flow
fun createFlow(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(100)
        emit(i)
    }
}

// 收集
viewModelScope.launch {
    createFlow().collect { value -> println(value) }
}

// 操作符
flowOf(1, 2, 3)
    .map { it * 2 }
    .filter { it > 3 }
    .flowOn(Dispatchers.IO)
    .catch { emit(-1) }
    .collect { }

// StateFlow：状态流
private val _state = MutableStateFlow(0)
val state: StateFlow<Int> = _state.asReadOnlyStateFlow()

// SharedFlow：共享流
private val _events = MutableSharedFlow<Event>()
val events: SharedFlow<Event> = _events.asSharedFlow()

// Channel：协程间通信
val channel = Channel<Int>(Channel.BUFFERED)
channel.send(1)
val value = channel.receive()
```

## 9. Android 线程模型

### 9.1 主线程职责

主线程（UI线程）职责：
- 接收用户输入事件
- 更新 UI（Views）
- 分发事件给合适的 View
- 执行短时动画
- 调用 Choreographer 进行帧渲染

主线程不能做：网络请求、耗时数据库操作、大量计算、超过 16ms 的操作。

主线程消息循环：ActivityThread.main() → Looper.prepareMainLooper() → Looper.loop()，永不退出。

### 9.2 Binder 线程池

Binder 线程池处理 IPC 调用，最大 16 个线程，按需创建，空闲回收。不要在 Binder 线程中执行耗时操作。

```java
// 位置：frameworks/native/libs/binder/ProcessState.cpp
static constexpr int kMaxThreadPoolSize = 16;
```

常见错误：在 AIDL 实现的 onTransact() 中执行耗时操作 → Binder 线程被阻塞 → IPC 调用排队。

### 9.3 Android 特有的线程优先级

```java
// Android 线程优先级（nice 值）
Process.setThreadPriority(Process.THREAD_PRIORITY_DEFAULT);    // 0，主线程
Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);  // 10，后台线程
Process.setThreadPriority(Process.THREAD_PRIORITY_FOREGROUND); // -2，前台
Process.setThreadPriority(Process.THREAD_PRIORITY_DISPLAY);    // -4，显示
Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO);      // -16，音频
Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_AUDIO);// -19，实时音频
```

nice 值范围 -20（最高）到 +19（最低），映射到 Linux 优先级 100-139。

---

## 10. 并发设计模式

### 10.1 Thread-Per-Message

每个请求一个线程，简单但不适合高并发。

```java
// 不推荐：线程开销大
new Thread(() -> handleRequest(request)).start();

// 推荐：使用线程池
executor.execute(() -> handleRequest(request));
```

### 10.2 Worker Thread

预先创建线程池，复用线程，配合任务队列使用。

```java
BlockingQueue<Task> queue = new LinkedBlockingQueue<>(100);
ExecutorService workers = Executors.newFixedThreadPool(4);

while (true) {
    Task task = queue.take();  // 阻塞等待
    task.execute();
}
```

### 10.3 Producer-Consumer

解耦生产者和消费者，BlockingQueue 是核心实现。

```java
BlockingQueue<Item> queue = new LinkedBlockingQueue<>(100);

// 生产者
new Thread(() -> {
    while (true) {
        Item item = produce();
        queue.put(item);
    }
}).start();

// 消费者
new Thread(() -> {
    while (true) {
        Item item = queue.take();
        consume(item);
    }
}).start();
```

### 10.4 Pipeline

流水线处理，每阶段可并行。

```java
BlockingQueue<Data> q1 = new LinkedBlockingQueue<>(50);
BlockingQueue<Data> q2 = new LinkedBlockingQueue<>(50);

// 阶段1：读取
startStage("Reader", () -> {
    while (true) q1.offer(readData());
});

// 阶段2：处理
startStage("Processor", () -> {
    while (true) q2.offer(process(q1.poll()));
});

// 阶段3：写入
startStage("Writer", () -> {
    while (true) writeData(q2.poll());
});
```

### 10.5 Actor 模型

每个 Actor 独占自己的状态，消息传递通信。Kotlin 可用 Channel + Coroutine 实现。

```kotlin
// 用 Channel 模拟 Actor
private val actor = GlobalScope.actor<String> {
    var state = 0
    channel.consumeEach { msg ->
        when (msg) {
            "inc" -> state++
            "get" -> println("State: $state")
        }
    }
}
```

---

## 11. 性能与反模式

### 11.1 常见性能问题

锁竞争激烈：CPU 使用率不高但线程都在阻塞。解决：减小锁粒度、读写分离、无锁算法。

线程过多：线程创建和上下文切换消耗大量 CPU。解决：使用线程池、合理配置核心线程数。

伪共享（False Sharing）：多线程访问不同变量但在同一缓存行（64字节），修改任意一个整个缓存行失效。解决：LongAdder 分段设计。

### 11.2 并发反模式

在锁内执行耗时操作：应该只锁快速操作，耗时操作放外面。

省略 finally 中的 unlock：必须用 finally 保证锁释放。

使用 Thread.sleep 等待条件：应该用 wait/notify 或 Condition。

混淆线程和协程：在协程里用 Thread.sleep 阻塞线程，应该用 delay（挂起协程）。

```kotlin
// 错误
suspend fun wrong() {
    Thread.sleep(1000)  // 阻塞协程所在线程！
}

// 正确
suspend fun right() {
    delay(1000)  // 挂起协程，线程可以执行其他协程
}
```

---

## 12. 面试高频问题

**Q1: synchronized 和 Lock 的区别？**

synchronized 是 JVM 内置关键字，自动释放锁，不可中断不可超时不可公平锁；Lock 是 JUC 接口，支持中断、超时、公平锁，必须手动 unlock。

**Q2: volatile 和 synchronized 的区别？**

volatile 只保证可见性和有序性，不保证原子性；synchronized 保证原子性、可见性、有序性。

**Q3: 线程池的核心参数？**

corePoolSize、maximumPoolSize、keepAliveTime、unit、workQueue、threadFactory、handler。

**Q4: 线程池执行流程？**

线程数 < corePoolSize → 创建核心线程；队列满 → 创建非核心线程；达 maxPoolSize → 拒绝策略。

**Q5: ConcurrentHashMap 如何实现线程安全？**

JDK 7 分段锁；JDK 8+ 用 CAS + synchronized，锁粒度细化到单个桶。

**Q6: 什么是 CAS？有什么问题？**

Compare-And-Swap，硬件级原子操作。问题：ABA 问题（用 AtomicStampedReference）、自旋开销、只能保证单变量原子性。

**Q7: Coroutine 和线程的区别？**

协程是用户态调度，切换开销极小，挂起不阻塞线程；线程由 OS 调度，上下文切换开销大。

**Q8: 如何避免死锁？**

避免嵌套锁、按固定顺序获取锁、使用带超时的锁、减少锁持有时间、用 tryLock() 探测。

**Q9: 生产者-消费者如何实现？**

用 BlockingQueue：put() 满则阻塞，take() 空则阻塞。

**Q10: 什么是线程安全？如何实现？**

多线程访问时始终表现正确。实现方式：synchronized、Lock、volatile（单变量）、原子变量、并发容器、不可变对象、ThreadLocal。

---

## 总结

```
知识图谱：

基础层：Thread/Runnable/Callable → 线程创建
同步层：synchronized/volatile/Lock/Condition/ReadWriteLock/StampedLock
工具层：CountDownLatch/CyclicBarrier/Semaphore/Phaser
原子层：AtomicInteger/AtomicReference/LongAdder/CAS
容器层：ConcurrentHashMap/CopyOnWriteArrayList/BlockingQueue/ThreadLocalMap
线程池：ThreadPoolExecutor/Executors/饱和策略
协程层：Dispatchers/suspend/Scope/Flow/Channel
Android 层：主线程职责/Binder线程池/Process优先级
```

掌握以上内容，就具备了扎实的 Android 并发编程能力。

---

*文档更新时间: 2026-03-24*
