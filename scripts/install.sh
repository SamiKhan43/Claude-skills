#!/usr/bin/env bash
# Link every skill in ./skills into a Claude Code skills folder.
# Usage:
#   ./scripts/install.sh                          # personal skills: ~/.claude/skills
#   ./scripts/install.sh /path/to/project/.claude/skills
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)/skills"
DEST="${1:-$HOME/.claude/skills}"

mkdir -p "$DEST"

count=0
for dir in "$SRC"/*/; do
  [ -f "${dir}SKILL.md" ] || continue          # only real skills
  name="$(basename "$dir")"
  ln -sfn "${dir%/}" "$DEST/$name"
  echo "linked $name -> $DEST/$name"
  count=$((count + 1))
done

echo "Done: $count skill(s) linked into $DEST"
echo "If $DEST did not exist before, restart Claude Code once."
