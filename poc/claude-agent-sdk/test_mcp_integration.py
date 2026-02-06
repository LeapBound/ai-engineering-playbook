#!/usr/bin/env python3
"""Test Claude Agent SDK with custom MCP tools (simulating Codex integration)."""

import asyncio
from typing import Any
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    create_sdk_mcp_server,
    tool,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
)


# Simulate a simple "code review" tool (like what Codex might provide)
@tool("code_review", "Review code for issues", {"code": str, "language": str})
async def code_review_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Simulate a code review tool."""
    code = args["code"]
    language = args.get("language", "python")

    # Simple mock review
    issues = []
    if "print" in code.lower():
        issues.append("Consider using logging instead of print statements")
    if "TODO" in code:
        issues.append("Found TODO comment - needs implementation")

    if issues:
        review = f"Code review for {language}:\n" + "\n".join(f"- {issue}" for issue in issues)
    else:
        review = f"Code review for {language}: No issues found!"

    return {
        "content": [{"type": "text", "text": review}]
    }


@tool("refactor_code", "Refactor code to improve quality", {"code": str, "style": str})
async def refactor_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Simulate a code refactoring tool."""
    code = args["code"]
    style = args.get("style", "clean")

    # Mock refactoring
    refactored = code.replace("print(", "logger.info(")

    return {
        "content": [{
            "type": "text",
            "text": f"Refactored code ({style} style):\n```python\n{refactored}\n```"
        }]
    }


def display_message(msg):
    """Display message in a readable format."""
    if isinstance(msg, AssistantMessage):
        for block in msg.content:
            if isinstance(block, TextBlock):
                print(f"Claude: {block.text}")
            elif isinstance(block, ToolUseBlock):
                print(f"[Using tool: {block.name}]")
                if block.input:
                    print(f"  Input: {block.input}")
    elif isinstance(msg, ResultMessage):
        if msg.total_cost_usd:
            print(f"Cost: ${msg.total_cost_usd:.6f}")


async def test_with_custom_mcp_tools():
    """Test Claude Agent SDK with custom MCP tools."""
    print("=== Test: Custom MCP Tools (Simulating Codex) ===\n")

    # Create a custom MCP server with our tools
    code_tools_server = create_sdk_mcp_server(
        name="code-tools",
        version="1.0.0",
        tools=[code_review_tool, refactor_tool]
    )

    options = ClaudeAgentOptions(
        mcp_servers={"codetools": code_tools_server},
        allowed_tools=[
            "mcp__codetools__code_review",
            "mcp__codetools__refactor_code",
            "Read",
            "Write",
        ],
        permission_mode="acceptEdits",
    )

    async with ClaudeSDKClient(options=options) as client:
        # Test 1: List available tools
        print("Test 1: List available tools")
        print("-" * 40)
        await client.query("What custom code tools do you have available?")

        async for message in client.receive_response():
            display_message(message)
        print()

        # Test 2: Use code review tool
        print("Test 2: Review the hello.py file we created earlier")
        print("-" * 40)
        await client.query("Read hello.py and review the code for any issues")

        async for message in client.receive_response():
            display_message(message)
        print()

        # Test 3: Use refactor tool
        print("Test 3: Refactor the code")
        print("-" * 40)
        await client.query("Refactor the code in hello.py to use logging instead of print")

        async for message in client.receive_response():
            display_message(message)
        print()


async def main():
    """Run the test."""
    await test_with_custom_mcp_tools()


if __name__ == "__main__":
    asyncio.run(main())
