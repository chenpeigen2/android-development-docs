# Android Handler 机制完全指南

> 作者：OpenClaw | 日期：2026-03-08

---

## 目录

1. [概述](#1-概述)
   - 1.1 [核心组件](#11-核心组件)
2. [整体架构](#2-整体架构)
   - 2.1 [组件关系图](#21-组件关系图)
   - 2.2 [完整工作流程](#22-完整工作流程)
   - 2.3 [超详细完整流程图](#23-超详细完整流程图)
3. [ThreadLocal 详解](#3-threadlocal-详解)
   - 3.1 [ThreadLocal 原理图](#31-threadlocal-原理图)
   - 3.2 [ThreadLocal.get() 流程图](#32-threadlocalget-流程图)
   - 3.3 [ThreadLocal 源码分析](#33-threadlocal-源码分析)
   - 3.4 [Looper.prepare() 流程图](#34-looperprepare-流程图)
   - 3.5 [Looper 中的 ThreadLocal 源码](#35-looper-中的-threadlocal-源码)
4. [Looper 详解](#4-looper-详解)
   - 4.1 [Looper.loop() 流程图](#41-looperloop-流程图)
   - 4.2 [Looper 源码分析](#42-looper-源码分析)
   - 4.3 [主线程初始化流程图](#43-主线程初始化流程图)
   - 4.4 [主线程初始化源码](#44-主线程初始化源码)
5. [MessageQueue 详解](#5-messagequeue-详解)
   - 5.1 [MessageQueue.next() 流程图](#51-messagequeuenext-流程图)
   - 5.2 [MessageQueue 源码分析](#52-messagequeue-源码分析)
6. [Message 详解](#6-message-详解)
   - 6.1 [消息池流程图](#61-消息池流程图)
   - 6.2 [Message 源码分析](#62-message-源码分析)
7. [Handler 详解](#7-handler-详解)
   - 7.1 [Handler 发送消息流程图](#71-handler-发送消息流程图)
   - 7.2 [Handler 发送消息源码](#72-handler-发送消息源码)
   - 7.3 [Handler.dispatchMessage() 流程图](#73-handlerdispatchmessage-流程图)
   - 7.4 [Handler.dispatchMessage() 源码](#74-handlerdispatchmessage-源码)
8. [Native 层实现](#8-native-层实现)
   - 8.1 [epoll 机制流程图](#81-epoll-机制流程图)
9. [同步屏障机制](#9-同步屏障机制)
   - 9.1 [同步屏障流程图](#91-同步屏障流程图)
   - 9.2 [同步屏障源码](#92-同步屏障源码)
10. [IdleHandler 机制](#10-idlehandler-机制)
11. [HandlerThread](#11-handlerthread)
12. [主线程消息循环](#12-主线程消息循环)
13. [常见问题](#13-常见问题)
    - 13.1 [loop() 为什么不会卡死？](#131-loop-为什么不会卡死)
    - 13.2 [Handler 内存泄漏](#132-handler-内存泄漏)
    - 13.3 [为什么 MessageQueue.next() 需要加锁？](#133-为什么-messagequeuenext-需要加锁)
14. [总结](#14-总结)

---

## 1. 概述

Handler 是 Android 消息机制的核心，实现了线程间的异步通信。

### 1.1 核心组件

| 组件 | 作用 | 关键点 |
|------|------|--------|
| **ThreadLocal** | 线程局部变量存储 | 每个线程有独立的 Looper |
| **Looper** | 消息循环器 | 不断从队列取消息，无限循环 |
| **MessageQueue** | 消息队列 | 单链表结构，按时间排序 |
| **Message** | 消息对象 | 包含 what、obj、when、target |
| **Handler** | 消息发送/处理 | 绑定 Looper，发送和处理消息 |

---

## 2. 整体架构

### 2.1 组件关系图

```
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
                            │  │   Message 链表            │  │
                            │  └───────────┬───────────────┘  │
                            │              │                  │
                            │              ▼                  │
                            │  ┌───────────────────────────┐  │
                            │  │        Handler            │  │
                            │  └───────────────────────────┘  │
                            └─────────────────────────────────┘
```

### 2.2 完整工作流程

```
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

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              Android Handler 机制超详细完整流程图                                │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════════════
                                          一、应用启动阶段
═══════════════════════════════════════════════════════════════════════════════════════════════════

  Zygote Fork 进程
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  ActivityThread.main()                                                                     │
  │  源码位置: frameworks/base/core/java/android/app/ActivityThread.java                       │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘
         │
         │  ① Looper.prepareMainLooper()
         ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  Looper.prepareMainLooper()                                                                │
  │  源码位置: frameworks/base/core/java/android/os/Looper.java                                │
  │                                                                                            │
  │  synchronized (Looper.class) {                                                             │
  │      prepare(false);  // false = 主线程不允许退出                                           │
  │      sMainLooper = myLooper();                                                             │
  │  }                                                                                         │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘
         │
         │  ② Looper.prepare(false)
         ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  Looper.prepare(quitAllowed)                                                               │
  │                                                                                            │
  │  if (sThreadLocal.get() != null) {                                                         │
  │      throw new RuntimeException("Only one Looper may be created per thread");              │
  │  }                                                                                         │
  │  sThreadLocal.set(new Looper(quitAllowed));  // 创建 Looper 并存入 ThreadLocal            │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘
         │
         │  ③ new Looper(false)
         ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  Looper 构造函数                                                                           │
  │                                                                                            │
  │  private Looper(boolean quitAllowed) {                                                     │
  │      mQueue = new MessageQueue(quitAllowed);  // 创建消息队列                              │
  │      mThread = Thread.currentThread();        // 记录当前线程                              │
  │  }                                                                                         │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘
         │
         │  ④ new MessageQueue(false)
         ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  MessageQueue 构造函数                                                                     │
  │  源码位置: frameworks/base/core/java/android/os/MessageQueue.java                          │
  │                                                                                            │
  │  MessageQueue(boolean quitAllowed) {                                                       │
  │      mQuitAllowed = quitAllowed;                                                           │
  │      mPtr = nativeInit();  // 初始化 Native 层，创建 epoll 实例                            │
  │  }                                                                                         │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘
         │
         │  ⑤ nativeInit() - Native 层
         ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  NativeInit() - C++ 层                                                                     │
  │  源码位置: frameworks/base/core/jni/android_os_MessageQueue.cpp                            │
  │                                                                                            │
  │  static jlong android_os_MessageQueue_nativeInit(JNIEnv* env, jclass clazz) {              │
  │      NativeMessageQueue* nativeMessageQueue = new NativeMessageQueue();                    │
  │      nativeMessageQueue->incStrong(env);                                                   │
  │      return reinterpret_cast<jlong>(nativeMessageQueue);                                   │
  │  }                                                                                         │
  │                                                                                            │
  │  NativeMessageQueue::NativeMessageQueue() {                                                │
  │      mLooper = new Looper(false);  // 创建 Native Looper                                   │
  │      mLooper->rebuildEpoll();       // 创建 epoll 实例                                     │
  │  }                                                                                         │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘
         │
         │  ⑥ ActivityThread.attach()
         ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  thread.attach(false, startSeq)                                                            │
  │  - 与 AMS 建立连接                                                                         │
  │  - 创建 Application                                                                        │
  │  - 调用 Application.onCreate()                                                             │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘
         │
         │  ⑦ Looper.loop() - 进入消息循环
         ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  ═══════════════════════════════════════════════════════════════════════════════════════   │
  │                                    从这里开始无限循环                                        │
  │  ═══════════════════════════════════════════════════════════════════════════════════════   │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════════════════════
                                       二、消息循环阶段 (Looper.loop)
═══════════════════════════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  Looper.loop()                                                                             │
  │  源码位置: frameworks/base/core/java/android/os/Looper.java                                │
  │                                                                                            │
  │  public static void loop() {                                                               │
  │      final Looper me = myLooper();  // 从 ThreadLocal 获取当前线程的 Looper               │
  │      final MessageQueue queue = me.mQueue;                                                 │
  │                                                                                            │
  │      for (;;) {  // ═══════════════════════════════════════════════════════════════════   │
  │  ┌───────────────────────────────────────────────────────────────────────────────────────┐│
  │  │                                                                                       ││
  │  │       Message msg = queue.next();  // 取出消息，可能阻塞                              ││
  │  │               │                                                                       ││
  │  │               ▼                                                                       ││
  │  │  ┌─────────────────────────────────────────────────────────────────────────────────┐ ││
  │  │  │  MessageQueue.next()                                                            │ ││
  │  │  │  源码位置: frameworks/base/core/java/android/os/MessageQueue.java               │ ││
  │  │  │                                                                                 │ ││
  │  │  │  Message next() {                                                               │ ││
  │  │  │      int nextPollTimeoutMillis = 0;                                             │ ││
  │  │  │      for (;;) {                                                                 │ ││
  │  │  │          // 1. Native 层阻塞等待                                                │ ││
  │  │  │          nativePollOnce(mPtr, nextPollTimeoutMillis);                          │ ││
  │  │  │                           │                                                     │ ││
  │  │  │                           ▼                                                     │ ││
  │  │  │          ┌───────────────────────────────────────────────────────────────────┐  │ ││
  │  │  │          │  nativePollOnce → NativeMessageQueue.pollOnce()                  │  │ ││
  │  │  │          │                    │                                              │  │ ││
  │  │  │          │                    ▼                                              │  │ ││
  │  │  │          │  Looper::pollOnce() (Native C++)                                  │  │ ││
  │  │  │          │  源码位置: system/core/libutils/Looper.cpp                        │  │ ││
  │  │  │          │                    │                                              │  │ ││
  │  │  │          │                    ▼                                              │  │ ││
  │  │  │          │  epoll_wait(mEpollFd, ...)                                        │  │ ││
  │  │  │          │  - 没有消息: 线程阻塞，不消耗 CPU                                  │  │ ││
  │  │  │          │  - 有消息到达: nativeWake() 唤醒，epoll_wait 返回                  │  │ ││
  │  │  │          └───────────────────────────────────────────────────────────────────┘  │ ││
  │  │  │                           │                                                     │ ││
  │  │  │                           ▼                                                     │ ││
  │  │  │          synchronized (this) {  // 加锁                                        │ ││
  │  │  │              final long now = SystemClock.uptimeMillis();                      │ ││
  │  │  │              Message msg = mMessages;  // 链表头                               │ ││
  │  │  │                                                                                    │ ││
  │  │  │              // 2. 检查同步屏障                                                  │ ││
  │  │  │              if (msg != null && msg.target == null) {                           │ ││
  │  │  │                  // 遇到屏障，跳过同步消息，找异步消息                          │ ││
  │  │  │                  do {                                                           │ ││
  │  │  │                      msg = msg.next;                                            │ ││
  │  │  │                  } while (msg != null && !msg.isAsynchronous());                │ ││
  │  │  │              }                                                                   │ ││
  │  │  │                                                                                    │ ││
  │  │  │              // 3. 处理消息                                                      │ ││
  │  │  │              if (msg != null) {                                                  │ ││
  │  │  │                  if (now < msg.when) {                                           │ ││
  │  │  │                      // 消息时间未到，计算等待时间                              │ ││
  │  │  │                      nextPollTimeoutMillis = (int)(msg.when - now);              │ ││
  │  │  │                  } else {                                                        │ ││
  │  │  │                      // 取出消息                                                 │ ││
  │  │  │                      mMessages = msg.next;                                       │ ││
  │  │  │                      msg.next = null;                                            │ ││
  │  │  │                      return msg;  // ← 返回消息                                  │ ││
  │  │  │                  }                                                               │ ││
  │  │  │              } else {                                                            │ ││
  │  │  │                  nextPollTimeoutMillis = -1;  // 没有消息，无限等待              │ ││
  │  │  │              }                                                                   │ ││
  │  │  │                                                                                    │ ││
  │  │  │              // 4. 处理 IdleHandler (空闲回调)                                   │ ││
  │  │  │              if (pendingIdleHandlerCount < 0 && 没有消息) {                      │ ││
  │  │  │                  // 执行空闲回调...                                              │ ││
  │  │  │              }                                                                   │ ││
  │  │  │          }  // synchronized 结束                                                 │ ││
  │  │  │      }  // for (;;) 结束                                                          │ ││
  │  │  │  }  // next() 结束                                                                │ ││
  │  │  └─────────────────────────────────────────────────────────────────────────────────┘  │ ││
  │  │               │                                                                       │ ││
  │  │               ▼                                                                       │ ││
  │  │          if (msg == null) {                                                           │ ││
  │  │              return;  // 队列退出，loop() 结束                                        │ ││
  │  │          }                                                                            │ ││
  │  │               │                                                                       │ ││
  │  │               ▼                                                                       │ ││
  │  │          // 5. 分发消息给 Handler                                                    │ ││
  │  │          msg.target.dispatchMessage(msg);                                             │ ││
  │  │          // msg.target 就是发送这条消息的 Handler                                    │ ││
  │  │               │                                                                       │ ││
  │  │               ▼                                                                       │ ││
  │  │          // 6. 回收消息到消息池                                                      │ ││
  │  │          msg.recycleUnchecked();                                                      │ ││
  │  │               │                                                                       │ ││
  │  │               └──────────────────────────────────────────────────────────────────────►││
  │  │                                      继续下一次循环                                   │ ││
  │  │                                                                                       ││
  │  │  }  // for (;;) 循环结束                                                              ││
  │  │  }  // loop() 方法结束                                                                ││
  │  └───────────────────────────────────────────────────────────────────────────────────────┘│
  │  }                                                                                         │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════════════════════
                                       三、发送消息阶段 (子线程 → 主线程)
═══════════════════════════════════════════════════════════════════════════════════════════════════

  子线程 (Thread-2)                                      主线程 (MainThread)
       │                                                       │
       │  handler.sendMessage(msg)                             │
       │         │                                             │
       ▼         │                                             │
  ┌─────────────────────────────────────────┐                  │
  │  Handler.sendMessage(msg)               │                  │
  │  源码: android/os/Handler.java          │                  │
  │                                         │                  │
  │  public final boolean sendMessage(Message msg) {            │
  │      return sendMessageDelayed(msg, 0);                     │
  │  }                                         │              │
  └─────────────────────────────────────────┘                  │
       │         │                                             │
       │         ▼                                             │
  ┌─────────────────────────────────────────┐                  │
  │  sendMessageDelayed(msg, 0)             │                  │
  │                                         │                  │
  │  return sendMessageAtTime(msg,          │                  │
  │      SystemClock.uptimeMillis() + delayMillis);            │
  └─────────────────────────────────────────┘                  │
       │         │                                             │
       │         ▼                                             │
  ┌─────────────────────────────────────────┐                  │
  │  sendMessageAtTime(msg, uptimeMillis)   │                  │
  │                                         │                  │
  │  return enqueueMessage(mQueue, msg, uptimeMillis);         │
  └─────────────────────────────────────────┘                  │
       │         │                                             │
       │         ▼                                             │
  ┌─────────────────────────────────────────┐                  │
  │  enqueueMessage(queue, msg, when)       │                  │
  │                                         │                  │
  │  msg.target = this;  // 设置 Handler    │                  │
  │  return queue.enqueueMessage(msg, when);│                  │
  └─────────────────────────────────────────┘                  │
       │         │                                             │
       │         ▼                                             │
  ┌─────────────────────────────────────────┐                  │
  │  MessageQueue.enqueueMessage(msg, when) │                  │
  │  源码: android/os/MessageQueue.java     │                  │
  │                                         │                  │
  │  synchronized (this) {                  │                  │
  │      msg.when = when;                   │                  │
  │      msg.markInUse();                   │                  │
  │                                         │                  │
  │      // 按时间插入链表                  │                  │
  │      Message p = mMessages;             │                  │
  │      if (p == null || when < p.when) {  │                  │
  │          msg.next = p;                  │                  │
  │          mMessages = msg;  // 插入头部  │                  │
  │      } else {                           │                  │
  │          // 遍历找位置插入              │                  │
  │          for (;;) { ... }               │                  │
  │      }                                  │                  │
  │                                         │                  │
  │      if (needWake) {                    │                  │
  │          nativeWake(mPtr);  // ← 唤醒主线程              │
  │      }                                  │                  │
  │  }                                      │                  │
  └─────────────────────────────────────────┐                  │
       │         │                                             │
       │         │  nativeWake(mPtr)                           │
       │         │                                             │
       │         └─────────────────────────────────────────────►│
       │                                                       │
       │                                         ┌─────────────▼─────────────┐
       │                                         │  nativeWake()             │
       │                                         │                           │
       │                                         │  NativeMessageQueue::wake()│
       │                                         │        │                  │
       │                                         │        ▼                  │
       │                                         │  Looper::wake()           │
       │                                         │        │                  │
       │                                         │        ▼                  │
       │                                         │  write(mWakeEventFd, 1)   │
       │                                         │  // 写入 eventfd          │
       │                                         │  // epoll_wait 被唤醒!    │
       │                                         └───────────────────────────┘
       │                                                       │
       │                                                       ▼
       │                                         nativePollOnce() 返回
       │                                                       │
       │                                                       ▼
       │                                         queue.next() 返回 msg
       │                                                       │
       │                                                       ▼
       │                                         msg.target.dispatchMessage(msg)


═══════════════════════════════════════════════════════════════════════════════════════════════════
                                       四、处理消息阶段 (dispatchMessage)
═══════════════════════════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  Handler.dispatchMessage(msg)                                                              │
  │  源码位置: frameworks/base/core/java/android/os/Handler.java                               │
  │                                                                                            │
  │  public void dispatchMessage(Message msg) {                                                │
  │      // 1. 检查 Message 的 callback (post 方式)                                            │
  │      if (msg.callback != null) {                                                           │
  │          handleCallback(msg);  // 执行 Runnable                                            │
  │          return;                                                                           │
  │      }                                                                                     │
  │                                                                                            │
  │      // 2. 检查 Handler 的 mCallback                                                       │
  │      if (mCallback != null) {                                                              │
  │          if (mCallback.handleMessage(msg)) {                                               │
  │              return;  // Callback 处理了消息                                               │
  │          }                                                                                 │
  │      }                                                                                     │
  │                                                                                            │
  │      // 3. 默认处理方式                                                                    │
  │      handleMessage(msg);  // 子类重写此方法                                                 │
  │  }                                                                                         │
  │                                                                                            │
  │  // handleCallback 实现                                                                    │
  │  private static void handleCallback(Message message) {                                     │
  │      message.callback.run();  // 直接执行 Runnable                                         │
  │  }                                                                                         │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════════════════════
                                       五、消息回收阶段 (recycleUnchecked)
═══════════════════════════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │  Message.recycleUnchecked()                                                                │
  │  源码位置: frameworks/base/core/java/android/os/Message.java                                │
  │                                                                                            │
  │  void recycleUnchecked() {                                                                 │
  │      // 1. 清空所有字段                                                                    │
  │      flags = 0;                                                                            │
  │      what = 0;                                                                             │
  │      arg1 = 0;                                                                             │
  │      arg2 = 0;                                                                             │
  │      obj = null;                                                                           │
  │      replyTo = null;                                                                       │
  │      sendingUid = UID_NONE;                                                                │
  │      when = 0;                                                                             │
  │      target = null;                                                                        │
  │      callback = null;                                                                      │
  │      data = null;                                                                          │
  │                                                                                            │
  │      // 2. 放入消息池                                                                      │
  │      synchronized (sPoolSync) {                                                            │
  │          if (sPoolSize < MAX_POOL_SIZE) {  // MAX_POOL_SIZE = 50                          │
  │              next = sPool;                                                                 │
  │              sPool = this;  // 头插法加入池                                                │
  │              sPoolSize++;                                                                  │
  │          }                                                                                 │
  │      }                                                                                     │
  │  }                                                                                         │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════════════════════
                                       六、时序图 (完整交互)
═══════════════════════════════════════════════════════════════════════════════════════════════════

  时间轴    主线程                    子线程                   Native层
    │
    │  ┌──────────────────┐
    │  │ ActivityThread.  │
    │  │    main()        │
    │  └────────┬─────────┘
    │           │
    │           ▼
    │  ┌──────────────────┐
    │  │ Looper.prepare   │
    │  │ MainLooper()     │
    │  └────────┬─────────┘
    │           │
    │           ▼
    │  ┌──────────────────┐                                    ┌──────────────────┐
    │  │ new MessageQueue │ ─────────────────────────────────► │ nativeInit()     │
    │  └────────┬─────────┘                                    │ 创建 epoll       │
    │           │                                              └──────────────────┘
    │           ▼
    │  ┌──────────────────┐
    │  │ Looper.loop()    │
    │  │ for(;;) {        │◄─────────────────────────────────────────────────────┐
    │  └────────┬─────────┘                                                      │
    │           │                                                                │
    │           ▼                                                                │
    │  ┌──────────────────┐                                    ┌──────────────────┐
    │  │ queue.next()     │                                    │                  │
    │  │ nativePollOnce() │ ─────────────────────────────────► │ epoll_wait()     │
    │  └────────┬─────────┘                                    │ 阻塞等待...      │
    │           │                                              └──────────────────┘
    │           │ (阻塞中，等待消息...)
    │           │
    │           │              ┌──────────────────┐
    │           │              │ handler.post()   │
    │           │              │ 或 sendMessage() │
    │           │              └────────┬─────────┘
    │           │                       │
    │           │                       ▼
    │           │              ┌──────────────────┐
    │           │              │ enqueueMessage() │
    │           │              │ 插入消息链表     │
    │           │              └────────┬─────────┘
    │           │                       │
    │           │                       │                    ┌──────────────────┐
    │           │                       └───────────────────►│ nativeWake()     │
    │           │                                            │ write(eventfd)   │
    │           │                                            └────────┬─────────┘
    │           │                                                     │
    │           │◄────────────────────────────────────────────────────┘
    │           │              epoll_wait 被唤醒
    │           ▼
    │  ┌──────────────────┐
    │  │ next() 返回 msg  │
    │  └────────┬─────────┘
    │           │
    │           ▼
    │  ┌──────────────────┐
    │  │ dispatchMessage()│
    │  │ handleMessage()  │
    │  └────────┬─────────┘
    │           │
    │           ▼
    │  ┌──────────────────┐
    │  │ recycleUnchecked │
    │  │ 消息回收到池     │
    │  └────────┬─────────┘
    │           │
    │           └────────────────────────────────────────────────────────────►
    │                                      继续下一次循环
    │
    ▼
```

---

## 3. ThreadLocal 详解

### 3.1 ThreadLocal 原理图

```
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

```
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
  │  3. map == null?   Yes → 返回 null                                      │
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

```
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

```
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
 * Looper 完整源码分析 - 对应上面的流程图
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

```
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

```
  MessageQueue.next()
         │
         │◄──────────────────────────────────────────────────────────────┐
         ▼                                                              │
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. Native 层阻塞: nativePollOnce(mPtr, timeout)                       │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. synchronized (this) 加锁                                            │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. 检查同步屏障, 跳过同步消息                                          │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  4. msg != null && now >= msg.when → 取出消息返回                      │
  │     否则计算等待时间                                                    │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  5. 处理 IdleHandler (空闲时执行)                                       │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         └──────────────────────────────────────────────────────────────────►
```

### 5.2 MessageQueue 源码分析

```java
/**
 * MessageQueue 完整源码分析 - 对应上面的流程图
 */
public final class MessageQueue {
    
    Message mMessages;  // 链表头
    private long mPtr;  // Native 层指针
    
    private native void nativePollOnce(long ptr, int timeoutMillis);
    private native static void nativeWake(long ptr);
    
    Message next() {
        int nextPollTimeoutMillis = 0;
        
        for (;;) {
            // 1. Native 层阻塞
            nativePollOnce(mPtr, nextPollTimeoutMillis);
            
            synchronized (this) {
                final long now = SystemClock.uptimeMillis();
                Message msg = mMessages;
                
                // 2. 检查同步屏障
                if (msg != null && msg.target == null) {
                    do {
                        msg = msg.next;
                    } while (msg != null && !msg.isAsynchronous());
                }
                
                if (msg != null) {
                    if (now < msg.when) {
                        nextPollTimeoutMillis = (int)(msg.when - now);
                    } else {
                        // 取出消息
                        mMessages = msg.next;
                        msg.next = null;
                        return msg;
                    }
                } else {
                    nextPollTimeoutMillis = -1;
                }
                // 3. 处理 IdleHandler...
            }
        }
    }
    
    boolean enqueueMessage(Message msg, long when) {
        synchronized (this) {
            msg.when = when;
            
            Message p = mMessages;
            if (p == null || when == 0 || when < p.when) {
                // 插入头部
                msg.next = p;
                mMessages = msg;
            } else {
                // 按时间插入
                Message prev;
                for (;;) {
                    prev = p;
                    p = p.next;
                    if (p == null || when < p.when) break;
                }
                msg.next = p;
                prev.next = msg;
            }
            
            if (needWake) nativeWake(mPtr);
        }
        return true;
    }
}
```

---

## 6. Message 详解

### 6.1 消息池流程图

```
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

```java
/**
 * Message 源码分析 - 对应上面的流程图
 */
public final class Message {
    
    public int what;
    public int arg1;
    public int arg2;
    public Object obj;
    
    long when;
    Handler target;
    Runnable callback;
    Message next;
    
    private static Message sPool;
    private static final int MAX_POOL_SIZE = 50;
    
    public static Message obtain() {
        synchronized (sPoolSync) {
            if (sPool != null) {
                Message m = sPool;
                sPool = m.next;
                m.next = null;
                return m;
            }
        }
        return new Message();
    }
    
    void recycleUnchecked() {
        what = 0; arg1 = 0; arg2 = 0; obj = null;
        when = 0; target = null; callback = null;
        
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

---

## 7. Handler 详解

### 7.1 Handler 发送消息流程图

```
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
  按时间插入链表, 必要时 nativeWake()
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

```
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

```
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
  │  write(mWakeEventFd, "1")  // 唤醒 epoll_wait                          │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 9. 同步屏障机制

### 9.1 同步屏障流程图

```
插入同步屏障后:

  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
  │ barrier │───►│ async   │───►│ sync    │───►│ sync    │
  │ target= │    │ when=150│    │ when=100│    │ when=200│
  │  null   │    │         │    │         │    │         │
  └─────────┘    └─────────┘    └─────────┘    └─────────┘
       │               │
       │               ▼
       │          跳过同步消息
       │          直接执行异步消息
```

### 9.2 同步屏障源码

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

```java
public class HandlerThread extends Thread {
    
    Looper mLooper;
    
    @Override
    public void run() {
        Looper.prepare();
        synchronized (this) {
            mLooper = Looper.myLooper();
            notifyAll();
        }
        Looper.loop();
    }
    
    public Looper getLooper() {
        synchronized (this) {
            while (isAlive() && mLooper == null) {
                wait();
            }
        }
        return mLooper;
    }
}
```

---

## 12. 主线程消息循环

```java
class H extends Handler {
    public static final int LAUNCH_ACTIVITY = 100;
    public static final int PAUSE_ACTIVITY = 101;
    public static final int RESUME_ACTIVITY = 107;
    
    public void handleMessage(Message msg) {
        switch (msg.what) {
            case LAUNCH_ACTIVITY:
                handleLaunchActivity(...);
                break;
            // ...
        }
    }
}
```

---

## 13. 常见问题

### 13.1 loop() 为什么不会卡死？

```
关键在于 nativePollOnce():
1. 没有消息时，线程在 epoll_wait() 中阻塞
2. 阻塞状态不消耗 CPU
3. 有新消息时，通过 nativeWake() 唤醒
4. 阻塞不会导致 ANR
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
    private WeakReference<Activity> ref;
    
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

```
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
```
  主线程: 读取 mMessages.next
  子线程: 修改 mMessages.next
  结果: 主线程可能读到旧值或新值，行为不可预测
```

**问题2: 链表损坏**
```
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
```
  - 同一条消息被取出两次
  - 新插入的消息被跳过
  - 消息顺序错乱
```

#### synchronized 的作用

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    synchronized (this) 的作用                               │
└─────────────────────────────────────────────────────────────────────────────┘

1. 互斥访问
   - 同一时刻只有一个线程能操作 mMessages 链表
   - 主线程读的时候，子线程不能写
   - 子线程写的时候，主线程不能读

2. 内存可见性
   - 一个线程修改后，其他线程能立即看到
   - 防止 CPU 缓存导致的数据不一致

3. 原子操作
   - 取出消息是一组操作，不可分割
   - 要么全部完成，要么全部不完成
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

```
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

```
核心组件:
- ThreadLocal: 线程局部存储 Looper
- Looper: 消息循环 (for(;;) + epoll)
- MessageQueue: 单链表，按时间排序
- Message: 消息池复用
- Handler: 发送/处理消息

工作流程:
1. prepare() → 创建 Looper 和 MessageQueue
2. loop() → 无限循环取消息
3. sendMessage() → 入队 + 唤醒
4. dispatchMessage() → 处理消息
```

---

*本文档由 OpenClaw 生成*
