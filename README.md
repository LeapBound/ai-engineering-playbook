# First Commit AI - 技术负责人的 AI 编程实践指南

> 不是教你如何用 AI，而是如何**约束 AI**，让它在你的规则下工作。

## 1. 开场（Why）

你的团队开始用 AI 写代码了，3 个月后你发现：

- ❌ 代码能跑，但架构越来越混乱
- ❌ 每个人用 AI 的方式不同，代码风格千奇百怪
- ❌ 技术债务快速积累，重构成本指数增长
- ❌ Code Review 反而更费时，因为要理解 AI 的逻辑

**问题根源**：AI 是个能干活但缺乏约束的初级工程师。

**本项目的答案**：建立结构化的工作流和约束机制，让 AI 在规则下工作。

这不是完美方案，而是一份面向技术负责人的工程化探索。

## 2. 技术负责人的真实痛点

### 1. 架构失控
- AI 不理解系统全局，容易产生碎片化解决方案
- 缺乏架构约束，每个功能都是“能跑就行”
- 技术债务快速积累，3 个月后代码库变成屎山

### 2. 质量难保证
- AI 生成的代码看起来能跑，但边界情况没考虑
- 缺少测试，重构时心里没底
- 出问题是 AI 的锅还是需求的锅？

### 3. 团队协作混乱
- 每个人用 AI 的方式不同，代码风格千奇百怪
- Code Review 成本反而更高，因为要理解 AI 的逻辑
- 新人用 AI 写的代码，老人看不懂

### 4. 维护性问题
- AI 生成的代码缺少注释和文档
- 过度设计或过度简化
- 业务逻辑散落各处，难以追溯

## 3. 核心价值与方法论（How）

### 本项目的价值
不是教你如何用 AI，而是如何**约束 AI**，让它在你的规则下工作。

### 核心理念
- AI 是个初级工程师，写代码很快，但需要清晰的指令和检查机制
- 技术负责人要做的：定义规则、设计工作流、建立检查点
- 结构化 > 自然语言：用 DSL、Schema、约定文档来约束 AI 的输出

### 核心原则
1. **结构化约束 > 自然语言指令**
   - 为什么：自然语言有歧义，AI 会按它的理解执行
   - 怎么做：用 DSL、Schema、约定文档来定义清晰规则
   - 案例：测试 DSL 定义“测什么”，而非让 AI 猜

2. **验证实际行为 > 信任 AI 推测**
   - 为什么：AI 会套用常见模式，但你的系统有特殊逻辑
   - 怎么做：探测真实 API 响应、执行测试、Review 代码
   - 案例：curl 探测 API 行为，而非让 AI 猜错误码

3. **人定规则，AI 执行**
   - 为什么：架构、质量标准、业务规则必须由人控制
   - 怎么做：技术负责人定义工作流的检查点
   - 案例：DSL 规则、测试策略由人定义，生成代码由 AI 完成

### 技术负责人的职责重新定义
- ✅ 定义架构约束和编码规范
- ✅ 设计 AI 编程工作流和检查点
- ✅ Review 关键决策和风险代码
- ❌ 不是写所有代码
- ❌ 不是当人肉 linter

## 4. 当前实践：第一个实践——结构化 API 测试工作流（What - Now）

我们从测试环节开始，因为：
1. 测试是最容易量化的质量指标
2. 测试工作流能验证“结构化约束”的有效性
3. 有了测试，才敢放心让 AI 大规模生成代码

但这只是第一步，完整的 AI 编程工作流还包括：
需求澄清 → 架构设计 → 代码实现 → 测试验证 → 代码审查

### 解决方案：三阶段测试生成工作流

**现有的 3 个 skills（结构化约束的具体应用）：**

1. `api-test-dsl-generator`：分析代码 → 生成结构化测试 DSL
   - 用 codex 分析 Controller/Service 的业务分支
   - curl 探测真实 API 响应（验证实际行为）
   - 生成 JSON 格式的测试 DSL（规则由人定义）

2. `api-test-executor`：DSL → 测试代码 → 执行
   - 生成标准化的 REST Assured 测试
   - 自动处理认证、数据准备、断言
   - 支持 Docker 容器化测试（默认）和本地模式
   - 执行并报告结果

3. `test-fixture-builder`：管理测试数据
   - 创建和维护 SQL fixture
   - 支持跨库数据关联

**为什么这样设计：**
- DSL 可审查：团队能 review “测什么”
- DSL 可复用：同一份 DSL 可生成不同语言的测试
- 探测优先：基于真实 API 行为而非代码推测

### 快速开始

```bash
# 1. 配置项目约定（模板：project-conventions.yaml）
# 2. 生成测试 DSL
/api-test-dsl-generator /api/users/login POST
# 3. 执行测试
/api-test-executor testing/tests/dsl/user/login-POST.json
```

### 一个端到端的小例子（登录 API）

**假设场景**：`POST /api/users/login`

**1) DSL（JSON）**

```json
{
  "name": "user login",
  "request": {
    "method": "POST",
    "path": "/api/users/login",
    "headers": {"Content-Type": "application/json"},
    "body": {"email": "user@example.com", "password": "correct_password"}
  },
  "assertions": [
    {"status": 200},
    {"jsonPath": "$.token", "exists": true},
    {"jsonPath": "$.user.id", "type": "number"}
  ]
}
```

**2) 生成的测试代码（REST Assured）**

```java
given()
  .contentType("application/json")
  .body(payload)
.when()
  .post("/api/users/login")
.then()
  .statusCode(200)
  .body("token", notNullValue())
  .body("user.id", instanceOf(Integer.class));
```

**3) 测试结果（示例输出）**

```text
[PASS] user login - status 200
[PASS] user login - token exists
[PASS] user login - user.id is number
```

> 注意：这里的断言来自 DSL，而不是 AI “猜测”出来的逻辑。🧪

### 技术栈
- 当前：Java/Spring Boot + REST Assured
- 计划：Python/FastAPI、Node.js/Express...

## 5. 路线图（What - Future）

### 完整的 AI 编程工作流

#### 1. 需求澄清 [规划中]
**痛点**：产品说“做个用户系统”，AI 不知道要做到什么程度
**方案**：结构化需求模板（功能清单、边界条件、验收标准）

#### 2. 架构设计 [规划中]
**痛点**：AI 不理解系统全局，容易产生碎片化方案
**方案**：架构约束文档（模块划分、接口规范、技术栈限制）

#### 3. 代码实现 [规划中]
**痛点**：每个人用 AI 的方式不同，代码风格千奇百怪
**方案**：编码规范 + Prompt 模板库

#### 4. 测试验证 [已实现] ✅
**痛点**：AI 生成的代码缺少测试，边界情况没覆盖
**方案**：结构化测试 DSL 工作流（当前 3 个 skills）

#### 5. 代码审查 [规划中]
**痛点**：Review 成本高，因为要理解 AI 的逻辑
**方案**：自动化 Checklist + 关键决策标注

#### 6. 部署上线 [规划中]
**痛点**：缺少变更记录，出问题难以回溯
**方案**：自动生成变更摘要和 Rollback 计划

## 6. 参与贡献（Join）

如果你也是技术负责人，在探索 AI 编程的落地方案：
- 有哪些环节最头疼？
- 有哪些约束机制有效？
- 团队规模和技术栈是什么？

欢迎分享你的实践和踩过的坑。

**讨论渠道**：
- Issues：问题反馈和需求讨论
- Discussions：经验分享和最佳实践

**贡献指南**：
- [CONTRIBUTING.md](CONTRIBUTING.md)

## 7. 相关资源

- [Claude Code 官方文档](https://claude.com/claude-code)
- [MCP 协议介绍](https://modelcontextprotocol.io)
