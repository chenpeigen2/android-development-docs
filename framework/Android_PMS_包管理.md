# Android PMS 包管理深度解析

> 作者：OpenClaw | 日期：2026-03-12
> 基于源码：AOSP Android 17 / API 37，固定 tag `android-17.0.0_r1`；复核日期：2026-09-10。

## 目录

- [1. 概述](#1-概述)
  - [1.1 PMS 的核心职责](#11-pms-的核心职责)
  - [1.2 PMS 在系统中的位置](#12-pms-在系统中的位置)
- [2. PMS 架构总览](#2-pms-架构总览)
  - [2.1 核心组件](#21-核心组件)
- [3. APK 安装流程](#3-apk-安装流程)
  - [3.1 安装流程总览](#31-安装流程总览)
  - [3.2 安装命令](#32-安装命令)
- [4. 组件解析](#4-组件解析)
  - [4.1 AndroidManifest.xml 解析](#41-androidmanifestxml-解析)
  - [4.2 Intent 匹配规则](#42-intent-匹配规则)
- [5. 权限管理机制](#5-权限管理机制)
  - [5.1 权限类型](#51-权限类型)
  - [5.2 权限组](#52-权限组)
  - [5.3 运行时权限请求](#53-运行时权限请求)
- [6. 应用签名验证](#6-应用签名验证)
  - [6.1 APK 签名方案](#61-apk-签名方案)
  - [6.2 签名命令](#62-签名命令)
- [7. dex2oat 编译流程](#7-dex2oat-编译流程)
  - [7.1 dex2oat 概述](#71-dex2oat-概述)
  - [7.2 ART 虚拟机](#72-art-虚拟机)
- [8. 应用更新流程](#8-应用更新流程)
  - [8.1 更新流程总览](#81-更新流程总览)
  - [8.2 热更新机制](#82-热更新机制)
- [9. 多用户支持](#9-多用户支持)
  - [9.1 多用户架构](#91-多用户架构)
  - [9.2 用户相关 API](#92-用户相关-api)
- [10. Instant App 机制](#10-instant-app-机制)
  - [10.1 Instant App 概述](#101-instant-app-概述)
  - [10.2 Instant App 开发](#102-instant-app-开发)
- [11. 应用备份与恢复](#11-应用备份与恢复)
  - [11.1 Backup 机制](#111-backup-机制)
  - [11.2 Backup 配置](#112-backup-配置)
  - [11.3 Backup API](#113-backup-api)
- [12. 应用优化建议](#12-应用优化建议)
  - [12.1 安装优化](#121-安装优化)
  - [12.2 更新优化](#122-更新优化)
- [13. 面试常见问题](#13-面试常见问题)
  - [13.1 基础问题](#131-基础问题)
  - [13.2 进阶问题](#132-进阶问题)
- [14. 源码路径](#14-源码路径)
  - [14.1 PMS 源码](#141-pms-源码)
  - [14.2 客户端源码](#142-客户端源码)
- [总结](#总结)

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

```text
应用层 (PackageManager API)
    ↓ Binder IPC
系统服务层 (PackageManagerService)
    ↓
存储层 (/data/app, /data/data, packages.xml)
```

---

## 2. PMS 架构总览

### 2.1 核心组件

PMS 持有可变包状态与安装协调逻辑，但查询、解析、权限和 ART 编译不是一个巨型 PackageParser 对象完成的。

```text
PackageManagerService
  Settings / PackageSetting：持久化与用户级包设置
  mPackages：AndroidPackage 等已解析包对象
  ComponentResolver：组件索引与 IntentFilter 匹配
  snapshotComputer -> Computer / ComputerEngine：查询快照、可见性过滤
  PackageParser2 -> ParsingPackageUtils -> ParsedPackage：解析新 APK
  PackageInstallerService / Session：安装者身份、session、写入、提交、校验
  InstallPackageHelper：prepare / scan / reconcile / commit 协调
  Installer -> installd：应用数据目录及 native 安装辅助，不是 Installer.install()
  PermissionManagerServiceInternal：对接权限服务
  DexOptHelper -> ART Service：按策略请求 dexopt
```

`Settings` 保存包与用户状态，不应把旧 `PackageParser.Package` 和四套 resolver 都伪装为 PMS 当前字段。对外 `IPackageManager` Binder 由 PMS 的内部实现提供，查询在合适的 Computer 快照上进行，避免不必要地长期持有可变状态锁。

源码：[PackageManagerService.java:5071](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/pm/PackageManagerService.java#5071)；[PackageManagerService.java:1200](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/pm/PackageManagerService.java#1200)；[PackageParser2.java:117](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/pm/parsing/PackageParser2.java#117)。

## 3. APK 安装流程

### 3.1 安装流程总览

```text
PackageInstaller.createSession -> Session.openWrite 写入 base / split APK
  -> Session.fsync / close -> Session.commit(statusReceiver)
  -> PackageInstallerSession：封存、安装权限/用户确认、APK 校验及 verification
  -> InstallingSession -> InstallPackageHelper.installPackagesTraced
      prepareInstallPackages：包结构/安装请求准备
      scanInstallPackages：候选包扫描
      reconcileInstallPackages：签名、共享库、更新及批次兼容性
      renameAndUpdatePaths：确定最终代码路径
      prepPerformDexoptIfNeeded：按需交 ART Service，异步完成后继续
      doPostDexopt -> commitPackagesLocked 等提交分支
      completeInstallProcess / doPostInstall：持久化、回调、广播和清理
```

这是普通非 staged 安装的主线；多包原子提交、APEX、增量安装及更新后的重启策略有额外分支。签名不是“解析完调用一次 verify 就万事大吉”：APK 内容校验与新旧 signing details 的更新兼容性是不同层次。

必须先更新最终代码路径再 dexopt，因为 ART 产物会编码路径；不是“commit 后总会完整 dex2oat”，也不是 Installer 提供通用 install()。失败应沿完成/清理路径回报 session 状态，不能无条件发送 PACKAGE_ADDED。

源码：[InstallPackageHelper.java:1081](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/pm/InstallPackageHelper.java#1081)；[InstallPackageHelper.java:1117](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/pm/InstallPackageHelper.java#1117)；[PackageInstallerSession.java:2392](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/pm/PackageInstallerSession.java#2392)。

### 3.2 安装命令

```bash
# adb install
adb install app.apk              # 普通安装
adb install -r app.apk           # 替换安装
adb install -d app.apk           # 请求允许降级，仍受 debuggable/安装权限等约束
adb install -g app.apk           # 请求授予可授予的运行时权限，不含所有特殊/签名权限

# pm install
adb shell pm install /data/local/tmp/app.apk
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

当前 PMS 安装解析入口使用内部 `PackageParser2`，委托 `ParsingPackageUtils`，产出 `ParsedPackage`；已安装包使用 `AndroidPackage` 等接口，不能继续用旧 `PackageParser.Package` 的公开字段描述其结构。

```java
// PackageParser2 的签名摘录，不是公共 SDK。
public ParsedPackage parsePackage(File packageFile, int flags, boolean useCaches)
        throws PackageParserException;
```

解析内容包括 manifest 的包身份、SDK/组件声明、intent-filter、请求权限与 split 关系等。解析器使用 ParseResult 传播错误，符合缓存条件时可以复用解析结果；缓存命中不免除安装策略、签名兼容性和用户权限检查。解析阶段得到的组件声明还要在扫描/提交过程中转为可查询状态，不能等同于“组件已经安装并可启动”。

源码：[PackageParser2.java:117](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/pm/parsing/PackageParser2.java#117)；[ReconcilePackageUtils.java:65](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/pm/ReconcilePackageUtils.java#65)。

### 4.2 Intent 匹配规则

```text
匹配流程：
1. Action 匹配 - 非 null action 必须匹配过滤器；null action 跳过该项检查，仍需满足其他匹配条件
2. Category 匹配 - 所有 Category 必须在 IntentFilter 中
3. Data 匹配 - MIME、scheme、authority、path 等按规则检查；不是字符串全等
4. 启动 Activity 的隐式解析还涉及 DEFAULT、导出/权限、包可见性和用户状态

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

IntentFilter 的底层判断见 [IntentFilter.java:2456](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/content/IntentFilter.java#2456)；解析到匹配组件不等于一定有权限启动。

### 5.1 权限类型

```text
1. 安装时权限
   • 正常权限 - 按安装策略授予（如 INTERNET；BLUETOOTH 为旧权限，现代扫描/连接另有运行时权限）
   • 签名权限 - 相同签名才能授予
   • privileged 保护标志 - 受 priv-app 位置、许可名单等约束，不是任意系统应用自动获得

2. 运行时权限
   • 危险权限 - 需要用户授权 (CAMERA, LOCATION)
   • 权限组用于组织展示，不保证同组权限自动一起授予

3. 特殊权限
   • SYSTEM_ALERT_WINDOW (悬浮窗)
   • WRITE_SETTINGS (系统设置)
```

### 5.2 权限组

```text
CALENDAR: READ_CALENDAR, WRITE_CALENDAR
CAMERA: CAMERA
CONTACTS: READ_CONTACTS, WRITE_CONTACTS, GET_ACCOUNTS
LOCATION: ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION
MICROPHONE: RECORD_AUDIO
PHONE: READ_PHONE_STATE, CALL_PHONE
SMS: SEND_SMS, RECEIVE_SMS, READ_SMS
历史 STORAGE: READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE（现代 target 不应沿用为通用存储权限）
现代媒体访问按 READ_MEDIA_*、选定照片等能力与 target/设备版本判断
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
    super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    if (requestCode == REQUEST_CODE && grantResults.length > 0
            && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
        // 权限授予
    }
}
```

---

## 6. 应用签名验证

### 6.1 APK 签名方案

```text
1. v1 (JAR Signing) - 旧方案，后续系统仍有兼容支持
   • 基于 JDK jarsigner
   • 保护签名条目内容；修改受保护内容会使原签名失效

2. v2 - Android 7.0+
   • 签名嵌入 APK
   • 保护完整性

3. v3 - Android 9.0+
   • 支持密钥轮转

4. v4 - Android 11+
   • 独立 .idsig 支持增量安装，与 v2/v3 等内容签名配合
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

dex2oat 是 ART 的 AOT 编译工具；运行时 JIT 由 ART 内部 JIT 完成，不是每个热点都启动 dex2oat 子进程。Android 17 中 PMS 通过 DexOptHelper 等协调 ART Service，按安装原因、profile、资源预算和策略决定是否编译以及编译多少。

```text
安装原因/后台优化请求 -> DexOptHelper / ART Service
  -> 编译过滤器、profile 与资源策略 -> dex2oat（需要 AOT 时）
运行中方法变热 -> ART JIT -> 进程内机器码 / profile 信息
profile -> 后续 profile-guided AOT
```

常见产物为 odex/vdex，按条件可能有 app image；实际路径受 ISA、代码位置和 ART 管理方式影响，不保证每个包都有 base.art。安装不必完整 AOT，不能把“安装 AOT 启动最快”写成无条件规律。

源码：[DexOptHelper.java:57](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/pm/DexOptHelper.java#57)；[ArtManagerLocal.java:379](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/libartservice/service/java/com/android/server/art/ArtManagerLocal.java#379)。

### 7.2 ART 虚拟机

ART 组合解释执行、JIT 和 AOT。过滤器示例：`verify` 以校验为主，`speed-profile` 按 profile 编译，`speed` 更偏向广泛编译。`quicken` / `everything` 不能作为本 tag 推荐的 PMS 编译策略清单；过滤器只是输入之一，实际工作还要看可用 profile 和是否已有可复用产物。

安装时减少编译成本与运行时优化之间是资源权衡；应分别看 dexopt 请求原因、编译结果和真实启动 trace，而非用 APK 大小推定收益。源码：[ArtManagerLocal.java:379](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/libartservice/service/java/com/android/server/art/ArtManagerLocal.java#379)。

## 8. 应用更新流程

### 8.1 更新流程总览

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        应用更新流程                                         │
└─────────────────────────────────────────────────────────────────────────────┘

1. 检测更新
   └─► 版本号比较 (versionCode)
       └─► 新版本 > 当前版本 → 提示更新

2. 下载 APK
   └─► DownloadManager 或自行下载
       └─► 验证可信来源与 APK 签名（散列只有与可信期望值比较才有意义）

3. 安装更新
   └─► 覆盖安装 (adb install -r)
       └─► 替换已存在的应用

4. 数据保留
   └─► /data/data/[packageName]/ 保留
       └─► SharedPreferences 保留
       └─► 数据库保留

5. 权限检查
   └─► 新增权限需要重新授权
       └─► 签名必须满足更新兼容规则（含合法签名轮换 lineage/capability）
```

### 8.2 热更新机制

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        热更新 vs 原生更新                                   │
└─────────────────────────────────────────────────────────────────────────────┘

原生更新 (Google Play):
• 安装客户端可采用差分下载或 split 交付
• 覆盖安装
• 是否需要用户确认取决于安装者能力和系统策略
• 数据保留

热更新 (Tinker/Sophix):
• 仅下载差分包
• 运行时合并
• 无需安装
• 生效时机由补丁框架决定，常需重启进程；不是 PMS 保证

热更新原理：
1. DexDiff 算法计算差异
2. 生成补丁包 (.patch)
3. 客户端下载补丁
4. 合并到原 DEX
5. 重新加载类

限制：
• 不能修改 AndroidManifest.xml
• 资源修改能力取决于补丁框架及版本，不能视为系统保证
• 不能新增四大组件
```

---

## 9. 多用户支持

### 9.1 多用户架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Android 多用户架构                                   │
└─────────────────────────────────────────────────────────────────────────────┘

用户类型：
1. 主用户 (User 0)
   • 系统第一个用户
   • user 0 是系统用户；headless system-user 模式下并非日常前台主用户
   • 用户管理能力还取决于用户类型、限制与管理权限

2. 次要用户 (User 10+)
   • 普通用户
   • 独立应用数据
   • 独立设置

3. 工作资料 (Work Profile)
   • 企业环境
   • 应用隔离
   • 独立 VPN/策略

4. 访客用户 (Guest)
   • 临时用户
   • 数据可清除

目录结构：
/data/user/
├── 0/                    # 主用户
│   └── com.example.app/
├── 10/                   # 次要用户
│   └── com.example.app/
└── 99/                   # 示例用户 ID，不固定为访客
    └── com.example.app/
```

### 9.2 用户相关 API

```java
UserManager um = context.getSystemService(UserManager.class);
boolean managed = um.isManagedProfile();
List<UserHandle> profiles = um.getUserProfiles(); // 调用用户可关联的 profiles，不是系统全部用户
UserHandle user = um.getUserForSerialNumber(serialNumber); // 序列号到 handle，可能为 null
```

`UserManager.createUser(String, int)` 的框架内部签名返回 `UserInfo`，不是 UserHandle；创建/移除用户属于受权限保护的系统能力，不能将它们列成普通应用可任意调用的 public SDK。用户 ID 与持久序列号也不是同一个值。

源码：[UserManager.java:4570](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/UserManager.java#4570)；[UserManager.java:5731](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/UserManager.java#5731)。

## 10. Instant App 机制

### 10.1 Instant App 概述

本节讨论固定 AOSP tag 仍保留的 instant-app 包状态与隔离机制，不将商店服务的历史产品规格当作 Android 17 平台约束。

Instant app 仍需由系统建立包/UID、代码与受限数据环境，并非“完全无需安装也没有本地存储”。PMS 根据 instant 状态对包查询可见性、组件解析和权限等施加额外限制。模块下载、链接入口和安装提示属于安装器/分发产品层，不能从 PMS 源码推出“每模块最大 10 MB”或“不能访问所有敏感权限”。

源码：[ComputerEngine.java:606](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/pm/ComputerEngine.java#606)。

### 10.2 Instant App 开发

使用平台 API 查询本应用包状态，不给出虚构的 `android { feature "instant" }` DSL：

```java
// API 26+；这里只查询状态，不代表某分发平台仍提供 instant 发布流程。
boolean instant = context.getPackageManager().isInstantApp();
```

本 tag 的服务端相关分支可用于维护兼容性和研究包可见性；商店发布、模块大小和安装提示 SDK 需另行按相应产品文档核验，不能靠 AOSP 固定 tag 证明。源码：[ComputerEngine.java:606](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/pm/ComputerEngine.java#606)。

## 11. 应用备份与恢复

### 11.1 Backup 机制

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Android Backup 机制                                 │
└─────────────────────────────────────────────────────────────────────────────┘

备份类型：
1. 键值对备份 (Key/Value Backup)
   • 适用于少量数据
   • SharedPreferences
   • 文件数据

2. 文件备份 (File Backup)
   • 适用于大量数据
   • 数据库文件
   • 整个目录

3. 设备到设备 (D2D)
   • 直接传输
   • 换机助手

备份位置：
• 由设备安装并选择的 BackupTransport 决定；AOSP 不保证 Google Drive
• 本地/设备迁移 transport（依设备实现）
• OEM 云服务

备份触发：
• 自动备份按 transport、调度与资源条件触发，不保证每天一次
• dataChanged 等请求由系统调度；旧 adb backup 不应作为 Android 17 通用备份方案
• 恢复通常发生在设备设置/包安装等流程，不是重置后自动执行备份
```

### 11.2 Backup 配置

Android 12+ 使用 dataExtractionRules 区分云备份与设备迁移；可保留 fullBackupContent 供旧平台。以下文件分开放置：

```xml
<!-- AndroidManifest.xml 的 application 属性片段 -->
<application
    android:allowBackup="true"
    android:fullBackupContent="@xml/backup_rules"
    android:dataExtractionRules="@xml/data_extraction_rules" />
```

```xml
<!-- res/xml/data_extraction_rules.xml -->
<data-extraction-rules>
    <cloud-backup>
        <include domain="sharedpref" path="." />
        <exclude domain="sharedpref" path="device.xml" />
    </cloud-backup>
    <device-transfer>
        <include domain="sharedpref" path="." />
        <exclude domain="sharedpref" path="device.xml" />
    </device-transfer>
</data-extraction-rules>
```

```xml
<!-- res/xml/backup_rules.xml：旧平台兼容规则 -->
<full-backup-content>
    <include domain="sharedpref" path="." />
    <exclude domain="sharedpref" path="device.xml" />
</full-backup-content>
```

`no_backup` 不是合法 domain；getNoBackupFilesDir 下的数据本来就不进入正常全量备份集合。备份白名单应排除设备绑定标识、凭据等不可迁移内容。

### 11.3 Backup API

```java
/**
 * BackupManager - 备份管理
 * 位置：frameworks/base/core/java/android/app/backup/BackupManager.java
 */
class BackupManager {
    // 请求备份
    public void dataChanged();
    
    // 恢复数据
    @Deprecated
    public int requestRestore(RestoreObserver observer);
}

// 使用示例
BackupManager bm = new BackupManager(context);
bm.dataChanged(); // 请求调度，不同步开始，也不用于强制立即全量备份

// 使用 BackupAgent
class MyBackupAgent extends BackupAgent {
    @Override
    public void onBackup(ParcelFileDescriptor oldState, 
            BackupDataOutput data, ParcelFileDescriptor newState) {
        // 执行备份
    }
    
    @Override
    public void onRestore(BackupDataInput data, 
            int appVersionCode, ParcelFileDescriptor newState) {
        // 执行恢复
    }
}
```

---

## 12. 应用优化建议

BackupManager 的历史 requestRestore 返回状态 int 且已废弃；调用也不能保证立即恢复。源码：[BackupManager.java:335](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/backup/BackupManager.java#335)。

### 12.1 安装优化

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        安装优化建议                                         │
└─────────────────────────────────────────────────────────────────────────────┘

1. APK 瘦身
   • 启用 R8 代码混淆
   • 移除无用资源 (shrinkResources)
   • 使用 WebP 替代 PNG
   • 按实际 ABI 交付 so，避免无用架构和重复依赖

2. 安装时间优化
   • 减少 Dex 数量
   • 控制依赖和安装产物；Multidex 用于方法数容量，不是安装加速技术
   • 延迟非必要运行时初始化（改善启动，不直接减少安装扫描）

3. 启动优化
   • 异步初始化
   • 懒加载
   • 预加载关键类

配置示例：
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'),
                    'proguard-rules.pro'
        }
    }
}
```

### 12.2 更新优化

```text
1. 增量更新
   • 使用 APK Patch
   • 减少下载量
   • 节省流量

2. 热更新
   • Tinker / Sophix
   • 快速修复 Bug
   • 无需发布新版

3. 动态加载
   • 插件化框架
   • 按需加载模块
   • 减少安装大小
```

---

## 13. 面试常见问题

### 13.1 基础问题

**Q1: PMS 的职责是什么？**

```text
1. 包管理 - APK 安装/卸载/更新
2. 组件解析 - AndroidManifest.xml 解析
3. 权限管理 - 权限检查和授予
4. 签名验证 - APK 完整性验证
5. 编译优化 - dex2oat 编译
```

**Q2: APK 安装流程？**

```text
1. 创建 Session
2. 复制 APK 到临时目录
3. 解析 AndroidManifest.xml
4. 验证签名
5. 创建应用目录
6. 按策略准备 dexopt；最终提交与完成回调见 3.1
7. 更新 packages.xml
8. 发送广播
```

**Q3: 运行时权限和安装时权限的区别？**

```text
安装时权限：
• 正常权限 - 自动授予
• 签名权限 - 相同签名

运行时权限：
• 危险权限 - 需要用户授权
• 权限组用于组织展示，不保证同组权限自动一起授予
• 可撤销
```

### 13.2 进阶问题

**Q4: Intent 匹配规则？**

```text
1. Action 匹配 - 非 null action 必须匹配过滤器；null action 跳过该项检查，仍需满足其他匹配条件
2. Category 匹配 - 所有 Category 必须在 IntentFilter 中
3. Data 匹配 - MIME、scheme、authority、path 等按规则检查；不是字符串全等
4. 启动 Activity 的隐式解析还涉及 DEFAULT、导出/权限、包可见性和用户状态
```

**Q5: APK 签名方案？**

```text
v1: JAR 条目签名；重签名并不绕过旧签名或更新兼容性校验
v2: 嵌入 APK, 保护完整性
v3: 支持密钥轮转
v4: 支持增量安装
```

**Q6: dex2oat 的作用？**

```text
将 DEX 字节码编译为 OAT 机器码
AOT 请求：安装/后台等；运行时热点由 ART JIT 处理
常见过滤器：verify / speed-profile / speed；由 ART Service 按原因和 profile 决定
```

**Q7: 多用户如何隔离应用数据？**

```text
目录隔离：
• /data/user/0/ - 主用户
• /data/user/10/ - 次要用户
• /data/user/99/ - 示例用户 ID；访客 ID 并非固定 99

权限隔离：
• 每个用户独立权限
• 应用数据不共享
```

**Q8: Instant App 的原理？**

```text
1. 按需加载模块
2. 在沙箱中运行
3. 无需完整安装
4. 平台没有该历史商店产品大小常量承诺

限制：
• 可申请能力受 instant-app 权限与可见性策略限制
• 不能后台运行
```

**Q9: 应用备份机制？**

```text
备份类型：
• 键值对备份 - 少量数据
• 文件备份 - 大量数据
• 设备到设备 - 直接传输

触发时机：
• 自动备份按 transport、调度与资源条件触发，不保证每天一次
• dataChanged 等请求由系统调度；旧 adb backup 不应作为 Android 17 通用备份方案
• 恢复通常发生在设备设置/包安装等流程，不是重置后自动执行备份
```

**Q10: 如何优化 APK 大小？**

```text
1. 启用 R8 代码混淆
2. 移除无用资源
3. 使用 WebP 替代 PNG
4. 按实际 ABI 交付 so
5. 减少 Dex 数量
```

---

## 14. 源码路径

### 14.1 PMS 源码

```text
frameworks/base/services/core/java/com/android/server/pm/
  PackageManagerService.java / Computer.java / ComputerEngine.java
  Settings.java / PackageSetting.java / ComponentResolver（resolver 子包）
  PackageInstallerService.java / PackageInstallerSession.java / InstallingSession.java
  InstallPackageHelper.java / ScanPackageUtils.java / ReconcilePackageUtils.java
  Installer.java / AppDataHelper.java / DexOptHelper.java
frameworks/base/core/java/com/android/internal/pm/parsing/PackageParser2.java
frameworks/base/core/java/com/android/internal/pm/pkg/parsing/ParsingPackageUtils.java
frameworks/base/services/core/java/com/android/server/pm/permission/PermissionManagerService.java
frameworks/base/services/permission/java/com/android/server/permission/access/permission/PermissionService.kt
art/libartservice/service/java/com/android/server/art/ArtManagerLocal.java
```

`PackageParser.java` 不在 pm 服务目录，`PermissionManagerService` 也不是 pm 根目录文件；ART Service 主导 dexopt，不能用历史 PackageDexOptimizer 作为现代主入口。源码：[PackageParser2.java:55](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/pm/parsing/PackageParser2.java#55)；[PermissionService.kt:118](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/permission/java/com/android/server/permission/access/permission/PermissionService.kt#118)。

### 14.2 客户端源码

```text
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

## 总结

本文详细讲解了 Android PMS (PackageManagerService) 的核心知识点，包括：

1. **PMS 架构** - 包管理核心服务
2. **APK 安装** - 完整安装流程
3. **组件解析** - AndroidManifest.xml 解析
4. **权限管理** - 运行时权限机制
5. **签名验证** - APK 签名方案
6. **dex2oat** - 编译优化
7. **应用更新** - 更新流程与热更新
8. **多用户支持** - 用户隔离机制
9. **Instant App** - 免安装体验
10. **备份恢复** - Backup 机制

掌握这些知识点对于 Android 面试和应用开发都至关重要。

---

*文档更新时间: 2026-09-10*
