# Android 知识点补充建议

## 当前文档覆盖情况分析

### ✅ 已覆盖的核心知识点

#### 1. UI 与图形
- ✅ View 绘制流程（8层架构）
- ✅ 自定义 View（Drawable/Canvas/Paint）
- ✅ 事件分发机制（ViewGroup/View）
- ✅ 动画（帧/补间/属性动画）

#### 2. 四大组件
- ✅ Activity 启动流程
- ✅ 四大组件基础
- ✅ 后台任务（Service/JobScheduler/WorkManager）

#### 3. 核心机制
- ✅ Binder 机制（深度解析）
- ✅ Handler 机制
- ✅ 虚拟机（JVM/Dalvik/ART）
- ✅ ClassLoader
- ✅ Zygote 与 SystemServer

#### 4. 性能优化
- ✅ 性能优化（启动/UI/内存/电量/网络）
- ✅ 内存泄漏检测与优化
- ✅ ANR 详解
- ✅ Systrace 性能分析

#### 5. 架构与设计
- ✅ 架构模式演进（MVC/MVP/MVVM/MVI）
- ✅ AndroidX 核心库（Lifecycle/ViewModel/LiveData）

#### 6. 三方库
- ✅ 图片加载（Glide/Fresco）
- ✅ 网络请求（OkHttp/Retrofit）
- ✅ 数据存储（MMKV）
- ✅ 动画框架（PAG/Lottie）

#### 7. 工具与构建
- ✅ Gradle 与 AGP
- ✅ 屏幕适配

---

## ❌ 缺失的重要知识点

### 一、异步编程与响应式（必选）⭐⭐⭐⭐⭐

#### 1. Kotlin Coroutines 协程
**重要性**：面试必问，实际开发必备

**应包含内容**：
- 协程基础概念（CoroutineScope/Job/Deferred）
- 协程调度器（Dispatchers）
- 协程启动模式（launch/async）
- 协程上下文与作用域
- Flow 流式编程
- Channel 通道
- 协程异常处理
- 协程取消与超时
- 协程在 Android 中的应用
- 协程 vs RxJava 对比
- 面试常见问题（10+题）

#### 2. RxJava 响应式编程
**重要性**：复杂业务场景必备，面试高频

**应包含内容**：
- Observable/Single/Completable/Maybe
- 操作符详解（map/flatMap/filter/zip/merge等）
- 线程调度（Schedulers）
- 背压策略
- 错误处理
- RxBus 事件总线
- RxPermissions 权限
- RxJava 与 Retrofit 集成
- RxJava vs Coroutines 对比
- 内存泄漏防护
- 面试常见问题（15+题）

---

### 二、依赖注入（必选）⭐⭐⭐⭐⭐

#### 3. Hilt 依赖注入
**重要性**：Google 官方推荐，MVVM 必备

**应包含内容**：
- 依赖注入基础概念
- Hilt 核心注解（@HiltAndroidApp/@AndroidEntryPoint）
- @Inject 注入
- @Module 和 @Provides
- 组件与作用域（@Singleton/@ActivityScoped等）
- ViewModel 注入
- Fragment 注入
- 预定义限定符（@ApplicationContext/@ActivityContext）
- Entry Points
- 测试支持
- Hilt vs Dagger2 vs Koin 对比
- 面试常见问题（10+题）

#### 4. Koin（可选）
**重要性**：Kotlin 项目首选，轻量级

**应包含内容**：
- Koin 基础概念
- Module 定义
- 依赖注入
- ViewModel 注入
- Scope 作用域
- Koin vs Hilt 对比

---

### 三、数据持久化（必选）⭐⭐⭐⭐⭐

#### 5. Room 数据库
**重要性**：Google 官方推荐，SQLite 封装

**应包含内容**：
- Room 基础（Entity/Dao/Database）
- 主键与索引
- 关系映射（一对一/一对多/多对多）
- 类型转换器（TypeConverter）
- 数据库迁移（Migration）
- 协程支持
- RxJava 支持
- LiveData 支持
- 事务处理
- Room vs GreenDAO vs Realm
- 性能优化
- 面试常见问题（10+题）

#### 6. DataStore（可选）
**重要性**：SP 的官方替代品

**应包含内容**：
- Preferences DataStore
- Proto DataStore
- vs SharedPreferences 对比
- vs MMKV 对比

---

### 四、数据序列化（必选）⭐⭐⭐⭐

#### 7. Gson/Moshi JSON 解析
**重要性**：网络请求必备

**应包含内容**：
- Gson 基础使用
- 注解详解（@SerializedName/@Expose）
- 泛型处理（TypeToken）
- 自定义序列化器
- 复杂对象解析
- Moshi vs Gson 对比
- 性能优化
- 面试常见问题（5+题）

---

### 五、组件化与路由（推荐）⭐⭐⭐⭐

#### 8. ARouter 路由框架
**重要性**：组件化必备

**应包含内容**：
- 路由基础概念
- @Route 注解
- 路由跳转
- 参数传递
- 拦截器
- 依赖注入
- 路由原理（APT）
- 组件化架构设计
- ARouter vs DeepLink
- 面试常见问题（5+题）

---

### 六、Jetpack Compose（趋势）⭐⭐⭐⭐⭐

#### 9. Jetpack Compose 声明式 UI
**重要性**：Android UI 未来趋势

**应包含内容**：
- Compose 基础概念
- Composable 函数
- State 状态管理
- Composition/Recomposition
- Modifier 修饰符
- Layout 布局（Column/Row/Box）
- Material Design 组件
- 列表（LazyColumn/LazyRow）
- 动画
- 主题与样式
- ViewModel 集成
- 协程集成
- Navigation
- 与传统 View 互操作
- 性能优化
- 面试常见问题（10+题）

---

### 七、多媒体（推荐）⭐⭐⭐

#### 10. 音视频开发
**重要性**：特定场景必备

**应包含内容**：
- MediaPlayer/ExoPlayer
- 音频录制（MediaRecorder/AudioRecord）
- 视频录制
- CameraX 相机
- 图片选择（Matisse）
- 图片压缩（Luban）

---

### 八、安全与加固（推荐）⭐⭐⭐

#### 11. Android 安全
**重要性**：面试可能问到

**应包含内容**：
- 签名机制
- 混淆配置（ProGuard/R8）
- 反编译与加固
- HTTPS 与证书绑定
- 数据加密
- WebView 安全
- 面试常见问题（5+题）

---

### 九、插件化与热修复（进阶）⭐⭐⭐

#### 12. 插件化框架
**重要性**：进阶必备

**应包含内容**：
- 插件化原理
- ClassLoader 机制
- 资源加载
- 四大组件插件化
- 主流框架对比（RePlugin/Shadow等）

#### 13. 热修复框架
**重要性**：进阶必备

**应包含内容**：
- 热修复原理
- Class 替换
- 资源修复
- so 库修复
- 主流框架对比（Tinker/Sophix）

---

### 十、NDK 与 JNI（进阶）⭐⭐⭐

#### 14. NDK 开发
**重要性**：特定场景必备

**应包含内容**：
- JNI 基础
- NDK Build
- CMake 构建脚本
- native 方法调用
- 数据类型映射
- 异常处理
- 性能优化
- 面试常见问题（5+题）

---

### 十一、系统定制（进阶）⭐⭐⭐

#### 15. AOSP 系统开发
**重要性**：系统级开发必备

**应包含内容**：
- AOSP 源码下载与编译
- 系统架构
- SystemUI 定制
- Framework 定制
- 系统应用开发

---

## 📊 优先级排序

### 必选补充（⭐⭐⭐⭐⭐ 面试高频 90%+）

1. **Kotlin Coroutines** - 协程
2. **RxJava** - 响应式编程
3. **Hilt** - 依赖注入
4. **Room** - 数据库
5. **Jetpack Compose** - 声明式 UI（趋势）
6. **Gson/Moshi** - JSON 解析

### 推荐补充（⭐⭐⭐⭐ 面试中频 60%+）

1. **ARouter** - 路由框架
2. **Koin** - Kotlin 依赖注入
3. **DataStore** - 数据存储
4. **音视频开发** - MediaPlayer/ExoPlayer
5. **Android 安全** - 混淆/加固

### 可选补充（⭐⭐⭐ 面试低频 30%+）

1. **插件化框架** - RePlugin/Shadow
2. **热修复框架** - Tinker/Sophix
3. **NDK 开发** - JNI/CMake
4. **AOSP 系统开发** - 系统定制

---

## 🎯 建议补充顺序

### 第一批（最高优先级）
1. **Kotlin Coroutines 详解**（必选）
2. **RxJava 完全指南**（必选）
3. **Hilt 依赖注入**（必选）
4. **Room 数据库详解**（必选）

### 第二批（高优先级）
1. **Jetpack Compose 详解**（趋势）
2. **Gson/Moshi JSON 解析**（基础）
3. **ARouter 路由框架**（组件化）
4. **Android 安全详解**（面试）

### 第三批（中优先级）
1. **Koin 依赖注入**（Kotlin 项目）
2. **DataStore 数据存储**（官方推荐）
3. **音视频开发**（特定场景）
4. **插件化与热修复**（进阶）

### 第四批（低优先级）
1. **NDK 开发详解**（特定场景）
2. **AOSP 系统开发**（系统级）

---

## 📈 知识点覆盖率分析

### 当前覆盖率

| 类别 | 已覆盖 | 需补充 | 覆盖率 |
|------|--------|--------|--------|
| UI 与图形 | 4 | 1 (Compose) | 80% |
| 四大组件 | 2 | 2 (BroadcastReceiver/ContentProvider) | 50% |
| 核心机制 | 5 | 0 | 100% |
| 异步编程 | 0 | 2 (Coroutines/RxJava) | 0% |
| 依赖注入 | 0 | 2 (Hilt/Koin) | 0% |
| 数据持久化 | 1 | 2 (Room/DataStore) | 33% |
| 三方库 | 4 | 3 (RxJava/Hilt/ARouter) | 57% |
| 性能优化 | 4 | 0 | 100% |
| 架构设计 | 2 | 0 | 100% |
| **平均** | **22** | **12** | **65%** |

### 目标覆盖率

补充第一批后：**80%**  
补充第二批后：**90%**  
补充第三批后：**95%**

---

## 💡 总结

### 最紧迫需要补充的（按重要性）

1. **Kotlin Coroutines** - 现代异步编程标准
2. **RxJava** - 复杂业务必备
3. **Hilt** - Google 官方依赖注入
4. **Room** - 官方数据库方案
5. **Jetpack Compose** - UI 未来趋势

### 建议

- 优先补充异步编程和依赖注入（面试必问）
- 其次补充数据持久化和 Compose（实际开发必备）
- 最后补充插件化、热修复等进阶内容

补充完这些知识点后，文档集将覆盖 Android 开发的完整知识体系，适合从初级到高级的所有开发者！
