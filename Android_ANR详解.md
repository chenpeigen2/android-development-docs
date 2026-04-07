# Android ANR 详解

> 作者：OpenClaw | 日期：2026-03-09

---

## 目录

1. [概述](#1-概述)
2. [深度解析：资深工程师视角](#2-深度解析资深工程师视角)
   - 2.1 [ANR 的本质——系统的"底线思维"](#21-anr-的本质系统的底线思维)
   - 2.2 [ANR 的触发阈值与分类](#22-anr-的触发阈值与分类)
   - 2.3 [ANR 的底层触发原理](#23-anr-的底层触发原理)
   - 2.4 [复杂 ANR 场景深度剖析](#24-复杂-anr-场景深度剖析)
   - 2.5 [资深工程师的排查工具链](#25-资深工程师的排查工具链)
   - 2.6 [架构级的 ANR 防御体系](#26-架构级的-anr-防御体系)
3. [ANR 原理](#3-anr-原理)
   - 3.1 [什么是 ANR](#31-什么是-anr)
   - 3.2 [ANR 触发机制](#32-anr-触发机制)
   - 3.3 [ANR 超时时间](#33-anr-超时时间)
4. [ANR 类型](#4-anr-类型)
   - 4.1 [KeyDispatchTimeout](#41-keydispatchtimeout)
   - 4.2 [BroadcastTimeout](#42-broadcasttimeout)
   - 4.3 [ServiceTimeout](#43-servicetimeout)
   - 4.4 [ContentProviderTimeout](#44-contentprovidertimeout)
5. [ANR 常见原因](#5-anr-常见原因)
   - 5.1 [主线程阻塞](#51-主线程阻塞)
   - 5.2 [CPU 负载过高](#52-cpu-负载过高)
   - 5.3 [死锁](#53-死锁)
   - 5.4 [Binder 调用阻塞](#54-binder-调用阻塞)
   - 5.5 [SP 导致 ANR](#55-sp-导致-anr)
6. [ANR 分析方法](#6-anr-分析方法)
   - 6.1 [traces.txt 分析](#61-tracestxt-分析)
   - 6.2 [ANR traces 位置](#62-anr-traces-位置)
   - 6.3 [分析流程](#63-分析流程)
   - 6.4 [ANR Info 关键字段](#64-anr-info-关键字段)
7. [ANR 监控方案](#7-anr-监控方案)
   - 7.1 [FileObserver 监控](#71-fileobserver-监控)
   - 7.2 [WatchDog 机制](#72-watchdog-机制)
   - 7.3 [ANR-WatchDog 库](#73-anr-watchdog-库)
   - 7.4 [Matrix ANR 检测](#74-matrix-anr-检测)
8. [ANR 优化策略](#8-anr-优化策略)
   - 8.1 [避免主线程耗时操作](#81-避免主线程耗时操作)
   - 8.2 [优化 BroadcastReceiver](#82-优化-broadcastreceiver)
   - 8.3 [优化 Service](#83-优化-service)
   - 8.4 [优化 SP](#84-优化-sp)
   - 8.5 [优化 Binder 调用](#85-优化-binder-调用)
9. [StrictMode 严格模式](#9-strictmode-严格模式)
10. [常见问题](#10-常见问题)
11. [知识体系总结](#11-知识体系总结)

---

## 1. 概述

ANR（Application Not Responding）是 Android 系统的一种保护机制。当主线程被阻塞超过一定时间，系统会弹出 ANR 对话框，提示用户应用无响应。理解 ANR 的原理、掌握分析和优化方法，是每个 Android 开发者的必备技能。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 影响分析                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  用户体验：
  - 应用卡顿，无法交互
  - 弹出 ANR 对话框
  - 用户可能选择强制关闭应用
  - 严重影响应用评分

  系统影响：
  - 系统资源被占用
  - 可能触发 Low Memory Killer
  - 影响其他应用运行

  开发影响：
  - 崩溃率上升
  - 应用商店排名下降
  - 用户流失
```

---

## 2. 深度解析：资深工程师视角

作为一名资深 Android 开发工程师，看待 ANR（Application Not Responding，应用无响应）不能仅仅停留在"主线程做了耗时操作"这个表层概念上。我们需要从系统调度机制、底层触发原理、监控工具链、复杂场景排查以及架构级防御这五个维度进行深度解构。

### 2.1 ANR 的本质——系统的"底线思维"

ANR 本质上不是 Bug，而是 Android 系统的一种自我保护机制。

Android 的设计哲学是：所有的 UI 绘制、用户交互事件（触摸、按键）都必须在主线程（UI 线程）中以极高的优先级实时响应。当系统发现主线程被阻塞，无法在规定时间内处理关键事件时，为了防止系统卡死，它会弹出 ANR 对话框，让用户决定是等待还是强杀。

### 2.2 ANR 的触发阈值与分类

不同类型的消息在主线程 MessageQueue 中的超时阈值不同：

```
┌──────────────────────────────────┬──────────┬───────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│         触发场景                 │ 超时时间  │       底层分发者           │                                                 核心机制                                             │
├──────────────────────────────────┼──────────┼───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Input 事件 (按键、触摸)         │ 5秒      │ InputDispatcher (Native层)│ 最严格。连续多个事件超时才会触发，单次超时只打印日志（慢分发）。                                       │
├──────────────────────────────────┼──────────┼───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ BroadcastReceiver (前台广播)    │ 10秒     │ AMS (Java层)              │ onReceive() 执行超时。后台广播通常是 60 秒（但现在后台广播受限严重）。                                   │
├──────────────────────────────────┼──────────┼───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Service (前台服务)              │ 20秒     │ ActivityManager (Java层)  │ onCreate(), onStart(), onBind() 等生命周期方法执行超时。后台服务 200 秒。                               │
├──────────────────────────────────┼──────────┼───────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ContentProvider                 │ 10秒     │ AMS (Java层)              │ publishContentProviders() 或 getContentProviderImpl() 超时。                                          │
└──────────────────────────────────┴──────────┴───────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

> **资深视角的坑**：很多人以为只有 5 秒和 10 秒。实际上，如果是在 ContentProvider 的 onCreate() 中发生了 ANR，系统抛出的异常信息里往往显示的是 Service 超时（20秒），因为应用启动时绑定 ContentProvider 是在 Application.attachBaseContext() 之后，Application.onCreate() 之前，这个流程被包裹在启动 Activity/Service 的流程中。

### 2.3 ANR 的底层触发原理

ANR 的触发分为"消息超时检测"和"ANR 弹窗决策"两步，且两者是异步的。

#### 2.3.1 超时检测机制：Handler 的 sendMessageDelayed

以 Service 为例，当 AMS 调用应用进程的 Service 生命周期时，会向主线程的 MessageQueue 发送一条延迟消息（例如 SERVICE_TIMEOUT_MSG，20秒）。

```
正常情况：应用进程在 20 秒内执行完毕，主动向 AMS 发送完成消息，
        AMS 拿到完成消息后，从 Queue 中移除那条延迟消息。

ANR  情况：20 秒后，那条延迟消息被主线程 Looper 取出执行，
        触发 AMS.checkTimeOut()。
```

#### 2.3.2 Input 超时的特殊性（Native 层监控）

从 Android 11 开始，Input ANR 的监控完全下沉到了 Native 层的 InputDispatcher。

它不再依赖 Java 层的 Handler 延迟消息，而是基于时间戳比对。当应用主线程通过 NativeInputEventReceiver 将事件从底层取走后，InputDispatcher 会记录时间。如果在这个连接上长时间没有收到应用的"finished"信号，就会在 Native 层直接 dump traces 并触发 ANR。

#### 2.3.3 ANR 的弹窗决策（为什么有时"暗杀"不弹窗？）

当超时触发后，系统并不会立刻弹窗，而是执行以下逻辑：

```
1. Dump Traces
   系统发送 SIGNAL_QUIT (信号 3) 给目标进程，
   让其在 /data/anr/traces.txt 中写入各线程的调用栈。

2. 等待 Shell 杀死
   系统启动一个 "ANR Manager" 线程，
   执行 kill -3 <pid>，并等待一段时间（通常几秒）看进程是否死亡。

3. 状态判断
   - 如果在等待期间，用户已经切到了后台（进程不可见），
     系统会直接在后台默默杀死进程，不弹窗。
   - 如果进程处于前台，且 dump 完成，
     系统才会向 UI 线程发送一条消息，弹出著名的"应用无响应"对话框。
```

### 2.4 复杂 ANR 场景深度剖析

在实际大厂应用中，简单的耗时操作早就被规范消灭了，剩下的都是疑难杂症：

#### 2.4.1 锁竞争导致的"假死"（最常见难点）

```
现象：主线程其实只执行了一行代码 synchronized(obj)，但就是卡住了。

原理：子线程持有锁 obj，且子线程因为某种原因（如死锁、网络阻塞、Binder 调用超时）被挂起。
     主线程等不到锁，发生 ANR。

排查：在 traces.txt 中，主线程状态必然是 BLOCKED 或 WAITING。
     此时不能只看主线程，必须全局搜索 holding 或 waiting to lock，
     找到持有锁的那个"罪魁祸首"线程。
```

#### 2.4.2 Binder 调用阻塞（跨进程坑）

```
现象：主线程调用了一个系统服务的方法（如 ContentResolver.query()，
     PackageManager.getPackageInfo()），或者调用了另一个进程的 AIDL 接口，结果卡住。

原理：客户端主线程通过 Binder 代理对象发请求，会挂起当前线程等待服务端返回。
     如果服务端（可能是别的 App 或者系统服务）繁忙或死锁，你的主线程就陪葬了。

排查：Traces 中主线程状态通常是 NATIVE 或 BLOCKED，
     栈帧里会出现 Binder.execTransact 等字样。
```

#### 2.4.3 内存问题引发的 ANR（隐蔽性极强）

```
现象：没有耗时操作，没有锁竞争，但在低端机上频繁 ANR。

原理：
1. GC 频繁：内存抖动或内存泄漏导致频繁 GC，
   GC 会暂停所有应用线程（包括主线程，特别是 ART 下的 foreground GC），
   累积超过阈值触发 ANR。

2. Low Memory Killer (LMK)：系统内存极度紧张时，会优先杀后台。
   但即使不杀前台，系统在分配内存时如果极度艰难，
   也会导致主线程调度延迟。
```

#### 2.4.4 死锁

```
原理：经典的 AB-BA 锁问题。
     虽然 Java 层有 ThreadMXBean 可以检测死锁，
     但如果是 Java 锁与 Native 锁（如 pthread_mutex_t）交叉死锁，
     系统往往无法自动检测，只能靠人肉看 traces。
```

### 2.5 资深工程师的排查工具链

遇到线上 ANR，别只盯着 traces.txt：

```
1. Perfetto (取代 Systrace)
   这是目前排查性能和 ANR 的最强神器。
   Traces 只是某一瞬间的切片，而 Perfetto 记录了整个系统前几秒的完整时间线。
   你能清楚看到 CPU 调度情况、主线程到底是在跑 Java 代码、跑 Native 代码、
   还是在等锁、等 IO。

2. AnrWatchDog (自研监控)
   系统 ANR 弹窗有延迟且可能被隐藏。
   我们在应用内起一个子线程，定期向主线程 post 一个空消息，
   如果超过比如 3 秒没执行，就认为发生了"准 ANR"，
   主动抓取当前堆栈上报到 APM 平台。
   这能抓到大量系统没弹窗的"暗卡"。

3. Logcat 全局搜索
   不要只搜 ANR in。
   要搜 Input dispatching timed out（Input ANR 前兆）、
   Slow delivery（慢分发）、Slow operation（慢操作，Android 12+ 增强）。

4. 线上 APM 矩阵
   结合 Matrix (微信开源) 或 Boom 等工具，
   监控主线程耗时操作、IO 监控、线程池监控。
```

### 2.6 架构级的 ANR 防御体系

作为资深开发，不仅要能排查，更要能在架构上避免：

#### 2.6.1 主线程调度隔离

```
严格规范：主线程绝对禁止网络请求、数据库读写、大文件 IO、
        SharedPreference apply（改用 MMKV 或异步 commit）、复杂 JSON 解析。

架构解耦：使用协程（Dispatchers.Main）或 RxJava 切换线程，
        确保链式调用中任何一步都不意外回到主线程做耗时操作。
```

#### 2.6.2 锁降级与无锁化设计

```
- 在架构设计中，尽量减少跨线程的共享状态。
- 如果必须同步，对于读多写少的场景，用 ReadWriteLock 替代 synchronized。
- 对于高并发计数，使用 AtomicInteger 等 CAS 类。
```

#### 2.6.3 Binder 调用防御

```
- 所有跨进程调用（特别是调系统服务），在主线程调用时必须加上超时保护
  （虽然有些系统 API 无法改，但自己的 AIDL 可以设计异步回调模式）。
- 对于 ContentProvider 的查询，如果数据量大，
  必须走异步加载（如 CursorLoader 或分页加载）。
```

#### 2.6.4 启动阶段专项治理

```
- 移除 ContentProvider 滥用：
  很多第三方 SDK（如 Firebase, LeakCanary 旧版）通过注册空 CP 来初始化，
  这会严重拖慢冷启动，极易在低配机引起 ContentProvider ANR。
  应改用 AppStartUp 库统一管理初始化。

- 延迟初始化：非必要初始化任务延迟到首页绘制完成后
  （IdleHandler 或 postDelayed）。
```

> **总结**：ANR 不是简单的"写错代码"，它是 Android 复杂的进程间通信（Binder）、系统调度机制、内存管理和应用层逻辑相互碰撞的结果。资深工程师面对 ANR，脑海中的第一反应应该是：是 CPU 抢不到？是锁被占用了？是等 Binder 返回？还是 GC 卡住了？借助 Perfetto 这类系统级工具，结合无死角的自研监控，才能真正将 ANR 控制在 P99.9 的指标之内。

---

## 3. ANR 原理

### 3.1 什么是 ANR

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         什么是 ANR                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：Application Not Responding（应用无响应）

  触发条件：
  1. 主线程在规定时间内没有处理完输入事件（按键、触摸等）
  2. BroadcastReceiver 在规定时间内没有执行完
  3. Service 在规定时间内没有执行完生命周期方法
  4. ContentProvider 在规定时间内没有完成发布

  本质：
  - 主线程被阻塞，无法响应消息
  - 系统检测到超时，触发 ANR
  - 弹出对话框供用户选择
```

### 3.2 ANR 触发机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 触发机制                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  核心组件：
  - ActivityManagerService（AMS）：负责 ANR 检测
  - Handler：消息调度机制
  - Looper：主线程消息循环
  - InputDispatching：输入事件分发

  触发流程：

  1. 事件发生
     - 用户按键/触摸
     - 发送广播
     - 启动 Service
     - 发布 ContentProvider

  2. AMS 记录时间戳
     - 记录事件开始时间
     - 设置超时定时器

  3. 定时检查
     - 超时时间到，检查是否完成
     - 未完成 → 触发 ANR

  4. ANR 处理
     - dump 堆栈信息到 traces.txt
     - 弹出 ANR 对话框
     - 记录 ANR 日志
```

### 3.3 ANR 超时时间

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 超时时间                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────┬───────────────────────────────────────────────────┐
  │       ANR 类型       │              超时时间（默认）                       │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 输入事件分发          │  5 秒                                            │
  │ (KeyDispatchTimeout) │  Activity.java: KEY_DISPATCHING_TIMEOUT = 5000  │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 前台广播              │  10 秒                                           │
  │ (BroadcastTimeout)   │  ActivityManagerService: BROADCAST_FG_TIMEOUT   │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 后台广播              │  60 秒                                           │
  │ (BroadcastTimeout)   │  ActivityManagerService: BROADCAST_BG_TIMEOUT   │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 前台 Service          │  20 秒                                           │
  │ (ServiceTimeout)     │  ActiveServices: SERVICE_TIMEOUT                │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ 后台 Service          │  200 秒                                          │
  │ (ServiceTimeout)     │  ActiveServices: SERVICE_BACKGROUND_TIMEOUT     │
  ├─────────────────────┼───────────────────────────────────────────────────┤
  │ ContentProvider      │  10 秒                                           │
  │ (ProviderTimeout)    │  ActivityManagerService: CONTENT_PROVIDER_TIMEOUT│
  └─────────────────────┴───────────────────────────────────────────────────┘

  源码位置：

  // frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java
  static final int BROADCAST_FG_TIMEOUT = 10 * 1000;  // 前台广播 10 秒
  static final int BROADCAST_BG_TIMEOUT = 60 * 1000;  // 后台广播 60 秒
  static final int CONTENT_PROVIDER_TIMEOUT = 10 * 1000; // ContentProvider 10 秒

  // frameworks/base/core/java/android/app/Activity.java
  static final int KEY_DISPATCHING_TIMEOUT = 5 * 1000; // 输入事件 5 秒

  // frameworks/base/services/core/java/com/android/server/am/ActiveServices.java
  static final int SERVICE_TIMEOUT = 20 * 1000;      // 前台 Service 20 秒
  static final int SERVICE_BACKGROUND_TIMEOUT = 200 * 1000; // 后台 Service 200 秒
```

---

## 4. ANR 类型

### 4.1 KeyDispatchTimeout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KeyDispatchTimeout（输入事件超时）                        │
└─────────────────────────────────────────────────────────────────────────────┘

  触发条件：主线程在 5 秒内没有处理完输入事件

  常见原因：
  1. 主线程执行耗时操作
     - 网络请求
     - 文件 I/O
     - 数据库操作
     - 复杂计算

  2. 主线程被锁阻塞
     - synchronized 锁等待
     - ReentrantLock 阻塞
     - 死锁

  3. Binder 调用阻塞
     - 同步 Binder 调用
     - 跨进程通信慢

  4. 系统 CPU 负载过高
     - 进程调度延迟
     - 系统资源紧张

  输入事件分发流程：

  InputEvent → InputDispatcher → InputChannel → ViewRootImpl
       │                                      │
       ▼                                      ▼
  AMS 检测超时                        DecorView.dispatchTouchEvent
       │                                      │
       ▼                                      ▼
  通知 AMS                            Activity.dispatchTouchEvent
       │                                      │
       ▼                                      ▼
  触发 ANR                            View.onTouchEvent
```

### 4.2 BroadcastTimeout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BroadcastTimeout（广播超时）                              │
└─────────────────────────────────────────────────────────────────────────────┘

  触发条件：
  - 前台广播：10 秒
  - 后台广播：60 秒

  常见原因：
  1. onReceive() 执行耗时操作
     - 网络请求
     - 文件 I/O
     - 数据库操作

  2. 有序广播阻塞
     - 前一个接收者处理慢
     - 等待后续接收者

  3. 静态广播启动进程
     - 进程启动耗时
     - 资源初始化

  // 错误示例
  public class MyReceiver extends BroadcastReceiver {
      @Override
      public void onReceive(Context context, Intent intent) {
          // 网络请求 - 耗时操作！
          String result = NetworkUtil.get("http://example.com");
      }
  }

  // 正确示例
  public class MyReceiver extends BroadcastReceiver {
      @Override
      public void onReceive(Context context, Intent intent) {
          // 启动 Service 处理
          Intent service = new Intent(context, MyService.class);
          context.startService(service);
      }
  }
```

### 4.3 ServiceTimeout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ServiceTimeout（Service 超时）                            │
└─────────────────────────────────────────────────────────────────────────────┘

  触发条件：
  - 前台 Service：20 秒
  - 后台 Service：200 秒

  涉及方法：
  - onCreate()
  - onStartCommand()
  - onBind()
  - onUnbind()
  - onDestroy()

  // 错误示例
  public class MyService extends Service {
      @Override
      public void onCreate() {
          super.onCreate();
          // 耗时操作！
          for (int i = 0; i < 100000; i++) {
              // 复杂计算
          }
      }
  }

  // 正确示例
  public class MyService extends Service {
      @Override
      public void onCreate() {
          super.onCreate();
          // 启动子线程处理
          new Thread(() -> {
              // 耗时操作
          }).start();
      }
  }

  // 使用 IntentService（已废弃，推荐使用 JobIntentService）
  public class MyIntentService extends IntentService {
      public MyIntentService() {
          super("MyIntentService");
      }

      @Override
      protected void onHandleIntent(Intent intent) {
          // 在子线程执行，不会 ANR
      }
  }
```

### 4.4 ContentProviderTimeout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                ContentProviderTimeout（ContentProvider 超时）                │
└─────────────────────────────────────────────────────────────────────────────┘

  触发条件：10 秒

  涉及方法：
  - onCreate()
  - query()
  - insert()
  - update()
  - delete()
  - getType()

  // 错误示例
  public class MyProvider extends ContentProvider {
      @Override
      public boolean onCreate() {
          // 耗时操作！
          initDatabase(); // 可能很慢
          return true;
      }

      @Override
      public Cursor query(Uri uri, String[] projection, ...) {
          // 网络请求 - 耗时！
          return networkQuery(uri);
      }
  }

  // 正确示例
  public class MyProvider extends ContentProvider {
      @Override
      public boolean onCreate() {
          // 延迟初始化
          return true;
      }

      @Override
      public Cursor query(Uri uri, String[] projection, ...) {
          // 只做本地查询
          return localQuery(uri);
      }
  }
```

---

## 5. ANR 常见原因

### 5.1 主线程阻塞

```java
// 错误示例：主线程执行耗时操作

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 1. 网络请求
        String result = NetworkUtil.get("http://example.com"); // ANR!
        
        // 2. 文件 I/O
        String content = readFile("/sdcard/large_file.txt"); // ANR!
        
        // 3. 数据库操作
        List<User> users = database.getAllUsers(); // ANR!
        
        // 4. 复杂计算
        for (int i = 0; i < 10000000; i++) {
            Math.sqrt(i); // ANR!
        }
        
        // 5. Thread.sleep()
        Thread.sleep(10000); // ANR!
    }
}

// 正确示例：使用子线程

// 1. 使用 Thread
new Thread(() -> {
    String result = NetworkUtil.get("http://example.com");
    runOnUiThread(() -> updateUI(result));
}).start();

// 2. 使用 AsyncTask
new AsyncTask<Void, Void, String>() {
    @Override
    protected String doInBackground(Void... voids) {
        return NetworkUtil.get("http://example.com");
    }
    @Override
    protected void onPostExecute(String result) {
        updateUI(result);
    }
}.execute();

// 3. 使用 ExecutorService
ExecutorService executor = Executors.newCachedThreadPool();
executor.execute(() -> {
    String result = NetworkUtil.get("http://example.com");
    runOnUiThread(() -> updateUI(result));
});

// 4. 使用 Kotlin Coroutines（推荐）
lifecycleScope.launch(Dispatchers.IO) {
    val result = NetworkUtil.get("http://example.com")
    withContext(Dispatchers.Main) {
        updateUI(result)
    }
}
```

### 5.2 CPU 负载过高

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CPU 负载过高                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  问题：即使主线程没有耗时操作，CPU 负载过高也可能导致 ANR

  原因：
  1. 后台线程占用大量 CPU
  2. 多个进程同时高负载
  3. 系统进程资源紧张
  4. GC 频繁触发

  症状：
  - traces.txt 显示主线程在处理其他消息
  - CPU 使用率持续很高
  - 多个线程处于 RUNNABLE 状态

  解决方案：
  1. 优化后台任务，降低优先级
  2. 使用 Process.setThreadPriority() 降低子线程优先级
  3. 减少后台线程数量
  4. 使用 JobScheduler 在合适时机执行

  // 降低线程优先级
  new Thread(() -> {
    Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);
    // 后台任务
  }).start();
```

### 5.3 死锁

```java
// 死锁示例

public class DeadlockExample {
    private final Object lock1 = new Object();
    private final Object lock2 = new Object();

    public void method1() {
        synchronized (lock1) {
            // 主线程持有 lock1，等待 lock2
            synchronized (lock2) {
                // 永远无法到达这里
            }
        }
    }

    public void method2() {
        synchronized (lock2) {
            // 子线程持有 lock2，等待 lock1
            synchronized (lock1) {
                // 永远无法到达这里
            }
        }
    }
}

// ANR traces.txt 会显示：
// "main" prio=5 tid=1 Blocked
//   - waiting to lock <0x12345678> (a java.lang.Object)
//   - locked <0x87654321> (a java.lang.Object)

// 避免死锁：
// 1. 固定锁顺序
// 2. 使用 tryLock() 超时
// 3. 减少锁粒度
// 4. 使用无锁数据结构
```

### 5.4 Binder 调用阻塞

```java
// Binder 调用阻塞示例

// 1. 系统 Service 调用
public void onClick(View v) {
    // PackageManager 调用可能阻塞
    PackageInfo info = getPackageManager().getPackageInfo(
        getPackageName(), PackageManager.GET_ACTIVITIES);
}

// 2. AMS 调用
public void onClick(View v) {
    // 获取运行中的任务可能阻塞
    List<ActivityManager.RunningTaskInfo> tasks = 
        ((ActivityManager) getSystemService(Context.ACTIVITY_SERVICE))
            .getRunningTasks(10);
}

// 3. 自定义 AIDL 调用
public void onClick(View v) {
    // 同步 Binder 调用
    String result = myAidlService.getData(); // 可能阻塞
}

// 解决方案：
// 1. 缓存结果，避免频繁调用
// 2. 使用异步调用
// 3. 在子线程调用
```

### 5.5 SP 导致 ANR

```java
// SharedPreferences 导致 ANR

// 错误示例：
public void onClick(View v) {
    SharedPreferences sp = getSharedPreferences("config", MODE_PRIVATE);
    
    // 1. getSharedPreferences() 可能阻塞（首次加载）
    // 2. commit() 同步写入，阻塞主线程
    sp.edit().putString("key", "value").commit(); // ANR!
}

// 正确示例：
// 1. 使用 apply() 异步写入
sp.edit().putString("key", "value").apply(); // 异步，不阻塞

// 2. 预加载 SP
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    // 在 Application 中预加载
    SharedPreferencesConfig.preload(this);
}

// 3. 使用 MMKV 替代（腾讯出品，性能更好）
MMKV.defaultMMKV().encode("key", "value");
```

---

## 6. ANR 分析方法

### 6.1 traces.txt 分析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         traces.txt 文件格式                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  // ANR 发生时间
  ----- pid 12345 at 2024-01-01 12:34:56 -----

  // 线程信息
  Cmd line: com.example.app

  // 主线程堆栈
  "main" prio=5 tid=1 Sleeping
    | group="main" sCount=1 dsCount=0 flags=1 obj=0x12345678
    | sysTid=12345 nice=0 cgrp=default sched=0/0 handle=0x12345678
    | state=S schedstat=( 123456789 12345678 12345 ) utm=12 stm=34
    | core=0 HZ=100
    | stack=0x12345678-0x12345678 stackSize=8192KB
    | held mutexes=
    at java.lang.Thread.sleep(Native Method)
    - sleeping on <0x12345678> (a java.lang.Object)
    at java.lang.Thread.sleep(Thread.java:373)
    at java.lang.Thread.sleep(Thread.java:314)
    at com.example.app.MainActivity$1.run(MainActivity.java:42)
    at android.os.Handler.handleCallback(Handler.java:883)
    at android.os.Handler.dispatchMessage(Handler.java:100)
    at android.os.Looper.loop(Looper.java:214)
    at android.app.ActivityThread.main(ActivityThread.java:7356)
    at java.lang.reflect.Method.invoke(Native Method)
    at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run
    at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:950)
```

### 6.2 ANR traces 位置

```bash
# Android 10 及以下
/data/anr/traces.txt

# Android 11+（需要 root）
/data/anr/anr_*

# 通过 adb 获取
adb pull /data/anr/traces.txt ./

# 通过 bugreport 获取
adb bugreport ./bugreport.zip
# 解压后在 FS/data/anr/ 目录下

# 通过 dropbox 获取（系统应用）
adb shell dumpsys dropbox --print 0 app_anr
```

### 6.3 分析流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 分析流程                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  Step 1: 获取 traces.txt
  ─────────────────────────────────────────────────────────────────────────
  - adb pull /data/anr/traces.txt
  - 或从 bugreport 中提取

  Step 2: 找到主线程
  ─────────────────────────────────────────────────────────────────────────
  - 搜索 "main" prio=5 tid=1
  - 查看主线程状态（Sleeping/Blocked/Runnable）

  Step 3: 分析主线程堆栈
  ─────────────────────────────────────────────────────────────────────────
  - 从上往下看调用栈
  - 找到业务代码位置
  - 确定阻塞原因

  Step 4: 检查其他线程
  ─────────────────────────────────────────────────────────────────────────
  - 查看是否有死锁
  - 检查 Binder 调用
  - 查看锁持有情况

  Step 5: 结合 ANR Info
  ─────────────────────────────────────────────────────────────────────────
  - 查看 ANR 类型
  - 检查 CPU 使用率
  - 分析进程状态
```

### 6.4 ANR Info 关键字段

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR Info 关键字段                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  // ANR 类型
  Reason: Input dispatching timed out (Waiting because no window has focus)

  // 进程信息
  PID: 12345
  Reason: executing service com.example.app/.MyService

  // CPU 使用情况
  Load: 8.5 / 7.2 / 5.1   // 1/5/15 分钟负载
  CPU usage from 0ms to 12345ms later (2024-01-01 12:34:56.123):
    50% 12345/com.example.app: 25% user + 25% kernel
    30% 567/system_server: 20% user + 10% kernel
    10% 890/com.android.systemui: 8% user + 2% kernel

  关键分析点：
  1. Reason - ANR 原因
  2. Load - 系统负载
  3. CPU usage - 各进程 CPU 使用率
  4. 主线程状态 - Sleeping/Blocked/Runnable
```

---

## 7. ANR 监控方案

### 7.1 FileObserver 监控

```java
/**
 * 监控 /data/anr/ 目录变化
 * 需要 root 权限或 debuggable 应用
 */
public class ANRFileObserver extends FileObserver {
    private static final String ANR_PATH = "/data/anr/";
    
    public ANRFileObserver() {
        super(ANR_PATH, FileObserver.CREATE | FileObserver.MODIFY);
    }
    
    @Override
    public void onEvent(int event, String path) {
        if (path != null && path.startsWith("anr_")) {
            // 检测到 ANR 文件
            Log.e("ANR", "ANR detected: " + path);
            // 上传或分析 traces
            analyzeANRFile(ANR_PATH + path);
        }
    }
}
```

### 7.2 WatchDog 机制

```java
/**
 * 自定义 WatchDog 检测主线程卡顿
 */
public class ANRWatchDog extends Thread {
    private static final int ANR_TIMEOUT = 5000; // 5 秒
    
    private volatile int tick = 0;
    private volatile boolean reported = false;
    
    private final Runnable ticker = new Runnable() {
        @Override
        public void run() {
            tick = 0;
            reported = false;
        }
    };
    
    @Override
    public void run() {
        setName("ANR-WatchDog");
        
        while (true) {
            boolean needPost = tick == 0;
            tick++;
            
            if (tick == 1 && !reported) {
                if (needPost) {
                    new Handler(Looper.getMainLooper()).post(ticker);
                }
            }
            
            try {
                Thread.sleep(ANR_TIMEOUT);
            } catch (InterruptedException e) {
                break;
            }
            
            // 如果 tick > 1，说明主线程没有响应
            if (tick >= 2 && !reported) {
                reported = true;
                onANRDetect();
            }
        }
    }
    
    private void onANRDetect() {
        Log.e("ANRWatchDog", "ANR detected!");
        // 打印主线程堆栈
        StackTraceElement[] stackTrace = Looper.getMainLooper()
            .getThread().getStackTrace();
        Log.e("ANRWatchDog", Arrays.toString(stackTrace));
    }
}
```

### 7.3 ANR-WatchDog 库

```gradle
// 添加依赖
dependencies {
    implementation 'com.github.anrwatchdog:anrwatchdog:1.4.0'
}
```

```java
// 在 Application 中初始化
public class MyApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        
        new ANRWatchDog()
            .setReportMainThreadOnly()
            .setANRListener(error -> {
                // 自定义处理
                Log.e("ANR", error.getMessage());
            })
            .start();
    }
}
```

### 7.4 Matrix ANR 检测

```gradle
// 添加 Matrix 依赖
dependencies {
    implementation 'com.tencent.matrix:matrix-android-lib:0.8.0'
    implementation 'com.tencent.matrix:matrix-android-commons:0.8.0'
    implementation 'com.tencent.matrix:matrix-trace-canary:0.8.0'
}
```

```java
// 初始化 Matrix
public class MyApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        
        Matrix.Builder builder = new Matrix.Builder(this);
        
        // ANR 检测
        builder.plugin(new TracePlugin(new TraceConfig.Builder()
            .setEnableAnrTrace(true)
            .build()));
        
        Matrix.init(builder.build());
        Matrix.with().startAllPlugins();
    }
}
```

---

## 8. ANR 优化策略

### 8.1 避免主线程耗时操作

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    避免主线程耗时操作                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 网络请求
  ─────────────────────────────────────────────────────────────────────────
  - 使用 OkHttp/Retrofit 异步请求
  - 使用 Coroutines/Okio 异步

  2. 文件 I/O
  ─────────────────────────────────────────────────────────────────────────
  - 使用子线程
  - 使用 Okio 优化

  3. 数据库操作
  ─────────────────────────────────────────────────────────────────────────
  - 使用 Room + Coroutines
  - 使用 WorkManager

  4. 复杂计算
  ─────────────────────────────────────────────────────────────────────────
  - 使用子线程
  - 使用 RenderScript（图像处理）
  - 使用 NDK（复杂计算）
```

### 8.2 优化 BroadcastReceiver

```java
// 1. 避免在 onReceive() 中执行耗时操作
public class MyReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        // 启动 Service 处理
        Intent service = new Intent(context, MyService.class);
        context.startService(service);
    }
}

// 2. 使用 goAsync() 延长处理时间
public class MyReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        final PendingResult pendingResult = goAsync();
        new Thread(() -> {
            try {
                // 耗时操作
            } finally {
                pendingResult.finish();
            }
        }).start();
    }
}

// 3. 动态注册替代静态注册（减少进程启动）
```

### 8.3 优化 Service

```java
// 1. 使用 JobService 替代普通 Service
public class MyJobService extends JobService {
    @Override
    public boolean onStartJob(JobParameters params) {
        // 在子线程执行
        new Thread(() -> {
            // 耗时操作
            jobFinished(params, false);
        }).start();
        return true;
    }
    
    @Override
    public boolean onStopJob(JobParameters params) {
        return false;
    }
}

// 2. 使用 WorkManager
public class MyWorker extends Worker {
    public MyWorker(Context context, WorkerParameters params) {
        super(context, params);
    }
    
    @Override
    public Result doWork() {
        // 后台任务
        return Result.success();
    }
}

// 3. 前台 Service（延长超时时间到 20 秒）
public class MyForegroundService extends Service {
    @Override
    public void onCreate() {
        super.onCreate();
        
        Notification notification = new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Service Running")
            .build();
            
        startForeground(1, notification);
    }
}
```

### 8.4 优化 SP

```java
// 1. 使用 apply() 替代 commit()
SharedPreferences sp = getSharedPreferences("config", MODE_PRIVATE);
sp.edit().putString("key", "value").apply(); // 异步

// 2. 预加载 SP
public class App extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        // 预加载常用 SP
        SharedPreferences preLoad = getSharedPreferences("preload", MODE_PRIVATE);
    }
}

// 3. 使用 MMKV 替代
MMKV kv = MMKV.defaultMMKV();
kv.encode("key", "value"); // 同步但极快
String value = kv.decodeString("key", null);
```

### 8.5 优化 Binder 调用

```java
// 1. 缓存结果
private PackageInfo cachedPackageInfo;

public PackageInfo getPackageInfo() {
    if (cachedPackageInfo == null) {
        cachedPackageInfo = getPackageManager().getPackageInfo(
            getPackageName(), PackageManager.GET_ACTIVITIES);
    }
    return cachedPackageInfo;
}

// 2. 异步调用
new Thread(() -> {
    PackageInfo info = getPackageManager().getPackageInfo(...);
    runOnUiThread(() -> updateUI(info));
}).start();

// 3. 减少调用频率
// 避免频繁调用系统服务
```

---

## 9. StrictMode 严格模式

```java
/**
 * StrictMode 用于检测主线程的磁盘和网络操作
 * 仅在 Debug 模式启用
 */
public class MyApplication extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        
        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(new StrictMode.ThreadPolicy.Builder()
                .detectDiskReads()      // 检测磁盘读
                .detectDiskWrites()     // 检测磁盘写
                .detectNetwork()        // 检测网络操作
                .penaltyLog()           // 打印日志
                .penaltyDialog()        // 弹出对话框
                .build());
                
            StrictMode.setVmPolicy(new StrictMode.VmPolicy.Builder()
                .detectActivityLeaks()  // 检测 Activity 泄漏
                .detectLeakedSqlLiteObjects()  // 检测 SQLite 泄漏
                .penaltyLog()
                .build());
        }
    }
}
```

---

## 10. 常见问题

### 10.1 如何快速定位 ANR？

```
一、获取 ANR 日志
─────────────────────────────────────────────────────────────────────────────
1. 通过 adb 导出 ANR 日志
   adb pull /data/anr/traces.txt
   
   关键信息：
   - ANR in [package]: 发生 ANR 的应用包名
   - Reason: 触发原因（如 Input dispatching timed out）
   - CPU usage: 当时的 CPU 负载
   - DALVIK THREADS (main): 主线程的堆栈信息

2. Android Studio 的 Logcat 过滤
   过滤关键字 ANR in 或 ActivityManager: ANR

二、分析主线程堆栈
─────────────────────────────────────────────────────────────────────────────
1. 查看主线程的阻塞点
   - 找到 "main" prio=5 tid=1
   - 从上往下看调用栈
   - 找到业务代码位置

2. 问题点判断：
   - nativePollOnce: 等待消息时的正常状态
   - BitmapFactory.decodeFile: 耗时操作导致
   - synchronized: 锁等待
   - Binder.execTransact: Binder 调用阻塞

三、使用工具监控主线程
─────────────────────────────────────────────────────────────────────────────
1. Android Studio Profiler
   - CPU Profiler: 记录主线程的方法耗时
   - Method Tracing: 生成 .trace 文件，查看方法调用耗时

2. BlockCanary 或 ANR-WatchDog
   - 自动检测主线程卡顿
   - 输出堆栈信息

四、代码审查与复现
─────────────────────────────────────────────────────────────────────────────
1. 审查主线程是否有耗时操作
2. 检查是否有死锁
3. 检查 Binder 调用频率
4. 尝试复现问题场景

五、优化与预防
─────────────────────────────────────────────────────────────────────────────
1. 异步化改造
   // 使用协程（Kotlin）
   lifecycleScope.launch(Dispatchers.IO) {
       val result = heavyOperation()
       withContext(Dispatchers.Main) {
           updateUI(result)
       }
   }

2. 减少主线程负载
   - 使用 RecyclerView 替代 ListView
   - 避免在 onDraw 中创建对象或执行计算

3. 监控 ANR 率
   - 集成 Firebase Crashlytics 或 Sentry
   - 统计线上 ANR 发生频率
```

### 10.2 如何预防 ANR？

```
1. 严格分离线程职责
   - 主线程仅处理 UI 更新和轻量级逻辑
   - 耗时操作必须放到子线程

2. 使用异步框架
   - Kotlin 协程（推荐）
   - RxJava
   - LiveData
   - WorkManager

3. 监控主线程阻塞
   - 使用 StrictMode 检测磁盘和网络操作
   - 使用性能分析工具（Android Profiler）
   - 使用 ANR 监控库

4. 优化耗时操作
   - 减少数据库查询时间
   - 压缩网络请求数据
   - 使用缓存策略
```

### 10.3 traces.txt 显示 "native" 方法？

```
可能是：
1. Native 代码阻塞
   - JNI 调用耗时
   - Native 库问题

2. 等待锁
   - synchronized 锁等待
   - ReentrantLock 阻塞

3. Binder 调用
   - 跨进程通信阻塞
   - 系统服务调用慢

4. I/O 操作
   - 文件读写
   - 网络请求
```

### 10.4 如何设计一个 ANR 监控工具？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ANR 监控工具设计                                         │
└─────────────────────────────────────────────────────────────────────────────┘

一、主线程 WatchDog 机制
─────────────────────────────────────────────────────────────────────────────
原理：子线程定期向主线程发送"心跳消息"，若超时未响应则认为可能 ANR

public class ANRWatchDog extends Thread {
    private static final int ANR_TIMEOUT = 5000; // 5 秒
    private volatile int tick = 0;
    private volatile boolean reported = false;
    
    private final Runnable ticker = new Runnable() {
        @Override
        public void run() {
            tick = 0;
            reported = false;
        }
    };
    
    @Override
    public void run() {
        setName("ANR-WatchDog");
        
        while (true) {
            boolean needPost = tick == 0;
            tick++;
            
            if (tick == 1 && !reported) {
                if (needPost) {
                    new Handler(Looper.getMainLooper()).post(ticker);
                }
            }
            
            try {
                Thread.sleep(ANR_TIMEOUT);
            } catch (InterruptedException e) {
                break;
            }
            
            // 如果 tick > 1，说明主线程没有响应
            if (tick >= 2 && !reported) {
                reported = true;
                onANRDetect();
            }
        }
    }
}

二、堆栈采样
─────────────────────────────────────────────────────────────────────────────
当检测到超时，抓取主线程堆栈和 CPU 使用率

private void onANRDetect() {
    // 1. 打印主线程堆栈
    StackTraceElement[] stackTrace = Looper.getMainLooper()
        .getThread().getStackTrace();
    String stackTraceString = Log.getStackTraceString(stackTrace);
    
    // 2. 获取 CPU 使用率
    String cpuUsage = getCpuUsage();
    
    // 3. 获取内存信息
    Debug.MemoryInfo memoryInfo = new Debug.MemoryInfo();
    Debug.getMemoryInfo(memoryInfo);
    
    // 4. 组装报告
    ANRReport report = new ANRReport();
    report.setStackTrace(stackTraceString);
    report.setCpuUsage(cpuUsage);
    report.setMemoryInfo(memoryInfo);
    report.setTimestamp(System.currentTimeMillis());
}

三、日志上报
─────────────────────────────────────────────────────────────────────────────
将堆栈信息、设备状态上传至服务器

public void uploadANRReport(ANRReport report) {
    // 1. 序列化报告
    String json = new Gson().toJson(report);
    
    // 2. 上传到服务器
    OkHttpClient client = new OkHttpClient();
    RequestBody body = RequestBody.create(
        MediaType.parse("application/json"), json);
    Request request = new Request.Builder()
        .url("https://api.example.com/anr/report")
        .post(body)
        .build();
    
    client.newCall(request).enqueue(new Callback() {
        @Override
        public void onResponse(Call call, Response response) {
            // 上传成功
        }
        
        @Override
        public void onFailure(Call call, IOException e) {
            // 上传失败，保存到本地
            saveToLocal(report);
        }
    });
}

四、优化策略
─────────────────────────────────────────────────────────────────────────────
1. 采样频率控制
   - 避免过于频繁的检测
   - 使用退避策略

2. 堆栈去重
   - 相同堆栈只上报一次
   - 减少服务器压力

3. 本地缓存
   - 网络不可用时保存到本地
   - 下次启动时重试上传

4. 隐私保护
   - 脱敏敏感信息
   - 用户授权后上传
```

### 10.5 主线程执行网络请求一定会导致 ANR 吗？

```
答案：不一定

分析：
─────────────────────────────────────────────────────────────────────────────
1. ANR 触发条件
   - 输入事件超时：5 秒
   - 如果网络请求耗时 < 5 秒，不会触发 ANR
   - 但仍会导致界面卡顿

2. 风险
   - 网络不稳定时，实际耗时可能超过阈值
   - 用户体验差，界面无响应
   - 可能触发 StrictMode 违规

3. 最佳实践
   - 所有网络请求必须异步（如 Retrofit + 协程/RxJava）
   - 使用 OkHttp 的异步请求
   - 使用 Kotlin 协程 withContext(Dispatchers.IO)

示例：
─────────────────────────────────────────────────────────────────────────────
// ❌ 错误：主线程网络请求
public void onClick(View v) {
    String result = NetworkUtil.get("http://example.com"); // 可能 ANR
    updateUI(result);
}

// ✅ 正确：异步网络请求
lifecycleScope.launch {
    val result = withContext(Dispatchers.IO) {
        NetworkUtil.get("http://example.com")
    }
    updateUI(result)
}

// ✅ 正确：Retrofit + 协程
interface ApiService {
    @GET("data")
    suspend fun getData(): Response<Data>
}

lifecycleScope.launch {
    val response = apiService.getData()
    if (response.isSuccessful) {
        updateUI(response.body())
    }
}
```

### 10.6 AsyncTask 的缺陷是什么？为什么官方废弃它？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AsyncTask 缺陷与废弃原因                                 │
└─────────────────────────────────────────────────────────────────────────────┘

一、内存泄漏
─────────────────────────────────────────────────────────────────────────────
问题：非静态内部类隐式持有 Activity 引用

// ❌ 错误示例
public class MainActivity extends Activity {
    private class MyTask extends AsyncTask<Void, Void, String> {
        @Override
        protected String doInBackground(Void... voids) {
            return heavyOperation();
        }
        
        @Override
        protected void onPostExecute(String result) {
            updateUI(result); // 隐式持有 Activity
        }
    }
}

// Activity 销毁时，Task 仍在执行 → 内存泄漏

解决方案：
// ✅ 使用静态内部类 + 弱引用
private static class MyTask extends AsyncTask<Void, Void, String> {
    private WeakReference<MainActivity> activityRef;
    
    MyTask(MainActivity activity) {
        activityRef = new WeakReference<>(activity);
    }
    
    @Override
    protected void onPostExecute(String result) {
        MainActivity activity = activityRef.get();
        if (activity != null && !activity.isFinishing()) {
            activity.updateUI(result);
        }
    }
}

二、生命周期问题
─────────────────────────────────────────────────────────────────────────────
问题：Activity 销毁后 onPostExecute 仍可能执行

- Activity 已销毁，但 Task 仍在后台执行
- onPostExecute 尝试更新已销毁的 Activity
- 可能导致崩溃或异常

解决方案：
- 在 onDestroy() 中取消任务
- 使用 Lifecycle-aware 组件（ViewModel + LiveData）

三、线程管理问题
─────────────────────────────────────────────────────────────────────────────
问题：Android 4.0+ 默认串行执行任务

// Android 1.6: 串行执行
// Android 1.6 - 3.0: 并行执行
// Android 3.0+: 串行执行（默认）

// 并行执行需要手动指定
task.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);

// 线程池配置：
private static final int CPU_COUNT = Runtime.getRuntime().availableProcessors();
private static final int CORE_POOL_SIZE = CPU_COUNT + 1;
private static final int MAXIMUM_POOL_SIZE = CPU_COUNT * 2 + 1;

问题：
- 线程池大小固定，无法灵活配置
- 任务过多时可能阻塞

四、官方推荐的替代方案
─────────────────────────────────────────────────────────────────────────────
1. Kotlin 协程（推荐）
   lifecycleScope.launch {
       val result = withContext(Dispatchers.IO) {
           heavyOperation()
       }
       updateUI(result)
   }

2. RxJava
   Observable.fromCallable(() -> heavyOperation())
       .subscribeOn(Schedulers.io())
       .observeOn(AndroidSchedulers.mainThread())
       .subscribe(result -> updateUI(result));

3. ExecutorService + Handler
   ExecutorService executor = Executors.newCachedThreadPool();
   executor.execute(() -> {
       String result = heavyOperation();
       new Handler(Looper.getMainLooper()).post(() -> {
           updateUI(result);
       });
   });

4. WorkManager（后台任务）
   WorkManager.getInstance(context).enqueue(workRequest);
```

### 10.7 ANR 的日志中 CPU Usage 字段如何分析？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CPU Usage 字段分析                                       │
└─────────────────────────────────────────────────────────────────────────────┘

一、CPU Usage 示例
─────────────────────────────────────────────────────────────────────────────
Load: 8.5 / 7.2 / 5.1   // 1/5/15 分钟系统负载
CPU usage from 0ms to 12345ms later (2024-01-01 12:34:56.123):
  50% 12345/com.example.app: 25% user + 25% kernel
  30% 567/system_server: 20% user + 10% kernel
  10% 890/com.android.systemui: 8% user + 2% kernel

二、高 CPU 负载分析
─────────────────────────────────────────────────────────────────────────────
症状：
- Load 值很高（> 核心数 * 2）
- 应用 CPU 使用率很高
- kernel 占比高（系统调用多）

可能原因：
1. 主线程竞争 CPU 资源
   - 死循环
   - 频繁的复杂计算
   - 大量 GC

2. 其他进程占用过多 CPU
   - 后台应用
   - 系统服务

解决方案：
- 优化算法，减少计算量
- 降低子线程优先级
- 使用 JobScheduler 在合适时机执行

三、低 CPU 负载分析
─────────────────────────────────────────────────────────────────────────────
症状：
- Load 值正常
- 应用 CPU 使用率低
- 主线程处于 Blocked/Sleeping 状态

可能原因：
1. 锁阻塞
   - synchronized 锁等待
   - ReentrantLock 阻塞
   - 死锁

2. I/O 等待
   - 文件读写
   - 网络请求
   - 数据库操作

3. Binder 调用阻塞
   - 跨进程通信慢
   - 系统服务响应慢

解决方案：
- 检查锁的使用，避免死锁
- I/O 操作放到子线程
- 使用异步 Binder 调用

四、分析工具
─────────────────────────────────────────────────────────────────────────────
1. top 命令
   adb shell top -m 10

2. dumpsys cpuinfo
   adb shell dumpsys cpuinfo

3. systrace / perfetto
   - 查看线程状态
   - 分析 CPU 调度
```

### 10.8 Binder 通信超时会导致 ANR 吗？

```
答案：会

┌─────────────────────────────────────────────────────────────────────────────┐
│                    Binder 通信与 ANR                                        │
└─────────────────────────────────────────────────────────────────────────────┘

一、Binder 通信原理
─────────────────────────────────────────────────────────────────────────────
1. 跨进程调用通过 Binder 实现
   - startService
   - bindService
   - ContentProvider.query()
   - ActivityManagerService 调用

2. 默认是同步调用
   - 调用线程阻塞等待返回
   - 如果服务端处理慢，客户端线程阻塞

二、ANR 场景
─────────────────────────────────────────────────────────────────────────────
案例 1：ContentProvider 查询超时

// 主线程调用 ContentProvider.query()
public void onClick(View v) {
    Cursor cursor = getContentResolver().query(
        Uri.parse("content://com.example.provider/data"),
        null, null, null, null
    ); // 如果 Provider 处理慢，主线程阻塞 → ANR
}

案例 2：AMS 调用超时

// 主线程调用系统服务
public void onClick(View v) {
    ActivityManager am = (ActivityManager) getSystemService(ACTIVITY_SERVICE);
    List<RunningTaskInfo> tasks = am.getRunningTasks(10);
    // 如果 AMS 响应慢，主线程阻塞 → ANR
}

案例 3：自定义 AIDL 服务超时

// 主线程调用 AIDL 服务
public void onClick(View v) {
    String result = myAidlService.getData(); // 同步 Binder 调用
    // 如果服务端处理慢，主线程阻塞 → ANR
}

三、解决方案
─────────────────────────────────────────────────────────────────────────────
1. 使用 AsyncQueryHandler
   // 异步查询 ContentProvider
   AsyncQueryHandler handler = new AsyncQueryHandler(getContentResolver()) {
       @Override
       protected void onQueryComplete(int token, Object cookie, Cursor cursor) {
           // 在主线程回调
           updateUI(cursor);
       }
   };
   
   handler.startQuery(0, null, uri, null, null, null, null);

2. 子线程访问 ContentProvider
   new Thread(() -> {
       Cursor cursor = getContentResolver().query(uri, null, null, null, null);
       runOnUiThread(() -> updateUI(cursor));
   }).start();

3. 缓存结果，避免频繁调用
   private PackageInfo cachedPackageInfo;
   
   public PackageInfo getPackageInfo() {
       if (cachedPackageInfo == null) {
           cachedPackageInfo = getPackageManager().getPackageInfo(...);
       }
       return cachedPackageInfo;
   }

4. 使用 Kotlin 协程
   lifecycleScope.launch {
       val cursor = withContext(Dispatchers.IO) {
           contentResolver.query(uri, null, null, null, null)
       }
       updateUI(cursor)
   }
```

### 10.9 列表滚动卡顿，如何判断是 ANR 的前兆？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    列表卡顿与 ANR 的关系                                    │
└─────────────────────────────────────────────────────────────────────────────┘

一、卡顿检测方法
─────────────────────────────────────────────────────────────────────────────
1. FPS 监控
   - 正常：60 FPS（16.6ms/帧）
   - 卡顿：FPS < 60
   - 严重卡顿：FPS < 30

2. Choreographer 日志
   adb logcat | grep Choreographer
   
   输出：
   I/Choreographer: Skipped 60 frames!  The application may be doing too much work on its main thread.
   
   - Skipped frames > 30: 明显卡顿
   - Skipped frames > 90: 接近 ANR（5秒）

3. Systrace 分析
   python $ANDROID_SDK/platform-tools/systrace/systrace.py \
       gfx view res am wm sched \
       -o trace.html
   
   分析：
   - 查看 UI 线程的 doFrame 耗时
   - 绿色：< 16ms
   - 黄色：接近 16ms
   - 红色：> 16ms（卡顿）

4. Perfetto 分析
   - 分析卡顿期间的线程状态
   - 查看锁竞争
   - 分析 CPU 调度

二、卡顿与 ANR 的关系
─────────────────────────────────────────────────────────────────────────────
1. 短期卡顿
   - 单帧渲染 > 16ms
   - 用户感知掉帧
   - 但未达到 ANR 阈值

2. 长期卡顿
   - 持续多帧卡顿
   - 累计时间可能超过 5 秒
   - 如果有输入事件等待处理 → ANR

3. 卡顿演变成 ANR 的条件
   - 卡顿期间有输入事件（触摸、按键）
   - 主线程无法及时处理输入事件
   - 超过 5 秒 → ANR

三、列表卡顿常见原因
─────────────────────────────────────────────────────────────────────────────
1. ViewHolder 未复用
   - 每次 onCreateViewHolder
   - 导致大量对象创建

2. onBindViewHolder 耗时
   - 复杂计算
   - 图片加载同步
   - 数据库查询

3. 布局复杂
   - Item 布局层级深
   - 过度绘制

4. 数据量大
   - 一次性加载过多数据
   - 未分页加载

四、优化方案
─────────────────────────────────────────────────────────────────────────────
1. 使用 RecyclerView 替代 ListView
   - ViewHolder 复用
   - DiffUtil 局部刷新

2. 异步加载图片
   Glide.with(context)
       .load(url)
       .into(imageView);

3. 简化 Item 布局
   - 使用 ConstraintLayout 减少层级
   - 避免过度绘制

4. 分页加载
   // 使用 Paging 库
   val pager = Pager(
       config = PagingConfig(pageSize = 20),
       pagingSourceFactory = { MyPagingSource() }
   ).flow
```

### 10.10 如何区分 ANR 和主线程卡顿（Jank）？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ANR vs 卡顿（Jank）对比                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  对比项         │  ANR                     │  卡顿（Jank）                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  定义           │  系统级弹窗              │  界面掉帧                     │
│                 │  主线程阻塞超过阈值      │  单帧渲染超过 16ms            │
├─────────────────────────────────────────────────────────────────────────────┤
│  阈值           │  5 秒（输入事件）        │  16.6ms（60fps）              │
│                 │  10 秒（前台广播）       │  无固定阈值                   │
│                 │  20 秒（前台 Service）   │                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  用户体验       │  弹出 ANR 对话框         │  界面不流畅                   │
│                 │  应用无响应              │  滚动掉帧                     │
│                 │  可能强制关闭            │  动画卡顿                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  检测方法       │  traces.txt 日志分析     │  Profiler 性能分析            │
│                 │  bugreport               │  Systrace 帧分析              │
│                 │  ANR 监控库              │  Choreographer 日志           │
├─────────────────────────────────────────────────────────────────────────────┤
│  分析工具       │  adb pull /data/anr/     │  GPU 呈现模式分析             │
│                 │  Android Studio Logcat   │  Perfetto                     │
│                 │  ANR-WatchDog            │  BlockCanary                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  常见原因       │  主线程耗时操作          │  布局复杂                     │
│                 │  死锁                    │  过度绘制                     │
│                 │  Binder 调用阻塞         │  onBindViewHolder 耗时        │
│                 │  CPU 负载过高            │  图片加载慢                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  严重程度       │  严重（崩溃级别）        │  中等（体验问题）             │
│                 │  影响应用评分            │  影响用户留存                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  优化策略       │  耗时操作子线程化        │  布局优化                     │
│                 │  避免死锁                │  减少过度绘制                 │
│                 │  优化 Binder 调用        │  RecyclerView 优化            │
│                 │  使用 WorkManager        │  图片异步加载                 │
└─────────────────────────────────────────────────────────────────────────────┘

一、ANR 分析方法
─────────────────────────────────────────────────────────────────────────────
1. 获取 traces.txt
   adb pull /data/anr/traces.txt

2. 分析主线程堆栈
   - 找到 "main" 线程
   - 查看阻塞原因
   - 定位业务代码

3. 检查 CPU 使用率
   - 高 CPU: 可能是死循环或计算密集
   - 低 CPU: 可能是锁等待或 I/O 阻塞

二、卡顿分析方法
─────────────────────────────────────────────────────────────────────────────
1. GPU 呈现模式分析
   开发者选项 → GPU 呈现模式分析 → 在屏幕上显示为条形图
   
   - 每条柱子代表一帧
   - 绿线：16ms 阈值
   - 超过绿线：卡顿

2. Systrace 分析
   python $ANDROID_SDK/platform-tools/systrace/systrace.py \
       gfx view res am wm sched \
       -o trace.html
   
   - 查看 F 标记（Frame）
   - 绿色：16ms 内完成
   - 黄色：接近 16ms
   - 红色：超过 16ms

3. Choreographer 日志
   adb logcat | grep Choreographer
   
   I/Choreographer: Skipped 30 frames!  The application may be doing too much work on its main thread.

三、关系与转换
─────────────────────────────────────────────────────────────────────────────
1. 卡顿是 ANR 的前兆
   - 长期卡顿可能演变成 ANR
   - 卡顿期间有输入事件等待 → ANR

2. ANR 是卡顿的极端情况
   - 主线程长时间阻塞
   - 无法响应任何操作

3. 监控策略
   - 先监控卡顿（BlockCanary）
   - 再监控 ANR（ANR-WatchDog）
   - 建立性能监控体系
```

---

## 11. 知识体系总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANR 知识体系                                        │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   ANR 检测      │
                           └────────┬────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            │                                               │
            ▼                                               ▼
    ┌───────────────┐                               ┌───────────────┐
    │  分析方法     │                               │  监控方案     │
    │               │                               │               │
    │  - traces.txt │                               │  - FileObserver│
    │  - ANR Info   │                               │  - WatchDog   │
    │  - bugreport  │                               │  - Matrix     │
    └───────────────┘                               └───────────────┘
            │
            ▼
    ┌───────────────┐
    │  ANR 类型     │
    │               │
    │  - Input      │
    │  - Broadcast  │
    │  - Service    │
    │  - Provider   │
    └───────────────┘
```

**核心知识点：**

1. **ANR 本质**：主线程被阻塞超过超时时间
2. **四种类型**：Input（5s）、Broadcast（10s/60s）、Service（20s/200s）、Provider（10s）
3. **常见原因**：主线程耗时操作、死锁、Binder 阻塞、CPU 负载高
4. **分析方法**：traces.txt 堆栈分析
5. **监控方案**：FileObserver、WatchDog、Matrix
6. **优化策略**：耗时操作子线程化、使用 apply() 替代 commit()

---

> 作者：OpenClaw | 日期：2026-03-09