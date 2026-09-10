# Android InputManager 输入系统深度解析

> 作者：OpenClaw | 日期：2026-03-12  
> 基于源码：AOSP Android 17 / API 37，固定 tag `android-17.0.0_r1`；复核日期：2026-09-10。

## 目录

- [1. 概述](#1-概述)
  - [1.1 IMS 的核心职责](#11-ims-的核心职责)
  - [1.2 IMS 在系统中的位置](#12-ims-在系统中的位置)
- [2. IMS 架构总览](#2-ims-架构总览)
  - [2.1 IMS 内部架构](#21-ims-内部架构)
  - [2.2 核心线程](#22-核心线程)
- [3. 输入事件读取 (EventHub)](#3-输入事件读取-eventhub)
  - [3.1 EventHub 架构](#31-eventhub-架构)
  - [3.2 原始事件结构](#32-原始事件结构)
  - [3.3 InputReader 处理流程](#33-inputreader-处理流程)
- [4. 输入事件分发流程](#4-输入事件分发流程)
  - [4.1 分发流程总览](#41-分发流程总览)
  - [4.2 InputDispatcher 分发逻辑](#42-inputdispatcher-分发逻辑)
  - [4.3 ANR 处理](#43-anr-处理)
- [5. InputChannel 与 InputConnection](#5-inputchannel-与-inputconnection)
  - [5.1 InputChannel](#51-inputchannel)
  - [5.2 InputConnection](#52-inputconnection)
- [6. 触摸事件处理](#6-触摸事件处理)
  - [6.1 触摸事件类型](#61-触摸事件类型)
  - [6.2 触摸事件分发流程](#62-触摸事件分发流程)
  - [6.3 onTouchEvent 源码](#63-ontouchevent-源码)
- [7. 按键事件处理](#7-按键事件处理)
  - [7.1 按键事件类型](#71-按键事件类型)
  - [7.2 按键事件分发流程](#72-按键事件分发流程)
  - [7.3 系统按键处理](#73-系统按键处理)
- [8. 输入法交互](#8-输入法交互)
  - [8.1 输入法架构](#81-输入法架构)
  - [8.2 输入法通信](#82-输入法通信)
- [9. 总结](#9-总结)

---

## 1. 概述

**InputManagerService (IMS)** 是 Android 系统的核心服务之一，负责管理所有输入设备的事件读取、分发和处理，包括触摸屏、键盘、鼠标、游戏手柄等。

### 1.1 IMS 的核心职责

```text
┌─────────────────────────────────────────────────────────────────┐
│                    IMS 核心职责                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  1. 输入事件读取 (Event Reading)                          │  │
│  │     • 从内核读取原始事件                                  │  │
│  │     • 设备热插拔检测                                      │  │
│  │     • 设备能力查询                                        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  2. 事件过滤与转换 (Event Filtering)                      │  │
│  │     • 原始事件转换为高级事件                              │  │
│  │     • 多点触控处理                                        │  │
│  │     • 手势识别                                            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  3. 事件分发 (Event Dispatch)                             │  │
│  │     • 确定目标窗口                                        │  │
│  │     • 按优先级分发                                        │  │
│  │     • 处理 ANR                                            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  4. 输入窗口与策略协作                              │  │
│  │     • 输入通道管理                                          │  │
│  │     • 焦点与窗口信息                                            │  │
│  │     • IMMS 另行管理文本输入                                          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 IMS 在系统中的位置

事件数据通道与控制通道必须分开。普通触摸不会先经过 Java IMS 或 IMMS 再发给应用；native 输入组件通常运行在 system_server，不能从 InputFlinger 名称推断独立进程。

```text
/dev/input/event* -> EventHub -> InputReader
  -> UnwantedInteractionBlocker -> PointerChoreographer -> InputProcessor
  -> InputDeviceMetricsCollector -> InputFilter -> InteractionReporter
  -> InputDispatcher -> InputChannel -> 应用 InputEventReceiver / ViewRootImpl

Java IMS <-> NativeInputManager：设备配置、策略回调、注入、通道管理
WMS InputMonitor -> SurfaceControl transaction -> SurfaceFlinger 窗口信息
  -> InputDispatcher：输入区域、层级、焦点等
IMM <-> IMMS <-> InputMethodService：编辑器连接、IME 绑定和可见性控制
```

上面 native listener 链省略 `TracedInputListener` 包装；构造时从 Dispatcher 向 Reader 反向连接，事件沿图中方向传递。IMS 不负责编辑器文本写入。源码：[InputManager.cpp:137](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/InputManager.cpp#137)；[InputMonitor.java:344](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/InputMonitor.java#344)

## 2. IMS 架构总览

### 2.1 IMS 内部架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          IMS 内部架构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    InputManagerService                               │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                  Java 层组件                                   │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │InputManager  │  │InputManager  │  │InputMethod   │     │ │ │
│   │   │   │Callback      │  │Policy        │  │Manager       │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                  Native 层组件                                │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │EventHub      │  │InputReader   │  │InputDispatcher│    │ │ │
│   │   │   │ (事件集线器) │  │ (输入读取)   │  │ (输入分发)   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │ │
│   │   │   │InputProcessor│ │InputListener │  │InputChannel  │     │ │ │
│   │   │   │ (输入分类)   │  │ (监听器)     │  │ (输入通道)   │     │ │ │
│   │   │   └──────────────┘  └──────────────┘  └──────────────┘     │ │ │
│   │   │                                                               │ │ │
│   │   └──────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心线程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        IMS 核心线程                                         │
└─────────────────────────────────────────────────────────────────────────────┘

1. InputReaderThread (输入读取线程)
   • 从 EventHub 读取原始事件
   • 解析和转换事件
   • 分发给 InputDispatcher
   • 线程优先级: high

2. InputDispatcherThread (输入分发线程)
   • 接收来自 InputReader 的事件
   • 确定目标窗口
   • 分发事件到应用
   • 处理 ANR
   • 线程优先级: high

3. 应用主线程 (Main Thread)
   • 接收分发的事件
   • 执行 View/Activity 回调
   • 处理输入事件

线程间通信：
InputReaderThread → InputDispatcherThread: InputListener 接口
InputDispatcherThread → Main Thread: InputChannel (Unix Socket)
```

---

## 3. 输入事件读取 (EventHub)

### 3.1 EventHub 架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EventHub 架构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

EventHub 职责：
1. 监控 /dev/input/ 目录
2. 读取原始输入事件
3. 设备热插拔检测
4. 设备能力查询

设备文件（编号由设备枚举决定，下面仅示例）：
• /dev/input/event0 - 触摸屏
• /dev/input/event1 - 键盘
• /dev/input/event2 - 鼠标
• /dev/input/event3 - 游戏手柄

工作原理：
1. 使用 epoll 监控多个设备文件
2. 使用 inotify 监控 /dev/input/ 目录变化
3. 当有事件时，epoll_wait() 返回
4. 读取原始事件 (struct input_event)
```

### 3.2 原始事件结构

```c
/**
 * 原始输入事件
 * 定义在内核: include/uapi/linux/input.h
 */
struct input_event {
    struct timeval time;    // 时间戳
    __u16 type;             // 事件类型
    __u16 code;             // 事件代码
    __s32 value;            // 事件值
};

// 事件类型
#define EV_SYN          0x00    // 同步事件
#define EV_KEY          0x01    // 按键事件
#define EV_REL          0x02    // 相对坐标 (鼠标)
#define EV_ABS          0x03    // 绝对坐标 (触摸屏)
#define EV_MSC          0x04    // 杂项事件
#define EV_SW           0x05    // 开关事件
#define EV_LED          0x11    // LED 事件
#define EV_SND          0x12    // 声音事件
#define EV_REP          0x14    // 重复事件
#define EV_FF           0x15    // 力反馈
#define EV_PWR          0x16    // 电源事件
#define EV_FF_STATUS    0x17    // 力反馈状态

// 触摸事件代码 (EV_ABS)
#define ABS_X           0x00    // X 坐标
#define ABS_Y           0x01    // Y 坐标
#define ABS_PRESSURE    0x18    // 压力
#define ABS_MT_SLOT     0x2f    // 多点触控槽位
#define ABS_MT_TOUCH_MAJOR 0x30 // 触摸面积
#define ABS_MT_POSITION_X  0x35 // MT X 坐标
#define ABS_MT_POSITION_Y  0x36 // MT Y 坐标
#define ABS_MT_TRACKING_ID 0x39 // MT 跟踪 ID
```

### 3.3 InputReader 处理流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        InputReader 处理流程                                 │
└─────────────────────────────────────────────────────────────────────────────┘

InputReader::loopOnce() {
    
    1. 从 EventHub 读取事件
       └─► EventHub.getEvents()
           └─► epoll_wait() 等待事件
           └─► 读取原始 input_event
    
    2. 处理事件
       └─► processEventsForDeviceLocked()
           └─► 根据设备类型分发
               ├─► TouchInputMapper (触摸)
               ├─► KeyboardInputMapper (键盘)
               ├─► CursorInputMapper (鼠标)
               └─► JoystickInputMapper (游戏手柄)
    
    3. 转换为高级事件
       └─► TouchInputMapper.process()
           └─► 计算触摸点
           └─► 生成 NotifyMotionArgs，尚不是应用 Java MotionEvent
           └─► 多点触控处理
    
    4. 分发给 InputDispatcher
       └─► InputListener.notifyMotion()
           └─► InputDispatcher.notifyMotion()
    
    5. 处理设备变化
       └─► 检测设备热插拔
       └─► 更新设备列表
}
```

---

## 4. 输入事件分发流程

### 4.1 分发流程总览

```text
InputReader listener 通知 -> InputDispatcher.notifyMotion(NotifyMotionArgs)
  -> 校验并将 MotionEntry 放入 inbound queue -> 唤醒 Looper
分发线程 dispatchOnce -> dispatchOnceInnerLocked -> dispatchMotionLocked
  -> 普通 DOWN：按坐标、display、touchable region、遮挡/信任策略选目标
  -> MOVE/UP：沿当前触摸状态和 pointer target 分发，可产生 CANCEL/拆分事件
  -> 焦点定向输入：按相应事件类型走 focused target 路径
  -> dispatchEventLocked -> Connection outboundQueue -> startDispatchCycleLocked
  -> InputPublisher / InputChannel
应用 WindowInputEventReceiver.onInputEvent -> enqueueInputEvent
  -> 输入 stage 链 -> DecorView.dispatchTouchEvent -> Activity / View 树
应用 finishInputEvent -> socket FINISHED -> dispatcher 完成确认
```

WMS 提供窗口与焦点状态，不是每个 MotionEvent 都同步向 WMS 查询。普通触摸目标不等于键盘焦点窗口。源码：[InputDispatcher.cpp:2175](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp#2175)；[ViewRootImpl.java:11453](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#11453)

### 4.2 InputDispatcher 分发逻辑

`InputDispatcher` 是 C++ 类，不能用带 `Vector<InputTarget>` 和 `mInputManager->getFocusedWindow()` 的 Java 风格代码冒充源码。真实入口签名与职责如下（接口摘录，省略实现）：

```cpp
void InputDispatcher::notifyMotion(const NotifyMotionArgs& args);
void InputDispatcher::dispatchOnce();
```

`notifyMotion` 接收 reader 的通知对象，校验后建立内部事件记录，并在锁保护下入队。`dispatchOnce` 在持锁区处理待派发事件、超时与命令；执行需要离开锁的策略命令后再 `pollOnce`，不是简单的阻塞 `pop()` 循环。

`dispatchMotionLocked` 同时考虑触摸路由和焦点定向输入；`dispatchEventLocked` 建立每个目标的派发记录，`startDispatchCycleLocked` 发布事件并维护等待确认队列。ANR 时间跟随 connection 的未完成请求推进，不应把它简化成应用回调里的计时器。

源码：[InputDispatcher.cpp:4679](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp#4679)；[InputDispatcher.cpp:983](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp#983)；[InputDispatcher.cpp:3893](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp#3893)

### 4.3 ANR 处理

输入 ANR 的两类关键状态是：已发送到窗口但未按时收到完成确认，以及存在焦点应用却迟迟没有可接收输入的焦点窗口。默认派发超时以 5 秒为基础并乘硬件超时倍率，窗口/应用提供的超时和策略可改变它；不存在“前台触摸 5 秒、后台触摸 10 秒”的通用规则。

```text
发送事件 -> connection.waitQueue / AnrTracker
  -> processAnrsLocked -> onAnrLocked
  -> policy 通知 -> Java 输入/窗口策略 -> AMS ANR 处理
应用完成确认 -> 从等待队列移除 -> 更新下一超时点
```

超时通知不等于立刻弹框或杀进程，后续诊断和用户界面受系统策略约束。现代 traces 通常由 `/data/anr/anr_*` 文件承载，不应硬编码为单一 `traces.txt`。排查时同时看焦点窗口、派发状态、Binder 阻塞和应用主线程，而不只缩短 `onTouchEvent`。

源码：[InputDispatcher.cpp:127](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp#127)；[InputDispatcher.cpp:1143](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp#1143)

## 5. InputChannel 与 InputConnection

### 5.1 InputChannel

`InputChannel` 包装 native 通道端点。其 Java 成对创建 API 返回数组，而非使用输出数组参数（框架内部 API，不是普通应用 SDK 接口）：

```java
public static InputChannel[] openInputChannelPair(String name);
private static native long[] nativeOpenInputChannelPair(String name);
```

普通窗口的真实建立方向是服务端创建、返回客户端端点：

```text
ViewRootImpl.setView -> IWindowSession.addToDisplay* -> WMS.addWindow
  -> WindowState.openInputChannel
  -> IMS.createInputChannel -> InputDispatcher.createInputChannel
       创建 Unix socket pair；保存 server connection，返回 client channel
  -> 经窗口添加结果返回应用
  -> WindowInputEventReceiver 绑定主线程 Looper
```

VRI 不先创建一对通道再调用虚构的 `WMS.registerInputChannel()`。socket 承载事件与完成确认，Binder 用于传递通道描述符和窗口控制。销毁窗口时还需要注销通道，不能只释放 Java 引用。

源码：[InputChannel.java:138](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/InputChannel.java#138)；[WindowState.java:2680](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowState.java#2680)；[InputDispatcher.cpp:6431](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp#6431)

连续节选 [WindowState.java:2680–2690](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/services/core/java/com/android/server/wm/WindowState.java#2680)（不是独立编译单元）：

```java
InputChannel openInputChannel() {
    if (mInputChannelToken != null) {
        throw new IllegalStateException("Window already has an input channel token.");
    }
    String name = getName();
    final InputChannel channel = mWmService.mInputManager.createInputChannel(name);
    mInputChannelToken = channel.getToken();
    mInputWindowHandle.setToken(mInputChannelToken);
    mWmService.mInputToWindowMap.put(mInputChannelToken, this);
    return channel;
}
```

mInputChannelToken 把 native connection 与 WindowState 关联；重复建立会抛异常。窗口销毁还要 removeInputChannel 和移除输入映射，不只释放客户端 Java InputChannel。

连续节选 [InputDispatcher.cpp:6431–6455](https://android.googlesource.com/platform/frameworks/native/+/refs/tags/android-17.0.0_r1/services/inputflinger/dispatcher/InputDispatcher.cpp#6431)（不是独立编译单元）：

```cpp
Result<std::unique_ptr<InputChannel>> InputDispatcher::createInputChannel(const std::string& name) {
    LOG_IF(INFO, DEBUG_CHANNEL_CREATION) << "channel '" << name << "' ~ createInputChannel";

    std::unique_ptr<InputChannel> serverChannel;
    std::unique_ptr<InputChannel> clientChannel;
    status_t result = InputChannel::openInputChannelPair(name, serverChannel, clientChannel);

    if (result) {
        return base::Error(result) << "Failed to open input channel pair with name " << name;
    }

    { // acquire lock
        std::scoped_lock _l(mLock);
        const sp<IBinder>& token = serverChannel->getConnectionToken();
        std::function<int(int events)> callback = std::bind(&InputDispatcher::handleReceiveCallback,
                                                            this, std::placeholders::_1, token);

        mConnectionManager.createConnection(std::move(serverChannel), mIdGenerator, callback);
    } // release lock

    // Wake the looper because some connections have changed.
    mLooper->wake();
    return clientChannel;
}

```

创建 pair 失败立即返回错误；成功后在锁内将 server endpoint 存入 Connection 并注册 Looper 回调，client endpoint 返回调用方。这解释了为何事件和 FINISHED 回执都能沿 socket 连接双向传输，及关闭窗口后仍持有旧端点不能继续接收有效输入。

### 5.2 InputConnection

以下是接口方法摘录与 BaseInputConnection 的核心行为，省略注解、其余方法和调试日志。

```java
/**
 * InputConnection - 输入连接
 * 位置：frameworks/base/core/java/android/view/inputmethod/InputConnection.java
 * 
 * 职责：应用与输入法之间的通信接口
 */
interface InputConnection {
    // 文本操作
    CharSequence getTextBeforeCursor(int n, int flags);
    CharSequence getTextAfterCursor(int n, int flags);
    CharSequence getSelectedText(int flags);
    
    // 文本编辑
    boolean commitText(CharSequence text, int newCursorPosition);
    boolean deleteSurroundingText(int beforeLength, int afterLength);
    boolean setComposingText(CharSequence text, int newCursorPosition);
    boolean finishComposingText();
    
    // 选择操作
    boolean setSelection(int start, int end);
    
    // 键盘操作
    boolean sendKeyEvent(KeyEvent event);
    boolean performEditorAction(int editorAction);
    
    // 光标操作
    boolean performContextMenuAction(int id);
}

/** BaseInputConnection.commitText 的实现摘录；其余 InputConnection 方法见接口。 */
@Override
public boolean commitText(CharSequence text, int newCursorPosition) {
    replaceText(text, newCursorPosition, false);
    sendCurrentText();
    return true;
}
```

---

`newCursorPosition` 是相对插入文本结束位置（正值）或开始位置（非正值）的游标偏移，不是直接传给 `setSelection()` 的绝对下标；例如 `1` 通常表示插入后。替换还要处理 composing span、选区和过滤器。源码：[BaseInputConnection.java:239](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/inputmethod/BaseInputConnection.java#239)。

## 6. 触摸事件处理

### 6.1 触摸事件类型

以下列举常量与方法签名，省略方法体和其余 API，不是可独立编译的 MotionEvent 类。

```java
/**
 * MotionEvent - 触摸事件
 * 位置：frameworks/base/core/java/android/view/MotionEvent.java
 */
class MotionEvent {
    // 动作类型
    public static final int ACTION_DOWN = 0;           // 按下
    public static final int ACTION_UP = 1;             // 抬起
    public static final int ACTION_MOVE = 2;           // 移动
    public static final int ACTION_CANCEL = 3;         // 取消
    public static final int ACTION_OUTSIDE = 4;        // 边界外
    public static final int ACTION_POINTER_DOWN = 5;   // 多点按下
    public static final int ACTION_POINTER_UP = 6;     // 多点抬起
    public static final int ACTION_HOVER_MOVE = 7;     // 悬停移动
    public static final int ACTION_SCROLL = 8;         // 滚动
    public static final int ACTION_HOVER_ENTER = 9;    // 悬停进入
    public static final int ACTION_HOVER_EXIT = 10;    // 悬停退出
    public static final int ACTION_BUTTON_PRESS = 11;  // 按钮按下
    public static final int ACTION_BUTTON_RELEASE = 12;// 按钮释放
    
    // 获取坐标
    public final float getX();
    public final float getY();
    public final float getX(int pointerIndex);
    public final float getY(int pointerIndex);
    
    // 获取多点触控信息
    public final int getPointerCount();
    public final int getPointerId(int pointerIndex);
    public final int findPointerIndex(int pointerId);
    
    // 获取压力和大小
    public final float getPressure();
    public final float getSize();
}
```

### 6.2 触摸事件分发流程

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        触摸事件分发流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Activity.dispatchTouchEvent()
    │
    ▼
Window.superDispatchTouchEvent()
    │
    ▼
DecorView.superDispatchTouchEvent()
    │
    ▼
ViewGroup.dispatchTouchEvent()
    │
    ├─► onInterceptTouchEvent() - 是否拦截
    │   │
    │   ├─► true: 拦截，不分发给子 View
    │   └─► false: 不拦截，分发给子 View
    │
    ▼
子 View.dispatchTouchEvent()
    │
    ├─► onTouch() - OnTouchListener
    │   │
    │   ├─► true: 消费，不调用 onTouchEvent()
    │   └─► false: 调用 onTouchEvent()
    │
    ▼
View.onTouchEvent()
    │
    ├─► true: 消费事件
    └─► false: 不消费，回传给父 View
```

### 6.3 onTouchEvent 源码

`View.onTouchEvent` 的点击判定依赖 enabled/clickable/longClickable、pressed/prepressed、触摸 slop、长按和取消状态。移出可点击范围后不能在 UP 时无条件调用 `performClick()`；禁用但可点击的 View 也可能消费事件而不执行点击。

```text
DOWN -> 建立按压/预按压状态，按条件安排长按检查
MOVE -> 检查 slop；移出范围清除按压并移除 tap/long-press 回调
UP   -> 仅在有效按压、未长按等条件下安排 PerformClick / performClickInternal
        -> 清理按压状态与回调
CANCEL -> 清理按压、长按和 tap 回调，不生成点击
```

这里是控制流摘要，不是完整实现；无障碍点击、鼠标上下文点击和 tooltip 分支也不能由四个 case 的示例代替。源码：[View.java:18447](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java#18447)

## 7. 按键事件处理

### 7.1 按键事件类型

```java
/**
 * KeyEvent - 按键事件
 * 位置：frameworks/base/core/java/android/view/KeyEvent.java
 */
class KeyEvent {
    // 动作类型
    public static final int ACTION_DOWN = 0;    // 按下
    public static final int ACTION_UP = 1;      // 抬起
    public static final int ACTION_MULTIPLE = 2;// 多次
    
    // 按键码
    public static final int KEYCODE_UNKNOWN = 0;
    public static final int KEYCODE_SOFT_LEFT = 1;
    public static final int KEYCODE_SOFT_RIGHT = 2;
    public static final int KEYCODE_HOME = 3;
    public static final int KEYCODE_BACK = 4;
    public static final int KEYCODE_CALL = 5;
    public static final int KEYCODE_ENDCALL = 6;
    public static final int KEYCODE_0 = 7;
    public static final int KEYCODE_1 = 8;
    // ... 更多按键码
    
    public static final int KEYCODE_VOLUME_UP = 24;
    public static final int KEYCODE_VOLUME_DOWN = 25;
    public static final int KEYCODE_POWER = 26;
    public static final int KEYCODE_CAMERA = 27;
    public static final int KEYCODE_MENU = 82;
    public static final int KEYCODE_ENTER = 66;
    public static final int KEYCODE_DEL = 67;   // 退格
    public static final int KEYCODE_TAB = 61;
    public static final int KEYCODE_SPACE = 62;
}
```

### 7.2 按键事件分发流程

```text
InputDispatcher -> 应用 ViewRootImpl input stages
  -> pre-IME / IME 阶段（符合条件的按键）
  -> DecorView.dispatchKeyEvent
       Window.Callback（Activity.dispatchKeyEvent）
         -> PhoneWindow.superDispatchKeyEvent -> DecorView.superDispatchKeyEvent
         -> 焦点 View 树 / OnKeyListener / onKeyDown、onKeyUp
         -> 未处理时 KeyEvent.dispatch(Activity, ...) -> Activity 回调
       Callback 未处理 -> PhoneWindow.onKeyDown/onKeyUp 的窗口 fallback
```

HOME/POWER 等可能先被系统 policy 消费；不能假定所有硬件按键都到 Activity。预测性返回也不能统一理解为普通 `KEYCODE_BACK` 派发。源码：[DecorView.java:343](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/policy/DecorView.java#343)；[Activity.java:4620](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/app/Activity.java#4620)

### 7.3 系统按键处理

`PhoneWindow` 的方法需要 `featureId`，不是 `public boolean onKeyDown(int keyCode, KeyEvent event)`：

```java
protected boolean onKeyDown(int featureId, int keyCode, KeyEvent event);
protected boolean onKeyUp(int featureId, int keyCode, KeyEvent event);
```

它负责窗口面板、菜单、音量/媒体按键相关 fallback。音量处理会走媒体控制器或媒体会话相关辅助逻辑，不能以临时构造 `AudioManager.adjustVolume()` 代替真实调用链；面板状态通过 `PanelFeatureState` 和对应 feature 查询，也没有示例中统一的 `mPanel.openPanel()` API。

源码：[PhoneWindow.java:2036](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/policy/PhoneWindow.java#2036)；[PhoneWindow.java:2148](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/com/android/internal/policy/PhoneWindow.java#2148)

## 8. 输入法交互

### 8.1 输入法架构

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        输入法架构                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    InputMethodManagerService                         │ │
│   │                    (系统服务)                                        │ │
│   └──────────────────────────────┬──────────────────────────────────────┘ │
│                                   │                                        │
│                                   │                                        │
│              ┌────────────────────┼────────────────────┐                  │
│              │                    │                    │                  │
│              ▼                    ▼                    ▼                  │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐          │
│   │ InputMethod   │    │ InputMethod   │    │ InputMethod   │          │
│   │ Service (拼音)│    │ Service (手写)│    │ Service (英文)│          │
│   └───────┬───────┘    └───────┬───────┘    └───────┬───────┘          │
│           │                    │                    │                    │
│           └────────────────────┼────────────────────┘                    │
│                                 │                                          │
│                                 │ InputConnection                          │
│                                 ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    应用 (EditText / TextView)                        │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 输入法通信

`showSoftInput` 返回 `boolean`，不是 `void`。接口摘录如下；返回值描述请求处理，不能据此判断键盘已经可见：

```java
public boolean showSoftInput(View view, int flags);
public boolean hideSoftInputFromWindow(IBinder windowToken, int flags);
@Deprecated
public void toggleSoftInput(int showFlags, int hideFlags);
```

必须区分三条并行协作的链路：

```text
1. 设备事件：InputDispatcher -> InputChannel -> ViewRootImpl / 输入 stages
   触摸命中 IME 窗口时 -> IME 自己的 View 树，而非先交 IMMS 选择输入法
2. 编辑器控制：窗口焦点/编辑器变化 -> 应用 IMM
   -> startInputOrWindowGainedFocus 等 Binder 请求 -> IMMS
   -> 验证调用身份与焦点、绑定输入法、建立输入 session
3. 文本编辑：InputMethodService -> 远程 InputConnection 包装
   -> 应用编辑器 InputConnection.commitText / setComposingText 等
   -> TextView/Editable 更新文本、选区、组合态
```

`EditorInfo` 是编辑器元信息，不是位于文本事件末端的执行对象。普通软键盘文字输入不要求变成 `KeyEvent`；硬键盘事件可被应用的 IME input stage 转交已建立的 IME session。IMMS 不是每次 `InputDispatcher` 派发后都重新选择输入法的线性节点。

本 tag 的 IMM 显示/隐藏实现通过 `setImeVisibilityOnInsetsController` 请求当前 ViewRootImpl 的 InsetsController；不能继续描述为该方法必然直接经 global invoker 调用 IMMS。显示要求 view 已建立适当焦点/served 状态；异步结果应观察 `WindowInsets.Type.ime()` 可见性，而非立刻读取 `showSoftInput` 返回值。

源码：[InputMethodManager.java:2468](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/inputmethod/InputMethodManager.java#2468)；[InputMethodManager.java:2559](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/inputmethod/InputMethodManager.java#2559)；[ViewRootImpl.java:8364](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewRootImpl.java#8364)；[InputConnection.java:738](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/inputmethod/InputConnection.java#738)

连续节选 [InputMethodManager.java:2572–2595](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/inputmethod/InputMethodManager.java#2572)（不是独立编译单元）：

```java
checkFocus();
synchronized (mH) {
    if (!hasServedByInputMethodLocked(view)) {
        ImeTracker.forLogging().onFailed(statsToken, ImeTracker.PHASE_CLIENT_VIEW_SERVED);
        ImeTracker.forLatency().onShowFailed(statsToken,
                ImeTracker.PHASE_CLIENT_VIEW_SERVED, ActivityThread::currentApplication);
        if (android.tracing.Flags.imetrackerProtolog()) {
            ProtoLog.w(INPUT_METHOD_MANAGER_WITH_LOGCAT,
                    "Ignoring showSoftInput() as view=%s is not served.", view);
        } else {
            Log.w(TAG, "Ignoring showSoftInput() as view=" + view + " is not served.");
        }
        return false;
    }

    ImeTracker.forLogging().onProgress(statsToken, ImeTracker.PHASE_CLIENT_VIEW_SERVED);

    final var viewRootImpl = view.getViewRootImpl();
    // In case of a running show IME animation, it should not be requested visible,
    // otherwise the animation would jump and not be controlled by the user anymore.
    // If predictive back is in progress, and a editText is focussed, we should
    // show the IME.
    if (viewRootImpl != null && (
            (viewRootImpl.getInsetsController().computeUserAnimatingTypes()
```

checkFocus 后仍需验证 served view；仅仅拿到一个非 null EditText 并不满足该条件。接下来还检查用户控制的 IME 动画和预测性返回状态，防止显示请求抢断交互动画。

连续节选 [InputMethodManager.java:2596–2613](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/inputmethod/InputMethodManager.java#2596)（不是独立编译单元）：

```java
                & WindowInsets.Type.ime()) == 0
        || viewRootImpl.getInsetsController()
                .isPredictiveBackImeHideAnimInProgress())) {
    ImeTracker.forLogging().onProgress(statsToken,
            ImeTracker.PHASE_CLIENT_NO_ONGOING_USER_ANIMATION);
    if (resultReceiver != null) {
        final boolean imeReqVisible = hasViewImeRequestedVisible(
                viewRootImpl.getView());
        resultReceiver.send(
                imeReqVisible ? InputMethodManager.RESULT_UNCHANGED_SHOWN
                        : InputMethodManager.RESULT_SHOWN, null);
    }
    setImeVisibilityOnInsetsController(viewRootImpl, true /* visible */, statsToken);
    return true;
}
ImeTracker.forLogging().onCancelled(statsToken,
        ImeTracker.PHASE_CLIENT_NO_ONGOING_USER_ANIMATION);
return false;
```

ResultReceiver 的回报依请求可见性等状态计算，不是显示器实测可见。hide 路径在部分兼容条件下即使 served window 不匹配也会返回 true，因此返回 boolean 更不能当成已隐藏证明。

文本编辑失败则优先检查 InputConnection 是否过期、选区/composing span 与编辑器线程；设备事件可达并不保证输入连接仍有效。

## 9. 总结

Android 17 的输入系统由 native `EventHub`、`InputReader`、`InputDispatcher` 与 Java 框架层协作完成。按键、触摸和输入法虽然入口不同，但设备事件通道、输入法控制通道和文本编辑通道必须分别分析。分析问题时要沿着“设备事件 → native 读取/分发 → Binder 或 InputChannel → ViewRootImpl/编辑器”的链路定位，而不是只观察某个 View 的回调。
