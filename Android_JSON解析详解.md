# Android JSON 解析详解

> 作者：OpenClaw | 日期：2026-03-13

---

## 目录

1. [概述](#1-概述)
2. [org.json 原生解析](#2-orgjson-原生解析)
3. [Gson 解析库](#3-gson-解析库)
4. [Moshi 解析库](#4-moshi-解析库)
5. [Jackson 解析库](#5-jackson-解析库)
6. [性能对比](#6-性能对比)
7. [最佳实践](#7-最佳实践)
8. [常见问题](#8-常见问题)
9. [知识体系总结](#9-知识体系总结)

---

## 1. 概述

### 1.1 JSON 是什么

```
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

```
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

```
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

```
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

```kotlin
// ==================== GsonBuilder 常用配置 ====================
val gson = GsonBuilder()
    // 美化输出（带缩进）
    .setPrettyPrinting()
    
    // 宽松模式（允许特殊字符）
    .setLenient()
    
    // 序列化 null 值
    .serializeNulls()
    
    // 日期格式
    .setDateFormat("yyyy-MM-dd HH:mm:ss")
    
    // 版本控制
    .setVersion(1.0)
    
    // 排除没有 @Expose 的字段
    .excludeFieldsWithoutExposeAnnotation()
    
    // 排除特定修饰符的字段
    .excludeFieldsWithModifiers(Modifier.STATIC, Modifier.TRANSIENT)
    
    // 生成不可执行的 JSON（带 )]}' 前缀，防止 XSS）
    .generateNonExecutableJson()
    
    // 字段命名策略
    .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
    
    // 自定义字段命名策略
    .setFieldNamingStrategy { field ->
        "prefix_${field.name}"
    }
    
    // 注册类型适配器
    .registerTypeAdapter(Date::class.java, DateTypeAdapter())
    .registerTypeAdapter(List::class.java, ListTypeAdapter())
    
    .create()

// ==================== FieldNamingPolicy 命名策略 ====================
// IDENTITY：原样保留
// LOWER_CASE_WITH_UNDERSCORES：user_name
// LOWER_CASE_WITH_DASHES：user-name
// UPPER_CAMEL_CASE：UserName
// UPPER_CAMEL_CASE_WITH_SPACES：User Name
```

### 3.5 泛型处理

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
    return gson.fromJson(jsonString, type)
}

// 使用
val response: ApiResponse<User> = parseApiResponse(jsonString)

// ==================== 泛型工具类 ====================
object GsonUtils {
    private val gson = GsonBuilder()
        .setPrettyPrinting()
        .serializeNulls()
        .setDateFormat("yyyy-MM-dd HH:mm:ss")
        .create()
    
    fun <T> fromJson(json: String, clazz: Class<T>): T {
        return gson.fromJson(json, clazz)
    }
    
    inline fun <reified T> fromJson(json: String): T {
        return gson.fromJson(json, object : TypeToken<T>() {}.type)
    }
    
    fun <T> fromJson(json: String, type: Type): T {
        return gson.fromJson(json, type)
    }
    
    fun <T> toJson(obj: T): String {
        return gson.toJson(obj)
    }
    
    fun <T> toJson(obj: T, type: Type): String {
        return gson.toJson(obj, type)
    }
    
    // List 解析
    inline fun <reified T> fromJsonList(json: String): List<T> {
        val type = TypeToken.getParameterized(List::class.java, T::class.java).type
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

// 使用 RuntimeTypeAdapterFactory（需要 extra 依赖）
// implementation("com.google.code.gson:gson-extras:2.10.1")

// 或自定义反序列化器
class ContentDeserializer : JsonDeserializer<Content> {
    override fun deserialize(
        json: JsonElement,
        typeOfT: Type,
        context: JsonDeserializationContext
    ): Content {
        val jsonObject = json.asJsonObject
        val type = jsonObject.get("type").asString
        
        return when (type) {
            "text" -> context.deserialize(json, Content.TextContent::class.java)
            "image" -> context.deserialize(json, Content.ImageContent::class.java)
            "video" -> context.deserialize(json, Content.VideoContent::class.java)
            else -> throw JsonParseException("Unknown content type: $type")
        }
    }
}
```

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

suspend fun <T> safeApiCall(call: suspend () -> Response<BaseResponse<T>>): ApiResult<T> {
    return try {
        val response = call()
        if (response.isSuccessful) {
            val body = response.body()
            if (body != null && body.code == 200) {
                ApiResult.Success(body.data!!)
            } else {
                ApiResult.Error(body?.code ?: -1, body?.message ?: "Unknown error")
            }
        } else {
            ApiResult.Error(response.code(), response.message())
        }
    } catch (e: Exception) {
        ApiResult.Error(-1, e.message ?: "Network error")
    }
}
```

---

## 4. Moshi 解析库

### 4.1 Moshi 简介

```
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

```
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

## 6. 性能对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         JSON 解析库性能对比                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  解析速度（越小越快）：
  ─────────────────────────────────────────────────────────────────────────
  
  ┌──────────────────┬──────────────┬──────────────┬──────────────────────────┐
  │      库           │  序列化(ms)   │  反序列化(ms) │         说明            │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  Jackson         │  5-10        │  8-15        │  最快，流式解析          │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  Moshi           │  10-20       │  15-25       │  较快，Okio 优化         │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  Gson            │  15-30       │  20-40       │  中等，反射开销          │
  ├──────────────────┼──────────────┼──────────────┼──────────────────────────┤
  │  org.json        │  20-40       │  30-50       │  较慢，手动解析          │
  └──────────────────┴──────────────┴──────────────┴──────────────────────────┘

  库大小：
  ─────────────────────────────────────────────────────────────────────────
  - org.json：0 KB（内置）
  - Gson：~240 KB
  - Moshi：~150 KB
  - Jackson：~1.5 MB

  内存占用：
  ─────────────────────────────────────────────────────────────────────────
  - Jackson：最低（流式解析）
  - Moshi：中等
  - Gson：较高（反射缓存）
  - org.json：中等

  选择建议：
  ─────────────────────────────────────────────────────────────────────────
  - 简单场景 / 无额外依赖：org.json
  - Java 项目 / 团队熟悉：Gson
  - Kotlin 项目 / 新项目：Moshi
  - 高性能 / 大数据量：Jackson
```

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
    val type = TypeToken.getParameterized(
        ApiResponse::class.java,
        T::class.java
    ).type
    return Gson().fromJson(json, type)
}

// ==================== 使用 Moshi ====================
inline fun <reified T> parseResponseMoshi(json: String): ApiResponse<T>? {
    val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
    val type = Types.newParameterizedType(ApiResponse::class.java, T::class.java)
    return moshi.adapter<ApiResponse<T>>(type).fromJson(json)
}
```

### 7.2 错误处理

```kotlin
// ==================== 安全解析 ====================
inline fun <reified T> safeParseJson(json: String): Result<T> {
    return try {
        val obj = Gson().fromJson(json, T::class.java)
        Result.success(obj)
    } catch (e: JsonSyntaxException) {
        Result.failure(ParseException("JSON syntax error", e))
    } catch (e: Exception) {
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
// ==================== 缓存 Gson 适配器 ====================
object GsonFactory {
    private val gsonCache = mutableMapOf<Type, Gson>()
    
    fun <T> getAdapter(type: Type): Gson {
        return gsonCache.getOrPut(type) {
            GsonBuilder()
                .setDateFormat("yyyy-MM-dd HH:mm:ss")
                .create()
        }
    }
}

// ==================== 缓存 Moshi 适配器 ====================
object MoshiFactory {
    private val moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()
    
    private val adapterCache = mutableMapOf<Type, JsonAdapter<*>>()
    
    @Suppress("UNCHECKED_CAST")
    fun <T> getAdapter(clazz: Class<T>): JsonAdapter<T> {
        return adapterCache.getOrPut(clazz) {
            moshi.adapter(clazz)
        } as JsonAdapter<T>
    }
}
```

---

## 8. 常见问题

```
Q1: Gson 和 Moshi 怎么选？
─────────────────────────────────────────────────────────────────────────
A: 
   - Java 项目或团队熟悉 Gson：选 Gson
   - Kotlin 新项目：选 Moshi（编译时代码生成，性能更好）
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

```
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
  4. Jackson：性能最高，大数据量场景
  5. 复用实例，缓存适配器，优化性能
```

---

> 作者：OpenClaw | 日期：2026-03-13