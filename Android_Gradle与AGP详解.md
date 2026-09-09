# Android Gradle & AGP 完全指南

> 适用环境：Android 17（API 37）；构建示例使用 AGP 9.1.1、Gradle 9.3.1、JDK 17，Android SDK 与构建工具各自独立发布。

> 作者：OpenClaw (Android 架构师) | 日期：2026-03-12

## 目录

- [1. 概述](#1-概述)
  - [1.1 Gradle 是什么](#11-gradle-是什么)
  - [1.2 AGP 版本对应](#12-agp-版本对应)
- [2. Gradle 核心原理](#2-gradle-核心原理)
  - [2.1 Gradle 架构](#21-gradle-架构)
  - [2.2 Gradle 守护进程](#22-gradle-守护进程)
- [3. Gradle 构建生命周期](#3-gradle-构建生命周期)
  - [3.1 三个阶段](#31-三个阶段)
  - [3.2 生命周期回调与配置缓存边界](#32-生命周期回调与配置缓存边界)
- [4. Project 与 Task 详解](#4-project-与-task-详解)
  - [4.1 Project 对象](#41-project-对象)
  - [4.2 Task 对象](#42-task-对象)
  - [4.3 Task 依赖图](#43-task-依赖图)
- [5. Gradle Wrapper 机制](#5-gradle-wrapper-机制)
  - [5.1 Wrapper 原理](#51-wrapper-原理)
  - [5.2 Wrapper 命令](#52-wrapper-命令)
- [6. build.gradle 完全解析](#6-buildgradle-完全解析)
  - [6.1 根项目 build.gradle](#61-根项目-buildgradle)
  - [6.2 应用模块 build.gradle](#62-应用模块-buildgradle)
  - [6.3 依赖类型](#63-依赖类型)
  - [6.4 依赖冲突解决](#64-依赖冲突解决)
  - [6.5 最小应用入口与构建诊断](#65-最小应用入口与构建诊断)
- [7. AGP 架构与版本演进](#7-agp-架构与版本演进)
  - [7.1 AGP 版本演进](#71-agp-版本演进)
  - [7.2 AGP 核心扩展](#72-agp-核心扩展)
- [8. AGP 完整构建流程](#8-agp-完整构建流程)
  - [8.1 构建流程图](#81-构建流程图)
- [9. 打包流程详解](#9-打包流程详解)
  - [9.1 AAPT2 资源编译](#91-aapt2-资源编译)
  - [9.2 DEX 编译](#92-dex-编译)
  - [9.3 APK 签名](#93-apk-签名)
- [10. 构建变体与产品风味](#10-构建变体与产品风味)
  - [10.1 Build Types](#101-build-types)
  - [10.2 Product Flavors](#102-product-flavors)
  - [10.3 Build Variants](#103-build-variants)
- [11. 构建优化实战](#11-构建优化实战)
  - [11.1 基础优化](#111-基础优化)
  - [11.2 高级优化](#112-高级优化)
  - [11.3 构建速度对比](#113-构建速度对比)
- [12. 自定义 Gradle 插件](#12-自定义-gradle-插件)
  - [12.1 用声明式任务生成文件](#121-用声明式任务生成文件)
  - [12.2 应用插件与验证缓存行为](#122-应用插件与验证缓存行为)
  - [12.3 Android Components 与产物 Provider](#123-android-components-与产物-provider)
  - [12.4 处理器与插件迁移顺序](#124-处理器与插件迁移顺序)
- [13. 面试常见问题](#13-面试常见问题)
  - [13.1 基础问题](#131-基础问题)
  - [13.2 进阶问题](#132-进阶问题)
- [总结](#总结)

---

## 1. 概述

### 1.1 Gradle 是什么

Gradle 是一个现代化的构建自动化工具：
• 基于 JVM 的构建工具
• 支持 Groovy/Kotlin DSL
• 强大的依赖管理
• 增量构建和缓存
• 可扩展的插件系统

### 1.2 AGP 版本对应

| 用途 | AGP | Gradle | 运行 Gradle 的 JDK | 支持边界 |
|------|-----|--------|-------------------|----------|
| 历史示例 | 8.3 | 最低 8.4 | 17 | 不用该旧组合推导 API 37 支持 |
| 迁移参照 | 9.0 | 9.1.0 | 17 | 官方最大 API 36.1，不是 API 37 基线 |
| 本文 API 37 示例 | **9.1.1** | **9.3.1** | **17** | 官方支持 API 37.0 及以下 |

这些是具体兼容组合，不是“任意更高版本都兼容”，也不是最新版本排名。SDK Build Tools、NDK、Kotlin、KSP 及三方插件分别受兼容矩阵约束；不要由 Android 17 推导其版本号。`compileSdk = 37` 开放编译 API，`targetSdk = 37` 则选择新行为，需要独立回归。

官方来源：[AGP 8.3](https://developer.android.com/build/releases/past-releases/agp-8-3-0-release-notes)、[AGP 9.0](https://developer.android.com/build/releases/agp-9-0-0-release-notes)、[AGP 9.1（页面明确列出 9.1.1 的 API 37 支持）](https://developer.android.com/build/releases/agp-9-1-0-release-notes)、[Android 17 配置](https://developer.android.com/about/versions/17/setup-sdk)。

---

## 2. Gradle 核心原理

### 2.1 Gradle 架构

```text
Gradle Daemon (守护进程)
    │
    ├── Gradle Core
    │   ├── Settings (设置)
    │   ├── Project (项目)
    │   ├── Task (任务)
    │   ├── Plugin (插件)
    │   └── Extension (扩展)
    │
    ├── Dependency Management
    │   ├── Repository (仓库)
    │   ├── Configuration (配置)
    │   └── Resolution (解析)
    │
    └── Build Cache & Incremental
        ├── Local Cache (本地缓存)
        ├── Remote Cache (远程缓存)
        └── Incremental (增量构建)
```

### 2.2 Gradle 守护进程

```text
守护进程作用:
• 保持 JVM 运行，避免每次启动
• 缓存构建状态
• 大幅提升构建速度

配置 (gradle.properties):
org.gradle.daemon=true
org.gradle.daemon.idletimeout=10800000

查看状态:
./gradlew --status

停止守护进程:
./gradlew --stop
```

---

## 3. Gradle 构建生命周期

### 3.1 三个阶段

```text
1. 初始化阶段 (Initialization)
   • 解析 settings.gradle(.kts)
   • 确定参与构建的 Project
   • 创建 Project 对象

2. 配置阶段 (Configuration)
   • 解析所有 build.gradle(.kts)
   • 执行脚本代码
   • 创建和配置 Task
   • 构建 Task 依赖图 (DAG)

3. 执行阶段 (Execution)
   • 确定执行顺序
   • 检查 Task 状态
   • 按顺序执行 Task
```

### 3.2 生命周期回调与配置缓存边界

初始化读取 settings 并确定项目图；配置阶段注册模型与任务；执行阶段只运行所需任务。Configuration Cache 保存配置结果和任务图，Build Cache 保存可缓存任务的输出，二者解决不同问题。

任务执行期不能再从 Project 读取动态配置对象。把值作为输入 Property 接入任务，Gradle 才能追踪变化并在配置缓存恢复后重建任务所需状态。`taskGraph.beforeTask/afterTask` 一类执行监听与 Configuration Cache 不兼容；跨任务监控采用 Build Service 或受支持的事件接口。

```kotlin
// build.gradle.kts：无输出的诊断任务，每次都会执行。
val message = providers.gradleProperty("buildMessage").orElse("hello")
tasks.register("printBuildMessage") {
    val capturedMessage = message.get() // 配置期求值，执行动作仅捕获 String
    doLast { println(capturedMessage) }
}
```

要利用 Build Cache，则把生成逻辑写成第 12 章的 `@CacheableTask`，声明所有输入和输出。配置缓存命中不意味着任务输出也命中缓存；UP-TO-DATE 表示本地输入输出未变，FROM-CACHE 表示从任务输出缓存恢复。

参考：[Gradle 9.3.1 配置缓存要求](https://docs.gradle.org/9.3.1/userguide/configuration_cache_requirements.html)、[Build Cache](https://docs.gradle.org/9.3.1/userguide/build_cache.html)。

## 4. Project 与 Task 详解

### 4.1 Project 对象

```kotlin
interface Project {
    val name: String              // 项目名称
    val path: String              // 项目路径 (:app)
    val projectDir: File          // 项目目录
    val buildDir: File            // 构建目录

    // 任务管理
    val tasks: TaskContainer

    // 依赖管理
    val dependencies: DependencyHandler

    // 扩展
    val extensions: ExtensionContainer

    // 生命周期
    fun afterEvaluate(action: Action<Project>)
}
```

### 4.2 Task 对象

```kotlin
interface Task {
    val name: String              // 任务名称
    val group: String?            // 任务分组
    val description: String?      // 任务描述
    val enabled: Boolean          // 是否启用

    // 输入输出
    val inputs: TaskInputs
    val outputs: TaskOutputs

    // 依赖
    fun dependsOn(vararg paths: Any): Task

    // 执行回调
    fun doFirst(action: Action<Task>)
    fun doLast(action: Action<Task>)
}

// 创建 Task
tasks.register("hello") {
    group = "custom"
    description = "Prints hello"

    doFirst {
        println("Before hello")
    }

    doLast {
        println("Hello, Gradle!")
    }
}
```

### 4.3 Task 依赖图

```text
Task 依赖图 (DAG):

                    assemble
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
      bundleDebug  bundleRelease  test
          │            │
          ▼            ▼
      packageDebug  packageRelease
          │            │
          ▼            ▼
    processResources processResources
          │            │
          ▼            ▼
      compileJava   compileJava

执行顺序: compileJava → processResources → package → bundle → assemble
```

---

## 5. Gradle Wrapper 机制

### 5.1 Wrapper 原理

```text
为什么需要 Wrapper:
1. 统一团队 Gradle 版本
2. 无需预先安装 Gradle
3. 自动下载指定版本

文件结构:
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── gradlew
└── gradlew.bat

gradle-wrapper.properties:
distributionUrl=https\://services.gradle.org/distributions/gradle-9.3.1-bin.zip
```

### 5.2 Wrapper 命令

```bash
# 生成 Wrapper
gradle wrapper

# 指定版本
gradle wrapper --gradle-version 9.3.1

# 升级版本
./gradlew wrapper --gradle-version 9.3.1
```

---

## 6. build.gradle 完全解析

### 6.1 根项目 build.gradle

以下是 **AGP 9.1.1 / Gradle 9.3.1 / JDK 17** 的最小 View 工程配置片段。它使用 AGP 内置 Kotlin，不再应用 `org.jetbrains.kotlin.android`。先设置 Wrapper，再在根工程统一插件版本；这里不引入无版本的 KSP，也不把 Hilt 处理器或缺少编译器插件的 Compose 混入基础示例。

```kotlin
// settings.gradle.kts
pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "Api37Sample"
include(":app")
```

```kotlin
// build.gradle.kts（根工程）
plugins {
    id("com.android.application") version "9.1.1" apply false
    id("com.android.library") version "9.1.1" apply false
}
```

### 6.2 应用模块 build.gradle

```kotlin
// app/build.gradle.kts
plugins {
    id("com.android.application")
}

android {
    namespace = "com.example.myapp"
    compileSdk = 37

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 24
        targetSdk = 37 // 仅在完成新行为验证后用于产品发布
        versionCode = 1
        versionName = "1.0.0"
    }
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    buildFeatures { viewBinding = true }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

dependencies {
    // AndroidX 依赖独立锁定，不随 compileSdk 自动升级。
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    testImplementation("junit:junit:4.13.2")
}
```

`org.jetbrains.kotlin.kapt` 与 AGP 9 内置 Kotlin 不兼容。只有处理器提供 KSP 实现、且生成类型依赖链都满足条件时才迁移；不能迁移时按官方方案评估 `com.android.legacy-kapt`，不要盲目改配置名。需要 Compose 时另配 Compose 编译器插件及其兼容版本。应用模块依赖 library 使用 `implementation(project(":library"))`；`api` 的使用场景是 library 对外暴露 API。

来源：[内置 Kotlin 迁移](https://developer.android.com/build/migrate-to-built-in-kotlin)、[Dagger KSP 生成类型限制](https://dagger.dev/dev-guide/ksp.html)、[AGP 9.1 发布说明](https://developer.android.com/build/releases/agp-9-1-0-release-notes)。应用入口的清单与源码配置见 6.5 节。

### 6.3 依赖类型

| 依赖类型 | 说明 |
|---------|------|
| implementation | 本模块编译/运行需要；不暴露给消费者编译类路径，但仍可进入消费者运行时类路径 |
| api | library 的依赖同时暴露给消费者编译与运行时类路径 |
| compileOnly | 仅编译时使用，不打包 |
| runtimeOnly | 仅运行时使用 |
| ksp | Kotlin 符号处理器 |
| testImplementation | 单元测试依赖 |
| debugImplementation | Debug 构建依赖 |

依赖可见性来源：[Gradle Java Library 的 API/implementation 分离](https://docs.gradle.org/9.3.1/userguide/java_library_plugin.html)。`implementation` 不等于“运行时不传递”，`compileOnly` 也不等于“运行时不需要”。

### 6.4 依赖冲突解决

```kotlin
// 查看依赖树
// ./gradlew app:dependencies

// 强制版本
dependencies {
    implementation("com.example:lib") {
        version {
            strictly("1.0.0")
        }
    }
}

// 排除传递依赖
dependencies {
    implementation("com.example:A") {
        exclude(group = "com.example", module = "common")
    }
}

// 全局强制版本
configurations.all {
    resolutionStrategy {
        force("com.example:common:1.0.0")
    }
}
```

---

### 6.5 最小应用入口与构建诊断

根 settings 中为插件和依赖分别配置仓库，并 include 应用模块：

```kotlin
// settings.gradle.kts
pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "Api37Sample"
include(":app")
```

配合 6.1–6.2 的 AGP 配置，添加一个不依赖布局资源的 Activity：

```xml
<!-- app/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:label="API 37 Sample">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

```kotlin
// app/src/main/java/com/example/myapp/MainActivity.kt
package com.example.myapp
class MainActivity : android.app.Activity() {
    override fun onCreate(savedInstanceState: android.os.Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(android.widget.TextView(this).apply { text = "Android 17 / API 37" })
    }
}
```

创建空的 `app/proguard-rules.pro`，通过 `local.properties` 的 sdk.dir 或 ANDROID_HOME 指向安装了 API 37 的 SDK。Gradle 运行 JDK、Java toolchain、Java source/target 和 Kotlin jvmTarget 是不同层次，示例统一为 17 以减少字节码目标不一致。

```powershell
.\gradlew.bat --version
.\gradlew.bat :app:assembleDebug --configuration-cache
.\gradlew.bat :app:assembleDebug --configuration-cache
.\gradlew.bat :app:dependencyInsight --dependency androidx.core --configuration debugRuntimeClasspath
```

插件解析失败先检查 pluginManagement，依赖解析失败检查 dependencyResolutionManagement；SDK 缺失与 Maven 仓库错误不是同一种问题。配置缓存失败按报告定位捕获的 Project/Configuration/脚本对象，不把 `--no-configuration-cache` 当成永久修复。

## 7. AGP 架构与版本演进

### 7.1 AGP 版本演进

| AGP 版本 | 公开 API 变化 |
|---------|----------------|
| 8.0 | 移除 Transform API，不是刚开始废弃 |
| 8.3 | KSP 仍是独立配置的处理插件，不能称为“AGP 默认 KSP” |
| 9.0 | 默认内置 Kotlin，DSL 转向新的公开接口 |
| 9.1.1 | 官方支持 API 37.0，采用对应 Gradle/JDK 组合 |

来源：[AGP 8.0 移除项](https://developer.android.com/build/releases/past-releases/agp-8-0-0-release-notes)、[AGP 9.0](https://developer.android.com/build/releases/agp-9-0-0-release-notes)、[AGP 9.1](https://developer.android.com/build/releases/agp-9-1-0-release-notes)。自定义插件不要强转到旧 `AppExtension`，也不要调用内部 AGP API。

### 7.2 AGP 核心扩展

```kotlin
// com.android.build.api.dsl.ApplicationExtension - 应用 DSL
android {
    // 基本配置
    namespace = "com.example"
    compileSdk = 37

    // 默认配置
    defaultConfig {
        applicationId = "com.example"
        minSdk = 24
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"
    }

    // 签名配置
    signingConfigs {
        create("release") {
            storeFile = file("keystore.jks")
            storePassword = providers.environmentVariable("RELEASE_STORE_PASSWORD").orNull
            keyAlias = "alias"
            keyPassword = providers.environmentVariable("RELEASE_KEY_PASSWORD").orNull
        }
    }

    // 构建类型
    buildTypes {
        debug { }
        release { }
    }

    // 产品风味
    productFlavors {
        create("google") { }
        create("huawei") { }
    }

    // 构建特性
    buildFeatures {
        viewBinding = true
        compose = true
        buildConfig = true
    }
}
```

---

## 8. AGP 完整构建流程

### 8.1 构建流程图

```text
./gradlew assembleDebug
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  1. 加载项目和插件                                           │
│     • 解析 settings.gradle                                  │
│     • 应用 Android 插件                                     │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. 资源处理 (AAPT2)                                         │
│     • aapt2 compile: *.xml → *.flat                        │
│     • aapt2 link: *.flat → resources.pb                    │
│     • mergeResources: 合并所有资源                          │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. 代码处理                                                 │
│     • aidl → Java                                           │
│     • 注解处理 (KAPT/KSP)                                   │
│     • Java 编译: .java → .class                             │
│     • Kotlin 编译: .kt → .class                             │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. DEX 编译                                                 │
│     • class → dex (d8)                                      │
│     • 多 dex 处理                                            │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  5. 打包                                                     │
│     • 合并所有 dex                                           │
│     • 合并资源                                               │
│     • 合并 native 库                                         │
│     • 生成未签名 APK                                         │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  6. 对齐 (zipalign；签名前)                                  │
│     • 检查 APK ZIP 条目及 native 库打包对齐                  │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  7. 签名并验证 (apksigner)                                  │
│     • 签名后不要再修改 APK                                  │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
   最终 APK
```

---

## 9. 打包流程详解

### 9.1 AAPT2 资源编译

```text
AAPT2 (Android Asset Packaging Tool 2)

1. 编译阶段 (compile):
   res/layout/main.xml → main.xml.flat (二进制格式)

2. 链接阶段 (link):
   *.flat → resources.pb + resource_table.pb

优点:
• 增量编译: 只编译变化的资源
• 并行编译: 多个资源并行处理
• 更快的链接: 预编译格式
```

### 9.2 DEX 编译

```text
DEX 编译流程:
.class ──► d8 ──► classes.dex

D8 编译器 (替代 DX):
• 更快的编译速度
• 更小的 DEX 体积
• 支持 Java 8+ 特性

MultiDex:
当方法数超过 65536:
classes.dex, classes2.dex, classes3.dex ...

android {
    defaultConfig {
        multiDexEnabled true
    }
}
```

### 9.3 APK 签名

```text
签名方案:

V1 签名 (JAR 签名):
• META-INF/ 目录下的三个文件
• 兼容 Android 7.0 以下

V2 签名 (APK 签名方案 v2):
• 签名数据在 ZIP 中央目录之前
• 更快的验证速度
• 更安全 (不能修改 APK)

V3 签名:
• 支持密钥轮换

V4 签名:
• 用于 ADB 增量安装

配置:
android {
    signingConfigs {
        release {
            v1SigningEnabled true
            v2SigningEnabled true
        }
    }
}
```

---

## 10. 构建变体与产品风味

### 10.1 Build Types

```kotlin
android {
    buildTypes {
        debug {
            isDebuggable = true
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }

        release {
            isDebuggable = false
            isMinifyEnabled = true
            isShrinkResources = true
        }
    }
}
```

### 10.2 Product Flavors

```kotlin
android {
    flavorDimensions += "channel"

    productFlavors {
        create("google") {
            dimension = "channel"
            manifestPlaceholders["CHANNEL"] = "google"
        }

        create("huawei") {
            dimension = "channel"
            manifestPlaceholders["CHANNEL"] = "huawei"
        }
    }
}
```

### 10.3 Build Variants

```text
Build Variants 组合:

Flavor Dimensions: channel
Build Types: debug, release

生成的 Variants:
• googleDebug, googleRelease
• huaweiDebug, huaweiRelease

构建命令:
./gradlew assembleGoogleDebug
./gradlew assembleHuaweiRelease
```

---

## 11. 构建优化实战

### 11.1 基础优化

```properties
# gradle.properties

# 守护进程
org.gradle.daemon=true

# 并行构建
org.gradle.parallel=true

# 构建缓存
org.gradle.caching=true

# 不默认开启按需配置；先验证插件与多项目配置行为

# 增加内存
org.gradle.jvmargs=-Xmx4096m -XX:+HeapDumpOnOutOfMemoryError

# Configuration Cache：需验证每个插件及任务的兼容性，不再统称实验性
org.gradle.configuration-cache=true
```

### 11.2 高级优化

```kotlin
// 1. 仅处理器明确支持 KSP 且插件已配置兼容版本时迁移 KAPT
plugins {
    id("com.google.devtools.ksp")
}

dependencies {
    // kapt("com.example:processor:1.0")
    ksp("com.example:processor:1.0")
}

// 2. 关闭未使用的代码生成功能（不是启用 Build Cache）
android {
    buildFeatures {
        buildConfig = false  // 不需要时禁用
        aidl = false
    }
}

// 3. 优化资源
android {
    buildTypes {
        release {
            isMinifyEnabled = true    // 与资源压缩配套启用代码压缩
            isShrinkResources = true  // 资源压缩
        }
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}
```

### 11.3 构建速度对比

```text
优化前:
• Clean Build: ~3 分钟
• Incremental Build: ~30 秒

优化后:
• Clean Build: ~1.5 分钟 (-50%)
• Incremental Build: ~10 秒 (-67%)

优化措施:
1. ✅ 启用守护进程和并行构建
2. ✅ 使用 KSP 替代 KAPT
3. ✅ 启用 Configuration Cache
4. ✅ 增加内存配置
5. ✅ 禁用不需要的 Build Features
```

---

## 12. 自定义 Gradle 插件

### 12.1 用声明式任务生成文件

以下插件在 buildSrc 中实现，只依赖 Gradle 9.3.1 公共 API。任务输入是 message，输出是目标文件；执行动作只读取任务属性，不访问 Project、扩展或执行期环境变量。

```kotlin
// buildSrc/build.gradle.kts
plugins { `kotlin-dsl`; `java-gradle-plugin` }
repositories { gradlePluginPortal(); mavenCentral() }
gradlePlugin {
    plugins {
        create("guide") {
            id = "example.guide"
            implementationClass = "example.GuidePlugin"
        }
    }
}
```

```kotlin
// buildSrc/src/main/kotlin/example/GuidePlugin.kt
package example

import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.api.DefaultTask
import org.gradle.api.provider.Property
import org.gradle.api.file.RegularFileProperty
import org.gradle.api.tasks.*

interface GuideExtension { val message: Property<String> }

@CacheableTask
abstract class GenerateGuide : DefaultTask() {
    @get:Input abstract val message: Property<String>
    @get:OutputFile abstract val outputFile: RegularFileProperty

    @TaskAction fun generate() {
        val text = message.get()
        require(text.isNotBlank()) { "guide.message 不可为空" }
        val output = outputFile.get().asFile
        output.parentFile.mkdirs()
        output.writeText(text + "\n", Charsets.UTF_8)
    }
}
class GuidePlugin : Plugin<Project> {
    override fun apply(project: Project) {
        val extension = project.extensions.create("guide", GuideExtension::class.java)
        extension.message.convention("Android 17")
        project.tasks.register("generateGuide", GenerateGuide::class.java) { task ->
            task.group = "documentation"
            task.message.set(extension.message)
            task.outputFile.set(project.layout.buildDirectory.file("generated/guide.txt"))
        }
    }
}
```

### 12.2 应用插件与验证缓存行为

```kotlin
// 根 build.gradle.kts；与已有 plugins 块合并。
plugins { id("example.guide") }
configure<example.GuideExtension> {
    message.set(providers.gradleProperty("guideMessage").orElse("API 37 sample"))
}
```

```powershell
.\gradlew.bat generateGuide --configuration-cache --build-cache
.\gradlew.bat generateGuide --configuration-cache --build-cache
.\gradlew.bat generateGuide -PguideMessage="changed" --configuration-cache --build-cache
```

第二次运行应具备配置缓存复用和任务 UP-TO-DATE 的条件；修改输入后任务重新执行。任务输出不能包含当前时间、随机 UUID 或绝对工作目录，否则相同输入无法产生相同结果。文件写入失败应让任务失败并输出错误，不能 catch 后打印“成功”。

### 12.3 Android Components 与产物 Provider

AGP 的变体模型使用 `androidComponents`。`beforeVariants` 控制哪些变体被创建；`onVariants` 获得已确定的变体并连接任务/产物 Provider，避免猜测 AGP 内部任务名或强转旧 AppExtension。

```kotlin
// app/build.gradle.kts；导入放在文件首部。
import com.android.build.api.artifact.SingleArtifact

androidComponents {
    // 演示按构建类型选择变体；不在此执行文件 I/O。
    onVariants(selector().withBuildType("release")) { variant ->
        val mergedManifest = variant.artifacts.get(SingleArtifact.MERGED_MANIFEST)
        tasks.register<Copy>("copy${variant.name.replaceFirstChar { it.uppercase() }}Manifest") {
            from(mergedManifest)
            into(layout.buildDirectory.dir("reports/manifests/${variant.name}"))
        }
    }
}
```

`from(mergedManifest)` 保留 Producer 依赖信息，Gradle 可以安排先生成清单再复制。不要提前 `.get().asFile` 读取尚未生成的文件；也不要手工把任务挂到某个偶然存在的内部 merge 任务名。若要修改产物，使用对应版本的 Artifacts transform API，声明输入/输出，而不是覆盖 AGP 原始输出目录。

### 12.4 处理器与插件迁移顺序

先固定 Wrapper/JDK/AGP，迁移公开 DSL，再处理 Kotlin 与代码生成链，最后检查配置缓存和任务缓存。Javac/KAPT 处理器与 KSP 不是配置名不同的同一机制：前者面向 Java 模型/桩，后者读取 Kotlin 符号。Dagger KSP 依赖其他处理器生成类型时，整个链必须使用兼容后端。

参考：[Gradle 9.3.1 自定义插件](https://docs.gradle.org/9.3.1/userguide/custom_plugins.html)、[自定义任务](https://docs.gradle.org/9.3.1/userguide/implementing_custom_tasks.html)、[AGP 公开扩展点](https://developer.android.com/build/extend-agp)、[内置 Kotlin](https://developer.android.com/build/migrate-to-built-in-kotlin)。

## 13. 面试常见问题

### 13.1 基础问题

**Q1: Gradle 构建生命周期？**

```text
1. 初始化阶段 - 解析 settings.gradle，创建 Project
2. 配置阶段 - 解析 build.gradle，创建 Task，构建 DAG
3. 执行阶段 - 按 DAG 顺序执行 Task
```

**Q2: implementation 和 api 的区别？**

```text
implementation:
• 编译和运行时都需要
• 不传递给消费者模块

api:
• 编译和运行时都需要
• 会传递给消费者模块
```

**Q3: Gradle 守护进程的作用？**

```text
• 保持 JVM 运行，避免每次启动
• 缓存构建状态
• 大幅提升构建速度 (2-3x)
```

### 13.2 进阶问题

**Q4: AGP 构建流程？**

```text
1. AAPT2 编译资源
2. Java/Kotlin 编译
3. DEX 编译 (d8)
4. APK 打包
5. 对齐 (zipalign；手工使用 apksigner 时必须先对齐)
6. 签名并验证 (apksigner；签名后不要修改 APK)
```

顺序依据：[apksigner](https://developer.android.com/tools/apksigner)。AGP 会管理相应任务，上述是概念流程，不代表所有任务串行执行。

**Q5: 如何解决依赖冲突？**

```text
1. 查看依赖树: ./gradlew dependencies
2. 强制版本: strictly("1.0.0")
3. 排除依赖: exclude(group, module)
4. 全局强制: resolutionStrategy.force()
```

**Q6: 构建优化方法？**

```text
1. 启用守护进程和并行构建
2. 使用 KSP 替代 KAPT
3. 启用 Configuration Cache
4. 增加内存配置
5. 禁用不需要的 Build Features
```

---

## 总结

本文详细讲解了 Android Gradle & AGP 的核心知识点：

1. **Gradle 核心原理** - 守护进程、增量构建
2. **构建生命周期** - 初始化、配置、执行
3. **Project 与 Task** - 构建基本单元
4. **build.gradle** - 完整配置解析
5. **AGP 构建流程** - 从源码到 APK
6. **构建优化** - 实战优化技巧

掌握这些知识点对于 Android 面试和项目构建优化都至关重要。

---
