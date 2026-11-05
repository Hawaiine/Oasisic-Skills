# Motion — 动效规范

> 来源：`patterns.md` §1.5/§2.4 + `analysis/00-cross-site-synthesis.md` §1.5/§1.7

---

## 1. 缓动曲线

### 1.1 全站只用 1–2 条主曲线（实测收敛）

**7 站拆解中 4 站明确单曲线策略**：

| 站点 | 主曲线 | 规则 |
|---|---|---|
| maxmilkin | `cubic-bezier(0.11,0.82,0.39,0.92)` | 全站锁死这一条 |
| pear | 5 处，但只有 1 种曲线 | 量多但统一 |
| digilab | 3 条过冲曲线 y1=1.02–1.08 | opacity 用无过冲 |
| radarlaboratory | UI 0.14–0.18s / 背景 2.4–2.8s | 双速体系 |

**禁止**：全站用 5+ 条不同缓动（linear / ease / ease-in-out / cubic-bezier 混用）。

### 1.2 推荐曲线

```css
:root {
  /* 主曲线：轻微过冲，y1 = 1.02–1.08 */
  --ease-main: cubic-bezier(0.23, 1.04, 0.32, 1);

  /* 纯淡入：无过冲，用于 opacity/color */
  --ease-fade: cubic-bezier(0.23, 1, 0.32, 1);

  /* 禁止第三条（除非有特殊需求并在 Brief 中说明）*/
}
```

**过冲曲线的视觉效果**：运动轻微超过目标位置再弹回，有「弹性」感而不失控制感。

**opacity 不用过冲**（来自 digilab 实测）：淡入淡出用无过冲曲线，否则元素会在接近消失时"反弹"。

---

## 2. 时长分级

### 2.1 三档时长（来自 maxmilkin 实测）

| 档位 | 时长 | 用途 |
|---|---|---|
| **即时** | 150ms | hover 颜色、focus 边框、button active 态 |
| **常规** | 300–500ms | 元素进场、下拉展开、tab 切换 |
| **大进场** | 2–3s | Hero 背景动画、氛围性装饰 |

**5–10 倍差制造层次感**：微交互 0.15s vs 氛围 2.5s，反差越大层次越清晰。

### 2.2 双速体系（radarlaboratory 模式）

```css
/* 工具类界面推荐 */
button, input, [class*="interactive"] {
  transition-duration: var(--duration-instant); /* ≤150ms，操作感 */
}

.ambient-bg, .decorative {
  animation-duration: var(--duration-ambient);  /* ≥2s，氛围感 */
}
```

**适用场景**：控制台/仪表盘（操作区 150ms + 背景装饰 2.5s）。

---

## 3. 动画属性约束

### 3.1 只动 transform 和 opacity

```css
/* ✅ 正确：GPU 加速，不触发布局 */
.enter { transform: translateY(20px); opacity: 0; }
.enter.active { transform: translateY(0); opacity: 1; }

/* ❌ 禁止：触发布局重排 */
.enter { height: 0; margin-top: -20px; }
.enter.active { height: auto; margin-top: 0; }
```

**禁止动画属性**：`width`、`height`、`top`、`left`、`right`、`bottom`、`padding`、`margin`。

**例外**：`color` / `background-color` 可以动，GPU 代价小。

### 3.2 减少动效媒体查询（必须实现）

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    /* 保留 opacity/color 变化，剥离轴向运动 */
    transition-property: opacity, color !important;
  }
}
```

**必须实现**，不是可选项。

---

## 4. 滚动编排

### 4.1 允许 vs 禁止

| 模式 | 状态 | 原因 |
|---|---|---|
| `position: sticky` + 原生滚动 | ✅ 允许 | 可访问、可调试、scrollY 正常工作 |
| GSAP ScrollTrigger | ✅ 允许 | 不劫持，只监听滚动位置 |
| `body { position: fixed }` + JS 虚拟滚动 | ❌ **禁止** | scrollY 恒 0、iOS 冲突、输入法吃手势、屏读器失效 |
| Lenis（需要虚拟滚动） | ❌ **禁止（默认配置）** | 默认模式劫持原生滚动 |
| `overscroll-behavior` 控制回弹 | ✅ 允许 | 非劫持 |

**digilab / nfinitepaper / goodfella 全部用了 `body{position:fixed}`，实测 `scrollY` 恒为 0，无头 Chromium 无法截图，屏读器失效。**

### 4.2 多场景编排（sticky 模式）

```html
<!-- 来自 pear.no 实测模式 -->
<div class="stage" style="height: calc(var(--scenes) * 100vh * var(--dwell))">
  <div class="pin" style="position: sticky; top: 0; height: 100vh; overflow: hidden;">
    <div class="scene" data-scene="1" style="position: absolute; inset: 0; opacity: 0;">...</div>
    <div class="scene" data-scene="2" style="position: absolute; inset: 0; opacity: 0;">...</div>
    <!-- CSS: .scene[data-active] { opacity: 1; } -->
  </div>
</div>
```

**原理**：容器撑高 = 场景数 × 停留时间，pin 区块 sticky 钉住视口，场景层靠 `scrollY` 切换 `opacity`，不劫持任何事件。

---

## 5. 实施清单

- [ ] 全站使用 1 条主曲线 + 1 条淡入曲线（至多 2 条）
- [ ] 时长三档：150ms / 300-500ms / 2-3s
- [ ] 只动 `transform` / `opacity`，不动布局属性
- [ ] 实现 `prefers-reduced-motion`（剥轴向运动，保 opacity/color）
- [ ] 无 `body { position: fixed }` 滚动劫持
- [ ] 关键操作区 ≤150ms（操作感），装饰区 ≥2s（氛围感）

---

## 更新日志

- **2026-11-06**：从 `analysis/00-cross-site-synthesis.md` §1.5/1.7 提取，补充代码示例。
