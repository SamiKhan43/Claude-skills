---
name: commit-and-pr-writer
description: Write Conventional Commit messages and PR descriptions from a git diff, with a diff scanner and message linter. Use for 'commit message', 'PR description', 'summarize my changes', 'split commits'.
---

# Commit and PR writer

Turn a set of changes into a clear commit message and a pull request description that a reviewer can act on. The value is in saying **why** the change exists and **what could go wrong**, not in restating the diff.

## Safety rules (read first)

- **Do not commit, push, or open a PR unless the user explicitly asks.** Propose the commands and let the user run them. Commits and pushes are visible to others and awkward to undo.
- **Never write secret values into a message or PR.** If the scan flags a possible secret, stop and tell the user before writing anything: the secret must be rotated, and removing it from the next commit is not enough.
- **Do not invent facts.** No issue numbers, test results, benchmark numbers, or motivations that you did not see. If the reason for the change is unclear, ask one short question or state your assumption.

## Workflow

### 1. Gather the changes

If you can run commands in the user's repo, use the bundled scanner first, then read the real diff:

```bash
python scripts/scan_diff.py                  # staged changes (falls back to unstaged)
python scripts/scan_diff.py main...HEAD      # whole branch, for a PR
git diff --staged                            # read the actual diff (use --stat first if it is large)
git log --oneline main..HEAD                 # commits already on the branch, for a PR
```

`scripts/scan_diff.py` groups files by area (code, tests, migrations, dependencies, config, CI, docs) and flags possible secrets, debug leftovers, missing tests, migrations, security-sensitive paths, possible API changes, and oversized changes. It is a heuristic, so confirm each flag against the diff.

If you cannot run commands, ask the user to paste `git diff --staged` (or `git diff main...HEAD` for a PR) and, if relevant, the issue or ticket text. You can still pipe pasted text to the scanner with `python scripts/scan_diff.py -` when code execution is available.

### 2. Understand the intent

Work out what behavior changed and why. Evidence, in order: branch name and ticket id, commit messages already on the branch, new or changed tests, comments near the change, then the user's words. See `references/guidelines.md` section 4.

### 3. Check the scope

If the diff mixes unrelated concerns (a feature plus a refactor plus formatting, or unrelated modules), propose a split instead of writing one vague message: list the groups, which files belong to each, and a message per group, plus the `git add -p` steps. Keep one logical change per commit. If it is already one logical change, write one commit.

### 4. Write the commit message

Format: `type(scope): subject`, then an optional body, then optional footers.

- **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- **Subject:** imperative mood ("add", "fix"), lowercase, no trailing period, about 50 characters and never over 72. Describe the behavior change, not the files.
- **Body:** only when the reason is not obvious. Leave a blank line after the subject, explain **why**, wrap at about 72 characters.
- **Footers:** `Closes #123` (only for numbers you know) and `BREAKING CHANGE: ...` when clients or deployments will break. A `!` after the type or scope also marks a breaking change.

Then check it. Save the message to a temporary file and run:

```bash
python scripts/lint_commit_message.py message.txt
```

Fix every error and sensible warnings before showing it to the user.

### 5. Write the PR description (when asked for a PR)

Start from `assets/pr-template.md`. Fill **What**, **Why**, **How to test**, then keep only the **Backend impact** lines that apply (database and migrations, API changes, security and authorization, performance, config and flags, rollout and rollback) and delete the rest. Rules:

- **Title:** same format as a commit header, because with squash-merge it becomes the commit on `main`.
- **How to test:** exact commands you can justify from the repo (for example the test file you saw changed). Say "tests not run" rather than implying they passed.
- **Breaking changes:** say who is affected, what they must do, and the timeline.
- **Migrations:** say whether old code still works during the deploy and how to roll back.
- Keep it proportionate. A one-line fix needs a two-line PR, not the whole template.

### 6. Present the result

Reply with, in this order:

1. **Heads-up** (only if the scan found something real): secrets, debug code, missing tests, a very large diff, a risky migration.
2. **The commit message** in a code block (or the split plan with one message per commit).
3. **The PR title and description** in a markdown code block, ready to paste. Use four backticks around it if the body contains code fences.
4. **Optional commands** the user can run, for example `git commit -F message.txt` or `gh pr create --title "..." --body-file pr.md`. Present them as suggestions.

Keep the reply short. Do not retell the diff.

## Scale the output to the change

- Typo, docs, or config tweak: a one-line commit, no body, a two-line PR.
- Normal change: header plus a short body, a PR with What / Why / How to test.
- Large or risky change (migration, auth, public API): full PR with the relevant backend impact sections, and suggest splitting if the scan says it is large.

## Example

Input summary: staged diff changes `app/auth.py` to validate `exp`, `iss`, `aud` when decoding tokens, adds `tests/test_auth.py::test_expired_token`, branch `fix/42-expired-tokens`.

Output:

```
fix(auth): reject expired refresh tokens

Tokens were accepted after expiry because exp was decoded but never
validated. Validate exp, iss and aud on every decode and return 401.

Closes #42
```

The PR title would be `fix(auth): reject expired refresh tokens`, with a **Why** that names the bug, **How to test** pointing at `pytest tests/test_auth.py::test_expired_token`, and a **Security / authorization** line saying previously-valid expired tokens now get a 401.

## Bundled files

- `scripts/scan_diff.py`: summarizes a diff and flags risks. Usage: `python scripts/scan_diff.py [git-diff-args | -]`. Exit code 1 means a possible secret was found.
- `scripts/lint_commit_message.py`: checks a message against the Conventional Commits format. Usage: `python scripts/lint_commit_message.py message.txt` (or `-` for stdin). Exit code 1 means errors.
- `assets/pr-template.md`: the PR description skeleton to fill in. It can also be copied to `.github/pull_request_template.md` if the user wants a default template in their repo.
- `references/guidelines.md`: commit types with examples, good and bad messages, breaking changes, how to split diffs, PR sizing, backend PR sections, issue-linking keywords, and what not to write. Read it when a case is not covered above.
