---
name: "api-test-executor"
description: |
  Execute API test DSL and generate REST Assured test code.
  Triggers on: execute test dsl, run api tests, test executor
  Part of the API Testing skill category.
  Supports Docker mode: docker test, 容器测试
allowed-tools: "Read, Write, Edit, Bash(mvn:*, source:*, env:*), Grep, Glob"
version: 5.1.0
license: MIT
author: "Nova Dev Team"
---

# API Test Executor

## Overview

读取测试 DSL 文件，生成**标准化**的 REST Assured + JUnit 5 测试代码，并执行测试。

**核心原则：所有生成的测试类必须遵循同一个标准模板，确保一致性。**

## 项目配置

**首先读取：** `testing/tests/config/project-conventions.yaml`

从中获取：
- `api_response` → 响应结构和字段映射
- `modules` → 数据库环境前缀
- `test_data.phone_prefix` → 测试数据清理模式
- `authentication` → 登录配置

---

## 标准模板

**所有生成的测试类必须使用以下结构：**

```java
package {test_package};

import {base_test_class};
import io.restassured.http.ContentType;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.*;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@DisplayName("{DSL.description}")
public class {ClassName}ApiTest extends {BaseTestClass} {

    private static final String BASE_PATH = "{DSL.endpoint}";

    @Override
    protected String dbEnvPrefix() {
        return "{DSL.db_env_prefix}";  // 从 project-conventions 的 modules 获取
    }

    @Override
    protected String baseUrl() {
        return "{DSL.base_url}";  // 从 project-conventions 的 base_urls 获取
    }

    @BeforeEach
    public void setupTest() {
        // 清理测试数据（使用 project-conventions 的 phone_prefix）
        // 重置登录状态
        logout();
    }

    // ... test methods
}
```

---

## 测试方法生成规则

### 未登录场景（auth: false）

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

### 需要登录场景（auth: true）

```java
@Test
@Order({n})
@DisplayName("{case.description}")
public void test_{case.id}() {
    // 1. Setup fixtures（如有跨库，先用户库再主库）
    setupFixture("{fixture_id}-{user_module}", "{USER_DB_PREFIX}");
    setupFixture("{fixture_id}");

    // 2. Login
    login("{phone}", "{verification_code}");

    // 3. Execute
    givenWithAuth()
        .body({request_body})
    .when()
        .{method}(BASE_PATH)
    .then()
        .statusCode({expected_status})
        .body("{field}", equalTo({value}));
}
```

**登录参数说明：**
- `phone`: 从 fixture 中使用的测试手机号
- `verification_code`: 使用 `project-conventions.yaml` 中的 `test_data.fixed_verification_code`（通常是 "123456"）

### requires_mock 场景

```java
@Disabled("需要 Mock {service}，留给单元测试")
@Test
@Order({n})
@DisplayName("{case.description}")
public void test_{case.id}() {
    // 保留完整代码结构，便于复制到单元测试
}
```

### requires_manual 场景

```java
@Disabled("需要手动执行或特殊环境配置")
@Test
@Order({n})
@DisplayName("{case.description}")
public void test_{case.id}() {
    // 保留完整代码结构，便于后续手动执行
}
```

---

## 外部服务可用性处理

**原则：先试后跳过**

1. 先生成正常测试代码
2. 运行测试，如果返回错误
3. 检查日志确认是外部服务问题后，再添加 `@Disabled`

---

## 外部系统幂等键处理

**问题：** 外部系统常用订单号做幂等检查，重复运行测试会冲突。

**解决方案：在测试代码中动态生成唯一 ID**

```java
@Test
public void test_callback_success() throws Exception {
    setupFixture("some-fixture");

    // 动态生成唯一 ID
    String uniqueRef = "TEST_" + System.currentTimeMillis();

    // 更新 fixture 中的幂等键
    try (Connection conn = openConnection();
         PreparedStatement stmt = conn.prepareStatement(
             "UPDATE {table} SET {idempotency_field} = ? WHERE id = ?")) {
        stmt.setString(1, uniqueRef);
        stmt.setLong(2, fixtureRecordId);
        stmt.executeUpdate();
    }

    // 请求中使用动态 ID
    given()
        .body(Map.of("order_no", uniqueRef, ...))
    .when()
        .post(BASE_PATH)
    .then()
        .statusCode(200);
}
```

---

## 调试失败的测试

测试返回意外结果时：

1. **打印完整响应：** 在 `.then()` 前加 `.log().all()`
2. **查看服务端日志：** 确保应用配置了日志输出到文件
3. **用请求中的唯一 ID 搜索日志**

---

## 断言类型转换

### JSON 响应断言（默认）

| DSL 类型 | Java 断言 |
|---------|----------|
| `"string"` | `equalTo("string")` |
| `123` (整数) | `equalTo(123)` |
| `123.45` (小数) | `equalTo(123.45F)` |
| `true/false` | `equalTo(true)` / `equalTo(false)` |
| `null` | `equalTo(null)` |
| `[]` | `equalTo(List.of())` |

**类型歧义处理：**
```java
// 当 JSON 返回的数字类型不确定时
.body("field", anyOf(equalTo(0), equalTo(0.0F)))
```

### 纯文本响应断言（body_text）

当 DSL 中使用 `body_text` 字段时（非 JSON 响应）：

```java
.then()
    .statusCode(200)
    .body(equalTo("Expected plain text response"));
```

**常见场景：**
- HTML 页面返回
- CSV/XML 等非 JSON 格式
- 重定向响应

---

## 执行测试

### Docker 模式（默认）

默认使用 Docker 容器执行测试，隔离环境，不占用本地端口：

```bash
cd testing/docker && bash start.sh
```

### 本地模式

当用户明确说"本地跑"、"不用 docker"时使用（需本地已启动应用）：

```bash
cd testing/nova-dev-tests && mvn test -Dtest={ClassName}ApiTest 2>&1 | tail -50
```

**流程：**
1. `mvn package` 构建应用 JAR
2. `docker compose up -d nova-app` 启动应用容器（8080 端口）
3. 等待健康检查通过
4. `docker compose run --rm nova-api-test` 在容器中执行测试
5. 自动清理容器

**Docker 相关文件：**
- `testing/docker/docker-compose.yml` — 服务定义
- `testing/docker/Dockerfile.test` — 测试容器镜像
- `testing/docker/start.sh` / `stop.sh` — 启动/停止脚本

**Docker 模式排查：**
| 问题 | 排查 |
|------|------|
| 健康检查失败 | `docker logs docker-nova-app-1` |
| 测试连接失败 | 检查 `TEST_BASE_URL` 和网络 |
| 构建失败 | 检查 JAR 是否生成 |

---

## 结果报告

```
测试结果: {ClassName}ApiTest
  总计: X, 通过: Y, 跳过: Z (@Disabled), 失败: W

  通过: test_xxx, test_yyy, ...
  跳过: test_zzz (requires_mock)
  失败: test_aaa - {错误原因}
```

---

## 生成后自检清单

- [ ] **继承检查**：类继承了基类？
- [ ] **@BeforeEach 检查**：有 cleanup + `logout()`？
- [ ] **import 检查**：有 `java.util.List` 导入？
- [ ] **fixture 检查**：需要登录的测试用了 `setupFixture()`？
- [ ] **跨库 fixture 检查**：需要登录的测试先加载用户库 fixture？
- [ ] **类型检查**：小数用了 `F` 后缀？
- [ ] **Order 检查**：@Order 从 1 开始连续递增？
- [ ] **testability 检查**：`requires_manual` 和 `requires_mock` 用了 @Disabled？
- [ ] **body_text 检查**：DSL 有 `body_text` 时用了 `.body(equalTo("..."))`？

---

## 常见错误修复

| 错误 | 原因 | 修复 |
|------|------|------|
| `NoSuchMethodError: logout` | 没继承基类 | 检查 extends |
| `Expected 5000.0 but was 5000.0` | 类型不匹配 | 用 `5000.0F` |
| `Login failed` | fixture 没有验证码 | 检查用户库 fixture |
| `JDBC connection failed` | 环境变量缺失 | 检查环境配置 |
| 服务端错误响应 | 服务端异常 | 用 `.log().all()` + 查看日志 |
| 幂等冲突 | 重复运行测试 | 用动态生成唯一 ID |
| `Expected 0 but was 0.0` | JSON 数字类型歧义 | 用 `anyOf()` |

---

## ClassName 推导规则

取 endpoint 最后 1-2 个有意义的路径段，转为 PascalCase。

---

## Related Skills

- api-test-dsl-generator: 生成 DSL
- test-fixture-builder: 管理 SQL fixture 文件
