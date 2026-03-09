# Android 事件分发机制详解

> 作者：OpenClaw | 日期：2026-03-08

---

## 目录

1. [概述](#1-概述)
2. [事件类型](#2-事件类型)
   - 2.1 [触摸事件 (MotionEvent)](#21-触摸事件-motionevent)
   - 2.2 [事件批次](#22-事件批次)
   - 2.3 [多指触控详解](#23-多指触控详解)
     - 2.3.1 [基本概念](#231-基本概念)
     - 2.3.2 [多指触控事件类型](#232-多指触控事件类型)
     - 2.3.3 [获取手指信息的关键方法](#233-获取手指信息的关键方法)
     - 2.3.4 [正确处理多指触控](#234-正确处理多指触控)
     - 2.3.5 [多指触控的事件分发](#235-多指触控的事件分发)
     - 2.3.6 [多指触控的典型场景](#236-多指触控的典型场景)
     - 2.3.7 [多指触控与 ViewGroup 分发](#237-多指触控与-viewgroup-分发)
     - 2.3.8 [多指触控常见问题](#238-多指触控常见问题)
     - 2.3.9 [手势检测器汇总](#239-手势检测器汇总)
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
   - 9.1 [分发入口](#91-分发入口)
   - 9.2 [如何找到并分发给子 View](#92-viewgroup-如何找到并分发给子-view)
   - 9.3 [isTransformedTouchPointInView - 边界检查](#93-istransformedtouchpointinview---检查触摸点是否在子-view-内)
   - 9.4 [dispatchTransformedTouchEvent - 分发事件](#94-dispatchtransformedtouchevent---分发事件)
   - 9.5 [子 View 收不到事件的原因](#95-子-view-收不到事件的原因)
   - 9.6 [TouchDelegate 为什么设置在父 ViewGroup 上](#96-touchdelegate-为什么设置在父-viewgroup-上)
   - 9.7 [TouchTarget 链表](#97-touchtarget-链表)
   - 9.8 [子 View 重叠时的触摸分配与 Z 轴](#98-子-view-重叠时的触摸分配与-z-轴)
     - 9.8.1 [触摸分配规则](#981-触摸分配规则)
     - 9.8.2 [源码解析](#982-源码解析)
     - 9.8.3 [View 的 Z 轴与层级](#983-view-的-z-轴与层级)
     - 9.8.4 [bringToFront() 详解](#984-bringtofront-详解)
     - 9.8.5 [触摸分配与 bringToFront 的关系](#985-触摸分配与-bringtofront-的关系)
     - 9.8.6 [实际开发中的应用场景](#986-实际开发中的应用场景)
     - 9.8.7 [注意事项](#987-注意事项)
     - 9.8.8 [完整示例](#988-完整示例)
10. [View 事件分发](#10-view-事件分发)
    - 10.1 [分发入口](#101-分发入口)
    - 10.2 [事件处理优先级](#102-事件处理优先级)
    - 10.3 [onTouchEvent 详解](#103-ontouchevent-完整源码分析)
    - 10.4 [点击、长按、双击检测机制](#104-点击长按双击检测机制)
      - 10.4.1 [点击检测](#1041-点击检测click)
      - 10.4.2 [长按检测](#1042-长按检测long-click)
      - 10.4.3 [双击检测](#1043-双击检测double-tap)
      - 10.4.4 [完整示例](#1044-完整示例支持单击长按双击的-view)
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
    - 13.4 [完整示例](#134-完整示例)
    - 13.5 [多个子 View 的情况](#135-多个子-view-的情况)
    - 13.3 [原理详解](#133-原理详解)
      - 13.3.1 [TouchDelegate 基本概念](#1331-touchdelegate-基本概念)
      - 13.3.2 [View.setTouchDelegate() 源码](#1332-viewsettouchdelegate-源码)
      - 13.3.3 [TouchDelegate 类定义](#1333-touchdelegate-类定义)
      - 13.3.4 [View.dispatchTouchEvent() 中调用](#1334-viewdispatchtouchevent-中调用-touchdelegate)
      - 13.3.5 [完整工作流程](#1335-完整工作流程)
      - 13.3.6 [关键点总结](#1336-关键点总结)
      - 13.3.7 [正确使用方式](#1337-正确使用方式)
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

### 2.3 多指触控详解

#### 2.3.1 基本概念

多指触控（Multi-touch）是指同时有多根手指触摸屏幕的场景。Android 通过 **Pointer ID** 来区分不同的手指。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         多指触控核心概念                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  Pointer（指针）= 每一根手指
  Pointer ID = 手指的唯一标识符（从0开始分配）

  典型场景：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │    手指1 (Pointer ID=0)          手指2 (Pointer ID=1)                  │
  │         ●                            ●                                 │
  │         │                            │                                 │
  │         ▼                            ▼                                 │
  │                                                                         │
  │    ┌───────────────────────────────────────────────────────────────┐   │
  │    │                       屏幕                                     │   │
  │    │                                                               │   │
  │    │                                                               │   │
  │    └───────────────────────────────────────────────────────────────┘   │
  │                                                                         │
  │  事件序列：                                                          │
  │  ACTION_DOWN (pointerId=0)                                           │
  │      ↓                                                               │
  │  ACTION_POINTER_DOWN (pointerId=1)  ← 第二个手指按下                  │
  │      ↓                                                               │
  │  ACTION_MOVE (包含两个手指的信息)                                      │
  │      ↓                                                               │
  │  ACTION_POINTER_UP (pointerId=1)    ← 第二个手指抬起                   │
  │      ↓                                                               │
  │  ACTION_UP (pointerId=0)                                            │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 2.3.2 多指触控事件类型

| 事件 | 常量 | 值 | 描述 |
|------|------|-----|------|
| ACTION_DOWN | 0 | 0x0 | 第一个手指按下，**开始一个新的触摸序列** |
| ACTION_POINTER_DOWN | 5 | 0x5 | **其他手指**按下（第二个、第三个...） |
| ACTION_MOVE | 2 | 0x2 | 任意手指移动，**包含所有手指的位置信息** |
| ACTION_POINTER_UP | 6 | 0x6 | **其他手指**抬起（第二个、第三个...） |
| ACTION_UP | 1 | 0x1 | 最后一个手指抬起，**结束触摸序列** |
| ACTION_CANCEL | 3 | 0x3 | 整个触摸序列被取消 |

**重要**：`ACTION_POINTER_DOWN` 和 `ACTION_POINTER_UP` **不会结束触摸序列**，只有 `ACTION_UP` 才会。

#### 2.3.3 获取手指信息的关键方法

```java
// 获取当前触摸点数量（几根手指）
int pointerCount = event.getPointerCount();

// 获取指定索引的 Pointer ID
int pointerId = event.getPointerId(int pointerIndex);

// 根据 Pointer ID 获取指针索引
int pointerIndex = event.findPointerIndex(int pointerId);

// 获取指定索引手指的 X 坐标
float x = event.getX(int pointerIndex);

// 获取指定索引手指的 Y 坐标
float y = event.getY(int pointerIndex);

// 获取动作的指针索引（哪个手指触发了这个事件）
int actionIndex = event.getActionIndex();

// 获取动作（已废弃，使用 getActionMasked()）
int action = event.getAction();

// ★★★ 获取动作掩码（排除索引信息）★★★
int actionMasked = event.getActionMasked();

// 获取所有手指的位掩码（哪些手指在触摸）
int pointerIdBits = event.getPointerIdBits();
```

#### 2.3.4 正确处理多指触控

```java
@Override
public boolean onTouchEvent(MotionEvent event) {
    // ★★★ 必须使用 getActionMasked() ★★★
    int actionMasked = event.getActionMasked();
    
    switch (actionMasked) {
        case MotionEvent.ACTION_DOWN:
            // 第一个手指按下
            // 记录初始触摸
            mActivePointerId = event.getPointerId(0);
            mLastX = event.getX(0);
            mLastY = event.getY(0);
            break;
            
        case MotionEvent.ACTION_POINTER_DOWN:
            // ★★★ 新增手指按下 ★★★
            // 获取是第几个手指（actionIndex）
            int newPointerIndex = event.getActionIndex();
            int newPointerId = event.getPointerId(newPointerIndex);
            
            // 可以记录新增手指的位置
            float x = event.getX(newPointerIndex);
            float y = event.getY(newPointerIndex);
            break;
            
        case MotionEvent.ACTION_MOVE:
            // ★★★ 手指移动，遍历所有触摸点 ★★★
            // 注意：可能有多个手指在移动
            for (int i = 0; i < event.getPointerCount(); i++) {
                int pointerId = event.getPointerId(i);
                float x = event.getX(i);
                float y = event.getY(i);
                
                // 处理每个手指的移动
                if (pointerId == mActivePointerId) {
                    // 主手指
                    handlePrimaryMove(x, y);
                } else {
                    // 辅助手指（如双指缩放）
                    handleSecondaryMove(pointerId, x, y);
                }
            }
            break;
            
        case MotionEvent.ACTION_POINTER_UP:
            // ★★★ 某个手指抬起 ★★★
            int pointerIndex = event.getActionIndex();
            int pointerId = event.getPointerId(pointerIndex);
            
            if (pointerId == mActivePointerId) {
                // ★★★ 主手指抬起，切换到另一个手指 ★★★
                // 找到剩余手指中索引最小的作为新的主手指
                int newPointerIndex = pointerIndex == 0 ? 1 : 0;
                mActivePointerId = event.getPointerId(newPointerIndex);
                mLastX = event.getX(newPointerIndex);
                mLastY = event.getY(newPointerIndex);
            }
            break;
            
        case MotionEvent.ACTION_UP:
            // 最后一个手指抬起，触摸序列结束
            mActivePointerId = -1;
            break;
            
        case MotionEvent.ACTION_CANCEL:
            // 触摸序列被取消
            mActivePointerId = -1;
            break;
    }
    
    return true;
}
```

#### 2.3.5 多指触控的事件分发

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    多指触控的事件分发流程                                    │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 第一根手指按下：ACTION_DOWN
  ─────────────────────────────────────────────────────────────────────────────
     
     系统
       │
       ▼
     Activity.dispatchTouchEvent(DOWN, pointerId=0)
       │
       ▼
     ViewGroup.dispatchTouchEvent(DOWN, pointerId=0)
       │
       ├─► onInterceptTouchEvent(DOWN)
       │
       ├─► findTouchTarget() → 找到目标子 View
       │
       ├─► addTouchTarget(child, pointerIdBit=0x1)  ★ 将 pointerId 加入 TouchTarget
       │
       └─► mFirstTouchTarget 指向 [Child, pointerIdBit=0x1]
     
     后续 MOVE/UP 事件都会直接分发给这个 Child


  2. 第二根手指按下：ACTION_POINTER_DOWN
  ─────────────────────────────────────────────────────────────────────────────

     系统
       │
       ▼
     Activity.dispatchTouchEvent(POINTER_DOWN, pointerId=1)
       │
       ▼
     ViewGroup.dispatchTouchEvent(POINTER_DOWN, pointerId=1)
       │
       ├─► onInterceptTouchEvent(POINTER_DOWN)  ★ 也会调用！
       │
       ├─► 遍历子 View，找新手指的目标
       │     （同一点评下可能找到不同或相同的子 View）
       │
       ├─► 如果找到新目标：
       │     addTouchTarget(newChild, pointerIdBit=0x2)
       │
       └─► mFirstTouchTarget 可能指向多个目标
           ┌─────────────────────────────────────────┐
           │  TouchTarget 链表结构                   │
           │  mFirstTouchTarget → [ChildA, id=0x1]  │
           │                        → [ChildB, id=0x2]│
           │                        → null           │
           └─────────────────────────────────────────┘

     ★★★ 关键：每个 pointerId 有自己的 TouchTarget ★★★


  3. 手指移动：ACTION_MOVE
  ─────────────────────────────────────────────────────────────────────────────

     系统
       │
       ▼
     Activity.dispatchTouchEvent(MOVE, 包含所有手指信息)
       │
       ▼
     ViewGroup.dispatchTouchEvent(MOVE)
       │
       ▼
     遍历 TouchTarget 链表，分发给所有目标：
     
     TouchTarget target = mFirstTouchTarget;
     while (target != null) {
         // 分发事件给每个目标
         dispatchTransformedTouchEvent(ev, false, 
                 target.child, target.pointerIdBits);
         target = target.next;
     }
     
     ★★★ 重要 ★★★
     - 所有被触摸的子 View 都会收到 MOVE 事件
     - 事件包含所有手指的信息
     - 每个 View 需要自己提取相关信息


  4. 第二根手指抬起：ACTION_POINTER_UP
  ─────────────────────────────────────────────────────────────────────────────

     系统
       │
       ▼
     Activity.dispatchTouchEvent(POINTER_UP, pointerId=1)
       │
       ▼
     ViewGroup.dispatchTouchEvent(POINTER_UP, pointerId=1)
       │
       ├─► 找到 pointerId=1 对应的 TouchTarget
       │
       ├─► 从链表中移除该 TouchTarget
       │
       └─► 剩余手指继续分发给剩余的 TouchTarget
     
     ★★★ 重要 ★★★
     - ACTION_POINTER_UP 不会结束触摸序列
     - 只有所有手指都抬起（ACTION_UP）才会结束


  5. 最后一根手指抬起：ACTION_UP
  ─────────────────────────────────────────────────────────────────────────────

     系统
       │
       ▼
     Activity.dispatchTouchEvent(UP)
       │
       ▼
     ViewGroup.dispatchTouchEvent(UP)
       │
       ├─► 清空 TouchTarget 链表
       │     cancelAndClearTouchTargets(ev)
       │
       └─► 触摸序列结束
```

#### 2.3.6 多指触控的典型场景

**场景一：双指缩放（ScaleGestureDetector）**

```java
public class ScaleView extends View {
    private ScaleGestureDetector mScaleDetector;
    private float mScaleFactor = 1.0f;
    
    public ScaleView(Context context) {
        super(context);
        mScaleDetector = new ScaleGestureDetector(context, 
                new ScaleGestureDetector.SimpleOnScaleGestureListener() {
            @Override
            public boolean onScale(ScaleGestureDetector detector) {
                // ★★★ 获取缩放因子 ★★★
                mScaleFactor *= detector.getScaleFactor();
                
                // 限制缩放范围
                mScaleFactor = Math.max(0.5f, Math.min(mScaleFactor, 3.0f));
                
                // 重新绘制
                invalidate();
                return true;
            }
        });
    }
    
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        // ★★★ 交给 ScaleGestureDetector 处理 ★★★
        mScaleDetector.onTouchEvent(event);
        return true;
    }
}
```

**ScaleGestureDetector 原理：**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ScaleGestureDetector 原理                                │
└─────────────────────────────────────────────────────────────────────────────┘

  核心变量：
  - mFocusX, mFocusY        焦点位置（两手指中间）
  - mPrevSpanX, mPrevSpanY  上一帧两手指的距离
  - mCurrSpanX, mCurrSpanY  当前帧两手指的距离
  - mScaleFactor            缩放因子


  检测逻辑：
  ─────────────────────────────────────────────────────────────────────────────

  ACTION_POINTER_DOWN（第二根手指按下）:
       │
       ▼
  记录初始位置和距离
       │
       ▼
  等待 MOVE 事件
       │
       ▼
  ACTION_MOVE:
       │
       ├─► 计算当前两指距离
       │     span = sqrt((x2-x1)² + (y2-y1)²)
       │
       ├─► 计算缩放因子
       │     scaleFactor = currentSpan / previousSpan
       │
       ├─► 计算焦点位置
       │     focusX = (x1 + x2) / 2
       │     focusY = (y1 + y2) / 2
       │
       └─► onScale() 回调
           │
           ├─► 返回 true：处理缩放，后续事件继续
           └─► 返回 false：忽略本次缩放


  时序图：
  ─────────────────────────────────────────────────────────────────────────────

  手指1按下 → 手指2按下 → 双指移动 → 手指1抬起 → 手指2抬起
     │           │            │           │           │
     ▼           ▼            ▼           ▼           ▼
  DOWN    POINTER_DOWN    MOVE     POINTER_UP       UP
              │          onScale      (如果缩放完成)
              │            │
              └────────────┘
              保存为上一帧距离
```

**场景二：双指滚动（Scroll）**

```java
@Override
public boolean onTouchEvent(MotionEvent event) {
    switch (event.getActionMasked()) {
        case MotionEvent.ACTION_DOWN:
            mLastX = event.getX();
            mLastY = event.getY();
            break;
            
        case MotionEvent.ACTION_POINTER_DOWN:
            // 第二根手指按下，放弃之前的滚动
            mLastX = event.getX(event.getActionIndex());
            mLastY = event.getY(event.getActionIndex());
            break;
            
        case MotionEvent.ACTION_MOVE:
            if (event.getPointerCount() >= 2) {
                // ★★★ 双指滚动：计算中心点移动 ★★★
                float focusX = (event.getX(0) + event.getX(1)) / 2;
                float focusY = (event.getY(0) + event.getY(1)) / 2;
                
                float deltaX = focusX - mLastX;
                float deltaY = focusY - mLastY;
                
                // 执行滚动
                scrollBy((int) -deltaX, (int) -deltaY);
                
                mLastX = focusX;
                mLastY = focusY;
            } else {
                // 单指滚动
                float x = event.getX();
                float y = event.getY();
                
                int deltaX = (int) (x - mLastX);
                int deltaY = (int) (y - mLastY);
                
                scrollBy(-deltaX, -deltaY);
                
                mLastX = x;
                mLastY = y;
            }
            break;
    }
    return true;
}
```

**场景三：同时双指缩放和滚动**

```java
@Override
public boolean onTouchEvent(MotionEvent event) {
    // 让 ScaleGestureDetector 处理缩放
    mScaleDetector.onTouchEvent(event);
    
    // 让 RotationGestureDetector 处理旋转
    mRotationDetector.onTouchEvent(event);
    
    // 处理滚动（排除缩放的手指）
    switch (event.getActionMasked()) {
        case MotionEvent.ACTION_MOVE:
            if (event.getPointerCount() == 1) {
                // 单指滚动
                handleScroll(event.getX(), event.getY());
            } else if (event.getPointerCount() == 2) {
                // 双指滚动
                float focusX = (event.getX(0) + event.getX(1)) / 2;
                float focusY = (event.getY(0) + event.getY(1)) / 2;
                handleScroll(focusX, focusY);
            }
            break;
    }
    return true;
}
```

#### 2.3.7 多指触控与 ViewGroup 分发

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ViewGroup 多指触控分发源码解析                              │
│  源码位置: frameworks/base/core/java/android/view/ViewGroup.java            │
└─────────────────────────────────────────────────────────────────────────────┘

  关键字段：
  ─────────────────────────────────────────────────────────────────────────────

  // 触摸目标链表（支持多指）
  private TouchTarget mFirstTouchTarget;

  // 位掩码：哪些 pointerId 已经被分发了
  // 例如：0x3 表示 pointer 0 和 1 都已分发
  private int mFirstTouchTargetChildPointerIdBits;


  dispatchTouchEvent 关键代码：
  ─────────────────────────────────────────────────────────────────────────────

  @Override
  public boolean dispatchTouchEvent(MotionEvent ev) {
      ...
      final int actionMasked = ev.getActionMasked();
      final int actionIndex = ev.getActionIndex();
      
      // ★★★ 处理 ACTION_DOWN（第一个手指） ★★★
      if (actionMasked == MotionEvent.ACTION_DOWN) {
          // 重置状态
          cancelAndClearTouchTargets(ev);
          resetTouchState();
      }
      
      // 检查是否拦截
      final boolean intercepted;
      if (actionMasked == MotionEvent.ACTION_DOWN 
              || mFirstTouchTarget != null) {
          // ★★★ DOWN 或有目标时检查拦截 ★★★
          final boolean disallowIntercept = 
                  (mGroupFlags & FLAG_DISALLOW_INTERCEPT) != 0;
          if (!disallowIntercept) {
              intercepted = onInterceptTouchEvent(ev);
          } else {
              intercepted = false;
          }
      } else {
          intercepted = true;
      }
      
      // ★★★ 分发事件 ★★★
      if (!intercepted) {
          // 分发给子 View
          if (actionMasked == MotionEvent.ACTION_DOWN) {
              // ★★★ 只有 DOWN 才找新目标 ★★★
              for (int i = 0; i < childrenCount; i++) {
                  // 找到目标子 View
                  if (dispatchTransformedTouchEvent(ev, false, child, idBits)) {
                      // ★★★ 加入 TouchTarget 链表 ★★★
                      newTouchTarget = addTouchTarget(child, idBitsToAssign);
                      alreadyDispatched = true;
                      break;
                  }
              }
          } else if (actionMasked == MotionEvent.ACTION_POINTER_DOWN) {
              // ★★★ POINTER_DOWN：新增手指 ★★★
              // 获取新手指的 pointerId
              final int pointerId = ev.getPointerId(actionIndex);
              final int idBits = 1 << pointerId;  // 例如：0x4 表示 pointer 2
              
              // 检查是否已经分发给这个 pointer
              if ((idBits & mFirstTouchTargetChildPointerIdBits) == 0) {
                  // 找新手指的目标
                  for (int i = 0; i < childrenCount; i++) {
                      if (dispatchTransformedTouchEvent(ev, false, child, idBits)) {
                          newTouchTarget = addTouchTarget(child, idBits);
                          break;
                      }
                  }
              }
          }
      }
      
      // ★★★ 分发给现有 TouchTarget ★★★
      if (mFirstTouchTarget != null) {
          TouchTarget target = mFirstTouchTarget;
          while (target != null) {
              // 分发给链表中的每个目标
              final boolean handled = dispatchTransformedTouchEvent(
                      ev, canceled, target.child, target.pointerIdBits);
              target = target.next;
          }
      }
      
      return handled;
  }
```

#### 2.3.8 多指触控常见问题

**问题一：双指缩放时画面抖动**

```java
// 错误做法：在 onScale 中直接使用 detector.getFocusX()
@Override
public boolean onScale(ScaleGestureDetector detector) {
    float focusX = detector.getFocusX();  // 焦点的坐标可能跳动
    // 导致画面抖动
    return true;
}

// 正确做法：使用上一帧记录的焦点位置
private float mLastFocusX;
private float mLastFocusY;

@Override
public boolean onTouchEvent(MotionEvent event) {
    mScaleDetector.onTouchEvent(event);
    
    switch (event.getActionMasked()) {
        case MotionEvent.ACTION_MOVE:
            if (event.getPointerCount() >= 2) {
                // ★★★ 计算稳定的焦点位置 ★★★
                mLastFocusX = (event.getX(0) + event.getX(1)) / 2;
                mLastFocusY = (event.getY(0) + event.getY(1)) / 2;
            }
            break;
    }
    return true;
}

@Override
public boolean onScale(ScaleGestureDetector detector) {
    // 使用稳定的焦点位置
    float focusX = mLastFocusX;
    float focusY = mLastFocusY;
    // ...
    return true;
}
```

**问题二：手指抬起后缩放失效**

```java
// 原因：ACTION_POINTER_UP 后没有更新状态
@Override
public boolean onTouchEvent(MotionEvent event) {
    mScaleDetector.onTouchEvent(event);
    
    switch (event.getActionMasked()) {
        case MotionEvent.ACTION_POINTER_UP:
            // ★★★ 必须通知 ScaleGestureDetector ★★★
            // 否则它会认为手指数量没变
            // ScaleGestureDetector 内部会自动处理
            break;
    }
    return true;
}

// 实际上 ScaleGestureDetector.onTouchEvent() 已经处理了 POINTER_UP
// 只需要调用它即可，不需要额外处理
```

**问题三：双指操作时触发单击事件**

```java
// 原因：单击检测只看 ACTION_UP，没考虑多指
@Override
public boolean onTouchEvent(MotionEvent event) {
    switch (event.getActionMasked()) {
        case MotionEvent.ACTION_UP:
            // ★★★ 检查是否是多指操作 ★★★
            if (event.getPointerCount() == 1) {
                // 只有单指才触发单击
                performClick();
            }
            break;
    }
    return true;
}
```

#### 2.3.9 手势检测器汇总

Android 提供了多种手势检测器，都在 `android.view` 包下：

| 检测器 | 用途 | 关键方法 |
|--------|------|----------|
| GestureDetector | 单击、长按、双击 | onSingleTapConfirmed, onDoubleTap, onLongPress |
| ScaleGestureDetector | 双指缩放 | onScale, getScaleFactor |
| RotateGestureDetector | 双指旋转 | onRotate, getRotationDegrees |
| VelocityTracker | 速度追踪 | computeCurrentVelocity, getXVelocity |

**VelocityTracker 在 RecyclerView 滑动中的应用：**

```java
/**
 * 使用 VelocityTracker 实现类似 RecyclerView 的 fling 效果
 */
public class FlingView extends View {
    private VelocityTracker mVelocityTracker;
    private Scroller mScroller;
    
    private int mLastX;
    private int mLastY;
    private int mScrollX;
    private int mScrollY;
    
    // 最大 fling 速度（像素/秒）
    private static final int MAX_FLING_VELOCITY = 5000;
    
    public FlingView(Context context) {
        super(context);
        mVelocityTracker = VelocityTracker.obtain();
        mScroller = new Scroller(context);
    }
    
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        // ★★★ 速度追踪 ★★★
        mVelocityTracker.addMovement(event);
        
        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                // 停止正在进行的 fling
                if (!mScroller.isFinished()) {
                    mScroller.abortAnimation();
                }
                
                mLastX = (int) event.getX();
                mLastY = (int) event.getY();
                break;
                
            case MotionEvent.ACTION_MOVE:
                int x = (int) event.getX();
                int y = (int) event.getY();
                
                int deltaX = x - mLastX;
                int deltaY = y - mLastY;
                
                // 滚动内容
                mScrollX -= deltaX;
                mScrollY -= deltaY;
                
                // 重绘
                invalidate();
                
                mLastX = x;
                mLastY = y;
                break;
                
            case MotionEvent.ACTION_UP:
                // ★★★ 计算 fling 速度 ★★★
                mVelocityTracker.computeCurrentVelocity(1000, MAX_FLING_VELOCITY);
                
                float velocityX = mVelocityTracker.getXVelocity();
                float velocityY = mVelocityTracker.getYVelocity();
                
                // 如果速度足够快，启动 fling
                if (Math.abs(velocityX) > ViewConfiguration.getMinimumFlingVelocity()
                        || Math.abs(velocityY) > ViewConfiguration.getMinimumFlingVelocity()) {
                    startFling((int) -velocityX, (int) -velocityY);
                }
                break;
                
            case MotionEvent.ACTION_CANCEL:
                mVelocityTracker.clear();
                break;
        }
        
        return true;
    }
    
    private void startFling(int velocityX, int velocityY) {
        // ★★★ 使用 Scroller 实现惯性滑动 ★★★
        mScroller.fling(
                mScrollX, mScrollY,          // 起始位置
                velocityX, velocityY,        // 初始速度
                0, 10000,                    // 最小/最大 X 滚动范围
                0, 10000                     // 最小/最大 Y 滚动范围
        );
        
        // 触发重绘，启动动画
        postInvalidateOnAnimation();
    }
    
    @Override
    public void computeScroll() {
        // ★★★ Scroller 滚动计算 ★★★
        if (mScroller.computeScrollOffset()) {
            // 更新滚动位置
            mScrollX = mScroller.getCurrX();
            mScrollY = mScroller.getCurrY();
            
            // 重绘
            postInvalidateOnAnimation();
        }
    }
    
    @Override
    protected void onDetachedFromWindow() {
        super.onDetachedFromWindow();
        mVelocityTracker.recycle();
    }
}
```

**VelocityTracker 核心方法：**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VelocityTracker 使用方法                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 获取 VelocityTracker 实例
  ─────────────────────────────────────────────────────────────────────────────
  // 推荐方式：从池中获取，复用对象
  VelocityTracker tracker = VelocityTracker.obtain();

  2. 添加运动事件
  ─────────────────────────────────────────────────────────────────────────────
  tracker.addMovement(motionEvent);

  3. 计算速度（重要：必须在 ACTION_UP 中调用）
  ─────────────────────────────────────────────────────────────────────────────
  // 参数：时间单位（毫秒），最大速度
  tracker.computeCurrentVelocity(1000);

  4. 获取速度
  ─────────────────────────────────────────────────────────────────────────────
  float velocityX = tracker.getXVelocity();  // 水平速度
  float velocityY = tracker.getYVelocity();    // 垂直速度

  // 也可以获取指定指针的速度
  float vX = tracker.getXVelocity(pointerId);
  float vY = tracker.getYVelocity(pointerId);

  5. 回收
  ─────────────────────────────────────────────────────────────────────────────
  tracker.recycle();


  RecyclerView 滑动速度计算原理：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │  RecyclerView 内部使用类似逻辑：                                       │
  │  ────────────────────────────────────────────────────────────────── │
  │                                                                     │
  │  1. ACTION_DOWN: 记录起始位置，清空速度                                │
  │                                                                     │
  │  2. ACTION_MOVE:                                                    │
  │     - 记录多个采样点                                                  │
  │     - 每次 MOVE 都添加到 VelocityTracker                              │
  │                                                                     │
  │  3. ACTION_UP:                                                      │
  │     - computeCurrentVelocity(1000) 计算速度                          │
  │     - 如果速度 > 最小 fling 阈值                                     │
  │     - 调用 startScroll() / fling() 启动惯性滑动                       │
  │                                                                     │
  │  4. computeScroll():                                                │
  │     - Scroller 计算下一帧位置                                         │
  │     - scrollTo() 应用滚动                                            │
  │     - postInvalidateOnAnimation() 继续下一帧                          │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────────┘


  速度计算详解：
  ─────────────────────────────────────────────────────────────────────────────

  computeCurrentVelocity(units, maxVelocity)

  参数：
  - units: 时间单位（1000 = 1秒，100 = 0.1秒）
  - maxVelocity: 最大速度限制

  返回速度 = (当前位置 - 起始位置) / 时间

  示例：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  假设采样点：                                                          │
  │  time=0ms:   x=0                                                     │
  │  time=100ms: x=100                                                   │
  │  time=200ms: x=200                                                   │
  │                                                                         │
  │  computeCurrentVelocity(1000):                                         │
  │  velocityX = (200 - 0) / 200 * 1000 = 1000 px/s                       │
  │                                                                         │
  │  computeCurrentVelocity(100):                                          │
  │  velocityX = (200 - 0) / 200 * 100 = 100 px/0.1s = 1000 px/s         │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

**组合使用示例：**

```java
public class MultiGestureView extends View {
    private GestureDetector mGestureDetector;
    private ScaleGestureDetector mScaleDetector;
    private RotateGestureDetector mRotateDetector;
    private VelocityTracker mVelocityTracker;
    
    public MultiGestureView(Context context) {
        super(context);
        
        // 单击、双击、长按
        mGestureDetector = new GestureDetector(context, 
                new GestureDetector.SimpleOnGestureListener());
        
        // 缩放
        mScaleDetector = new ScaleGestureDetector(context,
                new ScaleGestureDetector.SimpleOnScaleGestureListener());
        
        // 旋转
        mRotateDetector = new RotateGestureDetector(context,
                new RotateGestureDetector.SimpleOnRotateGestureListener() {
            @Override
            public boolean onRotate(RotateGestureDetector detector) {
                // 处理旋转
                return true;
            }
        });
        
        // 速度追踪
        mVelocityTracker = VelocityTracker.obtain();
    }
    
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        // ★★★ 按顺序调用所有检测器 ★★★
        mGestureDetector.onTouchEvent(event);
        mScaleDetector.onTouchEvent(event);
        mRotateDetector.onTouchEvent(event);
        
        // 速度追踪
        mVelocityTracker.addMovement(event);
        
        return true;
    }
    
    @Override
    protected void onDetachedFromWindow() {
        super.onDetachedFromWindow();
        mVelocityTracker.recycle();
    }
}
```

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

### 9.1 分发入口

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ViewGroup.dispatchTouchEvent() 流程图                    │
│  源码位置: frameworks/base/core/java/android/view/ViewGroup.java            │
└─────────────────────────────────────────────────────────────────────────────┘

  MotionEvent 事件到达 ViewGroup
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Step 1: 辅助处理                                                        │
  │  ─────────────────────────────────────────────────────────────────────── │
  │  - 安全检查（窗口已停止则丢弃）                                           │
  │  - 鼠标/触控笔按钮状态处理                                                │
  │  - 取消之前的悬停状态                                                     │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Step 2: 检查是否拦截                                                    │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  final boolean intercepted;                                             │
  │  if (actionMasked == ACTION_DOWN || mFirstTouchTarget != null) {        │
  │      // ★ DOWN 事件 或 已有触摸目标时才检查拦截                           │
  │      intercepted = onInterceptTouchEvent(ev);                           │
  │  } else {                                                               │
  │      // ★ 非 DOWN 且无触摸目标，直接拦截                                  │
  │      intercepted = true;                                                │
  │  }                                                                       │
  │                                                                         │
  │  // requestDisallowInterceptTouchEvent 可以阻止拦截                      │
  │  if (!disallowIntercept && intercepted) { ... }                         │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ├──── intercepted=true ────► 自己处理 onTouchEvent()
        │
        ▼ (intercepted=false)
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Step 3: 遍历子 View，找到触摸目标                                        │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  if (actionMasked == ACTION_DOWN) {                                     │
  │      // ★ 只有 DOWN 事件才需要找子 View                                  │
  │      // 后续事件直接发给 mFirstTouchTarget                               │
  │      for (int i = childrenCount - 1; i >= 0; i--) {                     │
  │          View child = children[i];                                      │
  │                                                                         │
  │          // 1. 检查 child 是否能接收事件                                  │
  │          if (!canViewReceivePointerEvents(child)) continue;             │
  │                                                                         │
  │          // 2. 检查触摸点是否在 child 范围内                              │
  │          if (!isTransformedTouchPointInView(x, y, child, null))         │
  │              continue;                                                  │
  │                                                                         │
  │          // 3. 分发给 child                                              │
  │          if (dispatchTransformedTouchEvent(ev, false, child, id)) {     │
  │              // ★★★ child 消费了事件，加入 TouchTarget 链表 ★★★         │
  │              newTouchTarget = addTouchTarget(child, idBitsToAssign);    │
  │              alreadyDispatched = true;                                  │
  │              break;  // 找到目标，退出循环                                │
  │          }                                                               │
  │      }                                                                   │
  │  }                                                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Step 4: 后续事件处理                                                    │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  if (mFirstTouchTarget == null) {                                       │
  │      // ★ 没有子 View 消费，自己处理                                      │
  │      handled = dispatchTransformedTouchEvent(ev, canceled, null, 0);    │
  │  } else {                                                               │
  │      // ★ 有触摸目标，分发给链表中的所有目标                               │
  │      TouchTarget target = mFirstTouchTarget;                            │
  │      while (target != null) {                                           │
  │          dispatchTransformedTouchEvent(ev, canceled, target.child, id); │
  │          target = target.next;                                          │
  │      }                                                                   │
  │  }                                                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
     返回 handled
```

**源码片段**（简化版）：

```java
// frameworks/base/core/java/android/view/ViewGroup.java
@Override
public boolean dispatchTouchEvent(MotionEvent ev) {
    int action = ev.getAction();
    int actionMasked = action & MotionEvent.ACTION_MASK;
    
    // ========== Step 1: 处理 ACTION_DOWN ==========
    if (actionMasked == MotionEvent.ACTION_DOWN) {
        // 取消之前的触摸目标
        cancelAndClearTouchTargets(ev);
        resetTouchState();
    }
    
    // ========== Step 2: 检查拦截 ==========
    final boolean intercepted;
    if (actionMasked == MotionEvent.ACTION_DOWN 
            || mFirstTouchTarget != null) {
        final boolean disallowIntercept = 
                (mGroupFlags & FLAG_DISALLOW_INTERCEPT) != 0;
        if (!disallowIntercept) {
            intercepted = onInterceptTouchEvent(ev);
        } else {
            intercepted = false;
        }
    } else {
        // 没有 DOWN 且没有目标，直接拦截
        intercepted = true;
    }
    
    // ========== Step 3: 分发给子 View ==========
    TouchTarget newTouchTarget = null;
    boolean alreadyDispatched = false;
    
    if (!intercepted) {
        if (actionMasked == MotionEvent.ACTION_DOWN) {
            final int childrenCount = mChildrenCount;
            final View[] children = mChildren;
            
            // 倒序遍历（后添加的 View 在上层）
            for (int i = childrenCount - 1; i >= 0; i--) {
                final int childIndex = getAndVerifyPreorderedIndex(
                        childrenCount, i, customOrder);
                final View child = children[childIndex];
                
                // ★★★ 关键：检查触摸点是否在 child 内 ★★★
                if (!canViewReceivePointerEvents(child)
                        || !isTransformedTouchPointInView(x, y, child, null)) {
                    continue;
                }
                
                // 分发给 child
                if (dispatchTransformedTouchEvent(ev, false, child, idBits)) {
                    // ★★★ child 消费了，加入 TouchTarget ★★★
                    newTouchTarget = addTouchTarget(child, idBitsToAssign);
                    alreadyDispatched = true;
                    break;
                }
            }
        }
    }
    
    // ========== Step 4: 处理结果 ==========
    if (mFirstTouchTarget == null) {
        // 没有子 View 消费，自己处理
        handled = dispatchTransformedTouchEvent(ev, canceled, null, 0);
    } else {
        // 分发给 TouchTarget 链表
        TouchTarget target = mFirstTouchTarget;
        while (target != null) {
            final TouchTarget next = target.next;
            if (alreadyDispatched && target == newTouchTarget) {
                handled = true;
            } else {
                final boolean cancelChild = resetCancelNextUpFlag(target.child)
                        || intercepted;
                if (dispatchTransformedTouchEvent(ev, cancelChild,
                        target.child, target.pointerIdBits)) {
                    handled = true;
                }
            }
            target = next;
        }
    }
    
    return handled;
}
```

### 9.2 如何找到并分发给子 View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ViewGroup 找子 View 的流程                               │
└─────────────────────────────────────────────────────────────────────────────┘

  触摸点坐标 (x, y) 是相对于 ViewGroup 的
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  1. 获取所有子 View                                                      │
  │  ─────────────────────────────────────────────────────────────────────── │
  │  final View[] children = mChildren;                                     │
  │  final int childrenCount = mChildrenCount;                              │
  │                                                                         │
  │  // 按照 Z-order 倒序遍历（后添加的 View 可能在上层）                      │
  │  for (int i = childrenCount - 1; i >= 0; i--) { ... }                   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  2. 过滤不可见/不可点击的 View                                            │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  // View 正在播放动画 或 View 可见                                        │
  │  if (!canViewReceivePointerEvents(child)) continue;                     │
  │                                                                         │
  │  // 判断逻辑：                                                           │
  │  // (child.getAnimation() != null) || (child.mViewFlags & VISIBILITY)   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  3. 检查触摸点是否在子 View 范围内                                        │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  if (!isTransformedTouchPointInView(x, y, child, null)) continue;       │
  │                                                                         │
  │  // 这个方法会：                                                         │
  │  // 1. 将 ViewGroup 坐标转换为 child 的本地坐标                           │
  │  // 2. 检查本地坐标是否在 child 的 (0, 0, width, height) 内               │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  4. 分发给子 View                                                        │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  if (dispatchTransformedTouchEvent(ev, false, child, idBits)) {         │
  │      // child 消费了事件                                                 │
  │      addTouchTarget(child, idBits);  // 加入 TouchTarget 链表           │
  │      break;  // 退出循环                                                 │
  │  }                                                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 9.3 isTransformedTouchPointInView - 边界检查

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    isTransformedTouchPointInView 源码分析                   │
│  源码位置: frameworks/base/core/java/android/view/ViewGroup.java            │
└─────────────────────────────────────────────────────────────────────────────┘

  /**
   * 检查触摸点是否在子 View 的范围内
   * 
   * @param x 触摸点 x（ViewGroup 坐标系）
   * @param y 触摸点 y（ViewGroup 坐标系）
   * @param child 子 View
   * @param outPoint 输出转换后的本地坐标（可选）
   * @return true 表示在范围内
   */
  private boolean isTransformedTouchPointInView(
          float x, float y, View child, PointF outPoint) {
      
      // ★★★ 坐标转换 ★★★
      // 将 ViewGroup 的坐标转换为 child 的本地坐标
      float localX = x + mScrollX - child.mLeft;
      float localY = y + mScrollY - child.mTop;
      
      // 考虑 child 的变换矩阵（scale, rotation, translation）
      if (!child.hasIdentityMatrix()) {
          final float[] point = getTempPoint();
          point[0] = localX;
          point[1] = localY;
          child.getInverseMatrix().mapPoints(point);
          localX = point[0];
          localY = point[1];
      }
      
      // ★★★ 边界检查 ★★★
      // 检查本地坐标是否在 child 的边界内
      // child 的本地坐标范围是 (0, 0, width, height)
      final boolean isInView = child.pointInView(localX, localY);
      
      // 输出转换后的坐标
      if (outPoint != null) {
          outPoint.x = localX;
          outPoint.y = localY;
      }
      
      return isInView;
  }
```

**View.pointInView() 源码**：

```java
// frameworks/base/core/java/android/view/View.java
public boolean pointInView(float localX, float localY) {
    // 检查是否在 (0, 0, width, height) 范围内
    return localX >= 0 && localX < (mRight - mLeft)
        && localY >= 0 && localY < (mBottom - mTop);
}
```

**关键点**：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         坐标转换公式                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ViewGroup 坐标 (x, y) → Child 本地坐标 (localX, localY)

  localX = x + mScrollX - child.mLeft
  localY = y + mScrollY - child.mTop

  其中：
  - (x, y): 触摸点相对于 ViewGroup 的坐标
  - mScrollX/mScrollY: ViewGroup 的滚动偏移
  - child.mLeft/mTop: child 在 ViewGroup 中的位置

  示例：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ViewGroup (mScrollX = 0)                                               │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │         (x=150, y=100)  ← 触摸点                                  │  │
  │  │              ●                                                    │  │
  │  │              │                                                    │  │
  │  │              │                                                    │  │
  │  │         ┌────┴──────────┐                                        │  │
  │  │         │               │                                        │  │
  │  │         │   Child       │  mLeft=100, mTop=50                    │  │
  │  │         │   width=100   │  width = mRight - mLeft = 200 - 100    │  │
  │  │         │   height=80   │  height = mBottom - mTop = 130 - 50    │  │
  │  │         └───────────────┘                                        │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  │                                                                         │
  │  localX = 150 + 0 - 100 = 50  ✓ (0 <= 50 < 100)                        │
  │  localY = 100 + 0 - 50  = 50  ✓ (0 <= 50 < 80)                         │
  │                                                                         │
  │  结论：触摸点在 Child 范围内                                             │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 9.4 dispatchTransformedTouchEvent - 分发事件

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    dispatchTransformedTouchEvent 源码分析                   │
│  源码位置: frameworks/base/core/java/android/view/ViewGroup.java            │
└─────────────────────────────────────────────────────────────────────────────┘

  /**
   * 将事件分发给子 View 或自己处理
   * 
   * @param event 原始事件
   * @param cancel 是否发送 CANCEL
   * @param child 目标子 View（null 表示自己处理）
   * @param desiredPointerIdBits 目标触摸点 ID
   * @return true 表示事件被消费
   */
  private boolean dispatchTransformedTouchEvent(
          MotionEvent event, boolean cancel, View child, int desiredPointerIdBits) {
      
      final boolean handled;
      
      // ========== 处理 CANCEL ==========
      if (cancel) {
          MotionEvent cancelEvent = MotionEvent.obtain(event);
          cancelEvent.setAction(MotionEvent.ACTION_CANCEL);
          
          if (child == null) {
              handled = super.dispatchTouchEvent(cancelEvent);
          } else {
              handled = child.dispatchTouchEvent(cancelEvent);
          }
          
          cancelEvent.recycle();
          return handled;
      }
      
      // ========== 处理多点触控分割 ==========
      final int oldPointerIdBits = event.getPointerIdBits();
      final int newPointerIdBits = oldPointerIdBits & desiredPointerIdBits;
      
      // 如果没有匹配的触摸点，直接返回
      if (newPointerIdBits == 0) {
          return false;
      }
      
      // ========== 分发事件 ==========
      MotionEvent transformedEvent;
      
      if (newPointerIdBits == oldPointerIdBits) {
          // 不需要分割触摸点
          if (child == null || child.hasIdentityMatrix()) {
              // 直接使用原事件
              if (child == null) {
                  handled = super.dispatchTouchEvent(event);
              } else {
                  // ★★★ 坐标转换后分发给 child ★★★
                  final float offsetX = mScrollX - child.mLeft;
                  final float offsetY = mScrollY - child.mTop;
                  event.offsetLocation(offsetX, offsetY);
                  handled = child.dispatchTouchEvent(event);
                  event.offsetLocation(-offsetX, -offsetY);  // 恢复
              }
              return handled;
          }
          transformedEvent = MotionEvent.obtain(event);
      } else {
          // 分割触摸点
          transformedEvent = event.split(newPointerIdBits);
      }
      
      // ========== 坐标转换 + 分发 ==========
      if (child == null) {
          // 没有子 View，自己处理
          handled = super.dispatchTouchEvent(transformedEvent);
      } else {
          // 坐标转换
          final float offsetX = mScrollX - child.mLeft;
          final float offsetY = mScrollY - child.mTop;
          transformedEvent.offsetLocation(offsetX, offsetY);
          
          // 考虑 child 的变换矩阵
          if (!child.hasIdentityMatrix()) {
              transformedEvent.transform(child.getInverseMatrix());
          }
          
          // ★★★ 分发给 child ★★★
          handled = child.dispatchTouchEvent(transformedEvent);
      }
      
      transformedEvent.recycle();
      return handled;
  }
```

**关键点**：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    dispatchTransformedTouchEvent 关键点                     │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 坐标转换
     ─────────────────────────────────────────────────────────────────────────
     event.offsetLocation(mScrollX - child.mLeft, mScrollY - child.mTop)
     
     这样 child 收到的 event.getX()/getY() 就是相对于自己的坐标

  2. 变换矩阵
     ─────────────────────────────────────────────────────────────────────────
     如果 child 有 scale/rotation/translation，需要用逆矩阵转换坐标

  3. 多点触控分割
     ─────────────────────────────────────────────────────────────────────────
     event.split(newPointerIdBits) 可以从一个多点触控事件中分离出特定触摸点

  4. CANCEL 处理
     ─────────────────────────────────────────────────────────────────────────
     当 intercepted=true 时，会给当前的 TouchTarget 发送 CANCEL
```

### 9.5 子 View 收不到事件的原因

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    子 View 收不到事件的常见原因                              │
└─────────────────────────────────────────────────────────────────────────────┘

  原因 1：触摸点不在子 View 范围内
  ─────────────────────────────────────────────────────────────────────────────

  isTransformedTouchPointInView() 返回 false

  可能的情况：
  - 触摸点确实在子 View 外面
  - 子 View 超出了父 ViewGroup 的边界（默认会被裁剪）
  - 子 View 有负的 margin/translation


  原因 2：子 View 不可见或正在隐藏动画
  ─────────────────────────────────────────────────────────────────────────────

  canViewReceivePointerEvents() 返回 false

  检查：
  - child.getVisibility() != VISIBLE
  - child.getAnimation() == null || !child.getAnimation().isInitialized()


  原因 3：父 ViewGroup 拦截了事件
  ─────────────────────────────────────────────────────────────────────────────

  onInterceptTouchEvent() 返回 true

  解决方案：
  - 在子 View 中调用 parent.requestDisallowInterceptTouchEvent(true)


  原因 4：子 View 在 ACTION_DOWN 时返回了 false
  ─────────────────────────────────────────────────────────────────────────────

  如果子 View 的 dispatchTouchEvent() 在 ACTION_DOWN 时返回 false：
  - 子 View 不会被加入 TouchTarget 链表
  - 后续的 MOVE/UP 事件不会再分发给该子 View


  原因 5：子 View 被其他 View 覆盖
  ─────────────────────────────────────────────────────────────────────────────

  ViewGroup 倒序遍历子 View，后添加的 View 优先接收事件

  检查：
  - 子 View 的 Z-order（elevation, translationZ）
  - 子 View 在 mChildren 数组中的位置


  原因 6：子 View 超出边界（无 TouchDelegate）
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ViewGroup                                                              │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │     点击这里                                                       │  │
  │  │        ●─────────┐                                                │  │
  │  │                  │                                                │  │
  │  │                  ▼                                                │  │
  │  │         ┌────────────────┐                                        │  │
  │  │         │                │                                        │  │
  │  │         │   Child View   │  ← child 实际边界                      │  │
  │  │         │                │                                        │  │
  │  │         └────────────────┘                                        │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  │                                                                         │
  │  问题：点击在 child 边界外，事件不会分发给 child                          │
  │  解决：使用 TouchDelegate（见 9.6 节）                                   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 9.6 TouchDelegate 为什么设置在父 ViewGroup 上

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TouchDelegate 设置位置的原理                             │
└─────────────────────────────────────────────────────────────────────────────┘

  问题：为什么 TouchDelegate 必须设置在父 ViewGroup 上？

  答案：因为事件分发顺序决定的！

  事件分发顺序：
  ─────────────────────────────────────────────────────────────────────────────

  ViewGroup.dispatchTouchEvent()
      │
      ├─► Step 1: 检查自己的 TouchDelegate  ★★★ 先检查 ★★★
      │       if (mTouchDelegate != null) {
      │           if (mTouchDelegate.onTouchEvent(event)) return true;
      │       }
      │
      ├─► Step 2: 检查是否拦截
      │       intercepted = onInterceptTouchEvent(ev);
      │
      ├─► Step 3: 遍历子 View，找触摸目标
      │       for (child : children) {
      │           // isTransformedTouchPointInView 检查触摸点是否在 child 内
      │           // 如果触摸点在 child 边界外，这里直接 continue
      │           if (!isTransformedTouchPointInView(x, y, child)) continue;
      │           
      │           // 分发给 child
      │           child.dispatchTouchEvent(event);
      │       }
      │
      └─► Step 4: 自己处理
              super.dispatchTouchEvent(event);


  如果 TouchDelegate 设置在子 View 上：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ViewGroup                                                              │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │     点击这里                                                       │  │
  │  │        ●─────────┐                                                │  │
  │  │                  │                                                │  │
  │  │                  ▼                                                │  │
  │  │         ┌────────────────┐                                        │  │
  │  │         │                │                                        │  │
  │  │         │   Child View   │  child.setTouchDelegate(delegate)      │  │
  │  │         │                │                                        │  │
  │  │         └────────────────┘                                        │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  │                                                                         │
  │  流程：                                                                 │
  │  1. ViewGroup.dispatchTouchEvent() 被调用                              │
  │  2. isTransformedTouchPointInView() 检查触摸点                          │
  │  3. 触摸点不在 child 内 → continue（跳过 child）                        │
  │  4. child.dispatchTouchEvent() 不会被调用                               │
  │  5. child 的 TouchDelegate 永远不会执行                                 │
  │                                                                         │
  │  ★★★ 结论：TouchDelegate 无效 ★★★                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  如果 TouchDelegate 设置在父 ViewGroup 上：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ViewGroup  parent.setTouchDelegate(delegate)                          │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │     点击这里  ← 在 TouchDelegate.bounds 内                         │  │
  │  │        ●─────────┐                                                │  │
  │  │        │         │                                                │  │
  │  │        │    ┌────┴───────────┐                                    │  │
  │  │        │    │                │                                    │  │
  │  │        │    │   Child View   │  delegateView = child              │  │
  │  │        │    │                │                                    │  │
  │  │        │    └────────────────┘                                    │  │
  │  │        │         bounds（扩展区域）                                 │  │
  │  │        └─────────────────────────┘                                │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  │                                                                         │
  │  流程：                                                                 │
  │  1. ViewGroup.dispatchTouchEvent() 被调用                              │
  │  2. ★ 先检查 ViewGroup 的 TouchDelegate ★                              │
  │  3. TouchDelegate.onTouchEvent() 检查触摸点在 bounds 内                 │
  │  4. 调用 child.dispatchTouchEvent()                                    │
  │  5. child 响应点击                                                     │
  │                                                                         │
  │  ★★★ 结论：TouchDelegate 生效 ★★★                                      │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### 9.7 TouchTarget 链表

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TouchTarget 链表结构                                │
│  源码位置: frameworks/base/core/java/android/view/ViewGroup.java            │
└─────────────────────────────────────────────────────────────────────────────┘

  private static final class TouchTarget {
      public View child;              // 目标 View
      public TouchTarget next;        // 链表下一个节点
      public int pointerIdBits;       // 关联的触摸点 ID（支持多点触控）
  }

  // ViewGroup 的成员变量
  private TouchTarget mFirstTouchTarget;  // 链表头


  为什么需要链表？
  ─────────────────────────────────────────────────────────────────────────────

  支持多点触控：多个手指可能同时触摸不同的子 View

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ViewGroup                                                              │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                                                                   │  │
  │  │     手指1 ●              手指2 ●                                  │  │
  │  │         │                    │                                    │  │
  │  │         ▼                    ▼                                    │  │
  │  │    ┌─────────┐          ┌─────────┐                               │  │
  │  │    │ Child A │          │ Child B │                               │  │
  │  │    └─────────┘          └─────────┘                               │  │
  │  │                                                                   │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  │                                                                         │
  │  mFirstTouchTarget → [Child A, pointerId=0]                            │
  │                           │                                            │
  │                           ▼                                            │
  │                       [Child B, pointerId=1]                           │
  │                           │                                            │
  │                           ▼                                            │
  │                          null                                          │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  关键方法
  ─────────────────────────────────────────────────────────────────────────────

  1. addTouchTarget() - 添加目标
  ─────────────────────────────────────────────────────────────────────────────

  private TouchTarget addTouchTarget(View child, int pointerIdBits) {
      TouchTarget target = TouchTarget.obtain(child, pointerIdBits);
      target.next = mFirstTouchTarget;  // 头插法
      mFirstTouchTarget = target;
      return target;
  }

  2. TouchTarget.obtain() - 从对象池获取
  ─────────────────────────────────────────────────────────────────────────────

  // TouchTarget 使用对象池避免频繁创建对象
  private static final int MAX_RECYCLED = 32;
  private static TouchTarget sRecycleBin;
  private static int sRecycledCount;

  public static TouchTarget obtain(View child, int pointerIdBits) {
      TouchTarget target;
      if (sRecycleBin == null) {
          target = new TouchTarget();
      } else {
          target = sRecycleBin;
          sRecycleBin = target.next;
          sRecycledCount--;
          target.next = null;
      }
      target.child = child;
      target.pointerIdBits = pointerIdBits;
      return target;
  }

  3. clearTouchTargets() - 清空链表
  ─────────────────────────────────────────────────────────────────────────────

  private void clearTouchTargets() {
      TouchTarget target = mFirstTouchTarget;
      while (target != null) {
          TouchTarget next = target.next;
          target.recycle();  // 回收对象
          target = next;
      }
      mFirstTouchTarget = null;
  }


  后续事件如何分发？
  ─────────────────────────────────────────────────────────────────────────────

  // MOVE/UP 事件直接分发给 mFirstTouchTarget 链表中的所有目标
  if (mFirstTouchTarget != null) {
      TouchTarget target = mFirstTouchTarget;
      while (target != null) {
          TouchTarget next = target.next;
          if (alreadyDispatched && target == newTouchTarget) {
              handled = true;
          } else {
              dispatchTransformedTouchEvent(ev, cancelChild,
                      target.child, target.pointerIdBits);
          }
          target = next;
      }
  }
```

**TouchTarget 完整源码**：

```java
// frameworks/base/core/java/android/view/ViewGroup.java
private static final class TouchTarget {
    public View child;
    public TouchTarget next;
    public int pointerIdBits;
    
    // 对象池
    private static final Object sRecycleLock = new Object();
    private static TouchTarget sRecycleBin;
    private static int sRecycledCount;
    private static final int MAX_RECYCLED = 32;
    
    public static TouchTarget obtain(View child, int pointerIdBits) {
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
    
    public void recycle() {
        synchronized (sRecycleLock) {
            if (sRecycledCount < MAX_RECYCLED) {
                next = sRecycleBin;
                sRecycleBin = this;
                sRecycledCount++;
            }
        }
    }
}
```

### 9.8 子 View 重叠时的触摸分配与 Z 轴

#### 9.8.1 触摸分配规则

当多个子 View 重叠时，触摸事件会分配给**最上层**的 View（Z 轴最高的 View）。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    子 View 重叠时的事件分配                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  ViewGroup
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │    Child1 (先添加，下层)                                                │
  │    ┌─────────────┐                                                      │
  │    │             │                                                      │
  │    │             │                                                      │
  │    └─────────────┘                                                      │
  │                       Child2 (后添加，上层)                              │
  │                       ┌─────────────┐                                   │
  │                       │             │                                   │
  │                       │      ●      │  ← 触摸点                         │
  │                       │   事件给    │                                   │
  │                       │   Child2   │                                   │
  │                       └─────────────┘                                   │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  规则：倒序遍历，先检查后添加的 View
  - Child2 会先被检查，如果触摸点在 Child2 内，事件分配给 Child2
  - Child1 永远收不到事件（被 Child2 遮挡）
```

#### 9.8.2 源码解析

```java
// ViewGroup.dispatchTouchEvent() 中的遍历逻辑
for (int i = childrenCount - 1; i >= 0; i--) {
    final View child = children[i];
    
    // 检查触摸点是否在 child 范围内
    if (!canViewReceivePointerEvents(child) 
            || !isTransformedTouchPointInView(x, y, child, null)) {
        continue;  // 不在范围内，跳过
    }
    
    // 找到目标，分配事件
    if (dispatchTransformedTouchEvent(ev, false, child, idBits)) {
        // 事件被消费，加入 TouchTarget
        newTouchTarget = addTouchTarget(child, idBitsToAssign);
        alreadyDispatched = true;
        break;  // ★★★ 找到目标后立即退出 ★★★
    }
}
```

**关键点**：
- `childrenCount - 1` 开始的倒序遍历
- **后添加的 View 在数组末尾，优先被检查**
- 找到目标后立即 `break`，不会继续检查下层的 View

#### 9.8.3 View 的 Z 轴与层级

Android 中 View 的层级（Z 轴）由以下因素决定：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View Z 轴决定因素                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 添加顺序（mChildren 数组中的位置）
  ─────────────────────────────────────────────────────────────────────────────
  后添加的 View 在上层（数组末尾）

  2. elevation（海拔）
  ─────────────────────────────────────────────────────────────────────────
  view.setElevation(float elevation)
  - elevation 越大，越靠近用户
  - 主要影响阴影绘制

  3. translationZ（Z 轴位移）
  ─────────────────────────────────────────────────────────────────────────
  view.setTranslationZ(float translationZ)
  - 动画过程中临时提升 View 层级
  - 动画结束后通常恢复为 0

  4. bringToFront() 方法
  ─────────────────────────────────────────────────────────────────────────
  view.bringToFront()
  - 将 View 移到 mChildren 数组末尾
  - 变成最上层 View
```

**⚠️ 重要：translationZ 和 elevation 不影响事件分发！**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           translationZ 和 elevation 是否影响事件分发？                      │
└─────────────────────────────────────────────────────────────────────────────┘

  答案：**不影响！**

  ────────────────────────────────────────────────────────────────────────────
  
  Android 事件分发只依据一个因素：
  
  ★ mChildren 数组中的顺序 ★
  
  ────────────────────────────────────────────────────────────────────────────

  示例：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ViewGroup 包含两个重叠的 Button：                                     │
  │  ┌──────────────┐                                                      │
  │  │ Button A    │  elevation=10, translationZ=20                        │
  │  └──────────────┘                                                      │
  │        ┌──────────────┐                                                │
  │        │ Button B    │  elevation=0, translationZ=0                    │
  │        └──────────────┘                                                │
  │                                                                         │
  │  假设 A 先添加，B 后添加：                                              │
  │  mChildren = [A, B]                                                    │
  │                                                                         │
  │  触摸重叠区域 → B 响应（因为 B 在数组末尾，上层）                     │
  │                                                                         │
  │  即使 A 的 elevation 和 translationZ 更大：                             │
  │  - A 的阴影更深                                                        │
  │  - A 看起来在上层                                                       │
  │  - 但事件仍然分配给 B！                                                 │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  为什么这样设计？
  ─────────────────────────────────────────────────────────────────────────

  1. 性能考虑
     - 数组顺序访问 O(1)
     - 不需要计算 Z 值进行排序

  2. 确定性
     - 开发者可以精确控制事件分配
     - bringToFront() 的效果可预测

  3. 分离关注点
     - 视觉层级（elevation）由渲染系统处理
     - 事件层级由数组顺序处理


  那 elevation/translationZ 有什么用？
  ─────────────────────────────────────────────────────────────────────────

  1. **elevation** - 阴影绘制
     - 视觉上看起来在上层
     - 不影响事件传递

  2. **translationZ** - 动画时的层级提升
     - 点击穿透等动画效果
     - 动画结束后应恢复为 0
     - 不影响事件传递（因为不改变 mChildren 数组）

  3. **bringToFront()** - 唯一影响事件分发的方式
     - 改变 mChildren 数组顺序
     - 真正改变触摸目标


  验证代码：
  ─────────────────────────────────────────────────────────────────────────

  // 设置 elevation 和 translationZ
  buttonA.setElevation(50f);
  buttonA.setTranslationZ(30f);

  // 触摸测试：仍然会分配给后添加的 buttonB
  // 因为 mChildren = [buttonA, buttonB]，buttonB 在末尾

  // 只有 bringToFront() 才能改变
  buttonA.bringToFront();
  // 现在 mChildren = [buttonB, buttonA]，buttonA 在末尾
  // 触摸会分配给 buttonA
```

#### 9.8.4 bringToFront() 详解

**方法签名：**

```java
public void bringToFront() {
    if (mParent != null) {
        mParent.bringChildToFront(this);
    }
}
```

**ViewGroup.bringChildToFront() 源码：**

```java
public void bringChildToFront(View child) {
    if (child != null) {
        // 从数组中移除
        removeFromArray(index);
        // 添加到数组末尾（最上层）
        addInArray(child, childrenCount - 1);
        // 刷新视图
        child.mParent = this;
        invalidate();
    }
}
```

**效果演示：**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         bringToFront() 效果                                │
└─────────────────────────────────────────────────────────────────────────────┘

  调用前：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  mChildren 数组: [Child1, Child2, Child3]                             │
  │                                                                         │
  │     Child1 (下层)                                                      │
  │         │                                                              │
  │     Child2 (中层)                                                      │
  │         │                                                              │
  │     Child3 (上层)  ← 触摸优先分配                                      │
  └─────────────────────────────────────────────────────────────────────────┘

  child2.bringToFront() 调用后：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  mChildren 数组: [Child1, Child3, Child2]  ★ Child2 移到末尾           │
  │                                                                         │
  │     Child1 (下层)                                                      │
  │         │                                                              │
  │     Child3 (中层)                                                      │
  │         │                                                              │
  │     Child2 (上层)  ← 现在 Child2 优先接收触摸事件！                     │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 9.8.5 触摸分配与 bringToFront 的关系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              bringToFront() 对触摸事件分配的影响                            │
└─────────────────────────────────────────────────────────────────────────────┘

  示例场景：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  两个重叠的 Button                                                      │
  │  ┌──────────────┐                                                      │
  │  │ Button Red   │                                                      │
  │  └──────────────┘                                                      │
  │        ┌──────────────┐                                                │
  │        │ Button Blue  │ ← 初始：Blue 在上层                            │
  │        └──────────────┘                                                │
  │                                                                         │
  │  触摸 Blue 区域 → Blue 响应                                            │
  │  触摸 Red 区域 → Blue 响应（因为 Blue 在上层遮挡了 Red）                │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘

  点击 Red 区域让 Red 响应：
  ─────────────────────────────────────────────────────────────────────────

  redButton.bringToFront();

  效果：
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  两个重叠的 Button                                                      │
  │  ┌──────────────┐                                                      │
  │  │ Button Red   │ ← 现在 Red 在上层                                    │
  │  └──────────────┘                                                      │
  │        ┌──────────────┐                                                │
  │        │ Button Blue  │                                                │
  │        └──────────────┘                                                │
  │                                                                         │
  │  触摸 Red 区域 → Red 响应 ✓                                            │
  │  触摸 Blue 区域 → 取决于位置：                                          │
  │    - 如果完全被 Red 遮挡 → Red 响应                                     │
  │    - 如果有部分露出 → 露出部分 → Blue 响应                             │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 9.8.6 实际开发中的应用场景

**场景一：拖拽时提升层级**

```java
// 拖拽开始时，将拖拽的 View 移到最上层
view.setOnLongClickListener(v -> {
    // 方式一：bringToFront
    v.bringToFront();
    
    // 方式二：设置 translationZ（动画效果更好）
    v.setTranslationZ(10f);
    
    // 开始拖拽逻辑
    startDrag(v);
    return true;
});

// 拖拽结束后恢复
view.setOnDragListener((v, event) -> {
    switch (event.getAction()) {
        case DragEvent.ACTION_DRAG_ENDED:
            v.setTranslationZ(0f);  // 恢复层级
            break;
    }
    return true;
});
```

**场景二：RecyclerView Item 拖拽排序**

```java
// ItemTouchHelper 拖拽时自动调用 bringToFront
// 源码简略：
public void onSelectedChanged(RecyclerView.ViewHolder viewHolder, int actionState) {
    if (actionState == ItemTouchHelper.ACTION_STATE_DRAG) {
        // 拖拽时提升 Item 层级
        viewHolder.itemView.setTranslationZ(10f);
    }
}

public void clearView(RecyclerView recyclerView, 
        RecyclerView.ViewHolder viewHolder) {
    // 拖拽结束后恢复
    viewHolder.itemView.setTranslationZ(0f);
}
```

**场景三：自定义 ViewGroup 实现叠加选择**

```java
public class OverlapSelectLayout extends ViewGroup {
    
    @Override
    public boolean onInterceptTouchEvent(MotionEvent ev) {
        // 总是让下层 View 先处理 touch 事件
        // 通过调整遍历顺序实现
        return super.onInterceptTouchEvent(ev);
    }
    
    @Override
    public boolean dispatchTouchEvent(MotionEvent ev) {
        // ★★★ 关键：倒序遍历 ★★★
        // 让后添加的 View（上层）优先接收事件
        for (int i = getChildCount() - 1; i >= 0; i--) {
            View child = getChildAt(i);
            if (isTransformedTouchPointInView(ev.getX(), ev.getY(), child, null)) {
                if (child.dispatchTouchEvent(ev)) {
                    return true;
                }
            }
        }
        return super.dispatchTouchEvent(ev);
    }
}
```

#### 9.8.7 注意事项

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    bringToFront() 注意事项                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  1. bringToFront() 会修改 ViewGroup 的 mChildren 数组
  ─────────────────────────────────────────────────────────────────────────────
  - 可能触发 ViewGroup 重新布局
  - 性能开销：O(n)，n 为子 View 数量

  2. 动画过程中使用 translationZ 更平滑
  ─────────────────────────────────────────────────────────────────────────────
  view.setTranslationZ(20f);  // 不改变数组顺序，只改变绘制位置
  // 动画结束后
  view.setTranslationZ(0f);

  3. bringToFront() 不改变 elevation
  ─────────────────────────────────────────────────────────────────────────────
  - 只改变 mChildren 数组顺序
  - elevation 仍然影响阴影绘制

  4. 多指触控时每个手指独立分配
  ─────────────────────────────────────────────────────────────────────────────
  - 不同手指可能分配给不同的子 View
  - 由 TouchTarget 链表管理
```

#### 9.8.8 完整示例：动态切换顶层 View

```java
public class LayerSwitchView extends ViewGroup {
    
    private int mCheckedIndex = -1;
    
    public LayerSwitchView(Context context) {
        super(context);
        setClipChildren(false);  // 允许子 View 超出边界
    }
    
    public void setCheckedIndex(int index) {
        if (mCheckedIndex == index) return;
        
        int oldIndex = mCheckedIndex;
        mCheckedIndex = index;
        
        if (oldIndex >= 0 && oldIndex < getChildCount()) {
            // 旧的选中 View 移到下层
            View oldView = getChildAt(oldIndex);
            oldView.setTranslationZ(0f);
        }
        
        if (index >= 0 && index < getChildCount()) {
            // 新的选中 View 移到上层
            View newView = getChildAt(index);
            
            // 方式一：bringToFront
            newView.bringToFront();
            
            // 方式二：设置 translationZ（更平滑）
            // newView.setTranslationZ(10f);
        }
        
        invalidate();
    }
    
    @Override
    protected void onLayout(boolean changed, int l, int t, int r, int b) {
        for (int i = 0; i < getChildCount(); i++) {
            View child = getChildAt(i);
            child.layout(l, t, r, b);
        }
    }
}
```

---

## 10. View 事件分发

### 10.1 分发入口

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    View.dispatchTouchEvent() 流程图                         │
│  源码位置: frameworks/base/core/java/android/view/View.java                 │
└─────────────────────────────────────────────────────────────────────────────┘

  MotionEvent 到达 View
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Step 1: 辅助处理                                                        │
  │  ─────────────────────────────────────────────────────────────────────── │
  │  - 安全检查（窗口已停止则丢弃）                                           │
  │  - 鼠标/触控笔按钮状态处理                                                │
  │  - 处理嵌套滑动（NestedScroll）                                          │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Step 2: 检查 TouchDelegate                                              │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  if (mTouchDelegate != null) {                                          │
  │      if (mTouchDelegate.onTouchEvent(event)) {                          │
  │          return true;  // TouchDelegate 消费了事件                      │
  │      }                                                                  │
  │  }                                                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Step 3: 检查 OnTouchListener                                            │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  if (mListenerInfo != null                                              │
  │          && mListenerInfo.mOnTouchListener != null                      │
  │          && (mViewFlags & ENABLED_MASK) == ENABLED                      │
  │          && mListenerInfo.mOnTouchListener.onTouch(this, event)) {      │
  │      return true;  // OnTouchListener 消费了事件                        │
  │  }                                                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Step 4: 调用 onTouchEvent()                                             │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  return onTouchEvent(event);                                            │
  │                                                                         │
  │  // onTouchEvent 内部会处理：                                            │
  │  // - 点击检测（performClick）                                           │
  │  // - 长按检测（performLongClick）                                       │
  │  // - 滚动检测                                                           │
  │  // - 上下文菜单                                                         │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

**源码片段**：

```java
// frameworks/base/core/java/android/view/View.java
public boolean dispatchTouchEvent(MotionEvent event) {
    // 辅助处理（省略）
    ...
    
    boolean result = false;
    
    // Step 1: TouchDelegate 处理
    if (mTouchDelegate != null) {
        if (mTouchDelegate.onTouchEvent(event)) {
            result = true;
        }
    }
    
    // Step 2: OnTouchListener 处理
    if (!result && mListenerInfo != null) {
        final OnTouchListener li = mListenerInfo.mOnTouchListener;
        if (li != null && (mViewFlags & ENABLED_MASK) == ENABLED
                && li.onTouch(this, event)) {
            result = true;
        }
    }
    
    // Step 3: onTouchEvent 处理
    if (!result && onTouchEvent(event)) {
        result = true;
    }
    
    return result;
}
```

### 10.2 事件处理优先级

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View 事件处理优先级                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  优先级从高到低：

  1. TouchDelegate.onTouchEvent()
     ─────────────────────────────────────────────────────────────────────────
     用于扩大点击区域，优先级最高
     
  2. OnTouchListener.onTouch()
     ─────────────────────────────────────────────────────────────────────────
     外部设置的监听器，可以完全控制事件处理
     
  3. View.onTouchEvent()
     ─────────────────────────────────────────────────────────────────────────
     View 内部的触摸处理，包括：
     - 点击检测
     - 长按检测
     - 滚动检测
     - 状态更新（pressed、focused）
     
  4. OnClickListener.onClick()
     ─────────────────────────────────────────────────────────────────────────
     在 onTouchEvent 的 ACTION_UP 中调用
     只有当 View 是 clickable 时才会触发
     
  5. OnLongClickListener.onLongClick()
     ─────────────────────────────────────────────────────────────────────────
     在 ACTION_DOWN 后约 500ms 触发
     如果返回 true，则不会再触发 onClick


  完整调用链：
  ─────────────────────────────────────────────────────────────────────────────

  dispatchTouchEvent()
      │
      ├─► TouchDelegate.onTouchEvent()  ──► return true  (消费)
      │
      ├─► OnTouchListener.onTouch()     ──► return true  (消费)
      │
      └─► onTouchEvent()
              │
              ├─► ACTION_DOWN:
              │     ├─► 设置 pressed 状态
              │     └─► postDelayed(mPendingCheckForLongPress, 500ms)
              │
              ├─► ACTION_MOVE:
              │     └─► 检查是否移出边界
              │
              ├─► ACTION_UP:
              │     ├─► 移除长按回调
              │     ├─► performClick()  ──► OnClickListener.onClick()
              │     └─► 清除 pressed 状态
              │
              └─► ACTION_CANCEL:
                    └─► 清除所有状态
```

### 10.3 onTouchEvent 完整源码分析

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    View.onTouchEvent() 完整源码                             │
│  源码位置: frameworks/base/core/java/android/view/View.java                 │
└─────────────────────────────────────────────────────────────────────────────┘

  public boolean onTouchEvent(MotionEvent event) {
      final float x = event.getX();
      final float y = event.getY();
      final int viewFlags = mViewFlags;
      final int action = event.getAction();
      
      // ========== 检查 View 是否可点击 ==========
      final boolean clickable = (viewFlags & CLICKABLE) == CLICKABLE
              || (viewFlags & LONG_CLICKABLE) == LONG_CLICKABLE
              || (viewFlags & CONTEXT_CLICKABLE) == CONTEXT_CLICKABLE;
      
      // 如果 View 被禁用但可点击，仍返回 true（消费事件但不执行动作）
      if ((viewFlags & ENABLED_MASK) == DISABLED) {
          if (action == MotionEvent.ACTION_UP && (mPrivateFlags & PFLAG_PRESSED) != 0) {
              setPressed(false);
          }
          mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
          return clickable;
      }
      
      // ========== 委托给 TouchDelegate 处理 ==========
      if (mTouchDelegate != null) {
          if (mTouchDelegate.onTouchEvent(event)) {
              return true;
          }
      }
      
      // ========== 可点击则处理事件 ==========
      if (clickable || (viewFlags & TOOLTIP) == TOOLTIP) {
          switch (action) {
              case MotionEvent.ACTION_DOWN:
                  // ★★★ 按下处理 ★★★
                  mPrivateFlags3 |= PFLAG3_FINGER_DOWN;
                  
                  // 记录按下位置和时间
                  mHasPerformedLongPress = false;
                  
                  if (!clickable) {
                      // 不可点击，检查长按以显示 tooltip
                      checkForLongClick(0, x, y);
                      break;
                  }
                  
                  // 设置 pressed 状态
                  setPressed(true, x, y);
                  
                  // ★★★ 关键：检查长按 ★★★
                  checkForLongClick(ViewConfiguration.getLongPressTimeout(), x, y);
                  break;
                  
              case MotionEvent.ACTION_MOVE:
                  // ★★★ 移动处理 ★★★
                  if (!clickable) {
                      break;
                  }
                  
                  // 检查是否移出 View 边界
                  if (!pointInView(x, y, mTouchSlop)) {
                      // 移出边界，取消 pressed 状态
                      removeLongPressCallback();
                      setPressed(false);
                  }
                  
                  // 更新 pressed 区域
                  if ((mPrivateFlags & PFLAG_PRESSED) != 0) {
                      // Drawable 状态更新
                      refreshDrawableState();
                  }
                  break;
                  
              case MotionEvent.ACTION_UP:
                  // ★★★ 抬起处理 ★★★
                  mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
                  
                  // 移除长按回调
                  removeLongPressCallback();
                  
                  if ((mPrivateFlags & PFLAG_PRESSED) != 0) {
                      // 在 pressed 状态下抬起
                      
                      // 检查是否可以获取焦点
                      boolean focusTaken = false;
                      if (isFocusable() && isFocusableInTouchMode() && !isFocused()) {
                          focusTaken = requestFocus();
                      }
                      
                      if (!mHasPerformedLongPress && !focusTaken) {
                          // ★★★ 执行点击 ★★★
                          removeTapCallback();
                          
                          // performClick 内部会调用 OnClickListener
                          if (performClick()) {
                              return true;
                          }
                      }
                      
                      // 清除 pressed 状态
                      setPressed(false);
                  }
                  
                  removeTapCallback();
                  break;
                  
              case MotionEvent.ACTION_CANCEL:
                  // ★★★ 取消处理 ★★★
                  removeLongPressCallback();
                  removeTapCallback();
                  mPrivateFlags3 &= ~PFLAG3_FINGER_DOWN;
                  setPressed(false);
                  break;
          }
          
          return true;  // 可点击的 View 始终消费事件
      }
      
      return false;  // 不可点击的 View 不消费事件
  }
```

---

## 10.5 点击、长按、双击检测机制

### 10.4 点击、长按、双击检测机制

#### 10.4.1 点击检测（Click）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         点击检测机制                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  触发条件：
  ─────────────────────────────────────────────────────────────────────────────
  1. ACTION_DOWN 时 View 进入 pressed 状态
  2. ACTION_MOVE 时手指没有移出 View 边界（touchSlop 范围内）
  3. ACTION_UP 时 View 仍处于 pressed 状态
  4. 没有触发长按（mHasPerformedLongPress = false）
  5. 按下时间 < 长按超时（默认 500ms）

  时序图：
  ─────────────────────────────────────────────────────────────────────────────

  ACTION_DOWN                    ACTION_UP
       │                              │
       │◄──────── 约 100ms ──────────►│
       │                              │
       ▼                              ▼
  ┌─────────┐                    ┌─────────┐
  │ pressed │                    │ perform │
  │ = true  │                    │ Click() │
  └─────────┘                    └─────────┘
       │                              │
       │         手指在 View 内        │
       │    ◄─────────────────────►   │
       │                              │
       └──────────────────────────────┘


  performClick() 源码：
  ─────────────────────────────────────────────────────────────────────────────

  public boolean performClick() {
      // 通知无障碍服务
      notifyAutofillManagerOnClick();
      
      final boolean result;
      final ListenerInfo li = mListenerInfo;
      
      if (li != null && li.mOnClickListener != null) {
          // 播放点击音效
          playSoundEffect(SoundEffectConstants.CLICK);
          
          // ★★★ 调用 OnClickListener ★★★
          li.mOnClickListener.onClick(this);
          result = true;
      } else {
          result = false;
      }
      
      // 发送无障碍事件
      sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_CLICKED);
      
      return result;
  }
```

#### 10.4.2 长按检测（Long Click）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         长按检测机制                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  触发条件：
  ─────────────────────────────────────────────────────────────────────────────
  1. ACTION_DOWN 后约 500ms（ViewConfiguration.getLongPressTimeout()）
  2. 手指没有移出 View 边界
  3. ACTION_UP 没有发生

  实现原理：Handler + Runnable 延迟执行
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  ACTION_DOWN                                                            │
  │       │                                                                 │
  │       ▼                                                                 │
  │  setPressed(true)                                                       │
  │       │                                                                 │
  │       ▼                                                                 │
  │  postDelayed(mPendingCheckForLongPress, 500ms)                         │
  │       │                                                                 │
  │       │   ┌────────────────────────────────────────────────────────┐    │
  │       │   │                    500ms 后                           │    │
  │       │   │                                                        │    │
  │       │   │  if (still pressed && !moved out) {                   │    │
  │       │   │      mHasPerformedLongPress = true;                   │    │
  │       │   │      performLongClick();  // ★★★ 触发长按 ★★★       │    │
  │       │   │  }                                                     │    │
  │       │   │                                                        │    │
  │       │   └────────────────────────────────────────────────────────┘    │
  │       │                                                                 │
  │       │   如果手指抬起或移出边界：                                       │
  │       │   removeLongPressCallback();  // 取消长按检测                   │
  │       │                                                                 │
  │       ▼                                                                 │
  │  ACTION_UP / ACTION_CANCEL / MOVE_OUT                                  │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  关键源码：
  ─────────────────────────────────────────────────────────────────────────────

  // CheckForLongPress 是一个 Runnable
  private final class CheckForLongPress implements Runnable {
      private int mOriginalWindowAttachCount;
      private float mX;
      private float mY;
      
      @Override
      public void run() {
          if ((mViewFlags & LONG_CLICKABLE) == LONG_CLICKABLE
                  || (mViewFlags & TOOLTIP) == TOOLTIP) {
              
              // 检查 View 状态
              if (isPressed() 
                      && mOriginalWindowAttachCount == mWindowAttachCount) {
                  
                  // ★★★ 执行长按 ★★★
                  if (performLongClick(mX, mY)) {
                      mHasPerformedLongPress = true;
                  }
              }
          }
      }
  }
  
  // 检查并设置长按回调
  private void checkForLongClick(int delay, float x, float y) {
      if ((mViewFlags & LONG_CLICKABLE) == LONG_CLICKABLE
              || (mViewFlags & TOOLTIP) == TOOLTIP) {
          mHasPerformedLongPress = false;
          
          if (mPendingCheckForLongPress == null) {
              mPendingCheckForLongPress = new CheckForLongPress();
          }
          mPendingCheckForLongPress.setAnchor(x, y);
          mPendingCheckForLongPress.rememberWindowAttachCount();
          
          // ★★★ 延迟 500ms 执行 ★★★
          postDelayed(mPendingCheckForLongPress, delay);
      }
  }
  
  // performLongClick 源码
  public boolean performLongClick() {
      return performLongClickInternal(Float.NaN, Float.NaN);
  }
  
  private boolean performLongClickInternal(float x, float y) {
      sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_LONG_CLICKED);
      
      boolean handled = false;
      final ListenerInfo li = mListenerInfo;
      
      if (li != null && li.mOnLongClickListener != null) {
          // ★★★ 调用 OnLongClickListener ★★★
          handled = li.mOnLongClickListener.onLongClick(View.this);
      }
      
      // 显示 tooltip
      if (!handled) {
          handled = showTooltip(x, y);
      }
      
      return handled;
  }


  长按与点击的关系：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  情况 1：短按（< 500ms）                                                 │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  ACTION_DOWN ──► ~100ms ──► ACTION_UP                                  │
  │                                    │                                    │
  │                                    ▼                                    │
  │                              performClick() ✓                           │
  │                                                                         │
  │                                                                         │
  │  情况 2：长按（>= 500ms），onLongClick 返回 false                        │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  ACTION_DOWN ──► 500ms ──► onLongClick() ──► ACTION_UP                 │
  │                              │                      │                   │
  │                              ▼                      ▼                   │
  │                         返回 false            performClick() ✓          │
  │                                                                         │
  │                                                                         │
  │  情况 3：长按（>= 500ms），onLongClick 返回 true                         │
  │  ─────────────────────────────────────────────────────────────────────  │
  │  ACTION_DOWN ──► 500ms ──► onLongClick() ──► ACTION_UP                 │
  │                              │                      │                   │
  │                              ▼                      ▼                   │
  │                         返回 true            performClick() ✗          │
  │                              │              (mHasPerformedLongPress    │
  │                              ▼               = true，跳过)              │
  │                         点击被吞掉                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

#### 10.4.3 双击检测（Double Tap）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         双击检测机制                                        │
│  ★★★ 双击不是 View 原生支持，需要使用 GestureDetector ★★★                  │
└─────────────────────────────────────────────────────────────────────────────┘

  View 本身不直接支持双击检测，需要使用 GestureDetector：
  ─────────────────────────────────────────────────────────────────────────────

  public class DoubleTapView extends View implements GestureDetector.OnDoubleTapListener {
      
      private GestureDetector mGestureDetector;
      
      public DoubleTapView(Context context, AttributeSet attrs) {
          super(context, attrs);
          
          // 创建 GestureDetector
          mGestureDetector = new GestureDetector(context, new GestureDetector.SimpleOnGestureListener());
          
          // 设置双击监听
          mGestureDetector.setOnDoubleTapListener(this);
          
          // 必须设置可点击
          setClickable(true);
      }
      
      @Override
      public boolean onTouchEvent(MotionEvent event) {
          // ★★★ 先让 GestureDetector 处理 ★★★
          boolean consumed = mGestureDetector.onTouchEvent(event);
          
          // 如果 GestureDetector 没处理，交给父类
          if (!consumed) {
              return super.onTouchEvent(event);
          }
          return true;
      }
      
      @Override
      public boolean onSingleTapConfirmed(MotionEvent e) {
          // 单击确认（确定不是双击）
          Log.d("TAG", "Single tap");
          return true;
      }
      
      @Override
      public boolean onDoubleTap(MotionEvent e) {
          // ★★★ 双击 ★★★
          Log.d("TAG", "Double tap");
          return true;
      }
      
      @Override
      public boolean onDoubleTapEvent(MotionEvent e) {
          // 双击期间的额外事件
          return false;
      }
  }


  GestureDetector 原理：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  GestureDetector 内部实现：                                              │
  │  ─────────────────────────────────────────────────────────────────────  │
  │                                                                         │
  │  核心变量：                                                              │
  │  - mDoubleTapTimeout = 300ms  （两次点击的最大间隔）                     │
  │  - mDoubleTapSlop          （两次点击的最大距离）                        │
  │  - mLastDownTime           （上次 DOWN 的时间）                          │
  │  - mLastDownX/Y            （上次 DOWN 的位置）                          │
  │                                                                         │
  │                                                                         │
  │  检测逻辑：                                                              │
  │  ─────────────────────────────────────────────────────────────────────  │
  │                                                                         │
  │  第一次点击：                                                            │
  │  ACTION_DOWN ──► ACTION_UP                                              │
  │       │              │                                                  │
  │       │              ▼                                                  │
  │       │         记录 mFirstTapTime、mFirstTapX/Y                        │
  │       │         发送延迟消息（300ms）                                    │
  │       │              │                                                  │
  │       │              ▼                                                  │
  │       │         等待第二次点击...                                        │
  │                                                                         │
  │  第二次点击（在 300ms 内）：                                             │
  │  ACTION_DOWN                                                            │
  │       │                                                                 │
  │       ▼                                                                 │
  │  检查：                                                                  │
  │  - 当前时间 - mFirstTapTime < 300ms                                     │
  │  - 当前位置 - mFirstTapX/Y < mDoubleTapSlop                             │
  │       │                                                                 │
  │       ▼                                                                 │
  │  移除延迟消息                                                            │
  │       │                                                                 │
  │       ▼                                                                 │
  │  ACTION_UP ──► onDoubleTap() ✓                                         │
  │                                                                         │
  │                                                                         │
  │  没有第二次点击（超过 300ms）：                                          │
  │  ─────────────────────────────────────────────────────────────────────  │
  │                                                                         │
  │  延迟消息触发 ──► onSingleTapConfirmed() ✓                              │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  GestureDetector 核心源码：
  ─────────────────────────────────────────────────────────────────────────────

  // frameworks/base/core/java/android/view/GestureDetector.java
  
  public class GestureDetector {
      
      // 双击超时（300ms）
      private static final int DOUBLE_TAP_TIMEOUT = ViewConfiguration.getDoubleTapTimeout();
      
      // 双击最大距离
      private int mDoubleTapSlop;
      
      // 状态
      private boolean mStillDown;
      private boolean mInLongPress;
      private boolean mAlwaysInTapRegion;
      
      // 第一次点击信息
      private long mPreviousUpTime;
      private float mPreviousDownX;
      private float mPreviousDownY;
      
      // 双击检测
      private boolean mIsDoubleTapping;
      
      public boolean onTouchEvent(MotionEvent ev) {
          final int action = ev.getAction();
          
          switch (action & MotionEvent.ACTION_MASK) {
              case MotionEvent.ACTION_DOWN:
                  mStillDown = true;
                  mInLongPress = false;
                  mAlwaysInTapRegion = true;
                  
                  // ★★★ 检查是否是双击 ★★★
                  if (mIsLongpressEnabled) {
                      // 设置长按检测
                      mHandler.removeMessages(LONG_PRESS);
                      mHandler.sendEmptyMessageAtTime(LONG_PRESS, 
                              mCurrentDownEvent.getDownTime() + LONGPRESS_TIMEOUT);
                  }
                  
                  // 检查是否在双击窗口内
                  if (mPreviousUpTime != 0 
                          && (eventTime - mPreviousUpTime) <= DOUBLE_TAP_TIMEOUT) {
                      
                      // 检查位置
                      if (mDoubleTapListener != null) {
                          // ★★★ 检查是否是双击的第二次 DOWN ★★★
                          final double deltaX = x - mPreviousDownX;
                          final double deltaY = y - mPreviousDownY;
                          
                          if (deltaX * deltaX + deltaY * deltaY < mDoubleTapSlop * mDoubleTapSlop) {
                              // 在双击范围内
                              mIsDoubleTapping = true;
                              mDoubleTapListener.onDoubleTap(ev);
                          }
                      }
                  }
                  break;
                  
              case MotionEvent.ACTION_UP:
                  mStillDown = false;
                  
                  if (mIsDoubleTapping) {
                      // ★★★ 双击的 UP 事件 ★★★
                      mDoubleTapListener.onDoubleTapEvent(ev);
                      handled = true;
                  } else if (mInLongPress) {
                      mInLongPress = false;
                  } else {
                      // 单击
                      if (mDoubleTapListener != null) {
                          // 延迟发送单击确认，等待可能的第二次点击
                          mHandler.sendEmptyMessageDelayed(SINGLE_TAP, DOUBLE_TAP_TIMEOUT);
                      }
                  }
                  break;
          }
          
          return handled;
      }
  }


  双击时序图：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  第一次点击                          第二次点击                          │
  │  ─────────────────────────────────────────────────────────────────────  │
  │                                                                         │
  │  DOWN ──► UP                          DOWN ──► UP                       │
  │    │        │                           │        │                      │
  │    │        ▼                           │        ▼                      │
  │    │   记录时间/位置                     │   onDoubleTap()               │
  │    │   等待 300ms                        │   onDoubleTapEvent()          │
  │    │        │                           │                               │
  │    │        │◄──── < 300ms ────────────►│                               │
  │    │        │                           │                               │
  │    │   如果超过 300ms：                  │                               │
  │    │   onSingleTapConfirmed()           │                               │
  │    │                                     │                               │
  │    └─────────────────────────────────────┘                               │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  点击 vs 长按 vs 双击 对比：
  ─────────────────────────────────────────────────────────────────────────────

  ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
  │                 │    点击         │    长按         │    双击         │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 检测方式        │ onTouchEvent    │ onTouchEvent    │ GestureDetector │
  │                 │ (原生支持)       │ (原生支持)       │ (需要使用)      │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 时间要求        │ < 500ms         │ >= 500ms        │ 两次点击间隔    │
  │                 │                 │                 │ < 300ms         │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 触发时机        │ ACTION_UP       │ ACTION_DOWN     │ 第二次 UP       │
  │                 │                 │ 后 500ms        │                 │
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 位置要求        │ 手指未移出边界   │ 手指未移出边界   │ 两次位置接近    │
  │                 │                 │                 │ (< doubleTapSlop)│
  ├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
  │ 回调方法        │ onClick()       │ onLongClick()   │ onDoubleTap()   │
  └─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

#### 10.4.4 完整示例：支持单击、长按、双击的 View

```java
/**
 * 支持单击、长按、双击的自定义 View
 */
public class MultiTouchView extends View {
    
    private GestureDetector mGestureDetector;
    private OnMultiTouchListener mListener;
    
    public interface OnMultiTouchListener {
        void onSingleTap();      // 单击
        void onDoubleTap();      // 双击
        void onLongPress();      // 长按
    }
    
    public MultiTouchView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }
    
    private void init(Context context) {
        // 必须设置可点击
        setClickable(true);
        setLongClickable(true);
        
        // 创建 GestureDetector
        mGestureDetector = new GestureDetector(context, 
                new GestureDetector.SimpleOnGestureListener() {
            
            @Override
            public boolean onSingleTapConfirmed(MotionEvent e) {
                // 确认是单击（不是双击）
                if (mListener != null) {
                    mListener.onSingleTap();
                }
                return true;
            }
            
            @Override
            public boolean onDoubleTap(MotionEvent e) {
                // 双击
                if (mListener != null) {
                    mListener.onDoubleTap();
                }
                return true;
            }
            
            @Override
            public void onLongPress(MotionEvent e) {
                // 长按
                if (mListener != null) {
                    mListener.onLongPress();
                }
            }
        });
        
        // 设置双击监听
        mGestureDetector.setOnDoubleTapListener(
                (GestureDetector.OnDoubleTapListener) mGestureDetector.getOnGestureListener());
    }
    
    @Override
    public boolean onTouchEvent(MotionEvent event) {
        // 先让 GestureDetector 处理
        boolean consumed = mGestureDetector.onTouchEvent(event);
        
        // 如果 GestureDetector 没处理，交给父类
        if (!consumed) {
            return super.onTouchEvent(event);
        }
        return true;
    }
    
    public void setOnMultiTouchListener(OnMultiTouchListener listener) {
        mListener = listener;
    }
}


// 使用示例
MultiTouchView touchView = findViewById(R.id.touch_view);
touchView.setOnMultiTouchListener(new MultiTouchView.OnMultiTouchListener() {
    @Override
    public void onSingleTap() {
        Log.d("TAG", "单击");
    }
    
    @Override
    public void onDoubleTap() {
        Log.d("TAG", "双击");
    }
    
    @Override
    public void onLongPress() {
        Log.d("TAG", "长按");
    }
});
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

#### 13.3.1 TouchDelegate 基本概念

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TouchDelegate 基本概念                              │
└─────────────────────────────────────────────────────────────────────────────┘

TouchDelegate 的作用：扩大 View 的可触摸区域

关键理解：
1. bounds 是相对于设置 TouchDelegate 的 View 的坐标系
2. View 正常的可触摸区域是 (0, 0, width, height)
3. 通过设置 bounds 为 (-50, -50, width+50, height+50) 可以扩大触摸区域
4. 不需要父 ViewGroup 参与

示例：
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    View 的坐标系                                                            │
│    ┌─────────────────────────────────────────────────────────────────────┐ │
│    │                                                                     │ │
│    │   (-50,-50)                                                         │ │
│    │       ┌─────────────────────────────────────────┐                  │ │
│    │       │          TouchDelegate.bounds           │                  │ │
│    │       │      (扩展后的触摸区域)                  │                  │ │
│    │       │                                         │                  │ │
│    │       │      (0,0)                              │                  │ │
│    │       │         ┌───────────────────┐          │                  │ │
│    │       │         │                   │          │                  │ │
│    │       │         │   View 实际区域    │          │                  │ │
│    │       │         │   (width, height) │          │                  │ │
│    │       │         │                   │          │                  │ │
│    │       │         └───────────────────┘          │                  │ │
│    │       │                                         │                  │ │
│    │       │                                         │                  │ │
│    │       └─────────────────────────────────────────┘                  │ │
│    │                                                                     │ │
│    └─────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│    点击阴影区域（View 外围）也能触发 View 的点击事件                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 13.3.2 View.setTouchDelegate() 源码

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         View.setTouchDelegate()                             │
│  源码位置: frameworks/base/core/java/android/view/View.java                 │
└─────────────────────────────────────────────────────────────────────────────┘

  /**
   * Sets the TouchDelegate for this View.
   */
  public void setTouchDelegate(TouchDelegate touchDelegate) {
      mTouchDelegate = touchDelegate;
  }
  
  // View 的成员变量
  private TouchDelegate mTouchDelegate;
```

#### 13.3.3 TouchDelegate 类定义

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TouchDelegate 类定义                                │
│  源码位置: frameworks/base/core/java/android/view/TouchDelegate.java        │
└─────────────────────────────────────────────────────────────────────────────┘

  public class TouchDelegate {
      
      /** 目标 View，接收转发的触摸事件 */
      private View mDelegateView;
      
      /** 代理区域（相对于设置 TouchDelegate 的 View 的坐标系）*/
      private Rect mBounds;
      
      /** 扩展后的边界（考虑触摸 slop）*/
      private Rect mSlopBounds;
      
      /** 当前是否正在处理触摸序列 */
      private boolean mDelegateTargeted;
      
      /**
       * Constructor
       * @param bounds 代理区域（相对于 View 的坐标系，可以包含负数）
       * @param delegateView 目标 View（通常就是设置 TouchDelegate 的 View 本身）
       */
      public TouchDelegate(Rect bounds, View delegateView) {
          mBounds = bounds;
          mSlopBounds = new Rect(bounds);
          mSlopBounds.inset(-ViewConfiguration.getTouchSlop(), 
                  -ViewConfiguration.getTouchSlop());
          mDelegateView = delegateView;
      }
      
      /**
       * 处理触摸事件
       * @param event 触摸事件（坐标相对于设置 TouchDelegate 的 View）
       * @return True if the event was consumed
       */
      public boolean onTouchEvent(MotionEvent event) {
          int x = (int) event.getX();
          int y = (int) event.getY();
          boolean sendToDelegate = true;
          boolean handled = false;
          
          switch (event.getAction()) {
              case MotionEvent.ACTION_DOWN:
                  // ★★★ 检查触摸点是否在代理区域内 ★★★
                  mDelegateTargeted = mBounds.contains(x, y);
                  sendToDelegate = mDelegateTargeted;
                  break;
                  
              case MotionEvent.ACTION_MOVE:
                  // MOVE 事件：如果移出 slop 边界，发送 CANCEL
                  if (!mSlopBounds.contains(x, y)) {
                      // 移出了扩展边界
                      sendToDelegate = true;
                      // 发送 CANCEL
                  }
                  break;
                  
              case MotionEvent.ACTION_UP:
              case MotionEvent.ACTION_CANCEL:
                  sendToDelegate = mDelegateTargeted;
                  mDelegateTargeted = false;
                  break;
          }
          
          if (sendToDelegate) {
              // ★★★ 转发给目标 View 的 onTouchEvent ★★★
              handled = mDelegateView.dispatchTouchEvent(event);
          }
          
          return handled;
      }
  }
```

#### 13.3.4 View.dispatchTouchEvent() 中调用 TouchDelegate

```
┌─────────────────────────────────────────────────────────────────────────────┐
│          View.dispatchTouchEvent() 中调用 TouchDelegate                     │
│  源码位置: frameworks/base/core/java/android/view/View.java                 │
└─────────────────────────────────────────────────────────────────────────────┘

  public boolean dispatchTouchEvent(MotionEvent event) {
      // ... 省略前面代码
      
      boolean result = false;
      
      // ★★★ 如果有 TouchDelegate，先让代理处理 ★★★
      if (mTouchDelegate != null) {
          if (mTouchDelegate.onTouchEvent(event)) {
              result = true;  // TouchDelegate 处理了事件
          }
      }
      
      // 如果 TouchDelegate 没处理，继续自己的 onTouchEvent
      if (!result && onTouchEvent(event)) {
          result = true;
      }
      
      return result;
  }
```

#### 13.3.5 完整工作流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TouchDelegate 完整工作流程                          │
└─────────────────────────────────────────────────────────────────────────────┘

  用户触摸屏幕
        │
        ▼
  Activity.dispatchTouchEvent()
        │
        ▼
  PhoneWindow.superDispatchTouchEvent()
        │
        ▼
  DecorView.dispatchTouchEvent()
        │
        │  正常事件分发...
        ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  目标 View.dispatchTouchEvent(event)                                    │
  │  ─────────────────────────────────────────────────────────────────────── │
  │                                                                         │
  │  // event.getX()/getY() 是相对于 View 自身的坐标                        │
  │  // 如果点击在 View 外围，坐标可能是负数                                 │
  │                                                                         │
  │  if (mTouchDelegate != null) {                                          │
  │      if (mTouchDelegate.onTouchEvent(event)) {                          │
  │          return true;  // TouchDelegate 消费了事件                      │
  │      }                                                                  │
  │  }                                                                      │
  │                                                                         │
  │  // TouchDelegate 没处理（点击在 View 实际区域内）                       │
  │  return onTouchEvent(event);                                            │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘


  TouchDelegate.onTouchEvent() 内部：
  ─────────────────────────────────────────────────────────────────────────────

  1. 检查 (x, y) 是否在 mBounds 内
     - mBounds 可能是 (-50, -50, width+50, height+50)
     - 所以点击 View 外围也能匹配

  2. 如果在代理区域内：
     - 调用 mDelegateView.dispatchTouchEvent(event)
     - 注意：这里调用的是 dispatchTouchEvent，不是 onTouchEvent
     - 所以会再次进入 View 的事件分发流程

  3. 如果移出代理区域：
     - 发送 ACTION_CANCEL 给目标 View
```

#### 13.3.6 关键点总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TouchDelegate 关键点                                │
└─────────────────────────────────────────────────────────────────────────────┘

  1. 坐标系问题
     ─────────────────────────────────────────────────────────────────────────
     - TouchDelegate.bounds 使用设置它的 View 的坐标系
     - 所以 bounds 可以包含负数（View 左边和上边的区域）
     - event.getX()/getY() 也是相对于该 View 的

  2. 为什么能扩大点击区域？
     ─────────────────────────────────────────────────────────────────────────
     - View 正常只响应 (0, 0, width, height) 内的触摸
     - 但 TouchDelegate 可以把 bounds 设置成 (-50, -50, width+50, height+50)
     - 这样点击 View 外围也能触发响应

  3. 事件如何到达 View 外围？
     ─────────────────────────────────────────────────────────────────────────
     关键点：父 ViewGroup 在分发事件时：
     
     // ViewGroup.dispatchTouchEvent()
     if (!disallowIntercept && onInterceptTouchEvent(ev)) {
         // ...
     }
     
     // 找到触摸点下的子 View
     final View[] children = mChildren;
     for (int i = childrenCount - 1; i >= 0; i--) {
         final View child = children[i];
         
         // ★★★ isTransformedTouchPointInView() 检查触摸点是否在子 View 内 ★★★
         // 这个检查使用的是子 View 的实际边界 (0, 0, width, height)
         // 所以点击在 View 外围时，事件不会分发给该子 View
         // 而是会分发给父 View 或者其他兄弟 View
     }
     
     问题来了：如果事件不会分发给 View，TouchDelegate 怎么生效？

  4. 真正的生效方式
     ─────────────────────────────────────────────────────────────────────────
     答案：需要在父 ViewGroup 中做特殊处理！
     
     // 在父 ViewGroup 中重写 dispatchTouchEvent
     @Override
     public boolean dispatchTouchEvent(MotionEvent ev) {
         // 先让子 View 的 TouchDelegate 处理
         final Rect bounds = new Rect();
         childView.getHitRect(bounds);
         bounds.inset(-50, -50);  // 扩大 50px
         
         if (bounds.contains((int)ev.getX(), (int)ev.getY())) {
             // 触摸点在扩展区域内，直接分发给子 View
             return childView.dispatchTouchEvent(ev);
         }
         
         return super.dispatchTouchEvent(ev);
     }
     
     或者更简单的方式：使用 TouchDelegate 但设置在父 ViewGroup 上！
```

#### 13.3.7 正确使用方式

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TouchDelegate 正确使用方式                          │
└─────────────────────────────────────────────────────────────────────────────┘

  方式一：设置在子 View 上（bounds 使用负坐标）
  ─────────────────────────────────────────────────────────────────────────────

  Button button = findViewById(R.id.button);
  
  // 扩大按钮的点击区域（向外扩展 50dp）
  // 注意：bounds 使用 button 自身的坐标系，所以包含负数
  int expand = (int) (50 * getResources().getDisplayMetrics().density);
  Rect bounds = new Rect(-expand, -expand, 
          button.getWidth() + expand, button.getHeight() + expand);
  
  TouchDelegate delegate = new TouchDelegate(bounds, button);
  button.setTouchDelegate(delegate);
  
  // ★★★ 问题：这种方式要求事件先到达 button ★★★
  // 如果点击在 button 外围，父 ViewGroup 不会把事件分发给 button
  // 所以 TouchDelegate 不会被调用！


  方式二：设置在父 ViewGroup 上（推荐）
  ─────────────────────────────────────────────────────────────────────────────

  // 在父 ViewGroup 中
  FrameLayout parent = findViewById(R.id.parent);
  Button button = findViewById(R.id.button);
  
  parent.post(() -> {
      // 获取 button 在 parent 中的位置
      Rect bounds = new Rect();
      button.getHitRect(bounds);  // 获取 button 在 parent 中的矩形
      
      // 扩大区域
      bounds.inset(-50, -50);
      
      // ★★★ 关键：TouchDelegate 设置在 parent 上 ★★★
      // bounds 使用 parent 的坐标系
      // delegateView 是 button
      TouchDelegate delegate = new TouchDelegate(bounds, button);
      parent.setTouchDelegate(delegate);
  });
  
  // 这样当触摸点落在 parent 的 bounds 区域内时：
  // 1. parent.dispatchTouchEvent() 被调用
  // 2. parent 的 TouchDelegate.onTouchEvent() 被调用
  // 3. TouchDelegate 检查触摸点在 bounds 内
  // 4. 调用 button.dispatchTouchEvent()
  // 5. button 响应点击


  完整示例代码：
  ─────────────────────────────────────────────────────────────────────────────

  public class MainActivity extends AppCompatActivity {
      
      @Override
      protected void onCreate(Bundle savedInstanceState) {
          super.onCreate(savedInstanceState);
          setContentView(R.layout.activity_main);
          
          FrameLayout parent = findViewById(R.id.parent);
          Button button = findViewById(R.id.small_button);
          
          // 等待 View 布局完成
          parent.post(() -> {
              expandClickArea(parent, button, 50);  // 扩大 50dp
          });
      }
      
      /**
       * 扩大 View 的点击区域
       * @param parent 父 View
       * @param view 需要扩大点击区域的 View
       * @param dp 扩大的距离（dp）
       */
      private void expandClickArea(View parent, View view, int dp) {
          // 转换 dp 为 px
          int px = (int) (dp * parent.getResources().getDisplayMetrics().density);
          
          // 获取 view 在 parent 中的位置
          Rect bounds = new Rect();
          view.getHitRect(bounds);
          
          // 扩大边界
          bounds.inset(-px, -px);
          
          // 创建 TouchDelegate 并设置到 parent
          TouchDelegate delegate = new TouchDelegate(bounds, view);
          parent.setTouchDelegate(delegate);
      }
  }
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
