# 二次元语音 MOD 工具包使用教程

本工具包基于[EBuyToDeep](https://space.bilibili.com/1273948298?spm_id_from=333.1387)制作的二次元语音mod，用于制作自定义角色语音包，核心流程是：

1. 生成角色工程（Lua + 目录）
2. 使用 GPT-SoVITS 批量合成语音
3. 对语音做增强和受击音效重命名
4. 打包放入 MOD 目录测试

---

## 1. 项目文件说明

```text
.
├─ mod_builder_ui.py           # 图形化角色工程生成器（推荐）
├─ mod_builder.py              # 命令行角色工程生成器
├─ tts_tool.html               # 批量语音合成页面
├─ requirements.txt            # Python 依赖
├─ 职业/                        # 6个职业基础模板
│  ├─ adamant.lua
│  ├─ broker.lua
│  ├─ ogryn.lua
│  ├─ psyker.lua
│  ├─ veteran.lua
│  └─ zealot.lua
└─ 语音增强/
   ├─ boost_volume.py          # 常规台词音量增强
   └─ rename_audio.py          # 受击音效重命名+增强
```

---

## 2. 环境准备

### 2.1 系统与软件

- Windows 10/11
- Python 3.9+
- ffmpeg（必须加入 PATH）
- Chrome / Edge（用于打开 `tts_tool.html`）
- GPT-SoVITS（本地部署）

### 2.2 安装 Python 依赖

```powershell
python -m pip install -r requirements.txt
```

`requirements.txt` 当前依赖：

- `customtkinter>=5.2.2`

### 2.3 检查 ffmpeg

```powershell
ffmpeg -version
```

能输出版本号才表示可用。

---

## 3. 启动 GPT-SoVITS API

进入你的 GPT-SoVITS 目录后，执行：

```powershell
runtime\python.exe api_v2.py
```

默认 API 地址一般是：

`http://127.0.0.1:9880`

> 建议：参考音频尽量使用 **WAV 格式**，稳定性和音质通常比压缩格式更好。

---

## 4. 第一步：生成角色工程

推荐图形界面：

```powershell
python mod_builder_ui.py
```

### 4.1 需要填写

- 职业：`broker / adamant / zealot / veteran / psyker / ogryn`
- 角色名：例如 `阿卡赛特`
- 角色代号：例如 `Akaset`（英文字母/数字/下划线）
- 语言：`ja`、`chs`、`en`（可多选）
- 输出目录

点击「一键生成项目」后会自动创建：

- `<角色名>/<角色代号>.lua`
- `audio/loc_xxx/<角色代号>/`
- `audio/wwise/events/player/play_xxx/<角色代号>/`
- `cartoon_preview/<职业>/<角色代号>/`

其中 `Lua` 内会自动完成：

- 角色代号替换
- 语言后缀替换（`_ja` / `_chs` / `_en`）
- `add_subtext("说话人")` 自动改为角色名

---

## 5. 第二步：批量语音合成（tts_tool.html）

双击或浏览器打开 `tts_tool.html`。

### 5.1 模型加载控制台

1. 填 API 地址（默认 `http://127.0.0.1:9880`）
2. 选择 GPT 模型路径（`.ckpt`）并点击加载
3. 选择 SoVITS 模型路径（`.pth`）并点击加载

### 5.2 推理参数配置

1. 填参考音频绝对路径（必填，推荐 WAV）
2. 填参考音频对应文本
3. 选择参考语言 / 目标语言 / 输出格式

### 5.3 文件与导入

1. 导入第 4 步生成的 Lua
2. 选择输出目录（建议选 `audio/loc_xxx/<角色代号>`）
3. 可选导入翻译 TXT（用于日语/英语）
4. 点击批量生成

页面功能：

- 批量生成
- 单条重生成
- 试听
- 导出待处理清单
- 智能扫描与匹配
- 批量导出

---

## 6. 翻译 TXT 格式（用于 ja/en）

格式要求：

1. 第一行是组名（例如 `ja_loc_adamant_male_a__guidance_correct_path_`）
2. 第二行固定是 `待处理台词`
3. 后续为“中文一行 + 翻译一行”交替

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

## 7. 第三步：语音增强

## 7.1 常规台词增强（loc）

把 `audio/loc_xxx/<角色代号>/` 下的语音复制到 `语音增强/input_aac`，然后运行：

```powershell
python boost_volume.py
```

## 7.2 受击语音处理（wwise）注意，该步骤不是必须，如果角色没有相应的音效则不用管

在角色目录：

`audio/wwise/events/player/play_xxx/<角色代号>/`

放入受击音频后并且将语音增强文件夹下的rename_audio.py放到该目录，在这个目录下执行，执行完毕后根据终端对lua代码里的对应部分进行修改：

```powershell
python rename_audio.py
```

脚本模式：

- `normal`：序号重命名 + 音量处理
- `fix`：保留原名 + 音量处理

---

## 8. 受击音效类型说明

- `attack_long`：近战蓄力重击
- `attack_short`：近战轻击
- `catapulted`：瘫痪，比如被炸飞或者挂边
- `catapulted_land`：被击飞后落地的重喘
- `land_heavy`：高处落地的轻喘
- `hurt_light`：轻伤
- `hurt_heavy`：受重伤或倒地
- `jump`：跳跃
- `scream_long`：尖叫
- `struggle_heavy`：不要管
- `getting_up`：不要管
- `grunt_short`：推开敌人的动作声音（比如“哼”的一声）
- `healing`：治疗
- `play_syringe`：三种扎针音效（约 15 秒）

---

## 9. 命令行用法（可选）

不使用图形界面时可直接：

```powershell
python mod_builder.py -p adamant -n 阿卡赛特 -c Akaset -l ja chs en -o .
```

参数：

- `-p`：职业代号
- `-n`：角色名
- `-c`：角色代号
- `-l`：语言列表（可多个）
- `-o`：输出目录

---

## 10. 常见问题

### 10.1 `ffmpeg` 找不到

确认 `ffmpeg -version` 可执行，不行就重新配置 PATH。

### 10.2 网页无法选择目录

请使用最新版 Chrome/Edge，并允许页面访问本地目录。

### 10.3 模型加载失败

确认 GPT-SoVITS 已用 `runtime\python.exe api_v2.py` 启动，且路径是绝对路径。

### 10.4 合成音色不稳定

优先使用干净的 **WAV 参考音频**，并确保参考文本与音频内容一致。

---

## 11. 测试网站

`moetide.top` 是用于测试自定义角色包选择的网站。  
感兴趣可以查看一下。
