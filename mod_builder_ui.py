#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import mod_builder

# 全局设置 CustomTkinter 主题为明亮模式，颜色主题为绿/蓝
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("二次元语音 MOD - 角色工程生成器")
        self.geometry("960x720")
        self.minsize(920, 680)
        
        # 现代柔和背景色
        self.configure(fg_color="#F4F7F8")

        # 变量初始化
        self.prof_var = ctk.StringVar(value="psyker")
        self.name_var = ctk.StringVar()
        self.code_var = ctk.StringVar()
        self.out_var = ctk.StringVar(value=str(Path(".").resolve()))
        self.status_var = ctk.StringVar(value="等待输入参数")
        self.lang_vars = {
            "ja": ctk.BooleanVar(value=True),
            "chs": ctk.BooleanVar(value=False),
            "en": ctk.BooleanVar(value=False),
        }

        # 字体统一定义
        self.font_title = ctk.CTkFont(family="Microsoft YaHei UI", size=22, weight="bold")
        self.font_subtitle = ctk.CTkFont(family="Microsoft YaHei UI", size=13)
        self.font_section = ctk.CTkFont(family="Microsoft YaHei UI", size=15, weight="bold")
        self.font_label = ctk.CTkFont(family="Microsoft YaHei UI", size=13, weight="bold")
        self.font_text = ctk.CTkFont(family="Microsoft YaHei UI", size=13)
        self.font_code = ctk.CTkFont(family="Consolas", size=13)

        self._build_ui()

    def _build_ui(self) -> None:
        # ================= 顶部卡片 (Hero) =================
        # corner_radius 实现真正的圆角
        hero_card = ctk.CTkFrame(self, fg_color="#E6F0EE", corner_radius=12)
        hero_card.pack(fill="x", padx=20, pady=(20, 10))

        # 内部使用网格布局
        hero_card.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(hero_card, text="角色工程初始化", font=self.font_title, text_color="#1A202C").grid(row=0, column=0, sticky="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(hero_card, text="自动生成 Lua + audio/wwise/cartoon_preview 完整结构", font=self.font_subtitle, text_color="#4A5568").grid(row=1, column=0, sticky="w", padx=24, pady=(0, 20))
        
        ctk.CTkLabel(hero_card, textvariable=self.status_var, font=self.font_subtitle, text_color="#0D9488").grid(row=0, column=1, rowspan=2, sticky="e", padx=24)

        # ================= 配置卡片 =================
        config_card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E2E8F0")
        config_card.pack(fill="x", padx=20, pady=10)
        
        # 增加内边距的容器
        c_inner = ctk.CTkFrame(config_card, fg_color="transparent")
        c_inner.pack(fill="x", padx=24, pady=24)

        ctk.CTkLabel(c_inner, text="参数配置", font=self.font_section, text_color="#2D3748").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 16))

        # --- 职业 ---
        ctk.CTkLabel(c_inner, text="职业", font=self.font_label, text_color="#4A5568").grid(row=1, column=0, sticky="w", pady=8)
        prof_box = ctk.CTkComboBox(
            c_inner, 
            values=list(mod_builder.PROFESSIONS.keys()), 
            variable=self.prof_var,
            command=self._sync_profession_hint,
            font=self.font_text,
            dropdown_font=self.font_text,
            corner_radius=6,          # 圆角下拉框
            border_width=1,
            border_color="#CBD5E1",
            button_color="#CBD5E1",
            button_hover_color="#94A3B8",
            width=200
        )
        prof_box.grid(row=1, column=1, sticky="w", pady=8)
        
        self.prof_hint = ctk.CTkLabel(c_inner, text="", font=self.font_text, text_color="#718096")
        self.prof_hint.grid(row=1, column=2, columnspan=2, sticky="w", padx=(16, 0))

        # --- 角色名与代号 ---
        ctk.CTkLabel(c_inner, text="角色名", font=self.font_label, text_color="#4A5568").grid(row=2, column=0, sticky="w", pady=8)
        ctk.CTkEntry(
            c_inner, textvariable=self.name_var, font=self.font_text, 
            corner_radius=6, border_width=1, border_color="#CBD5E1", width=200
        ).grid(row=2, column=1, sticky="w", pady=8)

        ctk.CTkLabel(c_inner, text="角色代号", font=self.font_label, text_color="#4A5568").grid(row=2, column=2, sticky="w", padx=(30, 0), pady=8)
        ctk.CTkEntry(
            c_inner, textvariable=self.code_var, font=self.font_text,
            corner_radius=6, border_width=1, border_color="#CBD5E1", width=200
        ).grid(row=2, column=3, sticky="w", pady=8)

        # --- 语言复选框 ---
        ctk.CTkLabel(c_inner, text="语言", font=self.font_label, text_color="#4A5568").grid(row=3, column=0, sticky="nw", pady=16)
        lang_frame = ctk.CTkFrame(c_inner, fg_color="transparent")
        lang_frame.grid(row=3, column=1, columnspan=3, sticky="w", pady=16)
        
        ctk.CTkCheckBox(lang_frame, text="日语 (ja)", variable=self.lang_vars["ja"], font=self.font_text, corner_radius=4).pack(side="left", padx=(0, 24))
        ctk.CTkCheckBox(lang_frame, text="汉语 (chs)", variable=self.lang_vars["chs"], font=self.font_text, corner_radius=4).pack(side="left", padx=(0, 24))
        ctk.CTkCheckBox(lang_frame, text="英语 (en)", variable=self.lang_vars["en"], font=self.font_text, corner_radius=4).pack(side="left")

        # --- 输出目录 ---
        ctk.CTkLabel(c_inner, text="输出目录", font=self.font_label, text_color="#4A5568").grid(row=4, column=0, sticky="w", pady=8)
        out_frame = ctk.CTkFrame(c_inner, fg_color="transparent")
        out_frame.grid(row=4, column=1, columnspan=3, sticky="we", pady=8)
        out_frame.columnconfigure(0, weight=1)
        
        ctk.CTkEntry(
            out_frame, textvariable=self.out_var, font=self.font_text,
            corner_radius=6, border_width=1, border_color="#CBD5E1"
        ).grid(row=0, column=0, sticky="we")
        
        ctk.CTkButton(
            out_frame, text="浏览...", command=self._pick_outdir, font=self.font_text,
            fg_color="#EDF2F7", text_color="#2D3748", hover_color="#E2E8F0", 
            corner_radius=6, width=80
        ).grid(row=0, column=1, padx=(12, 0))

        # --- 操作按钮区 ---
        op_frame = ctk.CTkFrame(c_inner, fg_color="transparent")
        op_frame.grid(row=5, column=0, columnspan=4, sticky="w", pady=(24, 4))
        
        ctk.CTkButton(
            op_frame, text="一键生成项目", command=self._run_build, font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold"),
            fg_color="#0D9488", hover_color="#0F766E", corner_radius=8, height=42, width=160
        ).pack(side="left")
        
        ctk.CTkButton(
            op_frame, text="清空日志", command=self._clear_log, font=ctk.CTkFont(family="Microsoft YaHei UI", size=13, weight="bold"),
            fg_color="#F59E0B", hover_color="#D97706", corner_radius=8, height=42, width=100
        ).pack(side="left", padx=(16, 0))

        # ================= 日志卡片 =================
        log_card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E2E8F0")
        log_card.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        l_inner = ctk.CTkFrame(log_card, fg_color="transparent")
        l_inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(l_inner, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header_frame, text="执行日志", font=self.font_section, text_color="#2D3748").pack(side="left")
        ctk.CTkLabel(header_frame, text="※ 输出结构会自动创建目录 | Lua 可直接导入 tts_tool.html", font=self.font_text, text_color="#718096").pack(side="right")

        # 现代风代码终端风格文本框
        self.log = ctk.CTkTextbox(
            l_inner,
            font=self.font_code,
            fg_color="#1E293B",        # 深蓝灰极客底色
            text_color="#F8FAFC",      # 亮白字体
            corner_radius=8,
            border_width=0
        )
        self.log.pack(fill="both", expand=True)

        # 初始化提示文字
        self._sync_profession_hint()

    def _sync_profession_hint(self, choice=None) -> None:
        p = mod_builder.PROFESSIONS[self.prof_var.get()]
        self.prof_hint.configure(text=f"{p.name_cn}  |  {p.loc_root}")

    def _pick_outdir(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.out_var.get() or ".")
        if selected:
            self.out_var.set(selected)

    def _selected_langs(self) -> list[str]:
        return [k for k, v in self.lang_vars.items() if v.get()]

    def _append_log(self, text: str) -> None:
        self.log.insert("end", text + "\n")
        self.log.see("end")

    def _clear_log(self) -> None:
        self.log.delete("1.0", "end")
        self.status_var.set("日志已清空，等待下一次生成")

    def _run_build(self) -> None:
        try:
            profession = mod_builder.PROFESSIONS[self.prof_var.get()]
            char_name = self.name_var.get().strip()
            if not char_name:
                raise mod_builder.BuilderError("角色名不能为空。")

            char_code = mod_builder._validate_code(self.code_var.get())
            langs = mod_builder._validate_languages(self._selected_langs())
            outdir = Path(self.out_var.get()).resolve()

            project_dir = mod_builder.build_project(
                root=outdir,
                profession=profession,
                char_name=char_name,
                char_code=char_code,
                langs=langs,
            )

            self._append_log(f"[OK] {char_name} 创建完成")
            self._append_log(f"  项目目录: {project_dir}")
            self._append_log(f"  Lua 文件: {project_dir / (char_code + '.lua')}")
            self._append_log(f"  语言: {', '.join(langs)}")
            self.status_var.set(f"最近成功: {char_name} ({profession.key})")
            messagebox.showinfo("完成", f"创建成功:\n{project_dir}")
        except Exception as exc:  # noqa: BLE001
            self._append_log(f"[ERROR] {exc}")
            self.status_var.set("生成失败，请检查参数")
            messagebox.showerror("失败", str(exc))

def main() -> int:
    app = App()
    app.mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
