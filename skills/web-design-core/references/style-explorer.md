# 风格对比页生成器

把 2–4 个候选方向并排成**一个离线 HTML**，同一视口、同一内容，用户直接点选。生成器 vendored 自 [oil-oil/oil-ui](https://github.com/oil-oil/oil-ui)（MIT），已去掉上游品牌资源与外链，字体随包附带（Instrument Serif，OFL）。

```bash
python3 skills/web-design-core/scripts/build_explorer.py <候选目录 | 候选 HTML 文件…> \
        [--output style-explorer.html] [--force]
```

输出是单文件（自包含 CSS/字体/预览），**无外部请求**，双击 `file://` 也能打开。

## 输入

最简单：一个目录里放几个候选 HTML，直接传目录；显示名取 `<title>`，没有就用文件名。

要展示「方向卡」信息时，同目录放 `manifest.json`：

```json
{
  "title": "项目名 · 三方向对比",
  "candidates": [
    {
      "source": "a.html",
      "name": "方向 A · 纸感编辑",
      "concept": "像一本被反复翻阅的纸书",
      "typography": "衬线标题 84px / 正文 17px / 行高 1.72",
      "palette": ["#f4efe6", "#1a1613", "#b23a1e"],
      "traits": ["大留白", "发丝线", "无圆角"]
    },
    { "source": "b.html", "name": "方向 B · 深夜仪表", "concept": "把状态压缩进一屏" },
    { "source": "c.html", "name": "方向 C · 瑞士网格", "concept": "让结构自己说话" }
  ]
}
```

- `source`：相对 manifest 的 HTML 路径（也可传截图，`"kind": "image"`）
- 跑在本机开发服务器上的真实页面：`"kind": "url"` + `"url": "http://localhost:3000/xxx"`（只接受回环地址）
- `name` / `concept` / `typography` / `palette` / `traits` 都可省略，省略即不显示；**`concept` 就是北极星那一句**，写不出来说明方向没定，见 `visual-direction.md`

## 三个候选的最小自检

生成完不要只看「有没有输出」，跑这四项：

```js
({
  ovf: document.documentElement.scrollWidth - document.documentElement.clientWidth, // 必须 0
  names: document.querySelectorAll('[data-candidate]').length,                       // == 候选数
  empty: document.querySelector('.empty').hidden,                                    // 必须 true
  ext: performance.getEntriesByType('resource').filter(r => !r.name.startsWith(location.origin)).length // 0（file:// 下恒为 0）
})
```

再点一次任一 `Select`，按钮文案应变成 `Selected`（选择状态会被记住，用于回传用户决定）。

## 已知坑

| 现象 | 原因 | 处理 |
|---|---|---|
| 页面能打开但空白、`.empty` 仍显示 | 模板里 `#pro-badge` 被删掉，脚本 `getElementById('pro-badge').hidden=...` 抛错，后续渲染全停 | 保留该元素（`hidden` 即可），不要为了去品牌把节点删掉 |
| 报「找不到本地资源 logo.png / fonts/*.ttf」 | 模板引用了相对资源 | 本仓库已随包提供 `assets/fonts/instrument-serif/`；替换品牌图时用 data URI，别新增外部文件 |
| 手机端挤成一团 | 生成器是响应式单列，但候选页本身可能是桌面布局 | 候选小样自己也要做 390 宽适配，对比页不会替它重排 |

## 与 `visual-direction.md` 的分工

- `visual-direction.md`：怎么产出**互不相似**的三个方向（差异轴、牺牲项、模糊词翻译）
- 本文：把方向变成**用户能点选的对比页**，以及验收它的四个数字

两者一起用：先按 §3 定三条差异轴 → 写 3 个候选 HTML → 跑生成器 → 用户点选 → 选中的方向再进 Design Brief 落地实现。