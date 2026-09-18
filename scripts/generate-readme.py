#!/usr/bin/env python3
"""
Generate Oasisic-Skills root README.md from skills/*/meta.yaml.

Rewrites only the auto-generated block between:
  <!-- SKILLS-TABLE:START -->
  ...
  <!-- SKILLS-TABLE:END -->

and writes the suggested GitHub repository description to .github/description.txt.
Everything outside those markers is preserved.

Output is deterministic — running this script twice produces byte-identical
files, so CI can safely use it as a sync gate.
"""

from pathlib import Path

try:
    import yaml
except ImportError:  # minimal fallback if PyYAML is absent (CI installs it)
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
README_PATH = ROOT / "README.md"
DESCRIPTION_PATH = ROOT / ".github" / "description.txt"

START_MARKER = "<!-- SKILLS-TABLE:START -->"
END_MARKER = "<!-- SKILLS-TABLE:END -->"
GENERATED_AT_PREFIX = "<!-- GENERATED-AT:"

STATUS_EMOJI = {"active": "✅", "wip": "🚧", "deprecated": "🗄️"}

REQUIRED_FIELDS = ["name", "title", "summary_zh", "summary_en", "status", "tags"]


def parse_meta(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(text) or {}

    # Fallback parser: single-line `key: value` only. Multi-line YAML values
    # (`>` / `|`) would be silently mis-parsed, so warn loudly when seen.
    data = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.endswith(("|", ">")) or stripped.endswith(("|-", ">-")):
            print(f"[generate-readme] ⚠ {path.name}: 检测到多行 YAML 值，PyYAML 缺失时会被误解析，请 pip install pyyaml")
        if ":" not in line or line.startswith(("  ", "-", "#")):
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key == "tags":
            data[key] = [v.strip() for v in value.strip("[]").split(",") if v.strip()]
        else:
            data[key] = value
    return data


def validate_meta(data: dict, path: Path) -> None:
    missing = [k for k in REQUIRED_FIELDS if not data.get(k)]
    if missing:
        print(f"[generate-readme] ⚠ {path.name}: 缺少字段：{', '.join(missing)}")
    if not data.get("upstream_repo") and not data.get("source_note"):
        print(f"[generate-readme] ⚠ {path.name}: 既无 upstream_repo 也无 source_note，来源无法追溯")


def load_skills() -> list:
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    for meta_path in sorted(SKILLS_DIR.glob("*/meta.yaml")):
        data = parse_meta(meta_path)
        validate_meta(data, meta_path)
        if data.get("status") == "deprecated":
            continue
        skills.append({
            "name": data.get("name", meta_path.parent.name),
            "title": data.get("title", meta_path.parent.name),
            "short_name": data.get("short_name", ""),
            "summary_zh": data.get("summary_zh", ""),
            "summary_en": data.get("summary_en", ""),
            "status": data.get("status", "active"),
            "version": data.get("version", ""),
            "tags": data.get("tags", []) or [],
            "upstream_repo": (data.get("upstream_repo") or "").strip(),
            "source_note": data.get("source_note", ""),
        })
    return sorted(skills, key=lambda s: s["name"])


def source_cell(skill: dict) -> str:
    """Source column: upstream repo as a readable link, else the in-repo path."""
    repo = skill["upstream_repo"]
    if repo:
        slug = repo.rstrip("/").split("github.com/", 1)[-1]
        return f"[{slug}]({repo})"
    return f"`skills/{skill['name']}/`"


def render_table(skills: list) -> str:
    lines = [
        "| Skill | Summary | Status | Tags | Source |",
        "|-------|---------|--------|------|--------|",
    ]
    for s in skills:
        summary = " / ".join(part for part in [s["summary_zh"], s["summary_en"]] if part)
        tags = ", ".join(s["tags"]) if s["tags"] else "-"
        status = f"{STATUS_EMOJI.get(s['status'], '')} {s['status']}".strip()
        lines.append(f"| {s['title']} | {summary} | {status} | {tags} | {source_cell(s)} |")
    return "\n".join(lines)


def render_description(skills: list) -> str:
    names = [s["short_name"] or s["name"] for s in skills]
    return f"🧩 Oasisic Skills · {len(skills)} 个 Hermes Agent Skill 合集（{' / '.join(names)}）"


def inject(readme_path: Path, block: str) -> None:
    text = readme_path.read_text(encoding="utf-8")
    if START_MARKER not in text or END_MARKER not in text:
        raise SystemExit("Missing SKILLS-TABLE markers in README.md")
    before, rest = text.split(START_MARKER, 1)
    after = rest.split(END_MARKER, 1)[1]
    # Drop any legacy GENERATED-AT line so the output stays deterministic.
    after = "\n".join(
        line for line in after.splitlines() if not line.strip().startswith(GENERATED_AT_PREFIX)
    )
    readme_path.write_text(
        before + START_MARKER + "\n" + block + "\n" + END_MARKER + after,
        encoding="utf-8",
    )


def main() -> None:
    if not yaml:
        print("[generate-readme] ⚠ PyYAML 未安装，回退到内置简化解析器（pip install pyyaml 更可靠）")
    skills = load_skills()
    inject(README_PATH, render_table(skills))
    DESCRIPTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    DESCRIPTION_PATH.write_text(render_description(skills) + "\n", encoding="utf-8")
    print(f"[generate-readme] updated README with {len(skills)} skills")
    print(f"[generate-readme] wrote description: {DESCRIPTION_PATH.read_text(encoding='utf-8').strip()}")


if __name__ == "__main__":
    main()