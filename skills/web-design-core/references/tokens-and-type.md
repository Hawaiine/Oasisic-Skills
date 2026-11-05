# Tokens & Typography — 实测 Token 规范

> 来源：`patterns.md` §1.10、§2.3、§3 + `component-systems.md` §1

---

## 1. 字阶（Type Scale）

### 1.1 比值选择（refero 12 份实测）

| 比值 | 出现频率 | 适用场景 |
|---|---|---|
| **Minor Third (1.2)** | **9/12 = 75%** | 默认选择，SaaS/工具 |
| Major Second (1.125) | 3/12 = 25% | 紧凑布局、信息密度高 |
| Perfect Fourth (1.25+) | 0/12 = 0% | ❌ 已不推荐 |

**结论**：1.125–1.2 是当前默认，1.25 以上已罕见。

### 1.2 基准字号

| 平台 | 基准 | 最小字号 |
|---|---|---|
| 桌面 | 14–16px | 12px |
| 移动 | **≥16px**（防止 iOS 自动缩放）| 14px |
| CJK 正文 | 16px | 14px |

### 1.3 行高（Line Height）

| 元素 | 西文 | CJK |
|---|---|---|
| 大标题（display） | 1.0–1.15 | 1.15–1.25 |
| 小标题（heading） | 1.15–1.25 | 1.25–1.4 |
| 正文（body） | 1.5–1.7 | **1.7–1.8** |
| 紧凑列表 | 1.4 | 1.6 |

**关键规则**：
- CJK 行高必须比西文高 0.1–0.2
- 正文行高 < 1.5（西文）或 < 1.7（CJK）会降低可读性

**依据**：
- [Linear](https://styles.refero.design/style/90ce5883-bb24-4466-93f7-801cd617b0d1)：display 72px/510/1.0，body 16px/400/1.5
- [Intercom](https://styles.refero.design/style/12255b63-e506-4bc1-a4cd-d05487de32f3)：正文 1.6

---

## 2. 字体选择

### 2.1 自有字体是"高级"的门槛

**refero 12 份实测**：11 份使用自托管定制字体，只有 1 份（Raycast）用现成 Inter。

| 站点 | 字体 | 类型 |
|---|---|---|
| Figma | figmaSans | 自托管 Variable |
| Linear | Inter Variable | 自托管（定制版）|
| Perplexity | pplxSans | 自托管 |
| Cursor | CursorGothic | 自托管 |
| OpenAI | OpenAI Sans | 自托管 |
| Stripe | sohne-var | 自托管 |
| Raycast | Inter | ❌ 现成字体 |

**结论**："用系统字体"在这个层级已不是默认，"有自己的字体"才是。

### 2.2 字体栈推荐

```css
/* 西文 SaaS */
font-family: "CustomSans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

/* CJK 混排 */
font-family: "CustomSans", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;

/* 等宽 */
font-family: "CustomMono", "SF Mono", Monaco, "Cascadia Code", monospace;
```

**禁止**：裸 `font-family: sans-serif;` 或 `font-family: Arial;`

---

## 3. 色板

### 3.1 暖白底取代纯白（三源交叉验证）

| 来源 | 浅色占比 | 样本量 |
|---|---|---|
| landingfolio | **72.8%** (233/320) | 320 |
| designprompts | **71.4%** (15/21) | 21 |
| refero SaaS | 100% 用暖白，0% 用纯白 | 12 |

**常见暖白值**：
- Intercom: `#faf9f6`
- Perplexity: `#faf8f5`
- Cursor: `#f7f5f0`（warm parchment）
- Brex: "white concrete"

**禁止**：纯 `#fff` 做页面画布（只在卡片表面用）。

### 3.2 单一强调色 + Alpha 阶梯

**refero 12 份中 11 份只有一个饱和强调色**。

**Alpha 阶梯标准**（来自 Linear/Intercom）：
- `0.1` — 悬停底色（hover background）
- `0.22` — 分割线、禁用态
- `0.6` — 次要文字
- `1.0` — 主强调色

**Linear 的明令**：
> Do not introduce additional chromatic accent colors as actions.

**禁止**：多个饱和强调色（红、蓝、紫同时出现在 CTA）。

### 3.3 暗色模式基准

| 系统 | 深色底 | 浅色底 |
|---|---|---|
| Linear | `#08090a` | `#fafafa` |
| Raycast | `#1c1c1e` | `#ffffff`（卡片）|
| Mercury | `#17172a` | `#f5f5f7` |

**规则**：暗色底用近黑（`#08090a` 系），不用纯 `#000`（对比过强）。

---

## 4. 间距

### 4.1 基数选择

| 基数 | 使用场景 |
|---|---|
| **4px** | 默认选择，8 的倍数体系（4/8/12/16/24/32…）|
| 8px | 大尺寸组件（如仪表盘、数据可视化）|

**推荐栈**（4px 基数）：
```
4px / 8px / 12px / 16px / 24px / 32px / 48px / 64px / 96px
```

---

## 5. 圆角（Border Radius）

### 5.1 双峰分布（refero 实测）

| 元素 | 实测值分布 | 推荐 |
|---|---|---|
| **控件**（buttons/inputs） | 4px(3) / 6px(3) / 12px(1) / 32px(pill, 1) | **4–6px** |
| **卡片**（cards） | 4px(3) / 12px(3) / 16px(3) / 6px(2) | **12–16px** |

**关键发现**：
- **中间值 8–10px 罕见**（只有 inputs 10px 出现 1 次）
- **两档制**：控件锐利（4–6px）+ 卡片容纳（12–16px）

**禁止**：全站统一用 8px（无层次）。

**依据**：
- [Stripe](https://styles.refero.design/style/48e5de76-05d5-4c4e-a269-c7c245b291ec)：buttons 4px / cards 4px
- [Linear](https://styles.refero.design/style/90ce5883-bb24-4466-93f7-801cd617b0d1)：buttons 6px / cards 12px
- [Ramp](https://styles.refero.design/style/b38702a0-75ab-474c-9106-00b624535825)：buttons 6px / cards 16px

---

## 6. 阴影策略

### 6.1 1px 发丝线替代阴影做层次

**三家明令**：
- Linear: `Use 0.5px hairline borders instead of shadows for surface separation`
- Intercom: `thin hairline borders in warm stone, no decorative shadows`
- Mercury: 用 `Slate Border` 分卡

**规则**：
- **阴影只在真正浮起的层用**：弹窗、下拉、toast
- **其余用 1px `rgba(0,0,0,0.1)` 发丝线**

### 6.2 浮层阴影标准

```css
/* 小浮层（dropdown） */
box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);

/* 中浮层（modal） */
box-shadow: 0 8px 24px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.08);

/* 大浮层（drawer） */
box-shadow: 0 16px 48px rgba(0,0,0,0.16), 0 4px 12px rgba(0,0,0,0.12);
```

**禁止**：
- 装饰性阴影（如卡片默认带阴影）
- 过重阴影（`rgba(0,0,0,0.5)` 系）

---

## 快速决策表

| 需求 | 推荐值 | 来源 |
|---|---|---|
| 字阶比值 | 1.2 | refero 9/12 |
| 基准字号（桌面）| 16px | 主流 |
| 正文行高（CJK）| 1.7–1.8 | 可读性标准 |
| 页面底色 | `#faf9f6` | Intercom/Perplexity |
| 强调色数量 | 1 个 | refero 11/12 |
| 控件圆角 | 4–6px | refero 双峰 |
| 卡片圆角 | 12–16px | refero 双峰 |
| 间距基数 | 4px | 8 的倍数体系 |
| 分割线 | 1px `rgba(0,0,0,0.1)` | Linear/Intercom |

---

## 更新日志

- **2026-11-06**：从 `patterns.md` + `component-systems.md` 提取实测数据，补充依据链接。
