# Templates and Test Method Rules

## Standard test class template

Use this structure for all generated API tests.

```java
package com.nova.tests.generated;

import com.nova.tests.base.AbstractApiTest;
import io.restassured.http.ContentType;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.*;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@DisplayName("{test_display_name}")
public class {ClassName}ApiTest extends AbstractApiTest {

    private static final String BASE_PATH = "{endpoint}";
    private static final long TEST_USER_ID = {user_id}L;
    private static final String TEST_PHONE = "{phone}";

    @Override
    protected String dbEnvPrefix() {
        return "{DB_PREFIX}";
    }

    // Do not override baseUrl(); Docker mode relies on the parent implementation.

    @BeforeEach
    public void setupTest() {
        executeSqlWithPrefix("NOVA_USER",
            "DELETE FROM nu_verification_codes WHERE phone = '" + TEST_PHONE + "'",
            "DELETE FROM nu_users WHERE phone = '" + TEST_PHONE + "'"
        );
        // Add module-specific cleanup here.
        logout();
    }

    // test methods
}
```

## Test method generation rules

### Unauthenticated (auth: false)

```java
@Test
@Order({n})
@DisplayName("{case.description}")
public void test_{case.id}() {
    given()
        .contentType(ContentType.JSON)
        .body({request_body})
    .when()
        .{method}(BASE_PATH)
    .then()
        .statusCode({expected_status})
        .body("{field}", equalTo({value}));
}
```

### Authenticated (auth: true)

```java
@Test
@Order({n})
@DisplayName("{case.description}")
public void test_{case.id}() {
    setupFixture("{fixture_id}-nova-user", "NOVA_USER");
    setupFixture("{fixture_id}");

    login("{phone}", "{verification_code}");

    givenWithAuth()
        .body({request_body})
    .when()
        .{method}(BASE_PATH)
    .then()
        .statusCode({expected_status})
        .body("{field}", equalTo({value}));
}
```

Use `test_data.fixed_verification_code` from `project-conventions.yaml` for login.

### requires_mock

```java
@Disabled("requires mock for {service}")
@Test
@Order({n})
@DisplayName("{case.description}")
public void test_{case.id}() {
    // Keep method structure for later unit-test extraction.
}
```

### requires_manual

```java
@Disabled("requires manual execution or special environment")
@Test
@Order({n})
@DisplayName("{case.description}")
public void test_{case.id}() {
    // Keep method structure for later manual runs.
}
```

### External dependency availability

- Generate the normal test first.
- If failures are confirmed as external service issues, add `@Disabled` with a clear reason.

### Idempotency keys

Generate a unique reference and persist it before calling the API.

```java
@Test
public void test_callback_success() throws Exception {
    setupFixture("some-fixture");

    String uniqueRef = "TEST_" + System.currentTimeMillis();

    try (Connection conn = openConnection();
         PreparedStatement stmt = conn.prepareStatement(
             "UPDATE {table} SET {idempotency_field} = ? WHERE id = ?")) {
        stmt.setString(1, uniqueRef);
        stmt.setLong(2, fixtureRecordId);
        stmt.executeUpdate();
    }

    given()
        .body(Map.of("order_no", uniqueRef))
    .when()
        .post(BASE_PATH)
    .then()
        .statusCode(200);
}
```

## Class naming

- Derive `{ClassName}` from the last 1-2 meaningful path segments of the endpoint.
- Convert to PascalCase and suffix with `ApiTest`.
