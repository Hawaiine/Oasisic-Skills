<p align="center">
  <img src="https://raw.githubusercontent.com/Hawaiine/Oasisic-Icons/main/icons/Surge/Surge/Surge.png" width="80" alt="Oasisic-Icons"/>
  <br/><br/>
  <b>Hermes Agent Skill — Hawaiine/Oasisic-Icons 唯一 canonical 长期维护规范</b>
  <br/><br/>
  <img alt="License" src="https://img.shields.io/static/v1?label=license&message=MIT&color=blue&style=flat-square"/>
  <img alt="Hermes Skill" src="https://img.shields.io/static/v1?label=Hermes&message=Skill&color=blueviolet&style=flat-square"/>
  <img alt="Project" src="https://img.shields.io/static/v1?label=ref&message=Hawaiine/Oasisic-Icons&color=blue&style=flat-square"/>
</p>

---

# 🎨 oasisic-icons-maintainer

**[Hawaiine/Oasisic-Icons](https://github.com/Hawaiine/Oasisic-Icons)** —— 跨平台代理策略组品牌图标合集（SSOT + 关系引擎 + 生成器 + CI 单向派生）。

本 Skill 保存的是**长期维护规则**：事实在哪、关系怎么判、路径怎么推、资产怎么处理、变化如何全链路传播、文档如何分界、验证到哪一步为止。
它不复制 README，也不保存当前仓库快照（图标数量、分类数、生态数、commit SHA 等）。

*English — the single canonical maintenance skill for the Oasisic-Icons asset repo: facts, invariants, change
propagation, documentation boundaries and validation limits. It stores stable rules, never repo snapshots.*

---

## 📂 仓库内容

```
skills/oasisic-icons-maintainer/
├── README.md              # 本文件（给人：用途 / 结构 / 用法）
├── SKILL.md               # Hermes 加载的核心知识：核心规则 + Change Propagation + 工作流入口
├── meta.yaml              # 根 README 生成脚本读取的元数据
└── references/            # 专项操作流程（同一 canonical Skill 的展开，不是第二套规范）
    ├── intake.md          # 用户图片入库：512 RGBA r≈115 处理、置名、批推、回读校验、坑
    ├── rename.md          # 品牌 identifier 改名：两层命名、Impact Matrix、全链路同步、consumer blast radius
    ├── ssot-sync.md       # brands.json 配置层 / 白名单 / 根图标 / 本机安全 push
    ├── audit.md           # 全库审计：数值重算、parity、体积异常、生态规则、ownership 分类、迁移
    └── spec-change.md     # 规范值变更传播：code → docs → README、残留扫描、几何校验 caveat
```

---

## 🚀 使用方式

### 对话中加载

```
skill_view(name='oasisic-icons-maintainer')
```

### 从本仓库安装（canonical source）

```bash
hermes skills tap add Hawaiine/Oasisic-Skills
hermes skills install Hawaiine/Oasisic-Skills/skills/oasisic-icons-maintainer
```

> 本仓库是该 Skill 的 **canonical source**：本机只消费它，不再维护第二份手工副本。
> 若本机 Hermes 版本的 tap 解析不可用，请改用官方支持的其它方式（直接 URL 安装 / external skill dir），
> **不要**手工复制 SKILL.md 冒充 canonical installation。

### 给其他 Agent 用

`SKILL.md` 是单文件、自包含的知识源，可直接喂给 Claude Code / Cursor / OpenCode 等；深流程按需附上 `references/`。

---

## 🧭 它覆盖什么 / What it covers

- **Repository Identity**：独立最高上游；下游只是 consumer，不得反向定义 SSOT 事实
- **SSOT**：`config/brands.json` + `config/categories.json`；`category` 与 `parent_brand` 语义互相独立
- **Naming Model**：`identifier`（目录/文件名）≠ `display_name`；显示名变更 ≠ identifier rename
- **Relationship Model**：`parent_brand` = immediate brand/product parent ≠ ownership / developer / platform
- **Physical Path**：一切路径推导走 `expected_icon_path()`，禁止各脚本自行拼装
- **Ecosystem**：生态根动态派生（graph root + canonical descendants 达阈值），不维护生态清单、不写死数量
- **Asset Model**：512×512 / RGBA / squircle r≈115 / 像素保真；
  `official source asset` ≠ `repository asset` ≠ `recreated artwork`
- **Change Propagation Protocol**：任何事实变化 → 依赖发现 → 影响分类 → 同步 → 重生成 →
  旧值残留扫描 → 校验（含 Acceptance Table）
- **Review Queue**：现实世界语义交人工裁决，evidence 不得成为第二真相
- **Generated Files**：SSOT → resolver → generator → derived → CI 单向派生，生成器必须幂等
- **Documentation Discipline**：generated / manual reference / historical 三类边界；
  current-state 文档里的 concrete icon path 是公开契约，**无豁免清单**
- **Validation**：结构一致性 CI + 文档引用校验 + 单测 + `git diff --check`；CI green ≠ 现实语义正确
- **Common Failure Modes**：文档路径失效、统计腐烂、身份混淆、字段与派生双轨、自洽 CI ≠ 现实真相
- **Git / PR Discipline**：branch → PR → review → merge；不直推 main、不重写历史

---

## ✅ 一次典型维护流程

```bash
# 1) 先读当前真实状态（不要凭记忆）
git fetch origin && git reset --hard origin/main
python3 scripts/ci-validate-icons.py
python3 scripts/ci-validate-docs.py
python3 -m unittest discover -s tests

# 2) 改动（SSOT → resolver → 生成器 → CI，禁止手改生成物）
#    · 新品牌：brands.json → validate-brand.py → 生成器 → CI
#    · 改名 / 移动 / 关系变化：先做 Impact Matrix，再按 Change Propagation 全链路同步
#    · 改路径/分类：文档中的可复制示例必须同批修改

# 3) 门禁 + 生成器幂等（两轮 0 diff）+ diff 确认后，分支 + PR（不直接推 main）
```

---

## 🔗 相关文档（都在上游仓库里）

| 文档 | 作用 |
|------|------|
| `docs/references/brand-naming-contract.md` | 命名与同步契约 |
| `docs/references/brand-ownership-audit.md` | 研究层：现实世界归属证据（历史快照，非当前状态） |
| `docs/guides/usage.md` | 面向用户的客户端图标配置指南 |
| `docs/migrations/*` | 历史迁移表（旧路径是其记录对象） |

---

## 📜 License

MIT —— 与上游仓库一致；品牌图标商标归各自权利人。
