# Android 事件分发机制详解

> 作者：OpenClaw | 日期：2026-03-08

---

## 目录

1. [概述](#1-概述)
2. [事件类型](#2-事件类型)
   - 2.1 [触摸事件 (MotionEvent)](#21-触摸事件-motionevent)
   - 2.2 [事件批次](#22-事件批次)
3. [分发流程](#3-分发流程)
   - 3.1 [整体流程图](#31-整体流程图)
   - 3.2 [传递顺序](#32-传递顺序)
4. [核心方法详解](#4-核心方法详解)
   - 4.1 [方法签名](#41-方法签名)
   - 4.2 [方法返回值含义](#42-方法返回值含义)
5. [dispatchTouchEvent](#5-dispatchtouchevent)
   - 5.1 [作用](#51-作用)
   - 5.2 [ViewGroup 中的实现逻辑](#52-viewgroup-中的实现逻辑)
   - 5.3 [关键点](#53-关键点)
6. [onInterceptTouchEvent](#6-onintercepttouchevent)
   - 6.1 [作用](#61-作用)
   - 6.2 [默认实现](#62-默认实现)
   - 6.3 [拦截时机](#63-拦截时机)
   - 6.4 [拦截后的处理](#64-拦截后的处理)
7. [onTouchEvent](#7-ontouchevent)
   - 7.1 [作用](#71-作用)
   - 7.2 [View 的默认实现](#72-view-的默认实现)
   - 7.3 [关键结论](#73-关键结论)
8. [事件传递规则](#8-事件传递规则)
   - 8.1 [传递规则总结](#81-传递规则总结)
   - 8.2 [核心规则](#82-核心规则)
   - 8.3 [ACTION_DOWN 的特殊性](#83-action_down-的特殊性)
9. [ViewGroup 事件分发](#9-viewgroup-事件分发)
   - 9.1 [分发流程](#91-分发流程)
   - 9.2 [触摸目标 (TouchTarget)](#92-触摸目标-touchtarget)
10. [View 事件分发](#10-view-事件分发)
    - 10.1 [分发流程](#101-分发流程)
    - 10.2 [优先级](#102-优先级)
    - 10.3 [onTouchEvent 详解](#103-ontouchevent-详解)
11. [Activity 事件分发](#11-activity-事件分发)
    - 11.1 [Activity 的 dispatchTouchEvent](#111-activity-的-dispatchtouchevent)
    - 11.2 [Activity 的 onTouchEvent](#112-activity-的-ontouchevent)
12. [典型场景分析](#12-典型场景分析)
    - 场景一：子 View 处理事件
    - 场景二：ViewGroup 拦截事件
    - 场景三：子 View 不处理事件
    - 场景四：多层嵌套不处理
    - 场景五：子 View 重叠时的分配
13. [TouchDelegate 扩大点击区域](#13-touchdelegate-扩大点击区域)
    - 13.1 [使用场景](#131-使用场景)
    - 13.2 [实现方式](#132-实现方式)
    - 13.3 [原理详解](#133-原理详解)
      - 13.3.1 [View.setTouchDelegate()](#1331-viewsettouchdelegate)
      - 13.3.2 [TouchDelegate 类定义](#1332-touchdelegate-类定义)
      - 13.3.3 [View.dispatchTouchEvent() 中调用](#1333-viewdispatchtouchevent-中调用-touchdelegate)
      - 13.3.4 [TouchDelegate 工作流程图](#1334-touchdelegate-工作流程图)
      - 13.3.5 [坐标转换示意图](#1335-坐标转换示意图)
      - 13.3.6 [注意事项](#1336-注意事项)
14. [滑动冲突解决](#14-滑动冲突解决)
    - 14.1 [常见滑动冲突场景](#141-常见滑动冲突场景)
    - 14.2 [解决策略](#142-解决策略)
15. [源码解析](#15-源码解析)
    - 15.1 [ViewGroup.findTouchTarget](#151-viewgroupfindtouchtarget)
    - 15.2 [dispatchTransformedTouchEvent](#152-dispatchtransformedtouchevent)
16. [最佳实践](#16-最佳实践)
    - 16.1 [开发建议](#161-开发建议)

---

## 1. 概述

Android 事件分发机制是 Android 触摸事件传递的核心机制，它决定了用户触摸屏幕时，事件如何从 Activity 传递到最终的 View 进行处理。理解这一机制对于解决滑动冲突、自定义 View、开发复杂交互应用至关重要。

事件分发涉及三个核心方法：
- `dispatchTouchEvent(MotionEvent)` - 事件分发
- `onInterceptTouchEvent(MotionEvent)` - 事件拦截（仅 ViewGroup 有）
- `onTouchEvent(MotionEvent)` - 事件处理

---

## 2. 事件类型

### 2.1 触摸事件 (MotionEvent)

Android 中最常用的是触摸事件，主要包括：

| 事件 | 常量 | 描述 |
|------|------|------|
| ACTION_DOWN | 0 | 手指按下屏幕 |
| ACTION_UP | 1 | 手指离开屏幕 |
| ACTION_MOVE | 2 | 手指在屏幕上滑动 |
| ACTION_CANCEL | 3 | 事件被取消 |
| ACTION_POINTER_DOWN | 5 | 多指按下（第二个手指） |
| ACTION_POINTER_UP | 6 | 多指抬起（第二个手指） |

### 2.2 事件批次

一个完整的触摸序列通常以 ACTION_DOWN 开始，以 ACTION_UP 结束：

```
DOWN → [MOVE → MOVE → ...] → UP
```

中间可能穿插 ACTION_CANCEL 表示事件被中断。

---

## 3. 分发流程

### 3.1 整体流程图

```
Activity
    ↓ dispatchTouchEvent
ViewGroup (DecorView)
    ↓ dispatchTouchEvent
    ↓ onInterceptTouchEvent
    ↓ (如果拦截)
View
    ↓ dispatchTouchEvent
    ↓ onTouchEvent
    ↓ (如果不处理)
ViewGroup
    ↓ onTouchEvent
Activity
    ↓ onTouchEvent
```

### 3.2 传递顺序

事件传递遵循自上而下的顺序：

1. **Activity** → 2. **ViewGroup** → 3. **View**

处理结果则自下而上返回：

1. **View** → 2. **ViewGroup** → 3. **Activity**

---

## 4. 核心方法详解

### 4.1 方法签名

```java
// Activity
public boolean dispatchTouchEvent(MotionEvent ev)

// ViewGroup
public boolean dispatchTouchEvent(MotionEvent ev)
public boolean onInterceptTouchEvent(MotionEvent ev)
public boolean onTouchEvent(MotionEvent ev)

// View
public boolean dispatchTouchEvent(MotionEvent ev)
public boolean onTouchEvent(MotionEvent ev)
```

### 4.2 方法返回值含义

| 返回值 | 含义 |
|--------|------|
| true | 事件被当前组件消费，不再继续传递 |
| false | 事件未被处理，传递给父容器 |

---

## 5. dispatchTouchEvent

### 5.1 作用

`dispatchTouchEvent` 是事件分发的入口方法，负责决定事件是交给自身处理还是传递给子 View。

### 5.2 ViewGroup 中的实现逻辑

```java
public boolean dispatchTouchEvent(MotionEvent ev) {
    // 1. 检查是否需要取消当前事件
    if (actionMasked == MotionEvent.ACTION_DOWN) {
        // 重置触摸状态
        mFirstTouchTarget = null;
    }
    
    // 2. 检查是否拦截
    if (onInterceptTouchEvent(ev)) {
        // 拦截事件，交给自身的 onTouchEvent 处理
        ev.setAction(MotionEvent.ACTION_CANCEL);
        return super.onTouchEvent(ev);
    }
    
    // 3. 查找触摸目标（子 View）
    TouchTarget target = findTouchTarget(child, x, y);
    
    if (target != null) {
        // 4. 分发给子 View
        if (dispatchTransformedTouchEvent(ev, false, target.child, idBitsToAssign)) {
            // 子 View 处理了事件
            mFirstTouchTarget = target;
            return true;
        }
    }
    
    // 5. 如果没有子 View 处理，交给自身的 onTouchEvent
    return super.onTouchEvent(ev);
}
```

### 5.3 关键点

- ACTION_DOWN 是事件序列的开始，会重置状态
- 只有当 mFirstTouchTarget 为 null 时才会调用 onInterceptTouchEvent
- 子 View 处理事件后会设置 mFirstTouchTarget

---

## 6. onInterceptTouchEvent

### 6.1 作用

`onInterceptTouchEvent` 用于 ViewGroup 判断是否拦截子 View 的事件。

### 6.2 默认实现

```java
public boolean onInterceptTouchEvent(MotionEvent ev) {
    // 默认不拦截
    return false;
}
```

### 6.3 拦截时机

| 事件 | 是否调用 onInterceptTouchEvent |
|------|------|
| ACTION_DOWN | 总是调用 |
| ACTION_MOVE | 如果 mFirstTouchTarget 不为 null |
| ACTION_UP | 如果 mFirstTouchTarget 不为 null |
| ACTION_CANCEL | 不调用 |

### 6.4 拦截后的处理

当 onInterceptTouchEvent 返回 true 拦截事件时：
1. 当前 ViewGroup 的 dispatchTouchEvent 会调用自身的 onTouchEvent
2. 子 View 会收到 ACTION_CANCEL 事件
3. mFirstTouchTarget 会被置为 null

---

## 7. onTouchEvent

### 7.1 作用

`onTouchEvent` 是真正处理触摸事件的方法。

### 7.2 View 的默认实现

```java
public boolean onTouchEvent(MotionEvent event) {
    final int action = event.getAction();
    
    // 可点击的 View 会消费事件
    if (isClickable() || isLongClickable()) {
        switch (action) {
            case MotionEvent.ACTION_UP:
                // 处理点击
                performClick();
                break;
            case MotionEvent.ACTION_DOWN:
                // 记录按下状态
                break;
        }
        return true; // 消费事件
    }
    
    return false; // 不消费，向上传递
}
```

### 7.3 关键结论

- **可点击的 View**（clickable 或 longClickable 为 true）默认会消费事件
- **不可点击的 View** 默认不消费事件
- 消费事件返回 true 后，事件不再向上传递

---

## 8. 事件传递规则

### 8.1 传递规则总结

```
┌─────────────────────────────────────────────────────────────┐
│                         Activity                             │
│                  dispatchTouchEvent                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      ViewGroup                               │
│              dispatchTouchEvent                              │
│                    ↓                                        │
│           onInterceptTouchEvent?                             │
│              ↓ (true/false)                                  │
│    ┌─────────────┴─────────────┐                            │
│    ↓                             ↓                           │
│ 子View处理                  super.onTouchEvent               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                         View                                 │
│               dispatchTouchEvent                              │
│                    ↓                                        │
│           onTouchEvent?                                      │
│              ↓ (true/false)                                  │
│         (消费/不消费)                                         │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 核心规则

1. **dispatchTouchEvent 返回 true**：事件被消费，不再传递
2. **dispatchTouchEvent 返回 false**：事件回传给父容器的 onTouchEvent
3. **onInterceptTouchEvent 返回 true**：拦截事件，交给自身的 onTouchEvent 处理
4. **onInterceptTouchEvent 返回 false**：不拦截，传递给子 View
5. **onTouchEvent 返回 true**：事件被消费，不再传递
6. **onTouchEvent 返回 false**：事件未处理，回传给父容器

### 8.3 ACTION_DOWN 的特殊性

- ACTION_DOWN 是每个事件序列的起点
- 收到 ACTION_DOWN 时，ViewGroup 会重置状态
- 如果子 View 消费了 ACTION_DOWN，后续事件会直接分发给它
- 如果子 View 没有消费 ACTION_DOWN，整个事件序列都不会再传给该子 View

---

## 9. ViewGroup 事件分发

### 9.1 分发流程

```java
public boolean dispatchTouchEvent(MotionEvent ev) {
    // 1. 处理鼠标事件（hover、scroll 等）
    ...
    
    boolean handled = false;
    
    // 2. 检查是否拦截
    final boolean intercepted;
    if (actionMasked == MotionEvent.ACTION_DOWN || mFirstTouchTarget != null) {
        // 只有 DOWN 事件或者已经有目标时才检查拦截
        intercepted = onInterceptTouchEvent(ev);
    } else {
        intercepted = false;
    }
    
    // 3. 事件没有被拦截，分发给子 View
    if (!intercepted) {
        if (child != null) {
            // 分发给子 View
            handled = dispatchTransformedTouchEvent(ev, false, child, idBitsToAssign);
        }
    }
    
    // 4. 如果没有子 View 处理，交给自身处理
    if (!handled) {
        handled = super.onTouchEvent(ev); // 即 ViewGroup 的 onTouchEvent
    }
    
    return handled;
}
```

### 9.2 触摸目标 (TouchTarget)

```java
private static final class TouchTarget {
    public View child;          // 目标 View
    public TouchTarget next;   // 下一个目标（支持多指）
    public int pointerIdBits;   // 触摸点 ID
}
```

TouchTarget 是一个链表结构，用于支持多指触控。

---

## 10. View 事件分发

### 10.1 分发流程

```java
public boolean dispatchTouchEvent(MotionEvent event) {
    // 1. 如果设置了 OnTouchListener，优先调用 onTouch
    if (mListenerInfo != null && mListenerInfo.mOnTouchListener != null) {
        if (mListenerInfo.mOnTouchListener.onTouch(this, event)) {
            return true; // onTouch 处理了事件
        }
    }
    
    // 2. 如果 onTouch 没有处理，调用 onTouchEvent
    return onTouchEvent(event);
}
```

### 10.2 优先级

```
OnTouchListener.onTouch > View.onTouchEvent > OnClickListener.onClick
```

### 10.3 onTouchEvent 详解

```java
public boolean onTouchEvent(MotionEvent event) {
    final int action = event.getAction();

    // 检查是否可以点击
    if (clickable || longClickable) {
        switch (action) {
            case MotionEvent.ACTION_DOWN:
                // 记录按下时间、位置等
                break;
                
            case MotionEvent.ACTION_MOVE:
                // 检查是否移出 View 边界
                if (!isInBoundsOfChild) {
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
        return true; // 可点击的 View 始终返回 true
    }

    return false;
}
```

---

## 11. Activity 事件分发

### 11.1 Activity 的 dispatchTouchEvent

### 11.1 Activity 的 dispatchTouchEvent

```java
public boolean dispatchTouchEvent(MotionEvent ev) {
    // 事件首先分发给 Window（DecorView）
    if (getWindow().superDispatchTouchEvent(ev)) {
        return true; // 事件被消费
    }
    
    // 如果 Window 没有处理，交给 Activity 的 onTouchEvent
    return onTouchEvent(ev);
}
```

### 11.2 Activity 的 onTouchEvent

```java
public boolean onTouchEvent(MotionEvent event) {
    // 默认情况下：
    // - 如果窗口是dialog样式，且在边界外点击，关闭dialog
    // - 否则不处理，返回 false
    if (mWindow.shouldCloseOnTouch(this, event)) {
        finish();
        return true;
    }
    return false;
}
```

---

## 12. 典型场景分析

### 场景一：子 View 处理事件

```
DOWN 事件：
Activity.dispatchTouchEvent → ViewGroup.dispatchTouchEvent → 
ViewGroup.onInterceptTouchEvent(false) → Child.dispatchTouchEvent → 
Child.onTouchEvent(true) → 返回 true

后续事件（MOVE/UP）：
直接分发给 Child，不再经过 ViewGroup.onInterceptTouchEvent
```

### 场景二：ViewGroup 拦截事件

```
DOWN 事件：
Activity.dispatchTouchEvent → ViewGroup.dispatchTouchEvent → 
ViewGroup.onInterceptTouchEvent(true) → 
ViewGroup.onTouchEvent(true) → 返回 true

后续事件（MOVE/UP）：
ViewGroup 直接处理，不再分发给子 View
```

### 场景三：子 View 不处理事件

```
DOWN 事件：
Activity.dispatchTouchEvent → ViewGroup.dispatchTouchEvent → 
ViewGroup.onInterceptTouchEvent(false) → Child.dispatchTouchEvent → 
Child.onTouchEvent(false) → 返回 false

后续事件（MOVE/UP）：
不再分发给 Child，直接交给 ViewGroup.onTouchEvent
```

### 场景四：多层嵌套不处理

```
DOWN 事件：
Activity → ViewGroup1 → ViewGroup2 → View 
→ onTouchEvent(false) → 返回 false
→ ViewGroup2.onTouchEvent(false) → 返回 false  
→ ViewGroup1.onTouchEvent(false) → 返回 false
→ Activity.onTouchEvent(false) → 返回 false
```

### 场景五：子 View 重叠时的分配

当多个子 View 重叠时，触摸事件会分配给**最上层**（最后添加）的 View：

```
ViewGroup
    ├── Child1 (下层)
    ├── Child2 (中层)
    └── Child3 (上层) ← 优先分配给这个
```

**源码逻辑**（ViewGroup.findTouchTarget）：

```java
private TouchTarget findTouchTarget(View child, float x, float y) {
    final View[] children = mChildren;
    // 倒序遍历，最后添加的 View 优先检查
    for (int i = children.length - 1; i >= 0; i--) {
        final View child = children[i];
        // 检查触摸点是否在子 View 范围内
        if (!canViewReceivePointerEvents(child) 
                || !isTransformedTouchPointInView(x, y, child, null)) {
            continue;
        }
        // 找到目标，立即返回
        TouchTarget target = TouchTarget.obtain(child, pointerIdBits);
        return target;
    }
    return null;
}
```

**注意**：如果上层 View 不处理事件（onTouchEvent 返回 false），事件不会传递给下层 View，而是直接回传给父容器的 onTouchEvent。

---

## 13. TouchDelegate 扩大点击区域

### 13.1 使用场景

当 View 比较小难以点击时，可以通过 TouchDelegate 扩大其点击响应区域。

### 13.2 实现方式

```java
// 在父容器的 onFinishInflate 或 post 中设置
View parent = button.getParent();
if (parent instanceof ViewGroup) {
    ViewGroup viewGroup = (ViewGroup) parent;
    
    // 需要在 post 中执行，确保 View 已经布局
    viewGroup.post(new Runnable() {
        @Override
        public void run() {
            Rect bounds = new Rect();
            button.getHitRect(bounds);
            
            // 扩大 50px
            bounds.top -= 50;
            bounds.bottom += 50;
            bounds.left -= 50;
            bounds.right += 50;
            
            // ★★★ 注意：TouchDelegate 设置在 button 上，不是 viewGroup ★★★
            TouchDelegate delegate = new TouchDelegate(bounds, button);
            button.setTouchDelegate(delegate);
        }
    });
}
```

### 13.3 原理详解

TouchDelegate 会在 View.dispatchTouchEvent() 中被调用，如果触摸点落在代理区域内，会将事件转发给目标 View。

#### 13.3.1 View.setTouchDelegate()

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View.setTouchDelegate()                             │
│  源码位置: frameworks/base/core/java/android/view/View.java                 │
│  注意: setTouchDelegate() 是 View 的方法，不是 ViewGroup！                 │
└─────────────────────────────────────────────────────────────────────────────┘

  /**
   * Sets the TouchDelegate for this View.
   * 设置触摸代理，可以扩大 View 的点击区域
   */
  public void setTouchDelegate(TouchDelegate touchDelegate) {
      mTouchDelegate = touchDelegate;
  }
  
  // View 持有一个 TouchDelegate 引用
  TouchDelegate mTouchDelegate;
```

#### 13.3.2 TouchDelegate 类定义

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TouchDelegate 类定义                                │
│  源码位置: frameworks/base/core/java/android/view/TouchDelegate.java        │
└─────────────────────────────────────────────────────────────────────────────┘

  /**
   * Helper class to handle situations where you want a view to have a larger 
   * touch area than its actual view bounds.
   * 
   * 触摸代理类，可以让 View 拥有比其实际边界更大的触摸区域
   */
  public class TouchDelegate {
      
      /**
       * View that should receive forwarded touches
       * 目标 View，接收转发的触摸事件
       */
      private View mDelegateView;
      
      /**
       * Bounds in local coordinates of the containing view that should be mapped 
       * to the delegate view.
       * 代理区域（父 View 坐标系中的矩形区域）
       */
      private Rect mBounds;
      
      /**
       * mBounds inflated to compensate for slop
       * 扩展后的边界（考虑触摸 slop）
       */
      private Rect mSlopBounds;
      
      /**
       * True if the delegate is currently the target of a touch event sequence
       * 当前是否正在处理触摸序列（DOWN 后为 true，UP 后为 false）
       */
      private boolean mDelegateTargeted;
      
      /**
       * Constructor
       * @param bounds 父 View 坐标系中的代理区域
       * @param delegateView 目标 View
       */
      public TouchDelegate(Rect bounds, View delegateView) {
          mBounds = bounds;
          mSlopBounds = new Rect(bounds);
          mSlopBounds.inset(-ViewConfiguration.getTouchSlop(), 
                  -ViewConfiguration.getTouchSlop());
          mDelegateView = delegateView;
      }
      
      /**
       * Forward touch events to the delegate view if the event is within the 
       * bounds established in the constructor.
       * 
       * 如果触摸事件在代理区域内，将事件转发给目标 View
       *
       * @param event The touch event to forward
       * @return True if the event was forwarded, false otherwise
       */
      public boolean onTouchEvent(MotionEvent event) {
          int x = (int) event.getX();
          int y = (int) event.getY();
          boolean sendToDelegate = true;
          boolean hit = true;
          boolean handled = false;
          
          switch (event.getAction()) {
              case MotionEvent.ACTION_DOWN:
                  // ★★★ DOWN 事件：检查是否在代理区域内 ★★★
                  mDelegateTargeted = mBounds.contains(x, y);
                  if (!mDelegateTargeted) {
                      // 不在代理区域内，不处理
                      sendToDelegate = false;
                  }
                  break;
                  
              case MotionEvent.ACTION_MOVE:
                  // ★★★ MOVE 事件：检查是否在 slop 边界内 ★★★
                  // 即使移出原始边界，只要还在 slop 边界内，仍转发
                  if (!mSlopBounds.contains(x, y)) {
                      // 移出了 slop 边界
                      hit = false;
                  }
                  sendToDelegate = mDelegateTargeted;
                  break;
                  
              case MotionEvent.ACTION_UP:
              case MotionEvent.ACTION_CANCEL:
                  // ★★★ UP/CANCEL 事件：结束触摸序列 ★★★
                  sendToDelegate = mDelegateTargeted;
                  mDelegateTargeted = false;
                  break;
          }
          
          if (sendToDelegate) {
              // ★★★ 关键：将事件坐标转换为目标 View 的坐标系 ★★★
              final Rect delegateViewBounds = new Rect();
              mDelegateView.getHitRect(delegateViewBounds);
              
              if (hit) {
                  // 事件在代理区域内，转发给目标 View
                  // 注意：坐标需要转换
                  event.setLocation(
                          x - delegateViewBounds.left, 
                          y - delegateViewBounds.top);
                  
                  // ★★★ 调用目标 View 的 onTouchEvent ★★★
                  handled = mDelegateView.onTouchEvent(event);
              } else {
                  // 事件移出了代理区域，发送 CANCEL 事件
                  event.setLocation(
                          x - delegateViewBounds.left, 
                          y - delegateViewBounds.top);
                  
                  final MotionEvent cancelEvent = MotionEvent.obtain(event);
                  cancelEvent.setAction(MotionEvent.ACTION_CANCEL);
                  mDelegateView.onTouchEvent(cancelEvent);
                  cancelEvent.recycle();
              }
          }
          
          return handled;
      }
  }
```

#### 13.3.3 View.dispatchTouchEvent() 中调用 TouchDelegate

```
┌─────────────────────────────────────────────────────────────────────────────┐
│          View.dispatchTouchEvent() 中调用 TouchDelegate                     │
│  源码位置: frameworks/base/core/java/android/view/View.java                 │
│  注意: TouchDelegate 是在 View 中调用的，不是 ViewGroup！                   │
└─────────────────────────────────────────────────────────────────────────────┘

  public boolean dispatchTouchEvent(MotionEvent event) {
      // ... 省略其他代码
      
      // ★★★ 如果有 TouchDelegate，先让代理处理 ★★★
      if (mTouchDelegate != null) {
          if (mTouchDelegate.onTouchEvent(event)) {
              return true;  // TouchDelegate 消费了事件
          }
      }
      
      // 如果 TouchDelegate 没有消费，继续自己的 onTouchEvent
      if (onTouchEvent(event)) {
          return true;
      }
      
      return false;
  }
  
  // ★★★ 重要说明 ★★★
  // 1. TouchDelegate 是 View 的成员变量，不是 ViewGroup 的
  // 2. 所以 TouchDelegate 只对设置了它的那个 View 生效
  // 3. 通常在父 ViewGroup 中调用 子View.setTouchDelegate() 来设置
  // 4. 实际触摸事件仍然要先到达父 ViewGroup，然后分发到子 View
  // 5. 子 View 的 dispatchTouchEvent 才会调用 TouchDelegate
```

#### 13.3.4 TouchDelegate 工作流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TouchDelegate 工作流程                              │
│  注意: TouchDelegate 是设置在目标 View 上的，不是父 ViewGroup               │
└─────────────────────────────────────────────────────────────────────────────┘

  用户触摸屏幕
        │
        ▼
  ViewGroup.dispatchTouchEvent(ev)
        │
        │  正常事件分发流程
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  目标 View.dispatchTouchEvent(ev)                                       │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  // ★★★ 关键代码 ★★★                                                   │
  │  if (mTouchDelegate != null) {                                          │
  │      if (mTouchDelegate.onTouchEvent(ev)) {                             │
  │          return true;  // TouchDelegate 处理了事件                      │
  │      }                                                                  │
  │  }                                                                      │
  │                                                                         │
  │  // TouchDelegate 没处理，继续自己的 onTouchEvent                        │
  │  return onTouchEvent(ev);                                               │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        │  mTouchDelegate.onTouchEvent(ev)
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  TouchDelegate.onTouchEvent(ev)                                         │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  1. ACTION_DOWN:                                                        │
  │     检查触摸点 (x,y) 是否在 mBounds 内                                  │
  │         │                                                               │
  │         ├── 在区域内: mDelegateTargeted = true                          │
  │         │             转发给目标 View (就是自己)                        │
  │         │                                                               │
  │         └── 不在区域内: mDelegateTargeted = false                       │
  │                       返回 false，继续正常处理                          │
  │                                                                         │
  │  2. ACTION_MOVE:                                                        │
  │     if (mDelegateTargeted) {                                            │
  │         检查是否在 mSlopBounds 内                                       │
  │             │                                                           │
  │             ├── 在 slop 边界内: 转发给目标 View                         │
  │             │                                                           │
  │             └── 移出 slop 边界: 发送 CANCEL 给目标 View                  │
  │     }                                                                   │
  │                                                                         │
  │  3. ACTION_UP / CANCEL:                                                 │
  │     if (mDelegateTargeted) {                                            │
  │         转发给目标 View                                                 │
  │         mDelegateTargeted = false                                       │
  │     }                                                                   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  ★★★ 实际使用场景 ★★★
  ─────────────────────────────────────────────────────────────────────────────

  通常用法:
  1. 父 ViewGroup 获取子 View 的边界
  2. 扩大这个边界作为代理区域
  3. 创建 TouchDelegate 并设置到子 View 上
  
  Button button = findViewById(R.id.button);
  
  // 获取 button 在父 ViewGroup 中的位置
  Rect bounds = new Rect();
  button.getHitRect(bounds);  // 获取 button 的可点击矩形
  
  // 扩大点击区域
  bounds.inset(-50, -50);  // 向外扩展 50px
  
  // 创建 TouchDelegate，bounds 是代理区域，button 是目标 View
  TouchDelegate delegate = new TouchDelegate(bounds, button);
  
  // ★★★ 注意：TouchDelegate 设置在 button 上 ★★★
  button.setTouchDelegate(delegate);
  
  // 这样当触摸点落在 bounds 范围内时：
  // 1. 事件先分发到 button
  // 2. button.dispatchTouchEvent() 调用 TouchDelegate.onTouchEvent()
  // 3. TouchDelegate 判断触摸点在 bounds 内，返回 true
  // 4. button.onTouchEvent() 被调用，button 响应点击
```

#### 13.3.5 坐标转换示意图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         坐标转换示意图                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  ViewGroup 坐标系:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  (0,0)                                                                  │
  │     ┌────────────────────────────────┐                                 │
  │     │                                │                                 │
  │     │      TouchDelegate Bounds      │                                 │
  │     │     (代理区域)                  │                                 │
  │     │                                │                                 │
  │     │        ┌─────────────┐        │                                 │
  │     │        │  目标 View   │        │                                 │
  │     │        │  (Button)   │        │                                 │
  │     │        │  (40,50)    │        │                                 │
  │     │        │   ↓         │        │                                 │
  │     │        └─────────────┘        │                                 │
  │     │                                │                                 │
  │     └────────────────────────────────┘                                 │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  用户触摸点: ViewGroup 坐标系中的 (60, 70)
  
  坐标转换:
  event.setLocation(
      60 - 40 = 20,  // x - delegateViewBounds.left
      70 - 50 = 20   // y - delegateViewBounds.top
  )
  
  转换后: 目标 View 坐标系中的 (20, 20)
  
  目标 View 接收到的 MotionEvent 坐标是相对于自身的
```

#### 13.3.6 注意事项

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TouchDelegate 注意事项                              │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 只能设置一个 TouchDelegate
     ─────────────────────────────────────────────────────────────────────────
     View.setTouchDelegate() 会覆盖之前的设置
     如果需要多个代理区域，需要自定义实现

  2. 需要在 View 布局完成后设置
     ─────────────────────────────────────────────────────────────────────────
     // 错误方式：View 还没布局，bounds 为空
     TouchDelegate delegate = new TouchDelegate(bounds, button);
     button.setTouchDelegate(delegate);
     
     // 正确方式：在 post 中设置
     button.post(() -> {
         Rect bounds = new Rect();
         button.getHitRect(bounds);
         bounds.inset(-50, -50);
         button.setTouchDelegate(new TouchDelegate(bounds, button));
     });

  3. 代理区域不能超出父 View 边界
     ─────────────────────────────────────────────────────────────────────────
     TouchDelegate 只能处理落在父 View 内的触摸事件
     超出父 View 的事件不会传递到该 View

  4. 事件坐标会被修改
     ─────────────────────────────────────────────────────────────────────────
     目标 View 收到的 MotionEvent 坐标已经被转换
     如果需要原始坐标，需要在转发前保存

  5. 与 onClick 的关系
     ─────────────────────────────────────────────────────────────────────────
     TouchDelegate 转发 onTouchEvent，所以 onClick 也能正常触发
     只要目标 View 是 clickable 的
```

---

## 14. 滑动冲突解决

### 14.1 常见滑动冲突场景

1. **外部滑动方向与内部滑动方向不一致**
   - 例如：ViewPager 内部嵌套 RecyclerView
   
2. **外部滑动方向与内部滑动方向一致**
   - 例如：两个 RecyclerView 嵌套

3. **以上两种情况混合**

### 14.2 解决策略

#### 策略一：父容器不拦截

```java
public class CustomViewGroup extends ViewGroup {
    private int mLastX;
    private int mLastY;
    
    @Override
    public boolean onInterceptTouchEvent(MotionEvent ev) {
        boolean intercepted = false;
        
        switch (ev.getAction()) {
            case MotionEvent.ACTION_DOWN:
                intercepted = false; // 不拦截 DOWN
                break;
                
            case MotionEvent.ACTION_MOVE:
                // 根据滑动方向决定是否拦截
                int deltaX = (int) (ev.getX() - mLastX);
                int deltaY = (int) (ev.getY() - mLastY);
                
                if (Math.abs(deltaX) > Math.abs(deltaY)) {
                    // 水平滑动，拦截
                    intercepted = true;
                } else {
                    // 垂直滑动，不拦截
                    intercepted = false;
                }
                break;
                
            case MotionEvent.ACTION_UP:
                intercepted = false;
                break;
        }
        
        mLastX = ev.getX();
        mLastY = ev.getY();
        
        return intercepted;
    }
}
```

#### 策略二：请求父容器不拦截

```java
childView.setOnTouchListener(new View.OnTouchListener() {
    @Override
    public boolean onTouch(View v, MotionEvent event) {
        switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
                // 请求父容器不拦截
                getParent().requestDisallowInterceptTouchEvent(true);
                break;
                
            case MotionEvent.ACTION_UP:
                // 恢复父容器拦截能力
                getParent().requestDisallowInterceptTouchEvent(false);
                break;
        }
        return false; // 事件继续传递
    }
});
```

---

## 15. 源码解析

### 15.1 ViewGroup.findTouchTarget

```java
private TouchTarget findTouchTarget(View child, float x, float y) {
    final View[] children = mChildren;
    for (int i = children.length - 1; i >= 0; i--) {
        final View child = children[i];
        // 检查触摸点是否在子 View 范围内
        if (!canViewReceivePointerEvents(child) 
                || !isTransformedTouchPointInView(x, y, child, null)) {
            continue;
        }
        // 找到目标
        TouchTarget target = TouchTarget.obtain(child, pointerIdBits);
        return target;
    }
    return null;
}
```

### 15.2 dispatchTransformedTouchEvent

```java
private boolean dispatchTransformedTouchEvent(MotionEvent event, boolean cancel,
        View child, int desiredPointerIdBits) {
    
    final boolean handled;
    
    // 如果有子 View，调用子 View 的 dispatchTouchEvent
    if (child != null) {
        handled = child.dispatchTouchEvent(event);
    } else {
        // 没有子 View，调用 super（即 View 的）dispatchTouchEvent
        handled = super.dispatchTouchEvent(event);
    }
    
    return handled;
}
```

---

## 16. 最佳实践

### 16.1 开发建议

1. **不要在 onInterceptTouchEvent 中做耗时操作**
   - 因为每次 MOVE 事件都会调用

2. **谨慎使用 requestDisallowInterceptTouchEvent**
   - 容易导致父容器无法响应点击事件

3. **处理滑动冲突时，优先考虑外部拦截**
   - 内部拦截需要更多代码

4. **注意 ACTION_DOWN 的初始化作用**
   - 重置状态、决定后续事件目标

### 16.2 常见问题排查

1. **点击事件无响应**
   - 检查 View 是否可点击
   - 检查是否被父容器拦截
   - 检查 onTouchEvent 是否返回 true

2. **滑动事件被父容器拦截**
   - 使用 requestDisallowInterceptTouchEvent
   - 或在 onInterceptTouchEvent 中正确判断滑动方向

3. **多指触控问题**
   - 使用 getActionMasked() 而非 getAction()
   - 使用 getPointerId() 和 getPointerIndex()

### 16.3 性能优化

1. **避免在事件分发中创建对象**
   - 减少 GC 压力

2. **使用硬件加速**
   - 提升绘制性能

3. **合理使用标志位**
   - 避免重复计算

---

## 总结

Android 事件分发机制是理解 Android 触摸交互的核心。关键点包括：

1. **三层传递**：Activity → ViewGroup → View
2. **核心方法**：dispatchTouchEvent、onInterceptTouchEvent、onTouchEvent
3. **事件序列**：以 ACTION_DOWN 开始，ACTION_UP 结束
4. **返回值的意义**：true 表示消费，false 表示不处理/继续传递
5. **滑动冲突**：通过拦截策略或 requestDisallowInterceptTouchEvent 解决

掌握这一机制，能够帮助开发者轻松应对复杂的交互需求，实现流畅的用户体验。

---

*文档创建时间：2026-03-07*
*来源：Android 官方文档 + 源码分析 + 实践经验 + Feishu 八股文*
