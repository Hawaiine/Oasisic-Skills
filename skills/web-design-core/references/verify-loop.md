# 实测验收回路（不看图也能判对错）

> 这套流程来自一次真实的整站改版返工：第一版按“深色玻璃 + 首屏折叠”交付，用户只说“不行”，而当时读图服务挂了，只能靠数字定位问题——结果发现三处结构性缺陷（折叠开关失效、手机端图表压到 85px、网格选择器选错卡片）。结论：**视觉验收可以没有眼睛，不能没有数字。**

## 1. 每次改动后必测的 6 个数字

用浏览器执行（Hermes：`browser_exec` + `js(...)`；其它宿主用 CDP/Playwright）。

```js
(() => ({
  ovf: document.documentElement.scrollWidth - document.documentElement.clientWidth, // 必须 0
  docH: document.documentElement.scrollHeight,                                      // 同屏密度是否如预期
  ext: performance.getEntriesByType('resource')
        .filter(r => !r.name.startsWith(location.origin)).length,                    // 必须 0（无外部依赖）
  rows: document.querySelectorAll('#tableBody tr').length,                           // 数据是否真的渲染
  revealed: document.querySelectorAll('.rv.in').length + '/' + document.querySelectorAll('.rv').length,
  fonts: getComputedStyle(document.body).fontSize + ' / ' + getComputedStyle(document.body).fontFamily.split(',')[0]
}))()
```

两个视口都要跑：**1440×900**（桌面布局是否铺开）与 **390×844**（是否横向溢出、是否误用桌面布局）。

```python
cdp('Emulation.setDeviceMetricsOverride', width=390, height=844, deviceScaleFactor=2, mobile=True)
```

## 2. 四个「静默失败」陷阱（都实测踩过）

| 陷阱 | 现象 | 判法 | 修法 |
|---|---|---|---|
| `.hide{display:none!important}` 盖掉内联样式 | 点了「展开」没反应 | `getComputedStyle(el).display` 仍是 `none` | 切换必须 `classList.toggle('hide')`，只改 `style.display` 无效 |
| 首屏 reveal 依赖 IntersectionObserver | IO 未触发/被禁用时整页 opacity 0 = 白屏 | `document.querySelectorAll('.rv.in').length` 为 0 | 加 `<noscript><style>.rv{opacity:1}</style></noscript>` + `setTimeout(…,1800)` 兜底 |
| 固定 viewBox 图表 | 390 宽下 940×240 只有 85px 高 | `svg.getBoundingClientRect().height` | 按 `innerWidth<=860` 切到 `430×210`，并挂 `resize` 重绘 |
| 网格里用 `:nth-of-type(n)` 定位卡片 | 网格塌成一列/选中错误元素 | `document.querySelector('#chartCard').getBoundingClientRect()` 为 null 即选错了 | 关键容器给 `id`，选择器用 id；结构变动后重测 |

## 3. 改版纪律

1. **先备份、留回滚点**：整站重写前复制原入口（`index.js.bak.vNN`），回滚只需改一行 import。
2. **一次只动一类变量**：布局 / 配色 / 信息密度分轮改，否则「不行」时无法判断是哪个变量导致的。
3. **每轮报数字，不报感觉**：交付写「ovf 0、docH 1316、mobile 2175、ext 0、rows 73」，不写「更清爽了」。
4. **结构改完重跑同一组数字**：只对比变化项；新增组件要补一条新的计数（例如 `.qrow` 57）。

## 4. 与 lint 脚本的分工

- `scripts/lint_design.sh`：静态源码层面（渐变、纯白底、统一圆角、玻璃拟态计数…），离线可跑。
- 本文这套：运行态层面（布局溢出、渲染结果、资源外链、动画可达性），必须真实浏览器。

两者都过才算完成；只有 lint 通过而运行态没测，就是「源码干净但页面坏了」。