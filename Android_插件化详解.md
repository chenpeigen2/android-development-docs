# Android 插件化详解

> 作者：OpenClaw | 日期：2026-03-11  
> 插件化架构完全指南 | 动态加载、类加载、资源加载

---

## 📚 目录

### 第一篇：插件化基础

**第 1 章 插件化概述**
- 1.1 [什么是插件化](#11-什么是插件化)
- 1.2 [插件化 vs 组件化](#12-插件化-vs-组件化)
- 1.3 [插件化 vs 热修复](#13-插件化-vs-热修复)
- 1.4 [应用场景](#14-应用场景)
- 1.5 [主流框架对比](#15-主流框架对比)

**第 2 章 插件化原理**
- 2.1 [ClassLoader 机制](#21-classloader-机制)
- 2.2 [双亲委派模型](#22-双亲委派模型)
- 2.3 [DexClassLoader 与 PathClassLoader](#23-dexclassloader-与-pathclassloader)
- 2.4 [类加载流程](#24-类加载流程)

**第 3 章 资源加载**
- 3.1 [Android 资源编译](#31-android-资源编译)
- 3.2 [Resources 与 AssetManager](#32-resources-与-assetmanager)
- 3.3 [插件资源加载方案](#33-插件资源加载方案)
- 3.4 [资源冲突解决](#34-资源冲突解决)

**第 4 章 四大组件插件化**
- 4.1 [Activity 插件化](#41-activity-插件化)
- 4.2 [Service 插件化](#42-service-插件化)
- 4.3 [BroadcastReceiver 插件化](#43-broadcastreceiver-插件化)
- 4.4 [ContentProvider 插件化](#44-contentprovider-插件化)

---

### 第二篇：插件化实现

**第 5 章 Activity 插件化详解**
- 5.1 [Activity 启动流程](#51-activity-启动流程)
- 5.2 [Hook IActivityManager](#52-hook-iactivitymanager)
- 5.3 [占坑 Activity 方案](#53-占坑-activity-方案)
- 5.4 [启动插件 Activity](#54-启动插件-activity)

**第 6 章 Service 插件化详解**
- 6.1 [Service 启动流程](#61-service-启动流程)
- 6.2 [代理 Service 方案](#62-代理-service-方案)
- 6.3 [动态代理实现](#63-动态代理实现)

**第 7 章 插件加载框架**
- 7.1 [插件 APK 加载](#71-插件-apk-加载)
- 7.2 [插件生命周期管理](#72-插件生命周期管理)
- 7.3 [插件通信机制](#73-插件通信机制)
- 7.4 [插件依赖管理](#74-插件依赖管理)

**第 8 章 主流框架源码分析**
- 8.1 [RePlugin 架构分析](#81-replugin-架构分析)
- 8.2 [VirtualAPK 架构分析](#82-virtualapk-架构分析)
- 8.3 [Shadow 架构分析](#83-shadow-架构分析)
- 8.4 [框架对比与选型](#84-框架对比与选型)

---

### 第三篇：插件化实战

**第 9 章 插件化项目实战**
- 9.1 [项目架构设计](#91-项目架构设计)
- 9.2 [宿主与插件开发](#92-宿主与插件开发)
- 9.3 [插件打包与发布](#93-插件打包与发布)
- 9.4 [插件版本管理](#94-插件版本管理)

**第 10 章 插件化踩坑指南**
- 10.1 [常见问题与解决方案](#101-常见问题与解决方案)
- 10.2 [兼容性问题](#102-兼容性问题)
- 10.3 [性能优化](#103-性能优化)
- 10.4 [调试技巧](#104-调试技巧)

**第 11 章 SystemUI 插件化方案**
- 11.1 [SystemUI 插件化概述](#111-systemui-插件化概述)
- 11.2 [SystemUI 插件化实现方案](#112-systemui-插件化实现方案)
- 11.3 [StatusBar 插件化实现](#113-statusbar-插件化实现)
- 11.4 [QuickSettings 插件化实现](#114-quicksettings-插件化实现)
- 11.5 [插件 IPC 通信](#115-插件-ipc-通信)
- 11.6 [插件安全机制](#116-插件安全机制)
- 11.7 [插件开发最佳实践](#117-插件开发最佳实践)
- 11.8 [实际案例：厂商定制 StatusBar](#118-实际案例厂商定制-statusbar)

---

### 第四篇：面试指南

**第 12 章 面试常见问题**
- 12.1 [插件化原理](#121-插件化原理)
- 12.2 [类加载机制](#122-类加载机制)
- 12.3 [资源加载](#123-资源加载)
- 12.4 [组件插件化](#124-组件插件化)
- 12.5 [框架对比](#125-框架对比)

---

## 第一篇：插件化基础

---

## 第 1 章 插件化概述

### 1.1 什么是插件化

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       插件化架构                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              宿主应用 (Host)                                 │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          插件管理框架                                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ 插件加载器  │  │ 资源管理器  │  │ 生命周期    │  │ 通信管理    │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                  │
│              │                     │                     │                  │
│              ▼                     ▼                     ▼                  │
│  ┌───────────────┐      ┌───────────────┐      ┌───────────────┐           │
│  │   插件 A      │      │   插件 B      │      │   插件 C      │           │
│  │   (APK)       │      │   (APK)       │      │   (APK)       │           │
│  │               │      │               │      │               │           │
│  │ - 功能模块1  │      │ - 功能模块2  │      │ - 功能模块3  │           │
│  │ - 独立打包   │      │ - 独立打包   │      │ - 独立打包   │           │
│  │ - 动态加载   │      │ - 动态加载   │      │ - 动态加载   │           │
│  └───────────────┘      └───────────────┘      └───────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘

核心特点：
1. 宿主应用独立运行
2. 插件可动态加载
3. 插件独立打包发布
4. 宿主与插件解耦
```

**插件化定义**：
- 将应用功能模块化，拆分为独立的插件 APK
- 宿主应用运行时动态加载插件
- 插件可以独立开发、测试、发布

### 1.2 插件化 vs 组件化

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    插件化 vs 组件化                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬────────────────────────┬────────────────────────┐
│       对比项      │        组件化          │         插件化         │
├──────────────────┼────────────────────────┼────────────────────────┤
│  编译方式        │   整体编译             │   独立编译             │
│  打包方式        │   一个 APK             │   多个 APK            │
│  发布方式        │   整体发布             │   插件独立发布         │
│  更新方式        │   整体更新             │   插件独立更新         │
│  加载时机        │   安装时               │   运行时动态加载       │
│  模块解耦        │   编译时解耦           │   运行时解耦           │
│  技术难度        │   ⭐⭐                 │   ⭐⭐⭐⭐⭐           │
│  灵活性          │   ⭐⭐⭐               │   ⭐⭐⭐⭐⭐           │
│  维护成本        │   ⭐⭐⭐               │   ⭐⭐⭐⭐             │
│  应用场景        │   中大型项目           │   超大型项目/平台      │
└──────────────────┴────────────────────────┴────────────────────────┘

组件化架构：
┌─────────────────────────────────────────────────────────────┐
│                        主工程 (App)                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              公共基础层 (Common/Base)                │   │
│  └─────────────────────────────────────────────────────┘   │
│         │              │              │                    │
│    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐              │
│    │ 模块 A  │    │ 模块 B  │    │ 模块 C  │              │
│    │(Module) │    │(Module) │    │(Module) │              │
│    └─────────┘    └─────────┘    └─────────┘              │
│         └──────────────┴──────────────┘                    │
│                          │                                  │
│                    编译时打包到同一个 APK                    │
└─────────────────────────────────────────────────────────────┘

插件化架构：
┌─────────────────────────────────────────────────────────────┐
│                        宿主 (Host)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   插件管理框架                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│              运行时动态加载                                 │
│         │              │              │                    │
│    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐              │
│    │ 插件 A  │    │ 插件 B  │    │ 插件 C  │              │
│    │ (APK)   │    │ (APK)   │    │ (APK)   │              │
│    └─────────┘    └─────────┘    └─────────┘              │
│         独立打包、独立发布、独立更新                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 插件化 vs 热修复

```
┌──────────────────┬────────────────────────┬────────────────────────┐
│       对比项      │         热修复         │         插件化         │
├──────────────────┼────────────────────────┼────────────────────────┤
│  目的            │   修复 Bug             │   功能扩展             │
│  更新范围        │   类/方法级别          │   模块/功能级别        │
│  更新大小        │   很小 (几 KB)         │   较大 (几 MB)         │
│  更新频率        │   紧急修复时           │   功能更新时           │
│  技术原理        │   类加载替换           │   插件动态加载         │
│  适用场景        │   线上紧急修复         │   功能动态扩展         │
│  灵活性          │   ⭐⭐                 │   ⭐⭐⭐⭐⭐           │
│  风险            │   较低                 │   较高                 │
└──────────────────┴────────────────────────┴────────────────────────┘
```

### 1.4 应用场景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       插件化应用场景                                        │
└─────────────────────────────────────────────────────────────────────────────┘

1. 功能动态扩展
   ┌─────────────┐
   │   电商平台   │
   └─────────────┘
   - 淘宝：双十一活动模块动态加载
   - 京东：秒杀活动模块动态下发
   - 拼多多：游戏模块按需加载

2. 模块独立开发
   ┌─────────────┐
   │   大型应用   │
   └─────────────┘
   - 360手机卫士：功能模块独立团队开发
   - 微信：小程序框架
   - 支付宝：生活服务模块

3. 功能按需加载
   ┌─────────────┐
   │   减小体积   │
   └─────────────┘
   - 首次安装包小
   - 按需下载功能模块
   - 不常用功能延迟加载

4. 业务隔离
   ┌─────────────┐
   │   团队协作   │
   └─────────────┘
   - 不同团队独立开发
   - 业务模块隔离
   - 降低耦合度
```

### 1.5 主流框架对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       主流插件化框架                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬────────────┬────────────┬────────────┬────────────┐
│     框架     │  RePlugin  │ VirtualAPK │   Shadow   │  DynamicAPK │
├──────────────┼────────────┼────────────┼────────────┼────────────┤
│  开发者      │   360      │   滴滴     │   腾讯     │   携程      │
│  开源时间    │   2017     │   2017     │   2019     │   2017      │
│  维护状态    │   活跃     │   停止     │   活跃     │   停止      │
│  Activity    │     ✅     │     ✅     │     ✅     │     ✅      │
│  Service     │     ✅     │     ✅     │     ✅     │     ✅      │
│  Receiver    │     ✅     │     ✅     │     ✅     │     ❌      │
│  Provider    │     ✅     │     ✅     │     ✅     │     ❌      │
│  资源隔离    │     ✅     │     ✅     │     ✅     │     ✅      │
│  增量更新    │     ✅     │     ❌     │     ✅     │     ❌      │
│  兼容性      │   ⭐⭐⭐⭐   │   ⭐⭐⭐⭐   │  ⭐⭐⭐⭐⭐  │   ⭐⭐⭐     │
│  接入难度    │     中     │     中     │     低     │     高      │
│  Android X   │     ✅     │     ✅     │     ✅     │     ❌      │
│  Kotlin      │     ✅     │     ✅     │     ✅     │     ❌      │
└──────────────┴────────────┴────────────┴────────────┴────────────┘

推荐选择：
- 新项目：Shadow（腾讯，官方推荐，兼容性最好）
- 老项目：RePlugin（360，稳定可靠）
- 学习研究：VirtualAPK（原理清晰，文档完善）
```

---

## 第 2 章 插件化原理

### 2.1 ClassLoader 机制

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Android ClassLoader 体系                              │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────┐
                        │   ClassLoader    │
                        └────────┬─────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
    ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
    │ BootClassLoader│    │ BaseDexClassLoader│    │ PathClassLoader │
    │               │    │               │    │               │
    │ - 核心 Java类│    │ - DexFile加载│    │ - 加载应用类  │
    │ - 系统引导类  │    │ - 基础实现    │    │ - 系统类加载器│
    └───────────────┘    └───────┬───────┘    └───────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            ┌───────────────┐         ┌───────────────┐
            │ PathClassLoader│         │DexClassLoader │
            │               │         │               │
            │- 加载已安装APK│         │- 加载外部DEX  │
            │- /data/app/   │         │- 插件APK加载  │
            └───────────────┘         └───────────────┘
```

### 2.2 双亲委派模型

```java
/**
 * 双亲委派模型
 */

// ClassLoader.loadClass() 源码
protected Class<?> loadClass(String name, boolean resolve) {
    // 1. 检查是否已加载
    Class<?> c = findLoadedClass(name);
    if (c == null) {
        try {
            if (parent != null) {
                // 2. 委托父加载器加载
                c = parent.loadClass(name, false);
            } else {
                // 3. 委托启动类加载器
                c = findBootstrapClassOrNull(name);
            }
        } catch (ClassNotFoundException e) {
            // 父加载器无法加载
        }
        
        if (c == null) {
            // 4. 自己加载
            c = findClass(name);
        }
    }
    return c;
}

// 双亲委派模型的作用：
// 1. 安全性：防止核心类被篡改
// 2. 唯一性：避免类重复加载
// 3. 层次性：类加载有明确的层次关系
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       双亲委派流程                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  应用类加载器                     扩展类加载器                    启动类加载器
       │                               │                               │
       │ loadClass("java.lang.String") │                               │
       │──────────────────────────────▶│                               │
       │                               │ loadClass()                   │
       │                               │──────────────────────────────▶│
       │                               │                               │
       │                               │         已加载? 返回           │
       │                               │◀──────────────────────────────│
       │         返回 Class            │                               │
       │◀──────────────────────────────│                               │
       │                               │                               │

流程：
1. 应用类加载器收到加载请求
2. 委托给父加载器（扩展类加载器）
3. 扩展类加载器委托给启动类加载器
4. 启动类加载器尝试加载
5. 如果无法加载，子加载器尝试加载
6. 都无法加载则抛出 ClassNotFoundException
```

### 2.3 DexClassLoader 与 PathClassLoader

```java
/**
 * PathClassLoader - 加载已安装的 APK
 */
public class PathClassLoader extends BaseDexClassLoader {
    public PathClassLoader(String dexPath, ClassLoader parent) {
        super(dexPath, null, null, parent);
    }
    
    // dexPath: /data/app/com.example.app-1/base.apk
    // 只能加载已安装应用的 dex 文件
}

/**
 * DexClassLoader - 加载外部 DEX/APK
 */
public class DexClassLoader extends BaseDexClassLoader {
    public DexClassLoader(String dexPath, 
                          String optimizedDirectory,
                          String librarySearchPath,
                          ClassLoader parent) {
        super(dexPath, optimizedDirectory, librarySearchPath, parent);
    }
    
    // dexPath: 插件 APK 路径
    // optimizedDirectory: DEX 优化目录（已废弃，Android 8.0+ 忽略）
    // librarySearchPath: Native 库路径
    // parent: 父类加载器
}

/**
 * 插件化中的使用
 */
public class PluginClassLoader {
    
    public static ClassLoader createPluginClassLoader(
            Context context, 
            String pluginApkPath) {
        
        // 插件的 DEX 路径
        String dexPath = pluginApkPath;
        
        // 优化目录（Android 8.0 以下需要）
        File optimizedDir = context.getDir("plugin_dex", Context.MODE_PRIVATE);
        
        // Native 库目录
        File libDir = context.getDir("plugin_lib", Context.MODE_PRIVATE);
        
        // 创建 DexClassLoader
        return new DexClassLoader(
            dexPath,
            optimizedDir.getAbsolutePath(),
            libDir.getAbsolutePath(),
            context.getClassLoader()  // 宿主的 ClassLoader 作为父加载器
        );
    }
}
```

### 2.4 类加载流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       类加载完整流程                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   加载       │───▶│   验证       │───▶│   准备       │───▶│   解析       │
│  Loading     │    │ Verification │    │ Preparation  │    │  Resolution  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                   │
                                                                   ▼
                                                        ┌──────────────┐
                                                        │   初始化     │
                                                        │Initialization│
                                                        └──────────────┘

1. 加载（Loading）
   - 通过 ClassLoader 读取 .class 文件
   - 将字节流转换为方法区的运行时数据结构
   - 生成 Class 对象

2. 验证（Verification）
   - 文件格式验证
   - 元数据验证
   - 字节码验证
   - 符号引用验证

3. 准备（Preparation）
   - 为类变量分配内存
   - 设置初始值（默认值）

4. 解析（Resolution）
   - 符号引用替换为直接引用

5. 初始化（Initialization）
   - 执行类构造器 <clinit>()
   - 初始化类变量
```

```java
/**
 * 插件类加载示例
 */
public class PluginLoader {
    
    private DexClassLoader pluginClassLoader;
    
    /**
     * 加载插件 APK
     */
    public void loadPlugin(Context context, String pluginPath) {
        // 1. 创建 ClassLoader
        pluginClassLoader = new DexClassLoader(
            pluginPath,
            context.getDir("dex", Context.MODE_PRIVATE).getAbsolutePath(),
            null,
            context.getClassLoader()
        );
        
        // 2. 加载插件类
        try {
            Class<?> pluginClass = pluginClassLoader.loadClass("com.plugin.MainPlugin");
            
            // 3. 创建实例
            Object instance = pluginClass.newInstance();
            
            // 4. 调用方法
            Method method = pluginClass.getMethod("doSomething");
            method.invoke(instance);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

## 第 3 章 资源加载

### 3.1 Android 资源编译

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Android 资源编译流程                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   资源文件   │───▶│    aapt      │───▶│  resources.  │───▶│    APK       │
│  res/ assets/│    │   编译       │    │     arsc     │    │   打包       │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘

aapt 编译过程：
1. 资源编译
   - XML 编译为二进制格式
   - 图片压缩
   - 生成资源 ID

2. 生成 R.java
   - 为每个资源生成常量 ID
   - 格式：0xPPTTNNNN
     - PP: Package ID（应用 0x7f，系统 0x01）
     - TT: Type ID（drawable、string 等）
     - NNNN: 资源序号

3. 生成 resources.arsc
   - 资源索引表
   - 资源 ID 到资源文件的映射
   - 支持多语言、多分辨率

资源 ID 结构：
┌────────────────────────────────────────────────────────────────┐
│              0x  7f    01    0001                              │
│                  │     │     │                                 │
│                  │     │     └── 资源序号（Entry ID）           │
│                  │     └──────── 资源类型（Type ID）            │
│                  └────────────── 包 ID（Package ID）           │
└────────────────────────────────────────────────────────────────┘
```

### 3.2 Resources 与 AssetManager

```java
/**
 * Resources 加载原理
 */

// 1. AssetManager 创建
AssetManager assetManager = new AssetManager();

// 2. 添加资源路径（反射调用）
Method addAssetPath = AssetManager.class.getDeclaredMethod(
    "addAssetPath", String.class);
addAssetPath.setAccessible(true);
addAssetPath.invoke(assetManager, apkPath);

// 3. 创建 Resources
Resources resources = new Resources(
    assetManager,
    displayMetrics,
    configuration
);

// 4. 加载资源
Drawable drawable = resources.getDrawable(R.drawable.icon);
String text = resources.getString(R.string.app_name);
```

```java
/**
 * 插件资源加载
 */
public class PluginResourceLoader {
    
    /**
     * 创建插件的 Resources
     */
    public static Resources loadPluginResources(Context context, String pluginApkPath) {
        try {
            // 1. 创建 AssetManager
            AssetManager assetManager = AssetManager.class.newInstance();
            
            // 2. 反射调用 addAssetPath
            Method addAssetPath = AssetManager.class.getDeclaredMethod(
                "addAssetPath", String.class);
            addAssetPath.setAccessible(true);
            addAssetPath.invoke(assetManager, pluginApkPath);
            
            // 3. 创建 Resources
            Resources hostResources = context.getResources();
            Resources pluginResources = new Resources(
                assetManager,
                hostResources.getDisplayMetrics(),
                hostResources.getConfiguration()
            );
            
            return pluginResources;
            
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}
```

### 3.3 插件资源加载方案

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       插件资源加载方案                                      │
└─────────────────────────────────────────────────────────────────────────────┘

方案一：合并资源（Shared Resources）
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐                                                            │
│  │  宿主资源   │                                                            │
│  └──────┬──────┘                                                            │
│         │ 合并                                                              │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────┐                               │
│  │            合并后的 Resources            │                               │
│  │  ┌───────────┐  ┌───────────┐           │                               │
│  │  │ 宿主资源  │  │ 插件资源  │           │                               │
│  │  └───────────┘  └───────────┘           │                               │
│  └─────────────────────────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘
优点：简单，插件可直接使用宿主资源
缺点：资源 ID 可能冲突，需要修改 aapt

方案二：独立资源（Separate Resources）
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐    ┌─────────────┐                                        │
│  │  宿主资源   │    │  插件资源   │                                        │
│  └──────┬──────┘    └──────┬──────┘                                        │
│         │                  │                                                │
│         ▼                  ▼                                                │
│  ┌─────────────┐    ┌─────────────┐                                        │
│  │ 宿主 Resources│   │ 插件 Resources│                                      │
│  └─────────────┘    └─────────────┘                                        │
│         │                  │                                                │
│         └────────┬─────────┘                                                │
│                  │ 根据上下文切换                                            │
│                  ▼                                                          │
│         ┌─────────────┐                                                    │
│         │   资源管理   │                                                    │
│         └─────────────┘                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
优点：资源隔离，ID 不会冲突
缺点：实现复杂，需要管理多个 Resources
```

```java
/**
 * 资源加载方案实现
 */

// 方案一：合并资源（修改 aapt，重新分配 ID）
// 使用 public.xml 固定资源 ID
// <?xml version="1.0" encoding="utf-8"?>
// <resources>
//     <public type="drawable" name="plugin_icon" id="0x7f010000" />
// </resources>

// 方案二：独立资源（推荐）
public class SeparateResourceLoader {
    
    // 宿主资源
    private Resources hostResources;
    
    // 插件资源映射
    private Map<String, Resources> pluginResourcesMap = new HashMap<>();
    
    /**
     * 加载插件资源
     */
    public void loadPlugin(String pluginPath, Context context) {
        Resources pluginResources = createPluginResources(context, pluginPath);
        pluginResourcesMap.put(pluginPath, pluginResources);
    }
    
    /**
     * 创建插件 Resources
     */
    private Resources createPluginResources(Context context, String pluginPath) {
        try {
            AssetManager assetManager = AssetManager.class.newInstance();
            Method addAssetPath = AssetManager.class.getDeclaredMethod(
                "addAssetPath", String.class);
            addAssetPath.setAccessible(true);
            addAssetPath.invoke(assetManager, pluginPath);
            
            Resources hostRes = context.getResources();
            return new Resources(
                assetManager,
                hostRes.getDisplayMetrics(),
                hostRes.getConfiguration()
            );
        } catch (Exception e) {
            return null;
        }
    }
    
    /**
     * 获取插件资源
     */
    public Resources getPluginResources(String pluginPath) {
        return pluginResourcesMap.get(pluginPath);
    }
}
```

### 3.4 资源冲突解决

```java
/**
 * 资源冲突问题与解决方案
 */

// 问题1：资源 ID 冲突
// 宿主和插件都有 R.drawable.icon

// 解决方案1：修改 Package ID
// 宿主：0x7f
// 插件1：0x70
// 插件2：0x71

// 解决方案2：资源前缀
// 宿主：R.drawable.host_icon
// 插件：R.drawable.plugin_icon

// 问题2：主题冲突
// 解决方案：插件使用独立主题
public class PluginActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // 使用插件的主题
        setTheme(R.style.PluginTheme);
        super.onCreate(savedInstanceState);
    }
}

// 问题3：样式冲突
// 解决方案：使用独立命名空间
// 宿主样式：style/AppTheme.Host
// 插件样式：style/AppTheme.Plugin
```

---

## 第 4 章 四大组件插件化

### 4.1 Activity 插件化

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Activity 插件化难点                                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. Activity 必须在 AndroidManifest.xml 中注册
   ┌─────────────────────────────────────────────────────────────────────────┐
   │  // 系统会检查 Activity 是否注册                                         │
   │  // 未注册会抛出 ActivityNotFoundException                              │
   │  startActivity(new Intent(this, PluginActivity.class));                 │
   └─────────────────────────────────────────────────────────────────────────┘

2. Activity 启动流程需要 Hook
   ┌─────────────────────────────────────────────────────────────────────────┐
   │  App ──▶ Instrumentation ──▶ AMN/AMS ──▶ ActivityStarter              │
   │                                          │                              │
   │                                          ▼                              │
   │                                    检查 Manifest                        │
   │                                          │                              │
   │                                    未注册则报错                         │
   └─────────────────────────────────────────────────────────────────────────┘

3. 解决方案：占坑 + 欺骗系统
   ┌─────────────────────────────────────────────────────────────────────────┐
   │  1. 在 Manifest 中预注册占坑 Activity（ProxyActivity）                  │
   │  2. 启动时用 ProxyActivity 欺骗系统                                      │
   │  3. 在合适时机替换为真实的插件 Activity                                   │
   └─────────────────────────────────────────────────────────────────────────┘
```

```xml
<!-- AndroidManifest.xml 预注册占坑 Activity -->
<application>
    <!-- 占坑 Activity -->
    <activity
        android:name=".proxy.ProxyActivity1"
        android:exported="false"
        android:launchMode="standard"
        android:theme="@style/PluginTheme" />
    
    <activity
        android:name=".proxy.ProxyActivity2"
        android:exported="false"
        android:launchMode="standard" />
    
    <!-- 更多占坑 Activity... -->
</application>
```

### 4.2 Service 插件化

```java
/**
 * Service 插件化方案
 */

// 代理 Service 方案
public class ProxyService extends Service {
    
    private Service pluginService;
    private String pluginServiceClassName;
    
    @Override
    public IBinder onBind(Intent intent) {
        return pluginService?.onBind(intent);
    }
    
    @Override
    public void onCreate() {
        super.onCreate();
        loadAndCreatePluginService();
    }
    
    private void loadAndCreatePluginService() {
        try {
            Class<?> serviceClass = pluginClassLoader.loadClass(pluginServiceClassName);
            pluginService = (Service) serviceClass.newInstance();
            
            // 反射调用 attach
            Method attach = Service.class.getDeclaredMethod(
                "attach", Context.class, ActivityThread.class, String.class, 
                IBinder.class, Application.class, Object.class);
            attach.setAccessible(true);
            attach.invoke(pluginService, this, null, null, null, getApplication(), null);
            
            pluginService.onCreate();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### 4.3 BroadcastReceiver 插件化

```java
/**
 * BroadcastReceiver 插件化
 */

// 动态注册方式（推荐）
public class PluginReceiverManager {
    
    public static void registerPluginReceiver(Context context, 
            String pluginApkPath, String receiverClassName, IntentFilter filter) {
        try {
            // 加载插件 Receiver
            DexClassLoader classLoader = new DexClassLoader(
                pluginApkPath, null, null, context.getClassLoader());
            Class<?> receiverClass = classLoader.loadClass(receiverClassName);
            BroadcastReceiver receiver = (BroadcastReceiver) receiverClass.newInstance();
            
            // 动态注册
            context.registerReceiver(receiver, filter);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

// 静态注册：解析插件 Manifest，提取 Receiver 信息，运行时注册
```

### 4.4 ContentProvider 插件化

```java
/**
 * ContentProvider 插件化
 */

// 代理 Provider 方案
public class ProxyProvider extends ContentProvider {
    
    private ContentProvider pluginProvider;
    
    @Override
    public boolean onCreate() {
        // 加载插件 Provider
        pluginProvider = loadPluginProvider();
        return pluginProvider != null && pluginProvider.onCreate();
    }
    
    @Override
    public Cursor query(Uri uri, String[] projection, String selection, 
            String[] selectionArgs, String sortOrder) {
        return pluginProvider?.query(uri, projection, selection, selectionArgs, sortOrder);
    }
    
    @Override
    public Uri insert(Uri uri, ContentValues values) {
        return pluginProvider?.insert(uri, values);
    }
    
    // ... 其他方法类似代理
}
```

---

## 第 5 章 Activity 插件化详解

### 5.1 Activity 启动流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Activity 启动流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Activity    │───▶│Instrumentation│───▶│   AMN/AMS    │───▶│ActivityStack │
│ startActivity│    │ execStartAct │    │  startActivity│    │  startActivity│
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                   │
                            ┌──────────────────────────────────────┘
                            ▼
                    ┌──────────────┐    ┌──────────────┐
                    │ 检查 Manifest │───▶│  创建 Activity│
                    │  是否注册    │    │  实例         │
                    └──────────────┘    └──────────────┘

Hook 点：
1. Instrumentation.execStartActivity()
2. ActivityManagerNative.getDefault()
3. ActivityThread.handleLaunchActivity()
```

### 5.2 Hook IActivityManager

```java
/**
 * Hook IActivityManager 实现插件 Activity 启动
 */
public class ActivityManagerHook {
    
    private static final String TAG = "ActivityManagerHook";
    
    /**
     * Hook ActivityManagerNative 的 gDefault
     */
    public static void hookActivityManager() throws Exception {
        // 1. 获取 ActivityManagerNative 的 gDefault 字段
        Class<?> amnClass = Class.forName("android.app.ActivityManagerNative");
        Field gDefaultField = amnClass.getDeclaredField("gDefault");
        gDefaultField.setAccessible(true);
        
        // 2. 获取 gDefault 对象
        Object gDefault = gDefaultField.get(null);
        
        // 3. 获取 Singleton 的 mInstance 字段
        Class<?> singletonClass = Class.forName("android.util.Singleton");
        Field mInstanceField = singletonClass.getDeclaredField("mInstance");
        mInstanceField.setAccessible(true);
        
        // 4. 获取原始的 IActivityManager
        Object originalIActivityManager = mInstanceField.get(gDefault);
        
        // 5. 创建动态代理
        Object proxy = Proxy.newProxyInstance(
            Thread.currentThread().getContextClassLoader(),
            new Class<?>[] { Class.forName("android.app.IActivityManager") },
            new IActivityManagerHandler(originalIActivityManager)
        );
        
        // 6. 替换为代理对象
        mInstanceField.set(gDefault, proxy);
    }
    
    /**
     * IActivityManager 代理处理器
     */
    private static class IActivityManagerHandler implements InvocationHandler {
        
        private Object original;
        
        public IActivityManagerHandler(Object original) {
            this.original = original;
        }
        
        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            if ("startActivity".equals(method.getName())) {
                // 找到 Intent 参数
                Intent rawIntent = null;
                int index = 0;
                for (int i = 0; i < args.length; i++) {
                    if (args[i] instanceof Intent) {
                        rawIntent = (Intent) args[i];
                        index = i;
                        break;
                    }
                }
                
                // 创建代理 Intent
                Intent proxyIntent = new Intent();
                proxyIntent.setClassName("com.example.host", 
                    "com.example.host.proxy.ProxyActivity");
                proxyIntent.putExtra("plugin_intent", rawIntent);
                
                // 替换原始 Intent
                args[index] = proxyIntent;
            }
            
            return method.invoke(original, args);
        }
    }
}
```

### 5.3 占坑 Activity 方案

```java
/**
 * 占坑 Activity 方案实现
 */

// 1. 预注册占坑 Activity
// AndroidManifest.xml
<activity android:name=".proxy.ProxyActivity" android:exported="false" />

// 2. 占坑 Activity 实现
public class ProxyActivity extends Activity {
    
    private Activity pluginActivity;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // 获取真实的插件 Activity 类名
        Intent intent = getIntent();
        String pluginActivityClass = intent.getStringExtra("plugin_activity_class");
        String pluginApkPath = intent.getStringExtra("plugin_apk_path");
        
        // 加载插件 Activity
        pluginActivity = loadPluginActivity(pluginApkPath, pluginActivityClass);
        
        // 调用插件 Activity 的 onCreate
        pluginActivity.onCreate(savedInstanceState);
    }
    
    private Activity loadPluginActivity(String apkPath, String activityClass) {
        try {
            // 创建 ClassLoader
            DexClassLoader classLoader = new DexClassLoader(
                apkPath, 
                getDir("dex", MODE_PRIVATE).getAbsolutePath(),
                null, 
                getClassLoader()
            );
            
            // 加载类
            Class<?> clazz = classLoader.loadClass(activityClass);
            Activity activity = (Activity) clazz.newInstance();
            
            // 设置资源和上下文
            attachPluginActivity(activity, apkPath);
            
            return activity;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    // 代理所有生命周期方法
    @Override
    protected void onStart() {
        super.onStart();
        pluginActivity?.onStart();
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        pluginActivity?.onResume();
    }
    
    @Override
    protected void onPause() {
        pluginActivity?.onPause();
        super.onPause();
    }
    
    @Override
    protected void onDestroy() {
        pluginActivity?.onDestroy();
        super.onDestroy();
    }
}
```

### 5.4 启动插件 Activity

```java
/**
 * 启动插件 Activity
 */
public class PluginActivityLauncher {
    
    /**
     * 启动插件 Activity
     */
    public static void startPluginActivity(Context context, 
            String pluginApkPath, String pluginActivityClass) {
        
        Intent intent = new Intent(context, ProxyActivity.class);
        intent.putExtra("plugin_apk_path", pluginApkPath);
        intent.putExtra("plugin_activity_class", pluginActivityClass);
        
        context.startActivity(intent);
    }
    
    /**
     * 启动插件 Activity（带参数）
     */
    public static void startPluginActivity(Context context, 
            String pluginApkPath, String pluginActivityClass, Bundle extras) {
        
        Intent intent = new Intent(context, ProxyActivity.class);
        intent.putExtra("plugin_apk_path", pluginApkPath);
        intent.putExtra("plugin_activity_class", pluginActivityClass);
        intent.putExtra("plugin_extras", extras);
        
        context.startActivity(intent);
    }
}

// 使用示例
PluginActivityLauncher.startPluginActivity(
    this,
    "/sdcard/plugin.apk",
    "com.plugin.MainActivity"
);
```

---

## 第 8 章 主流框架源码分析

### 8.1 RePlugin 架构分析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RePlugin 架构                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              RePlugin 架构                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        RePlugin Framework                              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │ PluginClient│  │PluginServer │  │PluginComm  │  │PluginLoader │  │  │
│  │  │ 客户端 API  │  │ 服务端管理  │  │ 进程通信    │  │ 类加载器    │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                  │
│              │                     │                     │                  │
│              ▼                     ▼                     ▼                  │
│  ┌───────────────┐      ┌───────────────┐      ┌───────────────┐           │
│  │   插件管理    │      │   类加载管理   │      │   资源管理    │           │
│  │ - 安装/卸载  │      │ - 独立 ClassL │      │ - 资源隔离    │           │
│  │ - 版本管理   │      │ - 类查找      │      │ - 资源加载    │           │
│  │ - 信息查询   │      │ - 类缓存      │      │ - 主题管理    │           │
│  └───────────────┘      └───────────────┘      └───────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘

特点：
1. 完整的四大组件支持
2. 独立的 ClassLoader 隔离
3. 资源隔离方案
4. 支持增量更新
5. Hook 点少，稳定性好
```

### 8.2 Shadow 架构分析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Shadow 架构（腾讯）                                   │
└─────────────────────────────────────────────────────────────────────────────┘

特点：
1. 零反射实现
2. 完全避开 Hook 系统
3. 使用动态代理 + 桩代码
4. 兼容性最好
5. 腾讯官方推荐

核心组件：
1. PluginManager：插件管理
2. PluginLoader：插件加载
3. PluginRuntime：运行时环境
4. ComponentManager：组件管理

优势：
- 不 Hook 系统 API
- 动态代理替代反射
- 兼容性极高
- 支持热更新
```

### 8.3 框架对比与选型

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       框架选型建议                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────────────────────────────────────────────────────┐
│    场景      │                         推荐方案                            │
├──────────────┼──────────────────────────────────────────────────────────────┤
│  新项目      │  Shadow（腾讯官方，兼容性最好，维护活跃）                     │
│  老项目      │  RePlugin（360，稳定性好，文档完善）                         │
│  学习研究    │  VirtualAPK（原理清晰，适合学习）                            │
│  快速集成    │  Shadow（接入简单，零反射）                                  │
│  高兼容要求  │  Shadow（支持 Android 14+）                                 │
│  大型项目    │  RePlugin（功能完整，生态完善）                              │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

---

## 第 10 章 插件化踩坑指南

### 10.1 常见问题与解决方案

```java
/**
 * 常见问题
 */

// 问题1：ClassNotFoundException
// 原因：ClassLoader 未正确设置
// 解决：确保使用插件的 ClassLoader
Class<?> clazz = pluginClassLoader.loadClass("com.plugin.PluginClass");

// 问题2：NotFoundException（资源找不到）
// 原因：使用了错误的 Resources
// 解决：使用插件的 Resources
Resources pluginRes = pluginResourceManager.getResources(pluginPath);
Drawable drawable = pluginRes.getDrawable(R.drawable.plugin_icon);

// 问题3：ClassCastException
// 原因：类由不同 ClassLoader 加载
// 解决：统一使用插件 ClassLoader 加载

// 问题4：So 文件加载失败
// 原因：So 文件路径未正确设置
// 解决：设置正确的 libraryPath
new DexClassLoader(dexPath, optimizedDir, libPath, parent);
```

### 10.2 兼容性问题

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Android 版本兼容性                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────────────────────────────────────────────────────┐
│  Android版本 │                       兼容性问题                             │
├──────────────┼──────────────────────────────────────────────────────────────┤
│  Android 9   │  限制非 SDK 接口调用，许多 Hook 点被禁用                      │
│  Android 10  │  更严格的隐藏 API 限制，需要使用公开 API                      │
│  Android 11  │  强制分区存储，插件文件访问受限                               │
│  Android 12  │  更严格的组件导出限制                                        │
│  Android 13  │  预定义的 Intent 需要声明                                    │
└──────────────┴──────────────────────────────────────────────────────────────┘

解决方案：
1. 使用 Shadow 框架（零反射，无 Hook）
2. 减少对系统 API 的依赖
3. 使用官方推荐的方式实现功能
```

---

## 第 18 章 面试常见问题

### 18.1 插件化原理

**Q1: 什么是插件化？为什么需要插件化？**

**A:**

插件化是将应用功能拆分为独立的插件 APK，宿主运行时动态加载的技术。

**应用场景**：
1. 功能动态扩展（电商活动模块）
2. 减小安装包体积
3. 模块独立开发
4. 热更新能力

**Q2: 插件化和组件化有什么区别？**

**A:**

| 对比项 | 组件化 | 插件化 |
|-------|-------|-------|
| 编译 | 整体编译 | 独立编译 |
| 打包 | 一个 APK | 多个 APK |
| 更新 | 整体更新 | 插件独立更新 |
| 加载 | 安装时 | 运行时动态 |

### 18.2 类加载机制

**Q3: 解释一下双亲委派模型？**

**A:**

```
加载流程：
1. 检查类是否已加载
2. 委托父加载器加载
3. 父加载器无法加载时，自己加载
4. 都无法加载则抛出 ClassNotFoundException

作用：
1. 安全性：防止核心类被篡改
2. 唯一性：避免类重复加载
```

**Q4: PathClassLoader 和 DexClassLoader 的区别？**

**A:**

| 对比项 | PathClassLoader | DexClassLoader |
|-------|----------------|----------------|
| 用途 | 加载已安装 APK | 加载外部 DEX/APK |
| 路径 | /data/app/ | 任意路径 |
| 场景 | 应用启动 | 插件化/热修复 |

### 18.3 资源加载

**Q5: 插件如何加载资源？如何解决资源冲突？**

**A:**

```java
// 资源加载
AssetManager assetManager = AssetManager.class.newInstance();
Method addAssetPath = AssetManager.class.getDeclaredMethod("addAssetPath", String.class);
addAssetPath.invoke(assetManager, pluginApkPath);
Resources resources = new Resources(assetManager, metrics, config);

// 解决冲突
// 方案1：修改 Package ID（宿主 0x7f，插件 0x70）
// 方案2：资源前缀命名
// 方案3：独立 Resources 管理
```

### 18.4 组件插件化

**Q6: Activity 插件化的原理？**

**A:**

1. **占坑方案**：预注册占坑 Activity
2. **Hook AMS**：替换 Intent 中的 Activity 为占坑 Activity
3. **替换回真实 Activity**：在 ActivityThread 加载时替换

```
启动流程：
startActivity(PluginActivity)
       ↓
Hook: 替换为 ProxyActivity
       ↓
AMS: 检查 ProxyActivity 已注册 ✓
       ↓
ActivityThread: 替换回 PluginActivity
       ↓
加载插件 Activity 类并实例化
```

### 18.5 框架对比

**Q7: 主流插件化框架对比？**

**A:**

| 框架 | 开发者 | 特点 | 推荐场景 |
|------|-------|------|---------|
| Shadow | 腾讯 | 零反射，兼容性最好 | 新项目 |
| RePlugin | 360 | 功能完整，稳定 | 大型项目 |
| VirtualAPK | 滴滴 | 原理清晰 | 学习研究 |

---

## 第 11 章 SystemUI 插件化方案

### 11.1 SystemUI 插件化概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SystemUI 插件化架构                                   │
└─────────────────────────────────────────────────────────────────────────────┘

为什么 SystemUI 需要插件化：
1. 厂商定制 - 不同厂商需要不同的 UI 风格
2. 快速迭代 - 无需重新编译 SystemUI
3. 模块解耦 - 功能模块独立开发
4. 动态下发 - 可通过应用商店更新

SystemUI 插件化特点：
• 系统级权限 - 需要系统签名或特权
• 独立进程 - 插件运行在独立进程
• IPC 通信 - 通过 Binder 与 SystemUI 通信
• 资源隔离 - 插件资源独立加载

架构图：
─────────────────────────────────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    SystemUI Process                                  │ │
│   │                                                                      │ │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│   │   │ PluginManager│  │ StatusBar    │  │ NavigationBar│            │ │
│   │   │              │  │              │  │              │            │ │
│   │   │ • 加载插件   │  │ • 状态栏视图 │  │ • 导航栏视图 │            │ │
│   │   │ • 管理生命周期│ │ • 通知管理   │  │ • 按键处理   │            │ │
│   │   │ • IPC 通信   │  │ • QuickSettings│ │ • 手势导航   │            │ │
│   │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │ │
│   │          │                 │                 │                      │ │
│   │          │                 │                 │                      │ │
│   │          └─────────────────┼─────────────────┘                      │ │
│   │                            │ Binder IPC                            │ │
│   │                            │                                        │ │
│   └────────────────────────────┼────────────────────────────────────────┘ │
│                                │                                          │
│                                ▼                                          │
│   ┌───────────────────────────────────────────────────────────────────────┐│
│   │                    Plugin Process (独立进程)                         ││
│   │                                                                        ││
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              ││
│   │   │ Plugin A     │  │ Plugin B     │  │ Plugin C     │              ││
│   │   │ (时钟插件)   │  │ (天气插件)   │  │ (音乐插件)   │              ││
│   │   │              │  │              │  │              │              ││
│   │   │ • 自定义视图 │  │ • 天气数据   │  │ • 播放控制   │              ││
│   │   │ • 事件处理   │  │ • UI 更新    │  │ • 进度显示   │              ││
│   │   └──────────────┘  └──────────────┘  └──────────────┘              ││
│   │                                                                        ││
│   └────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 PluginManager 源码详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SystemUI PluginManager 完整架构                          │
└─────────────────────────────────────────────────────────────────────────────┘

源码位置：frameworks/base/packages/SystemUI/src/com/android/systemui/plugins/

核心类：
├── PluginManager.java          # 插件管理器主类
├── PluginInstance.java         # 插件实例管理
├── PluginFactory.java          # 插件工厂
├── PluginContext.java          # 插件专用 Context
├── PluginClassLoader.java      # 插件类加载器
└── PluginActionManager.java    # 插件动作管理
```

```java
/**
 * PluginManager - 插件管理器完整源码分析
 * 位置：frameworks/base/packages/SystemUI/src/com/android/systemui/plugins/PluginManager.java
 */
public class PluginManager {
    private static final String TAG = "PluginManager";
    
    // 插件 Action
    public static final String PLUGIN_ACTION = "com.android.systemui.action.PLUGIN";
    
    // 插件权限
    public static final String PLUGIN_PERMISSION = "com.android.systemui.permission.PLUGIN";
    
    // 单例
    private static PluginManager sInstance;
    
    // 上下文
    private final Context mContext;
    
    // 包管理器
    private final PackageManager mPm;
    
    // 插件监听器映射
    private final ArrayMap<Class<?>, PluginListener<?>> mPlugins;
    
    // 插件实例映射
    private final ArrayMap<Class<?>, PluginInstance<?>> mPluginInstances;
    
    // 插件包名映射
    private final ArrayMap<String, PluginInstance<?>> mPackageInstances;
    
    // 插件版本
    private final int mPluginVersion;
    
    // 是否已连接
    private boolean mConnected;
    
    /**
     * 获取单例
     */
    public static PluginManager getInstance(Context context) {
        if (sInstance == null) {
            sInstance = new PluginManager(context.getApplicationContext());
        }
        return sInstance;
    }
    
    /**
     * 构造函数
     */
    private PluginManager(Context context) {
        mContext = context;
        mPm = context.getPackageManager();
        mPlugins = new ArrayMap<>();
        mPluginInstances = new ArrayMap<>();
        mPackageInstances = new ArrayMap<>();
        
        // 获取当前插件版本
        mPluginVersion = getVersion(mContext);
        
        // 注册包安装/卸载监听
        registerPackageReceiver();
    }
    
    /**
     * 注册插件监听器
     * @param listener 监听器
     * @param cls 插件接口类
     */
    public <T extends Plugin> void addPluginListener(
            PluginListener<T> listener, Class<T> cls) {
        addPluginListener(listener, cls, false);
    }
    
    /**
     * 注册插件监听器 (完整版)
     * @param listener 监听器
     * @param cls 插件接口类
     * @param allowMultiple 是否允许多个插件
     */
    public <T extends Plugin> void addPluginListener(
            PluginListener<T> listener, Class<T> cls, boolean allowMultiple) {
        
        // 1. 创建查询 Intent
        Intent intent = new Intent(PLUGIN_ACTION);
        intent.addCategory(cls.getName());
        
        // 2. 查询匹配的插件服务
        List<ResolveInfo> resolves = mPm.queryIntentServices(
                intent, PackageManager.GET_META_DATA);
        
        Log.d(TAG, "Found " + resolves.size() + " plugins for " + cls.getName());
        
        // 3. 遍历并连接插件
        for (ResolveInfo resolve : resolves) {
            // 检查权限
            if (!checkPermission(resolve.serviceInfo.packageName)) {
                Log.w(TAG, "Plugin " + resolve.serviceInfo.packageName 
                        + " doesn't have permission");
                continue;
            }
            
            // 检查版本
            if (!checkVersion(resolve.serviceInfo)) {
                Log.w(TAG, "Plugin " + resolve.serviceInfo.packageName 
                        + " version mismatch");
                continue;
            }
            
            // 创建插件实例
            PluginInstance<T> instance = createPluginInstance(cls, resolve);
            if (instance != null) {
                // 连接插件
                instance.connect(listener);
                
                mPluginInstances.put(cls, instance);
                mPackageInstances.put(resolve.serviceInfo.packageName, instance);
                
                // 如果不允许多个，只连接第一个
                if (!allowMultiple) {
                    break;
                }
            }
        }
        
        // 4. 保存监听器
        mPlugins.put(cls, listener);
    }
    
    /**
     * 创建插件实例
     */
    private <T extends Plugin> PluginInstance<T> createPluginInstance(
            Class<T> cls, ResolveInfo resolve) {
        
        ComponentName component = new ComponentName(
                resolve.serviceInfo.packageName, 
                resolve.serviceInfo.name);
        
        return new PluginInstance<>(
                mContext, 
                cls, 
                component,
                resolve.serviceInfo.applicationInfo);
    }
    
    /**
     * 检查插件权限
     */
    private boolean checkPermission(String packageName) {
        int result = mPm.checkPermission(PLUGIN_PERMISSION, packageName);
        return result == PackageManager.PERMISSION_GRANTED;
    }
    
    /**
     * 检查插件版本
     */
    private boolean checkVersion(ServiceInfo serviceInfo) {
        Bundle metaData = serviceInfo.metaData;
        if (metaData == null) {
            return false;
        }
        
        int version = metaData.getInt("com.android.systemui.plugins.version", 0);
        return version >= mPluginVersion;
    }
    
    /**
     * 获取当前插件版本
     */
    private int getVersion(Context context) {
        try {
            ApplicationInfo info = context.getApplicationInfo();
            Bundle metaData = info.metaData;
            if (metaData != null) {
                return metaData.getInt("com.android.systemui.plugins.version", 1);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error getting plugin version", e);
        }
        return 1;
    }
    
    /**
     * 注册包安装/卸载监听
     */
    private void registerPackageReceiver() {
        IntentFilter filter = new IntentFilter();
        filter.addAction(Intent.ACTION_PACKAGE_ADDED);
        filter.addAction(Intent.ACTION_PACKAGE_CHANGED);
        filter.addAction(Intent.ACTION_PACKAGE_REMOVED);
        filter.addDataScheme("package");
        
        mContext.registerReceiver(new PackageReceiver(), filter);
    }
    
    /**
     * 包变化接收器
     */
    private class PackageReceiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            String packageName = intent.getData().getSchemeSpecificPart();
            
            PluginInstance<?> instance = mPackageInstances.get(packageName);
            if (instance != null) {
                // 插件包变化，断开并重新连接
                instance.disconnect();
                mPackageInstances.remove(packageName);
                
                // 重新加载插件
                reloadPlugins();
            }
        }
    }
}
```

### 11.3 PluginInstance - 插件实例管理

```java
/**
 * PluginInstance - 插件实例管理
 * 位置：frameworks/base/packages/SystemUI/src/com/android/systemui/plugins/PluginInstance.java
 * 
 * 职责：
 * 1. 创建插件 Context
 * 2. 创建插件 ClassLoader
 * 3. 加载插件类
 * 4. 管理插件生命周期
 */
public class PluginInstance<T extends Plugin> {
    private static final String TAG = "PluginInstance";
    
    // SystemUI Context
    private final Context mSystemUIContext;
    
    // 插件接口类
    private final Class<T> mPluginClass;
    
    // 插件组件名
    private final ComponentName mComponent;
    
    // 插件 ApplicationInfo
    private final ApplicationInfo mPluginAppInfo;
    
    // 插件 Context (独立创建)
    private Context mPluginContext;
    
    // 插件 ClassLoader (独立创建)
    private ClassLoader mPluginClassLoader;
    
    // 插件实例
    private T mPluginInstance;
    
    // 插件监听器
    private PluginListener<T> mListener;
    
    // 是否已连接
    private boolean mConnected;
    
    /**
     * 构造函数
     */
    public PluginInstance(Context context, Class<T> cls, 
            ComponentName component, ApplicationInfo appInfo) {
        mSystemUIContext = context;
        mPluginClass = cls;
        mComponent = component;
        mPluginAppInfo = appInfo;
    }
    
    /**
     * 连接插件
     */
    public void connect(PluginListener<T> listener) {
        mListener = listener;
        mConnected = true;
        
        try {
            // 1. 创建插件 ClassLoader
            mPluginClassLoader = createPluginClassLoader();
            
            // 2. 创建插件 Context
            mPluginContext = createPluginContext();
            
            // 3. 加载插件类
            Class<?> pluginClass = mPluginClassLoader.loadClass(mComponent.getClassName());
            
            // 4. 实例化插件
            mPluginInstance = (T) pluginClass.getDeclaredConstructor().newInstance();
            
            // 5. 调用 onCreate
            mPluginInstance.onCreate(mPluginContext, mListener);
            
            // 6. 通知连接成功
            mListener.onPluginConnected(mPluginInstance);
            
            Log.d(TAG, "Plugin connected: " + mComponent.getClassName());
            
        } catch (Exception e) {
            Log.e(TAG, "Error connecting plugin", e);
            mConnected = false;
        }
    }
    
    /**
     * 断开插件
     */
    public void disconnect() {
        if (mPluginInstance != null) {
            mPluginInstance.onDestroy();
            
            if (mListener != null) {
                mListener.onPluginDisconnected(mPluginInstance);
            }
        }
        
        mConnected = false;
        mPluginInstance = null;
        mPluginContext = null;
        mPluginClassLoader = null;
    }
    
    /**
     * 创建插件 ClassLoader
     */
    private ClassLoader createPluginClassLoader() {
        // 获取插件 APK 路径
        String apkPath = mPluginAppInfo.sourceDir;
        
        // 获取优化目录
        String optimizedDir = mSystemUIContext.getCodeCacheDir().getAbsolutePath();
        
        // 获取 native 库目录
        String libPath = mPluginAppInfo.nativeLibraryDir;
        
        // 获取父 ClassLoader (SystemUI 的 ClassLoader)
        ClassLoader parent = mSystemUIContext.getClassLoader();
        
        // 创建 DexClassLoader
        return new DexClassLoader(apkPath, optimizedDir, libPath, parent);
    }
    
    /**
     * 创建插件 Context
     */
    private Context createPluginContext() {
        try {
            // 方式1: 使用 createPackageContext (推荐)
            Context pluginContext = mSystemUIContext.createPackageContext(
                    mComponent.getPackageName(),
                    Context.CONTEXT_INCLUDE_CODE | Context.CONTEXT_IGNORE_SECURITY);
            
            // 设置插件 ClassLoader
            // 注意: createPackageContext 会自动创建 ClassLoader
            // 但我们使用自己创建的 ClassLoader 以便更好地控制
            return new PluginContextWrapper(pluginContext, mPluginClassLoader);
            
        } catch (PackageManager.NameNotFoundException e) {
            Log.e(TAG, "Error creating plugin context", e);
            return null;
        }
    }
}
```

### 11.4 PluginContext 创建流程详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PluginContext 创建流程                                   │
└─────────────────────────────────────────────────────────────────────────────┘

创建流程：
─────────────────────────────────────────────────────────────────────────────

1. createPackageContext
   │
   ├─► ContextImpl.createPackageContext()
   │   │
   │   ├─► 创建 LoadedApk
   │   │   └─► 加载插件 APK 信息
   │   │
   │   ├─► 创建 ClassLoader
   │   │   └─► PathClassLoader (自动创建)
   │   │
   │   ├─► 创建 Resources
   │   │   └─► 加载插件资源
   │   │
   │   └─► 创建 ContextImpl
   │       └─► 绑定到插件包
   │
   └─► 返回插件 Context

2. 自定义 PluginContextWrapper
   │
   ├─► 包装原始 Context
   │
   ├─► 覆盖 getClassLoader()
   │   └─► 返回自定义 ClassLoader
   │
   ├─► 覆盖 getResources()
   │   └─► 返回插件资源
   │
   └─► 覆盖 getAssets()
       └─► 返回插件 AssetManager
```

```java
/**
 * PluginContextWrapper - 插件 Context 包装器
 * 
 * 作用：
 * 1. 隔离插件和宿主的 Context
 * 2. 自定义 ClassLoader
 * 3. 管理插件资源
 */
public class PluginContextWrapper extends ContextWrapper {
    private final ClassLoader mPluginClassLoader;
    private Resources mPluginResources;
    private AssetManager mPluginAssets;
    
    public PluginContextWrapper(Context base, ClassLoader classLoader) {
        super(base);
        mPluginClassLoader = classLoader;
    }
    
    @Override
    public ClassLoader getClassLoader() {
        return mPluginClassLoader;
    }
    
    @Override
    public Resources getResources() {
        if (mPluginResources == null) {
            mPluginResources = createPluginResources();
        }
        return mPluginResources;
    }
    
    @Override
    public AssetManager getAssets() {
        if (mPluginAssets == null) {
            mPluginAssets = createPluginAssets();
        }
        return mPluginAssets;
    }
    
    /**
     * 创建插件 Resources
     */
    private Resources createPluginResources() {
        try {
            // 获取插件 APK 路径
            String apkPath = getBaseContext().getPackageResourcePath();
            
            // 创建 AssetManager
            AssetManager assets = AssetManager.class.newInstance();
            
            // 添加插件资源路径
            Method addAssetPath = AssetManager.class.getDeclaredMethod(
                    "addAssetPath", String.class);
            addAssetPath.setAccessible(true);
            addAssetPath.invoke(assets, apkPath);
            
            // 获取 DisplayMetrics
            DisplayMetrics metrics = getBaseContext().getResources().getDisplayMetrics();
            
            // 获取 Configuration
            Configuration config = getBaseContext().getResources().getConfiguration();
            
            // 创建 Resources
            return new Resources(assets, metrics, config);
            
        } catch (Exception e) {
            Log.e("PluginContext", "Error creating plugin resources", e);
            return getBaseContext().getResources();
        }
    }
    
    /**
     * 创建插件 AssetManager
     */
    private AssetManager createPluginAssets() {
        try {
            AssetManager assets = AssetManager.class.newInstance();
            
            Method addAssetPath = AssetManager.class.getDeclaredMethod(
                    "addAssetPath", String.class);
            addAssetPath.setAccessible(true);
            addAssetPath.invoke(assets, getBaseContext().getPackageResourcePath());
            
            return assets;
            
        } catch (Exception e) {
            Log.e("PluginContext", "Error creating plugin assets", e);
            return getBaseContext().getAssets();
        }
    }
}
```

### 11.5 ClassLoader 创建流程详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    插件 ClassLoader 创建流程                                │
└─────────────────────────────────────────────────────────────────────────────┘

ClassLoader 层级结构：
─────────────────────────────────────────────────────────────────────────────

                    BootClassLoader (启动类加载器)
                           │
                           ▼
                PathClassLoader (SystemUI ClassLoader)
                           │
                           ▼
              DexClassLoader (插件 ClassLoader)
                           │
                           ▼
                    插件类加载

创建过程：
─────────────────────────────────────────────────────────────────────────────

1. 获取插件 APK 路径
   String apkPath = appInfo.sourceDir;
   // 例如: /data/app/com.example.plugin-1/base.apk

2. 获取优化目录
   String optimizedDir = context.getCodeCacheDir().getAbsolutePath();
   // 例如: /data/data/com.android.systemui/code_cache

3. 获取 Native 库目录
   String libPath = appInfo.nativeLibraryDir;
   // 例如: /data/app/com.example.plugin-1/lib/arm64

4. 获取父 ClassLoader
   ClassLoader parent = context.getClassLoader();
   // SystemUI 的 PathClassLoader

5. 创建 DexClassLoader
   ClassLoader pluginClassLoader = new DexClassLoader(
       apkPath,           // 插件 APK 路径
       optimizedDir,      // DEX 优化目录
       libPath,           // Native 库目录
       parent             // 父 ClassLoader
   );

类加载顺序 (双亲委派):
─────────────────────────────────────────────────────────────────────────────

插件类加载请求: loadClass("com.plugin.PluginClass")
       │
       ▼
   DexClassLoader.findClass()
       │
       ├─► 检查是否已加载
       │   └─► 已加载 → 直接返回
       │
       ├─► 委派给父加载器 (PathClassLoader)
       │   │
       │   ├─► SystemUI 类已加载 → 返回
       │   │
       │   └─► 委派给 BootClassLoader
       │       │
       │       ├─► Framework 类已加载 → 返回
       │       │
       │       └─► 未找到
       │
       └─► DexClassLoader 自己加载
           │
           └─► 从插件 APK 中加载类 → 返回

类隔离机制：
─────────────────────────────────────────────────────────────────────────────

SystemUI ClassLoader:
  └─► 加载 SystemUI 类
      └─► android.widget.TextView
      └─► com.android.systemui.statusbar.StatusBar

Plugin A ClassLoader:
  └─► 加载 Plugin A 类
      └─► com.plugin.a.PluginClass
      └─► 共享: android.widget.TextView (来自父加载器)

Plugin B ClassLoader:
  └─► 加载 Plugin B 类
      └─► com.plugin.b.PluginClass
      └─► 共享: android.widget.TextView (来自父加载器)

特点:
1. SystemUI 类只加载一次 (父加载器)
2. 每个插件有独立的 ClassLoader
3. 插件之间类隔离
4. 共享 Framework 类
```

### 11.6 完整插件加载流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SystemUI 插件完整加载流程                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   1. SystemUI 启动                                                         │
│      │                                                                      │
│      ▼                                                                      │
│   PluginManager.getInstance(context)                                        │
│      │                                                                      │
│      │ 初始化                                                               │
│      ▼                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  PluginManager                                                       │  │
│   │  • 创建单例                                                          │  │
│   │  • 获取插件版本                                                       │  │
│   │  • 注册包监听                                                         │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│      │                                                                      │
│      ▼                                                                      │
│   2. 注册插件监听器                                                         │
│      │                                                                      │
│      │ addPluginListener(listener, StatusBarPlugin.class)                  │
│      ▼                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  查询插件                                                             │  │
│   │  Intent intent = new Intent(PLUGIN_ACTION);                          │  │
│   │  intent.addCategory(StatusBarPlugin.class.getName());                │  │
│   │  List<ResolveInfo> resolves = pm.queryIntentServices(intent, 0);     │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│      │                                                                      │
│      ▼                                                                      │
│   3. 遍历插件                                                               │
│      │                                                                      │
│      │ for (ResolveInfo resolve : resolves)                                │
│      ▼                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  检查权限                                                             │  │
│   │  pm.checkPermission(PLUGIN_PERMISSION, packageName)                  │  │
│   │                                                                      │  │
│   │  检查版本                                                             │  │
│   │  metaData.getInt("com.android.systemui.plugins.version")            │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│      │                                                                      │
│      ▼                                                                      │
│   4. 创建插件实例                                                           │
│      │                                                                      │
│      │ new PluginInstance<>(context, cls, component, appInfo)             │
│      ▼                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  PluginInstance.connect(listener)                                    │  │
│   │                                                                      │  │
│   │  ┌────────────────────────────────────────────────────────────────┐  │  │
│   │  │  1. 创建 ClassLoader                                          │  │  │
│   │  │     DexClassLoader(apkPath, optimizedDir, libPath, parent)    │  │  │
│   │  └────────────────────────────────────────────────────────────────┘  │  │
│   │                                                                      │  │
│   │  ┌────────────────────────────────────────────────────────────────┐  │  │
│   │  │  2. 创建 Context                                              │  │  │
│   │  │     context.createPackageContext(packageName, flags)         │  │  │
│   │  │     new PluginContextWrapper(baseContext, classLoader)       │  │  │
│   │  └────────────────────────────────────────────────────────────────┘  │  │
│   │                                                                      │  │
│   │  ┌────────────────────────────────────────────────────────────────┐  │  │
│   │  │  3. 加载插件类                                                │  │  │
│   │  │     Class<?> cls = classLoader.loadClass(className)          │  │  │
│   │  └────────────────────────────────────────────────────────────────┘  │  │
│   │                                                                      │  │
│   │  ┌────────────────────────────────────────────────────────────────┐  │  │
│   │  │  4. 实例化插件                                                │  │  │
│   │  │     plugin = cls.getDeclaredConstructor().newInstance()      │  │  │
│   │  └────────────────────────────────────────────────────────────────┘  │  │
│   │                                                                      │  │
│   │  ┌────────────────────────────────────────────────────────────────┐  │  │
│   │  │  5. 调用 onCreate                                             │  │  │
│   │  │     plugin.onCreate(pluginContext, listener)                  │  │  │
│   │  └────────────────────────────────────────────────────────────────┘  │  │
│   │                                                                      │  │
│   │  ┌────────────────────────────────────────────────────────────────┐  │  │
│   │  │  6. 通知连接成功                                              │  │  │
│   │  │     listener.onPluginConnected(plugin)                         │  │  │
│   │  └────────────────────────────────────────────────────────────────┘  │  │
│   │                                                                      │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│      │                                                                      │
│      ▼                                                                      │
│   5. SystemUI 使用插件                                                      │
│      │                                                                      │
│      │ View statusBarView = plugin.getStatusBarView()                      │
│      ▼                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  添加插件视图到 StatusBar                                            │  │
│   │  statusBar.addView(statusBarView)                                    │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│      │                                                                      │
│      ▼                                                                      │
│   6. 插件运行中                                                             │
│      │                                                                      │
│      │ 插件处理事件、更新 UI                                               │
│      │                                                                      │
│      ▼                                                                      │
│   7. 插件卸载                                                               │
│      │                                                                      │
│      │ pluginInstance.disconnect()                                         │
│      ▼                                                                      │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │  1. plugin.onDestroy()                                               │  │
│   │  2. listener.onPluginDisconnected(plugin)                            │  │
│   │  3. 清理引用                                                          │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.7 StatusBar 插件化实现示例
```


```java
/**
 * StatusBar 插件接口
 */
public interface StatusBarPlugin extends Plugin {
    View getStatusBarView();
    void onHeightChanged(int height);
    void onNotificationCountChanged(int count);
}

/**
 * StatusBar 插件实现
 */
public class CustomStatusBarPlugin implements StatusBarPlugin {
    private Context mContext;
    private View mStatusBarView;
    
    @Override
    public void onCreate(Context context, PluginListener listener) {
        mContext = context;
        mStatusBarView = LayoutInflater.from(context)
                .inflate(R.layout.custom_status_bar, null);
        listener.onPluginConnected(this);
    }
    
    @Override
    public View getStatusBarView() {
        return mStatusBarView;
    }
}
```

### 11.8 QuickSettings 插件化

```java
/**
 * QuickSettings 插件接口
 */
public interface QuickSettingsPlugin extends Plugin {
    List<QSTile> getTiles();
    void onTileClick(String tileId);
}
```

### 11.9 插件安全机制

```
1. 权限控制
   <uses-permission android:name="com.android.systemui.permission.PLUGIN" />

2. 签名验证
   • 系统签名或特权应用

3. 版本检查
   <meta-data android:name="com.android.systemui.plugins.version" android:value="1" />

4. 沙箱隔离
   • 独立进程
   • 独立 ClassLoader
   • IPC 通信
```

### 11.10 插件开发最佳实践

```
1. 架构设计
   • 单一职责
   • 接口隔离
   • 依赖倒置

2. 性能优化
   • 懒加载
   • 异步初始化
   • 内存管理

3. 兼容性处理
   • 版本检查
   • 降级策略
   • 异常处理

4. 调试技巧
   adb shell dumpsys activity services | grep Plugin
   adb logcat -s PluginManager:V Plugin:V
```

---

## 总结

### 插件化核心要点

1. **类加载**：DexClassLoader 动态加载插件类
2. **资源加载**：AssetManager.addAssetPath 加载插件资源
3. **Activity 插件化**：占坑 + Hook AMS
4. **Service 插件化**：代理 Service 方案
5. **兼容性**：Android 高版本限制多，推荐 Shadow
6. **SystemUI 插件化**：
   - PluginManager 管理插件生命周期
   - DexClassLoader 加载插件类
   - createPackageContext 创建插件 Context
   - 独立进程 + Binder IPC 通信

### 学习建议

1. **基础**：ClassLoader、资源加载、反射
2. **进阶**：Activity 启动流程、Hook 技术
3. **实战**：使用 Shadow/RePlugin 集成
4. **深入**：阅读框架源码
5. **SystemUI**：研究 AOSP SystemUI 插件机制
   - frameworks/base/packages/SystemUI/src/com/android/systemui/plugins/

---

**文档版本**：v1.2  
**更新时间**：2026-03-12  
**适用版本**：Android 5.0+
