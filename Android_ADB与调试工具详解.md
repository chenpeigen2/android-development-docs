# Android ADB 与调试工具详解

> 作者：OpenClaw | 日期：2026-04-15
> Android 开发者必备的调试工具全面指南 | 命令速查 + 深度解析 + 实战技巧

---

## 目录

1. [概述](#1-概述)
2. [ADB 基础](#2-adb-基础)
3. [设备与系统命令](#3-设备与系统命令)
4. [应用管理（pm）](#4-应用管理pm)
5. [Activity 管理（am）](#5-activity-管理am)
6. [文件操作](#6-文件操作)
7. [日志系统（logcat）](#7-日志系统logcat)
8. [Input 模拟](#8-input-模拟)
9. [网络与端口转发](#9-网络与端口转发)
10. [屏幕操作](#10-屏幕操作)
11. [dumpsys 深度解析](#11-dumpsys-深度解析)
12. [进程与性能调试](#12-进程与性能调试)
13. [SQLite 与 Content Provider](#13-sqlite-与-content-provider)
14. [Systrace 与 Perfetto](#14-systrace-与-perfetto)
15. [Android Studio 调试工具](#15-android-studio-调试工具)
16. [APK 分析工具](#16-apk-分析工具)
17. [高级调试技巧](#17-高级调试技巧)
18. [面试常见问题](#18-面试常见问题)
19. [命令速查表](#19-命令速查表)

---

## 1. 概述

ADB（Android Debug Bridge）是 Android 开发中最核心的调试工具，它是一个客户端-服务端架构的命令行工具，提供了与 Android 设备通信的能力。

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ADB 架构                                             │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
  │  ADB Client  │  TCP   │  ADB Server  │  USB/  │  ADB Daemon  │
  │  (adb 命令)  │───────→│  (本机后台)  │─TCP───→│  (adbd 设备) │
  │              │  :5037 │              │        │              │
  └──────────────┘        └──────────────┘        └──────────────┘
       开发机                 开发机                  Android 设备

  通信流程：
  ─────────────────────────────────────────────────────────────────────────
  1. ADB Client 发送命令到本地 ADB Server（TCP 5037）
  2. ADB Server 发现连接的设备，建立连接
     - USB 连接：通过 adb forward 映射端口
     - WiFi 连接：通过 TCP 直接连接（adb connect）
  3. ADB Server 将命令转发给设备上的 adbd（端口号 5555）
  4. adbd 执行命令并返回结果

  ADB Server 职责：
  ─────────────────────────────────────────────────────────────────────────
  - 管理设备连接（USB/WiFi/模拟器）
  - 处理客户端请求并发到对应设备
  - 维护设备列表
  - 自动启动（检测到 adb 命令时）

  adbd 职责：
  ─────────────────────────────────────────────────────────────────────────
  - 运行在 Android 设备上的后台守护进程
  - 路径：/sbin/adbd（或 /system/bin/adbd）
  - 以 root 或 shell 用户运行
  - userdebug/eng 版本默认以 root 运行
  - user 版本以 shell 用户运行（受限）
```

### 1.1 ADB 工具链全景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Android 调试工具全景                                      │
└─────────────────────────────────────────────────────────────────────────────┘

  命令行工具：
  ─────────────────────────────────────────────────────────────────────────
  adb           → 设备通信（调试核心）
  aapt/aapt2    → 资源编译与 APK 分析
  apkanalyzer   → APK 组成分析（Android SDK）
  dexdump       → DEX 文件反编译查看
  simpleperf    → CPU 性能分析
  perfetto      → 系统级性能追踪（替代 systrace）
  screencap     → 设备端截图
  screenrecord  → 设备端录屏

  Android Studio 工具：
  ─────────────────────────────────────────────────────────────────────────
  Logcat           → 日志查看（带过滤和格式化）
  Layout Inspector → 布局层级检查
  Database Inspector→ 数据库可视化
  App Inspection   → 网络请求/后台任务检查
  Profiler         → CPU/内存/网络/能耗分析
  APK Analyzer     → APK 大小和组成分析

  第三方工具：
  ─────────────────────────────────────────────────────────────────────────
  scrcpy          → 投屏 + 控制（Genymobile）
  jadx            → APK/DEX 反编译
  Frida           → 动态插桩（安全研究）
  Charles/mitmproxy→ 网络抓包代理
  LeakCanary      → 内存泄漏检测
```

---

## 2. ADB 基础

### 2.1 环境配置

```
安装方式：
  ─────────────────────────────────────────────────────────────────────────
  方式一：Android Studio（推荐）
  - SDK Manager → SDK Tools → Android SDK Platform-Tools
  - 路径：$ANDROID_HOME/platform-tools/adb

  方式二：独立安装
  - Ubuntu: sudo apt install adb
  - macOS:  brew install android-platform-tools
  - Windows: 下载 SDK Platform-Tools ZIP

  环境变量：
  ─────────────────────────────────────────────────────────────────────────
  # ~/.bashrc 或 ~/.zshrc
  export ANDROID_HOME=$HOME/Android/Sdk
  export PATH=$PATH:$ANDROID_HOME/platform-tools
  export PATH=$PATH:$ANDROID_HOME/tools

  验证安装：
  ─────────────────────────────────────────────────────────────────────────
  $ adb version
  Android Debug Bridge version 1.0.41
  Version 34.0.5-11580240
```

### 2.2 设备连接

```
USB 连接：
  ─────────────────────────────────────────────────────────────────────────
  1. 手机开启「开发者选项」→「USB 调试」
  2. USB 线连接电脑
  3. 手机弹出授权对话框，勾选「始终允许」

  # 查看已连接设备
  $ adb devices
  List of devices attached
  R5CR80XXXXX    device        ← USB 连接（device 表示正常）
  192.168.1.100:5555   device  ← WiFi 连接
  emulator-5554        device  ← 模拟器

  设备状态说明：
  ─────────────────────────────────────────────────────────────────────────
  device      → 正常连接
  offline     → 设备未响应（重启 adb server）
  unauthorized→ 未授权（手机上点击授权）
  recovery    → 设备在 Recovery 模式
  fastboot    → 设备在 Fastboot 模式

  WiFi 连接（Android 11+ 无线调试）：
  ─────────────────────────────────────────────────────────────────────────
  # 方式一：配对码连接（Android 11+）
  # 手机：开发者选项 → 无线调试 → 使用配对码配对设备
  $ adb pair <ip>:<pairing_port>
  Enter pairing code: XXXXXX

  # 方式二：先 USB 后 WiFi（需要同网络）
  $ adb tcpip 5555                    # 切换到 TCP 模式
  $ adb connect 192.168.1.100:5555    # 连接
  $ adb disconnect                     # 断开

  # 方式三：直接连接（需要设备已监听端口）
  $ adb connect 192.168.1.100:5555
```

### 2.3 ADB Server 管理

```
# 启动 ADB Server
$ adb start-server

# 停止 ADB Server（设备连接异常时尝试）
$ adb kill-server

# 重启 ADB Server
$ adb kill-server && adb start-server

# 指定 ADB Server 端口（默认 5037）
$ adb -P 5037 start-server

# 以 root 权限重启 adbd
$ adb root

# 以 usb 模式重启 adbd
$ adb usb
```

---

## 3. 设备与系统命令

### 3.1 设备信息

```
# 查看所有已连接设备
$ adb devices [-l]    # -l 显示设备详细信息

# 查看设备序列号
$ adb get-serialno

# 查看设备状态
$ adb get-state

# 指定设备执行命令（多设备时）
$ adb -s R5CR80XXXXX shell <command>    # 指定序列号
$ adb -d shell <command>                # 只用 USB 设备
$ adb -e shell <command>                # 只用模拟器
```

### 3.2 系统属性

```
# 查看所有系统属性
$ adb shell getprop

# 查看特定属性
$ adb shell getprop ro.build.version.sdk         # API Level
$ adb shell getprop ro.build.version.release     # Android 版本
$ adb shell getprop ro.product.model             # 设备型号
$ adb shell getprop ro.product.brand             # 品牌
$ adb shell getprop ro.product.manufacturer      # 厂商
$ adb shell getprop ro.build.display.id          # 构建版本号
$ adb shell getprop ro.hardware                  # 硬件平台
$ adb shell getprop gsm.version.baseband         # 基带版本

# 设置系统属性（需要 root）
$ adb shell setprop persist.sys.locale zh-CN

# 常用属性速查：
  ─────────────────────────────────────────────────────────────────────────
  ro.build.version.sdk          → SDK 版本（如 34）
  ro.build.version.release      → Android 版本（如 14）
  ro.product.model              → 型号（如 SM-S918B）
  ro.product.brand              → 品牌（如 samsung）
  ro.debuggable                 → 是否可调试（0/1）
  ro.build.type                 → 构建类型（user/userdebug/eng）
  persist.sys.timezone          → 时区
  ro.configuration.orientation  → 屏幕方向
```

### 3.3 系统操作

```
# 重启设备
$ adb reboot                    # 普通重启
$ adb reboot recovery           # 重启到 Recovery
$ adb reboot bootloader         # 重启到 Bootloader/Fastboot
$ adb reboot fastboot           # 重启到 Fastbootd（新设备）
$ adb reboot edl                # 重启到 EDL 模式（高通刷机）

# 等待设备就绪（阻塞直到设备可用）
$ adb wait-for-device

# 查看设备信息摘要
$ adb shell cat /proc/cpuinfo   # CPU 信息
$ adb shell cat /proc/meminfo   # 内存信息
$ adb shell df -h               # 磁盘空间
$ adb shell cat /proc/version   # 内核版本

# 查看屏幕分辨率和密度
$ adb shell wm size             # 分辨率
$ adb shell wm density          # 屏幕密度（DPI）
```

---

## 4. 应用管理（pm）

### 4.1 安装与卸载

```
# 安装 APK
$ adb install app.apk                     # 普通安装
$ adb install -r app.apk                  # 覆盖安装（保留数据）
$ adb install -r -t app.apk              # 允许安装测试 APK
$ adb install -r -d app.apk              # 允许降级安装
$ adb install -r -g app.apk              # 安装并授予所有权限
$ adb install --split apk_base.apk apk_arm64.apk  # 安装 Split APK
$ adb install-multiple base.apk config.apk        # 安装多 APK
$ adb install -i com.android.vending app.apk      # 指定安装来源（模拟 Play Store）

# 卸载应用
$ adb uninstall com.example.app           # 卸载
$ adb uninstall -k com.example.app        # 卸载但保留数据（-k = keep）

# 安装流程源码角度：
  ─────────────────────────────────────────────────────────────────────────
  adb install → adb push /data/local/tmp/app.apk
              → pm install /data/local/tmp/app.apk
              → adb shell rm /data/local/tmp/app.apk
```

### 4.2 包信息查询

```
# 列出所有已安装应用
$ adb shell pm list packages                     # 所有
$ adb shell pm list packages -3                  # 仅第三方
$ adb shell pm list packages -s                  # 仅系统
$ adb shell pm list packages -d                  # 已禁用的
$ adb shell pm list packages -e                  # 已启用的
$ adb shell pm list packages -f                  # 显示 APK 路径
$ adb shell pm list packages -u                  # 包含已卸载的（有数据的）

# 按关键字过滤
$ adb shell pm list packages | grep wechat

# 查看应用详细信息
$ adb shell dumpsys package com.example.app      # 完整信息
$ adb shell pm path com.example.app              # APK 安装路径
$ adb shell pm dump com.example.app              # dump 信息

# 查看 APK 路径
$ adb shell pm path com.example.app
  package:/data/app/~~hash==/com.example.app-hash==/base.apk

# 查看应用版本
$ adb shell dumpsys package com.example.app | grep versionName
  versionName=2.1.0
```

### 4.3 权限管理

```
# 列出应用的所有权限
$ adb shell dumpsys package com.example.app | grep permission

# 授予/撤销危险权限
$ adb shell pm grant com.example.app android.permission.CAMERA
$ adb shell pm revoke com.example.app android.permission.CAMERA

# 重置所有权限
$ adb shell pm reset-permissions

# 查看所有权限组
$ adb shell pm list permissions -g

# 查看运行时权限状态
$ adb shell dumpsys package com.example.app | grep -A 20 "runtime permissions"
```

### 4.4 数据管理

```
# 清除应用数据（等同于设置中的「清除数据」）
$ adb shell pm clear com.example.app

# 清除缓存
$ adb shell pm trim-caches 999999999999FREE  # 释放尽可能多的缓存空间

# 查看应用数据路径
$ adb shell pm dump com.example.app | grep dataDir
  dataDir=/data/user/0/com.example.app

# 查看应用占用空间
$ adb shell dumpsys diskstats
```

---

## 5. Activity 管理（am）

### 5.1 启动 Activity

```
# 基本启动
$ adb shell am start -n com.example.app/.MainActivity

# 带参数启动
$ adb shell am start -n com.example.app/.MainActivity \
    --es "key_string" "value" \          # 额外 String
    --ei "key_int" 100 \                 # 额外 int
    --ez "key_bool" true \               # 额外 boolean
    --el "key_long" 999999L              # 额外 long

# 带 Action 启动（隐式 Intent）
$ adb shell am start -a android.intent.action.VIEW \
    -d "https://www.example.com"

# 启动指定 Activity 并清空任务栈
$ adb shell am start -n com.example.app/.MainActivity \
    --activity-clear-task \
    --activity-no-animation

# 启动 Activity 并指定 Flag
$ adb shell am start -n com.example.app/.MainActivity \
    -f 0x10000000                        # FLAG_ACTIVITY_NEW_TASK

# 启动系统设置
$ adb shell am start -a android.settings.APPLICATION_DETAILS_SETTINGS \
    -d package:com.example.app           # 应用详情页
$ adb shell am start -a android.settings.SETTINGS  # 设置主页
$ adb shell am start -a android.settings.WIFI_SETTINGS  # WiFi 设置
```

### 5.2 启动 Service

```
# 启动 Service
$ adb shell am startservice -n com.example.app/.MyService

# 前台 Service（Android 8+）
$ adb shell am start-foreground-service -n com.example.app/.MyService

# 停止 Service
$ adb shell am stopservice -n com.example.app/.MyService
```

### 5.3 发送广播

```
# 发送自定义广播
$ adb shell am broadcast -a com.example.ACTION_CUSTOM

# 带额外数据的广播
$ adb shell am broadcast -a com.example.ACTION_CUSTOM \
    --es "message" "hello"

# 发送系统广播（模拟）
$ adb shell am broadcast -a android.intent.action.BOOT_COMPLETED

# 发送到指定包的广播
$ adb shell am broadcast -n com.example.app/.MyReceiver \
    -a com.example.ACTION_CUSTOM
```

### 5.4 强制停止与调试

```
# 强制停止应用
$ adb shell am force-stop com.example.app

# 杀死后台进程
$ adb shell am kill com.example.app

# 使应用进入 debug 等待状态
$ adb shell am set-debug-app -w com.example.app    # 等待调试器
$ adb shell am set-debug-app -w --persistent com.example.app  # 持久等待
$ adb shell am clear-debug-app                      # 取消等待

# 监控 Crash
$ adb shell am monitor    # 监控 ANR 和 Crash
```

---

## 6. 文件操作

### 6.1 基本文件传输

```
# 推送文件到设备
$ adb push local.txt /sdcard/remote.txt           # 推送单个文件
$ adb push local_dir/ /sdcard/remote_dir/          # 推送整个目录

# 从设备拉取文件
$ adb pull /sdcard/remote.txt local.txt            # 拉取单个文件
$ adb pull /sdcard/remote_dir/ local_dir/           # 拉取整个目录

# 同步文件（只传输变化的文件）
$ adb push --sync local_dir/ /sdcard/remote_dir/

# 注意事项：
  ─────────────────────────────────────────────────────────────────────────
  - Android 11+ 限制了 /sdcard/ 的访问范围（Scoped Storage）
  - 应用私有目录：/data/data/<package>/
  - 外部存储：/sdcard/ 或 /storage/emulated/0/
  - push 大文件时注意设备存储空间
```

### 6.2 Shell 文件操作

```
# 列出文件
$ adb shell ls -la /sdcard/
$ adb shell ls -la /sdcard/Download/

# 查看文件内容
$ adb shell cat /proc/cpuinfo
$ adb shell cat /system/build.prop

# 创建/删除
$ adb shell mkdir /sdcard/test_dir
$ adb shell rm /sdcard/test_file.txt
$ adb shell rm -r /sdcard/test_dir/

# 文件搜索
$ adb shell find /sdcard/ -name "*.apk" -type f
$ adb shell find /data/app/ -name "base.apk"      # 查找已安装 APK

# 文件权限
$ adb shell chmod 644 /sdcard/file.txt
$ adb shell chown shell:shell /sdcard/file.txt

# 查看文件大小
$ adb shell du -sh /sdcard/Download/
$ adb shell du -sh /data/data/com.example.app/
```

### 6.3 应用数据操作

```
# 备份应用数据
$ adb shell cp -r /data/data/com.example.app/ /sdcard/backup/

# 查看 SharedPreferences（需要 root 或 debuggable 应用）
$ adb shell cat /data/data/com.example.app/shared_prefs/*.xml

# 查看应用数据库
$ adb shell ls /data/data/com.example.app/databases/

# 拉取应用数据库到本地分析
$ adb pull /data/data/com.example.app/databases/app.db ./

# 查看应用缓存大小
$ adb shell du -sh /data/data/com.example.app/cache/
```

---

## 7. 日志系统（logcat）

### 7.1 基本用法

```
# 实时查看日志（Ctrl+C 停止）
$ adb logcat

# 输出后退出
$ adb logcat -d                        # dump 模式（不持续监听）

# 清除日志缓冲区
$ adb logcat -c

# 查看缓冲区大小和统计
$ adb logcat -g
```

### 7.2 日志级别与过滤

```
日志级别（优先级从低到高）：
  ─────────────────────────────────────────────────────────────────────────
  V → Verbose（详细）
  D → Debug（调试）
  I → Info（信息）
  W → Warning（警告）
  E → Error（错误）
  F → Fatal（致命）
  S → Silent（静默，不输出）

# 按级别过滤
$ adb logcat *:W                        # 只显示 Warning 及以上
$ adb logcat *:E                        # 只显示 Error 及以上

# 按 Tag 过滤
$ adb logcat -s "MainActivity"          # 只看 MainActivity tag
$ adb logcat -s "MainActivity:D" "*:S"  # MainActivity 的 Debug 及以上，其他静默

# 组合过滤
$ adb logcat MainActivity:D ActivityManager:I *:S

# 按 PID 过滤
$ adb logcat --pid=<pid>

# 按包名过滤（先获取 PID）
$ pid=$(adb shell pidof com.example.app)
$ adb logcat --pid=$pid

# 使用 grep 过滤
$ adb logcat | grep "keyword"
$ adb logcat | grep -i "exception"      # 忽略大小写
$ adb logcat | grep -E "Exception|Error"  # 正则
```

### 7.3 日志格式化

```
# 格式选项
$ adb logcat -v brief      # 默认：priority/tag(PID): message
$ adb logcat -v long       # 长格式：带时间戳和线程信息
$ adb logcat -v process    # 只显示 PID
$ adb logcat -v tag        # 只显示 priority/tag
$ adb logcat -v thread     # 只显示 priority:PID TID tag
$ adb logcat -v raw        # 只显示消息
$ adb logcat -v time       # 带时间：datetime priority/tag(PID): message
$ adb logcat -v threadtime # 带时间和线程（最详细，推荐分析用）
$ adb logcat -v color      # 彩色输出

# 常用组合
$ adb logcat -v threadtime *:V | grep "com.example"

# 输出到文件
$ adb logcat -v threadtime > logcat.txt
```

### 7.4 缓冲区管理

```
# Android 有多个日志缓冲区
$ adb logcat -b main       # 主日志（默认）
$ adb logcat -b system     # 系统日志
$ adb logcat -b events     # 事件日志
$ adb logcat -b radio      # 无线/电话日志
$ adb logcat -b crash      # Crash 日志
$ adb logcat -b all        # 所有缓冲区

# 组合缓冲区
$ adb logcat -b main,system,crash

# 设置缓冲区大小
$ adb logcat -G 16M        # 设置为 16MB
$ adb logcat -G 1M         # 设置为 1MB

# 查看缓冲区信息
$ adb logcat -g
```

### 7.5 高级用法

```
# 统计 Tag 的日志数量
$ adb logcat -v brief | awk '{print $1}' | sort | uniq -c | sort -rn | head -20

# 监控 ANR 日志
$ adb logcat -b main *:E | grep "ANR"

# 监控 GC 日志
$ adb logcat | grep "GC_"

# 监控 Activity 生命周期
$ adb logcat | grep "ActivityManager.*com.example"

# 导出 bugreport（包含完整设备状态和日志）
$ adb bugreport bugreport.zip

# 查看上一次 Crash
$ adb logcat -b crash -d

# 查看 StrictMode 违规
$ adb logcat | grep "StrictMode"

# 监控启动时间
$ adb logcat -b events | grep "am_proc_start"
```

---

## 8. Input 模拟

### 8.1 触摸与滑动

```
# 点击（x, y 坐标）
$ adb shell input tap 500 1000

# 滑动（从 x1,y1 到 x2,y2，耗时 ms）
$ adb shell input swipe 500 1500 500 500 300    # 向上滑动，300ms

# 长按（按住不松）
$ adb shell input swipe 500 1000 500 1000 1000  # 同一点停留 1000ms

# 多点触控（需要 sendevent 或 getevent）
$ adb shell getevent -l    # 查看触摸事件原始数据

# 获取屏幕分辨率来确定坐标范围
$ adb shell wm size
  Physical size: 1080x2400
```

### 8.2 按键模拟

```
# 模拟按键（KeyEvent）
$ adb shell input keyevent KEYCODE_HOME        # Home 键
$ adb shell input keyevent KEYCODE_BACK         # 返回键
$ adb shell input keyevent KEYCODE_MENU         # 菜单键
$ adb shell input keyevent KEYCODE_POWER        # 电源键
$ adb shell input keyevent KEYCODE_VOLUME_UP    # 音量+
$ adb shell input keyevent KEYCODE_VOLUME_DOWN  # 音量-
$ adb shell input keyevent KEYCODE_ENTER        # 回车
$ adb shell input keyevent KEYCODE_DEL          # 删除
$ adb shell input keyevent KEYCODE_TAB          # Tab
$ adb shell input keyevent KEYCODE_RECENT_APPS  # 最近任务

# 常用 KeyCode 速查：
  ─────────────────────────────────────────────────────────────────────────
  KEYCODE_HOME         3      KEYCODE_BACK         4
  KEYCODE_CALL         5      KEYCODE_ENDCALL      6
  KEYCODE_VOLUME_UP    24     KEYCODE_VOLUME_DOWN   25
  KEYCODE_POWER        26     KEYCODE_CAMERA        27
  KEYCODE_MENU         82     KEYCODE_ENTER         66
  KEYCODE_DEL          67     KEYCODE_TAB           61
```

### 8.3 文本输入

```
# 输入文本（不支持中文，仅 ASCII）
$ adb shell input text "hello world"

# 中文输入方案：通过剪贴板
$ adb shell am broadcast -a clipper.set \
    -e text "中文测试"
# 需要配合剪贴板广播接收器

# 另一种方案：使用 adb keyboard（第三方输入法）
# 安装 com.android.adbkeyboard 后
$ adb shell ime set com.android.adbkeyboard/.AdbIME
$ adb shell am broadcast -a ADB_INPUT_TEXT --es msg "中文"
```

### 8.4 手势录制与回放

```
# 录制 getevent 原始数据
$ adb shell getevent -l /dev/input/event2 > events.txt

# 回放（需要 root）
$ adb shell sendevent /dev/input/event2 <events>

# 使用 adb 录制/回放更简单的方式：
# 录制操作序列（需要第三方工具如 adb-record）
# 回放：循环执行 input 命令
```

---

## 9. 网络与端口转发

### 9.1 端口转发

```
# 正向转发（设备 → 本机）
  ─────────────────────────────────────────────────────────────────────────
  手机端口 → 电脑端口

  # 将手机 8080 端口映射到电脑 8080
  $ adb forward tcp:8080 tcp:8080

  # 典型场景：调试 WebView 或本地服务器
  # 电脑浏览器访问 localhost:8080 → 实际访问设备上的 8080

  # 查看所有转发规则
  $ adb forward --list

  # 移除转发规则
  $ adb forward --remove tcp:8080
  $ adb forward --remove-all          # 移除所有

  # 转发到 Unix socket（如 Chrome DevTools）
  $ adb forward tcp:9222 localabstract:chrome_devtools_remote

# 反向转发（本机 → 设备）
  ─────────────────────────────────────────────────────────────────────────
  电脑端口 → 手机端口

  # 将电脑 3000 端口映射到手机 3000
  $ adb reverse tcp:3000 tcp:3000

  # 典型场景：手机访问电脑上的开发服务器
  # 手机访问 localhost:3000 → 实际访问电脑的 3000

  # 查看所有反向转发
  $ adb reverse --list

  # 移除
  $ adb reverse --remove tcp:3000
  $ adb reverse --remove-all
```

### 9.2 网络配置

```
# 查看网络接口
$ adb shell ifconfig
$ adb shell ip addr

# 查看路由
$ adb shell ip route

# 查看 DNS
$ adb shell getprop net.dns1

# Ping 测试
$ adb shell ping -c 4 www.baidu.com

# 查看网络连接
$ adb shell netstat -tlnp
$ adb shell ss -tlnp

# 查看 WiFi 信息
$ adb shell dumpsys wifi | grep "mWifiInfo"

# 抓包（需要 tcpdump）
$ adb shell tcpdump -i any -s 0 -w /sdcard/capture.pcap
# 然后拉取到电脑用 Wireshark 分析
$ adb pull /sdcard/capture.pcap
```

---

## 10. 屏幕操作

### 10.1 截图

```
# 方式一：adb 截图（推荐）
$ adb shell screencap -p /sdcard/screenshot.png
$ adb pull /sdcard/screenshot.png
$ adb shell rm /sdcard/screenshot.png

# 一行完成
$ adb shell screencap -p /sdcard/screen.png && adb pull /sdcard/screen.png

# 方式二：直接输出到电脑（某些系统支持）
$ adb exec-out screencap -p > screenshot.png

# 方式三：直接复制到剪贴板（macOS）
$ adb exec-out screencap -p | pbcopy
```

### 10.2 录屏

```
# 开始录制
$ adb shell screenrecord /sdcard/video.mp4

# 限制时长（默认 180s，最大 180s）
$ adb shell screenrecord --time-limit 30 /sdcard/video.mp4

# 指定分辨率
$ adb shell screenrecord --size 1280x720 /sdcard/video.mp4

# 指定比特率（默认 4Mbps）
$ adb shell screenrecord --bit-rate 8000000 /sdcard/video.mp4

# 录制并显示触摸点
$ adb shell screenrecord --show-touches /sdcard/video.mp4

# 拉取录制文件
$ adb pull /sdcard/video.mp4

# 注意：
  ─────────────────────────────────────────────────────────────────────────
  - 录屏最长 3 分钟（180 秒）
  - 不支持录制音频
  - 某些设备不支持录制（安全限制，如 DRM 内容）
```

### 10.3 屏幕设置

```
# 查看当前分辨率
$ adb shell wm size
  Physical size: 1080x2400

# 修改分辨率（调试布局适配）
$ adb shell wm size 720x1280

# 恢复原始分辨率
$ adb shell wm size reset

# 查看屏幕密度
$ adb shell wm density
  Physical density: 480

# 修改密度
$ adb shell wm density 320        # 模拟不同密度
$ adb shell wm density reset      # 恢复

# 查看屏幕刷新率
$ adb shell dumpsys display | grep -i refresh

# 查看屏幕方向
$ adb shell dumpsys input | grep "SurfaceOrientation"
```

### 10.4 投屏工具（scrcpy）

```
scrcpy — 开源高性能投屏工具：
  ─────────────────────────────────────────────────────────────────────────
  安装：sudo apt install scrcpy / brew install scrcpy

  # 基本投屏
  $ scrcpy

  # 限制分辨率（提升性能）
  $ scrcpy -m 1024          # 最大尺寸 1024

  # 限制帧率
  $ scrcpy --max-fps=30

  # 录屏
  $ scrcpy --record file.mp4

  # 无线投屏
  $ scrcpy --tcpip=192.168.1.100:5555

  # 只读模式（不能操作）
  $ scrcpy --no-control

  # 关闭屏幕（仅电脑显示）
  $ scrcpy --turn-screen-off

  # 显示触摸点
  $ scrcpy --show-touches

  # 窗口标题自定义
  $ scrcpy --window-title "My Device"
  $ scrcpy --window-x 100 --window-y 100 --window-width 800 --window-height 600
```

---

## 11. dumpsys 深度解析

### 11.1 dumpsys 概述

```
dumpsys 是 Android 系统自带的诊断工具，可以输出系统服务的状态信息：

  ─────────────────────────────────────────────────────────────────────────
  # 列出所有可 dump 的服务
  $ adb shell dumpsys -l

  # 输出特定服务信息
  $ adb shell dumpsys <service_name>

  # 限制输出时间（超时 10s）
  $ adb shell dumpsys -t 10 <service_name>

  # 指定优先级
  $ adb shell dumpsys --priority HIGH <service_name>

  常用 dumpsys 服务列表：
  ─────────────────────────────────────────────────────────────────────────
  activity       → Activity/Task/Stack 信息
  meminfo        → 内存使用信息
  procstats      → 进程状态统计
  cpuinfo        → CPU 信息
  battery        → 电池状态
  wifi           → WiFi 信息
  network_stats  → 网络流量统计
  package        → 包管理信息
  window         → 窗口信息
  input          → 输入事件信息
  display        → 显示信息
  gfxinfo        → GPU 渲染信息
  dbinfo         → 数据库信息
  notification   → 通知信息
  alarm          → 闹钟信息
  jobscheduler   → JobScheduler 信息
  power          → 电源管理信息
  usagestats     → 使用统计
```

### 11.2 Activity 信息

```
# 查看 Activity 栈
$ adb shell dumpsys activity activities

# 查看当前顶部 Activity
$ adb shell dumpsys activity top | head -20

# 查看 Task 信息
$ adb shell dumpsys activity recents

# 查看指定应用的 Activity
$ adb shell dumpsys activity activities | grep "com.example"

# 查看 Service
$ adb shell dumpsys activity services com.example.app

# 查看 ContentProvider
$ adb shell dumpsys activity providers com.example.app

# 查看 Broadcast Receiver
$ adb shell dumpsys activity broadcasts | grep "com.example"

# 查看 Pending Intent
$ adb shell dumpsys activity intents
```

### 11.3 内存信息

```
# 查看应用内存使用（最重要的内存分析命令之一）
$ adb shell dumpsys meminfo com.example.app

  输出解读：
  ─────────────────────────────────────────────────────────────────────────
  ** MEMINFO in pid 12345 [com.example.app] **
                   Pss      Shared   Private
                 Total     Dirty     Dirty

  Native Heap    12345     1024      8192    ← Native 内存（C/C++）
  Dalvik Heap     8192      512      4096    ← Java 堆
  .so mmap        4096     2048        16    ← 共享库
  .apk mmap       1024        0         0    ← APK 映射
  .dex mmap        512        0         0    ← DEX 映射
  Graphics        6144        0      6144    ← GPU/图形
  Stack           1024        0      1024    ← 线程栈
  ─────────────────────────────────────────────────────────────────────────
  TOTAL          33337     3584     19448    ← 总 Pss
  Objects                                               ← Java 对象统计
    Views:         256      ViewRootImpl:       2
    AppContexts:     3      Activities:          2
    Assets:         10      LocalBinders:       15
  SQL
    heap:          256      dbFiles:            3
    rows:        12345      preparing:          0

# 按类型排序
$ adb shell dumpsys meminfo --sort <field>

# 查看系统整体内存
$ adb shell dumpsys meminfo

# 对比前后内存快照（检测泄漏）
$ adb shell dumpsys meminfo com.example.app > before.txt
# 操作应用...
$ adb shell dumpsys meminfo com.example.app > after.txt
$ diff before.txt after.txt
```

### 11.4 电池信息

```
# 查看电池状态
$ adb shell dumpsys battery

  当前状态：
  ─────────────────────────────────────────────────────────────────────────
  AC powered: false
  USB powered: true
  Wireless powered: false
  status: 2                    ← 2=Charging, 3=Discharging, 4=Not charging, 5=Full
  health: 2                    ← 2=Good
  level: 85                    ← 电量百分比
  voltage: 4200                ← 电压 mV
  temperature: 280             ← 温度（1/10°C，即 28.0°C）
  technology: Li-poly

# 模拟电池状态（测试低电量场景）
$ adb shell dumpsys battery set level 5         # 设置电量为 5%
$ adb shell dumpsys battery set status 3         # 设置为放电状态
$ adb shell dumpsys battery set charging false   # 设置未在充电
$ adb shell dumpsys battery reset                # 恢复真实状态

# 电池历史记录分析
$ adb shell dumpsys batterystats > battery.txt
$ adb shell dumpsys batterystats --charged com.example.app  # 充电以来的统计
```

### 11.5 网络统计

```
# 查看网络流量统计
$ adb shell dumpsys netstats

# 查看指定应用流量
$ adb shell dumpsys netstats | grep -A 20 "com.example"

# 查看当前网络连接
$ adb shell dumpsys connectivity

# 查看网络策略
$ adb shell dumpsys netpolicy
```

### 11.6 其他常用 dump

```
# GPU 渲染信息（分析卡顿）
$ adb shell dumpsys gfxinfo com.example.app

# 查看帧时间统计
$ adb shell dumpsys gfxinfo com.example.app framestats

# 重置帧统计
$ adb shell dumpsys gfxinfo com.example.app reset

# 输入事件信息
$ adb shell dumpsys input

# 窗口信息
$ adb shell dumpsys window windows
$ adb shell dumpsys window displays

# 闹钟信息
$ adb shell dumpsys alarm

# JobScheduler 任务
$ adb shell dumpsys jobscheduler

# 通知
$ adb shell dumpsys notification

# 数据库信息
$ adb shell dumpsys dbinfo

# 权限信息
$ adb shell dumpsys permission

# WebView 信息
$ adb shell dumpsys webviewupdate
```

---

## 12. 进程与性能调试

### 12.1 进程管理

```
# 查看所有进程
$ adb shell ps
$ adb shell ps -A                          # 显示所有进程

# 查看指定应用进程
$ adb shell ps | grep com.example

# 查看进程详细信息（PID、内存、CPU）
$ adb shell ps -A -p <pid> -o PID,NAME,RSS,PCPU

# 查看进程 PID
$ adb shell pidof com.example.app

# 杀死进程
$ adb shell kill <pid>
$ adb shell kill -9 <pid>                  # 强制杀死

# 查看线程
$ adb shell ps -T -p <pid>                 # 查看某进程的所有线程

# 实时进程监控（类似 Linux top）
$ adb shell top
$ adb shell top -m 10                      # 只显示前 10
$ adb shell top -p <pid>                   # 只监控某进程
$ adb shell top -t                         # 显示线程
```

### 12.2 CPU 分析

```
# CPU 使用率
$ adb shell top -n 1 | head -20

# CPU 信息
$ adb shell cat /proc/cpuinfo

# CPU 频率
$ adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq

# simpleperf（Android 自带的 CPU Profiler）
  ─────────────────────────────────────────────────────────────────────────
  # 录制 CPU 性能数据
  $ adb shell simpleperf stat -p <pid> --duration 10
  $ adb shell simpleperf record -p <pid> --duration 10 -o /sdcard/perf.data

  # 录制 Java 方法调用
  $ adb shell simpleperf record -p <pid> --duration 10 \
      --trace-offcpu -o /sdcard/perf.data

  # 拉取并分析
  $ adb pull /sdcard/perf.data
  $ simpleperf report -i perf.data

  # 火焰图
  $ simpleperf report -i perf.data --proto > perf.proto
  # 然后用 chrome://tracing 打开
```

### 12.3 内存分析

```
# 应用内存概览
$ adb shell dumpsys meminfo com.example.app

# 查看 Native 堆内存分配（需要 malloc debug）
$ adb shell dumpsys meminfo --malloc <pid>

# 触发 GC（查看 GC 后的内存变化）
$ adb shell am dumpheap com.example.app /sdcard/heap.hprof

# 导出 Java 堆（用于 MAT/LeakCanary 分析）
$ adb shell am dumpheap com.example.app /sdcard/heap.hprof
$ adb pull /sdcard/heap.hprof

# 查看 Bitmap 内存
$ adb shell dumpsys meminfo com.example.app | grep -i "bitmap\|graphics"

# 内存限制
$ adb shell cat /proc/<pid>/limits
$ adb shell getprop dalvik.vm.heapsize        # Dalvik 堆大小

# 查看 OOM 级别
$ adb shell getprop | grep dalvik.vm.heap
  dalvik.vm.heapstartsize=8m
  dalvik.vm.heapgrowthlimit=256m       ← dexopt 进程的堆上限
  dalvik.vm.heapsize=512m              ← 大堆（largeHeap=true）
```

---

## 13. SQLite 与 Content Provider

### 13.1 SQLite 数据库操作

```
# 进入 SQLite 命令行
$ adb shell sqlite3 /data/data/com.example.app/databases/app.db

  常用 SQLite 命令：
  ─────────────────────────────────────────────────────────────────────────
  .tables                    # 列出所有表
  .schema <table>            # 查看建表语句
  .headers on                # 显示列名
  .mode column               # 列模式显示
  .dump <table>              # 导出表数据为 SQL

  SELECT * FROM users LIMIT 10;
  SELECT count(*) FROM users;
  .quit

# 直接执行 SQL（不需要交互模式）
$ adb shell sqlite3 /data/data/com.example.app/databases/app.db \
    "SELECT * FROM users LIMIT 10;"

# 查看数据库列表
$ adb shell ls /data/data/com.example.app/databases/

# 导出数据库
$ adb pull /data/data/com.example.app/databases/app.db ./

# 数据库大小
$ adb shell du -h /data/data/com.example.app/databases/
```

### 13.2 Content Provider 操作

```
# 查询
$ adb shell content query --uri content://com.example.provider/users

# 带投影和条件查询
$ adb shell content query \
    --uri content://com.example.provider/users \
    --projection name:age \
    --where "age > 18"

# 插入
$ adb shell content insert \
    --uri content://com.example.provider/users \
    --bind name:s:John \
    --bind age:i:25

# 删除
$ adb shell content delete \
    --uri content://com.example.provider/users \
    --where "_id = 1"

# 更新
$ adb shell content update \
    --uri content://com.example.provider/users \
    --bind name:s:Jane \
    --where "_id = 1"

# 查询系统 Content Provider
$ adb shell content query --uri content://settings/system
$ adb shell content query --uri content://settings/secure
$ adb shell content query --uri content://settings/global

# 查询联系人（需要权限）
$ adb shell content query --uri content://com.android.contacts/contacts
```

### 13.3 设置命令

```
# 查看系统设置
$ adb shell settings list system
$ adb shell settings list secure
$ adb shell settings list global

# 获取单个设置值
$ adb shell settings get system screen_brightness
$ adb shell settings get global airplane_mode_on

# 设置值
$ adb shell settings put system screen_brightness 200
$ adb shell settings put global development_settings_enabled 1

# 常用设置：
  ─────────────────────────────────────────────────────────────────────────
  # 开启开发者选项
  $ adb shell settings put global development_settings_enabled 1
  # 开启 USB 调试（需要 root）
  $ adb shell settings put global adb_enabled 1
  # 关闭动画（性能测试）
  $ adb shell settings put global window_animation_scale 0
  $ adb shell settings put global transition_animation_scale 0
  $ adb shell settings put global animator_duration_scale 0
  # 显示触摸点
  $ adb shell settings put system show_touches 1
  # 显示布局边界
  $ adb shell setprop debug.layout true
```

---

## 14. Systrace 与 Perfetto

### 14.1 Systrace

```
Systrace 是 Android 系统级的性能分析工具，通过 ftrace 收集内核和框架事件：

  # 采集 Systrace（需要 Python 环境）
  $ python $ANDROID_HOME/platform-tools/systrace/systrace.py \
      --time=10 \
      --output=mytrace.html \
      sched freq idle am wm view gfx input dalvik

  常用 Tag：
  ─────────────────────────────────────────────────────────────────────────
  sched      → CPU 调度
  freq       → CPU 频率
  am         → Activity Manager
  wm         → Window Manager
  view       → View 系统（measure/layout/draw）
  gfx        → 图形渲染
  input      → 输入事件
  dalvik     → 虚拟机
  disk       → 磁盘 I/O
  network    → 网络

  在代码中自定义 Trace：
  ─────────────────────────────────────────────────────────────────────────
  // Java
  import android.os.Trace;
  Trace.beginSection("myCustomTrace");
  // ... 需要追踪的代码
  Trace.endSection();

  // Kotlin
  Trace.beginSection("myCustomTrace")
  // ...
  Trace.endSection()

  注意：
  ─────────────────────────────────────────────────────────────────────────
  - beginSection / endSection 必须在同一线程配对
  - 输出为 HTML 文件，用 Chrome 打开（chrome://tracing）
  - Systrace 已逐步被 Perfetto 替代
```

### 14.2 Perfetto

```
Perfetto 是 Systrace 的继任者，功能更强大：

  # 使用 adb 采集 Perfetto trace
  $ adb shell perfetto \
      -c - --txt \
      -o /data/misc/perfetto-traces/trace.pb <<EOF
  buffers: {
      size_kb: 63488
  }
  data_sources: {
      config {
          name: "linux.ftrace"
          ftrace_config {
              ftrace_events: "sched/sched_switch"
              ftrace_events: "power/cpu_frequency"
              ftrace_events: "sched/sched_wakeup"
              atrace_categories: "view"
              atrace_categories: "am"
              atrace_categories: "gfx"
          }
      }
  }
  duration_ms: 10000
  EOF

  # 拉取 trace 文件
  $ adb pull /data/misc/perfetto-traces/trace.pb

  # 使用 Perfetto UI 打开
  # 访问 https://ui.perfetto.dev 拖入 trace.pb 文件

  # 简化方式：使用 record_android_trace 工具
  $ ./record_android_trace \
      -t 10s \
      -o trace.pb \
      sched freq idle am wm view gfx input dalvik

  Perfetto vs Systrace：
  ─────────────────────────────────────────────────────────────────────────
  ┌──────────────┬────────────────────┬──────────────────────┐
  │     特性      │    Systrace        │     Perfetto         │
  ├──────────────┼────────────────────┼──────────────────────┤
  │  输出格式    │ HTML               │ Protocol Buffer      │
  │  数据量      │ 较小               │ 更大（更丰富）       │
  │  查看工具    │ Chrome             │ Perfetto UI          │
  │  自定义      │ 有限               │ 灵活（SQL 查询）     │
  │  AndroidX    │ 逐步弃用           │ 推荐                 │
  │  长时间采集  │ 不支持             │ 支持                 │
  └──────────────┴────────────────────┴──────────────────────┘
```

---

## 15. Android Studio 调试工具

### 15.1 Layout Inspector

```
Layout Inspector — 查看 UI 布局层级：

  打开方式：Android Studio → Tools → Layout Inspector

  功能：
  ─────────────────────────────────────────────────────────────────────────
  1. 查看视图层级树（TreeView）
  2. 查看每个 View 的属性（大小、位置、padding、margin）
  3. 3D 旋转视图层级（检查重叠）
  4. 实时更新（Live Updates）
  5. 渲染性能分析（过度绘制）

  使用场景：
  ─────────────────────────────────────────────────────────────────────────
  - 布局不对齐？→ 检查 View 的实际 bounds 和 padding
  - View 不显示？→ 检查 visibility 和大小是否为 0
  - 重叠问题？→ 3D 模式查看层叠关系
  - 性能问题？→ 检查嵌套层级是否过深

  Compose 支持：
  ─────────────────────────────────────────────────────────────────────────
  - 支持查看 Compose 节点树
  - 可以看到每个 Composable 的参数值
  - 支持重组计数（Recomposition counts）
```

### 15.2 Database Inspector

```
Database Inspector — 可视化查看 Room/SQLite 数据库：

  打开方式：Android Studio → View → Tool Windows → App Inspection

  功能：
  ─────────────────────────────────────────────────────────────────────────────────
  1. 查看数据库列表和表结构
  2. 浏览表数据（分页显示）
  3. 执行自定义 SQL 查询
  4. 实时数据变化通知（LiveData/Flow 观察的数据高亮）
  5. 编辑数据（修改单元格值）
  6. 导出数据库

  使用条件：
  ─────────────────────────────────────────────────────────────────────────
  - API Level 26+（Android 8.0+）
  - 应用处于 debug 模式（debuggable=true）
  - 运行在模拟器或 debug 设备上

  典型工作流：
  ─────────────────────────────────────────────────────────────────────────
  1. 打开 App Inspection
  2. 选择正在运行的应用进程
  3. 选择数据库文件
  4. 浏览/查询/编辑数据
  5. 操作应用 UI，观察数据库变化
```

### 15.3 Profiler

```
Profiler — CPU/内存/网络/能耗分析：

  打开方式：Android Studio → View → Tool Windows → Profiler

  四大模块：
  ─────────────────────────────────────────────────────────────────────────
  ┌──────────────┬──────────────────────────────────────────────────────┐
  │     模块      │                    功能                              │
  ├──────────────┼──────────────────────────────────────────────────────┤
  │  CPU         │ 方法追踪（Call Chart/Flame Chart/Top Down/Bottom Up）│
  │              │ 支持 Java/C++ 方法追踪                               │
  │  Memory      │ Java 堆转储、Native 内存、GC 事件                    │
  │              │ 内存分配跟踪、泄漏检测                                │
  │  Network     │ 请求时间线、请求/响应详情                             │
  │              │ 仅支持 HttpURLConnection 和 OkHttp                    │
  │  Energy      │ 电量使用预估（CPU/网络/GPS/传感器）                   │
  │              │ 帮助优化电池消耗                                      │
  └──────────────┴──────────────────────────────────────────────────────┘

  CPU Profiler 使用技巧：
  ─────────────────────────────────────────────────────────────────────────
  - Java Method Trace：追踪 Java 方法调用耗时
  - C/C++ Function Trace：追踪 Native 函数
  - Call Chart：按时间线展示调用关系
  - Flame Chart：按调用栈聚合展示（找热点函数）
  - Top Down：按调用层级展示耗时（找最耗时的调用链）
  - Bottom Up：按被调用次数排序（找最频繁的函数）

  Memory Profiler 使用技巧：
  ─────────────────────────────────────────────────────────────────────────
  - Heap Dump：查看当前堆上的所有对象
  - 按类名/包名过滤
  - 查看对象的引用链（GC Root → 对象）
  - 对比两个 Heap Dump（检测内存增长）
  - 记录内存分配（Allocation Tracker）
```

### 15.4 App Inspection

```
App Inspection — 综合检查工具：

  打开方式：Android Studio → View → Tool Windows → App Inspection

  功能模块：
  ─────────────────────────────────────────────────────────────────────────
  1. Database Inspector — 数据库查看
  2. Network Inspector — 网络请求查看
     - 查看请求 URL、方法、状态码
     - 查看请求/响应 Body
     - 响应时间分析
  3. Background Task Inspector — 后台任务查看
     - WorkManager 任务状态
     - JobScheduler 任务
     - 任务链依赖关系
```

---

## 16. APK 分析工具

### 16.1 aapt / aapt2

```
aapt（Android Asset Packaging Tool）— APK 资源分析：

  # 查看 APK 基本信息
  $ aapt dump badging app.apk

  # 查看权限
  $ aapt dump permissions app.apk

  # 查看资源列表
  $ aapt dump resources app.apk

  # 查看 AndroidManifest.xml
  $ aapt dump xmltree app.apk AndroidManifest.xml

  # 查看字符串资源
  $ aapt dump strings app.apk

  # 查看配置信息
  $ aapt dump configurations app.apk

  # aapt2（Gradle 构建使用的新版本）
  # 编译资源
  $ aapt2 compile --dir res -o compiled_resources.zip
  # 链接
  $ aapt2 link -o app.apk -I android.jar compiled_resources.zip
```

### 16.2 apkanalyzer

```
apkanalyzer — Android SDK 自带的 APK 分析工具：

  # APK 文件大小分析
  $ apkanalyzer apk summary app.apk
  $ apkanalyzer apk file-size app.apk
  $ apkanalyzer apk download-size app.apk

  # 查看文件组成
  $ apkanalyzer files list app.apk
  $ apkanalyzer files cat app.apk AndroidManifest.xml

  # Dex 分析
  $ apkanalyzer dex list app.apk              # 列出 DEX 文件
  $ apkanalyzer dex references app.apk        # 引用统计
  $ apkanalyzer dex count app.apk             # 方法数/字段数

  # 查看方法数（关键：65K 限制）
  $ apkanalyzer dex references --files classes.dex app.apk

  # 查看 Manifest
  $ apkanalyzer manifest print app.apk
  $ apkanalyzer manifest application-id app.apk
  $ apkanalyzer manifest version-name app.apk
  $ apkanalyzer manifest permissions app.apk
  $ apkanalyzer manifest min-sdk app.apk
  $ apkanalyzer manifest target-sdk app.apk
```

### 16.3 dexdump

```
dexdump — DEX 文件分析工具：

  # 查看 DEX 文件内容
  $ dexdump -d classes.dex

  # 查看类列表
  $ dexdump -l plain classes.dex | grep "Class descriptor"

  # 查看 DEX 文件头信息
  $ dexdump -h classes.dex

  # 输出 XML 格式
  $ dexdump -l xml classes.dex

  # 从 APK 提取 DEX 并分析
  $ unzip -p app.apk classes.dex > classes.dex
  $ dexdump -f classes.dex
```

### 16.4 jadx

```
jadx — 开源 APK/DEX 反编译工具：

  安装：https://github.com/skylot/jadx

  # 命令行使用
  $ jadx -d output_dir app.apk               # 反编译 APK 到目录
  $ jadx -d output_dir classes.dex            # 反编译 DEX
  $ jadx --show-bad-code app.apk              # 显示反编译失败的代码

  # GUI 模式
  $ jadx-gui app.apk                         # 打开 GUI 查看反编译代码

  常用场景：
  ─────────────────────────────────────────────────────────────────────────
  - 查看第三方库的实现逻辑
  - 分析混淆后的代码结构
  - 检查 APK 是否包含敏感信息
  - 学习优秀开源 App 的实现方式

  注意：反编译结果仅供学习，请遵守相关法律法规
```

---

## 17. 高级调试技巧

### 17.1 WebView 调试

```
# 开启 WebView 调试
  ─────────────────────────────────────────────────────────────────────────
  // 代码中开启（Application.onCreate）
  if (Build.VERSION_CODES.DEBUG) {
      WebView.setWebContentsDebuggingEnabled(true)
  }

  # Chrome DevTools 远程调试
  ─────────────────────────────────────────────────────────────────────────
  1. 手机连接 USB，打开包含 WebView 的页面
  2. 电脑 Chrome 访问：chrome://inspect
  3. 找到设备上的 WebView → 点击 "inspect"
  4. 使用完整的 DevTools 调试（Console/Network/Elements/Sources）

  # 通过 adb forward 访问
  $ adb forward tcp:9222 localabstract:webview_devtools_remote_<pid>
  # 然后浏览器访问 localhost:9222
```

### 17.2 Choreographer 分析

```
# 查看 VSync 和帧渲染信息
$ adb shell dumpsys gfxinfo com.example.app framestats

  输出格式（每帧一行）：
  ─────────────────────────────────────────────────────────────────────────
  Flags,IntendedVsync,Vsync,OldestInputEvent,NewestInputEvent,
  HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,
  SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,
  FrameCompleted,DequeueBufferDuration,QueueBufferDuration,

  关键指标（单位 ns）：
  ─────────────────────────────────────────────────────────────────────────
  DrawStart - PerformTraversalsStart  → measure/layout 耗时
  SyncStart - DrawStart               → draw 耗时
  SwapBuffers - SyncStart             → GPU 同步耗时
  FrameCompleted - IntendedVsync      → 整帧耗时（>16.6ms 即丢帧）

  # 计算 FPS（使用 dumpsys）
  $ adb shell dumpsys gfxinfo com.example.app | \
      awk '/Janky frames:/ {print}'
```

### 17.3 开发者选项调试技巧

```
常用开发者选项：
  ─────────────────────────────────────────────────────────────────────────
  # 通过 adb 开启/关闭
  # 显示布局边界
  $ adb shell setprop debug.layout true
  $ adb shell service call window 3

  # 显示 GPU 过度绘制
  $ adb shell setprop debug.hwui.overdraw show

  # 显示 GPU 渲染分析（Profile GPU Rendering）
  $ adb shell setprop debug.hwui.profile visual_bars

  # 严格模式（主线程 I/O 时闪屏）
  $ adb shell setprop persist.sys.strictmode.visual 1

  # 显示触摸操作
  $ adb shell settings put system show_touches 1
  $ adb shell settings put system pointer_location 1

  # 关闭所有动画（性能测试必须）
  $ adb shell settings put global window_animation_scale 0
  $ adb shell settings put global transition_animation_scale 0
  $ adb shell settings put global animator_duration_scale 0

  # 开启「不保留活动」（测试 Activity 恢复）
  $ adb shell settings put global always_finish_activities 1

  # 限制后台进程数
  $ adb shell settings put global activity_manager_constants max_phantom_processes=0

  # 开启布局检验器
  $ adb shell settings put global enable_blur_on_windows 0
```

### 17.4 Shell 脚本技巧

```
# 自动化测试脚本示例
  ─────────────────────────────────────────────────────────────────────────
  #!/bin/bash
  # monkey_test.sh — 自动化 Monkey 测试

  PACKAGE="com.example.app"
  EVENTS=10000
  SEED=12345

  echo "Starting monkey test for $PACKAGE..."
  adb shell monkey -p $PACKAGE \
      --throttle 300 \
      --seed $SEED \
      --pct-touch 40 \
      --pct-motion 25 \
      --pct-nav 15 \
      --pct-appswitch 10 \
      --pct-anyevent 10 \
      --hprof \
      --ignore-crashes \
      --ignore-timeouts \
      --ignore-security-exceptions \
      $EVENTS

  echo "Monkey test completed."
  echo "Checking for crashes..."
  adb logcat -b crash -d | grep "$PACKAGE"

# 监控启动时间
  ─────────────────────────────────────────────────────────────────────────
  #!/bin/bash
  # measure_cold_start.sh

  PACKAGE="com.example.app"
  ACTIVITY=".MainActivity"

  echo "Measuring cold start time..."
  adb shell am force-stop $PACKAGE
  sleep 1
  adb logcat -c

  START_TIME=$(date +%s%N)
  adb shell am start -n ${PACKAGE}/${ACTIVITY}
  sleep 5

  adb logcat -d | grep "Displayed $PACKAGE" | tail -1
  adb shell am force-stop $PACKAGE

# 自动截屏序列
  ─────────────────────────────────────────────────────────────────────────
  #!/bin/bash
  for i in {1..100}; do
      adb shell screencap -p /sdcard/seq_${i}.png
      sleep 1
  done
```

---

## 18. 面试常见问题

### 18.1 ADB 基础相关

**Q1：ADB 的架构是什么？客户端、服务端、守护进程分别做什么？**

```
ADB 采用 C/S 架构，三个组件：

  1. ADB Client
     - 运行在开发机上
     - 就是用户执行的 adb 命令
     - 通过 TCP 5037 与 ADB Server 通信

  2. ADB Server
     - 运行在开发机上的后台进程
     - 管理设备连接（USB/WiFi/模拟器）
     - 将 Client 请求路由到目标设备
     - 通过 USB 或 TCP 与 adbd 通信

  3. ADB Daemon（adbd）
     - 运行在 Android 设备上
     - 执行实际命令并返回结果
     - 路径：/sbin/adbd

  面试加分：
  ─────────────────────────────────────────────────────────────────────────
  - adb devices 发现不了设备时：重启 adb kill-server && start-server
  - 多设备时用 -s 指定序列号
  - Android 11+ 支持无线配对（adb pair）
```

**Q2：adb install 安装 APK 的完整流程是什么？**

```
安装流程：
  ─────────────────────────────────────────────────────────────────────────
  1. adb push APK 到 /data/local/tmp/
  2. 调用 pm install 发起安装
  3. PMS（PackageManagerService）校验：
     - 签名验证
     - 版本号检查
     - 权限声明
     - ABI 兼容性
  4. 复制 APK 到 /data/app/
  5. 创建数据目录 /data/data/<package>/
  6. 解析 AndroidManifest.xml
  7. dex2oat 编译（ART）
  8. 发送 PACKAGE_ADDED 广播

  常用参数：
  ─────────────────────────────────────────────────────────────────────────
  -r  覆盖安装（保留数据）
  -t  允许测试 APK
  -d  允许降级
  -g  自动授予权限
```

**Q3：ADB 的端口转发（forward/reverse）有什么区别？使用场景是什么？**

```
adb forward（正向转发）：
  电脑端口 → 设备端口
  场景：电脑浏览器访问设备上的服务

  $ adb forward tcp:8080 tcp:8080
  # 电脑访问 localhost:8080 → 设备上的 8080

  adb reverse（反向转发）：
  设备端口 → 电脑端口
  场景：设备访问电脑上的开发服务器

  $ adb reverse tcp:3000 tcp:3000
  # 设备访问 localhost:3000 → 电脑上的 3000

  面试关键：
  ─────────────────────────────────────────────────────────────────────────
  - forward 用于从电脑端访问设备
  - reverse 用于从设备端访问电脑
  - reverse 是反向代理，不需要设备有公网 IP
```

---

### 18.2 日志与调试相关

**Q4：adb logcat 的缓冲区有哪些？各有什么用？**

```
Android 日志缓冲区：
  ─────────────────────────────────────────────────────────────────────────
  main    → 应用日志（默认缓冲区）
  system  → 系统日志（系统服务输出）
  events  → 事件日志（系统事件统计）
  radio   → 无线/电话相关日志
  crash   → Crash 日志

  查看方式：
  $ adb logcat -b main        # 主缓冲区
  $ adb logcat -b crash       # Crash 缓冲区
  $ adb logcat -b all         # 所有缓冲区

  缓冲区大小可配置：
  $ adb logcat -G 16M         # 设置 16MB
```

**Q5：如何用 ADB 排查 ANR？**

```
ANR 排查步骤：
  ─────────────────────────────────────────────────────────────────────────
  1. 查看 traces 文件（最重要）
     $ adb pull /data/anr/traces.txt
     # 或者
     $ adb logcat -b main *:E | grep "ANR"

  2. 查看 ANR 时的 CPU 使用情况
     $ adb logcat -b main | grep "ANR in"

  3. 监控主线程阻塞
     $ adb logcat | grep "Choreographer.*skipped"
     # 跳过帧数过多 → 主线程有耗时操作

  4. dump 线程栈
     $ adb shell kill -3 <pid>
     $ adb pull /data/anr/traces.txt

  5. 使用 StrictMode 检测
     # 在 Application 中开启 StrictMode
     StrictMode.setThreadPolicy(ThreadPolicy.Builder()
         .detectAll().penaltyLog().build())

  ANR 常见原因：
  ─────────────────────────────────────────────────────────────────────────
  - 主线程 I/O 操作
  - 主线程网络请求
  - 主线程数据库查询
  - BroadcastReceiver.onReceive() 耗时
  - Binder 通信阻塞
```

**Q6：如何用 ADB 排查内存泄漏？**

```
内存泄漏排查步骤：
  ─────────────────────────────────────────────────────────────────────────
  1. 监控内存增长
     $ adb shell dumpsys meminfo com.example.app > before.txt
     # 操作应用...
     $ adb shell dumpsys meminfo com.example.app > after.txt
     $ diff before.txt after.txt

  2. 导出 Heap Dump
     $ adb shell am dumpheap com.example.app /sdcard/heap.hprof
     $ adb pull /sdcard/heap.hprof
     # 用 MAT 或 Android Studio Profiler 分析

  3. 查看 Activity 泄漏
     $ adb shell dumpsys activity com.example.app | grep "Activities"

  4. 自动化检测
     # 使用 LeakCanary（debug 构建）
     # 或使用 Android Studio Memory Profiler

  关键指标：
  ─────────────────────────────────────────────────────────────────────────
  - Views/Activities 数量 → Activity 泄漏
  - Native Heap 增长 → Native 内存泄漏
  - Dalvik Heap 增长 → Java 堆泄漏
  - GC 频繁触发 → 内存压力大
```

---

### 18.3 性能分析相关

**Q7：如何用 ADB 分析 UI 卡顿？**

```
UI 卡顿分析步骤：
  ─────────────────────────────────────────────────────────────────────────
  1. GPU 呈现模式分析
     $ adb shell dumpsys gfxinfo com.example.app framestats
     # 每帧耗时 > 16.6ms（1000000000/60ns）即丢帧

  2. Systrace 抓取
     $ python systrace.py --time=10 view gfx input

  3. Choreographer 跳帧日志
     $ adb logcat | grep "Choreographer"
     # "Skipped N frames! The application may be doing too much work on its main thread."

  4. 过度绘制
     $ adb shell setprop debug.hwui.overdraw show
     # 颜色：无色→蓝→绿→粉红→红（过度绘制次数递增）

  5. 布局层级检查
     $ adb shell dumpsys activity top | grep "VIEW"

  常见卡顿原因：
  ─────────────────────────────────────────────────────────────────────────
  - 布局嵌套过深（measure/layout 耗时）
  - 主线程 I/O
  - 图片解码过大
  - 动画计算过重
  - RecyclerView 滑动时加载
```

**Q8：Systrace 和 Perfetto 的区别？怎么选？**

```
┌──────────────┬────────────────────┬──────────────────────┐
│     特性      │    Systrace        │     Perfetto         │
├──────────────┼────────────────────┼──────────────────────┤
│  输出格式    │ HTML               │ Protocol Buffer      │
│  查看方式    │ Chrome 打开 HTML   │ ui.perfetto.dev      │
│  数据量      │ 较小               │ 更丰富               │
│  自定义事件  │ Trace.beginSection │ TRACE_EVENT 宏       │
│  SQL 查询    │ 不支持             │ 支持（Trace Processor│
│  长时间采集  │ 不支持             │ 支持                 │
│  官方推荐    │ 逐步弃用           │ 新项目推荐           │
└──────────────┴────────────────────┴──────────────────────┘

  选择建议：
  ─────────────────────────────────────────────────────────────────────────
  - 新项目/长期维护 → Perfetto
  - 快速分析/简单场景 → Systrace 仍然可用
  - Android 12+ → 系统默认使用 Perfetto
```

---

### 18.4 命令实战相关

**Q9：如何通过 ADB 模拟用户操作（点击、滑动、输入）？**

```
点击：
  $ adb shell input tap <x> <y>

滑动：
  $ adb shell input swipe <x1> <y1> <x2> <y2> [duration_ms]

按键：
  $ adb shell input keyevent KEYCODE_BACK

文本输入：
  $ adb shell input text "hello"      # 仅 ASCII
  # 中文需要通过剪贴板或第三方输入法

长按：
  $ adb shell input swipe <x> <y> <x> <y> 1000  # 同一点停留

获取坐标：
  $ adb shell settings put system pointer_location 1
  # 开发者选项 → 显示指针位置 → 查看坐标
```

**Q10：如何在不用 Android Studio 的情况下分析一个 APK？**

```
完整分析流程：
  ─────────────────────────────────────────────────────────────────────────
  1. 基本信息
     $ aapt dump badging app.apk
     $ aapt dump permissions app.apk

  2. 方法数分析（65K 限制）
     $ apkanalyzer dex references app.apk

  3. 大小分析
     $ apkanalyzer apk summary app.apk
     $ apkanalyzer files list app.apk

  4. 反编译查看源码
     $ jadx -d output app.apk

  5. DEX 分析
     $ unzip -p app.apk classes.dex | dexdump -f -

  6. 资源分析
     $ aapt dump resources app.apk
     $ aapt dump configurations app.apk

  7. 签名信息
     $ keytool -printcert -jarfile app.apk
     $ apksigner verify --print-certs app.apk
```

**Q11：adb shell dumpsys meminfo 的输出怎么看？**

```
关键指标解读：
  ─────────────────────────────────────────────────────────────────────────
  Pss（Proportional Set Size）：
  - 进程实际使用的物理内存（按比例分摊共享库）
  - 这是最有意义的指标，用于比较进程间内存

  关键字段：
  ─────────────────────────────────────────────────────────────────────────
  Native Heap    → C/C++ malloc 分配的内存（JNI/Bitmap 在旧版本）
  Dalvik Heap    → Java 堆（对象分配）
  .so mmap       → Native 库映射
  .dex mmap      → DEX 代码映射
  Graphics       → GPU 图形缓冲区
  Stack          → 线程栈
  TOTAL          → 总 Pss（最关注这个）

  Objects 部分：
  ─────────────────────────────────────────────────────────────────────────
  Views          → View 对象数量（Activity 泄漏时持续增长）
  Activities     → Activity 实例数（应该 == 栈中 Activity 数）

  排查步骤：
  ─────────────────────────────────────────────────────────────────────────
  1. 重点关注 TOTAL 行的 Pss Total
  2. 对比多次 dump，看哪个部分在增长
  3. Activities 数 > 预期 → Activity 泄漏
  4. Native Heap 增长 → Native 泄漏
```

**Q12：ADB 的 am 和 pm 命令有什么区别？**

```
am（Activity Manager）：
  ─────────────────────────────────────────────────────────────────────────
  管理应用运行时行为
  - am start       → 启动 Activity
  - am startservice→ 启动 Service
  - am broadcast   → 发送广播
  - am force-stop  → 强制停止应用
  - am dumpheap    → 导出堆内存
  - am monitor     → 监控 ANR/Crash

  pm（Package Manager）：
  ─────────────────────────────────────────────────────────────────────────
  管理应用包
  - pm install     → 安装 APK
  - pm uninstall   → 卸载应用
  - pm list packages → 列出应用
  - pm grant/revoke→ 授予/撤销权限
  - pm clear       → 清除应用数据
  - pm path        → 查看 APK 路径

  面试总结：
  ─────────────────────────────────────────────────────────────────────────
  am 管的是「运行中的应用」
  pm 管的是「安装的包」
  两者分别对应系统中 ActivityManagerService 和 PackageManagerService
```

---

### 18.5 综合面试题

**Q13：如何用 ADB 做自动化测试？**

```
基础方案：
  ─────────────────────────────────────────────────────────────────────────
  1. Monkey（压力测试）
     $ adb shell monkey -p com.example.app -v 10000
     --throttle 300            # 事件间隔
     --pct-touch 40            # 触摸占比
     --ignore-crashes          # 忽略 Crash 继续
     --hprof                   # Crash 时 dump 堆

  2. input 命令（精确操作）
     $ adb shell input tap 500 1000
     $ adb shell input swipe 500 1500 500 500
     $ adb shell input text "test"
     $ adb shell input keyevent KEYCODE_ENTER

  3. UIAutomator（Google 官方框架）
     $ adb shell uiautomator runtest test.jar -c com.example.Test

  高级方案：
  ─────────────────────────────────────────────────────────────────────────
  - Appium：跨平台自动化框架
  - UIAutomator2：Python 封装
  - scrcpy + 脚本：投屏 + 自动操作
```

**Q14：adb bugreport 包含哪些信息？怎么用？**

```
bugreport 是一份完整的设备诊断报告：

  生成方式：
  ─────────────────────────────────────────────────────────────────────────
  $ adb bugreport bugreport.zip    # Android 7+ 输出为 ZIP
  $ adb bugreport                  # 输出到当前目录

  内容：
  ─────────────────────────────────────────────────────────────────────────
  - 系统信息（build.prop、CPU、内存）
  - 系统日志（logcat 全缓冲区）
  - Kernel 日志（dmesg）
  - 所有 dumpsys 输出
  - ANR traces
  - Dropbox（系统错误日志）
  - 网络统计
  - 电池统计
  - 进程快照

  分析方式：
  ─────────────────────────────────────────────────────────────────────────
  1. 直接查看文本文件
  2. 使用 Battery Historian 分析电量
  3. 使用 bugreport 分析工具（Google 内部工具）
```

**Q15：如何用 ADB 调试多进程应用？**

```
# 查看应用的所有进程
$ adb shell ps | grep com.example
  u0_a123  12345  ...  com.example.app           # 主进程
  u0_a123  12346  ...  com.example.app:remote     # 远程服务进程
  u0_a123  12347  ...  com.example.app:push       # 推送进程

# 分别 dump 各进程
$ adb shell dumpsys meminfo 12345    # 主进程内存
$ adb shell dumpsys meminfo 12346    # remote 进程内存

# 查看各进程的日志
$ adb logcat --pid=12345
$ adb logcat --pid=12346

# 多进程调试注意事项：
  ─────────────────────────────────────────────────────────────────────────
  - Android Studio 默认只 attach 主进程
  - 需要在 Run Configuration 中选择多进程
  - 或使用 am set-debug-app -w 绑定特定进程
  - ContentProvider 运行在提供者进程，不在调用者进程
```

**Q16：adb shell dumpsys activity activities 输出怎么看？**

```
输出结构：
  ─────────────────────────────────────────────────────────────────────────
  Main stack:
    Task id #123
    * TaskRecord{xxx #123 A=com.example U=0}
      * ActivityRecord{xxx u0 com.example/.MainActivity}
        state=RESUMED

  关键信息：
  ─────────────────────────────────────────────────────────────────────────
  - Task id：任务 ID
  - Activity 列表：栈中所有 Activity（从底到顶）
  - state：当前状态（RESUMED/PAUSED/STOPPED/DESTROYED）
  - * 标记：表示当前在顶部的 Activity

  面试用途：
  ─────────────────────────────────────────────────────────────────────────
  - 检查 Activity 栈是否正确（启动模式是否生效）
  - 排查 Activity 泄漏（栈中是否有不该存在的 Activity）
  - 验证 taskAffinity 和 launchMode 配置
```

**Q17：如何用 ADB 实现应用的冷启动/热启动测试？**

```
冷启动测试：
  ─────────────────────────────────────────────────────────────────────────
  $ adb shell am force-stop com.example.app      # 杀掉进程
  $ adb logcat -c                                 # 清除日志
  $ adb shell am start -n com.example.app/.MainActivity
  $ adb logcat -d | grep "Displayed com.example"
  # 输出示例：Displayed com.example.app/.MainActivity: +1s234ms

  热启动测试：
  ─────────────────────────────────────────────────────────────────────────
  $ adb shell input keyevent KEYCODE_HOME         # 回到桌面（不杀进程）
  $ adb logcat -c
  $ adb shell am start -n com.example.app/.MainActivity
  $ adb logcat -d | grep "Displayed com.example"

  温启动测试：
  ─────────────────────────────────────────────────────────────────────────
  $ adb shell input keyevent KEYCODE_BACK         # 按返回（走 onStop）
  $ adb logcat -c
  $ adb shell am start -n com.example.app/.MainActivity
  $ adb logcat -d | grep "Displayed com.example"
```

**Q18：什么是 dropbox？如何用 ADB 查看？**

```
Dropbox 是 Android 系统的持久化错误日志系统：

  查看方式：
  ─────────────────────────────────────────────────────────────────────────
  $ adb shell dumpsys dropbox --print

  常见 Tag：
  ─────────────────────────────────────────────────────────────────────────
  SYSTEM_TOMBSTONE  → Native Crash 墓碑
  system_app_crash  → 系统 App Crash
  data_app_crash    → 第三方 App Crash
  SYSTEM_BOOT       → 系统启动时间
  BATTERY_DISCHARGE_INFO → 电池放电信息
  SYSTEM_WATCHDOG   → Watchdog 超时

  用途：
  ─────────────────────────────────────────────────────────────────────────
  - 查看历史 Crash（即使应用已不在运行）
  - 统计 Crash 频率
  - 分析 Native Crash 的 tombstone
  - 排查系统级问题
```

**Q19：如何通过 ADB 查看 Android 应用的网络请求？**

```
方式一：通过 dumpsys 查看统计
$ adb shell dumpsys netstats

方式二：抓包（tcpdump）
$ adb shell tcpdump -i any -s 0 -w /sdcard/capture.pcap
$ adb pull /sdcard/capture.pcap
# 用 Wireshark 分析

方式三：Charles/mitmproxy 代理
$ adb shell settings put global http_proxy <电脑IP>:8888
# 关闭代理
$ adb shell settings put global http_proxy :0

方式四：Android Studio Network Profiler
  - 仅支持 HttpURLConnection 和 OkHttp
  - 可以看到每个请求的 URL、状态码、Body

方式五：Stetho（Facebook 开源）
  - Chrome DevTools 查看网络请求
  - 需要代码集成
```

**Q20：adb shell 中的 monkey 命令怎么用？有哪些关键参数？**

```
Monkey 是 Android 自带的压力测试工具：

  基本用法：
  ─────────────────────────────────────────────────────────────────────────
  $ adb shell monkey -p com.example.app -v 10000

  关键参数：
  ─────────────────────────────────────────────────────────────────────────
  -p <package>       指定包名
  -v / -v -v -v -v   日志详细程度（1-3级）
  --throttle <ms>    事件间隔（默认无间隔）
  --seed <num>       随机种子（重现测试）
  --pct-touch <p>    触摸事件百分比
  --pct-motion <p>   滑动事件百分比
  --pct-nav <p>      导航键百分比
  --pct-appswitch <p> Activity 切换百分比
  --ignore-crashes   忽略 Crash 继续测试
  --ignore-timeouts  忽略 ANR 继续测试
  --hprof            Crash 时生成 Heap Dump
  --dbg-no-events    不发送事件（配合 --hprof 只做监控）

  推荐参数组合：
  ─────────────────────────────────────────────────────────────────────────
  $ adb shell monkey -p com.example.app \
      --throttle 300 \
      --pct-touch 40 \
      --pct-motion 25 \
      --pct-nav 10 \
      --ignore-crashes \
      --ignore-timeouts \
      --ignore-security-exceptions \
      -v -v 10000
```

---

## 19. 命令速查表

### 19.1 设备管理

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           设备管理速查                                       │
├─────────────────────────────────────┬────────────────────────────────────────┤
│              命令                    │              说明                      │
├─────────────────────────────────────┼────────────────────────────────────────┤
│ adb devices                         │ 列出设备                               │
│ adb connect <ip>:<port>             │ WiFi 连接                              │
│ adb disconnect                      │ 断开 WiFi 连接                        │
│ adb kill-server / start-server      │ 重启 ADB 服务                          │
│ adb reboot                          │ 重启设备                               │
│ adb reboot recovery                 │ 重启到 Recovery                        │
│ adb reboot bootloader               │ 重启到 Bootloader                      │
│ adb root                            │ 以 root 权限重启 adbd                  │
│ adb shell getprop ro.build.version.sdk│ 查看 API Level                        │
└─────────────────────────────────────┴────────────────────────────────────────┘
```

### 19.2 应用操作

```
┌─────────────────────────────────────┬────────────────────────────────────────┐
│              命令                    │              说明                      │
├─────────────────────────────────────┼────────────────────────────────────────┤
│ adb install [-r] app.apk            │ 安装 APK（-r 覆盖）                   │
│ adb uninstall [-k] <package>        │ 卸载（-k 保留数据）                   │
│ adb shell pm list packages [-3]     │ 列出应用（-3 仅第三方）               │
│ adb shell pm clear <package>        │ 清除应用数据                          │
│ adb shell pm grant <pkg> <perm>     │ 授予权限                              │
│ adb shell pm path <package>         │ 查看 APK 路径                        │
│ adb shell am start -n <comp>        │ 启动 Activity                         │
│ adb shell am force-stop <package>   │ 强制停止                              │
│ adb shell am broadcast -a <action>  │ 发送广播                              │
└─────────────────────────────────────┴────────────────────────────────────────┘
```

### 19.3 日志调试

```
┌─────────────────────────────────────┬────────────────────────────────────────┐
│              命令                    │              说明                      │
├─────────────────────────────────────┼────────────────────────────────────────┤
│ adb logcat                          │ 实时日志                               │
│ adb logcat -d                       │ dump 日志后退出                       │
│ adb logcat -c                       │ 清除日志                               │
│ adb logcat *:E                      │ 只显示 Error+                          │
│ adb logcat -s "Tag"                 │ 按 Tag 过滤                           │
│ adb logcat --pid=<pid>              │ 按 PID 过滤                           │
│ adb logcat -v threadtime            │ 详细时间+线程格式                     │
│ adb logcat -b crash                 │ 查看 Crash 缓冲区                    │
│ adb logcat -b main,system           │ 多缓冲区                              │
│ adb bugreport                       │ 导出完整诊断报告                      │
└─────────────────────────────────────┴────────────────────────────────────────┘
```

### 19.4 文件与屏幕

```
┌─────────────────────────────────────┬────────────────────────────────────────┐
│              命令                    │              说明                      │
├─────────────────────────────────────┼────────────────────────────────────────┤
│ adb push <local> <remote>           │ 推送文件                               │
│ adb pull <remote> [local]           │ 拉取文件                               │
│ adb shell ls -la <path>             │ 列出文件                               │
│ adb shell screencap -p <path>       │ 截图                                   │
│ adb shell screenrecord <path>       │ 录屏（最长 3 分钟）                   │
│ adb shell wm size                   │ 查看分辨率                             │
│ adb shell wm size 720x1280          │ 修改分辨率                             │
│ adb shell wm density                │ 查看密度                               │
└─────────────────────────────────────┴────────────────────────────────────────┘
```

### 19.5 性能与调试

```
┌─────────────────────────────────────┬────────────────────────────────────────┐
│              命令                    │              说明                      │
├─────────────────────────────────────┼────────────────────────────────────────┤
│ adb shell dumpsys meminfo <pkg>     │ 内存信息                               │
│ adb shell dumpsys activity top      │ 当前顶部 Activity                     │
│ adb shell dumpsys battery           │ 电池状态                               │
│ adb shell dumpsys gfxinfo <pkg>     │ GPU 渲染信息                          │
│ adb shell top -m 10                 │ CPU 使用率 Top 10                     │
│ adb shell ps -A                     │ 所有进程                               │
│ adb shell am dumpheap <pkg> <path>  │ 导出堆内存                            │
│ adb shell simpleperf record -p <pid>│ CPU Profiling                         │
│ adb shell dumpsys dropbox           │ 系统错误日志                          │
│ adb forward tcp:<port> tcp:<port>   │ 端口转发                              │
│ adb reverse tcp:<port> tcp:<port>   │ 反向端口转发                          │
└─────────────────────────────────────┴────────────────────────────────────────┘
```

---

> 作者：OpenClaw | 日期：2026-04-15
