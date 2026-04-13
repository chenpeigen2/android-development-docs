# NAComp 框架使用指南 — 搜索NA业务基础模块

> 百度APP搜索业务核心架构框架，提供 MVVM组件化、FSM状态机、RecyclerView委托适配器、夜间模式、字号适配等能力

---

## 1. 框架概述

| 属性 | 值 |
|------|---|
| 仓库 | `ssh://icode.baidu.com:8235/baidu/baiduapp-android/nacomp` |
| Maven Group | `com.baidu.searchbox.nacomp` |
| 负责人 | 周航 <zhouhang01@baidu.com> |
| 设计理念 | 组件化 + MVVM + FSM + 泛型类型安全 |

### 1.1 子模块划分

| 子模块 | 职责 |
|--------|------|
| **lib-nacomp-core** | 核心框架 — FSM状态机、MVVM架构、RecyclerView组件、工具类 |
| **lib-nacomp-extension** | 扩展库 — JSON解析、View扩展、PullToRefresh、夜间模式、字号适配、生命周期控制 |
| **lib-nacomp-bee-compat** | BEE兼容层 |

### 1.2 包结构

```
com.baidu.searchbox.nacomp/
├── fsm/                           # 有限状态机
│   ├── StateMachine<T>            # 状态机核心类
│   └── @State                     # 状态标记注解
├── mvvm/                          # MVVM架构
│   ├── IComponent                 # 组件接口
│   ├── IComponentGroup            # 组件组接口（包含子组件）
│   └── impl/
│       ├── BaseViewModel          # ViewModel基类
│       └── ViewModelProviders     # ViewModel工厂
├── recycler/                      # RecyclerView框架
│   ├── base/item/
│   │   └── ItemAdapter<M, C>      # 单类型适配器
│   └── delegate/
│       ├── DelegatorAdapter       # 多类型委托适配器
│       └── IAdapterData           # 适配器数据接口
├── util/                          # 工具类
│   ├── UniqueId                   # 唯一标识符
│   └── CollectionUtils            # 集合工具
└── extension/
    ├── base/
    │   ├── BaseExtItemComponent<M, VM>    # 列表项组件基类
    │   ├── BaseExtItemViewModel<M>        # 列表项ViewModel基类
    │   ├── BaseExtRVComponent             # RecyclerView容器组件
    │   └── BaseExtSlaveComponent<VM>      # 子组件基类
    ├── util/
    │   ├── JSONExtKt              # JSON扩展工具
    │   ├── ViewExKt               # View扩展工具
    │   └── RecyclerViewHelper     # RecyclerView工具
    ├── fontsize/
    │   ├── IFontSize              # 字号适配接口
    │   └── FontSizeInfo           # 字号信息
    ├── nightmode/
    │   ├── INightMode             # 夜间模式接口
    │   └── ResWrapper             # 资源包装器
    ├── lifecycle/
    │   ├── CeilingChildLifecycleOwner  # 带上限的子生命周期
    │   └── CeilingLifecycleOwner       # 可配置上限的生命周期
    ├── widget/
    │   ├── ThrottleClickListener       # 防抖点击监听
    │   ├── PullToRefreshRecyclerView   # 下拉刷新RecyclerView
    │   ├── PtrAdapter                  # 下拉刷新适配器
    │   ├── GridSpaceItemDecoration     # 网格间距装饰
    │   └── LifecyclePagerAdapter       # 生命周期感知PagerAdapter
    ├── viewopt/
    │   ├── ViewPool                # View复用池
    │   ├── ViewSource              # View来源接口
    │   ├── PooledViewSource        # 池化View来源
    │   └── NewSpawnViewSource      # 新建View来源
    ├── item/anchor/
    │   ├── AnchorAdapter           # 锚点适配器
    │   └── AnchorData              # 锚点数据
    └── debug/
        ├── DebugExtConfig          # 调试配置
        └── createAbControlDebugItem # AB测试调试项
```

---

## 2. 整体架构设计图

### 2.1 模块依赖架构

```
┌─────────────────────────────────────────────────────────────────┐
│                       业务模块层 (lib_hissug)                    │
│                                                                 │
│  lib_hissug_frame    lib_hot_search    lib_hissug_data          │
│  lib_hissug_impl     lib_hissug_view   lib_hissug_interface     │
│  lib_hot_topic                                                   │
├────────────────────────┬────────────────────────────────────────┤
│                        │                                        │
│  ┌─────────────────────▼──────────────────────┐                 │
│  │         lib-nacomp-extension (扩展层)        │                 │
│  │                                             │                 │
│  │  ┌──────────────┐  ┌─────────────────────┐ │                 │
│  │  │  base/        │  │  util/              │ │                 │
│  │  │  BaseExtSlave │  │  JSONExtKt          │ │                 │
│  │  │  BaseExtRV    │  │  ViewExKt           │ │                 │
│  │  │  BaseExtItem  │  │  RecyclerViewHelper │ │                 │
│  │  │  BaseExtItemVM│  │                     │ │                 │
│  │  └──────────────┘  ├─────────────────────┤ │                 │
│  │                    │  nightmode/          │ │                 │
│  │  ┌──────────────┐  │  INightMode          │ │                 │
│  │  │  fontsize/    │  │  ResWrapper          │ │                 │
│  │  │  IFontSize    │  ├─────────────────────┤ │                 │
│  │  │  FontSizeInfo │  │  widget/            │ │                 │
│  │  └──────────────┘  │  PullToRefresh       │ │                 │
│  │                    │  ThrottleClick       │ │                 │
│  │  ┌──────────────┐  │  GridSpace           │ │                 │
│  │  │  lifecycle/   │  ├─────────────────────┤ │                 │
│  │  │  CeilingChild │  │  viewopt/           │ │                 │
│  │  │  CeilingOwner │  │  ViewPool           │ │                 │
│  │  └──────────────┘  │  ViewSource          │ │                 │
│  │                    ├─────────────────────┤ │                 │
│  │  ┌──────────────┐  │  item/anchor/       │ │                 │
│  │  │  debug/       │  │  AnchorAdapter      │ │                 │
│  │  │  DebugExtConf │  │  AnchorData         │ │                 │
│  │  └──────────────┘  └─────────────────────┘ │                 │
│  └──────────────────────────┬──────────────────┘                 │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────┐                │
│  │          lib-nacomp-core (核心层)             │                │
│  │                                              │                │
│  │  ┌────────────┐ ┌──────────────┐ ┌────────┐ │                │
│  │  │   fsm/     │ │    mvvm/     │ │ util/  │ │                │
│  │  │            │ │              │ │        │ │                │
│  │  │ StateMachine│ │ IComponent   │ │UniqueId│ │                │
│  │  │ State<T>   │ │ IComponentGrp│ │Collectn│ │                │
│  │  │            │ │ BaseViewModel│ │Utils   │ │                │
│  │  │            │ │ ViewModelProv│ │        │ │                │
│  │  └────────────┘ └──────────────┘ └────────┘ │                │
│  │  ┌──────────────────────────────────────────┐│                │
│  │  │              recycler/                    ││                │
│  │  │  DelegatorAdapter  ItemAdapter<M,C>       ││                │
│  │  │  IAdapterData                              ││                │
│  │  └──────────────────────────────────────────┘│                │
│  └──────────────────────────────────────────────┘                │
│                                                                  │
│  ┌──────────────────────────────────────────────┐                │
│  │         lib-nacomp-bee-compat (兼容层)        │                │
│  │         BEE 框架兼容适配                       │                │
│  └──────────────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 MVVM 组件继承体系图

```
                         ┌──────────────┐
                         │  IComponent  │  (接口)
                         │  组件契约     │
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
           ┌────────┴────────┐    ┌─────────┴──────────┐
           │ IComponentGroup │    │ BaseExtSlaveComp<VM>│
           │ (组件组接口)     │    │ 子组件基类           │
           └─────────────────┘    └─────────┬──────────┘
                                           │
                    ┌──────────────────────┐┼─────────────────────┐
                    │                      │                      │
         ┌──────────┴──────────┐  ┌────────┴─────────┐  ┌────────┴──────────┐
         │ BaseExtRVComp<VM>   │  │ BaseExtItemComp  │  │  直接继承          │
         │ RecyclerView容器    │  │    <M, VM>       │  │  (页面级组件)       │
         └──────────┬──────────┘  │ 列表项组件       │  └────────┬──────────┘
                    │              └────────┬─────────┘           │
          ┌─────────┼─────────┐           │              ┌───────┼────────┐
          │         │         │           │              │       │        │
   ┌──────┴──┐ ┌───┴───┐ ┌──┴─────┐ ┌───┴────┐   ┌─────┴─┐ ┌───┴──┐ ┌──┴────────┐
   │AiTool  │ │HotSrch│ │Upload  │ │各种    │   │Search │ │SugPg │ │HistoryPg  │
   │Panel   │ │Page   │ │File    │ │ItemComp│   │Frame  │ │      │ │            │
   │Comp    │ │Comp   │ │Comp    │ │        │   │Comp   │ │Comp  │ │Comp        │
   └────────┘ └───────┘ └────────┘ └────────┘   └───────┘ └──────┘ └───────────┘
```

### 2.3 ViewModel 继承体系图

```
                      ┌──────────────────┐
                      │  BaseViewModel   │
                      │  (nacomp.mvvm)   │
                      └────────┬─────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                   │
  ┌─────────┴──────────┐ ┌────┴─────────────┐ ┌───┴──────────────┐
  │BaseExtItemViewModel│ │  页面级 ViewModel │ │  页面级 ViewModel │
  │      <M>           │ │  (无泛型Model)    │ │  (无泛型Model)    │
  │  列表项VM           │ └──────────────────┘ └──────────────────┘
  └─────────┬──────────┘
            │
   ┌────────┼────────┬──────────┬──────────┐
   │        │        │          │          │
┌──┴──┐ ┌──┴───┐ ┌──┴────┐ ┌───┴───┐ ┌───┴───┐
│Title│ │Text  │ │History│ │AIGC   │ │Upload │
│VM   │ │VM    │ │VM     │ │TplVM  │ │DocVM  │
└─────┘ └──────┘ └───────┘ └───────┘ └───────┘
```

### 2.4 适配器体系图 — Delegator 委托模式

```
                     ┌─────────────────────┐
                     │  DelegatorAdapter   │
                     │  多类型委托适配器     │
                     │                     │
                     │  put(ItemAdapter)   │ ← 注册类型委托
                     │  setItems(List)     │ ← 设置数据
                     └──────────┬──────────┘
                                │ 委托分发
              ┌─────────────────┼─────────────────┐
              │                 │                   │
     ┌────────┴───────┐ ┌──────┴────────┐  ┌──────┴────────┐
     │ ItemAdapter    │ │ ItemAdapter   │  │ ItemAdapter   │
     │   <Model, Comp>│ │  <Model, Comp>│  │  <Model, Comp>│
     │               │ │               │  │               │
     │  onCreateViewHolder() → 创建 Comp│  │               │
     │  getType() → UniqueId         │  │               │
     └───────┬───────┘ └───────┬───────┘  └───────┬───────┘
             │                 │                   │
     ┌───────┴───────┐ ┌──────┴──────┐    ┌───────┴──────┐
     │  Model:       │ │  Model:     │    │  Model:      │
     │  IAdapterData │ │  IAdapterData│   │  IAdapterData│
     │  getType()→   │ │  getType()→ │    │  getType()→  │
     │  UniqueId     │ │  UniqueId   │    │  UniqueId    │
     └───────────────┘ └─────────────┘    └──────────────┘


数据流转:
   IAdapterData.getType() → UniqueId
         ↓
   DelegatorAdapter 查找已注册的 ItemAdapter
         ↓
   ItemAdapter.onCreateViewHolder() → 创建 BaseExtItemComponent
         ↓
   Component.onBindViewModel() → ViewModel.setModel() → 更新UI
```

### 2.5 FSM 状态机架构图

```
   ┌──────────────────────────────────────────────────────────────┐
   │                     StateMachine<T>                          │
   │                   T = 宿主组件类型                            │
   │                                                              │
   │   ┌─────────┐    changeState()    ┌──────────────┐          │
   │   │ 当前状态 │ ──────────────────→ │   目标状态    │          │
   │   │ current │                     │              │          │
   │   └────┬────┘                     └──────────────┘          │
   │        │                                                     │
   │        │ handleMessage(msg)                                   │
   │        ↓                                                     │
   │   ┌────────────────────┐                                     │
   │   │ State<T>.handleMsg │                                     │
   │   │ return true/false  │                                     │
   │   └────────────────────┘                                     │
   └──────────────────────────────────────────────────────────────┘

                   State<T> 继承体系
                   (T = AISearchBoxComp)

                    ┌──────────────┐
                    │  State<T>    │
                    │  (nacomp.fsm)│
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │ BaseBoxState │ (抽象)
                    │  enter()     │
                    │  exit()      │
                    │  onMessage() │
                    └──────┬───────┘
              ┌────────────┼────────────┐────────────┐
              │            │            │            │
     ┌────────┴───┐ ┌─────┴────┐ ┌────┴───────┐ ┌──┴──────────┐
     │NormalBox   │ │ImageBox  │ │DocumentBox │ │AiToolPanel  │
     │State       │ │State     │ │State       │ │State        │
     │            │ │          │ │            │ │  ┌────────┐ │
     │ 普通搜索框  │ │ 图片搜索  │ │ 文档搜索    │ │  │嵌套FSM │ │
     └────────────┘ └──────────┘ └────────────┘ │  └────────┘ │
                                                  └────────────┘

状态转换流:
  NormalBox ──→ ImageBox      (用户上传图片)
  NormalBox ──→ DocumentBox   (用户上传文档)
  NormalBox ──→ AiToolPanel   (用户选择AI工具)
  ImageBox  ──→ NormalBox     (关闭)
  DocumentBox→ NormalBox      (关闭)
  AiToolPanel→ NormalBox      (关闭AI工具)
```

### 2.6 组件生命周期 & 事件传播架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HissugFrame (主控制器)                       │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    SearchFrameComp                            │  │
│  │              BaseExtSlaveComponent<SearchFrameVM>             │  │
│  │                                                               │  │
│  │   ┌───────────────────────────────────────────────────────┐   │  │
│  │   │              AISearchBoxComp                          │   │  │
│  │   │         BaseExtSlaveComponent<AISearchBoxVM>          │   │  │
│  │   │                                                       │   │  │
│  │   │   fsm: StateMachine<AISearchBoxComp>                  │   │  │
│  │   │   currentState: State<AISearchBoxComp>                │   │  │
│  │   └───────────────────────────────────────────────────────┘   │  │
│  │                                                               │  │
│  │   ┌──────────────────┐    ┌──────────────────────────────┐    │  │
│  │   │  SugPageComp     │    │  HistoryPageComp             │    │  │
│  │   │  SlaveComp<VM>   │    │  SlaveComp<HistoryPageVM>    │    │  │
│  │   │                  │    │                               │    │  │
│  │   │  (Sug建议页面)    │    │  ┌────────────────────────┐ │    │  │
│  │   └──────────────────┘    │  │ ListIntegrationComp    │ │    │  │
│  │                           │  │ BaseExtRVComp<VM>      │ │    │  │
│  │   ┌──────────────────┐    │  │                        │ │    │  │
│  │   │  RecommendComp   │    │  │ DelegatorAdapter       │ │    │  │
│  │   │  SlaveComp<VM>   │    │  │  ├─ ContentItemAdapter │ │    │  │
│  │   └──────────────────┘    │  │  ├─ AnchorItemAdapter  │ │    │  │
│  │                           │  │  ├─ FeedBackItemAdapter│ │    │  │
│  │   ┌──────────────────┐    │  │  ├─ IncognitoTipAdapt  │ │    │  │
│  │   │  AiToolPanelComp │    │  │  └─ HistoryAdapterAdapt│ │    │  │
│  │   │  BaseExtRVComp   │    │  └────────────────────────┘ │    │  │
│  │   │                  │    └──────────────────────────────┘    │  │
│  │   │ DelegatorAdapter│                                        │  │
│  │   │  ├─ Subtitle   │    ┌──────────────────────────────┐     │  │
│  │   │  ├─ WordList   │    │  ClassicHistoryPageComp      │     │  │
│  │   │  ├─ ImageList  │    │  SlaveComp<ClassicVM>        │     │  │
│  │   │  ├─ SwitchList │    │                               │     │  │
│  │   │  └─ Translate  │    │  HistoryListComp (RVComp)     │     │  │
│  │   └──────────────────┘    │   DelegatorAdapter           │     │  │
│  │                           │    ├─ HistoryItemAdapter     │     │  │
│  │   ┌──────────────────┐    │    ├─ HisTitleItemAdapter   │     │  │
│  │   │  BottomBarComp   │    │    ├─ MoreHisItemAdapter    │     │  │
│  │   │  SlaveComp<VM>   │    │    └─ FeedBackItemAdapter   │     │  │
│  │   └──────────────────┘    └──────────────────────────────┘     │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘


事件传播方向:
  ──→ 夜间模式 / 字号变更: 自顶向下 (通过 IComponentGroup 自动传播)
  ──→ 用户交互事件: 自底向上 (通过接口回调和 LiveData 观察)
  ←→ 模式切换: 水平传播 (通过 FSM 状态机)
```

### 2.7 数据流架构图

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   网络层      │     │    数据解析层     │     │    数据模型层      │
│  (OKHttp)    │     │  (JSONExtKt)    │     │  (IAdapterData)  │
│              │     │                 │     │                  │
│  JSONObject  │────→│  optStringIgnore│────→│  TitleItemModel  │
│  JSONArray   │     │  mapObjectNotNull│    │  HistoryItemData │
│              │     │  mapStringNotNull│    │  ContentItemData │
│              │     │  toStringStringMap│   │  ...             │
└─────────────┘     └─────────────────┘     └────────┬─────────┘
                                                       │
                                                       │ setItems()
                                                       ↓
                                             ┌──────────────────┐
                                             │ DelegatorAdapter │
                                             │                  │
                                             │  根据 UniqueId   │
                                             │  分发到对应的     │
                                             │  ItemAdapter     │
                                             └────────┬─────────┘
                                                      │
                                    ┌─────────────────┼─────────────────┐
                                    │                 │                  │
                              ┌─────┴──────┐   ┌─────┴──────┐    ┌─────┴──────┐
                              │ItemAdapter │   │ItemAdapter │    │ItemAdapter │
                              │  .onBind() │   │  .onBind() │    │  .onBind() │
                              └─────┬──────┘   └─────┬──────┘    └─────┬──────┘
                                    │                 │                  │
                              ┌─────┴──────┐   ┌─────┴──────┐    ┌─────┴──────┐
                              │Component   │   │Component   │    │Component   │
                              │  .onBindVM │   │  .onBindVM │    │  .onBindVM │
                              └─────┬──────┘   └─────┬──────┘    └─────┬──────┘
                                    │                 │                  │
                              ┌─────┴──────┐   ┌─────┴──────┐    ┌─────┴──────┐
                              │ViewModel   │   │ViewModel   │    │ViewModel   │
                              │  .setModel │   │  .setModel │    │  .setModel │
                              │  LiveData  │   │  LiveData  │    │  LiveData  │
                              │  → UI更新  │   │  → UI更新  │    │  → UI更新  │
                              └────────────┘   └────────────┘    └────────────┘
```

### 2.8 lib_hissug 中 NAComp 使用全景图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         lib_hissug 模块                                  │
│                                                                         │
│  ┌─── MVVM组件 ───────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  BaseExtSlaveComponent (23个)          BaseExtRVComponent (7个)     │ │
│  │  ┌────────────────────────────────┐    ┌────────────────────────┐  │ │
│  │  │ SearchFrameComp    (搜索框)    │    │ AiToolPanelComp (AI面板)│  │ │
│  │  │ AISearchBoxComp   (AI搜索框)   │    │ HotSearchPageComp(热搜) │  │ │
│  │  │ SugPageComp       (建议页)     │    │ BoardTabComp   (榜单)   │  │ │
│  │  │ HistoryPageComp   (历史页)     │    │ UploadFileComp (上传)   │  │ │
│  │  │ ClassicHistoryPg  (经典历史)   │    │ TplCardListComp(模板)   │  │ │
│  │  │ RecommendComp     (推荐)       │    │ HistoryListComp(历史)   │  │ │
│  │  │ CreationToolPage  (创作工具)   │    │ ListIntegrationComp    │  │ │
│  │  │ DiffusionBallComp (扩散球)     │    └────────────────────────┘  │ │
│  │  │ ColorfulAnimComp  (彩色动画)   │                                 │ │
│  │  │ GlowBoxBorderComp (发光边框)   │    BaseExtItemComponent (20个) │ │
│  │  │ ChangeModeBarComp (模式切换)   │    ┌────────────────────────┐  │ │
│  │  │ AiToolMenuBarComp (AI菜单栏)   │    │ TitleItemComp  (标题)  │  │ │
│  │  │ MultiModeKeyBarComp(键盘栏)    │    │ TextStyleItemComp     │  │ │
│  │  │ SearchServiceComp (搜索服务)   │    │ ImageStyleItemComp    │  │ │
│  │  │ ...更多(23个)                  │    │ HistoryItemComp       │  │ │
│  │  └────────────────────────────────┘    │ AIGCTplItemComp       │  │ │
│  │                                        │ UploadImageItemComp   │  │ │
│  │                                        │ UploadDocumentItemComp│  │ │
│  │                                        │ AnchorItemComp        │  │ │
│  │                                        │ ...更多(20个)         │  │ │
│  │                                        └────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌─── FSM状态机 ──────────────────────────────────────────────────────┐ │
│  │  SearchFrameComp.searchModeFsm (搜索模式)                          │ │
│  │  AISearchBoxComp.fsm           (搜索框状态)                        │ │
│  │  AIToolPanelState.fsm          (AI工具子状态)                      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌─── 工具使用 ───────────────────────────────────────────────────────┐ │
│  │  JSONExtKt       ~25+处   │  ResWrapper      ~20+处               │ │
│  │  FontSizeInfo    ~15+处   │  UniqueId        ~25+处               │ │
│  │  CollectionUtils ~4处     │  ThrottleClickListener ~2处            │ │
│  │  ViewExKt        ~5处     │  CeilingChildLifecycleOwner ~5处      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 引入依赖

### 2.1 build.gradle 声明

```gradle
// 核心框架（FSM、MVVM、RecyclerView、工具类）
implementation deps.business.nacomp.core

// 扩展库（JSON解析、View扩展、夜间模式、字号适配、下拉刷新等）
implementation deps.business.nacomp.extension
```

### 2.2 依赖选择指南

| 需求 | 引入的模块 |
|------|-----------|
| 仅使用 `CollectionUtils`、`UniqueId` | `nacomp.core` |
| 使用 `BaseExtItemComponent` 等 MVVM 组件 | `nacomp.core` + `nacomp.extension` |
| 使用 `JSONExtKt` 做数据解析 | `nacomp.extension` |
| 使用 `ResWrapper` 做夜间模式 | `nacomp.extension` |
| 使用 `StateMachine` | `nacomp.core` |
| 使用 `DelegatorAdapter` | `nacomp.core` + `nacomp.extension` |

---

## 4. 核心架构 — 组件继承体系

### 4.1 继承关系图

```
IComponent (接口)
└── IComponentGroup (接口，可包含子组件)

BaseViewModel (ViewModel基类)
├── BaseExtItemViewModel<M> (列表项ViewModel)
└── 自定义 ViewModel (如 SearchFrameViewModel)

BaseExtSlaveComponent<VM> (子组件基类，实现 IComponent)
├── BaseExtRVComponent (RecyclerView容器组件)
│   └── AiToolPanelComp, HotSearchPageComp, UploadFileComp, ...
├── BaseExtItemComponent<M, VM> (列表项组件)
│   └── TitleItemComp, ImageStyleItemComp, HistoryItemComp, ...
└── 其他 Slave 组件
    └── SearchFrameComp, SugPageComp, HistoryPageComp, ...
```

### 4.2 四大组件基类对比

| 基类 | 泛型 | 典型场景 | 核心回调 |
|------|------|---------|---------|
| **BaseExtSlaveComponent\<VM\>** | 1个泛型(VM) | 独立页面/区域组件 | `onCreateViewModel()`, `onBindViewModel()` |
| **BaseExtRVComponent** | 继承自Slave | 包含RecyclerView的容器 | `onRegisterDelegates()` 注册多类型 |
| **BaseExtItemComponent\<M, VM\>** | 2个泛型(M+VM) | RecyclerView的单个列表项 | `onCreateViewModel()`, `onBindViewModel()` |
| **BaseExtItemViewModel\<M\>** | 1个泛型(M) | 列表项的数据持有 | `setModel()`, LiveData属性 |

---

## 5. 使用指南 — MVVM 组件开发

### 5.1 开发一个列表项组件（完整流程）

#### Step 1: 定义数据模型（实现 IAdapterData）

```kotlin
class TitleItemModel(
    val title: String,
    val iconUrl: String = "",
    val iconRes: Int = 0
) : IAdapterData {

    companion object {
        // 每个类型用 UniqueId 生成唯一标识
        val TYPE: UniqueId = UniqueId.gen("TitleItemModel")
    }

    override fun getType(): UniqueId = TYPE
}
```

#### Step 2: 定义 ViewModel

```kotlin
class TitleItemVM : BaseExtItemViewModel<TitleItemModel>() {

    val title = MutableLiveData<String>()
    val iconUrl = MutableLiveData<String>()
    val iconRes = MutableLiveData<Int>()

    override fun setModel(model: TitleItemModel) {
        super.setModel(model)
        title.value = model.title
        iconUrl.value = model.iconUrl
        iconRes.value = model.iconRes
    }
}
```

#### Step 3: 定义 ItemAdapter（桥接 Model、View、Component）

```kotlin
class TitleItemAdapter(private val owner: LifecycleOwner) :
    ItemAdapter<TitleItemModel, TitleItemComp>(owner) {

    override fun onCreateViewHolder(parent: ViewGroup): TitleItemComp {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_hot_search_title, parent, false)
        return TitleItemComp(owner, view)
    }

    override fun getType(): UniqueId = TitleItemModel.TYPE
}
```

#### Step 4: 定义 Component（处理视图逻辑）

```kotlin
class TitleItemComp(owner: LifecycleOwner, view: View) :
    BaseExtItemComponent<TitleItemModel, TitleItemVM>(owner, view) {

    private val tvTitle: TextView = view.findViewById(R.id.tv_title)
    private val ivIcon: ImageView = view.findViewById(R.id.iv_icon)

    override fun onCreateViewModel(): TitleItemVM = TitleItemVM()

    override fun onBindViewModel(viewModel: TitleItemVM, owner: LifecycleOwner) {
        super.onBindViewModel(viewModel, owner)
        viewModel.title.observe(owner) { tvTitle.text = it }
        viewModel.iconUrl.observe(owner) { url ->
            // 加载图片
        }
    }

    override fun onNightModeChange(isNightMode: Boolean) {
        ResWrapper.setTextColor(tvTitle, UIUtils.getBlackTextColorResId())
    }

    override fun onFontSizeChange(info: FontSizeInfo) {
        info.updateTextSize(tvTitle, SizeType.FRAMEWORK)
    }
}
```

#### Step 5: 定义 RecyclerView 容器组件

```kotlin
class HotSearchPageComp(owner: LifecycleOwner, view: View) :
    BaseExtRVComponent(owner, view) {

    private val recyclerView: RecyclerView = view.findViewById(R.id.recycler_view)

    override fun onRegisterDelegates(delegator: DelegatorAdapter) {
        super.onRegisterDelegates(delegator)
        delegator.put(TitleItemAdapter(lifecycleOwner))
        delegator.put(TextStyleItemAdapter(lifecycleOwner))
        delegator.put(ImageStyleItemAdapter(lifecycleOwner))
        delegator.put(PhraseStyleItemAdapter(lifecycleOwner))
        delegator.put(ViewMoreItemAdapter(lifecycleOwner))
    }

    fun setData(items: List<IAdapterData>) {
        (recyclerView.adapter as? DelegatorAdapter)?.setItems(items)
    }
}
```

### 5.2 开发一个独立区域组件（Slave Component）

```kotlin
class SugPageComp(owner: LifecycleOwner, view: View) :
    BaseExtSlaveComponent<SugPageViewModel>(owner, view) {

    override fun onCreateViewModel(): SugPageViewModel {
        return ViewModelProviders.of(this).get(SugPageViewModel::class.java)
    }

    override fun onBindViewModel(viewModel: SugPageViewModel, owner: LifecycleOwner) {
        super.onBindViewModel(viewModel, owner)
        // 绑定数据
        viewModel.sugData.observe(owner) { data ->
            updateSugList(data)
        }
    }
}
```

### 5.3 组件层级 — IComponentGroup 使用

当一个列表项本身需要包含子组件时（如嵌套 RecyclerView），使用 `IComponentGroup`：

```kotlin
class HistoryAdapterComp(owner: LifecycleOwner, view: View) :
    BaseExtItemComponent<HistoryAdapterData, HistoryAdapterViewModel>(owner, view),
    IComponentGroup {

    private val children = mutableListOf<IComponent<*>>()

    private val childComp = run {
        // 创建子组件，使用 CeilingChildLifecycleOwner 控制生命周期上限
        val childLifecycle = CeilingChildLifecycleOwner(owner, Lifecycle.State.INITIALIZED)
        HistoryListComp(childLifecycle, view).apply {
            this@HistoryAdapterComp.add(this)
            setMaxLifecycle(Lifecycle.State.RESUMED)
        }
    }

    override fun add(component: IComponent<*>?) {
        if (component != null && !children.contains(component)) {
            children.add(component)
        }
    }

    override fun remove(component: IComponent<*>?) {
        component?.let { children.remove(it) }
    }

    override fun getChildren(): MutableList<IComponent<*>> = children.toMutableList()

    // 事件自动向下传播
    override fun onNightModeChange(isNightMode: Boolean) {
        children.forEach {
            if (it is INightMode) it.onNightModeChange(isNightMode)
        }
    }

    override fun onFontSizeChange(info: FontSizeInfo) {
        children.forEach {
            if (it is IFontSize) it.onFontSizeChange(info)
        }
    }
}
```

**事件传播模式** — 所有通用接口都遵循自动传播：

```kotlin
// 对任意接口事件，统一检查 IComponentGroup 并传播给子组件
if (component is IComponentGroup) {
    component.getChildren().forEach { child ->
        (child as? SomeInterface)?.someMethod()
    }
}
```

---

## 6. 使用指南 — FSM 状态机

### 6.1 核心概念

```
StateMachine<T>     — 状态机，T 是宿主类型
├── changeState()    — 切换状态
└── handleMessage()  — 分发消息给当前状态

State (基类)        — 状态基类
├── enter(owner)    — 进入状态时回调
├── exit(owner)     — 退出状态时回调
└── handleMsg(owner, msg) — 处理消息，返回 Boolean
```

### 6.2 完整使用示例

#### 定义状态

```kotlin
// 抽象基状态
abstract class BaseBoxState {

    // 状态进入
    open fun enter(owner: BaseBoxComp) {}

    // 状态退出
    open fun exit(owner: BaseBoxComp) {}

    // 处理消息
    open fun handleMsg(owner: BaseBoxComp, msg: Any?): Boolean = false

    // 状态转换方法
    open fun onEnterDocumentState(owner: BaseBoxComp) {}
    open fun onEnterImageState(owner: BaseBoxComp) {}
    open fun onEnterAiToolState(owner: BaseBoxComp, tool: AiTool) {}
}

// 具体状态 — 普通搜索框
class NormalBoxState : BaseBoxState() {
    override fun enter(owner: BaseBoxComp) {
        owner.showNormalBox()
    }

    override fun onEnterDocumentState(owner: BaseBoxComp) {
        owner.fsm.changeState(DocumentBoxState())
    }

    override fun onEnterImageState(owner: BaseBoxComp) {
        owner.fsm.changeState(ImageBoxState())
    }

    override fun onEnterAiToolState(owner: BaseBoxComp, tool: AiTool) {
        owner.fsm.changeState(AiToolPanelState(tool))
    }
}

// 具体状态 — 文档搜索
class DocumentBoxState : BaseBoxState() {
    override fun enter(owner: BaseBoxComp) {
        owner.showDocumentBox()
    }

    override fun handleMsg(owner: BaseBoxComp, msg: Any?): Boolean {
        return when (msg) {
            MSG_CLOSE -> {
                owner.fsm.changeState(NormalBoxState())
                true
            }
            else -> false
        }
    }
}
```

#### 在组件中使用状态机

```kotlin
class SearchFrameComp(owner: LifecycleOwner, view: View) :
    BaseExtSlaveComponent<SearchFrameViewModel>(owner, view) {

    // 创建状态机，this 作为宿主
    internal val searchModeFsm = StateMachine(this)

    init {
        // 设置初始状态
        searchModeFsm.changeState(NormalBoxState())
    }

    fun switchToDocumentMode() {
        // 通过消息驱动状态转换
        (searchModeFsm.currentState as? BaseBoxState)?.onEnterDocumentState(this)
    }

    fun switchToAiToolMode(tool: AiTool) {
        (searchModeFsm.currentState as? BaseBoxState)?.onEnterAiToolState(this, tool)
    }

    fun closeCurrentMode() {
        searchModeFsm.handleMessage(MSG_CLOSE)
    }
}
```

### 6.3 实际项目中的状态层级

```
搜索框状态层级:
BaseBoxState
├── NormalBoxState          # 普通搜索框
├── ImageBoxState           # 图片搜索模式
├── DocumentBoxState        # 文档搜索模式
└── AiToolPanelState        # AI工具面板
    ├── AiToolNoFileState   # 无文件上传
    ├── AiToolImageState    # 图片已上传
    └── AiToolDocumentState # 文档已上传
```

---

## 7. 使用指南 — RecyclerView 委托适配器

### 7.1 DelegatorAdapter 工作原理

```
DelegatorAdapter
├── put(ItemAdapter)         # 注册类型委托
├── setItems(List<IAdapterData>)  # 设置数据
└── 根据 IAdapterData.getType() 自动分发到对应的 ItemAdapter
```

### 7.2 多类型列表完整示例

```kotlin
// 1. 定义各种数据模型
data class TextItem(val text: String) : IAdapterData {
    companion object { val TYPE = UniqueId.gen("TextItem") }
    override fun getType() = TYPE
}

data class ImageItem(val url: String) : IAdapterData {
    companion object { val TYPE = UniqueId.gen("ImageItem") }
    override fun getType() = TYPE
}

data class BannerItem(val imgUrl: String) : IAdapterData {
    companion object { val TYPE = UniqueId.gen("BannerItem") }
    override fun getType() = TYPE
}

// 2. 在 RVComponent 中注册所有类型
class MyListComp(owner: LifecycleOwner, view: View) :
    BaseExtRVComponent(owner, view) {

    override fun onRegisterDelegates(delegator: DelegatorAdapter) {
        super.onRegisterDelegates(delegator)
        delegator.put(TextItemAdapter(lifecycleOwner))
        delegator.put(ImageItemAdapter(lifecycleOwner))
        delegator.put(BannerItemAdapter(lifecycleOwner))
    }
}

// 3. 混合数据直接 setItems
val items = listOf(
    TextItem("热搜榜"),
    ImageItem("https://xxx/1.jpg"),
    TextItem("更多热搜"),
    BannerItem("https://xxx/banner.png"),
    ImageItem("https://xxx/2.jpg")
)
(adapter as DelegatorAdapter).setItems(items)
```

### 7.3 lib_hissug 中的适配器一览

| 适配器 | 所属模块 | 用途 |
|--------|---------|------|
| `TitleItemAdapter` | lib_hot_search | 热搜标题 |
| `TextStyleItemAdapter` | lib_hot_search | 文字样式热搜项 |
| `ImageStyleItemAdapter` | lib_hot_search | 图片样式热搜项 |
| `ImageBtnStyleItemAdapter` | lib_hot_search | 图片按钮热搜项 |
| `PhraseStyleItemAdapter` | lib_hot_search | 短语样式热搜项 |
| `ViewMoreItemAdapter` | lib_hot_search | 查看更多 |
| `HistoryItemAdapter` | lib_hissug_frame | 搜索历史项 |
| `HisTitleItemAdapter` | lib_hissug_frame | 历史标题 |
| `MoreHisItemAdapter` | lib_hissug_frame | 更多历史 |
| `ContentItemAdapter` | lib_hissug_frame | 内容项 |
| `HisGuideAdapter` | lib_hissug_frame | 历史引导 |
| `UploadDocumentItemAdapter` | lib_hissug_frame | 文档上传项 |
| `AiToolTemplateItemAdapter` | lib_hissug_frame | AI工具模板项 |
| `AnchorItemAdapter` | lib_hissug_frame | 锚点项 |

---

## 8. 使用指南 — 工具类

### 8.1 JSONExtKt — 空安全 JSON 操作

**最高频使用的工具类**，所有 JSON 操作均不返回 null：

```kotlin
import com.baidu.searchbox.nacomp.extension.util.JSONExtKt

// 安全获取字符串（null → 默认值）
val token: String = JSONExtKt.optStringIgnoreNulls(jsonObj, "session_token", "")
val msg: String = JSONExtKt.optStringIgnoreNulls(jsonObj, "errmsg", "unknown")

// 安全获取字符串（null → null，不是空字符串）
val name: String? = JSONExtKt.optStringIgnoreNulls(jsonObj, "name")

// 列表 → JSONArray
val jsonArray: JSONArray = JSONExtKt.toJsonArray(list) { item -> item.toJson() }

// JSONArray → 非null对象列表（过滤null）
val items: List<Model> = JSONExtKt.mapObjectNotNull(jsonArray) { obj ->
    Model.fromJson(obj)
}

// JSONArray → 非null字符串列表（过滤null）
val names: List<String> = JSONExtKt.mapStringNotNull(jsonArray) { obj ->
    obj.optString("name")
}

// JSONObject → Map<String, String>
val map: Map<String, String> = JSONExtKt.toStringStringMap(jsonObj)
```

### 8.2 ResWrapper — 夜间模式资源包装

```kotlin
import com.baidu.searchbox.nacomp.extension.nightmode.ResWrapper

// 在 onNightModeChange 中使用
override fun onNightModeChange(isNightMode: Boolean) {
    // 文字颜色
    ResWrapper.setTextColor(textView, R.color.text_black)

    // 图片
    ResWrapper.setImageDrawable(imageView, R.drawable.icon_search)

    // 背景
    ResWrapper.setBackground(view, R.drawable.bg_card)
    ResWrapper.setBackgroundColor(view, R.color.bg_primary)

    // 获取资源
    val color: Int = ResWrapper.getColor(R.color.text_black)
    val drawable: Drawable? = ResWrapper.getDrawable(R.drawable.icon_search)
}
```

### 8.3 FontSizeInfo — 字号适配

```kotlin
import com.baidu.searchbox.nacomp.extension.fontsize.FontSizeInfo

override fun onFontSizeChange(info: FontSizeInfo) {
    // 文字大小
    info.updateTextSize(textView, SizeType.FRAMEWORK)

    // View 高度
    info.updateHeight(container, SizeType.FRAMEWORK)

    // View 宽度
    info.updateWidth(iconView, SizeType.FRAMEWORK)

    // View 整体尺寸（宽高都变）
    info.updateSize(avatarView, SizeType.FRAMEWORK)
}
```

### 7.4 ViewExKt — View 扩展

```kotlin
import com.baidu.searchbox.nacomp.extension.util.ViewExKt

// dp 转 px
val px: Int = ViewExKt.getDp(5)

// dp 转 px（Float版本）
val pxF: Float = ViewExKt.getDpF(5.5f)
```

### 7.5 CollectionUtils — 集合工具

```kotlin
import com.baidu.searchbox.nacomp.util.CollectionUtils

// 安全判空
if (CollectionUtils.isEmpty(list)) { ... }

// 安全获取最后一个元素
val last: Item? = CollectionUtils.getLast(list)
```

### 7.6 UniqueId — 唯一标识符

```kotlin
import com.baidu.searchbox.nacomp.util.UniqueId

// 在 companion object 中定义类型标识
companion object {
    val TYPE: UniqueId = UniqueId.gen("MyItemType")
}

// 每个 IAdapterData 实现类都需要一个 UniqueId
override fun getType(): UniqueId = TYPE
```

### 7.7 ThrottleClickListener — 防抖点击

```kotlin
import com.baidu.searchbox.nacomp.extension.widget.ThrottleClickListener

button.setOnClickListener(ThrottleClickListener {
    // 不会因为快速连续点击而重复触发
    handleClick()
})
```

---

## 8. 使用指南 — 生命周期控制

### 8.1 CeilingChildLifecycleOwner

用于子组件的生命周期上限控制，确保子组件的生命周期不会超过父组件：

```kotlin
import com.baidu.searchbox.nacomp.extension.lifecycle.CeilingChildLifecycleOwner

// 创建子组件时，绑定到父组件的生命周期
val childLifecycle = CeilingChildLifecycleOwner(parentOwner, Lifecycle.State.INITIALIZED)

val childComp = MyChildComp(childLifecycle, view).apply {
    // 设置最大生命周期状态
    setMaxLifecycle(Lifecycle.State.RESUMED)
}
```

### 8.2 CeilingLifecycleOwner 工具方法

```kotlin
// 创建 ceiling lifecycle
val ceiling = CeilingLifecycleOwner.createCeiling(parentOwner)

// 检查生命周期状态
if (ceiling.isResumed()) { ... }
if (ceiling.isAtLeastStarted()) { ... }

// 设置最大生命周期
ceiling.setMaxLifecycle(Lifecycle.State.RESUMED)
```

---

## 9. 使用指南 — 下拉刷新组件

### 9.1 PullToRefreshRecyclerView

```kotlin
import com.baidu.searchbox.nacomp.extension.widget.ptr.PullToRefreshRecyclerView
import com.baidu.searchbox.nacomp.extension.widget.ptr.PtrAdapter

// XML 中使用
<com.baidu.searchbox.nacomp.extension.widget.ptr.PullToRefreshRecyclerView
    android:id="@+id/ptr_recycler"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

// 代码中配置
val ptrRecyclerView = view.findViewById<PullToRefreshRecyclerView>(R.id.ptr_recycler)
ptrRecyclerView.adapter = PtrAdapter(DelegatorAdapter())

ptrRecyclerView.setOnRefreshListener {
    // 下拉刷新回调
    loadData()
}
```

---

## 10. 使用指南 — View 复用池

### 10.1 ViewPool 机制

```kotlin
import com.baidu.searchbox.nacomp.extension.viewopt.ViewPool
import com.baidu.searchbox.nacomp.extension.viewopt.PooledViewSource
import com.baidu.searchbox.nacomp.extension.viewopt.NewSpawnViewSource

// 创建带复用池的 View 来源
val viewSource = PooledViewSource(MyViewHolder::class.java)

// 或者不复用，每次新建
val newSource = NewSpawnViewSource { context ->
    MyView(context)
}
```

---

## 11. ProGuard 配置

文件位置: `app/zeus-build/proguard_rule/proguard-nacomp.pro`

```proguard
# NAComp 核心包
-keep class com.baidu.searchbox.nacomp.fsm.** { *; }
-keep class com.baidu.searchbox.nacomp.mvvm.** { *; }
-keep class com.baidu.searchbox.nacomp.recycler.** { *; }
-keep class com.baidu.searchbox.nacomp.util.** { *; }

# NAComp 扩展包
-keep class com.baidu.searchbox.nacomp.extension.util.** { *; }
-keep class com.baidu.searchbox.nacomp.extension.widget.** { *; }
-keep class com.baidu.searchbox.nacomp.extension.base.** { *; }
```

---

## 12. 组件化设计思想

### 12.1 设计原则

| 原则 | 实现方式 |
|------|---------|
| **单一职责** | 每个组件只负责一个功能区域 |
| **组合优于继承** | `IComponentGroup` 实现组件嵌套组合 |
| **类型安全** | 泛型约束 Model、ViewModel、Component 一一对应 |
| **生命周期感知** | 所有组件绑定 Android Lifecycle |
| **主题自适应** | `INightMode` + `IFontSize` 接口自动回调 |
| **事件向上传递** | 接口回调模式，子组件通过接口通知父组件 |
| **事件向下传播** | `IComponentGroup` 自动将事件分发给子组件 |

### 12.2 组件通信模式

```
┌──────────────────────────────────────────┐
│          Parent Component (Slave)         │
│                                          │
│   ┌──────────────────────────────────┐   │
│   │      RVComponent (RecyclerView)  │   │
│   │                                  │   │
│   │  ┌────────┐ ┌────────┐          │   │
│   │  │ItemComp│ │ItemComp│  ...     │   │
│   │  │  +VM   │ │  +VM   │          │   │
│   │  └────────┘ └────────┘          │   │
│   └──────────────────────────────────┘   │
│                                          │
│   ┌──────────┐  ┌──────────┐             │
│   │ChildComp │  │ChildComp │  ...        │
│   └──────────┘  └──────────┘             │
└──────────────────────────────────────────┘

通信方式:
1. 父→子: 直接调用子组件方法 / 通过 IComponentGroup 传播
2. 子→父: 接口回调 / LiveData 观察
3. 跨组件: 通过共享 ViewModel 或事件总线
```

### 12.3 新增组件的标准步骤

```
1. 定义 Model (实现 IAdapterData)
   └── 定义 UniqueId.TYPE

2. 定义 ViewModel (继承 BaseExtItemViewModel<M>)
   └── 声明 LiveData 属性
   └── 重写 setModel()

3. 定义 ItemAdapter (继承 ItemAdapter<M, C>)
   └── 实现 onCreateViewHolder()
   └── 实现 getType()

4. 定义 Component (继承 BaseExtItemComponent<M, VM>)
   └── 实现 onCreateViewModel()
   └── 实现 onBindViewModel()
   └── 实现 onNightModeChange()
   └── 实现 onFontSizeChange()

5. 注册到 DelegatorAdapter
   └── delegator.put(new ItemAdapter())
```

---

## 13. lib_hissug 中的 NAComp 组件清单

### 13.1 BaseExtItemComponent 实现（~20个）

| 组件 | 功能 |
|------|------|
| `TextStyleItemComp` | 热搜文字样式项 |
| `ImageBtnStyleItemComp` | 热搜图片按钮项 |
| `ViewMoreItemComp` | 查看更多按钮 |
| `AiToolPanelTranslateComp` | AI工具翻译项 |
| `AiToolTemplateItemComp` | AI工具模板项 |
| `UploadImageItemComp` | 图片上传项 |
| `UploadDocumentItemComp` | 文档上传项 |
| `AddFileItemComp` | 添加文件按钮 |
| `HisTitleItemComp` | 历史标题项 |
| `MoreHisItemComp` | 更多历史项 |
| `HistoryItemComp` | 历史内容项 |
| `AIGCTplItemComp` | AIGC模板项 |
| `QueryTplItemComp` | 查询模板项 |
| `QueryTplTitleItemComp` | 查询模板标题项 |
| `HisGuideComp` | 历史引导 |

### 13.2 BaseExtRVComponent 实现（7个）

| 组件 | 功能 |
|------|------|
| `AiToolPanelComp` | AI工具面板 |
| `HotSearchPageComp` | 热搜页面 |
| `BoardTabComp` | 榜单Tab |
| `UploadFileComp` | 文件上传区域 |
| `TplCardListComp` | 模板卡片列表 |
| `HistoryListComp` | 历史列表 |
| `ListIntegrationComp` | 列表集成组件 |

### 13.3 BaseExtSlaveComponent 实现（~23个）

| 组件 | 功能 |
|------|------|
| `SearchFrameComp` | 搜索框组件（含FSM） |
| `AISearchBoxComp` | AI搜索框 |
| `SugPageComp` | 建议页面 |
| `HistoryPageComp` | 历史页面 |
| `ClassicHistoryPageComp` | 经典历史页面 |
| `RecommendComp` | 推荐组件 |
| `AiToolPanelSyncOptionComp` | AI工具同步选项 |
| `CreationToolPageComp` | 创作工具页 |
| `AiToolMenuBarComp` | AI工具菜单栏 |
| `BaseBottomBarComp` | 底部栏基类 |
| `ChangeModeBarComp` | 模式切换栏 |
| `MultiModeKeyboardBarComp` | 多模式键盘栏 |
| `AiModeGuideComp` | AI模式引导 |
| `DiffusionBallComp` | 扩散球 |
| `SearchServiceComp` | 搜索服务 |
| `ColorfulAnimComp` | 彩色动画 |
| `GlowBoxBorderComp` | 发光边框 |
| `TplListFoldBoxComp` | 模板列表折叠框 |
| `ToolTemplateFoldBoxComp` | 工具模板折叠框 |
| `AiToolBlurBgComp` | AI工具模糊背景 |
| `BaseAiToolComp` | AI工具基类 |
| `MoreAiToolComp` | 更多AI工具 |
| `PullToChangeAiModeComp` | 下拉切换AI模式 |

---

## 14. 常见问题

### Q: BaseExtItemComponent 和 BaseExtSlaveComponent 怎么选？
- **列表项**（RecyclerView 的 item）→ `BaseExtItemComponent<M, VM>`
- **独立区域/页面**（不在 RecyclerView 中）→ `BaseExtSlaveComponent<VM>`

### Q: DelegatorAdapter 和 ItemAdapter 的关系？
- `DelegatorAdapter` 是总适配器，管理多种类型
- `ItemAdapter` 是单个类型的委托，注册到 DelegatorAdapter 中
- 每个 `ItemAdapter` 对应一对 `IAdapterData` + `BaseExtItemComponent`

### Q: 为什么要用 UniqueId 而不是整型 viewType？
- UniqueId 是字符串生成的唯一标识，避免跨模块 viewType 冲突
- 配合 `IAdapterData.getType()` 实现自动分发

### Q: 组件间如何通信？
1. **子→父**: 接口回调或 LiveData
2. **父→子**: 直接方法调用
3. **兄弟组件**: 通过共享 ViewModel
4. **通用事件**: `IComponentGroup` 自动向下传播（夜间模式、字号等）

### Q: 如何处理夜间模式？
1. Component 重写 `onNightModeChange(isNightMode: Boolean)`
2. 使用 `ResWrapper` 替代直接资源访问
3. `IComponentGroup` 会自动传播给子组件
