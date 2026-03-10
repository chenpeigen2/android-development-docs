# React Native 完全指南

> 作者：OpenClaw | 日期：2026-03-10  
> Facebook 跨平台移动开发框架 | Learn Once, Write Anywhere

---

## 📚 目录

### 第一篇：React Native 基础

**第 1 章 React Native 概述**
- 1.1 [什么是 React Native？](#11-什么是-react-native)
- 1.2 [核心优势](#12-核心优势)
- 1.3 [与 Flutter 对比](#13-与-flutter-对比)
- 1.4 [开发环境搭建](#14-开发环境搭建)

**第 2 章 JavaScript/TypeScript 基础**
- 2.1 [ES6+ 新特性](#21-es6-新特性)
- 2.2 [TypeScript 基础](#22-typescript-基础)
- 2.3 [函数与闭包](#23-函数与闭包)
- 2.4 [异步编程](#24-异步编程)

**第 3 章 React 基础**
- 3.1 [React 核心概念](#31-react-核心概念)
- 3.2 [JSX 语法](#32-jsx-语法)
- 3.3 [组件与 Props](#33-组件与-props)
- 3.4 [State 与生命周期](#34-state-与生命周期)
- 3.5 [Hooks 详解](#35-hooks-详解)

**第 4 章 React Native 核心组件**
- 4.1 [View 视图](#41-view-视图)
- 4.2 [Text 文本](#42-text-文本)
- 4.3 [Image 图片](#43-image-图片)
- 4.4 [ScrollView 滚动视图](#44-scrollview-滚动视图)
- 4.5 [FlatList 列表](#45-flatlist-列表)

**第 5 章 样式与布局**
- 5.1 [Flexbox 布局](#51-flexbox-布局)
- 5.2 [StyleSheet 样式](#52-stylesheet-样式)
- 5.3 [尺寸单位](#53-尺寸单位)
- 5.4 [响应式设计](#54-响应式设计)

**第 6 章 导航**
- 6.1 [React Navigation 基础](#61-react-navigation-基础)
- 6.2 [Stack Navigator](#62-stack-navigator)
- 6.3 [Tab Navigator](#63-tab-navigator)
- 6.4 [Drawer Navigator](#64-drawer-navigator)
- 6.5 [路由传参](#65-路由传参)

---

### 第二篇：React Native 进阶

**第 7 章 状态管理**
- 7.1 [Context API](#71-context-api)
- 7.2 [Redux](#72-redux)
- 7.3 [MobX](#73-mobx)
- 7.4 [Zustand](#74-zustand)
- 7.5 [状态管理对比](#75-状态管理对比)

**第 8 章 网络请求**
- 8.1 [Fetch API](#81-fetch-api)
- 8.2 [Axios](#82-axios)
- 8.3 [网络拦截器](#83-网络拦截器)
- 8.4 [缓存策略](#84-缓存策略)

**第 9 章 数据持久化**
- 9.1 [AsyncStorage](#91-asyncstorage)
- 9.2 [SQLite](#92-sqlite)
- 9.3 [Realm](#93-realm)
- 9.4 [WatermelonDB](#94-watermelondb)

**第 10 章 动画**
- 10.1 [Animated API](#101-animated-api)
- 10.2 [Reanimated](#102-reanimated)
- 10.3 [Lottie](#103-lottie)
- 10.4 [手势动画](#104-手势动画)

**第 11 章 手势处理**
- 11.1 [GestureResponder](#111-gestureresponder)
- 11.2 [React Native Gesture Handler](#112-react-native-gesture-handler)
- 11.3 [滑动删除](#113-滑动删除)
- 11.4 [拖拽排序](#114-拖拽排序)

**第 12 章 原生模块**
- 12.1 [Native Modules 基础](#121-native-modules-基础)
- 12.2 [iOS 原生模块](#122-ios-原生模块)
- 12.3 [Android 原生模块](#123-android-原生模块)
- 12.4 [Native UI Components](#124-native-ui-components)

---

### 第三篇：React Native 高级

**第 13 章 性能优化**
- 13.1 [性能分析工具](#131-性能分析工具)
- 13.2 [列表优化](#132-列表优化)
- 13.3 [图片优化](#133-图片优化)
- 13.4 [内存优化](#134-内存优化)
- 13.5 [Bundle 优化](#135-bundle-优化)

**第 14 章 调试与测试**
- 14.1 [调试工具](#141-调试工具)
- 14.2 [单元测试](#142-单元测试)
- 14.3 [组件测试](#143-组件测试)
- 14.4 [E2E 测试](#144-e2e-测试)

**第 15 章 新架构**
- 15.1 [Fabric](#151-fabric)
- 15.2 [TurboModules](#152-turbomodules)
- 15.3 [CodeGen](#153-codegen)
- 15.4 [架构迁移](#154-架构迁移)

**第 16 章 Expo 开发**
- 16.1 [Expo 基础](#161-expo-基础)
- 16.2 [Expo SDK](#162-expo-sdk)
- 16.3 [Expo Router](#163-expo-router)
- 16.4 [Expo vs Bare React Native](#164-expo-vs-bare-react-native)

**第 17 章 发布与部署**
- 17.1 [iOS 发布](#171-ios-发布)
- 17.2 [Android 发布](#172-android-发布)
- 17.3 [CodePush 热更新](#173-codepush-热更新)
- 17.4 [CI/CD](#174-cicd)

**第 18 章 面试常见问题**
- 18.1 [React Native 原理](#181-react-native-原理)
- 18.2 [Bridge 机制](#182-bridge-机制)
- 18.3 [与 Flutter 对比](#183-与-flutter-对比)
- 18.4 [性能优化](#184-性能优化)
- 18.5 [最佳实践](#185-最佳实践)

---

## 第一篇：React Native 基础

---

## 第 1 章 React Native 概述

### 1.1 什么是 React Native？

**React Native** 是 Facebook 开发的跨平台移动应用框架，使用 JavaScript 和 React 构建原生移动应用。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       React Native 核心架构                                 │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │ React Native │
                         └──────┬───────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  JavaScript   │      │    Bridge     │      │  Native       │
│    Layer      │──────│   通信层      │──────│   Modules     │
│               │      │               │      │               │
│ - React      │      │ - JSON       │      │ - iOS        │
│ - Components │      │ - Async      │      │ - Android    │
│ - State      │      │ - Batch      │      │ - Native UI  │
└───────────────┘      └───────────────┘      └───────────────┘
```

### 1.2 核心优势

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       React Native vs Flutter                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────┐
│       特性        │  React Native   │     Flutter      │
├──────────────────┼──────────────────┼──────────────────┤
│  编程语言        │   JavaScript    │   Dart          │
│  渲染方式        │   原生组件      │   Skia 自绘     │
│  性能            │   ⭐⭐⭐⭐        │   ⭐⭐⭐⭐⭐      │
│  热重载          │   ⭐⭐⭐⭐        │   ⭐⭐⭐⭐⭐      │
│  UI 一致性       │   ⭐⭐⭐         │   ⭐⭐⭐⭐⭐      │
│  学习曲线        │   ⭐⭐⭐         │   ⭐⭐⭐⭐        │
│  社区活跃度      │   ⭐⭐⭐⭐⭐      │   ⭐⭐⭐⭐⭐      │
│  生态成熟度      │   ⭐⭐⭐⭐⭐      │   ⭐⭐⭐⭐        │
│  包体积          │   中等          │   较大 (10MB+)  │
│  原生访问        │   Native Modules│   Platform      │
│                 │                 │   Channel       │
└──────────────────┴──────────────────┴──────────────────┘
```

**React Native 的优势**：

1. **跨平台**：一套 JavaScript 代码，iOS 和 Android 通用
2. **原生组件**：使用真正的原生 UI 组件
3. **热重载**：快速迭代，即时预览
4. **JavaScript 生态**：npm 丰富的包资源
5. **React 语法**：熟悉 React 的开发者上手快
6. **社区活跃**：Facebook 支持，社区贡献丰富
7. **CodePush**：支持热更新，无需重新发布

### 1.3 与 Flutter 对比

**React Native 适用场景**：
- ✅ 已有 React Web 开发经验
- ✅ 需要原生 UI 外观
- ✅ 快速迭代，频繁更新
- ✅ 需要复用 Web 代码

**Flutter 适用场景**：
- ✅ 追求极致性能
- ✅ 需要高度定制 UI
- ✅ 全新项目
- ✅ 需要像素级一致性

### 1.4 开发环境搭建

#### 安装 React Native CLI

```bash
# 1. 安装 Node.js
# 访问 https://nodejs.org/

# 2. 安装 React Native CLI
npm install -g react-native-cli

# 3. 安装 JDK（Android 开发）
# 访问 https://adoptium.net/

# 4. 安装 Android Studio
# 配置 Android SDK

# 5. 安装 Xcode（iOS 开发，仅 macOS）
# 从 App Store 安装

# 6. 安装 CocoaPods（iOS 依赖管理）
sudo gem install cocoapods
```

#### 创建第一个项目

```bash
# 创建项目
npx react-native@latest init MyApp

# 进入项目目录
cd MyApp

# iOS 运行
npx react-native run-ios

# Android 运行
npx react-native run-android

# 启动 Metro Bundler
npx react-native start
```

---

## 第 2 章 JavaScript/TypeScript 基础

### 2.1 ES6+ 新特性

```javascript
/**
 * ES6+ 常用特性
 */

// 1. 箭头函数
const add = (a, b) => a + b;

// 2. 解构赋值
const { name, age } = user;
const [first, second] = array;

// 3. 模板字符串
const greeting = `Hello, ${name}!`;

// 4. 展开运算符
const newArray = [...oldArray, newItem];
const newObject = { ...oldObject, newProp: value };

// 5. Promise
const fetchData = () => {
  return new Promise((resolve, reject) => {
    // 异步操作
    resolve(data);
  });
};

// 6. async/await
const loadUser = async () => {
  try {
    const user = await fetchUser();
    return user;
  } catch (error) {
    console.error(error);
  }
};

// 7. 可选链
const name = user?.profile?.name;

// 8. 空值合并
const value = input ?? 'default';
```

### 2.2 TypeScript 基础

```typescript
/**
 * TypeScript 基础类型
 */

// 1. 基本类型
let name: string = 'React Native';
let count: number = 42;
let isValid: boolean = true;

// 2. 数组
let numbers: number[] = [1, 2, 3];
let users: Array<string> = ['Alice', 'Bob'];

// 3. 接口
interface User {
  id: number;
  name: string;
  email?: string; // 可选属性
}

// 4. 类型别名
type Status = 'pending' | 'success' | 'error';

// 5. 函数类型
const fetchUser: (id: number) => Promise<User> = async (id) => {
  // ...
};

// 6. 泛型
function identity<T>(arg: T): T {
  return arg;
}

// 7. 组件 Props 类型
interface ButtonProps {
  title: string;
  onPress: () => void;
  disabled?: boolean;
}
```

### 2.3 函数与闭包

```javascript
/**
 * 函数与闭包
 */

// 1. 普通函数
function greet(name) {
  return `Hello, ${name}`;
}

// 2. 箭头函数
const greet = (name) => `Hello, ${name}`;

// 3. 高阶函数
const withLoading = (Component) => {
  return (props) => {
    if (props.loading) {
      return <ActivityIndicator />;
    }
    return <Component {...props} />;
  };
};

// 4. 闭包
const createCounter = () => {
  let count = 0;
  return {
    increment: () => ++count,
    decrement: () => --count,
    getCount: () => count,
  };
};

// 5. 柯里化
const add = (a) => (b) => a + b;
const add5 = add(5);
console.log(add5(3)); // 8
```

### 2.4 异步编程

```javascript
/**
 * 异步编程
 */

// 1. Callback
const fetchData = (callback) => {
  setTimeout(() => {
    callback(null, { data: 'success' });
  }, 1000);
};

// 2. Promise
const fetchData = () => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve({ data: 'success' });
    }, 1000);
  });
};

// 3. async/await
const loadData = async () => {
  try {
    const response = await fetchData();
    console.log(response);
  } catch (error) {
    console.error(error);
  }
};

// 4. Promise.all
const loadAllData = async () => {
  const [users, posts] = await Promise.all([
    fetchUsers(),
    fetchPosts(),
  ]);
  return { users, posts };
};

// 5. Promise.race
const fetchWithTimeout = async (url, timeout) => {
  const response = await Promise.race([
    fetch(url),
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Timeout')), timeout)
    ),
  ]);
  return response;
};
```

---

## 第 3 章 React 基础

### 3.1 React 核心概念

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       React 核心概念                                        │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │    React     │
                         └──────┬───────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  Components   │      │    State      │      │    Props      │
│               │      │               │      │               │
│ - Functional │      │ - useState   │      │ - 传递数据    │
│ - Class      │      │ - useReducer │      │ - 只读        │
│ - 组合       │      │ - Context    │      │ - 单向流      │
└───────────────┘      └───────────────┘      └───────────────┘
```

### 3.2 JSX 语法

```jsx
/**
 * JSX 语法
 */

// 1. 基础 JSX
const element = <Text>Hello, React Native!</Text>;

// 2. 嵌套 JSX
const card = (
  <View style={styles.card}>
    <Text style={styles.title}>Title</Text>
    <Text style={styles.content}>Content</Text>
  </View>
);

// 3. 表达式嵌入
const name = 'React Native';
const greeting = <Text>Hello, {name}!</Text>;

// 4. 条件渲染
const element = (
  <View>
    {isLoggedIn ? <Home /> : <Login />}
  </View>
);

// 5. 列表渲染
const items = ['Apple', 'Banana', 'Orange'];
const list = (
  <View>
    {items.map((item, index) => (
      <Text key={index}>{item}</Text>
    ))}
  </View>
);

// 6. 样式对象
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    fontSize: 18,
    color: '#333',
  },
});
```

### 3.3 组件与 Props

```jsx
/**
 * 函数组件
 */
const Greeting = ({ name }) => {
  return <Text>Hello, {name}!</Text>;
};

// 使用
<Greeting name="React Native" />

/**
 * 类组件
 */
class Counter extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
  }

  render() {
    return (
      <View>
        <Text>Count: {this.state.count}</Text>
        <Button 
          title="Increment" 
          onPress={() => this.setState({ count: this.state.count + 1 })}
        />
      </View>
    );
  }
}

/**
 * Props 类型检查
 */
import PropTypes from 'prop-types';

const UserCard = ({ name, age, email }) => {
  return (
    <View>
      <Text>{name}</Text>
      <Text>{age}</Text>
      <Text>{email}</Text>
    </View>
  );
};

UserCard.propTypes = {
  name: PropTypes.string.isRequired,
  age: PropTypes.number,
  email: PropTypes.string,
};

UserCard.defaultProps = {
  age: 0,
  email: '',
};
```

### 3.4 State 与生命周期

```jsx
/**
 * State 管理
 */

// 函数组件 + Hooks
const Counter = () => {
  const [count, setCount] = useState(0);

  return (
    <View>
      <Text>Count: {count}</Text>
      <Button title="+" onPress={() => setCount(count + 1)} />
    </View>
  );
};

/**
 * 生命周期（类组件）
 */
class Profile extends React.Component {
  constructor(props) {
    super(props);
    this.state = { user: null };
  }

  // 挂载
  componentDidMount() {
    this.fetchUser();
  }

  // 更新
  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) {
      this.fetchUser();
    }
  }

  // 卸载
  componentWillUnmount() {
    this.cancelRequest?.();
  }

  fetchUser = async () => {
    const user = await fetchUser(this.props.userId);
    this.setState({ user });
  };

  render() {
    const { user } = this.state;
    if (!user) return <ActivityIndicator />;
    return <UserProfile user={user} />;
  }
}
```

### 3.5 Hooks 详解

```jsx
/**
 * React Hooks
 */

// 1. useState - 状态管理
const [state, setState] = useState(initialValue);

// 2. useEffect - 副作用
useEffect(() => {
  // 组件挂载或依赖变化时执行
  return () => {
    // 清理函数
  };
}, [dependencies]);

// 3. useContext - 上下文
const value = useContext(MyContext);

// 4. useReducer - 复杂状态
const [state, dispatch] = useReducer(reducer, initialState);

// 5. useCallback - 缓存回调
const memoizedCallback = useCallback(() => {
  doSomething(a, b);
}, [a, b]);

// 6. useMemo - 缓存计算值
const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);

// 7. useRef - 引用
const inputRef = useRef(null);

// 8. 自定义 Hook
const useUser = (userId) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(data => {
      setUser(data);
      setLoading(false);
    });
  }, [userId]);

  return { user, loading };
};

// 使用自定义 Hook
const Profile = ({ userId }) => {
  const { user, loading } = useUser(userId);
  
  if (loading) return <ActivityIndicator />;
  return <UserProfile user={user} />;
};
```

---

## 第 4 章 React Native 核心组件

### 4.1 View 视图

```jsx
/**
 * View 组件 - 基础容器
 */
import { View } from 'react-native';

const ViewExample = () => {
  return (
    <View style={{
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: '#f5f5f5',
    }}>
      <View style={{
        width: 100,
        height: 100,
        backgroundColor: 'skyblue',
        borderRadius: 8,
      }} />
    </View>
  );
};
```

### 4.2 Text 文本

```jsx
/**
 * Text 组件 - 文本显示
 */
import { Text, StyleSheet } from 'react-native';

const TextExample = () => {
  return (
    <View>
      {/* 基础文本 */}
      <Text>Hello React Native</Text>
      
      {/* 样式文本 */}
      <Text style={styles.title}>Title</Text>
      
      {/* 嵌套文本 */}
      <Text>
        Hello <Text style={{ fontWeight: 'bold' }}>React Native</Text>!
      </Text>
      
      {/* 文本输入 */}
      <TextInput
        style={styles.input}
        placeholder="Enter text"
        onChangeText={setText}
        value={text}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    paddingHorizontal: 10,
  },
});
```

### 4.3 Image 图片

```jsx
/**
 * Image 组件 - 图片显示
 */
import { Image } from 'react-native';

const ImageExample = () => {
  return (
    <View>
      {/* 本地图片 */}
      <Image 
        source={require('./logo.png')} 
        style={{ width: 100, height: 100 }}
      />
      
      {/* 网络图片 */}
      <Image 
        source={{ uri: 'https://example.com/image.jpg' }}
        style={{ width: 100, height: 100 }}
      />
      
      {/* 圆形图片 */}
      <Image 
        source={{ uri: 'https://example.com/avatar.jpg' }}
        style={{ width: 80, height: 80, borderRadius: 40 }}
      />
      
      {/* 背景图片 */}
      <ImageBackground 
        source={require('./background.jpg')}
        style={{ width: '100%', height: 200 }}
      >
        <Text>Overlay Text</Text>
      </ImageBackground>
    </View>
  );
};
```

### 4.4 ScrollView 滚动视图

```jsx
/**
 * ScrollView - 滚动容器
 */
import { ScrollView } from 'react-native';

const ScrollViewExample = () => {
  return (
    <ScrollView 
      horizontal={false}  // 垂直滚动
      showsVerticalScrollIndicator={true}
      contentContainerStyle={{ padding: 20 }}
    >
      <Text style={styles.heading}>Section 1</Text>
      <Text>Content for section 1...</Text>
      
      <Text style={styles.heading}>Section 2</Text>
      <Text>Content for section 2...</Text>
      
      {/* 更多内容... */}
    </ScrollView>
  );
};
```

### 4.5 FlatList 列表

```jsx
/**
 * FlatList - 高性能列表
 */
import { FlatList, Text, View } from 'react-native';

const FlatListExample = () => {
  const data = [
    { id: '1', title: 'Item 1' },
    { id: '2', title: 'Item 2' },
    { id: '3', title: 'Item 3' },
  ];

  const renderItem = ({ item }) => (
    <View style={styles.item}>
      <Text>{item.title}</Text>
    </View>
  );

  return (
    <FlatList
      data={data}
      renderItem={renderItem}
      keyExtractor={item => item.id}
      ItemSeparatorComponent={() => <View style={styles.separator} />}
      ListHeaderComponent={() => <Text style={styles.header}>Header</Text>}
      ListFooterComponent={() => <Text style={styles.footer}>Footer</Text>}
      onEndReached={() => console.log('Load more')}
      onEndReachedThreshold={0.5}
    />
  );
};

const styles = StyleSheet.create({
  item: {
    padding: 20,
    backgroundColor: '#fff',
  },
  separator: {
    height: 1,
    backgroundColor: '#eee',
  },
});
```

---

## 第 5 章 样式与布局

### 5.1 Flexbox 布局

```jsx
/**
 * Flexbox 布局
 */

// 1. 主轴方向
<View style={{ flexDirection: 'row' }}>     {/* 水平 */}
<View style={{ flexDirection: 'column' }}> {/* 垂直 */}

// 2. 主轴对齐
<View style={{ justifyContent: 'flex-start' }}>    {/* 起点 */}
<View style={{ justifyContent: 'center' }}>        {/* 居中 */}
<View style={{ justifyContent: 'flex-end' }}>      {/* 终点 */}
<View style={{ justifyContent: 'space-between' }}> {/* 两端 */}
<View style={{ justifyContent: 'space-around' }}>  {/* 均分 */}
<View style={{ justifyContent: 'space-evenly' }}>  {/* 等距 */}

// 3. 交叉轴对齐
<View style={{ alignItems: 'flex-start' }}> {/* 起点 */}
<View style={{ alignItems: 'center' }}>     {/* 居中 */}
<View style={{ alignItems: 'flex-end' }}>   {/* 终点 */}
<View style={{ alignItems: 'stretch' }}>    {/* 拉伸 */}

// 4. Flex 比例
<View style={{ flex: 1 }}> {/* 占 1 份 */}
<View style={{ flex: 2 }}> {/* 占 2 份 */}

// 5. 完整示例
const FlexboxExample = () => {
  return (
    <View style={{
      flex: 1,
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    }}>
      <View style={{ width: 50, height: 50, backgroundColor: 'red' }} />
      <View style={{ width: 50, height: 50, backgroundColor: 'green' }} />
      <View style={{ width: 50, height: 50, backgroundColor: 'blue' }} />
    </View>
  );
};
```

### 5.2 StyleSheet 样式

```jsx
/**
 * StyleSheet - 样式表
 */
import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

// 使用
const App = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Hello</Text>
      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>Press Me</Text>
      </TouchableOpacity>
    </View>
  );
};
```

---

## 第 18 章 面试常见问题

### 18.1 React Native 原理

**Q: React Native 的工作原理是什么？**

**A:**

1. **JavaScript 线程**：
   - 运行 React 代码
   - 处理业务逻辑
   - 创建 Virtual DOM

2. **Bridge（桥接）**：
   - JSON 序列化通信
   - 异步批量传输
   - JS ↔ Native 消息传递

3. **Native 线程**：
   - 渲染原生 UI
   - 处理原生事件
   - 调用原生 API

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       React Native 工作流程                                 │
└─────────────────────────────────────────────────────────────────────────────┘

JavaScript Thread              Bridge              Native Thread
       │                         │                       │
       │  1. Virtual DOM         │                       │
       ├────────────────────────>│                       │
       │                         │  2. JSON Message      │
       │                         ├──────────────────────>│
       │                         │                       │
       │                         │  3. Native UI         │
       │                         │<──────────────────────┤
       │  4. Events              │                       │
       │<────────────────────────┤                       │
       │                         │                       │
```

### 18.2 Bridge 机制

**Q: React Native Bridge 的工作机制？**

**A:**

1. **通信方式**：
   - JSON 序列化
   - 异步传输
   - 批量处理

2. **性能瓶颈**：
   - 序列化开销
   - Bridge 队列阻塞
   - 大量数据传输

3. **新架构**：
   - Fabric：新渲染系统
   - TurboModules：直接调用
   - JSI：JavaScript 接口

### 18.3 与 Flutter 对比

**Q: React Native vs Flutter？**

**A:**

| 对比项 | React Native | Flutter |
|------|-------------|---------|
| 语言 | JavaScript/TypeScript | Dart |
| 渲染 | 原生组件 | Skia 自绘 |
| 性能 | 较高 | 更高 |
| UI 一致性 | 原生风格 | 自绘一致 |
| 包体积 | 中等 | 较大 |
| 热重载 | ✅ | ✅ |
| 生态 | npm 丰富 | 快速发展 |
| 学习曲线 | 需要 React | 需要学习 Dart |

### 18.4 性能优化

**Q: React Native 性能优化技巧？**

**A:**

1. **列表优化**：
   - 使用 FlatList/SectionList
   - 设置 keyExtractor
   - 使用 getItemLayout

2. **图片优化**：
   - 使用合适尺寸
   - 缓存策略
   - 懒加载

3. **内存优化**：
   - 及时清理监听器
   - 避免内存泄漏
   - 使用 PureComponent

4. **Bridge 优化**：
   - 减少 JS ↔ Native 通信
   - 批量处理
   - 使用新架构

### 18.5 最佳实践

**Q: React Native 开发最佳实践？**

**A:**

1. **代码组织**：
   - 功能模块化
   - 组件复用
   - 清晰的目录结构

2. **状态管理**：
   - 选择合适的方案
   - Redux/MobX/Zustand

3. **性能优化**：
   - 使用 memo/useMemo
   - 虚拟列表
   - 懒加载

4. **测试**：
   - 单元测试
   - 组件测试
   - E2E 测试

---

## 总结

### React Native 核心要点

1. **跨平台**：Learn Once, Write Anywhere
2. **原生组件**：真正的原生 UI
3. **JavaScript**：熟悉的语言和生态
4. **热重载**：快速迭代
5. **Bridge 机制**：JS ↔ Native 通信

### 适用场景

- ✅ 已有 React 经验的团队
- ✅ 需要原生 UI 外观
- ✅ 快速迭代的项目
- ✅ 复用 Web 代码

### 学习建议

1. **基础阶段**：JavaScript + React + 核心组件
2. **进阶阶段**：导航 + 状态管理 + 网络请求
3. **高级阶段**：原生模块 + 性能优化 + 新架构
4. **实战阶段**：完整项目开发

---

**文档版本**：v1.0  
**更新时间**：2026-03-10  
**适用版本**：React Native 0.73+
