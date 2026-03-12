# Android InputManager 输入系统深度解析

> 作者：OpenClaw | 日期：2026-03-12  
> 基于源码：Android 16 (API 36) AOSP

## 目录

1. [概述](#1-概述)
2. [IMS 架构总览](#2-ims-架构总览)
3. [输入事件读取 (EventHub)](#3-输入事件读取-eventhub)
4. [输入事件分发流程](#4-输入事件分发流程)
5. [InputChannel 与 InputConnection](#5-inputchannel-与-inputconnection)
6. [触摸事件处理](#6-触摸事件处理)
7. [按键事件处理](#7-按键事件处理)
8. [输入法交互](#8-输入法交互)
9. [手势识别](#9-手势识别)
10. [事件拦截与分发详解](#10-事件拦截与分发详解)
11. [源码路径](#11-源码路径)
12. [面试常见问题](#12-面试常见问题)

---

## 1. 概述

**InputManagerService (IMS)** 是 Android 系统的核心服务之一，负责管理所有输入设备的事件读取、分发和处理，包括触摸屏、键盘、鼠标、游戏手柄等。

### 1.1 IMS 的核心职责

```
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
│  │  4. 输入法支持 (IME Support)                              │  │
│  │     • 输入法连接                                          │  │
│  │     • 文本编辑                                            │  │
│  │     • 软键盘事件                                          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 IMS 在系统中的位置

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Android 输入系统架构                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    内核层 (Kernel Layer)                             │ │
│   │                                                                      │ │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│   │   │/dev/input/   │  │ Touchscreen │  │   Keyboard   │            │ │
│   │   │eventX        │  │ Driver       │  │   Driver     │            │ │
│   │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │ │
│   │          │                 │                 │                      │ │
│   └──────────┼─────────────────┼─────────────────┼──────────────────────┘ │
│              │                 │                 │                          │
│              ▼                 ▼                 ▼                          │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                    Native 层 (InputFlinger)                          │ │
│   │                                                                      │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                    EventHub                                  │ │ │
│   │   │                    (事件集线器)                              │ │ │
│   │   └──────────────────────────┬───────────────────────────────────┘ │ │
│   │                               │                                     │ │
│   │                               ▼                                     │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                    InputReader                               │ │ │
│   │   │                    (输入读取器)                              │ │ │
│   │   └──────────────────────────┬───────────────────────────────────┘ │ │
│   │                               │                                     │ │
│   │                               ▼                                     │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                    InputClassifier                           │ │ │
│   │   │                    (输入分类器)                              │ │ │
│   │   └──────────────────────────┬───────────────────────────────────┘ │ │
│   │                               │                                     │ │
│   │                               ▼                                     │ │
│   │   ┌──────────────────────────────────────────────────────────────┐ │ │
│   │   │                    InputDispatcher                           │ │ │
│   │   │                    (输入分发器)                              │ │ │
│   │   └──────────────────────────┬───────────────────────────────────┘ │ │
│   │                               │                                     │ │
│   └───────────────────────────────┼─────────────────────────────────────┘ │
│                                   │                                        │
│                                   ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────────┐│
│   │                    Java 层 (InputManagerService)                      ││
│   │                                                                        ││
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              ││
│   │   │InputManager  │  │WindowManager │  │InputMethodManager             ││
│   │   │Service       │  │Service       │  │              │              ││
│   │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              ││
│   │          │                 │                 │                        ││
│   └──────────┼─────────────────┼─────────────────┼────────────────────────┘│
│              │                 │                 │                          │
│              ▼                 ▼                 ▼                          │
│   ┌───────────────────────────────────────────────────────────────────────┐│
│   │                    应用层 (Application Layer)                         ││
│   │                                                                        ││
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              ││
│   │   │   View       │  │  Activity    │  │  Dialog      │              ││
│   │   │onTouchEvent()│  │dispatchKeyEvent()│            │              ││
│   │   └──────────────┘  └──────────────┘  └──────────────┘              ││
│   │                                                                        ││
│   └────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. IMS 架构总览

### 2.1 IMS 内部架构

```
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
│   │   │   │InputClassifier│ │InputListener │  │InputChannel  │     │ │ │
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

```
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EventHub 架构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

EventHub 职责：
1. 监控 /dev/input/ 目录
2. 读取原始输入事件
3. 设备热插拔检测
4. 设备能力查询

设备文件：
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

```
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
           └─► 生成 MotionEvent
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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        输入事件分发流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

InputDispatcher                  WMS                    应用进程
       │                          │                         │
       ▼                          │                         │
┌───────────────┐                │                         │
│notifyMotion() │                │                         │
└───────┬───────┘                │                         │
        │                        │                         │
        ▼                        │                         │
┌───────────────┐                │                         │
│确定目标窗口   │                │                         │
│               │                │                         │
│• 查找焦点窗口 │                │                         │
│• 检查权限     │                │                         │
└───────┬───────┘                │                         │
        │                        │                         │
        │                        │                         │
        └────────┬───────────────┤                         │
                 │               │                         │
                 ▼               │                         │
        ┌───────────────┐        │                         │
        │InputChannel   │        │                         │
        │(Unix Socket)  │        │                         │
        └───────┬───────┘        │                         │
                │                │                         │
                │                │                         │
                └────────────────┼─────────────────────────┤
                                 │                         │
                                 ▼                         │
                        ┌───────────────┐                  │
                        │ViewRootImpl   │                  │
                        │.dispatchMotion│                  │
                        └───────┬───────┘                  │
                                │                          │
                                ▼                          │
                        ┌───────────────┐                  │
                        │View 分发      │                  │
                        │               │                  │
                        │1. DecorView   │                  │
                        │2. ViewGroup   │                  │
                        │3. View        │                  │
                        └───────┬───────┘                  │
                                │                          │
                                ▼                          │
                        ┌───────────────┐                  │
                        │onTouchEvent() │                  │
                        └───────────────┘                  │
```

### 4.2 InputDispatcher 分发逻辑

```java
/**
 * InputDispatcher - 输入分发器
 * 位置：frameworks/native/services/inputflinger/InputDispatcher.cpp
 */
class InputDispatcher {
    
    /**
     * 处理触摸事件
     */
    void InputDispatcher::notifyMotion(const MotionEvent* motionEvent) {
        // 1. 验证事件
        if (!validateMotionEvent(motionEvent)) {
            return;
        }
        
        // 2. 入队等待分发
        mInboundQueue.push(motionEvent);
        
        // 3. 唤醒分发线程
        mLooper->wake();
    }
    
    /**
     * 分发循环
     */
    void InputDispatcher::dispatchOnce() {
        // 1. 从队列取出事件
        EventEntry* entry = mInboundQueue.pop();
        
        // 2. 确定目标窗口
        Vector<InputTarget> targets;
        findFocusedWindowTargetsLocked(entry, targets);
        
        // 3. 分发到目标窗口
        for (InputTarget target : targets) {
            dispatchEventLocked(entry, target);
        }
        
        // 4. 等待应用响应
        // 5. 处理 ANR
    }
    
    /**
     * 查找焦点窗口
     */
    void InputDispatcher::findFocusedWindowTargetsLocked(
            EventEntry* entry, Vector<InputTarget>& targets) {
        // 从 WMS 获取焦点窗口
        sp<InputWindowHandle> focusedWindow = 
                mInputManager->getFocusedWindow();
        
        // 添加到目标列表
        targets.push(focusedWindow);
    }
}
```

### 4.3 ANR 处理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        输入事件 ANR 处理                                    │
└─────────────────────────────────────────────────────────────────────────────┘

ANR 触发条件：
• 按键事件: 5 秒内未处理
• 触摸事件: 5 秒内未处理 (前台)
• 触摸事件: 10 秒内未处理 (后台)

ANR 检测流程：
1. InputDispatcher 分发事件后启动计时
2. 等待应用通过 finishInputEvent() 响应
3. 超时后触发 ANR

ANR 处理：
1. 打印 ANR 日志
2. 生成 traces.txt
3. 显示 ANR 对话框
4. 可选: 杀死进程

ANR 日志位置：
• /data/anr/traces.txt
• /data/anr/anr_* (Android 11+)

避免 ANR：
• 主线程不做耗时操作
• 快速处理输入事件
• 使用异步任务处理耗时工作
```

---

## 5. InputChannel 与 InputConnection

### 5.1 InputChannel

```java
/**
 * InputChannel - 输入通道
 * 位置：frameworks/base/core/java/android/view/InputChannel.java
 * 
 * 职责：应用与 IMS 之间的通信通道
 */
class InputChannel {
    // Native 层实现
    private long mPtr;  // Native 指针
    
    // 创建 InputChannel 对 (Unix Socket Pair)
    public static void openInputChannelPair(String name,
            InputChannel[] outChannels) {
        // 创建两个关联的 InputChannel
        // 一个给 IMS，一个给应用
    }
    
    // Native 方法
    private native long nativeOpenInputChannelPair(String name,
            InputChannel[] outChannels);
}

/**
 * InputChannel 使用流程
 * 
 * 1. ViewRootImpl 创建 InputChannel 对
 *    └─► InputChannel.openInputChannelPair()
 *        └─► 创建 Unix Socket Pair
 *
 * 2. 客户端 InputChannel 给应用
 *    └─► ViewRootImpl.setInputChannel()
 *
 * 3. 服务端 InputChannel 给 IMS
 *    └─► WMS.registerInputChannel()
 *
 * 4. IMS 通过服务端 InputChannel 发送事件
 *    └─► 写入 Unix Socket
 *
 * 5. 应用监听客户端 InputChannel
 *    └─► epoll_wait() 等待事件
 *    └─► 读取 Unix Socket
 *    └─► 分发到 View
 */
```

### 5.2 InputConnection

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

/**
 * InputConnection 实现类
 */
class BaseInputConnection implements InputConnection {
    // 关联的 View
    final View mTextView;
    
    // 文本编辑器
    final Editable mEditable;
    
    @Override
    public boolean commitText(CharSequence text, int newCursorPosition) {
        // 1. 提交文本
        mEditable.replace(selectionStart, selectionEnd, text);
        
        // 2. 更新光标位置
        setSelection(newCursorPosition, newCursorPosition);
        
        // 3. 通知 View 更新
        mTextView.invalidate();
        
        return true;
    }
}
```

---

## 6. 触摸事件处理

### 6.1 触摸事件类型

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

```
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

```java
/**
 * View.onTouchEvent()
 * 位置：frameworks/base/core/java/android/view/View.java
 */
public boolean onTouchEvent(MotionEvent event) {
    // 获取坐标
    final float x = event.getX();
    final float y = event.getY();
    
    // 检查是否可点击
    if ((viewFlags & CLICKABLE) == CLICKABLE ||
            (viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE) {
        
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                // 按下
                mHasPerformedLongPress = false;
                postDelayed(mPendingCheckForLongPress, 
                        ViewConfiguration.getLongPressTimeout());
                break;
                
            case MotionEvent.ACTION_MOVE:
                // 移动
                if (!pointInView(x, y, mTouchSlop)) {
                    // 移出 View，取消长按
                    removeCallbacks(mPendingCheckForLongPress);
                }
                break;
                
            case MotionEvent.ACTION_UP:
                // 抬起
                removeCallbacks(mPendingCheckForLongPress);
                if (!mHasPerformedLongPress) {
                    // 执行点击
                    performClick();
                }
                break;
                
            case MotionEvent.ACTION_CANCEL:
                // 取消
                removeCallbacks(mPendingCheckForLongPress);
                break;
        }
        
        return true; // 消费事件
    }
    
    return false; // 不消费事件
}
```

---

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

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        按键事件分发流程                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Activity.dispatchKeyEvent()
    │
    ├─► 焦点 View 处理
    │   │
    │   ▼
    │   View.dispatchKeyEvent()
    │   │
    │   ├─► onKey() - OnKeyListener
    │   │   │
    │   │   ├─► true: 消费
    │   │   └─► false: 继续
    │   │
    │   ▼
    │   View.onKeyDown() / onKeyUp()
    │   │
    │   ├─► true: 消费
    │   └─► false: 回传
    │
    ├─► Activity.onKeyDown() / onKeyUp()
    │   │
    │   ├─► true: 消费
    │   └─► false: 继续
    │
    └─► PhoneWindow.onKeyDown() / onKeyUp()
        │
        ├─► 处理系统按键 (音量/返回等)
        └─► 返回最终结果
```

### 7.3 系统按键处理

```java
/**
 * PhoneWindow.onKeyDown()
 * 位置：frameworks/base/core/java/com/android/internal/policy/PhoneWindow.java
 */
public boolean onKeyDown(int keyCode, KeyEvent event) {
    switch (keyCode) {
        case KeyEvent.KEYCODE_VOLUME_UP:
        case KeyEvent.KEYCODE_VOLUME_DOWN:
            // 调整音量
            AudioManager am = (AudioManager)getContext()
                    .getSystemService(Context.AUDIO_SERVICE);
            am.adjustVolume(
                    keyCode == KeyEvent.KEYCODE_VOLUME_UP 
                            ? AudioManager.ADJUST_RAISE 
                            : AudioManager.ADJUST_LOWER,
                    AudioManager.FLAG_SHOW_UI);
            return true;
            
        case KeyEvent.KEYCODE_BACK:
            // 返回键
            if (mPanel != null && mPanel.isShowing()) {
                // 关闭面板
                mPanel.closePanel();
                return true;
            }
            break;
            
        case KeyEvent.KEYCODE_MENU:
            // 菜单键
            if (mPanel != null) {
                mPanel.openPanel();
                return true;
            }
            break;
    }
    
    return false;
}
```

---

## 8. 输入法交互

### 8.1 输入法架构

```
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

```java
/**
 * InputMethodManager - 输入法管理器
 * 位置：frameworks/base/core/java/android/view/inputmethod/InputMethodManager.java
 */
class InputMethodManager {
    // 显示输入法
    public void showSoftInput(View view, int flags);
    
    // 隐藏输入法
    public boolean hideSoftInputFromWindow(IBinder windowToken, int flags);
    
    // 切换输入法
    public void toggleSoftInput(int showFlags, int hideFlags);
    
    // 获取输入法列表
    public List<InputMethodInfo> getInputMethodList();
    
    // 切换到指定输入法
    public void setInputMethod(IBinder token, String id);
}

/**
 * InputMethodService - 输入法服务
 * 位置：frameworks/base/core/java