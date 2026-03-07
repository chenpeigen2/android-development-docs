# Android Activity 启动流程完全指南

> 作者：OpenClaw | 日期：2026-03-07

## 目录

1. [概述](#1-概述)
2. [Activity 启动的两种方式](#2-activity-启动的两种方式)
3. [启动流程详解](#3-启动流程详解)
4. [核心组件交互](#4-核心组件交互)
5. [生命周期回调](#5-生命周期回调)
6. [常见问题与优化](#6-常见问题与优化)
7. [总结](#7-总结)

---

## 1. 概述

Activity 是 Android 应用开发中最常用的组件之一，它是用户与应用交互的入口。理解 Activity 的启动流程对于构建高性能、用户体验良好的 Android 应用至关重要。

本文将详细讲解从用户点击图标到 Activity 完整显示在屏幕上的全过程。

---

## 2. Activity 启动的两种方式

### 2.1 显式启动

```java
Intent intent = new Intent(this, MainActivity.class);
startActivity(intent);
```

直接指定目标 Activity 的类名。

### 2.2 隐式启动

```java
Intent intent = new Intent(Intent.ACTION_VIEW);
intent.setData(Uri.parse("https://example.com"));
startActivity(intent);
```

通过 Action、Data、Category 匹配系统或应用的 Activity。

---

## 3. 启动流程详解

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户空间                                  │
├─────────────────────────────────────────────────────────────────┤
│  App A (调用方)        │    ActivityTaskManagerService       │
│  ┌─────────────┐       │    ┌─────────────────────────────┐   │
│  │  Activity   │       │    │  ActivityTaskManagerService │   │
│  │  (Client)   │ ────► │    │  (System Server)           │   │
│  └─────────────┘  IPC  │    └─────────────────────────────┘   │
│                        │              │                        │
│                        │              ▼                        │
│                        │    ┌─────────────────────────────┐   │
│                        │    │  ActivityStackSupervisor  │   │
│                        │    └─────────────────────────────┘   │
│                        │              │                        │
│                        ▼              ▼                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Zygote 进程                           │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │           Activity Thread (主线程)                  │ │  │
│  │  │  ┌────────────┐  ┌────────────┐  ┌─────────────┐  │ │  │
│  │  │  │  Activity  │  │  Window   │  │  View      │  │ │  │
│  │  │  │  (Activity)│  │  Manager  │  │  Root      │  │ │  │
│  │  │  └────────────┘  └────────────┘  └─────────────┘  │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 完整流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Activity 启动流程图                                  │
└─────────────────────────────────────────────────────────────────────────────┘

用户点击                    应用层                     系统服务层                Zygote/系统
  │                          │                           │                       │
  ▼                          │                           │                       │
┌─────────┐                  │                           │                       │
│ 点击图标 │                  │                           │                       │
└────┬────┘                  │                           │                       │
     │                       │                           │                       │
     ▼                       │                           │                       │
┌─────────────┐              │                           │                       │
│startActivity│              │                           │                       │
│   (Intent)  │              │                           │                       │
└─────┬───────┘              │                           │                       │
      │                      │                           │                       │
      │                      │                           │                       │
      └──────────┬───────────┘                           │                       │
                 │                                       │                       │
                 ▼                                       │                       │
┌───────────────────────────────────────────────────────┐  │                       │
│                   Instrumentation                     │  │                       │
│  ┌────────────────────────────────────────────────┐  │  │                       │
│  │ 1. 检查启动参数                                │  │                       │
│  │ 2. 通过 Binder 调用 ATMS.startActivity()       │  │                       │
│  └────────────────────────────────────────────────┘  │                       │
└─────────────────────┬────────────────────────────────┘                       │
                      │                                                        │
                      ▼                                                        │
┌─────────────────────────────────────────────────────────────────────────────┐
│              ActivityTaskManagerService (ATMS) - System Server               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  3. ActivityStarter.execute()                                        │    │
│  │     - 解析 Intent                                                    │    │
│  │     - 检查权限                                                       │    │
│  │     - 决定启动模式 (launchMode)                                      │    │
│  │     - 处理 Flags                                                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  4. ActivityStackSupervisor.startActivityUnchecked()                │    │
│  │     - 决定 Task 归属                                                │    │
│  │     - 处理 Activity 栈                                              │    │
│  │     - 调度 ActivityStack                                           │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  5. ActivityStack.startActivityLocked()                           │    │
│  │     - 将 ActivityRecord 入栈                                       │    │
│  │     - 处理切换动画                                                  │    │
│  │     - 调用 resumeTopActivityInnerLocked()                          │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               │ IPC: startProcess()
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Zygote 进程 Fork                                    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  6. ZygoteServer.runSelectLoop()                                  │    │
│  │     - 接收 ZygoteProcess 消息                                      │    │
│  │     - Fork 新进程                                                  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  7. 新进程执行 ActivityThread.main()                               │    │
│  │     - 创建 Looper                                                  │    │
│  │     - 进入消息循环                                                 │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               │ IPC: bindApplication()
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        应用进程 (ActivityThread)                            │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  8. handleBindApplication()                                        │    │
│  │     - 创建 Application                                             │    │
│  │     - 调用 Application.onCreate()                                  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  9. ActivityThread.performLaunchActivity()                        │    │
│  │     ┌─────────────────────────────────────────────────────────┐   │    │
│  │     │  a. ClassLoader 加载 Activity 类                        │   │    │
│  │     │  b. 创建 Activity 实例 (newInstance)                   │   │    │
│  │     │  c. 创建 Context (createBaseContextForActivity)        │   │    │
│  │     │  d. activity.attach() - 关联 Window                    │   │    │
│  │     │  e. Instrumentation.callActivityOnCreate()              │   │    │
│  │     └─────────────────────────────────────────────────────────┘   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  10. Activity.onCreate()                                          │    │
│  │      - setContentView() - 设置布局                              │    │
│  │      - 触发 ViewRootImpl 创建                                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  11. ViewRootImpl.performTraversals()                            │    │
│  │      ┌─────────────────────────────────────────────────────┐    │    │
│  │      │  a. measure() → onMeasure()                         │    │    │
│  │      │  b. layout() → onLayout()                          │    │    │
│  │      │  c. draw() → onDraw()                               │    │    │
│  │      └─────────────────────────────────────────────────────┘    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  12. onStart() → onResume()                                      │    │
│  │      - Activity 可见且可交互                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         🎉 Activity 启动完成！                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 核心类协作时序图

```
     User          App             ATMS           Stack          Zygote       ActivityThread
      │             │               │               │               │                 │
      │─────────────│               │               │               │                 │
      │startActivity│               │               │               │                 │
      │─────────────│               │               │               │                 │
      │             │──Instrumentation.execStartActivity()──►│                 │
      │             │               │               │               │                 │
      │             │               │◄───startActivity()────│                 │
      │             │               │               │               │                 │
      │             │               │──ActivityStarter.execute()──►              │
      │             │               │               │               │                 │
      │             │               │──StackSupervisor.startActivityUnchecked()►│
      │             │               │               │               │                 │
      │             │               │               │──startActivityLocked()──►      │
      │             │               │               │               │                 │
      │             │               │◄───────────────────────────────────────────│
      │             │               │               │               │                 │
      │             │               │───────────────│startProcess()│                 │
      │             │               │               │               │                 │
      │             │               │               │◄──────Zygote.fork()───────────│
      │             │               │               │               │                 │
      │             │               │               │               │──►ActivityThread.main()
      │             │               │               │               │                 │
      │             │               │               │               │◄─────bindApplication()
      │             │               │               │               │                 │
      │             │◄───────────────────────────────────────────────handleBindApplication()
      │             │               │               │               │                 │
      │             │◄──────────────────────────────────performLaunchActivity()          │
      │             │               │               │               │                 │
      │◄────onCreate()───────────────────────────────────────────────────────────────────────│
      │             │               │               │               │                 │
      │◄────onStart()─────────────────────────────────────────────────────────────────────────│
      │             │               │               │               │                 │
      │◄────onResume()────────────────────────────────────────────────────────────────────────│
      │             │               │               │               │                 │
      ▼             ▼               ▼               ▼               ▼                 ▼
   完成         等待            等待             等待            等待               运行中
```

### 3.4 进程间通信 (IPC) 总结

```
┌─────────────────┐        Binder         ┌─────────────────┐
│   App Process   │◄───────────────────►│ System Server   │
│                 │                      │                 │
│ ApplicationThread│                      │   ATMS          │
│ (客户端 Stub)   │                      │ (服务端)        │
└────────┬────────┘                      └────────┬────────┘
         │                                        │
         │  IApplicationThread                   │
         │  (Binder 接口)                        │
         ▼                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│               AMS 与 ActivityThread 通信详解                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Binder 通信架构                        │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  应用进程 (Client)          系统服务进程 (Server)        │   │
│  │  ┌──────────────┐         ┌──────────────────┐       │   │
│  │  │ IApplication │◄───────►│ IActivityTask    │       │   │
│  │  │   Thread     │  Binder  │   Manager        │       │   │
│  │  │  (AIDL)    │          │    (AIDL)       │       │   │
│  │  └──────────────┘         └──────────────────┘       │   │
│  │          │                            │                  │   │
│  │          │                            │                  │   │
│  │          ▼                            ▼                  │   │
│  │  ┌──────────────┐         ┌──────────────────┐       │   │
│  │  │Application   │         │ ActivityTask     │       │   │
│  │  │Thread        │         │ ManagerService   │       │   │
│  │  │(客户端)      │         │ (ATMS 服务端)    │       │   │
│  │  └──────────────┘         └──────────────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 关键 AIDL 接口                           │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  IApplicationThread (应用 → 系统)                       │   │
│  │  ├── scheduleCreateActivity() - 创建 Activity           │   │
│  │  ├── scheduleResumeActivity() - 恢复 Activity         │   │
│  │  ├── schedulePauseActivity() - 暂停 Activity          │   │
│  │  ├── scheduleStopActivity() - 停止 Activity          │   │
│  │  └── scheduleDestroyActivity() - 销毁 Activity         │   │
│  │                                                          │   │
│  │  IActivityTaskManager (系统 → 应用)                       │   │
│  │  ├── startActivity() - 启动 Activity                   │   │
│  │  ├── finishActivity() - 结束 Activity                  │   │
│  │  └── getActivities() - 获取 Activity 列表              │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐        Binder         ┌─────────────────┐
│   App Process   │◄───────────────────►│ System Server   │
│                 │                      │                 │
│ ApplicationThread│                      │   ATMS          │
│ (客户端 Stub)   │                      │ (服务端)        │
└─────────────────┘                      └────────┬────────┘
                                                  │
                                                  │ Socket
                                                  ▼
                                         ┌─────────────────┐
│   Zygote 进程      │◄───────────────────►│  System Server  │
│                    │                      │                 │
│  ZygoteServer     │                      │  ActivityManager│
│  (监听 Socket)    │                      │  Service        │
└─────────────────┘                      └─────────────────┘
```

### 3.5 AMS 与 ActivityThread 完整通信流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│            AMS → ActivityThread 完整通信流程                                 │
└─────────────────────────────────────────────────────────────────────────────┘

1. ATMS (ActivityTaskManagerService) 在 SystemServer 中启动
       │
       ▼
2. 应用进程启动时，通过 Binder 获取 IActivityTaskManager
       │  (ServiceManager.getService("activity_task"))
       ▼
3. ATMS 通过 IApplicationThread Binder 接口与应用通信
       │
       │  应用端: ApplicationThread (继承 IApplicationThread.Stub)
       │  系统端: ApplicationThreadProxy (客户端代理)
       │
       ▼
4. 关键通信流程:

   ┌────────────────────────────────────────────────────────────────┐
   │  启动新 Activity (新进程)                                      │
   ├────────────────────────────────────────────────────────────────┤
   │                                                                 │
   │  ATMS.startActivity()                                          │
   │       │                                                         │
   │       ▼                                                         │
   │  ActivityStarter.execute()                                     │
   │       │                                                         │
   │       ▼                                                         │
   │  StackSupervisor.startActivityUnchecked()                       │
   │       │                                                         │
   │       ▼                                                         │
   │  processHolder.startProcess()                                  │
   │       │                                                         │
   │       ▼                                                         │
   │  ZygoteProcess.start()                                         │
   │       │                                                         │
   │       │  Socket 通信                                            │
   │       ▼                                                         │
   │  ZygoteServer.acceptSocket()                                   │
   │       │                                                         │
   │       ▼                                                         │
   │  fork() 创建新进程                                             │
   │       │                                                         │
   │       ▼                                                         │
   │  新进程执行 ActivityThread.main()                               │
   │       │                                                         │
   │       ▼                                                         │
   │  attachApplication()                                            │
   │       │  ┌──────────────────────────────────────────┐          │
   │       └──►│  Binder: IActivityTaskManager          │          │
   │              │  .attachApplication(appThread)     │          │
   │              └──────────────┬───────────────────────┘          │
   │                            │                                    │
   │                            ▼                                    │
   │              ATMS.attachApplication()                           │
   │                            │                                    │
   │                            ▼                                    │
   │              StackSupervisor.attachApplication()                │
   │                            │                                    │
   │                            ▼                                    │
   │              realStartActivityLocked()                         │
   │                            │                                    │
   │                            ▼                                    │
   │              ┌──────────────────────────────────────────┐     │
   │              │  Binder: IApplicationThread              │     │
   │              │  .scheduleCreateActivity()              │     │
   │              └──────────────┬───────────────────────┘     │
   │                            │                                 │
   │                            ▼                                 │
   │              ApplicationThread.scheduleCreateActivity()      │
   │                            │                                 │
   │                            ▼                                 │
   │              ActivityThread.handleCreateActivity()           │
   │                            │                                 │
   │                            ▼                                 │
   │              performLaunchActivity()                         │
   │                            │                                 │
   │                            ▼                                 │
   │              activity.onCreate()                            │
   │                                                                 │
   └────────────────────────────────────────────────────────────────┘

   ┌────────────────────────────────────────────────────────────────┐
   │  Activity 生命周期回调                                         │
   ├────────────────────────────────────────────────────────────────┤
   │                                                                 │
   │  ATMS 需要通知 Activity 执行生命周期时:                         │
   │                                                                 │
   │  1. ATMS 调用 IApplicationThread.scheduleResumeActivity()    │
   │        │                                                        │
   │        ▼                                                        │
   │  2. ApplicationThread → ActivityThread.H                       │
   │        │  (发送到主线程 Handler)                               │
   │        ▼                                                        │
   │  3. ActivityThread.H 处理 EXECUTE_TRANSACTION                 │
   │        │                                                        │
   │        ▼                                                        │
   │  4. ActivityThread.performResumeActivity()                    │
   │        │                                                        │
   │        ▼                                                        │
   │  5. mInstrumentation.callActivityOnResume()                  │
   │        │                                                        │
   │        ▼                                                        │
   │  6. activity.onResume()                                       │
   │                                                                 │
   └────────────────────────────────────────────────────────────────┘

### 3.6 ApplicationThread 详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ApplicationThread 详解                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    ApplicationThread 架构                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ApplicationThread 继承关系:                                             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                                                            │       │
│  │  public class ApplicationThread extends IApplicationThread.Stub │       │
│  │                                                            │       │
│  │  - 是 IApplicationThread 的服务端实现                         │       │
│  │  - 运行在应用进程                                            │       │
│  │  - 接收系统服务 (ATMS) 的指令                               │       │
│  │                                                            │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                                                            │       │
│  │  IApplicationThread (AIDL 接口)                             │       │
│  │                                                            │       │
│  │  ├── scheduleCreateActivity()     - 创建 Activity           │       │
│  │  ├── scheduleDestroyActivity()   - 销毁 Activity           │       │
│  │  ├── schedulePauseActivity()    - 暂停 Activity            │       │
│  │  ├── scheduleResumeActivity()  - 恢复 Activity            │       │
│  │  ├── scheduleStopActivity()    - 停止 Activity            │       │
│  │  ├── scheduleConfigurationChanged() - 配置变化            │       │
│  │  ├── scheduleLowMemory()       - 内存低                  │       │
│  │  └── bindApplication()        - 绑定 Application         │       │
│  │                                                            │       │
│  └──────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    ApplicationThread 核心方法                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  // 1. bindApplication - 应用进程启动时调用                              │
│  public void bindApplication(String processName, ApplicationInfo appInfo,    │
│      List<ProfilerInfo> profilerInfo, Bundle bundle,                     │
│      IInstrumentationWriter instrumentationWriter,                         │
│      List<ProviderInfo> providers, String seq) {                         │
│                                                                         │
│      // 创建 Application                                                │
│      AppBindData data = new AppBindData();                             │
│      data.processName = processName;                                    │
│      data.appInfo = appInfo;                                           │
│      ...                                                                │
│                                                                         │
│      // 发送到主线程 Handler                                           │
│      sendMessage(H.BIND_APPLICATION, data);                             │
│  }                                                                      │
│                                                                         │
│  // 2. scheduleCreateActivity - 创建 Activity                          │
│  public void scheduleCreateActivity(IBinder token, int ident,           │
│      ActivityInfo info, Configuration curConfig,                         │
│      Configuration overrideConfig, int procState, Bundle savedState,    │
│      List<ResultInfo> pendingResults, List<ReferrerInfo> pendingNewIntents,  │
│      boolean isForward, ProfilerInfo profilerInfo, Runnable crashHandler) {  │
│                                                                         │
│      // 创建 CreateActivityData                                         │
│      CreateActivityData data = new CreateActivityData();                │
│      data.token = token;                                               │
│      data.info = info;                                                 │
│      ...                                                                │
│                                                                         │
│      // 发送到主线程 Handler                                           │
│      sendMessage(H.EXECUTE_TRANSACTION, transaction);                    │
│  }                                                                      │
│                                                                         │
│  // 3. scheduleResumeActivity - 恢复 Activity                         │
│  public void scheduleResumeActivity(IBinder token, int procState,       │
│      boolean isForward, Bundle resumeArgs) {                            │
│                                                                         │
│      // 发送到主线程 Handler                                           │
│      sendMessage(H.EXECUTE_TRANSACTION, transaction);                    │
│  }                                                                      │
│                                                                         │
│  // 4. schedulePauseActivity - 暂停 Activity                          │
│  public void schedulePauseActivity(IBinder token, boolean finished,       │
│      boolean userLeaving, int configChanges, boolean deferResume) {      │
│                                                                         │
│      sendMessage(H.EXECUTE_TRANSACTION, transaction);                    │
│  }                                                                      │
│                                                                         │
│  // 5. scheduleDestroyActivity - 销毁 Activity                        │
│  public void scheduleDestroyActivity(IBinder token, boolean finishing,    │
│      int configChanges, boolean getnonConfigInstance) {                  │
│                                                                         │
│      sendMessage(H.EXECUTE_TRANSACTION, transaction);                    │
│  }                                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    ApplicationThread 消息处理                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ApplicationThread 通过 sendMessage() 发送消息到 ActivityThread.H          │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  ActivityThread.H (主线程 Handler)                              │  │
│  │                                                                 │  │
│  │  public void handleMessage(Message msg) {                      │  │
│  │      switch (msg.what) {                                      │  │
│  │          case BIND_APPLICATION:                                │  │
│  │              handleBindApplication((AppBindData)msg.obj);      │  │
│  │              break;                                           │  │
│  │                                                                 │  │
│  │          case EXECUTE_TRANSACTION:                            │  │
│  │              handleMessage((Transaction)msg.obj);              │  │
│  │              break;                                           │  │
│  │                                                                 │  │
│  │          case EXIT_APPLICATION:                                │  │
│  │              handleExitApplication();                          │  │
│  │              break;                                           │  │
│  │      }                                                        │  │
│  │  }                                                            │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Transaction 包含:                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  - CREATE_ACTIVITY         - 创建 Activity                     │  │
│  │  - PAUSE_ACTIVITY         - 暂停 Activity                    │  │
│  │  - RESUME_ACTIVITY        - 恢复 Activity                     │  │
│  │  - DESTROY_ACTIVITY      - 销毁 Activity                     │  │
│  │  - STOP_ACTIVITY_HIDE    - 停止 Activity                     │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    完整通信流程: ATMS → ApplicationThread → ActivityThread │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  System Server 进程                                             │   │
│  │  ┌────────────────────────────────────────────────────────────┐  │   │
│  │  │ ATMS.realStartActivityLocked()                           │  │   │
│  │  │     │                                                    │  │   │
│  │  │     │  Binder Call                                       │  │   │
│  │  │     ▼                                                    │  │   │
│  │  │  client.scheduleCreateActivity()                        │  │   │
│  │  └────────────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────┬────────────────────────────────────┘   │
│                               │                                        │
│                               │ Binder IPC                              │
│                               ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  应用进程                                                      │   │
│  │  ┌────────────────────────────────────────────────────────────┐  │   │
│  │  │ ApplicationThread.scheduleCreateActivity()               │  │   │
│  │  │     │                                                    │  │   │
│  │  │     │  sendMessage(H.EXECUTE_TRANSACTION, transaction)  │  │   │
│  │  │     ▼                                                    │  │   │
│  │  │  ActivityThread.H (Handler)                              │  │   │
│  │  │     │                                                    │  │   │
│  │  │     │  handleMessage()                                  │  │   │
│  │  │     ▼                                                    │  │   │
│  │  │  TransactionExecutor.execute()                          │  │   │
│  │  │     │                                                    │  │   │
│  │  │     ▼                                                    │  │   │
│  │  │  ActivityTransaction.traverse()                         │  │   │
│  │  │     │                                                    │  │   │
│  │  │     ▼                                                    │  │   │
│  │  │  ActivityThread.performCreateActivity()                 │  │   │
│  │  │     │                                                    │  │   │
│  │  │     │  1. ClassLoader 加载类                           │  │   │
│  │  │     │  2. 创建 Activity 实例                            │  │   │
│  │  │     │  3. 创建 Context                                 │  │   │
│  │  │     │  4. activity.attach()                           │  │   │
│  │  │     │  5. activity.onCreate()                          │  │   │
│  │  │     ▼                                                    │  │   │
│  │  │  完成！                                                   │  │   │
│  │  └────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.7 ApplicationThread 与 ActivityThread.H 交互

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                ApplicationThread → ActivityThread.H 消息流程                    │
└─────────────────────────────────────────────────────────────────────────────┘

1. ATMS 调用 (System Server)
       │
       ▼
2. ApplicationThread.scheduleXXXActivity() (应用进程 Binder 线程池)
       │  ┌─────────────────────────────────────────────┐
       └──►│ Binder 线程池接收请求                   │
            │ - Binder#onTransact()                   │
            │ - 调用 scheduleXXXActivity()           │
            └────────────────┬────────────────────────┘
                             │
                             ▼
3. ApplicationThread.sendMessage()
       │  ┌─────────────────────────────────────────────┐
       │  │ ActivityThread.H 发送消息                  │
       │  │ mH.sendMessage(msg)                       │
       │  │ - 切换到主线程                            │
       │  └────────────────┬────────────────────────┘
       ▼
4. ActivityThread.H.handleMessage()
       │  ┌─────────────────────────────────────────────┐
       │  │ 主线程处理消息                             │
       │  │ switch (msg.what) {                      │
       │  │   case EXECUTE_TRANSACTION:              │
       │  │     ...                                   │
       │  │ }                                         │
       │  └────────────────┬────────────────────────┘
       ▼
5. TransactionExecutor.execute()
       │  ┌─────────────────────────────────────────────┐
       │  │ 执行事务                                 │
       │  │ - 解析 Transaction                       │
       │  │ - 调用对应 Handler 方法                  │
       │  └────────────────┬────────────────────────┘
       ▼
6. 最终调用 Activity 方法
       │
       ├──► onCreate()
       ├──► onStart()
       ├──► onResume()
       ├──► onPause()
       ├──► onStop()
       └──► onDestroy()
```

### 3.8 关键时序图：ApplicationThread 生命周期回调

```
ATMS          ApplicationThread      ActivityThread.H     Activity
  │                   │                     │                  │
  │                   │                     │                  │
  │◄──── Binder ──────│                     │                  │
  │   scheduleCreate  │                     │                  │
  │                   │                     │                  │
  │                   │◄── sendMessage ──►│                  │
  │                   │                     │                  │
  │                   │                     │◄─ handleMessage│
  │                   │                     │                  │
  │                   │                     │◄─ execute()    │
  │                   │                     │                  │
  │                   │                     │◄─ performLaunch│
  │                   │                     │                  │
  │                   │                     │◄─ onCreate()  │
  │                   │                     │                  │
  │◄──── Binder ──────│                     │                  │
  │   scheduleResume  │                     │                  │
  │                   │                     │                  │
  │                   │◄── sendMessage ──►│                  │
  │                   │                     │                  │
  │                   │                     │◄─ handleMessage│
  │                   │                     │                  │
  │                   │                     │◄─ performResume│
  │                   │                     │                  │
  │                   │                     │◄─ onResume()   │
  │                   │                     │                  │
  ▼                   ▼                     ▼                  ▼
 完成                完成                   完成               运行中
```
   └────────────────────────────────────────────────────────────────┘
```

### 3.6 ViewRootImpl 衔接流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 Activity 与 ViewRootImpl 衔接流程                            │
└─────────────────────────────────────────────────────────────────────────────┘

Activity.onCreate()
       │
       ▼
setContentView(layoutResID)
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  DecorView 创建                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │ 1. PhoneWindow.setContentView()               │  │
│  │ 2. installDecor()                             │  │
│  │ 3. mContentParent = generateLayout()          │  │
│  │ 4. 返回 DecorView (包含 TitleBar + Content)   │  │
│  └─────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
Activity.onStart()
       │
                       ▼
Activity.onResume()
       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  ViewRootImpl 关联                                    │
│  ┌─────────────────────────────────────────────────┐  │
│  │ 1. activity.attach(app, ...)                   │  │
│  │    - 创建 PhoneWindow                          │  │
│  │    - 设置 WindowManager                        │  │
│  │                                               │  │
│  │ 2. windowManager.addView(view, params)        │  │
│  │    - 获取 WindowManagerGlobal                 │  │
│  │    - 调用 addView()                           │  │
│  │                                               │  │
│  │ 3. WindowManagerGlobal.addView()              │  │
│  │    - 创建 ViewRootImpl                        │  │
│  │    - 调用 root.setView()                     │  │
│  │                                               │  │
│  │ 4. ViewRootImpl.setView()                    │  │
│  │    - 保存 DecorView 到 mView                 │  │
│  │    - 请求布局 (scheduleTraversals())         │  │
│  └─────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
ViewRootImpl.performTraversals()
       │
       ├──► measure()  → onMeasure()  → setMeasuredDimension()
       │
       ├──► layout()   → onLayout()   → setFrame()
       │
       └──► draw()     → onDraw()     → drawCanvas()

       │
       ▼
    屏幕显示

┌─────────────────────────────────────────────────────────────────────────────┐
│                    ViewRootImpl 核心代码流程                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  // ActivityThread.handleResumeActivity()                               │
│  r.activity.makeVisible();                                              │
│                                                                         │
│  // Activity.makeVisible()                                              │
│  if (mWindowAdded) {                                                  │
│      mWindowManager.addView(mDecor, mWindowAttributes);                │
│  }                                                                     │
│                                                                         │
│  // WindowManagerGlobal.addView()                                      │
│  ViewRootImpl root = new ViewRootImpl(view.getContext(), display);    │
│  root.setView(view, wparams, panelParentView);                        │
│                                                                         │
│  // ViewRootImpl.setView()                                            │
│  public void setView(View view, WindowManager.LayoutParams attrs,       │
│                      View panelParentView) {                            │
│      mView = view;                                                    │
│      // 请求首次布局                                                    │
│      requestLayout();                                                  │
│  }                                                                     │
│                                                                         │
│  // ViewRootImpl.requestLayout()                                       │
│  public void requestLayout() {                                         │
│      scheduleTraversals();                                             │
│  }                                                                     │
│                                                                         │
│  // ViewRootImpl.scheduleTraversals()                                 │
│  void scheduleTraversals() {                                           │
│      mChoreographer.postCallback(                                      │
│          Choreographer.CALLBACK_TRAVERSAL,                            │
│          mTraversalRunnable,                                           │
│          null);                                                       │
│  }                                                                     │
│                                                                         │
│  // Choreographer 等待 VSync 信号后执行                                │
│  final TraversalRunnable mTraversalRunnable = new TraversalRunnable(); │
│                                                                         │
│  void doTraversal() {                                                  │
│      performTraversals();                                             │
│  }                                                                     │
│                                                                         │
│  void performTraversals() {                                           │
│      // 完整的 measure → layout → draw 流程                          │
│      performMeasure();                                                │
│      performLayout();                                                  │
│      performDraw();                                                   │
│  }                                                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.7 完整时序图 (AMS → AT → ViewRootImpl)

```
User    Activity   Instrumentation   ATMS      Stack   Zygote   AT       ViewRootImpl
 │         │            │              │          │        │        │           │
 │startActivity()     │              │          │        │        │           │
 │────────►│          │              │        │           │          │        │
 │         │execStartActivity()     │          │        │        │           │
 │         │──────────►│            │          │        │        │           │
 │         │           │startActivity()         │        │        │           │
 │         │           │─────────────►│         │        │        │           │
 │         │           │              │execute()│        │        │           │
 │         │           │              │───────►│         │        │           │
 │         │           │              │         │startProcess()        │
 │         │           │              │─────────►│        │        │           │
 │         │           │              │         │        │fork()   │           │
 │         │           │              │         │        │────►│   │           │
 │         │           │              │         │        │     │   │           │
 │         │           │              │         │        │  new proc   │
 │         │           │              │         │        │◄────│   │           │
 │         │           │              │         │        │     │   │           │
 │         │           │attachApplication(appThread)    │        │           │
 │         │           │◄─────────────│         │        │        │           │
 │         │           │              │         │        │        │           │
 │         │           │scheduleCreateActivity()        │        │           │
 │         │           │◄─────────────│         │        │        │           │
 │         │           │              │         │        │        │           │
 │         │handleCreateActivity()    │         │        │        │           │
 │         │◄─────────│              │         │        │        │           │
 │         │           │              │         │        │        │           │
 │         │performLaunchActivity()  │         │        │        │           │
 │         │──────►│                 │         │        │        │           │
 │         │        │onCreate()      │         │        │        │           │
 │◄────────│        │                 │         │        │        │           │
 │         │        │                 │         │        │        │           │
 │         │        │onStart()       │         │        │        │           │
 │◄────────│        │                 │         │        │        │           │
 │         │        │                 │         │        │        │           │
 │         │        │onResume()      │         │        │        │           │
 │◄────────│        │                 │         │        │        │           │
 │         │        │makeVisible()   │         │        │        │           │
 │         │        │──────►│        │         │        │        │           │
 │         │        │              │         │        │        │ addView() │
 │         │        │              │         │        │        │──────►│   │
 │         │        │              │         │        │        │        │   │
 │         │        │              │         │        │        │ ViewRootImpl
 │         │        │              │         │        │        │  .setView()
 │         │        │              │         │        │        │──────►│   │
 │         │        │              │         │        │        │        │   │
 │         │        │              │         │        │        │ scheduleTraversals()
 │         │        │              │         │        │        │──────►│   │
 │         │        │              │         │        │        │        │   │
 │         │        │              │         │        │        │ performTraversals()
 │         │        │              │         │        │        │◄─────│   │
 │         │        │              │         │        │        │        │   │
 │         │        │              │         │        │        │measure()│   │
 │         │        │              │         │        │        │──────►│   │
 │         │        │              │         │        │        │        │   │
 │         │        │              │         │        │        │layout() │   │
 │         │        │              │         │        │        │──────►│   │
 │         │        │              │         │        │        │        │   │
 │         │        │              │         │        │        │draw()  │   │
 │         │        │              │         │        │        │──────►│   │
 │         │        │              │         │        │        │        │   │
 ▼         ▼           ▼              ▼          ▼        ▼        ▼           ▼
   显示完成   完成           完成         完成      完成     完成      完成       完成
```

### 3.2 详细步骤

#### Step 1: 调用 startActivity()

```java
// 在 Activity 中
startActivity(new Intent(this, TargetActivity.class));

// 实际调用
public void startActivity(Intent intent) {
    startActivityForResult(intent, -1);
}
```

#### Step 2: Instrumentation 处理

```java
// Instrumentation.java
public ActivityResult execStartActivity(
    Context who, IBinder contextThread, IBinder token, Activity target,
    Intent intent, int requestCode, Bundle options) {
    
    // 检查 intent
    checkStartActivityResult(intent, who);
    
    // 通过 Binder 通知系统服务
    int result = ActivityTaskManager.getService()
        .startActivity(whoThread, who.getBasePackageName(), intent,
                intent.resolveTypeIfNeeded(who.getContentResolver()),
                token, target != null ? target.mEmbeddedID : null,
                requestCode, 0, null, options);
    
    checkStartActivityResult(result, intent);
    return null;
}
```

#### Step 3: ActivityTaskManagerService (ATMS) 处理

```java
// ActivityTaskManagerService.java
public final int startActivity(IApplicationThread caller, String callingPackage,
        Intent intent, String resolvedType, IBinder resultTo, String resultWho,
        int requestCode, int startFlags, ProfilerInfo profilerInfo,
        Bundle bOptions) {
    
    return startActivityAsUser(caller, callingPackage, intent, resolvedType,
            resultTo, resultWho, requestCode, startFlags, profilerInfo, bOptions,
            UserHandle.getCallingUserId());
}
```

#### Step 4: ActivityStarter 执行启动

```java
// ActivityStarter.java
int execute() {
    // 1. 解析 Intent
    // 2. 检查权限
    // 3. 查找或创建 Activity 记录
    // 4. 决定启动模式
    // 5. 调用 ActivityStackSupervisor 启动
}
```

#### Step 5: ActivityStackSupervisor 调度

```java
// ActivityStackSupervisor.java
boolean startActivityUnchecked(ActivityRecord r, ActivityRecord sourceRecord,
        IVoiceInteractionSession voiceSession, int startFlags, boolean checkedOptions,
        Bundle checkedOptions, boolean inTask, boolean keepCurTrans, boolean briefSnapshot) {
    
    // 1. 决定 Activity 所属的 Task
    // 2. 处理 launch mode (standard, singleTop, singleTask, singleInstance)
    // 3. 处理 intent flags (FLAG_ACTIVITY_NEW_TASK, etc.)
    // 4. 调用 ActivityStack.startActivityLocked()
}
```

#### Step 6: ActivityStack 管理

```java
// ActivityStack.java
void startActivityLocked(ActivityRecord r, boolean newTask, boolean keepCurTrans,
        boolean briefSnapshot) {
    
    // 1. 将 ActivityRecord 加入栈
    // 2. 处理 Activity 的切换动画
    // 3. 调用 resumeTopActivityInnerLocked()
}
```

#### Step 7: 创建 Application（如果需要）

```java
// ActivityThread.java
private void handleBindApplication(AppBindData data) {
    
    // 1. 创建 Application 对象
    Application app = data.info.makeApplication(data.restrictedBackupMode, null);
    
    // 2. 调用 Application.onCreate()
    if (mInstrumentation != null) {
        mInstrumentation.callApplicationOnCreate(app);
    }
}
```

#### Step 8: 创建 Activity 实例

```java
// ActivityThread.java
private Activity performLaunchActivity(ActivityClientRecord r, Intent customIntent) {
    
    // 1. 从 ActivityRecord 获取 ComponentName
    ComponentName component = r.intent.getComponent();
    
    // 2. 通过 ClassLoader 加载 Activity 类
    ClassLoader cl = r.packageInfo.getClassLoader();
    Activity activity = (Activity) cl.loadClass(component.getClassName()).newInstance();
    
    // 3. 创建 Context
    Context appContext = createBaseContextForActivity(r, activity);
    
    // 4. 初始化 Activity
    activity.attach(appContext, this, r.token, r.ident, r.application,
            r.intent, r.activityInfo, r.title, r.parent, r.embeddedID,
            r.overrideConfig, r.voiceSession, r.AssistContext, r.launchMode);
    
    // 5. 调用 onCreate()
    if (r.state != null) {
        r.state.setClassLoader(cl);
        activity.restoreState(r.state);
    }
    
    activity.mCalled = false;
    if (r.isPersistable()) {
        mInstrumentation.callActivityOnCreate(activity, r.state, r.persistentState);
    } else {
        mInstrumentation.callActivityOnCreate(activity, r.state);
    }
    
    // 6. 设置 Window
    activity.mWindow = PolicyManager.makeNewWindow(activity);
    
    return activity;
}
```

#### Step 9: 创建 Window 和 View

```java
// Activity.java
final void attach(...) {
    // 1. 创建 PhoneWindow
    mWindow = new PhoneWindow(this, windowActivityController);
    
    // 2. 设置 WindowManager
    mWindow.setWindowManager(
            (WindowManager)context.getSystemService(Context.WINDOW_SERVICE),
            mToken, mComponent.flattenToString(), (info.flags & ActivityInfo.FLAG_HARDWARE_ACCELERATED) != 0);
    
    // 3. 设置 ContentView
    setContentView(layoutResID);
}
```

#### Step 10: View 的绘制流程

```
onCreate()
    │
    ▼
onStart()
    │
    ▼
onResume()
    │
    ▼
ViewRootImpl.performTraversals()
    │
    ├──► measure()  ──► onMeasure()
    │
    ├──► layout()   ──► onLayout()
    │
    └──► draw()     ──► onDraw()
```

---

## 4. 核心组件交互

### 4.1 Binder 通信

```
App Process                              System Server
┌────────────────────┐                ┌────────────────────┐
│  ApplicationThread │◄──────────────►│ ActivityTaskManager │
│  (Client)          │    Binder IPC   │ Service (Server)    │
└────────────────────┘                └────────────────────┘
```

### 4.2 关键 AIDL 接口

- `IActivityTaskManager` - Activity 管理服务
- `IApplicationThread` - 应用线程回调
- `IWindowSession` - Window 会话管理

---

## 5. 生命周期回调

### 5.1 完整生命周期

```
onCreate()
    │
    ▼
onStart()─────────────► Activity 可见
    │                        │
    ▼                        │
onResume()────────────► Activity 可交互
    │                        │
    │                        ▼
    │◄─────────────── 用户离开 Activity
    │                        │
    │                        ▼
onPause()─────────────► Activity 可见但不可交互
    │                        │
    ▼                        │
onStop()──────────────► Activity 不可见
    │                        │
    │  重新进入              ▼
    └───────────────► onRestart() ──► onStart()
    │
    ▼
onDestroy()──────────► Activity 销毁
```

### 5.2 启动过程生命周期

```
启动新 Activity:
MainActivity.onPause() 
    │
    ▼
TargetActivity.onCreate()
    │
    ▼
TargetActivity.onStart()
    │
    ▼
TargetActivity.onResume()
    │
    ▼
MainActivity.onStop() (如果不可见)
```

---

## 6. 常见问题与优化

### 6.1 启动优化建议

1. **减少 onCreate() 工作量**
   - 使用延迟加载
   - 异步初始化
   
2. **优化布局层级**
   - 使用 ConstraintLayout
   - 减少嵌套

3. **使用 ViewStub**
   - 延迟加载不常用的 View

4. **避免 I/O 操作在主线程**
   - 使用 AsyncTask / Handler / Coroutines

### 6.2 启动模式详解

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `standard` | 每次创建新实例 | 默认模式 |
| `singleTop` | 如果栈顶是该 Activity，复用并调用 onNewIntent | 通知、消息 |
| `singleTask` | 栈内唯一，复用并清除其上所有 Activity | 主界面 |
| `singleInstance` | 独占一个任务栈 | 独立功能 |

### 6.3 Intent Flags 常用组合

```java
// 启动新任务
intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

// 清除栈
intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);

// 重新排序
intent.setFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
```

---

## 7. 总结

Activity 启动流程是 Android 系统中最核心的机制之一，涉及多个进程、多个系统服务的协作。理解这一流程有助于：

1. **调试问题** - 解决启动黑屏、ANR 等问题
2. **性能优化** - 提升应用启动速度
3. **架构设计** - 更好地设计组件间交互
4. **深度理解 Android 系统**

---

## 参考资料

- Android Open Source Project (AOSP)
- Android Developer Documentation
- 《Android Internals》

---

*本文档由 OpenClaw 自动生成*
