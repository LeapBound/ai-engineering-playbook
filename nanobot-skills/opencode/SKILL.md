---
name: opencode
description: "Plan-first AI coding workflow with OpenCode. Use when you need to: (1) Generate detailed implementation plans before execution, (2) Get human approval before making code changes, (3) Execute approved plans with full codebase context, (4) Manage multi-step development workflows with checkpoints."
metadata: {"nanobot":{"emoji":"📋","requires":{"bins":["opencode"]}}}
---

# OpenCode Skill

Use OpenCode for plan-first AI development workflows with approval gates.

## Workflow: Plan → Approve → Execute

### Phase 1: Planning (Read-only Analysis)

Generate detailed implementation plan without making changes:

```bash
opencode run --agent plan --format json "your task description"
```

**Output:** JSON event stream with plan details
- Parse events with `type: "text"` to extract plan content
- Plan includes: files to modify, implementation steps, considerations

### Phase 2: Approval

Review the generated plan and decide whether to proceed.

### Phase 3: Execution

Execute the approved plan:

```bash
opencode run --agent build --format json "Execute this plan: [plan content]"
```

**Output:** JSON event stream with execution results
- Events include: tool_call, tool_result, text, step_finish
- Actual file modifications are made

## JSON Event Stream Format

All `--format json` output is newline-delimited JSON events:

```json
{"type": "step_start", "part": {...}}
{"type": "text", "part": {"text": "plan content..."}}
{"type": "tool_call", "part": {"tool": {"name": "Write", ...}}}
{"type": "tool_result", "part": {...}}
{"type": "step_finish", "part": {"tokens": {...}}}
```

## Session Management

List previous sessions:
```bash
opencode session list --format json
```

Export/import sessions:
```bash
opencode session export <session-id> > session.json
opencode session import < session.json
```

## Common Patterns

**Safe exploration:**
```bash
opencode run --agent plan --format json "Analyze the authentication flow"
```

**Approved implementation:**
```bash
# 1. Get plan
opencode run --agent plan --format json "Add user login feature" > plan.json

# 2. Review plan.json

# 3. Execute
opencode run --agent build --format json "Execute plan from plan.json"
```

**Quick execution (skip planning):**
```bash
opencode run --format json "Fix typo in README"
```

## Tips

- Always use `--format json` for programmatic parsing
- Plan agent explicitly states "I can't make changes yet"
- Build agent performs actual file modifications
- Parse JSON events line-by-line (newline-delimited)
- Session list shows history with id, title, directory metadata
