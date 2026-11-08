#!/usr/bin/env python3
"""Validate markdown study guides.

Checks (errors fail the run, warnings are advice):
  ERROR   a link to #anchor (same file or another .md file) that does not exist
  ERROR   a relative link to a file that does not exist
  ERROR   an unclosed code fence
  WARNING Mermaid flowchart labels that are likely to break rendering
  WARNING Mermaid sequence messages containing ';' or '#'
  WARNING leftover chat phrases near the end of the file
  WARNING likely secrets, and a few stale/unsafe patterns worth a second look

Usage:
  python scripts/check_guide.py main.md guide-a.md guide-b.md
  python scripts/check_guide.py .            # every .md file in a folder (not recursive)

Exit code: 1 if any error was found, otherwise 0.
"""
import re
import sys
from pathlib import Path

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

CHAT_LEFTOVERS = [
    "what would you like",
    "if you want, i can",
    "let me know if",
    "i can also generate",
    "would you like me to",
    "do you want me to",
]

SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "looks like an AWS access key"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "looks like a GitHub token"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "looks like an API secret key"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "contains a private key"),
]

STALE_PATTERNS = [
    (re.compile(r"datetime\.utcnow\("), "datetime.utcnow() is deprecated; use datetime.now(timezone.utc)"),
    (re.compile(r"from jose import|python-jose"), "python-jose is poorly maintained; prefer PyJWT"),
    (re.compile(r"from passlib|passlib\.context"), "passlib is unmaintained; prefer pwdlib or argon2-cffi"),
]


def slugify(text: str) -> str:
    """Approximate GitHub's heading-to-anchor rule."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # [text](url) -> text
    text = text.replace("`", "")
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


class Doc:
    def __init__(self, path: Path):
        self.path = path
        self.anchors = set()
        self.links = []          # (line_no, text, target)
        self.errors = []
        self.warnings = []
        self.lines = path.read_text(encoding="utf-8").splitlines()
        self._parse()

    def _parse(self):
        seen = {}
        fence = None             # (marker_char, marker_len, lang, start_line)
        mermaid = None           # (start_line, kind, [lines])
        for no, line in enumerate(self.lines, 1):
            m = FENCE_RE.match(line)
            if m:
                marker, rest = m.group(1), m.group(2).strip()
                if fence is None:
                    fence = (marker[0], len(marker), rest.split()[0] if rest else "", no)
                    if fence[2] == "mermaid":
                        mermaid = (no, None, [])
                    continue
                if marker[0] == fence[0] and len(marker) >= fence[1] and not rest:
                    if mermaid:
                        self._check_mermaid(mermaid)
                        mermaid = None
                    fence = None
                    continue
            if fence is not None:
                if mermaid is not None:
                    mermaid[2].append((no, line))
                self._check_code_line(no, line)
                continue
            h = HEADING_RE.match(line)
            if h:
                slug = slugify(h.group(2))
                n = seen.get(slug, 0)
                seen[slug] = n + 1
                self.anchors.add(slug if n == 0 else f"{slug}-{n}")
            for lm in LINK_RE.finditer(line):
                self.links.append((no, lm.group(1), lm.group(2)))
        if fence is not None:
            self.errors.append(f"line {fence[3]}: code fence opened here is never closed")
        self._check_tail()

    def _check_code_line(self, no, line):
        for rx, msg in SECRET_PATTERNS:
            if rx.search(line):
                self.warnings.append(f"line {no}: {msg}")
        for rx, msg in STALE_PATTERNS:
            if rx.search(line):
                self.warnings.append(f"line {no}: {msg}")

    def _check_mermaid(self, block):
        start, _, body = block
        first = next((l.strip() for _, l in body if l.strip()), "")
        kind = first.split()[0] if first else ""
        if kind in ("flowchart", "graph"):
            for no, line in body:
                for m in re.finditer(r"\b[A-Za-z_]\w*\[([^\]\n]*)\]", line):
                    label = m.group(1)
                    if label[:1] in ('"', "(", "[", "/", "\\", "{"):
                        continue
                    if re.search(r"[()<>\"]", label):
                        self.warnings.append(
                            f"line {no}: mermaid label [{label}] has unquoted ( ) < > characters; wrap it in double quotes")
                for m in re.finditer(r"\b[A-Za-z_]\w*\{([^}\n]*)\}", line):
                    label = m.group(1)
                    if label[:1] != '"' and re.search(r"[()<>]", label):
                        self.warnings.append(
                            f"line {no}: mermaid decision label {{{label}}} has unquoted ( ) < >; wrap it in double quotes")
                for m in re.finditer(r"\|([^|\n]*)\|", line):
                    label = m.group(1)
                    if label[:1] != '"' and re.search(r"[()<>;]", label):
                        self.warnings.append(
                            f"line {no}: mermaid edge label |{label}| has risky characters; wrap it in double quotes")
        elif kind == "sequenceDiagram":
            for no, line in body:
                if "->>" in line or "-->>" in line:
                    msg = line.split(":", 1)[1] if ":" in line else ""
                    if ";" in msg or "#" in msg:
                        self.warnings.append(f"line {no}: mermaid sequence message contains ';' or '#', which can break parsing")

    def _check_tail(self):
        tail = "\n".join(self.lines[-15:]).lower()
        for phrase in CHAT_LEFTOVERS:
            if phrase in tail:
                self.warnings.append(f"near the end: leftover chat phrase '{phrase}' (remove it from the document)")


def check(paths):
    docs = {}

    def load(p: Path) -> Doc:
        key = p.resolve()
        if key not in docs:
            docs[key] = Doc(p)
        return docs[key]

    errors = warnings = 0
    for p in paths:
        doc = load(p)
        for no, text, target in doc.links:
            if re.match(r"^(https?:|mailto:|tel:)", target):
                continue
            file_part, _, frag = target.partition("#")
            if file_part == "":
                if frag and frag not in doc.anchors:
                    doc.errors.append(f"line {no}: link '#{frag}' does not match any heading in this file")
                continue
            tgt = (p.parent / file_part).resolve()
            if not tgt.exists():
                doc.errors.append(f"line {no}: linked file '{file_part}' does not exist")
                continue
            if frag and tgt.suffix.lower() == ".md":
                other = load(tgt)
                if frag not in other.anchors:
                    doc.errors.append(f"line {no}: '{file_part}#{frag}' does not match any heading in {file_part}")
        status = "OK" if not doc.errors else "ERRORS"
        print(f"{p}: {status} ({len(doc.errors)} errors, {len(doc.warnings)} warnings, {len(doc.anchors)} headings, {len(doc.links)} links)")
        for e in doc.errors:
            print(f"  ERROR   {e}")
        for w in doc.warnings:
            print(f"  WARNING {w}")
        errors += len(doc.errors)
        warnings += len(doc.warnings)
    print(f"\nTotal: {errors} errors, {warnings} warnings")
    return 1 if errors else 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    paths = []
    for arg in argv[1:]:
        p = Path(arg)
        if p.is_dir():
            paths.extend(sorted(p.glob("*.md")))
        else:
            paths.append(p)
    return check(paths)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
