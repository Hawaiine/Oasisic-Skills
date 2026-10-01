---
name: oasisic-icons-maintainer
description: >
  Use when maintaining Hawaiine/Oasisic-Icons (brand icon asset repo): SSOT brands.json /
  categories.json, relationship resolver, physical paths, ecosystem threshold, asset model
  (512×512 RGBA squircle), change-propagation, docs discipline, validation gates, PR workflow.
  Load before adding/renaming/moving brands, changing a spec/relation/category, editing docs,
  or judging "is CI enough". Specialized procedures: references/{intake,rename,ssot-sync,
  audit,spec-change}.md.
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Oasisic-Icons, icons, SSOT, brands-json, resolver, ecosystem, asset-model, change-propagation, docs, ci, github]
    category: github
    related_skills: [static-repo-restructure, logo-render, mihomo-rules-icon-sync, mihomo-icon-cross-repo-sync]
---

# Oasisic-Icons Maintainer

唯一 canonical Oasisic-Icons 维护 Skill。事实在 Oasisic-Icons 仓库，维护知识在 Oasisic-Skills，
本机只是 consumer / cache —— 不在此另存第二份长期手工副本。

## 何时使用
- 新增 / 删除 / 改名 / 移动品牌，调整分类，变更 parent_brand / 关系 / 生态，改规范值
- 处理用户提供的品牌图标（专项流程见 `references/intake.md`）
- 做全库审计（见 `references/audit.md`）、品牌改名（见 `references/rename.md`）、
  SSOT 层同步（见 `references/ssot-sync.md`）、规范值变更（见 `references/spec-change.md`）
- 判断「CI 绿灯是否等于正确」、写 PR、提炼规范

## 1. Repository Identity
- Oasisic-Icons 是**事实 / SSOT** 仓库，独立最高上游，不默认同步第三方图标库。
- 第三方图标库不是自动同步源；下游（consumer）是消费者，**不得反向定义 SSOT 事实**。
- consumer feedback 可以发现问题，但不能直接成为事实来源。
- 每次任务开始先读当前仓库真实状态：`git fetch && git reset --hard origin/main`，跑
  `ci-validate-icons.py` / `ci-validate-docs.py` / `unittest`。不要凭记忆或旧报告（数字会漂移）。

## 2. SSOT
- `config/brands.json` + `config/categories.json` 是唯一事实来源。
- `category`（一级物理分类）与 `parent_brand`（immediate parent）**互相独立**，禁止互相推导。
- Generated artifacts 不得反向成为 SSOT。repo 内事实 = config/*.json + 代码 + git 历史；文档只是派生物或人工参考。

## 3. Naming Model
- `identifier`（品牌 ID，决定目录与文件名）≠ `display_name`（显示名，独立概念）。
- **display_name 变更 ≠ identifier rename**：只改显示名不一定需要移动物理目录；identifier 变更属结构性 rename，必须走第 8 节 Change Propagation。
- 默认命名 `icon_path = icons/<category>/<brand>/<brand>.png`；目录名 / 文件名 / ID 三者一致
  （如 `GitHub/` + `GitHub.png`）；display_name 可另设（如显示名「QQ音乐」）。

## 4. Relationship Model
- `parent_brand` = **immediate brand/product parent**，不等于 ownership / acquisition / developer / provider / platform / hosting / distribution。
- 关系计算一律走 `scripts/brand_relationships.py`（resolve_graph_root / resolve_ecosystem_root / brand_role / expected_icon_path / validate_*）。
- **禁止任何脚本自建第二套关系逻辑**（同一语义只许一个 resolver）——new write 脚本 import 引擎的 root/ancestor helper，不手写 root-walker。
- 环检测靠集合去重与 `seen`（不设 depth 上限魔法数）；self-parent / missing parent / 白名单母公司分别处理；真正无法机器判定的现实歧义进 Review Queue（第 11 节）。
- root 语义：graph root = SSOT 内有条目且 SSOT 内无父；ecosystem root = graph root 且 `entity_type=ecosystem`。两者不混淆。

## 5. Physical Path Model
- 唯一解析器 `expected_icon_path()`。默认 `icons/<category>/<brand>/<brand>.png`；同类中间父递归嵌套
  `icons/<category>/<parent>/<brand>/<brand>.png`；`category == graph root` 时不重复节点目录。
- category 与 parent 属不同一级分类时不机械跨类迁移；无自身图标的 parent 不制造伪目录（语义边留 SSOT，白名单登记）。
- 1 brand = 1 canonical asset（默认文件名无后缀；变体位保留但当前全库未启用）。
- 禁止各脚本（生成器 / audit / rename）自行拼路径；一切跟随 resolver。

## 6. Ecosystem Model（动态）
- 规则只描述：graph root + canonical descendants 达阈值 → 一级生态分类。
- `descendants` 是**整个后代链（含孙代）**；canonical = 项目定义的 product_brand；中间 parent 即使后代多也不自动成为生态。
- 阈值 / 生态清单**永远不写死数量**——每次读取当前仓库并按 resolver 重算；生态数量、CI 组数都以脚本当前输出为准（**任何具体数字都不写进长期文档**）。
- 双向校验：声明 `entity_type=ecosystem` 的生态根必须达标；未达标的 graph root（有白名单母公司或后代不足）不得冒充生态。

## 7. Asset Model
- **512×512 / PNG / RGBA**，圆角矩形 squircle **r≈115**（≈22.4%，Apple 风格），四角 alpha=0，**保留原始底色**（白底必留，不得误杀成透明）。
- 三层次，必须分开讲：**official source asset**（品牌方原始文件，含来源 URL + 取得日期 + 变换链）≠
  **repository asset**（项目规范化落库 PNG：等比缩放 LANCZOS + 容器 alpha 掩码，不是官方逐字节副本）≠
  **recreated artwork**（禁止重绘 / 改色 / 改字形 / 改比例，只做项目规定的容器规范化）。
- `icon_status`：无字段 + 有真实 `icon_path` ⇒ **official**（默认）；`generated_temporary` ⇒ 必须有真实 `icon_path`；
  `pending` ⇒ 仅生态根，允许无 `icon_path`（官方资产不可得的合法临时态，拿到正式资产后同批转 official）。
- 复用仓库共享 normalizer / 掩码（`scripts/normalize-icons.py` 的 `render()`/`rounded_mask()`），不要手搓掩码数学（同一 maths 手搓版会引入角点/抗锯齿漂移）。
- 同一图像内容不得服务两个品牌（CI SHA-256 唯一性拦截）；重压缩走 `optimize-icons.py` 等**无损**路径，不做有损量化/降色。
- 具体处理数字与自检见 `references/intake.md`。

## 8. Change Propagation Protocol（核心规则）
> 任何事实变化，都必须主动寻找所有依赖该事实的位置，逐项判断：同步修改 / 自动生成 / 历史保留 / 迁移保留 / 测试更新 / 误命中。禁止局部修改后宣布完成；禁止无脑全文替换；禁止删除历史。

适用：brand rename、display-name change、brand ID change、category move、parent_brand change、ecosystem 关系变化、icon path migration、asset 规范变化、naming 规范变化、spec 变化、Skill rename。

流程：
```
changed source → dependency discovery → impact classification → synchronized changes
              → regeneration → old-value residue scan → validation
```

### 8.1 变更前：Impact Matrix
先记录 `Old value / New value / Change type / Authoritative source`，再搜索**至少**：
`old/new identifier、old/new display name、old/new directory、old/new filename、old/new icon_path、
old/new category、old/new parent_brand、old/new URL`（对应搜索词全部跑一遍）。

把每个命中分类为：`CURRENT-SSOT / GENERATED / CURRENT-DOC / TEST / SCRIPT / HISTORICAL /
MIGRATION / LEGACY / CONSUMER / FALSE-POSITIVE`。不同类别处理方式不同，**禁止**在分类前
`s/OLD/NEW/g`。

### 8.2 Brand Rename 全链路同步清单
检查：SSOT ID / display_name / brand directory / canonical icon filename / icon_path /
parent relationship / relationship export / surge-icon.json / glossary / category README /
parent README / root README / tests / fixtures / current docs / migration docs / legacy map /
consumer references。并确保 `old current SSOT ID = 0、old current directory = 0、
old current filename = 0、old current icon_path = 0`；而 historical old name / migration old
name / legacy old identifier 可合法保留。

### 8.3 各类传播
- **Physical rename**（identifier 变）：SSOT → icon_path → directory → filename → generated →
  docs → tests 全链路，禁止只改 `brands.json` 或只 `mv` 目录。
- **Case-only rename**（`Foo→foo`）：额外查 filesystem 大小写敏感度、Git index、临时两步改名
  `Foo→tmp→foo`、旧路径残留、重复 casing。
- **Relation change**（parent_brand 变）：重查 ancestor_chain / graph root / ecosystem root /
  physical hierarchy / category 派生 / relationship export / parent & child README —— parent 变化
  可能改 physical path、ecosystem membership、ancestor depth、category，不能只改一个字段。
- **Category change**：查 brands.json / categories.json / physical dir / icon_path / category
  README / root README / glossary / generated paths / tests / docs。禁止只动目录不更新 SSOT，
  也禁止只改 SSOT 而不让 resolver/generators 传播。
- **Spec change**（radius/dimensions/alpha/container/PNG mode 等）：spec → affected scripts →
  affected generators → affected tests → affected docs → affected existing assets → CI，不能只改规范文本。
- **display-name change**：identifier 不变则走轻量路径；但 glossary / README 表格 / generated 里的
  display_name 仍要同步（本仓库部分生成结果以 display_name 为键）。

### 8.4 变更后：Old-Value Residue Audit
变量后再次搜索全部 old value。不要只要求 `grep = 0`——逐项分类，目标 **`CURRENT old-value residue = 0`**；
Historical / Migration / Legacy / Consumer 允许有明确保留项。

### 8.5 Acceptance Table（每次 rename/move/relation/spec change 后报告）
```
Source of truth / Change type / Old value / New value
SSOT / Resolver / Directory / Filename / icon_path
Generated artifacts / Documentation / Tests
Historical / Migration / Legacy / Consumer
Old current references: 0
Regeneration: PASS   Tests: PASS   CI: PASS   Working tree: CLEAN
```
> 专项程序与应用模板见 `references/rename.md`。

## 9. Documentation Model
三类文档边界必须清楚，且**不得互为第二真相**：
- **generated**：由生成器重算，CI 逐字节校验，禁止手改。结果错就修 SSOT / resolver / generator。
- **manual reference**：人工维护，scan snapshot 必须带日期，不得伪装实时生成数据，不与 generated 清单混淆。
- **historical / migration**：保留旧路径是其职责，不是错误。
- **rule**：current-state 文档里的 concrete icon path（`icons/<…>/<file>.png`）是**可验证的公开契约**——
  用户复制即用。path 不存在 ⇒ **修文档**，绝不加永久 exception。历史 / 迁移旧路径只能存在于显式
  exclude 范围（`docs/migrations/**`、`upstream-history.md`、`brand-migration.md`、
  `category-migration.md`、`brand-ownership-audit.md`）；绝不靠「看到 Historical 就跳过」关键词绕过。
  `ci-validate-docs.py` 是「文档 → 抽 concrete path → 文件系统存在性」纯链，**无豁免清单**。

## 10. Generated Files
链：`SSOT → resolver → generators → derived → CI`。生成器（export-brand-relationships /
gen-physical-hierarchy-audit / generate-category-readmes / generate-icon-json /
generate-brand-glossary / update-readme-badges 等）必须**幂等**（连续两轮 0 diff）。
任何 derived artifact：不手改、不作为第二真相、修源头而不是修产物。

## 11. Review Queue / Semantic Boundary
- **CI green ≠ 现实世界语义正确**。ownership / JV / acquisition / corporate restructuring /
  brand hierarchy 这类现实归属若不能可靠计算 → 进 `config/brand-review-queue.json`
  （`is_ssot: false`），人工裁决后写回 SSOT，再把队列项置 RESOLVED（附 resolved_note）。
- evidence（审计文档等）只是研究层，**不得成为第二关系真相**；所有权 ≠ 层级，只有
  BRAND_HIERARCHY_CONFIRMED 级证据能判定 parent_brand。

## 12. Validation
- 提交前全绿：`ci-validate-icons.py`（组数以脚本输出为准）＋ `ci-validate-docs.py` ＋
  `python -m unittest discover -s tests` ＋ `git diff --check`；生成器幂等两轮 0 diff；工作区 clean；分支 + PR。
- CI 只证明结构一致性（SSOT schema、关系、物理路径、生成物一致、图像规范、唯一性、生态双向阈值、
  Review Queue schema、文档 concrete path）；不能证明现实归属正确 / 官方资产真实 / 被删资产是否有用户价值。
- 别把 CI 绿灯当语义正确，也别把「无法自动化」当必须重构。
- 变更模型后除跑 validator 外**必须跑全套 unittest**（模型变化会打破 pinned 测试语义而非 validator——同 commit 迁移 assertion，不删除测试）。

## 13. Standard Workflows（专项入口）
- 图片入库 → `references/intake.md`（512 RGBA r=115 处理、置名、批推纪律、回读校验、坑）
- 品牌改名 / 移动 / 关系变化 → `references/rename.md`（含 Change Propagation 应用与 acceptance）
- SSOT 层同步（白名单 / 根图标 / surge-icon 数组 / glossary）→ `references/ssot-sync.md`
- 全库审计（数值重算、PNG↔JSON parity、体积异常、生态规则 v2、ownership 分类、CI 组数、迁移机制、no-second-SSOT）→ `references/audit.md`
- 规范值传播（几何 / 命名 / 规范契约变更）→ `references/spec-change.md`

## 14. Common Failure Modes
- 文档 concrete path 失效（复制即 404）；同一文件多个统计口径；generated/manual 身份混淆 → 必然腐烂。
- 历史信息被当 current state（快照 / 迁移表 / 审计文档）；字段与派生 predicate 双轨（canonical 由
  entity_type 决定、有 icon_path ⇒ official）；对品牌 ID 而非通用条件硬编码特例。
- 自洽 CI ≠ 现实正确；在仓库里为下游改事实 / 让下游反向定义 SSOT；generated 被手改。
- 数字携带不重算；在多个文档重复复述实时数字（只信 README「仓库统计口径」生成行）。

## 15. Git / PR Discipline
- 默认 branch → commit → push branch → PR → review → merge；**不直接推 main，不 force push 旧历史**。
- 提交信息用详细中文 + emoji；变更最小化，单 PR 单一目的；含改名/迁移的分阶段 PR。
- diff 先确认再提交；仓库内旧知识先提炼再谈删除；汇报格式 STATUS / Changed / Verified / Remaining / Commit / PR / Blockers / Out-of-Scope。
- Skill 本身同样遵守 Change Propagation：目录名 == SKILL.md frontmatter.name == meta.yaml.name
  （Oasisic-Skills 用 `scripts/validate-skill-identity.py` 强制）；SKILL.md 是固定入口文件名，不得改名。