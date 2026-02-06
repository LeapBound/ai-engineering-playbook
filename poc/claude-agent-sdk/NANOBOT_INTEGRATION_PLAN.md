# 基于 Nanobot 的需求分析、开发、测试方案

## 现状分析总结

基于 codex 对 nanobot 代码库的深度分析（详见 `nanobot-analysis.md`），我们得出以下关键发现：

### Nanobot 架构特点

**核心组件：**
1. **AgentLoop** - 核心推理循环（LLM + 工具执行）
2. **ContextBuilder** - 构建系统提示和上下文
3. **ToolRegistry** - 工具注册和执行
4. **SkillsLoader** - 技能加载和管理
5. **MessageBus** - 异步消息队列
6. **ChannelManager** - 多渠道集成（Telegram/Feishu/WhatsApp）

**关键特性：**
- ✅ 轻量级、易理解的控制流
- ✅ 清晰的模块边界
- ✅ 基于目录的 Skills 系统
- ✅ 可扩展的 Tools 框架
- ✅ Subagent 支持（后台任务）

**局限性：**
- ⚠️ 单线程消息处理
- ⚠️ 内存消息总线（非持久化）
- ⚠️ Skills 激活是启发式的（LLM 驱动）
- ⚠️ 基于文件的简单记忆系统

## 集成方案设计

### 方案 1: 适配器模式（推荐）

**架构：**
```
nanobot (保持原有架构)
  ├─ AgentLoop (保持不变)
  ├─ ClaudeAgentProvider (新增)
  │   └─ 调用 Claude Agent SDK
  │       ├─ 使用 SDK 的工具生态
  │       └─ 使用 SDK 的 Agents 功能
  └─ 现有 Tools/Skills (保持不变)
```

**实现步骤：**

1. **创建 ClaudeAgentProvider**
   ```python
   # nanobot/providers/claude_agent_provider.py
   from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
   from nanobot.providers.base import LLMProvider

   class ClaudeAgentProvider(LLMProvider):
       def __init__(self, api_key: str, agents: dict = None):
           self.client = ClaudeSDKClient(
               options=ClaudeAgentOptions(
                   agents=agents or {},
                   allowed_tools=["Read", "Write", "Bash", "Edit"],
               )
           )

       async def chat(self, messages, tools, model, ...):
           # 1. 转换 nanobot 工具格式 -> SDK 格式
           # 2. 调用 Claude Agent SDK
           # 3. 转换响应格式 -> nanobot 格式
           pass
   ```

2. **在 CLI 中添加 provider 选择**
   ```python
   # nanobot/cli/commands.py
   if config.provider == "claude-agent":
       provider = ClaudeAgentProvider(...)
   else:
       provider = LiteLLMProvider(...)
   ```

3. **保持 AgentLoop 不变**
   - 工具循环逻辑保持原样
   - 只是 LLM 调用由 Claude Agent SDK 处理

**优势：**
- ✅ 最小侵入性
- ✅ 保持 nanobot 原有架构
- ✅ 可以逐步迁移
- ✅ 易于维护和回滚

### 方案 2: 深度集成（未来考虑）

完全用 Claude Agent SDK 替换 AgentLoop，需要大规模重构。

## 需求分析、开发、测试工作流设计

### 工作流架构

```
用户消息 (Telegram/Feishu/WhatsApp)
  ↓
nanobot MessageBus
  ↓
AgentLoop + ClaudeAgentProvider
  ↓
根据任务类型路由到不同的 Agent
  ├─ requirement-analyst (需求分析)
  ├─ architect (架构设计)
  ├─ developer (代码实现)
  ├─ tester (测试编写)
  └─ reviewer (代码审查)
```

### 1. 需求分析工作流

**Skill 定义：** `nanobot/skills/requirement-analysis/SKILL.md`

```markdown
---
name: requirement-analysis
description: Analyze and structure user requirements
metadata: |
  {
    "nanobot": {
      "always": false,
      "requires": []
    }
  }
---

# Requirement Analysis Skill

When user describes a feature or task, use this skill to:

1. **Clarify Requirements**
   - Ask clarifying questions
   - Identify ambiguities
   - Define scope boundaries

2. **Structure Requirements**
   - Functional requirements
   - Non-functional requirements
   - Acceptance criteria
   - Edge cases

3. **Output Format**
   Create a structured document in `workspace/requirements/<feature-name>.md`:

   ```markdown
   # Feature: <name>

   ## Overview
   Brief description

   ## Functional Requirements
   - FR1: ...
   - FR2: ...

   ## Non-Functional Requirements
   - NFR1: Performance...
   - NFR2: Security...

   ## Acceptance Criteria
   - [ ] Criterion 1
   - [ ] Criterion 2

   ## Edge Cases
   - Case 1: ...
   - Case 2: ...
   ```

4. **Use the requirement-analyst agent**
   The agent has specialized prompts for requirement gathering.
```

**Agent 定义：**
```python
# 在 ClaudeAgentProvider 中预定义
agents = {
    "requirement-analyst": AgentDefinition(
        description="Analyzes and structures user requirements",
        prompt="""You are a requirements analyst. Your job is to:
        1. Ask clarifying questions to understand user needs
        2. Identify ambiguities and edge cases
        3. Structure requirements in a clear, testable format
        4. Define acceptance criteria

        Always be thorough and ask follow-up questions.""",
        tools=["Read", "Write", "Edit"],
        model="sonnet",
    ),
}
```

### 2. 开发工作流

**Skill 定义：** `nanobot/skills/development/SKILL.md`

```markdown
---
name: development
description: Implement features based on requirements
metadata: |
  {
    "nanobot": {
      "always": false,
      "requires": []
    }
  }
---

# Development Skill

Implement features following these steps:

1. **Read Requirements**
   - Load requirement document from `workspace/requirements/`
   - Understand acceptance criteria

2. **Design Implementation**
   - Identify files to modify/create
   - Plan code structure
   - Consider existing patterns

3. **Implement Code**
   - Write clean, maintainable code
   - Follow project conventions
   - Add inline documentation

4. **Use the developer agent**
   The agent specializes in code implementation.
```

**Agent 定义：**
```python
agents = {
    "developer": AgentDefinition(
        description="Implements features based on requirements",
        prompt="""You are a software developer. Your job is to:
        1. Read and understand requirements thoroughly
        2. Design clean, maintainable implementations
        3. Follow existing code patterns and conventions
        4. Write self-documenting code
        5. Consider edge cases and error handling

        Always prioritize code quality over speed.""",
        tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
        model="sonnet",
    ),
}
```

### 3. 测试工作流

**Skill 定义：** `nanobot/skills/testing/SKILL.md`

```markdown
---
name: testing
description: Write and execute tests for implemented features
metadata: |
  {
    "nanobot": {
      "always": false,
      "requires": ["pytest"]
    }
  }
---

# Testing Skill

Write comprehensive tests:

1. **Read Requirements & Code**
   - Understand acceptance criteria
   - Analyze implementation

2. **Write Tests**
   - Unit tests for individual functions
   - Integration tests for workflows
   - Edge case tests
   - Use pytest framework

3. **Execute Tests**
   - Run test suite
   - Report results
   - Fix failures

4. **Use the tester agent**
   The agent specializes in test creation and execution.
```

**Agent 定义：**
```python
agents = {
    "tester": AgentDefinition(
        description="Writes and executes comprehensive tests",
        prompt="""You are a QA engineer. Your job is to:
        1. Write thorough unit and integration tests
        2. Cover edge cases and error conditions
        3. Ensure tests are maintainable and clear
        4. Use pytest best practices
        5. Report test results clearly

        Always aim for high coverage and meaningful tests.""",
        tools=["Read", "Write", "Bash"],
        model="sonnet",
    ),
}
```

### 4. 完整工作流示例

**用户输入（通过 Telegram）：**
```
"我需要一个用户登录功能，支持邮箱和密码登录"
```

**工作流执行：**

1. **需求分析阶段**
   ```
   User: 我需要一个用户登录功能，支持邮箱和密码登录

   Nanobot: 使用 requirement-analyst agent
   - 询问：需要记住登录状态吗？
   - 询问：密码复杂度要求？
   - 询问：登录失败后的处理？
   - 生成：workspace/requirements/user-login.md
   ```

2. **开发阶段**
   ```
   User: 开始实现登录功能

   Nanobot: 使用 developer agent
   - 读取：workspace/requirements/user-login.md
   - 设计：API 端点、数据模型、认证逻辑
   - 实现：创建/修改相关文件
   - 输出：实现完成的代码
   ```

3. **测试阶段**
   ```
   User: 为登录功能编写测试

   Nanobot: 使用 tester agent
   - 读取：需求文档和实现代码
   - 编写：test_user_login.py
   - 执行：pytest test_user_login.py
   - 报告：测试结果
   ```

## 任务路由逻辑

在 nanobot 中实现智能任务路由：

```python
# nanobot/agent/router.py
class TaskRouter:
    """Route tasks to appropriate agents based on intent."""

    KEYWORDS = {
        "requirement-analyst": ["需求", "分析", "clarify", "requirement"],
        "developer": ["实现", "开发", "implement", "code", "feature"],
        "tester": ["测试", "test", "验证", "verify"],
        "reviewer": ["审查", "review", "检查", "check"],
    }

    def route(self, message: str) -> str:
        """Determine which agent should handle this message."""
        message_lower = message.lower()

        for agent, keywords in self.KEYWORDS.items():
            if any(kw in message_lower for kw in keywords):
                return agent

        return "general"  # 默认通用 agent
```

## 实施计划

### Phase 1: 基础集成（1-2 周）
- [ ] 实现 ClaudeAgentProvider
- [ ] 在 nanobot 中集成 Claude Agent SDK
- [ ] 测试基本功能

### Phase 2: Skills 开发（2-3 周）
- [ ] 创建 requirement-analysis skill
- [ ] 创建 development skill
- [ ] 创建 testing skill
- [ ] 定义对应的 Agents

### Phase 3: 工作流优化（1-2 周）
- [ ] 实现任务路由逻辑
- [ ] 优化 agent 提示词
- [ ] 添加工作流状态追踪

### Phase 4: 测试和部署（1 周）
- [ ] 端到端测试
- [ ] 部署到 Telegram/Feishu
- [ ] 用户反馈收集

## 成本估算

基于 POC 测试结果：

- 需求分析：~$0.20-0.30 per session
- 代码实现：~$0.30-0.50 per feature
- 测试编写：~$0.40-0.60 per test suite

**月度估算（假设每天 10 个任务）：**
- 10 tasks/day × $0.50/task × 30 days = **$150/month**

## 下一步行动

1. **克隆 nanobot 到本地项目**
2. **实现 ClaudeAgentProvider**
3. **创建第一个 skill（requirement-analysis）**
4. **端到端测试**
5. **迭代优化**

## 相关文档

- [nanobot-analysis.md](./nanobot-analysis.md) - Codex 深度分析报告
- [POC_SUMMARY.md](./POC_SUMMARY.md) - Claude Agent SDK POC 总结
- [AGENTS_SUMMARY.md](./AGENTS_SUMMARY.md) - Agents 功能详细分析
