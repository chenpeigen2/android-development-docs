# Android Handler 机制详解

_作者：OpenClaw_  
_日期：2026-03-08_

---

## 目录

1. [概述](#1-概述)
2. [Handler 机制架构](#2-handler-机制架构)
3. [Looper 详解](#3-looper-详解)
4. [MessageQueue 详解](#4-messagequeue-详解)
5. [Handler 详解](#5-handler-详解)
6. [Message 详解](#6-message-详解)
7. [ThreadLocal 详解](#7-threadlocal-详解)
8. [同步屏障](#8-同步屏障)
9. [IdleHandler](#9-idlehandler)
10. [HandlerThread](#10-handlerthread)
11. [面试常见问题](#11-面试常见问题)
12. [总结](#12-总结)

---

## 1. 概述

Handler 是 Android 消息机制的核心，用于线程间通信。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Handler 作用                                       │
└─────────────────────────────────────────────────────────────────────────────┘

1. 线程间通信
   - 子线程 → 主线程 (更新 UI)
   - 主线程 → 子线程

2. 延迟执行
   - postDelayed()
   - sendMessageDelayed()

3. 任务调度
   - 消息队列管理
   - 按顺序执行任务
```

---

## 2. Handler 机制架构

### 2.1 核心组件

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Handler 机制架构                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    Thread (子线程)                     Thread (主线程)                      │
│         │                                   │                              │
│         │                                   ▼                              │
│         │                          ┌─────────────────┐                     │
│         │                          │     Looper      │                     │
│         │                          │   (消息循环)    │                     │
│         │                          └────────┬────────┘                     │
│         │                                   │                              │
│         │                          ┌────────▼────────┐                     │
│         │                          │  MessageQueue   │                     │
│         │                          │   (消息队列)    │                     │
│         │                          └────────┬────────┘                     │
│         │                                   │                              │
│         │                          ┌────────▼────────┐                     │
│         │                          │     Handler     │                     │
│         │                          │   (消息处理)    │                     │
│         │                          └────────┬────────┘                     │
│         │                                   │                              │
│         │                          ┌────────▼────────┐                     │
│         │                          │    Message      │                     │
│         │                          │   (消息对象)    │                     │
│         │                          └─────────────────┘                     │
│         │                                   ▲                              │
│         │                                   │                              │
│         └───────────────────────────────────┘                              │
│                    sendMessage() / post()                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 组件关系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         组件关系                                            │
└─────────────────────────────────────────────────────────────────────────────┘

Thread
   │
   │ 每个线程只能有一个 Looper
   ▼
Looper
   │
   │ 每个 Looper 只有一个 MessageQueue
   ▼
MessageQueue
   │
   │ 一个 MessageQueue 可以有多个 Handler
   ▼
Handler
   │
   │ 发送和处理 Message
   ▼
Message

ThreadLocal
   │
   │ 存储每个线程的 Looper
   └──► Thread -> Looper (一对一)
```

---

## 3. Looper 详解

### 3.1 Looper 作用

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Looper 作用                                         │
└─────────────────────────────────────────────────────────────────────────────┘

1. 消息循环
   - 不断从 MessageQueue 取出消息
   - 分发给对应的 Handler 处理

2. 线程绑定
   - 每个线程只能有一个 Looper
   - 通过 ThreadLocal 存储

3. 主线程 Looper
   - ActivityThread.main() 中创建
   - 自动启动循环
```

### 3.2 Looper 源码分析

```java
/**
 * Looper 核心源码
 */
public class Looper {
    
    // ThreadLocal 存储每个线程的 Looper
    static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<>();
    
    // 主线程 Looper
    private static Looper sMainLooper;
    
    // 消息队列
    final MessageQueue mQueue;
    
    // 绑定的线程
    final Thread mThread;
    
    /**
     * 准备 Looper (子线程使用)
     */
    public static void prepare() {
        prepare(true);
    }
    
    private static void prepare(boolean quitAllowed) {
        // 检查是否已存在 Looper
        if (sThreadLocal.get() != null) {
            throw new RuntimeException("Only one Looper may be created per thread");
        }
        // 创建并存储 Looper
        sThreadLocal.set(new Looper(quitAllowed));
    }
    
    /**
     * 准备主线程 Looper
     */
    public static void prepareMainLooper() {
        prepare(false);  // 主线程不允许退出
        synchronized (Looper.class) {
            if (sMainLooper != null) {
                throw new IllegalStateException("The main Looper has already been prepared.");
            }
            sMainLooper = myLooper();
        }
    }
    
    /**
     * 获取当前线程的 Looper
     */
    public static @Nullable Looper myLooper() {
        return sThreadLocal.get();
    }
    
    /**
     * 消息循环 (核心)
     */
    public static void loop() {
        final Looper me = myLooper();
        if (me == null) {
            throw new RuntimeException("No Looper; Looper.prepare() wasn't called on this thread.");
        }
        
        final MessageQueue queue = me.mQueue;
        
        // 无限循环
        for (;;) {
            // 1. 从队列取出消息 (可能阻塞)
            Message msg = queue.next();
            
            if (msg == null) {
                // 队列退出，结束循环
                return;
            }
            
            // 2. 分发消息给 Handler
            msg.target.dispatchMessage(msg);
            
            // 3. 回收消息
            msg.recycleUnchecked();
        }
    }
    
    /**
     * 退出循环
     */
    public void quit() {
        mQueue.quit(false);
    }
    
    public void quitSafely() {
        mQueue.quit(true);
    }
}
```

### 3.3 主线程 Looper 初始化

```java
/**
 * ActivityThread.main() - 主线程入口
 */
public static void main(String[] args) {
    // 1. 初始化主线程 Looper
    Looper.prepareMainLooper();
    
    // 2. 创建 ActivityThread
    ActivityThread thread = new ActivityThread();
    thread.attach(false, startSeq);
    
    // 3. 获取 Handler
    if (sMainThreadHandler == null) {
        sMainThreadHandler = thread.getHandler();
    }
    
    // 4. 启动消息循环
    Looper.loop();
    
    // 5. 循环结束，抛出异常
    throw new RuntimeException("Main thread loop unexpectedly exited");
}
```

---

## 4. MessageQueue 详解

### 4.1 MessageQueue 作用

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MessageQueue 作用                                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. 消息存储
   - 按时间排序的单链表
   - 支持同步消息和异步消息

2. 消息等待
   - 没有消息时阻塞
   - 使用 native 层的 epoll 机制

3. 同步屏障
   - 插入屏障后，同步消息被阻塞
   - 异步消息正常执行
```

### 4.2 MessageQueue 源码分析

```java
/**
 * MessageQueue 核心源码
 */
public final class MessageQueue {
    
    // 消息链表头
    Message mMessages;
    
    // 是否允许退出
    private final boolean mQuitAllowed;
    
    // 是否正在退出
    private boolean mQuitting;
    
    // 下一个消息的时间
    private long mNextMessageTime;
    
    /**
     * 取出下一条消息 (核心)
     */
    Message next() {
        int pendingIdleHandlerCount = -1;
        int nextPollTimeoutMillis = 0;
        
        for (;;) {
            // 1. native 层阻塞等待
            nativePollOnce(ptr, nextPollTimeoutMillis);
            
            synchronized (this) {
                final long now = SystemClock.uptimeMillis();
                Message prevMsg = null;
                Message msg = mMessages;
                
                // 2. 检查同步屏障
                if (msg != null && msg.target == null) {
                    // 遇到屏障，找下一条异步消息
                    do {
                        prevMsg = msg;
                        msg = msg.next;
                    } while (msg != null && !msg.isAsynchronous());
                }
                
                if (msg != null) {
                    if (now < msg.when) {
                        // 消息时间未到，计算等待时间
                        nextPollTimeoutMillis = (int) Math.min(msg.when - now, Integer.MAX_VALUE);
                    } else {
                        // 取出消息
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
                
                // 3. 处理 IdleHandler
                if (pendingIdleHandlerCount < 0 && (mMessages == null || now < mMessages.when)) {
                    pendingIdleHandlerCount = mIdleHandlers.size();
                }
                if (pendingIdleHandlerCount <= 0) {
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
        // 消息必须有 target (Handler)
        if (msg.target == null) {
            throw new IllegalArgumentException("Message must have a target.");
        }
        
        synchronized (this) {
            if (msg.isInUse()) {
                throw new IllegalStateException(msg + " This message is already in use.");
            }
            
            if (mQuitting) {
                IllegalStateException e = new IllegalStateException(msg.target + " sending message to a Handler on a dead thread");
                return false;
            }
            
            msg.markInUse();
            msg.when = when;
            Message p = mMessages;
            boolean needWake;
            
            // 按时间插入链表
            if (p == null || when == 0 || when < p.when) {
                // 插入头部
                msg.next = p;
                mMessages = msg;
                needWake = mBlocked;
            } else {
                // 插入中间
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
            
            // 唤醒等待
            if (needWake) {
                nativeWake(mPtr);
            }
        }
        return true;
    }
    
    /**
     * 添加同步屏障
     */
    public int postSyncBarrier() {
        return postSyncBarrier(SystemClock.uptimeMillis());
    }
    
    private int postSyncBarrier(long when) {
        synchronized (this) {
            final int token = mNextBarrierToken++;
            final Message msg = Message.obtain();
            msg.markInUse();
            msg.when = when;
            msg.arg1 = token;
            
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
    
    /**
     * 移除同步屏障
     */
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
}
```

---

## 5. Handler 详解

### 5.1 Handler 作用

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Handler 作用                                        │
└─────────────────────────────────────────────────────────────────────────────┘

1. 发送消息
   - sendMessage()
   - sendMessageDelayed()
   - post()
   - postDelayed()

2. 处理消息
   - handleMessage()
   - dispatchMessage()

3. 移除消息
   - removeMessages()
   - removeCallbacks()
```

### 5.2 Handler 源码分析

```java
/**
 * Handler 核心源码
 */
public class Handler {
    
    // 关联的 Looper
    final Looper mLooper;
    
    // 关联的消息队列
    final MessageQueue mQueue;
    
    // 回调接口
    final Callback mCallback;
    
    /**
     * 构造函数
     */
    public Handler() {
        this(null, false);
    }
    
    public Handler(Looper looper) {
        this(looper, null, false);
    }
    
    public Handler(Callback callback) {
        this(callback, false);
    }
    
    public Handler(Looper looper, Callback callback, boolean async) {
        mLooper = looper;
        mQueue = looper.mQueue;
        mCallback = callback;
        mAsynchronous = async;
    }
    
    public Handler(@Nullable Callback callback, boolean async) {
        // 获取当前线程的 Looper
        mLooper = Looper.myLooper();
        if (mLooper == null) {
            throw new RuntimeException("Can't create handler inside thread " + Thread.currentThread() + " that has not called Looper.prepare()");
        }
        mQueue = mLooper.mQueue;
        mCallback = callback;
        mAsynchronous = async;
    }
    
    /**
     * 发送消息
     */
    public final boolean sendMessage(@NonNull Message msg) {
        return sendMessageDelayed(msg, 0);
    }
    
    public final boolean sendMessageDelayed(@NonNull Message msg, long delayMillis) {
        if (delayMillis < 0) {
            delayMillis = 0;
        }
        return sendMessageAtTime(msg, SystemClock.uptimeMillis() + delayMillis);
    }
    
    public boolean sendMessageAtTime(@NonNull Message msg, long uptimeMillis) {
        MessageQueue queue = mQueue;
        if (queue == null) {
            RuntimeException e = new RuntimeException(this + " sendMessageAtTime() called with no mQueue");
            return false;
        }
        return enqueueMessage(queue, msg, uptimeMillis);
    }
    
    private boolean enqueueMessage(@NonNull MessageQueue queue, @NonNull Message msg, long uptimeMillis) {
        msg.target = this;  // 设置消息的 target
        msg.workSourceUid = ThreadLocalWorkSource.getUid();
        if (mAsynchronous) {
            msg.setAsynchronous(true);
        }
        return queue.enqueueMessage(msg, uptimeMillis);
    }
    
    /**
     * 发送 Runnable
     */
    public final boolean post(@NonNull Runnable r) {
        return sendMessageDelayed(getPostMessage(r), 0);
    }
    
    public final boolean postDelayed(@NonNull Runnable r, long delayMillis) {
        return sendMessageDelayed(getPostMessage(r), delayMillis);
    }
    
    private static Message getPostMessage(Runnable r) {
        Message m = Message.obtain();
        m.callback = r;
        return m;
    }
    
    /**
     * 分发消息
     */
    public void dispatchMessage(@NonNull Message msg) {
        // 1. 优先处理 Message 的 callback
        if (msg.callback != null) {
            handleCallback(msg);
        } else {
            // 2. 处理 Handler 的 callback
            if (mCallback != null) {
                if (mCallback.handleMessage(msg)) {
                    return;
                }
            }
            // 3. 调用 handleMessage
            handleMessage(msg);
        }
    }
    
    private static void handleCallback(Message message) {
        message.callback.run();
    }
    
    /**
     * 处理消息 (子类重写)
     */
    public void handleMessage(@NonNull Message msg) {
    }
    
    /**
     * 移除消息
     */
    public final void removeMessages(int what) {
        mQueue.removeMessages(this, what, null);
    }
    
    public final void removeCallbacks(@NonNull Runnable r) {
        mQueue.removeMessages(this, r, null);
    }
    
    public final void removeCallbacksAndMessages(@Nullable Object token) {
        mQueue.removeCallbacksAndMessages(this, token);
    }
}
```

### 5.3 Handler 使用示例

```kotlin
/**
 * Handler 使用示例
 */

// 1. 基本使用
class MainActivity : AppCompatActivity() {
    
    private val handler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                1 -> {
                    // 处理消息
                }
            }
        }
    }
    
    fun sendMessage() {
        val msg = handler.obtainMessage(1)
        msg.obj = "data"
        handler.sendMessage(msg)
    }
}

// 2. 使用 post
class MainActivity : AppCompatActivity() {
    
    private val handler = Handler(Looper.getMainLooper())
    
    fun updateUI() {
        Thread {
            // 子线程
            val data = fetchData()
            
            // 切换到主线程
            handler.post {
                textView.text = data
            }
        }.start()
    }
}

// 3. 延迟执行
handler.postDelayed({
    // 1 秒后执行
}, 1000)

// 4. 移除回调
override fun onDestroy() {
    handler.removeCallbacksAndMessages(null)
    super.onDestroy()
}
```

---

## 6. Message 详解

### 6.1 Message 结构

```java
/**
 * Message 结构
 */
public final class Message {
    
    // 消息标识
    public int what;
    
    // 参数
    public int arg1;
    public int arg2;
    
    // 任意对象
    public Object obj;
    
    // 回调
    Runnable callback;
    
    // 目标 Handler
    Handler target;
    
    // 下一条消息
    Message next;
    
    // 执行时间
    long when;
    
    // 是否异步
    boolean isAsynchronous;
    
    // 消息池
    private static final Object sPoolSync = new Object();
    private static Message sPool;
    private static int sPoolSize = 0;
    private static final int MAX_POOL_SIZE = 50;
    
    /**
     * 从池中获取消息
     */
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
    
    /**
     * 回收到池中
     */
    void recycleUnchecked() {
        flags = FLAG_IN_USE;
        what = 0;
        arg1 = 0;
        arg2 = 0;
        obj = null;
        replyTo = null;
        sendingUid = UID_NONE;
        workSourceUid = UID_NONE;
        when = 0;
        target = null;
        callback = null;
        data = null;
        
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

### 6.2 Message 复用

```kotlin
/**
 * Message 复用示例
 */

// ✅ 正确：使用 obtain()
val msg = Message.obtain()
msg.what = 1
msg.obj = "data"
handler.sendMessage(msg)

// ❌ 错误：直接 new
val msg = Message()  // 不推荐
msg.what = 1
handler.sendMessage(msg)

// ✅ 从 Handler 获取
val msg = handler.obtainMessage(1, "data")
handler.sendMessage(msg)
```

---

## 7. ThreadLocal 详解

### 7.1 ThreadLocal 作用

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ThreadLocal 作用                                    │
└─────────────────────────────────────────────────────────────────────────────┘

ThreadLocal 提供线程局部变量:
- 每个线程有独立的副本
- 线程间互不影响
- 用于存储线程特有的数据

Handler 机制中的应用:
- 存储每个线程的 Looper
- 保证每个线程只有一个 Looper
```

### 7.2 ThreadLocal 原理

```java
/**
 * ThreadLocal 源码
 */
public class ThreadLocal<T> {
    
    /**
     * 获取当前线程的值
     */
    public T get() {
        // 1. 获取当前线程
        Thread t = Thread.currentThread();
        
        // 2. 获取线程的 ThreadLocalMap
        ThreadLocalMap map = getMap(t);
        if (map != null) {
            // 3. 从 Map 中取出值
            ThreadLocalMap.Entry e = map.getEntry(this);
            if (e != null) {
                @SuppressWarnings("unchecked")
                T result = (T) e.value;
                return result;
            }
        }
        return setInitialValue();
    }
    
    /**
     * 设置当前线程的值
     */
    public void set(T value) {
        Thread t = Thread.currentThread();
        ThreadLocalMap map = getMap(t);
        if (map != null) {
            map.set(this, value);
        } else {
            createMap(t, value);
        }
    }
    
    /**
     * 获取线程的 Map
     */
    ThreadLocalMap getMap(Thread t) {
        return t.threadLocals;
    }
}

/**
 * Thread 类中有 ThreadLocalMap
 */
public class Thread {
    ThreadLocal.ThreadLocalMap threadLocals = null;
}
```

### 7.3 ThreadLocal 在 Looper 中的应用

```java
/**
 * Looper 使用 ThreadLocal 存储
 */
public class Looper {
    
    // 每个 Thread 有自己的 Looper
    static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<>();
    
    public static void prepare() {
        if (sThreadLocal.get() != null) {
            throw new RuntimeException("Only one Looper may be created per thread");
        }
        sThreadLocal.set(new Looper(true));
    }
    
    public static @Nullable Looper myLooper() {
        return sThreadLocal.get();
    }
}
```

---

## 8. 同步屏障

### 8.1 同步屏障原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         同步屏障 (Sync Barrier)                             │
└─────────────────────────────────────────────────────────────────────────────┘

同步屏障是一种特殊的 Message (target = null)
插入屏障后，队列会跳过所有同步消息，只处理异步消息

┌─────────────────────────────────────────────────────────────────────────────┐
│  消息队列:                                                                  │
│                                                                             │
│  普通消息: [msg1] → [msg2] → [msg3] → [msg4]                               │
│                                                                             │
│  插入屏障后:                                                                │
│  [barrier] → [async_msg1] → [msg3] → [msg4]                               │
│      ↑              ↑                                                       │
│   target=null   异步消息，会被处理                                          │
│                                                                             │
│  msg3、msg4 是同步消息，被屏障阻塞，不会被执行                              │
└─────────────────────────────────────────────────────────────────────────────┘

应用场景:
- UI 渲染优先 ( Choreographer 使用)
- 确保异步消息及时执行
```

### 8.2 同步屏障使用

```kotlin
/**
 * 同步屏障使用示例
 */

// 1. 插入同步屏障
val token = handler.looper.queue.postSyncBarrier()

// 2. 发送异步消息
val asyncMessage = Message.obtain().apply {
    what = 1
    setAsynchronous(true)  // 设置为异步
}
handler.sendMessage(asyncMessage)

// 3. 移除同步屏障
handler.looper.queue.removeSyncBarrier(token)

// Choreographer 中的使用
class Choreographer {
    
    private final class FrameDisplayEventReceiver extends DisplayEventReceiver implements Runnable {
        @Override
        public void onVsync(long timestampNanos, int builtInDisplayId, int frame) {
            // ...
            
            // 发送异步消息
            Message msg = Message.obtain(mHandler, this);
            msg.setAsynchronous(true);
            mHandler.sendMessageAtTime(msg, timestampNanos / TimeUtils.NANOS_PER_MS);
        }
    }
}
```

---

## 9. IdleHandler

### 9.1 IdleHandler 作用

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         IdleHandler 作用                                    │
└─────────────────────────────────────────────────────────────────────────────┘

IdleHandler 在消息队列空闲时执行

应用场景:
- 预加载
- 延迟初始化
- 清理工作
```

### 9.2 IdleHandler 使用

```kotlin
/**
 * IdleHandler 使用
 */

// 1. 添加 IdleHandler
Looper.myQueue().addIdleHandler {
    Log.d("IdleHandler", "Queue is idle, do something")
    
    // 返回 true: 下次空闲继续执行
    // 返回 false: 只执行一次，然后移除
    false
}

// 2. 实际应用
class MainActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // 在空闲时预加载
        Looper.myQueue().addIdleHandler {
            preloadData()
            false  // 只执行一次
        }
    }
    
    private fun preloadData() {
        // 预加载数据
    }
}

// 3. 使用 IdleHandler 做延迟初始化
class MyApp : Application() {
    
    override fun onCreate() {
        super.onCreate()
        
        // 核心初始化
        initCoreComponents()
        
        // 空闲时初始化非核心组件
        Looper.myQueue().addIdleHandler(object : MessageQueue.IdleHandler {
            override fun queueIdle(): Boolean {
                initNonCoreComponents()
                return false
            }
        })
    }
}
```

---

## 10. HandlerThread

### 10.1 HandlerThread 作用

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HandlerThread                                       │
└─────────────────────────────────────────────────────────────────────────────┘

HandlerThread = Thread + Looper

特点:
- 自带 Looper 的线程
- 可以创建 Handler
- 按顺序处理任务
- 适合后台任务
```

### 10.2 HandlerThread 使用

```kotlin
/**
 * HandlerThread 使用
 */

class MyService : Service() {
    
    private lateinit var handlerThread: HandlerThread
    private lateinit var backgroundHandler: Handler
    
    override fun onCreate() {
        super.onCreate()
        
        // 1. 创建 HandlerThread
        handlerThread = HandlerThread("BackgroundThread")
        handlerThread.start()
        
        // 2. 创建 Handler
        backgroundHandler = Handler(handlerThread.looper)
    }
    
    fun executeInBackground() {
        // 3. 在后台线程执行
        backgroundHandler.post {
            // 耗时操作
            val result = doHeavyWork()
            
            // 4. 切回主线程
            Handler(Looper.getMainLooper()).post {
                // 更新 UI
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // 5. 退出
        handlerThread.quit()
    }
}

// 实际应用：图片加载
class ImageLoader(private val context: Context) {
    
    private val handlerThread = HandlerThread("ImageLoader")
    private val handler: Handler
    
    init {
        handlerThread.start()
        handler = Handler(handlerThread.looper)
    }
    
    fun loadImage(url: String, callback: (Bitmap) -> Unit) {
        handler.post {
            val bitmap = downloadImage(url)
            
            Handler(Looper.getMainLooper()).post {
                callback(bitmap)
            }
        }
    }
    
    fun shutdown() {
        handlerThread.quit()
    }
}
```

---

## 11. 面试常见问题

### 11.1 loop() 为什么不会卡死？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         loop() 为什么不会卡死                               │
└─────────────────────────────────────────────────────────────────────────────┘

问题: loop() 是无限循环，为什么不会卡死主线程？

答案:
1. 没有消息时，线程会阻塞 (nativePollOnce)
2. 使用 Linux epoll 机制，阻塞时不消耗 CPU
3. 有消息时唤醒线程处理
4. 阻塞状态不会导致 ANR

ANR 的真正原因:
- 消息处理时间过长 (> 5s)
- 不是 loop() 循环本身

代码:
Message msg = queue.next();  // 可能阻塞，不消耗 CPU
if (msg == null) {
    return;  // 队列退出
}
msg.target.dispatchMessage(msg);  // 处理消息，可能耗时
```

### 11.2 为什么不能在子线程更新 UI？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         为什么不能在子线程更新 UI                            │
└─────────────────────────────────────────────────────────────────────────────┘

原因:
1. UI 控件不是线程安全的
2. 多线程同时修改 UI 会导致状态不一致
3. Android 设计上限制只能在主线程更新 UI

ViewRootImpl.checkThread():
void checkThread() {
    if (mThread != Thread.currentThread()) {
        throw new CalledFromWrongThreadException(
            "Only the original thread that created a view hierarchy can touch its views."
        );
    }
}

解决方案:
- 使用 Handler 切换到主线程
- 使用 runOnUiThread()
- 使用 View.post()
```

### 11.3 如何在子线程创建 Handler？

```kotlin
/**
 * 在子线程创建 Handler
 */

// ❌ 错误：直接创建会崩溃
Thread {
    val handler = Handler()  // RuntimeException: No Looper
}.start()

// ✅ 正确：先调用 Looper.prepare()
Thread {
    Looper.prepare()  // 创建 Looper
    val handler = Handler()
    handler.post {
        // 处理消息
    }
    Looper.loop()  // 开始循环
}.start()

// ✅ 更好：使用 HandlerThread
val handlerThread = HandlerThread("MyThread")
handlerThread.start()
val handler = Handler(handlerThread.looper)
```

### 11.4 MessageQueue 如何保证消息顺序？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MessageQueue 消息排序                               │
└─────────────────────────────────────────────────────────────────────────────┘

插入消息时，按 when (执行时间) 排序:

Message enqueueMessage(Message msg, long when) {
    // 按时间找到插入位置
    Message prev = null;
    Message p = mMessages;
    while (p != null && p.when <= when) {
        prev = p;
        p = p.next;
    }
    // 插入链表
    if (prev != null) {
        prev.next = msg;
    } else {
        mMessages = msg;
    }
    msg.next = p;
}

结果: 链表按 when 升序排列，next() 取出最早的消息
```

---

## 12. 总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Handler 机制总结                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  核心组件:                                                                  │
│  - Handler: 发送和处理消息                                                  │
│  - Looper: 消息循环                                                         │
│  - MessageQueue: 消息队列                                                   │
│  - Message: 消息对象                                                        │
│  - ThreadLocal: 线程局部存储 Looper                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  高级特性:                                                                  │
│  - 同步屏障: 优先处理异步消息                                               │
│  - IdleHandler: 空闲时执行                                                  │
│  - HandlerThread: 带 Looper 的线程                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  面试要点:                                                                  │
│  1. Handler 机制原理                                                        │
│  2. loop() 为什么不会卡死                                                   │
│  3. 为什么不能在子线程更新 UI                                                │
│  4. ThreadLocal 原理                                                        │
│  5. 同步屏障作用                                                            │
│  6. IdleHandler 使用场景                                                    │
│  7. Handler 内存泄漏及解决                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*本文档由 OpenClaw 生成*
