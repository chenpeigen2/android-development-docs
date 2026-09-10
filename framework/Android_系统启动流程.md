# Android 系统启动流程深度解析

> 作者：OpenClaw | 日期：2026-03-12  
> 基于源码：AOSP Android 17 / API 37，固定 tag `android-17.0.0_r1`；复核日期：2026-09-10。

## 目录

- [1. 概述](#1-概述)
  - [1.1 启动流程总览](#11-启动流程总览)
  - [1.2 启动时间分布](#12-启动时间分布)
- [2. Init 进程启动](#2-init-进程启动)
  - [2.1 Init 进程职责](#21-init-进程职责)
  - [2.2 init.rc 配置](#22-initrc-配置)
  - [2.3 Init 源码](#23-init-源码)
- [3. Zygote 进程 fork 机制](#3-zygote-进程-fork-机制)
  - [3.1 Zygote 职责](#31-zygote-职责)
  - [3.2 Zygote 启动流程](#32-zygote-启动流程)
  - [3.3 ZygoteInit 源码](#33-zygoteinit-源码)
  - [3.4 Zygote Fork 流程](#34-zygote-fork-流程)
- [4. SystemServer 启动流程](#4-systemserver-启动流程)
  - [4.1 SystemServer 职责](#41-systemserver-职责)
  - [4.2 SystemServer 启动流程](#42-systemserver-启动流程)
  - [4.3 SystemServer 源码](#43-systemserver-源码)
- [5. 系统服务启动顺序](#5-系统服务启动顺序)
  - [5.1 服务启动顺序](#51-服务启动顺序)
- [6. BootComplete 广播](#6-bootcomplete-广播)
  - [6.1 BootComplete 发送](#61-bootcomplete-发送)
  - [6.2 监听 BootComplete](#62-监听-bootcomplete)
- [7. 源码路径](#7-源码路径)
  - [7.1 Init 源码](#71-init-源码)
  - [7.2 Zygote 源码](#72-zygote-源码)
  - [7.3 SystemServer 源码](#73-systemserver-源码)
- [8. 面试常见问题](#8-面试常见问题)
  - [8.1 基础问题](#81-基础问题)
  - [8.2 进阶问题](#82-进阶问题)
- [总结](#总结)

---

## 1. 概述

Android 系统启动是一个复杂的过程，从按下电源键到桌面完全显示，涉及多个阶段和组件。

### 1.1 启动流程总览

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Android 系统启动流程                                  │
└─────────────────────────────────────────────────────────────────────────────┘

按下电源键
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Boot ROM                                                               │
│     • 执行固化在 ROM 中的启动代码                                           │
│     • 加载 Bootloader 到 RAM                                               │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Bootloader                                                             │
│     • 初始化硬件                                                            │
│     • 加载 Linux 内核                                                       │
│     • 传递启动参数                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Linux Kernel                                                           │
│     • 初始化内核                                                            │
│     • 挂载根文件系统                                                        │
│     • 启动 init 进程 (PID=1)                                                │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Init 进程                                                              │
│     • 解析 init.rc                                                         │
│     • 启动关键服务 (ueventd, healthd)                                       │
│     • 启动 Zygote 进程                                                      │
│     • 启动 ServiceManager                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. Zygote 进程                                                            │
│     • 创建 Dalvik/ART 虚拟机                                                │
│     • 预加载类和资源                                                        │
│     • 启动 SystemServer                                                     │
│     • 进入 Socket 监听                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6. SystemServer                                                           │
│     • 启动系统服务 (AMS, WMS, PMS 等)                                       │
│     • 进入 Binder 线程池                                                    │
│     • 协调用户启动与解锁后的启动广播                                              │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. Launcher (桌面)                                                        │
│     • 显示应用图标                                                          │
│     • 桌面可见；不等于各用户 BOOT_COMPLETED 已全部分发                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 启动时间分布

AOSP tag 不规定各阶段毫秒预算，也不能证明“高端设备冷启动 8–12 秒、热启动 2–4 秒”。应先定义测量起止点：电源复位到桌面、内核到 framework ready、用户解锁到应用可用是不同指标。

| 阶段 | 应观察的工作 | 常见影响因素 |
|---|---|---|
| Bootloader / kernel | 验证、装载、设备初始化 | 硬件、存储、verified boot、驱动 |
| init | 挂载、SELinux、属性、动作及服务启动 | 分区、加密、依赖与服务恢复 |
| Zygote | ART 初始化、类与资源预加载 | boot classpath、预加载表、页缓存 |
| system_server | 服务构造、发布、boot phase、PMS 扫描 | 包数量、异步依赖、设备功能 |
| Home / 用户解锁 | Home Activity、首帧、用户广播 | 用户存储、组件初始化、窗口管线 |

可以使用 boot timing 属性、logcat 及受设备权限支持的 trace 逐段定位；本文不提供未经设备测量的总耗时结论。

## 2. Init 进程启动

### 2.1 Init 进程职责

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Init 进程职责                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Init 进程 (PID=1):
1. 解析 init.rc 配置文件
2. 启动关键守护进程
3. 挂载文件系统
4. 设置系统属性
5. 启动 Zygote 和 ServiceManager
6. 监听子进程退出并重启

关键服务：
• ueventd: 设备事件管理
• healthd: 电池监控
• servicemanager: Binder 服务管理
• surfaceflinger: 图形合成
• zygote: 应用进程孵化器
```

### 2.2 init.rc 配置

init language 的 action 由触发器排队执行，service 是受 init 监护的进程定义，不是把 rc 从上到下当普通 shell 脚本执行。SELinux 初始化属于 init 的阶段入口，不存在这里 `exec /system/bin/selinux_setup` 的独立通用服务。

以下是教学配置，展示触发条件与服务声明，不冒充完整原版 init.rc：

```text
# 独立设备 rc 示例；程序、权限及 SELinux domain 必须由产品配置配套。
on property:sys.example.ready=1
    start example_worker

service example_worker /system/bin/example_worker
    class late_start
    user system
    group system
    disabled
```

`disabled` 阻止它被 class_start 默认启动；显式 start 仍可启动。`oneshot` 会改变退出后的重启行为；`critical`、`reboot_on_failure`、onrestart 等还有专门语义。不能无条件将每个服务退出都解释成系统重启。

真实 Zygote 服务声明由 ro.zygote 对应 rc 选择：

```text
system/core/rootdir/init.rc
system/core/rootdir/init.zygote64.rc
system/core/rootdir/init.zygote64_32.rc
```

对应路径：[init.rc:12](https://android.googlesource.com/platform/system/core/+/refs/tags/android-17.0.0_r1/rootdir/init.rc#12)；[init.zygote64.rc:1](https://android.googlesource.com/platform/system/core/+/refs/tags/android-17.0.0_r1/rootdir/init.zygote64.rc#1)。


### 2.3 Init 源码

主入口在 `system/core/init/main.cpp`，不是 init.cpp 里的旧单函数循环。真实阶段分派摘录：

```cpp
if (argc > 1) {
    if (!strcmp(argv[1], "subcontext")) {
        android::base::InitLogging(argv, &android::base::KernelLogger);
        const BuiltinFunctionMap& function_map = GetBuiltinFunctionMap();

        return SubcontextMain(argc, argv, &function_map);
    }

    if (!strcmp(argv[1], "selinux_setup")) {
        return SetupSelinux(argv);
    }

    if (!strcmp(argv[1], "second_stage")) {
        return SecondStageMain(argc, argv);
    }
}
```

第一阶段处理启动必需挂载及根目录准备；SELinux 阶段加载策略并切换到第二阶段；SecondStageMain 初始化属性服务、加载 rc、建立动作与服务管理，并运行事件循环。init 本身的 exec 阶段切换保留 PID 1，不是 fork 出一个新的系统 init。

```text
main -> FirstStageMain -> exec init selinux_setup
 -> SetupSelinux -> exec init second_stage -> SecondStageMain
 -> LoadBootScripts -> QueueEventTrigger 等
 -> 循环：执行待处理 action 命令 / 检查重启 / epoll 等待 / 分发事件
```

`ActionManager::ExecuteOneCommand` 每次推进动作命令；事件到来再安排下一轮工作，不能伪造 `ExecuteAction("early-init")` 同步执行整个阶段。子进程退出与服务重启由 service/reap 路径处理，ueventd 是独立入口而非在 init 主循环前直接调用 ueventd_init。

源码：[main.cpp:53](https://android.googlesource.com/platform/system/core/+/refs/tags/android-17.0.0_r1/init/main.cpp#53)；[init.cpp:1066](https://android.googlesource.com/platform/system/core/+/refs/tags/android-17.0.0_r1/init/init.cpp#1066)；[action_manager.cpp:72](https://android.googlesource.com/platform/system/core/+/refs/tags/android-17.0.0_r1/init/action_manager.cpp#72)。

## 3. Zygote 进程 fork 机制

### 3.1 Zygote 职责

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Zygote 职责                                          │
└─────────────────────────────────────────────────────────────────────────────┘

Zygote (受精卵):
1. 通过 app_process/AndroidRuntime 启动 ART 虚拟机
2. 预加载类和资源
3. 启动 SystemServer
4. 监听 Socket，响应 fork 请求
5. 为新应用提供进程模板

优势：
• 预加载共享资源，减少启动时间
• Copy-on-Write 机制，节省内存
• 统一的进程模板
```

### 3.2 Zygote 启动流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Zygote 启动流程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

app_process (app_main.cpp)
    │
    ▼
AndroidRuntime.start()
    │
    ├─► 启动虚拟机
    │   └─► JNI_CreateJavaVM()
    │
    ├─► 注册 JNI 方法
    │   └─► register_jni_procs()
    │
    ├─► 调用 ZygoteInit.main()
    │   │
    │   ├─► 预加载
    │   │   ├─► preloadClasses()
    │   │   ├─► preloadResources()
    │   │   ├─► preloadSharedLibraries()
    │   │   └─► preloadClasses 内 finally 调用 runtime.preloadDexCaches()
    │   │
    │   ├─► 启动 SystemServer
    │   │   └─► forkSystemServer()
    │   │
    │   └─► 进入监听循环
    │       └─► runSelectLoop()
    │
    └─► 等待请求
```

### 3.3 ZygoteInit 源码

预加载不是只依次调用四个无参方法。真实入口保留 timing、HAL/图形、资源与兼容配置准备：

```java
static void preload(TimingsTraceLog bootTimingsTraceLog) {
    Log.d(TAG, "begin preload");
    bootTimingsTraceLog.traceBegin("BeginPreload");
    beginPreload();
    bootTimingsTraceLog.traceEnd(); // BeginPreload
    bootTimingsTraceLog.traceBegin("PreloadClasses");
    preloadClasses();
    bootTimingsTraceLog.traceEnd(); // PreloadClasses
    bootTimingsTraceLog.traceBegin("CacheNonBootClasspathClassLoaders");
    cacheNonBootClasspathClassLoaders();
    bootTimingsTraceLog.traceEnd(); // CacheNonBootClasspathClassLoaders
    bootTimingsTraceLog.traceBegin("PreloadResources");
    Resources.preloadResources();
    bootTimingsTraceLog.traceEnd(); // PreloadResources
    Trace.traceBegin(Trace.TRACE_TAG_DALVIK, "PreloadAppProcessHALs");
    nativePreloadAppProcessHALs();
    Trace.traceEnd(Trace.TRACE_TAG_DALVIK);
    Trace.traceBegin(Trace.TRACE_TAG_DALVIK, "PreloadGraphicsDriver");
    maybePreloadGraphicsDriver();
    Trace.traceEnd(Trace.TRACE_TAG_DALVIK);
    preloadSharedLibraries();
    preloadTextResources();
    preloadCompatConfig();
```

后面还按分支预加载 HttpEngine，调用 WebViewFactory.prepareWebViewInZygote、endPreload 与 warmUpJcaProviders。WebView 准备不等于在普通 Zygote 加载完整 Chromium；具体 provider/renderer 还有独立进程与类加载路径。

preloadClasses 从 `/system/etc/preloaded-classes` 读取列表；使用运行时 boot class loader 加载/初始化，并在 finally 中调用 runtime.preloadDexCaches。不能把 `preloadDexCaches()` 虚构为 ZygoteInit 自身方法。预加载页可共享，但子进程修改时会 COW，并不是共享可变 Java 对象的跨进程通信。

main 在解析 ABI/socket/start-system-server 等参数后按是否启用 lazy preload 决定预加载，建立 `new ZygoteServer(isPrimaryZygote)`，primary 分支 forkSystemServer；子进程获得 Runnable 后运行入口，父进程进入 runSelectLoop。

源码：[ZygoteInit.java:128](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/os/ZygoteInit.java#128)；[ZygoteInit.java:291](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/os/ZygoteInit.java#291)；[ZygoteInit.java:909](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/os/ZygoteInit.java#909)。

### 3.4 Zygote Fork 流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Zygote Fork 流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

AMS/ProcessList 经 ZygoteProcess 请求创建进程
    │
    ▼
ZygoteProcess.start()
    │
    ├─► 连接 Zygote Socket
    │
    ├─► 发送 fork 请求
    │   └─► zygoteSendArgsAndGetResult：参数计数 + 逐行协议
    │
    └─► Zygote 处理请求
        │
        ▼
ZygoteServer.runSelectLoop()
    │
    ├─► 接收请求
    │   └─► ZygoteConnection.processCommand()
    │
    ├─► 解析参数
    │
    ├─► fork 进程
    │   └─► Zygote.forkAndSpecialize()
    │       └─► nativeForkAndSpecialize()
    │           └─► fork()
    │
    ├─► 子进程处理
    │   └─► handleChildProc()
    │       ├─► 设置进程名
    │       ├─► 关闭 Zygote Socket
    │       └─► 调用 ActivityThread.main()
    │
    └─► 父进程处理
        └─► 返回子进程 PID
```

---

## 4. SystemServer 启动流程

### 4.1 SystemServer 职责

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SystemServer 职责                                    │
└─────────────────────────────────────────────────────────────────────────────┘

SystemServer:
1. 启动 Java framework 服务及部分 native 支持；独立守护进程仍由 init 管理
2. 提供 Binder IPC 支持
3. 管理系统生命周期
4. 协调各服务交互

主要服务：
• ActivityManagerService (AMS)
• WindowManagerService (WMS)
• PackageManagerService (PMS)
• PowerManagerService (PMS)
• DisplayManagerService (DMS)
• InputManagerService (IMS)
• 等等...
```

### 4.2 SystemServer 启动流程

```text
ZygoteInit.forkSystemServer -> Zygote.forkSystemServer
  child -> handleSystemServerProcess -> SystemServer.main -> new SystemServer().run()
  -> Looper / android_servers / system context / SystemServiceManager
  -> startBootstrapServices(t)
  -> startCoreServices(t)
  -> startOtherServices(t)
  -> startApexServices(t)
  -> 处理初始化异步任务与主线程 Looper
```

SystemServiceManager 不等于 native servicemanager：前者维护 Java SystemService 实例及启动阶段，后者保存 Binder 服务注册。SystemServer 不是唯一服务进程，SurfaceFlinger、servicemanager 等由 init 启动。

源码：[SystemServer.java:852](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/java/com/android/server/SystemServer.java#852)；[SystemServer.java:1050](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/java/com/android/server/SystemServer.java#1050)。

### 4.3 SystemServer 源码

SystemServer.run 用同一 TimingsTraceAndSlog 记录启动阶段；实际 start*Services 方法接收该参数，不能贴旧的全部无参签名或不存在的 nativeInit()。

WMS 与 IMS 初始化的真实顺序是 **先创建 IMS，再将其传给 WMS，再设置回调并启动输入处理**，而不是先使用一个未初始化 inputManager。

```java
t.traceEnd();

t.traceBegin("StartInputManagerService");
inputManager = mSystemServiceManager.startService(
        InputManagerService.Lifecycle.class).getService();
t.traceEnd();

```

```java

t.traceBegin("StartWindowManagerService");
// WMS needs sensor service ready
mSystemServiceManager.startBootPhase(t, SystemService.PHASE_WAIT_FOR_SENSOR_SERVICE);
wm = WindowManagerService.main(context, inputManager, !mFirstBoot,
        new PhoneWindowManager(), mActivityManagerService.mActivityTaskManager);
ServiceManager.addService(Context.WINDOW_SERVICE, wm, /* allowIsolated= */ false,
        DUMP_FLAG_PRIORITY_CRITICAL | DUMP_FLAG_PRIORITY_HIGH
                | DUMP_FLAG_PROTO);
t.traceEnd();

t.traceBegin("SetWindowManagerService");
mActivityManagerService.setWindowManager(wm);
t.traceEnd();
```

PMS.main 的参数/返回值与初始化协作者也应以本 tag 为准，不使用旧 `(context, installer, factoryTest, FACTORY_TEST_OFF)` 签名。bootstrap 将 ATMS 与 AMS 初始化关联；ServiceManager 发布 Binder 与 `SystemService.onStart`、后续 `onBootPhase` 是不同边界。

服务创建成功不代表全系统已 ready：Display/Package 扫描和异步 sensor 等依赖可形成等待。`systemReady` 会协调启动 Home 和用户状态，但不是直接向所有用户无条件发送 BOOT_COMPLETED 的方法。

源码：[SystemServer.java:1192](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/java/com/android/server/SystemServer.java#1192)；[SystemServer.java:1375](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/java/com/android/server/SystemServer.java#1375)；[SystemServer.java:1789](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/java/com/android/server/SystemServer.java#1789)。

## 5. 系统服务启动顺序

### 5.1 服务启动顺序

必须区分启动函数分组和 SystemService 的 boot phase 数值：二者不是一份静态完整序号表。

| 分组 | 本 tag 代表性工作 | 约束 |
|---|---|---|
| Bootstrap | Installer、ATMS/AMS、电源、显示、PMS 等 | 先建立后续服务依赖的基本能力 |
| Core | Battery、UsageStats、WebView 更新等 | 部分受产品功能/实现选择约束 |
| Other | IMS、WMS、VibratorManager、存储、网络及其他服务 | 长列表穿插依赖、条件和异步任务，不代表列举顺序即所有设备顺序 |
| APEX | 模块定义的服务 | 由模块元数据与可用性决定 |

不存在 AOSP 通用 `Elm327Service`；振动管理当前使用 `VibratorManagerService.Lifecycle`。WMS/IMS 顺序见 4.3，不应把它们放在所有网络服务之后再声称精确全序。

SystemServiceManager.startBootPhase 向已启动服务派发 onBootPhase。phase 必须单调推进；服务根据自己依赖的阶段再开启工作，onStart 不能访问任意尚未 ready 的系统服务。不同用户的启动/解锁回调又是另一维度。

源码：[SystemServer.java:1467](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/java/com/android/server/SystemServer.java#1467)；[SystemServer.java:1550](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/java/com/android/server/SystemServer.java#1550)；[SystemServiceManager.java:305](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/SystemServiceManager.java#305)。

## 6. BootComplete 广播

### 6.1 BootComplete 发送

启动广播由用户状态机协调，不是 AMS.finishBooting 内直接先发送 locked 再等待一个虚构 addUserUnlockedListener。

```text
用户启动完成：UserController.finishUserBoot
 -> 用户进入 RUNNING_LOCKED 等状态
 -> 按用户状态/策略发送 ACTION_LOCKED_BOOT_COMPLETED
用户凭据存储解锁：finishUserUnlocked
 -> finishUserUnlockedCompleted（含初始化/迁移等条件）
 -> ACTION_BOOT_COMPLETED
```

LOCKED_BOOT_COMPLETED 面向 direct-boot-aware receiver，可用 device-protected storage；BOOT_COMPLETED 依赖相应用户解锁及启动完成。系统属性 sys.boot_completed、SystemService PHASE_BOOT_COMPLETED、Home 首帧和每用户广播不是同一个同步时刻。广播本身也可能被队列推迟，不能以已调用 AMS.systemReady 推断所有应用已收到。

源码：[UserController.java:766](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/UserController.java#766)；[UserController.java:1030](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/UserController.java#1030)。

### 6.2 监听 BootComplete

配置与实现分文件书写；下面只做短工作，不在广播里直接 startService 长期后台服务：

```xml
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
<!-- application 内 -->
<receiver android:name=".BootReceiver" android:exported="false">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

```java
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            // 应用自己的幂等短任务；持久后台工作应交 JobScheduler 等。
            // 不在主线程执行长 I/O，也不假定可无条件启动后台/前台服务。
        }
    }
}
```

若要接收 LOCKED_BOOT_COMPLETED，应声明 directBootAware 并只访问解锁前可用的数据；普通 BOOT_COMPLETED 示例不需要误加该属性。应用处于 stopped/restricted 状态等时还要考虑系统投递约束。

源码发送侧：[UserController.java:766](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/UserController.java#766)。

## 7. 源码路径

### 7.1 Init 源码

```text
system/core/init/
├── init.cpp                           # Init 主程序
├── parser.cpp                    # init.rc 解析器
├── sigchld_handler.cpp                 # 信号处理
├── property_service.cpp               # 属性服务
├── service.cpp                        # 服务管理
└── action.cpp                         # Action 管理

system/core/rootdir/
└── init.rc                            # 默认 init.rc

device/[manufacturer]/[device]/
└── init.[device].rc                   # 设备特定 init.rc
```

### 7.2 Zygote 源码

```text
frameworks/base/cmds/app_process/app_main.cpp
frameworks/base/core/jni/AndroidRuntime.cpp
frameworks/base/core/jni/com_android_internal_os_Zygote.cpp
frameworks/base/core/java/com/android/internal/os/
  ZygoteInit.java / Zygote.java / ZygoteConnection.java / ZygoteServer.java / RuntimeInit.java
frameworks/base/core/java/android/os/ZygoteProcess.java
```

app_process 负责 native 入口、ART 与 Java main 的衔接，socket 协议和 native fork 是不同层。源码：[ZygoteInit.java:824](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/os/ZygoteInit.java#824)。

### 7.3 SystemServer 源码

```text
frameworks/base/services/java/com/android/server/SystemServer.java
frameworks/base/services/core/java/com/android/server/SystemServiceManager.java
frameworks/base/services/core/java/com/android/server/SystemService.java
frameworks/base/services/core/java/com/android/server/am/UserController.java
frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java
frameworks/base/services/core/java/com/android/server/wm/WindowManagerService.java
frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java
```

SystemServiceManager/SystemService 位于 services/core/java，不是 SystemServer 的 services/java 同目录。

## 8. 面试常见问题

### 8.1 基础问题

**Q1: Android 系统启动流程？**

```text
1. Boot ROM - 执行固化代码
2. Bootloader - 初始化硬件，加载内核
3. Linux Kernel - 启动 init 进程
4. Init - 解析 init.rc，启动 Zygote
5. Zygote - 预加载类和资源，启动 SystemServer
6. SystemServer - 启动系统服务
7. Launcher - 显示桌面
```

**Q2: Zygote 的作用？**

```text
1. 创建 ART 虚拟机
2. 预加载类和资源
3. 启动 SystemServer
4. 监听 Socket，响应 fork 请求
5. 为新应用提供进程模板

优势：
• 预加载共享资源，减少启动时间
• Copy-on-Write 机制，节省内存
```

**Q3: SystemServer 启动了哪些服务？**

```text
引导服务:
• ActivityManagerService (AMS)
• PowerManagerService (PMS)
• PackageManagerService (PMS)
• DisplayManagerService (DMS)

核心服务:
• BatteryService
• UsageStatsService

其他服务:
• WindowManagerService (WMS)
• InputManagerService (IMS)
• 等等...
```

### 8.2 进阶问题

**Q4: Init 进程的职责？**

```text
1. 解析 init.rc 配置文件
2. 启动关键守护进程
3. 挂载文件系统
4. 设置系统属性
5. 启动 Zygote 和 ServiceManager
6. 监听子进程退出并重启
```

**Q5: Zygote fork 的流程？**

```text
1. AMS 通过 Zygote Socket 发送 fork 请求
2. Zygote 接收请求
3. Zygote.forkAndSpecialize() fork 新进程
4. 子进程处理:
   • 设置进程名
   • 关闭 Zygote Socket
   • 调用 ActivityThread.main()
5. 父进程返回子进程 PID
```

**Q6: BOOT_COMPLETED 广播何时发送？**

启动广播由用户状态机协调，不是 AMS.finishBooting 内直接先发送 locked 再等待一个虚构 addUserUnlockedListener。

```text
用户启动完成：UserController.finishUserBoot
 -> 用户进入 RUNNING_LOCKED 等状态
 -> 按用户状态/策略发送 ACTION_LOCKED_BOOT_COMPLETED
用户凭据存储解锁：finishUserUnlocked
 -> finishUserUnlockedCompleted（含初始化/迁移等条件）
 -> ACTION_BOOT_COMPLETED
```

LOCKED_BOOT_COMPLETED 面向 direct-boot-aware receiver，可用 device-protected storage；BOOT_COMPLETED 依赖相应用户解锁及启动完成。系统属性 sys.boot_completed、SystemService PHASE_BOOT_COMPLETED、Home 首帧和每用户广播不是同一个同步时刻。广播本身也可能被队列推迟，不能以已调用 AMS.systemReady 推断所有应用已收到。

源码：[UserController.java:766](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/UserController.java#766)；[UserController.java:1030](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/UserController.java#1030)。

---

## 总结

本文详细讲解了 Android 系统启动流程的核心知识点，包括：

1. **启动流程总览** - 从 Boot ROM 到 Launcher
2. **Init 进程** - 配置解析和服务启动
3. **Zygote 进程** - fork 机制和预加载
4. **SystemServer** - 系统服务启动
5. **服务启动顺序** - Bootstrap/Core/Other
6. **BootComplete** - 启动完成广播

掌握这些知识点对于 Android 面试和系统级开发都至关重要。

---

*文档更新时间: 2026-09-10*
