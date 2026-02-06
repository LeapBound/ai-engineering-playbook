---
name: codex
description: "Deep code analysis, implementation planning, and code modifications using Codex CLI. Use when you need to: (1) Analyze complex codebases or trace code paths, (2) Create implementation plans before coding, (3) Write or modify code with full codebase context, (4) Investigate bugs across multiple files, (5) Understand architecture or design patterns in existing code."
metadata: {"nanobot":{"emoji":"🔧","requires":{"bins":["codex"]}}}
---

# Codex Skill

Use `codex exec` for AI-powered code analysis and implementation with full codebase context.

## Basic Usage

```bash
codex exec "your prompt" --cd /path/to/repo --sandbox read-only
```

## Sandbox Modes

- `read-only`: Analysis only (safest)
- `workspace-write`: Can modify files
- `danger-full-access`: Full system access

## Common Patterns

**Analyze requirements:**
```bash
codex exec "Analyze this requirement and suggest implementation: [requirement]" \
  --cd /path/to/repo --sandbox read-only
```

**Plan implementation:**
```bash
codex exec "Create implementation plan for [feature]. List files and steps." \
  --cd /path/to/repo --sandbox read-only
```

**Implement code:**
```bash
codex exec "Implement [feature]" --cd /path/to/repo --sandbox workspace-write
```

**Debug issues:**
```bash
codex exec "Investigate why [issue] happens. Explain root cause." \
  --cd /path/to/repo --sandbox read-only
```

## Workflow

1. Analyze with `--sandbox read-only`
2. Plan with `--sandbox read-only`
3. Implement with `--sandbox workspace-write`
