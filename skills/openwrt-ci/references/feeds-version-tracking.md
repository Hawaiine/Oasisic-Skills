# Feeds 版本跟踪与 OpenWrt 语法

## 背景

构建用 `feeds.conf.default` 由 `scripts/gen-feeds-conf.sh` 生成。  
**权威源是 CI 调用该脚本的参数与输出**，不是仓库根目录的 `feeds.conf`（根文件常作本地参考，可能与 CI 不一致）。

## OpenWrt `scripts/feeds` 分隔符（P0）

OpenWrt `v25.12.x` `scripts/feeds` → `update_feed_via`：

```perl
($base_branch, $branch) = split(/;/, $src, 2);
($base_commit, $commit) = split(/\^/, $src, 2);
# $branch  → init_branch: git clone --depth 1 --branch
# $commit  → init_commit: clone + fetch + checkout commit
```

| 写法 | 语义 | 适用 |
|------|------|------|
| `src-git name URL;v1.26.1` | branch/tag | 正式版跟踪 |
| `src-git name URL;main` | branch | 跟主线 |
| `src-git name URL^FULL40SHA` | **commit pin** | 钉某次 fix（CI 推荐） |

### 致命错误

```bash
# 把完整 SHA 当 branch 名
src-git nikki https://github.com/nikkinikki-org/OpenWrt-nikki.git;f06b6b448928501e7511bdfb3497b1186d919316
```

```text
fatal: Remote branch f06b6b448928501e7511bdfb3497b1186d919316 not found
```

### 正确 pin

```bash
src-git nikki https://github.com/nikkinikki-org/OpenWrt-nikki.git^f06b6b448928501e7511bdfb3497b1186d919316
```

### 失败表象

- Job：`build`；Step：`配置 feeds…` → failure  
- 后续 qemu / release / persist → skipped  
- **check-upstream 可以是绿的**（已解析完整 SHA），仍会在 feeds 挂  
- 实测失败 run：`30098510806`（head 曾为 `a4efa24`）  
- 修复后成功 run：`30107519212`（head `75a011b`，feeds 过 → 全绿）

### 推荐实现

1. workflow 解析 `nikki_ref`（空=latest tag；可 short sha / branch / tag）→ **完整 40 位 SHA**  
2. `gen-feeds-conf`：第二参匹配 `^[0-9a-f]{40}$` 用 `^`；否则 tag/branch 用 `;`  
3. 验收：

```bash
bash scripts/gen-feeds-conf.sh v25.12.5 f06b6b448928501e7511bdfb3497b1186d919316 | tail -1
# 必须含 ^ 与 40 hex

bash scripts/gen-feeds-conf.sh v25.12.5 v1.26.1 | tail -1
# …;v1.26.1
```

## 版本去重（last_build）

| 项 | 正确做法 |
|----|----------|
| composite | `${OWRT_TAG}_nikki-${NIKKI_SHA}` |
| kernel.org | **仅展示**，勿作 should_build 主信号 |
| 持久化 | `persist-last-build` commit+push；commit 含 `[skip ci]` |
| gitignore | **不要**忽略 `last_build_version` |
| 假持久化 | 仅 job 内 `echo > file` 无回写 → 每次 `SAVED=none` |

删除 `last_build_version` 或清空 Actions cache 后，下一次为「更干净」的冷构建（更慢）。

## Release

- 标签：`oasisic-{owrt_ver}-nikki-{shortsha7}`  
- assets 含 `sha256sums.minisig`  
- 勿仅用 `oasisic-{owrt_ver}`（同版本互相覆盖）

## SHA 解析

优先：

```text
GET /repos/{owner}/{repo}/commits/{ref}
```

回退：`git ls-remote … REF^{}`（附注 tag 剥皮）。  
避免裸 `ls-remote | head -1` 拿到 tag 对象 hash。

## 2026-07 实战锚点（oasisic-openwrt）

| 项 | 值 |
|----|-----|
| 功能基线（语言修复文档期） | `b0f179d` |
| 清洁 CI 落点 | `a4efa24`（force_build / nikki_ref / persist / 短 Release） |
| feeds `^SHA` 修复 | `75a011b` |
| README 现状对齐 | `275c645` |
| `;SHA` 失败 run | `30098510806` |
| pin `f06b6b44` 成功 run | `30107519212` → Release 曾为 `oasisic-25.12.5-nikki-f06b6b4`（可清理后重建） |
| Nikki 示例 commit | `f06b6b448928501e7511bdfb3497b1186d919316`（mojibake fix） |

## 协作纪律（用户约定）

- 用户说「推」才普通 push；默认禁 force  
- 仅明确洗历史时用 `force-with-lease`  
- 优先：先推 → 审 `origin/main` → 问题用可复制提示词  
- 禁止让用户在多个 Agent 间搬运完整 diff  
