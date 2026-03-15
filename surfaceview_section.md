
---

## 5. SurfaceView 与 TextureView

### 5.1 SurfaceView

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SurfaceView 架构详解                                 │
└─────────────────────────────────────────────────────────────────────────────┘

SurfaceView 的特殊性：涉及 2 个 Surface

1. **宿主 Activity 的 Surface (Surface #1)**
   - 由 Activity 的 ViewRootImpl 管理
   - SurfaceView 在这个 Surface 上是透明的（"挖了个洞"）
   - SurfaceView 本身只是 View 层级中的占位符

2. **SurfaceView 的独立 Surface (Surface #2)**
   - 由 SurfaceView 内部管理（通过 SurfaceHolder）
   - 位于宿主 Surface 的"下方"
   - 这是真正绘制视频/相机/游戏内容的 Surface
   - 通过 Activity Surface 上的"洞"显示出来

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                  Activity 的 Surface (Surface #1)                   │ │
│   │                                                                      │ │
│   │   ┌───────────────────────────────────────────────────────────────┐ │ │
│   │   │                     View 层级                                  │ │ │
│   │   │                                                                │ │ │
│   │   │   ┌────────────────┐   ┌────────────────┐                    │ │ │
│   │   │   │    TextView    │   │    Button      │                    │ │ │
│   │   │   └────────────────┘   └────────────────┘                    │ │ │
│   │   │                                                                │ │ │
│   │   │        ┌────────────────────────────────────┐                │ │ │
│   │   │        │      SurfaceView (透明洞)          │                │ │ │
│   │   │        │                                    │  ← 只是占位    │ │ │
│   │   │        │        ┌──────────────────┐        │    不绘制内容  │ │ │
│   │   │        │        │ 透过洞可见下方   │        │                │ │ │
│   │   │        │        │   Surface 内容   │        │                │ │ │
│   │   │        │        └──────────────────┘        │                │ │ │
│   │   │        │                                    │                │ │ │
│   │   │        └────────────────────────────────────┘                │ │ │
│   │   │                                                                │ │ │
│   │   └───────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │             SurfaceView 的独立 Surface (Surface #2)                 │ │
│   │                                                                      │ │
│   │         这是真正绘制视频/相机/游戏内容的 Surface                      │ │
│   │         位于 Activity Surface 的下方                                 │ │
│   │         通过 SurfaceView 的"洞"显示出来                              │ │
│   │                                                                      │ │
│   │         由 SurfaceFlinger 直接管理，独立 BufferQueue                 │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│   SurfaceFlinger 合成顺序（从下到上）：                                    │
│   SurfaceView Surface (#2) → Activity Surface (#1) → 显示器               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

为什么 SurfaceView 的 Surface 在 View 层级"下方"？
- SurfaceView 的独立 Surface z-index 比 Activity 的 Surface 低
- 所以 SurfaceView 需要在 Activity Surface 上"挖洞"才能显示
- 这也是为什么 SurfaceView 不支持动画/变换的原因（它不参与 View 层级的变换）

特点：
- 涉及 2 个 Surface（Activity 的 + 独立的）
- 独立 Surface 可在子线程绘制
- 不支持动画、变换、透明度
- 性能最优
- 可能有黑屏问题（Surface 未准备好时）
```

### 5.2 TextureView

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TextureView 架构                                     │
└─────────────────────────────────────────────────────────────────────────────┘

TextureView 不创建新的 Surface，共享宿主的 Surface。
内容渲染到 OpenGL Texture，然后合成到宿主 Surface。

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐ │
│   │                  Activity 的 Surface (唯一的 Surface)               │ │
│   │                                                                      │ │
│   │   ┌───────────────────────────────────────────────────────────────┐ │ │
│   │   │                     View 层级                                  │ │ │
│   │   │                                                                │ │ │
│   │   │   ┌────────────────┐   ┌────────────────┐                    │ │ │
│   │   │   │    TextView    │   │    Button      │                    │ │ │
│   │   │   └────────────────┘   └────────────────┘                    │ │ │
│   │   │                                                                │ │ │
│   │   │        ┌──────────────────────────────────────┐              │ │ │
│   │   │        │           TextureView                │              │ │ │
│   │   │        │                                      │              │ │ │
│   │   │        │   • 使用 HardwareTexture             │              │ │ │
│   │   │        │   • 内容渲染到 GL Texture            │  ← 共享 Surface
│   │   │        │   • 与 View 层级一起合成             │              │ │ │
│   │   │        │   • 支持动画/变换/透明               │              │ │ │
│   │   │        │                                      │              │ │ │
│   │   │        └──────────────────────────────────────┘              │ │ │
│   │   │                                                                │ │ │
│   │   └───────────────────────────────────────────────────────────────┘ │ │
│   │                                                                      │ │
│   └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

特点：
- 共享宿主的 Surface（只有 1 个 Surface）
- 内容渲染到 GL Texture
- 支持动画、变换、透明度
- 支持 getBitmap() 截图
- 性能略低于 SurfaceView
```

### 5.3 SurfaceView vs TextureView 对比

| 特性 | SurfaceView | TextureView |
|------|-------------|-------------|
| Surface 数量 | 2 个（Activity + 独立） | 1 个（共享） |
| ViewRootImpl | 2 个 | 1 个（共享） |
| 渲染线程 | 可在任意线程 | 必须主线程创建，子线程渲染 |
| 透明度 | ❌ 不支持 | ✅ 支持 |
| 动画 | ❌ 不支持 | ✅ 支持 |
| 截图 | ❌ 不支持 | ✅ getBitmap() |
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 适用场景 | 视频、相机、游戏 | 视频滤镜、动画、截图 |

### 5.4 使用示例

#### SurfaceView 示例

```kotlin
class MySurfaceView(context: Context) : SurfaceView(context), SurfaceHolder.Callback {
    
    init {
        holder.addCallback(this)
    }
    
    override fun surfaceCreated(holder: SurfaceHolder) {
        // Surface #2 准备好，可以开始绘制
        // holder.surface 就是独立的 Surface
        DrawThread(holder.surface).start()
    }
    
    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) {}
    
    override fun surfaceDestroyed(holder: SurfaceHolder) {
        // Surface #2 销毁
    }
    
    private class DrawThread(private val surface: Surface) : Thread() {
        override fun run() {
            while (!isInterrupted) {
                var canvas: Canvas? = null
                try {
                    // 在子线程绘制到独立 Surface
                    canvas = surface.lockCanvas(null)
                    canvas?.drawColor(Color.BLACK)
                    // ... 绘制内容
                } finally {
                    canvas?.let { surface.unlockCanvasAndPost(it) }
                }
            }
        }
    }
}
```

#### TextureView 示例

```kotlin
class MyTextureView(context: Context) : TextureView(context), TextureView.SurfaceTextureListener {
    
    init {
        surfaceTextureListener = this
    }
    
    override fun onSurfaceTextureAvailable(surface: SurfaceTexture, width: Int, height: Int) {
        // SurfaceTexture 准备好（共享 Activity 的 Surface）
        // 可以用于视频播放等
    }
    
    override fun onSurfaceTextureSizeChanged(surface: SurfaceTexture, width: Int, height: Int) {}
    
    override fun onSurfaceTextureDestroyed(surface: SurfaceTexture): Boolean {
        return true
    }
    
    override fun onSurfaceTextureUpdated(surface: SurfaceTexture) {}
    
    // 支持动画和变换
    fun applyAnimation() {
        alpha = 0.5f              // 透明度
        rotation = 45f            // 旋转
        scaleX = 1.5f             // 缩放
        translationX = 100f       // 平移
    }
    
    // 支持截图
    fun captureFrame(): Bitmap? {
        return bitmap
    }
}
```

### 5.5 选择建议

| 场景 | 推荐 | 原因 |
|------|------|------|
| 视频播放器 | SurfaceView | 性能更好，无合成开销 |
| 相机预览 | SurfaceView | 低延迟，高帧率 |
| 游戏 | SurfaceView | 独立线程渲染，性能最优 |
| 视频滤镜/特效 | TextureView | 需要获取帧数据做处理 |
| 视频弹幕 | TextureView | 需要与 View 叠加 |
| 视频动画（如小窗） | TextureView | 需要动画/变换 |
| 直播推流 | TextureView | 需要获取帧数据编码 |
| 视频截图 | TextureView | getBitmap() 直接获取 |
