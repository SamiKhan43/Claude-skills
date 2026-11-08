# Guidelines: commit messages and pull request descriptions

Read this when you need the details behind the rules in SKILL.md: allowed commit types, how to split a messy diff, what a good backend PR says, and examples of good and bad output.

## Contents

1. [Commit types and scopes](#1-commit-types-and-scopes)
2. [Good and bad commit messages](#2-good-and-bad-commit-messages)
3. [Breaking changes](#3-breaking-changes)
4. [Finding the "why" in a diff](#4-finding-the-why-in-a-diff)
5. [Splitting a messy diff into commits](#5-splitting-a-messy-diff-into-commits)
6. [Pull request sizing and titles](#6-pull-request-sizing-and-titles)
7. [What a backend PR should say](#7-what-a-backend-pr-should-say)
8. [Linking issues](#8-linking-issues)
9. [Things not to write](#9-things-not-to-write)

---

## 1. Commit types and scopes

Format: `type(scope): subject`. The scope is optional. Use the lowercase name of the area changed (`auth`, `api`, `db`, `orders`, `ci`, `deps`).

| Type | Use for | Example |
|---|---|---|
| `feat` | A new capability for users or API clients | `feat(api): add cursor pagination to /tasks` |
| `fix` | A bug fix | `fix(auth): reject expired refresh tokens` |
| `docs` | Documentation only | `docs: explain idempotency keys` |
| `style` | Formatting with no behavior change (whitespace, semicolons) | `style: apply ruff format` |
| `refactor` | Restructuring with no behavior change | `refactor(orders): extract repository layer` |
| `perf` | A change made to improve performance | `perf(db): add index on orders.user_id` |
| `test` | Adding or fixing tests only | `test(auth): cover ownership checks` |
| `build` | Build system or dependency changes | `build(deps): upgrade fastapi to 0.115` |
| `ci` | CI configuration and scripts | `ci: run tests against PostgreSQL 16` |
| `chore` | Maintenance that fits nowhere else | `chore: remove unused env variable` |
| `revert` | Reverting an earlier commit | `revert: feat(api): add cursor pagination` |

Choosing between similar types:

- A change that fixes a bug **and** adds a feature is two commits.
- Adding a test for an existing bug fix is `test`. Fixing the bug together with its test is `fix`.
- If behavior changes for the user, it is `feat` or `fix`, never `refactor`.

## 2. Good and bad commit messages

**Header rules**

- Imperative mood: "add", "fix", "remove" (it completes "If applied, this commit will ...").
- About 50 characters, never more than 72. No trailing period. Lowercase after the colon.
- Say **what changed in behavior**, not which files changed.

**Body rules** (only when the header cannot carry the reason)

- Leave one blank line after the header.
- Explain **why** the change was needed and any non-obvious decision. The diff already shows how.
- Wrap lines at about 72 characters.
- Put issue references and `BREAKING CHANGE:` in the footer.

| Bad | Why | Good |
|---|---|---|
| `fix` | Says nothing | `fix(auth): return 401 for expired tokens` |
| `update code` | Vague | `refactor(orders): move pricing rules into a service` |
| `Added pagination.` | Past tense, capital, period | `feat(api): add cursor pagination to /tasks` |
| `fix bug in auth.py and orders.py` | Lists files, mixes concerns | Two commits, one per fix |
| `wip` | Not a finished thought | Squash or reword before sharing |
| `feat: stuff` | Vague subject | `feat(search): rank exact title matches first` |

**A complete example**

```
fix(auth): reject expired refresh tokens

Refresh tokens were accepted after expiry because the exp claim was
decoded but never validated. Validate exp, iss and aud on every decode
and return 401 with a WWW-Authenticate header.

Closes #42
```

## 3. Breaking changes

A breaking change makes existing clients or deployments stop working: a removed endpoint, a renamed field, a changed status code, a new required parameter, a dropped config variable, an incompatible migration.

Mark it in one or both of these ways:

```
feat(api)!: remove the /v1/login endpoint

BREAKING CHANGE: clients must use /v2/login. /v1/login now returns 410.
```

In a PR, also say who is affected, what they must do, and the migration or deprecation timeline.

## 4. Finding the "why" in a diff

The diff shows what changed. To state why, look for evidence in this order:

1. The branch name and any ticket or issue number in it.
2. Recent commit messages on the branch (`git log main..HEAD`).
3. Test changes: a new failing-then-passing test usually names the bug.
4. Comments, docstrings, and TODOs near the change.
5. The user's own description.

If none of these explain the reason, **ask one short question** or write the message with the "why" left out and say so. Do not invent a reason.

## 5. Splitting a messy diff into commits

Split when a diff mixes concerns, because separate commits are easier to review, revert, and bisect. Common splits:

- Formatting or rename-only changes vs. behavior changes.
- A refactor vs. the feature built on top of it.
- Tests vs. implementation (keep them together if they belong to the same fix).
- Unrelated modules or unrelated bug fixes.
- Dependency upgrades vs. the code changes they require (keep together if the build breaks otherwise).

Each commit should leave the project building and the tests passing.

Suggested commands to give the user:

```bash
git add -p                     # stage chosen hunks interactively
git commit -m "refactor(orders): extract pricing service"
git add -p
git commit -m "feat(orders): add bulk discount"
```

Do not run these yourself unless the user asks.

## 6. Pull request sizing and titles

- A good PR has one purpose and is reviewable in one sitting. Roughly under 400 changed lines is comfortable. Above that, suggest splitting.
- Large mechanical changes (renames, formatting, generated files) are fine if they are isolated in their own PR.
- The PR **title** uses the same format as a commit header (`feat(api): add cursor pagination`). With squash-merge, the title becomes the commit message on `main`.
- Write the description for a reviewer who has no context: what changed, why, how to verify, and what could go wrong.
- Keep small PRs small. A typo fix needs one sentence, not the full template.

## 7. What a backend PR should say

Include a section only when it applies, and say "none" in a few words rather than leaving a template line empty.

| Area | Say |
|---|---|
| **Database / migrations** | What tables or columns change, whether old code still works during the deploy (expand and contract), whether the migration locks a large table, how to roll back |
| **API changes** | New or changed endpoints, request and response examples, status codes, error format, whether it is breaking, version or deprecation plan |
| **Security / authorization** | Who can now do what, where ownership checks happen, new inputs and how they are validated, anything touching tokens, passwords, or permissions |
| **Performance** | New queries, indexes added, N+1 risks, caching, expected load |
| **Config / env / flags** | New environment variables and defaults, secrets that must be provisioned, feature flags and their default state |
| **Rollout and rollback** | Deploy order (migration first or code first), how to turn it off, how to revert safely |
| **Testing** | The exact commands and what was verified. Only claim tests pass if you have seen them pass |

## 8. Linking issues

- In a commit footer or PR description, `Closes #123`, `Fixes #123`, or `Resolves #123` closes the issue when the change merges into the default branch.
- `Refs #123` or `Related to #123` links without closing.
- For issues in another repo: `Closes owner/repo#123`.
- Only link an issue number you actually know: from the user, the branch name, or the commits. Never guess one.

## 9. Things not to write

- Restating the diff ("changed line 12 of auth.py").
- Listing every file touched.
- "Should work now", "hopefully fixes", or "tested locally" without evidence.
- Marketing language ("robust", "seamless", "significantly improved") with no numbers.
- Secrets, tokens, internal hostnames, customer data, or credentials, even as examples.
- Claims about performance gains without a measurement.
- Boilerplate sections that say nothing. Delete them instead.
