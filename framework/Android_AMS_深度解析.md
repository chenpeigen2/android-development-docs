# Android AMS 深度解析

> 作者：OpenClaw | 日期：2026-03-12  
> 基于源码：AOSP Android 17 / API 37，固定 tag `android-17.0.0_r1`；复核日期：2026-09-10。

## 目录

- [1. 概述](#1-概述)
  - [1.1 AMS 的核心职责](#11-ams-的核心职责)
  - [1.2 ATMS 的核心职责 (Android 10+)](#12-atms-的核心职责-android-10)
- [2. AMS 架构总览](#2-ams-架构总览)
  - [2.1 系统服务架构](#21-系统服务架构)
  - [2.2 AMS 内部架构](#22-ams-内部架构)
  - [2.3 核心数据结构](#23-核心数据结构)
- [3. AMS 与 ATMS 职责划分](#3-ams-与-atms-职责划分)
  - [3.1 重构背景](#31-重构背景)
  - [3.2 职责对比表](#32-职责对比表)
  - [3.3 ATMS 架构](#33-atms-架构)
  - [3.4 核心类关系](#34-核心类关系)
- [4. Task、TaskFragment 与 ActivityRecord](#4-tasktaskfragment-与-activityrecord)
  - [4.1 栈结构总览](#41-栈结构总览)
  - [4.2 Task 与 Activity 关系](#42-task-与-activity-关系)
  - [4.3 Root Task 的窗口模式与 Activity 类型](#43-root-task-的窗口模式与-activity-类型)
  - [4.4 Activity 状态](#44-activity-状态)
- [5. 进程优先级 (oom_adj) 机制](#5-进程优先级-oom_adj-机制)
  - [5.1 oom_adj 等级](#51-oom_adj-等级)
  - [5.2 进程状态 (ProcessState)](#52-进程状态-processstate)
  - [5.3 oom_adj 调整流程](#53-oom_adj-调整流程)
  - [5.4 查看 oom_adj 命令](#54-查看-oom_adj-命令)
- [6. LaunchMode 深度解析](#6-launchmode-深度解析)
  - [6.1 启动模式](#61-启动模式)
  - [6.2 Intent Flags](#62-intent-flags)
  - [6.3 LaunchMode 与 Flags 组合](#63-launchmode-与-flags-组合)
  - [6.4 taskAffinity 属性](#64-taskaffinity-属性)
- [7. Activity 生命周期调度](#7-activity-生命周期调度)
  - [7.1 生命周期总览](#71-生命周期总览)
  - [7.2 生命周期调度源码](#72-生命周期调度源码)
  - [7.3 生命周期与系统状态](#73-生命周期与系统状态)
- [8. 进程启动流程](#8-进程启动流程)
  - [8.1 进程启动完整流程](#81-进程启动完整流程)
  - [8.2 Zygote Fork 流程](#82-zygote-fork-流程)
  - [8.3 ActivityThread.main()](#83-activitythreadmain)
- [9. 源码路径](#9-源码路径)
  - [9.1 AMS 相关源码](#91-ams-相关源码)
  - [9.2 ATMS 相关源码](#92-atms-相关源码)
  - [9.3 客户端源码](#93-客户端源码)
  - [9.4 在线源码](#94-在线源码)
- [10. 面试常见问题](#10-面试常见问题)
  - [10.1 基础问题](#101-基础问题)
  - [10.2 进阶问题](#102-进阶问题)
  - [10.3 高级问题](#103-高级问题)
- [总结](#总结)

---

## 1. 概述

**ActivityManagerService (AMS)** 是 Android 系统的核心服务之一，负责管理应用的四大组件（Activity、Service、BroadcastReceiver、ContentProvider）以及进程的生命周期。

从 Android 10 (API 29) 开始，Google 对 AMS 进行了重大重构，将 Activity 相关的管理职责拆分到了 **ActivityTaskManagerService (ATMS)**，AMS 专注于进程管理、Service 和 ContentProvider 管理。

### 1.1 AMS 的核心职责

```text
┌─────────────────────────────────────────────────────────────────┐
│                    AMS 核心职责                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  1. 进程管理 (Process Management)                        │  │
│  │     • 进程启动与销毁                                     │  │
│  │     • 进程优先级 (oom_adj) 调整                          │  │
│  │     • 低内存杀进程 (LMK)                                 │  │
│  │     • 进程状态监控                                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  2. Service 管理                                         │  │
│  │     • startService / bindService                        │  │
│  │     • 前台服务                                           │  │
│  │     • 服务生命周期                                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  3. BroadcastReceiver 管理                              │  │
│  │     • 动态/静态注册                                      │  │
│  │     • 有序/粘性广播                                      │  │
│  │     • 广播分发队列                                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  4. ContentProvider 管理                                 │  │
│  │     • Provider 发布                                      │  │
│  │     • Provider 获取                                      │  │
│  │     • 权限检查                                           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  5. 权限管理 (Permission)                                │  │
│  │     • 运行时权限检查                                     │  │
│  │     • URI 权限授予                                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 ATMS 的核心职责 (Android 10+)

```text
┌─────────────────────────────────────────────────────────────────┐
│                    ATMS 核心职责                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  1. Activity 管理                                        │  │
│  │     • startActivity / finishActivity                    │  │
│  │     • Activity 栈管理                                    │  │
│  │     • Task 管理                                          │  │
│  │     • LaunchMode 处理                                    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  2. 窗口管理协调                                         │  │
│  │     • 与 WMS 交互                                        │  │
│  │     • 转场动画                                           │  │
│  │     • 最近任务列表                                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  3. 生命周期管理                                         │  │
│  │     • onPause / onResume / onStop / onDestroy           │  │
│  │     • Activity 状态转换                                  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. AMS 架构总览

### 2.1 系统服务架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Android 系统服务架构                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    System Server (系统服务进程)                      │ │
│   │                                                                      │ │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│   │   │     AMS      │  │     ATMS     │  │     WMS      │            │ │
│   │   │  Activity    │  │  Activity    │  │   Window     │            │ │
│   │   │  Manager     │  │  Task        │  │   Manager    │            │ │
│   │   │  Service     │  │  Manager     │  │   Service    │            │ │
│   │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │ │
│   │          │                 │                 │                      │ │
│   │          │    Binder IPC   │                 │                      │ │
│   │          │                 │                 │                      │ │
│   │   ┌──────▼─────────────────▼─────────────────▼───────┐            │ │
│   │   │                应用进程 (App Process)              │            │ │
│   │   │                                                      │            │ │
│   │   │  ┌──────────────┐  ┌──────────────┐              │            │ │
│   │   │  │ActivityThread│  │   Context    │              │            │ │
│   │   │  │  (主线程)    │  │   (上下文)   │              │            │ │
│   │   │  └──────────────┘  └──────────────┘              │            │ │
│   │   │                                                      │            │ │
│   │   └──────────────────────────────────────────────────┘            │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 AMS 内部架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AMS 内部架构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    ActivityManagerService                            │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                  核心组件                                     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │ProcessRecord │  │ ServiceRecord│  │ContentProvider│     │ │ │
│   │   │   │  (进程记录)  │  │  (服务记录)  │  │Record(提供者) │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │BroadcastQueue│  │ProviderMap   │  │PendingIntent │     │ │ │
│   │   │   │  (广播队列)  │  │ (提供者映射) │  │ (待定意图)   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                  辅助组件                                     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │OomAdjuster   │  │BatteryStats  │  │AppOpsService │     │ │ │
│   │   │   │(OOM 调整器)  │  │ (电池统计)   │  │ (应用操作)   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │UserController│  │ProcessList   │  │ActiveServices│     │ │ │
│   │   │   │ (用户控制器) │  │ (进程列表)   │  │ (服务管理)   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 核心数据结构

记录类描述服务端状态，不是应用组件实例，也不是早期版本一组 public 字段的简单集合。

```text
ProcessRecord extends ProcessRecordInternal
  getPid() / uid / processName：进程身份
  ProcessServiceRecord：Service 与绑定连接
  ProcessProviderRecord：Provider 发布/使用关系
  ProcessErrorStateRecord：crash / ANR 等错误状态
  WindowProcessController：与 ATMS 的进程级桥接
  am/psc 的内部记录与控制器：进程状态、adj、依赖传播
ServiceRecord：Service 实例标识、启动请求、绑定、前台状态等
ContentProviderRecord：Provider 标识、发布端、连接与外部引用等
```

uid 是 Linux UID（编码 Android 用户与 appId），不是单独的 Android 用户 ID。当前 ProcessRecord 不含旧 `activities`、`curAdj` 等直接字段；服务状态和 Provider 引用也不能用错误的 `int startRequested`、`ArrayMap<IBinder,Integer>` 伪造源码。应由记录的访问方法和职责子记录理解状态边界，而不是将历史字段机械移动。

源码：[ProcessRecord.java:91](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ProcessRecord.java#91)；[ServiceRecord.java:88](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ServiceRecord.java#88)；[ContentProviderRecord.java:46](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ContentProviderRecord.java#46)。

## 3. AMS 与 ATMS 职责划分

### 3.1 重构背景

从 Android 10 (API 29) 开始，Google 将 AMS 中的 Activity 管理相关代码拆分到了 ATMS，主要原因是：

1. **代码解耦** - AMS 代码量过大，职责不清晰
2. **性能优化** - Activity 管理可以独立优化
3. **模块化** - 便于系统服务拆分和重构

### 3.2 职责对比表

| 功能 | Android 9 (API 28) | Android 10+ (API 29+) |
|------|-------------------|---------------------|
| Activity 管理 | AMS | **ATMS** |
| Task/Stack 管理 | AMS | **ATMS** |
| 进程管理 | AMS | AMS |
| Service 管理 | AMS | AMS |
| BroadcastReceiver | AMS | AMS |
| ContentProvider | AMS | AMS |
| 权限检查 | AMS | AMS + ATMS |

### 3.3 ATMS 架构

```text
ActivityTaskManagerService
  ActivityStartController / ActivityStarter：请求解析、权限、任务选择与启动策略
  RootWindowContainer / DisplayContent / TaskDisplayArea：显示及容器树
  Task / TaskFragment / ActivityRecord：任务、嵌入片段与 Activity 状态
  ActivityTaskSupervisor：实际启动/恢复及进程连接后的调度
  WindowProcessController：ATMS 侧进程视图
  ClientLifecycleManager：客户端事务批处理与投递
  TaskOrganizerController / RecentTasks：组织器与最近任务
```

TaskOrganizer 是客户端组织器 API，服务端是 TaskOrganizerController；ActivityStack、TaskRecord 已不再是当前 wm 类。源码：[ActivityTaskManagerService.java:339](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskManagerService.java#339)。

### 3.4 核心类关系

```text
WindowContainer
  RootWindowContainer
    DisplayContent
      DisplayArea / TaskDisplayArea
        Task（root task，可嵌套 Task）
          TaskFragment（可选，嵌入 Activity 等）
            ActivityRecord extends WindowToken
              WindowState
```

Task 本身继承 TaskFragment；不是每个 Activity 都必须先有一个额外显式 TaskFragment。ActivityRecord 持有 WindowProcessController，与客户端 Activity 通过 token 和事务关联。Task 的 children 可以包含任务或 Activity/片段，不能用 `ArrayList<ActivityRecord> mActivities` 等旧结构代替整个层级。

源码：[Task.java:207](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/Task.java#207)；[TaskFragment.java:123](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/TaskFragment.java#123)；[ActivityRecord.java:372](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityRecord.java#372)。

## 4. Task、TaskFragment 与 ActivityRecord

### 4.1 栈结构总览

```text
RootWindowContainer
  DisplayContent（某逻辑显示）
    TaskDisplayArea
      Home root Task（ACTIVITY_TYPE_HOME）
        Launcher ActivityRecord
      普通 root Task / 应用 Task
        ActivityRecord A
        ActivityRecord B
      另一个 Task（可处于 freeform / pinned 等模式）
        ActivityRecord C
```

Home 任务不是收纳微信和支付宝等普通应用任务的固定“Launcher 栈”。任务的父容器、windowingMode 与 activityType 一起决定组织方式；桌面、全屏、分屏和嵌入不能统一映射为历史固定 stackId。

源码：[Task.java:207](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/Task.java#207)。

### 4.2 Task 与 Activity 关系

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Task 与 Activity 关系                                │
└─────────────────────────────────────────────────────────────────────────────┘

Task (任务)
├── Activity 1 (根 Activity)
│   ├── 启动 Activity 2
│   │   ├── 启动 Activity 3
│   │   │   └── 返回 → Activity 2
│   │   └── 返回 → Activity 1
│   └── 返回 → 桌面
└── 特点：
    • 每个 Task 有唯一的 taskId
    • Task 内的 Activity 形成栈结构
    • 按 Back 键依次出栈
    • 可通过 Intent.FLAG_ACTIVITY_NEW_TASK 创建新 Task

示例：微信聊天流程
Task 1 (微信)
├── LauncherActivity (启动页)
├── MainActivity (主页)
├── ChatActivity (聊天)
└── ImagePreviewActivity (图片预览)

按 Back 键：
ImagePreviewActivity → ChatActivity → MainActivity → LauncherActivity → 桌面
```

### 4.3 Root Task 的窗口模式与 Activity 类型

`activityType` 表示 HOME、RECENTS、STANDARD 等角色；`windowingMode` 表示 FULLSCREEN、FREEFORM、PINNED、MULTI_WINDOW 等窗口模式，两者不是同一维度。

- HOME 用于桌面；Recents 可由相关组件实现，但不能断言所有 RecentsActivity 都在 HOME task。
- 全屏普通任务随用户/显示区/启动规则动态创建，不占用固定 `FULLSCREEN_WORKSPACE_STACK_ID=1`。
- 自由窗口由 Task 的窗口模式和 bounds 配合 Shell 组织，不是固定 stackId=2。
- PiP 使用 pinned Task，与 Shell PiP 和 transition 协作，不是固定 stackId=3。

源码：[Task.java:207](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/Task.java#207)；[ActivityStarter.java:2015](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#2015)。

### 4.4 Activity 状态

真实枚举为 ActivityRecord.State，不是 ActivityState；finishing 等布尔状态不能代替完整生命周期状态机。

```java
enum State {
    INITIALIZING,
    STARTED,
    RESUMED,
    PAUSING,
    PAUSED,
    STOPPING,
    STOPPED,
    FINISHING,
    DESTROYING,
    DESTROYED,
    RESTARTING_PROCESS
}
```

普通启动推进 INITIALIZING → STARTED → RESUMED；暂停/停止和销毁是条件分支。仅 PAUSED 返回时不需要 onRestart/onStart，STOPPED 返回才经过 restart/start；进程被杀时不保证收到 onDestroy。服务端状态和客户端回调跨进程异步协调，不应在回调时刻强行认定两侧状态完全一致。

源码：[ActivityRecord.java:553](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityRecord.java#553)。

## 5. 进程优先级 (oom_adj) 机制

### 5.1 oom_adj 等级

当前使用 oom_score_adj 尺度；旧 0..15 的 oom_adj 数字不能混入现代表。典型常量位于 `services/core/java/com/android/server/am/psc/Constants.java`：

| 常量 | 值 | 含义 |
|---|---:|---|
| NATIVE_ADJ / SYSTEM_ADJ | -1000 / -900 | native / system_server 等高保护等级 |
| PERSISTENT_PROC_ADJ / PERSISTENT_SERVICE_ADJ | -800 / -700 | 常驻及相关服务 |
| FOREGROUND_APP_ADJ | 0 | 前台基准 |
| VISIBLE_APP_ADJ | 100 | 可见基准 |
| PERCEPTIBLE_APP_ADJ | 200 | 可感知基准，另有 50/225/250 等细分 |
| BACKUP_APP_ADJ / HEAVY_WEIGHT_APP_ADJ | 300 / 400 | 备份/重型应用 |
| SERVICE_ADJ / HOME_APP_ADJ | 500 / 600 | 服务/桌面 |
| PREVIOUS_APP_ADJ / SERVICE_B_ADJ | 700 / 800 | 上一个应用/服务 B |
| CACHED_APP_MIN_ADJ..MAX_ADJ | 900..999 | 缓存区间 |

实际 adj 还受窗口层级、进程依赖、服务绑定、缓存排序和特性开关影响。它是回收保护度，不是 CPU 调度优先级，也不是“负值进程任何情况下永不被杀”。源码：[Constants.java:76](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/psc/Constants.java#76)。

### 5.2 进程状态 (ProcessState)

`PROCESS_STATE_*` 常量定义在 `android.app.ActivityManager`，并映射 ActivityManager.PROCESS_STATE_* / ProcessStateEnum 等状态，不应虚构为 ProcessList 的源码字段。

```text
TOP / BOUND_TOP：顶部 Activity 或依赖关系
FOREGROUND_SERVICE / BOUND_FOREGROUND_SERVICE：前台服务及绑定依赖
IMPORTANT_FOREGROUND / IMPORTANT_BACKGROUND：重要工作
BACKUP / SERVICE / RECEIVER：当前组件工作
HOME / LAST_ACTIVITY：桌面和上一个 Activity
CACHED_ACTIVITY / CACHED_ACTIVITY_CLIENT / CACHED_RECENT / CACHED_EMPTY：缓存状态
```

procState 表示进程的逻辑状态，adj 表示回收排序；调度组、capability 还是另外的输出。它们一起从整个进程及依赖图计算，没有一张固定的 procState→adj 一一映射表。

源码：[ActivityManager.java:800](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityManager.java#800)；[ProcessStateController.java:304](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/psc/ProcessStateController.java#304)。

### 5.3 oom_adj 调整流程

```text
Activity / Service / Provider / Broadcast 状态或依赖变化
 -> AMS / ATMS 更新进程可见性与组件状态
 -> am/psc/ProcessStateController.enqueueUpdateTarget / runUpdate 等
 -> OomAdjuster / OomAdjusterImpl：遍历可达依赖，计算 adj/procState/调度组等
 -> 应用结果、通知进程组/lmkd 等
 -> /proc/<pid>/oom_score_adj 与 dumpsys 中反映已应用状态
```

增量更新可只覆盖受影响依赖，不能简化成 `Activity.onResume -> computeOomAdj -> 直接写 oom_adj`。进程状态还在 ProcessRecordInternal 等内部记录维护。源码：[ProcessStateController.java:277](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/psc/ProcessStateController.java#277)；[OomAdjusterImpl.java:1218](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/psc/OomAdjusterImpl.java#1218)。

连续节选 [ProcessStateController.java:275–317](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/psc/ProcessStateController.java#275)（不是独立编译单元）：

```java
 */
@GuardedBy("mLock")
public void enqueueUpdateTarget(@Nullable ProcessRecordInternal proc) {
    if (mBatchSession != null && mBatchSession.isActive()) {
        // BatchSession is active and a process has been enqueued for an update.
        getBatchSession().maybeEnqueueProcess(proc);
        return;
    }
    enqueueUpdateTargetImpl(proc);
}

@GuardedBy("mLock")
private void enqueueUpdateTargetImpl(@Nullable ProcessRecordInternal proc) {
    mOomAdjuster.enqueueOomAdjTargetLocked(proc);
}

/**
 * Remove a process that was added by {@link #enqueueUpdateTarget}.
 */
@GuardedBy("mLock")
public void removeUpdateTarget(@NonNull ProcessRecordInternal proc, boolean procDied) {
    mOomAdjuster.removeOomAdjTargetLocked(proc, procDied);
}

/**
 * Trigger an update on a single process (and any processes that have been enqueued with
 * {@link #enqueueUpdateTarget}).
 */
@GuardedBy("mLock")
public boolean runUpdate(@NonNull ProcessRecordInternal proc, @OomAdjReason int oomAdjReason) {
    if (mBatchSession != null && mBatchSession.isActive()) {
        // BatchSession is active, just enqueue the proc for now. The update will happen
        // at the end of the session.
        enqueueUpdateTarget(proc);
        return false;
    }
    return runUpdateimpl(proc, oomAdjReason);
}

@GuardedBy("mLock")
private boolean runUpdateimpl(@NonNull ProcessRecordInternal proc,
        @OomAdjReason int oomAdjReason) {
    commitStagedEvents();
```

BatchSession 活跃时 runUpdate 只入队并返回 false，不代表计算失败；更新会在批次结束推进。非批次调用提交 staged events 后交给 OomAdjuster。这样能把同一组 Activity/服务依赖变化合并，避免观察半更新关系。

组件依赖的影响会传播到其他进程，所以“只把当前 app 的 adj 改一下”不能等价替换控制器。排查应记录触发原因、批次状态、受影响集合和最终已应用结果，不能凭某个 onPause 时间点推出目标 adj。

### 5.4 查看 oom_adj 命令

```bash
adb shell pidof com.example.app
adb shell cat /proc/12345/oom_score_adj  # 将 12345 替换成实际 PID，权限依设备而定
adb shell dumpsys activity processes
```

应同时读取 adj、procState、调度组、可见组件与绑定关系；不能仅凭单个采样值推出整个生命周期。旧 `/proc/pid/oom_adj` 是历史兼容尺度，不用其 9/15 数字解释现代 900..999。源码尺度见 5.1。


---

## 6. LaunchMode 深度解析

### 6.1 启动模式

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LaunchMode 常用模式                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   1. standard (标准模式) - 默认                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   • 每次启动都创建新实例                                             │ │
│   │   • 可以有多个相同 Activity 实例                                     │ │
│   │   • 普通无特殊 flags 时进入调用方任务；仍受 NEW_TASK 等规则影响                                            │ │
│   │   • 默认非单例模式                                                         │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   示例：                                                                    │
│   Task A: [A → B → C]                                                      │
│   从 C 启动 B (standard): [A → B → C → B]                                 │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   2. singleTop (栈顶单例)                                            │ │
│   │   • 如果目标 Activity 已在栈顶，不创建新实例                          │ │
│   │   • 调用 onNewIntent()                                              │ │
│   │   • 如果不在栈顶，行为同 standard                                    │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   示例：                                                                    │
│   Task A: [A → B → C]                                                      │
│   从 C 启动 C (singleTop): [A → B → C] → onNewIntent()                   │
│   从 C 启动 B (singleTop): [A → B → C → B] (B 不在栈顶)                  │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   3. singleTask (任务单例)                                           │ │
│   │   • 在系统任务复用、用户与显示规则下查找已有实例，不是跨所有用户的全局单例                                                 │ │
│   │   • 如果已存在，将其所在 Task 移到前台                                │ │
│   │   • 调用 onNewIntent()                                              │ │
│   │   • 其上方的 Activity 会被清除                                       │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   示例：                                                                    │
│   Task A: [A → B → C]                                                      │
│   Task B: [D → E → F]  (F 为 singleTask)                                  │
│                                                                             │
│   从 C 启动 F:                                                             │
│   Task A: [A → B → C] (后台)                                               │
│   Task B: [D → E → F] (前台) → onNewIntent()                             │
│                                                                             │
│   如果 Task B 中 F 上面有 G:                                               │
│   Task B: [D → E → F → G]                                                 │
│   启动 F 后: [D → E → F] (G 被清除) → onNewIntent()                      │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   4. singleInstance (全局单例)                                       │ │
│   │   • 在系统任务复用、用户与显示规则下查找已有实例，不是跨所有用户的全局单例                                                 │ │
│   │   • 独占一个 Task                                                    │ │
│   │   • Task 中只有这一个 Activity                                       │ │
│   │   • 调用 onNewIntent()                                              │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   示例：                                                                    │
│   Task A: [A → B]                                                          │
│   Task C: [C]  (C 为 singleInstance，独占 Task)                           │
│                                                                             │
│   从 B 启动 C:                                                             │
│   Task A: [A → B] (后台)                                                   │
│   Task C: [C] (前台) → onNewIntent()                                      │
│                                                                             │
│   从 C 启动 D (standard):                                                  │
│   Task A: [A → B] (后台)                                                   │
│   Task C: [C] (后台)                                                       │
│   Task D: [D]（示例；也可能复用已有合适任务）                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

`singleInstancePerTask`（API 31+）要求该实例作为任务根，但可按 NEW_DOCUMENT/MULTIPLE_TASK 等规则创建不同任务实例；它不等于 singleInstance 独占整个任务。源码：[ActivityStarter.java:2015](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#2015)。

### 6.2 Intent Flags

```java
/**
 * 常用 Intent Flags
 * 位置：frameworks/base/core/java/android/content/Intent.java
 */

// 1. FLAG_ACTIVITY_NEW_TASK
//    • 在新 Task 中启动 Activity
//    • 类似 singleTask，但不清除上方 Activity
intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

// 2. FLAG_ACTIVITY_SINGLE_TOP
//    • 同 singleTop
intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);

// 3. FLAG_ACTIVITY_CLEAR_TOP
//    • 如果 Activity 已存在，清除其上方的所有 Activity
//    • 如果同时设置 FLAG_ACTIVITY_SINGLE_TOP，调用 onNewIntent()
//    • 否则销毁重建
intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);

// 4. FLAG_ACTIVITY_CLEAR_TASK
//    • 启动前清除 Task 中的所有 Activity
//    • 必须与 FLAG_ACTIVITY_NEW_TASK 一起使用
intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);

// 5. FLAG_ACTIVITY_NO_HISTORY
//    • Activity 不会留在栈中
//    • 离开后自动销毁
intent.setFlags(Intent.FLAG_ACTIVITY_NO_HISTORY);

// 6. FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS
//    • 不出现在最近任务列表中
intent.setFlags(Intent.FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS);

// 7. FLAG_ACTIVITY_REORDER_TO_FRONT
//    • 如果 Activity 已存在，将其移到前台
//    • 不创建新实例
intent.setFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
```

### 6.3 LaunchMode 与 Flags 组合

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LaunchMode 与 Flags 组合效果                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   场景 1: 退出登录，回到登录页                                               │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   // 清除所有 Activity，回到登录页                                   │ │
│   │   Intent intent = new Intent(this, LoginActivity.class);           │ │
│   │   intent.setFlags(                                                  │ │
│   │       Intent.FLAG_ACTIVITY_NEW_TASK |                              │ │
│   │       Intent.FLAG_ACTIVITY_CLEAR_TASK                              │ │
│   │   );                                                               │ │
│   │   startActivity(intent);                                            │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   场景 2: 通知栏点击，打开指定页面                                           │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   // 单例模式，如果存在则复用                                        │ │
│   │   Intent intent = new Intent(this, MainActivity.class);            │ │
│   │   intent.setFlags(                                                  │ │
│   │       Intent.FLAG_ACTIVITY_NEW_TASK |                              │ │
│   │       Intent.FLAG_ACTIVITY_CLEAR_TOP |                             │ │
│   │       Intent.FLAG_ACTIVITY_SINGLE_TOP                              │ │
│   │   );                                                               │ │
│   │   startActivity(intent);                                            │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   场景 3: 从深层页面回到首页                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   // 清除上方所有 Activity                                           │ │
│   │   Intent intent = new Intent(this, HomeActivity.class);            │ │
│   │   intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);                 │ │
│   │   startActivity(intent);                                            │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.4 taskAffinity 属性

```xml
<!--
  taskAffinity - Task 亲和性
  位置：AndroidManifest.xml

  作用：指定 Activity 倾向于在哪个 Task 中
  默认值：应用的包名
-->

<!-- 示例 1: 不同应用使用相同 taskAffinity -->
<application
    android:taskAffinity="com.shared.task">
    
    <!-- 该应用的 Activity 会倾向于在同一 Task 中 -->
</application>

<!-- 示例 2: 单独 Activity 使用不同 taskAffinity -->
<activity
    android:name=".SpecialActivity"
    android:taskAffinity="com.special.task"
    android:launchMode="singleTask">
    
    <!-- 该 Activity 会在独立的 Task 中 -->
</activity>

<!--
  注意：
  1. 非空 affinity 通常采用包名形式；空字符串表示不与任何任务有亲和性
  2. 与 singleTask 或 FLAG_ACTIVITY_NEW_TASK 配合使用
  3. standard/singleTop 配合 NEW_TASK 或 reparenting 时仍可能使用 affinity
-->
```

---

## 7. Activity 生命周期调度

### 7.1 生命周期总览

```text
创建：onCreate -> onStart -> onResume
短暂失去 resumed 状态：onPause -> onResume（不经过 onRestart）
不可见后返回：onPause -> onStop -> onRestart -> onStart -> onResume
结束：onPause -> onStop -> onDestroy（进程终止时可能没有 onDestroy）
```

这是典型全屏序列；多窗口允许多个 resumed Activity，输入焦点与 top-resumed 另行管理。onRestart 是从已停止状态重新启动，不是 onStop 到 onDestroy 的必经步骤。

源码：[TransactionExecutor.java:72](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/TransactionExecutor.java#72)。

### 7.2 生命周期调度源码

真实启动调度使用事务项，不是 handleLaunchActivity 内无条件直接调用 handleResumeActivity：

```text
ActivityTaskSupervisor.realStartActivityLocked
 -> LaunchActivityItem + Resume/Pause/StopActivityItem
 -> ClientLifecycleManager.scheduleTransactionItems
 -> IApplicationThread.scheduleTransaction
 -> ClientTransactionHandler.scheduleTransaction -> H.EXECUTE_TRANSACTION
 -> TransactionExecutor
    LaunchActivityItem.execute -> handleLaunchActivity -> performLaunchActivity -> onCreate
    生命周期前置状态 -> handleStartActivity -> onStart
    ResumeActivityItem.execute -> handleResumeActivity -> onResume / 窗口可见性
    ResumeActivityItem.postExecute -> ActivityClient.activityResumed
      -> IActivityClientController -> ActivityClientController
```

performLaunchActivity 在 Activity.attach 内创建 PhoneWindow，调用 Instrumentation.newActivity / callActivityOnCreate；onStart 由生命周期状态机推进。bindApplication 通常先创建 Application 并安装 Provider，不应将 makeApplication 旧签名随意粘贴到这里。

服务端真实选择终态的摘录：

```java
// Set desired final state.
final ActivityLifecycleItem lifecycleItem;
if (andResume) {
    lifecycleItem = new ResumeActivityItem(r.token, isTransitionForward,
            r.shouldSendCompatFakeFocus());
} else if (r.isVisibleRequested()) {
    lifecycleItem = new PauseActivityItem(r.token);
} else {
    lifecycleItem = new StopActivityItem(r.token);
}
```

源码：[ActivityTaskSupervisor.java:809](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#809)；[ActivityThread.java:4733](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#4733)；[ResumeActivityItem.java:79](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/ResumeActivityItem.java#79)。

### 7.3 生命周期与系统状态

不能用 onCreate/onStart/onPause/onDestroy 建立固定 adj 对照表。同一进程可能同时拥有可见 Activity、前台服务、Provider 客户端和绑定服务，最终取保护约束与依赖传播后的结果。

- 一个 Activity onStop，不代表进程马上成为 cached；另一个可见 Activity 或活跃服务可能继续提高保护等级。
- 前台服务通常处于可感知相关等级，但绑定、类型、最近前台状态和超时规则会改变结果，不能写成固定 adj=3。
- 分屏中非焦点 Activity 可能仍是 resumed；焦点不是唯一可见性或回收保护依据。
- onDestroy 只结束一个实例；进程并不必然立刻进入 900..999 或退出。

源码：[OomAdjusterImpl.java:1218](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/psc/OomAdjusterImpl.java#1218)。

## 8. 进程启动流程

### 8.1 进程启动完整流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        进程启动完整流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

应用启动请求            AMS                     Zygote              应用进程
      │                 │                        │                     │
      ▼                 │                        │                     │
┌───────────┐          │                        │                     │
│startActivity│         │                        │                     │
└─────┬─────┘          │                        │                     │
      │                │                        │                     │
      │                │                        │                     │
      └───────┬────────┘                        │                     │
              │                                 │                     │
              ▼                                 │                     │
    ┌─────────────────┐                        │                     │
    │  ATMS           │                        │                     │
    │  .startActivity()│                       │                     │
    └────────┬────────┘                        │                     │
             │                                 │                     │
             ▼                                 │                     │
    ┌─────────────────┐                        │                     │
    │  检查进程是否存在│                        │                     │
    │                 │                        │                     │
    │  进程不存在 →   │                        │                     │
    └────────┬────────┘                        │                     │
             │                                 │                     │
             │                                 │                     │
             └──────────────┬──────────────────┘                     │
                            │                                        │
                            ▼                                        │
                ┌───────────────────────┐                           │
                │  AMS/ProcessList.startProcessLocked()  │                           │
                │                      │                           │
                │  1. 检查权限         │                           │
                │  2. 创建 ProcessRecord│                          │
                │  3. 调用 ProcessList │                           │
                └──────────┬────────────┘                           │
                           │                                        │
                           ▼                                        │
                ┌───────────────────────┐                           │
                │  ProcessList          │                           │
                │  .startProcessLocked()│                           │
                │                      │                           │
                │  1. 准备启动参数     │                           │
                │  2. 打开 Zygote Socket│                          │
                └──────────┬────────────┘                           │
                           │                                        │
                           │                                        │
                           └──────────────┬─────────────────────────┤
                                          │                         │
                                          ▼                         │
                             ┌───────────────────────┐              │
                             │  ZygoteProcess        │              │
                             │  .start()             │              │
                             │                      │              │
                             │  1. 连接 Zygote      │              │
                             │  2. 发送启动参数     │              │
                             │  3. 等待 fork 完成   │              │
                             └──────────┬────────────┘              │
                                        │                           │
                                        ▼                           │
                             ┌───────────────────────┐              │
                             │  Zygote（Java 协议处理 + native fork）      │              │
                             │                      │              │
                             │  1. 接收请求         │              │
                             │  2. fork 新进程      │              │
                             │  3. 返回 PID         │              │
                             └──────────┬────────────┘              │
                                        │                           │
                                        │ fork                      │
                                        └───────────────┬───────────┤
                                                        │           │
                                                        ▼           │
                                          ┌───────────────────────┐ │
                                          │  新进程 (Child)       │ │
                                          │                      │ │
                                          │  1. 初始化 Runtime   │ │
                                          │  2. 调用             │ │
                                          │     ActivityThread   │ │
                                          │     .main()          │ │
                                          └──────────┬────────────┘ │
                                                     │              │
                                                     ▼              │
                                          ┌───────────────────────┐ │
                                          │  ActivityThread       │ │
                                          │  .main()              │ │
                                          │                      │ │
                                          │  1. Looper.prepareMainLooper() │ │
                                          │  2. 创建实例         │ │
                                          │  3. attach()         │ │
                                          │  4. Looper.loop()    │ │
                                          └──────────┬────────────┘ │
                                                     │              │
                                                     │              │
                                                     └──────────────┤
                                                                    │
                                                                    ▼
                                                       ┌───────────────────────┐
                                                       │  应用进程启动完成    │
                                                       │  等待 AMS 的消息     │
                                                       └───────────────────────┘
```

### 8.2 Zygote Fork 流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Zygote Fork 流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   1. Zygote 启动 (系统启动时)                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   init 进程 → ZygoteInit.main()                                     │ │
│   │      │                                                              │ │
│   │      ├─► 预加载类和资源 (preloadClasses, preloadResources)          │ │
│   │      │                                                              │ │
│   │      ├─► 启动 SystemServer (forkSystemServer)                       │ │
│   │      │                                                              │ │
│   │      └─► 进入 Socket 监听循环 (runSelectLoop)                       │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   2. Fork 请求处理                                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   ZygoteServer.runSelectLoop()                                      │ │
│   │      │                                                              │ │
│   │      ├─► 监听 Zygote Socket                                         │ │
│   │      │                                                              │ │
│   │      ├─► 接收请求 → ZygoteConnection.processCommand()              │ │
│   │      │                                                              │ │
│   │      └─► forkAndSpecialize() → fork 新进程                         │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   3. Fork 后处理                                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   子进程 (新应用):                                                   │ │
│   │      │                                                              │ │
│   │      ├─► handleChildProc()                                          │ │
│   │      │                                                              │ │
│   │      ├─► 设置进程名 (setArgV0)                                      │ │
│   │      │                                                              │ │
│   │      ├─► 运行时初始化；Application 在回连 AMS 后由 bindApplication 创建                                    │ │
│   │      │                                                              │ │
│   │      └─► 调用 ActivityThread.main()                                 │ │
│   │                                                                     │ │
│   │   父进程 (Zygote):                                                   │ │
│   │      │                                                              │ │
│   │      └─► 返回子进程 PID 给 AMS                                      │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   4. 优势                                                                   │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   • 预加载共享类和资源，减少启动时间                                 │ │
│   │   • Copy-on-Write 机制，节省内存                                    │ │
│   │   • 统一的进程模板                                                   │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.3 ActivityThread.main()

```java
/**
 * ActivityThread 主入口
 * 位置：frameworks/base/core/java/android/app/ActivityThread.java
 */
public static void main(String[] args) {
    // 1. 初始化 Looper
    Looper.prepareMainLooper();
    
    // 2. 创建 ActivityThread 实例
    ActivityThread thread = new ActivityThread();
    thread.attach(false, startSeq);
    
    // 3. 获取 Handler
    if (sMainThreadHandler == null) {
        sMainThreadHandler = thread.getHandler();
    }
    
    // 4. 进入消息循环
    Looper.loop();
    
    // 5. 正常情况下不会执行到这里
    throw new RuntimeException("Main thread loop unexpectedly exited");
}

/**
 * attach 到 AMS
 */
private void attach(boolean system, long startSeq) {
    sCurrentActivityThread = this;
    mSystemThread = system;
    
    if (!system) {
        // 应用进程
        RuntimeInit.setApplicationObject(mAppThread.asBinder());
        
        // 1. 获取 AMS 代理
        final IActivityManager mgr = ActivityManager.getService();
        
        // 2. 注册 ApplicationThread
        try {
            mgr.attachApplication(mAppThread, startSeq);
        } catch (RemoteException ex) {
            throw ex.rethrowFromSystemServer();
        }
        
        // 3. 注册 GC watcher（不是 Binder death recipient）
        BinderInternal.addGcWatcher(new Runnable() {
            @Override
            public void run() {
                // GC 监控
            }
        });
    } else {
        // 系统进程
        // ...
    }
}
```

---

连续节选 [ActivityManagerService.java:5231–5265](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ActivityManagerService.java#5231)（不是独立编译单元）：

```java
if (app == null && startSeq > 0) {
    final ProcessRecord pending = mProcessList.mPendingStarts.get(startSeq);
    if (pending != null && pending.getStartUid() == callingUid
            && pending.getStartSeq() == startSeq
            && mProcessList.handleProcessStartedLocked(pending, pid,
                pending.isUsingWrapper(), startSeq, true)) {
        app = pending;
    }
}

if (app == null) {
    Slog.w(TAG, "No pending application record for pid " + pid
            + " (IApplicationThread " + thread + "); dropping process");
    EventLogTags.writeAmDropProcess(pid);
    if (pid > 0 && pid != MY_PID) {
        killProcessQuiet(pid);
        //TODO: killProcessGroup(app.info.uid, pid);
        // We can't log the app kill info for this process since we don't
        // know who it is, so just skip the logging.
    } else {
        try {
            thread.scheduleExit();
        } catch (Exception e) {
            // Ignore exceptions.
        }
    }
    return;
}

// If this application record is still attached to a previous
// process, clean it up now.
if (app.getThread() != null) {
    handleAppDiedLocked(app, pid, true, true, false /* fromBinderDied */);
}

```

这段 AMS attachApplicationLocked 处理 startSeq 对应 pending start：应用可能先回连、系统后拿到 fork 结果。UID 和序号匹配才能补入记录；未知进程不能仅凭 PID 或进程名获得关联。握手通过后注册 death recipient、发送 bindApplication；初始化异常和 Binder 死亡都有清理路径，参见 Activity 启动文档的握手与有限重试分析。

## 9. 源码路径

### 9.1 AMS 相关源码

```text
frameworks/base/services/core/java/com/android/server/am/
  ActivityManagerService.java / ProcessList.java / ProcessRecord.java
  ServiceRecord.java / ActiveServices.java
  ContentProviderRecord.java / ContentProviderHelper.java / ProviderMap.java
  BroadcastQueue.java / BroadcastQueueModernImpl.java
  UserController.java / PendingIntentRecord.java / ConnectionRecord.java
  psc/ProcessStateController.java / psc/OomAdjuster.java / psc/OomAdjusterImpl.java
  psc/Constants.java / psc/ProcessRecordInternal.java
frameworks/base/services/core/java/com/android/server/appop/AppOpsService.java
```

`ActivityManagerServiceEx.java` 不是本 AOSP tag 的通用扩展入口；OOM 调整已在 am/psc，不能指向 am 根目录旧文件。源码：[ProcessStateController.java:63](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/psc/ProcessStateController.java#63)。

### 9.2 ATMS 相关源码

```text
frameworks/base/services/core/java/com/android/server/wm/
  ActivityTaskManagerService.java / ActivityClientController.java
  ActivityRecord.java / Task.java / TaskFragment.java
  ActivityStarter.java / ActivityStartController.java / ActivityTaskSupervisor.java
  RootWindowContainer.java / DisplayContent.java / TaskDisplayArea.java
  WindowProcessController.java / ClientLifecycleManager.java
  TaskOrganizerController.java / RecentTasks.java
frameworks/base/core/java/android/window/TaskOrganizer.java
```

旧 ActivityStack/TaskRecord/ActivityStackSupervisor 不作为当前类路径保留。源码：[Task.java:207](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/Task.java#207)。

### 9.3 客户端源码

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        客户端源码路径                                       │
└─────────────────────────────────────────────────────────────────────────────┘

frameworks/base/core/java/android/app/
├── ActivityThread.java                  # 应用主线程
├── Activity.java                        # Activity 基类
├── Instrumentation.java                 # 仪器类
├── Application.java                     # Application 基类
├── ContextImpl.java                     # Context 实现
├── LoadedApk.java                       # 加载的 APK
├── IActivityManager.aidl                # AMS AIDL 接口
├── IApplicationThread.aidl              # 应用线程接口
├── ActivityManager.java                 # ActivityManager API
├── ActivityTaskManager.java             # ActivityTaskManager API
└── PendingIntent.java                   # PendingIntent

frameworks/base/core/java/android/content/
├── Intent.java                          # Intent
├── ComponentName.java                   # 组件名
├── Context.java                         # Context 接口
└── IntentFilter.java                    # Intent 过滤器
```

### 9.4 在线源码

```text
AOSP 源码浏览器:
• https://cs.android.com/ (main 分支)
• https://android.googlesource.com/

AndroidX 源码:
• https://cs.android.com/androidx (androidx-main 分支)
```

---

## 10. 面试常见问题

### 10.1 基础问题

**Q1: AMS 和 ATMS 的区别是什么？**

```text
┌─────────────────────────────────────────────────────────────────┐
│  AMS (ActivityManagerService)                                   │
│  • 进程管理 (启动/销毁/优先级)                                   │
│  • Service 管理                                                 │
│  • BroadcastReceiver 管理                                       │
│  • ContentProvider 管理                                         │
│  • 权限管理                                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ATMS (ActivityTaskManagerService) - Android 10+                │
│  • Activity 管理                                                │
│  • Task/Stack 管理                                              │
│  • 生命周期调度                                                 │
│  • 窗口管理协调                                                 │
│  • 最近任务                                                     │
└─────────────────────────────────────────────────────────────────┘

分离原因：
1. 代码解耦 - AMS 代码量过大
2. 性能优化 - Activity 管理可独立优化
3. 模块化 - 便于系统服务拆分
```

**Q2: 什么是 oom_adj？如何调整？**

当前使用 oom_score_adj 尺度；旧 0..15 的 oom_adj 数字不能混入现代表。典型常量位于 `services/core/java/com/android/server/am/psc/Constants.java`：

| 常量 | 值 | 含义 |
|---|---:|---|
| NATIVE_ADJ / SYSTEM_ADJ | -1000 / -900 | native / system_server 等高保护等级 |
| PERSISTENT_PROC_ADJ / PERSISTENT_SERVICE_ADJ | -800 / -700 | 常驻及相关服务 |
| FOREGROUND_APP_ADJ | 0 | 前台基准 |
| VISIBLE_APP_ADJ | 100 | 可见基准 |
| PERCEPTIBLE_APP_ADJ | 200 | 可感知基准，另有 50/225/250 等细分 |
| BACKUP_APP_ADJ / HEAVY_WEIGHT_APP_ADJ | 300 / 400 | 备份/重型应用 |
| SERVICE_ADJ / HOME_APP_ADJ | 500 / 600 | 服务/桌面 |
| PREVIOUS_APP_ADJ / SERVICE_B_ADJ | 700 / 800 | 上一个应用/服务 B |
| CACHED_APP_MIN_ADJ..MAX_ADJ | 900..999 | 缓存区间 |

实际 adj 还受窗口层级、进程依赖、服务绑定、缓存排序和特性开关影响。它是回收保护度，不是 CPU 调度优先级，也不是“负值进程任何情况下永不被杀”。源码：[Constants.java:76](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/psc/Constants.java#76)。

**Q3: Activity 四种启动模式的区别？**

```text
┌────────────────────────────────────────────────────────────────┐
│  1. standard (默认)                                            │
│     • 每次启动创建新实例                                        │
│     • 可以有多个相同 Activity 实例                              │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  2. singleTop                                                  │
│     • 如果在栈顶，不创建新实例，调用 onNewIntent()              │
│     • 不在栈顶，行为同 standard                                │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  3. singleTask                                                 │
│     • 在系统任务复用、用户与显示规则下查找已有实例，不是跨所有用户的全局单例                                          │
│     • 如果存在，将其 Task 移到前台，调用 onNewIntent()          │
│     • 其上方的 Activity 会被清除                                │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  4. singleInstance                                             │
│     • 在系统任务复用、用户与显示规则下查找已有实例，不是跨所有用户的全局单例                                          │
│     • 独占一个 Task，Task 中只有这一个 Activity                 │
│     • 调用 onNewIntent()                                       │
└────────────────────────────────────────────────────────────────┘
```

### 10.2 进阶问题

**Q4: Activity 启动流程？**

应用 → ATMS/ActivityStarter → Task/TaskFragment 任务选择与恢复 → ActivityTaskSupervisor。缺少进程时 AMS/ProcessList 经 ZygoteProcess 请求进程；应用 main/attach 回连 AMS，接收 bindApplication 与 ClientTransaction。LaunchActivityItem 触发 onCreate，事务推进 onStart/onResume，再建立窗口和首帧。不存在当前版 scheduleLaunchActivity 单独接口。详见 7.2 与 8。

**Q5: Zygote fork 进程的流程？**

```text
1. Zygote 预加载 (系统启动时)
   ├─► preloadClasses() - 预加载类
   ├─► preloadResources() - 预加载资源
   └─► preloadSharedLibraries() - 预加载共享库

2. 进入 Socket 监听
   └─► ZygoteServer.runSelectLoop()

3. 接收 fork 请求
   ├─► ZygoteConnection.processCommand()
   └─► Zygote.forkAndSpecialize()

4. fork 新进程
   └─► nativeForkAndSpecialize() - Native 层 fork

5. 子进程处理
   ├─► handleChildProc() - 处理子进程
   ├─► setArgV0() - 设置进程名
   └─► ActivityThread.main() - 进入主循环

6. 父进程 (Zygote)
   └─► 返回子进程 PID 给 AMS

优势：
• 预加载共享类和资源，减少启动时间
• Copy-on-Write 机制，节省内存
• 统一的进程模板
```

**Q6: oom_adj 和进程状态的对应关系？**

不存在固定一一对应。procState、adj、调度组和 capability 是进程状态控制器综合组件与依赖图后的不同输出；使用 5.1 的现代 oom_score_adj 常量，不能将 CACHED_EMPTY=15 等旧尺度映射到当前系统。

**Q7: Activity 的生命周期回调顺序？**

```text
启动: onCreate → onStart → onResume

切换到另一个 Activity:
A: onPause
B: onCreate → onStart → onResume
A: onStop

返回:
A: onRestart → onStart → onResume
B: onStop → onDestroy

back 键退出:
onPause → onStop → onDestroy

按 Home 键:
onPause → onStop (不会 onDestroy)

重新打开:
onRestart → onStart → onResume
```

### 10.3 高级问题

**Q8: Android 10 对 AMS 的重构？**

```text
从 Android 10 (API 29) 开始：
1. Activity 管理拆分到 ATMS
2. AMS 保留进程/Service/Broadcast/Provider 管理
3. ATMS 负责 Task/Stack/Activity 生命周期

架构变化：
• AMS 和 ATMS 是 system_server 内职责独立的服务
• 进程内通过 LocalService 等接口协作；对应用提供 Binder 接口
• 代码更模块化，便于维护和测试
```

**Q9: ActivityStack、TaskRecord、ActivityRecord 的关系？**

前两个是旧架构类。Android 17 使用 Task（继承 TaskFragment）、TaskFragment 和 ActivityRecord（继承 WindowToken）。Task 可包含任务/Activity/片段；TaskFragment 管理相应 resumed/pausing 状态，ActivityRecord 通过 WindowProcessController 关联进程。不能沿用 mTaskHistory/mActivities 的旧图。

**Q10: LMK (Low Memory Killer) 杀进程的原则？**

现代回收由 lmkd 等协作，根据内存压力信号、配置和进程保护等级挑选候选；不是固定执行 15→9→0 的旧内核 minfree 表。缓存 adj 通常在 900..999，负值为较强保护，不意味着进程免于显式 kill、崩溃或所有内核 OOM 情况。实际设备阈值及厂商策略不由 frameworks/base tag 独立决定。

**Q11: Intent Flags 和 LaunchMode 的区别？**

```text
┌────────────────────────────────────────────────────────────────┐
│  LaunchMode (Manifest)                                          │
│  • 声明式配置                                                  │
│  • 影响 Activity 在 Task 中的行为                              │
│  • 系统级规则                                                  │
├────────────────────────────────────────────────────────────────┤
│  Intent Flags (Java 代码)                                      │
│  • 运行时配置                                                  │
│  • 更灵活，可动态改变                                          │
│  • 可以组合多个 Flag                                           │
├────────────────────────────────────────────────────────────────┤
│  组合规则：Flags 与 LaunchMode 共同参与任务选择                                     │
│  • 没有所有 Flags 都无条件覆盖所有 LaunchMode 的通用优先级公式                   │
└────────────────────────────────────────────────────────────────┘

常见组合：
• FLAG_ACTIVITY_NEW_TASK + singleTask 效果类似
• 但 Flag 更灵活，可动态指定
```

**Q12: 应用切换到后台时 AMS 的处理？**

客户端完成暂停后经 ActivityClient/IActivityClientController 向 ActivityClientController 报告；ATMS 更新 Activity/可见性状态，AMS 的进程状态控制器重新评估整个进程及依赖。不是直接 ProcessRecord.setProcessState 或固定从 adj=0 改到 1/2。是否调度 stop 取决于可见性与过渡流程。

**Q13: 如何保证 Service 不被杀死？**

普通应用没有“永不被杀”的 Service。合法前台服务需要满足启动、类型、权限、通知和时间限制，只能提高相应保护；绑定依赖也不等于固定 adj。START_STICKY 表示符合条件时系统尝试重建，不承诺立即/必然重启。可延迟的可靠任务用 JobScheduler 等调度，而不是永久驻留进程。

**Q14: 进程保活方案有哪些？**

```text
⚠️ 不推荐：很多方案违反 Android 设计原则

1. 合理的前台服务
   • 音乐播放、导航等正当场景
   • 使用 startForeground()

2. JobScheduler
   • 系统级任务调度
   • 省电且可靠

3. WorkManager
   • WorkManager 是官方推荐
   • 自动处理后台任务

4. 多进程
   • 将核心逻辑放到独立进程
   • 但会增加复杂度

❌ 不推荐的方案：
• 1 像素悬浮窗
• 账户同步
• 互踢机制
• 通知栏常驻
这些方案不应作为符合平台生命周期的可靠后台执行方案
```

**Q15: Activity 状态变化时 AMS 的回调？**

系统下发方向：ClientLifecycleManager → IApplicationThread.scheduleTransaction → 主线程 TransactionExecutor。

客户端完成报告方向：对应事务 postExecute/停止报告等 → ActivityClient → IActivityClientController → ActivityClientController.activityResumed/Paused/Stopped/Destroyed。它不是 ApplicationThread.scheduleTransaction 反向调用 ATMS，亦没有统一 activityRestarted 完成回调。

## 总结

本文详细讲解了 Android AMS (ActivityManagerService) 的核心知识点，包括：

1. **AMS 架构** - 系统服务职责划分
2. **ATMS 职责** - Android 10+ 的重构
3. **栈管理** - Task、TaskFragment、ActivityRecord
4. **进程优先级** - oom_adj 机制和 LMK
5. **LaunchMode** - 启动模式与任务复用规则
6. **生命周期** - Activity 状态调度
7. **进程启动** - Zygote fork 流程

掌握这些知识点对于 Android 面试和性能优化都至关重要。建议结合源码加深理解。

---

*文档更新时间: 2026-09-10*
