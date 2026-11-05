# 网页 UI 设计核心 🎨🧪

> **任何网页 / UI / 落地页任务的强制设计流程。**
>
> 不猜设计规范，全部基于实测数据。

---

## 📖 这是什么？

这是一个面向 AI 编码助手的设计流程 skill。它把「凭感觉设计」变成「按实测数据 + 强制流程设计」：

1. **强制 Design Brief** — 编码前必须输出 7 节设计规格（风格 / 字体 / 色板 / 栅格 / 圆角 / 动效 / 引用依据）
2. **实测 Token 规范** — 字阶、圆角、色板、行高全部来自 12 份真实产品的 DESIGN.md 逆向工程
3. **版式模式库** — 320 条落地页样本的 section 级分布统计（hero / feature / pricing / footer …）
4. **lint 脚本** — 自动拦截 9 类「AI 味」（紫蓝渐变、裸 sans-serif、emoji 图标、纯白底 …）
5. **7 站实测拆解** — 完整站点的 token / 结构 / 动效取证

---

## 📁 文件结构

```
skills/web-design-core/
├── README.md                      👈 本文件
├── SKILL.md                       👈 核心：触发条件 + 强制流程 + Brief 模板 + 自检清单
├── meta.yaml                      👈 根 README 脚本读取的元数据
├── references/                    👈 四份规范参考
│   ├── anti-patterns.md           # 5 个已泛滥套路 + 替代方案 + grep 检查命令
│   ├── tokens-and-type.md         # 字阶 / 圆角 / 色板 / 行高 / 字体（refero 12 份实测）
│   ├── layout-patterns.md         # 10 类版式模式 + 21 种风格流派（320 条样本）
│   ├── motion.md                  # 缓动 / 时长 / 滚动编排（7 站拆解）
│   └── component-systems.md       # Semi / Ant / Element / shadcn / Lucide 对比
├── scripts/
│   └── lint_design.sh             # 9 项自动检查，exit 0/1
└── teardowns/                     # 7 个站点完整拆解（六节齐整）
    ├── digilab.md                 # Next.js + GSAP + Lenis，3 条过冲曲线
    ├── maxmilkin.md               # 全站锁一条缓动，字号抽掉中量级
    ├── nfinitepaper.md            # 全站只用 400 字重，alpha 阶梯替代灰阶
    ├── srg.md                     # 双族硬分工，三档底色做节奏
    ├── pear.md                    # sticky 多场景编排，53 屏讲 3 个概念
    ├── goodfella.md               # 零圆角零阴影零边框，字重倒置
    ├── radarlaboratory.md         # 双速动效，配色模拟雷达屏幕
    └── _FAILED-batch2.md          # 5 个站点渲染失败模式与对策
```

---

## 🎯 强制三步流程

| # | 步骤 | 产出 | 缺失后果 |
|---|:---|:---|:---|
| ① | 加载 references（`anti-patterns.md` 必读） | — | 违规不可知 |
| ② | 编码前输出 **Design Brief**（7 节） | 设计规格文档 | **视为未完成** |
| ③ | 编码后跑 `lint_design.sh` + 10 项自检 | 自检报告 | **视为未完成** |

### Design Brief 七节

1. **风格定位** — 流派 / 色调 / 参考站点
2. **Typography** — 字体族 / 字阶 / 基准字号 / 行高
3. **色板** — 底色 / 强调色 / 功能色 / Alpha 阶梯
4. **栅格与间距** — 容器宽度 / 栅格列数 / 间距基数
5. **圆角与阴影** — 控件圆角 / 卡片圆角 / 阴影策略
6. **动效** — 主曲线 / 时长 / 滚动编排
7. **引用依据** — 每条规格标注来自哪个 reference 的哪一节

---

## 🔍 lint 脚本检查项

```bash
bash scripts/lint_design.sh <项目目录>
```

| # | 检查项 | 违规信号 |
|---|:---|:---|
| 1 | 紫蓝渐变 | `linear-gradient` 含 `#6366f1` / `#8b5cf6` 系 |
| 2 | 裸字体 | `font-family: sans-serif` 无具体字体族 |
| 3 | emoji 图标 | HTML/JSX 中出现 😀-🛿 范围字符 |
| 4 | 单一圆角 | 全站只有 1 种圆角值（无控件/卡片分档） |
| 5 | 纯白底 | `background: #fff` / `rgb(255,255,255)` |
| 6 | 纯黑字 | `color: #000` / `rgb(0,0,0)` |
| 7 | 玻璃拟态滥用 | `backdrop-filter: blur` 超过 3 处 |
| 8 | 滚动劫持 | `body` / `html` 上 `position: fixed` |
| 9 | 全大写+负字距 | `uppercase` 配 `letter-spacing < -0.03em` |

exit 0 = 全过；exit 1 = 有违规，需修正或在 Brief 中论证保留。

---

## 📊 核心实测结论

### 版式（landingfolio 320 条样本）

| Section | 主导模式 | 占比 |
|---|---|---|
| Hero | split image right | **40%** |
| Hero | centered | 30% |
| Hero | product screenshot | 26% |
| Feature | split image right | 40% |
| Feature | 3-column grid | 24% |
| Pricing | 2-tier / single plan | 各 36% |
| Header | logo left, links right | **72%** |
| Footer | multi column | **76%** |
| CTA | centered | 64% |
| Logo Cloud | row | 72% |

**全局基调**：浅色 **72.8%**（landingfolio）/ **71.4%**（designprompts）—— 两个独立样本交叉验证。

### Token（refero 12 份 DESIGN.md）

| 维度 | 实测结论 |
|---|---|
| 字阶 | Minor Third **1.2 = 9/12**，Major Second 1.125 = 3/12，无一份 ≥1.25 |
| 圆角 | 双峰：控件 4–6px / 卡片 12–16px，中间值 8–10px 罕见 |
| 强调色 | **11/12 站只有一个饱和强调色** |
| 字体 | **11/12 站自托管定制字体**，只 1 站用现成 Inter |
| 分区 | 1px 发丝线替代阴影（Linear 明令 "0.5px hairline instead of shadows"） |

---

## 🚫 五条硬禁止

1. 紫色渐变 + 模糊光晕（AI 产品默认套路）
2. 三列图标卡 + 通用线性图标（模板味）
3. 玻璃拟态当主视觉（性能差）
4. 纯黑纯白 + 全大写 + 负字距（CJK 直接失效）
5. `body{position:fixed}` 滚动劫持 + 每屏淡入（拖垮 LCP）

每条都有替代方案，见 `references/anti-patterns.md`。

---

## 🔗 数据来源

| 来源 | 样本 | 用途 |
|---|---|---|
| landingfolio.com | 320 条版式样本 + 38 类组件计数 | section 级模式分布 |
| designprompts.dev | 21 种风格完整规格 | 风格流派分类 |
| styles.refero.design | 12 份完整 DESIGN.md | token 实测值 |
| recent.design | 10 条（Style/Color/Category/Interaction 标签） | 配色与交互趋势 |
| detail.design | 12 条交互细节 | 动效与微交互 |
| spottedinprod.com | 12 条 UI 细节 | 界面细节 |
| inspora.design | 12 条标题 + tag | 风格标签 |

**未覆盖**：awwwards（WAF 403）、ui-design-bench（TLS 握手失败）—— 网络环境限制，未绕过。

---

## 🧩 与其他 skill 的关系

| Skill | 关系 |
|---|---|
| `frontend-design` | 互补：本 skill 提供强制流程与量化门禁，`frontend-design` 提供更细的 CJK 排版 / 动效词汇 / 组件模式参考 |
| `modern-web-showcase` | **已被本 skill 取代** |

---

## 📄 License

MIT
