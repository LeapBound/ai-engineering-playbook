#!/usr/bin/env python3
"""Test Claude Agent SDK custom agents feature."""

import asyncio
from claude_agent_sdk import (
    query,
    AgentDefinition,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
)


def display_message(msg):
    """Display message in a readable format."""
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(f"Claude: {block.text}")
            elif isinstance(block, ToolUseBlock):
                print(f"[Using tool: {block.name}]")
    elif isinstance(msg, ResultMessage):
        if msg.total_cost_usd:
            print(f"Cost: ${msg.total_cost_usd:.6f}")


async def test_code_reviewer_agent():
    """Test a code reviewer agent."""
    print("=== Test 1: Code Reviewer Agent ===\n")

    options = ClaudeAgentOptions(
        agents={
            "code-reviewer": AgentDefinition(
                description="Reviews code for best practices and potential issues",
                prompt="You are a code reviewer. Analyze code for bugs, performance issues, "
                "security vulnerabilities, and adherence to best practices. "
                "Provide constructive feedback in a concise manner.",
                tools=["Read"],
                model="sonnet",
            ),
        },
    )

    async for message in query(
        prompt="Use the code-reviewer agent to review the test_basic.py file",
        options=options,
    ):
        display_message(message)
    print()


async def test_python_expert_agent():
    """Test a Python expert agent that can write code."""
    print("=== Test 2: Python Expert Agent ===\n")

    options = ClaudeAgentOptions(
        agents={
            "python-expert": AgentDefinition(
                description="Python programming expert who writes clean, efficient code",
                prompt="You are a Python expert. Write clean, well-documented Python code "
                "following PEP 8 standards. Always include docstrings and type hints.",
                tools=["Write", "Read"],
                model="sonnet",
            ),
        },
        permission_mode="acceptEdits",
    )

    async for message in query(
        prompt="Use the python-expert agent to create a file called fibonacci.py "
        "that implements a fibonacci function with memoization",
        options=options,
    ):
        display_message(message)
    print()


async def test_multiple_agents():
    """Test multiple agents working together."""
    print("=== Test 3: Multiple Agents (Analyzer + Tester) ===\n")

    options = ClaudeAgentOptions(
        agents={
            "analyzer": AgentDefinition(
                description="Analyzes code structure and patterns",
                prompt="You are a code analyzer. Examine code structure, identify patterns, "
                "and provide insights about the codebase architecture.",
                tools=["Read", "Glob", "Grep"],
                model="sonnet",
            ),
            "tester": AgentDefinition(
                description="Creates comprehensive tests",
                prompt="You are a testing expert. Write thorough unit tests with good coverage. "
                "Use pytest and include edge cases.",
                tools=["Read", "Write", "Bash"],
                model="sonnet",
            ),
        },
        permission_mode="acceptEdits",
    )

    # First use analyzer
    print("Step 1: Using analyzer agent")
    print("-" * 40)
    async for message in query(
        prompt="Use the analyzer agent to find all Python test files in the current directory",
        options=options,
    ):
        display_message(message)
    print()

    # Then use tester
    print("Step 2: Using tester agent")
    print("-" * 40)
    async for message in query(
        prompt="Use the tester agent to create a test file called test_fibonacci.py "
        "that tests the fibonacci.py file we created earlier",
        options=options,
    ):
        display_message(message)
    print()


async def test_agent_with_custom_model():
    """Test agent with specific model configuration."""
    print("=== Test 4: Agent with Custom Model (Haiku) ===\n")

    options = ClaudeAgentOptions(
        agents={
            "quick-helper": AgentDefinition(
                description="Quick helper for simple tasks",
                prompt="You are a quick helper. Provide concise, direct answers.",
                tools=["Read"],
                model="haiku",  # Use faster, cheaper model
            ),
        },
    )

    async for message in query(
        prompt="Use the quick-helper agent to count how many lines are in test_basic.py",
        options=options,
    ):
        display_message(message)
    print()


async def main():
    """Run all agent tests."""
    await test_code_reviewer_agent()
    await test_python_expert_agent()
    await test_multiple_agents()
    await test_agent_with_custom_model()


if __name__ == "__main__":
    asyncio.run(main())
