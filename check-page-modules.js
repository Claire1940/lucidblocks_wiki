import fs from 'fs';

const pageContent = fs.readFileSync('src/app/[locale]/page.tsx', 'utf8');

// 提取所有 t.modules.xxx.title 的使用
const moduleMatches = pageContent.match(/t\.modules\.(\w+)\.title/g) || [];
const usedModules = [...new Set(moduleMatches.map(m => m.match(/t\.modules\.(\w+)\.title/)[1]))];

console.log('=== page.tsx 中实际渲染的模块 ===');
console.log('渲染模块数:', usedModules.length);
console.log('模块列表:');
usedModules.forEach((mod, i) => {
  console.log(`  ${i + 1}. ${mod}`);
});

// 需求中的 16 个模块
const requiredModules = [
  'demoDownload',
  'beginnerGuide',
  'coopGuide',
  'tasksObjectives',
  'controlsKeybinds',
  'contentSettings',
  'craftingEquipment',
  'lootItems',
  'enemiesHazards',
  'stealthEscape',
  'homeUpgrades',
  'community',
  'modsBepInEx',
  'popularMods',
  'controllerSupport',
  'playerCount'
];

console.log('\n=== 对比需求 ===');
const missing = requiredModules.filter(m => !usedModules.includes(m));
const extra = usedModules.filter(m => !requiredModules.includes(m));

if (missing.length > 0) {
  console.log('❌ 需求中有但页面未渲染的模块:');
  missing.forEach(m => console.log(`  - ${m}`));
} else {
  console.log('✅ 所有需求模块都已在页面中渲染');
}

if (extra.length > 0) {
  console.log('\n⚠️  页面中有但需求未要求的模块:');
  extra.forEach(m => console.log(`  - ${m}`));
}
