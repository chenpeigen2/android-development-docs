# Android 开发文档集

> 持续更新中... | 最后更新：2026-03-10

## 📚 文档统计

- **总文档数**：26 篇（新增 Flutter + Jetpack Compose）
- **总大小**：约 2.60 MB
- **总行数**：约 35,000+ 行

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

### 核心机制（8篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 10 | [Android_Binder机制深度解析.md](./Android_Binder机制深度解析.md) | 185KB | ⭐ 14 步完整调用链 + AIDL 示例 |
| 11 | [Android_Handler机制详解.md](./Android_Handler机制详解.md) | 90KB | Handler/Looper/MessageQueue 源码 |
| 12 | [Android_虚拟机详解.md](./Android_虚拟机详解.md) | 63KB | JVM/Dalvik/ART 对比 + GC 算法 |
| 13 | [Android_ClassLoader详解.md](./Android_ClassLoader详解.md) | 43KB | 双亲委派 + 热修复原理 |
| 14 | [Android_Zygote与SystemServer详解.md](./Android_Zygote与SystemServer详解.md) | 72KB | 进程启动 + 系统服务启动 |
| 15 | [AndroidX_核心库详解.md](./AndroidX_核心库详解.md) | 89KB | Lifecycle/ViewModel/LiveData/Room |
| 16 | [Android_架构模式演进详解.md](./Android_架构模式演进详解.md) | 74KB | MVC/MVP/MVVM/MVI 演进 |
| 17 | [Android_后台任务详解.md](./Android_后台任务详解.md) | 94KB | Service/JobScheduler/WorkManager |

### 性能优化（4篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 18 | [Android_性能优化详解.md](./Android_性能优化详解.md) | 156KB | 启动/UI/内存/电量/网络/APK 优化 |
| 19 | [Android_内存泄漏与内存优化详解.md](./Android_内存泄漏与内存优化详解.md) | 51KB | 内存泄漏检测 + 优化技巧 |
| 20 | [Android_ANR详解.md](./Android_ANR详解.md) | 39KB | ANR 原理 + 监控 + 优化 |
| 21 | [Android_Systrace_性能分析详解.md](./Android_Systrace_性能分析详解.md) | 132KB | Systrace 工具使用 + 分析方法 |

### 三方库详解（2篇）⭐ 热门

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 22 | [Android_三方库详解.md](./Android_三方库详解.md) | 201KB | Glide/Fresco/MMKV/PAG/Lottie |
| 23 | [Android_网络请求库详解.md](./Android_网络请求库详解.md) | 84KB | OkHttp/Retrofit 完全指南 |

### 跨平台开发（2篇）⭐ NEW!

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 24 | [Flutter_完全指南.md](./Flutter_完全指南.md) | 29KB | ⭐ Google 跨平台 UI 框架 |
| 25 | [Android_Jetpack_Compose详解.md](./Android_Jetpack_Compose详解.md) | 84KB | ⭐ Android 声明式 UI |

### 工具与构建（1篇）

| # | 文档名称 | 大小 | 说明 |
|---|----------|------|------|
| 26 | [Android_Gradle与AGP详解.md](./Android_Gradle与AGP详解.md) | 35KB | Gradle 构建流程 + AGP 详解 |

---

## 🌟 重点推荐

### 1. Flutter 完全指南 ⭐ NEW!

> **29KB | 18章 | 1000+ 行 | Google 跨平台 UI 框架**

**第一篇：Flutter 基础（6章）**
- Flutter 概述与核心优势
- Dart 语言基础（类型/函数/类/异步）
- 项目结构与 pubspec.yaml
- Widget 基础（StatelessWidget/StatefulWidget）
- 基础 Widget（Text/Image/Container/Button）
- 布局 Widget（Row/Column/ListView/GridView）

**第二篇：Flutter 进阶（6章）**
- 导航与路由（Navigator/路由传参/拦截器）
- 状态管理（Provider/Riverpod/Bloc/GetX）
- 网络请求（http/dio/JSON 序列化）
- 数据持久化（SharedPreferences/SQLite/Hive）
- 动画（Tween/AnimatedBuilder/Hero/Lottie）
- 手势与交互（GestureDetector/Dismissible）

**第三篇：Flutter 高级（6章）**
- 自定义 Widget（CustomPaint/RenderObject）
- Platform Channels（MethodChannel/EventChannel）
- 插件开发与发布
- 性能优化（渲染/内存/包体积）
- 测试（单元测试/Widget 测试/集成测试）
- 面试常见问题

**核心对比**：
- Flutter vs React Native（详细对比表）
- Flutter vs Jetpack Compose（选型建议）
- Widget 生命周期流程图
- 状态管理方案对比

---

### 2. Jetpack Compose 完全指南 ⭐ NEW!

> **84KB | 18章 | 3100+ 行 | Android 声明式 UI**

**第一篇：Compose 基础（12章）**
- Compose 概述与核心特性
- @Composable 函数详解
- 布局组件（Column/Row/Box/ConstraintLayout）
- Material 组件（Text/Button/TextField/Image/Card/Icon）
- LazyColumn/LazyRow 懒加载列表
- 动画（AnimatedVisibility/animate*AsState）
- 主题与样式（MaterialTheme/颜色/字体）
- Navigation 导航
- ViewModel 集成
- 协程集成（LaunchedEffect/DisposableEffect）

**第二篇：Compose 进阶（6章）**
- 手势处理（点击/长按/拖拽/缩放）
- Canvas 绘图
- View 互操作（AndroidView/ComposeView）
- 性能优化（重组机制/稳定性）
- UI 测试（Semantics/测试 API）
- 面试常见问题

**核心优势**：
- 声明式 UI vs 命令式 UI
- 智能重组机制
- Kotlin 协程集成
- 与传统 View 混合开发

---

### 3. Android 三方库详解

> **201KB | 42章 | 5000+ 行 | 面试高频**

**第一部分：图片加载库**
- **Glide**（10章）- Google 推荐
  - 三级缓存机制
  - 生命周期自动管理
  - 图片变换（圆形/圆角/模糊）
  - 面试常见问题

- **Fresco**（7章）- Facebook 出品
  - Native 内存管理
  - 渐进式 JPEG 支持

**第二部分：数据存储库**
- **MMKV**（8章）- 腾讯开源
  - mmap 原理
  - 多进程安全
  - 性能对比（100x SharedPreferences）

**第三部分：动画框架**
- **PAG**（6章）- 腾讯高性能动画
- **Lottie**（7章）- Airbnb 动画库

---

### 4. Android 网络请求库详解

> **84KB | 20章 | 2700+ 行 | 面试必看**

**第一篇：OkHttp（10章）**
- 拦截器机制
- 缓存策略
- 连接池管理
- WebSocket
- 面试常见问题

**第二篇：Retrofit（10章）**
- 动态代理原理
- 注解详解
- Converter/CallAdapter
- 与协程集成

---

### 5. Android Binder 机制深度解析

> **185KB | 2085 行 | 面试高频必看**

- 全局流程图（14 步完整调用链）
- Binder 驱动层核心源码
- mmap 一次拷贝原理
- AIDL 双向通信示例

---

## 🚀 新增内容

### 2026-03-10 ⭐ 重大更新

**新增跨平台开发（2篇）**：

1. ✅ **Flutter_完全指南.md** (29KB, 18章, 1000+行)
   - Google 跨平台 UI 框架
   - Dart 语言基础
   - Widget/状态管理/网络/动画
   - Platform Channels
   - 性能优化
   - 面试常见问题

2. ✅ **Android_Jetpack_Compose详解.md** (84KB, 18章, 3100+行)
   - Android 声明式 UI
   - Composable/State/Modifier
   - 布局/动画/导航
   - 手势/Canvas/性能优化
   - 面试常见问题

**文档总数**：24 篇 → **26 篇**（增加 2 篇）  
**总大小**：2.46 MB → **2.60 MB**（增加 0.14 MB）

---

## 📊 分类统计

| 类别 | 文档数 | 总大小 | 说明 |
|------|--------|--------|------|
| 基础知识 | 9 篇 | 1.08 MB | View/事件/动画/四大组件 |
| 核心机制 | 8 篇 | 0.80 MB | Binder/Handler/虚拟机/架构 |
| 性能优化 | 4 篇 | 0.38 MB | 性能/内存/ANR/Systrace |
| 三方库详解 | 2 篇 | 0.28 MB | 图片/网络/存储/动画库 |
| 跨平台开发 | 2 篇 | 0.11 MB | Flutter/Compose ⭐ NEW! |
| 工具与构建 | 1 篇 | 0.03 MB | Gradle/AGP |
| **总计** | **26 篇** | **2.60 MB** | **35,000+ 行** |

---

## 🎯 学习路径

### Android 开发者

1. **基础阶段**：View 绘制 → 事件分发 → 四大组件
2. **进阶阶段**：Binder → Handler → 虚拟机 → 性能优化
3. **实战阶段**：三方库（Glide/Retrofit）→ 架构模式
4. **现代 UI**：Jetpack Compose（Android 官方声明式 UI）

### 跨平台开发者

1. **Flutter 方向**：Dart → Widget → 状态管理 → 网络 → 动画
2. **React Native 方向**：（规划中）
3. **Compose Multiplatform**：（规划中）

---

## 📞 联系方式

- **作者**：陈培根 (OpenClaw)
- **邮箱**：o1831938181o@gmail.com
- **GitLab**：https://gitlab.com/chenpeigen/android-development-docs
- **更新频率**：持续更新中

---

*Generated by OpenClaw | 2026-03-10*
