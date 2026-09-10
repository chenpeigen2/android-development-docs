# Android Activity 启动流程完全指南

> 作者：OpenClaw | 日期：2026-03-07

## 目录

- [1. 概述](#1-概述)
- [2. Activity 启动的两种方式](#2-activity-启动的两种方式)
  - [2.1 显式启动](#21-显式启动)
  - [2.2 隐式启动](#22-隐式启动)
- [3. 启动流程详解](#3-启动流程详解)
  - [3.1 整体架构](#31-整体架构)
  - [3.2 完整流程图](#32-完整流程图)
  - [3.3 核心类协作时序图](#33-核心类协作时序图)
  - [3.4 进程间通信 (IPC) 总结](#34-进程间通信-ipc-总结)
  - [3.5 AMS 与 ActivityThread 完整通信流程](#35-ams-与-activitythread-完整通信流程)
  - [3.6 ApplicationThread 详解](#36-applicationthread-详解)
  - [3.7 ApplicationThread 与 ActivityThread.H 交互](#37-applicationthread-与-activitythreadh-交互)
  - [3.8 关键时序图：ApplicationThread 生命周期回调](#38-关键时序图applicationthread-生命周期回调)
  - [3.9 ViewRootImpl 衔接流程](#39-viewrootimpl-衔接流程)
  - [3.10 PhoneWindow 详解](#310-phonewindow-详解)
    - [3.10.1 PhoneWindow 创建时机](#3101-phonewindow-创建时机)
    - [3.10.2 mContentParent 初始化](#3102-mcontentparent-初始化)
    - [3.10.3 DecorView 什么时候添加到 WindowManager](#3103-decorview-什么时候添加到-windowmanager)
    - [3.10.4 Activity.attach() 详解](#3104-activityattach-详解)
    - [3.10.5 完整流程总结](#3105-完整流程总结)
  - [3.11 完整时序图 (AMS → AT → ViewRootImpl)](#311-完整时序图-ams--at--viewrootimpl)
  - [3.12 详细步骤](#312-详细步骤)
    - [Step 1: 调用 startActivity()](#step-1-调用-startactivity)
    - [Step 2: Instrumentation 处理](#step-2-instrumentation-处理)
    - [Step 3: ActivityTaskManagerService (ATMS) 处理](#step-3-activitytaskmanagerservice-atms-处理)
    - [Step 4: ActivityStarter 执行启动](#step-4-activitystarter-执行启动)
    - [Step 5: ActivityTaskSupervisor 调度与任务选择](#step-5-activitytasksupervisor-调度与任务选择)
    - [Step 6: Task 与 TaskFragment 管理](#step-6-task-与-taskfragment-管理)
    - [Step 7: 创建 Application（如果需要）](#step-7-创建-application如果需要)
    - [Step 8: 创建 Activity 实例](#step-8-创建-activity-实例)
    - [Step 9: 创建 Window 和 View](#step-9-创建-window-和-view)
    - [Step 10: View 的绘制流程](#step-10-view-的绘制流程)
- [4. 核心组件交互](#4-核心组件交互)
  - [4.1 Binder 通信](#41-binder-通信)
  - [4.2 关键 AIDL 接口](#42-关键-aidl-接口)
- [5. 生命周期回调](#5-生命周期回调)
  - [5.1 完整生命周期](#51-完整生命周期)
  - [5.2 启动过程生命周期](#52-启动过程生命周期)
- [6. 常见问题与优化](#6-常见问题与优化)
  - [6.1 启动优化建议](#61-启动优化建议)
  - [6.2 启动模式详解](#62-启动模式详解)
  - [6.3 Intent Flags 常用组合](#63-intent-flags-常用组合)
- [7. 总结](#7-总结)
- [参考资料](#参考资料)

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

Activity 启动涉及调用方、system_server 和目标应用；仅在目标进程不存在时走 Zygote 分支。Activity/Task 决策由 ATMS 管理，进程由 AMS/ProcessList 管理。两者在同一进程内通常通过 LocalService 等内部接口协作，不是每个箭头都跨 Binder。

```text
调用方 -> ATMS / ActivityStarter -> Task / TaskFragment / ActivityRecord
                         |                         |
                    AMS / ProcessList        ClientLifecycleManager
                         |                         |
                    Zygote socket             IApplicationThread
                         +--------> 目标 ActivityThread 主线程
                                           Activity -> PhoneWindow -> DecorView
                                           WindowManagerGlobal -> ViewRootImpl
```

`ActivityStackSupervisor`、`ActivityStack`、`TaskRecord` 是旧架构名称；本 tag 使用 `ActivityTaskSupervisor`、`Task`、`TaskFragment`。服务端 `ActivityRecord` 不是客户端 Activity 实例。源码：[ActivityTaskSupervisor.java:184](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#184)；[Task.java:207](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/Task.java#207)；[TaskFragment.java:123](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/TaskFragment.java#123)

### 3.2 完整流程图

```text
调用方 Activity.startActivity -> startActivityForResult -> Instrumentation.execStartActivity
  -> IActivityTaskManager.startActivity（应用到 system_server 的 Binder）
  -> ATMS.startActivityAsUser -> ActivityStartController.obtainStarter(...).execute()
  -> ActivityStarter.execute -> executeRequest -> startActivityUnchecked -> startActivityInner
  -> Task.startActivityLocked / RootWindowContainer.resumeFocusedTasksTopActivities
  -> Task / TaskFragment resume 路径 -> ActivityTaskSupervisor.startSpecificActivity
       已有进程：realStartActivityLocked
       无进程：ATMS.startProcessAsync -> AMS / ProcessList -> Process.start
                -> ZygoteProcess.start -> Zygote socket -> fork / specialize
目标 ActivityThread.main -> attach -> IActivityManager.attachApplication（回连 AMS）
  -> AMS.attachApplicationLocked -> IApplicationThread.bindApplication
  -> ATMS LocalService.attachApplication -> RootWindowContainer.attachApplication
  -> ActivityTaskSupervisor.realStartActivityLocked
  -> ClientLifecycleManager.scheduleTransactionItems -> IApplicationThread.scheduleTransaction
  -> ActivityThread.H.EXECUTE_TRANSACTION -> TransactionExecutor
  -> LaunchActivityItem -> handleLaunchActivity -> performLaunchActivity -> onCreate
  -> 生命周期状态推进 -> handleStartActivity -> onStart
  -> ResumeActivityItem -> handleResumeActivity -> performResumeActivity -> onResume
  -> WindowManager.addView -> ViewRootImpl.setView -> Choreographer traversal
  -> measure / layout / draw -> BLAST / SurfaceFlinger -> 实际呈现
```

源码：[ActivityStarter.java:837](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#837)；[ActivityTaskSupervisor.java:1171](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#1171)；[ActivityTaskSupervisor.java:809](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#809)；[ActivityThread.java:4414](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#4414)。

该图是普通前台冷启动的主要控制流，不是同步函数栈：Binder oneway、进程 fork 回连与主线程消息均有异步边界。复用已有 Activity 可以只发送 new-intent 事务而不执行 onCreate。onResume 也不是第一帧已经出现在屏幕上的证明。

**启动结果不是一个布尔成功值。** 先区分请求处理、创建新实例与进入 resumed。

| 场景 | 典型内部结果 | 应用端观察 |
|---|---|---|
| 解析/类信息失败 | START_INTENT_NOT_RESOLVED / START_CLASS_NOT_FOUND | Instrumentation 可转 ActivityNotFoundException |
| 权限/策略禁止 | 错误码、权限异常或 aborted 分支 | 无新 Activity，行为依检查点 |
| 顶部复用 | START_DELIVERED_TO_TOP | 新 Intent，不重建 |
| 已有任务前移 | START_TASK_TO_FRONT | 可见性/resume 变化 |
| 创建新实例 | START_SUCCESS | 仍需进程/事务/首帧 |
| 用户/包限制拦截 | 重定向到替代组件 | 最终组件可能不是原目标 |

公开 Activity.startActivity 返回 void；不能把 Starter 内部结果原样当它的返回值。callingUid 与 realCallingUid 分别记录代理与实际调用身份。quiet mode、包 suspended 等检查还可能替换目标，不能将原 URI grant 交给拦截页面。

以下为 [ActivityStarter.java:1404–1437](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#1404) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
        // can contain private information.
        Intent watchIntent = intent.cloneFilter();
        abort |= !mService.mController.activityStarting(watchIntent,
                aInfo.applicationInfo.packageName);
    } catch (RemoteException e) {
        mService.mController = null;
    }
}

final int sourceDisplayId =
        sourceRecord != null ? sourceRecord.getDisplayId() : INVALID_DISPLAY;
mInterceptor.setStates(userId, realCallingPid, realCallingUid, startFlags,
        callingPackage,
        callingFeatureId,
        sourceDisplayId);
if (mInterceptor.intercept(intent, rInfo, aInfo, resolvedType, inTask, inTaskFragment,
        callingPid, callingUid, checkedOptions, suggestedLaunchDisplayArea,
        request.componentSpecified)) {
    // activity start was intercepted, e.g. because the target user is currently in quiet
    // mode (turn off work) or the target application is suspended
    intent = mInterceptor.mIntent;
    rInfo = mInterceptor.mRInfo;
    aInfo = mInterceptor.mAInfo;
    resolvedType = mInterceptor.mResolvedType;
    inTask = mInterceptor.mInTask;
    callingPid = mInterceptor.mCallingPid;
    callingUid = mInterceptor.mCallingUid;
    checkedOptions = mInterceptor.mActivityOptions;

    // The interception target shouldn't get any permission grants
    // intended for the original destination
    intentGrants = null;
}

```

intercept 成功后重新取得 aInfo、rInfo、调用身份和 options，并清空 intentGrants。出现系统确认页时优先检查此阶段，而非认为 Activity 实例化错误。abort 路径给 resultTo 发送取消结果；不同检查点已有的服务端状态不同，不是每个失败都先创建 Activity 再删除。

### 3.3 核心类协作时序图

```text
调用方          ATMS/AMS                 Zygote           目标应用
  | startActivity  |                       |                 |
  |--------------->| 选择任务/检查启动策略   |                 |
  |<-- 同步结果 ----|                       |                 |
  |                |-- 需要时请求进程 ------>|--- fork ------->|
  |                |<------ attachApplication ----------------|
  |                |------- bindApplication ----------------->|
  |                |------- scheduleTransaction ------------->|
  |                |                       |        onCreate/start/resume
  |                |<------ IWindowSession add/relayout -------|
  |                |                       |           提交首帧 buffer
```

后台启动限制、用户/显示区、任务复用和窗口可见性会改变分支。同步返回启动结果与客户端生命周期执行要分开测量；不能将 Zygote fork 当成绘制的开始或完成点。源码：[ActivityStarter.java:1087](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#1087)。

### 3.4 进程间通信 (IPC) 总结

| 方向 | 接口 | 真实职责 |
|---|---|---|
| 应用 → system_server | `IActivityTaskManager` | startActivity 等任务/启动请求 |
| 应用 → AMS | `IActivityManager` | attachApplication 注册应用回调端、进程及组件请求 |
| system_server → 应用 | `IApplicationThread` | bindApplication、scheduleTransaction、组件调度 |
| 应用 → system_server | `IActivityClientController` | activityResumed/Paused/Stopped/Destroyed 等完成报告 |
| 应用 → WMS | `IWindowSession` | 窗口添加、relayout、绘制完成等 |
| system_server → Zygote | Unix domain socket | 进程创建参数与 PID 结果 |

`ApplicationThread` 是应用进程内 IApplicationThread 的 Binder **服务端 Stub**；系统持有它的代理。不能把“应用是业务客户端”套用到每个 Binder 接口方向。生命周期不再使用虚构的 `scheduleCreateActivity` 或旧版 `scheduleResumeActivity` 接口。

源码：[IApplicationThread.aidl:170](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/IApplicationThread.aidl#170)；[ActivityClient.java:61](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityClient.java#61)。

### 3.5 AMS 与 ActivityThread 完整通信流程

```text
调用方 Activity.startActivity -> startActivityForResult -> Instrumentation.execStartActivity
  -> IActivityTaskManager.startActivity（应用到 system_server 的 Binder）
  -> ATMS.startActivityAsUser -> ActivityStartController.obtainStarter(...).execute()
  -> ActivityStarter.execute -> executeRequest -> startActivityUnchecked -> startActivityInner
  -> Task.startActivityLocked / RootWindowContainer.resumeFocusedTasksTopActivities
  -> Task / TaskFragment resume 路径 -> ActivityTaskSupervisor.startSpecificActivity
       已有进程：realStartActivityLocked
       无进程：ATMS.startProcessAsync -> AMS / ProcessList -> Process.start
                -> ZygoteProcess.start -> Zygote socket -> fork / specialize
目标 ActivityThread.main -> attach -> IActivityManager.attachApplication（回连 AMS）
  -> AMS.attachApplicationLocked -> IApplicationThread.bindApplication
  -> ATMS LocalService.attachApplication -> RootWindowContainer.attachApplication
  -> ActivityTaskSupervisor.realStartActivityLocked
  -> ClientLifecycleManager.scheduleTransactionItems -> IApplicationThread.scheduleTransaction
  -> ActivityThread.H.EXECUTE_TRANSACTION -> TransactionExecutor
  -> LaunchActivityItem -> handleLaunchActivity -> performLaunchActivity -> onCreate
  -> 生命周期状态推进 -> handleStartActivity -> onStart
  -> ResumeActivityItem -> handleResumeActivity -> performResumeActivity -> onResume
  -> WindowManager.addView -> ViewRootImpl.setView -> Choreographer traversal
  -> measure / layout / draw -> BLAST / SurfaceFlinger -> 实际呈现
```

源码：[ActivityStarter.java:837](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#837)；[ActivityTaskSupervisor.java:1171](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#1171)；[ActivityTaskSupervisor.java:809](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#809)；[ActivityThread.java:4414](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#4414)。

`ActivityThread.attach(false, startSeq)` 调用的是 AMS 的 `attachApplication`，不是 `IActivityTaskManager.attachApplication`。AMS 将进程记录和 application thread 关联后发送 bind 请求，再交给 ATMS 的进程内接口尝试启动等待的 Activity。

`handleBindApplication` 建立 LoadedApk、Context 和 Application，并在正常非 restricted-backup 路径安装 ContentProvider，随后调用 Application.onCreate；Provider.onCreate 可以早于 Application.onCreate。不能在 Zygote 子进程初始化里直接创建 Application。

**PID / UID / startSeq 联合握手。** fork 结果回填与 attach Binder 可交错，PID 又会复用，不能只按 PID 接入 appThread。

以下为 [ActivityManagerService.java:5191–5225](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ActivityManagerService.java#5191) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
@GuardedBy("this")
private void attachApplicationLocked(@NonNull IApplicationThread thread,
        int pid, int callingUid, long startSeq) {
    // Find the application record that is being attached...  either via
    // the pid if we are running in multiple processes, or just pull the
    // next app record if we are emulating process with anonymous threads.
    ProcessRecord app;
    long startTime = SystemClock.uptimeMillis();
    long bindApplicationTimeMillis;
    long bindApplicationTimeNanos;
    if (pid != MY_PID && pid >= 0) {
        synchronized (mPidsSelfLocked) {
            app = mPidsSelfLocked.get(pid);
        }
        if (app != null && (app.getStartUid() != callingUid || app.getStartSeq() != startSeq)) {
            String processName = null;
            final ProcessRecord pending = mProcessList.mPendingStarts.get(startSeq);
            if (pending != null) {
                processName = pending.processName;
            }
            final String msg = "attachApplicationLocked process:" + processName
                    + " startSeq:" + startSeq
                    + " pid:" + pid
                    + " belongs to another existing app:" + app.processName
                    + " startSeq:" + app.getStartSeq();
            Slog.wtf(TAG, msg);
            // SafetyNet logging for b/131105245.
            EventLog.writeEvent(0x534e4554, "131105245", app.getStartUid(), msg);
            // If there is already an app occupying that pid that hasn't been cleaned up
            cleanUpApplicationRecordLocked(app, pid, false, false, -1,
                    true /*replacingPid*/, false /* fromBinderDied */);
            removePidLocked(pid, app);
            app = null;
        }
    } else {
```

AMS 将调用 UID 与 startSeq 同系统记录比较；失配先清理旧关联。UID/PID 来自 Binder 身份，startSeq 对应系统发起的启动请求，不是应用可凭空选择的授权凭据。

以下为 [ActivityManagerService.java:5231–5265](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ActivityManagerService.java#5231) 的连续源码节选；省略外围上下文，不是独立可编译程序。

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

pendingStarts 允许正确应用在进程结果回填前先 attach；未知记录则被丢弃/终止。之后注册 AppDeathRecipient，linkToDeath 与 bindApplication 都可能遇到死亡竞态；GC watcher 并不承担该职责。

以下为 [ActivityManagerService.java:5524–5548](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ActivityManagerService.java#5524) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java

        // See if the top visible activity is waiting to run in this process...
        if (com.android.server.am.Flags.expediteActivityLaunchOnColdStart()) {
            if (normalMode) {
                mAtmInternal.attachApplication(app.getWindowProcessController());
            }
        }
        updateOomAdjLocked(app, OOM_ADJ_REASON_PROCESS_BEGIN);
        checkTime(startTime, "attachApplicationLocked: after updateOomAdjLocked");

        if (!mConstants.mEnableWaitForFinishAttachApplication) {
            finishAttachApplicationInner(startSeq, callingUid, pid);
        }
        maybeSendBootCompletedLocked(app, isRestrictedBackupMode);
    } catch (Exception e) {
        // We need kill the process group here. (b/148588589)
        Slog.wtf(TAG, "Exception thrown during bind of " + app, e);
        app.resetPackageList(mProcessStats);
        app.unlinkDeathRecipient();
        app.killLocked("error during bind", ApplicationExitInfo.REASON_INITIALIZATION_FAILURE,
                true);
        handleAppDiedLocked(app, pid, false, true, false /* fromBinderDied */);
    }
}

```

expediteActivityLaunchOnColdStart 可提前通知 ATMS；mEnableWaitForFinishAttachApplication 控制是否等待绑定完成回执。oneway bindApplication 返回不等于 Application.onCreate 返回。绑定异常必须解除关联并清理失败进程，不能让半初始化状态继续服务。

### 3.6 ApplicationThread 详解

ApplicationThread 位于 ActivityThread 内部，继承 IApplicationThread.Stub。Binder 线程接收事务后，将生命周期工作交给主线程，而不是直接调用 Activity.onCreate。

真实实现摘录：

```java
@Override
public void scheduleTransaction(ClientTransaction transaction) throws RemoteException {
    ActivityThread.this.scheduleTransaction(transaction);
}
```

`ClientTransactionHandler.scheduleTransaction` 先 `preExecute`，再发送 `H.EXECUTE_TRANSACTION`。主线程 Handler 将 `ClientTransaction` 交给 `TransactionExecutor.execute`，执行事务项并协调前置/后置生命周期状态；不存在 `CreateActivityData`、`ActivityTransaction.traverse()` 或统一的 `CREATE_ACTIVITY` 整数列表。

服务端在 `realStartActivityLocked` 构造 `LaunchActivityItem`，根据 andResume 和可见性选取 `ResumeActivityItem`、`PauseActivityItem` 或 `StopActivityItem`，并通过 `scheduleTransactionItems` 投递。批处理和立即派发是 ClientLifecycleManager 的调度策略，不能假定每一生命周期都对应一个单独 Binder 消息。

源码：[ClientTransactionHandler.java:57](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ClientTransactionHandler.java#57)；[TransactionExecutor.java:72](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/TransactionExecutor.java#72)；[ActivityTaskSupervisor.java:1050](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#1050)。

**LaunchActivityItem 的三阶段不是三个生命周期。** 构造参数携带 token、组件、全局/override 配置、设备/显示、保存状态、待投递结果与 Intent、TaskFragment 和 ActivityWindowInfo。它们构成启动快照，不能用任意当前全局配置覆盖。

以下为 [LaunchActivityItem.java:202–232](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/LaunchActivityItem.java#202) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java

@Override
public void preExecute(@NonNull ClientTransactionHandler client) {
    client.countLaunchingActivities(1);
    client.updateProcessState(mProcState, false);
    CompatibilityInfo.applyOverrideIfNeeded(mCurConfig, mDisplayId);
    CompatibilityInfo.applyOverrideIfNeeded(mOverrideConfig, mDisplayId);
    client.updatePendingConfiguration(mCurConfig);
    if (mActivityClientController != null) {
        ActivityClient.setActivityClientController(mActivityClientController);
    }
}

@Override
public void execute(@NonNull ClientTransactionHandler client,
        @NonNull PendingTransactionActions pendingActions) {
    Trace.traceBegin(TRACE_TAG_ACTIVITY_MANAGER, "activityStart");
    final ActivityClientRecord r = new ActivityClientRecord(mActivityToken, mIntent, mIdent,
            mInfo, mOverrideConfig, mReferrer, mVoiceInteractor, mState, mPersistentState,
            mPendingResults, mPendingNewIntents, mSceneTransitionInfo, mIsForward,
            mProfilerInfo, client, mAssistToken, mShareableActivityToken, mLaunchedFromBubble,
            mTaskFragmentToken, mInitialCallerInfoAccessToken, mActivityWindowInfo, mDisplayId);
    client.handleLaunchActivity(r, pendingActions, mDeviceId, null /* customIntent */);
    Trace.traceEnd(TRACE_TAG_ACTIVITY_MANAGER);
}

@Override
public void postExecute(@NonNull ClientTransactionHandler client,
        @NonNull PendingTransactionActions pendingActions) {
    client.countLaunchingActivities(-1);
}
```

preExecute 增加 launching 计数、更新进程状态/pending configuration、缓存 ActivityClientController，不创建 View。execute 建立 ActivityClientRecord 并调用 handleLaunchActivity；postExecute 平衡 launching 计数，不代表首帧或 resume 完成报告。

应用 PendingTransactionActions 用于在本事务状态推进间传递恢复/onPostCreate 等待办，区别于 system_server 的 pending transaction map；二者并非同一个队列。

### 3.7 ApplicationThread 与 ActivityThread.H 交互

```text
system_server: ClientLifecycleManager -> ClientTransaction.schedule
  -- IApplicationThread.scheduleTransaction --> 应用 Binder 线程
  -> ActivityThread.ApplicationThread.scheduleTransaction
  -> ClientTransactionHandler.scheduleTransaction
     -> transaction.preExecute(this)
     -> sendMessage(ActivityThread.H.EXECUTE_TRANSACTION, transaction)
  -- 主线程消息 --> ActivityThread.H.handleMessage
  -> mTransactionExecutor.execute(transaction)
  -> executeTransactionItems / 具体 ClientTransactionItem
```

`preExecute` 用于事务到达时的预处理，不代表允许 Binder 线程执行 View 操作。耗时的 Activity 生命周期仍会阻塞主线程并推迟后续事务与输入处理。

源码：[ClientTransaction.java:243](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/ClientTransaction.java#243)；[ClientTransactionHandler.java:57](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ClientTransactionHandler.java#57)。

**服务端何时真正发 Binder。** ClientLifecycleManager 按 client.asBinder 聚合，不是每次 scheduleTransactionItems 都已经送达应用。

以下为 [ClientLifecycleManager.java:144–170](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ClientLifecycleManager.java#144) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
boolean scheduleTransactionItems(@NonNull IApplicationThread client,
        boolean shouldDispatchImmediately,
        @NonNull ClientTransactionItem... items) {
    // Wait until RootWindowContainer#performSurfacePlacementNoTrace to dispatch all pending
    // transactions at once.
    final ClientTransaction clientTransaction = getOrCreatePendingTransaction(client);

    final int size = items.length;
    for (int i = 0; i < size; i++) {
        clientTransaction.addTransactionItem(items[i]);
    }

    return onClientTransactionItemScheduled(clientTransaction, shouldDispatchImmediately);
}

/** Executes all the pending transactions. */
void dispatchPendingTransactions() {
    if (mPendingTransactions.isEmpty()) {
        return;
    }
    Trace.traceBegin(Trace.TRACE_TAG_WINDOW_MANAGER, "clientTransactionsDispatched");
    final int size = mPendingTransactions.size();
    for (int i = 0; i < size; i++) {
        final ClientTransaction transaction = mPendingTransactions.valueAt(i);
        scheduleTransaction(transaction);
    }
    mPendingTransactions.clear();
```

窗口 layout deferred/scheduled/in-progress 时可延迟到 surface placement 统一派发，以协调配置、生命周期与窗口变化。

以下为 [ClientLifecycleManager.java:217–241](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ClientLifecycleManager.java#217) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
private boolean onClientTransactionItemScheduled(
        @NonNull ClientTransaction clientTransaction,
        boolean shouldDispatchImmediately) {
    if (shouldDispatchImmediately || shouldDispatchPendingTransactionsImmediately()) {
        // Dispatch the pending transaction immediately.
        mPendingTransactions.remove(clientTransaction.getClient().asBinder());
        return scheduleTransaction(clientTransaction);
    }
    return true;
}

/** Must only be called with WM lock. */
private boolean shouldDispatchPendingTransactionsImmediately() {
    if (mWms == null) {
        return true;
    }
    // Do not dispatch when
    // 1. Layout deferred.
    // 2. Layout requested.
    // 3. Layout in process.
    // The pending transactions will be dispatched during layout in
    // RootWindowContainer#performSurfacePlacementNoTrace.
    return !mWms.mWindowPlacerLocked.isLayoutDeferred()
            && !mWms.mWindowPlacerLocked.isTraversalScheduled()
            && !mWms.mWindowPlacerLocked.isInLayout();
```

立即发送的 RemoteException 可反馈给调用者；入 pending map 成功不保证日后送达。launch 路径强制立即派发以发现死亡，compatibility 分支还可先 flush 该进程已有 pending 事务。

**客户端状态推进。**

以下为 [TransactionExecutor.java:94–108](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/TransactionExecutor.java#94) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
@VisibleForTesting
public void executeTransactionItems(@NonNull ClientTransaction transaction) {
    final List<ClientTransactionItem> items = transaction.getTransactionItems();
    final int size = items.size();
    for (int i = 0; i < size; i++) {
        final ClientTransactionItem item = items.get(i);
        if (item.isActivityLifecycleItem()) {
            executeLifecycleItem(transaction, (ActivityLifecycleItem) item);
        } else {
            executeNonLifecycleItem(transaction, item,
                    shouldExcludeLastLifecycleState(items, i));
        }
    }
}

```

生命周期项先推进到目标前一状态，再执行最终项；非生命周期项按其声明补齐前后状态。Launch 后重新查询记录，预销毁 token 要跳过，避免晚到请求复活 Activity。

以下为 [TransactionExecutor.java:114–137](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/TransactionExecutor.java#114) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
if (token != null && r == null
        && mTransactionHandler.getActivitiesToBeDestroyed().containsKey(token)) {
    // The activity has not been created but has been requested to destroy, so all
    // transactions for the token are just like being cancelled.
    Slog.w(TAG, "Skip pre-destroyed transaction item:\n" + item);
    return;
}

if (DEBUG_RESOLVER) Slog.d(TAG, tId(transaction) + "Resolving callback: " + item);
final int postExecutionState = item.getPostExecutionState();

if (item.shouldHaveDefinedPreExecutionState()) {
    final int closestPreExecutionState = mHelper.getClosestPreExecutionState(r,
            postExecutionState);
    if (closestPreExecutionState != UNDEFINED) {
        cycleToPath(r, closestPreExecutionState, transaction);
    }
}

item.execute(mTransactionHandler, mPendingActions);

item.postExecute(mTransactionHandler, mPendingActions);
if (r == null) {
    // Launch activity request will create an activity record.
```

executor 异常会记录事务信息并传播，不自动吞掉后继续；应结合具体 Activity/Application 异常定位。

### 3.8 关键时序图：ApplicationThread 生命周期回调

```text
服务端 LaunchActivityItem + 目标生命周期 item
  -> 客户端 TransactionExecutor
     -> LaunchActivityItem.execute -> handleLaunchActivity -> performLaunchActivity
          创建 Activity / attach PhoneWindow / onCreate
     -> 补齐 ON_START 状态 -> handleStartActivity -> onStart
     -> ResumeActivityItem.execute -> handleResumeActivity -> onResume
     -> ResumeActivityItem.postExecute -> ActivityClient.activityResumed
        -- IActivityClientController --> ActivityClientController.activityResumed
```

服务端下发请求和客户端上报完成是两条方向相反的接口。普通前台启动终态是 RESUMED；不可见启动、复用、重建、异常退出不能套用同一顺序。

源码：[LaunchActivityItem.java:216](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/LaunchActivityItem.java#216)；[ResumeActivityItem.java:79](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/ResumeActivityItem.java#79)。

**realStartActivityLocked 的等待与失败不是一回事。**

以下为 [ActivityTaskSupervisor.java:809–841](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#809) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
boolean realStartActivityLocked(ActivityRecord r, WindowProcessController proc,
        boolean andResume, boolean checkConfig) throws RemoteException {

    if (!mRootWindowContainer.allPausedActivitiesComplete()) {
        // While there are activities pausing we skipping starting any new activities until
        // pauses are complete. NOTE: that we also do this for activities that are starting in
        // the paused state because they will first be resumed then paused on the client side.
        ProtoLog.v(WM_DEBUG_STATES,
                "realStartActivityLocked: Skipping start of r=%s some activities pausing...",
                r);
        return false;
    }

    final Task task = r.getTask();
    if (andResume) {
        // Try pausing the existing resumed activity in the Task if any.
        if (task.pauseActivityIfNeeded(r, "realStart")) {
            return false;
        }
        final TaskFragment taskFragment = r.getTaskFragment();
        if (taskFragment != null && taskFragment.getResumedActivity() != null) {
            if (taskFragment.startPausing(mUserLeaving, false /* uiSleeping */, r,
                    "realStart")) {
                return false;
            }
        }
    }

    final Task rootTask = task.getRootTask();
    beginDeferResume();
    // The LaunchActivityItem also contains process configuration, so the configuration change
    // from WindowProcessController#setProcess can be deferred. The major reason is that if
    // the activity has FixedRotationAdjustments, it needs to be applied with configuration.
```

等待 pause 完成时可暂时返回 false。进入真实启动后，beginDeferResume 与 pauseConfigurationDispatch 抑制重复恢复和配置分发，finally 要成对释放；compatibility 可将 andResume 改为 false。

**死亡与有限重试。** tryRealStartActivityInner 检查 hasThread，构造 launch/终态 item 并要求立即投递，用 RemoteException 表示失败。

以下为 [ActivityTaskSupervisor.java:925–948](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#925) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
    }

    final RemoteException e = tryRealStartActivityInner(
            task, r, proc, activityClientController, andResume);
    if (e != null) {
        if (r.launchFailed) {
            // This is the second time we failed -- finish activity and give up.
            Slog.e(TAG, "Second failure launching "
                    + r.intent.getComponent().flattenToShortString() + ", giving up", e);
            proc.appDied("2nd-crash");
            r.finishIfPossible("2nd-crash", false /* oomAdj */);
            return false;
        }

        // This is the first time we failed -- restart process and
        // retry.
        r.launchFailed = true;
        r.detachFromProcess();
        throw e;
    }
} finally {
    endDeferResume();
    proc.resumeConfigurationDispatch();
}
```

第一次失败设置 launchFailed、脱离进程后抛出；第二次则结束 Activity 并放弃，而不是无限重试。

以下为 [ActivityTaskSupervisor.java:1171–1200](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#1171) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
void startSpecificActivity(ActivityRecord r, boolean andResume, boolean checkConfig) {
    // Is this activity's application already running?
    final WindowProcessController wpc =
            mService.getProcessController(r.processName, r.getUid());

    boolean knownToBeDead = false;
    if (wpc != null && wpc.hasThread()) {
        try {
            realStartActivityLocked(r, wpc, andResume, checkConfig);
            return;
        } catch (RemoteException e) {
            Slog.w(TAG, "Exception when starting activity "
                    + r.intent.getComponent().flattenToShortString(), e);
        }

        // If a dead object exception was thrown -- fall through to
        // restart the application.
        knownToBeDead = true;
        // Remove the process record so it won't be considered as alive.
        mService.mProcessNames.remove(wpc.mName, wpc.mUid);
        mService.mProcessMap.remove(wpc.getPid());
    } else if (ActivityTaskManagerService.isSdkSandboxActivityIntent(
            mService.mContext, r.intent)) {
        Slog.e(TAG, "Abort sandbox activity launching as no sandbox process to host it.");
        r.finishIfPossible("No sandbox process for the activity", false /* oomAdj */);
        r.launchFailed = true;
        r.detachFromProcess();
        return;
    }

```

startSpecificActivity 捕获死亡后移除旧 WPC 的映射并请求创建进程。SDK sandbox Activity 无宿主时明确终止，不能按普通应用任意新建宿主。成功后按 andResume/可见性设置 RESUMED、PAUSED 或 STOPPING，再进行进程状态更新。

### 3.9 ViewRootImpl 衔接流程

```text
performLaunchActivity
  -> Activity.attach：创建 PhoneWindow，关联 Context、token、WindowManager
  -> Activity.onCreate -> setContentView -> PhoneWindow.installDecor
       generateDecor + generateLayout -> android.R.id.content
  -> 生命周期进入 onStart / onResume
handleResumeActivity
  -> 满足可见性、未结束且窗口未添加等条件时 wm.addView(decor, layoutParams)
  -> WindowManagerGlobal.addView -> new ViewRootImpl -> root.setView
  -> requestLayout -> scheduleTraversals -> Choreographer traversal callback
  -> performTraversals：测量、窗口 relayout、布局、绘制（按实际条件执行）
```

`setContentView` 只建立内容树，不直接创建 ViewRootImpl；`attach` 在 onCreate **之前**，不是 onResume 后。`Activity.makeVisible` 的补充添加条件是 `!mWindowAdded`，通常 handleResumeActivity 已添加窗口，再将 DecorView 置为 VISIBLE。

首帧要经过 RenderThread/BLAST 的 buffer 提交及 SurfaceFlinger 呈现；`draw` 返回不是显示器已显示的时刻。源码：[ActivityThread.java:5997](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#5997)；[Activity.java:7476](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Activity.java#7476)；[ViewRootImpl.java:3307](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#3307)。

### 3.10 PhoneWindow 详解

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PhoneWindow 详解                                   │
└─────────────────────────────────────────────────────────────────────────────┘

PhoneWindow 是 普通 Activity 使用的 Window 实现类，负责：
- 管理 Activity 的顶层视图 (DecorView)
- 应用窗口装饰与系统栏外观请求（系统栏窗口本身由 SystemUI 管理）
- 内容区域的布局管理
```

#### 3.10.1 PhoneWindow 创建时机

`performLaunchActivity` 先建立 Activity 的 Context，再经 `Instrumentation.newActivity`（内部尊重 AppComponentFactory）创建实例，接着调用 Activity.attach，最后触发 onCreate。PhoneWindow 在 attach 内创建，窗口 token 来自服务端，不由 setContentView 生成。

```text
createBaseContextForActivity -> Instrumentation.newActivity
 -> Activity.attach -> new PhoneWindow(this, window, activityConfigCallback)
 -> Instrumentation.callActivityOnCreate
```

完整 attach 参数较多，包含 Instrumentation、token、Application、配置和 ActivityWindowInfo 等，不能把省略参数的教学调用当成可编译源码。源码：[Activity.java:9201](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Activity.java#9201)；[ActivityThread.java:4414](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#4414)。

#### 3.10.2 mContentParent 初始化

```text
Activity.setContentView -> PhoneWindow.setContentView
  mContentParent == null -> installDecor
    mDecor == null -> generateDecor
    mContentParent == null -> generateLayout(mDecor)
      根据 features、主题和窗口形态选择模板
      加入 decor 内容 -> findViewById(ID_ANDROID_CONTENT)
  普通非 content-transition 路径 -> 清理旧内容并 inflate 新布局
  通知 Window.Callback.onContentChanged
```

`mContentParent` 是内容容器而非 DecorView 本身。带 FEATURE_CONTENT_TRANSITIONS 的路径可用 Scene/TransitionManager 替换内容，不能无条件 removeAllViews；AppCompat 还会叠加自己的 sub-decor，不能将其实现归为 AOSP PhoneWindow。

源码：[PhoneWindow.java:558](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/policy/PhoneWindow.java#558)；[PhoneWindow.java:2921](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/policy/PhoneWindow.java#2921)。

#### 3.10.3 DecorView 什么时候添加到 WindowManager

`handleResumeActivity` 先 `performResumeActivity`，然后在窗口未初始化、Activity 未结束、将要可见等条件下准备 DecorView。若尚未添加且客户端可见，则设置 `mWindowAdded` 并 `wm.addView`；preserve-window、延迟客户端可见等分支可能复用或推迟添加。

`makeVisible` 不应重复添加已有窗口，其实际实现见：[Activity.java:7476](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Activity.java#7476)

```java
// Activity.makeVisible，保留核心条件；非完整 handleResumeActivity 实现。
if (!mWindowAdded) {
    ViewManager wm = getWindowManager();
    wm.addView(mDecor, getWindow().getAttributes());
    mWindowAdded = true;
}
mDecor.setVisibility(View.VISIBLE);
```

WindowManagerGlobal 创建 VRI，setView 注册服务端窗口并调度 traversal；是否实际绘制还受窗口可见性、Surface 和同步事务影响。源码：[ActivityThread.java:5997](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#5997)。

**三种可见性需要分别观察。**

| 层次 | 状态 | 含义 |
|---|---|---|
| ATMS 请求 | ActivityRecord visibility/resumed | 系统期望可见/恢复 |
| 客户端窗口 | mVisibleFromClient、mWindowAdded、DecorView visibility | 窗口注册与本地显隐 |
| 显示合成 | buffer、layer、fence、present | 图像真正进入显示管线 |

handleResumeActivity 可先以 INVISIBLE 添加 DecorView；preserve-window 可复用窗口，不能每次 resume 都 new VRI。

以下为 [ViewRootImpl.java:10190–10209](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#10190) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java

private int relayoutWindow(WindowManager.LayoutParams params, int viewVisibility,
        boolean insetsPending) throws RemoteException {
    int relayoutResult = 0;
    if (WindowManager.useClientSurface() && !mWindowLayout.isLocallyManaged()) {
        relayoutResult = updateSurfaceControl(viewVisibility);
    }
    final WindowConfiguration winConfig = getCompatWindowConfiguration();
    final int measuredWidth = mMeasuredWidth;
    final int measuredHeight = mMeasuredHeight;
    final boolean relayoutAsync;
    final StringBuilder relayoutSyncReason = Trace.isTagEnabled(Trace.TRACE_TAG_VIEW)
            ? new StringBuilder()
            : null;
    if (canRelayoutAsync(relayoutSyncReason)) {
        final InsetsState state = mInsetsController.getState();
        final Rect displayCutoutSafe = mTempRect;
        state.getDisplayCutoutSafe(displayCutoutSafe);
        mWindowLayout.computeFrames(mWindowAttributes.forRotation(winConfig.getRotation()),
                state, displayCutoutSafe, winConfig.getBounds(), winConfig.getWindowingMode(),
```

client-surface 仅在对应开关且非 locally-managed 窗口更新。frame、Insets 与 syncSeqId 等影响同步/异步 relayout 的选择，不能将其视为每帧请求 WMS 分配 Surface。

以下为 [ViewRootImpl.java:3065–3090](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#3065) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
void updateBlastSurfaceIfNeeded() {
    if (mBlastBufferQueue != null && mBlastBufferQueue.isSameSurfaceControl(mSurfaceControl)) {
        mBlastBufferQueue.update(mSurfaceControl,
            mSurfaceSize.x, mSurfaceSize.y,
            mWindowAttributes.format);
        return;
    }

    // If the SurfaceControl has been updated, destroy and recreate the BBQ to reset the BQ and
    // BBQ states.
    if (mBlastBufferQueue != null) {
        mBlastBufferQueue.destroy();
    }
    mBlastBufferQueue = new BLASTBufferQueue(mTag, true /* updateDestinationFrame */);
    // If we create and destroy BBQ without recreating the SurfaceControl, we can end up
    // queuing buffers on multiple apply tokens causing out of order buffer submissions. We
    // fix this by setting the same apply token on all BBQs created by this VRI.
    mBlastBufferQueue.setApplyToken(mBbqApplyToken);
    mBlastBufferQueue.update(mSurfaceControl, mSurfaceSize.x, mSurfaceSize.y,
            mWindowAttributes.format);
    mBlastBufferQueue.setTransactionHangCallback(sTransactionHangCallback);

    Surface blastSurface;

    blastSurface = mBlastBufferQueue.createSurfaceWithHandle();
    // Only call transferFrom if the surface has changed to prevent inc the generation ID and
```

BLAST 更新缓冲尺寸/格式并提供 Surface 的 producer 端。客户端 draw、BLAST transaction 和服务端绘制同步共同决定首次展示，不由 onResume 单独决定。

| 完成点 | 可确认 | 不能推断 |
|---|---|---|
| 启动请求返回 | 同步结果 | 目标已经创建 |
| Application.onCreate | 初始化阶段通过 | Activity 已显示 |
| onResume | 生命周期回调完成 | 首帧 present |
| addWindow 成功 | token/注册通过 | 有可显示 buffer |
| buffer/BLAST 提交 | 图像交付管线 | 显示器已呈现 |
| present fence / frame timeline | 对应帧呈现时序 | 网络内容全部加载 |

排查黑屏要区分无窗口、无有效 Surface、无 buffer、fence 等待、layer 不可见和转场未完成，不能只给 onResume 加延时。

#### 3.10.4 Activity.attach() 详解

`attach` 是框架内部初始化边界，而非应用覆写的生命周期回调。主要职责依次包括绑定基础 Context、关联 fragments 与 UI 线程、创建 PhoneWindow、设置 Window callback/布局 inflater factory、记录 ActivityThread/Instrumentation/token/Application/Intent/组件信息，并配置窗口参数。

```text
attachBaseContext(context)
 -> mUiThread = Thread.currentThread()
 -> mWindow = new PhoneWindow(this, window, activityConfigCallback)
 -> WindowControllerCallback / Callback / OnWindowDismissedCallback
 -> mMainThread / mInstrumentation / mToken / mApplication / mIntent 等
 -> softInputMode / uiOptions / WindowManager / container
 -> mWindowManager = mWindow.getWindowManager()
```

`uiOptions` 不是窗口标题，`setContentView` 也不在 attach 内执行。已有 window 参数用于窗口保留等流程；不能在 onCreate 之后再用已移除的 PolicyManager 覆盖 mWindow。源码：[Activity.java:9201](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Activity.java#9201)。

#### 3.10.5 完整流程总结

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                  Activity 创建与窗口初始化完整流程                           │
└─────────────────────────────────────────────────────────────────────────────┘

ActivityThread.performLaunchActivity()
       │
       ├──► 1. 创建 Activity 实例（反射）
       │        Activity activity = mInstrumentation.newActivity(...)
       │
       ├──► 2. 调用 Activity.attach()
       │        │
       │        ├──► 创建 PhoneWindow
       │        │        mWindow = new PhoneWindow(this, ...)
       │        │
       │        ├──► 设置 WindowManager
       │        │        mWindow.setWindowManager(...)
       │        │
       │        └──► 绑定 UI 线程
       │                 mUiThread = Thread.currentThread()
       │
       ├──► 3. 调用 Activity.onCreate()
       │        │
       │        └──► setContentView(layoutResID)
       │                 │
       │                 ├──► PhoneWindow.setContentView()
       │                 │
       │                 ├──► installDecor()
       │                 │        │
       │                 │        ├──► generateDecor() → 创建 DecorView
       │                 │        │
       │                 │        └──► generateLayout() → 初始化 mContentParent
       │                 │
       │                 └──► mLayoutInflater.inflate(layoutResID, mContentParent)
       │
       ├──► 4. 调用 Activity.onStart()
       │
       └──► 5. 调用 Activity.onResume()
                │
                └──► ActivityThread.handleResumeActivity()
                         │
                         └──► WindowManager.addView(decor, params)
                                  │
                                  ├──► 创建 ViewRootImpl
                                  │
                                  └──► ViewRootImpl.performTraversals()
                                           │
                                           ├──► measure()
                                           ├──► layout()
                                           └──► draw()
                                                   │
                                                   ▼
                                             屏幕显示 ✓
```

### 3.11 完整时序图 (AMS → AT → ViewRootImpl)

```text
调用方 Activity.startActivity -> startActivityForResult -> Instrumentation.execStartActivity
  -> IActivityTaskManager.startActivity（应用到 system_server 的 Binder）
  -> ATMS.startActivityAsUser -> ActivityStartController.obtainStarter(...).execute()
  -> ActivityStarter.execute -> executeRequest -> startActivityUnchecked -> startActivityInner
  -> Task.startActivityLocked / RootWindowContainer.resumeFocusedTasksTopActivities
  -> Task / TaskFragment resume 路径 -> ActivityTaskSupervisor.startSpecificActivity
       已有进程：realStartActivityLocked
       无进程：ATMS.startProcessAsync -> AMS / ProcessList -> Process.start
                -> ZygoteProcess.start -> Zygote socket -> fork / specialize
目标 ActivityThread.main -> attach -> IActivityManager.attachApplication（回连 AMS）
  -> AMS.attachApplicationLocked -> IApplicationThread.bindApplication
  -> ATMS LocalService.attachApplication -> RootWindowContainer.attachApplication
  -> ActivityTaskSupervisor.realStartActivityLocked
  -> ClientLifecycleManager.scheduleTransactionItems -> IApplicationThread.scheduleTransaction
  -> ActivityThread.H.EXECUTE_TRANSACTION -> TransactionExecutor
  -> LaunchActivityItem -> handleLaunchActivity -> performLaunchActivity -> onCreate
  -> 生命周期状态推进 -> handleStartActivity -> onStart
  -> ResumeActivityItem -> handleResumeActivity -> performResumeActivity -> onResume
  -> WindowManager.addView -> ViewRootImpl.setView -> Choreographer traversal
  -> measure / layout / draw -> BLAST / SurfaceFlinger -> 实际呈现
```

源码：[ActivityStarter.java:837](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#837)；[ActivityTaskSupervisor.java:1171](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#1171)；[ActivityTaskSupervisor.java:809](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#809)；[ActivityThread.java:4414](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#4414)。

### 3.12 详细步骤

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

Instrumentation.execStartActivity 处理 ActivityMonitor、调用身份及 Intent 准备，然后经 ATMS Binder 发起启动。`callingFeatureId` 等真实参数不能从旧签名中省掉后声称源码可编译；`checkStartActivityResult(result, intent)` 在返回后检查结果，不存在先调用 `checkStartActivityResult(intent, who)` 的重载。

源码：[Instrumentation.java:1973](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Instrumentation.java#1973)。

#### Step 3: ActivityTaskManagerService (ATMS) 处理

ATMS 的 startActivity 接受 callingPackage、callingFeatureId 等调用信息，转 startActivityAsUser，在用户校验及请求配置后调用 ActivityStartController.obtainStarter(...).execute。返回 int 结果不是客户端已经完成生命周期的证明。

源码：[ActivityTaskManagerService.java:1257](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskManagerService.java#1257)。

#### Step 4: ActivityStarter 执行启动

execute / executeRequest 负责解析、检查来源与权限、后台启动策略及创建 ActivityRecord。通过 startActivityUnchecked 延后窗口布局、收集 transition，再由 startActivityInner 计算 flags、可复用任务、目标 task/display area 和 Activity 插入/复用行为。

源码：[ActivityStarter.java:1770](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#1770)。

**布局延期与失败清理。** 一次启动会修改 task、ActivityRecord、可见性与转场参与者。deferWindowLayout 防止布局观察到中间状态，不是暂停应用 UI 线程。

以下为 [ActivityStarter.java:1793–1813](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#1793) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
try {
    mService.deferWindowLayout();
    r.mTransitionController.collect(r);
    try {
        Trace.traceBegin(Trace.TRACE_TAG_WINDOW_MANAGER, "startActivityInner");
        result = startActivityInner(r, sourceRecord, voiceSession, voiceInteractor,
                startFlags, options, inTask, inTaskFragment, balVerdict,
                intentGrants, realCallingUid);
    } catch (Exception ex) {
        Slog.e(TAG, "Exception on startActivityInner", ex);
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_WINDOW_MANAGER);
        startedActivityRootTask = handleStartResult(r, options, result, isIndependentLaunch,
                remoteTransition, transition, allowlistStatus);
    }
} finally {
    mService.continueWindowLayout();
}
postStartActivityProcessing(r, result, startedActivityRootTask);

return result;
```

内层 finally 执行 handleStartResult，外层 finally 执行 continueWindowLayout，失败也不能永久保留 deferred 状态。

以下为 [ActivityStarter.java:1840–1861](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#1840) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
if (!ActivityManager.isStartResultSuccessful(result) || startedActivityRootTask == null) {
    // If we are not able to proceed, disassociate the activity from the task. Leaving an
    // activity in an incomplete state can lead to issues, such as performing operations
    // without a window container.
    if (mStartActivity.getTask() != null) {
        mStartActivity.finishIfPossible("startActivity", true /* oomAdj */);
    } else if (mStartActivity.getParent() != null) {
        mStartActivity.getParent().removeChild(mStartActivity);
    }

    // Root task should also be detached from display and be removed if it's empty.
    if (startedActivityRootTask != null && startedActivityRootTask.isAttached()
            && !startedActivityRootTask.hasActivity()
            && !startedActivityRootTask.isActivityTypeHome()
            && !startedActivityRootTask.mCreatedByOrganizer) {
        startedActivityRootTask.removeIfPossible("handleStartResult");
    }
    if (isIndependentLaunch
            && mService.getTransitionController().isShellTransitionsEnabled()) {
        transition.abort();
    }
    return null;
```

失败记录被结束或脱离父容器；空 root task 只有满足附着、非 Home、非 organizer 创建等条件才移除。独立 Shell transition 也要 abort，不能任意删除组织器任务。客户端可能还没创建 Activity，所以这不是等同于应用 finish 的简单逆操作。

#### Step 5: ActivityTaskSupervisor 调度与任务选择

旧 ActivityStackSupervisor 不存在于本 tag；正确类为 ActivityTaskSupervisor。但 startActivityUnchecked **属于 ActivityStarter**，不能仅替换类名。监督器的 startSpecificActivity 决定直接调用 realStartActivityLocked 还是请求新进程。

源码：[ActivityTaskSupervisor.java:1171](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java#1171)。

**Task 选择仍属于 Starter。**

以下为 [ActivityStarter.java:2015–2055](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityStarter.java#2015) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
int startActivityInner(final ActivityRecord r, ActivityRecord sourceRecord,
        IVoiceInteractionSession voiceSession, IVoiceInteractor voiceInteractor,
        int startFlags, ActivityOptions options, Task inTask,
        TaskFragment inTaskFragment, BalVerdict balVerdict,
        NeededUriGrants intentGrants, int realCallingUid) {
    setInitialState(r, options, inTask, inTaskFragment, startFlags, sourceRecord,
            voiceSession, voiceInteractor, balVerdict, realCallingUid);

    computeLaunchingTaskFlags();
    mIntent.setFlags(mLaunchFlags);

    // Get top task at beginning because the order may be changed when reusing existing task.
    final Task prevTopRootTask = mPreferredTaskDisplayArea.getFocusedRootTask();
    final Task prevTopTask = prevTopRootTask != null ? prevTopRootTask.getTopLeafTask() : null;
    // allow reusing bubbled tasks only if the source activity is bubbled.
    final boolean includeLaunchedFromBubble =
            sourceRecord != null && sourceRecord.getLaunchedFromBubble();
    final Task reusedTask = resolveReusableTask(includeLaunchedFromBubble);

    // If requested, freeze the task list
    if (mOptions != null && mOptions.freezeRecentTasksReordering()
            && mSupervisor.mRecentTasks.isCallerRecents(r.launchedFromUid)
            && !mSupervisor.mRecentTasks.isFreezeTaskListReorderingSet()) {
        mFrozeTaskList = true;
        mSupervisor.mRecentTasks.setFreezeTaskListReordering();
    }

    // Compute if there is an existing task that should be used for.
    final Task targetTask = reusedTask != null ? reusedTask : computeTargetTask();
    final boolean newTask = targetTask == null;
    mTargetTask = targetTask;

    computeLaunchParams(r, sourceRecord, targetTask);

    // Check if starting activity on given task or on a new task is allowed.
    int startResult = isAllowedToStart(r, newTask, targetTask);
    if (startResult != START_SUCCESS) {
        if (r.resultTo != null) {
            r.resultTo.sendResult(INVALID_UID, r.resultWho, r.requestCode, RESULT_CANCELED,
                    null /* data */, null /* callerToken */, null /* dataGrants */);
        }
```

- mLaunchFlags 是计算后的 flags，并写回 Intent。
- mPreferredTaskDisplayArea 体现候选显示区；source、requested display 与窗口模式会参与。
- reusedTask 不存在时，computeTargetTask 仍可能选择来源任务。
- newTask 取决于 targetTask 是否为空，不等于 NEW_TASK 位是否置位。
- isAllowedToStart 在选定落点后校验；解析成功不代表任意任务均允许承载。

recycleTask 区分仅前移、投递 Intent、清理后加入新实例；mAddingToTask 与 mDoResume 不能合并。多文档、singleInstancePerTask、bubble/跨显示不能套用全局栈顶模型。

#### Step 6: Task 与 TaskFragment 管理

旧 ActivityStack 的职责拆分到 Task、TaskFragment 等容器。ActivityStarter 调用目标 root Task.startActivityLocked，并经 RootWindowContainer.resumeFocusedTasksTopActivities 推进 resume；TaskFragment 管理其 resumed/pausing Activity 状态。

源码：[Task.java:5506](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/Task.java#5506)；[TaskFragment.java:1357](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/TaskFragment.java#1357)。

**暂停是异步协议。** TaskFragment 检查 pausing 状态，必要时等待客户端完成报告或超时。

以下为 [TaskFragment.java:1357–1392](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/TaskFragment.java#1357) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
final boolean resumeTopActivity(ActivityRecord prev, ActivityOptions options,
        boolean skipPause) {
    ActivityRecord next = topRunningActivity(true /* focusableOnly */);
    if (next == null || !next.canResumeByCompat()) {
        return false;
    }

    if (mWmService.mAppLockController != null
            && mWmService.mAppLockController.isActivityLockedByAppLockLocked(next)) {
        // The top activity is locked by App Lock. Instead of resuming it, intercept the resume
        // and show the App Lock overlay. This is the "just-in-time" locking mechanism, refer to
        // AppLockOverlayController.
        ProtoLog.d(WM_DEBUG_STATES, "resumeTopActivity: next activity %s is locked by App"
                + " Lock, launching overlay", next);

        mWmService.mAppLockController.addLockedByAppLockActivityOverlayLocked(next);
        return true;
    }

    if (!skipPause && !mRootWindowContainer.allPausedActivitiesComplete()) {
        // If we aren't skipping pause, then we have to wait for currently pausing activities.
        ProtoLog.v(WM_DEBUG_STATES, "resumeTopActivity: Skip resume: some activity pausing.");
        return false;
    }

    final TaskDisplayArea taskDisplayArea = getDisplayArea();
    // If the top activity is the resumed one, nothing to do.
    if (mResumedActivity == next && next.isState(RESUMED)
            && taskDisplayArea.allResumedActivitiesComplete()) {
        // Ensure the visibility gets updated before execute app transition.
        taskDisplayArea.ensureActivitiesVisible(null /* starting */, true /* notifyClients */);
        // Make sure we have executed any pending transitions, since there
        // should be nothing left to do at this point.
        executeAppTransition(options);

        // In a multi-resumed environment, like in a freeform device, the top
```

mResumedActivity/mPausingActivity 是服务端状态，不是客户端当前执行的方法指针。onPause 同步 I/O 可推迟后续启动；skipPause、多窗口与兼容策略又会改变等待。next 已 resumed 时仍可能更新可见性与执行转场，不能用是否重复 onResume 判断窗口工作是否发生。

#### Step 7: 创建 Application（如果需要）

handleBindApplication 经 LoadedApk.makeApplicationInner 创建/取得 Application，设置 mInitialApplication，正常路径安装 Provider，再调用 Instrumentation.callApplicationOnCreate。Application 的初始化要在 Binder 回连后由应用主线程完成。

源码：[ActivityThread.java:7974](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#7974)；[ActivityThread.java:8293](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#8293)。

**实例存在与绑定完成不同。**

以下为 [ActivityThread.java:8256–8283](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#8256) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java
long timestampApplicationOnCreateNs = 0;
try {
    // If the app is being launched for full backup or restore, bring it up in
    // a restricted environment with the base application class.
    app = data.info.makeApplicationInner(data.restrictedBackupMode, null);

    // Propagate autofill compat state
    app.setAutofillOptions(data.autofillOptions);

    // Propagate Content Capture options
    app.setContentCaptureOptions(data.contentCaptureOptions);
    if (data.contentCaptureOptions != null) {
        if (data.contentCaptureOptions.enableReceiver
                && !data.contentCaptureOptions.lite) {
            // Warm up the background thread when:
            // 1) app is launched with content capture enabled, and
            // 2) the app is NOT launched with content capture lite enabled.
            BackgroundThread.startIfNeeded();
        }
    }
    sendMessage(H.SET_CONTENT_CAPTURE_OPTIONS_CALLBACK, data.appInfo.packageName);

    mInitialApplication = app;
    final boolean updateHttpProxy;
    synchronized (this) {
        updateHttpProxy = mUpdateHttpProxyOnBind;
        // This synchronized block ensures that any subsequent call to updateHttpProxy()
        // will see a non-null mInitialApplication.
```

LoadedApk.makeApplicationInner 创建 Application 并 attach Context；Instrumentation.onException 可参与处理，否则转成初始化失败。对象非 null 不意味着 Provider 和 onCreate 已通过。

以下为 [ActivityThread.java:8288–8312](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#8288) 的连续源码节选；省略外围上下文，不是独立可编译程序。

```java

// don't bring up providers in restricted mode; they may depend on the
// app's custom Application class
if (!data.restrictedBackupMode) {
    if (!ArrayUtils.isEmpty(data.providers)) {
        installContentProviders(app, data.providers);
    }
}

// Do this after providers, since instrumentation tests generally start their
// test thread at this point, and we don't want that racing.
try {
    mInstrumentation.onCreate(data.instrumentationArgs);
}
catch (Exception e) {
    throw new RuntimeException(
        "Exception thrown in onCreate() of " + data.instrumentationName, e);
}
try {
    timestampApplicationOnCreateNs = SystemClock.uptimeNanos();
    mInstrumentation.callApplicationOnCreate(app);
} catch (Exception e) {
    timestampApplicationOnCreateNs = 0;
    if (!mInstrumentation.onException(app, e)) {
        throw new RuntimeException(
```

正常 Provider.onCreate 可早于 Application.onCreate，依赖全局状态时要遵守该初始化边界。restrictedBackupMode 的简化初始化也不能混为正常应用主线。

#### Step 8: 创建 Activity 实例

performLaunchActivity 使用 createBaseContextForActivity(r) 与 Instrumentation.newActivity，调用 Activity.attach 后再触发 onCreate。保存状态通过生命周期框架在适当阶段恢复，不存在此处 `activity.restoreState` 的通用 API；onStart 由事务状态推进触发而非在 performLaunchActivity 尾部直接调用。

源码：[ActivityThread.java:4414](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java#4414)。

#### Step 9: 创建 Window 和 View

Activity.attach 创建 PhoneWindow 并设置 WindowManager；应用在 onCreate 中按需 setContentView。两者不能合并为 attach 内自动调用 setContentView，之后也不能再调用 PolicyManager.makeNewWindow。

源码：[Activity.java:9201](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Activity.java#9201)。

#### Step 10: View 的绘制流程

```text
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

```text
应用 IActivityTaskManager.Proxy -> system_server ATMS.Stub
system_server IApplicationThread.Proxy -> 应用 ApplicationThread.Stub
应用 ActivityClient -> IActivityClientController -> ActivityClientController
```

一个进程可同时是不同接口的客户端和服务端。Activity 生命周期请求与完成回报不能画成同一个 ApplicationThread 双向调用。源码：[IApplicationThread.aidl:170](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/IApplicationThread.aidl#170)。

### 4.2 关键 AIDL 接口

- `IActivityTaskManager` - Activity 管理服务
- `IApplicationThread` - 应用线程回调
- `IWindowSession` - Window 会话管理

---

## 5. 生命周期回调

### 5.1 完整生命周期

```text
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

```text
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
   - 使用 Executor 或切到后台 dispatcher 的协程；普通主线程 Handler 不会使 I/O 变成后台工作

**按冷、暖、热启动拆成本。**

- 冷：无可用应用进程，fork/specialize → attach/bind → Provider/Application → Activity/窗口/首帧。
- 暖：进程可用但 Activity 或窗口需重建；有 Application 不代表已有目标页面。
- 热：已有实例/任务返回前台，可能只有 newIntent/resume 和可见性/转场，不执行 onCreate。
- 死亡后重试：含 Binder 清理与 pending start，不能与正常二次点击混合统计。

```bash
adb shell am start -W -n com.example.app/.MainActivity
adb shell dumpsys activity activities
adb shell dumpsys activity processes
adb shell dumpsys window windows
adb logcat -v threadtime -s ActivityTaskManager ActivityManager AndroidRuntime WindowManager
```

am start -W 不测量所有异步业务内容加载时间。优化要区分 Provider/Application、Activity、inflate、traversal、RenderThread 和 SF；把 onCreate 的同步重任务挪到 Provider.onCreate 并不减少启动成本。

| 症状 | 优先检查 |
|---|---|
| 无 ActivityRecord | 解析、权限、拦截、后台启动 |
| 无 application thread | Zygote、pending start、startSeq、attach |
| Application 卡住 | Provider、锁、同步 Binder、I/O |
| resumed 却无窗口 | token、可见性条件、addWindow |
| 有窗口但无首帧 | BLAST、buffer、同步事务、layer/fence |

这些是诊断命令与分析方法，不代表本次执行过设备验证。

### 6.2 启动模式详解

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `standard` | 每次创建新实例 | 默认模式 |
| `singleTop` | 如果栈顶是该 Activity，复用并调用 onNewIntent | 通知、消息 |
| `singleTask` | 栈内唯一，复用并清除其上所有 Activity | 主界面 |
| `singleInstance` | 独占一个任务栈 | 独立功能 |
| `singleInstancePerTask` | 实例只能作为任务根；允许按 NEW_DOCUMENT/MULTIPLE_TASK 等规则创建多任务实例 | 多文档/多任务 |

**案例：顶部详情页复用。** `Home → List → Detail(42)`，从 Detail 以 SINGLE_TOP 打开 84：

```kotlin
startActivity(Intent(this, DetailActivity::class.java).apply {
    putExtra("item_id", 84L)
    addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
})

override fun onNewIntent(intent: Intent) {
    super.onNewIntent(intent)
    setIntent(intent)
    showItem(intent.getLongExtra("item_id", -1L)) // 应用函数
}
```

setIntent 避免 Activity.intent 保留旧参数。目标不在顶部时，SINGLE_TOP 不会搜索全任务自动清栈。

**CLEAR_TOP 案例。** `Home → List → Detail → Editor` 返回 List：会清除其上页面；若 List 为 standard 且没有 SINGLE_TOP 等保留条件，List 自身也可能销毁重建。不能仅凭 CLEAR_TOP 推断一定收到 onNewIntent。

**NEW_TASK 案例。** NEW_TASK 会选择已有合适任务或新建；退出登录需要重置对应任务时可用 NEW_TASK | CLEAR_TASK，但这不是删除系统所有任务。用户、显示区和 document 模式仍会影响落点。

**singleInstancePerTask 案例。** 要求实例作为任务根，可按文档/多任务规则创建其他任务根实例；它不等同于 singleInstance 独占整个任务。

### 6.3 Intent Flags 常用组合

```java
// NEW_TASK：选择可复用任务或创建任务，不保证每次新建
intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

// CLEAR_TOP：定位已有目标并清除其上方；standard 目标可能销毁重建
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

- 固定基线：AOSP `android-17.0.0_r1`；本文各节给出真实函数链接。
- Android Developer Documentation
- 《Android Internals》

---

*本文档由 OpenClaw 自动生成*
