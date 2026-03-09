import os
import subprocess
from pathlib import Path

# ================= ⚙️ 配置区域 =================

# 🔴 运行模式: 修改此处切换模式 ("normal" 或 "fix")
# normal: 序列化重命名 (1.wav, 2.wav...) + 调整音量 + 限制器
# fix:    保持原文件名 + 调整音量 (用于修复或微调)
OPERATION_MODE = "normal" 

# 限制器阈值 (仅 Normal 模式生效)
LIMIT_LEVEL = "0.9"

# ===============================================

SUPPORTED_EXTENSIONS = {'.aac', '.wav', '.ogg', '.mp3', '.flac'}

def run_ffmpeg(input_file, output_file, filter_cmd):
    """封装 FFmpeg 调用"""
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(input_file),
        "-filter:a", filter_cmd,
        "-c:a", "pcm_s16le", 
        "-ar", "44100",
        str(output_file)
    ]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise Exception("未找到 ffmpeg，请检查环境变量配置")
    except subprocess.CalledProcessError:
        raise Exception("FFmpeg 处理出错（可能是文件损坏或被占用）")

def process_folder_normal(folder, target_db):
    """【正常模式】重命名 + 调整音量 (无标记文件检测)"""
    
    # 1. 获取所有支持的音频文件
    files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]
    files.sort(key=lambda x: x.name)

    if not files: return 0
    print(f"📂 [Normal] 处理中: {folder.name}")

    # 2. 全部重命名为临时文件，防止命名冲突
    temp_files = []
    for f in files:
        temp_name = folder / f"temp_{f.name}"
        try:
            f.rename(temp_name)
            temp_files.append(temp_name)
        except: pass

    # 3. 逐个处理并重命名为序号
    count = 0
    for i, temp_file in enumerate(temp_files, start=1):
        output_wav = folder / f"{i}.wav"
        
        # 动态使用输入的分贝值
        filter_cmd = f"volume={target_db},alimiter=limit={LIMIT_LEVEL}:attack=5:release=50"
        
        try:
            run_ffmpeg(temp_file, output_wav, filter_cmd)
            os.remove(temp_file)
            count += 1
            print(f"   ✅ [{i}] {output_wav.name} (音量 {target_db})")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            # 如果失败，尝试还原文件名
            if temp_file.exists():
                original_name = temp_file.name.replace("temp_", "")
                temp_file.rename(folder / original_name)

    return count

def process_folder_fix(folder, target_db):
    """【修复模式】不重命名 + 调整音量"""
    files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == '.wav']
    files.sort(key=lambda x: x.name)

    if not files: return 0
    print(f"🔧 [Fix] 正在调整音量: {folder.name}")

    count = 0
    for f in files:
        # 创建临时文件
        temp_fix = folder / f"fix_temp_{f.name}"
        
        try:
            # 1. 先把原文件改名为临时文件
            f.rename(temp_fix)
            
            # 2. FFmpeg: temp -> 原文件名 (使用输入的分贝值)
            filter_cmd = f"volume={target_db}"
            
            run_ffmpeg(temp_fix, f, filter_cmd)
            
            # 3. 删除临时文件
            os.remove(temp_fix)
            count += 1
            print(f"   🔄 {f.name} ({target_db}) 成功")
            
        except Exception as e:
            print(f"   ❌ 处理失败: {f.name}")
            print(f"      原因: {e}")
            # 尝试还原文件
            if temp_fix.exists(): 
                if f.exists(): os.remove(f)
                temp_fix.rename(f)

    return count

def main():
    root_dir = Path(".")
    subfolders = sorted([f for f in root_dir.iterdir() if f.is_dir()])

    if not subfolders:
        print("未发现文件夹。")
        return

    print(f"=== 音频处理脚本 | 当前模式: {OPERATION_MODE.upper()} ===")
    
    if OPERATION_MODE == "normal":
        print(f"功能: 序列化重命名 (1.wav...) + 音量调整 + 限制器")
    elif OPERATION_MODE == "fix":
        print(f"功能: 保持文件名 + 仅调整音量")
    
    # === 新增：交互式输入分贝 ===
    db_input = input("\n🎚️  请输入要调整的分贝数值 (例如 10 或 -5): ").strip()
    
    # 简单的格式处理，确保带有 dB 单位
    if not db_input:
        print("❌ 未输入数值，程序退出。")
        return
    
    target_db = db_input
    if not target_db.lower().endswith("db"):
        target_db += "dB"

    print(f"\n⚙️  设定调整值为: {target_db}")
    
    confirm = input("⚠️  确认开始吗? (y/n): ")
    if confirm.lower() != 'y': return

    summary_data = {}

    for folder in subfolders:
        if OPERATION_MODE == "normal":
            # 传入 target_db
            count = process_folder_normal(folder, target_db)
        else:
            # 传入 target_db
            count = process_folder_fix(folder, target_db)
        
        if count > 0: summary_data[folder.name] = count

    print("\n" + "="*40)
    print("           处理结果统计           ")
    print("="*40)
    total = 0
    for name, count in summary_data.items():
        print(f"{name}：{count}个音频文件")
        total += count
    print("-" * 40)
    print(f"总计处理：{total} 个文件")

if __name__ == "__main__":
    main()