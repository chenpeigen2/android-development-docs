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
   - 4.5 [广播权限控制](#45-广播权限控制)
   - 4.6 [广播限制](#46-广播限制)
   - 4.7 [常用系统广播](#47-常用系统广播)
   - 4.8 [本地广播 LocalBroadcastManager](#48-本地广播-localbroadcastmanager)
   - 4.9 [广播原理](#49-广播原理)
   - 4.10 [BroadcastReceiver 常见问题](#410-broadcastreceiver-常见问题)
5. [ContentProvider](#5-contentprovider)
   - 5.1 [ContentProvider 是什么](#51-contentprovider-是什么)
   - 5.2 [ContentProvider 原理](#52-contentprovider-原理)
   - 5.3 [ContentProvider 启动流程](#53-contentprovider-启动流程经典面试题)
   - 5.4 [Application 启动流程](#54-application-启动流程)
   - 5.5 [ContentProvider 核心方法](#55-contentprovider-核心方法)
   - 5.6 [自定义 ContentProvider 完整示例](#56-自定义-contentprovider-完整示例)
   - 5.7 [UriMatcher 使用](#57-urimatcher-使用)
   - 5.8 [ContentObserver 监听数据变化](#58-contentobserver-监听数据变化)
   - 5.9 [批量操作](#59-批量操作)
   - 5.10 [ContentProvider 权限控制](#510-contentprovider-权限控制)
   - 5.11 [ContentProvider 与 Room](#511-contentprovider-与-room)
   - 5.12 [常用系统 ContentProvider](#512-常用系统-contentprovider)
   - 5.13 [ContentProvider 常见问题](#513-contentprovider-常见问题)
6. [四大组件对比](#6-四大组件对比)
7. [进程间通信 IPC](#7-进程间通信-ipc)
8. [常见问题](#8-常见问题)
9. [知识体系总结](#9-知识体系总结)
10. [资深工程师深度解析](#10-资深工程师深度解析)
    - 10.1 [四大组件与进程生命周期](#101-四大组件与进程生命周期)
    - 10.2 [组件间通信最佳实践](#102-组件间通信最佳实践)
    - 10.3 [四大组件常见踩坑](#103-四大组件常见踩坑)
    - 10.4 [组件化架构中的四大组件](#104-组件化架构中的四大组件)
    - 10.5 [四大组件性能优化](#105-四大组件性能优化)
    - 10.6 [Android 版本演进对四大组件的影响](#106-android-版本演进对四大组件的影响)
11. [面试高频题精选](#11-面试高频题精选)

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

  场景6：A → B → A 完整时序（经典面试题）
  ─────────────────────────────────────────────────────────────────────────

  前提：Activity A 已处于 onResume 状态，此时启动 Activity B（B 完全遮挡 A）

  【A 启动 B 的回调顺序】

    ① A.onPause()                  ← A 先进入暂停状态
    ② B.onCreate()  → B.onStart()  → B.onResume()   ← B 完整启动
    ③ A.onStop()                   ← A 确认 B 已显示后才停止

    ⚠️ 关键点：A.onPause() 和 B.onResume() 不能同时执行，
       旧 Activity 的 onPause 先执行完，新 Activity 才会 onResume。
       因此不要在 onPause 中做耗时操作，否则会阻塞新 Activity 的显示。

    ⚠️ 源码依据：ActivityStack.java 中的 completePauseLocked() 方法
       会触发新 Activity 的启动，确保旧 Activity 先 pause 再 resume 新的。

  【按 Back 键从 B 返回 A 的回调顺序】

    ④ B.onPause()                  ← B 先暂停
    ⑤ A.onRestart() → A.onStart() → A.onResume()   ← A 重新可见并可交互
    ⑥ B.onStop()    → B.onDestroy()                 ← B 销毁（standard 模式）

  【完整时序图】

    Activity A                    Activity B
    ─────────                    ─────────
    onResume()
         │
    onPause() ◄──── 用户点击启动 B
         │
         │                  onCreate()
         │                  onStart()
         │                  onResume()
         │
    onStop() ◄──── B 已完全显示
         │
         │              ◄──── 用户按 Back 键返回
         │                  onPause()
         │
    onRestart() ──►
    onStart() ──►
    onResume() ──►
         │
         │                  onStop()
         │                  onDestroy()

  【特殊情况：B 为透明/对话框样式 Activity】

    Activity A                    Activity B (透明)
    ─────────                    ─────────
    onResume()
         │
    onPause() ◄──── A 不会走到 onStop，因为 A 仍部分可见
         │
         │                  onCreate()
         │                  onStart()
         │                  onResume()
         │
         │              ◄──── 用户按 Back 键返回
         │                  onPause()
         │
    onResume() ◄──── A 直接 onResume，不需要 onRestart/onStart
         │
         │                  onStop()
         │                  onDestroy()

    原因：onStop 的触发条件是 Activity 不再可见。透明 Activity 不会
    完全遮挡底层 Activity，因此底层 Activity 只走到 onPause。

  场景7：屏幕旋转
  ─────────────────────────────────────────────────────────────────────────
  onPause → onStop → onDestroy → onCreate → onStart → onResume
  （相当于销毁重建）

  场景8：按Home键
  ─────────────────────────────────────────────────────────────────────────
  onPause → onStop（不会 onDestroy）

  场景9：从最近任务返回
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

### 5.3 ContentProvider 启动流程（经典面试题）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ContentProvider 启动流程                                  │
└─────────────────────────────────────────────────────────────────────────────┘

触发时机：
─────────────────────────────────────────────────────────────────────────
当其他进程通过 ContentResolver 访问本进程的 ContentProvider 时，
如果本进程尚未启动，系统会先启动本进程，然后初始化 ContentProvider。

启动流程（时序）：
─────────────────────────────────────────────────────────────────────────

  其他进程                         系统进程 (AMS)                   本进程
     │                                 │                              │
     │ ContentResolver.query()        │                              │
     │        │                        │                              │
     │        ▼                        │                              │
     │ ApplicationContentResolver      │                              │
     │        │                        │                              │
     │        │ acquireProvider()      │                              │
     │        ├───────────────────────►│                              │
     │        │                        │                              │
     │        │                        │ ① 查找目标 ContentProvider   │
     │        │                        │    所在进程是否已启动        │
     │        │                        │                              │
     │        │                        │ ② 进程未启动 →               │
     │        │                        │    AMS.startProcessLocked()  │
     │        │                        ├─────────────────────────────►│
     │        │                        │                              │
     │        │                        │                    ③ 进程启动入口
     │        │                        │                       ActivityThread.main()
     │        │                        │                              │
     │        │                        │                    ④ ActivityThread.attach()
     │        │                        │                              │
     │        │                        │              ⑤ ┌──────────────────────────┐
     │        │                        │                │ Application 启动流程：    │
     │        │                        │                │  a) LoadedApk.makeApplication()
     │        │                        │                │     → new Application()    │
     │        │                        │                │  b) Application.attach()   │
     │        │                        │                │     → attachBaseContext()  │
     │        │                        │                └──────────────────────────┘
     │        │                        │                              │
     │        │                        │              ⑥ installContentProviders()
     │        │                        │                ┌──────────────────────────────┐
     │        │                        │                │ 遍历 AndroidManifest.xml 中  │
     │        │                        │                │ 注册的所有 ContentProvider：  │
     │        │                        │                │                              │
     │        │                        │                │ for each provider:            │
     │        │                        │                │   a) ClassLoader 加载类       │
     │        │                        │                │   b) ContentProvider.         │
     │        │                        │                │      attachInfo()             │
     │        │                        │                │   c) ContentProvider.onCreate()│
     │        │                        │                └──────────────────────────────┘
     │        │                        │                              │
     │        │                        │              ⑦ Application.onCreate()
     │        │                        │                              │
     │        │                        │              ⑧ AMS 发布 Provider
     │        │                        │◄─────────────────────────────│
     │        │                        │  publishContentProviders()   │
     │        │                        │                              │
     │        │                        │ ⑨ 将 IContentProvider       │
     │        │                        │    注册到 AMS               │
     │        │                        │                              │
     │        │◄───────────────────────│                              │
     │        │ 返回 IContentProvider  │                              │
     │        │                        │                              │
     │        ▼                        │                              │
     │ 通过 Binder 调用               │                              │
     │ ContentProvider.query()        │                              │

⚠️ 关键顺序（面试高频）：
─────────────────────────────────────────────────────────────────────────

  Application 构造函数
        │
        ▼
  Application.attachBaseContext()    ← ContextImpl 注入
        │
        ▼
  ContentProvider.attachInfo()       ← Provider 关联 Context
        │
        ▼
  ContentProvider.onCreate()         ← Provider 初始化
        │
        ▼
  Application.onCreate()             ← Application 初始化
        │
        ▼
  Activity/Service.onCreate()        ← 组件创建

  结论：ContentProvider.onCreate() 先于 Application.onCreate() 执行！

源码路径：
─────────────────────────────────────────────────────────────────────────
  frameworks/base/core/java/android/app/ActivityThread.java
    → handleBindApplication()
      → LoadedApk.makeApplication()     // ⑤ 创建 Application
      → installContentProviders()        // ⑥ 安装所有 ContentProvider
      → Application.onCreate()           // ⑦ 回调 Application
      → ActivityManagerService            // ⑧ 发布到 AMS
        .publishContentProviders()

  frameworks/base/core/java/android/app/ContentProvider.java
    → attachInfo()                        // 关联 Context 和 ProviderInfo
    → onCreate()                          // 子类实现初始化逻辑

⚠️ 面试陷阱：
─────────────────────────────────────────────────────────────────────────
  Q: 在 ContentProvider.onCreate() 中能用 getContext() 吗？
  A: 可以。attachInfo() 在 onCreate() 之前调用，此时 Context 已注入。

  Q: 为什么 ContentProvider 要在 Application.onCreate() 之前初始化？
  A: 因为其他进程可能在 Application 还没初始化完成时就尝试访问 Provider，
     系统需要保证 Provider 尽早可用。

  Q: ContentProvider.onCreate() 能做耗时操作吗？
  A: 绝对不能！它在主线程执行，且阻塞 Application.onCreate()。
     耗时操作会延迟整个应用的启动速度。
```

### 5.4 Application 启动流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Application 启动流程                                   │
└─────────────────────────────────────────────────────────────────────────────┘

一、冷启动完整流程
─────────────────────────────────────────────────────────────────────────

  用户点击 App 图标
        │
        ▼
  Launcher.startActivity()
        │
        ▼
  AMS.startActivity()                    ← Binder 调用到系统进程
        │
        ▼
  AMS 解析 Intent，查找目标进程
        │
        ├── 进程已存在 → 直接调度 Activity
        │
        └── 进程不存在 → ② 创建新进程
                │
                ▼
          Zygote.fork()                  ← 从 Zygote 进程 fork
                │
                ▼
          ActivityThread.main()          ← App 进程入口
                │
                ▼
          ┌─────────────────────────────────────────────────────────┐
          │                  Application 创建链路                    │
          │                                                         │
          │  ActivityThread.main()                                  │
          │       │                                                 │
          │       ▼                                                 │
          │  Looper.prepareMainLooper()   ← 创建主线程 Looper      │
          │       │                                                 │
          │       ▼                                                 │
          │  ActivityThread.attach()      ← 通知 AMS 进程就绪      │
          │       │                                                 │
          │       ▼                                                 │
          │  ┌─ LoadedApk.makeApplication() ─────────────────────┐  │
          │  │                                                  │  │
          │  │  1) Instrumentation.newApplication()              │  │
          │  │       │                                          │  │
          │  │       ▼                                          │  │
          │  │     ClassLoader.loadClass()                       │  │
          │  │       │      ← 加载 Application 子类             │  │
          │  │       ▼                                          │  │
      ┌─────── new Application()  ◄─── Application 构造函数     │  │
      │ │  │       │                                          │  │
      │ │  │       ▼                                          │  │
      │ │  │  Application.attach(context)                      │  │
      │ │  │       │                                          │  │
      │ │  │       ▼                                          │  │
      │ │  │  Application.attachBaseContext()  ◄── 最早的回调   │  │
      │ │  │       │                                          │  │
      │ │  │       ▼                                          │  │
      │ │  │  Instrumentation.callApplicationOnCreate()        │  │
      │ │  │       │                                          │  │
      │ │  │       ▼                                          │  │
      │ │  └─ Application.onCreate()  ◄─── 常用初始化入口     ─┘  │
      │ │         │                                                │
      │ └─────────┼────────────────────────────────────────────────┘
      │           │
      │           ▼
      │     installContentProviders()  ← 初始化所有 ContentProvider
      │           │
      │           ▼
      │     Application.onCreate() 已经执行完（上面第⑦步）
      │           │
      │           ▼
      │     Activity.onCreate()        ← 第一个 Activity 创建
      │
      │ 源码路径：
      │   frameworks/base/core/java/android/app/ActivityThread.java
      │     → handleBindApplication()
      │       → createAppContext()
      │       → LoadedApk.makeApplication()
      │       → installContentProviders()
      │       → mInstrumentation.callApplicationOnCreate()
      │       → ActivityManagerNative.getDefault()
      │         .publishContentProviders()

二、Application 生命周期方法完整顺序
─────────────────────────────────────────────────────────────────────────

  ┌──────────────────────┐
  │  Application 构造函数  │  ← 最先执行，此时还没有 Context
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ attachBaseContext()   │  ← Context 注入，最早能用到 Context 的时机
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────────────┐
  │ ContentProvider.attachInfo()  │
  │ ContentProvider.onCreate()    │  ← 所有 Provider 依次初始化
  └──────────┬───────────────────┘
             │
             ▼
  ┌──────────────────────┐
  │ Application.onCreate() │  ← 常规初始化入口（三方 SDK 初始化等）
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ Activity/Service      │  ← 四大组件开始工作
  │ onCreate()            │
  └──────────────────────┘

三、进程优先级与 Application 的关系
─────────────────────────────────────────────────────────────────────────

  App 进程被创建的触发方式（按优先级从高到低）：

  1. 前台 Activity 启动              → 可见进程优先级
  2. startForegroundService()        → 服务进程优先级
  3. ContentProvider 被访问           → 后台进程优先级（可能被 AMS 杀掉）
  4. 发送有序广播触发                 → 后台进程优先级

  ⚠️ 无论哪种触发方式，Application 的初始化流程都一样：
     构造 → attachBaseContext → ContentProvider → onCreate

四、面试高频问题
─────────────────────────────────────────────────────────────────────────

  Q1: Application 构造函数被调用几次？
  A: 每个进程只调用一次。多进程 App 中，每个进程都有自己的 Application 实例。

  Q2: attachBaseContext() 和 onCreate() 有什么区别？
  A: attachBaseContext() 是 Context 注入时机，onCreate() 是初始化时机。
     如果需要在最早时机获取 Context（如初始化全局数据库），用 attachBaseContext()。
     大部分场景用 onCreate() 即可。

  Q3: ContentProvider 的初始化为什么插在 attachBaseContext 和 onCreate 之间？
  A: 源码设计决策。attachBaseContext 先让 Application 获得 Context 能力，
     然后初始化 ContentProvider（需要 Context），最后才回调 onCreate 给开发者。
     这保证了开发者在 onCreate 中能正常使用所有 Provider。

  Q4: 多进程情况下如何区分当前进程？
  A: 在 attachBaseContext() 或 onCreate() 中通过进程名判断：

     String currentProcess = getCurrentProcessName();
     if (currentProcess.endsWith(":push")) {
         // 推送进程，只初始化推送 SDK
     } else {
         // 主进程，全量初始化
     }

  Q5: 如何优化 Application 启动速度？
  A: 1) 延迟初始化：非必须的三方 SDK 移到子线程或首次使用时初始化
     2) 减少 ContentProvider 数量：每个 Provider 都在主线程初始化
     3) 使用 App Startup 库统一管理初始化
     4) 避免在 attachBaseContext() 中做 IO 操作
```

### 5.5 ContentProvider 核心方法

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

### 5.6 自定义 ContentProvider 完整示例

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

### 5.7 UriMatcher 使用

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

### 5.8 ContentObserver 监听数据变化

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

### 5.9 批量操作

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

### 5.10 ContentProvider 权限控制

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

### 5.11 ContentProvider 与 Room

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

### 5.12 常用系统 ContentProvider

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

### 5.13 ContentProvider 常见问题

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

## 10. 资深工程师深度解析

### 10.1 四大组件与进程生命周期

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    四大组件与进程优先级                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  Android 进程优先级（从高到低）：
  ─────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  1. 前台进程（Foreground Process）                                      │
  │     ──────────────────────────────────────────────────────────────      │
  │     条件（满足任一）：                                                   │
  │     • 正在执行 onResume() 的 Activity                                   │
  │     • 绑定到前台 Activity 的 Service                                    │
  │     • 正在执行 onCreate/onStartCommand/onDestroy 的 Service             │
  │     • 调用了 startForeground() 的 Service                               │
  │     • 正在执行 onReceive() 的 BroadcastReceiver                         │
  │                                                                         │
  │  2. 可见进程（Visible Process）                                         │
  │     ──────────────────────────────────────────────────────────────      │
  │     条件（满足任一）：                                                   │
  │     • 执行了 onPause 但未 onStop 的 Activity                           │
  │     • 绑定到可见 Activity 的 Service                                    │
  │                                                                         │
  │  3. 服务进程（Service Process）                                         │
  │     ──────────────────────────────────────────────────────────────      │
  │     条件：                                                               │
  │     • 已启动且正在运行的后台 Service（未调用 startForeground）           │
  │                                                                         │
  │  4. 后台进程（Background Process）                                      │
  │     ──────────────────────────────────────────────────────────────      │
  │     条件：                                                               │
  │     • 已 onStop 但未 onDestroy 的 Activity                              │
  │     • 对用户不可见                                                      │
  │                                                                         │
  │  5. 空进程（Empty Process）                                             │
  │     ──────────────────────────────────────────────────────────────      │
  │     条件：                                                               │
  │     • 不包含任何活跃组件的进程                                          │
  │     • 保留仅为缓存目的                                                  │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

```
组件对进程保活的影响：
─────────────────────────────────────────────────────────────────────────

  ┌──────────────────────────────────────────────────────────────────────────┐
  │                                                                          │
  │  Activity（前台）  ──►  进程提升为前台进程（最高优先级）                  │
  │  Activity（可见）  ──►  进程为可见进程（第二优先级）                      │
  │  Activity（后台）  ──►  进程降为后台进程                                  │
  │                                                                          │
  │  Service（前台）   ──►  进程提升为前台进程                                │
  │  Service（后台）   ──►  进程为服务进程                                    │
  │  Service（绑定到   ──►  进程优先级随绑定者提升                            │
  │   前台 Activity）                                                        │
  │                                                                          │
  │  BroadcastReceiver       ──►  onReceive() 执行期间为前台进程             │
  │                          ──►  执行完毕后恢复原有优先级                   │
  │                                                                          │
  │  ContentProvider         ──►  被访问时提升进程优先级                      │
  │                          ──►  无访问时不影响优先级                        │
  │                                                                          │
  └──────────────────────────────────────────────────────────────────────────┘

  实战经验：
  ─────────────────────────────────────────────────────────────────────────
  1. 音乐播放必须使用 ForegroundService，否则切后台很快被杀
  2. 后台下载任务应使用 WorkManager 而非 Service
  3. BroadcastReceiver.onReceive() 执行时间短，应尽快启动 Service
  4. 多进程架构中，每个进程有独立的组件生命周期
```

### 10.2 组件间通信最佳实践

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    组件间通信方式全景                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────┐
  │                                                                          │
  │  同进程通信：                                                            │
  │  ──────────────────────────────────────────────────────────────────────  │
  │                                                                          │
  │  1. Intent + Bundle（Activity / Service / BroadcastReceiver）            │
  │     优点：标准方式，系统支持                                             │
  │     缺点：数据大小限制（约 1MB）                                         │
  │     场景：简单数据传递                                                   │
  │                                                                          │
  │  2. ViewModel + LiveData（Activity / Fragment）                          │
  │     优点：生命周期感知，自动取消                                         │
  │     缺点：仅限同一 Activity 内                                           │
  │     场景：Fragment 间通信                                                │
  │                                                                          │
  │  3. 回调接口 / Listener                                                  │
  │     优点：直接、高效                                                     │
  │     缺点：需要手动管理生命周期                                           │
  │     场景：Activity 与 Service 通信                                       │
  │                                                                          │
  │  4. Event Bus（应用内事件总线）                                          │
  │     优点：解耦，一对多                                                   │
  │     缺点：调试困难，容易内存泄漏                                         │
  │     场景：全局事件通知                                                   │
  │                                                                          │
  └──────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────┐
  │                                                                          │
  │  跨进程通信：                                                            │
  │  ──────────────────────────────────────────────────────────────────────  │
  │                                                                          │
  │  1. AIDL（最强大）                                                      │
  │     支持方法调用、回调、复杂数据类型                                     │
  │     适合：频繁的双向 IPC                                                 │
  │                                                                          │
  │  2. Messenger（轻量级）                                                 │
  │     基于 Message 的串行通信                                              │
  │     适合：低频、单向通信                                                 │
  │                                                                          │
  │  3. ContentProvider（数据共享）                                          │
  │     标准 CRUD 接口                                                       │
  │     适合：数据共享场景                                                   │
  │                                                                          │
  │  4. BroadcastReceiver（事件通知）                                        │
  │     一对多通知                                                           │
  │     适合：系统事件监听                                                   │
  │                                                                          │
  └──────────────────────────────────────────────────────────────────────────┘
```

```java
/**
 * AIDL 跨进程通信示例
 */

// IMyAidlInterface.aidl
interface IMyAidlInterface {
    int add(int a, int b);
    String getMessage();
    void registerCallback(ICallback callback);
    void unregisterCallback(ICallback callback);
}

// ICallback.aidl
interface ICallback {
    void onResult(int code, String msg);
}

// 服务端 Service
public class AidlService extends Service {
    private final IMyAidlInterface.Stub binder = new IMyAidlInterface.Stub() {
        @Override
        public int add(int a, int b) {
            return a + b;
        }

        @Override
        public String getMessage() {
            return "Hello from AidlService";
        }

        @Override
        public void registerCallback(ICallback callback) {
            // 注册回调
        }

        @Override
        public void unregisterCallback(ICallback callback) {
            // 注销回调
        }
    };

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return binder;
    }
}

// 客户端绑定
public class MainActivity extends AppCompatActivity {
    private IMyAidlInterface aidlService;
    
    private ServiceConnection connection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            aidlService = IMyAidlInterface.Stub.asInterface(service);
            try {
                int result = aidlService.add(1, 2);
                String msg = aidlService.getMessage();
            } catch (RemoteException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            aidlService = null;
        }
    };
}
```

```
通信方式选择决策树：
─────────────────────────────────────────────────────────────────────────

                    需要组件间通信
                         │
                    是否跨进程？
                    /          \
                  是            否
                  │             │
                  │        同进程直接通信
                  │        ┌─────────────────────┐
                  │        数据简单？             │
                  │        /       \             │
                  │      是         否            │
                  │      │          │            │
                  │   Intent+     ViewModel     │
                  │   Bundle      + LiveData    │
                  │                            │
              跨进程通信
              ┌──────────────────────────────┐
              │ 通信模式？                     │
              ├──────────┬──────────┬─────────┤
              │ 方法调用  │ 数据共享  │ 事件通知│
              │    │     │    │     │    │    │
              │  AIDL    │Content  │ Broad- │
              │          │Provider │ cast   │
              └──────────┴──────────┴─────────┘
```

### 10.3 四大组件常见踩坑

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Activity 常见踩坑                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  坑1：onSaveInstanceState 与 FragmentTransaction 冲突
  ─────────────────────────────────────────────────────────────────────────
  问题：在 onSaveInstanceState 之后执行 commit() 会抛异常
  原因：onSaveInstanceState 之后状态已保存，commit 可能丢失
  解决：使用 commitAllowingStateLoss()（不推荐）
        或在 onSaveInstanceState 之前完成 commit（推荐）

  坑2：singleTask 启动模式下的意外行为
  ─────────────────────────────────────────────────────────────────────────
  问题：singleTask Activity 会清除其上方的 Activity
  原因：singleTask 默认带有 CLEAR_TOP 效果
  解决：明确理解 taskAffinity 的作用，必要时配合 FLAG_ACTIVITY_NEW_TASK

  坑3：Activity 重建导致异步回调空指针
  ─────────────────────────────────────────────────────────────────────────
  问题：屏幕旋转后异步回调引用了旧的 Activity 实例
  原因：Activity 重建后引用失效
  解决：使用 ViewModel 存储数据、弱引用、或在回调前检查 isFinishing()

  坑4：透明 Activity 导致生命周期异常
  ─────────────────────────────────────────────────────────────────────────
  问题：透明 Activity 不会触发下方 Activity 的 onStop
  原因：下方 Activity 仍然部分可见
  解决：注意 onPause 和 onStop 的区别，在 onPause 中也做必要的资源释放
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Service 常见踩坑                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  坑1：ForegroundService 未及时显示通知
  ─────────────────────────────────────────────────────────────────────────
  问题：Android 8.0+ 调用 startForegroundService() 后 5 秒内
        未调用 startForeground() 会导致 ANR
  解决：在 onCreate() 或 onStartCommand() 中立即调用 startForeground()

  坑2：bindService 后忘记 unbindService
  ─────────────────────────────────────────────────────────────────────────
  问题：Activity 销毁时未解绑导致 ServiceConnection 泄漏
  原因：ServiceConnection 保持着 Activity 引用
  解决：在 onStop() 或 onDestroy() 中调用 unbindService()
        推荐使用 LifecycleObserver 自动管理

  坑3：后台 Service 被系统杀死
  ─────────────────────────────────────────────────────────────────────────
  问题：Android 8.0+ 后台 Service 几分钟后被杀
  解决：使用 ForegroundService / WorkManager / JobScheduler

  坑4：IntentService 内存泄漏
  ─────────────────────────────────────────────────────────────────────────
  问题：IntentService 持有 Context 引用（已废弃）
  解决：使用 JobIntentService 或 CoroutineWorker 替代
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BroadcastReceiver 常见踩坑                               │
└─────────────────────────────────────────────────────────────────────────────┘

  坑1：动态注册未注销导致内存泄漏
  ─────────────────────────────────────────────────────────────────────────
  问题：Activity 销毁时未调用 unregisterReceiver()
  解决：
  - 在 onPause() 或 onDestroy() 中注销
  - 使用 Lifecycle-aware 方式自动注销

  坑2：静态广播在 Android 8.0+ 不生效
  ─────────────────────────────────────────────────────────────────────────
  问题：大部分隐式广播的静态注册不再生效
  解决：改为动态注册，或使用系统豁免的广播 Action

  坑3：onReceive() 中执行耗时操作 ANR
  ─────────────────────────────────────────────────────────────────────────
  问题：onReceive() 在主线程，前台广播 10 秒超时
  解决：使用 goAsync() 延长到 30 秒，或启动 Service 处理

  坑4：有序广播优先级设置无效
  ─────────────────────────────────────────────────────────────────────────
  问题：android:priority 设置了但没生效
  原因：动态注册和静态注册的优先级范围不同
        动态注册优先级始终高于静态注册
  解决：同一注册方式内比较 priority 值（-1000 到 1000）
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ContentProvider 常见踩坑                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  坑1：ContentProvider.onCreate() 耗时导致启动慢
  ─────────────────────────────────────────────────────────────────────────
  问题：onCreate() 在主线程执行，耗时操作会拖慢应用启动
  原因：ContentProvider.onCreate() 先于 Application.onCreate()
  解决：onCreate() 只做轻量初始化，耗时操作延迟到首次查询时

  坑2：Cursor 未关闭导致内存泄漏
  ─────────────────────────────────────────────────────────────────────────
  问题：query() 返回的 Cursor 用完后忘记 close()
  解决：使用 try-finally 或 try-with-resources

  坑3：notifyChange 频繁调用导致 UI 卡顿
  ─────────────────────────────────────────────────────────────────────────
  问题：批量插入时每条都调用 notifyChange 触发多次刷新
  解决：批量操作完成后统一调用一次 notifyChange

  坑4：exported=true 未加权限控制
  ─────────────────────────────────────────────────────────────────────────
  问题：ContentProvider 对外暴露但无权限保护
  解决：必须设置 readPermission / writePermission
        或设置 exported=false（仅内部使用）
```

### 10.4 组件化架构中的四大组件

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    组件化架构中的组件管理                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  传统单体架构：                                                         │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  ┌──────────────────────────────────────────────────────┐              │
  │  │                    App Module                        │              │
  │  │                                                      │              │
  │  │  Activity A  Activity B  Activity C                  │              │
  │  │  Service X   Receiver Y  Provider Z                  │              │
  │  │                                                      │              │
  │  │  直接引用，紧耦合                                    │              │
  │  └──────────────────────────────────────────────────────┘              │
  │                                                                         │
  │  组件化架构：                                                           │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                             │
  │  │ Module A │  │ Module B │  │ Module C │                             │
  │  │ (用户)   │  │ (商品)   │  │ (订单)   │                             │
  │  └────┬─────┘  └────┬─────┘  └────┬─────┘                             │
  │       │              │              │                                   │
  │       └──────────────┼──────────────┘                                   │
  │                      │                                                  │
  │              ┌───────┴───────┐                                         │
  │              │    Router     │  ← 路由层（ARouter 等）                 │
  │              └───────┬───────┘                                         │
  │                      │                                                  │
  │              ┌───────┴───────┐                                         │
  │              │  Common/Base │  ← 公共层                               │
  │              └───────────────┘                                         │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

```
组件化中四大组件的挑战与解决方案：
─────────────────────────────────────────────────────────────────────────

  1. Activity 跳转（跨模块）
  ─────────────────────────────────────────────────────────────────────────
  问题：模块间无直接依赖，无法直接创建 Intent
  
  解决方案：
  - ARouter：基于注解的路由框架
    @Route(path = "/user/profile")
    public class ProfileActivity extends AppCompatActivity { }
    
    ARouter.getInstance().build("/user/profile").navigation();
  
  - Deep Link：基于 URI 的路由
    Intent intent = new Intent(Intent.ACTION_VIEW,
        Uri.parse("myapp://user/profile?id=123"));

  2. Service 跨模块通信
  ─────────────────────────────────────────────────────────────────────────
  问题：模块间无法直接获取 Service 实例
  
  解决方案：
  - 接口暴露 + 反射
  - ARouter 的 IProvider
  - 统一的 ServiceManager

  3. BroadcastReceiver 跨模块事件
  ─────────────────────────────────────────────────────────────────────────
  问题：模块间需要通信但不想互相依赖
  
  解决方案：
  - 全局事件总线（LiveData / Flow / EventBus）
  - 模块级 LocalBroadcast
  - 统一的 EventHub

  4. ContentProvider 初始化问题
  ─────────────────────────────────────────────────────────────────────────
  问题：多个模块都有 ContentProvider，初始化顺序不可控
  
  解决方案：
  - App Startup：统一初始化入口
  - 懒加载：首次使用时初始化
  - 移除自动初始化，改为手动触发
```

```java
/**
 * App Startup 统一初始化
 */
// 模块 A 的 Initializer
public class ModuleAInitializer implements Initializer<Void> {
    @NonNull
    @Override
    public Void create(@NonNull Context context) {
        // 模块 A 初始化逻辑
        ModuleA.init(context);
        return null;
    }

    @NonNull
    @Override
    public List<Class<? extends Initializer<?>>> dependencies() {
        // 依赖其他 Initializer（控制初始化顺序）
        return Collections.emptyList();
    }
}

// AndroidManifest.xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false"
    tools:node="merge">
    
    <!-- 启用 ModuleA 的初始化 -->
    <meta-data
        android:name="com.example.modulea.ModuleAInitializer"
        android:value="androidx.startup" />
</provider>
```

### 10.5 四大组件性能优化

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Activity 性能优化                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  优化1：减少 onCreate 耗时
  ─────────────────────────────────────────────────────────────────────────
  问题：onCreate 耗时导致启动慢、白屏
  方案：
  - 布局优化：减少层级、使用 ViewStub 延迟加载、ConstraintLayout
  - 异步初始化：非必要初始化延迟到子线程
  - 闪屏页：使用 windowBackground 避免白屏

  // 优化前
  protected void onCreate(Bundle savedInstanceState) {
      super.onCreate(savedInstanceState);
      setContentView(R.layout.activity_main);  // 复杂布局
      
      initSDK();          // 耗时 SDK 初始化
      initDatabase();     // 数据库初始化
      loadConfig();       // 网络配置加载
  }

  // 优化后
  protected void onCreate(Bundle savedInstanceState) {
      super.onCreate(savedInstanceState);
      setContentView(R.layout.activity_main);  // 优化后的布局
      
      // 核心初始化（主线程）
      initCriticalComponents();
      
      // 非核心初始化（子线程）
      Executors.newSingleThreadExecutor().execute(() -> {
          initSDK();
          initDatabase();
          loadConfig();
      });
  }

  优化2：避免过度绘制
  ─────────────────────────────────────────────────────────────────────────
  - 移除不必要的背景
  - 使用 clipRect 裁剪绘制区域
  - 减少布局嵌套层级

  优化3：生命周期方法轻量化
  ─────────────────────────────────────────────────────────────────────────
  - onResume/onPause 中避免耗时操作
  - onStop 中释放资源而非等待 onDestroy
  - 使用 ViewModel 持有数据，避免重建时重新加载
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Service 性能优化                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  优化1：合理使用 Service 类型
  ─────────────────────────────────────────────────────────────────────────
  ┌─────────────────────────────┬───────────────────────────────────────┐
  │  场景                        │  推荐方案                              │
  ├─────────────────────────────┼───────────────────────────────────────┤
  │  音乐播放、导航              │  ForegroundService                    │
  │  后台上传下载                │  WorkManager                          │
  │  定时任务                    │  WorkManager / AlarmManager           │
  │  简单异步                    │  Coroutines / RxJava                  │
  │  跨进程方法调用              │  BoundService + AIDL                  │
  └─────────────────────────────┴───────────────────────────────────────┘

  优化2：ForegroundService 通知优化
  ─────────────────────────────────────────────────────────────────────────
  - 使用低优先级通知（NotificationManager.IMPORTANCE_LOW）
  - 提供用户操作入口（暂停/取消按钮）
  - 任务完成后立即移除通知

  优化3：避免 Service 泄漏
  ─────────────────────────────────────────────────────────────────────────
  - 启动式 Service：任务完成后调用 stopSelf()
  - 绑定式 Service：注意解绑时机
  - 使用 LifecycleObserver 自动管理
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BroadcastReceiver 性能优化                               │
└─────────────────────────────────────────────────────────────────────────────┘

  优化1：减少广播注册数量
  ─────────────────────────────────────────────────────────────────────────
  - 只注册真正需要的广播
  - 使用特定 Action 过滤，避免过于宽泛的 IntentFilter
  - 及时注销不再需要的广播

  优化2：onReceive() 中避免耗时操作
  ─────────────────────────────────────────────────────────────────────────
  - 短操作：直接处理
  - 中等操作：使用 goAsync()（最多 30 秒）
  - 长操作：启动 Service 或调度 WorkManager

  // goAsync() 示例
  public class MyReceiver extends BroadcastReceiver {
      @Override
      public void onReceive(Context context, Intent intent) {
          final PendingResult pendingResult = goAsync();
          
          new Thread(() -> {
              try {
                  // 执行耗时操作（不超过 30 秒）
                  processData(intent);
              } finally {
                  pendingResult.finish();
              }
          }).start();
      }
  }

  优化3：本地广播替代全局广播
  ─────────────────────────────────────────────────────────────────────────
  - 应用内通信使用 LiveData / Flow 替代广播
  - 减少跨进程通信开销
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ContentProvider 性能优化                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  优化1：批量操作代替单条操作
  ─────────────────────────────────────────────────────────────────────────
  - 使用 applyBatch() 批量操作（单事务）
  - 使用 bulkInsert() 批量插入
  - 减少 Binder 调用次数

  优化2：query 结果集优化
  ─────────────────────────────────────────────────────────────────────────
  - 使用 projection 限制查询列
  - 使用 selection 过滤行
  - 使用 sortOrder + limit 分页查询
  - 及时关闭 Cursor

  优化3：notifyChange 优化
  ─────────────────────────────────────────────────────────────────────────
  - 批量操作完成后调用一次
  - 使用 notifyForDescendants 控制通知范围
  - 避免在循环中反复调用

  优化4：异步查询
  ─────────────────────────────────────────────────────────────────────────
  - 使用 CursorLoader（已废弃）或自定义 Loader
  - 使用 Coroutines 异步查询
  - 使用 ContentProviderClient 管理连接
```

### 10.6 Android 版本演进对四大组件的影响

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Android 版本对四大组件的限制演进                          │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┬──────────────────────────────────────────────────────────────┐
  │  版本     │  影响内容                                                   │
  ├──────────┼──────────────────────────────────────────────────────────────┤
  │          │  Activity：                                                │
  │ Android  │  - 多窗口模式支持                                          │
  │  7.0     │  - 通知栏快捷回复（直接回复 RemoteInput）                   │
  │ (API 24) │                                                            │
  │          │  BroadcastReceiver：                                        │
  │          │  - CONNECTIVITY_ACTION 不再能静态注册                       │
  ├──────────┼──────────────────────────────────────────────────────────────┤
  │          │  Activity：                                                │
  │ Android  │  - 画中画模式（PictureInPicture）                          │
  │  8.0     │                                                            │
  │ (API 26) │  Service：                                                 │
  │          │  - 后台 Service 限制，必须使用 startForegroundService()     │
  │          │  - 5 秒内必须调用 startForeground()                        │
  │          │                                                            │
  │          │  BroadcastReceiver：                                        │
  │          │  - 静态注册隐式广播大部分失效                               │
  │          │  - 新增豁免列表                                            │
  ├──────────┼──────────────────────────────────────────────────────────────┤
  │          │  Activity：                                                │
  │ Android  │  - 支持 Bubble（气泡）显示                                 │
  │  10      │                                                            │
  │ (API 29) │  Service：                                                 │
  │          │  - 后台启动 Activity 限制                                  │
  │          │                                                            │
  │          │  ContentProvider：                                          │
  │          │  - 默认 exported=false（之前默认 true）                     │
  ├──────────┼──────────────────────────────────────────────────────────────┤
  │          │  Activity：                                                │
  │ Android  │  - 强制分区存储（Scoped Storage）                          │
  │  11      │                                                            │
  │ (API 30) │  Service：                                                 │
  │          │  - 前台服务类型（foregroundServiceType）必须声明            │
  │          │  - 后台启动限制更严格                                      │
  │          │                                                            │
  │          │  BroadcastReceiver：                                        │
  │          │  - 自定义广播默认 ordered=true                             │
  ├──────────┼──────────────────────────────────────────────────────────────┤
  │          │  Service：                                                 │
  │ Android  │  - 前台服务类型新增 health、connectedDevice 等              │
  │  14      │  - 运行时动态注册广播必须指定 EXPORTED 标志                │
  │ (API 34) │                                                            │
  │          │  Activity：                                                │
  │          │  - 隐式 Intent 限制更严格                                  │
  │          │  - 后台启动 Activity 需要特殊权限                           │
  └──────────┴──────────────────────────────────────────────────────────────┘
```

```
前台服务类型（Android 14+ 必须声明）：
─────────────────────────────────────────────────────────────────────────

  ┌──────────────────────┬────────────────────────────────────────────────┐
  │  foregroundServiceType │  说明                                       │
  ├──────────────────────┼────────────────────────────────────────────────┤
  │  camera               │  相机                                       │
  │  connectedDevice      │  连接的设备（蓝牙等）                       │
  │  dataSync             │  数据同步                                   │
  │  health               │  健康相关（心率等）                         │
  │  location             │  位置服务                                   │
  │  mediaPlayback        │  媒体播放                                   │
  │  mediaProjection      │  屏幕录制/投影                              │
  │  microphone           │  麦克风                                     │
  │  phoneCall            │  电话                                       │
  │  remoteMessaging      │  远程消息                                   │
  │  shortService         │  短时任务（系统级）                         │
  │  specialUse           │  特殊用途                                   │
  │  systemExempted       │  系统豁免                                   │
  └──────────────────────┴────────────────────────────────────────────────┘

  <!-- AndroidManifest.xml 声明 -->
  <service
      android:name=".MusicService"
      android:foregroundServiceType="mediaPlayback" />

  // 代码中启动
  startForeground(notificationId, notification,
      ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK);
```

```
适配建议：
─────────────────────────────────────────────────────────────────────────

  1. Activity 适配
     - 支持 ViewModel + SavedStateHandle 应对重建
     - 处理多窗口/画中画生命周期
     - 使用 Navigation 组件管理跳转

  2. Service 适配
     - 后台任务迁移到 WorkManager
     - 前台服务声明正确的 foregroundServiceType
     - 注意 Android 12+ 前台服务通知延迟（10 秒）

  3. BroadcastReceiver 适配
     - 静态广播仅保留系统豁免列表中的
     - 动态注册注意生命周期管理
     - 应用内事件使用 Flow/LiveData 替代

  4. ContentProvider 适配
     - exported 默认 false，按需开放
     - 分区存储下 MediaStore 使用受限
     - 考虑 App Startup 替代 ContentProvider 初始化
```

---

## 11. 面试高频题精选

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Activity 相关面试题                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  Q1: Activity 的四种启动模式分别在什么场景下使用？
  ─────────────────────────────────────────────────────────────────────────
  A:
  - standard：默认模式，适合大多数普通页面
  - singleTop：适合消息详情页、通知点击页（避免栈顶重复创建）
  - singleTask：适合应用主页面（如微信主页，返回时清除上层）
  - singleInstance：适合系统级独立页面（如闹钟、来电界面）

  Q2: onSaveInstanceState 和 onRestoreInstanceState 的调用时机？
  ─────────────────────────────────────────────────────────────────────────
  A:
  调用时机：
  - onSaveInstanceState：在 onStop 之前，不一定触发（系统认为需要时才调用）
  - onRestoreInstanceState：在 onStart 之后、onResume 之前
  
  触发条件（onSaveInstanceState）：
  - 按 Home 键
  - 启动新 Activity
  - 屏幕旋转
  - 切换到其他应用
  不触发：按 Back 键（用户主动退出）

  注意：
  - 不要和持久化存储混淆，这只是临时状态保存
  - Bundle 有大小限制（约 1MB）

  Q3: Activity 启动过程经历了哪些主要步骤？
  ─────────────────────────────────────────────────────────────────────────
  A:
  1. 调用 Activity.startActivity()
  2. Instrumentation.execStartActivity()
  3. 通过 Binder 调用 ATMS.startActivityAsUser()
  4. ATMS 解析 Intent，查找目标 Activity
  5. 如果目标进程不存在，通过 Socket 通知 Zygote fork 新进程
  6. 新进程中 ActivityThread.main() 启动
  7. 通过 ApplicationThread.scheduleLaunchActivity() 回调
  8. ActivityThread.handleLaunchActivity()
  9. performLaunchActivity()：创建 Activity 实例，调用 attach()、onCreate()
  10. handleResumeActivity()：调用 onResume()， DecorView 添加到 WindowManager

  Q4: 如何处理 Activity 重建时的数据恢复？
  ─────────────────────────────────────────────────────────────────────────
  A:
  方案1：onSaveInstanceState + onRestoreInstanceState（适合少量数据）
  方案2：ViewModel（推荐，适合页面数据）
         - ViewModel 在配置变更时不会被销毁
         - 结合 SavedStateHandle 处理进程被杀的情况
  方案3：持久化存储（数据库/文件，适合大量数据）

  // 推荐方案
  public class MyViewModel extends ViewModel {
      private SavedStateHandle savedStateHandle;
      
      public MyViewModel(SavedStateHandle savedStateHandle) {
          this.savedStateHandle = savedStateHandle;
      }
      
      public LiveData<String> getData() {
          return savedStateHandle.getLiveData("key", "default");
      }
  }
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Service 相关面试题                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  Q5: Service 和 Thread 的区别？什么时候用 Service？
  ─────────────────────────────────────────────────────────────────────────
  A:
  Service：
  - 运行在主线程（需手动创建子线程）
  - 有独立生命周期，由 AMS 管理
  - 系统可感知，可提高进程优先级
  - 支持跨进程通信
  
  Thread：
  - 运行在子线程
  - 无独立生命周期，随进程消亡
  - 系统不可感知
  - 不支持跨进程
  
  使用 Service 的场景：
  - 需要后台长期运行（音乐播放）
  - 需要提高进程优先级（防止被杀）
  - 需要跨进程通信
  不需要 Service 的场景：
  - Activity 内的简单异步操作 → Coroutines
  - 后台一次性任务 → WorkManager

  Q6: Android 8.0+ 后台 Service 限制如何应对？
  ─────────────────────────────────────────────────────────────────────────
  A:
  限制内容：
  - 后台应用无法自由创建后台 Service
  - 调用 startForegroundService() 后必须 5 秒内调用 startForeground()
  
  应对方案：
  - 用户可感知任务 → ForegroundService + 通知
  - 后台一次性任务 → WorkManager
  - 定时任务 → WorkManager + AlarmManager
  - 即时任务 → Coroutines / RxJava

  Q7: IntentService 为什么被废弃？用什么替代？
  ─────────────────────────────────────────────────────────────────────────
  A:
  废弃原因：
  - IntentService 是 Service 的子类，有 Service 的所有限制
  - Android 8.0+ 后台 Service 限制使其几乎不可用
  - 串行处理任务的设计不够灵活
  
  替代方案：
  - WorkManager：推荐的替代方案，兼容性好，支持约束条件
  - CoroutineWorker：Kotlin 协程版本，更简洁
  - ListenableWorker：需要返回 ListenableFuture 的场景

  class MyWorker(context: Context, params: WorkerParameters) 
      : CoroutineWorker(context, params) {
      override suspend fun doWork(): Result {
          // 执行耗时任务
          return Result.success()
      }
  }
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BroadcastReceiver 相关面试题                             │
└─────────────────────────────────────────────────────────────────────────────┘

  Q8: 广播的静态注册和动态注册有什么区别？
  ─────────────────────────────────────────────────────────────────────────
  A:
  ┌─────────────────┬─────────────────────┬─────────────────────┐
  │  对比项           │  静态注册            │  动态注册            │
  ├─────────────────┼─────────────────────┼─────────────────────┤
  │  注册方式         │  AndroidManifest    │  代码中调用 API      │
  │  生效时机         │  应用安装后          │  registerReceiver 后│
  │  持续性           │  永久（跨应用重启）  │  随组件生命周期      │
  │  进程唤醒         │  可以唤醒应用        │  不可以              │
  │  Android 8.0+    │  大部分隐式广播失效  │  不受影响            │
  │  性能消耗         │  较高（系统维护）    │  较低                │
  │  适用场景         │  系统广播（豁免列表）│  应用内通信          │
  └─────────────────┴─────────────────────┴─────────────────────┘

  Q9: 如何实现有序广播的拦截和数据传递？
  ─────────────────────────────────────────────────────────────────────────
  A:
  发送方：sendOrderedBroadcast(intent, permission)
  
  接收方：
  1. 设置优先级：android:priority="100"（-1000 到 1000）
  2. 获取前一个接收者的数据：getResultData() / getResultCode()
  3. 传递给下一个：setResultData() / setResultCode()
  4. 拦截：abortBroadcast()
  
  执行顺序：高优先级先接收，可以修改数据或拦截

  Q10: LocalBroadcastManager 和全局广播的区别？
  ─────────────────────────────────────────────────────────────────────────
  A:
  LocalBroadcastManager：
  - 只在应用内传播
  - 不经过 Binder，效率更高
  - 其他应用无法发送/接收，更安全
  - 不受 Android 8.0+ 限制
  
  全局广播：
  - 跨应用传播
  - 经过系统 AMS，有 Binder 开销
  - 需要权限控制
  - 受 Android 版本限制
  
  注意：LocalBroadcastManager 已废弃，官方推荐使用 LiveData/Flow
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ContentProvider 相关面试题                               │
└─────────────────────────────────────────────────────────────────────────────┘

  Q11: ContentProvider 是如何实现跨进程共享数据的？
  ─────────────────────────────────────────────────────────────────────────
  A:
  实现原理：
  1. ContentProvider 基于 Binder 机制实现 IPC
  2. 客户端通过 ContentResolver 访问（代理模式）
  3. ContentResolver 通过 AMS 获取 IContentProvider 的 Binder 代理
  4. 调用 query/insert/update/delete 实际是跨进程 Binder 调用
  5. 服务端 ContentProvider 处理请求，返回结果
  
  数据传输：
  - Cursor 数据通过 CursorWindow（共享内存）传递
  - 大数据分页传输，避免 Binder 缓冲区溢出
  - 支持批量操作减少 IPC 次数

  Q12: ContentProvider 和 SQLite 直接使用哪个好？
  ─────────────────────────────────────────────────────────────────────────
  A:
  ContentProvider 优势：
  - 标准 CRUD 接口，统一数据访问
  - 内置跨进程支持
  - 权限控制机制
  - 数据变化通知（ContentObserver）
  - 系统集成（SyncAdapter、Loader 等）
  
  SQLite 直接使用优势：
  - 更简单直接
  - 无跨进程开销
  - 更灵活
  
  选择建议：
  - 需要跨进程共享 → ContentProvider
  - 仅应用内使用 → Room / SQLite
  - 需要数据变化通知 → ContentProvider + ContentObserver

  Q13: 为什么 ContentProvider.onCreate() 先于 Application.onCreate()？
  ─────────────────────────────────────────────────────────────────────────
  A:
  原因：
  1. ContentProvider 可能在 Application 初始化前就被其他进程访问
  2. AMS 在启动应用进程后，会先安装 ContentProvider
  3. 安装过程中会调用 ContentProvider.attachInfo() → onCreate()
  4. 所有 Provider 安装完成后，才调用 Application.onCreate()
  
  启动顺序：
  Application 构造函数
    → ContentProvider.attachInfo()
    → ContentProvider.onCreate()
    → Application.onCreate()
    → Activity/Service onCreate()
  
  注意：
  - ContentProvider.onCreate() 中不要依赖 Application 的初始化
  - 这也是许多 SDK 使用 ContentProvider 自动初始化的原理
  - App Startup 可以优化多个 SDK 的初始化顺序
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    综合面试题                                               │
└─────────────────────────────────────────────────────────────────────────────┘

  Q14: 四大组件可以不注册直接使用吗？
  ─────────────────────────────────────────────────────────────────────────
  A:
  - Activity：必须注册，否则抛出 ActivityNotFoundException
  - Service：必须注册，否则抛出 ServiceNotFoundException
  - BroadcastReceiver：静态注册必须声明；动态注册不需要
  - ContentProvider：必须注册，否则无法通过 ContentResolver 访问

  Q15: 四大组件的生命周期由谁管理？有什么共同点？
  ─────────────────────────────────────────────────────────────────────────
  A:
  管理者：
  - Activity：ATMS (ActivityTaskManagerService)
  - Service：AMS (ActivityManagerService)
  - BroadcastReceiver：AMS
  - ContentProvider：AMS
  
  共同点：
  1. 都在 AndroidManifest.xml 中注册
  2. 都有独立的生命周期
  3. 都由系统服务管理（不由应用控制）
  4. 都支持跨进程通信
  5. 都可以携带 Intent 数据

  Q16: 如何选择 IPC 方式？
  ─────────────────────────────────────────────────────────────────────────
  A:
  ┌───────────────────┬─────────────────────────────────────────────────┐
  │  需求              │  推荐方案                                       │
  ├───────────────────┼─────────────────────────────────────────────────┤
  │  简单数据传递      │  Intent + Bundle                                │
  │  方法调用          │  AIDL                                           │
  │  低频消息          │  Messenger                                      │
  │  数据共享          │  ContentProvider                                │
  │  事件通知          │  BroadcastReceiver                              │
  │  大文件传输        │  ContentProvider / 共享内存                      │
  │  实时通信          │  AIDL + 回调                                    │
  └───────────────────┴─────────────────────────────────────────────────┘

  Q17: 说说你对 Android 组件化的理解？四大组件在组件化中扮演什么角色？
  ─────────────────────────────────────────────────────────────────────────
  A:
  组件化理解：
  - 将应用拆分为独立的模块，每个模块可独立开发、测试
  - 模块间通过路由/接口通信，降低耦合
  
  四大组件在组件化中的角色：
  - Activity：通过路由框架（ARouter）实现跨模块跳转
  - Service：通过接口暴露（IProvider）实现跨模块服务调用
  - BroadcastReceiver：通过事件总线实现跨模块事件通知
  - ContentProvider：跨模块数据共享，也常被用作 SDK 自动初始化入口
  
  关键技术：
  - ARouter / DeepLink：Activity 路由
  - 接口下沉：Service 暴露接口到公共模块
  - 事件总线：LiveData / Flow 替代 BroadcastReceiver
  - App Startup：统一初始化，替代 ContentProvider 初始化
```

---

> 作者：OpenClaw | 日期：2026-03-09
