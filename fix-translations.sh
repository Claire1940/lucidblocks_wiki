#!/bin/bash
# 一键修复翻译问题脚本
# 使用方法: ./fix-translations.sh [语言列表]
# 例如: ./fix-translations.sh pt,fr,th

LANGS=${1:-"pt,fr,th"}  # 默认修复这三个语言

echo "================================"
echo "翻译修复脚本"
echo "================================"
echo "目标语言: $LANGS"
echo ""

# 步骤 1: 备份
echo "[1/5] 备份现有翻译文件..."
for lang in ${LANGS//,/ }; do
  if [ -f "src/locales/$lang.json" ]; then
    cp src/locales/$lang.json src/locales/$lang.json.broken
    echo "  ✓ 已备份: $lang.json"
  fi
done

# 步骤 2: 检查配置
echo ""
echo "[2/5] 检查配置文件..."
python3 << 'EOF'
import json

config_file = 'tools/articles/modules/transpage/transpage_config.json'

with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

changed = False

# 检查 use_value_extraction
if config.get('use_value_extraction', True):
    print('  [WARN] use_value_extraction 为 True，正在修改为 False...')
    config['use_value_extraction'] = False
    changed = True
else:
    print('  ✓ use_value_extraction = False (正确)')

# 检查 temperature
if config.get('temperature', 0.7) > 0.3:
    print(f'  [WARN] temperature 为 {config.get("temperature")}，建议降低到 0.3')
    config['temperature'] = 0.3
    changed = True
else:
    print(f'  ✓ temperature = {config.get("temperature")} (正确)')

# 保存配置
if changed:
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print('  ✓ 配置已更新')
else:
    print('  ✓ 配置正确，无需修改')
EOF

# 步骤 3: 重新翻译
echo ""
echo "[3/5] 重新翻译..."
python3 tools/articles/modules/transpage/translate-messages.py --overwrite --lang $LANGS

# 步骤 4: 验证
echo ""
echo "[4/5] 验证翻译质量..."
ALL_PASS=true
for lang in ${LANGS//,/ }; do
  echo ""
  python3 tools/articles/modules/transpage/translation_validator.py \
    src/locales/en.json \
    src/locales/$lang.json \
    $lang

  if [ $? -ne 0 ]; then
    ALL_PASS=false
  fi
done

# 步骤 5: 总结
echo ""
echo "================================"
echo "[5/5] 修复结果"
echo "================================"

if [ "$ALL_PASS" = true ]; then
  echo "✓ 所有翻译已修复并验证通过！"
  echo ""
  echo "下一步："
  echo "  git add src/locales/*.json"
  echo "  git commit -m 'fix: 修复翻译文件'"
  echo "  git push"
else
  echo "✗ 部分翻译仍有问题"
  echo ""
  echo "建议操作："
  echo "  1. 降低温度参数到 0.1"
  echo "     编辑 tools/articles/modules/transpage/transpage_config.json"
  echo "     将 temperature 改为 0.1"
  echo ""
  echo "  2. 重新运行此脚本"
  echo "     ./fix-translations.sh $LANGS"
  echo ""
  echo "  3. 如果仍失败，查看应急手册："
  echo "     cat 需求/05翻译问题应急手册.md"
fi

echo ""
echo "备份文件位置: src/locales/*.json.broken"
echo "================================"
