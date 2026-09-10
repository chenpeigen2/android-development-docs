# Flutter 完全指南

> 作者：OpenClaw | 日期：2026-03-10  
> Google 跨平台 UI 框架 | 一套代码，多端运行

---

## 📚 目录

- [第一篇：Flutter 基础](#第一篇flutter-基础)
- [第 1 章 Flutter 概述](#第-1-章-flutter-概述)
  - [1.1 什么是 Flutter？](#11-什么是-flutter)
  - [1.2 核心优势](#12-核心优势)
  - [1.3 与其他框架对比](#13-与其他框架对比)
  - [1.4 开发环境搭建](#14-开发环境搭建)
    - [安装 Flutter SDK](#安装-flutter-sdk)
    - [创建第一个项目](#创建第一个项目)
- [第 2 章 Dart 语言基础](#第-2-章-dart-语言基础)
  - [2.1 Dart 语言特性](#21-dart-语言特性)
  - [2.2 变量与类型](#22-变量与类型)
  - [2.3 函数与闭包](#23-函数与闭包)
  - [2.4 类与对象](#24-类与对象)
  - [2.5 异步编程](#25-异步编程)
- [第 3 章 Flutter 项目结构](#第-3-章-flutter-项目结构)
  - [3.1 项目创建](#31-项目创建)
  - [3.2 目录结构](#32-目录结构)
  - [3.3 pubspec.yaml 配置](#33-pubspecyaml-配置)
- [第 4 章 Widget 基础](#第-4-章-widget-基础)
  - [4.1 Widget 概念](#41-widget-概念)
  - [4.2 StatelessWidget](#42-statelesswidget)
  - [4.3 StatefulWidget](#43-statefulwidget)
- [第 5 章 基础 Widget](#第-5-章-基础-widget)
  - [5.1 Text 文本](#51-text-文本)
  - [5.2 Image 图片](#52-image-图片)
  - [5.3 Container 容器](#53-container-容器)
  - [5.4 Button 按钮](#54-button-按钮)
- [第 6 章 布局 Widget](#第-6-章-布局-widget)
  - [6.1 Row 横向布局](#61-row-横向布局)
  - [6.2 Column 纵向布局](#62-column-纵向布局)
  - [6.3 ListView 列表](#63-listview-列表)
- [第 18 章 面试常见问题](#第-18-章-面试常见问题)
  - [18.1 Flutter 原理](#181-flutter-原理)
  - [18.2 Widget 生命周期](#182-widget-生命周期)
  - [18.3 状态管理对比](#183-状态管理对比)
  - [18.4 与 React Native 对比](#184-与-react-native-对比)
  - [18.5 最佳实践](#185-最佳实践)
- [总结](#总结)
  - [Flutter 核心要点](#flutter-核心要点)
  - [适用场景](#适用场景)
  - [学习建议](#学习建议)
- [第 19 章 工程化实战：请求、持久化与宿主释放](#第-19-章-工程化实战请求持久化与宿主释放)
  - [19.1 Android Gradle 接入与 SDK 边界](#191-android-gradle-接入与-sdk-边界)
  - [19.2 FlutterEngine 与 Activity 分别拥有资源](#192-flutterengine-与-activity-分别拥有资源)

---

## 第一篇：Flutter 基础

---

## 第 1 章 Flutter 概述

### 1.1 什么是 Flutter？

**Flutter** 是 Google 推出的开源 UI 工具包，用于构建跨平台应用。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Flutter 核心特性                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │   Flutter    │
                         └──────┬───────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  跨平台       │      │  高性能       │      │  热重载       │
│               │      │               │      │               │
│ - Android    │      │ - 60fps      │      │ - 毫秒级     │
│ - iOS        │      │ - 原生编译    │      │ - 即时预览   │
│ - Web        │      │ - AOT        │      │ - 提升效率   │
│ - Desktop    │      │ - Skia 渲染  │      │               │
└───────────────┘      └───────────────┘      └───────────────┘
```

### 1.2 核心优势

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Flutter vs 其他跨平台框架                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────┬──────────────────┐
│       特性        │     Flutter      │  React Native   │     Xamarin      │
├──────────────────┼──────────────────┼──────────────────┼──────────────────┤
│  编程语言        │   Dart          │   JavaScript    │   C#            │
│  渲染方式        │   Skia 自绘     │   原生组件      │   原生组件      │
│  性能            │   ⭐⭐⭐⭐⭐      │      ⭐⭐⭐       │      ⭐⭐⭐       │
│  热重载          │   ⭐⭐⭐⭐⭐      │      ⭐⭐⭐⭐     │      ⭐⭐         │
│  UI 一致性       │   ⭐⭐⭐⭐⭐      │      ⭐⭐⭐       │      ⭐⭐⭐       │
│  学习曲线        │   ⭐⭐⭐⭐        │      ⭐⭐⭐       │      ⭐⭐⭐       │
│  社区活跃度      │   ⭐⭐⭐⭐⭐      │      ⭐⭐⭐⭐⭐   │      ⭐⭐⭐       │
│  生态成熟度      │   ⭐⭐⭐⭐        │      ⭐⭐⭐⭐⭐   │      ⭐⭐⭐⭐     │
│  包体积          │   较大 (10MB+)  │   中等          │   较大          │
│  原生访问        │   Platform      │   Native        │   P/Invoke      │
│                 │   Channel       │   Modules       │                 │
└──────────────────┴──────────────────┴──────────────────┴──────────────────┘
```

**Flutter 的优势**：

1. **跨平台**：一套代码运行在 Android、iOS、Web、Desktop
2. **高性能**：60fps 流畅动画，接近原生性能
3. **热重载**：毫秒级重载，快速迭代
4. **丰富的 Widget**：Material 和 Cupertino 风格
5. **单一代码库**：统一维护，减少成本
6. **Dart 语言**：强类型、异步支持、AOT 编译
7. **Skia 渲染**：自绘 UI，像素级控制

### 1.3 与其他框架对比

```dart
// Flutter 渲染架构
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Flutter 架构层次                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Framework (Dart)                                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Material │ Cupertino │ Widgets │ Rendering │ Animation │ Gestures  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Engine (C++)                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Skia │ Dart VM │ Text │ Platform Channels                            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Embedder (Platform-specific)                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Android (Java/Kotlin) │ iOS (Swift/ObjC) │ Web │ Desktop            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 开发环境搭建

#### 安装 Flutter SDK

此处固定下载 Flutter 3.16.0 Linux `.tar.xz` 归档，用 `tar` 而不是 ZIP 解压器；Windows 使用对应 SDK 的 ZIP 归档和 Windows 路径配置。安装后先核对 `flutter --version`，不让 PATH 中其他版本替换本章基线。

```bash
# 1. 下载 Flutter SDK
# 访问 https://flutter.dev/docs/get-started/install

# 2. 解压到指定目录
tar -xf flutter_linux_3.16.0-stable.tar.xz

# 3. 配置环境变量
export PATH="$PATH:`pwd`/flutter/bin"

# 4. 验证安装
flutter doctor

# 5. 配置 IDE（VS Code 或 Android Studio）
# 安装 Flutter 和 Dart 插件
```

#### 创建第一个项目

```bash
# 创建项目
flutter create my_app

# 进入项目目录
cd my_app

# 运行项目
flutter run

# 热重载：按 r
# 热重启：按 R
# 退出：按 q
```

---

## 第 2 章 Dart 语言基础

### 2.1 Dart 语言特性

```dart
/**
 * Dart 语言特点：
 * 
 * 1. 强类型语言（可选类型）
 * 2. 面向对象
 * 3. 支持异步（async/await）
 * 4. AOT 和 JIT 编译
 * 5. 空安全（Null Safety）
 */

// 1. 变量声明
var name = 'Flutter'; // 类型推断
String appName = 'MyApp'; // 显式类型
final version = '3.16.0'; // 运行时常量
const pi = 3.14159; // 编译时常量

// 2. 空安全
String? nullableName; // 可空类型
String nonNullableName = 'Dart'; // 非空类型

// 3. late 延迟初始化
late String description;

void main() {
  description = 'Flutter is awesome!';
  print(description);
}
```

### 2.2 变量与类型

```dart
/**
 * Dart 内置类型
 */

void main() {
  // 1. Numbers（数字）
  int count = 42;
  double price = 19.99;
  num number = 10; // int 或 double
  
  // 2. Strings（字符串）
  String greeting = 'Hello';
  String multiline = '''
    Multiple
    lines
  ''';
  String interpolation = 'Count: $count';
  
  // 3. Booleans（布尔）
  bool isValid = true;
  bool isEmpty = false;
  
  // 4. Lists（列表）
  List<int> numbers = [1, 2, 3, 4, 5];
  var mixed = [1, 'two', 3.0]; // List<Object>
  
  // 5. Sets（集合）
  Set<String> names = {'Alice', 'Bob', 'Charlie'};
  
  // 6. Maps（映射）
  Map<String, int> scores = {
    'Alice': 95,
    'Bob': 87,
  };
}
```

### 2.3 函数与闭包

```dart
/**
 * Dart 函数
 */

// 1. 基本函数
int add(int a, int b) {
  return a + b;
}

// 2. 箭头函数
int multiply(int a, int b) => a * b;

// 3. 可选参数
void greet(String name, [String? title]) {
  print('Hello, ${title ?? ''} $name');
}

// 4. 命名参数
void createUser({
  required String name,
  int? age,
  String city = 'Unknown',
}) {
  print('Name: $name, Age: $age, City: $city');
}

// 5. 闭包
Function makeAdder(int addBy) {
  return (int i) => i + addBy;
}

void main() {
  var add2 = makeAdder(2);
  print(add2(3)); // 5
}
```

### 2.4 类与对象

```dart
/**
 * Dart 类
 */

// 1. 基本类
class Person {
  String name;
  int age;
  
  Person(this.name, this.age);
  
  void introduce() {
    print('I am $name, $age years old.');
  }
}

// 2. 继承
class Student extends Person {
  String school;
  
  Student(String name, int age, this.school) : super(name, age);
  
  @override
  void introduce() {
    super.introduce();
    print('I study at $school');
  }
}

// 3. Mixin
mixin Flying {
  void fly() {
    print('Flying...');
  }
}

class Bird extends Animal with Flying {
  @override
  void makeSound() {
    print('Chirp!');
  }
}
```

### 2.5 异步编程

```dart
/**
 * Dart 异步编程
 */

// 1. Future
Future<String> fetchUser() {
  return Future.delayed(
    Duration(seconds: 2),
    () => 'User Data',
  );
}

// 2. async/await
Future<void> loadData() async {
  print('Loading...');
  String user = await fetchUser();
  print('Loaded: $user');
}

// 3. Stream
Stream<int> countStream() async* {
  for (int i = 1; i <= 5; i++) {
    await Future.delayed(Duration(seconds: 1));
    yield i;
  }
}

void main() async {
  // 使用 async/await
  await loadData();
  
  // 使用 Stream
  await for (int value in countStream()) {
    print(value);
  }
}
```

---

## 第 3 章 Flutter 项目结构

### 3.1 项目创建

```bash
# 创建基础项目
flutter create my_app

# 创建指定平台的项目
flutter create --platforms=android,ios my_app

# 创建 Kotlin 和 Swift 项目
flutter create --android-language kotlin --ios-language swift my_app
```

### 3.2 目录结构

```text
my_app/
├── android/          # Android 原生代码
├── ios/              # iOS 原生代码
├── lib/              # Dart 代码（主要开发目录）
│   └── main.dart     # 入口文件
├── test/             # 测试代码
├── web/              # Web 平台代码
└── pubspec.yaml      # 项目配置文件
```

### 3.3 pubspec.yaml 配置

```yaml
name: my_app
description: A new Flutter project.
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  
  cupertino_icons: ^1.0.6
  provider: ^6.1.1
  dio: ^5.4.0
  cached_network_image: ^3.3.1
  shared_preferences: ^2.2.2

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
  
  assets:
    - assets/images/
  
  fonts:
    - family: Roboto
      fonts:
        - asset: assets/fonts/Roboto-Regular.ttf
```

---

## 第 4 章 Widget 基础

### 4.1 Widget 概念

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Flutter Widget 树                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │   Widget     │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │StatelessWidget│  │StatefulWidget│  │ InheritedWidget│
  └──────────────┘  └──────────────┘  └──────────────┘
```

### 4.2 StatelessWidget

```dart
/**
 * StatelessWidget：无状态组件
 */

class MyStatelessWidget extends StatelessWidget {
  final String title;
  
  const MyStatelessWidget({super.key, required this.title});
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      child: Text(title),
    );
  }
}
```

### 4.3 StatefulWidget

```dart
/**
 * StatefulWidget：有状态组件
 */

class CounterWidget extends StatefulWidget {
  const CounterWidget({super.key});
  
  @override
  State<CounterWidget> createState() => _CounterWidgetState();
}

class _CounterWidgetState extends State<CounterWidget> {
  int _counter = 0;
  
  void _increment() {
    setState(() {
      _counter++;
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text('Count: $_counter'),
        SizedBox(height: 16),
        ElevatedButton(
          onPressed: _increment,
          child: Text('Increment'),
        ),
      ],
    );
  }
}
```

---

## 第 5 章 基础 Widget

### 5.1 Text 文本

```dart
class TextExamples extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // 基础文本
        Text('Hello Flutter'),
        
        // 样式文本
        Text(
          'Styled Text',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.blue,
          ),
        ),
        
        // 富文本
        RichText(
          text: TextSpan(
            text: 'Hello ',
            style: TextStyle(color: Colors.black),
            children: [
              TextSpan(
                text: 'Flutter',
                style: TextStyle(
                  color: Colors.blue,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
```

### 5.2 Image 图片

```dart
class ImageExamples extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // 资源图片
        Image.asset(
          'assets/images/logo.png',
          width: 100,
          height: 100,
        ),
        
        // 网络图片
        Image.network(
          'https://example.com/image.jpg',
          width: 100,
          height: 100,
          fit: BoxFit.cover,
        ),
        
        // 圆形图片
        ClipOval(
          child: Image.network(
            'https://example.com/avatar.jpg',
            width: 80,
            height: 80,
            fit: BoxFit.cover,
          ),
        ),
      ],
    );
  }
}
```

### 5.3 Container 容器

```dart
class ContainerExamples extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // 基础容器
        Container(
          width: 100,
          height: 100,
          color: Colors.blue,
        ),
        
        // 带边框和圆角
        Container(
          width: 150,
          height: 100,
          decoration: BoxDecoration(
            color: Colors.white,
            border: Border.all(color: Colors.blue, width: 2),
            borderRadius: BorderRadius.circular(8),
          ),
        ),
        
        // 渐变背景
        Container(
          width: 150,
          height: 100,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.blue, Colors.purple],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
      ],
    );
  }
}
```

### 5.4 Button 按钮

```dart
class ButtonExamples extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // ElevatedButton
        ElevatedButton(
          onPressed: () {
            print('ElevatedButton pressed');
          },
          child: Text('Elevated Button'),
        ),
        
        // TextButton
        TextButton(
          onPressed: () {
            print('TextButton pressed');
          },
          child: Text('Text Button'),
        ),
        
        // OutlinedButton
        OutlinedButton(
          onPressed: () {
            print('OutlinedButton pressed');
          },
          child: Text('Outlined Button'),
        ),
        
        // IconButton
        IconButton(
          icon: Icon(Icons.favorite),
          onPressed: () {
            print('IconButton pressed');
          },
        ),
      ],
    );
  }
}
```

---

## 第 6 章 布局 Widget

### 6.1 Row 横向布局

```dart
class RowExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        Container(width: 50, height: 50, color: Colors.red),
        Container(width: 50, height: 50, color: Colors.green),
        Container(width: 50, height: 50, color: Colors.blue),
      ],
    );
  }
}
```

### 6.2 Column 纵向布局

```dart
class ColumnExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(width: 100, height: 50, color: Colors.red),
        Container(width: 100, height: 50, color: Colors.green),
        Container(width: 100, height: 50, color: Colors.blue),
      ],
    );
  }
}
```

### 6.3 ListView 列表

```dart
class ListViewExample extends StatelessWidget {
  final List<String> items = List.generate(100, (index) => 'Item $index');
  
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) {
        return ListTile(
          title: Text(items[index]),
          onTap: () {
            print('Tapped ${items[index]}');
          },
        );
      },
    );
  }
}
```

---

## 第 18 章 面试常见问题

### 18.1 Flutter 原理

**Q: Flutter 的工作原理是什么？**

**A:**

1. **渲染机制**：
   - 使用 Skia 图形库
   - 自绘 UI，不依赖原生组件
   - 60fps 流畅渲染

2. **编译方式**：
   - JIT（即时编译）：开发阶段，支持热重载
   - AOT（提前编译）：发布阶段，性能接近原生

3. **架构层次**：
   - Framework（Dart）：Widget、Rendering、Animation
   - Engine（C++）：Skia、Dart VM
   - Embedder：平台适配层

### 18.2 Widget 生命周期

**Q: StatefulWidget 的生命周期？**

**A:**

```text
创建阶段：
1. createState() - 创建 State 对象
2. initState() - 初始化状态
3. didChangeDependencies() - 依赖变化

构建阶段：
4. build() - 构建 Widget 树

更新阶段：
5. didUpdateWidget() - Widget 更新
6. setState() - 触发重建

销毁阶段：
7. deactivate() - 从树中移除
8. dispose() - 释放资源
```

### 18.3 状态管理对比

**Q: Flutter 状态管理方案对比？**

**A:**

| 方案 | 特点 | 适用场景 |
|------|------|----------|
| setState | 简单直接 | 小型应用 |
| InheritedWidget | 原生方案 | 数据传递 |
| Provider | 推荐方案 | 中型应用 |
| Riverpod | 现代方案 | 复杂应用 |
| Bloc | 事件驱动 | 大型应用 |
| GetX | 全栈方案 | 快速开发 |

### 18.4 与 React Native 对比

**Q: Flutter vs React Native？**

**A:**

| 对比项 | Flutter | React Native |
|------|---------|--------------|
| 语言 | Dart | JavaScript |
| 渲染 | Skia 自绘 | 原生组件 |
| 性能 | 更高 | 较高 |
| 热重载 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| UI 一致性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 包体积 | 较大 | 中等 |
| 生态 | 快速发展 | 成熟 |

### 18.5 最佳实践

**Q: Flutter 开发的最佳实践？**

**A:**

1. **架构设计**：
   - 使用 MVVM 或 Clean Architecture
   - 分离 UI、逻辑、数据层

2. **状态管理**：
   - 优先使用 Provider 或 Riverpod
   - 避免过度使用 setState

3. **性能优化**：
   - 使用 const 构造函数
   - 避免 rebuild
   - 使用 ListView.builder

4. **代码规范**：
   - 遵循 Dart 代码规范
   - 使用 lint 工具
   - 编写单元测试

---

## 总结

### Flutter 核心要点

1. **跨平台**：一套代码，多端运行
2. **高性能**：Skia 渲染，60fps
3. **热重载**：毫秒级重载
4. **Dart 语言**：强类型、异步
5. **丰富的 Widget**：Material 和 Cupertino

### 适用场景

- ✅ 跨平台应用
- ✅ 高性能 UI
- ✅ 快速原型开发
- ✅ 创业项目

### 学习建议

1. **基础阶段**：掌握 Dart、Widget、布局
2. **进阶阶段**：状态管理、网络、动画
3. **高级阶段**：自定义 Widget、性能优化
4. **实战阶段**：完整项目开发

---

**文档版本**：v1.0  
**更新时间**：2026-09-09
**适用版本**：第 1–18 章以 Flutter 3.16.0 为历史基线；第 19 章单独使用 Flutter 3.35.0，不将两版 Android 模板或渲染默认值混用。


## 第 19 章 工程化实战：请求、持久化与宿主释放

Flutter 3.35.0 页面状态应由 State/Controller 持有，Repository 只负责业务接口。以下 `NotesRepository`、`Note` 是本文示例自定义类型，不是 Flutter API；真实实现需注入存储和错误策略。异步完成后先检查 `mounted`，dispose 时取消请求和订阅。

```dart
import 'package:flutter/material.dart';

class Note {
  const Note(this.text);
  final String text;
}
// 页面独占的请求作用域，不是共享给其他页面的全局 cancel-all Repository。
abstract interface class NotesRepository {
  Future<List<Note>> load();
  void cancelPending();
}
class NotesPage extends StatefulWidget {
  const NotesPage({super.key, required this.repository});
  final NotesRepository repository; // 业务接口
  @override State<NotesPage> createState() => _NotesPageState();
}
class _NotesPageState extends State<NotesPage> {
  int _generation = 0; bool _busy = false; String? _error;
  List<Note> _notes = const [];
  @override void initState() { super.initState(); load(); }
  @override void didUpdateWidget(covariant NotesPage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!identical(oldWidget.repository, widget.repository)) {
      ++_generation;
      oldWidget.repository.cancelPending();
      _notes = const [];
      load();
    }
  }
  Future<void> load() async {
    final generation = ++_generation;
    setState(() { _busy = true; _error = null; });
    try {
      final value = await widget.repository.load();
      if (mounted && generation == _generation) setState(() => _notes = value);
    } on Exception catch (_) {
      if (mounted && generation == _generation) setState(() => _error = '读取失败');
    } finally {
      if (mounted && generation == _generation) setState(() => _busy = false);
    }
  }
  @override void dispose() { ++_generation; widget.repository.cancelPending(); super.dispose(); }
  @override Widget build(BuildContext c) => Column(children: [
    if (_busy) const LinearProgressIndicator(), if (_error != null) Text(_error!),
    for (final note in _notes) Text(note.text),
    TextButton(onPressed: _busy ? null : load, child: const Text('重新加载')),
  ]);
}
```

`cancelPending()` 是业务接口，不是 Flutter 内建方法；若底层使用 `HttpClient`/dio，应让它真正关闭或取消请求。`setState` 不能在 dispose 后调用，`mounted` 不能代替资源取消。


### 19.1 Android Gradle 接入与 SDK 边界

Flutter 3.35.0 的 `FlutterExtension` 默认是 **minSdk 24、compileSdk/targetSdk 36、NDK 27.0.12077973**。在 Android 17 设备上运行不等于已经 target API 37；需要改 target 时应独立验证宿主 AGP、所有插件以及行为变更，而不是只改一个数字。

3.35.0 模板在 `settings.gradle.kts` 的 `pluginManagement` 中，从 `local.properties` 读取 `flutter.sdk`，再 `includeBuild("$flutterSdkPath/packages/flutter_tools/gradle")`；settings 应用 `dev.flutter.flutter-plugin-loader`，app 应用 `dev.flutter.flutter-gradle-plugin`。loader 与 app plugin 职责不同，不能省掉 includeBuild 后把插件当普通 Maven 依赖。add-to-app 宿主选择源码模块或预编译 AAR 方案；模块的 `.android` 是生成宿主，不把手工改动放在那里作为永久配置。

固定源码：[3.35.0 FlutterExtension](https://github.com/flutter/flutter/blob/3.35.0/packages/flutter_tools/gradle/src/main/kotlin/FlutterExtension.kt)、[settings 模板](https://github.com/flutter/flutter/blob/3.35.0/packages/flutter_tools/templates/app/android.tmpl/settings.gradle.kts.tmpl)。

### 19.2 FlutterEngine 与 Activity 分别拥有资源

普通 `FlutterActivity` 自建的 engine 默认随宿主销毁；缓存或外部提供的 engine 默认不销毁。预热引擎的所有者先执行 Dart 入口，再缓存；重新启动进程后缓存为空，必须重建，不能仅恢复一个 engine ID。

```kotlin
// 宿主初始化阶段，在主线程执行一次；不要在每次进入页面时重复创建。
val engine = FlutterEngine(applicationContext)
engine.dartExecutor.executeDartEntrypoint(DartExecutor.DartEntrypoint.createDefault())
FlutterEngineCache.getInstance().put("notes-engine", engine)

// Activity 内；宿主清单须声明 FlutterActivity，并具备模板要求的主题/配置。
startActivity(
    FlutterActivity.withCachedEngine("notes-engine")
        .destroyEngineWithActivity(false)
        .build(this)
)

// 真正的 engine 所有者结束服务、且已没有附着宿主时才执行：
// FlutterEngineCache.getInstance().remove("notes-engine")
// engine.destroy()
```

所需 import 为 `io.flutter.embedding.android.FlutterActivity`、`io.flutter.embedding.engine.FlutterEngine`、`FlutterEngineCache` 和 `io.flutter.embedding.engine.dart.DartExecutor`。缓存移除不等于 engine 已 destroy，也不能把同一 engine 同时附着到两个独立 Activity。插件实现 `ActivityAware` 时，在 `onDetachedFromActivityForConfigChanges` 清旧 Activity/监听器，在 `onReattachedToActivityForConfigChanges` 绑定新实例；保留 engine 并不允许永久保留旧 Activity。页面专属 MethodChannel handler 按页面所有权解绑，engine 级 handler 由 engine owner 释放，不能一概在任意 Activity 销毁时撤销共享 handler。

固定源码：[FlutterActivity.shouldDestroyEngineWithHost/configureFlutterEngine](https://github.com/flutter/flutter/blob/3.35.0/engine/src/flutter/shell/platform/android/io/flutter/embedding/android/FlutterActivity.java)、[Delegate.onDetach](https://github.com/flutter/flutter/blob/3.35.0/engine/src/flutter/shell/platform/android/io/flutter/embedding/android/FlutterActivityAndFragmentDelegate.java)、[ActivityAware](https://github.com/flutter/flutter/blob/3.35.0/engine/src/flutter/shell/platform/android/io/flutter/embedding/engine/plugins/activity/ActivityAware.java)。
