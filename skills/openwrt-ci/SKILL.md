---
name: openwrt-ci
description: "Use when maintaining OpenWrt firmware CI/CD (GitHub Actions SDK builds, feeds pin, last_build dedupe, QEMU smoke, Release/minisign) — especially Hawaiine/Oasisic-OpenWrt style pipelines. Encodes OpenWrt ; vs ^ feeds syntax, dispatch force_build/nikki_ref, and verified failure/success runs."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [openwrt, ci-cd, github-actions, feeds, nikki, firmware]
    related_skills: [systematic-debugging, plan, github-actions-workflows]
---

# OpenWrt CI Skill

从 [Oasisic OpenWrt](https://github.com/Hawaiine/Oasisic-OpenWrt) 实战提炼的固件 CI/CD 知识与模板。  
目标：搭流水线、审 PR、查失败 run 时行为一致，避免把「文档写过」当成「构建已通」。

**模板目录：** `templates/`（workflow / gen-feeds / gen-config / 向导与 CGI 片段）  
**深度参考：** `references/feeds-version-tracking.md`

---

## When to Use

- 新建或大改 OpenWrt 全量 SDK GitHub Actions 流水线  
- 排查 `feeds update` / Nikki 版本钉定 / 重复全量编译  
- 增加手动 pin（tag / branch / commit）与 Release 短标签  
- 首次启动向导、QEMU 烟雾、minisign、Discord 通知联调  

**不要用于：** 日常改业务规则集（mihomo-rules）、与编译无关的 LuCI 二次开发 alone。

---

## 一、推荐仓库结构

```
openwrt-firmware/
├── .github/
│   ├── workflows/
│   │   ├── openwrt-auto-build.yml   # 主流水线（见 templates/main-build.yml）
│   │   └── cleanup-actions.yml      # 定时清失败 run / 旧 cache
│   └── minisign.pub
├── files/                           # 注入 rootfs
│   ├── etc/config/
│   ├── etc/uci-defaults/99-custom
│   ├── etc/shadow                   # CI 写入随机 root 哈希
│   ├── usr/lib/<project>/           # firstboot / rollback 库
│   └── www/                         # 向导 + cgi-bin
├── scripts/
│   ├── gen-config.sh
│   ├── gen-feeds-conf.sh            # 必须正确实现 ; / ^
│   ├── check-firmware.sh
│   ├── check-docs-consistency.sh
│   ├── minisign-sign.sh
│   └── notify-discord.py
├── feeds.conf                       # 本地参考；CI 以 gen-feeds 输出为准
├── LICENSE
└── README.md
```

`last_build_version`：**成功构建后**由 job 回写；不要假设它永远在树里。删除它可强制「无历史」重建。

---

## 二、流水线（八个任务，正式构建与 PR 验证共用）

```
lint ─ check-upstream ─ build ─ qemu-smoke-test ─┬─ release ── persist-last-build
                                                 ├─ ci-prerelease（仅 PR）
                                                 └─ notify-failure（任一步失败时）
```

| Job | 职责 | 完成标准 |
|-----|------|----------|
| lint | `bash -n` / `py_compile` / workflow YAML / feeds 分隔符契约 | 几分钟内出结果，PR 必跑 |
| check-upstream | 解析 OWRT latest tag、Nikki ref→完整 SHA；算 composite；should_build；输出 `artifact_name` | outputs 含 `should_build` / `nikki_sha` / `nikki_short_sha` / `artifact_name` |
| build | 冷/热编译、签名、自检、上传 artifact | artifact 含镜像与 sha256sums（及 minisig）；PR 件名带 `-pr<号>` |
| qemu-smoke-test | 启动固件，LuCI 200 + JS 非 gzip 垃圾 | 失败则阻断 release；qemu/OVMF 缺失要**硬失败**，别静默跳过 |
| release | softprops 发 Release + Discord 成功卡片 | tag = `<ver>-n<shortsha>`；files 含 minisig |
| ci-prerelease | PR 构建产物发 `ci-<ver>-pr<n>-r<run>` prerelease | `prerelease: true`、`make_latest: false` |
| notify-failure | 失败卡片：失败任务 + 失败步骤 + 日志链接 | `if: failure()`，`continue-on-error: true` |
| persist-last-build | 回写 composite 到仓库 | commit 含 `[skip ci]`；main 可推 |

### needs 链

下游要用谁的 outputs，**必须**写进自己的 `needs:`。  
`release` 至少 `needs: [check-upstream, build, qemu-smoke-test]`。  
`persist-last-build` 在 release 成功之后。

### workflow_dispatch（必备）

```yaml
workflow_dispatch:
  inputs:
    force_build:
      description: '强制构建（跳过版本比较）'
      type: boolean
      default: false
    nikki_ref:
      description: 'Nikki ref（tag/branch/sha，空=latest tag）'
      type: string
      default: ''
    runner_image:
      description: 'Runner 镜像（空=仓库变量 RUNNER_IMAGE，再空=ubuntu-26.04）'
      type: string
      default: ''
```

三段回退：`inputs.runner_image || vars.RUNNER_IMAGE || 'ubuntu-26.04'`。
要对比验证另一镜像时不用改 main，dispatch 时填即可。

UI 上 `force_build` 是**勾选**，不是下拉。

### composite / should_build

推荐：

```text
COMPOSITE="${OWRT_TAG}_nikki-${NIKKI_SHA}"
```

- **kernel.org 版本只展示**，不要当 should_build 主信号  
- `force_build=true` → 强制 true  
- `COMPOSITE != SAVED` 或文件缺失 → true  
- 读写字段必须同一套（否则永远全量编）

### 缓存

| 层 | Key 要点 |
|----|----------|
| ccache | owrt_ver + `hashFiles('scripts/gen-config.sh')` |
| source | owrt_ver + config hash |
| dl/feeds | owrt_ver + **nikki_sha** + config hash |

`MAKE_JOBS: 4`（免费 runner）。clone / feeds / download 建议 3 次重试。  
编译：`make -jN || make -j1 V=s`。

**反模式：** 每次 build 成功再跑一遍清 cache 的 job（与独立 `cleanup-actions.yml` 重复，且伤热构建）。

---

## 三、Feeds 管理（P0）

OpenWrt `scripts/feeds`：

| 语法 | 含义 |
|------|------|
| `url;Tag或分支` | `clone --depth 1 --branch` |
| `url^完整Commit` | clone 后 fetch/checkout **commit** |

### gen-feeds-conf 契约

```bash
# 第二参 40 hex → ^
src-git nikki https://github.com/nikkinikki-org/OpenWrt-nikki.git^f06b6b448928501e7511bdfb3497b1186d919316
# Tag/分支 → ;
src-git nikki https://github.com/nikkinikki-org/OpenWrt-nikki.git;v1.26.1
```

模板：`templates/gen-feeds-conf.sh`（已实现 40 位检测）。

### 失败铁证

```text
Updating feed 'nikki' from '…git;f06b6b448928…'
fatal: Remote branch f06b6b448928501e7511bdfb3497b1186d919316 not found
```

- 失败 run：`https://github.com/Hawaiine/Oasisic-OpenWrt/actions/runs/30098510806`  
- 修复提交：`75a011b`  
- 成功 pin 构建：`https://github.com/Hawaiine/Oasisic-OpenWrt/actions/runs/30107519212`

**check-upstream 绿 ≠ feeds 对。**

深度说明见 `references/feeds-version-tracking.md`。

---

## 四、Nikki 跟踪策略

| 模式 | 行为 |
|------|------|
| 默认（定时） | latest Release Tag → 解析 SHA → feeds `^SHA` |
| 手动 pin | `nikki_ref=main` 或短/完整 sha，常加 `force_build=true` |
| 仅有新 commit 无新 tag | 定时**不会**自动吃到；必须手动 |

解析顺序建议：`GET /repos/.../commits/{ref}` → `git ls-remote … REF^{}`。

---

## 五、Release 与签名

- `tag_name: ${owrt_ver_safe}-n${nikki_short_sha}`（例 `25.12.6-n31339d5`）；**不要**带 `oasisic-` 前缀和 `-nikki-`，两个都是冗余  
- `files:` 必须包含 `sha256sums.minisig`（若签名步骤生成）  
- Release 正文用两行区分身份：`Nikki 版本`（取自产物包文件名，是编进固件的包版本）+ `Nikki 提交 31339d5（ref: v1.26.2）`（实际拉取的源码提交，括号里保留 ref 原文，tag/分支/sha 三种 pin 都不歧义）  
- Discord：`notify-discord.py`；`env` 里不要写 shell `$(date)` 指望展开，在 `run:` 内赋值  

Secrets：`MINISIGN_SECRET_KEY` / `MINISIGN_KEY_ID` / `MINISIGN_PASSWORD`；`DISCORD_BOT_TOKEN`。

---

## 六、首次启动与配置

### 状态机

```
99-custom → touch /etc/.oasisic-firstboot
index.html 检测 → setup.html
CGI 写 uci / 密码 → clear 标记 + chmod 000
可选 rollback（约 30 分钟有效）
```

模板：`templates/99-custom`、`firstboot.sh`、`setup-rollback.sh`、`cgi-bin/*`。

### 语言（zh_cn）

```sh
uci set luci.languages='internal'
uci set luci.languages.zh_cn='简体中文 (Simplified Chinese)'
uci set luci.main.lang='zh_cn'
```

规避 openwrt#16987（apk uci-defaults 在部分环境不跑）。

### 诊断

DNSPod：`119.29.29.29`（dns/ping/route）。

### 网络默认

LAN DHCP 客户端；IPv6 RA/DHCPv6/NDP 默认关（旁路场景）。hostname 用静态 `system` 配置。

---

## 七、QEMU 烟雾测试

- 优先 EFI 镜像；OVMF 缺失时**不要**静默 `exit 0` 放行 release（至少 fail 或明确 skip 策略文档化）  
- LuCI：`curl` 等 200  
- JS：体积下限 + 前两字节非 `1f 8b`（gzip 当 JS 吐）  
- 超时量级：300s 量级可调  

---

## 八、自检与文档校验

| 脚本 | 作用 |
|------|------|
| check-firmware | 包格式 APK/IPK、关键路径、99-custom 关键串 |
| check-docs-consistency | README 声称的包是否在 gen-config 启用 |

注意：若脚本 `exit 0` 仅信息级，**不能**当硬门禁吹嘘。

---

## 九、Git / 协作纪律（用户约定）

| 规则 | 说明 |
|------|------|
| 推送 | 用户说「推」才普通 push |
| force | 默认禁止；**仅明确洗历史** 用 `force-with-lease`，禁裸 `--force` |
| add | 禁 `git add -A`；白名单路径 |
| 审代码 | 优先审 `origin/main`，少让用户搬 diff |
| 分叉 | 执行方 `fetch` + `rebase origin/main` |
| 假完成 | 远程搜不到 `force_build`/`nikki_ref`/`persist-last-build`/`url^FULL_SHA` = 未落地 |

手动构建步骤（给用户的正规中文说明）：

1. Actions → 工作流 → Run workflow  
2. 勾选 `force_build`（需要时）  
3. 填写 `nikki_ref` 或留空  
4. 等五阶段结束 → Releases 下载  

---

## 九·四、Runner 镜像迁移（ubuntu-latest → 26.04，2026-10）

GitHub 于 2026-10-19 起把 `ubuntu-latest` 分批迁到 Ubuntu 26.04（runner-images#14748，11-19 完成），窗口期内镜像**随机漂移**。对策：显式固定镜像，别用 `latest`。

26.04 实测差异（探针 + 真实构建验证）：

| 项 | 24.04 | 26.04 |
|---|---|---|
| gcc | 13 | **15.2.0** |
| python | 3.12 | 3.14 |
| `qemu-system-x86-64` 包 | 有 | **已删除** → 改 `qemu-system-x86`（二进制名不变） |
| `libncurses5-dev` / `w` | 有 | 无正式包 → `libncurses-dev` |
| OVMF 路径 | `/usr/share/OVMF/OVMF_CODE_4M.fd` | 同 |
| OpenWrt tools/install | ✅ | ✅（gcc 15 下可编） |

**必踩的坑**：qemu 安装写 `|| true` 会静默吞错 → OVMF 找得到、qemu 缺二进制、300s 超时后才失败，日志误导。改成按序回退 + `command -v` 硬校验。

**缓存**：换镜像必须把镜像维度写进 ccache / source-tree 的 cache key，否则命中旧镜像的 `staging_dir/host`，报 `staging_dir/host/bin/python3: No such file or directory` → `package/system/apk [host] failed`。

## 九·四·五、60 天停用的防呆：每周心跳

GitHub 规则：公开仓库 60 天无提交活动 → 所有 schedule 工作流被自动停用。只在上游有新版本时才有 persist 提交的仓库，上游长期不发版就会中招。

**仓内心跳（主）**：`.github/workflows/keepalive.yml`

```yaml
on:
  schedule: [{cron: '0 3 * * 1'}]     # 每周一 UTC 03:00
  workflow_dispatch:
permissions: {contents: write, actions: write}
```

- 提交 `.github/keepalive` 时间戳，commit 带 `[skip ci]` → 每周制造一次活动，计时器持续归零
- 同一 job 再查 `/actions/workflows`，发现 `state != active` 就 `PUT /actions/workflows/{id}/enable`
- 心跳自身靠"每周提交"维持活跃，不会被自己的规则停掉；若它连续失败 60 天才需要人工
- 外部看门狗（本机 cron 检查并补提交）**只能当兜底**：本机可能停机

## 九·五、试编后回滚（验证构建 → 让定时自己编）

用户要求「先手动跑一次确认能编，然后把这次 Release / run 记录删掉，等定时流水线自己出包」：

1. 删 Release + tag：`DELETE /releases/{id}`、`DELETE /git/refs/tags/{tag}`
2. 删 run：`DELETE /actions/runs/{id}`（日志/artifact 一并清）
3. 回退去重键：`PATCH /git/refs/heads/main {"sha": "<baseline>", "force": true}` —— 指向该次 persist 提交的父提交，等效撤销那条 `chore: 更新 last_build_version [skip ci]`，不新增提交
4. 5 分钟后回读：main tip / `last_build_version` / releases / runs

坑：
- **删 Release 或 run 都不会让去重失效**；不动 `last_build_version` 就永远不会自动重编。
- 必须等 run `completed`（persist 在 build 之后才 push）。
- 回退前确认 main 无保护/无 ruleset，且 tip 仍是那条自动提交。

## 十、常见陷阱（精简表）

| ID | 坑 | 正确做法 |
|----|----|----------|
| P0 | feeds `url;完整SHA` | `url^完整SHA` |
| P0 | last_build 只写不 push / 被 gitignore | persist job + 取消 ignore |
| P0 | composite 读写字段不一致 | 同一套 `OWRT_TAG_nikki-SHA` |
| P0 | Release 仅 `oasisic-ver` | 加 `-nikki-shortsha` |
| P1 | minisig 只在 artifact | 加入 softprops files |
| P1 | 每构建 cleanup cache | 独立定时 cleanup |
| P1 | 根 feeds.conf 当权威 | gen-feeds-conf 为准 |
| P1 | dispatch 无 inputs | 加 force / nikki_ref |
| P1 | `ls-remote \| head -1` 解析附注 tag | commits API 或 `^{}` |
| P2 | QEMU 缺文件 exit 0 | 明确失败或文档化 skip |
| P2 | workflow env 中 `$(date)` | step run 内展开 |
| P2 | 429 checkout action | 多为 warning，重试即可 |

更多锚点与日志摘录见 `references/feeds-version-tracking.md`。

---

## 十一、排错方法

1. `gh run view <id>` 看哪一 job/step 红  
2. `gh run view <id> --log-failed` 搜 `Updating feed 'nikki'`、`Remote branch`、`^`、`;`  
3. 本地复现 gen-feeds 输出  
4. 确认 head SHA 是否含 `^SHA` 修复  
5. 去重异常：查 `last_build_version` 内容与 persist 是否绿  

---

## 十二、验证清单

- [ ] dispatch 有 `force_build` + `nikki_ref`  
- [ ] gen-feeds：40hex → `^`；tag → `;`  
- [ ] build 把 **完整 nikki_sha** 传给 gen-feeds  
- [ ] dl cache key 含 nikki_sha  
- [ ] composite 不含 kernel.org 主信号  
- [ ] persist-last-build 存在；gitignore 不忽略 last_build  
- [ ] Release tag 含 nikki shortsha；files 含 minisig  
- [ ] 无「每构建清 cache」重复 job  
- [ ] 手动 pin 构建：feeds 步绿 → 全绿（参考 run `30107519212`）  
- [ ] README 与实现对齐（无死链旧 Release 当真理）  

---

## 十三、模板文件

| 模板 | 对应 |
|------|------|
| `templates/main-build.yml` | 主 workflow（五阶段，含 pin） |
| `templates/cleanup.yml` | 定时清理 |
| `templates/gen-feeds-conf.sh` | feeds 生成（`;`/`^`） |
| `templates/gen-config.sh` | `.config` 生成 |
| `templates/99-custom` | 首次 uci-defaults |
| `templates/firstboot.sh` / `setup-rollback.sh` | 状态机 / 回滚 |
| `templates/cgi-bin/*` | 向导 CGI |
| `templates/index.html` | 入口页片段 |
| `templates/minisign-sign.sh` / `notify-discord.py` | 签名 / 通知 |

复制后按项目改 `OWRT_REPO`、Secrets 名、hostname、Discord channel 等。

---

## 十四、实战基线（oasisic-openwrt，2026-07）

| 提交/Run | 含义 |
|----------|------|
| `b0f179d` | 语言修复文档期基线 |
| `a4efa24` | dispatch + persist + 短 Release（历史洗净后） |
| `75a011b` | feeds 钉 commit 改 `^SHA` |
| `275c645` | README 按现状重写 |
| `30098510806` | `;SHA` feeds 失败 |
| `30107519212` | pin `f06b6b44` 全绿 |

Release / cache / last_build 可能被清理后重建——**以仓库当前状态与 Actions 为准**，不要把旧 tag 写死成永远存在。

---

## Completion criteria（本 skill 任务）

改 CI/feeds 后，在结束前必须给出：

1. 相关文件 diff 摘要  
2. `gen-feeds` 两条命令输出  
3. 若已推：`origin/main` tip SHA  
4. 若有失败 run：`gh` 日志关键行（`Remote branch` / `Updating feed`）  
