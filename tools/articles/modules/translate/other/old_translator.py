"""
MDX Article Translator Module
Translates English MDX articles to multiple languages in one API call.
"""

import re
import aiohttp
import asyncio
import os
from datetime import datetime
from typing import Dict, Optional, Tuple, List


class MDXTranslator:
    """Translator for MDX articles"""

    def __init__(self, config: dict):
        """
        Initialize translator with API configuration

        Args:
            config: Configuration dictionary containing API settings
        """
        # API credentials from root config
        self.api_key = config['api_key']
        self.api_base_url = config['api_base_url']

        # Translation-specific settings from translation section
        translation_config = config.get('translation', {})
        self.model = translation_config.get('model', config.get('model', 'gpt-4o'))
        self.temperature = translation_config.get('temperature', 0.7)
        self.max_tokens = translation_config.get('max_tokens', 12288)
        self.retry_attempts = translation_config.get('retry_attempts', 3)
        self.retry_delay = translation_config.get('retry_delay', 2)
        self.timeout = translation_config.get('timeout', 600)

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

        # Load translation prompt template
        self.translation_prompt_template = None
        self.load_translation_prompt()

    def load_translation_prompt(self):
        """Load translation prompt template from file"""
        try:
            template_path = 'tools/articles/translation-prompt-template.md'
            with open(template_path, 'r', encoding='utf-8') as f:
                self.translation_prompt_template = f.read()
            print(f"✅ Translation prompt template loaded")
        except Exception as e:
            print(f"❌ Error loading translation prompt template: {str(e)}")
            print(f"   Translation will not work without the template file")
            self.translation_prompt_template = None

    async def translate_to_multiple_languages(
        self,
        mdx_content: str,
        target_langs: List[str],
        session: aiohttp.ClientSession
    ) -> Dict[str, Optional[str]]:
        """
        Translate MDX content to multiple languages in one API call

        Args:
            mdx_content: Original MDX content in English
            target_langs: List of target language codes (e.g., ['es', 'pt', 'ru'])
            session: Aiohttp client session

        Returns:
            Dictionary mapping language codes to translated content
        """
        if not self.translation_prompt_template:
            print("❌ Translation prompt template not loaded")
            return {lang: None for lang in target_langs}

        # Build language list with game names
        language_list_lines = []
        for lang in target_langs:
            lang_name = self.lang_names.get(lang, lang)
            game_name = self.game_names.get(lang, 'Total Chaos')
            language_list_lines.append(
                f"- {lang_name} ({lang.upper()}): Game name = \"{game_name}\""
            )

        language_list = "\n".join(language_list_lines)

        # Build prompt from template
        prompt = self.translation_prompt_template.format(
            language_list=language_list,
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
            "max_tokens": self.max_tokens
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Print request info
        langs_str = ", ".join([lang.upper() for lang in target_langs])
        print(f"  📤 API请求 [多语言翻译: {langs_str}]:")
        print(f"     模型: {self.model}")
        print(f"     API: {self.api_base_url}")
        print(f"     内容长度: {len(mdx_content)} 字符")
        print(f"     目标语言数: {len(target_langs)}")
        print(f"     最大tokens: {self.max_tokens}")
        print(f"     超时时长: {self.timeout}秒")

        # Retry logic
        for attempt in range(self.retry_attempts):
            try:
                async with session.post(
                    url=self.api_base_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data['choices'][0]['message']['content'].strip()
                        print(f"  ✅ API成功 - 状态码: {response.status}")
                        print(f"     返回长度: {len(response_text)} 字符")

                        # Parse multi-language response
                        translations = self.parse_multi_language_response(response_text, target_langs)

                        # Report parsing results
                        success_count = sum(1 for v in translations.values() if v is not None)
                        print(f"  📝 解析结果: {success_count}/{len(target_langs)} 语言成功")

                        return translations
                    else:
                        error_text = await response.text()
                        print(f"  ❌ API错误 (尝试 {attempt + 1}/{self.retry_attempts}):")
                        print(f"     状态码: {response.status}")
                        print(f"     错误信息: {error_text[:200]}")

            except Exception as e:
                print(f"  ❌ API异常 (尝试 {attempt + 1}/{self.retry_attempts}):")
                print(f"     异常类型: {type(e).__name__}")
                print(f"     异常详情: {str(e)}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)

        # Return empty dict if all attempts failed
        return {lang: None for lang in target_langs}

    def parse_multi_language_response(
        self,
        response_text: str,
        target_langs: List[str]
    ) -> Dict[str, Optional[str]]:
        """
        Parse multi-language response from API

        Args:
            response_text: API response text containing multiple language translations
            target_langs: List of expected language codes

        Returns:
            Dictionary mapping language codes to translated content
        """
        results = {}

        for lang in target_langs:
            # Pattern to extract content for this language
            pattern = rf'---\s*LANGUAGE:\s*{lang}\s*---\s*\n(.*?)\n---\s*END\s+LANGUAGE:\s*{lang}\s*---'
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)

            if match:
                translated_content = match.group(1).strip()
                results[lang] = translated_content
                print(f"     ✅ {lang.upper()}: {len(translated_content)} 字符")
            else:
                results[lang] = None
                print(f"     ❌ {lang.upper()}: 未找到翻译内容")

        return results

    async def translate_article(
        self,
        mdx_content: str,
        target_langs: List[str],
        session: aiohttp.ClientSession,
        article_name: str = "unknown"
    ) -> Dict[str, Optional[str]]:
        """
        Translate entire MDX article to multiple languages

        Args:
            mdx_content: Original MDX content in English
            target_langs: List of target language codes
            session: Aiohttp client session
            article_name: Article identifier for logging (optional)

        Returns:
            Dictionary mapping language codes to translated MDX content
        """
        try:
            # Translate to all languages in one API call
            translations = await self.translate_to_multiple_languages(
                mdx_content,
                target_langs,
                session
            )

            return translations

        except Exception as e:
            print(f"❌ Error translating article: {str(e)}")
            return {lang: None for lang in target_langs}
