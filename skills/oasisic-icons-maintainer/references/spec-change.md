# Spec Change — 规范值变更与传播

专项流程：改变仓库的官方图标规范值并传播到每个声明它的位置。核心是 SKILL.md 第 8 节 Change Propagation 的
「spec 传播」分支：spec → affected scripts → generators → tests → docs → existing assets → CI，不能只改规范文本。

> **SSOT of 规范 = `scripts/normalize-icons.py` 顶部的 `RADIUS` 常量 + docstring**。任何与它不一致的文档都是陈旧残留。
> 本文档只记录**变更流程**，不记录当前数字——先读仓库当前值再动手。

## Geometry 校验的已知问题（每一次规范化都适用）
PIL `ImageDraw.rounded_rectangle(radius=R)` 是圆角矩形角，不是真 Apple supersquare，且**不**把角往里收 R 像素。
512×512 实测边缘内缩：R=99→约 90px，R=115→约 105px（第 0 行的透明带宽 R−10）。

- `scripts/normalize-icons.py` 里的 `int(a[RADIUS + 1, 0]) == 0` 对当前 squircle 是**错的**（[RADIUS+1][0] 已不透明），
  会误判合规图标为不合规。**把它当陈旧逻辑**，不要「修」图标去迎合它；修断言属于独立 bugfix（PR-CANDIDATE），
  需与 `rounded_mask()` 实测几何对齐（正确方向应检测透明带边缘，如 `RADIUS - 1` 一带，须实测后定案）。
- 校验手写 squircle 靠**测量角**：第 0 行从 x=0 走到首个不透明像素（左/上内缩），列同理，两值都 ≈ R−10（明显 >0 = 角被切），
  且中心不透明。`RADIUS+1` 型检查会 false-fail——是预期，不是 bug。

## 流程
1. 确认新值：Apple squircle 圆角 ≈ 图标尺寸 22.37%；用户没说精确就按仓库现有常量换算并让用户确认。
2. 枚举每个声明旧值的文件：
   `grep -rn "<旧值>" --include="*.py" --include="*.md" . | grep -v ".git"`（radius/尺寸/alpha/容器/PNG mode 对应所有写法）。
   典型：`README.md`（贡献指南 · 图标质量要求 + 发布与使用）、`docs/references/icon-quality-notes.md`、
   `scripts/normalize-icons.py` docstring、`scripts/optimize-icons.py` docstring、独立 spec 文档。
3. **按 code → docs → README 顺序改**：
   - `normalize-icons.py`：`RADIUS` 常量 + 顶部整段 docstring（规范 bullet + 用法保持在一个三引号块内，拆开文件就解析失败——每改必 lint）。
   - `optimize-icons.py` docstring：颜色/模式规则一致（严格 RGBA、`color_type_reduction=False`）。
   - `icon-quality-notes.md`：需要则重构，保留 历史/演变 表让旧值可追溯退役时间。
   - `README.md`：贡献指南质量 section + 发布与使用 summary 行。
   - `docs/references/upstream-history.md`：加里程碑/历史注记。仓库与上游已解耦——**绝不重造** mapping table / sync 脚本 / daily-sync workflow。
4. 若旧值用于存量 PNG：跑仓库自带 `python3 scripts/normalize-icons.py --apply`（幂等、保护手更新图标）；不写 ad-hoc 几何代码。
5. **传播门禁**：改完后 grep 仓库旧值，要求**非历史命中 = 0**；历史/演变表是唯一允许的残留。`git status -sb` 核对。
6. 提交 + **分支 + PR**（step 5 先于 commit 跑）；commit body 注明「spec docs/scripts/docstrings 已同步」。

## 坑
- **docstring 必须整体在一个三引号块**：它是项目规范正文；用法示例行落到两个 `"""` 之间模块就解析失败——每次改后 lint。
- **残留 grep 在 commit 之前**，不是之后：带着旧值进 docstring 等于把退役规范教给下一个会话。
- **历史表是唯一允许残留**；其余命中都是 residue。
- **改规范数 = 每个消费该数的地方都更新**：scripts、docs、README、CI workflows、引用该值的 commit message 都扫
  （`scripts/*.py` 和 `.github/workflows/*` 也查，不只文档）。
- **README 示例比它引用的图标活得久**：指向已删变体（`Spotify01`、`Netflix01`…）的 quick-start / 命名示例是死链，
  即使计数表已对。批量删改后 grep README 每个 cite 的路径确认在磁盘；换一个仍发该变体的品牌当示例，而不是拖进散文。
  同 commit 复核重生成的 manifest——陈旧的 surge-icon.json 在下一次 regen 前一直指着已删文件。
- **GFM 表格静默错渲**：缺分隔行（`|---|---|`）会把分类表降成纯文本、GitHub 上无报错。重写表格后在人可读渲染里目检一次，别只数行。
- **de-coupled 仓库别回耦合**：grep 旧值若命中 `sync-upstream`/`daily-sync`/`icon-mapping`，那些文件已删——当残留处理，不要重建。

## 与其它 reference 的关系
- 若规范变化伴随既有资产重规范化，处理方式参照 `references/intake.md`（共享 normalizer / 掩码、无损压缩、像素保真）。
- 若规范变化源自新品牌登记，先走 `references/ssot-sync.md` 的 SSOT 层。