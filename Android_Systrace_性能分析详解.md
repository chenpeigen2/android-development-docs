# Android Systrace 性能分析详解

> 作者：OpenClaw | 日期：2026-03-09
> 技术基线：AOSP `android-17.0.0_r1`；旧 Systrace 保留为历史工具说明，Android 17 使用 Perfetto。
> 
> 参考文档：https://www.androidperformance.com/2019/05/28/Android-Systrace-About/

---

## 目录

- [1. Systrace 简介](#1-systrace-简介)
  - [1.1 什么是 Systrace](#11-什么是-systrace)
  - [1.2 Systrace 与 Perfetto](#12-systrace-与-perfetto)
  - [1.3 Systrace 能做什么](#13-systrace-能做什么)
- [2. Systrace 使用方法](#2-systrace-使用方法)
  - [2.1 命令行采集](#21-命令行采集)
  - [2.2 参数详解](#22-参数详解)
  - [2.3 代码中添加 Trace](#23-代码中添加-trace)
- [3. 60fps 与 Vsync 机制](#3-60fps-与-vsync-机制)
  - [3.1 为什么是 60fps](#31-为什么是-60fps)
  - [3.2 Vsync 信号机制](#32-vsync-信号机制)
  - [3.3 高刷新率 90Hz/120Hz](#33-高刷新率-90hz120hz)
- [4. Choreographer 渲染机制](#4-choreographer-渲染机制)
  - [4.1 Choreographer 简介](#41-choreographer-简介)
  - [4.2 Choreographer 工作流程](#42-choreographer-工作流程)
  - [4.3 doFrame 处理流程](#43-doframe-处理流程)
  - [4.4 Callback 类型](#44-callback-类型)
- [5. 主线程与渲染线程](#5-主线程与渲染线程)
  - [5.1 主线程运行原理](#51-主线程运行原理)
  - [5.2 渲染线程 RenderThread](#52-渲染线程-renderthread)
  - [5.3 软件绘制 vs 硬件加速](#53-软件绘制-vs-硬件加速)
- [6. SystemServer 解读](#6-systemserver-解读)
  - [6.1 SystemServer 进程结构](#61-systemserver-进程结构)
  - [6.2 关键线程](#62-关键线程)
- [7. SurfaceFlinger 解读](#7-surfaceflinger-解读)
  - [7.1 SurfaceFlinger 工作流程](#71-surfaceflinger-工作流程)
  - [7.2 Buffer 合成流程](#72-buffer-合成流程)
- [8. Input 事件处理](#8-input-事件处理)
  - [8.1 InputReader 与 InputDispatcher](#81-inputreader-与-inputdispatcher)
  - [8.2 事件分发流程](#82-事件分发流程)
- [9. BufferQueue 与 Triple Buffer](#9-bufferqueue-与-triple-buffer)
  - [9.1 BufferQueue 模型](#91-bufferqueue-模型)
  - [9.2 单缓冲/双缓冲/三缓冲](#92-单缓冲双缓冲三缓冲)
  - [9.3 Triple Buffer 的作用](#93-triple-buffer-的作用)
- [10. CPU 状态分析](#10-cpu-状态分析)
  - [10.1 CPU 核心架构](#101-cpu-核心架构)
  - [10.2 线程 CPU 状态](#102-线程-cpu-状态)
  - [10.3 Runnable 状态分析](#103-runnable-状态分析)
  - [10.4 Sleep 状态分析](#104-sleep-状态分析)
  - [10.5 Uninterruptible Sleep 分析](#105-uninterruptible-sleep-分析)
- [11. Binder 与锁竞争](#11-binder-与锁竞争)
  - [11.1 Binder 通信机制](#111-binder-通信机制)
  - [11.2 锁竞争分析](#112-锁竞争分析)
- [12. 卡顿分析实战](#12-卡顿分析实战)
  - [12.1 卡顿定义与原理](#121-卡顿定义与原理)
  - [12.2 卡顿原因分类](#122-卡顿原因分类)
  - [12.3 分析流程与方法](#123-分析流程与方法)
  - [12.4 Perfetto 完整采集与 SQL 归因](#124-perfetto-完整采集与-sql-归因)
- [13. APM 监控方案](#13-apm-监控方案)
  - [13.1 FrameCallback 监控](#131-framecallback-监控)
  - [13.2 FrameInfo 监控](#132-frameinfo-监控)
  - [13.3 Looper Printer 监控](#133-looper-printer-监控)
- [14. 常见问题](#14-常见问题)
  - [14.1 Systrace 文件无法在 Chrome 打开](#141-systrace-文件无法在-chrome-打开)
  - [14.2 采集不到应用 Trace](#142-采集不到应用-trace)
  - [14.3 如何判断是应用问题还是系统问题](#143-如何判断是应用问题还是系统问题)
- [15. 知识体系总结](#15-知识体系总结)

---

## 1. Systrace 简介

### 1.1 什么是 Systrace

Systrace 是 Android 4.1 (API 16) 引入的性能分析工具，用于收集和分析 Android 系统和应用程序的时序信息。它可以图形化展示系统各个进程、线程的运行状态，帮助开发者定位性能问题。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Systrace 功能概览                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                          Systrace 采集                                   │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
  │  │ 内核信息    │  │ 系统服务    │  │ 应用进程    │  │ 硬件信息    │    │
  │  │ - CPU调度   │  │ - AMS/WMS   │  │ - 主线程    │  │ - GPU       │    │
  │  │ - 进程切换  │  │ - SF合成    │  │ - 渲染线程  │  │ - 显示      │    │
  │  │ - 中断处理  │  │ - Input     │  │ - 业务逻辑  │  │ - 电源      │    │
  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                        Chrome 可视化展示                                 │
  │  ┌──────────────────────────────────────────────────────────────────┐  │
  │  │ Timeline 按时间轴展示所有进程、线程的运行状态                     │  │
  │  │ - CPU 频率变化                                                    │  │
  │  │ - 线程运行状态 (Running/Runnable/Sleep)                           │  │
  │  │ - 方法执行耗时                                                    │  │
  │  │ - Vsync 信号                                                      │  │
  │  │ - Buffer 流转                                                     │  │
  │  └──────────────────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Systrace 与 Perfetto

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Systrace vs Perfetto                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────┬─────────────────────┬─────────────────────────────┐
  │       特性           │     Systrace        │     Perfetto               │
  ├─────────────────────┼─────────────────────┼─────────────────────────────┤
  │ 引入版本             │ Android 4.1         │ Android 9.0                │
  ├─────────────────────┼─────────────────────┼─────────────────────────────┤
  │ 数据格式             │ HTML/JSON           │ Protocol Buffers           │
  ├─────────────────────┼─────────────────────┼─────────────────────────────┤
  │ 查看工具             │ Chrome 浏览器       │ Perfetto UI / Chrome       │
  ├─────────────────────┼─────────────────────┼─────────────────────────────┤
  │ 采集时长             │ 较短（受内存限制）   │ 更长、更灵活               │
  ├─────────────────────┼─────────────────────┼─────────────────────────────┤
  │ 扩展性               │ 有限                │ 高度可扩展                 │
  ├─────────────────────┼─────────────────────┼─────────────────────────────┤
  │ 推荐使用             │ 兼容老版本          │ Android 9.0+ 推荐          │
  └─────────────────────┴─────────────────────┴─────────────────────────────┘

  Perfetto 是 Systrace 的继任者，功能更强大：
  - 支持更长时间的数据采集
  - 支持 SQL 查询分析
  - 支持自定义数据源
  - 支持 Android Studio Profiler 集成
```

### 1.3 Systrace 能做什么

```text
Systrace 可以分析的问题类型：
─────────────────────────────────────────────────────────────────────────────

1. 流畅性问题（卡顿、掉帧）
   ├── 应用主线程耗时
   ├── 渲染线程耗时
   ├── SurfaceFlinger 合成耗时
   └── Buffer 流转问题

2. 响应速度问题
   ├── 应用启动速度
   ├── 界面切换速度
   ├── 点击响应延迟
   └── 锁屏/解锁速度

3. 系统性能问题
   ├── CPU 调度问题
   ├── 锁竞争问题
   ├── Binder 通信耗时
   └── 内存压力

4. 功耗问题
   ├── CPU 频率策略
   ├── 后台进程活动
   └── 唤醒源分析
```

---

## 2. Systrace 使用方法

### 2.1 命令行采集

```bash
# 已有 Catapult systrace.py 环境的历史采集方式，不保证新 SDK 附带该脚本。
python systrace.py -t 10 -a com.example.app -o trace.html sched freq idle am wm gfx view binder_driver
# Android 17 简单模式；不要附加 --txt（这是 textproto 配置模式参数）。
adb shell perfetto -o /data/misc/perfetto-traces/quick.perfetto-trace -t 10s sched freq idle am wm gfx view binder_driver
```

需要 FrameTimeline、应用 trace 和 SQL 归因时使用下面完整配置；只采 GPU memory 或 linux.sysfs 无法得到后文的 CPU 调度和主线程事件。

```textproto
buffers { size_kb: 32768 fill_policy: RING_BUFFER }
duration_ms: 15000
data_sources { config { name: "linux.ftrace" ftrace_config {
  ftrace_events: "sched/sched_switch"
  ftrace_events: "sched/sched_waking"
  ftrace_events: "power/cpu_frequency"
  ftrace_events: "power/cpu_idle"
  ftrace_events: "binder/binder_transaction"
  ftrace_events: "binder/binder_transaction_received"
  atrace_categories: "am"
  atrace_categories: "wm"
  atrace_categories: "gfx"
  atrace_categories: "view"
  atrace_categories: "input"
  atrace_categories: "dalvik"
  atrace_apps: "com.example.app"
} } }
data_sources { config { name: "linux.process_stats" process_stats_config {
  scan_all_processes_on_start: true
} } }
data_sources { config { name: "android.surfaceflinger.frametimeline" } }
```

```powershell
adb push .\feed.pbtxt /data/local/tmp/feed.pbtxt
adb shell perfetto --txt -c /data/local/tmp/feed.pbtxt -o /data/misc/perfetto-traces/feed.perfetto-trace
# 终端 B：终端 A 正在采集时执行目标动作，不是采集结束后才操作
adb shell am start -W -n com.example.app/.MainActivity
# 终端 A 采集结束后再拉取
adb pull /data/misc/perfetto-traces/feed.perfetto-trace .\feed.perfetto-trace
```

`--txt` 用于 textproto 配置，不与无 -c 的简单分类模式混用。包满足采样条件且 atrace_apps 匹配。分类和 ftrace 事件依设备支持；检查 stderr、Trace stats 的丢包和缺失数据，空轨道不证明无耗时。

### 2.2 参数详解

Android 17 优先使用上一节的 Perfetto textproto，不混用旧 `systrace.py`、`atrace` 和 `perfetto` 三套参数。

| 配置 / 命令 | 含义 |
|---|---|
| `--txt -c <设备配置路径> -o <设备输出路径>` | Perfetto 解析 textproto 并采集，配置文件先推到设备 |
| `duration_ms: 15000` | 采集 15 秒，单位不是 CLI 简单模式的秒 |
| `buffers { size_kb: 32768 fill_policy: RING_BUFFER }` | 32 MiB 环形 trace buffer，不是每个 CPU 的 ftrace buffer |
| `linux.ftrace` 的 `ftrace_events` | `sched/sched_switch`、`sched/sched_waking` 等内核事件，取决于设备支持 |
| `atrace_categories` / `atrace_apps` | 系统分类 / 应用 Trace 标记包过滤 |
| `android.surfaceflinger.frametimeline` | FrameTimeline 实际/期望帧 |
| `linux.process_stats` | 进程、线程元数据，供 SQL 关联 |

使用设备的 `atrace --list_categories` 查询分类；不存在的 `--from-boost` 不能用于 Perfetto，开机 trace 需单独配置 boot tracing，不是给普通采集加 `--from-boot`。`network` 不是跨设备通用的 atrace 网络抓包分类：网络分析要结合应用标记、系统支持的数据源或有权限的抓包。`sched` 支持 CPU 调度分析，但并非所有 trace 都必须采集 sched；空轨道也不证明没有请求或耗时。

### 2.3 代码中添加 Trace

```kotlin
// ==================== Kotlin 代码中添加 Trace ====================

// 方式1：使用 Trace.beginSection/endSection
import android.os.Trace

class MainActivity : AppCompatActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        Trace.beginSection("MainActivity.onCreate")
        try {
            super.onCreate(savedInstanceState)
            setContentView(R.layout.activity_main)
            
            // 复杂初始化
            Trace.beginSection("initViews")
            try { initViews() } finally { Trace.endSection() }
            
            Trace.beginSection("loadData")
            try { loadData() } finally { Trace.endSection() }
        } finally {
            Trace.endSection()  // 对应 MainActivity.onCreate
        }
    }
    
    private fun initViews() {
        // 初始化视图逻辑
    }
    
    private fun loadData() {
        // 加载数据逻辑
    }
}

// 方式2：使用扩展函数自动管理
inline fun <T> trace(sectionName: String, block: () -> T): T {
    Trace.beginSection(sectionName)
    try {
        return block()
    } finally {
        Trace.endSection()
    }
}

// 使用
override fun onCreate(savedInstanceState: Bundle?) {
    trace("MainActivity.onCreate") {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        trace("initViews") {
            initViews()
        }
    }
}

// 方式3：使用 androidx.tracing.Trace（AndroidX）
import androidx.tracing.Trace

Trace.beginSection("MyOperation")
// ... 操作
Trace.endSection()
```

应用没有 `<trace-config>` 这样的系统识别 XML 来开启 atrace 分类；采集配置必须在 Perfetto textproto 中。调用 `Trace.beginSection/endSection` 要同线程、finally 配对；跨挂起点/线程使用 `beginAsyncSection/endAsyncSection`（API 29+）并用唯一 cookie，在取消/异常时也结束。

```java
// ==================== Java 代码中添加 Trace ====================
import android.os.Trace;

public class DataProcessor {
    
    public void processData(List<Data> dataList) {
        Trace.beginSection("DataProcessor.processData");
        try {
            for (Data data : dataList) {
                Trace.beginSection("processItem:" + data.getId());
                try {
                    processItem(data);
                } finally {
                    Trace.endSection();
                }
            }
        } finally {
            Trace.endSection();
        }
    }
    
    private void processItem(Data data) {
        // 处理单个数据项
    }
}
```

---

## 3. 60fps 与 Vsync 机制

### 3.1 为什么是 60fps

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         帧率与流畅度                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  屏幕刷新率（Hardware）：
  ─────────────────────────────────────────────────────────────────────────
  - 60Hz 屏幕：每秒刷新 60 次，间隔 16.6ms
  - 90Hz 屏幕：每秒刷新 90 次，间隔 11.1ms
  - 120Hz 屏幕：每秒刷新 120 次，间隔 8.3ms

  FPS（Software）：
  ─────────────────────────────────────────────────────────────────────────
  - FPS = Frame Per Second，每秒渲染帧数
  - 60fps：每秒渲染 60 帧，每帧需要在 16.6ms 内完成
  - 由软件系统控制

  为什么是 60fps？
  ─────────────────────────────────────────────────────────────────────────
  1. 60fps 是常见显示刷新/交互目标，不是人眼存在 60fps 感知上限
  2. 屏幕刷新率匹配：大部分屏幕是 60Hz
  3. 平衡性能与功耗：更高帧率意味着更高功耗
  4. 高刷新率需按实际刷新周期、deadline 和 FrameTimeline 判断

  时间预算：
  ─────────────────────────────────────────────────────────────────────────

  60fps (16.6ms)：
  ┌──────────────────────────────────────────────────────────────────────┐
  │ Input(2ms) │ Animation(2ms) │ Measure/Layout(4ms) │ Draw(4ms) │ GPU │
  └──────────────────────────────────────────────────────────────────────┘
  0            2ms              4ms                   8ms         12ms   16.6ms

  90fps (11.1ms)：
  ┌───────────────────────────────────────────────┐
  │ Input │ Anim │ Measure │ Draw │    GPU      │
  └───────────────────────────────────────────────┘
  0       1ms    2ms      4ms     6ms           11.1ms
```

### 3.2 Vsync 信号机制

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Vsync 信号分发                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  硬件 Vsync (HW_VSYNC)
          │
          ▼
  ┌───────────────────┐
  │   DispSync        │  ← 软件模拟 Vsync
  │   (SF 进程)       │
  └───────────────────┘
          │
     ┌────┴────┐
     ▼         ▼
  VSYNC-app  VSYNC-sf
  (16.6ms)   (16.6ms + offset)

  VSYNC-app：发送给应用进程，触发 Choreographer
  VSYNC-sf：发送给 SurfaceFlinger，触发合成

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    Vsync-Offset 机制                                    │
  │                                                                         │
  │   时间线 ──────────────────────────────────────────────────────────────▶│
  │                                                                         │
  │   VSYNC-app      │              │              │                        │
  │       ▼          │              │              │                        │
  │   ┌─────┐        │              │              │                        │
  │   │ App │  渲染   │              │              │                        │
  │   └─────┘        │              │              │                        │
  │                  ▼              │              │                        │
  │               VSYNC-sf          │              │                        │
  │              ┌──────┐           │              │                        │
  │              │  SF  │   合成     │              │                        │
  │              └──────┘           │              │                        │
  │                                ▼              ▼                        │
  │                            显示上一帧      显示新帧                    │
  └─────────────────────────────────────────────────────────────────────────┘

  Vsync-Offset 的作用：
  ─────────────────────────────────────────────────────────────────────────
  - 让 App 先渲染，SF 后合成，充分利用时间
  - 典型 offset：App 比 SF 早 4-6ms
  - 这样 App 和 SF 可以在一个 Vsync 周期内完成各自工作
```

### 3.3 高刷新率 90Hz/120Hz

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    高刷新率的挑战                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  帧时间对比：
  ─────────────────────────────────────────────────────────────────────────

  60Hz：  ┌────────────────────────────────────────────────────────────────┐ = 16.6ms
  90Hz：  ┌─────────────────────────────────────────┐ = 11.1ms
  120Hz： ┌────────────────────────────┐ = 8.3ms

  性能要求：
  ─────────────────────────────────────────────────────────────────────────

  ┌─────────────────┬───────────────┬───────────────┬─────────────────────┐
  │     指标         │    60Hz       │    90Hz       │     120Hz           │
  ├─────────────────┼───────────────┼───────────────┼─────────────────────┤
  │ 帧时间预算       │    16.6ms     │    11.1ms     │     8.3ms           │
  ├─────────────────┼───────────────┼───────────────┼─────────────────────┤
  │ CPU/GPU 压力     │    基准       │    1.5x       │     2x              │
  ├─────────────────┼───────────────┼───────────────┼─────────────────────┤
  │ 功耗影响         │    基准       │    +20~30%    │     +40~60%         │
  └─────────────────┴───────────────┴───────────────┴─────────────────────┘

  自适应刷新率：
  ─────────────────────────────────────────────────────────────────────────
  - 静态界面：降低到 60Hz 甚至更低
  - 滑动/动画：提升到 90Hz/120Hz
  - 游戏：根据游戏帧率动态调整
```

---

## 4. Choreographer 渲染机制

### 4.1 Choreographer 简介

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Choreographer 在渲染链路中的位置                          │
└─────────────────────────────────────────────────────────────────────────────┘

  承上：
  ─────────────────────────────────────────────────────────────────────────
  - 接收 App 的各种更新消息
  - 等到 Vsync 到来时统一处理
  - 处理 Input、Animation、Traversal
  - 判断卡顿掉帧情况

  启下：
  ─────────────────────────────────────────────────────────────────────────
  - 请求和接收 Vsync 信号
  - 通过 FrameDisplayEventReceiver.onVsync 回调
  - 调用 scheduleVsync 请求 Vsync

  核心作用：
  ─────────────────────────────────────────────────────────────────────────
  配合 Vsync，给上层 App 的渲染提供稳定的 Message 处理时机
```

### 4.2 Choreographer 工作流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Choreographer 工作流程                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 初始化阶段：
  ─────────────────────────────────────────────────────────────────────────
  Choreographer.getInstance()
      │
      ├── 创建 FrameHandler（绑定 Looper）
      ├── 创建 FrameDisplayEventReceiver（监听 Vsync）
      └── 创建 CallbackQueues（5 种类型）

  2. 请求 Vsync：
  ─────────────────────────────────────────────────────────────────────────
  ViewRootImpl.scheduleTraversals()
      │
      └── Choreographer.postCallback(CALLBACK_TRAVERSAL, ...)
          │
          └── scheduleFrameLocked()
              │
              └── FrameDisplayEventReceiver.scheduleVsync()

  3. Vsync 到来：
  ─────────────────────────────────────────────────────────────────────────
  SurfaceFlinger.appEventThread
      │
      └── BitTube 传递 Vsync 事件
          │
          └── DisplayEventDispatcher 收到事件
              │
              └── FrameDisplayEventReceiver.onVsync()
                  │
                  └── Message -> doFrame()

  4. doFrame 处理：
  ─────────────────────────────────────────────────────────────────────────
  doFrame()
      │
      ├── 计算掉帧逻辑
      ├── 记录帧绘制信息
      ├── doCallbacks(CALLBACK_INPUT)
      ├── doCallbacks(CALLBACK_ANIMATION)
      ├── doCallbacks(CALLBACK_INSETS_ANIMATION)
      ├── doCallbacks(CALLBACK_TRAVERSAL)
      └── doCallbacks(CALLBACK_COMMIT)
```

### 4.3 doFrame 处理流程

```kotlin
// ==================== doFrame 核心逻辑 ====================
void doFrame(long frameTimeNanos, int frame) {
    final long startNanos;
    synchronized (mLock) {
        // 1. 计算掉帧
        long intendedFrameTimeNanos = frameTimeNanos;
        startNanos = System.nanoTime();
        final long jitterNanos = startNanos - frameTimeNanos;
        
        if (jitterNanos >= mFrameIntervalNanos) {
            final long skippedFrames = jitterNanos / mFrameIntervalNanos;
            if (skippedFrames >= SKIPPED_FRAME_WARNING_LIMIT) {
                Log.i(TAG, "Skipped " + skippedFrames + " frames! "
                    + "The application may be doing too much work on its main thread.");
            }
        }
    }

    // 2. 记录帧信息
    mFrameInfo.setVsync(intendedFrameTimeNanos, frameTimeNanos);
    
    // 3. 按顺序处理 Callbacks
    try {
        Trace.traceBegin(Trace.TRACE_TAG_VIEW, "Choreographer#doFrame");
        
        mFrameInfo.markInputHandlingStart();
        doCallbacks(Choreographer.CALLBACK_INPUT, frameTimeNanos);

        mFrameInfo.markAnimationsStart();
        doCallbacks(Choreographer.CALLBACK_ANIMATION, frameTimeNanos);
        
        doCallbacks(Choreographer.CALLBACK_INSETS_ANIMATION, frameTimeNanos);

        mFrameInfo.markPerformTraversalsStart();
        doCallbacks(Choreographer.CALLBACK_TRAVERSAL, frameTimeNanos);

        doCallbacks(Choreographer.CALLBACK_COMMIT, frameTimeNanos);
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_VIEW);
    }
}
```

### 4.4 Callback 类型

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Choreographer Callback 类型                              │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────┬─────────────────────────────────────────────────────────┐
  │   Callback 类型  │                    说明                                │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ CALLBACK_INPUT  │ 输入事件处理，最高优先级                                │
  │                 │ - ViewRootImpl.ConsumeBatchedInputRunnable              │
  │                 │ - 处理 Touch、Key 事件                                  │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ CALLBACK_       │ 动画相关回调                                            │
  │ ANIMATION       │ - View.postOnAnimation                                 │
  │                 │ - ValueAnimator                                        │
  │                 │ - Choreographer.FrameCallback                          │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ CALLBACK_INSETS_│ Insets 动画回调                                         │
  │ ANIMATION       │ - 处理系统栏动画                                        │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ CALLBACK_       │ 遍历回调，包含 measure、layout、draw                    │
  │ TRAVERSAL       │ - ViewRootImpl.TraversalRunnable                       │
  │                 │ - performTraversals()                                  │
  ├─────────────────┼─────────────────────────────────────────────────────────┤
  │ CALLBACK_COMMIT │ 提交回调，最后执行                                      │
  │                 │ - 帧时间修正/提交阶段回调，不是 onTrimMemory 触发点                                    │
  │                 │ - 帧耗时监控                                           │
  └─────────────────┴─────────────────────────────────────────────────────────┘

  执行顺序：INPUT → ANIMATION → INSETS_ANIMATION → TRAVERSAL → COMMIT

  为什么是这个顺序？
  ─────────────────────────────────────────────────────────────────────────
  - INPUT 和 ANIMATION 会修改 View 的属性
  - TRAVERSAL 需要基于最新的属性进行测量、布局、绘制
  - COMMIT 是收尾工作
```

---

## 5. 主线程与渲染线程

### 5.1 主线程运行原理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Android 主线程初始化                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  进程启动流程：
  ─────────────────────────────────────────────────────────────────────────
  Zygote.fork()
      │
      └── ZygoteInit.zygoteInit() // 普通 app；childZygoteInit 是子 Zygote 分支
          │
          └── RuntimeInit.findStaticMain(ActivityThread.class)
              │
              └── ActivityThread.main()
                  │
                  ├── Looper.prepareMainLooper()
                  ├── ActivityThread.attach()
                  └── Looper.loop()

  ActivityThread.main() 源码：
  ─────────────────────────────────────────────────────────────────────────
  public static void main(String[] args) {
      Looper.prepareMainLooper();
      
      ActivityThread thread = new ActivityThread();
      thread.attach(false, startSeq);
      
      if (sMainThreadHandler == null) {
          sMainThreadHandler = thread.getHandler();
      }
      
      Looper.loop();  // 进入消息循环
  }

  主线程处理的消息类型：
  ─────────────────────────────────────────────────────────────────────────

  ┌───────────────────────┬─────────────────────────────────────────────────┐
  │       消息类型         │              说明                              │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ BIND_APPLICATION      │ 绑定 Application                                │
  │ LAUNCH_ACTIVITY       │ 启动 Activity                                   │
  │ PAUSE_ACTIVITY        │ 暂停 Activity                                   │
  │ STOP_ACTIVITY         │ 停止 Activity                                   │
  │ DESTROY_ACTIVITY      │ 销毁 Activity                                   │
  │ RECEIVER              │ 广播接收                                        │
  │ CREATE_SERVICE        │ 创建 Service                                    │
  │ BIND_SERVICE          │ 绑定 Service                                    │
  │ SERVICE_ARGS          │ Service 命令                                    │
  │ INSTALL_PROVIDER      │ 安装 Provider                                   │
  └───────────────────────┴─────────────────────────────────────────────────┘
```

### 5.2 渲染线程 RenderThread

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RenderThread 工作流程                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  硬件加速开启时（默认）：
  ─────────────────────────────────────────────────────────────────────────

  MainThread                        RenderThread
      │                                  │
      │  1. 更新 DisplayList             │
      ├──────────────────────────────────▶
      │                                  │
      │  2. syncAndDrawFrame             │
      ├──────────────────────────────────▶
      │                                  │
      │     (MainThread 释放)            │  3. dequeueBuffer
      │                                  │
      │                                  │  4. Skia GL/Vulkan 后端渲染
      │                                  │
      │                                  │  5. queueBuffer
      │                                  │
      │                                  │     ↓
      │                                  │  SurfaceFlinger

  RenderThread 的优势：
  ─────────────────────────────────────────────────────────────────────────
  1. 主线程在 RenderThread 同步点可能等待；提交 GPU 后可与后续工作重叠
  2. 可以并行处理下一帧的逻辑
  3. GPU 渲染不占用主线程 CPU
  4. 减少主线程卡顿概率

  RenderThread 初始化：
  ─────────────────────────────────────────────────────────────────────────
  ViewRootImpl.draw()
      │
      └── HardwareRenderer.draw()
          │
          ├── updateRootDisplayList()  // 更新 DisplayList
          └── syncAndDrawFrame()       // 同步并触发渲染
              │
              └── RenderProxy.syncAndDrawFrame()  // Native 层
                  │
                  └── DrawFrameTask.drawFrame()
                      │
                      └── RenderThread 真正渲染
```

### 5.3 软件绘制 vs 硬件加速

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    软件绘制 vs 硬件加速                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  软件绘制（关闭硬件加速）：
  ─────────────────────────────────────────────────────────────────────────
  
  MainThread
      │
      │  1. measure/layout
      │
      │  2. draw (CPU + libSkia)
      │     ↓
      │  3. queueBuffer
      │     ↓
      │  SurfaceFlinger

  特点：
  - 没有 RenderThread
  - 所有渲染工作在主线程
  - 使用 CPU + libSkia 渲染
  - 主线程压力大，容易卡顿

  硬件加速（默认开启）：
  ─────────────────────────────────────────────────────────────────────────
  
  MainThread                    RenderThread
      │                              │
      │  1. measure/layout           │
      │                              │
      │  2. 构建 DisplayList         │
      │     (记录绘制命令)            │
      │                              │
      │  3. 同步 DisplayList ─────────▶
      │                              │
      │     (主线程释放)              │  4. GPU 渲染
      │                              │
      │                              │  5. queueBuffer

  特点：
  - RenderThread 承担渲染工作
  - 使用 GPU 加速渲染
  - 主线程压力小
  - DisplayList 可复用和优化

  DisplayList 优势：
  ─────────────────────────────────────────────────────────────────────────
  1. 可按需多次绘制无需重新执行业务逻辑
  2. 特定操作（translate、scale）可作用于整个 DisplayList
  3. 可进行优化（如所有文本一起绘制）
  4. 可转移到另一个线程执行

  关闭硬件加速的方法：
  ─────────────────────────────────────────────────────────────────────────
  <!-- AndroidManifest.xml -->
  <application
      android:hardwareAccelerated="false">
      
  或单个 Activity/View：
  <activity android:hardwareAccelerated="false" />
  view.setLayerType(View.LAYER_TYPE_SOFTWARE, null);
```

---

## 6. SystemServer 解读

### 6.1 SystemServer 进程结构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SystemServer 进程结构                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  SystemServer 进程
  │
  ├── main 线程 (SystemServer)
  │   └── 负责启动服务
  │
  ├── android.display 线程
  │   └── DisplayManagerService
  │
  ├── android.ui 线程
  │   └── UiThread（共享 UI 工作线程，不存在统一 UIManagerService）
  │
  ├── ActivityManager 线程
  │   └── ActivityManagerService
  │
  ├── PackageManager 线程
  │   └── PackageManagerService
  │
  ├── PowerManager 线程
  │   └── PowerManagerService
  │
  └── 其他服务线程...

  关键服务说明：
  ─────────────────────────────────────────────────────────────────────────

  ┌───────────────────────┬─────────────────────────────────────────────────┐
  │       服务名称         │              职责                              │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ AMS                   │ Activity 生命周期管理                            │
  │ (ActivityManager)     │ 进程管理和调度                                   │
  │                       │ 内存策略（LMKD 是独立 daemon）                                   │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ WMS                   │ 窗口管理                                         │
  │ (WindowManager)       │ 输入事件分发                                     │
  │                       │ 动画管理                                         │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ PMS                   │ 应用安装/卸载                                    │
  │ (PackageManager)      │ 权限管理                                         │
  │                       │ 组件查询                                         │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ PMS                   │ 电源管理                                         │
  │ (PowerManager)        │ 休眠/唤醒                                        │
  │                       │ 电池统计                                         │
  └───────────────────────┴─────────────────────────────────────────────────┘
```

### 6.2 关键线程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SystemServer 关键线程                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  在 Systrace 中常见的 SystemServer 线程：

  ┌───────────────────────┬─────────────────────────────────────────────────┐
  │       线程名称         │              说明                              │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ android.bg            │ 后台操作，如 trimMemory                         │
  │ android.display       │ 显示相关操作                                    │
  │ android.ui            │ UI 相关操作                                     │
  │ android.anim          │ 动画处理                                        │
  │ android.fg            │ 前台操作                                        │
  │ Binder:xxx_x          │ Binder 通信线程                                 │
  │ InputReader           │ 读取输入事件                                    │
  │ InputDispatcher       │ 分发输入事件                                    │
  └───────────────────────┴─────────────────────────────────────────────────┘

  线程优先级：
  ─────────────────────────────────────────────────────────────────────────
  - android.display：最高优先级
  - android.ui：高优先级
  - android.anim：中等优先级
  - android.bg：低优先级
```

---

## 7. SurfaceFlinger 解读

### 7.1 SurfaceFlinger 工作流程

下面保留生产者/消费者抽象。Android 17 应用窗口常由客户端 BLASTBufferQueue 消费 BufferQueue，再以 SurfaceControl.Transaction.setBuffer 提交 SF；不是每个窗口都由 SF 直接 acquire 同一个 BufferQueue。检查 `BLASTBufferQueue::processNextBufferLocked`、`SurfaceFlinger::commit/composite` 和 Scheduler，而非把旧版线程/Layer 子类名当当前 ABI。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SurfaceFlinger 合成流程                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  App 进程                    SurfaceFlinger 进程
      │                              │
      │  1. dequeueBuffer            │
      │     (获取空闲 Buffer)         │
      │                              │
      │  2. 渲染到 Buffer             │
      │                              │
      │  3. queueBuffer ─────────────▶
      │     (提交 Buffer)             │
      │                              │
      │                              │  4. 等待 VSYNC-SF
      │                              │
      │                              │  5. acquireBuffer
      │                              │     (获取待合成 Buffer)
      │                              │
      │                              │  6. 合成 Layer
      │                              │     (GPU/HWC)
      │                              │
      │                              │  7. present
      │                              │     (送显)
      │                              │
      │                              │  8. releaseBuffer
      │                              │     (释放 Buffer)
      │  ◀────────────────────────────
      │     (Buffer 回收)

  SurfaceFlinger 线程：
  ─────────────────────────────────────────────────────────────────────────
  - main 线程：主合成线程
  - appEventThread：向 App 发送 Vsync
  - 合成由 Scheduler/VSyncDispatch 调度；不要把旧 sfEventThread 当当前固定线程
  - VSyncDispatch/Scheduler：Android 17 的预测与调度，不再以旧 DispSync 线程描述
```

### 7.2 Buffer 合成流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Buffer 合成方式                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  合成方式：
  ─────────────────────────────────────────────────────────────────────────

  1. GPU 合成 (Client Composition)
     ─────────────────────────────────────────────────────────────────────
     - RenderEngine 使用 GL/Vulkan 等后端，取决于设备配置
     - 灵活，支持各种效果
     - 功耗较高
     - 适用于复杂场景

  2. HWC 合成 (Device Composition)
     ─────────────────────────────────────────────────────────────────────
     - 使用硬件合成器 (Hardware Composer)
     - 功耗低，性能好
     - 有限制（层数、格式等）
     - 适用于简单场景

  合成策略：
  ─────────────────────────────────────────────────────────────────────────
  - 优先使用 HWC 合成
  - 当 Layer 数量超过 HWC 限制时，使用 GPU 合成
  - 特殊效果（模糊、阴影）需要 GPU 合成

  Layer 类型：
  ─────────────────────────────────────────────────────────────────────────

  ┌───────────────────────┬─────────────────────────────────────────────────┐
  │       Layer 类型       │              说明                              │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ BufferStateLayer      │ 应用窗口                                        │
  │ EffectLayer           │ 效果层（如圆角）                                │
  │ ContainerLayer        │ 容器层                                          │
  └───────────────────────┴─────────────────────────────────────────────────┘
```

---

## 8. Input 事件处理

### 8.1 InputReader 与 InputDispatcher

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Input 事件处理流程                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  硬件输入设备
      │
      ▼
  ┌─────────────┐
  │ EventHub    │ ← 监听 /dev/input/ 设备节点
  └─────────────┘
      │
      ▼
  ┌─────────────┐
  │ InputReader │ ← 读取原始事件
  │ (Native)    │   - 事件分类
  └─────────────┘   - 坐标转换
      │
      ▼
  ┌─────────────┐
  │ InputDispatcher │ ← 分发事件
  │ (Native)        │   - 查找目标窗口
  └─────────────────┘   - 事件过滤
      │
      ├──────────────────────────────────┐
      │                                  │
      ▼                                  ▼
  OutboundQueue                    WaitQueue
  (待发送事件)                      (等待确认的事件)
      │
      ▼
  ┌─────────────┐
  │ Connection  │ ← 与 App 的连接
  └─────────────┘
      │
      ▼
  App 进程
  ┌─────────────┐
  │ InputChannel│
  └─────────────┘
      │
      ▼
  PendingInputEventQueue
      │
      ▼
  UI Thread 处理
```

### 8.2 事件分发流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Systrace 中的 Input 事件流                               │
└─────────────────────────────────────────────────────────────────────────────┘

  Systrace 中可以看到：
  ─────────────────────────────────────────────────────────────────────────

  SystemServer 进程：
  ┌──────────────────────────────────────────────────────────────────────┐
  │ InputReader   │████████│        │████████│        │                   │
  │               │ read   │        │ read   │        │                   │
  ├──────────────────────────────────────────────────────────────────────┤
  │ InputDispatcher│      │████████│        │████████│                   │
  │               │       │dispatch│        │dispatch│                   │
  └──────────────────────────────────────────────────────────────────────┘

  OutboundQueue:  ┌─────┐        ┌─────┐
                 │Event│        │Event│
  WaitQueue:                ┌─────┐        ┌─────┐
                           │Event│        │Event│

  App 进程：
  ┌──────────────────────────────────────────────────────────────────────┐
  │ UI Thread     │        │████████│        │████████│                   │
  │               │        │deliver│        │process│                   │
  └──────────────────────────────────────────────────────────────────────┘

  InputResponse:
                 ┌────────────────────────────────────────────────────────┐
                 │ Input_Down  │ Input_Move │ ... │ Input_Up │             │
                 └────────────────────────────────────────────────────────┘
```

---

## 9. BufferQueue 与 Triple Buffer

### 9.1 BufferQueue 模型

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BufferQueue 生产者-消费者模型                            │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │    Producer (App)                    Consumer (SurfaceFlinger)          │
  │                                                                         │
  │    ┌──────────┐                      ┌──────────┐                       │
  │    │dequeue   │                      │acquire   │                       │
  │    │Buffer    │                      │Buffer    │                       │
  │    └────┬─────┘                      └────┬─────┘                       │
  │         │                                 │                             │
  │         ▼                                 ▼                             │
  │    ┌─────────────────────────────────────────────────────────┐          │
  │    │                     BufferQueue                         │          │
  │    │  ┌─────┐   ┌─────┐   ┌─────┐                            │          │
  │    │  │ Buf │   │ Buf │   │ Buf │                            │          │
  │    │  │  1  │   │  2  │   │  3  │                            │          │
  │    │  └─────┘   └─────┘   └─────┘                            │          │
  │    │     FREE   DEQUEUED   QUEUED                            │          │
  │    └─────────────────────────────────────────────────────────┘          │
  │         │                                 ▲                             │
  │         │                                 │                             │
  │    ┌────┴─────┐                      ┌────┴─────┐                       │
  │    │queue     │                      │release   │                       │
  │    │Buffer    │                      │Buffer    │                       │
  │    └──────────┘                      └──────────┘                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  Buffer 状态流转：
  ─────────────────────────────────────────────────────────────────────────
  FREE → DEQUEUED → QUEUED → ACQUIRED → FREE
          (App)      (App)    (SF)      (SF)

  关键操作：
  ─────────────────────────────────────────────────────────────────────────
  - dequeueBuffer：App 申请空闲 Buffer
  - queueBuffer：App 提交渲染完成的 Buffer
  - acquireBuffer：SF 获取待合成的 Buffer
  - releaseBuffer：SF 释放已合成的 Buffer
```

### 9.2 单缓冲/双缓冲/三缓冲

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    缓冲区数量对比                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  Single Buffer（单缓冲）：
  ─────────────────────────────────────────────────────────────────────────
  问题：屏幕显示和 App 渲染共用一个 Buffer
  后果：可能出现画面撕裂

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  时间轴                                                                  │
  │  ──────────────────────────────────────────────────────────────────────▶│
  │                                                                         │
  │  Buffer: [========= 显示 =========][======== 渲染 ========]             │
  │                                   ↑                                     │
  │                              可能出现撕裂                                │
  └─────────────────────────────────────────────────────────────────────────┘

  Double Buffer（双缓冲）：
  ─────────────────────────────────────────────────────────────────────────
  优点：显示和渲染使用不同 Buffer
  问题：连续超时时容易掉帧

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  Vsync 1    Vsync 2    Vsync 3    Vsync 4                              │
  │     │          │          │          │                                  │
  │     ▼          ▼          ▼          ▼                                  │
  │  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐                              │
  │  │App  │    │App  │    │     │    │     │  App 超时                    │
  │  │渲染 │    │渲染 │    │等待  │    │     │                              │
  │  │超时 │    │超时 │    │Buffer│    │     │                              │
  │  └─────┘    └─────┘    └─────┘    └─────┘                              │
  │                                                                         │
  │  SF:       合成        掉帧        合成                                 │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  Triple Buffer（三缓冲）：
  ─────────────────────────────────────────────────────────────────────────
  优点：有备用 Buffer，减少掉帧
  缺点：占用更多内存，增加延迟

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  Vsync 1    Vsync 2    Vsync 3    Vsync 4                              │
  │     │          │          │          │                                  │
  │     ▼          ▼          ▼          ▼                                  │
  │  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐                              │
  │  │App  │    │App  │    │App  │    │     │  有备用 Buffer              │
  │  │渲染 │    │渲染 │    │渲染 │    │     │  SF 可以合成上一帧          │
  │  └─────┘    └─────┘    └─────┘    └─────┘                              │
  │                                                                         │
  │  SF:       合成        合成        合成                                 │
  │            (帧1)       (帧2)       (帧3)                                │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 9.3 Triple Buffer 的作用

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Triple Buffer 的利弊                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  优点：
  ─────────────────────────────────────────────────────────────────────────
  1. 缓解掉帧
     - 连续超时时，SF 仍有 Buffer 可合成
     - 仅在缓冲饥饿场景可能减少掉帧，不保证固定收益

  2. 减少等待时间
     - 有可用槽位时可减少等待；槽位耗尽/围栏未就绪仍可能阻塞
     - 主线程可用时间变长

  3. 降低 GPU 和 SF 瓶颈
     - Buffer 可以提前进入队列
     - GPU 可以提前渲染

  缺点：
  ─────────────────────────────────────────────────────────────────────────
  1. 内存占用增加
     - 每个 Buffer 约几 MB
     - 3 个 Buffer = 3x 内存

  2. 延迟增加
     - 画面可能落后实际操作 1-2 帧
     - 对游戏等低延迟场景不友好

  掉帧判断方法：
  ─────────────────────────────────────────────────────────────────────────
  - App 端：主线程超时不一定掉帧
  - SF 端：看 expected/actual deadline 和呈现；有 Buffer 也可能因 GPU/fence/HWC 迟到
  - 需要结合 App 和 SF 两端判断
```

---

## 10. CPU 状态分析

### 10.1 CPU 核心架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CPU 核心架构类型                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  大小核架构 (big.LITTLE)：
  ─────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  骁龙 845 示例                                                          │
  │                                                                         │
  │  小核 (A55)          大核 (A75)                                         │
  │  ┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐                             │
  │  │CPU││CPU││CPU││CPU││CPU││CPU││CPU││CPU│                             │
  │  │ 0 ││ 1 ││ 2 ││ 3 ││ 4 ││ 5 ││ 6 ││ 7 │                             │
  │  │1.8G││1.8G││1.8G││1.8G││2.8G││2.8G││2.8G││2.8G│                     │
  │  └───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘                             │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  大中小核架构：
  ─────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  骁龙 855 示例                                                          │
  │                                                                         │
  │  小核 (A55)    中核 (A76)    大核 (A76+)                                 │
  │  ┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐                                   │
  │  │CPU││CPU││CPU││CPU││CPU││CPU││CPU│                                   │
  │  │ 0 ││ 1 ││ 2 ││ 3 ││ 4 ││ 5 ││ 6 │                                   │
  │  │1.8G││1.8G││1.8G││1.8G││2.4G││2.4G││2.8G│                           │
  │  └───┘└───┘└───┘└───┘└───┘└───┘└───┘                                   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  Systrace 中查看：
  ─────────────────────────────────────────────────────────────────────────
  - Kernel 区域显示 CPU 0-7
  - 不同颜色表示不同频率
  - 可以看到任务在核心间的迁移
```

### 10.2 线程 CPU 状态

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    线程 CPU 运行状态                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌───────────────────────┬─────────────────────────────────────────────────┐
  │       状态             │              说明 (Systrace 颜色)              │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Running               │ 正在 CPU 上执行 (绿色)                          │
  │                       │ 线程获得了 CPU 时间片                           │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Runnable              │ 就绪状态，等待 CPU 调度 (蓝色)                  │
  │                       │ 已获取除 CPU 外的所有资源                        │
  │                       │ 在运行队列中排队                                │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Sleep                 │ 可中断睡眠 (白色)                               │
  │ (TASK_INTERRUPTIBLE)  │ 等待某个事件（锁、IO、Binder 等）               │
  │                       │ 可以被 Signal 唤醒                              │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ Uninterruptible Sleep │ 不可中断睡眠 (橙色)                             │
  │ (TASK_UNINTERRUPTIBLE)│ 等待 IO 或内核锁                                │
  │                       │ 不能被 Signal 唤醒                              │
  │                       │ 分为 IOWait 和 Non-IOWait                       │
  └───────────────────────┴─────────────────────────────────────────────────┘

  状态转换图：
  ─────────────────────────────────────────────────────────────────────────

                    ┌──────────────┐
                    │   Running    │
                    └──────┬───────┘
                     ↑     │ 时间片用完
                     │     ▼
    唤醒        ┌────┴───────┐
     │          │  Runnable  │
     │          └────┬───────┘
     │               │ 等待资源
     │               ▼
  ┌──┴───────────────┐      ┌──────────────────┐
  │     Sleep        │      │ Uninterruptible  │
  │                  │      │     Sleep        │
  └──────────────────┘      └──────────────────┘
```

### 10.3 Runnable 状态分析

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Runnable 时间过长的原因                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  原因 1：优先级设置错误
  ─────────────────────────────────────────────────────────────────────────
  - 线程优先级过低，被其他线程抢占
  - 其他线程优先级过高

  解决方案：
  - 调整线程优先级（Process.setThreadPriority）
  - 普通应用不能任意设置 SCHED_FIFO；先限制并发并减少竞争，系统调度策略需权限和系统测试

  原因 2：绑核不合理
  ─────────────────────────────────────────────────────────────────────────
  - 多个线程绑定到同一核心
  - 该核心负载过高

  解决方案：
  - 以 CPU 簇为单位绑核，不要绑定单个核
  - 2 个大核平台减少绑大核的线程数

  原因 3：系统负载过高
  ─────────────────────────────────────────────────────────────────────────
  - 应用自身占用过多 CPU
  - 系统服务占用过高
  - 后台进程过多

  解决方案：
  - 优化应用自身代码
  - 通过 CPUSET 分组控制资源分配

  原因 4：CPU 算力限制
  ─────────────────────────────────────────────────────────────────────────
  - 温控限频
  - 省电模式
  - 低端机 CPU 性能弱

  原因 5：调度器异常
  ─────────────────────────────────────────────────────────────────────────
  - 厂商调度器 Bug
  - 锁频锁核机制问题

  分析技巧：
  ─────────────────────────────────────────────────────────────────────────
  1. wakeup from 是唤醒者不是抢占者；结合 sched_switch 和核上时间线判断竞争
  2. 检查当前核的频率和负载
  3. 检查 CPUSET 分组配置
  4. 检查线程优先级设置
```

### 10.4 Sleep 状态分析

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Sleep 时间过长的原因                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  常见原因：
  ─────────────────────────────────────────────────────────────────────────

  1. Binder 操作
     ─────────────────────────────────────────────────────────────────────
     - 跨进程调用耗时
     - 远端 Binder 执行慢
     - 锁竞争

  2. Java/Native 锁等待
     ─────────────────────────────────────────────────────────────────────
     - synchronized 锁竞争
     - ReentrantLock 竞争
     - futex 锁等待

  3. 主动等待
     ─────────────────────────────────────────────────────────────────────
     - Object.wait()
     - Condition.await()
     - Thread.sleep()

  4. 等待 GPU
     ─────────────────────────────────────────────────────────────────────
     - GPU 渲染任务重
     - GPU 频率低
     - 等待 GPU fence

  分析方法：
  ─────────────────────────────────────────────────────────────────────────

  1. 通过 wakeup from tid 查看唤醒线程
     - Systrace 中选中 Sleep 段
     - 查看 wakeup from 信息

  2. 使用 Simpleperf 还原代码执行流
     - 分析具体是什么操作导致睡眠

  3. 在 Systrace 中寻找时间对齐的事件
     - 找到相关的 Binder 调用
     - 找到相关的锁等待
```

### 10.5 Uninterruptible Sleep 分析

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Uninterruptible Sleep 分析                              │
└─────────────────────────────────────────────────────────────────────────────┘

  IOWait 常见原因：
  ─────────────────────────────────────────────────────────────────────────

  1. 主动 IO 操作
     - 频繁的文件读写
     - 数据库操作
     - 多个应用同时 IO

  2. 低内存导致 IO 变多
     - PageCache 不足
     - 频繁的内存回收
     - Swap 读取

  3. 器件性能差
     - 磁盘碎片化
     - 器件老化
     - 剩余空间少

  Non-IOWait 常见原因：
  ─────────────────────────────────────────────────────────────────────────

  1. 低内存导致等待
     - 内存回收慢路径

  2. Binder 等待
     - 高负载时 Binder 内部锁竞争

  3. 内核锁等待
     - mmap 锁竞争
     - 内存管理锁

  Block Reason 分析：
  ─────────────────────────────────────────────────────────────────────────

  Systrace 中会显示 Block Reason：
  sched_blocked_reason: pid=xxx iowait=0/1 caller=函数名

  - iowait=1：IO 等待
  - iowait=0：未标记 IO wait，不能单独证明是内核锁
  - caller：导致睡眠的内核函数

  常见 Block Reason：
  ┌───────────────────────────┬─────────────────────────────────────────────┐
  │       函数名               │              原因                          │
  ├───────────────────────────┼─────────────────────────────────────────────┤
  │ get_user_pages_fast       │ 内存页面锁定                                │
  │ __wait_on_bit             │ IO 等待                                     │
  │ mutex_lock                │ 内核 mutex 锁                               │
  │ down_read                 │ 读写锁                                      │
  │ shrink_inactive_list      │ 内存回收                                    │
  └───────────────────────────┴─────────────────────────────────────────────┘
```

---

## 11. Binder 与锁竞争

### 11.1 Binder 通信机制

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Binder 通信流程                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  App 进程                        SystemServer 进程
      │                                  │
      │  1. Binder.transact()            │
      │                                  │
      │  2. 写入 Parcel                  │
      │                                  │
      │  3. ioctl(BINDER_WRITE_READ)     │
      │     ↓                            │
      │  Binder Driver                   │
      │     ↓                            │
      │                          4. 唤醒目标线程
      │                                  │
      │                          5. 执行 onTransact
      │                                  │
      │                          6. 写入回复 Parcel
      │                                  │
      │     ↑                            │
      │  Binder Driver                   │
      │     ↑                            │
      │  7. 返回结果                     │
      │                                  │

  Systrace 中查看 Binder：
  ─────────────────────────────────────────────────────────────────────────
  - 勾选 Flow Events 可以看到 Binder 调用链路
  - 点击 Binder 块可以看到详细信息
  - 包括调用方、被调用方、耗时等
```

### 11.2 锁竞争分析

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Systrace 中的锁信息                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  锁竞争信息格式：
  ─────────────────────────────────────────────────────────────────────────

  monitor contention with owner Binder:1605_B (4667) 
  at void com.android.server.wm.ActivityTaskManagerService.activityPaused(...)
  (ActivityTaskManagerService.java:1733) 
  waiters=2 
  blocking from android.app.ActivityManager$StackInfo 
  com.android.server.wm.ActivityTaskManagerService.getFocusedStackInfo()
  (ActivityTaskManagerService.java:2064)

  信息解读：
  ─────────────────────────────────────────────────────────────────────────

  第一段（锁持有方）：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ monitor contention with owner Binder:1605_B (4667)                      │
  │                                                                         │
  │ 含义：锁正在被 Binder:1605_B 线程（TID=4667）持有                        │
  │                                                                         │
  │ at void ...ActivityTaskManagerService.activityPaused(...)              │
  │                                                                         │
  │ 含义：持有锁的线程正在执行 activityPaused 方法                           │
  │                                                                         │
  │ waiters=2                                                               │
  │                                                                         │
  │ 含义：锁池中已有 2 个等待者                                              │
  └─────────────────────────────────────────────────────────────────────────┘

  第二段（锁等待方）：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ blocking from ...ActivityTaskManagerService.getFocusedStackInfo()      │
  │                                                                         │
  │ 含义：当前线程在执行 getFocusedStackInfo 时被阻塞                        │
  └─────────────────────────────────────────────────────────────────────────┘

  锁等待分析流程：
  ─────────────────────────────────────────────────────────────────────────

  1. 找到锁持有线程
     - 查看 Owner 线程的执行情况
     - 确定持有锁的时间

  2. 查看等待队列
     - waiters=N 表示前面有 N 个等待者
     - 总等待数 = N + 1

  3. 分析锁释放后流程
     - 查看唤醒信息
     - 确认唤醒顺序

  常见的严重锁竞争：
  ─────────────────────────────────────────────────────────────────────────
  - mGlobalLock (ActivityTaskManagerService)
  - mServiceLock (ActivityManagerService)
  - mWindowMap (WindowManagerService)

  这些锁竞争严重时 waiters 可能达到 7-10 个
```

---

## 12. 卡顿分析实战

### 12.1 卡顿定义与原理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    卡顿的定义                                               │
└─────────────────────────────────────────────────────────────────────────────┘

  卡顿定义：
  ─────────────────────────────────────────────────────────────────────────
  稳定帧率输出的画面出现一帧或多帧没有绘制

  从三个角度定义：
  ─────────────────────────────────────────────────────────────────────────

  1. 现象角度：
     - App 连续动画或滑动时
     - 连续 2 帧或以上画面没有变化

  2. SurfaceFlinger 角度：
     - Vsync 到来时
     - App 没有可合成的 Buffer

  3. App 角度：
     - 渲染线程在一个 Vsync 周期内
     - 没有 queueBuffer 到 BufferQueue

  逻辑卡顿：
  ─────────────────────────────────────────────────────────────────────────
  - 渲染流程正常，有 Buffer 可合成
  - 但 Buffer 内容与上一帧相同
  - 用户看到连续相同画面

  原因：
  - 动画计算基于当前时间而非 Vsync 时间
  - 掉帧后动画变化不均匀
```

### 12.2 卡顿原因分类

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    卡顿原因分类                                             │
└─────────────────────────────────────────────────────────────────────────────┘

  应用层原因：
  ─────────────────────────────────────────────────────────────────────────

  ┌───────────────────────────┬─────────────────────────────────────────────┐
  │       原因                 │              分析方法                       │
  ├───────────────────────────┼─────────────────────────────────────────────┤
  │ 主线程耗时操作             │ 检查 doFrame 中各阶段耗时                  │
  │ - IO 操作                 │ - Input 耗时                               │
  │ - 复杂计算                │ - Animation 耗时                           │
  │ - 同步锁等待              │ - Traversal 耗时                           │
  ├───────────────────────────┼─────────────────────────────────────────────┤
  │ 渲染线程耗时              │ 检查 RenderThread 执行情况                 │
  │ - GPU 渲染重              │ - dequeueBuffer 耗时                       │
  │ - 复杂 Shader             │ - OpenGL 调用耗时                          │
  │ - 大量绘制调用            │ - queueBuffer 耗时                         │
  ├───────────────────────────┼─────────────────────────────────────────────┤
  │ 布局复杂                  │ 检查 measure/layout/draw 耗时              │
  │ - 层级过深                │ - 使用 Hierarchy Viewer                    │
  │ - 过度绘制                │ - 开启 GPU 过度绘制调试                    │
  └───────────────────────────┴─────────────────────────────────────────────┘

  系统层原因：
  ─────────────────────────────────────────────────────────────────────────

  ┌───────────────────────────┬─────────────────────────────────────────────┐
  │       原因                 │              分析方法                       │
  ├───────────────────────────┼─────────────────────────────────────────────┤
  │ SystemServer 锁竞争        │ 检查 SystemServer 中锁等待                 │
  │ - AMS/WMS 锁               │ - 查看锁竞争信息                            │
  │ - Binder 繁忙              │ - 分析 Binder 调用链路                      │
  ├───────────────────────────┼─────────────────────────────────────────────┤
  │ SurfaceFlinger 繁忙        │ 检查 SF 主线程执行情况                      │
  │ - 合成耗时                 │ - 合成操作耗时                              │
  │ - 截图等操作               │ - HWC 交互耗时                              │
  ├───────────────────────────┼─────────────────────────────────────────────┤
  │ CPU 调度问题               │ 检查 Kernel 区域                            │
  │ - 频率低                   │ - CPU 频率变化                              │
  │ - 跑在小核                 │ - 线程在哪个核运行                          │
  │ - 负载高                   │ - Runnable 时间                             │
  ├───────────────────────────┼─────────────────────────────────────────────┤
  │ 内存压力                   │ 检查内存相关操作                            │
  │ - GC 频繁                  │ - GC 耗时                                   │
  │ - 内存回收                 │ - 内存分配耗时                              │
  │ - 低内存                   │ - Uninterruptible Sleep                    │
  └───────────────────────────┴─────────────────────────────────────────────┘
```

### 12.3 分析流程与方法

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Systrace 分析流程                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  Step 1：定位掉帧位置
  ─────────────────────────────────────────────────────────────────────────
  - 在 Systrace 中找到绿色帧（正常帧）
  - 找到帧之间间隔超过 16.6ms 的位置
  - 选中该帧，查看详细信息

  Step 2：分析 App 端
  ─────────────────────────────────────────────────────────────────────────
  - 检查主线程 (UI Thread) 执行情况
  - 检查渲染线程 (RenderThread) 执行情况
  - 找到耗时最长的部分

  Step 3：分析系统端
  ─────────────────────────────────────────────────────────────────────────
  - 检查 SystemServer 是否有锁竞争
  - 检查 SurfaceFlinger 合成情况
  - 检查 CPU 调度和频率

  Step 4：深入分析
  ─────────────────────────────────────────────────────────────────────────
  - 使用 TraceView/MethodTrace 分析具体方法
  - 使用 Simpleperf 分析 Native 代码
  - 结合代码逻辑定位根因

  快捷键（Systrace/Perfetto）：
  ─────────────────────────────────────────────────────────────────────────

  ┌─────────────┬───────────────────────────────────────────────────────────┐
  │    快捷键    │                       功能                               │
  ├─────────────┼───────────────────────────────────────────────────────────┤
  │ W           │ 放大                                                      │
  │ S           │ 缩小                                                      │
  │ A           │ 左移                                                      │
  │ D           │ 右移                                                      │
  │ M           │ 高亮选中区域                                              │
  │ 1           │ 选择模式                                                  │
  │ 2           │ 拖动模式                                                  │
  │ 3           │ 缩放模式                                                  │
  │ 4           │ 时间测量模式                                              │
  │ ?           │ 帮助                                                      │
  └─────────────┴───────────────────────────────────────────────────────────┘
```

---

### 12.4 Perfetto 完整采集与 SQL 归因

使用 2.1 节配置采集；在同步 Feed.load 打点后，执行以下 SQL。

```sql
SELECT name, value, severity FROM stats WHERE value != 0 AND severity != 'info';
SELECT COUNT(*) AS sched_count FROM sched;
SELECT COUNT(*) AS frame_count FROM actual_frame_timeline_slice;
SELECT s.id, s.name, s.ts, ROUND(s.dur / 1e6, 3) AS wall_ms,
       t.name AS thread_name, p.name AS process_name
FROM slice s JOIN thread_track tt ON tt.id = s.track_id
JOIN thread t ON t.utid = tt.utid JOIN process p ON p.upid = t.upid
WHERE p.name = 'com.example.app' AND s.dur > 0
ORDER BY s.dur DESC LIMIT 50;
WITH target AS (
 SELECT s.id, s.ts, s.dur, tt.utid FROM slice s
 JOIN thread_track tt ON tt.id = s.track_id
 JOIN thread t ON t.utid = tt.utid JOIN process p ON p.upid = t.upid
 WHERE p.name = 'com.example.app' AND s.name = 'Feed.load' AND s.dur > 0
)
SELECT target.id, st.state,
 ROUND(SUM(MIN(target.ts + target.dur, st.ts + st.dur) -
           MAX(target.ts, st.ts)) / 1e6, 3) AS overlap_ms
FROM target JOIN thread_state st ON st.utid = target.utid
 AND st.dur > 0 AND st.ts < target.ts + target.dur
 AND st.ts + st.dur > target.ts
GROUP BY target.id, st.state ORDER BY target.id, overlap_ms DESC;
SELECT a.id, p.name, a.layer_name, a.surface_frame_token,
       a.jank_type, a.present_type, ROUND(a.dur / 1e6, 3) AS actual_ms
FROM actual_frame_timeline_slice a JOIN process p ON p.upid = a.upid
WHERE p.name = 'com.example.app' AND a.dur > 0 ORDER BY a.ts;
```

空结果不是没有卡顿。同步 slice 父子不可累加；状态时长必须裁剪到 section 的交叠区间。FrameTimeline 配对 expected/actual 看期限，surface/display 帧并非一对一；跨线程/协程 async slice 用 flow 关联，不能强制映射单个 thread_track。

来源：[Perfetto CLI](https://perfetto.dev/docs/reference/perfetto-cli)、[SQL tables](https://perfetto.dev/docs/analysis/sql-tables)、[FrameTimeline](https://perfetto.dev/docs/data-sources/frametimeline)。


## 13. APM 监控方案

### 13.1 FrameCallback 监控

该循环测量回调频率，不是实际显示新帧 FPS，也不等同 jank rate；后台/页面停止时必须 stop，避免持续请求 Vsync。启动要防重复注册并重置计数。显示性能以 FrameTimeline/JankStats/FrameMetrics 配合判断。

```kotlin
// ==================== 使用 Choreographer.FrameCallback 监控 ====================

class FPSCallback : Choreographer.FrameCallback {
    
    private var lastFrameTimeNanos: Long = 0
    private var frameCount: Int = 0
    private var fps: Double = 0.0
    
    override fun doFrame(frameTimeNanos: Long) {
        if (lastFrameTimeNanos == 0L) {
            lastFrameTimeNanos = frameTimeNanos
            Choreographer.getInstance().postFrameCallback(this)
            return
        }
        
        frameCount++
        
        val elapsedNanos = frameTimeNanos - lastFrameTimeNanos
        val elapsedSeconds = elapsedNanos / 1_000_000_000.0
        
        if (elapsedSeconds >= 1.0) {
            fps = frameCount / elapsedSeconds
            Log.d("FPS", "FPS: $fps")
            
            frameCount = 0
            lastFrameTimeNanos = frameTimeNanos
        }
        
        // 继续监听下一帧
        Choreographer.getInstance().postFrameCallback(this)
    }
    
    fun start() {
        Choreographer.getInstance().removeFrameCallback(this)
        lastFrameTimeNanos = 0
        frameCount = 0
        Choreographer.getInstance().postFrameCallback(this)
    }
    
    fun stop() {
        Choreographer.getInstance().removeFrameCallback(this)
    }
}

// 使用
val fpsCallback = FPSCallback()
fpsCallback.start()

// 停止
fpsCallback.stop()
```

### 13.2 FrameInfo 监控

```bash
# ==================== 使用 dumpsys gfxinfo ====================

# 获取帧信息
adb shell dumpsys gfxinfo <package_name>

# 获取详细帧统计
adb shell dumpsys gfxinfo <package_name> framestats

# 输出示例：
# Total frames rendered: 1562
# Janky frames: 361 (23.11%)
# 50th percentile: 6ms
# 90th percentile: 23ms
# 95th percentile: 36ms
# 99th percentile: 101ms
# Number Missed Vsync: 33
# Number High input latency: 683
# Number Slow UI thread: 273
# Number Slow bitmap uploads: 8
# Number Slow issue draw commands: 18
```

```kotlin
// ==================== 代码中获取帧信息 ====================

// Android 7.0+ 可以通过 Window.OnFrameMetricsAvailableListener 获取
class FrameMetricsHelper(private val activity: Activity) {
    
    private var frameMetricsListener: Window.OnFrameMetricsAvailableListener? = null
    
    fun start() {
        frameMetricsListener = Window.OnFrameMetricsAvailableListener { _, frameMetrics, _ ->
            val metrics = FrameMetrics(frameMetrics)
            
            // 获取各阶段耗时（纳秒）
            val totalDuration = metrics.getMetric(FrameMetrics.TOTAL_DURATION)
            val inputDuration = metrics.getMetric(FrameMetrics.INPUT_HANDLING_DURATION)
            val layoutDuration = metrics.getMetric(FrameMetrics.LAYOUT_MEASURE_DURATION)
            val drawDuration = metrics.getMetric(FrameMetrics.DRAW_DURATION)
            val syncDuration = metrics.getMetric(FrameMetrics.SYNC_DURATION)
            val commandIssueDuration = metrics.getMetric(FrameMetrics.COMMAND_ISSUE_DURATION)
                val gpuDuration = if (Build.VERSION.SDK_INT >= 31)
                    metrics.getMetric(FrameMetrics.GPU_DURATION) else -1L
            
            // 检测掉帧
            val frameTimeMs = totalDuration / 1_000_000
            if (frameTimeMs > 16.6) {
                Log.w("FrameMetrics", "Dropped frame: ${frameTimeMs}ms")
                Log.d("FrameMetrics", "Input: ${inputDuration/1_000_000}ms")
                Log.d("FrameMetrics", "Layout: ${layoutDuration/1_000_000}ms")
                Log.d("FrameMetrics", "Draw: ${drawDuration/1_000_000}ms")
                Log.d("FrameMetrics", "Sync: ${syncDuration/1_000_000}ms")
                Log.d("FrameMetrics", "GPU: ${gpuDuration/1_000_000}ms")
            }
        }
        
        activity.window.addOnFrameMetricsAvailableListener(
            frameMetricsListener,
            Handler(Looper.getMainLooper())
        )
    }
    
    fun stop() {
        frameMetricsListener?.let {
            activity.window.removeOnFrameMetricsAvailableListener(it)
        }
    }
}

// 使用
val frameMetricsHelper = FrameMetricsHelper(this)
frameMetricsHelper.start()
```

### 13.3 Looper Printer 监控

```kotlin
// ==================== 使用 Looper Printer 监控主线程卡顿 ====================

class BlockDetector(private val blockThreshold: Long = 1000) {
    
    private var startTime: Long = 0
    private var isPrinting = false
    
    private val printer = Printer { x ->
        if (x.startsWith(">>>>> Dispatching to")) {
            startTime = SystemClock.uptimeMillis()
            isPrinting = true
        } else if (x.startsWith("<<<<< Finished to")) {
            isPrinting = false
            val endTime = SystemClock.uptimeMillis()
            val duration = endTime - startTime
            
            if (duration > blockThreshold) {
                // 检测到卡顿
                Log.w("BlockDetector", "Block detected: ${duration}ms")
                
                // 消息结束后当前栈已不是阻塞现场，只记录耗时；阻塞栈需独立 watchdog 在阻塞期间采样
                val stackTrace = emptyArray<StackTraceElement>() // 不伪造为阻塞现场
                Log.w("BlockDetector", stackTrace.joinToString("\n"))
            }
        }
    }
    
    fun start() {
        Looper.getMainLooper().setMessageLogging(printer)
    }
    
    fun stop() {
        Looper.getMainLooper().setMessageLogging(null)
    }
}

// 使用
val blockDetector = BlockDetector(blockThreshold = 500) // 500ms 阈值
blockDetector.start()
```

---

## 14. 常见问题

### 14.1 Systrace 文件无法在 Chrome 打开

```text
问题：
─────────────────────────────────────────────────────────────────────────
Chrome 打开 Systrace 文件显示空白或报错

原因：
─────────────────────────────────────────────────────────────────────────
1. Chrome 版本过旧，不支持 Systrace 格式
2. 文件过大（超过 300MB）
3. 采集时出现错误

解决方案：
─────────────────────────────────────────────────────────────────────────
1. 更新 Chrome 到最新版本
2. 减少采集时长或 Tag 数量
3. 使用 Perfetto UI (https://ui.perfetto.dev/) 替代
4. 使用 Perfetto 命令行工具分析大文件：
   
   # 进入 Trace Processor SQL shell，不会自动导出 SQLite 文件
   trace_processor_shell trace_file
   
   # 执行 SQL 查询
   trace_processor_shell -q query.sql trace_file
```

### 14.2 采集不到应用 Trace

```text
问题：
─────────────────────────────────────────────────────────────────────────
Systrace 中看不到应用的 Trace 信息

原因：
─────────────────────────────────────────────────────────────────────────
1. 没有使用 -a 参数指定应用包名
2. 应用没有使用 Trace API
3. 采集的 Tag 不包含应用相关 Tag

解决方案：
─────────────────────────────────────────────────────────────────────────
1. 使用 -a 参数：
   
   python systrace.py -a com.example.app -t 10 -o trace.html

2. 在代码中添加 Trace：
   
   Trace.beginSection("MyOperation")
   // ... 操作
   Trace.endSection()

3. 添加 view Tag：
   
   python systrace.py -a com.example.app view gfx -t 10 -o trace.html
```

### 14.3 如何判断是应用问题还是系统问题

下面 10/6/4ms 等只是 60Hz 教学预算，不是所有设备健康阈值。长 dequeue/Binder/Runnable 可能由应用自己的并发、占槽或远端逻辑造成，不能单凭所在线程判定系统责任。按 deadline、唤醒/锁链和对照采样归因。

```text
判断方法：
─────────────────────────────────────────────────────────────────────────

1. 查看 App 端：
   ─────────────────────────────────────────────────────────────────────
   - 主线程执行时间是否正常（< 10ms）
   - RenderThread 执行时间是否正常（< 6ms）
   - dequeueBuffer/queueBuffer 是否耗时

2. 查看 SystemServer：
   ─────────────────────────────────────────────────────────────────────
   - 是否有大量锁竞争
   - Binder 调用是否耗时
   - AMS/WMS 操作是否耗时

3. 查看 SurfaceFlinger：
   ─────────────────────────────────────────────────────────────────────
   - 合成操作是否耗时
   - 是否有 Buffer 可合成

4. 查看 CPU：
   ─────────────────────────────────────────────────────────────────────
   - CPU 频率是否正常
   - 线程是否跑在正确的核上
   - 是否有大量 Runnable 等待

快速判断：
─────────────────────────────────────────────────────────────────────────

┌─────────────────────────────┬───────────────────────────────────────────┐
│        现象                  │              可能原因                     │
├─────────────────────────────┼───────────────────────────────────────────┤
│ 主线程耗时 > 10ms            │ 应用问题：主线程有耗时操作                │
├─────────────────────────────┼───────────────────────────────────────────┤
│ RenderThread 耗时 > 6ms      │ 应用问题：渲染复杂                        │
├─────────────────────────────┼───────────────────────────────────────────┤
│ dequeueBuffer 耗时           │ 系统问题：SF 繁忙或 Buffer 不足           │
├─────────────────────────────┼───────────────────────────────────────────┤
│ Binder 调用耗时              │ 系统问题：锁竞争或远端执行慢              │
├─────────────────────────────┼───────────────────────────────────────────┤
│ 大量 Runnable 等待           │ 系统问题：CPU 负载高或调度问题            │
├─────────────────────────────┼───────────────────────────────────────────┤
│ CPU 频率低                   │ 系统问题：温控或省电策略                  │
└─────────────────────────────┴───────────────────────────────────────────┘
```

---

## 15. 知识体系总结

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Systrace 知识体系总结                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │    Systrace     │
                           │   性能分析      │
                           └────────┬────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
  ┌───────────┐              ┌───────────┐              ┌───────────┐
  │  基础知识  │              │  系统机制  │              │  实战分析  │
  │           │              │           │              │           │
  │ - 使用方法│              │ - Vsync   │              │ - 卡顿分析│
  │ - 参数配置│              │ - Choreographer│         │ - CPU状态 │
  │ - 添加Trace│             │ - 渲染线程│              │ - 锁竞争  │
  └───────────┘              │ - BufferQueue│            │ - APM监控 │
                             │ - Input    │              └───────────┘
                             │ - SF/SS    │
                             └───────────┘

  核心流程：
  ─────────────────────────────────────────────────────────────────────────
  
  Vsync → Choreographer.doFrame() → Input → Animation → Traversal
    │                                                           │
    │                      MainThread                           │
    │   ┌─────────────────────────────────────────────────────┐ │
    │   │ measure → layout → draw (DisplayList)               │ │
    │   └─────────────────────────────────────────────────────┘ │
    │                                                           │
    │                      RenderThread                         │
    │   ┌─────────────────────────────────────────────────────┐ │
    │   │ dequeueBuffer → GPU渲染 → queueBuffer               │ │
    │   └─────────────────────────────────────────────────────┘ │
    │                                                           │
    ▼                                                           ▼
  SurfaceFlinger commit/composite 调度
    │
    │   ┌─────────────────────────────────────────────────────┐
    │   │ acquireBuffer → 合成(GPU/HWC) → present             │
    │   └─────────────────────────────────────────────────────┘
    │
    ▼
  显示到屏幕

  关键指标：
  ─────────────────────────────────────────────────────────────────────────

  ┌───────────────────────┬─────────────────────────────────────────────────┐
  │       指标             │              健康值                           │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 主线程 doFrame         │ < 10ms                                         │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ RenderThread          │ < 6ms                                          │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ dequeueBuffer         │ < 1ms                                          │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ SurfaceFlinger 合成   │ < 4ms                                          │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ 掉帧率                 │ < 5%                                           │
  ├───────────────────────┼─────────────────────────────────────────────────┤
  │ FPS                   │ 稳定在 60（或 90/120）                          │
  └───────────────────────┴─────────────────────────────────────────────────┘

  分析技巧：
  ─────────────────────────────────────────────────────────────────────────
  1. 先看整体，再看局部
  2. App 端和系统端结合分析
  3. 关注时间对齐的事件
  4. 利用唤醒信息追踪调用链
  5. 结合代码理解 Trace 信息

  参考资料：
  ─────────────────────────────────────────────────────────────────────────
  - 官方文档：https://source.android.google.cn/devices/graphics
  - Perfetto：https://perfetto.dev/
  - Android Performance 博客：https://www.androidperformance.com/
```

---

> 作者：OpenClaw | 日期：2026-03-09
> 技术基线：AOSP `android-17.0.0_r1`；旧 Systrace 保留为历史工具说明，Android 17 使用 Perfetto。
> 
> 参考文档：https://www.androidperformance.com/2019/05/28/Android-Systrace-About/
固定源码：[Choreographer.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/Choreographer.java) 的 doFrame/doCallbacks；[BLASTBufferQueue.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/gui/BLASTBufferQueue.cpp) 的 processNextBufferLocked；[SurfaceFlinger.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/surfaceflinger/SurfaceFlinger.cpp) 的 commit/composite。
