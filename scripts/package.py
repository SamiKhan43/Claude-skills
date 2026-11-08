#!/usr/bin/env python3
"""Package each skill in ./skills into dist/<name>.skill (a zip archive).

Usage:
  python scripts/package.py                 # package every skill
  python scripts/package.py my-skill        # package one skill

The archive contains a single top-level folder named after the skill, which is
the layout claude.ai expects for uploaded skills.
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
DIST_DIR = ROOT / "dist"
SKIP_PARTS = {"__pycache__", ".git", ".DS_Store"}


def package(folder: Path) -> Path:
    DIST_DIR.mkdir(exist_ok=True)
    out = DIST_DIR / f"{folder.name}.skill"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(folder.rglob("*")):
            if path.is_dir() or SKIP_PARTS & set(path.parts) or path.suffix == ".pyc":
                continue
            zf.write(path, Path(folder.name) / path.relative_to(folder))
    return out


def main(argv) -> int:
    wanted = set(argv[1:])
    folders = [p for p in sorted(SKILLS_DIR.iterdir()) if (p / "SKILL.md").exists()]
    if wanted:
        folders = [p for p in folders if p.name in wanted]
    if not folders:
        print("No matching skills found.")
        return 1
    for folder in folders:
        print(f"packaged {package(folder)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
