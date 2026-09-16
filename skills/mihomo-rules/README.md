<p align="center">
  <img src="https://raw.githubusercontent.com/MetaCubeX/mihomo/Meta/docs/logo.png" width="80" alt="mihomo logo"/>
  <br/><br/>
  <b>Hermes Agent Skill — Hawaiine/mihomo-rules 维护知识库（Python 管线）</b>
  <br/><br/>
  <img alt="License" src="https://img.shields.io/static/v1?label=license&message=MIT&color=blue&style=flat-square"/>
  <img alt="Hermes Skill" src="https://img.shields.io/static/v1?label=Hermes&message=Skill+v3.0&color=blueviolet&style=flat-square"/>
  <img alt="Project" src="https://img.shields.io/static/v1?label=ref&message=Hawaiine/mihomo-rules&color=blue&style=flat-square"/>
</p>

---

# 🧩 mihomo-rules

**[Hawaiine/mihomo-rules](https://github.com/Hawaiine/mihomo-rules)**  
mihomo / clash-meta **RULE-SET** 规则集 · **116 品牌 · 125 规则集** · 约 32 万+ 规则 · 每日 CI 同步

加载 `SKILL.md` 后，Agent 应掌握：Python 日更管线、命名两线、classical 格式、全/小格式约定、verify 双门禁、CI 滤噪、Push 纪律。

---

## 📂 仓库内容

```
skills/mihomo-rules/
├── README.md    # 本文件（总览）
├── SKILL.md     # Hermes 加载的核心知识（单文件，含全部操作规范）
└── meta.yaml    # 根 README 脚本读取的元数据
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
git clone https://github.com/Hawaiine/Oasisic-Skills.git
# 复制到当前 profile 的 skills 目录
# 例如：cp skills/mihomo-rules/SKILL.md $HERMES_HOME/skills/networking/mihomo-rules/SKILL.md
```

---

## 📋 关键指标

| 模块 | 内容 |
|------|------|
| 口径 | 116 品牌 + 9 兜底 = 125 规则集 |
| 管线 | Python：fetch / parse / merge / write / ownership / generate / verify |
| Ruleset | classical payload、幂等写入、PROCESS 大小写 |
| behavior | 官方 domain/ipcidr/classical；本仓全 classical |
| Config | 子品牌优先 + 字母序、Cloudflare 置底、21 地区成对 |
| full/min | 段间/块间空行约定 |
| CI | daily-sync：滤噪 → 再 commit → 再 Discord |
| Discord | 实时统计；skip vs pushed；HEAD~1 变更统计 |
| 纪律 | 先 diff、说「推」、禁 force、禁假完成 |

### 相对 v2.x 的重大更正

| 旧（过时） | 新（现行） |
|------------|------------|
| `sync-upstream.sh` / `generate-config.sh` | `scripts/*.py` |
| 100「品牌」时代 | **116 品牌 · 125 规则集** |
| 仅域名 → behavior domain | **TYPE,value → classical** |
| rules 直连写 DIRECT | **🎯 全球直连** 别名 |
| 自动选择可含 DIRECT 的旧叙述 | 自动选择挂 **21 地区组**；直连走全球直连 |
| Discord 写死品牌数、规则数 0 | 实时扫描 + 提交后通知 |

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
  <sub>Aligned with mihomo-rules Python pipeline · 2026-08</sub>
</p>
