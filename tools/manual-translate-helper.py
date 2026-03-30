#!/usr/bin/env python3
"""
手动翻译辅助工具
将 en.json 分块，方便使用 ChatGPT/Claude 等工具翻译
"""

import json
import sys
from pathlib import Path

def split_json_for_manual_translation(input_file, output_dir, chunk_size=100):
    """
    将 JSON 文件分块，每块包含指定数量的键值对

    Args:
        input_file: 输入的 en.json 文件路径
        output_dir: 输出目录
        chunk_size: 每块的行数
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 分块策略：按顶级键分组
    chunks = []

    # SEO 部分（保持不变）
    if 'seo' in data:
        chunks.append(('00_seo', data['seo']))

    # Common 和 Hero
    if 'common' in data and 'hero' in data:
        chunks.append(('01_common_hero', {
            'common': data['common'],
            'hero': data['hero']
        }))

    # Modules - 分成多个小块
    if 'modules' in data:
        modules = data['modules']
        module_keys = list(modules.keys())

        # 每 3 个 module 一组
        for i in range(0, len(module_keys), 3):
            chunk_keys = module_keys[i:i+3]
            chunk_name = f'02_modules_{i//3+1}_{"-".join(chunk_keys[:2])}'
            chunk_data = {k: modules[k] for k in chunk_keys}
            chunks.append((chunk_name, {'modules': chunk_data}))

    # FAQ 和 CTA
    if 'faq' in data and 'cta' in data:
        chunks.append(('03_faq_cta', {
            'faq': data['faq'],
            'cta': data['cta']
        }))

    # Footer
    if 'footer' in data:
        chunks.append(('04_footer', {'footer': data['footer']}))

    # 保存分块
    for chunk_name, chunk_data in chunks:
        output_file = output_path / f'{chunk_name}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)

        # 计算行数
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())

        print(f'[OK] Created: {output_file.name} ({lines} lines)')

    print(f'\n[OK] Created {len(chunks)} chunk files')
    print(f'Output directory: {output_path.absolute()}')
    print('\nHow to use:')
    print('1. Copy each JSON file to ChatGPT/Claude/DeepL')
    print('2. Ask to translate to target language (keep JSON format)')
    print('3. Save translated result as corresponding file')
    print('4. Use merge command to combine all translated chunks')

def merge_translated_chunks(chunks_dir, output_file, lang):
    """
    合并翻译后的分块文件

    Args:
        chunks_dir: 分块文件目录
        output_file: 输出文件路径
        lang: 语言代码
    """
    chunks_path = Path(chunks_dir)
    chunk_files = sorted(chunks_path.glob('*.json'))

    if not chunk_files:
        print(f'Error: No JSON files found in {chunks_dir}')
        return

    merged_data = {}

    for chunk_file in chunk_files:
        print(f'Merging: {chunk_file.name}')
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk_data = json.load(f)

        # 合并数据
        for key, value in chunk_data.items():
            if key == 'modules' and key in merged_data:
                # 合并 modules
                merged_data[key].update(value)
            else:
                merged_data[key] = value

    # 保存合并结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    print(f'\n[OK] Merged to: {output_file}')

    # Validate JSON format
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            json.load(f)
        print('[OK] JSON format validation passed')
    except json.JSONDecodeError as e:
        print(f'[ERROR] JSON format error: {e}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:')
        print('  Split: python3 manual-translate-helper.py split <input.json> <output_dir>')
        print('  Merge: python3 manual-translate-helper.py merge <chunks_dir> <output.json> <lang>')
        print()
        print('Examples:')
        print('  python3 manual-translate-helper.py split src/locales/en.json temp/chunks')
        print('  python3 manual-translate-helper.py merge temp/chunks/vi src/locales/vi.json vi')
        sys.exit(1)

    command = sys.argv[1]

    if command == 'split':
        if len(sys.argv) < 4:
            print('Error: Need to specify input file and output directory')
            sys.exit(1)
        split_json_for_manual_translation(sys.argv[2], sys.argv[3])

    elif command == 'merge':
        if len(sys.argv) < 5:
            print('Error: Need to specify chunks directory, output file and language code')
            sys.exit(1)
        merge_translated_chunks(sys.argv[2], sys.argv[3], sys.argv[4])

    else:
        print(f'Error: Unknown command "{command}"')
        sys.exit(1)
