# Android 组件化详解

> 作者：OpenClaw | 日期：2026-03-11  
> 组件化架构完全指南 | 模块解耦、路由、通信

---

## 📚 目录

### 第一篇：组件化基础

**第 1 章 组件化概述**
- 1.1 [什么是组件化](#11-什么是组件化)
- 1.2 [组件化 vs 单工程](#12-组件化-vs-单工程)
- 1.3 [组件化优势](#13-组件化优势)
- 1.4 [组件化分层](#14-组件化分层)

**第 2 章 组件化架构设计**
- 2.1 [架构层次](#21-架构层次)
- 2.2 [模块划分原则](#22-模块划分原则)
- 2.3 [依赖关系](#23-依赖关系)
- 2.4 [公共组件设计](#24-公共组件设计)

**第 3 章 模块解耦**
- 3.1 [接口解耦](#31-接口解耦)
- 3.2 [依赖注入](#32-依赖注入)
- 3.3 [事件总线](#33-事件总线)
- 3.4 [服务发现](#34-服务发现)

**第 4 章 路由框架**
- 4.1 [路由原理](#41-路由原理)
- 4.2 [ARouter 使用](#42-arouter-使用)
- 4.3 [路由表生成](#43-路由表生成)
- 4.4 [拦截器机制](#44-拦截器机制)

**第 5 章 组件通信**
- 5.1 [页面跳转](#51-页面跳转)
- 5.2 [数据传递](#52-数据传递)
- 5.3 [服务调用](#53-服务调用)
- 5.4 [跨进程通信](#54-跨进程通信)

---

### 第二篇：组件化实现

**第 6 章 组件化项目结构**
- 6.1 [工程目录结构](#61-工程目录结构)
- 6.2 [Gradle 配置](#62-gradle-配置)
- 6.3 [模块独立运行](#63-模块独立运行)
- 6.4 [资源管理](#64-资源管理)

**第 7 章 公共组件封装**
- 7.1 [网络组件](#71-网络组件)
- 7.2 [图片加载组件](#72-图片加载组件)
- 7.3 [UI 组件库](#73-ui-组件库)
- 7.4 [工具类库](#74-工具类库)

**第 8 章 组件化最佳实践**
- 8.1 [模块边界定义](#81-模块边界定义)
- 8.2 [API 设计原则](#82-api-设计原则)
- 8.3 [版本管理](#83-版本管理)
- 8.4 [调试技巧](#84-调试技巧)

**第 18 章 面试常见问题**
- 18.1 [组件化原理](#181-组件化原理)
- 18.2 [路由实现](#182-路由实现)
- 18.3 [模块通信](#183-模块通信)
- 18.4 [与插件化对比](#184-与插件化对比)
- 18.5 [最佳实践](#185-最佳实践)

---

## 第一篇：组件化基础

---

## 第 1 章 组件化概述

### 1.1 什么是组件化

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       组件化架构                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              主工程 (App)                                    │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          Application Layer                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │   首页模块   │  │   用户模块   │  │   商品模块   │  │   订单模块   │  │  │
│  │  │  (Module)   │  │  (Module)   │  │  (Module)   │  │  (Module)   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                           Common Layer                                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │   网络      │  │   图片      │  │   路由      │  │   工具      │  │  │
│  │  │  (Library)  │  │  (Library)  │  │  (Library)  │  │  (Library)  │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘

核心特点：
1. 业务模块化：按业务拆分为独立 Module
2. 编译时解耦：模块间通过接口/路由通信
3. 统一打包：所有模块编译到同一个 APK
4. 可独立运行：模块可配置为独立 App
```

### 1.2 组件化 vs 单工程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    单工程 vs 组件化                                         │
└─────────────────────────────────────────────────────────────────────────────┘

单工程架构：
┌─────────────────────────────────────────────────────────────────────────────┐
│  App                                                                        │
│  ├── MainActivity.java                                                      │
│  ├── UserActivity.java                                                      │
│  ├── OrderActivity.java                                                     │
│  ├── ProductActivity.java                                                   │
│  ├── HttpUtil.java                                                          │
│  ├── ImageLoader.java                                                       │
│  └── ...                                                                    │
│                                                                             │
│  问题：                                                                      │
│  1. 代码耦合严重                                                             │
│  2. 编译速度慢                                                               │
│  3. 难以维护                                                                 │
│  4. 无法复用                                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

组件化架构：
┌─────────────────────────────────────────────────────────────────────────────┐
│  Project                                                                    │
│  ├── app/                    # 主工程                                       │
│  ├── module-user/            # 用户模块                                     │
│  ├── module-order/           # 订单模块                                     │
│  ├── module-product/         # 商品模块                                     │
│  ├── lib-common/             # 公共库                                       │
│  ├── lib-network/            # 网络库                                       │
│  └── lib-router/             # 路由库                                       │
│                                                                             │
│  优势：                                                                      │
│  1. 模块解耦                                                                 │
│  2. 并行开发                                                                 │
│  3. 编译加速                                                                 │
│  4. 代码复用                                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 组件化优势

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       组件化优势                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────────────────┐
│      优势        │                       说明                              │
├──────────────────┼──────────────────────────────────────────────────────────┤
│  解耦            │  模块间通过接口通信，降低耦合度                          │
│  并行开发        │  不同团队可独立开发不同模块                              │
│  编译加速        │  增量编译，只编译修改的模块                              │
│  代码复用        │  公共组件可被多个模块复用                                │
│  易于测试        │  模块可独立测试                                          │
│  易于维护        │  问题定位快，修改影响范围小                              │
│  灵活部署        │  模块可独立运行、调试                                    │
│  职责清晰        │  模块边界明确，职责单一                                  │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

### 1.4 组件化分层

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       组件化分层架构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          App 壳工程                                         │
│  - 集成所有模块                                                             │
│  - Application 初始化                                                       │
│  - 主界面容器                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          业务模块层                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   首页模块   │  │   用户模块   │  │   商品模块   │  │   订单模块   │        │
│  │             │  │             │  │             │  │             │        │
│  │ - 首页      │  │ - 登录注册  │  │ - 商品列表  │  │ - 订单列表  │        │
│  │ - 分类      │  │ - 个人中心  │  │ - 商品详情  │  │ - 订单详情  │        │
│  │ - 推荐      │  │ - 设置      │  │ - 搜索      │  │ - 支付      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          公共业务层                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   路由      │  │   登录SDK   │  │   支付SDK   │  │   分享SDK   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          基础组件层                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   网络      │  │   图片      │  │   数据库    │  │   工具类    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 第 2 章 组件化架构设计

### 2.1 架构层次

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       组件化架构层次                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 1: App Shell (应用壳)                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│  职责：集成模块、初始化、主界面                                              │
│  依赖：所有业务模块 + 公共层                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 2: Business Modules (业务模块)                                       │
│  ─────────────────────────────────────────────────────────────────────────  │
│  职责：具体业务功能                                                         │
│  依赖：公共业务层 + 基础组件层                                              │
│  通信：通过路由/接口                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 3: Common Business (公共业务)                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  职责：跨模块业务逻辑                                                       │
│  依赖：基础组件层                                                           │
│  包含：路由、登录SDK、支付SDK                                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│  Layer 4: Base Components (基础组件)                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│  职责：通用功能封装                                                         │
│  依赖：无                                                                   │
│  包含：网络、图片、数据库、工具类                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块划分原则

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       模块划分原则                                          │
└─────────────────────────────────────────────────────────────────────────────┘

1. 单一职责原则（SRP）
   ─────────────────────────────────────────────────────────────────────────
   每个模块只负责一个业务领域
   ✅ module-user：用户相关
   ✅ module-order：订单相关
   ❌ module-business：所有业务（职责不清）

2. 高内聚低耦合
   ─────────────────────────────────────────────────────────────────────────
   模块内部高度相关，模块间依赖最小化
   ✅ 模块间通过接口/路由通信
   ❌ 模块间直接调用实现类

3. 依赖倒置原则（DIP）
   ─────────────────────────────────────────────────────────────────────────
   高层模块依赖低层模块的抽象，而非具体实现
   ✅ 依赖接口 ILoginService
   ❌ 依赖实现类 LoginServiceImpl

4. 接口隔离原则（ISP）
   ─────────────────────────────────────────────────────────────────────────
   接口要小而专一，不要大而全
   ✅ IUserService、IOrderService 分离
   ❌ IService 包含所有功能

5. 按业务领域划分
   ─────────────────────────────────────────────────────────────────────────
   电商项目：首页、商品、购物车、订单、用户、支付
   社交项目：首页、消息、动态、用户、设置
```

### 2.3 依赖关系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       模块依赖关系                                          │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │     App     │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  module-user  │  │ module-order  │  │module-product │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │lib-common   │
                    │lib-router   │
                    │lib-network  │
                    └─────────────┘

规则：
1. App 依赖所有业务模块
2. 业务模块之间不能相互依赖
3. 业务模块依赖公共层
4. 公共层之间可以相互依赖
5. 依赖方向：从上到下，不能反向
```

### 2.4 公共组件设计

```kotlin
/**
 * 公共组件设计示例
 */

// 1. 网络组件 (lib-network)
object NetworkClient {
    private val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(LoggingInterceptor())
            .addInterceptor(AuthInterceptor())
            .build()
    }
    
    val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}

// 2. 图片加载组件 (lib-image)
object ImageLoader {
    fun load(imageView: ImageView, url: String?) {
        Glide.with(imageView.context)
            .load(url)
            .into(imageView)
    }
}

// 3. 路由组件 (lib-router)
object Router {
    fun navigate(context: Context, path: String) {
        ARouter.getInstance().build(path).navigation(context)
    }
}

// 4. 工具类组件 (lib-utils)
object SPUtils {
    fun put(key: String, value: Any) {
        // SharedPreferences 封装
    }
    
    fun <T> get(key: String, defaultValue: T): T {
        // ...
    }
}
```

---

## 第 3 章 模块解耦

### 3.1 接口解耦

```kotlin
/**
 * 接口解耦方案
 */

// 1. 定义公共接口 (lib-common)
interface IUserService {
    fun isLogin(): Boolean
    fun getUserInfo(): UserInfo?
    fun login(context: Context)
    fun logout()
}

// 2. 用户模块实现接口 (module-user)
class UserServiceImpl : IUserService {
    override fun isLogin(): Boolean {
        return UserManager.isLogin()
    }
    
    override fun getUserInfo(): UserInfo? {
        return UserManager.userInfo
    }
    
    override fun login(context: Context) {
        context.startActivity(Intent(context, LoginActivity::class.java))
    }
    
    override fun logout() {
        UserManager.logout()
    }
}

// 3. 服务注册 (App 启动时)
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // 注册服务实现
        ServiceLocator.register(IUserService::class.java, UserServiceImpl())
    }
}

// 4. 其他模块使用 (module-order)
class OrderViewModel : ViewModel() {
    private val userService: IUserService = ServiceLocator.get(IUserService::class.java)
    
    fun createOrder() {
        if (!userService.isLogin()) {
            userService.login(context)
            return
        }
        // 创建订单
    }
}
```

### 3.2 依赖注入

```kotlin
/**
 * 依赖注入方案（Koin）
 */

// 1. 添加依赖
// implementation "io.insert-koin:koin-android:3.5.0"

// 2. 定义 Module
val userModule = module {
    single<IUserService> { UserServiceImpl() }
    single<UserRepository> { UserRepositoryImpl(get()) }
    viewModel { UserViewModel(get()) }
}

val orderModule = module {
    single<IOrderService> { OrderServiceImpl() }
    viewModel { OrderViewModel(get(), get()) }  // get() 自动注入依赖
}

// 3. 初始化 Koin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        
        startKoin {
            androidContext(this@MyApp)
            modules(listOf(userModule, orderModule, commonModule))
        }
    }
}

// 4. 使用依赖注入
class OrderActivity : AppCompatActivity() {
    // 注入 ViewModel
    private val viewModel: OrderViewModel by viewModel()
    
    // 注入服务
    private val userService: IUserService by inject()
}
```

### 3.3 事件总线

```kotlin
/**
 * 事件总线方案
 */

// 1. 定义事件
data class LoginEvent(val user: UserInfo)
data class LogoutEvent(val reason: String)

// 2. 使用 LiveData + ViewModel（推荐）
object EventBus {
    private val events = mutableMapOf<Class<*>, MutableLiveData<*>>()
    
    @Suppress("UNCHECKED_CAST")
    fun <T> getEvent(eventClass: Class<T>): MutableLiveData<T> {
        return events.getOrPut(eventClass) { MutableLiveData<T>() } as MutableLiveData<T>
    }
    
    fun <T> post(event: T) {
        getEvent(event!!::class.java).postValue(event)
    }
}

// 3. 发送事件（module-user）
fun onLoginSuccess(user: UserInfo) {
    EventBus.post(LoginEvent(user))
}

// 4. 接收事件（module-order）
class OrderActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        EventBus.getEvent(LoginEvent::class.java).observe(this) {
            // 登录成功，刷新订单
            refreshOrders()
        }
    }
}
```

### 3.4 服务发现

```kotlin
/**
 * 服务发现模式
 */

// 1. 服务定位器
object ServiceLocator {
    private val services = mutableMapOf<Class<*>, Any>()
    
    fun <T> register(clazz: Class<T>, impl: T) {
        services[clazz] = impl as Any
    }
    
    @Suppress("UNCHECKED_CAST")
    fun <T> get(clazz: Class<T>): T {
        return services[clazz] as? T 
            ?: throw IllegalStateException("Service ${clazz.name} not registered")
    }
    
    fun <T> getOrNull(clazz: Class<T>): T? {
        return services[clazz] as? T
    }
}

// 2. 使用示例
// 注册
ServiceLocator.register(IUserService::class.java, UserServiceImpl())
ServiceLocator.register(IOrderService::class.java, OrderServiceImpl())

// 获取
val userService = ServiceLocator.get(IUserService::class.java)
val isLogin = userService.isLogin()
```

---

## 第 4 章 路由框架

### 4.1 路由原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       路由框架原理                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   页面跳转   │───▶│   路由中心   │───▶│  查找路由表  │───▶│  执行跳转   │
│              │    │              │    │              │    │              │
│Router.navigate│   │              │    │ /user/login  │    │ Intent启动  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘

核心组件：
1. 路由表：path -> Class 映射
2. 路由注解：标记可路由的页面
3. 路由拦截器：登录校验等
4. 参数解析：自动解析路由参数

编译时：
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  @Route 注解 │───▶│  APT 处理   │───▶│  生成路由表  │
│              │    │              │    │              │
│ @Route("/login")│  │ 注解处理器   │    │ Java 类      │
└──────────────┘    └──────────────┘    └──────────────┘

运行时：
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  路由跳转    │───▶│  查找路由表  │───▶│  创建 Intent │
│              │    │              │    │              │
│ /user/login │    │ path->class  │    │ startActivity│
└──────────────┘    └──────────────┘    └──────────────┘
```

### 4.2 ARouter 使用

```kotlin
/**
 * ARouter 使用示例
 */

// 1. 添加依赖
// build.gradle
plugins {
    id("com.alibaba.arouter") version "1.0.0"
}

dependencies {
    implementation("com.alibaba:arouter-api:1.5.2")
    kapt("com.alibaba:arouter-compiler:1.5.2")
}

android {
    defaultConfig {
        javaCompileOptions {
            annotationProcessorOptions {
                arguments["AROUTER_MODULE_NAME"] = project.name
            }
        }
    }
}

// 2. 初始化
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        ARouter.init(this)
    }
}

// 3. 定义路由
@Route(path = "/user/login")
class LoginActivity : AppCompatActivity()

@Route(path = "/user/profile")
class ProfileActivity : AppCompatActivity() {
    // 自动注入参数
    @Autowired
    @JvmField var userId: String? = null
    
    @Autowired(name = "from")
    @JvmField var fromPage: String? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ARouter.getInstance().inject(this)  // 注入参数
    }
}

// 4. 页面跳转
// 简单跳转
ARouter.getInstance()
    .build("/user/login")
    .navigation()

// 带参数跳转
ARouter.getInstance()
    .build("/user/profile")
    .withString("userId", "123")
    .withString("from", "home")
    .navigation()

// 获取 Fragment
val fragment = ARouter.getInstance()
    .build("/user/info_fragment")
    .navigation() as Fragment

// 带结果回调
ARouter.getInstance()
    .build("/user/select")
    .navigation(this, object : NavigationCallback {
        override fun onFound(postcard: Postcard) {}
        override fun onLost(postcard: Postcard) {}
        override fun onArrival(postcard: Postcard) {}
        override fun onInterrupt(postcard: Postcard) {}
    })
```

### 4.3 路由表生成

```kotlin
/**
 * 路由表生成原理
 */

// 1. 定义注解
@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.BINARY)
annotation class Route(val path: String, val group: String = "")

// 2. APT 处理器
class RouteProcessor : AbstractProcessor() {
    
    override fun process(annotations: Set<TypeElement>, roundEnv: RoundEnvironment): Boolean {
        // 收集所有 @Route 注解
        val routes = roundEnv.getElementsAnnotatedWith(Route::class.java)
        
        // 生成路由表类
        val builder = TypeSpec.classBuilder("ARouter$$Group$$${moduleName}")
            .addSuperinterface(IRouteGroup::class)
        
        val methodBuilder = FunSpec.builder("loadInto")
            .addParameter("atlas", Map::class)
        
        routes.forEach { element ->
            val route = element.getAnnotation(Route::class.java)
            methodBuilder.addStatement(
                "atlas.put(\"${route.path}\", ${element.simpleName}::class.java)"
            )
        }
        
        builder.addFunction(methodBuilder.build())
        
        // 写入 Java 文件
        JavaFile.builder("com.alibaba.android.arouter.routes", builder.build())
            .build()
            .writeTo(processingEnv.filer)
        
        return true
    }
}

// 3. 生成的路由表类
// ARouter$$Group$$user.java
public class ARouter$$Group$$user implements IRouteGroup {
    @Override
    public void loadInto(Map<String, Class<?>> atlas) {
        atlas.put("/user/login", LoginActivity.class);
        atlas.put("/user/profile", ProfileActivity.class);
    }
}
```

### 4.4 拦截器机制

```kotlin
/**
 * 拦截器使用
 */

// 1. 定义拦截器
@Interceptor(priority = 8, name = "登录拦截器")
class LoginInterceptor : IInterceptor {
    override fun process(postcard: Postcard, callback: InterceptorCallback) {
        // 需要登录的页面
        if (postcard.extra and RouteExtraFlag.NEED_LOGIN != 0) {
            if (!UserManager.isLogin()) {
                // 未登录，中断跳转
                callback.onInterrupt(null)
                // 跳转登录页
                ARouter.getInstance()
                    .build("/user/login")
                    .navigation()
                return
            }
        }
        // 继续跳转
        callback.onContinue(postcard)
    }
    
    override fun init(context: Context) {}
}

// 2. 标记需要登录的页面
@Route(path = "/order/list", extras = RouteExtraFlag.NEED_LOGIN)
class OrderListActivity : AppCompatActivity()

// 3. 定义标记常量
object RouteExtraFlag {
    const val NEED_LOGIN = 1
    const val NEED_VIP = 2
}

// 4. 多个拦截器按优先级执行
@Interceptor(priority = 1)  // 先执行
class AuthInterceptor : IInterceptor { ... }

@Interceptor(priority = 8)  // 后执行
class LoginInterceptor : IInterceptor { ... }
```

---

## 第 5 章 组件通信

### 5.1 页面跳转

```kotlin
/**
 * 页面跳转方式
 */

// 1. 使用 ARouter 跳转
ARouter.getInstance()
    .build("/user/profile")
    .withString("userId", "123")
    .withInt("age", 25)
    .withParcelable("user", user)
    .withTransition(R.anim.enter, R.anim.exit)
    .navigation()

// 2. 封装路由工具类
object Router {
    fun toLogin() {
        ARouter.getInstance().build("/user/login").navigation()
    }
    
    fun toProfile(userId: String) {
        ARouter.getInstance()
            .build("/user/profile")
            .withString("userId", userId)
            .navigation()
    }
    
    fun toOrderDetail(orderId: String) {
        ARouter.getInstance()
            .build("/order/detail")
            .withString("orderId", orderId)
            .navigation()
    }
}

// 3. 使用
Router.toProfile("123")
```

### 5.2 数据传递

```kotlin
/**
 * 数据传递方式
 */

// 1. 基本类型
ARouter.getInstance()
    .build("/user/profile")
    .withString("name", "张三")
    .withInt("age", 25)
    .withBoolean("vip", true)
    .navigation()

// 2. Parcelable 对象
@Parcelize
data class User(val id: String, val name: String) : Parcelable

ARouter.getInstance()
    .build("/user/detail")
    .withParcelable("user", user)
    .navigation()

// 3. 序列化对象
ARouter.getInstance()
    .build("/order/detail")
    .withSerializable("order", order)
    .navigation()

// 4. Bundle
val bundle = Bundle().apply {
    putString("userId", "123")
    putInt("type", 1)
}
ARouter.getInstance()
    .build("/user/profile")
    .with(bundle)
    .navigation()

// 5. 接收参数
@Route(path = "/user/profile")
class ProfileActivity : AppCompatActivity() {
    @Autowired
    @JvmField var userId: String? = null
    
    @Autowired
    @JvmField var type: Int = 0
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ARouter.getInstance().inject(this)
        // 使用参数
    }
}
```

### 5.3 服务调用

```kotlin
/**
 * 跨模块服务调用
 */

// 1. 定义服务接口 (lib-common)
interface IUserService : IProvider {
    fun isLogin(): Boolean
    fun getUserInfo(): UserInfo?
    fun login(context: Context)
}

// 2. 实现服务 (module-user)
@Route(path = "/user/service")
class UserServiceImpl : IUserService {
    override fun init(context: Context) {}
    
    override fun isLogin(): Boolean = UserManager.isLogin()
    
    override fun getUserInfo(): UserInfo? = UserManager.userInfo
    
    override fun login(context: Context) {
        context.startActivity(Intent(context, LoginActivity::class.java))
    }
}

// 3. 调用服务 (module-order)
// 方式1：通过路径获取
val userService = ARouter.getInstance()
    .build("/user/service")
    .navigation() as IUserService

// 方式2：通过类获取
val userService = ARouter.getInstance()
    .navigation(IUserService::class.java)

// 使用服务
if (!userService.isLogin()) {
    userService.login(this)
}

// 4. 单例服务
@Route(path = "/common/config", name = "配置服务")
class ConfigService : IProvider {
    override fun init(context: Context) {}
    
    fun getConfig(): Config { ... }
}

// 获取单例
val config = (ARouter.getInstance()
    .build("/common/config")
    .navigation() as ConfigService)
    .getConfig()
```

### 5.4 跨进程通信

```kotlin
/**
 * 跨进程通信方案
 */

// 1. AIDL（推荐）
// IOrderService.aidl
interface IOrderService {
    List<Order> getOrders();
    void createOrder(in Order order);
}

// 2. Messenger
class OrderService : Service() {
    private val messenger = Messenger(Handler { msg ->
        when (msg.what) {
            MSG_GET_ORDERS -> {
                // 处理请求
            }
        }
        true
    })
    
    override fun onBind(intent: Intent) = messenger.binder
}

// 3. ContentProvider
class OrderProvider : ContentProvider() {
    override fun query(...): Cursor {
        // 返回订单数据
    }
}

// 4. 使用 EventBus 跨进程
// 使用 LiveData + Room 观察数据变化
```

---

## 第 6 章 组件化项目结构

### 6.1 工程目录结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       组件化项目结构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Project/
├── app/                          # 主工程
│   ├── src/main/
│   │   ├── java/
│   │   │   └── com/example/app/
│   │   │       ├── App.kt        # Application
│   │   │       └── MainActivity.kt
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
│
├── module-user/                  # 用户模块
│   ├── src/main/
│   │   ├── java/
│   │   │   └── com/example/user/
│   │   │       ├── ui/           # 页面
│   │   │       │   ├── LoginActivity.kt
│   │   │       │   └── ProfileActivity.kt
│   │   │       ├── vm/           # ViewModel
│   │   │       ├── repo/         # Repository
│   │   │       └── service/      # 服务实现
│   │   └── AndroidManifest