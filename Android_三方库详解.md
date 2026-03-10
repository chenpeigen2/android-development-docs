# Android 图片加载库完全指南

> 作者：OpenClaw | 日期：2026-03-10

---

## 目录

### 第一部分：Glide - Google 推荐的图片加载库

#### 1. Glide 概述
- 1.1 [什么是 Glide？](#11-什么是-glide)
- 1.2 [核心优势对比](#12-核心优势对比)
- 1.3 [添加依赖](#13-添加依赖)
- 1.4 [权限配置](#14-权限配置)

#### 2. Glide 基本使用
- 2.1 [最简单的加载](#21-最简单的加载)
- 2.2 [加载不同来源](#22-加载不同来源)
- 2.3 [占位图和错误图](#23-占位图和错误图)
- 2.4 [指定图片大小](#24-指定图片大小)
- 2.5 [缩略图](#25-缩略图)
- 2.6 [加载 GIF](#26-加载-gif)
- 2.7 [清除图片和缓存](#27-清除图片和缓存)
- 2.8 [请求监听](#28-请求监听)

#### 3. Glide 缓存机制
- 3.1 [缓存架构](#31-缓存架构)
- 3.2 [缓存查找流程](#32-缓存查找流程)
- 3.3 [缓存 Key 生成规则](#33-缓存-key-生成规则)
- 3.4 [缓存策略](#34-缓存策略)
- 3.5 [跳过缓存](#35-跳过缓存)
- 3.6 [缓存失效](#36-缓存失效)
- 3.7 [自定义缓存大小](#37-自定义缓存大小)

#### 4. Glide 生命周期管理
- 4.1 [生命周期绑定原理](#41-生命周期绑定原理)
- 4.2 [源码解析](#42-源码解析)
- 4.3 [不同 Context 的影响](#43-不同-context-的影响)
- 4.4 [手动管理请求](#44-手动管理请求)

#### 5. Glide 图片变换
- 5.1 [内置变换](#51-内置变换)
- 5.2 [自定义变换](#52-自定义变换)
- 5.3 [多重变换](#53-多重变换)
- 5.4 [第三方变换库](#54-第三方变换库)

#### 6. Glide 高级功能
- 6.1 [预加载](#61-预加载)
- 6.2 [同步加载](#62-同步加载)
- 6.3 [自定义 Target](#63-自定义-target)
- 6.4 [自定义 ModelLoader](#64-自定义-modelloader)
- 6.5 [自定义 Module](#65-自定义-module)

#### 7. Glide 核心原理
- 7.1 [整体架构](#71-整体架构)
- 7.2 [核心组件](#72-核心组件)
- 7.3 [加载流程](#73-加载流程)

#### 8. Glide 源码解析
- 8.1 [初始化流程](#81-初始化流程)
- 8.2 [请求构建流程](#82-请求构建流程)
- 8.3 [Engine 加载流程](#83-engine-加载流程)
- 8.4 [DecodeJob 解码流程](#84-decodejob-解码流程)
- 8.5 [BitmapPool 实现](#85-bitmappool-实现)

#### 9. Glide 性能优化
- 9.1 [内存优化](#91-内存优化)
- 9.2 [加载优化](#92-加载优化)
- 9.3 [网络优化](#93-网络优化)
- 9.4 [列表优化](#94-列表优化)

#### 10. Glide 面试常见问题
- 10.1 [生命周期绑定](#101-生命周期绑定)
- 10.2 [缓存机制](#102-缓存机制)
- 10.3 [OOM 避免](#103-oom-避免)
- 10.4 [与 Picasso 区别](#104-与-picasso-区别)
- 10.5 [高清图加载](#105-高清图加载)
- 10.6 [圆角实现](#106-圆角实现)
- 10.7 [请求取消](#107-请求取消)
- 10.8 [预加载](#108-预加载)
- 10.9 [缓存 Key](#109-缓存-key)
- 10.10 [进度监听](#1010-进度监听)

---

### 第二部分：Fresco - Facebook 的图片加载库

#### 11. Fresco 概述
- 11.1 [什么是 Fresco？](#111-什么是-fresco)
- 11.2 [核心优势](#112-核心优势)
- 11.3 [添加依赖](#113-添加依赖)
- 11.4 [初始化配置](#114-初始化配置)

#### 12. Fresco 基本使用
- 12.1 [SimpleDraweeView](#121-simpledraweeview)
- 12.2 [加载网络图片](#122-加载网络图片)
- 12.3 [加载本地图片](#123-加载本地图片)
- 12.4 [占位图和进度条](#124-占位图和进度条)
- 12.5 [加载 GIF](#125-加载-gif)
- 12.6 [图片缩放](#126-图片缩放)

#### 13. Fresco 核心概念
- 13.1 [DraweeView](#131-draweeview)
- 13.2 [DraweeController](#132-draweecontroller)
- 13.3 [DraweeHierarchy](#133-draweehierarchy)
- 13.4 [ImagePipeline](#134-imagepipeline)

#### 14. Fresco 缓存机制
- 14.1 [三级缓存架构](#141-三级缓存架构)
- 14.2 [内存缓存](#142-内存缓存)
- 14.3 [磁盘缓存](#143-磁盘缓存)
- 14.4 [缓存配置](#144-缓存配置)

#### 15. Fresco 高级功能
- 15.1 [渐进式 JPEG](#151-渐进式-jpeg)
- 15.2 [图片加载监听](#152-图片加载监听)
- 15.3 [自定义 DataSource](#153-自定义-datasource)
- 15.4 [后处理器](#154-后处理器)
- 15.5 [图片请求构建](#155-图片请求构建)

#### 16. Fresco 性能优化
- 16.1 [内存管理](#161-内存管理)
- 16.2 [图片解码优化](#162-图片解码优化)
- 16.3 [网络优化](#163-网络优化)
- 16.4 [列表优化](#164-列表优化)

#### 17. Fresco 面试常见问题
- 17.1 [Fresco vs Glide](#171-fresco-vs-glide)
- 17.2 [内存管理优势](#172-内存管理优势)
- 17.3 [DraweeHierarchy](#173-draweehierarchy)
- 17.4 [渐进式加载](#174-渐进式加载)
- 17.5 [在 RecyclerView 中使用](#175-在-recyclerview-中使用)

---

### 第三部分：图片加载库对比与选型

#### 18. 功能对比
- 18.1 [核心功能对比表](#181-核心功能对比表)
- 18.2 [性能对比](#182-性能对比)
- 18.3 [包大小对比](#183-包大小对比)
- 18.4 [学习曲线对比](#184-学习曲线对比)

#### 19. 选型建议
- 19.1 [Glide 适用场景](#191-glide-适用场景)
- 19.2 [Fresco 适用场景](#192-fresco-适用场景)
- 19.3 [Picasso 适用场景](#193-picasso-适用场景)
- 19.4 [Coil 适用场景](#194-coil-适用场景)

#### 20. 迁移指南
- 20.1 [Picasso → Glide](#201-picasso--glide)
- 20.2 [Glide → Fresco](#202-glide--fresco)
- 20.3 [Fresco → Glide](#203-fresco--glide)

---

## 第一部分：Glide - Google 推荐的图片加载库

---

## 1. Glide 概述

### 1.1 什么是 Glide？

**Glide** 是 Google 推荐的 Android 图片加载库，专注于平滑滚动和高效的图片加载。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Glide 核心特性                                       │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │    Glide     │
                         └──────┬───────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  图片加载     │      │  缓存管理     │      │  生命周期     │
│               │      │               │      │               │
│ - 网络图片    │      │ - 内存缓存    │      │ - 自动绑定    │
│ - 本地资源    │      │ - 磁盘缓存    │      │ - 自动释放    │
│ - GIF/WebP    │      │ - 三级缓存    │      │ - 请求管理    │
│ - 视频        │      │               │      │               │
└───────────────┘      └───────────────┘      └───────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  图片变换     │      │  性能优化     │      │  扩展能力     │
│               │      │               │      │               │
│ - 圆形        │      │ - 位图复用    │      │ - 自定义模块  │
│ - 圆角        │      │ - 降采样      │      │ - 自定义加载  │
│ - 模糊        │      │ - 智能暂停    │      │ - 自定义变换  │
│ - 缩放        │      │ - 预加载      │      │               │
└───────────────┘      └───────────────┘      └───────────────┘
```

### 1.2 核心优势对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         图片加载库对比                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│     特性      │    Glide     │   Picasso    │   Fresco     │    Coil      │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 生命周期管理  │     ★★★★★   │     ★★★☆☆   │     ★★★★★   │     ★★★★★   │
│  缓存机制    │     ★★★★★   │     ★★★☆☆   │     ★★★★★   │     ★★★★★   │
│  GIF 支持    │     ★★★★★   │     ★☆☆☆☆   │     ★★★★★   │     ★★★★★   │
│  性能表现    │     ★★★★★   │     ★★★☆☆   │     ★★★★★   │     ★★★★★   │
│  易用性      │     ★★★★★   │     ★★★★★   │     ★★★☆☆   │     ★★★★★   │
│  包大小      │     ★★★☆☆   │     ★★★★☆   │     ★★☆☆☆   │     ★★★☆☆   │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

### 1.3 添加依赖

```gradle
dependencies {
    implementation 'com.github.bumptech.glide:glide:4.16.0'
    kapt 'com.github.bumptech.glide:compiler:4.16.0' // Kotlin 使用 kapt
    
    // 可选：OkHttp 集成
    implementation "com.github.bumptech.glide:okhttp3-integration:4.16.0"
    
    // 可选： transformations
    implementation 'jp.wasabeef:glide-transformations:4.3.0'
}
```

### 1.4 权限配置

```xml
<!-- 必需权限 -->
<uses-permission android:name="android.permission.INTERNET" />

<!-- 可选权限：磁盘缓存 -->
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
```

---

## 2. Glide 基本使用

### 2.1 最简单的加载

```java
// 基础用法
Glide.with(context)
    .load(url)
    .into(imageView);
```

```kotlin
// Kotlin 扩展函数
imageView.load(url)
```

### 2.2 加载不同来源

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Glide 支持的数据源                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │   String (URL)   │  ──► "https://example.com/image.jpg"                │
│  └──────────────────┘                                                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │   Uri            │  ──► Uri.parse("content://...")                     │
│  └──────────────────┘                                                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │   File           │  ──► new File("/sdcard/image.jpg")                  │
│  └──────────────────┘                                                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │   Resource ID    │  ──► R.drawable.image                                │
│  └──────────────────┘                                                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │   byte[]         │  ──► imageByteArray                                  │
│  └──────────────────┘                                                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │   Bitmap         │  ──► 直接加载 Bitmap 对象                            │
│  └──────────────────┘                                                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │   Drawable       │  ──► 直接加载 Drawable 对象                          │
│  └──────────────────┘                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

```java
// 1. 加载网络图片
Glide.with(context)
    .load("https://example.com/image.jpg")
    .into(imageView);

// 2. 加载资源 ID
Glide.with(context)
    .load(R.drawable.image)
    .into(imageView);

// 3. 加载本地文件
File file = new File("/sdcard/image.jpg");
Glide.with(context)
    .load(file)
    .into(imageView);

// 4. 加载 Uri
Uri uri = Uri.parse("content://media/external/images/media/1");
Glide.with(context)
    .load(uri)
    .into(imageView);

// 5. 加载 byte[]
byte[] imageBytes = getImageBytes();
Glide.with(context)
    .load(imageBytes)
    .into(imageView);

// 6. 加载 Bitmap
Bitmap bitmap = BitmapFactory.decodeResource(getResources(), R.drawable.image);
Glide.with(context)
    .load(bitmap)
    .into(imageView);
```

### 2.3 占位图和错误图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         占位图流程                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  加载开始                加载中                  加载结果
     │                     │                       │
     ▼                     ▼                       ▼
┌─────────┐           ┌─────────┐           ┌──────────────┐
│  开始   │           │  显示   │           │              │
│  加载   │──────────►│ 占位图  │──────────►│  成功：图片  │
│         │           │         │           │  失败：错误图│
└─────────┘           └─────────┘           └──────────────┘
```

```java
Glide.with(context)
    .load(url)
    .placeholder(R.drawable.placeholder)    // 加载中占位图
    .error(R.drawable.error)                // 加载失败图
    .fallback(R.drawable.fallback)          // url 为 null 时的图
    .into(imageView);
```

**占位图说明：**

| 方法 | 说明 | 使用场景 |
|------|------|----------|
| `placeholder()` | 加载中显示的占位图 | 网络较慢时展示 |
| `error()` | 加载失败时显示的图 | 网络错误、404 等 |
| `fallback()` | url 为 null 时显示的图 | 数据缺失情况 |

### 2.4 指定图片大小

```java
// 方式1: 固定尺寸
Glide.with(context)
    .load(url)
    .override(800, 600)  // 800x600 像素
    .into(imageView);

// 方式2: 原始尺寸
Glide.with(context)
    .load(url)
    .override(Target.SIZE_ORIGINAL)  // 不进行降采样
    .into(imageView);

// 方式3: 根据控件大小自动调整
Glide.with(context)
    .load(url)
    .into(imageView);  // 自动使用 ImageView 的尺寸
```

**⚠️ 注意事项：**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         override() 使用注意事项                              │
└─────────────────────────────────────────────────────────────────────────────┘

1. override() 不会改变 ImageView 的大小
   - 只改变图片的解码尺寸
   - ImageView 的 layout params 不受影响

2. override() 会影响缓存 Key
   - 不同尺寸的图片会分别缓存
   - 避免重复解码

3. 推荐做法：
   - 对于小图：使用 override() 避免加载过大图片
   - 对于大图：使用 Target.SIZE_ORIGINAL 保持原始质量
```

### 2.5 缩略图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         缩略图加载流程                                       │
└─────────────────────────────────────────────────────────────────────────────┘

     开始加载
        │
        ├──────────────────────┐
        │                      │
        ▼                      ▼
   加载缩略图               加载原图
   (10% 质量)              (100% 质量)
        │                      │
        ▼                      │
   显示缩略图                 │
        │                      │
        └──────────────────────┤
                               │
                               ▼
                          显示原图
```

```java
// 方式1: 质量缩略图
Glide.with(context)
    .load(url)
    .thumbnail(0.1f)  // 先加载 10% 质量的缩略图
    .into(imageView);

// 方式2: 不同 URL 的缩略图
String thumbnailUrl = "https://example.com/thumb.jpg";
String fullUrl = "https://example.com/full.jpg";

Glide.with(context)
    .load(fullUrl)
    .thumbnail(Glide.with(context).load(thumbnailUrl))
    .into(imageView);

// 方式3: 多级缩略图
Glide.with(context)
    .load(url)
    .thumbnail(0.25f)  // 先加载 25% 质量
    .thumbnail(0.5f)   // 再加载 50% 质量
    .into(imageView);
```

### 2.6 加载 GIF

```java
// 方式1: 自动检测 GIF
Glide.with(context)
    .load(gifUrl)  // 自动判断是否为 GIF
    .into(imageView);

// 方式2: 强制作为 GIF 加载
Glide.with(context)
    .asGif()
    .load(gifUrl)
    .error(R.drawable.error)  // 如果不是 GIF，显示错误图
    .into(imageView);

// 方式3: 加载 GIF 的第一帧
Glide.with(context)
    .asBitmap()
    .load(gifUrl)
    .into(imageView);

// 方式4: GIF 循环次数
Glide.with(context)
    .load(gifUrl)
    .loopCount(3)  // 循环 3 次
    .into(imageView);
```

### 2.7 清除图片和缓存

```java
// 1. 清除 View 上的图片
Glide.with(context).clear(imageView);

// 2. 清除内存缓存（主线程）
Glide.get(context).clearMemory();

// 3. 清除磁盘缓存（子线程）
new Thread(() -> {
    Glide.get(context).clearDiskCache();
}).start();

// 4. 清除特定 View 的缓存
Glide.with(context)
    .clear(imageView);

// 5. 清除所有缓存
new Thread(() -> {
    Glide.get(context).clearDiskCache();
}).start();
Glide.get(context).clearMemory();
```

### 2.8 请求监听

```java
Glide.with(context)
    .load(url)
    .listener(new RequestListener<Drawable>() {
        @Override
        public boolean onLoadFailed(@Nullable GlideException e, Object model,
                                    Target<Drawable> target, boolean isFirstResource) {
            // 加载失败
            Log.e("Glide", "Load failed", e);
            return false;  // 返回 false 让 error 占位图显示
        }

        @Override
        public boolean onResourceReady(Drawable resource, Object model,
                                       Target<Drawable> target, DataSource dataSource,
                                       boolean isFirstResource) {
            // 加载成功
            Log.d("Glide", "Load success from " + dataSource);
            return false;  // 返回 false 让图片正常显示
        }
    })
    .into(imageView);
```

---

## 3. Glide 缓存机制

### 3.1 缓存架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Glide 三级缓存架构                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │  第一级：活动资源 (Active Resources)                                  │ │
│   │                                                                       │ │
│   │  - 引用计数管理                                                       │ │
│   │  - 当前正在使用的资源                                                 │ │
│   │  - 弱引用持有，不参与 LRU                                             │ │
│   │  - 不会被回收                                                         │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │  第二级：内存缓存 (Memory Cache)                                      │ │
│   │                                                                       │ │
│   │  - LRU 策略                                                           │ │
│   │  - 基于最近使用时间                                                   │ │
│   │  - 快速访问，但占用内存                                               │ │
│   │  - 默认大小：可用内存的 1/8                                           │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │  第三级：磁盘缓存 (Disk Cache)                                        │ │
│   │                                                                       │ │
│   │  - LRU 策略                                                           │ │
│   │  - 持久化存储                                                         │ │
│   │  - 包括原始图片和解码后的图片                                         │ │
│   │  - 默认大小：250MB                                                    │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │  数据源 (Data Source)                                                 │ │
│   │                                                                       │ │
│   │  - 网络、本地文件、ContentProvider 等                                 │ │
│   └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 缓存查找流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         缓存查找流程                                         │
└─────────────────────────────────────────────────────────────────────────────┘

         开始加载
             │
             ▼
    ┌────────────────────┐
    │  生成缓存 Key      │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ 查找活动资源       │──────► 命中 ──► 返回
    │ (Active Resources) │
    └────────┬───────────┘
             │ 未命中
             ▼
    ┌────────────────────┐
    │ 查找内存缓存       │──────► 命中 ──► 移到活动资源 ──► 返回
    │ (Memory Cache)     │
    └────────┬───────────┘
             │ 未命中
             ▼
    ┌────────────────────┐
    │ 查找磁盘缓存       │──────► 命中 ──► 解码 ──► 写入缓存 ──► 返回
    │ (Disk Cache)       │
    └────────┬───────────┘
             │ 未命中
             ▼
    ┌────────────────────┐
    │ 从数据源加载       │
    │ (网络/本地)        │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ 解码图片           │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ 写入三级缓存       │
    └────────┬───────────┘
             │
             ▼
          返回图片
```

### 3.3 缓存 Key 生成规则

```java
/**
 * 缓存 Key 由以下因素决定：
 * 
 * EngineKey {
 *     model,          // 图片地址
 *     width,          // 目标宽度
 *     height,         // 目标高度
 *     signature,      // 签名（版本号等）
 *     transformations,// 变换
 *     options,        // 配置选项
 *     resourceClass,  // 资源类型
 *     transcodeClass  // 转码类型
 * }
 */

// 示例：不同的 Key
// 1. 不同 URL
Glide.with(context).load("url1").into(imageView);
Glide.with(context).load("url2").into(imageView);  // 不同 Key

// 2. 不同尺寸
Glide.with(context).load(url).override(100, 100).into(imageView);
Glide.with(context).load(url).override(200, 200).into(imageView);  // 不同 Key

// 3. 不同变换
Glide.with(context).load(url).circleCrop().into(imageView);
Glide.with(context).load(url).centerCrop().into(imageView);  // 不同 Key
```

### 3.4 缓存策略

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         缓存策略类型                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┬────────────────────────────────────────────────────┐
│       策略            │                      说明                          │
├──────────────────────┼────────────────────────────────────────────────────┤
│ AUTOMATIC (默认)     │ 自动选择：网络图片缓存原始+转换，本地只缓存转换    │
│ DATA                │ 只缓存原始图片（未解码）                           │
│ RESOURCE            │ 只缓存解码后的图片                                 │
│ ALL                 │ 缓存原始图片和解码后的图片                         │
│ NONE                │ 禁用磁盘缓存                                       │
└──────────────────────┴────────────────────────────────────────────────────┘
```

```java
// 1. 自动策略（默认）
Glide.with(context)
    .load(url)
    .diskCacheStrategy(DiskCacheStrategy.AUTOMATIC)
    .into(imageView);

// 2. 只缓存原始图片
Glide.with(context)
    .load(url)
    .diskCacheStrategy(DiskCacheStrategy.DATA)
    .into(imageView);

// 3. 只缓存解码后的图片
Glide.with(context)
    .load(url)
    .diskCacheStrategy(DiskCacheStrategy.RESOURCE)
    .into(imageView);

// 4. 缓存所有
Glide.with(context)
    .load(url)
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .into(imageView);

// 5. 禁用磁盘缓存
Glide.with(context)
    .load(url)
    .diskCacheStrategy(DiskCacheStrategy.NONE)
    .into(imageView);
```

### 3.5 跳过缓存

```java
// 1. 跳过内存缓存
Glide.with(context)
    .load(url)
    .skipMemoryCache(true)
    .into(imageView);

// 2. 跳过磁盘缓存
Glide.with(context)
    .load(url)
    .diskCacheStrategy(DiskCacheStrategy.NONE)
    .into(imageView);

// 3. 跳过所有缓存
Glide.with(context)
    .load(url)
    .skipMemoryCache(true)
    .diskCacheStrategy(DiskCacheStrategy.NONE)
    .into(imageView);
```

### 3.6 缓存失效

```java
// 方式1: 使用 signature
Glide.with(context)
    .load(url)
    .signature(new ObjectKey(System.currentTimeMillis())) // 每次都是新签名
    .into(imageView);

// 方式2: 使用版本号
Glide.with(context)
    .load(url)
    .signature(new StringKey("v1.0"))
    .into(imageView);

// 方式3: 使用 MediaStoreSignature
Glide.with(context)
    .load(uri)
    .signature(new MediaStoreSignature(mimeType, dateModified, orientation))
    .into(imageView);

// 方式4: 清除特定 URL 的缓存
new Thread(() -> {
    Glide.get(context).clearDiskCache();
}).start();
```

### 3.7 自定义缓存大小

```java
@GlideModule
public class CustomGlideModule extends AppGlideModule {
    
    @Override
    public void applyOptions(Context context, GlideBuilder builder) {
        // 1. 设置内存缓存大小（默认是可用内存的 1/8）
        int memoryCacheSizeBytes = 1024 * 1024 * 50; // 50MB
        builder.setMemoryCache(new LruResourceCache(memoryCacheSizeBytes));
        
        // 2. 设置磁盘缓存大小（默认 250MB）
        int diskCacheSizeBytes = 1024 * 1024 * 500; // 500MB
        builder.setDiskCache(new InternalCacheDiskCacheFactory(
            context, 
            diskCacheSizeBytes
        ));
        
        // 3. 设置 BitmapPool 大小
        builder.setBitmapPool(new LruBitmapPool(memoryCacheSizeBytes));
        
        // 4. 设置数组池大小
        builder.setArrayPool(new LruArrayPool(memoryCacheSizeBytes));
    }
}
```

---

## 4. Glide 生命周期管理

### 4.1 生命周期绑定原理

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         生命周期绑定原理                                     │
└─────────────────────────────────────────────────────────────────────────────┘

 Activity/Fragment
        │
        ▼
 SupportRequestManagerFragment (无 UI 的 Fragment)
        │
        ▼
 FragmentActivity.getSupportFragmentManager()
        │
        ▼
 Lifecycle (生命周期分发器)
        │
        ▼
 RequestManager (监听生命周期事件)
        │
        ├─► onStart()  ──► resumeRequests()
        ├─► onStop()   ──► pauseRequests()
        └─► onDestroy()──► clearRequests()
```

### 4.2 源码解析

```java
// RequestManagerRetriever.java
public RequestManager get(FragmentActivity activity) {
    if (Util.isOnBackgroundThread()) {
        // 子线程使用 Application Context
        return get(activity.getApplicationContext());
    } else {
        // 主线程绑定生命周期
        assertNotDestroyed(activity);
        FragmentManager fm = activity.getSupportFragmentManager();
        return supportFragmentGet(activity, fm, null);
    }
}

private RequestManager supportFragmentGet(Context context, FragmentManager fm,
                                          Fragment parentHint) {
    // 1. 获取或创建无 UI 的 Fragment
    SupportRequestManagerFragment current = getSupportRequestManagerFragment(fm);
    
    // 2. 获取 RequestManager
    RequestManager requestManager = current.getRequestManager();
    if (requestManager == null) {
        // 3. 创建 RequestManager 并绑定生命周期
        requestManager = new RequestManager(
            context, 
            current.getGlideLifecycle(), 
            current.getRequestManagerTreeNode()
        );
        current.setRequestManager(requestManager);
    }
    return requestManager;
}

// RequestManager.java
public synchronized void onStart() {
    resumeRequests();  // 恢复请求
    targetTracker.onStart();
}

public synchronized void onStop() {
    pauseRequests();  // 暂停请求
    targetTracker.onStop();
}

public synchronized void onDestroy() {
    targetTracker.onDestroy();
    for (Target<?> target : targetTracker.getAll()) {
        clear(target);  // 清除所有请求
    }
    targetTracker.clear();
    requestTracker.clearRequests();
    lifecycle.removeListener(this);
}
```

### 4.3 不同 Context 的影响

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         不同 Context 的影响                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┬────────────────────────────────────────────────────┐
│       Context 类型    │                      行为                          │
├──────────────────────┼────────────────────────────────────────────────────┤
│ Activity             │ 绑定生命周期，自动暂停/恢复/销毁                    │
│ Fragment             │ 绑定 Fragment 生命周期                             │
│ View                 │ 自动获取所在 Activity 的生命周期                   │
│ Application          │ 不绑定生命周期，直到应用退出                        │
│ Service              │ 不绑定生命周期，手动管理                            │
└──────────────────────┴────────────────────────────────────────────────────┘
```

```java
// 1. Activity Context
```java
// 1. Activity Context（推荐）
Glide.with(activity).load(url).into(imageView);

// 2. Fragment Context
Glide.with(fragment).load(url).into(imageView);

// 3. View Context
Glide.with(imageView).load(url).into(imageView);

// 4. Application Context（不推荐，除非在 Service 中）
Glide.with(context.getApplicationContext()).load(url).into(imageView);

// 5. 子线程中使用
new Thread(() -> {
    // 自动使用 Application Context
    Glide.with(context).load(url).into(imageView);
}).start();
```

### 4.4 手动管理请求

```java
public class CustomActivity extends AppCompatActivity {
    
    private RequestManager requestManager;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestManager = Glide.with(this);
    }
    
    @Override
    protected void onStart() {
        super.onStart();
        requestManager.onStart();  // 手动恢复
    }
    
    @Override
    protected void onStop() {
        super.onStop();
        requestManager.onStop();  // 手动暂停
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        requestManager.onDestroy();  // 手动销毁
    }
}
```

---

## 5. Glide 图片变换

### 5.1 内置变换

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Glide 内置变换                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┬────────────────────────────────────────────────────┐
│       变换方法        │                      效果                          │
├──────────────────────┼────────────────────────────────────────────────────┤
│ centerCrop()        │ 居中裁剪，填充 ImageView                           │
│ centerInside()      │ 居中缩放，完整显示图片                             │
│ fitCenter()         │ 保持比例，适配中心                                 │
│ circleCrop()        │ 圆形裁剪                                           │
│ roundedCorners(int) │ 圆角矩形                                           │
│ transform(...)      │ 自定义变换                                         │
└──────────────────────┴────────────────────────────────────────────────────┘
```

```java
// 1. 圆形
Glide.with(context)
    .load(url)
    .circleCrop()
    .into(imageView);

// 2. 居中裁剪
Glide.with(context)
    .load(url)
    .centerCrop()
    .into(imageView);

// 3. 适应中心
Glide.with(context)
    .load(url)
    .centerInside()
    .into(imageView);

// 4. 圆角矩形
Glide.with(context)
    .load(url)
    .transform(new RoundedCorners(20))
    .into(imageView);
```

### 5.2 自定义变换

```java
/**
 * 自定义变换步骤：
 * 1. 继承 BitmapTransformation
 * 2. 重写 transform() 方法
 * 3. 重写 updateDiskCacheKey() 方法
 * 4. 实现 equals() 和 hashCode()
 */
public class BlurTransformation extends BitmapTransformation {
    
    private static final String ID = "com.example.BlurTransformation";
    private int radius;
    
    public BlurTransformation(int radius) {
        this.radius = radius;
    }
    
    @Override
    protected Bitmap transform(@NonNull PoolProvider pool, 
                               @NonNull Bitmap toTransform, 
                               int outWidth, int outHeight) {
        // 实现模糊逻辑
        return blurBitmap(pool, toTransform, radius);
    }
    
    @Override
    public void updateDiskCacheKey(@NonNull MessageDigest messageDigest) {
        messageDigest.update(ByteBuffer.allocate(4).putInt(radius).array());
        messageDigest.update(ID.getBytes(CHARSET));
    }
    
    @Override
    public boolean equals(Object o) {
        return o instanceof BlurTransformation && 
               ((BlurTransformation) o).radius == radius;
    }
    
    @Override
    public int hashCode() {
        return ID.hashCode() + radius * 10;
    }
}
```

### 5.3 多重变换

```java
// 方式1: 单个变换
Glide.with(context)
    .load(url)
    .transform(new BlurTransformation(25))
    .into(imageView);

// 方式2: 多个变换
Glide.with(context)
    .load(url)
    .transforms(
        new CenterCrop(),
        new BlurTransformation(25),
        new RoundedCorners(20)
    )
    .into(imageView);

// 方式3: 使用 MultiTransformation
MultiTransformation<Bitmap> multiTransformation = new MultiTransformation<>(
    new CenterCrop(),
    new BlurTransformation(25),
    new RoundedCorners(20)
);

Glide.with(context)
    .load(url)
    .transform(multiTransformation)
    .into(imageView);
```

### 5.4 第三方变换库

```gradle
implementation 'jp.wasabeef:glide-transformations:4.3.0'
```

```java
// 1. 模糊
Glide.with(context)
    .load(url)
    .apply(RequestOptions.bitmapTransform(
        new BlurTransformation(25, 3)
    ))
    .into(imageView);

// 2. 灰度
Glide.with(context)
    .load(url)
    .apply(RequestOptions.bitmapTransform(
        new GrayscaleTransformation()
    ))
    .into(imageView);

// 3. 马赛克
Glide.with(context)
    .load(url)
    .apply(RequestOptions.bitmapTransform(
        new Pixelation(20)
    ))
    .into(imageView);
```

---

## 6. Glide 高级功能

### 6.1 预加载

```java
// 1. 预加载到缓存
Glide.with(context)
    .load(url)
    .preload(800, 600);  // 预加载 800x600 的图片

// 2. 预加载并指定回调
Glide.with(context)
    .downloadOnly()
    .load(url)
    .into(new CustomTarget<File>() {
        @Override
        public void onResourceReady(@NonNull File resource, @Nullable Transition<? super File> transition) {
            // 预加载完成
            Log.d("Glide", "Preload complete: " + resource.getAbsolutePath());
        }

        @Override
        public void onLoadCleared(@Nullable Drawable placeholder) {
        }
    });

// 3. 批量预加载
List<String> urls = Arrays.asList(url1, url2, url3);
for (String url : urls) {
    Glide.with(context)
        .load(url)
        .preload();
}
```

### 6.2 同步加载

```java
// ⚠️ 注意：必须在子线程中调用
new Thread(() -> {
    FutureTarget<Bitmap> futureTarget = Glide.with(context)
        .asBitmap()
        .load(url)
        .submit();
    
    try {
        // 阻塞等待
        Bitmap bitmap = futureTarget.get();
        
        // 在主线程中使用
        runOnUiThread(() -> {
            imageView.setImageBitmap(bitmap);
        });
    } catch (Exception e) {
        e.printStackTrace();
    } finally {
        futureTarget.cancel(true);
    }
}).start();
```

### 6.3 自定义 Target

```java
// 自定义 ViewTarget
public class CustomViewTarget extends ViewTarget<CustomView, Drawable> {
    
    public CustomViewTarget(CustomView view) {
        super(view);
    }
    
    @Override
    public void onResourceReady(@NonNull Drawable resource, @Nullable Transition<? super Drawable> transition) {
        // 资源准备好
        view.setImage(resource);
    }
    
    @Override
    public void onLoadCleared(@Nullable Drawable placeholder) {
        // 清除
        view.clear();
    }
    
    @Override
    public void onLoadFailed(@Nullable Drawable errorDrawable) {
        // 加载失败
        view.setError(errorDrawable);
    }
}

// 使用
Glide.with(context)
    .load(url)
    .into(new CustomViewTarget(customView));
```

### 6.4 自定义 ModelLoader

```java
/**
 * 自定义 ModelLoader 用于自定义数据源
 * 例如：自定义协议、加密图片等
 */
public class CustomModelLoader implements ModelLoader<CustomData, InputStream> {
    
    @Override
    public LoadData<InputStream> buildLoadData(CustomData data, int width, int height,
                                                Options options) {
        return new LoadData<>(data, new CustomDataFetcher(data));
    }
    
    @Override
    public boolean handles(CustomData data) {
        return true;
    }
    
    public static class Factory implements ModelLoaderFactory<CustomData, InputStream> {
        @Override
        public ModelLoader<CustomData, InputStream> build(MultiModelLoaderFactory factory) {
            return new CustomModelLoader();
        }
        
        @Override
        public void teardown() {}
    }
}

// 注册自定义 ModelLoader
@GlideModule
public class CustomGlideModule extends AppGlideModule {
    @Override
    public void registerComponents(Context context, Glide glide, Registry registry) {
        registry.append(CustomData.class, InputStream.class, 
            new CustomModelLoader.Factory());
    }
}
```

### 6.5 自定义 Module

```java
/**
 * GlideModule 用于全局配置 Glide
 */
@GlideModule
public class CustomGlideModule extends AppGlideModule {
    
    // 配置选项
    @Override
    public void applyOptions(Context context, GlideBuilder builder) {
        // 设置日志级别
        builder.setLogLevel(Log.DEBUG);
        
        // 设置默认请求选项
        builder.setDefaultRequestOptions(
            new RequestOptions()
                .format(DecodeFormat.PREFER_RGB_565)
                .diskCacheStrategy(DiskCacheStrategy.ALL)
        );
        
        // 设置缓存大小
        int memoryCacheSizeBytes = 1024 * 1024 * 50; // 50MB
        builder.setMemoryCache(new LruResourceCache(memoryCacheSizeBytes));
        
        int diskCacheSizeBytes = 1024 * 1024 * 500; // 500MB
        builder.setDiskCache(new InternalCacheDiskCacheFactory(
            context, 
            diskCacheSizeBytes
        ));
    }
    
    // 注册组件
    @Override
    public void registerComponents(Context context, Glide glide, Registry registry) {
        // 注册 OkHttp
        OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(20, TimeUnit.SECONDS)
            .build();
        
        registry.replace(GlideUrl.class, InputStream.class, 
            new OkHttpUrlLoader.Factory(client));
    }
    
    // 是否清空 Manifest merger
    @Override
    public boolean isManifestParsingEnabled() {
        return false;  // 提高性能
    }
}
```

---

## 7. Glide 核心原理

### 7.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Glide 整体架构                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                         ┌──────────────┐                                   │
│                         │    Glide     │                                   │
│                         │   (单例)     │                                   │
│                         └──────┬───────┘                                   │
│                                │                                            │
│        ┌───────────────────────┼───────────────────────┐                   │
│        │                       │                       │                   │
│        ▼                       ▼                       ▼                   │
│ ┌──────────────┐      ┌──────────────┐      ┌──────────────┐             │
│ │RequestManager│      │    Engine    │      │    Decode    │             │
│ │   Retriever  │──────│    (核心)    │──────│     Job      │             │
│ └──────────────┘      └──────────────┘      └──────────────┘             │
│        │                       │                       │                   │
│        ▼                       ▼                       ▼                   │
│ ┌──────────────┐      ┌──────────────┐      ┌──────────────┐             │
│ │  Lifecycle   │      │    Cache     │      │    Bitmap    │             │
│ │   Manager    │      │   (缓存)     │      │     Pool     │             │
│ └──────────────┘      └──────────────┘      └──────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 核心组件

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         核心组件说明                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬────────────────────────────────────────────────────────┐
│     组件          │                      说明                              │
├──────────────────┼────────────────────────────────────────────────────────┤
│ Glide            │ 单例，负责初始化和协调各组件                           │
│ RequestManager   │ 管理图片加载请求，绑定生命周期                         │
│ Engine           │ 核心引擎，负责加载任务的调度                           │
│ DecodeJob        │ 图片解码任务，从缓存或数据源加载数据                   │
│ BitmapPool       │ 位图复用池，减少 Bitmap 内存分配和 GC                  │
│ MemoryCache      │ 内存缓存，LRU 策略                                    │
│ DiskCache        │ 磁盘缓存，持久化存储                                  │
│ Registry         │ 组件注册中心，管理 ModelLoader、Encoder 等            │
└──────────────────┴────────────────────────────────────────────────────────┘
```

### 7.3 加载流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Glide 加载流程                                       │
└─────────────────────────────────────────────────────────────────────────────┘

1. Glide.with(context)
        │
        ▼
2. 获取 RequestManager（绑定生命周期）
        │
        ▼
3. RequestManager.load(url)
        │
        ▼
4. 创建 RequestBuilder
        │
        ▼
5. RequestBuilder.into(imageView)
        │
        ▼
6. 构建 Request，提交给 Engine
        │
        ▼
7. Engine 查找缓存
   ├── 活动资源（Active Resources）→ 返回
   ├── 内存缓存（Memory Cache）→ 移到活动资源 → 返回
   └── 未命中 → 启动 DecodeJob
        │
        ▼
8. DecodeJob 查找磁盘缓存
   ├── 命中 → 解码 → 写入缓存 → 回调
   └── 未命中 → 从网络加载 → 解码 → 写入缓存 → 回调
```

---

## 8. Glide 源码解析

### 8.1 初始化流程

```java
// Glide.java
public static Glide get(Context context) {
    if (glide == null) {
        synchronized (Glide.class) {
            if (glide == null) {
                checkAndInitializeGlide(context);
            }
        }
    }
    return glide;
}

private static void initializeGlide(Context context) {
    // 1. 查找所有 GlideModule
    // 2. 创建 GlideBuilder
    // 3. 调用 applyOptions
    // 4. 创建 Glide 实例
    // 5. 调用 registerComponents
}
```

### 8.2 请求构建流程

```java
// RequestBuilder.java
public ViewTarget<ImageView, TranscodeType> into(ImageView view) {
    // 1. 校验主线程
    Util.assertMainThread();
    
    // 2. 获取尺寸
    int width = view.getWidth();
    int height = view.getHeight();
    
    // 3. 构建 Request
    Request request = buildRequest(target, ...);
    
    // 4. 提交请求
    requestManager.track(target, request);
    
    return target;
}
```

### 8.3 Engine 加载流程

```java
// Engine.java
public <R> LoadStatus load(...) {
    // 1. 生成缓存 Key
    EngineKey key = keyFactory.buildKey(...);
    
    // 2. 查找活动资源
    EngineResource<?> active = loadFromActiveResources(key, isMemoryCacheable);
    if (active != null) {
        cb.onResourceReady(active, DataSource.MEMORY_CACHE);
        return null;
    }
    
    // 3. 查找内存缓存
    EngineResource<?> cached = loadFromCache(key, isMemoryCacheable);
    if (cached != null) {
        cb.onResourceReady(cached, DataSource.MEMORY_CACHE);
        return null;
    }
    
    // 4. 查找正在进行的任务
    EngineJob<?> current = jobs.get(key);
    if (current != null) {
        current.addCallback(cb);
        return new LoadStatus(cb, current);
    }
    
    // 5. 启动新任务
    EngineJob<R> engineJob = engineJobFactory.build(...);
    DecodeJob<R> decodeJob = decodeJobFactory.build(...);
    jobs.put(key, engineJob);
    engineJob.addCallback(cb);
    engineJob.start(decodeJob);
    
    return new LoadStatus(cb, engineJob);
}
```

### 8.4 DecodeJob 解码流程

```java
// DecodeJob.java
class DecodeJob<R> implements Runnable {
    
    @Override
    public void run() {
        try {
            if (isCancelled) {
                notifyFailed();
                return;
            }
            runWrapped();
        } catch (CallbackException e) {
            throw e;
        } catch (Throwable t) {
            notifyFailed();
        }
    }
    
    private void runWrapped() {
        switch (runReason) {
            case INITIALIZE:
                stage = getNextStage(Stage.INITIALIZE);
                currentGenerator = getNextGenerator();
                runGenerators();
                break;
            case SWITCH_TO_SOURCE_SERVICE:
                runGenerators();
                break;
            case DECODE_DATA:
                decodeFromRetrievedData();
                break;
        }
    }
    
    private Stage getNextStage(Stage current) {
        switch (current) {
            case INITIALIZE:
                return diskCacheStrategy.decodeCachedResource() 
                    ? Stage.RESOURCE_CACHE : getNextStage(Stage.RESOURCE_CACHE);
            case RESOURCE_CACHE:
                return diskCacheStrategy.decodeCachedData() 
                    ? Stage.DATA_CACHE : getNextStage(Stage.DATA_CACHE);
            case DATA_CACHE:
                return Stage.SOURCE;
            default:
                return Stage.FINISHED;
        }
    }
}
```

### 8.5 BitmapPool 实现

```java
// LruBitmapPool.java
public class LruBitmapPool implements BitmapPool {
    
    private final LruPoolStrategy strategy;
    private final Set<Bitmap.Config> allowedConfigs;
    
    @Override
    public Bitmap get(int width, int height, Bitmap.Config config) {
        Bitmap result = strategy.get(width, height, config);
        if (result != null) {
            result.eraseColor(Color.TRANSPARENT);
            return result;
        }
        return Bitmap.createBitmap(width, height, config);
    }
    
    @Override
    public void put(Bitmap bitmap) {
        if (bitmap == null || bitmap.isRecycled()) {
            return;
        }
        if (!bitmap.isMutable() || strategy.getSize(bitmap) > maxSize 
            || !allowedConfigs.contains(bitmap.getConfig())) {
            bitmap.recycle();
            return;
        }
        strategy.put(bitmap);
    }
}
```

---

## 9. Glide 性能优化

### 9.1 内存优化

```java
// 1. 使用 RGB_565 格式
Glide.with(context)
    .load(url)
    .format(DecodeFormat.PREFER_RGB_565) // 每像素 2 字节，节省 50% 内存
    .into(imageView);

// 2. 使用 override 控制大小
Glide.with(context)
    .load(url)
    .override(imageView.getWidth(), imageView.getHeight())
    .into(imageView);

// 3. Bitmap 复用（自动）
// Glide 内部自动使用 BitmapPool 复用 Bitmap

// 4. 清理缓存
@Override
public void onLowMemory() {
    super.onLowMemory();
    Glide.get(this).clearMemory();
}

@Override
public void onTrimMemory(int level) {
    super.onTrimMemory(level);
    Glide.get(this).trimMemory(level);
}
```

### 9.2 加载优化

```java
// 1. 缩略图策略
Glide.with(context)
    .load(url)
    .thumbnail(0.1f)  // 先加载 10% 质量
    .into(imageView);

// 2. 使用 WebP 格式
// 服务端优先提供 WebP 格式

// 3. 预加载
Glide.with(context)
    .load(url)
    .preload();
```

### 9.3 网络优化

```java
// OkHttp 集成
@GlideModule
public class OkHttpGlideModule extends LibraryGlideModule {
    @Override
    public void registerComponents(Context context, Glide glide, Registry registry) {
        OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(20, TimeUnit.SECONDS)
            .build();
        
        registry.replace(GlideUrl.class, InputStream.class, 
            new OkHttpUrlLoader.Factory(client));
    }
}
```

### 9.4 列表优化

```java
// RecyclerView 中使用
@Override
public void onBindViewHolder(ViewHolder holder, int position) {
    Glide.with(context)
        .load(urls.get(position))
        .placeholder(R.drawable.placeholder)
        .into(holder.imageView);
}

// 或者使用 clear 来避免复用问题
@Override
public void onViewRecycled(ViewHolder holder) {
    Glide.with(context).clear(holder.imageView);
}
```

---

## 10. Glide 面试常见问题

### 10.1 生命周期绑定

**Q: Glide 如何实现生命周期绑定？**

**A:** Glide 通过添加一个无 UI 的 Fragment（SupportRequestManagerFragment）到 Activity/Fragment 中，监听 Fragment 的生命周期事件，从而控制图片加载请求的暂停、恢复和销毁。

```java
// 核心代码
FragmentManager fm = activity.getSupportFragmentManager();
SupportRequestManagerFragment fragment = (SupportRequestManagerFragment) 
    fm.findFragmentByTag(FRAGMENT_TAG);
if (fragment == null) {
    fragment = new SupportRequestManagerFragment();
    fm.beginTransaction().add(fragment, FRAGMENT_TAG).commit();
}
```

### 10.2 缓存机制

**Q: Glide 的缓存机制是怎样的？**

**A:** Glide 采用三级缓存：

1. **活动资源（Active Resources）**：弱引用持有正在使用的资源，引用计数管理
2. **内存缓存（Memory Cache）**：LRU 策略，存储最近使用的资源
3. **磁盘缓存（Disk Cache）**：LRU 策略，持久化存储

查找顺序：活动资源 → 内存缓存 → 磁盘缓存 → 网络/本地

### 10.3 OOM 避免

**Q: Glide 如何避免 OOM？**

**A:**
1. **自动降采样**：根据 ImageView 大小自动调整图片尺寸
2. **Bitmap 复用**：使用 BitmapPool 复用 Bitmap，减少内存分配
3. **RGB_565 格式**：相比 ARGB_8888 节省 50% 内存
4. **生命周期管理**：自动释放不再需要的资源
5. **内存缓存大小限制**：默认使用可用内存的 1/8

### 10.4 与 Picasso 区别

**Q: Glide 与 Picasso 的区别？**

| 对比项 | Glide | Picasso |
|--------|-------|---------|
| 缓存 | 三级缓存（含活动资源） | 二级缓存 |
| 生命周期 | 自动绑定 | 需手动管理 |
| 图片格式 | RGB_565（默认） | ARGB_8888 |
| GIF 支持 | 原生支持 | 不支持 |
| 包大小 | 较大 | 较小 |
| Bitmap 复用 | 支持 | 不支持 |
| 速度 | 较快（缓存更完善） | 较慢 |

### 10.5 高清图加载

**Q: 如何让 Glide 加载高清图？**

**A:**
```java
Glide.with(context)
    .load(url)
    .format(DecodeFormat.PREFER_ARGB_8888) // 使用 ARGB_8888
    .override(Target.SIZE_ORIGINAL)        // 原始尺寸
    .into(imageView);
```

### 10.6 圆角实现

**Q: Glide 如何实现圆角图片？**

**A:**
```java
// 方式1：使用内置的 circleCrop
Glide.with(context)
    .load(url)
    .circleCrop()
    .into(imageView);

// 方式2：使用 RequestOptions
Glide.with(context)
    .load(url)
    .apply(RequestOptions.bitmapTransform(new RoundedCorners(20)))
    .into(imageView);

// 方式3：自定义 Transformation
```

### 10.7 请求取消

**Q: Glide 如何取消请求？**

**A:**
```java
// 方式1：通过 View
Glide.with(context).clear(imageView);

// 方式2：通过 Target
Target<Drawable> target = Glide.with(context)
    .load(url)
    .into(imageView);
Glide.with(context).clear(target);

// 方式3：自动取消（生命周期销毁时自动调用）
```

### 10.8 预加载

**Q: Glide 如何实现图片预加载？**

**A:**
```java
// 预加载到缓存
Glide.with(context)
    .load(url)
    .preload(width, height);

// 下载到磁盘
Glide.with(context)
    .downloadOnly()
    .load(url)
    .submit();
```

### 10.9 缓存 Key

**Q: Glide 的缓存 Key 由什么决定？**

**A:**
- 图片地址（model）
- 目标尺寸（width/height）
- 签名（signature）
- 变换（transformations）
- 配置选项（options）
- 资源类型（resourceClass）
- 转码类型（transcodeClass）

任何一个因素变化，都会生成不同的缓存 Key。

### 10.10 进度监听

**Q: 如何监听 Glide 的加载进度？**

**A:** 需要自定义 OkHttp 的 ProgressResponseBody：

```java
public class ProgressResponseBody extends ResponseBody {
    private ResponseBody responseBody;
    private ProgressListener listener;
    
    @Override
    public Source source() {
        return Okio.buffer(new ForwardingSource(responseBody.source()) {
            long totalBytesRead = 0L;
            
            @Override
            public long read(Buffer sink, long byteCount) throws IOException {
                long bytesRead = super.read(sink, byteCount);
                totalBytesRead += bytesRead != -1 ? bytesRead : 0;
                listener.onProgress(totalBytesRead, responseBody.contentLength());
                return bytesRead;
            }
        });
    }
}
```

---

## 第二部分：Fresco - Facebook 的图片加载库

---

## 11. Fresco 概述

### 11.1 什么是 Fresco？

**Fresco** 是 Facebook 开源的 Android 图片加载库，专注于高性能和内存优化。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Fresco 核心特性                                      │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │    Fresco    │
                         └──────┬───────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  内存管理     │      │  图片加载     │      │  高级特性     │
│               │      │               │      │               │
│ - Ashmem      │      │ - 网络        │      │ - 渐进式JPEG  │
│ - Native堆    │      │ - 本地        │      │ - 后处理器    │
│ - 自动释放    │      │ - GIF/WebP    │      │ - 多请求      │
└───────────────┘      └───────────────┘      └───────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  UI组件       │      │  缓存机制     │      │  性能优化     │
│               │      │               │      │               │
│- DraweeView   │      │ - 三级缓存    │      │ - 智能预加载  │
│- Hierarchy    │      │ - 内存缓存    │      │ - 图片解码    │
│- Controller   │      │ - 磁盘缓存    │      │ - 网络优化    │
└───────────────┘      └───────────────┘      └───────────────┘
```

### 11.2 核心优势

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Fresco vs 其他图片库                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────────────────┐
│       优势        │                          说明                            │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 内存管理优势      │ 使用 Ashmem（匿名共享内存）和 Native 堆，避免 OOM        │
│ 渐进式 JPEG      │ 支持渐进式 JPEG，先显示模糊图再逐渐清晰                 │
│ GIF/WebP 动画    │ 原生支持 GIF 和 WebP 动画                               │
│ 后处理器         │ 加载后可以对图片进行处理（模糊、圆角等）                 │
│ 多图请求         │ 支持同时请求多个图片源，取最快返回的                     │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

### 11.3 添加依赖

```gradle
dependencies {
    implementation 'com.facebook.fresco:fresco:3.1.3'
    
    // 可选：GIF 支持
    implementation 'com.facebook.fresco:animated-gif:3.1.3'
    
    // 可选：WebP 支持
    implementation 'com.facebook.fresco:animated-webp:3.1.3'
    implementation 'com.facebook.fresco:webpsupport:3.1.3'
    
    // 可选：OkHttp 网络层
    implementation 'com.facebook.fresco:imagepipeline-okhttp3:3.1.3'
}
```

### 11.4 初始化配置

```java
// 在 Application 中初始化
public class MyApplication extends Application {
    
    @Override
    public void onCreate() {
        super.onCreate();
        
        // 方式1: 默认配置
        Fresco.initialize(this);
        
        // 方式2: 自定义配置
        ImagePipelineConfig config = ImagePipelineConfig.newBuilder(this)
            .setBitmapsConfig(Bitmap.Config.ARGB_8888)
            .setBitmapMemoryCacheParamsSupplier(new Supplier<MemoryCacheParams>() {
                @Override
                public MemoryCacheParams get() {
                    return new MemoryCacheParams(
                        60 * 1024 * 1024,  // 最大内存：60MB
                        256,                // 最大缓存数量
                        Integer.MAX_VALUE,  // 最大驱逐大小
                        Integer.MAX_VALUE,  // 最大驱逐数量
                        Integer.MAX_VALUE   // 最大缓存存活时间
                    );
                }
            })
            .setMainDiskCacheConfig(
                DiskCacheConfig.newBuilder(this)
                    .setBaseDirectoryPath(getCacheDir())
                    .setMaxCacheSize(250 * 1024 * 1024)  // 250MB
                    .build()
            )
            .build();
        
        Fresco.initialize(this, config);
    }
}
```

---

## 12. Fresco 基本使用

### 12.1 SimpleDraweeView

```xml
<!-- 在 XML 中使用 -->
<com.facebook.drawee.view.SimpleDraweeView
    android:id="@+id/my_image_view"
    android:layout_width="130dp"
    android:layout_height="130dp"
    fresco:placeholderImage="@drawable/my_placeholder"
    fresco:roundAsCircle="true" />
```

### 12.2 加载网络图片

```java
// 基础用法
Uri uri = Uri.parse("https://example.com/image.jpg");
SimpleDraweeView draweeView = findViewById(R.id.my_image_view);
draweeView.setImageURI(uri);

// 带配置的加载
ImageRequest request = ImageRequestBuilder
    .newBuilderWithSource(uri)
    .setResizeOptions(new ResizeOptions(800, 600))
    .setLocalThumbnailPreviewsEnabled(true)
    .build();

DraweeController controller = Fresco.newDraweeControllerBuilder()
    .setImageRequest(request)
    .setOldController(draweeView.getController())
    .build();

draweeView.setController(controller);
```

### 12.3 加载本地图片

```java
// 加载资源 ID
Uri uri = Uri.parse("res://com.example.app/" + R.drawable.image);
draweeView.setImageURI(uri);

// 加载本地文件
Uri fileUri = Uri.parse("file:///sdcard/image.jpg");
draweeView.setImageURI(fileUri);

// 加载 ContentProvider
Uri contentUri = Uri.parse("content://media/external/images/media/1");
draweeView.setImageURI(contentUri);
```

### 12.4 占位图和进度条

```java
// XML 配置
<com.facebook.drawee.view.SimpleDraweeView
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    fresco:placeholderImage="@drawable/placeholder"
    fresco:placeholderImageScaleType="fitCenter"
    fresco:progressBarImage="@drawable/progress_bar"
    fresco:progressBarImageScaleType="centerInside"
    fresco:progressBarAutoRotateInterval="1000"
    fresco:failureImage="@drawable/error"
    fresco:failureImageScaleType="centerInside" />

// 代码配置
GenericDraweeHierarchy hierarchy = GenericDraweeHierarchyBuilder
    .newInstance(getResources())
    .setPlaceholderImage(R.drawable.placeholder)
    .setProgressBarImage(new ProgressBarDrawable())
    .setFailureImage(R.drawable.error)
    .build();

draweeView.setHierarchy(hierarchy);
```

### 12.5 加载 GIF

```java
// 自动播放 GIF
Uri gifUri = Uri.parse("https://example.com/animation.gif");

DraweeController controller = Fresco.newDraweeControllerBuilder()
    .setUri(gifUri)
    .setAutoPlayAnimations(true)  // 自动播放
    .setOldController(draweeView.getController())
    .build();

draweeView.setController(controller);

// 手动控制 GIF
ControllerListener listener = new BaseControllerListener() {
    @Override
    public void onFinalImageSet(String id, Object imageInfo, Animatable animatable) {
        if (animatable != null) {
            // 播放
            animatable.start();
            
            // 暂停
            // animatable.stop();
        }
    }
};

DraweeController controller = Fresco.newDraweeControllerBuilder()
    .setUri(gifUri)
    .setControllerListener(listener)
    .build();
```

### 12.6 图片缩放

```xml
<!-- XML 配置 -->
<com.facebook.drawee.view.SimpleDraweeView
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    fresco:actualImageScaleType="centerCrop" />
```

```java
// 代码配置
GenericDraweeHierarchy hierarchy = draweeView.getHierarchy();
hierarchy.setActualImageScaleType(ScalingUtils.ScaleType.CENTER_CROP);

// 可选缩放类型：
// - CENTER: 居中，不缩放
// - CENTER_CROP: 等比缩放，裁剪填充
// - CENTER_INSIDE: 等比缩放，完整显示
// - FIT_CENTER: 等比缩放，居中
// - FIT_START: 等比缩放，顶部对齐
// - FIT_END: 等比缩放，底部对齐
// - FIT_XY: 拉伸填充
// - FOCUS_CROP: 根据焦点裁剪
```

---

## 13. Fresco 核心概念

### 13.1 DraweeView

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DraweeView 层次结构                                  │
