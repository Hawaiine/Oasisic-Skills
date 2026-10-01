---
name: oasisic-icons-maintainer
description: >
  Use when maintaining Hawaiine/Oasisic-Icons (brand icon asset repository): SSOT config/brands.json +
  categories.json, relationship resolver, physical icon paths, dynamic ecosystem threshold, asset model
  (512×512 RGBA squircle), generated files, documentation discipline, validation gates, PR workflow.
  Load before adding / renaming / deleting brands, moving icons, editing docs with icon paths, or
  deciding whether "CI is green" is enough.
version: 1.0.0
tags: [oasisic-icons, icons, ssot, brands-json, resolver, ecosystem, asset-model, docs, ci, github]
---

# Oasisic-Icons Maintainer

> 面向 **Hawaiine/Oasisic-Icons** 的长期维护规则：事实、判断方法、验证边界。
> **不要凭记忆工作**：任何数字、文件名、关系都必须在动手前从当前仓库读取（见 §12）。

## When to Use

- 新增 / 删除 / 改名品牌，迁移图标目录，调整一级分类
- 判定 `parent_brand`、生态根、物理路径该长什么样
- 处理用户提供的品牌图标（入库 / 规范化 / provenance）
- 修改文档（README / AGENTS / docs），尤其是含**可复制图标路径**的位置
- 审「CI 绿灯」是否等于「正确」，或判断某风险是否必须在本次修复
- 判断某段旧知识该进 SSOT、进 Review Queue，还是进研究层文档

## 0. Repository Identity & Boundaries

- Oasisic-Icons 是**独立最高上游**：不默认同步任何第三方图标库；新增/替换图标直接走本仓库 PR。
- **下游（mihomo-rules 等）是 consumer**，不是本仓库事实来源：不得为了让下游舒服而改关系事实；
  下游差异记为 `DOWNSTREAM_STALE`，单独阶段同步。
- 仓库内**事实** = `config/*.json` + 代码行为 + git 历史；文档只是派生物或人工参考。
- 历史文档（migration / 审计快照）记录的是**当时**的事实，不得「顺手修正成当前状态」。

## 1. SSOT

```text
config/brands.json       # 品牌 / 图标 / 关系；含 parent_brands_without_icon 白名单
config/categories.json   # 分类元数据（functional / ecosystem、status active|reserved）
```

- 条目字段：`id` / `display_name` / `category` / `entity_type` / `icon_path`，可选 `parent_brand`、`canonical`、`icon_status`。
- `entity_type`：`product_brand`（canonical 主体）/ `country` / `system_icon` / `tool_app` / `ecosystem`（生态根）。
- **`category` = 第一层物理目录**；**`parent_brand` = immediate Brand/Product parent**。
  两者语义完全独立，**禁止互相自动推导**（例如 `parent_brand = Xiaomi` 不得把 `category` 改成 `Xiaomi`）。
- 白名单 `parent_brands_without_icon` 是「无自身图标、但可作为某品牌直接父级」的母公司名单，**就在 SSOT 内**；
  导出文件里的同名键只是镜像，不是第二真相。
- 派生文件（`config/surge-icon.json`、`config/brand-relationships.json`、`brand-glossary.md`、
  `physical-hierarchy-audit.md`、各级 `README.md`）**不得手工编辑**，必须由生成器重算。

## 2. Relationship Model

- `parent_brand` 只表达**品牌/产品层级**（immediate parent）：
  **不等于** ownership / 收购 / 持股 / developer / provider / platform / hosting / distribution / 平台集成。
  平台集成事实（如「某 AI 可通过某平台使用」）不得倒推 `parent_brand`。
- 关系计算唯一入口：`scripts/brand_relationships.py`
  （`resolve_graph_root` / `resolve_ecosystem_root` / `brand_role` / `_ancestor_set` / 校验函数）。
- **禁止第二套逻辑**：任何脚本/生成器/校验器不得重写关系推导，不得散落 `if entity_type == ...`
  （唯一 predicate：`is_canonical_brand()`）。
- 环检测靠访问集合，没有 magic depth 上限；self-parent、missing parent、白名单母公司分别处理，
  真正无法机器判定的现实歧义进 Review Queue（§6）。
- 关系事实只有一处：`brands.json`。研究/证据文档（ownership audit）是**研究层**，不是关系真相。

## 3. Physical Path

- 唯一路径解析器：`expected_icon_path()`。规则：

```text
icons/<category>/<brand>/<brand>.png                    # category == graph root 时不重复节点目录
icons/<category>/<middle-parent>/<brand>/<brand>.png    # 同类中间父品牌递归嵌套（可继续加深）
```

- `category == graph root` → **不重复**该节点目录；`cross-category parent` → **不机械迁移**，
  子品牌保留自身 category 与物理位置，语义边只留在 SSOT。
- 无自身图标的 parent **不制造伪目录、不复制他人资产**（登记白名单）。
- **1 brand = 1 canonical asset**：默认文件名 `<品牌名>.png`（无后缀）。
  变体命名位（`<品牌名>NN.png`）保留但当前全库不使用；不得为「多版本」另建并行真相。
- 叶子路径必须由 resolver 派生；CI 逐字节校验 `icon_path` 与磁盘一致。

## 4. Ecosystem（动态判定，不维护清单）

```text
graph root      = SSOT 内有条目 且 SSOT 内无父
ecosystem root  = graph root 且 entity_type = ecosystem
阈值            = canonical descendants（product_brand 后代，含孙代）≥ 2
```

- 阈值常量**以 resolver 代码为准**，不要凭记忆或旧文档写死；生态数量永远动态派生，禁止手工清单。
- 双向校验：声明 `entity_type=ecosystem` 必须达到阈值；未达阈值的 graph root（或仅有白名单母公司/单后代）
  **不得**冒充生态根。
- 中间层节点（SSOT 内有父）即使后代很多也**不建一级分类**——阈值只看生态根 descendants，防止分类爆炸。
- 生态分类目录 = `icons/<Root>/`；生态根自身图标（若有）= `icons/<Root>/<Root>/<Root>.png`。

## 5. Asset Model（图标规范）

- 几何：**512×512 / PNG / RGBA / squircle 圆角 r ≈ 115px（≈22.4%）/ 四角 alpha=0 / 保留原始底色**。
- **像素保真**：不得重绘 / 改色 / 去背景 / 改字形 / 改比例。使用官方素材时只允许「放入项目标准容器」：
  等比缩放 + 标准圆角遮罩；logo 本体的像素不得被人为改动。
- 三层概念必须分清：

```text
Official source asset   # 品牌方发布的原始文件（如官方 Brand Guidelines 资产包）
Repository asset        # 本仓库落库的规范化 PNG（derived asset，不是官方原文件逐字节落库）
Recreated artwork       # 禁止
```

- `icon_status` 语义：
  - 无该字段 + 有真实 `icon_path` ⇒ **official**（默认，绝大多数条目）
  - `generated_temporary` ⇒ **必须**有真实 `icon_path`（临时占位，需后续替换；不得走 pending 豁免）
  - `pending` ⇒ 仅限生态根，允许无 `icon_path`（语义根存在、无物理目录；官方资产不可得时的合法状态）
- **禁止伪造**：不得把 A 品牌的图标改名冒充 B（同一图像内容不得服务两个品牌，SHA 唯一性由 CI 拦截）。
- provenance 必须可追溯：官方来源 URL、取得日期、变换链（缩放 / 掩码 / 是否改色）记入 Review Queue、
  审计文档或 commit message。
- 工具脚本：`normalize-icons.py`（规范化）、`normalize-strips.py`（窄条字标裁切 + 底块）、
  `optimize-icons.py`（无损重压缩；**不做有损量化/降色型**）。

## 6. Review Queue（现实世界语义的出口）

- 结构 CI **不能**证明现实世界归属（谁属于谁、是否仍属某公司）。真正需要人工判断的进
  `config/brand-review-queue.json`（`is_ssot: false`，带 `status` / `issue_kinds`）。
- 人工裁决后：先写回 `brands.json`（唯一关系 SSOT），再把队列项置 `RESOLVED` 并附 `resolved_note`。
- 研究/证据（ownership audit 等）只能作为**研究层**保留，**不得**变成第二套关系叙事或自动判定依据。

## 7. Generated Files（单向派生）

```text
SSOT (brands.json + categories.json)
  → resolver (brand_relationships.py)
  → physical path (expected_icon_path)
  → generators
  → derived files
  → CI byte-exact verification
```

- 生成器：`export-brand-relationships.py`、`gen-physical-hierarchy-audit.py`、`generate-category-readmes.sh`、
  `generate-icon-json.sh`、`generate-brand-glossary.py`、`update-readme-badges.py`。
- 派生文件：`config/brand-relationships.json`、`config/surge-icon.json`、
  `docs/references/{brand-glossary,physical-hierarchy-audit}.md`、各级 `README.md`、`config/surge-icon.json`。
- **不得手改生成结果来「修好」CI**：要改就改 SSOT、生成器或校验器。
- 生成器必须**幂等**：连续两轮运行 0 diff，且工作区保持 clean。

## 8. Validation Gates（提交前全绿）

```bash
python3 scripts/ci-validate-icons.py     # 结构一致性（组数随版本增长，以脚本输出为准）
python3 scripts/ci-validate-docs.py      # current-state 文档中的 concrete icon path 必须真实存在
python3 -m unittest discover -s tests -v
git diff --check
# 生成器连跑两轮 → 0 diff
```

- 新增品牌顺序：metadata（`brands.json`）→ `validate-brand.py` → resolver → generator → CI。
- **CI 能证明**：SSOT schema 与唯一性、关系一致性、物理路径、生成物一致、图像规格、
  分类一致性、生态双向阈值、Review Queue schema、文档 concrete path 存在性。
- **CI 不能证明**：现实世界归属、官方资产真实性、交易后的品牌状态、某条 `parent_brand` 是否「应该」存在、
  被删除资产是否有用户价值。
- 结论：既不要把 CI 绿灯当作语义正确，也不要把已知风险自动升级为「必须重构」。

## 9. Documentation Discipline

- 三类文档边界必须明确：
  - **generated**：由生成器重算，CI 逐字节校验（各级 README、glossary、physical audit、导出 JSON）。
  - **manual reference**：人工维护（规范正文 + 人工判断 + **带日期的扫描快照**）；
    **不得伪装成实时生成数据**，实时指标只有一个出口（README「仓库统计口径」，由生成器写入）。
  - **historical / migration**：迁移表与审计快照，**保留旧路径是其职责**，不是错误。
- current-state 文档中的 **concrete icon path 视为公开契约**：用户会直接复制，
  必须真实存在，由 `scripts/ci-validate-docs.py` 校验
  （显式 include 白名单 / exclude 黑名单 + `KNOWN_MISSING` 显式豁免并写理由）。
- 禁止用「段落里出现 Historical 就跳过」这类关键词豁免让 current 文档逃过校验；
  也禁止为了让 CI 通过而删除历史记录。
- 改路径 / 改分类时，文档中的可复制示例必须**同批**修改，不得留到「下次一起改」。
- 文档里的实时统计数字不要多处复述：只引用生成的那一处。

## 10. Common Failure Modes（都真实发生过）

| 失败模式 | 症状 | 正确做法 |
|----------|------|----------|
| stale icon path in docs | 用户复制示例 → 404 | 改路径时同步改文档；`ci-validate-docs.py` 兜底 |
| stale usage example | 上手文档里的配置照抄即失效 | 示例路径属契约，纳入校验 |
| stale metrics | 同一人工文档出现多个互相矛盾的统计 | 实时数字只信生成的那一处；快照必须带日期 |
| generated/manual 混淆 | 人工文档被写进 generated 清单 → 必然腐烂 | 明确身份：generated / manual reference / historical |
| historical 当成 current | 用旧快照数字判断当前状态 | 先读 git + SSOT；快照只作对照 |
| canonical 字段 vs 派生谓词 | 以为字段是权威 | canonical 语义由 `entity_type` 派生；字段仅在特定分支需要 |
| icon_status 双轨 | 以为有字段才 official | 有真实 `icon_path` ⇒ official；字段只在 pending / generated_temporary 有意义 |
| 硬编码品牌特例 | 校验只对某个品牌生效，新生态根不适用 | 按 `entity_type` / 结构条件通用化，不按 ID 特判 |
| 自洽 CI 当现实真相 | 绿灯就宣布语义正确 | 现实归属交人工 + Review Queue；CI 只证明结构 |
| 为下游改事实 | SSOT 被 consumer 反向定义 | 下游差异记为 DOWNSTREAM_STALE，单独同步 |

## 11. PR & Git Discipline

- 默认**分支 + PR**，不直接推 `main`；不 `force push`、不重写历史（除非明确授权并留备份锚点）。
- 提交信息：详细中文 + emoji；变更最小化，**每个 PR 单一目的**（文档纠错 / 校验器 / Skill 不混在一个 PR）。
- **先看 diff 再 commit / push**；staged 内容、脱敏扫描、CI 结果都要确认。
- 大改动分阶段（如先文档纠错，再加防回归校验），每阶段独立可验证。
- 汇报格式：`STATUS / Changed / Verified / Remaining / Commit / PR / Blockers / Out-of-Scope`。

## 12. 先读当前状态（每次工作第一步）

```bash
git fetch origin && git reset --hard origin/main
python3 scripts/ci-validate-icons.py
python3 scripts/ci-validate-docs.py
python3 -m unittest discover -s tests
git ls-files 'icons/**/*.png' | wc -l
python3 -c "import json;d=json.load(open('config/brands.json'));print(len(d['brands']),len(d['parent_brands_without_icon']))"
git log --oneline -5
```

> 这些数字只用于**当次判断**；不要把它们写进长期文档、Skill 或记忆。
> 规范看 `AGENTS.md`（仓库级）+ `docs/references/brand-naming-contract.md`（命名契约）；
> 本文档与它们冲突时，以**仓库当前文件**为准。
