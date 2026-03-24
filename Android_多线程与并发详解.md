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
   - 8.2 [协程调度器 Dispatchers](#82-协程调度器-dispatchers)
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

多线程与并发是 Android 开发中最核心的能力之一，也是面试的重点难点。现代 Android 开发虽然已经进入 **Kotlin 协程时代**，但理解底层原理、掌握 Java 并发工具类，对于写出高效正确的并发代码至关重要。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 并发知识体系                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │                           Java 并发基础                                  │
  │     ┌──────────┬──────────┬──────────┬──────────┬──────────┐         │
  │     │  Thread  │ Synchronized│  Lock   │  volatile │ CAS/Atomics│      │
  │     └──────────┴──────────┴──────────┴──────────┴──────────┘         │
  │                                                                         │
  │     ┌──────────┬──────────┬──────────┬──────────┬──────────┐         │
  │     │ CountDown │ Cyclic   │ Sema-    │ Phaser   │Exchanger │         │
  │     │  Latch    │ Barrier  │  phore   │          │          │         │
  │     └──────────┴──────────┴──────────┴──────────┴──────────┘         │
  │                                                                         │
  │                           并发集合                                       │
  │     ┌──────────┬──────────┬──────────┬──────────┐                    │
  │     │Concurrent │ CopyOn   │ Blocking │Concurrent │                    │
  │     │HashMap    │WriteList │ Queue    │LinkedQueue│                    │
  │     └──────────┴──────────┴──────────┴──────────┘                    │
  │                                                                         │
  │                           线程池                                         │
  │     ┌──────────────────────────────────────────────┐                  │
  │     │           ThreadPoolExecutor                  │                  │
  │     │  corePoolSize / maxPoolSize / queue / policy │                  │
  │     └──────────────────────────────────────────────┘                  │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │                         Kotlin 协程（现代方案）                          │
  │     ┌──────────┬──────────┬──────────┬──────────┐                    │
  │     │Dispatchers│  suspend │   Flow   │ Channel  │                    │
  │     │  .IO/.Default/.Main│ 原理    │          │                    │
  │     └──────────┴──────────┴──────────┴──────────┘                    │
  │                                                                         │
  │     ┌──────────┬──────────┬──────────┬──────────┐                    │
  │     │  Scope   │  Context │ Coroutine │Exception │                    │
  │     │  作用域   │  上下文   │  构建器   │  处理   │                    │
  │     └──────────┴──────────┴──────────┴──────────┘                    │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Java 线程基础

### 2.1 Thread 创建与启动

```java
/**
 * 创建线程的 3 种方式
 */

// 方式1：继承 Thread
class MyThread extends Thread {
    @Override
    public void run() {
        // 业务逻辑
    }
}
new MyThread().start();  // 注意是 start()，不是 run()

// 方式2：实现 Runnable（推荐，Java 单继承限制）
class MyRunnable implements Runnable {
    @Override
    public void run() {
        // 业务逻辑
    }
}
new Thread(new MyRunnable()).start();

// 方式3：实现 Callable（有返回值，可抛异常）
class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        return "result";
    }
}
FutureTask<String> task = new FutureTask<>(new MyCallable());
new Thread(task).start();
String result = task.get();  // 阻塞等待结果

// 方式4：Lambda 简化（实际开发中最常用）
new Thread(() -> {
    // 业务逻辑
}).start();
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         start() vs run()                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  start():
  - 创建新线程
  - 调用 run() 在新线程执行
  - 只能调用一次

  run():
  - 普通方法调用
  - 在当前线程执行
  - 可以调用多次
```

### 2.2 线程状态与生命周期

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         线程状态转换图                                       │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │     NEW         │
                              │  (创建，未运行)  │
                              └────────┬────────┘
                                       │ start()
                                       ▼
                              ┌─────────────────┐
                              │   RUNNABLE       │◄──────────────┐
                              │  (就绪/运行中)    │               │
                              └────────┬────────┘               │
                                       │                         │
                    ┌──────────────────┼──────────────────┐       │
                    │                  │                  │       │
              sleep()/          等待synchronized         I/O完成  │
              wait()/           获得锁                           │
              join()           继续运行 ◄───────────────────────┘
                    │                  │
                    ▼                  ▼
          ┌─────────────────┐  ┌─────────────────┐
          │   BLOCKED       │  │    WAITING      │
          │  (阻塞，等待锁)  │  │  (无限期等待)   │
          └────────┬────────┘  └────────┬────────┘
                   │                    │
                   │   获得锁           │ 被唤醒/timeout
                   │                    │
                   └────────┬───────────┘
                            ▼
                   ┌─────────────────┐
                   │ TIMED_WAITING    │
                   │  (限时等待)      │
                   └────────┬────────┘
                            │
                            │ timeout/被唤醒
                            ▼
                   ┌─────────────────┐
                   │   TERMINATED     │
                   │   (已终止)       │
                   └─────────────────┘

  状态说明：
  ─────────────────────────────────────────────────────────────────────────
  NEW          创建了线程对象，还未 start()
  RUNNABLE     正在 JVM 中执行，或者等待 CPU 时间片
  BLOCKED      等待获取监视器锁（synchronized）
  WAITING      调用 Object.wait() / Thread.join() / LockSupport.park()
  TIMED_WAITING 调用 sleep() / wait(timeout) / join(timeout) / parkNanos()
  TERMINATED   线程执行完毕
```

### 2.3 线程优先级

```java
/**
 * 线程优先级：1-10，默认为 5
 * 注意：优先级只是提示，不保证严格按优先级执行
 */
Thread thread = new Thread(() -> {
    // 任务
});
thread.setPriority(Thread.MAX_PRIORITY);   // 10
thread.setPriority(Thread.NORM_PRIORITY);  // 5
thread.setPriority(Thread.MIN_PRIORITY);   // 1

// Android 特有优先级（Process 类）
Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);  // 10，后台
Process.setThreadPriority(Process.THREAD_PRIORITY_FOREGROUND);  // -2，前台
Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO);       // -16，音频
```

### 2.4 守护线程

```java
/**
 * 守护线程（Daemon Thread）
 * 特点：当所有非守护线程结束时，JVM 自动退出，守护线程被强制终止
 * 用途：垃圾回收线程、日志刷新线程、缓存清理等
 */

// 设置为守护线程
Thread daemonThread = new Thread(() -> {
    while (true) {
        // 守护任务
    }
});
daemonThread.setDaemon(true);  // 必须在 start() 前设置
daemonThread.start();

// 主线程是非守护线程
public static void main(String[] args) {
    Thread worker = new Thread(() -> {
        while (true) {
            // 如果主线程结束，这个线程也会被强制终止
        }
    });
    worker.setDaemon(true);
    worker.start();
    
    // 主线程结束 → JVM 退出 → 守护线程被强制终止
}
```

---

## 3. 线程同步机制

### 3.1 synchronized

`synchronized` 是 Java 最基础的同步手段，管程实现，自动获取/释放锁。

```java
/**
 * synchronized 的 3 种用法
 */

// 1. 同步实例方法（锁对象是 this）
public synchronized void method() {
    // 原子操作
}

// 等价于
public void method() {
    synchronized (this) {
        // 原子操作
    }
}

// 2. 同步静态方法（锁对象是类对象 Class）
public static synchronized void staticMethod() {
    // 原子操作
}

// 等价于
public static void staticMethod() {
    synchronized (MyClass.class) {
        // 原子操作
    }
}

// 3. 同步代码块（锁对象是指定的任意对象）
public void method() {
    synchronized (lockObject) {  // 推荐用专门的对象，减少锁粒度
        // 原子操作
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         synchronized 特性                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  可重入性：
  ─────────────────────────────────────────────────────────────────────────
  synchronized 是可重入锁，同一个线程可以反复进入：
  
  synchronized void methodA() {
      methodB();  // 可以调用，因为是同一个线程
  }
  
  synchronized void methodB() {
      // 业务逻辑
  }

  可见性：
  ─────────────────────────────────────────────────────────────────────────
  synchronized 保证：
  1. 原子性：一组操作不可中断
  2. 可见性：锁释放前，对共享变量的修改对其他线程可见
  3. 有序性：防止指令重排序

  锁的升级（偏斜锁 → 轻量级锁 → 重量级锁）：
  ─────────────────────────────────────────────────────────────────────────
  无竞争 → 偏斜锁（CAS 设置）
  轻度竞争 → 轻量级锁（自旋）
  激烈竞争 → 重量级锁（阻塞）
```

### 3.2 volatile

```java
/**
 * volatile：轻量级同步，不加锁，只保证可见性和有序性
 */

// 典型用法：标志位
public class VolatileFlag {
    private volatile boolean running = true;
    
    public void stop() {
        running = false;  // 写入对所有线程立即可见
    }
    
    public void run() {
        while (running) {  // 读取总是看到最新值
            // 业务逻辑
        }
    }
}

// 多线程下 volatile 的必要性
class VolatileDemo {
    private volatile int count = 0;  // volatile 保证可见性，但不保证原子性
    
    public void increment() {
        count++;  // 非原子操作！需要 synchronized
    }
    
    public int getCount() {
        return count;  // volatile 保证读取最新值
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      synchronized vs volatile                               │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬──────────────────────────┬──────────────────────────┐
  │     特性        │       synchronized      │        volatile         │
  ├─────────────────┼──────────────────────────┼──────────────────────────┤
  │  原子性         │          ✓              │           ✗              │
  │  可见性         │          ✓              │           ✓              │
  │  有序性         │          ✓              │           ✓              │
  │  性能           │        较重              │          轻量             │
  │  可重入         │          ✓              │           ✗              │
  │  阻塞           │       会阻塞             │         不阻塞            │
  └─────────────────┴──────────────────────────┴──────────────────────────┘

  使用场景：
  ─────────────────────────────────────────────────────────────────────────
  volatile：boolean 标志位、单次读写
  synchronized：复合操作（i++）、需要原子性的代码块
```

### 3.3 wait/notify/notifyAll

```java
/**
 * Object 的等待通知机制，必须在 synchronized 内使用
 */
class ProducerConsumer {
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
            lock.notify();  // 通知生产者继续生产
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
            lock.notify();  // 通知消费者
        }
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    wait/notifyAll 经典模式                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  标准套路（必须用 while 不用 if）：
  ─────────────────────────────────────────────────────────────────────────

  synchronized (obj) {
      while (条件不满足) {
          obj.wait();  // 虚假唤醒：用 while 循环防止
      }
      // 业务逻辑
  }

  生产者：
  synchronized (queue) {
      while (queue.isFull()) {
          queue.wait();
      }
      queue.add(item);
      queue.notifyAll();  // 用 notifyAll 不用 notify（防止死锁）
  }

  消费者：
  synchronized (queue) {
      while (queue.isEmpty()) {
          queue.wait();
      }
      queue.remove();
      queue.notifyAll();
  }
```

### 3.4 Lock 与 ReentrantLock

```java
/**
 * ReentrantLock：可重入锁，比 synchronized 更灵活
 */
class LockDemo {
    private final ReentrantLock lock = new ReentrantLock();
    
    public void method() {
        lock.lock();         // 获取锁
        try {
            // 业务逻辑
        } finally {
            lock.unlock();   // 必须在 finally 释放
        }
    }
    
    // 尝试获取锁（非阻塞）
    public void tryLockDemo() {
        if (lock.tryLock()) {  // 尝试获取，成功返回 true
            try {
                // 业务逻辑
            } finally {
                lock.unlock();
            }
        } else {
            // 获取失败，走其他逻辑
        }
    }
    
    // 带超时的尝试获取
    public void tryLockWithTimeout() throws InterruptedException {
        if (lock.tryLock(5, TimeUnit.SECONDS)) {
            try {
                // 业务逻辑
            } finally {
                lock.unlock();
            }
        }
    }
    
    // 公平锁（按等待顺序获取）
    ReentrantLock fairLock = new ReentrantLock(true);  // 公平锁，稍有性能损失
    
    // 可中断获取
    public void lockInterruptibly() throws InterruptedException {
        lock.lockInterruptibly();  // 可被中断的获取
        try {
            // 业务逻辑
        } finally {
            lock.unlock();
        }
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    synchronized vs ReentrantLock                            │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬──────────────────────────┬──────────────────────────┐
  │     特性        │       synchronized      │     ReentrantLock       │
  ├─────────────────┼──────────────────────────┼──────────────────────────┤
  │  响应中断       │          ✗              │           ✓              │
  │  尝试获取       │          ✗              │           ✓              │
  │  超时获取       │          ✗              │           ✓              │
  │  公平锁         │          ✗              │           ✓              │
  │  多条件         │          ✗              │           ✓              │
  │  粒度           │    块级别               │    更灵活                │
  │  自动释放       │          ✓              │           ✗              │
  │  性能           │      优化后相近          │                          │
  └─────────────────┴──────────────────────────┴──────────────────────────┘

  选择建议：
  ─────────────────────────────────────────────────────────────────────────
  简单同步 → synchronized
  需要高级特性（中断、超时、公平）→ ReentrantLock
  需要多个条件变量 → ReentrantLock + Condition
```

### 3.5 ReadWriteLock

```java
/**
 * ReadWriteLock：读写分离锁
 * 读操作可以并发，写操作需要独占
 */
class Cache<K, V> {
    private final Map<K, V> cache = new HashMap<>();
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
    
    // 注意：写锁后不能获取读锁（读写不互斥）
    // 但 ReentrantReadWriteLock 允许从写锁降级为读锁：
    public V writeThenRead(K key, V value) {
        rwLock.writeLock().lock();
        try {
            cache.put(key, value);
            // 锁降级：释放写锁前获取读锁
            rwLock.readLock().lock();  // 同一个线程，写锁→读锁可重入
            try {
                return cache.get(key);
            } finally {
                rwLock.readLock().unlock();  // 先释放读锁
            }
        } finally {
            rwLock.writeLock().unlock();  // 最后释放写锁
        }
    }
}
```

### 3.6 Condition

```java
/**
 * Condition：多线程精确等待/通知，比 wait/notify 更强大
 */
class BoundedBuffer<T> {
    private final Object[] items;
    private int count, takeIndex, putIndex;
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notEmpty = lock.newCondition();  // 队列非空
    private final Condition notFull = lock.newCondition();   // 队列非满
    
    public BoundedBuffer(int capacity) {
        items = new Object[capacity];
    }
    
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
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Object.wait/notify vs Condition                         │
└─────────────────────────────────────────────────────────────────────────────┘

  Object.wait/notify:
  - 只有一个条件队列
  - 容易产生虚假唤醒
  - 无法精确控制

  Condition:
  - 多个独立条件队列（notEmpty、notFull）
  - 必须和 ReentrantLock 配合
  - 更灵活，更清晰
  - 支持中断和超时
```

### 3.7 StampedLock

```java
/**
 * StampedLock：比 ReadWriteLock 更进一步的乐观读
 * 三种模式：写、读、乐观读
 */
class Point {
    private double x, y;
    private final StampedLock sl = new StampedLock();
    
    // 写锁（独占）
    public void move(double deltaX, double deltaY) {
        long stamp = sl.writeLock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            sl.unlockWrite(stamp);
        }
    }
    
    // 悲观读（和 WriteLock 互斥）
    public double distanceFromOrigin() {
        long stamp = sl.readLock();
        try {
            return Math.sqrt(x * x + y * y);
        } finally {
            sl.unlockRead(stamp);
        }
    }
    
    // 乐观读（不阻塞，写入少时性能最好）
    public double optimisticDistance() {
        long stamp = sl.tryOptimisticRead();  // 获取乐观读戳
        double currentX = x;  // 读取变量（非原子，视为快照）
        double currentY = y;
        
        // 检查戳是否有效（中间是否有写操作）
        if (!sl.validate(stamp)) {
            // 有写操作，升级为悲观读
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
}
```

---

## 4. Java 并发工具类

### 4.1 CountDownLatch

```java
/**
 * CountDownLatch：倒数计数器，等待一组线程完成
 * 场景：主线程等待多个子线程执行完毕
 */
class GameServer {
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

### 4.2 CyclicBarrier

```java
/**
 * CyclicBarrier：循环栅栏，让一组线程互相等待，到达某点后一起恢复执行
 * 场景：多线程分阶段计算，每阶段需全部完成
 */
class MatrixSolver {
    public double[][] solve(double[][] matrix) {
        int n = matrix.length;
        double[][] result = new double[n][n];
        
        // 分 3 个阶段：行归一化 → 列归一化 → 对角化
        CyclicBarrier barrier = new CyclicBarrier(n, () -> {
            System.out.println("Phase completed, moving to next...");
        });
        
        for (int i = 0; i < n; i++) {
            final int row = i;
            new Thread(() -> {
                try {
                    // 阶段1：行归一化
                    normalizeRow(result, row);
                    barrier.await();
                    
                    // 阶段2：列归一化
                    normalizeCol(result, row);
                    barrier.await();
                    
                    // 阶段3：对角化
                    normalizeDiag(result, row);
                    barrier.await();
                    
                } catch (InterruptedException | BrokenBarrierException e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }
        return result;
    }
    
    private void normalizeRow(double[][] m, int row) { }
    private void normalizeCol(double[][] m, int col) { }
    private void normalizeDiag(double[][] m, int diag) { }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CountDownLatch vs CyclicBarrier                         │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬──────────────────────────┬──────────────────────────┐
  │     特性        │     CountDownLatch       │    CyclicBarrier         │
  ├─────────────────┼──────────────────────────┼──────────────────────────┤
  │  用途           │  一组线程等待某个事件    │  一组线程互相等待        │
  │  重置           │  不能重置                │  可重置（Cyclic）        │
  │  计数方向       │  倒减（countDown）       │  正加（await）           │
  │  典型场景       │  "等 N 个线程完成后..."  │  "N 个线程都到达后..."   │
  └─────────────────┴──────────────────────────┴──────────────────────────┘
```

### 4.3 Semaphore

```java
/**
 * Semaphore：信号量，控制同时访问某资源的线程数量
 * 场景：连接池、令牌桶、限流
 */
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
            return null;  // 不应该走到这里
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

### 4.4 Exchanger

```java
/**
 * Exchanger：两个线程交换数据
 * 场景：生产者-消费者之间的数据交换
 */
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
            fullBuffer.clear();    // 清空，准备交换回去
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

```java
/**
 * Phaser：多阶段同步器，比 CyclicBarrier 更灵活
 * 场景：多阶段任务，每阶段完成后汇合
 */
class PhaserDemo {
    public void execute() throws InterruptedException {
        Phaser phaser = new Phaser(3);  // 3 个参与线程
        
        // 阶段1：初始化
        for (int i = 0; i < 3; i++) {
            final int threadId = i;
            new Thread(() -> {
                System.out.println("Phase 0: Thread " + threadId + " initializing");
                phaser.arriveAndAwaitAdvance();  // 等待其他线程完成阶段0
                
                // 阶段2：执行
                System.out.println("Phase 1: Thread " + threadId + " executing");
                phaser.arriveAndAwaitAdvance();  // 等待其他线程完成阶段1
                
                // 阶段3：收尾
                System.out.println("Phase 2: Thread " + threadId + " finalizing");
                phaser.arriveAndAwaitAdvance();
            }).start();
        }
        
        phaser.awaitAdvance(phaser.getPhase());  // 主线程等待所有阶段完成
        System.out.println("All phases completed");
    }
}
```

---

## 5. 原子类与 CAS

### 5.1 AtomicInteger/AtomicLong

```java
/**
 * 原子整数，比 synchronized 更轻量
 */
class Counter {
    private final AtomicInteger count = new AtomicInteger(0);
    
    // 无锁 increment
    public void increment() {
        count.incrementAndGet();  // i++
    }
    
    // 先获取再加
    public int getAndIncrement() {
        return count.getAndIncrement();  // 返回旧值
    }
    
    // 原子 CAS
    public boolean compareAndSet(int expected, int newValue) {
        return count.compareAndSet(expected, newValue);
    }
    
    // 原子更新（lambda）
    public void incrementBy(int delta) {
        count.updateAndGet(current -> current + delta);
    }
}
```

### 5.2 AtomicReference

```java
/**
 * 原子引用：无锁实现对象的原子更新
 */
class AtomicStack<T> {
    private final AtomicReference<Node<T>> top = new AtomicReference<>();
    
    public void push(T item) {
        Node<T> newHead = new Node<>(item);
        Node<T> oldHead;
        do {
            oldHead = top.get();
            newHead.next = oldHead;
        } while (!top.compareAndSet(oldHead, newHead));  // CAS 直到成功
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

### 5.3 AtomicIntegerFieldUpdater

```java
/**
 * AtomicIntegerFieldUpdater：对普通字段的原子更新（节省内存）
 * 场景：大量对象需要原子更新同一字段
 */
class Student {
    private volatile int score;  // 必须是 volatile
    // 不能是 private，否则需要 setAccessible(true)
}

class ScoreTracker {
    private final AtomicIntegerFieldUpdater<Student> scoreUpdater = 
        AtomicIntegerFieldUpdater.newUpdater(Student.class, "score");
    
    public void incrementScore(Student student) {
        scoreUpdater.incrementAndGet(student);
    }
    
    public void addScore(Student student, int delta) {
        scoreUpdater.addAndGet(student, delta);
    }
}
```

### 5.4 LongAdder（高并发场景）

```java
/**
 * LongAdder：高并发计数器，比 AtomicLong 性能更好
 * 原理：热点数据分段，多个累加单元竞争
 */
class Analytics {
    private final LongAdder totalClicks = new LongAdder();
    private final LongAdder totalViews = new LongAdder();
    
    public void recordClick() {
        totalClicks.increment();  // 比 AtomicLong.increment() 快很多
    }
    
    public void recordView() {
        totalViews.increment();
    }
    
    public long getTotalClicks() {
        return totalClicks.sum();
    }
    
    // LongAccumulator：更通用的累加器
    private final LongAccumulator maxScore = new LongAccumulator(
        Long::max,  // 累加规则
        0           // 初始值
    );
    
    public void recordScore(long score) {
        maxScore.accumulate(score);  // 记录最大值
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AtomicLong vs LongAdder                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  AtomicLong：
  - CAS 自旋，竞争激烈时性能急剧下降
  - 每次更新都需要循环重试

  LongAdder：
  - 分段思想（类似 ConcurrentHashMap 的分段锁）
  - 热点分段，多线程更新不同单元
  - sum() 时汇总所有单元
  - 写多读少时性能好

  选择：
  - 并发度低（< 1000线程）→ AtomicLong
  - 并发度高、写多读少 → LongAdder
  - 需要减法/其他操作 → LongAccumulator
```

### 5.5 CAS 原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAS (Compare-And-Swap) 原理                          │
└─────────────────────────────────────────────────────────────────────────────┘

  CAS 操作：
  ─────────────────────────────────────────────────────────────────────────
  三个操作数：内存位置(V)、预期原值(A)、新值(B)
  如果 V == A，将 V 设为 B，返回 true
  否则什么都不做，返回 false

  伪代码：
  boolean compareAndSwap(Object V, Object A, Object B) {
      if (V == A) {
          V = B;
          return true;
      }
      return false;
  }

  CPU 指令支持：
  ─────────────────────────────────────────────────────────────────────────
  Java 的 CAS 由 CPU 的 CAS 指令支持（cmpxchg / lock cmpxchg）
  是硬件级别的原子操作

  Java 实现：
  ─────────────────────────────────────────────────────────────────────────
  public final int incrementAndGet() {
      return unsafe.getAndAddInt(this, valueOffset, 1) + 1;
  }

  // Unsafe 类中的实现：
  public final int getAndAddInt(Object o, long offset, int delta) {
      int expected;
      do {
          expected = getIntVolatile(o, offset);  // 读取当前值
      } while (!compareAndSwapInt(o, offset, expected, expected + delta));
      // CAS 失败则重试，直到成功
      return expected;
  }

  ABA 问题：
  ─────────────────────────────────────────────────────────────────────────
  线程1: 读取 A
  线程2: 把 A 改成 B，又把 B 改成 A
  线程1: CAS 成功（值还是 A），但实际上已被修改过

  解决方案：版本号（AtomicStampedReference）
  AtomicStampedReference<Integer> ref = new AtomicStampedReference<>(100, 1);
  ref.compareAndSet(100, 200, stamp, stamp + 1);  // 同时比较版本号

---

## 6. 并发集合

### 6.1 ConcurrentHashMap

```java
/**
 * ConcurrentHashMap：高性能并发哈希映射
 * 原理：JDK 8 前分段锁，JDK 8 后 CAS + synchronized
 */
class MapDemo {
    private final ConcurrentHashMap<String, Object> map = 
        new ConcurrentHashMap<>();
    
    public void operations() {
        // 基本操作（线程安全）
        map.put("key", "value");
        map.get("key");
        
        // 原子操作（JDK 8+）
        map.putIfAbsent("key", "newValue");  // 不存在才插入
        map.remove("key", "expectedValue");  // 值匹配才删除
        map.replace("key", "oldValue", "newValue");  // 值匹配才替换
        
        // 批量操作
        map.forEach(1, (k, v) -> System.out.println(k + ":" + v));  // 并行遍历
        map.search(1, (k, v) -> k.startsWith("a") ? k : null);     // 并行搜索
        map.reduce(1, (k, v) -> v.toString().length(), 
                   Integer::sum);  // 并行聚合
        
        // compute 原子更新
        map.compute("counter", (k, v) -> 
            v == null ? "1" : String.valueOf(Integer.parseInt(v) + 1));
        
        // 计数（LongAdder 优化）
        map.merge("hits", 1L, Long::sum);
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ConcurrentHashMap vs Hashtable/synchronizedMap            │
└─────────────────────────────────────────────────────────────────────────────┘

  Hashtable/synchronizedMap：
  - 全局锁，所有操作串行化
  - 并发读也必须竞争锁

  ConcurrentHashMap：
  - 分段锁（JDK 7）或 CAS + synchronized（JDK 8）
  - 读操作大部分无锁（volatile 读取）
  - 写操作锁粒度小
  - 性能远优于 Hashtable

  JDK 8+ 优化：
  - 读：volatile 读，无锁
  - 写：CAS + synchronized（小部分冲突时用）
  - 链表 → 红黑树（桶内元素 > 8）
  - 红黑树旋转时锁头节点
```

### 6.2 CopyOnWriteArrayList

```java
/**
 * CopyOnWriteArrayList：写时复制列表
 * 读操作无锁，写操作复制全量数组
 * 场景：读多写少的并发场景
 */
class ReadHeavyList<T> {
    private final CopyOnWriteArrayList<T> list = new CopyOnWriteArrayList<>();
    
    // 读操作（无锁，极快）
    public T get(int index) {
        return list.get(index);  // 无锁，读取快照
    }
    
    public boolean contains(T item) {
        return list.contains(item);
    }
    
    // 遍历（安全，无需锁，写操作不影响读者）
    public void forEach(Consumer<T> action) {
        list.forEach(action);  // 遍历的是快照
    }
    
    // 写操作（复制全量，耗资源）
    public void add(T item) {
        list.add(item);  // 复制整个数组
    }
    
    public void remove(T item) {
        list.remove(item);  // 复制整个数组
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CopyOnWriteArrayList 特点                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  优点：
  - 读操作完全无锁，无阻塞
  - 遍历和读可以完全并发
  - 写不影响正在遍历的读者

  缺点：
  - 每次写都复制整个数组，内存开销大
  - 写操作频繁时性能急剧下降
  - 不能保证实时性（读者读到的是旧快照）

  适用场景：
  - 读远多于写（95% 读，5% 写）
  - 不需要实时数据（如缓存、配置）
  - 遍历操作远多于修改操作

  不适用：
  - 写操作频繁
  - 需要实时数据
  - 内存敏感
```

### 6.3 BlockingQueue

```java
/**
 * BlockingQueue：阻塞队列，生产者-消费者模式核心
 */
class ProducerConsumerDemo {
    
    public void demo() throws InterruptedException {
        BlockingQueue<String> queue = new LinkedBlockingQueue<>(10);
        
        // 生产者
        Thread producer = new Thread(() -> {
            try {
                while (true) {
                    String data = produceData();
                    queue.put(data);  // 队列满则阻塞
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        // 消费者
        Thread consumer = new Thread(() -> {
            try {
                while (true) {
                    String data = queue.take();  // 队列空则阻塞
                    process(data);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        producer.start();
        consumer.start();
    }
    
    // BlockingQueue 方法对照表
    public void blockingQueueMethods() throws InterruptedException {
        BlockingQueue<String> q = new LinkedBlockingQueue<>(3);
        
        // 抛异常组
        q.add("x");        // 满则 IllegalStateException
        q.remove();        // 空则 NoSuchElementException
        q.element();       // 空则 NoSuchElementException
        
        // 返回特殊值组
        q.offer("x");     // 满则 false
        q.poll();          // 空则 null
        q.peek();          // 空则 null
        
        // 阻塞组
        q.put("x");        // 满则一直阻塞
        q.take();          // 空则一直阻塞
        
        // 超时组
        q.offer("x", 5, TimeUnit.SECONDS);  // 满则等5秒，超时返回false
        q.poll(5, TimeUnit.SECONDS);         // 空则等5秒，超时返回null
    }
    
    // 常用实现
    public void implementations() {
        // 无界队列（自动扩容）
        BlockingQueue<E> unbounded = new LinkedBlockingQueue<>();
        
        // 有界队列
        BlockingQueue<E> bounded = new LinkedBlockingQueue<>(100);
        
        // 数组实现，性能更好
        BlockingQueue<E> arrayQueue = new ArrayBlockingQueue<>(100);
        
        // 同步队列（不存储，直接交接）
        BlockingQueue<E> syncQueue = new SynchronousQueue<>();
        
        // 优先队列
        BlockingQueue<E> priorityQueue = new PriorityBlockingQueue<>();
        
        // 延迟队列
        BlockingQueue<E> delayQueue = new DelayQueue<>();
    }
    
    private String produceData() { return ""; }
    private void process(String data) { }
}
```

### 6.4 ConcurrentLinkedQueue/Deque

```java
/**
 * ConcurrentLinkedQueue：无界非阻塞队列
 * ConcurrentLinkedDeque：双端队列
 */
class NonBlockingDemo {
    private final ConcurrentLinkedQueue<Task> queue = 
        new ConcurrentLinkedQueue<>();
    
    public void operations() {
        queue.offer(new Task());     // 入队
        Task t = queue.poll();       // 出队（无则 null）
        Task peek = queue.peek();    // 窥视（无则 null）
        
        // 无界，不会阻塞
        // 适合真正高并发的无界场景
    }
    
    // ConcurrentLinkedDeque：双端操作
    private final ConcurrentLinkedDeque<Task> deque = 
        new ConcurrentLinkedDeque<>();
    
    public void dequeOperations() {
        deque.addFirst(task);   // 头插
        deque.addLast(task);     // 尾插
        deque.pollFirst();       // 头出
        deque.pollLast();        // 尾出
    }
}
```

### 6.5 ThreadLocalMap

```java
/**
 * ThreadLocalMap：ThreadLocal 的内部实现
 * 弱引用 key，防止内存泄漏（但 value 仍需注意）
 */
class ThreadLocalDemo {
    // 每个线程独立的变量
    private final ThreadLocal<String> threadLocal = 
        ThreadLocal.withInitial(() -> "default");
    
    private final ThreadLocal<Map<String, Object>> threadLocalMap = 
        ThreadLocal.withInitial(HashMap::new);
    
    public void operations() {
        // 设置（只对当前线程可见）
        threadLocal.set("value");
        
        // 获取（只返回当前线程设置的值）
        String value = threadLocal.get();
        
        // 移除（防止内存泄漏）
        threadLocal.remove();
        
        // threadLocalMap 使用弱引用 key
        // 好处：ThreadLocal 对象无强引用时，可被 GC 回收
        // 坏处：value 可能泄漏（如果不再调用 get/set）
        
        // Android Handler 内存泄漏的根源之一：
        // Handler 持有 Activity 引用 → Activity 无法 GC
        // 但 Handler 是在子线程的 threadLocalMap 中... 复杂
    }
}

// 内存泄漏的场景
class LeakExample {
    private final ThreadLocal<byte[]> largeData = new ThreadLocal<>();
    
    public void wrongUsage() {
        // 如果在线程池中使用，线程复用
        ExecutorService executor = Executors.newFixedThreadPool(2);
        
        executor.submit(() -> {
            largeData.set(new byte[1024 * 1024 * 10]);  // 10MB
            
            // 业务逻辑
            // 线程归还时，largeData.value 仍在 threadLocalMap 中
            // 如果不 remove()，内存泄漏
        });
    }
    
    public void correctUsage() {
        ExecutorService executor = Executors.newFixedThreadPool(2);
        
        executor.submit(() -> {
            try {
                largeData.set(new byte[1024 * 1024 * 10]);
                // 业务逻辑
            } finally {
                largeData.remove();  // 清理
            }
        });
    }
}

---

## 7. 线程池

### 7.1 ThreadPoolExecutor 核心参数

```java
/**
 * ThreadPoolExecutor 构造函数参数详解
 */
class ThreadPoolConfig {
    
    public ThreadPoolExecutor createPool() {
        return new ThreadPoolExecutor(
            int corePoolSize,        // 核心线程数
            int maximumPoolSize,      // 最大线程数
            long keepAliveTime,       // 空闲线程存活时间
            TimeUnit unit,            // 时间单位
            BlockingQueue<Runnable> workQueue,    // 任务队列
            ThreadFactory threadFactory,           // 线程工厂
            RejectedExecutionHandler handler       // 拒绝策略
        );
    }
}

// 核心参数详解：
//
// corePoolSize：核心线程数
//   - 即使空闲也不回收的线程数
//   - allowCoreThreadTimeOut=true 时可被回收
//
// maximumPoolSize：最大线程数
//   - 队列满后，允许创建的最大线程数
//   - corePoolSize <= maxPoolSize
//
// keepAliveTime：非核心线程空闲存活时间
//   - 超过这个时间的非核心线程会被回收
//   - allowCoreThreadTimeOut=true 时核心线程也会被回收
//
// unit：keepAliveTime 的时间单位
//
// workQueue：任务队列
//   - LinkedBlockingQueue：无界队列（注意 OOM）
//   - ArrayBlockingQueue：有界队列
//   - SynchronousQueue：直接交接队列
//   - PriorityBlockingQueue：优先级队列
//
// threadFactory：线程工厂
//   - 创建线程，可设置名字、是否为守护线程、优先级等
//
// handler：拒绝策略（队列满+线程数达最大值时）
//   - AbortPolicy：抛 RejectedExecutionException（默认）
//   - CallerRunsPolicy：用调用者线程执行
//   - DiscardPolicy：丢弃任务
//   - DiscardOldestPolicy：丢弃最老的任务
```

### 7.2 线程池执行流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ThreadPoolExecutor 执行流程                               │
└─────────────────────────────────────────────────────────────────────────────┘

  提交任务：execute(Runnable command)

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ① 线程数 < corePoolSize？                                              │
  │     是 ──► 创建核心线程，执行任务                                        │
  │     否 ──► ②                                                            │
  │                                                                         │
  │  ② 队列未满？                                                          │
  │     是 ──► 任务入队等待                                                  │
  │     否 ──► ③                                                            │
  │                                                                         │
  │  ③ 线程数 < maximumPoolSize？                                          │
  │     是 ──► 创建非核心线程，执行任务                                      │
  │     否 ──► ④                                                            │
  │                                                                         │
  │  ④ 执行拒绝策略                                                        │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  示例：
  ThreadPoolExecutor pool = new ThreadPoolExecutor(
      4,    // corePoolSize
      8,    // maximumPoolSize
      60L,  // keepAliveTime
      TimeUnit.SECONDS,
      new LinkedBlockingQueue<>(100)  // 队列容量 100
  );

  任务数 = 1000 的执行过程：
  1. 前 4 个任务 → 4 个核心线程执行
  2. 4-104 个任务 → 入队列（100个）
  3. 105-108 个任务 → 创建非核心线程执行（4个）
  4. 109+ 个任务 → 触发拒绝策略
```

### 7.3 线程池分类

```java
/**
 * Executors 提供的线程池工厂
 */
class ThreadPoolTypes {
    
    // 1. 固定大小线程池（无界队列）
    public void fixedThreadPool() {
        ExecutorService pool = Executors.newFixedThreadPool(4);
        // corePoolSize = maxPoolSize = n
        // 任务全部入队列，队列无界
        // 风险：任务过多时，队列无限增长，可能 OOM
    }
    
    // 2. 缓存线程池（按需创建）
    public void cachedThreadPool() {
        ExecutorService pool = Executors.newCachedThreadPool();
        // corePoolSize = 0
        // maxPoolSize = Integer.MAX_VALUE
        // 60秒回收
        // 适合短时异步任务，但可能导致线程爆炸
    }
    
    // 3. 单线程池
    public void singleThreadPool() {
        ExecutorService pool = Executors.newSingleThreadExecutor();
        // corePoolSize = maxPoolSize = 1
        // 保证任务顺序执行
        // 内部用 LinkedBlockingQueue
    }
    
    // 4. 定时任务线程池
    public void scheduledThreadPool() {
        ScheduledExecutorService pool = 
            Executors.newScheduledThreadPool(4);
        
        pool.schedule(task, 3, TimeUnit.SECONDS);        // 延迟3秒执行
        pool.scheduleAtFixedRate(task, 1, 5, TimeUnit.SECONDS);  // 固定周期
        pool.scheduleWithFixedDelay(task, 1, 5, TimeUnit.SECONDS);  // 固定间隔
    }
    
    // 5. 工作窃取线程池
    public void workStealingPool() {
        ExecutorService pool = Executors.newWorkStealingPool(4);
        // ForkJoinPool 实现
        // 空闲线程从其他线程队列"偷"任务
        // 适合大量小任务的并行计算
    }
    
    // 6. 自定义线程池（推荐，明确参数）
    public void customPool() {
        ThreadPoolExecutor pool = new ThreadPoolExecutor(
            4,                                      // corePoolSize
            8,                                      // maxPoolSize
            60L,                                    // keepAliveTime
            TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(200),         // 有界队列
            new ThreadFactory() {                   // 自定义线程工厂
                private int count = 0;
                @Override
                public Thread newThread(Runnable r) {
                    Thread t = new Thread(r);
                    t.setName("MyPool-Worker-" + count++);
                    t.setPriority(Thread.NORM_PRIORITY);
                    return t;
                }
            },
            new ThreadPoolExecutor.CallerRunsPolicy()  // 拒绝策略：调用者执行
        );
    }
}
```

### 7.4 线程池饱和策略

```java
/**
 * 拒绝策略详解
 */
class RejectedPolicies {
    
    // 1. AbortPolicy（默认）：抛异常
    // new ThreadPoolExecutor.AbortPolicy()
    // 任务被拒绝时抛 RejectedExecutionException
    
    // 2. CallerRunsPolicy：用调用者线程执行
    // new ThreadPoolExecutor.CallerRunsPolicy()
    // 任务被拒绝时，由提交任务的线程执行
    // 优点：防止任务丢失，且有减速效果
    // 缺点：提交任务的线程被阻塞
    
    // 3. DiscardPolicy：丢弃任务
    // new ThreadPoolExecutor.DiscardPolicy()
    // 静默丢弃，不抛异常
    
    // 4. DiscardOldestPolicy：丢弃最老的任务
    // new ThreadPoolExecutor.DiscardOldestPolicy()
    // 丢弃队列中最老的任务，然后重试被拒绝的任务
    
    // 实际场景选择：
    public void choosePolicy() {
        // 高优先级任务不能用 DiscardOldestPolicy
        // CallerRunsPolicy 适合任务可以减速处理的场景
        // 高并发场景慎用无界队列 + 固定线程池
    }
}
```

### 7.5 线程池参数配置

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    线程池参数配置公式                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  CPU 密集型任务：
  ─────────────────────────────────────────────────────────────────────────
  线程数 = CPU 核心数 + 1
  
  CPU核心数 = Runtime.getRuntime().availableProcessors()

  IO 密集型任务：
  ─────────────────────────────────────────────────────────────────────────
  线程数 = CPU 核心数 × (1 + 等待时间 / 计算时间)

  混合型任务：
  ─────────────────────────────────────────────────────────────────────────
  线程数 = CPU 核心数 × CPU 利用率 × (1 + 等待时间 / 计算时间)

  实际配置建议：
  ─────────────────────────────────────────────────────────────────────────
  - 不要写死，用有界队列
  - 拒绝策略用 CallerRunsPolicy（防止任务丢失）
  - 监控队列大小和拒绝次数
  - 合理设置 keepAliveTime

  Android 主线程池（通常由系统管理）：
  - AsyncTask 的 SERIAL_EXECUTOR：串行执行
  - AsyncTask 的 THREAD_POOL_EXECUTOR：并发执行
  - IntentService：单线程 + Handler
  - Coroutines：默认 Dispatchers.Main

---

## 8. Kotlin 协程原理

### 8.1 协程是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         协程 vs 线程                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  线程：
  - 操作系统调度实体
  - 切换开销大（1-2KB 栈空间）
  - 竞争锁/上下文切换耗时

  协程：
  - 用户态调度实体（用户态线程）
  - 切换开销极小（状态机 + 栈帧）
  - 挂起/恢复，不阻塞线程
  - 单线程内可并发多个协程

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  线程模型（阻塞）：                                                      │
  │  Thread-1: [请求A(阻塞)][请求B(阻塞)][请求C(阻塞)]                      │
  │  Thread-2: 空闲...                                                      │
  │  3个线程同时跑                                                       │
  ├─────────────────────────────────────────────────────────────────────────┤
  │  协程模型（异步）：                                                     │
  │  Thread-1: [请求A(挂起)][请求B(挂起)][请求C]   ← 一个线程              │
  │  A挂起时，B可以运行。不用等A的IO返回                                   │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 协程调度器 Dispatchers

```kotlin
/**
 * 协程调度器
 */
class DispatchersDemo {
    
    fun dispatchers() {
        // 1. Main：主线程（UI线程）
        GlobalScope.launch(Dispatchers.Main) {
            // 更新 UI
            // 所有 Android 主线程操作
        }
        
        // 2. IO：IO 操作专用线程池（异步）
        GlobalScope.launch(Dispatchers.IO) {
            // 网络请求
            val data = api.fetch()
            // 文件读写
            val content = File("data.txt").readText()
            // 数据库操作
            db.query()
        }
        
        // 3. Default：CPU 密集型线程池（核心数线程）
        GlobalScope.launch(Dispatchers.Default) {
            // 排序、JSON解析、复杂计算
            val sorted = bigList.sorted()
            val result = processData(bigData)
        }
        
        // 4. Unconfined：不限制线程（不推荐）
        GlobalScope.launch(Dispatchers.Unconfined) {
            // 不指定线程，恢复时在哪个线程就在哪个
        }
        
        // 5. 单线程调度器（保证线程安全）
        val singleThread = Dispatchers.Default.limitedParallelism(1)
        GlobalScope.launch(singleThread) {
            // 所有协程在这个单线程执行
        }
    }
    
    // 线程池大小：
    // Dispatchers.IO：max(2, CPU核心数 * 2) 个线程
    // Dispatchers.Default：max(2, CPU核心数) 个线程
}
```

### 8.3 协程上下文与作用域

```kotlin
/**
 * 协程上下文与作用域
 */
class ScopeContextDemo {
    
    // 协程上下文：包含调度器、作业、拦截器等
    fun contextDemo() {
        val ctx = Dispatchers.Default + CoroutineName("MyCoroutine") + CoroutineExceptionHandler { _, e ->
            println("Error: $e")
        }
        
        GlobalScope.launch(ctx) {
            // 使用组合上下文
            println(coroutineContext[CoroutineName])
        }
    }
    
    // 协程作用域：管理协程生命周期
    fun scopeDemo(viewModel: ViewModel) {
        // viewModelScope：ViewModel 推荐，ViewModel 清除时自动取消
        viewModel.viewModelScope.launch {
            val data = repository.getData()
        }
        
        // lifecycleScope：Activity/Fragment 推荐
        lifecycleScope.launch {
            // Activity 销毁时自动取消
        }
        
        // 自定义作用域
        val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
        scope.launch {
            // 需要手动取消
        }
        scope.cancel()
    }
    
    // 结构化并发
    fun structuredConcurrency() {
        // 父协程取消，子协程全部取消
        // 子协程出错，默认取消父协程和所有兄弟协程
        // 所有子协程完成后，父协程才完成
        
        viewModelScope.launch {
            val user = async { fetchUser() }
            val posts = async { fetchPosts() }
            
            // 两个并发请求，都完成后才进入这里
            display(user.await(), posts.await())
        }
    }
}
```

### 8.4 suspend 原理

```kotlin
/**
 * suspend 函数原理：状态机
 */

// Kotlin 编译器将 suspend 函数编译为状态机：
suspend fun fetchData(): String {
    val r1 = request1()     // 状态0
    val r2 = request2(r1) // 状态1
    return process(r2)     // 状态2
}

// 编译器生成的伪代码（近似）：
class FetchDataCoroutine {
    var label = 0
    var result: String? = null
    
    suspendCoroutine<Unit> { continuation ->
        when (label) {
            0 -> {
                // 执行 request1()
                request1 { res ->
                    result = res
                    label = 1
                    suspendCoroutineCtl.resume(Unit)  // 恢复
                }
            }
            1 -> {
                // 执行 request2(result)
                request2(result) { res ->
                    result = process(res)
                    label = 2
                    suspendCoroutineCtl.resume(Unit)
                }
            }
            2 -> {
                // 完成，返回结果
                suspendCoroutineCtl.resume(result)
            }
        }
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         suspend 工作原理                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 编译转换：
  ─────────────────────────────────────────────────────────────────────────
  suspend 函数 → 状态机
  suspend lambda → 带有 Continuation 参数的普通 lambda

  2. 挂起点：
  ─────────────────────────────────────────────────────────────────────────
  suspend 函数在以下情况挂起：
  - 调用 other suspend 函数
  - delay()
  - yield()
  - channel.receive() 等阻塞操作

  3. 恢复：
  ─────────────────────────────────────────────────────────────────────────
  - 协程被调度执行
  - 从上次挂起点继续（状态机推进）
  - 不创建新线程，不阻塞原线程

  4. 关键类：
  ─────────────────────────────────────────────────────────────────────────
  Continuation：协程状态快照，包含堆栈帧和上下文
  DispatchedContinuation：带调度器的 Continuation
  Dispatcher：决定协程在哪个线程/线程池执行
```

### 8.5 协程构建器

```kotlin
/**
 * 协程构建器详解
 */
class CoroutineBuilders {
    
    // 1. launch：启动协程，不返回结果
    fun launchDemo() {
        viewModelScope.launch {
            // fire and forget
            val data = api.fetch()
            _state.value = data
        }
    }
    
    // 2. async：启动协程，返回 Deferred（结果）
    fun asyncDemo() {
        viewModelScope.launch {
            // 并发执行
            val deferred1 = async { api.fetchUser() }
            val deferred2 = async { api.fetchPosts() }
            
            // 等待两个结果
            val user = deferred1.await()
            val posts = deferred2.await()
            
            // 或 awaitAll
            val (u, p) = awaitAll(
                async { api.fetchUser() },
                async { api.fetchPosts() }
            )
        }
    }
    
    // 3. withContext：切换上下文并返回结果
    fun withContextDemo() {
        viewModelScope.launch {
            // 切换到 IO 线程
            val data = withContext(Dispatchers.IO) {
                api.fetch()
            }
            
            // 切换回主线程（隐式）
            _state.value = data
        }
    }
    
    // 4. withTimeout / withTimeoutOrNull：超时控制
    fun timeoutDemo() {
        viewModelScope.launch {
            // 超时抛异常
            withTimeout(3000L) {
                delay(4000L)  // 会超时
            }
            
            // 超时返回 null
            val result = withTimeoutOrNull(3000L) {
                delay(2000L)
                "success"
            }  // result = null（超时）
        }
    }
    
    // 5. runBlocking（测试用，阻塞当前线程）
    fun runBlockingDemo() {
        runBlocking {
            val result = withContext(Dispatchers.IO) {
                "blocking result"
            }
        }
    }
    
    // 6. produce（Flow Producer）
    fun produceDemo(): ReceiveChannel<Int> = produce {
        for (i in 1..5) {
            send(i)
        }
    }
    
    // 7. actor（Actor 模型）
    fun actorDemo(): SendChannel<String> = actor {
        channel.consumeEach { msg ->
            println(msg)
        }
    }
}
```

### 8.6 协程取消

```kotlin
/**
 * 协程取消
 */
class CancellationDemo {
    
    // 1. 取消协程
    fun cancellation() {
        val job = viewModelScope.launch {
            repeat(1000) { i ->
                println("Working $i")
                delay(500L)  // 每次循环挂起点
            }
        }
        
        // 取消协程
        job.cancel()
        
        // 等待取消完成
        job.join()
        
        // 取消并等待
        job.cancelAndJoin()
    }
    
    // 2. 协程取消的检查点
    fun cancellationCheckpoints() {
        viewModelScope.launch {
            try {
                for (i in 0..10000) {
                    // delay() 是检查点，取消时会抛出 CancellationException
                    delay(1)
                    doWork(i)
                }
            } catch (e: CancellationException) {
                // 协程被取消
            }
        }
        
        // 注意点：CPU密集型任务不会检查取消！
        viewModelScope.launch {
            for (i in 0..1000000000) {
                // 不会响应取消，因为没有挂起点
                compute(i)
                
                // 解决：定期 yield()
                if (i % 1000 == 0) yield()
            }
        }
    }
    
    // 3. 取消传播
    fun cancellationPropagation() {
        viewModelScope.launch {
            // 父协程
            launch {
                // 子协程1
                launch {
                    delay(1000L)
                }
                // 子协程2
                launch {
                    delay(1000L)
                }
                // 任一子协程失败 → 父协程失败 → 所有子协程取消
            }
        }
        
        // SupervisorJob：子协程失败不影响父和兄弟
        viewModelScope.launch(SupervisorJob()) {
            launch {
                throw Exception("Child 1 failed")
            }
            launch {
                // 这个仍然执行
                delay(1000L)
            }
        }
    }
    
    // 4. 清理资源
    fun cleanup() {
        viewModelScope.launch {
            try {
                val resource = acquireResource()
                // 使用资源
            } finally {
                releaseResource()  // 取消时也会执行
            }
            
            // 或使用 suspendCancellableCoroutine
            suspendCancellableCoroutine<Unit> { cont ->
                val callback = Callback {
                    cont.resume(Unit)
                }
                cont.invokeOnCancellation {
                    callback.cancel()  // 取消时清理
                }
            }
        }
    }
}
```

### 8.7 协程异常处理

```kotlin
/**
 * 协程异常处理
 */
class ExceptionHandling {
    
    // 1. try-catch
    fun tryCatch() {
        viewModelScope.launch {
            try {
                val data = api.fetch()
            } catch (e: Exception) {
                handleError(e)
            }
        }
    }
    
    // 2. CoroutineExceptionHandler（全局/作用域级别）
    val handler = CoroutineExceptionHandler { ctx, e ->
        println("Error in $ctx: $e")
    }
    
    fun globalHandler() {
        // 全局作用域
        GlobalScope.launch(handler) {
            throw Exception("Global error")
        }
        
        // 自定义作用域
        val scope = CoroutineScope(SupervisorJob() + handler)
        scope.launch {
            throw Exception("Scoped error")
        }
    }
    
    // 3. async 的异常处理
    fun asyncException() {
        viewModelScope.launch {
            val deferred = async {
                throw Exception("Async error")
            }
            
            try {
                deferred.await()  // 异常在这里抛出
            } catch (e: Exception) {
                handleError(e)
            }
        }
        
        // 推荐：使用 runCatching
        val result = runCatching {
            api.fetch()
        }
        result.onSuccess { data -> /* */ }
        result.onFailure { e -> handleError(e) }
    }
    
    // 4. 异常与结构化并发
    fun structuredException() {
        // launch：子协程异常会直接传播给父协程
        // async：子协程异常在 await() 时才抛出
        // 重要：async 中的异常不会立即传播（这与 launch 不同）
        
        viewModelScope.launch {
            // launch 子协程的异常会被视为未捕获
            // 需要用 SupervisorJob 或异常处理器
        }
    }
}
```

### 8.8 Flow 异步数据流

```kotlin
/**
 * Flow：冷异步数据流（替代 RxJava）
 */
class FlowDemo {
    
    // 1. 创建 Flow
    fun createFlow(): Flow<Int> = flow {
        for (i in 1..5) {
            delay(100)
            emit(i)  // 发射值
        }
    }
    
    // 2. 收集 Flow
    fun collectFlow() {
        viewModelScope.launch {
            createFlow().collect { value ->
                println("Received: $value")
            }
        }
        
        // 只收集新值（StateFlow/SharedFlow）
        // 与 LiveData 类似的模式
    }
    
    // 3. Flow 操作符
    fun flowOperators() {
        viewModelScope.launch {
            flow {
                for (i in 1..10) emit(i)
            }
                .map { it * 2 }                    // 转换
                .filter { it > 5 }                // 过滤
                .take(3)                          // 取前3个
                .onEach { println(it) }           // 副作用
                .catch { e -> emit(-1) }          // 异常处理
                .flowOn(Dispatchers.IO)           // 上游线程
                .collect { /* 主线程接收 */ }
        }
    }
    
    // 4. StateFlow：状态流
    class StateFlowViewModel : ViewModel() {
        private val _state = MutableStateFlow(0)
        val state: StateFlow<Int> = _state.asReadOnlyStateFlow()
        
        fun update(value: Int) {
            _state.value = value
        }
        
        // 与 LiveData 对比：
        // - StateFlow 没有生命周期感知，需要手动取消
        // - StateFlow.newValue() 总是更新，LiveData.postValue() 可合并
    }
    
    // 5. SharedFlow：共享流
    class SharedFlowViewModel : ViewModel() {
        private val _events = MutableSharedFlow<Event>()
        val events: SharedFlow<Event> = _events.asSharedFlow()
        
        fun sendEvent(event: Event) {
            viewModelScope.launch {
                _events.emit(event)  // 所有订阅者收到
            }
        }
    }
    
    // 6. Channel：协程间通信
    fun channelDemo() {
        val channel = Channel<Int>(Channel.BUFFERED)
        
        // 生产者
        viewModelScope.launch {
            for (i in 1..10) {
                channel.send(i)  // 挂起直到消费者接收
            }
            channel.close()
        }
        
        // 消费者
        viewModelScope.launch {
            for (value in channel) {
                println(value)
            }
        }
    }
    
    // 7. Flow 的背压
    fun backpressure() {
        // conflated：只保留最新值
        val flow1 = MutableSharedFlow<Int>(replay = 0, extraBufferCapacity = 0)
        
        // buffered：缓冲指定数量
        val flow2 = MutableSharedFlow<Int>(replay = 0, extraBufferCapacity = 10)
        
        // 背压处理
        flow.onBufferOverflow(BufferOverflow.DROP_OLDEST)  // 丢弃旧值
        flow.onBufferOverflow(BufferOverflow.DROP_LATEST)   // 丢弃新值
        flow.onBufferOverflow(BufferOverflow.SUSPEND)       // 挂起（默认）
    }
}

---

## 9. Android 线程模型

### 9.1 主线程职责

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 主线程（UI线程）职责                         │
└─────────────────────────────────────────────────────────────────────────────┘

  主线程不能做的事情：
  ─────────────────────────────────────────────────────────────────────────
  1. 网络请求（NetworkOnMainThreadException）
  2. 耗时数据库操作
  3. 耗时的文件操作
  4. 大量的计算
  5. 任何超过 16ms 的操作（导致卡顿）

  主线程的职责（应该做的）：
  ─────────────────────────────────────────────────────────────────────────
  1. 接收用户输入事件
  2. 更新 UI（Views）
  3. 分发事件给合适的 View
  4. 执行短时的动画
  5. 调用 Choreographer 进行帧渲染

  主线程消息循环：
  ─────────────────────────────────────────────────────────────────────────
  ActivityThread.main()
      └── Looper.prepareMainLooper()
          └── Looper.loop()  // 永不退出
              └── MessageQueue.next()  // 有消息则处理，无消息则阻塞
```

### 9.2 Binder 线程池

```java
/**
 * Binder 线程池：处理 IPC 调用
 */
class BinderPoolDemo {
    /*
     * Binder 线程池特点：
     * 1. 最大 16 个线程
     * 2. 按需创建，空闲回收
     * 3. 处理来自其他进程的 IPC 请求
     * 4. 不要在 Binder 线程中执行耗时操作！
     *
     * 位置：frameworks/native/libs/binder/ProcessState.cpp
     * 常量：kMaxThreadPoolSize = 16
     */
}
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Binder 线程池与主线程的关系                              │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    应用进程                                              │
  │                                                                         │
  │   ┌──────────────────────────────────────────────────────────────────┐ │
  │   │                     主线程（UI线程）                              │ │
  │   │                     Looper + Handler                             │ │
  │   └──────────────────────────────────────────────────────────────────┘ │
  │                                                                         │
  │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                     │
  │   │ Binder  │ │ Binder  │ │ Binder  │ │ Binder  │   (最多16个)         │
  │   │ 线程1   │ │ 线程2   │ │ 线程3   │ │ 线程N   │                     │
  │   └─────────┘ └─────────┘ └─────────┘ └─────────┘                     │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  常见错误：
  ─────────────────────────────────────────────────────────────────────────
  在 AIDL 实现的 onTransact() 中执行耗时操作
  → Binder 线程被阻塞 → 其他进程的 IPC 调用排队 → 系统变慢

  正确做法：
  ─────────────────────────────────────────────────────────────────────────
  onTransact() 收到请求 → 转发到工作线程 → 立即返回
```

### 9.3 Android 特有的线程优先级

```java
/**
 * Android Process 线程优先级
 * 位置：frameworks/base/core/java/android/os/Process.java
 */
class AndroidPriority {
    
    // Android 线程优先级（nice 值）
    public void setPriority() {
        // 主线程：0
        Process.setThreadPriority(Process.THREAD_PRIORITY_DEFAULT);
        
        // 后台线程：10（THREAD_PRIORITY_BACKGROUND = 10）
        Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);
        
        // UI 线程：-2（相对主线程提高优先级）
        Process.setThreadPriority(Process.THREAD_PRIORITY_FOREGROUND);
        
        // 显示相关：-4
        Process.setThreadPriority(Process.THREAD_PRIORITY_DISPLAY);
        
        // 动画相关：-8
        Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_DISPLAY);
        
        // 音频：-16
        Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO);
        
        // 实时音频：-19
        Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_AUDIO);
    }
    
    // 在 Kotlin Coroutines 中设置优先级（有限支持）
    public void coroutinePriority() {
        val dispatcher = Dispatchers.Default.limitedParallelism(1)
        // 注意：Android 不支持调整子线程的 nice 值
        // 协程线程池由系统统一调度
    }
}
```

---

## 10. 并发设计模式

### 10.1 Thread-Per-Message

```java
/**
 * Thread-Per-Message 模式：每个请求一个线程
 * 简单，但不适合高并发
 */
class ThreadPerMessageDemo {
    
    // 不推荐：线程开销大
    public void processRequest(Request request) {
        new Thread(() -> handleRequest(request)).start();
    }
    
    // 推荐：使用线程池
    private final ExecutorService executor = Executors.newCachedThreadPool();
    
    public void processRequestBetter(Request request) {
        executor.execute(() -> handleRequest(request));
    }
}
```

### 10.2 Worker Thread

```java
/**
 * Worker Thread 模式：预先创建线程池，复用线程
 * 配合任务队列使用
 */
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
}
```

### 10.3 Producer-Consumer

```java
/**
 * Producer-Consumer 模式：解耦生产者和消费者
 */
class ProducerConsumerPattern {
    
    public void demo() {
        BlockingQueue<Item> queue = new LinkedBlockingQueue<>(100);
        
        // 生产者
        IntStream.range(0, 4).forEach(i -> 
            new Thread(() -> {
                while (true) {
                    Item item = produce();
                    try {
                        queue.put(item);  // 满则阻塞
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }).start()
        );
        
        // 消费者
        IntStream.range(0, 2).forEach(i ->
            new Thread(() -> {
                while (true) {
                    try {
                        Item item = queue.take();  // 空则阻塞
                        consume(item);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }).start()
        );
    }
    
    private Item produce() { return new Item(); }
    private void consume(Item item) { }
    
    static class Item { }
}
```

### 10.4 Pipeline

```java
/**
 * Pipeline 模式：流水线处理，每阶段可并行
 */
class PipelineDemo {
    
    public void pipeline() {
        BlockingQueue<Data> q1 = new LinkedBlockingQueue<>(50);
        BlockingQueue<Data> q2 = new LinkedBlockingQueue<>(50);
        BlockingQueue<Data> q3 = new LinkedBlockingQueue<>(50);
        
        // 阶段1：读取
        startStage("Reader", () -> {
            while (true) {
                Data d = readData();
                q1.offer(d);
            }
        });
        
        // 阶段2：处理
        startStage("Processor", () -> {
            while (true) {
                Data d = q1.poll();
                Data processed = process(d);
                q2.offer(processed);
            }
        });
        
        // 阶段3：写入
        startStage("Writer", () -> {
            while (true) {
                Data d = q2.poll();
                writeData(d);
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

```kotlin
/**
 * Actor 模型：每个 Actor 独占自己的状态，消息传递通信
 * Kotlin 没有内置 Actor，但可以用 Channel + Coroutine 实现
 */
class ActorDemo {
    
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
    
    // 或用 Channel 作为收件箱
    class CounterActor : CoroutineScope by CoroutineScope(Dispatchers.Default) {
        private val mailbox = Channel<Msg>(Channel.UNLIMITED)
        private var count = 0
        
        suspend fun process() {
            for (msg in mailbox) {
                when (msg) {
                    is Increment -> count++
                    is GetCount -> msg.reply.complete(count)
                }
            }
        }
    }
    
    sealed class Msg
    class Increment : Msg()
    class GetCount(val reply: CompletableDeferred<Int>) : Msg()
}
```

---

## 11. 性能与反模式

### 11.1 常见性能问题

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         并发性能问题                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 锁竞争激烈
  ─────────────────────────────────────────────────────────────────────────
  现象：CPU 使用率不高，但线程都在阻塞
  
  原因：
  - 锁粒度太大（对整个集合加锁）
  - 锁范围不对（锁了不需要锁的代码）
  - 锁顺序死锁（多个线程互相等待对方的锁）
  
  解决：
  - 减小锁粒度（ConcurrentHashMap 分段锁）
  - 读写分离（ReadWriteLock）
  - 无锁算法（CAS、原子类）
  - 避免嵌套锁

  2. 线程过多
  ─────────────────────────────────────────────────────────────────────────
  现象：线程创建和上下文切换消耗大量 CPU
  
  原因：
  - 每个任务创建一个线程
  - 线程池配置不合理
  - 协程过多（虽然轻量，但仍有调度开销）
  
  解决：
  - 使用线程池
  - 合理配置核心线程数
  - 监控线程数

  3. 伪共享（False Sharing）
  ─────────────────────────────────────────────────────────────────────────
  现象：多线程访问不同变量，但性能差
  
  原因：CPU 缓存行 64 字节，两个变量在同一行
        修改任意一个，整个缓存行失效
  
  解决：
  - @Contended 注解（JDK 8+）
  - LongAdder（分段设计，避免伪共享）
  - padding 填充

  4. 过度同步
  ─────────────────────────────────────────────────────────────────────────
  现象：单线程比多线程还快
  
  原因：
  - synchronized 加在关键路径上
  - 所有操作都持有锁
  
  解决：
  - 减少锁持有时间
  - 缩小锁范围
  - 使用并发容器替代 synchronized
```

### 11.2 并发反模式

```java
/**
 * 常见并发反模式
 */

// 反模式1：在锁内执行耗时操作
class BadPattern1 {
    private final Object lock = new Object();
    
    public void wrong() {
        synchronized (lock) {
            // 网络请求！阻塞其他线程
            networkCall();
        }
    }
    
    public void right() {
        String data;
        synchronized (lock) {
            data = cachedData;  // 只锁快速操作
        }
        // 耗时操作放外面
        processData(data);
    }
}

// 反模式2：省略 finally 中的 unlock
class BadPattern2 {
    private final Lock lock = new ReentrantLock();
    
    public void wrong() {
        lock.lock();
        if (condition()) {
            return;  // 锁未释放！
        }
        lock.unlock();
    }
    
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
}

// 反模式3：双重检查锁定（DCL）在 Java 中不安全
class BadPattern3 {
    private volatile Resource resource;
    
    public Resource getResource() {
        if (resource == null) {  // 第一次检查
            synchronized (this) {
                if (resource == null) {  // 第二次检查
                    resource = new Resource();  // 可能重排序
                }
            }
        }
        return resource;
    }
    
    // 注意：Java 5+ 使用 volatile 可以安全实现 DCL
    // 但现代写法推荐直接用 enum 单例或 holder
}

// 反模式4：使用 Thread.sleep 等待条件
class BadPattern4 {
    public void wrong() {
        while (!condition) {
            Thread.sleep(1000);  // 浪费 CPU，不精确，响应差
        }
    }
    
    public void right() {
        synchronized (lock) {
            while (!condition) {
                lock.wait();  // 高效，精确
            }
        }
    }
}

// 反模式5：混淆线程和协程
class BadPattern5 {
    // 错误：在协程里用 Thread.sleep
    suspend fun wrong() {
        Thread.sleep(1000)  // 阻塞协程所在线程！
    }
    
    // 正确：用 delay（挂起协程，不阻塞线程）
    suspend fun right() {
        delay(1000)  // 挂起协程，线程可以执行其他协程
    }
}
```

---

## 12. 面试高频问题

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         面试高频问题                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Q1: synchronized 和 Lock 的区别？

  synchronized：
  - JVM 内置关键字，编译后monitorenter/monitorexit
  - 自动获取/释放锁
  - 不可中断、不可超时、不支持公平锁
  - 可重入（同一个线程）

  Lock：
  - java.util.concurrent.locks.Lock 接口
  - 必须手动 unlock()
  - 支持中断、超时、公平锁
  - 可重入
  - 可绑定多个 Condition

Q2: volatile 和 synchronized 的区别？

  volatile：
  - 只保证可见性和有序性
  - 不保证原子性
  - 性能高

  synchronized：
  - 保证原子性、可见性、有序性
  - 可重入
  - 性能较低

Q3: 线程池的核心参数有哪些？

  corePoolSize：核心线程数
  maximumPoolSize：最大线程数
  keepAliveTime：非核心线程存活时间
  unit：时间单位
  workQueue：任务队列
  threadFactory：线程工厂
  handler：拒绝策略

Q4: 线程池的执行流程？

  线程数<corePoolSize → 创建核心线程
  队列满 → 创建非核心线程
  达maxPoolSize → 拒绝策略

Q5: ConcurrentHashMap 如何实现线程安全？

  JDK 7：Segment 分段锁，每段独立锁
  JDK 8+：
  - 数组 + 链表/红黑树
  - Node 使用 volatile 保证可见性
  - 写操作用 CAS + synchronized
  - 锁粒度细化到单个桶

Q6: 什么是 CAS？有什么问题？

  CAS：Compare-And-Swap，硬件级原子操作
  三个操作数：内存位置、预期值、新值
  V==A 时设为 B，返回是否成功

  问题：
  - ABA 问题（用 AtomicStampedReference）
  - 自旋开销（竞争激烈时重试多）
  - 只能保证一个变量原子性

Q7: Coroutine 和线程的区别？

  - 协程是用户态调度，不占用系统资源
  - 协程切换开销极小（状态机）
  - 协程挂起不阻塞线程
  - 线程由 OS 调度，上下文切换开销大

Q8: 如何避免死锁？

  1. 避免嵌套锁
  2. 按固定顺序获取锁
  3. 使用带超时的锁
  4. 减少锁持有时间
  5. 使用 Lock.tryLock() 探测

Q9: 生产者-消费者模式如何实现？

  BlockingQueue：put() 满则阻塞，take() 空则阻塞
  或用 wait/notify 配合 synchronized

Q10: 什么是线程安全？如何实现？

  线程安全：多线程访问时，始终表现正确

  实现方式：
  1. synchronized
  2. Lock
  3. volatile（单变量）
  4. 原子变量
  5. 并发容器
  6. 不可变对象
  7. 线程局部变量（ThreadLocal）
```

---

## 总结

本文覆盖了 Android/Java 多线程与并发的核心知识点：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         知识图谱                                            │
└─────────────────────────────────────────────────────────────────────────────┘

  基础层：
  Thread / Runnable / Callable → 线程创建
  线程状态转换 → 生命周期理解
  守护线程 / 优先级 → 线程属性

  同步层：
  synchronized → 最基础同步
  volatile → 可见性
  wait/notify → 等待通知
  Lock/Condition → 高级同步
  ReadWriteLock/StampedLock → 读写分离

  工具层：
  CountDownLatch / CyclicBarrier / Phaser → 多线程同步
  Semaphore → 资源限制
  Exchanger → 数据交换

  原子层：
  AtomicInteger/Long → 原子整数
  AtomicReference → 原子引用
  LongAdder → 高并发计数
  CAS 原理 → 底层支撑

  容器层：
  ConcurrentHashMap → 并发哈希
  CopyOnWriteArrayList → 读多写少
  BlockingQueue → 生产者-消费者
  ThreadLocal → 线程局部存储

  线程池：
  ThreadPoolExecutor → 核心
  Executors 工厂 → 快速创建
  饱和策略 → 拒绝处理

  协程层：
  Dispatchers → 调度器
  suspend → 挂起原理
  Scope/Context → 生命周期
  Flow/Channel → 异步数据流

  Android 层：
  主线程职责 → 不能做的事
  Binder 线程池 → IPC
  Process 优先级 → Android 特有
```

掌握以上内容，就具备了扎实的 Android 并发编程能力。

---

*文档更新时间: 2026-03-24*

```
```
```
```
```

