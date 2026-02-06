#!/usr/bin/env python3
"""Test interactive conversation with ClaudeSDKClient."""

import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
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


async def test_multi_turn_conversation():
    """Test multi-turn conversation."""
    print("=== Test: Multi-Turn Conversation ===\n")

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="acceptEdits",
    )

    async with ClaudeSDKClient(options=options) as client:
        # Turn 1: Create a Python file
        print("Turn 1: Create a Python file")
        print("-" * 40)
        await client.query("Create a file called hello.py that prints 'Hello, World!'")

        async for message in client.receive_response():
            display_message(message)
        print()

        # Turn 2: Run the file
        print("Turn 2: Run the file")
        print("-" * 40)
        await client.query("Now run the hello.py file")

        async for message in client.receive_response():
            display_message(message)
        print()

        # Turn 3: Modify the file
        print("Turn 3: Modify the file")
        print("-" * 40)
        await client.query("Change the message to 'Hello from Claude Agent SDK!'")

        async for message in client.receive_response():
            display_message(message)
        print()


async def main():
    """Run the test."""
    await test_multi_turn_conversation()


if __name__ == "__main__":
    asyncio.run(main())
