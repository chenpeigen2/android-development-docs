# Android SystemUI 完全指南

> 作者：OpenClaw | 日期：2026-03-11  
> SystemUI 核心机制 | AOD 与通知系统深度解析

---

## 目录

1. [SystemUI 概述](#1-systemui-概述)
2. [SystemUI 启动流程](#2-systemui-启动流程)
3. [AOD (Always On Display) 详解](#3-aod-always-on-display-详解)
4. [通知系统详解](#4-通知系统详解)
5. [NotificationManagerService 深入分析](#5-notificationmanagerservice-深入分析)
6. [RemoteViews 深度解析](#6-remoteviews-深度解析)
7. [SystemUI 与 Framework 协作机制](#7-systemui-与-framework-协作机制)
8. [通知渲染流程](#8-通知渲染流程)
9. [通知模板系统](#9-通知模板系统)
10. [面试常见问题](#10-面试常见问题)

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

## 8. 通知模板

### 8.1 模板类型

```
┌──────────────────┬──────────────────────────────────────────────────────────┐
│      模板        │                       说明                              │
├──────────────────┼──────────────────────────────────────────────────────────┤
│  BigTextStyle    │  长文本通知，展开显示完整内容                            │
│  BigPictureStyle │  大图片通知，展开显示大图                                │
│  InboxStyle      │  收件箱通知，显示多行消息列表                            │
│  MessagingStyle  │  消息通知，显示对话内容                                  │
│  MediaStyle      │  媒体通知，显示播放控制                                  │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

---

## 10. 面试常见问题

**Q1: SystemUI 是什么？包含哪些组件？**

A: SystemUI 是 Android 系统的核心 UI 组件：
- StatusBar（状态栏）
- NavigationBar（导航栏）
- NotificationPanel（通知面板）
- Keyguard（锁屏）
- AOD（息屏显示）

**Q2: AOD 是如何实现的？**

A: 
1. 硬件：AMOLED 屏幕可单独点亮像素
2. 软件：DozeMachine 状态机控制
3. 状态流转：DOZE_INIT → DOZE_AOD → DOZE_REST → EXITED_DOZE

**Q3: RemoteViews 的原理？**

A: 
1. 跨进程视图机制
2. 序列化视图操作为 Action 列表
3. 在 SystemUI 进程反序列化并应用
4. 只支持有限的 View 类型

---

## 总结

### SystemUI 核心要点

1. **SystemUI**：系统级 UI（状态栏、导航栏、通知、锁屏）
2. **AOD**：DozeMachine 状态机 + 低功耗显示
3. **通知系统**：NMS + RemoteViews + SystemUI 协作
4. **RemoteViews**：跨进程视图，序列化操作

---

**文档版本**：v1.0  
**更新时间**：2026-03-11  
**参考源码**：Android 14 (API 34)