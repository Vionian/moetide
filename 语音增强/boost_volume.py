import os
import subprocess
from pathlib import Path

# ================= 配置区域 =================
INPUT_DIR = "input_aac"
OUTPUT_DIR = "noa" 

# 想要增加的分贝数
VOLUME_GAIN = "10dB" 

# 限制器阈值 (0.9 防止削波)
LIMIT_LEVEL = "0.9"
# ===========================================

def boost_volume_aggressive():
    input_path = Path(INPUT_DIR)
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"错误: 输入目录 '{INPUT_DIR}' 不存在。")
        return

    # 修改 1: 同时查找 .aac 和 .wav 文件 (忽略大小写)
    supported_extensions = {'.aac', '.wav'}
    files = [
        f for f in input_path.iterdir() 
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]
    
    if not files:
        print(f"在 '{INPUT_DIR}' 中未找到 .aac 或 .wav 文件。")
        return

    print(f"找到 {len(files)} 个音频文件。")
    print(f"准备执行: 增益 +{VOLUME_GAIN} 并启用硬限制器...")

    for file in files:
        output_file = output_path / file.name
        file_ext = file.suffix.lower()
        
        # 核心滤镜逻辑 (通用)
        filter_cmd = f"volume={VOLUME_GAIN},alimiter=limit={LIMIT_LEVEL}:attack=5:release=50"

        # 基础命令
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(file),
            "-filter:a", filter_cmd
        ]

        # 修改 2: 根据后缀名决定输出编码格式
        if file_ext == '.aac':
            # AAC 依然使用有损压缩，指定比特率
            cmd.extend([
                "-c:a", "aac",
                "-b:a", "256k"
            ])
        elif file_ext == '.wav':
            # WAV 使用 PCM 16位编码 (无损，标准格式)
            # 注意：WAV 不需要指定比特率(-b:a)，因为它是由采样率和位深决定的
            cmd.extend([
                "-c:a", "pcm_s16le"
            ])

        cmd.append(str(output_file))

        print(f"正在处理 [{file_ext[1:].upper()}]: {file.name} ...")
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  -> 完成")
        except subprocess.CalledProcessError:
            print(f"  -> {file.name} 处理失败！")
        except FileNotFoundError:
             print("  -> 错误: 找不到 ffmpeg，请确保已安装并配置环境变量。")
             break

    print(f"\n所有任务完成！文件在 '{OUTPUT_DIR}' 文件夹中。")

if __name__ == "__main__":
    boost_volume_aggressive()