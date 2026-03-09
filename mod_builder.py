#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Darktide 语音 MOD 项目构建器

功能：
1) 基于 职业/*.lua 模板生成角色专属 lua（支持 ja/chs/en 组合）
2) 自动创建项目目录结构（audio/cartoon_preview/wwise）
3) 自动创建常用受击音效子目录
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


LANG_LABEL = {
    "ja": "日语",
    "chs": "汉语",
    "en": "英语",
}

LANG_ORDER = ["ja", "chs", "en"]


@dataclass(frozen=True)
class Profession:
    key: str
    name_cn: str
    template_file: str
    loc_root: str
    play_root: str
    preview_root: str


PROFESSIONS = {
    "broker": Profession(
        key="broker",
        name_cn="巢都渣滓",
        template_file="broker.lua",
        loc_root="loc_broker_male_b",
        play_root="play_broker_male_b",
        preview_root="broker",
    ),
    "adamant": Profession(
        key="adamant",
        name_cn="法务官",
        template_file="adamant.lua",
        loc_root="loc_adamant_male_a",
        play_root="play_adamant_male_a",
        preview_root="adamant",
    ),
    "zealot": Profession(
        key="zealot",
        name_cn="狂信徒",
        template_file="zealot.lua",
        loc_root="loc_zealot_female_a",
        play_root="play_zealot_female_a",
        preview_root="zealot",
    ),
    "veteran": Profession(
        key="veteran",
        name_cn="老兵",
        template_file="veteran.lua",
        loc_root="loc_veteran_male_b",
        play_root="play_veteran_male_b",
        preview_root="veteran",
    ),
    "psyker": Profession(
        key="psyker",
        name_cn="灵能者",
        template_file="psyker.lua",
        loc_root="loc_psyker_male_c",
        play_root="play_psyker_male_c",
        preview_root="psyker",
    ),
    "ogryn": Profession(
        key="ogryn",
        name_cn="欧格林",
        template_file="ogryn.lua",
        loc_root="loc_ogryn_a",
        play_root="play_ogryn_a",
        preview_root="ogryn",
    ),
}


class BuilderError(RuntimeError):
    pass


def _validate_code(code: str) -> str:
    normalized = code.strip()
    if not re.fullmatch(r"[A-Za-z0-9_]+", normalized):
        raise BuilderError("角色代号只能包含英文字母、数字、下划线。")
    return normalized


def _validate_languages(langs: Iterable[str]) -> list[str]:
    got = []
    for lang in langs:
        lang = lang.lower().strip()
        if lang not in LANG_LABEL:
            raise BuilderError(f"不支持的语言: {lang}，只支持 ja/chs/en。")
        if lang not in got:
            got.append(lang)
    if not got:
        raise BuilderError("至少需要选择一种语言（ja/chs/en）。")
    return sorted(got, key=LANG_ORDER.index)


def _extract_template_tokens(template_text: str) -> dict[str, str]:
    class_match = re.search(r'E:set_class\("([^"]+)",\s*"([^"]+)_ja"', template_text)
    if not class_match:
        raise BuilderError("模板解析失败：无法定位 E:set_class(..._ja...)。")

    profession_key = class_match.group(1)
    old_code = class_match.group(2)

    loc_var_match = re.search(r"\blocal\s+(loc_[A-Za-z0-9_]+)\s*=\s*\"loc_[^\"]+/[^\"]+/\"", template_text)
    play_var_match = re.search(
        r"\blocal\s+(play_[A-Za-z0-9_]+)\s*=\s*\"wwise/events/player/play_[^\"]+/[^\"]+\"",
        template_text,
    )
    if not loc_var_match or not play_var_match:
        raise BuilderError("模板解析失败：无法定位 loc_/play_ 本地变量。")

    comment_match = re.search(r"^(--\s*【[^】]+】).*$", template_text, re.MULTILINE)
    if not comment_match:
        raise BuilderError("模板解析失败：无法定位文件头注释。")

    return {
        "profession_key": profession_key,
        "old_code": old_code,
        "old_loc_var": loc_var_match.group(1),
        "old_play_var": play_var_match.group(1),
        "comment_prefix": comment_match.group(1),
    }


def _split_template(template_text: str) -> tuple[str, str]:
    marker = "E:set_class("
    idx = template_text.find(marker)
    if idx < 0:
        raise BuilderError("模板解析失败：找不到 E:set_class。")
    return template_text[:idx], template_text[idx:]


def _retitle_set_class(text: str, char_name: str, lang: str) -> str:
    label = LANG_LABEL[lang]

    def repl(m: re.Match[str]) -> str:
        return f'{m.group(1)}{char_name}({label}){m.group(2)}'

    return re.sub(r'(E:set_class\([^,\n]+,\s*"[^"]+",\s*")[^"]*(".*?\))', repl, text, count=1)


def _retitle_subtext_speaker(text: str, char_name: str) -> str:
    # 把 :add_subtext("xxx", {...}) 的说话人统一改为角色名
    return re.sub(r'(:add_subtext\(\s*")[^"]*(")', rf"\1{char_name}\2", text)


def _build_language_section(
    body: str,
    old_code: str,
    new_code: str,
    char_name: str,
    lang: str,
) -> str:
    result = body
    result = result.replace(old_code, new_code)
    result = _retitle_set_class(result, char_name, lang)
    result = _retitle_subtext_speaker(result, char_name)

    if lang == "ja":
        return result
    if lang == "chs":
        result = result.replace(f"{new_code}_ja", f"{new_code}_chs")
        result = result.replace("ja_loc_", "loc_")
        return result
    if lang == "en":
        result = result.replace(f"{new_code}_ja", f"{new_code}_en")
        result = result.replace("ja_loc_", "en_loc_")
        return result

    raise BuilderError(f"未实现的语言转换: {lang}")


def _build_lua_content(template_text: str, char_name: str, char_code: str, langs: list[str]) -> str:
    tokens = _extract_template_tokens(template_text)
    old_code = tokens["old_code"]
    old_loc_var = tokens["old_loc_var"]
    old_play_var = tokens["old_play_var"]
    comment_prefix = tokens["comment_prefix"]

    prefix, body = _split_template(template_text)

    new_loc_var = f"loc_{char_code}"
    new_play_var = f"play_{char_code}"

    prefix = re.sub(rf"\b{re.escape(old_loc_var)}\b", new_loc_var, prefix)
    prefix = re.sub(rf"\b{re.escape(old_play_var)}\b", new_play_var, prefix)
    prefix = prefix.replace(old_code, char_code)
    prefix = re.sub(
        rf"^{re.escape(comment_prefix)}.*$",
        f"{comment_prefix}{char_name}",
        prefix,
        count=1,
        flags=re.MULTILINE,
    )

    sections = []
    for idx, lang in enumerate(langs):
        section = _build_language_section(body, old_code=old_code, new_code=char_code, char_name=char_name, lang=lang)
        if idx > 0:
            section = _split_template(section)[1]
        sections.append(section.strip())

    return (prefix.rstrip() + "\n\n" + "\n\n".join(sections).rstrip() + "\n")


def _mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _create_wwise_subdirs(base: Path, play_root: str) -> None:
    vce = [
        "catapulted",
        "catapulted_land",
        "coughing",
        "hurt_heavy",
        "hurt_light",
        "jump",
        "land_heavy",
        "scream_long",
        "attack_long",
        "attack_short",
        "grunt_short",
        "getting_up",
        "struggle_heavy",
    ]
    for item in vce:
        _mkdir(base / f"{play_root}__vce_{item}")

    for item in ["play_syringe_ability_start", "play_syringe_power_start", "play_syringe_speed_start"]:
        _mkdir(base / item)


def build_project(
    root: Path,
    profession: Profession,
    char_name: str,
    char_code: str,
    langs: list[str],
) -> Path:
    templates_dir = Path("职业")
    template_path = templates_dir / profession.template_file
    if not template_path.exists():
        raise BuilderError(f"模板不存在: {template_path}")

    template_text = template_path.read_text(encoding="utf-8")
    lua_content = _build_lua_content(template_text, char_name=char_name, char_code=char_code, langs=langs)

    project_dir = root / char_name
    _mkdir(project_dir)

    audio_loc = project_dir / "audio" / profession.loc_root / char_code
    audio_play = project_dir / "audio" / "wwise" / "events" / "player" / profession.play_root / char_code
    preview_dir = project_dir / "cartoon_preview" / profession.preview_root / char_code

    _mkdir(audio_loc)
    _mkdir(audio_play)
    _mkdir(preview_dir)
    _create_wwise_subdirs(audio_play, profession.play_root)

    lua_path = project_dir / f"{char_code}.lua"
    lua_path.write_text(lua_content, encoding="utf-8")

    return project_dir


def _cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Darktide 二次元语音 MOD 构建器")
    parser.add_argument(
        "-p",
        "--profession",
        required=True,
        choices=sorted(PROFESSIONS.keys()),
        help="职业代号：broker/adamant/zealot/veteran/psyker/ogryn",
    )
    parser.add_argument("-n", "--name", required=True, help="角色名（用于项目目录名和显示名）")
    parser.add_argument("-c", "--code", required=True, help="角色代号（用于文件名和资源目录）")
    parser.add_argument(
        "-l",
        "--langs",
        nargs="+",
        default=["ja"],
        help="语言组合，支持 ja chs en，例如: -l ja chs en",
    )
    parser.add_argument("-o", "--outdir", default=".", help="输出根目录（默认当前目录）")
    return parser.parse_args()


def main() -> int:
    args = _cli()
    try:
        profession = PROFESSIONS[args.profession]
        char_name = args.name.strip()
        if not char_name:
            raise BuilderError("角色名不能为空。")
        char_code = _validate_code(args.code)
        langs = _validate_languages(args.langs)
        outdir = Path(args.outdir).resolve()
        _mkdir(outdir)

        project_dir = build_project(
            root=outdir,
            profession=profession,
            char_name=char_name,
            char_code=char_code,
            langs=langs,
        )

        print("构建完成")
        print(f"项目目录: {project_dir}")
        print(f"职业: {profession.name_cn} ({profession.key})")
        print(f"角色: {char_name} / {char_code}")
        print(f"语言: {', '.join(langs)}")
        print(f"Lua: {project_dir / f'{char_code}.lua'}")
        print(f"LOC输出目录: {project_dir / 'audio' / profession.loc_root / char_code}")
        print(f"受击音效目录: {project_dir / 'audio' / 'wwise' / 'events' / 'player' / profession.play_root / char_code}")
        print(f"头像目录: {project_dir / 'cartoon_preview' / profession.preview_root / char_code}")
        return 0
    except BuilderError as exc:
        print(f"错误: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
