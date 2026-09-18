# 🧩 Oasisic-Skills

### Hermes Agent Skills Monorepo · Oasisic 技能合集

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Skills](https://img.shields.io/badge/Skills-4-blueviolet.svg)](#-技能清单)
[![README Check](https://github.com/Hawaiine/Oasisic-Skills/actions/workflows/readme-check.yml/badge.svg)](https://github.com/Hawaiine/Oasisic-Skills/actions/workflows/readme-check.yml)

> 🇨🇳 **一套仓库，集中维护 Hawaiine 的 Hermes Agent Skills。**
> 🇬🇧 **One repo to maintain Hawaiine's Hermes Agent Skills.**

---

<!-- SKILLS-TABLE:START -->
| Skill | Summary | Status | Tags | Source |
|-------|---------|--------|------|--------|
| 🤖⚙️ hermes-config-expert | 严格、可验证、可回滚的 Hermes Agent 配置工作流规范 / Strict, verifiable, and rollback-safe Hermes Agent configuration workflow | ✅ active | hermes, configuration, provider, mcp, security | `skills/hermes-config-expert/` |
| 📖 mihomo-rules | mihomo/clash-meta RULE-SET 规则集仓库维护知识库 / Maintenance knowledge base for the mihomo/clash-meta RULE-SET repo | ✅ active | networking, proxy, ruleset, ci, python, sub-brand | [Hawaiine/mihomo-rules](https://github.com/Hawaiine/mihomo-rules) |
| 🏗️ openwrt-ci | OpenWrt 固件 CI/CD 最佳实践与可复用模板 / OpenWrt firmware CI/CD best practices and reusable templates | ✅ active | openwrt, ci, firmware, github-actions, nikki | [Hawaiine/oasisic-openwrt](https://github.com/Hawaiine/oasisic-openwrt) |
| 🥷 stealth-browser-automation | 反爬虫隐身浏览器实战手册：源码级补丁 Chromium 突破 Cloudflare/Turnstile/FingerprintJS / Anti-bot stealth browser playbook: source-patched Chromium for Cloudflare/Turnstile/FingerprintJS | ✅ active | browser, automation, scraping, anti-bot, cloudflare | `skills/stealth-browser-automation/` |
<!-- SKILLS-TABLE:END -->

## 📖 这是什么

Oasisic-Skills 是一个 **Hermes Agent 技能合集仓库**：每个 Skill 独立自洽、可单独安装，同时共享同一套目录规范、元数据与文档生成工具链。

目前收录 4 个 Skill，覆盖四条主线：

- 🤖⚙️ **Hermes 配置** —— Provider / Model / MCP 的改动闭环（备份 → 修改 → 验证 → 回滚）
- 📖 **mihomo 规则集** —— mihomo / clash-meta RULE-SET 仓库的日更管线与校验纪律
- 🏗️ **OpenWrt 固件 CI** —— 五阶段固件流水线、feeds pin、签名与 Release 规范
- 🥷 **反爬浏览器** —— 源码级补丁 Chromium 穿过 Cloudflare / Turnstile / FingerprintJS

A collection of self-contained [Hermes Agent](https://hermes-agent.nousresearch.com/) skills sharing one directory convention, one metadata format, and one documentation toolchain. Each skill installs independently.

---

## 🚀 快速开始

### 对话内临时加载

在 Hermes 对话里直接加载，无需安装：

```bash
skill_view(name='mihomo-rules')
```

### 永久安装

复制到 **当前 profile** 的 skills 目录（可按功能分子目录，例如 `networking/`、`devops/`）：

```bash
# 1) 确认当前 profile 的数据根目录
echo $HERMES_HOME          # 例如 /opt/data

# 2) 复制某个 Skill（示例：mihomo-rules）
cp -r skills/mihomo-rules $HERMES_HOME/skills/networking/mihomo-rules

# 3) 校验：新的会话中应能被自动加载
```

> 💡 `$HERMES_HOME` 是当前 Hermes profile 的数据根目录，不同 profile 的 skills 互不影响。用 `hermes profile` 确认当前 profile。

### 给其他 Agent 用

`SKILL.md` 是单文件、自包含的 agent 知识源，可直接喂给 Claude Code / Cursor / OpenCode / Aider：

```bash
cp skills/stealth-browser-automation/SKILL.md .claude/stealth-browser.md
```

---

## 📁 仓库结构

```
Oasisic-Skills/
├── README.md                  ← 本文件（技能清单由脚本自动同步）
├── CONTRIBUTING.md            ← 新增 / 更新 Skill 的规范与红线
├── LICENSE                    ← MIT
├── scripts/
│   └── generate-readme.py     ← 从 skills/*/meta.yaml 生成技能清单与仓库描述
├── .github/
│   ├── description.txt        ← GitHub 仓库描述（由脚本生成）
│   └── workflows/
│       └── readme-check.yml   ← CI：校验 README / description 与 meta.yaml 同步
└── skills/
    ├── hermes-config-expert/        🤖⚙️ Hermes 配置专家（System Prompt + 5 份参考）
    ├── mihomo-rules/                📖 规则集维护知识库（SKILL.md 单文件加载）
    ├── openwrt-ci/                  🏗️ 固件 CI/CD（SKILL.md + 参考 + 14 个模板）
    └── stealth-browser-automation/  🥷 反爬浏览器（SKILL.md + Docker + 探针）
```

每个 Skill 统一三件套：

| 文件 | 给谁看 | 说明 |
|------|--------|------|
| `SKILL.md` | 🤖 Agent | 执行知识；frontmatter 的 `name` 必须与目录名一致 |
| `README.md` | 👤 人 | 上手说明、结构、用法（优先中英双语） |
| `meta.yaml` | 🛠️ 工具链 | 仓库元数据，驱动上面的技能清单生成 |

---

## 🔗 上游仓库

部分 Skill 是公开仓库的维护知识库，改动前请以这些仓库的当前 `main` 为准：

| 上游仓库 | 内容 |
|----------|------|
| [Hawaiine/mihomo-rules](https://github.com/Hawaiine/mihomo-rules) | mihomo / clash-meta RULE-SET 规则集与日更管线 |
| [Hawaiine/oasisic-openwrt](https://github.com/Hawaiine/oasisic-openwrt) | OpenWrt 固件工程与构建流水线 |
| [Hawaiine/Oasisic-Icons](https://github.com/Hawaiine/Oasisic-Icons) | 品牌图标资源 |
| [Hawaiine/Oasisic-IPTV](https://github.com/Hawaiine/Oasisic-IPTV) | 公开 IPTV 源采集 |

---

## 🤝 贡献

### 新增 Skill

三件套 + 元数据规范见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

### 更新 Skill

修改现有 Skill 前必须确认：

- 📖 先读实际文件与官方文档，禁止凭记忆操作
- 📋 先输出修改计划（目标 / 影响面 / 验证方式），确认后再动手
- ✍️ 只写入经过验证的信息，不确定的标「待验证」或不写
- 🎯 变更最小化，不顺手改无关内容
- 🔁 多变体（full/min、多平台等）一次全处理，禁止改一个漏一个

提交前跑一次生成脚本，CI 会校验同步：

```bash
python scripts/generate-readme.py
git diff --stat -- README.md .github/description.txt   # 有差异就一起提交
```

---

## 📜 License

MIT — 见 [LICENSE](./LICENSE)。