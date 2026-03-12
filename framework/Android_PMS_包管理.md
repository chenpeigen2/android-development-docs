# Android PMS 包管理深度解析

> 作者：OpenClaw | 日期：2026-03-12
> 基于源码：Android 16 (API 36) AOSP

## 目录

1. [概述](#1-概述)
2. [PMS 架构总览](#2-pms-架构总览)
3. [APK 安装流程](#3-apk-安装流程)
4. [组件解析](#4-组件解析)
5. [权限管理机制](#5-权限管理机制)
6. [应用签名验证](#6-应用签名验证)
7. [dex2oat 编译流程](#7-dex2oat-编译流程)
8. [源码路径](#8-源码路径)
9. [面试常见问题](#9-面试常见问题)

---

## 1. 概述

**PackageManagerService (PMS)** 是 Android 系统的核心服务之一，负责管理所有应用包的安装、卸载、更新、权限管理，以及组件的解析和查询。

### 1.1 PMS 的核心职责

- **包管理**: APK 安装、卸载、更新
- **组件解析**: AndroidManifest.xml 解析
- **权限管理**: 权限检查和授予
- **签名验证**: APK 签名验证
- **编译优化**: dex2oat 编译

### 1.2 PMS 在系统中的位置

```
应用层 (PackageManager API)
    ↓ Binder IPC
系统服务层 (PackageManagerService)
    ↓
存储层 (/data/app, /data/data, packages.xml)
```

---

## 2. PMS 架构总览

### 2.1 核心组件

```java
/**
 * PackageManagerService - 包管理服务
 * 位置：frameworks/base/services/core/java/com/android/server/pm/PackageManagerService.java
 */
class PackageManagerService {
    // 核心组件
    final PackageParser mPackageParser;       // 包解析器
    final Settings mSettings;                 // 包设置
    final Installer mInstaller;               // 安装器
    final PermissionManagerService mPermissionManager; // 权限管理
    
    // 包映射
    final ArrayMap<String, PackageParser.Package> mPackages; // 包名 → Package
    
    // 组件映射
    final ActivityIntentResolver mActivities; // Activity 解析器
    final ServiceIntentResolver mServices;    // Service 解析器
    final ProviderIntentResolver mProviders;  // Provider 解析器
    final ActivityIntentResolver mReceivers;  // Receiver 解析器
}

/**
 * Settings - 包设置
 * 位置：frameworks/base/services/core/java/com/android/server/pm/Settings.java
 */
class Settings {
    final ArrayMap<String, PackageSetting> mPackages; // 包设置映射
    final ArrayMap<String, SharedUserSetting> mSharedUsers; // 共享 UID
    
    void writePackageRestrictionsLPr(int userId); // 写入配置
    boolean readPackageRestrictionsLPr(int userId); // 读取配置
}
```

---

## 3. APK 安装流程

### 3.1 安装流程总览

```
1. 准备阶段
   └─► PackageInstaller.createSession()
       └─► 分配 Session ID
       └─► 准备临时目录

2. 复制 APK
   └─► PackageInstaller.Session.write()
       └─► 复制到临时目录

3. 解析 APK
   └─► PackageParser.parsePackage()
       └─► 解析 AndroidManifest.xml
       └─► 提取组件信息

4. 验证签名
   └─► ApkSignatureVerifier.verify()
       └─► 检查 APK 完整性

5. 安装
   └─► Installer.install()
       └─► 创建应用目录
       └─► dex2oat 编译

6. 完成
   └─► 更新 packages.xml
   └─► 发送 ACTION_PACKAGE_ADDED 广播
```

### 3.2 安装命令

```bash
# adb install
adb install app.apk              # 普通安装
adb install -r app.apk           # 替换安装
adb install -d app.apk           # 降级安装
adb install -g app.apk           # 授予所有权限

# pm install
adb shell pm install app.apk
adb shell pm install -r app.apk

# 卸载
adb uninstall com.example.app

# 查看已安装应用
adb shell pm list packages
adb shell pm list packages -3    # 第三方应用
adb shell pm dump com.example.app
```

---

## 4. 组件解析

### 4.1 AndroidManifest.xml 解析

```java
/**
 * PackageParser - 包解析器
 */
class PackageParser {
    // 解析 APK
    public Package parsePackage(File apkFile) {
        // 1. 解析 AndroidManifest.xml
        // 2. 提取 Activity/Service/Provider/Receiver
        // 3. 提取权限信息
        // 4. 提取签名信息
    }
}

/**
 * Package - 包信息
 */
class Package {
    String packageName;                         // 包名
    ArrayList<Activity> activities;             // Activity 列表
    ArrayList<Service> services;                // Service 列表
    ArrayList<Provider> providers;              // Provider 列表
    ArrayList<Activity> receivers;              // Receiver 列表
    ArrayList<String> requestedPermissions;     // 请求的权限
}
```

### 4.2 Intent 匹配规则

```
匹配流程：
1. Action 匹配 - Intent 必须指定 Action
2. Category 匹配 - 所有 Category 必须在 IntentFilter 中
3. Data 匹配 - Scheme/Host/Path/MimeType

示例：
<activity android:name=".MainActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:scheme="https" android:host="www.example.com" />
    </intent-filter>
</activity>
```

---

## 5. 权限管理机制

### 5.1 权限类型

```
1. 安装时权限
   • 正常权限 - 自动授予 (INTERNET, BLUETOOTH)
   • 签名权限 - 相同签名才能授予
   • 特权权限 - 系统应用专用

2. 运行时权限
   • 危险权限 - 需要用户授权 (CAMERA, LOCATION)
   • 分组管理

3. 特殊权限
   • SYSTEM_ALERT_WINDOW (悬浮窗)
   • WRITE_SETTINGS (系统设置)
```

### 5.2 权限组

```
CALENDAR: READ_CALENDAR, WRITE_CALENDAR
CAMERA: CAMERA
CONTACTS: READ_CONTACTS, WRITE_CONTACTS, GET_ACCOUNTS
LOCATION: ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION
MICROPHONE: RECORD_AUDIO
PHONE: READ_PHONE_STATE, CALL_PHONE
SMS: SEND_SMS, RECEIVE_SMS, READ_SMS
STORAGE: READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
```

### 5.3 运行时权限请求

```java
// 检查权限
if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
        != PackageManager.PERMISSION_GRANTED) {
    // 请求权限
    ActivityCompat.requestPermissions(this,
            new String[]{Manifest.permission.CAMERA},
            REQUEST_CODE);
}

// 处理结果
@Override
public void onRequestPermissionsResult(int requestCode,
        String[] permissions, int[] grantResults) {
    if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
        // 权限授予
    }
}
```

---

## 6. 应用签名验证

### 6.1 APK 签名方案

```
1. v1 (JAR Signing) - Android 7.0 之前
   • 基于 JDK jarsigner
   • 可以修改后重新签名

2. v2 - Android 7.0+
   • 签名嵌入 APK
   • 保护完整性

3. v3 - Android 9.0+
   • 支持密钥轮转

4. v4 - Android 11+
   • 支持增量安装
```

### 6.2 签名命令

```bash
# 生成密钥库
keytool -genkeypair -alias mykey -keyalg RSA -keysize 2048 \
    -validity 10000 -keystore my-release-key.jks

# 签名 APK
apksigner sign --ks my-release-key.jks --out app-signed.apk app.apk

# 查看签名
apksigner verify --print-certs app.apk
```

---

## 7. dex2oat 编译流程

### 7.1 dex2oat 概述

```
dex2oat - DEX to OAT 编译器
作用：将 DEX 字节码编译为 OAT 机器码

编译时机：
1. 安装时 (AOT) - 完整编译，启动最快
2. 运行时 (JIT) - 按需编译热点代码
3. 后台编译 - 根据使用情况优化

输出文件：
• odex: /data/app/[package]/oat/arm64/base.odex
• vdex: /data/app/[package]/oat/arm64/base.vdex
• art: /data/app/[package]/oat/arm64/base.art
```

### 7.2 ART 虚拟机

```
ART (Android Runtime) 特点：
1. AOT (Ahead-of-Time) 编译
2. JIT (Just-in-Time) 编译
3. 混合编译模式

编译策略：
• verify - 只验证
• quicken - 快速编译
• speed - 完整 AOT 编译
• everything - 编译所有代码
```

---

## 8. 源码路径

### 8.1 PMS 源码

```
frameworks/base/services/core/java/com/android/server/pm/
├── PackageManagerService.java          # PMS 主类
├── Settings.java                       # 包设置
├── PackageParser.java                  # 包解析器
├── Installer.java                      # 安装器
├── PermissionManagerService.java       # 权限管理
├── PackageDexOptimizer.java            # DEX 优化器
├── AppDataHelper.java                  # 应用数据助手
└── KeySetManagerService.java           # 密钥管理
```

### 8.2 客户端源码

```
frameworks/base/core/java/android/content/pm/
├── PackageManager.java                 # PackageManager API
├── ApplicationInfo.java                # 应用信息
├── ActivityInfo.java                   # Activity 信息
├── ServiceInfo.java                    # Service 信息
├── ProviderInfo.java                   # Provider 信息
├── PackageInfo.java                    # 包信息
└── PermissionInfo.java                 # 权限信息
```

---

## 9. 面试常见问题

### 9.1 基础问题

**Q1: PMS 的职责是什么？**

```
1. 包管理 - APK 安装/卸载/更新
2. 组件解析 - AndroidManifest.xml 解析
3. 权限管理 - 权限检查和授予
4. 签名验证 - APK 完整性验证
5. 编译优化 - dex2oat 编译
```

**Q2: APK 安装流程？**

```
1. 创建 Session
2. 复制 APK 到临时目录
3. 解析 AndroidManifest.xml
4. 验证签名
5. 创建应用目录
6. dex2oat 编译
7. 更新 packages.xml
8. 发送广播
```

**Q3: 运行时权限和安装时权限的区别？**

```
安装时权限：
• 正常权限 - 自动授予
• 签名权限 - 相同签名

运行时权限：
• 危险权限 - 需要用户授权
• 分组管理
• 可撤销
```

### 9.2 进阶问题

**Q4: Intent 匹配规则？**

```
1. Action 匹配 - Intent 必须指定 Action
2. Category 匹配 - 所有 Category 必须在 IntentFilter 中
3. Data 匹配 - Scheme/Host/Path/MimeType
```

**Q5: APK 签名方案？**

```
v1: JAR Signing, 可修改重签名
v2: 嵌入 APK, 保护完整性
v3: 支持密钥轮转
v4: 支持增量安装
```

**Q6: dex2oat 的作用？**

```
将 DEX 字节码编译为 OAT 机器码
编译时机：安装时/运行时/后台
编译策略：verify/quicken/speed/everything
```

---

## 总结

本文详细讲解了 Android PMS (PackageManagerService) 的核心知识点，包括：

1. **PMS 架构** - 包管理核心服务
2. **APK 安装** - 完整安装流程
3. **组件解析** - AndroidManifest.xml 解析
4. **权限管理** - 运行时权限机制
5. **签名验证** - APK 签名方案
6. **dex2oat** - 编译优化

掌握这些知识点对于 Android 面试和应用开发都至关重要。

---

*文档更新时间: 2026-03-12*