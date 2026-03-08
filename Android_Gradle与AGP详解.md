# Android Gradle & AGP 完全指南

> 作者：OpenClaw | 日期：2026-03-08

---

## 目录

1. [Gradle 基础](#1-gradle-基础)
   - 1.1 [什么是 Gradle](#11-什么是-gradle)
   - 1.2 [Gradle 构建生命周期](#12-gradle-构建生命周期)
   - 1.3 [Project 与 Task](#13-project-与-task)
   - 1.4 [Gradle Wrapper](#14-gradle-wrapper)
2. [Gradle 构建流程](#2-gradle-构建流程)
   - 2.1 [初始化阶段](#21-初始化阶段)
   - 2.2 [配置阶段](#22-配置阶段)
   - 2.3 [执行阶段](#23-执行阶段)
3. [build.gradle 详解](#3-buildgradle-详解)
   - 3.1 [依赖类型](#31-依赖类型)
   - 3.2 [依赖冲突解决](#32-依赖冲突解决)
4. [AGP 构建流程](#4-agp-构建流程)
   - 4.1 [AGP 版本演进](#41-agp-版本演进)
   - 4.2 [完整构建流程图](#42-完整构建流程图)
5. [打包流程详解](#5-打包流程详解)
   - 5.1 [AAPT2 资源编译](#51-aapt2-资源编译)
   - 5.2 [Java/Kotlin 编译](#52-javakotlin-编译)
   - 5.3 [DEX 编译](#53-dex-编译)
   - 5.4 [APK 签名](#54-apk-签名)
6. [构建变体](#6-构建变体)
   - 6.1 [Build Types](#61-build-types)
   - 6.2 [Product Flavors](#62-product-flavors)
   - 6.3 [Build Variants](#63-build-variants)
7. [构建优化](#7-构建优化)
   - 7.1 [Gradle 守护进程](#71-gradle-守护进程)
   - 7.2 [构建缓存](#72-构建缓存)
   - 7.3 [KSP vs KAPT](#73-ksp-vs-kapt)
8. [常见问题](#8-常见问题)
9. [总结](#9-总结)

---

## 1. Gradle 基础

### 1.1 什么是 Gradle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Gradle 概述                                         │
└─────────────────────────────────────────────────────────────────────────────┘

Gradle 是一个基于 JVM 的构建自动化工具:
- 基于 Groovy/Kotlin DSL 编写构建脚本
- 支持增量构建、构建缓存
- 强大的依赖管理
- 可扩展的插件系统
```

### 1.2 Gradle 构建生命周期

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Gradle 构建生命周期                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  gradle build
       │
       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 初始化阶段 (Initialization)                                         │
  │     - 解析 settings.gradle                                              │
  │     - 确定哪些 Project 参与构建                                         │
  │     - 创建 Project 对象                                                 │
  └─────────────────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. 配置阶段 (Configuration)                                            │
  │     - 解析所有 build.gradle                                             │
  │     - 创建和配置所有 Task                                               │
  │     - 构建 Task 依赖图 (DAG)                                            │
  └─────────────────────────────────────────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. 执行阶段 (Execution)                                                │
  │     - 根据 Task 依赖图执行 Task                                         │
  │     - 跳过 UP-TO-DATE 的 Task                                           │
  └─────────────────────────────────────────────────────────────────────────┘
       │
       ▼
  构建完成
```

### 1.3 Project 与 Task

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Project 与 Task 关系                                │
└─────────────────────────────────────────────────────────────────────────────┘

  Gradle 构建 = 多个 Project
  Project = 多个 Task
  Task = 最小执行单元

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Root Project                                                           │
  │  ├── app/ (Sub Project)                                                 │
  │  │   ├── compileJava Task                                               │
  │  │   ├── processResources Task                                          │
  │  │   └── assemble Task                                                  │
  │  │                                                                      │
  │  └── library/ (Sub Project)                                             │
  │      ├── compileJava Task                                               │
  │      └── assemble Task                                                  │
  └─────────────────────────────────────────────────────────────────────────┘


  Task 依赖图 (DAG):
  ─────────────────────────────────────────────────────────────────────────────

                        assemble
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
          package     bundleDebug   bundleRelease
              │            │            │
              ▼            ▼            ▼
          compileJava  compileJava  compileJava
```

### 1.4 Gradle Wrapper

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Gradle Wrapper                                      │
└─────────────────────────────────────────────────────────────────────────────┘

作用:
- 统一团队使用的 Gradle 版本
- 无需预先安装 Gradle
- 自动下载指定版本

项目结构:
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── gradlew           // Linux/Mac 脚本
├── gradlew.bat       // Windows 脚本
└── build.gradle

gradle-wrapper.properties:
distributionUrl=https\://services.gradle.org/distributions/gradle-8.0-bin.zip
```

---

## 2. Gradle 构建流程

### 2.1 初始化阶段

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         初始化阶段流程                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 查找 settings.gradle
  2. 读取 include 配置, 确定参与构建的模块
  3. 创建 Settings 对象
  4. 为每个模块创建 Project 对象

settings.gradle 示例:
─────────────────────────────────────────────────────────────────────────────

pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "MyApp"
include ':app'
include ':library'
```

### 2.2 配置阶段

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         配置阶段流程                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 解析所有 build.gradle 文件
  2. 执行脚本中的代码
  3. 创建和配置 Task
  4. 构建 Task 依赖图 (DAG)
  5. 触发 afterEvaluate 回调

注意: 配置阶段会执行 build.gradle 中的所有代码!
```

### 2.3 执行阶段

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         执行阶段流程                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 确定要执行的 Task 集合
  2. 检查 Task 状态:
     - UP-TO-DATE: 输入输出未变化，跳过
     - FROM-CACHE: 有缓存结果，跳过
     - SKIP: 条件不满足，跳过
     - EXECUTE: 需要执行
  3. 按依赖顺序执行 Task
  4. 执行 Task.doFirst / doLast 回调
```

---

## 3. build.gradle 详解

### 3.1 依赖类型

```groovy
dependencies {
    // implementation: 编译时依赖，不传递给依赖此模块的模块
    implementation 'androidx.core:core-ktx:1.12.0'
    
    // api: 编译时依赖，会传递给依赖此模块的模块
    api 'com.squareup.retrofit2:retrofit:2.9.0'
    
    // compileOnly: 仅编译时使用，不打包
    compileOnly 'org.projectlombok:lombok:1.18.30'
    
    // runtimeOnly: 仅运行时使用，编译时不可见
    runtimeOnly 'com.squareup.okhttp3:okhttp:4.12.0'
    
    // annotationProcessor / kapt: 注解处理器
    kapt 'com.github.bumptech.glide:compiler:4.16.0'
    
    // 测试依赖
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    
    // Debug 依赖
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}
```

### 3.2 依赖冲突解决

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         依赖冲突场景                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  依赖树:
  app
  ├── A (依赖 common:1.0)
  └── B (依赖 common:2.0)

  Gradle 默认策略: 选择最高版本 (common:2.0)


  强制指定版本:
  ─────────────────────────────────────────────────────────────────────────────

  dependencies {
      // 方式1: 强制版本
      implementation('com.example:common:1.0') {
          force = true
      }
      
      // 方式2: 排除传递依赖
      implementation('com.example:A') {
          exclude group: 'com.example', module: 'common'
      }
      
      // 方式3: 全局强制版本
      configurations.all {
          resolutionStrategy {
              force 'com.example:common:1.0'
          }
      }
  }

  查看依赖树:
  ─────────────────────────────────────────────────────────────────────────────

  ./gradlew app:dependencies
```

---

## 4. AGP 构建流程

### 4.1 AGP 版本演进

```
┌───────────────┬───────────────┬───────────────────────────────────────────┐
│  AGP 版本      │  Gradle 版本  │  重大变化                                 │
├───────────────┼───────────────┼───────────────────────────────────────────┤
│  3.0          │  4.1+         │  Transform API 引入                       │
├───────────────┼───────────────┼───────────────────────────────────────────┤
│  4.0          │  6.1+         │  Build Analyzer, Java 8+                 │
├───────────────┼───────────────┼───────────────────────────────────────────┤
│  7.0          │  7.0+         │  延迟任务初始化, V2 签名                   │
├───────────────┼───────────────┼───────────────────────────────────────────┤
│  8.0          │  8.0+         │  Transform API 废弃, 配置缓存稳定          │
├───────────────┼───────────────┼───────────────────────────────────────────┤
│  8.3+         │  8.4+         │  KSP 默认, 编译速度优化                   │
└───────────────┴───────────────┴───────────────────────────────────────────┘
```

### 4.2 完整构建流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGP 完整构建流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ./gradlew assembleDebug
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 加载项目和插件                                                       │
  │     - 解析 settings.gradle                                              │
  │     - 应用 Android 插件                                                 │
  │     - 配置 android {} 块                                                │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. 资源处理 (AAPT2)                                                     │
  │     ├── aapt2 compile: *.xml → *.flat                                  │
  │     ├── aapt2 link: *.flat → resources.pb                              │
  │     └── mergeResources: 合并所有资源                                    │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. 代码处理                                                             │
  │     ├── aidl → Java                                                     │
  │     ├── RenderScript → Java                                             │
  │     ├── 注解处理 (KAPT/KSP)                                             │
  │     ├── Java 编译 (javac): .java → .class                              │
  │     └── Kotlin 编译 (kotlinc): .kt → .class                            │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  4. DEX 编译                                                             │
  │     ├── class → dex (d8)                                                │
  │     └── 多 dex 处理 (如果方法数 > 65536)                                │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  5. 打包                                                                 │
  │     ├── 合并所有 dex                                                     │
  │     ├── 合并资源                                                        │
  │     ├── 合并 native 库                                                  │
  │     └── 生成未签名 APK                                                  │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  6. 签名                                                                 │
  │     ├── V1 签名 (JAR 签名)                                              │
  │     ├── V2 签名 (APK 签名方案 v2)                                       │
  │     ├── V3 签名 (APK 签名方案 v3)                                       │
  │     └── V4 签名 (ADB 增量安装)                                          │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  7. 对齐 (zipalign)                                                      │
  │     - 4 字节对齐，优化内存访问                                          │
  └─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
     最终 APK
```

---

## 5. 打包流程详解

### 5.1 AAPT2 资源编译

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AAPT2 编译流程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  AAPT2 (Android Asset Packaging Tool 2)

  1. 编译阶段 (compile):
     res/layout/main.xml → main.xml.flat  (二进制格式)

  2. 链接阶段 (link):
     *.flat → resources.pb + resource_table.pb

  优点:
  - 增量编译: 只编译变化的资源
  - 并行编译: 多个资源并行处理
  - 更快的链接: 预编译格式
```

### 5.2 Java/Kotlin 编译

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Java/Kotlin 编译流程                                │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 注解处理 (先于编译):
     @BindView, @Entity 等注解 → 生成代码

  2. Java 编译:
     .java ──► javac ──► .class

  3. Kotlin 编译:
     .kt ──► kotlinc ──► .class
```

### 5.3 DEX 编译

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEX 编译流程                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  .class ──► d8 ──► classes.dex

  D8 编译器 (替代 DX):
  - 更快的编译速度
  - 更小的 DEX 体积
  - 支持 Java 8+ 特性

  MultiDex:
  ─────────────────────────────────────────────────────────────────────────────
  当方法数超过 65536:
  classes.dex, classes2.dex, classes3.dex ...

  android {
      defaultConfig {
          multiDexEnabled true
      }
  }
```

### 5.4 APK 签名

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APK 签名方案                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  V1 签名 (JAR 签名):
  - META-INF/ 目录下的三个文件
  - 兼容 Android 7.0 以下

  V2 签名 (APK 签名方案 v2):
  - 签名数据在 ZIP 中央目录之前
  - 更快的验证速度
  - 更安全 (不能修改 APK)
  - Android 7.0+ 支持

  V3 签名:
  - 支持密钥轮换
  - Android 9.0+ 支持

  V4 签名:
  - 用于 ADB 增量安装
  - Android 11+ 支持

  推荐配置:
  ─────────────────────────────────────────────────────────────────────────────
  android {
      signingConfigs {
          release {
              storeFile file("keystore.jks")
              storePassword "password"
              keyAlias "my-key"
              keyPassword "password"
              v1SigningEnabled true
              v2SigningEnabled true
          }
      }
  }
```

---

## 6. 构建变体

### 6.1 Build Types

```groovy
android {
    buildTypes {
        debug {
            debuggable true
            minifyEnabled false
            applicationIdSuffix ".debug"
            versionNameSuffix "-debug"
        }
        
        release {
            debuggable false
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'),
                         'proguard-rules.pro'
        }
    }
}
```

### 6.2 Product Flavors

```groovy
android {
    flavorDimensions "channel", "env"
    
    productFlavors {
        // 渠道维度
        google { dimension "channel" }
        huawei { dimension "channel" }
        
        // 环境维度
        dev { dimension "env"; applicationIdSuffix ".dev" }
        prod { dimension "env" }
    }
}
```

### 6.3 Build Variants

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Build Variants 组合                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  Flavor Dimensions: channel, env
  Build Types: debug, release

  生成的 Variants:
  ─────────────────────────────────────────────────────────────────────────────
  googleDevDebug, googleDevRelease
  googleProdDebug, googleProdRelease
  huaweiDevDebug, huaweiDevRelease
  huaweiProdDebug, huaweiProdRelease
```

---

## 7. 构建优化

### 7.1 Gradle 守护进程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Gradle 守护进程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  作用:
  - 保持 JVM 运行，避免每次构建都启动 JVM
  - 缓存构建状态
  - 大幅提升构建速度

  配置 (gradle.properties):
  ─────────────────────────────────────────────────────────────────────────────
  org.gradle.daemon=true
  org.gradle.parallel=true
  org.gradle.caching=true
  org.gradle.configureondemand=true
  org.gradle.jvmargs=-Xmx4096m
```

### 7.2 构建缓存

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         构建缓存                                             │
└─────────────────────────────────────────────────────────────────────────────┘

  开启方式 (gradle.properties):
  ─────────────────────────────────────────────────────────────────────────────
  org.gradle.caching=true

  清除缓存:
  ─────────────────────────────────────────────────────────────────────────────
  ./gradlew cleanBuildCache
```

### 7.3 KSP vs KAPT

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KSP vs KAPT                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  KAPT (Kotlin Annotation Processing Tool):
  - 生成 Java 存根，然后 Java 处理
  - 编译速度慢
  - 兼容性好

  KSP (Kotlin Symbol Processing):
  - 直接处理 Kotlin 符号
  - 编译速度快 2x
  - AGP 8.3+ 默认推荐

  迁移:
  ─────────────────────────────────────────────────────────────────────────────
  // build.gradle
  plugins {
      id 'com.google.devtools.ksp' version '1.9.0-1.0.13'
  }
  
  dependencies {
      // kapt 'com.github.bumptech.glide:compiler:4.16.0'
      ksp 'com.github.bumptech.glide:compiler:4.16.0'
  }
```

---

## 8. 常见问题

### 8.1 Gradle 构建慢怎么办？

```
1. 开启守护进程和并行构建
   org.gradle.daemon=true
   org.gradle.parallel=true
   org.gradle.caching=true

2. 增加内存
   org.gradle.jvmargs=-Xmx4096m

3. 使用 KSP 替代 KAPT

4. 开启 Configuration Cache
   org.gradle.configuration-cache=true

5. 使用最新版 AGP 和 Gradle
```

### 8.2 依赖冲突怎么解决？

```
1. 查看依赖树:
   ./gradlew app:dependencies

2. 强制版本:
   implementation('xxx') { force = true }

3. 排除传递依赖:
   implementation('xxx') { exclude group: 'xxx' }
```

---

## 9. 总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Gradle & AGP 总结                                   │
└─────────────────────────────────────────────────────────────────────────────┘

核心概念:
- Gradle 生命周期: 初始化 → 配置 → 执行
- Project 与 Task: 构建的基本单元
- 依赖管理: implementation/api/compileOnly

AGP 构建流程:
- AAPT2 编译资源
- Java/Kotlin 编译
- DEX 编译 (d8)
- APK 打包签名

构建优化:
- Gradle 守护进程
- 构建缓存
- Configuration Cache
- KSP 替代 KAPT

构建变体:
- Build Types: debug/release
- Product Flavors: 多渠道/多环境
- Build Variants: 组合变体
```

---

*本文档由 OpenClaw 生成*
