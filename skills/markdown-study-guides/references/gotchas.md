# Gotchas: Mermaid, anchors, markdown, and code patterns

Read this when a guide will include diagrams, a table of contents, or code examples.

## Contents

1. [Mermaid rules](#1-mermaid-rules)
2. [Anchor (table of contents) rules](#2-anchor-table-of-contents-rules)
3. [Markdown formatting traps](#3-markdown-formatting-traps)
4. [Teach the safe version: code patterns](#4-teach-the-safe-version-code-patterns)
5. [Suggested learning order for a notes set](#5-suggested-learning-order-for-a-notes-set)

---

## 1. Mermaid rules

Mermaid diagrams break silently when a label contains the wrong character, and the user only sees an error box. Follow these rules:

- **Quote every flowchart label and edge label**: `A["Create session (Redis)"]`, `A -->|"POST /login"| B`. Unquoted parentheses, angle brackets, or quotes inside a label are the most common cause of broken diagrams.
- Database cylinders use `[("Label")]`. Decisions use `{"Label?"}`.
- **Sequence diagrams**: avoid `;` and `#` inside message text (they are treated as separators or comments). Keep messages short and plain, for example `C->>AS: Exchange code for tokens`.
- Do not write `<jwt>` or any `<tag>` in labels. Write `(jwt)` inside a quoted label, or describe it in words.
- Node IDs are single words (`A`, `AuthServer`). Put the human text in the label.
- `gitGraph` and `erDiagram` are fine for Git and schema guides. In `erDiagram`, write attributes as `type name PK` and relationship labels as a single word or a quoted phrase.
- Keep diagrams small (under about 10 nodes). If it needs more, split it.
- A diagram supports the text. It never replaces an explanation.

## 2. Anchor (table of contents) rules

GitHub builds an anchor from a heading by: lowercasing, removing punctuation (everything except letters, digits, spaces, hyphens, underscores), and replacing spaces with hyphens. Duplicate headings get `-1`, `-2` suffixes.

| Heading | Anchor |
|---|---|
| `## 7. OAuth 2.0` | `#7-oauth-20` |
| `## 6. .gitignore and files you must never commit` | `#6-gitignore-and-files-you-must-never-commit` |
| `## 14. GitHub Actions and CI/CD` | `#14-github-actions-and-cicd` |
| `## 8. OPTIONS method and CORS` | `#8-options-method-and-cors` |
| `## 24. Full example: a small REST API (FastAPI)` | `#24-full-example-a-small-rest-api-fastapi` |

Tips:

- Number the headings. Numbers make anchors unique and predictable.
- Avoid slashes, colons, and parentheses in headings you plan to link to. They are removed, which makes the anchor easy to get wrong. Prefer "and" over "/".
- Always run `scripts/check_guide.py` after editing headings or links.
- Do not link to a heading inside a code block. Lines starting with `#` inside code fences are comments, not headings.

## 3. Markdown formatting traps

- To show a code block that itself contains triple backticks (for example a template), wrap it in **four** backticks.
- Tables need a header separator row (`|---|---|`). A pipe inside a table cell must be escaped (`\|`) or moved out of the table.
- Leave a blank line before lists, tables, and code fences.
- Put a language after the opening fence (` ```python `, ` ```bash `, ` ```sql `, ` ```http `, ` ```yaml `, ` ```mermaid `) for syntax highlighting.
- Use `http` fences for raw HTTP messages, `text` for plain output.
- Use checkboxes (`- [ ]`) only for real checklists.
- Keep line length reasonable inside code blocks (about 100 characters) so they do not scroll sideways.
- If a document will be read on GitHub, avoid raw HTML.

## 4. Teach the safe version: code patterns

When an example touches one of these areas, write the safe version and say why in a comment or a nearby sentence.

| Area | Safe version |
|---|---|
| Passwords | Argon2id (pwdlib or argon2-cffi), or bcrypt. Never plain text, MD5, or plain SHA-256 |
| JWT in Python | PyJWT with a pinned `algorithms=[...]`, validate `exp`, `iss`, `aud`. Not python-jose |
| Time | Timezone-aware UTC (`datetime.now(timezone.utc)`), not `utcnow()`. Store UTC in the database |
| Secrets | Read from environment variables or a secret manager. Never hardcode, never commit |
| SQL | Parameterized queries. Never f-strings or concatenation |
| Money | `NUMERIC` or integer minor units. Never float |
| Cookies | `HttpOnly`, `Secure`, `SameSite`, short lifetime |
| CORS | Explicit allowlist. Never `*` with credentials, never reflect `Origin` blindly |
| Authorization | Ownership check inside the query. Never trust a client-supplied `user_id` |
| Retries | Only for idempotent requests, with exponential backoff and jitter, and timeouts on every outgoing call |
| Git | `--force-with-lease`, never force-push shared branches. Rotate leaked secrets before scrubbing history |
| GitHub Actions | Minimal `permissions:`, secrets in GitHub Secrets, pin third-party actions |
| Docker | Pin base image versions, do not run as root where avoidable, no secrets in images |

Also remember: examples must be coherent. If the guide sets a cookie, the code that reads the token must read that cookie. If the text says "validate the issuer", the example must validate it.

## 5. Suggested learning order for a notes set

When deciding where a new topic goes in `main.md`, follow a learning order like this, adjusting to what already exists:

1. Introduction to backend development (the big picture)
2. APIs
3. Databases
4. Authentication and authorization
5. HTTP and HTTPS
6. Git and GitHub
7. Docker, Linux, and deployment (CI/CD)
8. Testing
9. Caching, Redis, queues, and background jobs
10. System design and scalability
11. Security in depth (OWASP, secure coding)
12. Observability and cloud basics

Foundations first, then things you build on top, then operations and scale.
