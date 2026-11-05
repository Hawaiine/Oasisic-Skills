# Layout Patterns — 版式模式库

> 来源：`patterns.md` §0.3 + §1 + §2（landingfolio 320 条 + designprompts 21 种 + refero 12 份）

---

## 0. 全局基调

| 来源 | 浅色占比 | 样本量 |
|---|---|---|
| landingfolio | **72.8%** (233/320) | 320 |
| designprompts | **71.4%** (15/21) | 21 |

**结论**：浅色是默认，深色是刻意的设计选择。

---

## 1. Hero 模式（n=120，landingfolio 实测）

| 模式 | 占比 | 结构 | 适用场景 |
|---|---|---|---|
| **Split image right** | **40%** | 左半文字（H1+副标题+CTA），右半产品图，垂直居中 | SaaS、工具产品 |
| **Centered** | **30%** | 单列居中：H1→副标题(max 60ch)→双CTA→产品图/logo条 | 品牌型、开发者工具 |
| **Product screenshot** | **26%** | 文字居上，下方产品截图占 60–75% 视宽，轻微 3D 倾斜 | 产品功能可见即卖点 |
| Split image left | 3% | split 镜像版 | 与相邻 section 交替节奏 |
| Full bleed media | 2% | 全幅视频/大图，文字压在媒体上（需 scrim）| 品牌片、硬件 |

**三者合计 95.8%**，其余不到 5%。

**light/dark 比例**：light 78% / dark 22%（深色 hero 集中在 AI 工具与开发者产品）。

**依据**：
- Split right：[ProIntro](https://www.landingfolio.com/inspiration/post/prointro)、[Bugster](https://www.landingfolio.com/inspiration/post/bugster)
- Centered：[wild](https://www.landingfolio.com/inspiration/post/wild)、[Savvycal](https://www.landingfolio.com/inspiration/post/savvycal)
- Product screenshot：[Lindy](https://www.landingfolio.com/inspiration/post/lindy)、[Atlas](https://www.landingfolio.com/inspiration/post/atlas)

---

## 2. Feature 模式（n=25）

| 模式 | 占比 | 结构 | 适用场景 |
|---|---|---|---|
| **Split image right** | **40%** | 文字+截图/插图交替，每段一特性 | 3–6 个功能逐个讲透 |
| **3-column grid** | **24%** | 3 列等宽卡：图标+标题+2行说明 | 6–9 并列功能，无主次 |
| Split image left | 16% | 与 right 交替，Z 字阅读 | 长页面节奏变化 |
| 2-column grid | 8% | 2 列大卡，容纳更长说明 | 功能少但需展开 |
| Tabs | 8% | 顶部 tab 切换面板 | 同一产品的多个视图 |
| **Bento** | **4%** | 不等格网格（大+小拼合）| 功能多样，一屏全貌 |

⚠️ **3-column grid 注意**：单独用"三列+图标"会有模板味（anti-patterns.md ✗2），必须配真实截图或改 bento。

**依据**：[Juicy](https://www.landingfolio.com/inspiration/post/juicy)、[Polar](https://www.landingfolio.com/inspiration/post/polar)、[Woblo(bento)](https://www.landingfolio.com/inspiration/post/woblo)

---

## 3. Pricing 模式（n=25）

| 模式 | 占比 | 结构 | 适用场景 |
|---|---|---|---|
| **2-tier** | **36%** | 两列，一列标"Recommended"，价格数字最大 | 免费/付费双档，最常见 |
| **Single plan** | **36%** | 单卡居中，一个大价格+功能清单+CTA | 单一订阅制 |
| 3-tier | 20% | 三列，中间列高亮轻微上浮 | 有明确三档分层 |
| Comparison table | 8% | 行=功能，列=档位，✓/✗ | 功能差异复杂 |

**关键约束**：全部 25 条中，**无一条超过 3 档**；价格数字均为该 section 最大字号。

**依据**：[Bugster](https://www.landingfolio.com/inspiration/post/bugster)、[Designup](https://www.landingfolio.com/inspiration/post/designup)、[Clipdrop](https://www.landingfolio.com/inspiration/post/clipdrop)

---

## 4. Header / 导航（n=25）

| 模式 | 占比 | 结构 |
|---|---|---|
| **Logo left, links right** | **72%** | logo 居左，链接靠右，最右 CTA；高 56–72px，滚动后加模糊/描边 |
| Logo left, links center | 20% | logo 左、链接居中、CTA 右 |
| Minimal | 4% | 只有 logo + 一个 CTA |
| Centered logo | 4% | logo 居中，链接分列两侧 |

**72% 是版式库里最一致的一条，默认就用这个。**

**依据**：[Clipdrop](https://www.landingfolio.com/inspiration/post/clipdrop)、[Kinsta](https://www.landingfolio.com/inspiration/post/kinsta)

---

## 5. Footer（n=25）

| 模式 | 占比 | 结构 |
|---|---|---|
| **Multi column** | **76%** | 4–5 列链接矩阵（产品/资源/公司/法务）+左侧 logo；底部版权+社交 |
| Simple | 20% | 单行：logo + 少量链接 + 版权 |
| Big CTA | 4% | 页脚上方先放大 CTA 区块，再落链接 |

**深色 footer 最常见**（multi column 中 dark 占 40%），用深色收尾制造段落结束感。

**依据**：[Atlas](https://www.landingfolio.com/inspiration/post/atlas)、[Hustla](https://www.landingfolio.com/inspiration/post/hustla)

---

## 6. Testimonial（n=25）

| 模式 | 占比 | 适用场景 |
|---|---|---|
| **Single quote** | **40%** | 1–3 条高质量证言 |
| Wall | 24% | 8+ 条，重量 |
| Grid | 16% | 4–6 条，均衡排布 |
| Logos + quote | 12% | 企业客户，logo 比人名有说服力 |
| Carousel | 8% | 证言多但版面有限 |

---

## 7. CTA（n=25）

| 模式 | 占比 | 结构 |
|---|---|---|
| **Centered** | **64%** | 大标题+一行说明+单/双按钮，整体居中于色带 |
| Banner | 16% | 横向窄条，左文右按钮 |
| Split image | 12% | 左文右图 |
| Card | 8% | 卡片内嵌 CTA |

---

## 8. Logo Cloud（n=25）

| 模式 | 占比 | 结构 |
|---|---|---|
| **Row** | **72%** | 单行 5–7 个灰度 logo，等距，配"Trusted by…" |
| Grid | 28% | 2×3 或 3×2 网格 |

**统一特征**：logo 全部去色（灰度或单色 40–60% 不透明），hover 才恢复彩色。

---

## 9. 组件总量参考（landingfolio 38 类全站计数）

```
Feature 1025 > Hero 477 > Footer 402 > Header 390 > Testimonial 307 > CTA 304
> Content 247 > Logo Cloud 185 > Pricing 92 > Demo 63 > Signup 48
> Products 45 > FAQ 43 > Stats 42 > Casestudies 41 ...
```

**Feature 是 Hero 的 2.1 倍**：页面结构上"讲功能"的需求远大于"讲主张"。

---

## 10. 风格流派速查（21 种，designprompts 分类）

| 流派 | 基调 | 识别特征 | Token 特点 |
|---|---|---|---|
| 企业/科技 | Light + Sans | 近白底、单一电蓝/绿强调 | 圆角 4–6px，1px 发丝线 |
| 现代深色 | Dark + Sans | 近黑底 + 单一白/绿信号，细线网格 | 近黑 `#08090a`，等宽读数 |
| 瑞士极简 | Light + Sans | 可见分栏网格、黑线白场 | 圆角 0–2px，零阴影 |
| 编辑/印刷 | Light + Serif | 报纸栏宽 + 暖纸底 + 衬线标题 | 底 `#f5f1e8`，行高 1.4–1.6 |
| 奢华/古典 | Light/Dark + Serif | 暖雪花石底、金箔字 | 字距 +0.02–0.05em |
| 粗野主义 | Light | 厚黑实线边框、硬偏移阴影 | 圆角 0，`box-shadow: 6px 6px 0 #000` |
| 软形态/拟物 | Light | 双层阴影、柔和粉/砂底 | 圆角 16–32px |
| 赛博/终端 | Dark + Mono | 荧光绿、命令沟槽 | 等宽全站，圆角 0 |
| 动感/实验 | Dark | 超大移动大写字母，橙高亮 | 标题 64–120px，负字距 |

**完整 21 种见 `patterns.md` §2.1。**

---

## 快速决策

```
项目是什么类型？
├─ 作品集/Campaign → 允许低信息密度、全幅媒体、负字距（西文）
├─ SaaS/产品页 → Feature(split/3-col) + Hero(split-right/centered/screenshot)
├─ 需要被检索的内容 → 禁止"10屏讲1件事"
└─ CJK → 行高+0.2、字距清零、字号+1px

主色调？（先决定，再选布局）
├─ Light 72.8% → 暖白底 + 单一强调色
└─ Dark 27.2% → 近黑底 + 高对比文字
```

---

## 更新日志

- **2026-11-06**：从 `patterns.md` §0–§2 提取，精简到可快速查阅的格式。
