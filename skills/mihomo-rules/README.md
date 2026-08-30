<p align="center">
  <img src="https://raw.githubusercontent.com/MetaCubeX/mihomo/Meta/docs/logo.png" width="80" alt="mihomo logo"/>
</p>

<h1 align="center">📖 mihomo-rules-skill</h1>

<p align="center">
  <b>Hermes Agent Skill — Hawaiine/mihomo-rules 维护知识库（Python 管线）</b>
</p>

<p align="center">
  <img alt="License" src="https://img.shields.io/static/v1?label=license&message=MIT&color=blue&style=flat-square"/>
  <img alt="Hermes Skill" src="https://img.shields.io/static/v1?label=Hermes&message=Skill+v3.0&color=blueviolet&style=flat-square"/>
  <img alt="Project" src="https://img.shields.io/static/v1?label=ref&message=Hawaiine/mihomo-rules&color=blue&style=flat-square"/>
</p>

---

## 🎯 这是什么

**mihomo-rules-skill** 是 [Hermes Agent](https://github.com/NousResearch/hermes-agent) 用的 Skill，服务主仓库：

**[Hawaiine/mihomo-rules](https://github.com/Hawaiine/mihomo-rules)**  
mihomo / clash-meta **RULE-SET** 规则集 · **100 业务品牌 · 107 规则集** · 约 32 万+ 规则 · 每日 CI 同步

加载 `SKILL.md` 后，Agent 应掌握：

- 当前 **Python** 日更管线（`batch_update.py` 等），**不是**旧 shell 脚本
- 命名两线、ruleset classical 格式、**behavior=文件格式**（官方 classical）
- Android / Nikki × full/min 格式与策略组拓扑（🎯 全球直连、21 地区成对）
- verify 双门禁、写入幂等、CI 滤噪、Discord 通知时机
- Push 纪律：先 diff、说「推」再 push、禁 force / `git add -A`

---

## 📂 仓库内容

```
mihomo-rules-skill/
├── README.md    # 本文件
└── SKILL.md     # Hermes 加载的核心知识（单文件）
```

设计：**单 SKILL 可加载**；细节以主仓库代码与官方 wiki 为准。

---

## 🚀 使用方式

### 对话中加载

```
skill_view(name='mihomo-rules')
```

或把本仓库的 `SKILL.md` 装到 Hermes skills 目录后按本地技能名加载。

### 永久安装示例

```bash
git clone https://github.com/Hawaiine/mihomo-rules-skill.git
# 复制到当前 profile 的 skills 目录（路径因安装而异）
# 例如：cp SKILL.md ~/.hermes/skills/networking/mihomo-rules/SKILL.md
```

### 验证

问 Agent：

> mihomo-rules 日更入口脚本是什么？behavior 为什么全是 classical？

应能答出 `batch_update.py`、payload 为 `TYPE,value`、官方 rule-provider 格式等。

---

## 📋 Skill 涵盖（v3.0）

| 模块 | 内容 |
|------|------|
| 口径 | 99 品牌 + 7 兜底 = 106 规则集 |
| 管线 | Python：fetch / parse / merge / write / ownership / generate / verify |
| Ruleset | classical payload、幂等写入、PROCESS 大小写 |
| behavior | 官方 domain/ipcidr/classical；本仓全 classical |
| Config | 全球直连、21 地区成对、手动切换→全球直连、拦截含 REJECT |
| full/min | 段间/块间空行约定 |
| CI | daily-sync：滤噪 → 再 commit → 再 Discord |
| Discord | 实时统计；skip vs pushed；HEAD~1 变更统计 |
| 纪律 | 先 diff、说「推」、禁 force、禁假完成 |

### 相对 v2.x 的重大更正

| 旧（过时） | 新（现行） |
|------------|------------|
| `sync-upstream.sh` / `generate-config.sh` | `scripts/*.py` |
| 105/106「品牌」混用 | **99 品牌 · 106 规则集** |
| 仅域名 → behavior domain | **TYPE,value → classical** |
| rules 直连写 DIRECT | **🎯 全球直连** 别名 |
| 自动选择可含 DIRECT 的旧叙述 | 自动选择挂 **21 地区组**；直连走全球直连 |
| Discord 写死 99、规则数 0 | 实时扫描 + 提交后通知 |

---

## 🔗 关联资源

| 资源 | 链接 |
|------|------|
| 主仓库 | https://github.com/Hawaiine/mihomo-rules |
| mihomo 文档 | https://wiki.metacubex.one/config/ |
| rule-providers | https://wiki.metacubex.one/config/rule-providers/ |
| Oasisic-Icons | https://github.com/Hawaiine/Oasisic-Icons |
| Nikki | https://github.com/nikkinikki-org/OpenWrt-nikki |

---

## 📜 License

MIT License

---

<p align="center">
  <sub>Aligned with mihomo-rules Python pipeline · 2026-07</sub>
</p>
