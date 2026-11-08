#!/usr/bin/env python3
"""Scan a git diff: summarize what changed and flag things worth checking
before you commit or open a pull request.

Usage:
  python scripts/scan_diff.py                  # staged changes (falls back to unstaged)
  python scripts/scan_diff.py main...HEAD      # a range, e.g. this branch vs main
  python scripts/scan_diff.py HEAD~3           # any arguments accepted by `git diff`
  git diff | python scripts/scan_diff.py -     # read a unified diff from stdin

It is advisory: the checks are heuristics. It never prints the value of a
suspected secret, only the file, line number, and kind.

Exit code: 1 if a possible secret was found, otherwise 0 (2 on a git error).
"""
import re
import signal
import subprocess
import sys
from collections import OrderedDict

LARGE_LINES = 400
LARGE_FILES = 15

SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "API secret key"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"(?i)\b(?:password|passwd|secret|token|api[_-]?key)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]"),
     "hardcoded credential"),
]

DEBUG_PATTERNS = [
    (re.compile(r"\bprint\("), "print() call"),
    (re.compile(r"console\.log\("), "console.log call"),
    (re.compile(r"\bdebugger\b"), "debugger statement"),
    (re.compile(r"\bbreakpoint\(\)"), "breakpoint() call"),
    (re.compile(r"\bpdb\.set_trace\(|^\s*import pdb"), "pdb debugger"),
    (re.compile(r"\b(?:TODO|FIXME|XXX)\b"), "TODO/FIXME marker"),
]

DEP_FILES = {
    "requirements.txt", "pyproject.toml", "poetry.lock", "pipfile", "pipfile.lock", "uv.lock",
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "go.mod", "go.sum", "cargo.toml", "cargo.lock", "gemfile", "gemfile.lock",
    "pom.xml", "build.gradle", "build.gradle.kts",
}


def classify(path: str) -> str:
    p = path.lower()
    name = p.rsplit("/", 1)[-1]
    if re.search(r"(^|/)(tests?|__tests__|spec)(/|$)", p) or re.search(r"(_test\.|\.test\.|\.spec\.|^test_)", name):
        return "tests"
    if re.search(r"(^|/)(migrations?|alembic/versions|db/migrate)(/|$)", p):
        return "migrations"
    if p.startswith(".github/workflows/") or name in {".gitlab-ci.yml", "jenkinsfile"}:
        return "ci"
    if name in DEP_FILES or name.startswith("requirements") and name.endswith(".txt"):
        return "dependencies"
    if name.endswith((".md", ".rst", ".txt")) or p.startswith("docs/"):
        return "docs"
    if name.startswith((".env", "dockerfile", "docker-compose")) or name.endswith((".yml", ".yaml", ".toml", ".ini", ".cfg", ".json")):
        return "config"
    return "code"


def parse_diff(text: str):
    files = OrderedDict()
    cur = None
    in_hunk = False
    new_line = 0
    for line in text.splitlines():
        if line.startswith("diff --git "):
            m = re.match(r"diff --git a/(.*?) b/(.*)$", line)
            path = m.group(2) if m else line.split()[-1]
            cur = files.setdefault(path, {"added": 0, "removed": 0, "binary": False,
                                          "new": False, "deleted": False, "lines": []})
            in_hunk = False
            continue
        if cur is None:
            continue
        if line.startswith("@@"):
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", line)
            new_line = int(m.group(1)) if m else 0
            in_hunk = True
        elif in_hunk:
            if line.startswith("+"):
                cur["added"] += 1
                cur["lines"].append((new_line, line[1:]))
                new_line += 1
            elif line.startswith("-"):
                cur["removed"] += 1
            elif line.startswith(" "):
                new_line += 1
        else:
            if line.startswith("new file mode"):
                cur["new"] = True
            elif line.startswith("deleted file mode"):
                cur["deleted"] = True
            elif line.startswith(("Binary files", "GIT binary patch")):
                cur["binary"] = True
    return files


def get_diff(args):
    if args == ["-"]:
        return sys.stdin.read(), ""
    note = ""
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    if inside.returncode != 0:
        print("Not inside a git repository. Run this from your repo, or pipe a diff in:\n"
              "  git diff --staged | python scripts/scan_diff.py -", file=sys.stderr)
        sys.exit(2)
    cmd = ["git", "diff"] + (args if args else ["--staged"])
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        print(f"git error: {out.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    if not out.stdout.strip() and not args:
        out = subprocess.run(["git", "diff"], capture_output=True, text=True)
        note = "Nothing is staged, so this shows UNSTAGED changes."
    return out.stdout, note


def main(argv):
    text, note = get_diff(argv[1:])
    files = parse_diff(text)
    if not files:
        print("No changes found in the diff.")
        return 0

    total_add = sum(f["added"] for f in files.values())
    total_rem = sum(f["removed"] for f in files.values())
    areas = {}
    for path, f in files.items():
        areas.setdefault(classify(path), []).append(path)

    print(f"Files changed: {len(files)} (+{total_add} / -{total_rem})")
    if note:
        print(note)
    print("\nBy area:")
    for area in ("code", "tests", "migrations", "dependencies", "config", "ci", "docs"):
        if area in areas:
            print(f"  {area} ({len(areas[area])}):")
            for p in areas[area]:
                f = files[p]
                tag = " [new]" if f["new"] else " [deleted]" if f["deleted"] else " [binary]" if f["binary"] else ""
                print(f"    {p}  +{f['added']}/-{f['removed']}{tag}")

    flags, secret_found = [], False
    for path, f in files.items():
        area = classify(path)
        base = path.rsplit("/", 1)[-1]
        if base == ".env" or (base.startswith(".env.") and not base.endswith((".example", ".sample", ".template"))):
            flags.append(f"[SECRET FILE] {path} looks like a real env file; do not commit it")
            secret_found = True
        for no, content in f["lines"]:
            for rx, kind in SECRET_PATTERNS:
                if rx.search(content):
                    flags.append(f"[SECRET?] {path}:{no} possible {kind} (value not shown)")
                    secret_found = True
            if area == "code":
                for rx, kind in DEBUG_PATTERNS:
                    if rx.search(content):
                        flags.append(f"[DEBUG?] {path}:{no} {kind}")

    changed = total_add + total_rem
    if changed > LARGE_LINES or len(files) > LARGE_FILES:
        flags.append(f"[LARGE] {changed} changed lines in {len(files)} files; consider splitting into smaller commits or PRs")
    if "code" in areas and "tests" not in areas:
        flags.append("[NO TESTS] code changed but no test files changed")
    if "migrations" in areas:
        flags.append("[MIGRATION] schema change: check it is backward compatible and say how to roll back")
    if "dependencies" in areas:
        flags.append("[DEPENDENCIES] dependency files changed: mention what was added or upgraded and why")
    if "ci" in areas:
        flags.append("[CI] workflow files changed: mention the effect on builds and deployments")
    sensitive = [p for p in files if re.search(r"(auth|security|permission|password|token|session|jwt|oauth)", p.lower())]
    if sensitive:
        flags.append("[SECURITY AREA] touches: " + ", ".join(sensitive[:5]) + ": mention authorization/security impact")
    api = [p for p in files if re.search(r"(route|router|endpoint|controller|openapi|schema|serializer)", p.lower()) and classify(p) == "code"]
    if api:
        flags.append("[API?] possible API surface change in: " + ", ".join(api[:5]) + ": check for breaking changes")

    print("\nFlags:" if flags else "\nFlags: none")
    for fl in flags:
        print(f"  {fl}")

    kinds = set(areas)
    hint = None
    if kinds == {"docs"}:
        hint = "docs"
    elif kinds == {"tests"}:
        hint = "test"
    elif kinds == {"ci"}:
        hint = "ci"
    elif kinds <= {"dependencies", "config"}:
        hint = "build or chore"
    if hint:
        print(f"\nType hint: {hint} (heuristic; confirm from the diff)")
    return 1 if secret_found else 0


if __name__ == "__main__":
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)   # no traceback when piped to head/less
    sys.exit(main(sys.argv))
