# SystemUI Plugin 插件化详解

> 作者：OpenClaw | 日期：2026-03-12  
> 基于 Android 16 (API 36) AOSP 源码分析  
> 源码位置：`frameworks/base/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/`

---

## 📚 目录

**第 1 章 SystemUI Plugin 概述**
- 1.1 [什么是 SystemUI Plugin](#11-什么是-systemui-plugin)
- 1.2 [Plugin 架构总览](#12-plugin-架构总览)
- 1.3 [核心类介绍](#13-核心类介绍)

**第 2 章 PluginManagerImpl 源码分析**
- 2.1 [类结构与依赖](#21-类结构与依赖)
- 2.2 [插件加载流程](#22-插件加载流程)
- 2.3 [addPluginListener 详解](#23-addpluginlistener-详解)

**第 3 章 PluginInstance 源码分析**
- 3.1 [插件实例创建](#31-插件实例创建)
- 3.2 [ClassLoader 创建流程](#32-classloader-创建流程)
- 3.3 [Context 创建流程](#33-context-创建流程)

**第 4 章 PluginActionManager 源码分析**
- 4.1 [插件动作管理](#41-插件动作管理)
- 4.2 [插件生命周期](#42-插件生命周期)

**第 5 章 完整插件加载流程**
- 5.1 [时序图](#51-时序图)
- 5.2 [详细步骤](#52-详细步骤)

**第 6 章 插件开发实践**
- 6.1 [定义插件接口](#61-定义插件接口)
- 6.2 [实现插件](#62-实现插件)
- 6.3 [AndroidManifest 配置](#63-androidmanifest-配置)

---

## 第 1 章 SystemUI Plugin 概述

### 1.1 什么是 SystemUI Plugin

SystemUI Plugin 是 Android 系统提供的一种插件化机制，允许厂商或开发者在不修改 SystemUI 源码的情况下，扩展或替换 SystemUI 的功能。

**主要用途：**
- 厂商定制 StatusBar、NavigationBar 等 UI 组件
- 动态扩展 SystemUI 功能
- 模块化开发，解耦 SystemUI 组件

**源码位置：**
```
frameworks/base/packages/SystemUI/
├── plugin/                          # Plugin 库 (编译为 SystemUI-plugin-lib)
│   └── src/com/android/systemui/plugins/
│       ├── Plugin.java              # 插件接口
│       ├── PluginListener.java      # 插件监听器
│       └── ...
├── shared/
│   └── src/com/android/systemui/shared/plugins/
│       ├── PluginManagerImpl.java   # 插件管理器实现
│       ├── PluginInstance.java      # 插件实例
│       ├── PluginActionManager.java # 插件动作管理
│       ├── PluginEnabler.java       # 插件启用器
│       └── VersionInfo.java         # 版本信息
└── src/com/android/systemui/plugins/
    ├── PluginDependencyProvider.java
    ├── PluginEnablerImpl.java
    └── PluginsModule.java          # Dagger Module
```

### 1.2 Plugin 架构总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SystemUI Plugin 架构 (Android 16)                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    SystemUI Process                                  │  │
│   │                                                                      │  │
│   │   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │  │
│   │   │ PluginManagerImpl│  │   StatusBar      │  │ NavigationBar    │  │  │
│   │   │                  │  │                  │  │                  │  │  │
│   │   │ • addPluginListener() │ • registerPlugin() │ • registerPlugin()  │  │
│   │   │ • loadPlugin()  │  │ • 使用插件视图   │  │ • 使用插件视图   │  │  │
│   │   └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │  │
│   │            │                     │                     │            │  │
│   │            └─────────────────────┼─────────────────────┘            │  │
│   │                                  │                                   │  │
│   │                                  ▼                                   │  │
│   │   ┌────────────────────────────────────────────────────────────────┐│  │
│   │   │                    PluginInstance                              ││  │
│   │   │                                                                ││  │
│   │   │  1. createPluginClassLoader()  → DexClassLoader               ││  │
│   │   │  2. createPluginContext()      → PluginContextWrapper         ││  │
│   │   │  3. loadClass()                → 加载插件类                    ││  │
│   │   │  4. newInstance()              → 创建插件实例                  ││  │
│   │   │  5. plugin.onCreate()          → 初始化插件                    ││  │
│   │   │                                                                ││  │
│   │   └────────────────────────────────────────────────────────────────┘│  │
│   │                                                                      │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    │ Binder IPC                             │
│                                    ▼                                        │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                    Plugin APK (独立应用)                             │  │
│   │                                                                       │  │
│   │   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │  │
│   │   │ CustomStatusBar  │  │ CustomQS         │  │ CustomPlugin     │  │  │
│   │   │ implements       │  │ implements       │  │ implements       │  │  │
│   │   │ StatusBarPlugin  │  │ QSPlugin         │  │ Plugin           │  │  │
│   │   └──────────────────┘  └──────────────────┘  └──────────────────┘  │  │
│   │                                                                       │  │
│   │   AndroidManifest.xml:                                               │  │
│   │   <service android:name=".PluginService"                             │  │
│   │       android:permission="com.android.systemui.permission.PLUGIN">   │  │
│   │       <intent-filter>                                                │  │
│   │           <action android:name="com.android.systemui.action.PLUGIN"/>│  │
│   │       </intent-filter>                                               │  │
│   │   </service>                                                         │  │
│   │                                                                       │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 核心类介绍

| 类名 | 位置 | 职责 |
|------|------|------|
| `PluginManagerImpl` | shared/plugins | 插件管理器，负责加载和管理插件 |
| `PluginInstance` | shared/plugins | 插件实例，负责 ClassLoader 和 Context 创建 |
| `PluginActionManager` | shared/plugins | 插件动作管理，处理插件连接/断开 |
| `PluginEnabler` | shared/plugins | 插件启用/禁用控制 |
| `VersionInfo` | shared/plugins | 插件版本检查 |
| `Plugin` | plugin-lib | 插件基础接口 |
| `PluginListener` | plugin-lib | 插件监听器回调 |
| `PluginsModule` | src/plugins | Dagger 依赖注入模块 |

---

## 第 2 章 PluginManagerImpl 源码分析

> 源码位置：`frameworks/base/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginManagerImpl.java`

### 2.1 类结构与依赖

```java
/**
 * PluginManagerImpl - 插件管理器实现
 * 
 * 源码：frameworks/base/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginManagerImpl.java
 */
public class PluginManagerImpl implements PluginManager {
    private static final String TAG = "PluginManagerImpl";
    
    // 插件 Action
    public static final String PLUGIN_ACTION = "com.android.systemui.action.PLUGIN";
    
    // 上下文
    private final Context mContext;
    
    // 包管理器
    private final PackageManager mPm;
    
    // 插件动作管理器
    private final PluginActionManager mActionManager;
    
    // 插件启用器
    private final PluginEnabler mPluginEnabler;
    
    // 是否调试模式
    private final boolean mDebug;
    
    // 插件监听器列表
    private final ArrayMap<PluginListener<?>, PluginActionManager> mPluginListeners;
    
    /**
     * 构造函数 - 使用依赖注入
     */
    @Inject
    public PluginManagerImpl(
            @Main Context context,
            PluginActionManager actionManager,
            PluginEnabler pluginEnabler,
            @Named(PLUGIN_DEBUG) boolean debug) {
        mContext = context;
        mPm = context.getPackageManager();
        mActionManager = actionManager;
        mPluginEnabler = pluginEnabler;
        mDebug = debug;
        mPluginListeners = new ArrayMap<>();
    }
}
```

### 2.2 插件加载流程

```java
/**
 * 注册插件监听器
 * 
 * @param listener 插件监听器
 * @param cls      插件接口类
 * @param allowMultiple 是否允许多个插件
 */
@Override
public <T extends Plugin> void addPluginListener(
        PluginListener<T> listener, 
        Class<T> cls, 
        boolean allowMultiple) {
    
    // 1. 创建插件动作管理器
    PluginActionManager actionManager = mActionManager.create(
            listener, cls, allowMultiple);
    
    // 2. 保存监听器
    mPluginListeners.put(listener, actionManager);
    
    // 3. 查询插件
    queryPlugins(actionManager, cls);
}

/**
 * 查询可用插件
 */
private <T extends Plugin> void queryPlugins(
        PluginActionManager actionManager, 
        Class<T> cls) {
    
    // 1. 构建查询 Intent
    Intent intent = new Intent(PLUGIN_ACTION);
    intent.addCategory(cls.getName());
    
    // 2. 查询匹配的 Service
    List<ResolveInfo> resolves = mPm.queryIntentServices(
            intent, 
            PackageManager.GET_META_DATA);
    
    // 3. 过滤并加载插件
    for (ResolveInfo resolve : resolves) {
        // 检查是否启用
        if (!mPluginEnabler.isEnabled(resolve.serviceInfo)) {
            continue;
        }
        
        // 检查版本
        if (!checkVersion(resolve.serviceInfo)) {
            continue;
        }
        
        // 加载插件
        actionManager.loadPlugin(resolve.serviceInfo);
    }
}
```

### 2.3 addPluginListener 详解

```java
/**
 * addPluginListener 完整流程
 */
public <T extends Plugin> void addPluginListener(
        PluginListener<T> listener, 
        Class<T> cls) {
    addPluginListener(listener, cls, false);
}

/**
 * PluginListener 接口
 */
public interface PluginListener<T extends Plugin> {
    /**
     * 插件连接成功回调
     */
    void onPluginConnected(T plugin, PluginContext pluginContext);
    
    /**
     * 插件断开连接回调
     */
    void onPluginDisconnected(T plugin);
}
```

---

## 第 3 章 PluginInstance 源码分析

> 源码位置：`frameworks/base/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginInstance.java`

### 3.1 插件实例创建

```java
/**
 * PluginInstance - 插件实例
 * 
 * 源码：frameworks/base/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginInstance.java
 */
public class PluginInstance<T extends Plugin> {
    
    // SystemUI Context
    private final Context mSystemUIContext;
    
    // 插件信息
    private final ComponentName mComponentName;
    private final ApplicationInfo mAppInfo;
    
    // 插件实例
    private T mPlugin;
    
    // 插件 Context
    private Context mPluginContext;
    
    // 插件 ClassLoader
    private ClassLoader mClassLoader;
    
    /**
     * 创建插件实例
     */
    public void create() {
        // 1. 创建 ClassLoader
        mClassLoader = createClassLoader();
        
        // 2. 创建 Context
        mPluginContext = createPluginContext();
        
        // 3. 加载插件类
        Class<?> pluginClass = mClassLoader.loadClass(mComponentName.getClassName());
        
        // 4. 实例化
        mPlugin = (T) pluginClass.getDeclaredConstructor().newInstance();
        
        // 5. 调用 onCreate
        mPlugin.onCreate(mPluginContext);
    }
    
    /**
     * 销毁插件实例
     */
    public void destroy() {
        if (mPlugin != null) {
            mPlugin.onDestroy();
            mPlugin = null;
        }
        mPluginContext = null;
        mClassLoader = null;
    }
}
```

### 3.2 ClassLoader 创建流程

```java
/**
 * 创建插件 ClassLoader
 * 
 * 关键点：使用 DexClassLoader 加载插件 APK
 */
private ClassLoader createClassLoader() {
    // 1. 获取插件 APK 路径
    String apkPath = mAppInfo.sourceDir;
    // 例如: /data/app/com.example.plugin-1/base.apk
    
    // 2. 获取优化目录
    String optimizedDir = mSystemUIContext.getCodeCacheDir().getAbsolutePath();
    // 例如: /data/data/com.android.systemui/code_cache
    
    // 3. 获取 Native 库目录
    String nativeLibDir = mAppInfo.nativeLibraryDir;
    // 例如: /data/app/com.example.plugin-1/lib/arm64
    
    // 4. 获取父 ClassLoader (SystemUI 的 ClassLoader)
    ClassLoader parent = mSystemUIContext.getClassLoader();
    
    // 5. 创建 DexClassLoader
    return new DexClassLoader(
            apkPath,           // dexPath: 插件 APK 路径
            optimizedDir,      // optimizedDirectory: DEX 优化目录
            nativeLibDir,      // librarySearchPath: Native 库目录
            parent             // parent: 父 ClassLoader
    );
}
```

**ClassLoader 层级结构：**

```
                    BootClassLoader
                    (系统启动类)
                         │
                         ▼
                  PathClassLoader
                  (SystemUI ClassLoader)
                         │
                         ▼
                DexClassLoader
                (Plugin ClassLoader)
                         │
                         ▼
                   插件类加载

类加载顺序 (双亲委派)：
1. DexClassLoader 检查是否已加载
2. 委派给 PathClassLoader (SystemUI 类)
3. 委派给 BootClassLoader (Framework 类)
4. DexClassLoader 自己加载 (插件类)
```

### 3.3 Context 创建流程

```java
/**
 * 创建插件 Context
 * 
 * 关键点：使用 createPackageContext 创建独立的 Context
 */
private Context createPluginContext() {
    try {
        // 方式1: 使用 createPackageContext (推荐)
        Context pluginContext = mSystemUIContext.createPackageContext(
                mComponentName.getPackageName(),
                Context.CONTEXT_INCLUDE_CODE | Context.CONTEXT_IGNORE_SECURITY);
        
        // 返回包装后的 Context
        return new PluginContextWrapper(pluginContext, mClassLoader);
        
    } catch (PackageManager.NameNotFoundException e) {
        Log.e(TAG, "Failed to create plugin context", e);
        return null;
    }
}

/**
 * PluginContextWrapper - 插件 Context 包装器
 */
public class PluginContextWrapper extends ContextWrapper {
    private final ClassLoader mPluginClassLoader;
    private Resources mResources;
    
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
        if (mResources == null) {
            mResources = createPluginResources();
        }
        return mResources;
    }
    
    private Resources createPluginResources() {
        // 使用 AssetManager.addAssetPath 加载插件资源
        // ... 详见资源加载章节
    }
}
```

---

## 第 4 章 PluginActionManager 源码分析

> 源码位置：`frameworks/base/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginActionManager.java`

### 4.1 插件动作管理

```java
/**
 * PluginActionManager - 管理插件动作
 */
public class PluginActionManager<T extends Plugin> {
    
    private final Context mContext;
    private final PluginListener<T> mListener;
    private final Class<T> mPluginClass;
    private final Executor mExecutor;
    
    // 当前加载的插件
    private final List<PluginInstance<T>> mPlugins = new ArrayList<>();
    
    /**
     * 加载插件
     */
    public void loadPlugin(ServiceInfo serviceInfo) {
        mExecutor.execute(() -> {
            try {
                // 1. 创建插件实例
                PluginInstance<T> instance = new PluginInstance<>(
                        mContext, serviceInfo, mPluginClass);
                
                // 2. 初始化插件
                instance.create();
                
                // 3. 添加到列表
                mPlugins.add(instance);
                
                // 4. 通知监听器
                mListener.onPluginConnected(instance.getPlugin(), instance.getContext());
                
            } catch (Exception e) {
                Log.e(TAG, "Failed to load plugin: " + serviceInfo.name, e);
            }
        });
    }
    
    /**
     * 卸载插件
     */
    public void unloadPlugin(PluginInstance<T> instance) {
        mExecutor.execute(() -> {
            // 1. 通知监听器
            mListener.onPluginDisconnected(instance.getPlugin());
            
            // 2. 销毁插件
            instance.destroy();
            
            // 3. 从列表移除
            mPlugins.remove(instance);
        });
    }
}
```

### 4.2 插件生命周期

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    插件生命周期                                              │
└─────────────────────────────────────────────────────────────────────────────┘

1. 注册阶段
   SystemUI 调用 addPluginListener(listener, PluginClass.class)
         │
         ▼
   PluginManagerImpl 查询匹配的插件 Service
         │
         ▼
   创建 PluginActionManager

2. 加载阶段
   PluginActionManager.loadPlugin(serviceInfo)
         │
         ├─► 创建 PluginInstance
         │    │
         │    ├─► createClassLoader()  → DexClassLoader
         │    ├─► createPluginContext() → PluginContextWrapper
         │    ├─► loadClass()          → 加载插件类
         │    └─► newInstance()        → 创建插件实例
         │
         ▼
   plugin.onCreate(pluginContext)
         │
         ▼
   listener.onPluginConnected(plugin, context)

3. 运行阶段
   SystemUI 使用插件
         │
         ├─► 调用插件方法
         └─► 插件处理事件

4. 卸载阶段
   PluginActionManager.unloadPlugin(instance)
         │
         ├─► listener.onPluginDisconnected(plugin)
         │
         ▼
   plugin.onDestroy()
         │
         ▼
   释放资源 (ClassLoader, Context)
```

---

## 第 5 章 完整插件加载流程

### 5.1 时序图

```
┌────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────┐
│SystemUI│    │PluginManagerImpl│    │PluginActionManager│   │PluginInstance│
└───┬────┘    └────────┬────────┘    └────────┬─────────┘    └──────┬──────┘
    │                  │                      │                     │
    │ addPluginListener│                      │                     │
    │─────────────────►│                      │                     │
    │                  │                      │                     │
    │                  │ queryIntentServices  │                     │
    │                  │ (PackageManager)     │                     │
    │                  │                      │                     │
    │                  │ create(listener,cls) │                     │
    │                  │─────────────────────►│                     │
    │                  │                      │                     │
    │                  │                      │ loadPlugin()        │
    │                  │                      │────────────────────►│
    │                  │                      │                     │
    │                  │                      │                     │ createClassLoader()
    │                  │                      │                     │──────────────┐
    │                  │                      │                     │              │
    │                  │                      │                     │◄─────────────┘
    │                  │                      │                     │
    │                  │                      │                     │ createPluginContext()
    │                  │                      │                     │──────────────┐
    │                  │                      │                     │              │
    │                  │                      │                     │◄─────────────┘
    │                  │                      │                     │
    │                  │                      │                     │ loadClass()
    │                  │                      │                     │──────────────┐
    │                  │                      │                     │              │
    │                  │                      │                     │◄─────────────┘
    │                  │                      │                     │
    │                  │                      │                     │ newInstance()
    │                  │                      │                     │──────────────┐
    │                  │                      │                     │              │
    │                  │                      │                     │◄─────────────┘
    │                  │                      │                     │
    │                  │                      │                     │ plugin.onCreate()
    │                  │                      │                     │──────────────┐
    │                  │                      │                     │              │
    │                  │                      │                     │◄─────────────┘
    │                  │                      │                     │
    │                  │                      │ onPluginConnected() │
    │                  │◄─────────────────────│◄────────────────────│
    │                  │                      │                     │
    │ onPluginConnected│                      │                     │
    │◄─────────────────│                      │                     │
    │                  │                      │                     │
```

### 5.2 详细步骤

```
1. SystemUI 初始化
   ┌────────────────────────────────────────────────────────────────────────┐
   │ // StatusBar.java                                                       │
   │ PluginManager pluginManager = Dependency.get(PluginManager.class);     │
   │ pluginManager.addPluginListener(this, StatusBarPlugin.class);          │
   └────────────────────────────────────────────────────────────────────────┘

2. 查询插件
   ┌────────────────────────────────────────────────────────────────────────┐
   │ Intent intent = new Intent("com.android.systemui.action.PLUGIN");      │
   │ intent.addCategory("com.android.systemui.plugins.statusbar.StatusBarPlugin");│
   │ List<ResolveInfo> resolves = pm.queryIntentServices(intent, 0);        │
   └────────────────────────────────────────────────────────────────────────┘

3. 检查权限和版本
   ┌────────────────────────────────────────────────────────────────────────┐
   │ // 检查权限                                                             │
   │ pm.checkPermission("com.android.systemui.permission.PLUGIN", pkg);     │
   │                                                                        │
   │ // 检查版本                                                             │
   │ metaData.getInt("com.android.systemui.plugins.version");              │
   └────────────────────────────────────────────────────────────────────────┘

4. 创建 ClassLoader
   ┌────────────────────────────────────────────────────────────────────────┐
   │ DexClassLoader classLoader = new DexClassLoader(                       │
   │     apkPath,           // /data/app/com.plugin/base.apk               │
   │     optimizedDir,      // /data/data/com.android.systemui/code_cache  │
   │     nativeLibDir,      // /data/app/com.plugin/lib/arm64              │
   │     parentClassLoader  // SystemUI ClassLoader                        │
   │ );                                                                     │
   └────────────────────────────────────────────────────────────────────────┘

5. 创建 Context
   ┌────────────────────────────────────────────────────────────────────────┐
   │ Context pluginContext = context.createPackageContext(                 │
   │     pluginPackage,                                                     │
   │     CONTEXT_INCLUDE_CODE | CONTEXT_IGNORE_SECURITY                     │
   │ );                                                                     │
   └────────────────────────────────────────────────────────────────────────┘

6. 加载并实例化插件
   ┌────────────────────────────────────────────────────────────────────────┐
   │ Class<?> cls = classLoader.loadClass("com.plugin.MyStatusBarPlugin"); │
   │ Plugin plugin = (Plugin) cls.getDeclaredConstructor().newInstance();  │
   │ plugin.onCreate(pluginContext);                                        │
   └────────────────────────────────────────────────────────────────────────┘

7. 通知连接成功
   ┌────────────────────────────────────────────────────────────────────────┐
   │ listener.onPluginConnected(plugin, pluginContext);                     │
   └────────────────────────────────────────────────────────────────────────┘
```

---

## 第 6 章 插件开发实践

### 6.1 定义插件接口

```java
/**
 * 自定义插件接口
 * 
 * 位置：插件库中定义
 */
public interface CustomPlugin extends Plugin {
    /**
     * 获取自定义视图
     */
    View getCustomView();
    
    /**
     * 更新数据
     */
    void updateData(Bundle data);
}
```

### 6.2 实现插件

```java
/**
 * 插件实现
 */
public class MyCustomPlugin implements CustomPlugin {
    private Context mContext;
    private View mView;
    
    @Override
    public void onCreate(Context context, PluginListener listener) {
        mContext = context;
        
        // 使用插件 Context 加载布局
        mView = LayoutInflater.from(context)
                .inflate(R.layout.custom_plugin_layout, null);
    }
    
    @Override
    public void onDestroy() {
        // 清理资源
    }
    
    @Override
    public View getCustomView() {
        return mView;
    }
    
    @Override
    public void updateData(Bundle data) {
        // 更新 UI
    }
}
```

### 6.3 AndroidManifest 配置

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.plugin">
    
    <!-- 声明插件权限 -->
    <uses-permission android:name="com.android.systemui.permission.PLUGIN" />
    
    <application>
        
        <!-- 插件 Service -->
        <service
            android:name=".MyCustomPlugin"
            android:label="@string/plugin_name"
            android:permission="com.android.systemui.permission.PLUGIN">
            
            <intent-filter>
                <action android:name="com.android.systemui.action.PLUGIN" />
                <category android:name="com.example.plugin.CustomPlugin" />
            </intent-filter>
            
            <!-- 插件版本 -->
            <meta-data
                android:name="com.android.systemui.plugins.version"
                android:value="1" />
                
        </service>
        
    </application>
    
</manifest>
```

