---
name: test-fixture-v2
description: "创建或更新 SQL 测试数据 fixture（单库、跨库、验证码登录场景），用于 nova 项目 API/集成测试的可重复数据准备。用户提到 fixture、测试数据造数、SQL 造数、登录/验证码相关测试、需要幂等可重复执行的测试准备时触发。"
---

# Test Fixture V2

## 核心概念（幂等）

保证每个 fixture 自包含且可重复执行，严格遵循 DELETE before INSERT。

```sql
DELETE FROM {table} WHERE id = {test_id};
INSERT INTO {table} (...) VALUES (...);
```

## 类型判断

- **单库**：仅主库或仅用户库数据 → `{name}.sql`
- **跨库**：涉及 `login()` / 用户 + 验证码 → `{name}.sql` + `{name}-{user_module}.sql`
- **仅用户库**：单库但需要指定用户库 `dbEnvPrefix`

只要测试流程需要 `login()`，优先判定为跨库。

## 6 步创建流程

1. 读取 `testing/tests/config/project-conventions.yaml`，获取 `id_ranges`、`phone_prefix`、固定时间戳、模块与库映射。
2. 明确场景并分配 ID/手机号（按配置规则生成）。
3. 使用 MCP 数据库工具查询表结构，覆盖所有 NOT NULL 列。
4. 检查主表冗余/状态字段，确保业务逻辑读取的字段齐全。
5. 生成 SQL 文件（DELETE 在前，INSERT 在后；使用固定时间戳；按类型命名文件）。
6. 更新 cleanup 文件，覆盖新增 ID。

## 参考资料

- 需要示例时读取 `references/examples.md`。
- 遇到错误或疑问时读取 `references/troubleshooting.md`。
