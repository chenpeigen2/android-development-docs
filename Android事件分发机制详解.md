# Android 事件分发机制详解

> 源码版本：AOSP Android 17（API 37），`android-17.0.0_r1`。


> 作者：OpenClaw | 初稿日期：2026-03-08

---

## 目录

- [1. 概述](#1-概述)
- [2. 事件类型](#2-事件类型)
  - [2.1 触摸事件 (MotionEvent)](#21-触摸事件-motionevent)
  - [2.2 事件批次](#22-事件批次)
  - [2.3 多指触控详解](#23-多指触控详解)
    - [2.3.1 基本概念](#231-基本概念)
    - [2.3.2 多指触控事件类型](#232-多指触控事件类型)
    - [2.3.3 获取手指信息的关键方法](#233-获取手指信息的关键方法)
    - [2.3.4 正确处理多指触控](#234-正确处理多指触控)
    - [2.3.5 多指触控的事件分发](#235-多指触控的事件分发)
    - [2.3.6 多指触控的典型场景](#236-多指触控的典型场景)
    - [2.3.7 多指触控与 ViewGroup 分发](#237-多指触控与-viewgroup-分发)
    - [2.3.8 多指触控常见问题](#238-多指触控常见问题)
    - [2.3.9 手势检测器汇总](#239-手势检测器汇总)
- [3. 分发流程](#3-分发流程)
  - [3.1 整体流程图](#31-整体流程图)
  - [3.2 传递顺序](#32-传递顺序)
- [4. 核心方法详解](#4-核心方法详解)
  - [4.1 方法签名](#41-方法签名)
  - [4.2 方法返回值含义](#42-方法返回值含义)
- [5. dispatchTouchEvent](#5-dispatchtouchevent)
- [6. onInterceptTouchEvent](#6-onintercepttouchevent)
- [7. onTouchEvent](#7-ontouchevent)
  - [7.1 作用](#71-作用)
  - [7.2 View 的默认实现](#72-view-的默认实现)
  - [7.3 关键结论](#73-关键结论)
- [8. 事件传递规则](#8-事件传递规则)
- [9. ViewGroup 事件分发](#9-viewgroup-事件分发)
  - [9.1 分发入口](#91-分发入口)
  - [9.2 命中顺序和坐标变换](#92-命中顺序和坐标变换)
  - [9.3 中途拦截与多指](#93-中途拦截与多指)
  - [9.4 TouchDelegate 与普通子项的优先关系](#94-touchdelegate-与普通子项的优先关系)
  - [9.5 建议的验证序列](#95-建议的验证序列)
- [10. View 事件分发](#10-view-事件分发)
  - [10.1 分发入口](#101-分发入口)
  - [10.2 事件处理优先级](#102-事件处理优先级)
  - [10.3 onTouchEvent 状态处理](#103-ontouchevent-状态处理)
  - [10.4 点击、长按、双击检测机制](#104-点击长按双击检测机制)
    - [10.4.1 点击检测（Click）](#1041-点击检测click)
    - [10.4.2 长按检测（Long Click）](#1042-长按检测long-click)
    - [10.4.3 双击检测（Double Tap）](#1043-双击检测double-tap)
    - [10.4.4 完整示例：支持单击、长按、双击的 View](#1044-完整示例支持单击长按双击的-view)
- [11. Activity 事件分发](#11-activity-事件分发)
- [12. 典型场景分析](#12-典型场景分析)
  - [场景一：子 View 处理事件](#场景一子-view-处理事件)
  - [场景二：ViewGroup 拦截事件](#场景二viewgroup-拦截事件)
  - [场景三：子 View 不处理事件](#场景三子-view-不处理事件)
  - [场景四：多层嵌套不处理](#场景四多层嵌套不处理)
  - [场景五：子 View 重叠时的分配](#场景五子-view-重叠时的分配)
- [13. TouchDelegate 扩大点击区域](#13-touchdelegate-扩大点击区域)
  - [13.1 使用场景](#131-使用场景)
  - [13.2 实现方式](#132-实现方式)
  - [13.3 原理详解](#133-原理详解)
    - [13.3.1 TouchDelegate 基本概念](#1331-touchdelegate-基本概念)
    - [13.3.2 View.setTouchDelegate() 源码](#1332-viewsettouchdelegate-源码)
    - [13.3.3 TouchDelegate 类定义](#1333-touchdelegate-类定义)
    - [13.3.4 View.onTouchEvent() 中调用 TouchDelegate](#1334-viewontouchevent-中调用-touchdelegate)
    - [13.3.5 完整工作流程](#1335-完整工作流程)
    - [13.3.6 关键点总结](#1336-关键点总结)
    - [13.3.7 正确使用方式](#1337-正确使用方式)
- [14. 滑动冲突解决](#14-滑动冲突解决)
  - [14.1 常见滑动冲突场景](#141-常见滑动冲突场景)
  - [14.2 解决策略](#142-解决策略)
    - [策略一：父容器不拦截](#策略一父容器不拦截)
    - [策略二：请求父容器不拦截](#策略二请求父容器不拦截)
- [15. 源码解析](#15-源码解析)
  - [15.1 ViewGroup.findTouchTarget](#151-viewgroupfindtouchtarget)
  - [15.2 dispatchTransformedTouchEvent](#152-dispatchtransformedtouchevent)
- [16. 最佳实践](#16-最佳实践)
  - [16.1 开发建议](#161-开发建议)
  - [16.2 常见问题排查](#162-常见问题排查)
  - [16.3 性能优化](#163-性能优化)
- [总结](#总结)

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

```text
DOWN → [MOVE → MOVE → ...] → UP
```

ACTION_CANCEL 表示当前触摸流被取消，通常取代正常的结束路径；收到后应清理状态，而非等待后续 UP 完成点击。

### 2.3 多指触控详解

#### 2.3.1 基本概念

多指触控（Multi-touch）是指同时有多根手指触摸屏幕的场景。Android 通过 **Pointer ID** 来区分不同的手指。

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

```text
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

`dispatchTouchEvent` 负责决定本次事件交给哪条处理路径，返回是否处理。ViewGroup 管理子目标，View 则在安全过滤、enabled 等条件下依次考虑 OnTouchListener 和 onTouchEvent；不能把拦截简单写成“将原事件改成 CANCEL 后交给自己”。

```text
伪代码（普通 View 主干，省略辅助检查）：
若安全过滤通过：
  若 enabled 且 OnTouchListener 存在并消费 -> handled = true
  否则调用 onTouchEvent
返回 handled
```

具体子目标生命周期见第 9 节。依据：[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)、[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)。

## 6. onInterceptTouchEvent

`onInterceptTouchEvent` 的判断依赖状态，不是只看 action 的固定表：

| 条件 | Android 17 常规分发行为 |
|---|---|
| DOWN 或已有 `mFirstTouchTarget`，且未禁止拦截 | 调用 `onInterceptTouchEvent` |
| 上述条件成立，但 `FLAG_DISALLOW_INTERCEPT` 已设置 | 不调用，视为不拦截 |
| 非 DOWN 且没有子触摸目标 | 不调用，内部 `intercepted = true`，按普通 View 处理 |
| CANCEL 且仍有子触摸目标 | 仍可能进入拦截判断，随后取消并清理目标 |

新 DOWN 会重置旧触摸状态，包含禁止拦截标志。通常触摸输入默认不拦截，但固定 tag 的基类还处理鼠标主键点击滚动条 thumb 的特例，不能把无条件 `return false` 当完整实现。

父容器在 MOVE 中途拦截时，当前事件向已有子目标转换为 CANCEL 并删除目标；**不要断言同一个 MOVE 会再次送给父容器的 `onTouchEvent()`**。之后无子目标的事件才按父容器自身路径处理。父容器需要在拦截判断中记录坐标，并处理 CANCEL 清理。依据：[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)（`dispatchTouchEvent`、`onInterceptTouchEvent`）。

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
- 返回值向调用者报告是否处理；true 通常使该调用者不再尝试后备处理，不代表跨窗口或全局“停止传播”

---

## 8. 事件传递规则

1. 返回值表示这次调用是否处理事件，不是把事件作为新消息“反向冒泡”。查找目标的 DOWN 若子项返回 false，父容器还可能继续尝试其他命中子项；全无目标才走自身 View 分发路径。
2. 子项消费 DOWN 后建立 `TouchTarget`，普通单指后续事件按目标分发，不再每次重新做全量命中测试；父级仍可在满足条件时拦截并取消它。
3. 已有目标在 MOVE 返回 false，不等于自动清除目标或把手势转移给兄弟项；目标清理取决于 CANCEL、拦截、UP、移除等分支。
4. “没消费 DOWN 就永远不再收到事件”只适用于常规单指目标选择的简化讨论。启用 split motion events 时，后续 POINTER_DOWN 可以寻找新目标，不可当作所有多指情形的定律。
5. 多指跟踪使用稳定的 pointer ID，再用 `findPointerIndex(id)` 查当前 index。POINTER_UP 还要迁移活动指针；CANCEL 终止本次流，不是 MOVE/UP 之间的普通插入事件。

依据：[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)、[View.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/View.java)。

## 9. ViewGroup 事件分发

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

### 9.7 子项收不到 DOWN 的分层定位

| 检查位置 | 具体原因 | 应观察的量 |
|---|---|---|
| 窗口路由 | 事件没有进入当前窗口 | ViewRootImpl/Activity 入口日志 |
| 祖先拦截 | 某层 DOWN 就返回 true | 每层 onInterceptTouchEvent 的 action 与结果 |
| 命中条件 | 位置、scroll、矩阵、可见性不满足 | action pointer 的局部坐标与逆矩阵 |
| 重叠扫描 | 更靠前且可消费的兄弟已处理 | Z、自定义顺序、子 dispatch 返回值 |
| 子分发 | OnTouchListener 或安全过滤改变了路径 | listener、enabled、filterTouchesWhenObscured |
| 子处理 | DOWN 返回 false，未建立目标 | clickable/longClickable 与自定义 onTouchEvent |

TouchDelegate 并不出现在普通子项命中扫描之前。它位于 View.onTouchEvent，所以只有父自己进入这一层处理时才有机会转发扩展区域触摸，详见第 13 章。

### 9.8 实战：切换重叠卡片的前后关系

下面是应用代码，不调用隐藏的 TouchTarget 接口。按钮在手势之外改变下一条触摸流的候选顺序；卡片统一使用相同 Z，避免把 elevation 优先级和数组顺序混为一谈。

```kotlin
import android.content.Context
import android.graphics.Color
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView

class StackingDemo(context: Context) : LinearLayout(context) {
    private val stack = FrameLayout(context)
    private val first = card("卡片 A", Color.rgb(210, 225, 255))
    private val second = card("卡片 B", Color.rgb(235, 215, 255))

    init {
        orientation = VERTICAL
        addView(Button(context).apply {
            text = "将 A 放到前面"
            setOnClickListener { promote(first) }
        })
        addView(Button(context).apply {
            text = "将 B 放到前面"
            setOnClickListener { promote(second) }
        })
        addView(stack, LayoutParams(LayoutParams.MATCH_PARENT, dp(220)))
        stack.addView(first, FrameLayout.LayoutParams(dp(180), dp(140)).apply {
            leftMargin = dp(12); topMargin = dp(12)
        })
        stack.addView(second, FrameLayout.LayoutParams(dp(180), dp(140)).apply {
            leftMargin = dp(72); topMargin = dp(52)
        })
    }

    private fun card(label: String, color: Int) = TextView(context).apply {
        text = label
        gravity = Gravity.CENTER
        setBackgroundColor(color)
        elevation = 0f
        translationZ = 0f
        stateListAnimator = null // 避免按压时的 Z 动画改变本例排序条件
        setOnClickListener { text = "$label 被点击" }
    }

    private fun promote(view: View) {
        view.bringToFront()
    }

    private fun dp(value: Int) = (value * resources.displayMetrics.density + 0.5f).toInt()
}
```

两张卡片重叠区会优先尝试当前靠后的同 Z 子项；非重叠区仍按命中条件选择各自卡片。若最上层卡片在 DOWN 不消费，下层候选仍有机会。这与“只要视觉覆盖就一定吞掉触摸”不同。

## 10. View 事件分发

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

### 10.4 点击、长按、双击检测机制

#### 10.4.1 点击检测（Click）

```text
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

```text
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

```text
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

### 11.1 DecorView、Window.Callback 与 Activity

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

### 11.2 为什么不会无限递归

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

## 12. 典型场景分析

### 场景一：子 View 处理事件

```text
DOWN 事件：
Activity.dispatchTouchEvent → ViewGroup.dispatchTouchEvent →
ViewGroup.onInterceptTouchEvent(false) → Child.dispatchTouchEvent →
Child.onTouchEvent(true) → 返回 true

后续事件（MOVE/UP）：
直接分发给 Child，不再经过 ViewGroup.onInterceptTouchEvent
```

### 场景二：ViewGroup 拦截事件

```text
DOWN 事件：
Activity.dispatchTouchEvent → ViewGroup.dispatchTouchEvent →
ViewGroup.onInterceptTouchEvent(true) →
ViewGroup.onTouchEvent(true) → 返回 true

后续事件（MOVE/UP）：
ViewGroup 直接处理，不再分发给子 View
```

### 场景三：子 View 不处理事件

```text
DOWN 事件：
Activity.dispatchTouchEvent → ViewGroup.dispatchTouchEvent →
ViewGroup.onInterceptTouchEvent(false) → Child.dispatchTouchEvent →
Child.onTouchEvent(false) → 返回 false

后续事件（MOVE/UP）：
不再分发给 Child，直接交给 ViewGroup.onTouchEvent
```

### 场景四：多层嵌套不处理

```text
DOWN 事件：
Activity → ViewGroup1 → ViewGroup2 → View
→ onTouchEvent(false) → 返回 false
→ ViewGroup2.onTouchEvent(false) → 返回 false
→ ViewGroup1.onTouchEvent(false) → 返回 false
→ Activity.onTouchEvent(false) → 返回 false
```

### 场景五：子 View 重叠时的分配

当多个子 View 重叠时，触摸事件会分配给**最上层**（最后添加）的 View：

```text
ViewGroup
    ├── Child1 (下层)
    ├── Child2 (中层)
    └── Child3 (上层) ← 优先分配给这个
```

**源码逻辑**（ViewGroup.findTouchTarget）：

```java
private TouchTarget findTouchTarget(View child, float x, float y) {
    final View[] children = mChildren;
    // 无 Z/自定义顺序时可简化为倒序；完整顺序见第 9 节
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

**注意**：在 DOWN 寻找目标的阶段，上层命中子 View 的 dispatchTouchEvent 返回 false 时，父容器仍可尝试下层命中子项；所有候选都未处理才尝试自身路径。已有 TouchTarget 的 MOVE 返回 false 不会自动重新寻找下层目标，二者不可混淆。依据：[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)（dispatchTouchEvent）。

---

## 13. TouchDelegate 扩大点击区域

### 13.1 为什么代理要装在父 View 上

24dp 的图标可以拥有更大的触摸区域而不改变视觉布局。祖先先按普通子项边界命中，范围外的 DOWN 不会直接到达图标；把 TouchDelegate 安装到拥有这片空间的父 View 后，父自身的 onTouchEvent 才有机会把扩展区域中的事件转发给图标。

代理不改变测量、布局或祖先的命中边界，也不是全局先于子项的拦截器。普通兄弟先消费 DOWN、父 OnTouchListener 返回 true、祖先已拦截、父禁用而提前返回，均可能使代理没有执行机会。

### 13.2 字段、构造与注册

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

### 13.3 转发源码：锁定 DOWN，重写坐标

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

### 13.4 在 View.onTouchEvent 中的调用位置

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

### 13.5 实战：布局变化时重建扩展区域

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

### 15.1 getTouchTarget：按子项身份查找而不是命中测试

当前实现的方法名是 `getTouchTarget(View)`，不是 `findTouchTarget()`。它只遍历已经建立的链表并按对象身份查找；屏幕坐标命中发生在分配目标时的 `isTransformedTouchPointInView()`。

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
```

二者不能混用：getTouchTarget 找到 A，表示 A 已拥有至少一个 pointer ID，不表示当前任意指针都在 A 的几何区域内。新增指针再次落在 A 上，只扩展 A 的位集合。

### 15.2 dispatchTransformedTouchEvent：指针筛选、坐标变换和动作恢复

源码精简节选（省略注释；[ViewGroup.java](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/java/android/view/ViewGroup.java)）：

```java
private boolean dispatchTransformedTouchEvent(MotionEvent event, boolean cancel,
        View child, int desiredPointerIdBits) {
    final int oldAction = event.getAction();
    try {
        final boolean handled;
        if (cancel) {
            event.setAction(MotionEvent.ACTION_CANCEL);
        }
        final int oldPointerIdBits = event.getPointerIdBits();
        int newPointerIdBits = oldPointerIdBits & desiredPointerIdBits;
        if (newPointerIdBits == 0) {
            if (event.getAction() != MotionEvent.ACTION_CANCEL) {
                return false;
            } else {
                newPointerIdBits = oldPointerIdBits;
            }
        }
        final MotionEvent transformedEvent;
        if (newPointerIdBits == oldPointerIdBits) {
            if (child == null || child.hasIdentityMatrix()) {
                if (child == null) {
                    handled = super.dispatchTouchEvent(event);
                } else {
                    final float offsetX = mScrollX - child.mLeft;
                    final float offsetY = mScrollY - child.mTop;
                    event.offsetLocation(offsetX, offsetY);

                    handled = child.dispatchTouchEvent(event);

                    event.offsetLocation(-offsetX, -offsetY);
                }
                return handled;
            }
            transformedEvent = MotionEvent.obtain(event);
        } else {
            transformedEvent = event.split(newPointerIdBits);
        }
        if (child == null) {
            handled = super.dispatchTouchEvent(transformedEvent);
        } else {
            final float offsetX = mScrollX - child.mLeft;
            final float offsetY = mScrollY - child.mTop;
            transformedEvent.offsetLocation(offsetX, offsetY);
            if (!child.hasIdentityMatrix()) {
                transformedEvent.transform(child.getInverseMatrix());
            }

            handled = child.dispatchTouchEvent(transformedEvent);
        }
        transformedEvent.recycle();
        return handled;

    } finally {
        event.setAction(oldAction);
    }
}
```

这一层同时解决三类问题：

1. **指针所有权**：`oldPointerIdBits & desiredPointerIdBits` 选出该目标的指针；普通事件交集为空时丢弃，CANCEL 则使用旧集合继续通知。
2. **避免不必要分配**：无需拆分且子矩阵为单位矩阵时，临时 offset 原事件，分发后把 offset 撤销；需要不可逆矩阵变换或 split 时创建副本，分发后 recycle。
3. **避免动作污染**：cancel 参数把 action 改成 CANCEL；无论哪个 return 分支，都在 finally 恢复 oldAction。

注意该 tag 的 CANCEL 仍经过上述筛选/变换结构；不能复制旧实现的“CANCEL 直接原坐标分发并提前返回”作为当前源码。应用拦截/观察事件也应避免永久修改共享的 MotionEvent；确需保留副本时用 obtain 并在使用完毕 recycle。

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
