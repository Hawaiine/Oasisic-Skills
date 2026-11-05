---
name: web-design-core
description: "任何网页/UI/落地页/样式/配色/排版任务必须先加载。强制 Design Brief + 自检清单。"
version: 1.0.0
author: Noah
platforms: [linux]
metadata:
  hermes:
    category: creative
    tags: [Web, UI, Design, Frontend, Landing Page, Typography, Color]
license: MIT
---

# Web Design Core — 强制设计流程

**触发条件**：任何网页、UI、落地页、组件、样式、配色、排版任务必须先加载此 skill。不要猜测设计规范，全部基于 `references/` 实测数据。

---

## 强制流程（① ② ③，多方案时加 ④）

### ① 加载 references

| 任务类型 | 必读 | 何时 |
|---|---|---|
| 任何设计任务 | `references/anti-patterns.md` | **必读** |
| 落地页/营销页 | `references/layout-patterns.md` | 版式模式库 |
| Token/配色/字体 | `references/tokens-and-type.md` | 字阶/圆角/色板 |
| 动效/交互 | `references/motion.md` | 缓动/时长/滚动 |
| 组件库选型 | `references/component-systems.md` | Semi/Ant/Element/shadcn |
| 真实案例 | `teardowns/*.md` | 7 站实测拆解 |

加载：`skill_view('web-design-core', file_path='references/anti-patterns.md')`（必读）。`teardowns/` 文件用 skill_view 的 `file_path='teardowns/pear.md'` 格式读取。

### ② 编码前：输出 Design Brief（缺失即未完成）

```markdown
## Design Brief — [项目名]

### 1. 风格定位
流派：[企业科技/现代深色/瑞士极简/编辑印刷…]（layout-patterns.md §10）
色调：[light 72.8% / dark 27.2%]
参考站点：[teardowns/ 中的 1-2 个 + 借鉴什么]

### 2. Typography
字体族：[展示 / 正文 / 等宽]
字阶：[Minor Third 1.2 / Major Second 1.125]
基准字号：[桌面 16px / 移动 ≥16px]
行高：[标题 1.15-1.25 / 正文 1.5-1.7 / CJK 1.7-1.8]

### 3. 色板
底色：[暖白 #faf9f6 / 近黑 #08090a，禁纯 #fff/#000]
强调色：[单一饱和色，HSL]
功能色：[success/warning/danger]
Alpha 阶梯：[0.1 / 0.22 / 0.6]

### 4. 栅格与间距
容器最大宽度：[1200px / 1440px]
栅格列数：[12 列 / 自由]
间距基数：[4px / 8px]

### 5. 圆角与阴影
控件圆角：[4-6px]　卡片圆角：[12-16px]
阴影策略：[1px 发丝线 / 仅浮层阴影]

### 6. 动效（如有）
主曲线：[cubic-bezier(0.23,1.04,0.32,1) / ease-out]
时长：[150ms 微交互 / 300-500ms 常规 / 2-3s 氛围]
滚动编排：[sticky / 无劫持；禁 body{position:fixed}]

### 7. 引用依据
- [reference 文件 §章节 → 提取了哪条规则]
```

### ③ 编码后：运行自检（缺失即未完成）

```bash
bash /opt/data/skills/creative/web-design-core/scripts/lint_design.sh <项目目录>
```

**9 项自动检查**：紫蓝渐变、裸 sans-serif、emoji 图标、统一圆角、纯白底、纯黑字、玻璃拟态滥用、滚动劫持、全大写+负字距。

**改脚本后必测三组输入**：干净夹具 → exit 0；违规夹具 → exit 1 且逐条打印「文件:行号」；空目录 → exit 0。只测一组会把「静默跳过」误当成「通过」。脚本内所有 `$(grep … | wc -l)` 计数必须 `|| true` 并以 `${VAR:-0}` 兜底——`set -euo pipefail` 下「零匹配」是正常业务情况却会让脚本中途退出，后续检查全部不执行。

**多档检查要认变量**：圆角/字号这类「是否分两档」的判断必须同时统计字面值（`border-radius: 6px`）和变量定义（`--radius-control: 6px`）——规范本身就推荐用变量，只认字面值会把正确实现读成「无圆角」。加第二个计数器时用精确比较（`-eq 1 && -eq 0`），不要写 `-le 1`：空目录两项计数都是 0，`<=1` 会把它判成违规，这正是空目录夹具守的那条回归。

**lint 报违规 ≠ 必须改**：违规项若是有意的设计决定，在 Design Brief §7 写一句保留理由即可，但 5 条硬禁止不接受例外。

**10 项手动清单**（全 ✓ 才算完成）：
- [ ] 已输出 Design Brief
- [ ] lint 全通过或违规项已在 Brief 中论证
- [ ] 字体指定具体族（非裸 `sans-serif`）
- [ ] 底色用暖白/近黑，非纯 #fff/#000
- [ ] 全站只有一个饱和强调色
- [ ] 圆角分两档（控件 4-6px / 卡片 12-16px）；或属 0–2px 流派（瑞士极简/编辑印刷/brutalist）且在 Brief §5 注明为流派例外
- [ ] 阴影仅用于真浮层，其余 1px 发丝线
- [ ] CJK 正文行高 ≥1.7
- [ ] 字阶用 1.125 或 1.2
- [ ] Brief 中列出了引用的 reference 条目

### ④ 多方案任务：先定差异轴，再写代码

一次交付多个「风格必须明显不同」的页面时，先选 ≥3 条差异轴写进各自 Brief：底色明暗（近黑 / 暖纸 / 暖白）、字体族类别（纯无衬线 / 衬线+无衬线双族 / 等宽点缀）、信息密度（16px 基准大留白 vs 14px 基准紧凑）。只换强调色不算不同风格。交付前用浏览器读 computed style 客观核验，不要靠肉眼：

```js
js("(() => { const b=getComputedStyle(document.body), h=document.querySelector('h1'), s=getComputedStyle(h); return {bg:b.backgroundColor, color:b.color, size:b.fontSize, h1:s.fontSize, h1w:s.fontWeight}; })()")
```

---

## 五条硬禁止（详见 anti-patterns.md）

1. ❌ 紫色渐变 `#6366f1`/`#8b5cf6` + 大半径模糊光晕
2. ❌ 三列图标卡 + 通用线性图标（模板味）
3. ❌ 玻璃拟态当主视觉（`backdrop-filter` 超 3 处）
4. ❌ 纯黑纯白 + 全大写 + 负字距 > -0.03em（CJK 直接失效）
5. ❌ `body{position:fixed}` 滚动劫持 + 每屏淡入

每条都有替代方案，见 `anti-patterns.md`。

---

## 选型速查

**组件库**：React+字节→Semi｜React+国内ToB→Ant｜Vue3→Element Plus｜React+Tailwind→shadcn
**图标**：统一 Lucide（24px、strokeWidth 2px、跨框架）
**详见** `component-systems.md`

---

## 交付标准

必须包含 4 项，缺一即未完成：①Design Brief ②代码 ③自检报告（lint + 清单）④引用溯源。

被要求自评时按「已执行 / 论证偏离 / 忽略」三类逐条写，每条点名具体规则条目；忽略项必须写清原因和影响，不能只报通过项——用户要的是校准，不是成绩单。

---

## 更新日志

- **2026-11-06**：初版，整合 patterns.md + component-systems.md + 7 站拆解。
