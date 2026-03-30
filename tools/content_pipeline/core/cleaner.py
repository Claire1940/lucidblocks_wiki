"""
Web 内容清理模块

移除导航链接、广告、追踪等噪音内容
"""

import re
from typing import Set


class ContentCleaner:
    """Web 内容清理器 - 移除导航链接、广告、追踪等噪音"""

    # 页脚导航关键词
    FOOTER_NAVIGATION_KEYWORDS: Set[str] = {
        'more from', 'related', 'see also', 'quick links', 'trending',
        'about us', 'contact us', 'privacy policy', 'terms of service',
        'subscribe', 'newsletter', 'follow us', 'social media',
        'copyright', 'all rights reserved', 'sitemap', 'legal',
        'careers', 'press', 'blog', 'help center', 'support',
        'advertise', 'partnerships', 'affiliates'
    }

    # 评论表单关键词
    COMMENT_FORM_KEYWORDS: Set[str] = {
        'leave a comment', 'post a comment', 'add a comment',
        'post as guest', 'sign in to comment', 'join the discussion',
        'your email', 'your name', 'comment below',
        'share your thoughts', 'what do you think'
    }

    # 独立导航词
    STANDALONE_NAVIGATION_WORDS: Set[str] = {
        'explore', 'community', 'menu', 'home', 'sign in',
        'logout', 'register', 'login', 'search', 'browse',
        'categories', 'tags', 'archive', 'recent', 'main page',
        'discuss', 'all pages', 'wiki', 'fandom'
    }

    # 广告/追踪关键词
    AD_TRACKING_KEYWORDS: Set[str] = {
        'ad.gt', 'doubleclick.net', 'googlesyndication', 'googleadservices',
        'adserver', 'advertising', 'sponsored', 'advertisement',
        'pixel', 'tracking', 'analytics', 'tracker',
        'facebook.com/tr', 'twitter.com/i/adsct', 'linkedin.com/px',
        'outbrain', 'taboola', 'disqus', 'livefyre'
    }

    def __init__(self):
        """初始化清理器"""
        # 预编译正则表达式以提高性能
        self._compile_patterns()

    def _compile_patterns(self):
        """预编译正则表达式"""
        # 匹配 Markdown 链接: [text](url)
        self.link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')

        # 匹配空链接: [](url)
        self.empty_link_pattern = re.compile(r'\[\]\([^)]+\)')

        # 匹配面包屑导航: Home > Category > Page
        self.breadcrumb_pattern = re.compile(r'^[\w\s]+(\s*[>›»]\s*[\w\s]+){2,}$', re.MULTILINE)

        # 匹配 URL（用于移除所有 URL）
        self.url_pattern = re.compile(r'https?://[^\s\)]+')

    def clean(self, content: str) -> str:
        """
        主清理方法 - 按顺序执行所有清理步骤

        Args:
            content: 原始内容

        Returns:
            清理后的内容
        """
        if not content:
            return content

        # 1. 移除广告和追踪相关内容
        content = self._remove_ad_tracking(content)

        # 2. 移除重复的导航块（3+ 连续链接）
        content = self._remove_duplicate_navigation(content)

        # 3. 移除面包屑导航
        content = self._remove_breadcrumbs(content)

        # 4. 移除空链接
        content = self._remove_empty_links(content)

        # 5. 移除所有 URL，保留链接文本
        content = self._remove_all_urls(content)

        # 6. 移除页脚导航
        content = self._remove_footer_navigation(content)

        # 7. 移除评论表单
        content = self._remove_comment_forms(content)

        # 8. 移除独立的导航词
        content = self._remove_short_navigation_lines(content)

        # 9. 清理多余的空行
        content = self._clean_whitespace(content)

        return content

    def _remove_ad_tracking(self, content: str) -> str:
        """移除广告和追踪相关内容"""
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            line_lower = line.lower()
            # 检查是否包含广告/追踪关键词
            if not any(keyword in line_lower for keyword in self.AD_TRACKING_KEYWORDS):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _remove_duplicate_navigation(self, content: str) -> str:
        """移除重复的导航块（3+ 连续链接）"""
        lines = content.split('\n')
        cleaned_lines = []
        consecutive_links = 0

        for line in lines:
            # 检查是否是链接行
            if self.link_pattern.search(line.strip()):
                consecutive_links += 1
                # 如果连续链接少于3个，保留
                if consecutive_links < 3:
                    cleaned_lines.append(line)
            else:
                consecutive_links = 0
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _remove_breadcrumbs(self, content: str) -> str:
        """移除面包屑导航"""
        return self.breadcrumb_pattern.sub('', content)

    def _remove_empty_links(self, content: str) -> str:
        """移除空链接 [](url)"""
        return self.empty_link_pattern.sub('', content)

    def _remove_all_urls(self, content: str) -> str:
        """
        移除所有 URL，保留链接文本

        将 [text](url) 转换为 text
        """
        def replace_link(match):
            text = match.group(1)
            return text if text else ''

        # 先处理 Markdown 链接
        content = self.link_pattern.sub(replace_link, content)

        # 再移除剩余的裸 URL
        content = self.url_pattern.sub('', content)

        return content

    def _remove_footer_navigation(self, content: str) -> str:
        """移除页脚导航"""
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            line_lower = line.lower().strip()
            # 检查是否包含页脚导航关键词
            if not any(keyword in line_lower for keyword in self.FOOTER_NAVIGATION_KEYWORDS):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _remove_comment_forms(self, content: str) -> str:
        """移除评论表单"""
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            line_lower = line.lower().strip()
            # 检查是否包含评论表单关键词
            if not any(keyword in line_lower for keyword in self.COMMENT_FORM_KEYWORDS):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _remove_short_navigation_lines(self, content: str) -> str:
        """移除独立的导航词（单行且只有1-5个词）"""
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            # 检查是否是短行（1-5个词）且包含导航词
            words = stripped.split()
            if len(words) <= 5:
                line_lower = stripped.lower()
                # 检查是否包含任何导航词
                if any(nav_word in line_lower for nav_word in self.STANDALONE_NAVIGATION_WORDS):
                    continue  # 跳过包含导航词的短行
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _clean_whitespace(self, content: str) -> str:
        """清理多余的空行（保留最多2个连续空行）"""
        # 将3个或更多连续空行替换为2个
        content = re.sub(r'\n{3,}', '\n\n', content)
        # 移除行尾空格
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
        return content.strip()
