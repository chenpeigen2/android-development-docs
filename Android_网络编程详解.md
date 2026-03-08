# Android 网络编程详解

_作者：OpenClaw_  
_日期：2026-03-08_

---

## 目录

1. [HTTP 协议基础](#1-http-协议基础)
   - 1.1 [HTTP 请求结构](#11-http-请求结构)
   - 1.2 [HTTP 方法](#12-http-方法)
   - 1.3 [HTTP 状态码](#13-http-状态码)
2. [HTTP vs HTTPS](#2-http-vs-https)
   - 2.1 [区别对比](#21-区别对比)
   - 2.2 [HTTPS 握手过程](#22-https-握手过程)
3. [HTTP/1.1 vs HTTP/2 vs HTTP/3](#3-http11-vs-http2-vs-http3)
   - 3.1 [版本对比](#31-版本对比)
   - 3.2 [HTTP/2 多路复用](#32-http2-多路复用)
   - 3.3 [HTTP/3 (QUIC)](#33-http3-quic)
4. [TCP vs UDP](#4-tcp-vs-udp)
   - 4.1 [协议对比](#41-协议对比)
   - 4.2 [TCP 核心机制](#42-tcp-核心机制)
5. [TCP 三次握手与四次挥手](#5-tcp-三次握手与四次挥手)
   - 5.1 [三次握手](#51-三次握手)
   - 5.2 [四次挥手](#52-四次挥手)
   - 5.3 [TIME_WAIT](#53-time_wait)
6. [Android 网络库](#6-android-网络库)
   - 6.1 [OkHttp 使用](#61-okhttp-使用)
   - 6.2 [Retrofit 使用](#62-retrofit-使用)
7. [网络优化](#7-网络优化)
   - 7.1 [优化策略](#71-优化策略)
   - 7.2 [弱网优化](#72-弱网优化)
8. [总结](#8-总结)

---

## 1. HTTP 协议基础

### 1.1 HTTP 请求结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HTTP 请求结构                                       │
└─────────────────────────────────────────────────────────────────────────────┘

请求行: POST /api/login HTTP/1.1
请求头: Host, Content-Type, Content-Length, User-Agent, Accept, Authorization
空行
请求体: {"username":"admin","password":"123456"}
```

### 1.2 HTTP 方法

| 方法 | 说明 | 幂等性 |
|------|------|--------|
| GET | 获取资源 | 是 |
| POST | 创建资源 | 否 |
| PUT | 完整更新资源 | 是 |
| PATCH | 部分更新 | 否 |
| DELETE | 删除资源 | 是 |

### 1.3 HTTP 状态码

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 1xx | 信息 | 100 Continue |
| 2xx | 成功 | 200 OK, 201 Created |
| 3xx | 重定向 | 301 永久, 302 临时, 304 未修改 |
| 4xx | 客户端错误 | 400 Bad Request, 401 Unauthorized, 404 Not Found |
| 5xx | 服务器错误 | 500 Internal Error, 503 Service Unavailable |

---

## 2. HTTP vs HTTPS

### 2.1 区别对比

| 特性 | HTTP | HTTPS |
|------|------|-------|
| 端口 | 80 | 443 |
| 数据传输 | 明文 | 加密 (SSL/TLS) |
| 安全性 | 低 | 高 |
| 证书 | 不需要 | 需要 CA 证书 |
| 性能 | 快 | 稍慢 (握手开销) |

### 2.2 HTTPS 握手过程

```
Client                                    Server
   │                                         │
   │ 1. Client Hello (加密套件、随机数)     │
   │ ─────────────────────────────────────► │
   │                                         │
   │ 2. Server Hello + 证书                  │
   │ ◄───────────────────────────────────── │
   │                                         │
   │ 3. 验证证书                             │
   │                                         │
   │ 4. Client Key Exchange (加密预主密钥)   │
   │ ─────────────────────────────────────► │
   │                                         │
   │ 5. 生成会话密钥                         │
   │                                         │
   │ 6. 加密通信开始                         │
   │ ◄─────────────────────────────────────► │
```

---

## 3. HTTP/1.1 vs HTTP/2 vs HTTP/3

### 3.1 版本对比

| 特性 | HTTP/1.1 | HTTP/2 | HTTP/3 |
|------|----------|--------|--------|
| 传输层 | TCP | TCP | UDP (QUIC) |
| 多路复用 | ❌ | ✅ | ✅ |
| 头部压缩 | ❌ | HPACK | QPACK |
| 队头阻塞 | 严重 | TCP层 | 完全解决 |
| 连接建立 | 多次RTT | 多次RTT | 0-RTT |
| 连接迁移 | ❌ | ❌ | ✅ |

### 3.2 HTTP/2 多路复用

```
一个 TCP 连接可以并发多个请求:

Stream 1: 请求1 ───►│───►│ 响应1 ───►│
Stream 2: 请求2 ───►│───►│ 响应2 ───►│
Stream 3: 请求3 ───►│───►│ 响应3 ───►│

核心概念:
- Stream: 双向字节流
- Message: 请求或响应
- Frame: 最小传输单位
```

### 3.3 HTTP/3 (QUIC)

```
基于 UDP 的可靠传输:
- 解决 TCP 队头阻塞
- 0-RTT 连接建立
- 连接迁移 (网络切换不断开)
```

---

## 4. TCP vs UDP

### 4.1 协议对比

| 特性 | TCP | UDP |
|------|-----|-----|
| 连接 | 面向连接 | 无连接 |
| 可靠性 | 可靠 | 尽力而为 |
| 顺序 | 有序 | 无序 |
| 流量控制 | 有 | 无 |
| 拥塞控制 | 有 | 无 |
| 速度 | 较慢 | 快 |
| 头部 | 20字节 | 8字节 |
| 应用 | HTTP, FTP | DNS, 视频, 游戏 |

### 4.2 TCP 核心机制

- 确认应答 (ACK)
- 超时重传
- 序列号 (SEQ)
- 滑动窗口
- 拥塞控制 (慢启动、拥塞避免、快速重传、快速恢复)

---

## 5. TCP 三次握手与四次挥手

### 5.1 三次握手

```
Client                                    Server
   │                                         │
   │ 1. SYN=1, seq=x                        │
   │ ─────────────────────────────────────► │
   │    状态: SYN_SENT                       │
   │                                         │
   │ 2. SYN=1, ACK=1, seq=y, ack=x+1        │
   │ ◄───────────────────────────────────── │
   │    状态: SYN_RCVD                       │
   │                                         │
   │ 3. ACK=1, seq=x+1, ack=y+1             │
   │ ─────────────────────────────────────► │
   │    状态: ESTABLISHED                    │
   │                        ESTABLISHED      │

为什么是三次？
- 防止历史连接请求突然到达
- 同步双方序列号
- 确认双方收发能力
```

### 5.2 四次挥手

```
Client                                    Server
   │                                         │
   │ 1. FIN=1, seq=u                        │
   │ ─────────────────────────────────────► │
   │    状态: FIN_WAIT_1                     │
   │                                         │
   │ 2. ACK=1, seq=v, ack=u+1               │
   │ ◄───────────────────────────────────── │
   │    状态: FIN_WAIT_2    CLOSE_WAIT      │
   │                                         │
   │ 3. FIN=1, ACK=1, seq=w                 │
   │ ◄───────────────────────────────────── │
   │                        LAST_ACK         │
   │                                         │
   │ 4. ACK=1, seq=u+1, ack=w+1             │
   │ ─────────────────────────────────────► │
   │    状态: TIME_WAIT    CLOSED           │
   │    (等待 2MSL 后 CLOSED)               │

为什么是四次？
- TCP 全双工，每个方向需要单独关闭
- Server 可能还有数据要发送
```

### 5.3 TIME_WAIT

```
作用:
1. 确保最后的 ACK 能到达
2. 等待旧数据包消失

MSL (Maximum Segment Lifetime):
- Linux 默认 60 秒
- 2MSL = 120 秒

解决方案:
- SO_REUSEADDR
- tcp_tw_reuse
- 使用长连接
```

---

## 6. Android 网络库

### 6.1 OkHttp 使用

```kotlin
// 创建 Client
val client = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .addInterceptor(LoggingInterceptor())
    .cache(Cache(cacheDir, 10 * 1024 * 1024))
    .build()

// GET 请求
val request = Request.Builder()
    .url("https://api.example.com/users")
    .get()
    .build()

client.newCall(request).execute().use { response ->
    val body = response.body?.string()
}

// POST 请求
val json = """{"name":"test"}"""
val body = json.toRequestBody("application/json".toMediaType())
val request = Request.Builder()
    .url("https://api.example.com/users")
    .post(body)
    .build()
```

### 6.2 Retrofit 使用

```kotlin
// 定义接口
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: Int): User
    
    @POST("users")
    suspend fun createUser(@Body user: User): User
}

// 创建实例
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .client(okHttpClient)
    .build()

val api = retrofit.create(ApiService::class.java)

// 调用
viewModelScope.launch {
    val user = api.getUser(1)
}
```

---

## 7. 网络优化

### 7.1 优化策略

| 优化类型 | 策略 |
|----------|------|
| 连接优化 | 连接池、HTTP/2、Keep-Alive、DNS预解析 |
| 数据优化 | Gzip压缩、Protocol Buffers、图片压缩、增量更新 |
| 缓存优化 | HTTP缓存、本地缓存、预加载 |
| 请求优化 | 请求合并、批量请求、取消无用请求 |

### 7.2 弱网优化

```kotlin
// 1. 超时设置
val client = OkHttpClient.Builder()
    .connectTimeout(15, TimeUnit.SECONDS)
    .readTimeout(15, TimeUnit.SECONDS)
    .writeTimeout(15, TimeUnit.SECONDS)
    .build()

// 2. 重试机制
class RetryInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()
        var response: Response? = null
        var retryCount = 0
        
        while (retryCount < 3) {
            try {
                response = chain.proceed(request)
                if (response.isSuccessful) return response
            } catch (e: IOException) {
                // 重试
            }
            retryCount++
        }
        return response!!
    }
}

// 3. 离线缓存
val cache = Cache(cacheDir, 10 * 1024 * 1024)
val client = OkHttpClient.Builder()
    .cache(cache)
    .addInterceptor { chain ->
        var request = chain.request()
        if (!isNetworkAvailable()) {
            request = request.newBuilder()
                .cacheControl(CacheControl.FORCE_CACHE)
                .build()
        }
        chain.proceed(request)
    }
    .build()
```

---

## 8. 总结

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         网络编程面试要点                                    │
└─────────────────────────────────────────────────────────────────────────────┘

1. HTTP vs HTTPS 区别
2. HTTP/1.1 vs HTTP/2 vs HTTP/3 区别
3. TCP vs UDP 区别
4. TCP 三次握手/四次挥手过程
5. 为什么是三次握手/四次挥手
6. TIME_WAIT 状态的作用
7. OkHttp/Retrofit 使用
8. 网络优化策略
```

---

*本文档由 OpenClaw 生成*
