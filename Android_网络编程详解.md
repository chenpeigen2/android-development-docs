# Android 网络编程详解

_作者：OpenClaw_  
_日期：2026-03-08_

---

## 目录

- [1. HTTP 协议基础](#1-http-协议基础)
  - [1.1 HTTP 请求结构](#11-http-请求结构)
  - [1.2 HTTP 方法](#12-http-方法)
  - [1.3 HTTP 状态码](#13-http-状态码)
- [2. HTTP vs HTTPS](#2-http-vs-https)
  - [2.1 区别对比](#21-区别对比)
  - [2.2 HTTPS 握手过程](#22-https-握手过程)
- [3. HTTP/1.1 vs HTTP/2 vs HTTP/3](#3-http11-vs-http2-vs-http3)
  - [3.1 版本对比](#31-版本对比)
  - [3.2 HTTP/2 多路复用](#32-http2-多路复用)
  - [3.3 HTTP/3 (QUIC)](#33-http3-quic)
- [4. TCP vs UDP](#4-tcp-vs-udp)
  - [4.1 协议对比](#41-协议对比)
  - [4.2 TCP 核心机制](#42-tcp-核心机制)
- [5. TCP 三次握手与四次挥手](#5-tcp-三次握手与四次挥手)
  - [5.1 三次握手](#51-三次握手)
  - [5.2 四次挥手](#52-四次挥手)
  - [5.3 TIME_WAIT](#53-time_wait)
- [6. Android 网络库](#6-android-网络库)
  - [6.1 OkHttp 使用](#61-okhttp-使用)
  - [6.2 Retrofit 使用](#62-retrofit-使用)
  - [6.3 Android 17 局域网权限与证书配置](#63-android-17-局域网权限与证书配置)
- [7. 网络优化](#7-网络优化)
  - [7.1 优化策略](#71-优化策略)
  - [7.2 弱网优化](#72-弱网优化)
- [8. 总结](#8-总结)

---

## 1. HTTP 协议基础

### 1.1 HTTP 请求结构

```text
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

TLS 1.3 的完整证书握手（忽略可选客户端认证）如下；它不是 TLS 1.2 RSA 密钥交换，已没有 `ClientKeyExchange` 发送 RSA 加密预主密钥的步骤。

```text
Client                                    Server
ClientHello + key_share              ->
                                     <-  ServerHello + key_share
双方从 (EC)DHE 共享秘密及握手 transcript 经 HKDF 派生密钥
                                     <-  {EncryptedExtensions,
                                          Certificate, CertificateVerify, Finished}
验证证书链、hostname、签名与 Finished  ->
{Finished}                           ->
Application Data                    <->  Application Data
```

大括号内是握手密钥保护的消息；证书用于身份认证，(EC)DHE 用于协商共享秘密。会话恢复可使用 PSK；0-RTT early data 只适用于恢复且有重放风险，不可默认承载支付等非幂等写操作。来源：[RFC 8446 §2、§4.4、§8](https://www.rfc-editor.org/rfc/rfc8446)。

---

## 3. HTTP/1.1 vs HTTP/2 vs HTTP/3

### 3.1 版本对比

| 特性 | HTTP/1.1 | HTTP/2 | HTTP/3 |
|------|----------|--------|--------|
| 传输层 | TCP | TCP | UDP 上的 QUIC |
| 多路复用 | ❌ | ✅ | ✅ |
| 头部压缩 | ❌ | HPACK | QPACK |
| 队头阻塞 | 严重 | TCP层 | 消除跨独立流的传输层队头阻塞；流内仍有序 |
| 连接建立 | TCP + TLS 握手 | TCP + TLS 握手 | 首次通常 1-RTT，恢复可 0-RTT |
| 连接迁移 | ❌ | ❌ | ✅ |

### 3.2 HTTP/2 多路复用

```text
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

```text
基于 UDP 的可靠传输:
- 解决 TCP 队头阻塞
- 首次完整握手通常 1-RTT；恢复且满足条件才可发送 0-RTT 数据
- Connection ID 支持连接迁移，仍需路径验证及对端策略；不保证任意切网都不断开
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
| 头部 | 最小 20 字节（不含选项） | 8 字节 |
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

```text
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

```text
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
- Server 可能还有数据要发送；若 ACK 与 FIN 合并，实际报文数可以少于四个。
```

### 5.3 TIME_WAIT

```text
作用:
1. 确保最后的 ACK 能到达
2. 等待旧数据包消失

MSL (Maximum Segment Lifetime):
- 协议用 2MSL 描述等待旧段过期；Linux `TCP_TIMEWAIT_LEN` 通常直接定义约 60 秒 TIME_WAIT，并非 MSL=60 秒再乘二。
- 应用优先复用连接；SO_REUSEADDR 只影响绑定规则，不删除活跃连接的 TIME_WAIT。不要在 Android 应用中把 tcp_tw_reuse 当可用优化接口。

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
// Client 应复用；execute() 示例必须从工作线程调用，非 2xx 也需显式处理。
val client = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .addInterceptor(LoggingInterceptor())
    .cache(Cache(File(cacheDir, "http_cache"), 10L * 1024 * 1024))
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

### 6.3 Android 17 局域网权限与证书配置

Android 17 上，**targetSdk ≥ 37** 的应用直接访问本地网络前，必须声明并运行时获得危险权限 `ACCESS_LOCAL_NETWORK`；它归入用户界面的 Nearby devices 权限组。**targetSdk ≤ 36** 且已有 `INTERNET` 的应用走 split permission 隐式授权，不要为低 target 添加或请求该新权限。Android 16 是通过 `RESTRICT_LOCAL_NETWORK` 显式 opt-in 的测试阶段，临时使用 `NEARBY_WIFI_DEVICES`，不能把这套测试授权方式当成 Android 17 的正式流程。

保护覆盖 Wi-Fi/Ethernet 等广播能力接口上的本地网络流量：TCP 主动连接和接受连接、UDP 单播/组播/广播的发送和接收，以及 `.local` 解析。Socket、OkHttp、Cronet、NsdManager 等上层 API 都不能绕过；WebView 继承宿主权限。蜂窝网络、公网访问不因此需要 LAN 权限；本地网络定义排除 VPN 接口，不能仅凭目标是私网 IP 就认定触发。 IPv4 范围含 `169.254.0.0/16`、`100.64.0.0/10`、`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`；IPv6 包括 link-local、直连路由、Thread 等 stub networks 和多子网场景，另含组播 `224.0.0.0/4`、`ff00::/8` 与广播 `255.255.255.255`。地址范围仍须结合上述接口定义。

例外是访问配置的本地 DNS 服务器的 53 端口，以及系统中介选择路径：Google Cast output switcher；mDNS 使用 `DiscoveryRequest.FLAG_SHOW_PICKER` 配合 `NsdManager.registerServiceInfoCallback()`，连接用户选择服务返回的地址无需广泛 LAN 授权。**普通 NsdManager 扫描并非一律豁免**，也不能把一个选中设备的授权扩展为整网扫描。

权限所属组之前已获授权时可能无需再次弹窗，但调用前仍检查权限；拒绝或撤销应停用相关功能、解释用途并提供用户主动重试入口，而不是循环弹窗。TCP 可能表现为超时，UDP 可能是 `EPERM`，不能把所有失败都归为权限错误。

```xml
<!-- 以下用于 targetSdk >= 37 且需要直接广泛 LAN 访问的应用 -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_LOCAL_NETWORK" />
```

```kotlin
// compileSdk 37；Activity 中使用 Activity Result API。
private val requestLan = registerForActivityResult(
    ActivityResultContracts.RequestPermission()
) { granted -> if (granted) connectSelectedDevice() else showLanPermissionDenied() }

fun onConnectClicked() {
    val needsLan = Build.VERSION.SDK_INT >= 37 && applicationInfo.targetSdkVersion >= 37
    val permission = Manifest.permission.ACCESS_LOCAL_NETWORK
    if (!needsLan || ContextCompat.checkSelfPermission(this, permission) ==
        PackageManager.PERMISSION_GRANTED) {
        connectSelectedDevice() // 网络工作不得同步阻塞主线程
    } else {
        requestLan.launch(permission)
    }
}
```

官方范围：[Local network permission](https://developer.android.com/privacy-and-security/local-network-permission)、[Local network definition](https://developer.android.com/privacy-and-security/local-network-definition)。固定 tag 证据：[AndroidManifest.xml](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/core/res/AndroidManifest.xml) 的危险权限声明；[platform.xml](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-17.0.0_r1/data/etc/platform.xml) 的 `INTERNET` → `ACCESS_LOCAL_NETWORK`、`targetSdk="37"` split；自编 ROM 还须核对 `access_local_network_permission_enabled`，不能将定制开关当作正式 Android 17 适用范围的替代描述。

HTTPS 配置应将企业 CA 限定到域名，debug-overrides 只信任调试 CA，不使用 trust-all。

AOSP `android-17.0.0_r1` 的真实路径是 **`external/conscrypt/nsc/src/android/security/net/config/RootTrustManager.java`**，包名仍是 `android.security.net.config`，不是旧 `frameworks/base` 路径，也不是 `com.android.org.conscrypt`。`checkServerTrusted(..., Socket/SSLEngine/hostname)` 从握手取得 host，调用 `ApplicationConfig.getConfigForHostname(host)`，再委托 `NetworkSecurityTrustManager` 完成链校验和配置 pin 检查。路径是固定版本源码证据，不是建议应用调用隐藏 API。见 [RootTrustManager.java](https://android.googlesource.com/platform/external/conscrypt/+/refs/tags/android-17.0.0_r1/nsc/src/android/security/net/config/RootTrustManager.java)。OkHttp 仍执行主机名验证；按域选择信任配置不等于自动替代所有客户端的主机名校验。

OkHttp 请求的取消必须传到 `Call.cancel()`，Response 必须在 `use` 中关闭；POST/支付请求必须由业务协议定义幂等键后才允许重试。


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
        val request = chain.request()
        val first = chain.proceed(request) // IOException 原样传播，不返回 response!!
        if (request.method != "GET" || first.code != 503 ||
            first.header("Retry-After") != "0" || chain.call().isCanceled()) return first
        first.close() // 再次 proceed 前关闭旧响应
        return chain.proceed(request) // 最多额外一次；最终响应归调用者关闭
    }
}
// 仅 addInterceptor；网络拦截器不能多次 proceed。
// 需要退避的重试放到上层可取消 delay，并限定幂等操作、次数和总预算。

// 3. 离线缓存
val cache = Cache(File(cacheDir, "http_cache"), 10L * 1024 * 1024)
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

```text
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
