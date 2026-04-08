# Android SystemUI 完全指南

> 作者：OpenClaw | 日期：2026-03-11  
> SystemUI 核心机制 | AOD 与通知系统深度解析

---

## 目录

### 一、SystemUI 基础
- [第1章 SystemUI 概述](#1-systemui-概述)
  - [1.1 什么是 SystemUI](#11-什么是-systemui)
  - [1.2 SystemUI 包含的组件](#12-systemui-包含的组件)
  - [1.3 SystemUI 进程](#13-systemui-进程)

- [第2章 SystemUI 启动流程](#2-systemui-启动流程)
  - [2.1 整体架构](#21-整体架构)
  - [2.2 启动时序](#22-启动时序)
  - [2.3 核心组件初始化](#23-核心组件初始化)

### 二、核心功能模块
- [第3章 AOD (Always On Display)](#3-aod-always-on-display-详解)
  - [3.1 AOD 概述](#31-aod-概述)
  - [3.2 Doze 状态机](#32-doze-状态机)
  - [3.3 AOD 显示流程](#33-aod-显示流程)
  - [3.4 AOD 核心组件源码](#34-aod-核心组件源码)

- [第4章 通知系统](#4-通知系统详解)
  - [4.1 通知系统架构](#41-通知系统概述)
  - [4.2 通知发送流程](#42-通知发送流程)
  - [4.3 通知核心组件](#43-通知核心组件)

- [第5章 NotificationManagerService](#5-notificationmanagerservice-深入分析)
  - [5.1 NMS 架构](#51-nms-架构)
  - [5.2 NMS 核心流程](#52-nms-核心流程)

- [第6章 RemoteViews 机制](#6-remoteviews-深度解析)
  - [6.1 RemoteViews 原理](#61-remoteviews-原理)
  - [6.2 RemoteViews 支持的 View](#62-remoteviews-支持的-view)
  - [6.3 RemoteViews 操作](#63-remoteviews-操作)
  - [6.4 Actions 机制深度解析](#64-actions-机制深度解析)
  - [6.5 反射创建与 View 白名单机制](#65-反射创建与-view-白名单机制)

- [第7章 通知渲染流程](#7-通知渲染流程)
  - [7.1 渲染架构](#71-渲染架构)
  - [7.2 渲染流程详解](#72-渲染流程详解)

- [第8章 通知模板系统](#8-通知模板系统)
  - [8.1 通知模板类型](#81-通知模板类型)
  - [8.2 模板使用示例](#82-模板使用示例)
  - [8.3 模板底层实现](#83-模板底层实现)

### 三、系统集成
- [第9章 SystemUI 与 Framework 协作](#9-systemui-与-framework-协作)

### 四、高级特性
- [第10章 面试常见问题](#10-面试常见问题)

- [第11章 NotificationManagerService 高级特性](#11-notificationmanagerservice-高级特性)
  - [11.1 NMS 核心数据结构](#111-nms-核心数据结构)
  - [11.2 通知排名算法](#112-通知排名算法)
  - [11.3 通知分组机制](#113-通知分组机制)
  - [11.4 通知气泡 (Bubble)](#114-通知气泡-bubble)
  - [11.5 通知声音和振动](#115-通知声音和振动)

- [第12章 AOD 高级特性](#12-aod-高级特性)
  - [12.1 AOD 与 PowerManagerService 交互](#121-aod-与-powermanagerservice-交互)
  - [12.2 AOD 硬件抽象层](#122-aod-硬件抽象层-hal)
  - [12.3 AOD 传感器集成](#123-aod-传感器集成)
  - [12.4 AOD 配置和设置](#124-aod-配置和设置)

- [第13章 Keyguard 锁屏系统](#13-keyguard-锁屏系统)
  - [13.1 Keyguard 概述](#131-keyguard-概述)
  - [13.2 Keyguard 启动流程](#132-keyguard-启动流程)
  - [13.3 KeyguardViewMediator 源码](#133-keyguardviewmediator-源码分析)
  - [13.4 KeyguardUpdateMonitor](#134-keyguardupdatemonitor-状态管理)
  - [13.5 安全验证机制](#135-安全验证机制)
  - [13.6 图案解锁源码](#136-图案解锁源码分析)
  - [13.7 生物识别解锁](#137-生物识别解锁)
  - [13.8 锁屏与 SystemUI 交互](#138-锁屏与-systemui-交互)
  - [13.9 Keyguard 状态机](#139-keyguard-状态机)
  - [13.10 锁屏安全最佳实践](#1310-锁屏安全最佳实践)

- [第14章 Keyguard 面试常见问题](#14-keyguard-面试常见问题)
  - [14.1 Keyguard 启动与验证](#141-keyguard-启动与验证)

---

## 1. SystemUI 概述

### 1.1 什么是 SystemUI

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SystemUI 在系统中的位置                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           Android 系统架构                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        应用层 (Apps)                                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│  │ Launcher│ │Phone   │ │Camera  │ │Settings│ │  ...   │            │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Framework 层 (Java)                                   │
│  ┌─────────────────────────────────────────────────────────────────┐      │
│  │                      SystemUI                                      │      │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │      │
│  │  │StatusBar │ │NavBar   │ │Notification│ │Keyguard │         │      │
│  │  │ 状态栏   │ │ 导航栏   │ │  通知面板  │ │ 锁屏    │         │      │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │      │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │      │
│  │  │  Power   │ │Volume   │ │ AOD      │ │  Quick   │         │      │
│  │  │  电源菜单 │ │ 音量条   │ │ 息屏显示  │ │ 快捷面板  │         │      │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │      │
│  └─────────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Native 层 (C/C++)                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│  │ SurfaceFlinger│ │  InputDispatcher │ │  AudioFlinger │ │ ...   │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Linux Kernel                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 SystemUI 包含的组件

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SystemUI 核心组件                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  StatusBar (状态栏)                                                        │
│  ├── StatusBarIconView - 状态栏图标                                       │
│  ├── SignalIconView - 信号图标                                            │
│  ├── BatteryIconView - 电池图标                                           │
│  ├── ClockView - 时间显示                                                 │
│  └── NotificationIconContainer - 通知图标容器                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  NavigationBar (导航栏)                                                    │
│  ├── NavBarView - 导航栏容器                                               │
│  ├── BackButton - 返回按钮                                                │
│  ├── HomeButton - Home 按钮                                               │
│  ├── RecentButton - 多任务按钮                                            │
│  └── EdgeNavStrategy - 边缘滑动策略                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Notification (通知)                                                       │
│  ├── NotificationPanelView - 通知面板                                       │
│  ├── NotificationStackScrollLayout - 通知列表                             │
│  ├── NotificationView - 单条通知视图                                       │
│  ├── ExpandableNotificationRow - 可展开通知行                              │
│  └── MediaNotificationView - 媒体通知                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Keyguard (锁屏)                                                           │
│  ├── KeyguardHostView - 锁屏主视图                                         │
│  ├── LockPatternView - 图案解锁                                           │
│  ├── FingerprintUnlockView - 指纹解锁                                     │
│  └── BiometricUnlockView - 生物识别解锁                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  AOD (Always On Display)                                                  │
│  ├── AODView - AOD 主视图                                                 │
│  ├── AODDisplayView - AOD 显示区域                                       │
│  ├── AODClockView - AOD 时钟                                             │
│  ├── AODNotificationView - AOD 通知视图                                   │
│  └── DozeMachine - Doze 状态机                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  PowerMenu (电源菜单)                                                     │
│  ├── GlobalActionsDialog - 全局操作对话框                                 │
│  ├── PowerMenuView - 电源菜单视图                                         │
│  └── PowerButton - 电源按钮                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 SystemUI 进程

```java
/**
 * SystemUI 是一个运行在 system_server 进程中的系统级应用
 * 进程名: com.android.systemui
 * 进程名: com.android.systemui:pixel (在某些设备上)
 */

// SystemUI 进程创建流程
// 1. system_server 启动时创建 SystemUIService
// 2. SystemUIService.onStart() 启动 SystemUIApplication
// 3. SystemUIApplication.onCreate() 初始化各个组件
// 4. 每个组件都是一个独立的服务/控制器
```

---

## 2. SystemUI 启动流程 (Android 16)

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/`
>
> 关键文件:
> - `SystemUIApplication.java` - 应用入口
> - `SystemUIService.java` - 服务入口
> - `SystemUIInitializer.java` - 初始化器
> - `CoreStartable.java` - 核心启动接口

### 2.1 整体架构 (Android 16 Dagger 注入)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                SystemUI 启动架构 (Android 16 Dagger)                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         System Server 进程                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SystemServer.main()                               │   │
│  │                                                                      │   │
│  │   1. startBootstrapServices()  - 引导服务                           │   │
│  │   2. startCoreServices()       - 核心服务                           │   │
│  │   3. startOtherServices()      - 其他服务                           │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │   ┌────────────────────────────────────────────────────────────┐    │   │
│  │   │  SystemServiceManager.startService(SystemUIService.class)  │    │   │
│  │   └────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SystemUIApplication.onCreate()                          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. Dagger 依赖注入初始化                                            │   │
│  │     mInitializer = mContextAvailableCallback.onContextAvailable()   │   │
│  │     mSysUIComponent = mInitializer.getSysUIComponent()              │   │
│  │                                                                      │   │
│  │  2. 设置主题和 GPU 优先级                                            │   │
│  │     setTheme(R.style.Theme_SystemUI)                                │   │
│  │     ThreadedRenderer.setContextPriority()                           │   │
│  │                                                                      │   │
│  │  3. 注册 BOOT_COMPLETED 广播                                        │   │
│  │     registerReceiver(mBootCompletedReceiver)                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SystemUIService.onCreate()                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ((SystemUIApplication) getApplication())                            │   │
│  │      .startSystemUserServicesIfNeeded();                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              SystemUIApplication.startSystemUserServicesIfNeeded()          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  CoreStartable 启动 (Dagger Map 注入):                               │   │
│  │                                                                      │   │
│  │  Map<Class<?>, Provider<CoreStartable>> sortedStartables =          │   │
│  │      mSysUIComponent.getStartables();        // 系统用户服务         │   │
│  │  sortedStartables.putAll(                                            │   │
│  │      mSysUIComponent.getPerUserStartables()); // 每用户服务          │   │
│  │                                                                      │   │
│  │  // 拓扑排序启动 (处理依赖关系)                                      │   │
│  │  startServicesIfNeeded(sortedStartables, "StartServices", ...);     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心源码分析 (Android 16 AOSP)

#### SystemUIApplication.java

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/SystemUIApplication.java`

```java
/**
 * SystemUI 应用入口 (Android 16 AOSP)
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/SystemUIApplication.java
 */
public class SystemUIApplication extends Application implements
        SystemUIAppComponentFactoryBase.ContextInitializer, HasWMComponent {

    public static final String TAG = "SystemUIService";

    private CoreStartable[] mServices;
    private boolean mServicesStarted;
    private SysUIComponent mSysUIComponent;
    private SystemUIInitializer mInitializer;
    private ProcessWrapper mProcessWrapper;

    public SystemUIApplication() {
        super();
        if (!isSubprocess()) {
            Trace.registerWithPerfetto();
        }
        // SysUI may be building without protolog preprocessing
        ProtoLog.REQUIRE_PROTOLOGTOOL = false;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        Log.v(TAG, "SystemUIApplication created.");

        // 1. Dagger 依赖注入初始化
        TimingsTraceLog log = new TimingsTraceLog("SystemUIBootTiming", Trace.TRACE_TAG_APP);
        log.traceBegin("DependencyInjection");
        mInitializer = mContextAvailableCallback.onContextAvailable(this);
        mSysUIComponent = mInitializer.getSysUIComponent();
        mBootCompleteCache = mSysUIComponent.provideBootCacheImpl();
        log.traceEnd();

        GlobalRootComponent rootComponent = mInitializer.getRootComponent();

        // 2. 设置 Looper 追踪标签
        rootComponent.getMainLooper().setTraceTag(Trace.TRACE_TAG_APP);
        mProcessWrapper = rootComponent.getProcessWrapper();

        // 3. 设置应用主题
        setTheme(R.style.Theme_SystemUI);

        // 4. GPU 优先级设置
        if (mProcessWrapper.isSystemUser()) {
            int sfPriority = SurfaceControl.getGPUContextPriority();
            if (sfPriority == ThreadedRenderer.EGL_CONTEXT_PRIORITY_REALTIME_NV) {
                ThreadedRenderer.setContextPriority(
                        ThreadedRenderer.EGL_CONTEXT_PRIORITY_HIGH_IMG);
            }

            // 5. 注册 BOOT_COMPLETED 广播
            IntentFilter bootCompletedFilter = new IntentFilter(
                    Intent.ACTION_LOCKED_BOOT_COMPLETED);
            bootCompletedFilter.setPriority(IntentFilter.SYSTEM_HIGH_PRIORITY);
            registerReceiver(new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                    if (mBootCompleteCache.isBootComplete()) return;
                    unregisterReceiver(this);
                    mBootCompleteCache.setBootComplete();
                    if (mServicesStarted) {
                        for (CoreStartable service : mServices) {
                            notifyBootCompleted(service);
                        }
                    }
                }
            }, bootCompletedFilter);
        } else if (!isSubprocess()) {
            // 非系统用户：启动二级用户服务
            startSecondaryUserServicesIfNeeded();
        }
    }

    /**
     * 启动系统用户的所有 CoreStartable 服务
     */
    public void startSystemUserServicesIfNeeded() {
        if (!shouldStartSystemUserServices()) {
            Log.wtf(TAG, "Tried starting SystemUser services on non-SystemUser");
            return;
        }

        final String vendorComponent = mInitializer.getVendorComponent(getResources());

        // 获取 Dagger 注入的 Startables (按类名排序)
        Map<Class<?>, Provider<CoreStartable>> sortedStartables = new TreeMap<>(
                Comparator.comparing(Class::getName));
        sortedStartables.putAll(mSysUIComponent.getStartables());        // 系统用户服务
        sortedStartables.putAll(mSysUIComponent.getPerUserStartables()); // 每用户服务

        startServicesIfNeeded(sortedStartables, "StartServices", vendorComponent);
    }

    /**
     * 启动二级用户服务
     */
    void startSecondaryUserServicesIfNeeded() {
        if (!shouldStartSecondaryUserServices()) {
            return;
        }
        Map<Class<?>, Provider<CoreStartable>> sortedStartables = new TreeMap<>(
                Comparator.comparing(Class::getName));
        sortedStartables.putAll(mSysUIComponent.getPerUserStartables());
        startServicesIfNeeded(sortedStartables, "StartSecondaryServices", null);
    }

    /**
     * 拓扑排序启动 CoreStartable (处理依赖关系)
     */
    private void startServicesIfNeeded(
            Map<Class<?>, Provider<CoreStartable>> startables,
            String metricsPrefix,
            String vendorComponent) {
        if (mServicesStarted) {
            return;
        }
        mServices = new CoreStartable[startables.size() + (vendorComponent == null ? 0 : 1)];

        DumpManager dumpManager = mSysUIComponent.createDumpManager();
        TimingsTraceLog log = new TimingsTraceLog("SystemUIBootTiming", Trace.TRACE_TAG_APP);
        log.traceBegin(metricsPrefix);

        HashSet<Class<?>> startedStartables = new HashSet<>();

        // 拓扑排序启动:
        // 1) 遍历队列中所有未启动的 startables
        // 2) 如果 startable 的所有依赖都已满足，启动它
        // 3) 否则放入下一轮队列
        // 4) 重复直到没有更多可启动的

        log.traceBegin("Topologically start Core Startables");
        ArrayDeque<Map.Entry<Class<?>, Provider<CoreStartable>>> nextQueue =
                new ArrayDeque<>(startables.entrySet());
        int serviceIndex = 0;
        boolean startedAny;
        int numIterations = 0;

        do {
            startedAny = false;
            ArrayDeque<Map.Entry<Class<?>, Provider<CoreStartable>>> queue = nextQueue;
            nextQueue = new ArrayDeque<>(startables.size());

            while (!queue.isEmpty()) {
                Map.Entry<Class<?>, Provider<CoreStartable>> entry = queue.removeFirst();
                Class<?> cls = entry.getKey();

                // 检查依赖是否满足
                Set<Class<? extends CoreStartable>> deps =
                        mSysUIComponent.getStartableDependencies().get(cls);
                if (deps == null || startedStartables.containsAll(deps)) {
                    // 依赖满足，启动服务
                    String clsName = cls.getName();
                    int i = serviceIndex;
                    timeInitialization(clsName,
                            () -> mServices[i] = startStartable(clsName, entry.getValue()),
                            log, metricsPrefix);
                    startedStartables.add(cls);
                    startedAny = true;
                    serviceIndex++;
                } else {
                    // 依赖未满足，放入下一轮
                    nextQueue.add(entry);
                }
            }
            numIterations++;
        } while (startedAny && !nextQueue.isEmpty());

        // 如果还有未启动的，抛出错误
        if (!nextQueue.isEmpty()) {
            // 记录缺失的依赖
            throw new RuntimeException("Failed to start all CoreStartables. Check logcat!");
        }

        // 注册 dump 处理
        for (int i = 0; i < mServices.length; i++) {
            final CoreStartable service = mServices[i];
            if (mBootCompleteCache.isBootComplete()) {
                notifyBootCompleted(service);
            }
            if (service.isDumpCritical()) {
                dumpManager.registerCriticalDumpable(service);
            } else {
                dumpManager.registerNormalDumpable(service);
            }
        }

        mSysUIComponent.getInitController().executePostInitTasks();
        log.traceEnd();
        mServicesStarted = true;
    }

    private static CoreStartable startStartable(
            String clsName, Provider<CoreStartable> provider) {
        Trace.traceBegin(Trace.TRACE_TAG_APP, "Provider<" + clsName + "">.get()");
        CoreStartable startable = provider.get();
        Trace.endSection();
        return startStartable(startable);
    }

    private static CoreStartable startStartable(CoreStartable startable) {
        Trace.traceBegin(Trace.TRACE_TAG_APP,
                startable.getClass().getSimpleName() + ".start()");
        startable.start();
        Trace.endSection();
        return startable;
    }
}
```

#### SystemUIService.java

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/SystemUIService.java`

```java
/**
 * SystemUI 服务入口 (Android 16 AOSP)
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/SystemUIService.java
 */
public class SystemUIService extends Service {

    private final Handler mMainHandler;
    private final DumpHandler mDumpHandler;
    private final BroadcastDispatcher mBroadcastDispatcher;
    private final LogBufferEulogizer mLogBufferEulogizer;
    private final LogBufferFreezer mLogBufferFreezer;
    private final BatteryStateNotifier mBatteryStateNotifier;

    @Inject
    public SystemUIService(
            @Main Handler mainHandler,
            DumpHandler dumpHandler,
            BroadcastDispatcher broadcastDispatcher,
            LogBufferEulogizer logBufferEulogizer,
            LogBufferFreezer logBufferFreezer,
            BatteryStateNotifier batteryStateNotifier,
            UncaughtExceptionPreHandlerManager uncaughtExceptionPreHandlerManager) {
        super();
        mMainHandler = mainHandler;
        mDumpHandler = dumpHandler;
        mBroadcastDispatcher = broadcastDispatcher;
        mLogBufferEulogizer = logBufferEulogizer;
        mLogBufferFreezer = logBufferFreezer;
        mBatteryStateNotifier = batteryStateNotifier;
    }

    @Override
    public void onCreate() {
        super.onCreate();

        // 启动所有 SystemUI 服务 (系统用户)
        ((SystemUIApplication) getApplication()).startSystemUserServicesIfNeeded();

        // 日志缓冲区冻结器
        mLogBufferFreezer.attach(mBroadcastDispatcher);

        // 注册未捕获异常处理器
        mUncaughtExceptionPreHandlerManager.registerHandler(
                (thread, throwable) -> mLogBufferEulogizer.record(throwable));

        // 电池状态通知
        if (getResources().getBoolean(
                R.bool.config_showNotificationForUnknownBatteryState)) {
            mBatteryStateNotifier.startListening();
        }

        // 调试模式: Binder 代理计数
        if (Build.IS_DEBUGGABLE) {
            BinderInternal.nSetBinderProxyCountEnabled(true);
            BinderInternal.nSetBinderProxyCountWatermarks(1000, 900, 950);
        }

        // 启动辅助 dump 服务
        startServiceAsUser(
                new Intent(getApplicationContext(), SystemUIAuxiliaryDumpService.class),
                UserHandle.SYSTEM);
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    protected void dump(FileDescriptor fd, PrintWriter pw, String[] args) {
        mDumpHandler.dump(fd, pw, massagedArgs);
    }
}
```

#### CoreStartable.java - 核心启动接口

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/CoreStartable.java`

```java
/**
 * CoreStartable 接口 (Android 16 AOSP)
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/CoreStartable.java
 *
 * 所有需要随 SystemUI 启动的组件都实现此接口。
 * 通过 Dagger 绑定到 CoreStartable Map 中。
 */
public interface CoreStartable extends Dumpable {
    String STARTABLE_DEPENDENCIES = "startable_dependencies";

    /**
     * 主入口点。SystemUI 启动后不久调用。
     */
    void start();

    /**
     * 系统广播 ACTION_LOCKED_BOOT_COMPLETED 后立即调用，
     * 或启动时如果 sys.boot_completed 已为 1。
     */
    default void onBootCompleted() {}

    /**
     * 是否作为关键 dump 注册
     */
    default boolean isDumpCritical() {
        return true;
    }

    @Override
    default void dump(@NonNull PrintWriter pw, @NonNull String[] args) {}

    /** 空实现 */
    CoreStartable NOP = new Nop();

    class Nop implements CoreStartable {
        @Override
        public void start() {}
    }
}
```

### 2.3 Dagger 组件绑定示例

```java
/**
 * CoreStartable 的 Dagger 绑定方式
 *
 * 在 Dagger Module 中绑定:
 */

@Module
public abstract class SystemUIModule {

    /**
     * 绑定 CoreStartable 到 Map
     * 使用 @ClassKey 注解指定类名作为 key
     */
    @Binds
    @IntoMap
    @ClassKey(CentralSurfacesImpl.class)
    abstract CoreStartable bindCentralSurfaces(CentralSurfacesImpl impl);

    @Binds
    @IntoMap
    @ClassKey(KeyguardViewMediator.class)
    abstract CoreStartable bindKeyguardViewMediator(KeyguardViewMediator impl);

    @Binds
    @IntoMap
    @ClassKey(NotificationListener.class)
    abstract CoreStartable bindNotificationListener(NotificationListener impl);

    /**
     * 声明依赖关系
     * NotificationListener 依赖 CentralSurfacesImpl 先启动
     */
    @Provides
    @IntoMap
    @Dependencies  // com.android.systemui.startable.Dependencies
    @ClassKey(NotificationListener.class)
    static Set<Class<? extends CoreStartable>> provideNotificationListenerDeps() {
        return Set.of(CentralSurfacesImpl.class);
    }
}
```

### 2.4 启动时序图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                SystemUI 启动时序 (Android 16)                                │
└─────────────────────────────────────────────────────────────────────────────┘

时间线:
│
├─── SystemServer.startOtherServices()
│   │
│   └─── ActivityManagerService.startService(SystemUIService)
│
├─── SystemUIApplication 构造函数
│   │   Trace.registerWithPerfetto()
│   │   ProtoLog.REQUIRE_PROTOLOGTOOL = false
│
├─── SystemUIApplication.onCreate()
│   │
│   ├─── [DependencyInjection] Dagger 初始化
│   │   mInitializer.onContextAvailable()
│   │   mSysUIComponent = mInitializer.getSysUIComponent()
│   │
│   ├─── setTheme(R.style.Theme_SystemUI)
│   │
│   └─── registerReceiver(BOOT_COMPLETED)
│
├─── SystemUIService 构造函数 (@Inject)
│   │   Dagger 注入: Handler, DumpHandler, BroadcastDispatcher, etc.
│
├─── SystemUIService.onCreate()
│   │
│   ├─── startSystemUserServicesIfNeeded()
│   │
│   ├─── mLogBufferFreezer.attach()
│   │
│   └─── startService(SystemUIAuxiliaryDumpService)
│
├─── startSystemUserServicesIfNeeded()
│   │
│   ├─── 获取 mSysUIComponent.getStartables()
│   ├─── 获取 mSysUIComponent.getPerUserStartables()
│   │
│   └─── 拓扑排序启动:
│       │
│       ├─── [Round 1] 启动无依赖的 CoreStartable
│       │   - CentralSurfacesImpl.start()
│       │   - KeyguardViewMediator.start()
│       │   - etc.
│       │
│       ├─── [Round 2] 启动依赖已满足的 CoreStartable
│       │   - NotificationListener.start() (依赖 CentralSurfacesImpl)
│       │   - etc.
│       │
│       └─── [Round N] 直到所有服务启动完成
│
├─── BOOT_COMPLETED 广播
│   │
│   └─── 遍历所有 CoreStartable.onBootCompleted()
│
└─── SystemUI 启动完成
```

### 2.5 主要 CoreStartable 服务列表

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              主要 CoreStartable 服务 (Android 16)                           │
└─────────────────────────────────────────────────────────────────────────────┘

系统用户服务:
┌───────────────────────────────────┬───────────────────────────────────────┐
│           类名                     │                  功能                  │
├───────────────────────────────────┼───────────────────────────────────────┤
│  CentralSurfacesImpl              │  状态栏/导航栏/锁屏中央管理             │
│  KeyguardViewMediator             │  锁屏中介                              │
│  NotificationListener             │  通知监听器                            │
│  VolumeUI                         │  音量 UI                              │
│  PowerUI                          │  电源 UI                              │
│  DockUI                           │  底座 UI                              │
│  ShortcutKeyDispatcher            │  快捷键分发                            │
│  LatencyTester                    │  延迟测试                              │
│  GarbageMonitor$Service           │  GC 监控                              │
│  KeyguardClipController           │  锁屏裁剪控制器                        │
│  EdgeBackGestureHandler           │  边缘返回手势                          │
│  UiModeManagerService             │  UI 模式管理                          │
│  DisplayViewportUpdater           │  显示视口更新                          │
│  ScreenDecorations                │  屏幕装饰 (圆角/刘海)                  │
│  SlicePermissionManager           │  Slice 权限管理                        │
│  TouchAnalyticsManager            │  触摸分析                              │
│  AccessibilityFloatingMenu        │  无障碍悬浮菜单                        │
└───────────────────────────────────┴───────────────────────────────────────┘

每用户服务:
┌───────────────────────────────────┬───────────────────────────────────────┐
│           类名                     │                  功能                  │
├───────────────────────────────────┼───────────────────────────────────────┤
│  NotificationShadeWindowController│  通知 Shade 窗口控制器                 │
│  StatusBarCoordinator             │  状态栏协调器                          │
│  ConfigurationControllerStartable │  配置变更控制器                        │
│  AppClipsService                  │  App Clips 服务                       │
│  CaptivePortalLoginActivityNotifier│  强制门户登录通知                      │
│  TvPipManager                     │  TV PiP 管理器                        │
└───────────────────────────────────┴───────────────────────────────────────┘
```

---

## 3. AOD (Always On Display) 详解

### 3.1 AOD 概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       AOD (Always On Display)                             │
└─────────────────────────────────────────────────────────────────────────────┘

AOD (Always On Display) 是一种在手机息屏后仍然显示部分信息的特性:

显示内容:
┌───────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│    ┌─────────────────────────────────────────┐                          │
│    │              AOD 显示区域                │                          │
│    │                                          │                          │
│    │     ╭─────────────────────────────╮    │                          │
│    │        │    12:30 PM            │    │  ← 时钟                  │
│    │        ╰─────────────────────────────╯    │                          │
│    │                                          │                          │
│    │     ┌──────┐  ┌──────┐  ┌──────┐      │  ← 通知图标              │
│    │     │ 💬 │  │ 📧 │  │ 🔔 │      │                          │
│    │     └──────┘  └──────┘  └──────┘      │                          │
│    │                                          │                          │
│    │     支付宝消息: 您有新的账单          │  ← 通知预览               │
│    │                                          │                          │
│    │     ┌────────────────────────────┐    │  ← 指纹图标              │
│    │     │         👆                  │    │                          │
│    │     └────────────────────────────┘    │                          │
│    │                                          │                          │
│    └─────────────────────────────────────────┘                          │
│                                                                           │
│    屏幕显示区域外 (LCD 关闭，只有部分像素点亮)                             │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

AOD 技术特点:
1. 低功耗: 只点亮少量像素
2. 显示内容可定制
3. 支持通知显示
4. 支持触控唤醒
5. 支持手势唤醒
```

### 3.2 AOD 架构 (Android 16)

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD 架构 (Android 16 AOSP)                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          应用层 (Settings)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                 AmbientDisplayConfiguration                         │   │
│  │   - alwaysOnEnabled() 检查 AOD 开关                                │   │
│  │   - pulseOnNotificationEnabled() 通知脉冲开关                      │   │
│  │   - dozePickupSensorAvailable() 抬起唤醒开关                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SystemUI Doze 模块 (Dagger 注入)                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DozeService (extends DreamService)               │   │
│  │   - onDreamingStarted() → mDozeMachine.requestState(INITIALIZED)   │   │
│  │   - onDreamingStopped() → mDozeMachine.requestState(FINISH)        │   │
│  │   - 实现 DozeMachine.Service 接口                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DozeMachine (@DozeScope)                         │   │
│  │   - 状态机核心，管理所有 Doze 状态转换                              │   │
│  │   - Part[] 数组：所有组件注册为 Part                                │   │
│  │   - requestState() / requestPulse() 状态请求                        │   │
│  │   - transitionTo() 状态转换执行                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         ▼                          ▼                          ▼            │
│  ┌─────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐    │
│  │  DozeTriggers   │  │  DozeScreenState    │  │  DozeScreenBrightness│    │
│  │  (触发器管理)    │  │  (屏幕状态控制)      │  │  (亮度控制)          │    │
│  └────────┬────────┘  └─────────────────────┘  └─────────────────────┘    │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DozeSensors                                       │   │
│  │   - TriggerSensor[] 传感器数组                                       │   │
│  │   - pickup/doubleTap/tap/longPress/udfps/quickPickup               │   │
│  │   - PluginSensor (wakeDisplay/wakeLockScreen)                       │   │
│  │   - ProximitySensor 距离传感器                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DozeHost (接口)                                   │   │
│  │   - addCallback() / removeCallback()                                │   │
│  │   - startDozing() / stopDozing()                                    │   │
│  │   - pulseWhileDozing()                                              │   │
│  │   - isAlwaysOnSuppressed() / isPulsePending()                       │   │
│  │   - setDozeScreenBrightness()                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Framework 层                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PowerManagerService                              │   │
│  │   - wakeUp() 唤醒设备                                               │   │
│  │   - DreamService 管理                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HAL 层                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Display HAL                                       │   │
│  │   - Display.STATE_DOZE / STATE_DOZE_SUSPEND / STATE_ON              │   │
│  │   - 低功耗显示模式                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 源码文件结构

```
frameworks/base/packages/SystemUI/src/com/android/systemui/doze/
├── DozeService.java              # DreamService 入口
├── DozeMachine.java              # 状态机核心
├── DozeMachine.State             # 状态枚举 (内部类)
├── DozeMachine.Part              # Part 接口 (内部类)
├── DozeMachine.Service           # Service 接口 (内部类)
├── DozeTriggers.java             # 触发器管理 (实现 Part)
├── DozeSensors.java              # 传感器管理
├── DozeScreenState.java          # 屏幕状态控制 (实现 Part)
├── DozeScreenBrightness.java     # 亮度控制
├── DozeHost.java                 # SystemUI 通信接口
├── DozeHost.Callback             # 回调接口
├── DozeLog.java                  # 日志工具
├── DozeLogger.kt                 # Kotlin 日志
├── DozePauser.java               # 暂停控制
├── DozeReceiver.java             # 广播接收器
├── DozeDockHandler.java          # 底座事件处理
├── DozeFalsingManagerAdapter.java # 误触管理
├── DozeFactory.java              # 工厂类
├── DozePausingService.java       # 暂停服务
├── DozeWakeLock.java             # WakeLock 管理
├── DozeUi.java                   # UI 控制
├── AlwaysOnDisplayPolicy.java    # AOD 策略
├── DozeAuthRemover.java          # 认证移除
├── DozeBrightnessHostForwarder.java # 亮度转发
├── DozeSuspendScreenState.java   # 挂起屏幕状态
├── DozeScreenStatePreventingAdapter.java # 状态适配器
└── dagger/
    ├── DozeComponent.java        # Dagger 组件
    ├── DozeModule.java           # Dagger 模块
    └── DozeScope.java            # Dagger 作用域
```

### 3.3 AOD 状态机 (DozeMachine)

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeMachine.java`

```java
/**
 * DozeMachine 状态机 (Android 16 AOSP)
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeMachine.java
 *
 * DozeMachine 实现状态机来协调 UI 和触发器如何工作，
 * 并与电源和屏幕状态进行交互。
 */

@DozeScope
public class DozeMachine {

    static final String TAG = "DozeMachine";
    static final boolean DEBUG = DozeService.DEBUG;

    /**
     * Doze 状态枚举 - 定义所有可能的 Doze 状态
     */
    public enum State {
        /** 默认状态。转换到 INITIALIZED 来启动 Doze */
        UNINITIALIZED,

        /** Doze 组件已设置。接下来转换到 DOZE 或 DOZE_AOD */
        INITIALIZED,

        /** 常规 Doze。设备休眠，监听脉冲触发器 */
        DOZE,

        /** 深度 Doze。设备休眠，不监听脉冲触发器 */
        DOZE_SUSPEND_TRIGGERS,

        /** 常亮显示。设备休眠，显示 UI，监听脉冲触发器 */
        DOZE_AOD,

        /** 已请求脉冲。设备唤醒，准备 UI */
        DOZE_REQUEST_PULSE,

        /** 正在显示脉冲。设备唤醒，显示 UI */
        DOZE_PULSING,

        /** 正在显示明亮壁纸的脉冲 */
        DOZE_PULSING_BRIGHT,

        /** 脉冲显示完成。接下来转换到 DOZE 或 DOZE_AOD */
        DOZE_PULSE_DONE,

        /** Doze 完成。DozeService 已结束 */
        FINISH,

        /** AOD 但显示屏暂时关闭 */
        DOZE_AOD_PAUSED,

        /** AOD，距离传感器接近，超时后转换到 DOZE_AOD_PAUSED */
        DOZE_AOD_PAUSING,

        /** 常亮显示。设备唤醒，显示底座 UI，监听脉冲触发器 */
        DOZE_AOD_DOCKED;

        /** 是否可以触发脉冲 */
        boolean canPulse() {
            switch (this) {
                case DOZE:
                case DOZE_AOD:
                case DOZE_AOD_PAUSED:
                case DOZE_AOD_PAUSING:
                case DOZE_AOD_DOCKED:
                    return true;
                default:
                    return false;
            }
        }

        /** 是否保持唤醒状态 */
        boolean staysAwake() {
            switch (this) {
                case DOZE_REQUEST_PULSE:
                case DOZE_PULSING:
                case DOZE_PULSING_BRIGHT:
                case DOZE_AOD_DOCKED:
                    return true;
                default:
                    return false;
            }
        }

        /** 是否是常亮显示状态 */
        boolean isAlwaysOn() {
            return this == DOZE_AOD || this == DOZE_AOD_DOCKED;
        }

        /** 获取对应的屏幕状态 */
        int screenState(DozeParameters parameters) {
            switch (this) {
                case UNINITIALIZED:
                case INITIALIZED:
                    return parameters.shouldControlScreenOff()
                            ? Display.STATE_ON : Display.STATE_OFF;
                case DOZE_REQUEST_PULSE:
                    return parameters.getDisplayNeedsBlanking()
                            ? Display.STATE_OFF : Display.STATE_ON;
                case DOZE_AOD_PAUSED:
                case DOZE:
                case DOZE_SUSPEND_TRIGGERS:
                    return Display.STATE_OFF;
                case DOZE_PULSING:
                case DOZE_PULSING_BRIGHT:
                case DOZE_AOD_DOCKED:
                    return Display.STATE_ON;
                case DOZE_AOD:
                case DOZE_AOD_PAUSING:
                    return Display.STATE_DOZE_SUSPEND;
                default:
                    return Display.STATE_UNKNOWN;
            }
        }
    }

    // 核心依赖 (通过 Dagger 注入)
    private final Service mDozeService;
    private final WakeLock mWakeLock;
    private final AmbientDisplayConfiguration mAmbientDisplayConfig;
    private final WakefulnessLifecycle mWakefulnessLifecycle;
    private final DozeHost mDozeHost;
    private final DockManager mDockManager;
    private final Part[] mParts;
    private final UserTracker mUserTracker;

    // 当前状态
    private State mState = State.UNINITIALIZED;
    private int mPulseReason;

    @Inject
    public DozeMachine(@WrappedService Service service,
            AmbientDisplayConfiguration ambientDisplayConfig,
            WakeLock wakeLock, WakefulnessLifecycle wakefulnessLifecycle,
            DozeLog dozeLog, DockManager dockManager,
            DozeHost dozeHost, Part[] parts, UserTracker userTracker) {
        // 初始化...
    }
}
```

#### 状态转换图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DozeMachine 状态转换图 (Android 16)                      │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │ UNINITIALIZED   │ ← 初始状态
                              └────────┬────────┘
                                       │ requestState(INITIALIZED)
                                       ▼
                              ┌─────────────────┐
                              │  INITIALIZED    │ ← 组件初始化完成
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
           ┌───────────────┐  ┌───────────────┐  ┌────────────────┐
           │     DOZE      │  │   DOZE_AOD    │  │DOZE_AOD_DOCKED │
           │ (屏幕关闭)     │  │ (常亮显示)    │  │  (底座模式)     │
           └───────┬───────┘  └───────┬───────┘  └───────┬────────┘
                   │                  │                  │
                   │  requestPulse()  │                  │
                   ▼                  ▼                  ▼
           ┌───────────────────────────────────────────────────┐
           │              DOZE_REQUEST_PULSE                    │
           │              (请求脉冲)                             │
           └───────────────────────┬───────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │      DOZE_PULSING        │ ← 显示脉冲
                    │    (或 DOZE_PULSING_BRIGHT)│
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │     DOZE_PULSE_DONE      │ ← 脉冲完成
                    └────────────┬─────────────┘
                                 │
                                 ▼ (返回 DOZE/DOZE_AOD)

           ┌───────────────────────────────────────────────────────┐
           │                    特殊状态                            │
           ├───────────────────────────────────────────────────────┤
           │  DOZE_AOD_PAUSING  →  DOZE_AOD_PAUSED  (距离传感器接近)│
           │  DOZE_SUSPEND_TRIGGERS (车载模式，禁用触发器)          │
           │  FINISH (Doze 结束)                                   │
           └───────────────────────────────────────────────────────┘
```

### 3.4 AOD 显示流程 (Android 16)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD 启动流程 (Android 16)                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. DreamService 启动                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

PowerManagerService:
├── 屏幕关闭超时
├── 调用 DreamManager.startDream()
└── 启动 DozeService

DozeService:
├── onCreate() → setWindowless(true)
├── 构建 Dagger DozeComponent
└── 获取 DozeMachine 实例

┌─────────────────────────────────────────────────────────────────────────────┐
│  2. 状态初始化                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

DozeService.onDreamingStarted():
├── mDozeMachine.requestState(State.INITIALIZED)
└── startDozing()

DozeMachine.transitionTo(UNINITIALIZED → INITIALIZED):
├── 执行所有 Part.transitionTo()
├── DozeTriggers: registerCallbacks()
├── DozeSensors: requestTemporaryDisable()
└── resolveIntermediateState(INITIALIZED)

resolveIntermediateState():
├── 检查 DockManager.isDocked() → DOZE_AOD_DOCKED
├── 检查 alwaysOnEnabled() → DOZE_AOD
└── 否则 → DOZE

┌─────────────────────────────────────────────────────────────────────────────┐
│  3. 进入 AOD 模式                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

DozeMachine.transitionTo(INITIALIZED → DOZE_AOD):
├── DozeTriggers.transitionTo():
│   ├── mWantProxSensor = true
│   ├── mWantSensors = true
│   └── mDozeSensors.setListening(true, true, true)
├── DozeScreenState.transitionTo():
│   ├── screenState = Display.STATE_DOZE_SUSPEND
│   └── mHandler.postDelayed(mApplyPendingScreenState, ENTER_DOZE_DELAY)
└── mDozeLog.traceState(DOZE_AOD)

┌─────────────────────────────────────────────────────────────────────────────┐
│  4. 传感器触发脉冲                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

DozeSensors 触发流程:
├── 传感器触发 (pickup/doubleTap/tap)
├── TriggerSensor.onTrigger()
├── mSensorCallback.onSensorPulse(reason, x, y, values)
└── DozeTriggers.onSensor()

DozeTriggers.onSensor():
├── proximityCheckThenCall() - 检查距离传感器
├── gentleWakeUp(reason) - 唤醒设备
│   └── mMachine.wakeUp(reason)
└── 或 requestPulse(reason) - 请求脉冲

DozeMachine.requestPulse():
├── 检查 canPulse(currentState)
├── mDozeHost.setPulsePending(true)
├── transitionTo(DOZE_REQUEST_PULSE)
└── transitionTo(DOZE_PULSING)

┌─────────────────────────────────────────────────────────────────────────────┐
│  5. 脉冲显示                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

DozeScreenState.transitionTo(DOZE_PULSING):
├── screenState = Display.STATE_ON
└── applyScreenState(Display.STATE_ON)

DozeHost.pulseWhileDozing():
├── 显示脉冲内容 (通知、时钟等)
└── PulseCallback.onPulseFinished()

DozeMachine.transitionTo(DOZE_PULSE_DONE):
├── resolveIntermediateState(DOZE_PULSE_DONE)
└── 返回 DOZE 或 DOZE_AOD
```

#### 脉冲触发原因 (DozeLog.PULSE_REASON_*)

```java
/**
 * 脉冲触发原因常量 (来自 DozeLog.java)
 */
public class DozeLog {

    public static final int PULSE_REASON_NONE = 0;
    public static final int PULSE_REASON_INTENT = 1;
    public static final int PULSE_REASON_NOTIFICATION = 2;
    public static final int PULSE_REASON_SENSOR_SIGMOTION = 3;
    public static final int REASON_SENSOR_PICKUP = 4;
    public static final int REASON_SENSOR_DOUBLE_TAP = 5;
    public static final int PULSE_REASON_SENSOR_LONG_PRESS = 6;
    public static final int PULSE_REASON_DOCKING = 7;
    public static final int REASON_SENSOR_WAKEUP = 8;
    public static final int REASON_SENSOR_TAP = 9;
    public static final int REASON_SENSOR_UDFPS_LONG_PRESS = 10;
    public static final int REASON_SENSOR_WAKE_REACH = 11;
    public static final int PULSE_REASON_FINGERPRINT_ACTIVATED = 12;
    public static final int REASON_SENSOR_QUICK_PICKUP = 13;
}
```

### 3.5 AOD 核心组件源码 (Android 16)

#### DozeService - Doze 服务入口

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeService.java`

```java
/**
 * DozeService - Doze 服务的入口点
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeService.java
 *
 * DozeService 继承自 DreamService，是 Android Doze 模式的入口。
 * 它通过 Dagger 注入 DozeComponent 来构建完整的 Doze 功能。
 */
public class DozeService extends DreamService
        implements DozeMachine.Service, RequestDoze, PluginListener<DozeServicePlugin> {

    private static final String TAG = "DozeService";
    static final boolean DEBUG = Log.isLoggable(TAG, Log.DEBUG);

    private final DozeComponent.Builder mDozeComponentBuilder;
    private DozeMachine mDozeMachine;
    private DozeServicePlugin mDozePlugin;
    private PluginManager mPluginManager;
    private DozeLog mDozeLog;
    private Executor mBgExecutor;

    @Inject
    public DozeService(DozeComponent.Builder dozeComponentBuilder, PluginManager pluginManager,
            DozeLog dozeLog, @UiBackground Executor bgExecutor) {
        mDozeLog = dozeLog;
        mBgExecutor = bgExecutor;
        mDozeComponentBuilder = dozeComponentBuilder;
        setDebug(DEBUG);
        mPluginManager = pluginManager;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        setWindowless(true);

        mPluginManager.addPluginListener(this, DozeServicePlugin.class, false);
        DozeComponent dozeComponent = mDozeComponentBuilder.build(this);
        mDozeMachine = dozeComponent.getDozeMachine();
        mDozeMachine.onConfigurationChanged(getResources().getConfiguration());
    }

    @Override
    public void onDreamingStarted() {
        super.onDreamingStarted();
        // 请求初始化状态
        mDozeMachine.requestState(DozeMachine.State.INITIALIZED);
        startDozing();
        if (mDozePlugin != null) {
            mDozePlugin.onDreamingStarted();
        }
    }

    @Override
    public void onDreamingStopped() {
        super.onDreamingStopped();
        // 请求结束状态
        mDozeMachine.requestState(DozeMachine.State.FINISH);
        if (mDozePlugin != null) {
            mDozePlugin.onDreamingStopped();
        }
    }

    @Override
    public void requestWakeUp(@DozeLog.Reason int reason) {
        final PowerManager pm = getSystemService(PowerManager.class);
        pm.wakeUp(SystemClock.uptimeMillis(), DozeLog.getPowerManagerWakeReason(reason),
                "com.android.systemui:NODOZE " + DozeLog.reasonToString(reason));
    }

    @Override
    public void setDozeScreenState(int state) {
        mDozeLog.traceDisplayState(state, false);
        super.setDozeScreenState(state);
        mDozeLog.traceDisplayState(state, true);
        if (mDozeMachine != null) {
            mDozeMachine.onScreenState(state);
        }
    }
}
```

#### DozeHost - Doze 与 SystemUI 的通信接口

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeHost.java`

```java
/**
 * DozeHost - Doze 服务与 SystemUI 其他部分通信的接口
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeHost.java
 */
public interface DozeHost {

    /** 添加/移除回调 */
    void addCallback(@NonNull Callback callback);
    void removeCallback(@NonNull Callback callback);

    /** 开始/停止 Doze */
    void startDozing();
    void stopDozing();

    /** 脉冲控制 */
    void pulseWhileDozing(@NonNull PulseCallback callback, int reason);
    void extendPulse(int reason);
    void stopPulsing();

    /** 时间更新 */
    @MainThread
    void dozeTimeTick();

    /** 状态查询 */
    boolean isPowerSaveActive();
    boolean isPulsingBlocked();
    boolean isProvisioned();
    boolean isPulsePending();
    boolean isAlwaysOnSuppressed();

    /** 设置脉冲待定状态 */
    void setPulsePending(boolean isPulsePending);

    /** 设置唤醒动画 */
    void setAnimateWakeup(boolean animateWakeup);

    /** SLPI 触摸事件 */
    void onSlpiTap(float x, float y);

    /** AOD 调光 */
    default void setAodDimmingScrim(float scrimOpacity) {}

    /** 屏幕亮度 */
    void setDozeScreenBrightness(int value);
    void setDozeScreenBrightnessFloat(float value);

    /** 温柔睡眠准备 */
    void prepareForGentleSleep(Runnable onDisplayOffCallback);
    void cancelGentleSleep();

    /** 脉冲时忽略触摸 */
    void onIgnoreTouchWhilePulsing(boolean ignore);

    /**
     * 回调接口 - 接收 Doze 事件
     */
    interface Callback {
        /** 高优先级通知到达 */
        default void onNotificationAlerted(Runnable onPulseSuppressedListener) {}

        /** 省电模式变化 */
        default void onPowerSaveChanged(boolean active) {}

        /** 常亮显示抑制状态变化 */
        default void onAlwaysOnSuppressedChanged(boolean suppressed) {}

        /** Dozing 状态可能更新 */
        default void onDozingChanged(boolean isDozing) {}

        /** 侧边指纹采集开始 */
        default void onSideFingerprintAcquisitionStarted() {}
    }

    /**
     * 脉冲回调接口
     */
    interface PulseCallback {
        void onPulseStarted();
        void onPulseFinished();
    }
}
```

#### DozeTriggers - 触发器管理

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeTriggers.java`

```java
/**
 * DozeTriggers - 处理环境状态变化的触发器
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeTriggers.java
 *
 * 实现 DozeMachine.Part 接口，响应各种触发事件：
 * - 通知到达
 * - 传感器事件 (抬起、双击、长按等)
 * - 距离传感器
 * - 底座事件
 */
@DozeScope
public class DozeTriggers implements DozeMachine.Part {

    private static final String TAG = "DozeTriggers";
    private static final int PROXIMITY_TIMEOUT_DELAY_MS = 500;

    private final Context mContext;
    private DozeMachine mMachine;
    private final DozeLog mDozeLog;
    private final DozeSensors mDozeSensors;
    private final DozeHost mDozeHost;
    private final AmbientDisplayConfiguration mConfig;
    private final DozeParameters mDozeParameters;
    private final WakeLock mWakeLock;
    private final DockManager mDockManager;
    private final ProximityCheck mProxCheck;

    @Inject
    public DozeTriggers(Context context, DozeHost dozeHost,
            AmbientDisplayConfiguration config,
            DozeParameters dozeParameters, AsyncSensorManager sensorManager,
            WakeLock wakeLock, DockManager dockManager,
            ProximitySensor proximitySensor, ProximityCheck proxCheck,
            DozeLog dozeLog, BroadcastDispatcher broadcastDispatcher,
            SecureSettings secureSettings, AuthController authController,
            UiEventLogger uiEventLogger, SessionTracker sessionTracker,
            KeyguardStateController keyguardStateController,
            DevicePostureController devicePostureController,
            UserTracker userTracker,
            SelectedUserInteractor selectedUserInteractor) {
        // 初始化...
        mDozeSensors = new DozeSensors(mContext.getResources(), mSensorManager,
                dozeParameters, config, wakeLock, this::onSensor, this::onProximityFar,
                dozeLog, proximitySensor, secureSettings, authController,
                devicePostureController, selectedUserInteractor);
    }

    /**
     * 传感器事件处理
     */
    @VisibleForTesting
    void onSensor(int pulseReason, float screenX, float screenY, float[] rawValues) {
        boolean isDoubleTap = pulseReason == DozeLog.REASON_SENSOR_DOUBLE_TAP;
        boolean isTap = pulseReason == DozeLog.REASON_SENSOR_TAP;
        boolean isPickup = pulseReason == DozeLog.REASON_SENSOR_PICKUP;
        boolean isLongPress = pulseReason == DozeLog.PULSE_REASON_SENSOR_LONG_PRESS;
        boolean isWakeOnPresence = pulseReason == DozeLog.REASON_SENSOR_WAKE_UP_PRESENCE;

        if (isDoubleTap || isTap) {
            mDozeHost.onSlpiTap(screenX, screenY);
            gentleWakeUp(pulseReason);
        } else if (isPickup) {
            if (shouldDropPickupEvent()) {
                mDozeLog.traceSensorEventDropped(pulseReason, "keyguard occluded");
                return;
            }
            gentleWakeUp(pulseReason);
        } else {
            mDozeHost.extendPulse(pulseReason);
        }
    }

    /**
     * 距离传感器事件处理
     */
    private void onProximityFar(boolean far) {
        if (mMachine.isExecutingTransition()) {
            return;
        }

        final boolean near = !far;
        final DozeMachine.State state = mMachine.getState();
        final boolean paused = (state == DozeMachine.State.DOZE_AOD_PAUSED);
        final boolean pausing = (state == DozeMachine.State.DOZE_AOD_PAUSING);
        final boolean aod = (state == DozeMachine.State.DOZE_AOD);

        if (far && (paused || pausing)) {
            // 距离传感器远离，恢复 AOD
            mMachine.requestState(DozeMachine.State.DOZE_AOD);
        } else if (near && aod) {
            // 距离传感器接近，开始暂停 AOD 倒计时
            mMachine.requestState(DozeMachine.State.DOZE_AOD_PAUSING);
        }
    }

    /**
     * 状态转换处理
     */
    @Override
    public void transitionTo(DozeMachine.State oldState, DozeMachine.State newState) {
        switch (newState) {
            case INITIALIZED:
                registerCallbacks();
                mDozeSensors.requestTemporaryDisable();
                break;
            case DOZE:
                mWantSensors = true;
                mInAod = false;
                break;
            case DOZE_AOD:
                mWantProxSensor = true;
                mWantSensors = true;
                mInAod = true;
                break;
            case DOZE_SUSPEND_TRIGGERS:
            case FINISH:
                stopListeningToAllTriggers();
                break;
        }
        mDozeSensors.setListening(mWantSensors, mWantTouchScreenSensors, mInAod);
    }
}
```

#### DozeSensors - 传感器管理

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeSensors.java`

```java
/**
 * DozeSensors - 跟踪和注册/注销传感器
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeSensors.java
 *
 * 传感器注册取决于:
 * - 传感器存在性/可用性
 * - 用户配置 (某些可通过设置开关)
 * - 距离传感器使用
 * - 触摸状态
 * - 设备姿态
 *
 * 支持的传感器:
 * - 抬起手势 (pickup gesture)
 * - 单击和双击手势 (single and double tap)
 * - UDFPS 长按手势
 * - reach 和 presence 手势
 * - 快速抬起手势 (quick pickup)
 */
public class DozeSensors {
    private static final String TAG = "DozeSensors";

    private final AsyncSensorManager mSensorManager;
    private final AmbientDisplayConfiguration mConfig;
    private final WakeLock mWakeLock;
    private final DozeLog mDozeLog;
    private final ProximitySensor mProximitySensor;

    // 触发传感器数组
    @VisibleForTesting
    protected TriggerSensor[] mTriggerSensors;

    // 传感器回调
    private final Callback mSensorCallback;
    private final Consumer<Boolean> mProxCallback;

    DozeSensors(Resources resources, AsyncSensorManager sensorManager,
            DozeParameters dozeParameters, AmbientDisplayConfiguration config,
            WakeLock wakeLock, Callback sensorCallback, Consumer<Boolean> proxCallback,
            DozeLog dozeLog, ProximitySensor proximitySensor,
            SecureSettings secureSettings, AuthController authController,
            DevicePostureController devicePostureController,
            SelectedUserInteractor selectedUserInteractor) {
        // ...
        mTriggerSensors = new TriggerSensor[] {
            // 显著运动传感器
            new TriggerSensor(
                    mSensorManager.getDefaultSensor(Sensor.TYPE_SIGNIFICANT_MOTION),
                    null, dozeParameters.getPulseOnSigMotion(),
                    DozeLog.PULSE_REASON_SENSOR_SIGMOTION,
                    false, false),
            // 抬起手势传感器
            new TriggerSensor(
                    mSensorManager.getDefaultSensor(Sensor.TYPE_PICK_UP_GESTURE),
                    Settings.Secure.DOZE_PICK_UP_GESTURE,
                    config.dozePickupSensorAvailable(),
                    DozeLog.REASON_SENSOR_PICKUP,
                    false, false),
            // 双击传感器
            new TriggerSensor(
                    findSensor(config.doubleTapSensorType()),
                    Settings.Secure.DOZE_DOUBLE_TAP_GESTURE,
                    true, DozeLog.REASON_SENSOR_DOUBLE_TAP,
                    dozeParameters.doubleTapReportsTouchCoordinates(),
                    true),
            // 单击传感器
            new TriggerSensor(
                    findSensors(config.tapSensorTypeMapping()),
                    Settings.Secure.DOZE_TAP_SCREEN_GESTURE,
                    true, DozeLog.REASON_SENSOR_TAP,
                    true, true),
            // UDFPS 长按传感器
            new TriggerSensor(
                    findSensor(config.udfpsLongPressSensorType()),
                    "doze_pulse_on_auth", true,
                    udfpsLongPressConfigured(),
                    DozeLog.REASON_SENSOR_UDFPS_LONG_PRESS,
                    true, true),
            // 唤醒显示手势
            new PluginSensor(
                    new SensorManagerPlugin.Sensor(TYPE_WAKE_DISPLAY),
                    Settings.Secure.DOZE_WAKE_DISPLAY_GESTURE,
                    mConfig.wakeScreenGestureAvailable(),
                    DozeLog.REASON_SENSOR_WAKE_UP_PRESENCE,
                    false, false),
            // 快速抬起传感器
            new TriggerSensor(
                    findSensor(config.quickPickupSensorType()),
                    Settings.Secure.DOZE_QUICK_PICKUP_GESTURE,
                    true, quickPickUpConfigured(),
                    DozeLog.REASON_SENSOR_QUICK_PICKUP,
                    false, false),
        };
    }

    /**
     * 设置传感器监听状态
     */
    public void setListening(boolean listen, boolean includeTouchScreenSensors,
            boolean includeAodOnlySensors) {
        mListening = listen;
        mListeningTouchScreenSensors = includeTouchScreenSensors;
        mListeningAodOnlySensors = includeAodOnlySensors;
        updateListening();
    }

    /**
     * 传感器回调接口
     */
    public interface Callback {
        /**
         * 传感器请求脉冲时调用
         * @param pulseReason 请求传感器，如 REASON_SENSOR_PICKUP
         * @param screenX 传感器触发的屏幕位置 X，或 -1
         * @param screenY 传感器触发的屏幕位置 Y，或 -1
         * @param rawValues 事件的原始值数组
         */
        void onSensorPulse(int pulseReason, float screenX, float screenY, float[] rawValues);
    }
}
```

#### DozeScreenState - 屏幕状态控制

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeScreenState.java`

```java
/**
 * DozeScreenState - 控制 Doze 时的屏幕状态
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeScreenState.java
 */
@DozeScope
public class DozeScreenState implements DozeMachine.Part {

    private static final String TAG = "DozeScreenState";

    /** 进入低功耗模式的延迟 */
    private static final int ENTER_DOZE_DELAY = 4000;
    /** 进入低功耗模式前隐藏壁纸的延迟 */
    public static final int ENTER_DOZE_HIDE_WALLPAPER_DELAY = 2500;
    /** UDFPS 激活时额外的显示状态延迟 */
    public static final int UDFPS_DISPLAY_STATE_DELAY = 1200;

    private final DozeMachine.Service mDozeService;
    private final Handler mHandler;
    private final DozeParameters mParameters;
    private final DozeHost mDozeHost;
    private final AuthController mAuthController;
    private final DozeLog mDozeLog;
    private final DozeScreenBrightness mDozeScreenBrightness;

    @Inject
    public DozeScreenState(
            @WrappedService DozeMachine.Service service,
            @Main Handler handler, DozeHost host,
            DozeParameters parameters, WakeLock wakeLock,
            AuthController authController,
            Provider<UdfpsController> udfpsControllerProvider,
            DozeLog dozeLog, DozeScreenBrightness dozeScreenBrightness,
            SelectedUserInteractor selectedUserInteractor) {
        // 初始化...
    }

    @Override
    public void transitionTo(DozeMachine.State oldState, DozeMachine.State newState) {
        int screenState = newState.screenState(mParameters);
        mDozeHost.cancelGentleSleep();

        if (newState == DozeMachine.State.FINISH) {
            mPendingScreenState = Display.STATE_UNKNOWN;
            mHandler.removeCallbacks(mApplyPendingScreenState);
            applyScreenState(screenState);
            mWakeLock.setAcquired(false);
            return;
        }

        final boolean pulseEnding = oldState == DOZE_PULSE_DONE && newState.isAlwaysOn();
        final boolean turningOn = (oldState == DOZE_AOD_PAUSED || oldState == DOZE)
                && newState.isAlwaysOn();
        final boolean justInitialized = oldState == DozeMachine.State.INITIALIZED;

        if (justInitialized || pulseEnding || turningOn) {
            mPendingScreenState = screenState;
            mHandler.post(mApplyPendingScreenState);
        } else {
            applyScreenState(screenState);
        }
    }

    private void applyScreenState(int screenState) {
        if (screenState != Display.STATE_UNKNOWN) {
            mDozeService.setDozeScreenState(screenState);
            if (screenState == Display.STATE_DOZE) {
                mDozeScreenBrightness.updateBrightnessAndReady(false);
            }
        }
    }
}
```

---

## 4. 通知系统详解

### 4.1 通知系统概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Android 通知系统架构                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           应用层 (Apps)                                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ 微信    │ │ 钉钉    │ │ 支付宝  │ │ 抖音    │ │  Phone  │        │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘        │
│       │           │           │           │           │               │
│       └───────────┴───────────┴───────────┴───────────┘               │
│                               │                                       │
│                               ▼                                       │
│              ┌─────────────────────────────────────┐                │
│              │     NotificationCompat.Builder       │                │
│              │     - 创建通知                       │                │
│              │     - 设置样式                       │                │
│              │     - 设置动作                       │                │
│              └──────────────────┬──────────────────┘                │
│                                  │                                      │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │ NotificationManager.notify()
                                   ▼
┌──────────────────────────────────┼──────────────────────────────────────┐
│                                  │     Framework 层                    │
│                                  │                                      │
│              ┌──────────────────┴──────────────────┐                │
│              │     NotificationManagerService        │                │
│              │     (NMS) - 通知管理服务             │                │
│              │                                      │                │
│              │  ┌────────────────────────────┐   │                │
│              │  │  NotificationRecord         │   │                │
│              │  │  - 通知数据                 │   │                │
│              │  │  - PostNotificationRunnable │   │                │
│              │  │  - EnqueueCallback         │   │                │
│              │  └────────────────────────────┘   │                │
│              └──────────────────┬──────────────────┘                │
│                                  │                                      │
└──────────────────────────────────┼──────────────────────────────────────┘
                                   │ Binder IPC
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SystemUI 进程                                    │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NotificationListenerService                    │   │
│  │   - 接收 NMS 通知                                                │   │
│  │   - 转发给 NotificationEntryManager                               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                  │                                      │
│                                  ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NotificationEntryManager                       │   │
│  │   - 管理通知条目                                                  │   │
│  │   - 处理通知状态                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                  │                                      │
│                                  ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NotificationViewManager                        │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │   │StatusBarIcon │  │ Notification │  │  Notification │         │   │
│  │   │    通知图标  │  │   PanelView  │  │   StackView   │         │   │
│  │   └──────────────┘  └──────────────┘  └──────────────┘         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 通知发送流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       通知发送完整流程                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. 应用层: 创建通知                                                       │
└─────────────────────────────────────────────────────────────────────────────┘

// 创建通知
NotificationCompat.Builder builder = new NotificationCompat.Builder(context, channelId)
    .setSmallIcon(R.drawable.ic_notification)    // 小图标
    .setContentTitle("标题")                     // 标题
    .setContentText("内容")                       // 内容
    .setStyle(new NotificationCompat.BigTextStyle().bigText("长文本内容..."))
    .setPriority(NotificationCompat.PRIORITY_HIGH) // 优先级
    .setCategory(NotificationCompat.CATEGORY_MESSAGE) // 类别
    .setAutoCancel(true);                         // 点击取消

// 发送通知
NotificationManager notificationManager = 
    (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
notificationManager.notify(notificationId, builder.build());

┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. Framework 层: NotificationManagerService 处理                          │
└─────────────────────────────────────────────────────────────────────────────┘

NotificationManagerService:
│
├── 接收通知
│   └── mBinderService.enqueueNotificationWithTag()
│
├── 创建 NotificationRecord
│   ├── 解析 Notification 对象
│   ├── 创建 NotificationRecord
│   └── 设置 tag 和 id
│
├── 验证通知
│   ├── 检查权限
│   ├── 检查 AppOps
│   └── 检查 Bundle
│
├── 检查过滤规则
│   ├── App 通知过滤
│   └── 渠道通知过滤
│
├── 检查静默规则
│   ├── 免打扰模式
│   └── 优先级过滤
│
├── 记录统计信息
│   └── NotificationStats
│
└── 准备传递

┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. 投递通知: PostNotificationRunnable                                     │
└─────────────────────────────────────────────────────────────────────────────┘

PostNotificationRunnable.run():
│
├── 将通知加入队列
│   └── mEnqueuedNotifications.add(key, record)
│
├── 检查权限并发布
│   └── mHandler.post(this)
│
├── 执行发布
│   ├── 绑定 NotificationChannel
│   ├── 提取 RemoteViews
│   ├── 提取气泡信息
│   └── 提取 People 路径
│
├── 持久化通知
│   └── 保存到 NotificationStore
│
└── 通知 SystemUI
    └── mSystemUI.onNotificationPosted(key, ranking)

┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. SystemUI 层: 接收并显示通知                                            │
└─────────────────────────────────────────────────────────────────────────────┘

NotificationListenerService.onNotificationPosted():
│
├── NotificationEntryManager.onNotificationPosted()
│   ├── 创建 NotificationEntry
│   ├── 添加到 mNotificationList
│   └── 触发更新回调
│
├── StatusBarNotificationController.onNotificationAdded()
│   ├── 更新状态栏图标
│   ├── 更新通知面板
│   └── 触发视图更新
│
└── NotificationRowPresenter.bindRow()
    ├── 展开通知行
    ├── 设置通知内容
    ├── 设置 RemoteViews
    └── 设置点击事件
```

### 4.3 通知核心组件

```java
/**
 * 通知核心组件
 */

// 1. NotificationRecord - 通知记录
// 位置: frameworks/base/services/core/java/com/android/server/notification/
public class NotificationRecord {
    private final String key;           // 唯一标识: pkg + id + tag
    private final Notification notification; // 原始通知
    private final String channelId;    // 渠道 ID
    private final int userId;          // 用户 ID
    private final long postTime;       // 发布时间
    private final int importance;      // 重要性级别
    private final Ranking ranking;     // 排名信息
    
    // 通知强度 (强度越高，越重要)
    public enum Intensity {
        NO_ALERT,      // 无提醒
        LOW_ALERT,    // 低提醒
        HIGH_ALERT,   // 高提醒
        PRIORITY,     // 优先级
    }
}

// 2. NotificationEntry - 通知条目 (SystemUI)
// 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/statusbar/notification/
public class NotificationEntry {
    private final String mKey;                    // 唯一标识
    private final StatusBarNotification mSbn;    // 系统通知对象
    private Notification mNotification;          // 通知内容
    private Ranking mRanking;                    // 排名
    private ExpandableNotificationRow mRow;      // 通知行视图
    private boolean mIsRemoved;                  // 是否已移除
    private boolean mIsDismissed;                // 是否已消除
    
    // 通知状态
    public enum State {
        DISMISSING,      // 正在消除
        DISMISSED,       // 已消除
        PENDING,         // 等待中
        POSTED,          // 已发布
        REMOVED,         // 已移除
    }
}

// 3. ExpandableNotificationRow - 可展开通知行
public class ExpandableNotificationRow extends FrameLayout {
    private NotificationEntry mEntry;           // 通知数据
    private NotificationContentView mExpanded;  // 展开视图
    private NotificationContentView mCollapsed; // 折叠视图
    private NotificationContentView mHeadsUp;   // 悬浮视图
    private RemoteViews mBigContentView;       // 大视图
    
    // 展开状态
    public enum ExpandState {
        COLLAPSED,      // 折叠
        EXPANDED,       // 展开
        HEADS_UP,       // 悬浮通知
    }
}
```

---

## 5. NotificationManagerService 深入分析

### 5.1 NMS 架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NotificationManagerService 架构                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        System Server 进程                                  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      NotificationManagerService                      │   │
│  │                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │                    核心组件                                    │  │   │
│  │  │                                                              │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │  │   │
│  │  │  │NotificationRecord│ │NotificationList│ │NotificationStore│   │  │   │
│  │  │  │  通知记录     │  │  通知列表    │  │  通知持久化   │    │  │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘    │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │                    管理组件                                    │  │   │
│  │  │                                                              │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │  │   │
│  │  │  │ RankingHelper│ │ConditionHelper│ │ZenModeHelper │    │  │   │
│  │  │  │  排名助手    │  │  条件助手    │  │  勿扰助手     │    │  │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘    │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 NMS 核心流程

```java
/**
 * NotificationManagerService 核心实现
 */

// 1. 服务入口
public class NotificationManagerService extends SystemService {
    
    @Override
    public void onStart() {
        // 发布 Binder 服务
        publishBinderService(Context.NOTIFICATION_SERVICE, mBinderService);
        
        // 初始化组件
        mRankingHelper = new RankingHelper(getContext(), mPm);
        mZenModeHelper = new ZenModeHelper(getContext());
        mConditionHelper = new ConditionHelper(getContext());
        mNotificationList = new NotificationList();
        
        // 注册监听器
        registerListeners();
    }
    
    // Binder 服务实现
    private final IBinder mBinderService = new INotificationManager.Stub() {
        
        @Override
        public void enqueueNotificationWithTag(String pkg, String opPkg, 
                String tag, int id, Notification notification, int userId) {
            
            // 检查权限
            checkCallerIsSystemOrSameApp(pkg);
            
            // 创建 NotificationRecord
            final NotificationRecord r = new NotificationRecord(
                getContext(), notification, pkg, tag, id, userId);
            
            // 排名
            mRankingHelper.extractSignals(r);
            
            // 检查是否应该拦截
            if (isBlocked(r)) {
                return;
            }
            
            // 加入队列
            mEnqueuedNotifications.add(r.getKey(), r);
            
            // 触发投递
            mHandler.post(new PostNotificationRunnable(r.getKey()));
        }
        
        @Override
        public void cancelNotificationWithTag(String pkg, String tag, 
                int id, int userId) {
            
            // 检查权限
            checkCallerIsSystemOrSameApp(pkg);
            
            // 构造 key
            final String key = Notification.keyFor(pkg, id, tag, userId);
            
            // 触发取消
            mHandler.post(new CancelNotificationRunnable(key));
        }
    };
}

// 2. PostNotificationRunnable - 投递通知
private class PostNotificationRunnable implements Runnable {
    
    private final String mKey;
    
    PostNotificationRunnable(String key) {
        mKey = key;
    }
    
    @Override
    public void run() {
        // 获取通知记录
        final NotificationRecord r = mEnqueuedNotifications.get(mKey);
        if (r == null) {
            return;
        }
        
        // 验证通知
        if (!validateNotification(r)) {
            mEnqueuedNotifications.remove(mKey);
            return;
        }
        
        // 应用排名
        mRankingHelper.rank(mNotificationList, r);
        
        // 应用勿扰
        if (mZenModeHelper.shouldIntercept(r)) {
            r.setIntercepted(true);
        }
        
        // 添加到通知列表
        mNotificationList.add(r);
        
        // 保存到持久化存储
        mNotificationStore.add(r);
        
        // 通知监听器
        notifyPosted(r);
        
        // 更新状态栏
        updateStatusBarIcons();
    }
}
```

---

## 6. RemoteViews 深度解析

### 6.1 RemoteViews 原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RemoteViews 原理                                    │
└─────────────────────────────────────────────────────────────────────────────┘

RemoteViews 是一种跨进程的视图机制:

┌─────────────────────────────────────────────────────────────────────────────┐
│                          应用进程                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    RemoteViews 创建                                  │   │
│  │                                                                   │   │
│  │  RemoteViews views = new RemoteViews(pkgName, layoutId);        │   │
│  │  views.setTextViewText(R.id.title, "标题");                       │   │
│  │  views.setImageViewResource(R.id.icon, R.drawable.icon);        │   │
│  │                                                                   │   │
│  │  // 序列化为 Parcel                                               │   │
│  │  Parcel parcel = Parcel.obtain();                               │   │
│  │  views.writeToParcel(parcel, 0);                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                      │
│                                    │ Binder IPC (Parcel)                  │
│                                    ▼                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SystemUI 进程                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    RemoteViews 应用                                  │   │
│  │                                                                   │   │
│  │  // 反序列化                                                      │   │
│  │  RemoteViews views = RemoteViews.CREATOR.createFromParcel(parcel); │   │
│  │                                                                   │   │
│  │  // 应用到 View                                                   │   │
│  │  View view = views.apply(context, parent);                      │   │
│  │  parent.addView(view);                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

核心特点:
1. 跨进程传递视图结构
2. 支持有限的 View 类型
3. 支持有限的操作方法
4. 安全性高 (限制操作范围)
```

### 6.2 RemoteViews 支持的 View

```java
/**
 * RemoteViews 支持的 View 类型
 */

// 布局容器
FrameLayout
LinearLayout
RelativeLayout
GridLayout

// 基础视图
TextView
ImageView
Button
ImageButton
ProgressBar
Chronometer

// 注意: 不支持自定义 View
```

### 6.3 RemoteViews 操作

```java
/**
 * RemoteViews 常用操作
 */

RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.notification);

// 文本操作
views.setTextViewText(R.id.title, "标题");
views.setTextColor(R.id.title, Color.RED);

// 图片操作
views.setImageViewResource(R.id.icon, R.drawable.icon);
views.setImageViewBitmap(R.id.icon, bitmap);

// 点击事件
Intent intent = new Intent(context, TargetActivity.class);
PendingIntent pendingIntent = PendingIntent.getActivity(context, 0, intent, 0);
views.setOnClickPendingIntent(R.id.button, pendingIntent);
```

### 6.4 Actions 机制深度解析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RemoteViews Actions 机制                                 │
│              每个 setXXX 调用的本质：创建一个 Action 对象                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Action 类继承体系 (AOSP: frameworks/base/core/java/android/widget/)        │
│                                              RemoteViews.java              │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │  Action (abstract)   │  ← Parcelable 接口
                    │  getActionTag()      │  ← 用于序列化标识
                    │  apply(View, ...)    │  ← 执行操作的核心方法
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────────┐
          │                    │                        │
          ▼                    ▼                        ▼
┌──────────────────┐ ┌──────────────────┐  ┌──────────────────────┐
│ ReflectionAction │ │ ViewGroupAction  │  │  特殊 Action          │
│ (反射调用方法)    │ │ (添加/移除子View) │  │                      │
└──────────────────┘ └──────────────────┘  ├──────────────────────┤
                                            │ SetEmptyViewAction   │
                                            │ SetPendingIntent     │
                                            │   TemplateAction     │
                                            │ SetOnClickFillIn     │
                                            │   IntentAction       │
                                            │ LayoutParamAction    │
                                            │ TextViewDrawable     │
                                            │   Action             │
                                            │ SetRemoteViews       │
                                            │   AdapterAction      │
                                            │ SetTextViewCompound  │
                                            │   DrawablesAction    │
                                            └──────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ReflectionAction —— 最核心的 Action 子类                                   │
│  几乎所有 setXXX 方法内部都创建 ReflectionAction                            │
└─────────────────────────────────────────────────────────────────────────────┘

private static final class ReflectionAction extends Action {
    int viewId;            // 目标 View 的 ID
    String methodName;     // 要调用的方法名（如 "setText"）
    int type;              // 参数类型标识
    Object value;          // 参数值

    // type 取值（定义在 RemoteViews 中）:
    static final int BOOLEAN       = 1;
    static final int BYTE          = 2;
    static final int SHORT         = 3;
    static final int INT           = 4;
    static final int LONG          = 5;
    static final int FLOAT         = 6;
    static final int DOUBLE        = 7;
    static final int CHAR          = 8;
    static final int STRING        = 9;
    static final int CHAR_SEQUENCE = 10;
    static final int URI           = 11;
    static final int BITMAP        = 12;
    static final int BUNDLE        = 13;
    static final int INTENT        = 14;
    static final int COLOR         = 15;
    static final int ICON          = 16;

    @Override
    public void apply(View root, ViewGroup rootParent, OnClickHandler handler) {
        // 1. 通过 viewId 找到目标 View
        View view = root.findViewById(viewId);
        if (view == null) return;

        // 2. 通过反射调用方法
        Class<?> paramType = getParameterType(type);
        Method method = view.getClass().getMethod(methodName, paramType);
        method.invoke(view, value);
    }
}

┌─────────────────────────────────────────────────────────────────────────────┐
│  setXXX 方法 → Action 的映射关系                                            │
└─────────────────────────────────────────────────────────────────────────────┘

RemoteViews API                          实际创建的 Action
──────────────────────────────────       ──────────────────────────────
setTextViewText(id, text)           →    ReflectionAction(id, "setText",
                                                    CHAR_SEQUENCE, text)
setTextViewTextSize(id, units, size)→    ReflectionAction(id, "setTextSize",
                                                    FLOAT, size)
setTextColor(id, color)             →    ReflectionAction(id, "setTextColor",
                                                    INT, color)
setImageViewResource(id, resId)     →    ReflectionAction(id, "setImageResource",
                                                    INT, resId)
setImageViewBitmap(id, bitmap)      →    ReflectionAction(id, "setImageBitmap",
                                                    BITMAP, bitmap)
setViewVisibility(id, visibility)   →    ReflectionAction(id, "setVisibility",
                                                    INT, visibility)
setBoolean(id, methodName, value)   →    ReflectionAction(id, methodName,
                                                    BOOLEAN, value)
setInt(id, methodName, value)       →    ReflectionAction(id, methodName,
                                                    INT, value)
setLong(id, methodName, value)      →    ReflectionAction(id, methodName,
                                                    LONG, value)
setDouble(id, methodName, value)    →    ReflectionAction(id, methodName,
                                                    DOUBLE, value)
setCharSequence(id, method, value)  →    ReflectionAction(id, methodName,
                                                    CHAR_SEQUENCE, value)
setOnClickPendingIntent(id, pi)     →    SetOnClickPendingIntentAction
setProgressBar(id, max, prog, ind)  →    SetProgressBarAction
setViewPadding(id, l, t, r, b)     →    ViewPaddingAction
addView(id, childRemoteViews)       →    ViewGroupAction (内嵌 RemoteViews)
removeAllViews(id)                  →    ViewGroupAction (清空子 View)
setRemoteAdapter(id, intent)        →    SetRemoteViewsAdapterIntent

┌─────────────────────────────────────────────────────────────────────────────┐
│  Action 的序列化与反序列化流程                                               │
└─────────────────────────────────────────────────────────────────────────────┘

序列化 (应用进程 — writeToParcel):
┌─────────────────────────────────────────────────────────────────┐
│  Parcel 数据布局:                                                │
│  ┌──────────┬──────────┬──────────┬──────────────────────────┐ │
│  │ mPackage │ mLayoutId│ count    │ Action[0]                │ │
│  │ (String) │ (int)    │ (int)    │ ┌─────────┬────────────┐ │ │
│  │          │          │          │ │ tag(int)│ data(...)  │ │ │
│  │          │          │          │ └─────────┴────────────┘ │ │
│  │          │          │          │ Action[1]                │ │
│  │          │          │          │ ┌─────────┬────────────┐ │ │
│  │          │          │          │ │ tag(int)│ data(...)  │ │ │
│  │          │          │          │ └─────────┴────────────┘ │ │
│  │          │          │          │ ...                      │ │
│  └──────────┴──────────┴──────────┴──────────────────────────┘ │
│                                                                  │
│  ReflectionAction 序列化:                                        │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐      │
│  │ TAG(1)   │ viewId   │methodName│ type     │ value    │      │
│  │ (int)    │ (int)    │ (String) │ (int)    │ (varies) │      │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘      │
└─────────────────────────────────────────────────────────────────┘

反序列化 (SystemUI 进程 — CREATOR.createFromParcel):
┌─────────────────────────────────────────────────────────────────┐
│  RemoteViews.CREATOR.createFromParcel(parcel):                  │
│                                                                  │
│  1. 读取 mPackage, mLayoutId                                    │
│  2. 创建 RemoteViews 对象                                        │
│  3. 读取 Action 数量                                             │
│  4. for 每个 Action:                                             │
│     ├── parcel.readInt() → actionTag                            │
│     ├── 根据 actionTag 创建对应 Action 实例                      │
│     │   (TAG = 1 → ReflectionAction                             │
│     │    TAG = 2 → SetOnClickPendingIntentAction                │
│     │    TAG = 3 → ReflectionActionWithoutParams                │
│     │    TAG = 4 → SetEmptyView  ...等等)                       │
│     ├── action.readFromParcel(parcel)                           │
│     └── mActions.add(action)                                    │
│  5. 返回完整的 RemoteViews                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  apply() 时执行所有 Actions                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

public View apply(Context context, ViewGroup parent, OnClickHandler handler) {
    // 1. 使用过滤后的 LayoutInflater 加载布局
    View result = inflateView(context, parent);   // ← 只能创建白名单 View

    // 2. 依次执行所有 Action
    performApply(result, parent, handler);
    return result;
}

private void performApply(View root, ViewGroup rootParent, OnClickHandler handler) {
    if (mActions != null) {
        for (int i = 0; i < mActions.size(); i++) {
            Action a = mActions.get(i);
            a.apply(root, rootParent, handler);   // ← 每个Action各自apply
        }
    }
}

// 以 ReflectionAction.apply() 为例:
@Override
public void apply(View root, ViewGroup rootParent, OnClickHandler handler) {
    View target = root.findViewById(viewId);
    if (target == null) return;

    Class<?> argType = PARAM_TYPES[type];          // 根据 type 获取参数类型
    Method method = target.getClass().getMethod(    // 反射获取方法
        methodName, argType);
    method.invoke(target, value);                   // 反射调用
}

// 关键：method.invoke() 在 SystemUI 进程执行
// 应用进程只负责"记录操作"，SystemUI 进程负责"执行操作"
// 这就是 RemoteViews 跨进程的本质

┌─────────────────────────────────────────────────────────────────────────────┐
│  为什么用 Action 列表而不是直接序列化 View？                                  │
└─────────────────────────────────────────────────────────────────────────────┘

方案对比:

方案 A：直接序列化 View 对象                         ❌ 不可行
├── View 有大量内部状态（Context、Window、Handler...）
├── 很多字段不可序列化（Canvas、native 指针）
├── 反序列化后 Context 丢失，View 无法正常工作
└── 跨进程安全性无法保证

方案 B：序列化布局 ID + 操作列表 (Action)             ✅ 实际方案
├── 只记录"做什么"，不记录"怎么做"
├── 在目标进程重新创建 View 并回放操作
├── Action 是简单的数据类，容易序列化
└── 目标进程拥有完整 Context，View 可以正常工作

这就是 RemoteViews 的设计哲学：
  应用进程：录制操作（布局 ID + Action 列表）
  SystemUI 进程：回放操作（inflate 布局 + 执行 Action）
```

### 6.5 反射创建与 View 白名单机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              RemoteViews 反射创建与 View 白名单机制                          │
│         为什么 RemoteViews 只能使用特定 View？如何实现的？                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. LayoutInflater 的过滤机制                                                │
│     (AOSP: frameworks/base/core/java/android/widget/RemoteViews.java)       │
└─────────────────────────────────────────────────────────────────────────────┘

RemoteViews.apply() 加载布局时，不是直接使用普通 LayoutInflater，
而是通过 RemoteViews.Context 的 inflate() 方法配合过滤机制:

private View inflateView(Context context, ViewGroup parent) {
    // 使用 RemoteViews 自己的 LayoutInflater
    LayoutInflater inflater = LayoutInflater.from(context).cloneInContext(context);
    inflater.setFilter(sLayoutInflaterFilter);   // ← 关键：设置过滤器
    return inflater.inflate(mLayoutId, parent, false);
}

// LayoutInflater.Filter 接口
public interface Filter {
    boolean onLoadClass(ClassLoader loader, String className);
    // 返回 true → 允许加载该 View
    // 返回 false → 拒绝加载，抛出异常
}

┌─────────────────────────────────────────────────────────────────────────────┐
│  2. View 白名单的实现                                                       │
│     sLayoutInflaterFilter 实际上是一个白名单检查器                            │
└─────────────────────────────────────────────────────────────────────────────┘

// AOSP 中的白名单定义 (简化展示)
private static final LayoutInflater.Filter sLayoutInflaterFilter =
    (loader, className) -> {
        // 检查类名是否在允许列表中
        // 白名单在 RemoteViews 初始化时通过静态注册
        return isAllowedViewClass(className);
    };

// AOSP 中实际的白名单注册方式:
// 通过内部数组定义所有允许的 View 类名
private static final String[] sAllowedViewClasses = {
    // ──── 布局容器 ────
    "android.widget.FrameLayout",
    "android.widget.LinearLayout",
    "android.widget.RelativeLayout",
    "android.widget.GridLayout",
    "android.widget.GridLayout$LayoutParams",

    // ──── 基础视图 ────
    "android.widget.TextView",
    "android.widget.ImageView",
    "android.widget.Button",
    "android.widget.ImageButton",
    "android.widget.ProgressBar",
    "android.widget.Chronometer",

    // ──── 高级视图 ────
    "android.widget.ViewFlipper",
    "android.widget.StackView",
    "android.widget.AdapterViewFlipper",
    "android.widget.ListView",
    "android.widget.GridView",

    // ──── 特殊视图 ────
    "android.widget.AnalogClock",
    "android.widget.TextClock",
    "android.view.View",
    "android.view.ViewGroup",
    "android.widget.RemoteViews.RemoteView",  // 注解标记
};

// Android 12+ 还支持通过 @RemoteView 注解自动注册:
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface RemoteView {
    // 标注了此注解的 View 自动加入白名单
}

// 例如:
@RemoteView
public class TextView extends View { ... }

@RemoteView
public class ImageView extends View { ... }

┌─────────────────────────────────────────────────────────────────────────────┐
│  3. 反射创建 View 的完整流程                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

LayoutInflater.inflate() 内部创建 View 的过程:

┌──────────────────────────────────────────────────────────────────────────┐
│  LayoutInflater.createViewFromTag()                                       │
│                                                                          │
│  1. 解析 XML 标签名 → className (如 "TextView")                          │
│                    ↓                                                     │
│  2. 调用 mFilter.onLoadClass(loader, className)                          │
│     ├── 返回 true  → 继续创建 View                                      │
│     └── 返回 false → 抛出 InflateException                              │
│                    ↓ (白名单通过)                                         │
│  3. createView(className, ...) → 反射创建                                │
│     ├── Class<?> clazz = loader.loadClass(fullClassName)                 │
│     ├── Constructor<?> constructor = clazz.getConstructor(               │
│     │       Context.class, AttributeSet.class)                           │
│     └── return constructor.newInstance(context, attrs)                   │
│                    ↓                                                     │
│  4. 返回 View 实例                                                        │
└──────────────────────────────────────────────────────────────────────────┘

实际代码调用链:
RemoteViews.apply(context, parent)
    └── inflateView(context, parent)
        └── LayoutInflater.inflate(layoutId, parent, false)
            └── rInflateChildren(parser, root, attrs, true)
                └── createViewFromTag(view, name, context, attrs)
                    ├── mFilter.onLoadClass(...)     // 白名单检查
                    └── createView(name, "...")       // 反射创建

┌─────────────────────────────────────────────────────────────────────────────┐
│  4. 安全限制的三层防线                                                       │
└─────────────────────────────────────────────────────────────────────────────┘

防线 1：布局加载时的 View 白名单过滤
├── LayoutInflater.Filter 拦截非法 View 类
├── 只允许白名单中的 View 被实例化
└── 即使 XML 中写了 <com.evil.CustomView> 也会被拒绝

防线 2：ReflectionAction 的方法调用限制
├── 只能调用预定义的方法名（setText, setVisibility 等）
├── 不能调用任意方法（方法名来自 API，不是来自 Parcel）
├── 参数类型由 type 字段限定，不能伪造
└── 实际上 ReflectionAction 的 methodName 只能是 SDK 中定义的名称

防线 3：资源加载的包名隔离
├── RemoteViews 中的 mPackage 决定了资源加载的来源
├── SystemUI 使用应用的 Context 加载布局资源
├── 但 View 类始终从 Framework (android.widget.*) 加载
└── 应用的自定义 View 类不会在 SystemUI 进程中加载

┌─────────────────────────────────────────────────────────────────────────────┐
│  5. 为什么不支持自定义 View？—— 完整技术分析                                 │
└─────────────────────────────────────────────────────────────────────────────┘

原因 1: 进程隔离与类加载器不匹配
├── 自定义 View 的 Class 文件在应用 APK 中
├── SystemUI 进程的 ClassLoader 无法加载应用的类
├── 即使加载了，Context、Resources 等依赖不匹配
└── 这是最根本的技术障碍

原因 2: 安全风险
├── 自定义 View 可在构造函数/draw 中执行任意代码
├── SystemUI 以 system uid 运行，权限极高
├── 恶意应用可通过自定义 View 在 SystemUI 中执行特权操作
└── 白名单机制确保只有 Google 审核过的 View 可以使用

原因 3: 序列化限制
├── 自定义 View 可能有复杂的内部状态
├── 这些状态难以通过 Parcel 传递
├── 反序列化后状态恢复不完整会导致异常
└── Action 机制只能操作属性，无法传递 View 的行为逻辑

原因 4: 兼容性与稳定性
├── 不同应用的 View 实现可能依赖不同的 API 版本
├── SystemUI 进程中的 View 可能与应用进程的版本不一致
├── 应用更新后 View 行为变化可能导致 SystemUI 崩溃
└── 白名单保证 SystemUI 不受第三方应用代码质量影响

┌─────────────────────────────────────────────────────────────────────────────┐
│  6. RemoteViews 反射机制的类图                                              │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌───────────────────┐
                        │   RemoteViews     │
                        │───────────────────│
                        │ mPackage: String  │
                        │ mLayoutId: int    │
                        │ mActions: ArrayList│
                        │ mBitmapCache      │
                        │───────────────────│
                        │ + apply()         │
                        │ + reapply()       │
                        │ + setXXX()        │
                        └───────┬───────────┘
                                │ 持有
                                ▼
                ┌───────────────────────────┐
                │   Action (abstract)       │
                │───────────────────────────│
                │ + getActionTag(): int     │
                │ + apply(View, ViewGroup,  │
                │     OnClickHandler)       │
                │ + writeToParcel()         │
                └───────┬───────────────────┘
                        │
        ┌───────────────┼───────────────────┐
        │               │                   │
        ▼               ▼                   ▼
┌───────────────┐ ┌──────────────┐ ┌────────────────────┐
│ReflectionAction│ │ViewGroupAction│ │SetOnClickPending  │
│───────────────│ │──────────────│ │  IntentAction      │
│viewId: int   │ │mViews:       │ │────────────────────│
│methodName:   │ │ RemoteViews[]│ │viewId: int         │
│ String       │ │──────────────│ │pendingIntent:      │
│type: int     │ │apply() →     │ │ PendingIntent      │
│value: Object │ │ addView()    │ │────────────────────│
│───────────────│ │ /removeView()│ │apply() →           │
│apply() →     │ └──────────────┘ │ setOnClickListener │
│ 反射调用方法  │                  │  + PendingIntent   │
└───────────────┘                  └────────────────────┘
        │
        │ 反射调用原理:
        │
        │ Method m = view.getClass()
        │     .getMethod(methodName, paramType);
        │ m.invoke(view, value);
        │
        │ 例如: setTextViewText(id, "hello")
        │   → methodName = "setText"
        │   → paramType  = CharSequence.class
        │   → value      = "hello"
        │
        │ 最终在 SystemUI 进程执行:
        │   textView.setText("hello");

┌─────────────────────────────────────────────────────────────────────────────┐
│  7. apply() vs reapply() 的区别                                             │
└─────────────────────────────────────────────────────────────────────────────┘

apply():
├── 重新 inflate 布局 + 执行所有 Action
├── 创建全新的 View 树
├── 开销大，适合首次加载
└── 返回新创建的 View

reapply():
├── 不重新 inflate，只执行 Action
├── 在已有的 View 上重新应用操作
├── 开销小，适合通知内容更新
└── 不返回 View（使用已有的）

// SystemUI 中的典型用法:
// 首次加载通知
View view = remoteViews.apply(context, parent);
parent.addView(view);

// 通知内容更新时
remoteViews.reapply(context, existingView);
// 不需要 remove → add，直接在原有 View 上刷新

这就是为什么通知更新比首次显示快的原因。
```

---

## 7. SystemUI 与 Framework 协作

### 7.1 通知协作流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SystemUI 与 Framework 协作                              │
└─────────────────────────────────────────────────────────────────────────────┘

应用进程:
├── NotificationManager.notify()
└── Binder IPC → NMS

NMS (system_server):
├── 创建 NotificationRecord
├── 排名和过滤
├── 持久化
└── 回调 SystemUI

SystemUI:
├── NotificationListenerService.onNotificationPosted()
├── 创建 NotificationEntry
├── 提取 RemoteViews
├── 渲染通知视图
└── 更新状态栏图标
```

---

## 8. 通知渲染流程

### 8.1 渲染架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       通知渲染架构                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      NotificationPanelView (通知面板)                      │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                NotificationStackScrollLayout                         │   │
│  │                    (通知滚动列表)                                      │   │
│  │                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │              ExpandableNotificationRow (1)                  │  │   │
│  │  │  ┌───────────────────────────────────────────────────────┐ │  │   │
│  │  │  │              NotificationContentView                    │ │  │   │
│  │  │  │  ┌─────────────────────────────────────────────────┐ │ │  │   │
│  │  │  │  │  RemoteViews.apply() → View Hierarchy        │ │ │  │   │
│  │  │  │  │                                                 │ │  │   │
│  │  │  │  │  ┌─────┐ ┌─────────────────────────────────┐ │ │  │   │
│  │  │  │  │  │Icon │ │Title: 新消息                   │ │ │  │   │
│  │  │  │  │  └─────┘ │Content: 你有新的消息            │ │ │  │   │
│  │  │  │  │          │Time: 10:30                      │ │ │  │   │
│  │  │  │  │          └─────────────────────────────────┘ │ │  │   │
│  │  │  │  └─────────────────────────────────────────────────┘ │ │  │   │
│  │  │  └───────────────────────────────────────────────────────┘ │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │              ExpandableNotificationRow (2)                  │  │   │
│  │  │              (另一条通知...)                                 │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 渲染流程详解

```java
/**
 * 通知渲染流程
 */

// 1. 接收通知
NotificationListenerService.onNotificationPosted(sbn, rankingMap):
│
├── 提取 StatusBarNotification
│   ├── Notification notification = sbn.getNotification()
│   └── String key = sbn.getKey()
│
└── 通知 NotificationEntryManager
    └── onNotificationPosted(sbn, rankingMap)

// 2. 创建通知条目
NotificationEntryManager.onNotificationPosted(sbn, rankingMap):
│
├── 创建 NotificationEntry
│   └── entry = new NotificationEntry(sbn)
│
├── 应用排名
│   └── mRankingManager.extractSignals(entry)
│
├── 添加到列表
│   └── mNotificationList.add(entry)
│
└── 触发更新
    └── mCallback.onNotificationAdded(entry)

// 3. 创建通知视图
NotificationRowBinderImpl.bindRow(entry, row):
│
├── 获取 RemoteViews
│   ├── RemoteViews contentView = notification.contentView
│   ├── RemoteViews bigContentView = notification.bigContentView
│   └── RemoteViews headsUpContentView = notification.headsUpContentView
│
├── 应用 RemoteViews
│   ├── row.setContentView(contentView)
│   ├── row.setBigContentView(bigContentView)
│   └── row.setHeadsUpView(headsUpContentView)
│
├── 设置展开状态
│   └── row.setExpanded(isExpanded)
│
└── 添加到列表
    └── mStackScrollLayout.addNotificationRow(row)

// 4. 渲染通知内容
NotificationContentView.setContent(RemoteViews views):
│
├── 清空现有视图
│   └── removeAllViews()
│
├── 应用 RemoteViews
│   └── View view = views.apply(mContext, this)
│
├── 添加到容器
│   └── addView(view)
│
└── 触发布局
    └── requestLayout()
```

---

## 9. 通知模板系统

### 9.1 通知模板类型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       通知模板类型                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────────────────┐
│      模板        │                       说明                              │
├──────────────────┼──────────────────────────────────────────────────────────┤
│  BigTextStyle    │  长文本通知，展开显示完整内容                            │
│  BigPictureStyle │  大图片通知，展开显示大图                                │
│  InboxStyle      │  收件箱通知，显示多行消息列表                            │
│  MessagingStyle  │  消息通知，显示对话内容                                  │
│  MediaStyle      │  媒体通知，显示播放控制                                  │
│  DecoratedCustom │  自定义通知，带系统装饰                                  │
│  CallStyle       │  来电通知，显示通话控制                                  │
└──────────────────┴──────────────────────────────────────────────────────────┘

模板布局结构:
┌─────────────────────────────────────────────────────────────────────────────┐
│  BigTextStyle (长文本)                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────┐ Title                                                      │   │
│  │  │Icon │ Content...                                                │   │
│  │  └─────┘ [展开后显示完整长文本内容...]                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  BigPictureStyle (大图片)                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────┐ Title                                                      │   │
│  │  │Icon │ Content                                                    │   │
│  │  └─────┘                                                            │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                    [大图片]                                    │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  MessagingStyle (消息)                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────┐ 对话标题                                                   │   │
│  │  │Icon │                                                            │   │
│  │  └─────┘                                                            │   │
│  │  User1: 消息1                                                       │   │
│  │  User2: 消息2                                                       │   │
│  │  User1: 消息3                                                       │   │
│  │  [输入框] [发送按钮]                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  MediaStyle (媒体)                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ┌────────┐ 歌曲标题                                                │   │
│  │  │ 专辑封面│ 歌手名                                                  │   │
│  │  │        │ 专辑名                                                  │   │
│  │  └────────┘                                                         │   │
│  │  [上一曲] [播放/暂停] [下一曲]                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  CallStyle (来电)                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ┌────────┐ 来电                                                    │   │
│  │  │ 头像   │ 张三                                                    │   │
│  │  │        │ +86 138****1234                                         │   │
│  │  └────────┘                                                         │   │
│  │  [挂断]                    [接听]                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 模板使用示例

```java
/**
 * 通知模板使用示例
 */

// 1. BigTextStyle - 长文本
NotificationCompat.Builder builder = new NotificationCompat.Builder(context, channelId)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("新消息")
    .setContentText("内容预览")
    .setStyle(new NotificationCompat.BigTextStyle()
        .bigText("这是一段很长的文本内容，在折叠状态下只显示预览，" +
                "展开后显示完整内容...")
        .setBigContentTitle("展开标题")
        .setSummaryText("摘要"));

// 2. BigPictureStyle - 大图片
NotificationCompat.Builder builder = new NotificationCompat.Builder(context, channelId)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("图片分享")
    .setContentText("点击查看大图")
    .setStyle(new NotificationCompat.BigPictureStyle()
        .bigPicture(bitmap)
        .bigLargeIcon(null)  // 展开时隐藏大图标
        .setBigContentTitle("展开标题")
        .setSummaryText("图片描述"));

// 3. InboxStyle - 收件箱
NotificationCompat.Builder builder = new NotificationCompat.Builder(context, channelId)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("新邮件")
    .setContentText("3 封未读邮件")
    .setStyle(new NotificationCompat.InboxStyle()
        .setBigContentTitle("收件箱")
        .setSummaryText("3 封未读")
        .addLine("邮件1: 标题...")
        .addLine("邮件2: 标题...")
        .addLine("邮件3: 标题..."));

// 4. MessagingStyle - 消息对话
Person user1 = new Person.Builder()
    .setName("张三")
    .setIcon(iconBitmap)
    .build();
    
Person user2 = new Person.Builder()
    .setName("李四")
    .build();

NotificationCompat.MessagingStyle style = new NotificationCompat.MessagingStyle("我")
    .addMessage(new NotificationCompat.MessagingStyle.Message(
        "你好", System.currentTimeMillis(), user1))
    .addMessage(new NotificationCompat.MessagingStyle.Message(
        "在吗？", System.currentTimeMillis() + 1000, user2))
    .addMessage(new NotificationCompat.MessagingStyle.Message(
        "在的", System.currentTimeMillis() + 2000, user1));

NotificationCompat.Builder builder = new NotificationCompat.Builder(context, channelId)
    .setSmallIcon(R.drawable.icon)
    .setStyle(style);

// 5. MediaStyle - 媒体控制
NotificationCompat.Builder builder = new NotificationCompat.Builder(context, channelId)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("正在播放")
    .setContentText("歌曲名 - 歌手")
    .setStyle(new androidx.media.app.NotificationCompat.MediaStyle()
        .setMediaSession(mediaSession.getSessionToken())
        .setShowActionsInCompactView(0, 1, 2))  // 显示哪些按钮
    .addAction(R.drawable.prev, "上一曲", prevPendingIntent)
    .addAction(R.drawable.pause, "暂停", pausePendingIntent)
    .addAction(R.drawable.next, "下一曲", nextPendingIntent);

// 6. CallStyle - 来电通知 (Android 11+)
Person caller = new Person.Builder()
    .setName("张三")
    .setIcon(iconBitmap)
    .setImportant(true)
    .build();

NotificationCompat.CallStyle style = NotificationCompat.CallStyle.forIncomingCall(
    caller,
    declinePendingIntent,
    answerPendingIntent
);

NotificationCompat.Builder builder = new NotificationCompat.Builder(context, channelId)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("来电")
    .setContentText("张三")
    .setStyle(style)
    .setFullScreenIntent(fullScreenPendingIntent, true);  // 全屏显示
```

### 9.3 模板底层实现

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    通知模板底层实现                                        │
└─────────────────────────────────────────────────────────────────────────────┘

模板的本质：预定义的 RemoteViews 布局

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. 模板生成 RemoteViews                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

// Notification.Builder.build() 时，Style 会生成 RemoteViews

public Notification build() {
    // ...
    
    // 如果设置了 Style，让 Style 填充 RemoteViews
    if (mStyle != null) {
        mStyle.addExtras(mExtras);
        mStyle.populateContentView(this);  // 填充折叠视图
        mStyle.populateBigContentView(this);  // 填充展开视图
        mStyle.populateHeadsUpContentView(this);  // 填充悬浮视图
    }
    
    // ...
}

// BigTextStyle 的实现
public class BigTextStyle extends Style {
    @Override
    public void populateBigContentView(Builder builder) {
        // 创建展开视图的 RemoteViews
        RemoteViews bigContentView = new RemoteViews(
            builder.mContext.getPackageName(),
            R.layout.notification_template_big_text
        );
        
        // 填充内容
        bigContentView.setTextViewText(R.id.title, mBigContentTitle);
        bigContentView.setTextViewText(R.id.big_text, mBigText);
        bigContentView.setTextViewText(R.id.text, mSummaryText);
        
        // 设置到 Notification
        builder.setCustomBigContentView(bigContentView);
    }
}

┌─────────────────────────────────────────────────────────────────────────────┐
│  2. 模板布局文件                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

// frameworks/base/core/res/res/layout/notification_template_big_text.xml

<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content">
    
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical">
        
        <!-- 标题 -->
        <TextView android:id="@+id/title"
            android:layout_width="match_parent"
            android:layout_height="wrap_content" />
        
        <!-- 大文本内容 -->
        <TextView android:id="@+id/big_text"
            android:layout_width="match_parent"
            android:layout_height="wrap_content" />
        
        <!-- 摘要 -->
        <TextView android:id="@+id/text"
            android:layout_width="match_parent"
            android:layout_height="wrap_content" />
    
    </LinearLayout>

</FrameLayout>

┌─────────────────────────────────────────────────────────────────────────────┐
│  3. SystemUI 渲染模板                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

// SystemUI 收到通知后，使用 RemoteViews.apply() 加载模板布局

ExpandableNotificationRow.bindNotification():
│
├── 获取 RemoteViews
│   RemoteViews bigContentView = notification.bigContentView;
│
├── 应用到视图
│   NotificationContentView contentView = getExpandedView();
│   contentView.setContent(bigContentView);
│
└── RemoteViews.apply()
    // 加载模板布局
    View view = inflater.inflate(R.layout.notification_template_big_text, parent, false);
    
    // 执行所有 Action
    for (Action action : mActions) {
        action.apply(view, parent, handler);
    }
```

---

## 10. 面试常见问题

### 10.1 SystemUI 基础

**Q1: SystemUI 是什么？包含哪些组件？**

**A:**

SystemUI 是 Android 系统的核心 UI 组件，运行在 system_server 进程中：

核心组件：
- StatusBar：状态栏
- NavigationBar：导航栏
- NotificationPanel：通知面板
- Keyguard：锁屏
- AOD：息屏显示
- PowerMenu：电源菜单
- Recents：最近任务
- VolumeUI：音量条

### 10.2 AOD

**Q2: AOD (Always On Display) 是如何实现的？**

**A:**

```
AOD 实现机制：

1. 硬件支持
   - AMOLED 屏幕（可单独点亮像素）
   - Display HAL 支持 AOD 模式

2. 软件架构
   - DozeService：管理 Doze 状态
   - DozeMachine：状态机控制
   - AODView：AOD 显示内容

3. 状态流转 (Android 16)
   UNINITIALIZED → INITIALIZED → DOZE_AOD → DOZE_PULSING → DOZE_PULSE_DONE → FINISH

4. 显示内容
   - 时钟（防烧屏移动）
   - 通知图标
   - 通知预览

5. 功耗优化
   - 低刷新率（1fps）
   - 部分像素点亮
   - 定时脉冲更新
```

### 10.3 通知系统

**Q3: 通知的发送和显示流程？**

**A:**

```
通知流程：

1. 应用层
   NotificationManager.notify()
   ↓
2. Framework 层 (NMS)
   - 创建 NotificationRecord
   - 排名和过滤
   - 持久化
   ↓
3. Binder IPC
   - 回调 NotificationListenerService
   ↓
4. SystemUI 层
   - NotificationEntryManager 处理
   - 创建 NotificationEntry
   - 提取 RemoteViews
   - 渲染通知视图
```

**Q4: RemoteViews 的原理？**

**A:**

```
RemoteViews 原理：

1. 定义
   - 跨进程视图机制
   - 序列化视图操作

2. 支持的 View
   - 基础：TextView, ImageView, Button
   - 容器：FrameLayout, LinearLayout
   - 不支持：自定义 View

3. 工作流程
   应用进程：
   - 创建 RemoteViews
   - 调用 setXXX 方法（记录 Action）
   - 序列化为 Parcel
   
   SystemUI 进程：
   - 反序列化 RemoteViews
   - 调用 apply() 创建 View
   - 执行所有 Action

4. Action 列表
   - SetTextAction
   - SetImageResourceAction
   - SetOnClickPendingIntentAction
   - ...
```

**Q5: 通知是如何排名的？**

**A:**

```
通知排名因素：

1. 重要性级别 (IMPORTANCE_HIGH > DEFAULT > LOW)
2. 通知渠道优先级
3. 通知类别 (CALL > MESSAGE > OTHER)
4. 通知时间
5. 用户设置
6. 通知频次

排名算法：
1. 按重要性分组
2. 同组按类别排序
3. 同类别按时间排序
```

**Q6: 通知模板是如何工作的？**

**A:**

```
通知模板工作原理：

1. 模板本质
   - 预定义的 RemoteViews 布局
   - Style 类负责填充内容

2. 使用流程
   - 创建 Style (BigTextStyle, MessagingStyle 等)
   - 设置内容
   - Notification.Builder.build() 时生成 RemoteViews

3. 渲染流程
   - SystemUI 收到 RemoteViews
   - RemoteViews.apply() 加载模板布局
   - 执行 Action 填充内容
```

---

## 11. NotificationManagerService 高级特性

> 本节内容基于 Android 16 (API 36) AOSP 源码分析
> 源码路径：frameworks/base/services/core/java/com/android/server/notification/

### 11.1 NMS 核心数据结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NotificationManagerService 源码结构                     │
└─────────────────────────────────────────────────────────────────────────────┘

// 位置：frameworks/base/services/core/java/com/android/server/notification/

NotificationManagerService.java
├── 内部类
│   ├── NotificationRecord        // 通知记录
│   ├── NotificationList          // 通知列表
│   ├── PostNotificationRunnable  // 发布通知
│   ├── CancelNotificationRunnable // 取消通知
│   ├── NotificationRankingUpdate  // 排名更新
│   └── ManagedServiceInfo         // 托管服务信息
│
├── 核心组件
│   ├── RankingHelper            // 排名助手
│   ├── ZenModeHelper            // 勿扰模式
│   ├── NotificationUsageStats   // 使用统计
│   ├── NotificationHistoryManager // 历史记录
│   ├── BubbleController         // 气泡控制
│   └── ConditionalNotificationCenter // 条件通知
│
└── Binder 服务
    ├── INotificationManager.Stub  // 通知管理接口
    └── NotificationManagerInternal // 内部接口
```

```java
/**
 * NotificationManagerService 核心源码
 */

public class NotificationManagerService extends SystemService {
    
    // 通知列表（按用户分组）
    private final ArrayMap<Integer, NotificationList> mNotificationLists = new ArrayMap<>();
    
    // 排名助手
    private RankingHelper mRankingHelper;
    
    // 勿扰模式
    private ZenModeHelper mZenModeHelper;
    
    // 条件助手
    private ConditionProviders mConditionProviders;
    
    // 通知监听器列表
    private final ArraySet<ManagedServiceInfo> mListeners = new ArraySet<>();
    
    // 通知助手列表
    private final ArraySet<ManagedServiceInfo> mAssistants = new ArraySet<>();
    
    // 通知分组
    private final ArrayMap<String, NotificationGroup> mNotificationGroups = new ArrayMap<>();
    
    @Override
    public void onStart() {
        // 1. 发布 Binder 服务
        publishBinderService(Context.NOTIFICATION_SERVICE, mService);
        publishLocalService(NotificationManagerInternal.class, mInternalService);
        
        // 2. 初始化组件
        mRankingHelper = new RankingHelper(getContext(), mPm);
        mZenModeHelper = new ZenModeHelper(getContext(), mHandler);
        mConditionProviders = new ConditionProviders(getContext(), mUserProfiles);
        mUsageStats = new NotificationUsageStats(getContext());
        mHistoryManager = new NotificationHistoryManager(getContext());
        mBubbleController = new BubbleController(getContext());
        
        // 3. 注册监听器
        mListeners.register(mListener);
        
        // 4. 启动线程
        mHandlerThread.start();
        mHandler = new WorkerHandler(mHandlerThread.getLooper());
    }
    
    /**
     * Binder 服务实现
     */
    private final INotificationManager.Stub mService = new INotificationManager.Stub() {
        
        @Override
        public void enqueueNotificationWithTag(String pkg, String opPkg,
                String tag, int id, Notification notification, int userId) {
            
            // 检查权限
            checkCallerIsSystemOrSameApp(pkg);
            
            // 检查通知限制
            checkEnqueueNotificationRateLimit(pkg, userId);
            
            // 检查通知数量限制
            if (isNotificationLimitReached(pkg, userId)) {
                Slog.w(TAG, "Package " + pkg + " has reached notification limit");
                return;
            }
            
            // 创建 NotificationRecord
            final NotificationRecord r = new NotificationRecord(
                getContext(), notification, pkg, tag, id, userId);
            
            // 提取排名信号
            mRankingHelper.extractSignals(r);
            
            // 检查是否被拦截
            if (isBlocked(r)) {
                Slog.d(TAG, "Notification blocked: " + r.getKey());
                return;
            }
            
            // 加入队列
            mHandler.post(new EnqueueNotificationRunnable(userId, r));
        }
        
        @Override
        public void cancelNotificationWithTag(String pkg, String tag,
                int id, int userId) {
            
            checkCallerIsSystemOrSameApp(pkg);
            
            final String key = Notification.keyFor(pkg, id, tag, userId);
            mHandler.post(new CancelNotificationRunnable(key, userId));
        }
        
        @Override
        public void cancelAllNotifications(String pkg, int userId) {
            checkCallerIsSystemOrSameApp(pkg);
            mHandler.post(new CancelAllNotificationsRunnable(pkg, userId));
        }
        
        @Override
        public void setNotificationsEnabledForPackage(String pkg, int uid, 
                boolean enabled) {
            checkCallerIsSystem();
            mPreferencesHelper.setNotificationsEnabledForPackage(pkg, uid, enabled);
        }
        
        @Override
        public NotificationChannel getNotificationChannel(String pkg, 
                String channelId) {
            checkCallerIsSystemOrSameApp(pkg);
            return mPreferencesHelper.getNotificationChannel(pkg, channelId);
        }
        
        @Override
        public List<NotificationChannel> getNotificationChannels(String pkg) {
            checkCallerIsSystemOrSameApp(pkg);
            return mPreferencesHelper.getNotificationChannels(pkg);
        }
        
        @Override
        public void createNotificationChannels(String pkg, 
                ParceledListSlice channels) {
            checkCallerIsSystemOrSameApp(pkg);
            mPreferencesHelper.createNotificationChannels(pkg, channels.getList());
        }
    };
    
    /**
     * 入队通知 Runnable
     */
    private class EnqueueNotificationRunnable implements Runnable {
        private final int mUserId;
        private final NotificationRecord mRecord;
        
        EnqueueNotificationRunnable(int userId, NotificationRecord record) {
            mUserId = userId;
            mRecord = record;
        }
        
        @Override
        public void run() {
            final NotificationRecord r = mRecord;
            final String key = r.getKey();
            
            // 1. 获取通知列表
            NotificationList list = mNotificationLists.get(mUserId);
            if (list == null) {
                list = new NotificationList();
                mNotificationLists.put(mUserId, list);
            }
            
            // 2. 移除旧通知（如果存在）
            NotificationRecord old = list.get(key);
            if (old != null) {
                list.remove(key);
                mUsageStats.unregisterCancelled(old);
            }
            
            // 3. 验证通知
            if (!validateNotification(r)) {
                Slog.e(TAG, "Invalid notification: " + key);
                return;
            }
            
            // 4. 应用排名
            mRankingHelper.rank(list, r);
            
            // 5. 应用勿扰
            if (mZenModeHelper.shouldIntercept(r)) {
                r.setIntercepted(true);
                mUsageStats.registerBlocked(r);
            }
            
            // 6. 添加到列表
            list.add(r);
            
            // 7. 保存到历史
            mHistoryManager.addNotification(r);
            
            // 8. 更新气泡
            mBubbleController.updateBubble(r);
            
            // 9. 通知监听器
            notifyPosted(r, old);
            
            // 10. 更新状态栏
            updateStatusBarIcons();
            
            // 11. 发送声音和振动
            if (!r.isIntercepted()) {
                buzzBeepBlink(r);
            }
        }
    }
}
```

### 11.2 通知排名算法

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    通知排名算法                                            │
└─────────────────────────────────────────────────────────────────────────────┘

排名是多因素综合评估：

┌──────────────────┬──────────────────────────────────────────────────────────┐
│      因素        │                       权重                              │
├──────────────────┼──────────────────────────────────────────────────────────┤
│  重要性级别      │  ★★★★★ (最重要)                                       │
│  通知渠道        │  ★★★★☆                                                │
│  通知类别        │  ★★★★☆                                                │
│  用户亲密度      │  ★★★☆☆                                                │
│  通知时间        │  ★★★☆☆                                                │
│  通知频次        │  ★★☆☆☆ (频繁可能降级)                                 │
│  应用优先级      │  ★★☆☆☆                                                │
└──────────────────┴──────────────────────────────────────────────────────────┘

排名流程：
┌─────────────────────────────────────────────────────────────────────────────┐
│  RankingHelper.rank(NotificationList list, NotificationRecord record)      │
│                                                                          │
│  1. 提取信号 (extractSignals)                                            │
│     ├── 读取 Notification 中的元数据                                     │
│     ├── 分析 NotificationChannel 设置                                    │
│     ├── 分析 Notification.Style                                          │
│     └── 计算用户亲密度                                                    │
│                                                                          │
│  2. 计算排名分数                                                          │
│     score = importanceScore * 100 +                                      │
│             channelScore * 10 +                                          │
│             categoryScore * 5 +                                          │
│             affinityScore * 2 +                                          │
│             timeScore                                                     │
│                                                                          │
│  3. 插入排序                                                              │
│     for (int i = 0; i < list.size(); i++) {                              │
│         if (record.getScore() > list.get(i).getScore()) {                │
│             list.addAt(i, record);                                        │
│             break;                                                        │
│         }                                                                 │
│     }                                                                     │
│                                                                          │
│  4. 生成 RankingMap                                                       │
│     return new RankingMap(list);                                         │
└─────────────────────────────────────────────────────────────────────────────┘

重要性级别：
IMPORTANCE_UNSPECIFIED = -1   // 未指定
IMPORTANCE_NONE = 0          // 不显示
IMPORTANCE_MIN = 1           // 最小
IMPORTANCE_LOW = 2           // 低
IMPORTANCE_DEFAULT = 3       // 默认
IMPORTANCE_HIGH = 4          // 高
IMPORTANCE_MAX = 5           // 最大

通知类别优先级：
CATEGORY_CALL > CATEGORY_MESSAGE > CATEGORY_EVENT > CATEGORY_ALARM > 
CATEGORY_REMINDER > CATEGORY_SOCIAL > CATEGORY_EMAIL > CATEGORY_PROMO
```

### 11.3 通知分组机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    通知分组机制                                            │
└─────────────────────────────────────────────────────────────────────────────┘

通知分组允许将多个通知合并为一个组：

┌─────────────────────────────────────────────────────────────────────────────┐
│  分组通知示例                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  微信 (3 条消息)                                                    │   │
│  │  ┌───────────────────────────────────────────────────────────────┐ │   │
│  │  │  张三: 你好                                                   │ │   │
│  │  │  李四: 在吗？                                                 │ │   │
│  │  │  王五: 明天见                                                 │ │   │
│  │  └───────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  邮件 (5 封未读)                                                    │   │
│  │  ┌───────────────────────────────────────────────────────────────┐ │   │
│  │  │  邮件1: 标题...                                               │ │   │
│  │  │  邮件2: 标题...                                               │ │   │
│  │  │  +3 封未读                                                    │ │   │
│  │  └───────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

分组实现：
```java
// 创建分组通知
Notification groupSummary = new Notification.Builder(context, channelId)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("微信")
    .setContentText("3 条消息")
    .setGroup("wechat_group")  // 分组 key
    .setGroupSummary(true)      // 标记为组摘要
    .build();

Notification notification1 = new Notification.Builder(context, channelId)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("张三")
    .setContentText("你好")
    .setGroup("wechat_group")  // 相同分组 key
    .build();

// 发送
notificationManager.notify(0, groupSummary);
notificationManager.notify(1, notification1);
```

分组规则：
1. 相同 setGroup() 值的通知属于同一组
2. 组摘要 (setGroupSummary(true)) 显示在组头部
3. 子通知按时间排序
4. 用户可以展开组查看所有子通知
```

### 11.4 通知气泡 (Bubble)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    通知气泡 (Bubble)                                       │
└─────────────────────────────────────────────────────────────────────────────┘

气泡是 Android 11 引入的悬浮通知形式：

┌─────────────────────────────────────────────────────────────────────────────┐
│  气泡显示效果                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

                    屏幕边缘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        │          ┌────┴────┐         │
        │          │  气泡   │         │  ← 悬浮气泡
        │          │   👤    │         │
        │          └────┬────┘         │
        │               │               │
        │          点击展开            │
        │               │               │
        │               ▼               │
        │    ┌─────────────────────┐   │
        │    │  张三               │   │  ← 展开的气泡
        │    │  你好！             │   │
        │    │  [输入框]          │   │
        │    │  [发送]             │   │
        │    └─────────────────────┘   │
        │               │               │
        └───────────────┴───────────────┘

气泡实现：
```java
// 创建气泡
BubbleMetadata bubble = new BubbleMetadata.Builder()
    .setIntent(bubbleIntent)  // 点击气泡打开的 Intent
    .setDesiredHeight(600)    // 气泡高度
    .setIcon(Icon.createWithResource(context, R.drawable.avatar))
    .build();

Notification notification = new Notification.Builder(context, channelId)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("张三")
    .setContentText("你好！")
    .setBubbleMetadata(bubble)  // 设置气泡
    .build();
```

气泡规则：
1. 需要 NotificationChannel 允许气泡
2. 用户可以在设置中关闭气泡
3. 气泡可以拖动和展开
4. 展开时显示 Activity 内容
```

### 11.5 通知声音和振动

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    通知声音和振动                                          │
└─────────────────────────────────────────────────────────────────────────────┘

NMS 处理通知声音和振动的流程：

NotificationManagerService.buzzBeepBlink(NotificationRecord record):
│
├── 1. 检查是否需要提醒
│   if (record.isIntercepted() || !record.shouldShowAlert()) {
│       return;  // 不需要提醒
│   }
│
├── 2. 检查勿扰模式
│   if (mZenModeHelper.shouldIntercept(record)) {
│       return;  // 勿扰模式拦截
│   }
│
├── 3. 播放声音
│   if (record.getSound() != null) {
│       playSound(record.getSound(), record.getAttributes());
│   }
│
├── 4. 触发振动
│   if (record.getVibration() != null) {
│       vibrate(record.getVibration(), record.getAttributes());
│   }
│
├── 5. 闪烁 LED
│   if (record.getLight() != null) {
│       blinkLight(record.getLight());
│   }
│
└── 6. 记录统计
    mUsageStats.registerAlerted(record);

声音配置：
NotificationChannel channel = new NotificationChannel(id, name, importance);
channel.setSound(
    Uri.parse("content://settings/system/notification_sound"),
    new AudioAttributes.Builder()
        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
        .setUsage(AudioAttributes.USAGE_NOTIFICATION)
        .build()
);

振动配置：
channel.enableVibration(true);
channel.setVibrationPattern(new long[]{0, 500, 200, 500});  // 延迟, 振动, 静音, 振动...
```

---

## 12. AOD 高级特性

> 本节内容基于 Android 16 (API 36) AOSP 源码分析
> 源码路径：frameworks/base/packages/SystemUI/src/com/android/systemui/doze/

### 12.1 AOD 与 WakefulnessLifecycle 交互

> **源码路径**:
> - `frameworks/base/packages/SystemUI/src/com/android/systemui/keyguard/WakefulnessLifecycle.java`
> - `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeMachine.java`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              AOD 与 WakefulnessLifecycle 交互 (Android 16)                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      WakefulnessLifecycle                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    唤醒状态生命周期                                   │   │
│  │                                                                   │   │
│  │  @Wakefulness int:                                                │   │
│  │  - WAKEFULNESS_ASLEEP      // 睡眠                                │   │
│  │  - WAKEFULNESS_WAKING      // 正在唤醒                            │   │
│  │  - WAKEFULNESS_AWAKE       // 已唤醒                              │   │
│  │  - WAKEFULNESS_GOING_TO_SLEEP  // 进入睡眠                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      DozeMachine                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │                    状态机                                    │  │   │
│  │  │  - resolveIntermediateState() 检查唤醒状态                   │  │   │
│  │  │  - WAKEFULNESS_AWAKE/WAKING → FINISH                         │  │   │
│  │  │  - 其他 → DOZE/DOZE_AOD/DOZE_AOD_DOCKED                      │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      DozeHost (接口)                                │   │
│  │  - startDozing() / stopDozing()                                    │   │
│  │  - pulseWhileDozing()                                              │   │
│  │  - isAlwaysOnSuppressed() / isPowerSaveActive()                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

```java
/**
 * DozeMachine 状态转换逻辑 (Android 16 AOSP)
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeMachine.java
 */
@DozeScope
public class DozeMachine {

    private final WakefulnessLifecycle mWakefulnessLifecycle;

    /**
     * 解析中间状态 - 根据 WakefulnessLifecycle 决定下一状态
     */
    private void resolveIntermediateState(State state) {
        switch (state) {
            case INITIALIZED:
            case DOZE_PULSE_DONE:
                final State nextState;
                @Wakefulness int wakefulness = mWakefulnessLifecycle.getWakefulness();

                // 如果设备已唤醒或正在唤醒，直接结束 Doze
                if (state != State.INITIALIZED
                        && (wakefulness == WAKEFULNESS_AWAKE
                        || wakefulness == WAKEFULNESS_WAKING)) {
                    nextState = State.FINISH;
                } else if (mDockManager.isDocked()) {
                    // 底座模式
                    nextState = mDockManager.isHidden() ? State.DOZE : State.DOZE_AOD_DOCKED;
                } else if (mAmbientDisplayConfig.alwaysOnEnabled(mUserTracker.getUserId())) {
                    // AOD 已启用
                    nextState = State.DOZE_AOD;
                } else {
                    // 常规 Doze
                    nextState = State.DOZE;
                }

                transitionTo(nextState, DozeLog.PULSE_REASON_NONE);
                break;
            default:
                break;
        }
    }
}
```

### 12.2 AOD 显示状态管理

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeScreenState.java`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD 显示状态管理 (Android 16)                            │
└─────────────────────────────────────────────────────────────────────────────┘

Display.State 状态映射:
┌─────────────────────┬───────────────────────────────────────────────────────┐
│  DozeMachine.State  │                  Display.State                       │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  UNINITIALIZED      │  STATE_ON (如果 shouldControlScreenOff) / STATE_OFF   │
│  INITIALIZED        │  STATE_ON (如果 shouldControlScreenOff) / STATE_OFF   │
│  DOZE               │  STATE_OFF                                          │
│  DOZE_SUSPEND_TRIGGERS │ STATE_OFF                                        │
│  DOZE_AOD           │  STATE_DOZE_SUSPEND                                 │
│  DOZE_AOD_PAUSED    │  STATE_OFF                                          │
│  DOZE_AOD_PAUSING   │  STATE_DOZE_SUSPEND                                 │
│  DOZE_AOD_DOCKED    │  STATE_ON                                           │
│  DOZE_REQUEST_PULSE │  STATE_OFF (如果需要消隐) / STATE_ON                 │
│  DOZE_PULSING       │  STATE_ON                                           │
│  DOZE_PULSING_BRIGHT│  STATE_ON                                           │
│  DOZE_PULSE_DONE    │  STATE_UNKNOWN                                      │
│  FINISH             │  STATE_UNKNOWN                                      │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

```java
/**
 * DozeScreenState - 控制 Doze 时的屏幕状态 (Android 16 AOSP)
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeScreenState.java
 */
@DozeScope
public class DozeScreenState implements DozeMachine.Part {

    private static final String TAG = "DozeScreenState";

    /** 进入低功耗模式的延迟 (4秒) */
    private static final int ENTER_DOZE_DELAY = 4000;
    /** 进入低功耗模式前隐藏壁纸的延迟 (2.5秒) */
    public static final int ENTER_DOZE_HIDE_WALLPAPER_DELAY = 2500;
    /** UDFPS 激活时额外的显示状态延迟 */
    public static final int UDFPS_DISPLAY_STATE_DELAY = 1200;

    private final DozeMachine.Service mDozeService;
    private final Handler mHandler;
    private final DozeParameters mParameters;
    private final DozeHost mDozeHost;
    private final DozeScreenBrightness mDozeScreenBrightness;

    @Override
    public void transitionTo(DozeMachine.State oldState, DozeMachine.State newState) {
        int screenState = newState.screenState(mParameters);
        mDozeHost.cancelGentleSleep();

        if (newState == DozeMachine.State.FINISH) {
            // 确保在 DozeService 销毁后不应用屏幕状态
            mPendingScreenState = Display.STATE_UNKNOWN;
            mHandler.removeCallbacks(mApplyPendingScreenState);
            applyScreenState(screenState);
            mWakeLock.setAcquired(false);
            return;
        }

        if (screenState == Display.STATE_UNKNOWN) {
            return; // 保持现有状态
        }

        final boolean pulseEnding = oldState == DOZE_PULSE_DONE && newState.isAlwaysOn();
        final boolean turningOn = (oldState == DOZE_AOD_PAUSED || oldState == DOZE)
                && newState.isAlwaysOn();
        final boolean justInitialized = oldState == DozeMachine.State.INITIALIZED;

        if (pulseEnding || turningOn || justInitialized) {
            mPendingScreenState = screenState;

            // 延迟屏幕状态转换
            boolean shouldDelayTransitionEnteringDoze = newState == DOZE_AOD
                    && mParameters.shouldDelayDisplayDozeTransition() && !turningOn;

            // 如果 UDFPS 正在认证，延迟更长时间
            boolean shouldDelayTransitionForUDFPS = newState == DOZE_AOD
                    && mUdfpsController != null && mUdfpsController.isFingerDown();

            if (shouldDelayTransitionEnteringDoze) {
                mHandler.postDelayed(mApplyPendingScreenState, ENTER_DOZE_DELAY);
            } else if (shouldDelayTransitionForUDFPS) {
                mDozeLog.traceDisplayStateDelayedByUdfps(mPendingScreenState);
                mHandler.postDelayed(mApplyPendingScreenState, UDFPS_DISPLAY_STATE_DELAY);
            } else {
                mHandler.post(mApplyPendingScreenState);
            }
        } else if (turningOff) {
            mDozeHost.prepareForGentleSleep(() -> applyScreenState(screenState));
        } else {
            applyScreenState(screenState);
        }
    }

    private void applyScreenState(int screenState) {
        if (screenState != Display.STATE_UNKNOWN) {
            mDozeService.setDozeScreenState(screenState);
            if (screenState == Display.STATE_DOZE) {
                mDozeScreenBrightness.updateBrightnessAndReady(false);
            }
        }
    }
}
```

### 12.3 AOD 传感器集成 (Android 16)

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeSensors.java`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD 传感器集成 (Android 16)                              │
└─────────────────────────────────────────────────────────────────────────────┘

支持的传感器类型 (DozeSensors.TriggerSensor):
┌───────────────────────────┬─────────────────────────────────────────────────┐
│        传感器类型          │                    说明                         │
├───────────────────────────┼─────────────────────────────────────────────────┤
│  TYPE_SIGNIFICANT_MOTION  │  显著运动检测                                   │
│  TYPE_PICK_UP_GESTURE     │  拾起手势 (Settings: DOZE_PICK_UP_GESTURE)      │
│  doubleTapSensorType      │  双击屏幕 (Settings: DOZE_DOUBLE_TAP_GESTURE)   │
│  tapSensorTypeMapping     │  单击屏幕 (Settings: DOZE_TAP_SCREEN_GESTURE)   │
│  longPressSensorType      │  长按 (Settings: DOZE_PULSE_ON_LONG_PRESS)      │
│  udfpsLongPressSensorType │  UDFPS 长按 (doze_pulse_on_auth)               │
│  TYPE_WAKE_DISPLAY        │  唤醒显示手势 (PluginSensor)                    │
│  TYPE_WAKE_LOCK_SCREEN    │  唤醒锁屏手势 (PluginSensor)                    │
│  quickPickupSensorType    │  快速拾起 (Settings: DOZE_QUICK_PICKUP_GESTURE) │
└───────────────────────────┴─────────────────────────────────────────────────┘

距离传感器状态影响:
┌─────────────────────────────────────────────────────────────────────────────┐
│  ProximitySensor 状态变化                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  NEAR (接近):                                                               │
│  - DOZE_AOD → DOZE_AOD_PAUSING → DOZE_AOD_PAUSED                           │
│  - 屏幕状态: STATE_DOZE_SUSPEND → STATE_OFF                                │
│                                                                             │
│  FAR (远离):                                                                │
│  - DOZE_AOD_PAUSED/DOZE_AOD_PAUSING → DOZE_AOD                             │
│  - 屏幕状态: STATE_OFF → STATE_DOZE_SUSPEND                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

```java
/**
 * DozeSensors 传感器管理 (Android 16 AOSP)
 *
 * 位置: frameworks/base/packages/SystemUI/src/com/android/systemui/doze/DozeSensors.java
 */
public class DozeSensors {
    private static final String TAG = "DozeSensors";

    private final AsyncSensorManager mSensorManager;
    private final AmbientDisplayConfiguration mConfig;
    private final WakeLock mWakeLock;
    private final DozeLog mDozeLog;
    private final ProximitySensor mProximitySensor;

    // 传感器数组
    @VisibleForTesting
    protected TriggerSensor[] mTriggerSensors;

    // 传感器回调
    private final Callback mSensorCallback;
    private final Consumer<Boolean> mProxCallback;

    DozeSensors(Resources resources, AsyncSensorManager sensorManager,
            DozeParameters dozeParameters, AmbientDisplayConfiguration config,
            WakeLock wakeLock, Callback sensorCallback, Consumer<Boolean> proxCallback,
            DozeLog dozeLog, ProximitySensor proximitySensor,
            SecureSettings secureSettings, AuthController authController,
            DevicePostureController devicePostureController,
            SelectedUserInteractor selectedUserInteractor) {

        // 初始化触发传感器数组
        mTriggerSensors = new TriggerSensor[] {
            // 显著运动传感器
            new TriggerSensor(
                    mSensorManager.getDefaultSensor(Sensor.TYPE_SIGNIFICANT_MOTION),
                    null, dozeParameters.getPulseOnSigMotion(),
                    DozeLog.PULSE_REASON_SENSOR_SIGMOTION,
                    false, false),

            // 拾起手势
            new TriggerSensor(
                    mSensorManager.getDefaultSensor(Sensor.TYPE_PICK_UP_GESTURE),
                    Settings.Secure.DOZE_PICK_UP_GESTURE,
                    config.dozePickupSensorAvailable(),
                    DozeLog.REASON_SENSOR_PICKUP,
                    false, false),

            // 双击传感器
            new TriggerSensor(
                    findSensor(config.doubleTapSensorType()),
                    Settings.Secure.DOZE_DOUBLE_TAP_GESTURE,
                    true, DozeLog.REASON_SENSOR_DOUBLE_TAP,
                    dozeParameters.doubleTapReportsTouchCoordinates(),
                    true),

            // 单击传感器 (支持多姿态)
            new TriggerSensor(
                    findSensors(config.tapSensorTypeMapping()),
                    Settings.Secure.DOZE_TAP_SCREEN_GESTURE,
                    true, DozeLog.REASON_SENSOR_TAP,
                    true, true),

            // UDFPS 长按
            new TriggerSensor(
                    findSensor(config.udfpsLongPressSensorType()),
                    "doze_pulse_on_auth", true,
                    udfpsLongPressConfigured(),
                    DozeLog.REASON_SENSOR_UDFPS_LONG_PRESS,
                    true, true),

            // 唤醒显示 (插件传感器)
            new PluginSensor(
                    new SensorManagerPlugin.Sensor(TYPE_WAKE_DISPLAY),
                    Settings.Secure.DOZE_WAKE_DISPLAY_GESTURE,
                    mConfig.wakeScreenGestureAvailable(),
                    DozeLog.REASON_SENSOR_WAKE_UP_PRESENCE,
                    false, false),

            // 快速拾起
            new TriggerSensor(
                    findSensor(config.quickPickupSensorType()),
                    Settings.Secure.DOZE_QUICK_PICKUP_GESTURE,
                    true, quickPickUpConfigured(),
                    DozeLog.REASON_SENSOR_QUICK_PICKUP,
                    false, false),
        };

        // 注册距离传感器
        mProximitySensor.register(proximityEvent -> {
            if (proximityEvent != null) {
                mProxCallback.accept(!proximityEvent.getBelow());
            }
        });
    }

    /**
     * 设置传感器监听状态
     */
    public void setListening(boolean listen, boolean includeTouchScreenSensors,
            boolean includeAodOnlySensors) {
        mListening = listen;
        mListeningTouchScreenSensors = includeTouchScreenSensors;
        mListeningAodOnlySensors = includeAodOnlySensors;
        updateListening();
    }

    /**
     * 传感器回调接口
     */
    public interface Callback {
        void onSensorPulse(int pulseReason, float screenX, float screenY, float[] rawValues);
    }
}
```

### 12.4 AOD 配置和设置 (Android 16)

> **源码路径**: `frameworks/base/core/java/android/hardware/display/AmbientDisplayConfiguration.java`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD 配置项 (Android 16)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Settings.Secure 配置项:
┌─────────────────────────────────────┬───────────────────────────────────────┐
│           配置项名称                  │                  说明                │
├─────────────────────────────────────┼───────────────────────────────────────┤
│  doze_enabled                       │  Doze 总开关                          │
│  doze_always_on                     │  常亮显示开关                         │
│  doze_pick_up_gesture               │  拾起唤醒                             │
│  doze_double_tap_gesture            │  双击唤醒                             │
│  doze_tap_screen_gesture            │  单击唤醒                             │
│  doze_pulse_on_long_press           │  长按脉冲                             │
│  doze_wake_display_gesture          │  唤醒显示手势                         │
│  doze_wake_lock_screen_gesture      │  唤醒锁屏手势                         │
│  doze_quick_pickup_gesture          │  快速拾起                             │
└─────────────────────────────────────┴───────────────────────────────────────┘

AmbientDisplayConfiguration 关键方法:
- alwaysOnEnabled(userId)          // 检查 AOD 是否启用
- pulseOnNotificationEnabled(userId) // 通知脉冲是否启用
- dozePickupSensorAvailable()      // 拾起传感器是否可用
- wakeScreenGestureAvailable()     // 唤醒手势是否可用
- screenOffUdfpsEnabled(userId)    // 熄屏 UDFPS 是否启用
- quickPickupSensorEnabled(userId) // 快速拾起是否启用
```

```java
/**
 * AmbientDisplayConfiguration - AOD 配置读取 (Android 16 AOSP)
 *
 * 位置: frameworks/base/core/java/android/hardware/display/AmbientDisplayConfiguration.java
 */
public class AmbientDisplayConfiguration {

    /**
     * 检查常亮显示是否启用
     */
    public boolean alwaysOnEnabled(int user) {
        // 检查设备支持 + 用户设置
        return !accessibilityInversionEnabled(user)
                && alwaysOnAvailable()
                && (alwaysOnSettingsForUser(user)
                || accessControlModeAlwaysOn(user));
    }

    /**
     * 检查通知脉冲是否启用
     */
    public boolean pulseOnNotificationEnabled(int user) {
        return pulseOnNotificationAvailable() && enabledBySetting(
                Settings.Secure.DOZE_PULSE_ON_NOTIFICATIONS, user, DOZE_PULSE_ON_NOTIFICATIONS_DEF);
    }

    /**
     * 检查拾起传感器是否可用
     */
    public boolean dozePickupSensorAvailable() {
        return mResources.getBoolean(com.android.internal.R.bool.config_dozePickupGestureAvailable);
    }

    /**
     * 获取双击传感器类型
     */
    public String doubleTapSensorType() {
        return mResources.getString(com.android.internal.R.string.config_dozeDoubleTapSensorType);
    }

    /**
     * 检查熄屏 UDFPS 是否启用
     */
    public boolean screenOffUdfpsEnabled(int userId) {
        return enabledBySetting(Settings.Secure.DOZE_PULSE_ON_AUTH, userId, 1);
    }

    /**
     * 检查快速拾起是否启用
     */
    public boolean quickPickupSensorEnabled(int userId) {
        return enabledBySetting(Settings.Secure.DOZE_QUICK_PICKUP_GESTURE, userId, 1);
    }
}
```

### 10.1 通知系统完整链路

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    通知系统完整链路（深度版）                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  第一步：应用创建通知 (Android SDK)                                        │
└─────────────────────────────────────────────────────────────────────────────┘

应用进程:
│
├── 1.1 创建 NotificationChannel (Android 8.0+)
│   NotificationChannel channel = new NotificationChannel(
│       "channel_id",        // 渠道 ID
│       "渠道名称",           // 用户可见名称
│       NotificationManager.IMPORTANCE_HIGH  // 重要性级别
│   );
│   channel.setDescription("渠道描述");
│   channel.enableLights(true);
│   channel.setLightColor(Color.RED);
│   channel.enableVibration(true);
│   channel.setVibrationPattern(new long[]{100, 200, 300, 400});
│   channel.setShowBadge(true);  // 启动器角标
│   mNotificationManager.createNotificationChannel(channel);
│
├── 1.2 创建 Notification.Builder
│   Notification.Builder builder = new Notification.Builder(context, channelId)
│       .setSmallIcon(R.drawable.ic_notification)
│       .setContentTitle("标题")
│       .setContentText("内容")
│       .setLargeIcon(bitmap)
│       .setContentIntent(pendingIntent)
│       .setDeleteIntent(deletePendingIntent)
│       .setAutoCancel(true)
│       .setOngoing(false)
│       .setWhen(System.currentTimeMillis())
│       .setShowWhen(true)
│       .setCategory(Notification.CATEGORY_MESSAGE)
│       .setPriority(Notification.PRIORITY_HIGH);
│
├── 1.3 创建 RemoteViews（自定义通知布局）
│   RemoteViews contentView = new RemoteViews(pkgName, R.layout.notification);
│   contentView.setTextViewText(R.id.title, "标题");
│   contentView.setImageViewResource(R.id.icon, R.drawable.icon);
│   contentView.setOnClickPendingIntent(R.id.button, pendingIntent);
│   builder.setCustomContentView(contentView);  // 折叠视图
│   builder.setCustomBigContentView(bigContentView);  // 展开视图
│
├── 1.4 添加 Action 按钮
│   Notification.Action action = new Notification.Action.Builder(
│       Icon.createWithResource(context, R.drawable.action_icon),
│       "回复",
│       replyPendingIntent
│   )
│   .addRemoteInput(remoteInput)  // 支持直接输入
│   .setAllowGeneratedReplies(true)
│   .build();
│   builder.addAction(action);
│
├── 1.5 设置样式 (Style)
│   // BigTextStyle
│   builder.setStyle(new Notification.BigTextStyle()
│       .bigText("长文本内容...")
│       .setBigContentTitle("展开标题")
│       .setSummaryText("摘要"));
│   
│   // MessagingStyle
│   Person user = new Person.Builder().setName("张三").build();
│   builder.setStyle(new Notification.MessagingStyle(user)
│       .addMessage("你好", System.currentTimeMillis(), user)
│       .setConversationTitle("对话标题"));
│
└── 1.6 发送通知
    NotificationManager.notify(id, builder.build());

┌─────────────────────────────────────────────────────────────────────────────┐
│  第二步：Framework 层处理 (NotificationManagerService)                      │
└─────────────────────────────────────────────────────────────────────────────┘

system_server 进程 (NotificationManagerService):
│
├── 2.1 接收通知请求
│   // INotificationManager.Stub.enqueueNotificationWithTag()
│   public void enqueueNotificationWithTag(String pkg, String opPkg,
│           String tag, int id, Notification notification, int userId) {
│       
│       // 检查调用者权限
│       checkCallerIsSystemOrSameApp(pkg);
│       
│       // 检查通知限制
│       enforceRateLimitingForNotification(pkg, userId);
│       
│       // 检查通知数量限制
│       enforceNotificationCountLimit(pkg, userId);
│   }
│
├── 2.2 创建 NotificationRecord
│   final NotificationRecord r = new NotificationRecord(
│       mContext,
│       notification,   // 通知对象
│       pkg,           // 包名
│       tag,           // 标签
│       id,            // ID
│       userId         // 用户 ID
│   );
│   
│   // 提取通知信号（用于排名）
│   mRankingHelper.extractSignals(r);
│
├── 2.3 应用过滤规则
│   // 检查应用通知权限
│   if (mPreferencesHelper.isBlocked(pkg, userId)) {
│       return;  // 应用通知被禁用
│   }
│   
│   // 检查渠道通知权限
│   if (mPreferencesHelper.isChannelBlocked(pkg, channelId, userId)) {
│       return;  // 渠道通知被禁用
│   }
│   
│   // 检查勿扰模式
│   if (mZenModeHelper.shouldIntercept(r)) {
│       r.setIntercepted(true);  // 被勿扰模式拦截
│   }
│
├── 2.4 保存到 NotificationRecord 列表
│   // 先移除旧通知（如果存在）
│   mNotificationList.remove(key);
│   
│   // 添加新通知
│   mNotificationList.add(r);
│
├── 2.5 持久化通知（重启后恢复）
│   mNotificationStore.add(r);
│
└── 2.6 通知 SystemUI
    // 回调所有注册的 NotificationListenerService
    for (ManagedServiceInfo info : mListeners) {
        // 通过 Binder IPC 回调
        info.service.onNotificationPosted(sbn, rankingMap);
    }

┌─────────────────────────────────────────────────────────────────────────────┐
│  第三步：SystemUI 接收通知 (NotificationListenerService)                    │
└─────────────────────────────────────────────────────────────────────────────┘

SystemUI 进程:
│
├── 3.1 NotificationListenerService.onNotificationPosted()
│   @Override
│   public void onNotificationPosted(StatusBarNotification sbn, 
│           RankingMap rankingMap) {
│       
│       // 获取通知排名
│       Ranking ranking = new Ranking();
│       rankingMap.getRanking(sbn.getKey(), ranking);
│       
│       // 转发给 NotificationEntryManager
│       mEntryManager.addNotification(sbn, ranking);
│   }
│
├── 3.2 NotificationEntryManager.addNotification()
│   // 创建 NotificationEntry
│   NotificationEntry entry = new NotificationEntry(sbn);
│   entry.setRanking(ranking);
│   
│   // 添加到通知列表
│   mNotificationList.add(entry);
│   
│   // 通知监听器
│   for (NotificationListener listener : mListeners) {
│       listener.onNotificationAdded(entry);
│   }
│
├── 3.3 NotificationRowBinder.bindRow()
│   // 获取 RemoteViews
│   RemoteViews contentView = notification.contentView;
│   RemoteViews bigContentView = notification.bigContentView;
│   RemoteViews headsUpContentView = notification.headsUpContentView;
│   
│   // 应用 RemoteViews 到通知行
│   row.setContentView(contentView);
│   row.setBigContentView(bigContentView);
│   row.setHeadsUpView(headsUpContentView);
│
└── 3.4 更新状态栏图标
    // 添加状态栏图标
    mStatusBarIconController.addIcon(iconKey, icon);

┌─────────────────────────────────────────────────────────────────────────────┐
│  第四步：通知渲染 (RemoteViews 展开与绑定)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

通知视图渲染:
│
├── 4.1 NotificationContentView.setContent()
│   public void setContent(RemoteViews views) {
│       // 清空现有内容
│       removeAllViews();
│       
│       // 应用 RemoteViews
│       View view = views.apply(mContext, this);
│       addView(view);
│   }
│
├── 4.2 RemoteViews.apply() 实现
│   public View apply(Context context, ViewGroup parent) {
│       // 1. 加载布局
│       View result = inflateView(context, parent);
│       
│       // 2. 执行所有 Action
│       performApply(result, parent);
│       
│       return result;
│   }
│
├── 4.3 执行 RemoteViews Action
│   private void performApply(View v, ViewGroup parent) {
│       if (mActions != null) {
│           for (Action action : mActions) {
│               // 每个 Action 修改 View
│               action.apply(v, parent, mOnClickHandler);
│           }
│       }
│   }
│
└── 4.4 渲染完成，通知视图显示在通知面板
```

### 10.2 RemoteViews 深度解析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RemoteViews 完整原理                                   │
└─────────────────────────────────────────────────────────────────────────────┘

RemoteViews 的本质：序列化的视图操作

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. RemoteViews 数据结构                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

public class RemoteViews implements Parcelable {
    // 包名（用于加载资源）
    private final String mPackage;
    
    // 布局 ID
    private final int mLayoutId;
    
    // 操作列表（序列化后跨进程传递）
    private ArrayList<Action> mActions;
    
    // 内存位图缓存
    private BitmapCache mBitmapCache;
    
    // 是否是主题应用
    private boolean mIsRoot;
    
    // 应用的包名（可能与 mPackage 不同）
    private String mApplicationPackage;
}

┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Action 列表（每个操作都是一个 Action）                                  │
└─────────────────────────────────────────────────────────────────────────────┘

// Action 基类
private abstract static class Action implements Parcelable {
    // 操作 ID（用于反序列化）
    abstract public int getActionTag();
    
    // 应用操作到 View
    abstract public void apply(View root, ViewGroup rootParent,
            OnClickHandler handler);
}

// 具体的 Action 实现：
├── SetTextAction          // 设置文本
├── SetTextColorAction     // 设置文字颜色
├── SetImageResourceAction // 设置图片资源
├── SetImageBitmapAction   // 设置 Bitmap
├── SetOnClickPendingIntentAction  // 设置点击事件
├── SetViewVisibilityAction  // 设置可见性
├── SetViewPaddingAction   // 设置内边距
├── SetProgressBarAction   // 设置进度条
├── SetChronometerAction   // 设置计时器
└── AddViewAction          // 添加子 View

┌─────────────────────────────────────────────────────────────────────────────┐
│  3. RemoteViews 创建与操作（应用进程）                                      │
└─────────────────────────────────────────────────────────────────────────────┘

// 创建 RemoteViews
RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.notification);

// 每个 setXXX 方法都会创建一个 Action 并添加到 mActions 列表
views.setTextViewText(R.id.title, "标题");
// 内部实现：
// mActions.add(new SetTextAction(R.id.title, "标题"));

views.setImageViewResource(R.id.icon, R.drawable.icon);
// 内部实现：
// mActions.add(new SetImageResourceAction(R.id.icon, R.drawable.icon));

views.setOnClickPendingIntent(R.id.button, pendingIntent);
// 内部实现：
// mActions.add(new SetOnClickPendingIntentAction(R.id.button, pendingIntent));

┌─────────────────────────────────────────────────────────────────────────────┐
│  4. RemoteViews 序列化（跨进程传递）                                        │
└─────────────────────────────────────────────────────────────────────────────┘

// NotificationManager.notify() 时，Notification 中的 RemoteViews 会被序列化

@Override
public void writeToParcel(Parcel dest, int flags) {
    // 1. 写入包名
    dest.writeString(mPackage);
    
    // 2. 写入布局 ID
    dest.writeInt(mLayoutId);
    
    // 3. 写入 Action 数量
    dest.writeInt(mActions.size());
    
    // 4. 序列化每个 Action
    for (Action action : mActions) {
        dest.writeInt(action.getActionTag());  // Action 类型
        action.writeToParcel(dest, flags);     // Action 数据
    }
    
    // 5. 写入位图缓存
    mBitmapCache.writeToParcel(dest, flags);
}

// Binder IPC 传递序列化后的 Parcel

┌─────────────────────────────────────────────────────────────────────────────┐
│  5. RemoteViews 反序列化（SystemUI 进程）                                   │
└─────────────────────────────────────────────────────────────────────────────┘

// NotificationListenerService 接收到通知后，RemoteViews 被反序列化

public static RemoteViews createFromParcel(Parcel parcel) {
    // 1. 读取包名
    String packageName = parcel.readString();
    
    // 2. 读取布局 ID
    int layoutId = parcel.readInt();
    
    // 3. 创建 RemoteViews
    RemoteViews views = new RemoteViews(packageName, layoutId);
    
    // 4. 读取 Action 数量
    int actionCount = parcel.readInt();
    
    // 5. 反序列化每个 Action
    for (int i = 0; i < actionCount; i++) {
        int actionTag = parcel.readInt();
        Action action = createActionFromTag(actionTag);
        action.readFromParcel(parcel);
        views.mActions.add(action);
    }
    
    return views;
}

┌─────────────────────────────────────────────────────────────────────────────┐
│  6. RemoteViews 应用（展开为 View）                                        │
└─────────────────────────────────────────────────────────────────────────────┘

// SystemUI 调用 apply() 方法将 RemoteViews 展开为真正的 View

public View apply(Context context, ViewGroup parent) {
    // 1. 使用 LayoutInflater 加载布局
    View result = inflateView(context, parent);
    
    // 2. 执行所有 Action，修改 View 属性
    performApply(result, parent);
    
    return result;
}

private View inflateView(Context context, ViewGroup parent) {
    // 使用 RemoteViews 的布局 ID 加载布局
    // 注意：使用的是 SystemUI 的 Context，但资源来自应用
    LayoutInflater inflater = LayoutInflater.from(context);
    return inflater.inflate(mLayoutId, parent, false);
}

private void performApply(View v, ViewGroup parent) {
    if (mActions != null) {
        for (Action action : mActions) {
            // 执行每个 Action
            action.apply(v, parent, mOnClickHandler);
        }
    }
}

// SetTextAction 的 apply 实现
private class SetTextAction extends Action {
    int mViewId;
    CharSequence mText;
    
    @Override
    public void apply(View root, ViewGroup rootParent, OnClickHandler handler) {
        TextView textView = root.findViewById(mViewId);
        if (textView != null) {
            textView.setText(mText);
        }
    }
}

// SetOnClickPendingIntentAction 的 apply 实现
private class SetOnClickPendingIntentAction extends Action {
    int mViewId;
    PendingIntent mPendingIntent;
    
    @Override
    public void apply(View root, ViewGroup rootParent, OnClickHandler handler) {
        View target = root.findViewById(mViewId);
        if (target != null && mPendingIntent != null) {
            target.setOnClickListener(v -> {
                try {
                    mPendingIntent.send();
                } catch (PendingIntent.CanceledException e) {
                    // 处理取消异常
                }
            });
        }
    }
}
```

### 10.3 AOD 状态机深度解析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD DozeMachine 状态机                                  │
└─────────────────────────────────────────────────────────────────────────────┘

DozeMachine 是 AOD 的核心，管理设备的 Doze 状态

┌─────────────────────────────────────────────────────────────────────────────┐
│  状态定义                                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

public enum State {
    // 初始状态
    DOZE_INIT,              // 初始化状态
    
    // Doze 状态（屏幕关闭）
    DOZE,                   // 深度睡眠，屏幕完全关闭
    DOZE_AOD,              // AOD 模式，屏幕部分点亮
    DOZE_AOD_PAUSING,      // AOD 暂停中
    DOZE_AOD_PAUSED,       // AOD 已暂停
    DOZE_SUSPEND,          // 挂起状态
    
    // 浅睡眠状态（屏幕微亮）
    DOZE_REQUEST_PULSE,    // 请求脉冲
    DOZE_PULSE_START,      // 脉冲开始
    DOZE_PULSE_DOZE,       // 脉冲 Doze
    DOZE_PULSE_DOZE_AOD,   // 脉冲 AOD
    DOZE_PULSE_DONE,       // 脉冲完成
    DOZE_REST,             // 浅睡眠休息
    
    // 退出状态
    EXITED_DOZE,           // 已退出 Doze
}

┌─────────────────────────────────────────────────────────────────────────────┐
│  状态转换图                                                                │
└─────────────────────────────────────────────────────────────────────────────┘

                          ┌──────────────┐
                          │  DOZE_INIT   │
                          └──────┬───────┘
                                 │
                                 ▼
         ┌───────────────────────┴───────────────────────┐
         │                                               │
         ▼                                               ▼
  ┌──────────────┐                              ┌──────────────┐
  │     DOZE     │◀─────────────────────────────│   DOZE_AOD   │
  │  (深度睡眠)  │                              │  (AOD模式)   │
  └──────┬───────┘                              └──────┬───────┘
         │                                             │
         │                                             │
         │    ┌────────────────────────────────────────┤
         │    │                                        │
         │    ▼                                        ▼
         │  ┌──────────────┐                    ┌──────────────┐
         │  │DOZE_REQUEST_ │                    │  DOZE_REST   │
         │  │    PULSE     │                    │  (浅睡眠)    │
         │  └──────┬───────┘                    └──────┬───────┘
         │         │                                   │
         │         ▼                                   │
         │  ┌──────────────┐                          │
         │  │DOZE_PULSE_   │                          │
         │  │    START     │                          │
         │  └──────┬───────┘                          │
         │         │                                   │
         │         ▼                                   │
         │  ┌──────────────┐                          │
         └─▶│DOZE_PULSE_   │◀─────────────────────────┘
            │    DONE      │
            └──────┬───────┘
                   │
                   ▼
          ┌──────────────┐
          │ EXITED_DOZE  │
          │  (退出Doze)  │
          └──────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  状态转换触发条件                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

进入 DOZE_AOD:
├── 屏幕关闭超时
├── 用户触发 AOD（设置已开启）
├── 传感器检测到设备静止
└── 充电时

从 DOZE_AOD 进入 DOZE_REST (脉冲):
├── 通知到达
├── 定时更新（每分钟）
├── 传感器事件
├── 电池状态变化
└── 时间变化

从 DOZE_AOD 进入 DOZE (深度睡眠):
├── AOD 超时（设备长时间静止）
├── 低电量
├── 口袋模式检测
└── 用户关闭 AOD

退出 Doze (EXITED_DOZE):
├── 用户触控屏幕
├── 按下电源键
├── 来电
├── 闹钟响铃
└── 拿起设备（传感器检测）

┌─────────────────────────────────────────────────────────────────────────────┐
│  脉冲 (Pulse) 机制                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

脉冲是 AOD 的短暂唤醒，用于更新显示内容

脉冲原因 (PulseReason):
├── PULSE_REASON_NOTIFICATION  - 新通知到达
├── PULSE_REASON_SENSOR        - 传感器触发
├── PULSE_REASON_TAP           - 用户点击
├── PULSE_REASON_LONG_TAP      - 用户长按
├── PULSE_REASON_WAKE_DISPLAY  - 唤醒显示
└── PULSE_REASON_TIMER         - 定时器

脉冲流程:
1. 触发脉冲请求
   └── transitionTo(DOZE_REQUEST_PULSE)

2. 开始脉冲
   └── transitionTo(DOZE_PULSE_START)

3. 显示脉冲内容
   ├── 通知脉冲：显示通知内容
   ├── 时间脉冲：更新时钟
   └── 传感器脉冲：显示唤醒动画

4. 脉冲完成
   └── transitionTo(DOZE_PULSE_DONE)

5. 返回 AOD 或 Doze
   └── transitionTo(DOZE_AOD) 或 transitionTo(DOZE)

┌─────────────────────────────────────────────────────────────────────────────┐
│  AOD 防烧屏 (Burn-in Protection)                                           │
└─────────────────────────────────────────────────────────────────────────────┘

AMOLED 屏幕长时间显示同一图像会导致烧屏，AOD 使用以下策略防止烧屏:

1. 位置偏移
   - AOD 内容定期微移位置
   - 偏移范围：±10 像素
   - 偏移间隔：每分钟

2. 亮度降低
   - AOD 亮度远低于正常亮度
   - 根据环境光调整

3. 内容轮换
   - 时钟位置变化
   - 通知图标位置变化

4. 定时关闭
   - 长时间静止后关闭 AOD
   - 设备放入口袋后关闭
```

### 10.4 面试常见问题

**Q1: 通知从 App 发送到 SystemUI 显示的完整流程？**

**A:**

```
1. App 创建 Notification
   └── Notification.Builder.build()

2. App 调用 NotificationManager.notify()
   └── Binder IPC 调用 NMS

3. NMS 处理通知
   ├── 创建 NotificationRecord
   ├── 应用过滤和排名
   ├── 持久化通知
   └── 回调 NotificationListenerService

4. SystemUI 接收通知
   ├── NotificationListenerService.onNotificationPosted()
   ├── NotificationEntryManager 创建 NotificationEntry
   └── 提取 RemoteViews

5. SystemUI 渲染通知
   ├── RemoteViews.apply() 展开为 View
   ├── 添加到 NotificationStackScrollLayout
   └── 更新状态栏图标
```

**Q2: RemoteViews 为什么不能使用自定义 View？**

**A:**

```
原因:
1. 安全性：RemoteViews 跨进程传递，使用自定义 View 可能带来安全风险
2. 兼容性：不同应用的 View 实现可能不同
3. 性能：跨进程加载自定义 View 开销大
4. 序列化：自定义 View 可能包含无法序列化的状态

支持的 View 类型：
- 布局容器：FrameLayout, LinearLayout, RelativeLayout, GridLayout
- 基础视图：TextView, ImageView, Button, ProgressBar
- 特殊视图：Chronometer, ViewFlipper
```

**Q3: 为什么 SystemUI 通知列表使用 NotificationStackScrollLayout（自定义 ViewGroup）而不是 RecyclerView？**

**A:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│    通知列表的布局选择：NotificationStackScrollLayout vs RecyclerView        │
└─────────────────────────────────────────────────────────────────────────────┘

NotificationStackScrollLayout 继承自 FrameLayout，
不是 RecyclerView，这是经过深思熟虑的设计决策。

┌─────────────────────────────────────────────────────────────────────────────┐
│  原因 1：通知数量极少，不需要 ViewHolder 复用                               │
└─────────────────────────────────────────────────────────────────────────────┘

RecyclerView 的核心优势是 ViewHolder 复用，适合大数据量列表:
├── RecyclerView 设计目标：成百上千条数据
├── 通知面板实际数量：通常 5-20 条，极端情况不超过 50 条
├── ViewHolder 复用在通知场景收益极小
└── 通知 View 之间差异大（不同模板、不同高度），复用反而增加复杂度

┌─────────────────────────────────────────────────────────────────────────────┐
│  原因 2：复杂的堆叠和交互动画，FrameLayout 天然支持                          │
└─────────────────────────────────────────────────────────────────────────────┘

通知面板有非常特殊的视觉交互:

  ┌─────────────────────┐
  │ 最新通知 (完全可见)   │  ← y 偏移 = 0
  ├─────────────────────┤
  │ 通知 2 (部分可见)    │  ← y 偏移 = -100px，被上面遮挡
  │  ┌─────────────────┐│
  │  │ 通知 3 (只露顶) ││  ← y 偏移 = -200px
  │  │  ┌─────────────┐││
  │  │  │  通知 4 ... │││
  │  │  └─────────────┘││
  │  └─────────────────┘│
  └─────────────────────┘

这种"堆叠"效果需要:
├── 每个子 View 可以有任意的 translationY / translationZ
├── 子 View 之间有重叠（overlap）
├── 子 View 可以有独立的高度（elevation）阴影
├── 展开/折叠时子 View 的位移是连续动画
└── FrameLayout 允许子 View 自由定位和重叠，LinearLayout 不行

RecyclerView 的局限:
├── RecyclerView 强制线性排列（LinearLayoutManager）
├── Item 之间不能重叠
├── 自定义 LayoutController 可以实现，但代价很大
├── 动画系统（ItemAnimator）不适合通知的堆叠动画
└── 需要大量 hack 才能达到 NotificationStackScrollLayout 的效果

┌─────────────────────────────────────────────────────────────────────────────┐
│  原因 3：每条通知高度不固定且可动态变化                                       │
└─────────────────────────────────────────────────────────────────────────────┘

通知 View 的高度在运行时频繁变化:
├── 展开/折叠切换 → 高度突变
├── 智能回复按钮展开 → 高度增加
├── 进度条通知 → 高度固定但内容更新
├── 图片通知 → 大图展开/收起
└── 通知组展开/折叠 → 子通知动态添加/移除

RecyclerView 的挑战:
├── 高度变化需要 notifyItemChanged → 触发重新 measure/layout
├── 动态高度变化会导致其他 Item 抖动
├── 需要手动管理 span size、view type
└── 复杂度远超直接使用 FrameLayout + 手动布局

NotificationStackScrollLayout 的方案:
├── 每条通知是一个独立的 ExpandableNotificationRow (FrameLayout)
├── 自行管理所有子 View 的 measure/layout
├── 重写 onMeasure() 和 onLayout() 实现堆叠算法
├── 高度变化通过 ValueAnimator 平滑过渡
└── 完全掌控每个子 View 的位置和大小

┌─────────────────────────────────────────────────────────────────────────────┐
│  原因 4：复杂的手势交互                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

通知面板的手势远比普通列表复杂:

├── 单条通知滑动删除（swipe to dismiss）
├── 下拉展开通知详情
├── 通知之间的速度追踪和惯性
├── "锁屏" 和 "通知面板" 的手势冲突处理
├── 双指操作（展开/折叠通知组）
├── 触摸事件的精确分发（通知内部按钮 vs 整体滑动）
└── 长按进入通知设置

RecyclerView 的 ItemTouchHelper 处理不了:
├── ItemTouchHelper 支持简单的滑动/拖拽
├── 但通知需要"滑动到一半弹回"（snooze）
├── 滑动过程中显示底层的 snooze/time 按钮
├── 这种交互需要完全自定义的触摸事件处理
└── NotificationStackScrollLayout 直接处理 onTouchEvent

┌─────────────────────────────────────────────────────────────────────────────┐
│  原因 5：性能考量                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

实际性能对比:

RecyclerView:
├── 每次 scroll → 需要计算 ViewHolder 复用
├── 滑动时持续 inflate/deatch/recycle
├── 对 5-20 条通知来说，管理开销 > 收益
└── Adapter、LayoutController、Recycler 多层抽象有额外开销

NotificationStackScrollLayout:
├── 所有通知 View 始终在 View 树中
├── 滑动只是修改 translationY，不需要 inflate/deatch
├── 直接操作 Canvas 绘制，减少过度绘制
├── 利用硬件加速的 translationZ 实现阴影
└── 通知数量少时，直接布局比 ViewHolder 复用更快

┌─────────────────────────────────────────────────────────────────────────────┐
│  总结                                                                       │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────────┐
                    │     RecyclerView 适合:        │
                    │  ✓ 数据量大 (100+)            │
                    │  ✓ Item 布局统一              │
                    │  ✓ 线性排列，无重叠            │
                    │  ✓ 简单手势                   │
                    └──────────────────────────────┘
                                vs
                    ┌──────────────────────────────┐
                    │  通知面板实际需求:             │
                    │  ✗ 数据量小 (5-20)            │
                    │  ✗ Item 布局差异大            │
                    │  ✗ 需要堆叠/重叠效果          │
                    │  ✗ 复杂手势交互               │
                    └──────────────────────────────┘

结论：NotificationStackScrollLayout (FrameLayout) 是更合适的选择。
      RecyclerView 在通知面板场景下没有优势，反而增加了复杂度。
      这也是 SystemUI 团队从 Android 4.x 开始就使用自定义 ViewGroup 的原因。
```

**Q4: AOD 是如何实现低功耗的？**

**A:**

```
硬件层面:
1. AMOLED 屏幕可单独点亮像素
2. Display HAL 支持 AOD 模式
3. 低刷新率（1fps）

软件层面:
1. DozeMachine 状态机控制
2. 定时脉冲更新（减少唤醒次数）
3. 防烧屏机制（位置偏移）
4. 传感器辅助（口袋模式检测）
```

**Q5: 通知渠道 (NotificationChannel) 的作用？**

**A:**

```
作用:
1. 分类管理：将通知按类型分组
2. 用户控制：用户可独立控制每类通知
3. 重要性级别：决定通知的显示方式
4. 统一管理：同一渠道的通知统一配置

属性:
- ID：唯一标识
- 名称：用户可见
- 重要性：IMPORTANCE_NONE 到 IMPORTANCE_MAX
- 声音、振动、灯光
- 是否显示角标
```

---

## 13. Keyguard 锁屏系统

> 本节内容基于 **Android 16 (API 36)** 源码分析
> 源码路径：`frameworks/base/packages/SystemUI/src/com/android/keyguard/`

### 13.1 Keyguard 概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Keyguard 锁屏系统概述 (Android 16)                     │
└─────────────────────────────────────────────────────────────────────────────┘

Keyguard 是 Android 系统的锁屏实现，负责：
1. 设备安全保护（防止未授权访问）
2. 安全验证（图案/密码/PIN/生物识别）
3. 锁屏界面显示（时间、通知、快捷设置）
4. 与 SystemUI 的状态同步

┌─────────────────────────────────────────────────────────────────────────────┐
│                 Android 16 Keyguard 分层架构                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          View Layer (视图层)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KeyguardSecurityContainer                        │   │
│  │  ├── PatternKeyguardView    (图案解锁)                              │   │
│  │  ├── PasswordKeyguardView    (密码解锁)                              │   │
│  │  ├── PINKeyguardView         (PIN 解锁)                              │   │
│  │  ├── KeyguardSimPinView      (SIM PIN)                               │   │
│  │  └── KeyguardSimPukView      (SIM PUK)                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KeyguardStatusView (状态视图)                      │   │
│  │  ├── 时钟显示 (KeyguardClockSwitch)                                  │   │
│  │  ├── 日期显示                                                        │   │
│  │  ├── 电量显示                                                        │   │
│  │  └── 运营商信息 (CarrierText)                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Controller Layer (控制器层)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KeyguardViewController                           │   │
│  │  - 视图生命周期管理                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KeyguardSecurityContainerController               │   │
│  │  - 安全模式切换                                                      │   │
│  │  - 验证流程控制                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    *ViewController (各视图控制器)                     │   │
│  │  - PatternKeyguardViewController                                    │   │
│  │  - PasswordKeyguardViewController                                   │   │
│  │  - PinViewController                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Model Layer (模型层)                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KeyguardUpdateMonitor (核心)                      │   │
│  │  - 系统状态监控 (SIM/电池/时间/安全)                                 │   │
│  │  - 状态变化通知                                                      │   │
│  │  - 回调管理 (KeyguardUpdateMonitorCallback)                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KeyguardSecurityModel                            │   │
│  │  - 安全模式定义 (None/PIN/Pattern/Password)                         │   │
│  │  - 安全级别判断                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Domain Layer (业务逻辑层) [Android 16 新增]            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    domain/interactor/                                │   │
│  │  - KeyguardKeyboardInteractor (键盘显示逻辑)                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DI Layer (依赖注入层) [Dagger]                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    dagger/                                           │   │
│  │  - KeyguardBouncerComponent                                         │   │
│  │  - KeyguardBouncerModule                                            │   │
│  │  - KeyguardStatusViewComponent                                      │   │
│  │  - KeyguardDisplayModule                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Logging Layer (日志层) [Android 16 新增]               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    logging/                                          │   │
│  │  - KeyguardLogger (核心日志)                                        │   │
│  │  - BiometricUnlockLogger (生物识别日志)                             │   │
│  │  - KeyguardTransitionAnimationLogger (转场动画日志)                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 13.2 Keyguard 源码目录结构 (Android 16)

```
frameworks/base/packages/SystemUI/src/com/android/keyguard/
├── KeyguardUpdateMonitor.java          # 核心状态监控器
├── KeyguardUpdateMonitorCallback.java  # 状态变化回调
├── KeyguardViewController.java         # 视图控制器接口
├── KeyguardSecurityModel.java          # 安全模式模型
├── KeyguardSecurityCallback.java       # 安全验证回调
├── KeyguardDisplayManager.java         # 显示管理器
│
├── security/                           # 安全验证视图
│   ├── KeyguardSecurityContainer.java
│   ├── KeyguardSecurityContainerController.java
│   ├── KeyguardSecurityView.java
│   ├── KeyguardSecurityViewFlipper.java
│   └── KeyguardSecurityViewTransition.kt
│
├── PinShapeAdapter.kt                  # PIN 形状适配器
├── PinShapeHintingView.java            # PIN 提示视图
├── NumPadKey.java                      # 数字键盘按键
├── NumPadButton.java                   # 数字按钮
├── NumPadAnimator.java                 # 按键动画
│
├── dagger/                             # Dagger 依赖注入
│   ├── KeyguardBouncerComponent.java
│   ├── KeyguardBouncerModule.java
│   ├── KeyguardBouncerScope.java
│   └── KeyguardDisplayModule.kt
│
├── domain/interactor/                  # 业务逻辑层 [新增]
│   └── KeyguardKeyboardInteractor.kt
│
├── logging/                            # 日志模块 [新增]
│   ├── KeyguardLogger.kt
│   ├── BiometricUnlockLogger.kt
│   └── KeyguardTransitionAnimationLogger.kt
│
└── mediator/                           # 协调器
    └── ScreenOnCoordinator.kt
```

### 13.3 Keyguard 启动流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Keyguard 启动流程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

SystemServer 启动:
│
├── 1. SystemServer.startOtherServices()
│   │
│   ├── WindowManagerService.onDisplayReady()
│   │   │
│   │   └── mPolicy.onDisplayReady()
│   │       │
│   │       └── PhoneWindowManager.onDisplayReady()
│   │           │
│   │           └── KeyguardViewMediator.onSystemReady()
│   │
│   └── KeyguardViewMediator 开始工作
│
├── 2. KeyguardViewMediator.onSystemReady()
│   │
│   ├── 读取锁屏配置
│   │   mLockPatternUtils.isSecure()  // 是否设置安全锁
│   │
│   ├── 读取设备策略
│   │   mDevicePolicyManager.getPasswordQuality()
│   │
│   └── 通知状态变化
│       mUpdateMonitor.registerCallback(mCallback)
│
├── 3. SystemUI KeyguardService 绑定
│   │
│   ├── KeyguardService.bindService()
│   │   Intent intent = new Intent(KeyguardService.ACTION_BIND_SERVICE);
│   │   mContext.bindService(intent, mConnection, Context.BIND_AUTO_CREATE);
│   │
│   └── KeyguardService.onCreate()
│       ├── 创建 KeyguardViewMediator
│       └── 初始化 KeyguardUpdateMonitor
│
└── 4. Keyguard 界面创建
    │
    ├── KeyguardBouncer.show()
    │   ├── inflateView()  // 加载锁屏视图
    │   └── showPrimaryBouncer()  // 显示安全验证
    │
    └── KeyguardHostView.onFinishInflate()
        ├── 初始化状态栏
        ├── 初始化时钟
        └── 初始化安全容器
```

### 13.3 KeyguardViewMediator 源码分析

```java
/**
 * KeyguardViewMediator - 锁屏中介器
 * 位置：frameworks/base/packages/SystemUI/src/com/android/keyguard/
 */

public class KeyguardViewMediator extends SystemUI {

    // 锁屏状态
    private boolean mShowing;
    private boolean mOccluded;      // 被其他应用遮挡
    private boolean mSecure;        // 是否需要安全验证
    private boolean mScreenOn;      // 屏幕是否开启

    // 核心组件
    private KeyguardUpdateMonitor mUpdateMonitor;
    private KeyguardBouncer mBouncer;
    private KeyguardLifecyclesObserver mLifecyclesObserver;

    // 状态回调
    private final KeyguardUpdateMonitorCallback mCallback =
        new KeyguardUpdateMonitorCallback() {

        @Override
        public void onScreenTurnedOff() {
            mScreenOn = false;
            // 屏幕关闭时显示锁屏
            if (shouldShowLockScreen()) {
                showLocked(null);
            }
        }

        @Override
        public void onScreenTurnedOn() {
            mScreenOn = true;
            notifyScreenOnChanged();
        }

        @Override
        public void onUserSwitchComplete(int userId) {
            // 用户切换时重置锁屏
            resetStateLocked();
        }

        @Override
        public void onKeyguardVisibilityChanged(boolean showing) {
            if (showing) {
                // 锁屏显示时播放动画
                mBouncer.show(false /* resetSecuritySelection */);
            }
        }

        @Override
        public void onTrustGranted(boolean newlyAcquired) {
            // 信任授权（如可信设备）
            if (newlyAcquired && mShowing) {
                dismissKeyguard();
            }
        }
    };

    /**
     * 显示锁屏
     */
    public void showLocked(Bundle options) {
        synchronized (this) {
            // 1. 检查是否需要显示
            if (!mSystemReady || mShowing) {
                return;
            }

            // 2. 设置显示状态
            mShowing = true;

            // 3. 更新状态
            mUpdateMonitor.reportKeyguardShowing(true);

            // 4. 显示 Bouncer
            mHandler.post(() -> {
                playSounds(true);  // 播放锁屏音效
                mBouncer.show(true /* resetSecuritySelection */);
            });

            // 5. 通知状态变化
            notifyKeyguardStateChanged();
        }
    }

    /**
     * 隐藏锁屏（解锁成功后）
     */
    public void hideLocked() {
        synchronized (this) {
            // 1. 检查是否可以隐藏
            if (!mShowing) {
                return;
            }

            // 2. 验证是否允许解锁
            if (!mUpdateMonitor.canDismissKeyguard()) {
                return;
            }

            // 3. 设置隐藏状态
            mShowing = false;

            // 4. 隐藏 Bouncer
            mHandler.post(() -> {
                playSounds(false);  // 播放解锁音效
                mBouncer.hide();
            });

            // 5. 通知状态变化
            notifyKeyguardStateChanged();
        }
    }

    /**
     * 尝试解锁
     */
    public void dismissKeyguard() {
        synchronized (this) {
            // 1. 检查是否允许解锁
            if (!mSecure) {
                // 无安全锁，直接解锁
                hideLocked();
                return;
            }

            // 2. 检查信任状态
            if (mUpdateMonitor.getUserTrustIsManaged()) {
                // 信任设备，直接解锁
                hideLocked();
                return;
            }

            // 3. 需要安全验证
            mBouncer.show(true /* resetSecuritySelection */);
        }
    }

    /**
     * 验证成功回调
     */
    public void onPasswordChecked(boolean success, int timeoutMs) {
        if (success) {
            // 验证成功，隐藏锁屏
            hideLocked();
        } else {
            // 验证失败，显示错误提示
            mBouncer.showTimeout();

            // 延迟后允许重试
            mHandler.postDelayed(() -> {
                mBouncer.reset();
            }, timeoutMs);
        }
    }
}
```

### 13.4 KeyguardUpdateMonitor 状态管理

```java
/**
 * KeyguardUpdateMonitor - 锁屏状态监听器
 * 位置：frameworks/base/packages/SystemUI/src/com/android/keyguard/
 */

public class KeyguardUpdateMonitor {

    // 状态标志
    private boolean mDeviceInteractive;     // 设备是否可交互
    private boolean mScreenOn;              // 屏幕是否开启
    private boolean mKeyguardShowing;       // 锁屏是否显示
    private boolean mBouncerShowing;        // 安全验证是否显示

    // 安全状态
    private int mFailedPasswordAttempts;    // 密码尝试失败次数
    private boolean mStrongAuthRequired;    // 是否需要强认证
    private boolean mTrustManaged;          // 是否信任设备

    // 回调列表
    private final ArrayList<KeyguardUpdateMonitorCallback> mCallbacks =
        new ArrayList<>();

    /**
     * 注册回调
     */
    public void registerCallback(KeyguardUpdateMonitorCallback callback) {
        synchronized (mCallbacks) {
            mCallbacks.add(callback);
        }
    }

    /**
     * 报告锁屏显示状态
     */
    public void reportKeyguardShowing(boolean showing) {
        if (mKeyguardShowing != showing) {
            mKeyguardShowing = showing;
            notifyKeyguardVisibilityChanged();
        }
    }

    /**
     * 报告安全验证结果
     */
    public void reportSuccessfulAuthentication() {
        // 1. 重置失败计数
        mFailedPasswordAttempts = 0;

        // 2. 清除强认证要求
        mStrongAuthRequired = false;

        // 3. 通知回调
        for (KeyguardUpdateMonitorCallback callback : mCallbacks) {
            callback.onStrongAuthStateChanged(false);
        }
    }

    /**
     * 报告安全验证失败
     */
    public void reportFailedAuthentication() {
        // 1. 增加失败计数
        mFailedPasswordAttempts++;

        // 2. 检查是否需要锁定
        int maxAttempts = getMaxFailedPasswordAttempts();
        if (mFailedPasswordAttempts >= maxAttempts) {
            // 达到最大尝试次数，锁定设备
            lockDevice();
        }

        // 3. 通知回调
        for (KeyguardUpdateMonitorCallback callback : mCallbacks) {
            callback.onFailedAuthenticationAttempt();
        }
    }

    /**
     * 检查是否可以解锁
     */
    public boolean canDismissKeyguard() {
        // 1. 无安全锁
        if (!isSecure()) {
            return true;
        }

        // 2. 信任设备
        if (mTrustManaged) {
            return true;
        }

        // 3. 生物识别已验证
        if (mBiometricAuthenticated) {
            return true;
        }

        return false;
    }

    // 内部监听器
    private final BroadcastReceiver mBroadcastReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();

            if (Intent.ACTION_TIME_TICK.equals(action)) {
                // 时间变化
                handleTimeTick();
            } else if (Intent.ACTION_BATTERY_CHANGED.equals(action)) {
                // 电池状态变化
                handleBatteryUpdate(intent);
            } else if (TelephonyManager.ACTION_SIM_CARD_STATE_CHANGED.equals(action)) {
                // SIM 卡状态变化
                handleSimStateChange(intent);
            }
        }
    };

    private void handleTimeTick() {
        for (KeyguardUpdateMonitorCallback callback : mCallbacks) {
            callback.onTimeChanged();
        }
    }
}
```

### 13.5 安全验证机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       安全验证机制                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  安全验证类型                                                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────────────────┐
│      类型        │                       说明                              │
├──────────────────┼──────────────────────────────────────────────────────────┤
│  Pattern         │  图案解锁（3x3 点阵）                                   │
│  PIN             │  PIN 码解锁（4-16 位数字）                               │
│  Password        │  密码解锁（4-16 位字符）                                 │
│  Fingerprint     │  指纹解锁                                               │
│  Face            │  人脸解锁                                               │
│  Iris            │  虹膜解锁                                               │
└──────────────────┴──────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  验证流程图                                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

用户触发解锁:
│
├── 1. 选择验证方式
│   KeyguardSecurityContainer.showSecurityScreen(mode)
│   │
│   ├── Pattern  → PatternKeyguardView
│   ├── PIN      → PINKeyguardView
│   ├── Password → PasswordKeyguardView
│   └── Biometric→ BiometricKeyguardView
│
├── 2. 用户输入
│   ├── 图案：绘制 3x3 点阵
│   ├── PIN：输入数字
│   ├── 密码：输入字符
│   └── 生物识别：扫描指纹/人脸
│
├── 3. 验证
│   KeyguardSecurityView.verifyPassword(password)
│   │
│   ├── LockPatternUtils.checkPattern(pattern)
│   ├── LockPatternUtils.checkPassword(password)
│   └── BiometricManager.authenticate()
│
├── 4. 验证结果
│   │
│   ├── 成功
│   │   ├── mUpdateMonitor.reportSuccessfulAuthentication()
│   │   └── mMediator.onPasswordChecked(true, 0)
│   │       └── hideLocked()  // 隐藏锁屏
│   │
│   └── 失败
│       ├── mUpdateMonitor.reportFailedAuthentication()
│       └── mMediator.onPasswordChecked(false, timeout)
│           ├── 显示错误提示
│           └── 延迟后允许重试
│
└── 5. 更新统计
    mLockSettingsService.reportSuccessfulAuthentication()
```

### 13.6 图案解锁源码分析

```java
/**
 * PatternKeyguardView - 图案解锁视图
 * 位置：frameworks/base/packages/SystemUI/src/com/android/keyguard/
 */

public class PatternKeyguardView extends KeyguardSecurityView {

    private LockPatternView mLockPatternView;
    private KeyguardUpdateMonitor mUpdateMonitor;
    private LockPatternUtils mLockPatternUtils;

    // 图案状态
    private enum PatternState {
        STATE_INPUT,       // 输入中
        STATE_CHECKING,    // 验证中
        STATE_SUCCESS,     // 验证成功
        STATE_FAILED,      // 验证失败
    }

    /**
     * 图案绘制监听
     */
    private LockPatternView.OnPatternListener mPatternListener =
        new LockPatternView.OnPatternListener() {

        @Override
        public void onPatternStart() {
            // 开始绘制图案
            mLockPatternView.removeCallbacks(mResetPatternRunnable);
            mLockPatternView.setDisplayMode(DisplayMode.Correct);
        }

        @Override
        public void onPatternCleared() {
            // 图案清除
            mLockPatternView.removeCallbacks(mResetPatternRunnable);
        }

        @Override
        public void onPatternCellAdded(List<Cell> pattern) {
            // 添加一个点
            // 播放触觉反馈
            performHapticFeedback();
        }

        @Override
        public void onPatternDetected(List<Cell> pattern) {
            // 图案绘制完成
            verifyPattern(pattern);
        }
    };

    /**
     * 验证图案
     */
    private void verifyPattern(List<Cell> pattern) {
        // 1. 显示验证中状态
        mLockPatternView.setEnabled(false);
        setState(STATE_CHECKING);

        // 2. 异步验证
        new AsyncTask<List<Cell>, Void, Boolean>() {
            @Override
            protected Boolean doInBackground(List<Cell>... patterns) {
                return mLockPatternUtils.checkPattern(patterns[0]);
            }

            @Override
            protected void onPostExecute(Boolean success) {
                if (success) {
                    // 验证成功
                    setState(STATE_SUCCESS);
                    mLockPatternView.setDisplayMode(DisplayMode.Correct);

                    // 通知验证成功
                    mUpdateMonitor.reportSuccessfulAuthentication();
                    mCallback.reportUnlockAttempt(true, 0);

                    // 解锁
                    mCallback.dismiss(true, KeyguardUpdateMonitor.getCurrentUser());
                } else {
                    // 验证失败
                    setState(STATE_FAILED);
                    mLockPatternView.setDisplayMode(DisplayMode.Wrong);

                    // 通知验证失败
                    mUpdateMonitor.reportFailedAuthentication();
                    mCallback.reportUnlockAttempt(false, 0);

                    // 显示错误提示
                    showError(getString(R.string.kg_wrong_pattern));

                    // 延迟后重置
                    mLockPatternView.postDelayed(mResetPatternRunnable, 2000);
                }
            }
        }.execute(pattern);
    }

    // 重置图案
    private final Runnable mResetPatternRunnable = () -> {
        mLockPatternView.clearPattern();
        mLockPatternView.setEnabled(true);
        setState(STATE_INPUT);
    };
}
```

### 13.7 生物识别解锁

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       生物识别解锁                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  生物识别类型                                                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────────────────┐
│      类型        │                       说明                              │
├──────────────────┼──────────────────────────────────────────────────────────┤
│  Fingerprint     │  指纹识别（Android 6.0+）                                │
│  Face            │  人脸识别（Android 10+）                                 │
│  Iris            │  虹膜识别（Android 10+）                                 │
└──────────────────┴──────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  生物识别架构                                                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          Framework 层                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    BiometricManager                                  │   │
│  │  - 生物识别能力查询                                                  │   │
│  │  - 认证请求调度                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    BiometricService                                  │   │
│  │  - 生物识别服务管理                                                  │   │
│  │  - 认证流程控制                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HAL 层                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Biometric HAL                                     │   │
│  │  - IBiometricsFingerprint                                           │   │
│  │  - IFace                                                            │   │
│  │  - IIris                                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

```java
/**
 * BiometricKeyguardView - 生物识别解锁视图
 * 位置：frameworks/base/packages/SystemUI/src/com/android/keyguard/
 */

public class BiometricKeyguardView extends KeyguardSecurityView {

    private BiometricManager mBiometricManager;
    private BiometricPrompt mBiometricPrompt;
    private KeyguardUpdateMonitor mUpdateMonitor;

    /**
     * 初始化生物识别
     */
    public void initializeBiometric() {
        // 1. 检查生物识别能力
        int result = mBiometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG);

        if (result == BiometricManager.BIOMETRIC_SUCCESS) {
            // 2. 创建 BiometricPrompt
            mBiometricPrompt = new BiometricPrompt(
                mContext,
                ContextCompat.getMainExecutor(mContext),
                mAuthenticationCallback
            );

            // 3. 配置提示信息
            PromptInfo promptInfo = new BiometricPrompt.PromptInfo.Builder()
                .setTitle("解锁设备")
                .setSubtitle("使用生物识别解锁")
                .setNegativeButtonText("使用密码")
                .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                .build();
        }
    }

    /**
     * 开始生物识别认证
     */
    public void startAuthentication() {
        if (mBiometricPrompt != null) {
            mBiometricPrompt.authenticate(promptInfo);
        }
    }

    /**
     * 认证回调
     */
    private BiometricPrompt.AuthenticationCallback mAuthenticationCallback =
        new BiometricPrompt.AuthenticationCallback() {

        @Override
        public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult result) {
            // 认证成功
            mUpdateMonitor.reportSuccessfulAuthentication();
            mCallback.dismiss(true, KeyguardUpdateMonitor.getCurrentUser());
        }

        @Override
        public void onAuthenticationFailed() {
            // 认证失败（可重试）
            showError("识别失败，请重试");
        }

        @Override
        public void onAuthenticationError(int errorCode, CharSequence errString) {
            // 认证错误
            switch (errorCode) {
                case BiometricPrompt.ERROR_LOCKOUT:
                    // 锁定，需要使用其他方式解锁
                    mCallback.switchToSecurityView(SECURITY_PASSWORD);
                    break;
                case BiometricPrompt.ERROR_CANCELED:
                    // 取消认证
                    break;
                case BiometricPrompt.ERROR_TIMEOUT:
                    // 超时
                    showError("认证超时");
                    break;
            }
        }
    };
}
```

### 13.8 锁屏与 SystemUI 交互

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       锁屏与 SystemUI 交互                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  交互场景                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

场景 1: 通知显示在锁屏
│
├── 1.1 通知到达
│   NMS → NotificationListenerService → NotificationEntryManager
│
├── 1.2 检查锁屏状态
│   if (KeyguardUpdateMonitor.isKeyguardShowing()) {
│       // 在锁屏上显示通知
│   }
│
├── 1.3 通知可见性控制
│   ├── 公开通知：锁屏上完整显示
│   ├── 私密通知：锁屏上隐藏内容
│   └── 隐藏通知：锁屏上不显示
│
└── 1.4 锁屏通知渲染
    KeyguardNotificationView.bindNotification(entry)

场景 2: 锁屏快捷设置
│
├── 2.1 下拉状态栏（锁屏状态）
│   StatusBar.expandNotificationsPanel()
│
├── 2.2 检查权限
│   if (KeyguardUpdateMonitor.canPerformLockScreenActions()) {
│       // 允许操作快捷设置
│   }
│
└── 2.3 快捷设置操作
    ├── 开关 Wi-Fi
    ├── 开关蓝牙
    ├── 调节亮度
    └── 切换铃声模式

场景 3: 电源键锁屏
│
├── 3.1 按下电源键
│   PowerManagerService.goToSleep()
│
├── 3.2 屏幕关闭
│   DisplayManagerService.onScreenTurnedOff()
│
├── 3.3 显示锁屏
│   KeyguardViewMediator.showLocked()
│
└── 3.4 锁屏状态通知
    KeyguardUpdateMonitor.reportKeyguardShowing(true)

场景 4: 解锁后恢复
│
├── 4.1 验证成功
│   KeyguardViewMediator.onPasswordChecked(true, 0)
│
├── 4.2 隐藏锁屏
│   KeyguardViewMediator.hideLocked()
│
├── 4.3 恢复应用状态
│   ├── Activity 恢复
│   ├── 通知可交互
│   └── 快捷设置完全可用
│
└── 4.4 状态同步
    StatusBar.onKeyguardStateChanged(false)
```

### 13.9 Keyguard 状态机

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Keyguard 状态机                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  状态定义                                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

enum KeyguardState {
    STATE_HIDE,              // 隐藏（已解锁）
    STATE_SHOW,              // 显示锁屏
    STATE_BOUNCER,           // 显示安全验证
    STATE_OCCLUDED,          // 被遮挡（如来电）
    STATE_SLEEP,             // 睡眠状态
}

┌─────────────────────────────────────────────────────────────────────────────┐
│  状态转换图                                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │  STATE_SLEEP │
                         │   (睡眠)     │
                         └──────┬───────┘
                                │ 屏幕亮起
                                ▼
         ┌──────────────────────┴──────────────────────┐
         │                                             │
         ▼                                             ▼
  ┌──────────────┐                              ┌──────────────┐
  │  STATE_SHOW  │◀─────────────────────────────│STATE_OCCLUDED│
  │  (显示锁屏)  │       遮挡结束                │  (被遮挡)    │
  └──────┬───────┘                              └──────────────┘
         │                                             ▲
         │ 需要验证                                    │
         ▼                                             │
  ┌──────────────┐                                     │
  │STATE_BOUNCER │─────────────────────────────────────┘
  │ (安全验证)   │            来电等遮挡
  └──────┬───────┘
         │
         │ 验证成功
         ▼
  ┌──────────────┐
  │  STATE_HIDE  │
  │   (已解锁)   │
  └──────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  状态转换触发条件                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

STATE_SLEEP → STATE_SHOW:
├── 屏幕亮起
├── 电源键按下
└── 通知唤醒

STATE_SHOW → STATE_BOUNCER:
├── 用户上滑
├── 需要安全验证
└── 生物识别失败

STATE_BOUNCER → STATE_HIDE:
├── 验证成功
├── 信任设备
└── Smart Lock 解锁

STATE_SHOW/STATE_BOUNCER → STATE_OCCLUDED:
├── 来电
├── 闹钟响铃
└── 全屏 Intent

STATE_OCCLUDED → STATE_SHOW:
├── 来电结束
├── 闹钟关闭
└── 全屏 Activity 退出

任何状态 → STATE_SLEEP:
├── 屏幕超时
├── 电源键按下
└── 主动休眠
```

### 13.10 锁屏安全最佳实践

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       锁屏安全最佳实践                                       │
└─────────────────────────────────────────────────────────────────────────────┘

1. 密码强度要求
├── 图案：至少 4 个点
├── PIN：至少 4 位数字
├── 密码：至少 4 位字符
└── 建议：使用复杂密码

2. 尝试限制
├── 5 次失败后：延迟 30 秒
├── 10 次失败后：延迟 60 秒
├── 30 次失败后：恢复出厂设置警告
└── 企业策略：可能更严格

3. 强认证要求
├── 设备重启后
├── 72 小时未验证
├── 添加新指纹后
└── 企业策略触发

4. 通知隐私
├── 敏感通知隐藏内容
├── 使用 Visibility 特性
└── 公开版本显示摘要

5. 生物识别注意事项
├── 不如密码安全
├── 可能被强制解锁
├── 设置备用密码
└── 定期更新生物数据

6. 设备管理
├── 启用 Find My Device
├── 设置远程锁定
├── 定期备份
└── 敏感数据加密
```

---

## 14. Keyguard 面试常见问题

> 本节补充 Keyguard 锁屏系统相关的面试问题

### 14.1 Keyguard 启动与验证

**Q1: Keyguard 的启动流程是什么？**

**A:**

```
Keyguard 启动流程：

1. SystemServer 启动
   └── WindowManagerService.onDisplayReady()
       └── PhoneWindowManager.onDisplayReady()
           └── KeyguardViewMediator.onSystemReady()

2. KeyguardViewMediator 初始化
   ├── 读取锁屏配置
   ├── 注册状态监听
   └── 绑定 KeyguardService

3. SystemUI KeyguardService
   ├── onCreate() 创建服务
   ├── 初始化 KeyguardUpdateMonitor
   └── 创建 KeyguardHostView

4. 显示锁屏
   └── KeyguardBouncer.show()
       └── 显示安全验证界面
```

**Q2: 生物识别解锁的原理？**

**A:**

```
生物识别解锁原理：

1. 架构层次
   Framework: BiometricManager/BiometricService
   Native:    BiometricService
   HAL:       IBiometricsFingerprint/IFace/IIris

2. 认证流程
   a. 应用请求认证
   b. BiometricService 检查能力
   c. HAL 层进行生物特征比对
   d. 返回认证结果

3. 安全机制
   - 生物数据存储在 TEE (可信执行环境)
   - 原始生物数据不出安全区
   - 仅存储特征模板

4. 限制
   - 不如密码安全
   - 可能被物理强制
   - 需要备用解锁方式
```

**Q3: 锁屏上通知的可见性控制？**

**A:**

```
锁屏通知可见性控制：

1. 通知可见性级别
   VISIBILITY_PUBLIC:    完全可见
   VISIBILITY_SECRET:    完全隐藏
   VISIBILITY_PRIVATE:   显示基本信息

2. 设置方式
   Notification.Builder.setVisibility(visibility)

3. 锁屏显示逻辑
   if (isSecure() && !isKeyguardUnlocked()) {
       switch (visibility) {
           case SECRET:    // 不显示
           case PRIVATE:   // 显示 "内容已隐藏"
           case PUBLIC:    // 完整显示
       }
   }

4. 用户控制
   设置 → 应用 → 通知 → 锁屏通知
```

---

## 总结

### SystemUI 核心要点

1. **SystemUI**：系统级 UI（状态栏、导航栏、通知、锁屏）
2. **AOD**：DozeMachine 状态机 + 低功耗显示 + 传感器集成
3. **通知系统**：NMS + RemoteViews + SystemUI 协作
4. **RemoteViews**：跨进程视图，序列化操作
5. **Keyguard**：锁屏安全验证 + 生物识别 + 状态管理

### 文档章节概览

| 章节 | 主题 | 重点内容 |
|------|------|----------|
| 1-2 | SystemUI 基础 | 概述、启动流程 |
| 3 | AOD | Doze 状态机、HAL、功耗优化 |
| 4-9 | 通知系统 | NMS、RemoteViews、渲染、模板 |
| 10 | Framework 协作 | SystemUI 与 Framework 交互 |
| 11-12 | 高级特性 | NMS 高级、AOD 高级 |
| 13 | Keyguard | 锁屏系统、安全验证 |
| 14 | 面试指南 | Keyguard 面试问题 |

---

**文档版本**：v3.0
**更新时间**：2026-03-12
**参考源码**：Android 16 (API 36)

> 本文档基于 Android 16 (API 36) 源码分析
> 源码地址：https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/packages/SystemUI/