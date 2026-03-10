# Android 三方库 - 补充建议

## 当前已覆盖的库

✅ **图片加载**
- Glide
- Fresco

✅ **数据存储**
- MMKV

✅ **动画框架**
- PAG
- Lottie

---

## 建议补充的三方库

### 1. 网络请求库（必选）

#### 🌟 OkHttp
- **重要性**: ⭐⭐⭐⭐⭐
- **原因**: 
  - Android 网络请求的事实标准
  - Glide、Retrofit 都依赖它
  - 面试必问（拦截器、缓存、连接池）
  - 使用率 > 90%

**建议章节**：
- OkHttp 概述与核心特性
- 基本使用（同步/异步/文件上传下载）
- 拦截器机制（应用/网络/连接/呼叫服务器）
- 缓存策略
- 连接池与复用
- HTTPS 与证书绑定
- WebSocket
- 性能优化
- 面试常见问题（10+ 题）

#### 🌟 Retrofit
- **重要性**: ⭐⭐⭐⭐⭐
- **原因**:
  - RESTful API 标准库
  - 与 OkHttp 配合使用
  - 面试高频（动态代理、注解解析）
  - MVVM 架构必备

**建议章节**：
- Retrofit 概述
- 基本使用（GET/POST/PUT/DELETE）
- 注解详解（@GET/@POST/@Body/@Field 等）
- 动态代理原理
- Converter（JSON/XML/ProtoBuf）
- CallAdapter（RxJava/Coroutines）
- 拦截器与日志
- 文件上传下载
- 错误处理
- 面试常见问题

---

### 2. 依赖注入库（必选）

#### 🌟 Hilt
- **重要性**: ⭐⭐⭐⭐⭐
- **原因**:
  - Google 官方推荐
  - 基于 Dagger2，简化使用
  - MVVM 架构必备
  - 面试高频

**建议章节**：
- Hilt 概述与优势
- 基本使用（@HiltAndroidApp/@AndroidEntryPoint）
- 依赖注入（@Inject/@Module/@Provides）
- 组件与作用域
- ViewModel 注入
- Fragment 注入
- 预定义限定符
- Entry Points
- 测试支持
- Hilt vs Dagger2 vs Koin
- 面试常见问题

#### ⭐ Koin
- **重要性**: ⭐⭐⭐⭐
- **原因**:
  - Kotlin 项目首选
  - 学习曲线平缓
  - 轻量级
  - 面试常见对比

**建议章节**：
- Koin 概述
- 基本使用
- Module 定义
- 依赖注入
- ViewModel 注入
- Scope 作用域
- Koin vs Hilt
- 面试常见问题

---

### 3. 响应式编程库（必选）

#### 🌟 RxJava
- **重要性**: ⭐⭐⭐⭐⭐
- **原因**:
  - 响应式编程标准
  - 面试必问（操作符、线程切换）
  - 复杂业务场景必备
  - 学习难度大，需要详细讲解

**建议章节**：
- RxJava 概述与核心概念
- Observable 创建（just/from/create/defer）
- 操作符详解（map/flatmap/filter/zip/merge）
- 线程调度（Schedulers）
- 背压策略
- 错误处理
- RxBus
- RxJava vs Coroutines
- 内存泄漏防护
- 面试常见问题（15+ 题）

#### 🌟 Kotlin Coroutines
- **重要性**: ⭐⭐⭐⭐⭐
- **原因**:
  - Kotlin 协程是趋势
  - 替代 RxJava
  - MVVM 架构必备
  - 面试高频

**建议章节**：
- 协程概述与核心概念
- 基本使用（launch/async/withContext）
- 作用域（GlobalScope/lifecycleScope/viewModelScope）
- 调度器（Dispatchers）
- Flow（冷流/热流）
- Channel
- 协程异常处理
- 协程取消
- 协程 vs RxJava
- 面试常见问题（10+ 题）

---

### 4. 数据序列化库（推荐）

#### 🌟 Gson
- **重要性**: ⭐⭐⭐⭐
- **原因**:
  - Google 官方库
  - 使用广泛
  - 面试常见（泛型擦除、反序列化）

**建议章节**：
- Gson 概述
- 基本使用
- 注解详解（@SerializedName/@Expose）
- 泛型处理
- 自定义序列化
- 复杂对象解析
- 性能优化
- Gson vs Moshi vs Jackson
- 面试常见问题

#### ⭐ Moshi
- **重要性**: ⭐⭐⭐⭐
- **原因**:
  - Square 出品
  - Kotlin 友好
  - 性能优于 Gson

---

### 5. 数据库库（推荐）

#### 🌟 Room
- **重要性**: ⭐⭐⭐⭐⭐
- **原因**:
  - Google 官方推荐
  - SQLite 的封装
  - Jetpack 组件
  - 支持协程和 RxJava
  - 面试高频

**建议章节**：
- Room 概述
- 基本使用（Entity/Dao/Database）
- 关系映射（一对一/一对多/多对多）
- 类型转换器
- 数据库迁移
- 协程支持
- RxJava 支持
- 性能优化
- Room vs GreenDAO vs Realm
- 面试常见问题（10+ 题）

---

### 6. 异步任务库（推荐）

#### ⭐ WorkManager
- **重要性**: ⭐⭐⭐⭐
- **原因**:
  - Jetpack 组件
  - 后台任务标准方案
  - 面试常见

**建议章节**：
- WorkManager 概述
- 基本使用（Worker/OneTimeWorkRequest/PeriodicWorkRequest）
- 任务约束
- 任务链
- 进度监听
- 协程支持
- 面试常见问题

---

### 7. 路由库（推荐）

#### ⭐ ARouter
- **重要性**: ⭐⭐⭐⭐
- **原因**:
  - 阿里开源
  - 组件化必备
  - 面试常见（路由原理）

**建议章节**：
- ARouter 概述
- 基本使用（@Route/@Autowired）
- 路由跳转
- 参数传递
- 拦截器
- 依赖注入
- 路由原理（APT）
- ARouter vs DeepLink
- 面试常见问题

---

### 8. 日志库（推荐）

#### ⭐ Timber
- **重要性**: ⭐⭐⭐
- **原因**:
  - JakeWharton 出品
  - 轻量级
  - 面试可能问到

---

### 9. 事件总线库（可选）

#### ⭐ EventBus
- **重要性**: ⭐⭐⭐
- **原因**:
  - 虽然使用率下降，但面试可能问到
  - 理解发布-订阅模式

**建议章节**：
- EventBus 概述
- 基本使用
- 线程模式
- 粘性事件
- 优先级
- EventBus vs RxJava vs LiveData
- 面试常见问题

---

### 10. 权限库（可选）

#### ⭐ RxPermissions
- **重要性**: ⭐⭐⭐
- **原因**:
  - 简化权限请求
  - 面试可能问到

---

### 11. 图片选择库（可选）

#### ⭐ Matisse
- **重要性**: ⭐⭐⭐
- **原因**:
  - 知乎开源
  - 图片选择标准方案

---

### 12. 崩溃收集库（可选）

#### ⭐ Bugly
- **重要性**: ⭐⭐⭐
- **原因**:
  - 腾讯出品
  - 崩溃收集标准方案

---

## 优先级排序

### 必选（⭐⭐⭐⭐⭐）
1. **OkHttp** - 网络基础
2. **Retrofit** - API 封装
3. **RxJava** - 响应式编程
4. **Kotlin Coroutines** - 协程
5. **Hilt** - 依赖注入
6. **Room** - 数据库

### 推荐（⭐⭐⭐⭐）
1. **Gson/Moshi** - JSON 解析
2. **Koin** - 依赖注入（Kotlin 项目）
3. **WorkManager** - 后台任务
4. **ARouter** - 路由

### 可选（⭐⭐⭐）
1. **EventBus** - 事件总线
2. **Timber** - 日志
3. **RxPermissions** - 权限
4. **Matisse** - 图片选择
5. **Bugly** - 崩溃收集

---

## 建议的文档结构

```
Android_三方库完全指南
├── 第一部分：图片加载库
│   ├── Glide
│   └── Fresco
│
├── 第二部分：网络请求库 ⭐ 新增
│   ├── OkHttp
│   └── Retrofit
│
├── 第三部分：依赖注入库 ⭐ 新增
│   ├── Hilt
│   └── Koin
│
├── 第四部分：响应式编程库 ⭐ 新增
│   ├── RxJava
│   └── Kotlin Coroutines
│
├── 第五部分：数据存储库
│   ├── MMKV
│   └── Room ⭐ 新增
│
├── 第六部分：动画框架
│   ├── PAG
│   └── Lottie
│
├── 第七部分：数据序列化库 ⭐ 新增
│   ├── Gson
│   └── Moshi
│
├── 第八部分：架构组件库 ⭐ 新增
│   ├── WorkManager
│   └── ARouter
│
└── 第九部分：对比与选型
```

---

## 面试重点分析

根据面试频率，建议重点补充：

### 高频（90%+）
1. ✅ OkHttp（拦截器、缓存）
2. ✅ Retrofit（动态代理）
3. ✅ RxJava（操作符、线程切换）
4. ✅ Coroutines（协程原理）
5. ✅ Hilt（依赖注入）

### 中频（60%+）
1. ✅ Room（ORM、迁移）
2. ✅ Gson（泛型擦除）
3. ✅ WorkManager（后台任务）
4. ✅ ARouter（路由原理）

### 低频（30%+）
1. ⚠️ EventBus
2. ⚠️ Timber
3. ⚠️ RxPermissions

---

## 总结

**当前文档缺失的重要库**：
1. ❌ OkHttp（最重要）
2. ❌ Retrofit（最重要）
3. ❌ RxJava（最重要）
4. ❌ Kotlin Coroutines（最重要）
5. ❌ Hilt（重要）
6. ❌ Room（重要）
7. ❌ Gson（重要）

**建议行动**：
1. 优先补充 OkHttp + Retrofit（网络层）
2. 其次补充 RxJava + Coroutines（异步层）
3. 然后补充 Hilt（依赖注入）
4. 最后补充 Room + Gson（数据层）

这样可以形成一个完整的 Android 开发知识体系！
