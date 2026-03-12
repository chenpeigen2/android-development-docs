# Android 系统启动流程深度解析

> 作者：OpenClaw | 日期：2026-03-12  
> 基于源码：Android 16 (API 36) AOSP

## 目录

1. [概述](#1-概述)
2. [Init 进程启动](#2-init-进程启动)
3. [Zygote 进程 fork 机制](#3-zygote-进程-fork-机制)
4. [SystemServer 启动流程](#4-systemserver-启动流程)
5. [系统服务启动顺序](#5-系统服务启动顺序)
6. [BootComplete 广播](#6-bootcomplete-广播)
7. [源码路径](#7-源码路径)
8. [面试常见问题](#8-面试常见问题)

---

## 1. 概述

Android 系统启动是一个复杂的过程，从按下电源键到桌面完全显示，涉及多个阶段和组件。

### 1.1 启动流程总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Android 系统启动流程                                  │
└─────────────────────────────────────────────────────────────────────────────┘

按下电源键
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Boot ROM                                                               │
│     • 执行固化在 ROM 中的启动代码                                           │
│     • 加载 Bootloader 到 RAM                                               │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Bootloader                                                             │
│     • 初始化硬件                                                            │
│     • 加载 Linux 内核                                                       │
│     • 传递启动参数                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Linux Kernel                                                           │
│     • 初始化内核                                                            │
│     • 挂载根文件系统                                                        │
│     • 启动 init 进程 (PID=1)                                                │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Init 进程                                                              │
│     • 解析 init.rc                                                         │
│     • 启动关键服务 (ueventd, healthd)                                       │
│     • 启动 Zygote 进程                                                      │
│     • 启动 ServiceManager                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. Zygote 进程                                                            │
│     • 创建 Dalvik/ART 虚拟机                                                │
│     • 预加载类和资源                                                        │
│     • 启动 SystemServer                                                     │
│     • 进入 Socket 监听                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6. SystemServer                                                           │
│     • 启动系统服务 (AMS, WMS, PMS 等)                                       │
│     • 进入 Binder 线程池                                                    │
│     • 发送 BOOT_COMPLETED 广播                                              │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. Launcher (桌面)                                                        │
│     • 显示应用图标                                                          │
│     • 系统启动完成                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 启动时间分布

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        启动时间分布 (典型值)                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬────────────────────────────────────────┐
│  阶段        │  时间 (ms)   │              说明                      │
├──────────────┼──────────────┼────────────────────────────────────────┤
│  Boot ROM    │  100-500     │  固化代码执行                          │
│  Bootloader  │  1000-3000   │  硬件初始化                            │
│  Kernel      │  1000-2000   │  内核初始化                            │
│  Init        │  500-1000    │  进程启动                              │
│  Zygote      │  2000-5000   │  预加载类和资源                        │
│  SystemServer│  3000-8000   │  系统服务启动                          │
│  Launcher    │  500-1500    │  桌面显示                              │
├──────────────┼──────────────┼────────────────────────────────────────┤
│  总计        │  8-20 秒     │  完整启动时间                          │
└──────────────┴──────────────┴────────────────────────────────────────┘

优化后启动时间 (高端设备)：
• 冷启动: 8-12 秒
• 热启动: 2-4 秒
```

---

## 2. Init 进程启动

### 2.1 Init 进程职责

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Init 进程职责                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Init 进程 (PID=1):
1. 解析 init.rc 配置文件
2. 启动关键守护进程
3. 挂载文件系统
4. 设置系统属性
5. 启动 Zygote 和 ServiceManager
6. 监听子进程退出并重启

关键服务：
• ueventd: 设备事件管理
• healthd: 电池监控
• servicemanager: Binder 服务管理
• surfaceflinger: 图形合成
• zygote: 应用进程孵化器
```

### 2.2 init.rc 配置

```
# init.rc 示例
# 位置：system/core/rootdir/init.rc

# 导入其他配置
import /system/etc/init/hw/init.${ro.hardware}.rc
import /system/etc/init/*.rc
import /vendor/etc/init/*.rc

# 早期初始化
on early-init
    # 设置 SELinux
    start ueventd
    exec -- /system/bin/selinux_setup

# 初始化
on init
    # 挂载文件系统
    mount_all /vendor/etc/fstab.${ro.hardware}
    
    # 设置系统属性
    setprop ro.build.fingerprint ${ro.system.build.fingerprint}

# 后期初始化
on late-init
    # 启动服务
    trigger early-fs
    trigger fs
    trigger post-fs
    trigger late-fs
    trigger post-fs-data
    trigger zygote-start
    trigger early-boot
    trigger boot

# 启动 Zygote
on zygote-start
    start servicemanager
    start surfaceflinger
    start zygote

# 服务定义
service servicemanager /system/bin/servicemanager
    class core
    user system
    group system
    critical
    onrestart restart zygote

service surfaceflinger /system/bin/surfaceflinger
    class core
    user system
    group graphics drmrpc
    onrestart restart zygote

service zygote /system/bin/app_process64 -Xzygote /system/bin --zygote --start-system-server
    class main
    socket zygote stream 660 root system
    onrestart write /sys/android_power/request_state wake
    onrestart write /sys/power/state on
    onrestart restart media
    onrestart restart netd
```

### 2.3 Init 源码

```cpp
/**
 * Init 主函数
 * 位置：system/core/init/init.cpp
 */
int main(int argc, char** argv) {
    // 1. 创建设备节点
    if (is_first_stage) {
        mount("tmpfs", "/dev", "tmpfs", MS_NOSUID, "mode=0755");
        mkdir("/dev/pts", 0755);
        mkdir("/dev/socket", 0755);
    }
    
    // 2. 初始化属性系统
    property_init();
    
    // 3. 解析 init.rc
    Parser parser;
    parser.ParseConfig("/system/etc/init/hw/init.rc");
    
    // 4. 启动早期服务
    ActionManager::GetInstance()->ExecuteAction("early-init");
    
    // 5. 启动 ueventd
    ueventd_init();
    
    // 6. 进入主循环
    while (true) {
        // 等待事件
        epoll_wait(epoll_fd, events, MAX_EVENTS, -1);
        
        // 处理事件
        for (auto& event : events) {
            if (event.data.fd == signal_fd) {
                // 处理子进程退出
                handle_signal();
            } else if (event.data.fd == property_fd) {
                // 处理属性变化
                handle_property();
            }
        }
        
        // 执行 Action
        ActionManager::GetInstance()->ExecuteAction("");
        
        // 重启崩溃的服务
        restart_processes();
    }
    
    return 0;
}
```

---

## 3. Zygote 进程 fork 机制

### 3.1 Zygote 职责

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Zygote 职责                                          │
└─────────────────────────────────────────────────────────────────────────────┘

Zygote (受精卵):
1. 创建 ART/Dalvik 虚拟机
2. 预加载类和资源
3. 启动 SystemServer
4. 监听 Socket，响应 fork 请求
5. 为新应用提供进程模板

优势：
• 预加载共享资源，减少启动时间
• Copy-on-Write 机制，节省内存
• 统一的进程模板
```

### 3.2 Zygote 启动流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Zygote 启动流程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

app_process (app_main.cpp)
    │
    ▼
AndroidRuntime.start()
    │
    ├─► 启动虚拟机
    │   └─► JNI_CreateJavaVM()
    │
    ├─► 注册 JNI 方法
    │   └─► register_jni_procs()
    │
    ├─► 调用 ZygoteInit.main()
    │   │
    │   ├─► 预加载
    │   │   ├─► preloadClasses()
    │   │   ├─► preloadResources()
    │   │   ├─► preloadSharedLibraries()
    │   │   └─► preloadDexCaches()
    │   │
    │   ├─► 启动 SystemServer
    │   │   └─► forkSystemServer()
    │   │
    │   └─► 进入监听循环
    │       └─► runSelectLoop()
    │
    └─► 等待请求
```

### 3.3 ZygoteInit 源码

```java
/**
 * ZygoteInit - Zygote 主类
 * 位置：frameworks/base/core/java/com/android/internal/os/ZygoteInit.java
 */
class ZygoteInit {
    
    public static void main(String argv[]) {
        // 1. 创建 Zygote Server Socket
        ZygoteServer zygoteServer = new ZygoteServer();
        
        // 2. 预加载
        preload(bootTimingsTraceLog);
        
        // 3. 启动 SystemServer
        if (startSystemServer) {
            Runnable r = forkSystemServer(abiList, socketName, zygoteServer);
            if (r != null) {
                r.run();
                return;
            }
        }
        
        // 4. 进入监听循环
        Log.i(TAG, "Accepting command socket connections");
        caller = zygoteServer.runSelectLoop(abiList);
        
        if (caller != null) {
            caller.run();
        }
    }
    
    static void preload(TimingsTraceLog bootTimingsTraceLog) {
        // 预加载类
        preloadClasses();
        
        // 预加载资源
        preloadResources();
        
        // 预加载共享库
        preloadSharedLibraries();
        
        // 预加载 DEX 缓存
        preloadDexCaches();
        
        // 预加载 WebView
        WebViewFactory.prepareWebViewInZygote();
    }
    
    /**
     * 预加载类
     */
    private static void preloadClasses() {
        // 读取预加载列表
        InputStream is = ClassLoader.getSystemClassLoader()
                .getResourceAsStream("preloaded-classes");
        
        BufferedReader br = new BufferedReader(new InputStreamReader(is));
        
        String line;
        while ((line = br.readLine()) != null) {
            // 跳过注释和空行
            if (line.startsWith("#") || line.isEmpty()) {
                continue;
            }
            
            // 加载类
            Class.forName(line);
        }
    }
}
```

### 3.4 Zygote Fork 流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Zygote Fork 流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

AMS 请求 fork
    │
    ▼
ZygoteProcess.start()
    │
    ├─► 连接 Zygote Socket
    │
    ├─► 发送 fork 请求
    │   └─► writeArgument()
    │
    └─► Zygote 处理请求
        │
        ▼
ZygoteServer.runSelectLoop()
    │
    ├─► 接收请求
    │   └─► ZygoteConnection.processCommand()
    │
    ├─► 解析参数
    │
    ├─► fork 进程
    │   └─► Zygote.forkAndSpecialize()
    │       └─► nativeForkAndSpecialize()
    │           └─► fork()
    │
    ├─► 子进程处理
    │   └─► handleChildProc()
    │       ├─► 设置进程名
    │       ├─► 关闭 Zygote Socket
    │       └─► 调用 ActivityThread.main()
    │
    └─► 父进程处理
        └─► 返回子进程 PID
```

---

## 4. SystemServer 启动流程

### 4.1 SystemServer 职责

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SystemServer 职责                                    │
└─────────────────────────────────────────────────────────────────────────────┘

SystemServer:
1. 启动所有系统服务
2. 提供 Binder IPC 支持
3. 管理系统生命周期
4. 协调各服务交互

主要服务：
• ActivityManagerService (AMS)
• WindowManagerService (WMS)
• PackageManagerService (PMS)
• PowerManagerService (PMS)
• DisplayManagerService (DMS)
• InputManagerService (IMS)
• 等等...
```

### 4.2 SystemServer 启动流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SystemServer 启动流程                                │
└─────────────────────────────────────────────────────────────────────────────┘

ZygoteInit.forkSystemServer()
    │
    ▼
Zygote.forkSystemServer()
    │
    ├─► fork() 创建新进程
    │
    └─► 子进程
        │
        ▼
com.android.server.SystemServer.main()
    │
    ├─► 创建 SystemServer 实例
    │
    ├─► 初始化 Native 服务
    │   └─► nativeInit()
    │
    ├─► 启动引导服务
    │   └─► startBootstrapServices()
    │       ├─► Installer
    │       ├─► ActivityManagerService
    │       ├─► PowerManagerService
    │       ├─► LightsService
    │       ├─► DisplayManagerService
    │       └─► PackageManagerService
    │
    ├─► 启动核心服务
    │   └─► startCoreServices()
    │       ├─► BatteryService
    │       ├─► UsageStatsService
    │       └─► WebViewUpdateService
    │
    ├─► 启动其他服务
    │   └─► startOtherServices()
    │       ├─► WindowManagerService
    │       ├─► InputManagerService
    │       ├─► NetworkManagementService
    │       ├─► ConnectivityService
    │       └─► 等等...
    │
    └─► 进入 Looper 循环
        └─► Looper.loop()
```

### 4.3 SystemServer 源码

```java
/**
 * SystemServer - 系统服务主类
 * 位置：frameworks/base/services/java/com/android/server/SystemServer.java
 */
class SystemServer {
    
    public static void main(String[] args) {
        new SystemServer().run();
    }
    
    private void run() {
        // 1. 初始化系统属性
        SystemProperties.set("persist.sys.dalvik.vm.lib.2", "libart.so");
        
        // 2. 创建消息循环
        Looper.prepareMainLooper();
        Looper.getMainLooper().setSlowLogThresholdMs(50, 100);
        
        // 3. 加载 native 库
        System.loadLibrary("android_servers");
        
        // 4. 初始化系统上下文
        createSystemContext();
        
        // 5. 创建 SystemServiceManager
        mSystemServiceManager = new SystemServiceManager(mSystemContext);
        LocalServices.addService(SystemServiceManager.class, mSystemServiceManager);
        
        // 6. 启动服务
        try {
            startBootstrapServices();   // 引导服务
            startCoreServices();        // 核心服务
            startOtherServices();       // 其他服务
        } catch (Throwable ex) {
            throw ex;
        }
        
        // 7. 进入消息循环
        Looper.loop();
    }
    
    /**
     * 启动引导服务
     */
    private void startBootstrapServices() {
        // Installer
        Installer installer = mSystemServiceManager.startService(Installer.class);
        
        // ActivityManagerService
        mActivityManagerService = mSystemServiceManager.startService(
                ActivityManagerService.Lifecycle.class).getService();
        
        // PowerManagerService
        mPowerManagerService = mSystemServiceManager.startService(
                PowerManagerService.class);
        
        // DisplayManagerService
        mDisplayManagerService = mSystemServiceManager.startService(
                DisplayManagerService.class);
        
        // PackageManagerService
        mPackageManagerService = PackageManagerService.main(
                mSystemContext, installer, 
                mFactoryTestMode, FactoryTest.FACTORY_TEST_OFF);
        
        // 等待 Installd 准备就绪
        installer.waitFor();
    }
    
    /**
     * 启动核心服务
     */
    private void startCoreServices() {
        // BatteryService
        mSystemServiceManager.startService(BatteryService.class);
        
        // UsageStatsService
        mSystemServiceManager.startService(UsageStatsService.class);
        
        // WebViewUpdateService
        mWebViewUpdateService = mSystemServiceManager.startService(
                WebViewUpdateService.class);
    }
    
    /**
     * 启动其他服务
     */
    private void startOtherServices() {
        // WindowManagerService
        wm = WindowManagerService.main(context, inputManager, 
                mFactoryTestMode != FactoryTest.FACTORY_TEST_LOW_LEVEL,
                !mFirstBoot, mOnlyCore);
        
        // InputManagerService
        inputManager = new InputManagerService(context);
        
        // 将 WMS 添加到 ServiceManager
        ServiceManager.addService(Context.WINDOW_SERVICE, wm);
        ServiceManager.addService(Context.INPUT_SERVICE, inputManager);
        
        // 启动其他服务...
        
        // 通知 AMS 系统启动完成
        mActivityManagerService.systemReady(() -> {
            // 启动 Launcher
            startHomeOnAllDisplays(currentUserId, "systemReady");
        });
    }
}
```

---

## 5. 系统服务启动顺序

### 5.1 服务启动顺序

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        系统服务启动顺序                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Phase 1: Bootstrap Services (引导服务)
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Installer                  - 安装器                                     │
│  2. DeviceIdentifiersPolicy    - 设备标识策略                               │
│  3. UriGrantsManager           - URI 授权管理                               │
│  4. ActivityManagerService     - Activity 管理                              │
│  5. PowerManagerService        - 电源管理                                   │
│  6. RecoverySystemService      - 恢复服务                                   │
│  7. LightsService              - 灯光服务                                   │
│  8. SidekickInternal           - 辅助服务                                   │
│  9. DisplayManagerService      - 显示管理                                   │
│  10. PackageManagerService     - 包管理                                    │
│  11. UserManagerService        - 用户管理                                   │
│  12. OverlayManagerService     - 覆盖层管理                                 │
│  13. SensorPrivacyService      - 传感器隐私                                 │
└─────────────────────────────────────────────────────────────────────────────┘

Phase 2: Core Services (核心服务)
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. BatteryService             - 电池服务                                   │
│  2. UsageStatsService          - 使用统计                                   │
│  3. WebViewUpdateService       - WebView 更新                               │
│  4. CachedDeviceStateService   - 缓存设备状态                               │
│  5. BinderCallsStatsService    - Binder 调用统计                            │
│  6. LooperStatsService         - Looper 统计                                │
│  7. RollbackManagerService     - 回滚管理                                   │
│  8. BugreportManagerService    - Bug 报告管理                               │
│  9. GpuService                 - GPU 服务                                   │
└─────────────────────────────────────────────────────────────────────────────┘

Phase 3: Other Services (其他服务)
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. VibratorService            - 振动服务                                   │
│  2. AlarmManagerService        - 闹钟服务                                   │
│  3. InputMethodManagerService  - 输入法管理                                 │
│  4. AccessibilityManagerService- 无障碍管理                                 │
│  5. StorageManagerService      - 存储管理                                   │
│  6. UiModeManagerService       - UI 模式管理                                │
│  7. LockSettingsService        - 锁设置服务                                 │
│  8. PersistentDataBlockService - 持久数据块                                 │
│  9. Elm327Service              - ELM327 服务                                │
│  10. ClipboardService          - 剪贴板服务                                 │
│  11. NetworkManagementService  - 网络管理                                   │
│  12. TextServicesManagerService- 文本服务                                   │
│  13. NetworkStatsService       - 网络统计                                   │
│  14. NetworkPolicyManagerService- 网络策略                                  │
│  15. WifiScanningService       - WiFi 扫描                                  │
│  16. ConnectivityService       - 连接服务                                   │
│  17. NsdService                - 网络服务发现                               │
│  18. WindowManagerService      - 窗口管理                                   │
│  19. InputManagerService       - 输入管理                                   │
│  20. ...                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. BootComplete 广播

### 6.1 BootComplete 发送

```java
/**
 * BootComplete 广播发送
 * 位置：frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java
 */
class ActivityManagerService {
    
    /**
     * 系统启动完成
     */
    void finishBooting() {
        // 1. 发送 LOCKED_BOOT_COMPLETED
        Intent lockedIntent = new Intent(Intent.ACTION_LOCKED_BOOT_COMPLETED);
        broadcastIntentLocked(..., lockedIntent, ...);
        
        // 2. 解锁后发送 BOOT_COMPLETED
        if (!mUserManager.isUserUnlocked(userId)) {
            // 等待用户解锁
            mUserController.addUserUnlockedListener(() -> {
                sendBootCompleted(userId);
            });
        } else {
            sendBootCompleted(userId);
        }
    }
    
    /**
     * 发送 BOOT_COMPLETED
     */
    void sendBootCompleted(int userId) {
        Intent intent = new Intent(Intent.ACTION_BOOT_COMPLETED);
        intent.addFlags(Intent.FLAG_RECEIVER_INCLUDE_BACKGROUND);
        
        broadcastIntentLocked(..., intent, ...);
        
        // 标记启动完成
        mBootCompleted = true;
    }
}
```

### 6.2 监听 BootComplete

```java
/**
 * 监听 BOOT_COMPLETED 广播
 */

// AndroidManifest.xml
<receiver android:name=".BootReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>

// BootReceiver.java
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            // 启动服务
            Intent serviceIntent = new Intent(context, MyService.class);
            context.startService(serviceIntent);
        }
    }
}

// 需要权限
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
```

---

## 7. 源码路径

### 7.1 Init 源码

```
system/core/init/
├── init.cpp                           # Init 主程序
├── init_parser.cpp                    # init.rc 解析器
├── signal_handler.cpp                 # 信号处理
├── property_service.cpp               # 属性服务
├── service.cpp                        # 服务管理
└── action.cpp                         # Action 管理

system/core/rootdir/
└── init.rc                            # 默认 init.rc

device/[manufacturer]/[device]/
└── init.[device].rc                   # 设备特定 init.rc
```

### 7.2 Zygote 源码

```
frameworks/base/cmds/app_process/
├── app_main.cpp                       # app_process 入口

frameworks/base/core/java/com/android/internal/os/
├── ZygoteInit.java                    # Zygote 主类
├── Zygote.java                        # Zygote 工具类
├── ZygoteConnection.java              # Zygote 连接
├── ZygoteServer.java                  # Zygote 服务端
└── RuntimeInit.java                   # 运行时初始化

frameworks/base/core/jni/
├── AndroidRuntime.cpp                 # Android Runtime
└── com_android_internal_os_Zygote.cpp # Zygote JNI
```

### 7.3 SystemServer 源码

```
frameworks/base/services/
├── java/com/android/server/
│   ├── SystemServer.java              # SystemServer 主类
│   ├── SystemServiceManager.java      # 服务管理器
│   └── SystemService.java             # 服务基类
│
├── core/java/com/android/server/
│   ├── am/ActivityManagerService.java # AMS
│   ├── wm/WindowManagerService.java   # WMS
│   ├── pm/PackageManagerService.java  # PMS
│   └── ...
│
└── ...
```

---

## 8. 面试常见问题

### 8.1 基础问题

**Q1: Android 系统启动流程？**

```
1. Boot ROM - 执行固化代码
2. Bootloader - 初始化硬件，加载内核
3. Linux Kernel - 启动 init 进程
4. Init - 解析 init.rc，启动 Zygote
5. Zygote - 预加载类和资源，启动 SystemServer
6. SystemServer - 启动系统服务
7. Launcher - 显示桌面
```

**Q2: Zygote 的作用？**

```
1. 创建 ART 虚拟机
2. 预加载类和资源
3. 启动 SystemServer
4. 监听 Socket，响应 fork 请求
5. 为新应用提供进程模板

优势：
• 预加载共享资源，减少启动时间
• Copy-on-Write 机制，节省内存
```

**Q3: SystemServer 启动了哪些服务？**

```
引导服务:
• ActivityManagerService (AMS)
• PowerManagerService (PMS)
• PackageManagerService (PMS)
• DisplayManagerService (DMS)

核心服务:
• BatteryService
• UsageStatsService

其他服务:
• WindowManagerService (WMS)
• InputManagerService (IMS)
• 等等...
```

### 8.2 进阶问题

**Q4: Init 进程的职责？**

```
1. 解析 init.rc 配置文件
2. 启动关键守护进程
3. 挂载文件系统
4. 设置系统属性
5. 启动 Zygote 和 ServiceManager
6. 监听子进程退出并重启
```

**Q5: Zygote fork 的流程？**

```
1. AMS 通过 Zygote Socket 发送 fork 请求
2. Zygote 接收请求
3. Zygote.forkAndSpecialize() fork 新进程
4. 子进程处理:
   • 设置进程名
   • 关闭 Zygote Socket
   • 调用 ActivityThread.main()
5. 父进程返回子进程 PID
```

**Q6: BOOT_COMPLETED 广播何时发送？**

```
发送时机：
1. 所有系统服务启动完成
2. 用户解锁设备后
3. SystemServer 调用 AMS.systemReady()

接收方式：
1. 注册 BroadcastReceiver
2. 监听 Intent.ACTION_BOOT_COMPLETED
3. 需要 RECEIVE_BOOT_COMPLETED 权限
```

---

## 总结

本文详细讲解了 Android 系统启动流程的核心知识点，包括：

1. **启动流程总览** - 从 Boot ROM 到 Launcher
2. **Init 进程** - 配置解析和服务启动
3. **Zygote 进程** - fork 机制和预加载
4. **SystemServer** - 系统服务启动
5. **服务启动顺序** - Bootstrap/Core/Other
6. **BootComplete** - 启动完成广播

掌握这些知识点对于 Android 面试和系统级开发都至关重要。

---

*文档更新时间: 2026-03-12*