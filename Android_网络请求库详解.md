# Android 网络请求库完全指南

> 作者：OpenClaw | 日期：2026-03-10  
> 涵盖：OkHttp | Retrofit

---

## 📚 目录

### 第一篇：OkHttp - Square 出品的网络请求库

**第 1 章 OkHttp 概述**
- 1.1 [什么是 OkHttp？](#11-什么是-okhttp)
- 1.2 [核心优势](#12-核心优势)
- 1.3 [添加依赖](#13-添加依赖)
- 1.4 [权限配置](#14-权限配置)

**第 2 章 OkHttp 基本使用**
- 2.1 [创建 OkHttpClient](#21-创建-okhttpclient)
- 2.2 [同步请求](#22-同步请求)
- 2.3 [异步请求](#23-异步请求)
- 2.4 [GET 请求](#24-get-请求)
- 2.5 [POST 请求](#25-post-请求)
- 2.6 [文件上传](#26-文件上传)
- 2.7 [文件下载](#27-文件下载)

**第 3 章 OkHttp 拦截器**
- 3.1 [拦截器概述](#31-拦截器概述)
- 3.2 [应用拦截器](#32-应用拦截器)
- 3.3 [网络拦截器](#33-网络拦截器)
- 3.4 [日志拦截器](#34-日志拦截器)
- 3.5 [缓存拦截器](#35-缓存拦截器)
- 3.6 [头部拦截器](#36-头部拦截器)

**第 4 章 OkHttp 缓存机制**
- 4.1 [缓存策略](#41-缓存策略)
- 4.2 [缓存配置](#42-缓存配置)
- 4.3 [强制刷新](#43-强制刷新)
- 4.4 [离线缓存](#44-离线缓存)

**第 5 章 OkHttp 连接管理**
- 5.1 [连接池](#51-连接池)
- 5.2 [连接复用](#52-连接复用)
- 5.3 [连接超时](#53-连接超时)
- 5.4 [DNS 解析](#54-dns-解析)

**第 6 章 OkHttp 高级功能**
- 6.1 [WebSocket](#61-websocket)
- 6.2 [HTTPS 配置](#62-https-配置)
- 6.3 [证书绑定](#63-证书绑定)
- 6.4 [Cookie 管理](#64-cookie-管理)
- 6.5 [请求重试](#65-请求重试)

**第 7 章 OkHttp 核心原理**
- 7.1 [请求流程](#71-请求流程)
- 7.2 [拦截器链](#72-拦截器链)
- 7.3 [连接池原理](#73-连接池原理)
- 7.4 [缓存原理](#74-缓存原理)

**第 8 章 OkHttp 源码解析**
- 8.1 [OkHttpClient 创建](#81-okhttpclient-创建)
- 8.2 [Call 创建与执行](#82-call-创建与执行)
- 8.3 [Dispatcher 调度器](#83-dispatcher-调度器)
- 8.4 [ConnectionPool](#84-connectionpool)

**第 9 章 OkHttp 性能优化**
- 9.1 [连接优化](#91-连接优化)
- 9.2 [缓存优化](#92-缓存优化)
- 9.3 [请求优化](#93-请求优化)
- 9.4 [内存优化](#94-内存优化)

**第 10 章 OkHttp 面试常见问题**
- 10.1 [拦截器原理](#101-拦截器原理)
- 10.2 [连接池复用](#102-连接池复用)
- 10.3 [缓存策略](#103-缓存策略)
- 10.4 [同步 vs 异步](#104-同步-vs-异步)
- 10.5 [Dispatcher](#105-dispatcher)
- 10.6 [责任链模式](#106-责任链模式)
- 10.7 [WebSocket](#107-websocket)
- 10.8 [HTTPS 握手](#108-https-握手)
- 10.9 [OkHttp vs HttpURLConnection](#109-okhttp-vs-httpurlconnection)
- 10.10 [最佳实践](#1010-最佳实践)

---

### 第二篇：Retrofit - Square 出品的 REST 客户端

**第 11 章 Retrofit 概述**
- 11.1 [什么是 Retrofit？](#111-什么是-retrofit)
- 11.2 [核心优势](#112-核心优势)
- 11.3 [添加依赖](#113-添加依赖)
- 11.4 [与 OkHttp 关系](#114-与-okhttp-关系)

**第 12 章 Retrofit 基本使用**
- 12.1 [创建 Retrofit 实例](#121-创建-retrofit-实例)
- 12.2 [定义 API 接口](#122-定义-api-接口)
- 12.3 [GET 请求](#123-get-请求)
- 12.4 [POST 请求](#124-post-请求)
- 12.5 [PUT 请求](#125-put-请求)
- 12.6 [DELETE 请求](#126-delete-请求)

**第 13 章 Retrofit 注解详解**
- 13.1 [请求方法注解](#131-请求方法注解)
- 13.2 [请求头注解](#132-请求头注解)
- 13.3 [请求参数注解](#133-请求参数注解)
- 13.4 [请求体注解](#134-请求体注解)
- 13.5 [标记注解](#135-标记注解)

**第 14 章 Retrofit 高级功能**
- 14.1 [Converter 转换器](#141-converter-转换器)
- 14.2 [CallAdapter 适配器](#142-calladapter-适配器)
- 14.3 [文件上传](#143-文件上传)
- 14.4 [文件下载](#144-文件下载)
- 14.5 [动态 URL](#145-动态-url)
- 14.6 [取消请求](#146-取消请求)

**第 15 章 Retrofit 与协程**
- 15.1 [suspend 函数](#151-suspend-函数)
- 15.2 [Flow 集成](#152-flow-集成)
- 15.3 [异常处理](#153-异常处理)
- 15.4 [超时控制](#154-超时控制)

**第 16 章 Retrofit 与 RxJava**
- 16.1 [RxJava 集成](#161-rxjava-集成)
- 16.2 [Observable 转换](#162-observable-转换)
- 16.3 [线程调度](#163-线程调度)
- 16.4 [错误处理](#164-错误处理)

**第 17 章 Retrofit 核心原理**
- 17.1 [动态代理](#171-动态代理)
- 17.2 [注解解析](#172-注解解析)
- 17.3 [ServiceMethod](#173-servicemethod)
- 17.4 [OkHttpCall](#174-okhttpcall)

**第 18 章 Retrofit 源码解析**
- 18.1 [Retrofit 创建流程](#181-retrofit-创建流程)
- 18.2 [create 方法解析](#182-create-方法解析)
- 18.3 [loadServiceMethod](#183-loadservicemethod)
- 18.4 [invoke 方法](#184-invoke-方法)

**第 19 章 Retrofit 性能优化**
- 19.1 [单例模式](#191-单例模式)
- 19.2 [缓存优化](#192-缓存优化)
- 19.3 [请求优化](#193-请求优化)
- 19.4 [错误处理优化](#194-错误处理优化)

**第 20 章 Retrofit 面试常见问题**
- 20.1 [动态代理原理](#201-动态代理原理)
- 20.2 [注解解析流程](#202-注解解析流程)
- 20.3 [Converter 原理](#203-converter-原理)
- 20.4 [CallAdapter 原理](#204-calladapter-原理)
- 20.5 [与 OkHttp 关系](#205-与-okhttp-关系)
- 20.6 [线程切换](#206-线程切换)
- 20.7 [suspend 支持](#207-suspend-支持)
- 20.8 [文件上传原理](#208-文件上传原理)
- 20.9 [Retrofit vs Volley](#209-retrofit-vs-volley)
- 20.10 [最佳实践](#2010-最佳实践)

---

## 第一篇：OkHttp - Square 出品的网络请求库

---

## 第 1 章 OkHttp 概述

### 1.1 什么是 OkHttp？

**OkHttp** 是 Square 公司开源的 Android/Java HTTP 客户端，是目前 Android 开发中使用最广泛的网络请求库。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OkHttp 核心特性                                      │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │    OkHttp    │
                         └──────┬───────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  高性能       │      │  拦截器       │      │  连接管理     │
│               │      │               │      │               │
│ - HTTP/2      │      │ - 应用拦截器  │      │ - 连接池      │
│ - SPDY        │      │ - 网络拦截器  │      │ - 连接复用    │
│ - GZIP        │      │ - 自定义拦截器│      │ - 超时控制    │
│ - 缓存        │      │               │      │               │
└───────────────┘      └───────────────┘      └───────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  安全性       │      │  易用性       │      │  扩展性       │
│               │      │               │      │               │
│ - HTTPS       │      │ - 流式 API    │      │ - WebSocket   │
│ - 证书绑定    │      │ - 异步请求    │      │ - Cookie      │
│ - TLS         │      │ - 请求重试    │      │ - 自定义 DNS  │
└───────────────┘      └───────────────┘      └───────────────┘
```

### 1.2 核心优势

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OkHttp 核心优势                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────────────────┐
│       优势        │                          说明                            │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 连接池复用        │ 多个请求共享同一个连接，减少握手时间                      │
│ GZIP 压缩        │ 自动压缩请求和响应，节省流量                              │
│ 响应缓存        │ 避免重复请求网络，提升响应速度                            │
│ 拦截器机制        │ 灵活扩展功能（日志、缓存、认证等）                        │
│ HTTP/2 支持      │ 多路复用，提升并发性能                                    │
│ WebSocket        │ 支持 WebSocket 长连接                                     │
│ 自动重试        │ 网络异常自动重试                                          │
│ HTTPS 支持       │ 内置 TLS，支持证书绑定                                    │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

### 1.3 添加依赖

```gradle
dependencies {
    // OkHttp 核心库
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    
    // OkHttp 日志拦截器
    implementation 'com.squareup.okhttp3:logging-interceptor:4.12.0'
}
```

### 1.4 权限配置

```xml
<!-- 网络权限 -->
<uses-permission android:name="android.permission.INTERNET" />

<!-- 网络状态权限（可选） -->
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

---

## 第 2 章 OkHttp 基本使用

### 2.1 创建 OkHttpClient

```java
// 方式1: 使用默认配置
OkHttpClient client = new OkHttpClient();

// 方式2: 自定义配置
OkHttpClient client = new OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)     // 连接超时
    .readTimeout(30, TimeUnit.SECONDS)        // 读取超时
    .writeTimeout(30, TimeUnit.SECONDS)       // 写入超时
    .retryOnConnectionFailure(true)           // 失败重试
    .cache(new Cache(cacheDir, 10 * 1024 * 1024)) // 缓存
    .build();
```

### 2.2 同步请求

```java
public void syncRequest() throws IOException {
    // 1. 创建 Request
    Request request = new Request.Builder()
        .url("https://api.example.com/data")
        .build();
    
    // 2. 创建 Call
    Call call = client.newCall(request);
    
    // 3. 执行同步请求（会阻塞当前线程）
    try (Response response = call.execute()) {
        if (response.isSuccessful()) {
            String responseData = response.body().string();
            Log.d("OkHttp", "Response: " + responseData);
        }
    }
}

// ⚠️ 注意：同步请求不能在主线程执行！
new Thread(() -> {
    try {
        syncRequest();
    } catch (IOException e) {
        e.printStackTrace();
    }
}).start();
```

### 2.3 异步请求

```java
public void asyncRequest() {
    // 1. 创建 Request
    Request request = new Request.Builder()
        .url("https://api.example.com/data")
        .build();
    
    // 2. 创建 Call
    Call call = client.newCall(request);
    
    // 3. 执行异步请求
    call.enqueue(new Callback() {
        @Override
        public void onFailure(Call call, IOException e) {
            // 请求失败（在子线程）
            e.printStackTrace();
        }
        
        @Override
        public void onResponse(Call call, Response response) throws IOException {
            // 请求成功（在子线程）
            if (response.isSuccessful()) {
                String responseData = response.body().string();
                
                // 切换到主线程更新 UI
                runOnUiThread(() -> {
                    textView.setText(responseData);
                });
            }
        }
    });
}
```

### 2.4 GET 请求

```java
// 基础 GET 请求
public void getRequest() {
    Request request = new Request.Builder()
        .url("https://api.example.com/users")
        .build();
    
    client.newCall(request).enqueue(callback);
}

// 带参数的 GET 请求
public void getWithParams() {
    // 方式1: 拼接 URL
    String url = "https://api.example.com/users?page=1&size=20";
    
    // 方式2: 使用 HttpUrl.Builder
    HttpUrl httpUrl = HttpUrl.parse("https://api.example.com/users")
        .newBuilder()
        .addQueryParameter("page", "1")
        .addQueryParameter("size", "20")
        .build();
    
    Request request = new Request.Builder()
        .url(httpUrl)
        .build();
    
    client.newCall(request).enqueue(callback);
}

// 带 Header 的 GET 请求
public void getWithHeaders() {
    Request request = new Request.Builder()
        .url("https://api.example.com/users")
        .addHeader("Authorization", "Bearer token123")
        .addHeader("Content-Type", "application/json")
        .build();
    
    client.newCall(request).enqueue(callback);
}
```

### 2.5 POST 请求

```java
// 1. POST JSON 数据
public void postJson() {
    String json = "{\"name\":\"张三\",\"age\":25}";
    
    RequestBody body = RequestBody.create(
        json, 
        MediaType.parse("application/json; charset=utf-8")
    );
    
    Request request = new Request.Builder()
        .url("https://api.example.com/users")
        .post(body)
        .build();
    
    client.newCall(request).enqueue(callback);
}

// 2. POST 表单数据
public void postForm() {
    RequestBody formBody = new FormBody.Builder()
        .add("username", "admin")
        .add("password", "123456")
        .build();
    
    Request request = new Request.Builder()
        .url("https://api.example.com/login")
        .post(formBody)
        .build();
    
    client.newCall(request).enqueue(callback);
}

// 3. POST Multipart（文件+参数）
public void postMultipart() {
    File file = new File("/sdcard/image.jpg");
    
    RequestBody requestBody = new MultipartBody.Builder()
        .setType(MultipartBody.FORM)
        .addFormDataPart("username", "张三")
        .addFormDataPart("avatar", "image.jpg",
            RequestBody.create(file, MediaType.parse("image/jpeg")))
        .build();
    
    Request request = new Request.Builder()
        .url("https://api.example.com/upload")
        .post(requestBody)
        .build();
    
    client.newCall(request).enqueue(callback);
}
```

### 2.6 文件上传

```java
// 1. 上传单个文件
public void uploadFile() {
    File file = new File("/sdcard/test.jpg");
    
    RequestBody fileBody = RequestBody.create(
        file, 
        MediaType.parse("image/jpeg")
    );
    
    Request request = new Request.Builder()
        .url("https://api.example.com/upload")
        .post(fileBody)
        .build();
    
    client.newCall(request).enqueue(callback);
}

// 2. 带进度的文件上传
public void uploadWithProgress() {
    File file = new File("/sdcard/test.zip");
    
    RequestBody requestBody = new RequestBody() {
        @Override
        public MediaType contentType() {
            return MediaType.parse("application/octet-stream");
        }
        
        @Override
        public void writeTo(BufferedSink sink) throws IOException {
            Source source = null;
            try {
                source = Okio.source(file);
                Buffer buffer = new Buffer();
                long total = file.length();
                long uploaded = 0;
                
                for (long read; (read = source.read(buffer, 8192)) != -1; ) {
                    sink.write(buffer, read);
                    uploaded += read;
                    
                    // 更新进度
                    int progress = (int) (uploaded * 100 / total);
                    runOnUiThread(() -> {
                        progressBar.setProgress(progress);
                    });
                }
            } finally {
                if (source != null) {
                    source.close();
                }
            }
        }
    };
    
    Request request = new Request.Builder()
        .url("https://api.example.com/upload")
        .post(requestBody)
        .build();
    
    client.newCall(request).enqueue(callback);
}
```

### 2.7 文件下载

```java
// 1. 基础文件下载
public void downloadFile() {
    Request request = new Request.Builder()
        .url("https://example.com/file.zip")
        .build();
    
    client.newCall(request).enqueue(new Callback() {
        @Override
        public void onFailure(Call call, IOException e) {
            e.printStackTrace();
        }
        
        @Override
        public void onResponse(Call call, Response response) throws IOException {
            if (response.isSuccessful()) {
                InputStream inputStream = response.body().byteStream();
                FileOutputStream fos = new FileOutputStream("/sdcard/file.zip");
                
                byte[] buffer = new byte[2048];
                int len;
                while ((len = inputStream.read(buffer)) != -1) {
                    fos.write(buffer, 0, len);
                }
                
                fos.flush();
                fos.close();
                inputStream.close();
            }
        }
    });
}

// 2. 带进度的文件下载
public void downloadWithProgress() {
    Request request = new Request.Builder()
        .url("https://example.com/file.zip")
        .build();
    
    client.newCall(request).enqueue(new Callback() {
        @Override
        public void onResponse(Call call, Response response) throws IOException {
            if (response.isSuccessful()) {
                long contentLength = response.body().contentLength();
                InputStream inputStream = response.body().byteStream();
                FileOutputStream fos = new FileOutputStream("/sdcard/file.zip");
                
                byte[] buffer = new byte[2048];
                int len;
                long downloaded = 0;
                
                while ((len = inputStream.read(buffer)) != -1) {
                    fos.write(buffer, 0, len);
                    downloaded += len;
                    
                    // 更新进度
                    int progress = (int) (downloaded * 100 / contentLength);
                    runOnUiThread(() -> {
                        progressBar.setProgress(progress);
                    });
                }
                
                fos.flush();
                fos.close();
                inputStream.close();
            }
        }
        
        @Override
        public void onFailure(Call call, IOException e) {
            e.printStackTrace();
        }
    });
}
```

---

## 第 3 章 OkHttp 拦截器

### 3.1 拦截器概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OkHttp 拦截器链                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌───────────────────────────────────────────────────────────────────────┐
  │                        应用拦截器 (Application Interceptors)           │
  │  - 不关心中间的响应（如缓存、重定向）                                  │
  │  - 总是只调用一次                                                      │
  │  - 可以监控整个请求过程                                                │
  └───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │                        OkHttp 核心                                    │
  │  - RetryAndFollowUpInterceptor (重试和重定向)                         │
  │  - BridgeInterceptor (桥接拦截器)                                    │
  │  - CacheInterceptor (缓存拦截器)                                     │
  │  - ConnectInterceptor (连接拦截器)                                   │
  └───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │                        网络拦截器 (Network Interceptors)               │
  │  - 可以访问中间响应（如缓存响应、重定向响应）                          │
  │  - 可以观察网络请求的完整过程                                          │
  │  - 可以访问 Connection                                                │
  └───────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌───────────────────────────────────────────────────────────────────────┐
  │                        CallServerInterceptor                          │
  │  - 真正执行网络请求                                                    │
  └───────────────────────────────────────────────────────────────────────┘
```

### 3.2 应用拦截器

```java
public class LoggingInterceptor implements Interceptor {
    
    @Override
    public Response intercept(Chain chain) throws IOException {
        // 1. 获取请求
        Request request = chain.request();
        
        long startTime = System.nanoTime();
        Log.d("OkHttp", String.format("Sending request %s on %s%n%s",
            request.url(), chain.connection(), request.headers()));
        
        // 2. 执行请求
        Response response = chain.proceed(request);
        
        long endTime = System.nanoTime();
        Log.d("OkHttp", String.format("Received response for %s in %.1fms%n%s",
            response.request().url(), (endTime - startTime) / 1e6d, response.headers()));
        
        return response;
    }
}

// 使用应用拦截器
OkHttpClient client = new OkHttpClient.Builder()
    .addInterceptor(new LoggingInterceptor())
    .build();
```

### 3.3 网络拦截器

```java
public class NetworkInterceptor implements Interceptor {
    
    @Override
    public Response intercept(Chain chain) throws IOException {
        Request request = chain.request();
        
        // 可以访问 Connection
        Connection connection = chain.connection();
        
        // 执行请求
        Response response = chain.proceed(request);
        
        // 可以看到缓存响应头
        Log.d("OkHttp", "Cache response: " + response.cacheResponse());
        Log.d("OkHttp", "Network response: " + response.networkResponse());
        
        return response;
    }
}

// 使用网络拦截器
OkHttpClient client = new OkHttpClient.Builder()
    .addNetworkInterceptor(new NetworkInterceptor())
    .build();
```

**应用拦截器 vs 网络拦截器对比：**

```
┌──────────────────┬──────────────────┬──────────────────┐
│       特性        │   应用拦截器     │   网络拦截器     │
├──────────────────┼──────────────────┼──────────────────┤
│ 调用次数          │      1 次        │     可能多次     │
│ 缓存响应          │      不关心      │       可见       │
│ 重定向响应        │      不关心      │       可见       │
│ Connection       │      不可访问    │       可访问     │
│ 适用场景          │   日志、统计     │   缓存、重试     │
└──────────────────┴──────────────────┴──────────────────┘
```

### 3.4 日志拦截器

```java
// 使用官方日志拦截器
HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
loggingInterceptor.setLevel(HttpLoggingInterceptor.Level.BODY);

OkHttpClient client = new OkHttpClient.Builder()
    .addInterceptor(loggingInterceptor)
    .build();

// 日志级别：
// - NONE: 不记录日志
// - BASIC: 请求/响应行
// - HEADERS: 请求/响应行 + 头
// - BODY: 请求/响应行 + 头 + 体
```

### 3.5 缓存拦截器

```java
public class CacheInterceptor implements Interceptor {
    
    @Override
    public Response intercept(Chain chain) throws IOException {
        Request request = chain.request();
        
        // 无网络时，强制使用缓存
        if (!isNetworkAvailable()) {
            request = request.newBuilder()
                .cacheControl(CacheControl.FORCE_CACHE)
                .build();
        }
        
        Response response = chain.proceed(request);
        
        if (isNetworkAvailable()) {
            // 有网络时，缓存有效期为 1 小时
            int maxAge = 60 * 60;
            response.newBuilder()
                .removeHeader("Pragma")
                .header("Cache-Control", "public, max-age=" + maxAge)
                .build();
        } else {
            // 无网络时，缓存有效期为 1 周
            int maxStale = 60 * 60 * 24 * 7;
            response.newBuilder()
                .removeHeader("Pragma")
                .header("Cache-Control", "public, only-if-cached, max-stale=" + maxStale)
                .build();
        }
        
        return response;
    }
}
```

### 3.6 头部拦截器

```java
public class HeaderInterceptor implements Interceptor {
    
    @Override
    public Response intercept(Chain chain) throws IOException {
        Request originalRequest = chain.request();
        
        // 添加通用请求头
        Request request = originalRequest.newBuilder()
            .addHeader("Content-Type", "application/json")
            .addHeader("Accept", "application/json")
            .addHeader("User-Agent", "Android App")
            .addHeader("Authorization", "Bearer " + getToken())
            .build();
        
        return chain.proceed(request);
    }
}
```

---

## 第 4 章 OkHttp 缓存机制

### 4.1 缓存策略

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OkHttp 缓存策略                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────────────────┐
│       策略        │                          说明                            │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ FORCE_NETWORK    │ 强制使用网络，不使用缓存                                │
│ FORCE_CACHE      │ 强制使用缓存，不使用网络                                │
│ maxAge           │ 缓存最大有效期（秒）                                    │
│ maxStale         │ 缓存过期后仍可使用的时间（秒）                          │
│ only-if-cached   │ 只使用缓存，如果缓存不存在则返回 504                   │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

### 4.2 缓存配置

```java
// 1. 创建缓存目录
File cacheDir = new File(getCacheDir(), "okhttp_cache");

// 2. 创建缓存对象（最大 10MB）
Cache cache = new Cache(cacheDir, 10 * 1024 * 1024);

// 3. 配置 OkHttpClient
OkHttpClient client = new OkHttpClient.Builder()
    .cache(cache)
    .build();

// 4. 使用缓存
Request request = new Request.Builder()
    .url("https://api.example.com/data")
    .cacheControl(new CacheControl.Builder()
        .maxAge(5, TimeUnit.MINUTES)  // 缓存 5 分钟
        .build())
    .build();
```

### 4.3 强制刷新

```java
// 方式1: 使用 CacheControl
Request request = new Request.Builder()
    .url("https://api.example.com/data")
    .cacheControl(CacheControl.FORCE_NETWORK)
    .build();

// 方式2: 使用 cacheControl() 方法
Request request = new Request.Builder()
    .url("https://api.example.com/data")
    .cacheControl(new CacheControl.Builder()
        .noCache()  // 不使用缓存
        .build())
    .build();
```

### 4.4 离线缓存

```java
public Response getWithOfflineCache(String url) throws IOException {
    Request.Builder requestBuilder = new Request.Builder().url(url);
    
    if (!isNetworkAvailable()) {
        // 无网络时，强制使用缓存
        requestBuilder.cacheControl(CacheControl.FORCE_CACHE);
    }
    
    Request request = requestBuilder.build();
    Response response = client.newCall(request).execute();
    
    if (response.code() == 504) {
        // 缓存不存在，返回错误
        return null;
    }
    
    return response;
}

// 检查网络是否可用
private boolean isNetworkAvailable() {
    ConnectivityManager cm = (ConnectivityManager) 
        getSystemService(Context.CONNECTIVITY_SERVICE);
    NetworkInfo activeNetwork = cm.getActiveNetworkInfo();
    return activeNetwork != null && activeNetwork.isConnectedOrConnecting();
}
```

---

## 第 5 章 OkHttp 连接管理

### 5.1 连接池

```java
// OkHttp 默认配置
// - 最大空闲连接数: 5
// - 空闲连接保活时间: 5 分钟

// 自定义连接池
ConnectionPool connectionPool = new ConnectionPool(
    10,     // 最大空闲连接数
    5,      // 保活时间
    TimeUnit.MINUTES
);

OkHttpClient client = new OkHttpClient.Builder()
    .connectionPool(connectionPool)
    .build();
```

### 5.2 连接复用

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OkHttp 连接复用原理                                  │
└─────────────────────────────────────────────────────────────────────────────┘

请求1 ──► 建立 TCP 连接 ──► 发送请求 ──► 接收响应 ──► 连接放入连接池
                                                              │
请求2 ──► 从连接池获取连接 ──► 发送请求 ──► 接收响应 ──► 连接放回连接池
                                                              │
请求3 ──► 从连接池获取连接 ──► 发送请求 ──► 接收响应 ──► 连接放回连接池

优势：
- 避免重复的 TCP 握手
- 减少 TLS 握手开销
- 提升请求速度
```

### 5.3 连接超时

```java
OkHttpClient client = new OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)     // 连接超时
    .readTimeout(30, TimeUnit.SECONDS)        // 读取超时
    .writeTimeout(30, TimeUnit.SECONDS)       // 写入超时
    .callTimeout(60, TimeUnit.SECONDS)        // 整个请求超时
    .build();
```

### 5.4 DNS 解析

```java
// 自定义 DNS
public class CustomDns implements Dns {
    
    @Override
    public List<InetAddress> lookup(String hostname) throws UnknownHostException {
        try {
            // 优先使用自定义 DNS
            return Arrays.asList(InetAddress.getAllByName(hostname));
        } catch (UnknownHostException e) {
            // 失败时使用系统 DNS
            return Dns.SYSTEM.lookup(hostname);
        }
    }
}

OkHttpClient client = new OkHttpClient.Builder()
    .dns(new CustomDns())
    .build();
```

---

## 第 6 章 OkHttp 高级功能

### 6.1 WebSocket

```java
// 1. 创建 WebSocket 监听器
WebSocketListener webSocketListener = new WebSocketListener() {
    
    @Override
    public void onOpen(WebSocket webSocket, Response response) {
        Log.d("WebSocket", "连接已建立");
    }
    
    @Override
    public void onMessage(WebSocket webSocket, String text) {
        Log.d("WebSocket", "收到消息: " + text);
    }
    
    @Override
    public void onMessage(WebSocket webSocket, ByteString bytes) {
        Log.d("WebSocket", "收到二进制消息");
    }
    
    @Override
    public void onClosing(WebSocket webSocket, int code, String reason) {
        Log.d("WebSocket", "连接正在关闭");
        webSocket.close(1000, null);
    }
    
    @Override
    public void onClosed(WebSocket webSocket, int code, String reason) {
        Log.d("WebSocket", "连接已关闭");
    }
    
    @Override
    public void onFailure(WebSocket webSocket, Throwable t, Response response) {
        Log.e("WebSocket", "连接失败", t);
    }
};

// 2. 创建 WebSocket
Request request = new Request.Builder()
    .url("wss://echo.websocket.org")
    .build();

WebSocket webSocket = client.newWebSocket(request, webSocketListener);

// 3. 发送消息
webSocket.send("Hello WebSocket!");

// 4. 关闭连接
webSocket.close(1000, "Closing");
```

### 6.2 HTTPS 配置

```java
// 信任所有证书（仅用于测试！）
public static OkHttpClient getUnsafeOkHttpClient() {
    try {
        // 创建信任所有证书的 TrustManager
        final TrustManager[] trustAllCerts = new TrustManager[] {
            new X509TrustManager() {
                @Override
                public void checkClientTrusted(X509Certificate[] chain, String authType) {
                }
                
                @Override
                public void checkServerTrusted(X509Certificate[] chain, String authType) {
                }
                
                @Override
                public X509Certificate[] getAcceptedIssuers() {
                    return new X509Certificate[] {};
                }
            }
        };
        
        // 安装信任管理器
        final SSLContext sslContext = SSLContext.getInstance("SSL");
        sslContext.init(null, trustAllCerts, new java.security.SecureRandom());
        
        // 创建 SSL 套接字工厂
        final SSLSocketFactory sslSocketFactory = sslContext.getSocketFactory();
        
        OkHttpClient.Builder builder = new OkHttpClient.Builder();
        builder.sslSocketFactory(sslSocketFactory, (X509TrustManager) trustAllCerts[0]);
        builder.hostnameVerifier((hostname, session) -> true);
        
        return builder.build();
    } catch (Exception e) {
        throw new RuntimeException(e);
    }
}

// ⚠️ 生产环境应该使用证书绑定！
```

### 6.3 证书绑定

```java
// 证书绑定（Certificate Pinning）
OkHttpClient client = new OkHttpClient.Builder()
    .certificatePinner(new CertificatePinner.Builder()
        .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        .add("api.example.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")
        .build())
    .build();
```

### 6.4 Cookie 管理

```java
// 1. 创建 CookieJar
public class PersistentCookieJar implements CookieJar {
    
    private Map<String, List<Cookie>> cookieStore = new HashMap<>();
    
    @Override
    public void saveFromResponse(HttpUrl url, List<Cookie> cookies) {
        cookieStore.put(url.host(), cookies);
    }
    
    @Override
    public List<Cookie> loadForRequest(HttpUrl url) {
        List<Cookie> cookies = cookieStore.get(url.host());
        return cookies != null ? cookies : new ArrayList<>();
    }
}

// 2. 使用 CookieJar
OkHttpClient client = new OkHttpClient.Builder()
    .cookieJar(new PersistentCookieJar())
    .build();
```

### 6.5 请求重试

```java
// 自定义重试拦截器
public class RetryInterceptor implements Interceptor {
    
    private int maxRetryCount = 3;  // 最大重试次数
    private int retryCount = 0;
    
    @Override
    public Response intercept(Chain chain) throws IOException {
        Request request = chain.request();
        Response response = null;
        IOException exception = null;
        
        while (retryCount < maxRetryCount) {
            try {
                response = chain.proceed(request);
                if (response.isSuccessful()) {
                    return response;
                }
            } catch (IOException e) {
                exception = e;
            } finally {
                retryCount++;
            }
        }
        
        if (exception != null) {
            throw exception;
        }
        
        return response;
    }
}

// 使用重试拦截器
OkHttpClient client = new OkHttpClient.Builder()
    .addInterceptor(new RetryInterceptor())
    .build();
```

---

## 第 7 章 OkHttp 核心原理

### 7.1 请求流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OkHttp 请求流程                                      │
└─────────────────────────────────────────────────────────────────────────────┘

1. 创建 Request
        │
        ▼
2. 创建 Call (RealCall)
        │
        ▼
3. 执行请求 (execute/enqueue)
        │
        ▼
4. Dispatcher 调度请求
        │
        ▼
5. 拦截器链执行
   ├─► RetryAndFollowUpInterceptor (重试和重定向)
   ├─► BridgeInterceptor (桥接拦截器)
   ├─► CacheInterceptor (缓存拦截器)
   ├─► ConnectInterceptor (连接拦截器)
   └─► CallServerInterceptor (网络请求)
        │
        ▼
6. 返回 Response
```

### 7.2 拦截器链

```java
/**
 * 拦截器链采用责任链模式
 * 
 * 每个拦截器都有三个职责：
 * 1. 对请求进行预处理
 * 2. 调用 chain.proceed() 将请求传递给下一个拦截器
 * 3. 对响应进行后处理
 */

public class RealInterceptorChain implements Interceptor.Chain {
    
    private final List<Interceptor> interceptors;
    private final int index;
    private final Request request;
    
    @Override
    public Response proceed(Request request) throws IOException {
        // 调用下一个拦截器
        Interceptor interceptor = interceptors.get(index);
        RealInterceptorChain next = new RealInterceptorChain(
            interceptors, index + 1, request
        );
        
        return interceptor.intercept(next);
    }
}
```

### 7.3 连接池原理

```java
/**
 * ConnectionPool 核心逻辑
 */

public final class ConnectionPool {
    
    // 最大空闲连接数
    private final int maxIdleConnections;
    
    // 保活时间
    private final long keepAliveDurationNs;
    
    // 连接队列
    private final ArrayDeque<RealConnection> connections = new ArrayDeque<>();
    
    // 获取连接
    RealConnection get(Address address) {
        // 1. 遍历连接池
        for (RealConnection connection : connections) {
            // 2. 检查连接是否可用
            if (connection.isEligible(address)) {
                return connection;
            }
        }
        return null;
    }
    
    // 放入连接
    void put(RealConnection connection) {
        connections.add(connection);
    }
}
```

### 7.4 缓存原理

```java
/**
 * CacheInterceptor 缓存逻辑
 */

public final class CacheInterceptor implements Interceptor {
    
    @Override
    public Response intercept(Chain chain) throws IOException {
        // 1. 尝试从缓存获取
        Response cacheCandidate = cache != null 
            ? cache.get(chain.request()) 
            : null;
        
        // 2. 判断缓存策略
        CacheStrategy strategy = new CacheStrategy.Factory(
            now, chain.request(), cacheCandidate
        ).get();
        
        Request networkRequest = strategy.networkRequest;
        Response cacheResponse = strategy.cacheResponse;
        
        // 3. 如果不使用网络，直接返回缓存
        if (networkRequest == null) {
            return cacheResponse;
        }
        
        // 4. 执行网络请求
        Response networkResponse = chain.proceed(networkRequest);
        
        // 5. 写入缓存
        if (cache != null) {
            cache.put(networkResponse);
        }
        
        return networkResponse;
    }
}
```

---

## 第 8 章 OkHttp 源码解析

### 8.1 OkHttpClient 创建

```java
public OkHttpClient() {
    this(new Builder());
}

public OkHttpClient(Builder builder) {
    this.dispatcher = builder.dispatcher;
    this.proxy = builder.proxy;
    this.protocols = builder.protocols;
    this.connectionSpecs = builder.connectionSpecs;
    this.interceptors = Util.immutableList(builder.interceptors);
    this.networkInterceptors = Util.immutableList(builder.networkInterceptors);
    this.eventListenerFactory = builder.eventListenerFactory;
    this.proxySelector = builder.proxySelector;
    this.cookieJar = builder.cookieJar;
    this.cache = builder.cache;
    this.internalCache = builder.internalCache;
    this.socketFactory = builder.socketFactory;
    // ... 其他配置
}
```

### 8.2 Call 创建与执行

```java
// 创建 Call
@Override
public Call newCall(Request request) {
    return new RealCall(this, request, false);
}

// RealCall.execute()
@Override
public Response execute() throws IOException {
    synchronized (this) {
        if (executed) throw new IllegalStateException("Already Executed");
        executed = true;
    }
    
    try {
        // 1. 加入调度队列
        client.dispatcher().executed(this);
        
        // 2. 执行拦截器链
        Response result = getResponseWithInterceptorChain();
        
        if (result == null) throw new IOException("Canceled");
        return result;
    } finally {
        // 3. 从调度队列移除
        client.dispatcher().finished(this);
    }
}
```

### 8.3 Dispatcher 调度器

```java
public final class Dispatcher {
    
    // 最大并发请求数
    private int maxRequests = 64;
    
    // 每个主机最大并发请求数
    private int maxRequestsPerHost = 5;
    
    // 异步请求队列
    private final ArrayDeque<AsyncCall> readyAsyncCalls = new ArrayDeque<>();
    private final ArrayDeque<AsyncCall> runningAsyncCalls = new ArrayDeque<>();
    
    // 同步请求队列
    private final ArrayDeque<RealCall> runningSyncCalls = new ArrayDeque<>();
    
    // 异步请求
    synchronized void enqueue(AsyncCall call) {
        // 1. 检查并发限制
        if (runningAsyncCalls.size() < maxRequests 
            && runningCallsForHost(call) < maxRequestsPerHost) {
            // 2. 加入运行队列
            runningAsyncCalls.add(call);
            // 3. 提交到线程池
            executorService().execute(call);
        } else {
            // 4. 加入等待队列
            readyAsyncCalls.add(call);
        }
    }
    
    // 请求完成
    void finished(AsyncCall call) {
        synchronized (this) {
            // 1. 从运行队列移除
            runningAsyncCalls.remove(call);
            
            // 2. 尝试运行等待队列中的请求
            promoteCalls();
        }
    }
}
```

### 8.4 ConnectionPool

```java
public final class ConnectionPool {
    
    // 最大空闲连接数（默认 5）
    private final int maxIdleConnections;
    
    // 保活时间（默认 5 分钟）
    private final long keepAliveDurationNs;
    
    // 清理线程
    private static final Executor executor = new ThreadPoolExecutor(
        0, 1, 60L, TimeUnit.SECONDS, 
        new SynchronousQueue<>(),
        Util.threadFactory("OkHttp ConnectionPool", true)
    );
    
    // 清理任务
    private final Runnable cleanupRunnable = () -> {
        while (true) {
            long waitNanos = cleanup(System.nanoTime());
            if (waitNanos == -1) return;
            try {
                Thread.sleep(waitNanos / 1000000L, (int) (waitNanos % 1000000L));
            } catch (InterruptedException e) {
                return;
            }
        }
    };
    
    // 清理过期连接
    long cleanup(long now) {
        int inUseConnectionCount = 0;
        long maxIdleConnection = Long.MIN_VALUE;
        RealConnection longestIdleConnection = null;
        
        // 遍历所有连接
        synchronized (this) {
            for (Iterator<RealConnection> i = connections.iterator(); i.hasNext(); ) {
                RealConnection connection = i.next();
                
                // 检查是否在使用
                if (pruneAndGetAllocationCount(connection, now) > 0) {
                    inUseConnectionCount++;
                    continue;
                }
                
                // 记录最久未使用的空闲连接
                long idleDurationNs = now - connection.idleAtNanos;
                if (idleDurationNs > maxIdleConnection) {
                    maxIdleConnection = idleDurationNs;
                    longestIdleConnection = connection;
                }
            }
            
            // 清理条件：超过最大空闲数 或 超过保活时间
            if (longestIdleConnection != null
                && (inUseConnectionCount > 0 || idleConnectionCount > maxIdleConnections)
                && maxIdleConnection > keepAliveDurationNs) {
                connections.remove(longestIdleConnection);
                longestIdleConnection.socket().close();
                return 0;
            }
        }
    }
}
```

---

## 第 9 章 OkHttp 性能优化

### 9.1 连接优化

```java
// 1. 使用全局单例
public class OkHttpManager {
    
    private static volatile OkHttpClient instance;
    
    public static OkHttpClient getInstance() {
        if (instance == null) {
            synchronized (OkHttpManager.class) {
                if (instance == null) {
                    instance = new OkHttpClient.Builder()
                        .connectTimeout(30, TimeUnit.SECONDS)
                        .readTimeout(30, TimeUnit.SECONDS)
                        .build();
                }
            }
        }
        return instance;
    }
}

// 2. 自定义连接池
ConnectionPool connectionPool = new ConnectionPool(
    10,     // 增加最大空闲连接数
    10,     // 增加保活时间
    TimeUnit.MINUTES
);

OkHttpClient client = new OkHttpClient.Builder()
    .connectionPool(connectionPool)
    .build();
```

### 9.2 缓存优化

```java
// 1. 配置缓存
File cacheDir = new File(getCacheDir(), "http_cache");
Cache cache = new Cache(cacheDir, 50 * 1024 * 1024); // 50MB

OkHttpClient client = new OkHttpClient.Builder()
    .cache(cache)
    .build();

// 2. 缓存策略
public Response getWithCache(String url) throws IOException {
    Request request = new Request.Builder()
        .url(url)
        .cacheControl(new CacheControl.Builder()
            .maxAge(5, TimeUnit.MINUTES)
            .build())
        .build();
    
    return client.newCall(request).execute();
}
```

### 9.3 请求优化

```java
// 1. 批量请求
public void batchRequests(List<String> urls) {
    List<Call> calls = new ArrayList<>();
    
    for (String url : urls) {
        Request request = new Request.Builder()
            .url(url)
            .build();
        calls.add(client.newCall(request));
    }
    
    // 并发执行
    for (Call call : calls) {
        call.enqueue(callback);
    }
}

// 2. 取消请求
public void cancelAll() {
    client.dispatcher().cancelAll();
}

// 3. 取消特定请求
public void cancelWithTag(Object tag) {
    for (Call call : client.dispatcher().queuedCalls()) {
        if (tag.equals(call.request().tag())) {
            call.cancel();
        }
    }
    
    for (Call call : client.dispatcher().runningCalls()) {
        if (tag.equals(call.request().tag())) {
            call.cancel();
        }
    }
}
```

### 9.4 内存优化

```java
// 1. 及时关闭 ResponseBody
try (Response response = client.newCall(request).execute()) {
    if (response.isSuccessful()) {
        String body = response.body().string();
        // 使用 body
    }
} // 自动关闭

// 2. 大文件使用流式读取
try (Response response = client.newCall(request).execute()) {
    InputStream inputStream = response.body().byteStream();
    // 流式处理，不一次性加载到内存
}

// 3. 限制响应体大小
public Response limitResponseSize(Response response, long maxSize) throws IOException {
    ResponseBody body = response.body();
    if (body.contentLength() > maxSize) {
        response.close();
        throw new IOException("Response too large");
    }
    return response;
}
```

---

## 第 10 章 OkHttp 面试常见问题

### 10.1 拦截器原理

**Q: OkHttp 拦截器的执行顺序是什么？**

**A:**

OkHttp 采用责任链模式，拦截器按顺序执行：

1. **应用拦截器** (Application Interceptors)
2. **RetryAndFollowUpInterceptor** (重试和重定向)
3. **BridgeInterceptor** (桥接拦截器)
4. **CacheInterceptor** (缓存拦截器)
5. **ConnectInterceptor** (连接拦截器)
6. **网络拦截器** (Network Interceptors)
7. **CallServerInterceptor** (网络请求)

每个拦截器都可以：
- 对请求进行预处理
- 调用 `chain.proceed()` 传递给下一个拦截器
- 对响应进行后处理

### 10.2 连接池复用

**Q: OkHttp 如何实现连接池复用？**

**A:**

OkHttp 使用 `ConnectionPool` 管理连接：

1. **连接池配置**：
   - 默认最大空闲连接数：5
   - 默认保活时间：5 分钟

2. **复用流程**：
   - 请求时，从连接池查找可用连接
   - 找到则直接复用，避免 TCP 握手
   - 找不到则创建新连接

3. **清理机制**：
   - 后台线程定期清理过期连接
   - 超过最大空闲数的连接被清理
   - 超过保活时间的连接被清理

### 10.3 缓存策略

**Q: OkHttp 的缓存策略是什么？**

**A:**

OkHttp 支持 HTTP 缓存：

1. **缓存控制**：
   - `Cache-Control: max-age=<seconds>` 缓存有效期
   - `Cache-Control: no-cache` 不使用缓存
   - `Cache-Control: only-if-cached` 只使用缓存

2. **缓存流程**：
   - 请求前检查缓存
   - 缓存有效且未过期，直接返回
   - 缓存过期，发送验证请求 (ETag/Last-Modified)
   - 无缓存，发送网络请求

3. **强制刷新**：
   ```java
   request.cacheControl(CacheControl.FORCE_NETWORK)
   ```

### 10.4 同步 vs 异步

**Q: OkHttp 同步请求和异步请求的区别？**

**A:**

| 对比项 | 同步请求 | 异步请求 |
|--------|---------|---------|
| 执行方式 | 阻塞当前线程 | 不阻塞当前线程 |
| 回调 | 无回调 | 有回调 |
| 线程 | 在调用线程执行 | 在线程池执行 |
| 使用场景 | 后台任务 | 主线程请求 |
| 并发控制 | 手动控制 | Dispatcher 自动控制 |

### 10.5 Dispatcher

**Q: Dispatcher 的作用是什么？**

**A:**

Dispatcher 负责：

1. **请求调度**：
   - 管理同步和异步请求队列
   - 控制并发请求数量

2. **并发限制**：
   - 最大并发请求数：64
   - 每个主机最大并发：5

3. **线程池管理**：
   - 维护线程池执行异步请求
   - 请求完成后自动执行等待队列中的请求

### 10.6 责任链模式

**Q: OkHttp 如何使用责任链模式？**

**A:**

责任链模式在 OkHttp 中的应用：

1. **拦截器链**：
   - 每个拦截器处理一部分逻辑
   - 通过 `chain.proceed()` 传递给下一个

2. **优势**：
   - 解耦：每个拦截器职责单一
   - 灵活：可以动态添加/删除拦截器
   - 扩展性强：易于添加新功能

### 10.7 WebSocket

**Q: OkHttp 如何实现 WebSocket？**

**A:**

```java
WebSocket webSocket = client.newWebSocket(request, listener);

// 发送消息
webSocket.send("Hello");

// 关闭连接
webSocket.close(1000, "Closing");
```

WebSocket 基于 HTTP 协议升级：
1. 发送 HTTP 请求，带上 Upgrade 头
2. 服务器返回 101 Switching Protocols
3. 升级成功，切换为 WebSocket 协议

### 10.8 HTTPS 握手

**Q: OkHttp 如何处理 HTTPS？**

**A:**

1. **TLS 握手**：
   - 客户端发送支持的加密套件
   - 服务器选择加密套件并返回证书
   - 客户端验证证书
   - 协商对称密钥

2. **证书验证**：
   - 验证证书链
   - 检查证书有效期
   - 验证域名匹配

3. **证书绑定**：
   ```java
   .certificatePinner(new CertificatePinner.Builder()
       .add("api.example.com", "sha256/xxx")
       .build())
   ```

### 10.9 OkHttp vs HttpURLConnection

**Q: OkHttp 相比 HttpURLConnection 的优势？**

**A:**

| 对比项 | OkHttp | HttpURLConnection |
|--------|--------|-------------------|
| API 设计 | 现代、易用 | 古老、难用 |
| 连接池 | ✅ 自动管理 | ❌ 需手动管理 |
| 拦截器 | ✅ 强大 | ❌ 无 |
| 缓存 | ✅ 自动 | ⚠️ 需配置 |
| HTTP/2 | ✅ 支持 | ⚠️ 部分支持 |
| WebSocket | ✅ 支持 | ❌ 不支持 |
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

### 10.10 最佳实践

**Q: OkHttp 的最佳实践是什么？**

**A:**

1. **使用单例**：
   ```java
   // 全局只创建一个 OkHttpClient
   OkHttpClient client = OkHttpClientSingleton.getInstance();
   ```

2. **配置超时**：
   ```java
   .connectTimeout(30, TimeUnit.SECONDS)
   .readTimeout(30, TimeUnit.SECONDS)
   ```

3. **使用拦截器**：
   - 日志拦截器
   - 缓存拦截器
   - 头部拦截器

4. **启用缓存**：
   ```java
   .cache(new Cache(cacheDir, 10 * 1024 * 1024))
   ```

5. **及时关闭**：
   ```java
   try (Response response = call.execute()) {
       // 使用 response
   } // 自动关闭
   ```

6. **错误处理**：
   ```java
   call.enqueue(new Callback() {
       @Override
       public void onFailure(Call call, IOException e) {
           // 处理网络错误
       }
       
       @Override
       public void onResponse(Call call, Response response) {
           // 检查响应码
           if (!response.isSuccessful()) {
               // 处理 HTTP 错误
           }
       }
   });
   ```

---

---

## 第二篇：Retrofit - Square 出品的 REST 客户端

---

## 第 11 章 Retrofit 概述

### 11.1 什么是 Retrofit？

**Retrofit** 是 Square 公司开源的 Android/Java REST 客户端，基于 OkHttp，通过注解和动态代理简化网络请求。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Retrofit 核心特性                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │   Retrofit   │
                         └──────┬───────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  注解驱动     │      │  类型安全     │      │  扩展性强     │
│               │      │               │      │               │
│ - @GET/@POST  │      │ - 编译时检查  │      │ - Converter   │
│ - @Body/@Field│      │ - 自动序列化  │      │ - CallAdapter │
│ - @Path/@Query│      │ - 泛型支持    │      │ - 拦截器      │
└───────────────┘      └───────────────┘      └───────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  协程支持     │      │  RxJava 支持  │      │  OkHttp 集成  │
│               │      │               │      │               │
│ - suspend     │      │ - Observable  │      │ - 拦截器      │
│ - Flow        │      │ - Single      │      │ - 缓存        │
│ - 异常处理    │      │ - Completable │      │ - Cookie      │
└───────────────┘      └───────────────┘      └───────────────┘
```

### 11.2 核心优势

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Retrofit 核心优势                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────────────────┐
│       优势        │                          说明                            │
├──────────────────┼──────────────────────────────────────────────────────────┤
│ 简洁的 API        │ 通过注解定义接口，代码简洁易读                          │
│ 类型安全          │ 编译时检查参数类型，减少运行时错误                      │
│ 自动序列化        │ 支持 JSON/XML/ProtoBuf 等多种格式                      │
│ 灵活的适配器      │ 支持 Call/RxJava/Coroutines 等多种返回类型             │
│ 与 OkHttp 无缝集成│ 共享 OkHttp 的所有特性（缓存、拦截器等）                │
│ 动态代理          │ 运行时动态生成接口实现                                  │
│ 异步支持          │ 支持协程和 RxJava，简化异步编程                         │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

### 11.3 添加依赖

```gradle
dependencies {
    // Retrofit 核心库
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    
    // Gson 转换器
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    
    // RxJava 适配器（可选）
    implementation 'com.squareup.retrofit2:adapter-rxjava3:2.9.0'
    
    // Moshi 转换器（可选）
    implementation 'com.squareup.retrofit2:converter-moshi:2.9.0'
    
    // Jackson 转换器（可选）
    implementation 'com.squareup.retrofit2:converter-jackson:2.9.0'
    
    // ProtoBuf 转换器（可选）
    implementation 'com.squareup.retrofit2:converter-protobuf:2.9.0'
}
```

### 11.4 与 OkHttp 关系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Retrofit 与 OkHttp 关系                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   应用层                                                                     │
│   ┌───────────────────────────────────────────────────────────────────┐   │
│   │  Retrofit                                                          │   │
│   │  - 注解定义接口                                                    │   │
│   │  - 动态代理                                                        │   │
│   │  - 数据转换（Converter）                                           │   │
│   │  - 适配器（CallAdapter）                                           │   │
│   └───────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌───────────────────────────────────────────────────────────────────┐   │
│   │  OkHttp                                                            │   │
│   │  - 网络请求执行                                                    │   │
│   │  - 拦截器链                                                        │   │
│   │  - 连接池                                                          │   │
│   │  - 缓存                                                            │   │
│   └───────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Retrofit 是 OkHttp 的上层封装，简化 API 调用                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 第 12 章 Retrofit 基本使用

### 12.1 创建 Retrofit 实例

```java
// 方式1: 基础配置
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.example.com/")  // 基础 URL
    .addConverterFactory(GsonConverterFactory.create())  // JSON 转换器
    .build();

// 方式2: 自定义 OkHttpClient
OkHttpClient okHttpClient = new OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .addInterceptor(new HttpLoggingInterceptor())
    .build();

Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient)  // 自定义 OkHttp
    .addConverterFactory(GsonConverterFactory.create())
    .build();

// 方式3: 单例模式
public class RetrofitManager {
    
    private static volatile Retrofit instance;
    
    public static Retrofit getInstance() {
        if (instance == null) {
            synchronized (RetrofitManager.class) {
                if (instance == null) {
                    instance = new Retrofit.Builder()
                        .baseUrl("https://api.example.com/")
                        .addConverterFactory(GsonConverterFactory.create())
                        .build();
                }
            }
        }
        return instance;
    }
}
```

### 12.2 定义 API 接口

```java
// 定义 API 接口
public interface ApiService {
    
    // GET 请求
    @GET("users")
    Call<List<User>> getUsers();
    
    // 带路径参数
    @GET("users/{id}")
    Call<User> getUser(@Path("id") int userId);
    
    // 带查询参数
    @GET("users")
    Call<List<User>> getUsers(
        @Query("page") int page,
        @Query("size") int size
    );
    
    // POST 请求
    @POST("users")
    Call<User> createUser(@Body User user);
    
    // PUT 请求
    @PUT("users/{id}")
    Call<User> updateUser(@Path("id") int userId, @Body User user);
    
    // DELETE 请求
    @DELETE("users/{id}")
    Call<Void> deleteUser(@Path("id") int userId);
}
```

### 12.3 GET 请求

```java
// 1. 创建 API 接口实例
ApiService apiService = retrofit.create(ApiService.class);

// 2. 创建 Call 对象
Call<List<User>> call = apiService.getUsers();

// 3. 异步请求
call.enqueue(new Callback<List<User>>() {
    @Override
    public void onResponse(Call<List<User>> call, Response<List<User>> response) {
        if (response.isSuccessful()) {
            List<User> users = response.body();
            // 处理数据
        } else {
            // 处理错误
        }
    }
    
    @Override
    public void onFailure(Call<List<User>> call, Throwable t) {
        // 网络错误
    }
});

// 4. 同步请求（在子线程）
new Thread(() -> {
    try {
        Response<List<User>> response = call.execute();
        if (response.isSuccessful()) {
            List<User> users = response.body();
        }
    } catch (IOException e) {
        e.printStackTrace();
    }
}).start();

// 5. 取消请求
call.cancel();
```

**带参数的 GET 请求：**

```java
// 方式1: 使用 @Query
@GET("users")
Call<List<User>> getUsers(
    @Query("page") int page,
    @Query("size") int size,
    @Query("sort") String sort
);

// 调用
apiService.getUsers(1, 20, "name");

// 生成的 URL: /users?page=1&size=20&sort=name

// 方式2: 使用 @QueryMap
@GET("users")
Call<List<User>> getUsers(@QueryMap Map<String, String> params);

// 调用
Map<String, String> params = new HashMap<>();
params.put("page", "1");
params.put("size", "20");
apiService.getUsers(params);

// 方式3: 使用 @Path
@GET("users/{id}/posts/{postId}")
Call<Post> getUserPost(
    @Path("id") int userId,
    @Path("postId") int postId
);

// 调用
apiService.getUserPost(123, 456);

// 生成的 URL: /users/123/posts/456
```

### 12.4 POST 请求

```java
// 1. POST JSON 数据
@POST("users")
Call<User> createUser(@Body User user);

// 调用
User user = new User("张三", 25);
Call<User> call = apiService.createUser(user);

// 2. POST 表单数据
@FormUrlEncoded
@POST("login")
Call<User> login(
    @Field("username") String username,
    @Field("password") String password
);

// 调用
apiService.login("admin", "123456");

// 3. POST 表单数据（Map）
@FormUrlEncoded
@POST("register")
Call<User> register(@FieldMap Map<String, String> fields);

// 调用
Map<String, String> fields = new HashMap<>();
fields.put("username", "张三");
fields.put("email", "zhangsan@example.com");
apiService.register(fields);

// 4. POST 多部分数据（文件上传）
@Multipart
@POST("upload")
Call<ResponseBody> uploadFile(
    @Part("description") RequestBody description,
    @Part MultipartBody.Part file
);

// 调用
File file = new File("/sdcard/image.jpg");
RequestBody requestFile = RequestBody.create(
    file, 
    MediaType.parse("image/jpeg")
);
MultipartBody.Part body = MultipartBody.Part.createFormData(
    "file", 
    file.getName(), 
    requestFile
);
RequestBody description = RequestBody.create(
    "这是图片描述", 
    MediaType.parse("text/plain")
);
apiService.uploadFile(description, body);
```

### 12.5 PUT 请求

```java
// PUT 更新资源
@PUT("users/{id}")
Call<User> updateUser(
    @Path("id") int userId,
    @Body User user
);

// 调用
User user = new User("李四", 30);
apiService.updateUser(123, user);

// PUT 表单
@FormUrlEncoded
@PUT("users/{id}")
Call<User> updateUser(
    @Path("id") int userId,
    @Field("name") String name,
    @Field("age") int age
);

// 调用
apiService.updateUser(123, "李四", 30);
```

### 12.6 DELETE 请求

```java
// DELETE 删除资源
@DELETE("users/{id}")
Call<Void> deleteUser(@Path("id") int userId);

// 调用
apiService.deleteUser(123);

// DELETE 带请求体
@HTTP(method = "DELETE", path = "users", hasBody = true)
Call<Void> deleteUsers(@Body List<Integer> userIds);

// 调用
apiService.deleteUsers(Arrays.asList(1, 2, 3));
```

---

## 第 13 章 Retrofit 注解详解

### 13.1 请求方法注解

```java
// 标准请求方法
@GET("users")        // GET 请求
@POST("users")       // POST 请求
@PUT("users")        // PUT 请求
@DELETE("users")     // DELETE 请求
@PATCH("users")      // PATCH 请求
@HEAD("users")       // HEAD 请求
@OPTIONS("users")    // OPTIONS 请求

// 自定义请求方法
@HTTP(method = "CUSTOM", path = "users")
Call<User> customRequest();

// 自定义请求方法（带请求体）
@HTTP(method = "CUSTOM", path = "users", hasBody = true)
Call<User> customRequestWithBody(@Body User user);
```

### 13.2 请求头注解

```java
// 方式1: 静态头部
@GET("users")
@Headers({
    "Accept: application/json",
    "Content-Type: application/json"
})
Call<List<User>> getUsers();

// 方式2: 动态头部
@GET("users")
Call<List<User>> getUsers(@Header("Authorization") String token);

// 方式3: 头部 Map
@GET("users")
Call<List<User>> getUsers(@HeaderMap Map<String, String> headers);

// 调用
Map<String, String> headers = new HashMap<>();
headers.put("Authorization", "Bearer token123");
headers.put("User-Agent", "Android App");
apiService.getUsers(headers);
```

### 13.3 请求参数注解

```java
// 1. @Query - 查询参数
@GET("users")
Call<List<User>> getUsers(
    @Query("page") int page,
    @Query("size") int size,
    @Query("status") String status
);

// 2. @QueryMap - 查询参数 Map
@GET("users")
Call<List<User>> getUsers(@QueryMap Map<String, String> params);

// 3. @Path - 路径参数
@GET("users/{id}/posts/{postId}")
Call<Post> getPost(
    @Path("id") int userId,
    @Path("postId") int postId
);

// 4. @Field - 表单字段
@FormUrlEncoded
@POST("login")
Call<User> login(
    @Field("username") String username,
    @Field("password") String password
);

// 5. @FieldMap - 表单字段 Map
@FormUrlEncoded
@POST("register")
Call<User> register(@FieldMap Map<String, String> fields);

// 6. @Body - 请求体
@POST("users")
Call<User> createUser(@Body User user);

// 7. @Part - 多部分
@Multipart
@POST("upload")
Call<ResponseBody> upload(
    @Part("description") RequestBody description,
    @Part MultipartBody.Part file
);

// 8. @PartMap - 多部分 Map
@Multipart
@POST("upload")
Call<ResponseBody> upload(
    @PartMap Map<String, RequestBody> params,
    @Part MultipartBody.Part file
);
```

### 13.4 请求体注解

```java
// 1. @Body - 对象作为请求体
@POST("users")
Call<User> createUser(@Body User user);

// 2. RequestBody - 原始请求体
@POST("data")
Call<ResponseBody> postData(@Body RequestBody body);

// 调用
String json = "{\"name\":\"张三\"}";
RequestBody body = RequestBody.create(
    json,
    MediaType.parse("application/json")
);
apiService.postData(body);

// 3. 多部分请求体
@Multipart
@POST("upload")
Call<ResponseBody> uploadMultipleFiles(
    @Part MultipartBody.Part file1,
    @Part MultipartBody.Part file2
);

// 调用
File file1 = new File("/sdcard/image1.jpg");
File file2 = new File("/sdcard/image2.jpg");

MultipartBody.Part part1 = MultipartBody.Part.createFormData(
    "file1", file1.getName(), RequestBody.create(file1, MediaType.parse("image/jpeg"))
);

MultipartBody.Part part2 = MultipartBody.Part.createFormData(
    "file2", file2.getName(), RequestBody.create(file2, MediaType.parse("image/jpeg"))
);

apiService.uploadMultipleFiles(part1, part2);
```

### 13.5 标记注解

```java
// 1. @FormUrlEncoded - 表单编码
@FormUrlEncoded
@POST("login")
Call<User> login(@Field("username") String username);

// 2. @Multipart - 多部分
@Multipart
@POST("upload")
Call<ResponseBody> upload(@Part MultipartBody.Part file);

// 3. @Streaming - 流式响应（用于大文件下载）
@Streaming
@GET("download")
Call<ResponseBody> downloadFile();
```

---

## 第 14 章 Retrofit 高级功能

### 14.1 Converter 转换器

```java
// 1. Gson 转换器
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .build();

// 2. 自定义 Gson
Gson gson = new GsonBuilder()
    .setDateFormat("yyyy-MM-dd HH:mm:ss")
    .excludeFieldsWithoutExposeAnnotation()
    .create();

Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create(gson))
    .build();

// 3. Moshi 转换器
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(MoshiConverterFactory.create())
    .build();

// 4. Jackson 转换器
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(JacksonConverterFactory.create())
    .build();

// 5. Simple XML 转换器
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(SimpleXmlConverterFactory.create())
    .build();

// 6. ProtoBuf 转换器
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(ProtoConverterFactory.create())
    .build();

// 7. 多个转换器（按顺序）
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(ProtoConverterFactory.create())
    .addConverterFactory(GsonConverterFactory.create())
    .build();
```

### 14.2 CallAdapter 适配器

```java
// 1. 默认 Call 适配器
@GET("users")
Call<List<User>> getUsers();

// 2. RxJava 适配器
// 添加依赖
implementation 'com.squareup.retrofit2:adapter-rxjava3:2.9.0'

// 配置
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .addCallAdapterFactory(RxJava3CallAdapterFactory.create())
    .build();

// 使用
@GET("users")
Observable<List<User>> getUsers();

@GET("users")
Single<List<User>> getUsers();

@GET("users")
Flowable<List<User>> getUsers();

// 3. 协程适配器
@GET("users")
suspend fun getUsers(): List<User>

// 4. 自定义 CallAdapter
public class StringCallAdapter implements CallAdapter<String, Call<String>> {
    
    @Override
    public Type responseType() {
        return String.class;
    }
    
    @Override
    public Call<String> adapt(Call<String> call) {
        return call;
    }
}
```

### 14.3 文件上传

```java
// 1. 上传单个文件
@Multipart
@POST("upload")
Call<ResponseBody> uploadFile(@Part MultipartBody.Part file);

// 调用
File file = new File("/sdcard/image.jpg");
RequestBody requestFile = RequestBody.create(
    file,
    MediaType.parse("image/jpeg")
);
MultipartBody.Part body = MultipartBody.Part.createFormData(
    "file",
    file.getName(),
    requestFile
);
apiService.uploadFile(body);

// 2. 上传文件+参数
@Multipart
@POST("upload")
Call<ResponseBody> uploadFile(
    @Part("userId") RequestBody userId,
    @Part("description") RequestBody description,
    @Part MultipartBody.Part file
);

// 调用
RequestBody userIdBody = RequestBody.create(
    "123",
    MediaType.parse("text/plain")
);
RequestBody descriptionBody = RequestBody.create(
    "这是图片描述",
    MediaType.parse("text/plain")
);
apiService.uploadFile(userIdBody, descriptionBody, body);

// 3. 上传多个文件
@Multipart
@POST("upload")
Call<ResponseBody> uploadFiles(@Part List<MultipartBody.Part> files);

// 调用
List<MultipartBody.Part> parts = new ArrayList<>();
for (File file : files) {
    RequestBody requestFile = RequestBody.create(
        file,
        MediaType.parse("image/jpeg")
    );
    parts.add(MultipartBody.Part.createFormData(
        "files",
        file.getName(),
        requestFile
    ));
}
apiService.uploadFiles(parts);

// 4. 带进度的文件上传
public class ProgressRequestBody extends RequestBody {
    
    private RequestBody requestBody;
    private UploadCallback callback;
    
    public ProgressRequestBody(RequestBody requestBody, UploadCallback callback) {
        this.requestBody = requestBody;
        this.callback = callback;
    }
    
    @Override
    public MediaType contentType() {
        return requestBody.contentType();
    }
    
    @Override
    public void writeTo(BufferedSink sink) throws IOException {
        BufferedSink bufferedSink = Okio.buffer(new ForwardingSink(sink) {
            long bytesWritten = 0L;
            long contentLength = 0L;
            
            @Override
            public void write(Buffer source, long byteCount) throws IOException {
                super.write(source, byteCount);
                if (contentLength == 0) {
                    contentLength = contentLength();
                }
                bytesWritten += byteCount;
                callback.onProgress(bytesWritten, contentLength);
            }
        });
        requestBody.writeTo(bufferedSink);
        bufferedSink.flush();
    }
}
```

### 14.4 文件下载

```java
// 1. 基础下载
@GET("download/{filename}")
Call<ResponseBody> downloadFile(@Path("filename") String filename);

// 调用
Call<ResponseBody> call = apiService.downloadFile("test.zip");
call.enqueue(new Callback<ResponseBody>() {
    @Override
    public void onResponse(Call<ResponseBody> call, Response<ResponseBody> response) {
        if (response.isSuccessful()) {
            writeResponseBodyToDisk(response.body());
        }
    }
    
    @Override
    public void onFailure(Call<ResponseBody> call, Throwable t) {
    }
});

// 写入文件
private void writeResponseBodyToDisk(ResponseBody body) {
    try {
        InputStream inputStream = body.byteStream();
        FileOutputStream fos = new FileOutputStream("/sdcard/test.zip");
        
        byte[] buffer = new byte[4096];
        int bytesRead;
        while ((bytesRead = inputStream.read(buffer)) != -1) {
            fos.write(buffer, 0, bytesRead);
        }
        
        fos.flush();
        fos.close();
        inputStream.close();
    } catch (IOException e) {
        e.printStackTrace();
    }
}

// 2. 大文件下载（流式）
@Streaming
@GET("download/{filename}")
Call<ResponseBody> downloadLargeFile(@Path("filename") String filename);

// 3. 断点续传
@Streaming
@GET("download/{filename}")
Call<ResponseBody> downloadFile(
    @Path("filename") String filename,
    @Header("Range") String range
);

// 调用
String range = "bytes=" + downloadedBytes + "-";
apiService.downloadFile("test.zip", range);
```

### 14.5 动态 URL

```java
// 方式1: 使用 @Url
@GET
Call<User> getUser(@Url String url);

// 调用
apiService.getUser("https://other-api.example.com/user/123");

// 方式2: 动态 baseUrl
public class RetrofitManager {
    
    private static Retrofit createRetrofit(String baseUrl) {
        return new Retrofit.Builder()
            .baseUrl(baseUrl)
            .addConverterFactory(GsonConverterFactory.create())
            .build();
    }
    
    public static ApiService getApiService(String baseUrl) {
        return createRetrofit(baseUrl).create(ApiService.class);
    }
}

// 调用
ApiService api1 = RetrofitManager.getApiService("https://api1.example.com/");
ApiService api2 = RetrofitManager.getApiService("https://api2.example.com/");
```

### 14.6 取消请求

```java
// 1. 取消单个请求
Call<User> call = apiService.getUser(123);
call.enqueue(callback);

// 取消
call.cancel();

// 2. 取消多个请求
List<Call> calls = new ArrayList<>();
calls.add(apiService.getUser(1));
calls.add(apiService.getUser(2));
calls.add(apiService.getUser(3));

// 取消所有
for (Call call : calls) {
    if (!call.isCanceled()) {
        call.cancel();
    }
}

// 3. 判断请求是否已取消
if (call.isCanceled()) {
    // 请求已取消
}
```

---

