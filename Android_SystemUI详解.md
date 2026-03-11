# Android SystemUI 完全指南

> 作者：OpenClaw | 日期：2026-03-11  
> SystemUI 深度解析 | 启动流程、AOD、通知系统全链路剖析

---

## 目录

1. [SystemUI 概述](#1-systemui-概述)
2. [SystemUI 启动流程](#2-systemui-启动流程)
3. [SystemUI 核心服务](#3-systemui-核心服务)
4. [AOD (Always On Display) 详解](#4-aod-always-on-display-详解)
5. [通知系统完全解析](#5-通知系统完全解析)
6. [RemoteViews 深度解析](#6-remoteviews-深度解析)
7. [通知渲染流程](#7-通知渲染流程)
8. [面试常见问题](#8-面试常见问题)
9. [总结](#9-总结)

---

## 1. SystemUI 概述

### 1.1 什么是 SystemUI

**SystemUI** 是 Android 系统的核心系统应用，负责渲染系统的用户界面元素。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SystemUI 负责的 UI 组件                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              SystemUI                                       │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          状态栏 (StatusBar)                            │  │
│  │  - 通知图标、系统图标（WiFi、信号、电池）                              │  │
│  │  - 下拉展开通知面板                                                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       通知面板 (NotificationShade)                     │  │
│  │  - 通知列表、快捷设置、亮度调节                                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       导航栏 (NavigationBar)                           │  │
│  │  - 返回、Home、最近任务按钮                                            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      锁屏 (Keyguard)                                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                   AOD (Always On Display)                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     最近任务 (Recents)                                 │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 SystemUI 架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SystemUI 架构层次                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          Framework 层                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │WindowManager│  │Notification │  │ Keyguard    │  │ PowerManager│        │
│  │  Service    │  │ManagerService│  │ Manager     │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ System Server 启动 SystemUIService
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SystemUI 进程                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     SystemUIApplication                                │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     SystemUIService                                    │  │
│  │  - 管理所有 SystemUI 服务                                              │  │
│  │  - 按配置启动各个组件                                                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     SystemUI 服务列表                                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ StatusBar   │  │Notification │  │  Keyguard   │  │   AOD       │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SystemUI 启动流程

### 2.1 完整启动流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SystemUI 启动流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  SystemServer                    Zygote                        SystemUI 进程
       │                            │                                │
       │ 1. startOtherServices()    │                                │
       ▼                            │                                │
┌─────────────────┐                 │                                │
│ 启动核心服务    │                 │                                │
│ - AMS/WMS/PMS  │                 │                                │
└────────┬────────┘                 │                                │
         │                          │                                │
         │ 2. startSystemUi()       │                                │
         ▼                          │                                │
┌─────────────────────────────────────────────────────────────────────────────┐
│  ActivityManagerService.startSystemUi()                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Intent intent = new Intent();                                       │   │
│  │  intent.setComponent(new ComponentName("com.android.systemui",      │   │
│  │      "com.android.systemui.SystemUIService"));                      │   │
│  │  context.startServiceAsUser(intent, UserHandle.SYSTEM);             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
         │                          │                                │
         │ 3. 进程不存在，请求 Zygote fork                           │
         │─────────────────────────▶│                                │
         │                          │ 4. Zygote fork 新进程         │
         │                          │───────────────────────────────▶│
         │                          │                                │
         │                          │                     ┌──────────┴──────────┐
         │                          │                     │ ActivityThread.main │
         │                          │                     │ - 创建 Looper       │
         │                          │                     └──────────┬──────────┘
         │                          │                                │
         │                          │                                ▼
         │                          │                     ┌─────────────────────┐
         │                          │                     │ SystemUIApplication │
         │                          │                     │ - onCreate()        │
         │                          │                     └──────────┬──────────┘
         │                          │                                │
         │                          │                                ▼
         │                          │                     ┌─────────────────────┐
         │                          │                     │ SystemUIService     │
         │                          │                     │ - onCreate()        │
         │                          │                     │ - 启动所有服务      │
         │                          │                     └─────────────────────┘
         │◀─────────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SystemUI 启动完成                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 启动流程源码解析

#### 步骤 1: SystemServer 启动 SystemUI

```java
// frameworks/base/services/java/com/android/server/SystemServer.java

private void startOtherServices(@NonNull TimingsTraceAndSlog t) {
    // ... 启动其他核心服务
    
    // 启动 SystemUI
    traceBeginAndSlog("StartSystemUI");
    try {
        startSystemUi(context, windowManagerF);
    } catch (Throwable e) {
        reportWtf("starting System UI", e);
    }
    traceEnd();
}

private static void startSystemUi(Context context, WindowManagerService windowManager) {
    // 1. 创建启动 SystemUIService 的 Intent
    Intent intent = new Intent();
    intent.setComponent(new ComponentName("com.android.systemui",
            "com.android.systemui.SystemUIService"));
    
    // 2. 作为系统用户启动服务 (SYSTEM_UID = 1000)
    context.startServiceAsUser(intent, UserHandle.SYSTEM);
    
    // 3. 通知 WindowManagerService SystemUI 已启动
    windowManager.onSystemUiStarted();
}
```

#### 步骤 2: SystemUIService 启动

```java
// frameworks/base/packages/SystemUI/src/com/android/systemui/SystemUIService.java

public class SystemUIService extends Service {
    
    @Override
    public void onCreate() {
        super.onCreate();
        
        // 1. 获取服务列表配置
        String[] services = getResources().getStringArray(
                R.array.config_systemUIServiceComponents);
        
        // 2. 初始化所有服务
        mServices = new SystemUI[services.length];
        
        for (int i = 0; i < mServices.length; i++) {
            try {
                // 3. 反射创建服务实例
                Class<?> cls = Class.forName(services[i]);
                mServices[i] = (SystemUI) cls.newInstance();
                
                // 4. 调用 start()
                mServices[i].mContext = this;
                mServices[i].start();
                
            } catch (Exception e) {
                Log.w(TAG, "Failed to start service: " + services[i], e);
            }
        }
    }
}
```

#### 步骤 3: 服务配置列表

```xml
<!-- frameworks/base/packages/SystemUI/res/values/config.xml -->

<string-array name="config_systemUIServiceComponents" translatable="false">
    <!-- 核心服务 -->
    <item>com.android.systemui.Dependency</item>
    <item>com.android.systemui.util.NotificationChannels</item>
    
    <!-- 状态栏和通知 -->
    <item>com.android.systemui.statusbar.phone.StatusBar</item>
    <item>com.android.systemui.statusbar.NotificationListener</item>
    
    <!-- 锁屏和 AOD -->
    <item>com.android.systemui.keyguard.KeyguardService</item>
    <item>com.android.systemui.aod.AodService</item>
    
    <!-- 其他 -->
    <item>com.android.systemui.recents.Recents</item>
    <item>com.android.systemui.navigationbar.NavigationBar</item>
    <item>com.android.systemui.volume.VolumeUI</item>
    <item>com.android.systemui.power.PowerUI</item>
</string-array>
```

---

## 3. SystemUI 核心服务

### 3.1 服务启动顺序

```
启动阶段 1: 基础设施
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Dependency                    - 依赖注入容器                            │
│  2. NotificationChannels          - 通知渠道初始化                          │
└─────────────────────────────────────────────────────────────────────────────┘

启动阶段 2: 核心组件
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. StatusBar                     - 状态栏                                  │
│  4. NotificationListener          - 通知监听                                │
│  5. KeyguardViewMediator          - 锁屏协调                                │
└─────────────────────────────────────────────────────────────────────────────┘

启动阶段 3: 功能组件
┌─────────────────────────────────────────────────────────────────────────────┐
│  6. AodService                    - AOD 服务                                │
│  7. VolumeUI                      - 音量界面                                │
│  8. PowerUI                       - 电源管理 UI                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 StatusBar 服务

```java
public class StatusBar extends SystemUI implements 
        CommandQueue.Callbacks,
        NotificationPresenter {
    
    @Override
    public void start() {
        // 1. 创建状态栏窗口
        createAndAddWindows();
        
        // 2. 初始化通知监听
        mNotificationListener.registerAsSystemService();
        
        // 3. 设置系统栏
        updateSystemBars();
    }
    
    private void createAndAddWindows() {
        // 1. 创建 PhoneStatusBarView
        mStatusBarView = (PhoneStatusBarView) LayoutInflater.from(mContext)
                .inflate(R.layout.status_bar, null);
        
        // 2. 添加到 WindowManager
        WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                mStatusBarHeight,
                WindowManager.LayoutParams.TYPE_STATUS_BAR,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT);
        
        mWindowManager.addView(mStatusBarView, lp);
    }
}
```

---

## 4. AOD (Always On Display) 详解

### 4.1 AOD 架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       AOD 架构                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              Framework 层                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │PowerManager │  │DisplayManager│  │ Keyguard    │  │ AlarmManager│        │
│  │  Service    │  │  Service    │  │ Manager     │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SystemUI 层                                    │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         AodController                                  │  │
│  │  - 管理 AOD 显示状态                                                   │  │
│  │  - 监听电源、显示、闹钟事件                                            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          AodService                                    │  │
│  │  - SystemUI 服务入口                                                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        AodNotificationContainer                        │  │
│  │  - 通知图标容器                                                        │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 AOD 启动流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       AOD 启动流程                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  SystemUIService              AodService                 AodController
       │                           │                           │
       │ 1. start()                │                           │
       │                           │                           │
       │ 2. 创建 AodService        │                           │
       │──────────────────────────▶│                           │
       │                           │                           │
       │                           │ 3. start()                │
       │                           │                           │
       │                           │ 4. 初始化 AodController   │
       │                           │──────────────────────────▶│
       │                           │                           │
       │                           │ 5. registerCallbacks()    │
       │                           │◀──────────────────────────│
       │                           │                           │
       │                           │ 6. 监听事件               │
       │                           │ - PowerManager            │
       │                           │ - DisplayManager          │
       │                           │ - KeyguardUpdateMonitor   │
```

### 4.3 AOD 核心源码

```java
public class AodService extends SystemUI {
    
    private AodController mController;
    
    @Override
    public void start() {
        mController = Dependency.get(AodController.class);
        mController.init();
    }
}

public class AodController implements 
        KeyguardUpdateMonitor.Callback,
        DozeHost.Callback {
    
    private boolean mAodShowing;
    private ViewGroup mAodContainer;
    
    public void init() {
        // 创建 AOD 容器
        mAodContainer = (ViewGroup) LayoutInflater.from(mContext)
                .inflate(R.layout.aod_container, null);
        
        // 注册回调
        mKeyguardUpdateMonitor.registerCallback(this);
    }
    
    public void showAod() {
        if (mAodShowing) return;
        mAodShowing = true;
        
        // 添加 AOD 视图
        WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.TYPE_AOD,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT);
        
        mWindowManager.addView(mAodContainer, lp);
        updateNotificationIcons();
    }
    
    public void hideAod() {
        if (!mAodShowing) return;
        mAodShowing = false;
        mWindowManager.removeView(mAodContainer);
    }
    
    @Override
    public void onKeyguardVisibilityChanged(boolean showing) {
        if (showing && !mPowerManager.isInteractive()) {
            showAod();
        } else {
            hideAod();
        }
    }
}
```

### 4.4 AOD 模式切换

```
                    ┌─────────────────┐
                    │   屏幕亮状态    │
                    │   (Interactive) │
                    └────────┬────────┘
                             │
                             │ 电源键按下 / 超时息屏
                             ▼
                    ┌─────────────────┐
                    │   Doze 模式     │
                    │   (低功耗状态)  │
                    └────────┬────────┘
                             │
                             │ Doze 进入完成
                             ▼
                    ┌─────────────────┐
                    │   AOD 模式      │
                    │  (Always On)    │
                    │                 │
                    │  - 显示时间     │
                    │  - 显示通知图标 │
                    │  - 低功耗刷新   │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  用户触摸   │   │  电源键     │   │  新通知     │
    │  WakeUp     │   │  WakeUp     │   │  脉冲显示   │
    └─────────────┘   └─────────────┘   └─────────────┘
```

---

## 5. 通知系统完全解析

### 5.1 通知系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       通知系统完整架构                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            应用层 (App)                                     │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          应用进程                                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                   │  │
│  │  │Notification │  │Notification │  │ RemoteViews │                   │  │
│  │  │ .Builder    │  │  对象       │  │  布局       │                   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                   │  │
│  │                                 │                                     │  │
│  │                                 │ NotificationManager.notify()        │  │
│  └─────────────────────────────────┼─────────────────────────────────────┘  │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     │ Binder IPC
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Framework 层 (System Server)                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                  NotificationManagerService (NMS)                      │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  职责:                                                           │  │  │
│  │  │  - 管理所有通知                                                   │  │  │
│  │  │  - 通知排序和过滤                                                 │  │  │
│  │  │  - 通知渠道管理                                                   │  │  │
│  │  │  - 通知权限检查                                                   │  │  │
│  │  │  - 通知监听者管理                                                 │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Binder IPC (NotificationListener)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SystemUI 层 (SystemUI 进程)                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    NotificationListenerService                         │  │
│  │  - onNotificationPosted()    收到新通知                               │  │
│  │  - onNotificationRemoved()   通知移除                                 │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       NotificationPresenter                            │  │
│  │  - 管理通知 UI 呈现                                                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       NotificationContentView                          │  │
│  │  - 通知内容视图                                                        │  │
│  │  - RemoteViews 渲染                                                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 通知发布流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       通知发布完整流程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

应用进程                          NMS (System Server)              SystemUI 进程
    │                                    │                               │
    │ 1. 创建 Notification              │                               │
    │ ┌─────────────────────────────┐   │                               │
    │ │ Notification noti = new    │   │                               │
    │ │   Notification.Builder()   │   │                               │
    │ │   .setSmallIcon(...)       │   │                               │
    │ │   .setContentTitle(...)    │   │                               │
    │ │   .setContentText(...)     │   │                               │
    │ │   .build();                │   │                               │
    │ └─────────────────────────────┘   │                               │
    │                                    │                               │
    │ 2. notify()                        │                               │
    │ ┌─────────────────────────────┐   │                               │
    │ │ NotificationManager        │   │                               │
    │ │   .notify(id, notification)│   │                               │
    │ └──────────────┬──────────────┘   │                               │
    │                │                  │                               │
    │                │ 3. Binder IPC    │                               │
    │                │ ────────────────▶│                               │
    │                │                  │                               │
    │                │                  ▼                               │
    │                │      ┌───────────────────────────────────────┐   │
    │                │      │ NMS.enqueueNotification()             │   │
    │                │      │                                       │   │
    │                │      │ 4. 权限检查                           │   │
    │                │      │ 5. 创建 NotificationRecord            │   │
    │                │      │ 6. 通知排序                           │   │
    │                │      │ 7. 保存到通知列表                     │   │
    │                │      └───────────────┬───────────────────────┘   │
    │                │                      │                           │
    │                │                      │ 8. 通知监听者            │
    │                │                      │ ─────────────────────────▶│
    │                │                      │                           │
    │                │                      │               ┌───────────┴───────────┐
    │                │                      │               │ NotificationListener  │
    │                │                      │               │                       │
    │                │                      │               │ onNotificationPosted()│
    │                │                      │               │ - 更新 UI             │
    │                │                      │               └───────────┬───────────┘
    │                │                      │                           │
    │                │                      │                           ▼
    │                │                      │               ┌───────────────────────┐
    │                │                      │               │ StatusBar             │
    │                │                      │               │ - 更新状态栏图标      │
    │                │                      │               │ - 显示 HeadsUp       │
    │                │                      │               │ - 更新通知面板        │
    │                │                      │               └───────────────────────┘
    │◀───────────────┼──────────────────────┼───────────────────────────┘
    │                │                      │
    ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        通知显示完成                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 NotificationManagerService (NMS)

```java
/**
 * NotificationManagerService - 通知管理服务
 * 
 * 位置: frameworks/base/services/core/java/com/android/server/notification/
 */
public class NotificationManagerService extends SystemService {
    
    // 通知列表
    private final ArrayMap<String, NotificationRecord> mNotifications = new ArrayMap<>();
    
    // 通知监听者列表
    private final ArrayList<NotificationListenerInfo> mListenerList = new ArrayList<>();
    
    @Override
    public void onStart() {
        // 发布服务
        publishBinderService(Context.NOTIFICATION_SERVICE, mService);
    }
    
    /**
     * 入队通知
     */
    void enqueueNotification(String pkg, String opPkg, int callingUid, 
            int callingPid, String tag, int id, Notification notification, 
            int[] idOut, int userId) {
        
        // 1. 权限检查
        checkCallerIsSystemOrSameApp(pkg);
        
        // 2. 创建 NotificationRecord
        NotificationRecord r = new NotificationRecord(mContext, 
                new StatusBarNotification(pkg, opPkg, id, tag, callingUid, 
                        callingPid, notification, UserHandle.getUserId(callingUid), 
                        null, System.currentTimeMillis()));
        
        // 3. 通知排序
        mRankingHelper.extractSignal(r);
        mRankingHelper.sort(mNotificationList);
        
        // 4. 保存通知
        mNotifications.put(r.getKey(), r);
        
        // 5. 通知监听者
        notifyPosted(r);
    }
    
    /**
     * 通知所有监听者
     */
    private void notifyPosted(NotificationRecord r) {
        for (NotificationListenerInfo listener : mListenerList) {
            listener.onNotificationPosted(r.getSbn(), r.getRanking());
        }
    }
}
```

### 5.4 NotificationListener (SystemUI)

```java
/**
 * NotificationListener - SystemUI 通知监听实现
 */
public class NotificationListener extends NotificationListenerService {
    
    private StatusBar mStatusBar;
    
    @Override
    public void onListenerConnected() {
        // 连接到 NMS
        // 可以获取所有活跃通知
        StatusBarNotification[] active = getActiveNotifications();
        mStatusBar.updateNotificationList(active);
    }
    
    @Override
    public void onNotificationPosted(StatusBarNotification sbn, 
            RankingMap rankingMap) {
        // 收到新通知
        mStatusBar.addNotification(sbn, rankingMap);
    }
    
    @Override
    public void onNotificationRemoved(StatusBarNotification sbn, 
            RankingMap rankingMap, int reason) {
        // 通知移除
        // reason: REASON_CLICK, REASON_CANCEL, REASON_TIMEOUT 等
        mStatusBar.removeNotification(sbn.getKey(), reason);
    }
}
```

---

## 6. RemoteViews 深度解析

### 6.1 RemoteViews 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RemoteViews 概述                                     │
└─────────────────────────────────────────────────────────────────────────────┘

RemoteViews 是一种跨进程 View 的描述方式：
- 应用进程创建 RemoteViews（描述布局）
- SystemUI 进程根据 RemoteViews 创建真正的 View

┌─────────────────────────────────────────────────────────────────────────────┐
│                          RemoteViews 工作原理                              │
└─────────────────────────────────────────────────────────────────────────────┘

应用进程                                      SystemUI 进程
    │                                              │
    │ 1. 创建 RemoteViews                         │
    │ ┌──────────────────────────────────────┐   │
    │ │ RemoteViews views = new RemoteViews( │   │
    │ │   "com.example.app",                 │   │
    │ │   R.layout.notification_layout       │   │
    │ │ );                                   │   │
    │ │                                      │   │
    │ │ // 设置内容                          │   │
    │ │ views.setTextViewText(R.id.title,    │   │
    │ │     "通知标题");                      │   │
    │ │ views.setImageViewResource(          │   │
    │ │   R.id.icon, R.drawable.icon);       │   │
    │ └──────────────────────────────────────┘   │
    │                                              │
    │ 2. 序列化为 Parcel                          │
    │ ┌──────────────────────────────────────┐   │
    │ │ RemoteViews 内部维护一个 Action 列表 │   │
    │ │ - SetTextViewTextAction              │   │
    │ │ - SetImageViewResourceAction         │   │
    │ │ - SetOnClickPendingIntentAction      │   │
    │ │                                      │   │
    │ │ writeToParcel() -> Parcel            │   │
    │ └──────────────────────────────────────┘   │
    │                                              │
    │ 3. 通过 Binder 传递                         │
    │ ─────────────────────────────────────────▶  │
    │                                              │
    │                                     ┌───────┴───────┐
    │                                     │ 4. 反序列化   │
    │                                     │               │
    │                                     │ RemoteViews   │
    │                                     │ .apply()      │
    │                                     └───────┬───────┘
    │                                             │
    │                                     ┌───────┴───────┐
    │                                     │ 5. 创建 View  │
    │                                     │               │
    │                                     │ - inflate布局 │
    │                                     │ - 执行Action  │
    │                                     │ - 返回View    │
    │                                     └───────────────┘
```

### 6.2 RemoteViews 源码分析

```java
/**
 * RemoteViews 类结构
 */
public class RemoteViews implements Parcelable, Filter {
    
    // 布局资源 ID
    private final int mLayoutId;
    
    // 应用包名
    private final String mPackage;
    
    // Action 列表
    private ArrayList<Action> mActions;
    
    /**
     * 构造函数
     */
    public RemoteViews(String packageName, int layoutId) {
        mPackage = packageName;
        mLayoutId = layoutId;
        mActions = new ArrayList<>();
    }
    
    /**
     * 设置 TextView 文本
     */
    public void setTextViewText(int viewId, CharSequence text) {
        // 添加一个 Action
        addAction(new SetTextViewTextAction(viewId, text));
    }
    
    /**
     * 设置 ImageView 资源
     */
    public void setImageViewResource(int viewId, int srcId) {
        addAction(new SetImageViewResourceAction(viewId, srcId));
    }
    
    /**
     * 设置点击事件
     */
    public void setOnClickPendingIntent(int viewId, PendingIntent pendingIntent) {
        addAction(new SetOnClickPendingIntentAction(viewId, pendingIntent));
    }
    
    /**
     * 应用 RemoteViews 到 ViewGroup
     */
    public View apply(Context context, ViewGroup parent) {
        // 1. Inflate 布局
        View result = inflateView(context, parent);
        
        // 2. 执行所有 Action
        performApply(result, parent);
        
        return result;
    }
    
    private void performApply(View v, ViewGroup parent) {
        if (mActions != null) {
            for (Action a : mActions) {
                a.apply(v, parent);
            }
        }
    }
    
    /**
     * Action 基类
     */
    private abstract static class Action implements Parcelable {
        abstract void apply(View root, ViewGroup rootParent);
    }
    
    /**
     * SetTextViewTextAction
     */
    private class SetTextViewTextAction extends Action {
        int viewId;
        CharSequence text;
        
        @Override
        void apply(View root, ViewGroup rootParent) {
            TextView tv = root.findViewById(viewId);
            if (tv != null) {
                tv.setText(text);
            }
        }
    }
}
```

### 6.3 RemoteViews 在通知中的应用

```java
/**
 * 通知中的 RemoteViews
 */
public class NotificationBuilder {
    
    /**
     * 设置自定义内容布局
     */
    public Builder setContent(RemoteViews views) {
        mContent = views;
        return this;
    }
    
    /**
     * 设置展开后的布局（大视图）
     */
    public Builder setBigContentView(RemoteViews views) {
        mBigContentView = views;
        return this;
    }
}
```

---

## 7. 通知渲染流程

### 7.1 通知渲染完整流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       通知渲染完整流程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  NMS                      NotificationListener           NotificationEntry
    │                              │                              │
    │ 1. onNotificationPosted()    │                              │
    │─────────────────────────────▶│                              │
    │                              │                              │
    │                              │ 2. addNotification()         │
    │                              │─────────────────────────────▶│
    │                              │                              │
    │                              │                              ▼
    │                              │                    ┌─────────────────────┐
    │                              │                    │ 创建 Entry          │
    │                              │                    │ - StatusBarNotif    │
    │                              │                    │ - ExpandableNotif   │
    │                              │                    └──────────┬──────────┘
    │                              │                               │
    │                              │                               ▼
    │                              │                    ┌─────────────────────┐
    │                              │                    │ inflate Views       │
    │                              │                    │ - content views     │
    │                              │                    │ - heads up views    │
    │                              │                    │ - public views      │
    │                              │                    └──────────┬──────────┘
    │                              │                               │
    │                              │                               ▼
    │                              │                    ┌─────────────────────┐
    │                              │                    │ RemoteViews.apply() │
    │                              │                    │ - 创建实际View      │
    │                              │                    │ - 执行所有Action    │
    │                              │                    └──────────┬──────────┘
    │                              │                               │
    │                              │                               ▼
    │                              │                    ┌─────────────────────┐
    │                              │                    │ 绑定到列表          │
    │                              │                    │ - 添加到RecyclerView│
    │                              │                    │ - 触发动画          │
    │                              │                    └─────────────────────┘
```

### 7.2 NotificationContentView

```java
/**
 * NotificationContentView - 通知内容视图容器
 */
public class NotificationContentView extends FrameLayout {
    
    // 远程视图包装器
    private RemoteViews mRemoteViews;
    
    // 实际渲染的 View
    private View mContent;
    
    /**
     * 设置 RemoteViews 并渲染
     */
    public void setRemoteViews(RemoteViews remoteViews) {
        if (mRemoteViews == remoteViews) {
            return;
        }
        
        mRemoteViews = remoteViews;
        
        // 1. 移除旧视图
        removeAllViews();
        
        // 2. 应用 RemoteViews
        mContent = remoteViews.apply(mContext, this);
        
        // 3. 添加新视图
        addView(mContent);
    }
}
```

### 7.3 通知模板

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       通知模板类型                                          │
└─────────────────────────────────────────────────────────────────────────────┘

1. 基础模板 (Basic)
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌────────┐                                                                 │
│  │ 小图标 │  标题                                           时间           │
│  │        │  内容文本                                                      │
│  └────────┘                                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

2. 大文本模板 (BigTextStyle)
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌────────┐                                                                 │
│  │ 小图标 │  标题                                           时间           │
│  │        │  内容摘要...                                                   │
│  └────────┘                                                                 │
│  ────────────────────────────────────────────────────────────────────────  │
│  展开后显示完整的大段文本内容...                                              │
│  可以显示多行文本，支持滚动                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

3. 大图片模板 (BigPictureStyle)
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌────────┐                                                                 │
│  │ 小图标 │  标题                                           时间           │
│  │        │  内容摘要                                                      │
│  └────────┘                                                                 │
│  ────────────────────────────────────────────────────────────────────────  │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                       │ │
│  │                        大图片显示                                     │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

4. 收件箱模板 (InboxStyle)
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌────────┐                                                                 │
│  │ 小图标 │  标题                                           时间           │
│  │        │  内容摘要                                                      │
│  └────────┘                                                                 │
│  ────────────────────────────────────────────────────────────────────────  │
│  ● 消息行 1                                                                 │
│  ● 消息行 2                                                                 │
│  ● 消息行 3                                                                 │
│  +2 more                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

5. 消息模板 (MessagingStyle)
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌────────┐                                                                 │
│  │ 小图标 │  对话标题                                      时间           │
│  │        │                                                                │
│  └────────┘                                                                 │
│  ────────────────────────────────────────────────────────────────────────  │
│  用户A: 消息内容 1                                    10:30                 │
│  用户B: 消息内容 2                                    10:31                 │
│  用户A: 消息内容 3                                    10:32                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.4 通知模板使用示例

```java
/**
 * 通知模板使用示例
 */

// 1. 基础通知
Notification notification = new Notification.Builder(context, CHANNEL_ID)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("标题")
    .setContentText("内容")
    .build();

// 2. BigTextStyle 大文本
Notification notification = new Notification.Builder(context, CHANNEL_ID)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("标题")
    .setContentText("摘要")
    .setStyle(new Notification.BigTextStyle()
        .bigText("这是一段很长的文本内容，可以在展开后完整显示..."))
    .build();

// 3. BigPictureStyle 大图片
Notification notification = new Notification.Builder(context, CHANNEL_ID)
    .setSmallIcon(R.drawable.icon)
    .setContentTitle("图片通知")
    .setStyle(new Notification.BigPictureStyle()
        .bigPicture(bitmap)
        .bigLargeIcon(null))
    .build();

// 4. MessagingStyle 消息
Notification notification = new Notification.Builder(context, CHANNEL_ID)
    .setSmallIcon(R.drawable.icon)
    .setStyle(new Notification.MessagingStyle("Me")
        .addMessage("Hello", System.currentTimeMillis(), "UserA")
        .addMessage("Hi there!", System.currentTimeMillis(), "UserB"))
    .build();

// 5. 自定义布局
RemoteViews customView = new RemoteViews(pkg, R.layout.custom_notification);
customView.setTextViewText(R.id.title, "自定义标题");

Notification notification = new Notification.Builder(context, CHANNEL_ID)
    .setSmallIcon(R.drawable.icon)
    .setCustomContentView(customView)
    .build();
```

---

## 8. 面试常见问题

### 8.1 SystemUI 基础

**Q1: SystemUI 是什么？它的作用是什么？**

**A:**

SystemUI 是 Android 系统的核心系统应用，负责渲染系统的用户界面元素，包括：
- 状态栏（StatusBar）
- 导航栏（NavigationBar）
- 通知面板（NotificationShade）
- 锁屏（Keyguard）
- AOD（Always On Display）
- 最近任务（Recents）

它作为一个独立进程运行，由 SystemServer 在系统启动时启动。

**Q2: SystemUI 的启动流程是什么？**

**A:**

```
1. SystemServer.startOtherServices()
      ↓
2. AMS.startSystemUi() 
   - 发送 Intent 启动 SystemUIService
      ↓
3. Zygote fork SystemUI 进程
      ↓
4. SystemUIApplication.onCreate()
      ↓
5. SystemUIService.onCreate()
   - 读取服务配置列表
   - 反射创建所有服务
   - 调用每个服务的 start()
      ↓
6. 各服务启动完成
   - StatusBar
   - NotificationListener
   - Keyguard
   - AOD
```

### 8.2 AOD 相关

**Q3: AOD 是什么？它是如何工作的？**

**A:**

AOD (Always On Display) 是息屏显示功能，在屏幕关闭时显示时间和通知图标。

工作原理：
1. **Doze 模式**：屏幕灭后进入低功耗状态
2. **AOD 显示**：在 Doze 模式下，使用低功耗显示
3. **通知更新**：收到通知时更新显示内容
4. **交互响应**：检测触摸/抬起唤醒屏幕

核心组件：
- AodService：SystemUI 服务入口
- AodController：控制 AOD 显示/隐藏
- AodAmbientDisplay：Doze 模式管理

### 8.3 通知系统

**Q4: 通知从发布到显示的完整流程？**

**A:**

```
应用进程:
1. 创建 Notification 对象
2. 调用 NotificationManager.notify()
      ↓ Binder IPC
NMS (System Server):
3. 权限检查
4. 创建 NotificationRecord
5. 通知排序
6. 保存到通知列表
7. 通知所有 NotificationListener
      ↓ Binder IPC
SystemUI 进程:
8. NotificationListener.onNotificationPosted()
9. 创建 NotificationEntry
10. Inflate 通知视图
11. RemoteViews.apply() 渲染布局
12. 添加到通知面板显示
```

**Q5: RemoteViews 是什么？为什么通知要用 RemoteViews？**

**A:**

RemoteViews 是一种跨进程 View 的描述方式。

**为什么需要 RemoteViews：**
1. 通知运行在 SystemUI 进程，不在应用进程
2. 应用无法直接操作系统 UI 的 View
3. RemoteViews 提供了安全的跨进程 View 更新机制

**工作原理：**
1. 应用进程：创建 RemoteViews，设置属性（作为 Action 保存）
2. 传递：通过 Binder 将 RemoteViews 传到 SystemUI
3. SystemUI：调用 apply() 创建真正的 View 并执行所有 Action

**限制：**
- 只支持有限的 View 类型（FrameLayout、LinearLayout、RelativeLayout、TextView、ImageView、Button 等）
- 只支持有限的操作（setText、setImageResource、setOnClickPendingIntent 等）

### 8.4 深度问题

**Q6: NMS (NotificationManagerService) 的核心职责是什么？**

**A:**

1. **通知管理**
   - 存储所有活跃通知
   - 处理通知的添加、更新、删除

2. **权限检查**
   - 检查应用是否有通知权限
   - 验证通知渠道是否有效

3. **通知排序**
   - 按优先级排序
   - 应用 Ranking 配置

4. **通知渠道管理**
   - 管理通知渠道（Channel）
   - 控制渠道重要性级别

5. **监听者管理**
   - 管理 NotificationListenerService
   - 分发通知事件

**Q7: 通知如何实现跨进程通信？**

**A:**

通知系统涉及多个进程的协作：

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   App 进程   │         │System Server│         │ SystemUI    │
│             │         │    (NMS)    │         │   进程      │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │ NotificationManager   │                       │
       │    .notify()          │                       │
       │ ────────────────────▶ │                       │
       │     (Binder IPC)      │                       │
       │                       │                       │
       │                       │ NotificationListener  │
       │                       │    callback           │
       │                       │ ────────────────────▶ │
       │                       │     (Binder IPC)      │
       │                       │                       │
       │                       │                       │
       │◀───────────────────── │◀───────────────────── │
       │     (RemoteViews      │     (状态同步)        │
       │      序列化传输)       │                       │
```

**跨进程机制：**
1. **Binder IPC**：NotificationManager 和 NMS 通信
2. **NotificationListener**：NMS 和 SystemUI 通信
3. **RemoteViews**：View 的跨进程描述，通过 Parcel 序列化

**Q8: 通知的渲染过程是怎样的？**

**A:**

```
1. RemoteViews 接收
   - SystemUI 收到 StatusBarNotification
   - 提取 Notification.contentView

2. RemoteViews 解析
   - 解析布局资源 ID
   - 解析 Action 列表

3. View 创建
   - 使用应用资源的 Context
   - Inflate 布局 XML

4. Action 执行
   - 遍历所有 Action
   - 调用 apply() 执行具体操作
   - 例如：setTextViewText() -> TextView.setText()

5. View 绑定
   - 将创建的 View 添加到通知容器
   - 绑定点击事件（PendingIntent）

6. 显示动画
   - 添加到 RecyclerView
   - 触发入场动画
```

---

## 9. 总结

### SystemUI 核心要点

1. **SystemUI 是什么**：Android 系统的核心 UI 应用，负责状态栏、通知、锁屏、AOD 等

2. **启动流程**：SystemServer → AMS → Zygote fork → SystemUIService → 启动所有服务

3. **AOD 机制**：
   - 基于 Doze 模式的低功耗显示
   - AodController 控制显示/隐藏
   - 监听电源、通知、闹钟事件

4. **通知系统**：
   - NMS 管理通知
   - NotificationListener 监听通知
   - RemoteViews 跨进程渲染

5. **RemoteViews**：
   - View 的跨进程描述
   - 通过 Action 列表记录操作
   - 在目标进程 apply() 创建真正的 View

### 架构图总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SystemUI 完整架构                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          System Server                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    AMS      │  │    WMS      │  │    NMS      │  │    PMS      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
         │                  │                  │                  │
         └──────────────────┴──────────────────┴──────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SystemUI 进程                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     SystemUIService                                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │  StatusBar  │  │Notification │  │  Keyguard   │  │    AOD      │  │  │
│  │  │             │  │  Listener   │  │             │  │  Service    │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │                                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ Notification│  │  RemoteViews│  │  Recents    │  │ NavigationBar│ │  │
│  │  │  Entry      │  │   渲染      │  │             │  │             │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**文档版本**：v1.0  
**更新时间**：2026-03-11  
**适用版本**：Android 10+ (API 29+)
