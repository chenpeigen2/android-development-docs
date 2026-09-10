# Android 四大组件详解

> 审阅基线：AOSP `android-17.0.0_r1`；审阅日期：2026-09-10。正文中的调用链为固定 tag 的关键路径分析，省略代码不是可独立编译的完整 AOSP 类；产品开关、权限和设备结果另行验证。


> 作者：OpenClaw | 日期：2026-03-09

---

## 目录

- [1. 概述](#1-概述)
- [2. Activity](#2-activity)
  - [2.1 Activity 是什么](#21-activity-是什么)
  - [2.2 Activity 生命周期](#22-activity-生命周期)
  - [2.3 Activity 启动模式](#23-activity-启动模式)
  - [2.4 Activity 任务栈](#24-activity-任务栈)
  - [2.5 Activity 启动流程](#25-activity-启动流程)
    - [状态保存的版本边界](#状态保存的版本边界)
  - [2.6 Activity 常见问题](#26-activity-常见问题)
- [3. Service](#3-service)
  - [3.1 Service 是什么](#31-service-是什么)
  - [3.2 Service 生命周期](#32-service-生命周期)
    - [绑定缓存、重绑定与非保证回调](#绑定缓存重绑定与非保证回调)
  - [3.3 Service 类型](#33-service-类型)
  - [3.4 Service 启动方式](#34-service-启动方式)
  - [3.5 Service 与 Thread 区别](#35-service-与-thread-区别)
  - [3.6 Service 常见问题](#36-service-常见问题)
- [4. BroadcastReceiver](#4-broadcastreceiver)
  - [4.1 BroadcastReceiver 是什么](#41-broadcastreceiver-是什么)
  - [4.2 广播类型](#42-广播类型)
  - [4.3 广播注册方式](#43-广播注册方式)
  - [4.4 广播发送方式](#44-广播发送方式)
  - [4.5 广播权限控制](#45-广播权限控制)
  - [4.6 广播限制](#46-广播限制)
  - [4.7 常用系统广播](#47-常用系统广播)
  - [4.8 本地广播 LocalBroadcastManager](#48-本地广播-localbroadcastmanager)
  - [4.9 广播原理](#49-广播原理)
  - [4.10 BroadcastReceiver 常见问题](#410-broadcastreceiver-常见问题)
- [5. ContentProvider](#5-contentprovider)
  - [5.1 ContentProvider 是什么](#51-contentprovider-是什么)
  - [5.2 ContentProvider 原理](#52-contentprovider-原理)
  - [5.3 ContentProvider 启动流程（经典面试题）](#53-contentprovider-启动流程经典面试题)
  - [5.4 Application 启动流程](#54-application-启动流程)
  - [5.5 ContentProvider 核心方法](#55-contentprovider-核心方法)
  - [5.6 自定义 ContentProvider 示例与 URI 约束](#56-自定义-contentprovider-示例与-uri-约束)
  - [5.7 UriMatcher 使用](#57-urimatcher-使用)
  - [5.8 ContentObserver 监听数据变化](#58-contentobserver-监听数据变化)
  - [5.9 批量操作](#59-批量操作)
    - [批量原子性与通知时机](#批量原子性与通知时机)
  - [5.10 ContentProvider 权限控制](#510-contentprovider-权限控制)
  - [5.11 ContentProvider 与 Room](#511-contentprovider-与-room)
  - [5.12 常用系统 ContentProvider](#512-常用系统-contentprovider)
  - [5.13 ContentProvider 常见问题](#513-contentprovider-常见问题)
- [6. 四大组件对比](#6-四大组件对比)
- [7. 进程间通信 IPC](#7-进程间通信-ipc)
- [8. 常见问题](#8-常见问题)
- [9. 知识体系总结](#9-知识体系总结)
- [10. 资深工程师深度解析](#10-资深工程师深度解析)
  - [10.1 四大组件与进程生命周期](#101-四大组件与进程生命周期)
  - [10.2 组件间通信最佳实践](#102-组件间通信最佳实践)
  - [10.3 四大组件常见踩坑](#103-四大组件常见踩坑)
  - [10.4 组件化架构中的四大组件](#104-组件化架构中的四大组件)
  - [10.5 四大组件性能优化](#105-四大组件性能优化)
  - [10.6 Android 版本演进对四大组件的影响](#106-android-版本演进对四大组件的影响)
- [11. 面试高频题精选](#11-面试高频题精选)

---

## 1. 概述

Android 四大组件是 Android 应用的基石，它们分别是：Activity、Service、BroadcastReceiver 和 ContentProvider。每个组件都有其特定的职责和使用场景，理解它们的工作原理和相互关系，是掌握 Android 开发的关键。

```text
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
  1. Activity/Service/Provider 及静态 Receiver 需在 Manifest 注册；动态 Receiver 例外
  2. 都有独立的生命周期
  3. 都可以跨进程通信
  4. 由系统注册/调度（Activity 主要 ATMS，其他主要 AMS；PMS 负责包解析）
```

---

## 2. Activity

### 2.1 Activity 是什么

```text
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
                ├── 状态栏区域的装饰/背景（不是 SystemUI 状态栏窗口）
                ├── TitleView (optional)
                └── ContentView (FrameLayout, id=content)
                      └── 用户布局
```

### 2.2 Activity 生命周期

```text
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
  │    │ onResume │  ← RESUMED：可交互状态，不保证窗口焦点                              │
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

```text
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

    ⚠️ 以上描述同一任务/显示区域中正常非透明页面切换的典型顺序，
不是跨进程、跨窗口的全局串行契约。Android 17 的服务端相关路径在
TaskFragment.startPausing()/completePause()，而不是 ActivityStack.java。

普通路径会等待旧页面 pause 完成，再推进目标 resumed；但存在 pause 超时、
resume-while-pausing、跨任务及多窗口 multi-resume 分支。窗口焦点也不等于
RESUMED：Activity 已 resumed 时可短暂没有焦点，多窗口中可有多个 resumed。
独占资源还应依据 onTopResumedActivityChanged、窗口焦点与具体 API 契约协调。
不要在 onPause 执行持久化大 I/O，它会阻塞本进程主线程并影响切换。

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
  （默认未自行处理相关 configChanges 时；进程重建和状态恢复另算）

  场景8：按Home键
  ─────────────────────────────────────────────────────────────────────────
  通常 onPause → onStop；后台进程可能被杀，不保证 onDestroy

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
        // - 独占资源结合 top-resumed、窗口焦点及具体 API 能力管理
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        // Activity 进入 PAUSED；窗口焦点由 onWindowFocusChanged 单独通知
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

```text
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
  │  在系统选定的 task 中复用目标实例并清除其上页面；不能跨用户/多任务绝对化  │
  │                                                                         │
  │  情况1 - A 已在栈中：                                                   │
  │  任务栈：[A, B, C, D] → 启动 A → [A]（清除 B, C, D，调用 onNewIntent）   │
  │                                                                         │
  │  情况2 - A 不在栈中：                                                   │
  │  目标不存在时按任务选择、affinity 与 flags 建立/选择 task，不保证追加到 [B,C]                       │
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
  │  在对应用户/任务匹配规则内具有独占 task 语义；不要跨用户宣称全局唯一                               │
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
    
```

```java
// Intent flags 示例（不与 manifest launchMode 一一等价）
Intent intent = new Intent(this, MainActivity.class);
intent.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);      // singleTop
intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);        // singleTask
intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);       // 清除目标之上的 Activity
```

```text
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

```text
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

以需要新建 Activity 实例的普通路径为例，固定 tag 的关键调用关系如下：

```text
App: Activity.startActivity -> startActivityForResult
  -> Instrumentation.execStartActivity
  -> IActivityTaskManager.startActivity
system_server:
  ActivityTaskManagerService -> ActivityStarter.execute
    -> 解析目标 / 权限与背景启动限制 / task 选择 / 进程准备
  ActivityTaskSupervisor.realStartActivityLocked
    -> ClientTransaction: LaunchActivityItem + lifecycle request
App:
  IApplicationThread.scheduleTransaction
    -> ActivityThread.scheduleTransaction -> TransactionExecutor.execute
      -> LaunchActivityItem.execute -> ActivityThread.handleLaunchActivity
        -> performLaunchActivity
           instantiate Activity
           makeApplicationInner if necessary
           Activity.attach (inside: PhoneWindow creation)
           Instrumentation.callActivityOnCreate
      -> lifecycle items / state path
           handleStartActivity -> onStart
           handleResumeActivity -> onResume / window attachment
```

`performLaunchActivity()` 不是直接调用 onCreate/onStart/onResume 的一个连续方法；start/resume 由事务执行器补齐目标生命周期。`scheduleLaunchActivity()` 是旧接口名称，不能替代 Android 17 的 scheduleTransaction 路径。

复用实例、透明 Activity、进程已经存在、配置重建与跨显示启动会经过不同分支；上图不是所有启动都 fork 一次。Activity.attach 创建 PhoneWindow，不应把“先在外部创建 PhoneWindow 再 attach”写成实际顺序。

ATMS 管任务与 Activity 服务端生命周期；AMS 管进程及服务/广播/Provider 等。PMS 提供包和组件解析；WMS 协调窗口。客户端真正执行回调的是 ActivityThread/Instrumentation，而不是 system_server 直接调用应用 Java 对象。

#### 状态保存的版本边界

`ActivityThread.performStopActivityInner()` 按 target 判断：需要保存且 target >= 28 时，先完成 onStop，再调用 onSaveInstanceState；旧 target 存在不同顺序。它不是“总在 onStop 之前”。主动 finish、系统直接杀进程等情况不保证保存/销毁回调，因此 Bundle 不能代替持久化存储。

`singleInstancePerTask` 也是现代启动模式：目标 Activity 作为 task root、同一 task 内单实例，但可根据 NEW_DOCUMENT/MULTIPLE_TASK 等规则出现在不同任务中。不能把“四种模式”的旧口诀当成 Android 17 的完整枚举。

### 2.6 Activity 常见问题

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Activity 常见问题                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  Q1: onSaveInstanceState 什么时候调用？
  ─────────────────────────────────────────────────────────────────────────
  A: 在框架需要保存可恢复 UI 状态时调用，不是进程终止通知；以下为常见场景：
     - 按 Home 键
     - 切换到其他应用
     - 屏幕旋转
     - 启动新 Activity
     
     注意：主动 finish 通常不保存；根 Launcher Activity 的 Back 可能把任务移到后台，不能只按按键名称判断

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
  A: Binder 事务缓冲是进程内在途事务共享预算（常见约 1MiB），不是单个 Intent 可用额度。大数据方案：
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

```text
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
  - 长时任务按用途选择合法前台服务或可调度工作；前台服务不是后台限制通行证

  误区：
  ─────────────────────────────────────────────────────────────────────────
  ❌ Service 在子线程执行
  ✓ Service 在主线程执行，耗时操作需要自己开线程

  ❌ Service 可以无限后台运行
  ✓ 后台 Service 启动和存活受限；具体停止/进程回收不能归结为固定几分钟
```

### 3.2 Service 生命周期

```text
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
  │    │ onCreate │  ← 每个 Service 实例创建一次；进程重建会产生新实例                                   │
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
  │    销毁条件：不再 started（stopService/stopSelf 等），且不再有保留服务的有效绑定                │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 绑定缓存、重绑定与非保证回调

`onBind()` 通常针对一组匹配 Intent 的绑定记录调用一次，系统复用返回的 Binder，不是每个客户端绑定都重新调用。最后一个相关绑定释放时调用 `onUnbind()`；如果返回 true 且服务仍存活，后续绑定可能调用 `onRebind()`，不是再次调用 onBind。

Service 同时 started/bound 时，stopService 清除 started 状态但不抹掉有效绑定。进程被杀不会保证执行 onDestroy；START_STICKY 仅表达允许系统在条件满足时重建，并不承诺立即重启，重建时 intent 也可能为 null。

源码对照：`ActiveServices` 管理启动/绑定记录，`ActivityThread.handleCreateService()` 注入 Context 后调用 onCreate，`handleServiceArgs()` 传递 startId 并调用 onStartCommand，`handleBindService()` / `handleUnbindService()` 分发绑定回调。

### 3.3 Service 类型

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Service 类型                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────────────────────────────────────────────────┐
  │     类型         │                      说明                                │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ Started Service  │ startService() 启动，独立运行                           │
  │                  │ 完成后停止 started 状态（stopSelf/stopService）                                 │
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
  │ Service          │ 后台执行受限，停止服务与杀进程需区分                                          │
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
        // START_STICKY: 条件允许时可重建，没有待交付 Intent 时可能传 null
        // START_NOT_STICKY: 无待处理启动时不因这个结果自动重建
        // START_REDELIVER_INTENT: 条件允许时重建并重新交付未完成 Intent
        return START_NOT_STICKY; // 示例一次性任务不依赖空 Intent 重启
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
    private boolean bindingRequested = false;
    
    private ServiceConnection connection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            MyBoundService.LocalBinder binder = (MyBoundService.LocalBinder) service;
            MainActivity.this.service = binder.getService();
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
        bindingRequested = bindService(intent, connection, Context.BIND_AUTO_CREATE);
    }
    
    @Override
    protected void onStop() {
        super.onStop();
        if (bindingRequested) {
            unbindService(connection);
            bindingRequested = false;
        }
        bound = false;
        service = null;
    }
}
```

绑定示例只适用于同进程 LocalBinder，跨进程应使用 AIDL/IBinder 协议。`bindService()` 返回成功与 `onServiceConnected()` 到达是两个阶段，因此必须按 bindingRequested 配对解绑，避免页面在连接回调前退出而泄漏。`onServiceDisconnected()` 表示非正常断连，不是正常 unbind 的必到回调；完整工程还需处理 onNullBinding/onBindingDied 并释放绑定。

### 3.5 Service 与 Thread 区别

```text
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

```text
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
   - 仅在满足前台服务启动/类型/权限条件时调用 startForegroundService，并立即提升到前台；不要等固定 5 秒预算
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
   - 不要依赖 onDestroy 中自启保活：回调可能不到达且后台启动可能被拒绝
```

---

## 4. BroadcastReceiver

### 4.1 BroadcastReceiver 是什么

```text
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
  - 默认在主线程执行；动态注册可指定 Handler 调度
  - 有广播完成期限；普通/前台广播、设备配置与 ANR 调度分支不同
  - 启动 Activity/Service 仍受后台启动、权限与前台服务限制

  注意：
  ─────────────────────────────────────────────────────────────────────────
  - onReceive() 不能执行耗时操作，否则会 ANR
  - 静态注册的广播在 Android 8.0+ 受限
```

### 4.2 广播类型

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         广播类型                                            │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 无序广播（Normal Broadcast）
  ─────────────────────────────────────────────────────────────────────────
  - 没有跨接收者结果传递/执行顺序保证，不承诺同一时刻并行执行
  - 无法拦截，无法修改
  - 效率高
  - sendBroadcast() 发送

  2. 有序广播（Ordered Broadcast）
  ─────────────────────────────────────────────────────────────────────────
  - 有序链传递结果；现代版本不应依赖跨进程 priority 全局排序
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

静态 receiver 随包安装被解析，但“应用没进程也能唤起”受 stopped 状态、广播豁免、Direct Boot、用户与权限等限制，不是永久无条件有效。

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <application>
        <receiver android:name=".BootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>
    </application>
</manifest>
```

```java
public class BootReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            // 调度适合的短工作/持久任务；不在这里无条件拉起 Activity/FGS。
        }
    }
}
```

动态注册应按需要明确 exported 属性。以下为 Android 17 同应用广播示例；兼容更低 API 可使用 AndroidX 对应封装，但不把库实现冒充 AOSP：

```java
public class MainActivity extends Activity {
    private boolean registered;
    private final BroadcastReceiver receiver = new BroadcastReceiver() {
        @Override public void onReceive(Context context, Intent intent) {
            if ("com.example.DATA_CHANGED".equals(intent.getAction())) {
                // 校验 payload 后更新轻量状态。
            }
        }
    };
    @Override protected void onStart() {
        super.onStart();
        registerReceiver(receiver, new IntentFilter("com.example.DATA_CHANGED"),
                Context.RECEIVER_NOT_EXPORTED);
        registered = true;
    }
    @Override protected void onStop() {
        if (registered) {
            unregisterReceiver(receiver);
            registered = false;
        }
        super.onStop();
    }
}
```

跨应用或来自某些特权应用进程的广播可能需要 EXPORTED；结合发送者权限和内容校验，不能把 NOT_EXPORTED 当所有系统广播都可接收的万能配置。网络变化优先研究 NetworkCallback，不必为了旧 CONNECTIVITY_ACTION 固定维护广播方案。

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
<permission android:name="com.example.MY_PERMISSION" android:protectionLevel="signature" />

<!-- 2. 发送带权限的广播 -->
<uses-permission android:name="com.example.MY_PERMISSION" />
```

```java
// 发送方：只有已获授该权限的接收者才能接收（声明不等于授权）
sendBroadcast(intent, "com.example.MY_PERMISSION");

// 接收方：只接受已获授指定权限的发送方
registerReceiver(receiver, filter, "com.example.MY_PERMISSION", null,
        Context.RECEIVER_EXPORTED); // 跨应用时仍验证 payload
```

### 4.6 广播限制

Android 8.0 起针对相应 target 限制 manifest 注册的大部分隐式广播；此限制与进程是否活着、包是否 stopped、接收者 exported 和发送权限共同作用。不能把所有系统 action 都列为豁免，也不能把“动态注册”理解为无时效、无权限和无调度限制。

典型需要区分的事件：

| 事件 | 关键语义 |
|---|---|
| BOOT_COMPLETED | 用户正常启动/解锁阶段的启动广播，需 RECEIVE_BOOT_COMPLETED |
| LOCKED_BOOT_COMPLETED | Direct Boot 阶段，**用户尚未解锁**；receiver 需 directBootAware，仅访问设备保护存储 |
| TIME_SET / TIMEZONE_CHANGED / LOCALE_CHANGED | 系统时间/地区变化，按官方豁免与声明条件判断 |
| MY_PACKAGE_REPLACED | 针对自己的包更新；不等于任意 PACKAGE_REPLACED 都获豁免 |
| SCREEN_ON / SCREEN_OFF / BATTERY_CHANGED | 不能仅靠 manifest 订阅所有此类事件；核对 Intent 文档的 registered-only 语义 |
| CONNECTIVITY_ACTION | 历史网络广播，改用适当网络监听 API |

旧文将 PACKAGE_ADDED、PACKAGE_REPLACED、电源/电池等整表写成“全部不受限制”是不成立的。系统 API 是否允许静态注册，应按该 action 文档与当前广播策略核对；省电、缓存进程延迟、后台活动启动限制也不因 action 属于豁免而取消。

### 4.7 常用系统广播

```text
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

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LocalBroadcastManager                               │
└─────────────────────────────────────────────────────────────────────────────┘

特点：
- 只在应用内传播，不跨进程
- 安全性高，其他应用无法发送/接收
- 效率高，不经过系统 Binder
- 不受 Android 8.0+ 限制
- 不受系统广播完成 ACK 计时，但阻塞主线程仍可能引发输入等 ANR

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

```text
推荐替代方案：
─────────────────────────────────────────────────────────────────────────

1. LiveData / Flow（推荐）
   - 生命周期感知
   - Flow 必须结合 repeatOnLifecycle 等收集；不会凭类型自动取消

2. EventBus / RxBus
   - 更灵活的事件总线
   - 支持线程切换

3. 自定义回调接口
   - 简单直接
   - 适合简单场景
```

### 4.9 广播原理

Android 17 固定 tag 的服务端实现是 `BroadcastController`、`BroadcastQueueImpl` 与 `BroadcastProcessQueue` 等，不是只存在 fgQueue/bgQueue 两条旧全局队列，也不是把上一版 `BroadcastQueueModernImpl` 名字照搬过来。

```text
ContextImpl.sendBroadcast / sendOrderedBroadcast
  -> AMS Binder entry -> BroadcastController
       resolve candidates / permission / exported / skip checks
  -> BroadcastQueueImpl
       per-process BroadcastProcessQueue, runnable/cold-start scheduling
  -> manifest receiver:
       IApplicationThread.scheduleReceiver
       ActivityThread.handleReceiver -> instantiate/dispatch onReceive
  -> registered receiver:
       IIntentReceiver delivery -> LoadedApk.ReceiverDispatcher
       Handler/Runnable -> onReceive
  -> PendingResult.finish / finishReceiver -> server completion
```

`FLAG_RECEIVER_FOREGROUND` 是广播调度/超时分类，不是“接收 App 当前有前台 Activity”。BroadcastQueueImpl 用相应前后台常量构建超时记录，并通过 ANR timer 路径处理；配置、调试器、豁免及调度因素都可能影响结果。不能把任意 onReceive 的预算写死为“10 秒/60 秒”。

动态注册允许指定调度 Handler，因此其 onReceive 不必永远在主线程；manifest receiver 通常由 ActivityThread 主线程分发。同进程主线程上的普通广播当然不会真的同时运行多个 onReceive。

### 4.10 BroadcastReceiver 常见问题

**goAsync 是否自动给 30 秒？** 不。它将 PendingResult 从同步回调移交给异步工作，仍必须在总的广播完成期限内调用 finish；排队等待工作线程的时间也消耗预算。它不是持久任务调度器，进程消失仍会中断工作。

```java
public final class ShortReceiver extends BroadcastReceiver {
    // 示例由应用生命周期拥有并限制并发的工作执行器。
    private static final ExecutorService WORK = Executors.newSingleThreadExecutor();
    @Override public void onReceive(Context context, Intent intent) {
        PendingResult result = goAsync();
        try {
            WORK.execute(() -> {
                try {
                    // 只做有界短工作；长任务交给合适的调度器。
                    processSmallPayload(intent);
                } finally {
                    result.finish();
                }
            });
        } catch (RejectedExecutionException failure) {
            result.finish();
        }
    }
}
```

`processSmallPayload` 是业务占位方法，示例未编译。生产实现要限制任务队列，避免前序工作占满完成期限。动态注册的注销应与注册作用域配对，不一定只能 onDestroy；如果 onStart 注册，onStop 注销更准确。

## 5. ContentProvider

### 5.1 ContentProvider 是什么

```text
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

ContentResolver 先获取目标 IContentProvider，再调用数据接口。AMS/ContentProviderHelper 负责查找或拉起 Provider，并不替每次 query 代理转发 Cursor：

```text
client ContentResolver.query(uri, ...)
  -> acquireProvider / acquireUnstableProvider
       -> ActivityThread.acquireProvider
       -> AMS.getContentProvider -> ContentProviderHelper
            resolve authority / permissions / user / process
            wait for publish if provider process is starting
       <- IContentProvider binder handle
  -> IContentProvider.query(...) -----------------> provider process
                                                    ContentProvider.Transport
                                                    permission checks
                                                    provider.query(...)
  <- cursor adapter / CursorWindow / data
```

同进程 Provider 可以直接在调用线程执行；跨进程请求通常在 Provider 进程 Binder 线程池执行。`ContentProviderNative` 是 Java Binder Stub，不是“Native C++ 数据库层”。每个 CRUD 方法需要考虑并发与 caller 身份，Provider 自己的 onCreate 则在进程绑定的主线程阶段执行。

### 5.3 ContentProvider 启动流程（经典面试题）

Provider 不只在其他进程首次访问时创建。应用因 Activity、Service 或广播启动时，`handleBindApplication()` 也会安装本进程所分配的 provider 列表；其他进程访问某 authority 只是拉起该进程的一种触发方式。

固定 tag 中普通、非 restricted-backup 绑定应用路径的顺序是：

```text
ActivityThread.handleBindApplication(data)
  -> data.info.makeApplicationInner(data.restrictedBackupMode, null)
       -> instantiate Application through Instrumentation/AppComponentFactory
       -> Application.attach(context)
            -> attachBaseContext(context)
  -> mInitialApplication = app
  -> if not restrictedBackupMode and providers non-empty:
       installContentProviders(app, data.providers)
         -> for providers assigned to this process:
              installProvider -> instantiateProvider
              -> ContentProvider.attachInfo(context, ProviderInfo)
                   -> provider.onCreate()
         -> ActivityManager.getService().publishContentProviders(...)
  -> mInstrumentation.callApplicationOnCreate(app)
  -> later component transactions/callbacks
```

**发布发生在 installContentProviders 内，因此早于后续 Application.onCreate。** 不能把 Application.onCreate 同时画在 providers 前和后，也不能写成遍历所有进程的 manifest Provider。Direct Boot、用户状态和 restricted backup 会改变传入列表及是否安装。

早发布使外部客户端可能在 Application.onCreate 尚未完成时访问 Provider。Provider 不能依赖 Application.onCreate 才初始化的静态字段；其自身 onCreate 只做轻量准备，数据服务必须能够独立、安全地完成首次访问。

`ContentProvider` 的真实源码路径是 `core/java/android/content/ContentProvider.java`，不是 android/app。attachInfo 在 onCreate 前注入 Context，因此 onCreate 中可使用 getContext，但不应进行大 I/O 或长阻塞。

### 5.4 Application 启动流程

```text
Activity / Service / Receiver / Provider demand
  -> system resolves component + process
  -> if missing: process startup through AMS / Zygote machinery
  -> ActivityThread.main -> main Looper -> attach
  -> server bindApplication -> ActivityThread.handleBindApplication
       -> Application construction
       -> attachBaseContext
       -> process-local Provider attachInfo/onCreate + publish
       -> Application.onCreate
  -> component-specific work
```

这张图是责任顺序，不把 `ActivityThread.attach()` 与 makeApplicationInner 描述为同一同步调用栈。Activity 启动入口主要是 ATMS，AMS 承担进程管理，不能继续引用 `ActivityManagerNative.getDefault()` 的旧名称。

正常应用每次进程生命周期有自己的 Application 实例；多进程有多个实例，不能用单例跨进程共享状态。测试 instrumentation、特殊加载与系统进程路径另行分析，不将“每个进程一次”扩大到任何场景。

进程优先级不是由“最初是 Activity/Provider/广播启动”永久确定。系统综合当前组件状态、绑定依赖、可见性和调用关系调整 OOM adj；Provider 依赖还可能提升服务端优先级。

```java
// API 28+ 的公开进程名读取；在附着 Context 后使用上下文相关服务。
String process = Application.getProcessName();
if (process.endsWith(":push")) {
    // 只初始化该进程确实需要的模块。
} else {
    // 主进程关键初始化；非关键工作按线程约束延迟处理。
}
```

非必要库可以延迟初始化，但不能盲目移至子线程：某些 SDK/View/Handler 要求主线程。App Startup 的依赖声明能管理同一初始化体系内的顺序，不会消除 Provider 本身，也不保证其他独立 Provider 的任意依赖自然满足。

### 5.5 ContentProvider 核心方法

```text
┌─────────────────┬─────────────────────────────────────────────────────────┐
│       方法       │                      说明                                │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ onCreate()       │ 初始化，在主线程调用                                    │
│ query()          │ 查询数据，返回 Cursor                                   │
│ insert()         │ 插入数据，返回新记录的 Uri                               │
│ update()         │ 更新数据，返回受影响的行数                               │
│ delete()         │ 删除数据，返回受影响的行数                               │
│ getType()        │ 返回 MIME 类型                                          │
│ call()           │ 自定义方法调用（基础 call API 11 起；重载按 API 区分）                          │
│ bulkInsert()     │ 批量插入                                                │
│ applyBatch()     │ 批量操作                                                │
└─────────────────┴─────────────────────────────────────────────────────────┘

MIME 类型格式：
- 单条记录：vnd.android.cursor.item/vnd.com.example.user
- 多条记录：vnd.android.cursor.dir/vnd.com.example.users
```

### 5.6 自定义 ContentProvider 示例与 URI 约束

下面提供可审阅的 CRUD 核心，省略 imports 与具体数据库 schema。`DbHelper` 为应用实现的 SQLiteOpenHelper，建库/迁移须另行实现；不要将其称为复制即编译的完整工程。关键是所有操作验证 URI、单条路径加入 `_id` 限制、绑定参数不拼用户值、Cursor 设置通知 URI。

```java
public class UserProvider extends ContentProvider {
    private static final String AUTHORITY = "com.example.provider";
    private static final Uri USERS = Uri.parse("content://" + AUTHORITY + "/users");
    private static final int DIR = 1, ITEM = 2;
    private static final UriMatcher MATCH = new UriMatcher(UriMatcher.NO_MATCH);
    static {
        MATCH.addURI(AUTHORITY, "users", DIR);
        MATCH.addURI(AUTHORITY, "users/#", ITEM);
    }
    private DbHelper helper;

    @Override public boolean onCreate() {
        helper = new DbHelper(requireContext()); // 不在此打开/迁移数据库。
        return true;
    }

    private int match(Uri uri) {
        if (!"content".equals(uri.getScheme()) || !AUTHORITY.equals(uri.getAuthority())) {
            throw new IllegalArgumentException("Wrong authority/scheme");
        }
        int kind = MATCH.match(uri);
        if (kind != DIR && kind != ITEM) throw new IllegalArgumentException("Unknown URI");
        return kind;
    }

    // 示例收敛为固定列/排序，拒绝外部传 SQL，避免伪完整的任意表达式接口。
    private void checkQuery(String[] projection, String selection, String[] args, String order) {
        if (projection != null || selection != null || args != null || order != null) {
            throw new IllegalArgumentException("This example only supports fixed queries");
        }
    }
    private String where(Uri uri) { return match(uri) == ITEM ? "_id=?" : null; }
    private String[] args(Uri uri) {
        return match(uri) == ITEM ? new String[]{Long.toString(ContentUris.parseId(uri))} : null;
    }

    private ContentValues safeValues(ContentValues input) {
        if (input == null || input.size() == 0) throw new IllegalArgumentException("Empty values");
        ContentValues result = new ContentValues();
        for (String key : input.keySet()) {
            if ("name".equals(key)) {
                String name = input.getAsString(key);
                if (name == null || name.length() > 200) throw new IllegalArgumentException("name");
                result.put(key, name);
            } else if ("age".equals(key)) {
                Integer age = input.getAsInteger(key);
                if (age == null || age < 0 || age > 150) throw new IllegalArgumentException("age");
                result.put(key, age);
            } else {
                throw new IllegalArgumentException("Unsupported column");
            }
        }
        return result;
    }

    @Override public Cursor query(Uri uri, String[] projection, String selection,
            String[] selectionArgs, String sortOrder) {
        checkQuery(projection, selection, selectionArgs, sortOrder);
        Cursor cursor = helper.getReadableDatabase().query("users",
                new String[]{"_id", "name", "age"}, where(uri), args(uri),
                null, null, "_id ASC");
        cursor.setNotificationUri(requireContext().getContentResolver(), USERS);
        return cursor; // 调用方关闭 Cursor。
    }

    @Override public Uri insert(Uri uri, ContentValues values) {
        if (match(uri) != DIR) throw new IllegalArgumentException("Insert requires directory URI");
        long id = helper.getWritableDatabase().insertOrThrow("users", null, safeValues(values));
        requireContext().getContentResolver().notifyChange(USERS, null);
        return ContentUris.withAppendedId(USERS, id);
    }

    @Override public int update(Uri uri, ContentValues values, String selection, String[] suppliedArgs) {
        checkQuery(null, selection, suppliedArgs, null);
        int changed = helper.getWritableDatabase().update("users", safeValues(values), where(uri), args(uri));
        if (changed != 0) requireContext().getContentResolver().notifyChange(USERS, null);
        return changed;
    }

    @Override public int delete(Uri uri, String selection, String[] suppliedArgs) {
        checkQuery(null, selection, suppliedArgs, null);
        int changed = helper.getWritableDatabase().delete("users", where(uri), args(uri));
        if (changed != 0) requireContext().getContentResolver().notifyChange(USERS, null);
        return changed;
    }

    @Override public String getType(Uri uri) {
        return match(uri) == DIR ? "vnd.android.cursor.dir/vnd.example.users"
                                : "vnd.android.cursor.item/vnd.example.user";
    }
}
```

同应用使用可设置 exported=false；若要对外开放，定义并授予所需权限，不能只写一个未声明的权限字符串。目录 URI 的 update/delete 在本示例影响全表，应由产品接口决定是否允许，敏感应用可直接拒绝 DIR 写入。

```xml
<provider
    android:name=".UserProvider"
    android:authorities="com.example.provider"
    android:exported="false" />
```

跨进程 query 常在 Binder 线程上执行，但同进程 ContentResolver 调用可直接在调用线程执行，因此数据库首次打开不能依靠“Provider 一定后台”规避主线程 I/O。客户端仍应异步请求，并处理取消与异常。

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
        // 批量 IPC；是否单事务由 Provider 实现保证，默认实现不保证
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

#### 批量原子性与通知时机

`ContentProvider.applyBatch()` 默认逐个应用 operation，`bulkInsert()` 默认循环 insert，不自动开启数据库事务。若需要全成全败，Provider 必须 beginTransaction，执行操作并检查结果，成功后 setTransactionSuccessful，finally 中 endTransaction；只在提交成功后一次 notifyChange。旧例逐条 insert 通知若原样放入事务，可能在回滚前泄露错误的变更信号。

不同数据库或跨 Provider 操作没有自动分布式事务。批量过大仍可能触及 Binder/内存限制，应按业务分块并说明各块是否允许部分成功。

### 5.10 ContentProvider 权限控制

```xml
<!-- 1. 声明权限 -->
<permission
    android:name="com.example.READ_USER"
    android:label="Read User"
    android:protectionLevel="signature" />
    
<permission
    android:name="com.example.WRITE_USER"
    android:label="Write User"
    android:protectionLevel="signature" />

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

```

```java
// 持有授权能力的发送方通过 Intent 向接收方临时授予 URI 权限
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
// 节选：仅展示 Room 初始化/query；其他 ContentProvider 抽象方法须完整实现。
public abstract class RoomProvider extends ContentProvider {
    
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

Room 的 build() 不等于在主线程完成查询。该同步 DAO 在同进程主线程访问时仍可能被 Room 拒绝；不要用 allowMainThreadQueries 掩盖调用线程问题。query 返回 Cursor 要设置通知 URI，写操作也要提供 notifyChange 与权限/URI 校验。

### 5.12 常用系统 ContentProvider

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         常用系统 ContentProvider                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬───────────────────────────────────────────────────────┐
│  Provider           │  URI                                      │  说明     │
├─────────────────────┼───────────────────────────────────────────────────────┤
│  Contacts           │  ContactsContract.Contacts.CONTENT_URI               │  联系人   │
│  CallLog            │  content://call_log/calls                │  通话记录 │
│  MediaStore.Images  │  content://media/external/images/media   │  图片     │
│  MediaStore.Video   │  content://media/external/video/media    │  视频     │
│  MediaStore.Audio   │  content://media/external/audio/media    │  音频     │
│  MediaStore.Files   │  content://media/external/file           │  文件     │
│  Calendar           │  content://com.android.calendar/events   │  日历     │
│  Browser            │  历史 Browser URI（非 17 通用公开契约）             │  书签     │
│  Settings           │  content://settings/system               │  系统设置 │
│  UserDictionary     │  content://user_dictionary/words         │  用户词典 │
│  Downloads          │  使用 DownloadManager 公共 API（不要依赖内部 URI）        │  下载     │
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
                 MediaStore.Images.Media.DISPLAY_NAME},
    null, null, 
    MediaStore.Images.Media.DATE_ADDED + " DESC");
```

### 5.13 ContentProvider 常见问题

```text
Q1: ContentProvider 的方法在哪个线程执行？
A: 常规安装时 onCreate 在主线程；跨进程请求在 Provider 的 Binder 线程，本地调用可在调用者线程

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

```text
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
1. Activity/Service/Provider 及静态 Receiver 需在 Manifest 注册；动态 Receiver 例外
2. 都有独立的生命周期
3. 都由系统管理
4. 都支持跨进程通信
```

---

## 7. 进程间通信 IPC

```text
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

```text
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

```text
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

以下层级是理解用的进程重要性模型，不是 Android 17 OOM adj 的完整枚举。实际优先级由 OomAdjuster/绑定依赖/可见状态等动态计算；前台服务不是 top Activity，持续执行回调也不等于永久最高优先级。

```text
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
  │     • 正在执行特定回调的 Service（前台服务常态另有独立重要性）                               │
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

```text
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
  3. BroadcastReceiver.onReceive() 执行时间短，长工作交合适调度器；不能无条件后台启动 Service
  4. 多进程架构中，每个进程有独立的组件生命周期
```

### 10.2 组件间通信最佳实践

```text
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
  │     缺点：受进程共享 Binder 事务缓冲预算限制                                         │
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

```text
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

```text
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
  解决：由 lifecycle/cancellation 管理回调，重建后重新订阅；仅弱引用或 isFinishing 不足以保证有效

  坑4：透明 Activity 导致生命周期异常
  ─────────────────────────────────────────────────────────────────────────
  问题：透明 Activity 不会触发下方 Activity 的 onStop
  原因：下方 Activity 仍然部分可见
  解决：注意 onPause 和 onStop 的区别，在 onPause 中也做必要的资源释放
```

```text
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
  问题：后台服务受到启动和执行限制，停止服务与进程被杀是不同事件
  解决：使用 ForegroundService / WorkManager / JobScheduler

  坑4：IntentService 内存泄漏
  ─────────────────────────────────────────────────────────────────────────
  问题：IntentService 持有 Context 引用（已废弃）
  解决：按任务选择 WorkManager/CoroutineWorker 等；JobIntentService 也已弃用
```

```text
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
  解决：goAsync 移交完成责任但不延长为固定 30 秒；长工作交合适调度器

  坑4：有序广播优先级设置无效
  ─────────────────────────────────────────────────────────────────────────
  问题：android:priority 设置了但没生效
  原因：动态注册和静态注册的优先级范围不同
        动态注册优先级始终高于静态注册
  解决：同一注册方式内比较 priority 值（-1000 到 1000）
```

```text
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

```text
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

```text
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
public class ModuleAInitializer implements Initializer<ModuleA> {
    @NonNull
    @Override
    public ModuleA create(@NonNull Context context) {
        // 模块 A 初始化逻辑
        return ModuleA.init(context); // 约定返回非空 ModuleA 实例
    }

    @NonNull
    @Override
    public List<Class<? extends Initializer<?>>> dependencies() {
        // 依赖其他 Initializer（控制初始化顺序）
        return Collections.emptyList();
    }
}

```

```xml
<!-- 在声明 tools namespace 的 manifest/application 中合并 -->
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

```text
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
      AppExecutors.background().execute(() -> { // 应用拥有并负责关闭的共享执行器
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

```text
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

```text
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
  - 有界短异步操作：goAsync，仍受广播整体完成期限约束
  - 长操作：调度合适工作，启动 Service/FGS 仍须满足系统条件

  // goAsync() 示例
  public class MyReceiver extends BroadcastReceiver {
      @Override
      public void onReceive(Context context, Intent intent) {
          final PendingResult pendingResult = goAsync();
          
          new Thread(() -> {
              try {
                  // 仅做有界短工作；不是固定 30 秒预算
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

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ContentProvider 性能优化                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  优化1：批量操作代替单条操作
  ─────────────────────────────────────────────────────────────────────────
  - 使用 applyBatch() 减少 IPC；Provider 实现事务才具备原子性
  - 使用 bulkInsert() 批量插入
  - 减少 Binder 调用次数

  优化2：query 结果集优化
  ─────────────────────────────────────────────────────────────────────────
  - 使用 projection 限制查询列
  - 使用 selection 过滤行
  - 使用 Provider 支持的结构化 query 参数分页；不要通用拼接 sortOrder + limit
  - 及时关闭 Cursor

  优化3：notifyChange 优化
  ─────────────────────────────────────────────────────────────────────────
  - 批量操作完成后调用一次
  - 在 registerContentObserver 中用 notifyForDescendants 控制对子路径的监听
  - 避免在循环中反复调用

  优化4：异步查询
  ─────────────────────────────────────────────────────────────────────────
  - 使用 CursorLoader（已废弃）或自定义 Loader
  - 使用 Coroutines 异步查询
  - 使用 ContentProviderClient 管理连接
```

### 10.6 Android 版本演进对四大组件的影响

版本史必须区分运行系统版本、target SDK 和 API 引入时间，不能把旧限制搬到 Android 17 再称为新增。

| 阶段 | 与本文相关的真实变化/边界 |
|---|---|
| API 24 | 多窗口与 Direct Boot；相关 target 下 CONNECTIVITY_ACTION manifest 接收受限 |
| API 26 | 后台 Service/隐式广播限制；startForegroundService 请求不等于已成为前台服务 |
| API 28 target | onSaveInstanceState 的正常 stop 保存顺序在 onStop 之后；非 SDK 接口限制需要单独评估 |
| Android 10+ | Activity 管理由 ATMS/任务体系承担；多窗口 multi-resume 不支持“全局只能一个 resumed”口诀 |
| Android 12 相应 target | 带 intent-filter 的组件显式 exported；后台启动 FGS 受限制 |
| Android 13/14 相应 target | 通知权限、前台服务类型/类型权限、动态 receiver 导出属性等分别生效 |
| Android 17 固定 tag | 客户端 Activity transaction items、BroadcastQueueImpl 按进程调度、Provider 安装与发布顺序见本文源码链 |

Provider 的 exported 默认值变化不是 Android 10 才引入，较早 target 行为已不同；现代工程应显式声明。自定义广播不会在 Android 11 默认变成 ordered=true，发送方式仍由 sendBroadcast/sendOrderedBroadcast 区分。

前台服务是“用户可感知并符合用途”的任务机制，不是永久保活 API。声明 foregroundServiceType、对应权限以及摄像头/麦克风/定位等运行时前提后，还须满足启动来源限制，及时提供通知，并在任务结束停止服务。

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
    <application>
        <service android:name=".MusicService"
            android:exported="false"
            android:foregroundServiceType="mediaPlayback" />
    </application>
</manifest>
```

```java
// 服务已经通过合法路径启动，并已创建有效通知渠道。
startForeground(notificationId, notification,
        ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK);
```

常见类型包括 camera、microphone、location、mediaPlayback、mediaProjection、dataSync、health、connectedDevice 等，具体类型有各自前置条件和超时；shortService 并非“仅系统能用”，systemExempted 也不是应用自填字符串即可豁免。

`ActiveServices.scheduleServiceForegroundTransitionTimeoutLocked()` 读取服务转换期限，`serviceForegroundTimeout()` 执行超时处理。前台通知延迟展示与这个转换期限是两回事；不要写成“一律 5 秒”“一律延迟 10 秒”，更不要用通知尚未显示判断 startForeground 一定未调用。

适配应该回归：冷启动/复用/旋转/进程死亡恢复、多窗口和 top-resumed、Service 启动与绑定交叉、广播 export/权限/异步完成、Direct Boot 与 Provider 提前初始化。这里列出的是需要进行的设备测试，不代表本轮已执行。

## 11. 面试高频题精选

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Activity 相关面试题                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  Q1: Activity 常见启动模式如何选择？
  ─────────────────────────────────────────────────────────────────────────
  A:
  - standard：默认模式，适合大多数普通页面
  - singleTop：适合消息详情页、通知点击页（避免栈顶重复创建）
  - singleTask：适合应用主页面（如微信主页，返回时清除上层）
  - singleInstance：确实需要独占 task 时使用；不是只限系统
- singleInstancePerTask：每任务 root 单实例，可依规则存在于多个任务

  Q2: onSaveInstanceState 和 onRestoreInstanceState 的调用时机？
  ─────────────────────────────────────────────────────────────────────────
  A:
  调用时机：
  - onSaveInstanceState：target >= 28 的正常 stop 保存路径在 onStop 之后；是否调用有条件
  - onRestoreInstanceState：在 onStart 之后、onResume 之前
  
  触发条件（onSaveInstanceState）：
  - 按 Home 键
  - 启动新 Activity
  - 屏幕旋转
  - 切换到其他应用
  主动 finish 通常不保存；Back 可能将根任务退到后台，不应按键名绝对判断

  注意：
  - 不要和持久化存储混淆，这只是临时状态保存
  - Bundle 受共享 Binder 事务预算限制，只存小型可恢复状态

  Q3: Activity 启动过程经历了哪些主要步骤？
  ─────────────────────────────────────────────────────────────────────────
  A:
  1. 调用 Activity.startActivity()
  2. Instrumentation.execStartActivity()
  3. 通过 Binder 调用 ATMS.startActivityAsUser()
  4. ATMS 解析 Intent，查找目标 Activity
  5. 如果目标进程不存在，通过 Socket 通知 Zygote fork 新进程
  6. 新进程中 ActivityThread.main() 启动
  7. 通过 ApplicationThread.scheduleTransaction() -> LaunchActivityItem.execute() 回调
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

```text
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
  - 合法启动后立即调用 startForeground；实际转换期限由系统配置，不写死 5 秒
  
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

```text
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
  
  有序回调可传结果/按条件中止；不能依赖跨进程 priority 的全局顺序

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

```text
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

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    综合面试题                                               │
└─────────────────────────────────────────────────────────────────────────────┘

  Q14: 四大组件可以不注册直接使用吗？
  ─────────────────────────────────────────────────────────────────────────
  A:
  - Activity：必须注册，否则抛出 ActivityNotFoundException
  - Service：必须注册；startService 找不到目标可返回 null，bindService 可返回 false；权限/限制还可能抛异常，不存在通用 ServiceNotFoundException
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
  1. 系统组件通过 Manifest 注册；动态 Receiver 使用运行时注册
  2. 都有独立的生命周期
  3. 都由系统服务管理（不由应用控制）
  4. 都支持跨进程通信
  5. Activity/Service/Receiver 使用 Intent；Provider 使用 URI/参数等协议

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


**固定 tag 源码证据：**

- [handleBindApplication / installContentProviders / performLaunchActivity / performStopActivityInner](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/ActivityThread.java)
- [makeApplicationInner / ReceiverDispatcher](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/LoadedApk.java)
- [attach / lifecycle APIs](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Activity.java)
- [started and bound lifecycle / onRebind](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Service.java)
- [startPausing / completePause](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/TaskFragment.java)
- [realStartActivityLocked](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java)
- [execute / lifecycle transition](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/TransactionExecutor.java)
- [execute](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/servertransaction/LaunchActivityItem.java)
- [service start/bind / foreground timeout](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ActiveServices.java)
- [receiver registration / exported checks](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/BroadcastController.java)
- [delivery scheduling / timeout](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/BroadcastQueueImpl.java)
- [goAsync / PendingResult.finish](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/content/BroadcastReceiver.java)
- [getContentProvider / publishContentProviders](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/ContentProviderHelper.java)
- [attachInfo / Transport / applyBatch / bulkInsert](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/content/ContentProvider.java)
