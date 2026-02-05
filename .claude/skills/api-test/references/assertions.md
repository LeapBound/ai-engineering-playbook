# Assertion Type Conversion Rules

## JSON response assertions (default)

Map DSL value types to Hamcrest assertions:

| DSL value | Java assertion |
| --- | --- |
| "string" | `equalTo("string")` |
| 123 (int) | `equalTo(123)` |
| 123.45 (decimal) | `equalTo(123.45F)` |
| true/false | `equalTo(true)` / `equalTo(false)` |
| null | `equalTo(null)` |
| [] | `equalTo(List.of())` |

### Numeric ambiguity

If the JSON numeric type is inconsistent, use a tolerant matcher:

```java
.body("field", anyOf(equalTo(0), equalTo(0.0F)))
```

## Plain text responses

When the DSL uses `body_text` (non-JSON response), assert against the full body:

```java
.then()
    .statusCode(200)
    .body(equalTo("Expected plain text response"));
```

## Assertion checklist

- Use `F` suffix for decimal values.
- Use `anyOf` for ambiguous numeric types.
- Prefer exact string matches unless the response is explicitly variable.
