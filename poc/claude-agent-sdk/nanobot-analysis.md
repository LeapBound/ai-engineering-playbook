# Nanobot Codebase Analysis

Generated on: 2026-02-06
Codebase analyzed at: `/tmp/nanobot`

---

## Executive Summary

`nanobot` is a compact, event-driven agent framework with a clean separation of concerns:

- **Input/Output decoupling** via an in-memory async message bus (`nanobot/bus/queue.py:11`)
- **Core reasoning loop** in `AgentLoop` that repeatedly calls an LLM + executes tools (`nanobot/agent/loop.py:25`)
- **Prompt/context assembly** from workspace identity files, memory, and skill metadata (`nanobot/agent/context.py:13`)
- **Extensibility-first structure** for tools, channels, and providers (`nanobot/agent/tools/base.py:7`, `nanobot/channels/base.py:10`, `nanobot/providers/base.py:30`)

It is intentionally lightweight and readable, with most core behavior centralized in a small number of files.

---

## 1) Architecture Overview

### 1.1 Core runtime topology

At gateway runtime (`nanobot gateway`), the main stack is assembled in `nanobot/cli/commands.py:155`:

1. Build `MessageBus` (`nanobot/cli/commands.py:179`)
2. Build LLM provider (`nanobot/cli/commands.py:192`)
3. Build `CronService` and inject into `AgentLoop` (`nanobot/cli/commands.py:198`, `nanobot/cli/commands.py:203`)
4. Build `ChannelManager` (`nanobot/cli/commands.py:246`)
5. Start concurrently:
   - agent loop (`agent.run()`) (`nanobot/cli/commands.py:264`)
   - channel manager (`channels.start_all()`) (`nanobot/cli/commands.py:265`)

### 1.2 Agent loop structure (core of the system)

`AgentLoop` (`nanobot/agent/loop.py:25`) is the central orchestrator.

High-level sequence per message:

```text
channel -> bus.inbound -> AgentLoop._process_message()
       -> session + context build
       -> provider.chat(messages, tools)
       -> if tool_calls: execute tools, append tool results, iterate
       -> else: finalize response
       -> save session history
       -> bus.outbound
```

Key implementation points:

- Main consume loop in `run()` (`nanobot/agent/loop.py:105`)
- Message handling in `_process_message()` (`nanobot/agent/loop.py:139`)
- Tool-iteration loop with `max_iterations` guard (`nanobot/agent/loop.py:185`)
- Session persistence after completion (`nanobot/agent/loop.py:229`)

### 1.3 Main components and responsibilities

| Component | File | Responsibility |
|---|---|---|
| `AgentLoop` | `nanobot/agent/loop.py:25` | Core LLM+tools reasoning loop and response generation |
| `ContextBuilder` | `nanobot/agent/context.py:13` | Builds system prompt + chat message payload |
| `ToolRegistry` | `nanobot/agent/tools/registry.py:8` | Registers tools, validates params, executes tools |
| `SessionManager` | `nanobot/session/manager.py:61` | Persistent conversation history (JSONL) |
| `SubagentManager` | `nanobot/agent/subagent.py:20` | Background subagents and result announcement |
| `MessageBus` | `nanobot/bus/queue.py:11` | Async inbound/outbound queues |
| `ChannelManager` | `nanobot/channels/manager.py:14` | Starts channels + dispatches outbound messages |
| `LiteLLMProvider` | `nanobot/providers/litellm_provider.py:12` | Unified provider abstraction for many model backends |
| `CronService` | `nanobot/cron/service.py:42` | Schedules and executes periodic jobs |
| `HeartbeatService` | `nanobot/heartbeat/service.py:38` | Periodic wake-up based on `HEARTBEAT.md` |

---

## 2) Skills System

## 2.1 Skill definition format

Skills are directory-based prompt modules, each with a `SKILL.md`:

```text
<skills-root>/<skill-name>/SKILL.md
```

Expected pattern:

- YAML-like frontmatter (`name`, `description`, optional `metadata` JSON string)
- Markdown body with procedural instructions/examples

Examples:

- `nanobot/skills/github/SKILL.md:1` (requires `gh` binary via metadata)
- `nanobot/skills/weather/SKILL.md:1` (requires `curl`)
- `nanobot/skills/summarize/SKILL.md:1` (requires `summarize` CLI)
- `nanobot/skills/cron/SKILL.md:1` (tool usage patterning)

## 2.2 How skills are loaded

`SkillsLoader` (`nanobot/agent/skills.py:13`) supports two skill roots:

- Workspace skills: `<workspace>/skills` (`nanobot/agent/skills.py:23`)
- Built-in skills: `nanobot/skills` (`nanobot/agent/skills.py:10`)

Precedence: **workspace overrides built-in** by skill name (`nanobot/agent/skills.py:38`, `nanobot/agent/skills.py:51`).

Metadata behavior:

- Frontmatter parser: `get_skill_metadata()` (`nanobot/agent/skills.py:203`)
- `metadata` field expects JSON with `nanobot` object (`nanobot/agent/skills.py:169`)
- Requirement checks for binaries/env vars (`nanobot/agent/skills.py:177`)
- `always` flag support (`nanobot/agent/skills.py:193`)

## 2.3 Progressive loading strategy

Implemented in `ContextBuilder.build_system_prompt()` (`nanobot/agent/context.py:28`):

1. **Always-on skills**: full content injected (`nanobot/agent/context.py:55`)
2. **All skills summary**: XML list with availability + path (`nanobot/agent/context.py:62`, `nanobot/agent/skills.py:101`)

This is important: the model usually sees summaries first and can then use `read_file` to load a skill on demand.

## 2.4 How skills integrate with the agent loop

There is no separate “skill executor.” Skills are prompt/context artifacts.

- Agent loop asks `ContextBuilder` to build messages (`nanobot/agent/loop.py:173`)
- Skills information is embedded in system prompt
- LLM decides whether to read a specific `SKILL.md` through file tools

### Architectural insight

This design makes skills cheap to add and version, but skill “triggering” is heuristic (LLM-driven) rather than deterministic routing.

---

## 3) Tools System

## 3.1 Tool framework architecture

The tool subsystem is clean and conventional:

- Abstract base tool interface (`Tool`) (`nanobot/agent/tools/base.py:7`)
- JSON-schema-like parameter definitions per tool (`nanobot/agent/tools/base.py:38`)
- Local parameter validation engine (`nanobot/agent/tools/base.py:55`)
- Registry for definitions and execution (`nanobot/agent/tools/registry.py:8`)

Execution flow:

1. LLM emits tool call
2. Agent loop passes `name + params` into `ToolRegistry.execute()` (`nanobot/agent/loop.py:217`)
3. Registry validates params (`nanobot/agent/tools/registry.py:57`)
4. Registry invokes `await tool.execute(...)` (`nanobot/agent/tools/registry.py:60`)
5. Result appended as `tool` message in context (`nanobot/agent/context.py:179`)

Validation behavior is tested in `tests/test_tool_validation.py:43`.

## 3.2 Built-in tools available

Registered in `AgentLoop._register_default_tools()` (`nanobot/agent/loop.py:74`):

### File tools

- `read_file` (`nanobot/agent/tools/filesystem.py:9`)
- `write_file` (`nanobot/agent/tools/filesystem.py:49`)
- `edit_file` (`nanobot/agent/tools/filesystem.py:89`)
- `list_dir` (`nanobot/agent/tools/filesystem.py:147`)

### Shell tool

- `exec` (`nanobot/agent/tools/shell.py:12`)
  - timeout support (`nanobot/agent/tools/shell.py:17`)
  - dangerous-pattern denylist (`nanobot/agent/tools/shell.py:25`)
  - optional workspace restriction (`nanobot/agent/tools/shell.py:124`)

### Web tools

- `web_search` (Brave API) (`nanobot/agent/tools/web.py:46`)
- `web_fetch` (readability extraction) (`nanobot/agent/tools/web.py:93`)

### Communication / orchestration tools

- `message` (`nanobot/agent/tools/message.py:9`)
- `spawn` (background subagents) (`nanobot/agent/tools/spawn.py:11`)
- `cron` (if cron service injected) (`nanobot/agent/loop.py:102`, `nanobot/agent/tools/cron.py:10`)

## 3.3 How to add custom tools

### Minimal implementation pattern

```python
from typing import Any
from nanobot.agent.tools.base import Tool


class WeatherApiTool(Tool):
    @property
    def name(self) -> str:
        return "weather_api"

    @property
    def description(self) -> str:
        return "Get weather for a city from internal API."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "city": {"type": "string", "minLength": 1}
            },
            "required": ["city"],
        }

    async def execute(self, city: str, **kwargs: Any) -> str:
        # call your API, return stringified result
        return f"Weather for {city}: ..."
```

### Registration point

Register in `AgentLoop._register_default_tools()` (`nanobot/agent/loop.py:74`).

```python
# nanobot/agent/loop.py
self.tools.register(WeatherApiTool())
```

### Notes

- Keep outputs concise but informative (tool outputs are re-fed to the model)
- Return user-readable error strings (current convention across built-ins)
- If tool needs per-session context, mirror `MessageTool.set_context()` pattern (`nanobot/agent/tools/message.py:22`)

---

## 4) Message Flow

## 4.1 Bus-level flow

Message types:

- `InboundMessage` (`nanobot/bus/events.py:8`)
- `OutboundMessage` (`nanobot/bus/events.py:26`)

Transport:

- In-memory async queues in `MessageBus` (`nanobot/bus/queue.py:20`, `nanobot/bus/queue.py:21`)

## 4.2 End-to-end channel flow

### Inbound path

1. Channel SDK callback receives platform message
2. Channel normalizes payload and calls `BaseChannel._handle_message()` (`nanobot/channels/base.py:84`)
3. `_handle_message()` enforces allowlist and publishes to bus inbound (`nanobot/channels/base.py:104`, `nanobot/channels/base.py:116`)
4. `AgentLoop.run()` consumes inbound and processes (`nanobot/agent/loop.py:113`, `nanobot/agent/loop.py:120`)

### Outbound path

1. Agent returns `OutboundMessage` and publishes to bus outbound (`nanobot/agent/loop.py:234` + `nanobot/agent/loop.py:122`)
2. `ChannelManager._dispatch_outbound()` consumes outbound (`nanobot/channels/manager.py:108`)
3. Routes by `msg.channel` and calls channel `send()` (`nanobot/channels/manager.py:119`, `nanobot/channels/manager.py:122`)

## 4.3 Channel integration specifics

### Telegram

- Long polling bot (`nanobot/channels/telegram.py:95`)
- Supports text + photo + voice + audio + documents (`nanobot/channels/telegram.py:110`)
- Downloads media to `~/.nanobot/media` (`nanobot/channels/telegram.py:246`)
- Optional Groq transcription for voice/audio (`nanobot/channels/telegram.py:255`)
- Markdown-to-Telegram-HTML conversion before send (`nanobot/channels/telegram.py:154`)

### Feishu

- WebSocket long connection (no webhook/public IP) (`nanobot/channels/feishu.py:43`, `nanobot/channels/feishu.py:93`)
- SDK runs in separate thread, marshals events to asyncio loop (`nanobot/channels/feishu.py:199`, `nanobot/channels/feishu.py:205`)
- Dedup cache for message IDs (`nanobot/channels/feishu.py:214`)
- Auto reaction on incoming messages (`nanobot/channels/feishu.py:235`)

### WhatsApp

- Python side uses WebSocket client to Node bridge (`nanobot/channels/whatsapp.py:31`, `nanobot/channels/whatsapp.py:43`)
- Node bridge (`bridge/src/server.ts:19`) wraps Baileys client (`bridge/src/whatsapp.ts:35`)
- Bridge forwards inbound events and receives send commands (`bridge/src/server.ts:34`, `bridge/src/server.ts:44`)

## 4.4 Subagent flow (special system channel)

`spawn` tool starts a background task (`nanobot/agent/tools/spawn.py:58`).

When done, subagent announces result by publishing an inbound `system` message (`nanobot/agent/subagent.py:198`).

Main loop detects `channel == "system"` and reroutes through `_process_system_message()` to original channel/chat (`nanobot/agent/loop.py:151`, `nanobot/agent/loop.py:240`).

---

## 5) Context & Memory

## 5.1 Context assembly

`ContextBuilder` (`nanobot/agent/context.py:13`) composes:

1. **Identity header** with time/runtime/workspace (`nanobot/agent/context.py:73`)
2. **Bootstrap workspace docs**: `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `IDENTITY.md` (`nanobot/agent/context.py:21`, `nanobot/agent/context.py:109`)
3. **Memory context** (`nanobot/agent/context.py:49`)
4. **Skills data** (always-loaded + summary) (`nanobot/agent/context.py:55`, `nanobot/agent/context.py:62`)
5. **Session metadata** (channel/chat id) (`nanobot/agent/context.py:148`)

Then builds message list as:

- `system` prompt
- session history
- current `user` input (possibly multimodal list with base64 image URLs) (`nanobot/agent/context.py:161`)

## 5.2 Memory model

`MemoryStore` (`nanobot/agent/memory.py:9`) is file-based:

- Long-term: `<workspace>/memory/MEMORY.md` (`nanobot/agent/memory.py:19`)
- Daily notes: `<workspace>/memory/YYYY-MM-DD.md` (`nanobot/agent/memory.py:23`)

What is currently injected automatically into prompt:

- long-term memory (`read_long_term`) (`nanobot/agent/memory.py:46`)
- today’s notes (`read_today`) (`nanobot/agent/memory.py:25`)

`get_recent_memories()` exists (`nanobot/agent/memory.py:56`) but is not wired into prompt assembly.

## 5.3 Session memory vs workspace memory

Two distinct memory concepts:

1. **Conversation session history** (JSONL) via `SessionManager` (`nanobot/session/manager.py:61`)
2. **Semantic/user memory notes** (markdown files) via `MemoryStore` (`nanobot/agent/memory.py:9`)

Session history is trimmed to latest 50 messages for context (`nanobot/session/manager.py:39`).

---

## 6) Extensibility Points

## 6.1 Add new capabilities: where to plug in

### A) Add a new tool

- Implement tool class under `nanobot/agent/tools/`
- Register in `AgentLoop._register_default_tools()` (`nanobot/agent/loop.py:74`)

### B) Add a new channel

- Implement `BaseChannel` (`nanobot/channels/base.py:10`)
- Add config model in `nanobot/config/schema.py`
- Wire creation in `ChannelManager._init_channels()` (`nanobot/channels/manager.py:32`)

### C) Add a new provider

- Implement `LLMProvider` (`nanobot/providers/base.py:30`)
- Instantiate in CLI (`nanobot/cli/commands.py:192` / `nanobot/cli/commands.py:307`)

### D) Add new skill packs

- Create `SKILL.md` in workspace: `<workspace>/skills/<name>/SKILL.md`
- Optional metadata for requirements and always-load behavior

### E) Add background workflows

- Expand `SubagentManager` tools/prompt (`nanobot/agent/subagent.py:97`, `nanobot/agent/subagent.py:208`)
- Add new scheduled patterns via `CronService` + `CronTool`

## 6.2 Claude Agent SDK integration strategy

Current state:

- nanobot already supports Claude-family models through LiteLLM model strings (e.g., `anthropic/...`) via `LiteLLMProvider` (`nanobot/providers/litellm_provider.py:12`)
- There is **no direct Claude Agent SDK adapter yet**

### Recommended integration approach (least disruptive)

Implement a provider adapter that preserves nanobot’s existing loop/tool runtime.

#### Step 1: Add new provider adapter

Create `nanobot/providers/claude_agent_provider.py` implementing `LLMProvider`.

Skeleton (SDK-agnostic, map to your installed SDK version):

```python
from typing import Any

from nanobot.providers.base import LLMProvider, LLMResponse, ToolCallRequest


class ClaudeAgentProvider(LLMProvider):
    def __init__(self, sdk_client: Any, default_model: str):
        super().__init__(api_key=None, api_base=None)
        self.client = sdk_client
        self.default_model = default_model

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        model = model or self.default_model

        # 1) Convert nanobot OpenAI-style tools to SDK tool schema
        sdk_tools = convert_tools(tools or [])

        # 2) Call Claude Agent SDK
        sdk_resp = await self.client.chat(
            model=model,
            messages=messages,
            tools=sdk_tools,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # 3) Map SDK tool-use blocks/events -> ToolCallRequest
        tool_calls = [
            ToolCallRequest(id=tc.id, name=tc.name, arguments=tc.arguments)
            for tc in extract_tool_calls(sdk_resp)
        ]

        return LLMResponse(
            content=extract_text(sdk_resp),
            tool_calls=tool_calls,
            finish_reason=extract_finish_reason(sdk_resp),
            usage=extract_usage(sdk_resp),
        )

    def get_default_model(self) -> str:
        return self.default_model
```

#### Step 2: Wire provider selection

Update creation points:

- `nanobot/cli/commands.py:192` (gateway)
- `nanobot/cli/commands.py:307` (direct agent)

Use config flag/provider choice to instantiate `ClaudeAgentProvider` instead of `LiteLLMProvider`.

#### Step 3: Keep AgentLoop unchanged initially

Because `AgentLoop` already handles tool loops (`nanobot/agent/loop.py:185`), your provider should return tool calls and **not auto-execute tools**.

### Alternative (deeper) integration

If you want Claude Agent SDK to own planning/tool orchestration end-to-end, you can replace parts of `AgentLoop` with SDK-native agent sessions. This is a larger refactor and would require:

- remapping nanobot tools into SDK-native tool handlers
- preserving session persistence semantics
- adapting channel/bus delivery boundaries

For maintainability, start with adapter mode first.

---

## 7) Architectural Insights (Strengths & Trade-offs)

### Strengths

- **Very understandable control flow** (small, explicit loop)
- **Good modular boundaries** (channels/tools/providers separated cleanly)
- **Prompt customization is practical** via workspace bootstrap files
- **Skill system is lightweight and easy to extend**
- **Subagent pattern provides scalable async offloading** without major complexity

### Trade-offs / caveats

- **Single-threaded message processing** in main loop; long tasks can queue behind others
- **In-memory bus only** (no durable broker)
- **Skill activation is heuristic** (LLM-driven) rather than deterministic routing
- **Memory is file-based and manual** (no embeddings/retrieval ranking)
- **Tool outputs are untyped strings**, which is simple but can be brittle for complex toolchains

### Practical improvement opportunities

1. Add structured tool result envelopes (JSON contract)
2. Add optional per-session async worker model for better concurrency
3. Add deterministic skill routing hints (keyword/rule pre-selector)
4. Add optional vector retrieval layer for memory/skills

---

## 8) Quick Reference: Key Files by Concern

- Agent loop: `nanobot/agent/loop.py:25`
- Context: `nanobot/agent/context.py:13`
- Memory: `nanobot/agent/memory.py:9`
- Skills loader: `nanobot/agent/skills.py:13`
- Subagents: `nanobot/agent/subagent.py:20`
- Tools base/registry: `nanobot/agent/tools/base.py:7`, `nanobot/agent/tools/registry.py:8`
- Bus/events: `nanobot/bus/events.py:8`, `nanobot/bus/queue.py:11`
- Channels: `nanobot/channels/base.py:10`, `nanobot/channels/manager.py:14`
- Telegram: `nanobot/channels/telegram.py:79`
- Feishu: `nanobot/channels/feishu.py:41`
- WhatsApp channel: `nanobot/channels/whatsapp.py:15`
- WhatsApp bridge (Node): `bridge/src/server.ts:19`, `bridge/src/whatsapp.ts:35`
- Provider abstraction: `nanobot/providers/base.py:30`
- LiteLLM provider: `nanobot/providers/litellm_provider.py:12`
- Gateway assembly: `nanobot/cli/commands.py:155`

