---
name: aosp-source-navigation
description: 定位 Android/AOSP 源码、追踪调用链并核对固定版本的类、方法和路径。用户询问源码在哪里、要求基于 AOSP 源码分析或更新 Android 技术文章时使用；也用于区分平台、AndroidX、第三方库及厂商私有实现的正确来源。
---

# Android / AOSP 源码定位

目标：找到**指定版本真正参与构建的实现**，给出可复核的路径、方法和必要分支。不要只返回搜索结果，也不要把技术文章改成查找记录。

## 从哪里开始

| 要做的事 | 优先入口 |
|---|---|
| 找类、符号、引用及跨项目关系 | Android Code Search：`https://cs.android.com/`，先选择目标版本 |
| 获取固定版本文件、目录和历史 | Gitiles：`https://android.googlesource.com/` |
| 确认 API 可用性、权限和迁移约束 | `https://developer.android.com/`；实现判断仍回到对应源码 |
| 核对厂商修改或当前工程实际行为 | 当前 checkout 与其 manifest/依赖锁定版本；不能用纯 AOSP 取代厂商实现 |
| 找具体子系统和外部库 | 按需读 [源码地图](references/source-map.md)，不要一次下载全部代码 |

## 定位流程

### 1. 先确定版本和代码所有者

- 已指定 tag/commit，就沿用它。没有指定时，从工程 manifest、依赖声明、用户目标确认；不要默认“最新版”。
- Android 17 文档的示例基线是 `android-17.0.0_r1`，**不是以后所有任务的默认版本**。
- 分开记录平台 tag、内核 revision、AndroidX/库版本和厂商分支。API level、targetSdk、补丁日期都不能唯一推出实现 commit。
- 本地 AOSP checkout 可用 `repo manifest -r` 查看解析后的项目 revision；需要保存时输出到 TEMP，不修改当前 checkout。子仓库用 `git rev-parse HEAD` 与 `git status --short` 确认未提交补丁。
- 平台发布 tag 在某个子项目不可用时，查同版本 manifest 的项目 revision；不要静默退回 main。

### 2. 按主题找到项目，再找到文件

先查源码地图中的项目与目录，再在 Code Search 中搜类名/方法名。要证明“不存在”，需检查目标目录或固定 revision 的树，而不是以一次搜索无结果下结论。

本地检索示例（在相应源码项目内运行）：

```powershell
rg --files -g '*Window*.java' -g '*Window*.kt'
rg -n 'class Window|interface Callback|superDispatchTouchEvent' core/java/android/view
rg -n 'setView\(|addToDisplayAsUser|postVsyncCallback' core/java/android/view/ViewRootImpl.java
rg -n 'messagequeue-gen|CombinedMessageQueue|CombinedDeliMessageQueue' core/java/Android.bp
```

`rg` 查的是工作区；只有内容与 revision 对应时，才能把结果标为该 tag 的源码证据。不要为查源码擅自 checkout/reset，或克隆完整 superproject。

### 3. 取到真实正文，不依赖搜索摘要

Android Code Search 的 superproject 路径与 Gitiles 子项目路径**不是同一个根目录**。例如：

```text
Code Search:
https://cs.android.com/android/platform/superproject/+/android-17.0.0_r1:frameworks/base/core/java/android/view/Window.java

Gitiles:
https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/Window.java
```

网页工具若拿不到动态正文，使用自带 [fetch_gitiles.py](scripts/fetch_gitiles.py)。在本 skill 目录下运行：

```powershell
python scripts/fetch_gitiles.py --project platform/frameworks/base --ref refs/tags/android-17.0.0_r1 --path core/java/android/view/Window.java --cache-dir "$env:TEMP\aosp-source-cache"
python scripts/fetch_gitiles.py --project platform/frameworks/base --ref refs/tags/android-17.0.0_r1 --path core/java/android/os --kind tree --cache-dir "$env:TEMP\aosp-source-cache"
```

- 文件使用 `?format=TEXT`，响应需 Base64 解码；目录使用 `?format=JSON`，去除 Gitiles 的防 XSSI 前缀后解析。
- 脚本仅依赖 Python 标准库，支持 `refs/tags/...` 或完整 commit SHA。输出源码缓存及 evidence JSON：URL、project、ref、path、抓取时间、状态、SHA-256；目录额外记录 tree ID。
- 缓存名绑定 URL 和内容哈希；缓存记录是定位证据，不是构建/运行验证。引用缓存时说明其 revision，不以旧抓取时间冒充本轮重新获取。

### 4. 沿真实边界追调用链

读取声明、调用方、实现方与决定路径的条件，不止 `rg` 命中的一行。

- Java/Kotlin → JNI：找 native 声明、`RegisterNatives`/方法注册表和 C++ 实现；不要只猜导出函数名。
- Binder：区分同进程直调、代理调用、AIDL/生成代码、服务端入口；`oneway`、线程与异常边界分别核对。
- Framework → native/内核：记录进程、线程和实际项目 revision；平台 tag 不等于设备内核 revision。
- 生成源码或多套实现：查 `Android.bp`、生成规则、Soong 变量、feature flag。文件存在不证明它参与当前构建。
- UI/窗口：区分客户端与服务端的对象所有权、建层分支、提交与显示完成。不要把一个运行分支说成所有设备默认。

### 5. 定位失败时怎么继续

- **404**：先检查 project/ref/path 三部分；再取父目录树；查同名 `.kt`、迁移目录、生成源和构建配置。最多尝试两次有依据的候选路径，仍无结果就报告缺失证据或请求源码。
- **429/5xx/超时**：同一目标最多做两次退避重试；可换同一 revision 的页面/原文读取方式，不能换版本冒充成功。脚本本身不会自动重试。
- **方法找不到**：先看接口、父类、委托、生成类、注册表及实际调用点，不创造一个“看起来像”的方法补链。
- **私有源码无权限**：停在可访问的接口边界，列出需要的仓库/文件；不能声称验证了 lib_hissug、NAComp 或其他厂商内部实现。

## 输出约定

源码定位任务至少给出：`project + ref/commit + 路径 + 符号 + 本轮确认的分支/行为 + 未核实边界`。行号只在真实文件上计算，附链接；方法名比单独行号更便于后续定位。

若用户要求写或修技术文章，把正确调用链、原理、算法和示例写回正文；“源码节选”与“示意代码”分开。不要只加版本声明、链接清单或 review 台账。结构检查通过不等于源码、编译或设备验证通过。

此 skill 不自行授权多代理、提交、推送、设备操作或发布。只有用户/适用指令要求时才执行这些工作；普通源码定位不生成额外 review 文件。

## 工具自检

修改下载辅助脚本后，在本 skill 目录运行 `python -B -m unittest discover -s scripts -p 'test_*.py'`。测试覆盖固定 ref、路径拒绝、Base64/目录解析、缓存溯源、HTTP 失败不写缓存和响应大小限制；不请求网络。
