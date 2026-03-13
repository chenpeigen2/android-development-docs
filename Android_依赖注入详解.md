# Android 依赖注入详解

> 作者：OpenClaw | 日期：2026-03-13

---

## 目录

1. [概述](#1-概述)
2. [依赖注入基础](#2-依赖注入基础)
3. [Hilt 依赖注入](#3-hilt-依赖注入)
4. [Koin 依赖注入](#4-koin-依赖注入)
5. [Dagger2 简介](#5-dagger2-简介)
6. [框架对比](#6-框架对比)
7. [最佳实践](#7-最佳实践)
8. [常见问题](#8-常见问题)
9. [知识体系总结](#9-知识体系总结)

---

## 1. 概述

### 1.1 什么是依赖注入

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         依赖注入定义                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  依赖注入（Dependency Injection，DI）：
  ─────────────────────────────────────────────────────────────────────────
  一种设计模式，将依赖对象的创建和管理交给外部容器，而不是在类内部创建

  控制反转（Inversion of Control，IoC）：
  ─────────────────────────────────────────────────────────────────────────
  将对象的创建和依赖关系的管理交给容器，实现控制权的反转

  解决的问题：
  ─────────────────────────────────────────────────────────────────────────
  - 降低耦合度
  - 提高代码可测试性
  - 便于复用和维护
  - 集中管理依赖
```

### 1.2 为什么需要依赖注入

```kotlin
// ==================== 问题：紧耦合 ====================
class UserRepository {
    private val api = UserApi()        // 内部创建
    private val dao = UserDao()        // 内部创建
    private val context = MyApp.context // 全局引用
    
    fun getUser(id: String): User {
        // ...
    }
}

// 问题：
// 1. 无法替换实现（如测试时用 Mock）
// 2. 难以单元测试
// 3. 依赖硬编码，难以维护

// ==================== 解决：依赖注入 ====================
class UserRepository(
    private val api: UserApi,      // 外部注入
    private val dao: UserDao,      // 外部注入
    private val context: Context   // 外部注入
) {
    fun getUser(id: String): User {
        // ...
    }
}

// 优点：
// 1. 依赖可替换（测试时注入 Mock）
// 2. 职责单一（只负责业务逻辑）
// 3. 易于测试和维护
```

### 1.3 依赖注入方式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         依赖注入方式                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 构造器注入（推荐）：
  ─────────────────────────────────────────────────────────────────────────
  class UserRepository(
      private val api: UserApi,
      private val dao: UserDao
  )

  2. 属性注入（Setter 注入）：
  ─────────────────────────────────────────────────────────────────────────
  class UserRepository {
      lateinit var api: UserApi
      lateinit var dao: UserDao
  }

  3. 接口注入：
  ─────────────────────────────────────────────────────────────────────────
  interface ApiInjector {
      fun inject(api: UserApi)
  }
  
  class UserRepository : ApiInjector {
      private var api: UserApi? = null
      
      override fun inject(api: UserApi) {
          this.api = api
      }
  }

  4. 方法注入：
  ─────────────────────────────────────────────────────────────────────────
  class UserRepository {
      private var api: UserApi? = null
      
      fun setApi(api: UserApi) {
          this.api = api
      }
  }
```

### 1.4 Android DI 框架对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DI 框架对比                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┬──────────────┬──────────────┬──────────────────────────┐
  │      框架         │   实现方式    │   复杂度      │        特点              │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  Hilt            │  编译时注解   │  中等         │  Google 官方，Android 专用│
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  Koin            │  运行时反射   │  简单         │  Kotlin 友好，轻量级      │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  Dagger2         │  编译时注解   │  复杂         │  功能强大，学习曲线陡      │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  Kodein          │  运行时       │  简单         │  Kotlin DSL              │
  └──────────────────┴──────────────┴──────────────┴──────────────────────────┘

  选择建议：
  ─────────────────────────────────────────────────────────────────────────
  - 新项目 / Java 项目：Hilt（Google 官方推荐）
  - Kotlin 项目 / 小型项目：Koin（简单易用）
  - 大型项目 / 需要极致性能：Dagger2
```

---

## 2. 依赖注入基础

### 2.1 手动依赖注入

```kotlin
// ==================== 手动实现 DI 容器 ====================
// 依赖类
interface UserRepository {
    fun getUser(id: String): User
}

class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {
    override fun getUser(id: String): User {
        // 实现
    }
}

// DI 容器
object AppContainer {
    // 单例
    private val userApi: UserApi by lazy { UserApi() }
    private val userDao: UserDao by lazy { UserDao() }
    
    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(userApi, userDao)
    }
}

// 使用
class UserViewModel(
    private val repository: UserRepository = AppContainer.userRepository
) : ViewModel() {
    // ...
}

// ==================== Application 级容器 ====================
class MyApplication : Application() {
    
    lateinit var appContainer: AppContainer
    
    override fun onCreate() {
        super.onCreate()
        appContainer = AppContainer()
    }
}

class AppContainer {
    private val userApi: UserApi by lazy { UserApi() }
    private val userDao: UserDao by lazy { UserDao() }
    
    val userRepository: UserRepository by lazy {
        UserRepositoryImpl(userApi, userDao)
    }
    
    // Activity 级容器
    fun createUserContainer(): UserContainer {
        return UserContainer(userRepository)
    }
}

class UserContainer(
    val userRepository: UserRepository
) {
    val userViewModelFactory = UserViewModelFactory(userRepository)
}

// Activity 中使用
class UserActivity : AppCompatActivity() {
    
    private lateinit var container: UserContainer
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        container = (application as MyApplication).appContainer.createUserContainer()
        
        val viewModel: UserViewModel by viewModels {
            container.userViewModelFactory
        }
    }
}
```

### 2.2 工厂模式

```kotlin
// ==================== ViewModelFactory ====================
class UserViewModelFactory(
    private val repository: UserRepository
) : ViewModelProvider.Factory {
    
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(UserViewModel::class.java)) {
            return UserViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

// 使用
class UserActivity : AppCompatActivity() {
    
    private val viewModel: UserViewModel by viewModels {
        UserViewModelFactory(AppContainer.userRepository)
    }
}

// ==================== 通用 Factory ====================
inline fun <reified VM : ViewModel> viewModelFactory(
    crossinline creator: () -> VM
): ViewModelProvider.Factory {
    return object : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            return creator() as T
        }
    }
}

// 使用
private val viewModel: UserViewModel by viewModels {
    viewModelFactory { UserViewModel(AppContainer.userRepository) }
}
```

### 2.3 服务定位器模式

```kotlin
// ==================== Service Locator ====================
object ServiceLocator {
    
    private val instances = mutableMapOf<KClass<*>, Any>()
    
    @Synchronized
    fun <T : Any> register(clazz: KClass<T>, instance: T) {
        instances[clazz] = instance
    }
    
    @Suppress("UNCHECKED_CAST")
    @Synchronized
    fun <T : Any> get(clazz: KClass<T>): T {
        return instances[clazz] as? T
            ?: throw IllegalStateException("No instance registered for ${clazz.simpleName}")
    }
    
    @Synchronized
    fun <T : Any> getOrNull(clazz: KClass<T>): T? {
        return instances[clazz] as? T
    }
    
    @Synchronized
    fun <T : Any> unregister(clazz: KClass<T>) {
        instances.remove(clazz)
    }
    
    @Synchronized
    fun clear() {
        instances.clear()
    }
}

// 注册
ServiceLocator.register(UserApi::class, UserApi())
ServiceLocator.register(UserRepository::class, UserRepositoryImpl())

// 获取
val repository = ServiceLocator.get(UserRepository::class)

// 注意：Service Locator 不是真正的 DI，它是一个反模式
// 推荐使用 Hilt 或 Koin 等正规 DI 框架
```

---

## 3. Hilt 依赖注入

### 3.1 Hilt 简介

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Hilt 简介                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  Hilt 是 Google 官方的 Android 依赖注入库，基于 Dagger2

  特点：
  ─────────────────────────────────────────────────────────────────────────
  - 基于 Dagger2，编译时生成代码
  - 专为 Android 优化
  - 简化了 Dagger2 的配置
  - 支持 ViewModel、Fragment、Activity 等

  依赖：
  ─────────────────────────────────────────────────────────────────────────
  // build.gradle (Project)
  plugins {
      id("com.google.dagger.hilt.android") version "2.50" apply false
  }
  
  // build.gradle (Module)
  plugins {
      id("com.android.application")
      id("org.jetbrains.kotlin.android")
      id("com.google.dagger.hilt.android")
      id("com.google.devtools.ksp")
  }
  
  dependencies {
      implementation("com.google.dagger:hilt-android:2.50")
      ksp("com.google.dagger:hilt-compiler:2.50")
      
      // ViewModel 支持
      implementation("androidx.hilt:hilt-navigation-fragment:1.1.0")
  }
```

### 3.2 基本配置

```kotlin
// ==================== Application ====================
@HiltAndroidApp
class MyApplication : Application() {
    // Hilt 入口点
}

// ==================== Activity ====================
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    // 可以注入依赖了
}

// ==================== Fragment ====================
@AndroidEntryPoint
class UserFragment : Fragment() {
    // 可以注入依赖了
}

// ==================== View ====================
@AndroidEntryPoint
class CustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {
    // 可以注入依赖了
}

// ==================== Service ====================
@AndroidEntryPoint
class MyService : Service() {
    // 可以注入依赖了
}

// ==================== BroadcastReceiver ====================
@AndroidEntryPoint
class MyReceiver : BroadcastReceiver() {
    // 可以注入依赖了
}

// 注意：ContentProvider 不支持 @AndroidEntryPoint
```

### 3.3 @Inject 注入

```kotlin
// ==================== 构造器注入 ====================
class UserRepository @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao
) {
    fun getUser(id: String): User {
        // ...
    }
}

// ==================== 字段注入 ====================
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    
    @Inject
    lateinit var userRepository: UserRepository
    
    @Inject
    lateinit var analytics: Analytics
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // userRepository 和 analytics 已自动注入
    }
}

// ==================== 方法注入 ====================
class UserRepository @Inject constructor(
    private val api: UserApi
) {
    private lateinit var context: Context
    
    @Inject
    fun setContext(context: Context) {
        this.context = context
    }
}
```

### 3.4 @Module 和 @Provides

```kotlin
// ==================== Module 定义 ====================
@Module
@InstallIn(SingletonComponent::class)  // 安装到 Application 级别
object NetworkModule {
    
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(LoggingInterceptor())
            .build()
    }
    
    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi {
        return retrofit.create(UserApi::class.java)
    }
}

// ==================== 数据库 Module ====================
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        ).build()
    }
    
    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
}

// ==================== Repository Module ====================
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    
    @Binds
    @Singleton
    abstract fun bindUserRepository(
        impl: UserRepositoryImpl
    ): UserRepository
}

// 或使用 @Provides
@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    
    @Provides
    @Singleton
    fun provideUserRepository(
        api: UserApi,
        dao: UserDao
    ): UserRepository {
        return UserRepositoryImpl(api, dao)
    }
}
```

### 3.5 组件和作用域

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Hilt 组件层次结构                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  SingletonComponent (Application)                                       │
  │  @Singleton                                                             │
  │       │                                                                 │
  │       ├── ActivityRetainedComponent (Activity 保留，横屏不销毁)          │
  │       │   @ActivityRetainedScoped                                       │
  │       │       │                                                         │
  │       │       └── ViewModelComponent                                    │
  │       │           @ViewModelScoped                                      │
  │       │                                                                 │
  │       ├── ActivityComponent (Activity)                                  │
  │       │   @ActivityScoped                                               │
  │       │       │                                                         │
  │       │       ├── FragmentComponent (Fragment)                          │
  │       │       │   @FragmentScoped                                       │
  │       │       │                                                         │
  │       │       └── ViewComponent (View)                                  │
  │       │           @ViewScoped                                           │
  │       │                                                                 │
  │       └── ServiceComponent (Service)                                    │
  │           @ServiceScoped                                                │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  作用域说明：
  ─────────────────────────────────────────────────────────────────────────
  - @Singleton：Application 生命周期
  - @ActivityRetainedScoped：Activity 生命周期（配置更改保留）
  - @ViewModelScoped：ViewModel 生命周期
  - @ActivityScoped：Activity 生命周期
  - @FragmentScoped：Fragment 生命周期
  - @ViewScoped：View 生命周期
  - @ServiceScoped：Service 生命周期
```

```kotlin
// ==================== Singleton 作用域 ====================
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    
    @Provides
    @Singleton
    fun provideSharedPreferences(@ApplicationContext context: Context): SharedPreferences {
        return context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
    }
}

// ==================== Activity 作用域 ====================
@Module
@InstallIn(ActivityComponent::class)
object ActivityModule {
    
    @Provides
    @ActivityScoped
    fun provideActivityDependency(): ActivityDependency {
        return ActivityDependency()
    }
}

// ==================== Fragment 作用域 ====================
@Module
@InstallIn(FragmentComponent::class)
object FragmentModule {
    
    @Provides
    @FragmentScoped
    fun provideFragmentDependency(): FragmentDependency {
        return FragmentDependency()
    }
}

// ==================== ViewModel 作用域 ====================
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // ViewModel 级别的单例
}

// 使用
@AndroidEntryPoint
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()
}
```

### 3.6 @ApplicationContext 和 @ActivityContext

```kotlin
// ==================== @ApplicationContext ====================
class UserRepository @Inject constructor(
    @ApplicationContext private val context: Context
) {
    fun getResource(): String {
        return context.getString(R.string.app_name)
    }
}

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "db").build()
    }
}

// ==================== @ActivityContext ====================
class ImageLoader @Inject constructor(
    @ActivityContext private val context: Context
) {
    fun load(imageView: ImageView, url: String) {
        Glide.with(context).load(url).into(imageView)
    }
}

// 使用
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    
    @Inject
    lateinit var imageLoader: ImageLoader  // 自动注入 Activity context
}
```

### 3.7 ViewModel 注入

```kotlin
// ==================== @HiltViewModel ====================
@HiltViewModel
class UserViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    
    private val userId: String = savedStateHandle["userId"] ?: ""
    
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user
    
    init {
        loadUser()
    }
    
    private fun loadUser() {
        viewModelScope.launch {
            _user.value = userRepository.getUser(userId)
        }
    }
}

// ==================== Fragment 中使用 ====================
@AndroidEntryPoint
class UserFragment : Fragment() {
    
    // 方式1：Fragment 独有 ViewModel
    private val viewModel: UserViewModel by viewModels()
    
    // 方式2：与 Activity 共享 ViewModel
    private val activityViewModel: UserViewModel by activityViewModels()
    
    // 方式3：带 SavedStateHandle 参数传递
    // 导航时传参
    // findNavController().navigate(R.id.userFragment, bundleOf("userId" to "123"))
}

// ==================== Activity 中使用 ====================
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    
    private val viewModel: UserViewModel by viewModels()
}

// ==================== 限定符 ====================
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainDispatcher

@Module
@InstallIn(SingletonComponent::class)
object CoroutinesModule {
    
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO
    
    @Provides
    @MainDispatcher
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main
}

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) : ViewModel() {
    
    fun loadData() {
        viewModelScope.launch(ioDispatcher) {
            // 在 IO 线程执行
        }
    }
}
```

### 3.8 接口绑定

```kotlin
// ==================== @Binds ====================
interface UserRepository {
    fun getUser(id: String): User
}

class UserRepositoryImpl @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {
    override fun getUser(id: String): User {
        // 实现
    }
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// 使用
class UserViewModel @Inject constructor(
    private val repository: UserRepository  // 注入接口
) : ViewModel() {
}

// ==================== 多实现绑定 ====================
interface DataSource {
    fun getData(): String
}

class LocalDataSource @Inject constructor() : DataSource {
    override fun getData() = "Local Data"
}

class RemoteDataSource @Inject constructor() : DataSource {
    override fun getData() = "Remote Data"
}

// 限定符
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class LocalSource

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class RemoteSource

@Module
@InstallIn(SingletonComponent::class)
object DataSourceModule {
    
    @Provides
    @LocalSource
    fun provideLocalDataSource(): DataSource = LocalDataSource()
    
    @Provides
    @RemoteSource
    fun provideRemoteDataSource(): DataSource = RemoteDataSource()
}

// 使用
class DataRepository @Inject constructor(
    @LocalSource private val localSource: DataSource,
    @RemoteSource private val remoteSource: DataSource
) {
    // ...
}
```

### 3.9 Entry Points

```kotlin
// ==================== 在不支持 @AndroidEntryPoint 的类中使用 ====================
// 定义 Entry Point
@EntryPoint
@InstallIn(SingletonComponent::class)
interface RepositoryEntryPoint {
    fun userRepository(): UserRepository
}

// 在 ContentProvider 中使用
class MyContentProvider : ContentProvider() {
    
    override fun query(...): Cursor? {
        val appContext = context?.applicationContext ?: return null
        
        val hiltEntryPoint = EntryPointAccessors.fromApplication(
            appContext,
            RepositoryEntryPoint::class.java
        )
        
        val userRepository = hiltEntryPoint.userRepository()
        // 使用 userRepository
    }
}

// ==================== 在非 Hilt 类中使用 ====================
class NonHiltClass(context: Context) {
    
    private val userRepository: UserRepository
    
    init {
        val entryPoint = EntryPointAccessors.fromApplication(
            context.applicationContext,
            RepositoryEntryPoint::class.java
        )
        userRepository = entryPoint.userRepository()
    }
}
```

### 3.10 测试支持

```kotlin
// ==================== 单元测试 ====================
@HiltAndroidTest
class UserRepositoryTest {
    
    @get:Rule
    var hiltRule = HiltAndroidRule(this)
    
    @Inject
    lateinit var userRepository: UserRepository
    
    @Before
    fun init() {
        hiltRule.inject()
    }
    
    @Test
    fun testGetUser() {
        val user = userRepository.getUser("123")
        assertEquals("张三", user.name)
    }
}

// ==================== 替换 Module（测试）====================
@Module
@InstallIn(SingletonComponent::class)
object TestNetworkModule {
    
    @Provides
    @Singleton
    fun provideFakeUserApi(): UserApi {
        return FakeUserApi()  // 测试用假实现
    }
}

// 测试配置
@UninstallModules(NetworkModule::class)  // 卸载原 Module
@HiltAndroidTest
class UserViewModelTest {
    
    @get:Rule
    var hiltRule = HiltAndroidRule(this)
    
    @Inject
    lateinit var userApi: UserApi  // 会注入 FakeUserApi
    
    // ...
}

// ==================== Robolectric 测试 ====================
@RunWith(RobolectricTestRunner::class)
@Config(application = HiltTestApplication::class)
@HiltAndroidTest
class ExampleTest {
    // ...
}
```

---

## 4. Koin 依赖注入

### 4.1 Koin 简介

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Koin 简介                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  Koin 是 Kotlin 原生的轻量级依赖注入框架

  特点：
  ─────────────────────────────────────────────────────────────────────────
  - 纯 Kotlin，DSL 风格
  - 运行时解析，无代码生成
  - 学习曲线低，易于上手
  - 支持协程、ViewModel、Compose

  依赖：
  ─────────────────────────────────────────────────────────────────────────
  // build.gradle
  dependencies {
      // Koin 核心
      implementation("io.insert-koin:koin-android:3.5.0")
      
      // ViewModel 支持
      implementation("io.insert-koin:koin-androidx-compose:3.5.0")
      
      // Navigation 支持
      implementation("io.insert-koin:koin-androidx-navigation:3.5.0")
      
      // WorkManager 支持
      implementation("io.insert-koin:koin-androidx-workmanager:3.5.0")
  }
```

### 4.2 基本配置

```kotlin
// ==================== Module 定义 ====================
val networkModule = module {
    // 单例
    single { 
        OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .build() 
    }
    
    single { 
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(get())  // 获取上面的 OkHttpClient
            .addConverterFactory(GsonConverterFactory.create())
            .build() 
    }
    
    single { get<Retrofit>().create(UserApi::class.java) }
}

val databaseModule = module {
    single { 
        Room.databaseBuilder(
            androidContext(),
            AppDatabase::class.java,
            "app_database"
        ).build() 
    }
    
    single { get<AppDatabase>().userDao() }
}

val repositoryModule = module {
    // 单例
    single<UserRepository> { UserRepositoryImpl(get(), get()) }
    
    // 或使用 factory（每次创建新实例）
    factory<UserRepository> { UserRepositoryImpl(get(), get()) }
}

val viewModelModule = module {
    // ViewModel
    viewModel { UserViewModel(get()) }
    
    // 带参数的 ViewModel
    viewModel { (userId: String) -> 
        UserViewModel(get(), userId) 
    }
}

// ==================== Application 初始化 ====================
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        startKoin {
            // Android 上下文
            androidContext(this@MyApplication)
            
            // 加载模块
            modules(
                networkModule,
                databaseModule,
                repositoryModule,
                viewModelModule
            )
        }
    }
}
```

### 4.3 依赖声明

```kotlin
// ==================== single（单例）====================
val appModule = module {
    // 单例，整个应用共享一个实例
    single { UserApi() }
    
    // 带名称的单例
    single(named("local")) { LocalDataSource() }
    single(named("remote")) { RemoteDataSource() }
    
    // 带作用域的单例
    single { UserRepository(get(), get(named("local"))) }
}

// ==================== factory（工厂）====================
val appModule = module {
    // 每次获取都创建新实例
    factory { UserAdapter() }
    
    // 带参数的工厂
    factory { (userId: String) -> 
        UserSession(userId) 
    }
}

// ==================== viewModel ====================
val viewModelModule = module {
    // ViewModel
    viewModel { UserViewModel(get()) }
    
    // 带参数的 ViewModel
    viewModel { (userId: String) -> 
        UserDetailViewModel(get(), userId) 
    }
    
    // 带 SavedStateHandle 的 ViewModel
    viewModel { UserViewModel(get(), get()) }  // 第二个 get 是 SavedStateHandle
}

// ==================== scoped（作用域）====================
val appModule = module {
    scope<MainActivity> {
        // 只在 MainActivity 作用域内单例
        scoped { ActivityDependency() }
    }
}
```

### 4.4 依赖注入

```kotlin
// ==================== by inject（懒加载）====================
class MainActivity : AppCompatActivity() {
    
    // 懒加载注入
    private val userRepository: UserRepository by inject()
    private val userApi: UserApi by inject()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 首次访问时才创建
        userRepository.getUser("123")
    }
}

// ==================== get()（立即获取）====================
class MainActivity : AppCompatActivity() {
    
    // 立即获取
    private val userRepository: UserRepository = get()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
    }
}

// ==================== ViewModel 注入 ====================
class MainActivity : AppCompatActivity() {
    
    // ViewModel 注入
    private val viewModel: UserViewModel by viewModel()
    
    // 带参数的 ViewModel
    private val detailViewModel: UserDetailViewModel by viewModel { 
        parametersOf("userId123") 
    }
    
    // Activity 共享 ViewModel
    private val sharedViewModel: SharedViewModel by viewModel()
}

class UserFragment : Fragment() {
    
    // Fragment 独有 ViewModel
    private val viewModel: UserViewModel by viewModel()
    
    // 与 Activity 共享 ViewModel
    private val sharedViewModel: SharedViewModel by sharedViewModel()
    
    // 带参数的 ViewModel
    private val detailViewModel: UserDetailViewModel by viewModel { 
        parametersOf("userId123") 
    }
}

// ==================== 带名称的注入 ====================
class MainActivity : AppCompatActivity() {
    
    private val localDataSource: DataSource by inject(named("local"))
    private val remoteDataSource: DataSource by inject(named("remote"))
    
    // 或
    private val dataSource: DataSource by inject {
        parametersOf("local")
    }
}
```

### 4.5 构造器注入

```kotlin
// ==================== 自动构造器注入 ====================
// Koin 可以自动解析构造器参数
class UserRepository(
    private val api: UserApi,
    private val dao: UserDao
) {
    // ...
}

val appModule = module {
    single { UserApi() }
    single { UserDao() }
    
    // 自动注入 api 和 dao
    single { UserRepository(get(), get()) }
    
    // 或更简洁
    singleOf(::UserRepository)
}

// ==================== singleOf / factoryOf ====================
val appModule = module {
    // 单例
    singleOf(::UserApi)
    singleOf(::UserDao)
    singleOf(::UserRepository)
    
    // 工厂
    factoryOf(::UserAdapter)
    
    // 绑定接口
    singleOf(::UserRepositoryImpl) bind UserRepository::class
}

// ==================== 带参数的构造 ====================
class UserSession(val userId: String)

val appModule = module {
    factory { (userId: String) -> UserSession(userId) }
}

// 使用
val session: UserSession = get { parametersOf("userId123") }
```

### 4.6 作用域

```kotlin
// ==================== 定义作用域 ====================
val appModule = module {
    // 定义作用域
    scope<MainActivity> {
        scoped { ActivityPresenter() }
        scoped { ActivityAdapter() }
    }
    
    scope<UserFragment> {
        scoped { FragmentPresenter() }
    }
}

// ==================== 使用作用域 ====================
class MainActivity : AppCompatActivity() {
    
    private val scope = createScope(this)
    
    private val presenter: ActivityPresenter by scope.inject()
    private val adapter: ActivityAdapter by scope.inject()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // ...
    }
    
    override fun onDestroy() {
        super.onDestroy()
        scope.close()  // 销毁作用域
    }
}

// ==================== 作用域链接 ====================
class MainActivity : AppCompatActivity() {
    
    private val activityScope = createScope(this)
    
    fun navigateToFragment() {
        val fragment = UserFragment().apply {
            // 链接作用域，Fragment 可以访问 Activity 的依赖
            linkScope(activityScope)
        }
    }
}
```

### 4.7 属性注入

```kotlin
// ==================== 属性定义 ====================
val appModule = module {
    single { UserApi(getProperty("api_key")) }
}

// ==================== 加载属性 ====================
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        startKoin {
            androidContext(this@MyApplication)
            
            // 加载属性
            properties(
                mapOf(
                    "api_key" to "your_api_key",
                    "debug" to true
                )
            )
            
            modules(appModule)
        }
    }
}

// ==================== 获取属性 ====================
class UserRepository {
    private val apiKey: String by KoinJavaComponent.getKoin().getProperty("api_key")
    private val debug: Boolean by KoinJavaComponent.getKoin().getProperty("debug", false)
}
```

### 4.8 Koin 测试

```kotlin
// ==================== 单元测试 ====================
class UserRepositoryTest : KoinTest {
    
    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(testModule)
    }
    
    // 注入
    private val userRepository: UserRepository by inject()
    
    @Test
    fun testGetUser() {
        val user = userRepository.getUser("123")
        assertEquals("张三", user.name)
    }
}

// ==================== Mock 替换 ====================
class UserViewModelTest : KoinTest {
    
    private val mockRepository: UserRepository = mockk()
    
    @get:Rule
    val koinTestRule = KoinTestRule.create {
        modules(module {
            single<UserRepository> { mockRepository }
        })
    }
    
    @Test
    fun testLoadUser() {
        every { mockRepository.getUser("123") } returns User("123", "张三")
        
        val viewModel: UserViewModel by viewModel()
        viewModel.loadUser("123")
        
        verify { mockRepository.getUser("123") }
    }
}

// ==================== checkModules ====================
class ModuleCheckTest {
    @Test
    fun checkKoinModules() {
        koinApplication {
            modules(appModule)
            checkModules()  // 检查所有依赖是否可解析
        }
    }
}
```

### 4.9 Compose 支持

```kotlin
// ==================== Compose 注入 ====================
@Composable
fun UserScreen() {
    // ViewModel
    val viewModel: UserViewModel = koinViewModel()
    
    // 或带参数
    val detailViewModel: UserDetailViewModel = koinViewModel { 
        parametersOf("userId123") 
    }
    
    // 普通依赖
    val userRepository: UserRepository = koinInject()
    
    // ...
}

// ==================== KoinApplication ====================
@Composable
fun App() {
    KoinApplication(
        application = koinApplication {
            modules(appModule)
        }
    ) {
        // 子组件可以使用 Koin
        UserScreen()
    }
}
```

---

## 5. Dagger2 简介

### 5.1 Dagger2 概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Dagger2 简介                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  Dagger2 是 Google 维护的编译时依赖注入框架

  特点：
  ─────────────────────────────────────────────────────────────────────────
  - 纯编译时，无反射
  - 性能最优
  - 功能强大，灵活性高
  - 学习曲线陡峭

  与 Hilt 的关系：
  ─────────────────────────────────────────────────────────────────────────
  - Hilt 基于 Dagger2
  - Hilt 简化了 Android 集成
  - 新项目推荐使用 Hilt

  核心注解：
  ─────────────────────────────────────────────────────────────────────────
  - @Component：连接器
  - @Module：模块
  - @Provides：提供依赖
  - @Inject：注入点
  - @Scope：作用域
  - @Qualifier：限定符
```

### 5.2 Dagger2 基本使用

```kotlin
// ==================== @Module ====================
@Module
object NetworkModule {
    
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder().build()
    }
    
    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .build()
    }
}

// ==================== @Component ====================
@Singleton
@Component(modules = [NetworkModule::class, DatabaseModule::class])
interface AppComponent {
    
    // 注入方法
    fun inject(activity: MainActivity)
    fun inject(fragment: UserFragment)
    
    // 提供依赖
    fun userRepository(): UserRepository
}

// ==================== 使用 ====================
class MyApplication : Application() {
    
    lateinit var appComponent: AppComponent
    
    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.create()
    }
}

@Singleton
class UserRepository @Inject constructor(
    private val api: UserApi
) {
    // ...
}

class MainActivity : AppCompatActivity() {
    
    @Inject
    lateinit var userRepository: UserRepository
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 注入
        (application as MyApplication).appComponent.inject(this)
    }
}
```

### 5.3 Dagger2 vs Hilt

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Dagger2 vs Hilt                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  Hilt 优势：
  ─────────────────────────────────────────────────────────────────────────
  - 无需手动创建 Component
  - 自动处理 Android 组件生命周期
  - 内置常用组件（Activity、Fragment、ViewModel 等）
  - 更少的样板代码

  Dagger2 优势：
  ─────────────────────────────────────────────────────────────────────────
  - 更灵活，可自定义 Component 层次结构
  - 非 Android 项目可用
  - 更精细的控制

  迁移建议：
  ─────────────────────────────────────────────────────────────────────────
  - 新项目：直接使用 Hilt
  - 现有项目：可以混合使用，逐步迁移
```

---

## 6. 框架对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         依赖注入框架对比                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┬──────────────┬──────────────┬──────────────┬──────────┐
  │      特性         │    Hilt      │    Koin      │   Dagger2    │  手动DI  │
  ├──────────────────┼──────────────┼──────────────┼──────────────┼──────────┤
  │  实现方式         │  编译时注解   │  运行时       │  编译时注解   │  手动    │
  ├──────────────────┼──────────────┼──────────────┼──────────────┼──────────┤
  │  性能             │  高          │  中           │  最高        │  最高    │
  ├──────────────────┼──────────────┼──────────────┼──────────────┼──────────┤
  │  学习曲线         │  中等         │  简单         │  陡峭        │  简单    │
  ├──────────────────┼──────────────┼──────────────┼──────────────┼──────────┤
  │  代码量           │  少           │  最少         │  多          │  多      │
  ├──────────────────┼──────────────┼──────────────┼──────────────┼──────────┤
  │  编译时检查       │  ✅          │  ❌           │  ✅          │  ❌      │
  ├──────────────────┼──────────────┼──────────────┼──────────────┼──────────┤
  │  ViewModel 支持   │  ✅ 内置     │  ✅ 内置      │  需配置      │  手动    │
  ├──────────────────┼──────────────┼──────────────┼──────────────┼──────────┤
  │  测试支持         │  ✅ 完善     │  ✅ 完善      │  ✅ 完善     │  手动    │
  ├──────────────────┼──────────────┼──────────────┼──────────────┼──────────┤
  │  Kotlin 友好      │  ✅          │  ✅ 最佳      │  一般        │  ✅      │
  └──────────────────┴──────────────┴──────────────┴──────────────┴──────────┘

  选择建议：
  ─────────────────────────────────────────────────────────────────────────
  
  1. 新项目（Android）：
     - Java 项目：Hilt
     - Kotlin 项目：Hilt 或 Koin
  
  2. 小型项目：
     - Koin（简单易用）
     - 手动 DI（无额外依赖）
  
  3. 大型项目：
     - Hilt（Google 官方推荐）
     - Dagger2（极致性能）
  
  4. 多平台项目：
     - Koin（Kotlin Multiplatform 支持）
  
  5. 需要编译时检查：
     - Hilt 或 Dagger2
```

---

## 7. 最佳实践

### 7.1 架构设计

```kotlin
// ==================== 分层架构 ====================
// Module 按层划分
val appModules = listOf(
    networkModule,      // 网络层
    databaseModule,     // 数据库层
    repositoryModule,   // 数据层
    useCaseModule,      // 业务层
    viewModelModule     // UI 层
)

// ==================== 接口绑定 ====================
// 使用接口，便于测试和替换
interface UserRepository {
    suspend fun getUser(id: String): User
}

class UserRepositoryImpl @Inject constructor(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {
    override suspend fun getUser(id: String): User {
        // 实现
    }
}

// Hilt 绑定
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// Koin 绑定
val repositoryModule = module {
    singleOf(::UserRepositoryImpl) bind UserRepository::class
}
```

### 7.2 作用域使用

```kotlin
// ==================== 作用域原则 ====================
// 1. Application 级：全局共享的依赖（API、数据库、Repository）
// 2. Activity 级：Activity 内共享的依赖
// 3. Fragment 级：Fragment 内共享的依赖
// 4. ViewModel 级：ViewModel 内共享的依赖

// Hilt 示例
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideUserApi(): UserApi = UserApi()
}

@Module
@InstallIn(ActivityComponent::class)
object ActivityModule {
    @Provides
    @ActivityScoped
    fun provideActivityAdapter(): UserAdapter = UserAdapter()
}

// Koin 示例
val appModule = module {
    single { UserApi() }  // Application 级
    viewModel { UserViewModel(get()) }  // ViewModel 级
    factory { UserAdapter() }  // 每次创建
}
```

### 7.3 命名和限定符

```kotlin
// ==================== 使用限定符区分相同类型 ====================
// Hilt
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class MainDispatcher

@Module
@InstallIn(SingletonComponent::class)
object CoroutinesModule {
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO
    
    @Provides
    @MainDispatcher
    fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main
}

// Koin
val appModule = module {
    single(named("io")) { Dispatchers.IO }
    single(named("main")) { Dispatchers.Main }
    
    single { CoroutineDispatcherProvider(
        io = get(named("io")),
        main = get(named("main"))
    )}
}
```

### 7.4 测试策略

```kotlin
// ==================== Hilt 测试 ====================
@HiltAndroidTest
class UserViewModelTest {
    
    @get:Rule
    var hiltRule = HiltAndroidRule(this)
    
    @BindValue
    @JvmField
    val mockRepository: UserRepository = mockk()
    
    @Inject
    lateinit var viewModel: UserViewModel
    
    @Before
    fun init() {
        hiltRule.inject()
    }
}

// ==================== Koin 测试 ====================
class UserViewModelTest : KoinTest {
    
    private val mockRepository: UserRepository = mockk()
    
    @get:Rule
    val koinRule = KoinTestRule.create {
        modules(module {
            single<UserRepository> { mockRepository }
        })
    }
    
    @Test
    fun test() {
        val viewModel: UserViewModel by viewModel()
        // ...
    }
}
```

---

## 8. 常见问题

```
Q1: Hilt 和 Koin 怎么选？
─────────────────────────────────────────────────────────────────────────
A: 
   - 编译时检查重要：Hilt
   - 简单易用优先：Koin
   - 团队熟悉 Dagger：Hilt
   - Kotlin 项目：都可以，Koin 更 Kotlin 友好

Q2: @Singleton 真的是单例吗？
─────────────────────────────────────────────────────────────────────────
A: 是的，但范围限于 Component 生命周期
   - SingletonComponent：Application 级单例
   - ActivityComponent：Activity 级单例
   - 注意：不同 Component 中的 @Singleton 是不同的实例

Q3: 为什么注入失败？
─────────────────────────────────────────────────────────────────────────
A: 常见原因：
   1. 忘记 @AndroidEntryPoint（Hilt）
   2. Module 未正确安装
   3. 依赖循环
   4. 作用域不匹配
   5. 类型不匹配（接口 vs 实现类）

Q4: Hilt 如何在非 Android 组件中使用？
─────────────────────────────────────────────────────────────────────────
A: 使用 @EntryPoint 和 EntryPointAccessors
   @EntryPoint
   @InstallIn(SingletonComponent::class)
   interface MyEntryPoint {
       fun userRepository(): UserRepository
   }
   
   val entryPoint = EntryPointAccessors.fromApplication(
       context, MyEntryPoint::class.java
   )
   val repository = entryPoint.userRepository()

Q5: Koin 和 Hilt 可以混用吗？
─────────────────────────────────────────────────────────────────────────
A: 不推荐。建议选择一个框架统一使用。

Q6: 如何处理循环依赖？
─────────────────────────────────────────────────────────────────────────
A: 
   1. 重新设计架构，避免循环依赖
   2. 使用 Lazy 注入
   3. 使用 Provider/Factory 延迟获取

   // Hilt
   @Inject
   lateinit var lazyRepository: Lazy<UserRepository>
   
   // Koin
   val repository: Lazy<UserRepository> = inject()

Q7: ViewModel 如何传递参数？
─────────────────────────────────────────────────────────────────────────
A:
   Hilt：使用 SavedStateHandle
   @HiltViewModel
   class UserViewModel @Inject constructor(
       private val savedStateHandle: SavedStateHandle
   ) : ViewModel() {
       val userId: String = savedStateHandle["userId"] ?: ""
   }
   
   Koin：使用 parametersOf
   viewModel { (userId: String) -> UserViewModel(get(), userId) }
   private val viewModel: UserViewModel by viewModel { parametersOf("123") }

Q8: 如何调试依赖注入问题？
─────────────────────────────────────────────────────────────────────────
A:
   Hilt：
   - 查看 generated 目录下的代码
   - 使用 kapt.showProcessorStats = true
   
   Koin：
   - 使用 KoinLogger
   - 调用 checkModules() 检查
   - 使用 koin.dump() 打印依赖图
```

---

## 9. 知识体系总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         依赖注入知识体系                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   依赖注入 DI   │
                           └────────┬────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
  ┌───────────┐              ┌───────────┐              ┌───────────┐
  │   Hilt    │              │   Koin    │              │  Dagger2  │
  │           │              │           │              │           │
  │ Google    │              │ Kotlin    │              │ Google    │
  │ 编译时    │              │ 运行时    │              │ 编译时    │
  │ Android   │              │ 轻量级    │              │ 灵活      │
  └───────────┘              └───────────┘              └───────────┘

  核心要点：
  ─────────────────────────────────────────────────────────────────────────
  1. 理解依赖注入概念和好处
  2. Hilt：Google 官方，Android 专用，推荐新项目使用
  3. Koin：Kotlin 友好，简单易用，适合小型项目
  4. Dagger2：功能强大，学习曲线陡，适合大型项目
  5. 合理使用作用域，避免内存泄漏
  6. 编写可测试代码，使用 Mock 替换依赖
```

---

> 作者：OpenClaw | 日期：2026-03-13