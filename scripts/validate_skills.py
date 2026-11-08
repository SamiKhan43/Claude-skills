#!/usr/bin/env python3
"""Validate every skill in ./skills.

Errors (exit code 1):
  - SKILL.md missing, or frontmatter missing/unparseable
  - `name` or `description` missing/empty
  - `name` not lowercase-kebab-case, or not equal to the folder name
  - a file referenced from SKILL.md (references/..., assets/..., scripts/...) that does not exist

Warnings:
  - SKILL.md longer than 500 lines
  - description shorter than 60 characters (too vague to trigger reliably)
  - description longer than 200 characters (claude.ai upload limit)
  - skill not mentioned in README.md

Usage:
  python scripts/validate_skills.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_RE = re.compile(r"`((?:references|assets|scripts)/[\w./-]+)`")


def parse_frontmatter(text: str):
    """Return (dict, error). Uses PyYAML if installed, otherwise a simple parser."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "SKILL.md must start with a '---' frontmatter block"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None, "frontmatter block is not closed with '---'"
    block = "\n".join(lines[1:end])
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(block)
        if not isinstance(data, dict):
            return None, "frontmatter is not a key: value mapping"
        return data, None
    except ImportError:
        data = {}
        for line in lines[1:end]:
            m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
            if m:
                data[m.group(1)] = m.group(2).strip().strip("\"'")
        return data, None
    except Exception as exc:  # YAML syntax error
        return None, f"frontmatter is not valid YAML: {exc}"


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print("No skills/ directory found.")
        return 1

    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    errors = warnings = 0
    skills = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))

    if not skills:
        print("No skills found in skills/.")
        return 1

    for folder in skills:
        problems, notes = [], []
        skill_md = folder / "SKILL.md"
        if not skill_md.exists():
            problems.append("missing SKILL.md")
        else:
            text = skill_md.read_text(encoding="utf-8")
            data, err = parse_frontmatter(text)
            if err:
                problems.append(err)
            else:
                name = str(data.get("name") or "").strip()
                desc = str(data.get("description") or "").strip()
                if not name:
                    problems.append("frontmatter is missing 'name'")
                else:
                    if not NAME_RE.match(name):
                        problems.append(f"name '{name}' must be lowercase letters, digits and hyphens")
                    if name != folder.name:
                        problems.append(f"name '{name}' does not match folder '{folder.name}'")
                if not desc:
                    problems.append("frontmatter is missing 'description'")
                elif len(desc) < 60:
                    notes.append("description is very short; add what it does and when to use it")
                elif len(desc) > 200:
                    notes.append(f"description is {len(desc)} characters; claude.ai uploads allow at most 200 (Claude Code allows more)")
            n_lines = len(text.splitlines())
            if n_lines > 500:
                notes.append(f"SKILL.md has {n_lines} lines; move detail into references/")
            for ref in sorted(set(REF_RE.findall(text))):
                if not (folder / ref).exists():
                    problems.append(f"SKILL.md mentions '{ref}' but the file does not exist")
        if readme and folder.name not in readme:
            notes.append("not mentioned in README.md (add a row to the Skills table)")

        status = "OK" if not problems else "ERRORS"
        print(f"{folder.name}: {status}")
        for p in problems:
            print(f"  ERROR   {p}")
        for n in notes:
            print(f"  WARNING {n}")
        errors += len(problems)
        warnings += len(notes)

    print(f"\n{len(skills)} skill(s) checked: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
