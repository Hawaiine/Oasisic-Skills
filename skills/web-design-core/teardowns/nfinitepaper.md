# nfinitepaper.com 深度拆解

> 渲染方式：真实 Chromium 渲染（CDP）。桌面 1440×900，移动 390×844（DPR 2），实测 2026-11-05。
> 站点栈：Next.js（`mainfont_*_module` CSS Modules）+ **Lenis** + **GSAP ScrollTrigger**（页面含两者字样）；内嵌隐藏的 **Tweakpane** 调参面板（`div.tp-dfwv{display:none}`，DOM 存在但 0×0，已从所有 token 统计中剔除 —— 首次采样时它污染出 `Roboto Mono` 与 `rgba(187,188,196,0.1)`，复核后排除）。
> 滚动：原生滚动可用（`scrollY` 实测可推进），用 `position: sticky` 做钉住段。视口高度通过 JS 变量 `--vh` 驱动（实测 1440×900 时 `--vh: 9px` = 视口/100，用于 `calc(var(--vh)*35-12rem)`），**故视口变更后必须 reload，否则 section 高度会失真**（实测未 reload 时文档高 11244px，reload 后 15674px）。

## 1. 截图清单

桌面 1440×900：

| 文件 | scrollY | 屏内主内容 |
|---|---|---|
| `nfinitepaper-desktop-1-top.png` | 0 | Hero（全屏视频背景 + 「100% Curbside Recyclable…」59.37px） |
| `nfinitepaper-desktop-2.png` | 1100 | Introducing… / Barrier Performance |
| `nfinitepaper-desktop-3.png` | 2400 | Technology 段（深底，water-based dispersion coatings） |
| `nfinitepaper-desktop-4.png` | 4200 | Sustainably sourced wood（impact 段） |
| `nfinitepaper-desktop-5.png` | 6000 | A Reduced Manufacturing Carbon footprint |
| `nfinitepaper-desktop-7-bottom.png` | 10200 | A 40% lower carbon footprint / 2 trillion… → News / About / Footer |

移动 390×844（DPR 2）：

| 文件 | scrollY |
|---|---|
| `nfinitepaper-mobile-1-top.png` | 0 |
| `nfinitepaper-mobile-2.png` | 900 |
| `nfinitepaper-mobile-3.png` | 2200 |
| `nfinitepaper-mobile-4.png` | 4200 |
| `nfinitepaper-mobile-5.png` | 7000 |
| `nfinitepaper-mobile-6-bottom.png` | 11000 |

## 2. Token 实测

### 2.1 字体

- 字体族：**只有 1 族** —— `mainFont, "mainFont Fallback", sans-serif`（next/font 自托管定制字体；剔除 Tweakpane 污染后 318 处全部是 mainFont）。无第二字体族、无 mono 字体（数据规格表也用 mainFont）。
- 字重：**全站只有 400**。实测所有 h1/h2/h3/p/li/dt/dd 的 `font-weight` 无一例外为 400。零粗体、零 light。
- 字距：display 级 `-0.02 ~ -0.03em`（237.5px → −4.75px = −0.02em；98.96px → −2.97px = −0.03em；59.37px → −1.78px = −0.03em）；正文 `normal`。
- 行高：display `1.05–1.2`（237.5/249.37 = 1.05；59.37/71.25 = 1.2）；正文 `1.4`（15.83/22.17）；列表项 `1.0`（20.78/20.78 —— 单行规格标签）。

**根字号**：@1440 实测 `15.8332px`；@390 实测 `16.6401px`（移动端略大，不是等比缩小）。即全站尺寸实际上分两套：桌面 15.83 基准，移动 16.64 基准。

**字号阶梯（桌面 1440）**

| 实测 px | 字重 | 行高 | 字距 | 用途 |
|---|---|---|---|---|
| 237.498 | 400 | 249.37 (1.05) | −4.75 (−0.02em) | 巨型单词（"Our" ×2，Technology / Impact 段的分段大字） |
| 98.9573 | 400 | 112.81 (1.14) | −2.969 (−0.03em) | 「Our Barrier Technology」段首大字 |
| 83.1242 | 400 | 83.12 (1.0) | −2.494 | 数据冲击句「A 40% lower carbon footprint / 2 trillion…」 |
| 59.3744 | 400 | 71.25 (1.2) | −1.781 | **H1**「100% Curbside Recyclable, sealable, printable…」（实测主体 59.37px，宽 1166px = 页宽 81%） |
| 35.6246 | 400 | 42.75 (1.2) | −1.069 | 段落引导句 |
| 34.6351 | 400 | 34.64 (1.0) | −1.039 | 新闻标题 |
| 20.781 | 400 | 20.78 / 24.94 | −0.623 | 小标题（Barrier Performance / Sustainably sourced…） |
| 15.8332 | 400 | 22.17 (1.4) | normal | **正文主级**（16px 基准） |
| 13.854 | 400 | 20.78 / 13.85 | normal | 署名 / 日期 |
| 12.8645 | 400 | 19.30 / 12.86 | normal | **导航**、规格标签 |
| 10.8853 | 400 | 10.89 | normal | 最小单位（Moisture 等指标名） |

阶梯比值：237.5/98.96 = 2.4；98.96/83.12 = 1.19；83.12/59.37 = 1.4；59.37/35.62 = 1.67；35.62/34.64 = 1.03（几乎并列）；34.64/20.78 = 1.67；20.78/15.83 = 1.31；15.83/13.85 = 1.14；13.85/12.86 = 1.08；12.86/10.89 = 1.18。
**共 11 级，跨度 21.8 倍，且全部 400 字重** —— 层级完全由字号承担，没有任何字重变化。

**移动端（390）**：root `16.6401px`；display 降为 62.4 / 37.44 / 26.0 / 21.84 / 16.64，行高 1.2–1.4（不再用 1.0–1.05 的紧行距）。文档高 14499px。

### 2.2 色板（computed style，已剔除 Tweakpane）

| hex | rgb | 次数 | 用途 |
|---|---|---|---|
| `#0f131a` | 15,19,26 | fg×93 / bg×3 | **主文字色 + 深底段底色**（近黑偏蓝，非纯黑） |
| `#fffaf6` | 255,250,246 | fg×17 / bg×10 | **主画布底 + 深底上的文字**（暖白，比纯白暖一档） |
| `#e9e2d2` | 233,226,210 | bg×10 | 次级面板底（米卡其）—— 规格卡片、分区块 |
| `#dff2f3` | 223,242,243 | bg×3 | 极淡青（按钮底） |
| `#71cbe1` | 113,203,225 | bg×3 | **主强调青**（仅填充） |
| `#8ab4fc` | 138,180,252 | fg×2 | 蓝色链接/强调文字（极少） |
| `rgba(15,19,26,0.6)` | — | fg×22 | **次要文字**（60% 不透明度黑） |
| `oklab(0.988 …/0.8)` | — | fg×9 | 深底上的 80% 白 |
| `oklab(0.988 …/0.75)` | — | fg×8 | 深底上的 75% 白 |
| `oklab(0.186 …/0.3)` | — | bg×8 | 30% 深色蒙层（视频遮罩） |

配色结构：**暖白底 + 近黑蓝字 + 一个青色强调 + 一组"不透明度阶梯"**。关键手法是 **用 0.6/0.75/0.8/0.3 四档 alpha 代替灰阶色板** —— 全站只有 6 个实心色，其余层次全靠 alpha，深浅两段之间自然过渡。强调青 `#71cbe1` 与蓝 `#8ab4fc` **只出现在填充与极少数链接**，正文永远是 `#0f131a` / 60% 黑。

### 2.3 间距 / 栅格 / 最大宽度

- **无 max-width 容器**（实测 `main > *` 的 max-width 为空）。横向约束是统一的 `margin-px-1` = `11.875px` 侧边距（≈0.75rem），Hero H1 实际左右各 130px（1166px 宽 / 1425 页宽）。
- Section 内边距（@1440 实测）：`py-60 md:pt-48 md:pb-*` → `47.5 / 95`；`p-12` → `11.875`（规格段，几乎全幅）；news `59.37 / 11.87`；about `85.1 / 11.87 / 23.75`。
- Section 高度序列（实测，reload 后）：**900（hero，`h-screen`）→ 831 → 692（specifications）→ 4509（technology，深底）→ 3600（impact）→ 692 → 900（深底 grid，`min-h-screen place-*`）→ 688 → 605 → 1118（news）→ 683（about）→ footer 580**。整页 **15674px @900 视口 ≈ 17.4 屏**（移动 14499px）。
- 栅格：只在局部用 grid（实测列宽 1306px / 306px / 836px / 712px / 44.5px 单列化），主体是 block 单列 + 绝对定位层。
- 边框：`border-black/12 border-t` —— **12% 黑色的 1px 顶边框**做分区，不用灰线。
- 圆角：`3.958px`（=0.25rem）、`1.979px`（=0.125rem）、`6px`、`6px 6px 0 0`、`2px`、`2px 0 0 2px`、`50%`/`100%`。**极小圆角体系**（2–6px），无大圆角卡片。
- 阴影：只有 2 个，且极轻 —— `rgba(0,0,0,0.2) 0 2px 4px`、`rgba(0,0,0,0.1) 0 0 2px`。

## 3. 版式结构

| # | Section | 高 | 布局 / 手法 |
|---|---|---|---|
| 0 | Hero | 900 | **全幅视频背景**（`VIDEO 1425×900`，`muted` + `loop`）+ `picture/img` 覆盖层 + 30% 深色蒙层；H1 59.37px 宽 1166px 居左下方（y=496） |
| 1 | Intro | 831 | 单列文案，35.62px 引导句 + 正文 |
| 2 | Specifications | 692 | `p-12`（11.875px 内边距）几乎全幅的**数据表**：Moisture / Oxygen 等指标 + `<0.3 g/m2/day` 等数值，20.78px 标签 + 10.89px 单位 |
| 3 | Technology | **4509** | 深底 `#0f131a`，内含 **`position:sticky top:0 h-screen`** 钉住层 → 滚动 5 屏讲 1 个技术点；段首 98.96px「Our Barrier Technology」+ 237.5px 巨型词「Our」 |
| 4 | Impact | 3600 | 浅底，59.37 / 83.12px 数据句 + 图片；`-mb-[calc(var(--vh)*35-12rem)]` 负边距叠压下一段 |
| 5 | 40% 数据段 | 692 | 83.12px 单句 + 2 trillion 数字 |
| 6 | Manufacturing | 900 | 深底 `min-h-screen` grid 居中（深色大字） |
| 7–9 | 过渡 / FAQ | 688 / 605 | 12% 黑顶边框分区；FAQ「Here are the essentials about Nfinite」 |
| 10 | News | 1118 | 34.64px 新闻标题列表 |
| 11 | About | 683 | 「Proven Leaders in ALD」等团队信息 |
| — | Footer | 580 | 单列 |

信息层级：**237.5 → 98.96 → 83.12 → 59.37 → 35.62 → 34.64 → 20.78 → 15.83 → 13.85 → 12.86 → 10.89**，11 级全部 400 字重。视觉上靠"数字句"（40% / 2 trillion / <0.3 g/m2/day）承担强调，而不是靠粗体或彩色。

留白策略：hero 与深底段用 `h-screen` 满屏 + 极少文字；规格段反过来用 `p-12` 把内容推到接近边缘（全幅数据表）；两种极端交替形成节奏。

导航：`position: fixed`，高 84px，透明底（`rgba(0,0,0,0)`），链接 12.8645px w400 无大写变换：Specifications / Technology / Impact / News / About / Contact us。

## 4. 动效

- **库**：**Lenis**（平滑滚动）+ **GSAP ScrollTrigger**（两者在页面字符串中命中；`window.gsap` 未挂全局）。
- **滚动模型**：`position: sticky` 钉住（实测 3 个 sticky：`sticky top-0 z-0 h-screen overflow-clip`、`sticky top-0`、一个 603px 的居中块）。**无滚动劫持**，原生 `scrollY` 正常工作。
- **过渡曲线**：**主曲线 `cubic-bezier(0.16, 1.08, 0.38, 0.98)`**（带过冲），时长 **0.4s / 0.5s / 0.7s / 2s** 四档；另有：
  - `0.1s cubic-bezier(0.52, 0, 0.74, 0)` —— 入场/退出类（快进慢出）
  - `0.3s cubic-bezier(0.4, 0, 0.2, 1)` —— 标准 Material 曲线（少量）
  - `0.2s ease-in-out`、`0.2s linear` —— 微反馈
- **keyframes**：仅 `fade-in 0.5s ease-in`。
- **视频/图形**：2 个 `<video>`（`loop` + `muted`，hero 全幅背景），7 个 `<canvas>`，32 张 `<img>`。
- **隐藏的 Tweakpane 面板**：站点内嵌调参 GUI（`tp-dfwv`，`display:none`）—— 说明设计参数是运行时变量，可现场调；这些参数最终写回 CSS 变量。
- 交互态：颜色/背景色过渡 0.4s 走主曲线（按钮实测 `transition: color .4s cubic-bezier(0.16,1.08,0.38,0.98), background-color .4s …`）。

## 5. 它"为什么好"（3 条可迁移原则）

1. **全站只用 1 个字重（400）+ 11 级字号，靠字号和数据承担全部强调**。实测 318 个文本节点 `font-weight` 全为 400，却有 11 级字号（237.5 → 10.89，跨度 21.8 倍）。强调手法是**把数字写成大字**：「A 40% lower carbon footprint」「2 trillion」「Moisture <0.3 g/m2/day」。迁移规则：**如果你在纠结用 600 还是 700，先看看能不能把关键事实写成一个比正文大 5–15 倍的数字/句子**；一个字重 + 足够宽的阶梯，比三档字重更干净。

2. **用 alpha 阶梯（0.6 / 0.75 / 0.8 / 0.3）替代灰阶色板**。实测只有 6 个实心色（`#fffaf6`、`#0f131a`、`#e9e2d2`、`#dff2f3`、`#71cbe1`、`#8ab4fc`），但黑色文字有 `#0f131a` 与 `rgba(15,19,26,0.6)` 两档、白字有 0.75/0.8 两档、深色蒙层是 0.3 alpha。深浅底切换时同一套 alpha 自动成立，不需要为暗色模式重配灰阶。迁移规则：**定义 1 主色 1 背景，次级文字一律用「主色 + 0.6 alpha」，蒙层用「主色 + 0.3」；不要引入 5 档灰。**

3. **规格/参数这类"数据内容"用接近全幅的表格 + 极小圆角（2–6px）+ 极轻阴影**，而不是卡片墙。实测 Specifications 段 `padding: 11.875px`（几乎贴边），标签 20.78px、单位 10.89px，圆角最大 6px，阴影仅 `0 2px 4px rgba(0,0,0,0.2)`。结果是"技术文档的可信感"，而不是"营销页的圆卡感"。迁移规则：**凡是要显得可信的数据区，把圆角压到 ≤6px、去掉卡片阴影、内边距压到 8–16px，让表格线（12% 黑）而不是白面积来分区**。

## 6. 不能照抄的地方

1. **11 级字号跨度 21.8 倍，且中间有 1.03 的并列档（35.62 / 34.64）** —— 这两级几乎相同却承担不同角色（引导句 vs 新闻标题），完全靠上下文区分。产品界面照抄会产生"看起来一样但语义不同"的层级混乱；这是 campaign 站点的特赦，不是系统。
2. **H1 实测 59.37px 却把宽度拉到 1166px（页宽 81%）**，纯靠字体自身的窄比例。换字体后 3 行会变 5 行并挤压 hero 视频构图；本站字体是定制的 `mainFont`，无 web-safe 等价物。
3. **深底段 4509px 只讲 1 个技术点（5 屏 sticky）**，全页 15674px ≈ 17.4 屏。信息密度极低，任何需要被检索/比较的内容（价格、规格对比、FAQ）都不适合这种预算。
4. **`--vh` JS 变量 + `h-screen` 混用导致视口变化即失真**：实测未 reload 时文档高 11244px，reload 后 15674px（差 4430px），`calc(var(--vh)*35-12rem)` 的负边距会连带错位。移动端浏览器地址栏收缩会触发同类问题。要迁移必须换成 `svh/dvh` 或 ResizeObserver 稳定化。
5. **依赖全幅视频背景（1425×900, muted loop）**：无 `poster`、`autoplay=false`（靠 JS 播放）。首屏是 LCP 也是最大带宽项，弱网/省流模式会退化成一个空框；同时 muted loop 视频对 prefers-reduced-motion 用户没有任何替代方案。
6. **内嵌 Tweakpane 面板**（`tp-dfwv`，虽 `display:none`）：说明站点带着开发者调参工具上线。第一版复制它的样式很容易连同这套 DOM/依赖一起搬进来，污染包体；也会给 CSS token 统计带来假数据（我第一次采样就误把 `Roboto Mono` 和 `rgba(187,188,196,0.1)` 当成站点 token）。
