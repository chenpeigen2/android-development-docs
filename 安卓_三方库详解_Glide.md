# Glide - Android 图片加载库详解

> 📚 **文档定位**：全面解析 Glide 的核心原理、使用方法、源码分析和最佳实践  
> 🎯 **适用场景**：Android 面试准备、实际项目开发、性能优化参考

---

## 目录

1. [Glide 概述](#1-glide-概述)
2. [基本使用](#2-基本使用)
3. [核心原理](#3-核心原理)
4. [缓存机制](#4-缓存机制)
5. [生命周期管理](#5-生命周期管理)
6. [图片转换与变换](#6-图片转换与变换)
7. [高级用法](#7-高级用法)
8. [性能优化](#8-性能优化)
9. [源码解析](#9-源码解析)
10. [面试常见问题](#10-面试常见问题)
11. [与其他图片库对比](#11-与其他图片库对比)

---

## 1. Glide 概述

### 1.1 什么是 Glide？

**Glide** 是 Google 推荐的 Android 图片加载库，由 Bump Technologies 开发，后被 Google 收购并维护。

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| **简单易用** | 流式 API，一行代码完成加载 |
| **高性能** | 自动降采样、位图池复用 |
| **智能缓存** | 二级缓存（内存 + 磁盘），支持多种缓存策略 |
| **生命周期感知** | 自动绑定 Activity/Fragment 生命周期 |
| **GIF/WebP 支持** | 原生支持 GIF 动图和 WebP 格式 |
| **图片转换** | 内置模糊、圆角、灰度等变换 |
| ** thumbnail** | 缩略图支持，先加载小图再加载大图 |

### 1.3 添加依赖

```gradle
dependencies {
    implementation 'com.github.bumptech.glide:glide:4.16.0'
    annotationProcessor 'com.github.bumptech.glide:compiler:4.16.0'
}
```

---

## 2. 基本使用

### 2.1 最简单的加载

```java
Glide.with(context)
    .load(url)
    .into(imageView);
```

### 2.2 加载不同来源

```java
// 加载网络图片
Glide.with(context).load("https://example.com/image.jpg").into(imageView);

// 加载本地资源
Glide.with(context).load(R.drawable.image).into(imageView);

// 加载本地文件
Glide.with(context).load(new File("/sdcard/image.jpg")).into(imageView);

// 加载 Uri
Glide.with(context).load(uri).into(imageView);

// 加载 byte[]
byte[] imageBytes = ...;
Glide.with(context).load(imageBytes).into(imageView);
```

### 2.3 占位图和错误图

```java
Glide.with(context)
    .load(url)
    .placeholder(R.drawable.placeholder)    // 加载中占位图
    .error(R.drawable.error)                // 加载失败图
    .fallback(R.drawable.fallback)          // url 为 null 时的图
    .into(imageView);
```

### 2.4 指定图片大小

```java
Glide.with(context)
    .load(url)
    .override(800, 600)        // 指定目标尺寸
    .override(Target.SIZE_ORIGINAL)  // 原始尺寸
    .into(imageView);
```

### 2.5 缩略图

```java
// 先加载 10% 质量的缩略图，再加载原图
Glide.with(context)
    .load(url)
    .thumbnail(0.1f)
    .into(imageView);

// 加载不同的缩略图
Glide.with(context)
    .load(url)
    .thumbnail(Glide.with(context).load(thumbnailUrl))
    .into(imageView);
```

### 2.6 加载 GIF

```java
// 自动检测并加载 GIF
Glide.with(context).load(gifUrl).into(imageView);

// 强制作为 GIF 加载
Glide.with(context)
    .asGif()
    .load(gifUrl)
    .into(imageView);

// 加载 GIF 的某一帧
Glide.with(context)
    .asBitmap()
    .load(gifUrl)
    .into(imageView);
```

### 2.7 清除图片

```java
// 清除 View 上的图片
Glide.with(context).clear(imageView);

// 清除所有缓存（需要在后台线程）
new Thread(() -> {
    Glide.get(context).clearDiskCache();
}).start();

// 清除内存缓存（主线程）
Glide.get(context).clearMemory();
```

---

## 3. 核心原理

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Glide                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Request    │  │    Engine    │  │    Decode    │      │
│  │   Manager    │──│    (核心)    │──│    Job       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         ▼                  ▼                  ▼              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Lifecycle   │  │    Cache     │  │    Bitmap    │      │
│  │  Manager     │  │   (缓存)     │  │     Pool     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 核心组件

#### 3.2.1 Glide（单例）
- 负责初始化和协调各组件
- 管理 RequestManagerRetriever
- 管理内存缓存、磁盘缓存、线程池

#### 3.2.2 RequestManager
- 管理图片加载请求
- 绑定生命周期
- 取消、暂停、恢复请求

#### 3.2.3 Engine
- 核心引擎，负责加载任务的调度
- 管理活动资源和缓存
- 启动 DecodeJob 执行解码

#### 3.2.4 DecodeJob
- 图片解码任务
- 从缓存或数据源加载数据
- 执行图片变换

#### 3.2.5 BitmapPool
- 位图复用池
- 减少 Bitmap 内存分配和 GC

### 3.3 加载流程

```
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

## 4. 缓存机制

### 4.1 缓存层级

Glide 采用**三级缓存**机制：

```
┌─────────────────────────────────────────────────────────┐
│  第一级：活动资源 (Active Resources)                     │
│  - 引用计数管理                                          │
│  - 当前正在使用的资源                                    │
│  - 弱引用持有，不参与 LRU                                │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  第二级：内存缓存 (Memory Cache)                        │
│  - LRU 策略                                              │
│  - 基于最近使用时间                                      │
│  - 快速访问，但占用内存                                  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  第三级：磁盘缓存 (Disk Cache)                          │
│  - LRU 策略                                              │
│  - 持久化存储                                            │
│  - 包括原始图片和解码后的图片                            │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  数据源 (Data Source)                                   │
│  - 网络、本地文件、ContentProvider 等                    │
└─────────────────────────────────────────────────────────┘
```

### 4.2 缓存 Key 的生成

缓存 Key 由以下因素决定：

```java
Key = EngineKey {
    model,          // 图片地址
    width,          // 目标宽度
    height,         // 目标高度
    signature,      // 签名（版本号等）
    transformations,// 变换
    options,        // 配置选项
    resourceClass,  // 资源类型
    transcodeClass  // 转码类型
}
```

### 4.3 缓存策略

Glide 提供多种缓存策略：

```java
// 默认策略：自动选择
.diskCacheStrategy(DiskCacheStrategy.AUTOMATIC)

// 只缓存原始图片
.diskCacheStrategy(DiskCacheStrategy.DATA)

// 只缓存解码后的图片
.diskCacheStrategy(DiskCacheStrategy.RESOURCE)

// 缓存原始和解码后的图片
.diskCacheStrategy(DiskCacheStrategy.ALL)

// 禁用磁盘缓存
.diskCacheStrategy(DiskCacheStrategy.NONE)
```

### 4.4 跳过缓存

```java
// 跳过内存缓存
.skipMemoryCache(true)

// 跳过磁盘缓存
.diskCacheStrategy(DiskCacheStrategy.NONE)
```

### 4.5 自定义缓存大小

```java
@GlideModule
public class CustomGlideModule extends AppGlideModule {
    @Override
    public void applyOptions(Context context, GlideBuilder builder) {
        // 设置内存缓存大小（默认是可用内存的 1/8）
        int memoryCacheSizeBytes = 1024 * 1024 * 50; // 50MB
        builder.setMemoryCache(new LruResourceCache(memoryCacheSizeBytes));
        
        // 设置磁盘缓存大小（默认 250MB）
        int diskCacheSizeBytes = 1024 * 1024 * 500; // 500MB
        builder.setDiskCache(new InternalCacheDiskCacheFactory(
            context, diskCacheSizeBytes));
        
        // 设置 BitmapPool 大小
        builder.setBitmapPool(new LruBitmapPool(memoryCacheSizeBytes));
    }
}
```

### 4.6 缓存失效

```java
// 方式1：使用 signature
Glide.with(context)
    .load(url)
    .signature(new ObjectKey(System.currentTimeMillis())) // 每次都是新签名
    .into(imageView);

// 方式2：使用版本号
.signature(new StringKey("v1.0"))

// 方式3：清除特定缓存（需要自定义 Key）
```

---

## 5. 生命周期管理

### 5.1 为什么需要生命周期管理？

1. **避免内存泄漏**：Activity 销毁时停止加载
2. **节省资源**：后台时不进行图片加载
3. **提升体验**：自动暂停和恢复请求

### 5.2 实现原理

Glide 通过 **SupportRequestManagerFragment** 实现生命周期绑定：

```
Activity/Fragment
        │
        ▼
SupportRequestManagerFragment (无 UI 的 Fragment)
        │
        ▼
Lifecycle (生命周期分发器)
        │
        ▼
RequestManager (监听生命周期事件)
        │
        ▼
Request (暂停/恢复/取消)
```

### 5.3 源码分析

```java
// RequestManagerRetriever.java
public RequestManager get(FragmentActivity activity) {
    if (Util.isOnBackgroundThread()) {
        return get(activity.getApplicationContext());
    } else {
        assertNotDestroyed(activity);
        FragmentManager fm = activity.getSupportFragmentManager();
        return supportFragmentGet(activity, fm, null);
    }
}

private RequestManager supportFragmentGet(Context context, FragmentManager fm,
                                          Fragment parentHint) {
    // 获取或创建无 UI 的 Fragment
    SupportRequestManagerFragment current = getSupportRequestManagerFragment(fm);
    RequestManager requestManager = current.getRequestManager();
    if (requestManager == null) {
        requestManager = new RequestManager(context, current.getLifecycle(), ...);
        current.setRequestManager(requestManager);
    }
    return requestManager;
}
```

### 5.4 生命周期事件处理

```java
// RequestManager.java
public synchronized void onStart() {
    resumeRequests();
    targetTracker.onStart();
}

public synchronized void onStop() {
    pauseRequests();
    targetTracker.onStop();
}

public synchronized void onDestroy() {
    targetTracker.onDestroy();
    for (Target<?> target : targetTracker.getAll()) {
        clear(target);
    }
    targetTracker.clear();
    requestTracker.clearRequests();
    lifecycle.removeListener(this);
}
```

### 5.5 不同 Context 的影响

```java
// Activity/Fragment Context → 绑定生命周期
Glide.with(activity).load(url).into(imageView);

// Application Context → 不绑定生命周期，直到应用退出
Glide.with(applicationContext).load(url).into(imageView);

// View → 自动获取 Activity Context
Glide.with(imageView).load(url).into(imageView);
```

---

## 6. 图片转换与变换

### 6.1 内置变换

```java
// 圆形
.circleCrop()

// 居中裁剪
.centerCrop()

// 适应中心
.centerInside()

// 填充
.fitCenter()
```

### 6.2 自定义变换

```java
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

### 6.3 使用变换

```java
// 单个变换
Glide.with(context)
    .load(url)
    .transform(new BlurTransformation(25))
    .into(imageView);

// 多个变换
Glide.with(context)
    .load(url)
    .transforms(
        new CenterCrop(),
        new BlurTransformation(25),
        new RoundedCorners(20)
    )
    .into(imageView);
```

### 6.4 第三方变换库

```gradle
implementation 'jp.wasabeef:glide-transformations:4.3.0'
```

```java
Glide.with(context)
    .load(url)
    .apply(RequestOptions.bitmapTransform(
        new BlurTransformation(25, 3)))
    .into(imageView);
```

---

## 7. 高级用法

### 7.1 自定义模块

```java
@GlideModule
public class CustomGlideModule extends AppGlideModule {
    
    @Override
    public void applyOptions(Context context, GlideBuilder builder) {
        // 配置缓存大小、日志级别等
        builder.setDefaultRequestOptions(
            new RequestOptions()
                .format(DecodeFormat.PREFER_RGB_565)
                .diskCacheStrategy(DiskCacheStrategy.ALL)
        );
    }
    
    @Override
    public void registerComponents(Context context, Glide glide, Registry registry) {
        // 注册自定义组件
        registry.append(String.class, InputStream.class, 
            new CustomUrlLoader.Factory());
    }
}
```

### 7.2 自定义 ModelLoader

用于自定义数据源（如自定义协议、加密图片等）：

```java
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
```

### 7.3 自定义 DataFetcher

```java
public class CustomDataFetcher implements DataFetcher<InputStream> {
    
    private CustomData data;
    
    public CustomDataFetcher(CustomData data) {
        this.data = data;
    }
    
    @Override
    public void loadData(Priority priority, DataCallback<? super InputStream> callback) {
        try {
            InputStream stream = fetchDataFromCustomSource(data);
            callback.onDataReady(stream);
        } catch (Exception e) {
            callback.onLoadFailed(e);
        }
    }
    
    @Override
    public void cleanup() {
        // 清理资源
    }
    
    @Override
    public void cancel() {
        // 取消请求
    }
    
    @Override
    public Class<InputStream> getDataClass() {
        return InputStream.class;
    }
    
    @Override
    public DataSource getDataSource() {
        return DataSource.REMOTE;
    }
}
```

### 7.4 监听请求状态

```java
Glide.with(context)
    .load(url)
    .listener(new RequestListener<Drawable>() {
        @Override
        public boolean onLoadFailed(GlideException e, Object model,
                                    Target<Drawable> target, boolean isFirstResource) {
            // 加载失败
            return false; // 返回 false 让 error 占位图显示
        }
        
        @Override
        public boolean onResourceReady(Drawable resource, Object model,
                                       Target<Drawable> target, DataSource dataSource,
                                       boolean isFirstResource) {
            // 加载成功
            return false; // 返回 false 让图片正常显示
        }
    })
    .into(imageView);
```

### 7.5 预加载

```java
// 预加载到缓存
Glide.with(context)
    .load(url)
    .preload(800, 600);

// 预加载并指定回调
Glide.with(context)
    .downloadOnly()
    .load(url)
    .into(new Target<File>() {
        @Override
        public void onResourceReady(File resource, Transition<? super File> transition) {
            // 预加载完成
        }
        // ... 其他方法
    });
```

### 7.6 同步加载

```java
// 在后台线程同步加载
FutureTarget<Bitmap> futureTarget = Glide.with(context)
    .asBitmap()
    .load(url)
    .submit();

try {
    Bitmap bitmap = futureTarget.get(); // 阻塞等待
    // 使用 bitmap
} catch (Exception e) {
    e.printStackTrace();
} finally {
    futureTarget.cancel(true);
}
```

---

## 8. 性能优化

### 8.1 内存优化

#### 使用 RGB_565 格式

```java
Glide.with(context)
    .load(url)
    .format(DecodeFormat.PREFER_RGB_565) // 每像素 2 字节，节省 50% 内存
    .into(imageView);
```

#### 使用 override 控制大小

```java
Glide.with(context)
    .load(url)
    .override(imageView.getWidth(), imageView.getHeight())
    .into(imageView);
```

#### Bitmap 复用

Glide 内部自动使用 BitmapPool 复用 Bitmap：

```java
// 查看复用情况
Glide.get(context).getBitmapPool().clearMemory();
```

### 8.2 加载优化

#### 缩略图策略

```java
// 先加载小图，再加载大图
Glide.with(context)
    .load(url)
    .thumbnail(0.1f)
    .into(imageView);
```

#### 使用 WebP 格式

```java
// 服务端优先提供 WebP 格式
```

### 8.3 网络优化

#### OkHttp 集成

```gradle
implementation "com.github.bumptech.glide:okhttp3-integration:4.16.0"
```

```java
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

### 8.4 列表优化

```java
// 在 RecyclerView 中使用
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

### 8.5 内存监控

```java
// 在低内存时清理缓存
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

---

## 9. 源码解析

### 9.1 Glide 初始化

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

### 9.2 Request 构建

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

### 9.3 Engine 加载

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

### 9.4 DecodeJob 解码

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

### 9.5 BitmapPool 实现

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

## 10. 面试常见问题

### Q1: Glide 如何实现生命周期绑定？

**答**：Glide 通过添加一个无 UI 的 Fragment（SupportRequestManagerFragment）到 Activity/Fragment 中，监听 Fragment 的生命周期事件，从而控制图片加载请求的暂停、恢复和销毁。

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

### Q2: Glide 的缓存机制是怎样的？

**答**：Glide 采用三级缓存：

1. **活动资源（Active Resources）**：弱引用持有正在使用的资源，引用计数管理
2. **内存缓存（Memory Cache）**：LRU 策略，存储最近使用的资源
3. **磁盘缓存（Disk Cache）**：LRU 策略，持久化存储

查找顺序：活动资源 → 内存缓存 → 磁盘缓存 → 网络/本地

### Q3: Glide 如何避免 OOM？

**答**：
1. **自动降采样**：根据 ImageView 大小自动调整图片尺寸
2. **Bitmap 复用**：使用 BitmapPool 复用 Bitmap，减少内存分配
3. **RGB_565 格式**：相比 ARGB_8888 节省 50% 内存
4. **生命周期管理**：自动释放不再需要的资源
5. **内存缓存大小限制**：默认使用可用内存的 1/8

### Q4: Glide 与 Picasso 的区别？

| 对比项 | Glide | Picasso |
|--------|-------|---------|
| 缓存 | 三级缓存（含活动资源） | 二级缓存 |
| 生命周期 | 自动绑定 | 需手动管理 |
| 图片格式 | RGB_565（默认） | ARGB_8888 |
| GIF 支持 | 原生支持 | 不支持 |
| 包大小 | 较大 | 较小 |
| Bitmap 复用 | 支持 | 不支持 |
| 速度 | 较快（缓存更完善） | 较慢 |

### Q5: 如何让 Glide 加载高清图？

**答**：
```java
Glide.with(context)
    .load(url)
    .format(DecodeFormat.PREFER_ARGB_8888) // 使用 ARGB_8888
    .override(Target.SIZE_ORIGINAL)        // 原始尺寸
    .into(imageView);
```

### Q6: Glide 如何实现圆角图片？

**答**：
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

### Q7: Glide 如何取消请求？

**答**：
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

### Q8: Glide 如何实现图片预加载？

**答**：
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

### Q9: Glide 的缓存 Key 由什么决定？

**答**：
- 图片地址（model）
- 目标尺寸（width/height）
- 签名（signature）
- 变换（transformations）
- 配置选项（options）
- 资源类型（resourceClass）
- 转码类型（transcodeClass）

任何一个因素变化，都会生成不同的缓存 Key。

### Q10: 如何监听 Glide 的加载进度？

**答**：需要自定义 OkHttp 的 ProgressResponseBody：

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

## 11. 与其他图片库对比

### 11.1 Glide vs Picasso

| 特性 | Glide | Picasso |
|------|-------|---------|
| 易用性 | ★★★★★ | ★★★★★ |
| 性能 | ★★★★★ | ★★★★☆ |
| 内存占用 | ★★★★☆ | ★★★☆☆ |
| 功能丰富度 | ★★★★★ | ★★★☆☆ |
| 包大小 | ★★★☆☆ | ★★★★☆ |

### 11.2 Glide vs Fresco

| 特性 | Glide | Fresco |
|------|-------|--------|
| 易用性 | ★★★★★ | ★★★☆☆ |
| 性能 | ★★★★★ | ★★★★★ |
| 内存优化 | ★★★★☆ | ★★★★★ |
| 功能丰富度 | ★★★★★ | ★★★★★ |
| 学习曲线 | ★★★★☆ | ★★★☆☆ |

### 11.3 Glide vs Coil

| 特性 | Glide | Coil |
|------|-------|------|
| 易用性 | ★★★★★ | ★★★★★ |
| 性能 | ★★★★★ | ★★★★★ |
| Kotlin 支持 | ★★★☆☆ | ★★★★★ |
| 现代 API | ★★★☆☆ | ★★★★★ |
| 社区活跃度 | ★★★★★ | ★★★★☆ |

### 11.4 选型建议

- **Glide**：通用场景，功能全面，适合大多数项目
- **Picasso**：简单项目，包大小敏感
- **Fresco**：内存敏感场景，大量图片加载
- **Coil**：Kotlin 项目，追求现代 API

---

## 12. 总结

### 12.1 Glide 的优势

1. **功能全面**：支持 GIF、WebP、视频帧、缩略图等
2. **性能优秀**：三级缓存、Bitmap 复用、自动降采样
3. **易于使用**：流式 API，一行代码完成加载
4. **生命周期感知**：自动管理请求，避免内存泄漏
5. **扩展性强**：支持自定义 ModelLoader、Transformation

### 12.2 最佳实践

1. **使用 Application Context**：在 Service、BroadcastReceiver 中
2. **指定图片大小**：使用 override 避免加载过大图片
3. **合理配置缓存**：根据场景选择缓存策略
4. **及时清理**：在 onTrimMemory 中清理缓存
5. **使用 thumbnail**：提升用户体验

### 12.3 注意事项

1. **不要在非主线程调用 with(Activity)**
2. **不要忘记添加 Internet 权限**
3. **混淆配置**：添加 Glide 的 ProGuard 规则
4. **版本兼容**：使用最新稳定版本

---

## 参考资料

- [Glide 官方文档](https://bumptech.github.io/glide/)
- [Glide GitHub](https://github.com/bumptech/glide)
- [Android 图片加载库对比](https://developer.android.com/topic/libraries/architecture/)
- [Glide 源码解析系列](https://www.jianshu.com/c/1c987e84c7d1)

---

**文档版本**：v1.0  
**更新时间**：2025年3月  
**适用版本**：Glide 4.16.0

