#!/usr/bin/env python3
"""
Fix truncated JSON files by completing missing parts
"""
import json
import sys

# Translation mapping for missing parts
translations = {
    "pt": {
        "step2Title": "Conecte-se com Jogadores",
        "step2Description": "Junte-se a servidores Discord ativos e encontre companheiros de equipe",
        "step3Title": "Acesse Ferramentas",
        "step3Description": "Use calculadoras, guias e recursos criados pela comunidade"
    },
    "es": {
        "step2Title": "Conéctate con Jugadores",
        "step2Description": "Únete a servidores de Discord activos y encuentra compañeros de equipo",
        "step3Title": "Accede a Herramientas",
        "step3Description": "Usa calculadoras, guías y recursos creados por la comunidad"
    },
    "vi": {
        "step2Title": "Kết nối với Người chơi",
        "step2Description": "Tham gia các máy chủ Discord hoạt động và tìm đồng đội",
        "step3Title": "Truy cập Công cụ",
        "step3Description": "Sử dụng máy tính, hướng dẫn và tài nguyên do cộng đồng tạo ra"
    },
    "th": {
        "step2Title": "เชื่อมต่อกับผู้เล่น",
        "step2Description": "เข้าร่วมเซิร์ฟเวอร์ Discord ที่ใช้งานอยู่และค้นหาเพื่อนร่วมทีม",
        "step3Title": "เข้าถึงเครื่องมือ",
        "step3Description": "ใช้เครื่องคิดเลข คู่มือ และทรัพยากรที่สร้างโดยชุมชน"
    },
    "ru": {
        "step2Title": "Общайтесь с игроками",
        "step2Description": "Присоединяйтесь к активным серверам Discord и находите товарищей по команде",
        "step3Title": "Доступ к инструментам",
        "step3Description": "Используйте калькуляторы, руководства и ресурсы, созданные сообществом"
    }
}

def fix_json_file(lang):
    """Fix a single JSON file"""
    file_path = f'src/locales/{lang}.json'

    try:
        # Try to load the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to parse as JSON
        try:
            data = json.loads(content)
            print(f"✅ {lang}.json is already valid")
            return True
        except json.JSONDecodeError as e:
            print(f"⚠️  {lang}.json has JSON error: {e}")

            # Try to fix by completing the structure
            if lang in translations:
                # Load English as template
                with open('src/locales/en.json', 'r', encoding='utf-8') as f:
                    en_data = json.load(f)

                # Find where the truncation happened
                if '"step2Title":' not in content:
                    # Need to add step2 and step3
                    trans = translations[lang]

                    # Remove incomplete part
                    if content.rstrip().endswith('"step2Title": "'):
                        content = content.rstrip()[:-16]  # Remove '"step2Title": "'
                    elif content.rstrip().endswith('"step2Title":'):
                        content = content.rstrip()[:-14]  # Remove '"step2Title":'

                    # Add complete structure
                    completion = f'''
        "step2Title": "{trans['step2Title']}",
        "step2Description": "{trans['step2Description']}",
        "step3Title": "{trans['step3Title']}",
        "step3Description": "{trans['step3Description']}"
      }},
      "featured": "{en_data['pages']['community']['featured']}",
      "all": "{en_data['pages']['community']['all']}"
    }}
  }}
}}'''

                    # Try to parse again
                    fixed_content = content + completion
                    data = json.loads(fixed_content)

                    # Save fixed version
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

                    print(f"✅ {lang}.json fixed and saved")
                    return True

            return False

    except Exception as e:
        print(f"❌ Error fixing {lang}.json: {e}")
        return False

# Fix all languages
languages = ['pt', 'es', 'vi', 'th', 'ru']
for lang in languages:
    fix_json_file(lang)
