# 源码地图：按问题找项目

这里的目录是**优先检索范围和候选路径**，不是所有版本都不变的 API 契约。先固定 revision，再用目录树、符号和构建规则确认。表内路径均相对所列 Git 项目的根；写文章时可再加 superproject 路径。

## 1. AOSP 平台入口

Gitiles 项目入口格式：`https://android.googlesource.com/<project>/`。

| 主题/搜索词 | Git 项目 | 优先目录或文件 |
|---|---|---|
| Window / View / ViewGroup / Choreographer / Insets | `platform/frameworks/base` | `core/java/android/view/` |
| PhoneWindow / DecorView | `platform/frameworks/base` | `core/java/com/android/internal/policy/` |
| ActivityThread / Instrumentation / LoadedApk / ContextImpl | `platform/frameworks/base` | `core/java/android/app/` |
| Handler / Looper / Message / MessageQueue | `platform/frameworks/base` | `core/java/android/os/`；队列实现还需读 `core/java/Android.bp` |
| ATMS / ActivityStarter / Task / TaskFragment / WMS | `platform/frameworks/base` | `services/core/java/com/android/server/wm/` |
| AMS / ProcessList / ActiveServices / 广播 / ANR | `platform/frameworks/base` | `services/core/java/com/android/server/am/` |
| PMS / PackageInstallerSession / InstallPackageHelper | `platform/frameworks/base` | `services/core/java/com/android/server/pm/`；解析代码按符号继续追 |
| ZygoteInit / ZygoteServer | `platform/frameworks/base` | `core/java/com/android/internal/os/` |
| SystemServer | `platform/frameworks/base` | `services/java/com/android/server/SystemServer.java` |
| Java Binder / Parcel / JNI 注册 | `platform/frameworks/base` | `core/java/android/os/`；`core/jni/android_util_Binder.cpp`；Parcel JNI 可由注册符号搜索 |
| ProcessState / IPCThreadState / libbinder / ServiceManager | `platform/frameworks/native` | `libs/binder/`；`cmds/servicemanager/` |
| Surface / BLASTBufferQueue / BufferQueue | `platform/frameworks/native` | `libs/gui/`；Java/JNI 入口另在 frameworks/base |
| SurfaceFlinger / 合成 | `platform/frameworks/native` | `services/surfaceflinger/` |
| RenderNode / RecordingCanvas / RenderThread / DrawFrameTask | `platform/frameworks/base` | `graphics/java/android/graphics/`；`libs/hwui/` |
| Skia 录制后实际绘制库 | `platform/external/skia` | 按调用符号查 `src/`；先从 HWUI 调用侧进入 |
| InputManagerService / InputDispatcher / EventHub | `platform/frameworks/base` 与 `platform/frameworks/native` | base 的 `services/core/java/com/android/server/input/`；native 的 `services/inputflinger/` |
| InputMethodManager / IMMS / Insets 控制 | `platform/frameworks/base` | `core/java/android/view/inputmethod/`；`services/core/java/com/android/server/inputmethod/`；`android/view/` |
| SystemUI / AOD / Doze / 通知 / Keyguard | `platform/frameworks/base` | `packages/SystemUI/`；Android 17 入口见下一节 |
| 服务端通知 / 排名 / 通知历史 | `platform/frameworks/base` | `services/core/java/com/android/server/notification/`；RemoteViews 在 `core/java/android/widget/RemoteViews.java` |
| JobScheduler / JobService / JobInfo | `platform/frameworks/base` | Android 17 优先检查 `apex/jobscheduler/`；不要一律套旧 `core/java/android/app/job/` |
| ART / GC / JIT / 对象头 / Monitor | `platform/art` | `runtime/`、`runtime/gc/`、`runtime/jit/`、`runtime/mirror/` |
| ClassLoader / DexPathList / Java 并发库 | `platform/libcore` | `dalvik/src/main/java/dalvik/system/`；`ojluni/src/main/java/` |
| TLS / TrustManager / Network Security Config | `platform/external/conscrypt` | `common/` 与 `nsc/`；RootTrustManager 实际包见下一节 |
| Connectivity / NSD / 网络栈 | `platform/packages/modules/Connectivity`；`platform/packages/modules/NetworkStack` | 先定位 API 和实际 Binder 实现；模块划分随版本核实 |
| 权限声明 / 兼容拆分 / 权限授予策略 | `platform/frameworks/base`；`platform/packages/modules/Permission` | base 的 `core/res/AndroidManifest.xml`、`data/etc/platform.xml`；再沿 Permission 实现追踪 |
| Keystore Java / Keystore2 native | `platform/frameworks/base`；`platform/system/security` | base 的 `keystore/java/android/security/keystore2/`；security 的 `keystore2/` |
| init / 启动阶段 | `platform/system/core` | `init/`；产品 rc 文件还要查 device/vendor 配置 |
| ADB / adbd | `platform/packages/modules/adb` | 项目根按 client/daemon/transport 符号搜索；主机 adb 版本与设备版本分开 |
| Perfetto / trace processor | `platform/external/perfetto`；Perfetto 官方文档 | 采集数据源和 SQL 表按实际 trace processor 版本核对 |
| Binder 驱动 / 调度器 | `kernel/common` 或设备实际内核仓库 | `drivers/android/binder.c`、`binder_alloc.c`；`kernel/sched/`。固定独立内核 SHA，不套平台 tag |

## 2. Android 17 中容易找错的位置

以下是 `android-17.0.0_r1` 文档维护时的具体定位线索，不自动外推到其他版本。

### 队列：不是搜到一个 MessageQueue.java 就结束

```text
project: platform/frameworks/base
core/java/Android.bp
core/java/android/os/CombinedMessageQueue/MessageQueue.java
core/java/android/os/CombinedDeliMessageQueue/MessageQueue.java
```

先核对 `messagequeue-gen`、候选源排除和输出，再核对实现内的并发/Deli 开关。生成后的同名文件、源候选和运行分支要区分。

### SystemUI：检查 Kotlin 入口和 Java 委托

```text
project: platform/frameworks/base
packages/SystemUI/src/com/android/systemui/application/SystemUIApplication.kt
packages/SystemUI/src/com/android/systemui/application/impl/SystemUIApplicationImpl.java
packages/SystemUI/shared/src/com/android/systemui/shared/plugins/
packages/SystemUI/plugin_core/src/com/android/systemui/plugins/
```

插件先搜 `PluginManagerImpl`、`PluginActionManager`、`PluginInstance`，再追创建、权限、版本校验和加载/卸载。不要照旧文章虚构根包下 Java Application 的实现。

### Conscrypt：包名和目录猜错会得到 404

```text
project: platform/external/conscrypt
nsc/src/android/security/net/config/RootTrustManager.java
```

它不是 `nsc/src/com/android/org/conscrypt/RootTrustManager.java`。路径失败应读目录树，不能直接删除真实实现分析或宣称“内部 API 没有固定路径”。

### WindowSurfaceController：字符串不是类定义

看到 `setCallsite("WindowSurfaceController")` 只能证明一个调试字符串。继续查 `WindowStateAnimator`、`WindowState.setClientSurface`、`ViewRootImpl` 和目录树，区分服务端建 surface 与客户端 surface 分支；不要据字符串拼出不存在的 `.java` 链接。

### 行号与方法名都可能漂移

旧文章的 `TraversalRunnable`、无参遍历、旧任务类与 ServiceManager 实现不能直接当作当前代码。先核对声明和调用：例如 `ViewRootImpl` 的 `TraversalCallback` / `postVsyncCallback`，再依据实际参数与条件解释。

## 3. AndroidX 和其他库去哪里找

| 范围 | 官方入口 | 如何固定版本 |
|---|---|---|
| AndroidX / Lifecycle / Room / Paging / Compose | `https://cs.android.com/androidx/platform/frameworks/support`；`https://android.googlesource.com/platform/frameworks/support/` | 工程解析后的 Maven 坐标、官方 release 对应 revision，或官方 `-sources.jar`；开发分支不能冒充已发布版本 |
| Google Maven | `https://dl.google.com/dl/android/maven2/` | `<group路径>/<artifact>/<version>/<artifact>-<version>-sources.jar`，先确认该构件确实发布源码包 |
| Maven Central | `https://repo.maven.apache.org/maven2/` | 同样按 GAV 定位；多平台/变体构件可能不是简单同名 sources.jar |
| AGP | `https://android.googlesource.com/platform/tools/base/`；官方 AGP release notes | 工程 AGP 版本与源码/发布说明对应；Gradle、JDK 单独记录 |
| Gradle | `https://github.com/gradle/gradle`；`https://docs.gradle.org/` | `gradle-wrapper.properties` 中版本与对应 release/tag |
| Kotlin / 协程 | `https://github.com/JetBrains/kotlin`；`https://github.com/Kotlin/kotlinx.coroutines` | Kotlin 编译器和协程依赖版本分开 |
| OkHttp / Retrofit / Moshi | `https://github.com/square/okhttp`、`square/retrofit`、`square/moshi` | 解析依赖版本对应的仓库 tag 或发布源码包 |
| Glide / Gson / Dagger / Koin | `https://github.com/bumptech/glide`、`google/gson`、`google/dagger`、`InsertKoinIO/koin` | 不以 README 的 main 示例证明旧版 API |
| MMKV / PAG / Fresco / Lottie | `https://github.com/Tencent/MMKV`、`Tencent/libpag`、`facebook/fresco`、`airbnb/lottie-android` | 核对 Android SDK、native/JNI 和相关依赖的各自版本 |
| Flutter | `https://github.com/flutter/flutter`；`https://docs.flutter.dev/` | framework revision 与对应 engine revision 分别核对；源码布局以目标版本为准 |
| React Native | `https://github.com/facebook/react-native`；`https://reactnative.dev/` | RN 版本、架构开关、模板/CLI 版本分别核对 |
| lib_hissug / NAComp / TCL 与其他厂商代码 | 用户工作区、获授权的私有 Git/Gerrit 与内部文档 | 当前厂商分支/SHA和本地补丁；公共搜索站不能证明私有类的实现 |

找不到库的 release tag 时，先读版本目录和发布资产/POM/SCM 信息，不盲猜所有库都采用 `v<version>`。Android Gradle 工程有能力运行时，可用 `dependencyInsight` 核对实际解析结果；不为简单源码定位启动完整构建。

## 4. 返回给用户的定位示例

```text
项目：platform/frameworks/base
版本：refs/tags/android-17.0.0_r1
文件：core/java/android/view/Window.java
符号：Window.Callback / superDispatchTouchEvent
已核实：Window 声明的回调和分发契约。
继续追踪：PhoneWindow 实现、DecorView、Activity 对 Window.Callback 的实现。
限制：仅 Window.java 不能证明完整触摸分发、ViewGroup 目标链及所有设备行为。
证据：固定版本链接 + 实际方法行号；下载时附 URL/ref/path/SHA-256。
```

应根据实际读取结果填写，不把此示例照抄成已完成的分析。
