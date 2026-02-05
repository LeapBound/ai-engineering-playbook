# Fixture Creation Rules and Templates

## Location and naming

- Store fixture SQL under `testing/nova-dev-tests/src/test/resources/fixtures/sql/`.
- Use lowercase, hyphenated names (e.g., `withdrawal-insufficient-credit.sql`).
- For cross-db setups, create two files:
  - `{name}.sql` for the main module database.
  - `{name}-nova-user.sql` for the user database.

Load order for authenticated tests:
1. `setupFixture("{name}-nova-user", "NOVA_USER")`
2. `setupFixture("{name}")`

## ID allocation

- Allocate IDs from `test_data.id_ranges` in `project-conventions.yaml`.
- Avoid reusing IDs already referenced by existing fixtures.
- Use `test_data.phone_prefix` + user ID for phone numbers.

## Standard fixture template

```sql
-- Fixture: {fixture-name}
-- {scenario description}

-- 1. Cleanup (idempotent)
DELETE FROM {table} WHERE id = {test_id};

-- 2. Insert
INSERT INTO {table} ({columns})
VALUES ({values});
```

## User database fixture template

Include both user and verification code rows when login is required.

```sql
-- Fixture: {fixture-name}-nova-user
-- {scenario description}

DELETE FROM nu_verification_codes WHERE phone = '{phone}';
DELETE FROM nu_users WHERE id = {user_id};

INSERT INTO nu_users (id, phone, status, created_at, updated_at)
VALUES ({user_id}, '{phone}', 'ACTIVE', NOW(), NOW());

INSERT INTO nu_verification_codes (phone, code, created_at, updated_at)
VALUES ('{phone}', '{fixed_verification_code}', NOW(), NOW());
```

## Cleanup rules

- Always delete by primary key or unique fields used in the insert.
- If multiple tables are involved, delete in reverse dependency order.
- Keep cleanup in the same fixture file as the inserts.

## Fixture quality checklist

- Use idempotent deletes before inserts.
- Include verification code rows for authenticated tests.
- Avoid hard-coded phone numbers not derived from `phone_prefix`.
- Keep cross-db fixtures paired and named consistently.
