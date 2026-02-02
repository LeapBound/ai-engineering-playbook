# Changelog

本文件记录项目的重要变更，格式遵循 [Keep a Changelog](https://keepachangelog.com/)。
版本号遵循语义化版本。

## [Unreleased]
### Added
- 结构化需求模板（功能清单、边界条件、验收标准），统一需求口径
- 架构约束文档（模块划分、接口规范、技术栈限制），稳定架构边界
- 编码规范 + Prompt 模板库，收敛 AI 输出风格
- 自动化 Review Checklist + 关键决策标注，降低审查成本
- 变更摘要 + Rollback 计划自动生成，提升上线可追溯性

## [0.1.0] - 2026-02-03
### Added
- 项目 README：技术负责人的 AI 编程实践指南
  - 核心方法论：结构化约束、验证实际行为、人定规则 AI 执行
  - 技术负责人的 4 大痛点分析
  - 完整的 AI 编程工作流路线图
- API 测试工作流（3 个 Claude Code Skills）：
  - `api-test-dsl-generator`：分析代码生成结构化测试 DSL
    - 用 codex 分析业务分支
    - curl 探测真实 API 响应
    - 生成 JSON 格式测试 DSL
  - `api-test-executor`：执行 DSL 生成测试代码
    - 生成 REST Assured 测试
    - 自动处理认证和数据准备
    - 执行测试并报告结果
  - `test-fixture-builder`：管理测试数据
    - 创建和维护 SQL fixture
    - 支持跨库数据关联
- 项目配置：
  - `.gitignore`：忽略本地配置，保留 skills 目录

### 技术栈
- Java/Spring Boot + REST Assured
- Claude Code + MCP
