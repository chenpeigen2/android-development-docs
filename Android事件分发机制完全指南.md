# Android 事件分发机制完全指南

## 目录

1. [概述](#1-概述)
2. [整体架构流程图](#2-整体架构流程图)
3. [内核层 (Linux Kernel)](#3-内核层-linux-kernel)
4. [Native 层](#4-native-层)
5. [Framework 层 - Input 子系统](#5-framework-层---input-子系统)
6. [Framework 层 - WindowManagerService](#6-framework-层---windowmanagerservice)
7. [App 层 - ViewRootImpl](#7-app层---viewrootimpl)
8. [App 层 - Activity](#8-app层---activity)
9. [App 层 - ViewGroup](#9-app层---viewgroup)
10. [App 层 - View](#10-app层---view)
11. [完整流程图汇总](#11-完整流程图汇总)
12. [核心方法详解](#12-核心方法详解)
13. [事件序列与状态管理](#13-事件序列与状态管理)
14. [典型场景分析](#14-典型场景分析)
15. [滑动冲突解决](#15-滑动冲突解决)
16. [进阶知识点](#16-进阶知识点)

---

## 1. 概述

Android 事件分发是一个**从硬件到 App** 的完整链路，涉及多个层次：

```
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           用户触摸屏幕                                        │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Linux Kernel (Input Driver)                          │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  1. 触摸屏产生中断                                                     │  │
│  │  2. Input Driver 读取事件数据                                          │  │
│  │  3. 创建 Input Event 放入 /dev/input/ 缓冲区                           │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ /dev/input/eventX
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Native Layer                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  InputReader: 从 /dev/input/ 读取原始事件                             │  │
│  │       ↓                                                              │  │
│  │  InputDispatcher: 将事件分发给目标窗口                                 │  │
│  │       ↓                                                              │  │
│  │  Socket (Client): 通过 socket 发送到 Framework                        │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ socket (pair)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Framework Layer                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  InputReaderThread (InputReader)                                     │  │
│  │       ↓ process()                                                    │  │
│  │  InputDispatcherThread (InputDispatcher)                             │  │
│  │       ↓ dispatchEvent()                                              │  │
│  │  WindowManagerService                                                │  │
│  │       ↓ dispatchInput()                                              │  │
│  │  ViewRootImpl.windowInputEventReceiver                               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              App Layer                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  Activity.dispatchTouchEvent()                                       │  │
│  │       ↓                                                              │  │
│  │  DecorView (ViewGroup).dispatchTouchEvent()                          │  │
│  │       ↓ onInterceptTouchEvent?                                       │  │
│  │       ↓                                                              │  │
│  │  [ViewGroup1 → ViewGroup2 → ... → View]                            │  │
│  │       ↓ onTouchEvent()                                               │  │
│  │  [View ← ViewGroup ← Activity]                                      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 内核层 (Linux Kernel)

### 3.1 触摸屏中断流程

```
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

```cpp
// 位置: frameworks/native/services/inputflinger/InputReader.cpp

void InputReader::processEventsLocked(const RawEvent* rawEvents, size_t count) {
    for (size_t i = 0; i < count; i++) {
        // 1. 读取原始事件
        const RawEvent& rawEvent = rawEvents[i];
        
        // 2. 根据事件类型分发
        switch (rawEvent.type) {
            case EV_SYN:
                // 同步事件，处理一批事件的结束
                processSynchronization();
                break;
                
            case EV_ABS:
                // 触摸坐标事件
                processMotion(rawEvent);
                break;
                
            case EV_KEY:
                // 按键事件
                processKey(rawEvent);
                break;
        }
    }
}

void InputReader::processMotion(const RawEvent& rawEvent) {
    // 1. 更新当前触摸点信息
    // 2. 创建 NotifyMotionArgs 事件
    // 3. 发送到 InputDispatcher
}
```

### 4.2 InputDispatcher

```cpp
// 位置: frameworks/native/services/inputflinger/InputDispatcher.cpp

void InputDispatcher::notifyMotion(const NotifyMotionArgs* args) {
    // 1. 寻找目标窗口
    std::vector<InputTarget> inputTargets;
    findTouchedWindowTargetsLocked(args, inputTargets);
    
    // 2. 构建 InputEvent
    MotionEvent* event = new MotionEvent();
    event->initialize(args->deviceId, args->source, args->action, ...);
    
    // 3. 通过 socket 发送到 App 端
    // 4. 等待 App 处理完成 (或不等待，取决于标志)
    injectInputEvent(event, INJECTION_TIMEOUT_MS);
}
```

### 4.3 Socket 通信

```
┌─────────────────┐          socket           ┌─────────────────┐
│  InputDispatcher│ ◄────────────────────────► │  App Process    │
│                 │                            │  (ViewRootImpl) │
│  /dev/socket/  │                            │                 │
│  input_channel │                            │  InputChannel   │
└─────────────────┘                            └─────────────────┘
```

---

## 5. Framework 层 - Input 子系统

### 5.1 InputReader 流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        InputReader 完整流程                                  │
└─────────────────────────────────────────────────────────────────────────────┘

InputReader::loopOnce()
    │
    ├──► mEventHub->getEvents()         // 从 /dev/input 读取事件
    │
    ├──► processEventsLocked()           // 处理原始事件
    │       │
    │       ├──► EV_SYN → processSynchronization()
    │       │       └──► mPolicy->notifySync()
    │       │
    │       ├──► EV_ABS → processMotion()
    │       │       └──► 转换为 NotifyMotionArgs
    │       │
    │       └──► EV_KEY → processKey()
    │               └──► 转换为 NotifyKeyArgs
    │
    └──► mQueuedListener->flush()       // 发送到 InputDispatcher
            │
            └──► InputDispatcher::notifyXXX()
```

### 5.2 InputDispatcher 分发

```java
// 位置: InputDispatcher.java

public void notifyMotion(NotifyMotionArgs args) {
    // 1. 验证事件有效性
    // 2. 找出目标窗口
    final int motionEntry = addEvent(dispatcherQueue, args);
    
    // 3. 找到目标窗口
    InputTargets targets = findTouchedWindowTargets(args);
    
    // 4. 准备分发
    for (InputTarget target : targets) {
        // 5. 通过 InputChannel 发送
        target.inputChannel.sendMessage(motionEvent);
    }
}
```

---

## 6. Framework 层 - WindowManagerService

### 6.1 WMS 角色

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     WindowManagerService 职责                               │
└─────────────────────────────────────────────────────────────────────────────┘

1. 窗口管理
   - 注册/移除窗口
   - 维护窗口 Z 轴顺序
   - 计算窗口可见区域

2. Input 事件路由
   - 找到事件目标窗口
   - 维护焦点窗口
   - 处理 ANR

3. 窗口动画
   - 窗口切换动画
   - 转场动画
```

### 6.2 Input 事件路由

```java
// 位置: WindowManagerService.java

// 1. WMS 接收 InputDispatcher 的事件
public void dispatchInputEvent(InputEvent event, InputChannel receiveChannel) {
    // 2. 找到目标窗口
    final int windowIndex = getWindowIndexForChannel(receiveChannel);
    final WindowState window = mWindowIndex.get(windowIndex);
    
    // 3. 转发给目标窗口的 InputChannel
    window.mInputChannel.sendMessage(event);
}
```

---

## 7. App层 - ViewRootImpl

### 7.1 ViewRootImpl 角色

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ViewRootImpl 核心职责                                 │
└─────────────────────────────────────────────────────────────────────────────┘

1. UI 线程与 Native 层的桥梁
   - 接收 InputDispatcher 的事件
   - 将事件分发给 DecorView

2. View 树的根节点
   - 执行 measure, layout, draw
   - 处理 invalidate, requestLayout

3. 输入事件处理入口
   - windowInputEventReceiver
   - 事件分发起点
```

### 7.2 Input 事件接收

```java
// 位置: ViewRootImpl.java

public final class ViewRootImpl extends ViewGroup {
    
    // 1. 接收端 - InputChannel
    final InputChannel mInputChannel;
    
    // 2. 输入事件接收器
    final WindowInputEventReceiver mInputEventReceiver;
    
    // 3. 构造函数中创建
    public ViewRootImpl(Context context, Display display) {
        // ...
        mInputChannel = new InputChannel();
        
        // 4. 注册到 WMS
        mWindowSession.addToDisplay(mWindow, mWindowParams, 
            VIEW_SYSTEM_UI_HIDE_LAYOUT, InputChannel[] {mInputChannel});
    }
    
    // 5. 输入事件处理
    final class WindowInputEventReceiver extends BaseInputReceiver {
        @Override
        public void onInputEvent(InputEvent event) {
            // 6. 处理事件
            enqueueInputEvent(event, this, 0, true);
        }
    }
    
    // 7. 将事件加入队列，等待处理
    void enqueueInputEvent(InputEvent event, InputEventReceiver receiver, 
            int flags, boolean processImmediately) {
        
        QueuedInputEvent q = obtainQueuedInputEvent(event, receiver, flags);
        
        // 插入队列尾部
        QueuedInputEvent last = mPendingInputEventTail;
        if (last != null) {
            last.next = q;
            mPendingInputEventTail = q;
        } else {
            mPendingInputEventHead = q;
            mPendingInputEventTail = q;
        }
        
        // 8. 立即处理
        if (processImmediately) {
            doProcessInputEvents();
        }
    }
    
    // 9. 处理输入事件
    void doProcessInputEvents() {
        while (mPendingInputEventHead != null) {
            QueuedInputEvent q = mPendingInputEventHead;
            mPendingInputEventHead = q.next;
            
            // 10. 分发事件
            deliverInputEvent(q);
        }
    }
    
    // 11. 分发到 View 树
    private void deliverInputEvent(QueuedInputEvent q) {
        InputEvent event = q.mEvent;
        
        // 12. 分发给 DecorView
        if (event instanceof MotionEvent) {
            // 13. 关键：调用 DecorView 的 dispatchPointerEvent
            result = mView.dispatchPointerEvent(event);
        }
    }
}
```

### 7.3 ViewRootImpl 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ViewRootImpl Input 处理流程                             │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────────┐
                              │  触摸屏产生事件      │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   Linux Kernel      │
                              │ /dev/input/eventX   │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   InputReader       │
                              │  (Native)           │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   InputDispatcher   │
                              │  (Native)           │
                              └──────────┬──────────┘
                                         │ socket
                                         ▼
                              ┌─────────────────────┐
                              │  WMS                │
                              │  dispatchInputEvent │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │  ViewRootImpl       │
                              │  windowInputEvent   │
                              │  Receiver           │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │  enqueueInputEvent │
                              │  → doProcessInput   │
                              │  Events             │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │  mView.dispatch     │
                              │  PointerEvent       │
                              │  (DecorView)        │
                              └─────────────────────┘
```

---

## 8. App层 - Activity

### 8.1 Activity 事件分发入口

```java
// 位置: Activity.java

public boolean dispatchTouchEvent(MotionEvent ev) {
    // 1. 事件分发开始
    // 2. 先分发给 Window 的 DecorView
    if (getWindow().superDispatchTouchEvent(ev)) {
        // 3. 如果 DecorView 处理了，返回 true
        return true;
    }
    
    // 4. 如果 DecorView 没处理，Activity 自己处理
    return onTouchEvent(ev);
}
```

### 8.2 Activity 流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Activity 事件分发流程                                │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────────┐
                         │  用户触摸屏幕         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  ViewRootImpl       │
                         │  dispatchPointer    │
                         │  Event              │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  DecorView          │
                         │  dispatchTouchEvent │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Activity           │
                         │  dispatchTouchEvent │
                         └──────────┐──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                      │
                         ▼                      ▼
              ┌──────────────────┐   ┌──────────────────┐
              │ getWindow()      │   │ onTouchEvent    │
              │ .superDispatch   │   │ (Activity 处理)  │
              │ TouchEvent(ev)   │   │                  │
              └────────┬─────────┘   └──────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Activity.onTouch │
              │ Event(ev)        │
              └──────────────────┘
```

---

## 9. App层 - ViewGroup

### 9.1 ViewGroup 核心逻辑

```java
// 位置: ViewGroup.java

public boolean dispatchTouchEvent(MotionEvent ev) {
    // 1. 检查是否需要取消当前事件
    if (actionMasked == MotionEvent.ACTION_DOWN) {
        mFirstTouchTarget = null;  // 重置触摸目标
    }
    
    // 2. 检查是否拦截
    final boolean intercepted;
    if (actionMasked == MotionEvent.ACTION_DOWN || mFirstTouchTarget != null) {
        // DOWN 事件或已有目标时，检查拦截
        intercepted = onInterceptTouchEvent(ev);
    } else {
        // MOVE/UP 如果没有目标，不拦截
        intercepted = false;
    }
    
    // 3. 如果拦截了
    if (intercepted) {
        // 取消当前事件
        ev.setAction(MotionEvent.ACTION_CANCEL);
        // 交给自身的 onTouchEvent 处理
        return super.dispatchTouchEvent(ev);
    }
    
    // 4. 检查是否需要取消 (mDisallowIntercept)
    if (mDisallowIntercept) {
        intercepted = false;
    }
    
    // 5. 如果不拦截，分发给子 View
    TouchTarget newTarget = null;
    if (!intercepted && isDispatchTransformationNeeded()) {
        // 6. 找到触摸点下的子 View
        for (int i = childrenCount - 1; i >= 0; i--) {
            final View child = getChildAt(i);
            
            // 检查是否可以接收事件
            if (!canViewReceivePointerEvents(child) 
                    || !isTransformedTouchPointInView(x, y, child, null)) {
                continue;
            }
            
            // 7. 分发给子 View
            if (dispatchTransformedTouchEvent(ev, false, child, idBitsToAssign)) {
                // 8. 子 View 处理了事件
                mFirstTouchTarget = newTarget;
                return true;
            }
        }
    }
    
    // 9. 如果没有子 View 处理，交给自身的 onTouchEvent
    return super.dispatchTouchEvent(ev);
}
```

### 9.2 ViewGroup 完整流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ViewGroup 事件分发完整流程                             │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────────┐
                         │  dispatchTouchEvent │
                         │  (开始)             │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  ACTION_DOWN?       │
                         │  重置 mFirstTouch   │
                         │  Target = null      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  检查拦截           │
                         │  onInterceptTouch   │
                         │  Event?             │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
            ┌───────────────┐               ┌───────────────┐
            │  返回 true    │               │  返回 false   │
            │  (拦截)       │               │  (不拦截)     │
            └───────┬───────┘               └───────┬───────┘
                    │                               │
                    ▼                               ▼
            ┌───────────────┐               ┌───────────────┐
            │ 事件设置为    │               │ 遍历子 View   │
            │ ACTION_CANCEL │               │               │
            └───────┬───────┘               └───────┬───────┘
                    │                               │
                    ▼                               ▼
            ┌───────────────┐               ┌───────────────┐
            │ 交给自身     │               │ 找到目标 View │
            │ onTouchEvent │               │ 分发事件      │
            └───────┬───────┘               └───────┬───────┘
                    │               ┌───────────────┴───────────────┐
                    │               │                               │
                    ▼               ▼                               ▼
            ┌───────────────┐ ┌───────────────┐             ┌───────────────┐
            │ 子View处理    │ │ 子View不处理  │             │ 没有子View    │
            │ → 返回true   │ │ → 返回false   │             │ → 交给自身    │
            └───────────────┘ └───────┬───────┘             └───────┬───────┘
                                    │                               │
                                    └───────────────┬───────────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────────┐
                                         │  super.dispatch    │
                                         │  TouchEvent        │
                                         │  → onTouchEvent   │
                                         └─────────────────────┘
```

---

## 10. App层 - View

### 10.1 View 事件处理

```java
// 位置: View.java

public boolean dispatchTouchEvent(MotionEvent event) {
    // 1. 优先级1: 如果设置了 OnTouchListener，优先调用 onTouch
    if (mListenerInfo != null && mListenerInfo.mOnTouchListener != null) {
        if (mListenerInfo.mOnTouchListener.onTouch(this, event)) {
            return true;  // onTouch 处理了事件
        }
    }
    
    // 2. 优先级2: 调用 onTouchEvent
    return onTouchEvent(event);
}

public boolean onTouchEvent(MotionEvent event) {
    final int action = event.getAction();
    
    // 3. 可点击的 View 会消费事件
    if (clickable || longClickable) {
        switch (action) {
            case MotionEvent.ACTION_DOWN:
                // 记录按下状态，启动长按检测
                break;
                
            case MotionEvent.ACTION_MOVE:
                // 检查是否移出 View 边界
                if (!pointInView(x, y, mTouchSlop)) {
                    // 移除长按回调
                    removeLongPressCallback();
                }
                break;
                
            case MotionEvent.ACTION_UP:
                // 执行点击
                if (!postPressed) {
                    performClick();
                }
                break;
                
            case MotionEvent.ACTION_CANCEL:
                // 重置状态
                break;
        }
        return true;  // 消费事件
    }
    
    // 4. 不可点击的 View 不消费事件
    return false;
}
```

### 10.2 View 事件处理流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          View 事件处理流程                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  dispatchTouchEvent │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  OnTouchListener    │
                    │  != null?           │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
    ┌─────────────────────┐          ┌─────────────────────┐
    │  onTouch() 返回 true │          │  onTouch() 返回 false│
    └──────────┬──────────┘          └──────────┬──────────┘
               │                                │
               ▼                                ▼
    ┌─────────────────────┐          ┌─────────────────────┐
    │  返回 true          │          │  onTouchEvent()    │
    │  (事件已处理)       │          └──────────┬──────────┘
    └─────────────────────┘                     │
                                                 ▼
                                    ┌─────────────────────┐
                                    │  clickable ||       │
                                    │  longClickable?     │
                                    └──────────┬──────────┘
                                               │
                          ┌────────────────────┴────────────────────┐
                          │                                         │
                          ▼                                         ▼
               ┌─────────────────────┐                  ┌─────────────────────┐
               │  是 (可点击)        │                  │  否 (不可点击)      │
               │  → 处理点击/长按    │                  │  → 返回 false       │
               │  → 返回 true        │                  │  (不消费事件)       │
               └─────────────────────┘                  └─────────────────────┘
```

---

## 11. 完整流程图汇总

### 11.1 从内核到 View 的完整链路

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Android 触摸事件完整分发链路                              │
└─────────────────────────────────────────────────────────────────────────────┘

硬件层:  触摸屏 ──中断──► Input Driver ──/dev/input/eventX──► 
                          │
Native层:                InputReader ──NotifyMotionArgs──► InputDispatcher ──socket──►
                          │                                        │
Framework层:             InputDispatcherThread              WindowManagerService
                          │                                        │
                          │ dispatchInputEvent                    │
                          │                                        ▼
                          │                              InputChannel
App层:                   │                                        │
                          ▼                                        ▼
                 ┌─────────────────────────────────────────────────────────────┐
                 │                    ViewRootImpl                            │
                 │         windowInputEventReceiver                           │
                 │                    │                                       │
                 │                    ▼                                       │
                 │         enqueueInputEvent → doProcessInputEvents          │
                 │                    │                                       │
                 │                    ▼                                       │
                 │         mView.dispatchPointerEvent                         │
                 │                    │ (DecorView)                           │
                 │                    ▼                                       │
                 │         Activity.dispatchTouchEvent                        │
                 │                    │                                       │
                 │                    ▼                                       │
                 │         DecorView.dispatchTouchEvent                       │
                 │                    │                                       │
                 │                    ▼                                       │
                 │         ViewGroup.onInterceptTouchEvent?                    │
                 │                    │                                       │
                 │         ┌──────────┴──────────┐                           │
                 │         │                      │                           │
                 │         ▼                      ▼                           │
                 │  [不拦截]                   [拦截]                         │
                 │         │                      │                           │
                 │         ▼                      ▼                           │
                 │  分发给子 View          自身 onTouchEvent                  │
                 │         │                      │                           │
                 │         ▼                      ▼                           │
                 │  ... → View              super.onTouchEvent               │
                 │         │                      │                           │
                 │         ▼                      ▼                           │
                 │  onTouchEvent              处理完成                        │
                 │  返回结果                                              │
                 └─────────────────────────────────────────────────────────────┘
```

---

## 12. 核心方法详解

### 12.1 方法对比表

| 方法 | 所在类 | 作用 | 返回值含义 |
|------|--------|------|------------|
| `dispatchTouchEvent` | Activity/ViewGroup/View | 事件分发入口 | true=已消费 |
| `onInterceptTouchEvent` | ViewGroup | 拦截判断 | true=拦截 |
| `onTouchEvent` | Activity/ViewGroup/View | 事件处理 | true=已消费 |

### 12.2 事件消费优先级

```
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ACTION_DOWN 特殊性                                │
└─────────────────────────────────────────────────────────────────────────────┘

1. 每个事件序列的开始
   - 标志用户一次完整的触摸操作
   
2. 会重置状态
   - mFirstTouchTarget = null
   - 重新寻找目标 View
   
3. 决定后续事件的目
   - 如果子 View 处理了 DOWN，后续事件直接发给它
   - 如果子 View 没处理 DOWN，后续事件不再发给它

4. onInterceptTouchEvent 总是被调用
   - MOVE/UP 只有在 mFirstTouchTarget != null 时才调用
```

### 13.2 事件序列图

```
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

```
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

```
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

```java
// 1. 使用 getActionMasked() 而不是 getAction()
int action = event.getActionMasked();

switch (action) {
    case MotionEvent.ACTION_DOWN:         // 第一个手指按下
        // ...
        break;
        
    case MotionEvent.ACTION_POINTER_DOWN: // 第二个手指按下
        int index = event.getActionIndex();
        float x =);
        float y = event.getY event.getX(index(index);
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
        
    case MotionEvent.ACTION_UP:           // 最后一个手指抬起
        // ...
        break;
}
```

### 16.2 TouchDelegate 扩大点击区域

```java
// 扩大点击区域
View parent = button.getParent();
if (parent instanceof ViewGroup) {
    ViewGroup viewGroup = (ViewGroup) parent;
    
    viewGroup.post(() -> {
        Rect bounds = new Rect();
        button.getHitRect(bounds);
        
        // 扩大 50px
        bounds.top -= 50;
        bounds.bottom += 50;
        bounds.left -= 50;
        bounds.right += 50;
        
        TouchDelegate delegate = new TouchDelegate(bounds, button);
        viewGroup.setTouchDelegate(delegate);
    });
}
```

### 16.3 异步事件处理

```java
// View.post() 获取宽高
view.post(new Runnable() {
    @Override
    public void run() {
        int width = view.getWidth();
        int height = view.getHeight();
    }
});

// ViewTreeObserver 监听
view.getViewTreeObserver().addOnGlobalLayoutListener(new OnGlobalLayoutListener() {
    @Override
    public void onGlobalLayout() {
        view.getViewTreeObserver().removeOnGlobalLayoutListener(this);
        int width = view.getWidth();
        int height = view.getHeight();
    }
});
```

---

*文档创建时间：2026-03-07*
*来源：Android 源码分析 + 知识体系总结*