# Android Binder 机制深度解析

> 作者：OpenClaw | 日期：2026-03-08

---

## 目录

- [1. 概述](#1-概述)
- [2. 为什么选择 Binder](#2-为什么选择-binder)
- [3. Binder 整体架构](#3-binder-整体架构)
- [4. Binder 全局流程图](#4-binder-全局流程图)
- [5. Binder 驱动层](#5-binder-驱动层)
  - [5.1 核心数据结构](#51-核心数据结构)
  - [5.2 内存映射 (mmap)](#52-内存映射-mmap)
  - [5.3 ioctl 命令](#53-ioctl-命令)
- [6. Native 层](#6-native-层)
  - [6.1 ProcessState](#61-processstate)
  - [6.2 IPCThreadState](#62-ipcthreadstate)
  - [6.3 BpBinder 与 BBinder](#63-bpbinder-与-bbinder)
- [7. Framework 层](#7-framework-层)
  - [7.1 Binder.java](#71-binderjava)
  - [7.2 BinderProxy.java](#72-binderproxyjava)
- [8. AIDL 详解](#8-aidl-详解)
  - [8.1 AIDL 语法](#81-aidl-语法)
  - [8.2 AIDL 生成的代码结构](#82-aidl-生成的代码结构)
  - [8.3 AIDL 完整示例](#83-aidl-完整示例)
- [9. Binder 线程池](#9-binder-线程池)
- [10. 跨进程通信方式对比](#10-跨进程通信方式对比)
  - [10.1 Bundle + Intent](#101-bundle--intent)
  - [10.2 共享内存 (MemoryFile)](#102-共享内存-memoryfile)
  - [10.3 管道 (Pipe)](#103-管道-pipe)
  - [10.4 信号 (Signal)](#104-信号-signal)
  - [10.5 消息队列](#105-消息队列)
  - [10.6 信号量 (Semaphore)](#106-信号量-semaphore)
  - [10.7 各种 IPC 方式完整对比表](#107-各种-ipc-方式完整对比表)
- [11. 常见问题](#11-常见问题)
  - [11.1 TransactionTooLargeException](#111-transactiontoolargeexception)
  - [11.2 Binder 线程耗尽](#112-binder-线程耗尽)
  - [11.3 Binder 死亡通知](#113-binder-死亡通知)
- [12. ServiceManager](#12-servicemanager)
- [13. Messenger](#13-messenger)
- [14. ContentProvider](#14-contentprovider)
- [15. 文件共享](#15-文件共享)
- [16. Socket IPC](#16-socket-ipc)
- [17. Binder 调试技巧](#17-binder-调试技巧)
- [18. 总结](#18-总结)
- [19. Binder 事务生命周期](#19-binder-事务生命周期)
  - [19.1 同步事务 vs 异步事务 (oneway)](#191-同步事务-vs-异步事务-oneway)
- [20. Binder 死锁问题](#20-binder-死锁问题)
- [21. Binder 对象传递](#21-binder-对象传递)
  - [21.1 文件描述符传递](#211-文件描述符传递)
- [22. Binder 调用链追踪](#22-binder-调用链追踪)
- [23. Binder 高频面试题](#23-binder-高频面试题)
- [24. Binder 架构图总结](#24-binder-架构图总结)
- [固定版本源码索引](#固定版本源码索引)

---

## 1. 概述

本文的 Java/JNI/libbinder 以 `android-17.0.0_r1` 为固定基线，讨论 **kernel Binder** 主路径，socket Binder RPC 是不同传输分支。驱动不是 platform tag 唯一确定的内核：第 5 章另固定 common kernel commit `d768b2f486b5e909eb5e489b83059400c3cb2799`，不把其文件标成 Android 17 的唯一设备驱动。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 是什么？                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  Binder 是 Android 系统中最重要的 IPC（Inter-Process Communication）机制：

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │     进程 A (App)                          进程 B (Service)               │
  │    ┌──────────────┐                      ┌──────────────┐               │
  │    │              │                      │              │               │
  │    │   调用方法   │  ════════════════════►│   执行方法   │               │
  │    │   getData()  │      Binder IPC      │   getData()  │               │
  │    │              │  ◄═══════════════════│   返回结果   │               │
  │    │              │                      │              │               │
  │    └──────────────┘                      └──────────────┘               │
  │                                                                         │
  │    用户空间                               用户空间                       │
  │    ──────────────────────────────────────────────────────────────────── │
  │    内核空间                               内核空间                       │
  │    ┌──────────────────────────────────────────────────────────────────┐ │
  │    │                      Binder 驱动                                  │ │
  │    │              (/dev/binder - 内核模块)                             │ │
  │    └──────────────────────────────────────────────────────────────────┘ │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  Binder 的核心特点：
  ─────────────────────────────────────────────────────────────────────────────
  1. 基于 C/S 架构（Client - Server）
  2. 只需要一次内存拷贝（mmap）
  3. 内核级 UID/PID 身份验证
  4. 支持同步调用和异步调用
  5. 支持跨进程传递文件描述符
```

---

## 2. 为什么选择 Binder

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    为什么 Android 选择 Binder 作为主要 IPC？                 │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │                         对比维度                                         │
  │  ┌─────────────┬─────────────────┬─────────────────────────────────────┐ │
  │  │   维度       │     Binder      │        传统 IPC                     │ │
  │  ├─────────────┼─────────────────┼─────────────────────────────────────┤ │
  │  │ 拷贝次数     │     1 次        │  Socket: 2次 / 共享内存: 0次        │ │
  │  ├─────────────┼─────────────────┼─────────────────────────────────────┤ │
  │  │ 安全性       │  内核级 UID/PID │  依赖上层协议，易被篡改             │ │
  │  ├─────────────┼─────────────────┼─────────────────────────────────────┤ │
  │  │ 易用性       │  AIDL 封装      │  需手动序列化与协议处理             │ │
  │  ├─────────────┼─────────────────┼─────────────────────────────────────┤ │
  │  │ 系统适配     │  深度整合组件   │  无法直接支持组件生命周期           │ │
  │  └─────────────┴─────────────────┴─────────────────────────────────────┘ │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  性能对比：内存拷贝次数
  ─────────────────────────────────────────────────────────────────────────────

  传统 IPC (如 Socket)：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  发送进程                    内核空间                    接收进程        │
  │  ┌─────────┐                ┌─────────┐                ┌─────────┐      │
  │  │ 用户缓冲 │ ──拷贝1──►    │ 内核缓冲 │ ──拷贝2──►    │ 用户缓冲 │      │
  │  │   区    │                │   区    │                │   区    │      │
  │  └─────────┘                └─────────┘                └─────────┘      │
  │                                                                         │
  │  ★ 需要两次拷贝，性能开销大                                              │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  Binder IPC：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  发送进程                    内核空间                    接收进程        │
  │  ┌─────────┐                ┌─────────────────────┐    ┌─────────┐      │
  │  │ 用户缓冲 │ ──拷贝──►     │  内核缓冲区          │    │         │      │
  │  │   区    │               │         ▲            │    │         │      │
  │  └─────────┘               │         │ mmap       │    │         │      │
  │                            │         ▼            │    │         │      │
  │                            │  用户空间映射区 ◄────┼────┤ 直接读取│      │
  │                            └─────────────────────┘    └─────────┘      │
  │                                                                         │
  │  ★ 只需要一次拷贝，接收方通过 mmap 直接读取                              │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  安全性对比：
  ─────────────────────────────────────────────────────────────────────────────

  传统 Linux IPC：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  普通数据包自填身份不可信；Unix domain socket 可通过内核 credentials 取得对端身份                                      │
  │  例如 SO_PEERCRED/SCM_CREDENTIALS；不是只有 Binder 支持可靠身份                                      │
  │  ────────────────────────────────────────                               │
  │  问题：只信任数据包里的自报身份会被伪造；应使用内核身份并做授权！                                                │
  │                                                                         │
  │  // 恶意进程可以伪造 UID                                                │
  │  data.uid = 1000;  // 伪造为 system_server                              │
  │  data.pid = 1234;                                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  Binder IPC：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  Binder 在内核中自动添加进程身份标记                                     │
  │  由 IPC 机制本身在内核中添加，不由应用程序控制                            │
  │                                                                         │
  │  // Binder 驱动自动添加（内核层）                                        │
  │  static void binder_transaction(...) {                                  │
  │      // ★ 由内核填充，无法伪造 ★                                        │
  │      t->sender_euid = task_euid(proc->tsk); // 示意：驱动记录凭据                            │
  │      // 接收描述符 tr.sender_pid 由发送线程与目标 PID namespace 计算；oneway 可为 0                       │
  │  }                                                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  UID 与 PID 详解：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  PID (Process ID) - 进程标识符                                          │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  定义：操作系统分配给每个进程的唯一数字标识                               │
  │  作用：标识一个正在运行的进程                                            │
  │  特点：                                                                 │
  │  - 每个进程有唯一的 PID                                                  │
  │  - 进程结束后 PID 可以被回收重用                                         │
  │  - 可以通过 getpid() 获取                                               │
  │  - 用于进程管理（kill、wait 等）                                         │
  │                                                                         │
  │  示例：                                                                 │
  │  PID 1234 → com.example.app (主进程)                                    │
  │  PID 1235 → com.example.app:remote (子进程)                             │
  │  PID 567 → system_server                                                │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  UID (User ID) - 用户标识符                                             │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  定义：Linux 中用于标识用户身份的数字                                    │
  │  作用：权限控制和资源访问                                                │
  │                                                                         │
  │  在 Android 中的特殊用法：                                              │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  - 每个 App 安装时分配唯一的 UID（基于包名）                             │
  │  - 同一 UID 的进程共享数据和权限                                         │
  │  - system_server 的 UID 是 1000 (Process.SYSTEM_UID)                   │
  │  - root 的 UID 是 0                                                     │
  │  - 普通 App 的 UID 从 10000 开始                                        │
  │                                                                         │
  │  UID 类型：                                                             │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  - real UID (ruid)：进程启动者的 UID                                    │
  │  - effective UID (euid)：进程实际运行时的权限 UID                       │
  │  - saved UID (suid)：保存的 UID，用于权限切换                           │
  │                                                                         │
  │  示例：                                                                 │
  │  UID 10060 → com.example.app                                            │
  │  UID 1000 → system (系统服务)                                           │
  │  UID 0 → root (超级用户)                                                │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  PID vs UID 对比                                                        │
  │  ─────────────────────────────────────────────────────────────────────  │
  │                                                                         │
  │  ┌─────────────┬─────────────────────┬─────────────────────────────┐   │
  │  │    对比项    │        PID          │           UID               │   │
  │  ├─────────────┼─────────────────────┼─────────────────────────────┤   │
  │  │  标识对象    │  进程               │  用户/应用                   │   │
  │  ├─────────────┼─────────────────────┼─────────────────────────────┤   │
  │  │  唯一性      │  系统内唯一          │  应用安装时分配              │   │
  │  ├─────────────┼─────────────────────┼─────────────────────────────┤   │
  │  │  生命周期    │  进程运行期间        │  应用安装后固定              │   │
  │  ├─────────────┼─────────────────────┼─────────────────────────────┤   │
  │  │  主要用途    │  进程管理            │  权限控制                    │   │
  │  ├─────────────┼─────────────────────┼─────────────────────────────┤   │
  │  │  可变性      │  进程重启后改变      │  一般不变                    │   │
  │  ├─────────────┼─────────────────────┼─────────────────────────────┤   │
  │  │  共享性      │  不共享              │  同一 App 多进程共享         │   │
  │  └─────────────┴─────────────────────┴─────────────────────────────┘   │
  │                                                                         │
  │  举例说明：                                                             │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  App: com.example.app                                                  │
  │  ├── 主进程    PID: 1234, UID: 10060                                   │
  │  ├── 子进程    PID: 1235, UID: 10060  ← 同一 App，UID 相同              │
  │  └── 子进程    PID: 1236, UID: 10060  ← 同一 App，UID 相同              │
  │                                                                         │
  │  App: com.other.app                                                    │
  │  └── 主进程    PID: 5678, UID: 10061  ← 不同 App，UID 不同              │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  Binder 中如何使用 UID/PID：
  ─────────────────────────────────────────────────────────────────────────────

  // 1. Binder 驱动自动填充（内核层，无法伪造）
  // kernel/drivers/android/binder.c
  static void binder_transaction(...) {
      t->sender_euid = task_euid(proc->tsk); // 示意：驱动记录凭据    // 发送方的 effective UID
      // 接收描述符 tr.sender_pid 由发送线程与目标 PID namespace 计算；oneway 可为 0 // 发送方的 PID
  }

  // 2. 服务端获取调用方身份（Java 层）
  public class MyService extends Service {
      @Override
      public IBinder onBind(Intent intent) {
          return new IMyService.Stub() {
              @Override
              public void secureMethod() {
                  // 获取调用方的 UID
                  int callingUid = Binder.getCallingUid();

                  // 获取调用方的 PID
                  int callingPid = Binder.getCallingPid();

                  // 权限检查
                  if (callingUid != Process.SYSTEM_UID) {
                      throw new SecurityException("Only system can call this");
                  }

                  // 或者检查包名
                  String[] packages = getPackageManager()
                      .getPackagesForUid(callingUid);
              }
          };
      }
  }

  // 3. 常用 API
  // 获取调用方 UID
  int callingUid = Binder.getCallingUid();

  // 获取调用方 PID
  int callingPid = Binder.getCallingPid();

  // 清除调用方身份（临时恢复本进程的 Binder 调用身份，不修改 Linux UID）
  long token = Binder.clearCallingIdentity();
  try {
      // 以本进程身份执行操作
  } finally {
      Binder.restoreCallingIdentity(token);
  }

  // 4. 常见 UID 常量
  // Process.ROOT_UID = 0           // root 用户
  // Process.SYSTEM_UID = 1000      // system_server
  // Process.PHONE_UID = 1001       // 电话服务
  // Process.FIRST_APPLICATION_UID = 10000  // 第一个 App UID
```

---

## 3. Binder 整体架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 整体架构图                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                          应用层 (Application)                            │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │   Activity              Service              ContentProvider      │  │
  │  │       │                    │                        │              │  │
  │  │       └────────────────────┼────────────────────────┘              │  │
  │  │                            │                                       │  │
  │  │                            ▼                                       │  │
  │  │                    ┌───────────────┐                               │  │
  │  │                    │    AIDL 接口   │                               │  │
  │  │                    │  (Stub/Proxy) │                               │  │
  │  │                    └───────────────┘                               │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       Framework 层 (Java)                                │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
  │  │  │  IBinder     │  │  Binder      │  │ BinderProxy  │            │  │
  │  │  │  (接口)      │  │  (服务端)    │  │  (客户端)    │            │  │
  │  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
  │  │         │                  │                  │                   │  │
  │  │         └──────────────────┼──────────────────┘                   │  │
  │  │                            │                                       │  │
  │  │                            ▼                                       │  │
  │  │                   ┌─────────────────┐                              │  │
  │  │                   │  Parcel (序列化) │                              │  │
  │  │                   └─────────────────┘                              │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (JNI)
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       Native 层 (C++)                                    │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
  │  │  │  BBinder     │  │  BpBinder    │  │ IPCThreadState│            │  │
  │  │  │  (服务端)    │  │  (客户端)    │  │  (线程状态)   │            │  │
  │  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
  │  │         │                  │                  │                   │  │
  │  │         └──────────────────┼──────────────────┘                   │  │
  │  │                            │                                       │  │
  │  │                            ▼                                       │  │
  │  │                   ┌─────────────────┐                              │  │
  │  │                   │  ProcessState   │                              │  │
  │  │                   │  (进程状态)     │                              │  │
  │  │                   └─────────────────┘                              │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (ioctl)
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       内核层 (Kernel)                                     │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │                    ┌─────────────────────┐                        │  │
  │  │                    │    Binder 驱动      │                        │  │
  │  │                    │   /dev/binder      │                        │  │
  │  │                    │                    │                        │  │
  │  │                    │  - binder_proc     │  (进程上下文)           │  │
  │  │                    │  - binder_thread   │  (线程上下文)           │  │
  │  │                    │  - binder_node     │  (Binder 实体)          │  │
  │  │                    │  - binder_ref      │  (Binder 引用)          │  │
  │  │                    │  - binder_buffer   │  (内存缓冲区)           │  │
  │  │                    │                    │                        │  │
  │  │                    └─────────────────────┘                        │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Binder 全局流程图

这条主链以远程 Java AIDL 同步请求为例，transport 为 kernel Binder。每层负责不同的资源，不能把接口对象、native Parcel 和 payload 指针混用。

```text
Client Java
  IMyService.Stub.Proxy.getData(id)
    Parcel.obtain(remote) / Parcel.obtain()
    writeInterfaceToken(DESCRIPTOR) -> writeInt(id)
    mRemote.transact(code, data, reply, 0)
      BinderProxy.transact
        检查/trace/WorkSource/监听
        transactNative(code, jobject data, jobject reply, flags)
Client JNI
  android_os_BinderProxy_transact
    parcelForJavaObject(dataObj/replyObj) -> native Parcel*
    getBPNativeData(obj)->mObject -> IBinder*
    target->transact(code, *data, reply, flags)
Client libbinder
  BpBinder::transact -> 检查活性/稳定性/transport
    IPCThreadState::transact(handle, code, data, reply, flags)
      writeTransactionData(BC_TRANSACTION, ...)
        mOut: 命令 + binder_transaction_data
      waitForResponse(reply)
        talkWithDriver() -> ioctl(BINDER_WRITE_READ)
Driver
  binder_ioctl -> binder_ioctl_write_read -> binder_thread_write
    BC_TRANSACTION -> binder_transaction
      handle -> ref -> node -> 目标 proc
      选择目标线程/进程，分配接收 buffer
      复制 payload / offsets，转换 Binder 对象与 FD
      同步事务栈 / todo / async_todo（按模式）
      唤醒目标等待线程
Server libbinder
  joinThreadPool / polling -> getAndExecuteCommand
    收到 BR_TRANSACTION 或 BR_TRANSACTION_SEC_CTX
    executeCommand
      保存原 calling identity，设置此次 caller PID/UID/SID
      buffer.ipcSetDataReference(接收 mmap 地址)
      由 tr.cookie/ptr 恢复目标 BBinder
      BBinder::transact -> JavaBBinder::onTransact
Server JNI / Java
  CallBooleanMethod(Binder.execTransact, native Parcel 对象地址, ...)
    Parcel.obtain(nativePtr)
    execTransactInternal
      AIDL Stub.onTransact
        enforceInterface -> 读参数 -> enforceNoDataAvail
        this.getData(id)
        reply.writeNoException -> reply.writeInt(result)
      observer/trace/异常处理
    finally recycle Parcel wrapper / 恢复 WorkSource
Server reply
  IPCThreadState::sendReply -> BC_REPLY -> driver
    同步事务栈定位原调用线程
Client resume
  waitForResponse 收到 BR_REPLY
    reply.ipcSetDataReference -> 返回 JNI -> Java
  Proxy: reply.readException -> reply.readInt
  finally recycle data/reply
  native freeBuffer -> BC_FREE_BUFFER 归还接收映射 buffer
```

**同步等待期间的分支：** Client 的 waitForResponse 可以收到嵌套入站事务、死亡/引用协议或错误，不能只处理 BR_REPLY。单次 ioctl 的 read buffer 是命令/描述符，不是所有业务 payload。

**本地分支：** asInterface 命中 queryLocalInterface 时直接调用本地实现，不走序列化和驱动；这也意味着业务方法可能在任意调用者线程执行。

**oneway 分支：** flags 包含 TF_ONE_WAY 时，不建立业务 reply 等待，但仍等待驱动的提交完成。服务端执行资源和错误处理见第 19.1 节。

**资源顺序：** 归还 buffer 与发送 reply 是独立协议动作；Java wrapper recycle、native Parcel 数据引用释放、BC_FREE_BUFFER 和驱动实际回收不是同一个时刻。

---

## 5. Binder 驱动层

### 5.1 核心数据结构

驱动对象是 per-open Binder 上下文及其节点关系，不能把早期 `binder_proc` 中的 buffer 字段当作当前声明。固定 common commit 的主要分工：

```text
binder_proc
  threads                binder_thread 红黑树
  nodes                  本进程 binder_node
  refs_by_desc/by_node    本上下文持有的 binder_ref 索引
  todo / waiting_threads  进程待办与空闲 Binder 线程
  alloc                  struct binder_alloc，负责接收缓冲区
  max_threads/requested_threads_started   驱动扩容计数

binder_thread
  proc / pid             所属上下文和 Linux TID
  transaction_stack      同步嵌套事务栈
  todo / wait            定向线程的工作与等待

binder_node
  proc / ptr / cookie    实体拥有者及用户态标识
  refs                   各进程对此节点的引用
  has_async_transaction / async_todo     同一 node 的 oneway 串行化

binder_ref
  proc / node            引用持有者与指向的实体
  data.desc/strong/weak  handle 与计数，非全局地址

binder_transaction
  from/from_parent       发送线程和嵌套链
  to_proc/to_thread/to_parent  目标及返回链
  buffer/code/flags      本次事务数据与标志
  sender_euid            内核凭据；不是另设固定 sender_pid 字段

binder_buffer / binder_alloc
  user_data/data_size/offsets_size  接收地址和区域大小
  allocated/free buffers / pages   分配记账与页管理
```

同一服务可被多个进程引用，各自 desc 不同；传递 handle 的整数值不能让另一个进程直接得到同一对象。node 死亡后驱动还需处理 refs/death work，不是简单 free 节点就能完成所有清理。

同步事务可以直接投递到嵌套调用栈中的等待线程；其他请求进入线程/进程 todo，oneway 还受 node 的 async_todo 限制。因此“所有事务都加到 target_proc->todo”只覆盖一部分分派情况。

---

### 5.2 内存映射 (mmap)

```text
发送进程 Parcel 的序列化 payload
  -> 驱动复制到接收方 binder_alloc 管理的页面
  -> 页面映射于接收进程先前 mmap 的地址范围
  -> BR_TRANSACTION 描述符给出接收地址
  -> Parcel::ipcSetDataReference 读取该范围
```

“一次拷贝”指一个方向的主要 payload 从发送缓冲区到接收缓冲区的内核搬运，不包括序列化、接收方解码成 Java 对象以及回程 reply 的另一笔传输。双方不是直接共享发送方 Parcel 内存。

common commit 的 `binder_mmap()` 调用 allocator 的 mmap handler；`binder_alloc_mmap_handler()` 建立地址范围/页数组等元数据，事务分配时按需配置 backing pages。不存在旧伪码的 `proc->buffer = kzalloc(整个范围)`、循环一次性 `alloc_page()` 后 `set_page_address()` 的当前路径。

libbinder 固定 tag 的预算公式：

```cpp
#define BINDER_VM_SIZE ((1 * 1024 * 1024) - sysconf(_SC_PAGE_SIZE) * 2)
```

在 4KiB 页设备是 1MiB-8KiB，16KiB 页则是 1MiB-32KiB；不是 Android 全设备硬编码 8KiB。这个公式是用户态映射预算，不足以证明“驱动里固定分配两个 guard page”。当前 C++ servicemanager 使用同一个 ProcessState，不再是旧 C 版 binder_open(128KiB)。

缓冲区由接收进程的多笔在途事务共享，并包含 offsets/object 元数据；oneway 另有异步空间记账。即使某一 Parcel 小于映射总大小，也可能因并发占用/碎片/其他分配失败而发生 FAILED_TRANSACTION，不能承诺“单笔小于 1MB 就安全”。

接收方 Parcel 不再使用数据时，native freeBuffer 回调写 `BC_FREE_BUFFER` 归还驱动缓冲区。`BC_REPLY` 表示提交响应，不等于每个请求缓冲区都会在这一步立即释放。

---

### 5.3 ioctl 命令

`BINDER_WRITE_READ` 是 ioctl request；BC/BR 是它所携带字节流中的协议命令，二者不要混成同一层枚举。

| 命令 | 方向 | 含义 |
|------|------|------|
| BC_TRANSACTION / BC_REPLY | 用户 -> 驱动 | 请求 / 同步响应 |
| BC_FREE_BUFFER | 用户 -> 驱动 | 归还已消费的接收 buffer |
| BC_ENTER_LOOPER / BC_REGISTER_LOOPER | 用户 -> 驱动 | 主动加入 / 响应驱动扩容请求的线程注册 |
| BC_REQUEST_DEATH_NOTIFICATION | 用户 -> 驱动 | 监听目标死亡 |
| BR_TRANSACTION / BR_REPLY | 驱动 -> 用户 | 收到事务描述符 / 回复描述符 |
| BR_TRANSACTION_COMPLETE | 驱动 -> 用户 | 提交完成，不表示远端业务已经完成 |
| BR_SPAWN_LOOPER | 驱动 -> 用户 | 请求用户态创建工作线程 |
| BR_DEAD_REPLY / BR_FAILED_REPLY | 驱动 -> 用户 | 对端死亡 / 事务失败 |
| BR_FROZEN_REPLY / BR_TRANSACTION_PENDING_FROZEN | 驱动 -> 用户 | 冻结状态相关返回，需结合特性和事务模式处理 |

`binder_write_read.write_buffer`/`read_buffer` 指向命令缓冲区；bulk payload 的地址和 offsets 通过 `binder_transaction_data` 描述，而不是直接把所有 payload 拷进 read_buffer。处理循环须尊重 write_consumed/read_consumed，不能假定一次 ioctl 恰好处理一笔业务。

原文将 BR_TRANSACTION_COMPLETE 编成 `_IO('r',15)`、BR_DEAD_REPLY 编成 16、BR_FAILED_REPLY 编成 17，混淆了协议值；此处不手写一套枚举。具体编码以当前 libbinder 使用的 UAPI `linux/android/binder.h` 为准（传统编号分别是 6、5、17），新增返回值由协议头和 `executeCommand` 对应处理。

---

## 6. Native 层

### 6.1 ProcessState

ProcessState 是 libbinder 的进程单例，初始化打开指定 Binder driver，查询协议/feature、设置线程请求额度并 mmap 接收地址区。`self()` 经 `init()` 管理单例，不是旧版无参构造加全局锁的原样源码。

```text
ProcessState::self()
  -> init(kDefaultDriver, false)
  -> ProcessState(driver)
     -> open_driver(driver)
     -> mmap(..., BINDER_VM_SIZE, PROT_READ,
             MAP_PRIVATE | MAP_NORESERVE, driverFD, 0)
```

它维护 handle->BpBinder 的 handle_entry 及弱引用信息，避免为同一 handle 无限制创建代理。`getStrongProxyForHandle()` 要同时处理既存 weak 引用的升级、创建失败与 handle 0 的特殊探测，不是一个只缓存 strong pointer 的普通数组。

`startThreadPool()` 才显式启动首个 PoolThread，构造本身不启动池；`joinThreadPool()` 属于 IPCThreadState 而不是 ProcessState。进程 fork 后不能直接复用已经初始化的 Binder 上下文，源码有 fork 后误用检查。

```cpp
// 应用/系统 native 侧初始化示意；普通 SDK 应用不直接调用这些隐藏接口。
sp<ProcessState> ps = ProcessState::self();
ps->startThreadPool();
// 专用 native daemon 如需让当前线程参与处理，可主动：
IPCThreadState::self()->joinThreadPool();
// app UI 线程通常不做上述 join，而是进入 Java Looper。
```

映射失败/driver 打开失败不能当作“没有服务缓存命中”处理，它们属于 transport 初始化失败。Binder RPC 不使用相同 kernel driver 路径，需要单独分析。

---

### 6.2 IPCThreadState

IPCThreadState 使用线程局部状态管理 mIn/mOut、调用身份、事务处理及死亡通知。Java 调用、native daemon 线程和 Binder pool 线程都可能按需取得当前线程实例，它不等于“只有线程池线程才能 transact”。

`writeTransactionData()` 把 BC 命令与 binder_transaction_data 写入 **mOut**；真正 ioctl 在 `talkWithDriver()`，不是 writeTransactionData 内部直接发送。`transact()` 先加入 TF_ACCEPT_FDS、检查 Parcel，再写入命令，最后区分同步和 oneway：

```cpp
// android-17.0.0_r1 transact 核心分支节选（省略 call restriction / tracing）。
if ((flags & TF_ONE_WAY) == 0) {
    if (reply) {
        err = waitForResponse(reply);
    } else {
        Parcel fakeReply;
        err = waitForResponse(&fakeReply);
    }
} else {
    err = waitForResponse(nullptr, nullptr);
}
```

因此 `reply == nullptr` 不意味着 oneway，flags 才决定；同步无 reply 仍读掉 fakeReply，oneway 仍通过 waitForResponse 驱动提交完成。

下面是 waitForResponse 的返回协议分支（固定 tag 行 1173–1197）：

```cpp
        switch (cmd) {
        case BR_ONEWAY_SPAM_SUSPECT:
            ALOGE("Process seems to be sending too many oneway calls.");
            CallStack::logStack("oneway spamming", CallStack::getCurrent().get(),
                    ANDROID_LOG_ERROR);
            [[fallthrough]];
        case BR_TRANSACTION_COMPLETE:
            if (!reply && !acquireResult) goto finish;
            break;

        case BR_TRANSACTION_PENDING_FROZEN:
            ALOGW("Sending oneway calls to frozen process.");
            goto finish;

        case BR_DEAD_REPLY:
            err = DEAD_OBJECT;
            goto finish;

        case BR_FAILED_REPLY:
            err = FAILED_TRANSACTION;
            goto finish;

        case BR_FROZEN_REPLY:
            err = enableFrozenObjectErrorCode() ? FROZEN_OBJECT : FAILED_TRANSACTION;
            goto finish;
```

收到 BR_REPLY 时按 TF_STATUS_CODE 区分状态 payload 和普通 Parcel；普通回复用 ipcSetDataReference 引用映射区，不再复制一遍。收到非回复命令则 `executeCommand(cmd)`，这使同步等待线程可以处理嵌套入站事务，并解释第 20 章为什么“回调必死锁”是错误结论。

`joinThreadPool(isMain)` 发送 ENTER/REGISTER 标记，循环 processPendingDerefs/getAndExecuteCommand；TIMED_OUT 对非 main 线程可退出，driver 关闭/拒绝有相应结束和错误分支。源码中的超时处理不能外推为所有 Android Binder 线程均有固定空闲回收周期。

身份状态在 executeCommand 入站时保存并替换，在 transact 返回/入站完成后恢复。跨线程执行时这些 ThreadLocal 状态不会随 Runnable 迁移；服务方法应在入口完成授权，而不是在异步线程再读 getCallingUid 并当原调用方身份。

---

### 6.3 BpBinder 与 BBinder

```text
IBinder
  +-- BBinder（本地实体）
  |     +-- JavaBBinder（Java Binder 的 native 包装）
  +-- BpBinder（远程代理；kernel handle 或 RPC transport）
```

`BpBinder::transact()` 先检查对象活性、稳定性/事务标志等条件，再分支到 kernel 的 `IPCThreadState::transact()` 或 RPC session。不能省掉 transport 判定后把所有 BpBinder 写成只持一个 mHandle 的旧字段布局。

`BBinder::transact()` 处理部分平台保留事务、Parcel 读位置和回复整理，再调用 onTransact；不是所有 code 无条件直达业务重写。JavaBBinder 覆盖 onTransact，把 **native Parcel 对象地址**传给 Java 包装层，而不是把 data.ipcData() 的 payload 地址伪装成 Parcel 指针。

对象关系决定语言层投影：JavaBBinder 可还原原 Java Binder；远程 native 对象由 JNI 对应到 BinderProxy。JavaBBinder 并不是“Java BinderProxy 的服务端包装”。

---

## 7. Framework 层

### 7.1 Binder.java

`Binder` 构造经 `getNativeBBinderHolder()` 获取 native holder，并由 NativeAllocationRegistry 管理清理；旧文的 `private native void init()` 不是当前初始化接口。AIDL Stub 调用 attachInterface 保存 owner 和 descriptor，queryLocalInterface 命中时直接返回本地实现。

Java 入站方法的实际资源/身份回收边界：

```java
// Binder.java:1304-1332 的控制结构，省略注释。
private boolean execTransact(int code, long dataObj, long replyObj, int flags) {
    Parcel data = Parcel.obtain(dataObj);
    Parcel reply = Parcel.obtain(replyObj);
    final int callingUid = data.isForRpc() ? -1 : Binder.getCallingUid();
    final long origWorkSource = callingUid == -1
            ? -1 : ThreadLocalWorkSource.setUid(callingUid);
    try {
        return execTransactInternal(code, data, reply, flags, callingUid);
    } finally {
        reply.recycle();
        data.recycle();
        if (callingUid != -1) ThreadLocalWorkSource.restore(origWorkSource);
    }
}
```

execTransactInternal 围绕 onTransact 做 observer/trace、异常封送和 StrictMode 等清理。同步调用把可封送异常写入 reply，oneway 没有业务 reply，只记录服务端异常。因此不能用统一 `catch(Exception) { reply.writeException(e); }` 表示所有模式。

JNI 回调发生在 **JavaBBinder::onTransact** 内；不存在另一个名为 android_os_Binder_execTransact 的 native 方法专门完成此桥接。onTransact 默认还支持 interface/dump/shell 等保留事务，业务 Stub 必须对接口 token、参数和权限做正确检查。

---

### 7.2 BinderProxy.java

BinderProxy.transact 不在客户端调用 `data.enforceInterface()`；那会消费请求头且把服务器的校验放错位置。客户端生成代理调用 writeInterfaceToken，服务端生成 Stub 在解析参数前 enforceInterface/enforceNoDataAvail。

```java
// Java 签名，Parcel 参数不是 long dataObj/replyObj。
public boolean transact(int code, Parcel data, Parcel reply, int flags)
        throws RemoteException {
    // 实际实现还含检查、监听、WorkSource/trace 等。
    return transactNative(code, data, reply, flags);
}
public native boolean transactNative(int code, Parcel data, Parcel reply, int flags)
        throws RemoteException;
```

JNI 取得 BinderProxyNativeData 里的 mObject，使用 parcelForJavaObject 转换 jobject Parcel，再 `target->transact(code, *data, reply, flags)`。mNativeData 不是可以直接强转 BpBinder 的地址；参数也不是 jlong 对象。

```cpp
    IBinder* target = getBPNativeData(env, obj)->mObject.get();
    if (target == NULL) {
        jniThrowException(env, "java/lang/IllegalStateException", "Binder has been finalized!");
        return JNI_FALSE;
    }

    ALOGV("Java code calling transact on %p in Java object %p with code %" PRId32 "\n",
            target, obj, code);

    //printf("Transact from Java code to %p sending: ", target); data->print();
    status_t err = target->transact(code, *data, reply, flags);
    //if (reply) printf("Transact from Java code to %p received: ", target); reply->print();

    if (err == NO_ERROR) {
        return JNI_TRUE;
    }

    env->CallStaticVoidMethod(gBinderOffsets.mClass, gBinderOffsets.mTransactionCallback, getpid(),
                              code, flags, err);

    if (err == UNKNOWN_TRANSACTION) {
        return JNI_FALSE;
    }

    signalExceptionForError(env, obj, err, true /*canThrowRemoteException*/, data->dataSize());
    return JNI_FALSE;
```

成功返回 true；UNKNOWN_TRANSACTION 返回 false；其他 transport 失败经 signalExceptionForError 映射到 Java 异常。服务端 reply 中的业务异常则由生成代理随后 readException() 抛出，两类错误不能混为一个 false 返回值。

---

## 8. AIDL 详解

AIDL 片段按文件拆分；生成 Java 展示 dispatch 模式而不是固定生成器逐字输出。真实项目由同 tag 的 AIDL 编译器生成，并保留接口 token/额外数据校验与 RemoteException 声明。

### 8.1 AIDL 语法

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AIDL 语法详解                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  AIDL 支持的数据类型：
  ─────────────────────────────────────────────────────────────────────────────

  1. Java 基本数据类型
     ─────────────────────────────────────────────────────────────────────────
     - byte, int, long（AIDL 不支持 Java short 标量）
     - float, double
     - boolean
     - char

  2. String 和 CharSequence
     ─────────────────────────────────────────────────────────────────────────
     - String
     - CharSequence

  3. List 和 Map
     ─────────────────────────────────────────────────────────────────────────
     - List<T>  (T 必须是支持的类型)
     - Map<K, V>  (K, V 必须是支持的类型)

  4. Parcelable
     ─────────────────────────────────────────────────────────────────────────
     - 自定义类型需要实现 Parcelable 接口
     - 需要在 AIDL 中声明: parcelable User;

  5. 其他 AIDL 接口
     ─────────────────────────────────────────────────────────────────────────
     - 可以传递其他 AIDL 定义的接口


  AIDL 文件示例：
  ─────────────────────────────────────────────────────────────────────────────

  // IMyService.aidl
  package com.example;

  // 声明 Parcelable 类型
  parcelable User;

  // 声明回调接口
  interface ICallback {
      void onResult(int code);
  }

  // 主接口
  interface IMyService {
      // 基本类型
      int getData(int id);

      // String
      String getName();

      // List
      List<String> getNames();

      // Parcelable
      User getUser(int id);

      // 异步回调
      void getDataAsync(int id, ICallback callback);

      // oneway 异步调用 (不等待返回)
      oneway void notifyEvent(int event);
  }
```

### 8.2 AIDL 生成的代码结构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AIDL 生成的代码结构                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  AIDL 编译后生成的 Java 文件结构：
  ─────────────────────────────────────────────────────────────────────────────

  public interface IMyService extends android.os.IInterface {

      // ========== 方法声明 ==========
      public int getData(int id) throws android.os.RemoteException;

      // ========== Stub 类 (服务端) ==========
      public static abstract class Stub extends android.os.Binder
              implements IMyService {

          private static final String DESCRIPTOR = "com.example.IMyService";

          // 方法编号
          static final int TRANSACTION_getData = 1;
          static final int TRANSACTION_getName = 2;

          /**
           * 将 Binder 转换为接口
           */
          public static IMyService asInterface(android.os.IBinder obj) {
              if (obj == null) return null;

              // 检查是否在同一进程
              android.os.IInterface iin = obj.queryLocalInterface(DESCRIPTOR);
              if (iin instanceof IMyService) {
                  // ★ 同一进程，直接返回 ★
                  return (IMyService) iin;
              }

              // ★ 跨进程，返回 Proxy ★
              return new Proxy(obj);
          }

          /**
           * 服务端处理事务
           */
          @Override
          public boolean onTransact(int code, Parcel data, Parcel reply, int flags) throws RemoteException {
              switch (code) {
                  case INTERFACE_TRANSACTION: {
                      reply.writeString(DESCRIPTOR);
                      return true;
                  }

                  case TRANSACTION_getData: {
                      data.enforceInterface(DESCRIPTOR);
                      int _arg0 = data.readInt();
                      // ★★★ 调用实际方法 ★★★
                      int _result = this.getData(_arg0);
                      reply.writeNoException();
                      reply.writeInt(_result);
                      return true;
                  }
              }
              return super.onTransact(code, data, reply, flags);
          }

          // ========== Proxy 类 (客户端) ==========
          private static class Proxy implements IMyService {

              private android.os.IBinder mRemote;

              Proxy(android.os.IBinder remote) {
                  mRemote = remote;
              }

              @Override
              public int getData(int id) throws android.os.RemoteException {
                  Parcel _data = Parcel.obtain();
                  Parcel _reply = Parcel.obtain();
                  int _result;

                  try {
                      _data.writeInterfaceToken(DESCRIPTOR);
                      _data.writeInt(id);

                      // ★★★ 发起远程调用 ★★★
                      mRemote.transact(TRANSACTION_getData, _data, _reply, 0);

                      _reply.readException();
                      _result = _reply.readInt();
                  } finally {
                      _reply.recycle();
                      _data.recycle();
                  }

                  return _result;
              }
          }
      }
  }
```

### 8.3 AIDL 完整示例

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AIDL 双向通信完整示例                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 定义 Parcelable 数据类
  ─────────────────────────────────────────────────────────────────────────────

  // User.java
  public class User implements Parcelable {
      public int id;
      public String name;

      public User(int id, String name) {
          this.id = id;
          this.name = name;
      }

      protected User(Parcel in) {
          id = in.readInt();
          name = in.readString();
      }

      public static final Creator<User> CREATOR = new Creator<User>() {
          @Override
          public User createFromParcel(Parcel in) {
              return new User(in);
          }

          @Override
          public User[] newArray(int size) {
              return new User[size];
          }
      };

      @Override
      public int describeContents() {
          return 0;
      }

      @Override
      public void writeToParcel(Parcel dest, int flags) {
          dest.writeInt(id);
          dest.writeString(name);
      }
  }


  2. 定义 AIDL 接口
  ─────────────────────────────────────────────────────────────────────────────

  // User.aidl
  parcelable User;

  // ICallback.aidl
  interface ICallback {
      void onUserReceived(in User user);
      void onError(int code);
  }

  // IUserService.aidl
  interface IUserService {
      User getUser(int id);
      void getUserAsync(int id, ICallback callback);
      void registerCallback(ICallback callback);
      void unregisterCallback(ICallback callback);
  }


  3. 服务端实现
  ─────────────────────────────────────────────────────────────────────────────

  // UserService.java
  public class UserService extends Service {

      private final RemoteCallbackList<ICallback> mCallbacks = new RemoteCallbackList<>();

      private final IUserService.Stub mBinder = new IUserService.Stub() {

          @Override
          public User getUser(int id) {
              // 模拟查询
              return new User(id, "User_" + id);
          }

          @Override
          public void getUserAsync(int id, ICallback callback) {
              // 在后台线程执行
              new Thread(() -> {
                  try {
                      User user = getUser(id);
                      // ★★★ 回调客户端 ★★★
                      callback.onUserReceived(user);
                  } catch (RemoteException e) {
                      try {
                          callback.onError(-1);
                      } catch (RemoteException ex) {
                          ex.printStackTrace();
                      }
                  }
              }).start();
          }

          @Override
          public void registerCallback(ICallback callback) {
              if (callback != null) {
                  mCallbacks.register(callback);
              }
          }

          @Override
          public void unregisterCallback(ICallback callback) {
              if (callback != null) {
                  mCallbacks.unregister(callback);
              }
          }
      };

      @Override
      public IBinder onBind(Intent intent) {
          return mBinder;
      }

      // 通知所有注册的客户端
      // 调用应在同一工作线程串行执行；避免重叠 beginBroadcast。
    private void notifyAllClients(User user) {
        int count = mCallbacks.beginBroadcast();
        try {
            for (int i = 0; i < count; i++) {
                try { mCallbacks.getBroadcastItem(i).onUserReceived(user); }
                catch (RemoteException ignored) { /* 死亡清理由 RemoteCallbackList 管理 */ }
            }
        } finally {
            mCallbacks.finishBroadcast();
        }
    }

    @Override public void onDestroy() {
        mCallbacks.kill();
        super.onDestroy();
    }

  }


  4. 客户端实现
  ─────────────────────────────────────────────────────────────────────────────

  // MainActivity.java
  public class MainActivity extends Activity {

      private IUserService mService;
      private boolean mBound = false;

      private ICallback mCallback = new ICallback.Stub() {
          @Override
          public void onUserReceived(User user) {
              runOnUiThread(() -> {
                  Toast.makeText(MainActivity.this,
                          "Received: " + user.name, Toast.LENGTH_SHORT).show();
              });
          }

          @Override
          public void onError(int code) {
              runOnUiThread(() -> {
                  Toast.makeText(MainActivity.this,
                          "Error: " + code, Toast.LENGTH_SHORT).show();
              });
          }
      };

      private ServiceConnection mConnection = new ServiceConnection() {
          @Override
          public void onServiceConnected(ComponentName name, IBinder service) {
              // ★ 获取服务接口 ★
              mService = IUserService.Stub.asInterface(service);
              mBound = true;

              try {
                  // 注册回调
                  mService.registerCallback(mCallback);

                  // 同步调用
                  User user = mService.getUser(1);
                  Log.d("MainActivity", "Sync: " + user.name);

                  // 异步调用
                  mService.getUserAsync(2, mCallback);

              } catch (RemoteException e) {
                  e.printStackTrace();
              }
          }

          @Override
          public void onServiceDisconnected(ComponentName name) {
              mService = null;
              mBound = false;
          }
      };

      @Override
      protected void onStart() {
          super.onStart();
          Intent intent = new Intent("com.example.UserService");
          intent.setPackage("com.example");
          bindService(intent, mConnection, BIND_AUTO_CREATE);
      }

      @Override
      protected void onStop() {
          super.onStop();
          if (mBound) {
              try {
                  mService.unregisterCallback(mCallback);
              } catch (RemoteException e) {
                  e.printStackTrace();
              }
              unbindService(mConnection);
              mBound = false;
          }
      }
  }
```

---

## 9. Binder 线程池

```text
app 进程 RuntimeInit nativeZygoteInit / onZygoteInit
  -> ProcessState::self()->startThreadPool()
     -> spawnPooledThread(true)
        -> 新 PoolThread（不是 UI 线程）
           -> IPCThreadState::joinThreadPool(true)
              -> BC_ENTER_LOOPER
  UI/main 线程继续 ActivityThread.main -> Looper.loop

驱动判断需要额外工作线程
  -> BR_SPAWN_LOOPER
  -> IPCThreadState::executeCommand
  -> ProcessState::spawnPooledThread(false)
  -> 新用户态线程 joinThreadPool(false) -> BC_REGISTER_LOOPER
```

默认 DEFAULT_MAX_BINDER_THREADS 为 15，设置的是驱动请求创建线程额度。普通启动一个首线程再允许驱动扩容时，常见可达 1+15；主动 join、系统服务重新配置及 polling 模型不属于“全 Android 固定 16”的规则。首个线程的 isMain 参数表示池角色，不能在图中把 Activity 生命周期/UI 分发放进这个线程。

池上限不是服务方法的并发安全屏障：本地 AIDL 直调执行在调用者线程，入站同步事务可嵌套回入等待线程。服务应对可共享状态设计锁/单线程所有权，并避免持业务锁跨远程调用。

同一 node 的 oneway 串行并不保证低负载；大量 oneway 能积压异步 buffer，服务端执行慢仍会耗尽资源。把耗时业务提交到受控队列后返回，需明确拒绝、任务 ID、结果回调、取消和调用身份，不能无限 new Thread 或把排队转移成另一个无界队列。

---

## 10. 跨进程通信方式对比

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Android 跨进程通信方式完整对比                           │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┬───────────────────┬───────────────────┬─────────────────┐
  │      方式        │      适用场景      │       优点        │      缺点       │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ Bundle + Intent  │ 简单参数传递       │ 简单快捷          │ 数据量小        │
  │                  │ Activity 启动传参  │ 系统原生支持      │ 单向通信        │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ 文件共享         │ 低频数据持久化     │ 实现简单          │ 并发需同步      │
  │                  │ 大数据传递        │ 无大小限制        │ 实时性差        │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ AIDL             │ 复杂远程方法调用   │ 支持并发          │ 实现复杂        │
  │                  │ 双向通信          │ 功能强大          │ 需处理线程安全  │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ Messenger        │ 简单消息传递       │ 简化线程管理      │ 单向通信        │
  │                  │ 基于 Binder       │ 自动排队          │ 不支持并发      │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ ContentProvider  │ 结构化数据共享     │ 标准化接口        │ 实现复杂        │
  │                  │ 数据库共享        │ 权限控制          │                │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ Socket           │ 跨设备通信        │ 灵活              │ 网络状态处理    │
  │                  │ 实时双向通信      │ 跨平台            │ 复杂            │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ 共享内存         │ 大数据高速传输     │ 零拷贝            │ 需要同步机制    │
  │ (MemoryFile)     │ 实时数据共享      │ 最高性能          │ 复杂            │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ 管道 (Pipe)      │ 简单数据流传输     │ 简单              │ 单向            │
  │                  │ 父子进程通信      │                   │ 可通过 FD 传递连接非亲缘进程    │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ 信号 (Signal)    │ 进程通知          │ 轻量级            │ 只能通知        │
  │                  │ 异常处理          │                   │ 不能传数据      │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ 消息队列         │ 异步消息传递       │ 解耦              │ 性能一般        │
  │ (MessageQueue)   │                  │                   │                │
  ├──────────────────┼───────────────────┼───────────────────┼─────────────────┤
  │ 信号量           │ 进程同步          │ 简单              │ 只能同步        │
  │ (Semaphore)      │ 资源互斥          │                   │ 不能传数据      │
  └──────────────────┴───────────────────┴───────────────────┴─────────────────┘


  性能对比 (拷贝次数)：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  通信方式              内存拷贝次数          性能评级                     │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  共享内存               0 次                 ★★★★★ (最高，需同步)        │
  │  Binder                 1 次                 ★★★★★ (推荐)               │
  │  Socket                 2 次                 ★★★☆☆                      │
  │  管道 (Pipe)            2 次                 ★★★☆☆                      │
  │  消息队列               2 次                 ★★★☆☆                      │
  │  信号 (Signal)          0 次                 ★★☆☆☆ (只能通知)           │
  │  信号量 (Semaphore)     0 次                 ★★☆☆☆ (只能同步)           │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  选择建议：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  场景                              推荐方案                             │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  简单参数传递                      Bundle + Intent                      │
  │  大文件/图片传递                   文件共享 / Uri                        │
  │  复杂业务交互                      AIDL                                  │
  │  简单消息通知                      Messenger                             │
  │  数据库共享                        ContentProvider                       │
  │  跨设备通信                        Socket                                │
  │  大数据实时传输                    共享内存 (MemoryFile)                  │
  │  高频小数据传输                    Binder (AIDL)                         │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 10.1 Bundle + Intent

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Bundle + Intent                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  特点：
  ─────────────────────────────────────────────────────────────────────────────
  - 最简单的 IPC 方式
  - 基于 Binder 实现
  - 适用于 Activity、Service、BroadcastReceiver 之间传递数据


  支持的数据类型：
  ─────────────────────────────────────────────────────────────────────────────

  1. 基本数据类型：byte, short, int, long, float, double, boolean, char
  2. 基本数据类型数组
  3. String 和 CharSequence
  4. Parcelable 实现类
  5. Serializable 实现类
  6. Bundle 本身
  7. IBinder


  使用示例：
  ─────────────────────────────────────────────────────────────────────────────

  // 发送方
  Intent intent = new Intent(this, TargetActivity.class);
  intent.putExtra("string_key", "Hello");
  intent.putExtra("int_key", 100);
  intent.putExtra("boolean_key", true);

  // 传递 Parcelable 对象
  User user = new User("张三", 25);
  intent.putExtra("user_key", user);

  startActivity(intent);


  // 接收方
  public class TargetActivity extends Activity {
      @Override
      protected void onCreate(Bundle savedInstanceState) {
          super.onCreate(savedInstanceState);

          Intent intent = getIntent();
          String stringValue = intent.getStringExtra("string_key");
          int intValue = intent.getIntExtra("int_key", 0);
          boolean boolValue = intent.getBooleanExtra("boolean_key", false);

          User user = intent.getParcelableExtra("user_key");
      }
  }


  注意事项：
  ─────────────────────────────────────────────────────────────────────────────

  1. 数据占接收方共享 Binder buffer（1MiB - 2*pageSize 映射预算）
  2. 不要传递大对象
  3. Parcelable 比 Serializable 效率高
  4. 跨进程传递时，对象会被序列化/反序列化
```

### 10.2 共享内存 (MemoryFile)

MemoryFile 是历史封装，其 getFileDescriptor 为非 SDK 接口。Android 17 应用侧使用公开 `android.os.SharedMemory`（API 27+），把它作为 Parcelable 经 Binder/Bundle 传递，不必反射 FD。

```java
// 发送方：先写完再限制为只读，最后发送，示例为一次发布而非可变共享协议。
SharedMemory memory = SharedMemory.create("payload", bytes.length);
ByteBuffer writable = memory.mapReadWrite();
try {
    writable.put(bytes);
} finally {
    SharedMemory.unmap(writable);
}
if (!memory.setProtect(OsConstants.PROT_READ)) {
    memory.close();
    throw new IOException("Unable to protect shared memory");
}
Bundle data = new Bundle();
data.putParcelable("memory", memory);
// 将 data 通过自有 AIDL/Messenger 发送；传输完成后 close 本地 memory。

// 接收方（取得自己的 SharedMemory/FD 所有权）：
SharedMemory received = data.getParcelable("memory", SharedMemory.class);
if (received == null) throw new IllegalArgumentException("missing memory");
ByteBuffer readable = received.mapReadOnly();
try {
    // 按协议边界解析，验证长度和版本；不让发送方控制越界访问。
} finally {
    SharedMemory.unmap(readable);
    received.close();
}
```

发送方 buffer 写入本身仍是内存写/拷贝，“零拷贝”指不再把整个 payload 通过 Binder 中转。只读发布需要先取消已有可写映射，setProtect 不会倒过来撤销既存映射的写权限；可变共享数据则必须设计跨进程同步和版本/长度一致性协议。

---

### 10.3 管道 (Pipe)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         管道 (Pipe)                                         │
└─────────────────────────────────────────────────────────────────────────────┘

  特点：
  ─────────────────────────────────────────────────────────────────────────────
  - 单向通信（半双工）
  - 匿名管道需共享端点；端点可经 Binder FD 传给非亲缘进程
  - 在 Android 中较少使用


  使用示例：
  ─────────────────────────────────────────────────────────────────────────────

  // 创建管道
  public class PipeExample {

      private ParcelFileDescriptor[] mPipe;

      public void createPipe() throws IOException {
          // 创建管道，返回读端和写端
          mPipe = ParcelFileDescriptor.createPipe();

          // mPipe[0] - 读端
          // mPipe[1] - 写端
      }

      // 写入数据
      public void write(byte[] data) throws IOException {
          FileOutputStream fos = new FileOutputStream(mPipe[1].getFileDescriptor());
          fos.write(data);
      }

      // 读取数据
      public byte[] read(int size) throws IOException {
          FileInputStream fis = new FileInputStream(mPipe[0].getFileDescriptor());
          byte[] buffer = new byte[size];
          fis.read(buffer);
          return buffer;
      }
  }
```

### 10.4 信号 (Signal)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         信号 (Signal)                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  特点：
  ─────────────────────────────────────────────────────────────────────────────
  - 只能发送通知，不能传递数据
  - 轻量级
  - 在 Android 中较少直接使用


  常见信号：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────┬─────────────────────────────────────────────────────────────┐
  │    信号     │                      含义                                    │
  ├─────────────┼─────────────────────────────────────────────────────────────┤
  │ SIGKILL     │ 强制终止进程                                                 │
  │ SIGTERM     │ 正常终止进程                                                 │
  │ SIGSTOP     │ 暂停进程                                                     │
  │ SIGCONT     │ 继续进程                                                     │
  │ SIGSEGV     │ 段错误                                                       │
  │ SIGPIPE     │ 管道破裂                                                     │
  └─────────────┴─────────────────────────────────────────────────────────────┘


  使用示例：
  ─────────────────────────────────────────────────────────────────────────────

  // 发送信号
  Process.sendSignal(pid, Process.SIGNAL_KILL);

  // 或使用 shell 命令
  // adb shell kill -9 <pid>
```

### 10.5 消息队列

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         消息队列 (Message Queue)                            │
└─────────────────────────────────────────────────────────────────────────────┘

  特点：
  ─────────────────────────────────────────────────────────────────────────────
  - 异步通信
  - 是否持久化由实现决定，Handler/Messenger 不持久化
  - 在 Android 中可以使用第三方库


  实现方式：
  ─────────────────────────────────────────────────────────────────────────────

  1. Android 原生 Handler + Messenger
  2. 普通 EventBus 只在进程内工作；跨进程需额外 IPC 桥
  3. RabbitMQ / Kafka（需要服务端）


  轻量级消息队列示例：
  ─────────────────────────────────────────────────────────────────────────────

  // 使用 Messenger 实现简单消息队列
  public class MessageQueueService extends Service {

      private LinkedBlockingQueue<Message> mQueue = new LinkedBlockingQueue<>();

      private Handler mHandler = new Handler(Looper.getMainLooper()) {
          @Override
          public void handleMessage(Message msg) {
              // 将消息放入队列
              mQueue.offer(msg);

              // 处理消息
              processMessages();
          }
      };

      private void processMessages() {
          while (!mQueue.isEmpty()) {
              Message msg = mQueue.poll();
              // 处理消息
          }
      }
  }
```

### 10.6 信号量 (Semaphore)

下面 `java.util.concurrent.Semaphore` 示例只在**同一进程的线程间**共享许可，不能同步两套进程各自 new 出来的实例。跨进程共享内存需使用具有进程共享语义的 native 同步原语或经 Binder 协议协调；不要据名字相同混淆。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         信号量 (Semaphore)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  特点：
  ─────────────────────────────────────────────────────────────────────────────
  - 用于进程同步
  - 不能传递数据
  - 通常与共享内存配合使用


  使用示例：
  ─────────────────────────────────────────────────────────────────────────────

  // 进程 A
  public class ProcessA {

      private Semaphore mSemaphore;

      public void init() throws Exception {
          // 创建信号量
          mSemaphore = new Semaphore(1);
      }

      public void accessSharedResource() throws InterruptedException {
          // 获取许可
          mSemaphore.acquire();

          try {
              // 访问共享资源
          } finally {
              // 释放许可
              mSemaphore.release();
          }
      }
  }
```

### 10.7 各种 IPC 方式完整对比表

下表拷贝次数仅比较典型用户态 buffered payload 路径，不含序列化/硬件/零拷贝变体；“无限”表示不受单次 Binder payload 的同一限制，并非没有内存、单行 CursorWindow、文件/磁盘等边界。安全性取决于权限、凭据验证和协议，不是 IPC 类型自带统一评分。Messenger 可借 replyTo 双向通信。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IPC 方式完整对比表                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐
  │     方式     │  拷贝   │  数据   │  通信   │  实现   │  安全   │  适用   │
  │              │  次数   │  大小   │  方向   │  复杂度 │  性     │  场景   │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ Bundle+Intent│   1次   │  <1MB   │  单向   │   低    │   高    │  简单   │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ 文件共享     │   2次   │  无限   │  双向   │   低    │   低    │  大数据 │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ AIDL         │   1次   │  <1MB   │  双向   │   高    │   高    │  复杂   │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ Messenger    │   1次   │  <1MB   │  单向   │   中    │   高    │  消息   │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ContentProvider│  1次   │  无限   │  双向   │   高    │   高    │  数据库 │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ Socket       │   2次   │  无限   │  双向   │   中    │   中    │  跨设备 │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ 共享内存     │   0次   │  无限   │  双向   │   高    │   低    │  高性能 │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ 管道         │   2次   │  有限   │  单向   │   低    │   中    │  父子   │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ 信号         │   0次   │  无     │  单向   │   低    │   中    │  通知   │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ 消息队列     │   2次   │  有限   │  双向   │   中    │   中    │  异步   │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
  │ 信号量       │   0次   │  无     │  N/A    │   中    │   中    │  同步   │
  └──────────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘


  推荐使用优先级：
  ─────────────────────────────────────────────────────────────────────────────

  1. Bundle + Intent - 最简单，优先考虑
  2. AIDL - 复杂业务交互
  3. ContentProvider - 数据共享
  4. Messenger - 简单消息
  5. 文件共享 - 大数据
  6. 共享内存 - 极致性能
  7. Socket - 跨设备
```

---

## 11. 常见问题

### 11.1 TransactionTooLargeException

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TransactionTooLargeException                            │
└─────────────────────────────────────────────────────────────────────────────┘

  原因：
  ─────────────────────────────────────────────────────────────────────────────
  接收缓冲区不足：请求或回复太大、多笔在途事务占用均可能触发

  解决方案：
  ─────────────────────────────────────────────────────────────────────────────
  1. 控制序列化后的 payload，Bundle 本身不会自动限制大小
  2. 大数据使用文件共享或 ContentProvider
  3. EventBus 仅适用于同进程事件，不替代 IPC
  4. 单例只在同进程共享，不能替代跨进程数据传输


  代码示例：
  ─────────────────────────────────────────────────────────────────────────────

  // ❌ 错误：传递大数据
  Intent intent = new Intent(this, SecondActivity.class);
  intent.putExtra("image", largeBitmap);  // 可能超过 1M
  startActivity(intent);

  // ✅ 正确：使用文件
  // 保存到文件
  File tempFile = new File(getCacheDir(), "temp_image.jpg");
  saveBitmapToFile(largeBitmap, tempFile);

  // 传递文件路径
  Intent intent = new Intent(this, SecondActivity.class);
  intent.putExtra("image_path", tempFile.getAbsolutePath());
  startActivity(intent);
```

### 11.2 Binder 线程耗尽

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 线程耗尽                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  原因：
  ─────────────────────────────────────────────────────────────────────────────
  当前进程的所有可用 Binder 工作线程都被阻塞，无法处理新请求

  解决方案：
  ─────────────────────────────────────────────────────────────────────────────
  1. 避免在 Binder 方法中执行耗时操作
  2. 使用异步方式处理请求
  3. oneway 仍占服务端线程；需缩短处理或设计有界异步队列


  代码示例：
  ─────────────────────────────────────────────────────────────────────────────

  // ❌ 错误：在 Binder 方法中执行耗时操作
  public int getData(int id) {
      // 耗时操作，阻塞 Binder 线程
      String result = slowNetworkRequest();
      return result.length();
  }

  // ✅ 正确：使用异步方式
  // AIDL 定义
  interface IMyService {
      void getDataAsync(int id, ICallback callback);
  }

  // 实现
  public void getDataAsync(int id, ICallback callback) {
      new Thread(() -> {
          String result = slowNetworkRequest();
          try {
              callback.onResult(result.length());
          } catch (RemoteException e) {
              e.printStackTrace();
          }
      }).start();
  }

  // ✅ 使用 oneway (不等待返回)
  oneway void notifyEvent(int event);
```

### 11.3 Binder 死亡通知

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 死亡通知                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  使用 DeathRecipient 监听远程服务死亡：
  ─────────────────────────────────────────────────────────────────────────────

  public class MainActivity extends Activity {

      private IBinder mRemoteBinder;

      private IBinder.DeathRecipient mDeathRecipient = new IBinder.DeathRecipient() {
          @Override
          public void binderDied() {
              // ★ Binder 死亡回调 ★
              // 注意：在 Binder 线程中执行，不能直接更新 UI
              if (mRemoteBinder != null) {
                  mRemoteBinder.unlinkToDeath(this, 0);
                  mRemoteBinder = null;
              }

              runOnUiThread(() -> {
                  Toast.makeText(MainActivity.this,
                          "Service died", Toast.LENGTH_SHORT).show();
                  // 重新绑定服务
                  rebindService();
              });
          }
      };

      private void linkToDeath(IBinder binder) {
          try {
              // ★ 注册死亡通知 ★
              binder.linkToDeath(mDeathRecipient, 0);
              mRemoteBinder = binder;
          } catch (RemoteException e) {
              e.printStackTrace();
          }
      }
  }
```

---

## 12. ServiceManager

系统服务注册中心以名称索引 Binder 引用；handle 0 是 Binder context manager 的特殊入口，不是每个服务都用 0。

```text
init 启动 /system/bin/servicemanager
  -> frameworks/native/cmds/servicemanager/main.cpp
  -> ProcessState::initWithDriver(driver)
  -> setThreadPoolMaxThreadCount(0)
  -> 创建 ServiceManager / Access，注册 manager
  -> IPCThreadState::setTheContextObject(manager)
  -> becomeContextManager()
  -> Looper + BinderCallback 的 polling 模式处理 driver 事件
```

这是当前 C++ 实现，不是旧 `service_manager.c -> binder_open(128*1024) -> binder_loop`。它使用 ProcessState 的 mmap 预算，线程请求额度为 0，但主 polling 线程照常处理请求；“0 线程”不能解释成没有任何线程执行。

Java `ServiceManager.getService(name)` 先查 sCache，再 `Binder.allowBlocking(rawGetService(name))`；底层代理/兼容包装处理 service manager 协议。addService 经过访问控制、名称检查和 SELinux 等约束，不是普通应用可随意向系统注册任意服务的 SDK。

查找成功得到远程 Binder 并不保证下一次 transact 仍存活；缓存需处理死亡和重新获取。把获取服务的动作写成总会阻塞直到存在也不准确，需区分 getService/checkService/waitForService 的具体协议及 lazy service 路径。

---

## 13. Messenger

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Messenger 详解                                      │
│  源码位置: frameworks/base/core/java/android/os/Messenger.java              │
└─────────────────────────────────────────────────────────────────────────────┘

  Messenger 是对 Binder 的轻量级封装，用于简单的消息传递：

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  特点：                                                                 │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  1. 基于 Handler + Binder 实现                                          │
  │  2. 一次只处理一个请求（串行）                                           │
  │  3. 不支持并发                                                          │
  │  4. 单向通信（需要两个 Messenger 实现双向）                              │
  │  5. 使用 Message 传递数据                                               │
  │                                                                         │
  │  对比 AIDL：                                                            │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  - Messenger: 简单、串行、消息传递                                       │
  │  - AIDL: 复杂、并发、方法调用                                           │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  源码分析：
  ─────────────────────────────────────────────────────────────────────────────

  // frameworks/base/core/java/android/os/Messenger.java

  public final class Messenger implements Parcelable {

      private final IMessenger mTarget;

      /**
       * 从 Handler 创建 Messenger
       */
      public Messenger(Handler target) {
          mTarget = target.getIMessenger();
      }

      /**
       * 发送消息
       */
      public void send(Message message) throws RemoteException {
          mTarget.send(message);
      }

      /**
       * 获取底层的 IBinder
       */
      public IBinder getBinder() {
          return mTarget.asBinder();
      }
  }


  // IMessenger.aidl
  oneway interface IMessenger {
      void send(in Message msg);
  }


  完整示例：
  ─────────────────────────────────────────────────────────────────────────────

  // 服务端
  public class MessengerService extends Service {

      // 服务端 Handler
      private Handler mHandler = new Handler(Looper.getMainLooper()) {
          @Override
          public void handleMessage(Message msg) {
              switch (msg.what) {
                  case MSG_FROM_CLIENT:
                      // ★ 收到客户端消息 ★
                      String data = msg.getData().getString("msg");
                      Log.d("Service", "Received: " + data);

                      // 回复客户端
                      Message reply = Message.obtain(null, MSG_FROM_SERVER);
                      Bundle bundle = new Bundle();
                      bundle.putString("reply", "Hello from Service");
                      reply.setData(bundle);

                      try {
                          // ★ 通过客户端的 Messenger 回复 ★
                          msg.replyTo.send(reply);
                      } catch (RemoteException e) {
                          e.printStackTrace();
                      }
                      break;
              }
          }
      };

      // 创建 Messenger
      private final Messenger mMessenger = new Messenger(mHandler);

      @Override
      public IBinder onBind(Intent intent) {
          // ★ 返回 Messenger 的 Binder ★
          return mMessenger.getBinder();
      }
  }


  // 客户端
  public class MainActivity extends Activity {

      private Messenger mServiceMessenger;
      private boolean mBound = false;

      // 客户端 Handler (接收服务端回复)
      private Handler mHandler = new Handler(Looper.getMainLooper()) {
          @Override
          public void handleMessage(Message msg) {
              switch (msg.what) {
                  case MSG_FROM_SERVER:
                      String reply = msg.getData().getString("reply");
                      Log.d("Client", "Reply: " + reply);
                      break;
              }
          }
      };

      // 客户端 Messenger
      private Messenger mClientMessenger = new Messenger(mHandler);

      private ServiceConnection mConnection = new ServiceConnection() {
          @Override
          public void onServiceConnected(ComponentName name, IBinder service) {
              // ★ 获取服务端 Messenger ★
              mServiceMessenger = new Messenger(service);
              mBound = true;

              // 发送消息
              Message msg = Message.obtain(null, MSG_FROM_CLIENT);
              Bundle bundle = new Bundle();
              bundle.putString("msg", "Hello from Client");
              msg.setData(bundle);

              // ★ 设置回复 Messenger ★
              msg.replyTo = mClientMessenger;

              try {
                  mServiceMessenger.send(msg);
              } catch (RemoteException e) {
                  e.printStackTrace();
              }
          }

          @Override
          public void onServiceDisconnected(ComponentName name) {
              mServiceMessenger = null;
              mBound = false;
          }
      };
  }
```

---

## 14. ContentProvider

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ContentProvider 详解                                │
│  源码位置: frameworks/base/core/java/android/content/ContentProvider.java   │
└─────────────────────────────────────────────────────────────────────────────┘

  ContentProvider 是 Android 提供的结构化数据共享机制：

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  特点：                                                                 │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  1. 标准化接口（CRUD 操作）                                              │
  │  2. 内置权限控制                                                        │
  │  3. 支持 URI 匹配                                                       │
  │  4. 支持 Cursor 返回结果集                                              │
  │  5. 基于 Binder 实现                                                    │
  │                                                                         │
  │  适用场景：                                                             │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  - 跨应用数据共享（联系人、短信、媒体库）                                 │
  │  - 数据库共享                                                           │
  │  - 文件共享                                                             │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  核心方法：
  ─────────────────────────────────────────────────────────────────────────────

  public abstract class ContentProvider {

      // 初始化
      public abstract boolean onCreate();

      // 查询
      public abstract Cursor query(Uri uri, String[] projection,
              String selection, String[] selectionArgs, String sortOrder);

      // 插入
      public abstract Uri insert(Uri uri, ContentValues values);

      // 更新
      public abstract int update(Uri uri, ContentValues values,
              String selection, String[] selectionArgs);

      // 删除
      public abstract int delete(Uri uri, String selection,
              String[] selectionArgs);

      // 获取类型
      public abstract String getType(Uri uri);
  }


  ContentProvider 的 Binder 通信：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ContentResolver (Client)              ContentProvider (Server)         │
  │  ┌─────────────────────┐               ┌─────────────────────┐         │
  │  │                     │               │                     │         │
  │  │ query()             │               │ query()             │         │
  │  │ insert()            │  ═════════►   │ insert()            │         │
  │  │ update()            │  Binder IPC   │ update()            │         │
  │  │ delete()            │  ◄═════════   │ delete()            │         │
  │  │                     │               │                     │         │
  │  │ ContentResolver     │               │ ContentProvider     │         │
  │  │ (应用进程)          │               │ (提供者进程)        │         │
  │  └─────────────────────┘               └─────────────────────┘         │
  │                                                                         │
  │  通信方式：                                                             │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  1. 客户端通过 ContentResolver 调用                                     │
  │  2. AMS 找到目标 ContentProvider                                        │
  │  3. 通过 Binder 调用目标进程的 ContentProvider                          │
  │  4. 返回 Cursor (通过 CursorWindow 共享内存)                            │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  CursorWindow 共享内存优化：
  ─────────────────────────────────────────────────────────────────────────────

  // CursorWindow 使用共享内存传输大数据

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ContentProvider 进程                    Client 进程                    │
  │  ┌─────────────────────┐                ┌─────────────────────┐         │
  │  │                     │                │                     │         │
  │  │  查询数据库          │                │                     │         │
  │  │       │             │                │                     │         │
  │  │       ▼             │                │                     │         │
  │  │  填充 CursorWindow  │                │                     │         │
  │  │  (共享内存)         │───────────────►│  读取 CursorWindow  │         │
  │  │                     │   共享内存      │  (同一块内存)       │         │
  │  │                     │                │                     │         │
  │  └─────────────────────┘                └─────────────────────┘         │
  │                                                                         │
  │  ★ CursorWindow 使用共享内存，避免大量数据通过 Binder 拷贝 ★            │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 15. 文件共享

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         文件共享 IPC                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  适用场景：
  ─────────────────────────────────────────────────────────────────────────────
  - 低频数据持久化
  - 大文件共享
  - 简单的数据交换


  以下演示同一应用的两个进程使用同一路径；不同应用的 getExternalFilesDir 不同且受沙箱保护。跨应用需 FileProvider/ContentProvider 提供 content Uri 并授予读权限，不直接分享私有绝对路径。

  实现方式：
  ─────────────────────────────────────────────────────────────────────────────

  // 进程 A: 写入文件
  public void writeFile(String content) {
      File file = new File(getExternalFilesDir(null), "shared.txt");
      try (FileOutputStream fos = new FileOutputStream(file)) {
          fos.write(content.getBytes());
      } catch (IOException e) {
          e.printStackTrace();
      }
  }

  // 进程 B: 读取文件
  public String readFile() {
      File file = new File(getExternalFilesDir(null), "shared.txt");
      try (FileInputStream fis = new FileInputStream(file)) {
          byte[] buffer = new byte[1024];
          StringBuilder sb = new StringBuilder();
          int len;
          while ((len = fis.read(buffer)) > 0) {
              sb.append(new String(buffer, 0, len));
          }
          return sb.toString();
      } catch (IOException e) {
          e.printStackTrace();
      }
      return null;
  }


  注意事项：
  ─────────────────────────────────────────────────────────────────────────────
  1. 需要处理并发访问（使用文件锁）
  2. 实时性差（需要轮询或监听）
  3. 需要处理文件权限


  SharedPreferences 跨进程：
  ─────────────────────────────────────────────────────────────────────────────

  // ⚠️ 注意：SharedPreferences 不支持跨进程安全访问！
  // MODE_MULTI_PROCESS 自 API 23 废弃

  // 推荐使用 ContentProvider 或其他 IPC 机制
```

---

## 16. Socket IPC

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Socket IPC                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  适用场景：
  ─────────────────────────────────────────────────────────────────────────────
  - 跨设备通信
  - 实时双向通信
  - 需要跨平台兼容


  本地 Socket 只能本机 IPC；此示例仅示意连接，生产代码须用帧长度/循环读取、超时和 try-with-resources，不能假定一次 read 就是一条完整消息。

  本地 Socket 示例：
  ─────────────────────────────────────────────────────────────────────────────

  // 服务端
  public class LocalSocketServer {

      private LocalServerSocket mServerSocket;

      public void start() {
          try {
              mServerSocket = new LocalServerSocket("my.socket");

              while (true) {
                  LocalSocket client = mServerSocket.accept();

                  // 处理客户端连接
                  new Thread(() -> handleClient(client)).start();
              }
          } catch (IOException e) {
              e.printStackTrace();
          }
      }

      private void handleClient(LocalSocket client) {
          try {
              InputStream is = client.getInputStream();
              OutputStream os = client.getOutputStream();

              // 读取数据
              byte[] buffer = new byte[1024];
              int len = is.read(buffer);
              if (len < 0) return; // EOF，不可拿 -1 构造 String
              String msg = new String(buffer, 0, len);

              // 回复
              os.write("Received".getBytes());

              client.close();
          } catch (IOException e) {
              e.printStackTrace();
          }
      }
  }


  // 客户端
  public class LocalSocketClient {

      public void connect() {
          try {
              LocalSocket socket = new LocalSocket();
              socket.connect(new LocalSocketAddress("my.socket"));

              OutputStream os = socket.getOutputStream();
              InputStream is = socket.getInputStream();

              // 发送数据
              os.write("Hello".getBytes());

              // 接收回复
              byte[] buffer = new byte[1024];
              int len = is.read(buffer);
              if (len < 0) return; // 实际协议需循环读满指定帧长度
              String reply = new String(buffer, 0, len);

              socket.close();
          } catch (IOException e) {
              e.printStackTrace();
          }
      }
  }
```

---

## 17. Binder 调试技巧

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 调试技巧                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 查看 Binder 线程状态
  ─────────────────────────────────────────────────────────────────────────────

  // 查看进程的 Binder 线程
  adb shell ps -T -p <pid>  # thread 名称/状态；访问权限依设备而定


  2. 查看 Binder 统计信息
  ─────────────────────────────────────────────────────────────────────────────

  // 查看 Binder 驱动统计
  adb shell cat /d/binder/stats


  3. 查看 Binder 进程信息
  ─────────────────────────────────────────────────────────────────────────────

  // 查看所有 Binder 进程
  adb shell ls /d/binder/proc  # 再读取具体 PID 文件


  4. 查看 Binder 事务
  ─────────────────────────────────────────────────────────────────────────────

  // 开启 Binder 事务日志
  // transaction_log 是调试输出，不能通过 echo 1 当作启用开关

  // 查看事务日志
  adb shell cat /d/binder/transaction_log


  5. dumpsys 查看 Binder 状态
  ─────────────────────────────────────────────────────────────────────────────

  // 查看所有服务
  adb shell service list

  // 查看特定服务
  adb shell dumpsys activity

  // 查看 Binder 线程池状态
  adb shell dumpsys <service_name>


  6. 常见错误排查
  ─────────────────────────────────────────────────────────────────────────────

  错误: TransactionTooLargeException
  原因: payload 太大或共享接收缓冲区不足
  解决: 减少数据量或使用文件共享

  错误: DeadObjectException
  原因: 对端进程已死亡
  解决: 使用 DeathRecipient 监听并重连

  错误: SecurityException
  原因: 权限不足
  解决: 检查 AndroidManifest.xml 权限声明

  错误: RemoteException
  原因: Binder 通信失败
  解决: 检查服务端是否正常、Binder 线程是否耗尽
```

---

## 18. 总结

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 核心知识点总结                               │
└─────────────────────────────────────────────────────────────────────────────┘

  1. Binder 架构分层
  ─────────────────────────────────────────────────────────────────────────────
  - 应用层: AIDL (Stub/Proxy)
  - Framework 层: Binder/BinderProxy, Parcel
  - Native 层: BBinder/BpBinder, IPCThreadState, ProcessState
  - 内核层: Binder 驱动 (/dev/binder)


  2. 一次内存拷贝原理
  ─────────────────────────────────────────────────────────────────────────────
  - 发送方: copy_from_user() 拷贝到内核
  - 接收方: 通过 mmap 直接读取 (无需拷贝)


  3. Binder 缓冲区大小
  ─────────────────────────────────────────────────────────────────────────────
  - 普通 libbinder: 1MiB - 2 * pageSize，共享接收预算
  - ServiceManager: 当前 C++ ProcessState mmap 预算
  - 预算减去 2 * runtime page size，不能推断两个实际 guard page


  4. 线程池
  ─────────────────────────────────────────────────────────────────────────────
  - 默认驱动扩容额度 15，另有首个 PoolThread/主动 join
  - 由 BR_SPAWN_LOOPER 触发创建


  5. 安全性
  ─────────────────────────────────────────────────────────────────────────────
  - 内核级 UID/PID 验证
  - 无法伪造身份


  6. AIDL 使用
  ─────────────────────────────────────────────────────────────────────────────
  - Stub: 服务端实现
  - Proxy: 客户端调用
  - asInterface(): 判断是否同进程


  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │                        Binder 核心数据结构                               │
  │  ┌─────────────────────────────────────────────────────────────────┐   │
  │  │                                                                 │   │
  │  │  binder_proc      进程上下文 (每个进程一个)                       │   │
  │  │  binder_thread    线程上下文 (每个 Binder 线程一个)               │   │
  │  │  binder_node      Binder 实体 (服务端)                           │   │
  │  │  binder_ref       Binder 引用 (客户端 handle)                    │   │
  │  │  binder_buffer    内存缓冲区                                     │   │
  │  │  binder_transaction  事务 (一次 IPC 调用)                        │   │
  │  │                                                                 │   │
  │  └─────────────────────────────────────────────────────────────────┘   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 19. Binder 事务生命周期

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 事务完整生命周期                             │
└─────────────────────────────────────────────────────────────────────────────┘

  事务状态流转：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │   Client                                                Server          │
  │     │                                                     │             │
  │     │  1. 创建事务                                         │             │
  │     │  binder_transaction_data                            │             │
  │     │     │                                               │             │
  │     │     ▼                                               │             │
  │     │  2. 写入命令 (BC_TRANSACTION)                        │             │
  │     │     │                                               │             │
  │     │     ▼                                               │             │
  │     │  3. ioctl(BINDER_WRITE_READ)                        │             │
  │     │     │                                               │             │
  │     │     │  ══════════════════════════════════════════►  │             │
  │     │     │            Binder 驱动                         │             │
  │     │     │  - 分配 binder_buffer                          │             │
  │     │     │  - copy_from_user (一次拷贝)                   │             │
  │     │     │  - 添加到目标进程 todo 队列                    │             │
  │     │     │  - wake_up_interruptible                       │             │
  │     │     │                                               │             │
  │     │     │            4. BR_TRANSACTION ◄─────────────────│             │
  │     │     │            5. executeCommand()                 │             │
  │     │     │            6. onTransact() 执行业务            │             │
  │     │     │            7. 写入回复                         │             │
  │     │     │            8. BC_REPLY                         │             │
  │     │     │  ══════════════════════════════════════════►  │             │
  │     │     │            Binder 驱动                         │             │
  │     │     │  - 释放 buffer                                │             │
  │     │     │  - 唤醒等待线程                               │             │
  │     │     │                                               │             │
  │     │  9. BR_REPLY ◄──────────────────────────────────────│             │
  │     │     │                                               │             │
  │     │     ▼                                               │             │
  │     │  10. 解析返回值                                     │             │
  │     │     │                                               │             │
  │     │     ▼                                               │             │
  │     │  11. 事务完成                                       │             │
  │     │                                                     │             │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


    buffer 生命周期独立于“业务调用返回”：接收 Parcel 释放后 freeBuffer 写 BC_FREE_BUFFER。
    事务状态是通过工作队列、同步事务栈、reply 和 buffer 所有权共同表达，
    驱动没有旧文中 TRANSACTION_STATE_PENDING/IN_PROGRESS/COMPLETE 的统一枚举。
    嵌套链见第 5 章 binder_transaction.from_parent / to_parent。
```

### 19.1 同步事务 vs 异步事务 (oneway)

| 模式 | 发送方等待 | 服务端结果 | 顺序 |
|------|------------|------------|------|
| 同步 | 提交后等 BR_REPLY，同时可执行嵌套入站命令 | reply 中返回值/异常 | 单线程调用的先后关系，不保证不同线程全局顺序 |
| 远程 oneway | 等驱动提交完成，不等业务回复 | 无业务 reply；提交仍可能失败 | 同一 node 的异步事务串行，同一发送线程有序 |
| 本地 AIDL 直调 | 普通函数调用 | 普通调用/异常 | 不通过驱动，oneway 不自动异步化 |

```cpp
// 核心差异在等待目标，不是 oneway 只写 mOut 然后不 flush。
if ((flags & TF_ONE_WAY) == 0) {
    Parcel fakeReply;
    err = waitForResponse(reply ? reply : &fakeReply);
} else {
    err = waitForResponse(nullptr, nullptr);
}
```

oneway 适合通知/事件、无返回值且允许协议级异步处理的请求。它不适合“必须确认已经执行完成”的调用；同一 node 的有序通知是允许的，因此原文“有顺序依赖一律不适合 oneway”过度绝对。跨 node 或同步/异步混用则需要业务序号/确认机制，不能推导全局顺序。

`BR_TRANSACTION_COMPLETE` 不意味着目标处理完成。远端进程冻结、死亡、异步缓冲区不足等仍会影响传输，不能把“无返回值”宣传成永不阻塞、永不失败。

---

## 20. Binder 死锁问题

同步 Binder 等待不是只等条件变量：`waitForResponse()` 的 default 分支调用 `executeCommand()`，驱动还利用同步事务栈定向嵌套回调。因此 A -> B -> C -> A 不因“同一个线程正在等 B”就必死锁；同一 Binder 线程等待对端 reply 也不需要另一个空闲池线程接收回复。

真正要分析的是**等待图和业务锁**：

```text
A:t1 持有锁 L，调用 B
B 另起任务，调用 A 的对象
A:t2 处理回调，试图获取 L -> 等 t1
B 等这个任务完成 -> 等 A:t2
A:t1 等 B 返回
形成 t1 -> B -> t2 -> L -> t1 的环
```

若同步事务栈回入同一个 t1，Java synchronized 的可重入性可能避免此特定锁等待，但会让对象在尚未完成的外层状态中被重入，破坏业务不变量。native 非递归锁、跨线程派发、应用层 future.get/latch.await 则可能形成实际死锁。

```java
// 用状态快照避免持业务锁跨 IPC；返回后再次验证状态是否仍可提交。
Request snapshot;
long expectedGeneration;
synchronized (lock) {
    snapshot = makeSnapshot();
    expectedGeneration = generation;
}
Response result = remote.process(snapshot); // 不持 lock
synchronized (lock) {
    if (generation == expectedGeneration) apply(result);
    else discardStale(result);
}
```

异步工作队列/oneway 只能消除协议中某些等待边，不能修复“持锁等回调”的整个等待环。增加线程数也不能解决真正的循环等待，SDK 没有通过 ServiceManager.getService("activity") 调整本进程池的公开接口。

排查时抓取所有相关进程的 Binder/业务线程栈与 Perfetto binder_transaction/binder_transaction_received 调度事件，标出每把锁和每个 Future 的拥有者；ANR 文件位置/读取权限依系统配置。StrictMode.detectCustomSlowCalls 需要业务显式 noteSlowCall，不能自动检测所有 Binder 死锁。

---

## 21. Binder 对象传递

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 对象传递详解                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  IBinder 跨进程传递原理：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │   进程 A (Server)                      进程 B (Client)                  │
  │  ┌─────────────────┐                  ┌─────────────────┐               │
  │  │                 │                  │                 │               │
  │  │  binder_node    │                  │  binder_ref     │               │
  │  │  (Binder 实体)   │                  │  (Binder 引用)  │               │
  │  │       │         │                  │       │         │               │
  │  │       │         │                  │       │         │               │
  │  │  BBinder        │                  │  BpBinder       │               │
  │  │  (Native 层)    │                  │  (Native 层)    │               │
  │  │       │         │                  │       │         │               │
  │  │       │         │                  │       │         │               │
  │  │  Binder         │                  │  BinderProxy    │               │
  │  │  (Java 层)      │                  │  (Java 层)      │               │
  │  │                 │                  │                 │               │
  │  └─────────────────┘                  └─────────────────┘               │
  │                                                                         │
  │  传递过程：                                                             │
  │  1. 进程 A 将 Binder 写入 Parcel                                       │
  │  2. Binder 驱动检测到 Binder 对象                                      │
  │  3. 在目标进程创建 binder_ref                                          │
  │  4. 目标进程收到 BpBinder/BinderProxy                                  │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  Parcel 写入/读取 IBinder：
  ─────────────────────────────────────────────────────────────────────────────

  // Java 层
  // 写入
  Parcel parcel = Parcel.obtain();
  parcel.writeStrongBinder(binder);

  // 读取
  IBinder binder = parcel.readStrongBinder();


  // Native 层
  // 写入
  Parcel parcel;
  parcel.writeStrongBinder(binder);

  // 读取
  sp<IBinder> binder = parcel.readStrongBinder();


    源码算法（Parcel.cpp: flattenBinder / unflattenBinder，kernel 分支）：

    写入：
    - 本地 BBinder：obj.hdr.type = BINDER_TYPE_BINDER，binder 字段保存 weakrefs 标识，
      cookie 保存 local Binder 指针；同时写入接受 FD / SID / 调度相关 flags。
    - 远程 BpBinder：obj.hdr.type = BINDER_TYPE_HANDLE，handle 来自 binderHandle()，
      不是 getExtension()（后者表示 Binder 扩展对象）。
    - null：BINDER_TYPE_BINDER + 零 binder/cookie。
    - writeObject 写入对象和 offsets 表，finishFlattenBinder 维护稳定性信息。

    驱动：
    - 根据发送方的 node/ref 找到实体，转换为接收方的 handle；
    - 如果接收方就是实体拥有者，则还原为本地 ptr/cookie。

    读取：
    - BINDER_TYPE_BINDER：按 cookie 恢复本地 sp<IBinder>；
    - BINDER_TYPE_HANDLE：ProcessState::getStrongProxyForHandle() 获取/复用代理；
    - finishUnflattenBinder 处理附加元数据。

    老式 flatten_binder(proc, binder, out) 全局函数不是当前函数签名。
    不能把 RPC Binder 经 kernel Binder 通道直接发送，源码检查并返回 INVALID_OPERATION。
```

### 21.1 文件描述符传递

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         文件描述符传递详解                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  原理：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │   进程 A                                进程 B                           │
  │  ┌─────────────────┐                  ┌─────────────────┐               │
  │  │                 │                  │                 │               │
  │  │  fd = 10        │                  │  fd = 25        │               │
  │  │  (指向文件 X)    │  ════════════════│  (指向同一文件 X)│               │
  │  │                 │  Binder 传递 FD   │                 │               │
  │  │                 │                  │                 │               │
  │  └─────────────────┘                  └─────────────────┘               │
  │                                                                         │
  │  传递过程：                                                             │
  │  1. 进程 A 将 fd 写入 Parcel                                           │
  │  2. Binder 驱动在目标进程分配新的 fd                                    │
  │  3. 新 fd 指向同一个 file 对象                                          │
  │  4. 进程 B 收到新的 fd                                                  │
  │                                                                         │
  │  ★ 注意：两个进程中的 fd 编号不同，但指向同一个文件 ★                    │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  代码示例：
  ─────────────────────────────────────────────────────────────────────────────

  // 发送方
  public void sendFileDescriptor(ParcelFileDescriptor pfd) {
      Parcel parcel = Parcel.obtain();
      parcel.writeFileDescriptor(pfd.getFileDescriptor());
      // 发送 parcel...
  }


  // 接收方
  public ParcelFileDescriptor receiveFileDescriptor(Parcel parcel) {
      ParcelFileDescriptor pfd = parcel.readFileDescriptor(); // 接收者负责 close
      return pfd;
  }


  Native 层：
  ─────────────────────────────────────────────────────────────────────────────

  // 发送
  int fd = open("/data/data/com.example/shared_file", O_RDWR);
  Parcel parcel;
  parcel.writeFileDescriptor(fd);

  // 接收
  int new_fd = parcel.readFileDescriptor(); // borrowed，Parcel 存活期内有效；延长寿命需 dup
  // new_fd 与发送方的 fd 不同，但指向同一个文件


  使用场景：
  ─────────────────────────────────────────────────────────────────────────────

  1. 共享内存（API 27+ 使用 SharedMemory，下面旧 MemoryFile 反射只作历史说明）
     ─────────────────────────────────────────────────────────────────────────
     // 创建共享内存
     MemoryFile memoryFile = new MemoryFile("shared", 1024);

     // 获取文件描述符
     Method method = MemoryFile.class.getDeclaredMethod("getFileDescriptor");
     FileDescriptor fd = (FileDescriptor) method.invoke(memoryFile);

     // 传递给其他进程
     ParcelFileDescriptor pfd = ParcelFileDescriptor.dup(fd);

  2. Socket 传递
     ─────────────────────────────────────────────────────────────────────────
     // 传递 LocalSocket 的文件描述符

  3. 硬件设备访问
     ─────────────────────────────────────────────────────────────────────────
     // 传递设备文件描述符


  注意事项：
  ─────────────────────────────────────────────────────────────────────────────

  1. 文件描述符在目标进程中是新的编号
  2. 发送后，发送方仍持有原始 fd
  3. 需要正确关闭 fd，避免泄漏
  4. 需要处理权限问题
```

---

## 22. Binder 调用链追踪

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 调用链追踪                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 使用 Systrace
  ─────────────────────────────────────────────────────────────────────────────

  // 采集 Systrace
  // 执行 Binder 调用
  $ python $ANDROID_SDK/platform-tools/systrace/systrace.py \
      --app=com.example \
      binder_driver \
      binder_lock \
      freq \
      sched \
      -o trace.html


  2. 使用 Perfetto
  ─────────────────────────────────────────────────────────────────────────────

  // 采集 trace
  $ adb shell perfetto \
      -c - --txt \
      -o /data/misc/perfetto-traces/trace \
      <<EOF

  buffers: {
      size_kb: 102400
      fill_policy: RING_BUFFER
  }

  data_sources: {
      config {
          name: "linux.ftrace"
          ftrace_config {
            ftrace_events: "binder/binder_transaction"
            ftrace_events: "binder/binder_transaction_received"
            ftrace_events: "sched/sched_switch"
            ftrace_events: "sched/sched_waking"
          }
          target_buffer: 0
      }
  }

  duration_ms: 10000
  EOF

  // 拉取 trace 文件
  $ adb pull /data/misc/perfetto-traces/trace

  // 在 https://ui.perfetto.dev/ 打开分析


  3. 添加日志追踪
  ─────────────────────────────────────────────────────────────────────────────

  // 自定义 Binder 追踪类
  public class BinderTrace {

      private static final String TAG = "BinderTrace";

      public static void logBinderCall(String method, long startTime) {
          long duration = SystemClock.elapsedRealtime() - startTime;
          Log.d(TAG, String.format("[%s] duration=%dms, thread=%s",
                  method, duration, Thread.currentThread().getName()));
      }

      public static void logBinderCall(String method, String target,
                                        long startTime, boolean success) {
          long duration = SystemClock.elapsedRealtime() - startTime;
          Log.d(TAG, String.format("[%s] target=%s, duration=%dms, success=%b, thread=%s",
                  method, target, duration, success,
                  Thread.currentThread().getName()));
      }
  }

  // 使用
  public int getData(int id) throws RemoteException {
      long startTime = SystemClock.elapsedRealtime();
      try {
          int result = mRemote.getData(id);
          BinderTrace.logBinderCall("getData", "RemoteService", startTime, true);
          return result;
      } catch (RemoteException e) {
          BinderTrace.logBinderCall("getData", "RemoteService", startTime, false);
          throw e;
      }
  }


  4. 使用 AOP 追踪
  ─────────────────────────────────────────────────────────────────────────────

  // 使用 AspectJ 追踪 Binder 调用
  @Aspect
  public class BinderTraceAspect {

      private static final String TAG = "BinderTrace";

      @Around("call(* android.os.IBinder.transact(..))") // 仅织入可控调用点，不能改写 boot classpath 实现
      public Object traceBinderCall(ProceedingJoinPoint joinPoint) throws Throwable {
          long startTime = SystemClock.elapsedRealtime();
          Object result = null;
          Throwable error = null;

          try {
              result = joinPoint.proceed();
          } catch (Throwable t) {
              error = t;
              throw t;
          } finally {
              long duration = SystemClock.elapsedRealtime() - startTime;
              Object[] args = joinPoint.getArgs();
              int code = (int) args[0];

              Log.d(TAG, String.format(
                  "transact: code=%d, duration=%dms, error=%s",
                  code, duration, error != null ? error.getMessage() : "none"));
          }

          return result;
      }
  }


  5. 使用 Debug.startMethodTracing
  ─────────────────────────────────────────────────────────────────────────────

  // 开始追踪
  Debug.startMethodTracing("binder_trace");

  // 执行 Binder 调用
  service.getData(1);

  // 停止追踪
  Debug.stopMethodTracing();

  // 分析 trace 文件
  // 使用 Android Studio 的 CPU Profiler 打开
  // 文件位置: /sdcard/Android/data/com.example/files/binder_trace.trace


  6. Binder 调用耗时统计
  ─────────────────────────────────────────────────────────────────────────────

  public class BinderCallMonitor {

      private static final ConcurrentHashMap<String, CallStats> sStats =
          new ConcurrentHashMap<>();

      public static class CallStats {
          public long totalCount;
          public long totalTime;
          public long maxTime;
          public long errorCount;
      }

      public static void recordCall(String method, long duration, boolean error) {
          CallStats stats = sStats.computeIfAbsent(method, k -> new CallStats());

          synchronized (stats) {
              stats.totalCount++;
              stats.totalTime += duration;
              stats.maxTime = Math.max(stats.maxTime, duration);
              if (error) {
                  stats.errorCount++;
              }
          }
      }

      public static void printStats() {
          for (Map.Entry<String, CallStats> entry : sStats.entrySet()) {
              CallStats stats = entry.getValue();
              synchronized (stats) {
              if (stats.totalCount == 0) continue;
              Log.d("BinderMonitor", String.format(
                  "%s: count=%d, avg=%dms, max=%dms, errors=%d",
                  entry.getKey(),
                  stats.totalCount,
                  stats.totalTime / stats.totalCount,
                  stats.maxTime,
                  stats.errorCount
              ));
              }
          }
      }
  }
```

---

## 23. Binder 高频面试题

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 高频面试题                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  Q1: Binder 为什么只需要一次内存拷贝？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  1. 发送方通过 copy_from_user() 将数据拷贝到内核缓冲区
  2. 接收方通过 mmap 将内核缓冲区映射到用户空间
  3. 接收方直接读取映射的内存，无需再次拷贝

  对比传统 IPC：
  - Socket/管道: 需要 2 次拷贝（用户→内核→用户）
  - 共享内存: 0 次拷贝，但需要复杂的同步机制


  Q2: Binder 如何保证安全性？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  1. 内核级 UID/PID 验证
     - Binder 驱动在内核中自动填充发送方的 UID/PID
     - 无法在用户空间伪造

  2. SELinux 策略
     - 可以限制哪些进程可以访问哪些服务

  3. 权限检查
     - 服务端可以检查调用方的 UID/GID
     - 可以通过 checkCallingPermission() 检查权限


  Q3: Binder 传输数据大小限制是多少？为什么？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  - 普通 libbinder: 1MiB - 2 * pageSize，在途事务共享，非单笔保证
  - ServiceManager: 当前 C++ ProcessState mmap 预算

  原因:
  1. Binder 使用 mmap 映射内存，需要预留空间
  2. 减去的是运行时页大小的两倍，4KiB 页下才是 8KiB
  3. 异步事务占用一半空间（约 512K）


  Q4: Binder 线程池有多少个线程？如何工作的？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  - 默认扩容额度 15，另有首个 PoolThread/主动 join
  - 主动加入/首个池线程: BC_ENTER_LOOPER（不是 UI main）
  - 工作线程: BC_REGISTER_LOOPER
  - 由 BR_SPAWN_LOOPER 触发创建新线程
  - 线程阻塞在 ioctl() 等待事务


  Q5: AIDL 生成的 Stub 和 Proxy 分别是什么？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  - Stub: 服务端实现，继承自 Binder，处理 onTransact()
  - Proxy: 客户端代理，持有 BinderProxy，调用 transact()
  - asInterface(): 判断是否同进程，同进程返回 Stub，跨进程返回 Proxy


  Q6: oneway 关键字的作用是什么？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  1. 异步调用，提交完成后返回，不等待业务 reply
  2. 不阻塞等待服务端返回
  3. 不能有返回值
  4. 多个 oneway 调用会排队执行
  5. 适用于通知、日志上报等不需要返回的场景


  Q7: 如何避免 Binder 死锁？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  1. 避免嵌套 Binder 调用
  2. 在新线程中执行耗时操作
  3. 使用 oneway 异步调用
  4. 增加 Binder 线程数（不推荐）
  5. 使用回调代替同步返回


  Q8: ServiceManager 的作用是什么？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  1. 系统服务的注册中心（类似 DNS）
  2. 管理所有系统服务的 Binder 引用
  3. 提供 addService() 注册服务
  4. 提供 getService() 查询服务
  5. handle = 0 是 ServiceManager 的固定句柄


  Q9: Binder 与其他 IPC 方式的对比？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  ┌──────────────┬─────────┬─────────┬─────────┬─────────┐
  │     方式     │  拷贝   │  安全性  │  易用性  │  性能   │
  ├──────────────┼─────────┼─────────┼─────────┼─────────┤
  │ Binder       │   1次   │   高    │   高    │   高    │
  │ Socket       │   2次   │   中    │   中    │   中    │
  │ 共享内存     │   0次   │   低    │   低    │   最高  │
  │ 管道         │   2次   │   中    │   中    │   中    │
  └──────────────┴─────────┴─────────┴─────────┴─────────┘


  Q10: Intent 传参为什么有限制？如何解决？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  限制原因:
  - Intent 通过 Binder 传递
  - Binder 缓冲区大小限制约 1M
  - 系统还要预留一部分空间

  解决方案:
  1. 使用文件共享
  2. 使用 ContentProvider + Uri
  3. EventBus / LiveData 仅用于同进程内
  4. 单例只在同进程共享，不能替代跨进程数据传输
  5. 跨进程大数据可传受控 Uri/FD


  Q11: 解释 BBinder 和 BpBinder 的区别？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  BBinder (Binder 本地对象):
  - 服务端持有
  - 继承自 IBinder
  - 实现 onTransact() 处理请求
  - 对应内核中的 binder_node

  BpBinder (Binder 代理对象):
  - 客户端持有
  - 持有 handle (句柄)
  - 调用 transact() 发送请求
  - 对应内核中的 binder_ref


  Q12: Parcel 是什么？为什么用 Parcel 而不是 Serializable？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  Parcel:
  - Android 专用序列化容器
  - Java 包装 native Parcel 缓冲区，不是基于 java.nio.ByteBuffer
  - 读写效率高
  - 用于 Binder IPC

  对比 Serializable:
  - Serializable 使用反射，效率低
  - Serializable 产生大量临时对象
  - Parcel 针对 IPC 编码，性能与对象/字段和负载相关，没有统一 10 倍保证
  - Parcel 不能用于持久化存储（版本兼容问题）


  Q13: Binder 驱动在内核中做了什么？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  1. 打开 /dev/binder 设备
  2. mmap 内存映射
  3. 处理 ioctl 命令 (BINDER_WRITE_READ)
  4. 管理 binder_proc、binder_thread、binder_node、binder_ref
  5. 实现 copy_from_user 一次拷贝
  6. 在目标进程的 todo 队列中添加事务
  7. 唤醒目标进程


  Q14: 如何监听 Binder 服务端死亡？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  // 使用 DeathRecipient
  IBinder.DeathRecipient deathRecipient = new IBinder.DeathRecipient() {
      @Override
      public void binderDied() {
          // 服务端死亡回调
          // 注意：在 Binder 线程中执行
      }
  };

  // 注册监听
  binder.linkToDeath(deathRecipient, 0);

  // 解除监听
  binder.unlinkToDeath(deathRecipient, 0);


  Q15: AIDL 支持哪些数据类型？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  1. AIDL 标量: byte, int, long, float, double, boolean, char
  2. String 和 CharSequence
  3. List (元素必须是支持的类型)
  4. Map (键值必须是支持的类型)
  5. Parcelable 实现类
  6. 其他 AIDL 接口


  Q16: Binder 通信是全双工还是半双工？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  - Binder 是支持请求/回复与反向回调的事务式 IPC，不宜直接套用半双工标签
  - 同步事务包含请求与回复，双方还可并发发起其他事务
  - 需要双向通信时，需要两次事务
  - 或者使用两个 Binder（各自作为 Client 和 Server）


  Q17: 解释 TransactionTooLargeException 如何避免？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  原因:
  - Intent 传递数据超过 Binder 缓冲区限制

  避免:
  1. 不要传递大图片、大文件
  2. 只传递必要的数据
  3. 使用 Parcelable 代替 Serializable
  4. 大数据使用文件或 ContentProvider
  5. 图片使用 Uri 而不是 Bitmap


  Q18: Binder 如何实现跨进程传递文件描述符？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  1. 使用 Parcel.writeFileDescriptor() 写入
  2. Binder 驱动检测到文件描述符类型
  3. 在目标进程中分配新的 fd
  4. 新 fd 指向同一个 file 对象
  5. 使用 Parcel.readFileDescriptor() 读取

  应用场景:
  - 共享内存 (MemoryFile)
  - Socket 传递
  - 硬件设备访问


  Q19: 什么是 Binder 线程池耗尽？如何避免？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  原因:
  - 当前进程的所有可用 Binder 工作线程都被阻塞
  - 无法处理新的 Binder 请求

  避免方法:
  1. 不要在 Binder 方法中执行耗时操作
  2. 耗时操作放到新线程中
  3. 使用异步方式 (oneway 或 callback)
  4. 合理设计 API，避免嵌套调用


  Q20: 简述 Binder 通信的完整流程？
  ─────────────────────────────────────────────────────────────────────────────

  A:
  Client 端:
  1. 调用 Proxy 方法
  2. Parcel 写入参数
  3. BinderProxy.transact()
  4. JNI 调用 Native 层
  5. BpBinder.transact()
  6. IPCThreadState.transact()
  7. writeTransactionData()
  8. ioctl(BINDER_WRITE_READ)

  内核层:
  9. binder_ioctl()
  10. binder_transaction()
  11. copy_from_user()
  12. 添加到目标进程 todo 队列
  13. wake_up_interruptible()

  Server 端:
  14. IPCThreadState 阻塞返回
  15. executeCommand()
  16. BBinder.transact()
  17. JNI 回调 Java
  18. Binder.execTransact()
  19. Stub.onTransact()
  20. 执行实际方法
  21. 写入返回值

  返回:
  22. 同样流程返回给 Client


  面试高频知识点总结：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  必须掌握：                                                             │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  1. Binder 是什么，为什么选择 Binder                                    │
  │  2. 一次内存拷贝原理 (mmap)                                             │
  │  3. Binder 接收预算与在途事务共享限制                                     │
  │  4. AIDL 使用 (Stub/Proxy/asInterface)                                  │
  │  5. Binder 线程池（默认扩容额度与主动加入线程分开计算）                                           │
  │  6. oneway 关键字                                                       │
  │  7. Binder 死锁问题                                                     │
  │                                                                         │
  │  进阶掌握：                                                             │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  1. Binder 驱动核心数据结构                                             │
  │  2. ServiceManager 原理                                                 │
  │  3. Binder 对象传递 (IBinder, 文件描述符)                               │
  │  4. Binder 调用链追踪                                                   │
  │  5. TransactionTooLargeException 处理                                   │
  │  6. Binder 与其他 IPC 方式对比                                          │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 24. Binder 架构图总结

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Binder 完整架构图                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                          应用层 (Application)                            │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │   Activity              Service              ContentProvider      │  │
  │  │       │                    │                        │              │  │
  │  │       └────────────────────┼────────────────────────┘              │  │
  │  │                            │                                       │  │
  │  │                            ▼                                       │  │
  │  │                    ┌───────────────┐                               │  │
  │  │                    │    AIDL 接口   │                               │  │
  │  │                    │  (Stub/Proxy) │                               │  │
  │  │                    └───────────────┘                               │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       Framework 层 (Java)                                │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
  │  │  │  IBinder     │  │  Binder      │  │ BinderProxy  │            │  │
  │  │  │  (接口)      │  │  (服务端)    │  │  (客户端)    │            │  │
  │  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
  │  │         │                  │                  │                   │  │
  │  │         └──────────────────┼──────────────────┘                   │  │
  │  │                            │                                       │  │
  │  │                            ▼                                       │  │
  │  │                   ┌─────────────────┐                              │  │
  │  │                   │  Parcel (序列化) │                              │  │
  │  │                   └─────────────────┘                              │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (JNI)
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       Native 层 (C++)                                    │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │  │
  │  │  │  BBinder     │  │  BpBinder    │  │ IPCThreadState│            │  │
  │  │  │  (服务端)    │  │  (客户端)    │  │  (线程状态)   │            │  │
  │  │  └──────────────┘  └──────────────┘  └──────────────┘            │  │
  │  │         │                  │                  │                   │  │
  │  │         └──────────────────┼──────────────────┘                   │  │
  │  │                            │                                       │  │
  │  │                            ▼                                       │  │
  │  │                   ┌─────────────────┐                              │  │
  │  │                   │  ProcessState   │                              │  │
  │  │                   │  (进程状态)     │                              │  │
  │  │                   └─────────────────┘                              │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (ioctl)
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       内核层 (Kernel)                                     │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │                    ┌─────────────────────┐                        │  │
  │  │                    │    Binder 驱动      │                        │  │
  │  │                    │   /dev/binder      │                        │  │
  │  │                    │                    │                        │  │
  │  │                    │  - binder_proc     │  (进程上下文)           │  │
  │  │                    │  - binder_thread   │  (线程上下文)           │  │
  │  │                    │  - binder_node     │  (Binder 实体)          │  │
  │  │                    │  - binder_ref      │  (Binder 引用)          │  │
  │  │                    │  - binder_buffer   │  (内存缓冲区)           │  │
  │  │                    │                    │                        │  │
  │  │                    └─────────────────────┘                        │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

*Generated by OpenClaw*



## 固定版本源码索引

本文平台实现基线为 `android-17.0.0_r1`。下列函数用于定位正文分析；代码标为“节选”时省略无关监控，标为“示意”时不是源码逐字复制。

- [ProcessState](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/binder/ProcessState.cpp)：`ProcessState; startThreadPool; getStrongProxyForHandle`。
- [IPCThreadState](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/binder/IPCThreadState.cpp)：`transact; waitForResponse; executeCommand; freeBuffer`。
- [Parcel](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/binder/Parcel.cpp)：`flattenBinder; unflattenBinder`。
- [JNI](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/jni/android_util_Binder.cpp)：`JavaBBinder::onTransact; android_os_BinderProxy_transact; javaObjectForIBinder`。
- [Binder](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/Binder.java)：`execTransact; execTransactInternal; getCallingUid; getCallingPid`。
- [servicemanager](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/cmds/servicemanager/main.cpp)：`main; BinderCallback`。
- [回调表](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/os/RemoteCallbackList.java)：`register; unregister; beginBroadcast; finishBroadcast`。
- [驱动独立 commit](https://android.googlesource.com/kernel/common/+/d768b2f486b5e909eb5e489b83059400c3cb2799/drivers/android/binder.c)：`binder_transaction; binder_thread_read; binder_mmap`。
