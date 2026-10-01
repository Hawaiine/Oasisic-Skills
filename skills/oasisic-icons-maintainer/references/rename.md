# Rename — 品牌标识符 rename 全链路与 Change Propagation

专项流程：改名/归一化 Oasisic-Icons 品牌 identifier（目录 + 默认 PNG + 变体 PNG）并同步每一个引用。
这是核心 SKILL.md 第 8 节 **Change Propagation Protocol** 的落地模板：改名不是一次 `git mv`，
是「改动 → 依赖发现 → 影响分类 → 同步 → 重生成 → 旧值残留扫描 → 校验」的完整审计。

每次执行前先读当前仓库真实状态；`config/brands.json` 里的 `id` / `icon_path` 与 `parent_brand` 指向
必须与 filesystem rename 放在**同一个 commit**。

## 两层模型（动手前先定）
- **Display 层**：官方/真实品牌名（如 `discovery+`、`哔哩哔哩`），只进 glossary 显示列与 README 显示名；
  绝不破坏官方 stylization（`discovery+` 不得变成 `discovery plus`）。
- **Identifier 层**：文件系统/JSON 名，遵守仓库 README 命名规则（如 `+`→`Plus` 大写，先例 DisneyPlus/ParamountPlus/AppleFitnessPlus）。
- 仓库证据与请求冲突时**停下报告**（规则行 + 既有先例品牌），让用户裁决——这是唯一允许故意阻塞的点。
- 官方名以 wiki/help center 核实；identifier 以 README 规则 + 先例核实，不凭记忆。

## Impact Matrix（改名专用，需要搜索的旧值）
在动手前建立 `Old value / New value / Change type / Authoritative source`，然后跑这些搜索词，逐命中分类：
`old/new identifier、display name、directory、filename、icon_path、category、parent_brand、URL`。
分类标签：`CURRENT-SSOT / GENERATED / CURRENT-DOC / TEST / SCRIPT / HISTORICAL / MIGRATION / LEGACY / CONSUMER / FALSE-POSITIVE`。
**禁止在分类前做无脑全文替换（sed `s/OLD/NEW/g`）**——同一旧值会在 SSOT、generated、tests、docs、
history、migration、legacy map、examples、comments、consumers 里出现，处理各不相同。

## 同步清单（identifier rename 全链路）
- SSOT：`brands.json` 的 `id` / `icon_path` / 可能的 `display_name`；指向旧 id 的 `parent_brand` 全部更新。
- 物理：目录 + 默认 PNG + 变体 PNG 一起 `git mv`。
- generated：`generate-icon-json.sh`、`generate-category-readmes.sh`、`generate-brand-glossary.py`（或手维护 glossary）、`update-readme-badges.py`。
- docs：current docs 里的可复制路径、`brand-naming-contract.md`（改名在此登记）。
- tests：grep 整个 test 树更新旧 id/display 断言，**不删除**（大小写/存在性检查继续对新名生效）。
- 保留：migration docs、历史快照里的旧名合法保留；legacy map/consumer 仅做只读 blast-radius 量化。
- 目标：`old current SSOT ID = 0、old current directory = 0、old current filename = 0、old current icon_path = 0`；
  而 historical/migration/legacy 的旧名可保留。

## 流程（步骤）
1. 确认 clean 工作树 + PR 分支（绝不 main）。
2. `git mv` 目录与每个 PNG（先 `mkdir -p` 目标）。`git diff --name-status` 应为 **`R100` 纯改名**
   （内容哈希不变）；若显示 delete+add 说明你改了字节。
3. 重生成派生文件，**采纳生成器而不是手改**：`cp surge-icon.json /tmp/before.json && bash generate-icon-json.sh && diff`。
   生成器是 JSON 与分类 README 的真值；改名后手工插入的行排序被重排是**正确**的 diff，采纳它，别交手排文件。
4. Glossary（`docs/references/brand-glossary.md`，手维护）：改该行（目录列→新 identifier，显示列→官方名）并放对排序位。
5. 顶层 README 表：只改 identifier 单元格。
6. 变体重编号（`X02→X01`）：先查 git 历史——默认 `<Brand>.png` 从未叫 `01`，所以单变体降号安全且必要；**绝不改名/删除默认图标**。
7. 校验（全过才算）：`ci-validate-icons.py`；对每个 rename 做**图像层**证据而非只看 git 的 R100——
   `sha256(新文件) == sha256(git show HEAD:<旧路径>)`，且 Pillow 检查每个改名 PNG（512×512/RGBA/角 alpha=0）；
   `surge-icon.json` 每个 `url` 都在磁盘存在、无旧 id 作为 JSON `name`、`(category,name)` 有序、条数==PNG 数；
   `git diff --check`；生成器幂等（JSON 与分类 README 各两轮 0 diff）；`git grep -n '<OldName>'` 只剩研究类文档
   （`icon-research.md` 等记录 provenance 的，保留）；glossary 行数与磁盘品牌目录数双向 set diff 为空。
8. 每个逻辑变化单独 commit（默认图标重编号 ≠ 品牌改名 ≠ doc 同步）。
9. push + PR；PR body 带改名表 + 证据 + blast-radius（见下）；CI 的 push 与 pull_request 两 run 都要 success。

## PR body（阶段报告规范）
带：改名表（旧路径→新路径 + 每行一条官方品牌证据）；三层命名决策（官方名 / 显示名 / 技术 identifier，引用先例）；
同步范围 + 生成器幂等证据（两轮 0 diff）；完整校验清单；consumer 影响计数；「未改 / out of scope」清单；
后续阶段待办。末尾给出 baseline SHA、commit SHA、PR URL、CI 状态、「waiting for review」。

## Consumer blast radius（只读，merge 前）
不改 consumer 仓库；只读量化：grep consumer 的配置文件（mihomo-rules 等）里每个旧 identifier 路径，
数会被 404 的引用（默认 vs 变体——重编号的变体可能零影响），把数量 + 受影响文件写进 PR body，
并标注顺序风险：icon PR 先合而 consumer 后同步会有一段死链期。

## 坑
- **glossary 大小写敏感 ASCII 排序**（全表整体，非分字母节）：`AD/AWS/BBC` 在 `AbemaTV` 前，`bilibili/discoveryPlus/iCloud`
  沉到节尾。插入前用代码复现既有顺序，手插到「明显字母位」是错的。
- **rebase/cherry-pick 混入改名 commit 后陈旧行会存活**：新旧行并存、计数膨过磁盘数。每次 rebase/cherry-pick 后
  重查 glossary 唯一性 + 行数 == 磁盘数，删陈旧行并 `--amend` 进改名 commit。
- **`&&` 链会掩盖副作用**：`git checkout -- file && grep -c pat file`——`grep -c` 零命中 rc=1 会中断链，但 checkout 已先跑了。
  还原与检查分开写，任何意外重查状态。
- **分支攒了别的 PR 的提交**：重建——base 到 `origin/main`，只 cherry-pick 本 PR 的 commit，同名单远程分支用
  `--force-with-lease`（分支内容变，PR 自身历史不重写）。
- **不要为了 push 而造空 commit**：分支已满足裁决结果就报状态 + 全量校验并停。
- **Case-only rename（`Bilibili→bilibili`）**：先查 filesystem 大小写敏感度——ext4 上 `git mv` 是干净 R100；
  大小写不敏感卷上新旧名冲突，要走临时名 `X→x_tmp→x`。

## 与 SSOT 层的关系
本流程覆盖 identifier + 全引用同步；`brands.json` 的增删/白名单/根图标联动见 `references/ssot-sync.md`。
若改名伴随 `+` 品牌、跨分类、或某品牌从无图标变为有根图标，先读对应 reference 再动手。