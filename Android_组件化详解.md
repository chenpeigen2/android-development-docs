# Android 组件化详解

> 作者：OpenClaw | 日期：2026-04-02  
> 组件化架构完全指南 | 模块解耦、路由、通信

---

## 📚 目录

- [1. 概述](#1-概述)
- [2. 分层架构](#2-分层架构)
- [3. 模块划分原则](#3-模块划分原则)
- [4. 模块解耦方案](#4-模块解耦方案)
- [5. 路由框架](#5-路由框架)
- [6. 组件通信](#6-组件通信)
- [7. 项目结构与 Gradle 配置](#7-项目结构与-gradle-配置)
- [8. 最佳实践](#8-最佳实践)
- [9. 面试常见问题](#9-面试常见问题)
- [10. 业界实践：百度App组件化之路](#10-业界实践百度app组件化之路)

---

## 1. 概述

### 1.1 什么是组件化

组件化是将一个大型 App 拆分为多个独立业务模块的架构方式。每个模块可独立开发、编译、运行，模块间通过接口或路由进行通信，实现真正的解耦。

```
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

```
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

```
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
```
module-home      # 首屏、首页
module-user      # 登录、注册、个人中心
module-product   # 商品列表、商品详情
module-order     # 订单、购物车
module-pay       # 支付
module-search    # 搜索
module-shop      # 店铺
```

**社交项目：**
```
module-home      # 首页 Feed
module-message   # 消息、聊天
module-moment    # 动态、朋友圈
module-user      # 用户、设置
module-medial    # 拍照、图片处理
```

### 3.3 接口定义规范

接口放在公共层（`lib-common`），模块只依赖接口，不依赖实现：

```
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

```
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

**1. Gradle 配置：**

```kotlin
// 项目 build.gradle.kts
plugins {
    id("com.alibaba.arouter") version "1.5.2"
}

// 模块 build.gradle.kts
plugins {
    kotlin("kapt")
}

dependencies {
    implementation("com.alibaba:arouter-api:1.5.2")
    kapt("com.alibaba:arouter-compiler:1.5.2")
}

android {
    kapt {
        arguments {
            arg("AROUTER_MODULE_NAME", project.name)
            arg("AROUTER_GENERATE_DOC", "yes")
        }
    }
}
```

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
        if (postcard.extra == NEED_LOGIN && !UserManager.isLogin()) {
            // 中断跳转
            callback.onInterrupt(null)
            // 跳转登录页
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

```
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

**方案一：isDebug 开关（简单常用）**

```kotlin
// build.gradle.kts (module-user)
android {
    defaultConfig {
        applicationId = if (isDebug) "com.example.user" else "com.example.app.user"
    }

    buildFeatures {
        buildConfig = true
    }
}

// 独立运行时
if (isDebug) {
    plugins.withId("com.android.application") {
        configure<ApplicationExtension> {
            defaultConfig.applicationId = "com.example.user"
        }
    }
} else {
    plugins.withId("com.android.library") {
        configure<LibraryExtension> {
            defaultConfig.namespace = "com.example.user"
        }
    }
}
```

**方案二：单独 Debug 变体（推荐）**

```
android {
    // 对每个模块配置 debugApplicationIdSuffix
    // 或在 app 中添加 sourceSets 依赖其他模块的 src/debug/
}
```

**模块间依赖配置：**

```kotlin
// module-order 的 build.gradle.kts
dependencies {
    // 只暴露接口，不暴露实现细节
    api(project(":lib-common"))   // 上层可依赖
    implementation(project(":lib-network"))
    implementation(project(":lib-image"))
    compileOnly(project(":module-user"))  // 编译时依赖，运行时不需要
}
```

### 7.3 模块独立运行配置

每个模块的 `src/main/AndroidManifest.xml` 在独立运行时有 Application 和 Launch Activity：

```xml
<!-- module-user/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- 独立运行时生效 -->
    <application
        android:name=".UserApp"
        tools:replace="android:name">

        <activity
            android:name=".ui.LoginActivity"
            tools:node="replace">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

### 7.4 资源冲突管理

不同模块可能有同名资源（如 `strings.xml`、`colors.xml`）。解决方案：

1. **模块名前缀**：所有资源加模块前缀
   - `user_strings.xml` / `order_strings.xml`

2. **资源分包**：
   ```
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

```
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

**解决方案：** 所有三方库更新到最新版本并二进制化，差异部分运行时打补丁

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
