#!/usr/bin/env python3
"""Skill 身份一致性校验（只读，不生成任何文件）

规则（唯一契约）：
    skills/<dir>/ 目录名 == SKILL.md frontmatter `name` == meta.yaml `name`

另校验：
    - SKILL.md 存在且带 frontmatter（name + description）
    - README.md 存在
    - root README 的 SKILLS-TABLE 行数与参与生成的 skill 数一致（不产生第二份名字映射）
    - SKILL.md 里引用的 references/xxx.md 真实存在；references/ 下每个文件都被引用到

不做：不维护第二份 skill 名单、不做名字映射、不改写任何文件。

用法：
    python3 scripts/validate-skill-identity.py [--root DIR]

退出码：0 = 全部一致；1 = 存在不一致。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT_DEFAULT = Path(__file__).resolve().parent.parent
SKILLS_DIR_NAME = "skills"
START_MARKER = "<!-- SKILLS-TABLE:START -->"
END_MARKER = "<!-- SKILLS-TABLE:END -->"

NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
# 只匹配“本 skill 的本地 references/ 相对路径”，不匹配上游 docs/references/ 文档路径
REF_RE = re.compile(r"(?<![A-Za-z0-9_/])references/([A-Za-z0-9._\-]+\.md)")


def frontmatter(text: str) -> str | None:
    """返回 SKILL.md 的 YAML frontmatter 文本（无则 None）。"""
    if not text.startswith("---"):
        return None
    rest = text.split("\n", 1)[1] if "\n" in text else ""
    for line in rest.splitlines():
        if line.strip() == "---":
            return rest.split(line, 1)[0]
    return None


def frontmatter_name(text: str) -> str | None:
    fm = frontmatter(text)
    if fm is None:
        return None
    # frontmatter 的顶层 name（缩进行是嵌套字段，忽略）
    for line in fm.splitlines():
        if line.startswith((" ", "\t", "-", "#")):
            continue
        m = NAME_RE.match(line)
        if m:
            return m.group(1).strip().strip("\"'")
    return None


def file_name(path: Path) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith((" ", "\t", "-", "#")):
            continue
        m = NAME_RE.match(line)
        if m:
            return m.group(1).strip().strip("\"'")
    return None


def validate_one(d: Path, root: Path, errs: list[str]) -> None:
    rel = d.relative_to(root).as_posix()
    skill_md, meta, readme = d / "SKILL.md", d / "meta.yaml", d / "README.md"

    if not skill_md.is_file():
        errs.append(f"{rel}: 缺少 SKILL.md（固定入口文件名，不得改名）")
        return
    if not readme.is_file():
        errs.append(f"{rel}: 缺少 README.md")
    if not meta.is_file():
        errs.append(f"{rel}: 缺少 meta.yaml")
        return

    text = skill_md.read_text(encoding="utf-8")
    if frontmatter(text) is None:
        errs.append(f"{rel}/SKILL.md: 缺少 YAML frontmatter（--- ... ---）")
    elif "description:" not in frontmatter(text):
        errs.append(f"{rel}/SKILL.md: frontmatter 缺少 description")
    fm_name = frontmatter_name(text)
    if not fm_name:
        errs.append(f"{rel}/SKILL.md: frontmatter 缺少顶层 name")

    dir_name = d.name
    if fm_name and fm_name != dir_name:
        errs.append(f"目录名与 frontmatter.name 不一致：{rel}/ 目录名={dir_name} != "
                    f"SKILL.md name={fm_name}")
    meta_name = file_name(meta)
    if not meta_name:
        errs.append(f"{rel}/meta.yaml: 缺少顶层 name")
    elif meta_name != dir_name:
        errs.append(f"目录名与 meta.yaml.name 不一致：{rel}/ 目录名={dir_name} != "
                    f"meta.yaml name={meta_name}")

    # references/ 双向一致：SKILL.md 引用的必须存在；存在的必须被引用
    refs = d / "references"
    on_disk = sorted(p.name for p in refs.glob("*.md")) if refs.is_dir() else []
    referenced = sorted(set(REF_RE.findall(text)) | set(REF_RE.findall(
        readme.read_text(encoding="utf-8") if readme.is_file() else "")))
    for name in referenced:
        if name not in on_disk:
            errs.append(f"{rel}: SKILL.md/README 引用了不存在的 references/{name}")
    for name in on_disk:
        if name not in referenced:
            errs.append(f"{rel}: references/{name} 存在但未被 SKILL.md/README 引用")


def check_root_readme(root: Path, skill_count: int, errs: list[str]) -> None:
    readme = root / "README.md"
    if not readme.is_file():
        errs.append("仓库根缺少 README.md")
        return
    text = readme.read_text(encoding="utf-8")
    if START_MARKER not in text or END_MARKER not in text:
        errs.append("README.md 缺少 SKILLS-TABLE 标记，无法与 meta.yaml 同步")
        return
    block = text.split(START_MARKER, 1)[1].split(END_MARKER, 1)[0]
    rows = [ln for ln in block.splitlines() if ln.strip().startswith("|")]
    data_rows = [ln for ln in rows if not set(ln) <= set("|-: ")]
    # 首行是表头，其余为数据行
    data_rows = [ln for ln in data_rows if "Skill | Summary" not in ln and "---" not in ln]
    if len(data_rows) != skill_count:
        errs.append(f"README SKILLS-TABLE 行数={len(data_rows)} != skills/ 下 skill 数="
                    f"{skill_count}（请运行 python scripts/generate-readme.py）")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Skill 身份一致性校验（目录名 == SKILL.md name == meta.yaml name）")
    parser.add_argument("--root", default=str(ROOT_DEFAULT), help="仓库根目录")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    skills_dir = root / SKILLS_DIR_NAME
    dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.is_dir() else []
    if not dirs:
        print(f"  ✗ 未找到任何 skill 目录：{skills_dir}")
        return 1

    errs: list[str] = []
    for d in dirs:
        validate_one(d, root, errs)
    check_root_readme(root, len(dirs), errs)

    for e in errs:
        print(f"  ✗ {e}")
    if errs:
        print(f"  Skill 身份校验：FAIL（{len(errs)} 项不一致）")
        return 1
    print(f"  ✓ Skill 身份校验：PASS（{len(dirs)} 个 skill：目录名 == SKILL.md name == meta.yaml name）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
