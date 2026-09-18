# 🤝 Contributing to Oasisic-Skills

> 🇨🇳 中文在前，🇬🇧 English below.

---

## 🇨🇳 新增一个 Skill

1. 建目录 `skills/<skill-name>/`，至少包含三件套：

   | 文件 | 必需 | 说明 |
   |------|------|------|
   | `SKILL.md` | ✅ | 给 Agent 读的执行知识；frontmatter 的 `name` **必须**与目录名一致 |
   | `README.md` | ✅ | 给人读的说明：这是什么 / 结构 / 用法 / 关键点（优先中英双语） |
   | `meta.yaml` | ✅ | 仓库元数据，驱动根 README 生成 |

2. `meta.yaml` 字段：

   ```yaml
   name: skill-name              # 必须等于目录名
   short_name: "中文短名"         # 用于仓库描述，4-8 字
   title: "🎯 skill-name"         # 技能清单里显示的名称（可带 emoji）
   summary_zh: "一句话中文简介"
   summary_en: "One-line English summary"
   status: active                # active / wip / deprecated
   version: "1.0.0"              # semver
   tags: [tag1, tag2]
   upstream_repo: ""             # 有上游仓库时填 URL
   source_note: "归档说明"        # upstream_repo 为空时必填，说明来源
   ```

   > `upstream_repo` 与 `source_note` **至少填一个**，保证来源可追溯。

3. 刷新生成物：

   ```bash
   python scripts/generate-readme.py
   git diff --stat -- README.md .github/description.txt
   ```

4. 提交前确认暂存内容，再 commit / push：

   ```bash
   git add -A
   git diff --cached --stat    # 不该提交的（缓存、临时脚本）先撤出
   ```

---

## 🇨🇳 更新一个 Skill

1. 先读当前 `SKILL.md` / `README.md` / `meta.yaml` 的**实际内容**。
2. 输出修改计划（目标 / 影响范围 / 关键变更 / 验证方式），确认后再动手。
3. 只写入经过验证的真实信息；不确定的标注「待验证」或不写。
4. 变更最小化，不顺手修改无关内容。
5. 完成后验证格式与引用一致性（链接可达、名称三处一致）。

---

## 🇨🇳 红线

- ❌ 手改根 README 里自动生成的技能清单（交给脚本）
- ❌ `SKILL.md` 的 `name`、目录名、`meta.yaml` 的 `name` 三处不一致
- ❌ 凭记忆直接改、有 Skill 不加载、修一个漏一个
- ❌ 把未验证的信息写进 Skill
- ❌ 未确认 diff 就 commit / push

---

## 🇬🇧 Adding a new skill

1. Create `skills/<skill-name>/` with `SKILL.md`, `README.md`, and `meta.yaml`.
   The `name` in `SKILL.md` frontmatter **must** match the directory name.
2. Fill `meta.yaml` (see the field table above); provide either `upstream_repo` or `source_note`.
3. Run `python scripts/generate-readme.py` and commit the refreshed `README.md` / `.github/description.txt` together with your changes.
4. Check `git diff --cached --stat` before committing — never stage caches or scratch scripts.

## 🇬🇧 Updating an existing skill

1. Read the actual `SKILL.md` / `README.md` / `meta.yaml` first.
2. Post a change plan (goal / blast radius / key edits / how it will be verified) before editing.
3. Write only verified information; mark anything uncertain as "unverified" or leave it out.
4. Keep the diff minimal — no drive-by edits.
5. Verify formatting and cross-references afterwards (links resolve, names aligned).

## 🇬🇧 Rules

- Do not hand-edit the auto-generated skills table.
- Keep every skill self-contained under `skills/<skill-name>/`.
- Update generated artifacts via the script, not by hand.
- Never commit unverified content or unconfirmed diffs.