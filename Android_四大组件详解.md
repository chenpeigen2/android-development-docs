# Android 四大组件详解

> 作者：OpenClaw | 日期：2026-03-09

---

## 目录

1. [概述](#1-概述)
2. [Activity](#2-activity)
   - 2.1 [Activity 是什么](#21-activity-是什么)
   - 2.2 [Activity 生命周期](#22-activity-生命周期)
   - 2.3 [Activity 启动模式](#23-activity-启动模式)
   - 2.4 [Activity 任务栈](#24-activity-任务栈)
   - 2.5 [Activity 启动流程](#25-activity-启动流程)
   - 2.6 [Activity 常见问题](#26-activity-常见问题)
3. [Service](#3-service)
   - 3.1 [Service 是什么](#31-service-是什么)
   - 3.2 [Service 生命周期](#32-service-生命周期)
   - 3.3 [Service 类型](#33-service-类型)
   - 3.4 [Service 启动方式](#34-service-启动方式)
   - 3.5 [Service 与 Thread 区别](#35-service-与-thread-区别)
   - 3.6 [Service 常见问题](#36-service-常见问题)
4. [BroadcastReceiver](#4-broadcastreceiver)
   - 4.1 [BroadcastReceiver 是什么](#41-broadcastreceiver-是什么)
   - 4.2 [广播类型](#42-广播类型)
   - 4.3 [广播注册方式](#43-广播注册方式)
   - 4.4 [广播发送方式](#44-广播发送方式)
   - 4.5 [广播限制](#45-广播限制)
   - 4.6 [本地广播 LocalBroadcast](#46-本地广播-localbroadcast)
   - 4.7 [BroadcastReceiver 常见问题](#47-broadcastreceiver-常见问题)
5. [ContentProvider](#5-contentprovider)
   - 5.1 [ContentProvider 是什么](#51-contentprovider-是什么)
   - 5.2 [ContentProvider 原理](#52-contentprovider-原理)
   - 5.3 [ContentProvider 使用](#53-contentprovider-使用)
   - 5.4 [ContentProvider 核心方法](#54-contentprovider-核心方法)
   - 5.5 [ContentObserver 监听](#55-contentobserver-监听)
   - 5.6 [ContentProvider 常见问题](#56-contentprovider-常见问题)
6. [四大组件对比](#6-四大组件对比)
7. [进程间通信 IPC](#7-进程间通信-ipc)
8. [常见问题](#8-常见问题)
9. [知识体系总结](#9-知识体系总结)

---

## 1. 概述

Android 四大组件是 Android 应用的基石，它们分别是：Activity、Service、BroadcastReceiver 和 ContentProvider。每个组件都有其特定的职责和使用场景，理解它们的工作原理和相互关系，是掌握 Android 开发的关键。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         四大组件概览                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────┐│
  │    │  Activity   │    │   Service   │    │BroadcastRecv│    │ Content ││
  │    │             │    │             │    │             │    │Provider ││
  │    │   界面展示   │    │   后台服务   │    │   消息接收   │    │ 数据共享 ││
  │    └─────────────┘    └─────────────┘    └─────────────┘    └─────────┘│
  │           │                  │                  │                │      │
  │           ▼                  ▼                  ▼                ▼      │
  │    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────┐│
  │    │ 用户交互入口 │    │ 后台长期任务 │    │ 系统事件监听 │    │跨进程数据││
  │    │ 视图容器    │    │ 无界面运行   │    │ 应用间通信   │    │ 统一接口 ││
  │    └─────────────┘    └─────────────┘    └─────────────┘    └─────────┘│
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  共同特点：
  ─────────────────────────────────────────────────────────────────────────
  1. 都需要在 AndroidManifest.xml 中注册
  2. 都有独立的生命周期
  3. 都可以跨进程通信
  4. 都由系统管理（AMS/PMS）
```

---

## 2. Activity

### 2.1 Activity 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Activity 定义                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  官方定义：
  "An Activity is a single, focused thing that the user can do."

  核心职责：
  ─────────────────────────────────────────────────────────────────────────
  1. 提供用户界面（UI）的容器
  2. 处理用户交互事件
  3. 管理应用界面生命周期
  4. 作为应用入口点之一

  本质：
  ─────────────────────────────────────────────────────────────────────────
  - Activity 是一个 Context（继承自 ContextThemeWrapper）
  - Activity 是一个 Window 的容器
  - Activity 持有一个 DecorView（窗口根视图）
  - Activity 通过 PhoneWindow 管理视图

  层次结构：
  ─────────────────────────────────────────────────────────────────────────
  
  Activity
    └── Window (PhoneWindow)
          └── DecorView (FrameLayout)
                ├── StatusBar
                ├── TitleView (optional)
                └── ContentView (FrameLayout, id=content)
                      └── 用户布局
```

### 2.2 Activity 生命周期

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Activity 生命周期                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  完整生命周期：                                                         │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │    ┌──────────┐                                                        │
  │    │ onCreate │  ← 创建：初始化布局、变量                               │
  │    └────┬─────┘                                                        │
  │         │                                                              │
  │         ▼                                                              │
  │    ┌──────────┐                                                        │
  │    │ onStart  │  ← 可见：Activity 即将可见                              │
  │    └────┬─────┘                                                        │
  │         │                                                              │
  │         ▼                                                              │
  │    ┌──────────┐                                                        │
  │    │ onResume │  ← 可交互：获得焦点，可交互                              │
  │    └────┬─────┘                                                        │
  │         │        ┌─────────────────────────────────┐                   │
  │         │        │     Activity Running            │                   │
  │         └───────►│     (用户交互状态)               │                   │
  │                  └─────────────────────────────────┘                   │
  │         │                       │                                      │
  │         ▼                       ▼                                      │
  │    ┌──────────┐           ┌──────────┐                                │
  │    │ onPause  │  ◄────────│ 新Activity│  失去焦点                      │
  │    └────┬─────┘           └──────────┘                                │
  │         │                                                              │
  │         ▼                                                              │
  │    ┌──────────┐                                                        │
  │    │ onStop   │  ← 不可见：被其他 Activity 完全遮挡                     │
  │    └────┬─────┘                                                        │
  │         │                                                              │
  │         ▼                                                              │
  │    ┌──────────┐                                                        │
  │    │ onDestroy│  ← 销毁：释放资源                                       │
  │    └──────────┘                                                        │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         生命周期场景分析                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  场景1：正常启动
  ─────────────────────────────────────────────────────────────────────────
  onCreate → onStart → onResume

  场景2：正常退出
  ─────────────────────────────────────────────────────────────────────────
  onPause → onStop → onDestroy

  场景3：打开新Activity（新Activity完全遮挡）
  ─────────────────────────────────────────────────────────────────────────
  旧Activity: onPause → onStop
  新Activity: onCreate → onStart → onResume

  场景4：打开透明/对话框Activity（旧Activity部分可见）
  ─────────────────────────────────────────────────────────────────────────
  旧Activity: onPause（不会调用 onStop）
  新Activity: onCreate → onStart → onResume

  场景5：返回旧Activity
  ─────────────────────────────────────────────────────────────────────────
  从 onStop 恢复: onRestart → onStart → onResume
  从 onPause 恢复: onResume

  场景6：屏幕旋转
  ─────────────────────────────────────────────────────────────────────────
  onPause → onStop → onDestroy → onCreate → onStart → onResume
  （相当于销毁重建）

  场景7：按Home键
  ─────────────────────────────────────────────────────────────────────────
  onPause → onStop（不会 onDestroy）

  场景8：从最近任务返回
  ─────────────────────────────────────────────────────────────────────────
  onRestart → onStart → onResume
```

```java
/**
 * Activity 生命周期最佳实践
 */
public class MainActivity extends AppCompatActivity {
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // 初始化操作
        // - 布局加载完成
        // - 初始化变量
        // - 恢复状态（savedInstanceState）
    }
    
    @Override
    protected void onStart() {
        super.onStart();
        // Activity 即将可见
        // - 注册监听器
        // - 开始动画
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        // Activity 可交互
        // - 恢复暂停的操作
        // - 获取相机/传感器等独占资源
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        // Activity 失去焦点
        // - 保存未提交的数据
        // - 释放独占资源
        // - 不要执行耗时操作！
    }
    
    @Override
    protected void onStop() {
        super.onStop();
        // Activity 不可见
        // - 释放不需要的资源
        // - 取消网络请求
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Activity 即将销毁
        // - 释放所有资源
        // - 取消所有回调
    }
    
    @Override
    protected void onRestart() {
        super.onRestart();
        // Activity 从 stop 状态重新启动
    }
    
    // 保存状态
    @Override
    protected void onSaveInstanceState(@NonNull Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putString("key", "value");
    }
    
    // 恢复状态
    @Override
    protected void onRestoreInstanceState(@NonNull Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        String value = savedInstanceState.getString("key");
    }
}
```

### 2.3 Activity 启动模式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Activity 启动模式                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  1. standard（默认）                                                    │
  │  ─────────────────────────────────────────────────────────────────────── │
  │  每次启动都创建新实例，允许多个相同 Activity 实例                         │
  │                                                                         │
  │  任务栈：[A] → 启动 A → [A, A] → 启动 A → [A, A, A]                     │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  2. singleTop（栈顶复用）                                               │
  │  ─────────────────────────────────────────────────────────────────────── │
  │  如果目标 Activity 在栈顶，则复用，否则创建新实例                         │
  │                                                                         │
  │  情况1 - A 在栈顶：                                                     │
  │  任务栈：[A, B, A] → 启动 A → [A, B, A]（复用，调用 onNewIntent）        │
  │                                                                         │
  │  情况2 - A 不在栈顶：                                                   │
  │  任务栈：[A, B, C] → 启动 A → [A, B, C, A]（创建新实例）                 │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  3. singleTask（栈内复用）                                              │
  │  ─────────────────────────────────────────────────────────────────────── │
  │  整个系统中只存在一个实例，如果在栈中存在则复用并清除其上的所有 Activity  │
  │                                                                         │
  │  情况1 - A 已在栈中：                                                   │
  │  任务栈：[A, B, C, D] → 启动 A → [A]（清除 B, C, D，调用 onNewIntent）   │
  │                                                                         │
  │  情况2 - A 不在栈中：                                                   │
  │  任务栈：[B, C] → 启动 A → [B, C, A]（创建新实例）                       │
  │                                                                         │
  │  特点：                                                                 │
  │  - 可以指定 taskAffinity，在新任务栈中创建                               │
  │  - 常用于应用主界面                                                     │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  4. singleInstance（单实例）                                            │
  │  ─────────────────────────────────────────────────────────────────────── │
  │  整个系统中只存在一个实例，且独占一个任务栈                               │
  │                                                                         │
  │  任务栈1：[A, B, C] → 启动 D(singleInstance)                            │
  │  任务栈1：[A, B, C]                                                     │
  │  任务栈2：[D]（独占一个任务栈）                                          │
  │                                                                         │
  │  特点：                                                                 │
  │  - 独占一个任务栈                                                       │
  │  - 不会被其他 Activity 影响                                             │
  │  - 常用于系统级应用（如电话、闹钟）                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

```xml
<!-- AndroidManifest.xml 中配置 -->
<activity
    android:name=".MainActivity"
    android:launchMode="singleTask" />
    
<!-- 或使用 Intent Flags -->
Intent intent = new Intent(this, MainActivity.class);
intent.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);      // singleTop
intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);        // singleTask
intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);       // 清除目标之上的 Activity
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         常用 Intent Flags                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  FLAG_ACTIVITY_NEW_TASK        在新任务栈中启动                         │
  │  FLAG_ACTIVITY_SINGLE_TOP      栈顶复用（同 singleTop）                 │
  │  FLAG_ACTIVITY_CLEAR_TOP       清除目标之上的 Activity                  │
  │  FLAG_ACTIVITY_CLEAR_TASK      清除任务栈中所有 Activity                │
  │  FLAG_ACTIVITY_NO_HISTORY      不保留在任务栈中                         │
  │  FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS  不出现在最近任务列表               │
  │  FLAG_ACTIVITY_BROUGHT_TO_FRONT  与 NEW_TASK 配合使用                   │
  │  FLAG_ACTIVITY_REORDER_TO_FRONT  将已存在的 Activity 移到前台           │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Activity 任务栈

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Activity 任务栈（Task）                             │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  Task 是一组以栈（Back Stack）形式管理的 Activity 集合

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  后进先出（LIFO）：                                                     │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │    ┌─────────────┐                                                     │
  │    │ Activity C  │  ← 栈顶（当前显示）                                  │
  │    ├─────────────┤                                                     │
  │    │ Activity B  │                                                     │
  │    ├─────────────┤                                                     │
  │    │ Activity A  │  ← 栈底                                              │
  │    └─────────────┘                                                     │
  │                                                                         │
  │    按 Back 键：C 出栈 → 显示 B                                          │
  │    启动 D：D 入栈 → [A, B, C, D]                                        │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  taskAffinity（任务相关性）：
  ─────────────────────────────────────────────────────────────────────────
  - 定义 Activity 属于哪个任务栈
  - 默认 taskAffinity = 应用包名
  - 可以自定义 taskAffinity 创建新的任务栈

  <activity
      android:name=".MyActivity"
      android:taskAffinity="com.example.mytask" />
```

### 2.5 Activity 启动流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Activity 启动流程                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  应用进程：                    系统进程：                                │
  │                                                                         │
  │  Activity.startActivity()                                               │
  │         │                                                              │
  │         ▼                                                              │
  │  Instrumentation.execStartActivity()                                   │
  │         │                                                              │
  │         ▼                                                              │
  │  ActivityTaskManager.getService()                                      │
  │  .startActivity()  ───────────────────►  ATMS.startActivity()          │
  │                                               │                        │
  │                                               ▼                        │
  │                                         检查权限                       │
  │                                               │                        │
  │                                               ▼                        │
  │                                         解析 Intent                    │
  │                                               │                        │
  │                                               ▼                        │
  │                                         查找/创建目标进程               │
  │                                               │                        │
  │                                               ▼                        │
  │  ◄───────────────────────────────────────  ApplicationThread            │
  │         .scheduleTransaction()               .scheduleLaunchActivity()  │
  │         │                                                              │
  │         ▼                                                              │
  │  ActivityThread.handleLaunchActivity()                                  │
  │         │                                                              │
  │         ▼                                                              │
  │  ActivityThread.performLaunchActivity()                                 │
  │         │                                                              │
  │         ▼                                                              │
  │  1. 创建 Activity 实例                                                  │
  │  2. 创建 PhoneWindow                                                    │
  │  3. Activity.attach()                                                   │
  │  4. Activity.onCreate()                                                 │
  │  5. Activity.onStart()                                                  │
  │  6. Activity.onResume()                                                 │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  关键类：
  ─────────────────────────────────────────────────────────────────────────
  - ActivityTaskManagerService (ATMS)：管理 Activity 任务栈（Android 10+）
  - ActivityManagerService (AMS)：管理 Activity 生命周期
  - ApplicationThread：应用进程与系统进程通信的 Binder
  - ActivityThread：应用主线程，管理 Activity 生命周期
  - Instrumentation：Activity 启动的监控和拦截
```

### 2.6 Activity 常见问题

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Activity 常见问题                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  Q1: onSaveInstanceState 什么时候调用？
  ─────────────────────────────────────────────────────────────────────────
  A: 在 Activity 可能被系统销毁前调用：
     - 按 Home 键
     - 切换到其他应用
     - 屏幕旋转
     - 启动新 Activity
     
     注意：按 Back 键不会调用，因为这是用户主动退出

  Q2: onNewIntent 什么时候调用？
  ─────────────────────────────────────────────────────────────────────────
  A: 当 Activity 复用时调用（singleTop/singleTask/singleInstance）：
     - singleTop：Activity 在栈顶被复用
     - singleTask：Activity 在栈中被复用
     - singleInstance：Activity 被复用

  Q3: 如何避免屏幕旋转重建 Activity？
  ─────────────────────────────────────────────────────────────────────────
  A: 在 AndroidManifest.xml 中配置：
     android:configChanges="orientation|screenSize|keyboardHidden"

  Q4: Activity 如何传递大数据？
  ─────────────────────────────────────────────────────────────────────────
  A: Intent 传递数据有大小限制（约 1MB），大数据方案：
     - 使用单例/静态变量
     - 使用 EventBus/RxBus
     - 使用 ViewModel 共享数据
     - 持久化存储

  Q5: singleTask 和 singleInstance 区别？
  ─────────────────────────────────────────────────────────────────────────
  A: 
     - singleTask：可以在已有任务栈中，也可以创建新任务栈
     - singleInstance：必须独占一个新任务栈
```

---

## 3. Service

### 3.1 Service 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Service 定义                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  官方定义：
  "A Service is an application component that can perform long-running 
   operations in the background. It does not provide a user interface."

  核心职责：
  ─────────────────────────────────────────────────────────────────────────
  1. 执行后台长期运行的任务
  2. 不提供用户界面
  3. 独立于 Activity 的生命周期
  4. 可跨进程通信

  重要特点：
  ─────────────────────────────────────────────────────────────────────────
  - Service 默认在主线程执行（不是子线程！）
  - 耗时操作需要在 Service 内部创建子线程
  - Android 8.0+ 后台 Service 受限
  - 长时任务需要使用前台服务

  误区：
  ─────────────────────────────────────────────────────────────────────────
  ❌ Service 在子线程执行
  ✓ Service 在主线程执行，耗时操作需要自己开线程

  ❌ Service 可以无限后台运行
  ✓ Android 8.0+ 后台 Service 会被限制，很快被杀
```

### 3.2 Service 生命周期

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Service 生命周期                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  启动式 Service（startService）：                                       │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │    startService()                                                      │
  │         │                                                              │
  │         ▼                                                              │
  │    ┌──────────┐                                                        │
  │    │ onCreate │  ← 创建（只调用一次）                                   │
  │    └────┬─────┘                                                        │
  │         │                                                              │
  │         ▼                                                              │
  │    ┌──────────────┐                                                    │
  │    │onStartCommand│  ← 每次启动都调用                                  │
  │    └──────┬───────┘                                                    │
  │           │                                                            │
  │           │  多次 startService                                         │
  │           ▼                                                            │
  │    ┌──────────────┐                                                    │
  │    │onStartCommand│  ← 重复调用                                        │
  │    └──────┬───────┘                                                    │
  │           │                                                            │
  │           ▼                                                            │
  │    ┌───────────┐                                                       │
  │    │ onDestroy │  ← stopService() / stopSelf()                         │
  │    └───────────┘                                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  绑定式 Service（bindService）：                                        │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │    bindService()                                                       │
  │         │                                                              │
  │         ▼                                                              │
  │    ┌──────────┐                                                        │
  │    │ onCreate │  ← 创建                                                │
  │    └────┬─────┘                                                        │
  │         │                                                              │
  │         ▼                                                              │
  │    ┌──────────┐                                                        │
  │    │ onBind   │  ← 绑定，返回 IBinder                                  │
  │    └────┬─────┘                                                        │
  │         │                                                              │
  │         │  客户端使用服务                                               │
  │         │                                                              │
  │         ▼                                                              │
  │    ┌───────────┐                                                       │
  │    │ onUnbind  │  ← 所有客户端解绑                                     │
  │    └─────┬─────┘                                                       │
  │          │                                                             │
  │          ▼                                                             │
  │    ┌───────────┐                                                       │
  │    │ onDestroy │  ← 自动销毁                                           │
  │    └───────────┘                                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  混合模式（同时启动和绑定）：                                            │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │    onCreate → onStartCommand → onBind                                  │
  │                   ↑               ↑                                    │
  │            startService()      bindService()                           │
  │                                                                         │
  │    销毁条件：stopService() 且 所有客户端 unbindService()                │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Service 类型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Service 类型                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────────────────────────────────────────────────┐
  │     类型         │                      说明                                │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ Started Service  │ startService() 启动，独立运行                           │
  │                  │ 必须手动停止 stopSelf()                                 │
  │                  │ 适合：一次性任务                                        │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ Bound Service    │ bindService() 启动，与绑定者生命周期绑定                │
  │                  │ 所有客户端解绑后自动销毁                                │
  │                  │ 适合：IPC 通信、需要交互的任务                          │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ Foreground       │ startForeground() 显示通知                             │
  │ Service          │ 优先级高，不易被杀死                                    │
  │                  │ 适合：用户可感知的长时任务                              │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ Background       │ 后台运行，Android 8.0+ 受限                            │
  │ Service          │ 几分钟后被杀死                                          │
  │                  │ 不推荐使用                                              │
  └─────────────────┴─────────────────────────────────────────────────────────┘
```

### 3.4 Service 启动方式

```java
/**
 * 启动式 Service
 */
public class MyStartedService extends Service {
    
    @Override
    public void onCreate() {
        super.onCreate();
        // 初始化
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // 在子线程执行耗时操作
        new Thread(() -> {
            // 执行任务
            doWork();
            // 任务完成后停止
            stopSelf(startId);
        }).start();
        
        // 返回值说明：
        // START_STICKY: 被杀后重启，intent 为 null
        // START_NOT_STICKY: 被杀后不重启
        // START_REDELIVER_INTENT: 被杀后重启，重新传递 intent
        return START_STICKY;
    }
    
    @Override
    public void onDestroy() {
        super.onDestroy();
        // 释放资源
    }
    
    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;  // 启动式服务不需要绑定
    }
}

// 启动
Intent intent = new Intent(context, MyStartedService.class);
startService(intent);

// 停止
stopService(new Intent(context, MyStartedService.class));
// 或在 Service 内部调用 stopSelf()
```

```java
/**
 * 绑定式 Service
 */
public class MyBoundService extends Service {
    
    private final IBinder binder = new LocalBinder();
    
    public class LocalBinder extends Binder {
        MyBoundService getService() {
            return MyBoundService.this;
        }
    }
    
    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return binder;
    }
    
    // 暴露给客户端的方法
    public void doSomething() {
        // 业务逻辑
    }
}

// 客户端绑定
public class MainActivity extends AppCompatActivity {
    private MyBoundService service;
    private boolean bound = false;
    
    private ServiceConnection connection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            LocalBinder binder = (LocalBinder) service;
            MyBoundService.this.service = binder.getService();
            bound = true;
        }
        
        @Override
        public void onServiceDisconnected(ComponentName name) {
            bound = false;
        }
    };
    
    @Override
    protected void onStart() {
        super.onStart();
        Intent intent = new Intent(this, MyBoundService.class);
        bindService(intent, connection, Context.BIND_AUTO_CREATE);
    }
    
    @Override
    protected void onStop() {
        super.onStop();
        if (bound) {
            unbindService(connection);
            bound = false;
        }
    }
}
```

### 3.5 Service 与 Thread 区别

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Service vs Thread                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────────────────────────────────────────────────┐
  │     对比项       │                 Service                │    Thread     │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ 执行线程         │ 默认主线程（需手动开线程）              │ 子线程        │
  │ 生命周期         │ 独立于 Activity                        │ 随进程        │
  │ 后台运行         │ 可以（受限制）                         │ 可以          │
  │ 系统感知         │ 是（AMS 管理）                         │ 否            │
  │ 跨进程           │ 支持                                   │ 不支持        │
  │ 被杀后恢复       │ 可能（START_STICKY）                   │ 不可能        │
  │ 优先级           │ 较高                                   │ 较低          │
  │ 适用场景         │ 用户可感知的后台任务                   │ 简单异步任务  │
  └─────────────────┴─────────────────────────────────────────────────────────┘

  选择建议：
  ─────────────────────────────────────────────────────────────────────────
  - 简单异步任务（网络请求）→ Thread / Coroutines
  - 需要独立生命周期 → Service
  - 用户可感知长时任务 → ForegroundService
  - 需要跨进程通信 → BoundService
  - 延迟/周期任务 → WorkManager
```

### 3.6 Service 常见问题

```
Q1: Service 如何执行耗时操作？
─────────────────────────────────────────────────────────────────────────
A: Service 默认在主线程，耗时操作需要：
   - 创建子线程
   - 使用 IntentService（已废弃）
   - 使用 JobIntentService（已废弃）
   - 使用 Coroutines

Q2: Android 8.0+ 后台 Service 限制？
─────────────────────────────────────────────────────────────────────────
A: 后台应用无法创建后台 Service：
   - 使用 startForegroundService() + 5秒内调用 startForeground()
   - 使用 WorkManager 替代

Q3: Service 和 IntentService 区别？
─────────────────────────────────────────────────────────────────────────
A: 
   - Service：默认主线程，需手动开线程
   - IntentService：子线程执行，串行处理，自动停止（已废弃）

Q4: 如何保证 Service 不被杀死？
─────────────────────────────────────────────────────────────────────────
A: 无法完全保证，但可以提高优先级：
   - 使用前台服务（ForegroundService）
   - 返回 START_STICKY
   - 在 onDestroy 中重启
```

---

## 4. BroadcastReceiver

### 4.1 BroadcastReceiver 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BroadcastReceiver 定义                              │
└─────────────────────────────────────────────────────────────────────────────┘

  官方定义：
  "A broadcast receiver is a component that responds to system-wide 
   broadcast announcements."

  核心职责：
  ─────────────────────────────────────────────────────────────────────────
  1. 接收系统广播事件（开机、网络变化、电量变化等）
  2. 接收应用发送的自定义广播
  3. 作为应用间通信的一种方式

  特点：
  ─────────────────────────────────────────────────────────────────────────
  - 无界面组件
  - onReceive() 在主线程执行
  - 执行时间有限制（10秒/60秒）
  - 可以启动 Activity/Service

  注意：
  ─────────────────────────────────────────────────────────────────────────
  - onReceive() 不能执行耗时操作，否则会 ANR
  - 静态注册的广播在 Android 8.0+ 受限
```

### 4.2 广播类型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         广播类型                                            │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 无序广播（Normal Broadcast）
  ─────────────────────────────────────────────────────────────────────────
  - 所有接收者同时接收
  - 无法拦截，无法修改
  - 效率高
  - sendBroadcast() 发送

  2. 有序广播（Ordered Broadcast）
  ─────────────────────────────────────────────────────────────────────────
  - 按优先级顺序接收
  - 可以拦截（abortBroadcast）
  - 可以修改数据（setResult）
  - sendOrderedBroadcast() 发送

  3. 粘性广播（Sticky Broadcast）
  ─────────────────────────────────────────────────────────────────────────
  - 广播发送后会保留
  - Android 5.0+ 已废弃

  4. 本地广播（Local Broadcast）
  ─────────────────────────────────────────────────────────────────────────
  - 只在应用内传播
  - 安全性高，效率高
  - 推荐替代：LiveData / EventBus / Flow
```

### 4.3 广播注册方式

```java
/**
 * 静态注册（在 AndroidManifest.xml 中）
 * 特点：应用未运行时也能接收
 */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            // 开机启动
        }
    }
}

<!-- AndroidManifest.xml -->
<receiver android:name=".BootReceiver" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>

/**
 * 动态注册（代码中注册）
 * 特点：只在注册后生效，需要手动注销
 */
public class MainActivity extends AppCompatActivity {
    private NetworkReceiver networkReceiver;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        networkReceiver = new NetworkReceiver();
        IntentFilter filter = new IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION);
        registerReceiver(networkReceiver, filter);
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (networkReceiver != null) {
            unregisterReceiver(networkReceiver);
        }
    }
}
```

### 4.4 广播发送方式

```java
/**
 * 1. 发送无序广播
 */
Intent intent = new Intent("com.example.MY_ACTION");
intent.putExtra("data", "Hello");
sendBroadcast(intent);

/**
 * 2. 发送有序广播
 */
Intent intent = new Intent("com.example.ORDERED_ACTION");
sendOrderedBroadcast(intent, null);

// 接收有序广播
public class OrderedReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        // 获取上一个接收者传递的数据
        String data = getResultData();
        
        // 传递给下一个接收者
        setResultData("Modified: " + data);
        
        // 拦截广播（后面的接收者不会收到）
        // abortBroadcast();
    }
}

/**
 * 3. 发送本地广播
 */
LocalBroadcastManager.getInstance(context)
    .sendBroadcast(new Intent("com.example.LOCAL_ACTION"));

/**
 * 4. 发送粘性广播（已废弃）
 */
// sendStickyBroadcast(intent);  // Android 5.0+ 废弃
```

### 4.5 广播权限控制

```xml
<!-- 1. 声明权限 -->
<permission android:name="com.example.MY_PERMISSION" />

<!-- 2. 发送带权限的广播 -->
<uses-permission android:name="com.example.MY_PERMISSION" />
```

```java
// 发送方：只有声明了权限的应用才能接收
sendBroadcast(intent, "com.example.MY_PERMISSION");

// 接收方：只有声明了权限的应用才能发送
registerReceiver(receiver, filter, "com.example.MY_PERMISSION", null);
```

### 4.6 广播限制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 8.0+ 广播限制                               │
└─────────────────────────────────────────────────────────────────────────────┘

限制原因：
- 后台应用监听广播会消耗资源
- 静态注册的广播会在应用未运行时唤醒应用

限制内容：
- 静态注册的隐式广播不再生效（大部分）

不受限制的广播（可以静态注册）：
┌─────────────────────────────────────────────────────────────────────────────┐
│  广播 Action                          │  说明                               │
├────────────────────────────────────────┼────────────────────────────────────┤
│  BOOT_COMPLETED                       │  开机完成                           │
│  LOCKED_BOOT_COMPLETED                │  开机完成且设备已解锁               │
│  TIMEZONE_CHANGED                     │  时区变化                           │
│  TIME_SET                             │  时间变化                           │
│  DATE_CHANGED                         │  日期变化                           │
│  LOCALE_CHANGED                       │  语言变化                           │
│  MY_PACKAGE_REPLACED                  │  应用更新（仅自己）                 │
│  PACKAGE_REPLACED                     │  应用更新（需要权限）               │
│  PACKAGE_ADDED                        │  应用安装                           │
│  PACKAGE_REMOVED                      │  应用卸载                           │
│  ACTION_POWER_CONNECTED               │  连接电源                           │
│  ACTION_POWER_DISCONNECTED            │  断开电源                           │
│  BATTERY_LOW                          │  电量低                             │
│  BATTERY_OKAY                         │  电量恢复                           │
│  DEVICE_STORAGE_LOW                   │  存储空间低                         │
│  DEVICE_STORAGE_OK                    │  存储空间恢复                       │
└─────────────────────────────────────────────────────────────────────────────┘

受限制的广播（需要动态注册）：
- CONNECTIVITY_ACTION（网络变化）
- WIFI_STATE_CHANGED（WiFi 状态）
- SCREEN_ON / SCREEN_OFF（屏幕开关）

解决方案：
1. 使用动态注册
2. 使用 JobScheduler / WorkManager 替代
3. 使用系统 API 替代（如 ConnectivityManager.registerNetworkCallback）
```

### 4.7 常用系统广播

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         常用系统广播列表                                    │
└─────────────────────────────────────────────────────────────────────────────┘

系统状态类：
┌─────────────────────────────────────────────────────────────────────────────┐
│  Action                               │  说明                               │
├────────────────────────────────────────┼────────────────────────────────────┤
│  android.intent.action.BOOT_COMPLETED │  开机完成                           │
│  android.intent.action.SHUTDOWN       │  关机                               │
│  android.intent.action.REBOOT         │  重启                               │
│  android.net.conn.CONNECTIVITY_CHANGE │  网络状态变化                       │
│  android.net.wifi.WIFI_STATE_CHANGED  │  WiFi 状态变化                      │
│  android.intent.action.AIRPLANE_MODE  │  飞行模式变化                       │
│  android.intent.action.BATTERY_CHANGED│  电池状态变化                       │
│  android.intent.action.BATTERY_LOW    │  电量低                             │
│  android.intent.action.POWER_CONNECTED│  连接电源                           │
│  android.intent.action.POWER_DISCONNECTED │  断开电源                       │
│  android.intent.action.SCREEN_ON      │  屏幕亮起                           │
│  android.intent.action.SCREEN_OFF     │  屏幕熄灭                           │
│  android.intent.action.USER_PRESENT   │  用户解锁                           │
└─────────────────────────────────────────────────────────────────────────────┘

时间日期类：
┌─────────────────────────────────────────────────────────────────────────────┐
│  Action                               │  说明                               │
├────────────────────────────────────────┼────────────────────────────────────┤
│  android.intent.action.TIME_SET        │  时间设置变化                       │
│  android.intent.action.DATE_CHANGED    │  日期变化                           │
│  android.intent.action.TIMEZONE_CHANGED│  时区变化                           │
│  android.app.action.NEXT_ALARM_CLOCK_CHANGED │  闹钟变化                  │
└─────────────────────────────────────────────────────────────────────────────┘

应用相关类：
┌─────────────────────────────────────────────────────────────────────────────┐
│  Action                               │  说明                               │
├────────────────────────────────────────┼────────────────────────────────────┤
│  android.intent.action.PACKAGE_ADDED   │  应用安装                           │
│  android.intent.action.PACKAGE_REMOVED │  应用卸载                           │
│  android.intent.action.PACKAGE_REPLACED│  应用更新                           │
│  android.intent.action.MY_PACKAGE_REPLACED │  自己更新                       │
│  android.intent.action.PACKAGE_DATA_CLEARED │  应用数据清除                │
│  android.intent.action.PACKAGE_FIRST_LAUNCH │  首次启动                    │
└─────────────────────────────────────────────────────────────────────────────┘

媒体相关类：
┌─────────────────────────────────────────────────────────────────────────────┐
│  Action                               │  说明                               │
├────────────────────────────────────────┼────────────────────────────────────┤
│  android.intent.action.HEADSET_PLUG    │  耳机插拔                           │
│  android.media.VOLUME_CHANGED_ACTION   │  音量变化                           │
│  android.intent.action.MEDIA_MOUNTED   │  SD 卡挂载                          │
│  android.intent.action.MEDIA_UNMOUNTED │  SD 卡卸载                          │
│  android.intent.action.MEDIA_REMOVED   │  SD 卡移除                          │
│  android.intent.action.CAMERA_BUTTON   │  相机按键                           │
└─────────────────────────────────────────────────────────────────────────────┘

语言地区类：
┌─────────────────────────────────────────────────────────────────────────────┐
│  Action                               │  说明                               │
├────────────────────────────────────────┼────────────────────────────────────┤
│  android.intent.action.LOCALE_CHANGED  │  语言变化                           │
│  android.intent.action.CONFIGURATION_CHANGED │  配置变化                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.8 本地广播 LocalBroadcastManager

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LocalBroadcastManager                               │
└─────────────────────────────────────────────────────────────────────────────┘

特点：
- 只在应用内传播，不跨进程
- 安全性高，其他应用无法发送/接收
- 效率高，不经过系统 Binder
- 不受 Android 8.0+ 限制
- 不会产生 ANR

// 依赖
implementation 'androidx.localbroadcastmanager:localbroadcastmanager:1.1.0'
```

```java
/**
 * 注册本地广播
 */
public class MainActivity extends AppCompatActivity {
    
    private LocalBroadcastManager localBroadcastManager;
    private LocalReceiver localReceiver;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        localBroadcastManager = LocalBroadcastManager.getInstance(this);
        
        // 注册
        localReceiver = new LocalReceiver();
        IntentFilter filter = new IntentFilter("com.example.LOCAL_ACTION");
        localBroadcastManager.registerReceiver(localReceiver, filter);
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        // 注销
        localBroadcastManager.unregisterReceiver(localReceiver);
    }
    
    // 发送
    private void sendLocalBroadcast() {
        Intent intent = new Intent("com.example.LOCAL_ACTION");
        intent.putExtra("data", "Hello Local");
        localBroadcastManager.sendBroadcast(intent);
    }
    
    class LocalReceiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            String data = intent.getStringExtra("data");
        }
    }
}
```

```
推荐替代方案：
─────────────────────────────────────────────────────────────────────────

1. LiveData / Flow（推荐）
   - 生命周期感知
   - 自动取消订阅

2. EventBus / RxBus
   - 更灵活的事件总线
   - 支持线程切换

3. 自定义回调接口
   - 简单直接
   - 适合简单场景
```

### 4.9 广播原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         广播分发原理                                        │
└─────────────────────────────────────────────────────────────────────────────┘

发送方                      AMS                        接收方
   │                         │                           │
   │  sendBroadcast()        │                           │
   │────────────────────────►│                           │
   │                         │                           │
   │                         │  查找匹配的 Receiver      │
   │                         │  按优先级排序             │
   │                         │                           │
   │                         │  无序广播：并行分发       │
   │                         │  有序广播：串行分发       │
   │                         │                           │
   │                         │  scheduleRegisteredReceiver
   │                         │──────────────────────────►│
   │                         │                           │
   │                         │                   onReceive()
   │                         │                           │
   │                         │◄──────────────────────────│
   │                         │     处理完成              │

关键类：
- ActivityManagerService (AMS)：管理广播分发
- BroadcastQueue：管理广播队列
- BroadcastRecord：广播记录
- ReceiverList：接收者列表
- IntentResolver：Intent 匹配

两种 BroadcastQueue：
- fgQueue：前台广播队列，超时 10 秒
- bgQueue：后台广播队列，超时 60 秒
```

### 4.10 BroadcastReceiver 常见问题

```
Q1: onReceive() 可以执行耗时操作吗？
A: 不可以，onReceive() 在主线程执行：
   - 前台广播：10 秒超时
   - 后台广播：60 秒超时
   - 超时会导致 ANR
   
   解决方案：使用 goAsync() 或启动 Service

Q2: 动态注册忘记注销会怎样？
A: 会导致内存泄漏，必须在 onDestroy() 中注销
```

---

## 5. ContentProvider

### 5.1 ContentProvider 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ContentProvider 定义                                │
└─────────────────────────────────────────────────────────────────────────────┘

  官方定义：
  "A content provider manages access to a central repository of data."

  核心职责：
  ─────────────────────────────────────────────────────────────────────────
  1. 提供统一的数据访问接口
  2. 跨进程数据共享
  3. 数据的增删改查（CRUD）
  4. 数据变化通知

  URI 结构：
  ─────────────────────────────────────────────────────────────────────────
  content://com.example.provider/users/123
  
  scheme: content://
  authority: com.example.provider（唯一标识）
  path: users（表名）
  _id: 123（记录ID）
```

### 5.2 ContentProvider 原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ContentProvider 原理                                │
└─────────────────────────────────────────────────────────────────────────────┘

客户端进程                          系统进程 (AMS)                     服务端进程
     │                                   │                                  │
     │  ContentResolver.query()          │                                  │
     │         │                         │                                  │
     │         ▼                         │                                  │
     │  ApplicationContentResolver       │                                  │
     │         │                         │                                  │
     │         │  getContentProvider()   │                                  │
     │         ├────────────────────────►│                                  │
     │         │                         │                                  │
     │         │                         │  查找/启动 Provider 进程         │
     │         │                         │                                  │
     │         │                         │  IContentProvider.query()        │
     │         │                         ├─────────────────────────────────►│
     │         │                         │                                  │
     │         │                         │                          ContentProvider.query()
     │         │                         │                                  │
     │         │                         │◄─────────────────────────────────┤
     │         │                         │         返回 Cursor              │
     │         │                         │                                  │
     │         │◄────────────────────────│                                  │
     │         │   返回 Cursor           │                                  │
     │         │                         │                                  │
     │         ▼                         │                                  │
     │  返回给调用者                     │                                  │

关键类：
- ContentResolver：客户端访问入口
- IContentProvider：Binder 接口
- ContentProvider：服务端实现
- ContentProviderNative：Binder Native 层

特点：
- 通过 Binder 实现跨进程
- 数据以 Cursor 形式返回
- 支持批量操作（applyBatch）
```

### 5.3 ContentProvider 核心方法

```
┌─────────────────┬─────────────────────────────────────────────────────────┐
│       方法       │                      说明                                │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ onCreate()       │ 初始化，在主线程调用                                    │
│ query()          │ 查询数据，返回 Cursor                                   │
│ insert()         │ 插入数据，返回新记录的 Uri                               │
│ update()         │ 更新数据，返回受影响的行数                               │
│ delete()         │ 删除数据，返回受影响的行数                               │
│ getType()        │ 返回 MIME 类型                                          │
│ call()           │ 自定义方法调用（Android 5.0+）                          │
│ bulkInsert()     │ 批量插入                                                │
│ applyBatch()     │ 批量操作                                                │
└─────────────────┴─────────────────────────────────────────────────────────┘

MIME 类型格式：
- 单条记录：vnd.android.cursor.item/vnd.com.example.user
- 多条记录：vnd.android.cursor.dir/vnd.com.example.users
```

### 5.4 自定义 ContentProvider 完整示例

```java
/**
 * 自定义 ContentProvider 完整实现
 */
public class UserProvider extends ContentProvider {
    
    private static final String AUTHORITY = "com.example.provider";
    private static final int USER_DIR = 1;
    private static final int USER_ITEM = 2;
    
    private static final UriMatcher uriMatcher = new UriMatcher(UriMatcher.NO_MATCH);
    
    static {
        uriMatcher.addURI(AUTHORITY, "users", USER_DIR);
        uriMatcher.addURI(AUTHORITY, "users/#", USER_ITEM);
    }
    
    private SQLiteDatabase db;
    
    @Override
    public boolean onCreate() {
        // 在主线程调用，不能执行耗时操作
        DbHelper helper = new DbHelper(getContext());
        db = helper.getWritableDatabase();
        return true;
    }
    
    @Nullable
    @Override
    public Cursor query(@NonNull Uri uri, @Nullable String[] projection,
                        @Nullable String selection, @Nullable String[] selectionArgs,
                        @Nullable String sortOrder) {
        
        String tableName = getTableName(uri);
        
        switch (uriMatcher.match(uri)) {
            case USER_DIR:
                return db.query(tableName, projection, selection, 
                    selectionArgs, null, null, sortOrder);
            case USER_ITEM:
                String id = uri.getPathSegments().get(1);
                return db.query(tableName, projection, "_id = ?", 
                    new String[]{id}, null, null, sortOrder);
            default:
                throw new IllegalArgumentException("Unknown URI: " + uri);
        }
    }
    
    @Nullable
    @Override
    public Uri insert(@NonNull Uri uri, @Nullable ContentValues values) {
        String tableName = getTableName(uri);
        long id = db.insert(tableName, null, values);
        
        if (id > 0) {
            Uri newUri = ContentUris.withAppendedId(uri, id);
            // 通知数据变化
            getContext().getContentResolver().notifyChange(newUri, null);
            return newUri;
        }
        return null;
    }
    
    @Override
    public int update(@NonNull Uri uri, @Nullable ContentValues values,
                      @Nullable String selection, @Nullable String[] selectionArgs) {
        String tableName = getTableName(uri);
        int count = db.update(tableName, values, selection, selectionArgs);
        
        if (count > 0) {
            getContext().getContentResolver().notifyChange(uri, null);
        }
        return count;
    }
    
    @Override
    public int delete(@NonNull Uri uri, @Nullable String selection,
                      @Nullable String[] selectionArgs) {
        String tableName = getTableName(uri);
        int count = db.delete(tableName, selection, selectionArgs);
        
        if (count > 0) {
            getContext().getContentResolver().notifyChange(uri, null);
        }
        return count;
    }
    
    @Nullable
    @Override
    public String getType(@NonNull Uri uri) {
        switch (uriMatcher.match(uri)) {
            case USER_DIR:
                return "vnd.android.cursor.dir/vnd.com.example.users";
            case USER_ITEM:
                return "vnd.android.cursor.item/vnd.com.example.user";
            default:
                throw new IllegalArgumentException("Unknown URI: " + uri);
        }
    }
    
    private String getTableName(Uri uri) {
        return "users";
    }
}
```

```xml
<!-- AndroidManifest.xml 注册 -->
<provider
    android:name=".UserProvider"
    android:authorities="com.example.provider"
    android:exported="true"
    android:readPermission="com.example.READ_USER"
    android:writePermission="com.example.WRITE_USER" />
```

### 5.5 UriMatcher 使用

```java
/**
 * UriMatcher 用于匹配 URI
 */
public class UriMatcherExample {
    
    private static final String AUTHORITY = "com.example.provider";
    
    private static final int USERS = 1;           // users/
    private static final int USER_ID = 2;         // users/#
    private static final int USER_ORDERS = 3;     // users/#/orders
    private static final int ORDER_ID = 4;        // orders/#
    
    private static final UriMatcher matcher = new UriMatcher(UriMatcher.NO_MATCH);
    
    static {
        // # 匹配数字，* 匹配任意字符串
        matcher.addURI(AUTHORITY, "users", USERS);
        matcher.addURI(AUTHORITY, "users/#", USER_ID);
        matcher.addURI(AUTHORITY, "users/#/orders", USER_ORDERS);
        matcher.addURI(AUTHORITY, "orders/#", ORDER_ID);
    }
    
    public void match(Uri uri) {
        switch (matcher.match(uri)) {
            case USERS:
                // content://com.example.provider/users
                break;
            case USER_ID:
                // content://com.example.provider/users/123
                long id = ContentUris.parseId(uri);
                break;
            case USER_ORDERS:
                // content://com.example.provider/users/123/orders
                String userId = uri.getPathSegments().get(1);
                break;
            default:
                throw new IllegalArgumentException("Unknown URI: " + uri);
        }
    }
}
```

### 5.6 ContentObserver 监听数据变化

```java
/**
 * 监听 ContentProvider 数据变化
 */
public class UserObserver extends ContentObserver {
    
    public UserObserver(Handler handler) {
        super(handler);
    }
    
    @Override
    public void onChange(boolean selfChange, @Nullable Uri uri) {
        super.onChange(selfChange, uri);
        // 数据变化了，刷新 UI
        if (uri != null) {
            long id = ContentUris.parseId(uri);
            Log.d("Observer", "User " + id + " changed");
        }
    }
}

// 注册监听
public class MainActivity extends AppCompatActivity {
    
    private UserObserver observer;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        observer = new UserObserver(new Handler(Looper.getMainLooper()));
        
        Uri uri = Uri.parse("content://com.example.provider/users");
        // true 表示监听所有子 URI
        getContentResolver().registerContentObserver(uri, true, observer);
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        getContentResolver().unregisterContentObserver(observer);
    }
}
```

### 5.7 批量操作

```java
/**
 * 批量操作 - 提高性能
 */
public void batchInsert(List<User> users) {
    ContentResolver resolver = getContentResolver();
    Uri uri = Uri.parse("content://com.example.provider/users");
    
    ArrayList<ContentProviderOperation> operations = new ArrayList<>();
    
    for (User user : users) {
        operations.add(ContentProviderOperation.newInsert(uri)
            .withValue("name", user.name)
            .withValue("age", user.age)
            .build());
    }
    
    try {
        // 批量执行，在一个事务中
        resolver.applyBatch("com.example.provider", operations);
    } catch (Exception e) {
        e.printStackTrace();
    }
}

/**
 * 批量插入 - bulkInsert
 */
public int bulkInsert(List<User> users) {
    Uri uri = Uri.parse("content://com.example.provider/users");
    
    ContentValues[] valuesArray = new ContentValues[users.size()];
    for (int i = 0; i < users.size(); i++) {
        ContentValues values = new ContentValues();
        values.put("name", users.get(i).name);
        values.put("age", users.get(i).age);
        valuesArray[i] = values;
    }
    
    return getContentResolver().bulkInsert(uri, valuesArray);
}
```

### 5.8 ContentProvider 权限控制

```xml
<!-- 1. 声明权限 -->
<permission
    android:name="com.example.READ_USER"
    android:label="Read User"
    android:protectionLevel="normal" />
    
<permission
    android:name="com.example.WRITE_USER"
    android:label="Write User"
    android:protectionLevel="dangerous" />

<!-- 2. Provider 配置权限 -->
<provider
    android:name=".UserProvider"
    android:authorities="com.example.provider"
    android:exported="true"
    android:readPermission="com.example.READ_USER"
    android:writePermission="com.example.WRITE_USER" />

<!-- 3. 客户端申请权限 -->
<uses-permission android:name="com.example.READ_USER" />
<uses-permission android:name="com.example.WRITE_USER" />
```

```xml
<!-- URI 权限临时授予 -->
<provider
    android:name=".UserProvider"
    android:authorities="com.example.provider"
    android:exported="true"
    android:grantUriPermissions="true">
    
    <grant-uri-permission android:pathPattern="/users/.*" />
</provider>

<!-- 客户端通过 Intent 临时获取权限 -->
Intent intent = new Intent();
intent.setData(Uri.parse("content://com.example.provider/users/123"));
intent.setFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
```

### 5.9 ContentProvider 与 Room

```java
/**
 * Room + ContentProvider 结合使用
 */
@Database(entities = {User.class}, version = 1)
public abstract class AppDatabase extends RoomDatabase {
    public abstract UserDao userDao();
}

@Dao
public interface UserDao {
    @Query("SELECT * FROM users")
    Cursor getAllUsers();
    
    @Insert
    long insert(User user);
    
    @Update
    int update(User user);
    
    @Delete
    int delete(User user);
}

// ContentProvider 使用 Room
public class RoomProvider extends ContentProvider {
    
    private AppDatabase database;
    
    @Override
    public boolean onCreate() {
        database = Room.databaseBuilder(getContext(), 
            AppDatabase.class, "app.db").build();
        return true;
    }
    
    @Nullable
    @Override
    public Cursor query(@NonNull Uri uri, @Nullable String[] projection,
                        @Nullable String selection, @Nullable String[] selectionArgs,
                        @Nullable String sortOrder) {
        return database.userDao().getAllUsers();
    }
}
```

### 5.10 常用系统 ContentProvider

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         常用系统 ContentProvider                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬───────────────────────────────────────────────────────┐
│  Provider           │  URI                                      │  说明     │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Contacts           │  content://contacts/people               │  联系人   │
│  CallLog            │  content://call_log/calls                │  通话记录 │
│  MediaStore.Images  │  content://media/external/images/media   │  图片     │
│  MediaStore.Video   │  content://media/external/video/media    │  视频     │
│  MediaStore.Audio   │  content://media/external/audio/media    │  音频     │
│  MediaStore.Files   │  content://media/external/file           │  文件     │
│  Calendar           │  content://com.android.calendar/events   │  日历     │
│  Browser            │  content://browser/bookmarks             │  书签     │
│  Settings           │  content://settings/system               │  系统设置 │
│  UserDictionary     │  content://user_dictionary/words         │  用户词典 │
│  Downloads          │  content://downloads/my_downloads        │  下载     │
└─────────────────────┴───────────────────────────────────────────────────────┘

// 查询联系人示例
Cursor cursor = getContentResolver().query(
    ContactsContract.Contacts.CONTENT_URI,
    new String[]{ContactsContract.Contacts._ID, 
                 ContactsContract.Contacts.DISPLAY_NAME},
    null, null, null);

// 查询图片示例
Cursor cursor = getContentResolver().query(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    new String[]{MediaStore.Images.Media._ID,
                 MediaStore.Images.Media.DISPLAY_NAME,
                 MediaStore.Images.Media.DATA},
    null, null, 
    MediaStore.Images.Media.DATE_ADDED + " DESC");
```

### 5.11 ContentProvider 常见问题

```
Q1: ContentProvider 的方法在哪个线程执行？
A: onCreate() 在主线程，其他方法在调用者线程

Q2: ContentProvider.onCreate() 和 Application.onCreate() 顺序？
A: ContentProvider.onCreate() 先于 Application.onCreate()
   顺序：Application 构造函数 → ContentProvider.attachInfo() → 
         ContentProvider.onCreate() → Application.attachBaseContext() → 
         Application.onCreate() → Activity.onCreate()

Q3: ContentProvider 如何保证线程安全？
A: ContentProvider 的方法可能被多线程并发调用，需要自行同步：
   - 使用 synchronized 关键字
   - 使用数据库事务
   - 使用 ReentrantLock

Q4: ContentProvider 和 SQLite 的关系？
A: ContentProvider 是数据访问层，SQLite 是数据存储层：
   - ContentProvider 提供统一接口
   - SQLite 提供数据持久化
   - 两者可以结合使用（也可以用 Room、文件等）

Q5: 如何跨应用访问 ContentProvider？
A: 1. Provider 设置 exported="true"
   2. 客户端申请相应权限
   3. 使用 ContentResolver 访问

Q6: ContentProvider 返回的 Cursor 需要关闭吗？
A: 是的，必须调用 cursor.close()，否则会内存泄漏
   推荐使用 try-with-resources 或在 finally 中关闭

Q7: ContentProvider 和 FileProvider 的区别？
A: - ContentProvider：通用数据共享
   - FileProvider：专门用于文件共享，提供安全的 Uri
```

---

## 6. 四大组件对比

```
┌─────────────────┬──────────────────────────────────────────────────────────┐
│     组件         │                      核心特点                             │
├─────────────────┼──────────────────────────────────────────────────────────┤
│ Activity        │ 界面组件，用户交互入口                                    │
│ Service         │ 后台服务，无界面                                          │
│ BroadcastReceiver│ 消息接收器，响应广播                                     │
│ ContentProvider │ 数据共享，跨进程访问                                      │
└─────────────────┴──────────────────────────────────────────────────────────┘

┌─────────────────┬──────────────────────────────────────────────────────────┐
│     组件         │                      使用场景                             │
├─────────────────┼──────────────────────────────────────────────────────────┤
│ Activity        │ 展示界面、处理用户交互                                    │
│ Service         │ 音乐播放、文件下载、后台处理                              │
│ BroadcastReceiver│ 监听系统事件、应用间通信                                 │
│ ContentProvider │ 跨进程数据共享、访问系统数据                              │
└─────────────────┴──────────────────────────────────────────────────────────┘

共同点：
1. 都需要在 AndroidManifest.xml 中注册
2. 都有独立的生命周期
3. 都由系统管理
4. 都支持跨进程通信
```

---

## 7. 进程间通信 IPC

```
┌─────────────────┬──────────────────────────────────────────────────────────┐
│     方式         │                      说明                                │
├─────────────────┼──────────────────────────────────────────────────────────┤
│ Intent          │ 最简单，通过 Bundle 传递数据                             │
│ Binder/AIDL     │ 最强大，支持方法调用、回调                                │
│ Messenger       │ 轻量级，串行处理消息                                      │
│ ContentProvider │ 数据共享，标准 CRUD 接口                                  │
│ BroadcastReceiver│ 消息广播，一对多通信                                     │
│ Socket          │ 网络通信，开销较大                                        │
│ 共享内存        │ 高效大数据传输                                            │
└─────────────────┴──────────────────────────────────────────────────────────┘
```

---

## 8. 常见问题

```
Q1: 四大组件可以不在 Manifest 中注册吗？
A: 不可以，都必须注册（动态注册的广播例外）

Q2: 四大组件的生命周期谁管理？
A: 由系统服务管理（AMS/ATMS/PMS）

Q3: ContentProvider.onCreate() 为什么先于 Application.onCreate()？
A: 因为 ContentProvider 可能在 Application 初始化前被其他进程访问

Q4: 如何选择 IPC 方式？
A: 
   - 简单数据 → Intent + Bundle
   - 数据共享 → ContentProvider
   - 方法调用 → AIDL/Binder
   - 事件通知 → BroadcastReceiver
```

---

## 9. 知识体系总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         四大组件知识体系                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   四大组件      │
                           └────────┬────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
  ┌───────────┐              ┌───────────┐              ┌───────────┐
  │  Activity │              │  Service  │              │Broadcast  │
  │           │              │           │              │Receiver   │
  │ 界面展示  │              │ 后台服务  │              │ 消息接收  │
  │ 生命周期  │              │ 启动/绑定 │              │ 静态/动态 │
  │ 启动模式  │              │ 前台/后台 │              │ 有序/无序 │
  └───────────┘              └───────────┘              └───────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                                    ▼
                            ┌───────────┐
                            │ Content   │
                            │ Provider  │
                            │ 数据共享  │
                            │ 跨进程    │
                            └───────────┘

  核心要点：
  ─────────────────────────────────────────────────────────────────────────
  1. Activity：界面入口，生命周期管理，启动模式
  2. Service：后台任务，启动/绑定模式，前台服务
  3. BroadcastReceiver：消息接收，静态/动态注册
  4. ContentProvider：数据共享，URI 访问，权限控制
```

---

> 作者：OpenClaw | 日期：2026-03-09
