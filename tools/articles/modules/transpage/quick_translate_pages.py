import json
import asyncio
import aiohttp
from pathlib import Path

# 读取配置
with open('transpage_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 读取英文 pages
with open('../../../../src/locales/en.json', 'r', encoding='utf-8') as f:
    en_data = json.load(f)
    pages_en = json.dumps(en_data['pages'], ensure_ascii=False, indent=2)

# 需要翻译的语言
lang_map = {
    'de': 'German',
    'es': 'Spanish (Latin America)',
    'ja': 'Japanese',
    'tr': 'Turkish',
    'fr': 'French'
}

async def translate_pages(lang_code, lang_name):
    prompt = f'''Translate the following JSON content to {lang_name}.

IMPORTANT RULES:
1. Keep all JSON keys in English (do NOT translate keys)
2. Only translate the string values
3. Preserve all special terms: Lucid Blocks, Apotheosis, Steam, Steam Deck, Vulkan, Hookshot, Bee Glider, Qualia, Tiamana
4. Return ONLY valid JSON, no explanations

JSON to translate:
{pages_en}'''

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{config['api_base_url']}/chat/completions",
            headers={
                'Authorization': f"Bearer {config['api_key']}",
                'Content-Type': 'application/json'
            },
            json={
                'model': config['model'],
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.1
            },
            timeout=aiohttp.ClientTimeout(total=300)
        ) as resp:
            result = await resp.json()
            content = result['choices'][0]['message']['content']

            # 提取 JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()

            return json.loads(content)

async def main():
    for lang_code, lang_name in lang_map.items():
        print(f'翻译 {lang_code} ({lang_name})...')
        try:
            pages_translated = await translate_pages(lang_code, lang_name)

            # 读取现有文件
            locale_file = f'../../../../src/locales/{lang_code}.json'
            with open(locale_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 添加 pages
            data['pages'] = pages_translated

            # 保存
            with open(locale_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f'[OK] {lang_code} 完成')
        except Exception as e:
            print(f'[FAIL] {lang_code} 失败: {e}')

if __name__ == '__main__':
    asyncio.run(main())
    print('\n所有翻译完成！')
