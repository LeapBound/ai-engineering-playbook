---
name: "api-test-dsl-generator"
description: |
  Generate structured API test DSL from OpenAPI specs or existing controllers.
  Triggers on: generate test dsl, create api test plan, api test dsl
  Part of the API Testing skill category.
allowed-tools: "Read, Write, Grep, Glob, Bash(curl:*, mvn:*), mcp__nova-dev-mysql__list_tables, mcp__nova-dev-mysql__execute_sql, mcp__codex__codex"
version: 5.0.0
license: MIT
author: "Nova Dev Team"
---

# API Test DSL Generator

## Overview

分析 Controller/Service 代码，生成带有可测性标记的结构化测试 DSL（JSON 格式）。

**核心原则：先探测后写 DSL，确保 expect 部分反映实际 API 行为。**

## 项目配置

**首先读取：** `testing/tests/config/project-conventions.yaml`

从中获取：
- `api_response.http_status` → HTTP 状态码行为
- `modules` → 数据库前缀映射
- `external_dependencies` → requires_mock 标记依据
- `auth_required_patterns` / `auth_excluded_patterns` → 认证判断
- `base_urls` → API 基础 URL
- `authentication` → 登录配置

---

## DSL 标准结构

```json
{
  "dsl_version": "1.0",
  "module": "{module_name}",
  "db_env_prefix": "{from modules config}",
  "base_url": "{from base_urls config}",
  "endpoint": "/api/xxx",
  "method": "POST|GET|MIXED",
  "description": "API 描述",
  "auth_required": true,
  "cases": [...]
}
```

---

## 生成流程

### Step 1: 定位 Controller

```bash
grep -r "@PostMapping\|@GetMapping" --include="*Controller.java" | grep "{endpoint}"
```

读取 Controller，提取：
- 端点路径、HTTP 方法
- 请求参数类型（@RequestBody）
- 返回类型
- 是否需要认证（认证注解）

### Step 2: 分析 Service 实现

用 codex 分析业务逻辑：

```
工具: mcp__codex__codex
参数: 分析 {ServiceClass}.{method} 的所有分支：
1. 什么条件返回成功？
2. 什么条件返回错误？
3. 哪些分支依赖外部服务？
```

每个分支对应一个 test case。

### Step 3: 判断认证要求

根据配置文件判断：
- 匹配 `auth_required_patterns` → `auth_required: true`
- 匹配 `auth_excluded_patterns` → `auth_required: false`

**如果 auth_required: true，必须生成未登录的 case。**

### Step 4: curl 探测（关键）

**对每个 error case 必须探测实际响应：**

```bash
# 未登录场景
curl -s -X POST '{base_url}{endpoint}' \
  -H 'Content-Type: application/json' \
  -d '{}' | jq .

# 带认证场景
curl -s -X POST '{base_url}{endpoint}' \
  -H 'Content-Type: application/json' \
  -H '{token_header}: {token}' \
  -d '{body}' | jq .
```

**探测目的：**
- 确认实际 HTTP 状态码（不要猜）
- 确认 body 结构和错误消息
- 验证业务逻辑假设

### Step 5: 判断可测性

**核心原则：先试后跳过，不要过早标记 requires_mock**

| 条件 | testability | 说明 |
|------|-------------|------|
| 仅依赖数据库状态 | `api_testable` | 直接测试 |
| 依赖外部服务 | `api_testable` | **先尝试调用**，失败再改为 requires_mock |
| 需要外部服务返回特定错误 | `requires_mock` | 无法通过正常调用触发 |
| 需要特定时序/并发 | `requires_manual` | 无法自动化 |

### Step 6: 生成 cases

**按优先级排序：P0 → P1 → P2**

```json
{
  "id": "{action}_{scenario}",
  "category": "happy_path|error|boundary",
  "priority": "P0|P1|P2",
  "testability": "api_testable|requires_mock",
  "auth": true|false,
  "description": "描述",
  "precondition": {
    "type": "fixture",
    "fixture_id": "{fixture-name}"
  },
  "request": {
    "method": "POST",
    "path": "",
    "body": {...}
  },
  "expect": {
    "status": 200,
    "body": {
      "code": 200,
      "success": true,
      "data.field": "value"
    }
  }
}
```

---

## Case 生成规则

### 规则 1：认证 API 必须有未登录 case

根据 `project-conventions.yaml` 的 `on_auth_error` 配置生成 expect。

### 规则 2：业务错误用 body.code 判断

根据 `on_business_error` 配置，业务错误可能返回 HTTP 200，错误码在 body 中。

### 规则 3：需要登录的 case 标记 auth: true

```json
{
  "auth": true,
  "precondition": {
    "type": "fixture",
    "fixture_id": "{fixture-name}"
  }
}
```

### 规则 4：fixture_id 命名对应 SQL 文件

```
fixture_id: "{name}"
→ SQL 文件: {name}.sql + {name}-{user_module}.sql（如需登录）
```

### 规则 5：非 JSON 响应用 body_text

部分接口（如回调）返回纯字符串而非 JSON：

```json
{
  "expect": {
    "status": 200,
    "body_text": "SUCCESS"
  }
}
```

### 规则 6：会修改数据的 case 需要独立 fixture

- 只读查询的 case 可以共享 fixture
- 会修改数据的 case 必须用独立的 fixture
- 命名规则：`{base-name}-for-{scenario}`

### 规则 7：复杂数据链提前评估

某些场景需要完整的业务数据链（多表关联），在 DSL 中标注复杂度：

```json
{
  "precondition": {
    "type": "fixture",
    "fixture_id": "{name}",
    "complexity": "high"
  }
}
```

---

## 保存位置

```
testing/tests/dsl/{module}/{endpoint-slug}-{METHOD}.json
```

---

## 生成后自检清单

- [ ] **auth_required 正确**：认证 API 设置了 `auth_required: true`？
- [ ] **有未登录 case**：认证 API 有未登录错误的 case？
- [ ] **探测过 expect**：所有 error case 的 expect 来自 curl 探测？
- [ ] **fixture_id 存在**：precondition 中的 fixture 已存在或标记为待创建？
- [ ] **testability 正确**：外部依赖场景标记合理？

---

## 输出格式

```
生成 DSL: {path}

统计：
- 总 cases: X
- api_testable: Y (Z%)
- requires_mock: W

需要创建的 fixtures:
- {fixture_id}（状态）

下一步：执行 api-test-executor 生成测试代码
```

---

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| expect 与实际不符 | 没有 curl 探测 | 先探测再写 DSL |
| 缺少未登录 case | 忘记认证检查 | 检查 auth_required |
| fixture 不存在 | 只写了 DSL 没创建 fixture | 用 test-fixture-builder 创建 |

---

## Related Skills

- api-test-executor: 执行 DSL 生成 Java 测试代码
- test-fixture-builder: 创建 fixture SQL 文件
