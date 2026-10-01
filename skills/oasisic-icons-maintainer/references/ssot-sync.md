# SSOT Sync — brands.json 配置层 + 本机安全推送

专项流程：处理 `intake` / `rename` 之外那步常被漏掉的 **`config/brands.json` 层**（文件系统 rename/add 本身不会更新它），
以及在这台 headless 服务器上的**安全 git push / 回读**。两步漏掉很贵。

每次执行先读当前仓库真实状态；CI 门禁里 `Brands SSOT` 与 `生态一致性` 组专门抓这层不同步——生成器三件套不会修它。

## 何时用
- 给某品牌父级加**根图标**（之前有子无根 PNG）。
- 改名 / 新增品牌，且 `config/brands.json` + glossary + `parent_brands_without_icon` 白名单必须随文件系统移动。
- 在本机 headless 上 push Oasisic-Icons 分支：credential-store push + 审批被卡后回读远端 SHA 与 CI 状态。

## 1. brands.json 是第二处 SSOT —— 每次 add/delete/rename 都同步
每品牌存：`id`、`category`、`entity_type`、`parent_brand`、`icon_path`；另有顶层 `parent_brands_without_icon` 白名单，以及 `display_name` 品牌表。
CI 有专门组（`Brands SSOT`/`生态一致性`）检查这层——`generate-icon-json.sh` 等**不修它**。

结构变化必须**同一个 commit**里改：
- **新品牌**：追加条目（`category`/`entity_type`/`parent_brand`/`icon_path = icons/<Cat>/<id>/<id>.png`）。
- **新父级根图标**（≥2 canonical 后代已存在）：`生态一致性` 要求父级真的有根 PNG 在 `icons/<Parent>/`，
  **且**白名单只能存「被引用但无图标」的母公司——父级一旦有真图标，**立刻从 `parent_brands_without_icon` 移除**（留着会 FAIL CI），
  并把每个子 `parent_brand` 指到新 id（例：加 SINA 为根 → Weibo `parent_brand→SINA`，`Sina` 移出白名单）。
- **改名**：改条目 `id` + `icon_path`，以及指向旧 id 的所有 `parent_brand`。
- **Glossary**：有 `generate-brand-glossary.py` 就用，否则手改 `docs/references/brand-glossary.md`（大小写敏感 ASCII 位）；
  顺带核对 `docs/references/brand-ownership-audit.md` 矩阵计数。
- 改完**回读数据**（id→display/category/entity/parent/icon_path）再跑 CI gate。
- 只 rename 了 PNG 并重生成 surge-icon 的改名，会在 `Brands SSOT` 组 FAIL——这节就是防那个。

**brands.json 手改必须字节可复现**：`json.dump(indent=2, ensure_ascii=False)`，末尾恰一个 `\n`，中文显示名不转义。
格式化变了会产生整文件 diff，埋掉逻辑改动、破坏 R100 改名证据。改完确认 `git diff` 只有目标条目行。

### `+` 品牌命名约定
显示名带 `+` 时，identifier/目录/文件用 `Plus`（先例 DisneyPlus / ParamountPlus / AppleFitnessPlus / CATCHPLAYPlus），`display_name` 保留官方 `+`。
加/改前先 grep 仓库确认这约定，不发明一次性例外。id = dir = file 的 `Plus` 后缀必须一致。

## 2. 本机安全 push（credential 坑）
- 正常 `git push origin <branch>` 走 credential store：token 在 `~/.git-credentials`（600，`credential.helper=store`），push clean。
  **绝不在 push URL 里嵌 token，避免命令串里转义 `\.com` 主机名**——那形态会触发安全扫描卡审批。
- push **超时卡在审批**（用户没应答）时不要重试同款 token URL：改从 GitHub API 回读远端分支 HEAD
  （helper：token 取自 `~/.config/gh/hosts.yml`，不打印），检查该 SHA 的 `Validate Icons` run 状态。
  仅当远端落后才清一次 credential 推。报**实际远端 SHA + CI 结论**，而不是「pushed」。
- `~/.git-credentials` 可能已有可用 token；push 前确认它在且 600，而不是重写它。

## 3. CI gate（报完成前跑）
- 本地镜像 `python3 scripts/ci-validate-icons.py`——以脚本输出为准，不写死组数。
- push 后：远端 HEAD SHA == 本地；该 SHA 的 `Validate Icons` 为 success。workflow 在 push 与 pull_request 都触发，查你推的那个 SHA。
- rename 证据：`git diff --name-status` 出 `R100`；改名 PNG 与 `git show HEAD:<旧路径>` sha256 逐字节一致。

> 注意：CI 校验组数**不是常量**，历史上已多次扩容——**不要**在任何文档/报告里写死「N 组 PASS」，
> 每次以 `ci-validate-icons.py` 打印的 `Validation Groups: N / All groups: PASS` 为准。

## Rename 盲区（文件系统 + brands.json 之外的）
- **生成的 README / badge 行按 OLD display_name 匹配**——生成器以显示名做键，改名变了 display 会留陈旧行。
  手改派生行 + 同步 `docs/references/brand-naming-contract.md`（改名在此登记，不只是 diff）。
- **测试套件钉住改名品牌**——grep 整个 test 树找旧 id/display 并更新断言，不删除（大小写校验继续对新名生效）。
- **Consumer blast-radius 用 `search_files` 工具而非 shell `grep`**——超大仓库（mihomo-rules）会让 grep 超时；
  `search_files`（ripgrep）同答案不会超时。也查 consumer 的 `ownership_map.py` SUB_PARENT 里直接旧 id 引用。

## 坑
- **给母公司搬到真根图标却不碰白名单** → `生态一致性`/`Brands SSOT` FAIL：白名单只能存无图标母公司；拿到图标即移除并重指子。
- **以为生成器三件套覆盖 brands.json**——不覆盖：surge-icon + 分类 README 从磁盘重生成，`parent_brand`/`entity_type`/白名单必须同 commit 编辑。
- **token 进 push 命令被拦**——用 credential store；被卡后用 API 回读远端 SHA + CI，而不是再发 token-URL push。
- **`surge-icon.json` 的 `icons` 是 ARRAY 不是 dict**——写 spot-check/去重断言时遍历 list，按每条 `name`/`url` 键；
  dict 形断言（`icons[name]`）静默错。Glossary 表有 `|---|---|` 分隔行——计行/查唯一性时跳过，否则多一行。
- **回读检查要断言你刚写下的字面短语**——改写读或从 body 文件重算检查表；断言失败先 re-grep 主题再下结论。
- **从旧 ref 恢复文件会丢后来新增字段**——`git checkout <ref> -- file` 后，diff 元数据表单（old-ref vs new-ref）
  补回丢掉的东西（如后来 commit 追加的 parent_brand）。