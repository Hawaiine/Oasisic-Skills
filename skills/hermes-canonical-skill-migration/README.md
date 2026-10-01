<p align="center">
  <b>Hermes Agent Skill — 把外部 canonical Skill 安全接入本机</b>
  <br/><br/>
  <img alt="License" src="https://img.shields.io/static/v1?label=license&message=MIT&color=blue&style=flat-square"/>
  <img alt="Hermes Skill" src="https://img.shields.io/static/v1?label=Hermes&message=Skill&color=blueviolet&style=flat-square"/>
  <img alt="Scope" src="https://img.shields.io/static/v1?label=scope&message=skill%20migration&color=green&style=flat-square"/>
</p>

---

# 🧩 hermes-canonical-skill-migration

**把「外部 Git 仓库里的 canonical multi-file Hermes Skill」安全接入本机，并有序退役本机旧的重复 Skill。**

它是一份**迁移方法学**，不是任何项目的领域规范：只回答「source 怎么解析、装法怎么选、怎么证明真的加载了、
同名怎么排查、旧 Skill 怎么退役、证据怎么留」，不承载具体仓库的维护规则。

*English — a migration methodology for integrating an external repository's canonical multi-file Skill into a
local Hermes install: source resolution (tap / direct URL / external skill dirs), multi-file integrity,
discovery vs actual loading, name shadowing, legacy retirement with rollback evidence, and how to diagnose an
official install path that refuses to work without weakening any security control.*

---

## 📂 仓库内容

```
skills/hermes-canonical-skill-migration/
├── README.md                        # 本文件（给人：用途 / 结构 / 用法）
├── SKILL.md                         # 入口：核心不变量 + 决策树 + 迁移 checklist + 验收表
├── meta.yaml                        # 根 README 生成脚本读取的元数据
└── references/                      # 展开的专项程序（同一 Skill 的展开，不是第二套规范）
    ├── source-resolution.md         # tap / direct URL 诊断与失败分类（含 library vs CLI）
    ├── external-dirs.md             # external skill dir 前置条件、配置纪律、只读性验证
    ├── shadowing-and-loading.md     # 层级优先级、同名排查、Discovered/Registered/Loaded 取证
    ├── legacy-retirement.md         # 能力盘点、退役门、ACTIVE→RETIRED→ARCHIVED、回滚、残留分类
    └── troubleshooting.md           # 失败模式表 + 运行时新鲜度 + 升级后复测
```

---

## 🚀 使用方式

### 对话中加载

```
skill_view(name='hermes-canonical-skill-migration')
```

### 从本仓库安装（canonical source）

```bash
hermes skills tap add Hawaiine/Oasisic-Skills
hermes skills install Hawaiine/Oasisic-Skills/skills/hermes-canonical-skill-migration
```

> 本仓库是该 Skill 的 **canonical source**；本机只消费，不另存长期手工副本。
> 若本机 Hermes 的 tap 解析不可用，改用官方支持的其它方式（direct URL / external skill dir），
> **不要**手工复制 `SKILL.md` 冒充安装。

### 给其他 Agent 用

`SKILL.md` 自包含；需要细节时按需附上对应的 `references/*.md`。

---

## 🧭 它覆盖什么 / What it covers

- **Source Resolution 决策树**：官方 tap → direct URL install → external skill directory → `BLOCKED`；
  四级顺序固定，且不允许自行发明第五种机制
- **失败分类**：仓库结构 / tap 注册 / tap 索引 / CLI resolver / 网络 / 认证 / URL safety / source policy，
  以及 **library 层可解析但 CLI 层失败** 这一类「本机限制」而非「仓库缺陷」
- **Direct URL 链路验证**：URL → DNS/网络 → URL safety → HTTP fetch → SKILL.md parse → linked files；
  Fake-IP / 私网段拦截一律记为安全层 blocker
- **External dirs**：只允许指向**干净的 canonical checkout**；dirty → STOP；只读性按本机实现确认
- **多文件完整性**：入口 + 元数据 + references + scripts 全链路可读，拒绝「半安装成功」
- **三态区分**：Discovered / Registered / **Actually Loaded**；列表里有名字不是成功判据
- **Shadowing**：多层级优先级、同名副本清点、确认生效版本确实是 canonical
- **旧 Skill 退役**：能力盘点 → 退役门 → `ACTIVE → RETIRED → ARCHIVED`（不是 DELETE）→ 可回滚 + 证据保留
- **配置纪律**：备份三件套、最小精确改动、禁止整文件重写、区分三层运行时状态
- **升级后复测**：Hermes 升级后重新评估官方 tap / direct install，必要时从 workaround 切回官方机制
- **安全红线**：不为迁移成功关闭 URL safety / 网络策略 / 权限 / 分支保护 / 验证器

---

## ✅ 一次典型迁移流程

```bash
# 1) 先读真实状态，不要凭记忆
#    · canonical 仓库结构与默认分支
#    · 本机 Hermes 版本 + skills/tap/search/inspect/install/list/uninstall/config 的实际能力
#    · 本机已存在的同名 Skill（含 archive / retired 目录）

# 2) 按决策树选机制（tap → direct URL → external dirs → BLOCKED），每一步都实测并记录失败层级

# 3) external dir 路径下：确认 checkout 干净、revision == canonical、备份配置、最小改动

# 4) 证明接入：索引命中 + inspect 返回 canonical 内容 + references 逐个可读 + 同名无覆盖

# 5) 旧 Skill：能力盘点 → 退役门逐条满足 → 移出 active 路径（保留 backup/manifest/sha256）

# 6) 验收表填满：active canonical = 1，active obsolete = 0；未证明的项写 PARTIAL/BLOCKED
```

---

## 📜 License

MIT。
