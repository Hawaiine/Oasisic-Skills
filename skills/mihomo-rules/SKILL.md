---
name: mihomo-rules
description: >
  Maintain Hawaiine/mihomo-rules (mihomo/clash-meta RULE-SET repo): Python daily
  sync, config generation (Android/Nikki × full/min), ruleset write/verify,
  ownership, Discord notify, CI daily-sync. Use when editing rulesets, configs,
  scripts/, or reviewing daily sync / push discipline.
tags: [proxy, mihomo, clash-meta, ruleset, nikki, android, ci]
---

# mihomo-rules 管理 Skill

> 对标主仓库 **Hawaiine/mihomo-rules** 现状（2026-07-25 起 Python 管线）。  
> **禁止**再按旧 shell 脚本（`sync-upstream.sh` / `generate-config.sh`）指导。

## When to Use

- 增删改 `ruleset/<Brand>/`、校验 header/payload/README
- 日更 / CI / Discord 通知异常
- 改 `configs/Android|Nikki` full/min 或 `scripts/generate_config.py`
- 品牌归属（SUB_PARENT）、图标、behavior、策略组拓扑
- 写可复制 Hermes 提示词 / 审 diff / 等「推」再 push

## 数字口径（铁律）

| 说法 | 正确 |
|------|------|
| 业务品牌 | **100** |
| 兜底规则集 | **7**（Reject, Direct, Proxy, Applications, Private, LanCIDR, CNCIDR） |
| 规则集合计 | **107**（100+7） |
| 禁止 | 「106 品牌」「105 品牌」 |

规则总条数随日更变（约 32 万+ payload 行）；文档写「约 32 万+」，Discord 用实时扫描。

## 项目结构（当前）

```
mihomo-rules/
├── ruleset/<Brand>/<Brand>.yaml + README.md   # 107 目录，每目录仅允许这两个相关文件
├── configs/
│   ├── Android/{config.yaml, config.min.yaml, README.md}
│   └── Nikki/{config.yaml, config.min.yaml, README.md}
├── scripts/
│   ├── batch_update.py          # 日更入口 8 步 + Discord CLI --notify
│   ├── commit_writer.py         # 写 ruleset YAML/README，幂等 + behavior
│   ├── fetch_upstream.py
│   ├── parse_v2fly.py / parse_loyalsoldier.py / parse_blackmatrix7.py
│   ├── merge_and_dedup.py
│   ├── resolve_ownership.py
│   ├── match_icons.py
│   ├── generate_config.py       # 4 变体 config
│   ├── verify_configs.py        # 失败 exit≠0
│   ├── verify_rulesets.py       # 失败 exit≠0；多余文件检查
│   └── lib/
│       ├── ownership_map.py     # SUB_PARENT 单源
│       ├── ownership.py
│       ├── canonical.py         # PROCESS 不 lower
│       └── validators.py
└── .github/workflows/daily-sync.yml
```

## Push / 协作纪律（Noah）

1. **先完整 diff**，用户明确说 **「推」** 才 `git push`
2. **禁止** `git add -A`；白名单：`ruleset/` `configs/` `scripts/` 及明确文件
3. **禁止** 裸 force；整理历史仅用户明确要求时用 **`force-with-lease`**
4. 坏/半成品日更：**优先 `git revert`**，勿 reset+force 清历史
5. 六段式报告必须 `git status` / `git log` **本机核实**，禁止假完成
6. Telegram 长提示词：纯文本、可整段复制；易截断则拆条

## 命名两线

| 线 | 用途 | 例 |
|----|------|-----|
| **技术 ID** | 目录、yaml 文件名、provider key、RULE-SET 第 1 段 | `PrimeVideo`, `myTVSuper` |
| **显示名** | 策略组 name、Rule Name、RULE-SET 第 2 段 | `Prime Video`, `myTV Super` |

拼法：`RULE-SET,<ID>,<显示名>`（rules 出站策略名 **不加引号**）。

## Ruleset 格式

```yaml
# ===========================================
# Rule Name: <显示名>
# Author: Hawaiine
# Updated: YYYY-MM-DD HH:MM:SS
# DOMAIN-KEYWORD / DOMAIN-REGEX / DOMAIN / DOMAIN-SUFFIX /
# IP-CIDR / IP-CIDR6 / IP-ASN / PROCESS-NAME 计数
# ===========================================
payload:
  - DOMAIN-SUFFIX,example.com
  - IP-CIDR,1.2.3.0/24,no-resolve
```

- payload **一律 `TYPE,value` 行**（classical 文件格式）
- 每品牌目录 **仅** `<Brand>.yaml` + `README.md`（`verify_rulesets` 检查多余文件）
- `Updated:` 仅在 payload **实质变化**时更新；纯时间戳噪音禁止提交

## behavior（官方 mihomo）

权威：https://wiki.metacubex.one/config/rule-providers/  
及内容页：https://wiki.metacubex.one/config/rule-providers/content/

| behavior | payload 形态 |
|----------|----------------|
| **classical** | `DOMAIN-SUFFIX,x` / `IP-CIDR,x` / `PROCESS-NAME,x` … |
| **domain** | 无类型前缀：`.blogger.com`、`*.x.com` |
| **ipcidr** | 无类型前缀纯 CIDR |

**本仓库全部 ruleset 为 classical 行 → config `rule-providers.behavior` 与 README 一律 `classical`。**  
禁止旧启发式「仅域名 → domain」。

实现入口：

- `commit_writer.determine_behavior` → 恒 `classical`
- `generate_config.detect_behavior` / `BASE_PROVIDERS` → classical
- `verify_rulesets` README 期望 classical

## 策略组与 rules 拓扑

### 系统组（约 28 前置）

- `♻️ 自动选择`：`url-test`，proxies = 21 地区节点组；`lazy: true`
- 21 × `xx 节点`：`select`，`proxies: [🎯 全球直连]`，`use: [provider_xx]`（**成对**）
- `🛑 全球拦截`：`select` → `DIRECT`, `REJECT`（必须能拦，**不要**只指全球直连）
- `🎯 全球直连`：`select` → **仅** `DIRECT`（rules/组内直连别名）
- `🔧 手动切换`：`select` → **`🎯 全球直连`**, `♻️ 自动选择`，`use: [provider1]`
- `🔯 故障转移` / `🔀 负载均衡` / `🐟 漏网之鱼`

### rules 激活段（逻辑顺序）

```text
RULE-SET,Reject,🛑 全球拦截
[Android] RULE-SET,Applications,🎯 全球直连
RULE-SET,LanCIDR / Private / Direct / CNCIDR → 🎯 全球直连
GEOIP,CN,🎯 全球直连
RULE-SET,Proxy,🔧 手动切换
MATCH,🐟 漏网之鱼
```

- **Nikki**：`find-process-mode: off` → **无** Applications 激活规则  
- **Android**：`find-process-mode: strict` → **有** Applications  
- rules 出站：**`,🎯 全球直连`**，禁止 `,\"🎯 全球直连\"`  
- `proxy-providers.*.proxy`：**字面 `DIRECT`**（拉订阅），不是全球直连组名

### full / min 格式

| 约定 | full | min |
|------|------|-----|
| `rules:` 上方空行 | 有 | 无 |
| rules 段内空行 | 可分段注释 | **禁止** |
| 品牌 proxy-groups 块间空行 | **有** | **无** |
| rule-providers 块间空行 | **有** | **无** |
| proxy-groups↔rule-providers 段间 | **空一行** | 紧凑 |
| `proxy-groups:` 键出现次数 | **1** | **1** |

生成：`gen_proxy_groups` / `gen_rule_providers` 的 `blank_between`；`assemble_config`。

## Python 日更管线

### 入口

```bash
python3 scripts/batch_update.py              # 本地：可 commit/push
python3 scripts/batch_update.py --no-commit  # CI：只写盘+校验，不提交
```

### 8 步（概念）

fetch_upstream → batch_write（merge+write_ruleset）→ resolve_ownership --apply → generate_config → validate → verify_configs → verify_rulesets →（本地则）commit 或 idle

### 写入幂等（`commit_writer`）

- `_normalize_for_compare`：统一换行、滤 `Updated:`、行尾空白、去末尾空行  
- `write_ruleset` 路径锚定 **仓库根** `Path(__file__).resolve().parent.parent`  
- yaml/readme **独立**判断；无实质变化 **绝不** atomic_write  

### PROCESS 大小写（`lib/canonical.py`）

- `PROCESS*`：**禁止** `.lower()`，仅 strip  
- DOMAIN*：lower + 去尾点  

### CI `daily-sync.yml`

```text
checkout → Oasisic-Icons → batch_update --no-commit
→ verify_configs → verify_rulesets
→ 🧹 滤仅 Updated（sed '/Updated:/d' + md5，while read，pathspec ruleset/**/*.yaml）
→ 白名单 porcelain：ruleset/ configs/ scripts/
→ 有变更才 commit/push（cached 空则 exit 0）
→ Discord：--notify pushed | skip（滤噪之后！）
```

**禁止**在 `--no-commit` 末尾无脑发「同步成功」。

### Discord 通知（`batch_update.py`）

```bash
python3 scripts/batch_update.py --notify skip --noise-restored N
python3 scripts/batch_update.py --notify pushed --commit-sha SHA
```

- `collect_repo_stats()`：100 品牌 / 107 规则集 / **全库** rules_total（含兜底）  
- push 卡 ± 规则、config 变更：优先 **`HEAD~1..HEAD`**（提交后工作区干净）  
- 无 WEBHOOK：静默 return，不崩流水线  

## 校验命令

```bash
python3 scripts/verify_configs.py    # 4/4 PASS，失败 exit 1
python3 scripts/verify_rulesets.py   # 106 PASS，失败 exit 1
python3 scripts/generate_config.py   # 幂等应 [=] 跳过
python3 -m py_compile scripts/*.py scripts/lib/*.py
```

verify_configs 要点：rules 键与空行约定、系统组顺序、SUB_PARENT、Applications 语义、proxy-groups 仅 1 次、min 块间无空行、rules 无引号策略名、无 rules 字面 DIRECT（用全球直连别名）。

## 脏日更处理

| 症状 | 处理 |
|------|------|
| 仅 `# Updated:` 噪音 commit | 写端幂等 + CI 过滤；已发生则 revert，禁 force |
| PROCESS 被 lower | revert + 修 canonical |
| 半成品（有组无 provider） | revert，再成对重做地区 |
| 报告写「已推」但 origin 无 tip | 以 `git fetch` + `rev-parse origin/main` 为准 |

## 常见陷阱（现行）

1. **假完成六段式**：无 diff 却写已改完 → 推前必须 `git status`  
2. **behavior 标 domain** 但 payload 是 `TYPE,value` → 违反官方格式  
3. **f-string 过度转义** 生成 `\"🎯` → 品牌组全球直连坏掉（已修 gen_proxy_groups）  
4. **CI 先 success 通知再滤噪跳过提交** → 已改为滤噪后 notify  
5. **rules_total 只计 100 品牌** → 卡片假小数；须含 7 兜底  
6. **notify_pushed 用工作区 git diff** → 提交后 ± 恒 0；须 HEAD~1..HEAD  
7. **拦截组指全球直连** → 无 REJECT，广告拦不住  
8. **全球直连 ↔ 手动切换互相指向** → 环；全球直连只允许 DIRECT  
9. **文档链接** `/config/sniffer/` 404 → 官方 `/config/sniff/`  
10. **git add -A / 裸 force / 未说「推」就 push**  

## 提交前清单

- [ ] `verify_configs` 4/4、`verify_rulesets` 107  
- [ ] 无 `behavior: domain`（configs + README）  
- [ ] 无 `\"🎯` 错误转义  
- [ ] full/min 空行约定；21 地区 provider↔组成对  
- [ ] rules 直连用 🎯 全球直连；providers 仍 DIRECT  
- [ ] 手动切换首项为 🎯 全球直连（非 DIRECT）  
- [ ] 拦截组仍含 REJECT  
- [ ] 完整 diff；用户说「推」；白名单 add；普通 push  

## 版本锚点（主仓库，便于对照）

| 主题 | 约 commit |
|------|-----------|
| 全球直连 + 21 地区成对 | `029074e` |
| 日更噪音加固 / 路径锚定 | `499b924` 起 |
| behavior 全 classical + full 空行 | `0d97c47` |
| Discord 通知对齐 + 统计 | `f785d0e` / `952cc00` |
| 手动切换 → 全球直连 | `39b9998` |

以 `origin/main` 最新 log 为准，上表仅帮助检索历史。
