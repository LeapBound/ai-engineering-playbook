#!/usr/bin/env python3
"""Basic test of Claude Agent SDK."""

import asyncio
from claude_agent_sdk import query, AssistantMessage, TextBlock, ResultMessage


async def test_basic_query():
    """Test basic query functionality."""
    print("=== Test 1: Basic Query ===")

    async for message in query(prompt="What is 2 + 2? Just give me the answer."):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            if message.total_cost_usd:
                print(f"Cost: ${message.total_cost_usd:.6f}")
    print()


async def test_with_tools():
    """Test with file tools."""
    print("=== Test 2: With Tools (File Operations) ===")

    from claude_agent_sdk import ClaudeAgentOptions

    options = ClaudeAgentOptions(
        allowed_tools=["Write"],
        permission_mode="acceptEdits",  # Auto-accept file edits
    )

    async for message in query(
        prompt="Create a file called test_output.txt with the text 'Hello from Claude Agent SDK!'",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            if message.total_cost_usd:
                print(f"Cost: ${message.total_cost_usd:.6f}")
    print()


async def main():
    """Run all tests."""
    await test_basic_query()
    await test_with_tools()


if __name__ == "__main__":
    asyncio.run(main())
