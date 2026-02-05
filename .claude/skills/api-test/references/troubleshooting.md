# Troubleshooting and Docker Diagnostics

## Common failures and fixes

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Connection refused (Docker mode) | `baseUrl()` overridden in test class | Remove `baseUrl()` override and rely on `AbstractApiTest`. |
| No tests to run | `.dockerignore` excluded test sources | Verify `testing/` is included in the Docker context. |
| NoSuchMethodError: logout | Test class not extending base class | Ensure `extends AbstractApiTest`. |
| Expected 5000.0 but was 5000.0 | Float vs double mismatch | Use `5000.0F`. |
| Expected 0 but was 0.0 | JSON numeric type ambiguity | Use `anyOf(equalTo(0), equalTo(0.0F))`. |
| Login failed | Missing verification code fixture | Add `nu_verification_codes` row in `-nova-user.sql`. |
| JDBC connection failed | Missing env or DB prefix | Confirm `dbEnvPrefix()` and env vars in Docker. |
| Duplicate key | Fixture ID collision | Allocate new IDs from `id_ranges`. |
| Server error response | Service exception | Add `.log().all()` and inspect server logs. |
| Idempotency conflict | Reusing external order IDs | Generate unique IDs per run. |

## Docker diagnostics

1. Run the script: `./testing/scripts/run-api-test.sh -t {TestClassName}`.
2. If the app fails health checks, inspect logs: `docker logs docker-nova-app-1`.
3. If tests cannot connect, confirm the test class does not override `baseUrl()`.
4. If tests are not discovered, confirm `testing/` is in the Docker build context.
5. If Maven compilation fails, fix compilation errors before re-running.

## Test failure triage

- Add `.log().all()` before `.then()` to print response details.
- Search server logs using request IDs or user IDs from the fixture.
- Confirm fixtures were loaded in the correct database order.
