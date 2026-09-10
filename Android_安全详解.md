# Android 安全详解

> 作者：OpenClaw | 日期：2026-03-11  
> 应用安全防护完全指南 | 混淆、加固、加密、防护
> 平台分析基线：AOSP `android-17.0.0_r1`。第三方库/加固工具不是 AOSP API，版本和产品能力单独核验。

---

## 📚 目录

- [第一篇：Android 安全基础](#第一篇android-安全基础)
- [第 1 章 安全概述](#第-1-章-安全概述)
  - [1.1 Android 安全模型](#11-android-安全模型)
  - [1.2 安全威胁分析](#12-安全威胁分析)
  - [1.3 安全防护层次](#13-安全防护层次)
  - [1.4 安全开发原则](#14-安全开发原则)
- [第 2 章 应用签名](#第-2-章-应用签名)
  - [2.1 签名机制原理](#21-签名机制原理)
  - [2.2 调试签名与发布签名](#22-调试签名与发布签名)
  - [2.3 APK Signature Scheme](#23-apk-signature-scheme)
  - [2.4 多渠道打包](#24-多渠道打包)
  - [2.5 签名校验](#25-签名校验)
- [第 3 章 混淆详解](#第-3-章-混淆详解)
  - [3.1 混淆原理](#31-混淆原理)
  - [3.2 ProGuard 配置](#32-proguard-配置)
  - [3.3 R8 优化器](#33-r8-优化器)
  - [3.4 混淆规则详解](#34-混淆规则详解)
  - [3.5 常见混淆问题](#35-常见混淆问题)
- [第 4 章 加固技术](#第-4-章-加固技术)
  - [4.1 加固原理](#41-加固原理)
  - [4.2 DEX 加固](#42-dex-加固)
  - [4.3 SO 加固](#43-so-加固)
  - [4.4 资源保护](#44-资源保护)
  - [4.5 反调试技术](#45-反调试技术)
- [第 5 章 反编译与防护](#第-5-章-反编译与防护)
  - [5.1 反编译工具链](#51-反编译工具链)
  - [5.2 逆向分析流程](#52-逆向分析流程)
  - [5.3 代码防护策略](#53-代码防护策略)
  - [5.4 资源防护策略](#54-资源防护策略)
- [第二篇：数据安全](#第二篇数据安全)
- [第 6 章 数据加密](#第-6-章-数据加密)
  - [6.1 加密算法基础](#61-加密算法基础)
  - [6.2 对称加密（AES）](#62-对称加密aes)
  - [6.3 非对称加密（RSA）](#63-非对称加密rsa)
  - [6.4 哈希算法（SHA/MD5）](#64-哈希算法shamd5)
  - [6.5 Android Keystore](#65-android-keystore)
  - [6.6 Keystore 密钥的实际生命周期](#66-keystore-密钥的实际生命周期)
- [第 7 章 数据存储安全](#第-7-章-数据存储安全)
  - [7.1 SharedPreferences 安全](#71-sharedpreferences-安全)
  - [7.2 文件存储安全](#72-文件存储安全)
  - [7.3 数据库安全](#73-数据库安全)
  - [7.4 MMKV 加密存储](#74-mmkv-加密存储)
- [第 8 章 网络安全](#第-8-章-网络安全)
  - [8.1 HTTPS 原理](#81-https-原理)
  - [8.2 证书校验](#82-证书校验)
  - [8.3 证书绑定（SSL Pinning）](#83-证书绑定ssl-pinning)
  - [8.4 网络安全配置](#84-网络安全配置)
  - [8.5 抓包防护](#85-抓包防护)
- [第 9 章 四大组件安全](#第-9-章-四大组件安全)
  - [9.1 Activity 安全](#91-activity-安全)
  - [9.2 Service 安全](#92-service-安全)
  - [9.3 BroadcastReceiver 安全](#93-broadcastreceiver-安全)
  - [9.4 ContentProvider 安全](#94-contentprovider-安全)
- [第 10 章 WebView 安全](#第-10-章-webview-安全)
  - [10.1 WebView 漏洞](#101-webview-漏洞)
  - [10.2 JavaScript 接口安全](#102-javascript-接口安全)
  - [10.3 文件访问安全](#103-文件访问安全)
  - [10.4 WebView 最佳实践](#104-webview-最佳实践)
- [第 11 章 Intent 安全](#第-11-章-intent-安全)
  - [11.1 Intent 注入攻击](#111-intent-注入攻击)
  - [11.2 隐式 Intent 风险](#112-隐式-intent-风险)
  - [11.3 PendingIntent 安全](#113-pendingintent-安全)
  - [11.4 Deep Link 安全](#114-deep-link-安全)
- [第三篇：进阶防护](#第三篇进阶防护)
- [第 12 章 SO 安全](#第-12-章-so-安全)
  - [12.1 NDK 安全基础](#121-ndk-安全基础)
  - [12.2 SO 混淆](#122-so-混淆)
  - [12.3 反调试技术](#123-反调试技术)
  - [12.4 完整性校验](#124-完整性校验)
- [第 13 章 运行时防护](#第-13-章-运行时防护)
  - [13.1 Root 检测](#131-root-检测)
  - [13.2 模拟器检测](#132-模拟器检测)
  - [13.3 Hook 检测](#133-hook-检测)
  - [13.4 注入检测](#134-注入检测)
- [第 14 章 主流加固方案](#第-14-章-主流加固方案)
  - [14.1 360加固保](#141-360加固保)
  - [14.2 腾讯乐固](#142-腾讯乐固)
  - [14.3 阿里聚安全](#143-阿里聚安全)
  - [14.4 梆梆加固](#144-梆梆加固)
  - [14.5 方案对比](#145-方案对比)
- [第 15 章 安全最佳实践](#第-15-章-安全最佳实践)
  - [15.1 安全开发规范](#151-安全开发规范)
  - [15.2 安全测试清单](#152-安全测试清单)
  - [15.3 安全审计工具](#153-安全审计工具)
  - [15.4 漏洞修复流程](#154-漏洞修复流程)
- [第 18 章 面试常见问题](#第-18-章-面试常见问题)
  - [18.1 混淆原理](#181-混淆原理)
  - [18.2 加固技术](#182-加固技术)
  - [18.3 加密算法](#183-加密算法)
  - [18.4 网络安全](#184-网络安全)
  - [18.5 组件安全](#185-组件安全)
- [总结](#总结)
  - [Android 安全核心要点](#android-安全核心要点)
  - [安全防护层次](#安全防护层次)
  - [面试重点](#面试重点)

---

## 第一篇：Android 安全基础

---

## 第 1 章 安全概述

### 1.1 Android 安全模型

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Android 安全架构                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          应用层安全                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  混淆加固   │  │  数据加密   │  │  网络安全   │  │  组件防护   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          框架层安全                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  权限控制   │  │  沙箱隔离   │  │  签名校验   │  │  UID/GID    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          内核层安全                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  SELinux    │  │  进程隔离   │  │  文件权限   │  │  内核防护   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Android 安全模型核心要素**：

1. **应用沙箱**：每个应用运行在独立进程中，有独立 UID
2. **权限系统**：敏感操作需要用户授权
3. **代码签名**：所有 APK 必须签名才能安装
4. **SELinux**：强制访问控制，限制进程权限

### 1.2 安全威胁分析

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Android 应用安全威胁                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────┐
│     威胁类型      │     攻击方式     │     风险等级     │
├──────────────────┼──────────────────┼──────────────────┤
│  反编译          │  apktool/jadx    │   ⭐⭐⭐⭐⭐      │
│  代码注入        │  Xposed/Frida    │   ⭐⭐⭐⭐⭐      │
│  中间人攻击      │  Charles/Fiddler │   ⭐⭐⭐⭐        │
│  数据泄露        │  root 设备提取   │   ⭐⭐⭐⭐        │
│  组件暴露        │  Intent 劫持     │   ⭐⭐⭐         │
│  WebView 攻击    │  JS 注入         │   ⭐⭐⭐         │
│  重打包          │  修改后重新签名  │   ⭐⭐⭐⭐⭐      │
│  内存dump        │  运行时提取      │   ⭐⭐⭐⭐        │
└──────────────────┴──────────────────┴──────────────────┘
```

### 1.3 安全防护层次

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       安全防护层次                                          │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────────┐
                    │        第一层：代码保护       │
                    │   混淆 + 加固 + 反调试        │
                    └──────────────────────────────┘
                                  ▼
                    ┌──────────────────────────────┐
                    │        第二层：数据保护       │
                    │   加密存储 + 安全传输         │
                    └──────────────────────────────┘
                                  ▼
                    ┌──────────────────────────────┐
                    │        第三层：通信保护       │
                    │   HTTPS + 证书绑定           │
                    └──────────────────────────────┘
                                  ▼
                    ┌──────────────────────────────┐
                    │        第四层：运行时保护     │
                    │   Root检测 + Hook检测        │
                    └──────────────────────────────┘
                                  ▼
                    ┌──────────────────────────────┐
                    │        第五层：完整性校验     │
                    │   签名校验 + 完整性检查       │
                    └──────────────────────────────┘
```

### 1.4 安全开发原则

```kotlin
/**
 * 安全开发原则
 */

// 1. 最小权限原则
// ❌ 错误：申请不必要的权限
<uses-permission android:name="android.permission.READ_CONTACTS" />
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />

// ✅ 正确：只申请必要的权限
<uses-permission android:name="android.permission.INTERNET" />

// 2. 深度防御原则
// 多层防护，单点失效不影响整体
fun secureOperation() {
    if (!checkSignature()) return      // 签名校验
    if (!checkRoot()) return           // Root检测
    if (!checkDebug()) return          // 调试检测
    // 执行安全操作
}

// 3. 数据最小化原则
// ❌ 错误：存储敏感数据
sharedPreferences.edit().putString("password", password).apply()

// ✅ 正确：不存储敏感数据，或加密存储
val encrypted = encrypt(password)
secureStorage.save("credential", encrypted)

// 4. 安全默认原则
// ❌ 错误：默认导出组件
<activity android:name=".SecretActivity" android:exported="true" />

// ✅ 正确：默认不导出
<activity android:name=".SecretActivity" android:exported="false" />
```

---

## 第 2 章 应用签名

### 2.1 签名机制原理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       APK 签名原理                                          │
└─────────────────────────────────────────────────────────────────────────────┘

签名过程：
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   APK 文件   │───▶│  计算摘要    │───▶│  私钥签名    │
│              │    │  (SHA-256)   │    │  (RSA/ECDSA) │
└──────────────┘    └──────────────┘    └──────────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │  签名文件    │
                                        │  (.SF/.RSA)  │
                                        └──────────────┘

验证过程：
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   APK 文件   │───▶│  计算摘要    │    │  公钥验签    │
│              │    │  (SHA-256)   │    │  签名文件    │
└──────────────┘    └──────────────┘    └──────────────┘
                           │                   │
                           └─────────┬─────────┘
                                     ▼
                            ┌──────────────┐
                            │  比较摘要    │
                            │  验证完整性  │
                            └──────────────┘
```

### 2.2 调试签名与发布签名

```kotlin
/**
 * 调试签名 vs 发布签名
 */

// 调试签名（debug keystore）
// 位置：~/.android/debug.keystore
// 密码：android
// 别名：androiddebugkey
// 新建默认 debug 证书有效期通常为 30 年；已有文件用 keytool -list -v 核验

// 发布签名（release keystore）
// 需要自行创建
keytool -genkey -v -keystore release.keystore \
    -alias myapp \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000

// build.gradle 配置
android {
    signingConfigs {
        debug {
            storeFile file("debug.keystore")
            storePassword "android"
            keyAlias "androiddebugkey"
            keyPassword "android"
        }
        release {
            storeFile file("release.keystore")
            storePassword System.getenv("RELEASE_STORE_PASSWORD")
            keyAlias "myapp"
            keyPassword System.getenv("RELEASE_KEY_PASSWORD")
        }
    }
    
    buildTypes {
        debug {
            signingConfig signingConfigs.debug
        }
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

### 2.3 APK Signature Scheme

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       APK 签名方案                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────────┬──────────────────────────────────────────┐
│    方案      │    Android版本   │                   特点                   │
├──────────────┼──────────────────┼──────────────────────────────────────────┤
│  v1 (JAR)    │   Android 1.0+   │  校验签名条目；不覆盖整个 ZIP 结构                 │
│  v2          │   Android 7.0+   │  全文件签名，更安全                     │
│  v3          │   Android 9.0+   │  支持密钥轮替                           │
│  v4          │   Android 11+    │  独立 .idsig 支持增量安装，仍需要 v2/v3                           │
└──────────────┴──────────────────┴──────────────────────────────────────────┘

// build.gradle 配置
android {
    defaultConfig {
        // 推荐同时启用 v1、v2、v3
        signingConfig signingConfigs.release
    }
}
```

### 2.4 多渠道打包

```kotlin
/**
 * 多渠道打包
 */

// 1. 使用 productFlavors
android {
    flavorDimensions "channel"
    productFlavors {
        xiaomi { dimension "channel" }
        huawei { dimension "channel" }
        oppo { dimension "channel" }
        vivo { dimension "channel" }
    }
}

// 2. 使用美团 Walle（推荐）
// 添加依赖
plugins {
    id("com.meituan.android.walle") version "1.1.6"
}

walle {
    // 渠道配置文件
    channelFile = file("channel.txt")
    // 自定义渠道信息
    apkOutputFolder = file("build/apk/")
}

// 3. 读取渠道信息
val channel = WalleChannelReader.getChannel(context)

// 4. 美团 AndroidManifest 方案
// <meta-data android:name="CHANNEL" android:value="${CHANNEL_VALUE}" />
android {
    productFlavors {
        xiaomi { manifestPlaceholders = [CHANNEL_VALUE: "xiaomi"] }
    }
}
```

### 2.5 签名校验

```kotlin
// API 28+：接受可信签名及平台验证过的轮换历史；不是多签名者“精确集合”策略。
fun verifySignature(context: Context, expectedSha256: String): Boolean {
    require(expectedSha256.matches(Regex("[0-9a-fA-F]{64}")))
    val digest = expectedSha256.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
    return context.packageManager.hasSigningCertificate(
        context.packageName, digest, PackageManager.CERT_INPUT_SHA256
    )
}
// expectedSha256应替换为发布证书的完整SHA256指纹；不使用abc123等伪指纹。
// 多签名APK若要求签名者集合完全匹配，应读取GET_SIGNING_CERTIFICATES并比较
// SigningInfo.apkContentsSigners全体，而不是firstOrNull；轮换策略应单独定义。

```

---

## 第 3 章 混淆详解

### 3.1 混淆原理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       代码混淆原理                                          │
└─────────────────────────────────────────────────────────────────────────────┘

混淆前：
┌─────────────────────────────────────────────────────────────────────────────┐
│  public class UserManager {                                                 │
│      private String userName;                                               │
│      private String userPassword;                                           │
│                                                                             │
│      public void login(String name, String password) {                     │
│          // 登录逻辑                                                        │
│      }                                                                      │
│                                                                             │
│      public void updateUserInfo(String info) {                              │
│          // 更新逻辑                                                        │
│      }                                                                      │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▼
混淆后：
┌─────────────────────────────────────────────────────────────────────────────┐
│  public class a {                                                           │
│      private String a;                                                      │
│      private String b;                                                      │
│                                                                             │
│      public void a(String var1, String var2) {                              │
│          // 登录逻辑                                                        │
│      }                                                                      │
│                                                                             │
│      public void b(String var1) {                                           │
│          // 更新逻辑                                                        │
│      }                                                                      │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

混淆的作用：
1. 类名、方法名、字段名 → 短短的无意义名称
2. 删除未使用的代码（裁剪）
3. 优化字节码
4. 内联方法
5. 删除日志
```

### 3.2 ProGuard 配置

```groovy
/**
 * ProGuard 配置
 */

// build.gradle
android {
    buildTypes {
        release {
            // 启用混淆
            minifyEnabled true
            // 启用资源压缩
            shrinkResources true
            // 混淆配置文件
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'),
                         'proguard-rules.pro'
        }
    }
}
```

```pro
# proguard-rules.pro

# ========================================
# 基本配置
# ========================================

# 优化次数
-optimizationpasses 5

# 不跳过非公共的库类
-dontskipnonpubliclibraryclasses

# 混淆时不使用大小写混合类名
-dontusemixedcaseclassnames

# 不全局忽略警告；仅对明确可选且不会执行的依赖添加精确 -dontwarn 规则

# 优化时允许访问并修改有修饰符的类和类的成员
-allowaccessmodification

# 预校验
-dontpreverify

# 保留行号（调试用）
-keepattributes SourceFile,LineNumberTable

# 保留注解
-keepattributes *Annotation*

# 保留泛型
-keepattributes Signature

# 保留异常
-keepattributes Exceptions

# ========================================
# 保留 Android 基本组件
# ========================================

# 保留四大组件
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Service
-keep public class * extends android.content.BroadcastReceiver
-keep public class * extends android.content.ContentProvider
-keep public class * extends android.app.Fragment
-keep public class * extends androidx.fragment.app.Fragment

# 保留 Application
-keep public class * extends android.app.Application

# 保留 View
-keep public class * extends android.view.View

# 保留自定义 View 的构造函数
-keepclasseswithmembers class * {
    public <init>(android.content.Context, android.util.AttributeSet);
}

-keepclasseswithmembers class * {
    public <init>(android.content.Context, android.util.AttributeSet, int);
}

# 保留 Parcelable
-keep class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}

# 保留 Serializable
-keepclassmembers class * implements java.io.Serializable {
    static final long serialVersionUID;
    private static final java.io.ObjectStreamField[] serialPersistentFields;
    !static !transient <fields>;
    private void writeObject(java.io.ObjectOutputStream);
    private void readObject(java.io.ObjectInputStream);
    java.lang.Object writeReplace();
    java.lang.Object readResolve();
}

# ========================================
# 保留 Native 方法
# ========================================

-keepclasseswithmembernames class * {
    native <methods>;
}

# ========================================
# 保留枚举
# ========================================

-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# ========================================
# WebView
# ========================================

-keepclassmembers class * extends android.webkit.WebViewClient {
    public void *(android.webkit.WebView, java.lang.String, android.graphics.Bitmap);
    public boolean *(android.webkit.WebView, java.lang.String);
}

-keepclassmembers class * extends android.webkit.WebChromeClient {
    public void *(android.webkit.WebView, java.lang.String);
}

# ========================================
# 第三方库
# ========================================

# OkHttp
-dontwarn okhttp3.**
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }

# Retrofit
-dontwarn retrofit2.**
-keep class retrofit2.** { *; }
-keepclasseswithmembers class * {
    @retrofit2.http.* <methods>;
}

# Gson
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.google.gson.** { *; }
-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer

# Glide
-keep public class * implements com.bumptech.glide.module.GlideModule
-keep class * extends com.bumptech.glide.module.AppGlideModule {
 <init>(...);
}
-keep public enum com.bumptech.glide.load.ImageHeaderParser$** {
  **[] $VALUES;
  public *;
}
-keep class com.bumptech.glide.load.data.ParcelFileDescriptorRewinder$InternalRewinder {
  *** rewind();
}

# RxJava
-dontwarn sun.misc.**
-keepclassmembers class rx.internal.util.unsafe.*ArrayQueue*Field* {
   long producerIndex;
   long consumerIndex;
}
-keepclassmembers class rx.internal.util.unsafe.BaseLinkedQueueProducer {
   volatile rx.internal.util.atomic.LinkedQueueNode producerNode;
   volatile rx.internal.util.atomic.LinkedQueueNode consumerNode;
}

# Room
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class * { *; }
-dontwarn androidx.room.paging.**

# ========================================
# 删除日志
# ========================================

-assumenosideeffects class android.util.Log {
    public static boolean isLoggable(java.lang.String, int);
    public static int v(...);
    public static int i(...);
    public static int w(...);
    public static int d(...);
}
```

### 3.3 R8 优化器

```kotlin
/**
 * R8 vs ProGuard
 */

// R8 是 ProGuard 的替代品，更强大
// Android Gradle Plugin 3.4.0+ 默认使用 R8

// build.gradle 配置
android {
    buildTypes {
        release {
            // R8 配置
            minifyEnabled true
            shrinkResources true
            
            // R8 完整模式（推荐）
            // 使用完整的 R8 而不是兼容模式
            // 在 gradle.properties 中设置
            // android.enableR8.fullMode=true
        }
    }
}

// gradle.properties
android.enableR8=true
android.enableR8.fullMode=true
```

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       R8 vs ProGuard 对比                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────┐
│       特性        │    ProGuard     │       R8         │
├──────────────────┼──────────────────┼──────────────────┤
│  代码混淆        │       ✅         │       ✅         │
│  代码优化        │       ✅         │       ✅✅       │
│  资源压缩        │       ❌         │       ✅         │
│  编译速度        │       ⭐⭐⭐      │      ⭐⭐⭐⭐⭐   │
│  输出体积        │       ⭐⭐⭐⭐     │      ⭐⭐⭐⭐⭐   │
│  Kotlin 支持     │       ⭐⭐⭐      │      ⭐⭐⭐⭐⭐   │
│  兼容性          │       ✅         │    ProGuard 语法 │
└──────────────────┴──────────────────┴──────────────────┘
```

### 3.4 混淆规则详解

```pro
# ========================================
# -keep 保留规则详解
# ========================================

# 1. 保留类（不混淆类名）
-keep class com.example.MyClass

# 2. 保留类及其成员
-keep class com.example.MyClass { *; }

# 3. 保留类及其特定成员
-keep class com.example.MyClass {
    public <methods>;
    public <fields>;
}

# 4. 保留类及其构造函数
-keep class com.example.MyClass {
    public <init>(...);
}

# 5. 条件保留（如果类被保留，则保留其成员）
-keepclassmembers class com.example.MyClass {
    public void onClick(...);
}

# 6. 条件保留（如果成员存在，则保留整个类）
-keepclasseswithmembers class * {
    public <init>(android.content.Context, android.util.AttributeSet);
}

# ========================================
# 通配符
# ========================================

# * 匹配任意字符，不包括包分隔符
-keep class com.example.*

# ** 匹配任意字符，包括包分隔符
-keep class com.example.**

# *** 匹配任意类型
-keep class * {
    *** ***(...);
}

# <init> 匹配构造函数
# <fields> 匹配所有字段
# <methods> 匹配所有方法

# ========================================
# 常用规则模板
# ========================================

# 保留所有 public API
-keep public class * {
    public protected *;
}

# 保留所有实现了某接口的类
-keep class * implements com.example.MyInterface { *; }

# 保留所有被某注解标注的类
-keep @com.example.Keep class * { *; }

# 保留所有被某注解标注的成员
-keepclassmembers class * {
    @com.example.Keep *;
}
```

### 3.5 常见混淆问题

```kotlin
/**
 * 常见混淆问题及解决方案
 */

// 问题1：ClassNotFoundException
// 原因：使用反射的类被混淆
// 解决：保留反射使用的类
// -keep class com.example.ReflectClass { *; }

// 问题2：NoSuchMethodException
// 原因：反射调用的方法被混淆
// 解决：保留方法名
// -keepclassmembers class com.example.MyClass {
//     public void myMethod(...);
// }

// 问题3：JSON 解析失败
// 原因：实体类字段被混淆
// 解决：保留实体类
// -keep class com.example.bean.** { *; }

// 问题4：序列化/反序列化失败
// 原因：Parcelable/Serializable 类被混淆
// 解决：保留序列化类
// -keep class * implements android.os.Parcelable { *; }
// -keep class * implements java.io.Serializable { *; }

// 问题5：WebView JS 调用失败
// 原因：@JavascriptInterface 方法被混淆
// 解决：保留 JS 接口
// -keepclassmembers class * {
//     @android.webkit.JavascriptInterface <methods>;
// }

// 问题6：自定义 View 无法实例化
// 原因：构造函数被混淆
// 解决：保留自定义 View
// -keep public class * extends android.view.View {
//     public <init>(android.content.Context);
//     public <init>(android.content.Context, android.util.AttributeSet);
//     public <init>(android.content.Context, android.util.AttributeSet, int);
// }

// 问题7：EventBus/RxBus 失效
// 原因：订阅方法被混淆
// 解决：保留订阅方法
// -keepclassmembers class * {
//     @org.greenrobot.eventbus.Subscribe <methods>;
// }

// 问题8：DataBinding 失效
// 原因：生成的绑定类被混淆
// 解决：保留 DataBinding 类
// -keep class * extends androidx.databinding.DataBinderProxy { *; }
```

---

## 第 4 章 加固技术

### 4.1 加固原理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       APK 加固原理                                          │
└─────────────────────────────────────────────────────────────────────────────┘

原始 APK 结构：
┌──────────────────────────────┐
│         AndroidManifest.xml  │
│         classes.dex          │
│         resources.arsc       │
│         res/                 │
│         lib/                 │
│         META-INF/            │
└──────────────────────────────┘
                │
                ▼ 加固处理
┌──────────────────────────────┐
│         AndroidManifest.xml  │
│         classes.dex (壳)     │◀── 壳代码，负责解密原始DEX
│         assets/classes.dex   │◀── 加密的原始DEX
│         resources.arsc       │
│         res/                 │
│         lib/                 │
│         META-INF/            │
└──────────────────────────────┘

加固流程：
1. 加密原始 DEX 文件
2. 注入壳代码
3. 修改入口点
4. 运行时解密加载
```

### 4.2 DEX 加固

壳方案包含解密、完整性验证和动态加载，但反射 `DexPathList` 替换全应用 ClassLoader 不是公开 SDK，也不能用空函数冒充 Android17 完整实现。下面保留“解密后加载”的核心步骤，使用公开 `InMemoryDexClassLoader`（API26+）；应用接口由父加载器提供，插件实现显式加载，不声称替换系统创建 Activity/Application 的加载路径。

```kotlin
interface SecurePlugin { fun execute(context: Context) }

fun loadVerifiedPlugin(verifiedDex: ByteArray, parent: ClassLoader): SecurePlugin {
    // 调用前必须完成可信签名验证/认证解密；只处理应用控制且大小受限的DEX。
    // 此入口不能接收未认证的网络数据；加密本身不等于来源可信。
    require(verifiedDex.isNotEmpty())
    val loader = dalvik.system.InMemoryDexClassLoader(
        java.nio.ByteBuffer.wrap(verifiedDex).asReadOnlyBuffer(), parent
    )
    val entry = loader.loadClass("com.example.plugin.Entry")
        .asSubclass(SecurePlugin::class.java)
    return entry.getDeclaredConstructor().newInstance()
}
```

真实壳还需解决多DEX、资源/Native库、组件实例化及Android版本兼容。若使用文件型 `DexClassLoader`，target34+动态代码文件必须只读：打开输出流后、写入内容之前设置只读以缩小竞态；不要先写完可写DEX再尝试加载。内存加载避免该文件落盘步骤，不是绕过信任验证/应用商店动态代码政策。硬编码解密key不能提供不可提取的秘密。

### 4.3 SO 加固

```cpp
/**
 * SO 文件加固
 */

// 1. 字符串加密
// 原始字符串
const char* API_KEY = "your_api_key_here";

// 加密后
const char* API_KEY_ENCRYPTED = "\x12\x34\x56\x78...";
const char* getApiKey() {
    static char decrypted[64];
    if (decrypted[0] == 0) {
        decrypt_string(API_KEY_ENCRYPTED, decrypted, sizeof(decrypted));
    }
    return decrypted;
}

// 2. 函数名混淆（使用 LLVM Obfuscator）
// 编译时添加混淆选项
// -mllvm -fla  // 控制流平坦化
// -mllvm -sub  // 指令替换
// -mllvm -bcf  // 虚假控制流

// 3. 反调试
#include <sys/ptrace.h>

void anti_debug() {
    // 检测是否被调试
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) {
        exit(1);  // 已被调试，退出
    }
}

// 4. 完整性校验
int check_integrity() {
    // 读取 SO 文件并计算哈希
    // 与预期值比较
    return 0;
}
```

### 4.4 资源保护

```kotlin
/**
 * 资源保护策略
 */

// 1. 资源混淆（AndResGuard）
// build.gradle
plugins {
    id("com.andresguard") version "1.2.23"
}

andResGuard {
    whiteList = [
        "R.mipmap.ic_launcher",
        "R.string.app_name"
    ]
    use7zip = true
}

// 2. 敏感资源加密存储
object ResourceProtector {
    
    fun getEncryptedString(context: Context, resId: Int): String {
        val encrypted = context.getString(resId)
        return decrypt(encrypted)
    }
    
    private fun decrypt(data: String): String {
        // AES 解密
        val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
        // ... 解密逻辑
        return String(decryptedBytes)
    }
}

// 3. 动态加载资源
fun loadAsset(name: String): ByteArray {
    return context.assets.open(name).readBytes()
}
```

### 4.5 反调试技术

```kotlin
/**
 * 反调试技术
 */

object AntiDebug {
    
    /**
     * 检测调试器
     */
    fun isDebugged(): Boolean {
        // 1. 检查 Debug 状态
        if (BuildConfig.DEBUG) return false
        
        // 2. 检查是否被调试
        if (Debug.isDebuggerConnected()) return true
        
        // 3. 检查调试端口
        if (isPortListening(8700)) return true  // DDMS
        if (isPortListening(5005)) return true  // JDWP
        
        // 4. 检查 ptrace
        if (checkPtrace()) return true
        
        return false
    }
    
    private fun isPortListening(port: Int): Boolean {
        return try {
            val socket = java.net.Socket("127.0.0.1", port)
            socket.close()
            true
        } catch (e: Exception) {
            false
        }
    }
    
    private fun checkPtrace(): Boolean {
        return try {
            val file = File("/proc/self/status")
            val content = file.readText()
            val tracerPid = content.lines()
                .find { it.startsWith("TracerPid:") }
                ?.split(":")?.get(1)?.trim()?.toInt() ?: 0
            tracerPid != 0
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * 检测 Hook 框架
     */
    fun checkHook(): Boolean {
        val suspiciousPackages = listOf(
            "de.robv.android.xposed.installer",
            "com.saurik.substrate",
            "com.topjohnwu.magisk"
        )
        
        return suspiciousPackages.any { pkg ->
            try {
                context.packageManager.getPackageInfo(pkg, 0)
                true
            } catch (e: Exception) {
                false
            }
        }
    }
}
```

---

## 第 5 章 反编译与防护

### 5.1 反编译工具链

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Android 反编译工具                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────────────────┐
│     工具         │                      功能                               │
├──────────────────┼──────────────────────────────────────────────────────────┤
│  apktool         │  反编译资源文件、smali 代码                             │
│  jadx            │  DEX 转 Java 源码                                       │
│  dex2jar         │  DEX 转 JAR                                             │
│  jd-gui          │  查看 JAR 源码                                          │
│  Frida           │  运行时 Hook                                            │
│  Xposed          │  系统级 Hook 框架                                       │
│  IDA Pro         │  SO 文件分析                                            │
│  Ghidra          │  SO 文件分析（免费）                                    │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

```bash
# 反编译流程

# 1. 解压 APK
unzip app.apk -d app_unzip/

# 2. 使用 apktool 反编译
apktool d app.apk -o app_smali/

# 3. 使用 jadx 反编译为 Java
jadx app.apk -d app_java/

# 4. 使用 dex2jar
d2j-dex2jar.sh app.apk

# 5. 分析 SO 文件
# 使用 IDA Pro 或 Ghidra
```

### 5.2 逆向分析流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       逆向分析流程                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   获取 APK   │───▶│   解压分析   │───▶│  静态分析   │───▶│  动态分析   │
│              │    │              │    │              │    │              │
│ - 应用商店  │    │ - 资源文件  │    │ - Java 代码 │    │ - Hook      │
│ - 自己提取  │    │ - DEX 文件  │    │ - Smali     │    │ - 调试      │
│              │    │ - SO 文件   │    │ - SO 分析   │    │ - 抓包      │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### 5.3 代码防护策略

```kotlin
/**
 * 代码防护策略
 */

// 1. 关键代码放 SO
// Java/Kotlin 代码容易被反编译，SO 更难分析
// 将核心算法、加密逻辑放在 native 层

// 2. 代码混淆
// 使用 ProGuard/R8 混淆代码

// 3. 字符串加密
object StringEncryptor {
    private const val KEY = "your_secret_key"
    
    fun encrypt(input: String): String {
        // XOR 加密（简单示例）
        return input.map { (it.code xor KEY.hashCode()).toChar() }.joinToString("")
    }
    
    fun decrypt(encrypted: String): String {
        return encrypt(encrypted)  // XOR 是对称的
    }
}

// 使用
val apiKey = StringEncryptor.decrypt("\u1234\u5678...")

// 4. 反射调用
// 通过反射调用敏感方法，增加分析难度
class SecureCaller {
    private fun callSecretMethod() {
        val clazz = Class.forName("com.example.SecureClass")
        val method = clazz.getDeclaredMethod("secretMethod")
        method.invoke(null)
    }
}

// 5. 代码完整性校验
object IntegrityChecker {
    fun checkDexIntegrity(context: Context): Boolean {
        val expectedHash = "abc123..."  // 预期的 DEX 哈希
        val actualHash = calculateDexHash(context)
        return actualHash == expectedHash
    }
    
    private fun calculateDexHash(context: Context): String {
        val dexFile = File(context.applicationInfo.sourceDir)
        val bytes = dexFile.readBytes()
        val digest = MessageDigest.getInstance("SHA-256").digest(bytes)
        return digest.joinToString("") { "%02x".format(it) }
    }
}
```

### 5.4 资源防护策略

```kotlin
/**
 * 资源防护策略
 */

// 1. 资源混淆
// 使用 AndResGuard 混淆资源名称

// 2. 敏感资源加密
// 将敏感资源加密存储，运行时解密

// 3. 资源完整性校验
object ResourceIntegrity {
    fun verifyResources(context: Context): Boolean {
        val expectedHashes = mapOf(
            "res/drawable/logo.png" to "abc123...",
            "assets/config.json" to "def456..."
        )
        
        return expectedHashes.all { (path, expectedHash) ->
            val actualHash = calculateResourceHash(context, path)
            actualHash == expectedHash
        }
    }
}
```

---

## 第二篇：数据安全

---

## 第 6 章 数据加密

### 6.1 加密算法基础

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       加密算法分类                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────────────────────────┐
│      类型        │       算法        │              特点                   │
├──────────────────┼──────────────────┼──────────────────────────────────────┤
│  对称加密        │  AES, DES, 3DES  │  加解密用同一密钥，速度快           │
│  非对称加密      │  RSA, ECC        │  公钥加密私钥解密，安全但慢         │
│  哈希算法        │  MD5, SHA-1/256  │  单向不可逆，用于校验               │
│  消息认证码      │  HMAC            │  带密钥的哈希，防篡改               │
└──────────────────┴──────────────────┴──────────────────────────────────────┘
```

### 6.2 对称加密（AES）

采用 AES-GCM 同时提供保密性与完整性。CBC 单独使用无法检测恶意修改，不能作为“安全存储”的完整方案；同一 GCM 密钥绝不能重用 nonce。不要把口令直接 SHA-256 后当 AES 密钥，弱口令仍容易离线枚举。

```kotlin
import android.util.Base64
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

data class EncryptedData(val version: Int, val iv: String, val data: String)

object AESUtil {
    private const val TRANSFORMATION = "AES/GCM/NoPadding"
    // 临时演示密钥；持久化数据改用下节 AndroidKeyStore，不能每次生成。
    fun generateKey(): SecretKey = KeyGenerator.getInstance("AES").apply {
        init(256)
    }.generateKey()

    fun encrypt(data: String, key: SecretKey, aad: ByteArray = byteArrayOf()): EncryptedData {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        // 由 provider 生成新 IV；不要给默认 randomizedEncryptionRequired 的 Keystore key 传自定义 IV。
        cipher.init(Cipher.ENCRYPT_MODE, key)
        cipher.updateAAD(aad)
        val ciphertextAndTag = cipher.doFinal(data.toByteArray(Charsets.UTF_8))
        return EncryptedData(1,
            Base64.encodeToString(cipher.iv, Base64.NO_WRAP),
            Base64.encodeToString(ciphertextAndTag, Base64.NO_WRAP))
    }

    fun decrypt(value: EncryptedData, key: SecretKey, aad: ByteArray = byteArrayOf()): String {
        require(value.version == 1) { "Unknown encrypted format" }
        val iv = Base64.decode(value.iv, Base64.NO_WRAP)
        val ciphertextAndTag = Base64.decode(value.data, Base64.NO_WRAP)
        require(iv.size == 12 && ciphertextAndTag.size >= 16) { "Invalid GCM envelope" }
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, iv))
        cipher.updateAAD(aad)
        // AEADBadTagException 必须传播；验证成功前不交付任何明文。
        return cipher.doFinal(ciphertextAndTag).toString(Charsets.UTF_8)
    }
}

val key = AESUtil.generateKey()
val aad = "demo:record:1".toByteArray(Charsets.UTF_8)
val encrypted = AESUtil.encrypt("敏感数据", key, aad)
val decrypted = AESUtil.decrypt(encrypted, key, aad)
```

IV 不必保密，必须与格式版本、密文及 tag 一起保存；AAD 可绑定账号/记录 ID，解密时必须完全一致。该 v1 与旧 CBC 数据不兼容，迁移应保留旧 alias/格式读取分支，成功原子写入新格式后再清理旧 key。确有用户口令派生需求时，使用带随机 salt、经设备测量工作因子的密码 KDF，而不是硬编码口令。

### 6.3 非对称加密（RSA）

示例明确使用 SHA-256 OAEP 主摘要、SHA-1 MGF1（Android Keystore 兼容参数）；两端必须一致。导入 `javax.crypto.spec.OAEPParameterSpec`、`javax.crypto.spec.PSource`、`java.security.spec.MGF1ParameterSpec`。2048 位 RSA 的 OAEP/SHA-256 明文最多 190 字节；只封装随机 AES key，大数据使用混合加密。`ECB` 是 JCA 变换名称占位，不表示 RSA 有 ECB 分组模式。签名使用独立 Signature API，不是“私钥加密”。

```kotlin
/**
 * RSA 加密工具
 */
object RSAUtil {
    
    private const val ALGORITHM = "RSA"
    private const val TRANSFORMATION = "RSA/ECB/OAEPWithSHA-256AndMGF1Padding"
    private const val KEY_SIZE = 2048
    
    /**
     * 生成密钥对
     */
    fun generateKeyPair(): KeyPair {
        val keyPairGenerator = KeyPairGenerator.getInstance(ALGORITHM)
        keyPairGenerator.initialize(KEY_SIZE)
        return keyPairGenerator.generateKeyPair()
    }
    
    /**
     * 公钥加密
     */
    fun encryptWithPublicKey(data: String, publicKey: PublicKey): String {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, publicKey,
            OAEPParameterSpec("SHA-256", "MGF1", MGF1ParameterSpec.SHA1, PSource.PSpecified.DEFAULT))
        val encrypted = cipher.doFinal(data.toByteArray(Charsets.UTF_8))
        return Base64.encodeToString(encrypted, Base64.DEFAULT)
    }
    
    /**
     * 私钥解密
     */
    fun decryptWithPrivateKey(encryptedData: String, privateKey: PrivateKey): String {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.DECRYPT_MODE, privateKey,
            OAEPParameterSpec("SHA-256", "MGF1", MGF1ParameterSpec.SHA1, PSource.PSpecified.DEFAULT))
        val encrypted = Base64.decode(encryptedData, Base64.DEFAULT)
        val decrypted = cipher.doFinal(encrypted)
        return String(decrypted, Charsets.UTF_8)
    }
    
    /**
     * 私钥签名
     */
    fun sign(data: String, privateKey: PrivateKey): String {
        val signature = Signature.getInstance("SHA256withRSA")
        signature.initSign(privateKey)
        signature.update(data.toByteArray(Charsets.UTF_8))
        return Base64.encodeToString(signature.sign(), Base64.DEFAULT)
    }
    
    /**
     * 公钥验签
     */
    fun verify(data: String, signatureStr: String, publicKey: PublicKey): Boolean {
        val signature = Signature.getInstance("SHA256withRSA")
        signature.initVerify(publicKey)
        signature.update(data.toByteArray(Charsets.UTF_8))
        val signatureBytes = Base64.decode(signatureStr, Base64.DEFAULT)
        return signature.verify(signatureBytes)
    }
}
```

### 6.4 哈希算法（SHA/MD5）

```kotlin
/**
 * 哈希工具
 */
object HashUtil {
    
    /**
     * SHA-256 哈希
     */
    fun sha256(input: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        val hash = digest.digest(input.toByteArray(Charsets.UTF_8))
        return hash.joinToString("") { "%02x".format(it) }
    }
    
    /**
     * MD5 哈希（不推荐用于安全场景）
     */
    fun md5(input: String): String {
        val digest = MessageDigest.getInstance("MD5")
        val hash = digest.digest(input.toByteArray(Charsets.UTF_8))
        return hash.joinToString("") { "%02x".format(it) }
    }
    
    /**
     * HMAC-SHA256
     */
    fun hmacSha256(input: String, key: String): String {
        val secretKey = SecretKeySpec(key.toByteArray(Charsets.UTF_8), "HmacSHA256")
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(secretKey)
        val hash = mac.doFinal(input.toByteArray(Charsets.UTF_8))
        return hash.joinToString("") { "%02x".format(it) }
    }
    
    /**
     * 文件哈希
     */
    fun fileHash(file: File, algorithm: String = "SHA-256"): String {
        val digest = MessageDigest.getInstance(algorithm)
        file.inputStream().use { fis ->
            val buffer = ByteArray(8192)
            var bytesRead: Int
            while (fis.read(buffer).also { bytesRead = it } != -1) {
                digest.update(buffer, 0, bytesRead)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }
}
```

### 6.5 Android Keystore

```kotlin
object KeystoreManager {
    private const val PROVIDER = "AndroidKeyStore"
    private const val ALIAS = "notes-gcm-v1" // 不复用旧 CBC alias

    fun existingKey(): SecretKey {
        val store = KeyStore.getInstance(PROVIDER).apply { load(null) }
        return store.getKey(ALIAS, null) as? SecretKey
            ?: throw IllegalStateException("Key missing; require recovery or sign-in")
    }

    @Synchronized // 仅保证本进程；多进程应用由一个持钥服务协调首次创建和轮换。
    fun getOrCreateKey(): SecretKey {
        val store = KeyStore.getInstance(PROVIDER).apply { load(null) }
        if (store.containsAlias(ALIAS)) return existingKey()
        return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, PROVIDER).apply {
            init(KeyGenParameterSpec.Builder(ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .setRandomizedEncryptionRequired(true)
                .setUserAuthenticationRequired(false)
                .build())
        }.generateKey()
    }

    fun encrypt(data: String, aad: ByteArray = byteArrayOf()): EncryptedData =
        AESUtil.encrypt(data, getOrCreateKey(), aad)

    fun decrypt(data: EncryptedData, aad: ByteArray = byteArrayOf()): String =
        AESUtil.decrypt(data, existingKey(), aad) // 解密绝不生成替代 key
}
```

应用拿到非导出的 SecretKey 句柄；是否硬件保护应查看 `KeyInfo.getSecurityLevel()`（API 31+）等属性，不能保证所有设备都在 TEE/StrongBox。上述不要求用户认证，不能称为生物识别保护。需要认证时设置 `setUserAuthenticationParameters(...)`，按 per-use/timed key 契约使用 BiometricPrompt；准备处理认证失败及 key 永久失效。

原始密码尽量不落盘，通常保存短期 token；使用 Gson 等显式序列化 `EncryptedData`，不是调用数据类不存在的 `toJson/fromJson`。卸载/清数据或跨设备恢复时 key 可能缺失，解密失败应要求恢复或重新登录，不能静默生成同名 key。排除不可恢复的加密文件/偏好设置备份，或设计服务器恢复方案。

源码：[AndroidKeyStoreKeyGeneratorSpi.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/keystore/java/android/security/keystore2/AndroidKeyStoreKeyGeneratorSpi.java) 的 `engineInit/engineGenerateKey`；[AndroidKeyStoreAuthenticatedAESCipherSpi.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/keystore/java/android/security/keystore2/AndroidKeyStoreAuthenticatedAESCipherSpi.java) 的 `GCM.initAlgorithmSpecificParameters`。密钥生命周期还见 6.6 节。

### 6.6 Keystore 密钥的实际生命周期

`KeyGenParameterSpec` 描述用途、GCM 模式、padding、nonce 随机化和认证要求；`AndroidKeyStoreKeyGeneratorSpi` 将它转换为 Keystore/KeyMint 参数。应用拿到的是 `SecretKey` 代理，密钥材料不应写入 SharedPreferences 或 APK。

```text
首次使用 -> alias notes-gcm-v1 -> generateKey
加密 -> provider 生成随机 IV -> 保存 format/version/IV/ciphertext+tag
读取 -> 按 version 取 alias -> AAD 与 tag 校验 -> 明文
轮换 -> v1 解密 -> 生成 v2 -> 原子写入 -> 全量成功后再清理 v1
丢 key -> 明确恢复/重新登录，不生成同名新 key 覆盖旧密文
```

AES-GCM 的认证失败必须报错；密钥轮换需可恢复、可重试，文件用 `AtomicFile` 或数据库事务避免半写。`setUserAuthenticationRequired(true)` 才建立用户认证约束，普通生成示例不能称为生物识别保护。卸载、清除数据、设备安全策略变化或跨设备恢复都可能使原 key 不可用。源码：`KeyGenParameterSpec.java`、`AndroidKeyStoreKeyGeneratorSpi.java`、`system/security/keystore2/src/security_level.rs`。


## 第 7 章 数据存储安全

### 7.1 SharedPreferences 安全

```kotlin
/**
 * SharedPreferences 安全使用
 */

// ❌ 错误：直接存储敏感数据
val prefs = context.getSharedPreferences("user", Context.MODE_PRIVATE)
prefs.edit().putString("password", "123456").apply()

// ✅ 正确：加密后存储
object SecurePreferences {
    
    private const val PREFS_NAME = "secure_prefs"
    // 密钥仅通过 KeystoreManager 获取
    
    fun init(context: Context) {
        // 初始化只准备存储，不提前生成 key；读取已有密文必须使用 existingKey()。
    }
    
    fun putString(context: Context, key: String, value: String) {
        val encrypted = KeystoreManager.encrypt(value, (PREFS_NAME + ":" + key).toByteArray(Charsets.UTF_8))
        val json = Gson().toJson(encrypted)
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit().putString(key, json).apply()
    }
    
    fun getString(context: Context, key: String): String? {
        val json = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getString(key, null) ?: return null
        val encrypted = Gson().fromJson(json, EncryptedData::class.java)
        return KeystoreManager.decrypt(encrypted, (PREFS_NAME + ":" + key).toByteArray(Charsets.UTF_8))
    }
}
```

### 7.2 文件存储安全

```kotlin
/**
 * 安全文件存储
 */
object SecureFileStorage {
    
    /**
     * 加密存储文件
     */
    fun saveEncryptedFile(context: Context, fileName: String, data: String) {
        val encrypted = KeystoreManager.encrypt(data, fileName.toByteArray(Charsets.UTF_8))
        
        // 存储到内部存储（私有）
        require(fileName.matches(Regex("[A-Za-z0-9_-]+\\.enc"))) { "Invalid file name" }
        val file = File(context.filesDir, fileName)
        file.writeText(Gson().toJson(encrypted))
    }
    
    /**
     * 读取加密文件
     */
    fun readEncryptedFile(context: Context, fileName: String): String? {
        require(fileName.matches(Regex("[A-Za-z0-9_-]+\\.enc"))) { "Invalid file name" }
        val file = File(context.filesDir, fileName)
        if (!file.exists()) return null
        
        val json = file.readText()
        val encrypted = Gson().fromJson(json, EncryptedData::class.java)
        return KeystoreManager.decrypt(encrypted, fileName.toByteArray(Charsets.UTF_8))
    }
    
    /** 删除逻辑文件，不保证闪存旧物理页被擦除。 */
    fun deleteFile(file: File): Boolean = !file.exists() || file.delete()
}
```

闪存磨损均衡、日志文件系统和备份使“覆盖写随机数据再 delete”不能保证安全擦除，而且一次分配 file.length() 大小数组会 OOM。高敏感数据从一开始加密，按独立密钥隔离后进行密钥销毁；共享密钥仍被其他数据使用时不能直接删 key。

### 7.3 数据库安全

```kotlin
/**
 * 数据库安全
 */

// 1. 使用 SQLCipher 加密数据库
// 添加依赖
// implementation "net.zetetic:android-database-sqlcipher:4.5.4"

object SecureDatabase {
    
    private const val DB_NAME = "secure.db"
    // 由首次建库时生成并经 Keystore 封装持久化的随机口令提供；不是 APK 常量。
    
    fun getDatabase(context: Context, passphrase: ByteArray): SQLiteDatabase {
        // passphrase 由调用者安全解封；这里只展示 SQLCipher 4.5.4 打开过程。
        return SQLiteDatabase.openOrCreateDatabase(
            File(context.filesDir, DB_NAME),
            passphrase,
            null
        )
    }
}

// 2. Room + SQLCipher
@Database(entities = [User::class], version = 1)
abstract class SecureAppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    
    companion object {
        fun create(context: Context, passphrase: ByteArray): SecureAppDatabase {
            val factory = SupportFactory(passphrase)
            
            return Room.databaseBuilder(context, SecureAppDatabase::class.java, "secure.db")
                .openHelperFactory(factory)
                .build()
        }
    }
}
```

### 7.4 MMKV 加密存储

```kotlin
/**
 * MMKV 加密存储
 */

// 初始化 MMKV
MMKV.initialize(context)

// 使用加密的 MMKV
val mmkv = MMKV.mmkvWithID("secure", MMKV.SINGLE_PROCESS_MODE, unwrappedMmkvKey)
// unwrappedMmkvKey 来自经 Keystore 封装的随机密钥（按 MMKV 版本限制长度），不是代码常量。
// MMKV cryptKey 需要可用原始字节/字符串；非导出的 Keystore AES key 不能直接充当 cryptKey。

// 存储
mmkv.encode("token", "user_token")
mmkv.encode("user_id", 12345)

// 读取
val token = mmkv.decodeString("token")
val userId = mmkv.decodeInt("user_id")
```

---

## 第 8 章 网络安全

### 8.1 HTTPS 原理

TLS 1.3 的完整证书握手（忽略可选客户端认证）如下；它不是 TLS 1.2 RSA 密钥交换，已没有 `ClientKeyExchange` 发送 RSA 加密预主密钥的步骤。

```text
Client                                    Server
ClientHello + key_share              ->
                                     <-  ServerHello + key_share
双方从 (EC)DHE 共享秘密及握手 transcript 经 HKDF 派生密钥
                                     <-  {EncryptedExtensions,
                                          Certificate, CertificateVerify, Finished}
验证证书链、hostname、签名与 Finished  ->
{Finished}                           ->
Application Data                    <->  Application Data
```

大括号内是握手密钥保护的消息；证书用于身份认证，(EC)DHE 用于协商共享秘密。会话恢复可使用 PSK；0-RTT early data 只适用于恢复且有重放风险，不可默认承载支付等非幂等写操作。来源：[RFC 8446 §2、§4.4、§8](https://www.rfc-editor.org/rfc/rfc8446)。

### 8.2 证书校验

默认使用平台 TrustManager 和 OkHttp 主机名校验；仅比较 `chain[0].encoded` 不能替代证书有效期、链约束及信任根验证。

```kotlin
object SecureHttpClients {
    fun createDefault(): OkHttpClient = OkHttpClient.Builder().build()

    // 自定义企业 CA 的方式；这改变信任根集合，不等于 Certificate Pinning。
    fun createWithEnterpriseCa(context: Context): OkHttpClient {
        val certificate = context.assets.open("enterprise-ca.crt").use {
            CertificateFactory.getInstance("X.509").generateCertificate(it)
        }
        val store = KeyStore.getInstance(KeyStore.getDefaultType()).apply {
            load(null, null)
            setCertificateEntry("enterprise-ca", certificate)
        }
        val factory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm())
        factory.init(store)
        val manager = factory.trustManagers.filterIsInstance<X509TrustManager>().single()
        val ssl = SSLContext.getInstance("TLS").apply { init(null, arrayOf(manager), null) }
        return OkHttpClient.Builder().sslSocketFactory(ssl.socketFactory, manager).build()
        // 不设置 permissive hostnameVerifier；这个 client 只用于受控企业端点。
    }
}
```

更推荐下面按域的 Network Security Configuration，避免自定义 client 对所有域都信任企业 CA。`checkClientTrusted` 也不能空实现后宣称双向认证安全。

AOSP `android-17.0.0_r1` 的真实路径是 **`external/conscrypt/nsc/src/android/security/net/config/RootTrustManager.java`**，包名仍是 `android.security.net.config`，不是旧 `frameworks/base` 路径，也不是 `com.android.org.conscrypt`。`checkServerTrusted(..., Socket/SSLEngine/hostname)` 从握手取得 host，调用 `ApplicationConfig.getConfigForHostname(host)`，再委托 `NetworkSecurityTrustManager` 完成链校验和配置 pin 检查。路径是固定版本源码证据，不是建议应用调用隐藏 API。见 [RootTrustManager.java](https://android.googlesource.com/platform/external/conscrypt/+/refs/tags/android-17.0.0_r1/nsc/src/android/security/net/config/RootTrustManager.java)。OkHttp 仍执行主机名验证；按域选择信任配置不等于自动替代所有客户端的主机名校验。

### 8.3 证书绑定（SSL Pinning）

Pin 是 SPKI 的 SHA-256 Base64，不能用示意值发布；必须预置备用公钥并演练轮换。它是在正常链验证之上的额外限制，Android 官方不建议将 pinning 作为所有应用默认要求，以免 CA/服务端轮换导致断网。抓取当前站点 pin 仅适合在已验证连接、可信环境中离线辅助核验，不能在每次请求时下载新 pin 自我授权。

```kotlin
/**
 * SSL Pinning 实现
 */
object SSLPinning {
    
    /**
     * 方式1：使用 CertificatePinner
     */
    fun createClientWithPinning(): OkHttpClient {
        return OkHttpClient.Builder()
            .certificatePinner(
                CertificatePinner.Builder()
                    // 从服务器证书获取
                    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
                    .build()
            )
            .build()
    }
    
    /**
     * 方式2：自定义 TrustManager
     */
    fun createClientWithCustomTrust(context: Context): OkHttpClient {
        // 加载证书
        val cf = CertificateFactory.getInstance("X.509")
        val cert = context.assets.open("server.crt").use { cf.generateCertificate(it) }
        
        // 创建 KeyStore
        val keyStore = KeyStore.getInstance(KeyStore.getDefaultType())
        keyStore.load(null, null)
        keyStore.setCertificateEntry("server", cert)
        
        // 创建 TrustManager
        val tmf = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm())
        tmf.init(keyStore)
        
        // 创建 SSLContext
        val sslContext = SSLContext.getInstance("TLS")
        sslContext.init(null, tmf.trustManagers, null)
        
        return OkHttpClient.Builder()
            .sslSocketFactory(sslContext.socketFactory, tmf.trustManagers[0] as X509TrustManager)
            .build()
    }
    
    /**
     * 获取证书公钥哈希
     */
    fun getCertificateHash(url: String): String {
        val connection = URL(url).openConnection() as HttpsURLConnection
        connection.connectTimeout = 10_000
        connection.readTimeout = 10_000
        try {
            connection.connect() // 默认链验证与hostname验证仍启用；不要在主线程调用
            val cert = connection.serverCertificates.first() as X509Certificate
            val hash = MessageDigest.getInstance("SHA-256").digest(cert.publicKey.encoded)
            return "sha256/" + Base64.encodeToString(hash, Base64.NO_WRAP)
        } finally {
            connection.disconnect()
        }
    }
}
```

### 8.4 网络安全配置

Android 17 上，**targetSdk ≥ 37** 的应用直接访问本地网络前，必须声明并运行时获得危险权限 `ACCESS_LOCAL_NETWORK`；它归入用户界面的 Nearby devices 权限组。**targetSdk ≤ 36** 且已有 `INTERNET` 的应用走 split permission 隐式授权，不要为低 target 添加或请求该新权限。Android 16 是通过 `RESTRICT_LOCAL_NETWORK` 显式 opt-in 的测试阶段，临时使用 `NEARBY_WIFI_DEVICES`，不能把这套测试授权方式当成 Android 17 的正式流程。

保护覆盖 Wi-Fi/Ethernet 等广播能力接口上的本地网络流量：TCP 主动连接和接受连接、UDP 单播/组播/广播的发送和接收，以及 `.local` 解析。Socket、OkHttp、Cronet、NsdManager 等上层 API 都不能绕过；WebView 继承宿主权限。蜂窝网络、公网访问不因此需要 LAN 权限；本地网络定义排除 VPN 接口，不能仅凭目标是私网 IP 就认定触发。 IPv4 范围含 `169.254.0.0/16`、`100.64.0.0/10`、`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`；IPv6 包括 link-local、直连路由、Thread 等 stub networks 和多子网场景，另含组播 `224.0.0.0/4`、`ff00::/8` 与广播 `255.255.255.255`。地址范围仍须结合上述接口定义。

例外是访问配置的本地 DNS 服务器的 53 端口，以及系统中介选择路径：Google Cast output switcher；mDNS 使用 `DiscoveryRequest.FLAG_SHOW_PICKER` 配合 `NsdManager.registerServiceInfoCallback()`，连接用户选择服务返回的地址无需广泛 LAN 授权。**普通 NsdManager 扫描并非一律豁免**，也不能把一个选中设备的授权扩展为整网扫描。

权限所属组之前已获授权时可能无需再次弹窗，但调用前仍检查权限；拒绝或撤销应停用相关功能、解释用途并提供用户主动重试入口，而不是循环弹窗。TCP 可能表现为超时，UDP 可能是 `EPERM`，不能把所有失败都归为权限错误。

```xml
<!-- 以下用于 targetSdk >= 37 且需要直接广泛 LAN 访问的应用 -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_LOCAL_NETWORK" />
```

```kotlin
// compileSdk 37；Activity 中使用 Activity Result API。
private val requestLan = registerForActivityResult(
    ActivityResultContracts.RequestPermission()
) { granted -> if (granted) connectSelectedDevice() else showLanPermissionDenied() }

fun onConnectClicked() {
    val needsLan = Build.VERSION.SDK_INT >= 37 && applicationInfo.targetSdkVersion >= 37
    val permission = Manifest.permission.ACCESS_LOCAL_NETWORK
    if (!needsLan || ContextCompat.checkSelfPermission(this, permission) ==
        PackageManager.PERMISSION_GRANTED) {
        connectSelectedDevice() // 网络工作不得同步阻塞主线程
    } else {
        requestLan.launch(permission)
    }
}
```

官方范围：[Local network permission](https://developer.android.com/privacy-and-security/local-network-permission)、[Local network definition](https://developer.android.com/privacy-and-security/local-network-definition)。固定 tag 证据：[AndroidManifest.xml](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/res/AndroidManifest.xml) 的危险权限声明；[platform.xml](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/data/etc/platform.xml) 的 `INTERNET` → `ACCESS_LOCAL_NETWORK`、`targetSdk="37"` split；自编 ROM 还须核对 `access_local_network_permission_enabled`，不能将定制开关当作正式 Android 17 适用范围的替代描述。


```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <!-- 禁止明文流量；默认信任系统 CA -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
    
    <!-- 特定域名配置 -->
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set>
            <pin digest="SHA-256">7HIpactkIAq2Y49orFOOQKurWxmmSFZhBCoQYcRhJ3Y=</pin>
            <pin digest="SHA-256">fwza0LRMXouZHUG8fSd1dce45LB745YpQxvV958V/5c=</pin>
        </pin-set>
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </domain-config>
    
    <!-- 自签名证书 -->
    <domain-config>
        <domain includeSubdomains="true">internal.example.com</domain>
        <trust-anchors>
            <certificates src="@raw/my_ca_cert" />
        </trust-anchors>
    </domain-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ... >
</application>
```

### 8.5 抓包防护

```kotlin
/**
 * 抓包防护
 */
object AntiProxy {
    
    /**
     * 检测代理
     */
    fun isProxySet(): Boolean {
        val proxyHost = System.getProperty("http.proxyHost")
        val proxyPort = System.getProperty("http.proxyPort")
        return !proxyHost.isNullOrEmpty() && !proxyPort.isNullOrEmpty()
    }
    
    /**
     * 检测 VPN
     */
    fun isVpnActive(context: Context): Boolean {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetwork ?: return false
        val caps = cm.getNetworkCapabilities(network) ?: return false
        
        // VPN 通常使用 tun0 接口
        return caps.hasTransport(NetworkCapabilities.TRANSPORT_VPN)
    }
    
    /**
     * 禁用代理
     */
    fun createClientWithoutProxy(): OkHttpClient {
        return OkHttpClient.Builder()
            .proxy(Proxy.NO_PROXY)
            .build()
    }
    
    /**
     * 检测抓包应用
     */
    fun detectCaptureApps(context: Context): Boolean {
        val capturePackages = listOf(
            "com.charlesproxy.android",
            "com.telerik.Fiddler",
            "com.minhui.networkcapture",
            "com.minhui.wifipro"
        )
        
        return capturePackages.any { pkg ->
            try {
                context.packageManager.getPackageInfo(pkg, 0)
                true
            } catch (e: Exception) {
                false
            }
        }
    }
}
```

---

## 第 9 章 四大组件安全

### 9.1 Activity 安全

```kotlin
/**
 * Activity 安全
 */

// 1. exported 设置
// ❌ 不安全
<activity android:name=".SecretActivity" android:exported="true" />

// ✅ 安全
<activity android:name=".SecretActivity" android:exported="false" />

// 2. 权限保护
<activity 
    android:name=".AdminActivity"
    android:exported="true"
    android:permission="com.example.ACCESS_ADMIN" />

// 3. 运行时校验
class SecureActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 校验调用者
        if (!verifyCaller()) {
            finish()
            return
        }
        
        // 校验签名
        if (!SignatureChecker.checkSignature(this)) {
            finish()
            return
        }
    }
    
    private fun verifyCaller(): Boolean {
        val callingPackage = callingPackage ?: return false
        // 验证调用者包名
        return callingPackage == "com.example.trustedapp"
    }
}
```

### 9.2 Service 安全

```kotlin
/**
 * Service 安全
 */

// 1. exported 设置
<service 
    android:name=".SecureService"
    android:exported="false" />

// 2. 权限保护
<service 
    android:name=".ApiService"
    android:exported="true"
    android:permission="com.example.MY_PERMISSION" />

// 3. 运行时校验
class SecureService : Service() {
    // onBind 在服务主线程执行，Binder.getCallingUid() 此时不是远端客户端身份。
    override fun onBind(intent: Intent): IBinder = binder

    private val binder = object : IAdminApi.Stub() {
        override fun performAdminOperation() {
            // 校验发生在真实 Binder transaction 内，且在 clearCallingIdentity 之前。
            enforceCallingPermission("com.example.ACCESS_ADMIN", "Admin permission required")
            val callerUid = Binder.getCallingUid()
            performAuthorizedOperation(callerUid)
        }
    }
}
// IAdminApi 为项目 AIDL；Manifest 中导出的 service 也需同一 signature 权限。
```

### 9.3 BroadcastReceiver 安全

```kotlin
/**
 * BroadcastReceiver 安全
 */

// 1. 静态注册 - 权限保护
<receiver 
    android:name=".SecureReceiver"
    android:exported="true"
    android:permission="com.example.SEND_SECURE_BROADCAST">
    <intent-filter>
        <action android:name="com.example.SECURE_ACTION" />
    </intent-filter>
</receiver>

// 2. 发送带权限的广播
sendBroadcast(Intent("com.example.SECURE_ACTION"), "com.example.RECEIVE_SECURE_BROADCAST")

// 3. 进程内事件优先 StateFlow/回调；LocalBroadcastManager 已废弃（旧项目示例）
val localBroadcastManager = LocalBroadcastManager.getInstance(context)
localBroadcastManager.registerReceiver(receiver, IntentFilter("local_action"))

// 4. 运行时校验
class SecureReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // 校验调用者
        val callingUid = if (Build.VERSION.SDK_INT >= 34) sentFromUid else Process.INVALID_UID
            // API 34+ 且发送者分享身份时可用；不可用时拒绝需要身份的操作，不能从 Intent extras 相信 UID。
        if (!isTrustedUid(callingUid)) {
            return
        }
        
        // 处理广播
    }
}
```

### 9.4 ContentProvider 安全

```kotlin
/**
 * ContentProvider 安全
 */

// 1. exported 设置
<provider 
    android:name=".SecureProvider"
    android:authorities="com.example.secure"
    android:exported="false" />

// 2. 权限保护
<provider 
    android:name=".DataProvider"
    android:authorities="com.example.data"
    android:exported="true"
    android:readPermission="com.example.READ_DATA"
    android:writePermission="com.example.WRITE_DATA" />

// 3. 运行时校验
class SecureProvider : ContentProvider() {
    override fun query(
        uri: Uri,
        projection: Array<out String>?,
        selection: String?,
        selectionArgs: Array<out String>?,
        sortOrder: String?
    ): Cursor? {
        // 校验调用者
        val callingUid = Binder.getCallingUid()
        if (!isTrustedUid(callingUid)) {
            throw SecurityException("Unauthorized access")
        }
        
        // 查询数据
        return queryInternal(uri, projection, selection, selectionArgs, sortOrder)
    }
}
```

---

## 第 10 章 WebView 安全

### 10.1 WebView 漏洞

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       WebView 常见漏洞                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────────────────┐
│      漏洞        │                      说明                               │
├──────────────────┼──────────────────────────────────────────────────────────┤
│  任意代码执行    │  addJavascriptInterface 在 4.2 以下有 RCE 漏洞         │
│  密码明文存储    │  WebView 密码会明文存储在数据库中                       │
│  域控制不严      │  file:// 协议可访问本地文件                             │
│  跨域访问        │  setAllowFileAccessFromFileURLs 允许跨域                │
│  SSL 错误忽略    │  onReceivedSslError 忽略证书错误                        │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

### 10.2 JavaScript 接口安全

```kotlin
/**
 * JavaScript 接口安全
 */

// ❌ 危险：低版本存在 RCE 漏洞
webView.addJavascriptInterface(JavaInterface(), "Android")

// API 17+ 注解限制暴露方法，但不认证调用源；所有 frame 都可能调用。只给受控内容暴露最小接口。
class SecureJsInterface {
    @JavascriptInterface
    fun showToast(message: String) {
        Handler(Looper.getMainLooper()).post {
            Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
        }
    }
}

webView.addJavascriptInterface(SecureJsInterface(), "SecureAndroid")

// 安全配置
webView.settings.apply {
    // 禁用不必要的功能
    javaScriptEnabled = true  // 按需开启
    domStorageEnabled = true
    databaseEnabled = false
    allowFileAccess = false  // 禁止文件访问
    allowContentAccess = false
    allowFileAccessFromFileURLs = false
    allowUniversalAccessFromFileURLs = false
}
```

### 10.3 文件访问安全

```kotlin
/**
 * WebView 文件访问安全
 */

// ❌ 危险：允许访问本地文件
webView.settings.allowFileAccess = true
webView.settings.allowFileAccessFromFileURLs = true

// ✅ 安全：禁用文件访问
webView.settings.apply {
    allowFileAccess = false
    allowFileAccessFromFileURLs = false
    allowUniversalAccessFromFileURLs = false
    allowContentAccess = false
}

// 禁用 file:// 协议
webView.webViewClient = object : WebViewClient() {
    override fun shouldOverrideUrlLoading(view: WebView, url: String): Boolean {
        if (url.startsWith("file://")) {
            return true  // 拦截 file:// 协议
        }
        return false
    }
}

// 只加载 HTTPS 资源
webView.webViewClient = object : WebViewClient() {
    override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
        val url = request.url.toString()
        return !url.startsWith("https://")
    }
}
```

### 10.4 WebView 最佳实践

```kotlin
/**
 * WebView 安全最佳实践
 */

class SecureWebView(context: Context) : WebView(context) {
    
    init {
        configureSecurity()
    }
    
    private fun configureSecurity() {
        settings.apply {
            // 基础安全配置
            javaScriptEnabled = true
            domStorageEnabled = true
            
            // 禁用危险功能
            allowFileAccess = false
            allowFileAccessFromFileURLs = false
            allowUniversalAccessFromFileURLs = false
            allowContentAccess = false
            
            // 禁用自动保存密码
            savePassword = false
            
            // 禁用地理定位
            setGeolocationEnabled(false)
            
            // 缩放是可访问性/交互策略，不构成防伪装安全边界
            setSupportZoom(false)
            builtInZoomControls = false
            displayZoomControls = false
            
            // 禁用混合内容
            mixedContentMode = MIXED_CONTENT_NEVER_ALLOW
        }
        
        // 安全的 WebViewClient
        webViewClient = SecureWebViewClient()
        
        // 安全的 WebChromeClient
        webChromeClient = SecureWebChromeClient()
        
        // 移除危险接口
        removeJavascriptInterface("searchBoxJavaBridge_")
        removeJavascriptInterface("accessibility")
        removeJavascriptInterface("accessibilityTraversal")
    }
    
    /**
     * 加载安全的 URL
     */
    fun loadSecureUrl(url: String) {
        // 只允许 HTTPS
        if (!url.startsWith("https://")) {
            throw SecurityException("Only HTTPS URLs are allowed")
        }
        
        // 校验域名白名单
        val host = Uri.parse(url).host
        if (!isWhitelistedHost(host)) {
            throw SecurityException("Host not in whitelist: $host")
        }
        
        loadUrl(url)
    }
    
    private fun isWhitelistedHost(host: String?): Boolean {
        val whitelist = listOf("example.com", "api.example.com")
        return host != null && whitelist.any { host == it || host.endsWith(".$it") }
    }
}

class SecureWebViewClient : WebViewClient() {
    
    override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
        val url = request.url.toString()
        
        // 只允许 HTTPS
        if (!url.startsWith("https://")) {
            return true
        }
        
        // 禁止 file:// 协议
        if (url.startsWith("file://")) {
            return true
        }
        
        return false
    }
    
    override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {
        val url = request.url.toString()
        
        // 拦截危险请求
        if (url.contains("javascript:", ignoreCase = true)) {
            return WebResourceResponse("text/plain", "UTF-8", null)
        }
        
        return null
    }
    
    override fun onReceivedSslError(view: WebView, handler: SslErrorHandler, error: SslError) {
        // ❌ 危险：忽略 SSL 错误
        // handler.proceed()
        
        // ✅ 安全：取消加载
        handler.cancel()
        
        // 可选：显示警告
        Toast.makeText(view.context, "SSL Error", Toast.LENGTH_SHORT).show()
    }
}

class SecureWebChromeClient : WebChromeClient() {
    
    override fun onJsAlert(view: WebView, url: String, message: String, result: JsResult): Boolean {
        // 限制弹窗
        result.cancel()
        return true
    }
    
    override fun onJsConfirm(view: WebView, url: String, message: String, result: JsResult): Boolean {
        // 限制弹窗
        result.cancel()
        return true
    }
}
```

---

## 第 11 章 Intent 安全

### 11.1 Intent 注入攻击

```kotlin
/**
 * Intent 注入攻击
 */

// ❌ 危险：直接使用 Intent 数据
val userId = intent.getStringExtra("user_id")
startActivity(Intent(this, ProfileActivity::class.java).apply {
    putExtra("user_id", userId)  // 未校验，可能被篡改
})

// ✅ 安全：校验 Intent 数据
val userId = intent.getStringExtra("user_id")?.takeIf { 
    it.matches(Regex("^[a-zA-Z0-9]+$")) 
} ?: return

// ✅ 安全：使用 PendingIntent
val pendingIntent = PendingIntent.getActivity(
    context,
    0,
    Intent(context, ProfileActivity::class.java),
    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
)
```

### 11.2 隐式 Intent 风险

```kotlin
/**
 * 隐式 Intent 风险
 */

// ❌ 危险：隐式 Intent 可能被劫持
val intent = Intent("com.example.ACTION_LOGIN")
intent.putExtra("password", password)
startActivity(intent)

// ✅ 安全：使用显式 Intent
val intent = Intent(this, LoginActivity::class.java)
intent.putExtra("password", password)
startActivity(intent)

// ✅ 安全：设置包名限制
val intent = Intent("com.example.ACTION_LOGIN")
intent.setPackage(packageName)  // 限制在当前应用
startActivity(intent)

// ✅ 安全：添加权限
<activity 
    android:name=".LoginActivity"
    android:exported="true"
    android:permission="com.example.PERMISSION_LOGIN">
    <intent-filter>
        <action android:name="com.example.ACTION_LOGIN" />
    </intent-filter>
</activity>
```

### 11.3 PendingIntent 安全

```kotlin
/**
 * PendingIntent 安全
 */

// ❌ 危险：可变的 PendingIntent
val pendingIntent = PendingIntent.getActivity(
    context,
    0,
    Intent("com.example.ACTION"),
    PendingIntent.FLAG_UPDATE_CURRENT  // 可被篡改
)

// ✅ 安全：不可变的 PendingIntent
val pendingIntent = PendingIntent.getActivity(
    context,
    0,
    Intent(context, TargetActivity::class.java),
    PendingIntent.FLAG_IMMUTABLE  // target>=31 必须声明 mutability；RemoteInput 等场景可用受限显式 MUTABLE
)

// 不可变不等于已添加权限；本例未设置接收权限，目标组件仍须校验授权
val pendingIntent = PendingIntent.getBroadcast(
    context,
    0,
    Intent("com.example.ACTION"),
    PendingIntent.FLAG_IMMUTABLE
)

// 使用 requestCode 区分不同的 PendingIntent
val pendingIntent = PendingIntent.getActivity(
    context,
    REQUEST_CODE_UNIQUE,  // 唯一的 requestCode
    intent,
    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_ONE_SHOT  // 一次性使用
)
```

### 11.4 Deep Link 安全

```kotlin
/**
 * Deep Link 安全
 */

// 1. 声明 Deep Link
<activity android:name=".DeepLinkActivity" android:exported="true">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        
        <data android:scheme="https" android:host="example.com" />
        </intent-filter>
        <!-- 自定义 scheme 不能做域名验证，单独声明，防止 data 属性交叉组合。 -->
        <intent-filter>
            <action android:name="android.intent.action.VIEW" />
            <category android:name="android.intent.category.DEFAULT" />
            <category android:name="android.intent.category.BROWSABLE" />
            <data android:scheme="myapp" android:host="open" />
    </intent-filter>
</activity>

// 2. 安全处理 Deep Link
class DeepLinkActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val uri = intent?.data ?: return finish()
        
        // 校验来源
        if (!isSecureDeepLink(uri)) {
            finish()
            return
        }
        
        // 解析参数并校验
        val action = uri.getQueryParameter("action")
        val data = uri.getQueryParameter("data")
        
        when (action) {
            "open_profile" -> openProfile(data)
            "open_payment" -> openPaymentConfirmation(data) // 登录态、服务端授权和用户确认，不凭 Deep Link 直接支付
            else -> finish()  // 未知 action
        }
    }
    
    private fun isSecureDeepLink(uri: Uri): Boolean {
        // 校验 scheme
        if (!((uri.scheme == "https" && uri.host == "example.com") ||
                  (uri.scheme == "myapp" && uri.host == "open"))) return false
        
        // 校验 host
        if (uri.host != "example.com" && uri.host != "open") return false
        
        // 校验路径
        val validPaths = listOf("/profile", "/payment", "/share")
        if (uri.path !in validPaths) return false
        
        return true
    }
}

// 3. App Links（Android 6.0+）
// 自动验证域名所有权，避免选择对话框
// 需要在 /.well-known/assetlinks.json 部署验证文件
```

---

## 第三篇：进阶防护

---

## 第 12 章 SO 安全

### 12.1 NDK 安全基础

下面的编译/反调试属于加固示意，不是信任边界。官方 NDK Clang 不内置 OLLVM 的 `-fla/-sub/-bcf`；SO 用 PIC，PIE 是可执行文件要求。系统 BoringSSL/OpenSSL 不是应用可直接链接的稳定 NDK API，自带加密库须声明依赖并维护。`ptrace(PTRACE_TRACEME)` 会改变进程跟踪状态，失败也可能由策略限制引起，不能直接认定被调试而强制退出。

```cmake
# CMakeLists.txt 安全配置

# 启用安全编译选项
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fstack-protector-all")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -D_FORTIFY_SOURCE=2")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIE")

# 优化级别（不要过度优化）
set(CMAKE_C_FLAGS_RELEASE "-O2")

# 链接选项
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-z,relro")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-z,now")

# 启用 PIE（Position Independent Executable）
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
```

```cpp
// native-lib.cpp

#include <jni.h>
#include <string>
#include <sys/ptrace.h>
#include <unistd.h>

// 字符串加密
#define ENCRYPT_STR(str) decrypt_string(str)

static char* decrypt_string(const char* encrypted) {
    // 简单的 XOR 解密
    static thread_local char decrypted[256];
    size_t len = strlen(encrypted);
    if (len >= sizeof(decrypted)) return nullptr; // 保留终止符，拒绝溢出
    for (int i = 0; i < len; i++) {
        decrypted[i] = encrypted[i] ^ 0x5A;
    }
    decrypted[len] = '\0';
    return decrypted;
}

// 反调试
static int anti_debug() {
    // 检测 ptrace
    if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) {
        return 1;  // 被调试
    }
    
    // 检测调试端口
    FILE* fp = fopen("/proc/net/tcp", "r");
    if (fp) {
        char line[256];
        while (fgets(line, sizeof(line), fp)) {
            if (strstr(line, "5D8A") || strstr(line, "1388")) {
                fclose(fp);
                return 1;  // 检测到调试端口
            }
        }
        fclose(fp);
    }
    
    return 0;
}

// 完整性校验
static int check_integrity(const char* expected_hash) {
    // 读取自身并计算哈希
    // ... 实现
    return 0;
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_SecurityLib_getApiKey(JNIEnv* env, jobject thiz) {
    // 反调试检测
    if (anti_debug()) {
        return env->NewStringUTF("");
    }
    
    // 返回加密的 API Key
    const char* encrypted_key = "\x3a\x2d\x3e...";
    char* key = ENCRYPT_STR(encrypted_key);
    if (key == nullptr) return env->NewStringUTF("");
    jstring result = env->NewStringUTF(key);
    
    // 清理内存
    explicit_bzero(key, strlen(key)); // 本基线支持；普通 memset 可能被优化掉
    
    return result;
}
```

### 12.2 SO 混淆

```cmake
# 使用 LLVM Obfuscator 混淆 SO

# 添加混淆选项
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mllvm -fla")      # 控制流平坦化
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mllvm -sub")      # 指令替换
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mllvm -bcf")      # 虚假控制流
```

### 12.3 反调试技术

```cpp
/**
 * 反调试技术
 */

#include <sys/ptrace.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <dirent.h>

// 1. ptrace 反调试
int anti_ptrace() {
    return ptrace(PTRACE_TRACEME, 0, 0, 0) == -1;
}

// 2. 检测 TracerPid
int check_tracer_pid() {
    FILE* fp = fopen("/proc/self/status", "r");
    if (!fp) return 0;
    
    char line[256];
    while (fgets(line, sizeof(line), fp)) {
        if (strncmp(line, "TracerPid:", 10) == 0) {
            int pid = atoi(line + 10);
            fclose(fp);
            return pid != 0;
        }
    }
    fclose(fp);
    return 0;
}

// 3. 检测调试端口
int check_debug_port() {
    const char* ports[] = {"5D8A", "1388", "0BB8"};  // 23946, 5000, 3000
    FILE* fp = fopen("/proc/net/tcp", "r");
    if (!fp) return 0;
    
    char line[512];
    fgets(line, sizeof(line), fp);  // 跳过标题
    
    while (fgets(line, sizeof(line), fp)) {
        for (int i = 0; i < 3; i++) {
            if (strstr(line, ports[i])) {
                fclose(fp);
                return 1;
            }
        }
    }
    fclose(fp);
    return 0;
}

// 4. 检测 Frida
int check_frida() {
    DIR* dir = opendir("/data/local/tmp");
    if (dir) {
        struct dirent* entry;
        while ((entry = readdir(dir)) != NULL) {
            if (strstr(entry->d_name, "frida") || 
                strstr(entry->d_name, "re.frida")) {
                closedir(dir);
                return 1;
            }
        }
        closedir(dir);
    }
    
    // 检测 frida-server 进程
    FILE* fp = popen("ps -A | grep '[f]rida'", "r");
    if (fp) {
        char line[256];
        if (fgets(line, sizeof(line), fp)) {
            pclose(fp);
            return 1;
        }
        pclose(fp);
    }
    
    return 0;
}

// 5. 检测 Xposed
int check_su_binary() { // su 存在只是 Root 启发信号，不是 Xposed 检测
    FILE* fp = popen("which su", "r");
    if (fp) {
        char line[256];
        if (fgets(line, sizeof(line), fp)) {
            pclose(fp);
            return 1;
        }
        pclose(fp);
    }
    return 0;
}

// 综合检测
int comprehensive_anti_debug() {
    return anti_ptrace() || 
           check_tracer_pid() || 
           check_debug_port() || 
           check_frida() || 
           check_su_binary();
}
```

### 12.4 完整性校验

```cpp
/**
 * 完整性校验
 */

#include <openssl/sha.h>
#include <sys/mman.h>

// 计算 SO 文件哈希
int verify_so_integrity(const char* so_path, const char* expected_hash) {
    FILE* fp = fopen(so_path, "rb");
    if (!fp) return -1;
    
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    
    unsigned char buffer[4096];
    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), fp)) > 0) {
        SHA256_Update(&sha256, buffer, bytes_read);
    }
    
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_Final(hash, &sha256);
    
    fclose(fp);
    
    // 比较哈希
    char hash_str[65];
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(hash_str + (i * 2), "%02x", hash[i]);
    }
    hash_str[64] = '\0';
    
    return strcmp(hash_str, expected_hash) == 0 ? 0 : -1;
}

// 检测内存完整性
int verify_memory_integrity() {
    // 检查关键函数是否被 Hook
    // 比较函数开头的字节与预期值
    return 0;
}
```

---

## 第 13 章 运行时防护

### 13.1 Root 检测

Root/模拟器/Hook/代理检测只是可伪造的风险信号；包可见性、SELinux 和 /proc 限制会产生假阴性，不能代替服务器鉴权。客户端自身签名检测也能被修改；禁止把“检测不到”解释为设备可信。

```kotlin
/**
 * Root 检测
 */
object RootDetector {
    
    private val ROOT_PATHS = arrayOf(
        "/system/app/Superuser.apk",
        "/sbin/su",
        "/system/bin/su",
        "/system/xbin/su",
        "/data/local/xbin/su",
        "/data/local/bin/su",
        "/system/sd/xbin/su",
        "/system/bin/failsafe/su",
        "/data/local/su",
        "/su/bin/su",
        "/su/bin",
        "/magisk/.core/bin/su",
        "/apex/com.android.runtime/bin/su"
    )
    
    private val ROOT_PACKAGES = arrayOf(
        "com.koushikdutta.superuser",
        "com.thirdparty.superuser",
        "eu.chainfire.supersu",
        "com.noshufou.android.su",
        "com.topjohnwu.magisk"
    )
    
    /**
     * 检测 Root
     */
    fun isRooted(context: Context): Boolean {
        return checkRootPaths() || 
               checkRootPackages(context) || 
               checkSuBinary() ||
               checkRootProperties()
    }
    
    /**
     * 检测 Root 路径
     */
    private fun checkRootPaths(): Boolean {
        return ROOT_PATHS.any { path ->
            try {
                File(path).exists()
            } catch (e: Exception) {
                false
            }
        }
    }
    
    /**
     * 检测 Root 应用
     */
    private fun checkRootPackages(context: Context): Boolean {
        return ROOT_PACKAGES.any { pkg ->
            try {
                context.packageManager.getPackageInfo(pkg, 0)
                true
            } catch (e: Exception) {
                false
            }
        }
    }
    
    /**
     * 尝试执行 su
     */
    private fun checkSuBinary(): Boolean {
        return try {
            // 不执行 su（会触发授权提示/等待），只做文件存在的弱信号检查。
            File("/system/bin/su").exists() || File("/system/xbin/su").exists()
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * 检测 Root 属性
     */
    private fun checkRootProperties(): Boolean {
        return try {
            val process = Runtime.getRuntime().exec("getprop ro.build.tags")
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            val result = reader.readLine()
            result?.contains("test-keys") == true
        } catch (e: Exception) {
            false
        }
    }
}
```

### 13.2 模拟器检测

```kotlin
/**
 * 模拟器检测
 */
object EmulatorDetector {
    
    /**
     * 检测模拟器
     */
    fun isEmulator(context: Context): Boolean {
        return checkBuildProperties() ||
               checkHardware() ||
               /* 不读取手机号来推测模拟器：权限敏感且不可靠。 */
               checkFiles() ||
               checkQEmu()
    }
    
    private fun checkBuildProperties(): Boolean {
        return (Build.FINGERPRINT.startsWith("generic")
                || Build.FINGERPRINT.startsWith("unknown")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.MODEL.contains("Android SDK built for x86")
                || Build.MANUFACTURER.contains("Genymotion")
                || Build.BRAND.startsWith("generic") && Build.DEVICE.startsWith("generic")
                || "google_sdk" == Build.PRODUCT
                || Build.HARDWARE.contains("goldfish")
                || Build.HARDWARE.contains("ranchu")
                || Build.PRODUCT.contains("sdk")
                || Build.PRODUCT.contains("emulator")
                || Build.PRODUCT.contains("simulator"))
    }
    
    private fun checkHardware(): Boolean {
        return (Build.HARDWARE.contains("goldfish") ||
                Build.HARDWARE.contains("ranchu") ||
                Build.HARDWARE.contains("vbox86"))
    }
    
    private fun checkPhoneNumber(context: Context): Boolean {
        val tm = context.getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
        val phoneNumber: String? = null // 不请求 READ_PHONE_NUMBERS；历史特征不用于安全决策
        return phoneNumber == "15555215554" || phoneNumber == "15555215556"
    }
    
    private fun checkFiles(): Boolean {
        val emulatorFiles = arrayOf(
            "/dev/socket/genyd",
            "/dev/socket/baseband_genyd",
            "/dev/socket/qemud",
            "/dev/qemu_pipe"
        )
        return emulatorFiles.any { File(it).exists() }
    }
    
    private fun checkQEmu(): Boolean {
        return try {
            val process = Runtime.getRuntime().exec("getprop ro.kernel.qemu")
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            reader.readLine() == "1"
        } catch (e: Exception) {
            false
        }
    }
}
```

### 13.3 Hook 检测

```kotlin
/**
 * Hook 检测
 */
object HookDetector {
    
    private val HOOK_PACKAGES = arrayOf(
        "de.robv.android.xposed.installer",
        "org.lsposed.manager",
        "com.saurik.substrate",
        "com.topjohnwu.magisk"
    )
    
    /**
     * 检测 Xposed
     */
    fun isXposedInstalled(context: Context): Boolean {
        return HOOK_PACKAGES.any { pkg ->
            try {
                context.packageManager.getPackageInfo(pkg, 0)
                true
            } catch (e: Exception) {
                false
            }
        }
    }
    
    /**
     * 检测 Xposed 框架加载
     */
    fun isXposedLoaded(): Boolean {
        return try {
            Class.forName("de.robv.android.xposed.XposedBridge")
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * 检测方法 Hook
     */
    fun isMethodHooked(method: Method): Boolean {
        return try {
            val declaredMethods = Class.forName("java.lang.reflect.Method")
                .getDeclaredField("declaredMethods")
            // 检查方法是否被修改
            false
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * 检测 Frida
     */
    fun isFridaRunning(): Boolean {
        return try {
            // 检测 Frida 端口
            val socket = java.net.Socket("127.0.0.1", 27042)
            socket.close()
            true
        } catch (e: Exception) {
            false
        }
    }
    
    /**
     * 检测 Substrate
     */
    fun isSubstrateLoaded(): Boolean {
        return try {
            Class.forName("com.saurik.substrate.MS\$2")
            true
        } catch (e: Exception) {
            false
        }
    }
}
```

### 13.4 注入检测

```kotlin
/**
 * 注入检测
 */
object InjectionDetector {
    
    /**
     * 检测异常的 ClassLoader
     */
    fun checkClassLoader(): Boolean {
        val classLoader = this::class.java.classLoader
        val className = classLoader?.javaClass?.name
        
        // 检测异常的 ClassLoader
        val suspiciousLoaders = listOf(
            "dalvik.system.DexClassLoader",
            "de.robv.android.xposed.XposedClassLoader"
        )
        
        return className in suspiciousLoaders
    }
    
    /**
     * 检测异常的线程
     */
    fun checkSuspiciousThreads(): Boolean {
        val threadNames = Thread.getAllStackTraces().keys.map { it.name }
        
        val suspiciousNames = listOf(
            "Xposed",
            "Frida",
            "Substrate"
        )
        
        return threadNames.any { name ->
            suspiciousNames.any { suspicious ->
                name.contains(suspicious, ignoreCase = true)
            }
        }
    }
    
    /**
     * 检测 /proc/self/maps 中的异常库
     */
    fun checkLoadedLibraries(): Boolean {
        return try {
            val maps = File("/proc/self/maps").readText()
            val suspiciousLibs = listOf(
                "frida",
                "xposed",
                "substrate",
                "lsposed"
            )
            suspiciousLibs.any { lib -> maps.contains(lib, ignoreCase = true) }
        } catch (e: Exception) {
            false
        }
    }
}
```

---

## 第 14 章 主流加固方案

本章保留历史方案分类，未验证商业产品在 2026-09-10 的在售状态、价格、兼容性和命令行版本；下面能力对比不能当成实测排名或选购建议。Android 17 交付必须对加固后 APK 重新签名验证，并测试动态代码加载限制、16KB 页兼容、启动/崩溃回归。

### 14.1 360加固保

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       360 加固保                                           │
└─────────────────────────────────────────────────────────────────────────────┘

特点：
- DEX 加固
- SO 加固
- 防调试
- 防注入
- 防篡改

使用方式：
1. 下载加固保客户端
2. 上传 APK
3. 下载加固后的 APK
4. 重新签名

集成命令行：
java -jar jiagu.jar -login user password
java -jar jiagu.jar -importsign keystore_path password alias password
java -jar jiagu.jar -jiagu input.apk output_dir -autosign
```

### 14.2 腾讯乐固

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       腾讯乐固                                              │
└─────────────────────────────────────────────────────────────────────────────┘

特点：
- 多重 DEX 加固
- VMP 虚拟化保护
- SO 加固
- 防重打包
- 资源保护

使用方式：
1. 注册腾讯云账号
2. 开通乐固服务
3. 上传 APK
4. 下载加固后的 APK

命令行集成：
legu --input input.apk --output output.apk --sign-config sign.json
```

### 14.3 阿里聚安全

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       阿里聚安全                                            │
└─────────────────────────────────────────────────────────────────────────────┘

特点：
- DEX 加固
- SO 保护
- 病毒扫描
- 漏洞检测
- 内容安全

使用方式：
1. 注册阿里云账号
2. 开通聚安全服务
3. 上传 APK
4. 获取加固报告和加固后的 APK
```

### 14.4 梆梆加固

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       梆梆加固                                              │
└─────────────────────────────────────────────────────────────────────────────┘

特点：
- 多层 DEX 加固
- SO 虚拟化
- VMP 保护
- 防调试
- 防篡改

使用方式：
1. 注册梆梆账号
2. 上传 APK
3. 选择加固选项
4. 下载加固后的 APK
```

### 14.5 方案对比

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       加固方案对比                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬────────────┬────────────┬────────────┬────────────┐
│     方案     │   360      │   腾讯     │   阿里     │   梆梆     │
├──────────────┼────────────┼────────────┼────────────┼────────────┤
│  DEX 加固    │     ✅     │     ✅     │     ✅     │     ✅     │
│  SO 加固     │     ✅     │     ✅     │     ⭐⭐⭐   │     ✅     │
│  VMP 保护    │     ❌     │     ✅     │     ❌     │     ✅     │
│  资源保护    │     ✅     │     ✅     │     ✅     │     ✅     │
│  防调试      │     ✅     │     ✅     │     ✅     │     ✅     │
│  免费额度    │    有限    │    有限    │    有限    │    有限    │
│  兼容性      │    ⭐⭐⭐⭐  │   ⭐⭐⭐⭐⭐  │   ⭐⭐⭐⭐⭐  │   ⭐⭐⭐⭐   │
│  性能影响    │    中等    │     低     │     低     │    中等    │
└──────────────┴────────────┴────────────┴────────────┴────────────┘

选择建议：
- 普通应用：360、腾讯
- 游戏/性能敏感：对候选方案做加固前后启动、帧率、内存实测
- 高安全场景：审查威胁模型、密钥托管和供应链，不能按厂商品牌保证安全
```

---

## 第 15 章 安全最佳实践

### 15.1 安全开发规范

```kotlin
/**
 * 安全开发规范
 */

// 1. 代码规范
// ❌ 硬编码敏感信息
const val API_KEY = "sk-1234567890abcdef"
const val PASSWORD = "admin123"

// ✅ 从安全存储获取
val apiKey = SecureConfig.getApiKey()
val password = KeystoreManager.decrypt(encryptedPassword)

// 2. 日志规范
// ❌ 打印敏感信息
Log.d("TAG", "User password: $password")
Log.d("TAG", "Token: $token")

// ✅ 生产环境禁用敏感日志
if (BuildConfig.DEBUG) {
    Log.d("TAG", "User logged in")
}

// 或使用条件编译
// 在 proguard-rules.pro 中删除日志
-assumenosideeffects class android.util.Log {
    public static int d(...);
    public static int v(...);
    public static int i(...);
}

// 3. 异常处理规范
// ❌ 暴露敏感信息
try {
    // ...
} catch (e: Exception) {
    Toast.makeText(this, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
}

// ✅ 通用错误提示
try {
    // ...
} catch (e: Exception) {
    Log.e("TAG", "Error", e)  // 仅在调试时记录
    Toast.makeText(this, "操作失败，请稍后重试", Toast.LENGTH_SHORT).show()
}

// 4. 权限规范
// ❌ 申请过多权限
<uses-permission android:name="android.permission.READ_CONTACTS" />
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.CAMERA" />

// ✅ 按需申请
// 首次使用时申请，说明用途
fun requestCameraPermission() {
    if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
        != PackageManager.PERMISSION_GRANTED) {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.CAMERA),
            REQUEST_CAMERA
        )
    }
}

// 5. 组件导出规范
// ❌ 不必要地导出组件
<activity android:name=".MainActivity" android:exported="true" />

// ✅ 最小化导出
<activity android:name=".MainActivity" android:exported="false" />

// 必须导出时添加权限保护
<activity 
    android:name=".ApiActivity"
    android:exported="true"
    android:permission="com.example.ACCESS_ADMIN" />
```

### 15.2 安全测试清单

```markdown
## Android 应用安全测试清单

### 1. 代码安全
- [ ] 代码混淆已启用
- [ ] 无硬编码敏感信息
- [ ] 日志已禁用或脱敏
- [ ] 反射调用已保护

### 2. 数据安全
- [ ] 敏感数据已加密存储
- [ ] SharedPreferences 已加密
- [ ] 数据库已加密
- [ ] 临时文件已安全删除

### 3. 网络安全
- [ ] 使用 HTTPS
- [ ] 按威胁模型评估 pinning，若启用已验证备用 pin 与轮换
- [ ] TLS 链/hostname 校验完整，代理检测不作为信任依据
- [ ] 抓包防护已启用

### 4. 组件安全
- [ ] 组件导出已最小化
- [ ] Intent 数据已校验
- [ ] PendingIntent 使用 IMMUTABLE
- [ ] Deep Link 已校验

### 5. WebView 安全
- [ ] JavaScript 接口已保护
- [ ] 文件访问已禁用
- [ ] SSL 错误未忽略
- [ ] 域名白名单已配置

### 6. 运行时防护
- [ ] Root 检测已添加
- [ ] 模拟器检测已添加
- [ ] Hook 检测已添加
- [ ] 调试检测已添加

### 7. 完整性保护
- [ ] 签名校验已添加
- [ ] 完整性校验已添加
- [ ] 加固已实施
```

### 15.3 安全审计工具

```bash
# Android 安全审计工具

# 1. MobSF (Mobile Security Framework)
# 综合安全测试平台
docker pull opensecurity/mobile-security-framework-mobsf
docker run -it -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest

# 2. QARK (Quick Android Review Kit)
# LinkedIn 开源的安全扫描工具
pip install qark
qark --apk path/to/app.apk

# 3. Mariana Trench
# Meta 开源的静态分析工具
mariana-trench --system-jar-paths $ANDROID_HOME/platforms/android-30/android.jar \
  --apk path/to/app.apk

# 4. Drozer
# Android 安全评估框架
pip install drozer
drozer console connect

# 5. APKiD
# 识别加固方案
pip install apkid
apkid app.apk

# 6. jadx
# 反编译工具
jadx app.apk -d output/

# 7. Frida
# 动态分析工具
pip install frida-tools
frida -U -f com.example.app -l script.js
```

### 15.4 漏洞修复流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       安全漏洞修复流程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   漏洞发现   │───▶│   风险评估   │───▶│   修复方案   │───▶│   验证测试   │
│              │    │              │    │              │    │              │
│ - 安全测试  │    │ - 严重程度  │    │ - 制定方案  │    │ - 回归测试  │
│ - 用户反馈  │    │ - 影响范围  │    │ - 代码修复  │    │ - 安全验证  │
│ - 扫描报告  │    │ - 利用难度  │    │ - 测试验证  │    │ - 发布更新  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

**修复优先级**：

| 严重程度 | 描述 | 修复时限 |
|---------|------|---------|
| 严重 | 可导致数据泄露/远程执行 | 24小时内 |
| 高危 | 可导致敏感信息泄露 | 3天内 |
| 中危 | 可被利用但影响有限 | 7天内 |
| 低危 | 风险较低 | 下版本修复 |

---

## 第 18 章 面试常见问题

### 18.1 混淆原理

**Q1: 什么是代码混淆？ProGuard 和 R8 有什么区别？**

**A:**

代码混淆是将代码中的类名、方法名、字段名替换为无意义的短名称，增加逆向难度。

```text
┌──────────────────┬──────────────────┬──────────────────┐
│       特性        │    ProGuard     │       R8         │
├──────────────────┼──────────────────┼──────────────────┤
│  代码混淆        │       ✅         │       ✅         │
│  代码优化        │       ✅         │       ✅✅       │
│  资源压缩        │       ❌         │       ✅         │
│  编译速度        │       慢         │       快         │
│  Kotlin 支持     │       一般       │       好         │
│  默认启用        │     AGP < 3.4    │    AGP >= 3.4    │
└──────────────────┴──────────────────┴──────────────────┘
```

**Q2: 混淆有哪些常见问题？如何解决？**

**A:**

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| ClassNotFoundException | 反射使用的类被混淆 | `-keep class com.example.ReflectClass` |
| JSON 解析失败 | 实体类字段被混淆 | `-keep class com.example.bean.** { *; }` |
| WebView JS 失效 | @JavascriptInterface 被混淆 | 保留注解方法 |
| EventBus 失效 | 订阅方法被混淆 | 保留 @Subscribe 方法 |

### 18.2 加固技术

**Q3: APK 加固的原理是什么？**

**A:**

```text
加固原理：

1. 加密原始 DEX
   - 将 classes.dex 加密
   - 存储到 assets/ 目录

2. 注入壳代码
   - 添加壳 DEX 作为入口
   - 修改 AndroidManifest.xml

3. 运行时解密
   - 壳代码在 attachBaseContext 解密
   - 动态加载原始 DEX
   - 替换 ClassLoader
```

**Q4: 常见的加固方案有哪些？如何选择？**

**A:**

| 方案 | 特点 | 适用场景 |
|------|------|---------|
| 360加固保 | 免费、易用 | 普通应用 |
| 腾讯乐固 | VMP保护、性能好 | 游戏/金融 |
| 阿里聚安全 | 病毒扫描 | 阿里生态 |
| 梆梆加固 | 多层保护 | 高安全要求 |

### 18.3 加密算法

**Q5: 对称加密和非对称加密的区别？**

**A:**

| 对比项 | 对称加密 (AES) | 非对称加密 (RSA) |
|-------|---------------|-----------------|
| 密钥 | 加解密用同一密钥 | 公钥加密，私钥解密 |
| 速度 | 快 | 慢 |
| 安全性 | 密钥泄露风险 | 更安全 |
| 适用场景 | 大量数据加密 | 密钥交换、签名 |

**Q6: 什么是 Android Keystore？**

**A:**

Android Keystore 是 Android 提供的安全密钥存储系统：
- 密钥可由软件/TEE/StrongBox 保护；用 KeyInfo 核实安全级别
- 密钥不可导出
- 支持用户认证绑定
- 支持密钥使用限制

```kotlin
// 使用 Keystore 生成密钥
val keyGenerator = KeyGenerator.getInstance(
    KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore"
)
keyGenerator.init(
    KeyGenParameterSpec.Builder("my_key", 
        KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
        .setKeySize(256)
        .setUserAuthenticationRequired(true)
        .build()
)
```

### 18.4 网络安全

**Q7: 什么是 SSL Pinning？为什么要用？**

**A:**

SSL Pinning（证书绑定）是将服务器证书或公钥硬编码到客户端，防止中间人攻击。

**使用场景**：
- 防止 Charles/Fiddler 抓包
- 防止 DNS 劫持
- 防止伪造证书攻击

```kotlin
// OkHttp 证书绑定
val client = OkHttpClient.Builder()
    .certificatePinner(
        CertificatePinner.Builder()
            .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            .build()
    )
    .build()
```

**Q8: HTTPS 一定安全吗？**

**A:**

不一定。HTTPS 可能被以下方式攻击：
1. 中间人攻击（用户安装了恶意证书）
2. SSL Strip（降级攻击）
3. 证书伪造
4. 服务端配置不当

解决方案：
- 使用 SSL Pinning
- 校验证书链
- 禁用明文流量

### 18.5 组件安全

**Q9: Android 组件导出有什么风险？**

**A:**

| 组件 | 风险 | 防护 |
|------|------|------|
| Activity | 越权访问界面 | exported=false 或权限保护 |
| Service | 越权调用服务 | 权限校验、签名校验 |
| Receiver | 恶意广播攻击 | LocalBroadcast、权限保护 |
| Provider | 数据泄露 | readPermission、路径限制 |

**Q10: WebView 有哪些安全漏洞？**

**A:**

| 漏洞 | 说明 | 解决方案 |
|------|------|---------|
| addJavascriptInterface RCE | API < 17 有远程执行漏洞 | 使用 @JavascriptInterface |
| file:// 协议 | 可访问本地文件 | 禁用 file:// |
| 密码明文存储 | WebView 会保存密码 | setSavePassword(false) |
| SSL 错误忽略 | onReceivedSslError 处理不当 | 不要调用 handler.proceed() |

---

## 总结

### Android 安全核心要点

1. **代码安全**：混淆 + 加固 + 反调试
2. **数据安全**：加密存储 + 安全传输
3. **网络安全**：HTTPS + SSL Pinning
4. **组件安全**：最小化导出 + 权限保护
5. **运行时安全**：Root检测 + Hook检测

### 安全防护层次

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       安全防护金字塔                                        │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────┐
                        │    运行时防护    │
                        │  Root/Hook检测   │
                        └────────┬─────────┘
                                 │
                    ┌────────────┴────────────┐
                    │       通信安全          │
                    │   HTTPS + SSL Pinning   │
                    └────────────┬────────────┘
                                 │
               ┌─────────────────┴─────────────────┐
               │             数据安全              │
               │      加密存储 + Keystore          │
               └─────────────────┬─────────────────┘
                                 │
          ┌──────────────────────┴──────────────────────┐
          │                  组件安全                   │
          │       exported=false + 权限保护            │
          └──────────────────────┬──────────────────────┘
                                 │
     ┌───────────────────────────┴───────────────────────────┐
     │                      代码安全                        │
     │              混淆 + 加固 + 反调试                    │
     └───────────────────────────────────────────────────────┘
```

### 面试重点

1. **混淆原理**：ProGuard/R8 配置和常见问题
2. **加固原理**：DEX 加密、壳代码、动态加载
3. **加密算法**：AES、RSA、SHA、Keystore
4. **网络安全**：HTTPS、SSL Pinning、证书校验
5. **组件安全**：exported、权限、Intent 校验

---

**文档版本**：v1.0  
**更新时间**：2026-09-09
**适用版本**：平台源码 Android 17；GCM Keystore 示例 API 23+，其他 API 按各节注明。