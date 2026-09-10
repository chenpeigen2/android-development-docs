# Android 虚拟机详解

_作者：OpenClaw_
_日期：2026-03-08_

---

## 目录

- [1. 概述](#1-概述)
- [2. JVM vs Dalvik vs ART](#2-jvm-vs-dalvik-vs-art)
  - [2.1 架构对比](#21-架构对比)
  - [2.2 基于栈 vs 基于寄存器](#22-基于栈-vs-基于寄存器)
  - [2.3 对比示例](#23-对比示例)
- [3. Dalvik 虚拟机](#3-dalvik-虚拟机)
  - [3.1 Dalvik 特点](#31-dalvik-特点)
  - [3.2 Dalvik 启动流程](#32-dalvik-启动流程)
  - [3.3 Dalvik JIT 编译](#33-dalvik-jit-编译)
- [4. ART 虚拟机](#4-art-虚拟机)
  - [4.1 ART 特点](#41-art-特点)
  - [4.2 ART 编译策略](#42-art-编译策略)
  - [4.3 dex2oat 编译](#43-dex2oat-编译)
  - [4.4 ART 运行时](#44-art-运行时)
    - [4.4.1 Runtime 创建、启动和 Zygote fork 的生命周期](#441-runtime-创建启动和-zygote-fork-的生命周期)
    - [4.4.2 解释、JIT 与 AOT 的方法入口协作](#442-解释jit-与-aot-的方法入口协作)
- [5. DEX 文件格式](#5-dex-文件格式)
  - [5.1 DEX 文件结构](#51-dex-文件结构)
  - [5.2 DEX vs CLASS](#52-dex-vs-class)
- [6. ODEX 与 OAT 文件](#6-odex-与-oat-文件)
  - [6.1 ODEX 文件 (Dalvik)](#61-odex-文件-dalvik)
  - [6.2 OAT 文件 (ART)](#62-oat-文件-art)
  - [6.3 编译流程对比](#63-编译流程对比)
- [7. 内存管理](#7-内存管理)
  - [7.1 Dalvik 内存管理](#71-dalvik-内存管理)
  - [7.2 ART 内存管理](#72-art-内存管理)
  - [7.3 GC 类型](#73-gc-类型)
- [8. ART GC 算法深度解析](#8-art-gc-算法深度解析)
  - [8.1 CMS (Concurrent Mark Sweep) - Android 5-7](#81-cms-concurrent-mark-sweep---android-5-7)
  - [8.2 CC (Concurrent Copying) - Android 8+](#82-cc-concurrent-copying---android-8)
    - [8.2.1 CC RunPhases：真实顺序和配置分支](#821-cc-runphases真实顺序和配置分支)
    - [8.2.2 CMC RunPhases：标记和压缩不是同一暂停](#822-cmc-runphases标记和压缩不是同一暂停)
    - [8.2.3 CMC 的 MarkingPause：为什么必须处理新分配和弱引用](#823-cmc-的-markingpause为什么必须处理新分配和弱引用)
  - [8.3 HSC (Homogeneous Space Compact) - 后台压缩](#83-hsc-homogeneous-space-compact---后台压缩)
    - [8.3.1 HSC 的拒绝条件和真正的 STW](#831-hsc-的拒绝条件和真正的-stw)
  - [8.4 GC 触发策略](#84-gc-触发策略)
    - [8.4.1 分配失败不立刻等于 OOM](#841-分配失败不立刻等于-oom)
- [9. GC 日志解读](#9-gc-日志解读)
  - [9.1 ART GC 日志格式详解](#91-art-gc-日志格式详解)
  - [9.2 实战：通过 GC 日志定位问题](#92-实战通过-gc-日志定位问题)
  - [9.3 logcat GC 相关命令](#93-logcat-gc-相关命令)
- [10. JIT 编译与 Profile-Guided Compilation](#10-jit-编译与-profile-guided-compilation)
  - [10.1 ART JIT 编译器详解](#101-art-jit-编译器详解)
  - [10.2 Profile-Guided Compilation (PGC)](#102-profile-guided-compilation-pgc)
  - [10.3 编译层级](#103-编译层级)
  - [10.4 Deoptimization（逆优化）](#104-deoptimization逆优化)
- [11. ART 对象模型与内存布局](#11-art-对象模型与内存布局)
  - [11.1 ART 对象内存布局](#111-art-对象内存布局)
  - [11.2 ClassLinker 类加载](#112-classlinker-类加载)
  - [11.3 ART Method 模型](#113-art-method-模型)
- [12. ART 线程模型](#12-art-线程模型)
  - [12.1 ART 线程结构 (ArtThread)](#121-art-线程结构-artthread)
  - [12.2 线程状态转换](#122-线程状态转换)
  - [12.3 synchronized 在 ART 中的实现](#123-synchronized-在-art-中的实现)
- [13. 总结](#13-总结)
- [固定版本源码索引](#固定版本源码索引)

---

## 1. 概述

Android 虚拟机是 Android 系统的核心组件，负责运行应用程序代码。从 Dalvik 到 ART，Android 虚拟机经历了重大演进。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Android 虚拟机演进                                   │
└─────────────────────────────────────────────────────────────────────────────┘

Android 1.0 - 4.4          Android 5.0+
┌─────────────────┐        ┌─────────────────┐
│     Dalvik      │   →    │      ART        │
│   (JIT 编译)    │        │  (AOT + JIT)    │
└─────────────────┘        └─────────────────┘
     DEX + ODEX                  DEX + OAT
```

---

## 2. JVM vs Dalvik vs ART

### 2.1 架构对比

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         虚拟机架构对比                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────┬───────────────────┬───────────────────┐
│        JVM        │      Dalvik       │        ART        │
├───────────────────┼───────────────────┼───────────────────┤
│ 基于栈架构       │ 基于寄存器架构   │ 基于寄存器架构   │
├───────────────────┼───────────────────┼───────────────────┤
│ .class 文件      │ .dex 文件        │ .dex → .oat      │
├───────────────────┼───────────────────┼───────────────────┤
│ JIT 编译         │ JIT 编译         │ AOT + JIT        │
├───────────────────┼───────────────────┼───────────────────┤
│ 堆内存较大       │ 堆内存较小       │ 堆内存优化       │
├───────────────────┼───────────────────┼───────────────────┤
│ 桌面/服务器      │ 移动设备         │ 移动设备         │
└───────────────────┴───────────────────┴───────────────────┘
```

### 2.2 基于栈 vs 基于寄存器

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    基于栈 vs 基于寄存器                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         JVM (基于栈)                                        │
└─────────────────────────────────────────────────────────────────────────────┘

计算 a + b:
┌─────────────────────────────────────────────────────────────────────────────┐
│  操作数栈                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  push a      ──►  [a]                                               │  │
│  │  push b      ──►  [a, b]                                            │  │
│  │  add         ──►  [a+b]   (弹出两个，压入结果)                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  特点：                                                                      │
│  - 指令数量多（需要 push/pop 操作）                                         │
│  - 代码紧凑（指令短）                                                       │
│  - 移植性好                                                                  │
│  - 描述字节码解释模型，不直接决定 JIT/AOT 后机器码性能                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      Dalvik/ART (基于寄存器)                                │
└─────────────────────────────────────────────────────────────────────────────┘

计算 a + b:
┌─────────────────────────────────────────────────────────────────────────────┐
│  寄存器                                                                      │
│  r0 = a                                                                     │
│  r1 = b                                                                     │
│  add r2, r0, r1   ──►  r2 = r0 + r1                                        │
│                                                                             │
│  特点：                                                                      │
│  - 指令数量少（直接操作寄存器）                                             │
│  - 代码较长（指令包含寄存器编号）                                           │
│  - 通常减少解释器分派次数，不保证所有程序更快                                                                │
│  - 适合移动设备（减少内存访问）                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 对比示例

```java
// Java 源码
int sum(int a, int b) {
    return a + b;
}
```

**JVM 字节码 (基于栈):**
```text
iload_1    // 将局部变量1压入栈
iload_2    // 将局部变量2压入栈
iadd       // 弹出两个值，相加，压入结果
ireturn    // 返回栈顶值
```

**Dalvik 字节码 (基于寄存器):**
```text
add-int v0, v1, v2   // v0 = v1 + v2
return v0            // 返回 v0
```

---

## 3. Dalvik 虚拟机

### 3.1 Dalvik 特点

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Dalvik 虚拟机特点                                   │
└─────────────────────────────────────────────────────────────────────────────┘

1. 基于寄存器架构
   - 减少内存访问
   - 提高执行效率

2. DEX 文件格式
   - 多个 .class 合并为一个 .dex
   - 共享常量池，减少冗余

3. JIT 编译 (Android 2.2+)
   - 运行时编译热点代码
   - 缓存编译结果

4. 内存优化
   - 进程共享
   - 写时复制 (Copy-on-Write)
```

### 3.2 Dalvik 启动流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Dalvik 启动流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Zygote 进程
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. ZygoteInit.main()                                                      │
│     - 此时 VM 已由 native AndroidRuntime 启动，再进入 Java main                                                    │
│     - 预加载系统类和资源                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. fork() 新进程                                                          │
│     - 继承 Dalvik 实例                                                      │
│     - 共享预加载的类和资源                                                  │
└──────────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. 加载应用 DEX 文件                                                       │
│     - PathClassLoader 加载 classes.dex                                     │
│     - 解析 DEX 文件结构                                                     │
└──────────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. JIT 编译 (热点代码)                                                     │
│     - trace-based JIT                                                       │
│     - 编译频繁执行的方法                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. 执行应用代码                                                            │
│     - 解释执行或 JIT 执行                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Dalvik JIT 编译

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Dalvik JIT 编译                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Trace-based JIT (基于追踪的 JIT)                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. 解释执行                                                              │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ Dalvik 解释器执行字节码                                         │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                        │                                                  │
│                        ▼                                                  │
│  2. 热点检测                                                              │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ 热 trace/回边达到阈值后触发编译（历史 Dalvik 模型）                               │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                        │                                                  │
│                        ▼                                                  │
│  3. 编译                                                                  │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ 将热点代码编译为本地机器码                                      │   │
│     │ 缓存编译结果 (code cache)                                       │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                        │                                                  │
│                        ▼                                                  │
│  4. 执行                                                                  │
│     ┌─────────────────────────────────────────────────────────────────┐   │
│     │ 后续直接执行编译后的机器码                                      │   │
│     └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. ART 虚拟机

### 4.1 ART 特点

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ART 虚拟机特点                                      │
└─────────────────────────────────────────────────────────────────────────────┘

1. AOT (Ahead-of-Time) 编译
   - 按编译过滤器和 profile 在安装/后台阶段编译选定 DEX 方法
   - 运行时直接执行机器码
   - 启动速度快

2. JIT + AOT 混合 (Android 7.0+)
   - 未有可用 AOT 代码时解释执行并按热点触发 JIT
   - 后台 AOT 编译热点代码
   - 平衡安装速度和运行效率

3. 更好的 GC
   - 并发 GC
   - 压缩 GC
   - 减少暂停时间

4. 64 位支持
   - 更大的地址空间
   - 更好的性能
```

### 4.2 ART 编译策略

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ART 编译策略演进                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Android 5.0-6.0: 纯 AOT
┌─────────────────────────────────────────────────────────────────────────────┐
│  安装时                                                                      │
│  DEX ──────► dex2oat ──────► OAT (本地机器码)                              │
│                                                                             │
│  优点: 运行速度快，启动快                                                   │
│  缺点: 安装慢，占用存储大                                                   │
└─────────────────────────────────────────────────────────────────────────────┘

Android 7.0+: JIT + AOT 混合
┌─────────────────────────────────────────────────────────────────────────────┐
│  首次运行                                                                    │
│  DEX ──────► JIT 编译热点 ──────► 缓存                                     │
│                                                                             │
│  后台                                                                        │
│  热点代码 ──────► dex2oat ──────► OAT                                      │
│                                                                             │
│  后续运行                                                                    │
│  OAT + JIT 缓存 ──────► 直接执行                                            │
│                                                                             │
│  优点: 安装快，运行快，存储优化                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 dex2oat 编译

```kotlin
/**
 * dex2oat 编译过程
 *
 * 1. 读取 DEX 文件
 * 2. 解析类、方法、字段
 * 3. 编译为本地机器码
 * 4. 生成 OAT 文件
 */

// dex2oat 命令
//dex2oat --dex-file=classes.dex --oat-file=classes.oat

// OAT 文件结构
/**
 * OAT Header
 * ├── dex_file_count
 * ├── executable_offset
 * ├── key_value_store
 * └── oat_dex_files[]
 *
 * OAT Dex File
 * ├── dex_file_location
 * ├── dex_file_checksum
 * ├── dex_file_pointer
 * ├── class_offsets[]
 * └── lookup_table
 *
 * OAT Class
 * ├── status (kNotReady, kVerified, kInitialized)
 * ├── method_count
 * └── method_offsets[]
 */
```

### 4.4 ART 运行时

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ART 运行时架构                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  应用进程                                                                    │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         ART Runtime                                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │  │
│  │  │   Class    │  │   Method   │  │   Field     │                 │  │
│  │  │   Linker   │  │   Invoker  │  │   Accessor  │                 │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │  │
│  │                                                                      │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐│  │
│  │  │                    JIT Compiler                                ││  │
│  │  │  - JIT 编译热点代码                                            ││  │
│  │  │  - 生成优化后的机器码                                          ││  │
│  │  └─────────────────────────────────────────────────────────────────┘│  │
│  │                                                                      │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐│  │
│  │  │                    Garbage Collector                           ││  │
│  │  │  - CMC (Concurrent Mark Compact) / CC 等配置分支                                ││  │
│  │  │  - CC 使用 RegionSpace 与读屏障，不是固定二等分堆                                    ││  │
│  │  └─────────────────────────────────────────────────────────────────┘│  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

#### 4.4.1 Runtime 创建、启动和 Zygote fork 的生命周期

`Runtime::Create()`/`Init()` 建立运行时，`Runtime::Start()` 才进入启动阶段。GC heap、ClassLinker、intern table、JNI、线程列表与 boot image 的初始化有依赖顺序，不能在 Java ZygoteInit.main 内“再创建 VM”：Java main 已依赖这些组件才能执行。

```text
app_process / AndroidRuntime
  -> JNI_CreateJavaVM
     -> Runtime::Create / Runtime::Init
        -> 当前 native 主线程 Attach 到 ART
        -> 建立 Heap、boot class path、ClassLinker、JNI 等
     -> Runtime::Start
        -> core native 注册、运行时线程与 JIT 等启动策略
  -> Java ZygoteInit.main
     -> 类/资源预加载
     -> fork 前停止或协调不允许跨 fork 遗留的线程状态
     -> fork
        父：继续接受启动请求
        子：修复 TID、线程/锁、GC/JIT、运行参数与安全身份
             -> ActivityThread.main
```

这是生命周期概览，不是每个产品调用点完全相同的函数逐行拷贝。特别要区分“共享同一个虚拟机实例”与 fork 的地址空间快照：父子有独立的 Runtime 状态和线程，未修改的物理页可以共享，写入触发 COW。

`Runtime::PreZygoteFork()` 会协调 JIT、线程与 Heap；`PostZygoteFork()` 处理子进程阶段的 JIT 等恢复。不能把 fork 前所有线程原样复制成一组可运行子线程。预加载有利于启动和共享，但把带 native 线程/文件状态的业务单例随意预加载可能带来 fork 后不一致。

#### 4.4.2 解释、JIT 与 AOT 的方法入口协作

一次方法调用通常先由解析和 dispatch 确定 ArtMethod。已有匹配的 AOT/JIT entry point 时跳转机器码；没有可用代码时可经过解释桥，热点累计再排队 JIT。编译完成后更新后续入口，OSR 另负责正在运行的循环切换。

| 阶段 | 需要维护的状态 | 常见误判 |
|------|----------------|----------|
| 安装/后台编译 | dex checksum、class loader context、过滤器、profile | 只要磁盘有 odex 就一定能执行 |
| 类加载/链接 | defining loader、DEX 索引、类状态、解析缓存 | loadClass 一定会运行 clinit |
| JIT 排队/完成 | 编译类别、代码缓存、入口发布 | JIT 线程一创建，所有方法都是机器码 |
| 逆优化 | 编译帧映射、解释帧和恢复 PC | 换 DEX 文件就能无条件替换正在执行的类 |
| 进程终止 | shutdown 协调（若有序退出） | Android 杀进程也必定执行所有 Java finally |

调试器插桩或 ART 检查可改变入口和执行方式，性能结论需说明是否启用这些机制。下文的 GC 与锁也依赖线程是否正在 managed 状态，而不只依赖 Linux 是否把线程调度上 CPU。

---

## 5. DEX 文件格式

### 5.1 DEX 文件结构

下图为传统 standard DEX 035–040 的 header 形态（035 只是示例 magic）。固定 tag 的 `DexFile::HeaderV41` 增加 `container_size_` 与 `header_offset_`，不能把 112 字节及 035 当作 Android 17 唯一格式。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEX 文件结构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  DEX Header (112 bytes)                                                    │
│  ├── magic[8]         = "dex\n035\0"                                       │
│  ├── checksum         = Adler32 校验和                                     │
│  ├── signature[20]    = SHA-1 签名                                         │
│  ├── file_size        = 文件大小                                           │
│  ├── header_size      = 头大小 (0x70)                                      │
│  ├── endian_tag       = 字节序 (0x12345678)                                │
│  ├── link_size        = 链接段大小                                         │
│  ├── link_off         = 链接段偏移                                         │
│  ├── map_off          = Map 偏移                                           │
│  ├── string_ids_size  = 字符串数量                                         │
│  ├── string_ids_off   = 字符串偏移                                         │
│  ├── type_ids_size    = 类型数量                                           │
│  ├── type_ids_off     = 类型偏移                                           │
│  ├── proto_ids_size   = 原型数量                                           │
│  ├── proto_ids_off    = 原型偏移                                           │
│  ├── field_ids_size   = 字段数量                                           │
│  ├── field_ids_off    = 字段偏移                                           │
│  ├── method_ids_size  = 方法数量                                           │
│  ├── method_ids_off   = 方法偏移                                           │
│  ├── class_defs_size  = 类定义数量                                         │
│  ├── class_defs_off   = 类定义偏移                                         │
│  └── data_size        = 数据段大小                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  String IDs (字符串索引)                                                    │
│  ├── string_id[0]     → string_data_offset                                │
│  ├── string_id[1]     → string_data_offset                                │
│  └── ...                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Type IDs (类型索引)                                                        │
│  ├── type_id[0]       → descriptor_idx (string_id)                        │
│  ├── type_id[1]       → descriptor_idx                                    │
│  └── ...                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Proto IDs (原型索引)                                                       │
│  ├── proto_id[0]      → shorty_idx, return_type_idx, parameters_off       │
│  └── ...                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Field IDs (字段索引)                                                       │
│  ├── field_id[0]      → class_idx, type_idx, name_idx                     │
│  └── ...                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Method IDs (方法索引)                                                      │
│  ├── method_id[0]     → class_idx, proto_idx, name_idx                    │
│  └── ...                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Class Defs (类定义)                                                        │
│  ├── class_def[0]                                                        │
│  │   ├── class_idx      → type_id                                         │
│  │   ├── access_flags                                                     │
│  │   ├── superclass_idx                                                   │
│  │   ├── interfaces_off                                                   │
│  │   ├── source_file_idx                                                  │
│  │   ├── annotations_off                                                  │
│  │   ├── class_data_off                                                   │
│  │   └── static_values_off                                                │
│  └── ...                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Data (数据区)                                                              │
│  ├── string_data                                                          │
│  ├── class_data                                                           │
│  ├── code (方法字节码)                                                     │
│  └── ...                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 DEX vs CLASS

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEX vs CLASS 文件对比                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  CLASS 文件 (JVM)                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                        │
│  │  A.class   │  │  B.class   │  │  C.class   │                        │
│  │             │  │             │  │             │                        │
│  │ 常量池 A   │  │ 常量池 B   │  │ 常量池 C   │                        │
│  │ 方法 A     │  │ 方法 B     │  │ 方法 C     │                        │
│  │ 字段 A     │  │ 字段 B     │  │ 字段 C     │                        │
│  └─────────────┘  └─────────────┘  └─────────────┘                        │
│                                                                             │
│  问题: 每个类都有独立的常量池，存在大量重复字符串                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  DEX 文件 (Dalvik/ART)                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │                          classes.dex                                  ││
│  │  ┌─────────────────────────────────────────────────────────────────┐││
│  │  │ 共享常量池 (所有类共用)                                        │││
│  │  │ - 字符串只存储一次                                             │││
│  │  │ - 类型描述符共享                                               │││
│  │  └─────────────────────────────────────────────────────────────────┘││
│  │                                                                       ││
│  │  类 A | 类 B | 类 C | ...                                            ││
│  └───────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  优势: 共享常量池，减少冗余，文件体积更小                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. ODEX 与 OAT 文件

### 6.1 ODEX 文件 (Dalvik)

Dalvik 的 ODEX 是 dexopt 产生的优化 DEX，主要保存验证/链接相关信息和 quickening 后的字节码；不能把它说成 ART 的机器码产物。历史系统包可以带同目录 `.odex`，dalvik-cache 保存优化缓存；`oat/arm64/base.odex` 是 ART 命名方式，不属于 Dalvik。

### 6.2 OAT 文件 (ART)

ART 的 OAT 容纳代码元数据及经过编译的机器码；应用产物虽常以 `.odex` 为扩展名，但不能因此当作 Dalvik ODEX。现代产物要区分：

```text
APK / DEX             原始程序输入
OAT / .odex           编译代码、OatHeader、方法/DEX 关联元数据
.vdex                 验证依赖等，是否携带 DEX 与编译配置有关
.art                  boot/app image 中预初始化的运行时对象
```

不是所有方法都必须有机器码；`verify`、`speed-profile` 等过滤器决定编译范围，找不到可用代码时仍可解释/JIT。不能假定原始 DEX 总内嵌在 OAT，也不能把 `.art` 说成首次运行 JIT 自动写出的缓存。产物位置受 ART Service、架构、安装布局和模块配置影响。

---

### 6.3 编译流程对比

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         编译流程对比                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Dalvik:
┌─────────────────────────────────────────────────────────────────────────────┐
│  .java → javac → .class → dx → .dex → dexopt → .odex                       │
│                                          │                                                                  │
│                                          └── 安装时或首次运行               │
└─────────────────────────────────────────────────────────────────────────────┘

ART (Android 5-6):
┌─────────────────────────────────────────────────────────────────────────────┐
│  .java → javac → .class → dx/d8 → .dex → dex2oat → .oat                    │
│                                                    │                                                        │
│                                                    └── 安装时             │
└─────────────────────────────────────────────────────────────────────────────┘

ART (Android 7+):
┌─────────────────────────────────────────────────────────────────────────────┐
│  .java → javac → .class → d8 → .dex                                        │
│                                      │                                                                  │
│                                      ├── JIT (运行时)                           │
│                                      │                                                                  │
│                                      └── dex2oat (后台) → .oat          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. 内存管理

### 7.1 Dalvik 内存管理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Dalvik 堆内存                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Dalvik 堆结构:                                                             │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │ Active 堆││
│  │ - 新对象分配                                                          ││
│  │ - 触发 GC                                                             ││
│  └───────────────────────────────────────────────────────────────────────┘│
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │ Zygote 堆││
│  │ - 预加载的类和资源                                                    ││
│  │ - 进程间共享 (Copy-on-Write)                                          ││
│  └───────────────────────────────────────────────────────────────────────┘│
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │ 大对象分配（历史 Dalvik，不套用 ART 独立 LOS）││
│  │ - 不能据此推导 Dalvik 有 ART 的 LargeObjectSpace                                                     ││
│  └───────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘

GC 算法: Mark-Sweep
- 标记阶段: 从 GC Root 遍历，标记存活对象
- 清理阶段: 回收未标记的对象
- 缺点: 会产生内存碎片
```

### 7.2 ART 内存管理

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ART 堆内存                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ART 堆结构:                                                                │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │ Image Space││
│  │ - 预加载的类对象                                                       ││
│  │ - 可映射共享；含可写运行时状态，不保证整个空间只读                                                     ││
│  └───────────────────────────────────────────────────────────────────────┘│
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │ Zygote Space││
│  │ - Zygote 进程的对象                                                    ││
│  │ - Copy-on-Write                                                        ││
│  └───────────────────────────────────────────────────────────────────────┘│
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │ Alloc Space (Bump Pointer)││
│  │ - 新对象分配                                                          ││
│  │ - 指针碰撞分配                                                        ││
│  └───────────────────────────────────────────────────────────────────────┘│
│  ┌───────────────────────────────────────────────────────────────────────┐│
│  │ Large Object Space││
│  │ - 大型 primitive array 等，阈值/分配资格由 Heap 配置决定                                                      ││
│  │ - 独立管理                                                             ││
│  └───────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘

GC 算法:
1. CMS：保留为历史/配置路径，不能概括所有 Android 5–7 设备
2. CC 与 CMC：当前按构建和 Runtime 配置选择，见第 8 章
   - 压缩内存，消除碎片
   - 并发执行，减少暂停
```

### 7.3 GC 类型

`GcCause` 是**触发原因**，不等于收集器算法或“是否 STW”：

| 原因 | 语义 |
|------|------|
| `kGcCauseForAlloc` | 分配失败的线程等待 GC 后重试；不意味着所有 GC 阶段都暂停所有线程 |
| `kGcCauseBackground` | 为后续分配提前准备空间；并发 GC 仍有暂停/握手阶段 |
| `kGcCauseExplicit` | 显式请求，如 System.gc() |
| `kGcCauseForNativeAlloc` | native 分配水位触发 |
| `kGcCauseCollectorTransition` | 收集器转换 |
| `kGcCauseHomogeneousSpaceCompact` | 适用 CMS 配置的同类空间压缩 |

固定 tag 的枚举没有 `kGcCauseOOM`。分配重试、软引用清理等仍使用具体 cause；最后无法满足分配才抛 OOM。

---

## 8. ART GC 算法深度解析

### 8.1 CMS (Concurrent Mark Sweep) - Android 5-7

CMS 保留为历史原理比较：从根标记，处理并发期间引用变化，再清扫未标记对象；其非移动空间可能碎片化。重新标记主要补齐并发修改造成的可达性遗漏，不是“清理浮动垃圾”。本文不把某个桌面 JVM 的 10ms/100ms 暂停数字当作 ART 保证。

Android 17 的 `Heap` 同时包含 CC、CMC 和相关兼容路径。`gUseUserfaultfd` 对应的配置要求前台 `kCollectorTypeCMC`、后台 `kCollectorTypeCMCBackground`；使用读屏障的 CC 配置则使用 RegionSpace。要以 Runtime 参数与设备配置判定当前算法，不能只凭 API 版本指定 CC。

### 8.2 CC (Concurrent Copying) - Android 8+

`ConcurrentCopying::RunPhases()` 的实际主序列：

```text
InitializePhase()
  -> 可选 MarkingPhase()（generational 配置且非 young collection）
  -> FlipThreadRoots()
  -> CopyingPhase()
  -> ReclaimPhase()
  -> FinishPhase()
```

CC 把 RegionSpace 的 region 标成 from-space / to-space / unevac-from-space。需要疏散的 region 中，存活对象被复制到目的 region，转发信息和读屏障让 mutator 取得新地址；未疏散 region 可原位保留，young/full 路径也不同。它不是把整个 Java 堆切成两个等大的半空间、每次完整交换，因此“固定浪费一半堆”和“所有存活对象每次都复制”均不成立。

`FlipThreadRoots()` 协调线程根和入口，复制阶段使用读屏障及标记队列追踪并发可达性。回收阶段释放可回收的 from-space regions，并处理其他空间的对象；non-moving/LOS 等空间不会因此彻底消除碎片。低暂停也不意味着整个周期零 STW。

**CMC 对照。** `gc/collector/mark_compact.cc` 的 `MarkCompact` 不是 CC 别名。它先标记并计算活对象压缩位置，更新根/引用，利用 userfaultfd 等配置路径协调页级并发压缩和 mutator 缺页访问，最后回收空页；其主要移动空间是 bump-pointer space，而不是 CC 的 region 疏散复制模型。后台 CMC 压缩选择也不能写成统一的 HSC。

#### 8.2.1 CC RunPhases：真实顺序和配置分支

下面直接节选 `ConcurrentCopying::RunPhases()` 的控制骨架。保留验证分支很重要：debug 验证会额外暂停，不能把调试结果当作发布配置暂停上限。

```cpp
void ConcurrentCopying::RunPhases() {
  CHECK(kUseBakerReadBarrier || kUseTableLookupReadBarrier);
  CHECK(!is_active_);
  is_active_ = true;
  Thread* self = Thread::Current();
  thread_running_gc_ = self;
  Locks::mutator_lock_->AssertNotHeld(self);
  {
    ReaderMutexLock mu(self, *Locks::mutator_lock_);
    InitializePhase();
    // In case of forced evacuation, all regions are evacuated and hence no
    // need to compute live_bytes.
    if (use_generational_cc_ && !young_gen_ && !force_evacuate_all_) {
      MarkingPhase();
    }
  }
  ScopedPriorityChange spc(self);
  if (kUseBakerReadBarrier && kGrayDirtyImmuneObjects) {
    // Switch to read barrier mark entrypoints before we gray the objects. This is required in case
    // a mutator sees a gray bit and dispatches on the entrypoint. (b/37876887).
    ActivateReadBarrierEntrypoints();
    // Gray dirty immune objects concurrently to reduce GC pause times. We re-process gray cards in
    // the pause.
    ReaderMutexLock mu(self, *Locks::mutator_lock_);
    GrayAllDirtyImmuneObjects();
    spc.SetToNormalOrBetter();
  }
  FlipThreadRoots();
  {
    ReaderMutexLock mu(self, *Locks::mutator_lock_);
    spc.Reset();
    CopyingPhase();
  }
  // Verify no from space refs. This causes a pause.
  if (kEnableNoFromSpaceRefsVerification) {
    TimingLogger::ScopedTiming split("(Paused)VerifyNoFromSpaceReferences", GetTimings());
    ScopedPause pause(this, false);
    CheckEmptyMarkStack();
    if (kVerboseMode) {
      LOG(INFO) << "Verifying no from-space refs";
    }
    VerifyNoFromSpaceReferences();
    if (kVerboseMode) {
      LOG(INFO) << "Done verifying no from-space refs";
    }
    CheckEmptyMarkStack();
  }
  {
    ReaderMutexLock mu(self, *Locks::mutator_lock_);
    ReclaimPhase();
  }
  FinishPhase();
  CHECK(is_active_);
  is_active_ = false;
  thread_running_gc_ = nullptr;
}
```

- InitializePhase 建立这一轮 region/标记相关状态；GC 线程只在需要访问 managed 对象的区段获取 mutator lock 共享访问。
- generational 且非 young 且非强制全疏散时才先 MarkingPhase，计算存活信息指导哪些 region 值得疏散。young 与 full 不应套用同一“每次先扫描所有对象”描述。
- ActivateReadBarrierEntrypoints 必须先于把对象变 gray，否则 mutator 看到 gray 后可能进入错误的读屏障入口。
- FlipThreadRoots 协调所有线程根和访问入口；CopyingPhase 并发复制/扫描，处理 mark stacks 与引用。转发信息使并发遇到同一对象的线程收敛到同一目的对象，而不是复制出多个可见实例。
- ReclaimPhase 不只是交换两个指针：要依据 region 类型及对象存活状态回收，处理非移动空间/引用相关工作，最后 FinishPhase 清理本轮状态。

**例子：对象 A 指向 B，mutator 与 GC 同时读 B。** 读屏障不能直接返回旧 from-space 地址；需要检查标记/转发状态并取得可用的新引用。若 A 所在 region 本轮不疏散，它可以留原位，但 A->B 的引用仍须通过屏障/扫描保持正确。这个例子解释了为什么“不是每个 region 都复制”与“应用不读失效旧地址”可以同时成立。

#### 8.2.2 CMC RunPhases：标记和压缩不是同一暂停

固定 tag 的 MarkCompact 按是否需要压缩分支处理，完整主函数节选如下：

```cpp
void MarkCompact::RunPhases() {
  Thread* self = Thread::Current();
  thread_running_gc_ = self;
  Runtime* runtime = Runtime::Current();
  GetHeap()->PreGcVerification(this);
  InitializePhase();
  ScopedPriorityChange spc(self);
  {
    ReaderMutexLock mu(self, *Locks::mutator_lock_);
    TraceFaults();
    MarkingPhase();
    // From here, until we re-enable full weak-reference access, we are potentially blocking high
    // priority threads.
    spc.SetToNormalOrBetter();
  }
  MarkingPause();
  TraceFaults();
  bool perform_compaction;
  {
    ReaderMutexLock mu(self, *Locks::mutator_lock_);
    ReclaimPhase(&spc);  // Resets priority.
    // It may be better to remain at the higher priority, and raise it only once. But given
    // that both PrepareForCompaction() and Sweep() may take some time and do not block other
    // threads, we start out with the conservative option.
    perform_compaction = PrepareForCompaction();
    if (perform_compaction) {
      spc.SetToNormalOrBetter();  // With mutator_lock_ still held.
    }
  }
  if (perform_compaction) {
    // Compaction pause
    ThreadFlipVisitor visitor(this);
    FlipCallback callback(this);
    runtime->GetThreadList()->FlipThreadRoots(
        &visitor, &callback, this, GetHeap()->GetGcPauseListener());

    {
      ReaderMutexLock mu(self, *Locks::mutator_lock_);
      spc.Reset();
      if (IsValidFd(uffd_)) {
        CompactionPhase();
      }
    }
  } else {
    if (use_generational_) {
      DCHECK_IMPLIES(post_compact_end_ != nullptr, post_compact_end_ == black_allocations_begin_);
    }
    post_compact_end_ = black_allocations_begin_;
  }
  FinishPhase(perform_compaction);
  GetHeap()->PostGcVerification(this);
  thread_running_gc_ = nullptr;
}
```

`perform_compaction` 不是恒为 true；例如 generational 或策略判定可以只完成本轮相关标记/回收，保留黑分配边界。执行压缩时先 `FlipThreadRoots` 建立根与页映射的新视图，再在允许的 userfaultfd 路径执行 CompactionPhase。不能用“开头暂停一次，结束交换空间”概括它。

CMC 与 CC 的根本区别：CC 使用读屏障配合 region evacuation；CMC 计算压缩地址和页级元数据，更新引用并协调页访问。两者都有并发阶段、根处理与回收，但数据结构、转发路径及暂停分解不同。

#### 8.2.3 CMC 的 MarkingPause：为什么必须处理新分配和弱引用

`MarkingPause()` 中的关键语句节选（行 1603–1644）：

```cpp
      runtime->GetThreadList()->ForEach(visit_stacks_callback, this);
    }
    ProcessMarkStack();
    // Fetch only the accumulated objects-allocated count as it is guaranteed to
    // be up-to-date after the TLAB revocation above.
    freed_objects_ += bump_pointer_space_->GetAccumulatedObjectsAllocated();
    // Capture 'end' of moving-space at this point. Every allocation beyond this
    // point will be considered as black.
    // Align-up to page boundary so that black allocations happen from next page
    // onwards. Also, it ensures that 'end' is aligned for card-table's
    // ClearCardRange().
    black_allocations_begin_ = bump_pointer_space_->AlignEnd(thread_running_gc_, gPageSize, heap_);
    DCHECK_ALIGNED_PARAM(black_allocations_begin_, gPageSize);

    // Re-mark root set. Doesn't include thread-roots as they are already marked
    // above.
    ReMarkRoots(runtime);
    // Scan dirty objects.
    RecursiveMarkDirtyObjects(/*paused*/ true, accounting::CardTable::kCardDirty);

    heap_->SwapStacks();
    live_stack_freeze_size_ = heap_->GetLiveStack()->Size();
  }
  // TODO: For PreSweepingGcVerification(), find correct strategy to visit/walk
  // objects in bump-pointer space when we have a mark-bitmap to indicate live
  // objects. At the same time we also need to be able to visit black allocations,
  // even though they are not marked in the bitmap. Without both of these we fail
  // pre-sweeping verification. As well as we leave windows open wherein a
  // VisitObjects/Walk on the space would either miss some objects or visit
  // unreachable ones. These windows are when we are switching from shared
  // mutator-lock to exclusive and vice-versa starting from here till compaction pause.
  // heap_->PreSweepingGcVerification(this);

  // Disallow new system weaks to prevent a race which occurs when someone adds
  // a new system weak before we sweep them. Since this new system weak may not
  // be marked, the GC may incorrectly sweep it. This also fixes a race where
  // interning may attempt to return a strong reference to a string that is
  // about to be swept.
  runtime->DisallowNewSystemWeaks();
  // Enable the reference processing slow path, needs to be done with mutators
  // paused since there is no lock in the GetReferent fast path.
  heap_->GetReferenceProcessor()->EnableSlowPath();
```

1. 暂停期间收回线程本地 allocation stack/TLAB，防止线程继续往即将交换为 live stack 的结构写入。
2. 将 moving space 当前末端按页对齐，记录 `black_allocations_begin_`；之后的新分配按本轮黑分配规则处理，不因没有出现在旧 bitmap 就被误回收。
3. 再标记根和 dirty cards，补齐并发标记期间新建/改写的引用，再交换 allocation/live stacks。
4. 暂时限制新的 system weak 以及引用 fast path，避免弱表在清扫边界返回即将死亡的对象。这不是“WeakReference 一律立即变 null”，引用处理有协议与时序。

这个边界也说明暂停不能简单定义成“仅扫描线程栈”：它还同步分配边界、cards、系统弱引用以及后续压缩所需的不变量。

### 8.3 HSC (Homogeneous Space Compact) - 后台压缩

HSC 面向相同类型的 malloc spaces（main/backup）的压缩和交换，见 `Heap::PerformHomogeneousSpaceCompact()`。`Heap` 在 CC/CMC 前台收集器下关闭用于 OOM 的 homogeneous-space compaction。它不是“CC 遇到存活对象过多时的补救算法”。

```text
进程状态变化 / 允许的 OOM 压缩路径
  -> 检查 moving GC 是否允许、main/backup space 是否可用
  -> 在适用配置下将存活对象转移并更新引用
  -> 交换空间、恢复分配、记录压缩结果
```

后台表示调度时机，不保证“不影响前台”或“永不暂停”。是否触发还受收集器类型、后台转换策略和压缩条件控制。

---

#### 8.3.1 HSC 的拒绝条件和真正的 STW

`PerformHomogeneousSpaceCompact()` 要串行化 GC 并检查 moving GC 条件。下面是返回分支与空间切换的节选，不是“后台执行所以完全不暂停”：

```cpp
HomogeneousSpaceCompactResult Heap::PerformHomogeneousSpaceCompact() {
  Thread* self = Thread::Current();
  // Inc requested homogeneous space compaction.
  count_requested_homogeneous_space_compaction_++;
  // Store performed homogeneous space compaction at a new request arrival.
  ScopedThreadStateChange tsc(self, ThreadState::kWaitingPerformingGc);
  Locks::mutator_lock_->AssertNotHeld(self);
  {
    ScopedThreadStateChange tsc2(self, ThreadState::kWaitingForGcToComplete);
    MutexLock mu(self, *gc_complete_lock_);
    // Ensure there is only one GC at a time.
    WaitForGcToCompleteLocked(kGcCauseHomogeneousSpaceCompact, self);
    // Homogeneous space compaction is a copying transition, can't run it if the moving GC disable
    // count is non zero.
    // If the collector type changed to something which doesn't benefit from homogeneous space
    // compaction, exit.
    if (disable_moving_gc_count_ != 0 || IsMovingGc(collector_type_) ||
        !main_space_->CanMoveObjects()) {
      return kErrorReject;
    }
    if (!SupportHomogeneousSpaceCompactAndCollectorTransitions()) {
      return kErrorUnsupported;
    }
    collector_type_running_ = kCollectorTypeHomogeneousSpaceCompact;
  }
  if (Runtime::Current()->IsShuttingDown(self)) {
    // Don't allow heap transitions to happen if the runtime is shutting down since these can
    // cause objects to get finalized.
    FinishGC(self, collector::kGcTypeNone);
    return HomogeneousSpaceCompactResult::kErrorVMShuttingDown;
  }
  collector::GarbageCollector* collector;
  {
    ScopedSuspendAll ssa(__FUNCTION__);
    uint64_t start_time = NanoTime();
    // Launch compaction.
    space::MallocSpace* to_space = main_space_backup_.release();
    space::MallocSpace* from_space = main_space_;
    to_space->GetMemMap()->Protect(PROT_READ | PROT_WRITE);
    const uint64_t space_size_before_compaction = from_space->Size();
    AddSpace(to_space);
    // Make sure that we will have enough room to copy.
    CHECK_GE(to_space->GetFootprintLimit(), from_space->GetFootprintLimit());
    collector = Compact(to_space, from_space, kGcCauseHomogeneousSpaceCompact);
    const uint64_t space_size_after_compaction = to_space->Size();
    main_space_ = to_space;
    main_space_backup_.reset(from_space);
    RemoveSpace(from_space);
    SetSpaceAsDefault(main_space_);  // Set as default to reset the proper dlmalloc space.
    // Update performed homogeneous space compaction count.
    count_performed_homogeneous_space_compaction_++;
```

`kErrorReject`、`kErrorUnsupported`、`kErrorVMShuttingDown` 有不同含义：分别是本轮不允许移动/当前收集器不适合，或运行时不支持，或已进入关闭阶段。空间切换在 ScopedSuspendAll 保护下，调用者不能忽略结果后宣称压缩一定成功。


### 8.4 GC 触发策略

```text
分配快路径失败
  -> 分配慢路径 / 等待或请求 GC
  -> 重试分配、按策略增长堆或清理软引用
  -> 仍不能满足才 OOM

分配量达到动态 concurrent_start_bytes_ 水位
  -> RequestConcurrentGC()
  -> 提前并发回收，为后续分配留余量

native 分配压力 / 显式请求 / 进程前后台转换
  -> 对应 GcCause 与策略处理，不是统一 final GC
```

`GrowForUtilization()` 根据本轮存活量、target utilization、min/max free、增长上限及分配速率等调整目标堆和并发触发水位。不能写成固定“75% 使用率触发”。Zygote space 共享/COW 策略也不是一个叫“HSpace 压力”的 Dalvik 触发枚举。

---

#### 8.4.1 分配失败不立刻等于 OOM

`Heap::AllocateInternalWithGc()` 的慢路径会等待在途 GC、根据允许的 collector/allocator 重试，必要时增长堆并尝试更充分回收。它需要在发生 GC 的位置保护传入类等对象引用，因为 moving GC 可能改变其地址。

```text
一次申请失败
  -> 检查/等待当前 GC（不能持有会阻止其完成的锁）
  -> 重新尝试同一分配
  -> 按 gc_plan 和堆增长/软引用策略继续尝试
  -> 若 allocator 在转换中发生变化，按新条件重试
  -> 所有有效恢复路径失败后 ThrowOutOfMemoryError
```

| 失败类型 | 为什么 GC 不一定解决 | 分析材料 |
|----------|----------------------|----------|
| 活对象占用接近 growth limit | 强引用仍在，回收不了业务存活对象 | heap dump、持有链、每轮回收后存活量 |
| 连续空间/特定 allocator 不足 | 总空闲大于请求也可能无法满足该类分配 | allocator、LOS/非移动空间、碎片信息 |
| native 压力 | Java 存活图不能代表全部进程内存 | native allocation、RSS/PSS、位图等 native 资源 |
| 暂时性分配峰值 | GC 来不及在突发前提供足够余量 | 分配速率、concurrent-start 水位、任务并行度 |

不能只看 free 百分比判断“系统明明还有内存为什么 OOM”；进程堆上限、地址空间、分配器资格和 native 内存分别约束请求。

---

## 9. GC 日志解读

### 9.1 ART GC 日志格式详解

`Heap::CollectGarbageInternal()` 的日志把 cause、collector name、普通/LOS 回收量、空闲百分比、已分配量/目标量、暂停列表及总周期拼接在一起。示例数字仅用于解释格式：

```text
Background concurrent copying GC freed 10000(1024KB) AllocSpace objects,
4(512KB) LOS objects, 25% free, 12MB/16MB, paused 1ms total 20ms
```

- `freed` 后是本次回收的对象数与字节数，不是“分配器数量”，也不是回收后剩余占用。
- `25% free` 是空闲比例，不是使用率；`12MB/16MB` 是已分配量/当前目标堆量，不是“16MB 缩到 12MB”的前后对比。
- `paused` 是 mutator 暂停记录；`total` 是整个 GC 耗时（包括并发阶段）。总时长 20ms 不意味着主线程暂停 20ms。

### 9.2 实战：通过 GC 日志定位问题

**频繁 GC：** 联合观察单位时间次数、分配速率、`freed` 与回收后的已分配量。空闲比例高但频繁回收可能是临时对象 churn，不是单凭一个百分比就能判定泄漏。

**LOS 回收量大：** `freed ... LOS objects` 表示本次释放量大，不能反推当前 LOS 占用仍大。结合 heap dump 和分配栈检查 primitive arrays；现代 Bitmap 像素常位于 native 内存，不能都归入 Java LOS。

**暂停过长：** 对照 paused 列表、线程暂停等待与 Perfetto 调度切片，区分等待线程到达安全点和 GC 实际工作。减少不必要的存活引用和分配，使用 heap dump 定位持有链；不要靠无条件 System.gc() 或任意弱引用替换业务所有权来“治疗”暂停。

---

### 9.3 logcat GC 相关命令

```bash
# 查看 GC 日志
adb logcat | grep -E "GC|clamp"

# 查看特定进程的 GC
adb logcat --pid=12345 | grep "GC"  # PID 由本次进程确定

# 查看完整的 GC 追踪
adb logcat -v threadtime *:V | grep "GC"

# GC 日志输出受 ART 阈值/运行配置控制；log.tag.GC 不是统一开关

# 查看内存信息
adb shell dumpsys meminfo <package_name>

# 查看可达性工具输出（不是完整 Java heap dump）
adb shell dumpsys meminfo --unreachable <package_name>

# 查看 OOM 信息
adb logcat | grep -E "OOM|FATAL|OutOfMemory"

# 分析 Hprof 文件
# 使用 Android Studio Memory Profiler 或 MAT 打开 HPROF（jhat 已非现代 JDK 工具）
```

---

## 10. JIT 编译与 Profile-Guided Compilation

### 10.1 ART JIT 编译器详解

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ART JIT 编译器架构                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         JIT Compiler                                 │  │
│  │                                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │  │
│  │  │    IR      │  │   Machine   │  │  Optimizer  │                 │  │
│  │  │  (中间表示) │  │  Code Gen   │  │  (优化器)   │                 │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                 │  │
│  │                                                                       │  │
│  │  输入: DEX 字节码                                                      │  │
│  │  输出: 本地机器码                                                      │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘

JIT 编译流程：
1. 解释执行 - DEX 字节码先被解释执行
2. 热点检测 - 统计方法/循环执行次数
3. 编译排队 - 热点方法加入编译队列
4. 后台编译 - 在后台线程编译
5. 代码替换 - 编译完成后替换为机器码
```

### 10.2 Profile-Guided Compilation (PGC)

```text
构建/分发时 Baseline Profile 或云端 profile（若提供）
  -> 安装阶段可以基于 profile AOT，而非一律不编译
运行时解释/JIT
  -> ProfileSaver 收集类/方法使用信息
后台 dexopt
  -> 合并/选择 profile -> dex2oat 按过滤器编译
后续进程启动
  -> 加载可用产物；未覆盖的新热点仍可 JIT
```

Baseline Profile 通常来自应用构建/分发，并非安装器从零生成。运行时 profile 的典型系统路径是 `/data/misc/profiles/cur/<userId>/<package>/primary.prof` 与 `/data/misc/profiles/ref/<package>/primary.prof`（split 有各自 profile），不是应用私有 `files/profiles`。profile 是二进制格式；人类可读规则需经工具转换，不能把 `classes`/`methods` 文本列表当文件布局。

### 10.3 编译层级

ART 没有通用“Level 0–3 = 解释、Quick JIT、Regular JIT、AOT”的 API/状态枚举。固定 tag 的 JIT 使用 `CompilationKind` 区分 baseline、optimized、OSR 任务；解释器只是尚未使用机器码的执行方式，AOT 是另一个编译时机，不是必须从 JIT 晋级才能达到的 Level 3。

热点采样、优先级与阈值受 JitOptions、profile、设备配置和启动阶段影响，不能写死“1000 次升级”。OSR 用于在运行中的热点循环切入已编译代码，不是等待方法下一次调用才生效。

### 10.4 Deoptimization（逆优化）

逆优化把编译帧的执行状态重建为解释器可继续的状态。常见原因是调试/插桩需要解释执行、编译优化依赖的假设失效等；ART 根据 stack map/deoptimization metadata 恢复局部变量、寄存器和解释帧，再继续执行。

它不是自动修复编译器 bug 的通用机制，也不意味着替换磁盘 DEX 就能改写已经加载的类。JVMTI 类重定义有专门的限制和流程；普通应用的 ClassLoader 热加载不能直接等同于重定义。旧文中的 `kTrap/kThrow/kReturn` 不是本 tag 的统一逆优化类型枚举。

---

## 11. ART 对象模型与内存布局

### 11.1 ART 对象内存布局

固定 tag 的 `mirror::Object` 中核心头字段是：

```text
HeapReference<Class> klass_   4 字节压缩堆引用
uint32_t monitor_            4 字节 LockWord
实例字段与必要对齐填充
```

普通对象按 `kObjectAlignment`（8 字节）对齐，不是 64 位进程就把所有 Java 堆引用变为 8 字节。identity hash 不是额外固定 4 字节头字段：它可能编码在 LockWord 的 hash 状态中；锁膨胀后相关状态由 Monitor 保存。

数组在 Object 头后增加 `int32_t length_`，元素区按元素类型对齐，`Object[]` 使用压缩堆引用。`mirror::Class` 本身也是 Java 堆对象，包含 class loader、dex cache、字段/方法数组、vtable/iftable 等元数据；不能把普通 C++ `Class* this_class` 结构图当作其真实内存布局。

---

### 11.2 ClassLinker 类加载

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ClassLinker 类加载                                  │
└─────────────────────────────────────────────────────────────────────────────┘

ClassLinker 负责 ART 中的类加载和链接。

加载流程：
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. FindClass (查找类)                                                      │
│     • 通过 ClassLoader 查找类                                               │
│     • 检查是否已加载                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. DefineClass (定义类)                                                    │
│     • 解析 DEX 文件中的类数据                                                │
│     • 分配 Class 对象                                                       │
│     • 解析字段、方法、接口                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Linking (链接)                                                         │
│     • 验证: 字节码验证、类型检查                                             │
│     • 准备: 分配静态字段内存，初始化为默认值                                 │
│     • 解析: 将符号引用解析为直接引用                                         │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Initialization (按需初始化，不是每次 loadClass 都执行)                                                │
│     • 执行 <clinit> 静态初始化器                                            │
│     • 初始化静态字段为指定值                                                │
└─────────────────────────────────────────────────────────────────────────────┘

Class 状态机：
┌─────────────────────────────────────────────────────────────────────────────┐
│  NotReady → Loaded → Resolving → Resolved → Verifying → Verified → Initializing → Initialized（主线示意）                        │
│                                                                             │
│  • NotReady: 初始状态                                                      │
│  • Resolving: 正在链接/解析                                                        │
│  • Loaded: 加载完成                                                        │
│  • Resolved / Verified: 已解析 / 已验证；还有错误、重试等分支                                               │
│  • Initialized: 已初始化                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.3 ART Method 模型

`ArtMethod` 的字段而非旧版 Portable 编译器结构：

```cpp
// art/runtime/art_method.h 字段摘要（非完整声明）
GcRoot<mirror::Class> declaring_class_;
std::atomic<uint32_t> access_flags_;
uint32_t dex_method_index_;
uint16_t method_index_;
// union 中包含 uint16_t hotness_count_ 等复用状态
struct PtrSizedFields {
    void* data_;
    void* entry_point_from_quick_compiled_code_;
};
```

热点计数是 16 位字段，不是 ArtMethod 指针。指针大小字段按运行时 pointer size 布局；`data_` 随方法类别用于 JNI/运行时相关数据，不是直接内嵌异常表和行号表。调用解析后由 entry point 进入已有代码或运行时桥，解释/JIT/AOT 共享方法元数据；不能以伪造 `method->IsCompiled()` 分支替代真实入口和解析/解释桥。

---

## 12. ART 线程模型

### 12.1 ART 线程结构 (ArtThread)

当前 C++ 类名是 `art::Thread`，不是 `ArtThread`。其 TLS 分区保存状态/标志、栈边界、JNIEnvExt、managed peer、异常、suspend/checkpoint 等信息；不要用不存在的 `current_abi`/`ThrowingThrowable` 伪字段冒充声明。

Java 启动链：`Thread.start()` -> native `Thread_nativeCreate()` -> `Thread::CreateNativeThread()`。ART 先准备 native Thread 及 Java peer 引用，再通过 pthread 创建 OS 线程；线程入口完成 Init/注册、设置优先级，最后调用 Java peer 的 `run()`。JNI AttachCurrentThread 则把一个既存 native 线程接入 ART，是另一条路径。

### 12.2 线程状态转换

Java `Thread.State` 与 `art::ThreadState`、Linux 调度状态是三套模型。ART `kRunnable` 表示正在访问 managed heap（持有 mutator lock 的共享语义），不能只解释成“在运行队列等 CPU”。JNI native 执行通常是 `kNative`；进入 monitor、wait/sleep、GC 等有各自状态。

```text
managed 执行 kRunnable
  -> monitor 竞争 kBlocked -> 获锁后恢复
  -> Object.wait kWaiting / kTimedWaiting -> 重新取得 monitor
  -> Thread.sleep kSleeping -> 超时/中断
  -> JNI kNative -> 回 managed 时检查 suspend/checkpoint
```

`suspend_count`、挂起标志与安全点协调暂停；Linux 线程没有被调度不代表 ART 状态必然为 kSuspended。

---

### 12.3 synchronized 在 ART 中的实现

`LockWord` 区分 unlocked、thin-locked、fat-locked、hash/forwarding 等状态；ART 没有旧 HotSpot 的 biased-lock 升级链。

```text
MonitorEnter(obj)
  unlocked -> CAS 写入 thin owner / recursion count
  thin 且当前线程持有 -> 增加递归计数
  thin 且他线程持有 -> 重试/等待策略，必要时 Inflate
  hash / 递归溢出 / wait 等需要 Monitor 的情况 -> Inflate
  fat -> Monitor::Lock，竞争时在 mutex/condition 路径等待
MonitorExit(obj)
  thin -> 减递归计数，最后一次释放为 unlocked
  fat -> Monitor::Unlock，释放拥有者并通知等待者
```

第一次 CAS 失败不一定立即膨胀；fat lock 解锁也不会每次把对象头重置成 thin/unlocked，空闲 Monitor 的 deflation 是单独受安全条件约束的动作。`Object.wait()` 释放当前对象 monitor 后等待，返回前重新获取；其他已持有锁不会一并释放。

---

## 13. 总结

| 主题 | 正确的实现边界 |
|------|----------------|
| Dalvik / ART | 寄存器是 DEX 抽象，不等于物理寄存器；ART 5–6 主要 AOT，7+ 恢复 JIT 混合策略 |
| DEX / OAT / VDEX / image | 输入字节码、编译代码与元数据、验证依赖、预初始化对象分别管理 |
| GC | 当前实现同时含 CC、CMC 和兼容路径；cause 不等于算法，更不等于暂停时长 |
| 对象头 | 压缩 klass 引用 + 32 位 LockWord；hash 不是独立固定头字段 |
| 锁 | thin/fat、递归计数、膨胀/deflation；没有 ART biased lock |
| 编译 | baseline/optimized/OSR JIT 与 profile-guided AOT，不存在通用 Level 0–3 |
| 类加载 | defining loader 决定类身份，加载、验证、初始化不是同一个事件 |
| 线程 | art::Thread、Java Thread.State 和 Linux 线程调度状态需要分开分析 |

面试和性能排查应先锁定设备 ART 配置，再画调用链：GC 先看 cause/collector/paused/total，内存看存活图与 Java/native 分配，JIT 看 profile 覆盖和入口切换。减少无用分配与错误持有关系优先于无条件对象池、Bitmap.recycle() 或 System.gc()；这些操作都有生命周期与性能代价。

主要目录：`art/runtime/gc/collector/`（concurrent_copying、mark_compact、mark_sweep）、`gc/heap.cc`、`mirror/object.h`、`monitor.cc`、`jit/`、`class_linker.cc`、`thread.cc` 和 `art/dex2oat/`。

---

*文档更新时间: 2026-09-10*
*本文档由 OpenClaw 生成*


## 固定版本源码索引

本文平台实现基线为 `android-17.0.0_r1`。下列函数用于定位正文分析；代码标为“节选”时省略无关监控，标为“示意”时不是源码逐字复制。

- [Heap](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/gc/heap.cc)：`Heap; CollectGarbageInternal; GrowForUtilization; PerformHomogeneousSpaceCompact`。
- [CC](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/gc/collector/concurrent_copying.cc)：`RunPhases; FlipThreadRoots; CopyingPhase`。
- [CMC](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/gc/collector/mark_compact.cc)：`RunPhases; ConcurrentCompaction`。
- [GC cause](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/gc/gc_cause.h)：`GcCause`。
- [对象](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/mirror/object.h)：`Object.klass_; Object.monitor_`。
- [锁](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/monitor.cc)：`MonitorEnter; MonitorExit; Inflate; Deflate`。
- [方法](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/art_method.h)：`ArtMethod; PtrSizedFields`。
- [线程](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/thread.cc)：`CreateNativeThread`。
- [JIT](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/jit/jit.cc)：`CompileMethod; AddSamples`。
- [DEX](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/libdexfile/dex/dex_file.h)：`Header; HeaderV41`。

- [Runtime 生命周期](https://android.googlesource.com/platform/art/+/refs/tags/android-17.0.0_r1/runtime/runtime.cc)：`Runtime::Init; Start; PreZygoteFork; PostZygoteFork`。
