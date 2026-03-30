"""
Messages Translator Module
Translates UI messages from en.json to other languages
"""

import json
import aiohttp
import asyncio
import os
from pathlib import Path
from typing import Optional


class MessagesTranslator:
    """Translator for UI messages JSON files"""

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
        self.max_tokens = config.get('max_tokens', 8192)
        self.retry_attempts = config.get('retry_attempts', 5)  # Increase retries
        self.retry_delay = config.get('retry_delay', 3)  # Increase delay
        self.timeout = config.get('timeout', 900)  # Increase timeout for large JSON
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
        self.values_translation_prompt_template = None
        self.load_translation_prompt()

    def load_translation_prompt(self):
        """Load translation prompt templates from files"""
        module_dir = os.path.dirname(__file__)

        # Load full JSON translation prompt
        try:
            template_path = os.path.join(module_dir, 'prompts', 'messages-translation-prompt.md')
            with open(template_path, 'r', encoding='utf-8') as f:
                self.translation_prompt_template = f.read()
            print(f"[OK] Messages translation prompt template loaded")
        except Exception as e:
            print(f"[FAIL] Error loading messages translation prompt: {str(e)}")
            self.translation_prompt_template = None

        # Load values-only translation prompt
        try:
            values_template_path = os.path.join(module_dir, 'prompts', 'values-translation-prompt.md')
            with open(values_template_path, 'r', encoding='utf-8') as f:
                self.values_translation_prompt_template = f.read()
            print(f"[OK] Values translation prompt template loaded")
        except Exception as e:
            print(f"[FAIL] Error loading values translation prompt: {str(e)}")
            self.values_translation_prompt_template = None

    async def translate_to_language(
        self,
        messages_json: str,
        target_lang: str,
        session: aiohttp.ClientSession
    ) -> Optional[str]:
        """
        Translate messages JSON to a single target language

        Args:
            messages_json: Original messages JSON in English
            target_lang: Target language code (e.g., 'es', 'pt', 'ru')
            session: Aiohttp client session

        Returns:
            Translated messages JSON or None if failed
        """
        if not self.translation_prompt_template:
            print(f"[FAIL] Translation prompt template not loaded")
            return None

        # Get language name and game name
        lang_name = self.lang_names.get(target_lang, target_lang)
        game_name = self.game_names.get(target_lang, 'Total Chaos')

        # Build prompt from template
        prompt = self.translation_prompt_template.format(
            language_name=lang_name,
            lang_code=target_lang,
            game_name=game_name,
            content=messages_json
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
        print(f"  [SEND] API请求 [{target_lang.upper()}]:")
        print(f"     模型: {self.model}")
        print(f"     内容长度: {len(messages_json)} 字符")
        print(f"     最大tokens: {self.max_tokens}")

        # Retry logic
        for attempt in range(self.retry_attempts):
            try:
                # More detailed timeout configuration
                timeout = aiohttp.ClientTimeout(
                    total=self.timeout,
                    connect=120,      # Allow more time to connect
                    sock_read=600     # Allow more time to read large responses
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

                        # Remove markdown code blocks if present
                        if translated_content.startswith('```'):
                            lines = translated_content.split('\n')
                            if lines[0].startswith('```'):
                                lines = lines[1:]
                            if lines[-1].strip() == '```':
                                lines = lines[:-1]
                            translated_content = '\n'.join(lines)

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

    async def translate_values_list(
        self,
        values: list,
        target_lang: str,
        session: aiohttp.ClientSession
    ) -> Optional[list]:
        """
        Translate a list of string values (optimized for performance)

        Args:
            values: List of strings to translate
            target_lang: Target language code (e.g., 'es', 'pt', 'ru')
            session: Aiohttp client session

        Returns:
            List of translated strings or None if failed
        """
        if not self.values_translation_prompt_template:
            print(f"[FAIL] Values translation prompt template not loaded")
            return None

        # Convert values list to newline-separated text
        values_text = '\n'.join(values)

        # Get language name and game name
        lang_name = self.lang_names.get(target_lang, target_lang)
        game_name = self.game_names.get(target_lang, 'Slayerbound')

        # Build prompt from template
        prompt = self.values_translation_prompt_template.format(
            language_name=lang_name,
            lang_code=target_lang,
            game_name=game_name,
            line_count=len(values),
            content=values_text
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
        print(f"  [SEND] API请求 [{target_lang.upper()}] (值列表模式):")
        print(f"     模型: {self.model}")
        print(f"     值数量: {len(values)} 个")
        print(f"     内容长度: {len(values_text)} 字符")
        print(f"     最大tokens: {self.max_tokens}")

        # Retry logic
        for attempt in range(self.retry_attempts):
            try:
                timeout = aiohttp.ClientTimeout(
                    total=self.timeout,
                    connect=120,
                    sock_read=600
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

                        # Remove markdown code blocks if present
                        if translated_content.startswith('```'):
                            lines = translated_content.split('\n')
                            if lines[0].startswith('```'):
                                lines = lines[1:]
                            if lines[-1].strip() == '```':
                                lines = lines[:-1]
                            translated_content = '\n'.join(lines)

                        # Split by newlines to get list of translated values
                        translated_lines = translated_content.split('\n')

                        # Validate line count matches
                        if len(translated_lines) != len(values):
                            print(f"  [WARN] [{target_lang.upper()}] 行数不匹配: 期望 {len(values)}, 得到 {len(translated_lines)}")
                            # Try to handle mismatch
                            if len(translated_lines) > len(values):
                                # Truncate extra lines
                                translated_lines = translated_lines[:len(values)]
                                print(f"     已截断到 {len(values)} 行")
                            else:
                                # Pad with original values
                                for i in range(len(translated_lines), len(values)):
                                    translated_lines.append(values[i])
                                print(f"     已用原始值填充到 {len(values)} 行")

                        print(f"  [OK] [{target_lang.upper()}] 成功 - {len(translated_lines)} 个值")
                        return translated_lines
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
        messages_json: str,
        target_lang: str,
        output_path: Path,
        session: aiohttp.ClientSession
    ) -> bool:
        """
        Translate messages JSON and save immediately to file

        Args:
            messages_json: Original messages JSON in English
            target_lang: Target language code (e.g., 'es', 'pt', 'ru')
            output_path: Path to save translated file
            session: Aiohttp client session

        Returns:
            True if translation and save succeeded, False otherwise
        """
        # Translate
        translated_content = await self.translate_to_language(
            messages_json,
            target_lang,
            session
        )

        if not translated_content:
            return False

        # Save to file first (even if JSON is invalid)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Try to validate and pretty print JSON
            try:
                parsed_json = json.loads(translated_content)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(parsed_json, f, indent=2, ensure_ascii=False)
                print(f"  [OK] [{target_lang.upper()}] 已保存 (有效JSON) - {output_path.name}")
                return True
            except json.JSONDecodeError as e:
                # Save raw content even if JSON is invalid
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(translated_content)
                print(f"  [WARN] [{target_lang.upper()}] 已保存 (JSON格式有问题，需手动修复) - {output_path.name}")
                print(f"     JSON错误: {str(e)}")
                return True  # Still return True since we saved the file

        except Exception as e:
            print(f"  [FAIL] [{target_lang.upper()}] 保存文件失败: {str(e)}")
            return False
