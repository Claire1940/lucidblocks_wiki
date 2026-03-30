import fs from 'fs';
const en = JSON.parse(fs.readFileSync('src/locales/en.json', 'utf8'));

// 检查 modules 中的 16 个模块
const modules = en.modules || {};
const moduleKeys = Object.keys(modules);

console.log('=== 当前 en.json 中的模块数量 ===');
console.log('模块总数:', moduleKeys.length);
console.log('模块列表:', moduleKeys.join(', '));

// 检查每个模块的字段完整性
console.log('\n=== 模块字段完整性检查 ===');
moduleKeys.forEach(key => {
  const module = modules[key];
  console.log('\n[' + key + ']');
  console.log('  - title:', module.title ? '✅' : '❌');
  console.log('  - subtitle:', module.subtitle ? '✅' : '❌');

  // 检查特定字段
  const fields = Object.keys(module).filter(k => k !== 'title' && k !== 'subtitle');
  console.log('  - 其他字段:', fields.join(', '));
});

// 需求文件中的 16 个模块
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

console.log('\n=== 需求对比 ===');
console.log('需求要求模块数:', requiredModules.length);
console.log('实际实施模块数:', moduleKeys.length);

const missing = requiredModules.filter(m => !moduleKeys.includes(m));
const extra = moduleKeys.filter(m => !requiredModules.includes(m));

if (missing.length > 0) {
  console.log('\n❌ 缺失的模块:', missing.join(', '));
} else {
  console.log('\n✅ 所有需求模块都已实施');
}

if (extra.length > 0) {
  console.log('⚠️  额外的模块:', extra.join(', '));
}
