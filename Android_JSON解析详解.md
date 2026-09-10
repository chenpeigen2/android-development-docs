# Android JSON 解析详解

> 适用环境：Android 17（API 37）；示例采用 Gson 2.10.1、Moshi 1.15.0 和各节标注的 Jackson 版本，三方解析器不属于 AOSP 平台版本。

> 作者：OpenClaw | 日期：2026-03-13

---

## 目录

- [1. 概述](#1-概述)
  - [1.1 JSON 是什么](#11-json-是什么)
  - [1.2 Android JSON 解析方案](#12-android-json-解析方案)
- [2. org.json 原生解析](#2-orgjson-原生解析)
  - [2.1 JSONObject 和 JSONArray](#21-jsonobject-和-jsonarray)
  - [2.2 解析 JSON 字符串](#22-解析-json-字符串)
  - [2.3 构建 JSON](#23-构建-json)
  - [2.4 遍历 JSON](#24-遍历-json)
  - [2.5 复杂 JSON 解析示例](#25-复杂-json-解析示例)
  - [2.6 org.json 工具类封装](#26-orgjson-工具类封装)
- [3. Gson 解析库](#3-gson-解析库)
  - [3.1 Gson 简介](#31-gson-简介)
  - [3.2 基本使用](#32-基本使用)
  - [3.3 注解详解](#33-注解详解)
  - [3.4 GsonBuilder 配置](#34-gsonbuilder-配置)
  - [3.5 泛型处理](#35-泛型处理)
  - [3.6 自定义序列化器](#36-自定义序列化器)
  - [3.7 处理复杂场景](#37-处理复杂场景)
  - [3.8 与 Retrofit 集成](#38-与-retrofit-集成)
- [4. Moshi 解析库](#4-moshi-解析库)
  - [4.1 Moshi 简介](#41-moshi-简介)
  - [4.2 基本使用](#42-基本使用)
  - [4.3 Kotlin 特性支持](#43-kotlin-特性支持)
  - [4.4 自定义适配器](#44-自定义适配器)
  - [4.5 Moshi 工具类](#45-moshi-工具类)
- [5. Jackson 解析库](#5-jackson-解析库)
  - [5.1 Jackson 简介](#51-jackson-简介)
  - [5.2 基本使用](#52-基本使用)
  - [5.3 注解](#53-注解)
- [6. 性能测量与选型](#6-性能测量与选型)
- [7. 最佳实践](#7-最佳实践)
  - [7.1 统一响应封装](#71-统一响应封装)
  - [7.2 错误处理](#72-错误处理)
  - [7.3 缓存适配器](#73-缓存适配器)
- [8. 常见问题](#8-常见问题)
- [9. 知识体系总结](#9-知识体系总结)
- [10. 严格的数据边界与生命周期](#10-严格的数据边界与生命周期)
  - [10.1 org.json：缺失、null 与类型转换](#101-orgjson缺失null-与类型转换)
  - [10.2 Moshi：代码生成和错误分类](#102-moshi代码生成和错误分类)
  - [10.3 泛型、R8 与适配器复用](#103-泛型r8-与适配器复用)
  - [10.4 有界输入与取消](#104-有界输入与取消)
  - [10.5 性能实验的可重复步骤](#105-性能实验的可重复步骤)

---

## 1. 概述

### 1.1 JSON 是什么

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         JSON 定义                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  JSON (JavaScript Object Notation)：
  ─────────────────────────────────────────────────────────────────────────
  - 轻量级数据交换格式
  - 易于阅读和编写
  - 易于机器解析和生成
  - 语言无关，跨平台

  数据类型：
  ─────────────────────────────────────────────────────────────────────────
  - 对象（Object）：{ "key": "value" }
  - 数组（Array）：[1, 2, 3]
  - 字符串（String）："hello"
  - 数字（Number）：123, 3.14
  - 布尔（Boolean）：true, false
  - 空值（null）：null

  JSON 示例：
  ─────────────────────────────────────────────────────────────────────────
  {
    "name": "张三",
    "age": 25,
    "isStudent": false,
    "hobbies": ["编程", "阅读"],
    "address": {
      "city": "北京",
      "zipCode": "100000"
    },
    "scores": null
  }
```

### 1.2 Android JSON 解析方案

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         JSON 解析方案对比                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┬──────────────┬──────────────┬──────────────────────────┐
  │      库           │   性能        │   易用性      │        特点              │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  org.json        │  中等         │  一般         │  Android 内置，无需依赖   │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  Gson            │  较快         │  优秀         │  Google 出品，功能强大    │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  Moshi           │  快           │  优秀         │  Square 出品，Kotlin 友好 │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  Jackson         │  最快         │  一般         │  功能最全，体积大         │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  kotlinx.serialization │ 快     │  优秀         │  Kotlin 官方，编译时生成  │
  └──────────────────┴──────────────┴──────────────┴──────────────────────────┘

  选择建议：
  ─────────────────────────────────────────────────────────────────────────
  - 简单场景：org.json（无额外依赖）
  - Java 项目：Gson（成熟稳定）
  - Kotlin 项目：Moshi 或 kotlinx.serialization
  - 高性能需求：Jackson
```

---

## 2. org.json 原生解析

### 2.1 JSONObject 和 JSONArray

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         org.json 核心类                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  JSONObject：
  ─────────────────────────────────────────────────────────────────────────
  - 表示 JSON 对象（键值对集合）
  - 类似 Map<String, Object>

  JSONArray：
  ─────────────────────────────────────────────────────────────────────────
  - 表示 JSON 数组（有序集合）
  - 类似 List<Object>

  JSONException：
  ─────────────────────────────────────────────────────────────────────────
  - 解析异常
  - 所有解析操作都可能抛出
```

### 2.2 解析 JSON 字符串

```kotlin
// ==================== 解析 JSON 对象 ====================
val jsonString = """
{
    "name": "张三",
    "age": 25,
    "isStudent": false,
    "score": 95.5,
    "hobbies": ["编程", "阅读", "游戏"],
    "address": {
        "city": "北京",
        "district": "朝阳区"
    }
}
"""

try {
    val jsonObject = JSONObject(jsonString)

    // 获取基本类型
    val name: String = jsonObject.getString("name")
    val age: Int = jsonObject.getInt("age")
    val isStudent: Boolean = jsonObject.getBoolean("isStudent")
    val score: Double = jsonObject.getDouble("score")

    // 可空获取（不存在返回默认值）
    val nickname: String = jsonObject.optString("nickname", "无昵称")
    val level: Int = jsonObject.optInt("level", 1)
    val vip: Boolean = jsonObject.optBoolean("vip", false)

    // 检查 key 是否存在
    if (jsonObject.has("address")) {
        val address: JSONObject = jsonObject.getJSONObject("address")
        val city: String = address.getString("city")
        val district: String = address.getString("district")
    }

    // 获取数组
    val hobbies: JSONArray = jsonObject.getJSONArray("hobbies")
    for (i in 0 until hobbies.length()) {
        val hobby: String = hobbies.getString(i)
        println("Hobby $i: $hobby")
    }

} catch (e: JSONException) {
    e.printStackTrace()
}

// ==================== 解析 JSON 数组 ====================
val jsonArrayString = """
[
    {"id": 1, "name": "张三"},
    {"id": 2, "name": "李四"},
    {"id": 3, "name": "王五"}
]
"""

try {
    val jsonArray = JSONArray(jsonArrayString)

    val users = mutableListOf<User>()
    for (i in 0 until jsonArray.length()) {
        val item: JSONObject = jsonArray.getJSONObject(i)
        val id: Int = item.getInt("id")
        val name: String = item.getString("name")
        users.add(User(id, name))
    }

} catch (e: JSONException) {
    e.printStackTrace()
}
```

### 2.3 构建 JSON

```kotlin
// ==================== 构建 JSONObject ====================
val jsonObject = JSONObject()
jsonObject.put("name", "张三")
jsonObject.put("age", 25)
jsonObject.put("isStudent", false)

// 嵌套对象
val address = JSONObject()
address.put("city", "北京")
address.put("district", "朝阳区")
jsonObject.put("address", address)

// 嵌套数组
val hobbies = JSONArray()
hobbies.put("编程")
hobbies.put("阅读")
hobbies.put("游戏")
jsonObject.put("hobbies", hobbies)

// 转为字符串
val jsonString: String = jsonObject.toString()
// 美化输出（带缩进）
val prettyString: String = jsonObject.toString(2)

// ==================== 构建 JSONArray ====================
val jsonArray = JSONArray()
jsonArray.put(1)
jsonArray.put("hello")
jsonArray.put(true)
jsonArray.put(null)

// 嵌套对象
val item = JSONObject()
item.put("id", 100)
item.put("name", "test")
jsonArray.put(item)

val arrayString: String = jsonArray.toString()
```

### 2.4 遍历 JSON

```kotlin
// ==================== 遍历 JSONObject ====================
val jsonObject = JSONObject(jsonString)

// 方式1：获取所有 key
val keys: Iterator<String> = jsonObject.keys()
while (keys.hasNext()) {
    val key = keys.next()
    val value = jsonObject.get(key)
    println("$key: $value (${value::class.simpleName})")
}

// 方式2：获取 key 的 JSONArray（用于遍历）
val names: JSONArray? = jsonObject.names()
names?.let {
    for (i in 0 until it.length()) {
        val key = it.getString(i)
        val value = jsonObject.get(key)
        println("$key: $value")
    }
}

// ==================== 遍历 JSONArray ====================
val jsonArray = JSONArray(jsonArrayString)

for (i in 0 until jsonArray.length()) {
    val item = jsonArray.get(i)
    when (item) {
        is JSONObject -> println("Object: ${item.toString()}")
        is JSONArray -> println("Array: ${item.toString()}")
        is String -> println("String: $item")
        is Int -> println("Int: $item")
        is Boolean -> println("Boolean: $item")
        JSONObject.NULL -> println("Null")
    }
}

// 使用 forEach（Kotlin 扩展）
jsonArray.forEach { item ->
    println(item)
}
```

### 2.5 复杂 JSON 解析示例

```kotlin
// ==================== 复杂 JSON 结构 ====================
val complexJson = """
{
    "code": 200,
    "message": "success",
    "data": {
        "user": {
            "id": 1001,
            "name": "张三",
            "avatar": "https://example.com/avatar.jpg",
            "vip": true
        },
        "orders": [
            {
                "orderId": "202401010001",
                "amount": 299.00,
                "status": 1,
                "items": [
                    {"name": "商品A", "price": 199.00, "count": 1},
                    {"name": "商品B", "price": 100.00, "count": 1}
                ]
            },
            {
                "orderId": "202401020001",
                "amount": 500.00,
                "status": 2,
                "items": [
                    {"name": "商品C", "price": 500.00, "count": 1}
                ]
            }
        ],
        "pagination": {
            "page": 1,
            "pageSize": 10,
            "total": 25
        }
    }
}
"""

// 解析
data class User(
    val id: Int,
    val name: String,
    val avatar: String,
    val vip: Boolean
)

data class OrderItem(
    val name: String,
    val price: Double,
    val count: Int
)

data class Order(
    val orderId: String,
    val amount: Double,
    val status: Int,
    val items: List<OrderItem>
)

data class Pagination(
    val page: Int,
    val pageSize: Int,
    val total: Int
)

data class ApiResponse(
    val code: Int,
    val message: String,
    val user: User?,
    val orders: List<Order>,
    val pagination: Pagination
)

fun parseApiResponse(jsonString: String): ApiResponse? {
    return try {
        val root = JSONObject(jsonString)
        val code = root.getInt("code")
        val message = root.getString("message")

        val data = root.getJSONObject("data")

        // 解析 user
        val userJson = data.optJSONObject("user")
        val user = userJson?.let {
            User(
                id = it.getInt("id"),
                name = it.getString("name"),
                avatar = it.getString("avatar"),
                vip = it.getBoolean("vip")
            )
        }

        // 解析 orders
        val ordersJson = data.getJSONArray("orders")
        val orders = mutableListOf<Order>()
        for (i in 0 until ordersJson.length()) {
            val orderJson = ordersJson.getJSONObject(i)
            val itemsJson = orderJson.getJSONArray("items")
            val items = mutableListOf<OrderItem>()

            for (j in 0 until itemsJson.length()) {
                val itemJson = itemsJson.getJSONObject(j)
                items.add(
                    OrderItem(
                        name = itemJson.getString("name"),
                        price = itemJson.getDouble("price"),
                        count = itemJson.getInt("count")
                    )
                )
            }

            orders.add(
                Order(
                    orderId = orderJson.getString("orderId"),
                    amount = orderJson.getDouble("amount"),
                    status = orderJson.getInt("status"),
                    items = items
                )
            )
        }

        // 解析 pagination
        val paginationJson = data.getJSONObject("pagination")
        val pagination = Pagination(
            page = paginationJson.getInt("page"),
            pageSize = paginationJson.getInt("pageSize"),
            total = paginationJson.getInt("total")
        )

        ApiResponse(code, message, user, orders, pagination)

    } catch (e: JSONException) {
        e.printStackTrace()
        null
    }
}
```

### 2.6 org.json 工具类封装

```kotlin
// ==================== JSON 解析工具类 ====================
object JsonUtils {

    /**
     * 安全获取 String
     */
    fun JSONObject.getStringOrNull(key: String): String? {
        return try {
            if (has(key)) getString(key) else null
        } catch (e: JSONException) {
            null
        }
    }

    /**
     * 安全获取 Int
     */
    fun JSONObject.getIntOrNull(key: String): Int? {
        return try {
            if (has(key)) getInt(key) else null
        } catch (e: JSONException) {
            null
        }
    }

    /**
     * 安全获取 Long
     */
    fun JSONObject.getLongOrNull(key: String): Long? {
        return try {
            if (has(key)) getLong(key) else null
        } catch (e: JSONException) {
            null
        }
    }

    /**
     * 安全获取 Double
     */
    fun JSONObject.getDoubleOrNull(key: String): Double? {
        return try {
            if (has(key)) getDouble(key) else null
        } catch (e: JSONException) {
            null
        }
    }

    /**
     * 安全获取 Boolean
     */
    fun JSONObject.getBooleanOrNull(key: String): Boolean? {
        return try {
            if (has(key)) getBoolean(key) else null
        } catch (e: JSONException) {
            null
        }
    }

    /**
     * 解析 JSON 数组到 List
     */
    inline fun <reified T> parseArray(
        jsonArray: JSONArray,
        parser: (JSONObject) -> T
    ): List<T> {
        val list = mutableListOf<T>()
        for (i in 0 until jsonArray.length()) {
            try {
                val item = jsonArray.getJSONObject(i)
                list.add(parser(item))
            } catch (e: JSONException) {
                e.printStackTrace()
            }
        }
        return list
    }

    /**
     * List 转 JSONArray
     */
    inline fun <reified T> List<T>.toJsonArray(
        converter: (T) -> JSONObject
    ): JSONArray {
        val jsonArray = JSONArray()
        forEach { item ->
            jsonArray.put(converter(item))
        }
        return jsonArray
    }
}

// 使用示例
val jsonObject = JSONObject(jsonString)
val name: String? = jsonObject.getStringOrNull("name")
val age: Int? = jsonObject.getIntOrNull("age")

val orders: List<Order> = JsonUtils.parseArray(jsonArray) { item ->
    Order(
        orderId = item.getString("orderId"),
        amount = item.getDouble("amount")
    )
}
```

---

## 3. Gson 解析库

### 3.1 Gson 简介

**模型与反射**：Gson 主要通过 Java 反射处理模型；开放式反射与 R8 优化存在冲突，Kotlin 非空类型及默认构造参数也不在它的语言保证内。`data class` 声明非空不能防止 Gson 反射写入 null。已有 Gson 工程应验证数据契约、泛型与 release 混淆，再决定保留或迁移；不能仅因 Android 17 就改所有 JSON 依赖号。

来源：[Gson 一手 README](https://github.com/google/gson/blob/main/README.md)、[Gson 故障排查](https://github.com/google/gson/blob/main/Troubleshooting.md)。以下示例固定使用 Gson 2.10.1；`Strictness.STRICT` 不属于该版本 API。

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Gson 简介                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  Gson 是 Google 提供的 Java JSON 序列化/反序列化库

  特点：
  ─────────────────────────────────────────────────────────────────────────
  - 简单易用，API 简洁
  - 支持复杂对象（嵌套、泛型、集合）
  - 支持自定义序列化/反序列化
  - 支持注解配置
  - 性能优秀

  依赖：
  ─────────────────────────────────────────────────────────────────────────
  implementation("com.google.code.gson:gson:2.10.1")
```

### 3.2 基本使用

```kotlin
// ==================== 基本序列化 ====================
val gson = Gson()

// 对象 -> JSON
val user = User(1, "张三", 25)
val jsonString: String = gson.toJson(user)
// {"id":1,"name":"张三","age":25}

// JSON -> 对象
val userFromJson: User = gson.fromJson(jsonString, User::class.java)

// ==================== 集合序列化 ====================
// List -> JSON
val users = listOf(
    User(1, "张三", 25),
    User(2, "李四", 30)
)
val listJson: String = gson.toJson(users)

// JSON -> List（需要 TypeToken）
val type = object : TypeToken<List<User>>() {}.type
val usersFromJson: List<User> = gson.fromJson(listJson, type)

// Map -> JSON
val map = mapOf(
    "key1" to "value1",
    "key2" to "value2"
)
val mapJson: String = gson.toJson(map)

// JSON -> Map
val mapType = object : TypeToken<Map<String, String>>() {}.type
val mapFromJson: Map<String, String> = gson.fromJson(mapJson, mapType)

// ==================== 基本类型 ====================
val intJson: String = gson.toJson(123)       // "123"
val stringJson: String = gson.toJson("hello") // "\"hello\""
val booleanJson: String = gson.toJson(true)   // "true"

val number: Int = gson.fromJson("123", Int::class.java)
val text: String = gson.fromJson("\"hello\"", String::class.java)
```

### 3.3 注解详解

```kotlin
// ==================== @SerializedName 字段重命名 ====================
data class User(
    @SerializedName("user_id")
    val id: Int,

    @SerializedName("user_name")
    val name: String,

    // 多个别名（解析时按顺序匹配）
    @SerializedName(value = "user_age", alternate = ["age", "userAge"])
    val age: Int
)

// JSON: {"user_id": 1, "user_name": "张三", "age": 25}
// 可以正确解析

// ==================== @Expose 字段暴露控制 ====================
data class User(
    @Expose val id: Int,           // 序列化和反序列化都包含
    @Expose(serialize = true, deserialize = true) val name: String,
    @Expose(serialize = false) val password: String,  // 不序列化（不输出到 JSON）
    @Expose(deserialize = false) val createdAt: Long, // 不反序列化（不读取）
    val internalData: String       // 默认不包含（没有 @Expose）
)

// 使用 excludeFieldsWithoutExposeAnnotation() 启用
val gson = GsonBuilder()
    .excludeFieldsWithoutExposeAnnotation()
    .create()

// ==================== @Since 和 @Until 版本控制 ====================
data class User(
    @Since(1.0) val id: Int,
    @Since(2.0) val name: String,
    @Until(3.0) val legacyField: String
)

// 设置版本
val gson = GsonBuilder()
    .setVersion(2.0)  // 只包含 @Since <= 2.0 且 @Until > 2.0 的字段
    .create()

// ==================== transient 关键字 ====================
data class User(
    val id: Int,
    val name: String,
    @Transient val temporaryData: String  // 完全忽略，等同于没有 @Expose
)
```

### 3.4 GsonBuilder 配置

不要把所有选项串联成一份“推荐配置”：`excludeFieldsWithoutExposeAnnotation()` 会排除没有 `@Expose` 的字段；自定义命名策略会替代此前策略；`generateNonExecutableJson()` 会改变输出格式，不是通用 XSS 防护。宽松解析也不是网络输入的默认安全建议。

```kotlin
// 最小示例：只按协议需要显式输出 null；不默认启用 lenient 或特殊前缀。
val gson = GsonBuilder()
    .serializeNulls()
    .create()
```

去掉 `setLenient()` 不等于 Gson 2.10.1 已严格拒绝所有非标准 JSON。Gson **2.11.0+** 才提供 `Strictness.STRICT` 配置；如要采用，须先按发布说明升级并回归，不能直接复制到本文的 2.10.1 依赖上。日期、枚举未知值、缺失字段/null、数值溢出和最大输入大小都应按业务协议测试。

来源：[Gson Troubleshooting 的 malformed JSON/Strictness 说明](https://github.com/google/gson/blob/main/Troubleshooting.md)、[Gson 用户指南](https://github.com/google/gson/blob/main/UserGuide.md)。

### 3.5 泛型处理

公共 `inline` 不能访问对象的 `private` 字段；下面将共享 Gson 标成 `@PublishedApi internal`，以满足 Kotlin 公共内联函数的可见性要求。内联泛型用 `TypeToken<List<T>>` 保留嵌套类型；`T::class.java` 只保留原始 Class，会丢失 `List<User>` 等类型参数。允许 JSON `null` 的入口必须返回可空结果；声明非空时应显式校验。

来源：[Kotlin public inline 限制](https://kotlinlang.org/docs/inline-functions.html#restrictions-for-public-api-inline-functions)、[Gson TypeToken 排查](https://github.com/google/gson/blob/main/Troubleshooting.md)。

```kotlin
// ==================== 泛型类解析 ====================
// 通用 API 响应
data class ApiResponse<T>(
    val code: Int,
    val message: String,
    val data: T?
)

// 解析泛型响应
inline fun <reified T> parseApiResponse(jsonString: String): ApiResponse<T> {
    val gson = Gson()
    val type = object : TypeToken<ApiResponse<T>>() {}.type
    return requireNotNull(gson.fromJson<ApiResponse<T>>(jsonString, type)) {
        "Response must not be JSON null"
    }
}

// 使用
val response: ApiResponse<User> = parseApiResponse(jsonString)

// ==================== 泛型工具类 ====================
object GsonUtils {
    @PublishedApi
    internal val gson = GsonBuilder()
        .setPrettyPrinting()
        .serializeNulls()
        .setDateFormat("yyyy-MM-dd HH:mm:ss")
        .create()

    fun <T> fromJson(json: String, clazz: Class<T>): T? {
        return gson.fromJson(json, clazz)
    }

    inline fun <reified T> fromJson(json: String): T? {
        return gson.fromJson(json, object : TypeToken<T>() {}.type)
    }

    fun <T> fromJson(json: String, type: Type): T? {
        return gson.fromJson(json, type)
    }

    fun <T> toJson(obj: T): String {
        return gson.toJson(obj)
    }

    fun <T> toJson(obj: T, type: Type): String {
        return gson.toJson(obj, type)
    }

    // List 解析
    inline fun <reified T> fromJsonList(json: String): List<T>? {
        val type = object : TypeToken<List<T>>() {}.type
        return gson.fromJson(json, type)
    }
}

// 使用
val user = GsonUtils.fromJson<User>(jsonString)
val users = GsonUtils.fromJsonList<User>(jsonArrayString)
```

### 3.6 自定义序列化器

```kotlin
// ==================== 自定义 JsonSerializer ====================
// 日期序列化器
class DateSerializer : JsonSerializer<Date> {
    override fun serialize(
        src: Date,
        typeOfSrc: Type,
        context: JsonSerializationContext
    ): JsonElement {
        return JsonPrimitive(src.time)  // 转为时间戳
    }
}

// 自定义对象序列化
class UserSerializer : JsonSerializer<User> {
    override fun serialize(
        src: User,
        typeOfSrc: Type,
        context: JsonSerializationContext
    ): JsonElement {
        val jsonObject = JsonObject()
        jsonObject.addProperty("id", src.id)
        jsonObject.addProperty("name", src.name)
        jsonObject.addProperty("displayName", src.name.uppercase())  // 自定义逻辑
        jsonObject.addProperty("age", src.age)
        return jsonObject
    }
}

// ==================== 自定义 JsonDeserializer ====================
// 日期反序列化器
class DateDeserializer : JsonDeserializer<Date> {
    override fun deserialize(
        json: JsonElement,
        typeOfT: Type,
        context: JsonDeserializationContext
    ): Date {
        return try {
            // 支持多种格式
            when {
                json.isJsonPrimitive && json.asJsonPrimitive.isNumber -> {
                    Date(json.asLong)
                }
                json.isJsonPrimitive && json.asJsonPrimitive.isString -> {
                    val format = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
                    format.parse(json.asString) ?: Date()
                }
                else -> Date()
            }
        } catch (e: Exception) {
            Date()
        }
    }
}

// 自定义对象反序列化
class UserDeserializer : JsonDeserializer<User> {
    override fun deserialize(
        json: JsonElement,
        typeOfT: Type,
        context: JsonDeserializationContext
    ): User {
        val jsonObject = json.asJsonObject
        return User(
            id = jsonObject.get("id").asInt,
            name = jsonObject.get("name").asString,
            age = jsonObject.get("age")?.asInt ?: 0
        )
    }
}

// ==================== 注册序列化器 ====================
val gson = GsonBuilder()
    .registerTypeAdapter(Date::class.java, DateSerializer())
    .registerTypeAdapter(Date::class.java, DateDeserializer())
    .registerTypeAdapter(User::class.java, UserSerializer())
    .registerTypeAdapter(User::class.java, UserDeserializer())
    .create()

// 或使用 TypeAdapter（更高效）
class DateTypeAdapter : TypeAdapter<Date>() {
    override fun write(out: JsonWriter, value: Date?) {
        out.value(value?.time)
    }

    override fun read(reader: JsonReader): Date? {
        return try {
            if (reader.peek() == JsonToken.NULL) {
                reader.nextNull()
                null
            } else {
                Date(reader.nextLong())
            }
        } catch (e: Exception) {
            null
        }
    }
}

val gson = GsonBuilder()
    .registerTypeAdapter(Date::class.java, DateTypeAdapter())
    .create()
```

### 3.7 处理复杂场景

```kotlin
// ==================== 处理 null 和默认值 ====================
data class User(
    val id: Int = 0,
    val name: String = "",
    val age: Int = 0,
    val email: String? = null
)

// Gson 默认行为：
// - 不存在的字段：使用默认值
// - null 值：使用 null（不设置 serializeNulls 时序列化会跳过）

// ==================== 处理枚举 ====================
@JsonClass(generateAdapter = false) // 按 Moshi 文档保护反射枚举在 R8 下的语义
enum class Status {
    @SerializedName("pending")
    PENDING,

    @SerializedName("processing")
    PROCESSING,

    @SerializedName("completed")
    COMPLETED,

    @SerializedName("failed")
    FAILED
}

data class Order(
    val id: String,
    val status: Status
)

// ==================== 处理嵌套泛型 ====================
data class PageResponse<T>(
    val page: Int,
    val pageSize: Int,
    val total: Int,
    val list: List<T>
)

// 解析嵌套泛型
inline fun <reified T> parsePageResponse(json: String): PageResponse<T> {
    val gson = Gson()
    val listType = TypeToken.getParameterized(List::class.java, T::class.java).type
    val type = TypeToken.getParameterized(PageResponse::class.java, listType).type
    return gson.fromJson(json, type)
}

// ==================== 处理动态类型 ====================
// JSON 中某个字段可能是不同类型
data class Message(
    val type: String,
    val content: JsonElement  // 动态内容
)

fun parseMessage(json: String) {
    val message = Gson().fromJson(json, Message::class.java)

    when (message.type) {
        "text" -> {
            val text = message.content.asString
        }
        "image" -> {
            val image = Gson().fromJson(message.content, ImageContent::class.java)
        }
        "video" -> {
            val video = Gson().fromJson(message.content, VideoContent::class.java)
        }
    }
}

// ==================== 处理多态 ====================
sealed class Content {
    data class TextContent(val text: String) : Content()
    data class ImageContent(val url: String, val width: Int, val height: Int) : Content()
    data class VideoContent(val url: String, val duration: Int) : Content()
}

// 使用显式白名单反序列化器，不加载服务端提供的 JVM 类名。
class ContentDeserializer : JsonDeserializer<Content> {
    override fun deserialize(json: JsonElement, typeOfT: Type,
                             context: JsonDeserializationContext): Content {
        if (!json.isJsonObject) throw JsonParseException("content 必须是对象")
        val obj = json.asJsonObject
        fun text(key: String): String {
            val value = obj[key]
            if (value == null || !value.isJsonPrimitive || !value.asJsonPrimitive.isString)
                throw JsonParseException("$key 必须为字符串")
            return value.asString
        }
        fun number(key: String): Int {
            val value = obj[key]
            if (value == null || !value.isJsonPrimitive || !value.asJsonPrimitive.isNumber)
                throw JsonParseException("$key 必须为整数")
            val result = try { value.asBigDecimal.intValueExact() }
                catch (error: ArithmeticException) { throw JsonParseException("$key 超出整数范围", error) }
            if (result < 0) throw JsonParseException("$key 不可为负数")
            return result
        }
        return when (val type = text("type")) {
            "text" -> Content.TextContent(text("text"))
            "image" -> Content.ImageContent(text("url"), number("width"), number("height"))
            "video" -> Content.VideoContent(text("url"), number("duration"))
            else -> throw JsonParseException("未知 content 类型: $type")
        }
    }
}
val contentGson = GsonBuilder()
    .registerTypeAdapter(Content::class.java, ContentDeserializer())
    .create()
val content = requireNotNull(contentGson.fromJson<Content>(
    """{"type":"image","url":"https://example.com/a.png","width":64,"height":64}""",
    Content::class.java
))
```

本例限定反序列化。双向协议还需实现 serializer，显式写回 type 判别字段，不能依赖运行时子类默认序列化自动补出 type。Gson extras 的 RuntimeTypeAdapterFactory 不随 core 发布；使用 core 的公开接口即可实现自己的协议映射。

源码：[Gson 2.10.1 JsonDeserializer](https://github.com/google/gson/blob/gson-parent-2.10.1/gson/src/main/java/com/google/gson/JsonDeserializer.java)。

### 3.8 与 Retrofit 集成

```kotlin
// ==================== GsonConverterFactory ====================
val gson = GsonBuilder()
    .setDateFormat("yyyy-MM-dd HH:mm:ss")
    .registerTypeAdapter(Date::class.java, DateTypeAdapter())
    .create()

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create(gson))
    .build()

// ==================== 统一响应处理 ====================
data class BaseResponse<T>(
    val code: Int,
    val message: String,
    val data: T?
)

sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
}

suspend fun <T : Any> safeApiCall(call: suspend () -> Response<BaseResponse<T>>): ApiResult<T> {
    return try {
        val response = call()
        if (!response.isSuccessful) {
            response.errorBody()?.close()
            ApiResult.Error(response.code(), "HTTP 请求失败")
        } else {
            val body = response.body()
            val data = body?.data
            when {
                body == null -> ApiResult.Error(-2, "空响应")
                body.code != 200 -> ApiResult.Error(body.code, "业务请求失败")
                data == null -> ApiResult.Error(-2, "缺少响应数据")
                else -> ApiResult.Success(data)
            }
        }
    } catch (cancelled: kotlinx.coroutines.CancellationException) {
        throw cancelled
    } catch (invalid: JsonParseException) {
        ApiResult.Error(-2, "响应格式错误")
    } catch (network: java.io.IOException) {
        ApiResult.Error(-1, "网络请求失败")
    }
}
```

---

## 4. Moshi 解析库

### 4.1 Moshi 简介

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Moshi 简介                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  Moshi 是 Square 出品的 JSON 解析库，专为 Kotlin 优化

  特点：
  ─────────────────────────────────────────────────────────────────────────
  - Kotlin 友好（支持 data class、可空类型、默认参数）
  - 编译时代码生成（Kotlin 资源占用更少）
  - 更好的错误信息
  - 更小的体积
  - Okio 集成

  依赖：
  ─────────────────────────────────────────────────────────────────────────
  implementation("com.squareup.moshi:moshi:1.15.0")
  ksp("com.squareup.moshi:moshi-kotlin-codegen:1.15.0")
```

### 4.2 基本使用

`@JsonClass(generateAdapter = true)` 需要真正运行匹配版本的 codegen；仅添加 `moshi` runtime 不会自动生成适配器。KSP 插件版本必须在工程中显式配置并与 Kotlin/AGP 兼容，不能从 Android 17 推导。对未生成适配器的 Kotlin 类，普通 Java 反射不受支持，需 `moshi-kotlin` 与 `KotlinJsonAdapterFactory`，或补充 codegen 注解。

```kotlin
// 仅选择 Kotlin 反射方案时补充；与本文 1.15.0 runtime 保持一致。
implementation("com.squareup.moshi:moshi-kotlin:1.15.0")
// KotlinJsonAdapterFactory 位于 com.squareup.moshi.kotlin.reflect 包。
```

来源：[Moshi Kotlin/codegen 与反射说明](https://github.com/square/moshi/blob/parent-1.15.0/README.md)。后文带 `KotlinJsonAdapterFactory` 的示例同样需要此依赖，不是 core 的免费内置能力。

```kotlin
// ==================== 添加注解 ====================
@JsonClass(generateAdapter = true)
data class User(
    @Json(name = "user_id") val id: Int,
    @Json(name = "user_name") val name: String,
    val age: Int
)

// ==================== 基本 API ====================
val moshi = Moshi.Builder().build()

// 对象 -> JSON
val adapter: JsonAdapter<User> = moshi.adapter(User::class.java)
val user = User(1, "张三", 25)

val jsonString: String = adapter.toJson(user)
// {"user_id":1,"user_name":"张三","age":25}

// JSON -> 对象
val userFromJson: User? = adapter.fromJson(jsonString)

// ==================== 集合解析 ====================
// List
val listType = Types.newParameterizedType(List::class.java, User::class.java)
val listAdapter: JsonAdapter<List<User>> = moshi.adapter(listType)

val users = listOf(User(1, "张三", 25), User(2, "李四", 30))
val listJson: String = listAdapter.toJson(users)
val usersFromJson: List<User>? = listAdapter.fromJson(listJson)

// Map
val mapType = Types.newParameterizedType(
    Map::class.java,
    String::class.java,
    User::class.java
)
val mapAdapter: JsonAdapter<Map<String, User>> = moshi.adapter(mapType)
```

### 4.3 Kotlin 特性支持

```kotlin
// ==================== 可空类型和默认值 ====================
@JsonClass(generateAdapter = true)
data class User(
    val id: Int,
    val name: String,
    val nickname: String? = null,      // 可空，JSON 中不存在时为 null
    val age: Int = 0,                  // 默认值
    val email: String = "",            // 默认值
    val tags: List<String> = emptyList()  // 集合默认值
)

// Moshi 会正确处理：
// - JSON 中不存在的字段使用默认值
// - null 值正确赋给可空类型

// ==================== 枚举 ====================
@JsonClass(generateAdapter = true)
data class Order(
    val id: String,
    val status: Status
)

@JsonClass(generateAdapter = false) // 按 Moshi 文档保护反射枚举在 R8 下的语义
enum class Status {
    @Json(name = "pending") PENDING,
    @Json(name = "processing") PROCESSING,
    @Json(name = "completed") COMPLETED,
    @Json(name = "failed") FAILED
}

// ==================== 嵌套对象 ====================
@JsonClass(generateAdapter = true)
data class Address(
    val city: String,
    val district: String
)

@JsonClass(generateAdapter = true)
data class User(
    val id: Int,
    val name: String,
    val address: Address?  // 嵌套对象
)
```

### 4.4 自定义适配器

```kotlin
// ==================== 自定义 JsonAdapter ====================
class DateAdapter {
    @ToJson
    fun toJson(writer: JsonWriter, value: Date?) {
        writer.value(value?.time)
    }

    @FromJson
    fun fromJson(reader: JsonReader): Date? {
        return if (reader.peek() == JsonReader.Token.NULL) {
            reader.nextNull()
            null
        } else {
            Date(reader.nextLong())
        }
    }
}

// 注册适配器
val moshi = Moshi.Builder()
    .add(DateAdapter())
    .build()

// ==================== 自定义枚举适配器 ====================
class StatusAdapter {
    @FromJson
    fun fromJson(status: String): Status {
        return when (status.lowercase()) {
            "pending" -> Status.PENDING
            "processing" -> Status.PROCESSING
            "completed" -> Status.COMPLETED
            "failed" -> Status.FAILED
            else -> throw JsonDataException("Unknown status: $status")
        }
    }

    @ToJson
    fun toJson(status: Status): String {
        return status.name.lowercase()
    }
}

// ==================== 使用 @ToJson/@FromJson 注解 ====================
class UserAdapter {
    @FromJson
    fun fromJson(json: UserJson): User {
        return User(
            id = json.userId,
            name = json.userName,
            age = json.userAge
        )
    }

    @ToJson
    fun toJson(user: User): UserJson {
        return UserJson(
            userId = user.id,
            userName = user.name,
            userAge = user.age
        )
    }
}
```

### 4.5 Moshi 工具类

```kotlin
// ==================== Moshi 工具类 ====================
object MoshiUtils {

    private val moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())  // Kotlin 支持
        .add(DateAdapter())
        .build()

    inline fun <reified T> fromJson(json: String): T? {
        val adapter = moshi.adapter(T::class.java)
        return adapter.fromJson(json)
    }

    inline fun <reified T> toJson(obj: T): String {
        val adapter = moshi.adapter(T::class.java)
        return adapter.toJson(obj) ?: "{}"
    }

    inline fun <reified T> fromJsonList(json: String): List<T>? {
        val listType = Types.newParameterizedType(List::class.java, T::class.java)
        val adapter = moshi.adapter<List<T>>(listType)
        return adapter.fromJson(json)
    }
}

// ==================== 与 Retrofit 集成 ====================
val moshi = Moshi.Builder()
    .add(KotlinJsonAdapterFactory())
    .build()

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(MoshiConverterFactory.create(moshi))
    .build()
```

---

## 5. Jackson 解析库

### 5.1 Jackson 简介

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Jackson 简介                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  Jackson 是 Java 生态最成熟的 JSON 库，性能最优

  特点：
  ─────────────────────────────────────────────────────────────────────────
  - 性能最高（流式解析）
  - 功能最全
  - 支持多种数据格式（JSON/XML/YAML等）
  - 体积较大

  依赖：
  ─────────────────────────────────────────────────────────────────────────
  implementation("com.fasterxml.jackson.core:jackson-databind:2.16.0")
  implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.16.0")
```

### 5.2 基本使用

```kotlin
// ==================== ObjectMapper ====================
val mapper = ObjectMapper()
    .registerModule(KotlinModule())  // Kotlin 支持
    .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)  // 忽略未知属性
    .setSerializationInclusion(JsonInclude.Include.NON_NULL)  // 不序列化 null

// 对象 -> JSON
val user = User(1, "张三", 25)
val jsonString: String = mapper.writeValueAsString(user)
// 美化输出
val prettyString: String = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(user)

// JSON -> 对象
val userFromJson: User = mapper.readValue(jsonString, User::class.java)

// ==================== 集合解析 ====================
// List
val users = listOf(User(1, "张三", 25), User(2, "李四", 30))
val listJson: String = mapper.writeValueAsString(users)

val typeFactory = mapper.typeFactory
val listType = typeFactory.constructCollectionType(List::class.java, User::class.java)
val usersFromJson: List<User> = mapper.readValue(listJson, listType)

// Map
val mapType = typeFactory.constructMapType(Map::class.java, String::class.java, User::class.java)
val mapFromJson: Map<String, User> = mapper.readValue(mapJson, mapType)
```

### 5.3 注解

```kotlin
// ==================== 常用注解 ====================
data class User(
    @JsonProperty("user_id")
    val id: Int,

    @JsonProperty("user_name")
    val name: String,

    @JsonIgnore
    val password: String,  // 忽略此字段

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    val createdAt: Date? = null,

    @JsonInclude(JsonInclude.Include.NON_NULL)
    val email: String? = null,  // null 时不序列化

    @JsonAlias(["age", "userAge"])
    val userAge: Int = 0  // 别名
)
```

---

## 6. 性能测量与选型

解析性能取决于模型结构、输入大小、分配量、适配器缓存、设备和构建配置。比较前先固定数据契约，再测冷启动与稳态解析。

| 对比维度 | 必须统一的条件 |
|----------|----------------|
| 解析/序列化耗时 | 相同 JSON、模型、缺失字段策略、冷热适配器及线程 |
| 内存与分配 | 流式/树模型/对象映射分开测，记录峰值与 GC |
| APK 成本 | 使用相同 release/R8 配置，计算传递依赖和生成代码，不只看单个 JAR |
| 正确性 | 泛型、null、默认值、未知枚举、数字范围和错误输入 |

对已有 Java/Gson 业务可先审计再迁移；新 Android/Kotlin 模型可评估 Moshi codegen 或 Kotlin Serialization，不能预先宣布某库最快。`org.json` 可减少额外依赖，但仍需手工维护字段契约。Android 17 平台更新不会自动改变三方库的序列化协议。

来源：[Gson Android/Kotlin 限制](https://github.com/google/gson/blob/main/README.md)、[Moshi 代码生成](https://github.com/square/moshi/blob/parent-1.15.0/README.md)、[Android Microbenchmark](https://developer.android.com/topic/performance/benchmarking/microbenchmark-overview)。

---

## 7. 最佳实践

### 7.1 统一响应封装

```kotlin
// ==================== 通用响应模型 ====================
data class ApiResponse<T>(
    val code: Int,
    val message: String,
    val data: T?
) {
    val isSuccess: Boolean get() = code == 200

    fun getDataOrThrow(): T {
        if (!isSuccess) throw ApiException(code, message)
        return data ?: throw ApiException(-1, "Data is null")
    }
}

class ApiException(val code: Int, override val message: String) : Exception(message)

// ==================== 使用 Gson ====================
inline fun <reified T> parseResponse(json: String): ApiResponse<T> {
    val type = object : TypeToken<ApiResponse<T>>() {}.type
    return requireNotNull(Gson().fromJson<ApiResponse<T>>(json, type)) {
        "Response must not be JSON null"
    }
}

// ==================== 使用 Moshi ====================
// dataType 必须包含完整泛型，如 Types.newParameterizedType(List::class.java, User::class.java)。
// 依赖 moshi-kotlin；Type 是 java.lang.reflect.Type。
fun <T> parseResponseMoshi(json: String, dataType: Type): ApiResponse<T>? {
    val moshi = Moshi.Builder().addLast(KotlinJsonAdapterFactory()).build()
    val type = Types.newParameterizedType(ApiResponse::class.java, dataType)
    return moshi.adapter<ApiResponse<T>>(type).fromJson(json)
}
```

### 7.2 错误处理

```kotlin
// ==================== 安全解析 ====================
inline fun <reified T : Any> safeParseJson(json: String): Result<T> {
    return try {
        val type = object : TypeToken<T>() {}.type
        val obj = GsonUtils.gson.fromJson<T>(json, type)
        Result.success(requireNotNull(obj) { "JSON null is not allowed here" })
    } catch (e: JsonParseException) {
        Result.failure(IllegalArgumentException("JSON parse failed", e))
    } catch (e: IllegalArgumentException) {
        Result.failure(e)
    }
}

// 使用
val result = safeParseJson<User>(jsonString)
result.onSuccess { user ->
    // 处理成功
}.onFailure { error ->
    // 处理失败
}
```

### 7.3 缓存适配器

```kotlin
// Gson 和 Moshi 自身会缓存适配器；复用配置完成的实例即可。
object GsonFactory {
    private val gson = GsonBuilder()
        .setDateFormat("yyyy-MM-dd HH:mm:ss")
        .create()

    fun <T> getAdapter(type: TypeToken<T>): TypeAdapter<T> = gson.getAdapter(type)
}

object MoshiFactory {
    private val moshi = Moshi.Builder()
        .addLast(KotlinJsonAdapterFactory())
        .build()

    fun <T> getAdapter(type: Type): JsonAdapter<T> = moshi.adapter(type)
}
// Type/TypeToken 携带完整泛型；不使用无锁 mutableMapOf 跨线程建缓存。
// 自定义 TypeAdapter/JsonAdapter 仍需遵守自身的线程安全契约。
```

源码：[Gson 2.10.1 `Gson.getAdapter`](https://github.com/google/gson/blob/gson-parent-2.10.1/gson/src/main/java/com/google/gson/Gson.java)、[Moshi 1.15.0 `Moshi.adapter`](https://github.com/square/moshi/blob/parent-1.15.0/moshi/src/main/java/com/squareup/moshi/Moshi.java)。

---

## 8. 常见问题

```text
Q1: Gson 和 Moshi 怎么选？
─────────────────────────────────────────────────────────────────────────
A:
   - 现有 Gson：先审计 Kotlin/null/泛型及 R8，再决定是否迁移
   - Kotlin 新项目：评估 Moshi codegen / Kotlin Serialization，性能需实测
   - 需要 Kotlin 特性支持（可空、默认值）：Moshi 更好

Q2: 如何处理 JSON 字段名和类字段名不一致？
─────────────────────────────────────────────────────────────────────────
A: 使用注解
   - Gson：@SerializedName("json_field_name")
   - Moshi：@Json(name = "json_field_name")
   - Jackson：@JsonProperty("json_field_name")

Q3: 解析时如何忽略未知字段？
─────────────────────────────────────────────────────────────────────────
A:
   - Gson：默认忽略
   - Moshi：默认忽略
   - Jackson：mapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)

Q4: 如何处理日期格式？
─────────────────────────────────────────────────────────────────────────
A:
   - Gson：GsonBuilder().setDateFormat("yyyy-MM-dd HH:mm:ss")
   - Moshi：自定义 DateAdapter
   - Jackson：@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")

Q5: 解析泛型 List<T> 怎么做？
─────────────────────────────────────────────────────────────────────────
A:
   - Gson：TypeToken.getParameterized(List::class.java, T::class.java).type
   - Moshi：Types.newParameterizedType(List::class.java, T::class.java)

Q6: 如何处理 null 值？
─────────────────────────────────────────────────────────────────────────
A:
   - Gson：
     - 默认不序列化 null
     - serializeNulls() 开启 null 序列化
   - Moshi：
     - 正确处理可空类型
     - 使用默认值处理缺失字段

Q7: 性能优化建议？
─────────────────────────────────────────────────────────────────────────
A:
   1. 复用 Gson/Moshi 实例（不要每次创建）
   2. 缓存 JsonAdapter/TypeToken
   3. 大数据量考虑 Jackson 流式解析
   4. 使用编译时代码生成（Moshi codegen）
   5. 避免复杂的自定义序列化器
```

---

## 9. 知识体系总结

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         JSON 解析知识体系                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────────┐
                           │   JSON 解析     │
                           └────────┬────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
  ┌───────────┐              ┌───────────┐              ┌───────────┐
  │  org.json │              │   Gson    │              │   Moshi   │
  │           │              │           │              │           │
  │ 内置库    │              │ Google    │              │ Square    │
  │ 手动解析  │              │ 反射      │              │ 编译生成  │
  │ 无依赖    │              │ 功能全    │              │ Kotlin好  │
  └───────────┘              └───────────┘              └───────────┘

  核心要点：
  ─────────────────────────────────────────────────────────────────────────
  1. org.json：Android 内置，简单场景无需额外依赖
  2. Gson：成熟稳定，Java 项目首选
  3. Moshi：Kotlin 友好，新项目推荐
  4. Jackson：可评估流式解析；性能由业务样本与设备决定
  5. 复用实例，缓存适配器，优化性能
```

---

> 作者：OpenClaw | 日期：2026-03-13

## 10. 严格的数据边界与生命周期

### 10.1 org.json：缺失、null 与类型转换

Android 平台 `org.json` 的实现位于 AOSP `libcore/json/src/main/java/org/json/`。`has(name)` 判断成员是否存在；`isNull(name)` 对缺失成员和 JSON null 都返回 true。`getString` 等方法可能进行类型转换，因此“调用未抛异常”不等于满足业务 schema。

```kotlin
import org.json.JSONObject
import org.json.JSONException

data class Account(val id: String, val nickname: String?)
fun parseAccount(json: String): Account {
    val obj = JSONObject(json)
    if (!obj.has("id") || obj.isNull("id")) throw JSONException("缺少 id")
    val rawId = obj.get("id")
    if (rawId !is String || rawId.isBlank()) throw JSONException("id 必须为非空字符串")
    val nickname = if (!obj.has("nickname") || obj.isNull("nickname")) null else {
        obj.get("nickname") as? String ?: throw JSONException("nickname 类型错误")
    }
    return Account(rawId, nickname)
}
```

上述模型有意把缺失 nickname 与显式 null 合并。如果 PATCH 协议区分“未修改”和“清空”，则用三态模型 Missing/Null/Value，不能压缩成一个 nullable 字段。

源码：[AOSP Android 17 JSONObject.java](https://android.googlesource.com/platform/libcore/+/refs/tags/android-17.0.0_r1/json/src/main/java/org/json/JSONObject.java)。

### 10.2 Moshi：代码生成和错误分类

Moshi 1.15.0 的 Kotlin 类可以使用 `moshi-kotlin-codegen` 生成适配器，也可以使用 `moshi-kotlin` 的 KotlinJsonAdapterFactory。两种方案择一配置；下面选反射路径，不要求示例工程额外运行 KSP。

```kotlin
// dependencies：moshi:1.15.0 与 moshi-kotlin:1.15.0
import com.squareup.moshi.JsonDataException
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory

data class ProductDto(val id: String, val title: String, val stock: Int = 0)
val productMoshi = Moshi.Builder().addLast(KotlinJsonAdapterFactory()).build()
val productAdapter = productMoshi.adapter(ProductDto::class.java).nonNull()

fun parseProduct(input: String): ProductDto {
    val product = requireNotNull(productAdapter.fromJson(input))
    if (product.id.isBlank() || product.stock < 0) throw JsonDataException("商品字段不合法")
    return product
}
```

缺失 stock 使用默认值，显式 `"stock":null` 则违反非空契约。`JsonDataException` 表示结构/类型不符合模型，`IOException` 表示读取或 JSON 编码问题。两类错误都不能直接用空商品掩盖；UI 应显示协议异常或失败重试状态。`failOnUnknown()` 可用于严格内部协议测试，开放服务端协议则要权衡新增字段的向前兼容。

参考：[Moshi 1.15.0 发布源码](https://github.com/square/moshi/tree/parent-1.15.0)、[Moshi 官方使用说明](https://github.com/square/moshi)。

### 10.3 泛型、R8 与适配器复用

`List<User>` 需要包含类型参数的 Type；`List::class.java` 只能提供原始类型。公共 inline 封装使用 `@PublishedApi internal` 访问缓存实例，并保留完整嵌套类型。应用级复用 Gson/Moshi/配置完成的 ObjectMapper 和模型适配器，不缓存绑定 Activity 的回调。

Gson **2.10.1** 不能按新版 Gson 自动附带完整 consumer rules 来配置。`@SerializedName` 固定协议字段名，但不会自行保留反射访问的字段、构造器或 `TypeToken` 的泛型元数据。下面给出一个明确模型的保守规则，不无差别保留全应用：

```kotlin
package com.example.json
import com.google.gson.annotations.SerializedName

data class JsonUser(
    @field:SerializedName("id") val id: String = "",
    @field:SerializedName("name") val name: String = ""
)
```

```proguard
-keepattributes Signature,*Annotation*,InnerClasses,EnclosingMethod
-keep class com.google.gson.reflect.TypeToken { *; }
-keep class * extends com.google.gson.reflect.TypeToken
-keep class com.example.json.JsonUser {
    <fields>;
    public <init>();
}
```

`-keepattributes` 本身不让类/成员成为存活入口；上述模型规则同时保留实际反射目标。换模型时按实际 DTO 及嵌套类型扩充，不能只替换 JSON 字符串。所有构造参数有默认值的 Kotlin/JVM 类可生成无参构造器；没有可用无参构造器时，Gson 的 Unsafe 路径可能不执行 Kotlin 初始化逻辑。显式 JSON null 仍可绕过 Kotlin 非空约束，默认值不是协议验证器。

Moshi 1.15.0 core 自带内部规则，但反射 DTO 仍需应用保留；codegen DTO 减少这类反射需求。用于反射解析的枚举按该版 README 使用 `@JsonClass(generateAdapter = false)` 等配套规则。release 测试输入包含泛型嵌套、缺失字段、显式 null、未知枚举和数字溢出。

固定版本证据：[Gson 2.10.1 示例规则](https://github.com/google/gson/blob/gson-parent-2.10.1/examples/android-proguard-example/proguard.cfg)、[`ConstructorConstructor.get`](https://github.com/google/gson/blob/gson-parent-2.10.1/gson/src/main/java/com/google/gson/internal/ConstructorConstructor.java)、[Moshi 1.15.0 R8/ProGuard 说明](https://github.com/square/moshi/blob/parent-1.15.0/README.md#r8--proguard)。

### 10.4 有界输入与取消

大文件使用流式解析，每读完一个对象就交给下游，不把完整 JSONArray 和完整业务列表同时常驻内存。输入层限制压缩后/解压后大小、协议允许的嵌套深度和字段长度；仅检查 HTTP Content-Length 无法约束 chunked 或解压后的内容。

同步 JSON 解析不会在所有循环中自动响应协程取消。批量映射在 Default dispatcher 上运行并定期 `ensureActive()`；流在拥有者作用域中使用 `use` 关闭。不要捕获所有 Exception 后返回默认对象，从而吞掉 CancellationException 或程序错误。

### 10.5 性能实验的可重复步骤

1. 固定真实脱敏样本：小对象、深层泛型、大数组、异常输入分别测量。
2. 在相同 release/R8 配置下预热适配器，把首次建适配器和稳态解析分开。
3. 记录每次解析时间、分配字节、峰值内存；不把网络时间计入纯解析指标。
4. 校验输出完全一致后再比较性能，流式解析与整树解析按相同业务输出量比较。

Android 17 更新平台的 `org.json` 与运行环境；Gson、Moshi、Jackson 的代码仍由应用依赖决定。不能以系统版本推导某个解析器“性能最高”。

参考：[Gson TypeToken](https://github.com/google/gson/blob/gson-parent-2.10.1/gson/src/main/java/com/google/gson/reflect/TypeToken.java)、[Moshi](https://github.com/square/moshi)、[Microbenchmark](https://developer.android.com/topic/performance/benchmarking/microbenchmark-overview)。
