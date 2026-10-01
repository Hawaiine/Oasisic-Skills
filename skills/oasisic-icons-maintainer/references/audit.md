# Oasisic-Icons 审计操作参考（audit）

> 本文件是 canonical `oasisic-icons-maintainer` Skill 的**专项审计流程**补充。
> SSOT 结构、关系模型、物理路径、资产规范、通用 PR 纪律以 `SKILL.md` 为准；这里只回答三件事：
> **审计怎么做、每条命中怎么分类、哪些坑在本仓库真实存在过**。
> 本文件**不携带任何仓库快照**（数量、组数、commit、日期统计）。文中出现的数字一律是**规则常量或几何常量**（如阈值 `≥2`、`512×512`、`r≈115`）；一切**计数类数字必须在现场重算**。

---

## 0. 前置：先读当前仓库真实状态（每次审计第一步）

审计报告、迁移文档、旧 Skill、上一次会话的结论**都不是真相**。动手前按顺序重建现场：

```bash
git fetch origin && git reset --hard origin/main
git ls-files 'icons/**/*.png' | wc -l                 # 磁盘真实资产
python3 -c "import json;d=json.load(open('config/brands.json'));print(len(d['brands']),len(d['parent_brands_without_icon']))"
python3 scripts/ci-validate-icons.py                  # 组数从本行输出读取，不写死
python3 scripts/ci-validate-docs.py
python3 -m unittest discover -s tests -v
git diff --check
git log --oneline -n <N>
```

- **组数、生态数、PNG 数、canonical 数全部从上面命令的输出读取**，不得从本文件、旧报告或记忆里取值。
- 校验器输出的 `Validation Groups: N / All groups: PASS` 是唯一权威；N 随版本增长，禁止在脚本、文档、PR 正文里写死。
- 先确认工作树干净、`main` 未被污染，再开始任何写操作。

---

## 1. 审计不变式（违反则结论无效）

1. **数字重算，不携带。** 每条结论的计数都必须从当前工作树/`git show HEAD:<path>` 重算；旧草稿数字会在 revert 后存活并写进已发布文本。
2. **stale 文本先定位来源，再决定改不改。** 用户报告「当前状态矛盾」（旧计数、被取代的状态、已删除的段落「仍然存在」）时，**不要**直接 re-grep 工作树开始重写：先 `git show HEAD:<path>` 确认 HEAD 的真实内容，再用 `git show <candidate>:<path>` 在近期 commit 里定位那段文字。
3. **逐条命中分类，不做 zeros-hit 庆祝。** 语义 stale 扫描的每个命中都要打标签：`CURRENT_STALE` / `HISTORICAL_OK` / `CODE_OK` / `FALSE_POSITIVE`。零命中不等于干净，可能是扫描正则根本没匹配到。
4. **打标签而非静默重写。** 逐项给出「在 HEAD 不存在 / 文字属于 commit X / 已由 commit Y 修复」式结论，不要把本来正确的文件再「修」一遍。
5. **带日期的审计头必须显式标注快照身份。** 仍引用旧总量的历史审计文档，头部要写明它是历史快照（`Historical snapshot`），否则会被读成当前状态。注意子串假阳性（例如把「…收购…生态」误配成「`16.*生态`」这类模式）。
6. **历史文档不「顺手修正成当前」。** `docs/migrations/**`、`upstream-history.md`、`brand-migration.md`、`category-migration.md`、`brand-ownership-audit.md` 里保留旧路径/旧数量是**它们的职责**，不是错误。

---

## 2. 文件真实性与格式

### 2.1 伪 PNG（magic bytes）

下载被限流时可能把 HTML 错误页存成 `.png`。判定以**文件头**为准，不以扩展名：

```bash
# 任一：不是 PNG magic(89504e47) 即标记（注意 HTML 错误页 head 常以 "404:" 起）
find . -name '*.png' ! -exec sh -c 'head -c 4 "$1" | od -An -tx1 | tr -d " " | grep -q 89504e47' _ {} \; -print
```

- 删除伪文件时**两侧同步**：磁盘 PNG 与它对应的派生清单条目一起清（见 §3）。
- **magic bytes + 文件大小不足以证明可解码**：CI 必须用 Pillow 真实 `load()`/`getpixel`（见 §4.1），一个从不安装依赖的「硬化解码器」只会在 CI 上失败，不在本地暴露。
  - Pillow 小坑：`load()` 在运行时返回 `self`，但 Pyright 会把函数体内的 `im` 模块判为 out-of-scope——对已加载图像用 `getpixel` 并加显式 `# type: ignore`，别去和类型检查器较劲。

### 2.2 尺寸 / 模式规范化

- 基线几何：**`512×512` / RGBA / squircle 圆角 `r≈115`（≈22.4% of 512）/ 四角 `alpha==0` / 保留原始底色**（`r≈99` 是早期约定，已废弃，勿再写有效）。
- 规范化脚本必须**幂等**：`size==512×512 且 mode==RGBA 且角点 alpha==0` 视为已合规、不动（保护用户手工更新的图标；在脚本 docstring 与 commit body 里写明这条跳过规则）。
- 非正方形源：**先补成正方形再缩放**——用最外不透明环的中位色补边（环透明则补透明）；**绝不删背景**（白底保持白底，只有四角变透明）。
- 圆角遮罩：`alpha *= rounded_rect_mask(512, r=115)`，LANCZOS 缩放。
- **严格 RGBA**：全库 PNG 必须 `mode==RGBA`；无损重压缩时传 `color_type_reduction=False`，否则会被降成等价的调色板/灰度色型（无损但字面不一致）。
- **不做有损量化**：不引入 pngquant/降色型（不可逆的像素改动）；体积指标用「单文件上限 + 平均值」口径，不追极端压缩。
- 压缩用 pyoxipng（`pip install pyoxipng`，无需系统二进制；可 `--target` 装到临时目录 + `PYTHONPATH`）。

### 2.3 窄条字标（wordmark strip）

- 极端宽高比（>`~1.8`）的窄条字标直接居中会在方图里几乎不可读：**先裁到内容 bbox**，再放到一块**不透明圆角底块**上。
- 底块填充色 = 内容主色（该主色偏亮时加深），否则白色；**当 logo 位于透明背景时，绝不能用 logo 自身主色做底色**——文字会融进自己的颜色。
- 处理脚本与规则同步记录到资产规范文档，勿只改图不改规范。

### 2.4 稳定排序与去重

- 生成器输出必须确定性：排序键固定为 **`(category, name)` 元组**（`name` = 无扩展名的 stem；category = 目录名）。按完整相对路径或按文件名字母序都会得到不同结果。
- 验证：跑生成器前后 `diff` 必须为空；**生成器连跑两轮 0 diff** 且工作区保持 clean。
- 默认图必须唯一：`<Brand>.png` 不得与任何变体同内容；同内容时**删重复变体并顺延编号**（不要删默认图、也不要把默认换成别的变体），顺延后全库做一次 SHA-256 去重校验（零碰撞）。

### 2.5 体积异常扫描

- 对全库做一次体积/尺寸异常扫描，把异常（非 `512×512`、异常偏大/偏小的单文件）列成清单写入参考文档，供人工复核；清单属于**人工参考**，不得伪装成实时生成数据。

---

## 3. PNG ↔ 派生文件一致性（双向）

### 3.1 磁盘 ↔ SSOT ↔ Surge JSON

- **双向对账**：Surge 条目的 ID 集合 == manifest ID 集合，且逐条 `name`/`category`/`URL` 匹配（只比数量会漏掉「替换了条目」这类漂移）。
- 对账口径统一：比对前先把两侧路径归一化到同一相对形式（`icons/` 前缀**只加一侧**会静默全错）。

**实测文件形状（写断言前先读真实结构）：**

- `surge-icon.json` 的 `icons` 是**数组**——重复检测要在 entry/`name` 层级做，不能当 dict key 查。
- `brand-glossary.md` 是 **markdown 表**——任何逐行正则必须跳过 `|---|` 分隔行，否则每一条分隔行都是一个「幻影重复」。
- 手工写的断言若按错误形状写，第一次运行就挂，白烧一个 debug 周期。

### 3.2 Glossary 显示名

- 对账：glossary 每行 `| Technical ID | Display Name |` 与技术 ID 全量（`icons` 二层目录）对比，断言数量相等、缺失/多余/重复为空、各分区内 `sorted()`（Python 默认大小写敏感序，即仓库既有排序约定）。
- glossary 检查必须同时校验 **ID 集合**与**逐条 display_name 映射**；只查 ID 会漏掉显示名漂移。
- Display 列**不重复英文 ID**（`Technical ID | Display Name` 两列结构）；品牌真实性优先 ≠ 机械复制英文名。只对有明确证据的条目动手，勿全表重写。

### 3.3 README 一致性

- README 中每一处**硬编码汇总数字**（badges、导语里的「N 个活跃分类」等）都要与 SSOT/文件系统核对并以漂移为 FAIL；**预防**：由 badge/updater 脚本每轮**动态写入**这些行，绝不手打。
- 「仓库统计口径」只有**一个出口**（README 的 metrics 行，多个具名字段由生成器 `ssot_metrics()` 产出，CI 逐字段重算）。任何文档引用数字都必须映射到其中一个具名字段——**禁止模糊的「brands = N」**（它会把 SSOT 条目数与 PNG 数混为一谈）。
- README 分类表按**整体重建**（表头 + 分隔行 + 全部数据行 + 合计），先补回小节标题再插表；逐行 patch 会丢行、吞标题。重建后重跑生成器让 badges/计数跟上。
- README 覆盖度：目录结构里的所有分类、生成器脚本（含用法）、`scripts/` 下所有 `.sh` 的脚本表、相关项目链接。
- 生态计数句（「当前 N 个」）与生态根资产状态句（`icon_status` + `icon_path`，带 `（generated）`）同样是**生成**的，避免 `pending → official` 转换后残留旧文案。
- repo topics 用于可发现性：图标类仓库的典型 topics 为 `icons` + 工具名（如 `surge`/`clash`/`mihomo`）+ `proxy` + 对应客户端名；设置后核对回读。

---

## 4. CI 校验面

### 4.1 校验器覆盖（按**名字**描述，不按固定序号）

- **PNG 真实解码**：Pillow `load()` + `getpixel`（magic bytes/文件大小不算）。
- **规格**：`512×512`、RGBA、四角 `alpha==0` 的**像素级**检查。
- **分类一致性**：`categories.json` 定义 == 磁盘目录 == README 分类表，三者相等；分类目录 ⊆ 白名单，且每个 active 分类都在磁盘存在。
- **reserved 与磁盘不得矛盾**：reserved 分类若实际含品牌或 PNG 即 FAIL（reserved = 0 brands、0 PNGs）。
- **canonical 唯一性**（跨分类）、**SHA-256 零碰撞**。
- **物理路径**：manifest `icon_path` 必须**逐字节等于 resolver 的 `expected_icon_path()` 输出**——没有任何手工编辑能满足此组，resolver 是唯一写者。
- **关系完整性**：`parent_brand` 存在、非 self、无环（用访问集合而非 magic depth）。
- **白名单纯净**：`parent_brands_without_icon` 中若含「已有图标」的品牌即 FAIL。
- **生态一致性（双向）**：forward `entity_type=ecosystem ⇒ 达到阈值`；reverse「有 manifest 条目且达阈值的 graph root ⇒ 必须 `entity_type=ecosystem`」——**reverse 才是防绕过的那一道**，forward-only 是平凡可绕的。reverse 门**必须豁免白名单母公司**（它们按定义没有 manifest 条目/图标，不豁免则每个白名单母公司都是假 FAIL）。
- **漏标拦截**：位于生态目录内的**非根**品牌必须声明 `parent_brand = 该目录`。
- **README 表结构**、**README stats**、**parent README 字节一致**（见 §6）。
- **关系派生导出**字节级重算比对，并断言其**不是第二 SSOT**。
- **Review Queue** schema 校验，并断言 `is_ssot: false`。
- **legacy 路径扫描**（见 §7）。

### 4.2 docs 校验器：**无豁免机制**

- `ci-validate-docs.py` 是一条**纯链**：current/normative 文档 → 提取 concrete `icons/.../*.png` 路径 → 路径必须在磁盘真实存在。
- **绝不添加 `KNOWN_MISSING` / allowlist / exception 映射**。伪 concrete 示例（被禁的反例路径、抽象嵌套示例）要**改写成正则不匹配的形式**：目录形式（`icons/<Cat>/<Brand>/`）或占位符形式（`icons/<category>/<a>/<b>/<brand>/<brand>.png`），语义保留。
- 必须保留在文本里的旧路径**只能存在于显式 exclude 清单**（`docs/migrations/**`、`upstream-history.md`、`brand-migration.md`、`category-migration.md`、`brand-ownership-audit.md`）。
- **禁止关键词豁免**：current 文档里出现 `Historical` / `Legacy` 字样**不构成豁免**；被豁免的唯一含义是「位于被排除的路径内」。
- 该校验器**不 import brands/categories SSOT** 是设计正确（有测试断言不存在第二真相源）。
- 每个改动都要带**变异测试**：向被 include 的文档注入一个不存在的 concrete 路径 → 应带行号 FAIL；恢复 → PASS。

### 4.3 legacy 扫描实现要点

- **自命中**：一个检查「无活跃文件引用已删除路径」的扫描器会命中**它自己的模式表**。用两个变量的字符串拼接构造模式字面量，保证完整可匹配串从不出现在源码里。
- **跳过字节码/二进制**：跳过带 `__pycache__` 段的路径、二进制/字节码后缀、以及前 1 KB 含 NUL 的文件。此 bug 本地会隐藏（无缓存文件），CI 上失败——**本地绿也要在干净 clone 上复现 CI 步骤**。
- `.gitignore` 里加上 `__pycache__` 与 `*.pyc`（CI 运行会产生未跟踪缓存）。
- **canonical ≠ legacy**：某个品牌 ID 回归 canonical 后必须从 legacy 表移除；当旧目录名等于当前 canonical 路径段时，登记**完整旧前缀**（如 `icons/xAI/`）而不是 `/<segment>/` 通配。加一条测试断言 legacy 模式不匹配任何当前 `icon_path`。
- **legacy 映射单源**：旧名映射只放**一个模块**，供 CI legacy 扫描与测试共同消费；映射复制到两处必然漂移，新 legacy 名字只能加在一个地方。
- legacy 扫描豁免 `docs/migrations/`（历史记录合法引用旧名），只在活跃文件里计数。

---

## 5. 关系与生态审计

### 5.1 拓扑定义

```text
graph root      = SSOT 内有条目 且 SSOT 内无父
ecosystem root  = graph root 且 entity_type = ecosystem
阈值            = canonical descendants（product_brand 后代，含孙代）达到 resolver 规定的阈值
```

- **graph root ≠ ecosystem root**：`resolve_graph_root()` 只做纯拓扑（最顶节点）；`resolve_ecosystem_root()` 仅当该顶节点是 `entity_type=ecosystem` 才返回，否则 `None`。
- 未达阈值的顶节点是 **Graph Root Parent**：不建生态目录，但仍是**物理父节点**，必须有自己的 parent README。
- 阈值**只作用于 graph roots**：已有生态根之下的中间层节点，即使后代很多也**不得**升格为新一级分类（防分类爆炸）。
- 统计谓词只数 **canonical（`product_brand`）后代**（唯一 predicate，如 `is_canonical_brand()`）；`country`/`system_icon`/`tool_app`/`ecosystem` 实体不计入阈值，否则非品牌会虚增计数、静默造出/伪造生态。
- **parent entity_type 门**：`parent_brand` 指向非 canonical（country/system_icon/tool_app 或任何非产品类型）即 FAIL；parent 节点必须是 `product_brand` 或 `ecosystem`。
- **不维护生态清单**：生态数量永远从 manifest 子节点计数动态派生，禁止在脚本/文档/文案里硬编码「几个生态」。
- **单 resolver 规则**：任何需要根/祖先遍历的比较或消费脚本，都必须 import 关系引擎的 `resolve_graph_root()` / ancestor 帮助函数。第二套手写 root-walker 会与引擎拓扑静默分叉，且需永久同步——这条规则就是为防这个 dual-parser 缺陷而设。
- **单一 SSOT**：关系事实只有 `brands.json` 一处；导出文件里的同名键只是镜像。有测试断言不存在第二真相源。

### 5.2 生态迁移与目录

- **≥阈值 的 parent（含孙代口径）必须拥有一级目录** `icons/<Parent>/`，子品牌迁入并把 `parent_brand` 保留、`category` 指向父品牌；子树根条目标 `entity_type=ecosystem` 且 `category: self`。未达阈值的 parent 照记 `parent_brand`，留在功能分类。
- 迁移必须 `git mv` + **前后逐字节 SHA 校验**（`git show HEAD:<old> | sha256sum` vs `sha256sum <new>`），呈现为 `R100`。
- **`icon_path` 必须同步**改成 `icons/<category>/<id>/<id>.png`；只改 `category` 不改 `icon_path` 会直接 CI 失败。
- **空目录陷阱**：`git mv` 会在旧品牌目录留下空壳，CI 的 Naming/Canonical 唯一性会把它当作「另一分类里的同品牌」报重复。迁移后扫描并删除空目录（`find icons -mindepth 2 -maxdepth 2 -type d -empty`）。
- **变体一起迁**：迁品牌目录前先迁**它全部 PNG**，含编号变体；留下变体会搁浅文件并破坏 SHA-256 / parity 检查。
- 生成器按**磁盘目录**数品牌：残留的**空目录会虚增品牌数**（并丢 README 行）。任何迁移后删除腾空目录，并断言「磁盘品牌目录数 == manifest 品牌数」。
- 迁移前的决策必须来自**当前 manifest 的全量 parent 扫描表**（子数、root 图标有无、当前 category、entity_type、是否已有专属目录），逐一判定，不能沿用旧的结论。

### 5.3 `pending` 生态根：临时态

- **无自身图标的生态根**登记为白名单 `parent_brands_without_icon`（白名单只用于**根本没有 manifest 条目**的 parent），**绝不伪造图标**。
- 合法的一等公民形态：`entity_type: ecosystem` + 有 manifest 条目 + `icon_status: pending` + **无 `icon_path`**。这是**过渡态**：一旦官方素材到手，同一批改动里把 `icon_status` 改成 `official` + 写入真实 `icon_path`，并把 Review Queue 项置 `RESOLVED` 附 `resolved_note`（缺 note 会被 CI 判 FAIL）。
- `resolve_ecosystem_root()` 需要一个正式的 `entity_type=ecosystem` SSOT 节点；`icon_status=pending` **不取消**生态身份，子节点仍能解析到根。「有生态目录但 manifest 无根节点」是**遗留形态**——迁移它，不要两套模型并存。
- 资产模型必须显式且带变异测试：`pending`（仅生态）**允许**缺 `icon_path` → `expected_icon_path()` 返回 None、物理校验跳过、不产 Surge URL；`generated_temporary` **必须**有真实 `icon_path`（不得套用 pending 豁免）；其它任何 entity_type 缺 `icon_path` 即 FAIL（无静默通过）。测试要证明 pending 豁免**不能**被其它状态复用。
- 节点一旦转正式，所有仍写「root 条目/root 图标 pending，登记在白名单」的文档立刻陈旧：全树 grep（README、命名契约、迁移文档、审计文档、生成的关系导出 note 字段、测试 docstring）**一次改完**；生成导出的 `note` 字段最容易漏。

### 5.4 撤销迁移 / revert

- 若生态目录迁移被用户反转：`git reset --mixed` 会让 index 与磁盘失同步，之后 `git mv` 报 No such file。用 `git checkout <ref> -- <paths>` 还原原路径，`git diff` 确认零残留再提交 revert。
- 从旧 ref 恢复文件时（`git checkout <ref> -- file`），**该 ref 之后新增的字段**（如后续 commit 追加的 `parent_brand`）会静默丢失：把字段按 old-ref vs new-ref diff 一遍，回填 revert 丢掉的内容。

---

## 6. 生成器与 parent README

- **生成器幂等**：连跑两轮 0 diff，工作区 clean。
- **parent README 字节一致**：生成的 parent README 必须与 `expected_parent_readme()` **逐字节相同**，用**全库动态遍历**校验（禁止硬编码名字清单——新 parent 节点必须在零测试改动下被捕获）；手写 README 只做最小结构检查。
- **marker 必须指向真实生成器入口**：生成的 README 带自动生成 marker，marker 若指向幻影/陈旧脚本，生成器会把该 README 当作手写并**静默跳过重生成**。声称「全部已重生成」前先核验 marker 串，并**一次成批**迁移所有陈旧 marker（用 Python walk，不要用递归 grep——grep 在大树上会卡）。
- **角色标签三态**：Ecosystem Root / **Graph Root Parent** / Intermediate Parent Brand——未达阈值的顶节点**绝不能**标成 intermediate。**每个有 ≥1 子节点的物理父节点都必须有 parent README**（生态根 + 非生态 graph root + 中间父品牌），不只是生态根。
- 关系模型变更后**重新生成全部 parent README**，再跑字节一致 CI 组证明仓库与生成器一致。
- 生成物永远不手改来「修好」CI：要改就改 SSOT、生成器或校验器。
- `git mv` **不会创建目标目录**（`NewDir` 不存在时直接失败）：先 `mkdir -p`。
- `json.dump` 写出的文件**已带一个 `\n`**；再手工追加会变成双换行，`git diff --check` 报「new blank line at EOF」。用 `s.rstrip('\n')+'\n'` 归一化。

---

## 7. 归属与关系分类边界（ownership ≠ parent_brand）

- **企业持股 ≠ 品牌直接父级**。股权/合并事实属于**审计证据层**（commit message、审计文档），**绝不进 `parent_brand` 树**。判定 parent 以**品牌身份**为依据（官方产品列表、官方 ToS/隐私政策声明「两家公司独立运营」），而不是「谁持有谁」。收购方**不得**被写成「其官方文档称并不运营的品牌」的 brand parent。
- **平台集成 / 分销 / developer 同样不是 `parent_brand`**。一个产品可通过伙伴平台使用，这是**平台集成/分销**事实，不能反转或竞争 developer 的 `parent_brand`；两者可同时为真。只把 **Brand/Product Hierarchy** 这条边写进 manifest；平台关系留在审计证据层或 Review Queue。
- **不为单个案例扩张 SSOT schema**：仓库没有通用 relation-type 字段时，把边界写进命名契约 + 审计文档 + 一条回归测试，而不是加新 manifest 字段——除非确有全库 consumer 需要。schema 增长是 consumer 驱动的决策，不是 evidence 驱动的。
- **控股口径**：全资或多数控股可记为 `parent_brand`；少数股权、合资**一律不设母公司**；已分拆独立 / 已停运 / 公共非营利分别记 `NO_PARENT` / `RETIRED` 类状态。这些判定交 Review Queue，不靠结构 CI。
- **每条 `parent_brand` 边按证据类型分类**，关审前逐边标注：`BRAND_HIERARCHY_CONFIRMED`（明确的品牌伞/产品层级证明）、`CORPORATE_OWNERSHIP_ONLY`（仅股权/合并）、`DEVELOPER_PROVIDER_ONLY`、`PLATFORM_RELATION_ONLY`、`AMBIGUOUS`。**只有 `BRAND_HIERARCHY_CONFIRMED` 能证明该边**；其余类型可*支持*决策但**不得*替代*层级证明**——把「全资/多数控股」记成 `CONFIRMED_PARENT` 而该边的证据本身只是 ownership，是静默的语义过度声明。
- **可机读的证据清单**（若保留）：放在 `config/` 下，每边一条（child、parent、classification、review_status、证据 URL），并带回归测试断言：与 live SSOT 边集合**双向**集合相等（含条数，缺失或过期即 FAIL）；ownership-only / developer-only 的边保持 `OPEN_REVIEW`，不得静默提升为 confirmed；证据分类计数有 fixture，分类漂移即失败。
- 证据不足时**保留 SSOT 原值**并把该边标 `OPEN_REVIEW`，**绝不**用证据反推 SSOT。**CI 绿 / 结构 PASS ≠ 语义关审**：只要有 open-review 边或未解决的跨库不一致，结论就是 `BLOCKED`，blockers 列在 PR 正文的最终状态行。
- **一手来源可追溯**：每个有争议的模型，把**确切的**一手来源 URL（ToS / 隐私政策 / FAQ / 品牌指南 / 帮助中心）与生效日期记在审计文档决策旁，而不是只塞进 commit message。仅有社交帖子的日期只能记作**品牌身份改名 / branding transition**，没有 SEC/登记文件就**不得**标成「已证实的法人实体改名」——这个区分决定审计文档怎么措辞。
- **official-art provenance 必须拆成三条带标签的事实**，不许写成一句混合断言：`Official source asset`（厂商指南 URL + 资产包 URL + 成员名 + 取得日期）/ `Repository asset`（项目规范化派生物：等比缩放 + 项目共享圆角容器遮罩，**明确声明它不是官方文件逐字节副本**）/ `Logo artwork`（未重绘 / 未改色 / 未改设计，附像素证据：RGB 与缩放后的官方源一致、max diff 0）。厂商指南通常要求「按下载原样使用」，因此**不得**声称「官方资产未被改动」；加 CI guard 断言这三条标签始终存在于 README。
- **官方素材获取**：厂商品牌指南页常被 WAF 前置——对资产 URL 直接 `curl -I` 可能 403，而带浏览器 UA + 指南页 `Referer` 的 GET 返回 200。从厂商 zip 取资产后**只做**等比缩放 + 项目容器 alpha 遮罩，**绝不**重绘 / 改色 / 裁切 logo，也绝不改别家文件名。
- **容器遮罩复用，不要重新推导**：仓库里大多数图标共享**字节相同**的 alpha 通道，取该 alpha 作为 canonical squircle（四角 alpha=0），与官方 RGB 合成，别去猜半径。合入后断言新文件 SHA-256 全库唯一。
- **品牌识别视觉核验**：身份存疑时，用 PIL 拼一张带序号标签的 contact sheet（多图标一格），一次 vision 调用读全，比逐个调用高效。

### 7.1 证据层：证明有 consumer，否则删除（Historical Example）

> **Historical Example**：2026-10-01，本仓库的**机读证据层**被移除（JSON + 生成器 + 审计文档 + 其测试）。此事仅作历史示例，不代表当前文件清单。

- **规则（不是一次性事件）**：一个机读证据清单若**没有任何 live consumer**（CI / 生成器 / resolver / 下游都干净），且其中**绝大多数条目没有可独立核验的 `source.url`**，它就不是「支撑证据」，而是**第二套关系叙事**。判定：无 live consumer 且无可独立核验来源 ⇒ 删除 JSON + 生成器 + 审计文档，去掉其测试，**只留一条**历史说明（README 段落 + `upstream-history.md` 一行）写明移除原因。
- 标成 `blocking: false` **不等于**无害：计数照样漂移，读者照样把它当成图。
- **删除后用 guard 代替沉默**（三条）：
  1. 断言被删除的路径**保持不存在**，且历史说明行存在；
  2. 断言 SSOT 条目上**永不出现** `ownership` / `developer` / `platform` / `distribution` / `evidence` 这些字段名；
  3. 对下游的**机读关系导出**（如 `config/brand-relationships.json`，带 `generated: true` + 指明 `source`）仍可保留，但必须 CI 强制为派生物：逐行重算比对，并断言它**不是第二 SSOT**。
- 新品牌登记走**单一确定性入口**（如 `validate-brand.py`），复用关系引擎，**拒绝猜测 `parent_brand`**，无法机器判定的现实案例路由到机读 Review Queue（CI 组校验队列 schema + 断言 `is_ssot: false`）。
- PR 正文保留一行明确写出证据层结论。
- **禁止引用已删除的 `config/icon-mapping.json`**：该映射已删除，**勿再生成、勿再当现存要求**（旧文档出现它属 `HISTORICAL_OK`，只有在 `docs/migrations/**` 等显式排除路径里才合法）。

---

## 8. 模型变更会打破 pinned 测试，而不是校验器

- 把一个逻辑生态根提升为正式 SSOT 节点后，**校验器可能全绿，而 unittest 仍在断言旧模型**（白名单成员、`expected_icon_path() is None`、alias 检查）。**CI 门禁绿 ≠ 测试套件一致。**
- 任何关系/资产模型变更后：跑全套单测，grep 测试树里受影响的 ID，**在同一 commit 里迁移这些断言——绝不删除测试**。套件规模预期**增长**（新增不变量会带来新的变异覆盖）。
- 新品牌登记顺序：metadata（`brands.json`）→ `validate-brand.py` → resolver → generator → CI。

---

## 9. 分类与 entity_type

- 移动图标前，依据**实际图像**（vision）与 manifest `entity_type` 判断，而不是名字：在代理规则图标集里，通用的规则集/策略图标是 System，真实品牌才是其功能分类；代理术语读作 provider/ruleset，不是字面现实物体。**混合分类**（品牌 + 一个通用项）意味着那个通用项被错分类——移走它，保留品牌。
- CI 校验 `entity_type` 合法性与生态一致性，但**不校验**任意的 category/entity_type **贴合度**：一个 `product_brand` 条目可待在非品牌功能分类里而 CI 仍通过（生态目录是例外，由生态一致性组强制）。任何移动后，打印目标分类的 `entity_type` 分布，把矛盾的条目对齐到该分类约定（System → `system_icon`）。

---

## 10. 历史重建为干净 PR

- **把旧 PR 纯粹当候选材料**：用本地 git 读每个 commit 的 `parent` / message / `numstat` / patch（`rev-list --reverse`、`diff-tree`、`show`），与最终树对比。逐条分类：**KEEP / MERGE_INTO_OTHER / REIMPLEMENT_CLEANLY / SUPERSEDED / DROP**，在 PR 评论里发布分类表并写明被排除的错误方向，注明这是**审计判断**而非 cherry-pick 脚本。
- commit 级「文件被后续 commit 触碰」的检查只是**分诊**：任何自动生成物在**真正读过其 patch** 之前，只能标为 DRAFT。**绝不让关键词分类器代替审计。**
- 重建意味着**该相同的产物清单必须相同**：对比 old-tip vs new-tip 的资产树 blob SHA-256 集合，并明确陈述；任何漂移都是红旗。
- 按 pathspec 分阶段成若干逻辑 commit（SSOT → assets → engine → generators → validator/CI → tests → docs → derived），每条 message 写入文件后用 `-F` 提交（heredoc commit body 可能触发 shell 生命周期防护）。最后一条 commit 后验证生成器幂等（两轮 0 diff）并重跑校验器 + 套件，再推。
- **provider 限流时不要把逐 commit 历史审计外包给 subagent**（429 会在审计中途杀死子进程）。用 git 本地做；若某子进程确实失败，如实说明，不要把草稿当成品。

---

## 11. PR / CI 流程（一律 PR-only）

- **分支 → commit → push 分支 → PR → review → merge**。**绝不直接推 `main`**（任何形式的直推 `main` 都禁止）；不 force push、不重写历史，除非明确授权且留备份锚点。
- 提交信息：详细中文 + emoji；变更最小化，**每个 PR 单一目的**（文档纠错 / 校验器 / Skill 不混在一个 PR）。
- **先看 diff 再 commit / push**；确认 staged 内容、脱敏、CI 结果。
- `Validate Icons` 类 workflow 会**同时**触发 `push` 与 `pull_request` 两个 run，**两个都必须 success** 才能收尾。
- 每项 CI 增强都带**变异（负向）测试**：改 fixture → 期望 rc=1 + 指定错误文本 → 在 `finally` 里恢复。至少覆盖：漏标 `parent_brand`、删除生态目录、0 子节点的幻影生态目录、错误 `entity_type`、脏白名单条目、root 图标在生态目录之外、子节点 `category` 仍指向旧功能分类。
- 生态迁移后的**验证三件套**：① 校验器全组 PASS；② 负向测试全拦截；③ 生成器连跑两轮 0 diff。
- `gh` CLI 本机未预装时：用 `~/.config/gh/hosts.yml` 的 token 走 GitHub REST API（`api('/repos/{owner}/{repo}/pulls/N','PATCH',{'body':...})` 模式），git push 走 credential store；安装 gh 后需 `export PATH="$HOME/.local/bin:$PATH"`。
- **PR 正文**：每个数字都在**每次 revert/commit 之后**从当前工作树重算（迁移行数、parent_brand 条目数、active/reserved 总数、PNG/JSON parity）。推后 PATCH 正文并**读回**，确认 live 文本与重算数字一致。
- **读回断言必须是正文里的字面短语**：用改写措辞的检查串会在 PATCH 成功时也失败；断言精确子串（或直接从正文文件重算检查表），失败时先在正文里 grep 该主题再下结论。
- **增量 patch 会腐化正文**：多次小改后正文会退化成「patch 的 patch」，head SHA 与结论过时。此时**重建为一篇全新文档**（head SHA、commit 数、文件增量、清单、完整 commit 矩阵）整体 PATCH，再读回；**不要**在陈旧正文上继续堆小改。
- 汇报格式：`STATUS / Changed / Verified / Remaining / Commit / PR / Blockers / Out-of-Scope`。
- 收尾核对：工作树 clean、`git diff --check` 退出码 0、PR 处于 open 且**未合并**、`main` 未被触碰。

---

## 12. 常见坑速查

| 坑 | 后果 | 做法 |
|----|------|------|
| 按文件名/全路径排序 | 生成器输出不稳定 | 排序键固定 `(category, name)` |
| 手改 JSON 数组删元素 | 遗留尾逗号 / 双换行 | 用 Python `json.load`/`json.dump` 重排，`rstrip('\n')+'\n'` |
| 删 PNG 忘记删派生条目 | 生成器引用缺失文件 | 两侧同步清理 |
| `.DS_Store` 混入分类目录 | 污染目录列举 | 加入 `.gitignore` 并清理 |
| 限流下载存成 HTML | 伪 PNG 混入 | 按 magic bytes 校验 + Pillow 真解码 |
| 空品牌目录 | 虚增品牌数 / 丢 README 行 | 迁移后删空目录并断言目录数 == manifest 数 |
| oxipng 无损伤但改 `mode` | 「是否 RGBA」复检误导 | 规范表述为「RGBA 源 + 无损重压」，并禁用 color_type_reduction |
| 同一图像服务两个品牌 | SHA 唯一性 FAIL + 伪造 | 一个资产只归一个品牌；缺图标走白名单/队列 |
| 关键词豁免文档校验 | current 文档逃过校验 | 只用显式路径 exclude，伪示例改写成正则不匹配形式 |
| 硬编码品牌特例 | 新生态根不适用 | 按 `entity_type`/结构条件通用化，绝不按 ID 特判 |
| 手写第二套 root-walker | 与引擎拓扑静默分叉 | 一律 import 关系引擎函数 |
| 本地绿就当 CI 绿 | `__pycache__`/Pillow 等仅 CI 暴露 | 在干净 clone 上复现 CI 步骤 |
| 把 CI 绿灯当语义正确 | 现实归属未经证实 | 结构 CI 只证结构；语义交 Review Queue + 一手证据 |

---

## 13. 参考入口（在**当前仓库**里读取，不在本文件里抄）

- `docs/references/brand-naming-contract.md`（命名契约）
- `scripts/ci-validate-icons.py`（结构校验，组数以运行输出为准）、`scripts/ci-validate-docs.py`（文档 concrete 路径）
- `scripts/brand_relationships.py`（唯一关系引擎）、`expected_icon_path()`（唯一路径解析）
- `config/brands.json` / `config/categories.json`（SSOT）、`config/brand-review-queue.json`（人工裁决出口）
- `docs/migrations/**`、`upstream-history.md`、`brand-migration.md`、`category-migration.md`、`brand-ownership-audit.md`（历史/研究层，旧路径与旧数字是其职责）

> 本文件与仓库当前文件冲突时，**以仓库当前文件为准**；与 `SKILL.md` 冲突时，以 `SKILL.md` 的通用规则 + 仓库现状为准。
