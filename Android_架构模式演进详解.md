# Android 架构模式演进详解

> 适用环境：Android 17（API 37）；示例采用 AndroidX ViewModel、Lifecycle 与 Kotlin Flow，架构模式本身不绑定平台发布版本。

> 作者：OpenClaw | 日期：2026-03-09

---

## 目录

- [1. 概述](#1-概述)
- [2. 架构演进历程](#2-架构演进历程)
- [3. MVC 架构](#3-mvc-架构)
  - [3.1 MVC 是什么](#31-mvc-是什么)
  - [3.2 MVC 结构图](#32-mvc-结构图)
  - [3.3 MVC 代码示例](#33-mvc-代码示例)
  - [3.4 MVC 优缺点](#34-mvc-优缺点)
- [4. MVP 架构](#4-mvp-架构)
  - [4.1 MVP 是什么](#41-mvp-是什么)
  - [4.2 MVP 结构图](#42-mvp-结构图)
  - [4.3 MVP 代码示例](#43-mvp-代码示例)
  - [4.4 MVP 优缺点](#44-mvp-优缺点)
- [5. MVVM 架构](#5-mvvm-架构)
  - [5.1 MVVM 是什么](#51-mvvm-是什么)
  - [5.2 MVVM 结构图](#52-mvvm-结构图)
  - [5.3 MVVM 三种实现方式](#53-mvvm-三种实现方式)
  - [5.4 LiveData 方式（传统）](#54-livedata-方式传统)
  - [5.5 DataBinding 方式](#55-databinding-方式)
  - [5.6 StateFlow 方式（生命周期感知）](#56-stateflow-方式生命周期感知)
  - [5.7 三种方式对比](#57-三种方式对比)
  - [5.8 MVVM 优缺点](#58-mvvm-优缺点)
- [6. MVI 架构](#6-mvi-架构)
  - [6.1 MVI 是什么](#61-mvi-是什么)
  - [6.2 MVI 结构图](#62-mvi-结构图)
  - [6.3 MVI 代码示例](#63-mvi-代码示例)
  - [6.4 MVI 优缺点](#64-mvi-优缺点)
- [7. 架构对比](#7-架构对比)
  - [7.2 MVVM vs MVI 的界限模糊](#72-mvvm-vs-mvi-的界限模糊)
- [8. 架构选择指南](#8-架构选择指南)
- [9. Clean Architecture](#9-clean-architecture)
- [10. 常见问题](#10-常见问题)
  - [10.1 MVVM 和 MVI 怎么选？](#101-mvvm-和-mvi-怎么选)
  - [10.2 ViewModel 如何传递参数？](#102-viewmodel-如何传递参数)
  - [10.3 如何处理一次性事件（Toast/导航）？](#103-如何处理一次性事件toast导航)
  - [10.4 LiveData postValue 和 setValue 区别？](#104-livedata-postvalue-和-setvalue-区别)
  - [10.5 Flow 的发射线程和收集线程是什么关系？](#105-flow-的发射线程和收集线程是什么关系)
  - [10.6 LiveData vs Flow 怎么选？](#106-livedata-vs-flow-怎么选)
- [11. 知识体系总结](#11-知识体系总结)
- [12. Android 17 下的状态与任务边界](#12-android-17-下的状态与任务边界)

---

## 1. 概述

Android 架构模式是组织代码的一种方式，目的是解决代码耦合、提高可维护性和可测试性。从早期的 MVC 到现代的 MVI，架构模式不断演进，每种模式都有其适用场景和优缺点。

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

### 5.6 StateFlow 方式（生命周期感知）

StateFlow 保存当前 UI 状态，ViewModel 负责加载与转换，View 只收集并渲染。下面以详情页为例：仓库通过工厂注入；SavedStateHandle 保存可重建页面的 ID，而不是保存大对象；刷新会取消前一次加载。

```kotlin
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import java.io.IOException
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class Article(val id: String, val title: String)
interface ArticleRepository { suspend fun find(id: String): Article }
sealed interface ArticleUi {
    data object Loading : ArticleUi
    data class Content(val article: Article) : ArticleUi
    data class Error(val message: String) : ArticleUi
}
class ArticleViewModel(
    private val savedState: SavedStateHandle,
    private val repository: ArticleRepository
) : ViewModel() {
    private val mutableUi = MutableStateFlow<ArticleUi>(ArticleUi.Loading)
    val ui: StateFlow<ArticleUi> = mutableUi.asStateFlow()
    private var loading: Job? = null

    init { reload() }

    fun open(id: String) {
        savedState["articleId"] = id
        reload()
    }
    fun reload() {
        loading?.cancel()
        val id = savedState.get<String>("articleId")
        if (id.isNullOrBlank()) {
            mutableUi.value = ArticleUi.Error("缺少文章 ID")
            return
        }
        loading = viewModelScope.launch {
            mutableUi.value = ArticleUi.Loading
            try {
                val article = repository.find(id)
                ensureActive() // 即使仓库未及时响应取消，也不提交旧结果
                mutableUi.value = ArticleUi.Content(article)
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (network: IOException) {
                mutableUi.value = ArticleUi.Error("加载失败，请重试")
            }
        }
    }
}
```

Fragment 的 Factory 使用 CreationExtras 创建带恢复能力的 SavedStateHandle。业务仓库由 Application 容器或 DI 提供；导航参数名称与 `articleId` 一致。

```kotlin
import androidx.fragment.app.viewModels
import androidx.lifecycle.createSavedStateHandle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory

// Fragment 字段；repository 是宿主提供的 ArticleRepository。
private val model: ArticleViewModel by viewModels {
    viewModelFactory {
        initializer { ArticleViewModel(createSavedStateHandle(), repository) }
    }
}
// onViewCreated 中：
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(androidx.lifecycle.Lifecycle.State.STARTED) {
        model.ui.collect { state ->
            when (state) {
                ArticleUi.Loading -> renderLoading()
                is ArticleUi.Content -> renderArticle(state.article)
                is ArticleUi.Error -> renderError(state.message, model::reload)
            }
        }
    }
}
```

`renderLoading/renderArticle/renderError` 是页面自己的渲染函数，每次都应更新 loading、内容和错误区的可见性。STARTED 以下停止收集不等于自动取消 ViewModel 的加载；网络任务归 ViewModel 所有，视图观察归 viewLifecycleOwner 所有。进程被回收后 ViewModel 会重建，使用保存的 ID 重新读取仓库；需要持久保存的编辑草稿应写数据库或文件。

参考：[ViewModel 工厂](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-factories)、[SavedStateHandle](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate)、[生命周期协程](https://developer.android.com/topic/libraries/architecture/coroutines)。

### 5.7 三种方式对比

```text
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

```text
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

```text
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

```text
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

        // 只在 UI 可见时收集；不是仅在销毁时才停止。
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.state.collect { state -> render(state) }
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

```text
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

```text
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

```text
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

- 优先明确 UI 层、数据层、单向数据流（UDF）与单一可信数据源，而不是按年份强制选择某个缩写。
- Domain/use case 层是可选层：跨多个 ViewModel 复用业务逻辑或 UI 层逻辑过于复杂时再引入，不能要求每个 CRUD 操作都多包一层。
- MVVM 和 MVI 不是 Android 17 的新旧 API 关系。复杂状态可以集中归约，但“使用 MVI”本身不保证串行化、无竞态或可恢复。
- View UI 用 `repeatOnLifecycle`；Fragment 应使用 `viewLifecycleOwner`。Compose 使用 `collectAsStateWithLifecycle()`，需单独引入匹配版本的 `lifecycle-runtime-compose`。

来源：[Android 架构建议](https://developer.android.com/topic/architecture/recommendations)。这些建议不要求升级全部 AndroidX artifact；Android 17 的平台行为与库版本应分开测试。

---

## 9. Clean Architecture

```text
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

```text
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

先区分可丢失提示与必须兑现的业务结果。`SharedFlow(replay=0)` 在无订阅者时不保留事件；extraBufferCapacity 也不会让离线订阅者收到历史事件。Channel 的接收语义同样不能提供进程死亡后的“恰好一次导航”。

必须确认的结果转为状态，并在 UI 成功处理后回传确认 ID：

```kotlin
data class PendingNavigation(val eventId: Long, val orderId: String)
data class CheckoutUi(val pending: PendingNavigation? = null)

// ViewModel 内；由结算成功结果生成 pending。
private val mutable = kotlinx.coroutines.flow.MutableStateFlow(CheckoutUi())
val ui = mutable.asStateFlow()

fun navigationHandled(eventId: Long) {
    mutable.update { state ->
        if (state.pending?.eventId == eventId) state.copy(pending = null) else state
    }
}
```

UI 检查当前导航目的地并执行跳转，随后确认该 ID；旧确认不能清掉新结果。旋转重建后若仍有 pending，可以继续处理；进程死亡恢复需要 SavedStateHandle 或持久层保存必要信息。即使使用确认协议，崩溃仍可能发生在跳转和确认之间，因此导航目标必须幂等。Toast、动画等允许丢失的提示则可用无 replay 的事件流。

参考：[UI 事件处理](https://developer.android.com/topic/architecture/ui-layer/events)、[SharedFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)。

### 10.4 LiveData postValue 和 setValue 区别？

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LiveData postValue vs setValue                          │
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
  - 最终会调用 setValue()
  - 子线程调用时使用

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  注意事项：                                                             │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  1. postValue 多次调用，只会通知最后一次值                              │
  │                                                                         │
  │     // 子线程                                                           │
  │     liveData.postValue(1)                                               │
  │     liveData.postValue(2)                                               │
  │     liveData.postValue(3)                                               │
  │     // 观察者只会收到 3，中间值被合并                                    │
  │                                                                         │
  │  2. setValue 在子线程调用会崩溃                                         │
  │                                                                         │
  │     // 错误！                                                            │
  │     thread { liveData.setValue(1) }  // CalledFromWrongThreadException  │
  │                                                                         │
  │     // 正确                                                              │
  │     thread { liveData.postValue(1) }                                    │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

```kotlin
// 示例：正确使用
class UserViewModel(private val repository: UserRepository) : ViewModel() {

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    fun loadUsers() {
        viewModelScope.launch(Dispatchers.IO) {
            // 子线程获取数据
            val result = repository.getUsers()

            // 方式1：postValue（子线程）
            _users.postValue(result.getOrNull())

            // 方式2：切回主线程 setValue
            // withContext(Dispatchers.Main) {
            //     _users.value = result.getOrNull()
            // }
        }
    }
}
```

### 10.5 Flow 的发射线程和收集线程是什么关系？

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Flow 线程模型                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  核心概念：
  ─────────────────────────────────────────────────────────────────────────
  - Flow 是冷流：不收集就不执行
  - 发射线程：由 flowOn() 决定
  - 收集线程：由 collect 所在的协程决定

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  flowOn() 的作用：                                                      │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  1. 改变上游（发射）的执行线程                                          │
  │  2. 不影响下游（收集）的执行线程                                        │
  │  3. 多次 flowOn() 只有最后一个生效                                     │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

```kotlin
// ==================== 示例1：基本线程控制 ====================
fun getUsers(): Flow<List<User>> = flow {
    // 这里在 IO 线程执行（由 flowOn 决定）
    println("发射线程: ${Thread.currentThread().name}")  // DefaultDispatcher-worker-1

    val users = apiService.getUsers()  // 网络请求
    emit(users)  // 发射数据
}.flowOn(Dispatchers.IO)  // 指定上游在 IO 线程

// ViewModel
viewModelScope.launch {
    // 这里在主线程执行（由 viewModelScope 决定）
    repository.getUsers().collect { users ->
        println("收集线程: ${Thread.currentThread().name}")  // main
        _state.update { it.copy(users = users) }
    }
}

// 输出：
// 发射线程: DefaultDispatcher-worker-1
// 收集线程: main
```

```kotlin
// ==================== 示例2：flowOn 只影响上游 ====================
fun getData(): Flow<Int> = flow {
    // 上游：flowOn(Dispatchers.IO) 生效
    println("上游线程: ${Thread.currentThread().name}")
    repeat(10) {
        emit(it)
        delay(100)
    }
}
    .map {
        // 中间操作：也受 flowOn(Dispatchers.IO) 影响
        println("map 线程: ${Thread.currentThread().name}")
        it * 2
    }
    .flowOn(Dispatchers.IO)  // 上游和中间操作都在 IO 线程

// 收集
lifecycleScope.launch {
    // 下游：在 launch 的上下文（主线程）
    getData().collect {
        println("collect 线程: ${Thread.currentThread().name}")
    }
}

// 输出：
// 上游线程: DefaultDispatcher-worker-1
// map 线程: DefaultDispatcher-worker-1
// collect 线程: main
```

```kotlin
// ==================== 示例3：StateFlow 线程安全 ====================
class UserViewModel : ViewModel() {

    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun loadData() {
        // 在 IO 线程发射
        viewModelScope.launch(Dispatchers.IO) {
            val data = repository.getData()

            // StateFlow.value 是线程安全的
            // 内部有同步机制，可以在任意线程调用
            _state.update { it.copy(data = data) }
        }

        // 或者
        viewModelScope.launch {
            repository.getDataFlow()
                .flowOn(Dispatchers.IO)
                .collect { data ->
                    // 这里在主线程（viewModelScope 默认主线程）
                    _state.update { it.copy(data = data) }
                }
        }
    }
}
```

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Flow 线程控制总结                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  规则：                                                                 │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  1. flow { } 里的代码：由最近的 flowOn() 决定                          │
  │  2. collect { } 里的代码：由 collect 所在的协程决定                     │
  │  3. StateFlow.value / update：线程安全，任意线程可调用                  │
  │                                                                         │
  │  常见模式：                                                             │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  // ViewModel 中                                                        │
  │  viewModelScope.launch {                    // 主线程                   │
  │      repository.getData()                   // 返回 Flow               │
  │          .flowOn(Dispatchers.IO)            // 上游在 IO 线程          │
  │          .collect { data ->                 // 下游在主线程            │
  │              _state.update { ... }          // 更新状态                │
  │          }                                                              │
  │  }                                                                      │
  │                                                                         │
  │  UI 更新：collect 在主线程 → 可以直接更新 UI                           │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 10.6 LiveData vs Flow 怎么选？

LiveData 适合既有 View/XML 页面中的可观察状态，它主动感知 LifecycleOwner 并在活跃状态派发；Flow 是协程流抽象，本身不感知 Android 生命周期，需要在 UI 边界结合 repeatOnLifecycle。StateFlow 保存当前状态，SharedFlow 可表达多播流，但不自带持久事件队列。

| 场景 | 选择与理由 |
|---|---|
| 既有 XML/DataBinding 页面 | 可以继续使用 LiveData，避免仅为替换类型重写稳定业务 |
| Repository 数据变换、合并、重试 | Flow 提供结构化的操作符链，取消与协程作用域一致 |
| ViewModel 当前 UI 状态 | StateFlow + 生命周期感知收集，重新订阅得到最近状态 |
| 必须兑现的业务结果 | 保存为状态并确认消费，不能只靠无 replay 事件流 |

从 Flow 转 LiveData 或从 LiveData 转 Flow 时明确谁订阅、何时停止，以及冷流是否会重复触发网络请求。不要在同一个页面维护两份可独立修改的 UI 真相。

参考：[Android 架构建议](https://developer.android.com/topic/architecture/recommendations)、[生命周期协程](https://developer.android.com/topic/libraries/architecture/coroutines)。

## 11. 知识体系总结

```text
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

  架构选择原则：
  ─────────────────────────────────────────────────────────────────────────
  - 中小项目：MVVM + ViewModel + LiveData/Flow
  - Domain/use case：按复用与复杂度引入，不强制所有项目分层
  - 复杂状态：MVI
```

---

> 作者：OpenClaw | 日期：2026-03-09

## 12. Android 17 下的状态与任务边界

应用进程、Activity、Fragment View 和 ViewModel 不是同一生命周期。配置变化保留 ViewModel 不代表进程死亡保留内存；`SavedStateHandle` 用于轻量恢复状态，数据库负责持久业务事实。Repository 不持有页面 View，也不把 Activity Context 放进应用级单例。

Android 17/API 37 的本地网络权限改变局域网功能的进入条件，不改变 MVVM/MVI 的单向数据流：UI 发起授权，ViewModel 接收授权结果，Repository 只处理已满足前置条件的请求。无锁 MessageQueue 的实现变化也不改变 Handler 公共调用方式；架构层不反射其内部消息链表。

验收同一页面时依次覆盖旋转、后台恢复、返回栈重建、重复点击重试、请求乱序、权限拒绝和进程恢复。用这些场景检查状态归属，比仅按类名判断“是否 MVI”更有效。

参考：[Android 17 行为变化](https://developer.android.com/about/versions/17/behavior-changes-17)、[应用架构建议](https://developer.android.com/topic/architecture/recommendations)。
