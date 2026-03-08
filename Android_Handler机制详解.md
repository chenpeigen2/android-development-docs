# Android Handler 机制完全指南

> 作者：OpenClaw  
> 日期：2026-03-08

---

## 目录

1. [概述](#1-概述)
2. [整体架构](#2-整体架构)
3. [ThreadLocal 详解](#3-threadlocal-详解)
4. [Looper 详解](#4-looper-详解)
5. [MessageQueue 详解](#5-messagequeue-详解)
6. [Message 详解](#6-message-详解)
7. [Handler 详解](#7-handler-详解)
8. [Native 层实现](#8-native-层实现)
9. [同步屏障机制](#9-同步屏障机制)
10. [IdleHandler 机制](#10-idlehandler-机制)
11. [HandlerThread 详解](#11-handlerthread-详解)
12. [主线程消息循环](#12-主线程消息循环)
13. [面试常见问题](#13-面试常见问题)
14. [总结](#14-总结)

---

## 1. 概述

Handler 是 Android 消息机制的核心，它实现了线程间的异步通信。理解 Handler 机制对于掌握 Android 系统运作原理至关重要。

### 1.1 Handler 机制的作用

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Handler 机制的作用                                  │
└─────────────────────────────────────────────────────────────────────────────┘

1. 线程间通信
   - 子线程 → 主线程 (更新 UI)
   - 主线程 → 子线程
   - 任意线程间通信

2. 延迟执行
   - postDelayed(runnable, delayMillis)
   - sendMessageDelayed(msg, delayMillis)

3. 任务调度
   - 消息队列管理
   - 按时间顺序执行
   - 优先级控制

4. 系统协调
   - Choreographer 帧调度
   - InputEvent 分发
   - 生命周期回调
```

### 1.2 核心组件概览

| 组件 | 作用 | 关系 |
|------|------|------|
| ThreadLocal | 线程局部变量存储 | 存储 Looper |
| Looper | 消息循环器 | 持有 MessageQueue |
| MessageQueue | 消息队列 | 持有 Message 链表 |
| Message | 消息对象 | 持有 Handler 引用 |
| Handler | 消息发送/处理 | 持有 Looper 和 Callback |
| Thread | 线程 | 持有 Looper (通过 ThreadLocal) |

---

## 2. 整体架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Handler 机制架构图                                  │
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
                        │  │   loop() {                │  │
                        │  │     for(;;) {             │  │
                        │  │       msg = queue.next()  │  │
                        │  │       msg.target.         │  │
                        │  │         dispatchMessage() │  │
                        │  │     }                     │  │
                        │  │   }                       │  │
                        │  └───────────┬───────────────┘  │
                        │              │                  │
                        │              ▼                  │
                        │  ┌───────────────────────────┐  │
                        │  │      MessageQueue         │  │
                        │  │   Message 链表            │  │
                        │  │   msg1→msg2→msg3          │  │
                        │  │   nativePollOnce          │  │
                        │  │   nativeWake              │  │
                        │  └───────────┬───────────────┘  │
                        │              │                  │
                        │              ▼                  │
                        │  ┌───────────────────────────┐  │
                        │  │        Handler            │  │
                        │  │   sendMessage()           │  │
                        │  │   post()                  │  │
                        │  │   dispatchMessage()       │  │
                        │  │   handleMessage()         │  │
                        │  └───────────────────────────┘  │
                        └─────────────────────────────────┘
```

### 2.2 完整工作流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Handler 完整工作流程                                │
└─────────────────────────────────────────────────────────────────────────────┘

1. 准备阶段
   ActivityThread.main()
       │
       ├──► Looper.prepareMainLooper()
       │         │
       │         └──► new Looper() → new MessageQueue() → nativeInit()
       │
       └──► Looper.loop()

2. 消息循环
   for (;;) {
       Message msg = queue.next();           // 阻塞等待
       msg.target.dispatchMessage(msg);       // 分发消息
       msg.recycleUnchecked();                // 回收消息
   }

3. 发送消息
   Handler.sendMessage(msg)
       └──► queue.enqueueMessage(msg, when)
                 └──► nativeWake()  // 唤醒等待

4. 处理消息
   Handler.dispatchMessage(msg)
       ├──► msg.callback.run()               // Runnable
       ├──► mCallback.handleMessage(msg)      // Callback
       └──► handleMessage(msg)                // 默认处理
```

---

## 3. ThreadLocal 详解

### 3.1 ThreadLocal 原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ThreadLocal 内部结构                                │
└─────────────────────────────────────────────────────────────────────────────┘

   Thread 1                    Thread 2                    Thread 3
   ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
   │ threadLocals    │        │ threadLocals    │        │ threadLocals    │
   │ (ThreadLocalMap)│        │ (ThreadLocalMap)│        │ (ThreadLocalMap)│
   └────────┬────────┘        └────────┬────────┘        └────────┬────────┘
            │                          │                          │
            ▼                          ▼                          ▼
   ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
   │ Key: sThreadLocal│       │ Key: sThreadLocal│       │ Key: sThreadLocal│
   │ Value: Looper1  │        │ Value: Looper2  │        │ Value: Looper3  │
   └─────────────────┘        └─────────────────┘        └─────────────────┘
```

### 3.2 ThreadLocal 源码分析

```java
public class ThreadLocal<T> {
    
    // 获取当前线程的值
    public T get() {
        Thread t = Thread.currentThread();
        ThreadLocalMap map = getMap(t);
        if (map != null) {
            ThreadLocalMap.Entry e = map.getEntry(this);
            if (e != null) {
                return (T) e.value;
            }
        }
        return setInitialValue();
    }
    
    // 设置当前线程的值
    public void set(T value) {
        Thread t = Thread.currentThread();
        ThreadLocalMap map = getMap(t);
        if (map != null) {
            map.set(this, value);
        } else {
            createMap(t, value);
        }
    }
    
    // 获取线程的 ThreadLocalMap
    ThreadLocalMap getMap(Thread t) {
        return t.threadLocals;  // Thread 类的成员变量
    }
}

// Thread 类
public class Thread {
    ThreadLocal.ThreadLocalMap threadLocals = null;
}
```

### 3.3 Looper 中的 ThreadLocal

```java
public class Looper {
    // 静态 ThreadLocal，所有线程共享作为 Key
    static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<>();
    
    // 准备 Looper
    public static void prepare() {
        if (sThreadLocal.get() != null) {
            throw new RuntimeException("Only one Looper may be created per thread");
        }
        sThreadLocal.set(new Looper(true));
    }
    
    // 获取当前线程的 Looper
    public static Looper myLooper() {
        return sThreadLocal.get();
    }
}
```

---

## 4. Looper 详解

### 4.1 Looper 核心源码

```java
public final class Looper {
    
    // ThreadLocal 存储
    static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<>();
    private static Looper sMainLooper;
    
    // 消息队列和线程
    final MessageQueue mQueue;
    final Thread mThread;
    
    private Looper(boolean quitAllowed) {
        mQueue = new MessageQueue(quitAllowed);
        mThread = Thread.currentThread();
    }
    
    // 准备主线程 Looper
    public static void prepareMainLooper() {
        prepare(false);  // 主线程不允许退出
        synchronized (Looper.class) {
            if (sMainLooper != null) {
                throw new IllegalStateException("The main Looper has already been prepared.");
            }
            sMainLooper = myLooper();
        }
    }
    
    // 消息循环 (核心)
    public static void loop() {
        final Looper me = myLooper();
        if (me == null) {
            throw new RuntimeException("No Looper; Looper.prepare() wasn't called on this thread.");
        }
        
        final MessageQueue queue = me.mQueue;
        
        for (;;) {
            // 1. 取出消息 (可能阻塞)
            Message msg = queue.next();
            if (msg == null) {
                return;  // 队列退出
            }
            
            // 2. 分发消息
            msg.target.dispatchMessage(msg);
            
            // 3. 回收消息
            msg.recycleUnchecked();
        }
    }
    
    // 退出
    public void quit() {
        mQueue.quit(false);
    }
    
    public void quitSafely() {
        mQueue.quit(true);
    }
}
```

### 4.2 主线程 Looper 初始化

```java
// ActivityThread.main()
public static void main(String[] args) {
    // 1. 初始化主线程 Looper
    Looper.prepareMainLooper();
    
    // 2. 创建 ActivityThread
    ActivityThread thread = new ActivityThread();
    thread.attach(false, startSeq);
    
    // 3. 启动消息循环
    Looper.loop();
    
    // 4. 如果退出，抛异常
    throw new RuntimeException("Main thread loop unexpectedly exited");
}
```

---

## 5. MessageQueue 详解

### 5.1 MessageQueue 核心源码

```java
public final class MessageQueue {
    
    // 消息链表头
    Message mMessages;
    
    // 是否允许退出
    private final boolean mQuitAllowed;
    private boolean mQuitting;
    
    // Native 层指针
    private long mPtr;
    
    // 取出下一条消息 (核心)
    Message next() {
        int pendingIdleHandlerCount = -1;
        int nextPollTimeoutMillis = 0;
        
        for (;;) {
            // Native 层阻塞等待
            nativePollOnce(mPtr, nextPollTimeoutMillis);
            
            synchronized (this) {
                final long now = SystemClock.uptimeMillis();
                Message prevMsg = null;
                Message msg = mMessages;
                
                // 检查同步屏障
                if (msg != null && msg.target == null) {
                    // 遇到屏障，找下一条异步消息
                    do {
                        prevMsg = msg;
                        msg = msg.next;
                    } while (msg != null && !msg.isAsynchronous());
                }
                
                if (msg != null) {
                    if (now < msg.when) {
                        // 消息时间未到
                        nextPollTimeoutMillis = (int) Math.min(msg.when - now, Integer.MAX_VALUE);
                    } else {
                        // 取出消息
                        mBlocked = false;
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
                    mBlocked = true;
                    continue;
                }
                
                // 执行 IdleHandler...
            }
        }
    }
    
    // 入队消息
    boolean enqueueMessage(Message msg, long when) {
        if (msg.target == null) {
            throw new IllegalArgumentException("Message must have a target.");
        }
        
        synchronized (this) {
            if (msg.isInUse()) {
                throw new IllegalStateException(msg + " This message is already in use.");
            }
            
            if (mQuitting) {
                return false;
            }
            
            msg.markInUse();
            msg.when = when;
            
            Message p = mMessages;
            boolean needWake;
            
            if (p == null || when == 0 || when < p.when) {
                // 插入头部
                msg.next = p;
                mMessages = msg;
                needWake = mBlocked;
            } else {
                // 按时间插入
                needWake = mBlocked && p.target == null && msg.isAsynchronous();
                Message prev;
                for (;;) {
                    prev = p;
                    p = p.next;
                    if (p == null || when < p.when) {
                        break;
                    }
                    if (needWake && p.isAsynchronous()) {
                        needWake = false;
                    }
                }
                msg.next = p;
                prev.next = msg;
            }
            
            if (needWake) {
                nativeWake(mPtr);
            }
        }
        return true;
    }
}
```

---

## 6. Message 详解

### 6.1 Message 结构

```java
public final class Message {
    
    // 消息标识
    public int what;
    public int arg1;
    public int arg2;
    public Object obj;
    
    // 回调和目标
    Runnable callback;
    Handler target;
    
    // 链表指针
    Message next;
    
    // 执行时间
    long when;
    
    // 是否异步
    boolean isAsynchronous;
    
    // 消息池
    private static Message sPool;
    private static int sPoolSize = 0;
    private static final int MAX_POOL_SIZE = 50;
    
    // 从池中获取
    public static Message obtain() {
        synchronized (sPoolSync) {
            if (sPool != null) {
                Message m = sPool;
                sPool = m.next;
                m.next = null;
                m.flags = 0;
                sPoolSize--;
                return m;
            }
        }
        return new Message();
    }
    
    // 回收
    void recycleUnchecked() {
        flags = FLAG_IN_USE;
        what = 0;
        arg1 = 0;
        arg2 = 0;
        obj = null;
        when = 0;
        target = null;
        callback = null;
        
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

### 7.1 Handler 核心源码

```java
public class Handler {
    
    final Looper mLooper;
    final MessageQueue mQueue;
    final Callback mCallback;
    
    public Handler() {
        this(null, false);
    }
    
    public Handler(Looper looper) {
        this(looper, null, false);
    }
    
    public Handler(Callback callback, boolean async) {
        mLooper = Looper.myLooper();
        if (mLooper == null) {
            throw new RuntimeException(
                "Can't create handler inside thread that has not called Looper.prepare()");
        }
        mQueue = mLooper.mQueue;
        mCallback = callback;
    }
    
    // 发送消息
    public final boolean sendMessage(Message msg) {
        return sendMessageDelayed(msg, 0);
    }
    
    public final boolean sendMessageDelayed(Message msg, long delayMillis) {
        if (delayMillis < 0) delayMillis = 0;
        return sendMessageAtTime(msg, SystemClock.uptimeMillis() + delayMillis);
    }
    
    public boolean sendMessageAtTime(Message msg, long uptimeMillis) {
        MessageQueue queue = mQueue;
        if (queue == null) return false;
        return enqueueMessage(queue, msg, uptimeMillis);
    }
    
    private boolean enqueueMessage(MessageQueue queue, Message msg, long uptimeMillis) {
        msg.target = this;
        if (mAsynchronous) {
            msg.setAsynchronous(true);
        }
        return queue.enqueueMessage(msg, uptimeMillis);
    }
    
    // post Runnable
    public final boolean post(Runnable r) {
        return sendMessageDelayed(getPostMessage(r), 0);
    }
    
    public final boolean postDelayed(Runnable r, long delayMillis) {
        return sendMessageDelayed(getPostMessage(r), delayMillis);
    }
    
    private static Message getPostMessage(Runnable r) {
        Message m = Message.obtain();
        m.callback = r;
        return m;
    }
    
    // 分发消息
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
}
```

---

## 8. Native 层实现

### 8.1 Native 方法

```java
// MessageQueue 中的 Native 方法
public final class MessageQueue {
    
    // Native 层初始化
    private native static long nativeInit();
    private native static void nativeDestroy(long ptr);
    private native void nativePollOnce(long ptr, int timeoutMillis);
    private native static void nativeWake(long ptr);
    private native static boolean nativeIsPolling(long ptr);
    private native static void nativeSetFileDescriptorEvents(long ptr, int fd, int events);
}
```

### 8.2 Native 实现 (C++)

```cpp
// android_os_MessageQueue.cpp

static void android_os_MessageQueue_nativePollOnce(JNIEnv* env, jobject obj,
        jlong ptr, jint timeoutMillis) {
    NativeMessageQueue* nativeMessageQueue = reinterpret_cast<NativeMessageQueue*>(ptr);
    nativeMessageQueue->pollOnce(env, obj, timeoutMillis);
}

void NativeMessageQueue::pollOnce(JNIEnv* env, jobject pollObj, int timeoutMillis) {
    mPollEnv = env;
    mPollObj = pollObj;
    mLooper->pollOnce(timeoutMillis);
    mPollEnv = NULL;
    mPollObj = NULL;
}

// Looper.cpp
int Looper::pollOnce(int timeoutMillis, int* outFd, int* outEvents, void** outData) {
    int result = 0;
    for (;;) {
        // 处理已触发的 Response
        while (mResponseIndex < mResponses.size()) {
            const Response& response = mResponses.itemAt(mResponseIndex++);
            int ident = response.request.ident;
            if (ident >= 0) {
                int fd = response.request.fd;
                int events = response.events;
                void* data = response.request.data;
                if (outFd != NULL) *outFd = fd;
                if (outEvents != NULL) *outEvents = events;
                if (outData != NULL) *outData = data;
                return ident;
            }
        }
        
        if (result != 0) {
            if (outFd != NULL) *outFd = 0;
            if (outEvents != NULL) *outEvents = 0;
            if (outData != NULL) *outData = NULL;
            return result;
        }
        
        result = pollInner(timeoutMillis);
    }
}

int Looper::pollInner(int timeoutMillis) {
    // 使用 epoll_wait 等待事件
    struct epoll_event eventItems[EPOLL_MAX_EVENTS];
    int eventCount = epoll_wait(mEpollFd, eventItems, EPOLL_MAX_EVENTS, timeoutMillis);
    
    // 处理事件...
    return result;
}
```

### 8.3 epoll 机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         epoll 机制                                         │
└─────────────────────────────────────────────────────────────────────────────┘

epoll 是 Linux 高效的 I/O 多路复用机制:

1. epoll_create() - 创建 epoll 实例
2. epoll_ctl() - 添加/修改/删除监听的文件描述符
3. epoll_wait() - 等待事件

MessageQueue 使用 epoll:
- 监听 eventfd (用于 nativeWake)
- 没有消息时，epoll_wait 阻塞
- nativeWake() 写入 eventfd，唤醒 epoll_wait

┌─────────────────────────────────────────────────────────────────────────────┐
│  pollOnce(timeout)                                                         │
│       │                                                                    │
│       ▼                                                                    │
│  epoll_wait(timeout)                                                       │
│       │                                                                    │
│       ├── 超时: 返回                                                       │
│       ├── 有事件: 处理事件                                                 │
│       └── 被唤醒 (nativeWake): 返回                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. 同步屏障机制

### 9.1 同步屏障原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         同步屏障 (Sync Barrier)                             │
└─────────────────────────────────────────────────────────────────────────────┘

同步屏障是特殊的 Message (target = null)
插入后，队列跳过所有同步消息，只处理异步消息

┌─────────────────────────────────────────────────────────────────────────────┐
│  消息队列:                                                                  │
│                                                                             │
│  普通情况: [msg1] → [msg2] → [msg3]                                        │
│                                                                             │
│  插入屏障后: [barrier] → [async_msg] → [msg3] → [msg4]                     │
│                 ↑            ↑                                              │
│              target=null   异步消息，会被处理                               │
│                                                                             │
│  msg3、msg4 是同步消息，被屏障阻塞                                          │
└─────────────────────────────────────────────────────────────────────────────┘

应用场景:
- Choreographer 使用同步屏障优先处理 VSync 信号
- 确保渲染相关的异步消息优先执行
```

### 9.2 同步屏障源码

```java
// MessageQueue.java

// 添加同步屏障
public int postSyncBarrier() {
    return postSyncBarrier(SystemClock.uptimeMillis());
}

private int postSyncBarrier(long when) {
    synchronized (this) {
        final int token = mNextBarrierToken++;
        final Message msg = Message.obtain();
        msg.markInUse();
        msg.when = when;
        msg.arg1 = token;  // target = null 表示屏障
        
        Message prev = null;
        Message p = mMessages;
        if (when != 0) {
            while (p != null && p.when <= when) {
                prev = p;
                p = p.next;
            }
        }
        if (prev != null) {
            msg.next = p;
            prev.next = msg;
        } else {
            msg.next = p;
            mMessages = msg;
        }
        return token;
    }
}

// 移除同步屏障
public void removeSyncBarrier(int token) {
    synchronized (this) {
        Message prev = null;
        Message p = mMessages;
        while (p != null && (p.target != null || p.arg1 != token)) {
            prev = p;
            p = p.next;
        }
        if (p != null) {
            if (prev != null) {
                prev.next = p.next;
            } else {
                mMessages = p.next;
            }
            p.recycleUnchecked();
            if (p != null) {
                nativeWake(mPtr);
            }
        }
    }
}

// next() 中检查屏障
Message next() {
    // ...
    if (msg != null && msg.target == null) {
        // 遇到屏障，找下一条异步消息
        do {
            prevMsg = msg;
            msg = msg.next;
        } while (msg != null && !msg.isAsynchronous());
    }
    // ...
}
```

### 9.3 Choreographer 使用同步屏障

```java
// Choreographer.java

void scheduleVsyncLocked() {
    mDisplayEventReceiver.scheduleVsync();
}

private final class FrameDisplayEventReceiver extends DisplayEventReceiver {
    @Override
    public void onVsync(long timestampNanos, int builtInDisplayId, int frame) {
        // 发送异步消息
        Message msg = Message.obtain(mHandler, this);
        msg.setAsynchronous(true);  // 设置为异步
        mHandler.sendMessageAtTime(msg, timestampNanos / TimeUtils.NANOS_PER_MS);
    }
}
```

---

## 10. IdleHandler 机制

### 10.1 IdleHandler 接口

```java
public static interface IdleHandler {
    /**
     * 返回 true: 继续监听下次空闲
     * 返回 false: 移除监听
     */
    boolean queueIdle();
}
```

### 10.2 IdleHandler 使用

```java
// 添加 IdleHandler
Looper.myQueue().addIdleHandler(new MessageQueue.IdleHandler() {
    @Override
    public boolean queueIdle() {
        // 空闲时执行
        return false;  // 只执行一次
    }
});

// 实际应用: 延迟初始化
class MyApp extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        
        // 核心初始化
        initCore();
        
        // 空闲时初始化非核心组件
        Looper.myQueue().addIdleHandler(() -> {
            initNonCore();
            return false;
        });
    }
}
```

---

## 11. HandlerThread 详解

### 11.1 HandlerThread 源码

```java
public class HandlerThread extends Thread {
    
    Looper mLooper;
    private @Nullable Handler mHandler;
    
    public HandlerThread(String name) {
        super(name);
        mPriority = Process.THREAD_PRIORITY_DEFAULT;
    }
    
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
    
    public Looper getLooper() {
        if (!isAlive()) {
            return null;
        }
        synchronized (this) {
            while (isAlive() && mLooper == null) {
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
```

### 11.2 HandlerThread 使用

```kotlin
class BackgroundService : Service() {
    
    private lateinit var handlerThread: HandlerThread
    private lateinit var handler: Handler
    
    override fun onCreate() {
        handlerThread = HandlerThread("Background")
        handlerThread.start()
        handler = Handler(handlerThread.looper)
    }
    
    fun execute(task: Runnable) {
        handler.post(task)
    }
    
    override fun onDestroy() {
        handlerThread.quit()
    }
}
```

---

## 12. 主线程消息循环

### 12.1 主线程 Handler

```java
// ActivityThread 中的 H 类
class H extends Handler {
    public static final int LAUNCH_ACTIVITY         = 100;
    public static final int PAUSE_ACTIVITY          = 101;
    public static final int STOP_ACTIVITY_SHOW      = 102;
    public static final int STOP_ACTIVITY_HIDE      = 103;
    public static final int SHOW_WINDOW             = 104;
    public static final int HIDE_WINDOW             = 105;
    public static final int RESUME_ACTIVITY         = 107;
    public static final int DESTROY_ACTIVITY        = 109;
    public static final int BIND_APPLICATION        = 110;
    public static final int EXIT_APPLICATION        = 111;
    public static final int NEW_INTENT              = 112;
    public static final int RECEIVER                = 113;
    public static final int CREATE_SERVICE          = 114;
    public static final int SERVICE_ARGS            = 115;
    public static final int STOP_SERVICE            = 116;
    
    public void handleMessage(Message msg) {
        switch (msg.what) {
            case LAUNCH_ACTIVITY: {
                handleLaunchActivity(r, pendingActions, customIntent);
            } break;
            case RESUME_ACTIVITY:
                handleResumeActivity(r.token, false, r.isForward, r.reason);
                break;
            case PAUSE_ACTIVITY:
                handlePauseActivity(r.token, false, false, null, r.reason);
                break;
            case STOP_ACTIVITY_SHOW:
                handleStopActivity(r.token, true, r.info);
                break;
            case DESTROY_ACTIVITY:
                handleDestroyActivity(r.token, false, r.configChanges, false);
                break;
            // ...
        }
    }
}
```

---

## 13. 面试常见问题

### 13.1 loop() 为什么不会卡死？

```
问题: loop() 是无限循环，为什么不会卡死主线程？

答案:
1. 没有消息时，线程在 nativePollOnce() 中阻塞
2. 阻塞使用 epoll 机制，不消耗 CPU
3. 有消息时通过 nativeWake() 唤醒
4. 阻塞状态不会导致 ANR

ANR 的真正原因:
- 消息处理时间过长 (> 5s)
- 不是 loop() 循环本身
```

### 13.2 为什么不能在子线程更新 UI？

```
原因:
1. UI 控件不是线程安全的
2. 多线程同时修改会导致状态不一致
3. Android 设计限制只能在主线程更新 UI

ViewRootImpl.checkThread():
void checkThread() {
    if (mThread != Thread.currentThread()) {
        throw new CalledFromWrongThreadException(...);
    }
}
```

### 13.3 内存泄漏问题

```java
// ❌ 错误: 匿名内部类持有外部类引用
class MainActivity extends Activity {
    private Handler handler = new Handler() {
        @Override
        public void handleMessage(Message msg) {
            // 持有 Activity 引用
        }
    };
}

// ✅ 正确: 静态内部类 + 弱引用
class MainActivity extends Activity {
    private static class SafeHandler extends Handler {
        private WeakReference<MainActivity> ref;
        
        SafeHandler(MainActivity activity) {
            ref = new WeakReference<>(activity);
        }
        
        @Override
        public void handleMessage(Message msg) {
            MainActivity activity = ref.get();
            if (activity != null) {
                // 处理消息
            }
        }
    }
    
    @Override
    protected void onDestroy() {
        handler.removeCallbacksAndMessages(null);
    }
}
```

---

## 14. 总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Handler 机制总结                                    │
└─────────────────────────────────────────────────────────────────────────────┘

核心组件:
- ThreadLocal: 线程局部存储 Looper
- Looper: 消息循环
- MessageQueue: 消息队列 (单链表 + epoll)
- Handler: 发送/处理消息
- Message: 消息对象 (对象池)

高级特性:
- 同步屏障: 优先处理异步消息
- IdleHandler: 空闲时执行
- HandlerThread: 带 Looper 的线程

面试要点:
1. Handler 机制原理
2. loop() 为什么不会卡死
3. ThreadLocal 原理
4. 同步屏障作用
5. 内存泄漏及解决
```

---

*本文档由 OpenClaw 生成*
