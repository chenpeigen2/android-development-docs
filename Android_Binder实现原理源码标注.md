# Binder 实现原理 — 完整源码标注

## 一、Binder 整体架构分层

```
┌─────────────────────────────────────────────────────┐
│                    Java 层                           │
│  IBinder (接口)    Binder (服务端)   BinderProxy (客户端) │
│  ServiceManager    Parcel (序列化)                     │
├─────────────────────────────────────────────────────┤
│                    JNI 层                            │
│  android_util_Binder.cpp   android_os_Parcel.cpp     │
│  JavaBBinder (Java→Native桥接)  javaObjectForIBinder  │
├─────────────────────────────────────────────────────┤
│                   Native 层 (libbinder)              │
│  BpBinder (代理端)    BBinder (服务端)                  │
│  IPCThreadState       ProcessState                   │
├─────────────────────────────────────────────────────┤
│                   内核驱动层                           │
│  /dev/binder    binder_ioctl    binder_mmap           │
└─────────────────────────────────────────────────────┘
```

## 二、核心类体系

### ① IBinder — 最顶层接口

`IBinder.java:95`

```java
public interface IBinder {
    int FIRST_CALL_TRANSACTION = 0x00000001;   // 用户自定义 code 起始
    int LAST_CALL_TRANSACTION  = 0x00ffffff;   // 用户自定义 code 上限
    int FLAG_ONEWAY = 0x00000001;              // 异步单向调用标志
    int MAX_IPC_SIZE = 64 * 1024;              // IPC 数据大小建议上限

    // 核心方法：发起一次跨进程调用
    boolean transact(int code, Parcel data, Parcel reply, int flags);

    // 死亡通知
    void linkToDeath(DeathRecipient recipient, int flags);
    boolean unlinkToDeath(DeathRecipient recipient, int flags);
}
```

### ② Binder — 服务端基类（本地对象）

`Binder.java`

| 方法 | 行号 | 作用 |
|------|------|------|
| getCallingUid() | L341 | native 方法，获取调用方 UID（由内核填入） |
| getCallingPid() | L331 | native 方法，获取调用方 PID |
| clearCallingIdentity() | L447 | 清除调用方身份，临时切换为本进程身份 |
| restoreCallingIdentity() | L460 | 恢复调用方身份 |
| onTransact() | L922 | 服务端处理请求的入口，子类重写 |
| execTransact() | L1366 | native 层回调入口（Binder 线程调用） |

### ③ BinderProxy — 客户端代理（远程对象的本地代表）

`BinderProxy.java:51`

```java
public final class BinderProxy implements IBinder {
    // 由 native 层创建，Java 层不能直接实例化
    public boolean transact(int code, Parcel data, Parcel reply, int flags) {
        // ... 检查、追踪
        return transactNative(code, data, reply, flags);  // → JNI
    }
    public native boolean transactNative(int code, Parcel data, Parcel reply, int flags);
}
```

## 三、Binder Proxy/Stub 模式（AIDL 本质）

AIDL 编译后自动生成 `Stub`（服务端）和 `Stub.Proxy`（客户端），以 `IActivityTaskManager` 为例：

### 获取远程代理

`ActivityTaskManager.java:149`

```java
public static IActivityTaskManager getService() {
    return IActivityTaskManagerSingleton.get();
}

private static final Singleton<IActivityTaskManager> IActivityTaskManagerSingleton =
    new Singleton<IActivityTaskManager>() {
        @Override
        protected IActivityTaskManager create() {
            // 1. 从 ServiceManager 获取该服务的 BinderProxy
            final IBinder b = ServiceManager.getService(Context.ACTIVITY_TASK_SERVICE);
            // 2. asInterface 判断本地/远程，返回 Stub 或 Proxy
            return IActivityTaskManager.Stub.asInterface(b);
        }
    };
```

### asInterface 的判断逻辑（AIDL 生成模式）

```java
// AIDL 自动生成，伪代码
public static IActivityTaskManager asInterface(IBinder obj) {
    if (obj == null) return null;
    // 查询是否是本地对象（同进程）
    IInterface iin = obj.queryLocalInterface(DESCRIPTOR);
    if (iin != null && iin instanceof IActivityTaskManager) {
        return (IActivityTaskManager) iin;    // 同进程：直接返回本地 Stub
    }
    return new Stub.Proxy(obj);                // 跨进程：返回 Proxy（持有 BinderProxy）
}
```

**同进程**走直接方法调用，**跨进程**走 `BinderProxy.transact()` → Binder 驱动 → `Binder.execTransact()` → `onTransact()`

## 四、Parcel — 跨进程数据序列化

### Parcel 获取（对象池复用）

`Parcel.java:559`

```java
public static Parcel obtain() {
    synchronized (sPoolSync) {
        if (sOwnedPool != null) {
            res = sOwnedPool;           // 从对象池取
            sOwnedPool = res.mPoolNext;
        }
    }
    if (res == null) res = new Parcel(0); // 池空则创建
    return res;
}
```

### 关键序列化方法

| 方法 | 行号 | 作用 |
|------|------|------|
| writeInt() | L1276 | 写入 int |
| writeLong() | L1287 | 写入 long |
| writeString() | L1320 | 写入 String |
| writeStrongBinder() | L1381 | 写入 IBinder 对象（关键！） |
| readInt() | L3378 | 读取 int |
| readStrongBinder() | L3464 | 读取 IBinder 对象 |

### writeStrongBinder — Binder 对象跨进程传递的精髓

`Parcel.java:1381`

```java
public final void writeStrongBinder(IBinder val) {
    nativeWriteStrongBinder(mNativePtr, val);   // → JNI → native Parcel
}

public final IBinder readStrongBinder() {
    return nativeReadStrongBinder(mNativePtr);   // → JNI → 可能返回 BinderProxy
}
```

当 `writeStrongBinder(binder)` 时：

- 如果是**同进程**传递，`readStrongBinder()` 返回原始的 `Binder` 对象
- 如果是**跨进程**传递，Binder 驱动自动创建一个 `BinderProxy`，`readStrongBinder()` 返回代理对象
- 这就是为什么 Binder 可以跨进程传递"引用"

## 五、Binder 驱动交互（mmap + ioctl）

### ProcessState — 进程级 Binder 初始化

`android_util_Binder.cpp:1376`

```cpp
// 获取 servicemanager 的 BinderProxy（handle=0）
static jobject android_os_BinderInternal_getContextObject(JNIEnv* env, jobject clazz) {
    sp<IBinder> b = ProcessState::self()->getContextObject(NULL);
    return javaObjectForIBinder(env, b);
}
```

`ProcessState::self()` 做了什么（native 层，不在本仓库）：

1. 打开 `/dev/binder` 驱动设备
2. 调用 `mmap()` 映射一块内存（默认 1MB），用于**接收**跨进程数据
3. 启动 Binder 线程池，循环调用 `ioctl()` 等待请求

### mmap — 只拷贝一次的关键

```
发送方进程                          Binder 驱动                     接收方进程
┌──────────┐                    ┌──────────────┐                ┌──────────┐
│ 用户空间  │  copy_from_user   │   内核空间    │  mmap 共享     │ 用户空间  │
│ Parcel   │ ─────────────────→│ binder_alloc │ ══════════════ │ Parcel   │
│ 数据     │  一次内存拷贝      │   buffer     │  零拷贝读取    │ 直接读取  │
└──────────┘                    └──────────────┘                └──────────┘
```

传统 IPC 需要两次拷贝（用户→内核→用户），Binder 通过 mmap 在接收方映射内核 buffer，只需**一次拷贝**。

### ioctl — 实际通信

```
发送方: ioctl(mDriverFD, BINDER_WRITE_READ, &bwr)
  └─ bwr.write_buffer = 请求数据
  └─ bwr.read_buffer  = 接收回复

接收方: ioctl(mDriverFD, BINDER_WRITE_READ, &bwr)
  └─ 阻塞等待 → 驱动唤醒 → bwr.read_buffer 中就是请求数据
```

## 六、Binder 线程模型

### Binder 线程池

每个进程启动后，`ProcessState` 会创建 Binder 线程池：

`android_util_Binder.cpp:1386`

```cpp
static void android_os_BinderInternal_joinThreadPool(JNIEnv* env, jobject clazz) {
    android::IPCThreadState::self()->joinThreadPool();  // 当前线程加入 Binder 线程池
}

static void android_os_BinderInternal_setMaxThreads(JNIEnv* env, jobject clazz, jint maxThreads) {
    ProcessState::self()->setThreadPoolMaxThreadCount(maxThreads);  // 设置最大线程数
}
```

- 主线程默认就是 Binder 线程
- Binder 驱动根据负载自动创建额外线程（最多 15 个）
- 每个线程独立调用 `ioctl()` 等待/处理请求

### FLAG_ONEWAY — 异步调用

`IBinder.java:176`

```java
int FLAG_ONEWAY = 0x00000001;
```

| 模式 | flags | 行为 |
|------|-------|------|
| 同步调用 | 0 | 发送方 `ioctl()` 阻塞，等待服务端处理完毕返回 |
| 异步调用 | FLAG_ONEWAY | 发送方 `ioctl()` 立即返回，不等待结果 |

`Binder.java:1455` — 服务端 oneway 异常处理：

```java
// execTransactInternal 中的 catch 块
if ((flags & FLAG_ONEWAY) != 0) {
    // oneway 调用：异常只打日志，无法传回调用方
    Log.w(TAG, "Binder call failed.", e);
} else {
    // 同步调用：把异常写入 reply 传回
    reply.writeException(e);
}
```

**oneway 有序性保证**：对同一个 IBinder 对象的多个 oneway 调用，在接收方按发送顺序依次执行。

## 七、身份认证机制

### getCallingUid / getCallingPid — 由内核填入

`Binder.java:331`

```java
@CriticalNative
public static final native int getCallingPid();   // 调用方 PID
public static final native int getCallingUid();   // 调用方 UID
```

这两个值由 Binder 驱动在 ioctl 时填入，应用无法伪造。这是 Android 权限检查的基石。

### clearCallingIdentity / restoreCallingIdentity

`Binder.java:447`

```java
// 场景：system_server 收到 App 的 Binder 调用后，需要以自身身份操作
public static final native long clearCallingIdentity();     // 保存调用方身份，切换为本进程
public static final native void restoreCallingIdentity(long token); // 恢复调用方身份
```

典型用法：

```java
// system_server 中的服务端代码
public void doSomething() {
    int callingUid = Binder.getCallingUid();  // 获取调用方
    // 权限检查...
    long token = Binder.clearCallingIdentity();
    try {
        // 以 system_server 身份执行操作（如访问内部文件）
    } finally {
        Binder.restoreCallingIdentity(token);  // 恢复
    }
}
```

## 八、ServiceManager — 服务注册与发现

### 获取 servicemanager 的代理

`ServiceManager.java:149`

```java
private static IServiceManager getIServiceManager() {
    // BinderInternal.getContextObject() → 返回 servicemanager 的 BinderProxy (handle=0)
    sServiceManager = ServiceManagerNative
            .asInterface(Binder.allowBlocking(BinderInternal.getContextObject()));
    return sServiceManager;
}
```

`android_util_Binder.cpp:1376`

```cpp
// getContextObject(NULL) → 获取 handle=0 的 BinderProxy
// handle=0 就是 servicemanager 进程在 Binder 驱动中的固定句柄
sp<IBinder> b = ProcessState::self()->getContextObject(NULL);
return javaObjectForIBinder(env, b);
```

### 服务注册

`ServiceManager.java:253`

```java
public static void addService(String name, IBinder service, ...) {
    getIServiceManager().addService(name, service, allowIsolated, dumpPriority);
}
```

### 服务发现

`ServiceManager.java:169`

```java
public static IBinder getService(String name) {
    IBinder service = sCache.get(name);   // 先查本地缓存
    if (service != null) return service;
    return Binder.allowBlocking(rawGetService(name));  // 没有则跨进程查询 servicemanager
}
```

## 九、javaObjectForIBinder — Binder 对象的双向映射

`android_util_Binder.cpp:962`

```cpp
jobject javaObjectForIBinder(JNIEnv* env, const sp<IBinder>& val) {
    if (val == NULL) return NULL;

    if (val->checkSubclass(&gBinderOffsets)) {
        // 是 JavaBBinder → 本地对象，直接返回原始 Java Binder
        jobject object = static_cast<JavaBBinder*>(val.get())->object();
        return object;
    }

    // 是 BpBinder → 远程对象，创建 BinderProxy
    BinderProxyNativeData* nativeData = new BinderProxyNativeData();
    nativeData->mObject = val;       // 持有 BpBinder
    jobject object = env->CallStaticObjectMethod(gBinderProxyOffsets.mClass,
            gBinderProxyOffsets.mGetInstance, ...);  // 创建 BinderProxy Java 对象
    return object;
}
```

这个函数决定了跨进程传递的 IBinder 是变成 `Binder`（同进程）还是 `BinderProxy`（跨进程）。

## 十、DeathRecipient — 死亡通知

`IBinder.java:363`

```java
public interface DeathRecipient {
    void binderDied();
}

void linkToDeath(DeathRecipient recipient, int flags) throws RemoteException;
boolean unlinkToDeath(DeathRecipient recipient, int flags);
```

`BinderProxy.java:635`

```java
public void linkToDeath(DeathRecipient recipient, int flags) throws RemoteException {
    linkToDeathNative(recipient, flags);    // → JNI → 向 Binder 驱动注册死亡通知
    mDeathRecipients.add(recipient);
}
```

当服务端进程死亡时，Binder 驱动会通知所有注册了 `linkToDeath` 的客户端，回调 `binderDied()`。

## 十一、完整跨进程通信流程图

```
客户端进程                                    Binder 驱动                    服务端进程
═════════                                    ══════════                    ═════════

① ServiceManager.getService("activity")
  │  → rawGetService()
  │    → servicemanager (handle=0) 查询
  │
② 获取 ATMS 的 BinderProxy (handle=X)
  │
③ IActivityTaskManager.Stub.Proxy.startActivity()
  │
  ├─ Parcel data = Parcel.obtain()
  ├─ data.writeInterfaceToken(DESCRIPTOR)
  ├─ data.writeStrongBinder(caller)        ← Binder 对象跨进程传递
  ├─ data.writeString(callingPackage)
  │
  ├─ mRemote.transact(TRANSACTION_startActivity, data, reply, 0)
  │   ↑ BinderProxy.transact()              [BinderProxy.java:534]
  │   │
  ├─ transactNative(code, data, reply, flags)
      │ ↑ JNI                               [BinderProxy.java:622]
      │
④     ├─ android_os_BinderProxy_transact()  [android_util_Binder.cpp:1542]
        │
        ├─ Parcel* data = parcelForJavaObject()   Java Parcel → Native Parcel
        ├─ IBinder* target = getBPNativeData()->mObject  // BpBinder
        │
        ├─ target->transact(code, data, reply, flags)
          │ ↑ BpBinder::transact() (native)
          │
⑤         ├─ IPCThreadState::self()->transact()
            │
            ├─ writeTransactionData(BC_TRANSACTION, ...)
            │
            ├─ waitForResponse(&reply)
              │
              ├─ ioctl(mProcess->mDriverFD, BINDER_WRITE_READ, &bwr)
                │ ↑ 进入内核空间
                │
 ══════════════╪═════════════════════════════════════════════════════
                │
                ├─ 1. 从发送方 copy_from_user 一次
                ├─ 2. 写入接收方 mmap 的共享内存
                ├─ 3. 找到目标进程 (handle → binder_node → binder_proc)
                ├─ 4. 唤醒目标进程的 Binder 线程
                ├─ 5. 挂起当前线程等待回复（同步调用）
                │
 ══════════════╪═════════════════════════════════════════════════════
                │
⑥               ├─ Binder 线程被唤醒
                  │ ↑ ioctl() 返回
                  │
⑦                 ├─ IPCThreadState::executeCommand(cmd)
                    │
                    ├─ BBinder::transact()
                      │ ↑ JavaBBinder::onTransact()   [android_util_Binder.cpp:407]
                      │
⑧                   ├─ env->CallBooleanMethod(mObject, gBinderOffsets.mExecTransact, ...)
                        │ ↑ 回到 Java 层
                        │
⑨                     ├─ Binder.execTransact()           [Binder.java:1366]
                          │ Parcel.obtain(nativePtr) → Java Parcel
                          │
⑩                       ├─ Binder.execTransactInternal()  [Binder.java:1392]
                            │
⑪                          ├─ onTransact(code, data, reply, flags) [Binder.java:1445]
                              │ ↑ AIDL Stub 根据 code 分发
                              │
⑫                             ├─ data.enforceInterface(DESCRIPTOR)  校验接口
                              ├─ 读取参数
                              ├─ ATMS.startActivity(...)            真正执行
                              ├─ reply.writeNoException()
                              └─ reply.writeInt(result)

 ══════════════ 回程：reply 通过 Binder 驱动返回 ══════════════

⑤'  挂起的 ioctl() 返回 → 读取 reply
④'  android_os_BinderProxy_transact() 返回 JNI_TRUE
③'  BinderProxy.transact() 返回 true
②'  Proxy 从 reply 读取结果: reply.readInt()
①'  返回给调用者
```

## 十二、Binder 机制关键设计总结

| 设计点 | 原理 | 源码体现 |
|--------|------|----------|
| 一次拷贝 | 接收方 mmap 映射内核 buffer，发送方 copy_from_user 一次 | `ProcessState::self()` → `mmap()` |
| 身份认证 | UID/PID 由 Binder 驱动填入，无法伪造 | `Binder.getCallingUid()` L341 |
| Proxy/Stub | AIDL 自动生成客户端代理和服务端存根 | `Stub.asInterface()` 判断本地/远程 |
| Binder 引用传递 | `writeStrongBinder()` 写入，驱动自动在对方进程创建代理 | `Parcel.java:1381` |
| 服务发现 | servicemanager 进程，固定 handle=0 | `BinderInternal.getContextObject()` → handle=0 |
| 线程池 | 驱动按需创建线程，最多 15+1 个 | `setMaxThreads()` `BinderInternal.java:158` |
| 死亡通知 | 驱动监测进程死亡，通知所有注册方 | `linkToDeath()` `BinderProxy.java:635` |
| 同步/异步 | flags=0 阻塞等待；FLAG_ONEWAY 立即返回 | `IBinder.java:176` |
| JNI 桥接 | JavaBBinder 包装 Java Binder 为 native BBinder | `javaObjectForIBinder()` `android_util_Binder.cpp:962` |
