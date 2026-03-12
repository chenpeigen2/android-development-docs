# Android Gradle & AGP 完全指南

> 作者：OpenClaw (Android 架构师) | 日期：2026-03-12
> 基于版本：Gradle 8.5+ / AGP 8.3+

## 目录

1. [概述](#1-概述)
2. [Gradle 核心原理](#2-gradle-核心原理)
3. [Gradle 构建生命周期](#3-gradle-构建生命周期)
4. [Project 与 Task 详解](#4-project-与-task-详解)
5. [Gradle Wrapper 机制](#5-gradle-wrapper-机制)
6. [build.gradle 完全解析](#6-buildgradle-完全解析)
7. [AGP 架构与版本演进](#7-agp-架构与版本演进)
8. [AGP 完整构建流程](#8-agp-完整构建流程)
9. [打包流程详解](#9-打包流程详解)
10. [构建变体与产品风味](#10-构建变体与产品风味)
11. [构建优化实战](#11-构建优化实战)
12. [自定义 Gradle 插件](#12-自定义-gradle-插件)
13. [面试常见问题](#13-面试常见问题)

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

| AGP 版本 | Gradle 版本 | JDK 版本 |
|---------|------------|---------|
| 8.0     | 8.0+       | 17      |
| 8.1     | 8.0+       | 17      |
| 8.2     | 8.2+       | 17      |
| 8.3     | 8.4+       | 17      |
| 8.4     | 8.6+       | 17      |
| 8.5     | 8.7+       | 17      |

---

## 2. Gradle 核心原理

### 2.1 Gradle 架构

```
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

```
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

```
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

### 3.2 生命周期回调

```kotlin
// 初始化阶段
gradle.settingsEvaluated {
    println("Settings evaluated!")
}

// 配置阶段
gradle.beforeProject {
    println("Before: ${it.name}")
}

gradle.afterProject {
    println("After: ${it.name}")
}

// 执行阶段
gradle.taskGraph.beforeTask {
    println("Before task: ${it.name}")
}

gradle.taskGraph.afterTask {
    println("After task: ${it.name}")
}
```

---

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

```
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

```
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
distributionUrl=https\://services.gradle.org/distributions/gradle-8.5-bin.zip
```

### 5.2 Wrapper 命令

```bash
# 生成 Wrapper
gradle wrapper

# 指定版本
gradle wrapper --gradle-version 8.5

# 升级版本
./gradlew wrapper --gradle-version 8.6
```

---

## 6. build.gradle 完全解析

### 6.1 根项目 build.gradle

```kotlin
// build.gradle.kts (根项目)

plugins {
    id("com.android.application") version "8.3.0" apply false
    id("com.android.library") version "8.3.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.22" apply false
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

tasks.register("clean", Delete::class) {
    delete(rootProject.buildDir)
}
```

### 6.2 应用模块 build.gradle

```kotlin
// app/build.gradle.kts

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.devtools.ksp")
}

android {
    namespace = "com.example.myapp"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
        }
        
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

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        viewBinding = true
        compose = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    
    api(project(":library"))
    
    ksp("com.google.dagger:hilt-compiler:2.50")
    
    testImplementation("junit:junit:4.13.2")
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}
```

### 6.3 依赖类型

| 依赖类型 | 说明 |
|---------|------|
| implementation | 编译和运行时都需要，不传递 |
| api | 编译和运行时都需要，会传递 |
| compileOnly | 仅编译时使用，不打包 |
| runtimeOnly | 仅运行时使用 |
| ksp | Kotlin 符号处理器 |
| testImplementation | 单元测试依赖 |
| debugImplementation | Debug 构建依赖 |

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

## 7. AGP 架构与版本演进

### 7.1 AGP 版本演进

| AGP 版本 | 重大变化 |
|---------|---------|
| 3.0 | Transform API 引入 |
| 4.0 | Build Analyzer, Java 8+ |
| 7.0 | 延迟任务初始化, V2 签名 |
| 8.0 | Transform API 废弃, 配置缓存 |
| 8.3+ | KSP 默认, 编译速度优化 |

### 7.2 AGP 核心扩展

```kotlin
// AppExtension - 应用配置
android {
    // 基本配置
    namespace = "com.example"
    compileSdk = 34
    
    // 默认配置
    defaultConfig {
        applicationId = "com.example"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
    
    // 签名配置
    signingConfigs {
        create("release") {
            storeFile = file("keystore.jks")
            storePassword = "password"
            keyAlias = "alias"
            keyPassword = "password"
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

```
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
│  6. 签名                                                     │
│     • V1 签名 (JAR)                                          │
│     • V2 签名 (APK 签名方案)                                 │
│     • V3 签名 (密钥轮换)                                     │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  7. 对齐 (zipalign)                                          │
│     • 4 字节对齐，优化内存访问                               │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
   最终 APK
```

---

## 9. 打包流程详解

### 9.1 AAPT2 资源编译

```
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

```
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

```
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

```
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

# 按需配置
org.gradle.configureondemand=true

# 增加内存
org.gradle.jvmargs=-Xmx4096m -XX:+HeapDumpOnOutOfMemoryError

# Configuration Cache (实验性)
org.gradle.configuration-cache=true
```

### 11.2 高级优化

```kotlin
// 1. 使用 KSP 替代 KAPT
plugins {
    id("com.google.devtools.ksp")
}

dependencies {
    // kapt("com.example:processor:1.0")
    ksp("com.example:processor:1.0")
}

// 2. 启用 Build Cache
android {
    buildFeatures {
        buildConfig = false  // 不需要时禁用
        aidl = false
        renderScript = false
    }
}

// 3. 优化资源
android {
    buildTypes {
        release {
            isShrinkResources = true  // 资源压缩
        }
    }
    
    packagingOptions {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}
```

### 11.3 构建速度对比

```
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

### 12.1 插件基础

```kotlin
// buildSrc/src/main/kotlin/MyPlugin.kt

class MyPlugin : Plugin<Project> {
    override fun apply(project: Project) {
        // 创建扩展
        val extension = project.extensions.create<MyExtension>("myPlugin")
        
        // 注册任务
        project.tasks.register("hello") {
            group = "custom"
            description = "Prints hello"
            
            doLast {
                println("Hello from MyPlugin!")
                println("Message: ${extension.message.get()}")
            }
        }
    }
}

// 扩展定义
interface MyExtension {
    val message: Property<String>
}
```

### 12.2 使用插件

```kotlin
// build.gradle.kts

plugins {
    id("my-plugin")
}

myPlugin {
    message.set("Hello, World!")
}
```

---

## 13. 面试常见问题

### 13.1 基础问题

**Q1: Gradle 构建生命周期？**

```
1. 初始化阶段 - 解析 settings.gradle，创建 Project
2. 配置阶段 - 解析 build.gradle，创建 Task，构建 DAG
3. 执行阶段 - 按 DAG 顺序执行 Task
```

**Q2: implementation 和 api 的区别？**

```
implementation:
• 编译和运行时都需要
• 不传递给消费者模块

api:
• 编译和运行时都需要
• 会传递给消费者模块
```

**Q3: Gradle 守护进程的作用？**

```
• 保持 JVM 运行，避免每次启动
• 缓存构建状态
• 大幅提升构建速度 (2-3x)
```

### 13.2 进阶问题

**Q4: AGP 构建流程？**

```
1. AAPT2 编译资源
2. Java/Kotlin 编译
3. DEX 编译 (d8)
4. APK 打包
5. 签名 (V1/V2/V3)
6. 对齐 (zipalign)
```

**Q5: 如何解决依赖冲突？**

```
1. 查看依赖树: ./gradlew dependencies
2. 强制版本: strictly("1.0.0")
3. 排除依赖: exclude(group, module)
4. 全局强制: resolutionStrategy.force()
```

**Q6: 构建优化方法？**

```
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

*文档更新时间: 2026-03-12*