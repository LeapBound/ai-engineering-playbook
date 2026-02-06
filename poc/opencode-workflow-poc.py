#!/usr/bin/env python3
"""
OpenCode Workflow PoC Script
测试 "规划 → 审批 → 执行" 工作流的可行性
"""

import subprocess
import json
import time
import sys
from pathlib import Path
from typing import Optional, Dict, Any


class OpenCodeWorkflowPoC:
    """OpenCode 工作流概念验证"""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.plan_file = Path("/tmp/opencode_plan.json")
        self.session_id: Optional[str] = None

    def run_command(self, cmd: list[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """执行命令并返回结果"""
        print(f"🔧 Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=capture_output,
            text=True
        )
        return result

    def phase1_planning(self, task_description: str) -> Dict[str, Any]:
        """Phase 1: 规划阶段 - 生成执行计划"""
        print("\n" + "="*60)
        print("📋 Phase 1: 规划阶段")
        print("="*60)

        # 使用 plan agent + JSON 格式
        cmd = ["opencode", "run", "--agent", "plan", "--format", "json", task_description]
        result = self.run_command(cmd)

        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            sys.exit(1)

        # 解析 JSON 事件流
        output = result.stdout
        print(f"\n📄 OpenCode JSON 事件流:")

        plan_text = ""
        events = []

        for line in output.strip().split('\n'):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                events.append(event)

                # 提取 text 类型的事件（包含计划内容）
                if event.get("type") == "text":
                    text_content = event.get("part", {}).get("text", "")
                    plan_text += text_content
                    print(f"  📝 {event['type']}: {text_content[:100]}...")
                elif event.get("type") == "step_finish":
                    tokens = event.get("part", {}).get("tokens", {})
                    print(f"  ✅ {event['type']}: tokens={tokens}")
                else:
                    print(f"  🔹 {event['type']}")
            except json.JSONDecodeError:
                print(f"  ⚠️  无法解析行: {line[:50]}...")

        # 保存解析后的计划
        plan_data = {
            "task": task_description,
            "plan_text": plan_text,
            "events": events
        }

        self.plan_file.write_text(json.dumps(plan_data, indent=2))
        print(f"\n✅ 计划已保存到: {self.plan_file}")
        print(f"\n📋 提取的计划内容:\n{'-'*60}\n{plan_text}\n{'-'*60}")

        return plan_data

    def phase2_approval(self, plan: Dict[str, Any], auto_approve: bool = True) -> bool:
        """Phase 2: 审批阶段 - 人工审查"""
        print("\n" + "="*60)
        print("👀 Phase 2: 审批阶段")
        print("="*60)

        print("\n请审查以下计划:")
        print("-" * 60)

        # 显示计划文本
        plan_text = plan.get("plan_text", "")
        if plan_text:
            print(plan_text)
        else:
            print(json.dumps(plan, indent=2)[:500] + "...")

        print("-" * 60)

        if auto_approve:
            print("\n✅ 自动批准模式：计划已批准")
            return True

        approval = input("\n输入 'approve' 批准执行，其他任何输入将拒绝: ").strip().lower()

        if approval == "approve":
            print("✅ 计划已批准")
            return True
        else:
            print("❌ 计划被拒绝")
            return False

    def phase3_execution(self, plan: Dict[str, Any]) -> bool:
        """Phase 3: 执行阶段 - 使用 build agent 执行"""
        print("\n" + "="*60)
        print("⚙️  Phase 3: 执行阶段")
        print("="*60)

        # 提取任务描述
        task = plan.get("task", "")
        plan_text = plan.get("plan_text", "")

        # 构建执行指令
        execution_prompt = f"Execute this plan:\n{plan_text}\n\nOriginal task: {task}"

        print(f"\n🔹 使用 build agent 执行计划...")
        print(f"执行指令: {execution_prompt[:100]}...")

        # 使用 build agent 执行
        cmd = ["opencode", "run", "--agent", "build", "--format", "json", execution_prompt]
        result = self.run_command(cmd)

        if result.returncode != 0:
            print(f"❌ 执行失败: {result.stderr}")
            return False

        # 解析执行结果
        output = result.stdout
        print(f"\n📄 执行结果 (JSON 事件流):")

        for line in output.strip().split('\n'):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                event_type = event.get("type")

                if event_type == "text":
                    text = event.get("part", {}).get("text", "")
                    print(f"  📝 {text[:100]}...")
                elif event_type == "tool_call":
                    tool = event.get("part", {}).get("tool", {})
                    print(f"  🔧 Tool call: {tool.get('name', 'unknown')}")
                elif event_type == "tool_result":
                    print(f"  ✅ Tool result received")
                elif event_type == "step_finish":
                    tokens = event.get("part", {}).get("tokens", {})
                    print(f"  ✅ Step finished: tokens={tokens}")
                else:
                    print(f"  🔹 {event_type}")
            except json.JSONDecodeError:
                pass

        print(f"\n✅ 执行完成")
        return True

    def phase4_persistence_test(self) -> bool:
        """Phase 4: 持久性测试 - 验证 session list 功能"""
        print("\n" + "="*60)
        print("💾 Phase 4: Session 管理测试")
        print("="*60)

        # 测试 session list
        print(f"\n🔹 测试 session list...")
        result = self.run_command(["opencode", "session", "list", "--format", "json"])

        if result.returncode == 0:
            print(f"✅ 成功获取 session 列表")
            try:
                sessions = json.loads(result.stdout)
                print(f"📋 Session 数量: {len(sessions) if isinstance(sessions, list) else 'N/A'}")
                print(f"内容预览:\n{json.dumps(sessions, indent=2)[:500]}...")
                return True
            except json.JSONDecodeError:
                print(f"输出:\n{result.stdout[:500]}...")
                return True
        else:
            print(f"❌ 获取 session 列表失败: {result.stderr}")
            return False

    def run_poc(self, task_description: str, auto_approve: bool = True):
        """运行完整的 PoC 流程"""
        print("\n" + "="*60)
        print("🚀 OpenCode Workflow PoC 开始")
        print("="*60)
        print(f"项目目录: {self.project_dir}")
        print(f"任务描述: {task_description}")

        try:
            # Phase 1: 规划
            plan = self.phase1_planning(task_description)

            # Phase 2: 审批
            if not self.phase2_approval(plan, auto_approve=auto_approve):
                print("\n❌ PoC 终止：计划未获批准")
                return

            # Phase 3: 执行
            execution_success = self.phase3_execution(plan)

            # Phase 4: 持久性测试
            if execution_success:
                persistence_success = self.phase4_persistence_test()

            # 总结
            print("\n" + "="*60)
            print("📊 PoC 测试总结")
            print("="*60)
            print(f"✅ Phase 1 (规划): 成功")
            print(f"✅ Phase 2 (审批): 成功")
            print(f"{'✅' if execution_success else '❌'} Phase 3 (执行): {'成功' if execution_success else '失败'}")
            if execution_success:
                print(f"{'✅' if persistence_success else '❌'} Phase 4 (持久性): {'成功' if persistence_success else '失败'}")

        except KeyboardInterrupt:
            print("\n\n⚠️  PoC 被用户中断")
        except Exception as e:
            print(f"\n\n❌ PoC 执行出错: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    # 配置
    project_dir = "/tmp/opencode-test-project"
    task_description = "Create a simple Python function that adds two numbers"

    # 创建测试项目目录
    Path(project_dir).mkdir(parents=True, exist_ok=True)

    # 运行 PoC
    poc = OpenCodeWorkflowPoC(project_dir)
    poc.run_poc(task_description)


if __name__ == "__main__":
    main()
