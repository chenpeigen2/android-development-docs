# lib_hissug 模块架构详解

> 历史 & 搜索建议（History & Suggestions），百度APP搜索主入口组件，当前版本 **50.2.10**

---

## 1. 模块概述

lib_hissug 是百度APP的核心搜索体验模块，用户点击搜索框后进入输入态时展示的页面。PV以亿为单位，搜索用户启动后第一时间使用，承载着提升搜索渗透率、DAU、PV的重要目标。

- **仓库路径**: `repos/business/components/lib_hissug`
- **Maven坐标**: `com.baidu.searchbox.hissug`
- **主控类**: `HissugFrame`

页面根据是否有 query 分为两种效果：
- **无 query → His页面**：包含推荐内容
- **有 query → Sug页面**：搜索建议结果

---

## 2. 模块目录结构

```
lib_hissug/
├── lib_hissug_interface/       # 接口定义、契约、数据模型
├── lib_hissug_frame/           # 主控制器/编排层（HissugFrame）
├── lib_hissug_impl/            # 业务逻辑实现
├── lib_hissug_data/            # 数据管理、网络请求、本地存储
├── lib_hissug_view/            # UI组件和自定义View
├── lib_hot_search/             # 热搜功能
├── lib_hot_topic/              # 热议话题功能
├── resources/                  # 资源包和配置
│   ├── duner_above_box_bottom/
│   ├── duner_above_box_colorful_bottom/
│   ├── duner_above_box_colorful_top/
│   ├── duner_above_box_top/
│   ├── duner_at_box_colorful_top/
│   └── duner_at_box_top/
├── CHANGELOG.md
├── CLAUDE.md
├── README.md
└── version.properties          # 版本号: 50.2.10
```

**源文件统计**: 约 1,725 个 Kotlin/Java 源文件

---

## 3. 核心模块说明

### 3.1 lib_hissug_interface — 接口层

| 职责 | 说明 |
|------|------|
| 接口定义 | `ISearchFrame` 等核心接口 |
| 数据模型 | `com.baidu.searchbox.hissug.searchable.bean` 下的数据类 |
| 契约声明 | 模块间通信的接口契约 |

**关键路径**: `lib_hissug_interface/src/main/java/com/baidu/searchbox/frame/`

### 3.2 lib_hissug_frame — 控制层

| 职责 | 说明 |
|------|------|
| 主控类 | `HissugFrame` — 编排整个搜索建议体验 |
| 状态管理 | 搜索模式状态机（FSM） |
| 数据编排 | 推荐数据管理、UBC埋点 |

**关键路径**: `lib_hissug_frame/src/main/java/com/baidu/searchbox/hissug/`

### 3.3 lib_hissug_impl — 实现层

| 职责 | 说明 |
|------|------|
| 业务逻辑 | 搜索建议的具体业务实现 |

### 3.4 lib_hissug_data — 数据层

| 职责 | 说明 |
|------|------|
| 数据获取 | `BoxDataFetcher` 数据获取逻辑 |
| 网络请求 | HTTP管理和OKHttp集成 |
| 本地存储 | 搜索历史本地缓存 |
| 数据解析 | JSON解析（依赖nacomp） |

**关键路径**: `lib_hissug_data/src/main/java/com/baidu/searchbox/hissug/data/`

### 3.5 lib_hissug_view — 视图层

| 职责 | 说明 |
|------|------|
| 自定义View | 搜索框、建议列表等UI组件 |
| 主题适配 | 夜间模式、字号适配 |

**关键路径**: `lib_hissug_view/src/main/java/com/baidu/searchbox/hissug/widget/`

### 3.6 lib_hot_search / lib_hot_topic — 扩展功能

| 模块 | 功能 |
|------|------|
| lib_hot_search | 热搜榜功能 |
| lib_hot_topic | 热议话题功能 |

---

## 4. 功能模块详解

### 4.1 搜索历史（His）
- 普通历史
- 图片历史
- 图文历史
- 小程序直达历史
- 常搜

### 4.2 搜索建议（Sug）
- **通用Sug**: 根据用户输入的文字内容进行策略匹配纯文本结果
- **特型Sug**: 根据用户输入的文字内容进行策略生成特型结果，包含图片、icon、详细信息等

### 4.3 搜索推荐（Rec）
- **搜索发现**: 依据用户搜索、浏览行为推荐
- **框下推荐**: 依据用户结果页回退行为推荐
- **搜索榜单**: 热搜榜、小说榜等

### 4.4 搜索运营
- **Banner**: 特定日期范围下发图片运营位

### 4.5 用户体验
- 反馈机制: His反馈、Sug反馈、推荐反馈

---

## 5. 构建配置

### 5.1 Gradle 构建
```bash
# 构建所有模块
cd .. && ./gradlew :business:components:lib_hissug:build

# 构建指定模块
cd .. && ./gradlew :business:components:lib_hissug:lib_hissug_frame:build

# 清理构建
cd .. && ./gradlew :business:components:lib_hissug:clean
```

### 5.2 测试
```bash
# 单元测试
cd .. && ./gradlew :business:components:lib_hissug:test

# 集成测试
cd .. && ./gradlew :business:components:lib_hissug:connectedAndroidTest
```

### 5.3 构建特征
- **插件**: `com.android.library` + Kotlin支持
- **Lint**: 警告视为错误（严格质量控制）
- **混淆**: 自定义ProGuard规则
- **测试框架**: Robolectric

---

## 6. NAComp 框架集成

> **NAComp 完整使用指南见**: [NAComp_框架使用指南.md](./NAComp_框架使用指南.md)

**NAComp**（搜索NA业务基础模块）是百度内部的核心架构框架，提供 MVVM组件化、FSM状态机、RecyclerView委托适配器、夜间模式、字号适配等能力。

| 属性 | 值 |
|------|---|
| 仓库 | `ssh://icode.baidu.com:8235/baidu/baiduapp-android/nacomp` |
| Maven Group | `com.baidu.searchbox.nacomp` |
| 负责人 | 周航 <zhouhang01@baidu.com> |

### 6.1 lib_hissug 中的 NAComp 使用概况

| 子模块 | nacomp依赖 | 约 import 数 | 主要用途 |
|--------|-----------|-------------|---------|
| lib_hissug_frame | `core` + `extension` | ~150+ | FSM状态机、MVVM组件、UI扩展、JSON解析、RecyclerView |
| lib_hot_search | `core` + `extension` | ~40+ | BaseExtItemComponent/ViewModel、适配器、JSON解析 |
| lib_hissug_data | `extension` | ~20+ | JSON解析、CollectionUtils、Debug |
| lib_hissug_interface | `core` + `extension` | ~15+ | CollectionUtils、JSON解析 |

### 6.2 核心能力速览

| 能力 | 核心类 | 使用量 |
|------|--------|--------|
| MVVM列表项 | `BaseExtItemComponent` + `BaseExtItemViewModel` | ~20对 |
| RecyclerView容器 | `BaseExtRVComponent` + `DelegatorAdapter` | 7个 |
| 独立区域组件 | `BaseExtSlaveComponent` | ~23个 |
| FSM状态机 | `StateMachine` + State类 | 3台状态机 |
| JSON解析 | `JSONExtKt` | ~25+处 |
| 夜间模式 | `ResWrapper` + `INightMode` | ~20+处 |
| 字号适配 | `FontSizeInfo` + `IFontSize` | ~15+处 |
| 组件层级 | `IComponentGroup` | 嵌套组件 |

---

## 7. 模块依赖关系

```
lib_hissug_frame (主控制器)
    ├── lib_hissug_interface (接口契约)
    ├── lib_hissug_impl (业务实现)
    ├── lib_hissug_data (数据层)
    └── lib_hissug_view (视图层)

lib_hot_search (热搜)
    └── lib_hissug_interface

lib_hot_topic (热议)
    └── lib_hissug_interface
```

**外部关键依赖**:
- **NAComp**: 架构基础设施（FSM、MVVM、JSON解析、UI扩展）
- **Pyramid框架**: IOC容器和依赖注入
- **UBC**: 用户行为统计和分析
- **AndroidX & Kotlin**: 标准Android开发库
- **OKHttp**: 网络请求

---

## 8. 性能考量

- **TTI优化**: Time To Interactive优化已文档化，非常重要
- **懒加载**: FlowLayout使用懒加载
- **TabLayout性能**: 需要持续监控
- **搜索框延迟**: 首次获取His网络数据延迟到输入法弹出后

---

## 9. 关键类索引

| 类名 | 模块 | 职责 |
|------|------|------|
| `HissugFrame` | lib_hissug_frame | 主控制器，编排搜索建议体验 |
| `ISearchFrame` | lib_hissug_interface | 主搜索接口，外部集成用 |
| `BoxDataFetcher` | lib_hissug_data | 数据获取逻辑 |
| `SearchFrameComp` | lib_hissug_frame | 搜索框组件，含FSM状态机 |
| `HissugRecommendAndGuessDataManager` | lib_hissug_frame | 推荐数据管理 |
| `FloatSearchBoxLayout` | lib_hissug_frame | 浮动搜索框布局 |
| `AiToolPanelComp` | lib_hissug_frame | AI工具面板组件 |

---

## 10. 集成点

- 与主 `SearchFrame` 集成
- 与首页通信获取推荐内容
- 使用账号系统获取用户历史
- UBC 集成做用户行为分析
- 通过 nacomp 框架统一架构模式
