# 二次元语音 MOD 工具包

这个项目用于制作 Darktide 角色语音 MOD，覆盖以下完整流程：

1. 角色工程初始化（职业模板 + 目录结构 + Lua 自动生成）
2. GPT-SoVITS 批量语音合成（网页工作台）
3. 音频增强与受击音效重命名处理

---

## 目录结构

```text
.
├─ mod_builder.py              # 角色工程生成核心逻辑（CLI）
├─ mod_builder_ui.py           # 角色工程生成图形界面（推荐）
├─ tts_tool.html               # GPT-SoVITS 批量合成工作台
├─ requirements.txt            # Python 依赖说明
├─ 职业/
│  ├─ adamant.lua
│  ├─ broker.lua
│  ├─ ogryn.lua
│  ├─ psyker.lua
│  ├─ veteran.lua
│  └─ zealot.lua
└─ 语音增强/
   ├─ boost_volume.py          # 常规语音增强
   └─ rename_audio.py          # 受击音效重命名+增强
```

---

## 环境要求

- Windows 10/11（推荐）
- Python 3.9+
- `ffmpeg`（加入系统 PATH）
- Chrome / Edge（用于 `tts_tool.html` 的目录读写权限）
- GPT-SoVITS API 服务（默认 `http://127.0.0.1:9880`）

---

## 安装依赖

```powershell
python -m pip install -r requirements.txt
```

当前 Python 依赖：

- `customtkinter`（用于 `mod_builder_ui.py` 图形界面）

---

## 快速开始

### 第 1 步：初始化角色工程

推荐使用图形界面：

```powershell
python mod_builder_ui.py
```

在界面中选择：

- 职业（`broker / adamant / zealot / veteran / psyker / ogryn`）
- 角色名（例如：`阿卡赛特`）
- 角色代号（例如：`Akaset`）
- 语言（`ja / chs / en` 可多选）
- 输出目录

点击「一键生成项目」后会自动创建：

- `<角色名>/<角色代号>.lua`
- `audio/loc_xxx/<角色代号>/`
- `audio/wwise/events/player/play_xxx/<角色代号>/`
- `cartoon_preview/<职业>/<角色代号>/`

并自动创建受击音效常用子目录（`catapulted`、`hurt_heavy`、`play_syringe_*` 等）。

---

### 第 2 步：批量语音合成（GPT-SoVITS）

打开 `tts_tool.html`，按顺序操作：

1. **模型加载**
   - 填 API 地址（默认 `http://127.0.0.1:9880`）
   - 填 GPT 模型路径（`.ckpt`）并加载
   - 填 SoVITS 模型路径（`.pth`）并加载
2. **推理参数**
   - 参考音频绝对路径（必填）
   - 参考文本
   - 参考语言 / 目标语言 / 输出格式
3. **文件导入**
   - 导入第 1 步生成的 Lua
   - 选择输出目录（建议选 `audio/loc_xxx/<角色代号>`）
   - 可选导入翻译 TXT

支持功能：

- 批量生成
- 单条重生成
- 试听
- 导出待处理清单
- 智能扫描与匹配

---

### 第 3 步：语音增强

#### 3.1 常规语音（loc）

将合成后的音频放入 `语音增强/input_aac`，执行：

```powershell
python 语音增强/boost_volume.py
```

#### 3.2 受击语音（wwise）

在 `audio/wwise/events/player/play_xxx/<角色代号>/` 对应目录中放好受击音频后并且将语音增强文件夹下的rename_audio.py放到该目录，在这个目录下执行：

```powershell
python rename_audio.py
```

脚本支持两种模式：

- `normal`：序号重命名 + 音量处理
- `fix`：保留文件名 + 音量处理

---

## 翻译 TXT 格式说明（用于日语/英语）

格式必须是：

1. 一行组名（例如 `ja_loc_adamant_male_a__guidance_correct_path_`）
2. 一行固定标题：`待处理台词`
3. 后续按“中文一行 + 翻译一行”交替

示例：

```text
ja_loc_adamant_male_a__guidance_correct_path_
待处理台词
保持队形，继续前进。
隊形を保って、進み続け。

按既定路线行进。
既定のルートに沿って進む。
```

---

## 命令行用法（可选）

不使用图形界面时可以直接：

```powershell
python mod_builder.py -p adamant -n 阿卡赛特 -c Akaset -l ja chs en -o .
```

参数说明：

- `-p` 职业代号
- `-n` 角色名
- `-c` 角色代号（仅字母/数字/下划线）
- `-l` 语言列表（`ja chs en`）
- `-o` 输出目录



## 常见问题

### 1) `ffmpeg` 找不到

执行 `ffmpeg -version` 检查环境变量；未通过则安装 ffmpeg 并加入 PATH。

### 2) 网页无法读写本地目录

请使用最新版 Chrome/Edge，并在页面弹窗中授予目录权限。

### 3) 模型加载失败

确认 GPT-SoVITS API 已启动，且模型路径使用绝对路径。

### 4) 角色名未替换到台词说话人

请使用当前版本 `mod_builder.py` 重新生成 Lua，`add_subtext("...")` 说话人会自动改成角色名。
