# Android 网络请求库完全指南

> 适用环境：Android 17（API 37）；源码分析固定为 OkHttp 4.12.0 与 Retrofit 2.9.0，协程与 RxJava 适配按该发布版本说明。

> 作者：OpenClaw | 日期：2026-03-10
> 涵盖：OkHttp | Retrofit

---

## 目录

- [第一篇：OkHttp - Square 出品的网络请求库](#第一篇okhttp---square-出品的网络请求库)
- [第 1 章 OkHttp 概述](#第-1-章-okhttp-概述)
  - [1.1 什么是 OkHttp？](#11-什么是-okhttp)
  - [1.2 核心优势](#12-核心优势)
  - [1.3 添加依赖](#13-添加依赖)
  - [1.4 权限配置](#14-权限配置)
- [第 2 章 OkHttp 基本使用](#第-2-章-okhttp-基本使用)
  - [2.1 创建 OkHttpClient](#21-创建-okhttpclient)
  - [2.2 同步请求](#22-同步请求)
  - [2.3 异步请求](#23-异步请求)
  - [2.4 GET 请求](#24-get-请求)
  - [2.5 POST 请求](#25-post-请求)
  - [2.6 文件上传](#26-文件上传)
  - [2.7 文件下载](#27-文件下载)
- [第 3 章 OkHttp 拦截器](#第-3-章-okhttp-拦截器)
  - [3.1 拦截器概述](#31-拦截器概述)
  - [3.2 应用拦截器](#32-应用拦截器)
  - [3.3 网络拦截器](#33-网络拦截器)
  - [3.4 日志拦截器](#34-日志拦截器)
  - [3.5 缓存拦截器](#35-缓存拦截器)
  - [3.6 头部拦截器](#36-头部拦截器)
- [第 4 章 OkHttp 缓存机制](#第-4-章-okhttp-缓存机制)
  - [4.1 缓存策略](#41-缓存策略)
  - [4.2 缓存配置](#42-缓存配置)
  - [4.3 强制刷新](#43-强制刷新)
  - [4.4 离线缓存](#44-离线缓存)
- [第 5 章 OkHttp 连接管理](#第-5-章-okhttp-连接管理)
  - [5.1 连接池](#51-连接池)
  - [5.2 连接复用](#52-连接复用)
  - [5.3 连接超时](#53-连接超时)
  - [5.4 DNS 解析](#54-dns-解析)
- [第 6 章 OkHttp 高级功能](#第-6-章-okhttp-高级功能)
  - [6.1 WebSocket](#61-websocket)
  - [6.2 HTTPS 配置](#62-https-配置)
  - [6.3 证书绑定](#63-证书绑定)
  - [6.4 Cookie 管理](#64-cookie-管理)
  - [6.5 请求重试](#65-请求重试)
- [第 7 章 OkHttp 核心原理](#第-7-章-okhttp-核心原理)
  - [7.1 整体架构](#71-整体架构)
  - [7.2 请求完整流程（源码级）](#72-请求完整流程源码级)
  - [7.3 拦截器链（责任链模式）深度分析](#73-拦截器链责任链模式深度分析)
  - [7.4 连接池原理（ConnectionPool）](#74-连接池原理connectionpool)
  - [7.5 缓存原理（CacheInterceptor）](#75-缓存原理cacheinterceptor)
  - [7.6 RetryAndFollowUpInterceptor 重试与重定向](#76-retryandfollowupinterceptor-重试与重定向)
  - [7.7 Okio 底层 I/O](#77-okio-底层-io)
- [第 8 章 OkHttp 源码解析](#第-8-章-okhttp-源码解析)
  - [8.1 源码入口与对象职责](#81-源码入口与对象职责)
  - [8.2 Call 创建与执行（同步/异步）](#82-call-创建与执行同步异步)
  - [8.3 Dispatcher 调度器（并发控制核心）](#83-dispatcher-调度器并发控制核心)
  - [8.4 RealConnection 与 Socket](#84-realconnection-与-socket)
  - [8.5 Exchange 与连接释放](#85-exchange-与连接释放)
- [第 9 章 OkHttp 性能优化](#第-9-章-okhttp-性能优化)
  - [9.1 连接优化](#91-连接优化)
  - [9.2 缓存优化](#92-缓存优化)
  - [9.3 请求优化](#93-请求优化)
  - [9.4 内存优化](#94-内存优化)
- [第 10 章 OkHttp 面试常见问题](#第-10-章-okhttp-面试常见问题)
  - [10.1 拦截器原理](#101-拦截器原理)
  - [10.2 连接池复用](#102-连接池复用)
  - [10.3 缓存策略](#103-缓存策略)
  - [10.4 同步 vs 异步](#104-同步-vs-异步)
  - [10.5 Dispatcher](#105-dispatcher)
  - [10.6 责任链模式](#106-责任链模式)
  - [10.7 WebSocket](#107-websocket)
  - [10.8 HTTPS 握手](#108-https-握手)
  - [10.9 OkHttp vs HttpURLConnection](#109-okhttp-vs-httpurlconnection)
  - [10.10 最佳实践](#1010-最佳实践)
- [第二篇：Retrofit - Square 出品的 REST 客户端](#第二篇retrofit---square-出品的-rest-客户端)
- [第 11 章 Retrofit 概述](#第-11-章-retrofit-概述)
  - [11.1 什么是 Retrofit？](#111-什么是-retrofit)
  - [11.2 核心优势](#112-核心优势)
  - [11.3 添加依赖](#113-添加依赖)
  - [11.4 与 OkHttp 关系](#114-与-okhttp-关系)
- [第 12 章 Retrofit 基本使用](#第-12-章-retrofit-基本使用)
  - [12.1 创建 Retrofit 实例](#121-创建-retrofit-实例)
  - [12.2 定义 API 接口](#122-定义-api-接口)
  - [12.3 GET 请求](#123-get-请求)
  - [12.4 POST 请求](#124-post-请求)
  - [12.5 PUT 请求](#125-put-请求)
  - [12.6 DELETE 请求](#126-delete-请求)
- [第 13 章 Retrofit 注解详解](#第-13-章-retrofit-注解详解)
  - [13.1 请求方法注解](#131-请求方法注解)
  - [13.2 请求头注解](#132-请求头注解)
  - [13.3 请求参数注解](#133-请求参数注解)
  - [13.4 请求体注解](#134-请求体注解)
  - [13.5 标记注解](#135-标记注解)
- [第 14 章 Retrofit 高级功能](#第-14-章-retrofit-高级功能)
  - [14.1 Converter 转换器](#141-converter-转换器)
  - [14.2 CallAdapter 适配器](#142-calladapter-适配器)
  - [14.3 文件上传](#143-文件上传)
  - [14.4 文件下载](#144-文件下载)
  - [14.5 动态 URL](#145-动态-url)
  - [14.6 取消请求](#146-取消请求)
- [第 15 章 Retrofit 与协程](#第-15-章-retrofit-与协程)
  - [15.1 suspend 接口与返回类型](#151-suspend-接口与返回类型)
  - [15.2 创建客户端](#152-创建客户端)
  - [15.3 取消如何传到网络层](#153-取消如何传到网络层)
  - [15.4 ViewModel 与视图生命周期](#154-viewmodel-与视图生命周期)
  - [15.5 HTTP、业务与协议错误](#155-http业务与协议错误)
  - [15.6 重试与超时](#156-重试与超时)
- [第 16 章 Retrofit 与 RxJava](#第-16-章-retrofit-与-rxjava)
  - [16.1 选择匹配的适配器](#161-选择匹配的适配器)
  - [16.2 接口与线程](#162-接口与线程)
  - [16.3 订阅与释放](#163-订阅与释放)
  - [16.4 重试操作符](#164-重试操作符)
  - [16.5 背压与请求数量](#165-背压与请求数量)
- [第 17 章 Retrofit 核心原理](#第-17-章-retrofit-核心原理)
  - [17.1 动态代理](#171-动态代理)
  - [17.2 注解到请求](#172-注解到请求)
  - [17.3 Converter](#173-converter)
  - [17.4 CallAdapter](#174-calladapter)
  - [17.5 缓存与复用](#175-缓存与复用)
- [第 18 章 Retrofit 源码调用链](#第-18-章-retrofit-源码调用链)
  - [18.1 loadServiceMethod](#181-loadservicemethod)
  - [18.2 HttpServiceMethod](#182-httpservicemethod)
  - [18.3 OkHttpCall](#183-okhttpcall)
  - [18.4 parseResponse](#184-parseresponse)
- [第 19 章 网络性能与可观测性](#第-19-章-网络性能与可观测性)
  - [19.1 复用与并发预算](#191-复用与并发预算)
  - [19.2 大响应](#192-大响应)
  - [19.3 测试设计](#193-测试设计)
  - [19.4 Android 17 本地网络权限](#194-android-17-本地网络权限)
- [第 20 章 常见问题](#第-20-章-常见问题)
  - [20.1 suspend 是否运行在主线程上？](#201-suspend-是否运行在主线程上)
  - [20.2 HTTP 错误为什么没有进入 onFailure？](#202-http-错误为什么没有进入-onfailure)
  - [20.3 连接池为什么不能解决所有慢请求？](#203-连接池为什么不能解决所有慢请求)
  - [20.4 取消后为什么仍要校验页面状态？](#204-取消后为什么仍要校验页面状态)
  - [20.5 版本升级改变哪些边界？](#205-版本升级改变哪些边界)

---

## 第一篇：OkHttp - Square 出品的网络请求库

---

## 第 1 章 OkHttp 概述

### 1.1 什么是 OkHttp？

**OkHttp** 是 Square 公司开源的 Android/Java HTTP 客户端，是目前 Android 开发中使用最广泛的网络请求库。

```text
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

```text
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

```text
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

```text
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

不能无条件开启 BODY：它会记录请求/响应内容；`redactHeader` 仅隐藏指定头，不会脱敏 URL 查询参数或 JSON 正文。下例仅在 debug 开 BASIC；即使 BASIC 也可能输出带敏感参数的 URL，应避免把 token 放入 URL，并按项目日志策略决定是否完全关闭。来源：[OkHttp 4.12.0 HttpLoggingInterceptor](https://github.com/square/okhttp/blob/parent-4.12.0/okhttp-logging-interceptor/src/main/kotlin/okhttp3/logging/HttpLoggingInterceptor.kt)。

```java
// 使用官方日志拦截器
HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
loggingInterceptor.redactHeader("Authorization");
loggingInterceptor.redactHeader("Cookie");
loggingInterceptor.redactHeader("Set-Cookie");
loggingInterceptor.setLevel(BuildConfig.DEBUG
        ? HttpLoggingInterceptor.Level.BASIC
        : HttpLoggingInterceptor.Level.NONE);

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

```text
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

```text
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

TLS 同时校验证书信任链与主机名；缺少任意一项都不能确认服务端身份。正常客户端使用平台默认校验：

```java
OkHttpClient client = new OkHttpClient.Builder().build();
```

需要开发 CA 时，用 Android Network Security Configuration（API 24+）的 `debug-overrides` 限定调试包，而不是在生产客户端注入 trust-all。清单需设置 `android:networkSecurityConfig="@xml/network_security_config"`：

```xml
<!-- res/xml/network_security_config.xml；需在 res/raw/debug_cas 提供开发 CA。 -->
<network-security-config>
    <debug-overrides>
        <trust-anchors>
            <certificates src="@raw/debug_cas" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

这里不会允许明文 HTTP，也不取消主机名校验。证书绑定不是所有生产应用的强制配置；是否启用应结合威胁模型、证书轮换和备用公钥设计，不能使用示意 pin 发布。来源：[Android 网络安全配置](https://developer.android.com/privacy-and-security/security-config)、[OkHttp 4.12.0 HTTPS 文档](https://github.com/square/okhttp/blob/parent-4.12.0/docs/https.md)。

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

`retryOnConnectionFailure(true)` 处理连接失败后的可恢复路径，不会把任意 4xx/5xx 都重试。业务重试应限制为可重放请求；支付等写操作必须由服务端幂等协议保证，不能靠客户端重试次数消除重复提交。

以下应用拦截器只对 `Retry-After: 0` 的 GET 503 立即重试一次。重试前关闭响应，最终响应所有权交给调用者；没有实例级共享计数。需要等待的退避由上层协程 `delay` 或任务调度器承担，不在 Dispatcher 线程中 `sleep`。

```java
// 应用拦截器：仅立即重试一次带 Retry-After: 0 的 GET 503。
public final class ImmediateGetRetry implements okhttp3.Interceptor {
    @Override public okhttp3.Response intercept(Chain chain) throws java.io.IOException {
        okhttp3.Request request = chain.request();
        okhttp3.Response first = chain.proceed(request);
        if (!"GET".equals(request.method()) || first.code() != 503
                || !"0".equals(first.header("Retry-After")) || chain.call().isCanceled()) {
            return first;
        }
        first.close();
        return chain.proceed(request);
    }
}
```

网络拦截器要求每次恰好调用一次 `proceed()`，上述类只能用 `addInterceptor` 注册。调用者用 `response.use { ... }` 或 try-with-resources 关闭最终响应；异常直接交给上层处理，取消不再触发重试。

参考：[OkHttp 4.12.0 拦截器](https://github.com/square/okhttp/blob/parent-4.12.0/docs/interceptors.md)、[RetryAndFollowUpInterceptor.kt](https://github.com/square/okhttp/blob/parent-4.12.0/okhttp/src/main/kotlin/okhttp3/internal/http/RetryAndFollowUpInterceptor.kt)。

## 第 7 章 OkHttp 核心原理

### 7.1 整体架构

OkHttp 4.12.0 的一次调用由 `RealCall` 表示；应用层请求和响应经过拦截器链，连接发现由 `ExchangeFinder` 协助完成，一次实际 HTTP 交换由 `Exchange` 连接协议编解码器和连接。

```text
OkHttpClient.newCall(Request) -> RealCall
  -> 应用拦截器
  -> RetryAndFollowUpInterceptor   恢复、重定向、认证后续请求
  -> BridgeInterceptor            HTTP 头与透明 gzip
  -> CacheInterceptor             缓存策略与条件请求
  -> ConnectInterceptor           建立 Exchange / 寻找连接
  -> 网络拦截器
  -> CallServerInterceptor        通过 Exchange 读写请求响应
```

这些是库内部实现，不是 AOSP 类；业务只依赖 `Call`、`Interceptor`、`EventListener` 等公共接口。

### 7.2 请求完整流程（源码级）

`execute()` 和 `enqueue()` 都先检查 Call 是否已经执行，一个 Call 只能执行一次。同步路径在调用线程执行拦截器链，异步路径由 Dispatcher 提交 `AsyncCall`。`getResponseWithInterceptorChain()` 组装链；结束或异常路径负责释放占用。收到响应头不代表请求资源全部结束：响应体可能仍在读取，直到关闭、读完或失败才完成相应交换。

### 7.3 拦截器链（责任链模式）深度分析

应用拦截器面向逻辑请求，能看到缓存命中，并可短路返回；网络拦截器面向实际网络交换，重定向时可能运行多次，纯缓存命中时不会运行。它必须保持同一 host/port 并恰好调用一次 `proceed`。应用拦截器多次调用时必须先关闭旧响应体。

```kotlin
class RequestIdInterceptor : okhttp3.Interceptor {
    override fun intercept(chain: okhttp3.Interceptor.Chain): okhttp3.Response {
        val request = chain.request().newBuilder()
            .header("X-Request-Id", java.util.UUID.randomUUID().toString())
            .build()
        return chain.proceed(request) // 不消费、不关闭将交给调用者的 body
    }
}
```

### 7.4 连接池原理（ConnectionPool）

连接池持有可复用的 `RealConnection`。复用先检查地址、路由、TLS 等条件和连接健康状况；HTTP/1.1 通常由一个交换独占连接，HTTP/2 在同一连接上复用多个流。`maxIdleConnections` 限制空闲连接保留数量，不是并发请求上限；跨 host 的 HTTP/2 合并还有证书和路由等约束，不能仅凭 IP 相同认定可复用。

### 7.5 缓存原理（CacheInterceptor）

缓存策略比较请求缓存指令、响应有效期与已有条目：新鲜命中直接返回，过期条目可以带 `If-None-Match`/`If-Modified-Since` 发起条件请求。304 表示继续使用已有实体并合并头，不是空业务数据。`no-cache` 允许存储但要求重新验证，`no-store` 禁止存储；用户切换时还要处理带身份信息的缓存隔离。

### 7.6 RetryAndFollowUpInterceptor 重试与重定向

连接故障恢复需要判断异常类型、请求体能否重放及是否存在其他路由。重定向和认证响应会生成 follow-up request；库限制后续请求数量，避免无限循环。业务幂等性仍由服务端协议决定。文件流等一次性请求体不应随意重新发送；取消后停止恢复并向调用者报告取消。

### 7.7 Okio 底层 I/O

Okio 使用 Source/Sink 和分段 Buffer 组织读写，减少细碎 I/O 与数据复制。`ResponseBody.string()` 会一次性读取全部内容且只能消费一次；大文件用 `source()`/`byteStream()` 流式写到文件，并用 `use` 关闭。日志拦截器和解析器若都消费原 body，会破坏一次性读取契约。

源码：[RealCall.kt](https://github.com/square/okhttp/blob/parent-4.12.0/okhttp/src/main/kotlin/okhttp3/internal/connection/RealCall.kt)、[CacheInterceptor.kt](https://github.com/square/okhttp/blob/parent-4.12.0/okhttp/src/main/kotlin/okhttp3/internal/cache/CacheInterceptor.kt)、[RealConnection.kt](https://github.com/square/okhttp/blob/parent-4.12.0/okhttp/src/main/kotlin/okhttp3/internal/connection/RealConnection.kt)。

## 第 8 章 OkHttp 源码解析

### 8.1 源码入口与对象职责

固定路径为 `okhttp/src/main/kotlin/okhttp3/internal/`。先读 `connection/RealCall.kt` 中的 `getResponseWithInterceptorChain()`，再沿 `http/RealInterceptorChain.kt` 跟进；连接层依次阅读 `ExchangeFinder.kt`、`RealConnection.kt`、`Exchange.kt`。不要把早期 Java 实现的内部字段直接用于 4.12.0。

### 8.2 Call 创建与执行（同步/异步）

`newCall` 只创建调用对象，不立即发包。异步 `enqueue` 的回调不在 Android 主线程；`onFailure` 表示传输执行失败，HTTP 404/500 仍进入 `onResponse`。调用者必须检查状态码并关闭响应体。

```java
okhttp3.Call call = client.newCall(request);
call.enqueue(new okhttp3.Callback() {
    @Override public void onFailure(okhttp3.Call call, java.io.IOException error) {
        if (call.isCanceled()) return; // 页面离开不是网络错误提示
        // 将错误映射到业务状态，再切换主线程更新 UI。
    }
    @Override public void onResponse(okhttp3.Call call, okhttp3.Response response)
            throws java.io.IOException {
        try (okhttp3.Response owned = response) {
            if (!owned.isSuccessful()) {
                // 映射 HTTP 错误；不要把服务器原始错误页直接展示给用户。
                return;
            }
            String body = owned.body() == null ? "" : owned.body().string();
            // 此处解析 body；向 UI 提交前还需检查页面/请求标识。
        }
    }
});
// 页面停止持有该请求时：call.cancel();
```

### 8.3 Dispatcher 调度器（并发控制核心）

4.12.0 默认 `maxRequests=64`、`maxRequestsPerHost=5`，用于异步调用的排队和晋升；同步调用被记录，但不由这两个阈值排队。增加上限会同时增加服务端压力、解析并发和内存占用，不一定降低页面耗时。

### 8.4 RealConnection 与 Socket

连接建立包含 DNS、路由选择、TCP、代理隧道（适用时）、TLS 与协议协商。EventListener 可以分段记录这些过程；连接复用时不会再次出现完整 DNS/TLS 序列。读取超时、连接超时和整个 Call 超时覆盖的阶段不同，应分别设置预算。

### 8.5 Exchange 与连接释放

`Exchange` 跟踪一次请求/响应交换的完成情况，并通过 `RealCall.messageDone` 报告请求体与响应体完成。连接最终是否归还池取决于调用状态、连接可复用性和剩余分配；HTTP/2 的单个流取消不等于关闭整个共享连接。业务最重要的职责是关闭 body、传播取消，不调用内部“归还连接”方法。

源码：[Dispatcher.kt](https://github.com/square/okhttp/blob/parent-4.12.0/okhttp/src/main/kotlin/okhttp3/Dispatcher.kt)、[Exchange.kt](https://github.com/square/okhttp/blob/parent-4.12.0/okhttp/src/main/kotlin/okhttp3/internal/connection/Exchange.kt)。

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

```text
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

```text
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

```text
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

## 第 15 章 Retrofit 与协程

### 15.1 suspend 接口与返回类型

Retrofit 2.9.0 原生识别 suspend 方法。返回 `T` 时非 2xx 抛 `HttpException`；返回 `Response<T>` 时由调用者检查 HTTP 状态。网络 I/O 失败和 JSON 转换失败仍会抛异常。以下例子采用 Gson converter，DTO 字段显式可空，在数据边界做校验。

```kotlin
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Path

data class ProfileDto(val id: String?, val name: String?)
data class Profile(val id: String, val name: String)
interface ProfileApi {
    @GET("profiles/{id}")
    suspend fun profile(@Path("id") id: String): Response<ProfileDto>
}
sealed interface ProfileResult {
    data class Data(val profile: Profile) : ProfileResult
    data class HttpError(val code: Int) : ProfileResult
    data object NetworkError : ProfileResult
    data object InvalidPayload : ProfileResult
}
class ProfileRepository(private val api: ProfileApi) {
    suspend fun load(id: String): ProfileResult = try {
        val response = api.profile(id)
        if (!response.isSuccessful) {
            response.errorBody()?.close()
            ProfileResult.HttpError(response.code())
        } else {
            val dto = response.body()
            val validId = dto?.id?.takeIf { it.isNotBlank() }
            val name = dto?.name
            if (validId == null || name == null) ProfileResult.InvalidPayload
            else ProfileResult.Data(Profile(validId, name))
        }
    } catch (cancelled: kotlinx.coroutines.CancellationException) {
        throw cancelled
    } catch (badJson: com.google.gson.JsonParseException) {
        ProfileResult.InvalidPayload
    } catch (network: java.io.IOException) {
        ProfileResult.NetworkError
    }
}
```

### 15.2 创建客户端

```kotlin
val http = okhttp3.OkHttpClient.Builder()
    .connectTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
    .readTimeout(20, java.util.concurrent.TimeUnit.SECONDS)
    .callTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
    .build()
val api = retrofit2.Retrofit.Builder()
    .baseUrl("https://example.com/api/") // 替换为业务服务器，末尾保留 /
    .client(http)
    .addConverterFactory(retrofit2.converter.gson.GsonConverterFactory.create())
    .build().create(ProfileApi::class.java)
val repository = ProfileRepository(api)
```

### 15.3 取消如何传到网络层

2.9.0 的 `KotlinExtensions.kt` 使用 `suspendCancellableCoroutine`，并在取消回调里执行 `Call.cancel()`。因此直接调用 suspend 接口即可，不必再套 `withContext(IO)` 让网络“异步”。这不等于所有后续解析/映射都没有 CPU 开销；大规模数据转换放到 Default dispatcher。

### 15.4 ViewModel 与视图生命周期

ViewModel 在 `viewModelScope` 中启动请求，将加载/数据/失败表达为 StateFlow；Fragment 使用 `viewLifecycleOwner` 收集状态。旋转时 ViewModel 通常保留，请求不会因旧 View 销毁而重复发起；离开导航目的地并清理 ViewModel 时取消请求。如果每次重新加载会覆盖旧请求，先取消旧 Job，必要时再校验请求 ID。

### 15.5 HTTP、业务与协议错误

HTTP 200 并不代表业务成功；业务 envelope 的 code 在 Repository 解包。401 进入认证流程，403 是权限拒绝，429/503 可按 Retry-After 调度。204、JSON null 和空字符串是不同协议结果，不能统一强转为非空 DTO。

### 15.6 重试与超时

只为幂等请求定义次数上限和带抖动的退避；`delay` 能响应取消。`withTimeout` 限制整个协程操作，OkHttp callTimeout 限制单个 Call。不要同时在 Repository、拦截器、Worker 各重试三次而导致请求成倍放大。

源码：[Retrofit 2.9.0 KotlinExtensions.kt](https://github.com/square/retrofit/blob/2.9.0/retrofit/src/main/java/retrofit2/KotlinExtensions.kt)。

## 第 16 章 Retrofit 与 RxJava

### 16.1 选择匹配的适配器

以下限定 RxJava 2：依赖 `com.squareup.retrofit2:adapter-rxjava2:2.9.0`、`io.reactivex.rxjava2:rxjava:2.2.21`、`io.reactivex.rxjava2:rxandroid:2.1.1`。不要混用 RxJava 3 的类型与 RxJava 2 适配器。

### 16.2 接口与线程

```kotlin
interface RxProfileApi {
    @retrofit2.http.GET("profiles/{id}")
    fun profile(@retrofit2.http.Path("id") id: String): io.reactivex.Single<ProfileDto>
}
val rxApi = retrofit2.Retrofit.Builder()
    .baseUrl("https://example.com/api/")
    .client(http)
    .addConverterFactory(retrofit2.converter.gson.GsonConverterFactory.create())
    .addCallAdapterFactory(retrofit2.adapter.rxjava2.RxJava2CallAdapterFactory.createAsync())
    .build().create(RxProfileApi::class.java)
```

`createAsync()` 使用异步 Call；默认 `create()` 使用同步执行，通常需要 `subscribeOn(Schedulers.io())`。`observeOn(AndroidSchedulers.mainThread())` 控制下游 UI 消费线程，而不是修改 OkHttp 内部调度器。

### 16.3 订阅与释放

```kotlin
// Fragment 的字段；在 onViewCreated 中添加订阅。
private val requests = io.reactivex.disposables.CompositeDisposable()

fun loadProfile(id: String) {
    requests.add(rxApi.profile(id)
        .observeOn(io.reactivex.android.schedulers.AndroidSchedulers.mainThread())
        .subscribe(
            { dto -> /* 校验 DTO 后渲染当前 View */ },
            { error -> /* 映射 HTTP、网络、解析错误并显示重试入口 */ }
        ))
}
// Fragment.onDestroyView 中调用 requests.clear()，再清空 binding。
```

`clear()` 释放本批订阅但容器可再次使用；`dispose()` 使容器永久结束。释放订阅会取消对应网络调用，不能省略 onError 消费函数。

### 16.4 重试操作符

`retry()` 无参数会不断重订阅。使用 `retryWhen` 时应按异常类型、次数、退避生成新的订阅机会，并让页面释放中止等待；认证失败不能通过无限重试恢复。

### 16.5 背压与请求数量

一次 HTTP 响应并不会因为改为 Flowable 就逐条流式解析 JSON。搜索输入应用防抖与 `switchMap` 淘汰旧查询；批量请求应用受限并发，不能无界 flatMap。

源码：[RxJava2CallAdapterFactory](https://github.com/square/retrofit/blob/2.9.0/retrofit-adapters/rxjava2/src/main/java/retrofit2/adapter/rxjava2/RxJava2CallAdapterFactory.java)、[CallEnqueueObservable](https://github.com/square/retrofit/blob/2.9.0/retrofit-adapters/rxjava2/src/main/java/retrofit2/adapter/rxjava2/CallEnqueueObservable.java)。

## 第 17 章 Retrofit 核心原理

### 17.1 动态代理

`Retrofit.create()` 为服务接口建立 Java 动态代理；调用接口方法时解析注解并执行 `ServiceMethod`，不是生成一个实现了每个业务方法的源码文件。

### 17.2 注解到请求

`RequestFactory` 把方法注解解析为 HTTP 方法、相对路径及 ParameterHandler。调用时再把参数绑定到 Path/Query/Header/Body。接口声明的静态配置被缓存，实际参数每次传入。

### 17.3 Converter

Converter 将请求体编码或将响应体转换为模型。Factory 按注册顺序询问，过于宽泛的 converter 应靠后；例如 Gson 几乎接受所有模型，先注册会遮挡只处理特定类型的 converter。

### 17.4 CallAdapter

CallAdapter 改变调用的外部抽象，例如 Call、RxJava Single。它不负责把 JSON 变成 DTO。suspend 方法走 HttpServiceMethod 中的协程适配分支，不需要额外的旧协程 adapter artifact。

### 17.5 缓存与复用

Retrofit 缓存方法解析结果以减少重复反射；这不是 HTTP 响应缓存。HTTP 缓存仍由共享 OkHttpClient 的 Cache 控制，登录态、拦截器与连接池也属于客户端配置。

源码：[Retrofit.java](https://github.com/square/retrofit/blob/2.9.0/retrofit/src/main/java/retrofit2/Retrofit.java)、[RequestFactory.java](https://github.com/square/retrofit/blob/2.9.0/retrofit/src/main/java/retrofit2/RequestFactory.java)。

## 第 18 章 Retrofit 源码调用链

### 18.1 loadServiceMethod

代理方法调用进入 `loadServiceMethod(method)`，优先从缓存读取；缓存缺失时解析并发布。应沿同一标签源码阅读，缓存内部同步策略不属于公共兼容契约。

### 18.2 HttpServiceMethod

解析返回类型、注解、converter 和 adapter，区分普通调用、SuspendForBody、SuspendForResponse。非空 suspend body 遇到 null 会走异常路径，接口应如实描述可空性。

### 18.3 OkHttpCall

每次业务调用创建 OkHttpCall，延迟构建原始 OkHttp Call；参数转换失败会在创建请求阶段报告。`clone()` 创建可再次执行的调用，已经 execute/enqueue 的对象不能直接复用。

### 18.4 parseResponse

非 2xx 形成 error response；204/205 关闭 body 并返回空 body；普通成功响应交给 responseConverter。使用 `Response<T>` 时错误体由调用者处理并关闭，成功 DTO 转换器则在转换期间消费响应体。

源码：[HttpServiceMethod.java](https://github.com/square/retrofit/blob/2.9.0/retrofit/src/main/java/retrofit2/HttpServiceMethod.java)、[OkHttpCall.java](https://github.com/square/retrofit/blob/2.9.0/retrofit/src/main/java/retrofit2/OkHttpCall.java)。

## 第 19 章 网络性能与可观测性

### 19.1 复用与并发预算

共享 OkHttpClient/Retrofit，按不同认证或缓存边界建立少量配置。请求延迟拆为排队、DNS、建连、TLS、服务端等待、下载、解析和 UI 提交，避免把所有慢请求都归因于连接池。

### 19.2 大响应

下载使用 `@Streaming` 的 ResponseBody 和文件流，在后台写临时文件，成功后再替换目标文件；失败清理临时文件。`string()` 和 `bytes()` 都会整体加载，不能用于不受限下载。

### 19.3 测试设计

固定版本 `mockwebserver:4.12.0` 可模拟 200、204、401、503、延迟与断连。测试同时检查结果、请求次数、取消后不更新 UI、body 关闭，以及日志中没有 token/个人数据。

### 19.4 Android 17 本地网络权限

targetSdk 37 的本地网络访问受 `ACCESS_LOCAL_NETWORK` 运行时权限保护。直接访问局域网设备的功能应先声明并申请权限，授权后才创建连接；系统提供的设备选择器可走平台中介访问路径，避免申请广泛局域网权限。拒绝时显示功能不可用和重新授权入口，不循环请求权限。普通远端 HTTPS 仍使用 `INTERNET`，不能把两类权限混为一谈。

```xml
<uses-permission android:name="android.permission.INTERNET" />
<!-- 仅在功能访问局域网时声明；API 37 上还须运行时申请。 -->
<uses-permission android:name="android.permission.ACCESS_LOCAL_NETWORK" />
```

网络库不会代替 Activity 完成授权。连接失败时先区分权限、DNS、TLS、HTTP 和业务错误，不以“更新 OkHttp”替代平台权限处理。

参考：[Android 17 target 行为变化](https://developer.android.com/about/versions/17/behavior-changes-17)、[EventListener](https://github.com/square/okhttp/blob/parent-4.12.0/okhttp/src/main/kotlin/okhttp3/EventListener.kt)。

## 第 20 章 常见问题

### 20.1 suspend 是否运行在主线程上？

调用可以从主线程发起，底层异步 I/O 不阻塞主线程；拿到模型后的业务计算仍在当前协程上下文中执行。

### 20.2 HTTP 错误为什么没有进入 onFailure？

OkHttp 收到了合法 HTTP 响应，传输层调用已成功；检查 `isSuccessful`。Retrofit 是否抛 HttpException 则取决于声明为 body、Response 还是 Call。

### 20.3 连接池为什么不能解决所有慢请求？

连接池减少建连开销，不解决服务端耗时、Dispatcher 排队和主线程解析。先分阶段度量再调整并发。

### 20.4 取消后为什么仍要校验页面状态？

取消和结果提交可能竞争；已经排到主线程的业务任务不一定被网络取消撤回。使用生命周期收集、请求 ID 与状态归属共同避免旧结果覆盖。

### 20.5 版本升级改变哪些边界？

系统升级关注权限、网络安全和后台限制；OkHttp/Retrofit 升级关注公共 API、最低运行要求、TLS、converter 和 adapter 行为。AOSP `android-17.0.0_r1` 不用于选择 Maven artifact 版本。
