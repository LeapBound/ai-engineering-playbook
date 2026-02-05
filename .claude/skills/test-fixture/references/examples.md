# Fixture Examples

以下示例用于快速套用模板，按需替换表名与字段。所有时间戳、手机号前缀、验证码等都从 `project-conventions.yaml` 获取。

## 单库示例（主库）

文件：`{fixture}.sql`

```sql
-- Fixture: user-active
-- Description: 活跃用户基础数据
DELETE FROM nl_customers WHERE id = {customer_id};

INSERT INTO nl_customers (id, user_id, status, created_at, updated_at)
VALUES ({customer_id}, {user_id}, 'ACTIVE', '{default_timestamp}', '{default_timestamp}');
```

## 跨库示例（主库 + 用户库）

适用：测试流程需要 `login()` 或验证码。

文件 1：`{fixture}.sql`（主库）

```sql
-- Fixture: user-login
DELETE FROM nl_customers WHERE id = {customer_id};

INSERT INTO nl_customers (id, user_id, status, created_at, updated_at)
VALUES ({customer_id}, {user_id}, 'ACTIVE', '{default_timestamp}', '{default_timestamp}');
```

文件 2：`{fixture}-{user_module}.sql`（用户库，例如 `nu`）

```sql
-- Fixture: user-login-nu
DELETE FROM nu_users WHERE id = {user_id};

INSERT INTO nu_users (id, phone, status, created_at, updated_at)
VALUES ({user_id}, '{phone}', 'ACTIVE', '{default_timestamp}', '{default_timestamp}');
```

## 验证码处理示例

确保验证码幂等：每次都 DELETE + INSERT，且状态为 `ACTIVE`。

```sql
DELETE FROM nu_verification_codes WHERE phone = '{phone}';

INSERT INTO nu_verification_codes (phone, code, type, status, expired_at, created_at)
VALUES ('{phone}', '{fixed_verification_code}', 'LOGIN', 'ACTIVE', '{max_future_timestamp}', '{default_timestamp}');
```

提示：`fixed_verification_code` 与 `max_future_timestamp` 使用配置中的固定值，避免过期或状态错误。
