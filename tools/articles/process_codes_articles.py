#!/usr/bin/env python3
"""
Process codes文章.md and create individual MDX files
"""

import re
import os

def parse_articles(content):
    """Parse the content and extract individual articles"""
    articles = []

    # Split content by "## title:" markers
    sections = re.split(r'(?=## title:)', content)

    for section in sections:
        if not section.strip() or '## title:' not in section:
            continue

        article = {}
        lines = section.split('\n')
        content_lines = []
        found_content_start = False

        for i, line in enumerate(lines):
            # Parse frontmatter
            if line.strip().startswith('## title:'):
                match = re.search(r'## title:\s*"(.+?)"', line)
                if match:
                    article['title'] = match.group(1)
            elif 'description:' in line:
                match = re.search(r'description:\s*"(.+?)"', line)
                if match:
                    article['description'] = match.group(1)
            elif 'keywords:' in line:
                match = re.search(r'keywords:\s*\\\[(.+?)\\\]', line)
                if match:
                    keywords_str = match.group(1)
                    keywords = [k.strip().strip('"') for k in keywords_str.split(',')]
                    article['keywords'] = keywords
            elif 'canonical:' in line:
                match = re.search(r'canonical:\s*"(.+?)"', line)
                if match:
                    article['canonical'] = match.group(1)
            elif 'date:' in line:
                match = re.search(r'date:\s*"(.+?)"', line)
                if match:
                    article['date'] = match.group(1)

            # Check for content start
            elif not found_content_start:
                # Content starts after metadata and after first non-empty line
                if (line.strip() and
                    not any(x in line for x in ['title:', 'description:', 'keywords:', 'canonical:', 'date:', 'You:', 'ChatGPT:', '---', '已思考', '以 markdown形式输出'])):
                    found_content_start = True
                    content_lines.append(line)
            else:
                # Stop at next article marker or instruction
                if any(x in line for x in ['You:', 'ChatGPT:', '以 markdown形式输出', 'spin a brainrot']) and i > 20:
                    # Check if this is the start of next article instruction
                    if re.match(r'(You:|ChatGPT:|以 markdown形式输出)', line.strip()):
                        break
                    # Check if it's another article title format "spin a brainrot xxx codes"
                    if re.match(r'^spin a brainrot .+ codes \d+', line.strip()):
                        break

                # Add line to content
                if line.strip():
                    content_lines.append(line)

        if 'title' in article and content_lines:
            # Clean up content - remove trailing instruction lines
            cleaned_content = []
            for line in content_lines:
                # Stop at FAQ ending or instruction markers
                if any(marker in line for marker in ['希望这', '祝你', '如果你愿意', '欢迎你随时告诉我']):
                    break
                cleaned_content.append(line)

            article['content'] = '\n'.join(cleaned_content).strip()

            # Only add if content is substantial
            if len(article['content']) > 200:
                articles.append(article)

    return articles

def generate_filename(title):
    """Generate filename from title"""
    # "Spin A Brainrot 10k Likes Codes Guide" -> "spin-a-brainrot-10k-likes-codes"
    filename = title.lower()
    filename = filename.replace(' guide', '')
    filename = filename.replace(' ', '-')
    filename = re.sub(r'[^a-z0-9-]', '', filename)
    return f"{filename}.mdx"

def create_mdx_file(article, output_dir):
    """Create an MDX file from article data"""
    if 'title' not in article or 'content' not in article:
        return None

    filename = generate_filename(article['title'])
    filepath = os.path.join(output_dir, filename)

    # Build frontmatter
    keywords_list = article.get('keywords', [])
    keywords_str = str(keywords_list) if keywords_list else '[]'

    frontmatter = f"""---
title: "{article.get('title', '')}"
description: "{article.get('description', '')}"
keywords: {keywords_str}
canonical: "{article.get('canonical', '')}"
date: "{article.get('date', '2025-11-21')}"
---

"""

    # Combine frontmatter and content
    full_content = frontmatter + article['content']

    return filepath, full_content

def main():
    # Read the source file
    source_file = '/Users/bk_libin/Documents/GameProjects/1121SpinaBrainrot/tools/articles/codes文章.md'
    output_dir = '/Users/bk_libin/Documents/GameProjects/1121SpinaBrainrot/src/content/codes'

    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse articles
    articles = parse_articles(content)

    print(f"Found {len(articles)} articles")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create files
    created_files = []
    for i, article in enumerate(articles):
        result = create_mdx_file(article, output_dir)
        if result:
            filepath, file_content = result
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)
            created_files.append(filepath)
            print(f"{i+1}. Created: {os.path.basename(filepath)} ({len(article['content'])} chars)")

    print(f"\n✅ Successfully created {len(created_files)} MDX files in {output_dir}")

if __name__ == '__main__':
    main()
