# Nanobot Skills

Custom skills for [nanobot](https://github.com/HKUDS/nanobot) to integrate AI coding assistants.

## Available Skills

### codex
Deep code analysis, implementation planning, and code modifications using Codex CLI.

**Use when you need to:**
- Analyze complex codebases or trace code paths
- Create implementation plans before coding
- Write or modify code with full codebase context
- Investigate bugs across multiple files
- Understand architecture or design patterns

**Installation:**
```bash
cp -r codex ~/.nanobot/workspace/skills/
```

### claude-code
AI-powered coding assistance with Claude Code CLI for quick answers and automation.

**Use when you need to:**
- Get quick answers about code without interactive session
- Process code through pipes or scripts
- Generate structured output with JSON schema
- Run automated code analysis or generation tasks
- Integrate Claude into CI/CD pipelines

**Installation:**
```bash
cp -r claude-code ~/.nanobot/workspace/skills/
```

## Usage

After installation, nanobot will automatically recognize these skills. You can use them by asking nanobot to use the specific skill:

```bash
nanobot agent -m "Use codex skill to analyze the authentication flow in /path/to/repo"
nanobot agent -m "Use claude-code skill to explain what recursion is"
```

## Requirements

- **codex skill**: Requires [codex CLI](https://github.com/anthropics/codex-cli)
- **claude-code skill**: Requires [Claude Code CLI](https://claude.ai/download)
