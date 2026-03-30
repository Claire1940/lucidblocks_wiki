# 翻译系统改进方案

## 📋 现状总结

### 当前文件结构
```
tools/articles/modules/transpage/
├── translate-messages-enhanced.py  (416行) - 主入口 ✅ 保留
├── translator.py                   (15K)   - API调用 ✅ 保留（依赖）
├── smart_chunk_translator.py       (12K)   - 分块逻辑 ✅ 保留（依赖）
├── json_extractor.py               (5.6K)  - 值提取 ❓ 可选（当前未使用）
├── checkpoint_manager.py           (新增)  - 断点续传 ✅ 已创建
└── enhanced_validator.py           (新增)  - 增强验证 ✅ 已创建
```

### 需要删除的重复脚本
```
tools/
├── simple_translate.py             ❌ 删除（临时脚本）
├── quick_translate.py              ❌ 删除（功能重复）
├── translate_missing.py            ❌ 删除（功能重复）
├── translate_modules.py            ❌ 删除（功能重复）
└── translate_modules_lang.py       ❌ 删除（功能重复）

tools/articles/modules/transpage/
└── translate-messages.py           ❌ 删除（旧版本）
```

---

## 🎯 改进方案

### 方案 A：最小改动（推荐）⭐

**只修改 `smart_chunk_translator.py`，集成新功能**

#### 步骤 1：在文件开头添加导入

```python
# 在 smart_chunk_translator.py 第 20 行后添加
import os
import sys

# 导入新模块
try:
    from checkpoint_manager import CheckpointManager
    from enhanced_validator import EnhancedTranslationValidator
except ImportError:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    from checkpoint_manager import CheckpointManager
    from enhanced_validator import EnhancedTranslationValidator
```

#### 步骤 2：修改 SmartChunkTranslator.__init__

在第 149 行的 `__init__` 方法中添加：

```python
def __init__(self, translator, config: dict):
    self.translator = translator
    self.config = config
    self.protected_terms = ProtectedTermsManager(config)
    self.validator = TranslationValidator()

    # 新增：增强验证器和断点管理器
    self.enhanced_validator = EnhancedTranslationValidator()
    self.checkpoint_manager = CheckpointManager()
    self.protected_terms_list = self.protected_terms.protected_terms

    # 分块配置
    self.chunk_strategies = [...]
```

#### 步骤 3：修改 translate_chunk 方法（添加进度保存）

在第 175-249 行的 `translate_chunk` 方法中，成功后立即保存：

```python
async def translate_chunk(
    self,
    chunk_name: str,
    chunk_data: dict,
    target_lang: str,
    session: aiohttp.ClientSession
) -> ChunkResult:
    """翻译单个分块"""
    try:
        # ... 原有的翻译逻辑 ...

        # 验证结构
        valid, error = self.validator.validate_structure(chunk_data, translated_data)
        if not valid:
            return ChunkResult(...)

        # 新增：立即保存分块结果
        self.checkpoint_manager.save_chunk(target_lang, chunk_name, translated_data)

        return ChunkResult(
            success=True,
            chunk_name=chunk_name,
            content=translated_data,
            tokens_estimate=tokens_estimate
        )
    except Exception as e:
        return ChunkResult(...)
```

#### 步骤 4：修改 translate_with_strategy 方法（添加断点恢复）

在第 251-303 行的 `translate_with_strategy` 方法开头添加：

```python
async def translate_with_strategy(
    self,
    data: dict,
    target_lang: str,
    strategy: str,
    chunk_size: Optional[int],
    session: aiohttp.ClientSession
) -> Tuple[bool, Optional[dict], List[ChunkResult]]:
    """使用指定策略翻译（支持断点恢复）"""
    print(f"\n  [策略] {strategy} (chunk_size={chunk_size})")

    # 分块
    if strategy == 'top_level':
        chunks = self.split_by_top_level(data)
    else:
        chunks = self.split_by_size(data, chunk_size)

    print(f"  [分块] 共 {len(chunks)} 个分块")

    # 新增：检查断点
    checkpoint = self.checkpoint_manager.load_checkpoint(target_lang)
    completed_chunks = []

    if checkpoint and checkpoint['strategy'] == strategy:
        completed_chunks = checkpoint['completed_chunks']
        print(f"  [恢复] 已完成 {len(completed_chunks)} 个分块，继续翻译剩余部分")

        # 从已保存的分块中加载数据
        for chunk_name in completed_chunks:
            if chunk_name in chunks:
                del chunks[chunk_name]  # 跳过已完成的分块

    # 翻译剩余分块
    tasks = [
        self.translate_chunk(name, chunk, target_lang, session)
        for name, chunk in chunks.items()
    ]

    results = await asyncio.gather(*tasks)

    # 新增：更新检查点
    newly_completed = [r.chunk_name for r in results if r.success]
    all_completed = completed_chunks + newly_completed

    self.checkpoint_manager.save_checkpoint(
        lang=target_lang,
        strategy=strategy,
        completed_chunks=all_completed,
        total_chunks=len(self.split_by_top_level(data) if strategy == 'top_level' else self.split_by_size(data, chunk_size))
    )

    # 检查结果
    failed_chunks = [r for r in results if not r.success]

    if failed_chunks:
        print(f"  [失败] {len(failed_chunks)}/{len(results)} 个分块失败")
        for result in failed_chunks:
            print(f"    - {result.chunk_name}: {result.error}")
        return False, None, results

    # 合并结果（包括从检查点恢复的）
    merged_data = self.checkpoint_manager.merge_chunks(
        target_lang,
        all_completed
    )

    # ... 原有的验证逻辑 ...
```

#### 步骤 5：在 translate_with_fallback 方法末尾添加清理

在第 342 行后添加：

```python
async def translate_with_fallback(...):
    # ... 原有逻辑 ...

    if success:
        report['final_status'] = 'success'

        # 新增：成功后清理检查点
        self.checkpoint_manager.clear_checkpoint(target_lang)

        # 新增：执行增强验证
        validation_results = self.enhanced_validator.validate_all(
            original=data,
            translated=translated_data,
            protected_terms=self.protected_terms_list
        )

        report['validation'] = validation_results

        if not validation_results['passed']:
            print(f"  [警告] 翻译质量检查发现问题:")
            for check_name, check_result in validation_results['checks'].items():
                if not check_result['passed']:
                    print(f"    - {check_name}: {check_result}")

        return True, translated_data, report
```

---

### 方案 B：完全重写（不推荐）

创建全新的 `translate-messages-v2.py`，从零开始设计。

**缺点**：
- 工作量大
- 需要大量测试
- 可能引入新 bug

---

## 🧪 测试新功能

### 测试断点续传

```bash
# 1. 开始翻译（模拟中途失败）
cd tools/articles/modules/transpage
python translate-messages-enhanced.py --lang pt --overwrite

# 假设翻译到第 5 个分块时失败

# 2. 检查检查点
ls -lh temp/checkpoints/
cat temp/checkpoints/pt_checkpoint.json

# 3. 检查已保存的分块
ls -lh temp/chunks/
# 应该看到 pt_seo.json, pt_nav.json 等

# 4. 重新运行（应该从断点恢复）
python translate-messages-enhanced.py --lang pt --overwrite
# 输出应该显示：[恢复] 已完成 5 个分块，继续翻译剩余部分
```

### 测试增强验证

```python
# 在 Python 中测试
cd tools/articles/modules/transpage
python enhanced_validator.py

# 应该看到测试输出，包括：
# - 正常翻译通过
# - FAQ 问答互换检测
# - 空值检测
# - 专有名词检测
```

---

## 📊 改进效果对比

| 功能 | 改进前 | 改进后 |
|------|--------|--------|
| 断点续传 | ❌ 无 | ✅ 有（保存每个分块） |
| 进度保存 | ❌ 无 | ✅ 有（checkpoint.json） |
| 空值检查 | ❌ 无 | ✅ 有 |
| FAQ 结构检查 | ❌ 无 | ✅ 有（问答互换检测） |
| 专有名词检查 | ⚠️ 基础 | ✅ 增强（统计出现次数） |
| 失败恢复 | ❌ 从头开始 | ✅ 从断点继续 |

---

## 🚀 实施步骤

### 第一阶段：清理重复脚本（立即执行）

```bash
cd D:/web/0306WWE2K26

# 删除重复脚本
rm tools/simple_translate.py
rm tools/quick_translate.py
rm tools/translate_missing.py
rm tools/translate_modules.py
rm tools/translate_modules_lang.py
rm tools/articles/modules/transpage/translate-messages.py

# 提交
git add -A
git commit -m "chore: remove duplicate translation scripts"
```

### 第二阶段：集成新功能（按需执行）

1. **测试新模块**
```bash
cd tools/articles/modules/transpage
python checkpoint_manager.py  # 测试断点管理器
python enhanced_validator.py  # 测试增强验证器
```

2. **修改 smart_chunk_translator.py**
   - 按照上面的步骤 1-5 修改
   - 每修改一步就测试一次

3. **完整测试**
```bash
# 测试翻译（小文件）
python translate-messages-enhanced.py --lang pt --strategy tiny --overwrite

# 检查结果
python -m json.tool ../../src/locales/pt.json > /dev/null && echo "✓ JSON valid"

# 检查检查点
cat temp/checkpoints/pt_checkpoint.json
```

### 第三阶段：文档更新

更新 `使用说明.md` 和 `快速参考.md`，添加新功能说明。

---

## ⚠️ 注意事项

1. **备份重要**
   - 修改前先备份 `smart_chunk_translator.py`
   - 测试时使用小文件

2. **渐进式改进**
   - 不要一次性修改所有代码
   - 每个功能单独测试

3. **保持兼容性**
   - 新功能应该是可选的
   - 不影响现有的翻译流程

4. **错误处理**
   - 如果新模块导入失败，应该降级到旧逻辑
   - 不能因为新功能导致整个系统崩溃

---

## 💡 使用建议

**推荐工作流程**：

```bash
# 1. 清理重复脚本（立即执行）
git rm tools/simple_translate.py tools/quick_translate.py ...

# 2. 测试新模块（确保可用）
python tools/articles/modules/transpage/checkpoint_manager.py
python tools/articles/modules/transpage/enhanced_validator.py

# 3. 小范围测试集成（可选）
# 只修改 translate_chunk 方法，添加分块保存
# 测试是否正常工作

# 4. 逐步扩展（可选）
# 添加断点恢复
# 添加增强验证

# 5. 生产使用
python translate-messages-enhanced.py --lang pt --overwrite --report
```

---

## 📞 问题排查

### Q: 导入新模块失败
```python
ImportError: No module named 'checkpoint_manager'
```

**解决**：
```python
# 在 smart_chunk_translator.py 中添加
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
```

### Q: 检查点文件损坏
```bash
# 手动清理
rm -rf temp/checkpoints/*
rm -rf temp/chunks/*
```

### Q: 翻译卡住不动
```bash
# 检查是否在等待 API 响应
# 查看最新的检查点
cat temp/checkpoints/pt_checkpoint.json

# 如果确认卡住，强制清理后重试
rm temp/checkpoints/pt_checkpoint.json
python translate-messages-enhanced.py --lang pt --overwrite
```

---

## 🎓 总结

**核心改进**：
1. ✅ 断点续传 - 失败后可恢复
2. ✅ 进度保存 - 每个分块立即保存
3. ✅ 增强验证 - 空值、FAQ、专有名词检查

**实施建议**：
- 先清理重复脚本（必做）
- 测试新模块（必做）
- 集成新功能（可选，按需）

**风险控制**：
- 备份原文件
- 渐进式修改
- 充分测试
