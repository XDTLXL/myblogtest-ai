// 从 Playwright JSON 报告提取"基线结论"注解，用于生成测试结论
const fs = require('fs');
// Playwright 的 json reporter 会把报告写到 stdout；这里读取重定向后的文件。
// PowerShell 的 Out-File 会带 BOM，需要先去掉再解析。
const raw = fs.readFileSync('results.json', 'utf8');
const report = JSON.parse(raw.replace(/^\uFEFF/, ''));

const rows = [];
function walk(suites) {
  for (const s of suites || []) {
    for (const spec of s.specs || []) {
      for (const t of spec.tests || []) {
        for (const r of t.results || []) {
          for (const a of r.annotations || []) {
            rows.push({ test: spec.title, type: a.type, desc: a.description });
          }
        }
      }
    }
    walk(s.subsuites || s.suites);
  }
}
walk(report.suites);

console.log('=== 实测结论基线（共 ' + rows.length + ' 条） ===\n');
for (const r of rows) {
  console.log('【' + r.type + '】');
  console.log('  用例: ' + r.test);
  console.log('  结论: ' + r.desc);
  console.log('');
}
console.log('=== 汇总 ===');
console.log('total=' + report.stats.expected + ' failed=' + report.stats.unexpected + ' flaky=' + report.stats.flaky + ' duration=' + Math.round(report.stats.duration / 1000) + 's');
