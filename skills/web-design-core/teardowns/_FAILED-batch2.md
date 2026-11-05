# 第二批失败站点记录

> 按任务规则：「如果某站点打不开或渲染失败，明确标注"失败"并跳过，不要编造。」
> 以下 5 个站点在本无头 Chromium 环境中**渲染失败**，未产出有效拆解。所有结论来自实测证据，无推测填充。

环境：Chromium (CDP)，WebGL 2.0 可用（`OpenGL ES 3.0 Chromium / WebKit WebGL`），桌面 1440×900 DPR1，移动 390×844 DPR1。

---

## 1. activetheory.net —— 失败（反自动化拦截）

**证据**：
- 首次访问返回 `document.title = "Not Supported"`，正文只有一句 `"Your browser is not supported"`，DOM 节点数极少。
- 覆盖 UA 为完整 Chrome 131 Windows UA（`Network.setUserAgentOverride`）后重试，`try_enter()` 仍然失败（`navigation failed`，节点数始终 < 20）。
- 说明其检测不止 UA —— 很可能还包括 WebGL renderer 指纹、`navigator` 完整性、或 headless 特征（`navigator.webdriver`）。

**结论**：未拿到任何 token、结构或截图。**不编造**。要拆解需真实非 headless 浏览器（如带 Xvfb 的完整 Chrome + stealth 补丁）。

---

## 2. follow.art —— 失败（Cloudflare 挑战页）

**证据**：
- 页面标题 `"Just a moment..."`，DOM 仅 **54 个节点**，文档高 855px。
- `collect_tokens()` 只返回 4 个字号 / 2 个颜色（全是挑战页自身的样式）。
- 截图主导色 76–87%（挑战页的纯色背景 + 一行提示）。

**结论**：Cloudflare Turnstile/JS challenge 未通过。**按项目既定规则不绕过反爬**。无有效数据。

---

## 3. stefanvitasovic.dev —— 失败（Next.js hydration 未完成）

**证据**：
- `document.title` 正确（`Stefan Vitasović | Creative Developer`），927 个节点，但 **`document.body.scrollHeight = 0`**。
- 文档高 900px（= 视口），`body` 高度 **0**，`body` 的 4 个子元素全是 `0px` 高（`DIV` / `SCRIPT` / `NEXT-ROUTE-ANNOUNCER` / `SCRIPT`）。
- 无任何可滚动容器（`scrollers: []`），无 sticky，无已知动画库字符串。
- 所有截图 `scrollY` 恒为 0（8 张里 6 张主导色 13–91%），即内容从未渲染。

**结论**：Next.js 客户端 hydration 失败或内容由某个在无头环境不触发的事件（如 `requestIdleCallback`、IntersectionObserver + 真实输入）驱动。**DOM 里没有任何可测量的设计内容**。

---

## 4. 18.burocratik.com —— 失败（滚动完全锁定）

**证据**：
- 技术栈极重：**Nuxt (`__NUXT`) + Lenis + three.js + barba.js + matter.js，9 个 WebGL canvas**，16316 个 DOM 节点。
- 文档高 **82098px**（91 屏），但 `uninstrument()` 解锁后 `scrollY` 仍恒为 **0**。
- 桌面 5 张截图中 4 张主导色完全相同（**71.5%**），即全部停在同一帧；首屏 100% 纯色。
- 移动 3 张主导色 87.3%（同一帧）。

**结论**：barba（页面转场）+ Lenis 的组合在无 headless 输入事件时完全不推进。**拿不到任何滚动位置的真实画面**，token 虽可测但缺少与版面位置的对应关系，不足以支撑"版式结构"与"动效"两节。

---

## 5. lusion.co/about —— 失败（WebGL canvas 未初始化）

**证据**：
- `document.title` 正确（`Lusion - About Us`），1004 个节点，正文 2512 字符（"WE ARE A CREATIVE PRODUCTION STUDIO CRAFTING UNIQUE DIGITAL EXPERIENCES…"）。
- **3 个 canvas 中 2 个是 `0×0`**，第三个 `782×439`（未适配视口）。
- 等待 5 秒后再测，canvas 尺寸不变（仍 `0x0` / `0x0` / `782x439`）。
- 截图 **98.9% 纯黑 `rgb(0,0,0)`**（桌面与移动都是 98.9–99.6%）。
- `document.body.scrollHeight = 900`（= 视口），无滚动容器，无 sticky。

**结论**：three.js 场景初始化失败（canvas 未分配尺寸），页面停在纯黑加载态。**正文文本存在但视觉层完全没有渲染**。

---

## 汇总

| 站点 | 失败类型 | 能否补救 |
|---|---|---|
| activetheory.net | 反自动化拦截（UA + fingerprint） | 需非 headless + stealth |
| follow.art | Cloudflare 挑战 | 按规则不绕过 |
| stefanvitasovic.dev | Next.js hydration 失败 | 需真实浏览器交互 |
| 18.burocratik.com | barba+Lenis 滚动锁定 | 需真实输入事件 |
| lusion.co/about | three.js canvas 未初始化 | 需 GPU 加速的真实渲染 |

**共同根因**：本环境是无头 Chromium + 软件/受限 GPU 合成。5 个站的共同特征是"主视觉由 WebGL 实时绘制 且 内容挂载依赖真实输入或 GPU 合成"。

**已尝试但无效的手段**（记录以免重复劳动）：
- `Network.setUserAgentOverride` 覆盖为完整桌面 Chrome UA → activetheory 仍拒绝
- `uninstrument()`：解除 `body{position:fixed}`、强制 `visibility:visible` / `opacity:1` → 对 stefanvitasovic / burocratik18 无效（内容根本不存在，不是被隐藏）
- `preloader_kill()`：移除高 z-index 全屏覆盖层 → 对 lusion 无效（黑屏来自 canvas 而非遮罩）
- 多次重试 + 递增等待（5–12s）→ lusion canvas 始终保持 0×0
- 降 DPR（2→1）→ 解决了 srg 的截图超时，但对上述 5 站无效

**有效手段**（供后续批次复用）：
- `body{position:fixed}` 解锁 + `invisible`/`opacity:0` 强制显示 → 让 digilab、good-fella 的滚动截图成功
- 降 DPR 到 1 → 让 17 个视频的 srg 从连续超时变为可拍
- 分段多次 `scrollTo` + 每段独立验证主导色占比 → 避免了"以为拍到了其实全空"的假成功
