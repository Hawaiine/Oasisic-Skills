# digilab.co 深度拆解

> 渲染方式：真实 Chromium 渲染（CDP），1440×900 桌面 + 390×844 移动，deviceScaleFactor 2（移动）。
> 实测时间：2026-11-05。站点栈：Next.js（`/_next/static/chunks/*`）+ GSAP ScrollTrigger + Lenis（页面内联代码含 `ScrollTrigger`、`lenis` 字样）。
>
> **重要渲染说明（诚实标注）**：本站用 `body{position:fixed}` + JS 虚拟滚动劫持页面。原生滚动被完全禁用（`window.scrollY`、`document.documentElement.scrollTop`、`body.scrollTop` 恒为 0，wheel / PageDown / `Input.synthesizeScrollGesture` 全部无效），且非首屏 section 带 `class="invisible"` 等 JS 解除。因此：
> - 首屏截图 = 未干预的真实渲染；
> - 滚动位置截图 = 在 DevTools 中临时解除 `body` 定位锁（`position:static`）与 `invisible` 类后拍摄，**仅解除滚动锁与隐藏态，未改任何 token / 布局 / 动效参数**；解除后 ScrollTrigger 正常随 `scrollY` 推进（已用 `ScrollTrigger.refresh()` 校验，且视口内文本随滚动由 hero → "Capture audio" → "Detect species" → "Get in contact with us" 变化，证明揭示逻辑真实运行）。
> - 视觉描述基于 DOM 几何与 computed style 实测，不是凭像素印象。

## 1. 截图清单

> 说明：本站用 `body{position:fixed}` + JS 虚拟滚动。原生滚动被完全禁用（`window.scrollY`、`documentElement.scrollTop`、`body.scrollTop` 恒为 0；wheel / PageDown / `Input.synthesizeScrollGesture` 全部无效），且首屏外 section 带 `class="invisible"` 等 JS 解除。因此滚动位置截图是在 DevTools 中**临时解除 body 定位锁（`position:static`）与 `invisible` 类**后拍摄的 —— 只动这两个开关，未改任何 token / 布局 / 动效参数。解除后 ScrollTrigger 会随 `scrollY` 正常推进（视口内文本由 hero → "Capture audio" → "Detect species" → "Get in contact with us" 变化，证明揭示逻辑真实运行）。
> 另一限制：主要内容承载在 `position:fixed` 的 100svh 容器内，**整页截图（captureBeyondViewport）除首屏外全是空白切片**，已删除这类无效切片，只用逐屏滚动截图。
> 每张截图都做了"非纯色"校验（主导色占比 < 92%），排除空帧。

桌面 1440×900：

| 文件 | scrollY | 屏内主内容（DOM 实测） |
|---|---|---|
| `digilab-desktop-scroll-1-top.png` | 0 | Hero「AI-powered acoustic insights for wildlife monitoring」+ Korimako 声纹段 |
| `digilab-desktop-scroll-2.png` | 1400 | intro 推进 / 品牌陈述「Digilab is an artificial intelligence company…」 |
| `digilab-desktop-scroll-3.png` | 3200 | intro 结束、过渡到反色段 |
| `digilab-desktop-scroll-4.png` | 6600 | 01 Capture audio |
| `digilab-desktop-scroll-5.png` | 9600 | 02 Detect species |
| `digilab-desktop-scroll-6-bottom.png` | 14367（文档底） | 结尾 CTA「Get in contact with us」 |

移动 390×844（DPR 1，仪表化同上，文档 8437px）：

| 文件 | scrollY |
|---|---|
| `digilab-mobile-scroll-1-top.png` | 0 |
| `digilab-mobile-scroll-2.png` | 1200 |
| `digilab-mobile-scroll-3.png` | 3000 |
| `digilab-mobile-scroll-4.png` | 5600 |
| `digilab-mobile-scroll-5-bottom.png` | 8100（底） |

## 2. Token 实测

### 2.1 字体

- 字体族：`denimInk, "denimInk Fallback", sans-serif, sans-serif`（全站唯一族；`denimInk` 为定制/商用字体，回退为 next/font 自生成的 metrics 调整族）
- 字重：**只用到 400 与 500 两档**。标题、导航、按钮全部 500；正文 400。没有 600/700。
- 字距：随字号线性缩放 —— 实测 `-0.03em`（84.11px → −2.523px；47.5px → −1.425px；11.875px → −0.2375px）。正文 `letter-spacing: normal`。
- 行高：display 级统一 **1.1**（84.11/92.53、34.64/38.10），47.5px → 57px（1.2），正文 15.83/23.75 = **1.5**，微文案 11.875/16.625 = **1.4**。

**字号阶梯（桌面 1440，rem 基准 = 15.8333px）**

| 实测 px | rem | 字重 | 行高 | 用途 |
|---|---|---|---|---|
| 84.1146 | 5.31 | 500 | 92.526 (1.1) | Hero H1 / 结尾 CTA H2 |
| 47.5 | 3.0 | 500 | 57 (1.2) | 品牌陈述 H2 |
| 34.6354 | 2.19 | 500 | 38.099 (1.1) | 章节 H2（01/02/03 步骤） |
| 23.75 | 1.5 | 500 | 26.125 (1.1) | 人物卡姓名（Dr Carol Bedoya 等） |
| 15.8333 | 1.0 | 400/500 | 23.75 (1.5) | 正文 / 列表标签 |
| 11.875 | 0.75 | 400/500 | 16.625 (1.4) | 导航、按钮、图注 |
| 10.8854 | 0.6875 | 500 | 11.974 | 极微文案（sound on / credit） |

阶梯比值：84.11 / 47.5 = 1.77；47.5 / 34.64 = 1.37；34.64 / 23.75 = 1.46；23.75 / 15.83 = 1.5；15.83 / 11.88 = 1.33。**非等比阶梯**，靠近 1.4–1.5 的粗节奏，只在 Hero 处跳到 1.77 制造断层。

**根字号是流式/分段式的**：1440px 宽 → `html{font-size:15.8333px}`；780px 宽（平板段）→ `20.267px`；390px 宽（移动）→ `16.64px`。即不是单一 `vw` 公式，而是分断点切换基准（截图实测值，非推测）。

**移动端（390）**：root `16.64px`；H1 `36.4px`/`40.04`/`-1.092px`（2.19rem）；正文 `12.48px`/`17.472`（1.4）。即移动端 Hero 从桌面的 5.31rem 降到 2.19rem（−59%），正文从 1rem 降到 0.75rem。

### 2.2 色板（computed style 实测 hex + 用途）

| hex | rgb | 用途（按出现频次与元素角色） |
|---|---|---|
| `#160e20` | rgb(22,14,32) | 主文字色。全文 234 处文本色，是唯一正文色。偏紫的近黑，非纯黑 |
| `#f2eee5` | rgb(242,238,229) | 主画布底（body + 主 section）—— 奶油暖白 |
| `#f8f8f0` | rgb(248,248,240) | 次级画布（下半部 section background）—— 比主底更亮的奶油 |
| `#cda6ff` | rgb(205,166,255) | **主强调紫**。33 处使用，全部是组件底色（主按钮、图形块），从不作文字色 |
| `#29a176` | rgb(41,161,118) | 次强调绿。19 处，图形/圆点（`lines-dot-inner`） |
| `#fe4f32` | rgb(254,79,50) | 次强调橙红。17 处，小面积图形/标记 |
| `#b379ff` | rgb(179,121,255) | 紫色深一档。11 处，图形层次用 |
| `#605a67` | rgb(96,90,103) | 次要文字（灰紫）。7 处，caption / 数据来源说明 |
| `#45355b` | rgb(69,53,91) | 播放器/深色组件底 |
| oklab(0.977 …/0.4) | — | 半透明浅色文字（页脚 credit，40% 不透明度） |

配色结构：**1 奶油底 + 1 近黑字 + 4 个高饱和点缀（紫系 2 个、绿、橙红）**。点缀色 100% 用于「填充块/圆点」，0 处用于文字 —— 这是该站色彩不显廉价的关键机制。

### 2.3 间距 / 栅格 / 最大宽度

- 无 `max-width` 容器：实测所有「容器」`max-width: none`，唯一横向约束是 `header-wrapper` 的 `padding-inline: 19.7917px`（= 1.25rem）。内容靠 section 高度与绝对定位构图，不靠纵向栅格。
- Section 内边距（实测）：`pt: 138.542px / pb: 19.79px`（品牌 logo 条）、`pt/pb: 118.75px`（团队）、`pt/pb: 197.917px`（结尾 CTA）。
- Section 高度：`3600px`（hero 区 `h-[200lvh] md:h-[400lvh]`）、`1800px`（`h-[200vh]` dark 段）、**`7200px`**（三步骤 pinned 区）、`586 / 861 / 672`（下半常规段）。整页文档高 **15267px @900 视口 ≈ 17 屏**；移动端 **9330px**。
- 无 CSS Grid 多列布局（`grid-template-columns` 实测只有单列）；两栏/多栏关系由绝对定位 + flex 完成。
- 边框：`1px dashed rgb(203,203,203)`（虚线分隔，3 处）、`1px solid rgb(205,166,255)`（紫色描边，2 处）。

### 2.4 圆角 / 阴影

- **圆角只有 3 档**：`50%`级（`3.35544e+07px`，98 处 —— 圆形），`1.97917px`（= 0.125rem，5 处，小标签），`29.6875px`（= 1.875rem，5 处，胶囊按钮）。
- **全站 0 处 box-shadow**。深度完全由色彩块层叠与图形承担 —— 这是本站"平面感"的来源。

## 3. 版式结构

| # | Section | 高度 | 背景 | 布局模式 |
|---|---|---|---|---|
| 0 | Hero（含 intro 序列） | 3600 | 透明（用 body 底） | H1 三行居中断行（`line-wrapper` 逐行包裹，762px 宽）；`intro-screen` 绝对定位叠在 100svh 固定层上，共 2 屏 intro |
| 1 | Dark 过渡段 | 1800 | 透明 / 深色 | `grid h-[200vh]`，`dark-selection` —— 滚动推进的反色段 |
| 2 | 三步骤流程 | **7200** | `#f2eee5` | 单列纵向，每步一屏，pinned：`01 Capture audio` → `02 Detect species` → `03 Visualise your result`。H2 34.64px，标题在 DOM 里重复一次（`Capture audioCapture audio`）用于逐行揭示 |
| 3 | Partners / logos | 586 | `#f8f8f0` | 单行 logo 条，上下 138/20px 内边距 |
| 4 | Our Team | 861 | `#f8f8f0` | 人物列表，姓名 23.75px w500，上下 118.75px |
| 5 | Contact CTA | 672 | `#f8f8f0` | 居中 H2 84.11px + 胶囊按钮，上下 197.9px |

信息层级：**H1(84) → 陈述(47.5) → 步骤(34.6) → 人名(23.75) → 正文(15.8) → 标签(11.9)**。层级几乎全靠字号 + 留白，字重只有 400/500 两档 —— 这是"不用粗体也能分级"的做法。

留白策略：靠 section 高度（1200–7200px 级）而非 padding 制造呼吸；横向几乎无 padding（0 或 19.79px），文字直接以页面宽度排版，Hero 三行断行宽度锁定 762px（≈ 页面 53%）。

导航：`header{position:fixed; top:0; z-index:100}`，高 0（内容绝对定位），链接 11.875px w500，无底色无描边无 backdrop-filter（`backdrop-filter: none`）。链接项：What We Do / KMGBF / Our Team / Our Projects / Partners / About Us。

## 4. 动效

- **库**：GSAP **ScrollTrigger** + **Lenis**（内联代码字符串命中 `ScrollTrigger`、`lenis`；`window.gsap` 未挂全局，说明按模块打包）。无 Framer Motion / Locomotive / Swiper / three.js。
- **滚动模型**：`body{position:fixed; top:0; left:0; right:0}` + 虚拟滚动 —— 原生滚动被接管，页面位移由 JS 驱动。文档高 15267px 但原生 `scrollY` 恒 0。
- **过渡曲线（transition-timing-function 实测去重）**：
  - `cubic-bezier(0.16, 1.08, 0.38, 0.98)` —— 主曲线，**带过冲**（y1=1.08 > 1），用于 `all` 0.8s / 1s / 2s、颜色 0.4s、`grid-template-rows` 0.5s
  - `cubic-bezier(0.34, 1.02, 0.68, 1)` —— 次曲线，颜色 0.5s
  - `cubic-bezier(0.26, 1.04, 0.54, 1)` —— `transform, translate, scale, rotate` 0.5s
  - `cubic-bezier(0.4, 0, 0.2, 1)` —— 仅 `opacity` 0.3s（唯一标准 Material 曲线，只给淡入）
  - 三条主曲线都带 **1.02–1.08 的过冲**，是本站"弹性但不夸张"的署名手感。
- **时长**：微交互 0.3–0.5s；状态切换 0.8s；背景/图形级 1–2s。
- **滚动叙事**：intro 序列（2 屏）→ 反色过渡（200vh）→ 三步骤 pinned（7200px = 8 屏，每步约 2.7 屏）→ 常规段。`infinite-roll` keyframes 2s linear（logo/图形无限滚动的 marquee）。
- **交互态**：Hover 走颜色过渡（0.4–0.5s，带过冲曲线），不是位移/缩放。
- **媒体**：28 张 `<img>`、1 个 `<video>`、2 个 `<canvas>` —— canvas 用于波形/频谱可视化。

## 5. 它"为什么好"（3 条可迁移原则）

1. **点缀色只做填充，永不做文字**。实测 4 个高饱和色（`#cda6ff` / `#29a176` / `#fe4f32` / `#b379ff`）共 80 处使用，全部落在 `background-color`（填充块、圆点、按钮底），`color`（文字色）使用次数为 **0**；全站文字色只有 `#160e20` 与 `#605a67` 两种。结果是画面可以很"彩色"却不花 —— 迁移规则：**accent 色允许进 fill / border / 图形，禁止进 text；文字色限制在 1 主 1 次**。

2. **字重锁死在 2 档，层级交给字号 + 留白**。全站只出现 400 与 500，H1 与正文的字重相同（500 vs 400），层级完全由 5.31rem → 3rem → 2.19rem → 1.5rem → 1rem → 0.75rem 的 1.37–1.77 倍台阶承担。迁移规则：**先定 6 级字号阶梯（1.33–1.5 比值，Hero 单独放一个 1.7+ 的跳档），再决定是否需要第三个字重 —— 通常不需要**。

3. **全站只用一条带过冲的缓动曲线族**。三条主曲线 `(0.16,1.08,0.38,0.98)` / `(0.34,1.02,0.68,1)` / `(0.26,1.04,0.54,1)` 的 y1 都在 1.02–1.08（轻微过冲），唯独 `opacity` 淡入用无过冲的标准曲线。所有组件共享同一"物理感"，这正是"Awwwards 感"的机械来源，而不是靠某个炫技特效。迁移规则：**定义 1 条主缓动（带 1.02–1.08 过冲）+ 1 条纯淡入缓动，全站禁止出现第三种**。

## 6. 不能照抄的地方

1. **滚动劫持 + fixed body 是可用性负债**。实测在无头 Chromium 中整页锁死：`window.scrollY`/`documentElement.scrollTop`/`body.scrollTop` 恒 0，`wheel`、`PageDown`、`Input.synthesizeScrollGesture` 全部无法推进，必须手动改 `body.style.position='static'` 才能看到第二屏。真实用户里任何 JS 失败、输入法拦截、浏览器手势冲突（尤其 iOS Safari 地址栏收缩、Android 返回手势）都会导致页面无法浏览。
2. **`invisible` 类 + JS 揭示 = 无 JS 时全文不可见**。首屏以外所有 section 初始 `class="invisible"`，解除后才渲染（实测临时解除 20 个节点）。对 SEO 抓取、读者模式、打印、prefers-reduced-motion 用户都是直接失效。
3. **`h-[400lvh]` / 7200px pinned 区 = 内容密度极低**。15267px 文档只有 6 个 section，其中 7200px 只讲 3 句流程；移动端 9330px 到联系方式需滚 10+ 屏。这是"作品集型"预算，产品页/信息页模仿会把跳出率拉高。
4. **导航与正文 11.875px（0.75rem）低于常见基线**，桌面正文 15.83px 尚可，但导航、按钮、图注都压到 11.9px；移动端正文掉到 12.48px。CJK 混排时这个尺寸会明显吃力，不应照抄。
5. **字体 `denimInk` 无 web-safe 等价物**。它的窄字宽 + 低对比是 Hero 三行断行成立的前提，换字体后 5.31rem 的 H1 会溢出或断行崩掉，必须整套重算（本站 Hero 断行宽度锁死 762px = 页面 53%，与字体宽度强耦合）。
6. **全站零阴影 + 全圆形/无圆角二极**：`50%` 与 `0.125rem`/`1.875rem` 三档，中间圆角（4/8/12px）完全缺失。迁移到卡片型产品界面会缺少层级手段，只能靠底色差 —— 在内容密集的后台里会糊。
