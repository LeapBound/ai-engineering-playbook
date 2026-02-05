---
name: api-test-v2
description: Generate and execute REST Assured + JUnit 5 API tests for Nova services, including test class creation, fixtures, and assertions. Use when the user asks to write or extend API tests, add coverage for an endpoint, verify API behavior, create test fixtures, or run API tests via Docker or local scripts.
---

# API Test (Nova)

## Project config (always load)
- Read `testing/tests/config/project-conventions.yaml`.
- Extract:
  - `api_response` structure and field mapping.
  - `modules` database environment prefixes.
  - `test_data.phone_prefix` and `test_data.fixed_verification_code`.
  - `test_data.id_ranges` for ID allocation.
  - `authentication` settings.

## Workflow (5 phases)

### Phase 1: Understand the request
- Identify endpoint, HTTP method, module, and required auth.
- List target scenarios (success, failure, boundary, idempotency).
- Note any priority or must-cover cases.

### Phase 2: Analyze code paths
- Locate controller mapping for the endpoint and inspect request/response models.
- Trace service logic to enumerate success and failure paths.
- Identify external dependencies or required mocks.

### Phase 3: Generate tests and fixtures
- Load `references/templates.md` for the standard test class template and test method rules.
- Load `references/fixtures.md` for fixture creation rules and SQL templates.
- Create the test class under `testing/nova-dev-tests/src/test/java/com/nova/tests/generated/`.
- Create fixture SQL files following the naming conventions from the references.
- Allocate IDs and test phone numbers using `project-conventions.yaml`.

### Phase 4: Execute tests
- Use the project automation script: `testing/scripts/run-api-test.sh -t {TestClassName}`.
- The script is located in the project root, not bundled with this skill.
- If execution is skipped or blocked, capture the reason and proceed to reporting.
- For environment or Docker issues, load `references/troubleshooting.md`.

### Phase 5: Report and record results
- Summarize pass/fail/skip counts and key failures.
- If required, update `testing/TEST_COVERAGE.md` per project conventions or script output.
- If not executed, mark the test as pending with the blocking reason.

## References (load only when needed)
- `references/templates.md` - standard test class template and method generation rules.
- `references/fixtures.md` - fixture creation rules, cross-db templates, naming.
- `references/assertions.md` - assertion type conversion and response handling.
- `references/troubleshooting.md` - common failures and Docker diagnostics.
