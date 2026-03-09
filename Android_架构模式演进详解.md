# Android 架构模式演进详解

> 作者：OpenClaw | 日期：2026-03-09

---

## 目录

1. [概述](#1-概述)
2. [架构演进历程](#2-架构演进历程)
3. [MVC 架构](#3-mvc-架构)
4. [MVP 架构](#4-mvp-架构)
5. [MVVM 架构](#5-mvvm-架构)
6. [MVI 架构](#6-mvi-架构)
7. [架构对比](#7-架构对比)
8. [架构选择指南](#8-架构选择指南)
9. [Clean Architecture](#9-clean-architecture)
10. [常见问题](#10-常见问题)
11. [知识体系总结](#11-知识体系总结)

---

## 1. 概述

Android 架构模式是组织代码的一种方式，目的是解决代码耦合、提高可维护性和可测试性。从早期的 MVC 到现代的 MVI，架构模式不断演进，每种模式都有其适用场景和优缺点。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         架构模式演进                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  时间线：
  ─────────────────────────────────────────────────────────────────────────
  
  1979  MVC         Trygve Reenskaug 提出（Smalltalk）
  2010  MVP         Android 开发社区推广
  2017  MVVM        Google 推出 Architecture Components
  2018  MVI         借鉴前端架构（Redux/Cycle.js）

  演进动力：
  ─────────────────────────────────────────────────────────────────────────
  1. 解耦：降低各层之间的依赖
  2. 可测试：方便单元测试
  3. 可维护：代码结构清晰
  4. 可扩展：易于添加新功能
```

---

## 2. 架构演进历程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         架构演进核心问题                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  MVC 的问题：
  - Activity/Fragment 过于臃肿（既是 View 又是 Controller）
  - View 和 Controller 耦合紧密
  - 难以单元测试

  MVP 的改进：
  - View 和 Model 完全解耦
  - Presenter 处理业务逻辑
  - View 只负责 UI 展示

  MVP 的问题：
  - Presenter 与 View 接口耦合
  - 手动管理生命周期
  - 大量接口定义

  MVVM 的改进：
  - 使用 DataBinding 自动更新 UI
  - ViewModel 不持有 View 引用
  - LiveData 自动管理生命周期

  MVVM 的问题：
  - 状态管理复杂
  - 多个 LiveData 可能导致状态不一致
  - DataBinding 调试困难

  MVI 的改进：
  - 单向数据流，状态可预测
  - 不可变状态，线程安全
  - 便于状态调试和回溯
```

---

## 3. MVC 架构

### 3.1 MVC 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MVC（Model-View-Controller）                        │
└─────────────────────────────────────────────────────────────────────────────┘

  Model：数据层，负责数据处理和业务逻辑
  View：视图层，负责 UI 展示
  Controller：控制层，连接 Model 和 View

  职责：
  ─────────────────────────────────────────────────────────────────────────
  Model：
  - 数据模型
  - 业务逻辑
  - 数据存取
  - 网络请求
  
  View：
  - UI 布局
  - 用户交互
  - 数据展示
  
  Controller：
  - 处理用户输入
  - 调用 Model 获取数据
  - 更新 View 显示
```

### 3.2 MVC 结构图

```
                    ┌─────────────────────────────────────┐
                    │             用户操作                 │
                    └──────────────────┬──────────────────┘
                                       ▼
                    ┌─────────────────────────────────────┐
                    │           Controller                │
                    │        (Activity/Fragment)          │
                    └──────────┬───────────────┬──────────┘
              ┌────────────────┘               └────────────────┐
              ▼                                                 ▼
    ┌─────────────────┐                             ┌─────────────────┐
    │      Model      │◄────────────────────────────│       View      │
    │                 │      通知数据变化            │                 │
    │  - 数据模型     │                             │  - XML 布局     │
    │  - 业务逻辑     │                             │  - UI 组件      │
    └─────────────────┘                             └─────────────────┘

  Android 中的 MVC：
  - Model：Java Bean、Repository、网络请求等
  - View：XML 布局文件
  - Controller：Activity/Fragment

  问题：Activity/Fragment 既充当 View 又充当 Controller，职责不清
```

### 3.3 MVC 代码示例

```java
// ==================== Model ====================
public class UserModel {
    public interface OnLoginListener {
        void onSuccess(User user);
        void onFailure(String error);
    }
    
    public void login(String username, String password, OnLoginListener listener) {
        // 模拟网络请求
        new Thread(() -> {
            try {
                Thread.sleep(1000);
                if ("admin".equals(username) && "123456".equals(password)) {
                    listener.onSuccess(new User(username));
                } else {
                    listener.onFailure("用户名或密码错误");
                }
            } catch (InterruptedException e) {
                listener.onFailure(e.getMessage());
            }
        }).start();
    }
}

// ==================== Controller（Activity）===================
public class LoginActivity extends AppCompatActivity {
    private EditText etUsername, etPassword;
    private Button btnLogin;
    private TextView tvResult;
    private UserModel userModel;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        
        etUsername = findViewById(R.id.et_username);
        etPassword = findViewById(R.id.et_password);
        btnLogin = findViewById(R.id.btn_login);
        tvResult = findViewById(R.id.tv_result);
        userModel = new UserModel();
        
        btnLogin.setOnClickListener(v -> {
            userModel.login(etUsername.getText().toString(), 
                etPassword.getText().toString(),
                new UserModel.OnLoginListener() {
                    @Override
                    public void onSuccess(User user) {
                        runOnUiThread(() -> tvResult.setText("登录成功"));
                    }
                    @Override
                    public void onFailure(String error) {
                        runOnUiThread(() -> tvResult.setText("失败：" + error));
                    }
                });
        });
    }
}
```

### 3.4 MVC 优缺点

```
优点：
1. 结构简单，易于理解
2. 早期 Android 默认架构
3. 适合小型项目

缺点：
1. Activity/Fragment 过于臃肿
2. View 和 Controller 耦合紧密
3. 难以进行单元测试
4. Model 与 View 可以直接通信
```

---

## 4. MVP 架构

### 4.1 MVP 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MVP（Model-View-Presenter）                         │
└─────────────────────────────────────────────────────────────────────────────┘

  Model：数据层
  View：视图层（接口定义）
  Presenter：表现层，连接 Model 和 View

  与 MVC 的区别：
  - View 和 Model 完全解耦（不直接通信）
  - Presenter 作为中间人
  - View 只通过接口与 Presenter 交互
```

### 4.2 MVP 结构图

```
                    ┌─────────────────────────────────────┐
                    │             用户操作                 │
                    └──────────────────┬──────────────────┘
                                       ▼
                    ┌─────────────────────────────────────┐
                    │              View                   │
                    │        (Activity/Fragment)          │
                    │        实现 View 接口               │
                    └──────────────────┬──────────────────┘
                                       │ View 接口
                                       ▼
                    ┌─────────────────────────────────────┐
                    │            Presenter                │
                    │  - 处理业务逻辑                      │
                    │  - 调用 Model                       │
                    │  - 更新 View（通过接口）             │
                    └──────────────────┬──────────────────┘
                                       ▼
                    ┌─────────────────────────────────────┐
                    │              Model                  │
                    └─────────────────────────────────────┘
```

### 4.3 MVP 代码示例

```java
// ==================== 契约类 ====================
public interface LoginContract {
    interface View {
        void showLoading();
        void hideLoading();
        void showSuccess(String message);
        void showError(String error);
        String getUsername();
        String getPassword();
    }
    
    interface Presenter {
        void login();
        void onDestroy();
    }
}

// ==================== Presenter ====================
public class LoginPresenter implements LoginContract.Presenter {
    private LoginContract.View view;
    private LoginModel model;
    
    public LoginPresenter(LoginContract.View view) {
        this.view = view;
        this.model = new LoginModel();
    }
    
    @Override
    public void login() {
        if (TextUtils.isEmpty(view.getUsername()) || TextUtils.isEmpty(view.getPassword())) {
            view.showError("用户名或密码不能为空");
            return;
        }
        view.showLoading();
        model.login(view.getUsername(), view.getPassword(), new LoginModel.Callback() {
            @Override
            public void onSuccess(User user) {
                view.hideLoading();
                view.showSuccess("欢迎 " + user.getUsername());
            }
            @Override
            public void onFailure(String error) {
                view.hideLoading();
                view.showError(error);
            }
        });
    }
    
    @Override
    public void onDestroy() {
        view = null;  // 防止内存泄漏
    }
}

// ==================== View ====================
public class LoginActivity extends AppCompatActivity implements LoginContract.View {
    private LoginPresenter presenter;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        presenter = new LoginPresenter(this);
        findViewById(R.id.btn_login).setOnClickListener(v -> presenter.login());
    }
    
    @Override public void showLoading() { /*...*/ }
    @Override public void hideLoading() { /*...*/ }
    @Override public void showSuccess(String msg) { /*...*/ }
    @Override public void showError(String error) { /*...*/ }
    @Override public String getUsername() { return etUsername.getText().toString(); }
    @Override public String getPassword() { return etPassword.getText().toString(); }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        presenter.onDestroy();
    }
}
```

### 4.4 MVP 优缺点

```
优点：
1. View 和 Model 完全解耦
2. 易于单元测试
3. 职责清晰
4. 代码结构清晰

缺点：
1. 接口过多
2. Presenter 与 View 耦合
3. 生命周期管理复杂
4. Presenter 可能臃肿
```

---

## 5. MVVM 架构

### 5.1 MVVM 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MVVM（Model-View-ViewModel）                            │
└─────────────────────────────────────────────────────────────────────────────┘

  Model：数据层
  View：视图层
  ViewModel：视图模型层

  与 MVP 的区别：
  - ViewModel 不持有 View 引用
  - 使用 DataBinding 或 LiveData 自动更新 UI
  - View 和 ViewModel 通过数据绑定连接
```

### 5.2 MVVM 结构图

```
                    ┌─────────────────────────────────────┐
                    │              View                   │
                    │        (Activity/Fragment)          │
                    │  - 观察 ViewModel 数据              │
                    │  - 绑定数据到 UI                    │
                    └──────────────────┬──────────────────┘
                                       │ 数据绑定
                                       ▼
                    ┌─────────────────────────────────────┐
                    │            ViewModel                │
                    │  - 持有 LiveData/Flow              │
                    │  - 不持有 View 引用                 │
                    └──────────────────┬──────────────────┘
                                       ▼
                    ┌─────────────────────────────────────┐
                    │              Model                  │
                    └─────────────────────────────────────┘
```

### 5.3 MVVM 三种实现方式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MVVM 三种实现方式                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  1. LiveData 方式（传统，Google 官方推荐）
  ─────────────────────────────────────────────────────────────────────────
  - 使用 ViewModel + LiveData
  - View 观察 LiveData 变化
  - 手动更新 UI

  2. DataBinding 方式
  ─────────────────────────────────────────────────────────────────────────
  - XML 布局直接绑定数据
  - 双向绑定 @={}
  - 自动更新 UI

  3. StateFlow 方式（现代推荐）
  ─────────────────────────────────────────────────────────────────────────
  - 使用 Kotlin Flow
  - 单向数据流
  - 更灵活的线程控制
```

### 5.4 LiveData 方式（传统）

```kotlin
// ==================== ViewModel + LiveData ====================
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    
    // 私有 MutableLiveData，对外暴露 LiveData
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _errorMessage = MutableLiveData<String>()
    val errorMessage: LiveData<String> = _errorMessage
    
    fun loadUsers() {
        _isLoading.value = true
        
        viewModelScope.launch {
            repository.getUsers()
                .onSuccess { users ->
                    _isLoading.value = false
                    _users.value = users
                }
                .onFailure { error ->
                    _isLoading.value = false
                    _errorMessage.value = error.message
                }
        }
    }
    
    fun deleteUser(userId: String) {
        viewModelScope.launch {
            repository.deleteUser(userId)
                .onSuccess {
                    // 更新列表
                    _users.value = _users.value?.filter { it.id != userId }
                }
        }
    }
}

// ==================== Activity 观察 LiveData ====================
class UserActivity : AppCompatActivity() {
    private lateinit var binding: ActivityUserBinding
    private val viewModel: UserViewModel by viewModels()
    private lateinit var adapter: UserAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUserBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        adapter = UserAdapter { user ->
            viewModel.deleteUser(user.id)
        }
        binding.recyclerView.adapter = adapter
        
        // 观察 users LiveData
        viewModel.users.observe(this) { users ->
            adapter.submitList(users)
        }
        
        // 观察 isLoading LiveData
        viewModel.isLoading.observe(this) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }
        
        // 观察 errorMessage LiveData
        viewModel.errorMessage.observe(this) { error ->
            error?.let {
                Snackbar.make(binding.root, it, Snackbar.LENGTH_SHORT).show()
            }
        }
        
        // 初始加载
        viewModel.loadUsers()
        
        // 下拉刷新
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadUsers()
            binding.swipeRefresh.isRefreshing = false
        }
    }
}
```

### 5.5 DataBinding 方式

```xml
<!-- ==================== XML 布局（DataBinding）==================== -->
<?xml version="1.0" encoding="utf-8"?>
<layout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto">
    
    <data>
        <import type="android.view.View" />
        <variable
            name="viewModel"
            type="com.example.UserViewModel" />
    </data>
    
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical">
        
        <!-- 双向绑定：EditText 内容自动同步到 ViewModel -->
        <EditText
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:hint="搜索用户"
            android:text="@={viewModel.searchQuery}" />
        
        <!-- 条件显示 -->
        <ProgressBar
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="center"
            android:visibility="@{viewModel.isLoading ? View.VISIBLE : View.GONE}" />
        
        <!-- RecyclerView 需要自定义 BindingAdapter -->
        <androidx.recyclerview.widget.RecyclerView
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            app:items="@{viewModel.users}" />
        
        <!-- 单向绑定 -->
        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="@{viewModel.errorMessage}"
            android:textColor="@color/red"
            android:visibility="@{viewModel.errorMessage != null ? View.VISIBLE : View.GONE}" />
            
    </LinearLayout>
</layout>
```

```kotlin
// ==================== ViewModel（DataBinding）====================
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    
    // 双向绑定字段
    val searchQuery = ObservableField<String>("")
    
    // LiveData
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users
    
    private val _isLoading = MutableLiveData<Boolean>(false)
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage
    
    init {
        // 监听搜索框变化
        searchQuery.addOnPropertyChangedCallback(object : Observable.OnPropertyChangedCallback() {
            override fun onPropertyChanged(sender: Observable?, propertyId: Int) {
                search(searchQuery.get() ?: "")
            }
        })
    }
    
    fun loadUsers() {
        _isLoading.value = true
        viewModelScope.launch {
            repository.getUsers()
                .onSuccess { 
                    _isLoading.value = false
                    _users.value = it 
                }
                .onFailure { 
                    _isLoading.value = false
                    _errorMessage.value = it.message 
                }
        }
    }
    
    private fun search(query: String) {
        // 搜索逻辑
    }
}

// ==================== Activity（DataBinding）====================
class UserActivity : AppCompatActivity() {
    private lateinit var binding: ActivityUserBinding
    private val viewModel: UserViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // DataBinding 初始化
        binding = DataBindingUtil.setContentView(this, R.layout.activity_user)
        binding.lifecycleOwner = this  // 重要！让 LiveData 生效
        binding.viewModel = viewModel
        
        viewModel.loadUsers()
    }
}
```

### 5.6 StateFlow 方式（现代推荐）

```kotlin
// ==================== ViewModel + StateFlow ====================
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    
    // 单一状态源（UiState）
    data class UiState(
        val isLoading: Boolean = false,
        val users: List<User> = emptyList(),
        val error: String? = null
    )
    
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state.asStateFlow()
    
    // 一次性事件（Toast/导航）
    private val _event = MutableSharedFlow<UiEvent>()
    val event: SharedFlow<UiEvent> = _event.asSharedFlow()
    
    sealed class UiEvent {
        data class ShowToast(val message: String) : UiEvent()
        data class NavigateToDetail(val userId: String) : UiEvent()
    }
    
    fun loadUsers() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            
            repository.getUsers()
                .onSuccess { users ->
                    _state.update { it.copy(isLoading = false, users = users) }
                }
                .onFailure { error ->
                    _state.update { it.copy(isLoading = false, error = error.message) }
                }
        }
    }
    
    fun onUserClick(userId: String) {
        viewModelScope.launch {
            _event.emit(UiEvent.NavigateToDetail(userId))
        }
    }
    
    fun deleteUser(userId: String) {
        viewModelScope.launch {
            repository.deleteUser(userId)
                .onSuccess {
                    _state.update { 
                        it.copy(users = it.users.filter { u -> u.id != userId }) 
                    }
                    _event.emit(UiEvent.ShowToast("删除成功"))
                }
        }
    }
}

// ==================== Activity（StateFlow）====================
class UserActivity : AppCompatActivity() {
    private lateinit var binding: ActivityUserBinding
    private val viewModel: UserViewModel by viewModels()
    private lateinit var adapter: UserAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUserBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        adapter = UserAdapter(
            onItemClick = { viewModel.onUserClick(it.id) },
            onDeleteClick = { viewModel.deleteUser(it.id) }
        )
        binding.recyclerView.adapter = adapter
        
        // 收集状态
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                // 收集 UI 状态
                viewModel.state.collect { state ->
                    render(state)
                }
            }
        }
        
        // 收集一次性事件
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.event.collect { event ->
                    when (event) {
                        is UserViewModel.UiEvent.ShowToast -> {
                            Snackbar.make(binding.root, event.message, Snackbar.LENGTH_SHORT).show()
                        }
                        is UserViewModel.UiEvent.NavigateToDetail -> {
                            startActivity(Intent(this@UserActivity, DetailActivity::class.java).apply {
                                putExtra("userId", event.userId)
                            })
                        }
                    }
                }
            }
        }
    }
    
    private fun render(state: UserViewModel.UiState) {
        binding.progressBar.isVisible = state.isLoading
        adapter.submitList(state.users)
        
        state.error?.let {
            binding.errorTextView.text = it
            binding.errorTextView.isVisible = true
        } ?: run {
            binding.errorTextView.isVisible = false
        }
    }
}
```

### 5.7 三种方式对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MVVM 三种实现方式对比                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
  │     特性         │    LiveData     │   DataBinding   │   StateFlow     │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 学习曲线         │ 低              │ 高              │ 中              │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 代码量           │ 中              │ 少（XML绑定）   │ 中              │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 调试难度         │ 低              │ 高              │ 低              │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 线程控制         │ 自动（主线程）  │ 自动            │ 灵活            │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 操作符支持       │ 少              │ 无              │ 丰富            │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 状态管理         │ 分散（多个LD）  │ 分散            │ 集中（State）   │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 推荐场景         │ 简单页面        │ 表单页面        │ 复杂页面        │
  └─────────────────┴─────────────────┴─────────────────┴─────────────────┘

  推荐选择：
  ─────────────────────────────────────────────────────────────────────────
  - 新项目：StateFlow（现代推荐）
  - 表单页面：DataBinding（双向绑定方便）
  - 简单页面：LiveData（够用即可）
  - 已有项目：保持一致，不混用
```

### 5.8 MVVM 优缺点

```
优点：
1. ViewModel 不依赖 View
2. LiveData/Flow 自动管理生命周期
3. 便于单元测试
4. 数据驱动 UI

缺点：
1. DataBinding 调试困难
2. 多个 LiveData 状态管理复杂
3. 学习曲线较陡
```

---

## 6. MVI 架构

### 6.1 MVI 是什么

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MVI（Model-View-Intent）                                │
└─────────────────────────────────────────────────────────────────────────────┘

  Model：状态（State），不可变
  View：视图层，渲染状态
  Intent：用户意图/动作

  核心概念：
  - 单向数据流（Unidirectional Data Flow）
  - 不可变状态（Immutable State）
  - 状态机（State Machine）
```

### 6.2 MVI 结构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MVI 单向数据流                                      │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │    ┌─────────┐      Intent       ┌─────────┐      State       ┌─────────┐
    │    │         │ ──────────────────►│         │ ──────────────────►│         │
    │    │  View   │                    │  Model  │                    │  View   │
    │    │         │◄──────────────────│         │◄──────────────────│         │
    │    └─────────┘      Render       └─────────┘                   └─────────┘
    │                                                                     │
    │    用户操作 → Intent → Model 处理 → 新 State → View 渲染            │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘

  数据流向：
  1. 用户操作产生 Intent
  2. Intent 被 Model 处理
  3. Model 产生新的 State
  4. View 渲染新的 State
```

### 6.3 MVI 代码示例

```kotlin
// ==================== State（不可变状态）===================
data class UiState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val error: String? = null
)

// ==================== Intent（用户意图）===================
sealed class UserIntent {
    object LoadUsers : UserIntent()
    object Refresh : UserIntent()
    data class DeleteUser(val userId: String) : UserIntent()
}

// ==================== ViewModel ====================
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    
    // 单一状态源
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state
    
    // 处理 Intent
    fun processIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUsers -> loadUsers()
            is UserIntent.Refresh -> loadUsers()
            is UserIntent.DeleteUser -> deleteUser(intent.userId)
        }
    }
    
    private fun loadUsers() {
        viewModelScope.launch {
            // 更新状态：加载中
            _state.update { it.copy(isLoading = true, error = null) }
            
            repository.getUsers()
                .onSuccess { users ->
                    // 更新状态：成功
                    _state.update { it.copy(isLoading = false, users = users) }
                }
                .onFailure { error ->
                    // 更新状态：失败
                    _state.update { it.copy(isLoading = false, error = error.message) }
                }
        }
    }
    
    private fun deleteUser(userId: String) {
        viewModelScope.launch {
            repository.deleteUser(userId)
                .onSuccess {
                    // 更新状态：从列表中移除
                    _state.update { it.copy(users = it.users.filter { u -> u.id != userId }) }
                }
        }
    }
}

// ==================== View（Activity）===================
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()
    private lateinit var adapter: UserAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_user)
        
        adapter = UserAdapter { user ->
            // 发送 Intent
            viewModel.processIntent(UserIntent.DeleteUser(user.id))
        }
        
        findViewById<RecyclerView>(R.id.recyclerView).adapter = adapter
        
        findViewById<SwipeRefreshLayout>(R.id.swipeRefresh).setOnRefreshListener {
            viewModel.processIntent(UserIntent.Refresh)
        }
        
        // 观察状态
        lifecycleScope.launch {
            viewModel.state.collect { state ->
                render(state)
            }
        }
        
        // 初始加载
        viewModel.processIntent(UserIntent.LoadUsers)
    }
    
    // 渲染状态
    private fun render(state: UiState) {
        findViewById<SwipeRefreshLayout>(R.id.swipeRefresh).isRefreshing = state.isLoading
        adapter.submitList(state.users)
        
        state.error?.let { error ->
            Snackbar.make(findViewById(R.id.root), error, Snackbar.LENGTH_SHORT).show()
        }
    }
}
```

### 6.4 MVI 优缺点

```
优点：
1. 单向数据流，状态可预测
2. 不可变状态，线程安全
3. 便于状态调试和回溯（时间旅行）
4. 易于测试

缺点：
1. 代码量较大
2. 简单功能过度设计
3. 学习曲线陡峭
4. State 类可能膨胀
```

---

## 7. 架构对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         四种架构对比表                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌───────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
  │   特性     │      MVC        │      MVP        │      MVVM       │      MVI        │
  ├───────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 数据流     │ 双向            │ 双向            │ 双向绑定/单向*  │ 单向            │
  ├───────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ View-Model │ 可直接通信      │ 完全解耦        │ 完全解耦        │ 完全解耦        │
  │ 耦合度     │                 │                 │                 │                 │
  ├───────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 状态管理   │ 分散            │ Presenter 管理  │ ViewModel 管理  │ 集中（State）   │
  ├───────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 可测试性   │ 困难            │ 容易            │ 容易            │ 容易            │
  ├───────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 代码量     │ 少              │ 多（接口）      │ 中等            │ 多              │
  ├───────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 学习曲线   │ 低              │ 中              │ 中高            │ 高              │
  ├───────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 适用场景   │ 简单项目        │ 中型项目        │ 中大型项目      │ 复杂状态项目    │
  └───────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘

  *注：现代 MVVM 使用 StateFlow 可以实现单向数据流，与 MVI 模式接近
```

### 7.2 MVVM vs MVI 的界限模糊

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    现代 MVVM 与 MVI 的融合                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  传统 MVVM（双向绑定）：
  ─────────────────────────────────────────────────────────────────────────
  - DataBinding 双向绑定 @={}
  - 多个 LiveData 独立管理
  - 状态分散

  现代 MVVM（单向数据流）：
  ─────────────────────────────────────────────────────────────────────────
  - 使用 StateFlow/SharedFlow
  - 单一 UiState 状态类
  - 用户操作通过函数调用

  // 现代 MVVM（类似 MVI）
  class UserViewModel : ViewModel() {
      // 单一状态源
      private val _state = MutableStateFlow(UiState())
      val state: StateFlow<UiState> = _state
      
      // 用户操作
      fun loadUsers() { ... }
      fun deleteUser(id: String) { ... }
  }

  // MVI
  class UserViewModel : ViewModel() {
      private val _state = MutableStateFlow(UiState())
      val state: StateFlow<UiState> = _state
      
      // 用户意图
      fun processIntent(intent: UserIntent) { ... }
  }

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  核心区别：                                                             │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  MVVM：用户操作 → ViewModel 方法调用                                   │
  │        loadUsers(), deleteUser(id)                                     │
  │                                                                         │
  │  MVI：用户操作 → Intent → processIntent()                              │
  │        UserIntent.LoadUsers, UserIntent.DeleteUser(id)                 │
  │                                                                         │
  │  MVI 的优势：                                                           │
  │  - Intent 是密封类，可以穷举所有用户操作                               │
  │  - 便于日志记录、调试、回放                                            │
  │  - 更严格的单向数据流约束                                               │
  │                                                                         │
  │  实际上：现代 MVVM + StateFlow 已经是"轻量级 MVI"                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 8. 架构选择指南

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         架构选择决策树                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  问题1：项目规模？
  ─────────────────────────────────────────────────────────────────────────
  小型项目（Demo/工具类）──► MVC 或不用架构
  中型项目 ──► MVP 或 MVVM
  大型项目 ──► MVVM 或 MVI

  问题2：状态复杂度？
  ─────────────────────────────────────────────────────────────────────────
  简单状态 ──► MVP 或 MVVM
  复杂状态 ──► MVI

  问题3：团队规模？
  ─────────────────────────────────────────────────────────────────────────
  小团队 ──► 简单架构（MVP/MVVM）
  大团队 ──► 严格架构（MVVM + Clean Architecture / MVI）

  问题4：测试需求？
  ─────────────────────────────────────────────────────────────────────────
  高测试覆盖 ──► MVP / MVVM / MVI
  低测试需求 ──► MVC

  推荐方案：
  ─────────────────────────────────────────────────────────────────────────
  2024+ 推荐方案：MVVM + Clean Architecture
  或：MVI（复杂状态场景）
```

---

## 9. Clean Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Clean Architecture                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  分层：
  ─────────────────────────────────────────────────────────────────────────
  
  ┌─────────────────────────────────────────────────────────────────────┐
  │                          Presentation Layer                          │
  │                    (Activity/Fragment/ViewModel)                     │
  └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                            Domain Layer                              │
  │                      (UseCase/Entity/Repository接口)                 │
  └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                             Data Layer                               │
  │                    (Repository实现/DataSource/Api/DB)                │
  └─────────────────────────────────────────────────────────────────────┘

  依赖规则：
  ─────────────────────────────────────────────────────────────────────────
  - 外层依赖内层
  - 内层不知道外层的存在
  - Domain 层完全独立，不依赖任何框架
```

```kotlin
// Domain Layer
data class User(val id: String, val name: String)

interface UserRepository {
    suspend fun getUsers(): Result<List<User>>
}

class GetUsersUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(): Result<List<User>> = repository.getUsers()
}

// Data Layer
class UserRepositoryImpl(
    private val apiService: ApiService,
    private val userDao: UserDao
) : UserRepository {
    override suspend fun getUsers(): Result<List<User>> {
        return try {
            val users = apiService.getUsers()
            userDao.insertAll(users)
            Result.success(users)
        } catch (e: Exception) {
            val cached = userDao.getAll()
            if (cached.isNotEmpty()) {
                Result.success(cached)
            } else {
                Result.failure(e)
            }
        }
    }
}

// Presentation Layer
class UserViewModel(private val getUsersUseCase: GetUsersUseCase) : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state
    
    fun loadUsers() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            getUsersUseCase()
                .onSuccess { users -> _state.update { it.copy(isLoading = false, users = users) } }
                .onFailure { error -> _state.update { it.copy(isLoading = false, error = error.message) } }
        }
    }
}
```

---

## 10. 常见问题

### 10.1 MVVM 和 MVI 怎么选？

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MVVM vs MVI：界限已经模糊                               │
└─────────────────────────────────────────────────────────────────────────────┘

  现代 MVVM（推荐）：
  ─────────────────────────────────────────────────────────────────────────
  class UserViewModel : ViewModel() {
      // 单一状态源（单向数据流）
      private val _state = MutableStateFlow(UiState())
      val state: StateFlow<UiState> = _state
      
      // 事件
      private val _event = MutableSharedFlow<UiEvent>()
      val event: SharedFlow<UiEvent> = _event
      
      // 直接调用方法
      fun loadUsers() { ... }
      fun deleteUser(id: String) { ... }
  }

  MVI：
  ─────────────────────────────────────────────────────────────────────────
  class UserViewModel : ViewModel() {
      private val _state = MutableStateFlow(UiState())
      val state: StateFlow<UiState> = _state
      
      // 统一 Intent 入口
      fun processIntent(intent: UserIntent) {
          when (intent) {
              is UserIntent.LoadUsers -> loadUsers()
              is UserIntent.DeleteUser -> deleteUser(intent.id)
          }
      }
  }

  选择建议：
  ─────────────────────────────────────────────────────────────────────────
  
  选择 MVVM（现代写法）：
  - 大多数场景足够用
  - 代码更简洁
  - 团队更容易上手
  
  选择 MVI：
  - 需要严格记录所有用户操作（日志/分析）
  - 需要状态回溯/时间旅行调试
  - 复杂的状态机逻辑
  - 团队有前端 Redux 经验

  结论：
  ─────────────────────────────────────────────────────────────────────────
  现代 MVVM + StateFlow = 轻量级 MVI
  
  两者核心思想相同：
  - 单一状态源
  - 单向数据流
  - 不可变状态（StateFlow）
  
  区别只是 API 设计风格：
  - MVVM：直接调用方法
  - MVI：通过 Intent 封装操作
```

### 10.2 ViewModel 如何传递参数？

```kotlin
// 使用 Factory
class UserViewModelFactory(private val userId: String) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return UserViewModel(userId) as T
    }
}

// 使用
val viewModel = ViewModelProvider(this, UserViewModelFactory("123"))
    .get(UserViewModel::class.java)

// 或使用 Hilt
@HiltViewModel
class UserViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    private val userId: String = savedStateHandle["userId"] ?: ""
}
```

### 10.3 如何处理一次性事件（Toast/导航）？

```kotlin
// 使用 SharedFlow（推荐）
private val _event = MutableSharedFlow<UiEvent>()
val event: SharedFlow<UiEvent> = _event

// 发送事件
_event.emit(UiEvent.ShowToast("成功"))

// 观察
lifecycleScope.launch {
    viewModel.event.collect { event ->
        when (event) {
            is UiEvent.ShowToast -> Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
            is UiEvent.Navigate -> findNavController().navigate(event.destination)
        }
    }
}
```

---

## 11. 知识体系总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         架构模式知识体系                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   架构模式      │
                           └────────┬────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
  ┌───────────┐              ┌───────────┐              ┌───────────┐
  │    MVC    │              │    MVP    │              │   MVVM    │
  │           │              │           │              │           │
  │ 简单直接  │              │ 接口解耦  │              │ 数据绑定  │
  │ 职责混乱  │              │ 易于测试  │              │ 生命周期  │
  └───────────┘              └───────────┘              └───────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                                    ▼
                            ┌───────────┐
                            │    MVI    │
                            │           │
                            │ 单向数据流│
                            │ 不可变状态│
                            └───────────┘

  核心演进：
  ─────────────────────────────────────────────────────────────────────────
  1. 解耦：MVC → MVP → MVVM/MVI
  2. 可测试：Activity 臃肿 → Presenter/ViewModel 可测
  3. 状态管理：分散 → 集中
  4. 数据流：双向 → 单向

  推荐方案（2024+）：
  ─────────────────────────────────────────────────────────────────────────
  - 中小项目：MVVM + ViewModel + LiveData/Flow
  - 大型项目：MVVM + Clean Architecture
  - 复杂状态：MVI
```

---

> 作者：OpenClaw | 日期：2026-03-09