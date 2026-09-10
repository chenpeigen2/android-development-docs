# Android 组件化详解

> 适用环境：Android 17（API 37）；模块边界采用 Gradle/AGP 公共 API，ARouter 1.5.2 独立作为传统注解处理器接入示例。

> 作者：OpenClaw | 日期：2026-04-02
> 组件化架构完全指南 | 模块解耦、路由、通信

---

## 目录

- [1. 概述](#1-概述)
  - [1.1 什么是组件化](#11-什么是组件化)
  - [1.2 组件化 vs 单工程 vs 插件化](#12-组件化-vs-单工程-vs-插件化)
  - [1.3 组件化优势](#13-组件化优势)
- [2. 分层架构](#2-分层架构)
  - [2.1 四层结构](#21-四层结构)
  - [2.2 模块依赖规则](#22-模块依赖规则)
- [3. 模块划分原则](#3-模块划分原则)
  - [3.1 五大原则](#31-五大原则)
  - [3.2 常见模块划分](#32-常见模块划分)
  - [3.3 接口定义规范](#33-接口定义规范)
- [4. 模块解耦方案](#4-模块解耦方案)
  - [4.1 接口解耦](#41-接口解耦)
  - [4.2 依赖注入（Koin / Hilt）](#42-依赖注入koin--hilt)
  - [4.3 事件总线](#43-事件总线)
  - [4.4 服务发现](#44-服务发现)
- [5. 路由框架](#5-路由框架)
  - [5.1 路由原理](#51-路由原理)
  - [5.2 ARouter 使用](#52-arouter-使用)
  - [5.3 路由拦截器](#53-路由拦截器)
  - [5.4 路由表生成原理](#54-路由表生成原理)
- [6. 组件通信](#6-组件通信)
  - [6.1 页面跳转](#61-页面跳转)
  - [6.2 数据传递](#62-数据传递)
  - [6.3 服务调用](#63-服务调用)
  - [6.4 跨进程通信](#64-跨进程通信)
- [7. 项目结构与 Gradle 配置](#7-项目结构与-gradle-配置)
  - [7.1 目录结构](#71-目录结构)
  - [7.2 Gradle 配置](#72-gradle-配置)
  - [7.3 模块独立运行配置](#73-模块独立运行配置)
  - [7.4 资源冲突管理](#74-资源冲突管理)
- [8. 最佳实践](#8-最佳实践)
  - [8.1 模块边界定义](#81-模块边界定义)
  - [8.2 API 设计原则](#82-api-设计原则)
  - [8.3 版本管理](#83-版本管理)
  - [8.4 调试技巧](#84-调试技巧)
- [9. 面试常见问题](#9-面试常见问题)
  - [Q1：组件化原理？](#q1组件化原理)
  - [Q2：ARouter 路由表是如何生成的？](#q2arouter-路由表是如何生成的)
  - [Q3：模块间如何通信？](#q3模块间如何通信)
  - [Q4：组件化和插件化的区别？](#q4组件化和插件化的区别)
  - [Q5：组件化有哪些问题/挑战？](#q5组件化有哪些问题挑战)
- [10. 业界实践：百度App组件化之路](#10-业界实践百度app组件化之路)
  - [10.1 大型App复杂度来源](#101-大型app复杂度来源)
  - [10.2 组件化演进历程](#102-组件化演进历程)
    - [阶段一：2013年 — 初始态（钻木取火）](#阶段一2013年--初始态钻木取火)
    - [阶段二：2014-2015年 — 蒸汽机时代](#阶段二2014-2015年--蒸汽机时代)
    - [阶段三：2016-2017年 — 电力时代](#阶段三2016-2017年--电力时代)
    - [阶段四：2018-2019年 — 理想态（核能时代）](#阶段四2018-2019年--理想态核能时代)
  - [10.3 组件化实现路径](#103-组件化实现路径)
    - [第一步：编译隔离、架构分层及层级访问限制](#第一步编译隔离架构分层及层级访问限制)
    - [第二步：三方库规范化与基础库体系化](#第二步三方库规范化与基础库体系化)
    - [第三步：运行时分发与隔离服务](#第三步运行时分发与隔离服务)
    - [第四步：服务层建立](#第四步服务层建立)
    - [第五步：建立组件模型](#第五步建立组件模型)
    - [第六步：业务组件化](#第六步业务组件化)
    - [第七步：劣化控制](#第七步劣化控制)
  - [10.4 组件化收益](#104-组件化收益)
  - [10.5 核心原则](#105-核心原则)
- [参考资料](#参考资料)
- [11. 可替换的组件契约与装配](#11-可替换的组件契约与装配)
  - [11.1 API 模块不暴露实现类型](#111-api-模块不暴露实现类型)
  - [11.2 api 与 implementation 的传播](#112-api-与-implementation-的传播)
  - [11.3 不依赖私有路由 API 的页面跳转](#113-不依赖私有路由-api-的页面跳转)
  - [11.4 独立调试与启动顺序](#114-独立调试与启动顺序)
  - [11.5 Android 17 的组件边界](#115-android-17-的组件边界)

---

## 1. 概述

### 1.1 什么是组件化

组件化是将一个大型 App 拆分为多个独立业务模块的架构方式。每个模块可独立开发、编译、运行，模块间通过接口或路由进行通信，实现真正的解耦。

```text
┌─────────────────────────────────────────┐
│            主工程 (App Shell)           │
│  · 集成所有模块                         │
│  · 统一初始化                           │
│  · 充当运行容器                         │
└──────────────────┬──────────────────────┘
                   │
     ┌─────────────┼─────────────┬─────────────┐
     ▼             ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ 用户模块 │  │ 订单模块 │  │ 商品模块 │  │ 支付模块 │
│ (独立)  │  │ (独立)  │  │ (独立)  │  │ (独立)  │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     └─────────────┴─────────────┴─────────────┘
                          │
                   ┌──────▼──────┐
                   │  公共层     │
                   │ 网络/图片   │
                   │ 路由/工具  │
                   └─────────────┘
```

**核心特点：**
- 业务模块化：按业务域拆分为独立 Module
- 编译时解耦：模块间通过接口/路由通信，不直接依赖
- 统一打包：所有模块编译到同一个 APK
- 独立运行：模块可配置为独立 App 单独调试

### 1.2 组件化 vs 单工程 vs 插件化

| 对比项 | 单工程 | 组件化 | 插件化 |
|--------|--------|--------|--------|
| 代码耦合 | 高耦合 | 低耦合 | 低耦合 |
| 编译速度 | 慢（全量编译） | 快（增量编译） | 快（插件独立编译） |
| 模块独立运行 | ❌ | ✅ | ✅ |
| 动态更新 | ❌ | ❌ | ✅（热更新） |
| 复杂度 | 低 | 中 | 高 |
| 适用场景 | 小型项目 | 中大型项目 | 需要动态发布的项目 |

> **组件化 ≠ 插件化**：插件化可以动态加载插件（.apk/.so），组件化只是代码拆分为独立模块，打包时仍需全量编译进 APK。如需动态更新能力，可进一步引入插件化框架（如 Shadow、RePlugin）。

### 1.3 组件化优势

| 优势 | 说明 |
|------|------|
| **解耦** | 模块间通过接口通信，直接依赖降为零 |
| **并行开发** | 不同团队独立开发不同模块 |
| **编译加速** | 增量编译，只编译修改的模块 |
| **独立调试** | 模块可单独打包为 App 运行 |
| **代码复用** | 公共组件可被多个模块复用 |
| **职责清晰** | 模块边界明确，单一职责 |
| **易于测试** | 模块可独立测试 |

---

## 2. 分层架构

### 2.1 四层结构

```text
┌──────────────────────────────────────────────────────┐
│                 Layer 1: App Shell                   │
│               （应用壳工程）                          │
│  · 集成所有业务模块                                  │
│  · Application 初始化                                 │
│  · 主界面容器                                         │
└────────────────────────────┬─────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  业务模块层    │  │  业务模块层    │  │  业务模块层    │
│  module-user  │  │  module-order │  │ module-product│
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        └────────────────────┼────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────┐
│              Layer 3: 公共业务层                      │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│   │ 路由 SDK  │  │ 登录 SDK  │  │ 分享 SDK  │         │
│   └──────────┘  └──────────┘  └──────────┘         │
└────────────────────────────┬─────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────┐
│              Layer 4: 基础组件层                       │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│   │ 网络库    │  │ 图片加载  │  │ 工具类   │         │
│   └──────────┘  └──────────┘  └──────────┘         │
└──────────────────────────────────────────────────────┘
```

**各层职责：**

| 层级 | 名称 | 职责 | 依赖关系 |
|------|------|------|----------|
| L1 | App Shell | 集成模块、初始化、主界面 | 依赖所有业务模块 |
| L2 | 业务模块 | 具体业务功能实现 | 依赖公共业务层 + 基础组件层 |
| L3 | 公共业务 | 跨模块业务逻辑（路由、登录等） | 依赖基础组件层 |
| L4 | 基础组件 | 通用功能封装（网络、图片、工具） | 无依赖 |

### 2.2 模块依赖规则

```text
                    ┌─────────┐
                    │   App   │
                    └────┬────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌───────────┐      ┌───────────┐      ┌───────────┐
│module-user│      │module-order│     │module-prod │
└─────┬─────┘      └─────┬─────┘      └─────┬─────┘
      └──────────────────┼──────────────────┘
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
      ┌───────────┐           ┌───────────┐
      │lib-common │           │lib-router │
      └───────────┘           └───────────┘
```

**依赖规则：**
1. App 依赖所有业务模块
2. 业务模块之间**不能**相互依赖
3. 业务模块依赖公共层
4. 公共层之间避免循环依赖
5. 依赖方向从上到下，**不能反向**

---

## 3. 模块划分原则

### 3.1 五大原则

| 原则 | 说明 | 正确示例 | 错误示例 |
|------|------|----------|----------|
| **SRP** 单一职责 | 每个模块只负责一个业务域 | module-user：用户相关 | module-all：什么都装 |
| **DIP** 依赖倒置 | 高层依赖抽象，不依赖具体实现 | 依赖 `ILoginService` 接口 | 依赖 `LoginServiceImpl` 实现 |
| **ISP** 接口隔离 | 接口小而专一 | `IUserService` + `IOrderService` 分开 | `IService` 包含所有功能 |
| **高内聚低耦合** | 模块内高度相关，模块间最小依赖 | 模块间通过路由通信 | 模块间直接调用 |
| **按业务域划分** | 以业务边界为模块边界 | 电商：用户/商品/订单/支付 | 按技术层划分 |

### 3.2 常见模块划分

**电商项目：**
```text
module-home      # 首屏、首页
module-user      # 登录、注册、个人中心
module-product   # 商品列表、商品详情
module-order     # 订单、购物车
module-pay       # 支付
module-search    # 搜索
module-shop      # 店铺
```

**社交项目：**
```text
module-home      # 首页 Feed
module-message   # 消息、聊天
module-moment    # 动态、朋友圈
module-user      # 用户、设置
module-medial    # 拍照、图片处理
```

### 3.3 接口定义规范

接口放在公共层（`lib-common`），模块只依赖接口，不依赖实现：

```text
lib-common/
├── api/
│   ├── IUserService.kt      # 用户服务接口
│   ├── IOrderService.kt     # 订单服务接口
│   └── IModuleInit.kt       # 模块初始化接口
```

```kotlin
// lib-common/api/IUserService.kt
interface IUserService : IProvider {
    fun isLogin(): Boolean
    fun getUserInfo(): UserInfo?
    fun login(context: Context)
    fun logout()
}

// module-user 实现
@Route(path = "/user/service")
class UserServiceImpl : IUserService {
    override fun init(context: Context) {}
    override fun isLogin() = UserManager.isLogin()
    override fun getUserInfo() = UserManager.userInfo
    override fun login(context: Context) {
        context.startActivity(Intent(context, LoginActivity::class.java))
    }
    override fun logout() { UserManager.logout() }
}
```

---

## 4. 模块解耦方案

### 4.1 接口解耦

接口解耦是组件化的基础。模块间不直接引用，而是通过公共接口通信。

**方案：服务定位器 + 接口**

```kotlin
// 1. 定义接口 (lib-common)
interface ILoginService {
    fun isLogin(): Boolean
    fun getToken(): String?
}

// 2. 模块实现 (module-user)
class LoginServiceImpl : ILoginService {
    override fun isLogin() = TokenManager.hasToken()
    override fun getToken() = TokenManager.token
}

// 3. App 启动时注册 (App 模块)
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        ServiceLoader.load(ILoginService::class.java, LoginServiceImpl())
    }
}

// 4. 其他模块调用 (module-order)
class OrderPresenter {
    private val loginService = ServiceLoader.get(ILoginService::class.java)

    fun createOrder() {
        if (!loginService.isLogin()) {
            // 跳转登录
            return
        }
        // 正常业务
    }
}
```

### 4.2 依赖注入（Koin / Hilt）

**Koin 示例：**

```kotlin
// 1. 定义模块
val userModule = module {
    single<IUserService> { UserServiceImpl() }
    single<UserRepository> { UserRepositoryImpl(get()) }
    viewModel { UserViewModel(get()) }
}

val orderModule = module {
    single<IOrderService> { OrderServiceImpl(get()) }
    viewModel { OrderViewModel(get(), get()) }
}

// 2. 初始化
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@App)
            modules(userModule, orderModule, commonModule)
        }
    }
}

// 3. 使用（构造函数注入 / by inject）
class OrderActivity : AppCompatActivity() {
    private val viewModel: OrderViewModel by viewModel()
    private val userService: IUserService by inject()
}
```

**Hilt 示例（Android 官方推荐）：**

```kotlin
// 1. 依赖 @Module
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient = ...

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit = ...
}

// 2. 在接口实现上标注 @Singleton + @EntryPoint
// 3. 在 Application 中 @HiltAndroidApp
// 4. 在 Activity/ViewModel 中 @AndroidEntryPoint
```

### 4.3 事件总线

对于跨模块的事件通知（如登录状态变化），使用事件总线避免直接耦合：

```kotlin
// 1. 定义事件（lib-common）
sealed class UserEvent {
    data class Login(val user: UserInfo) : UserEvent()
    data class Logout(val reason: String = "") : UserEvent()
    data class ProfileUpdate(val user: UserInfo) : UserEvent()
}

// 2. 事件总线（基于 LiveData）
object EventBus {
    private val events = ConcurrentHashMap<Class<*>, MutableLiveData<*>>()

    @Suppress("UNCHECKED_CAST")
    fun <T> getEvent(clazz: Class<T>): MutableLiveData<T> {
        return events.getOrPut(clazz) { MutableLiveData<T>() } as MutableLiveData<T>
    }

    fun <T> post(event: T) {
        getEvent(event!!::class.java).postValue(event)
    }
}

// 3. 发送事件 (module-user)
fun onLoginSuccess(user: UserInfo) {
    EventBus.post(UserEvent.Login(user))
}

// 4. 订阅事件 (module-order)
class OrderListFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        EventBus.getEvent(UserEvent.Login::class.java)
            .observe(viewLifecycleOwner) { event ->
                refreshOrderList()  // 登录成功后刷新订单
            }
    }
}
```

> **注意**：事件总线适合**一对一**或**少量订阅**的场景。对于复杂的跨模块通信，优先使用服务调用（接口解耦），因为接口调用是显式的、可追溯的，事件总线容易导致事件流向不清晰。

### 4.4 服务发现

基于接口的服务发现，让模块无需直接引用实现类：

```kotlin
// 基于 ARouter 的服务发现
interface IConfigService : IProvider {
    fun getAppId(): String
    fun getApiHost(): String
}

@Route(path = "/common/config", name = "配置服务")
class ConfigServiceImpl : IConfigService {
    override fun init(context: Context) { /* 初始化 */ }
    override fun getAppId() = "app_12345"
    override fun getApiHost() = "https://api.example.com"
}

// 获取服务（任意模块）
val configService = ARouter.getInstance()
    .build("/common/config")
    .navigation() as IConfigService

println(configService.getApiHost())
```

---

## 5. 路由框架

### 5.1 路由原理

路由框架解决的是**跨模块页面跳转**问题。模块之间没有直接依赖，无法通过 `startActivity` 直接启动其他模块的 Activity。

```text
┌──────────────────────────────────────────────────────────────┐
│                        路由原理                               │
└──────────────────────────────────────────────────────────────┘

  调用方                          路由中心                       目标模块
     │                               │                            │
     │  navigate("/order/detail")   │                            │
     │ ─────────────────────────────►│                            │
     │                               │ 查找路由表                  │
     │                               │ path → Activity Class      │
     │                               │                            │
     │                               │ Intent                     │
     │                               │───────────────────────────►│
     │                               │         startActivity()    │
     │                               │                            │
     │                               │◄───────────────────────────│
     │                               │       onCreate()           │
     │                               │                            │

编译时（APT）：
  @Route(path = "/order/detail")
  class OrderDetailActivity ...
  ──────────────────────────────► APT 生成路由表类

运行时：
  navigate("/order/detail")
  ──────────────────────────────► 路由中心查表 ──► Intent.startActivity()
```

**路由核心能力：**
1. **页面导航**：`/user/login` → `LoginActivity`
2. **参数注入**：自动解析路由参数到目标 Activity
3. **拦截器**：登录拦截、埋点等
4. **服务调用**：获取跨模块服务实例

### 5.2 ARouter 使用

**1. Gradle 配置（ARouter 1.5.2，外置 Kotlin/KAPT 工具链）：**

ARouter API、compiler 和可选 register 插件是不同构件，各有独立版本。这里使用注解处理器，不使用字节码注册插件；`kapt {}` 与 `android {}` 同级。

```kotlin
// 模块 build.gradle.kts；限定外置 Kotlin/KAPT 的旧工具链。
// Android/Kotlin 插件版本必须由根工程统一提供。
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.kapt")
}

kapt { // 与 android 同级
    arguments {
        arg("AROUTER_MODULE_NAME", project.name)
        arg("AROUTER_GENERATE_DOC", "enable")
    }
}

dependencies {
    implementation("com.alibaba:arouter-api:1.5.2")
    kapt("com.alibaba:arouter-compiler:1.5.2")
}
```

ARouter 1.5.2 通过注解处理器生成路由表，以下配置属于外置 Kotlin/KAPT 工具链。AGP 9 内置 Kotlin 工程使用支持的 KSP 处理器或 legacy-kapt 迁移路径，不能仅重命名配置就把 Javac 处理器变成 KSP 处理器。参考：[ARouter 1.5.2](https://github.com/alibaba/ARouter/blob/1.5.2/README_CN.md)、[内置 Kotlin 迁移](https://developer.android.com/build/migrate-to-built-in-kotlin)。

**2. 初始化：**

```kotlin
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            ARouter.openDebug()
            ARouter.openLog()
        }
        ARouter.init(this)
    }
}
```

**3. 定义路由页面：**

```kotlin
// 简单页面
@Route(path = "/user/login")
class LoginActivity : AppCompatActivity()

// 带参数页面（自动注入）
@Route(path = "/user/profile")
class ProfileActivity : AppCompatActivity() {
    @Autowired
    lateinit var userId: String

    @Autowired(name = "from")
    lateinit var fromPage: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ARouter.getInstance().inject(this)  // 必须调用，注入参数
    }
}

// Fragment
@Route(path = "/order/list_fragment")
class OrderListFragment : Fragment()
```

**4. 跳转：**

```kotlin
// 基本跳转
ARouter.getInstance().build("/user/login").navigation()

// 带参数
ARouter.getInstance()
    .build("/user/profile")
    .withString("userId", "123")
    .withString("from", "home")
    .navigation()

// 获取 Fragment
val fragment = ARouter.getInstance()
    .build("/order/list_fragment")
    .navigation() as OrderListFragment

// 带结果回调
ARouter.getInstance()
    .build("/user/select")
    .navigation(this, object : NavigationCallback {
        override fun onFound(postcard: Postcard) {}
        override fun onLost(postcard: Postcard) {}
        override fun onArrival(postcard: Postcard) {}
        override fun onInterrupt(postcard: Postcard) {}
    })

// 在 Fragment 中跳转
ARouter.getInstance().build("/order/detail")
    .withString("orderId", orderId)
    .navigation(requireContext())
```

### 5.3 路由拦截器

拦截器用于在路由跳转前做统一处理，如登录校验、埋点：

```kotlin
// 1. 定义拦截器
@Interceptor(priority = 8, name = "登录拦截器")
class LoginInterceptor : IInterceptor {

    override fun init(context: Context) {
        // 初始化，只会调用一次
    }

    override fun process(postcard: Postcard, callback: InterceptorCallback) {
        // 检查是否需要登录
        if ((postcard.extra and RouteExtra.NEED_LOGIN) != 0 && !UserManager.isLogin()) {
            // 中断跳转
            callback.onInterrupt(IllegalStateException("需要登录"))
            // 登录页不设置 NEED_LOGIN，避免递归进入同一拦截分支。
            // ARouter 的 Activity navigation 路径内部切回主线程；拦截器不直接操作 View。
            ARouter.getInstance().build("/user/login").navigation()
            return
        }
        // 继续
        callback.onContinue(postcard)
    }
}

// 2. 定义标记
object RouteExtra {
    const val NEED_LOGIN = 1
}

// 3. 在路由上标记
@Route(path = "/order/list", extras = RouteExtra.NEED_LOGIN)
class OrderListActivity : AppCompatActivity()

// 4. 多个拦截器按 priority 从小到大执行
// priority = 1 → priority = 8 → 目标页面
```

`extras` 是应用定义的位标记，上述按位判断允许与其他标记组合；每个分支只调用一次 `onContinue` 或 `onInterrupt`。拦截器中的 UI 操作不能假定处于主线程。源码：[ARouter 1.5.2 `_ARouter._navigation/runInMainThread`](https://github.com/alibaba/ARouter/blob/1.5.2/arouter-api/src/main/java/com/alibaba/android/arouter/launcher/_ARouter.java)。

### 5.4 路由表生成原理

ARouter 通过 APT（注解处理器）在编译时自动生成路由表：

```kotlin
// @Route 注解的类
@Route(path = "/user/login")
class LoginActivity : AppCompatActivity()

// APT 在编译时生成：
// ARouter$$Group$$user.java
public class ARouter$$Group$$user implements IRouteGroup {
    @Override
    public void loadInto(Map<String, Class<?>> atlas) {
        atlas.put("/user/login", LoginActivity.class);
    }
}
```

**流程：**
1. APT 扫描所有 `@Route` 注解的类
2. 按模块分组，生成 `ARouter$$Group$$<模块名>` 类
3. 运行时，ARouter 合并所有分组，构建完整路由表
4. `navigate()` 时查表获取目标 Class，通过反射/Intent 启动

---

## 6. 组件通信

### 6.1 页面跳转

**推荐：使用 ARouter 封装工具类**

```kotlin
// Router.kt 封装常用跳转
object Router {
    fun toLogin() = ARouter.getInstance().build("/user/login").navigation()

    fun toProfile(userId: String) =
        ARouter.getInstance().build("/user/profile")
            .withString("userId", userId)
            .navigation()

    fun toOrderDetail(orderId: String) =
        ARouter.getInstance().build("/order/detail")
            .withString("orderId", orderId)
            .navigation()

    fun toProductDetail(productId: String) =
        ARouter.getInstance().build("/product/detail")
            .withString("productId", productId)
            .navigation()
}

// 调用方
Router.toProfile("123")
Router.toOrderDetail("order_456")
```

### 6.2 数据传递

| 方式 | 适用场景 | 大小限制 |
|------|----------|----------|
| 基本类型（`withString`/`withInt`） | 简单参数 | ~1MB |
| Parcelable 对象 | 推荐，效率高 | ~1MB |
| Serializable 对象 | 兼容性好，效率低 | ~1MB |
| Bundle | 复杂参数组合 | ~1MB |

```kotlin
// 基本类型
ARouter.getInstance().build("/user/profile")
    .withString("name", "张三")
    .withInt("age", 25)
    .withBoolean("vip", true)
    .navigation()

// Parcelable（推荐）
@Parcelize
data class Product(val id: String, val name: String, val price: Double) : Parcelable

ARouter.getInstance().build("/product/detail")
    .withParcelable("product", product)
    .navigation()

// 接收方
@Route(path = "/product/detail")
class ProductDetailActivity : AppCompatActivity() {
    @Autowired
    lateinit var product: Product

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ARouter.getInstance().inject(this)
    }
}
```

### 6.3 服务调用

通过 ARouter 获取跨模块服务实例：

```kotlin
// 1. 定义服务接口 (lib-common)
interface IUserService : IProvider {
    fun isLogin(): Boolean
    fun getUserInfo(): UserInfo?
    fun login(context: Context)
}

// 2. 模块实现 (module-user)
@Route(path = "/user/service")
class UserServiceImpl : IUserService {
    override fun init(context: Context) {}
    override fun isLogin() = UserManager.isLogin()
    override fun getUserInfo() = UserManager.userInfo
    override fun login(context: Context) {
        context.startActivity(Intent(context, LoginActivity::class.java))
    }
}

// 3. 调用服务 (module-order)
class OrderPresenter {
    private val userService = ARouter.getInstance()
        .build("/user/service")
        .navigation() as IUserService

    fun createOrder() {
        if (!userService.isLogin()) {
            userService.login(context)
            return
        }
        // 创建订单...
    }
}
```

### 6.4 跨进程通信

当组件化进一步演进到多进程架构时，需要跨进程通信：

**方案对比：**

| 方案 | 适用场景 | 复杂度 | 性能 |
|------|----------|--------|------|
| AIDL | 跨进程服务调用 | 中 | 高 |
| Messenger | 简单串行通信 | 低 | 中 |
| ContentProvider | 共享数据 | 中 | 中 |
| Socket | 复杂自定义协议 | 高 | 中 |

**AIDL 示例：**

```kotlin
// IOrderService.aidl
interface IOrderService {
    List<Order> getOrders();
    void createOrder(in Order order);
}

// OrderService.kt（服务端）
@LocalStub  // 本地进程内使用
class OrderService : Service() {
    private val binder = object : IOrderService.Stub() {
        override fun getOrders(): List<Order> = orderRepository.getOrders()
        override fun createOrder(order: Order) {
            orderRepository.create(order)
        }
    }
    override fun onBind(intent: Intent) = binder
}

// 客户端绑定
val intent = Intent().apply {
    component = ComponentName("com.example.app", "com.example.app.service.OrderService")
}
bindService(intent, connection, Context.BIND_AUTO_CREATE)
```

---

## 7. 项目结构与 Gradle 配置

### 7.1 目录结构

```text
Project/
├── app/                          # 主工程（壳）
│   ├── src/main/
│   │   ├── java/com/example/app/
│   │   │   ├── App.kt            # Application
│   │   │   ├── MainActivity.kt   # 主界面
│   │   │   └── MainViewModel.kt
│   │   ├── AndroidManifest.xml
│   │   └── res/
│   └── build.gradle.kts
│
├── module-user/                  # 用户模块
│   ├── src/main/
│   │   ├── java/com/example/user/
│   │   │   ├── ui/
│   │   │   │   ├── LoginActivity.kt
│   │   │   │   └── ProfileActivity.kt
│   │   │   ├── service/
│   │   │   │   └── UserServiceImpl.kt
│   │   │   └── UserViewModel.kt
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
│
├── module-order/                 # 订单模块
│   └── ...
│
├── lib-common/                   # 公共接口/工具
│   ├── src/main/java/com/example/common/
│   │   ├── api/                  # 服务接口定义
│   │   │   ├── IUserService.kt
│   │   │   └── IOrderService.kt
│   │   ├── event/                # 事件定义
│   │   │   └── UserEvent.kt
│   │   ├── router/              # 路由常量
│   │   │   └── RouterPath.kt
│   │   └── util/                # 工具类
│   └── build.gradle.kts
│
├── lib-network/                  # 网络库
├── lib-image/                    # 图片库
│
└── build.gradle.kts              # 根构建配置
```

### 7.2 Gradle 配置

**推荐用独立调试宿主，而不是把 library 的 debug 变体误认为 APK。** `com.android.library` 不生成可安装应用，没有 `applicationId`；`namespace` 位于 `android` 层级，不在 `defaultConfig`。原来的 `plugins.withId` 只注册回调，并不会切换插件；`debugApplicationIdSuffix` 也不是标准 Android DSL。

```kotlin
// module-user/build.gradle.kts：始终是 library，AGP 9 使用内置 Kotlin。
plugins { id("com.android.library") }
android {
    namespace = "com.example.user"
    compileSdk = 37
    defaultConfig { minSdk = 24 }
}

// debug-user-app/build.gradle.kts：独立、仅用于开发的宿主 application。
// 插件版本由根工程提供；API 37 可参考 AGP 9.1.1/Gradle 9.3.1/JDK 17。
plugins { id("com.android.application") }
android {
    namespace = "com.example.user.debughost"
    compileSdk = 37
    defaultConfig {
        applicationId = "com.example.user.debughost"
        minSdk = 24
        targetSdk = 37
    }
}
dependencies { implementation(project(":module-user")) }
```

以上两段属于两个不同文件，不可合并成同一个脚本；`settings.gradle.kts` 需 include 两个模块。业务模块的接口应放入独立契约模块，不靠 `compileOnly(project(":module-user"))` 掩盖运行时耦合：

```kotlin
// module-order/build.gradle.kts
// 假设 :lib-user-api 是工程实际创建并 include 的接口模块。
dependencies {
    implementation(project(":lib-user-api"))
    implementation(project(":lib-network"))
}
// app 组装层负责打包接口的真实实现，例如 implementation(project(":module-user"))。
// 仅当接口类型出现在 library 的公共 API 中时，才需要 api(project(":lib-user-api"))。
```

`implementation` 隔离消费者的**编译**类路径，不阻止依赖进入最终运行时；`compileOnly` 不负责打包，也不保证实现运行时存在。

来源：[创建 Android library](https://developer.android.com/studio/projects/android-library)、[模块化模式](https://developer.android.com/topic/modularization/patterns)、[Gradle API/implementation](https://docs.gradle.org/9.3.1/userguide/java_library_plugin.html)、[AGP 9.1 支持矩阵](https://developer.android.com/build/releases/agp-9-1-0-release-notes)。

### 7.3 模块独立运行配置

启动入口放到调试宿主清单，不放业务 library 的 `src/main` 中，避免合并进正式应用；也不应靠 `tools:replace` 无条件覆盖宿主 Application。

```xml
<!-- debug-user-app/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:label="User Debug Host">
        <!-- DebugHostActivity 由调试宿主实现，组装业务页面与测试依赖。 -->
        <activity
            android:name=".DebugHostActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

启动器入口需要允许外部启动，显式设置 `android:exported="true"`；内部页面不要因此一律导出。带 intent-filter 的组件在 targetSdk 31+ 需要明确 exported，Android 17 仍需遵守。来源：[Android 12 exported 要求](https://developer.android.com/about/versions/12/behavior-changes-12#exported)、[Activity 清单](https://developer.android.com/guide/topics/manifest/activity-element)。

### 7.4 资源冲突管理

不同模块可能有同名资源（如 `strings.xml`、`colors.xml`）。解决方案：

1. **模块名前缀**：所有资源加模块前缀
   - `user_strings.xml` / `order_strings.xml`

2. **资源分包**：
   ```text
   module-user/src/main/res/
   ├── values/user_strings.xml
   └── drawable/user_icon.png
   ```

3. **禁止模块间资源共享**：公共资源必须放在 `lib-common` 中

---

## 8. 最佳实践

### 8.1 模块边界定义

- **宁拆勿合**：模块拆得太细可以合并，拆得太粗难以拆分
- **先粗后细**：初期按大业务域划分，后期根据需要再拆分
- **避免循环依赖**：A→B→C→A 是常见错误，用接口打破循环

### 8.2 API 设计原则

1. **接口要稳定**：公共 API 一旦发布，尽量保持兼容
2. **最小暴露**：只暴露必要的类和方法
3. **版本标记**：接口变更时加 `@Deprecated` 并提供迁移方案
4. **文档注释**：接口方法必须有清晰的 JavaDoc 说明

```kotlin
/**
 * 用户服务接口
 *
 * 所有模块通过此接口访问用户相关功能
 *
 * @see UserServiceImpl
 */
interface IUserService : IProvider {
    /**
     * 当前是否已登录
     * @return true 已登录，false 未登录
     */
    fun isLogin(): Boolean

    /**
     * 获取当前用户信息
     * @return UserInfo 若未登录返回 null
     */
    fun getUserInfo(): UserInfo?
}
```

### 8.3 版本管理

| 组件 | 版本策略 | 推荐工具 |
|------|----------|----------|
| 公共库 | 统一 `version.gradle` 管理 | Gradle version catalog |
| 组件 | 独立 `gradle.properties` | |
| 依赖 | 锁定主版本，按需升级 minor | Renovate / Dependabot |

```kotlin
// gradle/libs.versions.toml (version catalog)
[versions]
arouter = "1.5.2"
koin = "3.5.0"
okhttp = "4.12.0"

[libraries]
arouter-api = { group = "com.alibaba", name = "arouter-api", version.ref = "arouter" }
arouter-compiler = { group = "com.alibaba", name = "arouter-compiler", version.ref = "arouter" }
koin-android = { group = "io.insert-koin", name = "koin-android", version.ref = "koin" }
```

### 8.4 调试技巧

**1. 路由调试（ARouter）：**
```kotlin
// 调试版本开启日志
if (BuildConfig.DEBUG) {
    ARouter.openDebug()
    ARouter.openLog()
}

// 打印路由表
ARouter.printAllRouteInfo(activity)
```

**2. 模块独立调试：**
在 Android Studio 中，直接运行 `module-user` 会以独立 App 启动；运行 `app` 则集成所有模块。

**3. 依赖问题排查：**
```bash
# 查看依赖树
./gradlew :module-order:dependencies

# 排查依赖冲突
./gradlew :app:app:dependencies --configuration releaseRuntimeClasspath
```

---

## 9. 面试常见问题

### Q1：组件化原理？

**答：** 组件化的核心是**解耦**和**模块独立运行**。

- **编译期解耦**：模块间不直接引用，通过接口（依赖倒置）或路由进行通信
- **动态配置**：Gradle 中 `isDebug` 开关控制模块是作为 `application`（独立运行）还是 `library`（集成到 App）
- **路由框架**：ARouter 等框架维护 path→Activity 的映射表，实现跨模块页面跳转
- **APT 注解处理**：编译时扫描 `@Route` 等注解，自动生成路由表代码

### Q2：ARouter 路由表是如何生成的？

**答：** ARouter 通过 **APT（注解处理器）** 在编译时生成。

1. 编译时，APT 扫描所有被 `@Route(path="...")` 注解的类
2. 按模块分组，每个模块生成一个 `ARouter$$Group$$<模块名>.java` 文件
3. 每个生成类实现 `IRouteGroup` 接口，在 `loadInto()` 方法中注册 path→Class 映射
4. 运行时，ARouter 合并所有分组，构建完整路由表，导航时查表获取目标 Class

### Q3：模块间如何通信？

**答：** 组件化中有四种常见通信方式：

| 方式 | 原理 | 适用场景 |
|------|------|----------|
| **路由跳转** | 路由表 path 映射到 Activity Class | 页面跳转 |
| **服务调用** | 接口 + 实现类注册到 ServiceLoader/ARouter | 获取数据、调用业务方法 |
| **事件总线** | 发布-订阅模式传递事件 | 状态同步（如登录事件） |
| **界面回调** | `startActivityForResult` / ARouter 带回调导航 | 需要返回结果的跳转 |

**实际项目中**，页面跳转用 ARouter，服务调用用 ARouter 服务发现，登录状态同步用 LiveData 事件总线。

### Q4：组件化和插件化的区别？

| 对比 | 组件化 | 插件化 |
|------|--------|--------|
| 编译产物 | 全部打进 APK | 插件独立 .apk 或 .so |
| 动态更新 | ❌ | ✅ 可动态加载/更新插件 |
| 复杂度 | 中 | 高 |
| 兼容性 | 好 | 差（需兼容各类 Hook） |
| 典型框架 | ARouter（路由） | Shadow、RePlugin |
| 核心原理 | 模块拆分 + Gradle 配置 | ClassLoader 动态加载 + Hook |

**结论**：组件化解决的是代码架构问题（拆分解耦），插件化解决的是动态发布问题。可以理解为：插件化 = 组件化 + 动态加载能力。

### Q5：组件化有哪些问题/挑战？

| 问题 | 解决方案 |
|------|----------|
| **资源冲突** | 模块加资源前缀，或在 lib-common 统一管理 |
| **路由表维护** | 统一路由路径常量（如 RouterPath object） |
| **版本同步** | 使用 Gradle version catalog 统一管理依赖版本 |
| **全量编译** | 组件化本身解决；进一步用 AGP 缓存 / Gradle 并行编译 |
| **初始化顺序** | 抽象为 `IModuleInit` 接口，按拓扑排序初始化 |

---

## 10. 业界实践：百度App组件化之路

> 以下内容整理自百度App技术团队《百度App组件化之路》，原文链接：https://juejin.cn/post/6844904061804740622
> 虽从iOS平台出发，但方法论与实现路径适用于大部分平台。

### 10.1 大型App复杂度来源

百度App是一个典型的大型App案例，其复杂度来源具有代表性：

| 复杂度来源 | 具体表现 | 目标 |
|-----------|---------|------|
| **业务规模大** | 技术方向70+，单端代码量180w+ | 隔离组件间影响，避免故障蔓延 |
| **团队规模大** | 数百人有代码权限 | 保障高效并行开发 |
| **接入业务多** | 30+ 内部接入业务 | 保障快速接入与基础能力复用 |
| **迭代速度快** | 3周一个版本（2周开发+1周测试） | 避免高速迭代下组件化劣化 |
| **技术形态多** | H5、NA、Hybrid、Talos、Flutter并存 | 保障基础能力复用 |

### 10.2 组件化演进历程

百度App组件化经历了四个阶段：

#### 阶段一：2013年 — 初始态（钻木取火）

> 所有业务在一个工程里开发，各业务和基础逻辑交错，没有边界

**问题：**
- 基础库甚至开源库都有业务侵入，入侵成本极低
- 首屏各业务间没有容器隔离，牵一发而动全身
- 共用服务（远程配置、端能力）没有组件化，`if else/switch case` 无限蔓延
- 逻辑、资源、数据没有合理归属，基础组件对外输出困难

#### 阶段二：2014-2015年 — 蒸汽机时代

**做了什么：**
- 拆出三方库，粗粒度拆出基础库，归到业务组件下层
- 引入框架容器，对首屏各业务进行隔离
- 新兴业务组件采用组件化模式开发，明确外部依赖
- 制定依赖规范，禁止层级反向依赖（但仅有规范，没有工具链强制支撑）
- 组件依赖通过 Adapter 注入

**遗留问题：**
- 组件归属模糊，部分组件游离在基础库和业务组件之间
- Adapter 一对一解耦效率不高
- 主App中遗留端能力接口与插件系统SDK并存

#### 阶段三：2016-2017年 — 电力时代

**重点建设：**
- 组件化框架（Pyramid、SchemeRouter）
- 分发框架（RemoteConfig、PMS、预取分发）
- 数据拆分框架（CocoaSetting）

#### 阶段四：2018-2019年 — 理想态（核能时代）

**达到的状态：**
- 各组件做到逻辑、资源、数据各有归属
- 主工程进一步弱化
- 层级更加明确，游离于基础库和业务组件之间的通用服务有了归属
- 组件可自下而上对外输出
- 整个App通过中央仓库组件列表经 EasyBox 组装
- 框架容器加载及系统事件分发统一到轻量级 AppLauncher

### 10.3 组件化实现路径

百度App总结了**自下而上的七步组件化建设路径**：

#### 第一步：编译隔离、架构分层及层级访问限制

```text
┌─────────────────────────────────────────────────────────┐
│                    编译隔离机制                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  · 通过构建系统（EasyBox）明确每个组件的对外接口         │
│  · 明确组件的外部依赖                                    │
│  · 下层组件不可以访问上层组件（反向访问限制）             │
│  · 同层组件间也不能无限制调用                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 第二步：三方库规范化与基础库体系化

**基础库问题：**
- 没有防修改机制，业务侵入成本低
- 交叉依赖问题：同一基础依赖的逻辑归属到同一组件

**解决方案：** 基础库二进制化，实行组件负责人制度，体系化建设

**三方库问题：**
- 没有防修改机制，业务侵入成本低
- Github PR响应不及时

三方库先固定版本，再评估 API/ABI、minSdk、注解处理器、R8 与许可证变化。维护差异采用可追踪的源码补丁或内部发布构件；运行时修改库行为会扩大排错与平台升级成本，不作为常规依赖管理方式。

来源：[Gradle 依赖锁定](https://docs.gradle.org/9.3.1/userguide/dependency_locking.html)、[Android 17 target 行为变化](https://developer.android.com/about/versions/17/behavior-changes-17)。例如反射 `MessageQueue` 私有结构的诊断/插桩组件需要单独排查，升级路由 API 本身不能证明它们已兼容。

#### 第三步：运行时分发与隔离服务

百度自研了 **Pyramid 组件化框架**，核心能力：

| 能力 | 说明 |
|------|------|
| **系统事件分发** | Pyramid 将系统事件分发给各子组件 |
| **组件间通信** | 从 Adapter 一对一解耦升级为一对多解耦 |
| **强依赖转弱依赖** | 技术组件对外输出时，被依赖组件具有可替代性 |

**四大分发服务：**
- **端能力**：SchemeRouter 归属服务层框架，SchemeHandler 归属各组件
- **配置分发**：集中解析改造为分发机制，升级为云控服务
- **数据拆分**：配合配置分发，数据拆分到各组件内部管理
- **资源/预取分发**：建立资源/预取分发服务

#### 第四步：服务层建立

将多业务调用的低依赖组件去业务化，抽象成通用服务：

> 账号服务、分享服务、云控服务、统计服务、性能服务、AI服务

#### 第五步：建立组件模型

**组件模型的定义：** 每个组件是一个独立的功能单元：

- **功能单元**：明确功能范围
- **逻辑单元**：逻辑归属清晰
- **数据及资源管理单元**：数据、资源各有归属
- **H5通信单元**：H5与Native通信接口
- **性能量化单元**：可独立做性能优化
- **编译输出单元**：1个或多个二进制产物

#### 第六步：业务组件化

按照组件模型，确定业务的功能范围、逻辑与接口边界，快速组件化。

#### 第七步：劣化控制

> **没有防劣化机制，填坑速度永远比不上挖坑速度。**

- 组件接口变更记录通知
- 依赖变更记录通知
- Warning数变化监控
- 在 Tekes 平台统一管理

### 10.4 组件化收益

百度App组件化的实际收益：

| 维度 | 收益 |
|------|------|
| **复杂度控制** | 复杂度控制在组件内部，对外"简单可依赖" |
| **并行开发** | 远程配置新增从4+小时降至0.5小时，提升8倍+ |
| **复用** | 百度App矩阵产品复用率50%以上 |
| **编译速度** | 平均从15分钟/次优化到2分钟/次 |
| **质量** | 单组件故障影响范围内敛到组件内部，不会引发整体crash |
| **可量化** | 为启动速度、体积等提供量化单位 |

### 10.5 核心原则

引用《每个架构师都应该研究下康威定律》中的观点：

> 架构的目标是用于管理复杂性、易变性和不确定性，以确保在长期的系统演化过程中，一部分架构的变化不会对架构的其它部分产生不必要的负面影响。
>
> 这样可以确保业务和研发效率的敏捷，让应用的易变部分能够频繁地变化，对应用的其它部分的影响尽可能的小。

---

## 参考资料

| 资源 | 链接 |
|------|------|
| ARouter GitHub | https://github.com/alibaba/ARouter |
| Android 组件化文档 | https://developer.android.com/topic/modularization |
| AOSP 源码 | https://cs.android.com/ |
| 《Android 进阶解密》 | 架构设计参考 |

---

*本文档由 OpenClaw 整理，持续更新*

## 11. 可替换的组件契约与装配

### 11.1 API 模块不暴露实现类型

接口模块表达业务能力，不返回实现库的 Retrofit Response、数据库 Entity 或 Activity。下面是可独立编译的 API：

```kotlin
// :feature:profile-api，纯 Kotlin 类型。
package example.profile.api

data class Profile(val id: String, val displayName: String)
sealed interface ProfileResult {
    data class Found(val profile: Profile) : ProfileResult
    data object NotFound : ProfileResult
    data object Unavailable : ProfileResult
}
interface ProfileService { suspend fun find(id: String): ProfileResult }
```

`:feature:profile-impl` 依赖 api 并实现它；消费方依赖 api；宿主 app 同时依赖实现模块，在启动时完成装配。实现构造器也用接口接收网络/存储依赖，错误在实现层映射为契约类型；协程取消继续传播，不转换为 Unavailable。

```kotlin
// :feature:profile-impl 中的独立示例。
class MemoryProfileService : example.profile.api.ProfileService {
    private val profiles = mapOf("1" to example.profile.api.Profile("1", "Alice"))
    override suspend fun find(id: String): example.profile.api.ProfileResult {
        require(id.isNotBlank())
        return profiles[id]?.let { example.profile.api.ProfileResult.Found(it) }
            ?: example.profile.api.ProfileResult.NotFound
    }
}
// :app 装配点；不持有 Activity。
class AppServices {
    val profiles: example.profile.api.ProfileService = MemoryProfileService()
}
```

### 11.2 api 与 implementation 的传播

```kotlin
// profile-impl/build.gradle.kts：公开类签名实现 ProfileService，向消费者暴露该类型。
dependencies {
    api(project(":feature:profile-api"))
    // 网络、数据库等实现依赖使用 implementation。
}
// 消费方 feature 模块：
// implementation(project(":feature:profile-api"))
// app 装配层：
// implementation(project(":feature:profile-impl"))
```

`implementation` 隐藏消费者的编译类路径，不是运行时剔除。单独发布 AAR 时还需发布模块元数据/POM 才能传递外部依赖；直接复制一个 AAR 不会自动带齐其全部三方库。

### 11.3 不依赖私有路由 API 的页面跳转

在 app 装配层将业务导航意图转成显式 Intent。目标组件未注册、安装形态不包含目标模块或参数无效都需要失败分支；授权、登录等是业务进入条件，不只是字符串路径匹配。

```kotlin
sealed interface OpenProfileResult {
    data object Opened : OpenProfileResult
    data object InvalidId : OpenProfileResult
    data object Unavailable : OpenProfileResult
}
// 由 app 将 destination 指向实际详情 Activity；示例不约定 ARouter 内部接口。
fun openProfile(
    context: android.content.Context,
    destination: Class<out android.app.Activity>,
    id: String
): OpenProfileResult {
    if (id.isBlank()) return OpenProfileResult.InvalidId
    val intent = android.content.Intent(context, destination).putExtra("profileId", id)
    if (context !is android.app.Activity) intent.addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
    return try {
        context.startActivity(intent)
        OpenProfileResult.Opened
    } catch (missing: android.content.ActivityNotFoundException) {
        OpenProfileResult.Unavailable
    } catch (denied: SecurityException) {
        OpenProfileResult.Unavailable
    }
}
```

Activity 在清单中注册；仅供应用内使用的入口设置 `exported=false`，外部深链入口对参数、登录态和权限独立校验。动态特性模块应先完成安装再路由，不能把“类在源码中存在”当作运行时已安装。

### 11.4 独立调试与启动顺序

优先为 feature 建立小型 demo app，保持 feature 始终为 Android library，避免同一目录频繁切换 application/library DSL。demo 和正式 app 使用同一契约，仅替换装配实现。初始化图按依赖拓扑执行；允许延迟的服务按需创建，不能让所有模块都在 Application.onCreate 同步读盘和联网。

### 11.5 Android 17 的组件边界

运行时权限由可见宿主 UI 申请，业务模块通过结果回调或状态流接收授权结果。targetSdk 37 的本地网络访问权限、后台启动规则和 native 页大小要求影响最终应用，不能在每个 library 的清单里盲目添加权限。组件测试至少覆盖未装配服务、无效路由、取消请求、Activity 重建与 release/R8 路由表保留。

参考：[模块化模式](https://developer.android.com/topic/modularization/patterns)、[Android library 发布依赖](https://developer.android.com/studio/projects/android-library)、[Gradle 9.3.1 API 分离](https://docs.gradle.org/9.3.1/userguide/java_library_plugin.html)、[Android 17 行为变化](https://developer.android.com/about/versions/17/behavior-changes-17)。
