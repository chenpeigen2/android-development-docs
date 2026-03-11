# Android Jetpack Compose 详解

> **Jetpack Compose** 是 Android 的现代声明式 UI 工具包，使用 Kotlin 构建 UI

---

## 目录

1. [Compose 概述](#1-compose-概述)
2. [基础概念](#2-基础概念)
3. [Composable 函数](#3-composable-函数)
4. [State 状态管理](#4-state-状态管理)
5. [Modifier 修饰符](#5-modifier-修饰符)
6. [Layout 布局](#6-layout-布局)
7. [Material Design 组件](#7-material-design-组件)
8. [列表（LazyColumn/LazyRow）](#8-列表lazycolumnlazyrow)
9. [动画](#9-动画)
10. [主题与样式](#10-主题与样式)
11. [ViewModel 集成](#11-viewmodel-集成)
12. [协程集成](#12-协程集成)
13. [Navigation 导航](#13-navigation-导航)
14. [与传统 View 互操作](#14-与传统-view-互操作)
15. [手势处理](#15-手势处理)
16. [Canvas 自定义绘制](#16-canvas-自定义绘制)
17. [性能优化](#17-性能优化)
18. [面试常见问题](#18-面试常见问题)

---

## 1. Compose 概述

### 1.1 什么是 Jetpack Compose

Jetpack Compose 是 Android 的现代声明式 UI 工具包：

- **声明式 UI**：描述 UI 应该是什么样子，而不是如何构建
- **Kotlin 优先**：完全使用 Kotlin 编写
- **无需 XML**：UI 完全用代码描述
- **状态驱动**：UI 自动响应状态变化
- **预览支持**：实时预览 UI 组件

### 1.2 Compose vs 传统 View

| 对比项 | 传统 View | Jetpack Compose |
|--------|-----------|-----------------|
| **UI 定义** | XML 布局 | Kotlin 代码 |
| **范式** | 命令式 | 声明式 |
| **状态管理** | 手动更新 | 自动响应 |
| **复用** | 自定义 View | Composable 函数 |
| **性能** | View 层级开销 | 轻量级组合 |
| **预览** | 需要运行 | 实时预览 |

### 1.3 项目配置

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
}

dependencies {
    // Compose BOM
    implementation(platform("androidx.compose:compose-bom:2024.02.00"))
    
    // 核心组件
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    
    // Activity 集成
    implementation("androidx.activity:activity-compose:1.8.2")
    
    // ViewModel 集成
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    
    // 调试工具
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}
```

### 1.4 Hello Compose

```kotlin
// MainActivity.kt
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            // 设置主题
            MaterialTheme {
                // 使用 Surface 作为容器
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    // 调用自定义 Composable
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
    MaterialTheme {
        Greeting("Android")
    }
}
```

---

## 2. 基础概念

### 2.1 声明式 UI

**命令式（传统 View）**：
```kotlin
// 命令式：告诉系统如何做
val textView = findViewById<TextView>(R.id.textView)
textView.text = "Hello"
textView.setTextColor(Color.RED)
textView.visibility = View.VISIBLE
```

**声明式（Compose）**：
```kotlin
// 声明式：描述 UI 是什么
Text(
    text = "Hello",
    color = Color.Red,
    modifier = Modifier.visible(isVisible)
)
```

### 2.2 组合（Composition）

- **Composition**：Composable 函数执行后生成的 UI 树
- **Initial Composition**：首次执行创建 Composition
- **Recomposition**：状态变化后重新执行更新 UI

```kotlin
@Composable
fun Counter() {
    // state 会触发 Recomposition
    var count by remember { mutableStateOf(0) }
    
    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

### 2.3 重组（Recomposition）特点

1. **智能重组**：只重组受影响的部分
2. **可跳过**：如果输入未变化，可跳过重组
3. **可重启**：Composable 可以重新启动
4. **乐观执行**：假设重组会成功，失败时回滚

### 2.4 Composable 函数规则

```kotlin
// ✅ 正确：Composable 可以调用其他 Composable
@Composable
fun ValidComposable() {
    Text("Hello")
    AnotherComposable()
}

// ✅ 正确：Composable 可以读取状态
@Composable
fun ReadState(name: String) {
    Text("Hello $name")
}

// ❌ 错误：Composable 不应有返回值（除了 Unit）
@Composable
fun WrongReturn(): String {  // 错误！
    return "Hello"
}

// ❌ 错误：Composable 不应有副作用
@Composable
fun WrongSideEffect() {
    // 错误！不应直接修改外部状态
    externalVar = 123
}

// ✅ 正确：使用副作用 API
@Composable
fun CorrectSideEffect() {
    LaunchedEffect(Unit) {
        // 在这里执行副作用
        saveToDatabase()
    }
}
```

---

## 3. Composable 函数

### 3.1 基本结构

```kotlin
// @Composable 注解
@Composable
fun MyComposable(
    // 参数（不可变）
    title: String,
    // 可选参数
    modifier: Modifier = Modifier,
    // 函数类型参数
    onClick: () -> Unit = {}
) {
    // 函数体
    Text(
        text = title,
        modifier = modifier.clickable { onClick() }
    )
}
```

### 3.2 函数命名约定

```kotlin
// ✅ 正确：名词，表示 UI 组件
@Composable
fun UserProfileCard() { }

// ✅ 正确：动词 + 名词，表示动作
@Composable
fun DrawDivider() { }

// ❌ 错误：动词，不表示 UI
@Composable
fun LoadData() { }  // 应该用普通函数

// ✅ 正确：小写字母开头表示返回 Modifier
fun Modifier.roundedCorner() = this.then(
    Modifier.clip(RoundedCornerShape(8.dp))
)
```

### 3.3 remember 和 rememberSaveable

```kotlin
@Composable
fun RememberExample() {
    // remember：在重组中保持状态
    var count by remember { mutableStateOf(0) }
    
    // rememberSaveable：在配置更改（如旋转）后也能保持
    var savedCount by rememberSaveable { mutableStateOf(0) }
    
    // remember 保存复杂对象
    val dataList = remember {
        mutableListOf<String>()  // 注意：这里不应该用可变列表
    }
    
    // 正确方式：使用不可变列表 + 重新赋值
    var items by remember { mutableStateOf(listOf<String>()) }
    
    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

### 3.4 稳定性（Stability）

```kotlin
// 稳定类型：不可变且可预测
data class User(
    val id: Int,
    val name: String  // String 是稳定的
)

// 不稳定类型：可变或有不可预测的变化
data class MutableUser(
    val id: Int,
    var name: String  // var 使其不稳定
)

// 使用 @Immutable 注解标记稳定类型
@Immutable
data class ImmutableUser(
    val id: Int,
    val name: String
)

// 使用 @Stable 注解标记有条件稳定的类型
@Stable
data class StableUser(
    val id: Int,
    private var _name: String
) {
    val name: String get() = _name
    
    fun updateName(newName: String) {
        _name = newName
    }
}
```

---

## 4. State 状态管理

### 4.1 State 基础

```kotlin
@Composable
fun StateBasics() {
    // mutableStateOf 创建可观察的状态
    var text by remember { mutableStateOf("") }
    
    // 也可以使用 delegate 语法
    val textState = remember { mutableStateOf("") }
    
    Column {
        // TextField 会自动更新状态
        TextField(
            value = text,
            onValueChange = { text = it },
            label = { Text("Enter text") }
        )
        
        // Text 会自动响应状态变化
        Text("You typed: $text")
    }
}
```

### 4.2 State 类型

```kotlin
@Composable
fun StateTypes() {
    // 基本类型
    var intValue by remember { mutableStateOf(0) }
    var stringValue by remember { mutableStateOf("") }
    var booleanValue by remember { mutableStateOf(false) }
    
    // 集合类型
    var listValue by remember { mutableStateOf(listOf<String>()) }
    var mapValue by remember { mutableStateOf(mapOf<String, Int>()) }
    
    // 自定义对象
    data class User(val name: String, val age: Int)
    var userValue by remember { mutableStateOf(User("", 0)) }
    
    // 使用 mutableStateListOf
    val items = remember { mutableStateListOf<String>() }
    items.add("New Item")  // 直接修改
    
    // 使用 mutableStateMapOf
    val map = remember { mutableStateMapOf<String, Int>() }
    map["key"] = 123
}
```

### 4.3 State Hoisting（状态提升）

```kotlin
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
    count: Int,
    onIncrement: () -> Unit
) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}

// 使用示例
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }
    
    GoodCounter(
        count = count,
        onIncrement = { count++ }
    )
}
```

### 4.4 Stateful vs Stateless

```kotlin
// Stateful：包含内部状态
@Composable
fun StatefulCounter() {
    var count by remember { mutableStateOf(0) }
    
    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}

// Stateless：无内部状态，完全由外部控制
@Composable
fun StatelessCounter(
    count: Int,
    onIncrement: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Text("Count: $count")
        Button(onClick = onIncrement) {
            Text("Increment")
        }
    }
}
```

### 4.5 状态持久化

```kotlin
@Composable
fun PersistentState() {
    // rememberSaveable：配置更改后保持状态
    var text by rememberSaveable { mutableStateOf("") }
    
    // 自定义 Saver
    data class User(val id: Int, val name: String)
    
    val userSaver = Saver<User?, String>(
        save = { it?.let { "${it.id},${it.name}" } },
        restore = { 
            it?.split(",")?.let { parts ->
                User(parts[0].toInt(), parts[1])
            }
        }
    )
    
    var user by rememberSaveable(stateSaver = userSaver) { 
        mutableStateOf(null) 
    }
    
    // ListSaver
    val listSaver = listSaver<User?, Any>(
        save = { listOf(it?.id, it?.name) },
        restore = { User(it[0] as Int, it[1] as String) }
    )
}
```

---

## 5. Modifier 修饰符

### 5.1 Modifier 基础

```kotlin
@Composable
fun ModifierBasics() {
    Box(
        modifier = Modifier
            .size(100.dp)           // 设置大小
            .background(Color.Blue) // 设置背景
            .padding(16.dp)         // 设置内边距
            .border(2.dp, Color.Red) // 设置边框
    )
}
```

### 5.2 顺序很重要

```kotlin
@Composable
fun ModifierOrder() {
    // ❌ 错误：padding 在 background 后，背景不会包含 padding 区域
    Box(
        modifier = Modifier
            .background(Color.Blue)
            .padding(16.dp)
    )
    
    // ✅ 正确：padding 在 background 前，背景包含 padding 区域
    Box(
        modifier = Modifier
            .padding(16.dp)
            .background(Color.Blue)
    )
    
    // 点击区域也受顺序影响
    Box(
        modifier = Modifier
            .clickable { }      // 整个 Box 可点击
            .size(100.dp)
    )
    
    Box(
        modifier = Modifier
            .size(100.dp)
            .clickable { }      // 只有 100.dp 区域可点击
    )
}
```

### 5.3 常用 Modifier

```kotlin
@Composable
fun CommonModifiers() {
    Column {
        // 尺寸
        Box(modifier = Modifier.size(100.dp))
        Box(modifier = Modifier.width(100.dp).height(50.dp))
        Box(modifier = Modifier.fillMaxSize())
        Box(modifier = Modifier.fillMaxWidth())
        Box(modifier = Modifier.wrapContentSize())
        
        // 内边距
        Box(modifier = Modifier.padding(16.dp))
        Box(modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp))
        Box(modifier = Modifier.padding(start = 8.dp, top = 4.dp, end = 8.dp, bottom = 4.dp))
        
        // 外边距（offset 不影响布局）
        Box(modifier = Modifier.offset(10.dp, 20.dp))
        
        // 背景
        Box(modifier = Modifier.background(Color.Blue))
        Box(modifier = Modifier.background(Color.Blue, RoundedCornerShape(8.dp)))
        
        // 边框
        Box(modifier = Modifier.border(2.dp, Color.Red))
        Box(modifier = Modifier.border(2.dp, Color.Red, RoundedCornerShape(8.dp)))
        
        // 裁剪
        Box(modifier = Modifier.clip(RoundedCornerShape(8.dp)))
        Box(modifier = Modifier.clip(CircleShape))
        
        // 透明度
        Box(modifier = Modifier.alpha(0.5f))
        
        // 旋转、缩放
        Box(modifier = Modifier.rotate(45f))
        Box(modifier = Modifier.scale(1.5f))
        
        // 权重（在 Row/Column 中）
        Row {
            Box(modifier = Modifier.weight(1f).height(50.dp).background(Color.Red))
            Box(modifier = Modifier.weight(2f).height(50.dp).background(Color.Blue))
        }
    }
}
```

### 5.4 自定义 Modifier

```kotlin
// 扩展函数创建自定义 Modifier
fun Modifier.shimmer(): Modifier = composed {
    var size by remember { mutableStateOf(IntSize.Zero) }
    val transition = rememberInfiniteTransition(label = "shimmer")
    
    val startOffsetX by transition.animateFloat(
        initialValue = -2 * size.width.toFloat(),
        targetValue = 2 * size.width.toFloat(),
        animationSpec = infiniteRepeatable(animation = tween(1000)),
        label = "shimmerOffset"
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
    Box(
        modifier = Modifier
            .size(200.dp)
            .shimmer()
    )
}
```

### 5.5 Modifier 链式调用原理

```kotlin
// Modifier 是一个接口
interface Modifier {
    // 组合多个 Modifier
    infix fun then(other: Modifier): Modifier
    
    companion object : Modifier {
        override fun then(other: Modifier): Modifier = other
    }
}

// 链式调用实际上是在组合
Modifier
    .size(100.dp)
    .padding(16.dp)
    .background(Color.Blue)

// 等价于
Modifier.size(100.dp) then Modifier.padding(16.dp) then Modifier.background(Color.Blue)
```

---

## 6. Layout 布局

### 6.1 Column（垂直布局）

```kotlin
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

// Arrangement 选项
// - SpaceBetween：两端对齐，中间平分
// - SpaceEvenly：均匀分布
// - SpaceAround：每个元素两侧相等间距
// - Center：居中
// - Top/Bottom：顶部/底部对齐

// Alignment 选项
// - Start/CenterHorizontally/End
```

### 6.2 Row（水平布局）

```kotlin
@Comotlin
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

### 6.3 Box（层叠布局）

```kotlin
@Composable
fun BoxExample() {
    Box(
        modifier = Modifier.size(200.dp)
    ) {
        // 底层
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Blue)
        )
        
        // 顶层，居中
        Text(
            text = "Overlay",
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

### 6.4 ConstraintLayout（约束布局）

```kotlin
// 添加依赖：implementation("androidx.constraintlayout:constraintlayout-compose:1.0.1")

@Composable
fun ConstraintLayoutExample() {
    ConstraintLayout(modifier = Modifier.fillMaxSize()) {
        // 创建引用
        val (text1, text2, button) = createRefs()
        
        Text(
            text = "Text 1",
            modifier = Modifier.constrainAs(text1) {
                top.linkTo(parent.top, margin = 16.dp)
                start.linkTo(parent.start, margin = 16.dp)
            }
        )
        
        Text(
            text = "Text 2",
            modifier = Modifier.constrainAs(text2) {
                top.linkTo(text1.bottom, margin = 8.dp)
                start.linkTo(text1.start)
            }
        )
        
        Button(
            onClick = { },
            modifier = Modifier.constrainAs(button) {
                top.linkTo(text2.bottom, margin = 16.dp)
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
@Composable
fun CustomLayoutExample() {
    // 自定义瀑布流布局
    StaggeredGrid(
        rows = 3,
        modifier = Modifier.fillMaxWidth()
    ) {
        for (i in 0..10) {
            Text(
                text = "Item $i",
                modifier = Modifier
                    .background(Color.LightGray)
                    .padding(8.dp)
            )
        }
    }
}

@Composable
fun StaggeredGrid(
    rows: Int,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(
        content = content,
        modifier = modifier
    ) { measurables, constraints ->
        // 测量所有子元素
        val placeables = measurables.map { measurable ->
            measurable.measure(constraints)
        }
        
        // 计算每行的宽度
        val rowWidths = IntArray(rows) { 0 }
        placeables.forEachIndexed { index, placeable ->
            val row = index % rows
            rowWidths[row] += placeable.width
        }
        
        // 计算最大宽度
        val maxWidth = rowWidths.maxOrNull() ?: constraints.minWidth
        
        // 计算高度
        val rowHeights = IntArray(rows) { 0 }
        placeables.forEachIndexed { index, placeable ->
            val row = index % rows
            rowHeights[row] = maxOf(rowHeights[row], placeable.height)
        }
        val totalHeight = rowHeights.sumOf { it }
        
        // 设置布局大小
        layout(maxWidth, totalHeight) {
            // 放置子元素
            val rowX = IntArray(rows) { 0 }
            placeables.forEachIndexed { index, placeable ->
                val row = index % rows
                placeable.place(
                    x = rowX[row],
                    y = rowHeights.take(row).sum()
                )
                rowX[row] += placeable.width
            }
        }
    }
}
```

---

## 7. Material Design 组件

### 7.1 Button 系列

```kotlin
@Composable
fun ButtonExamples() {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        // 普通按钮
        Button(onClick = { }) {
            Text("Button")
        }
        
        // 填充按钮（默认）
        FilledButton(onClick = { }) {
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
        
        // tonal 按钮
        FilledTonalButton(onClick = { }) {
            Text("Tonal Button")
        }
        
        // 图标按钮
        IconButton(onClick = { }) {
            Icon(Icons.Default.Favorite, contentDescription = "Favorite")
        }
        
        // 带图标的按钮
        Button(onClick = { }) {
            Icon(
                imageVector = Icons.Default.Add,
                contentDescription = null,
                modifier = Modifier.size(ButtonDefaults.IconSize)
            )
            Spacer(Modifier.size(ButtonDefaults.IconSpacing))
            Text("Add")
        }
        
        // 悬浮按钮
        FloatingActionButton(onClick = { }) {
            Icon(Icons.Default.Add, contentDescription = "Add")
        }
        
        // 扩展悬浮按钮
        ExtendedFloatingActionButton(
            onClick = { },
            icon = { Icon(Icons.Default.Add, contentDescription = null) },
            text = { Text("Add") }
        )
    }
}
```

### 7.2 TextField 系列

```kotlin
@Composable
fun TextFieldExamples() {
    var text by remember { mutableStateOf("") }
    
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        // 基础输入框
        TextField(
            value = text,
            onValueChange = { text = it },
            label = { Text("Label") }
        )
        
        // 填充输入框
        OutlinedTextField(
            value = text,
            onValueChange = { text = it },
            label = { Text("Label") },
            placeholder = { Text("Placeholder") },
            leadingIcon = { Icon(Icons.Default.Person, null) },
            trailingIcon = { Icon(Icons.Default.Visibility, null) },
            isError = false,
            singleLine = true
        )
        
        // 密码输入框
        var password by remember { mutableStateOf("") }
        var passwordVisible by remember { mutableStateOf(false) }
        
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
                        imageVector = if (passwordVisible) 
                            Icons.Default.Visibility 
                        else 
                            Icons.Default.VisibilityOff,
                        contentDescription = "Toggle password visibility"
                    )
                }
            }
        )
    }
}
```

### 7.3 Card

```kotlin
@Composable
fun CardExamples() {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        // 基础卡片
        Card {
            Text("Card content", modifier = Modifier.padding(16.dp))
        }
        
        // Elevated 卡片
        ElevatedCard {
            Text("Elevated card", modifier = Modifier.padding(16.dp))
        }
        
        // Outlined 卡片
        OutlinedCard {
            Text("Outlined card", modifier = Modifier.padding(16.dp))
        }
        
        // 自定义卡片
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            shape = RoundedCornerShape(8.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            ),
            elevation = CardDefaults.cardElevation(
                defaultElevation = 8.dp
            )
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Card Title",
                    style = MaterialTheme.typography.titleLarge
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Card description goes here",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}
```

### 7.4 Dialog

```kotlin
@Composable
fun DialogExamples() {
    var showDialog by remember { mutableStateOf(false) }
    
    Column {
        Button(onClick = { showDialog = true }) {
            Text("Show Dialog")
        }
        
        // 基础对话框
        if (showDialog) {
            AlertDialog(
                onDismissRequest = { showDialog = false },
                title = { Text("Dialog Title") },
                text = { Text("Dialog content goes here") },
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

// 自定义 Dialog
@Composable
fun CustomDialogExample() {
    var showCustomDialog by remember { mutableStateOf(false) }
    
    if (showCustomDialog) {
        Dialog(onDismissRequest = { showCustomDialog = false }) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text("Custom Dialog")
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("This is a custom dialog content")
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(onClick = { showCustomDialog = false }) {
                        Text("Close")
                    }
                }
            }
        }
    }
}
```

### 7.5 其他常用组件

```kotlin
@Composable
fun OtherComponents() {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        // Chip
        AssistChip(
            onClick = { },
            label = { Text("Chip") },
            leadingIcon = {
                Icon(Icons.Default.Star, null, Modifier.size(16.dp))
            }
        )
        
        // Switch
        var checked by remember { mutableStateOf(false) }
        Switch(
            checked = checked,
            onCheckedChange = { checked = it }
        )
        
        // Checkbox
        var checkedBox by remember { mutableStateOf(false) }
        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(
                checked = checkedBox,
                onCheckedChange = { checkedBox = it }
            )
            Text("Checkbox")
        }
        
        // RadioButton
        var selectedOption by remember { mutableStateOf(0) }
        Row(verticalAlignment = Alignment.CenterVertically) {
            RadioButton(
                selected = selectedOption == 0,
                onClick = { selectedOption = 0 }
            )
            Text("Option 1")
            Spacer(modifier = Modifier.width(16.dp))
            RadioButton(
                selected = selectedOption == 1,
                onClick = { selectedOption = 1 }
            )
            Text("Option 2")
        }
        
        // Slider
        var sliderValue by remember { mutableStateOf(0f) }
        Slider(
            value = sliderValue,
            onValueChange = { sliderValue = it },
            valueRange = 0f..100f
        )
        
        // Progress
        LinearProgressIndicator(progress = 0.7f)
        CircularProgressIndicator(progress = 0.7f)
        
        // Badge
        BadgedBox(
            badge = { Badge { Text("99+") } }
        ) {
            Icon(Icons.Default.Mail, contentDescription = "Mail")
        }
        
        // Divider
        HorizontalDivider(thickness = 1.dp, color = Color.Gray)
        VerticalDivider(thickness = 1.dp, color = Color.Gray)
    }
}
```

---

## 8. 列表（LazyColumn/LazyRow）

### 8.1 LazyColumn

```kotlin
@Composable
fun LazyColumnExample() {
    val items = (1..100).toList()
    
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // 单个项
        items(items) { item ->
            Card {
                Text(
                    text = "Item $item",
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                )
            }
        }
        
        // 带键的项（提高性能）
        items(
            items = items,
            key = { item -> item }
        ) { item ->
            Card {
                Text("Item $item")
            }
        }
        
        // 带类型的项
        items(
            items = items,
            contentType = { item -> if (item % 2 == 0) "even" else "odd" }
        ) { item ->
            if (item % 2 == 0) {
                EvenItem(item)
            } else {
                OddItem(item)
            }
        }
    }
}

@Composable
fun EvenItem(item: Int) {
    Card(colors = CardDefaults.cardColors(containerColor = Color.Blue)) {
        Text("Even: $item", modifier = Modifier.padding(16.dp))
    }
}

@Composable
fun OddItem(item: Int) {
    Card(colors = CardDefaults.cardColors(containerColor = Color.Red)) {
        Text("Odd: $item", modifier = Modifier.padding(16.dp))
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
            Card(
                modifier = Modifier.size(100.dp)
            ) {
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
        columns = GridCells.Fixed(3),  // 固定 3 列
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(items) { item ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(1f)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text("Item $item")
                }
            }
        }
    }
    
    // 自适应宽度
    LazyVerticalGrid(
        columns = GridCells.Adaptive(minSize = 100.dp)
    ) {
        // ...
    }
}
```

### 8.4 Header 和 Footer

```kotlin
@Composable
fun LazyListWithHeader() {
    LazyColumn {
        // Header
        item {
            Text(
                text = "Header",
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(16.dp)
            )
        }
        
        // 列表项
        items((1..20).toList()) { item ->
            Text("Item $item", modifier = Modifier.padding(16.dp))
        }
        
        // Footer
        item {
            Text(
                text = "Footer",
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}
```

### 8.5 分组列表

```kotlin
data class Group(
    val title: String,
    val items: List<String>
)

@Composable
fun GroupedList(groups: List<Group>) {
    LazyColumn {
        groups.forEach { group ->
            // 组标题
            stickyHeader {
                Text(
                    text = group.title,
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(MaterialTheme.colorScheme.primaryContainer)
                        .padding(8.dp)
                )
            }
            
            // 组内项
            items(group.items) { item ->
                Text(
                    text = item,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                )
            }
        }
    }
}
```

### 8.6 性能优化

```kotlin
@Composable
fun OptimizedList() {
    // 1. 使用 key 提高重组效率
    LazyColumn {
        items(
            items = items,
            key = { item -> item.id }
        ) { item ->
            ItemView(item)
        }
    }
    
    // 2. 使用 contentType 优化回收
    LazyColumn {
        items(
            items = mixedItems,
            contentType = { item -> 
                when (item) {
                    is Header -> "header"
                    is Content -> "content"
                    is Footer -> "footer"
                }
            }
        ) { item ->
            when (item) {
                is Header -> HeaderView(item)
                is Content -> ContentView(item)
                is Footer -> FooterView(item)
            }
        }
    }
    
    // 3. 避免在 items 中创建对象
    // ❌ 错误
    LazyColumn {
        items(items) { item ->
            val formattedDate = SimpleDateFormat().format(item.date)  // 每次重组都创建
            Text(formattedDate)
        }
    }
    
    // ✅ 正确
    LazyColumn {
        items(items, key = { it.id }) { item ->
            ItemView(item, item.formattedDate)  // 预先格式化
        }
    }
    
    // 4. 使用 derivedStateOf 减少重组
    val filteredItems by remember {
        derivedStateOf {
            items.filter { it.isVisible }
        }
    }
    
    LazyColumn {
        items(filteredItems) { item ->
            ItemView(item)
        }
    }
}
```

---

## 9. 动画

### 9.1 简单动画

```kotlin
@Composable
fun SimpleAnimations() {
    // 1. AnimatedVisibility - 可见性动画
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
    
    // 2. animateContentSize - 内容大小变化动画
    var expanded by remember { mutableStateOf(false) }
    
    Column(
        modifier = Modifier
            .clickable { expanded = !expanded }
            .animateContentSize()
            .background(Color.LightGray)
            .padding(16.dp)
    ) {
        Text(if (expanded) "Expanded content with more text" else "Short")
    }
    
    // 3. Crossfade - 淡入淡出切换
    var currentState by remember { mutableStateOf("A") }
    
    Crossfade(targetState = currentState, label = "crossfade") { state ->
        Text("State: $state")
    }
}
```

### 9.2 状态动画

```kotlin
@Composable
fun StateAnimations() {
    // 1. animate*AsState
    var enabled by remember { mutableStateOf(false) }
    
    val color by animateColorAsState(
        targetValue = if (enabled) Color.Green else Color.Red,
        animationSpec = tween(durationMillis = 500),
        label = "color"
    )
    
    val size by animateDpAsState(
        targetValue = if (enabled) 100.dp else 50.dp,
        label = "size"
    )
    
    Box(
        modifier = Modifier
            .size(size)
            .background(color)
            .clickable { enabled = !enabled }
    )
    
    // 2. AnimatedContent
    var count by remember { mutableStateOf(0) }
    
    AnimatedContent(
        targetState = count,
        transitionSpec = {
            if (targetState > initialState) {
                slideInVertically { height -> height } + fadeIn() togetherWith
                    slideOutVertically { height -> -height } + fadeOut()
            } else {
                slideInVertically { height -> -height } + fadeIn() togetherWith
                    slideOutVertically { height -> height } + fadeOut()
            }
        },
        label = "animatedContent"
    ) { targetCount ->
        Text(text = "$targetCount", fontSize = 50.sp)
    }
}
```

### 9.3 无限动画

```kotlin
@Composable
fun InfiniteAnimations() {
    // 1. rememberInfiniteTransition
    val infiniteTransition = rememberInfiniteTransition(label = "infinite")
    
    val color by infiniteTransition.animateColor(
        initialValue = Color.Red,
        targetValue = Color.Blue,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "color"
    )
    
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.5f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )
    
    Box(
        modifier = Modifier
            .size(100.dp)
            .scale(scale)
            .background(color)
    )
}
```

### 9.4 AnimationSpec

```kotlin
@Composable
fun AnimationSpecExamples() {
    // 1. tween - 时长动画
    val colorTween by animateColorAsState(
        targetValue = Color.Green,
        animationSpec = tween(
            durationMillis = 1000,
            delayMillis = 500,
            easing = FastOutSlowInEasing
        ),
        label = "tween"
    )
    
    // 2. spring - 弹簧动画
    val sizeSpring by animateDpAsState(
        targetValue = 100.dp,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioHighBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "spring"
    )
    
    // 3. keyframes - 关键帧动画
    val value by animateFloatAsState(
        targetValue = 1f,
        animationSpec = keyframes {
            durationMillis = 1000
            0f at 0
            0.5f at 500 with FastOutSlowInEasing
            0.8f at 800
            1f at 1000
        },
        label = "keyframes"
    )
    
    // 4. repeatable - 重复动画
    val repeatValue by animateFloatAsState(
        targetValue = 1f,
        animationSpec = repeatable(
            iterations = 3,
            animation = tween(500),
            repeatMode = RepeatMode.Reverse
        ),
        label = "repeatable"
    )
}
```

---

## 10. 主题与样式

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

### 10.2 Typography

```kotlin
// 定义字体
val Typography = Typography(
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    ),
    titleLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 22.sp,
        lineHeight = 28.sp,
        letterSpacing = 0.sp
    ),
    labelSmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 11.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.5.sp
    )
)

// 使用
@Composable
fun TypographyExample() {
    Column {
        Text(
            text = "Title Large",
            style = MaterialTheme.typography.titleLarge
        )
        Text(
            text = "Body Large",
            style = MaterialTheme.typography.bodyLarge
        )
    }
}
```

### 10.3 Shapes

```kotlin
// 定义形状
val Shapes = Shapes(
    small = RoundedCornerShape(4.dp),
    medium = RoundedCornerShape(8.dp),
    large = RoundedCornerShape(16.dp)
)

// 使用
@Composable
fun ShapeExample() {
    Card(
        shape = MaterialTheme.shapes.medium
    ) {
        Text("Card with medium shape")
    }
}
```

### 10.4 自定义主题

```kotlin
// 自定义主题值
data class AppColors(
    val brand: Color,
    val accent: Color,
    val error: Color
)

private val LocalAppColors = staticCompositionLocalOf {
    AppColors(
        brand = Color.Unspecified,
        accent = Color.Unspecified,
        error = Color.Unspecified
    )
}

@Composable
fun AppTheme(
    content: @Composable () -> Unit
) {
    val appColors = AppColors(
        brand = Color(0xFF6200EE),
        accent = Color(0xFF03DAC5),
        error = Color(0xFFB00020)
    )
    
    CompositionLocalProvider(LocalAppColors provides appColors) {
        MaterialTheme(
            content = content
        )
    }
}

// 使用
@Composable
fun CustomThemeExample() {
    val appColors = LocalAppColors.current
    Box(modifier = Modifier.background(appColors.brand))
}
```

---

## 11. ViewModel 集成

### 11.1 基础使用

```kotlin
// ViewModel
class MainViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()
    
    fun increment() {
        _count.value++
    }
}

// Composable
@Composable
fun ViewModelExample() {
    val viewModel: MainViewModel = viewModel()
    val count by viewModel.count.collectAsState()
    
    Column {
        Text("Count: $count")
        Button(onClick = { viewModel.increment() }) {
            Text("Increment")
        }
    }
}
```

### 11.2 ViewModel + SavedStateHandle

```kotlin
class SavedStateViewModel(
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    var name by savedStateHandle.saveable { mutableStateOf("") }
    
    fun updateName(newName: String) {
        name = newName
    }
}

@Composable
fun SavedStateExample() {
    val viewModel: SavedStateViewModel = viewModel()
    
    Column {
        TextField(
            value = viewModel.name,
            onValueChange = { viewModel.updateName(it) }
        )
    }
}
```

### 11.3 Hilt + ViewModel

```kotlin
// 添加依赖
// implementation("androidx.hilt:hilt-navigation-compose:1.1.0")

@HiltViewModel
class HiltViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users
    
    init {
        loadUsers()
    }
    
    private fun loadUsers() {
        viewModelScope.launch {
            _users.value = repository.getUsers()
        }
    }
}

@Composable
fun HiltExample() {
    val viewModel: HiltViewModel = hiltViewModel()
    val users by viewModel.users.collectAsState()
    
    LazyColumn {
        items(users) { user ->
            Text(user.name)
        }
    }
}
```

---

## 12. 协程集成

### 12.1 LaunchedEffect

```kotlin
@Composable
fun LaunchedEffectExample() {
    var data by remember { mutableStateOf("") }
    
    // 当 key 变化时执行
    LaunchedEffect(key1 = "load") {
        // 协程作用域
        data = withContext(Dispatchers.IO) {
            fetchDataFromNetwork()
        }
    }
    
    Text(data)
}

// 带参数的 LaunchedEffect
@Composable
fun LaunchedEffectWithKey(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }
    
    // userId 变化时重新执行
    LaunchedEffect(key1 = userId) {
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
    
    Column {
        Text(data)
        Button(
            onClick = {
                // 在事件处理器中使用
                scope.launch {
                    data = withContext(Dispatchers.IO) {
                        fetchData()
                    }
                }
            }
        ) {
            Text("Load Data")
        }
    }
}
```

### 12.3 rememberAsyncImagePainter（Coil）

```kotlin
// 添加依赖
// implementation("io.coil-kt:coil-compose:2.5.0")

@Composable
fun AsyncImageExample() {
    AsyncImage(
        model = "https://example.com/image.jpg",
        contentDescription = null,
        modifier = Modifier.size(200.dp),
        contentScale = ContentScale.Crop
    )
    
    // 带状态的图片
    AsyncImage(
        model = "https://example.com/image.jpg",
        contentDescription = null,
        modifier = Modifier.size(200.dp),
        placeholder = painterResource(R.drawable.placeholder),
        error = painterResource(R.drawable.error),
        onSuccess = { },
        onError = { }
    )
}
```

---

## 13. Navigation 导航

### 13.1 基础导航

```kotlin
// 添加依赖
// implementation("androidx.navigation:navigation-compose:2.7.6")

@Composable
fun NavigationExample() {
    val navController = rememberNavController()
    
    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigate = { navController.navigate("detail") }
            )
        }
        
        composable("detail") {
            DetailScreen(
                onBack = { navController.popBackStack() }
            )
        }
    }
}

@Composable
fun HomeScreen(onNavigate: () -> Unit) {
    Column {
        Text("Home Screen")
        Button(onClick = onNavigate) {
            Text("Go to Detail")
        }
    }
}

@Composable
fun DetailScreen(onBack: () -> Unit) {
    Column {
        Text("Detail Screen")
        Button(onClick = onBack) {
            Text("Back")
        }
    }
}
```

### 13.2 带参数导航

```kotlin
@Composable
fun NavigationWithArgs() {
    val navController = rememberNavController()
    
    NavHost(navController, startDestination = "home") {
        composable("home") {
            HomeScreen { userId ->
                navController.navigate("detail/$userId")
            }
        }
        
        // 必填参数
        composable(
            route = "detail/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId")
            DetailScreen(userId = userId ?: "")
        }
        
        // 可选参数
        composable(
            route = "profile?userId={userId}",
            arguments = listOf(
                navArgument("userId") {
                    type = NavType.StringType
                    defaultValue = ""
                }
            )
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
                        icon = { Icon(item.icon, contentDescription = null) },
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
        NavHost(
            navController = navController,
            startDestination = "home",
            modifier = Modifier.padding(padding)
        ) {
            composable("home") { HomeScreen() }
            composable("search") { SearchScreen() }
            composable("profile") { ProfileScreen() }
        }
    }
}
```

---

## 14. 与传统 View 互操作

### 14.1 在 Compose 中使用 View

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
    
    // 嵌入 MapView
    AndroidView(
        modifier = Modifier.fillMaxSize(),
        factory = { context ->
            MapView(context).apply {
                onCreate(null)
                getMapAsync { map ->
                    // 配置地图
                }
            }
        }
    )
}
```

### 14.2 在 View 中使用 Compose

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
        Text("Hello from Compose in View!")
    }
}
```

### 14.3 互操作最佳实践

```kotlin
// 1. 渐进式迁移
class MixedActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContentView(R.layout.activity_mixed)
        
        // 部分 View 使用 Compose
        val composeView = findViewById<ComposeView>(R.id.composeView)
        composeView.setContent {
            // Compose 内容
        }
    }
}

// 2. 共享 ViewModel
class SharedViewModel : ViewModel() {
    val data = MutableStateFlow("")
}

// 在 View 中
val viewModel by viewModels<SharedViewModel>()

// 在 Compose 中
val viewModel: SharedViewModel = viewModel()
```

---

## 15. 手势处理

### 15.1 点击手势

```kotlin
@Composable
fun ClickGestures() {
    // 1. clickable
    Box(
        modifier = Modifier
            .size(100.dp)
            .clickable { }
            .background(Color.Blue)
    )
    
    // 2. combinedClickable
    var clickCount by remember { mutableStateOf(0) }
    Box(
        modifier = Modifier
            .size(100.dp)
            .combinedClickable(
                onClick = { clickCount++ },
                onDoubleClick = { clickCount += 10 },
                onLongClick = { clickCount = 0 }
            )
            .background(Color.Green)
    )
    
    // 3. 点击指示
    Box(
        modifier = Modifier
            .size(100.dp)
            .clickable(
                interactionSource = remember { MutableInteractionSource() },
                indication = rememberRipple(bounded = true)
            ) { }
            .background(Color.Red)
    )
}
```

### 15.2 拖动手势

```kotlin
@Composable
fun DragGestures() {
    var offsetX by remember { mutableStateOf(0f) }
    var offsetY by remember { mutableStateOf(0f) }
    
    Box(
        modifier = Modifier
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

### 15.3 缩放和旋转

```kotlin
@Composable
fun TransformGestures() {
    var scale by remember { mutableStateOf(1f) }
    var rotation by remember { mutableStateOf(0f) }
    var offset by remember { mutableStateOf(Offset.Zero) }
    
    Box(
        modifier = Modifier
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

---

## 16. Canvas 自定义绘制

### 16.1 基础 Canvas

```kotlin
@Composable
fun CanvasExample() {
    Canvas(modifier = Modifier.size(200.dp)) {
        // 绘制圆
        drawCircle(
            color = Color.Red,
            radius = 100f,
            center = center
        )
        
        // 绘制矩形
        drawRect(
            color = Color.Blue,
            topLeft = Offset(0f, 0f),
            size = Size(100f, 100f)
        )
        
        // 绘制线
        drawLine(
            color = Color.Green,
            start = Offset(0f, 0f),
            end = Offset(size.width, size.height),
            strokeWidth = 4f
        )
        
        // 绘制路径
        val path = Path().apply {
            moveTo(0f, 0f)
            lineTo(size.width / 2, size.height / 2)
            lineTo(size.width, 0f)
            close()
        }
        drawPath(path, Color.Yellow)
    }
}
```

### 16.2 复杂绘制

```kotlin
@Composable
fun ComplexCanvas() {
    Canvas(modifier = Modifier.fillMaxSize()) {
        // 绘制渐变背景
        drawRect(
            brush = Brush.verticalGradient(
                colors = listOf(Color.Cyan, Color.Blue),
                startY = 0f,
                endY = size.height
            )
        )
        
        // 绘制圆弧
        drawArc(
            color = Color.Red,
            startAngle = 0f,
            sweepAngle = 270f,
            useCenter = true,
            style = Stroke(width = 8f),
            size = Size(200f, 200f),
            topLeft = Offset(50f, 50f)
        )
        
        // 绘制文字
        drawIntoCanvas { canvas ->
            val paint = Paint().apply {
                color = Color.White
                textSize = 50f
            }
            canvas.nativeCanvas.drawText(
                "Hello Canvas",
                50f,
                300f,
                paint.asFrameworkPaint()
            )
        }
    }
}
```

---

## 17. 性能优化

### 17.1 稳定性优化

```kotlin
// 1. 使用 @Immutable 和 @Stable
@Immutable
data class User(val id: Int, val name: String)

@Stable
class UserViewModel {
    private val _user = MutableStateFlow(User(0, ""))
    val user: StateFlow<User> = _user
}

// 2. 避免不稳定的参数
@Composable
fun UnstableExample(users: List<User>) {
    // List 是不稳定的，每次都会重组
}

// 使用稳定的包装
@Immutable
data class UserList(val items: List<User>)

@Composable
fun StableExample(users: UserList) {
    // UserList 是稳定的
}
```

### 17.2 重组优化

```kotlin
// 1. 使用 remember 避免重复计算
@Composable
fun RememberOptimization() {
    val expensiveValue = remember {
        // 只计算一次
        performExpensiveCalculation()
    }
}

// 2. 使用 derivedStateOf 减少重组
@Composable
fun DerivedStateExample() {
    var searchQuery by remember { mutableStateOf("") }
    val items = remember { listOf<String>() }
    
    val filteredItems by remember {
        derivedStateOf {
            if (searchQuery.isEmpty()) {
                items
            } else {
                items.filter { it.contains(searchQuery, ignoreCase = true) }
            }
        }
    }
}

// 3. 使用 key 优化 LazyColumn
LazyColumn {
    items(
        items = items,
        key = { it.id }  // 唯一键
    ) { item ->
        ItemView(item)
    }
}
```

### 17.3 布局优化

```kotlin
// 1. 使用 Modifier.graphicsLayer 进行变换
Box(
    modifier = Modifier
        .graphicsLayer {
            rotationZ = rotation
            scaleX = scale
            scaleY = scale
        }
)

// 2. 避免过度嵌套
// ❌ 错误
Column {
    Column {
        Column {
            Text("Too nested")
        }
    }
}

// ✅ 正确
Column {
    Text("Flatter")
}

// 3. 使用 BaselineSkip
Column {
    Text("Title")
    Spacer(Modifier.height(8.dp))
    Text("Content")
}
```

### 17.4 性能分析工具

```kotlin
// 1. Composition Tracing
// 在 LocalInspectionMode 中启用

// 2. Layout Inspector
// Android Studio -> View -> Tool Windows -> Layout Inspector

// 3. Recomposition Count
// 使用 remember 记录重组次数
@Composable
fun RecompositionCounter() {
    var recompositionCount by remember { mutableStateOf(0) }
    SideEffect {
        recompositionCount++
        Log.d("Recomposition", "Count: $recompositionCount")
    }
}
```

---

## 18. 面试常见问题

### 18.1 基础概念

**Q1: Compose 与传统 View 的区别？**

A:
- **范式**：Compose 是声明式，View 是命令式
- **UI 定义**：Compose 用 Kotlin 代码，View 用 XML
- **状态管理**：Compose 自动响应状态，View 需要手动更新
- **性能**：Compose 通过智能重组优化，View 有层级开销
- **复用**：Compose 使用 Composable 函数，View 使用自定义 View

**Q2: 什么是重组（Recomposition）？**

A:
重组是指 Composable 函数在状态变化时重新执行的过程。特点：
- **智能**：只重组受影响的部分
- **可跳过**：如果输入未变化可跳过
- **乐观**：假设成功，失败时回滚
- **可并行**：不同 Composable 可并行重组

**Q3: remember 和 rememberSaveable 的区别？**

A:
- `remember`：在重组中保持状态，配置更改（如旋转）后丢失
- `rememberSaveable`：在重组和配置更改后都保持状态，通过 Bundle 保存

### 18.2 状态管理

**Q4: 什么是状态提升（State Hoisting）？**

A:
状态提升是将状态从子组件移到父组件的模式：
- 子组件变成无状态（Stateless）
- 父组件持有状态和业务逻辑
- 通过参数传递状态，通过回调传递事件
- 优点：可测试、可复用、单一数据源

**Q5: State 和 MutableState 的区别？**

A:
- `State<T>`：只读接口，用于读取状态
- `MutableState<T>`：可变接口，继承自 State，可以修改值
- 使用 `by` 代理语法简化访问

### 18.3 性能优化

**Q6: 如何优化 Compose 性能？**

A:
1. **稳定性**：使用 @Immutable/@Stable 注解
2. **remember**：缓存计算结果
3. **derivedStateOf**：减少不必要的重组
4. **LazyColumn key**：优化列表性能
5. **避免过度嵌套**：减少层级
6. **graphicsLayer**：用于变换操作

**Q7: 什么是稳定性（Stability）？**

A:
稳定性决定了 Compose 是否可以跳过重组：
- **稳定**：不可变或变化可预测
- **不稳定**：可变或变化不可预测
- 使用 @Immutable/@Stable 注解标记稳定类型

### 18.4 高级问题

**Q8: Compose 的执行模型是什么？**

A:
1. **Composition**：首次执行创建 UI 树
2. **Layout**：测量和放置元素
3. **Drawing**：绘制到屏幕
4. **Recomposition**：状态变化后重新执行

**Q9: Modifier 的执行顺序为什么重要？**

A:
Modifier 链的顺序会影响最终效果：
- 后面的 Modifier 作用在前面的结果上
- 例如：`padding.background` vs `background.padding`
- `padding.background`：背景包含 padding 区域
- `background.padding`：背景不包含 padding 区域

**Q10: 如何处理 Compose 中的副作用？**

A:
使用副作用 API：
- `LaunchedEffect`：在组合中安全地调用协程
- `rememberCoroutineScope`：获取协程作用域
- `DisposableEffect`：需要清理的副作用
- `SideEffect`：在成功组合后执行

### 18.5 实战问题

**Q11: 如何在 Compose 中实现 MVVM？**

A:
```kotlin
@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val users by viewModel.users.collectAsState()
    
    LazyColumn {
        items(users) { user ->
            UserItem(user, viewModel::onUserClick)
        }
    }
}
```

**Q12: Compose 中如何处理导航？**

A:
```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    
    NavHost(navController, startDestination = "home") {
        composable("home") { HomeScreen() }
        composable("detail/{id}") { DetailScreen() }
    }
}
```

**Q13: LazyColumn 和 RecyclerView 的区别？**

A:
- LazyColumn 使用 Composable 作为项
- RecyclerView 需要 Adapter 和 ViewHolder
- LazyColumn 自动处理回收
- LazyColumn 更简洁，代码量更少

**Q14: 如何调试 Compose 重组？**

A:
1. 使用 Layout Inspector
2. 启用 Composition Tracing
3. 使用 Log 记录重组次数
4. 检查稳定性警告

**Q15: Compose 中如何处理异步数据？**

A:
```kotlin
@Composable
fun AsyncDataExample(viewModel: MyViewModel = viewModel()) {
    val data by viewModel.data.collectAsState()
    
    when {
        data.isLoading -> LoadingView()
        data.error != null -> ErrorView(data.error)
        else -> DataView(data.value)
    }
}
```

---

## 总结

Jetpack Compose 是 Android UI 的未来，掌握 Compose 对于现代 Android 开发至关重要。核心要点：

1. **声明式思维**：描述 UI 是什么，而不是如何构建
2. **状态驱动**：UI 自动响应状态变化
3. **组合优于继承**：通过组合小函数构建复杂 UI
4. **性能优化**：理解重组、稳定性、remember
5. **互操作**：与传统 View 无缝协作

---

*Generated by OpenClaw | 2026-03-11*