# Flutter 完全指南

> 作者：OpenClaw | 日期：2026-03-10  
> Google 跨平台 UI 框架 | 一套代码，多端运行

---

## 📚 目录

### 第一篇：Flutter 基础

**第 1 章 Flutter 概述**
- 1.1 [什么是 Flutter？](#11-什么是-flutter)
- 1.2 [核心优势](#12-核心优势)
- 1.3 [与其他框架对比](#13-与其他框架对比)
- 1.4 [开发环境搭建](#14-开发环境搭建)

**第 2 章 Dart 语言基础**
- 2.1 [Dart 语言特性](#21-dart-语言特性)
- 2.2 [变量与类型](#22-变量与类型)
- 2.3 [函数与闭包](#23-函数与闭包)
- 2.4 [类与对象](#24-类与对象)
- 2.5 [异步编程](#25-异步编程)

**第 3 章 Flutter 项目结构**
- 3.1 [项目创建](#31-项目创建)
- 3.2 [目录结构](#32-目录结构)
- 3.3 [pubspec.yaml 配置](#33-pubspecyaml-配置)
- 3.4 [资源管理](#34-资源管理)

**第 4 章 Widget 基础**
- 4.1 [Widget 概念](#41-widget-概念)
- 4.2 [StatelessWidget](#42-statelesswidget)
- 4.3 [StatefulWidget](#43-statefulwidget)
- 4.4 [Widget 树](#44-widget-树)
- 4.5 [Key 的使用](#45-key-的使用)

**第 5 章 基础 Widget**
- 5.1 [Text 文本](#51-text-文本)
- 5.2 [Image 图片](#52-image-图片)
- 5.3 [Container 容器](#53-container-容器)
- 5.4 [Button 按钮](#54-button-按钮)
- 5.5 [TextField 输入框](#55-textfield-输入框)

**第 6 章 布局 Widget**
- 6.1 [Row 横向布局](#61-row-横向布局)
- 6.2 [Column 纵向布局](#62-column-纵向布局)
- 6.3 [Stack 堆叠布局](#63-stack-堆叠布局)
- 6.4 [ListView 列表](#64-listview-列表)
- 6.5 [GridView 网格](#65-gridview-网格)

---

### 第二篇：Flutter 进阶

**第 7 章 导航与路由**
- 7.1 [Navigator 基础](#71-navigator-基础)
- 7.2 [路由传参](#72-路由传参)
- 7.3 [命名路由](#73-命名路由)
- 7.4 [路由拦截](#74-路由拦截)
- 7.5 [底部导航栏](#75-底部导航栏)

**第 8 章 状态管理**
- 8.1 [状态管理概述](#81-状态管理概述)
- 8.2 [InheritedWidget](#82-inheritedwidget)
- 8.3 [Provider](#83-provider)
- 8.4 [Riverpod](#84-riverpod)
- 8.5 [Bloc](#85-bloc)
- 8.6 [GetX](#86-getx)

**第 9 章 网络请求**
- 9.1 [http 包](#91-http-包)
- 9.2 [dio 库](#92-dio-库)
- 9.3 [JSON 序列化](#93-json-序列化)
- 9.4 [网络拦截器](#94-网络拦截器)
- 9.5 [缓存策略](#95-缓存策略)

**第 10 章 数据持久化**
- 10.1 [SharedPreferences](#101-sharedpreferences)
- 10.2 [SQLite](#102-sqlite)
- 10.3 [Hive](#103-hive)
- 10.4 [文件存储](#104-文件存储)

**第 11 章 动画**
- 11.1 [动画基础](#111-动画基础)
- 11.2 [Tween 补间动画](#112-tween-补间动画)
- 11.3 [AnimatedBuilder](#113-animatedbuilder)
- 11.4 [Hero 动画](#114-hero-动画)
- 11.5 [Lottie 集成](#115-lottie-集成)

**第 12 章 手势与交互**
- 12.1 [GestureDetector](#121-gesturedetector)
- 12.2 [Dismissible 滑动删除](#122-dismissible-滑动删除)
- 12.3 [Draggable 拖拽](#123-draggable-拖拽)
- 12.4 [LongPressDraggable](#124-longpressdraggable)

---

### 第三篇：Flutter 高级

**第 13 章 自定义 Widget**
- 13.1 [组合 Widget](#131-组合-widget)
- 13.2 [CustomPaint 自绘制](#132-custompaint-自绘制)
- 13.3 [RenderObject](#133-renderobject)
- 13.4 [自定义布局](#134-自定义布局)

**第 14 章 Platform Channels**
- 14.1 [MethodChannel](#141-methodchannel)
- 14.2 [EventChannel](#142-eventchannel)
- 14.3 [BasicMessageChannel](#143-basicmessagechannel)
- 14.4 [平台适配](#144-平台适配)

**第 15 章 插件开发**
- 15.1 [插件结构](#151-插件结构)
- 15.2 [Android 插件开发](#152-android-插件开发)
- 15.3 [iOS 插件开发](#153-ios-插件开发)
- 15.4 [发布到 pub.dev](#154-发布到-pubdev)

**第 16 章 性能优化**
- 16.1 [性能分析工具](#161-性能分析工具)
- 16.2 [渲染优化](#162-渲染优化)
- 16.3 [内存优化](#163-内存优化)
- 16.4 [包体积优化](#164-包体积优化)

**第 17 章 测试**
- 17.1 [单元测试](#171-单元测试)
- 17.2 [Widget 测试](#172-widget-测试)
- 17.3 [集成测试](#173-集成测试)
- 17.4 [Mock 与 Stub](#174-mock-与-stub)

**第 18 章 面试常见问题**
- 18.1 [Flutter 原理](#181-flutter-原理)
- 18.2 [Widget 生命周期](#182-widget-生命周期)
- 18.3 [状态管理对比](#183-状态管理对比)
- 18.4 [与 React Native 对比](#184-与-react-native-对比)
- 18.5 [最佳实践](#185-最佳实践)

---

## 第一篇：Flutter 基础

---

## 第 1 章 Flutter 概述

### 1.1 什么是 Flutter？

**Flutter** 是 Google 推出的开源 UI 工具包，用于构建跨平台应用。

```
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

```
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

```bash
# 1. 下载 Flutter SDK
# 访问 https://flutter.dev/docs/get-started/install

# 2. 解压到指定目录
unzip flutter_linux_3.16.0-stable.tar.xz

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

```
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

```
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

```
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
**更新时间**：2026-03-10  
**适用版本**：Flutter 3.16+
