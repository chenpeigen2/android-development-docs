# Android ClassLoader 详解

_作者：OpenClaw_
_日期：2026-03-08_

---

## 目录

- [1. 概述](#1-概述)
- [2. Java ClassLoader 回顾](#2-java-classloader-回顾)
  - [2.1 JVM ClassLoader 体系](#21-jvm-classloader-体系)
  - [2.2 双亲委派模型](#22-双亲委派模型)
- [3. Android ClassLoader 体系](#3-android-classloader-体系)
  - [3.1 Android ClassLoader 继承关系](#31-android-classloader-继承关系)
  - [3.2 BaseDexClassLoader](#32-basedexclassloader)
  - [3.3 DexPathList](#33-dexpathlist)
- [4. BootClassLoader](#4-bootclassloader)
  - [4.1 概述](#41-概述)
  - [4.2 源码分析](#42-源码分析)
  - [4.3 预加载类](#43-预加载类)
- [5. PathClassLoader](#5-pathclassloader)
  - [5.1 概述](#51-概述)
  - [5.2 源码分析](#52-源码分析)
  - [5.3 应用启动时的创建](#53-应用启动时的创建)
- [6. DexClassLoader](#6-dexclassloader)
  - [6.1 概述](#61-概述)
  - [6.2 源码分析](#62-源码分析)
  - [6.3 插件化示例](#63-插件化示例)
- [7. InMemoryDexClassLoader](#7-inmemorydexclassloader)
  - [7.1 概述](#71-概述)
  - [7.2 源码分析](#72-源码分析)
  - [7.3 适用场景](#73-适用场景)
- [8. 双亲委派模型](#8-双亲委派模型)
  - [8.1 Android 中的双亲委派](#81-android-中的双亲委派)
  - [8.2 打破双亲委派](#82-打破双亲委派)
- [9. 热修复与插件化](#9-热修复与插件化)
  - [9.1 热修复原理](#91-热修复原理)
  - [9.2 热修复实现](#92-热修复实现)
  - [9.3 插件化原理](#93-插件化原理)
  - [9.4 插件化实现](#94-插件化实现)
- [10. 总结](#10-总结)
- [固定版本源码索引](#固定版本源码索引)

---

## 1. 概述

ClassLoader 是 Java/Android 中负责加载类文件的核心组件。理解 ClassLoader 对于掌握热修复、插件化等技术至关重要。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ClassLoader 作用                                    │
└─────────────────────────────────────────────────────────────────────────────┘

.java 源文件
     │
     ▼ javac 编译
.class 字节码 (JVM)
     │
     ▼ dx/d8 工具
.dex 文件 (Android)
     │
     ▼ ClassLoader 加载
Class 对象 (内存)
     │
     ▼ 实例化
Object 对象
```

---

## 2. Java ClassLoader 回顾

### 2.1 JVM ClassLoader 体系

下图是 Java 8 的历史模型；Java 9+ 的平台类加载器取代 Extension ClassLoader，Android 的 BootClassLoader/DEX 路径不能用桌面 JVM 的 ext 目录解释。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         JVM ClassLoader 体系                                │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────────────┐
                        │   Bootstrap ClassLoader │
                        │   (C++ 实现)            │
                        │   加载核心类库           │
                        │   java.lang.*, java.util.*  │
                        └───────────┬─────────────┘
                                    │
                        ┌───────────▼─────────────┐
                        │  Extension ClassLoader  │
                        │  加载扩展类库            │
                        │  $JAVA_HOME/lib/ext     │
                        └───────────┬─────────────┘
                                    │
                        ┌───────────▼─────────────┐
                        │  Application ClassLoader │
                        │  加载应用类              │
                        │  classpath 中的类        │
                        └───────────┬─────────────┘
                                    │
                        ┌───────────▼─────────────┐
                        │   Custom ClassLoader    │
                        │   用户自定义            │
                        └─────────────────────────┘
```

### 2.2 双亲委派模型

```java
/**
 * Java 双亲委派模型
 *
 * 加载类时，先委托父加载器加载
 * 父加载器无法加载时，才自己加载
 */
protected Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
    // 1. 检查是否已加载
    Class<?> c = findLoadedClass(name);
    if (c == null) {
        try {
            if (parent != null) {
                // 2. 委托父加载器加载
                c = parent.loadClass(name, false);
            } else {
                // 3. 委托 Bootstrap 加载
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
```

**双亲委派的好处：**

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         双亲委派的好处                                      │
└─────────────────────────────────────────────────────────────────────────────┘

1. 安全性
   - 防止核心类被篡改
   - 用户无法自定义 java.lang.String

2. 避免重复加载
   - 父加载器已加载的类，子加载器不需要再加载

3. 统一性
   - 核心类由同一加载器加载，保证一致性
```

---

## 3. Android ClassLoader 体系

### 3.1 Android ClassLoader 继承关系

```text
java.lang.ClassLoader
  +-- java.lang.BootClassLoader（libcore 内部类，桥接 ART boot class path）
  +-- dalvik.system.BaseDexClassLoader
        +-- PathClassLoader
        |     +-- DelegateLastClassLoader
        +-- DexClassLoader
        +-- InMemoryDexClassLoader
```

这是继承关系，不是 parent 委派链。应用的 parent、共享库加载器和 split 加载器由 LoadedApk 配置，不一定只是单层 BootClassLoader。

---

### 3.2 BaseDexClassLoader

`BaseDexClassLoader` 持有 `DexPathList`，但 `findClass()` 并非只查 `dexElements`。外层 `ClassLoader.loadClass()` 已先做已加载检查与 parent 委派；进入本类后按下列顺序搜索：

```text
sharedLibraryLoaders（每个调用 loadClass）
  -> pathList.findClass(name, suppressedExceptions)
  -> sharedLibraryLoadersAfter（每个调用 loadClass）
  -> ClassNotFoundException，附带所有 suppressedExceptions
```

前置共享库可以先于应用自身命中，后置库只在应用查找失败后命中。这是平台加载器图的一部分，不应把“补丁放到 dexElements[0]”解释为能覆盖 parent 或共享库已经定义的类。

---

### 3.3 DexPathList

```java
/**
 * DexPathList 管理多个 DEX 文件
 */
final class DexPathList {
    // DEX 文件列表
    private Element[] dexElements;

    // 原生库路径
    private final List<File> nativeLibraryDirectories;

    Class<?> findClass(String name, List<Throwable> suppressed) {
        // 遍历所有 DEX 文件查找类
        for (Element element : dexElements) {
            Class<?> clazz = element.findClass(name, definingContext, suppressed);
            if (clazz != null) {
                return clazz;
            }
        }
        return null;
    }
}
```

---

## 4. BootClassLoader

### 4.1 概述

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BootClassLoader                                     │
└─────────────────────────────────────────────────────────────────────────────┘

作用：
- 负责 boot class path 的类查找；预加载由 ZygoteInit 驱动
- 类似于 JVM 的 Bootstrap ClassLoader
- Java 门面 + ART native 类查找，并非纯 Java 实现

加载内容：
- boot class path 中的运行时 DEX / boot image 类
- java.lang.* 核心类
- android.* 系统类

特点：
- 在 Zygote 进程中创建
- 所有应用进程共享（Copy-on-Write）
```

### 4.2 源码分析

```java
/**
 * BootClassLoader 源码
 */
class BootClassLoader extends ClassLoader {

    private static BootClassLoader instance;

    public static synchronized BootClassLoader getInstance() {
        if (instance == null) {
            instance = new BootClassLoader();
        }
        return instance;
    }

    public BootClassLoader() {
        super(null);  // 无父加载器
    }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        // 从系统 DEX 缓存中查找
        return Class.classForName(name, false, null);
    }

    @Override
    protected URL findResource(String name) {
        // 从系统资源中查找
        return null;
    }
}

// ZygoteInit 中预加载类
public static void main(String argv[]) {
    // 预加载系统类
    preloadClasses();
    // ...
}

private static void preloadClasses() {
    // 读取 preloaded-classes 文件
    // 加载所有系统核心类
}
```

### 4.3 预加载类

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         预加载类列表 (preloaded-classes)                    │
└─────────────────────────────────────────────────────────────────────────────┘

文件位置: /frameworks/base/config/preloaded-classes

部分内容:
┌─────────────────────────────────────────────────────────────────────────────┐
│  android.app.Activity                                                       │
│  android.app.Application                                                    │
│  android.content.Context                                                    │
│  android.view.View                                                          │
│  android.widget.TextView                                                    │
│  android.widget.Button                                                      │
│  java.lang.String                                                           │
│  java.lang.Object                                                           │
│  java.lang.Class                                                            │
│  ...（实际集合以本 tag 配置及产品预加载策略为准）                                                        │
└─────────────────────────────────────────────────────────────────────────────┘

预加载的好处:
- 所有应用进程共享（Copy-on-Write）
- 加快应用启动速度
- 减少内存占用
```

---

## 5. PathClassLoader

### 5.1 概述

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PathClassLoader                                     │
└─────────────────────────────────────────────────────────────────────────────┘

作用：
- 加载已安装应用的类（APK 中的 classes.dex）
- 加载系统应用的类

特点：
- 可从传入路径加载 DEX/APK/JAR，不以是否安装为限制
- 同样能加载可访问、格式有效且符合动态加载策略的 DEX/APK
- Android 应用的默认类加载器
```

### 5.2 源码分析

```java
/**
 * PathClassLoader 源码
 */
public class PathClassLoader extends BaseDexClassLoader {

    /**
     * 创建 PathClassLoader
     *
     * @param dexPath        DEX 文件路径 (APK 路径)
     * @param librarySearchPath 原生库搜索路径
     * @param parent         父加载器
     */
    public PathClassLoader(String dexPath, String librarySearchPath, ClassLoader parent) {
        super(dexPath, null, librarySearchPath, parent);
    }

    /**
     * 简化构造函数
     */
    public PathClassLoader(String dexPath, ClassLoader parent) {
        super(dexPath, null, null, parent);
    }
}

// 使用示例
PathClassLoader pathClassLoader = new PathClassLoader(
    "/data/app/com.example-xxx/base.apk",  // APK 路径
    "/data/app/com.example-xxx/lib/arm",   // 原生库路径
    ClassLoader.getSystemClassLoader()      // 父加载器
);
```

### 5.3 应用启动时的创建

Android 17 的主链如下（源码函数名，省略 instrumentation/split 的分支）：

```text
ActivityThread.handleBindApplication(data)
  -> LoadedApk.makeApplicationInner(...)
     -> LoadedApk.getClassLoader()
        -> 若 mClassLoader == null：createOrUpdateClassLoaderLocked(null)
           -> ApplicationLoaders.getDefault().getClassLoaderWithSharedLibraries(...)
           -> mDefaultClassLoader
           -> AppComponentFactory.instantiateClassLoader(...)
           -> mClassLoader
     -> Instrumentation.newApplication(classLoader, appClass, context)
```

`getClassLoader()` 可能先创建默认加载器，再让 AppComponentFactory 定制；隔离 split 和共享库增加委派边。它不会在构造参数里递归调用自己，否则未初始化的 `mClassLoader` 将导致无限递归。SDK 的 `android.jar` 只有编译桩，运行时实现来自设备 boot class path。

---

## 6. DexClassLoader

### 6.1 概述

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DexClassLoader                                     │
└─────────────────────────────────────────────────────────────────────────────┘

作用：
- 动态加载未安装的 APK、JAR 或 DEX 文件
- 常用于插件化、热修复等场景

特点：
- 可加载应用可访问且符合安全策略的 DEX/APK
- optimizedDirectory 从 API 26 起被忽略，构造参数可传 null
- 灵活性高
```

### 6.2 源码分析

```java
/**
 * DexClassLoader 源码
 */
public class DexClassLoader extends BaseDexClassLoader {

    /**
     * 创建 DexClassLoader
     *
     * @param dexPath          DEX/APK 文件路径 (支持多个，用 File.pathSeparator 分隔)
     * @param optimizedDirectory 优化后的 DEX 输出目录 (已废弃，API 26+ 忽略)
     * @param librarySearchPath 原生库搜索路径
     * @param parent           父加载器
     */
    public DexClassLoader(String dexPath, String optimizedDirectory,
            String librarySearchPath, ClassLoader parent) {
        super(dexPath, null, librarySearchPath, parent);
    }
}

// 使用示例
String dexPath = new File(context.getCodeCacheDir(), "verified-plugin.apk").getPath();
// 前置条件：来源/签名已验证，文件按只读发布；不可直接加载可篡改的共享存储代码。
String optimizedDirectory = null; // API 26+ 忽略
String librarySearchPath = null;
ClassLoader parent = getClass().getClassLoader();

DexClassLoader dexClassLoader = new DexClassLoader(
    dexPath,
    optimizedDirectory,
    librarySearchPath,
    parent
);

// 加载类
Class<?> clazz = dexClassLoader.loadClass("com.example.plugin.PluginClass");
Object instance = clazz.getDeclaredConstructor().newInstance();
```

### 6.3 插件化示例

以下只演示可信插件入口的加载；调用前需校验包完整性，并在写入完成前将目标文件设为只读后发布。反射 AssetManager.addAssetPath 属于非 SDK 历史方式，不能作为 Android 17 应用兼容方案；API 30+ 的资源扩展应使用 ResourcesLoader/ResourcesProvider，并隔离宿主与插件资源生命周期。

```java
/**
 * 插件化加载示例
 */
public class PluginManager {

    private DexClassLoader pluginClassLoader;
    private Context context;

    public PluginManager(Context context) {
        this.context = context;
    }

    /**
     * 加载插件 APK
     */
    public void loadPlugin(String pluginPath) {
        // 1. 获取插件的优化目录
        File optimizedDirectory = context.getDir("plugin_dex", Context.MODE_PRIVATE);

        // 2. 创建 DexClassLoader
        pluginClassLoader = new DexClassLoader(
            pluginPath,
            optimizedDirectory.getAbsolutePath(),
            null,
            context.getClassLoader()
        );

        // 3. 加载插件入口类
        try {
            Class<?> pluginClass = pluginClassLoader.loadClass("com.plugin.PluginEntry");
            Method onCreate = pluginClass.getMethod("onCreate", Context.class);
            onCreate.invoke(null, context);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // 资源加载不由 DexClassLoader 完成；交给基于 ResourcesLoader 的资源适配层。

}
```

---

## 7. InMemoryDexClassLoader

### 7.1 概述

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         InMemoryDexClassLoader                             │
└─────────────────────────────────────────────────────────────────────────────┘

作用：
- 从内存中加载 DEX 文件
- Android 8.0 (API 26) 引入

特点：
- DEX 文件不需要存储在文件系统
- 适合动态下载的 DEX
- 不落地不等于安全沙箱，仍以宿主 UID/权限执行
```

### 7.2 源码分析

```java
/**
 * InMemoryDexClassLoader 源码
 */
public class InMemoryDexClassLoader extends BaseDexClassLoader {

    /**
     * 创建 InMemoryDexClassLoader
     *
     * @param dexBuffers  DEX 文件的 ByteBuffer 数组
     * @param librarySearchPath 原生库搜索路径
     * @param parent      父加载器
     */
    public InMemoryDexClassLoader(ByteBuffer[] dexBuffers,
            String librarySearchPath, ClassLoader parent) {
        super(dexBuffers, librarySearchPath, parent);
    }
}

// 使用示例
public class DynamicLoader {

    /**
     * 从网络下载 DEX 并加载
     */
    public void loadDexFromNetwork(byte[] dexBytes) {
        // 1. 将 byte[] 转换为 ByteBuffer
        ByteBuffer dexBuffer = ByteBuffer.wrap(dexBytes);
        ByteBuffer[] dexBuffers = new ByteBuffer[] { dexBuffer };

        // 2. 创建 InMemoryDexClassLoader
        InMemoryDexClassLoader classLoader = new InMemoryDexClassLoader(
            dexBuffers,
            null,
            getClass().getClassLoader()
        );

        // 3. 加载类
        try {
            Class<?> clazz = classLoader.loadClass("com.example.DynamicClass");
            // 使用加载的类
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
    }
}
```

### 7.3 适用场景

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         InMemoryDexClassLoader 适用场景                     │
└─────────────────────────────────────────────────────────────────────────────┘

1. 动态功能模块
   - 从服务器下载 DEX
   - 不保存到文件系统
   - 即时加载使用

2. 安全加固
   - DEX 文件加密存储
   - 运行时解密到内存
   - 减少落地文件，不阻止内存转储或运行时分析

3. 热修复
   - 下载补丁 DEX
   - 内存中加载
   - 通过新加载器加载新类；不能替换已定义的 Class

4. 插件化
   - 插件动态下载
   - 无需文件存储
   - 即插即用
```

---

## 8. 双亲委派模型

### 8.1 Android 中的双亲委派

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 双亲委派模型                                │
└─────────────────────────────────────────────────────────────────────────────┘

加载顺序:

┌─────────────────────────────────────────────────────────────────────────────┐
│  loadClass("com.example.MyClass")                                          │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. 检查是否已加载                                                          │
│     Class<?> clazz = findLoadedClass(name);                                │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼ (未加载)
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. 委托父加载器 (BootClassLoader)                                          │
│     parent.loadClass(name);                                                │
│     - 尝试从系统类中加载                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼ (父加载器无法加载)
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. 自己加载                                                                │
│     findClass(name);                                                       │
│     - 从 DEX 文件中查找类                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 打破双亲委派

平台提供 `DelegateLastClassLoader`（API 27+），不必从另一个加载器上直接调用 protected `findClass()`。下面使用公开构造函数加载经过验证并只读发布的代码：

```java
ClassLoader pluginLoader = new DelegateLastClassLoader(
        verifiedPluginPath, context.getClassLoader());
Class<?> entry = pluginLoader.loadClass("com.example.plugin.Entry");
```

其 `loadClass(name, resolve)` 顺序为：`findLoadedClass` -> boot class path -> 自己的 `findClass` -> parent。boot class path 仍优先，所以这不是允许覆盖 `java.lang.String` 的安全绕过。插件与宿主共享接口必须由共同的 parent 定义；插件不能再打包同名接口副本，否则同名类因 defining loader 不同而不可强转。

新加载器不重定义原加载器中已经加载的 Class，调用方仍需通过显式接口/入口切换到新实现。仅改变查找顺序不会自动替换已经实例化的对象或已链接的方法。

---

## 9. 热修复与插件化

### 9.1 热修复原理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         热修复原理                                          │
└─────────────────────────────────────────────────────────────────────────────┘

核心思想：将补丁 DEX 插入到 dexElements 数组的前面

┌─────────────────────────────────────────────────────────────────────────────┐
│  正常加载顺序:                                                              │
│  dexElements = [base.dex]                                                  │
│  查找类: base.dex → 找到旧类                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  热修复后:                                                                  │
│  dexElements = [patch.dex, base.dex]                                       │
│  查找类: patch.dex → 找到新类 (不再查找 base.dex)                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 热修复实现

以下保留为理解 dexElements 的**非 SDK 反射实验**，不是 Android 17 可交付热修复方案。字段访问可能被隐藏 API 策略拒绝，只能影响此加载器尚未定义的类，且需要与类加载并发协调。

```java
/**
 * 热修复工具类
 */
public class HotFix {

    /**
     * 注入补丁 DEX
     */
    public static void injectPatch(Context context, String patchPath) {
        try {
            // 1. 获取应用的 PathClassLoader
            PathClassLoader pathClassLoader = (PathClassLoader) context.getClassLoader();

            // 2. 获取 PathClassLoader 的 pathList 字段
            Field pathListField = BaseDexClassLoader.class.getDeclaredField("pathList");
            pathListField.setAccessible(true);
            Object pathList = pathListField.get(pathClassLoader);

            // 3. 获取原始的 dexElements
            Field dexElementsField = pathList.getClass().getDeclaredField("dexElements");
            dexElementsField.setAccessible(true);
            Object[] oldElements = (Object[]) dexElementsField.get(pathList);

            // 4. 创建补丁的 DexClassLoader
            DexClassLoader patchClassLoader = new DexClassLoader(
                patchPath,
                context.getCacheDir().getAbsolutePath(),
                null,
                pathClassLoader.getParent()
            );

            // 5. 获取补丁的 dexElements
            Object patchPathList = pathListField.get(patchClassLoader);
            Object[] patchElements = (Object[]) dexElementsField.get(patchPathList);

            // 6. 合并 dexElements (补丁在前)
            Object[] newElements = (Object[]) java.lang.reflect.Array.newInstance(
                    oldElements.getClass().getComponentType(),
                    patchElements.length + oldElements.length);
            // 字段类型为 Element[]，不能用运行时类型 Object[] 赋值。
            System.arraycopy(patchElements, 0, newElements, 0, patchElements.length);
            System.arraycopy(oldElements, 0, newElements, patchElements.length, oldElements.length);

            // 7. 设置新的 dexElements
            dexElementsField.set(pathList, newElements);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### 9.3 插件化原理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         插件化原理                                          │
└─────────────────────────────────────────────────────────────────────────────┘

核心思想：使用 DexClassLoader 加载插件 APK

┌─────────────────────────────────────────────────────────────────────────────┐
│  宿主应用 (Host)                                                            │
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │ PathClassLoader                                                       ││
│  │ - 加载宿主的类                                                        ││
│  │ - 父加载器: BootClassLoader                                           ││
│  └───────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  插件1 (Plugin1)                                                            │
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │ DexClassLoader                                                        ││
│  │ - 加载插件1的类                                                        ││
│  │ - 父加载器: 宿主的 PathClassLoader                                    ││
│  └───────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  插件2 (Plugin2)                                                            │
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │ DexClassLoader                                                        ││
│  │ - 加载插件2的类                                                        ││
│  │ - 父加载器: 宿主的 PathClassLoader                                    ││
│  └───────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.4 插件化实现

ClassLoader 只解决类加载，不向 PackageManager 注册组件。`new Intent(context, pluginClass)` 不能直接启动未安装 APK 中的 Activity；它生成的是宿主包的组件名，而该类不在宿主 manifest 中。

一个可控的插件接口应定义在宿主公共 API 中，插件只提供业务/视图实现；宿主 Activity 仍在 manifest 注册：

```java
// 宿主公共接口：插件编译时依赖，但不要再打包一份。
public interface PluginEntry {
    void attach(Context hostContext);
    View createView(Context hostContext);
}

// 业务入口加载（异常交给上层处理），verifiedReadOnlyPath 由可信分发层提供。
public static PluginEntry loadPlugin(Context context, String verifiedReadOnlyPath)
        throws ReflectiveOperationException {
    ClassLoader loader = new DexClassLoader(
            verifiedReadOnlyPath, null, null, context.getClassLoader());
    Class<?> type = loader.loadClass("com.plugin.PluginEntryImpl");
    PluginEntry entry = type.asSubclass(PluginEntry.class)
            .getDeclaredConstructor().newInstance();
    entry.attach(context);
    return entry;
}

// 主线程中启动已声明的宿主容器，而不是任意插件 Activity。
context.startActivity(new Intent(context, PluginHostActivity.class));
```

资源不能由 loader 自动合并：Android 17 可使用公开 `ResourcesProvider.loadFromApk()` 与 `ResourcesLoader.addProvider()`/`Resources.addLoaders()`，并设计资源 ID 隔离、关闭 provider 的时机及容器销毁回调。宿主容器需负责 Activity 生命周期转发、状态保存和配置变化；仅加载入口并不意味着这些问题已经解决。

---

## 10. 总结

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ClassLoader 总结                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Android ClassLoader 对比:                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  BootClassLoader:                                                       │
│  - 加载 boot class path 的运行时类（非 SDK android.jar）                                         │
│  - Zygote 进程中创建，所有应用共享                                       │
│                                                                         │
│  PathClassLoader:                                                       │
│  - 加载已安装 APK 的类                                                   │
│  - 应用的默认类加载器                                                    │
│  - 同样能加载可访问、格式有效且符合动态加载策略的 DEX/APK                                                 │
│                                                                         │
│  DexClassLoader:                                                        │
│  - 加载外部 DEX/APK                                                      │
│  - 用于插件化、热修复                                                    │
│  - 灵活性高                                                              │
│                                                                         │
│  InMemoryDexClassLoader (API 26+):                                      │
│  - 从内存加载 DEX                                                        │
│  - 不需要文件存储                                                        │
│  - 需要同等严格的来源验证和代码信任边界                                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  面试要点:                                                                   │
│                                                                             │
│  1. Java ClassLoader vs Android ClassLoader                               │
│  2. 双亲委派模型及其打破                                                   │
│  3. PathClassLoader vs DexClassLoader 区别                                 │
│  4. 热修复原理 (dexElements 插入)                                          │
│  5. 插件化原理 (DexClassLoader + Resources)                                │
│  6. InMemoryDexClassLoader 的使用场景                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*本文档由 OpenClaw 生成*


## 固定版本源码索引

本文平台实现基线为 `android-17.0.0_r1`。下列函数用于定位正文分析；代码标为“节选”时省略无关监控，标为“示意”时不是源码逐字复制。

- [加载器搜索图](https://android.googlesource.com/platform/libcore/+/refs/tags/android-17.0.0_r1/dalvik/src/main/java/dalvik/system/BaseDexClassLoader.java#232)：`findClass`。
- [PathClassLoader](https://android.googlesource.com/platform/libcore/+/refs/tags/android-17.0.0_r1/dalvik/src/main/java/dalvik/system/PathClassLoader.java)：`constructors`。
- [DexClassLoader](https://android.googlesource.com/platform/libcore/+/refs/tags/android-17.0.0_r1/dalvik/src/main/java/dalvik/system/DexClassLoader.java)：`constructor`。
- [BootClassLoader](https://android.googlesource.com/platform/libcore/+/refs/tags/android-17.0.0_r1/ojluni/src/main/java/java/lang/ClassLoader.java)：`BootClassLoader.findClass; findResource`。
- [应用加载器创建](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/LoadedApk.java)：`getClassLoader; createOrUpdateClassLoaderLocked; makeApplicationInner`。
- [DelegateLast](https://android.googlesource.com/platform/libcore/+/refs/tags/android-17.0.0_r1/dalvik/src/main/java/dalvik/system/DelegateLastClassLoader.java)：`loadClass`。
- [DEX 顺序](https://android.googlesource.com/platform/libcore/+/refs/tags/android-17.0.0_r1/dalvik/src/main/java/dalvik/system/DexPathList.java)：`findClass`。
