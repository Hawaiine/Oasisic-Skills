# 🥷 Stealth Browser Skill
### 反爬虫隐身浏览器实战手册 · Anti-Bot Stealth Browser Playbook

> **🌐 [English](#english) | [中文](#chinese)**

---

<a id="chinese"></a>

## 🇨🇳 中文介绍

**隐身浏览器技能包** — 一套让 AI Agent 能突破 Cloudflare / Turnstile / FingerprintJS / BrowserScan 等反爬虫检测的完整方案。

> 🎯 **一句话：** Cloudflare 又把你拦在「Just a moment…」那一页了？这份战场上磨出来的手册 + [CloakBrowser](https://pypi.org/project/cloakbrowser/)（源码级补丁 Chromium），帮你穿过层层关卡。
>
> ✅ **80% 的检测站点**只要 `launch(humanize=True)` 一行代码就能过
> 💪 **剩下 20%** 用 Tier-2（住宅代理 + Xvfb 有头模式 + geoip 时区匹配）

### ✨ 四大亮点

| # | 亮点 | 说明 |
|---|------|------|
| 🚀 | **源码级补丁** | 补丁编进 C++ 编译，不是运行时 JS 注入。检测站点看到的是真浏览器 — **因为它就是真的** |
| 🎯 | **双层战术** | Tier-1: `launch(humanize=True)` 一行搞定 80% → Tier-2: 住宅代理 + 有头 + geoip 啃硬骨头 |
| 🔧 | **即装即用探针** | 装完跑 `python scripts/probe.py`，四个检测站自动评分 + 截图，武器有没有问题一眼便知 |
| 🐳 | **Docker 支持** | 多阶段构建，镜像自带 206MB Chromium，无需每台机器下载。`docker run --rm stealth-browser` 一键跑探针 |

### 📦 安装

```bash
mkdir -p stealth && cd stealth
python -m venv .venv && source .venv/bin/activate
pip install cloakbrowser
cloakbrowser install      # ~206MB 二进制，~30s
```

系统依赖（Debian/Ubuntu 一般自带）：`libnss3 libatk-bridge2.0-0 libatk1.0-0 libgbm1 libasound2 xvfb`

CloakBrowser 暴露的是 **Playwright 兼容 API**，已有 Playwright 代码改一行 import 就能迁过来。

### 🏗️ 仓库结构

```
.
├── 📖 README.md                         ← 你正在看
│   （中英双语 · 带表情包 · 上手教程）
├── 📄 PLAYBOOK.md                       ← 单文件 agent 手册
│   （给 Claude Code / Cursor / 任何 AI Agent 直接消费）
├── 📜 LICENSE                            ← MIT
├── 🧪 scripts/
│   └── probe.py                         ← 四站检测探针
├── 📚 references/
│   └── test-targets.md                  ← 检测站点详解 + 基线
└── 🧩 skills/
    └── stealth-browser-automation/       ← Hermes Agent skill 格式
        ├── SKILL.md
        ├── references/test-targets.md
        └── scripts/probe.py
```

### 🎮 快速上手

**Tier-1 — 80% 的站点，无头就行：**

```python
from cloakbrowser import launch

browser = launch(humanize=True)
page = browser.new_page()
page.goto("https://nowsecure.nl/")
print(page.title())
browser.close()
```

**Tier-2 — 硬骨头（全开 CF Bot Management / Turnstile 互动 / DataDome）：**

```python
browser = launch(
    proxy="http://user:pass@residential-host:port",  # 必须是住宅 IP
    geoip=True,        # 时区/locale 跟代理 IP 对齐 + 自动伪造 WebRTC IP
    headless=False,    # Linux 服务器配 Xvfb
    humanize=True,     # 贝塞尔曲线鼠标 + 逐字符打字 + 真实滚动
)
```

无头服务器跑有头模式：`xvfb-run -a python script.py`

### 🐳 Docker 部署

```bash
# 构建镜像（~600MB，含 CloakBrowser 二进制）
docker build -t stealth-browser docker/

# 跑探针（Tier-1）
docker run --rm stealth-browser

# 跑探针（Tier-2）
docker run --rm --shm-size=2g \
  -e XVFB=1 \
  -e PROXY="http://user:pass@residential:port" \
  -e GEOIP=1 \
  stealth-browser

# 持久化浏览器数据（缓存 CF cookies）
docker run --rm -v $PWD/user-data:/user-data \
  -e PERSISTENT_DIR=/user-data \
  stealth-browser python your-script.py
```

> 💡 Docker 优势：镜像自带 206MB stealth Chromium，部署到任何机器都无需重新下载。`--shm-size=2g` 是 Chromium 在容器内跑有头模式的常见需求。

### 🔬 装完先跑探针

```bash
# Tier-1 基线
python scripts/probe.py

# Tier-2 测试
PROXY="http://user:pass@residential:port" GEOIP=1 \
  XVFB=1 xvfb-run -a python scripts/probe.py
```

输出在 `/tmp/cloak-probe/`（`OUT=` 改路径）。

### 🔍 补充检测站（不在探针内，用于深入诊断）

| 站点 | 测试内容 | Tier-1 预期 |
|------|---------|-------------|
| `bot.incolumitas.com` | 结构化 JSON 评分面板 | `intoli` 6/6 OK，仅 `WEBDRIVER: FAIL` |
| `pixelscan.net` | WebRTC + canvas + 字体指纹 | 大部分绿色 |
| `kasadatech.com` | Kasada 机器人检测 | 🟡 Tier-2 也可能失败 |
| `geetest.com/en/demo` | 极验行为分析 | 🟡 可能需要人工介入 |

### 🩺 失败诊断流程

> ⚠️ **关键认知：数据中心 IP 像穿西装去夜店蹦迪 — 衣冠楚楚但一眼假。** CF 在 IP 层就把你 403 了，根本不会让你的浏览器有机会展示指纹。**先诊断再调参！**

```bash
# 1. 查 ASN
curl -s "https://ipinfo.io/$(curl -s https://api.ipify.org)/json" | jq .org
# 数据中心: "AS14061 DigitalOcean" / "AS16509 Amazon"
# 住宅: "AS4837 China Unicom" / "AS7922 Comcast"

# 2. 检查 DOM 有没有 CF challenge iframe
# document.querySelector('iframe[src*="challenges.cloudflare.com"]')
# → null: IP 层拦截，换浏览器没用，必须换 IP
# → 找到 iframe: 挑战层失败，调整 humanize / 有头模式
```

### 🪤 踩坑高亮

| 坑 | 现象 | 解决 |
|----|------|------|
| 🖥️🔧 | FingerprintJS 显示 `Browser Tampering: Yes` | 只看 bot 分的站点能过；不能过的上 Tier-2 |
| 🌐 | 数据中心 IP → CF 直接 403 | **别怪补丁，去拿住宅代理** |
| 🕐 | 时区跟 IP 不匹配 | 永远 `proxy=` + `geoip=True` 一起用 |
| 🎭 | 纯无头 Turnstile 互动验证翻车 | 升 `headless=False` + Xvfb |
| 📸 | 截图看着正常但实际被拦 | 一定要同时检查 `response.status` + 页面正文 |
| 🔒 | Turnstile 在 closed shadow root | 用 `page.frames` 不是 `querySelector` |
| 📁 | `+x` 权限丢失 | 用 `unzip` 而不是 Python `zipfile` |

### 🔗 给不同 Agent 用

| Agent | 用法 |
|-------|------|
| **Hermes Agent** | `cp -r skills/stealth-browser-automation ~/.skills/devops/` |
| **Claude Code / Cursor / Aider** | 把 `PLAYBOOK.md` 喂给 agent，或 `cp PLAYBOOK.md .claude/stealth-browser.md` |
| **任何平台** | `docker run --rm stealth-browser` 直跑探针，无需装 Python |

### 🏠 没预算买代理？住宅 IP 替代方案

- 🏡 **自己家宽带** → SSH SOCKS5: `ssh -D 1080 -N user@home-box` → `proxy="socks5://127.0.0.1:1080"`
- 📱 **手机热点 / 5G** → 大部分运营商移动 IP 被 CF 归类为住宅
- 👨‍👩‍👧 **朋友家 / 第二住处** → 同上 SOCKS5

实在没辙 → IPRoyal 按量付费 ~$2/GB 最便宜。

### 🤔 什么时候不该用 CloakBrowser

- 有 JSON API 的直接打 API → 更快、更轻
- 真的弹出 CAPTCHA → 需要打码服务（2captcha / capsolver）
- 纯 HTTP 抓 JSON → `curl` / `httpx` 就够了
- DataDome / Kasada / 极验 → 有头 + 住宅是**必要但不充分**条件

### 🤝 贡献

踩到清单里没有的坑？发现 tier-2 也搞不定的新站点？欢迎 PR。**贡献关键是具体** — 站点名 + 失败现象 + 修复方法。

---

<a id="english"></a>

## 🇬🇧 English

**Stealth Browser Skill** — A complete anti-bot browsing toolkit for AI agents, combining a source-patched Chromium ([CloakBrowser](https://pypi.org/project/cloakbrowser/)) with a battle-tested two-tier playbook for bypassing Cloudflare, Turnstile, FingerprintJS, BrowserScan, DataDome, and similar anti-bot stacks.

### ✨ Why This Exists

Stock Playwright / Puppeteer / Selenium gets blocked on sites protected by Cloudflare. You swap to `playwright-stealth` — works for a week, then Chrome updates and it breaks. You try `undetected-chromedriver` — same cycle.

**The root cause:** Anti-bot is no longer a 1v1 code game. It's an ML scoring system — browser fingerprint, behavior patterns, IP reputation, TLS fingerprint, all scored together. Patching runtime JS flags only shaves a couple of points.

**CloakBrowser's approach:** Patch at the C++ source level, not at runtime. Detection sites see a *real* browser — because it *is* one.

### 🎮 Quick Start

```bash
pip install cloakbrowser
cloakbrowser install
```

```python
from cloakbrowser import launch
browser = launch(humanize=True)
page = browser.new_page()
page.goto("https://nowsecure.nl/")
print(page.title())
browser.close()
```

### 🐳 Docker (no-Python-setup path)

```bash
docker build -t stealth-browser docker/
docker run --rm stealth-browser                    # tier-1 probe
docker run --rm --shm-size=2g -e XVFB=1 stealth-browser  # headed
```

### 🎯 Two-Tier Strategy

| Tier | Setup | Hit Rate | Targets |
|------|-------|----------|---------|
| **1️⃣** | `launch(humanize=True)` — headless, datacenter IP OK | ~80% | nowsecure.nl, BrowserScan, FingerprintJS demo, generic CF pages |
| **2️⃣** | Residential proxy + Xvfb headed + geoip + humanize | ~95%+ | Full CF Bot Management, Turnstile interactive, DataDome, Kasada |

### 🔬 The Probe

`python scripts/probe.py` runs four canonical detection sites and reports PASS/FAIL:

| Site | Trait | Expected (Tier-1) |
|------|-------|-------------------|
| `nowsecure.nl` | CF + nodriver detection | ✅ PASS |
| `browserscan.net/bot-detection` | Fingerprint surface scan | ✅ PASS (4/4 green) |
| `demo.fingerprint.com/playground` | Commercial fingerprint ML | ✅ Bot: Not detected ⚠️ Tampering: Yes |
| `nopecha.com/demo/cloudflare` | Full CF Bot Management | ❌ FAIL (expected — needs Tier-2) |

### 🔍 Supplementary targets (for deeper diagnosis)

| Target | What it tests | Expected (tier-1) |
|--------|--------------|-------------------|
| `bot.incolumitas.com` | Structured JSON scoreboard | `intoli` 6/6 OK, `WEBDRIVER: FAIL` only |
| `pixelscan.net` | WebRTC + canvas + font fingerprint | Green on most checks |
| `kasadatech.com` | Kasada bot detection | 🟡 May block even with tier-2 |
| `geetest.com/en/demo` | 极验 behavior analysis | 🟡 May need human-in-the-loop |

### 🩺 Triage Flow

```
Target returns 403 / challenge
        │
        ▼
Check ASN ──────────► Datacenter? ──► Need residential proxy
        │
        ▼
Check DOM for CF iframe
  ├── iframe absent + 403 → IP-layer block → **stop tuning browser, change IP**
  └── iframe present → challenge-layer → try headed + humanize + cookies
```

### 🪤 Top Pitfalls

- **`Browser Tampering: Yes`** on FingerprintJS — expected even with C++ patches. Only matters if the target checks tampering.
- **Datacenter IP → instant 403** — CF Bot Management rejects at IP layer before your browser even gets to show its fingerprints.
- **Timezone/IP mismatch** — always pair `proxy=` with `geoip=True`.
- **Headless can fail** Turnstile interactive — upgrade to `headless=False` + Xvfb.
- **Screenshots lie** — always check `response.status` + body text for blocking markers.
- **Turnstile is in closed shadow root** — use `page.frames`, not `querySelector`.
- **`xvfb-run` needs `xauth`** — workaround: start Xvfb directly and set `DISPLAY`.

### 🏠 Free Residential IP Options

1. **Home broadband** → SSH SOCKS5 tunnel → point proxy there
2. **Mobile hotspot / 5G** → carrier IPs are classified residential by CF
3. **Friend's house** → same SOCKS5 trick

### 🧩 Agent Integration

| Agent | How |
|-------|-----|
| **Hermes Agent** | `cp -r skills/stealth-browser-automation ~/.skills/devops/` |
| **Claude Code / Cursor / OpenCode / Aider** | Feed `PLAYBOOK.md` as context |
| **Any platform** | `docker run --rm stealth-browser` — zero setup |

### 🤝 Contributing

Found a site that beats Tier-2? Discovered a pitfall not listed? PRs welcome. **Specificity is key** — site name, failure mode, fix applied.

### 📜 License

MIT — see [LICENSE](../../LICENSE).

### 🙏 Credits

- [CloakBrowser](https://pypi.org/project/cloakbrowser/) — the real hero doing all the heavy lifting. This repo is just its field notes.
- Battle-tested via [Hermes Agent](https://hermes-agent.nousresearch.com) in real-world automation workflows.