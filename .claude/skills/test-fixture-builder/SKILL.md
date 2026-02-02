---
name: "test-fixture-builder"
description: |
  Build and manage test data fixtures for API testing.
  Triggers on: create test fixture, test data builder, fixture
  Part of the API Testing skill category.
allowed-tools: "Read, Write, Edit, Grep, Glob, mcp__nova-dev-mysql__list_tables, mcp__nova-dev-mysql__execute_sql"
version: 5.0.0
license: MIT
author: "Nova Dev Team"
---

# Test Fixture Builder

## Overview

创建和管理 SQL 驱动的测试数据 fixtures。

**核心原则：每个 fixture 必须自包含且幂等。**

**幂等实现方式：Fixture SQL 文件内必须包含 DELETE 语句（DELETE before INSERT 模式）。**

```sql
-- 标准 Fixture 模式
-- 1. 先删除（确保幂等）
DELETE FROM {table} WHERE id = {test_id};

-- 2. 再插入
INSERT INTO {table} (...) VALUES (...);
```

这样确保：
- 重复运行测试不会因主键冲突失败
- 每次测试都从干净的已知状态开始
- 无需手动运行 cleanup 脚本

## 项目配置

**首先读取：** `testing/tests/config/project-conventions.yaml`

从中获取：
- `test_data.id_ranges` → ID 分配区间
- `test_data.phone_prefix` → 测试手机号前缀
- `test_data.default_timestamp` → 固定时间戳
- `test_data.max_future_timestamp` → 最大未来时间戳
- `modules` → 数据库映射和表前缀

---

## Fixture 类型判断（首要步骤）

创建 fixture 前，先判断类型：

| 场景 | 类型 | 需要的文件 |
|------|------|-----------|
| 仅主库数据 | 单库 | `{name}.sql` |
| 需要登录（有用户+验证码） | 跨库 | `{name}.sql` + `{name}-{user_module}.sql` |
| 仅用户库数据 | 单库 | `{name}.sql`（指定 dbEnvPrefix） |

**判断规则：如果测试需要 `login()`，必须创建跨库 fixture。**

---

## 创建流程

### Step 1: 读取项目配置

从 `project-conventions.yaml` 获取：
- ID 区间分配
- 手机号前缀规则
- 数据库/表前缀映射

### Step 2: 确定场景和 ID

```
场景：{描述}
user_id: 根据 id_ranges.users 分配
phone: 根据 phone_prefix + user_id 后缀
customer_id: 根据 id_ranges.customers 分配
其他 ID: 根据需要分配
```

### Step 3: 查询表结构

用 MCP 数据库工具查询实际表结构：

```
工具: mcp__nova-dev-mysql__list_tables
参数: table_names = "{表名}"
```

确认 NOT NULL 列，确保 INSERT 完整。

### Step 4: 检查冗余字段

**关键：业务逻辑可能读冗余字段而非关联表！**

如果测试失败但数据存在，优先检查主表的状态冗余字段是否设置。

### Step 5: 生成 SQL 文件

**文件结构（必须按此顺序）：**

```sql
-- Fixture: {fixture-name}
-- Description: {场景描述}

-- 1. DELETE 语句（确保幂等）
DELETE FROM {table1} WHERE id = {test_id};
DELETE FROM {table2} WHERE id = {test_id};

-- 2. INSERT 语句
INSERT INTO {table1} (...) VALUES (...);
INSERT INTO {table2} (...) VALUES (...);
```

**生成规则：**
- 使用 `project-conventions.yaml` 中的固定时间戳
- 使用分配的 ID 区间
- DELETE 语句在前，INSERT 在后
- 保存到 fixture 目录

### Step 6: 更新 cleanup 文件

确保 cleanup 文件覆盖新 ID。

---

## 验证码特殊处理（关键）

**问题：验证码用一次就变 USED，必须确保幂等。**

验证码表必须严格遵循 DELETE + INSERT 模式（见上面的幂等规则）：

```sql
-- 正确：每次都重建验证码
DELETE FROM {verification_table} WHERE phone = '{phone}';
INSERT INTO {verification_table} (phone, code, type, status, expired_at, ...)
VALUES ('{phone}', '{fixed_verification_code}', 'LOGIN', 'ACTIVE', '{max_future_timestamp}', ...);
```

**关键配置（从 project-conventions.yaml 读取）：**
- `code`: 使用 `test_data.fixed_verification_code`（通常是 '123456'）
- `expired_at`: 使用 `test_data.max_future_timestamp`（'2037-12-31 23:59:59'）确保不过期
- `status`: 必须是 'ACTIVE'
- `type`: 通常是 'LOGIN' 或 'REGISTER'

---

## 复杂度评估

| 复杂度 | 涉及表数 | 建议 |
|--------|---------|------|
| 低 | 1-2 表 | 直接创建 |
| 中 | 3-4 表 | 仔细检查外键和状态字段 |
| 高 | 5+ 表 | 参考已有高复杂度 fixture，可能需要先 @Disabled |

---

## 外部系统约束

当 fixture 数据会被传递到外部系统时：

### 1. 配置值必须与外部系统实际配置匹配

用 MCP 数据库工具查询实际可用的配置值后再写 fixture。

### 2. 业务状态机中间态必须完整还原

如果模拟流程中间状态，必须把所有中间态字段都设置正确。

### 3. 关联表的数据一致性

多表 fixture 中，关联字段必须在所有表中保持一致。

### 4. 幂等键唯一性

涉及外部系统幂等检查的字段，fixture 中可以写占位值，**测试代码负责动态生成唯一值**。

---

## 测试隔离规则

**问题：** 多个测试用同一个 fixture，但某个测试修改了数据库状态，污染后续测试。

**解决方案：**

1. **只读查询的 case** —— 可以共享 fixture
2. **会修改数据的 case** —— 必须用独立 fixture

**命名规则：**
```
{base-fixture}-for-{scenario}
```

---

## 生成后自检清单

- [ ] **文件位置正确**：SQL 在 fixture 目录下？
- [ ] **幂等性保证**：每个 fixture 文件都以 DELETE 语句开始？
- [ ] **跨库完整**：需要登录的场景有用户库 fixture 文件？
- [ ] **NOT NULL 完整**：INSERT 包含所有 NOT NULL 列？
- [ ] **冗余字段设置**：主表的冗余字段已设置？
- [ ] **cleanup 更新**：cleanup 文件包含新 ID？
- [ ] **时间戳合规**：使用 project-conventions 中的时间戳？

---

## 错误排查

| 错误 | 原因 | 修复 |
|------|------|------|
| Login failed | 验证码状态是 USED | 改用 DELETE + INSERT |
| 业务判断失败但数据存在 | 冗余字段未设置 | 检查主表的状态冗余字段 |
| Duplicate key | ID 与其他 fixture 冲突 | 使用不同 ID |
| NOT NULL constraint | INSERT 缺少必填列 | 用 MCP list_tables 检查表结构 |
| 外部系统返回 400/403 | 配置值与外部系统不匹配 | 查询实际配置值后修正 fixture |
| 状态机操作失败 | 中间态字段未设置 | 检查业务流程，补全所有状态字段 |
| 幂等键冲突 | 重复运行测试 | 测试代码动态生成唯一值 |

---

## Related Skills

- api-test-dsl-generator: DSL 中的 fixture_id 引用这里的 fixture
- api-test-executor: 通过 AbstractApiTest.setupFixture() 执行这里的 SQL
