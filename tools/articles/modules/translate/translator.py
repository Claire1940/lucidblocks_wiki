"""
MDX Article Translator Module (Single Language)
Translates English MDX articles to one language per API call for better performance.
"""

import re
import aiohttp
import asyncio
import os
import json
import traceback
from pathlib import Path
from typing import Optional
from string import Template

class MDXTranslator:
    """Translator for MDX articles - single language per call"""

    def __init__(self, config: dict):
        """
        Initialize translator with API configuration

        Args:
            config: Configuration dictionary containing API settings
        """
        # API credentials
        self.api_key = config['api_key']
        self.api_base_url = config['api_base_url']
        self.api_url = f"{self.api_base_url.rstrip('/')}/chat/completions"
        self.model = config.get('model', 'gemini-2.0-flash')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 6144)
        self.retry_attempts = config.get('retry_attempts', 3)
        self.retry_delay = config.get('retry_delay', 2)
        self.timeout = config.get('timeout', 300)
        self.group = config.get('group', 'default')

        # Game names and language names from config
        self.game_names = config.get('game_names', {})
        self.lang_names = config.get('lang_names', {
            'es': 'Spanish',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'de': 'German',
            'fr': 'French',
            'zh': 'Chinese',
            'ko': 'Korean',
            'vi': 'Vietnamese',
            'th': 'Thai'
        })

        # Load translation prompt templates
        self.translation_prompt_template = None
        self.load_translation_prompt()

    def load_translation_prompt(self):
        """Load translation prompt template from file"""
        try:
            # Prompt is in the same module directory
            module_dir = os.path.dirname(__file__)
            template_path = os.path.join(module_dir, 'prompts', 'translation-prompt.md')

            with open(template_path, 'r', encoding='utf-8') as f:
                self.translation_prompt_template = f.read()
            print(f"[OK] Translation prompt template loaded")
        except Exception as e:
            print(f"[FAIL] Error loading translation prompt template: {str(e)}")
            print(f"   Translation will not work without the template file")
            self.translation_prompt_template = None


    async def translate_to_language(
        self,
        mdx_content: str,
        target_lang: str,
        session: aiohttp.ClientSession,
        article_name: str = "unknown"
    ) -> Optional[str]:
        """
        Translate MDX content to a single target language

        Args:
            mdx_content: Original MDX content in English
            target_lang: Target language code (e.g., 'es', 'pt', 'ru')
            session: Aiohttp client session
            article_name: Article identifier for logging (optional)

        Returns:
            Translated MDX content or None if failed
        """
        if not self.translation_prompt_template:
            print(f"[FAIL] Translation prompt template not loaded")
            return None

        # Get language name and game name
        lang_name = self.lang_names.get(target_lang, target_lang)
        game_name = self.game_names.get(target_lang, 'Total Chaos')

        # Build prompt from template
        template = Template(self.translation_prompt_template)
        prompt = template.substitute(
            language_name=lang_name,
            lang_code=target_lang,
            game_name=game_name,
            content=mdx_content
        )

        # API request payload
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
            "group": self.group
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Print request info
        print(f"  [SEND] API请求 [{target_lang.upper()}] - {article_name}:")
        print(f"     模型: {self.model}")
        print(f"     内容长度: {len(mdx_content)} 字符")
        print(f"     最大tokens: {self.max_tokens}")

        # Retry logic
        for attempt in range(self.retry_attempts):
            try:
                # 设置详细的超时配置，避免连接断开
                timeout = aiohttp.ClientTimeout(
                    total=self.timeout,      # 600秒总超时
                    connect=60,              # 连接建立超时60秒
                    sock_read=300            # Socket读取超时300秒（足够读取长响应）
                )

                async with session.post(
                    url=self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        translated_content = data['choices'][0]['message']['content'].strip()

                        print(f"  [OK] [{target_lang.upper()}] 成功 - {len(translated_content)} 字符")
                        return translated_content
                    else:
                        error_text = await response.text()
                        print(f"  [FAIL] [{target_lang.upper()}] API错误 (尝试 {attempt + 1}/{self.retry_attempts})")
                        print(f"     状态码: {response.status}")
                        print(f"     错误: {error_text[:200]}")

            except asyncio.TimeoutError:
                print(f"  [TIME] [{target_lang.upper()}] 超时 (尝试 {attempt + 1}/{self.retry_attempts})")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue

            except Exception as e:
                print(f"  [FAIL] [{target_lang.upper()}] 异常 (尝试 {attempt + 1}/{self.retry_attempts})")
                print(f"     异常: {type(e).__name__}: {str(e)}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue

        # All attempts failed
        return None

    async def translate_and_save(
        self,
        mdx_content: str,
        target_lang: str,
        output_path: Path,
        session: aiohttp.ClientSession,
        article_name: str = "unknown"
    ) -> tuple[bool, str]:
        """
        Translate MDX content and save immediately to file

        Args:
            mdx_content: Original MDX content in English
            target_lang: Target language code (e.g., 'es', 'pt', 'ru')
            output_path: Path to save translated file
            session: Aiohttp client session
            article_name: Article identifier for logging (optional)

        Returns:
            Tuple of (success: bool, error_message: str)
        """
        if not self.translation_prompt_template:
            error_msg = "Translation prompt template not loaded"
            print(f"[FAIL] {error_msg}")
            return False, error_msg

        # Get language name and game name
        lang_name = self.lang_names.get(target_lang, target_lang)
        game_name = self.game_names.get(target_lang, 'Total Chaos')

        # Build prompt from template
        template = Template(self.translation_prompt_template)
        prompt = template.substitute(
            language_name=lang_name,
            lang_code=target_lang,
            game_name=game_name,
            content=mdx_content
        )

        # API request payload
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
            "group": self.group
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Connection": "keep-alive"
        }

        # Print request info
        print(f"  [SEND] API请求 [{target_lang.upper()}] - {article_name}:")
        print(f"     模型: {self.model}")
        print(f"     内容长度: {len(mdx_content)} 字符")
        print(f"     最大tokens: {self.max_tokens}")

        # Retry logic
        for attempt in range(self.retry_attempts):
            try:
                # 简化超时配置（参考 api_client.py 的成功实现）
                timeout = aiohttp.ClientTimeout(total=self.timeout)

                async with session.post(
                    url=self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=timeout
                ) as response:
                    if response.status == 200:
                        # 直接读取JSON（参考 api_client.py）
                        data = await response.json()

                        # 保存完整响应到文件（用于调试）
                        debug_dir = Path("tools/articles/logs/debug")
                        debug_dir.mkdir(parents=True, exist_ok=True)
                        response_file = debug_dir / f"{target_lang}_{article_name}_response.json"

                        try:
                            with open(response_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            print(f"  [SAVE] [{target_lang.upper()}] 响应已保存: {response_file}")
                        except Exception as save_err:
                            print(f"  [WARN] [{target_lang.upper()}] 保存响应失败: {save_err}")

                        translated_content = data['choices'][0]['message']['content'].strip()

                        # Remove markdown code blocks if present
                        if translated_content.startswith('```'):
                            lines = translated_content.split('\n')
                            if lines[0].startswith('```'):
                                lines = lines[1:]
                            if lines and lines[-1].strip() == '```':
                                lines = lines[:-1]
                            translated_content = '\n'.join(lines).strip()

                        print(f"  [RECV] [{target_lang.upper()}] 响应接收完成 - {len(translated_content)} 字符")

                        # 立即写入文件
                        try:
                            # 确保目录存在
                            output_path.parent.mkdir(parents=True, exist_ok=True)

                            # 写入文件
                            with open(output_path, 'w', encoding='utf-8') as f:
                                f.write(translated_content)

                            print(f"  [OK] [{target_lang.upper()}] 已保存 - {output_path.name} ({len(translated_content)} 字符)")
                            return True, ""

                        except Exception as e:
                            error_msg = f"保存文件失败: {str(e)}"
                            print(f"  [FAIL] [{target_lang.upper()}] {error_msg}")
                            return False, error_msg
                    else:
                        error_text = await response.text()
                        error_msg = f"HTTP {response.status}: {error_text[:500]}"
                        print(f"  [FAIL] [{target_lang.upper()}] API错误 (尝试 {attempt + 1}/{self.retry_attempts})")
                        print(f"     状态码: {response.status}")
                        print(f"     错误: {error_text[:200]}")

                        # 如果是最后一次尝试，返回错误
                        if attempt == self.retry_attempts - 1:
                            return False, error_msg

                        await asyncio.sleep(self.retry_delay)
                        continue

            except asyncio.TimeoutError:
                error_msg = f"请求超时 (超过 {self.timeout}秒)"
                print(f"  [TIME] [{target_lang.upper()}] 超时 (尝试 {attempt + 1}/{self.retry_attempts})")

                if attempt == self.retry_attempts - 1:
                    return False, error_msg

                await asyncio.sleep(self.retry_delay)
                continue

            except Exception as e:
                # 保存完整错误日志到文件
                error_dir = Path("tools/articles/logs/errors")
                error_dir.mkdir(parents=True, exist_ok=True)
                error_file = error_dir / f"{target_lang}_{article_name}_error_{attempt + 1}.log"

                error_msg = f"{type(e).__name__}: {str(e)}"

                try:
                    with open(error_file, 'w', encoding='utf-8') as f:
                        f.write(f"=== Translation Error Log ===\n")
                        f.write(f"Timestamp: {asyncio.get_event_loop().time()}\n")
                        f.write(f"Article: {article_name}\n")
                        f.write(f"Language: {target_lang}\n")
                        f.write(f"Attempt: {attempt + 1}/{self.retry_attempts}\n\n")

                        f.write(f"Error Type: {type(e).__name__}\n")
                        f.write(f"Error Message: {str(e)}\n\n")

                        f.write("Full Traceback:\n")
                        f.write(traceback.format_exc())

                        f.write(f"\n\nRequest Details:\n")
                        f.write(f"API URL: {self.api_base_url}\n")
                        f.write(f"Model: {self.model}\n")
                        f.write(f"Max Tokens: {self.max_tokens}\n")
                        f.write(f"Temperature: {self.temperature}\n")
                        f.write(f"Timeout: {self.timeout}\n")
                        f.write(f"Content Length: {len(mdx_content)} characters\n")
                except Exception as log_err:
                    print(f"  [WARN] Failed to save error log: {log_err}")

                print(f"  [FAIL] [{target_lang.upper()}] 异常 (尝试 {attempt + 1}/{self.retry_attempts})")
                print(f"     异常: {error_msg}")
                print(f"     完整日志: {error_file}")

                if attempt == self.retry_attempts - 1:
                    return False, error_msg

                await asyncio.sleep(self.retry_delay)
                continue

        # All attempts failed
        return False, "所有重试尝试均失败"

