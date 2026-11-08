---
name: markdown-study-guides
description: Write accurate markdown study guides on technical topics, keep a main.md index, and fix buggy .md notes. Use for 'make a markdown', 'write X in markdown', 'correct my md file', 'add this topic'.
---

# Markdown study guides

The user is building a personal knowledge base of markdown notes, one file per topic, so they can relearn a topic later and so other people can learn it from scratch. The notes will probably end up in a GitHub repository. Your job is to produce guides that are **correct, complete, consistent with each other, and easy to scan**, and to keep the index file up to date.

## Workflow

1. **Work out what the request is.**
   - *A topic name* ("make a markdown for databases") → write a new guide from scratch.
   - *A pasted document* → this is a correction job. Fix it (see "Correcting existing notes") and keep the author's structure and topics unless they ask for changes.
   - *A list of topics, chapters, or video timestamps* → use that list as the outline, in that order. Drop the timestamps and links. Then add important related material the list misses, because users say things like "if you know more, include them". Say briefly what you added.
   - Do not interrogate the user. For "make X in markdown", pick sensible scope and go. One or two assumptions can be stated in the closing message.
2. **Check volatile facts.** Library names and versions, standards and top-10 lists (OWASP, RFCs), cloud features, and CLI flags change. If a web search tool is available, verify the ones you are unsure about. If not, write from solid knowledge and tell the user which details to double-check against official sources.
3. **Write the guide** using the structure in `assets/guide-template.md` (see "Standard structure").
4. **Validate** the file with `python scripts/check_guide.py <files>`. It checks table-of-contents anchors, cross-file links, code-fence balance, and common Mermaid mistakes. Fix every error. Review warnings and fix the real ones.
5. **Update `main.md`** (see "The main.md index").
6. **Deliver** the files: write to `/mnt/user-data/outputs/`, call `present_files`, then reply briefly (what the file covers, what was added beyond the request, anything untested or worth verifying).

## Standard structure

Use this skeleton for every guide, so the notes feel like one set:

1. `# Title: Subtitle`
2. One paragraph saying what the guide covers and who it is for.
3. `## Quick summary`: 5 to 8 bullets, or a small table, of the whole topic.
4. `## Table of contents`: numbered, each entry a working anchor link, followed by a "Related guides" line linking sibling guides.
5. Numbered sections (`## 1. ...`). Start with the big picture, then fundamentals, then practical details, then advanced and operational material.
6. A full working example near the end for practical topics (small, runnable, with the real commands to try it).
7. `## Checklist: things to remember`: numbered, one line each.
8. `## Common pitfalls and interview questions`: a "Pitfalls" list, then "Interview questions" with 1 to 3 sentence answers.

Number sections, and write headings so the generated anchors are predictable (`## 7. OAuth 2.0` becomes `#7-oauth-20`). Keep the title, the one-paragraph description, and the Quick summary as the opening. Do not replace the opening with a friendly analogy unless the user asks for one: in this project the user tried an analogy-style intro and asked for the original opening back.

## Style rules, and why they matter

- **Plain, direct sentences.** Define a term the first time it appears. Readers are learning, but they are adults.
- **Tables for comparisons** (SQL vs NoSQL, sessions vs JWT, merge vs rebase). A comparison in a table is faster to review later than the same content in paragraphs.
- **Short, correct code.** Prefer 10 to 40 line examples that run as written. Add a comment where a line carries a lesson (`# pin the algorithm`, `# NEVER build SQL with f-strings`). Never put real secrets in examples; load them from environment variables.
- **Use current, maintained libraries and safe defaults.** For example PyJWT instead of python-jose, Argon2id through pwdlib or argon2-cffi instead of passlib, timezone-aware datetimes instead of `utcnow()`, parameterized SQL, `--force-with-lease` instead of `--force`. A study guide that teaches an unsafe pattern is worse than no guide.
- **Be honest about limits.** If code is untested, say so in your closing message. If a number or a feature depends on a version, say "check the latest".
- **Link instead of repeating.** When a guide touches a topic that has its own guide (auth inside an API guide, HTTP caching inside a backend intro), summarize in a few bullets and link to the sibling file. Duplicated content drifts apart.
- **Teach the why.** Each rule in the guide should come with its reason in a few words ("never trust the client, because users control their device").
- **No chat leftovers.** The file must not contain "What would you like next?", "I can also generate...", or similar. Those belong in your reply, not in the document.
- **Diagrams only where they help.** Use Mermaid for flows, sequences, and ER diagrams. Quote labels, avoid risky characters (see `references/gotchas.md`).
- **Keep the sections proportionate.** Cover the whole topic, but keep each section tight enough to scan. If a guide is turning into a book, link out or split it.

## The main.md index

`main.md` is the entry point for the whole notes folder (it is renamed to `README.md` when the notes are pushed to GitHub). Keep it simple: a title, two or three sentences on what the notes are for, and a `## Topics` section.

Each topic gets a block like this:

```markdown
### [Topic Name](topic-guide.md)

One-line description. Covered in this note:

- [Section name](topic-guide.md#3-section-heading)
- [Another section](topic-guide.md#7-another-heading)
```

Rules:

- Add the new topic in logical learning order (backend intro, then APIs, databases, auth, HTTP, Git, and so on), not just at the bottom.
- Link only to anchors that exist. Run `python scripts/check_guide.py main.md *.md` from the notes folder to verify.
- Insert with a small Python or `str_replace` edit instead of regenerating the file, so earlier blocks stay untouched.
- Keep the guides in the same folder as `main.md`, or the relative links break. If the user moves them into folders, update the links.

## Correcting existing notes

When the user pastes a document and asks for it to be fixed or improved ("this was generated by Copilot, I think it has bugs"):

1. Keep their topic list and overall order. Improve it, do not replace it.
2. Look for these problems, in roughly this order:
   - **Broken rendering**: Mermaid labels with unquoted parentheses or angle brackets, unbalanced code fences, tables without header separators, nested fences that need four backticks.
   - **Wrong or unsafe code**: deprecated APIs, naive/timezone mistakes, hardcoded secrets, string-built SQL, examples whose pieces do not connect (for instance a cookie that is set but never read), claims in the text that the code does not implement (validating `iss`/`aud`).
   - **Outdated recommendations**: unmaintained libraries, deprecated algorithms or grant types.
   - **Contradictions** between sections, and wrong terminology.
   - **Missing context**: a table of contents with dead links, missing "why", missing pitfalls.
   - **Chat leftovers** at the end of the file.
3. Write the corrected file in full. Do not hand back a list of suggestions when the user asked for a corrected file.
4. In the reply, summarize the fixes in a short list grouped by kind (diagram bugs, code bugs, content gaps), so the user learns what was wrong.

## Small related requests

These came up alongside the guides. Handle them the same way each time:

- **GitHub repo description**: give a one-sentence "About" text, an even shorter option, 2 or 3 repo name ideas, a topics (tags) list, and a reminder to rename `main.md` to `README.md` and add a LICENSE.
- **"What should I learn next?"**: recommend one next topic with a reason, then a short ordered list. Base it on what already exists in the notes (check `main.md`). Ask which one to write first.
- **Changing only a section** (for example the opening) of an existing guide: edit just that part with a small script or `str_replace`. If the user says "give it back", restore the earlier text exactly and leave the rest alone.

## Bundled resources

- `assets/guide-template.md`: a copy-and-fill skeleton of the standard structure. Read it before writing a new guide.
- `references/gotchas.md`: Mermaid rules, GitHub anchor rules, markdown formatting traps, and a list of "teach the safe version" code patterns. Read it when a diagram will be included or code will be written.
- `scripts/check_guide.py`: the validator described in the workflow. Usage: `python scripts/check_guide.py main.md some-guide.md` (exit code 1 when there are errors).
