---
name: hermes-canonical-skill-migration
description: >
  Use when integrating, reinstalling, or retiring an external canonical multi-file Hermes Agent Skill —
  choosing between the official GitHub tap, a direct SKILL.md URL, and a read-only external skill directory;
  verifying multi-file integrity (SKILL.md / meta / references / scripts); proving an external skill is
  actually LOADED rather than merely visible; detecting name shadowing across local / external / hub /
  builtin tiers; inventorying and retiring legacy duplicate skills with rollback evidence; and re-validating
  the install path after a Hermes upgrade. Also diagnoses why an official install path fails (tap registration
  vs indexing, CLI resolver limits, URL-safety or private-range interception) without weakening security controls.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, skills, migration, external-dirs, tap, shadowing, retirement, validation]
    category: hermes
    related_skills: [hermes-config-expert, skill-collection-management, hub-tap-skill-publish, hermes-migration]
---

# Canonical Skill 迁移 / External Skill Source Integration

把「外部 Git 仓库里的 canonical multi-file Skill」安全接入本机 Hermes，并有序退役本机旧的重复 Skill。

本 Skill 只负责**迁移与集成**：source resolution → installation → discovery → actual loading → shadowing →
legacy retirement → evidence。它**不承载任何具体领域知识**（不维护某个资产仓库、不复制任何项目的领域规范）。
领域规范属于各自的 canonical Skill。参见 `references/` 五份展开：source-resolution / external-dirs /
shadowing-and-loading / legacy-retirement / troubleshooting。

## 何时使用

- 要把某个外部仓库的 canonical Skill 接入本机，或把本机的手工副本换成 canonical 来源
- 想在「本机是哪个版本 / tap 能不能用 / 要不要改配置」上做决策，而不是先动手
- 官方 tap 或 direct install 报「找不到 / 解析失败 / 不允许」，需要区分**仓库结构问题**与**本机 CLI / 网络 / 安全层限制**
- 需要证明「本机实际加载的是 canonical 版本」，而不是「`skills list` 里看到名字」
- 需要退役本机旧 Skill，且要求**可回滚、保留证据、不产生第二份长期 source**
- Hermes 升级后要复测安装路径，决定是否从 workaround 切回官方机制

## 核心不变量（Invariants）

1. **Canonical repository = 唯一事实来源。** Hermes 本机是 consumer / runtime view / cache，
   不得被重新定义成 source；任何「在本机再存一份长期规范」的方案都违反本 Skill。
2. **禁止手工复制。** 不允许把 `SKILL.md` / `references/` 手动拷进本机冒充安装，不允许临时 fork
   冒充 canonical。只用官方支持的机制：GitHub tap → direct URL install → external skill directory。
   若三者都不可用 = `BLOCKED`，报告而不是发明第四种机制。
3. **Discovered ≠ Registered ≠ Actually loaded。** 接入成功的判据是「Agent runtime 索引命中 **且**
   入口文件与 linked files 实际可读」，不是文件存在、也不是列表里出现名字。
4. **同名唯一。** 同一个 Skill name 全机只能有 **1 份 active canonical**；retired / backup /
   historical / migration 记录不算 active，但必须能被解释身份。
5. **不弱化安全换取成功。** URL safety、网络策略、权限、分支保护、验证器都不得为迁移而关闭或绕过。
   环境限制 → `report blocker` + 改用官方支持的替代机制。
6. **退役有门（Retirement Gate）。** canonical 已合并/已确定 + 本机 checkout 与 canonical revision 一致 +
   可发现 + 实际可加载 + references 可用 + 同名 shadowing 已解决 + 旧 Skill 能力已盘点 + backup 已校验，
   才允许退役旧 Skill。
7. **结论必须带证据。** 每一步都要有命令输出或文件事实；「应该可以」不是证据。
8. **不把快照写回 Skill。** commit SHA、版本号、路径、数量、日期、PR 编号属于**报告**，
   不属于长期规则；写入 Skill 前必须抽象成规则。

## 三个身份（必须能逐项回答）

| 身份 | 含义 | 判定要点 |
|------|------|----------|
| **canonical source** | 外部 Git 仓库的默认分支工作树 | 干净 checkout、HEAD == 预期 revision、可编辑、唯一 |
| **consumer / cache** | Hermes 本机 | 只读消费；可能是 external dir 引用，也可能是官方 install 落地的副本 |
| **retired / backup / historical** | 已退役或迁移证据 | 不在 active 发现路径；保留 manifest / sha256 / 迁移记录 |

出现「仓库 + 本机副本 + 旧 Skill」三者并存且身份不明时，**先做 Source Inventory 再谈完成**。

## Source Resolution 决策树

```
0. 确认 canonical repository 结构符合 Hermes Skill 规范（SKILL.md + 可选 references/scripts/…）
        ↓
1. 官方 GitHub tap 可用？（tap add → search → inspect → install 全链路实测）
        ↓ yes → 用官方 tap/install
        ↓ no
2. 官方 direct URL install 可用？（URL → DNS → URL safety → HTTP fetch → SKILL.md parse → linked files）
        ↓ yes → 用 direct install（记录 URL + revision，保证可追溯）
        ↓ no
3. 本机支持 external skill directory？（读本机实现，不以文档推断）
        ↓ yes → 用 canonical 仓库的干净 checkout 作为只读 external source
        ↓ no
4. BLOCKED：报告失败层级、已实测证据、可行替代项；不绕过安全层、不手工复制
```

每一步失败都必须归类（见 `references/source-resolution.md`）：仓库结构 / tap 注册 / tap 索引 /
CLI resolver / 网络 / 认证 / URL safety / source policy —— **不要一律归因于「仓库有问题」**。

## 安装路径要点

### A. 官方 tap

- 先 `tap list` 确认注册状态，再逐个实测 `search` / `inspect` / `install`。
- 区分 **library 层能解析** 与 **CLI 层能解析**：底层 source 可读但 CLI 不显示 = `CLI / indexing limitation`，
  此时**不要**去改 Skill 仓库结构迁就 CLI。

### B. Direct URL install

- 只使用 canonical 仓库**默认分支**的官方 URL；不要用 PR branch URL、临时 commit URL。
- 链路逐段验证：DNS/网络 → URL safety → HTTP 状态 → SKILL.md 解析 → linked files 可得。
- 遇到 Fake-IP / 私网段映射 / URL safety 拒绝 → 记 `network / safety-layer blocker`，
  **禁止**关闭安全检查来「解决」（见「安全红线」）。

### C. External skill directory

- 前置条件：指向**干净的 canonical checkout**（默认分支、up to date），
  不是 scratch / PR workspace / 复制目录 / 打包解压目录。
- 工作区 dirty → `STOP`；不要 `reset --hard` / `clean -fd` / 覆盖用户改动，除非用户明确授权。
- external dir 的语义是「Hermes 直接消费 canonical 源」，**不是**「安装一份本地副本」。
- 只读性必须按**本机实际实现**确认（curation / sync / update 是否会写回该目录），不以文档推断；
  无法保证只读 → `STOP` 并做安全评估、考虑文件系统层保护。

细节与配置纪律见 `references/external-dirs.md`。

## 多文件完整性（Multi-file Skill）

「SKILL.md 能加载」不等于接入成功。至少逐项验证可读：

```
入口文件（SKILL.md）→ 元数据（meta.yaml / frontmatter）→ references/ → scripts/ → 其它 linked files
```

若入口可读但 references 缺失 = **半安装成功（partial install）**，必须按失败处理。
入口里声明的每个引用都要真实存在，且真实存在的每个引用都应被入口/README 引用（双向一致）。

## 实际加载验证（不能只看列表）

三态分别取证，缺一不可：

```
Discovered  → 本机发现该 Skill（索引/目录扫描）
Registered  → 本机把它登记为可用 Skill（安装记录 / hub 状态 / external 登记）
Loaded      → Agent runtime 真实索引命中，且能取到 canonical 内容与 linked files
```

推荐取证方式（按本机实现选择）：

- 走 **Agent runtime / prompt 构建**路径确认索引命中该 Skill；
- 用 **skill 查看/检查**（inspect / view）确认返回的是 canonical 内容，且 source 指向 canonical 而不是旧副本；
- 有 references 的，逐个打开确认可读。

注意：某些版本的 `skills list` 只覆盖 local / builtin / hub，**不含 external dirs**；
「列表里没有」不等于「没接入」，「列表里有」也不等于「加载的是 canonical」。详见
`references/shadowing-and-loading.md`。

## Shadowing（同名覆盖）

发现层级通常存在多档：local / project-local / external / hub / builtin，且有明确优先级。
必须做：

1. 读**本机实际实现**的优先级规则；
2. 列出同一 name 的**所有副本**（含 archive/retired 目录，标注是否 active）；
3. 判断最终生效的是哪一份；
4. 确认生效版本确实是 canonical source；
5. 确认旧 local copy 不会静默覆盖 canonical。

```
「看到 Skill」 ≠ 「加载了正确 Skill」
```

## 旧 Skill 处理与退役

1. **先盘点能力，再谈删除**：对每个旧 Skill 记录 Purpose / Unique Knowledge / Operational Procedures /
   Validation Gates / Failure Modes / Historical Caveats / Destination。
2. **合并判断看能力不看名字**：多个旧 Skill 是否属于**同一维护领域**、是否形成**重复规范风险**；
   若是 → 收敛为 `one canonical Skill + references/`。不要求所有 Skill 都合并。
3. **退役路径必须可回滚**：`ACTIVE → RETIRED → ARCHIVED`，而不是 `ACTIVE → DELETED`。
   保留 backup + manifest + sha256 + 迁移记录；恢复通道是**临时回滚**，不是重建第二份长期源。
4. **残留判定分类**，不要用 `grep = 0` 当唯一标准：
   `ACTIVE / CANONICAL / RETIRED / ARCHIVE / HISTORICAL / MIGRATION / FALSE-POSITIVE`；
   硬标准是 **active obsolete source = 0**，历史记录/备份可以合法存在。

完整流程见 `references/legacy-retirement.md`。

## 配置修改纪律（涉及 config.yaml 时）

```
read → backup → minimal targeted edit → verify diff → runtime validation
```

- 备份：同一时间戳，`config.yaml` / `auth.json` / `.env`（存在则一并备份）；
  `.env` 不得被 truncate / rewrite / clear / 重排；**禁止整文件重写**，只做最小精确改动。
- 改前先确认该键在**当前版本**的 schema 与语义；改后确认文件仍可解析、其它字段未变、
  受影响文件之外的字节未变。
- 配置生效范围要区分：`filesystem / config state` vs `新进程 state` vs `运行中进程 state`。

## 运行时新鲜度（Runtime Staleness）

改完文件/配置，**不等于**正在运行的服务已经加载新 Skill。必须区分三层状态并分别取证。
需要刷新时优先：**重建 prompt / 新起进程 / 新会话**；不要为验证而无必要地重启生产服务。

## Hermes 升级后必须复测

升级后按 `CLI help → tap search → tap inspect → direct install test → external_dirs 对比`
顺序复测，并选择**最简且官方**的机制。若官方 tap 恢复正常，可从 external dirs 切回官方 tap/install，
但必须完成完整验证（发现 / inspect / 实际加载 / references / shadowing）后再切换。
细节见 `references/troubleshooting.md`。

## 标准迁移 Checklist

```
[ ] canonical repository identified（结构符合 Hermes Skill 规范）
[ ] repository structure verified
[ ] current Hermes version verified
[ ] CLI capabilities verified（skills / tap / search / inspect / install / list / uninstall / config）
[ ] tap tested
[ ] direct URL tested
[ ] external_dirs capability verified（读本机实现，不靠文档推断）
[ ] installation strategy selected（决策树路径已记录）
[ ] canonical checkout clean 且 revision == canonical
[ ] config backed up（config.yaml / auth.json / .env）
[ ] minimal config change applied
[ ] Skill discovered
[ ] Skill inspected（内容与 source 正确）
[ ] Skill actually loaded
[ ] references available（X/Y）
[ ] same-name shadowing checked
[ ] old Skill capability inventory completed
[ ] backup verified（文件数 / sha256）
[ ] old Skill retired（ACTIVE → RETIRED，未删除）
[ ] runtime state refreshed if required
[ ] final canonical chain verified（active canonical = 1，active obsolete = 0）
```

## 验收表（每次迁移后必须能填满）

```
Canonical repository:
Canonical revision:

Hermes version:

Tap:                PASS / FAIL / BLOCKED
Direct URL:         PASS / FAIL / BLOCKED
External dirs:      PASS / FAIL / BLOCKED
Selected strategy:

Canonical checkout: CLEAN / DIRTY

Discovery:          PASS / FAIL
Inspection:         PASS / FAIL
Actual loading:     PASS / FAIL
References:         X/Y

Same-name shadowing: NONE / FOUND
Old Skills:          INVENTORIED / RETIRED / BLOCKED
Backup:              VERIFIED / BLOCKED
Runtime refresh:     REQUIRED / NOT REQUIRED

Final canonical source:
Active canonical copies:  <number>
Active obsolete copies:   <number>
```

硬条件：

```
Active canonical copies = 1
Active obsolete copies  = 0
```

任一项无法证明 → `MIGRATION-PARTIAL`；存在客观阻塞 → `MIGRATION-BLOCKED`。
**不要为了得到 COMPLETE 而绕过验证。**

## 安全红线

禁止为迁移成功而：

```
关闭 / 绕过 URL safety            修改网络安全策略            绕过权限
修改代理安全规则                  禁用验证器                  绕过 GitHub 分支保护
```

安全检查失败 ≠ 安全检查应该被关闭。正确顺序是：`report blocker → 使用官方支持的替代机制`。

## 边界（不要越界）

- 本 Skill 不描述任何**领域**维护规则；领域知识属于对应 canonical Skill。
- 本 Skill 不负责清理 tap / stray hub / 旧 clone / scratch copy / 分支 / backup；
  这些要先分类（`ACTIVE / CANONICAL / RETIRED / STRAY / TEMPORARY / HISTORICAL`）再谈 cleanup。
- 不要假设只能迁移某个特定仓库；任何符合 Hermes Skill 结构的 canonical Git 仓库都适用。

## Failure Modes（速查，完整表见 troubleshooting）

```
tap 注册了但 Skill 不被索引 | library 可解析但 CLI 失败 | direct URL 被 URL safety 拦截
Fake-IP / 私网段拦截        | 多文件 Skill 半安装        | external dir 指向过期 checkout
external dir 指向 dirty 工作树 | 同名 local Skill 覆盖 canonical | 装了但没真正加载
references 缺失             | 运行中进程仍是旧索引        | 临时工作目录被当成 canonical
canonical 未验证就退役旧 Skill | Hermes 意外改写了 canonical checkout
```

每个 failure mode 的 symptom / diagnosis / safe action / unsafe workaround 见
`references/troubleshooting.md`。

## References

| 文件 | 内容 |
|------|------|
| `references/source-resolution.md` | tap / direct URL 的失败分类与诊断、library vs CLI 解析、网络与安全层 blocker、证据记录 |
| `references/external-dirs.md` | external skill dir 的前置条件、canonical vs 工作副本、配置纪律、只读性验证、source inventory |
| `references/shadowing-and-loading.md` | 层级优先级、同名排查、Discovered/Registered/Loaded 取证、按版本的能力差异 |
| `references/legacy-retirement.md` | 能力盘点、合并判断、退役门、ACTIVE→RETIRED→ARCHIVED、回滚、残留分类 |
| `references/troubleshooting.md` | 失败模式表（症状/诊断/安全动作/危险 workaround）、运行时新鲜度、升级复测 |
