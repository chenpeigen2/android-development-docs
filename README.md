# Android 开发文档集

> 持续更新中... | 最后更新：2026-04-15

## 文档统计

- **总文档数**：43 篇
- **总大小**：约 4.4 MB
- **总行数**：约 93,000+ 行

---

## 文档目录

### 基础知识（9篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 1 | [Android_View_绘制流程.md](./Android_View_绘制流程.md) | 347KB | View 绘制 8 层架构完整解析 |
| 2 | [Android_自定义View_绘制完全指南.md](./Android_自定义View_绘制完全指南.md) | 166KB | Drawable/Canvas/Paint 详解 + 实战案例 |
| 3 | [Android事件分发机制详解.md](./Android事件分发机制详解.md) | 204KB | ViewGroup/View 事件分发源码解析 |
| 4 | [Android事件分发机制完全指南.md](./Android事件分发机制完全指南.md) | 56KB | 事件分发基础与典型场景 |
| 5 | [Android_Activity_启动流程.md](./Android_Activity_启动流程.md) | 102KB | ActivityThread 核心流程 |
| 6 | [Android_动画完全指南.md](./Android_动画完全指南.md) | 46KB | 帧动画/补间动画/属性动画 |
| 7 | [Android_四大组件详解.md](./Android_四大组件详解.md) | 108KB | Activity/Service/Receiver/Provider |
| 8 | [Android_屏幕适配详解.md](./Android_屏幕适配详解.md) | 69KB | 多分辨率适配方案 |
| 9 | [Android_网络编程详解.md](./Android_网络编程详解.md) | 12KB | HTTP/HTTPS/TCP/UDP 协议详解 |

### 核心机制（10篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 10 | [Android_Binder机制深度解析.md](./Android_Binder机制深度解析.md) | 269KB | 14 步完整调用链 + AIDL 示例 |
| 11 | [Android_Handler机制详解.md](./Android_Handler机制详解.md) | 90KB | Handler/Looper/MessageQueue 源码 |
| 12 | [Android_虚拟机详解.md](./Android_虚拟机详解.md) | 63KB | JVM/Dalvik/ART 对比 + GC 算法 |
| 13 | [Android_ClassLoader详解.md](./Android_ClassLoader详解.md) | 43KB | 双亲委派 + 热修复原理 |
| 14 | [Android_Zygote与SystemServer详解.md](./Android_Zygote与SystemServer详解.md) | 72KB | 进程启动 + 系统服务启动 |
| 15 | [AndroidX_核心库详解.md](./AndroidX_核心库详解.md) | 145KB | Lifecycle/ViewModel/LiveData/Room/ViewPager2/Fragment |
| 16 | [Android_架构模式演进详解.md](./Android_架构模式演进详解.md) | 74KB | MVC/MVP/MVVM/MVI 演进 |
| 17 | [Android_后台任务详解.md](./Android_后台任务详解.md) | 94KB | Service/JobScheduler/WorkManager |
| 18 | [Android_多线程与并发详解.md](./Android_多线程与并发详解.md) | 120KB | Java线程/同步/CAS/并发集合/线程池/Kotlin协程/Flow（12章）|
| 19 | [Android_SystemUI_详解.md](./Android_SystemUI_详解.md) | 323KB | StatusBar/NavBar/AOD/通知/Keyguard/RemoteViews 源码 (Android 16 AOSP) |

### Framework 核心（6篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 20 | [Android_AMS_深度解析.md](./framework/Android_AMS_深度解析.md) | 116KB | AMS/ATMS/ActivityStack/oom_adj/LaunchMode（10章 47+面试题）|
| 21 | [Android_WMS_窗口管理.md](./framework/Android_WMS_窗口管理.md) | 42KB | WindowToken/WindowState/Surface/Choreographer/VSync（10章）|
| 22 | [Android_PMS_包管理.md](./framework/Android_PMS_包管理.md) | 23KB | APK安装/组件解析/权限管理/签名验证（9章）|
| 23 | [Android_InputManager_输入系统.md](./framework/Android_InputManager_输入系统.md) | 47KB | EventHub/InputChannel/触摸按键事件分发（10章）|
| 24 | [Android_进程与线程调度.md](./framework/Android_进程与线程调度.md) | 38KB | CFS/优先级/Binder线程池/Looper/线程池（9章）|
| 25 | [Android_系统启动流程.md](./framework/Android_系统启动流程.md) | 37KB | Init/Zygote/SystemServer/BootComplete（8章）|

### 性能优化（4篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 26 | [Android_性能优化详解.md](./Android_性能优化详解.md) | 252KB | 启动/UI渲染/内存/网络/RecyclerView/自定义View 优化 + 资深工程师深度解析 |
| 27 | [Android_内存泄漏与内存优化详解.md](./Android_内存泄漏与内存优化详解.md) | 71KB | GC机制演进/内存泄漏原理/检测 + 优化技巧 |
| 28 | [Android_ANR详解.md](./Android_ANR详解.md) | 83KB | ANR 原理/监控/优化 + 资深工程师深度解析 |
| 29 | [Android_Systrace_性能分析详解.md](./Android_Systrace_性能分析详解.md) | 132KB | Systrace 工具使用 + 分析方法 |

### 架构进阶（3篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 30 | [Android_SystemUI_Plugin详解.md](./Android_SystemUI_Plugin详解.md) | 34KB | SystemUI 插件化（6章）|
| 31 | [Android_Plugin详解.md](./Android_Plugin详解.md) | 120KB | 应用插件化框架详解（11章）|
| 32 | [Android_组件化详解.md](./Android_组件化详解.md) | 43KB | 模块解耦/路由/通信（18章）|

### 三方库详解（2篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 33 | [Android_三方库详解.md](./Android_三方库详解.md) | 201KB | Glide/Fresco/MMKV/PAG/Lottie |
| 34 | [Android_网络请求库详解.md](./Android_网络请求库详解.md) | 84KB | OkHttp/Retrofit 完全指南 |

### 跨平台开发（3篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 35 | [Flutter_完全指南.md](./Flutter_完全指南.md) | 29KB | Google 跨平台 UI 框架 |
| 36 | [React_Native完全指南.md](./React_Native完全指南.md) | 29KB | Facebook 跨平台框架 |
| 37 | [Android_Jetpack_Compose详解.md](./Android_Jetpack_Compose详解.md) | 61KB | Android 声明式 UI（18章）|

### 工具与构建（2篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 38 | [Android_Gradle与AGP详解.md](./Android_Gradle与AGP详解.md) | 21KB | Gradle 构建流程 + AGP 详解 |
| 43 | [Android_ADB与调试工具详解.md](./Android_ADB与调试工具详解.md) | 96KB | ADB命令/pm/am/logcat/dumpsys/性能调试/Systrace/Perfetto/Studio工具/APK分析 |

### 数据处理（1篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 39 | [Android_JSON解析详解.md](./Android_JSON解析详解.md) | 53KB | org.json/Gson/Moshi/Jackson 对比 + 最佳实践 |

### 依赖注入（1篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 40 | [Android_依赖注入详解.md](./Android_依赖注入详解.md) | 117KB | Hilt/Koin/Dagger2 完全指南 + 最佳实践 |

### 安全与防护（1篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 41 | [Android_安全详解.md](./Android_安全详解.md) | 120KB | 混淆/加固/加密/网络安全（18章）|

### 显示系统（1篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 42 | [Android_Window与Surface详解.md](./Android_Window与Surface详解.md) | 61KB | Window/Surface/ViewRootImpl 关系详解（10章）|

---

## 分类统计

| 类别 | 文档数 | 总大小 | 说明 |
|------|--------|--------|------|
| 基础知识 | 9 篇 | 1.1 MB | View/事件/动画/四大组件 |
| 核心机制 | 10 篇 | 1.3 MB | Binder/Handler/虚拟机/SystemUI/AndroidX/多线程并发 |
| Framework 核心 | 6 篇 | 312 KB | AMS/WMS/PMS/IMS/进程线程/启动流程 |
| 性能优化 | 4 篇 | 540 KB | 性能/内存/ANR/Systrace |
| 架构进阶 | 3 篇 | 204 KB | 插件化/组件化 |
| 三方库详解 | 2 篇 | 288 KB | 图片/网络/存储/动画库 |
| 跨平台开发 | 3 篇 | 128 KB | Flutter/RN/Compose |
| 工具与构建 | 2 篇 | 117 KB | Gradle/AGP/ADB/调试工具 |
| 数据处理 | 1 篇 | 53 KB | JSON 解析 |
| 依赖注入 | 1 篇 | 117 KB | Hilt/Koin/Dagger2 |
| 安全与防护 | 1 篇 | 120 KB | 混淆/加固/加密 |
| 显示系统 | 1 篇 | 61 KB | Window/Surface/ViewRootImpl |
| **总计** | **43 篇** | **4.4 MB** | **93,000+ 行** |

---

## 更新日志

### 2026-04-15 ADB 与调试工具详解新增

**新增文档（1篇）**：

1. **Android_ADB与调试工具详解.md** (96KB, 19章, 2493行)
   - ADB 架构（Client/Server/Daemon 三层模型）
   - ADB 基础（环境配置/USB+WiFi 连接/Server 管理）
   - 设备与系统命令（设备信息/系统属性/重启模式）
   - 应用管理 pm（安装卸载/权限/包信息/数据管理）
   - Activity 管理 am（启动 Activity/Service/广播/强制停止）
   - 文件操作（push/pull/应用数据操作）
   - 日志系统 logcat（过滤/格式化/缓冲区/高级用法）
   - Input 模拟（触摸/滑动/按键/文本输入/手势录制）
   - 网络与端口转发（forward/reverse/抓包）
   - 屏幕操作（截图/录屏/scrcpy 投屏）
   - dumpsys 深度解析（Activity/内存/电池/网络/GPU）
   - 进程与性能调试（top/ps/simpleperf/内存分析）
   - SQLite 与 Content Provider（数据库操作/content 命令/settings）
   - Systrace 与 Perfetto（系统级追踪/对比选择）
   - Android Studio 调试工具（Layout Inspector/Database Inspector/Profiler/App Inspection）
   - APK 分析工具（aapt/apkanalyzer/dexdump/jadx）
   - 高级调试技巧（WebView/Choreographer/开发者选项/Shell 脚本）
   - 面试常见问题（20 道高频题）
   - 命令速查表（5 类快速参考）

---

### 2026-04-08 SystemUI RemoteViews 机制扩展

**文档增强（1篇）**：

1. **Android_SystemUI_详解.md** (281KB -> 323KB)
   - 新增 6.4 Actions 机制深度解析（Action 类继承体系/ReflectionAction 反射调用/序列化反序列化流程/Action 列表设计哲学）
   - 新增 6.5 反射创建与 View 白名单机制（LayoutInflater Filter/白名单实现/@RemoteView 注解/反射创建流程/安全三层防线/apply vs reapply）
   - 新增面试题：为什么通知列表用 FrameLayout 而不是 RecyclerView

---

### 2026-04-06 性能优化与 ANR 文档重写

**文档重写（2篇）**：

1. **Android_性能优化详解.md** (156KB -> 252KB)
   - 新增资深工程师深度解析章节
   - 扩展启动优化（冷启动/热启动/懒加载/异步初始化）
   - 新增 UI 渲染优化（RecyclerView/自定义 View 性能优化）
   - 新增内存优化（大图加载/内存池/Native 内存/LeakCanary 原理）
   - 新增网络优化（OkHttp 拦截器/缓存策略/连接池）

2. **Android_ANR详解.md** (39KB -> 83KB)
   - 新增资深工程师深度解析章节
   - 扩展 ANR 触发机制（Service/Broadcast/ContentProvider/Input 四类 ANR）
   - 新增 WatchDog/Matrix/ANR-WatchDog 监控方案对比

3. **Android_内存泄漏与内存优化详解.md** (51KB -> 71KB)
   - 新增 GC 机制演进章节（Dalvik/ART GC 算法对比）
   - 新增内存泄漏原理分析

---

### 2026-04-01 GC 算法与内存管理补全

1. **Android_内存泄漏与内存优化详解.md** - GC 算法和 Android 内存管理文档补全

---

### 2026-03-24 多线程与并发详解新增

**新增文档（1篇）**：

1. **Android_多线程与并发详解.md** (120KB, 12章)
   - Java 线程基础/线程同步/CAS/并发集合/线程池
   - Kotlin 协程原理（suspend状态机/Dispatchers/Flow）
   - 并发设计模式/性能与反模式/面试高频问题

---

### 2026-03-15 Window 与 Surface 详解新增

1. **Android_Window与Surface详解.md** (36KB -> 61KB, 10章)
   - Window 与 Surface 核心概念
   - WindowManager.addView 详解
   - SurfaceView 与 TextureView 对比
   - ViewRootImpl/WMS 创建 Surface 源码分析

---

### 2026-03-13 JSON解析 + 依赖注入 + AndroidX 增强

**新增文档（2篇）**：

1. **Android_JSON解析详解.md** (53KB, 9章) - org.json/Gson/Moshi/Jackson 对比
2. **Android_依赖注入详解.md** (117KB, 9章) - Hilt/Koin/Dagger2 完全指南

**文档增强（1篇）**：

1. **AndroidX_核心库详解.md** (89KB -> 145KB) - 新增 ViewPager2 + Fragment 完整讲解

---

### 2026-03-12 Framework 核心文档新增 (6篇)

1. **Android_AMS_深度解析.md** (116KB, 10章, 47+面试题)
2. **Android_WMS_窗口管理.md** (42KB, 10章)
3. **Android_PMS_包管理.md** (23KB, 9章)
4. **Android_InputManager_输入系统.md** (47KB, 10章)
5. **Android_进程与线程调度.md** (38KB, 9章)
6. **Android_系统启动流程.md** (37KB, 8章)

---

### 2026-03-11 安全详解 + Jetpack Compose + 跨平台新增

1. **Android_安全详解.md** (120KB, 18章) - 混淆/加固/加密/网络安全
2. **Android_Jetpack_Compose详解.md** (61KB, 18章) - 全面重写
3. **Flutter_完全指南.md** (29KB, 18章)
4. **React_Native完全指南.md** (29KB, 18章)

---

## 联系方式

- **作者**：陈培根 (OpenClaw)
- **邮箱**：o1831938181o@gmail.com
- **GitLab**：https://gitlab.com/chenpeigen/android-development-docs
- **更新频率**：持续更新中

---

*Generated by OpenClaw | 2026-04-15*
