#!/usr/bin/env python3
"""Lint a commit message against the Conventional Commits format.

Usage:
  python scripts/lint_commit_message.py message.txt
  echo "fix(auth): reject expired tokens" | python scripts/lint_commit_message.py -

Errors (exit code 1):
  - header is not `type(scope)!: subject` with an allowed type
  - header longer than 72 characters
  - no blank line between header and body

Warnings:
  - header longer than 50 characters
  - subject ends with a period, starts with a capital letter, or is not imperative
  - subject is vague ("update", "wip", "fix stuff")
  - body line longer than 72 characters
  - malformed BREAKING CHANGE footer

Merge, revert, fixup and squash commits are skipped.
"""
import re
import sys

TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"]
HEADER_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)\s]+)\))?(?P<bang>!)?: (?P<subject>.+)$")
BAD_FIRST_WORDS = {
    "added", "adds", "adding", "fixed", "fixes", "fixing", "updated", "updates", "updating",
    "removed", "removes", "removing", "changed", "changes", "changing", "implemented",
    "implements", "implementing", "created", "creates", "creating", "refactored", "refactors",
}
VAGUE = {"wip", "fix", "fixes", "update", "updates", "changes", "misc", "stuff", "tmp", "temp", "asdf", "test"}


def lint(message: str):
    errors, warnings = [], []
    lines = message.rstrip("\n").split("\n")
    header = lines[0].strip() if lines else ""

    if re.match(r"^(Merge |Revert \"|fixup! |squash! )", header):
        return [], ["skipped: merge/revert/fixup/squash commit"]

    m = HEADER_RE.match(header)
    if not m:
        errors.append("header must look like `type(scope): subject` (scope optional), e.g. `fix(auth): reject expired tokens`")
    else:
        if m.group("type") not in TYPES:
            errors.append(f"type '{m.group('type')}' is not allowed; use one of: {', '.join(TYPES)}")
        subject = m.group("subject")
        first_word = subject.split()[0].lower()
        if subject.endswith("."):
            warnings.append("subject should not end with a period")
        if re.match(r"^[A-Z][a-z]", subject):
            warnings.append("start the subject with a lowercase letter")
        if first_word in BAD_FIRST_WORDS:
            warnings.append(f"use the imperative mood: '{first_word}' should be e.g. 'add', 'fix', 'update', 'remove'")
        if subject.lower() in VAGUE or len(subject) < 8:
            warnings.append("subject is too vague; say what changed")

    if len(header) > 72:
        errors.append(f"header is {len(header)} characters; keep it at 72 or fewer (ideally 50)")
    elif len(header) > 50:
        warnings.append(f"header is {len(header)} characters; 50 or fewer reads best")

    if len(lines) > 1 and lines[1].strip() != "":
        errors.append("leave a blank line between the header and the body")

    in_fence = False
    for no, line in enumerate(lines[1:], 2):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or line.startswith((" ", "\t")) or "http://" in line or "https://" in line:
            continue
        if len(line) > 72:
            warnings.append(f"line {no} is {len(line)} characters; wrap body lines at about 72")
        if re.match(r"(?i)^breaking[ -]change", line) and not re.match(r"^BREAKING[ -]CHANGE: .+", line):
            warnings.append(f"line {no}: write the footer exactly as `BREAKING CHANGE: description`")
    return errors, warnings


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    text = sys.stdin.read() if argv[1] == "-" else open(argv[1], encoding="utf-8").read()
    errors, warnings = lint(text)
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARNING {w}")
    if not errors and not warnings:
        print("OK: message follows the convention")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
