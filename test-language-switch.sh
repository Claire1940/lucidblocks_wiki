#!/bin/bash

# 语言切换功能测试脚本
# 使用 curl 命令测试各个路由和语言切换

echo "=========================================="
echo "UTD Wiki 语言切换功能测试"
echo "=========================================="
echo ""

# 设置测试 URL（可以修改为你的实际域名）
BASE_URL="${1:-http://localhost:3000}"

echo "测试 URL: $BASE_URL"
echo ""

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_url() {
    local url=$1
    local description=$2
    local expected_redirect=$3

    echo -e "${YELLOW}测试: ${description}${NC}"
    echo "URL: $url"

    # 使用 -I 只获取 header，-L 跟随重定向
    response=$(curl -s -I -L "$url" 2>&1)
    status_code=$(echo "$response" | grep -i "^HTTP" | tail -1 | awk '{print $2}')

    if [ -n "$expected_redirect" ]; then
        redirect_location=$(echo "$response" | grep -i "^location:" | head -1 | awk '{print $2}' | tr -d '\r')
        if [[ "$redirect_location" == *"$expected_redirect"* ]]; then
            echo -e "${GREEN}✓ 通过${NC} - 重定向到: $redirect_location"
        else
            echo -e "${RED}✗ 失败${NC} - 期望重定向到: $expected_redirect, 实际: $redirect_location"
        fi
    else
        if [ "$status_code" = "200" ]; then
            echo -e "${GREEN}✓ 通过${NC} - 状态码: $status_code"
        else
            echo -e "${RED}✗ 失败${NC} - 状态码: $status_code"
        fi
    fi
    echo ""
}

# 测试 1: 根路径重定向
echo "=========================================="
echo "测试 1: 根路径自动重定向"
echo "=========================================="
test_url "$BASE_URL/" "根路径应重定向到 /en 或 /zh" "/en"

# 测试 2: 英文主页
echo "=========================================="
echo "测试 2: 英文主页"
echo "=========================================="
test_url "$BASE_URL/en" "英文主页应返回 200"

# 测试 3: 中文主页
echo "=========================================="
echo "测试 3: 中文主页"
echo "=========================================="
test_url "$BASE_URL/zh" "中文主页应返回 200"

# 测试 4: 英文攻略页
echo "=========================================="
echo "测试 4: 英文攻略列表"
echo "=========================================="
test_url "$BASE_URL/en/guides" "英文攻略列表应返回 200"

# 测试 5: 中文攻略页
echo "=========================================="
echo "测试 5: 中文攻略列表"
echo "=========================================="
test_url "$BASE_URL/zh/guides" "中文攻略列表应返回 200"

# 测试 6: 英文攻略详情页（假设有 beginner 攻略）
echo "=========================================="
echo "测试 6: 英文攻略详情页"
echo "=========================================="
test_url "$BASE_URL/en/guides/beginner" "英文攻略详情页应返回 200"

# 测试 7: 中文攻略详情页
echo "=========================================="
echo "测试 7: 中文攻略详情页"
echo "=========================================="
test_url "$BASE_URL/zh/guides/beginner" "中文攻略详情页应返回 200"

# 测试 8: 检查 SEO 标签（hreflang）
echo "=========================================="
echo "测试 8: 检查 SEO hreflang 标签"
echo "=========================================="
echo -e "${YELLOW}检查英文攻略页的 hreflang 标签${NC}"
hreflang_check=$(curl -s "$BASE_URL/en/guides/beginner" | grep -o '<link[^>]*hrefLang="[^"]*"[^>]*>' | head -3)
if [ -n "$hreflang_check" ]; then
    echo -e "${GREEN}✓ 找到 hreflang 标签:${NC}"
    echo "$hreflang_check"
else
    echo -e "${RED}✗ 未找到 hreflang 标签${NC}"
fi
echo ""

# 测试 9: 检查 canonical URL
echo "=========================================="
echo "测试 9: 检查 canonical URL"
echo "=========================================="
echo -e "${YELLOW}检查英文攻略页的 canonical URL${NC}"
canonical_check=$(curl -s "$BASE_URL/en/guides/beginner" | grep -o 'rel="canonical"[^>]*' | head -1)
if [ -n "$canonical_check" ]; then
    echo -e "${GREEN}✓ 找到 canonical 标签:${NC}"
    echo "$canonical_check"
else
    echo -e "${RED}✗ 未找到 canonical 标签${NC}"
fi
echo ""

echo "=========================================="
echo "测试完成！"
echo "=========================================="
echo ""
echo "如果所有测试都通过，说明语言切换功能正常工作。"
echo ""
echo "手动测试建议："
echo "1. 访问 $BASE_URL/zh/guides/beginner"
echo "2. 点击导航栏的语言切换按钮"
echo "3. 确认 URL 变为 $BASE_URL/en/guides/beginner"
echo "4. 确认页面内容切换为英文"
echo ""
