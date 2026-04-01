# AndroidX 核心库详解

> 作者：OpenClaw | 日期：2026-03-09

---

## 目录

1. [概述](#1-概述)
2. [Lifecycle](#2-lifecycle)
3. [ViewModel](#3-viewmodel)
4. [LiveData](#4-livedata)
5. [Room](#5-room)
6. [WorkManager](#6-workmanager)
7. [Navigation](#7-navigation)
8. [DataStore](#8-datastore)
9. [Paging](#9-paging)
10. [ViewPager2](#10-viewpager2)
11. [Fragment](#11-fragment)
12. [核心库对比](#12-核心库对比)
13. [ConstraintLayout](#13-constraintlayout)
14. [常见问题](#14-常见问题)
15. [知识体系总结](#15-知识体系总结)

---

## 1. 概述

AndroidX 是 Android Jetpack 的核心组件库，提供了一系列向后兼容、独立更新的库，帮助开发者构建稳定、高效、可维护的应用。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AndroidX 核心库                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │    基础架构：                                                           │
  │    ─────────────────────────────────────────────────────────────────────── │
  │    AppCompat        兼容库，Material Design 支持                        │
  │    Core              基础 API 扩展                                      │
  │    Activity          Activity 扩展（ComponentActivity）                 │
  │    Fragment          Fragment 管理                                      │
  │                                                                         │
  │    架构组件：                                                           │
  │    ─────────────────────────────────────────────────────────────────────── │
  │    Lifecycle          生命周期感知                                      │
  │    ViewModel          视图模型，数据持久化                              │
  │    LiveData           可观察的数据持有者                                │
  │    Room               SQLite ORM                                        │
  │    DataStore          数据存储（替代 SharedPreferences）                │
  │    WorkManager        后台任务调度                                      │
  │    Navigation         导航组件                                          │
  │    Paging             分页加载                                          │
  │                                                                         │
  │    UI 组件：                                                            │
  │    ─────────────────────────────────────────────────────────────────────── │
  │    RecyclerView       列表视图                                          │
  │    ViewPager2         滑动页面                                          │
  │    SwipeRefreshLayout 下拉刷新                                          │
  │    ConstraintLayout   约束布局                                          │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Lifecycle

### 2.1 Lifecycle 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Lifecycle 定义                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  Lifecycle 是一个持有组件生命周期状态（如 Activity/Fragment）的类，
  允许其他对象观察这个状态。

  解决的问题：
  ─────────────────────────────────────────────────────────────────────────
  - 避免在 Activity/Fragment 中手动管理生命周期
  - 防止内存泄漏
  - 代码更清晰，职责分离

  核心类：
  ─────────────────────────────────────────────────────────────────────────
  - LifecycleOwner：生命周期拥有者（Activity/Fragment）
  - LifecycleObserver：生命周期观察者
  - Lifecycle：生命周期状态管理
```

### 2.2 生命周期状态和事件

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         生命周期状态                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  状态（State）：
  ─────────────────────────────────────────────────────────────────────────
  INITIALIZED → CREATED → STARTED → RESUMED → DESTROYED

  事件（Event）：
  ─────────────────────────────────────────────────────────────────────────
  ON_CREATE → ON_START → ON_RESUME → ON_PAUSE → ON_STOP → ON_DESTROY

  状态与事件对应：
  ─────────────────────────────────────────────────────────────────────────
  
       ON_CREATE          ON_START          ON_RESUME
          │                  │                  │
          ▼                  ▼                  ▼
  INITIALIZED ───────► CREATED ───────► STARTED ───────► RESUMED
                                               ▲                  │
                                               │                  │
                                          ON_PAUSE              │
                                               │                  │
                                               │             ON_DESTROY
                                          ON_STOP                  │
                                               │                  │
                                               ▼                  ▼
                                           STARTED ───────► CREATED ───────► DESTROYED

  State 关系：
  ─────────────────────────────────────────────────────────────────────────
  RESUMED >= STARTED >= CREATED >= INITIALIZED
```

### 2.3 Lifecycle 使用

```kotlin
// ==================== 方式1：实现 DefaultLifecycleObserver ====================
class MyObserver : DefaultLifecycleObserver {
    
    override fun onCreate(owner: LifecycleOwner) {
        // onCreate 时执行
    }
    
    override fun onStart(owner: LifecycleOwner) {
        // onStart 时执行
    }
    
    override fun onResume(owner: LifecycleOwner) {
        // onResume 时执行
    }
    
    override fun onPause(owner: LifecycleOwner) {
        // onPause 时执行
    }
    
    override fun onStop(owner: LifecycleOwner) {
        // onStop 时执行
    }
    
    override fun onDestroy(owner: LifecycleOwner) {
        // onDestroy 时执行
    }
}

// 注册观察者
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(MyObserver())
    }
}
```

```kotlin
// ==================== 方式2：使用 @OnLifecycleEvent 注解（已废弃）====================
@Deprecated("Use DefaultLifecycleObserver instead")
class MyObserver : LifecycleObserver {
    
    @OnLifecycleEvent(Lifecycle.Event.ON_CREATE)
    fun onCreate() {
        // onCreate 时执行
    }
    
    @OnLifecycleEvent(Lifecycle.Event.ON_START)
    fun onStart() {
        // onStart 时执行
    }
}
```

### 2.4 自定义 LifecycleOwner

```kotlin
// ==================== 自定义 LifecycleOwner ====================
class MyActivity : Activity(), LifecycleOwner {
    
    private val lifecycleRegistry = LifecycleRegistry(this)
    
    override val lifecycle: Lifecycle
        get() = lifecycleRegistry
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleRegistry.currentState = Lifecycle.State.CREATED
    }
    
    override fun onStart() {
        super.onStart()
        lifecycleRegistry.currentState = Lifecycle.State.STARTED
    }
    
    override fun onResume() {
        super.onResume()
        lifecycleRegistry.currentState = Lifecycle.State.RESUMED
    }
    
    override fun onDestroy() {
        super.onDestroy()
        lifecycleRegistry.currentState = Lifecycle.State.DESTROYED
    }
}
```

### 2.5 Lifecycle-aware 组件

```kotlin
// ==================== 生命周期感知的 LocationManager ====================
class LocationManager(private val context: Context) : DefaultLifecycleObserver {
    
    private var locationManager: LocationManager? = null
    
    override fun onStart(owner: LifecycleOwner) {
        // 开始获取位置
        startLocationUpdates()
    }
    
    override fun onStop(owner: LifecycleOwner) {
        // 停止获取位置，节省电量
        stopLocationUpdates()
    }
    
    private fun startLocationUpdates() {
        // 启动位置监听
    }
    
    private fun stopLocationUpdates() {
        // 停止位置监听
    }
}

// 使用
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycle.addObserver(LocationManager(this))
    }
}
```

---

## 3. ViewModel

### 3.1 ViewModel 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ViewModel 定义                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  ViewModel 是为 UI 组件准备数据的类，在配置更改（如屏幕旋转）后仍能保留数据。

  核心特点：
  ─────────────────────────────────────────────────────────────────────────
  1. 生命周期长于 Activity/Fragment（配置更改后存活）
  2. 不持有 View/Activity/Fragment 引用（避免内存泄漏）
  3. 与 UI 逻辑分离，便于测试

  生命周期：
  ─────────────────────────────────────────────────────────────────────────
  
  Activity 生命周期：       ViewModel 生命周期：
  ─────────────────────     ─────────────────────
  onCreate()                │
  onStart()                 │
  onResume()                │
  onPause()                 │  ViewModel 存活
  onStop()                  │  （配置更改后保留）
  onDestroy()               │
  ─── 配置更改 ───          │
  onCreate()                │
  ...                       │
  onDestroy()               │
  ─── 真正销毁 ───          ▼
                            onCleared()
```

### 3.2 ViewModel 使用

```kotlin
// ==================== 基本 ViewModel ====================
class UserViewModel : ViewModel() {
    
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    fun loadUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            // 加载数据
            _isLoading.value = false
        }
    }
    
    override fun onCleared() {
        super.onCleared()
        // 清理资源
    }
}

// ==================== Activity 中使用 ====================
class MainActivity : AppCompatActivity() {
    // 方式1：by viewModels()
    private val viewModel: UserViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        lifecycleScope.launch {
            viewModel.users.collect { users ->
                // 更新 UI
            }
        }
    }
}

// ==================== Fragment 中使用 ====================
class UserFragment : Fragment() {
    // 方式1：与 Activity 共享 ViewModel
    private val activityViewModel: UserViewModel by activityViewModels()
    
    // 方式2：Fragment 独有的 ViewModel
    private val fragmentViewModel: UserViewModel by viewModels()
    
    // 方式3：带 Factory 的 ViewModel
    private val viewModel: UserViewModel by viewModels {
        UserViewModelFactory(userId)
    }
}
```

### 3.3 ViewModel 传参

```kotlin
// ==================== 方式1：Factory ====================
class UserViewModelFactory(private val userId: String) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(UserViewModel::class.java)) {
            return UserViewModel(userId) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

class UserViewModel(private val userId: String) : ViewModel() {
    // ...
}

// 使用
val viewModel: UserViewModel by viewModels { UserViewModelFactory("123") }

// ==================== 方式2：SavedStateHandle ====================
class UserViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    
    // 从 SavedStateHandle 获取参数
    private val userId: String = savedStateHandle["userId"] ?: ""
    
    // 也可以保存数据
    fun saveData(data: String) {
        savedStateHandle["data"] = data
    }
    
    fun getData(): String? {
        return savedStateHandle["data"]
    }
}

// Fragment 导航时传参
val bundle = bundleOf("userId" to "123")
findNavController().navigate(R.id.userFragment, bundle)

// ==================== 方式3：Hilt 依赖注入 ====================
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    private val userId: String = savedStateHandle["userId"] ?: ""
}

// Activity 中使用
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()
}
```

### 3.4 ViewModelScope

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         viewModelScope                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  viewModelScope 是 ViewModel 的扩展属性，绑定到 ViewModel 的生命周期

  特点：
  ─────────────────────────────────────────────────────────────────────────
  - 自动在 onCleared() 时取消
  - 默认在主线程启动
  - 适合处理 UI 相关的异步任务

  使用：
  ─────────────────────────────────────────────────────────────────────────
```

```kotlin
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state.asStateFlow()
    
    fun loadData() {
        // viewModelScope 自动管理生命周期
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            
            repository.getData()
                .onSuccess { data ->
                    _state.update { it.copy(data = data, isLoading = false) }
                }
                .onFailure { error ->
                    _state.update { it.copy(error = error.message, isLoading = false) }
                }
        }
    }
    
    // 切换线程
    fun loadDataWithIo() {
        viewModelScope.launch(Dispatchers.IO) {
            // 在 IO 线程执行
            val data = repository.getDataFromDb()
            withContext(Dispatchers.Main) {
                // 切回主线程
                _state.update { it.copy(data = data) }
            }
        }
    }
}
```

---

## 4. LiveData

### 4.1 LiveData 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LiveData 定义                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  LiveData 是一种可观察的数据存储器类，具有生命周期感知能力。

  核心特点：
  ─────────────────────────────────────────────────────────────────────────
  1. 生命周期感知：只在活跃状态（STARTED/RESUMED）通知观察者
  2. 自动清理：销毁时自动移除观察者，避免内存泄漏
  3. 总是最新值：观察者变为活跃时，自动收到最新值
  4. 配置更改：屏幕旋转后恢复数据

  与 Flow 的区别：
  ─────────────────────────────────────────────────────────────────────────
  - LiveData：简单，自动生命周期管理，适合简单场景
  - Flow：灵活，丰富操作符，适合复杂场景
```

### 4.2 LiveData 使用

```kotlin
// ==================== 基本 LiveData ====================
class UserViewModel : ViewModel() {
    
    // 私有 MutableLiveData
    private val _users = MutableLiveData<List<User>>()
    // 公开 LiveData（不可变）
    val users: LiveData<List<User>> = _users
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    fun loadUsers() {
        _isLoading.value = true
        
        viewModelScope.launch {
            repository.getUsers()
                .onSuccess { users ->
                    _isLoading.value = false
                    _users.value = users  // setValue（主线程）
                }
                .onFailure {
                    _isLoading.value = false
                }
        }
    }
    
    fun loadUsersInBackground() {
        viewModelScope.launch(Dispatchers.IO) {
            val users = repository.getUsersFromDb()
            _users.postValue(users)  // postValue（任意线程）
        }
    }
}

// ==================== 观察 LiveData ====================
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 观察 LiveData
        viewModel.users.observe(this) { users ->
            // 只在活跃状态接收
            adapter.submitList(users)
        }
        
        viewModel.isLoading.observe(this) { isLoading ->
            binding.progressBar.isVisible = isLoading
        }
    }
}
```

### 4.3 LiveData 转换

```kotlin
// ==================== Transformations.map ====================
class UserViewModel : ViewModel() {
    private val _userId = MutableLiveData<String>()
    val userId: LiveData<String> = _userId
    
    // 转换：根据 userId 获取用户名
    val userName: LiveData<String> = Transformations.map(_userId) { id ->
        "User-$id"
    }
    
    // 转换：格式化显示
    val formattedId: LiveData<String> = _userId.map { id ->
        "ID: $id"
    }
}

// ==================== Transformations.switchMap ====================
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    
    private val _userId = MutableLiveData<String>()
    
    // switchMap：根据输入切换 LiveData 源
    val user: LiveData<User> = _userId.switchMap { id ->
        repository.getUserLiveData(id)
    }
    
    fun setUserId(id: String) {
        _userId.value = id
    }
}

// ==================== MediatorLiveData ====================
class FormViewModel : ViewModel() {
    
    val name = MutableLiveData<String>()
    val email = MutableLiveData<String>()
    
    // 合并多个 LiveData
    val isFormValid: MediatorLiveData<Boolean> = MediatorLiveData<Boolean>().apply {
        addSource(name) { checkFormValidity() }
        addSource(email) { checkFormValidity() }
    }
    
    private fun checkFormValidity() {
        val nameValid = !name.value.isNullOrBlank()
        val emailValid = !email.value.isNullOrBlank() && email.value!!.contains("@")
        isFormValid.value = nameValid && emailValid
    }
}
```

### 4.4 setValue vs postValue

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    setValue vs postValue                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  setValue(value)：
  ─────────────────────────────────────────────────────────────────────────
  - 必须在主线程调用
  - 同步设置值，立即通知观察者
  - 主线程调用时使用

  postValue(value)：
  ─────────────────────────────────────────────────────────────────────────
  - 可以在任意线程调用
  - 内部通过 Handler 切换到主线程
  - 多次调用只通知最后一次值
  - 子线程调用时使用

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  注意：postValue 多次调用，中间值可能丢失                               │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  // 子线程快速调用                                                       │
  │  liveData.postValue(1)                                                  │
  │  liveData.postValue(2)                                                  │
  │  liveData.postValue(3)                                                  │
  │  // 观察者可能只收到 3                                                   │
  │                                                                         │
  │  // 如果需要每次都收到，使用 setValue 切换线程                           │
  │  withContext(Dispatchers.Main) {                                        │
  │      liveData.value = 1                                                 │
  │      liveData.value = 2                                                 │
  │      liveData.value = 3                                                 │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Room

### 5.1 Room 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Room 定义                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  Room 是 SQLite 的 ORM（对象关系映射）库，提供抽象层让 SQLite 使用更简单

  核心组件：
  ─────────────────────────────────────────────────────────────────────────
  - Entity：数据库表对应的实体类
  - DAO（Data Access Object）：数据访问接口
  - Database：数据库持有者

  优势：
  ─────────────────────────────────────────────────────────────────────────
  - 编译时 SQL 语法检查
  - 类型安全
  - 支持 LiveData/Flow
  - 支持迁移
```

### 5.2 Entity 实体类

```kotlin
// ==================== 基本 Entity ====================
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    @ColumnInfo(name = "name")
    val name: String,
    
    @ColumnInfo(name = "email")
    val email: String,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis()
)

// ==================== 复合主键 ====================
@Entity(tableName = "user_roles", primaryKeys = ["user_id", "role_id"])
data class UserRole(
    @ColumnInfo(name = "user_id")
    val userId: Long,
    
    @ColumnInfo(name = "role_id")
    val roleId: Long
)

// ==================== 嵌入对象 ====================
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey
    val id: Long,
    
    val title: String,
    
    @Embedded
    val author: Author
)

data class Author(
    val authorName: String,
    val authorEmail: String
)

// ==================== 关联关系 ====================
@Entity
data class User(
    @PrimaryKey val id: Long,
    val name: String
)

@Entity(foreignKeys = [
    ForeignKey(
        entity = User::class,
        parentColumns = ["id"],
        childColumns = ["user_id"],
        onDelete = ForeignKey.CASCADE
    )
])
data class Order(
    @PrimaryKey val id: Long,
    val userId: Long,
    @ColumnInfo(name = "user_id") val userId: Long
)

// ==================== 类型转换器 ====================
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? {
        return value?.let { Date(it) }
    }
    
    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? {
        return date?.time
    }
    
    @TypeConverter
    fun fromString(value: String?): List<String> {
        return value?.split(",") ?: emptyList()
    }
    
    @TypeConverter
    fun listToString(list: List<String>?): String? {
        return list?.joinToString(",")
    }
}
```

### 5.3 DAO 数据访问

```kotlin
// ==================== DAO 接口 ====================
@Dao
interface UserDao {
    
    // 插入
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: User): Long
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(users: List<User>)
    
    // 更新
    @Update
    suspend fun update(user: User): Int
    
    // 删除
    @Delete
    suspend fun delete(user: User): Int
    
    @Query("DELETE FROM users WHERE id = :userId")
    suspend fun deleteById(userId: Long): Int
    
    @Query("DELETE FROM users")
    suspend fun deleteAll()
    
    // 查询
    @Query("SELECT * FROM users")
    suspend fun getAll(): List<User>
    
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getById(userId: Long): User?
    
    @Query("SELECT * FROM users WHERE name LIKE '%' || :keyword || '%'")
    suspend fun searchByName(keyword: String): List<User>
    
    // 返回 LiveData（自动更新）
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getAllLiveData(): LiveData<List<User>>
    
    // 返回 Flow（自动更新）
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getAllFlow(): Flow<List<User>>
    
    // 分页查询
    @Query("SELECT * FROM users LIMIT :limit OFFSET :offset")
    suspend fun getPage(limit: Int, offset: Int): List<User>
    
    // 统计
    @Query("SELECT COUNT(*) FROM users")
    suspend fun getCount(): Int
    
    // 事务
    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserWithOrders(userId: Long): UserWithOrders
}

// 关联查询
data class UserWithOrders(
    @Embedded val user: User,
    @Relation(
        parentColumn = "id",
        entityColumn = "user_id"
    )
    val orders: List<Order>
)
```

### 5.4 Database 数据库

```kotlin
// ==================== Database 定义 ====================
@Database(
    entities = [User::class, Order::class],
    version = 1,
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun orderDao(): OrderDao
}

// ==================== 单例获取 ====================
object DatabaseProvider {
    @Volatile
    private var INSTANCE: AppDatabase? = null
    
    fun getDatabase(context: Context): AppDatabase {
        return INSTANCE ?: synchronized(this) {
            INSTANCE ?: Room.databaseBuilder(
                context.applicationContext,
                AppDatabase::class.java,
                "app_database"
            )
                .addCallback(object : RoomDatabase.Callback() {
                    override fun onCreate(db: SupportSQLiteDatabase) {
                        // 数据库创建时初始化数据
                    }
                })
                .build()
                .also { INSTANCE = it }
        }
    }
}

// ==================== 使用 Hilt 注入 ====================
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
```

### 5.5 数据库迁移

```kotlin
// ==================== 迁移策略 ====================
@Database(
    entities = [User::class],
    version = 2  // 版本升级
)
abstract class AppDatabase : RoomDatabase()

// 迁移 1 → 2：添加 age 字段
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0")
    }
}

// 迁移 2 → 3：添加新表
val MIGRATION_2_3 = object : Migration(2, 3) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """.trimIndent())
    }
}

// 构建数据库时添加迁移
Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
    .build()

// 降级策略
Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
    .fallbackToDestructiveMigration()  // 无法迁移时销毁重建（谨慎使用）
    .fallbackToDestructiveMigrationOnDowngrade()  // 降级时销毁重建
    .build()
```

---

## 6. WorkManager

### 6.1 WorkManager 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WorkManager 定义                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  WorkManager 是 Jetpack 的后台任务调度库，保证任务在合适时机执行

  特点：
  ─────────────────────────────────────────────────────────────────────────
  1. 兼容性：Android 6.0+，自动选择 JobScheduler/AlarmManager
  2. 保证执行：重启后任务仍然存在
  3. 约束条件：网络、电量、充电等
  4. 任务链：顺序/并行执行多个任务

  适用场景：
  ─────────────────────────────────────────────────────────────────────────
  - 数据同步
  - 日志上传
  - 定期备份
  - 图片处理
```

### 6.2 Worker 定义

```kotlin
// ==================== 基本 Worker ====================
class SyncWorker(
    context: Context,
    params: WorkerParameters
) : Worker(context, params) {
    
    override fun doWork(): Result {
        return try {
            // 执行任务
            val data = inputData.getString("key")
            
            // 同步数据
            syncData()
            
            // 返回结果
            val outputData = workDataOf("result" to "success")
            Result.success(outputData)
        } catch (e: Exception) {
            Result.failure()
        }
    }
}

// ==================== CoroutineWorker（推荐）====================
class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        return try {
            // 可以使用协程
            val data = withContext(Dispatchers.IO) {
                fetchData()
            }
            
            // 显示进度（Android 11+）
            setProgress(workDataOf("progress" to 50))
            
            Result.success(workDataOf("data" to data))
        } catch (e: Exception) {
            Result.retry()  // 重试
            // 或 Result.failure()
        }
    }
}

// ==================== RxWorker（RxJava）====================
class RxSyncWorker(
    context: Context,
    params: WorkerParameters
) : RxWorker(context, params) {
    
    override fun createWork(): Single<Result> {
        return fetchData()
            .map { Result.success() }
            .onErrorReturnItem(Result.failure())
    }
}
```

### 6.3 任务调度

```kotlin
// ==================== 一次性任务 ====================
val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
    .setInputData(workDataOf("key" to "value"))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresCharging(true)
            .setRequiresBatteryNotLow(true)
            .setRequiresDeviceIdle(false)
            .build()
    )
    .setInitialDelay(10, TimeUnit.MINUTES)
    .setBackoffCriteria(
        BackoffPolicy.LINEAR,
        30,
        TimeUnit.SECONDS
    )
    .addTag("sync_work")
    .build()

WorkManager.getInstance(context).enqueue(workRequest)

// ==================== 周期性任务（最小 15 分钟）====================
val periodicWork = PeriodicWorkRequestBuilder<SyncWorker>(
    1, TimeUnit.HOURS,      // 重复间隔
    15, TimeUnit.MINUTES    // 灵活窗口
).build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork(
        "sync_work",
        ExistingPeriodicWorkPolicy.KEEP,  // 或 REPLACE
        periodicWork
    )

// ==================== 任务链 ====================
val workA = OneTimeWorkRequestBuilder<WorkA>().build()
val workB = OneTimeWorkRequestBuilder<WorkB>().build()
val workC = OneTimeWorkRequestBuilder<WorkC>().build()

// 顺序执行
WorkManager.getInstance(context)
    .beginWith(workA)
    .then(workB)
    .then(workC)
    .enqueue()

// 并行执行后合并
WorkManager.getInstance(context)
    .beginWith(listOf(workA, workB))
    .then(workC)
    .enqueue()

// ==================== 观察任务状态 ====================
WorkManager.getInstance(context)
    .getWorkInfoByIdLiveData(workRequest.id)
    .observe(this) { workInfo ->
        when (workInfo?.state) {
            WorkInfo.State.ENQUEUED -> { /* 等待中 */ }
            WorkInfo.State.RUNNING -> { /* 运行中 */ }
            WorkInfo.State.SUCCEEDED -> { 
                val result = workInfo.outputData.getString("result")
            }
            WorkInfo.State.FAILED -> { /* 失败 */ }
            WorkInfo.State.BLOCKED -> { /* 阻塞 */ }
            WorkInfo.State.CANCELLED -> { /* 取消 */ }
            null -> {}
        }
    }

// ==================== 取消任务 ====================
// 取消单个任务
WorkManager.getInstance(context).cancelWorkById(workId)

// 取消标签下所有任务
WorkManager.getInstance(context).cancelAllWorkByTag("sync_work")

// 取消唯一任务
WorkManager.getInstance(context).cancelUniqueWork("unique_work")
```

---

## 7. Navigation

### 7.1 Navigation 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Navigation 定义                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  Navigation 是 Jetpack 的导航组件，用于管理 Fragment 之间的导航

  核心组件：
  ─────────────────────────────────────────────────────────────────────────
  - NavController：导航控制器
  - NavHost：导航容器（NavHostFragment）
  - NavGraph：导航图（定义目的地和路径）
  - NavDestination：目的地（Fragment/Activity）

  功能：
  ─────────────────────────────────────────────────────────────────────────
  - Fragment 事务管理
  - 参数传递
  - 深度链接
  - 返回栈管理
  - 动画配置
```

### 7.2 Navigation Graph

```xml
<!-- res/navigation/nav_graph.xml -->
<?xml version="1.0" encoding="utf-8"?>
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">
    
    <!-- Home Fragment -->
    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment"
        android:label="Home"
        tools:layout="@layout/fragment_home">
        
        <!-- 参数定义 -->
        <argument
            android:name="userId"
            app:argType="string"
            app:nullable="true" />
        
        <!-- 动作 -->
        <action
            android:id="@+id/action_home_to_detail"
            app:destination="@id/detailFragment"
            app:enterAnim="@anim/slide_in_right"
            app:exitAnim="@anim/slide_out_left"
            app:popEnterAnim="@anim/slide_in_left"
            app:popExitAnim="@anim/slide_out_right" />
    </fragment>
    
    <!-- Detail Fragment -->
    <fragment
        android:id="@+id/detailFragment"
        android:name="com.example.DetailFragment"
        android:label="Detail"
        tools:layout="@layout/fragment_detail">
        
        <argument
            android:name="itemId"
            app:argType="string" />
    </fragment>
    
    <!-- Activity 目的地 -->
    <activity
        android:id="@+id/settingsActivity"
        android:name="com.example.SettingsActivity"
        android:label="Settings" />
    
    <!-- 深度链接 -->
    <deepLink app:uri="example.com/detail/{itemId}" />
    
</navigation>
```

### 7.3 NavController 使用

```kotlin
// ==================== 在 Activity 中设置 ====================
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // 获取 NavController
        val navController = findNavController(R.id.nav_host_fragment)
        
        // 设置 ActionBar
        setupActionBarWithNavController(navController)
        
        // 设置 BottomNavigationView
        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)
        bottomNav.setupWithNavController(navController)
    }
    
    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment)
        return navController.navigateUp() || super.onSupportNavigateUp()
    }
}

// ==================== 在 Fragment 中导航 ====================
class HomeFragment : Fragment() {
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // 导航到 Detail
        binding.btnDetail.setOnClickListener {
            // 方式1：使用 Action
            findNavController().navigate(R.id.action_home_to_detail)
            
            // 方式2：带参数
            findNavController().navigate(
                R.id.action_home_to                bundleOf("itemId" to "123")
            )
            
            // 方式3：使用 Directions（Safe Args）
            val direction = HomeFragmentDirections.actionHomeToDetail("123")
            findNavController().navigate(direction)
        }
    }
}

// ==================== 返回栈管理 ====================
// 返回
findNavController().navigateUp()

// 返回到指定目的地
findNavController().popBackStack(R.id.homeFragment, false)

// 清空返回栈到根
findNavController().popBackStack(R.id.homeFragment, true)
```

### 7.4 Safe Args

```gradle
// build.gradle
plugins {
    id("androidx.navigation.safeargs.kotlin")
}

dependencies {
    implementation("androidx.navigation:navigation-fragment-ktx:2.7.0")
    implementation("androidx.navigation:navigation-ui-ktx:2.7.0")
}
```

```kotlin
// 自动生成的 Directions 类
// HomeFragmentDirections.actionHomeToDetail(itemId: String)

// 发送方
val direction = HomeFragmentDirections.actionHomeToDetail("123")
findNavController().navigate(direction)

// 接收方（自动生成的 Args 类）
class DetailFragment : Fragment() {
    private val args: DetailFragmentArgs by navArgs()
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val itemId = args.itemId
    }
}
```

---

## 8. DataStore

### 8.1 DataStore 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DataStore 定义                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  DataStore 是 Jetpack 的数据存储库，用于替代 SharedPreferences

  特点：
  ─────────────────────────────────────────────────────────────────────────
  1. 异步 API（协程/Flow）
  2. 数据一致性保证
  3. 类型安全（Preferences DataStore / Proto DataStore）
  4. 无 ANR 风险

  与 SharedPreferences 对比：
  ─────────────────────────────────────────────────────────────────────────
  - SP：同步 API，可能阻塞，有 ANR 风险
  - DataStore：异步 API，不会阻塞
```

### 8.2 Preferences DataStore

```kotlin
// ==================== 创建 DataStore ====================
// 方式1：顶层属性
private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

// 方式2：依赖注入
@Module
@InstallIn(SingletonComponent::class)
object DataStoreModule {
    @Provides
    @Singleton
    fun provideDataStore(@ApplicationContext context: Context): DataStore<Preferences> {
        return context.dataStore
    }
}

// ==================== 读写数据 ====================
class SettingsRepository(private val dataStore: DataStore<Preferences>) {
    
    // 定义 Key
    private object PreferencesKeys {
        val DARK_MODE = booleanPreferencesKey("dark_mode")
        val USER_ID = stringPreferencesKey("user_id")
        val FONT_SIZE = intPreferencesKey("font_size")
    }
    
    // 读取数据
    val darkMode: Flow<Boolean> = dataStore.data
        .map { preferences -> preferences[PreferencesKeys.DARK_MODE] ?: false }
    
    val userId: Flow<String?> = dataStore.data
        .map { preferences -> preferences[PreferencesKeys.USER_ID] }
    
    // 读取多个值
    val settings: Flow<Settings> = dataStore.data
        .map { preferences ->
            Settings(
                darkMode = preferences[PreferencesKeys.DARK_MODE] ?: false,
                fontSize = preferences[PreferencesKeys.FONT_SIZE] ?: 14
            )
        }
    
    // 写入数据
    suspend fun setDarkMode(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferencesKeys.DARK_MODE] = enabled
        }
    }
    
    suspend fun setUserId(id: String) {
        dataStore.edit { preferences ->
            preferences[PreferencesKeys.USER_ID] = id
        }
    }
    
    // 删除数据
    suspend fun clearUserId() {
        dataStore.edit { preferences ->
            preferences.remove(PreferencesKeys.USER_ID)
        }
    }
    
    // 清空所有
    suspend fun clearAll() {
        dataStore.edit { preferences ->
            preferences.clear()
        }
    }
}

// ==================== 使用 ====================
class SettingsViewModel(private val repository: SettingsRepository) : ViewModel() {
    val darkMode: Flow<Boolean> = repository.darkMode
    
    fun setDarkMode(enabled: Boolean) {
        viewModelScope.launch {
            repository.setDarkMode(enabled)
        }
    }
}
```

### 8.3 Proto DataStore

```protobuf
// proto/settings.proto
syntax = "proto3";

option java_package = "com.example.datastore";
option java_multiple_files = true;

message Settings {
  bool dark_mode = 1;
  int32 font_size = 2;
  string user_id = 3;
}
```

```kotlin
// ==================== Serializer ====================
object SettingsSerializer : Serializer<Settings> {
    override val defaultValue: Settings = Settings.getDefaultInstance()
    
    override suspend fun readFrom(input: InputStream): Settings {
        return try {
            Settings.parseFrom(input)
        } catch (e: InvalidProtocolBufferException) {
            defaultValue
        }
    }
    
    override suspend fun writeTo(t: Settings, output: OutputStream) {
        t.writeTo(output)
    }
}

// ==================== 创建 Proto DataStore ====================
private val Context.settingsDataStore: DataStore<Settings> by dataStore(
    fileName = "settings.pb",
    serializer = SettingsSerializer
)

// ==================== 读写 ====================
class SettingsRepository(private val dataStore: DataStore<Settings>) {
    
    val settings: Flow<Settings> = dataStore.data
    
    suspend fun updateDarkMode(enabled: Boolean) {
        dataStore.updateData { currentSettings ->
            currentSettings.toBuilder()
                .setDarkMode(enabled)
                .build()
        }
    }
    
    suspend fun updateSettings(settings: Settings) {
        dataStore.updateData { settings }
    }
}
```

---

## 9. Paging

### 9.1 Paging 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Paging 定义                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  Paging 是 Jetpack 的分页加载库，用于高效加载和显示大量数据

  核心组件：
  ─────────────────────────────────────────────────────────────────────────
  - PagingSource：数据源（网络/数据库）
  - PagingData：分页数据容器
  - Pager：创建 PagingData 流
  - PagingDataAdapter：RecyclerView 适配器

  功能：
  ─────────────────────────────────────────────────────────────────────────
  - 自动分页加载
  - 加载状态管理
  - 错误处理和重试
  - 刷新和重载
```

### 9.2 PagingSource

```kotlin
// ==================== 网络数据源 ====================
class UserPagingSource(
    private val apiService: ApiService
) : PagingSource<Int, User>() {
    
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, User> {
        return try {
            val page = params.key ?: 1
            val pageSize = params.loadSize
            
            val response = apiService.getUsers(page, pageSize)
            
            LoadResult.Page(
                data = response.users,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.users.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }
    
    override fun getRefreshKey(state: PagingState<Int, User>): Int? {
        return state.anchorPosition?.let { anchorPosition ->
            state.closestPageToPosition(anchorPosition)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(anchorPosition)?.nextKey?.minus(1)
        }
    }
}

// ==================== Room 数据源 ====================
@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY id ASC")
    fun getAllPaging(): PagingSource<Int, User>
}
```

### 9.3 Pager 和 ViewModel

```kotlin
// ==================== Repository ====================
class UserRepository(private val apiService: ApiService, private val userDao: UserDao) {
    
    fun getUsersPaging(): Flow<PagingData<User>> {
        return Pager(
            config = PagingConfig(
                pageSize = 20,
                prefetchDistance = 5,
                enablePlaceholders = false,
                initialLoadSize = 40
            ),
            pagingSourceFactory = { UserPagingSource(apiService) }
        ).flow
    }
    
    fun getUsersFromDb(): Flow<PagingData<User>> {
        return Pager(
            config = PagingConfig(pageSize = 20),
            pagingSourceFactory = { userDao.getAllPaging() }
        ).flow
    }
}

// ==================== ViewModel ====================
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery
    
    // 使用 cachedIn 缓存分页数据
    val users: Flow<PagingData<User>> = repository.getUsersPaging()
        .cachedIn(viewModelScope)
    
    // 带搜索参数的分页
    fun searchUsers(query: String) {
        _searchQuery.value = query
    }
}

// ==================== 使用 combine 实现搜索 ====================
val users: Flow<PagingData<User>> = searchQuery
    .debounce(300)
    .flatMapLatest { query ->
        Pager(
            config = PagingConfig(pageSize = 20),
            pagingSourceFactory = { UserSearchPagingSource(apiService, query) }
        ).flow
    }
    .cachedIn(viewModelScope)
```

### 9.4 PagingDataAdapter

```kotlin
// ==================== DiffUtil ====================
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
        return oldItem.id == newItem.id
    }
    
    override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
        return oldItem == newItem
    }
}

// ==================== Adapter ====================
class UserPagingAdapter : PagingDataAdapter<User, UserViewHolder>(UserDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        return UserViewHolder(
            ItemUserBinding.inflate(
                LayoutInflater.from(parent.context),
                parent,
                false
            )
        )
    }
    
    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        val user = getItem(position)
        holder.bind(user)
    }
}

// ==================== Fragment 中使用 ====================
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()
    private lateinit var adapter: UserPagingAdapter
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        adapter = UserPagingAdapter()
        binding.recyclerView.adapter = adapter.withLoadStateHeaderAndFooter(
            header = LoadingStateAdapter { adapter.retry() },
            footer = LoadingStateAdapter { adapter.retry() }
        )
        
        // 收集分页数据
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.users.collectLatest { pagingData ->
                adapter.submitData(pagingData)
            }
        }
        
        // 监听加载状态
        adapter.addLoadStateListener { loadState ->
            when (loadState.refresh) {
                is LoadState.Loading -> {
                    binding.progressBar.isVisible = true
                }
                is LoadState.NotLoading -> {
                    binding.progressBar.isVisible = false
                }
                is LoadState.Error -> {
                    binding.progressBar.isVisible = false
                    val error = (loadState.refresh as LoadState.Error).error
                    Snackbar.make(binding.root, error.message ?: "Error", Snackbar.LENGTH_SHORT).show()
                }
            }
        }
    }
}
```

---

## 10. RecyclerView

### 10.1 RecyclerView 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RecyclerView 定义                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  RecyclerView 是用于显示大量数据列表的 UI 组件，提供高效的视图回收和复用机制

  核心特点：
  ─────────────────────────────────────────────────────────────────────────
  - ViewHolder 模式：强制复用，避免 findViewById
  - 四级缓存：mAttachedScrap → mCachedViews → mViewCacheExtension → mRecyclerPool
  - LayoutManager：解耦布局方式（线性、网格、瀑布流）
  - ItemDecoration：解耦分割线、间距
  - ItemAnimator：解耦动画

  与 ListView 对比：
  ─────────────────────────────────────────────────────────────────────────
  ┌──────────────────┬──────────────────┬───────────────────────────────────┐
  │      特性         │    ListView      │         RecyclerView              │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  ViewHolder      │  可选（非强制）   │  强制要求                         │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  缓存机制        │  1级（mActiveViews）│  4级缓存，更精细                  │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  局部刷新        │  麻烦             │  DiffUtil 高效局部刷新            │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  布局管理器      │  单一（垂直列表）  │  Linear/Grid/Staggered/GapHelper  │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  分割线          │  自行绘制          │  ItemDecoration 解耦              │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  动画            │  有限             │  ItemAnimator 完全自定义           │
  └──────────────────┴──────────────────┴───────────────────────────────────┘
```

### 10.2 缓存机制详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RecyclerView 缓存层级                                │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┐    屏幕上的 ViewHolder，快速复用（位置不变）
  │ mAttachedScrap  │    invalidate 后失效
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐    滑出屏幕的 ViewHolder，默认 2 个
  │  mCachedViews   │    可通过 setViewCacheSize 调整
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐    自定义缓存扩展（很少用）
  │ mViewCacheExt    │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐    RecyclerPool，共享池，默认 5 种类型，每种 10 个
  │  mRecyclerPool  │    用于 RecyclerView 嵌套场景
  └─────────────────┘

  复用流程：
  ─────────────────────────────────────────────────────────────────────────
  1. onBindViewHolder 复用：从 CachedViews 或 Pool 获取
  2. getViewForPosition -> tryGetViewHolderForPositionByDeadline
  3. 先查 CachedViews（按 position/id 匹配）
  4. 再查 Pool（按 viewType 匹配）
  5. 都没找到 → onCreateViewHolder
```

```kotlin
// 自定义 RecyclerPool
val pool = RecycledViewPool().apply {
    setMaxRecycledViews(VIEW_TYPE_NORMAL, 10)
    setMaxRecycledViews(VIEW_TYPE_HEADER, 5)
}
recyclerView.setRecycledViewPool(pool)

// 预设置缓存数量（默认2）
recyclerView.setItemViewCacheSize(20)
```

### 10.3 LayoutManager 优化

```kotlin
// 使用 hasStableIds 提供稳定 ID，帮助缓存
adapter.setHasStableIds(true)

// setHasFixedSize 避免主动请求 Layout（性能提升明显）
recyclerView.setHasFixedSize(true)

// 预取数量调整（Android 5.0+）
(recyclerView.layoutManager as LinearLayoutManager).apply {
    prefetchItemCount = 3  // 默认 2
}

// 额外布局空间
layoutManager.extraLayoutSpace = Resources.getSystem().displayMetrics.heightPixels
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LayoutManager 选择                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────────────────────────────────────────────────┐
  │ 场景            │  推荐                                                   │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ 普通列表        │  LinearLayoutManager                                    │
  │ 网格列表        │  GridLayoutManager（避免嵌套 RecyclerView）              │
  │ 瀑布流          │  StaggeredGridLayoutManager                              │
  │ 横向滚动        │  LinearLayoutManager.HORIZONTAL                         │
  └─────────────────┴─────────────────────────────────────────────────────────┘
```

### 10.4 Adapter 优化

```kotlin
// ❌ 错误：每次绑定都创建新对象
override fun onBindViewHolder(holder: VH, position: Int) {
    holder.textView.text = items[position].name
    holder.imageView.setImageBitmap(loadBitmap(items[position].imageRes))
}

// ✅ 正确：使用 Glide 等图片库，避免创建 Bitmap
override fun onBindViewHolder(holder: VH, position: Int) {
    val item = items[position]
    holder.textView.text = item.name
    Glide.with(holder.itemView.context)
        .load(item.imageUrl)
        .into(holder.imageView)
}
```

```kotlin
// ✅ 使用 DiffUtil 而非 notifyDataSetChanged
val diffResult = DiffUtil.calculateDiff(MyDiffCallback(oldList, newList))
diffResult.dispatchUpdatesTo(adapter)

// ✅ 多类型 ViewHolder 优化
override fun getItemViewType(position: Int): Int {
    return when {
        items[position].isHeader -> VIEW_TYPE_HEADER
        items[position].isFooter -> VIEW_TYPE_FOOTER
        else -> VIEW_TYPE_NORMAL
    }
}
```

```kotlin
// ✅ Payload 增量更新（避免完全重绑）
override fun onBindViewHolder(holder: VH, position: Int, payloads: MutableList<Any>) {
    if (payloads.isEmpty()) {
        super.onBindViewHolder(holder, position, payloads)
    } else {
        // 只更新变化的部分
        val payload = payloads[0] as String
        when (payload) {
            "NAME_CHANGED" -> holder.updateName(items[position].name)
            "AVATAR_CHANGED" -> holder.updateAvatar(items[position].avatarUrl)
        }
    }
}

// ✅ 发送 Payload
adapter.notifyItemChanged(position, "NAME_CHANGED")
```

### 10.5 刷新优化

```kotlin
// ❌ 全量刷新（性能差）
adapter.notifyDataSetChanged()

// ✅ 局部刷新
adapter.notifyItemChanged(position)
adapter.notifyItemRangeChanged(positionStart, itemCount)
adapter.notifyItemInserted(position)
adapter.notifyItemRemoved(position)

// ✅ 使用 AsyncListDiffer（自动后台线程计算 Diff）
val differ = AsyncListDiffer(this, DiffCallback())
differ.submitList(newList)
```

### 10.6 图片加载与复用

```kotlin
// Glide 配合 RecyclerView
Glide.with(context)
    .load(url)
    .override(200, 200)  // 指定尺寸避免加载原图
    .centerCrop()
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .into(holder.imageView)

// ViewHolder 回收时取消旧请求，防止图片错位
override fun onViewRecycled(holder: VH) {
    super.onViewRecycled(holder)
    Glide.with(holder.itemView.context).clear(holder.imageView)
}
```

### 10.7 嵌套 RecyclerView 优化

```kotlin
// 禁止嵌套 RecyclerView 自行滚动
nestedRecyclerView.isNestedScrollingEnabled = false

// ✅ 使用 SharedViewPool 共享缓存
val sharedPool = RecycledViewPool()
horizontalRecyclerView.setRecycledViewPool(sharedPool)
verticalRecyclerView.setRecycledViewPool(sharedPool)
```

### 10.8 ItemDecoration 优化

```kotlin
// ❌ 过度绘制：在 onDraw 中绘制整个区域
// ✅ 只绘制必要区域
class DividerDecoration(private val divider: Drawable) : RecyclerView.ItemDecoration() {
    override fun onDrawOver(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        for (i in 0 until parent.childCount) {
            val child = parent.getChildAt(i)
            // 只在必要位置绘制分割线
        }
    }
    
    override fun getItemOffsets(outRect: Rect, view: View, parent: RecyclerView, state: RecyclerView.State) {
        outRect.set(0, 0, 0, divider.intrinsicHeight)
    }
}
```

### 10.9 性能检测工具

```bash
# 开启 RecyclerView 调试日志
adb shell setprop log.tag.RecyclerView VERBOSE

# Systrace 分析卡顿
python -m systrace -a com.example.app -o trace.html
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    优化 Checklist                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  基础优化：
  ─────────────────────────────────────────────────────────────────────────
  ✅ setHasFixedSize(true) — 避免主动请求 Layout
  ✅ setHasStableIds(true) — 帮助 DiffUtil 精确匹配
  ✅ DiffUtil 替代 notifyDataSetChanged
  ✅ onBindViewHolder 中避免创建对象
  ✅ 使用 ViewPool 共享缓存

  进阶优化：
  ─────────────────────────────────────────────────────────────────────────
  ✅ Payload 增量更新
  ✅ AsyncListDiffer 后台 Diff
  ✅ 合理设置缓存池大小
  ✅ Glide 替代直接加载图片
  ✅ onViewRecycled 取消旧请求
  ✅ setNestedScrollingEnabled(false)（嵌套场景）
```

### 10.10 面试高频追问

```
Q1: RecyclerView 与 ListView 区别？
─────────────────────────────────────────────────────────────────────────
A: 
   - RecyclerView 强制 ViewHolder，ListView 可选
   - RecyclerView 4级缓存更精细，ListView 只有 1级
   - RecyclerView 局部刷新更高效（DiffUtil）
   - RecyclerView 解耦更好（LayoutManager、ItemDecoration、Animator）

Q2: 为什么 notifyDataSetChanged 性能差？
─────────────────────────────────────────────────────────────────────────
A: 触发完整 rebind 和重排，无法利用缓存

Q3: RecyclerView 嵌套 RecyclerView 怎么优化？
─────────────────────────────────────────────────────────────────────────
A: 
   - setNestedScrollingEnabled(false)
   - 使用 SharedViewPool 共享缓存池

Q4: 滑动了 1000 条数据，缓存机制如何工作？
─────────────────────────────────────────────────────────────────────────
A:
   - 屏幕内 ViewHolder 在 mAttachedScrap
   - 滑出屏幕的进入 mCachedViews（默认 2 个）
   - 超过 2 个的进入 mRecyclerPool（按 viewType）
   - CachedViews 是按 position 匹配的，Pool 是按 viewType 匹配

Q5: 如何实现 DiffUtil 的局部刷新？
─────────────────────────────────────────────────────────────────────────
A: 重写 getChangePayload() 返回 payload 对象，onBindViewHolder 接收并只更新变化部分
```

---

## 11. ViewPager2

### 10.1 ViewPager2 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ViewPager2 定义                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  ViewPager2 是用于水平或垂直滑动切换页面的组件，基于 RecyclerView 实现

  与 ViewPager 的区别：
  ─────────────────────────────────────────────────────────────────────────
  ┌──────────────────┬──────────────────┬───────────────────────────────────┐
  │      特性         │    ViewPager     │         ViewPager2                │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  实现基础         │  自定义 ViewGroup │  RecyclerView                    │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  垂直滑动         │  ❌ 不支持        │  ✅ 支持                          │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  RTL 支持         │  ❌ 不支持        │  ✅ 支持                          │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  notifyDataSetChanged │  ❌ 有问题   │  ✅ 完美支持                      │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  DiffUtil         │  ❌ 不支持        │  ✅ 支持                          │
  ├──────────────────┼──────────────────┼───────────────────────────────────┤
  │  FakeDrag         │  ❌ 不支持        │  ✅ 支持（模拟拖拽）              │
  └──────────────────┴──────────────────┴───────────────────────────────────┘

  核心优势：
  ─────────────────────────────────────────────────────────────────────────
  1. 基于 RecyclerView，性能更好
  2. 支持垂直滑动
  3. 支持 RTL 布局
  4. 支持 DiffUtil 高效更新
  5. 解决 ViewPager 的 notifyDataSetChange 问题
```

### 10.2 基本使用

```xml
<!-- ==================== XML 布局 ==================== -->
<androidx.viewpager2.widget.ViewPager2
    android:id="@+id/viewPager"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

```kotlin
// ==================== FragmentStateAdapter ====================
class ViewPagerAdapter(
    activity: FragmentActivity
) : FragmentStateAdapter(activity) {
    
    private val fragments = listOf(
        HomeFragment(),
        DiscoverFragment(),
        ProfileFragment()
    )
    
    override fun getItemCount(): Int = fragments.size
    
    override fun createFragment(position: Int): Fragment {
        return fragments[position]
    }
}

// ==================== Activity 中使用 ====================
class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // 设置 Adapter
        binding.viewPager.adapter = ViewPagerAdapter(this)
        
        // 设置初始页面
        binding.viewPager.currentItem = 0
        
        // 设置离屏页面限制（预加载）
        binding.viewPager.offscreenPageLimit = 1
    }
}
```

### 10.3 页面切换监听

```kotlin
// ==================== 页面切换回调 ====================
binding.viewPager.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
    
    override fun onPageSelected(position: Int) {
        // 页面被选中
        Log.d("ViewPager", "Selected: $position")
    }
    
    override fun onPageScrolled(
        position: Int,
        positionOffset: Float,
        positionOffsetPixels: Int
    ) {
        // 页面滚动中
        // positionOffset: 0.0 ~ 1.0，表示滚动进度
    }
    
    override fun onPageScrollStateChanged(state: Int) {
        // 滚动状态变化
        when (state) {
            ViewPager2.SCROLL_STATE_IDLE -> { /* 空闲 */ }
            ViewPager2.SCROLL_STATE_DRAGGING -> { /* 拖拽中 */ }
            ViewPager2.SCROLL_STATE_SETTLING -> { /* 惯性滚动 */ }
        }
    }
})

// 注意：销毁时注销（避免内存泄漏）
override fun onDestroy() {
    super.onDestroy()
    binding.viewPager.unregisterOnPageChangeCallback(callback)
}
```

### 10.4 与 TabLayout 联动

```kotlin
// ==================== 方式1：TabLayoutMediator ====================
val tabTitles = listOf("首页", "发现", "我的")

TabLayoutMediator(binding.tabLayout, binding.viewPager) { tab, position ->
    tab.text = tabTitles[position]
}.attach()

// ==================== 方式2：带图标的 Tab ====================
val tabIcons = listOf(
    R.drawable.ic_home,
    R.drawable.ic_discover,
    R.drawable.ic_profile
)

TabLayoutMediator(binding.tabLayout, binding.viewPager) { tab, position ->
    tab.text = tabTitles[position]
    tab.icon = ContextCompat.getDrawable(this, tabIcons[position])
}.attach()

// ==================== 方式3：自定义 TabView ====================
TabLayoutMediator(binding.tabLayout, binding.viewPager) { tab, position ->
    val customView = LayoutInflater.from(this)
        .inflate(R.layout.custom_tab, null)
    customView.findViewById<TextView>(R.id.tvTitle).text = tabTitles[position]
    tab.customView = customView
}.attach()
```

### 10.5 垂直滑动

```kotlin
// ==================== XML 设置 ====================
<androidx.viewpager2.widget.ViewPager2
    android:id="@+id/viewPager"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical" />

// ==================== 代码设置 ====================
binding.viewPager.orientation = ViewPager2.ORIENTATION_VERTICAL  // 垂直
binding.viewPager.orientation = ViewPager2.ORIENTATION_HORIZONTAL  // 水平（默认）
```

### 10.6 禁用滑动

```kotlin
// ==================== 禁用用户滑动 ====================
binding.viewPager.isUserInputEnabled = false  // 禁用滑动
binding.viewPager.isUserInputEnabled = true   // 启用滑动

// 使用场景：引导页最后一页禁止返回
```

### 10.7 动态更新数据

```kotlin
// ==================== FragmentStateAdapter 动态更新 ====================
class DynamicPagerAdapter(
    fragment: Fragment
) : FragmentStateAdapter(fragment) {
    
    private var items: List<PageItem> = emptyList()
    
    fun submitList(newItems: List<PageItem>) {
        val oldList = items
        items = newItems
        // 自动使用 DiffUtil
        notifyItemRangeChanged(0, newItems.size)
    }
    
    override fun getItemCount(): Int = items.size
    
    override fun createFragment(position: Int): Fragment {
        return PageFragment.newInstance(items[position])
    }
}

// 注意：ViewPager2 基于 RecyclerView，支持 notifyItemChanged 等
```

### 10.8 ViewPager2 + Fragment 生命周期

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ViewPager2 Fragment 生命周期                             │
└─────────────────────────────────────────────────────────────────────────────┘

  默认行为（offscreenPageLimit = OFFSCREEN_PAGE_LIMIT_DEFAULT = -1）：
  ─────────────────────────────────────────────────────────────────────────
  - 只保留当前可见的 Fragment
  - 滑走后 Fragment 会被销毁
  - 滑回来会重新创建

  设置 offscreenPageLimit = 1：
  ─────────────────────────────────────────────────────────────────────────
  - 当前页 + 左右各 1 页会被保留
  - 滑走不会销毁（在限制范围内）
  - 超出范围的 Fragment 会被销毁

  生命周期流程：
  ─────────────────────────────────────────────────────────────────────────
  
  滑入页面：
  Fragment → onAttach → onCreate → onCreateView → onViewCreated
          → onStart → onResume

  滑出页面（offscreenPageLimit 外）：
  Fragment → onPause → onStop → onDestroyView

  注意：FragmentStateAdapter 使用 BEHAVIOR_RESUME_ONLY_CURRENT_FRAGMENT 时：
  - 只有当前页会执行 onResume
  - 其他页保持在 onStart 状态
```

```kotlin
// ==================== BEHAVIOR_RESUME_ONLY_CURRENT_FRAGMENT ====================
class ViewPagerAdapter(
    activity: FragmentActivity
) : FragmentStateAdapter(activity) {
    
    // 默认行为：只有当前页处于 RESUMED 状态
    // 其他页处于 STARTED 状态（不会 onResume）
    
    override fun getItemCount(): Int = 3
    
    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> HomeFragment()
            1 -> DiscoverFragment()
            else -> ProfileFragment()
        }
    }
}

// Fragment 中处理可见性
class HomeFragment : Fragment() {
    
    override fun onResume() {
        super.onResume()
        // 页面可见时执行
        loadData()
    }
    
    override fun onPause() {
        super.onPause()
        // 页面不可见时暂停
        pauseVideo()
    }
}
```

### 10.9 Transformer 动画

```kotlin
// ==================== 内置 Transformer ====================
// 页面缩放效果
binding.viewPager.setPageTransformer(ZoomOutPageTransformer())

// 深度效果
binding.viewPager.setPageTransformer(DepthPageTransformer())

// ==================== 自定义 Transformer ====================
class ZoomOutPageTransformer : ViewPager2.PageTransformer {
    
    private val minScale = 0.85f
    private val minAlpha = 0.5f
    
    override fun transformPage(page: View, position: Float) {
        val pageWidth = page.width
        val pageHeight = page.height
        
        when {
            position < -1 -> {  // [-Infinity,-1)
                page.alpha = 0f
            }
            position <= 1 -> {  // [-1,1]
                val scaleFactor = max(minScale, 1 - Math.abs(position))
                val vertMargin = pageHeight * (1 - scaleFactor) / 2
                val horzMargin = pageWidth * (1 - scaleFactor) / 2
                
                page.translationX = if (position < 0) {
                    horzMargin - vertMargin / 2
                } else {
                    horzMargin + vertMargin / 2
                }
                
                page.scaleX = scaleFactor
                page.scaleY = scaleFactor
                page.alpha = minAlpha + (scaleFactor - minScale) / (1 - minScale) * (1 - minAlpha)
            }
            else -> {  // (1,+Infinity]
                page.alpha = 0f
            }
        }
    }
}

// ==================== 3D 翻转效果 ====================
class CubeTransformer : ViewPager2.PageTransformer {
    
    override fun transformPage(page: View, position: Float) {
        page.cameraDistance = 20000f
        
        when {
            position < -1 -> {
                page.alpha = 0f
            }
            position <= 0 -> {
                page.alpha = 1f
                page.pivotX = page.width.toFloat()
                page.rotationY = 90 * position
            }
            position <= 1 -> {
                page.alpha = 1f
                page.pivotX = 0f
                page.rotationY = 90 * position
            }
            else -> {
                page.alpha = 0f
            }
        }
    }
}
```

### 10.10 ViewPager2 常见问题

```
Q1: ViewPager2 中 Fragment 如何刷新数据？
─────────────────────────────────────────────────────────────────────────
A: 
   1. 使用 LiveData/Flow 自动刷新
   2. Fragment 实现 Lazy 初始化，在 onResume 加载数据
   3. 使用 FragmentResultListener 传递数据

Q2: 如何实现无限轮播？
─────────────────────────────────────────────────────────────────────────
A: 方案：getItemCount 返回 Int.MAX_VALUE，position % realCount 取模

   override fun getItemCount(): Int = Int.MAX_VALUE
   
   override fun createFragment(position: Int): Fragment {
       val realPosition = position % realCount
       return fragments[realPosition]
   }
   
   // 初始位置设置为中间
   viewPager.currentItem = Int.MAX_VALUE / 2

Q3: 如何禁止预加载？
─────────────────────────────────────────────────────────────────────────
A: ViewPager2 无法完全禁止预加载，最小 offscreenPageLimit = 1
   但可以使用懒加载 Fragment 来延迟加载数据

Q4: FragmentStateAdapter vs FragmentPagerAdapter？
─────────────────────────────────────────────────────────────────────────
A: 
   - FragmentPagerAdapter（已废弃）：所有 Fragment 保留在内存
   - FragmentStateAdapter（推荐）：只保留当前页，自动回收
```

---

## 11. Fragment

### 11.1 Fragment 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Fragment 定义                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  Fragment 是一种可以嵌入 Activity 中的 UI 片段，拥有自己的布局和生命周期

  核心特点：
  ─────────────────────────────────────────────────────────────────────────
  1. 模块化：将 UI 和逻辑拆分为独立模块
  2. 可复用：同一 Fragment 可用于多个 Activity
  3. 灵活组合：动态组合多个 Fragment
  4. 生命周期：与 Activity 生命周期关联

  使用场景：
  ─────────────────────────────────────────────────────────────────────────
  - 底部导航栏（多个 Tab）
  - 主从布局（手机单列，平板双列）
  - ViewPager 页面
  - Dialog 弹窗
```

### 11.2 Fragment 生命周期

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Fragment 生命周期                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  完整生命周期：
  ─────────────────────────────────────────────────────────────────────────
  
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  onAttach()           Fragment 与 Activity 关联                         │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onCreate()           Fragment 创建                                     │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onCreateView()       创建 Fragment 视图                                │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onViewCreated()      视图创建完成                                      │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onViewStateRestored() 恢复视图状态                                     │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onStart()            Fragment 可见                                     │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onResume()           Fragment 可见且可交互                             │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onPause()            Fragment 不再可交互                               │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onStop()             Fragment 不再可见                                 │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onDestroyView()      销毁 Fragment 视图                                │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onDestroy()          Fragment 销毁                                     │
  │       │                                                                 │
  │       ▼                                                                 │
  │  onDetach()           Fragment 与 Activity 解除关联                     │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  与 Activity 生命周期的关系：
  ─────────────────────────────────────────────────────────────────────────
  
  Activity              Fragment
  ─────────────────────────────────────
  onCreate()      →     onAttach()
                       → onCreate()
                       → onCreateView()
                       → onViewCreated()
                       → onViewStateRestored()
  
  onStart()       →     onStart()
  
  onResume()      →     onResume()
  
  onPause()       →     onPause()
  
  onStop()        →     onStop()
  
  onDestroy()     →     onDestroyView()
                       → onDestroy()
                       → onDetach()

  Fragment View 生命周期（单独管理）：
  ─────────────────────────────────────────────────────────────────────────
  - addToBackStack 后返回：只走 onDestroyView，Fragment 实例保留
  - 再次显示：重新走 onCreateView → onViewCreated
  - 这就是 View 的重建，需要注意状态保存和恢复
```

### 11.3 创建 Fragment

```kotlin
// ==================== 基本 Fragment ====================
class HomeFragment : Fragment(R.layout.fragment_home) {
    
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    
    // 方式1：使用 viewBinding delegate（推荐）
    // class HomeFragment : Fragment() {
    //     private val binding by viewBinding(FragmentHomeBinding::bind)
    // }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentHomeBinding.bind(view)
        
        // 初始化视图
        binding.textView.text = "Hello"
        
        // 设置点击事件
        binding.button.setOnClickListener {
            // 处理点击
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // 避免内存泄漏
    }
}

// ==================== 带参数的 Fragment ====================
class DetailFragment : Fragment(R.layout.fragment_detail) {
    
    private val args: DetailFragmentArgs by navArgs()
    
    // 或手动获取参数
    private var itemId: String? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 获取参数
        itemId = arguments?.getString("itemId")
    }
    
    companion object {
        fun newInstance(itemId: String): DetailFragment {
            return DetailFragment().apply {
                arguments = bundleOf("itemId" to itemId)
            }
        }
    }
}
```

### 11.4 FragmentManager 和事务

```kotlin
// ==================== 获取 FragmentManager ====================
// Activity 中
val fragmentManager = supportFragmentManager

// Fragment 中获取子 Fragment 的 Manager
val childFragmentManager = childFragmentManager

// Fragment 中获取 Activity 的 Manager
val parentFragmentManager = parentFragmentManager

// ==================== FragmentTransaction ====================
class MainActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 方式1：使用 supportFragmentManager
        supportFragmentManager.commit {
            replace(R.id.container, HomeFragment())
            addToBackStack("home")
        }
        
        // 方式2：传统方式
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, HomeFragment())
            .addToBackStack("home")
            .commit()
    }
}

// ==================== 常用事务操作 ====================
// 添加
supportFragmentManager.commit {
    add(R.id.container, HomeFragment())
}

// 替换
supportFragmentManager.commit {
    replace(R.id.container, HomeFragment())
}

// 移除
supportFragmentManager.commit {
    remove(homeFragment)
}

// 隐藏（不销毁视图）
supportFragmentManager.commit {
    hide(homeFragment)
}

// 显示
supportFragmentManager.commit {
    show(homeFragment)
}

// 添加到返回栈
supportFragmentManager.commit {
    replace(R.id.container, HomeFragment())
    addToBackStack(null)  // null 或自定义名称
}

// ==================== 事务提交方式 ====================
// commit()：异步提交，在主线程队列中排队
supportFragmentManager.commit { /* ... */ }

// commitNow()：同步提交，立即执行
supportFragmentManager.commitNow { /* ... */ }

// commitAllowingStateLoss()：允许状态丢失（Activity 重建后）
supportFragmentManager.commit(allowStateLoss = true) { /* ... */ }

// ==================== 动画 ====================
supportFragmentManager.commit {
    setCustomAnimations(
        R.anim.slide_in_right,   // enter
        R.anim.slide_out_left,   // exit
        R.anim.slide_in_left,    // popEnter
        R.anim.slide_out_right   // popExit
    )
    replace(R.id.container, HomeFragment())
    addToBackStack(null)
}
```

### 11.5 Fragment 返回栈

```kotlin
// ==================== 返回栈管理 ====================
// 添加到返回栈
supportFragmentManager.commit {
    replace(R.id.container, DetailFragment())
    addToBackStack("detail")  // 可选名称
}

// 处理返回键
override fun onBackPressed() {
    if (supportFragmentManager.backStackEntryCount > 0) {
        supportFragmentManager.popBackStack()
    } else {
        super.onBackPressed()
    }
}

// 使用 OnBackPressedDispatcher（推荐）
class MainActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (supportFragmentManager.backStackEntryCount > 0) {
                    supportFragmentManager.popBackStack()
                } else {
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                }
            }
        })
    }
}

// ==================== popBackStack 操作 ====================
// 弹出栈顶
supportFragmentManager.popBackStack()

// 弹出到指定 Tag
supportFragmentManager.popBackStack("home", 0)  // 弹出到 home（不包含 home）
supportFragmentManager.popBackStack("home", FragmentManager.POP_BACK_STACK_INCLUSIVE)  // 包含 home

// 弹出到指定 ID
supportFragmentManager.popBackStack(transactionId, 0)

// 弹出所有
supportFragmentManager.popBackStack(null, FragmentManager.POP_BACK_STACK_INCLUSIVE)

// ==================== 监听返回栈变化 ====================
supportFragmentManager.addOnBackStackChangedListener {
    val count = supportFragmentManager.backStackEntryCount
    Log.d("BackStack", "Count: $count")
}
```

### 11.6 Fragment 通信

```kotlin
// ==================== 方式1：ViewModel 共享 ====================
// Activity 和 Fragment 共享 ViewModel
class SharedViewModel : ViewModel() {
    private val _selectedItem = MutableStateFlow<Item?>(null)
    val selectedItem: StateFlow<Item?> = _selectedItem
    
    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Fragment 中
class ListFragment : Fragment() {
    // 与 Activity 共享
    private val viewModel: SharedViewModel by activityViewModels()
}

class DetailFragment : Fragment() {
    private val viewModel: SharedViewModel by activityViewModels()
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.selectedItem.collect { item ->
                // 响应选中变化
            }
        }
    }
}

// ==================== 方式2：Fragment Result API（推荐）====================
// 发送方
button.setOnClickListener {
    setFragmentResult("requestKey", bundleOf("data" to "value"))
}

// 接收方
setFragmentResultListener("requestKey") { requestKey, bundle ->
    val data = bundle.getString("data")
}

// Fragment 之间通信
// Fragment A 发送
parentFragmentManager.setFragmentResult("userSelected", bundleOf("userId" to "123"))

// Fragment B 接收
parentFragmentManager.setFragmentResultListener("userSelected", viewLifecycleOwner) { _, bundle ->
    val userId = bundle.getString("userId")
}

// ==================== 方式3：接口回调（传统方式）====================
interface OnItemSelectedListener {
    fun onItemSelected(item: Item)
}

class ListFragment : Fragment() {
    private var listener: OnItemSelectedListener? = null
    
    override fun onAttach(context: Context) {
        super.onAttach(context)
        listener = context as? OnItemSelectedListener
    }
    
    override fun onDetach() {
        super.onDetach()
        listener = null
    }
    
    private fun onItemClick(item: Item) {
        listener?.onItemSelected(item)
    }
}

class MainActivity : AppCompatActivity(), OnItemSelectedListener {
    override fun onItemSelected(item: Item) {
        // 处理选中
    }
}

// ==================== 方式4：Activity 方法调用 ====================
// 不推荐，耦合度高
class MyFragment : Fragment() {
    private fun doSomething() {
        (activity as? MainActivity)?.someMethod()
    }
}
```

### 11.7 Fragment 懒加载

```kotlin
// ==================== 方式1：Fragment.setMaxLifecycle（推荐）====================
// ViewPager2 + FragmentStateAdapter 自动实现
// 只有当前可见的 Fragment 会执行 onResume

class LazyFragment : Fragment() {
    
    private var isLoaded = false
    
    override fun onResume() {
        super.onResume()
        if (!isLoaded) {
            isLoaded = true
            loadData()
        }
    }
    
    private fun loadData() {
        // 只加载一次
    }
}

// ==================== 方式2：使用 Lifecycle 观察可见性 ====================
class LazyFragment : Fragment() {
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        viewLifecycleOwner.lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onResume(owner: LifecycleOwner) {
                // 页面可见时加载
                loadData()
            }
            
            override fun onPause(owner: LifecycleOwner) {
                // 页面不可见时暂停
            }
        })
    }
}

// ==================== 方式3：自定义懒加载属性 ====================
fun Fragment.doWhenResumed(block: () -> Unit) {
    viewLifecycleOwner.lifecycleScope.launch {
        viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.RESUMED) {
            block()
        }
    }
}

// 使用
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        doWhenResumed {
            // 只有在 RESUMED 状态才执行
            loadData()
        }
    }
}
```

### 11.8 DialogFragment

```kotlin
// ==================== 基本 DialogFragment ====================
class MyDialogFragment : DialogFragment() {
    
    private var _binding: DialogMyBinding? = null
    private val binding get() = _binding!!
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = DialogMyBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // 设置对话框样式
        dialog?.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        dialog?.window?.setLayout(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.WRAP_CONTENT
        )
        
        binding.btnCancel.setOnClickListener { dismiss() }
        binding.btnConfirm.setOnClickListener {
            // 返回结果
            setFragmentResult("dialogResult", bundleOf("confirmed" to true))
            dismiss()
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

// 显示对话框
MyDialogFragment().show(parentFragmentManager, "my_dialog")

// ==================== 全屏 Dialog ====================
class FullScreenDialog : DialogFragment() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setStyle(STYLE_NORMAL, R.style.FullScreenDialog)
    }
    
    override fun onCreateView(...): View {
        return FragmentFullScreenBinding.inflate(inflater, container, false).root
    }
}

// styles.xml
<style name="FullScreenDialog" parent="Theme.MaterialComponents.Light.Dialog">
    <item name="android:windowIsFloating">false</item>
    <item name="android:windowBackground">@android:color/white</item>
    <item name="android:statusBarColor">@color/status_bar</item>
</style>

// ==================== 底部弹窗 BottomSheetDialogFragment ====================
class MyBottomSheet : BottomSheetDialogFragment() {
    
    override fun onCreateView(...): View {
        return BottomSheetMyBinding.inflate(inflater, container, false).root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        // 设置展开高度
        (view.parent as View).layoutParams.height = ViewGroup.LayoutParams.MATCH_PARENT
    }
}
```

### 11.9 Fragment 状态保存与恢复

```kotlin
// ==================== 保存状态 ====================
class MyFragment : Fragment() {
    
    private var myData: String? = null
    
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("myData", myData)
    }
    
    override fun onViewStateRestored(savedInstanceState: Bundle?) {
        super.onViewStateRestored(savedInstanceState)
        myData = savedInstanceState?.getString("myData")
    }
}

// ==================== 使用 SavedStateHandle（推荐）====================
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    
    var myData: String?
        get() = savedStateHandle["myData"]
        set(value) {
            savedStateHandle["myData"] = value
        }
}

// ==================== 配置更改时保留 Fragment ====================
// 在 Activity 的 onCreate 中检查 savedInstanceState
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    
    if (savedInstanceState == null) {
        // 首次创建
        supportFragmentManager.commit {
            replace(R.id.container, HomeFragment())
        }
    }
    // 否则 FragmentManager 会自动恢复 Fragment
}
```

### 11.10 Fragment 常见问题

```
Q1: Fragment 重叠问题？
─────────────────────────────────────────────────────────────────────────
A: 原因：Activity 重建时 Fragment 自动恢复，又手动添加了一次
   解决：
   1. 在 onCreate 中检查 savedInstanceState
   2. 或者使用 findFragmentById 检查是否已存在

   override fun onCreate(savedInstanceState: Bundle?) {
       super.onCreate(savedInstanceState)
       if (savedInstanceState == null) {
           supportFragmentManager.commit {
               replace(R.id.container, HomeFragment())
           }
       }
   }

Q2: IllegalStateException: Can not perform this action after onSaveInstanceState
─────────────────────────────────────────────────────────────────────────
A: 原因：在 Activity 状态保存后执行 Fragment 事务
   解决：
   1. 使用 commitAllowingStateLoss（可能丢失状态）
   2. 在生命周期安全的位置执行事务
   3. 使用 Fragment Result API 替代回调

Q3: Fragment 中使用 requireActivity() 和 getActivity()？
─────────────────────────────────────────────────────────────────────────
A:
   - requireActivity()：返回非空 Activity，如果为空抛异常（推荐）
   - getActivity()：可能返回 null，需要空检查

Q4: Fragment 如何获取 Context？
─────────────────────────────────────────────────────────────────────────
A:
   - onAttach 之后：requireContext() / requireActivity()
   - onViewCreated 中：view.context
   - 推荐使用 requireContext()，会在 Fragment 未附加时抛出明确异常

Q5: ViewPager + Fragment 如何实现懒加载？
─────────────────────────────────────────────────────────────────────────
A: ViewPager2 + FragmentStateAdapter 自动处理：
   - 只有当前页 onResume
   - 其他页保持在 onStart
   - 在 onResume 中加载数据即可

Q6: Fragment 之间如何传递复杂对象？
─────────────────────────────────────────────────────────────────────────
A:
   1. 共享 ViewModel（推荐）
   2. 将对象转为 JSON 字符串传递
   3. 使用 Navigation Safe Args（支持 Parcelable）
   4. 使用 Fragment Result API（Bundle 限制）
```

---

## 12. 核心库对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AndroidX 核心库对比                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────────┬───────────────────────────────────────┐
  │     库           │     用途         │              说明                     │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ Lifecycle       │ 生命周期管理     │ 观察组件生命周期，自动管理            │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ ViewModel       │ 数据持久化       │ 配置更改后保留数据，与 UI 分离         │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ LiveData        │ 数据观察         │ 生命周期感知，自动更新 UI              │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ Room            │ 数据库 ORM       │ 类型安全，支持 Flow/LiveData          │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ WorkManager     │ 后台任务         │ 保证执行，约束条件，任务链             │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ Navigation      │ 导航管理         │ Fragment 事务，参数传递，深度链接      │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ DataStore       │ 数据存储         │ 替代 SP，异步 API，类型安全            │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ Paging          │ 分页加载         │ 自动分页，加载状态管理                 │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ ViewPager2      │ 滑动页面         │ 基于 RecyclerView，支持垂直滑动        │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ Fragment        │ UI 片段          │ 模块化 UI，生命周期管理                │
  ├─────────────────┼─────────────────┼───────────────────────────────────────┤
  │ ConstraintLayout│ 布局优化         │ 扁平化布局，减少嵌套层级               │
  └─────────────────┴─────────────────┴───────────────────────────────────────┘

  LiveData vs Flow 选择：
  ─────────────────────────────────────────────────────────────────────────
  - 简单场景：LiveData
  - 复杂操作符：Flow
  - 新项目推荐：StateFlow（兼具两者优点）
```

---

## 13. ConstraintLayout

### 13.1 ConstraintLayout 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ConstraintLayout 定义                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  ConstraintLayout 是一个灵活高效的布局管理器，通过约束关系定位子视图

  优势：
  ─────────────────────────────────────────────────────────────────────────
  1. 扁平化布局：减少嵌套层级，提高性能
  2. 灵活定位：相对定位、居中、偏移
  3. 性能优化：减少 Measure 嵌套次数
  4. 可视化编辑：Layout Editor 支持

  与其他布局对比：
  ─────────────────────────────────────────────────────────────────────────
  - LinearLayout：简单线性排列，需要嵌套
  - RelativeLayout：相对定位，但复杂布局性能差
  - FrameLayout：简单叠加，定位能力有限
  - ConstraintLayout：强大约束，扁平化，性能好
```

### 13.2 相对定位

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         相对定位约束                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  基本约束：
  ─────────────────────────────────────────────────────────────────────────
  layout_constraintLeft_toLeftOf        左边对齐到某边
  layout_constraintLeft_toRightOf       左边对齐到某边右边
  layout_constraintRight_toLeftOf       右边对齐到某边左边
  layout_constraintRight_toRightOf      右边对齐到某边
  layout_constraintTop_toTopOf          顶部对齐到某边
  layout_constraintTop_toBottomOf       顶部对齐到某边底部
  layout_constraintBottom_toTopOf       底部对齐到某边顶部
  layout_constraintBottom_toBottomOf    底部对齐到某边
  layout_constraintStart_toEndOf        开始边对齐到某边结束边
  layout_constraintStart_toStartOf      开始边对齐到某边开始边
  layout_constraintEnd_toStartOf        结束边对齐到某边开始边
  layout_constraintEnd_toEndOf          结束边对齐到某边结束边

  特殊值：
  ─────────────────────────────────────────────────────────────────────────
  - parent：父容器
  - @id/xxx：指定 View 的 ID
```

```xml
<!-- ==================== 基本相对定位 ==================== -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    
    <!-- A 在左上角 -->
    <TextView
        android:id="@+id/tvA"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="A"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    
    <!-- B 在 A 的右边 -->
    <TextView
        android:id="@+id/tvB"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="B"
        app:layout_constraintLeft_toRightOf="@id/tvA"
        app:layout_constraintTop_toTopOf="@id/tvA" />
    
    <!-- C 在 A 的下面 -->
    <TextView
        android:id="@+id/tvC"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="C"
        app:layout_constraintLeft_toLeftOf="@id/tvA"
        app:layout_constraintTop_toBottomOf="@id/tvA" />
    
</androidx.constraintlayout.widget.ConstraintLayout>
```

### 13.3 居中和偏移

```xml
<!-- ==================== 居中 ==================== -->
<!-- 水平居中 -->
<TextView
    app:layout_constraintLeft_toLeftOf="parent"
    app:layout_constraintRight_toRightOf="parent" />

<!-- 垂直居中 -->
<TextView
    app:layout_constraintTop_toTopOf="parent"
    app:layout_constraintBottom_toBottomOf="parent" />

<!-- 完全居中 -->
<TextView
    app:layout_constraintLeft_toLeftOf="parent"
    app:layout_constraintRight_toRightOf="parent"
    app:layout_constraintTop_toTopOf="parent"
    app:layout_constraintBottom_toBottomOf="parent" />

<!-- ==================== 偏移（bias）==================== -->
<!-- 水平偏移 0.3（30% 位置）-->
<TextView
    app:layout_constraintLeft_toLeftOf="parent"
    app:layout_constraintRight_toRightOf="parent"
    app:layout_constraintHorizontal_bias="0.3" />

<!-- 垂直偏移 0.7（70% 位置）-->
<TextView
    app:layout_constraintTop_toTopOf="parent"
    app:layout_constraintBottom_toBottomOf="parent"
    app:layout_constraintVertical_bias="0.7" />

<!-- bias 范围：0.0（最左/最上）到 1.0（最右/最下），默认 0.5（居中）-->
```

### 13.4 尺寸约束

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         尺寸约束                                            │
└─────────────────────────────────────────────────────────────────────────────┘

  layout_width / layout_height 取值：
  ─────────────────────────────────────────────────────────────────────────
  1. 固定值：100dp
  2. wrap_content：根据内容，但有约束限制
  3. 0dp（MATCH_CONSTRAINT）：根据约束扩展填充

  layout_constrainedWidth / layout_constrainedHeight：
  ─────────────────────────────────────────────────────────────────────────
  - 当 width/height 为 wrap_content 时，限制不超过约束边界
  - 默认 false（可能超出边界）
  - 设为 true 时，内容过长会被限制

  layout_constrainedPercent：
  ─────────────────────────────────────────────────────────────────────────
  - 按父容器百分比设置尺寸
```

```xml
<!-- ==================== 0dp 扩展填充 ==================== -->
<!-- 宽度占满父容器 -->
<TextView
    android:layout_width="0dp"
    android:layout_height="wrap_content"
    app:layout_constraintLeft_toLeftOf="parent"
    app:layout_constraintRight_toRightOf="parent" />

<!-- 占据两个 View 之间的空间 -->
<View
    android:layout_width="0dp"
    android:layout_height="1dp"
    app:layout_constraintLeft_toRightOf="@id/tvA"
    app:layout_constraintRight_toLeftOf="@id/tvB" />

<!-- ==================== 百分比尺寸 ==================== -->
<!-- 宽度为父容器的 50% -->
<TextView
    android:layout_width="0dp"
    android:layout_height="wrap_content"
    app:layout_constraintLeft_toLeftOf="parent"
    app:layout_constraintRight_toRightOf="parent"
    app:layout_constraintWidth_percent="0.5" />

<!-- 高度为父容器的 30% -->
<View
    android:layout_width="match_parent"
    android:layout_height="0dp"
    app:layout_constraintTop_toTopOf="parent"
    app:layout_constraintBottom_toBottomOf="parent"
    app:layout_constraintHeight_percent="0.3" />

<!-- ==================== constrainedWidth ==================== -->
<!-- 内容过长时不会超出约束边界 -->
<TextView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:singleLine="true"
    android:ellipsize="end"
    app:layout_constrainedWidth="true"
    app:layout_constraintLeft_toLeftOf="parent"
    app:layout_constraintRight_toRightOf="parent" />
```

### 13.5 Chain 链

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Chain 链                                            │
└─────────────────────────────────────────────────────────────────────────────┘

  定义：
  ─────────────────────────────────────────────────────────────────────────
  链是一组 View 通过双向约束连接，作为一个整体在约束边界内分布

  链模式：
  ─────────────────────────────────────────────────────────────────────────
  - CHAIN_SPREAD：均匀分布（默认）
  - CHAIN_SPREAD_INSIDE：两端贴边，中间均匀分布
  - CHAIN_PACKED：紧密排列，可通过 bias 调整整体位置
  - CHAIN_WEIGHTED：按权重分配空间
```

```xml
<!-- ==================== 水平链 ==================== -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    
    <TextView
        android:id="@+id/tv1"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="1"
        app:layout_constraintHorizontal_chainStyle="spread"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toLeftOf="@id/tv2" />
    
    <TextView
        android:id="@+id/tv2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="2"
        app:layout_constraintLeft_toRightOf="@id/tv1"
        app:layout_constraintRight_toLeftOf="@id/tv3" />
    
    <TextView
        android:id="@+id/tv3"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="3"
        app:layout_constraintLeft_toRightOf="@id/tv2"
        app:layout_constraintRight_toRightOf="parent" />
    
</androidx.constraintlayout.widget.ConstraintLayout>

<!-- ==================== Weighted Chain（按权重分配）==================== -->
<TextView
    android:id="@+id/tv1"
    android:layout_width="0dp"
    android:layout_height="wrap_content"
    app:layout_constraintHorizontal_weight="1"
    app:layout_constraintLeft_toLeftOf="parent"
    app:layout_constraintRight_toLeftOf="@id/tv2" />

<TextView
    android:id="@+id/tv2"
    android:layout_width="0dp"
    android:layout_height="wrap_content"
    app:layout_constraintHorizontal_weight="2"
    app:layout_constraintLeft_toRightOf="@id/tv1"
    app:layout_constraintRight_toRightOf="parent" />
<!-- tv2 宽度是 tv1 的 2 倍 -->

<!-- ==================== Packed Chain ==================== -->
<TextView
    android:id="@+id/tv1"
    app:layout_constraintHorizontal_chainStyle="packed"
    app:layout_constraintHorizontal_bias="0.2"
    ... />
<!-- 整体靠左偏移 20% -->
```

```
  链模式图示：
  ─────────────────────────────────────────────────────────────────────────
  
  CHAIN_SPREAD（均匀分布）：
  |   A   |   B   |   C   |
  |  ↑    |  ↑    |  ↑    |
  | 等间距分布                |
  
  CHAIN_SPREAD_INSIDE（两端贴边）：
  |A     B     C|
  |↑            ↑|
  |两端贴边，中间等间距        |
  
  CHAIN_PACKED（紧密排列）：
  |  ABC         |
  |  ↑           |
  | 作为一个整体，bias 控制位置 |
```

### 13.6 Guideline 辅助线

```xml
<!-- ==================== Guideline ==================== -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    
    <!-- 垂直辅助线，距左边 100dp -->
    <androidx.constraintlayout.widget.Guideline
        android:id="@+id/guideVertical"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        app:layout_constraintGuide_begin="100dp" />
    
    <!-- 水平辅助线，距顶部 30% -->
    <androidx.constraintlayout.widget.Guideline
        android:id="@+id/guideHorizontal"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        app:layout_constraintGuide_percent="0.3" />
    
    <!-- 距右边 50dp -->
    <androidx.constraintlayout.widget.Guideline
        android:id="@+id/guideEnd"
        android:orientation="vertical"
        app:layout_constraintGuide_end="50dp" />
    
    <!-- 使用辅助线定位 -->
    <TextView
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintLeft_toLeftOf="@id/guideVertical"
        app:layout_constraintTop_toTopOf="@id/guideHorizontal"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintBottom_toBottomOf="parent" />
    
</androidx.constraintlayout.widget.ConstraintLayout>
```

### 13.7 Barrier 屏障

```xml
<!-- ==================== Barrier ==================== -->
<!-- Barrier 根据多个 View 的位置自动调整 -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content">
    
    <TextView
        android:id="@+id/tvLabel1"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Label 1"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    
    <TextView
        android:id="@+id/tvLabel2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Longer Label 2"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintTop_toBottomOf="@id/tvLabel1" />
    
    <!-- Barrier 在最长的 Label 右边 -->
    <androidx.constraintlayout.widget.Barrier
        android:id="@+id/barrier"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        app:barrierDirection="end"
        app:constraint_referenced_ids="tvLabel1,tvLabel2" />
    
    <!-- 输入框始终在最长 Label 右边 -->
    <EditText
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        app:layout_constraintLeft_toRightOf="@id/barrier"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    
</androidx.constraintlayout.widget.ConstraintLayout>
```

### 13.8 Group 分组

```xml
<!-- ==================== Group ==================== -->
<!-- 批量控制多个 View 的可见性 -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    
    <TextView android:id="@+id/tv1" ... />
    <TextView android:id="@+id/tv2" ... />
    <TextView android:id="@+id/tv3" ... />
    
    <!-- 分组 -->
    <androidx.constraintlayout.widget.Group
        android:id="@+id/group"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        app:constraint_referenced_ids="tv1,tv2,tv3" />
    
</androidx.constraintlayout.widget.ConstraintLayout>

// 代码中控制
binding.group.visibility = View.GONE  // 同时隐藏 tv1, tv2, tv3
```

### 13.9 Flow 流式布局

```xml
<!-- ==================== Flow（ConstraintLayout 2.0+）==================== -->
<!-- 自动换行的流式布局 -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    
    <androidx.constraintlayout.helper.widget.Flow
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        app:constraint_referenced_ids="tv1,tv2,tv3,tv4,tv5"
        app:flow_wrapMode="chain"
        app:flow_horizontalStyle="spread"
        app:flow_verticalStyle="spread"
        app:flow_horizontalGap="8dp"
        app:flow_verticalGap="8dp"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_toTopOf="parent" />
    
    <TextView android:id="@+id/tv1" ... />
    <TextView android:id="@+id/tv2" ... />
    <TextView android:id="@+id/tv3" ... />
    <TextView android:id="@+id/tv4" ... />
    <TextView android:id="@+id/tv5" ... />
    
</androidx.constraintlayout.widget.ConstraintLayout>

<!-- flow_wrapMode 取值：
  - none：不换行（默认）
  - chain：换行，每行作为链
  - aligned：换行，对齐排列
-->
```

### 13.10 Layer 图层

```xml
<!-- ==================== Layer ==================== -->
<!-- 批量设置背景、padding、elevation 等 -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    
    <androidx.constraintlayout.helper.widget.Layer
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:background="@drawable/bg_rounded"
        android:padding="16dp"
        app:constraint_referenced_ids="tv1,tv2" />
    
    <TextView android:id="@+id/tv1" ... />
    <TextView android:id="@+id/tv2" ... />
    
</androidx.constraintlayout.widget.ConstraintLayout>
```

### 13.11 ConstraintLayout 常见问题

```
Q1: 为什么设置约束后 View 还是在左上角？
─────────────────────────────────────────────────────────────────────────
A: 需要同时设置水平和垂直两个方向的约束：
   - 水平：left + right
   - 垂直：top + bottom

Q2: wrap_content 为什么会超出边界？
─────────────────────────────────────────────────────────────────────────
A: 使用 app:layout_constrainedWidth="true" 限制

Q3: 如何让两个 View 宽度相等？
─────────────────────────────────────────────────────────────────────────
A: 都设置为 0dp，使用 chain 或设置相同 weight

Q4: ConstraintLayout 性能真的更好吗？
─────────────────────────────────────────────────────────────────────────
A: 
   - 减少嵌套层级 → 减少 Measure 次数
   - 复杂布局效果明显
   - 简单布局差异不大
```

---

## 14. 常见问题

### 14.1 ViewModel 什么时候销毁？

```
ViewModel 在以下情况销毁：
- Activity 真正 finish（不是配置更改）
- Fragment 真正 detach

注意：
- 屏幕旋转不会销毁 ViewModel
- ViewModel.onCleared() 在销毁时调用
```

### 14.2 LiveData 和 Flow 怎么选？

```
LiveData：
- 简单场景
- 需要自动生命周期管理
- 已有项目

Flow（推荐）：
- 复杂操作符（debounce、combine、flatMapLatest）
- 需要更多控制
- 新项目首选
```

### 14.3 Room 能在主线程访问吗？

```
默认：不允许在主线程访问（会抛异常）

解决：
1. 使用 suspend 函数（推荐）
2. 返回 LiveData/Flow（自动异步）
3. allowMainThreadQueries()（不推荐）

Room.databaseBuilder(...)
    .allowMainThreadQueries()  // 仅用于测试！
    .build()
```

---

## 15. 知识体系总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AndroidX 核心库知识体系                             │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   AndroidX     │
                           └────────┬────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
  ┌───────────┐              ┌───────────┐              ┌───────────┐
  │ 架构组件  │              │ 数据组件  │              │ UI 组件   │
  │           │              │           │              │           │
  │ Lifecycle │              │ Room      │              │ Navigation│
  │ ViewModel │              │ DataStore │              │ Paging    │
  │ LiveData  │              │           │              │           │
  │ WorkManager│             │           │              │           │
  └───────────┘              └───────────┘              └───────────┘

  核心要点：
  ─────────────────────────────────────────────────────────────────────────
  1. Lifecycle：生命周期感知，自动管理
  2. ViewModel：配置更改后保留数据
  3. LiveData/Flow：数据观察，响应式编程
  4. Room：类型安全的 ORM
  5. WorkManager：保证执行的后台任务
  6. Navigation：Fragment 导航管理
  7. DataStore：替代 SharedPreferences
  8. Paging：高效分页加载
```

---

> 作者：OpenClaw | 日期：2026-03-09
