# BestHolidays

BestHolidays 是一个面向 Windows 的休息日提醒小工具。

它会根据本地节假日与调休数据，自动判断近期是否临近休息日，并在指定时间通过 Windows 系统通知进行提醒。程序支持后台运行，并提供系统托盘图标，可以通过右键菜单直接退出，不需要手动打开任务管理器结束进程。

---

## 功能特性

- 自动读取本地节假日与调休数据
- 判断工作日、周末、法定节假日、调休工作日
- 支持每日定时检查
- 临近休息日前自动发送 Windows 系统通知
- 后台运行，无需控制台窗口
- 支持系统托盘图标
- 支持右键托盘图标退出程序
- 支持通过配置文件修改提醒时间
- 支持使用 PyInstaller 打包为 Windows 可执行程序

---

## 适用场景

如果你经常忘记：

- 明天是不是休息日
- 这周有没有调休
- 哪天开始放假
- 今天是不是休息前最后一个工作日

那么这个小工具可以在每天固定时间自动提醒你。

---

## 下载与使用

### 使用打包版本

注意：不要只单独拿出 `scheduler.exe` 运行。程序需要依赖同目录下的 `_internal` 文件夹。

解压后的目录结构通常类似：

```text
scheduler/
├─ scheduler.exe
├─ _internal/
```

双击运行：

```text
scheduler.exe
```

程序启动后会在右下角系统托盘显示图标，并在启动时发送一条通知，表示程序已经开始后台运行。

---

## 如何退出程序

程序运行后，会在 Windows 任务栏右下角显示托盘图标。

右键托盘图标，选择：

```text
退出
```

即可正常关闭程序。

如果没有看到图标，可以点击任务栏右下角的上箭头，查看隐藏的托盘图标。

---

## 配置提醒时间

提醒时间由 `settings.json` 控制。

示例：

```json
{
  "remind_hour": 14,
  "remind_start_minute": 0,
  "remind_end_minute": 10,
  "check_interval_seconds": 30
}
```

字段说明：

| 字段 | 说明 |
|---|---|
| `remind_hour` | 提醒小时，24 小时制 |
| `remind_start_minute` | 提醒时间窗口开始分钟 |
| `remind_end_minute` | 提醒时间窗口结束分钟 |
| `check_interval_seconds` | 后台检查间隔，单位为秒 |

例如上面的配置表示：

```text
每天 14:00 到 14:10 之间检查一次是否需要提醒
```

如果当天已经提醒过，则不会重复提醒。

---

## 节假日数据

节假日与调休数据由 `holidays.json` 控制。

示例：

```json
{
  "holidays": [
    "2026-01-01",
    "2026-02-16",
    "2026-02-17"
  ],
  "workdays": [
    "2026-02-14",
    "2026-02-15"
  ]
}
```

字段说明：

| 字段 | 说明 |
|---|---|
| `holidays` | 法定节假日或额外休息日 |
| `workdays` | 调休工作日 |

程序会综合判断：

- `holidays` 中的日期视为休息日
- `workdays` 中的日期视为工作日
- 普通周六、周日默认视为休息日
- 普通周一至周五默认视为工作日

---

## 提醒逻辑

程序主要会判断以下几种情况。

### 明天开始休息

如果明天是休息日，程序会提醒：

```text
提醒：明天开始休息
开始时间：YYYY-MM-DD 周X
结束时间：YYYY-MM-DD 周X
共 X 天
```

### 今天是休息前最后一个工作日

如果后天开始休息，并且今天是最后一个工作日，程序会提醒：

```text
提醒：今天是休息前最后一个工作日
休息将于：YYYY-MM-DD 周X 开始
休息到：YYYY-MM-DD 周X
共 X 天
```

### 后天开始休息

如果后天开始休息，程序会提醒：

```text
提醒：后天开始休息
开始时间：YYYY-MM-DD 周X
结束时间：YYYY-MM-DD 周X
共 X 天
```

### 近期没有临近休息日

如果近期没有临近休息日，程序不会发送正式休息提醒。

---

## 开机自启动

如果希望程序开机自动运行，可以将 `scheduler.exe` 的快捷方式放入 Windows 启动文件夹。

操作方式：

1. 按下 `Win + R`
2. 输入：

```text
shell:startup
```

3. 回车
4. 将 `scheduler.exe` 的快捷方式复制到打开的文件夹中

注意：建议放入快捷方式，而不是直接复制整个 exe 文件。

---

## 从源码运行

如果你想直接运行源码，需要先安装依赖：

```bash
pip install plyer pystray pillow
```

然后在项目根目录运行：

```bash
python scheduler.py
```

建议先进入项目目录：

```bash
cd BestHolidays
python scheduler.py
```

---

## 源码运行说明

源码运行时，程序会读取项目目录下的资源文件：

```text
BestHolidays/
├─ main.py
├─ scheduler.py
├─ holidays.json
├─ settings.json
├─ holiday.ico
```

其中：

| 文件 | 说明 |
|---|---|
| `main.py` | 日期判断与提醒文本生成 |
| `scheduler.py` | 后台定时检查、系统通知、托盘图标与退出逻辑 |
| `holidays.json` | 节假日与调休数据 |
| `settings.json` | 提醒时间配置 |
| `holiday.ico` | 程序图标与托盘图标 |

---

## 打包方式

本项目使用 PyInstaller 打包为 Windows 可执行程序。

安装 PyInstaller：

```bash
pip install pyinstaller
```

在项目根目录执行：

```bash
pyinstaller scheduler.spec
```

打包完成后，生成文件位于：

```text
dist/scheduler/
```

目录结构通常类似：

```text
dist/
└─ scheduler/
   ├─ scheduler.exe
   └─ _internal/
```

分发时请压缩整个 `dist/scheduler` 文件夹，而不是只分发单个 `scheduler.exe`。

---

## 重新打包建议

如果修改了代码、图标或配置后需要重新打包，建议先删除旧的打包产物：

```text
build/
dist/
__pycache__/
```

然后重新执行：

```bash
pyinstaller scheduler.spec
```

其中：

| 目录 | 说明 |
|---|---|
| `build/` | PyInstaller 的临时构建目录 |
| `dist/` | 最终打包输出目录 |
| `__pycache__/` | Python 运行缓存目录 |

这些目录都可以重新生成。

---

## 项目文件说明

| 文件 / 文件夹 | 说明 |
|---|---|
| `main.py` | 日期判断、休息日判断、提醒文本生成 |
| `scheduler.py` | 后台定时器、系统通知、托盘图标、右键退出 |
| `holidays.json` | 节假日与调休数据 |
| `settings.json` | 提醒时间与检查间隔配置 |
| `holiday.ico` | 程序图标与托盘图标 |
| `scheduler.spec` | PyInstaller 打包配置 |
| `README.md` | 项目说明文档 |
| `LICENSE` | 项目许可证 |
| `build/` | PyInstaller 临时构建目录，可删除 |
| `dist/` | PyInstaller 输出目录，用于分发 |
| `__pycache__/` | Python 缓存目录，可删除 |

---

## 常见问题

### 为什么运行后没有看到窗口？

这是正常现象。

BestHolidays 是后台提醒工具，默认不会打开主窗口。请查看 Windows 任务栏右下角托盘区域。

### 为什么任务栏没有看到图标？

可能是图标被 Windows 收进了隐藏托盘区域。

请点击任务栏右下角的上箭头，查看隐藏图标。

### 为什么没有弹出通知？

请检查：

- Windows 系统通知是否开启
- 是否开启了勿扰模式
- 程序是否已经在后台运行
- `settings.json` 中的提醒时间窗口是否正确
- `holidays.json` 中是否配置了对应日期

### 为什么不能只发 `scheduler.exe`？

因为默认打包方式是文件夹模式，`scheduler.exe` 依赖 `_internal` 文件夹中的运行库和资源文件。

请分发整个：

```text
dist/scheduler/
```

而不是单独分发 exe。

### 能不能打包成单文件 exe？

理论上可以使用 PyInstaller 的 `--onefile` 模式。

但本项目依赖图标、JSON 配置文件和日志写入。为了方便调试与修改配置，当前更推荐使用文件夹模式分发。

### 节假日会自动更新吗？

不会。

本工具使用本地 `holidays.json` 数据，不会联网获取最新节假日安排。

如果国家法定节假日或调休安排发生变化，需要手动更新 `holidays.json`。

### 重复启动会怎么样？

如果重复运行程序，可能会出现多个托盘图标，也可能会发送多次启动通知。

如果发生这种情况，请右键托盘图标逐个退出，或者在任务管理器中结束多余进程。

---

## 后续计划

可能加入的功能：

- 图形化设置界面
- 自动更新节假日数据
- 开机自启动开关
- 防止重复启动
- 自定义提醒文案
- 更清晰的日志查看功能

---

## License

本项目基于仓库中的 `LICENSE` 文件授权。