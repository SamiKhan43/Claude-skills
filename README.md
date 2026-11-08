# Claude Skills

My collection of reusable [Claude](https://claude.ai) skills for specialized tasks, automated workflows, and productivity.

These skills work with **Claude Code** (as personal or project skills) and can be uploaded to **claude.ai** as ZIP archives.

## Features

- Reusable skills for specialized tasks and workflows.
- Organized directory structure, with one folder per skill.
- Automated validation of skill files and references.
- One-command installation for Claude Code.
- One-command packaging of skills for claude.ai.
- GitHub Actions validation on every push and pull request.

---

## Skills

| Skill | What it does | Triggers when you say things like |
|---|---|---|
| [`markdown-study-guides`](skills/markdown-study-guides/SKILL.md) | Creates accurate Markdown study guides, maintains a `main.md` index, and corrects existing notes. Includes validation for table-of-contents links, cross-file links, and Mermaid diagrams. | "Make a Markdown guide for databases", "Correct my MD file", "Add this topic to my notes" |

_Add a row here for every new skill._

---

## Repository Structure

```text
claude-skills/
├── README.md
├── LICENSE
├── .gitignore
├── skills/                         # One folder per skill
│   └── markdown-study-guides/
│       ├── SKILL.md                # Skill instructions
│       ├── references/             # Additional reference material
│       ├── assets/                 # Templates and resources
│       └── scripts/                # Helper scripts
├── templates/
│   └── new-skill/
│       └── SKILL.md                # Starting point for new skills
├── scripts/
│   ├── install.sh                  # Install skills into Claude Code
│   ├── validate_skills.py          # Validate skill structure and references
│   └── package.py                  # Package skills as .skill archives
└── .github/
    └── workflows/
        └── validate.yml            # Validate skills on push and pull requests
```

Packaging creates a `dist/` folder. It is generated, listed in `.gitignore`, and not committed. Release packages are attached to GitHub Releases instead.

---

## Requirements

- **Python 3** for the scripts in `scripts/` (they use only the standard library; PyYAML is optional).
- **Bash** for `scripts/install.sh` (macOS, Linux, Git Bash, or WSL).
- **Claude Code** and/or a **claude.ai** account.

---

## Installation

### Claude Code

You can install skills globally (personal) or locally (project-specific).

#### Personal installation

Personal skills are available across your Claude Code projects.

```bash
git clone https://github.com/<your-username>/claude-skills.git
cd claude-skills
bash scripts/install.sh
```

The installation script creates symlinks from each skill directory into:

```text
~/.claude/skills/
```

This means that when you pull repository updates, your installed skills automatically receive the updated files. If `~/.claude/skills/` did not exist before, restart Claude Code once.

#### Project-specific installation

To install skills into a particular project:

```bash
bash scripts/install.sh /path/to/project/.claude/skills
```

Project skills are stored inside the project's `.claude/skills/` directory and can be shared with the project repository.

#### Manual installation

Alternatively, copy an individual skill folder into:

```text
~/.claude/skills/<skill-name>/
```

For project-specific installation:

```text
your-project/.claude/skills/<skill-name>/
```

**Windows:** run `install.sh` from Git Bash or WSL, or copy the skill folders by hand. Creating symlinks on Windows may need extra setup.

### claude.ai

Custom skills can be uploaded to claude.ai as ZIP archives.

#### 1. Enable code execution

Go to:

**Settings → Capabilities → Code execution and file creation**

Enable the capability. Skills need it to run.

#### 2. Package a skill

Download a `.skill` archive from the repository's Releases page, or generate one yourself:

```bash
python scripts/package.py
```

To package a specific skill:

```bash
python scripts/package.py markdown-study-guides
```

The generated archive will be available in:

```text
dist/markdown-study-guides.skill
```

The `.skill` file is a ZIP archive. If necessary, rename its extension to `.zip`.

#### 3. Upload the skill

1. Open [Claude](https://claude.ai).
2. Navigate to **Customize → Skills**.
3. Click the **+** button.
4. Select **Create skill → Upload a skill**.
5. Select your ZIP archive.
6. Enable the skill using its toggle.

Uploaded custom skills are private to your account unless shared through supported organization features. Menu names can change between app versions.

**Note:** Skills you enable on claude.ai also load in Claude Code when you are signed in with the same Claude account. The sync is one-way, from claude.ai to Claude Code, and needs a recent version of Claude Code (check the Claude Code documentation for the current minimum version). A skill installed from this repository on disk overrides a synced skill with the same name.

---

## Usage

After installing, ask in plain words. Claude loads the skill when the request matches its description:

- "Make a Markdown guide for Docker"
- "Write everything about Redis in Markdown"
- "Correct my MD file" (paste your notes)
- "Add this topic to my notes" (with a list of chapters)

In Claude Code you can also run a skill by name, for example `/markdown-study-guides`.

If Claude does not pick the skill up on its own, be explicit: "Use the markdown-study-guides skill to write a guide on Docker." On claude.ai, also check that the skill's toggle is on.

---

## Add a New Skill

Follow these steps to add a skill to the repository.

### 1. Create a skill folder

Copy the existing template:

```bash
cp -r templates/new-skill skills/my-new-skill
```

### 2. Edit SKILL.md

Open:

```text
skills/my-new-skill/SKILL.md
```

Add the required YAML frontmatter:

```yaml
---
name: my-new-skill
description: Explain what the skill does and when Claude should use it.
---
```

Keep the description under 200 characters if you want to upload the skill to claude.ai. Then write the skill instructions.

### 3. Add supporting resources

Create optional directories when needed:

- `references/` — Additional documentation and reference material.
- `assets/` — Templates and other resources.
- `scripts/` — Helper scripts and automation.

Reference these files inside `SKILL.md` and explain when Claude should use them.

### 4. Validate the skill

Run:

```bash
python scripts/validate_skills.py
```

Fix any reported errors before committing.

### 5. Update the README

Add the new skill to the **Skills** table above.

### 6. Commit and push

```bash
git add .
git commit -m "Add my-new-skill"
git push
```

---

## Conventions

Follow these conventions to keep the repository consistent.

- **Naming:** Folder names and frontmatter `name` values must match and use lowercase kebab-case.
- **Descriptions:** Clearly explain what the skill does and when it should be triggered. Keep them under 200 characters if you want to upload the skill to claude.ai (Claude Code allows longer).
- **Frontmatter fields:** Claude Code supports extra frontmatter fields beyond the open standard. If you use them, the skill may not upload to claude.ai, so keep them for skills you only use in Claude Code.
- **Conciseness:** Keep `SKILL.md` reasonably short. Move detailed information into `references/` when necessary.
- **Progressive disclosure:** Load supporting resources only when they are relevant.
- **Accuracy:** Use correct, current information and maintained tools.
- **Security:** Never include API keys, passwords, tokens, or personal information.
- **Maintainability:** Keep instructions organized, reusable, and easy to understand.

---

## Validate

The repository includes a validation script to check skill structure and file references.

Install PyYAML (optional):

```bash
pip install pyyaml
```

Run the validator:

```bash
python scripts/validate_skills.py
```

The validator checks:

- YAML frontmatter.
- Skill naming conventions.
- Required files.
- Supporting file references.

It also warns about descriptions over 200 characters, very long `SKILL.md` files, and skills missing from this README.

The same validation runs automatically through GitHub Actions whenever you push changes or open a pull request.

---

## Releases

To create a new release:

### 1. Package the skills

```bash
python scripts/package.py
```

### 2. Create a version tag

```bash
git tag v1.0.0
git push origin v1.0.0
```

### 3. Publish a GitHub Release

1. Open your repository on GitHub.
2. Navigate to **Releases**.
3. Select **Create a new release**.
4. Choose your version tag.
5. Attach the generated `.skill` files from `dist/`.
6. Publish the release.

Users can download individual skill packages and upload them to claude.ai.

---

## Security

Skills can contain instructions, scripts, and external dependencies.

Before installing a skill:

- Review its `SKILL.md` instructions.
- Inspect bundled scripts before executing them.
- Check external dependencies.
- Only install skills from sources you trust.
- Never include secrets or sensitive information in skill files.

---

## Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a new skill following the repository conventions.
3. Add any required references, assets, and scripts.
4. Run the validation script.
5. Test the skill in Claude Code or claude.ai.
6. Update the README if you add a new skill.
7. Submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).