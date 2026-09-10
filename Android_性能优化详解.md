# Android 性能优化完全指南

> 作者：OpenClaw  
> 日期：2026-03-08
> 技术基线：AOSP `android-17.0.0_r1`。业务收益数字是示例，不是跨设备保证。

---

## 目录

- [1. 性能优化概述](#1-性能优化概述)
  - [1.1 优化维度](#11-优化维度)
  - [1.2 性能金字塔](#12-性能金字塔)
  - [1.3 资深工程师的五个层次](#13-资深工程师的五个层次)
  - [1.4 性能指标体系：分位值思维](#14-性能指标体系分位值思维)
- [2. 深度解析——资深工程师的性能优化观](#2-深度解析资深工程师的性能优化观)
  - [2.1 性能优化的本质](#21-性能优化的本质)
  - [2.2 性能优化的黄金法则](#22-性能优化的黄金法则)
  - [2.3 线上 APM 监控体系](#23-线上-apm-监控体系)
  - [2.4 性能劣化归因方法论](#24-性能劣化归因方法论)
  - [2.5 Baseline Profiles 与编译优化](#25-baseline-profiles-与编译优化)
- [3. 启动优化](#3-启动优化)
  - [3.1 启动类型详解](#31-启动类型详解)
  - [3.2 冷启动流程源码分析](#32-冷启动流程源码分析)
  - [3.3 启动时间测量](#33-启动时间测量)
  - [3.4 启动优化策略](#34-启动优化策略)
  - [3.5 App Startup 库](#35-app-startup-库)
  - [3.6 启动器框架完整实现](#36-启动器框架完整实现)
  - [3.7 ContentProvider 滥用治理](#37-contentprovider-滥用治理)
  - [3.8 首帧优化](#38-首帧优化)
  - [3.9 启动优化工具](#39-启动优化工具)
- [4. UI 渲染优化](#4-ui-渲染优化)
  - [4.1 渲染原理](#41-渲染原理)
  - [4.2 16ms 法则](#42-16ms-法则)
  - [4.3 VSync 与 Choreographer](#43-vsync-与-choreographer)
  - [4.4 双缓冲与三缓冲](#44-双缓冲与三缓冲)
  - [4.5 渲染性能分析](#45-渲染性能分析)
  - [4.6 渲染优化策略](#46-渲染优化策略)
  - [4.7 RecyclerView 性能优化专题](#47-recyclerview-性能优化专题)
  - [4.8 自定义 View 性能优化](#48-自定义-view-性能优化)
- [5. 内存优化](#5-内存优化)
  - [5.1 Java 运行时数据区与 ART](#51-java-运行时数据区与-art)
  - [5.2 Android 内存管理](#52-android-内存管理)
  - [5.3 内存泄漏检测](#53-内存泄漏检测)
  - [5.4 内存优化策略](#54-内存优化策略)
  - [5.5 OOM 分析与处理](#55-oom-分析与处理)
- [6. 线程与并发优化](#6-线程与并发优化)
  - [6.1 线程池调优](#61-线程池调优)
  - [6.2 协程调度优化](#62-协程调度优化)
  - [6.3 锁优化策略](#63-锁优化策略)
  - [5.6 内存抖动检测与治理](#56-内存抖动检测与治理)
  - [5.7 Bitmap 内存管理演进](#57-bitmap-内存管理演进)
  - [5.8 onTrimMemory 与主动内存预算](#58-ontrimmemory-与主动内存预算)
  - [5.9 Native 内存泄漏排查](#59-native-内存泄漏排查)
- [7. 电量优化](#7-电量优化)
  - [7.1 电量消耗分析](#71-电量消耗分析)
  - [7.2 电量优化策略](#72-电量优化策略)
  - [7.4 Doze 模式与 App Standby](#74-doze-模式与-app-standby)
  - [7.3 Battery Historian 使用教程](#73-battery-historian-使用教程)
  - [7.5 GPS 精度分级策略](#75-gps-精度分级策略)
  - [7.6 Android 12+ 前台服务限制](#76-android-12-前台服务限制)
  - [7.7 WorkManager 最佳实践](#77-workmanager-最佳实践)
- [8. 网络优化](#8-网络优化)
  - [8.1 网络请求优化](#81-网络请求优化)
  - [8.2 HTTP/2 与 OkHttp 配置](#82-http2-与-okhttp-配置)
  - [8.3 弱网策略](#83-弱网策略)
  - [8.4 网络状态感知](#84-网络状态感知)
  - [8.5 图片加载优化](#85-图片加载优化)
  - [8.6 网络缓存策略](#86-网络缓存策略)
- [9. APK 体积优化](#9-apk-体积优化)
  - [9.1 体积分析](#91-体积分析)
  - [9.2 R8 完整瘦身策略](#92-r8-完整瘦身策略)
  - [9.3 资源优化](#93-资源优化)
  - [9.4 So 动态库优化](#94-so-动态库优化)
- [10. 性能分析工具链](#10-性能分析工具链)
  - [10.2 CPU Profiler 高级用法](#102-cpu-profiler-高级用法)
  - [10.3 Memory Profiler 高级用法](#103-memory-profiler-高级用法)
  - [10.4 Layout Inspector](#104-layout-inspector)
  - [10.1 Perfetto 深度使用](#101-perfetto-深度使用)
  - [10.5 线上监控工具](#105-线上监控工具)
  - [10.6 Simpleperf（Native CPU Profiling）](#106-simpleperfnative-cpu-profiling)
  - [10.7 线上性能监控矩阵](#107-线上性能监控矩阵)
  - [10.8 从 Perfetto 时间线到优化决策](#108-从-perfetto-时间线到优化决策)
- [11. 面试常见问题](#11-面试常见问题)
  - [11.1 启动优化问题](#111-启动优化问题)
  - [11.2 渲染优化问题](#112-渲染优化问题)
  - [11.3 内存优化问题](#113-内存优化问题)
  - [11.4 综合问题](#114-综合问题)
- [12. 总结](#12-总结)

---

## 1. 性能优化概述

### 1.1 优化维度

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 性能优化维度                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────┬───────────────────────────────────────────────────────┐
│     优化维度       │                      关键指标                        │
├───────────────────┼───────────────────────────────────────────────────────┤
│     启动优化       │ 冷启动 < 5s，热启动 < 1.5s，温启动 < 2s             │
├───────────────────┼───────────────────────────────────────────────────────┤
│   UI 渲染优化      │ 60fps (16.6ms/帧)，避免卡顿                         │
├───────────────────┼───────────────────────────────────────────────────────┤
│     内存优化       │ OOM 率 < 0.1%，内存泄漏率 = 0                        │
├───────────────────┼───────────────────────────────────────────────────────┤
│     电量优化       │ 待机功耗 < 50mAh/天，后台功耗最小化                  │
├───────────────────┼───────────────────────────────────────────────────────┤
│     网络优化       │ 请求成功率 > 99%，响应时间 < 500ms                   │
├───────────────────┼───────────────────────────────────────────────────────┤
│   APK 体积优化     │ 体积 < 20MB (普通应用)，< 50MB (大型应用)           │
└───────────────────┴───────────────────────────────────────────────────────┘
```

### 1.2 性能金字塔

```text
                        ┌───────────┐
                        │  用户体验  │
                        └─────┬─────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
          ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
          │   流畅    │ │   稳定    │ │   省电    │
          └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
                │             │             │
                └─────────────┼─────────────┘
                              │
                        ┌─────▼─────┐
                        │   启动快   │
                        └───────────┘
```

### 1.3 资深工程师的五个层次

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 资深工程师看待性能优化的五个层次                             │
└─────────────────────────────────────────────────────────────────────────────┘

层次 5 ┌──────────────────────────────────────────────────────────────────────┐
       │  架构级预防：在架构设计阶段就考虑性能，从根源避免问题              │
       │  - 启动器框架、无锁化设计、协程调度隔离                          │
       └──────────────────────────────────────────────────────────────────────┘
           ▲
层次 4 ┌───┴──────────────────────────────────────────────────────────────────┐
       │  优化治理：定位到根因后，进行精准优化                             │
       │  - 异步化、缓存策略、内存复用、延迟加载                          │
       └──────────────────────────────────────────────────────────────────────┘
           ▲
层次 3 ┌───┴──────────────────────────────────────────────────────────────────┐
       │  精准定位：用工具找到性能瓶颈的精确位置                           │
       │  - Perfetto、CPU Profiler、Memory Profiler、heapprofd            │
       └──────────────────────────────────────────────────────────────────────┘
           ▲
层次 2 ┌───┴──────────────────────────────────────────────────────────────────┐
       │  数据监控：建立线上+线下性能监控体系                              │
       │  - Matrix、Firebase Performance、自研 APM                       │
       └──────────────────────────────────────────────────────────────────────┘
           ▲
层次 1 ┌───┴──────────────────────────────────────────────────────────────────┐
       │  指标定义：建立可量化的性能指标                                   │
       │  - 冷启动 P90 < 3s、低帧率尾部 P1 > 50fps、OOM率 < 0.05%            │
       └──────────────────────────────────────────────────────────────────────┘

初级工程师只停留在第4层（优化），不懂数据驱动。
资深工程师从第1层开始，自下而上构建完整的性能优化闭环。
```

### 1.4 性能指标体系：分位值思维

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    为什么平均值不靠谱？分位值思维                            │
└─────────────────────────────────────────────────────────────────────────────┘

场景：你的 App 冷启动数据
  - 100 次测量中，90 次 1.5s，10 次 12s

平均值 = (90 × 1.5 + 10 × 12) / 100 = 2.55s  ← 看起来还行
P50    = 1.5s                                   ← 一半用户体验不错
P90    = 1.5s                                   ← 90% 用户还行
P99    = 12s                                    ← 1% 用户体验极差！← 这才是重点

关键分位值定义：
┌──────────┬────────────────────────────────────────────────────────────────┐
│  指标    │  含义                                                          │
├──────────┼────────────────────────────────────────────────────────────────┤
│  P50     │  中位数，50% 的用户体验在这个值以内                           │
│  P90     │  90% 的用户体验在这个值以内（通常作为达标线）                 │
│  P99     │  99% 的用户体验在这个值以内（通常作为红线）                   │
│  P99.9   │  极端值，通常对应低端机或极端场景（需要专项治理）             │
└──────────┴────────────────────────────────────────────────────────────────┘

冷启动指标分类：
┌──────────────────┬────────────────────────┬───────────────────────────────┐
│  指标名称        │  全称                  │  含义                         │
├──────────────────┼────────────────────────┼───────────────────────────────┤
│  TTID            │  Time To Initial       │  首帧显示时间（窗口可见）     │
│                  │  Display               │  = 用户看到第一个画面的时间   │
├──────────────────┼────────────────────────┼───────────────────────────────┤
│  TTFD            │  Time To Full          │  完全可交互时间               │
│                  │  Display               │  = 数据加载完、列表可滑动     │
└──────────────────┴────────────────────────┴───────────────────────────────┘

> 资深工程师不只看平均值，而是按设备档位（高端/中端/低端）分别统计 P90 和 P99。
> 低端机的 P99 才是性能优化的真正试金石。
```

---

## 2. 深度解析——资深工程师的性能优化观

### 2.1 性能优化的本质

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                   性能优化的本质：不是"不卡"                                │
└─────────────────────────────────────────────────────────────────────────────┘

  初级工程师的理解：      资深工程师的理解：
  ┌──────────────┐       ┌──────────────────────────────────────────────┐
  │ 不卡就行     │       │ 可度量 → 可归因 → 可预防 → 可持续           │
  └──────────────┘       └──────────────────────────────────────────────┘

  1. 可度量：一切性能问题必须有数据支撑
     ❌ "用户反馈卡" → 没法定位、没法验证
     ✅ "冷启动 P99 从 8s 优化到 3.2s" → 清晰可验证

  2. 可归因：性能劣化必须能找到根因
     ❌ "可能是图片太大了"
     ✅ "Bitmap.decodeStream 在主线程执行了 4.2s，图片 8000x6000"

  3. 可预防：架构层面防止性能问题再次发生
     ❌ "手动 Code Review"
     ✅ "CI 集成 Macrobenchmark，性能劣化自动拦截"

  4. 可持续：优化成果必须有监控守护
     ❌ "发版前测一下"
     ✅ "线上 APM 实时监控，P99 超阈值自动告警"
```

### 2.2 性能优化的黄金法则

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                     性能优化的四条黄金法则                                  │
└─────────────────────────────────────────────────────────────────────────────┘

法则 1：测量先行，不要凭感觉优化
─────────────────────────────────────────────────────────────────────────────
  ❌ "我觉得这里慢，优化一下吧"
  ✅ 用 Profiler / Perfetto 先测量，确认瓶颈位置，再动手

  // 错误示范：凭猜测优化
  // "我觉得这个循环慢" → 改了半天发现瓶颈在 IO

  // 正确流程：
  // 1. CPU Profiler → 发现 80% 时间在 BitmapFactory.decodeStream
  // 2. 定位到具体调用点 → 第 42 行
  // 3. 分析原因 → 原图 8000x6000，没有 inSampleSize
  // 4. 修复 → inSampleSize = 4
  // 5. 回测验证 → 耗时从 4.2s 降到 200ms

法则 2：二八法则，80% 的性能问题来自 20% 的代码
─────────────────────────────────────────────────────────────────────────────
  不要试图优化所有代码，而是用 Profiler 的 Flame Chart 找到"火焰尖峰"
  —— 那个最宽的色块就是你要优化的 20%。

法则 3：回归测试，优化不能引入新问题
─────────────────────────────────────────────────────────────────────────────
  - 优化前：记录基准数据（截图、数值）
  - 优化后：对比验证（性能提升 + 功能正常）
  - 自动化：CI 集成性能基线测试

法则 4：用数据说话，上线前后对比
─────────────────────────────────────────────────────────────────────────────
  - 灰度发布：5% → 20% → 50% → 100%
  - A/B 对比：实验组 vs 对照组的性能指标
  - 数据看板：发版后 7 天内性能指标趋势
```

### 2.3 线上 APM 监控体系

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                   线上 APM（Application Performance Monitoring）            │
└─────────────────────────────────────────────────────────────────────────────┘

为什么需要线上 APM？
─────────────────────────────────────────────────────────────────────────────
  - 线下测试设备有限，无法覆盖所有机型和系统版本
  - 用户网络环境复杂（弱网、断网、2G/3G/4G/5G/WiFi）
  - 线下很难模拟真实用户的行为模式
  - 很多性能问题只在特定场景下复现

APM 核心监控模块：
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    APM 监控矩阵                                     │ │
│   ├──────────────────┬──────────────────────────────────────────────────┤│
│   │  启动监控        │  冷/温/热启动耗时、TTID、TTFD                   ││
│   ├──────────────────┼──────────────────────────────────────────────────┤│
│   │  卡顿监控        │  主线程消息耗时、帧率、Choreographer 掉帧        ││
│   ├──────────────────┼──────────────────────────────────────────────────┤│
│   │  ANR 监控        │  WatchDog 检测、ANR 堆栈采集                     ││
│   ├──────────────────┼──────────────────────────────────────────────────┤│
│   │  内存监控        │  Java 堆/ Native 堆水位、内存泄漏、GC 频率      ││
│   ├──────────────────┼──────────────────────────────────────────────────┤│
│   │  网络监控        │  请求耗时、成功率、流量、DNS 耗时                ││
│   ├──────────────────┼──────────────────────────────────────────────────┤│
│   │  IO 监控         │  主线程文件读写、大文件检测                       ││
│   ├──────────────────┼──────────────────────────────────────────────────┤│
│   │  电量监控        │  WakeLock 持有时长、GPS 使用时长                 ││
│   └──────────────────┴──────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

方案一：Matrix（微信开源）核心模块
─────────────────────────────────────────────────────────────────────────────
  // build.gradle
  dependencies {
      implementation 'com.tencent.matrix:matrix-android-lib:0.6.6'
      implementation 'com.tencent.matrix:matrix-trace-canary:0.6.6'     // 启动/卡顿/ANR
      implementation 'com.tencent.matrix:matrix-resource-canary:0.6.6'  // 内存泄漏
      implementation 'com.tencent.matrix:matrix-io-canary:0.6.6'        // IO 监控
      implementation 'com.tencent.matrix:matrix-battery-canary:0.6.6'   // 电量监控
  }

  // 核心原理——主线程 Looper 消息耗时监控：
  public class LooperMonitor implements Printer {
      @Override
      public void println(String x) {
          if (x.startsWith(">>>>> Dispatching to")) {
              // 记录消息开始时间
              mStartTime = System.currentTimeMillis();
              // 开始采样主线程堆栈
              startDumpStack();
          }
          if (x.startsWith("<<<<< Finished to")) {
              long duration = System.currentTimeMillis() - mStartTime;
              if (duration > mThreshold) {
                  // 超过阈值，上报卡顿
                  reportBlock(duration, getStackTraces());
              }
              stopDumpStack();
          }
      }
  }
  // Looper.loop() 中每处理一条消息前后都会调用 Printer.println()
  // 通过替换 Looper 的 Printer 即可监控所有主线程消息的耗时

方案二：Firebase Performance
─────────────────────────────────────────────────────────────────────────────
  // 自动采集：启动耗时、网络请求、屏幕渲染
  // 无需代码，添加依赖即可

  dependencies {
      implementation 'com.google.firebase:firebase-perf:20.5.0'
  }

  // 自定义 Trace（手动打点）
  val trace = Firebase.performance.newTrace("load_home_data")
  trace.start()
  // ... 执行耗时操作 ...
  trace.stop()

  // 自定义指标
  val metric = trace.getMetric("data_count")
  metric.increment(loadedItems.size.toLong())

方案三：自研 APM 的关键技术点
─────────────────────────────────────────────────────────────────────────────

  1. 主线程卡顿检测（Choreographer 回调间隔）
     Choreographer.getInstance().postFrameCallback(object : FrameCallback {
         private var lastFrameTimeNanos: Long = 0

         override fun doFrame(frameTimeNanos: Long) {
             if (lastFrameTimeNanos > 0) {
                 val durationMs = (frameTimeNanos - lastFrameTimeNanos) / 1_000_000
                 if (durationMs > 100) {  // 超过 100ms（约 6 帧）
                     // 报告卡顿
                     reportJank(durationMs, getCurrentStackTrace())
                 }
             }
             lastFrameTimeNanos = frameTimeNanos
             Choreographer.getInstance().postFrameCallback(this)
         }
     })

  2. 内存水位监控（定期采样）
     val handler = Handler(Looper.getMainLooper())
     val runnable = object : Runnable {
         override fun run() {
             val runtime = Runtime.getRuntime()
             val usedMemory = (runtime.totalMemory() - runtime.freeMemory()) / 1024 / 1024
             val maxMemory = runtime.maxMemory() / 1024 / 1024
             val usageRatio = usedMemory.toFloat() / maxMemory.toFloat()

             if (usageRatio > 0.85f) {
                 // 内存使用率超过 85%，主动 Dump 并上报
                 dumpHprofAndReport()
             }
             handler.postDelayed(this, 30_000)  // 每 30 秒采样一次
         }
     }

  3. 数据上报策略
     - 本地聚合：相同堆栈合并计数，减少上报量
     - 按优先级上报：ANR > OOM > 卡顿 > 启动慢
     - 采样率控制：高频事件按比例采样（如 10%）
     - WiFi 上报：非紧急数据等待 WiFi 环境
```

### 2.4 性能劣化归因方法论

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│              从"用户反馈卡"到"定位到具体代码行"的完整链路                  │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1：用户反馈 → APM 平台筛选
─────────────────────────────────────────────────────────────────────────────
  用户反馈："首页打开很慢"
  → APM 后台筛选条件：
    - 页面：首页
    - 时间范围：最近 7 天
    - 设备：中端机（骁龙 680, 6GB RAM）
    - 系统：Android 13
    - App 版本：3.2.0

Step 2：查看性能指标趋势
─────────────────────────────────────────────────────────────────────────────
  发现：冷启动 P99 从 3.1s（v3.1.0）→ 6.8s（v3.2.0）
  对比发版时间线：v3.2.0 发版后，P99 飙升

Step 3：关联代码变更
─────────────────────────────────────────────────────────────────────────────
  查看 v3.1.0 → v3.2.0 的 Git 变更：
  - 新增了 Firebase SDK 初始化
  - 新增了首页 Banner 广告 SDK
  - 修改了首页布局（新增 3 层嵌套）

Step 4：火焰图定位热点
─────────────────────────────────────────────────────────────────────────────
  从 APM 上报的卡顿堆栈生成火焰图，发现：
  - FirebaseInitProvider.onCreate() 耗时 1.2s ← ContentProvider 滥用
  - AdSDK.init() 耗时 800ms ← 同步初始化
  - HomeFragment.onViewCreated() 耗时 2.1s ← 布局嵌套 + 数据库查询

Step 5：精准修复
─────────────────────────────────────────────────────────────────────────────
  - Firebase → 改用 App Startup 延迟初始化
  - AdSDK → 移到子线程，首页渲染完成后才初始化
  - 首页布局 → ConstraintLayout 替代嵌套，数据库查询改异步

Step 6：灰度验证 → 全量发布 → 指标回归
─────────────────────────────────────────────────────────────────────────────
  灰度 5% → 观察 48h → P99 从 6.8s 降到 3.3s
  灰度 50% → 观察 24h → 稳定
  全量发布 → 持续监控 7 天 → 确认无劣化
```

### 2.5 Baseline Profiles 与编译优化

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                  Baseline Profiles：按启动路径提供编译画像               │
└─────────────────────────────────────────────────────────────────────────────┘

ART 编译策略演进：
─────────────────────────────────────────────────────────────────────────────
  Android 5.0 之前 (Dalvik)：解释执行 + JIT（Android 2.2 起） → 慢
  Android 5.0-6.0 (ART)：   完全 AOT，安装时全量编译 → 安装慢、占空间
  Android 7.0+ (ART)：      AOT + JIT 混合编译，Profile 引导 → 平衡

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Android 7.0+ 编译流程：                                               │
  │                                                                       │
  │  App 首次安装                                                          │
  │      │                                                                │
  │      ▼                                                                │
  │  解释执行并 JIT 编译热点                                              │
  │      │                                                                │
  │      ▼                                                                │
  │  运行时记录"热点代码"（Profile）                                      │
  │      │                                                                │
  │      ▼                                                                │
  │  设备空闲时，基于 Profile 进行 AOT 编译                               │
  │      │                                                                │
  │      ▼                                                                │
  │  后续运行直接执行机器码（快）                                          │
  └─────────────────────────────────────────────────────────────────────────┘

  问题：用户首次安装后的体验取决于 JIT，启动比后续使用慢很多。

Baseline Profiles 的作用：
─────────────────────────────────────────────────────────────────────────────
  开发者在打包时就提供一份"热点代码列表"（Baseline Profiles），
  在受支持的安装/编译流程中，ART 可用这份列表对关键路径做引导编译。
  是否及时安装并使用 profile 取决于交付方式、工具链及设备策略；它不消除全部 JIT。

  验证收益：
  - 使用相同设备、版本、数据与启动场景，对比无 profile 和已使用 profile 的编译模式。
  - 分别报告启动时间和帧时间分位数；I/O、锁等待与业务工作量可能仍是瓶颈。
  - 本文没有对应实测数据，不承诺固定提速百分比。

如何生成和集成 Baseline Profiles：
─────────────────────────────────────────────────────────────────────────────

  // 1. 添加依赖（benchmark 模块的 build.gradle）
  dependencies {
      implementation("androidx.benchmark:benchmark-macro-junit4:1.2.3")
      implementation("androidx.test.ext:junit:1.1.5")
      implementation("androidx.test.espresso:espresso-core:3.5.1")
      implementation("androidx.test.uiautomator:uiautomator:2.2.0")
  }

  // 2. 编写生成 Baseline Profiles 的测试
  @RunWith(AndroidJUnit4::class)
  class BaselineProfileGenerator {
      @get:Rule
      val baselineProfileRule = BaselineProfileRule()

      @Test
      fun generateBaselineProfile() {
          baselineProfileRule.collect(
              packageName = "com.example.app",
              maxIterations = 15,
              stableIterations = 3
          ) {
              // 启动应用
              pressHome()
              startActivityAndWait()

              // 模拟用户操作路径
              device.findObject(By.text("首页")).click()
              device.waitForIdle()

              device.findObject(By.text("详情")).click()
              device.waitForIdle()

              // ... 覆盖更多关键路径
          }
      }
  }

  // 3. app 模块的 build.gradle 中配置
  android {
      defaultConfig {
          // ...
      }
  }
  dependencies {
      // 自动将生成的 Baseline Profiles 打入 APK
      baselineProfile(project(":benchmark"))
  }

  // 4. 使用 Macrobenchmark 验证收益
  @RunWith(AndroidJUnit4::class)
  class StartupBenchmark {
      @get:Rule
      val rule = MacrobenchmarkRule()

      @Test
      fun startupWithoutBaselineProfile() = benchmarkStartup(CompilationMode.None())

      @Test
      fun startupWithBaselineProfile() = benchmarkStartup(CompilationMode.Partial())

      private fun benchmarkStartup(compilationMode: CompilationMode) {
          rule.measureRepeated(
              packageName = "com.example.app",
              metrics = listOf(StartupTimingMetric()),
              compilationMode = compilationMode,
              iterations = 10,
              startupMode = StartupMode.COLD
          ) {
              pressHome()
              startActivityAndWait()
          }
      }
  }

> Baseline Profiles 的价值是把代表性用户路径交给 profile-guided compilation。
> 仍需配置生成/打包流程、维护场景并检查 profile 是否被使用；不能替代减少主线程工作。
> 生成工具按所用 AGP、Baseline Profile Gradle 插件和 Android Studio 版本配置，不假设只升级 AGP 就自动生效。
```

---

## 3. 启动优化

### 3.1 启动类型详解

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         启动类型详解                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  启动类型       │  进程状态  │  Activity 状态  │  耗时  │  用户体验        │
├─────────────────────────────────────────────────────────────────────────────┤
│  冷启动         │  不存在   │  不存在         │  最长  │  显示启动窗口    │
│  (Cold Start)   │           │                 │  2-5s  │  → 显示内容      │
├─────────────────────────────────────────────────────────────────────────────┤
│  温启动         │  存在     │  不存在/被回收  │  中等  │  显示启动窗口    │
│  (Warm Start)   │           │                 │  1-2s  │  → 显示内容      │
├─────────────────────────────────────────────────────────────────────────────┤
│  热启动         │  存在     │  存在(后台)     │  最短  │  直接显示内容    │
│  (Hot Start)    │           │                 │  <1s   │  无启动窗口      │
└─────────────────────────────────────────────────────────────────────────────┘

Android vitals 过慢启动参考线（不是推荐体验目标）:
- 冷启动: < 5 秒
- 温启动: < 2 秒
- 热启动: < 1.5 秒
```

### 3.2 冷启动流程源码分析

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         冷启动完整流程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

用户点击图标                系统层                    应用层
      │                       │                         │
      ▼                       │                         │
┌───────────┐                │                         │
│ Launcher  │                │                         │
│ onClick() │                │                         │
└─────┬─────┘                │                         │
      │                      │                         │
      │ startActivity()      │                         │
      └─────────────────────►│                         │
                             │                         │
                             ▼                         │
┌────────────────────────────────────────────────────────────────────────────┐
│                    ActivityTaskManagerService                              │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 1. startActivity()                                                   │ │
│  │    - 检查调用者权限                                                  │ │
│  │    - 解析 Intent                                                    │ │
│  │    - 检查目标 Activity 是否存在                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 2. ActivityStarter.execute()                                         │ │
│  │    - 解析启动参数                                                    │ │
│  │    - 确定 Launch Mode                                               │ │
│  │    - 确定 Task 归属                                                  │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 3. 检查目标进程是否存在                                              │ │
│  │    if (app == null) {                                               │ │
│  │        startProcess()  // 启动新进程                                 │ │
│  │    }                                                                │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
                                     │ startProcess()
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         Zygote 进程 Fork                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 4. Process.start()                                                   │ │
│  │    - 通过 Socket 连接 Zygote                                        │ │
│  │    - 发送 fork 请求                                                  │ │
│  │    - Zygote fork 新进程                                              │ │
│  │    - 新进程执行 ActivityThread.main()                                │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────┬───────────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    新进程 - ActivityThread                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 5. ActivityThread.main()                                             │ │
│  │    ├── Looper.prepareMainLooper()    // 准备主线程 Looper            │ │
│  │    ├── ActivityThread.attach()       // 附加到 AMS                   │ │
│  │    │       │                                                         │ │
│  │    │       └── AMS.attachApplication()                               │ │
│  │    │               │                                                 │ │
│  │    │               └── bindApplication()                             │ │
│  │    │                       │                                         │ │
│  │    │                       └── Application.onCreate()  ← ─ ─ ─ ─ ─ ─ │ │
│  │    │                               │                                 │ │
│  │    └── Looper.loop()               │  // 启动消息循环                │ │
│  │                                    │                                 │ │
│  └────────────────────────────────────┼──────────────────────────────────┘ │
│                                       │                                   │
│  ┌────────────────────────────────────┼──────────────────────────────────┐ │
│  │ 6. handleBindApplication()         │                                 │ │
│  │    ├── create Application          │                                 │ │
│  │    ├── installContentProviders()   │                                 │ │
│  │    └── Application.onCreate() ◄────┘  ← 关键优化点!                  │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 7. handleLaunchActivity()                                           │ │
│  │    ├── performLaunchActivity()                                      │ │
│  │    │       ├── Activity.attach()                                    │ │
│  │    │       ├── Activity.onCreate()  ← 关键优化点!                   │ │
│  │    │       └── Activity.onStart()                                   │ │
│  │    └── handleResumeActivity()                                       │ │
│  │            └── Activity.onResume()  ← 关键优化点!                   │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ 8. 首帧绘制                                                          │ │
│  │    ├── WindowManager.addView()                                      │ │
│  │    ├── ViewRootImpl.performTraversals()                             │ │
│  │    │       ├── performMeasure()                                     │ │
│  │    │       ├── performLayout()                                      │ │
│  │    │       └── performDraw()                                        │ │
│  │    └── SurfaceFlinger 合成                                          │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                              首帧显示完成
```

### 3.3 启动时间测量

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         启动时间测量方法                                    │
└─────────────────────────────────────────────────────────────────────────────┘

方法 1: adb shell am start
─────────────────────────────────────────────────────────────────────────────
adb shell am start -W [包名]/[Activity全路径]

输出示例:
Starting: Intent { act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] cmp=com.example/.MainActivity }
Status: ok
Activity: com.example/.MainActivity
ThisTime: 1234      ← 当前 Activity 启动时间
TotalTime: 2345     ← 总启动时间 (包含前一个 Activity)
WaitTime: 2500      ← AMS 启动时间 (包含 TotalTime)
Complete: true

方法 2: logcat 过滤
─────────────────────────────────────────────────────────────────────────────
adb logcat -s ActivityTaskManager:I | grep "Displayed"

输出:
ActivityTaskManager: Displayed com.example/.MainActivity: +1s234ms

方法 3: 代码打点 (精确测量)
─────────────────────────────────────────────────────────────────────────────
// Application.attach()
@Override
protected void attachBaseContext(Context base) {
    super.attachBaseContext(base);
    LaunchTimer.start("Application.attach");
}

// Application.onCreate()
@Override
public void onCreate() {
    LaunchTimer.end("Application.attach");
    LaunchTimer.start("Application.onCreate");
    super.onCreate();
    // ...
    LaunchTimer.end("Application.onCreate");
}

// Activity.onCreate()
@Override
protected void onCreate(Bundle savedInstanceState) {
    LaunchTimer.start("Activity.onCreate");
    super.onCreate(savedInstanceState);
    // ...
    LaunchTimer.end("Activity.onCreate");
}

方法 4: Systrace/Perfetto
─────────────────────────────────────────────────────────────────────────────
python $ANDROID_SDK/platform-tools/systrace/systrace.py \
    --app=com.example \
    gfx view wm am \
    -o trace.html
```

### 3.4 启动优化策略

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         启动优化策略详解                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Application.onCreate() 优化                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  问题: Application.onCreate() 是同步执行的，阻塞启动                        │
│                                                                             │
│  ❌ 错误做法:                                                               │
│  public class MyApp extends Application {                                  │
│      @Override                                                             │
│      public void onCreate() {                                              │
│          super.onCreate();                                                 │
│          // 同步初始化所有 SDK                                             │
│          initAnalytics();      // 200ms                                    │
│          initPush();           // 150ms                                    │
│          initImageLoader();    // 100ms                                    │
│          initDatabase();       // 300ms                                    │
│          initNetwork();        // 200ms                                    │
│          // 总耗时: 950ms，严重拖慢启动                                    │
│      }                                                                     │
│  }                                                                         │
│                                                                             │
│  ✅ 正确做法 1: 异步初始化                                                  │
│  public class MyApp extends Application {                                  │
│      @Override                                                             │
│      public void onCreate() {                                              │
│          super.onCreate();                                                 │
│                                                                             │
│          // 核心库同步初始化                                               │
│          initCore();                                                       │
│                                                                             │
│          // 非核心库异步初始化                                             │
│          new Thread(() -> {                                                │
│              initAnalytics();                                              │
│              initPush();                                                   │
│              initImageLoader();                                            │
│          }).start();                                                       │
│      }                                                                     │
│  }                                                                         │
│                                                                             │
│  ✅ 正确做法 2: IdleHandler 延迟初始化                                      │
│  public class MyApp extends Application {                                  │
│      @Override                                                             │
│      public void onCreate() {                                              │
│          super.onCreate();                                                 │
│          initCore();                                                       │
│                                                                             │
│          // 主线程空闲时初始化                                             │
│          Looper.myQueue().addIdleHandler(() -> {                           │
│              initNonCore();                                                │
│              return false;  // 只执行一次                                  │
│          });                                                               │
│      }                                                                     │
│  }                                                                         │
│                                                                             │
│  ✅ 正确做法 3: 启动器框架 (美团)                                           │
│  public final class StartupDispatcher {
    enum State { PENDING, RUNNING, SUCCEEDED, FAILED, SKIPPED }
    private final Map<Class<? extends IStartupTask>, IStartupTask> tasks = new LinkedHashMap<>();
    private final Map<Class<? extends IStartupTask>, State> states = new HashMap<>();
    private final ExecutorService executor; // 调用方拥有生命周期
    private final Handler main = new Handler(Looper.getMainLooper());
    private Context app;
    private boolean started;

    public StartupDispatcher(ExecutorService executor) { this.executor = executor; }

    public synchronized StartupDispatcher addTask(IStartupTask task) {
        if (started) throw new IllegalStateException("Already started");
        if (tasks.containsKey(task.getClass())) throw new IllegalArgumentException("Duplicate task");
        tasks.put(task.getClass(), task);
        return this;
    }

    // 启动前检查缺失依赖和环，不能让任务永远等待。
    private void visit(Class<? extends IStartupTask> key,
                       Set<Class<? extends IStartupTask>> visiting,
                       Set<Class<? extends IStartupTask>> visited) {
        if (visited.contains(key)) return;
        IStartupTask task = tasks.get(key);
        if (task == null) throw new IllegalArgumentException("Missing dependency: " + key);
        if (!visiting.add(key)) throw new IllegalArgumentException("Dependency cycle: " + key);
        for (Class<? extends IStartupTask> dep : task.dependencies()) visit(dep, visiting, visited);
        visiting.remove(key);
        visited.add(key);
    }

    public synchronized void start(Context context) {
        if (started) throw new IllegalStateException("Single use dispatcher");
        Set<Class<? extends IStartupTask>> visiting = new HashSet<>(), visited = new HashSet<>();
        for (Class<? extends IStartupTask> key : tasks.keySet()) visit(key, visiting, visited);
        app = context.getApplicationContext();
        started = true;
        for (Class<? extends IStartupTask> key : tasks.keySet()) states.put(key, State.PENDING);
        drain();
    }

    private void drain() { // 只在 this 锁内访问调度状态
        List<IStartupTask> ordered = new ArrayList<>(tasks.values());
        ordered.sort(Comparator.comparingInt(IStartupTask::priority));
        boolean skipped;
        do {
            skipped = false;
            for (IStartupTask task : ordered) {
                Class<? extends IStartupTask> key = task.getClass();
                if (states.get(key) != State.PENDING) continue;
                boolean ready = true, failed = false;
                for (Class<? extends IStartupTask> dep : task.dependencies()) {
                    State state = states.get(dep);
                    ready &= state == State.SUCCEEDED;
                    failed |= state == State.FAILED || state == State.SKIPPED;
                }
                if (failed) {
                    states.put(key, State.SKIPPED);
                    skipped = true;
                } else if (ready) {
                    states.put(key, State.RUNNING); // 提交前保留状态，防多依赖完成时重复启动
                    Runnable run = () -> {
                        boolean ok = false;
                        try {
                            task.execute(app);
                            ok = true;
                        } catch (RuntimeException e) {
                            Log.e("Startup", "Task failed: " + key.getName(), e);
                        } finally {
                            finished(key, ok); // Error 仍传播，但不遗漏状态结算
                        }
                    };
                    try {
                        if (task.isOnMainThread()) {
                            if (!main.post(run)) throw new RejectedExecutionException("Main looper stopped");
                        } else executor.execute(run);
                    } catch (RejectedExecutionException e) {
                        states.put(key, State.FAILED);
                        skipped = true;
                    }
                }
            }
        } while (skipped); // 传递失败到所有后继节点
    }

    private synchronized void finished(Class<? extends IStartupTask> key, boolean ok) {
        states.put(key, ok ? State.SUCCEEDED : State.FAILED);
        drain();
    }

    public synchronized Map<Class<? extends IStartupTask>, State> snapshot() {
        return new HashMap<>(states);
    }
}

// Application 持有共享 executor；DeviceInfoTask/UserInfoTask/NetworkManager 是业务实现。
// dependencies() 必须返回构造后不变的依赖集合，execute() 返回代表该节点完成。
ExecutorService startupExecutor = Executors.newFixedThreadPool(2);
new StartupDispatcher(startupExecutor)
    .addTask(new NetworkInitTask())
    .addTask(new DeviceInfoTask())
    .addTask(new UserInfoTask())
    .start(this);
// 不在主线程 await；在应用定义的任务域结束时 shutdown executor，避免重复创建线程池。

```

### 3.5 App Startup 库

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│              App Startup：替代 ContentProvider 滥用的官方方案               │
└─────────────────────────────────────────────────────────────────────────────┘

问题背景：
─────────────────────────────────────────────────────────────────────────────
  很多第三方 SDK（Firebase、LeakCanary、WorkManager 等）通过注册空的
  ContentProvider 来实现自动初始化。每个 ContentProvider 都会在
  Application.onCreate() 之前被实例化，严重拖慢启动。

  // AndroidManifest.xml 中常见的第三方 SDK 注册
  <provider
      android:name="com.google.firebase.provider.FirebaseInitProvider"
      android:authorities="${applicationId}.firebaseinitprovider"
      android:exported="false" />
  <provider
      android:name="androidx.work.impl.WorkManagerInitializer"
      android:authorities="${applicationId}.workmanager-init"
      android:exported="false" />
  <!-- 每个 Provider 都要执行 onCreate()，串行执行，累积耗时 200-500ms -->

App Startup 解决方案：
─────────────────────────────────────────────────────────────────────────────

  // 1. 添加依赖
  dependencies {
      implementation "androidx.startup:startup-runtime:1.2.0"
  }

  // 2. 创建 Initializer（每个 SDK 一个）
  public class FirebaseInitializer implements Initializer<FirebaseApp> {
      @NonNull
      @Override
      public FirebaseApp create(@NonNull Context context) {
          FirebaseApp.initializeApp(context);
          return FirebaseApp.getInstance();
      }

      @NonNull
      @Override
      public List<Class<? extends Initializer<?>>> dependencies() {
          return Collections.emptyList();  // 无依赖
      }
  }

  public class AnalyticsInitializer implements Initializer<Analytics> {
      @NonNull
      @Override
      public Analytics create(@NonNull Context context) {
          return Analytics.init(context);
      }

      @NonNull
      @Override
      public List<Class<? extends Initializer<?>>> dependencies() {
          return Arrays.asList(FirebaseInitializer.class);  // 依赖 Firebase
      }
  }

  // 3. AndroidManifest.xml 中只注册一个 InitializationProvider
  <provider
      android:name="androidx.startup.InitializationProvider"
      android:authorities="${applicationId}.androidx-startup"
      android:exported="false"
      tools:node="merge">
      <meta-data
          android:name="com.example.FirebaseInitializer"
          android:value="androidx.startup" />
  </provider>

  // 4. 禁用第三方 SDK 的自动初始化
  <provider
      android:name="com.google.firebase.provider.FirebaseInitProvider"
      tools:node="remove" />

  // 5. 延迟初始化：不在 manifest 中声明，改为手动触发
  AppInitializer.getInstance(context).initializeComponent(MyInitializer.class);
```

### 3.6 启动器框架完整实现

```java
// 基于有向无环图（DAG）的并行初始化框架（美团/有赞方案）
//
// 设计思路：
// 1. 将所有初始化任务抽象为 Task
// 2. 声明 Task 之间的依赖关系
// 3. 构建 DAG → 拓扑排序 → 并行执行无依赖任务

// ┌──────────┐    ┌──────────┐
// │ 网络初始化│    │ 设备信息  │     ← 无依赖，并行执行
// └─────┬────┘    └─────┬────┘
//       │               │
//       ▼               ▼
// ┌──────────────────────────┐
// │     用户信息初始化        │    ← 依赖网络+设备
// └───────────┬──────────────┘
//             ▼
// ┌──────────────────────────┐
// │     数据预加载            │    ← 依赖用户信息
// └──────────────────────────┘

// Task 接口定义
public interface IStartupTask {
    void execute(Context context);
    List<Class<? extends IStartupTask>> dependencies();
    boolean isOnMainThread();    // 是否需要在主线程
    int priority();             // 优先级，值越小越高
}

// 具体任务示例
public class NetworkInitTask implements IStartupTask {
    @Override
    public void execute(Context context) {
        OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS).build();
        NetworkManager.setClient(client);
    }
    @Override
    public List<Class<? extends IStartupTask>> dependencies() {
        return Collections.emptyList();
    }
    @Override
    public boolean isOnMainThread() { return false; }
    @Override
    public int priority() { return 1; }
}

// 启动调度器核心实现
public final class StartupDispatcher {
    enum State { PENDING, RUNNING, SUCCEEDED, FAILED, SKIPPED }
    private final Map<Class<? extends IStartupTask>, IStartupTask> tasks = new LinkedHashMap<>();
    private final Map<Class<? extends IStartupTask>, State> states = new HashMap<>();
    private final ExecutorService executor; // 调用方拥有生命周期
    private final Handler main = new Handler(Looper.getMainLooper());
    private Context app;
    private boolean started;

    public StartupDispatcher(ExecutorService executor) { this.executor = executor; }

    public synchronized StartupDispatcher addTask(IStartupTask task) {
        if (started) throw new IllegalStateException("Already started");
        if (tasks.containsKey(task.getClass())) throw new IllegalArgumentException("Duplicate task");
        tasks.put(task.getClass(), task);
        return this;
    }

    // 启动前检查缺失依赖和环，不能让任务永远等待。
    private void visit(Class<? extends IStartupTask> key,
                       Set<Class<? extends IStartupTask>> visiting,
                       Set<Class<? extends IStartupTask>> visited) {
        if (visited.contains(key)) return;
        IStartupTask task = tasks.get(key);
        if (task == null) throw new IllegalArgumentException("Missing dependency: " + key);
        if (!visiting.add(key)) throw new IllegalArgumentException("Dependency cycle: " + key);
        for (Class<? extends IStartupTask> dep : task.dependencies()) visit(dep, visiting, visited);
        visiting.remove(key);
        visited.add(key);
    }

    public synchronized void start(Context context) {
        if (started) throw new IllegalStateException("Single use dispatcher");
        Set<Class<? extends IStartupTask>> visiting = new HashSet<>(), visited = new HashSet<>();
        for (Class<? extends IStartupTask> key : tasks.keySet()) visit(key, visiting, visited);
        app = context.getApplicationContext();
        started = true;
        for (Class<? extends IStartupTask> key : tasks.keySet()) states.put(key, State.PENDING);
        drain();
    }

    private void drain() { // 只在 this 锁内访问调度状态
        List<IStartupTask> ordered = new ArrayList<>(tasks.values());
        ordered.sort(Comparator.comparingInt(IStartupTask::priority));
        boolean skipped;
        do {
            skipped = false;
            for (IStartupTask task : ordered) {
                Class<? extends IStartupTask> key = task.getClass();
                if (states.get(key) != State.PENDING) continue;
                boolean ready = true, failed = false;
                for (Class<? extends IStartupTask> dep : task.dependencies()) {
                    State state = states.get(dep);
                    ready &= state == State.SUCCEEDED;
                    failed |= state == State.FAILED || state == State.SKIPPED;
                }
                if (failed) {
                    states.put(key, State.SKIPPED);
                    skipped = true;
                } else if (ready) {
                    states.put(key, State.RUNNING); // 提交前保留状态，防多依赖完成时重复启动
                    Runnable run = () -> {
                        boolean ok = false;
                        try {
                            task.execute(app);
                            ok = true;
                        } catch (RuntimeException e) {
                            Log.e("Startup", "Task failed: " + key.getName(), e);
                        } finally {
                            finished(key, ok); // Error 仍传播，但不遗漏状态结算
                        }
                    };
                    try {
                        if (task.isOnMainThread()) {
                            if (!main.post(run)) throw new RejectedExecutionException("Main looper stopped");
                        } else executor.execute(run);
                    } catch (RejectedExecutionException e) {
                        states.put(key, State.FAILED);
                        skipped = true;
                    }
                }
            }
        } while (skipped); // 传递失败到所有后继节点
    }

    private synchronized void finished(Class<? extends IStartupTask> key, boolean ok) {
        states.put(key, ok ? State.SUCCEEDED : State.FAILED);
        drain();
    }

    public synchronized Map<Class<? extends IStartupTask>, State> snapshot() {
        return new HashMap<>(states);
    }
}

// Application 持有共享 executor；DeviceInfoTask/UserInfoTask/NetworkManager 是业务实现。
// dependencies() 必须返回构造后不变的依赖集合，execute() 返回代表该节点完成。
ExecutorService startupExecutor = Executors.newFixedThreadPool(2);
new StartupDispatcher(startupExecutor)
    .addTask(new NetworkInitTask())
    .addTask(new DeviceInfoTask())
    .addTask(new UserInfoTask())
    .start(this);
// 不在主线程 await；在应用定义的任务域结束时 shutdown executor，避免重复创建线程池。

```

### 3.7 ContentProvider 滥用治理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│             ContentProvider 滥用：拖慢启动的隐形杀手                       │
└─────────────────────────────────────────────────────────────────────────────┘

核心原理：
  ActivityThread.handleBindApplication() 中：
    1. installContentProviders()  ← 串行初始化所有 ContentProvider
    2. Application.onCreate()     ← Provider 全部完成后才执行

审计项目中的 ContentProvider：
─────────────────────────────────────────────────────────────────────────────
  # 查看合并后的 Manifest
  ./gradlew :app:processReleaseManifest
  grep -n "android:name.*Provider" \
      app/build/intermediates/merged_manifests/release/AndroidManifest.xml

  # 常见的第三方 SDK ContentProvider：
  # FirebaseInitProvider、WorkManagerInitializer、
  # ProcessLifecycleOwnerInitializer、AndroidXStartupProvider

治理方案：
─────────────────────────────────────────────────────────────────────────────
  1. 使用 tools:node="remove" 移除第三方 Provider，改为手动初始化

  <provider
      android:name="com.google.firebase.provider.FirebaseInitProvider"
      tools:node="remove" />

  2. 使用 App Startup 统一管理（见 3.5 节）

  3. 延迟初始化：IdleHandler 或首帧后再初始化非核心 SDK

  Looper.myQueue().addIdleHandler(() -> {
      FirebaseApp.initializeApp(context);  // 主线程空闲时初始化
      return false;
  });
```

### 3.8 首帧优化

```java
// 首帧耗时 = setContentView(inflate) + 数据加载 + 首次渲染

// 优化 1：AsyncLayoutInflater 异步填充布局
// dependencies { implementation "androidx.asynclayoutinflater:asynclayoutinflater:1.0.0" }

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // 先显示骨架屏
    setContentView(R.layout.skeleton_loading)

    // 异步 inflate 真实布局
    AsyncLayoutInflater(this).inflate(R.layout.activity_main, null) { view, _, _ ->
        setContentView(view)
        initViews(view)
    }
}

// 优化 2：ViewStub 按需加载
// 首帧只加载用户立即能看到的 View，不可见的用 ViewStub 占位
// <ViewStub android:id="@+id/stub_ad" android:layout="@layout/ad_banner" />

// 优化 3：Fragment 懒加载
// ViewPager2 + FragmentStateAdapter 使用 setMaxLifecycle 控制 Fragment 生命周期
// 只有当前可见的 Fragment 才执行 onResume()

// 优化 4：延迟加载非必要数据
// 首帧只加载展示所需的最小数据集，其余数据异步加载
viewModel.loadMinimalData().observe(this) { data ->
    updateUI(data)                      // 立即展示
    viewModel.loadFullDataInBackground() // 后台加载完整数据
}
```

### 3.9 启动优化工具

CPU Profiler 定位方法与调用栈；Perfetto 使用第 2 章配置，在采集期间触发冷启动，关联 `bindApplication`、Activity 生命周期、首个应用帧与 SurfaceFlinger 实际展示。旧 SDK 的 `platform-tools/systrace/systrace.py` 不是 Android 17 开发工具必定附带的文件。

启动回归使用独立 `com.android.test` benchmark 模块（依赖 `androidx.benchmark:benchmark-macro-junit4`），目标为非 debuggable、可 profile 的 release 应用；模块配置见 2.5。`MacrobenchmarkRule` 提供 `measureRepeated`，不是不存在的 `measure` / `MacrobenchmarkScope.Actions`。

```kotlin
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {
    @get:Rule val rule = MacrobenchmarkRule()

    @Test fun startupCold() = rule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        compilationMode = CompilationMode.None(),
        startupMode = StartupMode.COLD,
        iterations = 10,
        setupBlock = { pressHome() }
    ) {
        startActivityAndWait()
    }
}
```

对比 Baseline Profile 时另跑 `CompilationMode.Partial`；控制设备温度、编译模式、数据和启动入口。首帧时间不等于业务全部就绪；TTFD 要在真实内容可用时调用 `reportFullyDrawn()`，不能在 onCreate 无条件调用来缩短指标。

源码：[MacrobenchmarkRule.measureRepeated](https://github.com/androidx/androidx/blob/androidx-main/benchmark/benchmark-macro-junit4/src/main/java/androidx/benchmark/macro/junit4/MacrobenchmarkRule.kt)。此为 AndroidX 开发分支，项目仍须锁定所使用库版本；它不属于 AOSP 平台 tag。


---

## 4. UI 渲染优化

### 4.1 渲染原理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 渲染架构                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                         应用层 (App)                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                        View Hierarchy                                  │ │
│  │   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐             │ │
│  │   │Activity │──►│Window  │──►│DecorView│──►│ViewGroup│             │ │
│  │   └─────────┘   └─────────┘   └─────────┘   └─────────┘             │ │
│  │                                                     │                 │ │
│  │                                                     ▼                 │ │
│  │                                            ┌───────────────┐          │ │
│  │                                            │ performTraversals│       │ │
│  │                                            │  - measure     │          │ │
│  │                                            │  - layout      │          │ │
│  │                                            │  - draw        │          │ │
│  │                                            └───────┬───────┘          │ │
│  └────────────────────────────────────────────────────┼──────────────────┘ │
│                                                       │                    │
└───────────────────────────────────────────────────────┼────────────────────┘
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         系统框架层 (Framework)                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     Choreographer                                      │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │  VSync 信号接收                                              │    │ │
│  │   │  - 与屏幕刷新率同步 (60Hz = 16.6ms)                          │    │ │
│  │   │  - 调度 CALLBACK_INPUT, CALLBACK_ANIMATION, CALLBACK_TRAVERSAL│   │ │
│  │   └─────────────────────────────────────────────────────────────┘    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     SurfaceFlinger                                     │ │
│  │   ┌─────────────────────────────────────────────────────────────┐    │ │
│  │   │  图层合成                                                    │    │ │
│  │   │  - 收集所有 Surface                                          │    │ │
│  │   │  - 合成最终图像                                              │    │ │
│  │   │  - 提交给 Hardware Composer                                  │    │ │
│  │   └─────────────────────────────────────────────────────────────┘    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                                        │
                                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         硬件层 (Hardware)                                   │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     Hardware Composer (HWC)                            │ │
│  │   - GPU 合成                                                           │ │
│  │   - 显示到屏幕                                                         │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 16ms 法则

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         16ms 法则详解                                       │
└─────────────────────────────────────────────────────────────────────────────┘

60fps = 60 帧每秒 = 每帧 16.6ms (1000ms / 60 = 16.6ms)

┌─────────────────────────────────────────────────────────────────────────────┐
│  正常情况 (每帧 < 16ms)                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  时间轴:  0ms      16ms     33ms     50ms     66ms     83ms                │
│           │        │        │        │        │        │                   │
│  VSync:   ▼        ▼        ▼        ▼        ▼        ▼                   │
│           ├────────┤        │        │        │        │                   │
│           │ Frame1 │        │        │        │        │                   │
│           ├────────┼────────┤        │        │        │                   │
│           │        │ Frame2 │        │        │        │                   │
│           │        ├────────┼────────┤        │        │                   │
│           │        │        │ Frame3 │        │        │                   │
│           │        │        ├────────┼────────┤        │                   │
│           │        │        │        │ Frame4 │        │                   │
│           │        │        │        ├────────┼────────┤                   │
│           │        │        │        │        │ Frame5 │                   │
│                                                                             │
│  结果: 流畅 60fps                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  卡顿情况 (某帧 > 16ms)                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  时间轴:  0ms      16ms     33ms     50ms     66ms     83ms                │
│           │        │        │        │        │        │                   │
│  VSync:   ▼        ▼        ▼        ▼        ▼        ▼                   │
│           ├─────────────────────────┤        │        │        │           │
│           │      Frame1 (30ms)      │        │        │        │           │
│           │        卡顿!            ├────────┤        │        │           │
│           │                         │ Frame2 │        │        │           │
│           │                         ├────────┼────────┤        │           │
│           │                         │        │ Frame3 │        │           │
│                                                                             │
│  结果: Frame1 超时，VSync 信号到达时未完成，跳过一帧                        │
│        用户体验: 卡顿、掉帧                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 VSync 与 Choreographer

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VSync 与 Choreographer                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Choreographer 工作流程                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Display (屏幕)                                                            │
│       │                                                                     │
│       │ VSync 信号 (每 16.6ms)                                              │
│       ▼                                                                     │
│   ┌─────────────────┐                                                      │
│   │ FrameDisplayEvent│                                                      │
│   │    Receiver      │                                                      │
│   └────────┬────────┘                                                      │
│            │                                                                │
│            ▼                                                                │
│   ┌─────────────────────────────────────────────────────────────────┐     │
│   │                      Choreographer                              │     │
│   │                                                                 │     │
│   │   CallbackQueue:                                                │     │
│   │   ┌─────────────────────────────────────────────────────────┐  │     │
│   │   │ CALLBACK_INPUT (优先级最高)                              │  │     │
│   │   │   - 输入事件处理                                        │  │     │
│   │   ├─────────────────────────────────────────────────────────┤  │     │
│   │   │ CALLBACK_ANIMATION (优先级中)                           │  │     │
│   │   │   - 动画计算                                            │  │     │
│   │   ├─────────────────────────────────────────────────────────┤  │     │
│   │   │ CALLBACK_TRAVERSAL (优先级最低)                         │  │     │
│   │   │   - measure, layout, draw                               │  │     │
│   │   └─────────────────────────────────────────────────────────┘  │     │
│   │                                                                 │     │
│   └─────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Choreographer 源码分析                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  // Choreographer.java                                                     │
│  public final class Choreographer {                                        │
│                                                                             │
│      // 回调类型                                                           │
│      public static final int CALLBACK_INPUT = 0;                           │
│      public static final int CALLBACK_ANIMATION = 1;                       │
│      public static final int CALLBACK_TRAVERSAL = 2;                       │
│      public static final int CALLBACK_COMMIT = 3;                          │
│  }                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 双缓冲与三缓冲

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         双缓冲与三缓冲                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  双缓冲 (Double Buffering)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  原理: 使用两个缓冲区，一个用于显示，一个用于绘制                           │
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐                                     │
│   │ Front Buffer│     │ Back Buffer │                                     │
│   │  (显示中)   │◄────│  (绘制中)   │                                     │
│   └─────────────┘     └─────────────┘                                     │
│         │                    │                                             │
│         ▼                    ▼                                             │
│      显示器              GPU 绘制                                          │
│                                                                             │
│  VSync 时交换缓冲区，避免撕裂                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  三缓冲 (Triple Buffering)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  原理: 使用三个缓冲区，减少丢帧                                             │
│                                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                 │
│   │ Buffer A    │     │ Buffer B    │     │ Buffer C    │                 │
│   │  (显示中)   │     │  (准备好)   │     │  (绘制中)   │                 │
│   └─────────────┘     └─────────────┘     └─────────────┘                 │
│                                                                             │
│  优点: 当 GPU 绘制快于显示器时，可以提前准备下一帧                          │
│  缺点: 增加延迟 (多一帧延迟)                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.5 渲染性能分析

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         渲染性能分析方法                                    │
└─────────────────────────────────────────────────────────────────────────────┘

1. GPU 过度绘制分析
─────────────────────────────────────────────────────────────────────────────
   开发者选项 → 调试 GPU 过度绘制

   颜色含义:
   - 无色: 没有过度绘制 (绘制 1 次)
   - 蓝色: 过度绘制 1x (绘制 2 次)
   - 绿色: 过度绘制 2x (绘制 3 次)
   - 粉色: 过度绘制 3x (绘制 4 次)
   - 红色: 过度绘制 4x+ (绘制 5 次以上)

   目标: 避免红色，减少粉色和绿色

2. GPU 渲染分析
─────────────────────────────────────────────────────────────────────────────
   开发者选项 → GPU 呈现模式分析 → 在屏幕上显示为条形图

   颜色含义:
   - 橙色: 交换缓冲区时间
   - 红色: 执行命令时间
   - 蓝色: 更新视图时间
   - 紫色: 输入处理时间
   - 深绿: 动画时间
   - 浅绿: 测量/布局时间

   目标: 每帧保持在 16ms 绿线以下

3. Systrace 分析
─────────────────────────────────────────────────────────────────────────────
   python $ANDROID_SDK/platform-tools/systrace/systrace.py \
       gfx view res am wm sched \
       -o trace.html

   分析重点:
   - Frame 时间线 (彩色圆点)
   - 绿色: 16ms 内完成
   - 黄色: 接近 16ms
   - 红色: 超过 16ms (卡顿)
```

### 4.6 渲染优化策略

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         渲染优化策略详解                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  1. 减少过度绘制                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ❌ 问题代码:                                                               │
│  <RelativeLayout android:background="#FFFFFF">  <!-- 背景 1 -->           │
│      <LinearLayout android:background="#FFFFFF"> <!-- 背景 2，重复 -->    │
│          <TextView android:background="#FFFFFF" /> <!-- 背景 3，重复 -->  │
│      </LinearLayout>                                                       │
│  </RelativeLayout>                                                         │
│                                                                             │
│  ✅ 优化后:                                                                 │
│  <RelativeLayout>  <!-- 移除背景 -->                                       │
│      <LinearLayout>  <!-- 移除背景 -->                                     │
│          <TextView android:background="#FFFFFF" />  <!-- 只保留必要背景 -->│
│      </LinearLayout>                                                       │
│  </RelativeLayout>                                                         │
│                                                                             │
│  优化技巧:                                                                  │
│  - 父布局背景能覆盖子布局时，移除子布局背景                                │
│  - 使用 android:background="@null" 移除不必要背景                         │
│  - 使用 canvas.clipRect() 限制绘制区域                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  2. 布局层级优化                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ❌ 问题: 嵌套过深                                                          │
│  <LinearLayout>                    <!-- 层级 1 -->                         │
│      <LinearLayout>                <!-- 层级 2 -->                         │
│          <RelativeLayout>          <!-- 层级 3 -->                         │
│              <FrameLayout>         <!-- 层级 4 -->                         │
│                  <TextView />                                               │
│              </FrameLayout>                                                 │
│          </RelativeLayout>                                                  │
│      </LinearLayout>                                                        │
│  </LinearLayout>                                                            │
│                                                                             │
│  ✅ 优化: 使用 ConstraintLayout                                             │
│  <androidx.constraintlayout.widget.ConstraintLayout>  <!-- 层级 1 -->      │
│      <TextView                                                              │
│          app:layout_constraintTop_toTopOf="parent"                         │
│          app:layout_constraintStart_toStartOf="parent" />                  │
│  </androidx.constraintlayout.widget.ConstraintLayout>                      │
│                                                                             │
│  优化工具: Layout Inspector 查看布局层级                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  3. ViewStub 延迟加载                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  场景: 某些 View 不需要立即显示                                            │
│                                                                             │
│  <!-- 定义 ViewStub -->                                                     │
│  <ViewStub                                                                  │
│      android:id="@+id/stub_progress"                                       │
│      android:layout="@layout/progress_view"                                │
│      android:inflatedId="@+id/progress_view" />                            │
│                                                                             │
│  // 需要时才加载                                                            │
│  ViewStub stub = findViewById(R.id.stub_progress);                         │
│  View progressView = stub.inflate();                                       │
│  // 或者                                                                    │
│  stub.setVisibility(View.VISIBLE);  // 自动 inflate                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  4. 使用硬件加速                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  API 11 引入，targetSdk>=14 默认开启硬件加速                                             │
│                                                                             │
│  检查是否启用:                                                              │
│  view.isHardwareAccelerated()  // View 级别                                │
│  canvas.isHardwareAccelerated()  // Canvas 级别                            │
│                                                                             │
│  自定义 View 优化:                                                          │
│  // 使用 RenderNode (API 29+)                                              │
│  public class CustomView extends View {                                    │
│      private RenderNode renderNode;                                        │
│                                                                             │
│      public CustomView(Context context) {                                  │
│          super(context);                                                   │
│          renderNode = new RenderNode("CustomNode");                        │
│      }                                                                     │
│                                                                             │
│      @Override                                                             │
│      protected void onDraw(Canvas canvas) {                                │
│          // 使用 DisplayListCanvas                                         │
│          RecordingCanvas recordingCanvas = renderNode.beginRecording();    │
│          // 绘制操作...                                                     │
│          renderNode.endRecording();                                        │
│          canvas.drawRenderNode(renderNode);                                │
│      }                                                                     │
│  }                                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.7 RecyclerView 性能优化专题

```java
// ┌─────────────────────────────────────────────────────────────────────────┐
// │       RecyclerView 四级缓存机制：面试必考，工程必用                            │
// └─────────────────────────────────────────────────────────────────────────┘
//
// 四级缓存：
// ┌─────────────────────────────────────────────────────────────────────────┐
// │  Level 1: mChangedScrap     │  ViewHolder 被标记为 "changed" 的缓存       │
// │           (Adapter 内部)     │  仅在 layout 期间有效                       │
// │                              │  用于 pre-layout 阶段                      │
// ├─────────────────────────────────────────────────────────────────────────┤
// │  Level 2: mAttachedScrap   │  与 RecyclerView 仍关联但被标记 remove 的  │
// │           (Adapter 内部)     │  仅在 layout 期间有效                        │
// ├─────────────────────────────────────────────────────────────────────────┤
// │  Level 3: mCachedViews     │  默认缓存大小 2（setItemViewCacheSize 可调）│
// │           (RecyclerView)    │  不走 onCreateViewHolder，直接复用           │
// │                              │  FIFO 淘汰                                   │
// ├─────────────────────────────────────────────────────────────────────────┤
// │  Level 4: RecycledViewPool │  按 viewType 分类缓存                         │
// │           (全局共享)         │  默认每种 viewType 缓存 5 个                │
// │                              │  走 onCreateViewHolder，需重新 bindData      │
// └─────────────────────────────────────────────────────────────────────────┘
//
// 查找顺序：mChangedScrap → mAttachedScrap → mCachedViews → RecycledViewPool
// 是否 bind 还取决于 updated/invalid 等状态，不能仅凭层级保证

// 优化 1：增大 CacheView 数量（适合固定列表项少的场景）
recyclerView.setItemViewCacheSize(10)  // 默认 2，可适当增大

// 优化 2：共享 RecycledViewPool（多个 RecyclerView 共享）
val pool = RecyclerView.RecycledViewPool()
pool.setMaxRecycledViews(TYPE_HEADER, 5)
pool.setMaxRecycledViews(TYPE_CONTENT, 20)

recyclerView1.setRecycledViewPool(pool)
recyclerView2.setRecycledViewPool(pool)  // 多个列表共享同一个池

// 优化 3：DiffUtil 精准刷新（替代 notifyDataSetChanged）
class UserDiffCallback(
    private val oldList: List<User>,
    private val newList: List<User>
) : DiffUtil.Callback() {

    override fun getOldListSize(): Int = oldList.size
    override fun getNewListSize(): Int = newList.size

    override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
        return oldList[oldPos].id == newList[newPos].id
    }

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        return oldList[oldPos] == newList[newPos]
    }

    override fun getChangePayload(oldPos: Int, newPos: Int): Any? {
        // 精准更新：只传递变化的字段
        val diff = Bundle()
        if (oldList[oldPos].name != newList[newPos].name) {
            diff.putString("name", newList[newPos].name)
        }
        return if (diff.size() > 0) diff else null
    }
}

// 使用
val diffResult = DiffUtil.calculateDiff(UserDiffCallback(oldList, newList))
diffResult.dispatchUpdatesTo(adapter)

// 优化 4：RecyclerView.setHasFixedSize(true)
// RecyclerView 自身尺寸不依赖 adapter 内容时使用，不是 item 大小固定
recyclerView.setHasFixedSize(true)

// 优化 5：预取（Prefetch）
// RecyclerView 默认已开启预取，但在嵌套 RecyclerView 时需要额外处理
recyclerView.setItemViewCacheSize(4)  // 增大缓存以配合预取
```

### 4.8 自定义 View 性能优化

```java
// ┌─────────────────────────────────────────────────────────────────────────┐
// │          自定义 View 的 6 个性能陷阱与优化                                │
// └─────────────────────────────────────────────────────────────────────────┘
//
// 陷阱 1：在 onDraw 中创建对象
// ❌ 每帧创建 Paint 对象
@Override
protected void onDraw(Canvas canvas) {
    Paint paint = new Paint();  // GC 压力 → 内存抖动 → 卡顿
    paint.setColor(Color.RED);
    canvas.drawRect(0, 0, getWidth(), getHeight(), paint);
}

// ✅ 复用成员变量
private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
{ paint.setColor(Color.RED); }

@Override
protected void onDraw(Canvas canvas) {
    canvas.drawRect(0, 0, getWidth(), getHeight(), paint);
}

// 陷阱 2：频繁调用 invalidate()
// ❌ 在动画中每帧全量 invalidate
ValueAnimator.ofFloat(0f, 1f).apply {
    addUpdateListener { invalidate() }  // 整个 View 重绘
    start()
}

// ✅ 只 invalidate 需要更新的区域
addUpdateListener {
    invalidate(dirtyRect)  // 只重绘脏区域
}

// 陷阱 3：在 onDraw 中做耗时计算
// ❌
@Override
protected void onDraw(Canvas canvas) {
    for (Point p : complexPath) {  // 复杂路径计算
        path.lineTo(p.x, p.y);
    }
    canvas.drawPath(path, paint);
}

// ✅ 在数据变化时预计算路径，onDraw 只负责绘制
private Path precomputedPath = new Path();

public void updateData(List<Point> points) {
    precomputedPath.reset();
    for (Point p : points) {
        precomputedPath.lineTo(p.x, p.y);
    }
    invalidate();
}

@Override
protected void onDraw(Canvas canvas) {
    canvas.drawPath(precomputedPath, paint);  // O(1)
}

// 陷阱 4：不使用硬件层
// 对于频繁移动但内容不变的 View，使用硬件层加速
view.setLayerType(View.LAYER_TYPE_HARDWARE, null)  // GPU 缓存
// 动画结束后关闭
view.setLayerType(View.LAYER_TYPE_NONE, null)
```

---

## 5. 内存优化

### 5.1 Java 运行时数据区与 ART

运行时数据区不是 JMM（线程可见性/有序性）模型；不能直接套用 HotSpot Eden/S0/S1。Android 进程还包含 Native、共享映射、图形缓冲区和线程栈。

### 5.2 Android 内存管理

ART 不能套用 HotSpot 的 Eden/S0/S1 固定布局。`Heap` 按 boot image、Zygote、allocation/region、large object 等 space 管理对象；allocation stack 是追踪新分配对象的元数据，不是年轻代对象存储区。

在 AOSP `android-17.0.0_r1`，应沿 `art/runtime/gc/heap.cc` 的 `Heap::Heap`、`Heap::CollectGarbageInternal` 与 `art/runtime/gc/collector/` 阅读实际收集器选择；Concurrent Copying（CC）与 Concurrent Mark Compact（CMC）由构建、运行配置和设备能力决定。并发收集也有暂停/屏障/分配等待，不能保证“GC 都小于 1ms”。

```text
分配 -> 检查空间/水位 -> 并发请求或分配慢路径等待 GC
     -> 按当前 collector 标记、复制/整理或清扫
     -> 更新存活量和下次触发阈值

历史 CMS 分类：
  Sticky 追踪上次 GC 后的分配；不是 Eden + Survivor
  Partial 排除 Zygote space；不是任意年轻代/老年代百分比
  Full 扫描更大范围；image 等空间仍有不同回收规则
```

这些历史名字不代表 Android 17 固定使用三种 CMS。日志的 collector 名称、freed、paused 和 total 必须分别看，total 包含并发工作，不能全部当作主线程暂停。Dalvik 后期也有并发 GC，不能概括成所有版本单线程全程 STW。

来源：[AOSP 17 heap.cc](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/gc/heap.cc)、[ART GC 调试](https://source.android.com/docs/core/runtime/gc-debug)。

`MemoryLimiter` 是 **system_server 中 `com.android.server.am.MemoryLimiter` 的进程级内存限制服务**，不是应用可配置的 Java 堆上限，也不是 LMKD。`Configuration` 是 Java record，字段为 `memVisible/memNotVisible/swapVisible/swapNotVisible`，单位 bytes。默认测试配置 4/2/2/2 GiB 明确不是生产统一限额；是否运行取决于 feature flag、`/vendor/etc/memory-limiter-config.xml`、RAM 匹配及内核/cgroup 支持。

```text
ProcessRecord/进程状态变更
 -> MemoryLimiter 的进程记录选择 visible/notVisible 限额
 -> configureLimit(nativeService, pid, uid, memHigh, swapHigh)
 -> Native 监控 memory.high / memory.swap.high
 -> 内存高水位后进入额外 anon+swap 采样
 -> anon+swap 超限 -> onLimitExceeded(LIMIT_TYPE_ANON_SWAP)
 -> 释放限额；可选触发系统 profiling
 -> MESSAGE_KILL 延迟 KILL_DELAY_MS=30_000
 -> Injector.killProcess -> IActivityManager.killPids -> AMS.killPids
 -> REASON_OTHER + SUBREASON_KILL_PID
```

Native 的 anon+swap 阈值对应 `memHigh + swapHigh`，不能用 PSS、RSS 或 `Runtime.maxMemory()` 直接替代。30 秒给可选 profiler 完成，不是应用保证获得的清理窗口；限额/退出描述不是稳定 SDK 契约，部分设备可能未启用。

源码：[MemoryLimiter.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/am/MemoryLimiter.java) 的 `Configuration/isMemoryLimiterSupported/onLimitExceeded`；[Native MemoryLimiter.cpp](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/jni/com_android_server_am_MemoryLimiter.cpp) 的 `testAnonSwap/configureLimit`。退出必须结合 `ApplicationExitInfo` reason、description、timestamp、PSS/RSS 和设备日志；仅 `REASON_OTHER` 不能认定 MemoryLimiter，`MemoryLimiter:AnonSwap` 只能作本 tag 的启发分类。

### 5.3 内存泄漏检测

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         内存泄漏检测                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  常见内存泄漏场景                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. 静态变量持有 Context                                                    │
│  ❌ 泄漏代码:                                                               │
│  public class Utils {                                                       │
│      private static Context sContext;                                      │
│      public static void init(Context context) {                            │
│          sContext = context;  // 泄漏! Activity 无法释放                   │
│      }                                                                     │
│  }                                                                         │
│  ✅ 修复:                                                                   │
│  public class Utils {                                                       │
│      private static Context sContext;                                      │
│      public static void init(Context context) {                            │
│          sContext = context.getApplicationContext();  // 使用 Application  │
│      }                                                                     │
│  }                                                                         │
│                                                                             │
│  2. 非静态内部类                                                            │
│  ❌ 泄漏代码:                                                               │
│  public class MainActivity extends Activity {                              │
│      private class MyThread extends Thread {  // 隐式持有 Activity        │
│          @Override public void run() { /* ... */ }                        │
│      }                                                                     │
│  }                                                                         │
│  ✅ 修复: 使用静态内部类 + 弱引用                                           │
│  private static class MyThread extends Thread {                            │
│      private WeakReference<MainActivity> ref;                              │
│      MyThread(MainActivity activity) {                                     │
│          ref = new WeakReference<>(activity);                              │
│      }                                                                     │
│  }                                                                         │
│                                                                             │
│  3. Handler 泄漏                                                            │
│  ❌ 泄漏代码:                                                               │
│  public class MainActivity extends Activity {                              │
│      private Handler handler = new Handler() {  // 隐式持有 Activity      │
│          @Override public void handleMessage(Message msg) { /* ... */ }   │
│      };                                                                    │
│  }                                                                         │
│  ✅ 修复:                                                                   │
│  private static class SafeHandler extends Handler {                        │
│      private WeakReference<MainActivity> ref;                              │
│      SafeHandler(MainActivity activity) { ref = new WeakReference<>(activity); }│
│      @Override public void handleMessage(Message msg) {                    │
│          MainActivity activity = ref.get();                                │
│          if (activity != null) { /* ... */ }                               │
│      }                                                                     │
│  }                                                                         │
│  // onDestroy 中移除消息                                                   │
│  @Override protected void onDestroy() {                                    │
│      handler.removeCallbacksAndMessages(null);                             │
│  }                                                                         │
│                                                                             │
│  4. 注册未取消                                                              │
│  ❌ 泄漏代码:                                                               │
│  @Override protected void onCreate(Bundle savedInstanceState) {            │
│      registerReceiver(receiver, filter);  // 忘记 unregisterReceiver      │
│  }                                                                         │
│  ✅ 修复:                                                                   │
│  @Override protected void onDestroy() {                                    │
│      unregisterReceiver(receiver);                                         │
│  }                                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LeakCanary 使用                                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  // build.gradle                                                           │
│  dependencies {                                                            │
│      debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'│
│  }                                                                         │
│                                                                             │
│  // 自动检测 Activity/Fragment 泄漏                                        │
│  // 只需添加依赖，无需额外代码                                              │
│                                                                             │
│  // 手动检测                                                                │
│  AppWatcher.objectWatcher.watch(myObject, "Watch description");           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 内存优化策略

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         内存优化策略                                        │
└─────────────────────────────────────────────────────────────────────────────┘

1. 使用优化的数据结构
─────────────────────────────────────────────────────────────────────────────
   - SparseArray / LongSparseArray 替代 HashMap<Integer, Object>
   - SparseIntArray / SparseBooleanArray 替代 HashMap<Integer, Integer/Boolean>
   - ArrayMap 替代 HashMap (少量数据时)

2. Bitmap 优化
─────────────────────────────────────────────────────────────────────────────
   // 加载缩略图
   BitmapFactory.Options options = new BitmapFactory.Options();
   options.inSampleSize = 4;  // 缩小 4 倍
   options.inPreferredConfig = Bitmap.Config.RGB_565;  // 2字节/像素，省一半
   Bitmap bitmap = BitmapFactory.decodeFile(path, options);

   // 及时回收
   if (bitmap != null && !bitmap.isRecycled()) {
       bitmap.recycle();
   }

3. 使用 String 池
─────────────────────────────────────────────────────────────────────────────
   String s1 = "hello";  // 使用字符串池
   String s2 = new String("hello");  // ❌ 创建新对象
   String s3 = s2.intern();  // ✅ 返回池中引用

4. 避免在 onDraw 中创建对象
─────────────────────────────────────────────────────────────────────────────
   ❌ 错误:
   @Override protected void onDraw(Canvas canvas) {
       Paint paint = new Paint();  // 每帧创建! 严重性能问题
       canvas.drawRect(..., paint);
   }

   ✅ 正确:
   private Paint paint = new Paint();  // 成员变量，复用
   @Override protected void onDraw(Canvas canvas) {
       canvas.drawRect(..., paint);
   }
```

### 5.5 OOM 分析与处理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OOM 分析与处理                                      │
└─────────────────────────────────────────────────────────────────────────────┘

1. OOM 类型
─────────────────────────────────────────────────────────────────────────────
   - Java Heap OOM: Java 堆内存不足
   - Native OOM: Native 内存不足 (通常是 Bitmap)
   - Thread OOM: 线程数过多

2. 分析 OOM
─────────────────────────────────────────────────────────────────────────────
   // 捕获 OOM 堆栈
   try {
       // 可能 OOM 的操作
   } catch (OutOfMemoryError e) {
       // 打印内存信息
       Debug.MemoryInfo memoryInfo = new Debug.MemoryInfo();
       Debug.getMemoryInfo(memoryInfo);
       Log.e("OOM", "Memory: " + memoryInfo.getTotalPrivateDirty() + " KB");
   }

   // 使用 Memory Profiler 分析内存快照
   // 1. 捕获 Heap Dump
   // 2. 查看对象数量和大小
   // 3. 找出占用大的对象

3. 处理 OOM
─────────────────────────────────────────────────────────────────────────────
   - 增大堆内存: android:largeHeap="true"
   - 减少内存占用: 图片压缩、数据结构优化
   - 内存复用: 对象池、Bitmap 复用
   - 延迟加载: 分页加载、按需加载
```

---

## 6. 线程与并发优化

### 6.1 线程池调优

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    线程池调优：不只是 newCachedThreadPool                    │
└─────────────────────────────────────────────────────────────────────────────┘

ThreadPoolExecutor 核心参数：
─────────────────────────────────────────────────────────────────────────────
  ThreadPoolExecutor(
      int corePoolSize,      // 核心线程数（空闲也不回收）
      int maximumPoolSize,   // 最大线程数（核心+临时线程）
      long keepAliveTime,    // 临时线程空闲存活时间
      TimeUnit unit,         // 时间单位
      BlockingQueue<Runnable> workQueue,  // 任务等待队列
      ThreadFactory threadFactory,        // 线程工厂（可自定义线程名）
      RejectedExecutionHandler handler    // 拒绝策略
  )

  // 推荐配置（CPU 密集型任务）
  int cpuCount = Runtime.getRuntime().availableProcessors();
  int corePoolSize = cpuCount + 1;
  int maxPoolSize = cpuCount * 2 + 1;

  ThreadPoolExecutor cpuExecutor = new ThreadPoolExecutor(
      corePoolSize, maxPoolSize,
      30, TimeUnit.SECONDS,
      new LinkedBlockingQueue<>(128),
      new NamedThreadFactory("cpu-pool"),
      new ThreadPoolExecutor.AbortPolicy()  // 调用者处理拒绝/降级，不让主线程回退执行慢任务
  );

  // 推荐配置（IO 密集型任务）
  // IO 任务大部分时间在等待，所以线程数可以远大于 CPU 核数
  ThreadPoolExecutor ioExecutor = new ThreadPoolExecutor(
      cpuCount * 2, cpuCount * 4,
      60, TimeUnit.SECONDS,
      new LinkedBlockingQueue<>(256),
      new NamedThreadFactory("io-pool"),
      new ThreadPoolExecutor.AbortPolicy()
  );

  // 自定义 ThreadFactory（便于排查线程问题）
  class NamedThreadFactory implements ThreadFactory {
      private final AtomicInteger counter = new AtomicInteger(0);
      private final String prefix;

      NamedThreadFactory(String prefix) { this.prefix = prefix; }

      @Override
      public Thread newThread(Runnable r) {
          Thread t = new Thread(() -> {
                Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND);
                r.run();
            }, prefix + "-" + counter.incrementAndGet());
          // 优先级只在上面的新线程 Runnable 内设置，不能改变创建线程。
          return t;
      }
  }
```

### 6.2 协程调度优化

```kotlin
// ┌─────────────────────────────────────────────────────────────────────────┐
// │              协程调度器选择：不是所有 IO 都该用 Dispatchers.IO            │
// └─────────────────────────────────────────────────────────────────────────┘

// Dispatchers 选择指南：
// ┌──────────────────────┬───────────────────────────────────────────────────┐
// │  调度器               │  适用场景                                        │
// ├──────────────────────┼───────────────────────────────────────────────────┤
// │  Dispatchers.Main    │  UI 更新、轻量级状态管理（仅 Android）            │
// │  Dispatchers.IO      │  阻塞 IO（默认并行度 max(64, CPU数)，可配置；limitedParallelism 可弹性扩展）           │
// │  Dispatchers.Default │  CPU 密集计算：JSON 解析、图片处理、排序          │
// │  Dispatchers.Unconfined│ 不推荐，行为不可预测                           │
// │  自定义线程池         │  特殊需求：限制并发数、隔离 IO                    │
// └──────────────────────┴───────────────────────────────────────────────────┘

// 错误示例：用 IO 调度器做 CPU 密集计算
lifecycleScope.launch(Dispatchers.IO) {
    // ❌ 大图压缩是 CPU 密集型，不应该在 IO 线程池
    val compressed = compressBitmap(largeBitmap)
    withContext(Dispatchers.Main) { showImage(compressed) }
}

// 正确示例：
lifecycleScope.launch(Dispatchers.Main) {
    val compressed = withContext(Dispatchers.Default) {
        compressBitmap(largeBitmap)  // CPU 密集 → Default
    }
    showImage(compressed)
}

// 自定义协程调度器（限制并发数）
val limitedIoDispatcher = Dispatchers.IO.limitedParallelism(10)

// 隔离慢速 IO（避免阻塞正常 IO 线程池）
val slowIoDispatcher = Executors.newFixedThreadPool(2).asCoroutineDispatcher()
lifecycleScope.launch(slowIoDispatcher) {
    // 大文件下载等慢速操作，不会影响其他 IO 任务
    downloadLargeFile(url)
}
```

### 6.3 锁优化策略

```java
// ┌─────────────────────────────────────────────────────────────────────────┐
// │            锁的选择：没有万能锁，只有合适的锁                             │
// └─────────────────────────────────────────────────────────────────────────┘
//
// ┌───────────────────┬──────────────┬──────────────┬───────────────────────┐
// │  对比项            │ synchronized │ ReentrantLock│ CAS (Atomic类)        │
// ├───────────────────┼──────────────┼──────────────┼───────────────────────┤
// │  实现层面          │ JVM 层       │ API 层       │ CPU 指令层             │
// │  可中断            │ 否           │ 是           │ 无锁                  │
// │  超时获取          │ 否           │ 是           │ 无锁                  │
// │  公平锁            │ 否           │ 可选         │ 无锁                  │
// │  性能（低竞争）    │ 高           │ 高           │ 最高                  │
// │  性能（高竞争）    │ 中           │ 高           │ 低（自旋消耗 CPU）    │
// │  适用场景          │ 简单同步     │ 复杂同步     │ 计数器、状态标志       │
// └───────────────────┴──────────────┴──────────────┴───────────────────────┘

// 读多写少场景：ReadWriteLock
public class ConfigManager {
    private final ReadWriteLock rwLock = new ReentrantReadWriteLock();
    private final Map<String, String> config = new HashMap<>();

    public String get(String key) {
        rwLock.readLock().lock();
        try {
            return config.get(key);  // 读锁不互斥，并发读无阻塞
        } finally {
            rwLock.readLock().unlock();
        }
    }

    public void set(String key, String value) {
        rwLock.writeLock().lock();
        try {
            config.put(key, value);  // 写锁互斥
        } finally {
            rwLock.writeLock().unlock();
        }
    }
}

// 高并发计数：AtomicInteger（无锁 CAS）
// ❌ 性能差
private int counter = 0;
public synchronized void increment() { counter++; }

// ✅ 无锁化
private AtomicInteger counter = new AtomicInteger(0);
public void increment() { counter.incrementAndGet(); }
```

### 5.6 内存抖动检测与治理
```java
// ┌─────────────────────────────────────────────────────────────────────────┐
// │      内存抖动 (Memory Churn)：频繁 GC 导致的 UI 卡顿                    │
// └─────────────────────────────────────────────────────────────────────────┘
//
// 症状：
//   - Profiler 中内存曲线呈锯齿状（频繁上升下降）
//   - Choreographer 日志显示跳帧
//   - Logcat 中频繁出现 "GC alloc space" 日志
//
// 常见场景与修复：

// ❌ 场景 1：循环中创建对象
public void processItems(List<String> items) {
    for (String item : items) {
        // ❌ 每次循环创建新的 Formatter
        String formatted = new Formatter().format("Item: %s", item).toString();
    }
}

// ✅ 复用 Formatter
public void processItems(List<String> items) {
    StringBuilder sb = new StringBuilder(64);  // 预分配容量
    Formatter formatter = new Formatter(sb);
    for (String item : items) {
        sb.setLength(0);  // 清空但保留 char[]
        formatter.format("Item: %s", item);
        String formatted = sb.toString();
    }
}

// ❌ 场景 2：onDraw 中创建 Paint/Path
@Override
protected void onDraw(Canvas canvas) {
    Paint paint = new Paint();  // 60fps → 每秒创建 60 个 Paint 对象
    paint.setColor(Color.RED);
    canvas.drawCircle(cx, cy, radius, paint);
}

// ✅ 成员变量复用
private final Paint circlePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
{ circlePaint.setColor(Color.RED); }

// ❌ 场景 3：自动装箱
HashMap<Integer, String> map = new HashMap<>();
for (int i = 0; i < 10000; i++) {
    map.put(i, "value" + i);  // 每次 put 都创建 Integer 对象
}

// ✅ 使用 SparseArray
SparseArray<String> sparseArray = new SparseArray<>(10000);
for (int i = 0; i < 10000; i++) {
    sparseArray.put(i, "value" + i);  // 无装箱
}

// 检测工具：
// 1. Memory Profiler → 查看内存曲线是否锯齿状
// 2. Allocation Tracker → 按分配次数排序，找到高频分配的调用栈
// 3. LeakCanary 检测对象保留/泄漏，不是分配抖动探针
```

### 5.7 Bitmap 内存管理演进
```java
// ┌─────────────────────────────────────────────────────────────────────────┐
// │       Bitmap 内存管理的演进史：面试必考的知识点                          │
// └─────────────────────────────────────────────────────────────────────────┘
//
// ┌──────────────────────┬───────────────────────────────────────────────────┐
// │  Android 版本          │  Bitmap 内存位置                                  │
// ├──────────────────────┼───────────────────────────────────────────────────┤
// │  Android 2.3.3 (API 10) 之前 │  Native Heap（不计数，容易 OOM）           │
// │  Android 3.0 (API 11) ~ 7.1 │  Java Heap（计数，但容易 OOM）              │
// │  Android 8.0 (API 26)       │  Native Heap + 计数（最佳方案）             │
// └──────────────────────┴───────────────────────────────────────────────────┘
//
// 关键演进细节：
// - API 10 及以前：像素在 Native Heap，回收可能延迟
//   仅确认无人使用时可主动 recycle；不手动回收不等同必然泄漏
//
// - API 11~25：像素数据移到 Java Heap，Bitmap 对象本身就是 Java 对象
//   GC 可以自动回收，但计入 Java Heap 上限（容易 OOM）
//
// - API 26+：像素数据回到 Native Heap，但通过 NativeAllocationRegistry
//   让 GC 感知其大小，GC 时自动释放 Native 内存
//   不再需要手动 recycle()

// 大图加载方案：BitmapRegionDecoder（加载超大图片的部分区域）
public class LargeImageView extends View {
    private BitmapRegionDecoder decoder;
    private Rect visibleRect = new Rect();

    public void setImage(String filePath) {
        InputStream is = new FileInputStream(filePath);
        decoder = BitmapRegionDecoder.newInstance(is, false);
        // 只解码可见区域，而不是整张图片
        requestLayout();
    }

    @Override
    protected void onDraw(Canvas canvas) {
        BitmapFactory.Options options = new BitmapFactory.Options();
        options.inPreferredConfig = Bitmap.Config.RGB_565;
        options.inSampleSize = calculateSampleSize();

        visibleRect.set(0, scrollY, getWidth(), scrollY + getHeight());
        Bitmap bitmap = decoder.decodeRegion(visibleRect, options);
        canvas.drawBitmap(bitmap, 0, 0, paint);
    }
}

// inBitmap 复用（API 19+）
// 复用已有 Bitmap 的内存区域，避免重新分配
BitmapFactory.Options options = new BitmapFactory.Options();
options.inBitmap = reusableBitmap;  // 复用这个 Bitmap 的内存
options.inMutable = true;
Bitmap newBitmap = BitmapFactory.decodeFile(path, options);

// Glide 内部已自动处理 inBitmap 复用
```

### 5.8 onTrimMemory 与主动内存预算

API 34 起不再发送旧 `TRIM_MEMORY_RUNNING_*`、`MODERATE/COMPLETE` 压力通知；`onLowMemory()` 也不再调用，API 35 已废弃。不能依赖它们在 Android 17 杀进程前清理。`TRIM_MEMORY_UI_HIDDEN` 仍表达 UI 已不可见。

```java
@Override public void onTrimMemory(int level) {
    super.onTrimMemory(level);
    if (level == ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN) {
        uiCache.evictAll(); // 仅释放业务确认可重建的缓存，不 recycle 正在使用的图片
    }
}
```

正常运行设置缓存/图片尺寸/并发预算，页面退出注销监听。高压力下自动主线程 HPROF 会进一步暂停并消耗资源，只在授权诊断与采样策略下转储。

来源：[ComponentCallbacks2](https://developer.android.com/reference/android/content/ComponentCallbacks2)、[ComponentCallbacks](https://developer.android.com/reference/android/content/ComponentCallbacks)。

### 5.9 Native 内存泄漏排查

heapprofd 是 Perfetto 的 Native 分配采样数据源，不使用旧示例虚构的 `heapprofd --pid --sampling --standalone` 参数。应用需 debuggable/profileable 并满足设备权限。

```bash
# Perfetto 官方 tools/heap_profile 主机脚本；先下载并检查脚本。
python3 heap_profile -n com.example.app -c 1000 -d 10000
# -c 连续 dump 间隔 ms；-d 时长 ms；结果位置按脚本输出。
```

也可在 Perfetto 配置 `android.heapprofd`、`heapprofd_config.process_cmdline`、`sampling_interval_bytes` 与连续 dump；分析未释放分配栈随时间的变化，符号解析需要匹配的未剥离 SO。采样不是所有 malloc 的无损记录。

ASan/HWASan 检测越界和 use-after-free，必须重新编译 Native 代码；wrap.sh 只设置运行环境，不会自动插桩。NDK ASan 不支持通用 LeakSanitizer；CMake 的 `-DANDROID_SANITIZE=address` 不是自动启用开关，应以 `target_compile_options(... -fsanitize=address -fno-omit-frame-pointer)` 和 `target_link_options(... -fsanitize=address)` 配置并满足运行时要求。新项目评估受支持的 HWASan 设备/构建。

`dumpsys gfxinfo` 资源增长只是信号，应区分缓存水位与持续泄漏。
来源：[Native heap profiling](https://perfetto.dev/docs/quickstart/heap-profiling)、[NDK ASan](https://developer.android.com/ndk/guides/asan)。

## 7. 电量优化

### 7.1 电量消耗分析

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         电量消耗分析                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  主要耗电因素                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────────┐│
│   │  耗电因素          │  耗电程度  │  优化策略                          ││
│   ├───────────────────────────────────────────────────────────────────────┤│
│   │  屏幕              │  ★★★★★   │  降低亮度、减少唤醒时间            ││
│   │  CPU               │  ★★★★☆   │  减少计算、使用后台线程            ││
│   │  网络              │  ★★★★☆   │  批量请求、使用缓存                ││
│   │  GPS               │  ★★★☆☆   │  按需开启、降低精度                ││
│   │  传感器            │  ★★☆☆☆   │  及时注销、降低采样率              ││
│   │  WakeLock          │  ★★★★☆   │  及时释放、使用超时                ││
│   │  Alarm             │  ★★★☆☆   │  使用 setAndAllowWhileIdle         ││
│   └───────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

电量统计命令:
adb shell dumpsys batterystats --charged <package_name>
```

### 7.2 电量优化策略

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         电量优化策略                                        │
└─────────────────────────────────────────────────────────────────────────────┘

1. 网络请求优化
─────────────────────────────────────────────────────────────────────────────
   - 批量请求，减少网络唤醒次数
   - 使用 WiFi 而非移动数据
   - 监听网络状态，网络差时延迟请求

2. WakeLock 优化
─────────────────────────────────────────────────────────────────────────────
   // ❌ 错误: 忘记释放
   PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
   WakeLock wakeLock = pm.newWakeLock(PARTIAL_WAKE_LOCK, "MyTag");
   wakeLock.acquire();
   // 忘记 release()!

   // ✅ 正确: 使用 try-finally
   WakeLock wakeLock = pm.newWakeLock(PARTIAL_WAKE_LOCK, "MyTag");
   wakeLock.acquire(10*60*1000L);  // 设置超时，防止忘记释放
   try {
       // 执行任务
   } finally {
       if (wakeLock.isHeld()) {
           wakeLock.release();
       }
   }

3. 后台任务优化
─────────────────────────────────────────────────────────────────────────────
   - 使用 WorkManager 替代手动后台线程
   - 设置网络约束和充电约束
   - 使用 JobScheduler 批量执行
```

### 7.4 Doze 模式与 App Standby

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Doze 模式与 App Standby                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Doze 模式 (Android 6.0+)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  触发条件:                                                                  │
│  - 设备未充电                                                               │
│  - 屏幕关闭                                                                 │
│  - 设备静止                                                                 │
│                                                                             │
│  限制:                                                                      │
│  - 网络访问被暂停                                                           │
│  - Alarm 被推迟 (setAndAllowWhileIdle 除外)                                │
│  - WiFi/蓝牙扫描被暂停                                                      │
│  - 同步适配器被暂停                                                         │
│                                                                             │
│  维护窗口 (定期执行):                                                       │
│  - 网络请求可以执行                                                         │
│  - 同步可以执行                                                             │
│  - 间隔越来越长                                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  App Standby (Android 6.0+)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  触发条件:                                                                  │
│  - 应用在后台长时间未被使用                                                 │
│  - 没有前台服务                                                             │
│  - 没有通知栏通知                                                           │
│                                                                             │
│  限制:                                                                      │
│  - 网络访问被限制                                                           │
│  - Job 被推迟                                                               │
│  - 同步被推迟                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Battery Historian 使用教程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                Battery Historian：Google 官方电量分析工具                    │
└─────────────────────────────────────────────────────────────────────────────┘

安装与使用：
─────────────────────────────────────────────────────────────────────────────
  # 1. 安装 Docker（已安装则跳过）
  # macOS: brew install --cask docker
  # Linux: sudo apt install docker.io

  # 2. 拉取 Battery Historian 镜像
  docker run -d -p 9999:9999 gcr.io/android-battery-historian/stable:3.1 \
      --port 9999

  # 3. 重置电量数据
  adb shell dumpsys batterystats --reset

  # 4. 操作你的 App（模拟正常使用场景）

  # 5. 导出电量报告
  adb bugreport bugreport.zip

  # 6. 打开浏览器访问
  # http://localhost:9999
  # 上传 bugreport.zip 文件

分析重点：
─────────────────────────────────────────────────────────────────────────────
  ┌───────────────────┬───────────────────────────────────────────────────────┐
  │  指标              │  说明                                                 │
  ├───────────────────┼───────────────────────────────────────────────────────┤
  │  CPU Running      │  CPU 唤醒频率和时长（应该尽量少）                     │
  │  Network          │  网络模块活跃时长（应该批量处理）                     │
  │  Wake Lock        │  WakeLock 持有时长（应该及时释放）                   │
  │  GPS              │  GPS 使用时长（应该用完即关）                        │
  │  Sensors          │  传感器活跃时长（应该降低采样率）                    │
  │  Screen On        │  屏幕亮起时长（影响最大）                            │
  └───────────────────┴───────────────────────────────────────────────────────┘

  典型问题定位：
  - CPU Running 持续活跃 → 有后台线程在跑
  - Wake Lock 长时间持有 → 忘记 release()
  - Network 频繁小包 → 应该合并请求
  - GPS 持续运行 → 应该降低更新频率或使用融合定位
```

### 7.5 GPS 精度分级策略

```java
// ┌─────────────────────────────────────────────────────────────────────────┐
// │              GPS 精度分级：不是所有场景都需要高精度                        │
// └─────────────────────────────────────────────────────────────────────────┘

// 策略：根据业务场景选择合适的精度级别
// ┌──────────────────┬──────────────────────────┬──────────────────────┐
// │  场景             │  推荐方案                 │  耗电量               │
// ├──────────────────┼──────────────────────────┼──────────────────────┤
// │  打车/导航        │  GPS 高精度               │  高                   │
// │  附近的人/店铺    │  融合定位 (Fused) 100m    │  中                   │
// │  天气/城市定位    │  网络定位 (粗略)          │  低                   │
// │  统计用户地域     │  IP 定位                  │  极低                 │
// └──────────────────┴──────────────────────────┴──────────────────────┘

// 融合定位（推荐使用 FusedLocationProvider）
// dependencies { implementation 'com.google.android.gms:play-services-location:21.0.1' }

// 高精度请求（导航场景）
val highAccuracyRequest = LocationRequest.Builder(
    Priority.PRIORITY_HIGH_ACCURACY,  // GPS + WiFi + 基站
    1000  // 间隔 1 秒
).build()

// 平衡精度请求（附近的人）
val balancedRequest = LocationRequest.Builder(
    Priority.PRIORITY_BALANCED_POWER_ACCURACY,  // WiFi + 基站为主
    10_000  // 间隔 10 秒
).build()

// 低功耗请求（城市级定位）
val lowPowerRequest = LocationRequest.Builder(
    Priority.PRIORITY_LOW_POWER,  // 仅 WiFi + 基站
    60_000  // 间隔 60 秒
).build()

// 及时停止定位（关键！）
override fun onPause() {
    super.onPause()
    fusedLocationClient.removeLocationUpdates(locationCallback)
}

override fun onResume() {
    super.onResume()
    // 只在前台时才请求定位
    fusedLocationClient.requestLocationUpdates(
        balancedRequest, locationCallback, mainLooper
    )
}
```

### 7.6 Android 12+ 前台服务限制

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│        Android 12+ 前台服务启动限制（Foreground Service Launch              │
│        Restrictions）                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

Android 12 变更：
─────────────────────────────────────────────────────────────────────────────
  - 后台应用无法启动前台服务（少数例外除外）
  - 违反会抛出 ForegroundServiceStartNotAllowedException

  例外情况（允许后台启动前台服务）：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 高优先级 Firebase Cloud Messaging (FCM) 消息                       │
  │  2. 用户与应用交互（Activity 可见、通知点击等）                        │
  │  3. 应用刚刚从后台启动（有短暂的豁免窗口）                             │
  │  4. 使用 startForeground() 的 Service 由前台应用调用                   │
  │  5. 特殊权限：SYSTEM_ALERT_WINDOW、ACCESSIBILITY                       │
  └─────────────────────────────────────────────────────────────────────────┘

Android 14 进一步限制：
  - 前台服务类型必须声明（camera、location、mediaPlayback 等）
  - 部分类型需要声明对应权限

适配方案：
─────────────────────────────────────────────────────────────────────────────
  // 方案 1：使用 WorkManager 替代前台服务（推荐）
  val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
      .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
      .setConstraints(Constraints.Builder()
          .setRequiredNetworkType(NetworkType.CONNECTED).build())
      .build()
  WorkManager.getInstance(context).enqueue(workRequest)

  // 方案 2：使用 setForeground() 在 WorkManager 中实现前台服务效果
  class SyncWorker(appContext: Context, params: WorkerParameters) :
      CoroutineWorker(appContext, params) {

      override suspend fun doWork(): Result {
          setForeground(ForegroundInfo(
              1,
              NotificationCompat.Builder(applicationContext, "sync")
                  .setContentTitle("正在同步...")
                  .build()
          ))
          // 执行同步任务
          return Result.success()
      }
  }
```

### 7.7 WorkManager 最佳实践

```kotlin
// 使用 WorkManager 执行后台任务
val workRequest = PeriodicWorkRequestBuilder<SyncWorker>(
    1, TimeUnit.HOURS  // 每小时执行一次
)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)  // 有网络时执行
            .setRequiresBatteryNotLow(true)  // 电量充足时执行
            .setRequiresCharging(true)  // 充电时执行
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(workRequest)

class SyncWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    override fun doWork(): Result {
        // 执行后台任务
        return Result.success()
    }
}
```

---

## 8. 网络优化

### 8.1 网络请求优化

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         网络请求优化                                        │
└─────────────────────────────────────────────────────────────────────────────┘

1. 连接复用
─────────────────────────────────────────────────────────────────────────────
   // OkHttp 连接池
   OkHttpClient client = new OkHttpClient.Builder()
       .connectionPool(new ConnectionPool(5, 5, TimeUnit.MINUTES))
       .build();

2. 请求压缩
─────────────────────────────────────────────────────────────────────────────
   // Gzip 压缩
   // 不显式设置 Accept-Encoding，保留 OkHttp 透明 gzip
   @GET("api/data")
   Call<Response> getData();

3. 批量请求
─────────────────────────────────────────────────────────────────────────────
   - 合并多个小请求为一个
   - 减少网络握手次数

4. 请求去重
─────────────────────────────────────────────────────────────────────────────
   - 相同请求只发送一次
   - 使用缓存避免重复请求
```

### 8.2 HTTP/2 与 OkHttp 配置

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│           HTTP/2 多路复用与 OkHttp 高级配置                                │
└─────────────────────────────────────────────────────────────────────────────┘

HTTP/1.1 vs HTTP/2：
─────────────────────────────────────────────────────────────────────────────
  ┌──────────────────────┬────────────────────────┬───────────────────────────┐
  │  特性                │  HTTP/1.1              │  HTTP/2                    │
  ├──────────────────────┼────────────────────────┼───────────────────────────┤
  │  连接复用            │  Keep-Alive (串行)     │  多路复用 (并行)           │
  │  头部压缩            │  无                    │  HPACK 压缩               │
  │  服务器推送          │  不支持                │  Server Push              │
  │  二进制协议          │  文本                  │  二进制帧                  │
  │  并发请求数          │  6 (浏览器限制)        │  无限制                    │
  │  队头阻塞            │  应用层有              │  仅 TCP 层有              │
  └──────────────────────┴────────────────────────┴───────────────────────────┘

  OkHttp 默认支持 HTTP/2，无需额外配置。
  前提条件：服务端必须支持 HTTP/2（Nginx/Apache 已默认支持）。

OkHttp 最佳配置：
─────────────────────────────────────────────────────────────────────────────
  OkHttpClient client = new OkHttpClient.Builder()
      // 连接池：最多保持 10 个空闲连接，存活 5 分钟
      .connectionPool(new ConnectionPool(10, 5, TimeUnit.MINUTES))
      // 连接超时
      .connectTimeout(15, TimeUnit.SECONDS)
      // 读取超时
      .readTimeout(20, TimeUnit.SECONDS)
      // 写入超时
      .writeTimeout(20, TimeUnit.SECONDS)
      // 启用 HTTP/2（默认已开启）
      .protocols(Arrays.asList(Protocol.HTTP_2, Protocol.HTTP_1_1))
      // Cookie 内存管理（CookieManager 默认不持久化）
      .cookieJar(new JavaNetCookieJar(new CookieManager()))
      // 添加统一请求头
      .addInterceptor(chain -> {
          Request original = chain.request();
          Request request = original.newBuilder()
              .header("Accept-Encoding", "gzip")  // OkHttp 自动处理 gzip
              // HTTP/2 不使用 Connection 头
              .build();
          return chain.proceed(request);
      })
      // 日志拦截器（仅 Debug）
      .addInterceptor(new HttpLoggingInterceptor()
          .setLevel(BuildConfig.DEBUG ? Level.BODY : Level.NONE))
      .build();

  // 连接复用验证：同一 host 多个请求共享 TCP 连接
  // 在 HTTP/2 下，同一 host 的所有请求共享同一个 TCP 连接
```

### 8.3 弱网策略

```java
// ┌─────────────────────────────────────────────────────────────────────────┐
// │         弱网策略：让 App 在地铁、电梯、地下车库也能正常工作              │
// └─────────────────────────────────────────────────────────────────────────┘

// 策略 1：超时与重试（指数退避）
public final class RetryInterceptor implements Interceptor {
    @Override public Response intercept(Chain chain) throws IOException {
        Request request = chain.request();
        Response first = chain.proceed(request);
        if (!"GET".equals(request.method()) || first.code() != 503 ||
                !"0".equals(first.header("Retry-After")) || chain.call().isCanceled()) return first;
        first.close();
        return chain.proceed(request);
    }
}
// 仅应用拦截器，最多额外一次；延迟退避放上层可取消协程。
// 非幂等提交不能盲目重试，最终 HTTP 状态保留给业务。

// 策略 2：离线缓存（有网用网络，无网用缓存）
public class OfflineCacheInterceptor implements Interceptor {
    private final Context context;

    public OfflineCacheInterceptor(Context context) { this.context = context; }

    @Override
    public Response intercept(Chain chain) throws IOException {
        Request request = chain.request();
        boolean isNetworkAvailable = isNetworkAvailable(context);

        if (!isNetworkAvailable) {
            // 无网络：强制使用缓存，允许 7 天过期
            request = request.newBuilder()
                .cacheControl(new CacheControl.Builder()
                    .maxStale(7, TimeUnit.DAYS).build())
                .build();
        }
        return chain.proceed(request);
    }
}

// 策略 3：网络质量感知，动态调整请求策略
// WiFi/5G → 高清图片、预加载更多数据
// 4G/弱网 → 压缩图片、减少请求
// 2G/无网 → 极简模式、纯缓存
```

### 8.4 网络状态感知

```java
// NetworkCallback 实时监听网络变化（Android 5.0+）
public class NetworkMonitor {
    private ConnectivityManager cm;
    private Network currentNetwork;
    private int currentQuality = QUALITY_UNKNOWN;  // 网络质量等级

    public static final int QUALITY_UNKNOWN = 0;
    public static final int QUALITY_POOR = 1;      // 2G/弱网
    public static final int QUALITY_MODERATE = 2;   // 3G/一般 4G
    public static final int QUALITY_GOOD = 3;        // WiFi/强 4G/5G

    private final ConnectivityManager.NetworkCallback callback =
        new ConnectivityManager.NetworkCallback() {
            @Override
            public void onAvailable(Network network) {
                currentNetwork = network;
                // 等 onCapabilitiesChanged 更新状态。
            }

            @Override
            public void onLost(Network network) {
                if (!network.equals(currentNetwork)) return;
                currentNetwork = null;
                currentQuality = QUALITY_UNKNOWN;
                // 通知业务层：网络已断开
                EventBus.post(new NetworkLostEvent());
            }

            @Override
            public void onCapabilitiesChanged(Network network,
                    NetworkCapabilities caps) {
                // 判断网络质量
                if (caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)) {
                    currentQuality = QUALITY_GOOD;
                } else if (caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR)) {
                    int downBandwidth = caps.getLinkDownstreamBandwidthKbps();
                    if (downBandwidth > 10000) currentQuality = QUALITY_GOOD;      // 4G+
                    else if (downBandwidth > 2000) currentQuality = QUALITY_MODERATE;
                    else currentQuality = QUALITY_POOR;
                }
                EventBus.post(new NetworkQualityEvent(currentQuality));
            }
        };

    public void register(Context context) {
        cm = context.getSystemService(ConnectivityManager.class);
        NetworkRequest request = new NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build();
        cm.registerDefaultNetworkCallback(callback); // API 24+，成对注销
    }

    public void unregister() {
        cm.unregisterNetworkCallback(callback);
    }
}
```

### 8.5 图片加载优化

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         图片加载优化                                        │
└─────────────────────────────────────────────────────────────────────────────┘

1. 使用 Glide / Picasso
─────────────────────────────────────────────────────────────────────────────
   Glide.with(context)
       .load(url)
       .placeholder(R.drawable.placeholder)
       .error(R.drawable.error)
       .override(200, 200)  // 指定大小，避免加载原图
       .into(imageView);

2. 图片压缩
─────────────────────────────────────────────────────────────────────────────
   // 服务端返回合适的尺寸
   // WebP 格式替代 PNG/JPG

3. 图片缓存
─────────────────────────────────────────────────────────────────────────────
   - 内存缓存: LRU 策略
   - 磁盘缓存: 持久化存储
```

### 8.6 网络缓存策略

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         网络缓存策略                                        │
└─────────────────────────────────────────────────────────────────────────────┘

// OkHttp 缓存配置
int cacheSize = 10 * 1024 * 1024;  // 10MB
Cache cache = new Cache(context.getCacheDir(), cacheSize);

OkHttpClient client = new OkHttpClient.Builder()
    .cache(cache)
    .build();

// 强制使用缓存
Request request = new Request.Builder()
    .cacheControl(CacheControl.FORCE_CACHE)
    .url(url)
    .build();

// 强制使用网络
Request request = new Request.Builder()
    .cacheControl(CacheControl.FORCE_NETWORK)
    .url(url)
    .build();

// 允许旧缓存；单个 Call 不会自动先缓存后网络双发
Request request = new Request.Builder()
    .cacheControl(new CacheControl.Builder()
        .maxStale(7, TimeUnit.DAYS)
        .build())
    .url(url)
    .build();
```

---

## 9. APK 体积优化

### 9.1 体积分析

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APK 体积分析                                        │
└─────────────────────────────────────────────────────────────────────────────┘

APK 结构:
├── classes.dex        # 编译后的代码
├── resources.arsc     # 资源索引
├── res/               # 资源文件
│   ├── drawable-xxxhdpi/
│   ├── layout/
│   └── values/
├── lib/               # Native 库
│   ├── armeabi-v7a/
│   └── arm64-v8a/
├── assets/            # 原始资源
├── META-INF/          # 签名信息
└── AndroidManifest.xml

分析命令:
echo "APK 大小分布"
apkanalyzer files list app.apk

echo "使用 APK Analyzer"
android {
    buildTypes {
        release {
            shrinkResources true  // 资源压缩
            minifyEnabled true    // 代码压缩
        }
    }
}
```

### 9.2 R8 完整瘦身策略

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         代码混淆与优化                                      │
└─────────────────────────────────────────────────────────────────────────────┘

1. ProGuard / R8 配置
─────────────────────────────────────────────────────────────────────────────
   android {
       buildTypes {
           release {
               minifyEnabled true      // 启用代码压缩
               shrinkResources true    // 启用资源压缩
               proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'),
                            'proguard-rules.pro'
           }
       }
   }

2. ProGuard 规则
─────────────────────────────────────────────────────────────────────────────
   # proguard-rules.pro
   
   # 保留应用入口
   -keep public class * extends android.app.Activity
   -keep public class * extends android.app.Service
   -keep public class * extends android.content.BroadcastReceiver
   
   # 保留序列化类
   -keepclassmembers class * implements java.io.Serializable {
       static final long serialVersionUID;
       private static final java.io.ObjectStreamField[] serialPersistentFields;
       private void writeObject(java.io.ObjectOutputStream);
       private void readObject(java.io.ObjectInputStream);
   }
   
   # 保留 Native 方法
   -keepclasseswithmembernames class * {
       native <methods>;
   }
   
   # Retrofit / Gson 保留
   -keepattributes Signature
   -keepattributes *Annotation*
   -keep class com.google.gson.** { *; }
   -keep class * implements com.google.gson.TypeAdapterFactory
   -keep class * implements com.google.gson.JsonSerializer
   -keep class * implements com.google.gson.JsonDeserializer
```

### 9.3 资源优化

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         资源优化                                            │
└─────────────────────────────────────────────────────────────────────────────┘

1. 删除无用资源
─────────────────────────────────────────────────────────────────────────────
   android {
       buildTypes {
           release {
               shrinkResources true  // 自动删除未使用的资源
           }
       }
   }
   
   # 手动检查
   ./gradlew :app:lintRelease # 查看 UnusedResources 报告

2. 图片优化
─────────────────────────────────────────────────────────────────────────────
   - 使用 WebP 格式替代 PNG/JPG
   - 使用 Vector Drawable 替代位图
   - 压缩 PNG: pngquant, TinyPNG
   
   # 转换为 WebP
   cwebp -q 80 input.png -o output.webp

3. 资源压缩
─────────────────────────────────────────────────────────────────────────────
   # res/raw/ 下的文件压缩
   android {
       aaptOptions {
           noCompress 'txt', 'mp3'  // 不压缩这些格式
       }
   }

4. 限定密度资源
─────────────────────────────────────────────────────────────────────────────
   # 只保留必要密度
   android {
       defaultConfig {
           resConfigs "zh", "en"  // 只保留中英文
           resConfigs "xxhdpi"    // 只保留 xxhdpi
       }
   }
```

### 9.4 So 动态库优化

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         So 动态库优化                                       │
└─────────────────────────────────────────────────────────────────────────────┘

1. 只保留必要 ABI
─────────────────────────────────────────────────────────────────────────────
   android {
       defaultConfig {
           ndk {
               abiFilters 'armeabi-v7a', 'arm64-v8a'  // 只保留这两种
           }
       }
   }
   
   # 2024年推荐: 只保留 arm64-v8a
   ndk {
       abiFilters 'arm64-v8a'  // 大多数设备已支持 64 位
   }

2. So 文件裁剪
─────────────────────────────────────────────────────────────────────────────
   # 使用 strip 裁剪符号表
   llvm-strip --strip-unneeded libtest.so # 使用匹配 NDK，保留原始符号
   
   # 使用 UPX 压缩 (部分场景)
   # 不把 UPX 用作 Android SO 常规发布方案，需验证 ELF 与 16KB 页兼容

3. 动态加载
─────────────────────────────────────────────────────────────────────────────
   - 非核心功能按需下载
   - 使用 Split APKs 分架构打包
```

---

## 10. 性能分析工具链

### 10.2 CPU Profiler 高级用法

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CPU Profiler                                        │
└─────────────────────────────────────────────────────────────────────────────┘

位置: Android Studio → View → Tool Windows → Profiler

功能:
├── 方法追踪 (Method Tracing)
│   ├── 记录方法执行时间
│   ├── 分析调用栈
│   └── 找出耗时方法
├── 采样 (Sampled)
│   ├── 低开销
│   └── 周期性采样
└── 仪器化 (Instrumented)
    ├── 精确追踪
    └── 高开销

使用方法:
1. 选择要分析的进程
2. 点击 CPU 区域
3. 选择 Record Configuration
4. 点击 Record 开始记录
5. 操作应用
6. 点击 Stop 停止记录
7. 分析结果

分析技巧:
- 关注 Top Down 视图，找出耗时调用链
- 关注 Flame Graph，可视化热点方法
- 关注 Wall Clock Time vs Thread Time
```

### 10.3 Memory Profiler 高级用法

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Memory Profiler                                     │
└─────────────────────────────────────────────────────────────────────────────┘

功能:
├── 实时内存监控
│   ├── Java 堆内存
│   ├── Native 内存
│   └── GC 事件
├── Heap Dump
│   ├── 查看对象数量和大小
│   ├── 分析内存泄漏
│   └── 查看对象引用链
└── Native Memory Profiler (API 26+)
    ├── 追踪 Native 内存分配
    └── 分析 Native 泄漏

使用方法:
1. 选择进程
2. 点击 Memory 区域
3. 操作应用触发内存分配
4. 点击 Capture Heap Dump
5. 分析结果

分析技巧:
- 按 Retained Size 排序，找出大对象
- 查看 Instance 的引用链
- 对比多个 Heap Dump，找出泄漏对象
```

### 10.4 Layout Inspector

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Layout Inspector                                    │
└─────────────────────────────────────────────────────────────────────────────┘

位置: Android Studio → View → Tool Windows → Layout Inspector

功能:
├── 查看视图层级
├── 查看视图属性
├── 查看布局边界
└── 导出视图层级

使用方法:
1. 运行应用到目标页面
2. 打开 Layout Inspector
3. 选择进程和 Activity
4. 点击 View 结构

分析技巧:
- 检查布局层级是否过深
- 检查是否有不可见但占空间的 View
- 检查 View 的属性是否合理
```

### 10.1 Perfetto 深度使用

只采 android.packages_list 无法得到 CPU/帧/锁信息。旧 systrace.py 需要已有 Catapult 工具，不能假定新 SDK 仍带脚本；Android 17 主路径如下。

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

### 10.5 线上监控工具

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LeakCanary                                          │
└─────────────────────────────────────────────────────────────────────────────┘

配置:
// build.gradle
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}

自动检测:
- Activity 泄漏
- Fragment 泄漏
- View 泄漏
- ViewModel 泄漏

手动检测:
// 监控特定对象
AppWatcher.objectWatcher.watch(myObject, "MyObject description")

// 检查是否有泄漏
if (AppWatcher.objectWatcher.hasWatchedObjects) {
    // 有对象正在被监控
}

分析报告:
1. 泄漏对象的引用链
2. 泄漏原因分析
3. 泄漏历史记录
```

### 10.6 Simpleperf（Native CPU Profiling）

```bash
# 在 NDK simpleperf 脚本目录；应用满足 debuggable/profileable 权限。
python3 app_profiler.py -p com.example.app -r "-e cpu-cycles -g --duration 10"
python3 report_html.py -i perf.data -o report.html
```

stat 是计数、record 是采样，都不是无损方法跟踪。`--trace-offcpu` 还需设备/调度事件权限。不存在旧示例的 `--group-colored-events`，`report --protobuf/--proto` 不是生成 Chrome/Perfetto 火焰图的正确流程。report_html.py 消费 perf.data，符号需匹配 ABI/build-id。Android Studio CPU Profiler 本身也支持 Native 采样。
来源：[Simpleperf 应用采样](https://android.googlesource.com/platform/system/extras/+/refs/tags/android-17.0.0_r1/simpleperf/doc/android_application_profiling.md)。

### 10.7 线上性能监控矩阵

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│              线上性能监控工具对比与选型                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┬────────────────────────┬───────────────────┬───────────────────────┐
│  工具                │  开源方                │  核心能力          │  适用场景               │
├──────────────────────┼────────────────────────┼───────────────────┼───────────────────────┤
│  Matrix              │  腾讯微信              │  启动/卡顿/ANR/     │  大型 App，全链路      │
│                      │                        │  泄漏/IO/电量       │  性能监控              │
├──────────────────────┼────────────────────────┼───────────────────┼───────────────────────┤
│  Firebase Perf       │  Google                │  自动采集启动/     │  快速接入，            │
│                      │                        │  网络/渲染          │  无需自建后台          │
├──────────────────────┼────────────────────────┼───────────────────┼───────────────────────┤
│  Sentry              │  Sentry                │  崩溃/ANR/         │  崩溃为主，            │
│                      │                        │  性能事务           │  性能为辅              │
├──────────────────────┼────────────────────────┼───────────────────┼───────────────────────┤
│  Android Vitals      │  Google Play Console   │  ANR率/崩溃率/     │  只支持 Play 分发      │
│                      │                        │  唤醒次数           │  的 App                │
├──────────────────────┼────────────────────────┼───────────────────┼───────────────────────┤
│  自研 APM            │  自研                  │  完全定制           │  有研发资源，          │
│                      │                        │                    │  需要深度定制          │
└──────────────────────┴────────────────────────┴───────────────────┴───────────────────────┘

推荐方案：
  - 小团队：Firebase Performance（免费、自动采集）
  - 中型团队：Matrix（功能全面、开源免费）
  - 大型团队：Matrix + 自研扩展（接入内部监控平台）
```

---

### 10.8 从 Perfetto 时间线到优化决策

以“首屏等待账户数据”为例，在读取、数据库打开、模型解析处添加稳定 trace 名称，采集 `sched`、`am`、`wm`、`gfx`、`view`、`binder_driver` 和 FrameTimeline。启动前开始采集，复现一次动作，结束后在 UI 中确认应用 slice、线程状态和帧轨道都实际存在。

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

主线程 `Running` 主要查计算；`Runnable` 却未运行查 CPU 竞争；同步 Binder 后休眠沿 flow 查服务端；等待数据库锁查持锁事务。若 UI 线程已结束而 FrameTimeline 仍迟到，转查 RenderThread/GPU/SurfaceFlinger。优化必要依赖链（例如先显示本地缓存、后台刷新），不要把所有初始化盲目并行化。


## 11. 面试常见问题

### 11.1 启动优化问题

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  Q: 冷启动流程是什么？                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  A:                                                                          │
│  1. Launcher startActivity()                                                │
│  2. ATMS.startActivity()                                                    │
│  3. Zygote fork 进程                                                        │
│  4. ActivityThread.main()                                                   │
│  5. bindApplication() → Application.onCreate()                             │
│  6. handleLaunchActivity() → Activity.onCreate/onStart/onResume            │
│  7. performTraversals() → 首帧绘制                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Q: 如何优化冷启动？                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  A:                                                                          │
│  1. Application.onCreate() 异步初始化非核心 SDK                             │
│  2. 使用 IdleHandler 延迟初始化                                             │
│  3. 布局优化: 减少层级、使用 ViewStub                                       │
│  4. 避免主线程 IO 操作                                                      │
│  5. 预加载 Class                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 渲染优化问题

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  Q: 为什么 16ms 一帧？                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  A: 60fps = 1000ms / 60 = 16.6ms                                           │
│     屏幕刷新率 60Hz，每秒刷新 60 次，每帧需要在 16ms 内完成                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Q: 什么是 VSync？                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  A: 垂直同步信号，由显示器发出                                              │
│     - 保证 CPU/GPU 生成帧与显示器刷新同步                                   │
│     - 避免画面撕裂                                                          │
│     - Choreographer 接收 VSync，调度绘制                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Q: 如何减少过度绘制？                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  A:                                                                          │
│  1. 移除不必要的背景                                                        │
│  2. 使用 canvas.clipRect() 限制绘制区域                                    │
│  3. 减少布局层级                                                            │
│  4. 使用 ViewStub 延迟加载                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.3 内存优化问题

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  Q: 常见内存泄漏场景？                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  A:                                                                          │
│  1. 静态变量持有 Context                                                    │
│  2. 非静态内部类/匿名内部类持有外部类引用                                   │
│  3. Handler 导致的泄漏                                                      │
│  4. 注册的广播/事件未取消                                                   │
│  5. 单例模式持有 Context                                                    │
│  6. 资源未关闭 (Cursor, Stream)                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Q: 如何检测内存泄漏？                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  A:                                                                          │
│  1. LeakCanary 自动检测                                                     │
│  2. Memory Profiler 分析 Heap Dump                                          │
│  3. 多次 GC 后对象数量不减，可能有泄漏                                      │
│  4. 使用 MAT 分析引用链                                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Q: Bitmap 内存优化？                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  A:                                                                          │
│  1. 使用 inSampleSize 缩放                                                  │
│  2. 使用 RGB_565 (2字节) 替代 ARGB_8888 (4字节)                            │
│  3. 及时 recycle()                                                          │
│  4. 使用 Glide 等图片库自动管理                                             │
│  5. 复用 Bitmap (inBitmap)                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.4 综合问题

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  Q: ANR 产生原因和解决方案？                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  A:                                                                          │
│  产生原因:                                                                   │
│  1. 主线程执行耗时操作 (> 5s)                                               │
│  2. BroadcastReceiver onReceive 耗时 (> 10s)                               │
│  3. Service 生命周期方法耗时                                                │
│  4. ContentProvider onCreate 耗时                                          │
│                                                                             │
│  解决方案:                                                                   │
│  1. 耗时操作放子线程                                                        │
│  2. 结构化协程/有界 Executor；AsyncTask 已废弃                              │
│  3. 延迟非必要工作，postDelayed 不会消除主线程计算成本                                                   │
│  4. 优化锁的使用，避免死锁                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Q: 如何做电量优化？                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  A:                                                                          │
│  1. 减少网络请求频率，批量处理                                              │
│  2. 使用 WorkManager 执行后台任务                                           │
│  3. 及时释放 WakeLock                                                       │
│  4. GPS 按需开启，降低精度                                                  │
│  5. 适配 Doze 模式和 App Standby                                            │
│  6. 减少后台 CPU 使用                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. 总结

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         性能优化总结                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  优化维度       │  核心要点                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  启动优化       │  异步初始化、延迟加载、布局优化、MultiDex 优化            │
├─────────────────────────────────────────────────────────────────────────────┤
│  渲染优化       │  16ms 法则、减少过度绘制、布局层级优化、VSync 同步        │
├─────────────────────────────────────────────────────────────────────────────┤
│  内存优化       │  避免泄漏、Bitmap 优化、数据结构优化、及时回收            │
├─────────────────────────────────────────────────────────────────────────────┤
│  电量优化       │  减少唤醒、网络批量、WorkManager、Doze 适配               │
├─────────────────────────────────────────────────────────────────────────────┤
│  网络优化       │  连接复用、请求压缩、缓存策略、图片优化                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  APK 优化       │  代码混淆、资源压缩、So 裁剪、动态加载                    │
└─────────────────────────────────────────────────────────────────────────────┘

性能优化口诀:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  启动要快，异步加载                                                         │
│  渲染流畅，十六毫秒                                                         │
│  内存省用，泄漏要防                                                         │
│  电量优化，后台休眠                                                         │
│  网络高效，缓存优先                                                         │
│  包体精简，混淆压缩                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

常用工具速查:
┌─────────────────────────────────────────────────────────────────────────────┐
│  工具              │  用途                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  CPU Profiler      │  分析方法耗时、调用栈                                  │
│  Memory Profiler   │  分析内存分配、检测泄漏                                │
│  Layout Inspector  │  查看布局层级、属性                                    │
│  Systrace          │  分析系统性能、帧率                                    │
│  LeakCanary        │  自动检测内存泄漏                                      │
│  GPU Profiler      │  分析过度绘制、渲染性能                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*本文档由 OpenClaw 生成*