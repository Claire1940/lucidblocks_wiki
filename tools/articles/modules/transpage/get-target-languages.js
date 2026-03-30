#!/usr/bin/env node
/**
 * Get Target Languages - 获取目标翻译语言列表
 *
 * 从配置文件读取需要翻译的语言列表
 * 用于自动化翻译流程
 *
 * 使用方法：
 *   node get-target-languages.js
 *   node get-target-languages.js --format comma  # 输出逗号分隔
 *   node get-target-languages.js --format json   # 输出 JSON 数组
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 配置文件路径
const CONFIG_PATH = path.join(__dirname, 'transpage_config.json');

// 备用：扫描 src/locales/ 目录
const LOCALES_DIR = path.join(process.cwd(), 'src/locales');

/**
 * 从配置文件读取语言列表
 */
function getLanguagesFromConfig() {
  try {
    const configContent = fs.readFileSync(CONFIG_PATH, 'utf-8');
    const config = JSON.parse(configContent);

    if (config.languages && Array.isArray(config.languages)) {
      return config.languages;
    }

    return null;
  } catch (error) {
    console.error(`[WARN] 无法读取配置文件: ${error.message}`);
    return null;
  }
}

/**
 * 从 src/locales/ 目录扫描语言文件
 */
function getLanguagesFromDirectory() {
  try {
    if (!fs.existsSync(LOCALES_DIR)) {
      console.error(`[ERROR] 目录不存在: ${LOCALES_DIR}`);
      return [];
    }

    const files = fs.readdirSync(LOCALES_DIR);

    // 提取语言代码（排除 en.json）
    const languages = files
      .filter(file => file.endsWith('.json') && file !== 'en.json')
      .map(file => file.replace('.json', ''));

    return languages;
  } catch (error) {
    console.error(`[ERROR] 扫描目录失败: ${error.message}`);
    return [];
  }
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  const format = args.includes('--format')
    ? args[args.indexOf('--format') + 1]
    : 'comma';

  // 优先从配置文件读取
  let languages = getLanguagesFromConfig();

  // 如果配置文件没有，则扫描目录
  if (!languages || languages.length === 0) {
    console.error('[INFO] 配置文件中未找到语言列表，扫描 src/locales/ 目录...');
    languages = getLanguagesFromDirectory();
  }

  if (!languages || languages.length === 0) {
    console.error('[ERROR] 未找到任何目标语言');
    process.exit(1);
  }

  // 输出结果
  if (format === 'json') {
    console.log(JSON.stringify(languages, null, 2));
  } else if (format === 'comma') {
    console.log(languages.join(','));
  } else if (format === 'space') {
    console.log(languages.join(' '));
  } else {
    // 默认：每行一个
    languages.forEach(lang => console.log(lang));
  }
}

main();
