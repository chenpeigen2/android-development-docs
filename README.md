# Android 开发文档集

> 持续更新中... | 最后更新：2026-03-15

## 📚 文档统计

- **总文档数**：40 篇
- **总大小**：约 3.65 MB
- **总行数**：约 58,000+ 行

---

## 📖 文档目录

### 基础知识（9篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 1 | [Android_View_绘制流程.md](./Android_View_绘制流程.md) | 347KB | View 绘制 8 层架构完整解析 |
| 2 | [Android_自定义View_绘制完全指南.md](./Android_自定义View_绘制完全指南.md) | 166KB | Drawable/Canvas/Paint 详解 + 实战案例 |
| 3 | [Android事件分发机制详解.md](./Android事件分发机制详解.md) | 204KB | ViewGroup/View 事件分发源码解析 |
| 4 | [Android事件分发机制完全指南.md](./Android事件分发机制完全指南.md) | 56KB | 事件分发基础与典型场景 |
| 5 | [Android_Activity_启动流程.md](./Android_Activity_启动流程.md) | 102KB | ActivityThread 核心流程 |
| 6 | [Android_动画完全指南.md](./Android_动画完全指南.md) | 46KB | 帧动画/补间动画/属性动画 |
| 7 | [Android_四大组件详解.md](./Android_四大组件详解.md) | 76KB | Activity/Service/Receiver/Provider |
| 8 | [Android_屏幕适配详解.md](./Android_屏幕适配详解.md) | 69KB | 多分辨率适配方案 |
| 9 | [Android_网络编程详解.md](./Android_网络编程详解.md) | 12KB | HTTP/HTTPS/TCP/UDP 协议详解 |

### 核心机制（15篇）⭐ Framework 核心文档

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 10 | [Android_Binder机制深度解析.md](./Android_Binder机制深度解析.md) | 185KB | ⭐ 14 步完整调用链 + AIDL 示例 |
| 11 | [Android_Handler机制详解.md](./Android_Handler机制详解.md) | 90KB | Handler/Looper/MessageQueue 源码 |
| 12 | [Android_虚拟机详解.md](./Android_虚拟机详解.md) | 63KB | JVM/Dalvik/ART 对比 + GC 算法 |
| 13 | [Android_ClassLoader详解.md](./Android_ClassLoader详解.md) | 43KB | 双亲委派 + 热修复原理 |
| 14 | [Android_Zygote与SystemServer详解.md](./Android_Zygote与SystemServer详解.md) | 72KB | 进程启动 + 系统服务启动 |
| 15 | [AndroidX_核心库详解.md](./AndroidX_核心库详解.md) | 132KB | Lifecycle/ViewModel/LiveData/Room/ViewPager2/Fragment ⭐ 2026-03-13 更新 |
| 16 | [Android_架构模式演进详解.md](./Android_架构模式演进详解.md) | 74KB | MVC/MVP/MVVM/MVI 演进 |
| 17 | [Android_后台任务详解.md](./Android_后台任务详解.md) | 94KB | Service/JobScheduler/WorkManager |
| 18 | [Android_SystemUI_详解.md](./Android_SystemUI_详解.md) | 281KB | ⭐ StatusBar/NavBar/AOD/通知/Keyguard 源码 (Android 16 AOSP) |

### Framework 核心（6篇）⭐ 2026-03-12 新增

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 19 | [Android_AMS_深度解析.md](./framework/Android_AMS_深度解析.md) | 116KB | ⭐ AMS/ATMS/ActivityStack/oom_adj/LaunchMode（10章 47+面试题）|
| 20 | [Android_WMS_窗口管理.md](./framework/Android_WMS_窗口管理.md) | 42KB | ⭐ WindowToken/WindowState/Surface/Choreographer/VSync（10章）|
| 21 | [Android_PMS_包管理.md](./framework/Android_PMS_包管理.md) | 11KB | ⭐ APK安装/组件解析/权限管理/签名验证（9章）|
| 22 | [Android_InputManager_输入系统.md](./framework/Android_InputManager_输入系统.md) | 9KB | ⭐ EventHub/InputChannel/触摸按键事件分发（10章）|
| 23 | [Android_进程与线程调度.md](./framework/Android_进程与线程调度.md) | 26KB | ⭐ CFS/优先级/Binder线程池/Looper/线程池（9章）|
| 24 | [Android_系统启动流程.md](./framework/Android_系统启动流程.md) | 26KB | ⭐ Init/Zygote/SystemServer/BootComplete（8章）|

### 性能优化（4篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 25 | [Android_性能优化详解.md](./Android_性能优化详解.md) | 156KB | 启动/UI/内存/电量/网络/APK 优化 |
| 26 | [Android_内存泄漏与内存优化详解.md](./Android_内存泄漏与内存优化详解.md) | 51KB | 内存泄漏检测 + 优化技巧 |
| 27 | [Android_ANR详解.md](./Android_ANR详解.md) | 39KB | ANR 原理 + 监控 + 优化 |
| 28 | [Android_Systrace_性能分析详解.md](./Android_Systrace_性能分析详解.md) | 132KB | Systrace 工具使用 + 分析方法 |

### 架构进阶（3篇）⭐ NEW!

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 29 | [Android_SystemUI_Plugin详解.md](./Android_SystemUI_Plugin详解.md) | 35KB | ⭐ SystemUI 插件化（6章 894行）|
| 30 | [Android_Plugin详解.md](./Android_Plugin详解.md) | 32KB | ⭐ 普通应用插件化（11章 636行）|
| 31 | [Android_组件化详解.md](./Android_组件化详解.md) | 46KB | ⭐ 模块解耦/路由/通信（18章 1028行）|

### 三方库详解（2篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 31 | [Android_三方库详解.md](./Android_三方库详解.md) | 201KB | Glide/Fresco/MMKV/PAG/Lottie |
| 32 | [Android_网络请求库详解.md](./Android_网络请求库详解.md) | 84KB | OkHttp/Retrofit 完全指南 |

### 跨平台开发（3篇）⭐ NEW!

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 33 | [Flutter_完全指南.md](./Flutter_完全指南.md) | 29KB | ⭐ Google 跨平台 UI 框架 |
| 34 | [React_Native完全指南.md](./React_Native完全指南.md) | 29KB | ⭐ Facebook 跨平台框架 |
| 35 | [Android_Jetpack_Compose详解.md](./Android_Jetpack_Compose详解.md) | 62KB | ⭐ Android 声明式 UI（18章 2600+行）|

### 工具与构建（1篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 36 | [Android_Gradle与AGP详解.md](./Android_Gradle与AGP详解.md) | 35KB | Gradle 构建流程 + AGP 详解 |

### 数据处理（1篇）⭐ 2026-03-13 新增

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 37 | [Android_JSON解析详解.md](./Android_JSON解析详解.md) | 43KB | ⭐ org.json/Gson/Moshi/Jackson 对比 + 最佳实践 |

### 依赖注入（1篇）⭐ 2026-03-13 新增

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 38 | [Android_依赖注入详解.md](./Android_依赖注入详解.md) | 52KB | ⭐ Hilt/Koin/Dagger2 完全指南 + 最佳实践 |

### 安全与防护（1篇）⭐ NEW!

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 39 | [Android_安全详解.md](./Android_安全详解.md) | 120KB | ⭐ 混淆/加固/加密/网络安全（18章 3730行）|

### 显示系统（1篇）⭐ 2026-03-15 新增

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 40 | [Android_Window与Surface详解.md](./Android_Window与Surface详解.md) | 36KB | ⭐ Window/Surface/ViewRootImpl 关系详解（10章）|

## 🌟 重点推荐

### 1. Android 安全详解 ⭐ 2026-03-11 新增

> **120KB | 18章 | 3730行 | 安全防护完全指南**

**第一篇：Android 安全基础**
- 安全模型/威胁分析/防护层次
- 应用签名机制（v1/v2/v3/v4）
- 混淆详解（ProGuard/R8 配置）
- 加固技术（DEX/SO/反调试）
- 反编译与防护

**第二篇：数据安全**
- 数据加密（AES/RSA/SHA/Keystore）
- 数据存储安全（SP/文件/数据库/MMKV）
- 网络安全（HTTPS/SSL Pinning/抓包防护）

**第三篇：进阶防护**
- 四大组件安全
- WebView 安全
- Intent 安全（注入攻击/PendingIntent/Deep Link）
- SO 安全（NDK/反调试/完整性校验）
- 运行时防护（Root/Hook/模拟器检测）
- 主流加固方案对比（360/腾讯/阿里/梆梆）
- 安全最佳实践
- 面试常见问题（10+题）

---

### 2. React Native 完全指南 ⭐ NEW!

> **29KB | 18章 | 1160+ 行 | Facebook 跨平台框架**

**第一篇：React Native 基础（6章）**
- React Native 概述与核心架构
- JavaScript/TypeScript 基础（ES6+/异步编程）
- React 基础（组件/Props/State/Hooks）
- 核心组件（View/Text/Image/FlatList）
- 样式与布局（Flexbox/StyleSheet）
- 导航（React Navigation）

**第二篇：React Native 进阶（6章）**
- 状态管理（Context/Redux/MobX/Zustand）
- 网络请求（Fetch/Axios/拦截器）
- 数据持久化（AsyncStorage/SQLite/Realm）
- 动画（Animated/Reanimated/Lottie）
- 手势处理（Gesture Handler）
- 原生模块（Native Modules）

**第三篇：React Native 高级（6章）**
- 性能优化（列表/图片/内存/Bundle）
- 调试与测试（单元/组件/E2E）
- 新架构（Fabric/TurboModules/CodeGen）
- Expo 开发（SDK/Router）
- 发布与部署（CodePush/CI/CD）
- 面试常见问题

**核心对比**：
- React Native vs Flutter（详细对比）
- Bridge 机制原理
- 新架构优势
- 适用场景分析

---

### 2. Flutter 完全指南

> **29KB | 18章 | 1000+ 行 | Google 跨平台 UI 框架**

- Dart 语言基础
- Widget 体系
- 状态管理（Provider/Riverpod/Bloc）
- Platform Channels
- 性能优化
- 面试常见问题

---

### 3. Jetpack Compose 完全指南 ⭐ 2026-03-11 更新

> **62KB | 18章 | 2600+ 行 | Android 声明式 UI**

- Compose 概述 vs 传统 View
- Composable 函数/State/Modifier
- Layout 布局（Column/Row/Box/ConstraintLayout）
- Material Design 3 组件
- LazyColumn/LazyRow/LazyVerticalGrid 列表
- 动画（AnimatedVisibility/Crossfade/animate*AsState）
- 主题与样式
- ViewModel/Hilt 集成
- 协程集成（LaunchedEffect）
- Navigation 导航
- 与传统 View 互操作
- 手势处理（点击/拖动/缩放）
- Canvas 自定义绘制
- 性能优化/稳定性
- 面试常见问题（15+题）

---

### 4. Android 三方库详解

> **201KB | 42章 | 5000+ 行 | 面试高频**

- Glide/Fresco（图片加载）
- MMKV（数据存储）
- PAG/Lottie（动画框架）

---

### 5. Android 网络请求库详解

> **84KB | 20章 | 2700+ 行**

- OkHttp（拦截器/缓存/WebSocket）
- Retrofit（动态代理/注解/协程）

---

## 📊 跨平台框架对比

| 对比项 | Flutter | React Native | Jetpack Compose |
|------|---------|--------------|-----------------|
| **公司** | Google | Meta | Google |
| **语言** | Dart | JS/TS | Kotlin |
| **渲染** | Skia 自绘 | 原生组件 | 原生组件 |
| **性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **热重载** | ✅ | ✅ | ✅ |
| **跨平台** | iOS/Android/Web/Desktop | iOS/Android | Android |
| **学习曲线** | 中等 | 需 React | 需 Kotlin |
| **生态** | 快速发展 | npm 丰富 | Android 专属 |

**选型建议**：
- **Flutter**：全新项目，追求性能和一致性
- **React Native**：有 React 经验，快速迭代
- **Jetpack Compose**：Android 原生开发

---

## 📈 分类统计

| 类别 | 文档数 | 总大小 | 说明 |
|------|--------|--------|------|
| 基础知识 | 9 篇 | 1.08 MB | View/事件/动画/四大组件 |
| 核心机制 | 9 篇 | 1.10 MB | Binder/Handler/虚拟机/SystemUI/AndroidX ⭐ |
| **Framework 核心** | **6 篇** | **0.23 MB** | **AMS/WMS/PMS/IMS/进程线程/启动流程 ⭐** |
| 性能优化 | 4 篇 | 0.38 MB | 性能/内存/ANR/Systrace |
| 架构进阶 | 3 篇 | 0.11 MB | 插件化/组件化 ⭐ |
| 三方库详解 | 2 篇 | 0.28 MB | 图片/网络/存储/动画库 |
| 跨平台开发 | 3 篇 | 0.12 MB | Flutter/RN/Compose ⭐ |
| 数据处理 | 1 篇 | 0.04 MB | JSON解析 ⭐ |
| 依赖注入 | 1 篇 | 0.05 MB | Hilt/Koin/Dagger2 ⭐ |
| 安全与防护 | 1 篇 | 0.12 MB | 混淆/加固/加密 ⭐ |
| 显示系统 | 1 篇 | 0.04 MB | Window/Surface/ViewRootImpl ⭐ |
| **总计** | **40 篇** | **3.65 MB** | **58,000+ 行** |

---

## 🚀 更新日志

### 2026-03-15 ⭐ Window 与 Surface 详解新增

**新增文档（1篇）**：

1. ✅ **Android_Window与Surface详解.md** (36KB, 10章)
   - Window 与 Surface 核心概念
   - Window 与 Surface 的对应规则（每个 ViewRootImpl 对应一个 Surface）
   - WindowManager.addView 详解（完整流程）
   - SurfaceView 与 TextureView 架构对比
   - Dialog 与 PopupWindow 的 Surface 处理
   - ViewRootImpl 创建 Surface 源码分析
   - WMS 分配 Surface 源码分析
   - 验证方法（ViewRootImpl 数量/Surface 创建监控）
   - 常见问题（Activity 有几个 Surface？悬浮窗会创建 Surface 吗？）

**文档总数**：40 篇 → **41 篇**
**总大小**：3.60 MB → **3.65 MB**

---

### 2026-03-13 ⭐ JSON解析 + 依赖注入 + AndroidX 增强

**新增文档（2篇）**：

1. ✅ **Android_JSON解析详解.md** (43KB, 9章, 1564行)
   - org.json 原生解析（JSONObject/JSONArray/工具类封装）
   - Gson 完全指南（注解/泛型/自定义序列化器/Retrofit集成）
   - Moshi 完全指南（Kotlin支持/自定义适配器/Compose集成）
   - Jackson 简介
   - 性能对比 + 最佳实践 + 面试常见问题

2. ✅ **Android_依赖注入详解.md** (52KB, 9章, 1867行)
   - 依赖注入基础概念（DI/IoC/注入方式）
   - 手动依赖注入（工厂模式/服务定位器）
   - Hilt 完全指南（@Inject/@Module/组件层次/作用域/ViewModel/Entry Points/测试）
   - Koin 完全指南（Module定义/依赖声明/作用域/Compose/测试）
   - Dagger2 简介
   - 框架对比 + 最佳实践 + 面试常见问题

**文档增强（1篇）**：

1. ✅ **AndroidX_核心库详解.md** (89KB → 132KB, +1073行)
   - 新增 ViewPager2 完整讲解（基本使用/TabLayout联动/Transformer动画/生命周期）
   - 新增 Fragment 完整讲解（生命周期/事务管理/返回栈/通信/懒加载/DialogFragment）

**文档总数**：38 篇 → **40 篇**
**总大小**：3.33 MB → **3.60 MB**
**新增章节**：27 章 | **新增行数**：4000+ 行

---

### 2026-03-12 ⭐ Framework 核心文档新增 (6篇)

**新增 Framework 核心文档（6篇）**：

1. ✅ **Android_AMS_深度解析.md** (116KB, 10章, 47+面试题)
   - AMS 架构总览与内部架构
   - AMS 与 ATMS 职责划分 (Android 10+ 重构)
   - ActivityStack 与 TaskRecord 栈管理
   - 进程优先级 (oom_adj) 机制 (15级优先级/LMK)
   - LaunchMode 深度解析 (4种模式/Intent Flags/taskAffinity)
   - Activity 生命周期调度 (源码分析/状态转换)
   - 进程启动流程 (Zygote Fork 完整流程)
   - 源码路径 (AMS/ATMS/客户端源码)
   - 面试常见问题 (15道高频题)

2. ✅ **Android_WMS_窗口管理.md** (42KB, 10章)
   - WMS 架构总览 (内部架构/窗口层级结构)
   - WindowToken 与 WindowState (窗口令牌/状态)
   - Surface 与 SurfaceFlinger (图形系统架构)
   - ViewRootImpl 绘制调度 (performTraversals 流程)
   - Choreographer 编舞者 (VSync 协调机制)
   - VSync 信号机制 (垂直同步/三缓冲)
   - 窗口动画系统 (转场动画)
   - 面试常见问题 (8道高频题)

3. ✅ **Android_PMS_包管理.md** (11KB, 9章)
   - PMS 架构总览 (核心组件/数据结构)
   - APK 安装流程 (完整流程/命令)
   - 组件解析 (AndroidManifest/Intent匹配)
   - 权限管理机制 (权限类型/权限组/运行时权限)
   - 应用签名验证 (签名方案/命令)
   - dex2oat 编译流程 (ART虚拟机)
   - 面试常见问题 (6道高频题)

4. ✅ **Android_InputManager_输入系统.md** (9KB, 10章)
   - IMS 架构总览 (核心线程/Native组件)
   - 输入事件读取 (EventHub/原始事件)
   - 输入事件分发流程 (分发逻辑/ANR)
   - InputChannel 与 InputConnection (通信机制)
   - 触摸事件处理 (MotionEvent/分发流程)
   - 按键事件处理 (KeyEvent/系统按键)
   - 输入法交互 (IME架构/通信)
   - 面试常见问题 (6道高频题)

5. ✅ **Android_进程与线程调度.md** (26KB, 9章)
   - Linux 进程调度 (CFS)
   - Android 线程优先级 (nice值/优先级常量)
   - Binder 线程池 (架构/配置)
   - Looper/MessageQueue 原理 (源码分析)
   - HandlerThread/IntentService (使用示例)
   - 线程池最佳实践 (ThreadPoolExecutor/Coroutines)
   - 面试常见问题 (6道高频题)

6. ✅ **Android_系统启动流程.md** (26KB, 8章)
   - 启动流程总览 (Boot ROM → Launcher)
   - Init 进程启动 (init.rc 配置)
   - Zygote 进程 fork 机制 (预加载/Socket监听)
   - SystemServer 启动流程 (服务启动)
   - 系统服务启动顺序 (Bootstrap/Core/Other)
   - BootComplete 广播 (发送时机/监听)
   - 面试常见问题 (6道高频题)

**文档总数**：31 篇 → **37 篇**
**总大小**：3.07 MB → **3.30 MB**
**新增章节**：56 章 | **新增面试题**：47+ 道

---

### 2026-03-12 ⭐ SystemUI 增强 + Keyguard 章节

**SystemUI 文档重大更新**:
- ✅ **Android_SystemUI_详解.md** (184KB → 230KB, +1000行)
   - 新增第13章：Keyguard 锁屏系统（完整源码分析）
   - KeyguardService 启动流程
   - KeyguardViewMediator 源码分析
   - KeyguardUpdateMonitor 状态管理
   - 安全验证机制（图案/密码/PIN/生物识别）
   - 图案解锁源码分析
   - 生物识别解锁架构
   - 锁屏与 SystemUI 交互
   - Keyguard 状态机
   - 锁屏安全最佳实践
   - 新增第14章：面试常见问题补充（Keyguard 相关）

**文档总数**：31 篇（不变）
**总大小**：3.01 MB → **3.06 MB**

---

### 2026-03-12 ⭐ 架构进阶新增

**新增架构进阶（2篇）**：

1. ✅ **Android_插件化详解.md** (69KB, 18章, 1449行)
   - 第一篇：插件化基础（概述/原理/资源加载/四大组件插件化）
   - 第二篇：插件化实现（Activity/Service/Receiver/Provider）
   - 第三篇：主流框架（RePlugin/Shadow/VirtualApp）
   - 插件化 vs 组件化 vs 热修复对比

2. ✅ **Android_组件化详解.md** (46KB, 18章, 1028行)
   - 第一篇：组件化基础（概述/架构设计/模块解耦/路由框架）
   - 第二篇：组件化实现（项目结构/Gradle配置/调试发布）
   - 第三篇：实战案例（WanAndroid 组件化实践）

3. ✅ **Android_SystemUI_详解.md** (184KB, 11章, 3304行) ⭐
   - SystemUI 启动流程源码分析
   - AOD (Always On Display) 详解
   - 通知系统深度解析
   - NotificationManagerService 源码分析
   - RemoteViews 深度解析
   - 通知渲染流程与模板系统

**文档总数**：29 篇 → **31 篇**
**总大小**：2.81 MB → **3.01 MB**

---

### 2026-03-11 ⭐ Android 安全详解新增

1. ✅ **Android_安全详解.md** (120KB, 18章, 3730行)
   - 第一篇：Android 安全基础（签名/混淆/加固/反编译）
   - 第二篇：数据安全（加密/存储安全/网络安全）
   - 第三篇：进阶防护（组件安全/WebView/Intent/SO安全/运行时防护）
   - 主流加固方案对比（360/腾讯/阿里/梆梆）
   - 安全最佳实践与面试常见问题

**文档总数**：28 篇 → **29 篇**  
**总大小**：2.69 MB → **2.81 MB**

---

### 2026-03-11 ⭐ Jetpack Compose 增强

1. ✅ **Android_Jetpack_Compose详解.md** (62KB, 18章, 2600+行)
   - 全面重写，增强内容
   - Compose 基础概念 vs 传统 View
   - Composable/State/Modifier 深入解析
   - Material Design 3 完整组件示例
   - LazyColumn/LazyRow/LazyVerticalGrid 列表
   - 动画系统（AnimatedVisibility/Crossfade/animate*AsState/spring）
   - 主题与样式（Material Theme/Typography/Shapes）
   - ViewModel/Hilt 协程集成
   - Navigation 导航（基础/参数/Bottom Nav）
   - 与传统 View 互操作（AndroidView/ComposeView）
   - 手势处理（点击/拖动/缩放/变换）
   - Canvas 自定义绘制
   - 性能优化技巧
   - 15+ 面试常见问题

**文档总数**：27 篇 → **28 篇**  
**总大小**：2.63 MB → **2.69 MB**

---

### 2026-03-10 ⭐ 重大更新

**新增跨平台开发（3篇）**：

1. ✅ **React_Native完全指南.md** (29KB, 18章, 1160+行)
   - Facebook 跨平台框架
   - JavaScript/TypeScript 基础
   - React + React Native 核心
   - 状态管理/网络/动画
   - 新架构（Fabric/TurboModules）
   - 面试常见问题

2. ✅ **Flutter_完全指南.md** (29KB, 18章, 1000+行)
   - Google 跨平台 UI 框架
   - Dart 语言基础
   - Widget/状态管理
   - 性能优化

3. ✅ **Android_Jetpack_Compose详解.md** (84KB, 18章, 3100+行)
   - Android 声明式 UI
   - Composable/State/Modifier
   - 布局/动画/导航

**文档总数**：24 篇 → **27 篇**（增加 3 篇）  
**总大小**：2.46 MB → **2.63 MB**（增加 0.17 MB）

---

## 📞 联系方式

- **作者**：陈培根 (OpenClaw)
- **邮箱**：o1831938181o@gmail.com
- **GitLab**：https://gitlab.com/chenpeigen/android-development-docs
- **更新频率**：持续更新中

---

*Generated by OpenClaw | 2026-03-15*
