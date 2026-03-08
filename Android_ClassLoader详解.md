# Android ClassLoader 详解

_作者：OpenClaw_  
_日期：2026-03-08_

---

## 目录

1. [概述](#1-概述)
2. [Java ClassLoader 回顾](#2-java-classloader-回顾)
3. [Android ClassLoader 体系](#3-android-classloader-体系)
4. [BootClassLoader](#4-bootclassloader)
5. [PathClassLoader](#5-pathclassloader)
6. [DexClassLoader](#6-dexclassloader)
7. [InMemoryDexClassLoader](#7-inmemorydexclassloader)
8. [双亲委派模型](#8-双亲委派模型)
9. [热修复与插件化](#9-热修复与插件化)
10. [总结](#10-总结)

---

## 1. 概述

ClassLoader 是 Java/Android 中负责加载类文件的核心组件。理解 ClassLoader 对于掌握热修复、插件化等技术至关重要。

```
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

```
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
protected Class<?> loadClass(String name, boolean resolve) {
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

```
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android ClassLoader 体系                            │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────────────┐
                        │     java.lang.ClassLoader│
                        └───────────┬─────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│ BootClassLoader   │   │ PathClassLoader   │   │ DexClassLoader    │
│ (系统启动类加载器) │   │ (应用类加载器)    │   │ (动态加载器)      │
└───────────────────┘   └───────────────────┘   └───────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
  加载系统核心类          加载已安装 APK          加载外部 DEX/APK
  android.jar            classes.dex             插件化/热修复
```

### 3.2 BaseDexClassLoader

```java
/**
 * BaseDexClassLoader 是 PathClassLoader 和 DexClassLoader 的父类
 * 
 * 核心实现：
 * - DexPathList pathList: 管理 DEX 文件列表
 */
public class BaseDexClassLoader extends ClassLoader {
    
    private final DexPathList pathList;
    
    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        // 委托给 DexPathList 查找
        Class<?> clazz = pathList.findClass(name, suppressedExceptions);
        if (clazz == null) {
            throw new ClassNotFoundException(name);
        }
        return clazz;
    }
}
```

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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BootClassLoader                                     │
└─────────────────────────────────────────────────────────────────────────────┘

作用：
- Android 系统启动时预加载核心系统类
- 类似于 JVM 的 Bootstrap ClassLoader
- 由 Java 实现（非 C++）

加载内容：
- android.jar 中的类
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
    
    public static BootClassLoader getInstance() {
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

```
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
│  ... (约 3000+ 个类)                                                        │
└─────────────────────────────────────────────────────────────────────────────┘

预加载的好处:
- 所有应用进程共享（Copy-on-Write）
- 加快应用启动速度
- 减少内存占用
```

---

## 5. PathClassLoader

### 5.1 概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PathClassLoader                                     │
└─────────────────────────────────────────────────────────────────────────────┘

作用：
- 加载已安装应用的类（APK 中的 classes.dex）
- 加载系统应用的类

特点：
- 只能加载已安装的 APK
- 无法加载外部 DEX/APK
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

```java
/**
 * ActivityThread 中创建 PathClassLoader
 */
public static ActivityThread currentActivityThread() {
    // ...
}

private void handleBindApplication(AppBindData data) {
    // 创建应用的 PathClassLoader
    mInitialApplication = data.info.makeApplication(data.restrictedBackupMode, null);
}

// LoadedApk.makeApplication()
public Application makeApplication(boolean forceDefaultAppClass, Instrumentation instrumentation) {
    // 创建 PathClassLoader
    ClassLoader cl = getClassLoader();
    // ...
}

// LoadedApk.getClassLoader()
public ClassLoader getClassLoader() {
    synchronized (this) {
        if (mClassLoader == null) {
            // 创建 PathClassLoader
            mClassLoader = ApplicationLoaders.getDefault().getClassLoader(
                zip,
                mApplicationInfo.targetSdkVersion,
                mLibraries,
                getClassLoader(),
                mAppDir
            );
        }
        return mClassLoader;
    }
}
```

---

## 6. DexClassLoader

### 6.1 概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DexClassLoader                                     │
└─────────────────────────────────────────────────────────────────────────────┘

作用：
- 动态加载未安装的 APK、JAR 或 DEX 文件
- 常用于插件化、热修复等场景

特点：
- 可以加载任意路径的 DEX/APK
- 需要指定优化输出目录
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
String dexPath = "/sdcard/plugin.apk";
String optimizedDirectory = context.getCacheDir().getAbsolutePath();
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
Object instance = clazz.newInstance();
```

### 6.3 插件化示例

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
    
    /**
     * 加载插件的资源
     */
    public Resources loadPluginResources(String pluginPath) {
        try {
            AssetManager assetManager = AssetManager.class.newInstance();
            Method addAssetPath = AssetManager.class.getMethod("addAssetPath", String.class);
            addAssetPath.invoke(assetManager, pluginPath);
            
            Resources superRes = context.getResources();
            return new Resources(assetManager, superRes.getDisplayMetrics(), superRes.getConfiguration());
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
}
```

---

## 7. InMemoryDexClassLoader

### 7.1 概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         InMemoryDexClassLoader                             │
└─────────────────────────────────────────────────────────────────────────────┘

作用：
- 从内存中加载 DEX 文件
- Android 8.0 (API 26) 引入

特点：
- DEX 文件不需要存储在文件系统
- 适合动态下载的 DEX
- 安全性更高（不落地）
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

```
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
   - 防止逆向分析

3. 热修复
   - 下载补丁 DEX
   - 内存中加载
   - 动态替换类

4. 插件化
   - 插件动态下载
   - 无需文件存储
   - 即插即用
```

---

## 8. 双亲委派模型

### 8.1 Android 中的双亲委派

```
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

```java
/**
 * 打破双亲委派模型
 * 
 * 场景：热修复、插件化需要先加载补丁类
 */
public class HotFixClassLoader extends PathClassLoader {
    
    private final DexClassLoader patchClassLoader;
    
    public HotFixClassLoader(String dexPath, ClassLoader parent, String patchPath) {
        super(dexPath, parent);
        
        // 创建补丁 ClassLoader
        patchClassLoader = new DexClassLoader(
            patchPath,
            null,
            null,
            parent  // 注意：父加载器相同
        );
    }
    
    @Override
    protected Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
        // 1. 先检查是否已加载
        Class<?> clazz = findLoadedClass(name);
        if (clazz != null) {
            return clazz;
        }
        
        // 2. 先从补丁中加载（打破双亲委派）
        try {
            clazz = patchClassLoader.findClass(name);
            if (clazz != null) {
                return clazz;
            }
        } catch (ClassNotFoundException e) {
            // 补丁中没有，继续
        }
        
        // 3. 再委托父加载器
        try {
            clazz = super.loadClass(name, resolve);
            if (clazz != null) {
                return clazz;
            }
        } catch (ClassNotFoundException e) {
            // 父加载器没有，继续
        }
        
        // 4. 自己加载
        return findClass(name);
    }
}
```

---

## 9. 热修复与插件化

### 9.1 热修复原理

```
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
            Object[] newElements = new Object[patchElements.length + oldElements.length];
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

```
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

```java
/**
 * 插件化管理器
 */
public class PluginManager {
    
    private static final Map<String, DexClassLoader> plugins = new HashMap<>();
    
    /**
     * 加载插件
     */
    public static void loadPlugin(Context context, String pluginPath) {
        if (plugins.containsKey(pluginPath)) {
            return;
        }
        
        // 1. 创建优化目录
        File optimizedDirectory = context.getDir("plugin_dex", Context.MODE_PRIVATE);
        
        // 2. 创建 DexClassLoader
        DexClassLoader classLoader = new DexClassLoader(
            pluginPath,
            optimizedDirectory.getAbsolutePath(),
            null,
            context.getClassLoader()
        );
        
        // 3. 缓存
        plugins.put(pluginPath, classLoader);
        
        // 4. 加载插件资源
        loadPluginResources(pluginPath, classLoader);
    }
    
    /**
     * 加载插件资源
     */
    private static void loadPluginResources(String pluginPath, DexClassLoader classLoader) {
        try {
            AssetManager assetManager = AssetManager.class.newInstance();
            Method addAssetPath = AssetManager.class.getMethod("addAssetPath", String.class);
            addAssetPath.invoke(assetManager, pluginPath);
            
            // 创建 Resources 对象
            Resources superRes = context.getResources();
            Resources pluginResources = new Resources(
                assetManager,
                superRes.getDisplayMetrics(),
                superRes.getConfiguration()
            );
            
            // 缓存资源
            pluginResourcesMap.put(pluginPath, pluginResources);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    /**
     * 启动插件的 Activity
     */
    public static void startPluginActivity(Context context, String pluginPath, 
            String activityClassName) {
        DexClassLoader classLoader = plugins.get(pluginPath);
        if (classLoader == null) {
            loadPlugin(context, pluginPath);
            classLoader = plugins.get(pluginPath);
        }
        
        try {
            Class<?> activityClass = classLoader.loadClass(activityClassName);
            Intent intent = new Intent(context, activityClass);
            context.startActivity(intent);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

## 10. 总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ClassLoader 总结                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Android ClassLoader 对比:                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  BootClassLoader:                                                       │
│  - 加载系统核心类 (android.jar)                                         │
│  - Zygote 进程中创建，所有应用共享                                       │
│                                                                         │
│  PathClassLoader:                                                       │
│  - 加载已安装 APK 的类                                                   │
│  - 应用的默认类加载器                                                    │
│  - 无法加载外部 DEX/APK                                                 │
│                                                                         │
│  DexClassLoader:                                                        │
│  - 加载外部 DEX/APK                                                      │
│  - 用于插件化、热修复                                                    │
│  - 灵活性高                                                              │
│                                                                         │
│  InMemoryDexClassLoader (API 26+):                                      │
│  - 从内存加载 DEX                                                        │
│  - 不需要文件存储                                                        │
│  - 安全性高                                                              │
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
