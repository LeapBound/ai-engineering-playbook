---
name: claude-code
description: "Use Claude Code CLI for AI-powered coding assistance with full IDE integration. Use when you need to: (1) Get quick answers about code without starting interactive session, (2) Process code through pipes or scripts, (3) Generate structured output with JSON schema, (4) Run automated code analysis or generation tasks, (5) Integrate Claude into CI/CD pipelines or automation workflows."
metadata: {"nanobot":{"emoji":"🤖","requires":{"bins":["claude"]}}}
---

# Claude Code Skill

Use `claude -p` for non-interactive AI coding assistance with full tool access.

## Basic Usage

```bash
claude -p "your prompt"
```

## Key Options

**Working Directory:**
```bash
claude -p "analyze this code" --add-dir /path/to/project
```

**Model Selection:**
```bash
claude -p "your prompt" --model sonnet  # or opus, haiku
```

**Structured Output:**
```bash
claude -p "extract data" --output-format json
claude -p "extract data" --json-schema '{"type":"object","properties":{"name":{"type":"string"}}}'
```

**Tool Control:**
```bash
claude -p "your prompt" --tools "Bash,Read,Edit"  # specific tools
claude -p "your prompt" --tools ""  # disable all tools
```

**Budget Control:**
```bash
claude -p "your prompt" --max-budget-usd 0.50
```

## Common Patterns

**Quick code analysis:**
```bash
claude -p "Explain what this function does" --add-dir .
```

**Generate code:**
```bash
claude -p "Write a Python function to parse JSON" --output-format text
```

**Structured data extraction:**
```bash
claude -p "Extract all function names from this file" \
  --output-format json \
  --add-dir /path/to/code
```

**Automated refactoring:**
```bash
claude -p "Refactor this code to use async/await" \
  --add-dir . \
  --tools "Read,Edit"
```

**Pipeline integration:**
```bash
cat error.log | claude -p "Analyze these errors and suggest fixes"
```

## Tips

- Use `-p` for non-interactive, scriptable output
- `--add-dir` grants file access to specific directories
- `--output-format json` for structured, parseable results
- `--tools` controls which operations Claude can perform
- `--max-budget-usd` prevents runaway costs in automation
