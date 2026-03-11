# Android Jetpack Compose 详解

> 作者：OpenClaw | 日期：2026-03-11  
> Android 现代声明式 UI 工具包 | Kotlin 优先，告别 XML

---

## 📚 目录

### 第一篇：Compose 基础

**第 1 章 Compose 概述**
- 1.1 [什么是 Jetpack Compose？](#11-什么是-jetpack-compose)
- 1.2 [核心优势](#12-核心优势)
- 1.3 [与传统 View 对比](#13-与传统-view-对比)
- 1.4 [开发环境搭建](#14-开发环境搭建)

**第 2 章 Kotlin 基础**
- 2.1 [Kotlin 语言特性](#21-kotlin-语言特性)
- 2.2 [高阶函数与 Lambda](#22-高阶函数与-lambda)
- 2.3 [扩展函数](#23-扩展函数)
- 2.4 [协程基础](#24-协程基础)

**第 3 章 Composable 函数**
- 3.1 [Composable 注解](#31-composable-注解)
- 3.2 [函数规则与约定](#32-函数规则与约定)
- 3.3 [remember 与记忆化](#33-remember-与记忆化)
- 3.4 [重组与智能跳过](#34-重组与智能跳过)

**第 4 章 State 状态管理**
- 4.1 [State 与 MutableState](#41-state-与-mutablestate)
- 4.2 [状态提升](#42-状态提升)
- 4.3 [rememberSaveable](#43-remembersaveable)
- 4.4 [StateFlow 集成](#44-stateflow-集成)

**第 5 章 Modifier 修饰符**
- 5.1 [Modifier 基础](#51-modifier-基础)
- 5.2 [常用修饰符](#52-常用修饰符)
- 5.3 [顺序的重要性](#53-顺序的重要性)
- 5.4 [自定义 Modifier](#54-自定义-modifier)

**第 6 章 布局组件**
- 6.1 [Column 纵向布局](#61-column-纵向布局)
- 6.2 [Row 横向布局](#62-row-横向布局)
- 6.3 [Box 堆叠布局](#63-box-堆叠布局)
- 6.4 [ConstraintLayout](#64-constraintlayout)
- 6.5 [自定义 Layout](#65-自定义-layout)

---

### 第二篇：Compose 进阶

**第 7 章 Material Design 组件**
- 7.1 [Button 按钮](#71-button-按钮)
- 7.2 [TextField 输入框](#72-textfield-输入框)
- 7.3 [Card 卡片](#73-card-卡片)
- 7.4 [Dialog 对话框](#74-dialog-对话框)
- 7.5 [其他组件](#75-其他组件)

**第 8 章 列表**
- 8.1 [LazyColumn](#81-lazycolumn)
- 8.2 [LazyRow](#82-lazyrow)
- 8.3 [LazyVerticalGrid](#83-lazyverticalgrid)
- 8.4 [性能优化](#84-性能优化)

**第 9 章 动画**
- 9.1 [AnimatedVisibility](#91-animatedvisibility)
- 9.2 [animate*AsState](#92-animateasstate)
- 9.3 [Crossfade](#93-crossfade)
- 9.4 [infiniteTransition](#94-infinitetransition)
- 9.5 [AnimationSpec](#95-animationspec)

**第 10 章 主题与样式**
- 10.1 [Material Theme](#101-material-theme)
- 10.2 [ColorScheme](#102-colorscheme)
- 10.3 [Typography](#103-typography)
- 10.4 [Shapes](#104-shapes)
- 10.5 [暗黑模式](#105-暗黑模式)

**第 11 章 ViewModel 集成**
- 11.1 [viewModel() 函数](#111-viewmodel-函数)
- 11.2 [StateFlow 收集](#112-stateflow-收集)
- 11.3 [Hilt 集成](#113-hilt-集成)
- 11.4 [SavedStateHandle](#114-savedstatehandle)

**第 12 章 协程集成**
- 12.1 [LaunchedEffect](#121-launchedeffect)
- 12.2 [rememberCoroutineScope](#122-remembercoroutinescope)
- 12.3 [DisposableEffect](#123-disposableeffect)
- 12.4 [SideEffect](#124-sideeffect)

---

### 第三篇：Compose 高级

**第 13 章 Navigation 导航**
- 13.1 [NavHost 基础](#131-navhost-基础)
- 13.2 [参数传递](#132-参数传递)
- 13.3 [Bottom Navigation](#133-bottom-navigation)
- 13.4 [深层链接](#134-深层链接)

**第 14 章 与传统 View 互操作**
- 14.1 [AndroidView](#141-androidview)
- 14.2 [ComposeView](#142-composeview)
- 14.3 [渐进式迁移](#143-渐进式迁移)
- 14.4 [最佳实践](#144-最佳实践)

**第 15 章 手势处理**
- 15.1 [点击手势](#151-点击手势)
- 15.2 [拖动手势](#152-拖动手势)
- 15.3 [缩放与旋转](#153-缩放与旋转)
- 15.4 [多点触控](#154-多点触控)

**第 16 章 Canvas 自定义绘制**
- 16.1 [DrawScope](#161-drawscope)
- 16.2 [基本图形](#162-基本图形)
- 16.3 [Path 路径](#163-path-路径)
- 16.4 [渐变与阴影](#164-渐变与阴影)

**第 17 章 性能优化**
- 17.1 [稳定性与跳过](#171-稳定性与跳过)
- 17.2 [重组优化](#172-重组优化)
- 17.3 [布局优化](#173-布局优化)
- 17.4 [性能分析工具](#174-性能分析工具)

**第 18 章 面试常见问题**
- 18.1 [Compose 原理](#181-compose-原理)
- 18.2 [重组机制](#182-重组机制)
- 18.3 [与传统 View 对比](#183-与传统-view-对比)
- 18.4 [性能优化](#184-性能优化)
- 18.5 [最佳实践](#185-最佳实践)

---

## 第一篇：Compose 基础

---

## 第 1 章 Compose 概述

### 1.1 什么是 Jetpack Compose？

**Jetpack Compose** 是 Android 的现代声明式 UI 工具包，完全使用 Kotlin 构建 UI。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Compose 核心特性                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │   Compose    │
                         └──────┬───────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  声明式 UI    │      │  Kotlin 优先  │      │  无需 XML     │
│               │      │               │      │               │
│ - 描述 UI    │      │ - 简洁语法   │      │ - 代码即 UI  │
│ - 状态驱动   │      │ - 类型安全   │      │ - 实时预览   │
│ - 自动更新   │      │ - 空安全     │      │ - 热重载     │
└───────────────┘      └───────────────┘      └───────────────┘
```

### 1.2 核心优势

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Compose vs 传统 View 开发                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────┐
│       特性        │    Compose      │    传统 View     │
├──────────────────┼──────────────────┼──────────────────┤
│  UI 定义方式     │   Kotlin 代码   │   XML 布局      │
│  编程范式        │   声明式        │   命令式        │
│  状态管理        │   自动响应      │   手动更新      │
│  代码量          │   ⭐⭐⭐⭐⭐      │   ⭐⭐⭐         │
│  可测试性        │   ⭐⭐⭐⭐⭐      │   ⭐⭐⭐         │
│  学习曲线        │   ⭐⭐⭐⭐        │   ⭐⭐⭐⭐⭐      │
│  预览功能        │   实时预览      │   需要运行      │
│  性能            │   智能重组      │   View 开销     │
│  兼容性          │   Android 5+   │   全版本        │
└──────────────────┴──────────────────┴──────────────────┘
```

**Compose 的优势**：

1. **声明式 UI**：描述 UI 是什么，而不是如何构建
2. **Kotlin 优先**：完全使用 Kotlin，无需 XML
3. **状态驱动**：UI 自动响应状态变化
4. **代码简洁**：减少样板代码，提高开发效率
5. **实时预览**：Android Studio 中实时预览 UI
6. **智能重组**：只更新变化的部分
7. **互操作**：与传统 View 无缝协作

### 1.3 与传统 View 对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    命令式 vs 声明式                                        │
└─────────────────────────────────────────────────────────────────────────────┘

【命令式（传统 View）】
┌───────────────────────────────────────────────────────────────────────────┐
│  // 找到 View                                                              │
│  val textView = findViewById<TextView>(R.id.textView)                     │
│  val button = findViewById<Button>(R.id.button)                           │
│                                                                            │
│  // 手动设置属性                                                           │
│  textView.text = "Hello"                                                   │
│  textView.setTextColor(Color.RED)                                          │
│  button.visibility = View.VISIBLE                                          │
│                                                                            │
│  // 状态变化时需要手动更新                                                  │
│  fun updateUI(user: User) {                                                │
│      textView.text = user.name                                             │
│      button.isEnabled = user.isActive                                      │
│  }                                                                         │
└───────────────────────────────────────────────────────────────────────────┘

【声明式（Compose）】
┌───────────────────────────────────────────────────────────────────────────┐
│  @Composable                                                               │
│  fun UserView(user: User) {                                                │
│      Column {                                                              │
│          Text(                                                             │
│              text = user.name,                                             │
│              color = Color.Red                                             │
│          )                                                                 │
│          Button(                                                           │
│              enabled = user.isActive,                                      │
│              onClick = { }                                                 │
│          ) {                                                               │
│              Text("Click")                                                 │
│          }                                                                 │
│      }                                                                     │
│  }                                                                         │
│  // user 变化时，UI 自动更新                                               │
└───────────────────────────────────────────────────────────────────────────┘
```

### 1.4 开发环境搭建

#### 项目配置

```kotlin
// build.gradle (Module)
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    buildFeatures {
        compose = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.3"
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // Compose BOM（统一版本管理）
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    
    // 核心组件
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    
    // Activity 集成
    implementation("androidx.activity:activity-compose:1.8.2")
    
    // ViewModel 集成
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    
    // 调试工具
    debugImplementation("androidx.compose.ui:ui-tooling")
}
```

#### Hello Compose

```kotlin
// MainActivity.kt
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            // 设置 Material 主题
            MyApplicationTheme {
                // Surface 是容器
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Greeting("Android")
                }
            }
        }
    }
}

// @Composable 注解标记可组合函数
@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

// @Preview 注解用于预览
@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    MyApplicationTheme {
        Greeting("Android")
    }
}
```

---

## 第 2 章 Kotlin 基础

### 2.1 Kotlin 语言特性

```kotlin
/**
 * Compose 中常用的 Kotlin 特性
 */

// 1. 数据类（不可变）
data class User(
    val id: Int,
    val name: String,
    val email: String
)

// 2. 解构声明
val (id, name, email) = user

// 3. 默认参数
@Composable
fun Card(
    title: String,
    subtitle: String = "",
    modifier: Modifier = Modifier
) { }

// 4. 命名参数
Card(
    title = "Hello",
    modifier = Modifier.padding(16.dp)
)

// 5. 尾随 Lambda
// 这两种写法等价
Button(onClick = { }, content = { Text("Click") })
Button(onClick = { }) {
    Text("Click")
}

// 6. 作用域函数
Column {
    // this: ColumnScope
    Text("Hello")
}
```

### 2.2 高阶函数与 Lambda

```kotlin
/**
 * 高阶函数：接收函数作为参数或返回函数
 */

// 接收 Lambda 参数
@Composable
fun List(
    items: List<String>,
    itemContent: @Composable (String) -> Unit
) {
    Column {
        items.forEach { item ->
            itemContent(item)
        }
    }
}

// 使用
List(items = listOf("A", "B", "C")) { item ->
    Text(item)
}

// 带接收者的 Lambda
@Composable
fun ColumnScope.Header(title: String) {
    // this: ColumnScope
    Text(title, style = MaterialTheme.typography.headlineMedium)
}
```

### 2.3 扩展函数

```kotlin
/**
 * 扩展函数：为现有类添加新功能
 */

// 扩展 Modifier
fun Modifier.circleCrop(): Modifier = this
    .clip(CircleShape)
    .border(2.dp, Color.White, CircleShape)

// 使用
Image(
    painter = painterResource(R.drawable.avatar),
    modifier = Modifier
        .size(80.dp)
        .circleCrop()
)

// 扩展 Composable
@Composable
fun String.toAnnotatedString(): AnnotatedString {
    return buildAnnotatedString {
        append(this@toAnnotatedString)
    }
}
```

### 2.4 协程基础

```kotlin
/**
 * 协程：异步编程
 */

// 1. 协程构建器
suspend fun fetchUser(): User {
    return withContext(Dispatchers.IO) {
        // 网络请求
        api.getUser()
    }
}

// 2. 在 Composable 中启动协程
@Composable
fun DataLoader() {
    LaunchedEffect(Unit) {
        val user = fetchUser()
        // 更新状态
    }
}

// 3. rememberCoroutineScope
@Composable
fun ClickHandler() {
    val scope = rememberCoroutineScope()
    
    Button(onClick = {
        scope.launch {
            // 执行协程
        }
    }) {
        Text("Click")
    }
}
```

---

## 第 3 章 Composable 函数

### 3.1 Composable 注解

```kotlin
/**
 * @Composable 注解
 * 
 * 作用：
 * 1. 标记函数为可组合函数
 * 2. 编译器会生成额外代码
 * 3. 只能在其他 Composable 中调用
 */

// 基本用法
@Composable
fun SimpleText(text: String) {
    Text(text)
}

// 带默认参数
@Composable
fun Card(
    title: String,
    modifier: Modifier = Modifier,
    onClick: () -> Unit = {}
) {
    Surface(
        modifier = modifier.clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Text(title)
    }
}

// 接收 Composable 参数
@Composable
fun Container(
    content: @Composable () -> Unit
) {
    Surface {
        content()
    }
}

// 使用
Container {
    Text("Hello")
}
```

### 3.2 函数规则与约定

```kotlin
/**
 * Composable 函数规则
 */

// ✅ 正确：名词，表示 UI 组件
@Composable
fun UserProfileCard() { }

@Composable
fun MovieList() { }

// ✅ 正确：小写开头的扩展函数返回 Modifier
fun Modifier.roundedCorner(radius: Dp): Modifier {
    return this.clip(RoundedCornerShape(radius))
}

// ❌ 错误：动词，不表示 UI
@Composable
fun LoadData() { }  // 应该是普通函数

// ❌ 错误：有返回值
@Composable
fun WrongReturn(): String {  // Composable 应返回 Unit
    return "Hello"
}

// ✅ 正确：返回 Unit（隐式）
@Composable
fun CorrectFunction() {
    // 函数体
}
```

### 3.3 remember 与记忆化

```kotlin
/**
 * remember：在重组中保持状态
 */

@Composable
fun RememberExample() {
    // 1. 基础 remember
    var count by remember { mutableStateOf(0) }
    
    // 2. remember 计算值
    val formattedDate = remember { 
        SimpleDateFormat("yyyy-MM-dd").format(Date())
    }
    
    // 3. remember 带依赖
    val filteredList = remember(items, filter) {
        items.filter { it.matches(filter) }
    }
    
    // 4. rememberSaveable：配置更改后保持
    var text by rememberSaveable { mutableStateOf("") }
    
    // 5. 自定义 Saver
    data class User(val id: Int, val name: String)
    
    val userSaver = Saver<User?, String>(
        save = { it?.let { "${it.id},${it.name}" } },
        restore = { 
            it?.split(",")?.let { (id, name) -> 
                User(id.toInt(), name) 
            }
        }
    )
    
    var user by rememberSaveable(stateSaver = userSaver) { 
        mutableStateOf(null) 
    }
}
```

### 3.4 重组与智能跳过

```kotlin
/**
 * 重组（Recomposition）
 * 
 * 特点：
 * 1. 智能跳过：输入未变化时跳过
 * 2. 可能频繁执行：避免副作用
 * 3. 可并行执行：不要依赖外部状态
 * 4. 可能被放弃：乐观执行
 */

@Composable
fun RecompositionExample(name: String) {
    // ❌ 错误：在 Composable 中执行副作用
    // loadData()  // 每次重组都会执行
    
    // ✅ 正确：使用 LaunchedEffect
    LaunchedEffect(name) {
        loadData(name)
    }
    
    // ✅ 正确：使用 remember 缓存计算
    val processedName = remember(name) {
        name.uppercase()
    }
    
    Text(processedName)
}

// 稳定性注解
@Immutable  // 标记为完全不可变
data class ImmutableUser(
    val id: Int,
    val name: String
)

@Stable  // 标记为可观察的变化
class StableUser {
    var name: String by mutableStateOf("")
}
```

---

## 第 4 章 State 状态管理

### 4.1 State 与 MutableState

```kotlin
/**
 * State：可观察的状态容器
 */

@Composable
fun StateExample() {
    // 1. 创建状态
    var count by remember { mutableStateOf(0) }
    val textState = remember { mutableStateOf("") }
    
    // 2. 读取状态
    Text("Count: $count")
    Text("Text: ${textState.value}")
    
    // 3. 修改状态
    Button(onClick = { count++ }) {
        Text("Increment")
    }
    
    // 4. 集合状态
    val items = remember { mutableStateListOf<String>() }
    items.add("New Item")
    
    val map = remember { mutableStateMapOf<String, Int>() }
    map["key"] = 123
}
```

### 4.2 状态提升

```kotlin
/**
 * 状态提升：将状态移到调用者
 */

// ❌ 错误：状态在组件内部
@Composable
fun BadCounter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// ✅ 正确：状态提升到调用者
@Composable
fun GoodCounter(
    count: Int,              // 状态由外部传入
    onIncrement: () -> Unit  // 事件由外部处理
) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

// 使用
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    
    GoodCounter(
        count = count,
        onIncrement = { count++ }
    )
}
```

### 4.3 rememberSaveable

```kotlin
/**
 * rememberSaveable：配置更改后保持状态
 */

@Composable
fun SaveableExample() {
    // 1. 基础用法
    var text by rememberSaveable { mutableStateOf("") }
    
    // 2. 保存列表
    var items by rememberSaveable { mutableStateOf(listOf<String>()) }
    
    // 3. 自定义 Saver
    data class User(val id: Int, val name: String)
    
    val userSaver = listSaver<User, Any>(
        save = { listOf(it.id, it.name) },
        restore = { User(it[0] as Int, it[1] as String) }
    )
    
    var user by rememberSaveable(stateSaver = userSaver) { 
        mutableStateOf(User(0, "")) 
    }
}
```

### 4.4 StateFlow 集成

```kotlin
/**
 * StateFlow 与 Compose 集成
 */

// ViewModel
class UserViewModel : ViewModel() {
    private val _user = MutableStateFlow(User())
    val user: StateFlow<User> = _user.asStateFlow()
    
    fun updateName(name: String) {
        _user.update { it.copy(name = name) }
    }
}

// Composable
@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    // 收集 StateFlow
    val user by viewModel.user.collectAsState()
    
    Column {
        Text("Name: ${user.name}")
        Button(onClick = { viewModel.updateName("New Name") }) {
            Text("Update")
        }
    }
}
```

---

## 第 5 章 Modifier 修饰符

### 5.1 Modifier 基础

```kotlin
/**
 * Modifier：修饰 Composable 的外观和行为
 */

@Composable
fun ModifierBasics() {
    Box(
        modifier = Modifier
            .size(100.dp)           // 大小
            .padding(16.dp)         // 内边距
            .background(Color.Blue) // 背景
            .border(2.dp, Color.Red)// 边框
            .clickable { }          // 点击
    )
}
```

### 5.2 常用修饰符

```kotlin
@Composable
fun CommonModifiers() {
    Column {
        // ===== 尺寸 =====
        Box(Modifier.size(100.dp))
        Box(Modifier.width(100.dp).height(50.dp))
        Box(Modifier.fillMaxSize())
        Box(Modifier.fillMaxWidth())
        Box(Modifier.wrapContentSize())
        
        // ===== 间距 =====
        Box(Modifier.padding(16.dp))
        Box(Modifier.padding(horizontal = 16.dp, vertical = 8.dp))
        
        // ===== 背景 =====
        Box(Modifier.background(Color.Blue))
        Box(Modifier.background(Color.Blue, RoundedCornerShape(8.dp)))
        
        // ===== 边框 =====
        Box(Modifier.border(2.dp, Color.Red))
        Box(Modifier.border(2.dp, Color.Red, RoundedCornerShape(8.dp)))
        
        // ===== 裁剪 =====
        Box(Modifier.clip(RoundedCornerShape(8.dp)))
        Box(Modifier.clip(CircleShape))
        
        // ===== 变换 =====
        Box(Modifier.alpha(0.5f))
        Box(Modifier.rotate(45f))
        Box(Modifier.scale(1.5f))
        
        // ===== 布局 =====
        Row {
            Box(Modifier.weight(1f).height(50.dp).background(Color.Red))
            Box(Modifier.weight(2f).height(50.dp).background(Color.Blue))
        }
    }
}
```

### 5.3 顺序的重要性

```kotlin
/**
 * Modifier 顺序影响最终效果
 */

@Composable
fun ModifierOrder() {
    Column {
        // 背景包含 padding 区域
        Box(
            modifier = Modifier
                .padding(16.dp)
                .background(Color.Blue)
                .size(100.dp)
        )
        
        // 背景不包含 padding 区域
        Box(
            modifier = Modifier
                .background(Color.Blue)
                .padding(16.dp)
                .size(100.dp)
        )
        
        // 点击区域顺序
        Box(
            modifier = Modifier
                .size(100.dp)
                .clickable { }  // 只有 100.dp 可点击
                .background(Color.Red)
        )
        
        Box(
            modifier = Modifier
                .clickable { }  // 整个区域可点击
                .size(100.dp)
                .background(Color.Red)
        )
    }
}
```

### 5.4 自定义 Modifier

```kotlin
/**
 * 自定义 Modifier
 */

// 使用 composed
fun Modifier.shimmer(): Modifier = composed {
    var size by remember { mutableStateOf(IntSize.Zero) }
    val transition = rememberInfiniteTransition(label = "shimmer")
    
    val startOffsetX by transition.animateFloat(
        initialValue = -2 * size.width.toFloat(),
        targetValue = 2 * size.width.toFloat(),
        animationSpec = infiniteRepeatable(tween(1000)),
        label = "offset"
    )
    
    background(
        brush = Brush.linearGradient(
            colors = listOf(Color.LightGray, Color.White, Color.LightGray),
            start = Offset(startOffsetX, 0f),
            end = Offset(startOffsetX + size.width.toFloat(), size.height.toFloat())
        )
    )
    .onGloballyPositioned { size = it.size }
}

// 使用
@Composable
fun ShimmerExample() {
    Box(Modifier.size(200.dp).shimmer())
}
```

---

## 第 6 章 布局组件

### 6.1 Column 纵向布局

```kotlin
/**
 * Column：垂直排列子元素
 */

@Composable
fun ColumnExample() {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.SpaceEvenly,  // 垂直排列
        horizontalAlignment = Alignment.CenterHorizontally  // 水平对齐
    ) {
        Text("Item 1")
        Text("Item 2")
        Text("Item 3")
    }
}

// Arrangement 选项：
// - Top: 顶部对齐
// - Center: 居中
// - Bottom: 底部对齐
// - SpaceBetween: 两端对齐
// - SpaceEvenly: 均匀分布
// - SpaceAround: 环绕分布

// Alignment 选项：
// - Start: 左对齐
// - CenterHorizontally: 水平居中
// - End: 右对齐
```

### 6.2 Row 横向布局

```kotlin
/**
 * Row：水平排列子元素
 */

@Composable
fun RowExample() {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text("Left")
        Text("Center")
        Text("Right")
    }
}
```

### 6.3 Box 堆叠布局

```kotlin
/**
 * Box：层叠子元素
 */

@Composable
fun BoxExample() {
    Box(modifier = Modifier.size(200.dp)) {
        // 底层
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Blue)
        )
        
        // 居中
        Text(
            text = "Center",
            modifier = Modifier.align(Alignment.Center)
        )
        
        // 右下角
        Text(
            text = "Bottom End",
            modifier = Modifier.align(Alignment.BottomEnd)
        )
    }
}
```

### 6.4 ConstraintLayout

```kotlin
/**
 * ConstraintLayout：约束布局
 */

// 添加依赖
// implementation("androidx.constraintlayout:constraintlayout-compose:1.0.1")

@Composable
fun ConstraintLayoutExample() {
    ConstraintLayout(modifier = Modifier.fillMaxSize()) {
        // 创建引用
        val (title, subtitle, button) = createRefs()
        
        Text(
            text = "Title",
            modifier = Modifier.constrainAs(title) {
                top.linkTo(parent.top, margin = 16.dp)
                start.linkTo(parent.start, margin = 16.dp)
            }
        )
        
        Text(
            text = "Subtitle",
            modifier = Modifier.constrainAs(subtitle) {
                top.linkTo(title.bottom, margin = 8.dp)
                start.linkTo(title.start)
            }
        )
        
        Button(
            onClick = { },
            modifier = Modifier.constrainAs(button) {
                top.linkTo(subtitle.bottom, margin = 16.dp)
                start.linkTo(parent.start)
                end.linkTo(parent.end)
            }
        ) {
            Text("Button")
        }
    }
}
```

### 6.5 自定义 Layout

```kotlin
/**
 * 自定义 Layout
 */

@Composable
fun StaggeredGrid(
    rows: Int,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(content, modifier) { measurables, constraints ->
        // 测量子元素
        val placeables = measurables.map { it.measure(constraints) }
        
        // 计算行高
        val rowHeights = IntArray(rows) { 0 }
        placeables.forEachIndexed { index, placeable ->
            val row = index % rows
            rowHeights[row] = maxOf(rowHeights[row], placeable.height)
        }
        
        // 计算总高度
        val totalHeight = rowHeights.sum()
        
        // 设置布局大小
        layout(constraints.maxWidth, totalHeight) {
            // 放置子元素
            val rowX = IntArray(rows) { 0 }
            val rowY = IntArray(rows) { 0 }
            
            placeables.forEachIndexed { index, placeable ->
                val row = index % rows
                placeable.place(rowX[row], rowY[row])
                rowX[row] += placeable.width
                rowY[row + 1] = rowY[row] + rowHeights[row]
            }
        }
    }
}
```

---

## 第 7 章 Material Design 组件

### 7.1 Button 按钮

```kotlin
/**
 * Button 组件
 */

@Composable
fun ButtonExamples() {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        // 填充按钮
        Button(onClick = { }) {
            Text("Filled Button")
        }
        
        // 描边按钮
        OutlinedButton(onClick = { }) {
            Text("Outlined Button")
        }
        
        // 文字按钮
        TextButton(onClick = { }) {
            Text("Text Button")
        }
        
        // elevated 按钮
        ElevatedButton(onClick = { }) {
            Text("Elevated Button")
        }
        
        // 图标按钮
        IconButton(onClick = { }) {
            Icon(Icons.Default.Favorite, "Favorite")
        }
        
        // 悬浮按钮
        FloatingActionButton(onClick = { }) {
            Icon(Icons.Default.Add, "Add")
        }
        
        // 带图标的按钮
        Button(onClick = { }) {
            Icon(Icons.Default.Add, null, Modifier.size(18.dp))
            Spacer(Modifier.width(8.dp))
            Text("Add")
        }
    }
}
```

### 7.2 TextField 输入框

```kotlin
/**
 * TextField 组件
 */

@Composable
fun TextFieldExamples() {
    var text by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        // 基础输入框
        TextField(
            value = text,
            onValueChange = { text = it },
            label = { Text("Label") }
        )
        
        // 描边输入框
        OutlinedTextField(
            value = text,
            onValueChange = { text = it },
            label = { Text("Label") },
            placeholder = { Text("Placeholder") },
            leadingIcon = { Icon(Icons.Default.Person, null) },
            singleLine = true
        )
        
        // 密码输入框
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            visualTransformation = if (passwordVisible) 
                VisualTransformation.None 
            else 
                PasswordVisualTransformation(),
            trailingIcon = {
                IconButton(onClick = { passwordVisible = !passwordVisible }) {
                    Icon(
                        if (passwordVisible) Icons.Default.Visibility
                        else Icons.Default.VisibilityOff,
                        "Toggle"
                    )
                }
            }
        )
    }
}
```

### 7.3 Card 卡片

```kotlin
/**
 * Card 组件
 */

@Composable
fun CardExamples() {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        // 基础卡片
        Card {
            Text("Card content", Modifier.padding(16.dp))
        }
        
        // Elevated 卡片
        ElevatedCard {
            Text("Elevated card", Modifier.padding(16.dp))
        }
        
        // 自定义卡片
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            ),
            elevation = CardDefaults.cardElevation(8.dp)
        ) {
            Column(Modifier.padding(16.dp)) {
                Text("Card Title", style = MaterialTheme.typography.titleLarge)
                Spacer(Modifier.height(8.dp))
                Text("Card content")
            }
        }
    }
}
```

### 7.4 Dialog 对话框

```kotlin
/**
 * Dialog 组件
 */

@Composable
fun DialogExamples() {
    var showDialog by remember { mutableStateOf(false) }
    
    Column {
        Button(onClick = { showDialog = true }) {
            Text("Show Dialog")
        }
        
        // AlertDialog
        if (showDialog) {
            AlertDialog(
                onDismissRequest = { showDialog = false },
                title = { Text("Dialog Title") },
                text = { Text("Dialog content") },
                confirmButton = {
                    TextButton(onClick = { showDialog = false }) {
                        Text("Confirm")
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showDialog = false }) {
                        Text("Dismiss")
                    }
                }
            )
        }
    }
}
```

### 7.5 其他组件

```kotlin
@Composable
fun OtherComponents() {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        // Switch
        var checked by remember { mutableStateOf(false) }
        Switch(checked = checked, onCheckedChange = { checked = it })
        
        // Checkbox
        var checkedBox by remember { mutableStateOf(false) }
        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(checked = checkedBox, onCheckedChange = { checkedBox = it })
            Text("Checkbox")
        }
        
        // RadioButton
        var selected by remember { mutableStateOf(0) }
        Row {
            RadioButton(selected = selected == 0, onClick = { selected = 0 })
            Text("Option 1")
            RadioButton(selected = selected == 1, onClick = { selected = 1 })
            Text("Option 2")
        }
        
        // Slider
        var sliderValue by remember { mutableStateOf(0f) }
        Slider(value = sliderValue, onValueChange = { sliderValue = it })
        
        // Progress
        LinearProgressIndicator(progress = 0.7f)
        CircularProgressIndicator(progress = 0.7f)
        
        // Badge
        BadgedBox(badge = { Badge { Text("99+") } }) {
            Icon(Icons.Default.Mail, "Mail")
        }
    }
}
```

---

## 第 8 章 列表

### 8.1 LazyColumn

```kotlin
/**
 * LazyColumn：高性能垂直列表
 */

@Composable
fun LazyColumnExample() {
    val items = (1..100).toList()
    
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // 基础用法
        items(items) { item ->
            Card { Text("Item $item", Modifier.padding(16.dp)) }
        }
        
        // 带 key（提高性能）
        items(items, key = { it }) { item ->
            Card { Text("Item $item") }
        }
        
        // 带 contentType（优化回收）
        items(items, contentType = { if (it % 2 == 0) "even" else "odd" }) {
            // ...
        }
    }
}
```

### 8.2 LazyRow

```kotlin
@Composable
fun LazyRowExample() {
    val items = (1..20).toList()
    
    LazyRow(
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(items) { item ->
            Card(Modifier.size(100.dp)) {
                Box(contentAlignment = Alignment.Center) {
                    Text("Item $item")
                }
            }
        }
    }
}
```

### 8.3 LazyVerticalGrid

```kotlin
@Composable
fun LazyGridExample() {
    val items = (1..50).toList()
    
    LazyVerticalGrid(
        columns = GridCells.Fixed(3),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(items) { item ->
            Card(Modifier.aspectRatio(1f)) {
                Box(contentAlignment = Alignment.Center) {
                    Text("Item $item")
                }
            }
        }
    }
}
```

### 8.4 性能优化

```kotlin
@Composable
fun OptimizedList() {
    // 1. 使用 key 提高重组效率
    LazyColumn {
        items(items, key = { it.id }) { item ->
            ItemView(item)
        }
    }
    
    // 2. 使用 contentType 优化回收
    LazyColumn {
        items(mixedItems, contentType = { it.type }) { item ->
            when (item) {
                is Header -> HeaderView(item)
                is Content -> ContentView(item)
            }
        }
    }
    
    // 3. 使用 derivedStateOf 减少重组
    val filteredItems by remember {
        derivedStateOf { items.filter { it.isVisible } }
    }
    
    LazyColumn {
        items(filteredItems) { ItemView(it) }
    }
}
```

---

## 第 9 章 动画

### 9.1 AnimatedVisibility

```kotlin
@Composable
fun AnimatedVisibilityExample() {
    var visible by remember { mutableStateOf(true) }
    
    Column {
        Button(onClick = { visible = !visible }) {
            Text("Toggle")
        }
        
        AnimatedVisibility(
            visible = visible,
            enter = fadeIn() + slideInVertically(),
            exit = fadeOut() + slideOutVertically()
        ) {
            Text("Hello, Animation!")
        }
    }
}
```

### 9.2 animate*AsState

```kotlin
@Composable
fun AnimateAsStateExample() {
    var enabled by remember { mutableStateOf(false) }
    
    val color by animateColorAsState(
        targetValue = if (enabled) Color.Green else Color.Red,
        animationSpec = tween(500)
    )
    
    val size by animateDpAsState(
        targetValue = if (enabled) 100.dp else 50.dp
    )
    
    Box(
        Modifier
            .size(size)
            .background(color)
            .clickable { enabled = !enabled }
    )
}
```

### 9.3 Crossfade

```kotlin
@Composable
fun CrossfadeExample() {
    var currentState by remember { mutableStateOf("A") }
    
    Crossfade(targetState = currentState) { state ->
        Text("State: $state")
    }
    
    Button(onClick = { currentState = if (currentState == "A") "B" else "A" }) {
        Text("Switch")
    }
}
```

### 9.4 infiniteTransition

```kotlin
@Composable
fun InfiniteAnimationExample() {
    val transition = rememberInfiniteTransition()
    
    val color by transition.animateColor(
        initialValue = Color.Red,
        targetValue = Color.Blue,
        animationSpec = infiniteRepeatable(tween(1000), RepeatMode.Reverse)
    )
    
    val scale by transition.animateFloat(
        initialValue = 1f,
        targetValue = 1.5f,
        animationSpec = infiniteRepeatable(tween(1000), RepeatMode.Reverse)
    )
    
    Box(Modifier.size(100.dp).scale(scale).background(color))
}
```

### 9.5 AnimationSpec

```kotlin
@Composable
fun AnimationSpecExample() {
    // tween：时长动画
    animateColorAsState(
        targetValue = Color.Green,
        animationSpec = tween(1000, easing = FastOutSlowInEasing)
    )
    
    // spring：弹簧动画
    animateDpAsState(
        targetValue = 100.dp,
        animationSpec = spring(dampingRatio = Spring.DampingRatioHighBouncy)
    )
    
    // keyframes：关键帧
    animateFloatAsState(
        targetValue = 1f,
        animationSpec = keyframes {
            durationMillis = 1000
            0f at 0
            0.5f at 500 with FastOutSlowInEasing
            1f at 1000
        }
    )
}
```

---

## 第 10 章 主题与样式

### 10.1 Material Theme

```kotlin
// 定义颜色
private val DarkColorScheme = darkColorScheme(
    primary = Purple80,
    secondary = PurpleGrey80,
    tertiary = Pink80
)

private val LightColorScheme = lightColorScheme(
    primary = Purple40,
    secondary = PurpleGrey40,
    tertiary = Pink40
)

// 应用主题
@Composable
fun MyAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    
    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        shapes = Shapes,
        content = content
    )
}
```

### 10.2 ColorScheme

```kotlin
@Composable
fun ColorSchemeExample() {
    val colors = MaterialTheme.colorScheme
    
    Column {
        Box(Modifier.background(colors.primary))
        Box(Modifier.background(colors.secondary))
        Box(Modifier.background(colors.surface))
        Text("Primary", color = colors.onPrimary)
    }
}
```

### 10.3 Typography

```kotlin
val Typography = Typography(
    bodyLarge = TextStyle(
        fontSize = 16.sp,
        fontWeight = FontWeight.Normal
    ),
    titleLarge = TextStyle(
        fontSize = 22.sp,
        fontWeight = FontWeight.Bold
    )
)

@Composable
fun TypographyExample() {
    Text("Title", style = MaterialTheme.typography.titleLarge)
    Text("Body", style = MaterialTheme.typography.bodyLarge)
}
```

### 10.4 Shapes

```kotlin
val Shapes = Shapes(
    small = RoundedCornerShape(4.dp),
    medium = RoundedCornerShape(8.dp),
    large = RoundedCornerShape(16.dp)
)

@Composable
fun ShapeExample() {
    Card(shape = MaterialTheme.shapes.medium) {
        Text("Card")
    }
}
```

### 10.5 暗黑模式

```kotlin
@Composable
fun DarkModeExample() {
    // 自动检测系统主题
    val darkTheme = isSystemInDarkTheme()
    
    MyAppTheme(darkTheme = darkTheme) {
        Surface(color = MaterialTheme.colorScheme.background) {
            Text("Hello")
        }
    }
}
```

---

## 第 11 章 ViewModel 集成

### 11.1 viewModel() 函数

```kotlin
class UserViewModel : ViewModel() {
    private val _name = MutableStateFlow("")
    val name: StateFlow<String> = _name.asStateFlow()
    
    fun updateName(newName: String) {
        _name.value = newName
    }
}

@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val name by viewModel.name.collectAsState()
    
    Column {
        Text("Name: $name")
        Button(onClick = { viewModel.updateName("New Name") }) {
            Text("Update")
        }
    }
}
```

### 11.2 StateFlow 收集

```kotlin
@Composable
fun StateFlowExample(viewModel: MyViewModel = viewModel()) {
    // collectAsState：收集 Flow 并转为 State
    val data by viewModel.data.collectAsState()
    
    // collectAsStateWithLifecycle：生命周期感知
    val data2 by viewModel.data.collectAsStateWithLifecycle()
    
    Text(data)
}
```

### 11.3 Hilt 集成

```kotlin
@HiltViewModel
class HiltViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    val users = repository.getUsers()
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}

@Composable
fun HiltExample(viewModel: HiltViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsState()
    
    LazyColumn {
        items(users) { user ->
            Text(user.name)
        }
    }
}
```

### 11.4 SavedStateHandle

```kotlin
class SavedStateViewModel(
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    var name by savedStateHandle.saveable { mutableStateOf("") }
}

@Composable
fun SavedStateExample(viewModel: SavedStateViewModel = viewModel()) {
    TextField(
        value = viewModel.name,
        onValueChange = { viewModel.name = it }
    )
}
```

---

## 第 12 章 协程集成

### 12.1 LaunchedEffect

```kotlin
@Composable
fun LaunchedEffectExample(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }
    
    // userId 变化时重新执行
    LaunchedEffect(userId) {
        user = fetchUser(userId)
    }
    
    user?.let { Text(it.name) }
}
```

### 12.2 rememberCoroutineScope

```kotlin
@Composable
fun CoroutineScopeExample() {
    val scope = rememberCoroutineScope()
    var data by remember { mutableStateOf("") }
    
    Button(onClick = {
        scope.launch {
            data = fetchData()
        }
    }) {
        Text("Load")
    }
}
```

### 12.3 DisposableEffect

```kotlin
@Composable
fun DisposableEffectExample() {
    DisposableEffect(Unit) {
        // 注册监听
        val listener = MyListener()
        registerListener(listener)
        
        onDispose {
            // 清理资源
            unregisterListener(listener)
        }
    }
}
```

### 12.4 SideEffect

```kotlin
@Composable
fun SideEffectExample() {
    var count by remember { mutableStateOf(0) }
    
    // 在成功重组后执行
    SideEffect {
        // 更新非 Compose 状态
        analytics.track("count_changed", count)
    }
    
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

---

## 第 13 章 Navigation 导航

### 13.1 NavHost 基础

```kotlin
@Composable
fun NavigationExample() {
    val navController = rememberNavController()
    
    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen(onNavigate = { navController.navigate("detail") })
        }
        composable("detail") {
            DetailScreen(onBack = { navController.popBackStack() })
        }
    }
}
```

### 13.2 参数传递

```kotlin
@Composable
fun NavigationWithArgs() {
    val navController = rememberNavController()
    
    NavHost(navController, "home") {
        composable("home") {
            HomeScreen { userId ->
                navController.navigate("detail/$userId")
            }
        }
        
        // 必填参数
        composable(
            "detail/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId")
            DetailScreen(userId ?: "")
        }
        
        // 可选参数
        composable(
            "profile?userId={userId}",
            arguments = listOf(navArgument("userId") { defaultValue = "" })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId")
            ProfileScreen(userId)
        }
    }
}
```

### 13.3 Bottom Navigation

```kotlin
@Composable
fun BottomNavigationExample() {
    val navController = rememberNavController()
    
    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentRoute = navBackStackEntry?.destination?.route
                
                items.forEach { item ->
                    NavigationBarItem(
                        icon = { Icon(item.icon, null) },
                        label = { Text(item.label) },
                        selected = currentRoute == item.route,
                        onClick = {
                            navController.navigate(item.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { padding ->
        NavHost(navController, "home", Modifier.padding(padding)) {
            composable("home") { HomeScreen() }
            composable("search") { SearchScreen() }
            composable("profile") { ProfileScreen() }
        }
    }
}
```

### 13.4 深层链接

```kotlin
@Composable
fun DeepLinkExample() {
    val navController = rememberNavController()
    
    NavHost(navController, "home") {
        composable(
            "detail/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType }),
            deepLinks = listOf(
                navDeepLink {
                    uriPattern = "https://example.com/user/{userId}"
                    action = Intent.ACTION_VIEW
                }
            )
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId")
            DetailScreen(userId)
        }
    }
}
```

---

## 第 14 章 与传统 View 互操作

### 14.1 AndroidView

```kotlin
@Composable
fun AndroidViewExample() {
    // 嵌入 WebView
    AndroidView(
        factory = { context ->
            WebView(context).apply {
                webViewClient = WebViewClient()
                loadUrl("https://example.com")
            }
        },
        update = { webView ->
            webView.loadUrl("https://example.com/new")
        }
    )
}
```

### 14.2 ComposeView

```xml
<!-- XML 布局 -->
<androidx.compose.ui.platform.ComposeView
    android:id="@+id/composeView"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

```kotlin
// Activity/Fragment
val composeView = findViewById<ComposeView>(R.id.composeView)
composeView.setContent {
    MaterialTheme {
        Text("Hello from Compose!")
    }
}
```

### 14.3 渐进式迁移

```kotlin
class MixedActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_mixed)
        
        // 部分 View 使用 Compose
        val composeView = findViewById<ComposeView>(R.id.composeView)
        composeView.setContent {
            MyComposableContent()
        }
    }
}
```

### 14.4 最佳实践

```
互操作最佳实践：

1. 优先使用 Compose
   - 新代码使用 Compose
   - 旧代码逐步迁移

2. 共享 ViewModel
   - View 和 Compose 共享 ViewModel
   - 使用 StateFlow/LiveData

3. 避免过度混合
   - 一个屏幕尽量统一
   - 减少边界转换

4. 性能考虑
   - AndroidView 有额外开销
   - 频繁更新考虑纯 Compose
```

---

## 第 15 章 手势处理

### 15.1 点击手势

```kotlin
@Composable
fun ClickGestures() {
    // clickable
    Box(
        Modifier
            .size(100.dp)
            .clickable { }
            .background(Color.Blue)
    )
    
    // combinedClickable
    Box(
        Modifier
            .combinedClickable(
                onClick = { },
                onDoubleClick = { },
                onLongClick = { }
            )
            .background(Color.Green)
    )
}
```

### 15.2 拖动手势

```kotlin
@Composable
fun DragGesture() {
    var offsetX by remember { mutableStateOf(0f) }
    var offsetY by remember { mutableStateOf(0f) }
    
    Box(
        Modifier
            .offset { IntOffset(offsetX.roundToInt(), offsetY.roundToInt()) }
            .size(100.dp)
            .background(Color.Blue)
            .pointerInput(Unit) {
                detectDragGestures { change, dragAmount ->
                    change.consume()
                    offsetX += dragAmount.x
                    offsetY += dragAmount.y
                }
            }
    )
}
```

### 15.3 缩放与旋转

```kotlin
@Composable
fun TransformGesture() {
    var scale by remember { mutableStateOf(1f) }
    var rotation by remember { mutableStateOf(0f) }
    var offset by remember { mutableStateOf(Offset.Zero) }
    
    Box(
        Modifier
            .size(200.dp)
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
                rotationZ = rotation
                translationX = offset.x
                translationY = offset.y
            }
            .pointerInput(Unit) {
                detectTransformGestures { _, pan, zoom, rotationChange ->
                    scale *= zoom
                    rotation += rotationChange
                    offset += pan
                }
            }
            .background(Color.Cyan)
    )
}
```

### 15.4 多点触控

```kotlin
@Composable
fun MultiTouchExample() {
    var touchCount by remember { mutableStateOf(0) }
    
    Box(
        Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                awaitEachGesture {
                    awaitFirstDown()
                    touchCount = 1
                    
                    do {
                        val event = awaitPointerEvent()
                        touchCount = event.changes.size
                    } while (event.changes.any { it.pressed })
                    
                    touchCount = 0
                }
            }
    ) {
        Text("Touches: $touchCount")
    }
}
```

---

## 第 16 章 Canvas 自定义绘制

### 16.1 DrawScope

```kotlin
@Composable
fun CanvasExample() {
    Canvas(Modifier.size(200.dp)) {
        // drawCircle, drawRect, drawLine, drawPath...
        drawCircle(Color.Red, radius = 100f, center = center)
    }
}
```

### 16.2 基本图形

```kotlin
@Composable
fun BasicShapes() {
    Canvas(Modifier.fillMaxSize()) {
        // 圆
        drawCircle(Color.Red, radius = 50f)
        
        // 矩形
        drawRect(Color.Blue, topLeft = Offset(100f, 100f), size = Size(100f, 100f))
        
        // 线
        drawLine(Color.Green, Offset(0f, 0f), Offset(200f, 200f), strokeWidth = 4f)
        
        // 圆角矩形
        drawRoundRect(Color.Yellow, cornerRadius = CornerRadius(10f))
        
        // 椭圆
        drawOval(Color.Cyan, size = Size(100f, 50f))
        
        // 弧
        drawArc(Color.Magenta, 0f, 270f, useCenter = true)
    }
}
```

### 16.3 Path 路径

```kotlin
@Composable
fun PathExample() {
    Canvas(Modifier.size(200.dp)) {
        val path = Path().apply {
            moveTo(0f, 0f)
            lineTo(100f, 100f)
            quadraticTo(150f, 50f, 200f, 100f)
            cubicTo(250f, 50f, 300f, 150f, 350f, 100f)
            close()
        }
        
        drawPath(path, Color.Blue, style = Stroke(4f))
    }
}
```

### 16.4 渐变与阴影

```kotlin
@Composable
fun GradientAndShadow() {
    Canvas(Modifier.size(200.dp)) {
        // 线性渐变
        drawRect(
            Brush.linearGradient(
                colors = listOf(Color.Cyan, Color.Blue),
                start = Offset.Zero,
                end = Offset(size.width, size.height)
            )
        )
        
        // 径向渐变
        drawCircle(
            Brush.radialGradient(
                colors = listOf(Color.Yellow, Color.Red),
                center = center,
                radius = 100f
            )
        )
        
        // 阴影
        drawIntoCanvas { canvas ->
            val paint = Paint().apply {
                color = Color.Blue
                asFrameworkPaint().setShadowLayer(10f, 5f, 5f, Color.Black.toArgb())
            }
            canvas.drawCircle(center, 50f, paint)
        }
    }
}
```

---

## 第 17 章 性能优化

### 17.1 稳定性与跳过

```kotlin
// ❌ 不稳定：可变属性
data class MutableUser(var name: String)

// ✅ 稳定：不可变
@Immutable
data class ImmutableUser(val name: String)

// ✅ 使用 @Stable
@Stable
class StableUser {
    var name by mutableStateOf("")
}

@Composable
fun UserCard(user: ImmutableUser) {
    // user 未变化时跳过重组
    Text(user.name)
}
```

### 17.2 重组优化

```kotlin
@Composable
fun RecompositionOptimization() {
    // 1. 使用 remember 缓存
    val formattedDate = remember(timestamp) {
        SimpleDateFormat().format(timestamp)
    }
    
    // 2. 使用 derivedStateOf
    val filteredItems by remember {
        derivedStateOf { items.filter { it.isVisible } }
    }
    
    // 3. 使用 key 优化 LazyColumn
    LazyColumn {
        items(items, key = { it.id }) { item ->
            ItemView(item)
        }
    }
}
```

### 17.3 布局优化

```kotlin
// 1. 使用 graphicsLayer 进行变换
Box(Modifier.graphicsLayer {
    rotationZ = rotation
    scaleX = scale
})

// 2. 避免过度嵌套
// ❌ 错误
Column { Column { Column { Text("") } } }

// ✅ 正确
Column { Text("") }

// 3. 使用 BaselineSkip
Column {
    Text("Title")
    Spacer(Modifier.height(8.dp))
    Text("Content")
}
```

### 17.4 性能分析工具

```
性能分析工具：

1. Layout Inspector
   - Android Studio -> View -> Tool Windows -> Layout Inspector
   - 查看 Compose 树结构

2. Composition Tracing
   - 启用 composition tracing
   - 分析重组次数

3. Profiler
   - CPU Profiler
   - Memory Profiler

4. Recomposition Count
   @Composable
   fun RecompositionCounter() {
       var count by remember { mutableStateOf(0) }
       SideEffect { count++ }
       Log.d("Recomposition", "Count: $count")
   }
```

---

## 第 18 章 面试常见问题

### 18.1 Compose 原理

**Q: Jetpack Compose 的工作原理？**

**A:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Compose 执行阶段                                      │
└─────────────────────────────────────────────────────────────────────────────┘

1. Composition（组合）
   - 执行 Composable 函数
   - 创建 UI 树（Slot Tree）
   - 首次组合：Initial Composition
   - 重新组合：Recomposition

2. Layout（布局）
   - 测量子元素
   - 确定位置和大小

3. Drawing（绘制）
   - 将 UI 绘制到屏幕
```

### 18.2 重组机制

**Q: 什么是重组（Recomposition）？如何优化？**

**A:**

```
重组特点：
1. 智能跳过：输入未变化时跳过
2. 可能频繁执行：避免副作用
3. 可并行执行：不要依赖外部状态
4. 乐观执行：可能被放弃

优化方法：
1. 使用 remember 缓存计算
2. 使用 derivedStateOf 减少重组
3. 使用 @Immutable/@Stable 注解
4. 状态提升减少重组范围
5. 使用 key 优化 LazyColumn
```

### 18.3 与传统 View 对比

**Q: Compose vs 传统 View？**

**A:**

| 对比项 | Compose | 传统 View |
|-------|---------|-----------|
| 范式 | 声明式 | 命令式 |
| UI 定义 | Kotlin | XML |
| 状态管理 | 自动响应 | 手动更新 |
| 代码量 | 少 | 多 |
| 学习曲线 | 需要学习 | 成熟稳定 |
| 预览 | 实时预览 | 需要运行 |
| 性能 | 智能重组 | View 开销 |

### 18.4 性能优化

**Q: Compose 性能优化技巧？**

**A:**

1. **稳定性优化**：使用 @Immutable/@Stable
2. **重组优化**：remember、derivedStateOf
3. **列表优化**：key、contentType
4. **布局优化**：减少嵌套、graphicsLayer
5. **避免副作用**：使用正确的 Effect API

### 18.5 最佳实践

**Q: Compose 开发最佳实践？**

**A:**

1. **状态管理**：
   - 状态提升
   - 单一数据源
   - 使用 ViewModel

2. **代码组织**：
   - 小型 Composable 函数
   - 功能模块化
   - 复用组件

3. **性能优化**：
   - 使用 remember
   - 避免不必要的重组
   - 使用 key

4. **测试**：
   - 组件测试
   - 状态测试
   - UI 测试

---

## 总结

### Compose 核心要点

1. **声明式 UI**：描述 UI 是什么
2. **Kotlin 优先**：完全使用 Kotlin
3. **状态驱动**：UI 自动响应状态
4. **智能重组**：只更新变化部分
5. **互操作**：与传统 View 协作

### 适用场景

- ✅ 新项目首选
- ✅ 追求开发效率
- ✅ 需要实时预览
- ✅ 复杂 UI 动画

### 学习建议

1. **基础阶段**：Composable、State、Modifier、Layout
2. **进阶阶段**：动画、主题、ViewModel、Navigation
3. **高级阶段**：自定义 Layout、Canvas、性能优化
4. **实战阶段**：完整项目开发

---

**文档版本**：v2.0  
**更新时间**：2026-03-11  
**适用版本**：Compose BOM 2024.02.00+