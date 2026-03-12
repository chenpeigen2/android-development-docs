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

## 2. SystemUI 启动流程

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SystemUI 启动架构                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         System Server 进程                                 │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                    SystemServer.main()                           │    │
│  │                                                                   │    │
│  │   1. startBootstrapServices()  - 引导服务                       │    │
│  │   2. startCoreServices()      - 核心服务                       │    │
│  │   3. startOtherServices()    - 其他服务                         │    │
│  │                              │                                  │    │
│  │                              ▼                                  │    │
│  │   ┌────────────────────────────────────────────────────────┐   │    │
│  │   │  SystemServiceManager.startServiceAsUser()            │   │    │
│  │   │  - 启动 SystemUIService                               │   │    │
│  │   └────────────────────────────────────────────────────────┘   │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                    │                                      │
│                                    ▼                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SystemUIService.onStart()                              │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  1. 获取 SystemUIApplication                                   │    │
│  │     final Object app = getApplication();                       │    │
│  │     ((SystemUIApplication) app).startServicesIfNeeded();      │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                    │                                      │
│                                    ▼                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   SystemUIApplication.startServicesIfNeeded()               │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  配置数组: mServices                                             │    │
│  │                                                                   │    │
│  │  final SystemUI[] SERVICES = new SystemUI[] {                   │    │
│  │      new StatusBar(),              // 状态栏                     │    │
│  │      new KeyguardView(),           // 锁屏                       │    │
│  │      new NotificationPanel(),       // 通知面板                   │    │
│  │      new VolumeUI(),               // 音量条                     │    │
│  │      new PowerUI(),                 // 电源菜单                   │    │
│  │      new Recents(),                // 最近任务                   │    │
│  │      new SystemBars(),              // 系统栏                     │    │
│  │      new NavigationBar(),           // 导航栏                     │    │
│  │      new StatusBar(),               // 状态栏                     │    │
│  │      new Magnification(),           // 放大镜                     │    │
│  │      new DirectionalPad(),          // 方向键                    │    │
│  │      new Shadow(),                 // 阴影                        │    │
│  │      new Pips(),                   // PiP                        │    │
│  │      new VpnDialogs(),              // VPN对话框                  │    │
│  │      new WorkChallenge(),          // 工作模式挑战                │    │
│  │  };                                                          │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                    │                                      │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │  循环启动每个服务:                                               │    │
│  │  for (SystemUI service : mServices) {                           │    │
│  │      service.start();                                           │    │
│  │  }                                                             │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 详细启动流程

```java
/**
 * SystemUI 启动源码分析
 */

// SystemUIService.java
public class SystemUIService extends Service {
    
    @Override
    public void onCreate() {
        super.onCreate();
        
        // 获取 SystemUIApplication
        // SystemUIApplication 是一个 Application
        final Object app = getApplication();
        
        // 启动所有 SystemUI 组件
        if (app instanceof SystemUIApplication) {
            ((SystemUIApplication) app).startServicesIfNeeded();
        }
    }
    
    @Override
    public void onStart(Intent intent, int startId) {
        // SystemUI 服务启动完成
    }
}

// SystemUIApplication.java
public class SystemUIApplication extends Application {
    
    // SystemUI 组件配置
    private static final Class<? extends SystemUI>[] SERVICES = new Class[] {
        // 核心组件
        StatusBar.class,           // 状态栏
        NavigationBar.class,       // 导航栏
        NotificationPanel.class,   // 通知面板
        KeyguardView.class,        // 锁屏
        VolumeUI.class,            // 音量条
        PowerUI.class,            // 电源菜单
        Recents.class,            // 最近任务
        SystemBars.class,         // 系统栏
        // 其他组件
        Magnification.class,
        DirectionalPad.class,
        Shadow.class,
        Pips.class,
        VpnDialogs.class,
        WorkChallenge.class,
    };
    
    @Override
    public void onCreate() {
        super.onCreate();
        // 保存 Application 实例
        sInstance = this;
        
        // 设置 System 属性
        System.setProperty("sys.systemui.volume", "true");
        System.setProperty("sys.systemui.navbars", "true");
    }
    
    public void startServicesIfNeeded() {
        // 过滤需要启动的服务
        final int N = mServicesConfig.length;
        for (int i = 0; i < N; ++i) {
            final Class<? extends SystemUI> clss = mServicesConfig[i];
            
            // 创建服务实例
            mServices[i] = clss.getConstructor(Context.class).newInstance(this);
            
            // 调用 start() 方法
            mServices[i].start();
            
            // 配置依赖注入
            mServices[i].configure();
        }
    }
}
```

### 2.3 组件启动时序

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SystemUI 组件启动时序                                    │
└─────────────────────────────────────────────────────────────────────────────┘

时间线:
│
├─── SystemServer 启动
│   │
│   ├─── SystemUIService.onCreate()
│   │
│   └─── SystemUIApplication.startServicesIfNeeded()
│       │
│       ├─── 1️⃣ SystemBars.start()
│       │      - 创建 StatusBarWindow
│       │      - 创建 NavigationBar
│       │      - 加载布局
│       │
│       ├─── 2️⃣ StatusBar.start()
│       │      - 创建状态栏图标
│       │      - 创建通知图标容器
│       │      - 注册广播接收器
│       │
│       ├─── 3️⃣ NavigationBar.start()
│       │      - 创建导航栏视图
│       │      - 配置导航栏按钮
│       │
│       ├─── 4️⃣ NotificationPanel.start()
│       │      - 创建通知面板
│       │      - 注册 NotificationListenerService
│       │      - 连接到 NotificationManagerService
│       │
│       ├─── 5️⃣ KeyguardView.start()
│       │      - 创建锁屏视图
│       │      - 配置解锁方式
│       │      - 启动 KeyguardService
│       │
│       ├─── 6️⃣ VolumeUI.start()
│       │      - 创建音量条
│       │      - 注册 AudioManager 监听
│       │
│       ├─── 7️⃣ PowerUI.start()
│       │      - 创建电源菜单
│       │      - 注册 BatteryManager 监听
│       │
│       └─── 8️⃣ Recents.start()
│              - 创建最近任务视图
│              - 配置任务缩略图
│
└─── SystemUI 启动完成

启动顺序设计原则:
1. 基础组件先启动 (SystemBars, StatusBar)
2. UI 组件后启动 (NotificationPanel, Keyguard)
3. 依赖关系: NotificationPanel 依赖 StatusBar
4. 每个组件独立初始化，互不阻塞
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

### 3.2 AOD 架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AOD 架构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          应用层                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Settings (设置)                                │   │
│  │   - AOD 开关                                                      │   │
│  │   - AOD 显示内容设置                                              │   │
│  │   - 勿扰模式设置                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Framework 层 (PowerManager)                         │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        DozeService                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │                    DozeMachine                               │  │   │
│  │  │                                                              │  │   │
│  │  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │  │   │
│  │  │  │DOZE_INIT│───▶│DOZE_AOD│───▶│DOZE_REST│───▶│EXITEDOZE││  │   │
│  │  │  │  初始化 │    │  AOD显示 │    │  浅睡眠  │    │  退出   │ │  │   │
│  │  │  └─────────┘    └─────────┘    └─────────┘    └─────────┘ │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     PowerManagerService                             │   │
│  │   - 控制 Doze 状态                                                │   │
│  │   - 管理WakeLock                                                  │   │
│  │   - 与 HAL 交互                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SystemUI 层 (AODView)                               │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         AODController                              │   │
│  │   - 管理 AOD 显示状态                                              │   │
│  │   - 控制 DozeParameter                                             │   │
│  │   - 与 PowerManager 交互                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         AODView                                      │   │
│  │   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐         │   │
│  │   │  AODClockView │  │AODNotification│  │AODBurnInView │         │   │
│  │   │    时钟视图    │  │   通知视图    │  │  防烧屏视图   │         │   │
│  │   └───────────────┘  └───────────────┘  └───────────────┘         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Native 层 (HAL)                                      │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Display HAL                                    │   │
│  │   - 控制屏幕刷新                                                  │   │
│  │   - AOD 模式设置                                                  │   │
│  │   - Always-on 控制                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Power HAL                                      │   │
│  │   - Doze 模式控制                                                 │   │
│  │   - 保持低功耗状态                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 AOD 状态机 (DozeMachine)

```java
/**
 * DozeMachine 状态机
 * 
 * AOD 的核心是 DozeMachine，它管理设备的 Doze 状态
 */

public enum DozeMachine.State {
    // 初始状态
    DOZE_INIT,           // 初始化
    
    // Doze 状态
    DOZE,                // 深度睡眠 (屏幕完全关闭)
    DOZE_AOD,            // AOD 模式 (屏幕部分点亮)
    DOZE_SUSPEND,        // 挂起状态
    
    // 浅睡眠状态
    DOZE_REST,           // 浅睡眠 (等待脉冲)
    
    // 退出状态
    EXITED_DOZE,         // 已退出 Doze
    
    // 过渡状态
    WAITING_FOR_UPDATE,  // 等待更新
    WAITING_FOR_QUIESCENT, // 等待静止
}

// 状态转换图
//
//        ┌─────────────────────────────────────────────┐
//        │                                             │
//        ▼                                             │
//   DOZE_INIT ─────▶ DOZE_AOD ◀────────────────┐    │
//        │              │                          │    │
//        │              │                          │    │
//        ▼              ▼                          │    │
//      DOZE ───────── DOZE_REST ────────────────┘    │
//        │                                              │
//        │                                              │
//        ▼                                              │
//   EXITED_DOZE ◀─────────────────────────────────────┘
//

/**
 * 状态转换触发条件
 */

// 进入 DOZE_AOD (AOD 模式)
transitionToState(DOZE_AOD):
  - 用户主动触发 AOD
  - 屏幕关闭超时
  - 检测到息屏动作

// 进入 DOZE_REST (浅睡眠)
transitionToState(DOZE_REST):
  - 需要更新 AOD 显示内容
  - 传感器事件触发
  - 定时器触发

// 退出 AOD
transitionToState(EXITED_DOZE):
  - 用户触控屏幕
  - 按下电源键
  - 来电
  - 闹钟响铃
```

### 3.4 AOD 显示流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       AOD 显示流程                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. AOD 触发条件检测                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

触发条件:
├── 屏幕关闭 (PowerManager.isScreenOn() = false)
├── 未进入口袋 (光线传感器)
├── 未遮挡 (距离传感器)
├── 电池未过低 (BatteryManager)
└── 用户已开启 AOD (Settings.Global.AOD_ENABLED)

┌─────────────────────────────────────────────────────────────────────────────┐
│  2. 进入 AOD 模式                                                        │
└─────────────────────────────────────────────────────────────────────────────┘

PowerManagerService:
├── 调用 DozeService.requestDoze()
├── 发送 DOZE_REQUEST_PULSE 消息
└── 进入 DOZE_AOD 状态

DisplayControl (HAL):
├── 调用 setAlwaysOnEnabled(true)
└── 切换到 AOD 显示模式

┌─────────────────────────────────────────────────────────────────────────────┐
│  3. AOD 内容渲染                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

AODView 渲染流程:
┌─────────────────────────┐
│  AODController         │
│  - 获取 AOD 配置        │
│  - 准备显示数据         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  AODClockView           │
│  - 绘制时钟             │
│  - 绘制日期             │
│  - 防烧屏移动           │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  AODNotificationView    │
│  - 获取通知数据         │
│  - 绘制通知图标         │
│  - 绘制通知预览         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  AODDisplayView         │
│  - 合成所有视图         │
│  - 写入帧缓冲区         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  SurfaceFlinger         │
│  - 合成显示图层         │
│  - 发送到显示硬件        │
└─────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  4. AOD 更新 (脉冲模式)                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

AOD 更新触发:
├── 定时更新 (每分钟)
├── 通知到达
├── 电池变化
└── 时间变化

脉冲 (Pulse) 流程:
1. 从 DOZE_AOD 进入 DOZE_REST
2. 更新 AOD 显示内容
3. 保持短暂显示
4. 返回 DOZE_AOD
```

### 3.5 AOD 核心组件源码

```java
/**
 * AODController - AOD 控制器的核心
 */

// SystemUI 中 AODController 的主要职责
public class AODController implements doze.DozeHost {
    
    // 依赖注入
    private final PowerManager mPowerManager;
    private final DozeParameter mDozeParameter;
    private final AODView mAODView;
    
    /**
     * 连接到 DozeService
     */
    @Override
    public void connectToDozeService() {
        // 获取 DozeService Binder
        IBinder dozeService = ServiceManager.getService("doze");
        mDozeHost = IDozeHost.Stub.asInterface(dozeService);
        
        // 注册回调
        mDozeHost.registerCallback(this);
    }
    
    /**
     * 请求进入 AOD 模式
     */
    public void requestAOD() {
        if (mDozeHost != null) {
            try {
                mDozeHost.requestState(DozeMachine.State.DOZE_AOD);
            } catch (RemoteException e) {
                // 处理异常
            }
        }
    }
    
    /**
     * 处理 Doze 脉冲
     */
    @Override
    public void onDozePulse(int pulseReason) {
        // pulseReason: 脉冲原因
        // - PULSE_REASON_NOTIFICATION
        // - PULSE_REASON_SENSOR
        // - PULSE_REASON_TAP
        
        switch (pulseReason) {
            case DozeMachine.PULSE_REASON_NOTIFICATION:
                // 通知脉冲 - 显示通知内容
                showNotificationPulse();
                break;
            case Doze_REASON_SENSOR:
                // 传感器脉冲 - 显示时钟等
                showClockPulse();
                break;
            case DozeMachine.PULSE_REASON_TAP:
                // 点击脉冲 - 响应用户点击
                handleTapPulse();
                break;
        }
    }
}

/**
 * AODView - AOD 显示视图
 */
public class AODView extends FrameLayout {
    
    // AOD 时钟
    private TextClock mTimeClock;
    private TextClock mDateClock;
    
    // AOD 通知
    private AODNotificationView mNotificationView;
    
    // 防烧屏
    private BurnInHelper mBurnInHelper;
    
    @Override
    protected void onDraw(Canvas canvas) {
        // 绘制前应用防烧屏偏移
        int offsetX = mBurnInHelper.getOffsetX(getWidth());
        int offsetY = mBurnInHelper.getOffsetY(getHeight());
        
        canvas.save();
        canvas.translate(offsetX, offsetY);
        
        super.onDraw(canvas);
        
        canvas.restore();
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

3. 状态流转
   DOZE_INIT → DOZE_AOD → DOZE_REST → EXITED_DOZE

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

> 本节内容基于 Android 14 源码分析
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

> 本节内容基于 Android 14 源码分析
> 源码路径：frameworks/base/packages/SystemUI/src/com/android/systemui/doze/

### 12.1 AOD 与 PowerManagerService 交互

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD 与 PowerManagerService 交互                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          PowerManagerService                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    电源状态管理                                      │   │
│  │                                                                   │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │  │WakeLock管理  │  │屏幕状态管理  │  │Doze模式管理   │         │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      DozeService                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │                    DozeMachine                               │  │   │
│  │  │  ┌─────────────────────────────────────────────────────┐   │  │   │
│  │  │  │              状态机管理                              │   │  │   │
│  │  │  │  - 状态转换                                        │   │  │   │
│  │  │  │  - 脉冲控制                                        │   │  │   │
│  │  │  │  - 传感器事件                                      │   │  │   │
│  │  │  └─────────────────────────────────────────────────────┘   │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      SystemUI (AOD)                                │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │                    AODController                             │  │   │
│  │  │  - 监听 Doze 状态                                         │  │   │
│  │  │  - 渲染 AOD 内容                                         │  │   │
│  │  │  - 处理脉冲事件                                           │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

交互流程：
```java
// PowerManagerService.java
public class PowerManagerService extends SystemService {
    
    // Doze 模式状态
    private boolean mDozeModeEnabled;
    
    /**
     * 进入 Doze 模式
     */
    public void enterDozeMode() {
        // 1. 设置 Doze 标志
        mDozeModeEnabled = true;
        
        // 2. 降低屏幕亮度
        mDisplayManager.setDozeMode(true);
        
        // 3. 通知 DozeService
        mDozeService.onEnterDoze();
        
        // 4. 释放不必要的 WakeLock
        releaseWakeLocks();
    }
    
    /**
     * 退出 Doze 模式
     */
    public void exitDozeMode() {
        // 1. 清除 Doze 标志
        mDozeModeEnabled = false;
        
        // 2. 恢复屏幕亮度
        mDisplayManager.setDozeMode(false);
        
        // 3. 通知 DozeService
        mDozeService.onExitDoze();
    }
    
    /**
     * 请求 AOD 脉冲
     */
    public void requestDozePulse(int reason) {
        if (mDozeModeEnabled) {
            mDozeService.requestPulse(reason);
        }
    }
}
```

### 12.2 AOD 硬件抽象层 (HAL)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD 硬件抽象层                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          Framework 层 (Java)                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DisplayManagerService                             │   │
│  │  - 设置 AOD 模式                                                    │   │
│  │  - 控制 AOD 参数                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Native 层 (C++)                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DisplayHAL                                       │   │
│  │  - 实现 AOD 接口                                                    │   │
│  │  - 控制显示硬件                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HAL 层                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    AOD HAL                                          │   │
│  │  - setAlwaysOnEnabled()     // 启用/禁用 AOD                        │   │
│  │  - setAodDisplayMode()      // 设置显示模式                         │   │
│  │  - setAodBrightness()       // 设置亮度                             │   │
│  │  - setAodPartialUpdate()    // 部分更新                             │   │
│  │  - setAodIdleTimeout()      // 设置空闲超时                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Kernel 层                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Display Driver                                   │   │
│  │  - 控制 AMOLED 显示                                                │   │
│  │  - 低功耗显示模式                                                   │   │
│  │  - 部分像素点亮                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

HAL 接口定义：
// hardware/interfaces/display/aidl/android/hardware/display/
interface IDisplay {
    void setAlwaysOnEnabled(boolean enabled);
    void setAodDisplayMode(AodDisplayMode mode);
    void setAodBrightness(int brightness);
    void setAodPartialUpdate(Rect region);
}

// AodDisplayMode
parcelable AodDisplayMode {
    int width;
    int height;
    int refreshRate;  // 1 fps for AOD
    int pixelFormat;
    int brightness;
}
```

### 12.3 AOD 传感器集成

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD 传感器集成                                          │
└─────────────────────────────────────────────────────────────────────────────┘

AOD 使用多种传感器来优化显示：

┌──────────────────┬──────────────────────────────────────────────────────────┐
│      传感器      │                       用途                              │
├──────────────────┼──────────────────────────────────────────────────────────┤
│  光线传感器      │  检测环境光，调整 AOD 亮度                              │
│  距离传感器      │  检测口袋模式，关闭 AOD                                 │
│  加速度传感器    │  检测设备静止，进入深度睡眠                             │
│  陀螺仪          │  检测设备运动，唤醒 AOD                                 │
│  拾起传感器      │  检测设备被拾起，退出 AOD                               │
│  双击传感器      │  检测双击屏幕，唤醒设备                                 │
└──────────────────┴──────────────────────────────────────────────────────────┘

传感器监听实现：
```java
// DozeSensors.java
public class DozeSensors {
    
    private SensorManager mSensorManager;
    
    // 注册传感器
    public void registerSensors() {
        // 1. 光线传感器
        Sensor lightSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_LIGHT);
        mSensorManager.registerListener(mLightListener, lightSensor, 
            SensorManager.SENSOR_DELAY_NORMAL);
        
        // 2. 距离传感器
        Sensor proxSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_PROXIMITY);
        mSensorManager.registerListener(mProxListener, proxSensor,
            SensorManager.SENSOR_DELAY_NORMAL);
        
        // 3. 拾起传感器
        Sensor pickupSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_PICK_UP_GESTURE);
        mSensorManager.registerListener(mPickupListener, pickupSensor,
            SensorManager.SENSOR_DELAY_NORMAL);
    }
    
    // 光线传感器监听
    private SensorEventListener mLightListener = new SensorEventListener() {
        @Override
        public void onSensorChanged(SensorEvent event) {
            float lux = event.values[0];
            
            // 根据环境光调整 AOD 亮度
            if (lux < 10) {
                // 暗环境，降低亮度
                mAODController.setBrightness(LOW_BRIGHTNESS);
            } else {
                // 亮环境，提高亮度
                mAODController.setBrightness(NORMAL_BRIGHTNESS);
            }
        }
    };
    
    // 距离传感器监听
    private SensorEventListener mProxListener = new SensorEventListener() {
        @Override
        public void onSensorChanged(SensorEvent event) {
            float distance = event.values[0];
            
            if (distance < 5.0f) {
                // 设备在口袋中，关闭 AOD
                mDozeMachine.transitionTo(State.DOZE_SUSPEND);
            } else {
                // 设备不在口袋中，恢复 AOD
                mDozeMachine.transitionTo(State.DOZE_AOD);
            }
        }
    };
    
    // 拾起传感器监听
    private SensorEventListener mPickupListener = new SensorEventListener() {
        @Override
        public void onSensorChanged(SensorEvent event) {
            // 设备被拾起，退出 AOD
            mDozeMachine.transitionTo(State.EXITED_DOZE);
        }
    };
}
```

### 12.4 AOD 配置和设置

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AOD 配置和设置                                          │
└─────────────────────────────────────────────────────────────────────────────┘

用户可配置的 AOD 选项：

┌──────────────────┬──────────────────────────────────────────────────────────┐
│      设置项      │                       说明                              │
├──────────────────┼──────────────────────────────────────────────────────────┤
│  AOD 开关        │  启用/禁用 AOD 功能                                    │
│  显示内容        │  时钟、通知图标、通知预览                               │
│  时钟样式        │  数字时钟、模拟时钟、无时钟                             │
│  亮度            │  AOD 显示亮度                                          │
│  始终显示        │  充电时始终显示                                        │
│  拾起唤醒        │  拾起设备时唤醒                                        │
│  双击唤醒        │  双击屏幕唤醒                                          │
└──────────────────┴──────────────────────────────────────────────────────────┘

配置实现：
```java
// Settings.Global
AOD_ENABLED = "aod_enabled"              // AOD 开关
AOD_CONTENT = "aod_content"              // 显示内容
AOD_CLOCK_STYLE = "aod_clock_style"      // 时钟样式
AOD_BRIGHTNESS = "aod_brightness"         // 亮度
AOD_ALWAYS_ON = "aod_always_on"           // 始终显示
AOD_PICK_UP_GESTURE = "aod_pick_up"       // 拾起唤醒
AOD_DOUBLE_TAP_GESTURE = "aod_double_tap" // 双击唤醒

// 读取配置
public boolean isAODEnabled() {
    return Settings.Global.getInt(mContext.getContentResolver(), 
        Settings.Global.AOD_ENABLED, 0) == 1;
}

public int getAODContent() {
    return Settings.Global.getInt(mContext.getContentResolver(),
        Settings.Global.AOD_CONTENT, AOD_CONTENT_CLOCK | AOD_CONTENT_NOTIFICATION);
}
```
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

**Q3: AOD 是如何实现低功耗的？**

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

**Q4: 通知渠道 (NotificationChannel) 的作用？**

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

> 本节内容基于 Android 14 源码分析
> 源码路径：frameworks/base/packages/SystemUI/src/com/android/keyguard/

### 13.1 Keyguard 概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Keyguard 锁屏系统概述                                  │
└─────────────────────────────────────────────────────────────────────────────┘

Keyguard 是 Android 系统的锁屏实现，负责：
1. 设备安全保护（防止未授权访问）
2. 安全验证（图案/密码/PIN/生物识别）
3. 锁屏界面显示（时间、通知、快捷设置）
4. 与 SystemUI 的状态同步

┌─────────────────────────────────────────────────────────────────────────────┐
│                       Keyguard 在系统中的位置                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          Framework 层                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KeyguardViewMediator                              │   │
│  │  - 锁屏状态管理                                                      │   │
│  │  - 锁屏显示/隐藏控制                                                 │   │
│  │  - 安全验证调度                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KeyguardUpdateMonitor                             │   │
│  │  - 状态变化监听                                                      │   │
│  │  - 时间/电池/SIM 状态更新                                            │   │
│  │  - 安全状态回调                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SystemUI 层                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    KeyguardService                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                  KeyguardHostView                           │   │   │
│  │  │  ┌─────────────────────────────────────────────────────┐   │   │   │
│  │  │  │              KeyguardSecurityContainer              │   │   │   │
│  │  │  │  ┌─────────────────────────────────────────────┐   │   │   │   │
│  │  │  │  │  PatternKeyguardView   (图案解锁)           │   │   │   │   │
│  │  │  │  │  PasswordKeyguardView   (密码解锁)           │   │   │   │   │
│  │  │  │  │  PINKeyguardView        (PIN 解锁)           │   │   │   │   │
│  │  │  │  │  BiometricKeyguardView  (生物识别)           │   │   │   │   │
│  │  │  │  └─────────────────────────────────────────────┘   │   │   │   │
│  │  │  └─────────────────────────────────────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 13.2 Keyguard 启动流程

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

**文档版本**：v2.0
**更新时间**：2026-03-12
**参考源码**：Android 14 (API 34)