# Source Resolution：从仓库到本机

本文件回答：**canonical Skill 应该以什么机制接入本机，以及每一步失败意味着什么。**

决策顺序固定（与 SKILL.md 的决策树一致）：

```
仓库结构 → 官方 tap → direct URL install → external skill directory → BLOCKED
```

不允许插入第五种机制。任何「手工复制 / 临时 fork / 打包解压后当 source」都违反核心不变量。

---

## 1. 先验证仓库侧结构（仓库的错不要推给本机）

接入前先确认 canonical 仓库本身符合 Hermes Skill 结构：

```
skills/<skill-name>/
├── SKILL.md          # 固定入口文件名，frontmatter 带 name + description；name == 目录名
├── README.md         # 给人读
├── meta.yaml         # 仓库元数据（若该仓库有此约定）
└── references/       # 可选；入口引用的文件必须真实存在
```

要点：

- **入口文件名固定** `SKILL.md`，不得改名；frontmatter `name`、目录名、以及元数据里的 `name` 必须一致。
- 仓库自身的校验脚本（identity / README 生成）必须先通过，再谈本机接入。
- 用 **默认分支（main / master）** 作为 source；PR branch、临时 commit 都不是 canonical。

## 2. 官方 tap：注册 ≠ 索引 ≠ 可安装

三步分别实测，不要跳步：

```bash
hermes skills tap list                        # 1) 注册状态
hermes skills search <skill-name>             # 2) 能否被搜索到
hermes skills inspect <identifier>            # 3) 能否解析并预览
```

失败分类表：

| 症状 | 归类 | 判断依据 | 安全动作 |
|------|------|----------|----------|
| tap 未出现在 `tap list` | **tap registration failure** | 配置/路径/tap 名不匹配 | 重新 `tap add`，确认仓库与 path 正确 |
| tap 已注册，`search` 命中 0 条 | **tap indexing failure** 或 **CLI resolver bug** | 换用 library 层直接解析同一 source | 记录为 CLI/indexing 限制，改用其它官方机制 |
| `search` 能命中但 `inspect` 失败 | **CLI resolver / source policy** | 同一 identifier 在底层 source 可预览 | 用 direct URL 路径复测，别改仓库结构 |
| 报网络 / 认证错误 | **network / authentication failure** | HTTP 状态、token 作用域、DNS 结果 | 修凭证或网络，不要改 Skill 仓库 |
| 被 URL 安全层拒绝 | **URL safety failure** | 日志里出现私网/危险地址判定 | 报 blocker；不关闭安全层 |

### library 层 vs CLI 层（关键区分）

同一台机器上完全可能出现：

```
library-level source resolution  = 可以读取 extra tap / 远端 SKILL.md
CLI-level resolution             = search / inspect / browse 解析不出来
```

这类现象必须标记为 **`CLI / indexing limitation`（本机限制）**，而**不是**「仓库结构有错」。
处理方式：换官方支持的其它机制（direct URL / external dirs），并在报告中记录该限制，
以便升级后复测。

## 3. Direct URL install：逐段验证链路

```
URL 合法性 → DNS/网络 → URL safety → HTTP fetch → SKILL.md parse → linked files 可得
```

- 只用 **canonical 仓库默认分支**的官方 URL；PR branch / 临时 commit URL 一律不用。
- 记录：URL、revision（或能定位 revision 的信息）、安装后的落地位置与内容摘要，
  保证日后可追溯「装的是哪一版」。

### 网络与安全层 blocker（不要「修」它们）

| 症状 | 归类 | 说明 |
|------|------|------|
| 域名被解析到私网 / 保留网段（例如 Fake-IP 场景） | **private-range interception** | 安全层按私网地址拦截属预期行为 |
| 请求被 URL safety 直接拒绝 | **URL safety rejection** | 这是**保护**，不是 bug |
| 缺少出网 / 代理配置导致超时 | **network failure** | 环境问题，需环境层解决 |

处理原则：

```
记录 blocker → 使用官方支持的替代机制（例如 external dirs）→ 报告中明确写 FAIL/BLOCKED 与原因
```

**禁止**：关闭 URL safety、放宽网络策略、绕过权限或代理安全规则来「让安装成功」。

## 4. 选择机制时的记录模板

每次 source resolution 都要能回答：

```
Canonical repository:
Canonical revision:
Tap:            PASS / FAIL / BLOCKED   （失败层级：注册 / 索引 / 解析 / 网络 / 安全）
Direct URL:     PASS / FAIL / BLOCKED   （失败层级：DNS / 安全层 / HTTP / 解析 / linked files）
External dirs:  PASS / FAIL / BLOCKED
Selected strategy:
Reason for rejecting the earlier options:
```

理由必须落在**实测证据**上（命令输出、日志行、HTTP 状态），而不是印象。
