# Android ANR 详解（源码版）

## 目录

- [1. 概述](#1-概述)
  - [ANR 触发阈值一览](#anr-触发阈值一览)
- [2. ANR 架构与源码组织](#2-anr-架构与源码组织)
  - [2.1 核心源码文件](#21-核心源码文件)
  - [2.2 ANR 架构图](#22-anr-架构图)
- [3. 超时检测机制源码分析](#3-超时检测机制源码分析)
  - [3.1 TimeoutRecord - 超时记录结构](#31-timeoutrecord---超时记录结构)
  - [3.2 Service 超时检测 - ActiveServices](#32-service-超时检测---activeservices)
    - [3.2.1 超时常量定义](#321-超时常量定义)
    - [3.2.2 Service 超时消息发送](#322-service-超时消息发送)
    - [3.2.3 Service 超时处理流程](#323-service-超时处理流程)
  - [3.3 Broadcast 超时检测 - BroadcastQueueImpl](#33-broadcast-超时检测---broadcastqueueimpl)
    - [3.3.1 超时常量定义](#331-超时常量定义)
    - [3.3.2 广播超时配置](#332-广播超时配置)
    - [3.3.3 广播超时消息处理](#333-广播超时消息处理)
  - [3.4 ContentProvider 超时检测](#34-contentprovider-超时检测)
  - [3.5 Input 超时检测 - Native 层](#35-input-超时检测---native-层)
    - [3.5.1 Native 层 Input 超时检测原理](#351-native-层-input-超时检测原理)
    - [3.5.2 Input ANR 的两种类型与连接断开](#352-input-anr-的两种类型与连接断开)
  - [3.6 Android 17 定时器到 ANR 的完整调用链](#36-android-17-定时器到-anr-的完整调用链)
- [4. ANR 触发链路分析](#4-anr-触发链路分析)
  - [4.1 AnrHelper - ANR 任务调度器](#41-anrhelper---anr-任务调度器)
    - [4.1.1 核心数据结构](#411-核心数据结构)
    - [4.1.2 ANR 记录入队](#412-anr-记录入队)
    - [4.1.3 ANR 消费线程](#413-anr-消费线程)
    - [4.1.4 AnrHelper 处理流程图](#414-anrhelper-处理流程图)
  - [4.2 ProcessErrorStateRecord - ANR 处理核心](#42-processerrorstaterecord---anr-处理核心)
    - [4.2.1 跳过 ANR 的条件](#421-跳过-anr-的条件)
    - [4.2.2 ANR 处理核心逻辑](#422-anr-处理核心逻辑)
    - [4.2.3 弹窗决策流程](#423-弹窗决策流程)
  - [4.3 AnrLatencyTracker - 性能追踪](#43-anrlatencytracker---性能追踪)
    - [4.3.1 追踪的阶段](#431-追踪的阶段)
    - [4.3.2 Dump 输出格式](#432-dump-输出格式)
- [5. ANR 类型与源码对应](#5-anr-类型与源码对应)
  - [5.1 Input ANR](#51-input-anr)
    - [5.1.1 Log 特征](#511-log-特征)
    - [5.1.2 Input ANR 的两种类型与连接断开](#512-input-anr-的两种类型与连接断开)
    - [5.1.3 根因分析（结合源码）](#513-根因分析结合源码)
    - [5.1.4 修复方案](#514-修复方案)
    - [5.1.5 分析方法（从 Log 定位根因）](#515-分析方法从-log-定位根因)
  - [5.2 Broadcast ANR](#52-broadcast-anr)
    - [5.2.1 Log 特征](#521-log-特征)
    - [5.2.2 超时源码位置](#522-超时源码位置)
    - [5.2.3 根因分析](#523-根因分析)
    - [5.2.4 修复方案](#524-修复方案)
  - [5.3 Service ANR](#53-service-anr)
    - [5.3.1 Log 特征](#531-log-特征)
    - [5.3.2 超时源码位置](#532-超时源码位置)
    - [5.3.3 根因分析](#533-根因分析)
    - [5.3.4 修复方案](#534-修复方案)
  - [5.4 ContentProvider ANR](#54-contentprovider-anr)
    - [5.4.1 Log 特征](#541-log-特征)
    - [5.4.2 超时源码位置](#542-超时源码位置)
    - [5.4.3 根因分析](#543-根因分析)
    - [5.4.4 修复方案](#544-修复方案)
- [6. ANR 排查方法](#6-anr-排查方法)
  - [6.1 traces.txt 分析](#61-tracestxt-分析)
  - [6.2 Perfetto 精准分析](#62-perfetto-精准分析)
- [7. ANR 防御体系](#7-anr-防御体系)
  - [7.1 主线程安全红线](#71-主线程安全红线)
  - [7.2 架构设计原则](#72-架构设计原则)
  - [7.3 Binder 调用防御](#73-binder-调用防御)
- [附录：源码索引](#附录源码索引)

---

## 1. 概述

ANR（Application Not Responding）表示系统监控的交互或组件工作未在预算内完成。主线程阻塞是常见原因，但异步广播未 finish、Binder 对端阻塞、CPU 饥饿也会触发；没有正在等待的工作时，单纯阻塞 5 秒不必然产生 ANR。记录、堆栈收集、弹窗和终止是不同阶段，后台 ANR 不一定显示对话框。本文源码固定为 AOSP `android-17.0.0_r1`。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 影响                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  用户体验：卡顿无响应 → 弹出 ANR 对话框 → 用户可能强制关闭 → 应用评分下降      │
│  系统影响：资源占用 → 可能触发 Low Memory Killer → 影响其他应用                │
│  开发影响：崩溃率上升 → 商店排名下降 → 用户流失                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ANR 触发阈值一览

| 类型 | 默认预算与判定 | AOSP 17 入口 |
|---|---|---|
| 已分发 Input 未完成 / 无焦点窗口 | 通常 5 秒；按连接或应用的 dispatching timeout，不是所有窗口固定 5 秒 | `InputDispatcher::processAnrsLocked()` |
| 前台 / 后台广播 | `FLAG_RECEIVER_FOREGROUND` 区分，基值 10 / 60 秒乘硬件倍率；CPU 饥饿可延长，不能按接收进程是否可见判断 | `BroadcastQueueImpl`、`BroadcastConstants.TIMEOUT` |
| Service 生命周期执行 | `isExecServicesFg()` 区分 20 / 200 秒乘硬件倍率；不是 `startForeground()` 通知是否存在 | `ActiveServices.serviceTimeout()` |
| Service 转前台 | 独立计时，`mServiceStartForegroundTimeoutMs` 默认 30 秒；到期复核后停止服务，再按默认 10 秒延迟交给 ANR 链路 | `serviceForegroundTimeout()` → `serviceForegroundTimeoutANR()` |
| Provider 获取 / 发布 / 调用 | 不是统一 10 秒 ANR；获取等待失败、发布超时初始化失败、受监控调用 ANR 是三条路径 | `ContentProviderHelper`、`ContentProviderClient` |

这些是该 tag 的默认值和代码分支，DeviceConfig、硬件倍率、调试状态、AnrTimer 功能开关会改变现场。`shortService`、JobService 等另有期限，不能套用普通 Service 的 20/200 秒。

---

## 2. ANR 架构与源码组织

### 2.1 核心源码文件

```text
frameworks/base/
├── core/
│   └── java/com/android/internal/os/
│       ├── TimeoutRecord.java              # 超时记录结构体
│       └── anr/
│           └── AnrLatencyTracker.java      # ANR 延迟追踪器
│
├── services/core/java/com/android/server/am/
│   ├── ActivityManagerService.java         # AMS - 超时消息与 ANR 协调
│   ├── ActiveServices.java                 # Service 超时检测
│   ├── AnrHelper.java                      # ANR 任务调度器
│   ├── ProcessErrorStateRecord.java        # ANR 处理核心
│   └── StackTracesDumpHelper.java          # traces.txt dump 辅助
│
├── services/core/java/com/android/server/wm/
│   └── InputMonitor.java                   # 窗口焦点监控
│
└── services/core/java/com/android/server/input/
    └── InputManagerService.java            # 输入管理服务
```

### 2.2 ANR 架构图

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ANR 架构                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │  InputDispatcher│     │  ActiveServices │     │      AMS        │       │
│  │    (Native)     │     │    (Java)       │     │    (Java)       │       │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘       │
│           │                       │                       │                │
│           │ 超时 5s                │ 超时 20s/200s          │ 超时 10s/60s    │
│           ▼                       ▼                       ▼                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      AnrHelper (Java)                                │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │  AnrConsumerThread - 异步消费 ANR 记录                          │ │   │
│  │  │  - 维护 ANR 记录队列 mAnrRecords                                 │ │   │
│  │  │  - 去重检查（跳过重复 ANR）                                      │ │   │
│  │  │  - 早期 Dump（主进程优先）                                       │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                  ProcessErrorStateRecord (Java)                      │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │  appNotResponding() - ANR 处理核心                              │ │   │
│  │  │  - 记录 ANR 到 EventLog                                         │ │   │
│  │  │  - Dump 线程堆栈到 traces.txt                                    │ │   │
│  │  │  - 获取 ANR Controller 延迟                                     │ │   │
│  │  │  - 决定是否弹窗（Silent vs Dialog）                              │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│                         ┌─────────────────┐                                 │
│                         │   ANR Dialog    │                                 │
│                         │   or Silent Kill│                                │
│                         └─────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 超时检测机制源码分析

### 3.1 TimeoutRecord - 超时记录结构

**源码路径**: `frameworks/base/core/java/com/android/internal/os/TimeoutRecord.java`

`TimeoutRecord` 是该 tag 使用的统一超时记录结构，用于封装所有类型的 ANR 超时信息。

```java
// TimeoutRecord.java（节选；按函数名定位）
@IntDef(value = {
        TimeoutKind.INPUT_DISPATCH_NO_FOCUSED_WINDOW,   // 1 - 无窗口焦点
        TimeoutKind.INPUT_DISPATCH_WINDOW_UNRESPONSIVE,  // 2 - 窗口无响应
        TimeoutKind.BROADCAST_RECEIVER,                  // 3 - 广播超时
        TimeoutKind.SERVICE_START,                       // 4 - Service 启动超时
        TimeoutKind.SERVICE_EXEC,                        // 5 - Service 执行超时
        TimeoutKind.CONTENT_PROVIDER,                    // 6 - ContentProvider 超时
        TimeoutKind.APP_REGISTERED,                      // 7 - 应用注册超时
        TimeoutKind.SHORT_FGS_TIMEOUT,                   // 8 - 短前 Service 超时
        TimeoutKind.JOB_SERVICE,                         // 9 - Job Service 超时
        TimeoutKind.APP_START,                           // 10 - 应用启动超时
})
public @interface TimeoutKind {}
```

**关键字段**:

```java
// TimeoutRecord.java（节选；按函数名定位）
@TimeoutKind
public final int mKind;              // 超时类型

public final String mReason;         // 超时原因描述

public final long mEndUptimeMillis;  // 超时触发时的系统启动时间

public final boolean mEndTakenBeforeLocks;  // 是否在获取锁之前记录时间

public final AnrLatencyTracker mLatencyTracker;  // 延迟追踪器

private AutoCloseable mExpiredTimer;  // 过期的定时器句柄
```

**工厂方法**:

```java
// TimeoutRecord.java（节选；按函数名定位）
/** 广播接收器超时记录 */
public static TimeoutRecord forBroadcastReceiver(@NonNull Intent intent) {
    final StringBuilder reason = new StringBuilder("Broadcast of ");
    intent.toString(reason);
    return TimeoutRecord.endingNow(TimeoutKind.BROADCAST_RECEIVER, reason.toString());
}

/** Input 窗口无响应超时 */
public static TimeoutRecord forInputDispatchWindowUnresponsive(@NonNull String reason) {
    return TimeoutRecord.endingNow(TimeoutKind.INPUT_DISPATCH_WINDOW_UNRESPONSIVE, reason);
}

/** Input 无焦点窗口超时 */
public static TimeoutRecord forInputDispatchNoFocusedWindow(@NonNull String reason) {
    return TimeoutRecord.endingNow(TimeoutKind.INPUT_DISPATCH_NO_FOCUSED_WINDOW, reason);
}

/** Service 执行超时 */
public static TimeoutRecord forServiceExec(@NonNull String shortInstanceName,
        long timeoutDurationMs) {
    String reason = "executing service " + shortInstanceName + ", waited "
            + timeoutDurationMs + "ms";
    return TimeoutRecord.endingNow(TimeoutKind.SERVICE_EXEC, reason);
}

/** ContentProvider 超时 */
public static TimeoutRecord forContentProvider(@NonNull String reason) {
    return TimeoutRecord.endingApproximatelyNow(TimeoutKind.CONTENT_PROVIDER, reason);
}
```

**超时类型到 ANR 子原因的映射**:

```java
// TimeoutRecord.java（节选；按函数名定位）
public @SubReason int getAppExitInfoAnrSubreason() {
    return switch (mKind) {
        case TimeoutRecord.TimeoutKind.APP_REGISTERED ->
                ApplicationExitInfo.SUBREASON_ANR_TYPE_APP_TRIGGERED;
        case TimeoutRecord.TimeoutKind.APP_START ->
                ApplicationExitInfo.SUBREASON_ANR_TYPE_BIND_APPLICATION;
        case TimeoutRecord.TimeoutKind.BROADCAST_RECEIVER ->
                ApplicationExitInfo.SUBREASON_ANR_TYPE_BROADCAST_OF_INTENT;
        case TimeoutRecord.TimeoutKind.CONTENT_PROVIDER ->
                ApplicationExitInfo.SUBREASON_ANR_TYPE_CONTENT_PROVIDER_NOT_RESPONDING;
        case TimeoutRecord.TimeoutKind.SERVICE_EXEC ->
                ApplicationExitInfo.SUBREASON_ANR_TYPE_EXECUTING_SERVICE;
        case TimeoutRecord.TimeoutKind.SHORT_FGS_TIMEOUT ->
                ApplicationExitInfo.SUBREASON_ANR_TYPE_FOREGROUND_SHORT_SERVICE_TIMEOUT;
        case TimeoutRecord.TimeoutKind.INPUT_DISPATCH_WINDOW_UNRESPONSIVE ->
                ApplicationExitInfo.SUBREASON_ANR_TYPE_INPUT_DISPATCHING_TIMEOUT;
        case TimeoutRecord.TimeoutKind.INPUT_DISPATCH_NO_FOCUSED_WINDOW ->
                ApplicationExitInfo.SUBREASON_ANR_TYPE_INPUT_DISPATCHING_TIMEOUT_NO_FOCUSED_WINDOW;
        case TimeoutRecord.TimeoutKind.JOB_SERVICE ->
                ApplicationExitInfo.SUBREASON_ANR_TYPE_JOB_SERVICE_START;
        case TimeoutRecord.TimeoutKind.SERVICE_START ->
                ApplicationExitInfo.SUBREASON_ANR_TYPE_START_FOREGROUND_SERVICE;
        default -> ApplicationExitInfo.SUBREASON_UNKNOWN;
    };
}
```

---

### 3.2 Service 超时检测 - ActiveServices

**源码路径**: `frameworks/base/services/core/java/com/android/server/am/ActiveServices.java`

Service 生命周期执行超时与“启动后未及时转前台”分别计时。前者以 `ProcessRecord` 为 key，后者以 `ServiceRecord` 为 key，不能用一个 Handler 消息取消所有服务的超时。

#### 3.2.1 超时常量定义

```java
// ActivityManagerConstants.java（摘录）
private static final long DEFAULT_SERVICE_TIMEOUT =
        20 * 1000 * Build.HW_TIMEOUT_MULTIPLIER;
private static final long DEFAULT_SERVICE_BACKGROUND_TIMEOUT =
        DEFAULT_SERVICE_TIMEOUT * 10;
```

`ProcessServiceRecord.isExecServicesFg()` 决定本次执行用哪个预算；`executeFg` 是生命周期执行的调度属性，不等价于 Foreground Service 的通知状态。`executingStart` 使用 uptime，与检查时钟一致。

#### 3.2.2 Service 超时消息发送

```text
bumpServiceExecutingLocked(ServiceRecord, ...)
  -> 维护 executeNesting / executingStart / executingServices
  -> scheduleServiceTimeoutLocked(ProcessRecord)
  -> mActiveServiceAnrTimer.start(proc, delay)
  -> AnrTimer 到期 -> AMS.MainHandler SERVICE_TIMEOUT_MSG
  -> serviceTimeout(proc)
```

AnrTimer Native 路径到期通过 `expire()` 通知 Handler；功能未启用时有 Handler fallback，不能写成“不再有 Java 定时器”。`start/cancel/accept/discard` 必须使用对应业务 key。

#### 3.2.3 Service 超时处理流程

```text
serviceTimeout(proc)
  -> 调试中 / 无 executing service / 无应用线程 / 已被杀：discard
  -> 根据 isExecServicesFg 计算 now - timeout
  -> 遍历 executingServices，比较 executingStart
  -> 超时且进程仍在 LRU：forServiceExec + accept
  -> 释放 AMS 锁 -> mAnrHelper.appNotResponding
  -> 尚不成立：discard 并按仍执行的服务重新 start

serviceDoneExecutingLocked
  -> executeNesting 归零后移除对应执行项
  -> 进程 executing 集合清空才 cancel(proc)
```

源码中没有本文旧版使用的 `computeServiceTimeoutTime(...)`、`handleServiceTimeout()` 或四参数 `Handler.sendMessageDelayed(...)`。实际预算来自 ActivityManagerConstants；完成一个服务不能消除同进程其他执行项的监控。

### 3.3 Broadcast 超时检测 - BroadcastQueueImpl

**源码路径**：`frameworks/base/services/core/java/com/android/server/am/BroadcastQueueImpl.java`。

#### 3.3.1 超时常量定义

AMS 为前后台队列配置 10/60 秒乘 `Build.HW_TIMEOUT_MULTIPLIER` 的基值，`BroadcastConstants.TIMEOUT` 承接配置；`calculateBroadcastTimeout()` 按 `BroadcastRecord.isForeground()` 选择。这里前台指 Intent 的 `FLAG_RECEIVER_FOREGROUND`，不是接收器所在进程的前台状态。

#### 3.3.2 广播超时配置

```java
// BroadcastQueueImpl.java（摘录）
private long calculateBroadcastTimeout(BroadcastRecord r) {
    return r.isForeground() ? mFgConstants.TIMEOUT : mBgConstants.TIMEOUT;
}
// BroadcastAnrTimer 构造参数包含 new AnrTimer.Args().extend(true)
```

CPU 饥饿情况下 AnrTimer 可扩展预算；官方诊断指南给 Android 14+ 的前台广播 10–20 秒、后台 60–120 秒范围。它是调度压力补偿，不是 `goAsync()` 获得任意额外时间。进程启动及接收线程排队也会占用投递预算；assumed-delivered 等路径并非都等待完成回执。

#### 3.3.3 广播超时消息处理

```text
startDeliveryTimeoutLocked(queue, timeout) -> mAnrTimer.start(queue, timeout)
正常完成 -> finishReceiver... -> cancelDeliveryTimeoutLocked(queue)
到期 -> MSG_DELIVERY_TIMEOUT -> deliveryTimeout(queue)
     -> deliveryTimeoutLocked(queue)
     -> finishReceiverActiveLocked(queue, DELIVERY_TIMEOUT, ...)
     -> forBroadcastReceiver(...) -> accept(queue, record)
     -> mService.mAnrHelper.appNotResponding(...)
     -> demoteFromRunningLocked(queue)
```

`finishReceiverActiveLocked()` 还复核接收进程与调试状态，不合条件会 `discard`。`goAsync()` 返回后必须在预算内调用 `PendingResult.finish()`；适合长期运行的任务应交给 WorkManager，而非无界延长广播执行。

### 3.4 ContentProvider 超时检测

必须区分以下三条链路，发布超时不等同于一次 `query()` 超时：

```text
1. 获取 Provider 等待发布
   ContentProviderHelper.getContentProviderImpl
   -> WAIT_FOR_CONTENT_PROVIDER_TIMEOUT_MSG
   -> ContentProviderRecord.onProviderPublishStatusLocked(false)
   -> 通知获取方失败；本消息本身不调用 AnrHelper

2. 进程启动后的 Provider 发布期限
   AMS.attachApplication... -> CONTENT_PROVIDER_PUBLISH_TIMEOUT_MSG
   -> ContentProviderHelper.processContentProviderPublishTimedOutLocked
   -> removeProcessLocked(REASON_INITIALIZATION_FAILURE,
                          "timeout publishing content providers")

3. Provider 调用无响应（启用客户端检测的路径）
   ContentProviderClient.setDetectNotResponding(timeoutMillis)
   -> beforeRemote -> NotRespondingRunnable
   -> ContentResolver.appNotRespondingViaProvider
   -> AMS -> ContentProviderHelper.appNotRespondingViaProvider
   -> TimeoutRecord.forContentProvider -> AnrHelper
```

`ContentResolver.CONTENT_PROVIDER_PUBLISH_TIMEOUT_MILLIS` 为 `10s × Build.HW_TIMEOUT_MULTIPLIER`；`CONTENT_PROVIDER_READY_TIMEOUT_MILLIS` 是发布预算再加 `10s ×` 倍率，即 `20s ×` 倍率，但不能据此声称所有 Provider 调用统一 10 秒 ANR。`setDetectNotResponding` 是隐藏接口，服务端还要求 `REMOVE_TASKS`；普通应用不能照抄作为通用超时 API。自己的同步 `query()` 阻塞主线程也可能先触发 Input ANR，责任进程与 Provider ANR 不同。

`ActivityThread.handleBindApplication()` 先安装 Provider，后调用 `Application.onCreate()`；Provider `onCreate()` 的数据库打开和 SDK 初始化应尽量轻量，首次查询的延迟仍需从工作线程承担。

### 3.5 Input 超时检测 - Native 层

Input 的超时检测在 Native InputDispatcher 中，窗口归属、报告、堆栈和弹窗仍经过 Java 的 WM/AM 链路；不能把检测 Native 化描述成整个 ANR 都在 Native 层。

#### 3.5.1 Native 层 Input 超时检测原理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Input ANR 检测机制 (Native)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  InputReader (Native)                                                        │
│       │                                                                      │
│       ▼                                                                     │
│  InputDispatcher (Native)                                                    │
│       │                                                                      │
│       ├── 1. 读取 Input 事件                                                │
│       │                                                                      │
│       ├── 2. 通过 InputChannel 发送到应用                                    │
│       │                                                                      │
│       ├── 3. 将事件加入 connection.waitQueue                                          │
│       │     启动超时计时 (5 秒)                                              │
│       │                                                                      │
│       ▼                                                                     │
│  NativeInputEventReceiver (Native)                                           │
│       │                                                                      │
│       ├── 4. 应用消费事件                                                    │
│       │                                                                      │
│       ▼                                                                     │
│  InputDispatcher (Native)                                                    │
│       │                                                                      │
│       ├── 5. 收到消费完成信号                                                │
│       │                                                                      │
│       ├── 6. 从 connection.waitQueue 移除记录                                          │
│       │                                                                      │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  如果 5 秒内没有收到完成信号:                                        │    │
│  │  - InputDispatcher 通知 policy，经 JNI/WM/AM 收集堆栈                          │    │
│  │  - 调用 AMS.appNotResponding() 触发 ANR                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  关键点:                                                                     │
│  - Input 超时检测在 Native 层完成，比 Java 层更早发现问题                     │
│  - 不再依赖 Java 层的 Handler 延迟消息                                      │
│  - InputDispatcher 维护 connection.waitQueue，记录所有未完成的输入事件                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 3.5.2 Input ANR 的两种类型与连接断开

根据 `TimeoutRecord.java` 中定义的 `TimeoutKind`，Input ANR 有两种:

| TimeoutKind | 值 | Log 中的 Reason | 场景 |
|-------------|-----|-----------------|------|
| INPUT_DISPATCH_WINDOW_UNRESPONSIVE | 2 | "Input dispatching timed out waiting to send event to app" | 窗口无响应 |
| INPUT_DISPATCH_NO_FOCUSED_WINDOW | 1 | "no window focus has been received within 5000 ms" | 无窗口焦点 |

---

### 3.6 Android 17 定时器到 ANR 的完整调用链

AOSP `android-17.0.0_r1` 不用一个全局 Handler 消息判断所有 ANR。`AnrTimer<V>` 以业务对象为 key，Native timer 到期后通过 `expire()` 向指定 Handler 投递消息；业务处理再决定 `cancel`、`accept` 或 `discard`。

```text
Service lifecycle callback
 -> ActiveServices.bumpServiceExecutingLocked
 -> scheduleServiceTimeoutLocked
 -> mActiveServiceAnrTimer.start(ProcessRecord, delay)
 -> SERVICE_TIMEOUT_MSG -> serviceTimeout
 -> 复查 executingStart / thread / killed 状态
 -> accept(TimeoutRecord.forServiceExec) -> appNotResponding

Broadcast receiver
 -> calculateBroadcastTimeout
 -> mAnrTimer.start(BroadcastProcessQueue, timeout)
 -> finishReceiverActiveLocked -> cancel
 -> MSG_DELIVERY_TIMEOUT -> deliveryTimeoutLocked
 -> accept(TimeoutRecord.forBroadcastReceiver) -> appNotResponding
```

`ActiveServices.ProcessAnrTimer` 内部类从 `ProcessRecord` 提取 PID/UID。服务回调完成后只有 executing 集合清空才取消进程计时器；前台服务转前台的期限由 `mServiceFGAnrTimer` 独立管理。广播计时器使用 `extend(true)`，前后台基值来自 `BroadcastConstants`。`goAsync()` 延迟的是 `finish()`，不是取消期限。

`AnrHelper.appNotResponding()` 先按 PID 去重、提交 early dump，再把 `AnrRecord` 放入 `mAnrRecords`，由 `AnrConsumerThread` 串行消费；早期堆栈、报告生成、进程退出不是同一时刻。排查应把 InputDispatcher 的事件 deadline、应用主线程、Binder 服务端和锁持有线程放在同一时间线上。

源码：`services/core/java/com/android/server/utils/AnrTimer.java`、`services/core/java/com/android/server/am/ActiveServices.java`、`BroadcastQueueImpl.java`、`AnrHelper.java`。


## 4. ANR 触发链路分析

### 4.1 AnrHelper - ANR 任务调度器

**源码路径**: `frameworks/base/services/core/java/com/android/server/am/AnrHelper.java`

`AnrHelper` 是 ANR 处理的调度器，使用独立线程异步消费 ANR 记录。

#### 4.1.1 核心数据结构

```java
// AnrHelper.java（节选；按函数名定位）
@GuardedBy("mAnrRecords")
private final ArrayList<AnrRecord> mAnrRecords = new ArrayList<>();  // ANR 记录队列

private final Set<Integer> mTempDumpedPids =
        Collections.synchronizedSet(new ArraySet<Integer>());  // 已 Dump 的 PID 集合

private final AtomicBoolean mRunning = new AtomicBoolean(false);  // 是否正在运行

private final ActivityManagerService mService;

private final ExecutorService mAuxiliaryTaskExecutor;   // 辅助任务线程池
private final ExecutorService mEarlyDumpExecutor;        // 早期 Dump 线程池
```

#### 4.1.2 ANR 记录入队

```java
// AnrHelper.java（节选；按函数名定位）
void appNotResponding(ProcessRecord anrProcess, String activityShortComponentName,
        ApplicationInfo aInfo, String parentShortComponentName,
        WindowProcessController parentProcess, boolean aboveSystem,
        TimeoutRecord timeoutRecord, boolean isContinuousAnr) {
    try {
        timeoutRecord.mLatencyTracker.appNotRespondingStarted();
        final int incomingPid = anrProcess.mPid;
        timeoutRecord.mLatencyTracker.waitingOnAnrRecordLockStarted();
        synchronized (mAnrRecords) {
            timeoutRecord.mLatencyTracker.waitingOnAnrRecordLockEnded();

            // 1. 零 PID 检查（极端情况，如 zygote 无响应）
            if (incomingPid == 0) {
                Slog.i(TAG, "Skip zero pid ANR, process=" + anrProcess.processName);
                return;
            }

            // 2. 重复 PID 检查（防止重复处理）
            if (mProcessingPid == incomingPid) {
                Slog.i(TAG, "Skip duplicated ANR, pid=" + incomingPid);
                return;
            }

            // 3. 已被提前 Dump 的检查
            if (!mTempDumpedPids.add(incomingPid)) {
                Slog.i(TAG, "Skip ANR being predumped, pid=" + incomingPid);
                return;
            }

            // 4. 队列中已有该 PID 的检查
            for (int i = mAnrRecords.size() - 1; i >= 0; i--) {
                if (mAnrRecords.get(i).mPid == incomingPid) {
                    Slog.i(TAG, "Skip queued ANR, pid=" + incomingPid);
                    return;
                }
            }

            // 5. 早期 Dump - 在独立线程提前 Dump 主进程的 traces
            Future<File> firstPidDumpPromise = mEarlyDumpExecutor.submit(() -> {
                File tracesFile = StackTracesDumpHelper.dumpStackTracesTempFile(
                        incomingPid, timeoutRecord.mLatencyTracker);
                mTempDumpedPids.remove(incomingPid);
                return tracesFile;
            });

            // 6. 创建 ANR 记录并加入队列
            mAnrRecords.add(new AnrRecord(anrProcess, activityShortComponentName, aInfo,
                    parentShortComponentName, parentProcess, aboveSystem, timeoutRecord,
                    isContinuousAnr, firstPidDumpPromise));
        }
        // 7. 启动 ANR 消费线程
        startAnrConsumerIfNeeded();
    } finally {
        timeoutRecord.mLatencyTracker.appNotRespondingEnded();
    }
}
```

#### 4.1.3 ANR 消费线程

```java
// AnrHelper.java（节选；按函数名定位）
private class AnrConsumerThread extends Thread {
    AnrConsumerThread() {
        super("AnrConsumer");
    }

    private AnrRecord next() {
        synchronized (mAnrRecords) {
            if (mAnrRecords.isEmpty()) {
                return null;
            }
            final AnrRecord record = mAnrRecords.remove(0);
            mProcessingPid = record.mPid;
            return record;
        }
    }

    @Override
    public void run() {
        AnrRecord r;
        while ((r = next()) != null) {
            // 如果进程已死亡，跳过
            final int currentPid = r.mApp.mPid;
            if (currentPid != r.mPid) {
                Slog.i(TAG, "Skip ANR with mismatched pid");
                continue;
            }

            final long startTime = SystemClock.uptimeMillis();
            final long reportLatency = startTime - r.mTimestamp;

            // 如果报告延迟过长，只 Dump 自己
            final boolean onlyDumpSelf = reportLatency > EXPIRED_REPORT_TIME_MS
                    || startTime < SELF_ONLY_AFTER_BOOT_MS;

            // 调用 ProcessErrorStateRecord 处理 ANR
            r.appNotResponding(onlyDumpSelf);

            final long endTime = SystemClock.uptimeMillis();
            Slog.d(TAG, "Completed ANR of " + r.mApp.processName + " in "
                    + (endTime - startTime) + "ms, latency " + reportLatency);
        }

        mRunning.set(false);
        // 队列非空时重启消费线程
        synchronized (mAnrRecords) {
            mProcessingPid = -1;
            if (!mAnrRecords.isEmpty()) {
                startAnrConsumerIfNeeded();
            }
        }
    }
}
```

#### 4.1.4 AnrHelper 处理流程图

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AnrHelper 处理流程                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐                                                        │
│  │ 超时触发          │                                                        │
│  │ (Service/Broadcast│                                                       │
│  │ /Input/CP)        │                                                        │
│  └────────┬────────┘                                                        │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ AnrHelper.appNotResponding() - ANR 记录入队                           │   │
│  │                                                                     │   │
│  │  去重检查:                                                            │   │
│  │  - mProcessingPid == incomingPid → 跳过 (重复 ANR)                  │   │
│  │  - mTempDumpedPids 已存在 → 跳过 (正在被 Dump)                       │   │
│  │  - mAnrRecords 队列中已存在 → 跳过 (已在队列中)                      │   │
│  │                                                                     │   │
│  │  早期 Dump:                                                           │   │
│  │  - mEarlyDumpExecutor.submit() 提前 Dump 主进程 traces               │   │
│  └────────┬────────────────────────────────────────────────────────────┘   │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ AnrConsumerThread.run() - 异步消费 ANR 记录                          │   │
│  │                                                                     │   │
│  │  判断是否只 Dump 自己:                                                │   │
│  │  - 报告延迟 > 10s → 只 Dump ANR 应用                                 │   │
│  │  - 启动时间 < 10min → 只 Dump ANR 应用 (减少启动负载)                │   │
│  │                                                                     │   │
│  └────────┬────────────────────────────────────────────────────────────┘   │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ AnrRecord.appNotResponding() → ProcessErrorStateRecord             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 4.2 ProcessErrorStateRecord - ANR 处理核心

**源码路径**: `frameworks/base/services/core/java/com/android/server/am/ProcessErrorStateRecord.java`

`ProcessErrorStateRecord.appNotResponding()` 是 ANR 处理的核心方法。

#### 4.2.1 跳过 ANR 的条件

```java
// ProcessErrorStateRecord.java（节选；按函数名定位）
@GuardedBy("mService")
boolean skipAnrLocked(String annotation) {
    // 1. 系统正在关机
    if (mService.mAtmInternal.isShuttingDown()) {
        Slog.i(TAG, "During shutdown skipping ANR: " + this);
        return true;
    }
    // 2. 已经在处理 ANR
    else if (isNotResponding()) {
        Slog.i(TAG, "Skipping duplicate ANR: " + this);
        return true;
    }
    // 3. 应用正在崩溃
    else if (isCrashing()) {
        Slog.i(TAG, "Crashing app skipping ANR: " + this);
        return true;
    }
    // 4. 应用已被 AM 杀死
    else if (mApp.isKilledByAm()) {
        Slog.i(TAG, "App already killed by AM skipping ANR: " + this);
        return true;
    }
    // 5. 应用已死亡
    else if (mApp.isKilled()) {
        Slog.i(TAG, "Skipping died app ANR: " + this);
        return true;
    }
    return false;
}
```

#### 4.2.2 ANR 处理核心逻辑

```java
// ProcessErrorStateRecord.java（节选；按函数名定位）
void appNotResponding(String activityShortComponentName, ApplicationInfo aInfo,
        String parentShortComponentName, WindowProcessController parentProcess,
        boolean aboveSystem, TimeoutRecord timeoutRecord,
        ExecutorService auxiliaryTaskExecutor, boolean onlyDumpSelf,
        boolean isContinuousAnr, Future<File> firstPidFilePromise) {
    String annotation = timeoutRecord.mReason;

    // 1. 关闭过期定时器
    timeoutRecord.closeExpiredTimer();

    // 2. 如果应用正在调试，跳过 ANR
    if (mApp.isDebugging()) {
        Slog.i(TAG, "Skipping debugged app ANR: " + this);
        return;
    }

    // 3. 记录 ANR 到 EventLog
    EventLog.writeEvent(EventLogTags.AM_ANR, mApp.userId, pid, mApp.processName,
            mApp.info.flags, annotation);

    // 4. 获取 ANR Controller 延迟
    AnrController anrController = mService.mActivityTaskManager.getAnrController(aInfo);
    long anrDialogDelayMs = 0;
    if (anrController != null) {
        anrDialogDelayMs = anrController.getAnrDelayMillis(packageName, uid);
    }

    // 5. 收集要 Dump 的进程 PID
    // firstPids: 优先 Dump 的进程（包括 ANR 主进程、父进程、AMS）
    // lastPids: 其他相关进程

    // 6. Dump 所有相关进程的 traces
    // 7. 构建 ANR 报告信息
    // 8. 决定是否弹窗或静默杀死
}
```

#### 4.2.3 弹窗决策流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ANR 弹窗决策流程                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ProcessErrorStateRecord.appNotResponding()                           │   │
│  └────────┬────────────────────────────────────────────────────────────┘   │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. 记录到 EventLog                                                    │   │
│  │    EventLog.writeEvent(AM_ANR, ...)                                 │   │
│  └────────┬────────────────────────────────────────────────────────────┘   │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 2. Dump 线程堆栈到 traces.txt                                         │   │
│  │    - firstPids: 主进程、父进程、AMS                                  │   │
│  │    - lastPids: 其他相关进程                                          │   │
│  │    - 使用 Signal 3 (SIGQUIT) 触发 dump                              │   │
│  └────────┬────────────────────────────────────────────────────────────┘   │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 3. 获取 ANR Controller 延迟                                           │   │
│  │    - 某些应用可以配置延迟弹窗                                         │   │
│  │    - anrController.getAnrDelayMillis()                               │   │
│  └────────┬────────────────────────────────────────────────────────────┘   │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 4. 判断是否后台 ANR (Silent ANR)                                      │   │
│  │    - 应用在后台且窗口不可见 → 静默杀死，不弹窗                         │   │
│  │    - 应用在前台 → 弹出 ANR 对话框                                     │   │
│  └────────┬────────────────────────────────────────────────────────────┘   │
│           │                                                                  │
│           ├── 后台 → Silent Kill (暗杀)                                    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 5. 弹窗或杀死                                                         │   │
│  │    - 前台应用: 弹出 "应用无响应" 对话框                               │   │
│  │    - 用户选择: 等待 或 关闭应用                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 4.3 AnrLatencyTracker - 性能追踪

**源码路径**: `frameworks/base/core/java/com/android/internal/os/anr/AnrLatencyTracker.java`

`AnrLatencyTracker` 是该 tag 使用的 ANR 性能追踪器，用于分析 ANR 处理流程中各阶段的耗时。

#### 4.3.1 追踪的阶段

```java
// AnrLatencyTracker.java（节选；按函数名定位）
// ANR 触发到处理完成的各阶段耗时
private long mAnrTriggerUptime;              // ANR 触发时间
private long mAppNotRespondingStartUptime;   // appNotResponding() 开始
private long mAnrRecordPlacedOnQueueUptime;  // ANR 记录入队时间
private long mAnrProcessingStartedUptime;   // ANR 处理开始时间
private long mDumpStackTracesStartUptime;    // Dump 开始时间

// 各种锁的等待时间
private long mGlobalLockTotalContention;     // AMS 全局锁等待时间
private long mPidLockTotalContention;        // PID 锁等待时间
private long mAMSLockTotalContention;        // AMS 锁等待时间
private long mProcLockTotalContention;       // Proc 锁等待时间
private long mAnrRecordLockTotalContention; // ANR 记录锁等待时间

// 各操作的耗时
private long mUpdateCpuStatsNowTotalLatency;      // 更新 CPU 统计耗时
private long mCurrentPsiStateTotalLatency;         // 获取 PSI 状态耗时
private long mCriticalEventLogTotalLatency;        // 关键事件日志耗时
```

#### 4.3.2 Dump 输出格式

```java
// AnrLatencyTracker.java（节选；按函数名定位）
public String dumpAsCommaSeparatedArrayWithHeader() {
    return "DurationsV5: " + mAnrTriggerUptime
            + "," + (mAppNotRespondingStartUptime - mAnrTriggerUptime)       // 触发到 appNotResponding
            + "," + (mAnrRecordPlacedOnQueueUptime - mAppNotRespondingStartUptime)  // 入队耗时
            + "," + (mAnrProcessingStartedUptime - mAnrRecordPlacedOnQueueUptime)    // 处理开始耗时
            + "," + (mDumpStackTracesStartUptime - mAnrProcessingStartedUptime)      // Dump 开始耗时
            + "," + mUpdateCpuStatsNowTotalLatency
            + "," + mCurrentPsiStateTotalLatency
            + "," + mProcessCpuTrackerMethodsTotalLatency
            + "," + mCriticalEventLogTotalLatency
            + "," + mGlobalLockTotalContention
            + "," + mPidLockTotalContention
            + "," + mAMSLockTotalContention
            + "," + mProcLockTotalContention
            + "," + mAnrRecordLockTotalContention
            // ... 更多指标
}
```

这个追踪数据对于分析 ANR 处理本身的性能问题非常重要，比如锁竞争导致的 ANR 处理延迟。

---

## 5. ANR 类型与源码对应

### 5.1 Input ANR

InputDispatcher 的 `processAnrsLocked()` 分别检查无焦点窗口期限和 AnrTracker 中连接事件的期限。`onAnrLocked()` 经 policy 通知 Java 层，后续并非 Native 独立处理。

#### 5.1.1 Log 特征

```text
ANR in com.example.app (Input dispatching timed out)
Reason: Input dispatching timed out waiting to send event to app.
Window is waiting in state WINDOW_KEY_DISPATCHING_PENDING because the
target window is not responding.
mTimeout: 5000ms
mSince: 1234567890123
```

**三要素快速定位**:
- `Reason` — 具体场景（发送事件超时 / 窗口无响应 / 无焦点窗口）
- `mTimeout: 5000ms` — 该示例的 Input 预算为 5 秒；实际取 dispatching timeout
- `mSince` — 超时计时开始的毫秒时间戳（可用于 trace 对齐）

#### 5.1.2 Input ANR 的两种类型与连接断开

根据 `TimeoutRecord.java` 和 `AnrController.java` 的源码分析，Input ANR 有两种类型，另列一个不是 ANR 类型的连接错误：

| 场景 | Reason 关键字 | 触发条件 | 责任方 |
|------|--------------|----------|--------|
| **窗口无响应** | `Input dispatching timed out waiting to send event to app` | 事件已发送给应用但 5s 未收到完成信号 | 应用主线程 |
| **无焦点窗口** | `no window focus has been received within 5000 ms` | 应用无焦点窗口超过 5s | 应用 / 系统 |
| **InputChannel 断开（非 ANR 类型）** | `InputChannel is closed` | InputChannel 被关闭 | 系统 / 应用 |

**场景一：窗口无响应（最常见）**

```text
用户触摸屏幕
       │
       ▼
InputReader (Native) — 读取原始输入事件
       │
       ▼
InputDispatcher (Native) — 通过 InputChannel 发送给目标窗口
       │
       ├─ 发送成功 → 事件加入 connection.waitQueue → 开始 5s 计时
       │
       ▼
NativeInputEventReceiver (Native) — 在应用端接收事件
       │
       ▼
InputEventReceiver.dispatchInputEvent (Java) → ViewRootImpl → View
       │
       ▼
finishInputEvent() — 发送完成信号 (FINISHED_EVENTS)
       │
       ▼
InputDispatcher 收到完成信号 → 从 connection.waitQueue 移除 → 计时终止
```

**超时链路源码分析**:

```cpp
// frameworks/base/services/core/jni/com_android_server_input_InputManagerService.cpp
// Native 回调入口 — InputDispatcher 检测到超时后通知 Java 层

// 1. InputDispatcher (Native) 检测到窗口无响应
//    调用 Java 层 InputManagerService.notifyWindowUnresponsive()
private void notifyWindowUnresponsive(IBinder token, int pid, boolean isPidValid, String reason) {
    mWindowManagerCallbacks.notifyWindowUnresponsive(token,
            isPidValid ? OptionalInt.of(pid) : OptionalInt.empty(), reason);
}

// 2. InputManagerCallback 收到通知，构建 TimeoutRecord
@Override
public void notifyWindowUnresponsive(@NonNull IBinder token, @NonNull OptionalInt pid, String reason) {
    TimeoutRecord timeoutRecord = TimeoutRecord.forInputDispatchWindowUnresponsive(
            timeoutMessage(pid, reason));
    mService.mAnrController.notifyWindowUnresponsive(token, pid, timeoutRecord);
}

// 3. AnrController 处理超时
//    路径: AnrController.java:143-198
//    - 通过 inputToken 找到 WindowState / ActivityRecord
//    - 如果能关联到 Activity，调用 activity.inputDispatchingTimedOut()
//    - 如果无法关联（嵌入式窗口），直接调用 mAmInternal.inputDispatchingTimedOut(pid)
//    - 异步 dump ANR 状态到 traces.txt

// 4. AMS 层的 inputDispatchingTimedOut 最终调用 ProcessErrorStateRecord.appNotResponding()
```

**场景二：无焦点窗口**

```java
// InputManagerCallback.java:108-112
@Override
public void notifyNoFocusedWindowAnr(@NonNull InputApplicationHandle applicationHandle) {
    TimeoutRecord timeoutRecord = TimeoutRecord.forInputDispatchNoFocusedWindow(
            timeoutMessage(OptionalInt.empty(), "Application does not have a focused window"));
    mService.mAnrController.notifyAppUnresponsive(applicationHandle, timeoutRecord);
}
```

场景二触发条件：
- 应用有焦点但无焦点窗口（焦点窗口被移除，新窗口还未创建）
- 应用刚启动，还在创建窗口的过程中

**场景三：InputChannel 断开**

```java
// NativeInputEventReceiver.cpp:305-318
int NativeInputEventReceiver::handleEvent(int receiveFd, int events, void* data) {
    if (events & (ALOOPER_EVENT_ERROR | ALOOPER_EVENT_HANGUP)) {
        // InputChannel 关闭时返回 REMOVE_CALLBACK，InputDispatcher 认为连接断开
        if (kDebugDispatchCycle) {
            ALOGD("channel '%s' ~ Publisher closed input channel or an error occurred. events=0x%x",
                  mName.c_str(), events);
        }
        return REMOVE_CALLBACK;  // 不触发 ANR，只是移除回调
    }
    // ...
}
```

InputChannel HANGUP 通常是应用主动关闭 window（如 Activity 销毁）导致，该错误回调本身不触发上述 Input 超时 ANR。

#### 5.1.3 根因分析（结合源码）

**根因 A：主线程在等锁（常见原因之一，不能从源码推出占比）**

```java
// 应用代码示例
class MyPresenter {
    private final Object lock = new Object();
    private String data;

    // 子线程：持有锁但被 IO 阻塞
    void loadData() {
        synchronized(lock) {
            data = performNetworkRequest();  // 网络 IO 慢
        }
    }

    // 主线程：等锁超时 5s
    void onCreate() {
        synchronized(lock) {   // ← 等这里！子线程还卡在网络请求
            render(data);
        }
    }
}
```

`traces.txt` 中表现为：
```text
"main" prio=5 tid=1 Blocked
  locks java.lang.Object@7a3e4568 held by thread 15
  at com.example.MyPresenter.onCreate(MyPresenter.java:25)
  at android.app.Activity.onCreate(Activity.java:1234)

"pool-1-thread-1" prio=5 tid=15 Runnable
  at java.net.SocketInputStream.read(SocketInputStream.java:163)
  at java.net.HttpURLConnectionImpl.readResponse(HttpURLConnectionImpl.java:456)
  - waiting to lock java.lang.Object@7a3e4568 held by thread 1
```

**根因 B：主线程在做同步 Binder 调用（system server 端阻塞）**

```java
// 主线程调用 ContentProvider / SMS / PackageManager 等系统服务
// 若远端阻塞，主线程可能耗尽输入的 deadline，不是 Binder 自带 5s 超时

// 典型场景：ContentProvider 初始化 + 多进程
ContentResolver.query(uri, ...)  // 跨进程调用
// Provider 宿主进程（未必 system_server）的 onCreate/调用执行慢
// 主线程同步 Binder 等待可能耗尽输入 deadline；Binder 本身没有统一 5 秒超时

// 另一个场景：通知栏 Service 连接
override fun onServiceConnected(name: ComponentName, service: IBinder) {
    // system server 端 Service.onBind() 慢
}

// traces.txt 表现：
// "main" prio=5 tid=1 Suspended
//   at ActivityThread.performBindService(ActivityThread.java:4567)
//   at ActivityThread$H.handleMessage(ActivityThread.java:2345)
//   - waiting for service connection (可能跨进程等锁)
```

**根因 C：主线程在执行耗时 I/O 操作**

```java
// 反例：大文件读取 / 大图加载 / SharedPreferences 多进程模式
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // ❌ SharedPreferences 首次读取，多进程模式下会解析 XML
    val prefs = getSharedPreferences("config", Context.MODE_MULTI_PROCESS)
    val data = prefs.getString("key", "")  // 如果文件大，可能耗时

    // ❌ 大图加载（即使在 ImageView 设置前 decode）
    val bitmap = BitmapFactory.decodeFile("/data/user/0/com.example/files/large.png")
    // BitmapFactory 在 decode 时需要申请内存 + 像素解析，
    // 如果图片超大（20MB+），可能超过 5s

    // ❌ 数据库初始化
    val db = SQLiteDatabase.openDatabase(path, null, OPEN_READONLY)
    // 首次打开可等待文件锁、恢复 WAL、校验或执行迁移；不会必然重建所有索引
}
```

**根因 D：主线程在等待 GC（内存压力大时）**

```text
"main" prio=5 tid=1 Runnable
  at com.example.MyActivity.onCreate(MyActivity.java:30)
  at android.app.Activity.performCreate(Activity.java:7890)
  at android.app.Instrumentation.callActivityOnCreate(Instrumentation.java:1306)
  - waiting for GC ( Alloc space:256MB, Free space:3MB, Objects:45000 )

// 原因：系统可用内存不足，GC concurrent mark 阶段没能及时完成
// 表现为 "waiting for GC" 关键字
```

**根因 E：主线程被 Choreographer 调度阻塞**

```java
// Choreographer 帧调度导致的延迟
// 如果上一帧 render 超过 16ms，后续帧会被阻塞
override fun doFrame(frameTimeNanos: Long) {
    // 上一帧超过 16ms，这一帧 callback 被延迟
    // 只有被监控的输入/组件工作超过 deadline 才可能 ANR；掉帧时长不能直接累加成 ANR
    doExpensiveRender()
    Choreographer.getInstance().postFrameCallback(this)
}
```

#### 5.1.4 修复方案

**方案 A：锁竞争修复**

```java
// ❌ 反例：锁粒度过大
class BadPresenter {
    private val lock = Any()
    private var cache: Bitmap? = null

    fun loadAndRender() {
        synchronized(lock) {
            cache = BitmapFactory.decodeFile(path)  // 大图 decode 中
            view.render(cache!!)                       // decode 还没完
        }  // 整个操作期间其他线程全被阻塞
    }
}

// ✅ 正例 1：缩小临界区，只锁必要的数据结构
class GoodPresenter {
    private val lock = Any()
    private @Volatile var cache: Bitmap? = null

    fun loadAndRender() {
        // 解码在临界区外完成
        val bitmap = BitmapFactory.decodeFile(path)

        synchronized(lock) {
            cache = bitmap  // 只锁赋值操作，毫秒级
        }
        // UI 操作在临界区外
        Handler(Looper.getMainLooper()).post { view.render(bitmap) }
    }
}

// ✅ 正例 2：使用 CopyOnWriteArrayList / ConcurrentHashMap 减少锁
class DataManager {
    private val cache = ConcurrentHashMap<String, Bitmap>()

    fun put(key: String, value: Bitmap) {
        cache[key] = value  // 并发安全；写入可能使用 CAS 或桶锁
    }

    fun get(key: String): Bitmap? {
        return cache[key]  // 无锁读取
    }
}

// ✅ 正例 3：ReadWriteLock
class CacheManager {
    private val rwLock = ReentrantReadWriteLock()
    private val cache = HashMap<String, Any>()

    fun read(key: String): Any? {
        rwLock.readLock().lock()
        try {
            return cache[key]
        } finally {
            rwLock.readLock().unlock()
        }
    }

    fun write(key: String, value: Any) {
        rwLock.writeLock().lock()
        try {
            cache[key] = value
        } finally {
            rwLock.writeLock().unlock()
        }
    }
}
```

**方案 B：Binder 调用修复**

```java
// ❌ 反例：主线程同步调用 ContentProvider
class BadFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // ContentProvider query 在主线程执行
        val cursor = contentResolver.query(uri, null, null, null, null)
        // 如果 ContentProvider 初始化慢，这里会 Block
    }
}

// ✅ 正例 1：ContentProvider 懒加载，不在启动路径上触发
class GoodFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        view.post {
            // post 仅排队，不保证首帧已上屏；真正查询仍切到后台
            loadData()
        }
    }

    private fun loadData() {
        lifecycleScope.launch {
            val cursor = withContext(Dispatchers.IO) {
                contentResolver.query(uri, null, null, null, null)
            }
            // 处理数据
        }
    }
}

// ✅ 正例 2：在 IO 线程查询并关闭 Cursor，只向主线程返回业务数据
suspend fun queryNames(resolver: ContentResolver, uri: Uri): List<String> =
    withContext(Dispatchers.IO) {
        resolver.query(uri, arrayOf("name"), null, null, null)?.use { cursor ->
            buildList {
                val column = cursor.getColumnIndexOrThrow("name")
                while (cursor.moveToNext()) add(cursor.getString(column))
            }
        } ?: emptyList()
    }
```

`withTimeout` / `Future.get(timeout)` 只能约束协作式等待，不能保证中断已进入 Binder 的同步调用；`withContext(IO)` 仍会等阻塞代码退出。需要取消的查询应将取消传给支持的 `CancellationSignal` overload，并验证 Provider 是否处理取消；任意 Binder 方法没有统一的应用级强制终止机制。

**方案 C：主线程 I/O 修复**

```java
// ❌ 反例：大图在主线程解码
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    val bitmap = BitmapFactory.decodeFile(path)  // ❌ 主线程 decode
    imageView.setImageBitmap(bitmap)
}

// ✅ 正例 1：协程 + IO 线程解码
lifecycleScope.launch {
    val bitmap = withContext(Dispatchers.IO) {
        BitmapFactory.decodeFile(path)  // IO 线程 decode
    }
    imageView.setImageBitmap(bitmap)     // 主线程设置
}

// ✅ 正例 2：大图先缩小再加载
lifecycleScope.launch {
    val options = BitmapFactory.Options().apply {
        inJustDecodeBounds = true  // 先获取尺寸，不分配内存
    }
    BitmapFactory.decodeFile(path, options)

    // 计算采样率
    options.inSampleSize = calculateInSampleSize(options, 1024, 1024)
    options.inJustDecodeBounds = false

    withContext(Dispatchers.IO) {
        BitmapFactory.decodeFile(path, options)  // 缩小后 decode
    }
}

// ✅ 正例 3：SharedPreferences 多进程模式替代方案
// MODE_MULTI_PROCESS 自 API 23 废弃，不能提供可靠跨进程一致性
// 使用 ContentProvider 或 Room 进行跨进程数据共享
```

**方案 D：GC 优化**

```java
// ❌ 避免在启动路径上创建大量对象
class BadActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ❌ 每次 onCreate 都创建新对象，增加 GC 压力
        val analytics = AnalyticsEngine()  // 重型对象
        val helpers = ArrayList<Helper>()   // 大集合
        val bitmapCache = LruCache<String, Bitmap>(100)  // 内存分配
    }
}

// ✅ 使用单例 / 对象池，减少启动路径上的内存分配
class GoodActivity : AppCompatActivity() {
    private val analytics by lazy { AnalyticsEngine.getInstance() }
    private val helpers by lazy { HelperPool.get() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 无重型对象分配
    }
}

// ✅ 主动触发 GC hint（谨慎使用）
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // 在重型操作前 hint 系统提前 GC
    System.gc()  // 提示性的，不保证立即执行
    // 然后执行重型操作
}
```

#### 5.1.5 分析方法（从 Log 定位根因）

**第一步：从 Logcat 找到 ANR 上下文**

```bash
# 过滤 ANR 相关的 Logcat
adb logcat | grep -E "ANR|InputDispatch|ActivityManager"

# 查找 ANR 前的应用行为
adb logcat -v time | grep -B 20 "ANR in com.example"
```

**关键 Log 位置**:

```text
// 1. ANR 触发时的主线程堆栈（在 traces.txt 中）
//    重点关注："main" prio=5 tid=1 ??? 状态

// 2. 状态关键字对照：
//    Runnable       → 正在执行（可能是 CPU 密集型）
//    Blocked        → 等待锁
//    TimedWaiting   → 等 Object.wait() + 超时
//    Waiting        → 等锁 / 等条件
//    Suspended      → 被挂起（GC 或 native 挂起）

// 3. Binder trace（如果 ANR 发生在跨进程调用）
adb bugreport bugreport.zip
# 查看 main.txt_transportable_bugreport/BUGreport_version > /main_entry/ANR
```

**第二步：traces.txt 分析**

```bash
# traces.txt 路径（不同 Android 版本略有不同）
# Android 17: /data/anr/anr_*；先列目录，不假定固定文件名
# 需要 root 或 adb shell read

adb shell ls -lt /data/anr/ # 需授权的调试构建；量产机改用 bugreport

# 分析主线程状态：
# 1. 如果是 "Blocked" — 找 waiting to lock xxx，找到持有锁的线程，看它在做什么
# 2. 如果是 "Runnable" — 看主线程当前在执行哪个方法
# 3. 如果是 "Waiting" — 找 wait() 调用，分析等待条件
# 4. 如果有 "GC" 关键字 — 内存压力大，优先解决内存泄漏
```

**traces.txt 典型模式速查**:

| traces.txt 关键字 | 含义 | 解决方案 |
|------------------|------|---------|
| `waiting to lock java/lang/Object@xxxxx` | 等锁 | 缩小锁粒度 / 改用无锁数据结构 |
| `performBindService` | Service 绑定慢 | 检查 Service.onBind() |
| `acquireContentProviderClient` | ContentProvider 获取慢 | 检查 Provider.onCreate() |
| `doFrame` / `Choreographer` | 渲染超时 | 减少 onDraw 耗时 / 检查 CPU 调度 |
| `android.database.sqlite` | 数据库操作 | 移到子线程 |
| `BitmapFactory.decode` | 图片解码 | 协程 + IO 线程 |
| `waitForGcToComplete` | 等待 GC | 检查内存泄漏 / 减少对象分配 |
| `nativePollOnce` | Looper 等待消息 | 正常等待，非阻塞 |

**第三步：Systrace / Perfetto 分析**

```bash
# Systrace（适合快速定位卡顿帧）
python $ANDROID_SDK/platform-tools/systrace/systrace.py \
    --app=com.example \
    gfx input view sched freq \
    -b 16384 \
    -o trace.html

# Perfetto（Android 10+，更详细）
adb shell perfetto \
    -c - \
    --txt \
    -o /data/misc/perfetto-traces/trace.perfetto-trace \
    <<EOF
buffers: {
    size_kb: 63488
    fill_policy: RING_BUFFER
}
duration_ms: 10000
data_sources: {
    config {
        name: "linux.ftrace"
        ftrace_config {
            ftrace_events: "sched/sched_switch"
            ftrace_events: "sched/sched_waking"
            ftrace_events: "power/cpu_frequency"
            ftrace_events: "power/cpu_idle"
        }
    }
    config {
        name: "android.surfaceflinger.frametimeline"
    }
}
EOF

adb pull /data/misc/perfetto-traces/trace.perfetto-trace .
```

**Systrace 中找 ANR**:

1. 在 Systrace 中找到 ANR 时间点（红色竖线）
2. 放大主线程（main）行
3. 找 `InputQueue` 或 `Choreographer` 的 gap（空白区域 = 无响应）
4. gap 不是代码栈；结合 thread_state、Binder flow、同时刻堆栈定位，不能把最后一个 slice 当作必然根因

```text
主线程行示意：
[ViewRootImpl]  [InputQueue]  [Choreographer]  [某方法]
   ████████████      ████           ████████████
   正常处理        等待消息         ANR 前的最后一帧
                  ← 5s gap →
                       ↑
                   这 5s 主线程在做什么？
```

**第四步：Simpleperf 分析 CPU 占用**

```bash
# 如果怀疑 CPU 抢占导致 ANR（根因 E）
adb shell simpleperf record -p <pid> --duration=10 \
    -o /data/local/tmp/perf.data

adb pull /data/local/tmp/perf.data .

# 使用 Simpleperf report 分析，不把 perf.data 当 Perfetto protobuf
simpleperf report -i perf.data # 使用匹配主机的 NDK simpleperf 工具
```

---

### 5.2 Broadcast ANR

#### 5.2.1 Log 特征

```text
ANR in com.example.app (while in broadcast)
Reason: Broadcast of Intent { act=android.intent.action.MY_BROADCAST }
```

#### 5.2.2 超时源码位置

- 超时常量: `ActivityManagerService.java + BroadcastConstants` (`BROADCAST_FG_TIMEOUT`, `BROADCAST_BG_TIMEOUT`)
- 超时链路: `BroadcastQueueImpl.BroadcastAnrTimer` → `MSG_DELIVERY_TIMEOUT` → `finishReceiverActiveLocked`

#### 5.2.3 根因分析

```text
Broadcast ANR 的两个主要根因：

根因 A：onReceive() 执行了耗时操作
─────────────────────────────────────────────────────────────────────────────
  // onReceive 中做了网络请求、数据库操作、文件 IO
  // onReceive 是在主线程执行的！

  override fun onReceive(context: Context, intent: Intent) {
      val data = NetworkService.getData()  // 网络请求，同步 → ANR
      val users = DBHelper.queryUsers()     // 数据库，同步 → ANR
      FileInputStream(path).readBytes()      // 文件 IO，同步 → ANR
  }

根因 B：onReceive 中启动了异步任务，但 ANR 已经触发
─────────────────────────────────────────────────────────────────────────────
  // onReceive 中启动了线程/协程，但 onReceive 本身很快就返回了
  // 这不会触发 ANR

  // 但如果 onReceive 中有同步代码 + 异步代码混合，
  // 同步部分阻塞超过 10s → ANR
```

#### 5.2.4 修复方案

```java
// BroadcastReceiver 中的耗时操作必须异步化

// 反例
override fun onReceive(context: Context, intent: Intent) {
    val data = fetchFromNetwork()  // 同步网络请求 → ANR
}

// 正例一：goAsync + 线程池
override fun onReceive(context: Context, intent: Intent) {
    val pendingResult = goAsync()
    receiverExecutor.execute { // 应用复用的有界 Executor；提交失败也必须 finish
        try {
            val data = fetchFromNetwork()
            // 处理数据
        } finally {
            pendingResult.finish()
        }
    }
}

// 正例二：直接用 WorkManager 处理广播逻辑
```

---

### 5.3 Service ANR

#### 5.3.1 Log 特征

```text
执行生命周期：executing service com.example/.MyService, waited ...ms
转前台超时：Context.startForegroundService() did not then call Service.startForeground()
```

#### 5.3.2 超时源码位置

执行超时：`ActivityManagerConstants.SERVICE_TIMEOUT/SERVICE_BACKGROUND_TIMEOUT` → `ActiveServices.serviceTimeout()`。
转前台超时：`scheduleServiceForegroundTransitionTimeoutLocked()` → `mServiceFGAnrTimer` → `serviceForegroundTimeout()` → `SERVICE_FOREGROUND_TIMEOUT_ANR_MSG` → `serviceForegroundTimeoutANR()`。

#### 5.3.3 根因分析

1. `onCreate/onStartCommand/onBind/onDestroy` 在主线程执行，等待锁或同步 I/O 会消耗生命周期预算。
2. `startForegroundService()` 后未及时 `startForeground()` 是独立期限；本 tag 默认转前台等待 30 秒、随后 ANR 延迟 10 秒，不应写成固定 5 秒。不要把用于后台启动资格判断的 `mFgsStartForegroundTimeoutMs`（默认 10 秒）混入此期限。
3. `serviceForegroundCrash()` 仍存在并产生 `ForegroundServiceDidNotStartInTimeException`；它不是上述 timer 回调函数。不能凭旧版本异常文档把本 tag 的 `serviceForegroundTimeoutANR()` 改写为必然 crash。
4. 服务进程冷启动慢会影响执行链，但 LMKD 终止本身不是 Service ANR。

#### 5.3.4 修复方案

```java
// 1. Service 生命周期中不做耗时操作
onCreate() {
    super.onCreate()
    // 不要在这里做数据库打开、网络请求
    // 改为在 onStartCommand 中用线程池处理，或用懒加载
}

// 2. startForegroundService 后必须及时调用 startForeground
class MyService : LifecycleService() {
    override fun onCreate() {
        super.onCreate()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForeground(NOTIFICATION_ID, notification)
        }
        // 异步处理耗时任务
        lifecycleScope.launch(Dispatchers.IO) {
            processHeavyTask()
        }
        return START_NOT_STICKY
    }
}

// 3. 用 WorkManager 替代后台 Service（推荐）
WorkManager.getInstance(context).enqueue(workRequest)
```

---

### 5.4 ContentProvider ANR

#### 5.4.1 Log 特征

```text
ANR in com.example.app (CONTENT_PROVIDER_TIMEOUT)
Reason: ContentProvider not responding
# timeout publishing content providers 是初始化失败退出，不是同一种 ANR
```

#### 5.4.2 超时源码位置

- 超时消息: `ActivityManagerService.MainHandler` (`WAIT_FOR_CONTENT_PROVIDER_TIMEOUT_MSG`)
- 等待失败：AMS.MainHandler；发布失败：`processContentProviderPublishTimedOutLocked()`；调用 ANR：`appNotRespondingViaProvider()`

#### 5.4.3 根因分析

```text
根因 A：ContentProvider.onCreate 中做了耗时操作
─────────────────────────────────────────────────────────────────────────────
  class MyProvider : ContentProvider() {
      override fun onCreate(): Boolean {
          // 数据库连接、配置加载、网络初始化
          // 全部在主线程执行
          DB = SQLiteDatabase.openDatabase(path, ...)
          return true
      }
  }

根因 B：第三方 SDK 通过 ContentProvider 初始化拖慢启动
─────────────────────────────────────────────────────────────────────────────
  // 很多 SDK（如旧版 LeakCanary、Firebase）注册空 CP 来触发初始化
  // 这会严重拖慢冷启动
```

#### 5.4.4 修复方案

```java
// 1. ContentProvider.onCreate 中不做耗时操作
class MyProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // 只做必须的事情，数据库连接放到首次 query 时懒加载
        return true
    }

    override fun query(...): Cursor? {
        if (!dbReady) {
            initDB()  // 懒加载
        }
        return db.query(...)
    }
}

// 2. 用 AndroidX App Startup 管理初始化依赖
// 默认 InitializationProvider 仍同步初始化；先移除对应自动初始化 meta-data，
// 才能在所需时机手动调用。线程由 SDK 契约决定，不存在 false=后台线程 参数。
AppInitializer.getInstance(context).initializeComponent(SDK1Initializer::class.java)

// 3. 检查并移除不必要的 ContentProvider 声明
// AndroidManifest.xml 中搜索 <provider>
// 按 SDK 契约移除不需要的自动初始化 Provider，并补齐手动初始化；非导出 Provider 也可能承担必要工作
```

---

## 6. ANR 排查方法

### 6.1 traces.txt 分析

```text
获取方式：

# Android 10 及以下
adb pull /data/anr/ ./anr/ # 仅可读该目录的授权设备

# Android 11+（需要 root）
adb bugreport bugreport.zip # 量产设备；不要依赖 su 或固定 traces.txt

# 通过 bugreport 获取
adb bugreport bugreport.zip
# 解压后在 FS/data/anr/ 目录下
```

**traces.txt 结构解读**:

```text
----- pid 12345 at 2024-01-01 12:00:00 -----
Cmd line: com.example.app
...
ANR in com.example.app (Input dispatching timed out)
Reason: Input dispatching timed out waiting to send event to app.
Load: 8.2 / 7.1 / 5.3
CPU usage from 0s to 5s ago:
  12% 345% / -3%: user / kernel

DALVIK THREADS (14 threads):
"main" prio=5 tid=1 Blocked
  - locked by "thread-2" tid=3   ← 主线程在等 tid=3 持有的锁
  at com.example.MyClass.doSomething(Native Method)
  ...
"thread-2" prio=5 tid=3 Runnable
  at com.example.MyClass.loadData(Native Method)   ← tid=3 在这里卡住了
  at java.lang.Thread.run(Thread.java:xxx)
  ...
```

**关键字段解读**:

```text
"main" prio=5 tid=1 Blocked
  prio=5  → 正常优先级
  prio=10 → Java 线程优先级，不代表正在运行
  Blocked → 在等锁
  WAIT    → 在 Object.wait() 或 Condition.await()
  SLEEPING→ 在 Thread.sleep()
  NATIVE  → 在执行 Native 代码
  Runnable→ Java 可运行状态；是否占 CPU 用 sched 轨道判断

tid=X Blocked
  - locked by "thread-Y" tid=Z
  → 正在等 tid=Z 持有的锁

Binder.transact
  → 主线程在做跨进程调用，需要看对端进程状态
```

### 6.2 Perfetto 精准分析

```bash
# 录制包含 ftrace + 进程调度的 trace
adb shell perfetto \
  -c - --txt \
  -o /data/misc/perfetto-traces/trace.perfetto-trace \
  <<'EOF'
buffers: { size_kb: 63488 fill_policy: RING_BUFFER }
data_sources: {
    config {
        name: "linux.ftrace"
        ftrace_config {
            ftrace_events: "sched/sched_switch"
            ftrace_events: "sched/sched_wakeup"
            ftrace_events: "power/cpu_frequency"
            ftrace_events: "power/cpu_idle"
            atrace_categories: "input"
            atrace_categories: "am"
            atrace_apps: "com.example.app"
        }
    }
}
data_sources: { config { name: "linux.process_stats" } }
duration_ms: 15000
EOF

adb pull /data/misc/perfetto-traces/trace.perfetto-trace .
# 打开 https://ui.perfetto.dev 导入分析
```

---

## 7. ANR 防御体系

### 7.1 主线程安全红线

```text
严格禁止在主线程执行以下操作：

┌─────────────────────────────────────────────────────────────────┐
│                      主线程安全红线                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  严格禁止：                                                       │
│  ✗ 同步网络执行/读取响应体；允许在主线程发起 enqueue 或 Retrofit suspend │
│  ✗ 数据库读写（SharedPreference / Room / SQLite）               │
│  ✗ 同步文件 IO；1KB 也可能触发慢存储等待                                │
│  ✗ 大图解码；按解码像素和耗时评估，不按压缩文件 100KB 划线                              │
│  ✗ 超出交互预算的 JSON 解析，无通用 10KB 阈值                                │
│  ✗ 无界锁等待或持锁执行慢操作；短临界区不等于 ANR                                   │
│  ✗ SharedPreference 的同步 read/write                           │
│                                                                  │
│  代码审查工具（StrictMode）：                                     │
│                                                                  │
│  StrictMode.setThreadPolicy(                                    │
│      ThreadPolicy.Builder()                                    │
│          .detectDiskReads()                                     │
│          .detectDiskWrites()                                    │
│          .detectNetwork()                                       │
│          .penaltyLog()                                          │
│          .build())                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 架构设计原则

```text
架构设计原则：

1. 减少跨线程共享状态
   - 用消息队列（LiveData、EventBus）替代直接共享变量
   - 用 Kotlin Flow / RxJava 替代回调地狱

2. 读多写少用读写锁
   val rwLock = ReentrantReadWriteLock()
   rwLock.readLock().lock()    // 读不阻塞读
   try { ... } finally { rwLock.readLock().unlock() }

3. 高并发计数用 CAS
   val counter = AtomicInteger()

4. 避免主线程持有锁时调用外部方法
   // 反例
   synchronized(lock) {
       someSDK.method()  // SDK 内部可能做 IO/Binder
   }
```

### 7.3 Binder 调用防御

同步 Binder 没有通用的客户端强制超时 API。将可能慢的远端调用移到后台，并在业务层提供取消、降级、并发上限；不能在主线程 `Future.get(3s)`，那仍阻塞三秒。取消 Future 也不保证停止 Binder 对端。

```kotlin
// 结果在 Cursor.use 内复制；页面销毁时不继续渲染。
viewLifecycleOwner.lifecycleScope.launch {
    val names = queryNames(requireContext().contentResolver, uri)
    render(names)
}
```

只有受线程契约允许的调用才能迁移到工作线程；WindowManager/View 操作往往要求所属 UI 线程，不能一律移走。跨进程定位需要同时查看客户端等待及服务端线程/锁。

---

## 附录：源码索引

| 功能 | 固定 tag 源码 | 函数证据 |
|---|---|---|
| 执行/转前台 | [ActiveServices.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ActiveServices.java) | `serviceTimeout / serviceForegroundTimeout / serviceForegroundTimeoutANR` |
| 广播 | [BroadcastQueueImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/BroadcastQueueImpl.java) | `calculateBroadcastTimeout / finishReceiverActiveLocked` |
| Provider | [ContentProviderHelper.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ContentProviderHelper.java) | `processContentProviderPublishTimedOutLocked / appNotRespondingViaProvider` |
| 计时器 | [AnrTimer.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/utils/AnrTimer.java) | `start / expire / accept / discard` |
| 调度 | [AnrHelper.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/AnrHelper.java) | `appNotResponding / AnrConsumerThread.run` |
| 处理 | [ProcessErrorStateRecord.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ProcessErrorStateRecord.java) | `appNotResponding / skipAnrLocked` |

Input 源码：[InputDispatcher.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp)，`processAnrsLocked/onAnrLocked`。广播时间范围：[官方诊断指南](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs)。
