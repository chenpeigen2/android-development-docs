# Android 事件分发机制完全指南

> 源码版本：AOSP Android 17（API 37），`android-17.0.0_r1`。


> 作者：OpenClaw | 初稿日期：2026-03-08

> AOSP 17 源码基线：`android-17.0.0_r1` 的 `frameworks/base/core/java/android/view/Window.java`，用于说明 Window 参数、Insets 与 ViewRootImpl 之间的边界。

---

## 目录

- [1. 概述](#1-概述)
- [2. 整体架构流程图](#2-整体架构流程图)
  - [2.1 完整架构图](#21-完整架构图)
- [3. 内核层 (Linux Kernel)](#3-内核层-linux-kernel)
  - [3.1 触摸屏中断流程](#31-触摸屏中断流程)
  - [3.2 关键数据结构](#32-关键数据结构)
- [4. Native 层](#4-native-层)
  - [4.1 InputReader](#41-inputreader)
  - [4.2 InputDispatcher](#42-inputdispatcher)
  - [4.3 Socket 通信](#43-socket-通信)
- [5. Framework 层 - Input 子系统](#5-framework-层---input-子系统)
  - [5.1 InputReader 流程](#51-inputreader-流程)
  - [5.2 InputDispatcher 分发](#52-inputdispatcher-分发)
- [6. Framework 层 - WindowManagerService](#6-framework-层---windowmanagerservice)
  - [6.1 WMS 角色](#61-wms-角色)
  - [6.2 Input 事件路由](#62-input-事件路由)
- [7. App层 - ViewRootImpl](#7-app层---viewrootimpl)
  - [7.1 ViewRootImpl 角色](#71-viewrootimpl-角色)
  - [7.2 Input 事件接收](#72-input-事件接收)
- [8. App层 - Activity](#8-app层---activity)
  - [8.1 Activity 分发入口](#81-activity-分发入口)
- [9. App层 - ViewGroup](#9-app层---viewgroup)
  - [9.1 分发入口](#91-分发入口)
  - [9.2 命中顺序和坐标变换](#92-命中顺序和坐标变换)
  - [9.3 中途拦截与多指](#93-中途拦截与多指)
  - [9.4 TouchDelegate 与普通子项的优先关系](#94-touchdelegate-与普通子项的优先关系)
  - [9.5 建议的验证序列](#95-建议的验证序列)
- [10. App层 - View](#10-app层---view)
  - [10.1 View 事件处理](#101-view-事件处理)
  - [10.2 View 事件处理流程图](#102-view-事件处理流程图)
- [11. 完整流程图汇总](#11-完整流程图汇总)
  - [11.1 从内核到 View 的完整链路](#111-从内核到-view-的完整链路)
- [12. 核心方法详解](#12-核心方法详解)
  - [12.1 方法对比表](#121-方法对比表)
  - [12.2 事件消费优先级](#122-事件消费优先级)
- [13. 事件序列与状态管理](#13-事件序列与状态管理)
  - [13.1 ACTION_DOWN 的特殊性](#131-action_down-的特殊性)
  - [13.2 事件序列图](#132-事件序列图)
- [14. 典型场景分析](#14-典型场景分析)
  - [场景一：子 View 处理事件](#场景一子-view-处理事件)
  - [场景二：ViewGroup 拦截事件](#场景二viewgroup-拦截事件)
- [15. 滑动冲突解决](#15-滑动冲突解决)
  - [15.1 外部拦截法](#151-外部拦截法)
  - [15.2 内部拦截法](#152-内部拦截法)
- [16. 进阶知识点](#16-进阶知识点)
  - [16.1 多指触控](#161-多指触控)
  - [16.2 TouchDelegate 扩大点击区域](#162-touchdelegate-扩大点击区域)
  - [16.3 异步事件处理](#163-异步事件处理)

---

## 1. 概述

Android 事件分发是一个**从硬件到 App** 的完整链路，涉及多个层次：

```text
硬件(触摸屏) → Linux内核 → Native层 → Framework层 → App层
```

理解这一机制对于：
- 解决滑动冲突
- 自定义 View 实现复杂交互
- 优化触摸响应性能
- 理解 Android 系统架构

至关重要。

---

## 2. 整体架构流程图

### 2.1 完整架构图

```text
流程示意（普通触摸；省略策略过滤、输入监视、IME 和无障碍分支）：
Input Driver -> /dev/input/eventX -> EventHub
  -> InputReader / InputDevice / mapper -> NotifyArgs
  -> InputDispatcher -> InputChannel（socketpair）
  -> App WindowInputEventReceiver -> ViewRootImpl 输入阶段链
  -> 根 View 的 dispatchPointerEvent -> 触摸 dispatchTouchEvent
```

窗口系统更新路由所需的窗口/焦点信息，但常规触摸数据不先交给 WMS 再由 Java 转发。图中的 native reader/dispatcher 是同一输入流程，不应再复制为一套额外“Framework 层”线程。依据：[InputReader.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/reader/InputReader.cpp)、[InputDispatcher.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp)、[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)。

## 3. 内核层 (Linux Kernel)

### 3.1 触摸屏中断流程

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                         触摸屏产生中断                                    │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      Input Driver (evdev.c)                              │
│                                                                          │
│  1. 中断处理函数: input_interrupt()                                    │
│  2. 读取原始数据: input_event()                                         │
│  3. 填充 input_event 结构体:                                           │
│     - struct timeval time;    // 时间戳                                  │
│     - __u16 type;             // 事件类型 (EV_ABS, EV_KEY)              │
│     - __u16 code;             // 事件码 (ABS_X, ABS_Y, BTN_TOUCH)       │
│     - __s32 value;            // 事件值                                  │
│  4. 写入 /dev/input/eventX 设备节点                                     │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │ /dev/input/event0-7
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        /dev/input/eventX                                 │
│                   (字符设备，循环缓冲区)                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 关键数据结构

```c
// 内核层 input_event 结构
struct input_event {
    struct timeval time;    // 时间戳
    __u16 type;            // 事件类型
    __u16 code;            // 事件码
    __s32 value;           // 事件值
};

// 常用事件类型
#define EV_SYN      0x00   // 同步事件
#define EV_KEY      0x01   // 按键事件
#define EV_REL      0x02   // 相对坐标(鼠标)
#define EV_ABS      0x03   // 绝对坐标(触摸屏)

// 触摸相关事件码
#define ABS_X       0x00    // X 坐标
#define ABS_Y       0x01    // Y 坐标
#define ABS_MT_POSITION_X  0x03a  // 多点触控 X
#define ABS_MT_POSITION_Y  0x03b  // 多点触控 Y
#define ABS_MT_TRACKING_ID 0x039  // 触控点 ID
#define BTN_TOUCH  0x14a   // 触摸按下
```

---

## 4. Native 层

### 4.1 InputReader

固定路径是 `frameworks/native/services/inputflinger/reader/InputReader.cpp`。原文将所有 EV_ABS/EV_KEY 在 InputReader 中直接转换为 MotionEvent 的实现不准确：它按设备批次处理，经 InputDevice/mapper 转成通知参数。

```text
伪代码（Android 17 主干，省略设备增删、超时和配置变化）：
loopOnce -> EventHub.getEvents
  -> processEventsLocked -> processEventsForDeviceLocked
  -> InputDevice.process -> 设备 mapper 输出 NotifyArgs
退出 reader 锁后：逐项 mNextListener.notify(args)
```

本 tag 使用待发送 NotifyArgs 集合和 listener 链，不能把旧 `mQueuedListener->flush()` 当当前逐字实现。依据：[InputReader.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/reader/InputReader.cpp)。

### 4.2 InputDispatcher

固定路径是 `frameworks/native/services/inputflinger/dispatcher/InputDispatcher.cpp`。`notifyMotion(const NotifyMotionArgs&)` 接受通知并安排入队；目标选择、分发及完成确认有后续流程，**正常物理触摸不会调用 injectInputEvent 来发送给 App**。

```text
伪代码（省略策略、过滤、丢弃、超时及多窗口分支）：
notifyMotion -> 验证/构造 MotionEntry -> inbound queue
  -> dispatchMotionLocked -> 选择输入窗口目标
  -> 连接的 outbound queue -> startDispatchCycleLocked
  -> InputPublisher.publishMotionEvent -> InputChannel
App 完成处理 -> 完成消息回到 dispatcher，推进等待状态
```

依据：[InputDispatcher.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp)。

### 4.3 Socket 通信

InputChannel 使用 `socketpair(AF_UNIX, SOCK_SEQPACKET, ...)` 创建成对端点，**不是一个固定命名的 `/dev/socket/input_channel` 服务端地址**。Binder 用于控制面和传递句柄等，不负责逐个触摸事件的常规传输。依据：[InputTransport.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/libs/input/InputTransport.cpp)。

## 5. Framework 层 - Input 子系统

### 5.1 InputReader 流程

```text
职责示意（非逐字源码）：
设备事件 -> EventHub -> InputReader / InputDevice / InputMapper
  -> NotifyArgs -> listener 链 -> InputDispatcher
```

这里仍是 native C++ 流程，不存在本章原来示例中的 `InputDispatcher.java`。Android Java 服务承担策略和系统集成，不应把 native 算法伪装成 Java 源码。依据：[InputReader.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/reader/InputReader.cpp)、[InputDispatcher.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp)。

### 5.2 InputDispatcher 分发

分发器依据窗口输入信息、触摸区域、焦点及策略选择目标。触摸不等于总发送给键盘焦点窗口，事件注入接口也不等于普通硬件输入路径。排队、发布、完成确认和 ANR 超时需要分开分析。依据：[InputDispatcher.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp)。

## 6. Framework 层 - WindowManagerService

### 6.1 WMS 角色

窗口系统管理窗口生命周期、几何、层级和焦点，并与输入系统共享路由所需信息及策略。InputDispatcher 负责基于这些信息选取输入目标，不能画成“每个 MotionEvent 先到 WMS 再转发 App”。

### 6.2 Input 事件路由

```text
职责示意（非逐字源码）：
控制面：窗口/输入信息更新，窗口注册与通道建立
数据面：InputDispatcher -> InputChannel -> App InputEventReceiver
```

删除原来虚构的 `WindowManagerService.dispatchInputEvent(...)` / `window.mInputChannel.sendMessage(...)` 源码；固定 tag 可从分发端和接收端核对实际数据路径。依据：[InputDispatcher.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp)、[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)（`setView`、`WindowInputEventReceiver`）。

## 7. App层 - ViewRootImpl

### 7.1 从 InputEventReceiver 进入 Java

每个窗口的 ViewRootImpl 持有 WindowInputEventReceiver。其 `onInputEvent()` 调用 `processRawInputEvent(event)`，不是直接把每一个输入对象都强转为 MotionEvent 交给 View。输入兼容处理可能将一个原事件变成多个事件，或直接结束该事件。

源码精简节选（省略注释；[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
public void processRawInputEvent(InputEvent event) {
    List<InputEvent> processedEvents = null;
    if (mInputCompatHandler != null) {
        Trace.traceBegin(Trace.TRACE_TAG_VIEW, "processInputEventForCompatibility");
        try {
            processedEvents = mInputCompatHandler.processInputEvent(event);
        } finally {
            Trace.traceEnd(Trace.TRACE_TAG_VIEW);
        }
    }
    if (processedEvents != null) {
        if (processedEvents.isEmpty()) {
            mInputEventReceiver.finishInputEvent(event, true);
        } else {
            for (int i = 0; i < processedEvents.size(); i++) {
                enqueueInputEvent(
                        processedEvents.get(i), mInputEventReceiver,
                        QueuedInputEvent.FLAG_MODIFIED_FOR_COMPATIBILITY, true);
            }
        }
    } else {
        enqueueInputEvent(event, mInputEventReceiver, 0, true);
    }
}
```

常规分支 `enqueueInputEvent(event, receiver, 0, true)` 将事件包成 QueuedInputEvent，并要求及时处理队列。批量输入待消费则由 `onBatchedInputEventPending()` 配合帧输入回调消费；启用 unbuffered input 时有立即消费分支。因此“所有触摸必须等下一次 doFrame 才分发”和“每个 MOVE 都立即独立唤醒 UI”都不准确。

### 7.2 InputStage 责任链与选路

setView 在窗口附着时按逆序构造链，真正的前向顺序为：

```text
NativePreIme -> ViewPreIme -> Ime -> EarlyPostIme
                                      -> NativePostIme -> ViewPostIme -> Synthetic
```

| 阶段 | 主要职责 |
|---|---|
| NativePreIme / NativePostIme | 向存在的原生输入队列提供处理机会 |
| ViewPreIme | View 树的 pre-IME 按键路径 |
| Ime | 将适合的输入交给输入法，可能异步完成 |
| EarlyPostIme | post-IME 早期状态处理，例如触摸模式等 |
| ViewPostIme | 把按键、pointer、其他 motion 路由到对应 View 入口 |
| Synthetic | 为未处理的特定输入生成合成事件，不是重复派发所有触摸 |

源码精简节选（省略注释；[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
mSyntheticInputStage = new SyntheticInputStage();
InputStage viewPostImeStage = new ViewPostImeInputStage(mSyntheticInputStage);
InputStage nativePostImeStage = new NativePostImeInputStage(viewPostImeStage,
        "aq:native-post-ime:" + counterSuffix);
InputStage earlyPostImeStage = new EarlyPostImeInputStage(nativePostImeStage);
InputStage imeStage = new ImeInputStage(earlyPostImeStage,
        "aq:ime:" + counterSuffix);
InputStage viewPreImeStage = new ViewPreImeInputStage(imeStage);
InputStage nativePreImeStage = new NativePreImeInputStage(viewPreImeStage,
        "aq:native-pre-ime:" + counterSuffix);
                mFirstInputStage = nativePreImeStage;
                mFirstPostImeInputStage = earlyPostImeStage;
```

源码精简节选（省略注释；[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
private void deliverInputEvent(QueuedInputEvent q) {
    Trace.asyncTraceBegin(Trace.TRACE_TAG_VIEW, "deliverInputEvent",
            q.mEvent.getId());

    if (Trace.isTagEnabled(Trace.TRACE_TAG_VIEW)) {
        Trace.traceBegin(Trace.TRACE_TAG_VIEW, "deliverInputEvent src=0x"
                + Integer.toHexString(q.mEvent.getSource()) + " eventTimeNano="
                + q.mEvent.getEventTimeNanos() + " id=0x"
                + Integer.toHexString(q.mEvent.getId()));
    }
    try {
        if (mInputEventConsistencyVerifier != null) {
            Trace.traceBegin(Trace.TRACE_TAG_VIEW, "verifyEventConsistency");
            try {
                mInputEventConsistencyVerifier.onInputEvent(q.mEvent, 0);
            } finally {
                Trace.traceEnd(Trace.TRACE_TAG_VIEW);
            }
        }

        InputStage stage;
        if (q.shouldSendToSynthesizer()) {
            stage = mSyntheticInputStage;
        } else {
            boolean canSkipToPostIme = q.shouldSkipIme()
                    && (q.mFlags & QueuedInputEvent.FLAG_SKIP_IME) == 0;
            stage = canSkipToPostIme ? mFirstPostImeInputStage : mFirstInputStage;
        }

        if (q.mEvent instanceof KeyEvent) {
            Trace.traceBegin(Trace.TRACE_TAG_VIEW, "preDispatchToUnhandledKeyManager");
            try {
                mUnhandledKeyManager.preDispatch((KeyEvent) q.mEvent);
            } finally {
                Trace.traceEnd(Trace.TRACE_TAG_VIEW);
            }
        }

        if (stage != null) {
            handleWindowFocusChanged();
            stage.deliver(q);
        } else {
            finishInputEvent(q);
        }
    } finally {
        Trace.traceEnd(Trace.TRACE_TAG_VIEW);
    }
}
```

`shouldSendToSynthesizer()` 和 `shouldSkipIme()` 决定从哪个阶段进入；不是每个事件都从链头走到底。InputStage 返回 FORWARD、FINISH_HANDLED、FINISH_NOT_HANDLED 等状态，异步阶段还需要排队和恢复，防止后续事件越过尚未完成的前序处理。

### 7.3 ViewPostImeInputStage：pointer 与非触摸 motion

ViewPostImeInputStage 的 pointer 分支还先让手写启动逻辑处理触摸；未被其完全处理时，才执行 `mView.dispatchPointerEvent(event)`。这里的 mView 一般是 DecorView。

源码精简节选（省略注释；[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
boolean handled = false;
if (!disableHandwritingInitiatorForIme()
        || mWindowAttributes.type != TYPE_INPUT_METHOD) {
    handled = mHandwritingInitiator.onTouchEvent(event);
}
if (handled) {
    mLastClickToolType = event.getToolType(event.getActionIndex());
}

mAttachInfo.mUnbufferedDispatchRequested = false;
mAttachInfo.mHandlingPointerEvent = true;
handled = handled || mView.dispatchPointerEvent(event);
```

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public final boolean dispatchPointerEvent(MotionEvent event) {
    if (event.isTouchEvent()) {
        return dispatchTouchEvent(event);
    } else {
        return dispatchGenericMotionEvent(event);
    }
}
```

因此不能把所有 MotionEvent 都等价于 dispatchTouchEvent。悬停、滚轮等非 touch event 会进入 `dispatchGenericMotionEvent()`；触摸屏 DOWN/MOVE/UP 才进入触摸分发状态机。鼠标 button/source/action 与触摸屏也不能只按一套单指代码处理。

### 7.4 finishInputEvent：结束应用端处理

源码精简节选（省略注释；[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)）：

```java
private void finishInputEvent(QueuedInputEvent q) {
    Trace.asyncTraceEnd(Trace.TRACE_TAG_VIEW, "deliverInputEvent",
            q.mEvent.getId());

    if (q.mReceiver != null) {
        boolean handled = (q.mFlags & QueuedInputEvent.FLAG_FINISHED_HANDLED) != 0;
        boolean modified = (q.mFlags & QueuedInputEvent.FLAG_MODIFIED_FOR_COMPATIBILITY) != 0;
        if (modified && mInputCompatHandler != null) {
            Trace.traceBegin(Trace.TRACE_TAG_VIEW, "processInputEventBeforeFinish");
            InputEvent processedEvent;
            try {
                processedEvent =
                        mInputCompatHandler.processInputEventBeforeFinish(q.mEvent);
            } finally {
                Trace.traceEnd(Trace.TRACE_TAG_VIEW);
            }
            if (processedEvent != null) {
                q.mReceiver.finishInputEvent(processedEvent, handled);
            }
        } else {
            q.mReceiver.finishInputEvent(q.mEvent, handled);
        }
        if (q.mEvent instanceof KeyEvent) {
            logHandledSystemKey((KeyEvent) q.mEvent, handled);
        }
    } else {
        q.mEvent.recycleIfNeededAfterDispatch();
    }

    recycleQueuedInputEvent(q);
}
```

应用最终向 receiver 回报 handled，并回收队列包装对象。兼容转换后的事件要通过 `processInputEventBeforeFinish()` 对应回原输入协议，而不是任意地对转换后的每个对象重复结束原事件。

handled=false 是本窗口应用端的处理结果，不代表 ViewRootImpl 把同一个事件自动送给屏幕上下一层应用窗口。窗口选择和系统策略属于 InputDispatcher；View 树的“子不处理，父有机会处理”不能跨进程照搬成“事件无限穿透所有窗口”。

## 8. App层 - Activity

### 8.1 DecorView、Window.Callback 与 Activity

源码精简节选（省略注释；[DecorView.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/policy/DecorView.java)）：

```java
public boolean dispatchTouchEvent(MotionEvent ev) {
    if (interceptBackProgress(ev)) {
        return true;
    }
    final Window.Callback cb = mWindow.getCallback();
    return cb != null && !mWindow.isDestroyed() && mFeatureId < 0
            ? cb.dispatchTouchEvent(ev) : super.dispatchTouchEvent(ev);
}
```

源码精简节选（省略注释；[Activity.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Activity.java)）：

```java
public boolean dispatchTouchEvent(MotionEvent ev) {
    if (ev.getAction() == MotionEvent.ACTION_DOWN) {
        onUserInteraction();
    }
    if (getWindow().superDispatchTouchEvent(ev)) {
        return true;
    }
    return onTouchEvent(ev);
}
```

源码精简节选（省略注释；[PhoneWindow.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/policy/PhoneWindow.java)）：

```java
public boolean superDispatchTouchEvent(MotionEvent event) {
    return mDecor.superDispatchTouchEvent(event);
}
```

源码精简节选（省略注释；[DecorView.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/policy/DecorView.java)）：

```java
public boolean superDispatchTouchEvent(MotionEvent event) {
    return super.dispatchTouchEvent(event);
}
```

### 8.2 为什么不会无限递归

```text
ViewPostImeInputStage
  DecorView.dispatchPointerEvent
    DecorView.dispatchTouchEvent
      Window.Callback（普通 Activity）.dispatchTouchEvent
        PhoneWindow.superDispatchTouchEvent
          DecorView.superDispatchTouchEvent
            super.dispatchTouchEvent -> ViewGroup 分发子树
        若 Window 路径未处理 -> Activity.onTouchEvent
```

两个 DecorView 入口职责不同：普通 dispatch 负责进入窗口 callback，superDispatch 则明确调用父类实现，避免再次回到 Activity。触摸首先进入 DecorView 再回调 Activity；教学中的“Activity → Window → DecorView”只描述 Activity 已进入后的下行半段。

该 tag 的 DecorView 还在窗口 callback 之前调用 `interceptBackProgress(ev)`；不能把预测返回等窗口行为与普通子项分发混为一个始终线性的调用链。应用在 Activity.dispatchTouchEvent 做日志时应委托 super，而不是同时手动再调 decorView.dispatchTouchEvent。

## 9. App层 - ViewGroup

### 9.1 分发状态与完整主干

`ViewGroup.dispatchTouchEvent()` 不是每收到一个 MOVE 都重新找最上层子 View。它先在 DOWN 阶段选中愿意处理事件的目标，再通过 `mFirstTouchTarget` 保存归属。多指分发开启后，同一个父容器可以持有多个目标，每个目标只拥有部分 pointer ID。

| 状态 | 存储位置 | 生命周期 |
|---|---|---|
| 当前目标链 | `mFirstTouchTarget` | DOWN 清理旧流；UP/CANCEL 清理本流 |
| 子目标 | `TouchTarget.child` | 仅在子项 dispatchTouchEvent 返回 true 后建立 |
| 指针集合 | `TouchTarget.pointerIdBits` | POINTER_DOWN 分配、POINTER_UP 移除 |
| 禁止拦截 | `FLAG_DISALLOW_INTERCEPT` | 子项向祖先请求；新 DOWN 重置 |
| 拆分开关 | `FLAG_SPLIT_MOTION_EVENTS` | 控制多个子项是否能独立拥有指针；鼠标事件另行排除 |


以下保留方法的实际控制流；注释、日志之外的分支仍可从代码看到，后续各节逐一解释其设计。

源码精简节选（省略注释；[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)）：

```java
public boolean dispatchTouchEvent(MotionEvent ev) {
    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onTouchEvent(ev, 1);
    }
    if (ev.isTargetAccessibilityFocus() && isAccessibilityFocusedViewOrHost()) {
        ev.setTargetAccessibilityFocus(false);
    }

    boolean handled = false;
    if (onFilterTouchEventForSecurity(ev)) {
        final int action = ev.getAction();
        final int actionMasked = action & MotionEvent.ACTION_MASK;
        if (actionMasked == MotionEvent.ACTION_DOWN) {
            cancelAndClearTouchTargets(ev);
            resetTouchState();
        }
        final boolean intercepted;
        ViewRootImpl viewRootImpl = getViewRootImpl();
        if (actionMasked == MotionEvent.ACTION_DOWN || mFirstTouchTarget != null) {
            final boolean disallowIntercept = (mGroupFlags & FLAG_DISALLOW_INTERCEPT) != 0;
            if (!disallowIntercept) {
                intercepted = onInterceptTouchEvent(ev);
                ev.setAction(action); // restore action in case it was changed
            } else {
                intercepted = false;
            }
        } else {
            intercepted = true;
        }
        if (intercepted || mFirstTouchTarget != null) {
            ev.setTargetAccessibilityFocus(false);
        }
        final boolean canceled = resetCancelNextUpFlag(this)
                || actionMasked == MotionEvent.ACTION_CANCEL;
        final boolean isMouseEvent = ev.getSource() == InputDevice.SOURCE_MOUSE;
        final boolean split = (mGroupFlags & FLAG_SPLIT_MOTION_EVENTS) != 0
                && !isMouseEvent;
        TouchTarget newTouchTarget = null;
        boolean alreadyDispatchedToNewTouchTarget = false;
        if (!canceled && !intercepted) {
            View childWithAccessibilityFocus = ev.isTargetAccessibilityFocus()
                    ? findChildWithAccessibilityFocus() : null;

            if (actionMasked == MotionEvent.ACTION_DOWN
                    || (split && actionMasked == MotionEvent.ACTION_POINTER_DOWN)
                    || actionMasked == MotionEvent.ACTION_HOVER_MOVE) {
                final int actionIndex = ev.getActionIndex(); // always 0 for down
                final int idBitsToAssign = split ? 1 << ev.getPointerId(actionIndex)
                        : TouchTarget.ALL_POINTER_IDS;
                removePointersFromTouchTargets(idBitsToAssign);

                final int childrenCount = mChildrenCount;
                if (newTouchTarget == null && childrenCount != 0) {
                    final float x = ev.getXDispatchLocation(actionIndex);
                    final float y = ev.getYDispatchLocation(actionIndex);
                    final ArrayList<View> preorderedList = buildTouchDispatchChildList();
                    final boolean customOrder = preorderedList == null
                            && isChildrenDrawingOrderEnabled();
                    final View[] children = mChildren;
                    for (int i = childrenCount - 1; i >= 0; i--) {
                        final int childIndex = getAndVerifyPreorderedIndex(
                                childrenCount, i, customOrder);
                        final View child = getAndVerifyPreorderedView(
                                preorderedList, children, childIndex);
                        if (childWithAccessibilityFocus != null) {
                            if (childWithAccessibilityFocus != child) {
                                continue;
                            }
                            childWithAccessibilityFocus = null;
                            i = childrenCount;
                        }

                        if (!child.canReceivePointerEvents()
                                || !isTransformedTouchPointInView(x, y, child, null)) {
                            ev.setTargetAccessibilityFocus(false);
                            continue;
                        }

                        newTouchTarget = getTouchTarget(child);
                        if (newTouchTarget != null) {
                            newTouchTarget.pointerIdBits |= idBitsToAssign;
                            break;
                        }

                        resetCancelNextUpFlag(child);
                        if (dispatchTransformedTouchEvent(ev, false, child, idBitsToAssign)) {
                            mLastTouchDownTime = ev.getDownTime();
                            if (preorderedList != null) {
                                for (int j = 0; j < childrenCount; j++) {
                                    if (children[childIndex] == mChildren[j]) {
                                        mLastTouchDownIndex = j;
                                        break;
                                    }
                                }
                            } else {
                                mLastTouchDownIndex = childIndex;
                            }
                            mLastTouchDownX = x;
                            mLastTouchDownY = y;
                            newTouchTarget = addTouchTarget(child, idBitsToAssign);
                            alreadyDispatchedToNewTouchTarget = true;
                            break;
                        }
                        ev.setTargetAccessibilityFocus(false);
                    }
                    if (preorderedList != null) preorderedList.clear();
                }

                if (newTouchTarget == null && mFirstTouchTarget != null) {
                    newTouchTarget = mFirstTouchTarget;
                    while (newTouchTarget.next != null) {
                        newTouchTarget = newTouchTarget.next;
                    }
                    newTouchTarget.pointerIdBits |= idBitsToAssign;
                }
            }
        }
        if (mFirstTouchTarget == null) {
            handled = dispatchTransformedTouchEvent(ev, canceled, null,
                    TouchTarget.ALL_POINTER_IDS);
        } else {
            TouchTarget predecessor = null;
            TouchTarget target = mFirstTouchTarget;
            while (target != null) {
                final TouchTarget next = target.next;
                if (alreadyDispatchedToNewTouchTarget && target == newTouchTarget) {
                    handled = true;
                } else {
                    final boolean cancelChild =
                            (target.child != null && resetCancelNextUpFlag(target.child))
                                    || intercepted;
                    if (target.child != null && dispatchTransformedTouchEvent(ev, cancelChild,
                            target.child, target.pointerIdBits)) {
                        handled = true;
                    }
                    if (cancelChild) {
                        if (predecessor == null) {
                            mFirstTouchTarget = next;
                        } else {
                            predecessor.next = next;
                        }
                        if (!target.isRecycled()) {
                            target.recycle();
                        }
                        target = next;
                        continue;
                    }
                }
                predecessor = target;
                target = next;
            }
        }
        if (canceled
                || actionMasked == MotionEvent.ACTION_UP
                || actionMasked == MotionEvent.ACTION_HOVER_MOVE) {
            resetTouchState();
        } else if (split && actionMasked == MotionEvent.ACTION_POINTER_UP) {
            final int actionIndex = ev.getActionIndex();
            final int idBitsToRemove = 1 << ev.getPointerId(actionIndex);
            removePointersFromTouchTargets(idBitsToRemove);
        }
    }

    if (!handled && mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onUnhandledEvent(ev, 1);
    }
    return handled;
}
```

初始 DOWN 即使发现残留目标，也会先 cancelAndClearTouchTargets，再 resetTouchState。这不是假设每条输入流永远完整：窗口切换、异常等情况可能使上一条流缺少正常结束事件，新的 DOWN 必须把状态机带回起点。

### 9.2 TouchTarget 链：建立、复用、移除

源码精简节选（省略注释；[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)）：

```java
private static final class TouchTarget {
    private static final int MAX_RECYCLED = 32;
    private static final Object sRecycleLock = new Object[0];
    private static TouchTarget sRecycleBin;
    private static int sRecycledCount;

    public static final int ALL_POINTER_IDS = -1; // all ones
    @UnsupportedAppUsage
    public View child;
    public int pointerIdBits;
    public TouchTarget next;

    @UnsupportedAppUsage
    private TouchTarget() {
    }

    public static TouchTarget obtain(@NonNull View child, int pointerIdBits) {
        if (child == null) {
            throw new IllegalArgumentException("child must be non-null");
        }

        final TouchTarget target;
        synchronized (sRecycleLock) {
            if (sRecycleBin == null) {
                target = new TouchTarget();
            } else {
                target = sRecycleBin;
                sRecycleBin = target.next;
                 sRecycledCount--;
                target.next = null;
            }
        }
        target.child = child;
        target.pointerIdBits = pointerIdBits;
        return target;
    }

    public boolean isRecycled() {
        return child == null;
    }

    public void recycle() {
        if (child == null) {
            throw new IllegalStateException("already recycled once");
        }

        synchronized (sRecycleLock) {
            if (sRecycledCount < MAX_RECYCLED) {
                next = sRecycleBin;
                sRecycleBin = this;
                sRecycledCount += 1;
            } else {
                next = null;
            }
            child = null;
        }
    }
}
```

源码精简节选（省略注释；[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)）：

```java
private TouchTarget getTouchTarget(@NonNull View child) {
    for (TouchTarget target = mFirstTouchTarget; target != null; target = target.next) {
        if (target.child == child) {
            return target;
        }
    }
    return null;
}

private TouchTarget addTouchTarget(@NonNull View child, int pointerIdBits) {
    final TouchTarget target = TouchTarget.obtain(child, pointerIdBits);
    target.next = mFirstTouchTarget;
    mFirstTouchTarget = target;
    return target;
}

private void removePointersFromTouchTargets(int pointerIdBits) {
    TouchTarget predecessor = null;
    TouchTarget target = mFirstTouchTarget;
    while (target != null) {
        final TouchTarget next = target.next;
        if ((target.pointerIdBits & pointerIdBits) != 0) {
            target.pointerIdBits &= ~pointerIdBits;
            if (target.pointerIdBits == 0) {
                if (predecessor == null) {
                    mFirstTouchTarget = next;
                } else {
                    predecessor.next = next;
                }
                target.recycle();
                target = next;
                continue;
            }
        }
        predecessor = target;
        target = next;
    }
}
```

`addTouchTarget()` 是头插法，因此链头是最近加入的目标；不是按 child index 排序的链，也不表示视觉最上层。对象池上限 32 是回收对象数，不是容器最多支持 32 个子项，更不是触摸屏硬件同时触点数的声明。

```text
p0 DOWN 命中 A：      head -> [A, bits=0001] -> null
p2 POINTER_DOWN 命中 B：head -> [B, bits=0100] -> [A, bits=0001]
p3 POINTER_DOWN 命中 A：head -> [B, bits=0100] -> [A, bits=1001]
p2 POINTER_UP 后：    head -> [A, bits=1001] -> null
```

这段例子中的 ID 取 0、2、3，是为了强调 **ID 不是 index**。index 是当前 MotionEvent 中数组位置；ID 用于跨帧追踪，同一子项再次命中只合并位，不再创建重复目标。

如果新增指针没有命中愿意处理的新子项，而链表已有目标，源码把该 ID 交给链尾，也就是最早加入的目标。这一回退使新增触点仍有所属；不能把它描述为“永远交给链头”或“新增手指没命中就整个事件丢失”。

### 9.3 拦截、CANCEL 与当前 MOVE 的去向

拦截判断发生于 DOWN 或 `mFirstTouchTarget != null` 时；若没有目标且不是 DOWN，父容器直接按 intercepted=true 处理，不再重复询问 onInterceptTouchEvent。`requestDisallowInterceptTouchEvent(true)` 使祖先跳过本流后续拦截判断，但不能阻止系统取消事件，也不能挽回已经发生的拦截。

最容易写错的是“父在 MOVE 拦截后，立即用同一个 MOVE 调用自己的 onTouchEvent”。在该 tag 中，若进入分发分支时已有目标链，代码会沿链把事件改成 CANCEL 发给原子项并移除目标；**不会在本次调用中再回到无目标分支重发原始 MOVE 给父自身**。后续 MOVE/UP 才因没有目标走父自身 View.dispatchTouchEvent。

| 输入到父容器 | 父拦截判断 | 子项看到 | 父 onTouchEvent |
|---|---|---|---|
| DOWN | false | DOWN，返回 true 建目标 | 不调用 |
| MOVE 1 | false | MOVE | 不调用 |
| MOVE 2 | true | CANCEL，并从目标链移除 | 本次不因这条已有目标分支再调用 |
| MOVE 3 | 无目标，直接 intercepted=true | 不再接收 | MOVE |
| UP | 同上 | 不再接收 | UP，之后清理父状态 |

因此拖动父容器应在 onInterceptTouchEvent 的 DOWN 记录坐标；决定接管时记录/重置拖动基准。不要等 onTouchEvent 首次收到 DOWN 才初始化，因为中途接管时它没有这个 DOWN。

外部 ACTION_CANCEL 则沿正常目标分发路径转成取消语义；`dispatchTransformedTouchEvent()` 即使算出的指针交集为空，也会保留 CANCEL，避免子项因错失取消而残留 pressed、长按计时或拖动状态。

源码精简节选（省略注释；[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)）：

```java
private void resetTouchState() {
    clearTouchTargets();
    resetCancelNextUpFlag(this);
    mGroupFlags &= ~FLAG_DISALLOW_INTERCEPT;
    mNestedScrollAxes = SCROLL_AXIS_NONE;
}

private void cancelAndClearTouchTargets(MotionEvent event) {
    if (mFirstTouchTarget != null) {
        boolean syntheticEvent = false;
        if (event == null) {
            final long now = SystemClock.uptimeMillis();
            event = MotionEvent.obtain(now, now,
                    MotionEvent.ACTION_CANCEL, 0.0f, 0.0f, 0);
            event.setSource(InputDevice.SOURCE_TOUCHSCREEN);
            syntheticEvent = true;
        }

        for (TouchTarget target = mFirstTouchTarget; target != null; target = target.next) {
            resetCancelNextUpFlag(target.child);
            dispatchTransformedTouchEvent(event, true, target.child, target.pointerIdBits);
        }
        clearTouchTargets();

        if (syntheticEvent) {
            event.recycle();
        }
    }
}
```

### 9.4 命中测试：父滚动、子位置与逆矩阵

父容器先判断子项能否接收 pointer event，再把当前触点转换到子坐标做 `pointInView()`。输入坐标不能直接与屏幕绝对坐标或一个未经变换的 Rect 比较。

源码精简节选（省略注释；[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)）：

```java
protected boolean isTransformedTouchPointInView(float x, float y, View child,
        PointF outLocalPoint) {
    final float[] point = getTempLocationF();
    point[0] = x;
    point[1] = y;
    transformPointToViewLocal(point, child);
    final boolean isInView = child.pointInView(point[0], point[1]);
    if (isInView && outLocalPoint != null) {
        outLocalPoint.set(point[0], point[1]);
    }
    return isInView;
}

public void transformPointToViewLocal(float[] point, View child) {
    point[0] += mScrollX - child.mLeft;
    point[1] += mScrollY - child.mTop;

    if (!child.hasIdentityMatrix()) {
        child.getInverseMatrix().mapPoints(point);
    }
}
```

计算可分两步理解：先得到 `(x + parent.scrollX - child.left, y + parent.scrollY - child.top)`；有非单位矩阵时，再乘 child 的逆矩阵。translation、scale、rotation 在显示侧施加变换，命中侧用逆变换把点送回 View 自己的局部几何。

例如 child.left=100，translationX=30，父 scrollX=10，屏幕上转换到父局部后的触点 x=125：先平移得到 35，再减去 translation 对应逆变换的 30，child 局部 x=5。只比较原始 left=100 到 right 会误判变换后的边缘。

命中测试只在分配新目标时使用。子项一旦消费 DOWN，手指移出边界并不会让父重新选择另一个兄弟；是否继续点击由子 onTouchEvent 的 slop/pressed 状态机处理。

### 9.5 split：每个子项拥有自己的动作序列

`split` 条件是开启 `FLAG_SPLIT_MOTION_EVENTS` 且事件来源不是 `SOURCE_MOUSE`。开启后，DOWN 和 POINTER_DOWN 可以选新目标；关闭时目标使用 `ALL_POINTER_IDS`，后来按下的手指不会凭位置另选兄弟。

```text
父容器原始流             A 的流（只拥有 ID 0）      B 的流（只拥有 ID 1）
DOWN p0@A               DOWN p0                   --
POINTER_DOWN p1@B        MOVE p0                   DOWN p1
MOVE p0,p1              MOVE p0                   MOVE p1
POINTER_UP p0           UP p0                     MOVE p1
UP p1                   --                        UP p1
```

`MotionEvent.split()` 不只是删去不属于目标的坐标：它重建 pointer index，并把不涉及自己的 POINTER_DOWN/UP 转为 MOVE；目标只剩一个有效指针且该指针正是动作指针时，转为 DOWN/UP。于是每个子项可以独立得到完整的单指生命周期。

消费状态以目标链为依据，不是 MOVE 返回值投票。子项在 DOWN 返回 true 后，某次 MOVE 返回 false，不会触发父重新扫描兄弟或删除目标；返回值仍影响这次事件的 handled 汇总，但不是“放弃后续手势”的接口。

### 9.6 Z 轴、绘制顺序与 bringToFront

源码精简节选（省略注释；[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)）：

```java
public ArrayList<View> buildTouchDispatchChildList() {
    return buildOrderedChildList();
}

ArrayList<View> buildOrderedChildList() {
    final int childrenCount = mChildrenCount;
    if (childrenCount <= 1 || !hasChildWithZ()) return null;

    if (mPreSortedChildren == null) {
        mPreSortedChildren = new ArrayList<>(childrenCount);
    } else {
        mPreSortedChildren.clear();
        mPreSortedChildren.ensureCapacity(childrenCount);
    }

    final boolean customOrder = isChildrenDrawingOrderEnabled();
    for (int i = 0; i < childrenCount; i++) {
        final int childIndex = getAndVerifyPreorderedIndex(childrenCount, i, customOrder);
        final View nextChild = mChildren[childIndex];
        final float currentZ = nextChild.getZ();
        int insertIndex = i;
        while (insertIndex > 0 && mPreSortedChildren.get(insertIndex - 1).getZ() > currentZ) {
            insertIndex--;
        }
        mPreSortedChildren.add(insertIndex, nextChild);
    }
    return mPreSortedChildren;
}

public void bringChildToFront(View child) {
    final int index = indexOfChild(child);
    if (index >= 0) {
        removeFromArray(index);
        addInArray(child, mChildrenCount);
        child.mParent = this;
        requestLayout();
        invalidate();
    }
}
```

当存在非零 Z 时，`buildOrderedChildList()` 按 `getZ()` 升序构建列表，同 Z 时保持基于普通/自定义 drawing order 的稳定顺序；触摸分发再从后往前扫描。没有 Z 排序列表时，才直接通过自定义 drawing order 或 mChildren 倒序扫描。

`getZ() = elevation + translationZ`。`bringToFront()` 调整父容器中的子项顺序并请求布局/重绘，不会自动把 elevation 设为全树最大。因此 A 的 Z=8dp、B 的 Z=0dp，即使 B 调了 bringToFront，也不能据此认定重叠区先分给 B。

这些排序只影响新触点的目标选择。把 A 提到最上层不会抢走 B 正在处理的手势；当前 TouchTarget 仍指向 B，直到结束或被取消。

## 10. App层 - View

### 10.1 dispatchTouchEvent 与 performOnTouchCallback

Android 17 将具体触摸回调收拢到 `performOnTouchCallback()`。外层负责无障碍目标检查、安全过滤和 nested scroll 的防御性清理；内层才调用滚动条拖动、OnTouchListener 和 onTouchEvent。

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public boolean dispatchTouchEvent(MotionEvent event) {
    if (event.isTargetAccessibilityFocus()) {
        if (!isAccessibilityFocusedViewOrHost()) {
            return false;
        }
        event.setTargetAccessibilityFocus(false);
    }
    boolean result = false;

    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onTouchEvent(event, 0);
    }

    final int actionMasked = event.getActionMasked();
    if (actionMasked == MotionEvent.ACTION_DOWN) {
        stopNestedScroll();
    }

    if (onFilterTouchEventForSecurity(event)) {
        result = performOnTouchCallback(event);
    }

    if (!result && mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onUnhandledEvent(event, 0);
    }
    if (actionMasked == MotionEvent.ACTION_UP ||
            actionMasked == MotionEvent.ACTION_CANCEL ||
            (actionMasked == MotionEvent.ACTION_DOWN && !result)) {
        stopNestedScroll();
    }

    return result;
}

private boolean performOnTouchCallback(MotionEvent event) {
    boolean handled = false;
    if ((mViewFlags & ENABLED_MASK) == ENABLED && handleScrollBarDragging(event)) {
        handled = true;
    }
    ListenerInfo li = mListenerInfo;
    if (li != null && li.mOnTouchListener != null && (mViewFlags & ENABLED_MASK) == ENABLED) {
        try {
            if (Trace.isTagEnabled(TRACE_TAG_VIEW)) {
                Trace.traceBegin(TRACE_TAG_VIEW,
                        "View.onTouchListener#onTouch - " + getClass().getSimpleName()
                                + ", eventId - " + event.getId());
            }
            handled = li.mOnTouchListener.onTouch(this, event);
        } finally {
            Trace.traceEnd(TRACE_TAG_VIEW);
        }
    }
    if (handled) {
        return true;
    }
    try {
        Trace.traceBegin(TRACE_TAG_VIEW, "View#onTouchEvent");
        return onTouchEvent(event);
    } finally {
        Trace.traceEnd(TRACE_TAG_VIEW);
    }
}
```

这里不是把几个返回值简单 OR：滚动条处理先写 handled，有启用的 OnTouchListener 时其返回值又赋给 handled，然后才决定是否调用 onTouchEvent。一般业务场景下可理解为启用的 listener 返回 true 则跳过 onTouchEvent；若返回 false 则继续默认处理。`setOnClickListener` 对应的点击回调在 onTouchEvent 的 UP 状态机后面，不与 OnTouchListener 并列直接执行。

### 10.2 onTouchEvent 的字段与返回值

| 字段 / 标志 | 用途 |
|---|---|
| CLICKABLE / LONG_CLICKABLE / CONTEXT_CLICKABLE | 是否支持相应用户交互；任一成立可形成 clickable 处理路径 |
| PFLAG_PRESSED / PFLAG_PREPRESSED | 当前按压视觉状态及滚动容器中的延迟按压状态 |
| mHasPerformedLongPress | 防止长按成功后又在 UP 重复触发普通点击 |
| mIgnoreNextUpEvent | 某些交互结束后忽略下一次 UP 点击 |
| mPendingCheckForTap / 长按回调 | 延迟显示按压与判定长按；MOVE 越界或 CANCEL 应移除 |
| mTouchDelegate | 在本 View 默认触摸处理里转发扩展点击区域 |

DISABLED 不等于一定返回 false。源码的禁用分支在未允许禁用点击时返回 clickable：可以消费但不执行正常点击。另一方面，父容器给子项分配事件主要不是检查 enabled，不能用 `isEnabled=false` 代替“让触摸透给后方兄弟”的明确分发设计。

### 10.3 onTouchEvent 源码与状态转换

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public boolean onTouchEvent(MotionEvent event) {
    final float x = event.getX();
    final float y = event.getY();
    final int viewFlags = mViewFlags;
    final int action = event.getAction();

    final boolean clickable = ((viewFlags & CLICKABLE) == CLICKABLE
            || (viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE)
            || (viewFlags & CONTEXT_CLICKABLE) == CONTEXT_CLICKABLE;

    if ((viewFlags & ENABLED_MASK) == DISABLED
            && (mPrivateFlags4 & PFLAG4_ALLOW_CLICK_WHEN_DISABLED) == 0) {
        if (action == MotionEvent.ACTION_UP && (mPrivateFlags & PFLAG_PRESSED) != 0) {
            setPressed(false);
        }
        mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
        return clickable;
    }
    if (mTouchDelegate != null) {
        if (mTouchDelegate.onTouchEvent(event)) {
            return true;
        }
    }

    if (clickable || (viewFlags & TOOLTIP) == TOOLTIP) {
        switch (action) {
            case MotionEvent.ACTION_UP:
                mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
                if ((viewFlags & TOOLTIP) == TOOLTIP) {
                    handleTooltipUp();
                }
                if (!clickable) {
                    removeTapCallback();
                    removeLongPressCallback();
                    mInContextButtonPress = false;
                    mHasPerformedLongPress = false;
                    mIgnoreNextUpEvent = false;
                    break;
                }
                boolean prepressed = (mPrivateFlags & PFLAG_PREPRESSED) != 0;
                if ((mPrivateFlags & PFLAG_PRESSED) != 0 || prepressed) {
                    boolean focusTaken = false;
                    if (isFocusable() && isFocusableInTouchMode() && !isFocused()) {
                        focusTaken = requestFocus();
                    }

                    if (prepressed) {
                        setPressed(true, x, y);
                    }

                    if (!mHasPerformedLongPress && !mIgnoreNextUpEvent) {
                        removeLongPressCallback();
                        if (!focusTaken) {
                            if (mPerformClick == null) {
                                mPerformClick = new PerformClick();
                            }
                            if (!post(mPerformClick)) {
                                performClickInternal();
                            }
                        }
                    }

                    if (mUnsetPressedState == null) {
                        mUnsetPressedState = new UnsetPressedState();
                    }

                    if (prepressed) {
                        postDelayed(mUnsetPressedState,
                                ViewConfiguration.getPressedStateDuration());
                    } else if (!post(mUnsetPressedState)) {
                        mUnsetPressedState.run();
                    }

                    removeTapCallback();
                }
                mIgnoreNextUpEvent = false;
                break;

            case MotionEvent.ACTION_DOWN:
                if (event.getSource() == InputDevice.SOURCE_TOUCHSCREEN) {
                    mPrivateFlags3 |= PFLAG3_FINGER_DOWN;
                }
                mHasPerformedLongPress = false;

                if (!clickable) {
                    checkForLongClick(
                            getLongPressTimeoutMillis(),
                            x,
                            y,
                            TOUCH_GESTURE_CLASSIFIED__CLASSIFICATION__LONG_PRESS);
                    break;
                }

                if (performButtonActionOnTouchDown(event)) {
                    break;
                }
                boolean isInScrollingContainer = isInScrollingContainer();
                if (isInScrollingContainer) {
                    mPrivateFlags |= PFLAG_PREPRESSED;
                    if (mPendingCheckForTap == null) {
                        mPendingCheckForTap = new CheckForTap();
                    }
                    mPendingCheckForTap.x = event.getX();
                    mPendingCheckForTap.y = event.getY();
                    postDelayed(mPendingCheckForTap, getTapTimeoutMillis());
                } else {
                    setPressed(true, x, y);
                    checkForLongClick(
                            getLongPressTimeoutMillis(),
                            x,
                            y,
                            TOUCH_GESTURE_CLASSIFIED__CLASSIFICATION__LONG_PRESS);
                }
                break;

            case MotionEvent.ACTION_CANCEL:
                if (clickable) {
                    setPressed(false);
                }
                removeTapCallback();
                removeLongPressCallback();
                mInContextButtonPress = false;
                mHasPerformedLongPress = false;
                mIgnoreNextUpEvent = false;
                mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
                break;

            case MotionEvent.ACTION_MOVE:
                if (clickable) {
                    drawableHotspotChanged(x, y);
                }

                final int motionClassification = event.getClassification();
                final boolean ambiguousGesture =
                        motionClassification == MotionEvent.CLASSIFICATION_AMBIGUOUS_GESTURE;
                int touchSlop = mViewConfiguration.getScaledTouchSlop();
                if (ambiguousGesture && hasPendingLongPressCallback()) {
                    float ambiguousGestureMultiplier =
                            mViewConfiguration.getScaledAmbiguousGestureMultiplier();
                    if (!pointInView(x, y, touchSlop)) {
                        removeLongPressCallback();
                        long delay = (long) (getLongPressTimeoutMillis()
                                * ambiguousGestureMultiplier);
                        delay -= event.getEventTime() - event.getDownTime();
                        checkForLongClick(
                                delay,
                                x,
                                y,
                                TOUCH_GESTURE_CLASSIFIED__CLASSIFICATION__LONG_PRESS);
                    }
                    touchSlop *= ambiguousGestureMultiplier;
                }
                if (!pointInView(x, y, touchSlop)) {
                    removeTapCallback();
                    removeLongPressCallback();
                    if ((mPrivateFlags & PFLAG_PRESSED) != 0) {
                        setPressed(false);
                    }
                    mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
                }

                final boolean deepPress =
                        motionClassification == MotionEvent.CLASSIFICATION_DEEP_PRESS;
                if (deepPress && hasPendingLongPressCallback()) {
                    removeLongPressCallback();
                    checkForLongClick(
                            0 ,
                            x,
                            y,
                            TOUCH_GESTURE_CLASSIFIED__CLASSIFICATION__DEEP_PRESS);
                }

                break;
        }

        return true;
    }

    return false;
}
```

DOWN 会建立 pressed 或 prepressed，并安排长按。滚动容器内先延迟 pressed，是为了避免用户只是滚动列表时每个经过的按钮都立即亮起。MOVE 会更新热点并按 touchSlop 判断是否已离开可点击区域；CANCEL 清理 pressed、tap/long-press 回调及相关手势状态，不调用 performClick。

UP 是否点击还受长按结果、忽略 UP 标志、焦点获取等条件约束。`PerformClick` 优先 post 执行，post 失败时同步回退到 `performClickInternal()`，所以不能说“所有点击都在 onTouchEvent 内同步执行完”。自定义可点击 View 应通过 performClick 暴露语义，才能兼容无障碍与非触摸激活。

## 11. 完整流程图汇总

### 11.1 从内核到 View 的完整链路

```text
流程示意（普通触摸；省略策略过滤、输入监视、IME 和无障碍分支）：
Input Driver -> /dev/input/eventX -> EventHub
  -> InputReader / InputDevice / mapper -> NotifyArgs
  -> InputDispatcher -> InputChannel（socketpair）
  -> App WindowInputEventReceiver -> ViewRootImpl 输入阶段链
  -> 根 View 的 dispatchPointerEvent -> 触摸 dispatchTouchEvent
```

窗口系统更新路由所需的窗口/焦点信息，但常规触摸数据不先交给 WMS 再由 Java 转发。图中的 native reader/dispatcher 是同一输入流程，不应再复制为一套额外“Framework 层”线程。依据：[InputReader.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/reader/InputReader.cpp)、[InputDispatcher.cpp](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp)、[ViewRootImpl.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java)。

应用窗口内继续沿第 8 节的 Window.Callback 链路分发；中途拦截时向已有子目标发 CANCEL，不是把当前 MOVE 改成 CANCEL 给父级自己。

## 12. 核心方法详解

### 12.1 方法对比表

| 方法 | 所在类 | 作用 | 返回值含义 |
|------|--------|------|------------|
| `dispatchTouchEvent` | Activity/ViewGroup/View | 事件分发入口 | true=已消费 |
| `onInterceptTouchEvent` | ViewGroup | 拦截判断 | true=拦截 |
| `onTouchEvent` | Activity/ViewGroup/View | 事件处理 | true=已消费 |

### 12.2 事件消费优先级

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          事件消费优先级                                     │
└─────────────────────────────────────────────────────────────────────────────┘

优先级从高到低:

  1.  OnTouchListener.onTouch()
         │
         │  (如果返回 true，不再执行后续)
         ▼
  2.  onTouchEvent()
         │
         │  (如果返回 true，不再执行后续)
         ▼
  3.  OnClickListener.onClick()
         │
         │  (在 onTouchEvent 的 ACTION_UP 中调用)
         ▼
  4.  OnLongClickListener.onLongClick()
```

---

## 13. 事件序列与状态管理

### 13.1 ACTION_DOWN 的特殊性

1. 返回值表示这次调用是否处理事件，不是把事件作为新消息“反向冒泡”。查找目标的 DOWN 若子项返回 false，父容器还可能继续尝试其他命中子项；全无目标才走自身 View 分发路径。
2. 子项消费 DOWN 后建立 `TouchTarget`，普通单指后续事件按目标分发，不再每次重新做全量命中测试；父级仍可在满足条件时拦截并取消它。
3. 已有目标在 MOVE 返回 false，不等于自动清除目标或把手势转移给兄弟项；目标清理取决于 CANCEL、拦截、UP、移除等分支。
4. “没消费 DOWN 就永远不再收到事件”只适用于常规单指目标选择的简化讨论。启用 split motion events 时，后续 POINTER_DOWN 可以寻找新目标，不可当作所有多指情形的定律。
5. 多指跟踪使用稳定的 pointer ID，再用 `findPointerIndex(id)` 查当前 index。POINTER_UP 还要迁移活动指针；CANCEL 终止本次流，不是 MOVE/UP 之间的普通插入事件。

依据：[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)、[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)。

### 13.2 事件序列图

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            典型事件序列                                     │
└─────────────────────────────────────────────────────────────────────────────┘

用户操作: 按下 → 滑动 → 抬起

时间轴:
  DOWN          MOVE1         MOVE2         ...         UP
   │              │              │                        │
   ▼              ▼              ▼                        ▼
┌──────┐    ┌──────┐     ┌──────┐               ┌──────┐
│事件ID │    │事件ID │     │事件ID │               │事件ID │
│=0x0000│    │=0x0002│     │=0x0002│               │=0x0001│
│action │    │action │     │action │               │action │
│ │=DOWN    │=MOVE  │     │=MOVE  │               │=UP    │
└──────┘    └──────┘     └──────┘               └──────┘

ViewGroup 处理:
  1. DOWN: onInterceptTouchEvent() 被调用
           ├── 如果返回 false (不拦截): 分发给子 View
           │      └── 子 View 处理 → mFirstTouchTarget = child
           └── 如果返回 true (拦截): 交给自身 onTouchEvent

  2. MOVE: 如果 mFirstTouchTarget != null
           onInterceptTouchEvent() 仍可能被调用
           ├── 如果拦截 → 子 View 收到 ACTION_CANCEL
           └── 如果不拦截 → 继续发给子 View

  3. UP:   同 MOVE
```

---

## 14. 典型场景分析

### 场景一：子 View 处理事件

```text
用户操作: 按下 → 滑动 → 抬起

流程:
DOWN:
  Activity.dispatchTouchEvent
    → DecorView.dispatchTouchEvent
      → ViewGroup1.dispatchTouchEvent
        → ViewGroup1.onInterceptTouchEvent(false)  // 不拦截
          → ViewGroup2.dispatchTouchEvent
            → ViewGroup2.onInterceptTouchEvent(false)
              → ChildView.dispatchTouchEvent
                → ChildView.onTouchEvent(true)     // 处理了!
                → 返回 true
              → mFirstTouchTarget = ChildView
              → 返回 true
            → 返回 true
          → 返回 true
        → 返回 true

MOVE/UP:
  (不再调用 onInterceptTouchEvent，直接发给目标)
  → ChildView.dispatchTouchEvent → onTouchEvent → 返回 true
```

### 场景二：ViewGroup 拦截事件

```text
用户操作: 按下 → 滑动 → 抬起

流程:
DOWN:
  Activity → DecorView → ViewGroup1
    → onInterceptTouchEvent(true)  // 拦截!
      → ViewGroup1.onTouchEvent(true)
      → 返回 true
      → mFirstTouchTarget = null

MOVE/UP:
  (没有目标，直接给自身)
  → ViewGroup1.onInterceptTouchEvent  // 不会被调用!
  → ViewGroup1.onTouchEvent
```

---

## 15. 滑动冲突解决

### 15.1 外部拦截法

```java
public class HorizontalViewGroup extends ViewGroup {
    private int mLastX;
    private int mLastY;
    private int mTouchSlop;

    @Override
    public boolean onInterceptTouchEvent(MotionEvent ev) {
        switch (ev.getAction()) {
            case MotionEvent.ACTION_DOWN:
                mLastX = (int) ev.getX();
                mLastY = (int) ev.getY();
                // 不拦截 DOWN，让子 View 处理
                return false;

            case MotionEvent.ACTION_MOVE:
                int deltaX = (int) (ev.getX() - mLastX);
                int deltaY = (int) (ev.getY() - mLastY);

                // 水平滑动距离大于垂直，拦截
                if (Math.abs(deltaX) > Math.abs(deltaY) + mTouchSlop) {
                    return true;  // 拦截，后续事件交给自身
                }
                return false;  // 不拦截，交给子 View

            case MotionEvent.ACTION_UP:
                return false;  // 不拦截

            default:
                return super.onInterceptTouchEvent(ev);
        }
    }
}
```

### 15.2 内部拦截法

```java
// 子 View 中
public boolean onTouch(View v, MotionEvent ev) {
    switch (ev.getAction()) {
        case MotionEvent.ACTION_DOWN:
            // 请求父 View 不拦截
            getParent().requestDisallowInterceptTouchEvent(true);
            break;

        case MotionEvent.ACTION_MOVE:
            // 处理自己的逻辑
            break;

        case MotionEvent.ACTION_UP:
            // 恢复父 View 拦截能力
            getParent().requestDisallowInterceptTouchEvent(false);
            break;
    }
    return false;  // 事件继续传递
}
```

---

## 16. 进阶知识点

### 16.1 多指触控

使用 actionMasked 判类型，actionIndex 只用于 POINTER_DOWN/POINTER_UP 等指明变化指针的事件。持续拖动保存 pointer ID，每次 MOVE 用 `findPointerIndex` 获取当前 index 并处理 -1；不要保存会重排的 index。CANCEL 必须清理手势状态。依据：[MotionEvent API](https://developer.android.com/reference/android/view/MotionEvent)。


```text
// 1. 使用 getActionMasked() 而不是 getAction()
int action = event.getActionMasked();

switch (action) {
    case MotionEvent.ACTION_DOWN:         // 第一个手指按下
        // ...
        break;

    case MotionEvent.ACTION_POINTER_DOWN: // 第二个手指按下
        int index = event.getActionIndex();
        float pointerX = event.getX(index);
        float pointerY = event.getY(index);
        // ...
        break;

    case MotionEvent.ACTION_MOVE:
        // 遍历所有触摸点
        for (int i = 0; i < event.getPointerCount(); i++) {
            float x = event.getX(i);
            float y = event.getY(i);
            // ...
        }
        break;

    case MotionEvent.ACTION_POINTER_UP:   // 手指抬起
        // ...
        break;

    case MotionEvent.ACTION_CANCEL:       // 清理本次手势，不触发点击
        break;

    case MotionEvent.ACTION_UP:           // 最后一个手指抬起
        // ...
        break;
}
```

### 16.2 TouchDelegate 扩大点击区域

#### 16.2.1 为什么代理要装在父 View 上

24dp 的图标可以拥有更大的触摸区域而不改变视觉布局。祖先先按普通子项边界命中，范围外的 DOWN 不会直接到达图标；把 TouchDelegate 安装到拥有这片空间的父 View 后，父自身的 onTouchEvent 才有机会把扩展区域中的事件转发给图标。

代理不改变测量、布局或祖先的命中边界，也不是全局先于子项的拦截器。普通兄弟先消费 DOWN、父 OnTouchListener 返回 true、祖先已拦截、父禁用而提前返回，均可能使代理没有执行机会。

#### 16.2.2 字段、构造与注册

| 字段 | 含义 |
|---|---|
| `mDelegateView` | 最终调用 dispatchTouchEvent 的目标 |
| `mBounds` | 扩展命中矩形，使用持有 delegate 的 View 的局部坐标 |
| `mSlopBounds` | 在 mBounds 外再加 touchSlop 的容错范围 |
| `mDelegateTargeted` | DOWN 是否选择了代理，用来维持整条流的归属 |
| `mSlop` | 来自 ViewConfiguration 的系统触摸容差 |

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
public void setTouchDelegate(TouchDelegate delegate) {
    mTouchDelegate = delegate;
}
```

源码精简节选（省略注释；[TouchDelegate.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/TouchDelegate.java)）：

```java
public TouchDelegate(Rect bounds, View delegateView) {
    mBounds = bounds;

    mSlop = ViewConfiguration.get(delegateView.getContext()).getScaledTouchSlop();
    mSlopBounds = new Rect(bounds);
    mSlopBounds.inset(-mSlop, -mSlop);
    mDelegateView = delegateView;
}
```

`setTouchDelegate()` 只有一个字段槽位，多次调用覆盖旧代理。构造器保存传入的 bounds 引用，但另建 mSlopBounds，因此不要在构造后只修改原 Rect 却期望 slop 范围自动跟着更新；重新计算时重新创建 delegate。

#### 16.2.3 转发源码：锁定 DOWN，重写坐标

源码精简节选（省略注释；[TouchDelegate.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/TouchDelegate.java)）：

```java
public boolean onTouchEvent(@NonNull MotionEvent event) {
    int x = (int)event.getX();
    int y = (int)event.getY();
    boolean sendToDelegate = false;
    boolean hit = true;
    boolean handled = false;

    switch (event.getActionMasked()) {
        case MotionEvent.ACTION_DOWN:
            mDelegateTargeted = mBounds.contains(x, y);
            sendToDelegate = mDelegateTargeted;
            break;
        case MotionEvent.ACTION_POINTER_DOWN:
        case MotionEvent.ACTION_POINTER_UP:
        case MotionEvent.ACTION_UP:
        case MotionEvent.ACTION_MOVE:
            sendToDelegate = mDelegateTargeted;
            if (sendToDelegate) {
                Rect slopBounds = mSlopBounds;
                if (!slopBounds.contains(x, y)) {
                    hit = false;
                }
            }
            break;
        case MotionEvent.ACTION_CANCEL:
            sendToDelegate = mDelegateTargeted;
            mDelegateTargeted = false;
            break;
    }
    if (sendToDelegate) {
        if (hit) {
            event.setLocation(mDelegateView.getWidth() / 2, mDelegateView.getHeight() / 2);
        } else {
            int slop = mSlop;
            event.setLocation(-(slop * 2), -(slop * 2));
        }
        handled = mDelegateView.dispatchTouchEvent(event);
    }
    return handled;
}
```

DOWN 决定 mDelegateTargeted，后续 MOVE、POINTER_DOWN、POINTER_UP、UP 沿用归属，不会因为手指从外面移入就中途启动代理。命中时 setLocation 到目标中心，使目标默认点击状态机把事件视为内部触摸；移出 slopBounds 时送到 `(-2*slop,-2*slop)`，让默认 View 清掉可点击按压状态。

CANCEL 会转发给既有目标并清 mDelegateTargeted。UP 分支没有显式将该字段设为 false，不能把“UP 和 CANCEL 都在此清位”当逐字源码；下一次 DOWN 会重新赋值。代理面向点击区域扩展，中心重定位不保留精确触点轨迹，不适合作为需要原始坐标的手写/绘图变换器。

#### 16.2.4 在 View.onTouchEvent 中的调用位置

源码精简节选（省略注释；[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)）：

```java
if (mTouchDelegate != null) {
        info.setTouchDelegateInfo(mTouchDelegate.getTouchDelegateInfo());
    }

    if (startedSystemDragForAccessibility()) {
        info.addAction(AccessibilityAction.ACTION_DRAG_CANCEL);
    }

    if (canAcceptAccessibilityDrop()) {
        info.addAction(AccessibilityAction.ACTION_DRAG_DROP);
    }

    if (a11yExtraRenderingInfoColorAdditions()) {
        info.setAvailableExtraData(
                Collections.singletonList(AccessibilityNodeInfo.EXTRA_DATA_RENDERING_INFO_KEY));
    }
}

@FlaggedApi(android.view.accessibility.Flags.FLAG_A11Y_EXTRA_RENDERING_INFO_COLOR_ADDITIONS)
@CallSuper
public void addExtraDataToAccessibilityNodeInfo(
        @NonNull AccessibilityNodeInfo info, @NonNull String extraDataKey,
        @Nullable Bundle arguments) {
    if (android.view.accessibility.Flags.fixAddExtraDataToAccessibilityNodeInfoDelegation()) {
        if (mAccessibilityDelegate != null) {
            mAccessibilityDelegate.addExtraDataToAccessibilityNodeInfo(
                    this, info, extraDataKey, arguments);
        } else {
            addExtraDataToAccessibilityNodeInfoInternal(info, extraDataKey, arguments);
        }
    } else {
        addExtraDataToAccessibilityNodeInfoInternal(info, extraDataKey, arguments);
    }
}

private void addExtraDataToAccessibilityNodeInfoInternal(
        @NonNull AccessibilityNodeInfo info, @NonNull String extraDataKey,
        @Nullable Bundle arguments) {
    if (extraDataKey.equals(AccessibilityNodeInfo.EXTRA_DATA_RENDERING_INFO_KEY)
            && a11yExtraRenderingInfoColorAdditions()) {
        final AccessibilityNodeInfo.ExtraRenderingInfo.Builder builder =
                new AccessibilityNodeInfo.ExtraRenderingInfo.Builder();
        Drawable background = getBackground();
        if (background instanceof ColorDrawable backgroundColorDrawable) {
            builder.setBackgroundColor(backgroundColorDrawable.getColor());
        }
        builder.setAlpha(getAlpha());
        info.setExtraRenderingInfo(builder.build());
    }
}

private void populateAccessibilityNodeInfoDrawingOrderInParent(AccessibilityNodeInfo info) {

    if ((mPrivateFlags & PFLAG_HAS_BOUNDS) == 0) {
        info.setDrawingOrder(0);
        return;
    }
    int drawingOrderInParent = 1;
    View viewAtDrawingLevel = this;
    final ViewParent parent = getParentForAccessibility();
    while (viewAtDrawingLevel != parent) {
        final ViewParent currentParent = viewAtDrawingLevel.getParent();
        if (!(currentParent instanceof ViewGroup)) {
            drawingOrderInParent = 0;
            break;
        } else {
            final ViewGroup parentGroup = (ViewGroup) currentParent;
            final int childCount = parentGroup.getChildCount();
            if (childCount > 1) {
                List<View> preorderedList = parentGroup.buildOrderedChildList();
                if (preorderedList != null) {
                    final int childDrawIndex = preorderedList.indexOf(viewAtDrawingLevel);
                    for (int i = 0; i < childDrawIndex; i++) {
                        drawingOrderInParent += numViewsForAccessibility(preorderedList.get(i));
                    }
                    preorderedList.clear();
                } else {
                    final int childIndex = parentGroup.indexOfChild(viewAtDrawingLevel);
                    final boolean customOrder = parentGroup.isChildrenDrawingOrderEnabled();
                    final int childDrawIndex = ((childIndex >= 0) && customOrder) ? parentGroup
                            .getChildDrawingOrder(childCount, childIndex) : childIndex;
                    final int numChildrenToIterate = customOrder ? childCount : childDrawIndex;
                    if (childDrawIndex != 0) {
                        for (int i = 0; i < numChildrenToIterate; i++) {
                            final int otherDrawIndex = (customOrder ?
                                    parentGroup.getChildDrawingOrder(childCount, i) : i);
                            if (otherDrawIndex < childDrawIndex) {
                                drawingOrderInParent +=
                                        numViewsForAccessibility(parentGroup.getChildAt(i));
                            }
                        }
                    }
                }
            }
        }
        viewAtDrawingLevel = (View) currentParent;
    }
    info.setDrawingOrder(drawingOrderInParent);
}

private static int numViewsForAccessibility(View view) {
    if (view != null) {
        if (view.includeForAccessibility()) {
            return 1;
        } else if (view instanceof ViewGroup) {
            return ((ViewGroup) view).getNumChildrenForAccessibility();
        }
    }
    return 0;
}

private View findLabelForView(View view, int labeledId) {
    if (mMatchLabelForPredicate == null) {
        mMatchLabelForPredicate = new MatchLabelForPredicate();
    }
    mMatchLabelForPredicate.mLabeledId = labeledId;
    return findViewByPredicateInsideOut(view, mMatchLabelForPredicate);
}

public boolean isVisibleToUserForAutofill(int virtualId) {
    if (mContext.isAutofillCompatibilityEnabled()) {
        final AccessibilityNodeProvider provider = getAccessibilityNodeProvider();
        if (provider != null) {
            final AccessibilityNodeInfo node = provider.createAccessibilityNodeInfo(virtualId);
            if (node != null) {
                return node.isVisibleToUser();
            }
        } else {
            Log.w(VIEW_LOG_TAG, "isVisibleToUserForAutofill(" + virtualId + "): no provider");
        }
        return false;
    }
    return true;
}

@UnsupportedAppUsage
public boolean isVisibleToUser() {
    return isVisibleToUser(null);
}

@UnsupportedAppUsage(trackingBug = 171933273)
protected boolean isVisibleToUser(Rect boundInView) {
    if (mAttachInfo != null) {
        if (mAttachInfo.mWindowVisibility != View.VISIBLE) {
            return false;
        }
        Object current = this;
        while (current instanceof View) {
            View view = (View) current;
            if (view.getAlpha() <= 0 || view.getTransitionAlpha() <= 0 ||
                    view.getVisibility() != VISIBLE) {
                return false;
            }
            current = view.mParent;
        }
        Rect visibleRect = mAttachInfo.mTmpInvalRect;
        Point offset = mAttachInfo.mPoint;
        if (!getGlobalVisibleRect(visibleRect, offset)) {
            return false;
        }
        if (boundInView != null) {
            visibleRect.offset(-offset.x, -offset.y);
            return boundInView.intersect(visibleRect);
        }
        return true;
    }
    return false;
}

public AccessibilityDelegate getAccessibilityDelegate() {
    return mAccessibilityDelegate;
}

public void setAccessibilityDelegate(@Nullable AccessibilityDelegate delegate) {
    mAccessibilityDelegate = delegate;
}

public AccessibilityNodeProvider getAccessibilityNodeProvider() {
    if (mAccessibilityDelegate != null) {
        return mAccessibilityDelegate.getAccessibilityNodeProvider(this);
    } else {
        return null;
    }
}

@UnsupportedAppUsage
public int getAccessibilityViewId() {
    if (mAccessibilityViewId == NO_ID) {
        mAccessibilityViewId = sNextAccessibilityViewId++;
    }
    return mAccessibilityViewId;
}

public int getAutofillViewId() {
    if (mAutofillViewId == NO_ID) {
        mAutofillViewId = mContext.getNextAutofillId();
    }
    if (getAutofillViewIdFromAutofillManager()
            && mAutofillViewId <= LAST_APP_AUTOFILL_ID) {
        AutofillManager afm = getAutofillManager();
        if (afm != null) {
            int autofillViewId = afm.getNextAutofillViewId();
            if (autofillViewId > LAST_APP_AUTOFILL_ID) {
                if (DBG) {
                    Log.d(AUTOFILL_LOG_TAG, "getAutofillViewId(): Using autofill view id "
                            + "created from autofill manager");
                }
                mAutofillViewId = autofillViewId;
            }
        }
    }

    return mAutofillViewId;
}

public int getAccessibilityWindowId() {
    return mAttachInfo != null ? mAttachInfo.mAccessibilityWindowId
            : AccessibilityWindowInfo.UNDEFINED_WINDOW_ID;
}

@ViewDebug.ExportedProperty(category = "accessibility")
public final @Nullable CharSequence getStateDescription() {
    return mStateDescription;
}

@ViewDebug.ExportedProperty(category = "accessibility")
@InspectableProperty
public CharSequence getContentDescription() {
    return mContentDescription;
}

@FlaggedApi(FLAG_SUPPLEMENTAL_DESCRIPTION)
@ViewDebug.ExportedProperty(category = "accessibility")
@InspectableProperty
@Nullable
public CharSequence getSupplementalDescription() {
    return mSupplementalDescription;
}

@RemotableViewMethod
public void setStateDescription(@Nullable CharSequence stateDescription) {
    if (mStateDescription == null) {
        if (stateDescription == null) {
            return;
        }
    } else if (mStateDescription.equals(stateDescription)) {
        return;
    }
    mStateDescription = stateDescription;
    if (!TextUtils.isEmpty(stateDescription)
            && getImportantForAccessibility() == IMPORTANT_FOR_ACCESSIBILITY_AUTO) {
        setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_YES);
    }
    if (AccessibilityManager.getInstance(mContext).isEnabled()) {
        AccessibilityEvent event = AccessibilityEvent.obtain();
        event.setEventType(AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED);
        event.setContentChangeTypes(AccessibilityEvent.CONTENT_CHANGE_TYPE_STATE_DESCRIPTION);
        sendAccessibilityEventUnchecked(event);
    }
}

@RemotableViewMethod
public void setContentDescription(CharSequence contentDescription) {
    if (mContentDescription == null) {
        if (contentDescription == null) {
            return;
        }
    } else if (mContentDescription.equals(contentDescription)) {
        return;
    }
    mContentDescription = contentDescription;
    final boolean nonEmptyDesc = contentDescription != null && contentDescription.length() > 0;
    if (nonEmptyDesc && getImportantForAccessibility() == IMPORTANT_FOR_ACCESSIBILITY_AUTO) {
        setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_YES);
        notifySubtreeAccessibilityStateChangedIfNeeded();
    } else {
        notifyViewAccessibilityStateChangedIfNeeded(
                AccessibilityEvent.CONTENT_CHANGE_TYPE_CONTENT_DESCRIPTION);
    }
}

@FlaggedApi(FLAG_SUPPLEMENTAL_DESCRIPTION)
@RemotableViewMethod
public void setSupplementalDescription(@Nullable CharSequence supplementalDescription) {
    if (mSupplementalDescription == null) {
        if (supplementalDescription == null) {
            return;
        }
    } else if (mSupplementalDescription.equals(supplementalDescription)) {
        return;
    }
    mSupplementalDescription = supplementalDescription;
    final boolean nonEmptyDesc = supplementalDescription != null
            && !supplementalDescription.isEmpty();
    if (nonEmptyDesc && getImportantForAccessibility() == IMPORTANT_FOR_ACCESSIBILITY_AUTO) {
        setImportantForAccessibility(IMPORTANT_FOR_ACCESSIBILITY_YES);
        notifySubtreeAccessibilityStateChangedIfNeeded();
    } else {
        notifyViewAccessibilityStateChangedIfNeeded(
                AccessibilityEvent.CONTENT_CHANGE_TYPE_SUPPLEMENTAL_DESCRIPTION);
    }
}

@RemotableViewMethod
public void setAccessibilityTraversalBefore(@IdRes int beforeId) {
    if (mAccessibilityTraversalBeforeId == beforeId) {
        return;
    }
    mAccessibilityTraversalBeforeId = beforeId;
    notifyViewAccessibilityStateChangedIfNeeded(
            AccessibilityEvent.CONTENT_CHANGE_TYPE_UNDEFINED);
}

@IdRes
@InspectableProperty
public int getAccessibilityTraversalBefore() {
    return mAccessibilityTraversalBeforeId;
}

@RemotableViewMethod
public void setAccessibilityTraversalAfter(@IdRes int afterId) {
    if (mAccessibilityTraversalAfterId == afterId) {
        return;
    }
    mAccessibilityTraversalAfterId = afterId;
    notifyViewAccessibilityStateChangedIfNeeded(
            AccessibilityEvent.CONTENT_CHANGE_TYPE_UNDEFINED);
}

@IdRes
@InspectableProperty
public int getAccessibilityTraversalAfter() {
    return mAccessibilityTraversalAfterId;
}

@IdRes
@ViewDebug.ExportedProperty(category = "accessibility")
@InspectableProperty
public int getLabelFor() {
    return mLabelForId;
}

@RemotableViewMethod
public void setLabelFor(@IdRes int id) {
    if (mLabelForId == id) {
        return;
    }
    mLabelForId = id;
    if (mLabelForId != View.NO_ID
            && mID == View.NO_ID) {
        mID = generateViewId();
    }
    notifyViewAccessibilityStateChangedIfNeeded(
            AccessibilityEvent.CONTENT_CHANGE_TYPE_UNDEFINED);
}

@CallSuper
@UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.R, trackingBug = 170729553)
protected void onFocusLost() {
    resetPressedState();
}

private void resetPressedState() {
    if ((mViewFlags & ENABLED_MASK) == DISABLED) {
        return;
    }

    if (isPressed()) {
        setPressed(false);

        if (!mHasPerformedLongPress) {
            removeLongPressCallback();
        }
    }
}

@ViewDebug.ExportedProperty(category = "focus")
@InspectableProperty(hasAttributeId = false)
public boolean isFocused() {
    return (mPrivateFlags & PFLAG_FOCUSED) != 0;
}

public View findFocus() {
    return (mPrivateFlags & PFLAG_FOCUSED) != 0 ? this : null;
}

@InspectableProperty(name = "isScrollContainer")
public boolean isScrollContainer() {
    return (mPrivateFlags & PFLAG_SCROLL_CONTAINER_ADDED) != 0;
}

public void setScrollContainer(boolean isScrollContainer) {
    if (isScrollContainer) {
        if (mAttachInfo != null && (mPrivateFlags&PFLAG_SCROLL_CONTAINER_ADDED) == 0) {
            mAttachInfo.mScrollContainers.add(this);
            mPrivateFlags |= PFLAG_SCROLL_CONTAINER_ADDED;
        }
        mPrivateFlags |= PFLAG_SCROLL_CONTAINER;
    } else {
        if ((mPrivateFlags&PFLAG_SCROLL_CONTAINER_ADDED) != 0) {
            mAttachInfo.mScrollContainers.remove(this);
        }
        mPrivateFlags &= ~(PFLAG_SCROLL_CONTAINER|PFLAG_SCROLL_CONTAINER_ADDED);
    }
}

@Deprecated
@DrawingCacheQuality
@InspectableProperty(enumMapping = {
        @EnumEntry(value = DRAWING_CACHE_QUALITY_LOW, name = "low"),
        @EnumEntry(value = DRAWING_CACHE_QUALITY_HIGH, name = "high"),
        @EnumEntry(value = DRAWING_CACHE_QUALITY_AUTO, name = "auto")
})
public int getDrawingCacheQuality() {
    return mViewFlags & DRAWING_CACHE_QUALITY_MASK;
}

@Deprecated
public void setDrawingCacheQuality(@DrawingCacheQuality int quality) {
    setFlags(quality, DRAWING_CACHE_QUALITY_MASK);
}

@InspectableProperty
public boolean getKeepScreenOn() {
    return (mViewFlags & KEEP_SCREEN_ON) != 0;
}

public void setKeepScreenOn(boolean keepScreenOn) {
    setFlags(keepScreenOn ? KEEP_SCREEN_ON : 0, KEEP_SCREEN_ON);
}

@IdRes
@InspectableProperty(name = "nextFocusLeft")
public int getNextFocusLeftId() {
    return mNextFocusLeftId;
}

public void setNextFocusLeftId(@IdRes int nextFocusLeftId) {
    mNextFocusLeftId = nextFocusLeftId;
}

@IdRes
@InspectableProperty(name = "nextFocusRight")
public int getNextFocusRightId() {
    return mNextFocusRightId;
}

public void setNextFocusRightId(@IdRes int nextFocusRightId) {
    mNextFocusRightId = nextFocusRightId;
}

@IdRes
@InspectableProperty(name = "nextFocusUp")
public int getNextFocusUpId() {
    return mNextFocusUpId;
}

public void setNextFocusUpId(@IdRes int nextFocusUpId) {
    mNextFocusUpId = nextFocusUpId;
}

@IdRes
@InspectableProperty(name = "nextFocusDown")
public int getNextFocusDownId() {
    return mNextFocusDownId;
}

public void setNextFocusDownId(@IdRes int nextFocusDownId) {
    mNextFocusDownId = nextFocusDownId;
}

@IdRes
@InspectableProperty(name = "nextFocusForward")
public int getNextFocusForwardId() {
    return mNextFocusForwardId;
}

public void setNextFocusForwardId(@IdRes int nextFocusForwardId) {
    mNextFocusForwardId = nextFocusForwardId;
}

@IdRes
@InspectableProperty(name = "nextClusterForward")
public int getNextClusterForwardId() {
    return mNextClusterForwardId;
}

public void setNextClusterForwardId(@IdRes int nextClusterForwardId) {
    mNextClusterForwardId = nextClusterForwardId;
}

public boolean isShown() {
    View current = this;
    do {
        if ((current.mViewFlags & VISIBILITY_MASK) != VISIBLE) {
            return false;
        }
        ViewParent parent = current.mParent;
        if (parent == null) {
            return false; // We are not attached to the view root
        }
        if (!(parent instanceof View)) {
            return true;
        }
        current = (View) parent;
    } while (current != null);

    return false;
}

private boolean detached() {
    View current = this;
    do {
        if ((current.mPrivateFlags4 & PFLAG4_DETACHED) != 0) {
            return true;
        }
        ViewParent parent = current.mParent;
        if (parent == null) {
            return false;
        }
        if (!(parent instanceof View)) {
            return false;
        }
        current = (View) parent;
    } while (current != null);

    return false;
}

@Deprecated
protected boolean fitSystemWindows(Rect insets) {
    if ((mPrivateFlags3 & PFLAG3_APPLYING_INSETS) == 0) {
        if (insets == null) {
            return false;
        }
        try {
            mPrivateFlags3 |= PFLAG3_FITTING_SYSTEM_WINDOWS;
            return dispatchApplyWindowInsets(new WindowInsets(insets)).isConsumed();
        } finally {
            mPrivateFlags3 &= ~PFLAG3_FITTING_SYSTEM_WINDOWS;
        }
    } else {
        return fitSystemWindowsInt(insets);
    }
}

private boolean fitSystemWindowsInt(Rect insets) {
    if ((mViewFlags & FITS_SYSTEM_WINDOWS) == FITS_SYSTEM_WINDOWS) {
        Rect localInsets = sThreadLocal.get();
        boolean res = computeFitSystemWindows(insets, localInsets);
        applyInsets(localInsets);
        return res;
    }
    return false;
}

private void applyInsets(Rect insets) {
    mUserPaddingStart = UNDEFINED_PADDING;
    mUserPaddingEnd = UNDEFINED_PADDING;
    mUserPaddingLeftInitial = insets.left;
    mUserPaddingRightInitial = insets.right;
    internalSetPadding(insets.left, insets.top, insets.right, insets.bottom);
}

public WindowInsets onApplyWindowInsets(WindowInsets insets) {
    if ((mPrivateFlags4 & PFLAG4_FRAMEWORK_OPTIONAL_FITS_SYSTEM_WINDOWS) != 0
            && (mViewFlags & FITS_SYSTEM_WINDOWS) != 0) {
        return onApplyFrameworkOptionalFitSystemWindows(insets);
    }
    if ((mPrivateFlags3 & PFLAG3_FITTING_SYSTEM_WINDOWS) == 0) {
        if (fitSystemWindows(insets.getSystemWindowInsetsAsRect())) {
            return insets.consumeSystemWindowInsets();
        }
    } else {
        if (fitSystemWindowsInt(insets.getSystemWindowInsetsAsRect())) {
            return insets.consumeSystemWindowInsets();
        }
    }
    return insets;
}

private WindowInsets onApplyFrameworkOptionalFitSystemWindows(WindowInsets insets) {
    Rect localInsets = sThreadLocal.get();
    WindowInsets result = computeSystemWindowInsets(insets, localInsets);
    applyInsets(localInsets);
    return result;
}

public void setOnApplyWindowInsetsListener(OnApplyWindowInsetsListener listener) {
    getListenerInfo().mOnApplyWindowInsetsListener = listener;
}

public WindowInsets dispatchApplyWindowInsets(WindowInsets insets) {
    try {
        mPrivateFlags3 |= PFLAG3_APPLYING_INSETS;
        if (mListenerInfo != null && mListenerInfo.mOnApplyWindowInsetsListener != null) {
            return mListenerInfo.mOnApplyWindowInsetsListener.onApplyWindowInsets(this, insets);
        } else {
            return onApplyWindowInsets(insets);
        }
    } finally {
        mPrivateFlags3 &= ~PFLAG3_APPLYING_INSETS;
    }
}

public void setWindowInsetsAnimationCallback(
        @Nullable WindowInsetsAnimation.Callback callback) {
    getListenerInfo().mWindowInsetsAnimationCallback = callback;
}

public boolean hasWindowInsetsAnimationCallback() {
    return getListenerInfo().mWindowInsetsAnimationCallback != null;
}

public void dispatchWindowInsetsAnimationPrepare(
        @NonNull WindowInsetsAnimation animation) {
    if (mListenerInfo != null && mListenerInfo.mWindowInsetsAnimationCallback != null) {
        mListenerInfo.mWindowInsetsAnimationCallback.onPrepare(animation);
    }
}

@NonNull
public Bounds dispatchWindowInsetsAnimationStart(
        @NonNull WindowInsetsAnimation animation, @NonNull Bounds bounds) {
    if (mListenerInfo != null && mListenerInfo.mWindowInsetsAnimationCallback != null) {
        return mListenerInfo.mWindowInsetsAnimationCallback.onStart(animation, bounds);
    }
    return bounds;
}

@NonNull
public WindowInsets dispatchWindowInsetsAnimationProgress(@NonNull WindowInsets insets,
        @NonNull List<WindowInsetsAnimation> runningAnimations) {
    if (mListenerInfo != null && mListenerInfo.mWindowInsetsAnimationCallback != null) {
        return mListenerInfo.mWindowInsetsAnimationCallback.onProgress(insets,
                runningAnimations);
    } else {
        return insets;
    }
}

public void dispatchWindowInsetsAnimationEnd(@NonNull WindowInsetsAnimation animation) {
    if (mListenerInfo != null && mListenerInfo.mWindowInsetsAnimationCallback != null) {
        mListenerInfo.mWindowInsetsAnimationCallback.onEnd(animation);
    }
}

public void setSystemGestureExclusionRects(@NonNull List<Rect> rects) {
    if (rects.isEmpty() && mListenerInfo == null) return;

    final ListenerInfo info = getListenerInfo();
    final boolean rectsChanged = !reduceChangedExclusionRectsMsgs()
            || !Objects.deepEquals(info.mSystemGestureExclusionRects, rects);
    if (info.mSystemGestureExclusionRects == null) {
        info.mSystemGestureExclusionRects = new ArrayList<>();
    }
    if (rectsChanged) {
        deepCopyRectsObjectRecycling(info.mSystemGestureExclusionRects, rects);
        updatePositionUpdateListener();
        postUpdate(this::updateSystemGestureExclusionRects);
    }
}

private void deepCopyRectsObjectRecycling(
        @NonNull ArrayList<Rect> dest, @NonNull List<Rect> src) {
    final int srcN = src.size();
    final int destN = dest.size();
    dest.ensureCapacity(srcN);
    for (int i = 0; i < srcN && i < destN; i++) {
        final Rect destVal = dest.get(i);
        final Rect srcVal = src.get(i);
        if (srcVal == null || destVal == null) {
            dest.set(i, Rect.copyOrNull(srcVal));
        } else {
            destVal.set(srcVal);
        }
    }
    for (int i = destN; i < srcN; i++) {
        dest.add(Rect.copyOrNull(src.get(i)));
    }
    for (int i = destN; i > srcN; i--) {
        dest.removeLast();
    }
}

private void updatePositionUpdateListener() {
    final ListenerInfo info = getListenerInfo();
    if (getSystemGestureExclusionRects().isEmpty()
            && collectPreferKeepClearRects().isEmpty()
            && collectUnrestrictedPreferKeepClearRects().isEmpty()
            && (info.mHandwritingArea == null || !shouldTrackHandwritingArea())) {
        if (info.mPositionUpdateListener != null) {
            mRenderNode.removePositionUpdateListener(info.mPositionUpdateListener);
            info.mPositionUpdateListener = null;
            info.mPositionChangedUpdate = null;
        }
    } else {
        if (info.mPositionUpdateListener == null) {
            info.mPositionChangedUpdate = () -> {
                updateSystemGestureExclusionRects();
                updateKeepClearRects();
                updateHandwritingArea();
            };
            info.mPositionUpdateListener = new RenderNode.PositionUpdateListener() {
                @Override
                public void positionChanged(long n, int l, int t, int r, int b) {
                    postUpdate(info.mPositionChangedUpdate);
                }

                @Override
                public void positionLost(long frameNumber) {
                    postUpdate(info.mPositionChangedUpdate);
                }
            };
            mRenderNode.addPositionUpdateListener(info.mPositionUpdateListener);
        }
    }
}

private void postUpdate(Runnable r) {
    final Handler h = getHandler();
    if (h != null) {
        h.postAtFrontOfQueue(r);
    }
}

void updateSystemGestureExclusionRects() {
    final AttachInfo ai = mAttachInfo;
    if (ai != null) {
        ai.mViewRootImpl.updateSystemGestureExclusionRectsForView(this);
    }
}

@NonNull
public List<Rect> getSystemGestureExclusionRects() {
    final ListenerInfo info = mListenerInfo;
    if (info != null) {
        final List<Rect> list = info.mSystemGestureExclusionRects;
        if (list != null) {
            return list;
        }
    }
    return Collections.emptyList();
}

public final void setPreferKeepClear(boolean preferKeepClear) {
    getListenerInfo().mPreferKeepClear = preferKeepClear;
    updatePositionUpdateListener();
    postUpdate(this::updateKeepClearRects);
}

public final boolean isPreferKeepClear() {
    return mListenerInfo != null && mListenerInfo.mPreferKeepClear;
}

public final void setPreferKeepClearRects(@NonNull List<Rect> rects) {
    final ListenerInfo info = getListenerInfo();
    final boolean rectsChanged = !reduceChangedExclusionRectsMsgs()
            || !Objects.deepEquals(info.mKeepClearRects, rects);
    if (info.mKeepClearRects == null) {
        info.mKeepClearRects = new ArrayList<>();
    }
    if (rectsChanged) {
        deepCopyRectsObjectRecycling(info.mKeepClearRects, rects);
        updatePositionUpdateListener();
        postUpdate(this::updateKeepClearRects);
    }
}

@NonNull
public final List<Rect> getPreferKeepClearRects() {
    final ListenerInfo info = mListenerInfo;
    if (info != null && info.mKeepClearRects != null) {
        return new ArrayList(info.mKeepClearRects);
    }

    return Collections.emptyList();
}

@SystemApi
@RequiresPermission(android.Manifest.permission.SET_UNRESTRICTED_KEEP_CLEAR_AREAS)
public final void setUnrestrictedPreferKeepClearRects(@NonNull List<Rect> rects) {
    final ListenerInfo info = getListenerInfo();
    final boolean rectsChanged = !reduceChangedExclusionRectsMsgs()
            || !Objects.deepEquals(info.mUnrestrictedKeepClearRects, rects);
    if (info.mUnrestrictedKeepClearRects == null) {
        info.mUnrestrictedKeepClearRects = new ArrayList<>();
    }
    if (rectsChanged) {
        deepCopyRectsObjectRecycling(info.mUnrestrictedKeepClearRects, rects);
        updatePositionUpdateListener();
        postUpdate(this::updateKeepClearRects);
    }
}

@SystemApi
@NonNull
public final List<Rect> getUnrestrictedPreferKeepClearRects() {
    final ListenerInfo info = mListenerInfo;
    if (info != null && info.mUnrestrictedKeepClearRects != null) {
        return new ArrayList(info.mUnrestrictedKeepClearRects);
    }

    return Collections.emptyList();
}

void updateKeepClearRects() {
    final AttachInfo ai = mAttachInfo;
    if (ai != null) {
        ai.mViewRootImpl.updateKeepClearRectsForView(this);
    }
}

@NonNull
List<Rect> collectPreferKeepClearRects() {
    ListenerInfo info = mListenerInfo;
    boolean keepClearForFocus = isFocused()
            && mViewConfiguration.isPreferKeepClearForFocusEnabled();
    boolean keepBoundsClear = (info != null && info.mPreferKeepClear) || keepClearForFocus;
    boolean hasCustomKeepClearRects = info != null && info.mKeepClearRects != null;

    if (!keepBoundsClear && !hasCustomKeepClearRects) {
        return Collections.emptyList();
    } else if (keepBoundsClear && !hasCustomKeepClearRects) {
        return Collections.singletonList(new Rect(0, 0, getWidth(), getHeight()));
    }

    final List<Rect> list = new ArrayList<>();
    if (keepBoundsClear) {
        list.add(new Rect(0, 0, getWidth(), getHeight()));
    }

    if (hasCustomKeepClearRects) {
        list.addAll(info.mKeepClearRects);
    }

    return list;
}

private void updatePreferKeepClearForFocus() {
    if (mViewConfiguration.isPreferKeepClearForFocusEnabled()) {
        updatePositionUpdateListener();
        post(this::updateKeepClearRects);
    }
}

@NonNull
List<Rect> collectUnrestrictedPreferKeepClearRects() {
    final ListenerInfo info = mListenerInfo;
    if (info != null && info.mUnrestrictedKeepClearRects != null) {
        return info.mUnrestrictedKeepClearRects;
    }

    return Collections.emptyList();
}

public void setHandwritingBoundsOffsets(float offsetLeft, float offsetTop,
        float offsetRight, float offsetBottom) {
    mHandwritingBoundsOffsetLeft = offsetLeft;
    mHandwritingBoundsOffsetTop = offsetTop;
    mHandwritingBoundsOffsetRight = offsetRight;
    mHandwritingBoundsOffsetBottom = offsetBottom;
}

public float getHandwritingBoundsOffsetLeft() {
    return mHandwritingBoundsOffsetLeft;
}

public float getHandwritingBoundsOffsetTop() {
    return mHandwritingBoundsOffsetTop;
}

public float getHandwritingBoundsOffsetRight() {
    return mHandwritingBoundsOffsetRight;
}

public float getHandwritingBoundsOffsetBottom() {
    return mHandwritingBoundsOffsetBottom;
}

public void setHandwritingArea(@Nullable Rect rect) {
    final ListenerInfo info = getListenerInfo();
    info.mHandwritingArea = rect;
    updatePositionUpdateListener();
    postUpdate(this::updateHandwritingArea);
}

@Nullable
public Rect getHandwritingArea() {
    final ListenerInfo info = mListenerInfo;
    if (info != null && info.mHandwritingArea != null) {
        return new Rect(info.mHandwritingArea);
    }
    return null;
}

void updateHandwritingArea() {
    if (!shouldTrackHandwritingArea()) return;
    final AttachInfo ai = mAttachInfo;
    if (ai != null) {
        ai.mViewRootImpl.getHandwritingInitiator().updateHandwritingAreasForView(this);
    }
}

boolean shouldInitiateHandwriting() {
    return isAutoHandwritingEnabled() || getHandwritingDelegatorCallback() != null;
}

public boolean shouldTrackHandwritingArea() {
    return shouldInitiateHandwriting();
}

public void setHandwritingDelegatorCallback(@Nullable Runnable callback) {
    mHandwritingDelegatorCallback = callback;
    if (callback != null) {
        setHandwritingArea(new Rect(0, 0, getWidth(), getHeight()));
    }
}

@Nullable
public Runnable getHandwritingDelegatorCallback() {
    return mHandwritingDelegatorCallback;
}

public void setAllowedHandwritingDelegatePackage(@Nullable String allowedPackageName) {
    mAllowedHandwritingDelegatePackageName = allowedPackageName;
}

@Nullable
public String getAllowedHandwritingDelegatePackageName() {
    return mAllowedHandwritingDelegatePackageName;
}

public void setIsHandwritingDelegate(boolean isHandwritingDelegate) {
    mIsHandwritingDelegate = isHandwritingDelegate;
}

public boolean isHandwritingDelegate() {
    return mIsHandwritingDelegate;
}

public void setAllowedHandwritingDelegatorPackage(@Nullable String allowedPackageName) {
    mAllowedHandwritingDelegatorPackageName = allowedPackageName;
}

@Nullable
public String getAllowedHandwritingDelegatorPackageName() {
    return mAllowedHandwritingDelegatorPackageName;
}

@FlaggedApi(FLAG_HOME_SCREEN_HANDWRITING_DELEGATOR)
public void setHandwritingDelegateFlags(
        @InputMethodManager.HandwritingDelegateFlags int flags) {
    mHandwritingDelegateFlags = flags;
}

@FlaggedApi(FLAG_HOME_SCREEN_HANDWRITING_DELEGATOR)
public @InputMethodManager.HandwritingDelegateFlags int getHandwritingDelegateFlags() {
    return mHandwritingDelegateFlags;
}

public void getLocationInSurface(@NonNull @Size(2) int[] location) {
    getLocationInWindow(location);
    if (mAttachInfo != null && mAttachInfo.mViewRootImpl != null) {
        location[0] += mAttachInfo.mViewRootImpl.mWindowAttributes.surfaceInsets.left;
        location[1] += mAttachInfo.mViewRootImpl.mWindowAttributes.surfaceInsets.top;
    }
}

public WindowInsets getRootWindowInsets() {
    if (mAttachInfo != null) {
        return mAttachInfo.mViewRootImpl.getWindowInsets(false );
    }
    return null;
}

public @Nullable WindowInsetsController getWindowInsetsController() {
    if (mAttachInfo != null) {
        return mAttachInfo.mViewRootImpl.getInsetsController();
    }
    ViewParent parent = getParent();
    if (parent instanceof View) {
        return ((View) parent).getWindowInsetsController();
    } else if (parent instanceof ViewRootImpl) {
        return ((ViewRootImpl) parent).getInsetsController();
    }
    return null;
}

@Nullable
public final OnBackInvokedDispatcher findOnBackInvokedDispatcher() {
    ViewParent parent = getParent();
    if (parent != null) {
        return parent.findOnBackInvokedDispatcherForChild(this, this);
    }
    return null;
}

@Deprecated
@UnsupportedAppUsage
protected boolean computeFitSystemWindows(Rect inoutInsets, Rect outLocalInsets) {
    WindowInsets innerInsets = computeSystemWindowInsets(new WindowInsets(inoutInsets),
            outLocalInsets);
    inoutInsets.set(innerInsets.getSystemWindowInsetsAsRect());
    return innerInsets.isSystemWindowInsetsConsumed();
}

public WindowInsets computeSystemWindowInsets(WindowInsets in, Rect outLocalInsets) {
    boolean isOptionalFitSystemWindows = (mViewFlags & OPTIONAL_FITS_SYSTEM_WINDOWS) != 0
            || (mPrivateFlags4 & PFLAG4_FRAMEWORK_OPTIONAL_FITS_SYSTEM_WINDOWS) != 0;
    if (isOptionalFitSystemWindows && mAttachInfo != null) {
        OnContentApplyWindowInsetsListener listener =
                mAttachInfo.mContentOnApplyWindowInsetsListener;
        if (listener == null) {
            outLocalInsets.setEmpty();
            return in;
        }
        Pair<Insets, WindowInsets> result = listener.onContentApplyWindowInsets(this, in);
        outLocalInsets.set(result.first.toRect());
        return result.second;
    } else {
        outLocalInsets.set(in.getSystemWindowInsetsAsRect());
        return in.consumeSystemWindowInsets().inset(outLocalInsets);
    }
}

protected boolean hasContentOnApplyWindowInsetsListener() {
    return mAttachInfo != null && mAttachInfo.mContentOnApplyWindowInsetsListener != null;
}

public void setFitsSystemWindows(boolean fitSystemWindows) {
    setFlags(fitSystemWindows ? FITS_SYSTEM_WINDOWS : 0, FITS_SYSTEM_WINDOWS);
}

@ViewDebug.ExportedProperty
@InspectableProperty
public boolean getFitsSystemWindows() {
    return (mViewFlags & FITS_SYSTEM_WINDOWS) == FITS_SYSTEM_WINDOWS;
}

@UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.R, trackingBug = 170729553)
public boolean fitsSystemWindows() {
    return getFitsSystemWindows();
}

@Deprecated
public void requestFitSystemWindows() {
    if (mParent != null) {
        mParent.requestFitSystemWindows();
    }
}

public void requestApplyInsets() {
    requestFitSystemWindows();
}

@UnsupportedAppUsage
public void makeOptionalFitsSystemWindows() {
    setFlags(OPTIONAL_FITS_SYSTEM_WINDOWS, OPTIONAL_FITS_SYSTEM_WINDOWS);
}

public void makeFrameworkOptionalFitsSystemWindows() {
    mPrivateFlags4 |= PFLAG4_FRAMEWORK_OPTIONAL_FITS_SYSTEM_WINDOWS;
}

public boolean isFrameworkOptionalFitsSystemWindows() {
    return (mPrivateFlags4 & PFLAG4_FRAMEWORK_OPTIONAL_FITS_SYSTEM_WINDOWS) != 0;
}

@ViewDebug.ExportedProperty(mapping = {
    @ViewDebug.IntToString(from = VISIBLE,   to = "VISIBLE"),
    @ViewDebug.IntToString(from = INVISIBLE, to = "INVISIBLE"),
    @ViewDebug.IntToString(from = GONE,      to = "GONE")
})
@InspectableProperty(enumMapping = {
        @EnumEntry(value = VISIBLE, name = "visible"),
        @EnumEntry(value = INVISIBLE, name = "invisible"),
        @EnumEntry(value = GONE, name = "gone")
})
@Visibility
public int getVisibility() {
    return mViewFlags & VISIBILITY_MASK;
}

@RemotableViewMethod
public void setVisibility(@Visibility int visibility) {
    setFlags(visibility, VISIBILITY_MASK);
}

@ViewDebug.ExportedProperty
@InspectableProperty
public boolean isEnabled() {
    return (mViewFlags & ENABLED_MASK) == ENABLED;
}

@RemotableViewMethod
public void setEnabled(boolean enabled) {
    if (enabled == isEnabled()) return;

    setFlags(enabled ? ENABLED : DISABLED, ENABLED_MASK);

    refreshDrawableState();
    invalidate(true);

    if (!enabled) {
        cancelPendingInputEvents();
    }
    notifyViewAccessibilityStateChangedIfNeeded(
            AccessibilityEvent.CONTENT_CHANGE_TYPE_ENABLED);
}

@RemotableViewMethod
public void setFocusable(boolean focusable) {
    setFocusable(focusable ? FOCUSABLE : NOT_FOCUSABLE);
}

@RemotableViewMethod
public void setFocusable(@Focusable int focusable) {
    if ((focusable & (FOCUSABLE_AUTO | FOCUSABLE)) == 0) {
        setFlags(0, FOCUSABLE_IN_TOUCH_MODE);
    }
    setFlags(focusable, FOCUSABLE_MASK);
}

@RemotableViewMethod
public void setFocusableInTouchMode(boolean focusableInTouchMode) {
    setFlags(focusableInTouchMode ? FOCUSABLE_IN_TOUCH_MODE : 0, FOCUSABLE_IN_TOUCH_MODE);
    if (focusableInTouchMode) {
        setFlags(FOCUSABLE, FOCUSABLE_MASK);
    }
}

public void setAutofillHints(@Nullable String... autofillHints) {
    if (autofillHints == null || autofillHints.length == 0) {
        mAutofillHints = null;
    } else {
        mAutofillHints = autofillHints;
    }
    if (sensitiveContentAppProtection()) {
        if (getContentSensitivity() == CONTENT_SENSITIVITY_AUTO) {
            updateSensitiveViewsCountIfNeeded(isAggregatedVisible());
        }
    }
}

@TestApi
public void setAutofilled(boolean isAutofilled, boolean hideHighlight) {
    boolean wasChanged = isAutofilled != isAutofilled();

    if (wasChanged) {
        if (isAutofilled) {
            mPrivateFlags3 |= PFLAG3_IS_AUTOFILLED;
        } else {
            mPrivateFlags3 &= ~PFLAG3_IS_AUTOFILLED;
        }

        if (hideHighlight) {
            mPrivateFlags4 |= PFLAG4_AUTOFILL_HIDE_HIGHLIGHT;
        } else {
            mPrivateFlags4 &= ~PFLAG4_AUTOFILL_HIDE_HIGHLIGHT;
        }

        invalidate();
    }
}

public void setSoundEffectsEnabled(boolean soundEffectsEnabled) {
    setFlags(soundEffectsEnabled ? SOUND_EFFECTS_ENABLED: 0, SOUND_EFFECTS_ENABLED);
}

@ViewDebug.ExportedProperty
@InspectableProperty
public boolean isSoundEffectsEnabled() {
    return SOUND_EFFECTS_ENABLED == (mViewFlags & SOUND_EFFECTS_ENABLED);
}

public void setHapticFeedbackEnabled(boolean hapticFeedbackEnabled) {
    setFlags(hapticFeedbackEnabled ? HAPTIC_FEEDBACK_ENABLED: 0, HAPTIC_FEEDBACK_ENABLED);
}

@ViewDebug.ExportedProperty
@InspectableProperty
public boolean isHapticFeedbackEnabled() {
    return HAPTIC_FEEDBACK_ENABLED == (mViewFlags & HAPTIC_FEEDBACK_ENABLED);
}

@ViewDebug.ExportedProperty(category = "layout", mapping = {
    @ViewDebug.IntToString(from = LAYOUT_DIRECTION_LTR,     to = "LTR"),
    @ViewDebug.IntToString(from = LAYOUT_DIRECTION_RTL,     to = "RTL"),
    @ViewDebug.IntToString(from = LAYOUT_DIRECTION_INHERIT, to = "INHERIT"),
    @ViewDebug.IntToString(from = LAYOUT_DIRECTION_LOCALE,  to = "LOCALE")
})
@InspectableProperty(hasAttributeId = false, enumMapping = {
        @EnumEntry(value = LAYOUT_DIRECTION_LTR, name = "ltr"),
        @EnumEntry(value = LAYOUT_DIRECTION_RTL, name = "rtl"),
        @EnumEntry(value = LAYOUT_DIRECTION_INHERIT, name = "inherit"),
        @EnumEntry(value = LAYOUT_DIRECTION_LOCALE, name = "locale")
})
@LayoutDir
public int getRawLayoutDirection() {
    return (mPrivateFlags2 & PFLAG2_LAYOUT_DIRECTION_MASK) >> PFLAG2_LAYOUT_DIRECTION_MASK_SHIFT;
}

@RemotableViewMethod
public void setLayoutDirection(@LayoutDir int layoutDirection) {
    if (getRawLayoutDirection() != layoutDirection) {
        mPrivateFlags2 &= ~PFLAG2_LAYOUT_DIRECTION_MASK;
        resetRtlProperties();
        mPrivateFlags2 |=
                ((layoutDirection << PFLAG2_LAYOUT_DIRECTION_MASK_SHIFT) & PFLAG2_LAYOUT_DIRECTION_MASK);
        resolveRtlPropertiesIfNeeded();
        requestLayout();
        invalidate(true);
    }
}

@ViewDebug.ExportedProperty(category = "layout", mapping = {
    @ViewDebug.IntToString(from = LAYOUT_DIRECTION_LTR, to = "RESOLVED_DIRECTION_LTR"),
    @ViewDebug.IntToString(from = LAYOUT_DIRECTION_RTL, to = "RESOLVED_DIRECTION_RTL")
})
@InspectableProperty(enumMapping = {
        @EnumEntry(value = LAYOUT_DIRECTION_LTR, name = "ltr"),
        @EnumEntry(value = LAYOUT_DIRECTION_RTL, name = "rtl")
})
@ResolvedLayoutDir
public int getLayoutDirection() {
    return ((mPrivateFlags2 & PFLAG2_LAYOUT_DIRECTION_RESOLVED_RTL) ==
            PFLAG2_LAYOUT_DIRECTION_RESOLVED_RTL) ? LAYOUT_DIRECTION_RTL : LAYOUT_DIRECTION_LTR;
}

@ViewDebug.ExportedProperty(category = "layout")
@UnsupportedAppUsage
public boolean isLayoutRtl() {
    return (getLayoutDirection() == LAYOUT_DIRECTION_RTL);
}

@ViewDebug.ExportedProperty(category = "layout")
public boolean hasTransientState() {
    return (mPrivateFlags2 & PFLAG2_HAS_TRANSIENT_STATE) == PFLAG2_HAS_TRANSIENT_STATE;
}

public void setHasTransientState(boolean hasTransientState) {
    final boolean oldHasTransientState = hasTransientState();
    mTransientStateCount = hasTransientState ? mTransientStateCount + 1 :
            mTransientStateCount - 1;
    if (mTransientStateCount < 0) {
        mTransientStateCount = 0;
        Log.e(VIEW_LOG_TAG, "hasTransientState decremented below 0: " +
                "unmatched pair of setHasTransientState calls");
    } else if ((hasTransientState && mTransientStateCount == 1) ||
            (!hasTransientState && mTransientStateCount == 0)) {
        mPrivateFlags2 = (mPrivateFlags2 & ~PFLAG2_HAS_TRANSIENT_STATE) |
                (hasTransientState ? PFLAG2_HAS_TRANSIENT_STATE : 0);
        final boolean newHasTransientState = hasTransientState();
        if (mParent != null && newHasTransientState != oldHasTransientState) {
            try {
                mParent.childHasTransientStateChanged(this, newHasTransientState);
            } catch (AbstractMethodError e) {
                Log.e(VIEW_LOG_TAG, mParent.getClass().getSimpleName() +
                        " does not fully implement ViewParent", e);
            }
        }
    }
}

public void setHasTranslationTransientState(boolean hasTranslationTransientState) {
    if (hasTranslationTransientState) {
        mPrivateFlags4 |= PFLAG4_HAS_TRANSLATION_TRANSIENT_STATE;
    } else {
        mPrivateFlags4 &= ~PFLAG4_HAS_TRANSLATION_TRANSIENT_STATE;
    }
}

public boolean hasTranslationTransientState() {
    return (mPrivateFlags4 & PFLAG4_HAS_TRANSLATION_TRANSIENT_STATE)
            == PFLAG4_HAS_TRANSLATION_TRANSIENT_STATE;
}

public void clearTranslationState() {
    if (mViewTranslationCallback != null) {
        mViewTranslationCallback.onClearTranslation(this);
    }
    clearViewTranslationResponse();
    if (hasTranslationTransientState()) {
        setHasTransientState(false);
        setHasTranslationTransientState(false);
    }
}

public boolean isAttachedToWindow() {
    return mAttachInfo != null;
}

public boolean isLaidOut() {
    return (mPrivateFlags3 & PFLAG3_IS_LAID_OUT) == PFLAG3_IS_LAID_OUT;
}

boolean isLayoutValid() {
    return isLaidOut() && ((mPrivateFlags & PFLAG_FORCE_LAYOUT) == 0);
}

public void setWillNotDraw(boolean willNotDraw) {
    setFlags(willNotDraw ? WILL_NOT_DRAW : 0, DRAW_MASK);
}

@ViewDebug.ExportedProperty(category = "drawing")
public boolean willNotDraw() {
    return (mViewFlags & DRAW_MASK) == WILL_NOT_DRAW;
}

@Deprecated
public void setWillNotCacheDrawing(boolean willNotCacheDrawing) {
    setFlags(willNotCacheDrawing ? WILL_NOT_CACHE_DRAWING : 0, WILL_NOT_CACHE_DRAWING);
}

@ViewDebug.ExportedProperty(category = "drawing")
@Deprecated
public boolean willNotCacheDrawing() {
    return (mViewFlags & WILL_NOT_CACHE_DRAWING) == WILL_NOT_CACHE_DRAWING;
}

@ViewDebug.ExportedProperty
@InspectableProperty
public boolean isClickable() {
    return (mViewFlags & CLICKABLE) == CLICKABLE;
}

public void setClickable(boolean clickable) {
    setFlags(clickable ? CLICKABLE : 0, CLICKABLE);
}

public void setAllowClickWhenDisabled(boolean clickableWhenDisabled) {
    if (clickableWhenDisabled) {
        mPrivateFlags4 |= PFLAG4_ALLOW_CLICK_WHEN_DISABLED;
    } else {
        mPrivateFlags4 &= ~PFLAG4_ALLOW_CLICK_WHEN_DISABLED;
    }
}

@InspectableProperty
public boolean isLongClickable() {
    return (mViewFlags & LONG_CLICKABLE) == LONG_CLICKABLE;
}

public void setLongClickable(boolean longClickable) {
    setFlags(longClickable ? LONG_CLICKABLE : 0, LONG_CLICKABLE);
}

@InspectableProperty
public boolean isContextClickable() {
    return (mViewFlags & CONTEXT_CLICKABLE) == CONTEXT_CLICKABLE;
}

public void setContextClickable(boolean contextClickable) {
    setFlags(contextClickable ? CONTEXT_CLICKABLE : 0, CONTEXT_CLICKABLE);
}

private void setPressed(boolean pressed, float x, float y) {
    if (pressed) {
        drawableHotspotChanged(x, y);
    }

    setPressed(pressed);
}

public void setPressed(boolean pressed) {
    final boolean needsRefresh = pressed != ((mPrivateFlags & PFLAG_PRESSED) == PFLAG_PRESSED);

    if (pressed) {
        mPrivateFlags |= PFLAG_PRESSED;
    } else {
        mPrivateFlags &= ~PFLAG_PRESSED;
    }

    if (needsRefresh) {
        refreshDrawableState();
    }
    dispatchSetPressed(pressed);
}

protected void dispatchSetPressed(boolean pressed) {
}

@ViewDebug.ExportedProperty
@InspectableProperty(hasAttributeId = false)
public boolean isPressed() {
    return (mPrivateFlags & PFLAG_PRESSED) == PFLAG_PRESSED;
}

public boolean isAssistBlocked() {
    return (mPrivateFlags3 & PFLAG3_ASSIST_BLOCKED) != 0;
}

@UnsupportedAppUsage
public void setAssistBlocked(boolean enabled) {
    if (enabled) {
        mPrivateFlags3 |= PFLAG3_ASSIST_BLOCKED;
    } else {
        mPrivateFlags3 &= ~PFLAG3_ASSIST_BLOCKED;
    }
}

@InspectableProperty
public boolean isSaveEnabled() {
    return (mViewFlags & SAVE_DISABLED_MASK) != SAVE_DISABLED;
}

public void setSaveEnabled(boolean enabled) {
    setFlags(enabled ? 0 : SAVE_DISABLED, SAVE_DISABLED_MASK);
}

@ViewDebug.ExportedProperty
@InspectableProperty
public boolean getFilterTouchesWhenObscured() {
    return (mViewFlags & FILTER_TOUCHES_WHEN_OBSCURED) != 0;
}

public void setFilterTouchesWhenObscured(boolean enabled) {
    setFlags(enabled ? FILTER_TOUCHES_WHEN_OBSCURED : 0,
            FILTER_TOUCHES_WHEN_OBSCURED);
    calculateAccessibilityDataSensitive();
}

public boolean isSaveFromParentEnabled() {
    return (mViewFlags & PARENT_SAVE_DISABLED_MASK) != PARENT_SAVE_DISABLED;
}

public void setSaveFromParentEnabled(boolean enabled) {
    setFlags(enabled ? 0 : PARENT_SAVE_DISABLED, PARENT_SAVE_DISABLED_MASK);
}

@ViewDebug.ExportedProperty(category = "focus")
public final boolean isFocusable() {
    return FOCUSABLE == (mViewFlags & FOCUSABLE);
}

@ViewDebug.ExportedProperty(mapping = {
        @ViewDebug.IntToString(from = NOT_FOCUSABLE, to = "NOT_FOCUSABLE"),
        @ViewDebug.IntToString(from = FOCUSABLE, to = "FOCUSABLE"),
        @ViewDebug.IntToString(from = FOCUSABLE_AUTO, to = "FOCUSABLE_AUTO")
        }, category = "focus")
@InspectableProperty(enumMapping = {
        @EnumEntry(value = NOT_FOCUSABLE, name = "false"),
        @EnumEntry(value = FOCUSABLE, name = "true"),
        @EnumEntry(value = FOCUSABLE_AUTO, name = "auto")
})
@Focusable
public int getFocusable() {
    return (mViewFlags & FOCUSABLE_AUTO) > 0 ? FOCUSABLE_AUTO : mViewFlags & FOCUSABLE;
}

@ViewDebug.ExportedProperty(category = "focus")
@InspectableProperty
public final boolean isFocusableInTouchMode() {
    return FOCUSABLE_IN_TOUCH_MODE == (mViewFlags & FOCUSABLE_IN_TOUCH_MODE);
}

@InspectableProperty
public boolean isScreenReaderFocusable() {
    return (mPrivateFlags3 & PFLAG3_SCREEN_READER_FOCUSABLE) != 0;
}

public void setScreenReaderFocusable(boolean screenReaderFocusable) {
    updatePflags3AndNotifyA11yIfChanged(PFLAG3_SCREEN_READER_FOCUSABLE, screenReaderFocusable);
}

@InspectableProperty
public boolean isAccessibilityHeading() {
    return (mPrivateFlags3 & PFLAG3_ACCESSIBILITY_HEADING) != 0;
}

public void setAccessibilityHeading(boolean isHeading) {
    updatePflags3AndNotifyA11yIfChanged(PFLAG3_ACCESSIBILITY_HEADING, isHeading);
}

private void updatePflags3AndNotifyA11yIfChanged(int mask, boolean newValue) {
    int pflags3 = mPrivateFlags3;
    if (newValue) {
        pflags3 |= mask;
    } else {
        pflags3 &= ~mask;
    }

    if (pflags3 != mPrivateFlags3) {
        mPrivateFlags3 = pflags3;
        notifyViewAccessibilityStateChangedIfNeeded(
                AccessibilityEvent.CONTENT_CHANGE_TYPE_UNDEFINED);
    }
}

public View focusSearch(@FocusRealDirection int direction) {
    if (mParent != null) {
        return mParent.focusSearch(this, direction);
    } else {
        return null;
    }
}

@ViewDebug.ExportedProperty(category = "focus")
@InspectableProperty
public final boolean isKeyboardNavigationCluster() {
    return (mPrivateFlags3 & PFLAG3_CLUSTER) != 0;
}

View findKeyboardNavigationCluster() {
    if (mParent instanceof View) {
        View cluster = ((View) mParent).findKeyboardNavigationCluster();
        if (cluster != null) {
            return cluster;
        } else if (isKeyboardNavigationCluster()) {
            return this;
        }
    }
    return null;
}

public void setKeyboardNavigationCluster(boolean isCluster) {
    if (isCluster) {
        mPrivateFlags3 |= PFLAG3_CLUSTER;
    } else {
        mPrivateFlags3 &= ~PFLAG3_CLUSTER;
    }
}

@TestApi
public final void setFocusedInCluster() {
    setFocusedInCluster(findKeyboardNavigationCluster());
}

private void setFocusedInCluster(View cluster) {
    if (this instanceof ViewGroup) {
        ((ViewGroup) this).mFocusedInCluster = null;
    }
    if (cluster == this) {
        return;
    }
    ViewParent parent = mParent;
    View child = this;
    while (parent instanceof ViewGroup) {
        ((ViewGroup) parent).mFocusedInCluster = child;
        if (parent == cluster) {
            break;
        }
        child = (View) parent;
        parent = parent.getParent();
    }
}

private void updateFocusedInCluster(View oldFocus, @FocusDirection int direction) {
    if (oldFocus != null) {
        View oldCluster = oldFocus.findKeyboardNavigationCluster();
        View cluster = findKeyboardNavigationCluster();
        if (oldCluster != cluster) {
            oldFocus.setFocusedInCluster(oldCluster);
            if (!(oldFocus.mParent instanceof ViewGroup)) {
                return;
            }
            if (direction == FOCUS_FORWARD || direction == FOCUS_BACKWARD) {
                ((ViewGroup) oldFocus.mParent).clearFocusedInCluster(oldFocus);
            } else if (oldFocus instanceof ViewGroup
                    && ((ViewGroup) oldFocus).getDescendantFocusability()
                            == ViewGroup.FOCUS_AFTER_DESCENDANTS
                    && ViewRootImpl.isViewDescendantOf(this, oldFocus)) {
                ((ViewGroup) oldFocus.mParent).clearFocusedInCluster(oldFocus);
            }
        }
    }
}

@ViewDebug.ExportedProperty(category = "focus")
@InspectableProperty
public final boolean isFocusedByDefault() {
    return (mPrivateFlags3 & PFLAG3_FOCUSED_BY_DEFAULT) != 0;
}

@RemotableViewMethod
public void setFocusedByDefault(boolean isFocusedByDefault) {
    if (isFocusedByDefault == ((mPrivateFlags3 & PFLAG3_FOCUSED_BY_DEFAULT) != 0)) {
        return;
    }

    if (isFocusedByDefault) {
        mPrivateFlags3 |= PFLAG3_FOCUSED_BY_DEFAULT;
    } else {
        mPrivateFlags3 &= ~PFLAG3_FOCUSED_BY_DEFAULT;
    }

    if (mParent instanceof ViewGroup) {
        if (isFocusedByDefault) {
            ((ViewGroup) mParent).setDefaultFocus(this);
        } else {
            ((ViewGroup) mParent).clearDefaultFocus(this);
        }
    }
}

boolean hasDefaultFocus() {
    return isFocusedByDefault();
}

public View keyboardNavigationClusterSearch(View currentCluster,
        @FocusDirection int direction) {
    if (isKeyboardNavigationCluster()) {
        currentCluster = this;
    }
    if (isRootNamespace()) {
        return FocusFinder.getInstance().findNextKeyboardNavigationCluster(
                this, currentCluster, direction);
    } else if (mParent != null) {
        return mParent.keyboardNavigationClusterSearch(currentCluster, direction);
    }
    return null;
}

public boolean dispatchUnhandledMove(View focused, @FocusRealDirection int direction) {
    return false;
}

public void setDefaultFocusHighlightEnabled(boolean defaultFocusHighlightEnabled) {
    mDefaultFocusHighlightEnabled = defaultFocusHighlightEnabled;
}

@ViewDebug.ExportedProperty(category = "focus")
@InspectableProperty
public final boolean getDefaultFocusHighlightEnabled() {
    return mDefaultFocusHighlightEnabled;
}

View findUserSetNextFocus(View root, @FocusDirection int direction) {
    switch (direction) {
        case FOCUS_LEFT:
            if (mNextFocusLeftId == View.NO_ID) return null;
            return findViewInsideOutShouldExist(root, mNextFocusLeftId);
        case FOCUS_RIGHT:
            if (mNextFocusRightId == View.NO_ID) return null;
            return findViewInsideOutShouldExist(root, mNextFocusRightId);
        case FOCUS_UP:
            if (mNextFocusUpId == View.NO_ID) return null;
            return findViewInsideOutShouldExist(root, mNextFocusUpId);
        case FOCUS_DOWN:
            if (mNextFocusDownId == View.NO_ID) return null;
            return findViewInsideOutShouldExist(root, mNextFocusDownId);
        case FOCUS_FORWARD:
            if (mNextFocusForwardId == View.NO_ID) return null;
            return findViewInsideOutShouldExist(root, mNextFocusForwardId);
        case FOCUS_BACKWARD: {
            if (mID == View.NO_ID) return null;
            final View rootView = root;
            final View startView = this;
            return root.findViewByPredicateInsideOut(startView,
                t -> findViewInsideOutShouldExist(rootView, t, t.mNextFocusForwardId)
                        == startView);
        }
    }
    return null;
}

View findUserSetNextKeyboardNavigationCluster(View root, @FocusDirection int direction) {
    switch (direction) {
        case FOCUS_FORWARD:
            if (mNextClusterForwardId == View.NO_ID) return null;
            return findViewInsideOutShouldExist(root, mNextClusterForwardId);
        case FOCUS_BACKWARD: {
            if (mID == View.NO_ID) return null;
            final int id = mID;
            return root.findViewByPredicateInsideOut(this,
                    (Predicate<View>) t -> t.mNextClusterForwardId == id);
        }
    }
    return null;
}

private View findViewInsideOutShouldExist(View root, int id) {
    return findViewInsideOutShouldExist(root, this, id);
}

private View findViewInsideOutShouldExist(View root, View start, int id) {
    if (mMatchIdPredicate == null) {
        mMatchIdPredicate = new MatchIdPredicate();
    }
    mMatchIdPredicate.mId = id;
    View result = root.findViewByPredicateInsideOut(start, mMatchIdPredicate);
    if (result == null) {
        Log.w(VIEW_LOG_TAG, "couldn't find view with id " + id);
    }
    return result;
}

public ArrayList<View> getFocusables(@FocusDirection int direction) {
    ArrayList<View> result = new ArrayList<View>(24);
    addFocusables(result, direction);
    return result;
}

public void addFocusables(ArrayList<View> views, @FocusDirection int direction) {
    addFocusables(views, direction, isInTouchMode() ? FOCUSABLES_TOUCH_MODE : FOCUSABLES_ALL);
}

public void addFocusables(ArrayList<View> views, @FocusDirection int direction,
        @FocusableMode int focusableMode) {
    if (views == null) {
        return;
    }
    if (!canTakeFocus()) {
        return;
    }
    if ((focusableMode & FOCUSABLES_TOUCH_MODE) == FOCUSABLES_TOUCH_MODE
            && !isFocusableInTouchMode()) {
        return;
    }
    views.add(this);
}

public void addKeyboardNavigationClusters(
        @NonNull Collection<View> views,
        int direction) {
    if (!isKeyboardNavigationCluster()) {
        return;
    }
    if (!hasFocusable()) {
        return;
    }
    views.add(this);
}

public void findViewsWithText(ArrayList<View> outViews, CharSequence searched,
        @FindViewFlags int flags) {
    if (getAccessibilityNodeProvider() != null) {
        if ((flags & FIND_VIEWS_WITH_ACCESSIBILITY_NODE_PROVIDERS) != 0) {
            outViews.add(this);
        }
    } else if ((flags & FIND_VIEWS_WITH_CONTENT_DESCRIPTION) != 0
            && (searched != null && searched.length() > 0)
            && (mContentDescription != null && mContentDescription.length() > 0)) {
        String searchedLowerCase = searched.toString().toLowerCase();
        String contentDescriptionLowerCase = mContentDescription.toString().toLowerCase();
        if (contentDescriptionLowerCase.contains(searchedLowerCase)) {
            outViews.add(this);
        }
    }
}

public ArrayList<View> getTouchables() {
    ArrayList<View> result = new ArrayList<View>();
    addTouchables(result);
    return result;
}

public void addTouchables(ArrayList<View> views) {
    final int viewFlags = mViewFlags;

    if (((viewFlags & CLICKABLE) == CLICKABLE || (viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE
            || (viewFlags & CONTEXT_CLICKABLE) == CONTEXT_CLICKABLE)
            && (viewFlags & ENABLED_MASK) == ENABLED) {
        views.add(this);
    }
}

@InspectableProperty(hasAttributeId = false)
public boolean isAccessibilityFocused() {
    return (mPrivateFlags2 & PFLAG2_ACCESSIBILITY_FOCUSED) != 0;
}

@UnsupportedAppUsage
public boolean requestAccessibilityFocus() {
    AccessibilityManager manager = AccessibilityManager.getInstance(mContext);
    if (!manager.isEnabled() || !manager.isTouchExplorationEnabled()) {
        return false;
    }
    if ((mViewFlags & VISIBILITY_MASK) != VISIBLE) {
        return false;
    }
    if ((mPrivateFlags2 & PFLAG2_ACCESSIBILITY_FOCUSED) == 0) {
        mPrivateFlags2 |= PFLAG2_ACCESSIBILITY_FOCUSED;
        ViewRootImpl viewRootImpl = getViewRootImpl();
        if (viewRootImpl != null) {
            viewRootImpl.setAccessibilityFocus(this, null);
        }
        invalidate();
        sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_ACCESSIBILITY_FOCUSED);
        return true;
    }
    return false;
}

@UnsupportedAppUsage
public void clearAccessibilityFocus() {
    clearAccessibilityFocusNoCallbacks(0);
    final ViewRootImpl viewRootImpl = getViewRootImpl();
    if (viewRootImpl != null) {
        final View focusHost = viewRootImpl.getAccessibilityFocusedHost();
        if (focusHost != null && ViewRootImpl.isViewDescendantOf(focusHost, this)) {
            viewRootImpl.setAccessibilityFocus(null, null);
        }
    }
}

private void sendAccessibilityHoverEvent(int eventType) {
    View source = this;
    while (true) {
        if (source.includeForAccessibility(false)) {
            source.sendAccessibilityEvent(eventType);
            return;
        }
        ViewParent parent = source.getParent();
        if (parent instanceof View) {
            source = (View) parent;
        } else {
            return;
        }
    }
}

void clearAccessibilityFocusNoCallbacks(int action) {
    if ((mPrivateFlags2 & PFLAG2_ACCESSIBILITY_FOCUSED) != 0) {
        mPrivateFlags2 &= ~PFLAG2_ACCESSIBILITY_FOCUSED;
        invalidate();
        if (AccessibilityManager.getInstance(mContext).isEnabled()) {
            AccessibilityEvent event = AccessibilityEvent.obtain(
                    AccessibilityEvent.TYPE_VIEW_ACCESSIBILITY_FOCUS_CLEARED);
            event.setAction(action);
            if (mAccessibilityDelegate != null) {
                mAccessibilityDelegate.sendAccessibilityEventUnchecked(this, event);
            } else {
                sendAccessibilityEventUnchecked(event);
            }
        }

        updatePreferKeepClearForFocus();
    }
}

public final boolean requestFocus() {
    return requestFocus(View.FOCUS_DOWN);
}

@TestApi
public boolean restoreFocusInCluster(@FocusRealDirection int direction) {
    if (restoreDefaultFocus()) {
        return true;
    }
    return requestFocus(direction);
}

@TestApi
public boolean restoreFocusNotInCluster() {
    return requestFocus(View.FOCUS_DOWN);
}

public boolean restoreDefaultFocus() {
    return requestFocus(View.FOCUS_DOWN);
}

public final boolean requestFocus(int direction) {
    return requestFocus(direction, null);
}

public boolean requestFocus(int direction, Rect previouslyFocusedRect) {
    return requestFocusNoSearch(direction, previouslyFocusedRect);
}

private boolean requestFocusNoSearch(int direction, Rect previouslyFocusedRect) {
    if (!canTakeFocus()) {
        return false;
    }
    if (isInTouchMode() &&
        (FOCUSABLE_IN_TOUCH_MODE != (mViewFlags & FOCUSABLE_IN_TOUCH_MODE))) {
           return false;
    }
    if (hasAncestorThatBlocksDescendantFocus()) {
        return false;
    }

    if (!isLayoutValid()) {
        mPrivateFlags |= PFLAG_WANTS_FOCUS;
    } else {
        clearParentsWantFocus();
    }

    handleFocusGainInternal(direction, previouslyFocusedRect);
    return true;
}

void clearParentsWantFocus() {
    if (mParent instanceof View) {
        ((View) mParent).mPrivateFlags &= ~PFLAG_WANTS_FOCUS;
        ((View) mParent).clearParentsWantFocus();
    }
}

public final boolean requestFocusFromTouch() {
    if (isInTouchMode()) {
        ViewRootImpl viewRoot = getViewRootImpl();
        if (viewRoot != null) {
            viewRoot.ensureTouchMode(false);
        }
    }
    return requestFocus(View.FOCUS_DOWN);
}

private boolean hasAncestorThatBlocksDescendantFocus() {
    final boolean focusableInTouchMode = isFocusableInTouchMode();
    ViewParent ancestor = mParent;
    while (ancestor instanceof ViewGroup) {
        final ViewGroup vgAncestor = (ViewGroup) ancestor;
        if (vgAncestor.getDescendantFocusability() == ViewGroup.FOCUS_BLOCK_DESCENDANTS
                || (!focusableInTouchMode && vgAncestor.shouldBlockFocusForTouchscreen())) {
            return true;
        } else {
            ancestor = vgAncestor.getParent();
        }
    }
    return false;
}

@ViewDebug.ExportedProperty(category = "accessibility", mapping = {
        @ViewDebug.IntToString(from = IMPORTANT_FOR_ACCESSIBILITY_AUTO, to = "auto"),
        @ViewDebug.IntToString(from = IMPORTANT_FOR_ACCESSIBILITY_YES, to = "yes"),
        @ViewDebug.IntToString(from = IMPORTANT_FOR_ACCESSIBILITY_NO, to = "no"),
        @ViewDebug.IntToString(from = IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS,
                to = "noHideDescendants")
    })
@InspectableProperty(enumMapping = {
        @EnumEntry(value = IMPORTANT_FOR_ACCESSIBILITY_AUTO, name = "auto"),
        @EnumEntry(value = IMPORTANT_FOR_ACCESSIBILITY_YES, name = "yes"),
        @EnumEntry(value = IMPORTANT_FOR_ACCESSIBILITY_NO, name = "no"),
        @EnumEntry(value = IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS,
                name = "noHideDescendants"),
})
public int getImportantForAccessibility() {
    return (mPrivateFlags2 & PFLAG2_IMPORTANT_FOR_ACCESSIBILITY_MASK)
            >> PFLAG2_IMPORTANT_FOR_ACCESSIBILITY_SHIFT;
}

public void setAccessibilityLiveRegion(int mode) {
    if (mode != getAccessibilityLiveRegion()) {
        mPrivateFlags2 &= ~PFLAG2_ACCESSIBILITY_LIVE_REGION_MASK;
        mPrivateFlags2 |= (mode << PFLAG2_ACCESSIBILITY_LIVE_REGION_SHIFT)
                & PFLAG2_ACCESSIBILITY_LIVE_REGION_MASK;
        notifyViewAccessibilityStateChangedIfNeeded(
                AccessibilityEvent.CONTENT_CHANGE_TYPE_UNDEFINED);
    }
}

@InspectableProperty(enumMapping = {
        @EnumEntry(value = ACCESSIBILITY_LIVE_REGION_NONE, name = "none"),
        @EnumEntry(value = ACCESSIBILITY_LIVE_REGION_POLITE, name = "polite"),
        @EnumEntry(value = ACCESSIBILITY_LIVE_REGION_ASSERTIVE, name = "assertive")
})
public int getAccessibilityLiveRegion() {
    return (mPrivateFlags2 & PFLAG2_ACCESSIBILITY_LIVE_REGION_MASK)
            >> PFLAG2_ACCESSIBILITY_LIVE_REGION_SHIFT;
}

public void setImportantForAccessibility(int mode) {
    final int oldMode = getImportantForAccessibility();
    if (mode != oldMode) {
        final boolean hideDescendants =
                mode == IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS;
        if (mode == IMPORTANT_FOR_ACCESSIBILITY_NO || hideDescendants) {
            final View focusHost = findAccessibilityFocusHost(hideDescendants);
            if (focusHost != null) {
                focusHost.clearAccessibilityFocus();
            }
        }
        final boolean maySkipNotify = oldMode == IMPORTANT_FOR_ACCESSIBILITY_AUTO
                || mode == IMPORTANT_FOR_ACCESSIBILITY_AUTO;
        final boolean oldIncludeForAccessibility =
                maySkipNotify && includeForAccessibility(false);
        mPrivateFlags2 &= ~PFLAG2_IMPORTANT_FOR_ACCESSIBILITY_MASK;
        mPrivateFlags2 |= (mode << PFLAG2_IMPORTANT_FOR_ACCESSIBILITY_SHIFT)
                & PFLAG2_IMPORTANT_FOR_ACCESSIBILITY_MASK;
        if (!maySkipNotify || oldIncludeForAccessibility != includeForAccessibility(false)) {
            notifySubtreeAccessibilityStateChangedIfNeeded();
        } else {
            notifyViewAccessibilityStateChangedIfNeeded(
                    AccessibilityEvent.CONTENT_CHANGE_TYPE_UNDEFINED);
        }
    }
}

private View findAccessibilityFocusHost(boolean searchDescendants) {
    if (isAccessibilityFocusedViewOrHost()) {
        return this;
    }

    if (searchDescendants) {
        final ViewRootImpl viewRoot = getViewRootImpl();
        if (viewRoot != null) {
            final View focusHost = viewRoot.getAccessibilityFocusedHost();
            if (focusHost != null && ViewRootImpl.isViewDescendantOf(focusHost, this)) {
                return focusHost;
            }
        }
    }

    return null;
}

public boolean isImportantForAccessibility() {
    final int mode = getImportantForAccessibility();
    if (mode == IMPORTANT_FOR_ACCESSIBILITY_NO
            || mode == IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS) {
        return false;
    }
    ViewParent parent = mParent;
    while (parent instanceof View) {
        if (((View) parent).getImportantForAccessibility()
                == IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS) {
            return false;
        }
        parent = parent.getParent();
    }

    return mode == IMPORTANT_FOR_ACCESSIBILITY_YES || isActionableForAccessibility()
            || hasListenersForAccessibility() || getAccessibilityNodeProvider() != null
            || getAccessibilityDelegate() != null
            || getAccessibilityLiveRegion() != ACCESSIBILITY_LIVE_REGION_NONE
            || isAccessibilityPane() || isAccessibilityHeading();
}

public ViewParent getParentForAccessibility() {
    if (mParent instanceof View) {
        View parentView = (View) mParent;
        if (parentView.includeForAccessibility()) {
            return mParent;
        } else {
            return mParent.getParentForAccessibility();
        }
    }
    return null;
}

@Nullable
View getSelfOrParentImportantForA11y() {
    if (isImportantForAccessibility()) return this;
    ViewParent parent = getParentForAccessibility();
    if (parent instanceof View) return (View) parent;
    return null;
}

public void addChildrenForAccessibility(ArrayList<View> outChildren) {

}

@UnsupportedAppUsage
public boolean includeForAccessibility() {
    return includeForAccessibility(true);
}

public boolean includeForAccessibility(boolean considerDataSensitivity) {
    if (mAttachInfo == null) {
        return false;
    }

    if (considerDataSensitivity) {
        if (!AccessibilityManager.getInstance(mContext).isRequestFromAccessibilityTool()
                && isAccessibilityDataSensitive()) {
            return false;
        }
    }

    return (mAttachInfo.mAccessibilityFetchFlags
            & AccessibilityNodeInfo.FLAG_SERVICE_REQUESTS_INCLUDE_NOT_IMPORTANT_VIEWS) != 0
            || isImportantForAccessibility();
}

@ViewDebug.ExportedProperty(category = "accessibility")
public boolean isAccessibilityDataSensitive() {
    if (mInferredAccessibilityDataSensitive == ACCESSIBILITY_DATA_SENSITIVE_AUTO) {
        calculateAccessibilityDataSensitive();
    }
    return mInferredAccessibilityDataSensitive == ACCESSIBILITY_DATA_SENSITIVE_YES;
}

void calculateAccessibilityDataSensitive() {
    if (mExplicitAccessibilityDataSensitive != ACCESSIBILITY_DATA_SENSITIVE_AUTO) {
        mInferredAccessibilityDataSensitive = mExplicitAccessibilityDataSensitive;
    } else if (getFilterTouchesWhenObscured()) {
        mInferredAccessibilityDataSensitive = ACCESSIBILITY_DATA_SENSITIVE_YES;
    } else if (mParent instanceof View && ((View) mParent).isAccessibilityDataSensitive()) {
        mInferredAccessibilityDataSensitive = ACCESSIBILITY_DATA_SENSITIVE_YES;
    } else {
        mInferredAccessibilityDataSensitive = ACCESSIBILITY_DATA_SENSITIVE_NO;
    }
}

public void setAccessibilityDataSensitive(
        @AccessibilityDataSensitive int accessibilityDataSensitive) {
    mExplicitAccessibilityDataSensitive = accessibilityDataSensitive;
    calculateAccessibilityDataSensitive();
}

public boolean isActionableForAccessibility() {
    return (isClickable() || isLongClickable() || isFocusable() || isContextClickable()
            || isScreenReaderFocusable());
}

private boolean hasListenersForAccessibility() {
    ListenerInfo info = getListenerInfo();
    return mTouchDelegate != null || info.mOnKeyListener != null
            || info.mOnTouchListener != null || info.mOnGenericMotionListener != null
            || info.mOnHoverListener != null || info.mOnDragListener != null;
}

@UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.R, trackingBug = 170729553)
public void notifyViewAccessibilityStateChangedIfNeeded(int changeType) {
    if (!AccessibilityManager.getInstance(mContext).isEnabled() || mAttachInfo == null) {
        return;
    }
    if ((changeType != AccessibilityEvent.CONTENT_CHANGE_TYPE_SUBTREE)
            && (isAccessibilityPane()
            || (changeType == AccessibilityEvent.CONTENT_CHANGE_TYPE_PANE_DISAPPEARED)
            && isAggregatedVisible())) {
        if ((isAggregatedVisible())
                || (changeType == AccessibilityEvent.CONTENT_CHANGE_TYPE_PANE_DISAPPEARED)) {
            final AccessibilityEvent event = AccessibilityEvent.obtain();
            onInitializeAccessibilityEvent(event);
            event.setEventType(AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED);
            event.setContentChangeTypes(changeType);
            event.setSource(this);
            onPopulateAccessibilityEvent(event);
            if (mParent != null) {
                try {
                    mParent.requestSendAccessibilityEvent(this, event);
                } catch (AbstractMethodError e) {
                    Log.e(VIEW_LOG_TAG, mParent.getClass().getSimpleName()
                            + " does not fully implement ViewParent", e);
                }
            }
            return;
        }
    }
    if (getAccessibilityLiveRegion() != ACCESSIBILITY_LIVE_REGION_NONE) {
        final AccessibilityEvent event = AccessibilityEvent.obtain();
        event.setEventType(AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED);
        event.setContentChangeTypes(changeType);
        sendAccessibilityEventUnchecked(event);
    } else if (mParent != null) {
        try {
            mParent.notifySubtreeAccessibilityStateChanged(this, this, changeType);
        } catch (AbstractMethodError e) {
            Log.e(VIEW_LOG_TAG, mParent.getClass().getSimpleName() +
                    " does not fully implement ViewParent", e);
        }
    }
}

@UnsupportedAppUsage
public void notifySubtreeAccessibilityStateChangedIfNeeded() {
    if (!AccessibilityManager.getInstance(mContext).isEnabled() || mAttachInfo == null) {
        return;
    }

    if ((mPrivateFlags2 & PFLAG2_SUBTREE_ACCESSIBILITY_STATE_CHANGED) == 0) {
        mPrivateFlags2 |= PFLAG2_SUBTREE_ACCESSIBILITY_STATE_CHANGED;
        if (mParent != null) {
            try {
                mParent.notifySubtreeAccessibilityStateChanged(
                        this, this, AccessibilityEvent.CONTENT_CHANGE_TYPE_SUBTREE);
            } catch (AbstractMethodError e) {
                Log.e(VIEW_LOG_TAG, mParent.getClass().getSimpleName() +
                        " does not fully implement ViewParent", e);
            }
        }
    }
}

private void notifySubtreeAccessibilityStateChangedByParentIfNeeded() {
    if (!AccessibilityManager.getInstance(mContext).isEnabled()) {
        return;
    }

    final View sendA11yEventView = (View) getParentForAccessibility();
    if (sendA11yEventView != null && sendA11yEventView.isShown()) {
        sendA11yEventView.notifySubtreeAccessibilityStateChangedIfNeeded();
    }
}

public void setTransitionVisibility(@Visibility int visibility) {
    mViewFlags = (mViewFlags & ~View.VISIBILITY_MASK) | visibility;
}

void resetSubtreeAccessibilityStateChanged() {
    mPrivateFlags2 &= ~PFLAG2_SUBTREE_ACCESSIBILITY_STATE_CHANGED;
}

public boolean dispatchNestedPrePerformAccessibilityAction(int action,
        @Nullable Bundle arguments) {
    for (ViewParent p = getParent(); p != null; p = p.getParent()) {
        if (p.onNestedPrePerformAccessibilityAction(this, action, arguments)) {
            return true;
        }
    }
    return false;
}

public boolean performAccessibilityAction(int action, @Nullable Bundle arguments) {
  if (mAccessibilityDelegate != null) {
      return mAccessibilityDelegate.performAccessibilityAction(this, action, arguments);
  } else {
      return performAccessibilityActionInternal(action, arguments);
  }
}

@UnsupportedAppUsage
public boolean performAccessibilityActionInternal(int action, @Nullable Bundle arguments) {
    if (isNestedScrollingEnabled()
            && (action == AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD
            || action == AccessibilityNodeInfo.ACTION_SCROLL_FORWARD
            || action == R.id.accessibilityActionScrollUp
            || action == R.id.accessibilityActionScrollLeft
            || action == R.id.accessibilityActionScrollDown
            || action == R.id.accessibilityActionScrollRight)) {
        if (dispatchNestedPrePerformAccessibilityAction(action, arguments)) {
            return true;
        }
    }

    switch (action) {
        case AccessibilityNodeInfo.ACTION_CLICK: {
            if (isClickable()) {
                performClickInternal();
                return true;
            }
        } break;
        case AccessibilityNodeInfo.ACTION_LONG_CLICK: {
            if (isLongClickable()) {
                performLongClick();
                return true;
            }
        } break;
        case AccessibilityNodeInfo.ACTION_FOCUS: {
            if (!hasFocus()) {
                getViewRootImpl().ensureTouchMode(false);
                return requestFocus();
            }
        } break;
        case AccessibilityNodeInfo.ACTION_CLEAR_FOCUS: {
            if (hasFocus()) {
                clearFocus();
                return !isFocused();
            }
        } break;
        case AccessibilityNodeInfo.ACTION_SELECT: {
            if (!isSelected()) {
                setSelected(true);
                return isSelected();
            }
        } break;
        case AccessibilityNodeInfo.ACTION_CLEAR_SELECTION: {
            if (isSelected()) {
                setSelected(false);
                return !isSelected();
            }
        } break;
        case AccessibilityNodeInfo.ACTION_ACCESSIBILITY_FOCUS: {
            if (!isAccessibilityFocused()) {
                return requestAccessibilityFocus();
            }
        } break;
        case AccessibilityNodeInfo.ACTION_CLEAR_ACCESSIBILITY_FOCUS: {
            if (isAccessibilityFocused()) {
                clearAccessibilityFocus();
                return true;
            }
        } break;
        case AccessibilityNodeInfo.ACTION_NEXT_AT_MOVEMENT_GRANULARITY: {
            if (arguments != null) {
                final int granularity = arguments.getInt(
                        AccessibilityNodeInfo.ACTION_ARGUMENT_MOVEMENT_GRANULARITY_INT);
                final boolean extendSelection = arguments.getBoolean(
                        AccessibilityNodeInfo.ACTION_ARGUMENT_EXTEND_SELECTION_BOOLEAN);
                return traverseAtGranularity(granularity, true, extendSelection);
            }
        } break;
        case AccessibilityNodeInfo.ACTION_PREVIOUS_AT_MOVEMENT_GRANULARITY: {
            if (arguments != null) {
                final int granularity = arguments.getInt(
                        AccessibilityNodeInfo.ACTION_ARGUMENT_MOVEMENT_GRANULARITY_INT);
                final boolean extendSelection = arguments.getBoolean(
                        AccessibilityNodeInfo.ACTION_ARGUMENT_EXTEND_SELECTION_BOOLEAN);
                return traverseAtGranularity(granularity, false, extendSelection);
            }
        } break;
        case AccessibilityNodeInfo.ACTION_SET_SELECTION: {
            CharSequence text = getIterableTextForAccessibility();
            if (text == null) {
                return false;
            }
            final int start = (arguments != null) ? arguments.getInt(
                    AccessibilityNodeInfo.ACTION_ARGUMENT_SELECTION_START_INT, -1) : -1;
            final int end = (arguments != null) ? arguments.getInt(
            AccessibilityNodeInfo.ACTION_ARGUMENT_SELECTION_END_INT, -1) : -1;
            if ((getAccessibilitySelectionStart() != start
                    || getAccessibilitySelectionEnd() != end)
                    && (start == end)) {
                setAccessibilitySelection(start, end);
                notifyViewAccessibilityStateChangedIfNeeded(
                        AccessibilityEvent.CONTENT_CHANGE_TYPE_UNDEFINED);
                return true;
            }
        } break;
        case R.id.accessibilityActionShowOnScreen: {
            if (mAttachInfo != null) {
                final Rect r = mAttachInfo.mTmpInvalRect;
                getDrawingRect(r);
                return requestRectangleOnScreen(r,
                        true,
                        RECTANGLE_ON_SCREEN_REQUEST_SOURCE_UNDEFINED);
            }
        } break;
        case R.id.accessibilityActionContextClick: {
            if (isContextClickable()) {
                performContextClick();
                return true;
            }
        } break;
        case R.id.accessibilityActionShowTooltip: {
            if ((mTooltipInfo != null) && (mTooltipInfo.mTooltipPopup != null)) {
                return false;
            }
            return showLongClickTooltip(0, 0);
        }
        case R.id.accessibilityActionHideTooltip: {
            if ((mTooltipInfo == null) || (mTooltipInfo.mTooltipPopup == null)) {
                return false;
            }
            hideTooltip();
            return true;
        }
        case R.id.accessibilityActionDragDrop: {
            if (!canAcceptAccessibilityDrop()) {
                return false;
            }
            try {
                if (mAttachInfo != null && mAttachInfo.mSession != null) {
                    final int[] location = new int[2];
                    getLocationInWindow(location);
                    final int centerX = location[0] + getWidth() / 2;
                    final int centerY = location[1] + getHeight() / 2;
                    return mAttachInfo.mSession.dropForAccessibility(mAttachInfo.mWindow,
                            centerX, centerY);
                }
            } catch (RemoteException e) {
                Log.e(VIEW_LOG_TAG, "Unable to drop for accessibility", e);
            }
            return false;
        }
        case R.id.accessibilityActionDragCancel: {
            if (!startedSystemDragForAccessibility()) {
                return false;
            }
            if (mAttachInfo != null && mAttachInfo.mDragToken != null) {
                cancelDragAndDrop();
                return true;
            }
            return false;
        }
    }
    return false;
}

private boolean canAcceptAccessibilityDrop() {
    if (!canAcceptDrag()) {
        return false;
    }
    ListenerInfo li = mListenerInfo;
    return (li != null) && (li.mOnDragListener != null || li.mOnReceiveContentListener != null);
}

private boolean traverseAtGranularity(int granularity, boolean forward,
        boolean extendSelection) {
    CharSequence text = getIterableTextForAccessibility();
    if (text == null || text.length() == 0) {
        return false;
    }
    TextSegmentIterator iterator = getIteratorForGranularity(granularity);
    if (iterator == null) {
        return false;
    }
    int current = getAccessibilitySelectionEnd();
    if (current == ACCESSIBILITY_CURSOR_POSITION_UNDEFINED) {
        current = forward ? 0 : text.length();
    }
    final int[] range = forward ? iterator.following(current) : iterator.preceding(current);
    if (range == null) {
        return false;
    }
    final int segmentStart = range[0];
    final int segmentEnd = range[1];
    int selectionStart;
    int selectionEnd;
    if (extendSelection && isAccessibilitySelectionExtendable()) {
        prepareForExtendedAccessibilitySelection();
        selectionStart = getAccessibilitySelectionStart();
        if (selectionStart == ACCESSIBILITY_CURSOR_POSITION_UNDEFINED) {
            selectionStart = forward ? segmentStart : segmentEnd;
        }
        selectionEnd = forward ? segmentEnd : segmentStart;
    } else {
        selectionStart = selectionEnd= forward ? segmentEnd : segmentStart;
    }
    setAccessibilitySelection(selectionStart, selectionEnd);
    final int action = forward ? AccessibilityNodeInfo.ACTION_NEXT_AT_MOVEMENT_GRANULARITY
            : AccessibilityNodeInfo.ACTION_PREVIOUS_AT_MOVEMENT_GRANULARITY;
    sendViewTextTraversedAtGranularityEvent(action, granularity, segmentStart, segmentEnd);
    return true;
}

@UnsupportedAppUsage
public CharSequence getIterableTextForAccessibility() {
    return getContentDescription();
}

public boolean isAccessibilitySelectionExtendable() {
    return false;
}

public void prepareForExtendedAccessibilitySelection() {
    return;
}

public int getAccessibilitySelectionStart() {
    return mAccessibilityCursorPosition;
}

public int getAccessibilitySelectionEnd() {
    return getAccessibilitySelectionStart();
}

public void setAccessibilitySelection(int start, int end) {
    if (start ==  end && end == mAccessibilityCursorPosition) {
        return;
    }
    if (start >= 0 && start == end && end <= getIterableTextForAccessibility().length()) {
        mAccessibilityCursorPosition = start;
    } else {
        mAccessibilityCursorPosition = ACCESSIBILITY_CURSOR_POSITION_UNDEFINED;
    }
    sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_TEXT_SELECTION_CHANGED);
}

private void sendViewTextTraversedAtGranularityEvent(int action, int granularity,
        int fromIndex, int toIndex) {
    if (mParent == null) {
        return;
    }
    AccessibilityEvent event = AccessibilityEvent.obtain(
            AccessibilityEvent.TYPE_VIEW_TEXT_TRAVERSED_AT_MOVEMENT_GRANULARITY);
    onInitializeAccessibilityEvent(event);
    onPopulateAccessibilityEvent(event);
    event.setFromIndex(fromIndex);
    event.setToIndex(toIndex);
    event.setAction(action);
    event.setMovementGranularity(granularity);
    mParent.requestSendAccessibilityEvent(this, event);
}

@UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.R, trackingBug = 170729553)
public TextSegmentIterator getIteratorForGranularity(int granularity) {
    switch (granularity) {
        case AccessibilityNodeInfo.MOVEMENT_GRANULARITY_CHARACTER: {
            CharSequence text = getIterableTextForAccessibility();
            if (text != null && text.length() > 0) {
                CharacterTextSegmentIterator iterator =
                    CharacterTextSegmentIterator.getInstance(
                            mContext.getResources().getConfiguration().locale);
                iterator.initialize(text.toString());
                return iterator;
            }
        } break;
        case AccessibilityNodeInfo.MOVEMENT_GRANULARITY_WORD: {
            CharSequence text = getIterableTextForAccessibility();
            if (text != null && text.length() > 0) {
                WordTextSegmentIterator iterator =
                    WordTextSegmentIterator.getInstance(
                            mContext.getResources().getConfiguration().locale);
                iterator.initialize(text.toString());
                return iterator;
            }
        } break;
        case AccessibilityNodeInfo.MOVEMENT_GRANULARITY_PARAGRAPH: {
            CharSequence text = getIterableTextForAccessibility();
            if (text != null && text.length() > 0) {
                ParagraphTextSegmentIterator iterator =
                    ParagraphTextSegmentIterator.getInstance();
                iterator.initialize(text.toString());
                return iterator;
            }
        } break;
    }
    return null;
}

public final boolean isTemporarilyDetached() {
    return (mPrivateFlags3 & PFLAG3_TEMPORARY_DETACH) != 0;
}

@CallSuper
public void dispatchStartTemporaryDetach() {
    mPrivateFlags3 |= PFLAG3_TEMPORARY_DETACH;
    notifyEnterOrExitForAutoFillIfNeeded(false);
    notifyAppearedOrDisappearedForContentCaptureIfNeeded(false);
    onStartTemporaryDetach();
}

public void onStartTemporaryDetach() {
    removeUnsetPressCallback();
    mPrivateFlags |= PFLAG_CANCEL_NEXT_UP_EVENT;
}

@CallSuper
public void dispatchFinishTemporaryDetach() {
    mPrivateFlags3 &= ~PFLAG3_TEMPORARY_DETACH;
    onFinishTemporaryDetach();
    if (hasWindowFocus() && hasFocus()) {
        notifyFocusChangeToImeFocusController(true );
    }
    notifyEnterOrExitForAutoFillIfNeeded(true);
    notifyAppearedOrDisappearedForContentCaptureIfNeeded(true);
}

public void onFinishTemporaryDetach() {
}

public KeyEvent.DispatcherState getKeyDispatcherState() {
    return mAttachInfo != null ? mAttachInfo.mKeyDispatchState : null;
}

public boolean dispatchKeyEventPreIme(KeyEvent event) {
    return onKeyPreIme(event.getKeyCode(), event);
}

public boolean dispatchKeyEvent(KeyEvent event) {
    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onKeyEvent(event, 0);
    }
    ListenerInfo li = mListenerInfo;
    if (li != null && li.mOnKeyListener != null && (mViewFlags & ENABLED_MASK) == ENABLED
            && li.mOnKeyListener.onKey(this, event.getKeyCode(), event)) {
        return true;
    }

    if (event.dispatch(this, mAttachInfo != null
            ? mAttachInfo.mKeyDispatchState : null, this)) {
        return true;
    }

    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onUnhandledEvent(event, 0);
    }
    return false;
}

public boolean dispatchKeyShortcutEvent(KeyEvent event) {
    return onKeyShortcut(event.getKeyCode(), event);
}

@FlaggedApi(FLAG_SCROLL_TO_TOP)
public boolean dispatchScrollToTop(int x) {
    return onScrollToTop(x);
}

@FlaggedApi(FLAG_SCROLL_TO_TOP)
public boolean onScrollToTop(int x) {
    return false;
}

public boolean dispatchTouchEvent(MotionEvent event) {
    if (event.isTargetAccessibilityFocus()) {
        if (!isAccessibilityFocusedViewOrHost()) {
            return false;
        }
        event.setTargetAccessibilityFocus(false);
    }
    boolean result = false;

    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onTouchEvent(event, 0);
    }

    final int actionMasked = event.getActionMasked();
    if (actionMasked == MotionEvent.ACTION_DOWN) {
        stopNestedScroll();
    }

    if (onFilterTouchEventForSecurity(event)) {
        result = performOnTouchCallback(event);
    }

    if (!result && mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onUnhandledEvent(event, 0);
    }
    if (actionMasked == MotionEvent.ACTION_UP ||
            actionMasked == MotionEvent.ACTION_CANCEL ||
            (actionMasked == MotionEvent.ACTION_DOWN && !result)) {
        stopNestedScroll();
    }

    return result;
}

private boolean performOnTouchCallback(MotionEvent event) {
    boolean handled = false;
    if ((mViewFlags & ENABLED_MASK) == ENABLED && handleScrollBarDragging(event)) {
        handled = true;
    }
    ListenerInfo li = mListenerInfo;
    if (li != null && li.mOnTouchListener != null && (mViewFlags & ENABLED_MASK) == ENABLED) {
        try {
            if (Trace.isTagEnabled(TRACE_TAG_VIEW)) {
                Trace.traceBegin(TRACE_TAG_VIEW,
                        "View.onTouchListener#onTouch - " + getClass().getSimpleName()
                                + ", eventId - " + event.getId());
            }
            handled = li.mOnTouchListener.onTouch(this, event);
        } finally {
            Trace.traceEnd(TRACE_TAG_VIEW);
        }
    }
    if (handled) {
        return true;
    }
    try {
        Trace.traceBegin(TRACE_TAG_VIEW, "View#onTouchEvent");
        return onTouchEvent(event);
    } finally {
        Trace.traceEnd(TRACE_TAG_VIEW);
    }
}

boolean isAccessibilityFocusedViewOrHost() {
    return isAccessibilityFocused() || (getViewRootImpl() != null && getViewRootImpl()
            .getAccessibilityFocusedHost() == this);
}

protected boolean canReceivePointerEvents() {
    return (mViewFlags & VISIBILITY_MASK) == VISIBLE || getAnimation() != null;
}

public boolean onFilterTouchEventForSecurity(MotionEvent event) {
    if ((mViewFlags & FILTER_TOUCHES_WHEN_OBSCURED) != 0
            && (event.getFlags() & MotionEvent.FLAG_WINDOW_IS_OBSCURED) != 0) {
        return false;
    }
    if (event.isInjectedFromAccessibilityService()
            && !event.isInjectedFromAccessibilityTool() && isAccessibilityDataSensitive()) {
        return false;
    }
    return true;
}

public boolean dispatchTrackballEvent(MotionEvent event) {
    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onTrackballEvent(event, 0);
    }

    return onTrackballEvent(event);
}

public boolean dispatchCapturedPointerEvent(MotionEvent event) {
    if (!hasPointerCapture()) {
        return false;
    }
    ListenerInfo li = mListenerInfo;
    if (li != null && li.mOnCapturedPointerListener != null
            && li.mOnCapturedPointerListener.onCapturedPointer(this, event)) {
        return true;
    }
    return onCapturedPointerEvent(event);
}

public boolean dispatchGenericMotionEvent(MotionEvent event) {
    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onGenericMotionEvent(event, 0);
    }

    final int source = event.getSource();
    if ((source & InputDevice.SOURCE_CLASS_POINTER) != 0) {
        final int action = event.getAction();
        if (action == MotionEvent.ACTION_HOVER_ENTER
                || action == MotionEvent.ACTION_HOVER_MOVE
                || action == MotionEvent.ACTION_HOVER_EXIT) {
            if (dispatchHoverEvent(event)) {
                return true;
            }
        } else if (dispatchGenericPointerEvent(event)) {
            return true;
        }
    } else if (dispatchGenericFocusedEvent(event)) {
        return true;
    }

    if (dispatchGenericMotionEventInternal(event)) {
        return true;
    }

    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onUnhandledEvent(event, 0);
    }
    return false;
}

private boolean dispatchGenericMotionEventInternal(MotionEvent event) {
    final boolean isRotaryEncoderEvent = event.isFromSource(InputDevice.SOURCE_ROTARY_ENCODER);
    if (isRotaryEncoderEvent) {
        if ((mPrivateFlags4 & PFLAG4_ROTARY_HAPTICS_DETERMINED) == 0) {
            if (mViewConfiguration.isViewBasedRotaryEncoderHapticScrollFeedbackEnabled()) {
                mPrivateFlags4 |= PFLAG4_ROTARY_HAPTICS_ENABLED;
            }
            mPrivateFlags4 |= PFLAG4_ROTARY_HAPTICS_DETERMINED;
        }
    }
    if (isRotaryEncoderEvent && ((mPrivateFlags4 & PFLAG4_ROTARY_HAPTICS_ENABLED) != 0)) {
        mPrivateFlags4 &= ~PFLAG4_ROTARY_HAPTICS_SCROLL_SINCE_LAST_ROTARY_INPUT;
        mPrivateFlags4 |= PFLAG4_ROTARY_HAPTICS_WAITING_FOR_SCROLL_EVENT;
    }
    ListenerInfo li = mListenerInfo;
    if (li != null && li.mOnGenericMotionListener != null
            && (mViewFlags & ENABLED_MASK) == ENABLED
            && li.mOnGenericMotionListener.onGenericMotion(this, event)) {
        return true;
    }

    final boolean onGenericMotionEventResult = onGenericMotionEvent(event);
    if (isRotaryEncoderEvent && ((mPrivateFlags4 & PFLAG4_ROTARY_HAPTICS_ENABLED) != 0)) {
        if ((mPrivateFlags4 & PFLAG4_ROTARY_HAPTICS_SCROLL_SINCE_LAST_ROTARY_INPUT) != 0) {
            doRotaryProgressForScrollHaptics(event);
        } else {
            doRotaryLimitForScrollHaptics(event);
        }
    }
    if (onGenericMotionEventResult) {
        return true;
    }

    final int actionButton = event.getActionButton();
    switch (event.getActionMasked()) {
        case MotionEvent.ACTION_BUTTON_PRESS:
            if (isContextClickable() && !mInContextButtonPress && !mHasPerformedLongPress
                    && (actionButton == MotionEvent.BUTTON_STYLUS_PRIMARY
                    || actionButton == MotionEvent.BUTTON_SECONDARY)) {
                if (performContextClick(event.getX(), event.getY())) {
                    mInContextButtonPress = true;
                    setPressed(true, event.getX(), event.getY());
                    removeTapCallback();
                    removeLongPressCallback();
                    return true;
                }
            }
            break;

        case MotionEvent.ACTION_BUTTON_RELEASE:
            if (mInContextButtonPress && (actionButton == MotionEvent.BUTTON_STYLUS_PRIMARY
                    || actionButton == MotionEvent.BUTTON_SECONDARY)) {
                mInContextButtonPress = false;
                mIgnoreNextUpEvent = true;
            }
            break;
    }

    if (mInputEventConsistencyVerifier != null) {
        mInputEventConsistencyVerifier.onUnhandledEvent(event, 0);
    }
    return false;
}

protected boolean dispatchHoverEvent(MotionEvent event) {
    ListenerInfo li = mListenerInfo;
    if (li != null && li.mOnHoverListener != null
            && (mViewFlags & ENABLED_MASK) == ENABLED
            && li.mOnHoverListener.onHover(this, event)) {
        return true;
    }

    return onHoverEvent(event);
}

protected boolean hasHoveredChild() {
    return false;
}

protected boolean pointInHoveredChild(MotionEvent event) {
    return false;
}

protected boolean dispatchGenericPointerEvent(MotionEvent event) {
    return false;
}

protected boolean dispatchGenericFocusedEvent(MotionEvent event) {
    return false;
}

@UnsupportedAppUsage(maxTargetSdk = Build.VERSION_CODES.R, trackingBug = 170729553)
public final boolean dispatchPointerEvent(MotionEvent event) {
    if (event.isTouchEvent()) {
        return dispatchTouchEvent(event);
    } else {
        return dispatchGenericMotionEvent(event);
    }
}

public void dispatchWindowFocusChanged(boolean hasFocus) {
    onWindowFocusChanged(hasFocus);
}

public void onWindowFocusChanged(boolean hasWindowFocus) {
    if (!hasWindowFocus) {
        if (isPressed()) {
            setPressed(false);
        }
        mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
        if ((mPrivateFlags & PFLAG_FOCUSED) != 0) {
            notifyFocusChangeToImeFocusController(false );
        }
        removeLongPressCallback();
        removeTapCallback();
        onFocusLost();
    } else if ((mPrivateFlags & PFLAG_FOCUSED) != 0) {
        notifyFocusChangeToImeFocusController(true );
        ViewRootImpl viewRoot = getViewRootImpl();
        if (viewRoot != null && initiationWithoutInputConnection() && onCheckIsTextEditor()) {
            viewRoot.getHandwritingInitiator().onEditorFocused(this);
        }
    }

    refreshDrawableState();
}

public boolean hasWindowFocus() {
    return mAttachInfo != null && mAttachInfo.mHasWindowFocus;
}

public boolean hasImeFocus() {
    return getViewRootImpl() != null && getViewRootImpl().getImeFocusController().hasImeFocus();
}

protected void dispatchVisibilityChanged(@NonNull View changedView,
        @Visibility int visibility) {
    onVisibilityChanged(changedView, visibility);
}

protected void onVisibilityChanged(@NonNull View changedView, @Visibility int visibility) {
}

public void dispatchDisplayHint(@Visibility int hint) {
    onDisplayHint(hint);
}

protected void onDisplayHint(@Visibility int hint) {
}

public void dispatchWindowVisibilityChanged(@Visibility int visibility) {
    onWindowVisibilityChanged(visibility);
}

protected void onWindowVisibilityChanged(@Visibility int visibility) {
    if (visibility == VISIBLE) {
        initialAwakenScrollBars();
    }
}

public boolean isAggregatedVisible() {
    return (mPrivateFlags3 & PFLAG3_AGGREGATED_VISIBLE) != 0;
}

boolean dispatchVisibilityAggregated(boolean isVisible) {
    final boolean thisVisible = getVisibility() == VISIBLE;
    if (thisVisible || !isVisible) {
        onVisibilityAggregated(isVisible);
    }
    return thisVisible && isVisible;
}

@CallSuper
public void onVisibilityAggregated(boolean isVisible) {
    boolean oldVisible = isAggregatedVisible();
    mPrivateFlags3 = isVisible ? (mPrivateFlags3 | PFLAG3_AGGREGATED_VISIBLE)
            : (mPrivateFlags3 & ~PFLAG3_AGGREGATED_VISIBLE);
    if (isVisible && mAttachInfo != null) {
        initialAwakenScrollBars();
    }

    final Drawable dr = mBackground;
    if (dr != null && isVisible != dr.isVisible()) {
        dr.setVisible(isVisible, false);
    }
    final Drawable hl = mDefaultFocusHighlight;
    if (hl != null && isVisible != hl.isVisible()) {
        hl.setVisible(isVisible, false);
    }
    final Drawable fg = mForegroundInfo != null ? mForegroundInfo.mDrawable : null;
    if (fg != null && isVisible != fg.isVisible()) {
        fg.setVisible(isVisible, false);
    }
    notifyAutofillManagerViewVisibilityChanged(isVisible);
    if (isVisible != oldVisible) {
        if (isAccessibilityPane()) {
            notifyViewAccessibilityStateChangedIfNeeded(isVisible
                    ? AccessibilityEvent.CONTENT_CHANGE_TYPE_PANE_APPEARED
                    : AccessibilityEvent.CONTENT_CHANGE_TYPE_PANE_DISAPPEARED);
        }

        notifyAppearedOrDisappearedForContentCaptureIfNeeded(isVisible);
        updateSensitiveViewsCountIfNeeded(isVisible);

        if (!getSystemGestureExclusionRects().isEmpty()) {
            postUpdate(this::updateSystemGestureExclusionRects);
        }

        if (!collectPreferKeepClearRects().isEmpty()) {
            postUpdate(this::updateKeepClearRects);
        }
    }
}

private void notifyAutofillManagerViewVisibilityChanged(boolean isVisible) {
    if (isAutofillable()) {
        AutofillManager afm = getAutofillManager();

        if (afm != null && getAutofillViewId() > LAST_APP_AUTOFILL_ID) {
            if (mVisibilityChangeForAutofillHandler != null) {
                mVisibilityChangeForAutofillHandler.removeMessages(0);
            }
            if (isVisible) {
                afm.notifyViewVisibilityChanged(this, true);
            } else {
                if (mVisibilityChangeForAutofillHandler == null) {
                    mVisibilityChangeForAutofillHandler =
                            new VisibilityChangeForAutofillHandler(afm, this);
                }
                mVisibilityChangeForAutofillHandler.obtainMessage(0, this).sendToTarget();
            }
        }
    }
}

@Visibility
public int getWindowVisibility() {
    return mAttachInfo != null ? mAttachInfo.mWindowVisibility : GONE;
}

public void getWindowVisibleDisplayFrame(Rect outRect) {
    if (mAttachInfo != null) {
        mAttachInfo.mViewRootImpl.getWindowVisibleDisplayFrame(outRect);
        return;
    }
    final WindowManager windowManager = mContext.getSystemService(WindowManager.class);
    final WindowMetrics metrics = windowManager.getMaximumWindowMetrics();
    final Insets insets = metrics.getWindowInsets().getInsets(
            WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
    outRect.set(metrics.getBounds());
    outRect.inset(insets);
    outRect.offsetTo(0, 0);
}

@UnsupportedAppUsage
@TestApi
public void getWindowDisplayFrame(@NonNull Rect outRect) {
    if (mAttachInfo != null) {
        mAttachInfo.mViewRootImpl.getDisplayFrame(outRect);
        return;
    }
    Display d = DisplayManagerGlobal.getInstance().getRealDisplay(Display.DEFAULT_DISPLAY);
    d.getRectSize(outRect);
}

public void dispatchConfigurationChanged(Configuration newConfig) {
    onConfigurationChanged(newConfig);
}

protected void onConfigurationChanged(Configuration newConfig) {
}

void dispatchCollectViewAttributes(AttachInfo attachInfo, int visibility) {
    performCollectViewAttributes(attachInfo, visibility);
}

void performCollectViewAttributes(AttachInfo attachInfo, int visibility) {
    if ((visibility & VISIBILITY_MASK) == VISIBLE) {
        if ((mViewFlags & KEEP_SCREEN_ON) == KEEP_SCREEN_ON) {
            attachInfo.mKeepScreenOn = true;
        }
        attachInfo.mSystemUiVisibility |= mSystemUiVisibility;
        ListenerInfo li = mListenerInfo;
        if (li != null && li.mOnSystemUiVisibilityChangeListener != null) {
            attachInfo.mHasSystemUiListeners = true;
        }
    }
}

void needGlobalAttributesUpdate(boolean force) {
    final AttachInfo ai = mAttachInfo;
    if (ai != null && !ai.mRecomputeGlobalAttributes) {
        if (force || ai.mKeepScreenOn || (ai.mSystemUiVisibility != 0)
                || ai.mHasSystemUiListeners) {
            ai.mRecomputeGlobalAttributes = true;
        }
    }
}

@ViewDebug.ExportedProperty
public boolean isInTouchMode() {
    if (mAttachInfo != null) {
        return mAttachInfo.mInTouchMode;
    }
    return mResources.getBoolean(com.android.internal.R.bool.config_defaultInTouchMode);
}

@ViewDebug.CapturedViewProperty
@UiContext
public final Context getContext() {
    return mContext;
}

public boolean onKeyPreIme(int keyCode, KeyEvent event) {
    return false;
}

public boolean onKeyDown(int keyCode, KeyEvent event) {
    if (KeyEvent.isConfirmKey(keyCode) && event.hasNoModifiers()) {
        if ((mViewFlags & ENABLED_MASK) == DISABLED) {
            return true;
        }

        if (event.getRepeatCount() == 0) {
            final boolean clickable = (mViewFlags & CLICKABLE) == CLICKABLE
                    || (mViewFlags & LONG_CLICKABLE) == LONG_CLICKABLE;
            if (clickable || (mViewFlags & TOOLTIP) == TOOLTIP) {
                final float x = getWidth() / 2f;
                final float y = getHeight() / 2f;
                if (clickable) {
                    setPressed(true, x, y);
                }
                checkForLongClick(
                        getLongPressTimeoutMillis(),
                        x,
                        y,
                        TOUCH_GESTURE_CLASSIFIED__CLASSIFICATION__UNKNOWN_CLASSIFICATION);
                return true;
            }
        }
    }

    return false;
}

public boolean onKeyLongPress(int keyCode, KeyEvent event) {
    return false;
}

public boolean onKeyUp(int keyCode, KeyEvent event) {
    if (KeyEvent.isConfirmKey(keyCode) && event.hasNoModifiers()) {
        if ((mViewFlags & ENABLED_MASK) == DISABLED) {
            return true;
        }
        if ((mViewFlags & CLICKABLE) == CLICKABLE && isPressed()) {
            setPressed(false);

            if (!mHasPerformedLongPress) {
                removeLongPressCallback();
                if (!event.isCanceled()) {
                    return performClickInternal();
                }
            }
        }
    }
    return false;
}

public boolean onKeyMultiple(int keyCode, int repeatCount, KeyEvent event) {
    return false;
}

public boolean onKeyShortcut(int keyCode, KeyEvent event) {
    return false;
}

public boolean onCheckIsTextEditor() {
    return false;
}

public InputConnection onCreateInputConnection(EditorInfo outAttrs) {
    return null;
}

public void onInputConnectionOpenedInternal(@NonNull InputConnection inputConnection,
        @NonNull EditorInfo editorInfo, @Nullable Handler handler) {}

public void onInputConnectionClosedInternal() {}

public boolean checkInputConnectionProxy(View view) {
    return false;
}

public void createContextMenu(ContextMenu menu) {
    ContextMenuInfo menuInfo = getContextMenuInfo();
    ((MenuBuilder)menu).setCurrentMenuInfo(menuInfo);

    onCreateContextMenu(menu);
    ListenerInfo li = mListenerInfo;
    if (li != null && li.mOnCreateContextMenuListener != null) {
        li.mOnCreateContextMenuListener.onCreateContextMenu(menu, this, menuInfo);
    }
    ((MenuBuilder)menu).setCurrentMenuInfo(null);

    if (mParent != null) {
        mParent.createContextMenu(menu);
    }
}

protected ContextMenuInfo getContextMenuInfo() {
    return null;
}

protected void onCreateContextMenu(ContextMenu menu) {
}

public boolean onTrackballEvent(MotionEvent event) {
    return false;
}

public boolean onGenericMotionEvent(MotionEvent event) {
    return false;
}

private boolean dispatchTouchExplorationHoverEvent(MotionEvent event) {
    final AccessibilityManager manager = AccessibilityManager.getInstance(mContext);
    if (!manager.isEnabled() || !manager.isTouchExplorationEnabled()) {
        return false;
    }

    final boolean oldHoveringTouchDelegate = mHoveringTouchDelegate;
    final int action = event.getActionMasked();
    boolean pointInDelegateRegion = false;
    boolean handled = false;

    final AccessibilityNodeInfo.TouchDelegateInfo info = mTouchDelegate.getTouchDelegateInfo();
    for (int i = 0; i < info.getRegionCount(); i++) {
        Region r = info.getRegionAt(i);
        if (r.contains((int) event.getX(), (int) event.getY())) {
            pointInDelegateRegion = true;
        }
    }
    if (!oldHoveringTouchDelegate) {
        if (removeChildHoverCheckForTouchExploration()) {
            if ((action == MotionEvent.ACTION_HOVER_ENTER
                    || action == MotionEvent.ACTION_HOVER_MOVE) && pointInDelegateRegion) {
                mHoveringTouchDelegate = true;
            }
        } else {
            if ((action == MotionEvent.ACTION_HOVER_ENTER
                    || action == MotionEvent.ACTION_HOVER_MOVE)
                    && !pointInHoveredChild(event)
                    && pointInDelegateRegion) {
                mHoveringTouchDelegate = true;
            }
        }
    } else {
        if (removeChildHoverCheckForTouchExploration()) {
            if (action == MotionEvent.ACTION_HOVER_EXIT
                    || (action == MotionEvent.ACTION_HOVER_MOVE)) {
                if (!pointInDelegateRegion) {
                    mHoveringTouchDelegate = false;
                }
            }
        } else {
            if (action == MotionEvent.ACTION_HOVER_EXIT
                    || (action == MotionEvent.ACTION_HOVER_MOVE
                    && (pointInHoveredChild(event) || !pointInDelegateRegion))) {
                mHoveringTouchDelegate = false;
            }
        }
    }
    switch (action) {
        case MotionEvent.ACTION_HOVER_MOVE:
            if (oldHoveringTouchDelegate && mHoveringTouchDelegate) {
                handled = mTouchDelegate.onTouchExplorationHoverEvent(event);
            } else if (!oldHoveringTouchDelegate && mHoveringTouchDelegate) {
                MotionEvent eventNoHistory = (event.getHistorySize() == 0)
                        ? event : MotionEvent.obtainNoHistory(event);
                eventNoHistory.setAction(MotionEvent.ACTION_HOVER_ENTER);
                handled = mTouchDelegate.onTouchExplorationHoverEvent(eventNoHistory);
                eventNoHistory.setAction(action);
                handled |= mTouchDelegate.onTouchExplorationHoverEvent(eventNoHistory);
            } else if (oldHoveringTouchDelegate && !mHoveringTouchDelegate) {
                final boolean hoverExitPending = event.isHoverExitPending();
                event.setHoverExitPending(true);
                mTouchDelegate.onTouchExplorationHoverEvent(event);
                MotionEvent eventNoHistory = (event.getHistorySize() == 0)
                        ? event : MotionEvent.obtainNoHistory(event);
                eventNoHistory.setHoverExitPending(hoverExitPending);
                eventNoHistory.setAction(MotionEvent.ACTION_HOVER_EXIT);
                mTouchDelegate.onTouchExplorationHoverEvent(eventNoHistory);
            }  // else: outside bounds, do nothing.
            break;
        case MotionEvent.ACTION_HOVER_ENTER:
            if (!oldHoveringTouchDelegate && mHoveringTouchDelegate) {
                handled = mTouchDelegate.onTouchExplorationHoverEvent(event);
            }
            break;
        case MotionEvent.ACTION_HOVER_EXIT:
            if (oldHoveringTouchDelegate) {
                mTouchDelegate.onTouchExplorationHoverEvent(event);
            }
            break;
    }
    return handled;
}

public boolean onHoverEvent(MotionEvent event) {
    if (mTouchDelegate != null && dispatchTouchExplorationHoverEvent(event)) {
        return true;
    }
    final int action = event.getActionMasked();
    if (!mSendingHoverAccessibilityEvents) {
        if ((action == MotionEvent.ACTION_HOVER_ENTER
                || action == MotionEvent.ACTION_HOVER_MOVE)
                && !hasHoveredChild()
                && pointInView(event.getX(), event.getY())) {
            sendAccessibilityHoverEvent(AccessibilityEvent.TYPE_VIEW_HOVER_ENTER);
            mSendingHoverAccessibilityEvents = true;
        }
    } else {
        if (action == MotionEvent.ACTION_HOVER_EXIT
                || (action == MotionEvent.ACTION_HOVER_MOVE
                        && !pointInView(event.getX(), event.getY()))) {
            mSendingHoverAccessibilityEvents = false;
            sendAccessibilityHoverEvent(AccessibilityEvent.TYPE_VIEW_HOVER_EXIT);
        }
    }

    if ((action == MotionEvent.ACTION_HOVER_ENTER || action == MotionEvent.ACTION_HOVER_MOVE)
            && event.isFromSource(InputDevice.SOURCE_MOUSE)
            && isOnScrollbar(event.getX(), event.getY())) {
        awakenScrollBars();
    }
    if (isHoverable() || isHovered()) {
        switch (action) {
            case MotionEvent.ACTION_HOVER_ENTER:
                setHovered(true);
                break;
            case MotionEvent.ACTION_HOVER_EXIT:
                setHovered(false);
                break;
        }
        dispatchGenericMotionEventInternal(event);
        return true;
    }

    return false;
}

private boolean isHoverable() {
    final int viewFlags = mViewFlags;
    if ((viewFlags & ENABLED_MASK) == DISABLED) {
        return false;
    }

    return (viewFlags & CLICKABLE) == CLICKABLE
            || (viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE
            || (viewFlags & CONTEXT_CLICKABLE) == CONTEXT_CLICKABLE;
}

@ViewDebug.ExportedProperty
public boolean isHovered() {
    return (mPrivateFlags & PFLAG_HOVERED) != 0;
}

public void setHovered(boolean hovered) {
    if (hovered) {
        if ((mPrivateFlags & PFLAG_HOVERED) == 0) {
            mPrivateFlags |= PFLAG_HOVERED;
            refreshDrawableState();
            onHoverChanged(true);
        }
    } else {
        if ((mPrivateFlags & PFLAG_HOVERED) != 0) {
            mPrivateFlags &= ~PFLAG_HOVERED;
            refreshDrawableState();
            onHoverChanged(false);
        }
    }
}

public void onHoverChanged(boolean hovered) {
}

protected boolean handleScrollBarDragging(MotionEvent event) {
    if (mScrollCache == null) {
        return false;
    }
    final float x = event.getX();
    final float y = event.getY();
    final int action = event.getAction();
    if ((mScrollCache.mScrollBarDraggingState == ScrollabilityCache.NOT_DRAGGING
            && action != MotionEvent.ACTION_DOWN)
                || !event.isFromSource(InputDevice.SOURCE_MOUSE)
                || !event.isButtonPressed(MotionEvent.BUTTON_PRIMARY)) {
        mScrollCache.mScrollBarDraggingState = ScrollabilityCache.NOT_DRAGGING;
        return false;
    }

    switch (action) {
        case MotionEvent.ACTION_MOVE:
            if (mScrollCache.mScrollBarDraggingState == ScrollabilityCache.NOT_DRAGGING) {
                return false;
            }
            if (mScrollCache.mScrollBarDraggingState
                    == ScrollabilityCache.DRAGGING_VERTICAL_SCROLL_BAR) {
                final Rect bounds = mScrollCache.mScrollBarBounds;
                getVerticalScrollBarBounds(bounds, null);
                final int range = computeVerticalScrollRange();
                final int offset = computeVerticalScrollOffset();
                final int extent = computeVerticalScrollExtent();

                final int thumbLength = ScrollBarUtils.getThumbLength(
                        bounds.height(), bounds.width(), extent, range);
                final int thumbOffset = ScrollBarUtils.getThumbOffset(
                        bounds.height(), thumbLength, extent, range, offset);

                final float diff = y - mScrollCache.mScrollBarDraggingPos;
                final float maxThumbOffset = bounds.height() - thumbLength;
                final float newThumbOffset =
                        Math.min(Math.max(thumbOffset + diff, 0.0f), maxThumbOffset);
                final int height = getHeight();
                if (Math.round(newThumbOffset) != thumbOffset && maxThumbOffset > 0
                        && height > 0 && extent > 0) {
                    final int newY = Math.round((range - extent)
                            / ((float)extent / height) * (newThumbOffset / maxThumbOffset));
                    if (newY != getScrollY()) {
                        mScrollCache.mScrollBarDraggingPos = y;
                        setScrollY(newY);
                    }
                }
                return true;
            }
            if (mScrollCache.mScrollBarDraggingState
                    == ScrollabilityCache.DRAGGING_HORIZONTAL_SCROLL_BAR) {
                final Rect bounds = mScrollCache.mScrollBarBounds;
                getHorizontalScrollBarBounds(bounds, null);
                final int range = computeHorizontalScrollRange();
                final int offset = computeHorizontalScrollOffset();
                final int extent = computeHorizontalScrollExtent();

                final int thumbLength = ScrollBarUtils.getThumbLength(
                        bounds.width(), bounds.height(), extent, range);
                final int thumbOffset = ScrollBarUtils.getThumbOffset(
                        bounds.width(), thumbLength, extent, range, offset);

                final float diff = x - mScrollCache.mScrollBarDraggingPos;
                final float maxThumbOffset = bounds.width() - thumbLength;
                final float newThumbOffset =
                        Math.min(Math.max(thumbOffset + diff, 0.0f), maxThumbOffset);
                final int width = getWidth();
                if (Math.round(newThumbOffset) != thumbOffset && maxThumbOffset > 0
                        && width > 0 && extent > 0) {
                    final int newX = Math.round((range - extent)
                            / ((float)extent / width) * (newThumbOffset / maxThumbOffset));
                    if (newX != getScrollX()) {
                        mScrollCache.mScrollBarDraggingPos = x;
                        setScrollX(newX);
                    }
                }
                return true;
            }
        case MotionEvent.ACTION_DOWN:
            if (mScrollCache.state == ScrollabilityCache.OFF) {
                return false;
            }
            if (isOnVerticalScrollbarThumb(x, y)) {
                mScrollCache.mScrollBarDraggingState =
                        ScrollabilityCache.DRAGGING_VERTICAL_SCROLL_BAR;
                mScrollCache.mScrollBarDraggingPos = y;
                return true;
            }
            if (isOnHorizontalScrollbarThumb(x, y)) {
                mScrollCache.mScrollBarDraggingState =
                        ScrollabilityCache.DRAGGING_HORIZONTAL_SCROLL_BAR;
                mScrollCache.mScrollBarDraggingPos = x;
                return true;
            }
    }
    mScrollCache.mScrollBarDraggingState = ScrollabilityCache.NOT_DRAGGING;
    return false;
}

public boolean onTouchEvent(MotionEvent event) {
    final float x = event.getX();
    final float y = event.getY();
    final int viewFlags = mViewFlags;
    final int action = event.getAction();

    final boolean clickable = ((viewFlags & CLICKABLE) == CLICKABLE
            || (viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE)
            || (viewFlags & CONTEXT_CLICKABLE) == CONTEXT_CLICKABLE;

    if ((viewFlags & ENABLED_MASK) == DISABLED
            && (mPrivateFlags4 & PFLAG4_ALLOW_CLICK_WHEN_DISABLED) == 0) {
        if (action == MotionEvent.ACTION_UP && (mPrivateFlags & PFLAG_PRESSED) != 0) {
            setPressed(false);
        }
        mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
        return clickable;
    }
    if (mTouchDelegate != null) {
        if (mTouchDelegate.onTouchEvent(event)) {
            return true;
        }
    }
```

这段在禁用处理之后、普通 clickable/tooltip 的 switch 之前。只要代理返回 true，父默认触摸处理就结束；如果返回 false，父仍可能走自身的点击逻辑。不能在父 OnTouchListener 中先 return true，再期待基类 onTouchEvent 自动执行代理。

```text
扩展区域 DOWN -> 祖先命中父容器
  父 ViewGroup.dispatchTouchEvent：没有普通子项消费
    父 View.dispatchTouchEvent -> performOnTouchCallback
      父 View.onTouchEvent -> TouchDelegate.onTouchEvent
        命中 mBounds -> 坐标移到图标中心
          图标.dispatchTouchEvent -> 图标.onTouchEvent -> true
后续 MOVE/UP -> 父自身分发路径 -> 同一个 delegate -> 同一个图标
```

#### 16.2.5 实战：布局变化时重建扩展区域

以下应用示例使用平台 API。要求 target 是 host 的直接子 View，且此扩展区域采用无额外旋转/缩放的父局部坐标。监听父子布局变化，避免旋转、窗口调整或文本重排后仍使用旧 Rect。

```kotlin
import android.graphics.Rect
import android.view.TouchDelegate
import android.view.View
import kotlin.math.roundToInt

class ExpandedTouchArea(
    private val host: View,
    private val target: View,
    extraDp: Float = 12f
) : AutoCloseable {
    private val expansionDp = extraDp
    private var installed: TouchDelegate? = null
    private var closed = false
    private val refresh = Runnable { update() }
    private val layoutListener = View.OnLayoutChangeListener { _, _, _, _, _, _, _, _, _ ->
        host.removeCallbacks(refresh)
        host.post(refresh)
    }

    init {
        require(target.parent === host) { "target 必须是 host 的直接子 View" }
        require(extraDp.isFinite() && extraDp >= 0f)
        host.addOnLayoutChangeListener(layoutListener)
        target.addOnLayoutChangeListener(layoutListener)
        host.post(refresh)
    }

    private fun update() {
        if (closed || !host.isLaidOut || !target.isLaidOut) return
        val extra = (expansionDp * target.resources.displayMetrics.density).roundToInt()
        val bounds = Rect()
        target.getHitRect(bounds)
        bounds.inset(-extra, -extra)
        if (!bounds.intersect(0, 0, host.width, host.height)) {
            if (host.touchDelegate === installed) host.touchDelegate = null
            installed = null
            return
        }
        installed = TouchDelegate(bounds, target)
        host.touchDelegate = installed
    }

    override fun close() {
        closed = true
        host.removeCallbacks(refresh)
        host.removeOnLayoutChangeListener(layoutListener)
        target.removeOnLayoutChangeListener(layoutListener)
        if (host.touchDelegate === installed) host.touchDelegate = null
        installed = null
    }
}
```

在视图创建后持有该对象，在对应视图生命周期销毁时 close。正常情况下不要在进行中的手势里切换 delegate，否则新对象没有旧 DOWN 建立的归属状态；若交互期间必须改变布局，应由上层明确取消旧交互再更新区域。

多个小按钮可各放进足够大的独立点击容器，避免多个扩展矩形重叠；需要聚合代理时，应在 DOWN 决定唯一目标并持续持有到 UP/CANCEL，而不是每个 MOVE 都重新选择最近按钮。

### 16.3 异步事件处理

View 的触摸分发在所属 UI 线程同步决定是否消费，不要把原始 MotionEvent 保存到后台稍后访问：事件可能被回收或复用。异步计算应复制需要的坐标/时间等值；确需保存事件时用 `MotionEvent.obtain(event)` 并明确 `recycle()` 的所有权。依据：[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)、[MotionEvent API](https://developer.android.com/reference/android/view/MotionEvent)。

获取布局后的宽高宜使用 `onSizeChanged` 或 AndroidX `doOnLayout`；任意 `View.post` 不是不附条件的“布局完成监听器”。不要在触摸回调执行长耗时工作。

---

*文档创建时间：2026-03-07*
*来源：Android 源码分析 + 知识体系总结*
