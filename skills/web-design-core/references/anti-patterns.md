# Anti-Patterns — 已泛滥的套路与禁止项

> 来源：`patterns.md` §4（基于 landingfolio 320 条 + designprompts 21 种 + refero 12 份实测）

**用途**：任何设计任务编码前必须全文阅读，确保不落入这些套路。

---

## 判断标准

套路 = 样本里高频出现 **且** 已被系统文档列为 "Don't" 或明显靠模板复制。

---

## ✗ 1. 紫色渐变 + 模糊光晕的"AI 产品"底图

### 症状

- `linear-gradient` 包含 `#6366f1` / `#8b5cf6` 系紫色
- `backdrop-filter: blur(40-80px)` 大半径模糊
- 几乎成了 AI 工具页的默认底图

### 为何禁止

- Linear 的规程明写：`Do not use decorative gradients on buttons, cards, or text — gradients are reserved for the hero atmospheric floor only`
- 已被滥用到注重品控的团队要专门写规则限制

### 替代方案

- **暖白底 + 单一实色强调色**（如 `#faf9f6` 底 + `#0077fa` 单色 CTA）
- **渐变只留在 hero 底层**，且不触碰控件

### 检查方式

```bash
grep -r "linear-gradient.*#[6-8][0-9a-f]{5}" src/
grep -r "backdrop-filter.*blur" src/
```

**依据**：
- [Linear Token 规范](https://styles.refero.design/style/90ce5883-bb24-4466-93f7-801cd617b0d1)（明令禁止装饰性渐变）
- [inspora: mesh gradients](https://www.inspora.design/posts/mesh-gradients)（标为"实验"）

---

## ✗ 2. 三列特性卡 + 线性图标的标准模板

### 症状

- 3-column grid 布局
- 每卡：通用线性图标（如 Feather Icons 默认集）+ 标题 + 2 行说明
- 白卡 + 圆角 + 阴影

### 为何禁止

- 3-column grid 占 Feature 的 24%（landingfolio 数据），但配上"通用图标"时，就成了**可识别为 AI 生成的模板**
- designprompts 的 21 种风格里，**没有一个**以"三列图标卡"作为识别特征——它们全部靠字体、底色、边框语言区分身份

### 替代方案

- **Bento 布局**（不等格网格，大格 + 小格拼合）
- **Split 交替**（左文右图 / 右文左图 Z 字阅读）
- **让特性靠真实界面截图承载**，不用抽象图标

### 检查方式

```bash
# 查找三列 grid + icon 组合
grep -A5 "grid-cols-3" src/ | grep -i "icon"
```

**依据**：
- [landingfolio feature 数据](https://www.landingfolio.com/components/feature)（3-col 24%，但与图标卡组合即模板味）
- [Woblo bento 替代](https://www.landingfolio.com/inspiration/post/woblo)

---

## ✗ 3. 玻璃拟态（glassmorphism）当主视觉

### 症状

- `backdrop-filter: blur(12-24px)` + 半透明白卡（`rgba(255,255,255,0.1-0.2)`）
- 叠在彩色渐变或图片上
- 大面积使用（非局部点缀）

### 为何禁止

- **性能问题**：blur 层重绘成本高，叠在渐变/图上会掉帧
- **无主流采用**：本批 399 条样本中，只有 2 条明确标 `glass`，且都是"实验"标签
- **没有一条主流 SaaS 把它当主视觉**

### 替代方案

- **只在弹窗/悬浮卡上用一层玻璃**（局部点缀）
- **主体用实色 + 1px 发丝线**（Linear/Intercom 模式）

### 检查方式

```bash
grep -r "backdrop-filter.*blur" src/ | wc -l  # 超过 3 处需警惕
```

**依据**：
- [inspora: glass slider experiment](https://www.inspora.design/posts/glass-slider-experiment)（标为"实验"）
- [inspora: soft glass workspace picker](https://www.inspora.design/posts/soft-glass-workspace-picker)（标为"实验"）

---

## ✗ 4. 纯黑纯白 + 全大写 + 负字距的"作品集腔"

### 症状

- 底色 `#000` / `#fff`（纯黑纯白）
- `text-transform: uppercase`（全大写）
- `letter-spacing: -0.03em` 或更负
- `line-height: 1.0`

### 为何禁止

- **refero 12 份中零份用纯黑白做 SaaS 主色**（全部用暖白 `#faf9f6` 或近黑 `#08090a`）
- **只适合短行标题**，正文用会牺牲可读性
- **中文/日文直接失效**：汉字无大小写、行高 1.0 会粘连

### 替代方案

- **暖白 `#faf9f6` 或近黑 `#08090a`**
- **标题用 1.15–1.25 行高**
- **字距 −0.02em 以内**

### 检查方式

```bash
grep -r "#fff\|#000\|rgb(255,255,255)\|rgb(0,0,0)" src/styles/
grep -r "text-transform.*uppercase" src/
grep -r "letter-spacing.*-0\.[0-9][3-9]" src/  # 负字距 > -0.03em
```

**依据**：
- [Intercom](https://styles.refero.design/style/12255b63-e506-4bc1-a4cd-d05487de32f3)（用 `#faf9f6` 非 `#fff`）
- [Linear](https://styles.refero.design/style/90ce5883-bb24-4466-93f7-801cd617b0d1)（用 `#08090a` 非 `#000`）
- [Monochrome 风格](https://www.designprompts.dev/)（黑白但配 Serif + 编辑栏宽，不是作品集腔）

---

## ✗ 5. "Loading → 淡入 → 滚动揭示"三件套铺满全站

### 症状

- 页面加载时有 preloader / spinner
- 每个元素进场都 `opacity: 0 → 1` + `translateY(20px → 0)`
- 滚动时每屏都有 `IntersectionObserver` 触发动画
- 大量视差（parallax）效果

### 为何禁止

- **首屏 LCP 被 preloader 拖垮**（Core Web Vitals 不达标）
- **用户感知不到层次**：当每一屏都 fade-up 时，就没有重点了
- **detail.design 12 条里 3 条是纯粹的滚动/加载动画**——说明这是设计师展示技巧，不是生产最佳实践

### 替代方案

- **只在 1–2 个关键节点用动效**：hero 进场 + section 切换
- **滚动揭示限制在首屏以下第一屏**
- **用 `will-change` 优化，但不滥用**

### 检查方式

```bash
grep -r "IntersectionObserver\|fadeInUp\|data-aos" src/ | wc -l
grep -r "preloader\|loading.*spinner" src/
```

**依据**：
- [AI Spreadsheet Fill](https://recent.design/i/1pd6afn-ai-spreadsheet-fill-interaction)（微交互示例，不是全站）
- [Smart Corner Morph](https://detail.design/detail/smart-corner-morph-animation)（细节展示，不是主视觉）

---

## 通用检查清单（编码后必查）

在提交前，逐项检查：

- [ ] 无紫蓝渐变 + 模糊光晕（除非 hero 底层且不碰控件）
- [ ] 无三列图标卡标准模板（若用 3-col，必须配真实截图或改 bento）
- [ ] 无大面积玻璃拟态（只在弹窗/悬浮卡局部用）
- [ ] 无纯 `#fff` / `#000`（用暖白 `#faf9f6` / 近黑 `#08090a`）
- [ ] 无全大写 + 负字距 > -0.03em（CJK 项目绝对禁止）
- [ ] 无全站滚动劫持或每屏淡入（限制在关键节点）
- [ ] 已运行 `lint_design.sh` 并修正违规项

**全 ✓ 才算通过。**

---

## 更新日志

- **2026-11-06**：从 `patterns.md` §4 提取，补充检查命令与依据链接。
