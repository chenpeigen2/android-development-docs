# Android Handler 机制完全指南

> 作者：OpenClaw | 日期：2026-03-08

---

## 目录

- [1. 概述](#1-概述)
  - [1.1 核心组件](#11-核心组件)
- [2. 整体架构](#2-整体架构)
  - [2.1 组件关系图](#21-组件关系图)
  - [2.2 完整工作流程](#22-完整工作流程)
  - [2.3 超详细完整流程图](#23-超详细完整流程图)
- [3. ThreadLocal 详解](#3-threadlocal-详解)
  - [3.1 ThreadLocal 原理图](#31-threadlocal-原理图)
  - [3.2 ThreadLocal.get() 流程图](#32-threadlocalget-流程图)
  - [3.3 ThreadLocal 源码分析](#33-threadlocal-源码分析)
  - [3.4 Looper.prepare() 流程图](#34-looperprepare-流程图)
  - [3.5 Looper 中的 ThreadLocal 源码](#35-looper-中的-threadlocal-源码)
- [4. Looper 详解](#4-looper-详解)
  - [4.1 Looper.loop() 流程图](#41-looperloop-流程图)
  - [4.2 Looper 源码分析](#42-looper-源码分析)
  - [4.3 主线程初始化流程图](#43-主线程初始化流程图)
  - [4.4 主线程初始化源码](#44-主线程初始化源码)
- [5. MessageQueue 详解](#5-messagequeue-详解)
  - [5.1 MessageQueue.next() 流程图](#51-messagequeuenext-流程图)
  - [5.2 MessageQueue 源码分析](#52-messagequeue-源码分析)
    - [5.2.1 Legacy 真正的摘链和退出顺序](#521-legacy-真正的摘链和退出顺序)
    - [5.2.2 concurrent 的 outer loop：poll、idle 和 teardown](#522-concurrent-的-outer-looppollidle-和-teardown)
    - [5.2.3 并发发布的真实字段与状态](#523-并发发布的真实字段与状态)
    - [5.2.4 退出、取消与屏障的应用边界](#524-退出取消与屏障的应用边界)
- [6. Message 详解](#6-message-详解)
  - [6.1 消息池流程图](#61-消息池流程图)
  - [6.2 Message 源码分析](#62-message-源码分析)
    - [回收状态不能只清 payload](#回收状态不能只清-payload)
- [7. Handler 详解](#7-handler-详解)
  - [7.1 Handler 发送消息流程图](#71-handler-发送消息流程图)
  - [7.2 Handler 发送消息源码](#72-handler-发送消息源码)
  - [7.3 Handler.dispatchMessage() 流程图](#73-handlerdispatchmessage-流程图)
  - [7.4 Handler.dispatchMessage() 源码](#74-handlerdispatchmessage-源码)
- [8. Native 层实现](#8-native-层实现)
  - [8.1 epoll 机制流程图](#81-epoll-机制流程图)
- [9. 同步屏障机制](#9-同步屏障机制)
  - [9.1 同步屏障流程图](#91-同步屏障流程图)
  - [9.2 同步屏障源码](#92-同步屏障源码)
- [10. IdleHandler 机制](#10-idlehandler-机制)
- [11. HandlerThread](#11-handlerthread)
- [12. 主线程消息循环](#12-主线程消息循环)
- [13. 常见问题](#13-常见问题)
  - [13.1 loop() 为什么不会卡死？](#131-loop-为什么不会卡死)
  - [13.2 Handler 内存泄漏](#132-handler-内存泄漏)
  - [13.3 为什么 MessageQueue.next() 需要加锁？](#133-为什么-messagequeuenext-需要加锁)
    - [不加锁会导致的问题](#不加锁会导致的问题)
    - [synchronized 的作用](#synchronized-的作用)
    - [为什么 nativePollOnce 在锁外面？](#为什么-nativepollonce-在锁外面)
- [14. 总结](#14-总结)
- [固定版本源码索引](#固定版本源码索引)

---

## 1. 概述

Handler 是 Android 消息机制的核心，实现了线程间的异步通信。

### 1.1 核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **ThreadLocal** | 线程局部变量存储 | 每个已 prepare 的线程至多一个 Looper |
| **Looper** | 消息循环器 | 不断从队列取消息，无限循环 |
| **MessageQueue** | 消息队列 | 实现可选：Legacy 链表 / concurrent 队列 |
| **Message** | 消息对象 | 包含 what、obj、when、target |
| **Handler** | 消息发送/处理 | 绑定 Looper，发送和处理消息 |

---

## 2. 整体架构

### 2.1 组件关系图

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Handler 机制整体架构                                 │
└─────────────────────────────────────────────────────────────────────────────┘

                            ┌─────────────────────────────────┐
                            │         Thread (主线程)          │
                            │                                 │
                            │  ┌───────────────────────────┐  │
                            │  │      ThreadLocal         │  │
                            │  │   (存储 Looper)           │  │
                            │  └───────────┬───────────────┘  │
                            │              │                  │
                            │              ▼                  │
                            │  ┌───────────────────────────┐  │
                            │  │         Looper            │  │
                            │  │   loop() { for(;;) }      │  │
                            │  └───────────┬───────────────┘  │
                            │              │                  │
                            │              ▼                  │
                            │  ┌───────────────────────────┐  │
                            │  │      MessageQueue         │  │
                            │  │   按时序组织的消息            │  │
                            │  └───────────┬───────────────┘  │
                            │              │                  │
                            │              ▼                  │
                            │  ┌───────────────────────────┐  │
                            │  │        Handler            │  │
                            │  └───────────────────────────┘  │
                            └─────────────────────────────────┘
```

### 2.2 完整工作流程

```text
1. 准备阶段
   ActivityThread.main()
       ├──► Looper.prepareMainLooper() → new Looper() → new MessageQueue()
       └──► Looper.loop()

2. 消息循环
   for (;;) {
       Message msg = queue.next();           // 阻塞等待
       msg.target.dispatchMessage(msg);       // 分发消息
       msg.recycleUnchecked();                // 回收消息
   }

3. 发送消息
   Handler.sendMessage(msg)
       └──► queue.enqueueMessage(msg, when) → nativeWake()

4. 处理消息
   Handler.dispatchMessage(msg)
       ├──► msg.callback.run()
       ├──► mCallback.handleMessage(msg)
       └──► handleMessage(msg)
```

### 2.3 超详细完整流程图

这里按 Android 17 的实际层次展开；`next()` 内部结构在第 5 章分别分析，不再把 Legacy 的 `mMessages` 当成所有设备的实现。

```text
进程主线程                         生产者线程                   Native
ActivityThread.main()
  Looper.prepareMainLooper()
    prepare(false)
      new Looper(false)
        new MessageQueue(false) -----------------------> nativeInit()
        保存当前 Thread                                  NativeMessageQueue
  thread.attach(false, startSeq)                         复用 Looper::getForThread()
    向 AMS 报告进程已启动                                不存在才 new Looper(false)
  Looper.loop()
    loopOnce(me, ident, thresholdOverride)
      mQueue.next()
        nextLegacy / nextConcurrent / Deli 路径
        nativePollOnce(ptr, timeout) ------------------> Looper::pollOnce()
                                                         epoll 等待或即时轮询
                                     handler.post(r)
                                       Message.obtain()
                                       msg.callback = r
                                       enqueueMessage()
                                         msg.target = handler
                                         设置异步标志（若 Handler 异步）
                                         发布消息，判断是否要唤醒
                                         nativeWake() --> eventfd 写入 uint64_t 1
        唤醒后重算可投递消息 <---------------------------- poll 返回
      msg.target.dispatchMessage(msg)
        callback.run() / Handler.Callback / handleMessage()
      正常分发结束后 msg.recycleUnchecked()
      下一个 loopOnce()
```

1. `attach()` 发起进程绑定协议；Application 的创建和 `onCreate()` 在后续 `H.BIND_APPLICATION -> handleBindApplication()` 中发生，不是 `attach()` 内直接同步创建。
2. NativeMessageQueue 优先取得当前线程的 Native Looper；创建 Native Looper 时由其构造过程初始化 epoll/eventfd，Java JNI 包装层并不调用私有的 `rebuildEpoll()`。
3. `nativePollOnce` 返回不等于“立刻得到刚发布的消息”：可能是 FD 事件、提前唤醒、超时或屏障状态变化，必须重新判断时间和屏障。
4. `loopOnce()` 在分发前后维护 observer、trace、调用身份和 WorkSource。业务异常会报告给 observer 后继续抛出，不会被 Looper 自动吞掉；不能把回收放进无条件成功路径后声称异常也完成回收。
5. Legacy 回收清字段并标记 in-use，之后可入池；并发模式保留 flags/链接、清理业务引用，不把 Message 重新投入全局池。入队后不应再改写、重复发送或手动回收同一 Message，详见第 6 章。

---

## 3. ThreadLocal 详解

### 3.1 ThreadLocal 原理图

```text
   Thread 1                    Thread 2                    Thread 3
   ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
   │ threadLocals    │        │ threadLocals    │        │ threadLocals    │
   └────────┬────────┘        └────────┬────────┘        └────────┬────────┘
            │                          │                          │
            ▼                          ▼                          ▼
   ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
   │ Key: sThreadLocal│       │ Key: sThreadLocal│       │ Key: sThreadLocal│
   │ Value: Looper1  │        │ Value: Looper2  │        │ Value: null     │
   └─────────────────┘        └─────────────────┘        └─────────────────┘
```

### 3.2 ThreadLocal.get() 流程图

```text
  sThreadLocal.get()
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 获取当前线程: Thread t = Thread.currentThread()                     │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. 获取线程的 ThreadLocalMap: map = t.threadLocals                     │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. map == null?   Yes → 调用 setInitialValue()                                      │
  │                    No  → 继续查找                                       │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  4. 以 sThreadLocal 为 key 查找 Entry, 返回 e.value                    │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 ThreadLocal 源码分析

```java
/**
 * ThreadLocal 源码分析 - 对应上面的流程图
 */
public class ThreadLocal<T> {

    public T get() {
        // 1. 获取当前线程
        Thread t = Thread.currentThread();

        // 2. 获取线程的 ThreadLocalMap
        ThreadLocalMap map = getMap(t);

        if (map != null) {
            // 3. 以 this 为 key 查找 Entry
            ThreadLocalMap.Entry e = map.getEntry(this);
            if (e != null) {
                // 4. 返回 value
                return (T) e.value;
            }
        }
        // 5. 没有找到，返回初始值
        return setInitialValue();
    }

    public void set(T value) {
        Thread t = Thread.currentThread();
        ThreadLocalMap map = getMap(t);
        if (map != null) {
            map.set(this, value);
        } else {
            createMap(t, value);
        }
    }

    ThreadLocalMap getMap(Thread t) {
        return t.threadLocals;
    }
}
```

### 3.4 Looper.prepare() 流程图

```text
  Looper.prepare()
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 检查当前线程是否已有 Looper                                         │
  │     if (sThreadLocal.get() != null)                                     │
  └─────────────────────────────────────────────────────────────────────────┘
         │
    ┌────┴────┐
   Yes        No
    │         │
    ▼         ▼
┌─────────┐  ┌─────────────────────────────────────────────────────────────┐
│抛出异常 │  │  2. 创建 Looper 并存入 ThreadLocal                          │
│         │  │     sThreadLocal.set(new Looper(quitAllowed))               │
│         │  │     new Looper() → mQueue = new MessageQueue()             │
└─────────┘  └─────────────────────────────────────────────────────────────┘
```

### 3.5 Looper 中的 ThreadLocal 源码

```java
/**
 * Looper 使用 ThreadLocal 存储 - 对应上面的流程图
 */
public class Looper {

    static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<>();

    public static void prepare() {
        prepare(true);
    }

    private static void prepare(boolean quitAllowed) {
        // 1. 检查是否已有 Looper
        if (sThreadLocal.get() != null) {
            throw new RuntimeException("Only one Looper may be created per thread");
        }
        // 2. 创建 Looper 并存入 ThreadLocal
        sThreadLocal.set(new Looper(quitAllowed));
    }

    public static void prepareMainLooper() {
        prepare(false);  // 主线程不允许退出
        synchronized (Looper.class) {
            if (sMainLooper != null) {
                throw new IllegalStateException("The main Looper has already been prepared.");
            }
            sMainLooper = myLooper();
        }
    }

    public static Looper myLooper() {
        return sThreadLocal.get();
    }
}
```

---

## 4. Looper 详解

### 4.1 Looper.loop() 流程图

```text
  Looper.loop()
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 获取当前线程的 Looper: me = myLooper()                              │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. 获取消息队列: queue = me.mQueue                                     │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. 进入无限循环 for (;;)  ◄────────────────────────────────────────┐  │
  └─────────────────────────────────────────────────────────────────────┤  │
         │                                                              │  │
         ▼                                                              │  │
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  4. 取出消息: Message msg = queue.next()  // 可能阻塞                  │
  └─────────────────────────────────────────────────────────────────────────┘
         │
    ┌────┴────┐
  (null)    (有消息)
    │         │
    ▼         ▼
┌─────────┐  ┌─────────────────────────────────────────────────────────────┐
│ return  │  │  5. 分发消息: msg.target.dispatchMessage(msg)              │
│ (退出)  │  └─────────────────────────────────────────────────────────────┘
└─────────┘                           │
                                      ▼
                        ┌─────────────────────────────────────────────────────┐
                        │  6. 回收消息: msg.recycleUnchecked()                │
                        └─────────────────────────────────────────────────────┘
                                      │
                                      └──────────────────────────────────────►
```

### 4.2 Looper 源码分析

```java
/**
 * Looper 分发语义示意；实际 loop() 调用 loopOnce()，监控与身份恢复见正文
 */
public final class Looper {

    static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<>();
    final MessageQueue mQueue;
    final Thread mThread;

    private Looper(boolean quitAllowed) {
        mQueue = new MessageQueue(quitAllowed);
        mThread = Thread.currentThread();
    }

    public static void loop() {
        // 1. 获取当前线程的 Looper
        final Looper me = myLooper();
        if (me == null) {
            throw new RuntimeException("No Looper; Looper.prepare() wasn't called on this thread.");
        }

        // 2. 获取消息队列
        final MessageQueue queue = me.mQueue;

        // 3. 无限循环
        for (;;) {
            // 4. 取出消息 (可能阻塞)
            Message msg = queue.next();
            if (msg == null) {
                return;  // 队列退出
            }

            // 5. 分发消息
            msg.target.dispatchMessage(msg);

            // 6. 回收消息
            msg.recycleUnchecked();
        }
    }

    public void quit() {
        mQueue.quit(false);
    }

    public void quitSafely() {
        mQueue.quit(true);
    }
}
```

### 4.3 主线程初始化流程图

```text
  JVM 启动
      │
      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  ActivityThread.main()                                                  │
  └─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. Looper.prepareMainLooper()                                          │
  │     └── new Looper(false) → mQueue = new MessageQueue(false)            │
  └─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. 创建 ActivityThread: thread.attach()                                │
  └─────────────────────────────────────────────────────────────────────────┘
      │
      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. Looper.loop()  // 进入消息循环，永不返回                             │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 4.4 主线程初始化源码

```java
/**
 * ActivityThread.main() - 对应上面的流程图
 */
public static void main(String[] args) {
    // 1. 初始化主线程 Looper
    Looper.prepareMainLooper();

    // 2. 创建 ActivityThread
    ActivityThread thread = new ActivityThread();
    thread.attach(false, startSeq);

    // 3. 启动消息循环
    Looper.loop();

    // 4. 正常情况下永远不会执行到这里
    throw new RuntimeException("Main thread loop unexpectedly exited");
}
```

---

## 5. MessageQueue 详解

### 5.1 MessageQueue.next() 流程图

固定 tag 的 `core/java/Android.bp` 中，`messagequeue-gen` 按 `release_package_messagequeue_implementation` 选择源码；未覆盖时使用 `CombinedMessageQueue/*.java`。输出类仍叫 `android.os.MessageQueue`，源码并不在旧路径 `core/java/android/os/MessageQueue.java`。

```text
构建时选择实现
  CombinedMessageQueue/MessageQueue.java
    getUseConcurrent() -> compat change / flag / 进程条件
    next() -> nextLegacy() 或 nextConcurrent()
  CombinedDeliMessageQueue/MessageQueue.java
    setUseDeliQueue()/getUseConcurrent() -> Legacy 或 Deli
  LegacyMessageQueue/MessageQueue.java
    有序单链表实现
```

Combined 的 `USE_NEW_MESSAGEQUEUE` 兼容变更及 flags/进程判断决定运行模式，不能简单写成“所有应用都用旧队列”或“Android 17 一律无锁”。Deli 是另一套构建选项，不能把它和 Combined 的内部字段混成一个类。

### 5.2 MessageQueue 源码分析

**Legacy 路径：有序链表、屏障选择和正确摘链。** 以下是 `nextLegacy()` 的核心算法示意，省略 FD 监听与日志，不是可独立编译的完整类：

```java
// nativePollOnce 在队列监视器锁外；timeout=0 轮询，-1 无限等待。
nativePollOnce(mPtr, nextPollTimeoutMillis);
synchronized (this) {
    final long now = SystemClock.uptimeMillis();
    Message prevMsg = null;
    Message msg = mMessages;
    if (msg != null && msg.target == null) {
        do {
            prevMsg = msg;
            msg = msg.next;
        } while (msg != null && !msg.isAsynchronous());
    }
    if (msg != null) {
        if (now < msg.when) {
            nextPollTimeoutMillis = (int) Math.min(msg.when - now, Integer.MAX_VALUE);
        } else {
            mBlocked = false;
            if (prevMsg != null) prevMsg.next = msg.next;
            else mMessages = msg.next;
            msg.next = null;
            msg.markInUse();
            return msg;
        }
    } else {
        nextPollTimeoutMillis = -1;
    }
    // 实际实现还维护异步计数/尾指针，处理 quit/dispose 和 IdleHandler 快照。
}
```

屏障后取出的异步消息通常不是头节点，必须更新 `prevMsg.next`，不能无条件 `mMessages = msg.next`，否则会丢失屏障和前面的同步消息。消息未到期时要限幅 timeout，防止 long 转 int 溢出。

Legacy 入队步骤：校验 `target` 与 in-use 状态；持锁检查 quitting；设置 `when` 和 in-use 标志；按时间插入（`when == 0` 走队首）；同时间普通消息保持 FIFO；若新消息改变阻塞线程的最早可执行候选才 `nativeWake`。退出后的发送回收消息并返回 false，而不是继续接收。

**Combined concurrent 路径：Treiber 栈发布、两个并发跳表排序。** `enqueueMessageConcurrent()` 通过 CAS 发布到共享栈；Looper 的 `nextMessage()` 将栈内容 drain 到同步/异步两个 `ConcurrentSkipListSet<Message>`（按 sEnqueueOrder 排序），按时间和插入序号选择候选。消费者要协调 drain、删除与 quitting 状态，也使用局部锁；“发布用 CAS”不等于整个 MessageQueue 所有操作无锁。先建立可见的消息节点，再按栈状态和到期时间决定唤醒，避免 lost wakeup。

**Deli 路径：MessageStack + MessageHeap。** `enqueueMessage()` 为消息分配普通递增序号或队首递减序号，通过 `mStack.pushMessage()` 发布；消费者 `heapSweep()`、`peek(false/true)`、`remove()` 在两个类别的候选中选择。相同时间普通消息为 FIFO，队首插入为 LIFO；取消先标记再清理，并用 native 指针引用计数避免 quit 与 nativeWake/dispose 竞争。

这两条并发路径都保持“一个 Looper 线程分发”，异步消息只是可以越过同步屏障，并不会自动转移到工作线程。耗时 Handler 回调仍会阻塞后续消息。

---

#### 5.2.1 Legacy 真正的摘链和退出顺序

下面节选固定 tag `CombinedMessageQueue/MessageQueue.java:975–1038`。此前的算法示意只突出 prevMsg；真实实现还维护 `mLast`、异步计数和 trace 计数，少一项可能让后续入队/唤醒判断失真：

```java
            nativePollOnce(ptr, nextPollTimeoutMillis);

            synchronized (this) {
                // Try to retrieve the next message.  Return if found.
                final long now = SystemClock.uptimeMillis();
                Message prevMsg = null;
                Message msg = mMessages;
                if (msg != null && msg.target == null) {
                    // Stalled by a barrier.  Find the next asynchronous message in the queue.
                    do {
                        prevMsg = msg;
                        msg = msg.next;
                    } while (msg != null && !msg.isAsynchronous());
                }
                if (msg != null) {
                    if (now < msg.when) {
                        // Next message is not ready.  Set a timeout to wake up when it is ready.
                        nextPollTimeoutMillis = (int) Math.min(msg.when - now, Integer.MAX_VALUE);
                    } else {
                        // Got a message.
                        mBlocked = false;
                        if (prevMsg != null) {
                            prevMsg.next = msg.next;
                            if (prevMsg.next == null) {
                                mLast = prevMsg;
                            }
                        } else {
                            mMessages = msg.next;
                            if (msg.next == null) {
                                mLast = null;
                            }
                        }
                        msg.next = null;
                        if (DEBUG) Log.v(TAG_L, "Returning message: " + msg);
                        msg.markInUse();
                        if (msg.isAsynchronous()) {
                            mAsyncMessageCount--;
                        }
                        decAndTraceMessageCount();
                        return msg;
                    }
                } else {
                    // No more messages.
                    nextPollTimeoutMillis = -1;
                }

                // Process the quit message now that all pending messages have been handled.
                if (mQuitting) {
                    dispose();
                    return null;
                }

                // If first time idle, then get the number of idlers to run.
                // Idle handles only run if the queue is empty or if the first message
                // in the queue (possibly a barrier) is due to be handled in the future.
                if (pendingIdleHandlerCount < 0
                        && (mMessages == null || now < mMessages.when)) {
                    pendingIdleHandlerCount = mIdleHandlers.size();
                }
                if (pendingIdleHandlerCount <= 0) {
                    // No idle handlers to run.  Loop and wait some more.
                    mBlocked = true;
                    continue;
                }
```

逐分支推演：

1. `barrier -> sync(已到期) -> async(未来)`：扫描跳过同步消息，但未来异步候选也不能投递，只设置到期 timeout。
2. `barrier -> sync -> async(已到期)`：prevMsg 指向 sync，修改 sync.next 摘走 async；barrier 与 sync 保留，直到屏障移除。
3. 普通头消息已到期：推进 mMessages；若队列空，mLast 同步清空。
4. `mQuitting` 检查发生在取出可执行候选之后。这配合 quitSafely 提前清理未来消息，使已到期且未被屏障阻塞的消息能够执行；它不是“忽略屏障清空所有消息”。
5. 到期屏障作为队首不满足 `now < mMessages.when`，即使当前没有可投递同步消息，也不会因此启动 idle 回调。

#### 5.2.2 concurrent 的 outer loop：poll、idle 和 teardown

`nextConcurrent()` 不只调用一个 nextMessage。它必须和 native FD 的存活以及 IdleHandler 重入协调，固定 tag 第 881–928 行：

```java
    private Message nextConcurrent() {
        final long ptr = mPtr;
        if (ptr == 0) {
            return null;
        }

        mNextPollTimeoutMillis = 0;
        int pendingIdleHandlerCount = -1; // -1 only during first iteration
        while (true) {
            if (mNextPollTimeoutMillis != 0) {
                Binder.flushPendingCommands();
            }

            mMessageDirectlyQueued = false;
            nativePollOnce(ptr, mNextPollTimeoutMillis);

            Message msg = nextMessage(false, false);
            if (msg != null) {
                msg.markInUse();
                decAndTraceMessageCount();
                return msg;
            }

            // Prevent any race between quit()/nativeWake() and dispose()
            if (mWorkerShouldQuit) {
                setMptrTeardownAndWaitForRefsToDrop();
                dispose();
                return null;
            }

            synchronized (mIdleHandlersLock) {
                // If first time idle, then get the number of idlers to run.
                // Idle handles only run if the queue is empty or if the first message
                // in the queue (possibly a barrier) is due to be handled in the future.
                if (pendingIdleHandlerCount < 0
                        && isIdle()) {
                    pendingIdleHandlerCount = mIdleHandlers.size();
                }
                if (pendingIdleHandlerCount <= 0) {
                    // No idle handlers to run.  Loop and wait some more.
                    continue;
                }

                if (mPendingIdleHandlers == null) {
                    mPendingIdleHandlers = new IdleHandler[Math.max(pendingIdleHandlerCount, 4)];
                }
                mPendingIdleHandlers = mIdleHandlers.toArray(mPendingIdleHandlers);
            }
```

这里先 poll 再读取并发队列，第一次 timeout=0，因此不是先无条件睡眠。非零 timeout 前 flush Binder 命令，是为了让当前线程缓冲的 IPC 命令在睡眠之前送出，不是 Handler 把消息改走 Binder。

`mWorkerShouldQuit` 后先 `setMptrTeardownAndWaitForRefsToDrop()`，阻止新的 native 指针引用并等待既有访问释放，然后 dispose。若只写“quit 时 nativeDestroy”，就漏掉了生产者可能正执行 nativeWake 的 use-after-free 竞争。

IdleHandler 列表在 `mIdleHandlersLock` 下快照，真正 `queueIdle()` 在锁外。返回 false 或回调异常后移除；回调结束把 timeout 重置为 0，再检查回调期间可能入队的消息。不能在持列表锁时调用用户代码。

#### 5.2.3 并发发布的真实字段与状态

Combined 使用 StackNode 家族表达消息/活动/休眠/退出状态。`enqueueMessageConcurrent()` 检查 in-use 后转到 `enqueueMessageUnchecked()`；真正序号、直插、CAS 与唤醒分支在第 2875–2973 行：

```java
    private boolean enqueueMessageUnchecked(@NonNull Message msg, long when) {
        long seq = when != 0 ? ((long) sNextInsertSeq.getAndAdd(this, 1L) + 1L)
                : ((long) sNextFrontInsertSeq.getAndAdd(this, -1L) - 1L);
        msg.when = when;
        msg.insertSeq = seq;
        msg.markInUse();
        incAndTraceMessageCount(msg, when);

        if (DEBUG) {
            Log.d(TAG_C, "Insert message"
                    + " what: " + msg.what
                    + " when: " + msg.when
                    + " seq: " + msg.insertSeq
                    + " barrier: " + isBarrier(msg)
                    + " async: " + msg.isAsynchronous()
                    + " now: " + SystemClock.uptimeMillis());
        }

        /* If we are running on the looper thread we can add directly to the priority queue */
        if (Thread.currentThread() == mLooperThread) {
            if (getQuitting()) {
                logDeadThread(msg);
                return false;
            }

            insertIntoPriorityQueue(msg);
            /*
             * We still need to do this even though we are the current thread,
             * otherwise next() may sleep indefinitely.
             */
            if (!mMessageDirectlyQueued) {
                mMessageDirectlyQueued = true;
                nativeWake(mPtr);
            }
            return true;
        }

        MessageNode node = new MessageNode(msg);
        while (true) {
            StackNode old = (StackNode) sState.getVolatile(this);
            boolean wakeNeeded;
            boolean inactive;

            node.mNext = old;
            switch (old.getNodeType()) {
                case STACK_NODE_ACTIVE:
                    /*
                     * The worker thread is currently active and will process any elements added to
                     * the stack before parking again.
                     */
                    node.mBottomOfStack = (StateNode) old;
                    inactive = false;
                    node.mWokeUp = true;
                    wakeNeeded = false;
                    break;

                case STACK_NODE_PARKED:
                    node.mBottomOfStack = (StateNode) old;
                    inactive = true;
                    node.mWokeUp = true;
                    wakeNeeded = true;
                    break;

                case STACK_NODE_TIMEDPARK:
                    node.mBottomOfStack = (StateNode) old;
                    inactive = true;
                    wakeNeeded = mStackStateTimedPark.mWhenToWake >= msg.when;
                    node.mWokeUp = wakeNeeded;
                    break;

                case STACK_NODE_QUITTING:
                    logDeadThread(msg);
                    decAndTraceMessageCount();
                    return false;

                default:
                    MessageNode oldMessage = (MessageNode) old;

                    node.mBottomOfStack = oldMessage.mBottomOfStack;
                    int bottomType = node.mBottomOfStack.getNodeType();
                    inactive = bottomType >= STACK_NODE_PARKED;
                    wakeNeeded = (bottomType == STACK_NODE_TIMEDPARK
                            && mStackStateTimedPark.mWhenToWake >= node.mMessage.when
                            && !oldMessage.mWokeUp);
                    node.mWokeUp = oldMessage.mWokeUp || wakeNeeded;
                    break;
            }
            if (sState.compareAndSet(this, old, node)) {
                if (inactive) {
                    if (wakeNeeded) {
                        concurrentWake();
                    } else {
                        mMessageCounts.incrementQueued();
                    }
                }
                return true;
            }
        }
    }
```

普通入队递增序号保证相同时间 FIFO；队首发送用另一组递减序号保证 LIFO。排序键并非只有 when：否则多生产者具有相同时间戳时顺序不稳定，队首语义也会被破坏。

CAS 的关键是“比较看到的旧 top，再把新节点连到这个旧 top 并发布”。遇到 quitting 状态必须失败并回收，不能把消息插到关闭队列后仍返回成功。Combined 的排序容器是 `ConcurrentSkipListSet`，不是消费者私有堆；Looper 自己入队可以直接插入，其他线程还可能并发查询/删除，所以 first() 也要处理并发移除导致的空集合。Deli 的 MessageHeap 是另一实现，不能混用其所有权模型。

Deli 将发布、heap 和 freelist 管理封装在 MessageStack：取消消息的逻辑移除与实际节点回收分开。仅把它叫无锁链表会漏掉堆排序、删除扫描、引用回收及 native 指针保护。

#### 5.2.4 退出、取消与屏障的应用边界

| 操作 | 发生什么 | 不保证什么 |
|------|----------|------------|
| send/post 返回 true | 消息被接受到队列 | 不保证进程存活至执行，也不保证回调成功 |
| removeCallbacks(r) | 匹配同一 Runnable 实例的排队工作 | 不停止已经进入 run() 的工作 |
| removeCallbacksAndMessages(token) | 删除匹配 token/obj 的待投递项 | 不能代替线程中阻塞 IO 的取消 |
| quit() | 停止接收，清理待投递消息并唤醒消费者退出 | 不会中断当前回调 |
| quitSafely() | 保留已到期的可执行工作、丢弃未来工作 | 不保证越过屏障执行被挡住的同步消息 |
| removeSyncBarrier(token) | 删除对应隐藏屏障，必要时唤醒 | 不代表应用能安全反射操纵系统屏障 |

例如组件销毁时，可先停止外部生产者，再移除本组件 token 的排队工作，取消正在执行的 IO，最后 quitSafely。只 quit 不停止生产源会让后续 post 返回 false，调用者必须处理，而不能无限重试。

---

## 6. Message 详解

### 6.1 消息池流程图

下图仅针对 Legacy 模式。`Message.obtain()` 首先判断 `MessageQueue.getUseConcurrent()`，并发模式直接 new Message；不读取 sPool。

```text
  Message.obtain():
  ────────────────────────────────────────────────────────────────────────
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  sPool != null?   Yes → 从池中取出, sPool = sPool.next                 │
  │                   No  → new Message()                                   │
  └─────────────────────────────────────────────────────────────────────────┘

  msg.recycleUnchecked():
  ────────────────────────────────────────────────────────────────────────
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 清空消息字段                                                        │
  │  2. sPoolSize < 50?  Yes → 放入池中: sPool = msg                       │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Message 源码分析

关键字段分三类：业务数据 `what/arg1/arg2/obj/data`，分发目标 `target/callback/when`，队列协议 `flags/next/prev/insertSeq` 等。业务字段可以在回收时释放，但并发移除仍可能持有旧 Message，因此协议字段不能按 Legacy 的方式全部重置并复用。

实际 `recycleUnchecked()`（第 388–406 行）：

```java
    void recycleUnchecked() {
        if (MessageQueue.getUseConcurrent()) {
            // Once a message has entered the queue, it may still be referenced by removing threads
            // forever and may not be recycled. As such, its flags field must not be cleared.
            clearReferenceFields();

            // However, we should still mark this as in-use.
            markInUse();
        } else {
            clear();
            synchronized (sPoolSync) {
                if (sPoolSize < MAX_POOL_SIZE) {
                    next = sPool;
                    sPool = this;
                    sPoolSize++;
                }
            }
        }
    }
```

- **Legacy：** `clear()` 设置 `flags = FLAG_IN_USE`，清业务字段/目标/时间等，再持 `sPoolSync` 将对象放回至多 50 个的全局池。下次 obtain 取出才把 flags 清零并递减计数。
- **Concurrent：** `clearReferenceFields()` 清理 obj/target/callback 等引用（其中使用 sentinel，屏障 target=null 特殊保留），而 flags 和链接仍供移除线程使用；随后 markInUse，不加入全局池。
- 这个差异是防止取消扫描误认被重新利用的对象，不是偶然的性能选择。不能在并发模式从反射字段假定看到“纯空消息”，更不能将其重新发送。

`Message.recycle()` 在 in-use 时抛异常；Looper/队列内部的 recycleUnchecked 才能处理已入队对象。Message.obtain(orig) 是按规定字段复制，不代表 native/Binder 资源或 obj 的深拷贝。

#### 回收状态不能只清 payload

实际 Message 对象池取出步骤（固定 tag 第 225–239 行）同时维护 flags 与计数：

```java
    public static Message obtain() {
        if (!MessageQueue.getUseConcurrent()) {
            synchronized (sPoolSync) {
                if (sPool != null) {
                    Message m = sPool;
                    sPool = m.next;
                    m.next = null;
                    m.flags = 0; // clear in-use flag
                    sPoolSize--;
                    return m;
                }
            }
        }
        return new Message();
    }
```

如果漏掉 sPoolSize--，池容量记账会一直增长到上限，后续对象不再入池；如果回收时把 flags 清零，已经回收的 Message 会被误认为可再次发送。两个问题都不能用“这是简化代码”掩盖。

---

## 7. Handler 详解

### 7.1 Handler 发送消息流程图

```text
  Handler.sendMessage(msg)
         │
         ▼
  sendMessageDelayed(msg, 0)
         │
         ▼
  sendMessageAtTime(msg, uptimeMillis)
         │
         │  msg.target = this
         │
         ▼
  mQueue.enqueueMessage(msg, when)
         │
         ▼
  发布到选定队列，必要时 nativeWake()
```

### 7.2 Handler 发送消息源码

```java
/**
 * Handler 发送消息源码 - 对应上面的流程图
 */
public class Handler {

    final MessageQueue mQueue;

    public final boolean sendMessage(Message msg) {
        return sendMessageDelayed(msg, 0);
    }

    public final boolean sendMessageDelayed(Message msg, long delayMillis) {
        if (delayMillis < 0) delayMillis = 0;
        return sendMessageAtTime(msg, SystemClock.uptimeMillis() + delayMillis);
    }

    public boolean sendMessageAtTime(Message msg, long uptimeMillis) {
        return enqueueMessage(mQueue, msg, uptimeMillis);
    }

    private boolean enqueueMessage(MessageQueue queue, Message msg, long uptimeMillis) {
        msg.target = this;
        msg.workSourceUid = ThreadLocalWorkSource.getUid();
        if (mAsynchronous) msg.setAsynchronous(true);
        return queue.enqueueMessage(msg, uptimeMillis);
    }

    public final boolean post(Runnable r) {
        return sendMessageDelayed(getPostMessage(r), 0);
    }

    private static Message getPostMessage(Runnable r) {
        Message m = Message.obtain();
        m.callback = r;
        return m;
    }
}
```

### 7.3 Handler.dispatchMessage() 流程图

```text
  Handler.dispatchMessage(msg)
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. msg.callback != null?   Yes → handleCallback(msg); return          │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. mCallback != null?      Yes → mCallback.handleMessage(msg)         │
  │                                    返回 true → return                   │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. handleMessage(msg)  // 默认处理，子类重写                           │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 7.4 Handler.dispatchMessage() 源码

```java
/**
 * 分发消息 - 对应上面的流程图
 */
public void dispatchMessage(Message msg) {
    if (msg.callback != null) {
        handleCallback(msg);
    } else {
        if (mCallback != null) {
            if (mCallback.handleMessage(msg)) {
                return;
            }
        }
        handleMessage(msg);
    }
}

private static void handleCallback(Message message) {
    message.callback.run();
}

public void handleMessage(Message msg) {
    // 子类重写
}
```

---

## 8. Native 层实现

### 8.1 epoll 机制流程图

```text
  nativePollOnce(ptr, timeout)
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  epoll_wait(mEpollFd, events, maxEvents, timeout)                       │
  │       ├── 超时: 返回                                                    │
  │       ├── 有事件: 处理                                                  │
  │       └── 被唤醒: 返回                                                  │
  └─────────────────────────────────────────────────────────────────────────┘

  nativeWake(ptr)
          │
          ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  uint64_t inc = 1; write(mWakeEventFd, &inc, sizeof(inc)); // eventfd 需要 8 字节                          │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 9. 同步屏障机制

### 9.1 同步屏障流程图

```text
插入同步屏障后:

  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
  │ barrier │───►│ async   │───►│ sync    │───►│ sync    │
  │ target= │    │ when=150│    │ when=100│    │ when=200│
  │  null   │    │         │    │         │    │         │
  └─────────┘    └─────────┘    └─────────┘    └─────────┘
       │               │
       │               ▼
       │          跳过同步消息
       │          只执行已到期的异步消息
```

### 9.2 同步屏障源码

以下是 Legacy 分支的结构示意（省略 token 分配和摘链），`postSyncBarrier`/`removeSyncBarrier` 是平台隐藏 API，不是应用 SDK API。屏障按时间插入、以 token 移除；越过屏障不能越过异步消息自身的 when。

```java
// 添加同步屏障
public int postSyncBarrier() {
    synchronized (this) {
        final Message msg = Message.obtain();
        msg.arg1 = token;  // target = null 表示屏障
        // 按时间插入...
        return token;
    }
}

// 移除同步屏障
public void removeSyncBarrier(int token) {
    synchronized (this) {
        // 找到并移除屏障...
    }
}
```

---

## 10. IdleHandler 机制

Legacy 在队列为空或队首消息尚未到期时准备 IdleHandler 快照，并在锁外回调；到期屏障挡住同步消息不等于 idle。返回 true 表示保留到下一次空闲机会，并非在空闲期间持续忙轮询。

```java
public static interface IdleHandler {
    boolean queueIdle();  // 返回 true 继续监听，false 移除
}

// 使用示例
Looper.myQueue().addIdleHandler(() -> {
    // 空闲时执行
    return false;  // 只执行一次
});
```

---

## 11. HandlerThread

`HandlerThread.run()` 依次记录 TID、`Looper.prepare()`、持锁发布 `mLooper` 并 `notifyAll()`、设置线程优先级、调用 `onLooperPrepared()`，最后进入 `Looper.loop()`。`getLooper()` 在未启动/已结束时返回 null，在已启动但 Looper 未发布时等待，并在源码中捕获 InterruptedException。

```java
// 应用侧示例，不覆盖 HandlerThread 的内部生命周期。
HandlerThread worker = new HandlerThread("worker", Process.THREAD_PRIORITY_BACKGROUND);
worker.start();
Handler handler = new Handler(worker.getLooper());
handler.post(() -> { /* 串行短任务；耗时操作要支持取消 */ });
// 所属组件结束时：quitSafely 处理已到期消息，丢弃未来消息；不会中断正在执行的回调。
worker.quitSafely();
```

---

## 12. 主线程消息循环

Android 17 的 Activity 生命周期不是 `H.LAUNCH_ACTIVITY = 100` 一组旧消息号：

```text
ApplicationThread.scheduleTransaction(ClientTransaction)
  -> ClientTransactionHandler.scheduleTransaction()
  -> H.EXECUTE_TRANSACTION
  -> TransactionExecutor.execute(transaction)
  -> LaunchActivityItem / ResumeActivityItem / PauseActivityItem ...
```

`H.BIND_APPLICATION -> handleBindApplication()` 负责绑定应用、创建 Application 并调用初始化逻辑。事务对象表达 Activity 生命周期和 callback 顺序，Handler 负责把事务分发到主线程；不要把事务项等同于旧版每个生命周期一个 H 消息。

---

## 13. 常见问题

### 13.1 loop() 为什么不会卡死？

```text
关键在于 nativePollOnce():
1. 没有消息时，线程在 epoll_wait() 中阻塞
2. 阻塞状态不消耗 CPU
3. 有新消息时，通过 nativeWake() 唤醒
4. 正常空闲等待不是 ANR；若输入/组件工作长期无法执行，仍可能出现 ANR
```

### 13.2 Handler 内存泄漏

```java
// ❌ 错误
Handler handler = new Handler() {
    @Override
    public void handleMessage(Message msg) { }
};

// ✅ 正确
private static class SafeHandler extends Handler {
    private final WeakReference<Activity> ref;

        SafeHandler(Activity activity) {
            super(Looper.getMainLooper());
            ref = new WeakReference<>(activity);
        }

    @Override
    public void handleMessage(Message msg) {
        Activity activity = ref.get();
        if (activity != null) { }
    }
}

// onDestroy 中移除消息
handler.removeCallbacksAndMessages(null);
```

### 13.3 为什么 MessageQueue.next() 需要加锁？

以下共享链表竞争分析专指 Legacy 分支；Combined/Deli 的发布和消费协议见第 5 章。单消费者本身不会让生产者的写入自动安全。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MessageQueue 的并发场景                                  │
└─────────────────────────────────────────────────────────────────────────────┘

   主线程 (消费消息)                    子线程 (生产消息)
        │                                   │
        ▼                                   ▼
  ┌──────────────┐                  ┌──────────────┐
  │ queue.next() │                  │ enqueueMessage│
  │  读取 mMessages│                  │  写入 mMessages│
  └──────────────┘                  └──────────────┘
        │                                   │
        │     同时访问同一个链表!           │
        └───────────────────────────────────┘
```

#### 不加锁会导致的问题

**问题1: 数据竞争**
```text
  主线程: 读取 mMessages.next
  子线程: 修改 mMessages.next
  结果: 主线程可能读到旧值或新值，行为不可预测
```

**问题2: 链表损坏**
```text
  初始状态: A → B → C

  时序:
  t1: 主线程执行 next()，准备取出 A
      msg = mMessages;        // msg = A
      mMessages = msg.next;   // 准备执行，但还没执行

  t2: 子线程执行 enqueueMessage(D)，D 插入头部
      D.next = mMessages;     // D.next = A
      mMessages = D;          // mMessages = D

  t3: 主线程继续
      mMessages = msg.next;   // mMessages = B

  结果: D 丢失！链表变成 B → C，D 消失了
```

**问题3: 消息丢失或重复处理**
```text
  - 若没有 in-use 检查，生产者可能重复入队同一 Message
  - 新插入的消息被跳过
  - 消息顺序错乱
```

#### synchronized 的作用

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    synchronized (this) 的作用                               │
└─────────────────────────────────────────────────────────────────────────────┘

1. 互斥访问
   - 同一时刻只有一个线程能操作 mMessages 链表
   - 主线程读的时候，子线程不能写
   - 子线程写的时候，主线程不能读

2. 内存可见性
   - unlock happens-before 后续对同一监视器的 lock
   - 防止 CPU 缓存导致的数据不一致

3. 原子操作
   - 取出消息是一组操作，不可分割
   - 相对使用同一把锁的访问者互斥；异常不会回滚已完成的修改
```

#### 为什么 nativePollOnce 在锁外面？

```java
for (;;) {
    nativePollOnce(mPtr, nextPollTimeoutMillis);  // ← 锁外面！

    synchronized (this) {  // ← 锁里面
        // 操作链表
    }
}
```

**原因：**
1. `nativePollOnce` 是阻塞操作，可能等待很长时间
2. 如果在锁内阻塞，子线程的 `enqueueMessage` 也会被阻塞
3. 把阻塞放在锁外面，子线程可以随时插入消息并唤醒主线程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         正确的加锁粒度                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  主线程
    │
    ▼
  nativePollOnce() ← 阻塞在这里，不持锁
    │
    │  (子线程可以执行 enqueueMessage，获取锁，插入消息，nativeWake 唤醒)
    │
    ▼  被唤醒
  synchronized (this) {  ← 获取锁
    取出消息              ← 快速操作，持锁时间短
  }  ← 释放锁
    │
    ▼
  分发消息 (不持锁)

核心原则: 链表操作必须加锁，阻塞等待不能持锁!
```

---

## 14. 总结

```text
核心组件:
- ThreadLocal: 线程局部存储 Looper
- Looper: 消息循环 (for(;;) + epoll)
- MessageQueue: Legacy 有序链表或并发队列，按到期时间选择消息
- Message: Legacy 池复用；并发模式清引用但不复用入队对象
- Handler: 发送/处理消息

工作流程:
1. prepare() → 创建 Looper 和 MessageQueue
2. loop() → 无限循环取消息
3. sendMessage() → 入队 + 唤醒
4. dispatchMessage() → 处理消息
```

---

*本文档由 OpenClaw 生成*


## 固定版本源码索引

本文平台实现基线为 `android-17.0.0_r1`。下列函数用于定位正文分析；代码标为“节选”时省略无关监控，标为“示意”时不是源码逐字复制。

- [队列构建选择](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/Android.bp#252)：`messagequeue-gen`。
- [Combined 队列](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/CombinedMessageQueue/MessageQueue.java)：`getUseConcurrent; nextLegacy; nextConcurrent; enqueueMessageConcurrent`。
- [Deli 队列](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/CombinedDeliMessageQueue/MessageQueue.java)：`enqueueMessage; next; nextMessage`。
- [分发与回收](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/Message.java)：`obtain; recycleUnchecked`。
- [Looper](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/Looper.java)：`loop; loopOnce`。
- [Handler](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/Handler.java)：`enqueueMessage; dispatchMessage`。
- [主线程](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java)：`H.handleMessage; handleBindApplication`。
