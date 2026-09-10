# Android SystemUI 完全指南

> 审阅基线：AOSP `android-17.0.0_r1`；审阅日期：2026-09-10。正文中的调用链为固定 tag 的关键路径分析，省略代码不是可独立编译的完整 AOSP 类；产品开关、权限和设备结果另行验证。


> 作者：OpenClaw | 日期：2026-03-11  
> SystemUI 核心机制 | AOD 与通知系统深度解析

---

## 目录

- [1. SystemUI 概述](#1-systemui-概述)
  - [1.1 什么是 SystemUI](#11-什么是-systemui)
  - [1.2 SystemUI 包含的组件](#12-systemui-包含的组件)
  - [1.3 SystemUI 进程](#13-systemui-进程)
- [2. SystemUI 启动流程（Android 17）](#2-systemui-启动流程android-17)
  - [2.1 整体架构：接口入口、实现入口与注入](#21-整体架构接口入口实现入口与注入)
  - [2.2 核心源码分析](#22-核心源码分析)
    - [抽象入口与真实状态字段](#抽象入口与真实状态字段)
    - [onCreate：引导配置和 boot 分发](#oncreate引导配置和-boot-分发)
    - [系统用户与次用户服务集合](#系统用户与次用户服务集合)
    - [依赖驱动的启动算法](#依赖驱动的启动算法)
    - [SystemUIService：启动门面，不是应用入口替代物](#systemuiservice启动门面不是应用入口替代物)
  - [2.3 Dagger 组件绑定示例](#23-dagger-组件绑定示例)
  - [2.4 启动时序图](#24-启动时序图)
  - [2.5 主要启动组件与核验方法](#25-主要启动组件与核验方法)
- [3. AOD (Always On Display) 详解](#3-aod-always-on-display-详解)
  - [3.1 AOD 概述](#31-aod-概述)
  - [3.2 AOD 架构（Android 17 职责示意）](#32-aod-架构android-17-职责示意)
    - [源码文件结构](#源码文件结构)
  - [3.3 AOD 状态机 (DozeMachine)](#33-aod-状态机-dozemachine)
  - [3.4 AOD 显示流程（Android 17）](#34-aod-显示流程android-17)
    - [触发原因与调试](#触发原因与调试)
  - [3.5 AOD 核心组件源码（Android 17）](#35-aod-核心组件源码android-17)
    - [DozeService：框架生命周期到状态机](#dozeservice框架生命周期到状态机)
    - [DozeHost：UI 与控制策略的边界](#dozehostui-与控制策略的边界)
    - [DozeTriggers：通知、手势与 proximity](#dozetriggers通知手势与-proximity)
    - [DozeSensors：注册不等于传感器一定可用](#dozesensors注册不等于传感器一定可用)
    - [DozeScreenState：目标状态与实际应用分开](#dozescreenstate目标状态与实际应用分开)
- [4. 通知系统详解](#4-通知系统详解)
  - [4.1 通知系统概述](#41-通知系统概述)
  - [4.2 通知发送流程](#42-通知发送流程)
  - [4.3 通知核心组件](#43-通知核心组件)
- [5. NotificationManagerService 深入分析](#5-notificationmanagerservice-深入分析)
  - [5.1 NMS 架构](#51-nms-架构)
  - [5.2 NMS 核心流程](#52-nms-核心流程)
    - [取消、更新与用户可见性的区别](#取消更新与用户可见性的区别)
- [6. RemoteViews 深度解析](#6-remoteviews-深度解析)
  - [6.1 RemoteViews 原理](#61-remoteviews-原理)
  - [6.2 RemoteViews 支持的 View](#62-remoteviews-支持的-view)
  - [6.3 RemoteViews 操作](#63-remoteviews-操作)
  - [6.4 Actions 机制深度解析](#64-actions-机制深度解析)
    - [当前 Action 的真实映射](#当前-action-的真实映射)
    - [反射不是任意方法执行](#反射不是任意方法执行)
    - [序列化、缓存和变体](#序列化缓存和变体)
    - [apply/reapply 与异步绑定](#applyreapply-与异步绑定)
  - [6.5 反射创建与 View 白名单机制](#65-反射创建与-view-白名单机制)
    - [三个需要同时存在的边界](#三个需要同时存在的边界)
    - [为什么不能简单序列化自定义 View](#为什么不能简单序列化自定义-view)
    - [点击与集合模板](#点击与集合模板)
- [7. SystemUI 与 Framework 协作](#7-systemui-与-framework-协作)
  - [7.1 通知协作流程](#71-通知协作流程)
- [8. 通知渲染流程](#8-通知渲染流程)
  - [8.1 渲染架构](#81-渲染架构)
  - [8.2 渲染流程详解](#82-渲染流程详解)
    - [接收与集合更新](#接收与集合更新)
    - [建表、准备与内容绑定](#建表准备与内容绑定)
    - [复用与重建的判断](#复用与重建的判断)
- [9. 通知模板系统](#9-通知模板系统)
  - [9.1 通知模板类型](#91-通知模板类型)
  - [9.2 模板使用示例](#92-模板使用示例)
  - [9.3 模板底层实现](#93-模板底层实现)
- [10. 面试常见问题](#10-面试常见问题)
  - [10.1 SystemUI 基础](#101-systemui-基础)
  - [10.2 AOD](#102-aod)
  - [10.3 通知系统](#103-通知系统)
- [11. NotificationManagerService 高级特性](#11-notificationmanagerservice-高级特性)
  - [11.1 NMS 核心数据结构与更新事务](#111-nms-核心数据结构与更新事务)
  - [11.2 当前排序算法：两轮排序与 group proxy](#112-当前排序算法两轮排序与-group-proxy)
  - [11.3 通知分组：身份、summary 与子通知](#113-通知分组身份summary-与子通知)
  - [11.4 通知气泡：元数据不是资格豁免](#114-通知气泡元数据不是资格豁免)
  - [11.5 声音与振动：提醒策略和视觉打断分别建模](#115-声音与振动提醒策略和视觉打断分别建模)
  - [11.6 偏好持久化与活跃通知不是一个数据库](#116-偏好持久化与活跃通知不是一个数据库)
  - [11.7 通知历史：条件记录、缓冲、保留与关闭清理](#117-通知历史条件记录缓冲保留与关闭清理)
- [12. AOD 高级特性](#12-aod-高级特性)
  - [12.1 AOD 与 WakefulnessLifecycle：中间态必须回到策略判断](#121-aod-与-wakefulnesslifecycle中间态必须回到策略判断)
  - [12.2 显示状态管理：pending、延迟和取消](#122-显示状态管理pending延迟和取消)
  - [12.3 传感器：监听资格与注册行为分离](#123-传感器监听资格与注册行为分离)
  - [12.4 AmbientDisplayConfiguration：available 不等于 enabled](#124-ambientdisplayconfigurationavailable-不等于-enabled)
  - [12.5 贯穿通知到 AOD 的可观测链路](#125-贯穿通知到-aod-的可观测链路)
  - [12.6 RemoteViews 异步绑定的代际与资源寿命](#126-remoteviews-异步绑定的代际与资源寿命)
  - [12.7 Pulse 和防烧屏：状态与动画边界](#127-pulse-和防烧屏状态与动画边界)
  - [12.8 为什么不能用一句“通知列表不适合 RecyclerView”解释架构](#128-为什么不能用一句通知列表不适合-recyclerview解释架构)
- [13. Keyguard 锁屏系统](#13-keyguard-锁屏系统)
  - [13.1 Keyguard 概述](#131-keyguard-概述)
  - [13.2 源码目录与实现边界](#132-源码目录与实现边界)
  - [13.3 启动链：system_server 绑定与 SystemUI startable 协作](#133-启动链system_server-绑定与-systemui-startable-协作)
  - [13.4 Mediator 的显示、隐藏与完成处理](#134-mediator-的显示隐藏与完成处理)
  - [13.5 KeyguardUpdateMonitor：监听与信任语义](#135-keyguardupdatemonitor监听与信任语义)
  - [13.6 安全模式与图案认证完整回调](#136-安全模式与图案认证完整回调)
  - [13.7 生物识别：认证结果到解锁模式](#137-生物识别认证结果到解锁模式)
  - [13.8 锁屏通知、隐私与窗口交互](#138-锁屏通知隐私与窗口交互)
  - [13.9 真实状态模型与 scene 迁移](#139-真实状态模型与-scene-迁移)
  - [13.10 安全与生命周期实践](#1310-安全与生命周期实践)
- [14. Keyguard 面试常见问题](#14-keyguard-面试常见问题)
  - [14.1 谁启动 Keyguard？](#141-谁启动-keyguard)
  - [14.2 认证成功为什么还没有立即隐藏锁屏？](#142-认证成功为什么还没有立即隐藏锁屏)
  - [14.3 Trust managed 可以跳过 bouncer 吗？](#143-trust-managed-可以跳过-bouncer-吗)
  - [14.4 锁屏与 AOD 是同一个状态机吗？](#144-锁屏与-aod-是同一个状态机吗)
  - [14.5 如何定位通知只在锁屏消失？](#145-如何定位通知只在锁屏消失)
- [总结](#总结)

---

## 1. SystemUI 概述

### 1.1 什么是 SystemUI

```text
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
│                      系统 UI 应用（独立进程，通过 Binder 与 Framework 服务协作）                                   │
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

SystemUI 覆盖状态栏、通知、锁屏、快捷设置、音量、电源交互和 AOD 等 UI。功能名不等于固定 Java 类名：旧文的 AODView、FingerprintUnlockView、EdgeNavStrategy 等不应被当作此 tag 的类路径索引。

```text
SystemUI process
  status/notification: NotificationListener, NotifCollection, NotifPipeline,
                       ShadeListBuilder, ExpandableNotificationRow,
                       NotificationStackScrollLayout
  doze: DozeService, DozeMachine, DozeTriggers, DozeSensors,
        DozeScreenState, DozeUi, DozeHost
  keyguard: KeyguardService, KeyguardViewMediator, KeyguardUpdateMonitor,
            credential view/controllers, repositories/interactors
  other UI: navigation, quick settings, volume, power, screen decorations
```

并非所有控制器都实现 CoreStartable，也并非所有功能都在同一设备构建中启用。Recents/手势导航与 Launcher/Quickstep、WM Shell 的分工由产品配置决定，不能声称所有最近任务界面都绘制在 SystemUI 中。

### 1.3 SystemUI 进程

SystemUI 是独立系统应用，常规主进程为 `com.android.systemui`，**不运行在 system_server 进程中**。SystemServer 发起组件启动，AMS 负责应用进程与 Service 调度；进程启动后先创建 Application，再创建 Service。

```text
system_server: SystemServer.startSystemUi(context, windowManager)
  -> PackageManagerInternal.getSystemUiServiceComponent()
  -> context.startServiceAsUser(intent, UserHandle.SYSTEM)
  -> windowManager.onSystemUiStarted()

com.android.systemui process:
  AppComponentFactory -> application.impl.SystemUIApplicationImpl
  Application.onCreate -> dependency graph
  SystemUIService.onCreate -> startSystemUserServicesIfNeeded
```

这里没有 `SystemServiceManager.startService(SystemUIService.class)`；SystemUIService 是 Android Service，不是 system_server 内的 SystemService。`windowManager.onSystemUiStarted()` 也不等于所有 SystemUI UI 已完成首帧，是启动协作节点。

多用户会建立相应用户的 SystemUI 生命周期；带冒号的子进程不应无条件启动全部 startables。判断应来自实际 Application/ProcessWrapper 路径，不能凭某厂商的 `:pixel` 进程名推导 AOSP 规则。

## 2. SystemUI 启动流程（Android 17）

### 2.1 整体架构：接口入口、实现入口与注入

固定 tag 将 Application 抽象接口与初始化实现拆分到不同构建目标。入口不在旧 `src/com/android/systemui/SystemUIApplication.java`：

| 文件 | 职责 |
|---|---|
| `application/SystemUIApplication.kt` | 抽象 Application，声明系统用户/次用户启动方法 |
| `application/impl/SystemUIApplicationImpl.java` | 实现 onCreate、startables、boot/configuration 分发 |
| `SystemUIAppComponentFactoryBase.kt` | 创建 Application 并注入 Context 可用回调，解析受注入组件 |
| `SystemUIInitializer.java` | 构建 root/SysUI/WM 依赖图，处理初始化协作 |
| `SystemUIService.java` | Service 的 onCreate 触发系统用户 startables |

以上路径均相对于 `frameworks/base/packages/SystemUI/src/com/android/systemui/`。SystemUI manifest 的 `android:name` 指向 `.application.impl.SystemUIApplicationImpl`，`appComponentFactory` 指向 PhoneSystemUIAppComponentFactory。抽象基类不是可以直接实例化的 Application。

```text
AppComponentFactory.instantiateApplicationCompat
  -> super instantiate concrete Application
  -> require ApplicationContextInitializer
  -> setContextAvailableCallback
       -> createSystemUIInitializerInternal(context)
            cached initializer ? reuse
            else createSystemUIInitializer(applicationContext)
                 -> init(false)
                 -> sysUIComponent.inject(factory)

SystemUIApplicationImpl.onCreate
  -> callback.onContextAvailable(this)
  -> mInitializer / mSysUIComponent / mBootCompleteCache
  -> main-thread LockPatternUtils initialization
  -> looper tracing / theme / graphics and UI setup
  -> system user: boot/locale receivers
     secondary main process: per-user startables
     subprocess: do not start all services
```

为什么工厂要在创建 Application 时设置回调，而不是 Service 自己 new 初始化器？因为 Application、Provider 与其他注入组件共享同一依赖图，Context 可用的时刻决定初始化顺序。provider context initializer 也可能经工厂触发初始化；`createSystemUIInitializerInternal()` 的缓存避免每个入口各建一套 graph。

### 2.2 核心源码分析

#### 抽象入口与真实状态字段

`SystemUIApplication` 仅声明 `startSystemUserServicesIfNeeded()` 与 `startSecondaryUserServicesIfNeeded()`，注释要求主线程调用。实现类中的关键字段为：

```java
// SystemUIApplicationImpl 的关键字段结构（省略注入与非核心字段）
private final AtomicReference<CoreStartable[]> mServices = new AtomicReference<>();
private final AtomicBoolean mServicesStarted = new AtomicBoolean(false);
private ApplicationContextAvailableCallback mContextAvailableCallback;
private SysUIComponent mSysUIComponent;
private SystemUIInitializer mInitializer;
private ProcessWrapper mProcessWrapper;
private BootCompleteCacheImpl mBootCompleteCache;
```

AtomicReference/AtomicBoolean 是此版本真实字段，不能用旧数组加普通 boolean 冒充。原子字段不意味着入口变成任意线程可并发启动的通用 API；主线程契约、回调线程与依赖初始化顺序仍需遵守。

#### onCreate：引导配置和 boot 分发

onCreate 的第一段执行 Context 回调获取 graph，再初始化 LockPatternUtils，设置 Looper trace、主题等。GPU 优先级设置是条件逻辑：只有系统用户分支且 SF priority 对应特定值才提升 renderer context priority，不是强制所有 GPU 操作 realtime。

boot 接收的是 `ACTION_LOCKED_BOOT_COMPLETED`。`handleBootCompletedOnSeparateThread()` 开关为真时，receiver 可在 background Handler 收到广播，再由 mainExecutor 设置 boot cache 并通知 startables；非该分支在默认接收线程执行。次用户主进程直接启动 per-user startables，子进程提前退出其启动分支。


源码：[SystemUIApplicationImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/application/impl/SystemUIApplicationImpl.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void onCreate() {
    super.onCreate();
    Log.v(TAG, "SystemUIApplication created.");
    // This line is used to setup Dagger's dependency injection and should be kept at the
    // top of this method.
    TimingsTraceLog log = new TimingsTraceLog("SystemUIBootTiming",
            Trace.TRACE_TAG_APP);
    log.traceBegin("DependencyInjection");
    mInitializer = mContextAvailableCallback.onContextAvailable(this);
    mSysUIComponent = mInitializer.getSysUIComponent();
    mBootCompleteCache = mSysUIComponent.provideBootCacheImpl();
    log.traceEnd();

    log.traceBegin("LockPatterUtils");
    // This is only here to ensure that LockPatternUtils is instantiated from the main thread
    // first to help avoid situations when it's instantiated from a background thread, which
    // makes it unsafe to use with the version of checkCredential that takes a non-null
    // progressCallback.
    mSysUIComponent.getLockPatternUtils();
    log.traceEnd();

    GlobalRootComponent rootComponent = mInitializer.getRootComponent();

    // Enable Looper trace points.
    // This allows us to see Handler callbacks on traces.
    rootComponent.getMainLooper().setTraceTag(Trace.TRACE_TAG_APP);
    mProcessWrapper = rootComponent.getProcessWrapper();
    ComposeView_androidKt.disableWindowInsetsRulers(ComposeView.Companion);

    // TODO(b/458193632): Re-enable once the crash is fixed in Compose.
    ComposeFoundationFlags.isCacheWindowForPagerEnabled = false;

    // Set the application theme that is inherited by all services. Note that setting the
    // application theme in the manifest does only work for activities. Keep this in sync with
    // the theme set there.
    setTheme(R.style.Theme_SystemUI);

    View.setTraceLayoutSteps(
            rootComponent.getSystemPropertiesHelper()
                    .getBoolean("persist.debug.trace_layouts", false));
    View.setTracedRequestLayoutClassClass(
            rootComponent.getSystemPropertiesHelper()
                    .get("persist.debug.trace_request_layout_class", null));

    if (Flags.enableLayoutTracing()) {
        View.setTraceLayoutSteps(true);
    }
    Animator.setPostNotifyEndListenerEnabled(true);

    if (mProcessWrapper.isSystemUser()) {
        IntentFilter bootCompletedFilter = new
                IntentFilter(Intent.ACTION_LOCKED_BOOT_COMPLETED);
        bootCompletedFilter.setPriority(IntentFilter.SYSTEM_HIGH_PRIORITY);

        // If SF GPU context priority is set to realtime, then SysUI should run at high.
        // The priority is defaulted at medium.
        int sfPriority = SurfaceControl.getGPUContextPriority();
        Log.i(TAG, "Found SurfaceFlinger's GPU Priority: " + sfPriority);
        if (sfPriority == ThreadedRenderer.EGL_CONTEXT_PRIORITY_REALTIME_NV) {
            Log.i(TAG, "Setting SysUI's GPU Context priority to: "
                    + ThreadedRenderer.EGL_CONTEXT_PRIORITY_HIGH_IMG);
            ThreadedRenderer.setContextPriority(
                    ThreadedRenderer.EGL_CONTEXT_PRIORITY_HIGH_IMG);
        }

        if (Flags.handleBootCompletedOnSeparateThread()) {
            final Handler bgHandler = mSysUIComponent.getBackgroundHandler();
            final Executor mainExecutor = mSysUIComponent.getMainExecutor();
            registerReceiver(new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                    if (mBootCompleteCache.isBootComplete()) return;

                    if (DEBUG) Log.v(TAG, "BOOT_COMPLETED received");
                    unregisterReceiver(this);
                    mainExecutor.execute(() -> {
                        Trace.traceBegin(Trace.TRACE_TAG_APP,
                                "signaling onBootCompleted");
                        mBootCompleteCache.setBootComplete();
                        if (mServicesStarted.get()) {
                            final CoreStartable[] services = mServices.get();
                            for (int i = 0; i < services.length; i++) {
                                notifyBootCompleted(services[i]);
                            }
                        }
                        Trace.traceEnd(Trace.TRACE_TAG_APP);
                    });
                }
            }, bootCompletedFilter, null, bgHandler);
        } else {
            registerReceiver(new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                    if (mBootCompleteCache.isBootComplete()) return;

                    if (DEBUG) Log.v(TAG, "BOOT_COMPLETED received");
                    unregisterReceiver(this);
                    mBootCompleteCache.setBootComplete();
                    if (mServicesStarted.get()) {
                        final CoreStartable[] services = mServices.get();
                        final int N = services.length;
                        for (int i = 0; i < N; i++) {
                            notifyBootCompleted(services[i]);
                        }
                    }
                }
            }, bootCompletedFilter);
        }

        IntentFilter localeChangedFilter = new IntentFilter(Intent.ACTION_LOCALE_CHANGED);
        if (Flags.handleBootCompletedOnSeparateThread()) {
            final Handler bgHandler = mSysUIComponent.getBackgroundHandler();
            registerReceiver(new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                    if (Intent.ACTION_LOCALE_CHANGED.equals(intent.getAction())) {
                        if (!mBootCompleteCache.isBootComplete()) return;
                        // Update names of SystemUi notification channels
                        NotificationChannels.createAll(context);
                    }
                }
            }, localeChangedFilter, null, bgHandler);
        } else {
            registerReceiver(new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                    if (Intent.ACTION_LOCALE_CHANGED.equals(intent.getAction())) {
                        if (!mBootCompleteCache.isBootComplete()) return;
                        // Update names of SystemUi notification channels
                        NotificationChannels.createAll(context);
                    }
                }
            }, localeChangedFilter);
        }
    } else {
        // We don't need to startServices for sub-process that is doing some tasks.
        // (screenshots, sweetsweetdesserts or tuner ..)
        if (isSubprocess()) {
            return;
        }
        // For a secondary user, boot-completed will never be called because it has already
        // been broadcasted on startup for the primary SystemUI process.  Instead, for
        // components which require the SystemUI component to be initialized per-user, we
        // start those components now for the current non-system user.
        startSecondaryUserServicesIfNeeded();
    }
}
```


#### 系统用户与次用户服务集合

系统用户合并 `getStartables()` 与 `getPerUserStartables()`，次用户只加入 per-user map。TreeMap 以类名排序保证确定性，但类名顺序不等于依赖顺序；真正的依赖调度发生在 startServicesIfNeeded 中。


```java
public void startSystemUserServicesIfNeeded() {
    if (!shouldStartSystemUserServices()) {
        Log.wtf(TAG, "Tried starting SystemUser services on non-SystemUser");
        return;  // Per-user startables are handled in #startSystemUserServicesIfNeeded.
    }
    final String vendorComponent = mInitializer.getVendorComponent(getResources());

    // Sort the startables so that we get a deterministic ordering.
    // TODO: make #start idempotent and require users of CoreStartable to call it.
    Map<Class<?>, Provider<CoreStartable>> sortedStartables = new TreeMap<>(
            Comparator.comparing(Class::getName));
    sortedStartables.putAll(mSysUIComponent.getStartables());
    sortedStartables.putAll(mSysUIComponent.getPerUserStartables());
    startServicesIfNeeded(
            sortedStartables, "StartServices", vendorComponent);
}

public void startSecondaryUserServicesIfNeeded() {
    if (!shouldStartSecondaryUserServices()) {
        return;  // Per-user startables are handled in #startSystemUserServicesIfNeeded.
    }
    // Sort the startables so that we get a deterministic ordering.
    Map<Class<?>, Provider<CoreStartable>> sortedStartables = new TreeMap<>(
            Comparator.comparing(Class::getName));
    sortedStartables.putAll(mSysUIComponent.getPerUserStartables());
    startServicesIfNeeded(
            sortedStartables, "StartSecondaryServices", null);
}
```


#### 依赖驱动的启动算法

算法逐轮扫描尚未启动的条目，只有依赖集合已包含在 startedStartables 中时，才 `Provider.get()`、`CoreStartable.start()` 并记录完成。未满足的条目进入下一轮；一轮没有进展而队列仍非空时，说明有缺失依赖或环，记录错误并失败，而不是静默跳过。

这种实现不是优化后的入度队列式 Kahn 算法：在依赖链很长时会重复扫描；注释假设大多数组件无依赖、两三轮足够。N 个组件、K 轮扫描的成本大致随 N*K 和依赖集合检查增长，不能声称恒定时间。启动回调抛异常也不会自动回滚之前所有组件。

启动前检查 `sys.boot_completed` 处理进程晚启动/重启；vendor component 按专门分支创建；所有组件随后注册到 DumpManager，必要时收到 onBootCompleted，最后执行 post-init tasks 并置 started 状态。


```java
private void startServicesIfNeeded(
        Map<Class<?>, Provider<CoreStartable>> startables,
        String metricsPrefix,
        String vendorComponent) {
    if (mServicesStarted.get()) {
        return;
    }
    final CoreStartable[] services =
            new CoreStartable[startables.size() + (vendorComponent == null ? 0 : 1)];
    mServices.set(services);

    if (!mBootCompleteCache.isBootComplete()) {
        // check to see if maybe it was already completed long before we began
        // see ActivityManagerService.finishBooting()
        if ("1".equals(getRootComponent().getSystemPropertiesHelper()
                .get("sys.boot_completed"))) {
            mBootCompleteCache.setBootComplete();
            if (DEBUG) {
                Log.v(TAG, "BOOT_COMPLETED was already sent");
            }
        }
    }

    DumpManager dumpManager = mSysUIComponent.createDumpManager();

    Log.v(TAG, "Starting SystemUI services for user "
            + Process.myUserHandle().getIdentifier() + ".");
    TimingsTraceLog log = new TimingsTraceLog("SystemUIBootTiming",
            Trace.TRACE_TAG_APP);
    log.traceBegin(metricsPrefix);

    HashSet<Class<?>> startedStartables = new HashSet<>();

    // Perform a form of topological sort:
    // 1) Iterate through a queue of all non-started startables
    //   If the startable has all of its dependencies met
    //     - start it
    //   Else
    //     - enqueue it for the next iteration
    // 2) If anything was started and the "next" queue is not empty, loop back to 1
    // 3) If we're done looping and there are any non-started startables left, throw an error.
    //
    // This "sort" is not very optimized. We assume that most CoreStartables don't have many
    // dependencies - zero in fact. We assume two or three iterations of this loop will be
    // enough. If that ever changes, it may be worth revisiting.

    log.traceBegin("Topologically start Core Startables");
    boolean startedAny = false;
    ArrayDeque<Map.Entry<Class<?>, Provider<CoreStartable>>> queue;
    ArrayDeque<Map.Entry<Class<?>, Provider<CoreStartable>>> nextQueue =
            new ArrayDeque<>(startables.entrySet());
    int numIterations = 0;

    int serviceIndex = 0;

    do {
        startedAny = false;
        queue = nextQueue;
        nextQueue = new ArrayDeque<>(startables.size());

        while (!queue.isEmpty()) {
            Map.Entry<Class<?>, Provider<CoreStartable>> entry = queue.removeFirst();

            Class<?> cls = entry.getKey();
            Set<Class<? extends CoreStartable>> deps =
                    mSysUIComponent.getStartableDependencies().get(cls);
            if (deps == null || startedStartables.containsAll(deps)) {
                String clsName = cls.getName();
                int i = serviceIndex;  // Copied to make lambda happy.
                timeInitialization(
                        clsName,
                        () -> services[i] = startStartable(clsName, entry.getValue()),
                        log,
                        metricsPrefix);
                startedStartables.add(cls);
                startedAny = true;
                serviceIndex++;
            } else {
                nextQueue.add(entry);
            }
        }
        numIterations++;
    } while (startedAny && !nextQueue.isEmpty()); // if none were started, stop.

    if (!nextQueue.isEmpty()) { // If some startables were left over, throw an error.
        while (!nextQueue.isEmpty()) {
            Map.Entry<Class<?>, Provider<CoreStartable>> entry = nextQueue.removeFirst();
            Class<?> cls = entry.getKey();
            Set<Class<? extends CoreStartable>> deps =
                    mSysUIComponent.getStartableDependencies().get(cls);
            StringJoiner stringJoiner = new StringJoiner(", ");
            for (Class<? extends CoreStartable> c : deps) {
                if (!startedStartables.contains(c)) {
                    stringJoiner.add(c.getName());
                }
            }
            Log.e(TAG, "Failed to start " + cls.getName()
                    + ". Missing dependencies: [" + stringJoiner + "]");
        }

        throw new RuntimeException("Failed to start all CoreStartables. Check logcat!");
    }
    Log.i(TAG, "Topological CoreStartables completed in " + numIterations + " iterations");
    log.traceEnd();

    if (vendorComponent != null) {
        timeInitialization(
                vendorComponent,
                () -> {
                    services[services.length - 1] =
                            startAdditionalStartable(vendorComponent);
                },
                log,
                metricsPrefix);
    }

    for (serviceIndex = 0; serviceIndex < services.length; serviceIndex++) {
        final CoreStartable service = services[serviceIndex];
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

    mServicesStarted.set(true);
}

private static void notifyBootCompleted(CoreStartable coreStartable) {
    if (Trace.isEnabled()) {
        Trace.traceBegin(
                Trace.TRACE_TAG_APP,
                coreStartable.getClass().getSimpleName() + ".onBootCompleted()");
    }
    coreStartable.onBootCompleted();
    Trace.endSection();
}
```


#### SystemUIService：启动门面，不是应用入口替代物

服务的 onCreate 首先调用 Application 的 `startSystemUserServicesIfNeeded()`，之后配置日志冻结、异常日志、电池通知和调试 Binder 计数等。构造器通过依赖注入提供 Handler/DumpHandler 等，不是无参创建每个控制器。


源码：[SystemUIService.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/SystemUIService.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void onCreate() {
    super.onCreate();

    // Start all of SystemUI
    ((SystemUIApplication) getApplication()).startSystemUserServicesIfNeeded();

    // Finish initializing dump logic
    mLogBufferFreezer.attach(mBroadcastDispatcher);

    // Attempt to dump all LogBuffers for any uncaught exception
    mUncaughtExceptionPreHandlerManager.registerHandler(
            (thread, throwable) -> mLogBufferEulogizer.record(throwable));

    // If configured, set up a battery notification
    if (getResources().getBoolean(R.bool.config_showNotificationForUnknownBatteryState)) {
        mBatteryStateNotifier.startListening();
    }

    // For debugging RescueParty
    if (Build.IS_DEBUGGABLE && SystemProperties.getBoolean("debug.crash_sysui", false)) {
        throw new RuntimeException();
    }

    if (Build.IS_DEBUGGABLE) {
        // b/71353150 - looking for leaked binder proxies
        BinderInternal.nSetBinderProxyCountEnabled(true);
        BinderInternal.nSetBinderProxyCountWatermarks(
                /* high= */ 1000, /* low= */ 900, /* warning= */ 950);
        BinderInternal.setBinderProxyCountCallback(
                new BinderInternal.BinderProxyCountEventListener() {
                    @Override
                    public void onLimitReached(int uid) {
                        Slog.w(TAG,
                                "uid " + uid + " sent too many Binder proxies to uid "
                                + Process.myUid());
                    }
                }, mMainHandler);
    }

    // Bind the dump service so we can dump extra info during a bug report
    startServiceAsUser(
            new Intent(getApplicationContext(), SystemUIAuxiliaryDumpService.class),
            UserHandle.SYSTEM);
}
```


### 2.3 Dagger 组件绑定示例

下面是**自定义功能示例**，展示 multibinding，不伪造某两项 AOSP 组件间的依赖关系：

```java
@Module
abstract class ExampleStartableModule {
    @Binds @IntoMap @ClassKey(ExampleStartable.class)
    abstract CoreStartable bindExample(ExampleStartable implementation);
}

final class ExampleStartable implements CoreStartable {
    @Inject ExampleStartable(ExampleRepository repository) {
        // 保存依赖，不在构造器偷偷启动重复监听。
    }
    @Override public void start() {
        // 启动这一功能；由宿主保证正确线程和调用时机。
    }
    @Override public void onBootCompleted() {
        // 需要 boot 完成的任务放在这里；不能反向依赖未声明组件。
    }
}
```

`ExampleRepository` 是业务占位类型。真实工程需按本构建目标的模块/qualifier 将依赖 map 提供给 `SysUIComponent.getStartableDependencies()`；不要把示例里的 `NotificationListener -> CentralSurfacesImpl` 当固定 tag 的真实边。

CoreStartable 是普通进程内启动契约，不等于每项都声明 Android Service。实例构造、start、boot callback、dump 注册属于不同阶段；代码不能仅在构造器里做完副作用就认为拓扑关系已生效。

### 2.4 启动时序图

```text
system_server                 SystemUI Application                    Service
startSystemUi
  startServiceAsUser -------> instantiate Application
                              set context callback
                              onCreate -> graph/theme/receivers
                                                        ------------> onCreate
                              <--------------------------- startSystemUserServicesIfNeeded
                              merge/sort maps
                              topological rounds: provider.get -> start
                              vendor startable / dump registration
                              executePostInitTasks -> servicesStarted
LOCKED_BOOT_COMPLETED ------> receiver -> boot cache -> onBootCompleted
                              (or already-booted property branch)
```

图中 boot 信号与服务初始化可能交错，boot cache 和 started 状态负责判断何时分发；不可把 boot 广播写成所有 startable 都只会在其到达后才创建。启动完成也不是每个功能异步数据加载或首帧完成。

### 2.5 主要启动组件与核验方法

可以从 `CentralSurfacesImpl`、`KeyguardViewMediator` 等实现及 `SysUIComponent` 的 map 绑定查找具体功能。旧表把 UiModeManagerService、普通控制器、Activity 和所有平台分支都当 CoreStartable，是分类错误；完整集合应由该产品最终依赖图决定。

审阅一个组件时，要依次确认实现契约、map key、provider、依赖 map、start 副作用和 boot callback。若功能没启动，先看是否进入 map/是否被依赖阻塞，再看 start 后异步工作；不要仅凭类存在就推断它在每个用户与设备上都已启动。

平台调试可结合 SystemUIBootTiming trace、`dumpsys activity service com.android.systemui/.SystemUIService` 的 dump 参数以及对应日志分析。命令可用性和 dump 输出受构建权限与产品影响；本轮未运行设备验证。

## 3. AOD (Always On Display) 详解

### 3.1 AOD 概述

```text
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
│    OLED 示例：大部分像素保持黑色；面板低功耗能力由硬件实现决定                             │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

AOD 技术特点:
1. 低功耗: 低亮度/低刷新/局部内容及低功耗显示状态协作，不只由像素数量决定
2. 显示内容可定制
3. 支持通知显示
4. 支持触控唤醒
5. 支持手势唤醒
```

### 3.2 AOD 架构（Android 17 职责示意）

> **源码路径**: `frameworks/base/packages/SystemUI/src/com/android/systemui/doze/`

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD 架构（职责示意）                              │
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

本轮直接核对的实现位于 `packages/SystemUI/src/com/android/systemui/doze/`：

```text
DozeService.java       DreamService entry
DozeMachine.java       State / Part / Service + transition logic
DozeTriggers.java      notification / proximity / sensor decisions
DozeSensors.java       sensor registration + callbacks
DozeScreenState.java   display state timing
DozeUi.java            pulse callback + time tick
DozeHost.java          SystemUI host contract
DozeLog.java           reason/state logging
```

Dagger 组件与资源策略决定各 Part 的实际注入。DozeMachine 的 Service 是内部控制接口，不要与 Android Service 或设备空闲管理的 Doze 混为一谈。PowerManager/DreamManager 的 dozing dream 协作与应用后台 DeviceIdleController 是不同责任体系。

### 3.3 AOD 状态机 (DozeMachine)

Android 17 当前枚举不仅包含 DOZE/DOZE_AOD/常规 pulse，还包含 `DOZE_PULSING_WITHOUT_UI`、`DOZE_PULSING_AUTH_UI` 和 `DOZE_AOD_MINMODE`。旧文深度段中的 DOZE_INIT、DOZE_REST、EXITED_DOZE 等不是这个状态机的真实枚举。

State 中的 canPulse、staysAwake、isAlwaysOn 与 screenState 分别回答：能否提出脉冲、是否需要持有状态唤醒、是否属于 AOD 状态族、期望 Display 状态。四者并不等价，尤其 AOD_DOCKED/MINMODE 可映射 STATE_ON，而普通 AOD 映射 DOZE_SUSPEND。


源码：[DozeMachine.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/doze/DozeMachine.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public enum State {
    /** Default state. Transition to INITIALIZED to get Doze going. */
    UNINITIALIZED,
    /** Doze components are set up. Followed by transition to DOZE or DOZE_AOD. */
    INITIALIZED,
    /** Regular doze. Device is asleep and listening for pulse triggers. */
    DOZE,
    /** Deep doze. Device is asleep and is not listening for pulse triggers. */
    DOZE_SUSPEND_TRIGGERS,
    /** Always-on doze. Device is asleep, showing UI and listening for pulse triggers. */
    DOZE_AOD,
    /** Pulse has been requested. Device is awake and preparing UI */
    DOZE_REQUEST_PULSE,
    /** Pulse is showing. Device is awake and showing UI. */
    DOZE_PULSING,
    /** Pulse is showing with bright wallpaper. Device is awake and showing UI. */
    DOZE_PULSING_BRIGHT,
    /** Device is awake and not showing any UI. */
    DOZE_PULSING_WITHOUT_UI,
    /** Device is awake and showing authentication UI (any relevant biometric UI and auth
     * messages. */
    DOZE_PULSING_AUTH_UI,
    /** Pulse is done showing. Followed by transition to DOZE or DOZE_AOD. */
    DOZE_PULSE_DONE,
    /** Doze is done. DozeService is finished. */
    FINISH,
    /** AOD, but the display is temporarily off. */
    DOZE_AOD_PAUSED,
    /** AOD, prox is near, transitions to DOZE_AOD_PAUSED after a timeout. */
    DOZE_AOD_PAUSING,
    /**
     * Always-on doze. Device is awake, showing docking UI and listening
     * for pulse triggers.
    */
    DOZE_AOD_DOCKED,
    /**
     * Always-on doze. Device is awake, showing min-mode UI and listening
     * for pulse triggers.
    */
    DOZE_AOD_MINMODE;

    boolean canPulse() {
        switch (this) {
            case DOZE:
            case DOZE_AOD:
            case DOZE_AOD_PAUSED:
            case DOZE_AOD_PAUSING:
            case DOZE_AOD_DOCKED:
            case DOZE_AOD_MINMODE:
                return true;
            default:
                return false;
        }
    }

    boolean staysAwake() {
        switch (this) {
            case DOZE_REQUEST_PULSE:
            case DOZE_PULSING:
            case DOZE_PULSING_BRIGHT:
            case DOZE_PULSING_WITHOUT_UI:
            case DOZE_PULSING_AUTH_UI:
            case DOZE_AOD_DOCKED:
            case DOZE_AOD_MINMODE:
                return true;
            default:
                return false;
        }
    }

    boolean isAlwaysOn() {
        return this == DOZE_AOD || this == DOZE_AOD_DOCKED || this == DOZE_AOD_MINMODE;
    }

    int screenState(DozeParameters parameters) {
        switch (this) {
            case UNINITIALIZED:
            case INITIALIZED:
                return parameters.shouldControlScreenOff() ? Display.STATE_ON
                        : Display.STATE_OFF;
            case DOZE_REQUEST_PULSE:
                return parameters.getDisplayNeedsBlanking() ? Display.STATE_OFF
                        : Display.STATE_ON;
            case DOZE_AOD_PAUSED:
            case DOZE:
            case DOZE_SUSPEND_TRIGGERS:
                return Display.STATE_OFF;
            case DOZE_PULSING:
            case DOZE_PULSING_WITHOUT_UI:
            case DOZE_PULSING_AUTH_UI:
            case DOZE_PULSING_BRIGHT:
            case DOZE_AOD_DOCKED:
            case DOZE_AOD_MINMODE:
                return Display.STATE_ON;
            case DOZE_AOD:
            case DOZE_AOD_PAUSING:
                return Display.STATE_DOZE_SUSPEND;
            default:
                return Display.STATE_UNKNOWN;
        }
    }
}
```


状态请求必须在主线程；`requestState()` 禁止用普通入口请求 DOZE_REQUEST_PULSE，脉冲原因由 requestPulse 专门传入。请求进入队列，当前切换期间 Part 再请求新状态时由队列继续处理，避免简单递归立即打乱当前切换。


```java
public void requestState(State requestedState) {
    Preconditions.checkArgument(requestedState != State.DOZE_REQUEST_PULSE);
    requestState(requestedState, DozeLog.PULSE_REASON_NONE);
}

public void requestPulse(int pulseReason) {
    // Must not be called during a transition. There's no inherent problem with that,
    // but there's currently no need to execute from a transition and it simplifies the
    // code to not have to worry about keeping the pulseReason in mQueuedRequests.
    Preconditions.checkState(!isExecutingTransition());
    requestState(State.DOZE_REQUEST_PULSE, pulseReason);
}

private void requestState(State requestedState, int pulseReason) {
    Assert.isMainThread();
    if (DEBUG) {
        Log.i(TAG, "request: current=" + mState + " req=" + requestedState,
                new Throwable("here"));
    }

    boolean runNow = !isExecutingTransition();
    mQueuedRequests.add(requestedState);
    if (runNow) {
        mWakeLock.acquire(REASON_CHANGE_STATE);
        for (int i = 0; i < mQueuedRequests.size(); i++) {
            // Transitions in Parts can call back into requestState, which will
            // cause mQueuedRequests to grow.
            transitionTo(mQueuedRequests.get(i), pulseReason);
        }
        mQueuedRequests.clear();
        mWakeLock.release(REASON_CHANGE_STATE);
    }
}
```


真正切换先应用 transitionPolicy，再校验转换、更新状态、通知所有 Part、调整状态 WakeLock，最后解析中间态。FINISH 是终止状态；不能直接从任意状态跳入 pulsing，不能把每个传感器事件都解释为必然发生完整一次 pulse。


```java
private void transitionTo(State requestedState, int pulseReason) {
    State newState = transitionPolicy(requestedState);

    if (DEBUG) {
        Log.i(TAG, "transition: old=" + mState + " req=" + requestedState + " new=" + newState);
    }

    if (newState == mState) {
        return;
    }

    validateTransition(newState);

    State oldState = mState;
    mState = newState;

    mDozeLog.traceState(newState);
    TrackTracer.instantForGroup("keyguard", "doze_machine_state", newState.ordinal());

    updatePulseReason(newState, oldState, pulseReason);
    performTransitionOnComponents(oldState, newState);
    updateWakeLockState(newState);

    resolveIntermediateState(newState);
}

private State transitionPolicy(State requestedState) {
    if (mState == State.FINISH) {
        return State.FINISH;
    }

    if (mDozeHost.isAlwaysOnSuppressed() && requestedState.isAlwaysOn()) {
        Log.i(TAG, "Doze is suppressed by an app. Suppressing state: " + requestedState);
        mDozeLog.traceAlwaysOnSuppressed(requestedState, "app");
        return State.DOZE;
    }
    if (mDozeHost.isPowerSaveActive() && requestedState.isAlwaysOn()) {
        Log.i(TAG, "Doze is suppressed by battery saver. Suppressing state: " + requestedState);
        mDozeLog.traceAlwaysOnSuppressed(requestedState, "batterySaver");
        return State.DOZE;
    }
    if ((mState == State.DOZE_AOD_PAUSED || mState == State.DOZE_AOD_PAUSING
            || mState == State.DOZE_AOD || mState == State.DOZE
            || mState == State.DOZE_AOD_MINMODE
            || mState == State.DOZE_AOD_DOCKED || mState == State.DOZE_SUSPEND_TRIGGERS)
            && requestedState == State.DOZE_PULSE_DONE) {
        Log.i(TAG, "Dropping pulse done because current state is already done: " + mState);
        return mState;
    }
    if (requestedState == State.DOZE_REQUEST_PULSE && !mState.canPulse()) {
        Log.i(TAG, "Dropping pulse request because current state can't pulse: " + mState);
        return mState;
    }
    return requestedState;
}
```


```text
UNINITIALIZED -> INITIALIZED -> policy chooses DOZE / AOD / DOCKED / MINMODE
                                  |
                     allowed pulse request + reason
                                  v
                           DOZE_REQUEST_PULSE
                                  |
                       host pulse started callback
                                  v
       DOZE_PULSING / BRIGHT / WITHOUT_UI / AUTH_UI (condition-dependent)
                                  |
                       host pulse finished callback
                                  v
                          DOZE_PULSE_DONE
                                  |
                         resolveIntermediateState
                      -> resting doze state or FINISH

proximity: AOD -> AOD_PAUSING -> AOD_PAUSED; far -> AOD
service dream stopped -> FINISH
```

这是主干和分支摘要，不声称图中任意节点可彼此跳转；合法前驱以 validateTransition 为准。状态图是软件逻辑，并不等于每一步都立即对应硬件屏幕状态完成。

### 3.4 AOD 显示流程（Android 17）

DozeService 是 windowless DreamService，不额外创建一个名叫 AODView 的独立窗口。onCreate 构建 DozeComponent；onDreamingStarted 请求 INITIALIZED 并调用 startDozing；onDreamingStopped 请求 FINISH。显示内容由 SystemUI 的锁屏/AOD UI 协作提供。

```text
Dream / power coordination -> DozeService.onDreamingStarted
  -> DozeMachine.requestState(INITIALIZED)
  -> Part.transitionTo callbacks
  -> resolveIntermediateState: min mode / wakefulness / dock / always-on policy
  -> DozeScreenState.transitionTo -> pending display state
  -> DozeMachine.Service.setDozeScreenState -> DreamService/power display path
```

通知/手势到达后，DozeTriggers 根据设置、pulse pending、距离传感器及是否允许脉冲作决定。有的 tap/pickup 路径直接 gentleWakeUp，有的请求 pulse，有的只 extendPulse；不是“收到手势就进入 DOZE_PULSING”。

requestPulse 只提出请求态；**实际进入 pulsing 由 DozeUi 的 host pulse callback 驱动**。旧图把 requestPulse 后立刻同步 transitionTo(DOZE_PULSING) 是错误的。


源码：[DozeUi.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/doze/DozeUi.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
private void pulseWhileDozing(int reason) {
    mHost.pulseWhileDozing(
            new DozeHost.PulseCallback() {
                @Override
                public void onPulseStarted() {
                    try {
                        DozeMachine.State requestState = DozeMachine.State.DOZE_PULSING;
                        if (reason == DozeLog.PULSE_REASON_SENSOR_WAKE_REACH) {
                            requestState = DozeMachine.State.DOZE_PULSING_BRIGHT;
                        } else if (reason == DozeLog.REASON_SENSOR_UDFPS_LONG_PRESS
                                || reason == DozeLog.REASON_SENSOR_QUICK_PICKUP) {
                            requestState = DozeMachine.State.DOZE_PULSING_WITHOUT_UI;
                        } else if (reason
                                == DozeLog.PULSE_REASON_FINGERPRINT_PULSE_SHOW_AUTH_UI) {
                            requestState = DozeMachine.State.DOZE_PULSING_AUTH_UI;
                        }

                        mMachine.requestState(requestState);
                    } catch (IllegalStateException e) {
                        // It's possible that the pulse was asynchronously cancelled while
                        // we were waiting for it to start (under stress conditions.)
                        // In those cases we should just ignore it. b/127657926
                    }
                }

                @Override
                public void onPulseFinished() {
                    mMachine.requestState(DozeMachine.State.DOZE_PULSE_DONE);
                }
            }, reason);
}
```


常规脉冲结束请求 PULSE_DONE，然后由 DozeMachine 判断返回 AOD/DOZE 或因正在唤醒而 FINISH。时间更新的 `scheduleTimeTick()` / `onTimeTick()` 属于显示内容更新，并不意味着每分钟必须跑一次完整 pulse 状态链。

#### 触发原因与调试

DozeLog 中 reason 用于区分通知、手势、认证等来源；不同 reason 可能影响 pulse UI 类型。应使用源码常量名，不创造 PULSE_REASON_TIMER 等任意枚举，并核对触发者是否实际传该值。

```text
request origin -> DozeTriggers decision -> requestPulse(reason)
  -> DozeMachine stores reason -> DozeUi selects pulse state
  -> DozeLog / trace: rejected, suppressed, proximity, state, display application
```

诊断需区分“触发没有到达”“被 proximity/策略抑制”“状态已转换但 pending display 尚未应用”“buffer/UI 未更新”。只有单条 screen on/off 日志不能证明整条 AOD 链都成功。

### 3.5 AOD 核心组件源码（Android 17）

#### DozeService：框架生命周期到状态机

插件监听仍可能使用弃用兼容的 onPluginConnected/onPluginDisconnected 回调；这不意味着 17 的 PluginListener 只有两阶段。Service 销毁需撤销监听并销毁状态机，dream 停止与 Android Service destroy 不是相同回调。


源码：[DozeService.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/doze/DozeService.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void onCreate() {
    super.onCreate();

    setWindowless(true);

    mPluginManager.addPluginListener(this, DozeServicePlugin.class, false /* allowMultiple */);
    DozeComponent dozeComponent = mDozeComponentBuilder.build(this);
    mDozeMachine = dozeComponent.getDozeMachine();
}

public void onDestroy() {
    if (mPluginManager != null) {
        mPluginManager.removePluginListener(this);
    }
    super.onDestroy();
    mDozeMachine.destroy();
    mDozeMachine = null;
}

public void onDreamingStarted() {
    super.onDreamingStarted();
    mDozeMachine.requestState(DozeMachine.State.INITIALIZED);
    startDozing();
    if (mDozePlugin != null) {
        mDozePlugin.onDreamingStarted();
    }
}

public void onDreamingStopped() {
    super.onDreamingStopped();
    mDozeMachine.requestState(DozeMachine.State.FINISH);
    if (mDozePlugin != null) {
        mDozePlugin.onDreamingStopped();
    }
}

public void setDozeScreenState(int state) {
    mDozeLog.traceDisplayState(state, /* afterRequest */ false);
    super.setDozeScreenState(state);
    mDozeLog.traceDisplayState(state, /* afterRequest */ true);
    if (mDozeMachine != null) {
        mDozeMachine.onScreenState(state);
    }
}
```


#### DozeHost：UI 与控制策略的边界

DozeHost 把 SystemUI 显示/动画/pulse 行为与 DozeMachine 的状态控制分离。Part 通过接口请求工作，而不是直接操作整个锁屏树。pulseWhileDozing 带 started/finished 回调；startDozing/stopDozing 与 DreamService 同名方法属于不同对象职责。

```text
DozeMachine Parts -> DozeHost
  startDozing / stopDozing
  pulseWhileDozing(PulseCallback, reason) / extendPulse
  isPowerSaveActive / isPulsePending / isAlwaysOnSuppressed
  dozeTimeTick / brightness / gentle-sleep coordination
```

组件注册的 host callback 应按生命周期撤销。仅 setDozeScreenBrightness 改数值不能跳过真实 Display/Dream 协议或设备亮度策略。

#### DozeTriggers：通知、手势与 proximity

以下保留该 tag 的传感器决策方法，而不是把所有非 tap 事件合并为 extendPulse 的伪实现。事件能否进入状态机受理由、遮挡、低功耗/配置和 proximity 等条件影响。


源码：[DozeTriggers.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/doze/DozeTriggers.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
void onSensor(int pulseReason, float screenX, float screenY, float[] rawValues) {
    boolean isDoubleTap = pulseReason == DozeLog.REASON_SENSOR_DOUBLE_TAP;
    boolean isTap = pulseReason == DozeLog.REASON_SENSOR_TAP;
    boolean isPickup = pulseReason == DozeLog.REASON_SENSOR_PICKUP;
    boolean isLongPress = pulseReason == DozeLog.PULSE_REASON_SENSOR_LONG_PRESS;
    boolean isWakeOnPresence = pulseReason == DozeLog.REASON_SENSOR_WAKE_UP_PRESENCE;
    boolean isWakeOnReach = pulseReason == DozeLog.PULSE_REASON_SENSOR_WAKE_REACH;
    boolean isUdfpsLongPress = pulseReason == DozeLog.REASON_SENSOR_UDFPS_LONG_PRESS;
    boolean isQuickPickup = pulseReason == DozeLog.REASON_SENSOR_QUICK_PICKUP;
    boolean isWakeDisplayEvent = isQuickPickup || ((isWakeOnPresence || isWakeOnReach)
            && rawValues != null && rawValues.length > 0 && rawValues[0] != 0);

    if (isWakeOnPresence) {
        onWakeScreen(isWakeDisplayEvent,
                mMachine.getState(),
                pulseReason);
    } else if (isLongPress) {
        requestPulse(pulseReason, true /* alreadyPerformedProxCheck */,
                null /* onPulseSuppressedListener */);
    } else if (isWakeOnReach || isQuickPickup) {
        if (isWakeDisplayEvent) {
            requestPulse(pulseReason, true /* alreadyPerformedProxCheck */,
                    null /* onPulseSuppressedListener */);
        }
    } else {
        proximityCheckThenCall((isNear) -> {
            if (isNear != null && isNear) {
                // In pocket, drop event.
                mDozeLog.traceSensorEventDropped(pulseReason, "prox reporting near");
                return;
            }
            if (isDoubleTap || isTap) {
                mDozeHost.onSlpiTap(screenX, screenY);
                gentleWakeUp(pulseReason);
            } else if (isPickup) {
                if (shouldDropPickupEvent())  {
                    mDozeLog.traceSensorEventDropped(pulseReason, "keyguard occluded");
                    return;
                }
                gentleWakeUp(pulseReason);
            } else if (isUdfpsLongPress) {
                if (canPulse(mMachine.getState(), true)) {
                    mDozeLog.d("updfsLongPress - setting aodInterruptRunnable to run when "
                            + "the display is on");
                    // Since the gesture won't be received by the UDFPS view, we need to
                    // manually inject an event once the display is ON
                    mAodInterruptRunnable = () ->
                            mAuthController.onAodInterrupt((int) screenX, (int) screenY,
                                    rawValues[3] /* major */, rawValues[4] /* minor */);
                } else {
                    mDozeLog.d("udfpsLongPress - Not sending aodInterrupt. "
                            + "Unsupported doze state.");
                }
                requestPulse(DozeLog.REASON_SENSOR_UDFPS_LONG_PRESS, true, null);
            } else {
                mDozeHost.extendPulse(pulseReason);
            }
        }, true /* alreadyPerformedProxCheck */, pulseReason);
    }

    if (isPickup && !shouldDropPickupEvent()) {
        final long timeSinceNotification =
                SystemClock.elapsedRealtime() - mNotificationPulseTime;
        final boolean withinVibrationThreshold =
                timeSinceNotification < mDozeParameters.getPickupVibrationThreshold();
        mDozeLog.tracePickupWakeUp(withinVibrationThreshold);
    }
}

private void onProximityFar(boolean far) {
    // Proximity checks are asynchronous and the user might have interacted with the phone
    // when a new event is arriving. This means that a state transition might have happened
    // and the proximity check is now obsolete.
    if (mMachine.isExecutingTransition()) {
        mDozeLog.d("onProximityFar called during transition. Ignoring sensor response.");
        return;
    }

    final boolean near = !far;
    final DozeMachine.State state = mMachine.getState();
    final boolean paused = (state == DozeMachine.State.DOZE_AOD_PAUSED);
    final boolean pausing = (state == DozeMachine.State.DOZE_AOD_PAUSING);
    final boolean aod = (state == DozeMachine.State.DOZE_AOD);

    if (state == DozeMachine.State.DOZE_PULSING
            || state == DozeMachine.State.DOZE_PULSING_BRIGHT
            || state == State.DOZE_PULSING_WITHOUT_UI
            || state == State.DOZE_PULSING_AUTH_UI) {
        mDozeLog.traceSetIgnoreTouchWhilePulsing(near);
        mDozeHost.onIgnoreTouchWhilePulsing(near);
    }

    if (far && (paused || pausing)) {
        mDozeLog.d("Prox FAR, unpausing AOD");
        mMachine.requestState(DozeMachine.State.DOZE_AOD);
    } else if (near && aod) {
        mDozeLog.d("Prox NEAR, starting pausing AOD countdown");
        mMachine.requestState(DozeMachine.State.DOZE_AOD_PAUSING);
    }
}

public void transitionTo(DozeMachine.State oldState, DozeMachine.State newState) {
    if (oldState == DOZE_SUSPEND_TRIGGERS && (newState != FINISH
            && newState != UNINITIALIZED)) {
        // Register callbacks that were unregistered when we switched to
        // DOZE_SUSPEND_TRIGGERS state.
        registerCallbacks();
    }
    switch (newState) {
        case INITIALIZED:
            mAodInterruptRunnable = null;
            sWakeDisplaySensorState = true;
            registerCallbacks();
            mDozeSensors.requestTemporaryDisable();
            break;
        case DOZE:
            mAodInterruptRunnable = null;
            mWantProxSensor = false;
            mWantSensors = true;
            mWantTouchScreenSensors = true;
            mInAod = false;
            break;
        case DOZE_AOD:
            mAodInterruptRunnable = null;
            mWantProxSensor = true;
            mWantSensors = true;
            mWantTouchScreenSensors = true;
            mInAod = true;
            if (!sWakeDisplaySensorState) {
                onWakeScreen(false, newState, DozeLog.REASON_SENSOR_WAKE_UP_PRESENCE);
            }
            break;
        case DOZE_AOD_PAUSED:
        case DOZE_AOD_PAUSING:
            mWantProxSensor = true;
            break;
        case DOZE_PULSING:
        case DOZE_PULSING_WITHOUT_UI:
        case DOZE_PULSING_AUTH_UI:
        case DOZE_PULSING_BRIGHT:
            mWantProxSensor = true;
            mWantTouchScreenSensors = false;
            break;
        case DOZE_AOD_DOCKED:
            mWantProxSensor = false;
            mWantTouchScreenSensors = false;
            break;
        case DOZE_AOD_MINMODE:
            mWantProxSensor = false;
            mWantTouchScreenSensors = false;
            break;
        case DOZE_PULSE_DONE:
            mDozeSensors.requestTemporaryDisable();
            break;
        case DOZE_SUSPEND_TRIGGERS:
        case FINISH:
            stopListeningToAllTriggers();
            break;
        default:
    }
    mDozeSensors.setListening(mWantSensors, mWantTouchScreenSensors, mInAod);
}
```


#### DozeSensors：注册不等于传感器一定可用

实际 TriggerSensor 数组由设备资源、用户设置、传感器存在性和姿态决定；PluginSensor 还依赖插件协议。不存在的传感器不会因为 settings put 一个开关就出现。订阅与停止订阅必须随 Doze state/触摸/屏幕状态更新，不能一直注册全部传感器。


源码：[DozeSensors.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/doze/DozeSensors.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void setListening(boolean listen, boolean includeTouchScreenSensors,
        boolean includeAodOnlySensors) {
    if (mListening == listen && mListeningTouchScreenSensors == includeTouchScreenSensors
            && mListeningAodOnlySensors == includeAodOnlySensors) {
        return;
    }
    mListening = listen;
    mListeningTouchScreenSensors = includeTouchScreenSensors;
    mListeningAodOnlySensors = includeAodOnlySensors;
    updateListening();
}
```


这段仅展示订阅控制入口，构造器的完整硬件组合没有在文章复制。定位某一个设备手势应沿 TriggerSensor.updateListening/onTrigger、SensorManager callback、DozeTriggers.onSensor 逐层查，并核对资源 sensor type 与 setting；具体硬件触发结果不是静态源码能证明的。

#### DozeScreenState：目标状态与实际应用分开

进入 AOD、pulse 结束、从暂停恢复、显示消隐、UDFPS finger-down 都会影响何时应用目标状态。FINISH 时撤销 pending callback，避免 Service 结束后继续应用旧屏幕状态。详细分支与延时常量放在第 12 章，避免用一个简化 if/else 冒充完整实现。

在本 tag，applyScreenState 除转发 Service 外还更新 DozeInteractor；亮度同步和 STATE_DOZE 处理也有各自条件。后续 UI 层应消费一致的状态，而不是仅观察旧的 screen boolean。


源码：[DozeScreenState.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/doze/DozeScreenState.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
private void applyScreenState(int screenState) {
    if (screenState != Display.STATE_UNKNOWN) {
        if (DEBUG) Log.d(TAG, "setDozeScreenState(" + screenState + ")");
        mDozeService.setDozeScreenState(screenState);
        mDozeInteractor.setDozeScreenState(screenState);
        if (screenState == Display.STATE_DOZE) {
            // If we're entering doze, update the doze screen brightness. We might have been
            // clamping it to the dim brightness during the screen off animation, and we should
            // now change it to the brightness we actually want according to the sensor.
            mDozeScreenBrightness.updateBrightnessAndReady(false /* force */);
        }
        mPendingScreenState = Display.STATE_UNKNOWN;
        mWakeLock.setAcquired(false);
    }
}
```

## 4. 通知系统详解

### 4.1 通知系统概述

通知系统跨 App、system_server 与 SystemUI 三个责任域：App 生成声明式 Notification，NMS 验证/保存运行时记录并分发监听事件，SystemUI 建立可显示条目、分组/过滤/排序并绑定视图。NMS 不直接操纵 SystemUI 的 View。

```text
App NotificationManager.notify
  -> INotificationManager.enqueueNotificationWithTag
system_server NotificationManagerService
  -> enqueueNotificationInternal
  -> EnqueueNotificationRunnable -> PostNotificationRunnable
  -> NotificationListeners.notifyPostedLocked -> listener Binder callback
SystemUI NotificationListener
  -> registered NotificationHandler (including NotifCollection)
  -> NotifCollection -> NotifPipeline / ShadeListBuilder
  -> preparation / inflation / view manager -> notification rows
```

旧 NotificationEntryManager 管线不是此 tag 的当前收集链。要区分 NMS 排名信息与 SystemUI 最终列表排序：后者还受 grouping、section、coordinator、stability 及 UI 状态等影响。

### 4.2 通知发送流程

```java
// Android 17 应用侧示例。调用前已满足适用的 POST_NOTIFICATIONS 授权。
NotificationManager nm = context.getSystemService(NotificationManager.class);
String channelId = "messages";
nm.createNotificationChannel(new NotificationChannel(
        channelId, "消息", NotificationManager.IMPORTANCE_DEFAULT));
Intent open = new Intent(context, TargetActivity.class);
PendingIntent click = PendingIntent.getActivity(context, 0, open,
        PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
Notification notification = new Notification.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_notification)
        .setContentTitle("新消息")
        .setContentText("点击查看")
        .setStyle(new Notification.BigTextStyle().bigText("完整消息正文"))
        .setContentIntent(click)
        .setAutoCancel(true)
        .build();
nm.notify(100, notification);
```

渠道重要性和用户设置决定实际提醒策略；`.setPriority()` 的旧优先级不能覆盖现代 channel 配置。创建 Notification 不代表已经显示：权限拒绝、channel 禁用、速率/数量限制、DND、用户状态及监听可见性会影响结果。

Binder 入口读取调用 UID/PID 与包身份，内部解析用户与渠道，构造 StatusBarNotification/NotificationRecord，经过过滤、信号提取及入队。Enqueue 与 Post 是两个不同阶段：mEnqueuedNotifications 是 ArrayList，不是可以按 key 调 add/get 的 map。

```text
enqueueNotificationInternal
  -> caller/user/channel/notification validation
  -> record + signals + disqualifying feature checks
  -> handler EnqueueNotificationRunnable
       -> under mNotificationLock add to pending collection
       -> assist/ranking-related scheduling
       -> handler PostNotificationRunnable
            -> locate pending record / compare existing record
            -> insert or replace active record + key index
            -> rank, attention, listener events
            -> history condition
            -> finally remove pending record
```

这是关键职责序列，省略锁内细分与功能开关；不是所有通知都先持久化磁盘再回调。活动通知主要在内存，通知历史是条件记录，不支持将任意活动 Notification 自动从磁盘恢复。

### 4.3 通知核心组件

| 类型 | 所在进程 | 实际责任 |
|---|---|---|
| NotificationRecord | system_server | StatusBarNotification、channel、importance、ranking/统计状态 |
| NotificationEntry | SystemUI | sbn/ranking、绑定任务、dismiss/lifetime 状态 |
| NotifCollection | SystemUI | 处理 post/update/remove 与集合事件 |
| ShadeListBuilder | SystemUI | 分组、过滤、section/sort/stability 等建表 |
| ExpandableNotificationRow | SystemUI | 通知行交互、可展开内容与组子项 |
| NotificationContentView | SystemUI | contracted/expanded/heads-up 等内容 View 容器 |

ExpandableNotificationRow 的真实继承链经过 ExpandableOutlineView 等，不是简单 `extends FrameLayout` 加三份 NotificationContentView 的虚构类。实际 private/public layout 与内容 slot 也不是“一个字段 mExpanded 对应全部 RemoteViews”。

分离模型与视图的意义在于异步 inflate、过滤暂不可见条目、处理延长 lifetime 与移除事件。notification 已从 App 发出、已被 NMS 接受、已进入 collection、row 已 inflate、最终进入可见列表，是五个不同检查点。

## 5. NotificationManagerService 深入分析

### 5.1 NMS 架构

```text
NotificationManagerService (SystemService in system_server)
  mService: INotificationManager.Stub -> public Binder entry
  mNotificationLock
    mEnqueuedNotifications: ArrayList<NotificationRecord>
    mNotificationList: ArrayList<NotificationRecord>
    mNotificationsByKey: ArrayMap<String, NotificationRecord>
    mSummaryByGroupKey: ArrayMap<String, NotificationRecord>
  RankingHelper / PreferencesHelper / ZenModeHelper / ConditionProviders
  NotificationAttentionHelper / NotificationUsageStats
  NotificationListeners / NotificationAssistants
  NotificationHistoryManager
```

NotificationRecord 是独立源文件，不是 NMS 内部类；NotificationRankingUpdate 来自 framework service API；ManagedServiceInfo 来自托管服务体系。旧图中的 NotificationList、NotificationStore、ConditionalNotificationCenter 不能作为当前实现类证明。

NMS 的 Binder 服务字段是 `mService`。onStart 发布服务与生命周期初始化相互协作，不能用四个无来源 new 构造器概括整个依赖图。对应用调用，NMS 首先是系统边界：客户端自行拼装的数据不能绕过权限/包身份/用户检查。

### 5.2 NMS 核心流程

以下保留当前 tag 的入队实现，阅读时重点看锁、pending 集合和 Post 调度，而不是把它等同最终发布。后台 Handler 排队也意味着 notify 返回不等于已经在通知栏看见内容。


源码：[NotificationManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/notification/NotificationManagerService.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
protected class EnqueueNotificationRunnable implements Runnable {
    private final NotificationRecord r;
    private final int userId;
    private final boolean isAppForeground;
    private final boolean isAppProvided;
    private final PostNotificationTracker mTracker;

    EnqueueNotificationRunnable(int userId, NotificationRecord r, boolean foreground,
            boolean isAppProvided, PostNotificationTracker tracker) {
        this.userId = userId;
        this.r = r;
        this.isAppForeground = foreground;
        this.isAppProvided = isAppProvided;
        this.mTracker = checkNotNull(tracker);
    }

    @Override
    public void run() {
        boolean enqueued = false;
        try {
            enqueued = enqueueNotification();
        } finally {
            if (!enqueued) {
                mTracker.cancel();
                synchronized (mNotificationLock) {
                    markOffloadedBitmapsForDeletion(r);
                }
            }
        }
    }

    /**
     * @return True if we successfully enqueued the notification and handed off the task of
     * posting it to a background thread; false otherwise.
     */
    private boolean enqueueNotification() {
        synchronized (mNotificationLock) {
            // allowlistToken is populated by unparceling, so it will be absent if the
            // EnqueueNotificationRunnable is created directly by NMS (as we do for group
            // summaries) instead of via notify(). Fix that.
            r.getNotification().overrideAllowlistToken(ALLOWLIST_TOKEN);

            final long snoozeAt =
                    mSnoozeHelper.getSnoozeTimeForUnpostedNotification(
                            r.getUser().getIdentifier(),
                            r.getSbn().getPackageName(), r.getSbn().getKey());
            final long currentTime = System.currentTimeMillis();
            if (snoozeAt > currentTime) {
                (new SnoozeNotificationRunnable(r.getSbn().getKey(),
                        snoozeAt - currentTime, null)).snoozeLocked(r);
                return false;
            }

            final String contextId =
                    mSnoozeHelper.getSnoozeContextForUnpostedNotification(
                            r.getUser().getIdentifier(),
                            r.getSbn().getPackageName(), r.getSbn().getKey());
            if (contextId != null) {
                (new SnoozeNotificationRunnable(r.getSbn().getKey(),
                        0, contextId)).snoozeLocked(r);
                return false;
            }

            final StatusBarNotification n = r.getSbn();
            if (DBG) Slog.d(TAG, "EnqueueNotificationRunnable.run for: " + n.getKey());
            NotificationRecord old = mNotificationsByKey.get(n.getKey());
            if (old != null) {
                // Retain ranking information from previous record
                r.copyRankingInformation(old);
            }

            // If we don't have a previous record, before adding this record to enqueued list,
            // see if we have a previously enqueued version of this notification so we can share
            // instance ID if necessary.
            NotificationRecord previouslyEnqueued = null;
            if (old == null) {
                previouslyEnqueued = findNotificationByListLocked(mEnqueuedNotifications,
                        n.getKey());
            }

            mEnqueuedNotifications.add(r);
            mTtlHelper.scheduleTimeoutLocked(r, SystemClock.elapsedRealtime());

            // Either initialize instance ID for statsd logging, or carry over from old SBN.
            if (old != null && old.getSbn().getInstanceId() != null) {
                n.setInstanceId(old.getSbn().getInstanceId());
            } else if (previouslyEnqueued != null
                    && previouslyEnqueued.getSbn().getInstanceId() != null) {
                n.setInstanceId(previouslyEnqueued.getSbn().getInstanceId());
            } else {
                n.setInstanceId(mNotificationInstanceIdSequence.newInstanceId());
            }

            final int callingUid = n.getUid();
            final int callingPid = n.getInitialPid();
            final Notification notification = n.getNotification();
            final String pkg = n.getPackageName();
            final int id = n.getId();
            final String tag = n.getTag();

            // We need to fix the notification up a little for bubbles
            updateNotificationBubbleFlags(r, isAppForeground);

            // Handle grouped notifications and bail out early if we
            // can to avoid extracting signals.
            handleGroupedNotificationLocked(r, old, callingUid, callingPid);

            if (enablePersonalContextService()) {
                final PersonalContextManagerInternal pcmi =
                        getLocalService(PersonalContextManagerInternal.class);
                if (pcmi != null) {
                    final NotificationRankingUpdate update = makeRankingUpdateLocked(null);
                    final NotificationEvent event =
                            new NotificationEnqueuedEvent(
                                    r.getSbn(), r.getChannel(), update.getRankingMap());
                    pcmi.onNotificationEvent(event);
                }
            }

            // if this is a group child, unsnooze parent summary
            if (n.isGroup() && notification.isGroupChild()) {
                mSnoozeHelper.repostGroupSummary(pkg, r.getUserId(), n.getGroupKey());
            }

            // This conditional is a dirty hack to limit the logging done on
            //     behalf of the download manager without affecting other apps.
            if (!pkg.equals("com.android.providers.downloads")
                    || Log.isLoggable("DownloadManager", Log.VERBOSE)) {
                int enqueueStatus = EVENTLOG_ENQUEUE_STATUS_NEW;
                if (old != null) {
                    enqueueStatus = EVENTLOG_ENQUEUE_STATUS_UPDATE;
                }
                int appProvided = isAppProvided ? 1 : 0;
                EventLogTags.writeNotificationEnqueue(callingUid, callingPid,
                        pkg, id, tag, userId, notification.toString(),
                        enqueueStatus, appProvided);
            }

            // tell the assistant service about the notification
            if (mAssistants.isEnabled()) {
                mAssistants.onNotificationEnqueuedLocked(r);
                mHandler.postDelayed(
                        new PostNotificationRunnable(r.getKey(), r.getSbn().getPackageName(),
                                r.getUid(), mTracker),
                        DELAY_FOR_ASSISTANT_TIME);
            } else {
                mHandler.post(
                        new PostNotificationRunnable(r.getKey(), r.getSbn().getPackageName(),
                                r.getUid(), mTracker));
            }
            return true;
        }
    }
}
```


Post 阶段负责最终加入/更新活动记录。旧记录参与视觉中断判断和更新统计；终止路径也必须从 pending 列表移除相应条目，否则会留下“入队但永不发布”的残留状态。下列真实实现可用来核对这些分支：


```java
protected class PostNotificationRunnable implements Runnable {
    private final String key;
    private final String pkg;
    private final int uid;
    private final PostNotificationTracker mTracker;

    PostNotificationRunnable(String key, String pkg, int uid, PostNotificationTracker tracker) {
        this.key = key;
        this.pkg = pkg;
        this.uid = uid;
        this.mTracker = checkNotNull(tracker);
    }

    @Override
    public void run() {
        boolean posted = false;
        try {
            posted = postNotification();
        }  catch (Exception e) {
            Slog.e(TAG, "Error posting", e);
        } finally {
            if (!posted) {
                mTracker.cancel();
            }
        }
    }

    /**
     * @return True if we successfully processed the notification and handed off the task of
     * notifying all listeners to a background thread; false otherwise.
     */
    private boolean postNotification() {
        boolean appBanned = !areNotificationsEnabledForPackageInt(uid);
        boolean isCallNotification = isCallNotification(pkg, uid);
        boolean posted = false;
        synchronized (NotificationManagerService.this.mNotificationLock) {
            try {
                NotificationRecord r = findNotificationByListLocked(mEnqueuedNotifications,
                        key);
                if (r == null) {
                    Slog.i(TAG, "Cannot find enqueued record for key: " + key);
                    return false;
                }

                final StatusBarNotification n = r.getSbn();
                final Notification notification = n.getNotification();
                boolean isCallNotificationAndCorrectStyle = isCallNotification
                        && notification.isStyle(Notification.CallStyle.class);

                if (favoritesIncomingCallLights()) {
                    int callType = notification.extras.getInt(Notification.EXTRA_CALL_TYPE, -1);
                    boolean isIncomingCall =
                            callType == Notification.CallStyle.CALL_TYPE_INCOMING;
                    r.setIsRealCallIncomingNotification(
                            isCallNotificationAndCorrectStyle && isIncomingCall);
                }

                if (!(notification.isMediaNotification() || isCallNotificationAndCorrectStyle)
                        && (appBanned || isRecordBlockedLocked(r))) {
                    mUsageStats.registerBlocked(r);
                    if (DBG) {
                        Slog.e(TAG, "Suppressing notification from package " + pkg);
                    }
                    return false;
                }

                if (isBridgedNotificationBlocked(r)) {
                    mUsageStats.registerBlocked(r);
                    if (DBG) {
                        Slog.e(TAG, "Suppressing bridged notification on behalf of package "
                                + r.getBridgedPackageName());
                    }
                    return false;
                }

                // Check if this is an updated for a summary for an aggregated sparse
                // group and remove it because that summary has been canceled
                if (mGroupHelper.isUpdateForCanceledSummary(r)) {
                    if (DBG) {
                        Log.w(TAG,
                                "Suppressing notification because summary was canceled: "
                                        + r);
                    }
                    String groupKey = r.getGroupKey();
                    NotificationRecord groupSummary = mSummaryByGroupKey.get(groupKey);
                    if (groupSummary != null && groupSummary.getKey().equals(r.getKey())) {
                        mSummaryByGroupKey.remove(groupKey);
                    }
                    return false;
                }

                final boolean isPackageSuspended =
                        isPackagePausedOrSuspended(r.getSbn().getPackageName(), r.getUid());
                r.setHidden(isPackageSuspended);
                if (isPackageSuspended) {
                    mUsageStats.registerSuspendedByAdmin(r);
                }
                NotificationRecord old = mNotificationsByKey.get(key);

                int index = indexOfNotificationLocked(n.getKey());
                if (index < 0) {
                    mNotificationList.add(r);
                    mUsageStats.registerPostedByApp(r);
                    mUsageStatsManagerInternal.reportNotificationPosted(r.getSbn().getOpPkg(),
                            r.getSbn().getUser(), mTracker.getStartTime());
                    final boolean isInterruptive = isVisuallyInterruptive(null, r);
                    r.setInterruptive(isInterruptive);
                    r.setTextChanged(isInterruptive);
                } else {
                    old = mNotificationList.get(index);  // Potentially *changes* old
                    mNotificationList.set(index, r);
                    mUsageStats.registerUpdatedByApp(r, old);
                    mUsageStatsManagerInternal.reportNotificationUpdated(r.getSbn().getOpPkg(),
                            r.getSbn().getUser(), mTracker.getStartTime());
                    // Make sure we don't lose the foreground service state.
                    notification.flags |=
                            old.getNotification().flags & FLAG_FOREGROUND_SERVICE;
                    // Make sure we don't lose the computer control flag state.
                    if (android.companion.virtualdevice.flags.Flags.computerControlAccess()) {
                        notification.flags |=
                                old.getNotification().flags & FLAG_COMPUTER_CONTROL;
                    }
                    r.isUpdate = true;
                    final boolean isInterruptive = isVisuallyInterruptive(old, r);
                    r.setTextChanged(isInterruptive);
                    if (isInterruptive) {
                        r.resetRankingTime();
                    }
                    markOffloadedBitmapsForDeletion(old);
                }

                mNotificationsByKey.put(n.getKey(), r);

                // Ensure if this is a foreground service that the proper additional
                // flags are set.
                if (notification.isForegroundService()) {
                    notification.flags |= FLAG_NO_CLEAR;
                }

                // Ensure if this is a computer control notification that the proper additional
                // flags are set.
                if (android.companion.virtualdevice.flags.Flags.computerControlAccess()
                        && notification.isComputerControl()) {
                    notification.flags |= FLAG_NO_CLEAR | FLAG_NO_DISMISS;
                    notification.flags &= ~FLAG_AUTO_CANCEL;
                }

                // Posts the notification if it has a small icon, and potentially autogroup
                // the new notification.
                if (notification.getSmallIcon() != null && !isCritical(r)) {
                    StatusBarNotification oldSbn = (old != null) ? old.getSbn() : null;
                    if (oldSbn == null || !Objects.equals(oldSbn.getGroup(), n.getGroup())
                            || !Objects.equals(oldSbn.getNotification().getGroup(),
                                n.getNotification().getGroup())
                            || oldSbn.getNotification().flags
                            != n.getNotification().flags
                            || !old.getChannel().getId().equals(r.getChannel().getId())
                            || old.hasAdjustment(KEY_GROUP_KEY)) {
                        synchronized (mNotificationLock) {
                            final String autogroupName
                                    = GroupHelper.getFullAggregateGroupKey(r);
                            boolean willBeAutogrouped =
                                    mGroupHelper.onNotificationPosted(r,
                                        hasAutoGroupSummaryLocked(r));
                            if (willBeAutogrouped) {
                                // The newly posted notification will be autogrouped, but
                                // was not autogrouped onPost, to avoid an unnecessary sort.
                                // We add the autogroup key to the notification without a
                                // sort here, and it'll be sorted below with extractSignals.
                                addAutogroupKeyLocked(key,
                                        autogroupName, /*requestSort=*/false);
                            } else {
                                // Wait 3 seconds so that the app has a chance to post
                                // a group summary or children (complete a group)
                                mHandler.postDelayed(() -> {
                                    synchronized (mNotificationLock) {
                                        NotificationRecord record =
                                                mNotificationsByKey.get(key);
                                        if (record != null) {
                                            mGroupHelper.onNotificationPostedWithDelay(
                                                    record, mNotificationList,
                                                    mSummaryByGroupKey);
                                        }
                                    }
                                }, key, DELAY_FORCE_REGROUP_TIME);
                            }
                         }
                    }
                }

                mRankingHelper.extractSignals(r);
                mRankingHelper.sort(mNotificationList);
                final int position = mRankingHelper.indexOf(mNotificationList, r);

                int buzzBeepBlinkLoggingCode = 0;
                if (!r.isHidden()) {
                    if (mGroupHelper.isSummaryWithAllChildrenBundled(r, mNotificationList,
                            mEnqueuedNotifications)) {
                        notification.flags |= Notification.FLAG_SILENT;
                    }

                    buzzBeepBlinkLoggingCode = mAttentionHelper.buzzBeepBlinkLocked(r,
                            new NotificationAttentionHelper.Signals(
                                    mUserProfiles.isCurrentProfile(r.getUserId()),
                                    mListenerHints));
                }

                if (notification.getSmallIcon() != null) {
                    NotificationRecordLogger.NotificationReported maybeReport =
                            mNotificationRecordLogger.prepareToLogNotificationPosted(r, old,
                                    position, buzzBeepBlinkLoggingCode,
                                    getGroupInstanceId(r.getSbn().getGroupKey()));
                    notifyListenersPostedAndLogLocked(r, old, mTracker, maybeReport);
                    posted = true;
                } else {
                    Slog.e(TAG, "Not posting notification without small icon: " + notification);
                    if (old != null && !old.isCanceled) {
                        mListeners.notifyRemovedLocked(r, REASON_ERROR, r.getStats());
                        mHandler.post(() -> {
                            synchronized (mNotificationLock) {
                                mGroupHelper.onNotificationRemoved(r, mNotificationList,
                                        /* sendingDelete= */ false);
                            }
                        });
                    }

                    if (callstyleCallbackApi()) {
                        notifyCallNotificationEventListenerOnRemoved(r);
                    }

                    // ATTENTION: in a future release we will bail out here
                    // so that we do not play sounds, show lights, etc. for invalid
                    // notifications
                    Slog.e(TAG, "WARNING: In a future release this will crash the app: "
                            + n.getPackageName());
                }

                if (mShortcutHelper != null) {
                    mShortcutHelper.maybeListenForShortcutChangesForBubbles(r,
                            false /* isRemoved */);
                }

                maybeRecordInterruptionLocked(r);
                maybeRegisterMessageSent(r);
                maybeReportForegroundServiceUpdate(r, true);
            } finally {
                int N = mEnqueuedNotifications.size();
                for (int i = 0; i < N; i++) {
                    final NotificationRecord enqueued = mEnqueuedNotifications.get(i);
                    if (Objects.equals(key, enqueued.getKey())) {
                        mEnqueuedNotifications.remove(i);
                        break;
                    }
                }
            }
        }
        return posted;
    }
}
```


#### 取消、更新与用户可见性的区别

同一通知 key 更新通常替换旧记录，而不是无条件 append 新 row。key 由 StatusBarNotification 的身份组成，不能调用不存在的 Notification.keyFor 伪造唯一规则。取消经过 NMS 的 cancel 相关校验与事件分发，SystemUI 还有消除拦截、lifetime extension 和动画收尾，不等于 removeView 立即完成全部删除。

DND 拦截提醒、channel 禁用、锁屏隐私隐藏、SystemUI section 过滤是不同层次；“没响”和“没投递”和“列表不显示”不能混在一个 isBlocked 布尔量中排查。第 11 章进一步分析 rank、attention、偏好与历史存储的真实边界。

## 6. RemoteViews 深度解析

### 6.1 RemoteViews 原理

```text
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
PendingIntent pendingIntent = PendingIntent.getActivity(context, 0, intent, PendingIntent.FLAG_IMMUTABLE);
views.setOnClickPendingIntent(R.id.button, pendingIntent);
```

### 6.4 Actions 机制深度解析

RemoteViews 不把运行中的 View 对象序列化到 SystemUI，而是传布局/资源来源、变体和可回放的 Action。View 持有 Context、Handler、窗口与 native 资源，这些不能按普通对象跨进程复制；Action 只记录目标 View ID、受支持的操作及数据。

```text
App: RemoteViews(pkg, layoutId)
       -> setTextViewText(id, text) -> ReflectionAction
       -> setImageViewBitmap(id, bitmap) -> BitmapReflectionAction / bitmap cache
       -> setOnClickPendingIntent(id, pi) -> SetOnClickResponse
       -> serialize Notification/RemoteViews

SystemUI: decode -> choose layout variant -> inflate allowed Views
          -> performApply -> action.apply(root, parent, ActionApplyParams)
          -> render in SystemUI's own view tree
```

#### 当前 Action 的真实映射

| API | 固定 tag 的相关实现 | 为什么不是统一 setXXX 类 |
|---|---|---|
| setTextViewText | ReflectionAction，setCharSequence("setText") | 方法名与参数类型受校验 |
| setTextColor / setImageViewResource | ReflectionAction | 反射的是受支持单参数方法 |
| setTextViewTextSize | TextViewSizeAction | units 与 size 两个参数需要专门 action |
| setImageViewBitmap | BitmapReflectionAction | bitmap cache 与内存传输不同于普通参数 |
| setOnClickPendingIntent | SetOnClickResponse | 点击响应、PendingIntent 与安全启动协作 |
| setProgressBar | 多个 setBoolean/setInt 操作 | 不是虚构 SetProgressBarAction |
| setViewPadding | ViewPaddingAction | 多参数操作 |
| addView / removeAllViews | ViewGroupActionAdd / ViewGroupActionRemove | 子 RemoteViews 与回收/移除策略 |

这些类型是实现细节，不是 SDK 保证的序列化 ABI。ReflectionAction 的 tag 在该版为 2，点击 response tag 为 1；旧表颠倒了两者。不要编造通用 decoder 依赖 tag=1 是 ReflectionAction，更不要认为通知 Parcel 可以手写固定字段顺序跨版本解析。

#### 反射不是任意方法执行

`BaseReflectionAction` 先找到目标 View，并根据 action 类型确定参数类别；内部 `getMethod()` 检查方法签名及 `@RemotableViewMethod`，然后缓存 MethodHandle。带泛型参数的支持类型还有类型实参匹配，异步实现通过注解 asyncImpl 指向另一个返回 Runnable 的方法。


源码：[RemoteViews.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/widget/RemoteViews.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
private static MethodHandle getMethod(View view, String methodName,
        @Nullable Class<?> paramType, @Nullable Class<?> paramTypeArgument, boolean async) {
    MethodArgs result;
    Class<? extends View> klass = view.getClass();

    synchronized (sMethods) {
        // The key is defined by the view class, param class and method name.
        sLookupKey.set(klass, paramType, paramTypeArgument, methodName);
        result = sMethods.get(sLookupKey);

        if (result == null) {
            Method method;
            try {
                if (paramType != null && paramTypeArgument != null) {
                    method = klass.getMethod(methodName, paramType);
                    Type actualParam = method.getGenericParameterTypes()[0];
                    if (!(actualParam instanceof ParameterizedType)) {
                        throw new NoSuchMethodException(
                                String.format("Found %s but its parameter is %s, not generic",
                                        method, actualParam));
                    }
                    Type actualParamTypeArg =
                            ((ParameterizedType) actualParam).getActualTypeArguments()[0];
                    if (!paramTypeArgument.equals(actualParamTypeArg)) {
                        throw new NoSuchMethodException(
                                String.format(
                                        "Found %s but it accepts %s and I wanted %s<%s>",
                                        method, actualParam, paramType, paramTypeArgument));
                    }
                } else if (paramType != null) {
                    method = klass.getMethod(methodName, paramType);
                } else {
                    method = klass.getMethod(methodName);
                }
                if (!method.isAnnotationPresent(RemotableViewMethod.class)) {
                    throw new ActionException("view: " + klass.getName()
                            + " can't use method with RemoteViews: "
                            + methodName + parametersToString(paramType, paramTypeArgument));
                }

                result = new MethodArgs();
                result.syncMethod = MethodHandles.publicLookup().unreflect(method);
                result.asyncMethodName =
                        method.getAnnotation(RemotableViewMethod.class).asyncImpl();
            } catch (NoSuchMethodException | IllegalAccessException ex) {
                throw new ActionException("view: " + klass.getName() + " doesn't have method: "
                        + methodName + parametersToString(paramType, paramTypeArgument), ex);
            }

            MethodKey key = new MethodKey();
            key.set(klass, paramType, paramTypeArgument, methodName);
            sMethods.put(key, result);
        }

        if (!async) {
            return result.syncMethod;
        }
        // Check this so see if async method is implemented or not.
        if (result.asyncMethodName.isEmpty()) {
            return null;
        }
        // Async method is lazily loaded. If it is not yet loaded, load now.
        if (result.asyncMethod == null) {
            MethodType asyncType = result.syncMethod.type()
                    .dropParameterTypes(0, 1).changeReturnType(Runnable.class);
            try {
                result.asyncMethod = MethodHandles.publicLookup().findVirtual(
                        klass, result.asyncMethodName, asyncType);
            } catch (NoSuchMethodException | IllegalAccessException ex) {
                throw new ActionException("Async implementation declared as "
                        + result.asyncMethodName + " but not defined for " + methodName
                        + ": public Runnable " + result.asyncMethodName + " ("
                        + TextUtils.join(",", asyncType.parameterArray()) + ")");
            }
        }
        return result.asyncMethod;
    }
}
```


因此安全性不来自“调用者只能写 SDK 硬编码 methodName”。`setInt/setBoolean/setCharSequence` 本身允许提供方法名，methodName 也会通过序列化传输；关键在接收端重新校验。直接 getMethod + invoke 而省略注解检查的旧示例，会错误表达安全边界。

#### 序列化、缓存和变体

RemoteViews 可包含 ApplicationInfo/资源来源、布局 ID、bitmap 缓存、action 列表以及多布局/尺寸变体等。Action 通过 tag 选择对应读入逻辑；完整 writeToParcel/read 构造器才是布局顺序依据，不能用“包名、布局、count、actions、bitmap”伪格式冒充。

```text
logical data, not a wire-format specification:
  resource identity + layout variant
  shared/cached bitmap data
  ordered list of action type + action payload
  additional flags / state required by this version
```

bitmap cache 可减少重复对象传输，但不取消 Binder/进程内存预算。大图应按显示需求缩小，通知更新也应控制频率；“只传 Action 所以无限便宜”是不成立的。

#### apply/reapply 与异步绑定

`apply()` 通常建立新 View 树并应用操作；`reapply()` 在满足布局/类型兼容条件时复用现有树。SystemUI 会检查 package/layout 与缓存等条件，再选择 apply/reapply 或异步版本，而不是每次通知更新都无条件复用。

```text
new content required?
  -> yes: create/recover Notification.Builder and RemoteViews variants
  -> same compatible layout + cached view?
       yes: reapply/reapplyAsync
       no:  apply/applyAsync
  -> completion: attach correct content slot, update cache
  -> failure/cancellation: discard obsolete result, report inflation error
```

异步 inflate 的耗时部分可在后台，最终 UI 更新需回到相应线程。旧任务取消与新通知版本更新之间存在竞态，必须避免旧结果覆盖新状态；文章不能通过一个同步 for-loop 忽略这些生命周期。

### 6.5 反射创建与 View 白名单机制

“白名单”可作为安全模型称呼，但当前实现并不是维护 `sAllowedViewClasses` 字符串数组。RemoteViews 实现 LayoutInflater.Filter；接口接收 `Class`，通过 `@RemoteViews.RemoteView` 检查类，不是 `onLoadClass(ClassLoader, String)`。


```java
public boolean onLoadClass(Class clazz) {
    return clazz.isAnnotationPresent(RemoteView.class);
}
```


LayoutInflater 在加载/解析 Class 后检查 Filter，允许的类才进入构造流程。注解早于 Android 12 就已存在，不是该版才“自动注册”；RemoteView 注解自身也不是 View，GridLayout.LayoutParams 更不能列为可 inflate 的 View 类型。

#### 三个需要同时存在的边界

1. **资源 Context**：按发起方的资源身份解析布局、drawable、字符串，并处理用户/配置；不是用纯 SystemUI Resources 查应用 R.layout 数字。
2. **类加载与 View Filter**：宿主不因此自动加载 App 自定义类代码，平台允许的 View 还要通过注解过滤。
3. **Action 方法检查**：方法存在还不够，签名/参数类型及 RemotableViewMethod 都要满足。

```text
RemoteViews.apply
  -> select matching remote layout
  -> build resource-aware Context + cloned inflater
  -> install RemoteViews class filter
  -> inflate View tree
       class load -> onLoadClass(Class) -> allowed constructor
  -> performApply
       target ID -> typed action -> checked MethodHandle / specific action
```

仅给第三方 View 标注 RemoteView 不会使其类自动可在 SystemUI 加载；也不应该把 SystemUI 插件代码机制与 RemoteViews 混合。前者是受信代码执行，后者面向外部应用的受限声明式 UI。

#### 为什么不能简单序列化自定义 View

构造函数/draw 可执行任意逻辑，若直接在高权限宿主中运行会破坏进程与权限边界。RemoteViews 因而传“布局身份和操作”，不是传“实现代码”。View 过滤、资源来源和方法检查保护不同阶段，缺少任意一层都会改变安全模型。

这也解释为什么 RemoteViews 只能表达特定操作，不能像普通 View 那样任意调用业务方法。真正需要自定义交互时，应用应设计合适的通知样式和 PendingIntent，而不是尝试向 SystemUI 注入自定义控件类。

#### 点击与集合模板

单 View 点击使用 PendingIntent；集合子项的模板/fill-in Intent 是另一种协议。PendingIntent 的 creator 身份、mutable/immutable、目标显式性和后台 Activity 启动限制仍然生效。普通打开页面的点击通常选 immutable，RemoteInput 等需要系统补充数据的场景按其契约选择，不应统一给所有 pending intent 使用 flags=0。

本文的独立 RemoteViews 示例用于展示 API，不包含完整通知 permission/channel 生命周期；应用在目标系统上应测试初次显示、同布局更新、布局变更、图片失败、取消与锁屏隐私两种内容版本。

## 7. SystemUI 与 Framework 协作

### 7.1 通知协作流程

```text
Application -> NotificationManager -> NMS permission/channel/record
NMS -> managed notification listener Binder callback
SystemUI NotificationListener -> NotifCollection events
NotifPipeline / ShadeListBuilder -> grouped/filtered ordered list
Preparation/inflation -> content views
ShadeViewManager / notification stack -> display and interaction
User dismiss/click -> SystemUI event / PendingIntent -> system coordination
```

资源 inflation 不发生在 NMS，它只传通知数据/受控信息。声音、振动、气泡资格与锁屏隐私也有不同所有者，不能画成 NMS 直接调用 `mSystemUI.onNotificationPosted()` 再向 row setContent 的同步方法调用。

活动记录、用户偏好与通知历史三者要分开：活动列表在内存；偏好持久化保存渠道等策略；历史记录仅保留选定信息供用户查看，并非完整可重放的通知。这种分层使 SystemUI 重连可从 NMS 取活动快照，而不是从历史文件“恢复全部通知”。

## 8. 通知渲染流程

### 8.1 渲染架构

```text
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

#### 接收与集合更新

NotificationListener 把已处理的 post 事件派发给注册的 NotificationHandler，NotifCollection 消费 sbn 与 RankingMap，创建/更新 entry 并驱动重建。收集模型与视图建立分开，使取消、重复更新和异步 inflation 能按一致事件顺序处理。


源码：[NotificationListener.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/statusbar/NotificationListener.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void onNotificationPosted(final StatusBarNotification sbn,
        final RankingMap rankingMap) {
    if (DEBUG) Log.d(TAG, "onNotificationPosted: " + sbn);
    String key = sbn.getKey();
    if (!isKeyInRankingMap(key, rankingMap)) {
        Log.wtf(TAG, "Got bad rankingMap in onNotificationPosted for "
                + key);
    }
    if (sbn != null && !onPluginNotificationPosted(sbn, rankingMap)) {
        if (!isKeyInRankingMap(key, rankingMap)) {
            Log.wtf(TAG, "Missing ranking after plugins for " + key);
        }
        mMainExecutor.execute(() -> {
            for (NotificationHandler handler : mNotificationHandlers) {
                handler.onNotificationPosted(sbn, rankingMap);
            }
        });
    } else if (isKeyInRankingMap(key, rankingMap)) {
        Log.wtf(TAG, "Plugin prevented post but left ranking " + key);
    }
}
```


源码：[NotifCollection.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/statusbar/notification/collection/NotifCollection.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
private void onNotificationPosted(StatusBarNotification sbn, RankingMap rankingMap) {
    Assert.isMainThread();

    postNotification(sbn, requireRanking(rankingMap, sbn.getKey()));
    applyRanking(rankingMap);
    dispatchEventsAndRebuildList("onNotificationPosted");
}

private void dispatchEventsAndRebuildList(String reason) {
    Trace.beginSection("NotifCollection.dispatchEventsAndRebuildList");
    if (mMainHandler.hasCallbacks(mRebuildListRunnable)) {
        mMainHandler.removeCallbacks(mRebuildListRunnable);
    }

    dispatchEvents();

    if (mBuildListener != null) {
        mBuildListener.onBuildList(mReadOnlyNotificationSet, reason);
    }
    Trace.endSection();
}
```


#### 建表、准备与内容绑定

ShadeListBuilder 处理 grouping/filtering/排序稳定性，PreparationCoordinator 在合适阶段启动需要的 inflate，未完成或失败的条目可被过滤；并非所有组内 child 永远保持 fully inflated。视图绑定与最终加入列表要分别观察。

`RowContentBindStage` 根据 dirty/required flags 请求绑定或释放内容。当前具体 binder 是 **`NotificationRowContentBinderImpl.kt`**，不是旧 `NotificationContentInflater.java`。源码保留的 `NotificationContentInflater...` trace 字符串同样不证明该旧类仍存在。


源码：[NotificationRowContentBinderImpl.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/statusbar/notification/row/NotificationRowContentBinderImpl.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
override fun bindContent(
    entry: NotificationEntry,
    row: ExpandableNotificationRow,
    @InflationFlag contentToBind: Int,
    bindParams: BindParams,
    forceInflate: Boolean,
    callback: InflationCallback?,
) {
    if (row.isRemoved) {
        // We don't want to reinflate anything for removed notifications. Otherwise views might
        // be readded to the stack, leading to leaks. This may happen with low-priority groups
        // where the removal of already removed children can lead to a reinflation.
        logger.logNotBindingRowWasRemoved(row.loggingKey)
        return
    }
    logger.logBinding(row.loggingKey, contentToBind)
    val sbn: StatusBarNotification = entry.sbn

    // To check if the notification has inline image and preload inline image if necessary.
    row.imageResolver.preloadImages(sbn.notification)
    if (forceInflate) {
        remoteViewCache.clearCache(entry)
    }

    // Cancel any pending frees on any view we're trying to bind since we should be bound after.
    cancelContentViewFrees(row, contentToBind)
    val task =
        AsyncInflationTask(
            inflationExecutor,
            inflateSynchronously,
            userProfileBadgeProvider,
            /* reInflateFlags = */ contentToBind,
            remoteViewCache,
            entry,
            conversationProcessor,
            row,
            bindParams,
            callback,
            remoteInputManager.remoteViewsOnClickHandler,
            /* isMediaFlagEnabled = */ smartReplyStateInflater,
            notifLayoutInflaterFactoryProvider,
            headsUpStyleProvider,
            promotedNotificationContentExtractor,
            logger,
        )
    if (inflateSynchronously) {
        task.onPostExecute(task.doInBackground())
    } else {
        task.executeOnExecutor(inflationExecutor)
    }
}
```


bindContent 会依据 flags、cache 与同步/异步选择建立任务。任务从通知恢复 Builder，根据 contracted/expanded/heads-up/public 等需要生成 RemoteViews，再走 apply/reapply。finish 阶段设置相应内容 slot、更新缓存并完成回调，失败时由 inflation error 路径处理。

```text
notification update -> abort/replace old binding task
  -> recover Builder + resolve package resource Context
  -> create requested RemoteViews variants
  -> apply/reapply or async equivalents
  -> valid latest task completes
       -> update NotificationContentView children + cache
       -> row update / inflation callback
  -> obsolete/cancelled/failed task does not overwrite latest content
```

`ExpandableNotificationRow` 不是自己直接从 Notification.contentView 三字段同步 addView 的简化实现。现代 template 可在 SystemUI 端由 Builder 生成，原始 Notification 的这些字段不必全部预先填满。

#### 复用与重建的判断

复用需要新旧 RemoteViews 的 package/layout 等兼容，并且 view cache、绑定 flags、功能开关满足条件。布局 ID 相同也不能保证任何主题/配置/自定义 action 都可随意重用；出错时应重建或报告，而不是留下半更新界面。


```kotlin
fun canReapplyRemoteView(newView: RemoteViews?, oldView: RemoteViews?): Boolean {
    return newView == null && oldView == null ||
        newView != null &&
            oldView != null &&
            oldView.getPackage() != null &&
            newView.getPackage() != null &&
            newView.getPackage() == oldView.getPackage() &&
            newView.layoutId == oldView.layoutId &&
            !oldView.hasFlags(RemoteViews.FLAG_REAPPLY_DISALLOWED)
}
```


静态分析能证明有这些条件与回调，不能证明某一通知在真机必然走 reapplyAsync、也不能估计其耗时。回归应覆盖同 key 更新、模板变更、取消途中完成、屏幕配置变化和 public/private 内容切换。

## 9. 通知模板系统

### 9.1 通知模板类型

```text
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
        .bigLargeIcon((Bitmap) null)  // 展开时隐藏大图标
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
    .setIcon(IconCompat.createWithBitmap(iconBitmap)) // 此示例使用 androidx.core.app.Person
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

// 6. CallStyle：平台 API 31 起；NotificationCompat 按库与系统能力适配
Person caller = new Person.Builder()
    .setName("张三")
    .setIcon(IconCompat.createWithBitmap(iconBitmap)) // 此示例使用 androidx.core.app.Person
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

模板是 Framework 的 Notification.Builder/Style 与平台布局资源共同生成的 RemoteViews，不是每个 Style 都实现 `populateContentView/populateBigContentView`。固定 tag 的入口包括 createContentView/createBigContentView/createHeadsUpContentView，Style 可提供相应 make 方法。

App build Notification 时会保存样式数据；现代路径下，SystemUI 的内容绑定器可 recoverBuilder 并在需要时生成视图。因此不能说“所有 RemoteViews 都在 App 的 build() 里已经完全生成”，也不能只读取 notification.bigContentView 作为唯一来源。

```text
App Notification.Builder + Style + extras
  -> Notification payload (may include custom RemoteViews)
SystemUI NotificationRowContentBinderImpl
  -> recovered Builder / package context
  -> createContentView / createBigContentView / heads-up variant
       -> Style make* method or standard template
       -> framework layout resources + actions
  -> inflate/bind according to content flags
```

系统模板的布局会包含大量 include、尺寸/字体/颜色资源以及内部控件。下方只展示**应用自定义布局示例**，不把简单 FrameLayout 冒充 `core/res/res/layout/notification_template_big_text.xml` 的原文：

```xml
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">
    <TextView android:id="@+id/title"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />
    <TextView android:id="@+id/body"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:maxLines="3" />
</LinearLayout>
```

实际自定义通知也受目标 SDK 的系统装饰和尺寸限制；不应承诺完全替换通知外观。标准 MessagingStyle 不会自动因几条 Message 就出现回复输入框，仍需配合 RemoteInput action；CallStyle/fullScreenIntent 是否展示全屏还受权限、用途和系统策略影响。

通知的样式数据、生成布局、RemoteViews 应用和最终通知 row 是四个层次。排查模板问题，应先看 Builder/Style extras 是否正确，再看 content flags/生成结果，最后看 apply 与 row slot，不能仅在最外层通知列表盲目强刷。

## 10. 面试常见问题

### 10.1 SystemUI 基础

**Q1: SystemUI 是什么？包含哪些组件？**

**A:**

SystemUI 是 Android 系统的核心 UI 组件，运行在独立的 com.android.systemui 进程中：

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

```text
AOD 实现机制：

1. 硬件支持
   - AMOLED 屏幕（可单独点亮像素）
   - Display HAL 支持 AOD 模式

2. 软件架构
   - DozeService：管理 Doze 状态
   - DozeMachine：状态机控制
   - DozeHost 与锁屏视图/状态管线：AOD 显示内容

3. 典型状态流转（非全部 Android 17 分支）
   UNINITIALIZED → INITIALIZED → DOZE_AOD
   → DOZE_REQUEST_PULSE → DOZE_PULSING → DOZE_PULSE_DONE
   → 按 wakefulness/设置解析回稳态；退出由 FINISH 收尾

4. 显示内容
   - 时钟（防烧屏移动）
   - 通知图标
   - 通知预览

5. 功耗优化
   - 显示低功耗模式（刷新率由设备能力/策略决定，不保证 1fps）
   - 部分像素点亮
   - 定时脉冲更新
```

### 10.3 通知系统

**Q3: 通知的发送和显示流程？**

**A:**

```text
通知流程：

1. 应用层
   NotificationManager.notify()
   ↓
2. Framework 层 (NMS)
   - 创建 NotificationRecord
   - 排名和过滤
   - 更新内存活跃集合；偏好与可选历史另行持久化
   ↓
3. Binder IPC
   - 回调 NotificationListenerService
   ↓
4. SystemUI 层
   - NotificationListener → NotifCollection → 列表构建/绑定管线处理
   - 创建 NotificationEntry
   - 提取 RemoteViews
   - 渲染通知视图
```

**Q4: RemoteViews 的原理？**

**A:**

```text
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
   - ReflectionAction（例如 setText 的参数化操作）
   - ReflectionAction（例如 setImageResource）
   - SetOnClickResponse（交互响应包装）
   - ...
```

**Q5: 通知是如何排名的？**

**A:**

```text
通知排名不能表示成 importance/category 的统一加权得分：
1. RankingHelper 当前先用 NotificationTimeComparator 生成初始 rank。
2. 按 group proxy、criticality、summary 与 sortKey 构造 global sort key。
3. 最终比较器排序；SystemUI 还有分组、section、过滤及视觉稳定性策略。
渠道重要性影响提醒/展示资格，但不能据此推导所有通知的最终总序。

```

**Q6: 通知模板是如何工作的？**

**A:**

```text
通知模板工作原理：

1. 模板本质
   - 预定义的 RemoteViews 布局
   - Style 类负责填充内容

2. 使用流程
   - 创建 Style (BigTextStyle, MessagingStyle 等)
   - 设置内容
   - Builder 保存样式数据；部分视图由 SystemUI recoverBuilder 后按需生成

3. 渲染流程
   - SystemUI 收到 RemoteViews
   - RemoteViews.apply() 加载模板布局
   - 执行 Action 填充内容
```

---

## 11. NotificationManagerService 高级特性

本章沿用第 4–9 章的 Android 17 通知路径，进一步区分服务端记录、排序、分组、提醒策略与历史数据。这里的“通知入库”不能同时指代三个不同对象：活跃通知在内存中，渠道/偏好由策略文件保存，可选通知历史由独立管理器维护。

### 11.1 NMS 核心数据结构与更新事务

`NotificationRecord` 是同目录独立类，不是 NMS 的内部类；`StatusBarNotification` 是 framework 数据载体。实际活跃集合涉及 `mNotificationList`、`mNotificationsByKey`，尚未完成发布的记录在 `mEnqueuedNotifications`。不存在旧文所画的统一 `NotificationStore`、`NotificationList` 类型或 `ConditionalNotificationCenter`。

```text
notify Binder 请求
  -> 校验调用方/权限/渠道与构造 NotificationRecord
  -> EnqueueNotificationRunnable: pending/enqueued、分组及调度
  -> PostNotificationRunnable: 找 old、替换/加入 active、排序、分发
        + mNotificationList: 参与排序的活跃记录
        + mNotificationsByKey: 按唯一 key 查询活跃记录
        + mEnqueuedNotifications: 尚未发布完成的候选
  -> NotificationListeners: 通知 SystemUI 等获准监听者
```

第 4 章已给出两个 Runnable 的实际实现。它们不是“一个只封装参数，一个毫无条件地 append”：更新与新建路径不同，取消可能与排队发布竞争，发布前还要处理无效图标、权限/渠道变更等条件。阅读锁内代码时要同时检查 list 与 map 的更新，避免仅看某个 `add()` 就断言所有通知都已成功上屏。

`RankingHelper`、`PreferencesHelper`、`ZenModeHelper`、`NotificationHistoryManager` 是分工协作对象；气泡窗口的 UI 控制不由一个 NMS 内部 `BubbleController` 完成。服务端资格判断和 SystemUI/Shell 展示是两层。

### 11.2 当前排序算法：两轮排序与 group proxy

不能用 `importance * 100 + category * 10 + timestamp` 冒充源码。该 tag 的初始比较器是 `NotificationTimeComparator`，比较记录的 ranking time；时间已经由记录构建/更新语义处理，不等于随手读取 `System.currentTimeMillis()`。


源码：[NotificationTimeComparator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/notification/NotificationTimeComparator.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public int compare(NotificationRecord left, NotificationRecord right) {
    // earliest first
    return -1 * Long.compare(left.getRankingTimeMs(), right.getRankingTimeMs());
}
```

`RankingHelper.sort()` 首先清除旧 global sort key，进行初始排序并写入 authoritative rank，再为每组选择 proxy，形成结构化字符串，最后由 final comparator 排序：


源码：[RankingHelper.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/notification/RankingHelper.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void sort(ArrayList<NotificationRecord> notificationList) {
    final int N = notificationList.size();
    // clear global sort keys
    for (int i = N - 1; i >= 0; i--) {
        notificationList.get(i).setGlobalSortKey(null);
    }

    // Rank each record individually.
    notificationList.sort(mPreliminaryComparator);

    synchronized (mProxyByGroupTmp) {
        // record individual ranking result and nominate proxies for each group
        for (int i = 0; i < N; i++) {
            final NotificationRecord record = notificationList.get(i);
            record.setAuthoritativeRank(i);
            final String groupKey = record.getGroupKey();
             NotificationRecord existingProxy = mProxyByGroupTmp.get(groupKey);
            // summaries are mostly hidden in systemui - if there is a child notification,
            // use its rank
            if (existingProxy == null || existingProxy.getNotification().isGroupSummary()) {
                mProxyByGroupTmp.put(groupKey, record);
            }
        }
        // assign global sort key:
        //   is_recently_intrusive:group_rank:is_group_summary:group_sort_key:rank
        for (int i = 0; i < N; i++) {
            final NotificationRecord record = notificationList.get(i);
            NotificationRecord groupProxy = mProxyByGroupTmp.get(record.getGroupKey());
            String groupSortKey = record.getNotification().getSortKey();

            // We need to make sure the developer provided group sort key (gsk) is handled
            // correctly:
            //   gsk="" < gsk=non-null-string < gsk=null
            //
            // We enforce this by using different prefixes for these three cases.
            String groupSortKeyPortion;
            if (groupSortKey == null) {
                groupSortKeyPortion = "nsk";
            } else if (groupSortKey.equals("")) {
                groupSortKeyPortion = "esk";
            } else {
                groupSortKeyPortion = "gsk=" + groupSortKey;
            }

            boolean isGroupSummary = record.getNotification().isGroupSummary();
            char intrusiveRank = '2';
            record.setGlobalSortKey(
                    formatSimple("crtcl=0x%04x:intrsv=%c:grnk=0x%04x:gsmry=%c:%s:rnk=0x%04x",
                    record.getCriticality(),
                    intrusiveRank,
                    groupProxy.getAuthoritativeRank(),
                    isGroupSummary ? '0' : '1',
                    groupSortKeyPortion,
                    record.getAuthoritativeRank()));
        }
        mProxyByGroupTmp.clear();
    }

    // Do a second ranking pass, using group proxies
    Collections.sort(notificationList, mFinalComparator);
}
```

阅读这一实现时有五个容易漏掉的细节：

1. `authoritativeRank` 是初排结果，不是开发者传入的固定名次。
2. 组代理可以影响组内成员在全局序列中的位置，不能独立对每个 child 做简单 importance 排序。
3. `groupSortKey` 的空字符串、非空字符串与 null 有专门前缀，字典序语义不同。
4. summary 在 global sort key 中有独立位，不能仅靠通知发出时间决定它排在子项哪里。
5. 服务端顺序不是最终屏幕上所有区域的单一总序。SystemUI 的 collection/list-builder/coordinator 还要处理 section、过滤、提升、分组及视觉稳定性。

渠道重要性、用户设置、DND 与气泡资格仍然重要，但它们不是旧文声称的 `CALL > MESSAGE > OTHER` 固定类别总序。排查排序应记录 key、groupKey、rankingTime、authoritativeRank、globalSortKey 和 SystemUI section，而不是反复调整一个杜撰的权重函数。

### 11.3 通知分组：身份、summary 与子通知

应用的 `setGroup()` 是组标识的一部分，实际 `StatusBarNotification` 的 group key 还区分用户和包等身份；不同应用恰好使用字符串 `messages` 不会因此成为同一组。应用主动分组、服务端自动分组和 SystemUI 视觉分组也不是一个动作。

```java
// 应用示例：省略渠道建立、通知权限及资源定义。
String group = "messages";
Notification child = new Notification.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_message)
        .setContentTitle("Alice")
        .setContentText("新消息")
        .setGroup(group)
        .setSortKey("001")
        .build();
Notification summary = new Notification.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_message)
        .setContentTitle("消息汇总")
        .setGroup(group)
        .setGroupSummary(true)
        .setGroupAlertBehavior(Notification.GROUP_ALERT_CHILDREN)
        .build();
manager.notify(1001, child);
manager.notify(1000, summary);
```

summary 的标题/样式和 child 是各自独立的通知记录。更新某个 child 应复用自己的 tag/id；不能让 summary 与 child 共用同一个 key 而把一次更新误认作“自动吞通知”。移除、展开、组抑制以及 summary 是否单独可见由后续管线判断，不能从发送顺序直接推导 UI 结果。

提醒行为还要结合 group alert behavior。组内所有 child 与 summary 都配置高重要性并不意味着每项必然独立响铃；排查应区分“记录存在”“可见”“发生 alert”三个结果。

### 11.4 通知气泡：元数据不是资格豁免

气泡不是任意 `BubbleMetadata` 都能立即触发的悬浮窗。现代会话气泡还需要满足有效会话/shortcut、通知与渠道、用户气泡设置、目标 Activity 与 PendingIntent 的要求；SystemUI/Shell 可能保留普通通知而拒绝气泡展示。

```java
// 平台 API 示例片段：shortcutId 须对应应用已发布且合规的会话 shortcut。
Notification.BubbleMetadata bubble =
        new Notification.BubbleMetadata.Builder(shortcutId)
                .setDesiredHeight(600)
                .build();
Notification message = new Notification.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_message)
        .setShortcutId(shortcutId)
        .setStyle(messagingStyle)
        .setBubbleMetadata(bubble)
        .build();
manager.notify(conversationId, message);
```

`setDesiredHeight()` 是期望尺寸，不是绕过窗口策略的绝对像素承诺。实际工程需要提供可用的对话内容 Activity、返回栈及普通通知降级体验；本片段省略这些业务定义，不是独立可运行工程。

### 11.5 声音与振动：提醒策略和视觉打断分别建模

当前 NMS 发布路径调用 `NotificationAttentionHelper` 处理提醒；它不能被简化成无条件调用 ringtone/vibrator。权限、渠道、用户设置、DND、分组提醒规则、更新节流和设备状态都会影响最终结果。

**核验边界：**本轮已核对 NMS 中对 helper 的实际调用，但 helper 文件抓取遇到限流，未逐分支复核其内部实现。因此这里不继续保留旧文假装逐行源码的 `shouldMuteNotification()` 实现，也不宣称已验证 Android 17 所有音振组合。

尤其不要把 `isVisuallyInterruptive()` 等同“确实响铃”。它检查新旧记录的可见内容变化，并对 summary、前台服务/UIJ 等更新做不同处理；下面是实际实现，用于解释历史记录触发与视觉变化的联系：


源码：[NotificationManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/notification/NotificationManagerService.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
protected boolean isVisuallyInterruptive(@Nullable NotificationRecord old,
        @NonNull NotificationRecord r) {
    // Ignore summary updates because we don't display most of the information.
    if (r.getSbn().isGroup() && r.getSbn().getNotification().isGroupSummary()) {
        if (DEBUG_INTERRUPTIVENESS) {
            Slog.v(TAG, "INTERRUPTIVENESS: "
                    +  r.getKey() + " is not interruptive: summary");
        }
        return false;
    }

    if (old == null) {
        if (DEBUG_INTERRUPTIVENESS) {
            Slog.v(TAG, "INTERRUPTIVENESS: "
                    +  r.getKey() + " is interruptive: new notification");
        }
        return true;
    }

    Notification oldN = old.getSbn().getNotification();
    Notification newN = r.getSbn().getNotification();
    if (oldN.extras == null || newN.extras == null) {
        if (DEBUG_INTERRUPTIVENESS) {
            Slog.v(TAG, "INTERRUPTIVENESS: "
                    +  r.getKey() + " is not interruptive: no extras");
        }
        return false;
    }

    // Ignore visual interruptions from FGS/UIJs because users
    // consider them one 'session'. Count them for everything else.
    if (r.getSbn().getNotification().isFgsOrUij()) {
        if (DEBUG_INTERRUPTIVENESS) {
            Slog.v(TAG, "INTERRUPTIVENESS: "
                    + r.getKey() + " is not interruptive: FGS/UIJ");
        }
        return false;
    }

    final String oldTitle = String.valueOf(oldN.extras.get(EXTRA_TITLE));
    final String newTitle = String.valueOf(newN.extras.get(EXTRA_TITLE));
    if (!Objects.equals(oldTitle, newTitle)) {
        if (DEBUG_INTERRUPTIVENESS) {
            Slog.v(TAG, "INTERRUPTIVENESS: "
                    +  r.getKey() + " is interruptive: changed title");
            Slog.v(TAG, "INTERRUPTIVENESS: " + String.format("   old title: %s (%s@0x%08x)",
                    oldTitle, oldTitle.getClass(), oldTitle.hashCode()));
            Slog.v(TAG, "INTERRUPTIVENESS: " + String.format("   new title: %s (%s@0x%08x)",
                    newTitle, newTitle.getClass(), newTitle.hashCode()));
        }
        return true;
    }

    // Do not compare Spannables (will always return false); compare unstyled Strings
    final String oldText = String.valueOf(oldN.extras.get(EXTRA_TEXT));
    final String newText = String.valueOf(newN.extras.get(EXTRA_TEXT));
    if (!Objects.equals(oldText, newText)) {
        if (DEBUG_INTERRUPTIVENESS) {
            Slog.v(TAG, "INTERRUPTIVENESS: "
                    + r.getKey() + " is interruptive: changed text");
            Slog.v(TAG, "INTERRUPTIVENESS: " + String.format("   old text: %s (%s@0x%08x)",
                    oldText, oldText.getClass(), oldText.hashCode()));
            Slog.v(TAG, "INTERRUPTIVENESS: " + String.format("   new text: %s (%s@0x%08x)",
                    newText, newText.getClass(), newText.hashCode()));
        }
        return true;
    }

    if (oldN.getProgressState() != newN.getProgressState()) {
        if (DEBUG_INTERRUPTIVENESS) {
            Slog.v(TAG, "INTERRUPTIVENESS: "
                    + r.getKey() + " is interruptive: significantly changed progress");
        }
        return true;
    }

    if (Notification.areIconsDifferent(oldN, newN)) {
        if (DEBUG_INTERRUPTIVENESS) {
            Slog.v(TAG, "INTERRUPTIVENESS: "
                    +  r.getKey() + " is interruptive: icons differ");
        }
        return true;
    }

    // Fields below are invisible to bubbles.
    if (r.canBubble()) {
        if (DEBUG_INTERRUPTIVENESS) {
            Slog.v(TAG, "INTERRUPTIVENESS: "
                    +  r.getKey() + " is not interruptive: bubble");
        }
        return false;
    }

    // Actions
    if (Notification.areActionsVisiblyDifferent(oldN, newN)) {
        if (DEBUG_INTERRUPTIVENESS) {
            Slog.v(TAG, "INTERRUPTIVENESS: "
                    +  r.getKey() + " is interruptive: changed actions");
        }
        return true;
    }

    try {
        Notification.Builder oldB = Notification.Builder.recoverBuilder(getContext(), oldN);
        Notification.Builder newB = Notification.Builder.recoverBuilder(getContext(), newN);

        // Style based comparisons
        if (Notification.areStyledNotificationsVisiblyDifferent(oldB, newB)) {
            if (DEBUG_INTERRUPTIVENESS) {
                Slog.v(TAG, "INTERRUPTIVENESS: "
                        +  r.getKey() + " is interruptive: styles differ");
            }
            return true;
        }

        // Remote views
        if (Notification.areRemoteViewsChanged(oldB, newB)) {
            if (DEBUG_INTERRUPTIVENESS) {
                Slog.v(TAG, "INTERRUPTIVENESS: "
                        +  r.getKey() + " is interruptive: remoteviews differ");
            }
            return true;
        }
    } catch (Exception e) {
        Slog.w(TAG, "error recovering builder", e);
    }
    return false;
}
```

因此“静音通知一定不记历史”和“响铃一次就必然插入一条历史”都不是从该方法能推出的结论。应继续检查 `NotificationRecord` 的 interruption 状态与历史开关。

### 11.6 偏好持久化与活跃通知不是一个数据库

固定 tag 的 NMS 使用 `/data/system/notification_policy.xml`：`systemDir` 来自 `new File(Environment.getDataDirectory(), "system")`，再交给 `AtomicFile`。旧文写成 `/data/system_ce/<user>/notification_policy.xml` 是错误路径。这里保存策略、偏好等信息，不是把每条活跃 Notification 完整序列化后在重启时自动重放。

`PreferencesHelper` 的 XML 读写负责应用/渠道/分组偏好。用户设置变更经过服务接口与权限检查，修改内存状态并按服务调度保存；不要将 XML 子段当成整个策略文件的唯一根节点。

```text
活跃通知: NMS 内存 list/map -> listener 分发 -> SystemUI UI
偏好策略: PreferencesHelper 等 -> NMS AtomicFile 策略文件
可选历史: NotificationHistoryManager -> 每用户数据库/缓冲/批量文件
```

这三条路径的寿命不同。进程重启后的重新投递、包重装后的渠道状态、用户锁定时历史目录不可用，必须分别分析。`dumpsys notification` 看到一条通知，并不证明它已经写入历史文件。

### 11.7 通知历史：条件记录、缓冲、保留与关闭清理

历史记录不是每次 notify 都写一个文件，也不是点击“清除通知”才开始保存。NMS 的 `maybeRecordInterruptionLocked()` 根据记录状态构造历史条目并交给历史管理器：


源码：[NotificationManagerService.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/notification/NotificationManagerService.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
protected void maybeRecordInterruptionLocked(NotificationRecord r) {
    if (r.isInterruptive() && !r.hasRecordedInterruption()) {
        String channelId = r.getNotification().getChannelId();
        mAppUsageStats.reportInterruptiveNotification(r.getSbn().getPackageName(),
                channelId,
                getRealUserId(r.getSbn().getUserId()));
        Trace.traceBegin(Trace.TRACE_TAG_SYSTEM_SERVER, "notifHistoryAddItem");
        try {
            if (r.getNotification().getSmallIcon() != null) {
                final HistoricalNotification.Builder builder
                        = new HistoricalNotification.Builder()
                        .setPackage(r.getSbn().getPackageName())
                        .setUid(r.getSbn().getUid())
                        .setUserId(r.getSbn().getNormalizedUserId())
                        .setChannelId(channelId)
                        .setPostedTimeMs(System.currentTimeMillis())
                        .setTitle(r.getNotification().getHistoryTitle(getContext()))
                        .setText(r.getNotification().getHistoryText(getContext()))
                        .setIcon(r.getNotification().getSmallIcon());
                mHistoryManager.addNotification(builder.build());
            }
        } finally {
            Trace.traceEnd(Trace.TRACE_TAG_SYSTEM_SERVER);
        }
        r.setRecordedInterruption(true);
    }
}
```

历史数据库有内存 buffer；该 tag 的 `WRITE_BUFFER_INTERVAL_MS` 为 20 分钟、`HISTORY_RETENTION_DAYS` 为 1。它按批次写文件并安排裁剪，这不同于“每通知一文件”，也不构成设备在任意时刻恰好仅有最后 24 小时数据的实时承诺。

序列化使用 NotificationHistoryProto，其中顶层包含 string pool、major version 和 repeated notification；每条记录有 package/channel 的文本或索引、uid/userId、posted time、title/text/icon、conversation id 等字段。这里不沿用旧文杜撰的字段编号与 protobuf schema。

关闭历史会调用清理，不是“仅停止写入但永不删除旧数据”。用户尚未解锁时需要延后访问对应目录：


源码：[NotificationHistoryManager.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/notification/NotificationHistoryManager.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
void onHistoryEnabledChanged(@UserIdInt int userId, boolean historyEnabled) {
    synchronized (mLock) {
        if (historyEnabled) {
            mHistoryEnabled.put(userId, historyEnabled);
        }
        final NotificationHistoryDatabase userHistory =
                getUserHistoryAndInitializeIfNeededLocked(userId);
        if (userHistory != null) {
            if (!historyEnabled) {
                disableHistory(userHistory, userId);
            }
        } else {
            mUserPendingHistoryDisables.put(userId, !historyEnabled);
        }
    }
}

private void disableHistory(NotificationHistoryDatabase userHistory, @UserIdInt int userId) {
    userHistory.disableHistory();

    mUserPendingHistoryDisables.put(userId, false);
    mHistoryEnabled.put(userId, false);
    mUserState.put(userId, null);
}
```


源码：[NotificationHistoryDatabase.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/notification/NotificationHistoryDatabase.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void disableHistory() {
    synchronized (mLock) {
        for (AtomicFile file : mHistoryFiles) {
            file.delete();
        }
        mHistoryDir.delete();
        mHistoryFiles.clear();
    }
}
```

读取由 NMS 的受权限保护接口进入历史管理器，不是旧文声称 Settings 通过一个通用 ContentProvider 任意查表。历史可能包含敏感标题和正文，调试导出也应遵循最小化原则。

排查“历史没有该条”应先核实用户与开关，再检查 interruption 条件、写入缓冲和用户解锁状态，最后检查读取权限与裁剪；不能只检查通知是否出现过图标。

## 12. AOD 高级特性

第 3 章介绍部件分工，本章补充中间态消解、屏幕电源状态、传感器订阅、设置以及异步调试。这里的 Doze 是 SystemUI 的息屏显示控制，不能直接当成 DeviceIdleController 的应用待机状态机。

### 12.1 AOD 与 WakefulnessLifecycle：中间态必须回到策略判断

`INITIALIZED` 和 `DOZE_PULSE_DONE` 并不是停留任意长时间的稳定显示模式。`resolveIntermediateState()` 会结合 wakefulness、dock、Always On 与 MINMODE 开关选择后续状态，不能把所有设备写死成 pulse done 后直接返回 DOZE_AOD：


源码：[DozeMachine.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/doze/DozeMachine.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
private void resolveIntermediateState(State state) {
    switch (state) {
        case INITIALIZED:
        case DOZE_PULSE_DONE:
            final State nextState;
            @Wakefulness int wakefulness = mWakefulnessLifecycle.getWakefulness();
            if (state == State.INITIALIZED &&
                    mMinModeManager.isPresent() &&
                    MinModeManagerUtilsKt.isMinModeAvailable(mMinModeManager.get())) {
                nextState = State.DOZE_AOD_MINMODE;
            } else if (state != State.INITIALIZED && (wakefulness == WAKEFULNESS_AWAKE
                    || wakefulness == WAKEFULNESS_WAKING)) {
                nextState = State.FINISH;
            } else if (mDockManager.isDocked()) {
                nextState = mDockManager.isHidden() ? State.DOZE : State.DOZE_AOD_DOCKED;
            } else if (mAmbientDisplayConfig.alwaysOnEnabled(mUserTracker.getUserId())) {
                nextState = State.DOZE_AOD;
            } else {
                nextState = State.DOZE;
            }

            transitionTo(nextState, DozeLog.PULSE_REASON_NONE);
            break;
        default:
            break;
    }
}
```

这里的几个层次必须区分：wakefulness 描述系统睡醒过程；DozeMachine.State 描述 SystemUI doze 控制；Display.STATE_* 描述显示电源状态。名字相似不代表枚举一一对应。

当请求在已有转换处理中到达时，DozeMachine 通过请求队列和 wake lock 保持处理顺序；不要在部件 callback 中递归实现自己的“直接跳状态”。第 3 章的 `requestState()` / `transitionTo()` 已说明请求、校验、派发和收尾的关系。

### 12.2 显示状态管理：pending、延迟和取消

屏幕切换既要协调面板低功耗模式，又要避免动画、触摸或 UDFPS 工作还未结束就过早挂起。`DozeScreenState` 的 `mPendingScreenState` 以及 Handler callback 是实际状态的一部分，不应只画一条 `setDozeScreenState()` 直线。


源码：[DozeScreenState.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/doze/DozeScreenState.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void transitionTo(DozeMachine.State oldState, DozeMachine.State newState) {
    int screenState = newState.screenState(mParameters);
    mDozeHost.cancelGentleSleep();

    if (newState == DozeMachine.State.FINISH) {
        // Make sure not to apply the screen state after DozeService was destroyed.
        mPendingScreenState = Display.STATE_UNKNOWN;
        mHandler.removeCallbacks(mApplyPendingScreenState);

        applyScreenState(screenState);
        mWakeLock.setAcquired(false);
        return;
    }

    if (screenState == Display.STATE_UNKNOWN) {
        // We'll keep it in the existing state
        return;
    }

    final boolean messagePending = mHandler.hasCallbacks(mApplyPendingScreenState);
    final boolean pulseEnding = oldState == DOZE_PULSE_DONE && newState.isAlwaysOn();
    final boolean turningOn = (oldState == DOZE_AOD_PAUSED || oldState == DOZE)
            && newState.isAlwaysOn();
    final boolean turningOff = (oldState.isAlwaysOn() && newState == DOZE)
            || (oldState == DOZE_AOD_PAUSING && newState == DOZE_AOD_PAUSED);
    final boolean justInitialized = oldState == DozeMachine.State.INITIALIZED;
    if (messagePending || justInitialized || pulseEnding || turningOn) {
        // During initialization, we hide the navigation bar. That is however only applied after
        // a traversal; setting the screen state here is immediate however, so it can happen
        // that the screen turns on again before the navigation bar is hidden. To work around
        // that, wait for a traversal to happen before applying the initial screen state.
        mPendingScreenState = screenState;

        // Delay screen state transitions even longer while animations are running.
        boolean shouldDelayTransitionEnteringDoze = newState == DOZE_AOD
                && mParameters.shouldDelayDisplayDozeTransition() && !turningOn;

        // Delay screen state transition longer if UDFPS is actively authenticating a fp
        boolean shouldDelayTransitionForUDFPS = newState == DOZE_AOD
                && mUdfpsController != null && mUdfpsController.isFingerDown();

        if (!messagePending) {
            if (DEBUG) {
                Log.d(TAG, "Display state changed to " + screenState + " delayed by "
                        + (shouldDelayTransitionEnteringDoze ? ENTER_DOZE_DELAY : 1));
            }

            if (shouldDelayTransitionEnteringDoze) {
                if (justInitialized) {
                    // If we are delaying transitioning to doze and the display was not
                    // turned on we set it to 'on' first to make sure that the animation
                    // is visible before eventually moving it to doze state.
                    // The display might be off at this point for example on foldable devices
                    // when we switch displays and go to doze at the same time.
                    applyScreenState(Display.STATE_ON);

                    // Restore pending screen state as it gets cleared by 'applyScreenState'
                    mPendingScreenState = screenState;
                }

                mHandler.postDelayed(mApplyPendingScreenState, ENTER_DOZE_DELAY);
            } else if (shouldDelayTransitionForUDFPS) {
                mDozeLog.traceDisplayStateDelayedByUdfps(mPendingScreenState);
                mHandler.postDelayed(mApplyPendingScreenState, UDFPS_DISPLAY_STATE_DELAY);
            } else {
                mHandler.post(mApplyPendingScreenState);
            }
        } else if (DEBUG) {
            Log.d(TAG, "Pending display state change to " + screenState);
        }

        if (shouldDelayTransitionEnteringDoze || shouldDelayTransitionForUDFPS) {
            mWakeLock.setAcquired(true);
        }
    } else if (turningOff) {
        if (SceneContainerFlag.isEnabled()) {
            applyScreenState(screenState);
        } else {
            mDozeHost.prepareForGentleSleep(() -> applyScreenState(screenState));
        }
    } else {
        applyScreenState(screenState);
    }
}
```

该实现中的延迟不是统一的“唤醒耗时”：`ENTER_DOZE_DELAY`、`ENTER_DOZE_HIDE_WALLPAPER_DELAY`、`UDFPS_DISPLAY_STATE_DELAY` 分别服务不同条件，该 tag 对应 4000/2500/1200ms。条件不满足时不会因为常量存在而强制等待。

屏幕状态的最终应用还会移除/更新待处理任务并释放对应 wake lock。FINISH、重复请求和新请求覆盖旧 pending state 都是调试重点：只看某次请求 log，不能证明它最后已经成为面板状态。

### 12.3 传感器：监听资格与注册行为分离

DozeSensors 的设置、当前监听状态、触屏传感器是否允许以及功耗状态共同决定注册。它不是在构造函数中无条件同时打开所有传感器，更不是退出时只将一个 Boolean 清零就已撤销硬件订阅。


源码：[DozeSensors.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/doze/DozeSensors.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void setListening(boolean listen, boolean includeTouchScreenSensors,
        boolean includeAodOnlySensors) {
    if (mListening == listen && mListeningTouchScreenSensors == includeTouchScreenSensors
            && mListeningAodOnlySensors == includeAodOnlySensors) {
        return;
    }
    mListening = listen;
    mListeningTouchScreenSensors = includeTouchScreenSensors;
    mListeningAodOnlySensors = includeAodOnlySensors;
    updateListening();
}

public void setListeningWithPowerState(boolean listen, boolean includeTouchScreenSensors,
        boolean includeAodRequiringSensors, boolean lowPowerStateOrOff) {
    final boolean shouldRegisterProxSensors =
            !mSelectivelyRegisterProxSensors || lowPowerStateOrOff;
    if (mListening == listen
            && mListeningTouchScreenSensors == includeTouchScreenSensors
            && mListeningProxSensors == shouldRegisterProxSensors
            && mListeningAodOnlySensors == includeAodRequiringSensors
    ) {
        return;
    }
    mListening = listen;
    mListeningTouchScreenSensors = includeTouchScreenSensors;
    mListeningProxSensors = shouldRegisterProxSensors;
    mListeningAodOnlySensors = includeAodRequiringSensors;
    updateListening();
}

private void updateListening() {
    boolean anyListening = false;
    for (TriggerSensor s : mTriggerSensors) {
        boolean listen = mListening
                && (!s.mRequiresTouchscreen || mListeningTouchScreenSensors)
                && (!s.mRequiresProx || mListeningProxSensors)
                && (!s.mRequiresAod || mListeningAodOnlySensors);

        //AOD might be turned off in visual because of BetterySaver or isAlwaysOnSuppressed(),
        //but AOD isn't really turned off, in these cases, udfpsLongPressSensor should be
        //unregistered.
        if (!mListeningAodOnlySensors && KEY_DOZE_PULSE_ON_AUTH.equals(s.mSetting)) {
            if (mConfig.alwaysOnEnabled(mSelectedUserInteractor.getSelectedUserId())
                    && !mConfig.screenOffUdfpsEnabled(
                    mSelectedUserInteractor.getSelectedUserId())) {
                listen = false;
            }
        }

        s.setListening(listen);
        if (listen) {
            anyListening = true;
        }
    }

    if (!anyListening) {
        mSecureSettings.unregisterContentObserverAsync(mSettingsObserver);
    } else if (!mSettingRegistered) {
        for (TriggerSensor s : mTriggerSensors) {
            s.registerSettingsObserver(mSettingsObserver);
        }
    }
    mSettingRegistered = anyListening;
}
```

TriggerSensor 与 PluginSensor 的注册/回调方式不同；后者还依赖已连接的 SensorManagerPlugin。一次性 trigger 的重新武装和持续监听 sensor 的注销也不同。第 3 章的 trigger 处理说明了如何切回 Handler 并结合 proximity/状态门控请求 pulse。

实际故障至少分三类：资源 overlay 没有提供目标传感器，监听资格计算得到 false，以及回调已经到达但 pulse 被当前状态或距离条件拒绝。三个阶段分别记录日志，才能避免把“屏幕没有亮”一概归为传感器驱动故障。

### 12.4 AmbientDisplayConfiguration：available 不等于 enabled

`available` 往往取决于硬件/资源和调试配置，`enabled(user)` 还要结合对应用户的 Secure 设置与策略。Always On、通知 pulse、tap/double tap、pickup 并非同一个总开关：


源码：[AmbientDisplayConfiguration.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/hardware/display/AmbientDisplayConfiguration.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public boolean pulseOnNotificationEnabled(int user) {
    return boolSetting(Settings.Secure.DOZE_ENABLED, user,
            mDozeEnabledByDefault ? 1 : 0)
            && pulseOnNotificationAvailable();
}

public boolean pulseOnNotificationAvailable() {
    return mContext.getResources().getBoolean(R.bool.config_pulseOnNotificationsAvailable)
            && ambientDisplayAvailable();
}

public boolean alwaysOnEnabled(int user) {
    return boolSetting(Settings.Secure.DOZE_ALWAYS_ON, user, mAlwaysOnByDefault ? 1 : 0)
            && alwaysOnAvailable() && !accessibilityInversionEnabled(user);
}

public boolean alwaysOnAvailable() {
    return (alwaysOnDisplayDebuggingEnabled() || alwaysOnDisplayAvailable())
            && ambientDisplayAvailable();
}

public boolean ambientDisplayAvailable() {
    return !TextUtils.isEmpty(ambientDisplayComponent());
}
```

这些方法说明为什么不能只写 `settings get secure doze_always_on` 就宣布硬件已支持 AOD。检查时要确定当前用户、overlay、资源对应的 sensor/display 能力和实际运行开关；本轮没有设备运行结果，不给出某机型默认值保证。

### 12.5 贯穿通知到 AOD 的可观测链路

```text
App notify
  -> NMS enqueue/post: key、channel、old/new、ranking/interruption
  -> NotificationListener: listener 可见性与 ranking
  -> NotifCollection: add/update/remove 生命周期
  -> 列表构建 / 内容绑定 / 锁屏隐私与过滤
  -> DozeHost / DozeTriggers: 当前状态、pulse reason、proximity
  -> DozeMachine: request queue、transition、Part callbacks
  -> DozeScreenState: pending display state、延迟任务、wake lock
  -> Dream/Display 服务与硬件显示状态
```

这是跨组件诊断图，不代表 NotifCollection 的每次 add 都直接调用一次 pulse。通知发布、heads-up、AOD pulse、实际屏幕点亮有各自资格判断；相同 key 的多次更新也可能复用视图或被抑制。

建议用 key 与时间戳关联服务端和 SystemUI 日志，并同时记录用户、group、渠道以及 doze 状态。若只对比 App notify 的时间与屏幕截图，会漏掉 Binder 排队、后台绑定与 pending display state 的取消。

### 12.6 RemoteViews 异步绑定的代际与资源寿命

RemoteViews 传递的是布局标识与序列化 actions，不是发送方的 View 对象、ClassLoader 或任意 Java 闭包。第 5–9 章已经分别展示 class filter、允许调用的方法、Builder 恢复及 NotificationRowContentBinderImpl 的实际路径，本节不再构造一个不存在的自定义 wire format。

同一个 notification key 可能在旧 inflation 尚未结束时更新。绑定流程必须处理取消/过期结果，避免将旧标题覆盖新内容；异步 inflate 完成也不等于 row 已经进入可见窗口。排查应区分 collection entry、content flags、inflate task、cached RemoteViews 和 row 的各个 content slot。

`reapply` 只适用于兼容已有视图结构的更新。包或布局身份改变、重应用被禁止、缓存缺失或异常，都可能导致重新 apply。复用可以减少 inflate 成本，却不能免除 action 执行、图片处理和布局开销。

回收/移除通知时要取消对应工作并释放 UI 引用。持有插件 Context 或旧通知 row 的长期单例缓存，可能在包更新后继续保留旧资源/ClassLoader；这属于资源寿命问题，不是单纯在列表上调用一次 notifyDataSetChanged 能修复的。

### 12.7 Pulse 和防烧屏：状态与动画边界

Android 17 的真实枚举以第 3 章 State 定义为准，没有旧文的 `DOZE_INIT`、`DOZE_REST`、`EXITED_DOZE`。Pulse 通过请求、中间态、host callback 及完成后的状态解析闭环运行；用户唤醒、finish 或其它请求到达时，不能继续播放预先硬编码的固定状态序列。

防烧屏包括时钟/内容的有限位移及显示侧策略，但本文不把固定 ±10px 或固定 1fps 作为所有设备的源码常量。需要结合该产品的尺寸资源、显示模式和实际实现确认。降低刷新率也不意味着 SystemUI 可以在主线程阻塞：唤醒和认证 UI 仍依赖及时响应。

### 12.8 为什么不能用一句“通知列表不适合 RecyclerView”解释架构

通知交互包括组展开、heads-up、swipe、锁屏/解锁过渡、隐私内容切换和持续的行状态。列表实现需要协调这些状态，但 RecyclerView 并非原则上不支持重叠动画，通知数也不是跨配置永远固定在 50 以下。

选择当前容器/渲染管线，是具体实现与迁移阶段的结果，不能用未经基准测试的“必然更快”证明。性能分析应拆分 collection/list build、RemoteViews inflate/reapply、measure/layout、draw、RenderThread 与合成，记录可重复 workload 后再比较。

本轮只做文档与关键源码路径静态审阅，没有做 Perfetto、功耗或帧率实验。因此保留分层分析方法，删除旧文伪造的绝对性能结论。

## 13. Keyguard 锁屏系统

Keyguard 分布在 SystemUI UI/认证控制和 system_server 的窗口策略、凭据/生物识别服务两侧。不能把一个应用 BiometricPrompt demo 当成系统锁屏解锁实现；也不能把 UI 隐藏等同安全凭据已通过。

### 13.1 Keyguard 概述

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Keyguard 锁屏系统概述 (Android 17)                     │
└─────────────────────────────────────────────────────────────────────────────┘

Keyguard 是 Android 系统的锁屏实现，负责：
1. 设备安全保护（防止未授权访问）
2. 安全验证（图案/密码/PIN/生物识别）
3. 锁屏界面显示（时间、通知、快捷设置）
4. 与 SystemUI 的状态同步

┌─────────────────────────────────────────────────────────────────────────────┐
│                 Android 17 Keyguard 分层架构                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          View Layer (视图层)                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KeyguardSecurityContainer                        │   │
│  │  ├── KeyguardPatternView    (图案解锁)                              │   │
│  │  ├── KeyguardPasswordView    (密码解锁)                              │   │
│  │  ├── KeyguardPINView         (PIN 解锁)                              │   │
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
│  │  - KeyguardPatternViewController                                    │   │
│  │  - KeyguardPasswordViewController                                   │   │
│  │  - KeyguardPINViewController                                                │   │
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
│                      Domain Layer (业务逻辑层) [架构分工示意，不表示版本引入时间]            │
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
│                      Logging Layer (日志层) [架构分工示意，不表示版本引入时间]               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    logging/                                          │   │
│  │  - KeyguardLogger (核心日志)                                        │   │
│  │  - BiometricUnlockLogger (生物识别日志)                             │   │
│  │  - KeyguardTransitionAnimationLogger (转场动画日志)                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```


### 13.2 源码目录与实现边界

```text
packages/SystemUI/src/com/android/
  keyguard/
    KeyguardUpdateMonitor.java
    KeyguardPatternViewController.java
    KeyguardSecurityContainerController.java
  systemui/keyguard/
    KeyguardService.java
    KeyguardViewMediator.java
    shared/model/KeyguardState.kt
services/core/java/com/android/server/policy/
  PhoneWindowManager.java
  keyguard/KeyguardServiceDelegate.java
core/java/com/android/internal/widget/
  LockPatternChecker.java
```

此处列出已取得固定 tag 源码的核心入口，不再画不存在的 `com/android/keyguard/security/` 通用子目录。UI 视图控制、monitor、mediator 与 scene/transition 模型并不是同一个层次；产品开关决定部分新旧 UI 路径，不能把某个类存在解释成所有产品必经。

### 13.3 启动链：system_server 绑定与 SystemUI startable 协作

```text
SystemUI Application 的 DI/startables 启动
  -> KeyguardViewMediator.start() -> setupLocked()

system_server PhoneWindowManager.bindKeyguard()
  -> KeyguardServiceDelegate.bindService()
  -> bindServiceAsUser -> SystemUI KeyguardService Binder
  -> onSystemReady 等事件 -> mediator Handler
  -> handleSystemReady() -> doKeyguardLocked()/注册状态监听
```

两条路径需要协作，不是 SystemServer 直接 new Mediator 并调用其私有初始化方法。`KeyguardServiceDelegate` 缓存尚未连通时的系统状态，连接建立后回放；Binder 已绑定、system ready、keyguard 已显示以及首帧完成分别有不同时间点。


源码：[KeyguardServiceDelegate.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/policy/keyguard/KeyguardServiceDelegate.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void bindService(@NonNull Context context, @NonNull Handler handler) {
    Intent intent = new Intent();
    final Resources resources = context.getApplicationContext().getResources();

    final ComponentName keyguardComponent = ComponentName.unflattenFromString(
            resources.getString(com.android.internal.R.string.config_keyguardComponent));
    intent.addFlags(Intent.FLAG_DEBUG_TRIAGED_MISSING);
    intent.setComponent(keyguardComponent);

    if (!context.bindServiceAsUser(intent, mKeyguardConnection, Context.BIND_AUTO_CREATE,
            handler, UserHandle.SYSTEM)) {
        Log.v(TAG, "*** Keyguard: can't bind to " + keyguardComponent);
        mKeyguardReportedState.disable();
    } else {
        if (DEBUG) Log.v(TAG, "*** Keyguard started");
    }

    final DreamManagerInternal dreamManager =
            LocalServices.getService(DreamManagerInternal.class);
    if (dreamManager != null) {
        dreamManager.registerDreamManagerStateListener(mDreamManagerStateListener);
    }
}

public void onSystemReady() {
    if (mKeyguardService != null) {
        try {
            mKeyguardService.onSystemReady();
        } catch (RemoteException e) {
            Slog.w(TAG, "Remote Exception", e);
        }
    } else {
        mKeyguardState.systemReady = true;
    }
}
```


源码：[KeyguardViewMediator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/keyguard/KeyguardViewMediator.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void start() {
    synchronized (this) {
        setupLocked();
    }
}

private void handleSystemReady() {
    synchronized (this) {
        if (DEBUG) Log.d(TAG, "onSystemReady");
        mSystemReady = true;
        doKeyguardLocked(null);
        mUpdateMonitor.registerCallback(mUpdateCallback);
        adjustStatusBarLocked();
        mDreamOverlayStateController.addCallback(mDreamOverlayStateCallback);

        mHandler.obtainMessage(BOOT_INTERACTOR).sendToTarget();

        final DreamViewModel dreamViewModel = mDreamViewModel.get();
        final CommunalTransitionViewModel communalViewModel =
                mCommunalTransitionViewModel.get();

        mJavaAdapter.alwaysCollectFlow(dreamViewModel.getDreamAlpha(),
                getRemoteSurfaceAlphaApplier());
        mJavaAdapter.alwaysCollectFlow(dreamViewModel.getTransitionEnded(),
                getFinishedCallbackConsumerForDream());
        mJavaAdapter.alwaysCollectFlow(dreamViewModel.getTransitioningFromOrToDream(),
                (relevantToDream) -> mIsKeyguardStateRelevantToDream = relevantToDream);
        mJavaAdapter.alwaysCollectFlow(communalViewModel.getShowCommunalFromOccluded(),
                (showCommunalFromOccluded) -> {
                    mShowCommunalWhenUnoccluding = showCommunalFromOccluded;
                });
        mJavaAdapter.alwaysCollectFlow(communalViewModel.getTransitionFromOccludedEnded(),
                getFinishedCallbackConsumer());

        // System ready can be invoked in the middle of user switching, so check for this state
        // and issue the call manually as that important event was missed.
        if (mUserTracker.isUserSwitching()) {
            mUserChangedCallback.onUserChanging(mUserTracker.getUserId(), mContext, () -> {});
        }
    }
    // Most services aren't available until the system reaches the ready state, so we
    // send it here when the device first boots.
    maybeSendUserPresentBroadcast();
}
```

`KeyguardViewMediator` 实现 CoreStartable，不是旧教程中的 `extends SystemUI`。启动方法中的监听注册与安全显示策略不能删成一句“显示锁屏”：当前用户切换、provisioning、外部禁用请求和设备状态都可能改变后续流程。

### 13.4 Mediator 的显示、隐藏与完成处理

Mediator 用 Handler 串行化重要事件，并与 view controller、窗口状态、解锁转场及用户状态协调。以下是该 tag 的实际关键处理方法；字段和分支保留，避免用一个 `mShowing = false` 伪装解锁：


源码：[KeyguardViewMediator.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/keyguard/KeyguardViewMediator.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
private void handleShow(Bundle options) {
    Trace.beginSection("KeyguardViewMediator#handleShow");
    try {
        handleShowInner(options);
    } finally {
        Trace.endSection();
    }
}

private void handleShowInner(Bundle options) {
    final boolean showUnlocked = options != null
            && options.getBoolean(OPTION_SHOW_DISMISSIBLE, false);
    final int currentUser = mSelectedUserInteractor.getSelectedUserId();
    if (showUnlocked) {
        // tell KeyguardUpdateMonitor to keep the device unlocked until the next lock signal
        mUpdateMonitor.tryForceIsDismissibleKeyguard();
    } else if (mLockPatternUtils.isSecure(currentUser)) {
        mLockPatternUtils.getDevicePolicyManager().reportKeyguardSecured(currentUser);
    }
    synchronized (KeyguardViewMediator.this) {
        if (!mSystemReady) {
            if (DEBUG) Log.d(TAG, "ignoring handleShow because system is not ready.");
            notifyLockNowCallback();
            return;
        }
        if (DEBUG) Log.d(TAG, "handleShow");

        mKeyguardExitTransition = null;
        mWakeAndUnlocking = false;
        setUnlockAndWakeFromDream(false, WakeAndUnlockUpdateReason.SHOW);
        setPendingLock(false);

        final boolean forceCallback;
        if (ENABLE_NEW_KEYGUARD_SHELL_TRANSITIONS) {
            // Always update to the future showing state before the transaction.
            forceCallback = true;
        } else {
            final boolean hidingOrGoingAway =
                    mHiding || mKeyguardStateController.isKeyguardGoingAway();
            if (hidingOrGoingAway) {
                Log.d(TAG, "Forcing setShowingLocked because one of these is true:"
                        + "mHiding=" + mHiding
                        + ", keyguardGoingAway="
                        + mKeyguardStateController.isKeyguardGoingAway()
                        + ", which means we're showing in the middle of hiding.");
            }
            forceCallback = hidingOrGoingAway;
        }

        // Force if we're showing in the middle of unlocking, to ensure we end up in the
        // correct state.
        setShowingLocked(true, forceCallback /* force */, "handleShowInner");
        mHiding = false;

        // Any valid exit animation will set this to false before proceeding
        mIsKeyguardExitAnimationCanceled = true;
        // Make sure to remove any pending exit animation requests that would override a SHOW
        mHandler.removeMessages(START_KEYGUARD_EXIT_ANIM);
        mHandler.removeMessages(HIDE);
        mKeyguardInteractor.showKeyguard();
        mShadeController.get().instantCollapseShade();
        mKeyguardStateController.notifyKeyguardGoingAway(false);

        if (!KeyguardWmStateRefactor.isEnabled()) {
            // Handled directly in StatusBarKeyguardViewManager if enabled.
            mKeyguardViewControllerLazy.get().show(options);
        }

        resetKeyguardDonePendingLocked();
        mHideAnimationRun = false;
        adjustStatusBarLocked();
        userActivity();
        mUpdateMonitor.setKeyguardGoingAway(false);
        mKeyguardViewControllerLazy.get().setKeyguardGoingAwayState(false);
        mShowKeyguardWakeLock.release();
    }
    mKeyguardDisplayManager.show();

    scheduleNonStrongBiometricIdleTimeout();
}

private void handleKeyguardDone() {
    Trace.beginSection("KeyguardViewMediator#handleKeyguardDone");
    final int currentUser = mSelectedUserInteractor.getSelectedUserId();
    mUiBgExecutor.execute(() -> {
        if (mLockPatternUtils.isSecure(currentUser)) {
            mLockPatternUtils.getDevicePolicyManager().reportKeyguardDismissed(currentUser);
        }
    });
    if (DEBUG) Log.d(TAG, "handleKeyguardDone");
    synchronized (this) {
        resetKeyguardDonePendingLocked();
    }

    if (mGoingToSleep) {
        mUpdateMonitor.clearFingerprintRecognizedWhenKeyguardDone(currentUser);
        Log.i(TAG, "Device is going to sleep, aborting keyguardDone");
    } else {
        setPendingLock(false); // user may have authenticated during the screen off animation

        handleHide();
        mKeyguardInteractor.keyguardDoneAnimationsFinished();
        mUpdateMonitor.clearFingerprintRecognizedWhenKeyguardDone(currentUser);
    }
    Trace.endSection();
}

private void handleHide() {
    Trace.beginSection("KeyguardViewMediator#handleHide");

    // It's possible that the device was unlocked (via BOUNCER) while dozing. It's time to
    // wake up.
    if (mAodShowing) {
        mPM.wakeUp(mSystemClock.uptimeMillis(), PowerManager.WAKE_REASON_GESTURE,
                "com.android.systemui:BOUNCER_DOZING");
    }

    synchronized (KeyguardViewMediator.this) {
        if (DEBUG) Log.d(TAG, "handleHide");

        // If waking and unlocking, waking from dream has been set properly.
        if (!mWakeAndUnlocking) {
            setUnlockAndWakeFromDream(mStatusBarStateController.isDreaming()
                    && mPM.isInteractive(), WakeAndUnlockUpdateReason.HIDE);
        }

        if (mBootCompleted && ((mShowing && !mOccluded) || mUnlockingAndWakingFromDream)) {
            if (mUnlockingAndWakingFromDream) {
                Log.d(TAG, "hiding keyguard before waking from dream");
            }
            mHiding = true;
            mLastHideRequest = mLastShowRequest;
            mKeyguardGoingAwayRunnable.run();
        } else {
            if (!KeyguardWmStateRefactor.isEnabled()) {
                mKeyguardViewControllerLazy.get().hide(
                        mSystemClock.uptimeMillis() + mHideAnimation.getStartOffset(),
                        mHideAnimation.getDuration());
            }

            onKeyguardExitFinished("Hiding keyguard while occluded. Just hide the keyguard "
                    + "view and exit.");
        }

        // It's possible that the device was unlocked (via BOUNCER or Fingerprint) while
        // dreaming. It's time to wake up.
        if ((mDreamOverlayShowing || mUpdateMonitor.isDreaming()) && !mOrderUnlockAndWake) {
            mPM.wakeUp(mSystemClock.uptimeMillis(), PowerManager.WAKE_REASON_GESTURE,
                    "com.android.systemui:UNLOCK_DREAMING");
        }
    }
    Trace.endSection();
}
```

这些分支说明“认证成功”和“锁屏已经消失”之间仍有工作：核实当前用户/睡眠状态、处理 going-away/远程动画、同步窗口可见性和完成回调。代码出现 legacy/new 路径分支时必须保留 flag 条件，不能挑一个分支写成 Android 17 的唯一流程。

调试时至少同时记录 showing、occluded、going-away、wakefulness 和 bouncer/scene 状态。应用盖在锁屏上（occluded）不必然意味着设备已认证；反过来，认证已满足也可能仍在执行退出动画。

### 13.5 KeyguardUpdateMonitor：监听与信任语义

monitor 汇集电池、SIM、用户和认证相关状态。回调集合使用 WeakReference；注册后会发送当前状态快照，重复注册与失效引用也需要处理。即使用弱引用，拥有明确生命周期的控制器仍应成对注册/移除，不能依赖 GC 决定什么时候停止业务回调。


源码：[KeyguardUpdateMonitor.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/keyguard/KeyguardUpdateMonitor.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void registerCallback(KeyguardUpdateMonitorCallback callback) {
    Assert.isMainThread();
    mLogger.logRegisterCallback(callback);
    // Prevent adding duplicate callbacks

    for (int i = 0; i < mCallbacks.size(); i++) {
        if (mCallbacks.get(i).get() == callback) {
            mLogger.logException(
                    new Exception("Called by"),
                    "Object tried to add another callback");
            return;
        }
    }
    mCallbacks.add(new WeakReference<>(callback));
    removeCallback(null); // remove unused references
    sendUpdates(callback);
}

public void removeCallback(KeyguardUpdateMonitorCallback callback) {
    Assert.isMainThread();
    mLogger.logUnregisterCallback(callback);

    mCallbacks.removeIf(el -> el.get() == callback);
}

public boolean getUserCanSkipBouncer(int userId) {
    return getUserHasTrust(userId) || getUserUnlockedWithBiometric(userId)
            || forceIsDismissibleIsKeepingDeviceUnlocked();
}

public boolean getUserHasTrust(int userId) {
    return !isTrustDisabled() && mUserHasTrust.get(userId)
            && isUnlockingWithTrustAgentAllowed();
}

public boolean getUserTrustIsManaged(int userId) {
    return mUserTrustIsManaged.get(userId) && !isTrustDisabled();
}
```

`getUserTrustIsManaged()` 描述信任是否受管理，并不代表当前用户已经被信任。是否能跳过 bouncer 应遵循 `getUserCanSkipBouncer()` 所组合的 trust/biometric 与 strong-auth 约束，不能写 `if (isManaged) dismiss()`。

一次生物识别回调也不必然满足所有认证强度要求。重启后、lockout、管理员策略或强认证状态变化时，界面必须按系统策略要求主凭据；不要用 UI 布尔值绕过服务器侧凭据判断。

### 13.6 安全模式与图案认证完整回调

PIN、图案、密码、SIM PIN/PUK 和生物识别不是可以互换的 UI 皮肤。SecurityContainerController 根据安全模式和认证结果决定继续显示哪一个安全屏幕、是否允许 finish；SIM 解锁成功也不等于用户的设备凭据已验证。

图案入口在 `KeyguardPatternViewController.OnPatternListener.onPatternDetected()`，不是 `PatternKeyguardView.onPatternDetected()`。它禁用输入、取消先前待完成检查、构造 LockscreenCredential 并异步调用 LockPatternChecker；短图案和有效凭据路径的统计/回调不同：


源码：[KeyguardPatternViewController.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/keyguard/KeyguardPatternViewController.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void onPatternDetected(final List<LockPatternView.Cell> pattern) {
    mKeyguardUpdateMonitor.setCredentialAttempted();
    mLockPatternView.disableInput();
    if (mPendingLockCheck != null) {
        mPendingLockCheck.cancel(false);
    }

    final int userId = mSelectedUserInteractor.getSelectedUserId();
    if (pattern.size() < LockPatternUtils.MIN_PATTERN_REGISTER_FAIL) {
        // Treat single-sized patterns as erroneous taps.
        if (pattern.size() == 1) {
            mFalsingCollector.updateFalseConfidence(FalsingClassifier.Result.falsed(
                    0.7, getClass().getSimpleName(), "empty pattern input"));
        }
        mLockPatternView.enableInput();
        onPatternChecked(userId, false, Duration.ZERO,
                false /* not valid - too short */, false /* isDuplicate */);
        return;
    }

    mLatencyTracker.onActionStart(ACTION_CHECK_CREDENTIAL);
    mLatencyTracker.onActionStart(ACTION_CHECK_CREDENTIAL_UNLOCKED);
    mPendingLockCheck = LockPatternChecker.checkCredential(
            mLockPatternUtils,
            LockscreenCredential.createPattern(pattern),
            userId,
            new LockPatternChecker.OnCheckCallback() {

                @Override
                public void onEarlyMatched() {
                    mLatencyTracker.onActionEnd(ACTION_CHECK_CREDENTIAL);
                    onPatternChecked(
                            userId,
                            true /* matched */,
                            Duration.ZERO /* timeout */,
                            true /* isValidPattern */,
                            false /* isDuplicate */);
                }

                @Override
                public void onChecked(VerifyCredentialResponse response) {
                    boolean matched = response.isMatched();
                    Duration timeout = response.getTimeout();
                    boolean isDuplicate = lockscreenIndicateDuplicateGuesses()
                            && response.isCredAlreadyTried();
                    mLatencyTracker.onActionEnd(ACTION_CHECK_CREDENTIAL_UNLOCKED);
                    mLockPatternView.enableInput();
                    mPendingLockCheck = null;
                    if (!matched) {
                        onPatternChecked(
                                userId,
                                false /* matched */,
                                timeout,
                                true /* isValidPattern */,
                                isDuplicate);
                    }
                }

                @Override
                public void onCancelled() {
                    // We already got dismissed with the early matched callback, so we
                    // cancelled the check. However, we still need to note down the latency.
                    mLatencyTracker.onActionEnd(ACTION_CHECK_CREDENTIAL_UNLOCKED);
                }
            });
    if (pattern.size() > MIN_PATTERN_BEFORE_POKE_WAKELOCK) {
        getKeyguardSecurityCallback().userActivity();
        getKeyguardSecurityCallback().onUserInput();
    }
}

private void onPatternChecked(int userId, boolean matched, Duration timeout,
        boolean isValidPattern, boolean isDuplicate) {
    boolean dismissKeyguard = mSelectedUserInteractor.getSelectedUserId() == userId;
    if (matched) {
        mBouncerHapticPlayer.playAuthenticationFeedback(
                /* authenticationSucceeded= */true
        );
        getKeyguardSecurityCallback().reportUnlockAttempt(userId, true,
                Duration.ZERO, isDuplicate);
        if (dismissKeyguard) {
            mLockPatternView.setDisplayMode(LockPatternView.DisplayMode.Correct);
            mLatencyTracker.onActionStart(LatencyTracker.ACTION_LOCKSCREEN_UNLOCK);
            mUiLatencyStatsManager.ifPresent(m -> m.reportEvent(
                    UiLatencyStatsManager.EVENT_LOCK_SCREEN_UNLOCK_START,
                    SystemClock.elapsedRealtime()));
            Log.i(TAG,
                    "StartUnlock. "
                    + "User: " + userId
                    + " TS: " + SystemClock.uptimeMillis()
            );
            getKeyguardSecurityCallback().dismiss(true, userId, SecurityMode.Pattern);
        }
    } else {
        mBouncerHapticPlayer.playAuthenticationFeedback(
                /* authenticationSucceeded= */false
        );
        mLockPatternView.setDisplayMode(LockPatternView.DisplayMode.Wrong);
        if (isValidPattern) {
            getKeyguardSecurityCallback()
                    .reportUnlockAttempt(userId, false, timeout, isDuplicate);
            if (timeout.isPositive()) {
                Duration lockoutEndTime = mLockPatternUtils.getLockoutEndTime(userId);
                handleAttemptLockout(lockoutEndTime);
            }
        }
        if (timeout.isZero()) {
            int wrongPatternStringId =
                    isDuplicate
                            ? R.string.kg_primary_auth_duplicate_guess_pattern
                            : R.string.kg_wrong_pattern;
            mMessageAreaController.setMessage(wrongPatternStringId);
            mLockPatternView.postDelayed(mCancelPatternRunnable, PATTERN_CLEAR_TIMEOUT_MS);
        }
    }
}
```

该 tag 的结果参数使用 `Duration timeout`，并包含重复尝试等信息，不能把旧版 `int timeoutMs` 接口原封不动标为 Android 17。结果到达时还要核对用户身份，成功路径报告解锁并 dismiss，失败路径恢复输入/显示错误或进入锁定倒计时。

超时策略来自凭据校验与系统安全策略，不能固定宣称“失败 5 次就 30 秒、10 次就清空设备”。设备管理器的数据擦除阈值、Gatekeeper/凭据限流与 UI 提示是不同层次；本轮未做恶意尝试或设备策略测试。

`LockPatternChecker` 是异步协作入口，不是在 SystemUI 本地比较明文图案字符串。业务日志不能记录图案点序列、PIN/密码或认证 token；取消与清理同样属于敏感数据寿命管理。

### 13.7 生物识别：认证结果到解锁模式

系统锁屏的结果由 KeyguardUpdateMonitor 等状态输入进入 BiometricUnlockController。不同传感器和交互状态会选择不同解锁模式：息屏唤醒、保持 bouncer、解除锁屏、仅处理已唤醒 UI 并不是统一的 `authenticate -> hide`。


源码：[BiometricUnlockController.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/statusbar/phone/BiometricUnlockController.java)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```java
public void onBiometricAuthenticated(int userId, BiometricSourceType biometricSourceType,
        boolean isStrongBiometric) {
    Trace.beginSection("BiometricUnlockController#onBiometricAuthenticated");
    try {
        if (mUpdateMonitor.isGoingToSleep()) {
            mLogger.deferringAuthenticationDueToSleep(userId,
                    biometricSourceType,
                    mPendingAuthenticated != null);
            mPendingAuthenticated = new PendingAuthenticated(userId, biometricSourceType,
                    isStrongBiometric);
            return;
        }
        mBiometricType = biometricSourceType;
        mMetricsLogger.write(new LogMaker(MetricsEvent.BIOMETRIC_AUTH)
                .setType(MetricsEvent.TYPE_SUCCESS).setSubtype(toSubtype(biometricSourceType)));
        Optional.ofNullable(
                        BiometricUiEvent.SUCCESS_EVENT_BY_SOURCE_TYPE.get(biometricSourceType))
                .ifPresent(event -> UI_EVENT_LOGGER.log(event, getSessionId()));

        boolean unlockWithBypassAllowed =
                mKeyguardStateController.isOccluded()
                        || mKeyguardBypassController.onBiometricAuthenticated(
                        biometricSourceType, isStrongBiometric);

        if (secureLockDevice() && mSecureLockDeviceInteractor.get().isSecureLockDeviceEnabled()
                .getValue() && biometricSourceType == BiometricSourceType.FACE
        ) {
            mLogger.d("Delaying face authenticated signal until user confirmation on the "
                    + "Secure Lock Device UI.");
            return;
        } else if (unlockWithBypassAllowed) {
            mKeyguardViewMediator.userActivity();
            startWakeAndUnlock(biometricSourceType, isStrongBiometric);
        } else {
            if (SceneContainerFlag.isEnabled()) {
                // Always unlock with scene container enabled. device unlock state should always
                // be consistent with auth success event, whether lockscreen gets dismissed or
                // not is determined later by DeviceEntryInteractor.
                startWakeAndUnlock(MODE_NONE_UNLOCKED,
                        BiometricUnlockSource.Companion.fromBiometricSourceType(
                                biometricSourceType));
            }
            mLogger.d("onBiometricUnlocked aborted by bypass controller");
        }
    } finally {
        Trace.endSection();
    }
}

private @WakeAndUnlockMode int calculateMode(BiometricSourceType biometricSourceType,
        boolean isStrongBiometric) {
    if (biometricSourceType == BiometricSourceType.FACE
            || biometricSourceType == BiometricSourceType.IRIS) {
        return calculateModeForPassiveAuth(isStrongBiometric);
    } else {
        return calculateModeForFingerprint(isStrongBiometric);
    }
}

private @WakeAndUnlockMode int calculateModeForFingerprint(boolean isStrongBiometric) {
    final boolean unlockingAllowed =
            mUpdateMonitor.isUnlockingWithBiometricAllowed(isStrongBiometric);
    final boolean deviceInteractive = mUpdateMonitor.isDeviceInteractive();
    final boolean keyguardShowing = mKeyguardStateController.isShowing();
    final boolean deviceDreaming = mUpdateMonitor.isDreaming();

    logCalculateModeForFingerprint(unlockingAllowed, deviceInteractive,
            keyguardShowing, deviceDreaming, isStrongBiometric);
    if (!deviceInteractive) {
        if (!keyguardShowing && !mScreenOffAnimationController.isKeyguardShowDelayed()) {
            if (mKeyguardStateController.isUnlocked()) {
                return MODE_WAKE_AND_DISMISS;
            }
            return MODE_ONLY_WAKE;
        } else if (mDozeScrimController.isPulsing() && unlockingAllowed) {
            return MODE_WAKE_AND_DISMISS_PULSING;
        } else if (unlockingAllowed || !mKeyguardStateController.isMethodSecure()) {
            return MODE_WAKE_AND_DISMISS;
        } else {
            return MODE_SHOW_BOUNCER;
        }
    }
    if (unlockingAllowed && deviceDreaming) {
        return MODE_WAKE_AND_DISMISS_FROM_DREAM;
    }
    if (keyguardShowing) {
        if (isPrimaryBouncerShowing() && unlockingAllowed) {
            return MODE_DISMISS_BOUNCER;
        } else if (unlockingAllowed) {
            return MODE_DISMISS;
        } else if (!isBouncerShowing()) {
            return MODE_SHOW_BOUNCER;
        }
    }
    return MODE_NONE;
}

private @WakeAndUnlockMode int calculateModeForPassiveAuth(boolean isStrongBiometric) {
    final boolean deviceInteractive = mUpdateMonitor.isDeviceInteractive();
    final boolean isKeyguardShowing = mKeyguardStateController.isShowing();
    final boolean unlockingAllowed =
            mUpdateMonitor.isUnlockingWithBiometricAllowed(isStrongBiometric);
    final boolean deviceDreaming = mUpdateMonitor.isDreaming();
    final boolean bypass = mKeyguardBypassController.getBypassEnabled()
            || mAuthController.isUdfpsFingerDown();
    final boolean isBouncerShowing = isBouncerShowing();

    logCalculateModeForPassiveAuth(unlockingAllowed, deviceInteractive, isKeyguardShowing,
            deviceDreaming, bypass, isStrongBiometric);
    if (!deviceInteractive) {
        if (!unlockingAllowed) {
            return bypass ? MODE_SHOW_BOUNCER : MODE_NONE;
        } else if (!isKeyguardShowing) {
            return bypass ? MODE_WAKE_AND_DISMISS : MODE_ONLY_WAKE_UNLOCKED;
        } else if (mDozeScrimController.isPulsing()) {
            return MODE_WAKE_AND_DISMISS_PULSING; // always unlock from the pulsing state
        } else {
            if (bypass) {
                // Wake-up fading out nicely
                return MODE_WAKE_AND_DISMISS_PULSING;
            } else {
                // We could theoretically return MODE_NONE_UNLOCKED, but this means that the
                // device would be not interactive, unlocked, and the user would not see the
                // device state.
                return MODE_ONLY_WAKE_UNLOCKED;
            }
        }
    }
    if (unlockingAllowed && deviceDreaming) {
        final boolean wakeAndUnlock = bypass || (dreamsV2() && isBouncerShowing);
        return wakeAndUnlock ? MODE_WAKE_AND_DISMISS_FROM_DREAM : MODE_ONLY_WAKE_UNLOCKED;
    }
    if (unlockingAllowed && mKeyguardStateController.isOccluded()) {
        return MODE_DISMISS;
    }
    if (isKeyguardShowing) {
        if (unlockingAllowed) {
            if (isBouncerShowing) {
                return MODE_DISMISS_BOUNCER;
            } else if (bypass) {
                return MODE_DISMISS;
            } else {
                return MODE_NONE_UNLOCKED;
            }
        } else {
            return bypass ? MODE_SHOW_BOUNCER : MODE_NONE;
        }
    }
    return MODE_NONE;
}
```

指纹与被动认证分支不同，还要考虑认证强度、bypass、交互状态、bouncer 和强认证要求。生物识别不能笼统断言“全部弱于凭据且都用同一种 HAL”；具体强度分类与系统策略以设备实现和安全规范为准。

应用层 framework/AndroidX BiometricPrompt 用于应用自己的认证请求，不会让普通应用拥有 KeyguardUpdateMonitor 的系统级控制权。旧文混合两套 Prompt API 的片段已移除，避免复制后既无法编译又产生“可代替系统解锁”的错误理解。

### 13.8 锁屏通知、隐私与窗口交互

通知路径仍是 NMS -> NotificationListener -> NotifCollection/后续列表管线，不是旧 NotificationEntryManager。通知在锁屏上是否显示、是否隐藏正文、工作资料是否受限，需要综合当前用户、锁屏设置、通知 visibility/publicVersion 和 SystemUI 的锁屏用户策略。

```text
同一 NotificationEntry
  -> 全量 private 内容: 用户已获准查看时
  -> public/redacted 内容: 锁屏敏感内容受限时
  -> 过滤/不展示: 用户或渠道策略不允许时
```

展示 public 内容不应泄露 private 标题、图片、远程输入草稿或隐私摘要；也不能通过复用上一条已解锁 row 的缓存绕过重新绑定。用户切换/资料锁定与 keyguard 状态变化都可能要求更新已有行，而不仅仅影响新来的通知。

WindowManager 侧 keyguard 可见性、occlusion 与应用窗口策略需要同步，导航/状态栏和通知 shade 也随之调整。这不表示 Keyguard 是一个额外 system_server View；实际 UI 仍位于 SystemUI 进程。

### 13.9 真实状态模型与 scene 迁移

旧文的 `STATE_HIDE/STATE_SHOW/STATE_BOUNCER/STATE_OCCLUDED` 是概念草图，不是 Android 17 的统一源码枚举。当前 KeyguardState 定义如下，保留弃用注解与 scene-container 提示，防止将迁移期模型冒充唯一 UI 状态源：


源码：[KeyguardState.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/src/com/android/systemui/keyguard/shared/model/KeyguardState.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
enum class KeyguardState {
    /**
     * The display is completely off, as well as any sensors that would trigger the device to wake
     * up.
     */
    OFF,
    /**
     * The device has entered a special low-power mode within SystemUI. Doze is technically a
     * special dream service implementation. No UI is visible. In this state, a least some
     * low-powered sensors such as lift to wake or tap to wake are enabled, or wake screen for
     * notifications is enabled, allowing the device to quickly wake up.
     */
    DOZING,
    /**
     * A device state after the device times out, which can be from both LOCKSCREEN or GONE states.
     * DOZING is an example of special version of this state. Dreams may be implemented by third
     * parties to present their own UI over keyguard, like a screensaver.
     */
    @Deprecated(
        "This state won't exist anymore when scene container gets enabled. If you are " +
            "writing prod code today, make sure to either use flag aware APIs in " +
            "[KeyguardTransitionInteractor] or flag appropriately with [SceneContainerFlag]."
    )
    DREAMING,
    /**
     * The device has entered a special low-power mode within SystemUI, also called the Always-on
     * Display (AOD). A minimal UI is presented to show critical information. If the device is in
     * low-power mode without a UI, then it is DOZING.
     */
    AOD,
    /**
     * The security screen prompt containing UI to prompt the user to use a biometric credential
     * (ie: fingerprint). When supported, this may show before showing the primary bouncer.
     */
    ALTERNATE_BOUNCER,
    /**
     * The security screen prompt UI, containing PIN, Password, Pattern for the user to verify their
     * credentials.
     */
    @Deprecated(
        "This state won't exist anymore when scene container gets enabled. If you are " +
            "writing prod code today, make sure to either use flag aware APIs in " +
            "[KeyguardTransitionInteractor] or flag appropriately with [SceneContainerFlag]."
    )
    PRIMARY_BOUNCER,
    /**
     * Device is actively displaying keyguard UI and is not in low-power mode. Device may be
     * unlocked if SWIPE security method is used, or if face lockscreen bypass is false.
     */
    LOCKSCREEN,
    /**
     * Device is locked or on dream and user has swiped from the right edge to enter the glanceable
     * hub UI. From this state, the user can swipe from the left edge to go back to the lock screen
     * or dream, as well as swipe down for the notifications and up for the bouncer.
     */
    @Deprecated(
        "This state won't exist anymore when scene container gets enabled. If you are " +
            "writing prod code today, make sure to either use flag aware APIs in " +
            "[KeyguardTransitionInteractor] or flag appropriately with [SceneContainerFlag]."
    )
    GLANCEABLE_HUB,
    /**
     * Keyguard is no longer visible. In most cases the user has just authenticated and keyguard is
     * being removed, but there are other cases where the user is swiping away keyguard, such as
     * with SWIPE security method or face unlock without bypass.
     */
    @Deprecated(
        "This state won't exist anymore when scene container gets enabled. If you are " +
            "writing prod code today, make sure to either use flag aware APIs in " +
            "[KeyguardTransitionInteractor] or flag appropriately with [SceneContainerFlag]."
    )
    GONE,
    /**
     * Only used in scene framework. This means we are currently on any scene framework scene that
     * is not Lockscreen. Transitions to and from UNDEFINED are always bound to the
     * [SceneTransitionLayout] scene transition that either transitions to or from the Lockscreen
     * scene. These transitions are automatically handled by [LockscreenSceneTransitionInteractor].
     */
    UNDEFINED,
    /** An activity is displaying over the keyguard. */
    @Deprecated(
        "This state won't exist anymore when scene container gets enabled. If you are " +
            "writing prod code today, make sure to either use flag aware APIs in " +
            "[KeyguardTransitionInteractor] or flag appropriately with [SceneContainerFlag]."
    )
    OCCLUDED;

    fun checkValidState() {
        val isStateValid: Boolean
        val isEnabled: String
        if (SceneContainerFlag.isEnabled) {
            isStateValid = this === mapToSceneContainerState()
            isEnabled = "enabled"
        } else {
            isStateValid = this !== UNDEFINED
            isEnabled = "disabled"
        }

        if (!isStateValid) {
            throw IllegalStateException(
                "State $this is not a valid state when scene container is $isEnabled"
            )
        }
    }

    fun mapToSceneContainerState(): KeyguardState {
        return when (this) {
            OFF,
            DOZING,
            AOD,
            ALTERNATE_BOUNCER,
            LOCKSCREEN -> this
            GLANCEABLE_HUB,
            PRIMARY_BOUNCER,
            GONE,
            OCCLUDED,
            DREAMING,
            UNDEFINED -> UNDEFINED
        }
    }

    fun mapToSceneContainerContent(): ContentKey? {
        return when (this) {
            OFF,
            DOZING,
            AOD,
            ALTERNATE_BOUNCER,
            LOCKSCREEN -> Scenes.Lockscreen
            GLANCEABLE_HUB -> Scenes.Communal
            PRIMARY_BOUNCER -> Overlays.Bouncer
            GONE -> Scenes.Gone
            OCCLUDED -> Scenes.Occluded
            DREAMING -> Scenes.Dream
            UNDEFINED -> null
        }
    }

    companion object {

        /**
         * Whether the device is awake ([PowerInteractor.isAwake]) when we're FINISHED in the given
         * keyguard state.
         */
        fun deviceIsAwakeInState(state: KeyguardState, scene: ContentKey?): Boolean {
            state.checkValidState()
            return when (state) {
                OFF -> false
                DOZING -> false
                DREAMING -> false
                GLANCEABLE_HUB -> true
                AOD -> false
                ALTERNATE_BOUNCER -> true
                PRIMARY_BOUNCER -> true
                LOCKSCREEN -> true
                GONE -> true
                OCCLUDED -> true
                UNDEFINED -> deviceIsAwakeInScene(scene!!)
            }
        }

        private fun deviceIsAwakeInScene(scene: ContentKey): Boolean {
            return scene != Scenes.Dream
        }

        /**
         * Whether the device is awake ([PowerInteractor.isAsleep]) when we're FINISHED in the given
         * keyguard state.
         */
        fun deviceIsAsleepInState(state: KeyguardState, scene: ContentKey?): Boolean {
            return !deviceIsAwakeInState(state, scene)
        }
    }
}
```

状态模型、Mediator 的 mShowing/occluded、认证授权状态是不同维度。一次 LOCKSCREEN -> GONE 的视觉转场，不能单独证明凭据验证来自哪种安全途径；发生 OCCLUDED 也不应清空所有锁屏安全状态。

监听状态转场的消费者需要处理 started/running/finished/canceled 等转场寿命以及 scope 取消；本章没有逐项审计全部 scene/interactor 实现，不提供超出已核验入口的统一替代代码。

### 13.10 安全与生命周期实践

认证 UI 的输入监听、monitor callback、异步 credential task 和动画各有寿命。View detach 或当前用户变化时，应按控制器实际实现取消/解除旧工作，不能等旧结果回来后再盲目修改新用户界面。

显示错误与失败统计要使用系统提供的结果，避免客户端自己计数作为认证依据。处理 lockout 时，倒计时只是 UI 表达，真正重试资格仍应由认证服务判断。

锁屏通知默认采用最小必要内容，并提供可靠的 publicVersion；日志排障应优先 key、状态和时序，而不是凭据或通知正文。生物识别可用性、强度、管理策略和设备功耗需要实机验证，本次文档核验不代替这些安全验收。

## 14. Keyguard 面试常见问题

### 14.1 谁启动 Keyguard？

SystemUI startables 初始化 Mediator；system_server 的 PhoneWindowManager 通过 KeyguardServiceDelegate 绑定 SystemUI 的 KeyguardService，并传递系统 ready 等事件。它不是 SystemServer 直接 new 一个运行在本进程的 Keyguard View。

### 14.2 认证成功为什么还没有立即隐藏锁屏？

先区分认证结果、当前用户/strong-auth 状态、Mediator 完成处理以及退出转场。结果可能需要主凭据补充，用户可能已经切换，也可能已经认证但还在完成 going-away/窗口动画。应沿结果到模式选择再到 Handler/视图的链路分析，而不是强制设 mShowing=false。

### 14.3 Trust managed 可以跳过 bouncer 吗？

不可以这样判断。managed 与 has trust 是不同含义；`getUserCanSkipBouncer()` 还组合认证/强认证条件。UI 不得把“由信任服务管理”当作“已经认证”。

### 14.4 锁屏与 AOD 是同一个状态机吗？

不是。DozeMachine 控制息屏显示过程；keyguard 模型和 scene/transition 控制锁屏 UI；wakefulness 和显示电源状态又是另外维度。它们协作，但不能将各自枚举混成一条五态循环。

### 14.5 如何定位通知只在锁屏消失？

先确认 NMS 和 NotifCollection 中记录仍存在，再看当前用户/资料、通知 visibility/publicVersion、锁屏用户设置和过滤/分组策略，最后检查内容绑定与窗口可见性。不要仅凭截图断言通知已被 NMS 删除。

## 总结

SystemUI 是独立进程的系统应用；Android 17 的 Application 入口、startables 和插件 Kotlin 路径需要从固定 tag 追踪。通知、Doze 和 Keyguard 各有服务端策略、状态控制与 UI 渲染边界，理解异步回调、取消、用户切换和产品开关，比记住一条没有条件分支的伪调用链更重要。

本文保留基础概念、架构图、应用通知示例和设计解释，用真实方法替换旧版/虚构实现。源码节选并非可独立编译工程；本轮全文阅读与关键源码静态核验不等于对全部 AOSP 断言、所有开关组合或硬件行为的穷举验证。

**源码基线：** AOSP `android-17.0.0_r1`；**审阅日期：** 2026-09-10。
