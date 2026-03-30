#!/bin/bash
# 验证多语言 combat 路由是否正常工作

BASE_URL="http://localhost:3000"
LANGUAGES=("es" "pt" "fr" "tr" "th" "ja" "ko" "en")

echo "开始验证多语言 /combat 路由..."
echo "========================================"

SUCCESS_COUNT=0
FAIL_COUNT=0

for lang in "${LANGUAGES[@]}"; do
    if [ "$lang" = "en" ]; then
        URL="$BASE_URL/combat"
    else
        URL="$BASE_URL/$lang/combat"
    fi

    echo -n "测试 $lang: $URL ... "

    # 使用 curl 检查 HTTP 状态码
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL" --max-time 10)

    if [ "$STATUS" = "200" ]; then
        echo "✓ 成功 (HTTP $STATUS)"
        ((SUCCESS_COUNT++))
    else
        echo "✗ 失败 (HTTP $STATUS)"
        ((FAIL_COUNT++))
    fi
done

echo "========================================"
echo "测试结果: $SUCCESS_COUNT 成功, $FAIL_COUNT 失败"

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✓ 所有路由测试通过!"
    exit 0
else
    echo "✗ 有 $FAIL_COUNT 个路由测试失败"
    exit 1
fi
