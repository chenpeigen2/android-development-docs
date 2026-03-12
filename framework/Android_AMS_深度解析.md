# Android AMS 深度解析

> 作者：OpenClaw | 日期：2026-03-12  
> 基于源码：Android 16 (API 36) AOSP

## 目录

1. [概述](#1-概述)
2. [AMS 架构总览](#2-ams-架构总览)
3. [AMS 与 ATMS 职责划分](#3-ams-与-atms-职责划分)
4. [ActivityStack 与 TaskRecord](#4-activitystack-与-taskrecord)
5. [进程优先级 (oom_adj) 机制](#5-进程优先级-oom_adj-机制)
6. [LaunchMode 深度解析](#6-launchmode-深度解析)
7. [Activity 生命周期调度](#7-activity-生命周期调度)
8. [进程启动流程](#8-进程启动流程)
9. [源码路径](#9-源码路径)
10. [面试常见问题](#10-面试常见问题)

---

## 1. 概述

**ActivityManagerService (AMS)** 是 Android 系统的核心服务之一，负责管理应用的四大组件（Activity、Service、BroadcastReceiver、ContentProvider）以及进程的生命周期。

从 Android 10 (API 29) 开始，Google 对 AMS 进行了重大重构，将 Activity 相关的管理职责拆分到了 **ActivityTaskManagerService (ATMS)**，AMS 专注于进程管理、Service 和 ContentProvider 管理。

### 1.1 AMS 的核心职责

```
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

```
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

```
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

```
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

```java
/**
 * ProcessRecord - 进程记录
 * 位置：frameworks/base/services/core/java/com/android/server/am/ProcessRecord.java
 */
class ProcessRecord {
    // 进程基本信息
    ApplicationInfo info;              // 应用信息
    String processName;                // 进程名
    int pid;                           // 进程 ID
    int uid;                           // 用户 ID
    
    // 进程状态
    int curAdj;                        // 当前 oom_adj
    int setAdj;                        // 设置的 oom_adj
    int curProcState;                  // 当前进程状态
    int setProcState;                  // 设置的进程状态
    
    // 组件引用
    ArrayList<ActivityRecord> activities;      // Activity 列表
    ArrayList<ServiceRecord> services;         // Service 列表
    ArrayList<ConnectionRecord> connections;   // Service 连接
    ArrayList<ContentProviderRecord> pubProviders; // 发布的 Provider
    HashSet<ContentProviderRecord> conProviders;   // 使用的 Provider
    
    // 状态标志
    boolean crashing;                  // 是否正在崩溃
    boolean notResponding;             // 是否 ANR
    boolean bad;                       // 是否为坏进程
    boolean killed;                    // 是否已被杀
}

/**
 * ServiceRecord - 服务记录
 * 位置：frameworks/base/services/core/java/com/android/server/am/ServiceRecord.java
 */
class ServiceRecord {
    ComponentName name;                // 组件名
    String processName;                // 进程名
    Intent.FilterComparison intent;    // Intent
    
    // 服务状态
    boolean started;                   // 是否已启动
    boolean requestedStop;             // 是否请求停止
    int startRequested;                // 启动计数
    boolean delayed;                   // 是否延迟启动
    
    // 绑定相关
    ArrayMap<IBinder, ArrayList<ConnectionRecord>> connections; // 绑定连接
    
    // 前台服务
    boolean isForeground;              // 是否前台服务
    Notification foregroundNoti;       // 前台通知
}

/**
 * ContentProviderRecord - 内容提供者记录
 * 位置：frameworks/base/services/core/java/com/android/server/am/ContentProviderRecord.java
 */
class ContentProviderRecord {
    ProviderInfo info;                 // Provider 信息
    ComponentName name;                // 组件名
    String processName;                // 进程名
    
    // 状态
    boolean singleton;                 // 是否单例
    boolean noReleaseNeeded;           // 是否不需要释放
    
    // 引用计数
    ArrayMap<IBinder, Integer> connections; // 连接计数
}
```

---

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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ATMS 架构                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │               ActivityTaskManagerService                             │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                 核心组件                                      │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │ActivityRecord│  │ TaskRecord   │  │ActivityStack │     │ │ │
│   │   │   │ (Activity记录)│  │  (任务记录)  │  │ (Activity栈) │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │ActivityStarter│ │RootWindowContainer│WindowProcess│   │ │ │
│   │   │   │ (启动控制器)  │  │ (根窗口容器) │  │Controller   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                 辅助组件                                      │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │TaskOrganizer │  │RecentTasks   │  │DisplayContent│     │ │ │
│   │   │   │ (任务组织器) │  │ (最近任务)   │  │ (显示内容)   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 核心类关系

```java
/**
 * ActivityRecord - Activity 记录
 * 位置：frameworks/base/services/core/java/com/android/server/wm/ActivityRecord.java
 */
class ActivityRecord {
    // Activity 基本信息
    ComponentName mActivityComponent;  // 组件名
    Intent intent;                     // 启动 Intent
    String packageName;                // 包名
    String processName;                // 进程名
    
    // 状态
    ActivityState state;               // Activity 状态
    boolean finishing;                 // 是否正在结束
    boolean destroyed;                 // 是否已销毁
    
    // 关联
    TaskRecord task;                   // 所属 Task
    ActivityStack stack;               // 所属 Stack
    ProcessRecord app;                 // 所属进程
    
    // Window
    WindowToken appToken;              // Window Token
    ActivityRecord waitingVisible;     // 等待可见的 Activity
}

/**
 * TaskRecord - 任务记录
 * 位置：frameworks/base/services/core/java/com/android/server/wm/TaskRecord.java
 */
class TaskRecord {
    // 基本信息
    int taskId;                        // 任务 ID
    Intent intent;                     // 根 Intent
    ComponentName origActivity;        // 原始 Activity
    
    // 栈管理
    ArrayList<ActivityRecord> mActivities; // Activity 列表
    ActivityStack stack;               // 所属 Stack
    
    // 状态
    int userId;                        // 用户 ID
    boolean wasPaused;                 // 是否已暂停
}

/**
 * ActivityStack - Activity 栈
 * 位置：frameworks/base/services/core/java/com/android/server/wm/ActivityStack.java
 */
class ActivityStack {
    // 栈管理
    ArrayList<TaskRecord> mTaskHistory;    // Task 列表
    ActivityRecord mPausingActivity;       // 正在暂停的 Activity
    ActivityRecord mResumedActivity;       // 已恢复的 Activity
    
    // 状态
    ActivityRecord mLastPausedActivity;    // 最后暂停的 Activity
    boolean mGoingToSleep;                 // 是否进入休眠
}
```

---

## 4. ActivityStack 与 TaskRecord

### 4.1 栈结构总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Activity 栈结构                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                     RootWindowContainer                              │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                   DisplayContent (显示 0)                     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌────────────────────────────────────────────────────┐    │ │ │
│   │   │   │            ActivityStack (Launcher 栈)             │    │ │ │
│   │   │   │                                                     │    │ │ │
│   │   │   │   ┌──────────────────────────────────────────┐    │    │ │ │
│   │   │   │   │      TaskRecord (Task 1 - 微信)          │    │    │ │ │
│   │   │   │   │                                          │    │    │ │ │
│   │   │   │   │   ┌────────────────────────────────┐    │    │    │ │ │
│   │   │   │   │   │ ActivityRecord (聊天界面)     │    │    │    │ │ │
│   │   │   │   │   └────────────────────────────────┘    │    │    │ │ │
│   │   │   │   │   ┌────────────────────────────────┐    │    │    │ │ │
│   │   │   │   │   │ ActivityRecord (朋友圈)       │    │    │    │ │ │
│   │   │   │   │   └────────────────────────────────┘    │    │    │ │ │
│   │   │   │   └──────────────────────────────────────────┘    │    │ │ │
│   │   │   │                                                     │    │ │ │
│   │   │   │   ┌──────────────────────────────────────────┐    │    │ │ │
│   │   │   │   │      TaskRecord (Task 2 - 支付宝)        │    │    │ │ │
│   │   │   │   │                                          │    │    │ │ │
│   │   │   │   │   ┌────────────────────────────────┐    │    │    │ │ │
│   │   │   │   │   │ ActivityRecord (首页)         │    │    │    │ │ │
│   │   │   │   │   └────────────────────────────────┘    │    │    │ │ │
│   │   │   │   │   ┌────────────────────────────────┐    │    │    │ │ │
│   │   │   │   │   │ ActivityRecord (扫一扫)       │    │    │    │ │ │
│   │   │   │   │   └────────────────────────────────┘    │    │    │ │ │
│   │   │   │   └──────────────────────────────────────────┘    │    │ │ │
│   │   │   │                                                     │    │ │ │
│   │   │   └────────────────────────────────────────────────────┘    │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Task 与 Activity 关系

```
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

### 4.3 ActivityStack 类型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ActivityStack 类型                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   1. Home Stack (桌面栈)                                                    │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   • 包含 Launcher 和 RecentsActivity                               │ │
│   │   • 系统级 Stack，优先级较低                                        │ │
│   │   • 位置：stackId = HOME_STACK_ID (0)                             │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   2. Fullscreen Stack (全屏栈)                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   • 标准应用 Stack                                                 │ │
│   │   • 占据全屏显示                                                   │ │
│   │   • 位置：stackId = FULLSCREEN_WORKSPACE_STACK_ID (1)             │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   3. Freeform Stack (自由窗口栈)                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   • 桌面模式自由窗口                                                │ │
│   │   • 可拖动、调整大小                                                │ │
│   │   • 位置：stackId = FREEFORM_WORKSPACE_STACK_ID (2)               │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   4. Pinned Stack (画中画栈)                                                │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   • 画中画模式 (PiP)                                               │ │
│   │   • 小窗口悬浮                                                     │ │
│   │   • 位置：stackId = PINNED_STACK_ID (3)                           │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 Activity 状态

```java
/**
 * Activity 状态枚举
 * 位置：frameworks/base/services/core/java/com/android/server/wm/ActivityRecord.java
 */
enum ActivityState {
    INITIALIZING,      // 初始化中
    RESUMED,           // 已恢复 (前台)
    PAUSING,           // 正在暂停
    PAUSED,            // 已暂停
    STOPPING,          // 正在停止
    STOPPED,           // 已停止
    FINISHING,         // 正在结束
    DESTROYING,        // 正在销毁
    DESTROYED          // 已销毁
}

/**
 * 状态转换图
 * 
 * INITIALIZING
 *      │
 *      ▼
 *   RESUMED ◄────────────┐
 *      │                 │
 *      ▼                 │
 *   PAUSING              │
 *      │                 │
 *      ▼                 │
 *   PAUSED ──────────────┤ (onRestart → onStart → onResume)
 *      │                 │
 *      ▼                 │
 *   STOPPING             │
 *      │                 │
 *      ▼                 │
 *   STOPPED ─────────────┘ (返回到前台)
 *      │
 *      ▼
 *   FINISHING
 *      │
 *      ▼
 *   DESTROYING
 *      │
 *      ▼
 *   DESTROYED
 */
```

---

## 5. 进程优先级 (oom_adj) 机制

### 5.1 oom_adj 等级

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        oom_adj 等级表                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┬──────────────────┬────────────────────────────────────────┐
│  adj 值     │     优先级        │              说明                      │
├─────────────┼──────────────────┼────────────────────────────────────────┤
│  -1000      │ NATIVE_ADJ       │ Native 进程 (不被 LMK 杀)             │
│  -900       │ SYSTEM_ADJ       │ 系统进程 (system_server)              │
│  -800       │ PERSISTENT_PROC  │ 常驻进程 (Phone 等)                   │
│  -700       │ PERSISTENT_SERVICE│ 常驻服务                             │
│  0          │ FOREGROUND_APP   │ 前台应用 (当前显示的 Activity)        │
│  1          │ VISIBLE_APP      │ 可见应用 (不在前台但可见)             │
│  2          │ PERCEPTIBLE_APP  │ 可感知应用 (播放音乐)                 │
│  3          │ BACKUP_APP       │ 备份应用                              │
│  4          │ HEAVY_WEIGHT_APP │ 重量级应用                            │
│  5          │ SERVICE          │ 服务进程                              │
│  6          │ HOME_APP         │ 桌面进程                              │
│  7          │ PREVIOUS_APP     │ 前一个应用                            │
│  8          │ SERVICE_B        │ B 类服务 (旧缓存服务)                 │
│  9          │ CACHED_APP       │ 缓存应用 (最近最少使用)               │
│  10-15      │ CACHED_APP_MAX   │ 缓存应用 (更少使用)                   │
└─────────────┴──────────────────┴────────────────────────────────────────┘

LMK (Low Memory Killer) 杀进程顺序：
adj 越大，越容易被杀
9 → 8 → 7 → 6 → 5 → ... → 0 (最后杀)
```

### 5.2 进程状态 (ProcessState)

```java
/**
 * 进程状态枚举
 * 位置：frameworks/base/services/core/java/com/android/server/am/ProcessList.java
 */
class ProcessList {
    // 进程状态常量
    static final int PROCESS_STATE_UNKNOWN = -1;
    static final int PROCESS_STATE_PERSISTENT = 0;
    static final int PROCESS_STATE_PERSISTENT_UI = 1;
    static final int PROCESS_STATE_TOP = 2;              // 前台 Activity
    static final int PROCESS_STATE_BOUND_TOP = 3;        // 绑定到前台应用
    static final int PROCESS_STATE_FOREGROUND_SERVICE = 4; // 前台服务
    static final int PROCESS_STATE_BOUND_FOREGROUND_SERVICE = 5;
    static final int PROCESS_STATE_IMPORTANT_FOREGROUND = 6;
    static final int PROCESS_STATE_IMPORTANT_BACKGROUND = 7;
    static final int PROCESS_STATE_TRANSIENT_BACKGROUND = 8;
    static final int PROCESS_STATE_BACKUP = 9;
    static final int PROCESS_STATE_SERVICE = 10;
    static final int PROCESS_STATE_RECEIVER = 11;
    static final int PROCESS_STATE_TOP_SLEEPING = 12;
    static final int PROCESS_STATE_HEAVY_WEIGHT = 13;
    static final int PROCESS_STATE_HOME = 14;
    static final int PROCESS_STATE_LAST_ACTIVITY = 15;
    static final int PROCESS_STATE_CACHED_ACTIVITY = 16;
    static final int PROCESS_STATE_CACHED_ACTIVITY_CLIENT = 17;
    static final int PROCESS_STATE_CACHED_RECENT = 18;
    static final int PROCESS_STATE_CACHED_EMPTY = 19;
}
```

### 5.3 oom_adj 调整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        oom_adj 调整流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Activity 状态变化            AMS/ATMS                    OomAdjuster
       │                         │                            │
       ▼                         │                            │
┌─────────────┐                 │                            │
│onResume()   │                 │                            │
└──────┬──────┘                 │                            │
       │                        │                            │
       │                        │                            │
       └────────────┬───────────┘                            │
                    │                                        │
                    ▼                                        │
          ┌─────────────────┐                              │
          │ATMS 更新        │                              │
          │ActivityRecord   │                              │
          │.state = RESUMED │                              │
          └────────┬────────┘                              │
                   │                                       │
                   │                                       │
                   └───────────────┬───────────────────────┘
                                   │
                                   ▼
                      ┌───────────────────────┐
                      │  OomAdjuster          │
                      │  .computeOomAdj()     │
                      │                       │
                      │  1. 检查进程状态      │
                      │  2. 计算新的 oom_adj  │
                      │  3. 更新 ProcessRecord│
                      └───────────┬───────────┘
                                  │
                                  ▼
                      ┌───────────────────────┐
                      │  写入 /proc/[pid]/oom_adj│
                      │                       │
                      │  LMK 监控该值决定杀进程│
                      └───────────────────────┘

触发 oom_adj 调整的时机：
1. Activity 状态变化 (onResume/onPause/onStop)
2. Service 启动/绑定/停止
3. 前台服务启动/停止
4. ContentProvider 使用/释放
5. 广播接收/完成
```

### 5.4 查看 oom_adj 命令

```bash
# 查看进程 oom_adj
adb shell cat /proc/[pid]/oom_adj

# 查看进程 oom_score_adj
adb shell cat /proc/[pid]/oom_score_adj

# 查看所有进程 oom_adj
adb shell ps -A | grep [package]
adb shell cat /proc/[pid]/oom_adj

# 示例
$ adb shell ps -A | grep com.example
u0_a123      12345  1234  ...  com.example.app

$ adb shell cat /proc/12345/oom_adj
0  # 前台应用

# 应用切换到后台后
$ adb shell cat /proc/12345/oom_adj
9  # 缓存应用
```

---

## 6. LaunchMode 深度解析

### 6.1 四种启动模式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LaunchMode 四种模式                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   1. standard (标准模式) - 默认                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   • 每次启动都创建新实例                                             │ │
│   │   • 可以有多个相同 Activity 实例                                     │ │
│   │   • 谁启动就进入谁的 Task                                            │ │
│   │   • 栈顶模式                                                         │ │
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
│   │   • 全局只有一个实例                                                 │ │
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
│   │   • 全局只有一个实例                                                 │ │
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
│   Task D: [D] (前台，新 Task)                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

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

```
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
  1. taskAffinity 必须包含至少一个点 (.)
  2. 与 singleTask 或 FLAG_ACTIVITY_NEW_TASK 配合使用
  3. standard/singleTop 模式下，taskAffinity 不影响启动行为
-->
```

---

## 7. Activity 生命周期调度

### 7.1 生命周期总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Activity 生命周期                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Activity 启动                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   onCreate()                                                        │ │
│   │      │                                                              │ │
│   │      ▼                                                              │ │
│   │   onStart()                                                         │ │
│   │      │                                                              │ │
│   │      ▼                                                              │ │
│   │   onResume() ◄──────────────────┐ (从 onPause 返回)                │ │
│   │      │                          │                                   │ │
│   │      │ Activity 可见且可交互     │                                   │ │
│   │      │                          │                                   │ │
│   │      ▼                          │                                   │ │
│   │   onPause() ────────────────────┘                                   │ │
│   │      │                                                              │ │
│   │      ├─► 另一个 Activity 进入前台                                   │ │
│   │      │                                                              │ │
│   │      ▼                                                              │ │
│   │   onStop() ◄───────────────────┐ (从 onRestart 返回)               │ │
│   │      │                         │                                    │ │
│   │      ├─► Activity 完全不可见   │                                    │ │
│   │      │                         │                                    │ │
│   │      ▼                         │                                    │ │
│   │   onRestart() ─────────────────┘                                    │ │
│   │      │                                                              │ │
│   │      ▼                                                              │ │
│   │   onDestroy()                                                       │ │
│   │      │                                                              │ │
│   │      ▼                                                              │ │
│   │   Activity 销毁                                                     │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 生命周期调度源码

```java
/**
 * ActivityThread - 生命周期调度
 * 位置：frameworks/base/core/java/android/app/ActivityThread.java
 */
class ActivityThread {
    
    /**
     * 处理 Launch Activity 请求
     */
    private void handleLaunchActivity(ActivityClientRecord r, Intent customIntent) {
        // 1. 创建 Activity
        Activity a = performLaunchActivity(r, customIntent);
        
        if (a != null) {
            // 2. 处理状态
            r.createdConfig = new Configuration(mConfiguration);
            
            // 3. 调用 onResume
            handleResumeActivity(r.token, false, r.isForward, 
                    !r.activity.mFinished && !r.startsNotResumed);
        }
    }
    
    /**
     * 执行 Activity 启动
     */
    private Activity performLaunchActivity(ActivityClientRecord r, Intent customIntent) {
        // 1. 获取 ActivityInfo
        ActivityInfo aInfo = r.activityInfo;
        
        // 2. 创建 Context
        ContextImpl appContext = createBaseContextForActivity(r);
        
        // 3. 创建 Activity 实例
        Activity activity = null;
        java.lang.ClassLoader cl = appContext.getClassLoader();
        activity = mInstrumentation.newActivity(cl, component.getClassName(), r.intent);
        
        // 4. 创建 Application
        Application app = r.packageInfo.makeApplication(false, mInstrumentation);
        
        // 5. 调用 attach
        activity.attach(appContext, this, getInstrumentation(), r.token,
                r.ident, app, r.intent, r.activityInfo, title, r.parent,
                r.embeddedID, r.lastNonConfigurationInstances, config);
        
        // 6. 调用 onCreate
        if (r.isPersistable()) {
            mInstrumentation.callActivityOnCreate(activity, r.state, r.persistentState);
        } else {
            mInstrumentation.callActivityOnCreate(activity, r.state);
        }
        
        // 7. 调用 onStart
        if (!r.activity.mFinished) {
            activity.performStart();
            r.state = null;
        }
        
        return activity;
    }
    
    /**
     * 处理 Resume Activity
     */
    final void handleResumeActivity(IBinder token, boolean clearHide, 
            boolean isForward, boolean reallyResume) {
        
        // 1. 调用 onResume
        ActivityClientRecord r = performResumeActivity(token, clearHide);
        
        if (r != null) {
            final Activity a = r.activity;
            
            // 2. 将 DecorView 添加到 WindowManager
            if (r.window == null && !a.mFinished && willBeVisible) {
                r.window = r.activity.getWindow();
                View decor = r.window.getDecorView();
                ViewManager wm = a.getWindowManager();
                WindowManager.LayoutParams l = r.window.getAttributes();
                wm.addView(decor, l);
            }
            
            // 3. 通知 ATMS resume 完成
            if (reallyResume) {
                ActivityManager.getService().activityResumed(token);
            }
        }
    }
}
```

### 7.3 生命周期与系统状态

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    生命周期与系统状态对应                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Activity 状态          系统状态              oom_adj                      │
│   ────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│   onCreate()            INITIALIZING          0 (FOREGROUND_APP)           │
│   onStart()             RESUMED/PAUSED        0-1                          │
│   onResume()            RESUMED               0 (FOREGROUND_APP)           │
│   onPause()             PAUSING/PAUSED        0-2                          │
│   onStop()              STOPPING/STOPPED      2-7                          │
│   onDestroy()           DESTROYING/DESTROYED  9+ (CACHED_APP)              │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │   特殊情况：                                                         │ │
│   │                                                                     │ │
│   │   1. 前台服务 (Foreground Service)                                  │ │
│   │      • oom_adj = 3 (PERCEPTIBLE_APP)                               │ │
│   │      • 不容易被杀                                                   │ │
│   │                                                                     │ │
│   │   2. 可见但非前台 (Visible but not focused)                         │ │
│   │      • oom_adj = 1 (VISIBLE_APP)                                   │ │
│   │      • 如：分屏模式下的非焦点应用                                   │ │
│   │                                                                     │ │
│   │   3. 后台播放音乐 (Background music)                                │ │
│   │      • oom_adj = 2 (PERCEPTIBLE_APP)                               │ │
│   │      • 用户可感知                                                   │ │
│   │                                                                     │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. 进程启动流程

### 8.1 进程启动完整流程

```
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
                │  AMS.startProcess()  │                           │
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
                             │  Zygote (Native)      │              │
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
                                          │  1. Looper.prepare() │ │
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

```
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
│   │      ├─► 创建 Application (可选)                                    │ │
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
        
        // 3. 注册 Binder 死亡监听
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

## 9. 源码路径

### 9.1 AMS 相关源码

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AMS 源码路径                                         │
└─────────────────────────────────────────────────────────────────────────────┘

frameworks/base/services/core/java/com/android/server/am/
├── ActivityManagerService.java          # AMS 主类
├── ActivityManagerServiceEx.java        # AMS 扩展
├── ProcessRecord.java                   # 进程记录
├── ServiceRecord.java                   # 服务记录
├── ContentProviderRecord.java           # ContentProvider 记录
├── ProcessList.java                     # 进程列表管理
├── OomAdjuster.java                     # OOM 调整器
├── ActiveServices.java                  # 服务管理
├── BroadcastQueue.java                  # 广播队列
├── ProviderMap.java                     # Provider 映射
├── BatteryStatsService.java             # 电池统计
├── AppOpsService.java                   # 应用操作服务
├── UserController.java                  # 用户控制器
├── PendingIntentRecord.java             # PendingIntent 记录
└── ConnectionRecord.java                # 服务连接记录
```

### 9.2 ATMS 相关源码

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ATMS 源码路径                                        │
└─────────────────────────────────────────────────────────────────────────────┘

frameworks/base/services/core/java/com/android/server/wm/
├── ActivityTaskManagerService.java      # ATMS 主类
├── ActivityRecord.java                  # Activity 记录
├── TaskRecord.java                      # Task 记录
├── ActivityStack.java                   # Activity 栈
├── ActivityStarter.java                 # Activity 启动器
├── RootWindowContainer.java             # 根窗口容器
├── WindowProcessController.java         # 窗口进程控制器
├── TaskOrganizerController.java         # Task 组织器
├── RecentTasks.java                     # 最近任务
├── DisplayContent.java                  # 显示内容
├── ActivityStackSupervisor.java         # Activity 栈管理器
└── TaskOrganizer.java                   # Task 组织器
```

### 9.3 客户端源码

```
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

```
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

```
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

```
oom_adj (Out of Memory Adjuster) 是进程的优先级值：
• 值越小，优先级越高，越不容易被 LMK 杀死
• 值越大，优先级越低，越容易被 LMK 杀死

常见值：
• 0: 前台应用 (当前显示的 Activity)
• 1: 可见应用 (不在前台但可见)
• 2: 可感知应用 (播放音乐)
• 5: 服务进程
• 9: 缓存应用

调整时机：
• Activity 状态变化 (onResume/onPause/onStop)
• Service 启动/停止
• 前台服务启动/停止
• ContentProvider 使用/释放

调整者：OomAdjuster.computeOomAdj()
```

**Q3: Activity 四种启动模式的区别？**

```
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
│     • 全局只有一个实例                                          │
│     • 如果存在，将其 Task 移到前台，调用 onNewIntent()          │
│     • 其上方的 Activity 会被清除                                │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  4. singleInstance                                             │
│     • 全局只有一个实例                                          │
│     • 独占一个 Task，Task 中只有这一个 Activity                 │
│     • 调用 onNewIntent()                                       │
└────────────────────────────────────────────────────────────────┘
```

### 10.2 进阶问题

**Q4: Activity 启动流程？**

```
1. 客户端调用 startActivity()
   └─► Instrumentation.execStartActivity()

2. Binder IPC 调用 ATMS
   └─► ActivityTaskManagerService.startActivity()

3. ATMS 处理
   ├─► ActivityStarter.execute() - 解析 Intent/检查权限
   ├─► ActivityStackSupervisor.startActivityUnchecked() - 决定 Task 归属
   └─► ActivityStack.startActivityLocked() - ActivityRecord 入栈

4. 检查目标进程是否存在
   ├─► 存在 → 直接调度生命周期
   └─► 不存在 → AMS.startProcess()

5. AMS 启动进程
   └─► ProcessList.startProcessLocked()
       └─► ZygoteProcess.start()
           └─► Zygote fork 新进程

6. 新进程启动
   └─► ActivityThread.main()
       ├─► Looper.prepareMainLooper()
       ├─► attach() → 注册到 AMS
       └─► Looper.loop()

7. AMS 回调
   └─► ApplicationThread.bindApplication()
       └─► handleBindApplication()
           └─► Application.onCreate()

8. ATMS 调度 Activity
   └─► ApplicationThread.scheduleLaunchActivity()
       └─► handleLaunchActivity()
           ├─► performLaunchActivity() - onCreate/onStart
           └─► handleResumeActivity() - onResume
```

**Q5: Zygote fork 进程的流程？**

```
1. Zygote 预加载 (系统启动时)
   ├─► preloadClasses() - 预加载类
   ├─► preloadResources() - 预加载资源
   └─► preloadSharedLibraries() - 预加载共享库

2. 进入 Socket 监听
   └─► ZygoteServer.runSelectLoop()

3. 接收 fork 请求
   ├─► ZygoteConnection.processCommand()
   └─► ZygoteConnection.forkAndSpecialize()

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

```
┌────────────────────────────────────────────────────────────────┐
│  进程状态                    oom_adj       说明                │
├────────────────────────────────────────────────────────────────┤
│  PROCESS_STATE_TOP         0             前台 Activity          │
│  PROCESS_STATE_BOUND_TOP  0             绑定到前台             │
│  PROCESS_STATE_FOREGROUND_SERVICE  0-1  前台服务              │
│  PROCESS_STATE_IMPORTANT_FOREGROUND  2  重要前台              │
│  PROCESS_STATE_IMPORTANT_BACKGROUND  7  重要后台              │
│  PROCESS_STATE_SERVICE      5-10        服务进程              │
│  PROCESS_STATE_HOME        6            桌面进程              │
│  PROCESS_STATE_CACHED_ACTIVITY  9      缓存 Activity         │
│  PROCESS_STATE_CACHED_EMPTY  15        空缓存进程            │
└────────────────────────────────────────────────────────────────┘
```

**Q7: Activity 的生命周期回调顺序？**

```
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

```
从 Android 10 (API 29) 开始：
1. Activity 管理拆分到 ATMS
2. AMS 保留进程/Service/Broadcast/Provider 管理
3. ATMS 负责 Task/Stack/Activity 生命周期

架构变化：
• AMS 和 ATMS 独立运行
• 通过 Binder 交互
• 代码更模块化，便于维护和测试
```

**Q9: ActivityStack、TaskRecord、ActivityRecord 的关系？**

```
┌────────────────────────────────────────────────────────────────┐
│  ActivityStack (Activity 栈)                                   │
│  • 管理多个 TaskRecord                                        │
│  • 栈结构：mTaskHistory                                       │
│  • 状态管理：mPausingActivity, mResumedActivity              │
├────────────────────────────────────────────────────────────────┤
│  TaskRecord (任务记录)                                          │
│  • 管理一个 Task 中的所有 Activity                            │
│  • 栈结构：mActivities                                        │
│  • 属性：taskId, intent, origActivity                         │
├────────────────────────────────────────────────────────────────┤
│  ActivityRecord (Activity 记录)                               │
│  • 描述一个 Activity 实例                                     │
│  • 状态：state, finishing, destroyed                         │
│  • 关联：task, stack, app                                    │
└────────────────────────────────────────────────────────────────┘

层级关系：
ActivityStack → TaskRecord → ActivityRecord
```

**Q10: LMK (Low Memory Killer) 杀进程的原则？**

```
1. oom_adj 越大越容易被杀
   CACHED_EMPTY (15) → CACHED_APP (9) → ... → FOREGROUND_APP (0)

2. 内存阈值
   • 系统有多个内存阈值 (minfree)
   • 当可用内存低于阈值时，杀死对应优先级的进程

3. 杀进程顺序
   a. 先杀 CACHED_EMPTY (adj=15)
   b. 再杀 CACHED_APP (adj=9-10)
   c. 依此类推...
   d. 最后杀 FOREGROUND_APP (adj=0)

4. 保护机制
   • PERSISTENT_PROC (-800) 不被杀
   • SYSTEM_ADJ (-900) 不被杀
   • NATIVE_ADJ (-1000) 不被杀
```

**Q11: Intent Flags 和 LaunchMode 的区别？**

```
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
│  优先级：Flags > LaunchMode                                     │
│  • 如果 Flags 指定了行为，会覆盖 LaunchMode                   │
└────────────────────────────────────────────────────────────────┘

常见组合：
• FLAG_ACTIVITY_NEW_TASK + singleTask 效果类似
• 但 Flag 更灵活，可动态指定
```

**Q12: 应用切换到后台时 AMS 的处理？**

```
1. onPause 触发
   └─► ATMS.activityPaused()

2. 更新进程状态
   └─► ProcessRecord.setProcessState()

3. 调整 oom_adj
   └─► OomAdjuster.computeOomAdj()
   • 从 0 (FOREGROUND_APP) 调整为 1-2 (VISIBLE/PERCEPTIBLE)

4. 如果需要
   └─► 启动 Home Activity
   └─► 调度 onStop
```

**Q13: 如何保证 Service 不被杀死？**

```
1. 前台服务 (Foreground Service)
   • startForeground() 启动前台服务
   • oom_adj = 2-3，不容易被杀
   • 需要显示通知栏

2. 绑定到前台 Activity
   • 与可见 Activity 绑定
   • oom_adj = 1 (VISIBLE_APP)

3. 使用 sticky 的 Service
   • return START_STICKY
   • 被杀死后会自动重启

4. 使用 JobScheduler/WorkManager
   • 系统级任务调度
   • 更可靠的后台任务
```

**Q14: 进程保活方案有哪些？**

```
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
这些方案可能会被 Google Play 下架
```

**Q15: Activity 状态变化时 AMS 的回调？**

```
┌────────────────────────────────────────────────────────────────┐
│  客户端                                                       │
│  Activity.onXxx()                                            │
│       │                                                       │
│       ▼                                                       │
│  Instrumentation                                              │
│       │                                                       │
│       ▼                                                       │
│  ApplicationThread.scheduleTransaction()                       │
└────────────────────────────────────────────────────────────────┘
                      │ Binder IPC
                      ▼
┌────────────────────────────────────────────────────────────────┐
│  系统服务端                                                   │
│  ActivityTaskManagerService                                    │
│       │                                                       │
│       ├─► activityPaused()    → onPause 完成                  │
│       ├─► activityStopped()   → onStop 完成                   │
│       ├─► activityResumed()   → onResume 完成                 │
│       ├─► activityDestroyed()→ onDestroy 完成                │
│       └─► activityRestarted()→ onRestart 完成                │
└────────────────────────────────────────────────────────────────┘
```

---

## 总结

本文详细讲解了 Android AMS (ActivityManagerService) 的核心知识点，包括：

1. **AMS 架构** - 系统服务职责划分
2. **ATMS 职责** - Android 10+ 的重构
3. **栈管理** - ActivityStack、TaskRecord、ActivityRecord
4. **进程优先级** - oom_adj 机制和 LMK
5. **LaunchMode** - 四种启动模式详解
6. **生命周期** - Activity 状态调度
7. **进程启动** - Zygote fork 流程

掌握这些知识点对于 Android 面试和性能优化都至关重要。建议结合源码加深理解。

---

*文档更新时间: 2026-03-12*
