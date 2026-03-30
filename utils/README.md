# Utils 工具目录

这个目录包含项目的实用工具脚本。

## API 连通性测试

### 文件
- `test_api_connection.py` - Gemini API 连通性测试脚本

### 功能
该脚本用于测试 Gemini API 的连通性和功能,包括:

1. **基础连通性测试** - 验证 API 是否可访问并正常响应
2. **流式响应测试** - 测试 SSE (Server-Sent Events) 流式响应功能
3. **非流式响应测试** - 测试标准的 JSON 响应功能

### 使用方法

#### 1. 安装依赖
```bash
pip install requests
```

或使用 requirements.txt (如果有):
```bash
pip install -r requirements.txt
```

#### 2. 运行测试
```bash
python utils/test_api_connection.py
```

或者直接执行:
```bash
chmod +x utils/test_api_connection.py
./utils/test_api_connection.py
```

### 输出示例

脚本会显示详细的测试过程和结果:

```
============================================================
  Gemini API 连通性测试
============================================================

🔧 配置信息:
   - API 端点: https://svip.theapi.top
   - 模型: gemini-2.5-flash
   - 超时设置: 30秒

============================================================
  测试 1: 基础连通性测试
============================================================

📡 发送请求到: https://svip.theapi.top/v1/chat/completions
🤖 使用模型: gemini-2.5-flash
💬 测试消息: 你好

⏱️  响应时间: 1.23秒
📊 状态码: 200
✅ 连接成功!

🤖 AI 回复:
您好！有什么我可以帮助您的吗？

📈 Token 使用:
   - 提示词: 5
   - 完成: 12
   - 总计: 17

...
```

### 配置说明

脚本中的配置常量:

```python
API_BASE_URL = "https://svip.theapi.top"  # API 端点
API_KEY = "sk-..."                         # API 密钥
MODEL = "gemini-2.5-flash"                 # 使用的模型
TIMEOUT = 30                               # 请求超时时间(秒)
```

### 注意事项

1. **API Key 安全**: 当前 API Key 直接硬编码在脚本中,仅用于测试。生产环境建议使用环境变量:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```

2. **网络连接**: 确保网络可以访问 API 端点

3. **Python 版本**: 需要 Python 3.6+

4. **依赖库**: 仅需要 `requests` 库

### 故障排查

#### 连接超时
- 检查网络连接
- 尝试增加 `TIMEOUT` 值
- 确认 API 端点是否可访问

#### 401 未授权
- 检查 API Key 是否正确
- 确认 API Key 是否有效

#### 429 配额超限
- API Key 的使用配额已用完
- 检查账户余额和计费详情
- 更换新的 API Key 或等待配额重置

#### JSON 解析错误
- 检查 API 响应格式
- 查看原始响应内容

### 使用配置文件

为了方便管理 API Key,可以创建独立的配置文件:

1. 复制示例配置:
   ```bash
   cp utils/api_config.example.py utils/api_config.py
   ```

2. 编辑 `api_config.py` 填入你的 API Key

3. 修改 `test_api_connection.py` 导入配置:
   ```python
   from api_config import API_BASE_URL, API_KEY, MODEL, TIMEOUT
   ```

4. 将 `api_config.py` 添加到 `.gitignore` 避免泄露密钥

### 扩展功能

可以根据需要添加更多测试场景:

```python
# 添加自定义测试
def test_custom_scenario():
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "你的测试消息"}
        ],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 500
    }
    # ... 测试逻辑
```

### 相关资源

- [Gemini API 文档](https://ai.google.dev/docs)
- [OpenAI API 兼容格式](https://platform.openai.com/docs/api-reference)
