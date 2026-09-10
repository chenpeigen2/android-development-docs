# SystemUI Plugin 插件化详解

> 作者：OpenClaw；全文修订：2026-09-10。源码基线固定为 AOSP `android-17.0.0_r1`。
> 本文分析 SystemUI 内部插件协议，不把普通应用动态加载、Android Service 生命周期与 SystemUI Plugin 生命周期混为一谈。代码注明“等价伪代码”时保留关键条件，但不是源码逐字摘录或独立可编译工程。

## 目录

- [第 1 章 SystemUI Plugin 概述](#第-1-章-systemui-plugin-概述)
  - [1.1 什么是 SystemUI Plugin](#11-什么是-systemui-plugin)
  - [1.2 Plugin 架构总览](#12-plugin-架构总览)
  - [1.3 核心类介绍](#13-核心类介绍)
- [第 2 章 PluginManagerImpl 源码分析](#第-2-章-pluginmanagerimpl-源码分析)
  - [2.1 类结构与依赖](#21-类结构与依赖)
  - [2.2 插件加载流程](#22-插件加载流程)
  - [2.3 addPluginListener 与移除](#23-addpluginlistener-与移除)
- [第 3 章 PluginInstance 源码分析](#第-3-章-plugininstance-源码分析)
  - [3.1 插件实例创建](#31-插件实例创建)
  - [3.2 ClassLoader 创建流程](#32-classloader-创建流程)
  - [3.3 Context 创建流程](#33-context-创建流程)
- [第 4 章 PluginActionManager 源码分析](#第-4-章-pluginactionmanager-源码分析)
  - [4.1 插件动作管理](#41-插件动作管理)
  - [4.2 插件生命周期](#42-插件生命周期)
- [第 5 章 完整插件加载流程](#第-5-章-完整插件加载流程)
  - [5.1 时序图](#51-时序图)
  - [5.2 详细步骤与故障定位](#52-详细步骤与故障定位)
- [第 6 章 插件开发实践](#第-6-章-插件开发实践)
  - [6.1 定义插件接口](#61-定义插件接口)
  - [6.2 实现插件与消费生命周期](#62-实现插件与消费生命周期)
  - [6.3 AndroidManifest 配置](#63-androidmanifest-配置)
- [第 7 章 状态、版本和异常恢复的实现细节](#第-7-章-状态版本和异常恢复的实现细节)
  - [7.1 PluginInstance 的真实字段与状态组合](#71-plugininstance-的真实字段与状态组合)
  - [7.2 版本契约的两个分支：返回 false 与抛出异常](#72-版本契约的两个分支返回-false-与抛出异常)
  - [7.3 PackageConfig 的包级含义与多候选分支](#73-packageconfig-的包级含义与多候选分支)
  - [7.4 两套错误状态：组件禁用与受保护调用失败](#74-两套错误状态组件禁用与受保护调用失败)
  - [7.5 未捕获异常预处理与包替换恢复](#75-未捕获异常预处理与包替换恢复)
- [第 8 章 懒加载监听用例与故障回归](#第-8-章-懒加载监听用例与故障回归)
  - [8.1 四阶段监听的完整消费示例](#81-四阶段监听的完整消费示例)
  - [8.2 回归场景与可观察结果](#82-回归场景与可观察结果)

---

## 第 1 章 SystemUI Plugin 概述

### 1.1 什么是 SystemUI Plugin

SystemUI Plugin 将特定扩展接口的实现放在单独安装的 APK 中，由 SystemUI 在自己的进程内加载。它适合平台开发、原型验证和已建立签名、接口版本及产品配置契约的厂商扩展；不是任意第三方 APK 都能接入的 Android SDK 扩展点。

“无需修改 SystemUI”有前提：宿主已经定义接口、注册监听器并实际消费接口返回值。仅在 APK 中实现某个类，并不会自动替换整个状态栏、导航栏或锁屏。若宿主没有消费该扩展点，仍然要修改宿主及其依赖注入配置。

插件 APK 是独立安装包，但**插件对象不是运行在插件进程的 Binder 服务**。PackageManager 的查询用于发现入口；类加载后，插件构造函数、初始化及宿主调用均在 SystemUI 进程执行。插件错误可能拖慢或破坏 SystemUI，ClassLoader 过滤不是隔离不可信代码的沙箱。

### 1.2 Plugin 架构总览

```text
安装的 plugin.apk
  manifest <service> + interface-specific action
       |
       | PackageManager.queryIntentServices(Intent(action), 0)
       v
SystemUI process
  PluginManagerImpl
    listener -> PluginActionManager<T>
                   | background: discover/filter/create lifecycle manager
                   | main: onPluginConnected(instance)
                   v
                PluginInstance<T>
                  + PluginFactory<T>: class loader/context/version
                  + PluginLifecycleManager<T>: load/unload
                  + PluginListener<T>: attach/load/unload/detach
                   |
                   v
                Plugin implementation object (same process)
```

`<service>` 在这里是 PackageManager 可解析的注册载体，不要求实现类继承 `android.app.Service`。`PluginActionManager.handleQueryPlugins()` 的注释明确说明不应该真正启动这个 Service。不要调用 `startService()` 或 `bindService()` 来启动该实现类，也不要期待收到 `Service.onStartCommand()`。

### 1.3 核心类介绍

该 tag 的文件划分如下，不能使用旧 Java 后缀伪装当前源码：

```text
frameworks/base/packages/SystemUI/
  plugin_core/src/com/android/systemui/plugins/
    Plugin.kt
    PluginListener.kt
    PluginLifecycleManager.kt
    PluginManager.kt
  plugin/src/com/android/systemui/plugins/
    ... 具体扩展接口，例如 DozeServicePlugin
  shared/src/com/android/systemui/shared/plugins/
    PluginManagerImpl.kt
    PluginActionManager.kt
    PluginInstance.kt
    PluginEnabler.kt
    PluginEnvironment.kt
    PackageConfig.kt
    VersionChecker.kt
    VersionInfo.kt
```

| 类型 | 责任 | 不承担的责任 |
|---|---|---|
| `PluginManagerImpl` | 为 listener 建立 action manager、处理包变化、崩溃禁用入口 | 不直接查询所有 service 后用统一 action 加 category |
| `PluginActionManager` | 按 action 查询、检查许可、维护实例集合、切换执行器 | 不启动 Android Service |
| `PluginInstance` | 插件对象与生命周期、加载状态、失败状态 | 不是 APK 安装器 |
| `PluginFactory`（位于 `PluginInstance.kt`） | ClassLoader、对象、Context 和版本校验 | 不提供进程隔离 |
| `VersionChecker` / `VersionInfo` | 接口及依赖版本契约 | 不是读取一个任意 manifest version 整数即可 |
| `PackageConfig` / `PluginEnabler` | 产品特权列表与组件启用状态 | 不替代签名权限检查 |

## 第 2 章 PluginManagerImpl 源码分析

### 2.1 类结构与依赖

`PluginManagerImpl.kt` 实现 `PluginManager`，同时接收包事件广播。核心关系是 `pluginMap: listener -> PluginActionManager`，而非只有一个全局 `mActionManager`。不同接口拥有不同 action、目标 `Class<T>` 和 `allowMultiple` 配置，必须分别查询、分别控制生命周期。

其依赖包括宿主 Context、`PluginActionManager.Factory`、插件启用器、偏好记录和 `PackageConfig` 等。使用 factory 的意义是为每次注册绑定不可混用的参数；不能把示意构造器误写成固定 AOSP 的 `@Inject PluginManagerImpl(Context, PluginActionManager, ...)`。

### 2.2 插件加载流程

调用链的关键是先从接口取得 action，再建立 action manager：

```text
PluginManagerImpl.addPluginListener(listener, cls, allowMultiple)
  -> PluginManager.Helper.getAction(cls)
  -> addPluginListener(action, listener, cls, allowMultiple)
       -> pluginPrefs.addAction(action)
       -> actionManagerFactory.create(...).apply { loadAll() }
       -> synchronized: pluginMap.put(listener, actionManager)
       -> startListening()
```

`loadAll()` 把查询提交给后台执行器。提交任务不等于监听器已收到插件，更不保证 `addPluginListener()` 返回时插件可用。使用方只能在 `onPluginLoaded()` 后访问实例，在 `onPluginUnloaded()` 后停止访问。

action 来自插件接口的契约，例如接口上的 `@ProvidesInterface(action=..., version=...)`。没有“所有插件统一用 `com.android.systemui.action.PLUGIN`，再把接口类名放入 category”的协议。category 既不替代接口注解，也不替代版本校验。

### 2.3 addPluginListener 与移除

注册为一个接口建立消费关系；`allowMultiple=false` 不代表随意取查询结果第一项。`handleQueryPlugins()` 在出现多个候选且不允许多实例时拒绝加载该批候选，避免随安装顺序选择不同实现。

移除的实际路径是：

```text
removePluginListener(listener)
  -> pluginMap.remove(listener)?.destroy()
  -> map empty ? stopListening() : keep package receiver
```

`destroy()` 会安排已持有实例的主线程销毁。调用方仍应处理生命周期回调，清理视图、监听器、异步任务与缓存引用。不要以为 map 中删掉一个 key 就能强制释放插件加载器。

包增加、更新、改变会触发 `reloadPackage(pkg)`；移除走 `onPackageRemoved(pkg)`；用户解锁可触发 `loadAll()`。这解释了为什么插件要支持多轮 attach/load/unload/detach，而不是按应用 `Application.onCreate()` 的“一生一次”模型设计。

## 第 3 章 PluginInstance 源码分析

### 3.1 插件实例创建

`PluginInstance.Factory.create()` 先建立生命周期管理对象，内部持有 `PluginFactory`。创建 manager 与真正执行插件构造函数是两个阶段。

```text
PluginInstance.Factory.create(hostContext, appInfo, component, cls, listener)
  -> 产品环境与 privileged package 检查
  -> PluginInstance(..., PluginFactory(...), env)

主线程 PluginInstance.onCreate()
  -> hasError ? return
  -> listener.onPluginAttached(manager)
       false: 不自动加载，必要时卸载旧 pluginData
       true: 如果尚未加载，调用 loadPlugin()
```

`loadPlugin()` 的主要步骤如下，注意 Context 创建、版本检查和通知使用方的先后关系：

```kotlin
// 等价伪代码：省略同步注解、日志与防护包装内部实现。
fun loadPlugin() {
    if (hasError || pluginData != null) return
    val objectInstance = pluginFactory.createPlugin(this) ?: return
    val context = pluginFactory.createPluginContext() ?: return
    if (!checkVersion(objectInstance)) return
    pluginData = PluginData(objectInstance, context)
    if (objectInstance !is PluginFragment) {
        objectInstance.onCreate(hostContext, context)
    }
    listener.onPluginLoaded(objectInstance, context, this)
}
```

`createPlugin()` 经 `Class.forName(componentName.className, true, loader)` 初始化类并由 instance factory 构造。非测试环境还可能由 `protectIfAble()` 为受保护接口包装代理；版本检查会识别 `PluginWrapper` 并检查底层实例。不要把“有异常防护”理解为所有插件异常都不会传播或宿主一定能恢复。

版本检查返回 false 时会标记错误并卸载/detach；注解版本检查还可能直接抛出异常，不能保证所有失败都走完同一清理序列。受保护调用的 onFail 另行持久化失败信息以避免重启循环，历史失败是否生效取决于 PluginEnvironment 与超时；详见第 7 章。

### 3.2 ClassLoader 创建流程

固定 tag 的 `PluginFactory.createClassLoader()` 使用 **PathClassLoader**，不是 DexClassLoader：

```text
LoadedApk.makePaths(null, true, pluginAppInfo, zipPaths, libPaths)
  -> 从 ApplicationInfo 组装 APK/split/相关路径与 native 搜索路径
ClassLoaderFilter(baseClassLoader, FILTERED_PACKAGES,
                  ClassLoader.getSystemClassLoader())
  -> PathClassLoader(join(zipPaths), join(libPaths), filteredLoader)
```

`ClassLoaderFilter` 本身有系统类加载器作为 parent；在自己的 `findClass()` 中只把匹配指定包前缀的类委派给宿主提供的 base loader。Android 17 中过滤项不仅包括 plugin 接口，还涉及 Compose、日志及部分共享类型。应以 `FILTERED_PACKAGES` 为准，不应写成“任何宿主实现类都对子插件可见”。

```text
plugin PathClassLoader
   -> filtered parent ClassLoader
        -> system class loader / framework classes
        -> findClass: allowed prefix -> host baseClassLoader
   -> plugin APK paths: concrete implementation
```

共享 API 必须只由约定的加载器定义。插件构建时应将接口作为只编译依赖，避免又打入相同类名导致类型身份不一致。Java/Kotlin 的类型身份包含定义它的 ClassLoader，类名相同并不保证可强制转换。

这条链也不需要 `optimizedDirectory`。在通用应用使用 DexClassLoader 时，该参数自 API 26 起无效；把 SystemUI code_cache 路径当成当前插件加载必要条件是两重错误。

另一个容易误读的细节：此 tag 的 `createPlugin()` 和 `createPluginContext()` 各自调用 `createClassLoader()`，并不能从接口设计推断“内部一定缓存并共享同一个 ClassLoader 对象”。自定义类型跨边界时，更应遵守宿主共享契约，不能依赖对象身份巧合。

### 3.3 Context 创建流程

当前路径为：

```text
PluginFactory.createPluginContext()
  -> createClassLoader()
  -> hostContext.createApplicationContext(pluginAppInfo, 0)
  -> PluginContextWrapper(applicationContext, loader)
```

这里没有 `CONTEXT_IGNORE_SECURITY`，也不是通过反射 `AssetManager.addAssetPath()` 手工拼资源。base Context 对应插件 ApplicationInfo，提供插件包资源；wrapper 改写 `getClassLoader()`，并为 `LAYOUT_INFLATER_SERVICE` 返回在 wrapper 中克隆的 inflater。

```kotlin
// 结构化摘意：资源依旧由 baseContext 提供。
class PluginContextWrapper(
    base: Context,
    private val loader: ClassLoader,
) : ContextWrapper(base) {
    private val pluginInflater by lazy {
        LayoutInflater.from(baseContext).cloneInContext(this)
    }
    override fun getClassLoader(): ClassLoader = loader
    override fun getSystemService(name: String): Any? =
        if (name == LAYOUT_INFLATER_SERVICE) pluginInflater
        else baseContext.getSystemService(name)
}
```

为何同时给 `hostContext` 和 `pluginContext`？宿主上下文与插件资源、主题和自定义 View 的解析环境不同。`Plugin.onCreate(hostContext, pluginContext)` 明确提供二者，插件加载自身布局通常选后者。旧文中的单参数 `onCreate(pluginContext)` 或 `onCreate(Context, PluginListener)` 均不匹配此接口。

Context 的包资源来源不改变 Linux UID 或执行进程。插件仍然在宿主安全上下文中运行，不能通过 ContextWrapper 获得隔离执行能力。

## 第 4 章 PluginActionManager 源码分析

### 4.1 插件动作管理

`loadAll()` -> 后台 `queryAll()` -> `handleQueryPlugins(null)`。查询前，管理器会安排旧实例断开并清空其实例集合。按包更新则先 `removePkg(pkg)`，再 `queryPkg(pkg)`。

`loadPluginComponent(component)` 至少检查以下三道不同的门槛：

1. **产品配置**：非 debuggable 环境不能加载非 privileged component；factory 还检查 privileged package。
2. **启用状态**：`PluginEnabler.isEnabled(component)` 必须成立。安装成功不等于已启用。
3. **权限**：`PackageManager.checkPermission(PLUGIN_PERMISSION, packageName)` 必须授予。SystemUI manifest 把该权限定义为 `signature`。

检查通过后获取 `ApplicationInfo`，构造 `PluginInstance` 并加入集合，随后通过 main executor 调用 `onPluginConnected(instance)`，该方法实际调用 `instance.onCreate()`。

不要将 manifest 中的 `android:permission` 与 `uses-permission` 混淆。前者限制谁能访问声明的组件，后者表示插件申请权限；SystemUI 这里检查的是**插件包已经持有该权限**。写上任一 XML 属性都不能绕过签名授权。

### 4.2 插件生命周期

Android 17 `PluginListener.kt` 以四阶段回调为主：

```text
onPluginAttached(manager)        // 可决定懒加载
  -> manager.loadPlugin()
       -> Plugin.onCreate(hostContext, pluginContext)
       -> onPluginLoaded(plugin, context, manager)
  -> 使用插件
  -> manager.unloadPlugin()
       -> onPluginUnloaded(plugin, manager)
       -> Plugin.onDestroy()    // PluginFragment 由其 Fragment 生命周期处理
  -> onPluginDetached(manager)  // 不再对旧 manager 请求 reload
```

`onPluginConnected()` / `onPluginDisconnected()` 仍作为弃用兼容回调存在。默认的 `onPluginLoaded()` / `onPluginUnloaded()` 会转发旧回调，因此旧消费者仍能工作；新教程不应只给两阶段接口冒充完整协议。

attached 不等于 loaded：监听器返回 false 时可以持有 manager，稍后按需求加载。unloaded 也不必然 detached：同一 manager 可以卸载实例后重新加载。包替换或失败则可能结束 manager 的有效期，需要消费新一轮 attached。

正常卸载先通知宿主撤走 UI 和引用，再调用插件 `onDestroy()`，最后清空 `pluginData`。插件必须取消自己注册的 listener、Handler 回调、协程和 native 资源；否则逻辑卸载完成而对象仍被引用，代码及资源不会及时回收。

## 第 5 章 完整插件加载流程

### 5.1 时序图

```text
Host/Main         PluginManager        ActionManager/BG       Instance/Main
   | register            |                    |                    |
   |-------------------->| create + loadAll   |                    |
   |                     |------------------->| query services     |
   |                     |                    | product/enabled/   |
   |                     |                    | permission checks  |
   |                     |                    | create manager     |
   |                     |                    |------------------->|
   |<-------------------------------------------------- attached --|
   | return true         |                    |                    |
   |                     |                    |  createPlugin +    |
   |                     |                    |  context + version |
   |                     |                    |  plugin.onCreate   |
   |<---------------------------------------------------- loaded --|
   | use plugin          |                    |                    |
   | unregister / package update              |                    |
   |                     | destroy/removePkg  |                    |
   |                     |------------------->|------------------->|
   |<-------------------------------------------------- unloaded --|
   |                     |                    |  plugin.onDestroy  |
   |<-------------------------------------------------- detached --|
```

这张图表示管理器通常采用的执行器调度，不表示 API 的所有公开方法自动切主线程。`PluginInstance` 的 load/unload 方法有同步保护，但同步锁不是线程切换。消费方主动调用 manager 时仍应遵守宿主的主线程/UI 约定。

### 5.2 详细步骤与故障定位

从“查不到插件”到“已加载但界面不显示”，要区分失败所在层次：

- **发现失败**：先核对实际接口 action 与 manifest action，再看包可见性、服务声明、用户和安装状态；不要首先怀疑 Dex。
- **拒绝加载**：检查 debuggable、privileged 配置、组件启用和签名权限。non-privileged 在 user build 上被拒绝是设计行为。
- **类加载失败**：核对实现类名、APK/split 路径及只编译的共享 API；检查初始化异常、ABI 与 native 依赖。
- **版本失败**：核对接口版本与其依赖，注意 `@Requires`、保护接口包装及新旧宿主组合；不是递增 manifest 元数据就能修复。
- **回调成功但无 UI**：检查 host 是否消费返回 View、插件 inflater 是否使用正确 Context、View 是否还挂在旧 parent。
- **更新后仍引用旧实现**：检查 unloaded/detached 的清理和外部缓存，不应继续调用旧 manager。

验证顺序应包含安装、启用、加载、更新重载、禁用、卸载、多候选冲突和接口不兼容。本文只做固定 tag 静态源码核验，没有在设备上执行上述回归。

## 第 6 章 插件开发实践

### 6.1 定义插件接口

以下为**宿主自定义扩展点示例**，`CustomPlugin` 并非 AOSP 已有接口。接口及其 action 由宿主和插件共同约定，实际工程还要让宿主注册并显示该 View。

```kotlin
@ProvidesInterface(action = CustomPlugin.ACTION, version = CustomPlugin.VERSION)
interface CustomPlugin : Plugin {
    fun getCustomView(): View
    fun updateData(data: Bundle)

    companion object {
        const val ACTION = "com.example.systemui.action.CUSTOM_PLUGIN"
        const val VERSION = 1
    }
}
```

接口类需要处于宿主提供的共享 API/过滤范围，或者同步调整宿主 ClassLoader 契约。随便把接口定义在未共享的包里，再在两个 APK 各自打包，会造成类型转换失败。该改动属于平台构建配置，不是普通应用 SDK 设置。

### 6.2 实现插件与消费生命周期

```kotlin
// 插件端。共享 Plugin/CustomPlugin 库只参与编译，不重复打包。
@Requires(target = CustomPlugin::class, version = CustomPlugin.VERSION)
class MyCustomPlugin : CustomPlugin {
    private var view: TextView? = null

    override fun onCreate(hostContext: Context, pluginContext: Context) {
        // 示例用系统 TextView；真实资源由 pluginContext 解析。
        view = TextView(pluginContext).apply { text = "插件已加载" }
    }

    override fun getCustomView(): View = checkNotNull(view)

    override fun updateData(data: Bundle) {
        view?.text = data.getString("text").orEmpty()
    }

    override fun onDestroy() {
        // 真实插件还应取消自己的异步任务、监听器与 native 资源。
        view = null
    }
}
```

```kotlin
// 宿主端示例：container 与 manager 由宿主注入，调用发生在主线程。
class CustomPluginHost(
    private val manager: PluginManager,
    private val container: ViewGroup,
) : PluginListener<CustomPlugin> {
    private var attachedView: View? = null

    fun start() {
        manager.addPluginListener(this, CustomPlugin::class.java, false)
    }

    override fun onPluginLoaded(
        plugin: CustomPlugin,
        pluginContext: Context,
        manager: PluginLifecycleManager<CustomPlugin>,
    ) {
        val view = plugin.getCustomView()
        check(view.parent == null) { "Plugin view already attached" }
        container.addView(view)
        attachedView = view
    }

    override fun onPluginUnloaded(
        plugin: CustomPlugin,
        manager: PluginLifecycleManager<CustomPlugin>,
    ) {
        attachedView?.let(container::removeView)
        attachedView = null
    }

    fun stop() {
        manager.removePluginListener(this)
    }
}
```

此示例展示生命周期配对，不包含产品签名、Soong/Gradle 接口库配置和权限授权操作。不能把代码片段当成任意商业设备均可安装运行的插件工程。

### 6.3 AndroidManifest 配置

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.plugin">
    <uses-permission android:name="com.android.systemui.permission.PLUGIN" />
    <application android:label="Custom SystemUI Plugin">
        <!-- 仅供 PackageManager 发现，不能作为 Android Service 启动。 -->
        <service
            android:name=".MyCustomPlugin"
            android:exported="true"
            android:permission="com.android.systemui.permission.PLUGIN">
            <intent-filter>
                <action android:name="com.example.systemui.action.CUSTOM_PLUGIN" />
            </intent-filter>
        </service>
    </application>
</manifest>
```

带 intent-filter 的组件显式写出 exported；action 必须匹配接口。不需要虚构的 `com.android.systemui.plugins.version` 元数据，也不需要用 category 放接口类名。签名权限、系统插件开关以及生产构建特权列表须另行满足。

`android:permission` 对误启动者增加访问限制，但 SystemUI 发现路径仍然不启动此组件。若应用希望真的提供 Binder IPC Service，应另声明一个继承 Service 的类，并设计独立协议，不要混用这里的插件入口。


**固定 tag 源码证据：**

- [PluginManagerImpl.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginManagerImpl.kt)
- [PluginActionManager.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginActionManager.kt)
- [PluginInstance.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginInstance.kt)
- [Plugin.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/plugin_core/src/com/android/systemui/plugins/Plugin.kt)
- [PluginListener.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/plugin_core/src/com/android/systemui/plugins/PluginListener.kt)
- [PluginLifecycleManager.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/plugin_core/src/com/android/systemui/plugins/PluginLifecycleManager.kt)
- [VersionChecker.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/VersionChecker.kt)
- [PackageConfig.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PackageConfig.kt)
- [AndroidManifest.xml](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/AndroidManifest.xml)


## 第 7 章 状态、版本和异常恢复的实现细节

本章补足前面主链路中不能省略的边界。以下代码来自同一个 Android 17 tag，不再用旧版 Java 字段或两回调模型替代当前 Kotlin 实现。

### 7.1 PluginInstance 的真实字段与状态组合

核心状态不是一个统一的 `mPlugin != null`。构造依赖包含 hostContext、listener、componentName、pluginFactory 和 env；实例保存 `PluginData<T>(plugin, context)`，用 `pluginData` 表示当前已加载对象，同时用 `hasError` 表示错误状态。`plugin` 与 `pluginContext` 的 getter 在错误状态下返回 null。

```text
发现候选 -> 创建 PluginInstance
  hasError = loadFailure()
    true  -> 不再发送正常 attached/load；需要走恢复条件
    false -> onCreate -> listener.onPluginAttached
               false -> attached but unloaded（懒加载）
               true  -> loadPlugin
                          pluginData != null: 已有实例
                          pluginData == null: 创建/校验/初始化
成功使用 -> unloadPlugin -> attached but unloaded
管理器销毁 -> unloadPlugin -> detached
受保护调用失败 -> storeFailure -> hasError -> unload -> detached
```

这些是语义状态，并非源码中另有一个同名枚举。管理器存在不代表对象存在；`onPluginUnloaded` 不等于已经 detach。UI 应把“正在显示的 View”与“允许请求加载的 lifecycle manager”分开持有，否则懒加载、包重载与失败恢复会混淆。

下面保留实际 load/check/unload 分支及其顺序：


源码：[PluginInstance.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginInstance.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
override fun loadPlugin() {
    if (hasError) {
        logger.w("Previous Fatal Exception detected for plugin class")
        return
    }

    if (pluginData != null) {
        logger.d("Load request when already loaded")
        return
    }

    // Both of these calls take about 1 - 1.5 seconds in test runs
    val plugin = pluginFactory.createPlugin(this)
    val pluginContext = pluginFactory.createPluginContext()
    if (plugin == null || pluginContext == null) {
        logger.e("Requested load, but failed")
        return
    }

    if (!checkVersion(plugin)) {
        logger.e("loadPlugin: version check failed")
        return
    }

    pluginData = PluginData(plugin, pluginContext)

    logger.e("Loaded plugin; running callbacks")
    if (plugin !is PluginFragment) {
        // Only call onCreate for plugins that aren't fragments, as fragments
        // will get the onCreate as part of the fragment lifecycle.
        plugin.onCreate(hostContext, pluginContext)
    }
    listener.onPluginLoaded(plugin, pluginContext, this)
}

private fun checkVersion(plugin: T): Boolean {
    if (hasError) return false
    if (pluginFactory.checkVersion(plugin)) return true

    logger.wtf({ "Version check failed for '$str1'" }) { str1 = debugName }
    hasError = true
    unloadPlugin()
    listener.onPluginDetached(this)
    return false
}

override fun unloadPlugin() {
    val (plugin, _) =
        pluginData
            ?: run {
                logger.d("Unload request when already unloaded")
                return
            }

    logger.i("Unloading plugin, running callbacks")
    listener.onPluginUnloaded(plugin, this)
    if (plugin !is PluginFragment) {
        // Only call onDestroy for plugins that aren't fragments, as fragments
        // will get the onDestroy as part of the fragment lifecycle.
        plugin.onDestroy()
    }
    pluginData = null
}
```

注意 `pluginData` 在 plugin.onCreate 之前建立。如果初始化或监听回调抛出未受保护异常，不能从这段代码推导“一定完整回滚到 null”；它没有覆盖所有调用的统一 try/finally。宿主和插件必须自行遵守异常与清理契约，测试不能只覆盖正常卸载。

`@Synchronized`（源码中位于这些方法前）用于互斥，不会把调用转到 main executor，也不会让外部持有的 View 引用自动安全。触发懒加载的宿主仍应在约定线程调用，避免把重型类初始化藏在关键动画帧中。

### 7.2 版本契约的两个分支：返回 false 与抛出异常

当前 VersionChecker 不是简单读取 `Plugin.VERSION`。它先为接口和实现构建 VersionInfo：实现存在注解版本信息时递归检查依赖；否则在 plugin 非空时走旧 version fallback。


源码：[VersionChecker.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/VersionChecker.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
override fun <T : Plugin> checkVersion(
    instanceClass: Class<T>,
    pluginClass: Class<T>,
    plugin: Plugin?,
): Boolean {
    val pluginVersion = VersionInfo(pluginClass)
    val instanceVersion = VersionInfo(instanceClass)
    if (instanceVersion.hasVersionInfo) {
        pluginVersion.checkVersion(instanceVersion)
    } else if (plugin != null) {
        val fallbackVersion = plugin.version
        if (fallbackVersion != pluginVersion.defaultVersion) {
            return false
        }
    }
    return true
}
```

**这两条失败路径不同：**fallback 数字不匹配返回 false；注解分支的 `VersionInfo.checkVersion()` 会抛出 InvalidVersionException。PluginInstance 的局部 checkVersion 包装中，false 分支设置 hasError、卸载并 detach，但它没有把所有抛出的异常转成 false，因此不能承诺每次版本失败都正常走完这组回调。

VersionInfo 以 Class 为 key 记录版本和 required 状态。`@ProvidesInterface`、`@Requires`、`@Requirements`、`@DependsOn`、`@Dependencies` 分别提供接口版本、声明需求以及递归依赖。递归中使用 containsKey 避免重复加入：


源码：[VersionInfo.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/VersionInfo.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
fun checkVersion(plugin: VersionInfo) {
    val versions = versions.toMutableMap()
    plugin.versions.forEach { (aClass, version) ->
        val v =
            versions.remove(aClass)
                ?: createVersion(aClass)
                ?: throw InvalidVersionException(
                    "${aClass.simpleName} does not provide an interface",
                    isTooNew = false,
                )

        if (v.version != version.version) {
            throw InvalidVersionException(
                aClass,
                isTooNew = v.version < version.version,
                expectedVersion = v.version,
                actualVersion = version.version,
            )
        }
    }

    versions.forEach { (aClass, version) ->
        if (version.isRequired) {
            throw InvalidVersionException(
                "Missing required dependency ${aClass.simpleName}",
                isTooNew = false,
            )
        }
    }
}

private fun MutableMap<Class<*>, Version>.addClass(cls: Class<*>, isRequired: Boolean) {
    if (containsKey(cls)) return
    cls.getDeclaredAnnotation<ProvidesInterface>()?.let { annotation ->
        this[cls] = Version(annotation.version, isRequired = true)
    }
    cls.getDeclaredAnnotation<Requires>()?.let { annotation ->
        this[annotation.target.java] = Version(annotation.version, isRequired)
    }
    cls.getDeclaredAnnotation<Requirements>()?.let { annotation ->
        annotation.value.forEach { this[it.target.java] = Version(it.version, isRequired) }
    }
    cls.getDeclaredAnnotation<DependsOn>()?.let { annotation ->
        addClass(annotation.target.java, isRequired = true)
    }
    cls.getDeclaredAnnotation<Dependencies>()?.let { annotation ->
        annotation.value.forEach { addClass(it.target.java, isRequired = true) }
    }
}
```

缺失 required dependency、接口未提供版本、接口预期与实现声明不一致都可能失败。`isTooNew` 区分实现要求比宿主更新的情况，不意味着任意低版本都兼容。不要在宿主遇到错误时直接删除注解“让它通过”：这会把显式兼容检查变成潜在 NoSuchMethodError/语义不匹配。

构建时应把接口 artifact、依赖注解和宿主实现一起纳入兼容矩阵。只把 APK 的 versionCode 加一不会改变这些接口契约；相同类名由不同 ClassLoader 定义也会破坏以 Class 为 key 的关系。

### 7.3 PackageConfig 的包级含义与多候选分支

privileged 配置同时维护包集合和组件集合。传入可解析组件名时，该组件的包也会进入包集合；`isPrivileged(component)` 还检查包集合。因此不能将配置里的一个组件字符串解读为“严格只允许此组件、同包其余组件必然被拒绝”。权限和启用状态检查仍独立存在。


源码：[PackageConfig.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PackageConfig.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
class PackageConfig(vararg privilegedNames: String) {
    private val privilegedPackages: Set<String>
    private val privilegedComponents: Set<ComponentName>

    init {
        val packages = mutableSetOf<String>()
        val components = mutableSetOf<ComponentName>()
        for (name in privilegedNames) {
            val component = ComponentName.unflattenFromString(name)
            if (component != null) {
                components.add(component)
                packages.add(component.packageName)
            } else {
                packages.add(name)
            }
        }

        privilegedPackages = packages
        privilegedComponents = components
    }

    fun isPrivileged(pluginName: ComponentName): Boolean {
        return pluginName in privilegedComponents || isPackagePrivileged(pluginName.packageName)
    }

    fun isPackagePrivileged(packageName: String): Boolean {
        return packageName in privilegedPackages
    }
}
```

候选冲突由 action manager 处理：`allowMultiple=false` 不是随便选查询结果第一项。包定向查询也要与已经存在的实例数结合检查。实际查询分支如下：


源码：[PluginActionManager.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginActionManager.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
private fun queryPkg(pkg: String) {
    logger.d({ "queryPkg($str1)" }) { str1 = pkg }
    if (allowMultiple || (pluginInstances.size == 0)) {
        handleQueryPlugins(pkg)
    } else {
        logger.d("Too many matching packages found")
    }
}

private fun handleQueryPlugins(pkgName: String?) {
    // This isn't actually a service and shouldn't ever be started, but is
    // a convenient PM based way to manage our plugins.
    val intent = Intent(action)
    if (pkgName != null) {
        intent.setPackage(pkgName)
    }
    val result = packageManager.queryIntentServices(intent, 0)
    var logLevel = if (result.size <= 0) LogLevel.DEBUG else LogLevel.INFO
    val logMessage = buildString {
        append("Found ")
        append(result.size)
        append(" plugins")

        if (result.size > 1 && !allowMultiple) {
            append(", but multiple plugins are disallowed.")
            logLevel = LogLevel.ERROR
        }

        append(" ($env)")

        for (info in result) {
            val name = ComponentName(info.serviceInfo.packageName, info.serviceInfo.name)
            append("\n $name")

            if (logLevel != LogLevel.ERROR) {
                val pluginInstance = loadPluginComponent(name)
                if (pluginInstance != null) {
                    // add plugin before sending PLUGIN_CONNECTED message
                    pluginInstances.add(pluginInstance)
                    mainExecutor.execute { onPluginConnected(pluginInstance) }
                }
            }
        }
    }

    logger.log(logLevel, logMessage)
}
```

因此排查“安装第二个插件后原插件也不显示”时，需要记录完整候选列表、allowMultiple 和触发的是全量查询还是按包更新，而不是把结果随机性归因于 ClassLoader。候选的顺序不应成为产品选择策略；需要明确单选或多实例消费协议。

### 7.4 两套错误状态：组件禁用与受保护调用失败

组件启用状态由 PluginEnabler 管理，其真实枚举同时携带持久值和 autoEnable 属性：


源码：[PluginEnabler.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginEnabler.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
enum class DisableReason(val value: Int, val autoEnable: Boolean) {
    ENABLED(0, autoEnable = true),
    DISABLED_MANUALLY(1, autoEnable = false),
    DISABLED_INVALID_VERSION(2, autoEnable = true),
    DISABLED_FROM_EXPLICIT_CRASH(3, autoEnable = true),
    DISABLED_FROM_SYSTEM_CRASH(4, autoEnable = true),
    DISABLED_UNKNOWN(100, autoEnable = false);

    companion object {
        private val valueMap by lazy { entries.associateBy { it.value } }

        fun fromValue(value: Int): DisableReason = valueMap[value] ?: DISABLED_UNKNOWN
    }
}
```

手工禁用与 unknown 不应被普通自动恢复覆盖；invalid version、归因插件崩溃与系统崩溃的枚举允许相应恢复分支。这里的 autoEnable 只表示分支资格，不保证每次 PACKAGE_REPLACED 都一定启用。

另一路是 PluginInstance 的受保护接口失败。`onFail()` 先同步保存失败时间、信息及最多 20 个栈帧，再置 hasError，卸载并 detach；它旨在避免进程重启后立刻再次触发同一失败：


源码：[PluginInstance.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginInstance.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
override fun onFail(className: String, methodName: String, failure: Throwable): Boolean {
    logger.e({ "Failure from '$str1'. Disabling Plugin." }, failure) { str1 = debugName }

    storeFailure(failure)
    hasError = true
    unloadPlugin()
    listener.onPluginDetached(this)
    return true
}

private fun storeFailure(failure: Throwable) {
    getSharedPreferences().edit(commit = true) {
        clear()
        putLong(FAIL_TIME, System.currentTimeMillis())
        putString(FAIL_MESSAGE, failure.message)
        var i = 0
        while (i < failure.stackTrace.size && i < FAIL_MAX_STACK) {
            putString("Stack[$i]", "${failure.stackTrace[i]}")
            i++
        }
    }
}

private fun loadFailure(): Boolean {
    val sharedPrefs = getSharedPreferences()

    if (env.isEng || env.isTestMode) {
        hasError = false
        return false
    }

    // TODO(b/438515243): Check apk checksums for differences (systemui & plugin)
    // If the failure occurred too long ago, we ignore it to check if it's still happening.
    if (sharedPrefs.getLong(FAIL_TIME, 0) < System.currentTimeMillis() - FAIL_TIMEOUT_MILLIS) {
        hasError = false
        return false
    }

    // Log previous the failure so that it appears in new bugreports
    logger.e({ "Disabling Plugin '$str1' due to persisted failure '$str2'" }) {
        str1 = debugName
        str2 = sharedPrefs.getString(FAIL_MESSAGE, "Unknown")
    }

    hasError = true
    return true
}
```

该 tag 使用 `PluginFailure_$debugName` SharedPreferences；24 小时超时决定旧失败是否仍然阻止加载，eng/test 模式绕过该历史失败。代码还有 APK checksum 检测 TODO，因此不能承诺“重新安装了 APK 就必定立即清掉 PluginInstance 失败记录”。这套记录和 PluginEnabler 的组件状态不是同一个存储。

工程上要同时观察：组件是否 enabled、是否存在近期 failure、是否创建了新 manager、listener 是否仍持有旧 manager。只执行一次启用操作而保留旧错误实例，不能等同恢复已成功。

### 7.5 未捕获异常预处理与包替换恢复

PluginManagerImpl 的异常预处理器会扫描栈及 cause，尝试禁用涉及的非特权插件；无法归因时保守禁用可禁用的插件。测试模式绕过此行为，特权插件也有特殊处理。它不是对任意异常的 catch-and-resume，预处理器返回不能证明 SystemUI 进程不会继续崩溃。


源码：[PluginManagerImpl.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginManagerImpl.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
override fun uncaughtException(thread: Thread, throwable: Throwable) {
    if (env.isTestMode) {
        return
    }

    // Search for and disable plugins that may have been involved in this crash.
    if (checkStack(throwable)) {
        logger.e("Uncaught plugin error", throwable)
        return
    }

    // We couldn't find any plugins involved in this crash, just to be safe disable all the
    // plugins, so we can be sure that SysUI keeps running as expected.
    synchronized(this) {
        logger.e("System Crash; Disabling all plugins", throwable)
        for ((_, manager) in pluginMap) {
            manager.disableAll()
        }
    }
}

fun checkStack(throwable: Throwable?): Boolean {
    if (throwable == null) {
        return false
    }

    var disabledAny = false
    synchronized(this) {
        for (element in throwable.stackTrace) {
            for ((_, manager) in pluginMap) {
                disabledAny = disabledAny || manager.checkAndDisable(element.className)
            }
        }
    }
    return disabledAny || checkStack(throwable.cause)
}
```

包变化与手工禁用广播的实际处理如下。尤其 PACKAGE_REPLACED 自动启用条件还要求解析出非 null ComponentName；普通 package URI 不应被解释成必然满足该条件：


源码：[PluginManagerImpl.kt](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/packages/SystemUI/shared/src/com/android/systemui/shared/plugins/PluginManagerImpl.kt)。下方为该 tag 的方法/类型节选，省略所在类的其他成员与 imports，不作为独立工程。


```kotlin
override fun onReceive(context: Context, intent: Intent) {
    when (intent.action) {
        Intent.ACTION_USER_UNLOCKED -> {
            synchronized(this) {
                for ((_, manager) in pluginMap) {
                    manager.loadAll()
                }
            }
        }

        DISABLE_PLUGIN -> {
            val component =
                ComponentName.unflattenFromString("${intent.data}".substring(10))
                    ?: throw IllegalStateException("Received invalid URI: ${intent.data}")

            // Don't disable privileged plugins as they are a part of the OS.
            if (packages.isPrivileged(component)) return

            pluginEnabler.setDisabled(component, DisableReason.DISABLED_INVALID_VERSION)
            hostContext
                .getSystemService(NotificationManager::class.java)
                ?.cancel(component.className, SystemMessageProto.SystemMessage.NOTE_PLUGIN)
        }

        else -> {
            val pkg =
                intent.data?.encodedSchemeSpecificPart
                    ?: throw IllegalStateException("Received invalid URI: ${intent.data}")
            val componentName = ComponentName.unflattenFromString(pkg)

            if (Intent.ACTION_PACKAGE_REPLACED == intent.action && componentName != null) {
                val disableReason = pluginEnabler.getDisableReason(componentName)
                if (disableReason.autoEnable) {
                    logger.i({ "Re-enabling disabled plugin that was updated: $str1" }) {
                        str1 = componentName.flattenToShortString()
                    }
                    pluginEnabler.setEnabled(componentName)
                }
            }

            val isReload =
                Intent.ACTION_PACKAGE_ADDED == intent.action ||
                    Intent.ACTION_PACKAGE_CHANGED == intent.action ||
                    Intent.ACTION_PACKAGE_REPLACED == intent.action
            synchronized(this) {
                for (actionManager in pluginMap.values) {
                    if (isReload) {
                        actionManager.reloadPackage(pkg)
                    } else {
                        actionManager.onPackageRemoved(pkg)
                    }
                }
            }
        }
    }
}
```

恢复需要重新发现并取得新的 attached 生命周期。旧插件的协程、Handler、传感器与 View 如果没有在卸载阶段清理，即使新实例成功连接，仍会有旧对象回调和资源泄漏。ClassLoader 只有在不再被对象、线程等引用时才可能回收，“从列表删除”并不等于卸载所有已定义类。

## 第 8 章 懒加载监听用例与故障回归

### 8.1 四阶段监听的完整消费示例

下例基于第 6 章自定义 CustomPlugin；只说明平台宿主生命周期模式，省略 DI/imports/界面创建。所有入口由宿主在主线程串行调用，且注册时不允许多个插件。

```kotlin
class LazyCustomPluginHost(
    private val pluginManager: PluginManager,
    private val container: ViewGroup,
) : PluginListener<CustomPlugin> {
    private var lifecycle: PluginLifecycleManager<CustomPlugin>? = null
    private var attachedView: View? = null
    private var registered = false
    private var visible = false

    fun start() {
        if (registered) return
        registered = true
        pluginManager.addPluginListener(this, CustomPlugin::class.java, false)
    }

    override fun onPluginAttached(
        manager: PluginLifecycleManager<CustomPlugin>,
    ): Boolean {
        lifecycle = manager
        // 返回 false 时仅 attach；仍允许以后主动 loadPlugin。
        return visible && registered
    }

    fun setVisible(value: Boolean) {
        visible = value
        val manager = lifecycle ?: return
        if (value && registered) manager.loadPlugin() else manager.unloadPlugin()
    }

    override fun onPluginLoaded(
        plugin: CustomPlugin,
        pluginContext: Context,
        manager: PluginLifecycleManager<CustomPlugin>,
    ) {
        if (!registered || !visible || lifecycle !== manager) return
        val view = plugin.getCustomView()
        check(view.parent == null) { "Plugin view already has a parent" }
        container.addView(view)
        attachedView = view
    }

    override fun onPluginUnloaded(
        plugin: CustomPlugin,
        manager: PluginLifecycleManager<CustomPlugin>,
    ) {
        if (lifecycle !== manager) return
        attachedView?.let(container::removeView)
        attachedView = null
        // 不清 lifecycle：同一个 manager 仍可能再次 load。
    }

    override fun onPluginDetached(manager: PluginLifecycleManager<CustomPlugin>) {
        if (lifecycle !== manager) return
        attachedView?.let(container::removeView)
        attachedView = null
        lifecycle = null
        // 不再对旧 manager 重试，等待新一轮 attached。
    }

    fun stop() {
        if (!registered) return
        registered = false
        visible = false
        lifecycle?.unloadPlugin()
        pluginManager.removePluginListener(this)
        attachedView?.let(container::removeView)
        attachedView = null
        lifecycle = null
    }
}
```

示例显式区分 unload 与 detach，并在 stop 后不再请求新加载。真实工程还应把异步业务结果绑定到当前 manager/插件代际，防止旧任务在包替换后写回新 UI。该示例没有模拟所有 executor 竞争和异常，不应当成通过设备回归的现成组件。

如果 `getCustomView()` 违反接口约定返回已有 parent 的 View，示例选择明确失败而不是静默从另一个容器抢走 View；产品可以设计可控的错误展示，但必须定义责任归属。使用方撤除 View 应在 onPluginUnloaded 发生，插件资源清理则由其 onDestroy 完成，顺序不能倒置。

### 8.2 回归场景与可观察结果

| 场景 | 应检查的阶段与结果 | 不能用什么替代 |
|---|---|---|
| 首次安装且权限满足 | 查询候选、attach、create/context/version、loaded | 仅检查 APK 已安装 |
| 懒加载且页面不可见 | attached、plugin 为 null，显示后才 load | 将未加载误报为类加载失败 |
| 同一 manager 卸载再加载 | unloaded/onDestroy 后重新创建，未先 detach | 继续调用旧 plugin 对象 |
| 多候选但 allowMultiple=false | 查询数量/实例集合与拒绝原因 | 随机选第一个服务 |
| 接口注解不匹配 | InvalidVersionException 路径与错误日志 | 只检查 false 返回分支 |
| 受保护调用抛错 | failure prefs、hasError、unload/detach | 仅查询组件 enabled |
| 未归因系统崩溃 | 预处理器禁用策略及下次启动状态 | 宣称崩溃已被吞掉 |
| 包更新后恢复 | 自动启用条件、新实例/新 manager 与近期失败记录 | 保证任意重装都清除失败 |
| 宿主页面销毁 | 注销 listener、撤 UI、取消异步任务 | 等待弱引用或 GC 自行处理 |

以上是从源码推导的验证计划，本轮未执行设备注入异常、安装替换或 SystemUI 重启测试。测试应在受控工程/设备上进行，避免把系统级插件实验推广为普通应用可通用采用的生产扩展方案。
