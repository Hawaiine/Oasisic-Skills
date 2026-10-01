# Intake — 用户图片 → 入库规范化 PNG

专项流程：把用户（Noah）发来的单个品牌 logo + 品牌名，规范化成 Oasisic-Icons 仓库规格、暂存，
并在用户指令下批推。与 `logo-render`（SVG→PNG 85% 填充，mihomo 策略组用）不同——这里是**逐个**把用户图片放进 `icons/<Category>/<Brand>/`。

每次执行前一概先读当前仓库真实状态 + 跑 `ci-validate-icons.py`；处理数字如有疑问以
`scripts/normalize-icons.py` 顶部的 `RADIUS` 常量与 docstring 为准（不凭记忆/旧文档）。

## 用户偏好（始终适用）
- **简洁状态**：给状态=是否可用/待推 push 清单，不要过程复述。
- **diff 确认再提交**：展示具体变更集（增/删/覆盖 + 大小）等用户「推 / 先推」才 `git commit + push`，中途不自动推。
- **图标文件名与策略组/规则集名逐字一致**；改名即目录+文件 rename（删旧增新）。
- **批量不碎片**：多个 intake 先累积，用户触发一次批推，再核对。

## 处理规范（硬数字）
- 输出恰为 **512×512 RGBA**，圆角 **r=115**（本类用 115，不是某些旧文档引用的 99；以 normalize-icons.py 常量为准），四角透明。
- **保留原始底色**：白底保持白，只把四角变透明；不得误把白底擦成透明（白底是资产的一部分）。
- 源 > 512 → LANCZOS 缩到 512；源已是 512 → 只加角掩码。
- **复用仓库 normalizer，不手搓掩码数学**：importlib 加载 `Oasisic-Icons/scripts/normalize-icons.py`，
  `render(im, rounded_mask())`。自己重写同一套数学就是角点/抗锯齿漂移的来源。
- 存盘后 **oxipng 无损压缩**：`level=4, strip=StripChunks.safe(), optimize_alpha=True, color_type_reduction=False`
  （False 必须，降色型会丢 alpha）。模块缺失：`pip install --target /opt/data/.work/pylibs pyoxipng` + `PYTHONPATH`。
  压缩前先备份原文件，并用 PIL 证明像素安全：压缩前后 `alpha 通道 bytes` 与 白底合成后 `RGB bytes` 必须逐字节一致，否则还原。
- 每次保存自检并汇报：`size==512×512`、`mode==RGBA`、四角 alpha==0、`transparent_width ≥ 100`
  （填满的 512 圆角 r=115 首行透明宽约 105；<100 说明角没切掉，先查再说「完成」）、中心像素不透明。

## 置名 / 改名规则
- 新品牌：`icons/<Category>/<Name>/<Name>.png`，先 `mkdir -p` 品牌目录。
- 改名（如 `Discovery-Plus`→`DiscoveryPlus`）：`git rm` 旧目录文件、`git add` 新；纯改名不留 `Brand01` 变体。
- **任何 add/delete/rename 后、报告或 push 前**必须跑同步三件套：`generate-icon-json.sh`、
  `generate-category-readmes.sh`、`ci-validate-icons.py`（gate：PNG 数与 JSON 数一致、每品牌有默认 `<品牌>.png`、无旧式 `-1/-2`、变体零填充）。`surge-icon.json`/分类 README 长期滞后于磁盘，必须重生成。
- 用户只说「新增 X」且只发一张图 → 只处理那一张，**不要臆测第二张**（最大错误来源）。
- 多变体品牌默认保留最低编号为 canonical `Brand.png`，高的为 `Brand01/02…`；普通 intake 不擅自造变体。

## Git 纪律
- 删除用 `git rm -f`，新增/覆盖用 `git add`。
- **覆盖旧默认文件时 index/worktree 可能漂移**：`git rm`+`git add` 后工作树可能不是你以为的字节。汇报前核对真实字节（见下）。
- 每批一个 commit，消息如 `🎬 新增 A、B，清理 C/D 旧变体`。
- 正常批推不 force push；干净 squash 历史。用户明确说「直接提交。先不走pr了」时是显式授权模式，可直推 main，
  **否则一律分支 + PR**；被显式请求时仍每逻辑批一个 commit，并主动建议 squash + force-with-lease，未经授权不重写已推历史。
- 失败成批量回滚：用户偏好 `git reset --hard <baseline>` + `git push --force-with-lease origin main`，而不是连环 `--amend`。

## 核对门禁（每次核对 / 报完成前必做）
push 后**重读磁盘真实文件**核对 size + mtime（`git status` 干净 ≠ 覆盖真的落盘）：
```python
import os, hashlib, time
for p in [ "icons/Media/Bilibili/Bilibili.png", ...]:
    s=os.stat(p); print(p, s.st_size, time.strftime('%b %d %H:%M',time.localtime(s.st_mtime)),
          hashlib.sha256(open(p,'rb').read()).hexdigest()[:12])
```
- 期望入库后约 50KB/512RGBA tile；若有 8 万+ 字节且 old mtime → 覆盖没落盘，重做重推。
- 交叉核对 `raw.githubusercontent.com` 目标项：改名旧路径应 404、新路径 200；并对 push 的 HEAD 逐文件 sha256 read-back 对比本地，报 `READBACK n/n matched`。
- 逐项报 size+符合预期；任何一项不符就明说，不报「全部已推」。

## 坑（每个都花过时间）
- **renamed 而不重生成 JSON/README → 下游 404**：surge-icon 存 raw 路径，只 `git mv` 目录不重生成就指向死链；gate 抓数量不抓路径，只有重生成修路径。
- **默认文件覆盖其实没落盘**：见上，靠 size+mtime 查。
- **绝不写入缓存/臆测的图片字节**：落库后 `vision_analyze` 复核确实是该品牌，不是本会话早前的缓存素材（一次错图重推两次）。
- **无字标 logo 用 vision 验证时别用诱导式提问**（「这是 X 吗」会得到自信的错答）：按「附件位置 ↔ 清单顺序」对应为一级真相；对照仓库已有该品牌文件同家族；亚洲品牌对照官方新闻。提示词保持中性（「识别每个 tile、读出文字」）。
- **覆盖后损伤是批量 commit 时用 reset 而非 amend**。
- **每批押入都含 README 统计同步**：跑 `update-readme-badges.py` 重生成 shields 计数/正文「当前共 N 个」，并核对分类列表合计与 `icon-quality-notes.md` 扫描范围（脚本不更新这两处）。历史遗留：badge 正则曾被写坏（吞引号），验证 badge 行以 `?style=flat-square" alt="...Count">` 结尾。
- **`git rm` 未跟踪路径** → `fatal: pathspec did not match`；`git rm` 只删跟踪文件，未跟踪用 `git add`；半成功的 rm 后重查 `git status`。
- **transparent_width < 100 说明角没切**：非方 strip（宽高比 >~1.8）要先裁到内容、铺在不透明白/深底块上，不得留中间透明带。
- **白底必须保留**：若自检中心是白、四角也是白 → 你把背景擦了。掩码只乘 alpha，绝不碰 RGB。
- **Discord 缩略图缓存**：改完推了校正图，聊天里可能还显示旧图——以 raw GitHub URL 为准，不信聊天缩略图。

## 脚本
- `scripts/intake_normalize.py`：`python3 intake_normalize.py <src> <repo> <category> <brand>`，输出自检 dict；不打印 `SELF-CHECK PASS` 就不要 commit。
- 仓库根：`generate-icon-json.sh`（磁盘→JSON）、`generate-category-readmes.sh`（分类清单）、`ci-validate-icons.py`（门禁）、`normalize-icons.py`（共享规范化，import 其 render/rounded_mask 而非重写）。