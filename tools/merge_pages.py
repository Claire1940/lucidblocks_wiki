#!/usr/bin/env python3
"""
快速合并 pages 配置到其他语言文件
保留现有翻译，只添加缺失的结构
"""

import json
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
LOCALES_DIR = ROOT_DIR / "src" / "locales"

# 目标语言
TARGET_LANGS = ["pt", "fr", "es", "de", "it", "ja", "ko"]

def deep_merge(base, overlay):
    """深度合并两个字典，overlay 优先"""
    result = base.copy()
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def main():
    # 读取英文 pages 配置
    en_file = LOCALES_DIR / "en.json"
    with open(en_file, 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    en_pages = en_data.get("pages", {})

    if not en_pages:
        print("[FAIL] No pages section found in en.json")
        return

    print(f"[OK] Loaded en.json with {len(en_pages)} page categories")

    # 为每种语言合并
    for lang in TARGET_LANGS:
        lang_file = LOCALES_DIR / f"{lang}.json"

        if not lang_file.exists():
            print(f"[SKIP] {lang}.json not found")
            continue

        # 读取目标语言文件
        with open(lang_file, 'r', encoding='utf-8') as f:
            lang_data = json.load(f)

        # 获取现有的 pages（如果有）
        existing_pages = lang_data.get("pages", {})

        # 深度合并：英文结构 + 现有翻译
        merged_pages = deep_merge(en_pages, existing_pages)

        # 更新 pages 部分
        lang_data["pages"] = merged_pages

        # 保存
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(lang_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Updated {lang}.json - {len(merged_pages)} categories")

    print("\n[DONE] All language files updated with pages structure")

if __name__ == "__main__":
    main()
