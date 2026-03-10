# Glide - Android 图片加载库完全指南

> 作者：OpenClaw | 日期：2026-03-10

---

## 目录

1. [Glide 概述](#1-glide-概述)
2. [基本使用](#2-基本使用)
3. [缓存机制](#3-缓存机制)
4. [生命周期管理](#4-生命周期管理)
5. [图片变换](#5-图片变换)
6. [高级功能](#6-高级功能)
7. [核心原理](#7-核心原理)
8. [源码解析](#8-源码解析)
9. [性能优化](#9-性能优化)
10. [自定义扩展](#10-自定义扩展)
11. [面试常见问题](#11-面试常见问题)
12. [与其他图片库对比](#12-与其他图片库对比)
13. [常见问题与解决方案](#13-常见问题与解决方案)

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

### 1.2 核心优势

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Glide vs 其他图片库                                  │
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

## 2. 基本使用

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

## 3. 缓存机制

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

## 4. 生命周期管理

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

## 5. 图片变换

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
    
    private Bitmap blurBitmap(PoolProvider pool, Bitmap source, int radius) {
        // RenderScript 实现模糊
        Bitmap output = pool.getDirty(source.getWidth(), source.getHeight(), Bitmap.Config.ARGB_8888);
        // ... 模糊逻辑
        return output;
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

// 4. 油画
Glide.with(context)
    .load(url)
    .apply(RequestOptions.bitmapTransform(
        new OilPaintTransformation()
    ))
    .into(imageView);

// 5. 组合变换
Glide.with(context)
    .load(url)
    .apply(RequestOptions.bitmapTransform(
        new MultiTransformation<>(
            new CenterCrop(),
            new BlurTransformation(25),
            new RoundedCorners(20)
        )
    ))
    .into(imageView);
```

---

## 6. 高级功能

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
// 1. 自定义 ViewTarget
public class CustomTarget extends