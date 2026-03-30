"""
API Client Module
Handles asynchronous API calls to GPT-4o with retry logic and error handling.
"""
import asyncio
import aiohttp
import json
from typing import Dict, Optional
import time
import os
from pathlib import Path


class APIClient:
    def __init__(self, config: Dict):
        """
        Initialize the API client.

        Args:
            config: Configuration dictionary with API settings
        """
        self.api_key = config['api_key']
        self.base_url = config['api_base_url']
        self.api_url = f"{self.base_url.rstrip('/')}/chat/completions"
        self.model = config['model']
        self.temperature = config['temperature']
        self.max_tokens = config['max_tokens']
        self.retry_attempts = config.get('retry_attempts', 3)
        self.retry_delay = config.get('retry_delay', 2)
        self.timeout = config.get('timeout', 600)  # 默认600秒（10分钟）

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'start_time': None,
            'end_time': None
        }

    async def generate_article(
        self,
        session: aiohttp.ClientSession,
        prompt: str,
        article_info: Dict
    ) -> Optional[str]:
        """
        Generate a single article via API.

        Args:
            session: aiohttp ClientSession
            prompt: The complete prompt for article generation
            article_info: Dictionary with article metadata (for logging)

        Returns:
            Generated article content or None if failed
        """
        self.stats['total_requests'] += 1

        for attempt in range(self.retry_attempts):
            try:
                async with session.post(
                    url=self.api_url,
                    json={
                        "model": self.model,
                        "max_tokens": self.max_tokens,
                        "temperature": self.temperature,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a professional SEO content writer specializing in gaming articles."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "stream": False,
                        "group": "default"
                    },
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']

                        # Save debug response
                        self._save_debug_response(article_info, result)

                        # Track token usage
                        if 'usage' in result:
                            self.stats['total_tokens'] += result['usage']['total_tokens']

                            # Check if response was truncated
                            finish_reason = result['choices'][0].get('finish_reason', 'unknown')
                            if finish_reason == 'length':
                                print(f"⚠️  Response truncated due to length limit for {article_info.get('keyword', 'Unknown')}")
                                print(f"   Tokens used: {result['usage']['completion_tokens']}/{self.max_tokens}")

                        self.stats['successful_requests'] += 1
                        return content

                    elif response.status == 429:  # Rate limit
                        wait_time = self.retry_delay * (attempt + 1) * 2
                        print(f"⚠️  Rate limited for {article_info['title']}, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue

                    else:
                        error_text = await response.text()
                        print(f"❌ API error {response.status} for {article_info.get('keyword', article_info.get('title', 'Unknown'))}: {error_text}")

                        if attempt < self.retry_attempts - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                        else:
                            self.stats['failed_requests'] += 1
                            return None

            except asyncio.TimeoutError:
                print(f"⏱️  Timeout for {article_info.get('keyword', article_info.get('title', 'Unknown'))} (attempt {attempt + 1}/{self.retry_attempts})")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    self.stats['failed_requests'] += 1
                    return None

            except Exception as e:
                import traceback
                print(f"❌ Exception for {article_info.get('keyword', article_info.get('title', 'Unknown'))}: {str(e)}")
                print(f"   Exception type: {type(e).__name__}")
                print(f"   Full traceback:")
                traceback.print_exc()
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    self.stats['failed_requests'] += 1
                    return None

        self.stats['failed_requests'] += 1
        return None

    def _save_debug_response(self, article_info: Dict, result: Dict):
        """
        Save API response to debug log file.

        Args:
            article_info: Article metadata
            result: API response JSON
        """
        try:
            # Create debug directory if it doesn't exist
            debug_dir = Path("../../logs/debug")
            debug_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename from article info
            keyword = article_info.get('keyword', 'unknown')
            language = article_info.get('language', 'en')
            filename = f"{language}_{keyword.replace(' ', '-')}_response.json"
            filepath = debug_dir / filename

            # Save response
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️  Failed to save debug response: {e}")

    async def generate_articles_batch(
        self,
        prompts: list,
        batch_size: int = 100
    ) -> list:
        """
        Generate multiple articles in batches.

        Args:
            prompts: List of tuples (prompt, article_info)
            batch_size: Number of concurrent requests

        Returns:
            List of tuples (article_info, content or None)
        """
        self.stats['start_time'] = time.time()
        results = []

        async with aiohttp.ClientSession() as session:
            # Process in batches
            for i in range(0, len(prompts), batch_size):
                batch = prompts[i:i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(prompts) + batch_size - 1) // batch_size

                print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} articles)...")

                # Create tasks for this batch
                tasks = [
                    self.generate_article(session, prompt, article_info)
                    for prompt, article_info in batch
                ]

                # Execute batch concurrently
                batch_results = await asyncio.gather(*tasks)

                # Combine with article info
                for (prompt, article_info), content in zip(batch, batch_results):
                    results.append((article_info, content))

                # Progress update
                completed = i + len(batch)
                print(f"✅ Completed {completed}/{len(prompts)} articles")

                # Small delay between batches to avoid overwhelming the API
                if i + batch_size < len(prompts):
                    await asyncio.sleep(1)

        self.stats['end_time'] = time.time()
        return results

    def get_stats(self) -> Dict:
        """
        Get API call statistics.

        Returns:
            Dictionary with statistics
        """
        stats = self.stats.copy()

        if stats['start_time'] and stats['end_time']:
            duration = stats['end_time'] - stats['start_time']
            stats['duration_seconds'] = round(duration, 2)
            stats['requests_per_second'] = round(stats['total_requests'] / duration, 2)
        else:
            stats['duration_seconds'] = 0
            stats['requests_per_second'] = 0

        stats['success_rate'] = (
            round(stats['successful_requests'] / stats['total_requests'] * 100, 2)
            if stats['total_requests'] > 0 else 0
        )

        return stats

    def print_stats(self):
        """Print formatted statistics."""
        stats = self.get_stats()

        print("\n" + "=" * 60)
        print("📊 API CALL STATISTICS")
        print("=" * 60)
        print(f"Total Requests:       {stats['total_requests']}")
        print(f"Successful:           {stats['successful_requests']} ✅")
        print(f"Failed:               {stats['failed_requests']} ❌")
        print(f"Success Rate:         {stats['success_rate']}%")
        print(f"Total Tokens:         {stats['total_tokens']}")
        print(f"Duration:             {stats['duration_seconds']}s")
        print(f"Requests/Second:      {stats['requests_per_second']}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test the API client
    import json

    with open('tools/articles/config.json', 'r') as f:
        config = json.load(f)

    client = APIClient(config)

    # Test single request
    async def test():
        test_prompt = "Write a short test paragraph about Pixel Blade game."
        test_info = {'title': 'Test Article', 'url_path': '/test/'}

        async with aiohttp.ClientSession() as session:
            result = await client.generate_article(session, test_prompt, test_info)

            if result:
                print("✅ Test successful!")
                print(f"Response length: {len(result)} characters")
                print(f"Preview: {result[:200]}...")
            else:
                print("❌ Test failed")

        client.print_stats()

    asyncio.run(test())
