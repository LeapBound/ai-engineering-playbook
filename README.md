# AI Engineering Playbook

> 面向技术负责人的 AI 工程治理方法论

## 问题定义

AI 引入后，代码一致性开始下降，团队难以维持统一的工程标准。  
Review 成本上升，因为需要识别生成代码背后的隐含假设与边界。  
技术债风险加剧，局部最优的实现堆叠成系统性失控。  
当约束缺失时，架构、质量与维护性都会被动下滑。

## 立场声明

本项目不是教写代码，而是防止工程失控。  
技术负责人需要把注意力放在规则、边界与审计机制上。  
核心目标是让 AI 在可验证的约束中执行。

## 核心方法

- 输出必须结构化（结构化测试模板/Schema/Checklist）
- 规则优先，自然语言提示被约束
- 人只审规则，AI 执行

## 4. 当前实践：第一个实践——结构化 API 测试工作流（What - Now）

我们从测试环节开始，因为：
1. 测试是最容易量化的质量指标
2. 测试工作流能验证“结构化约束”的有效性
3. 有了测试，才敢放心让 AI 大规模生成代码

但这只是第一步，完整的 AI 编程工作流还包括：
需求澄清 → 架构设计 → 代码实现 → 测试验证 → 代码审查

### 解决方案：双技能测试生成工作流

**当前实现方式（基于 `api-test` skill）：**
1. 分析代码路径（Controller/Service）
2. 直接生成 REST Assured 测试类 + SQL fixture
3. 执行测试
4. 报告结果

**现有的 2 个 skills（结构化约束的具体应用）：**

1. `api-test`：生成并执行 REST Assured + JUnit 5 API 测试
   - 生成测试类、fixtures 和断言
   - 自动处理认证、数据准备、执行与结果报告
   - 支持 Docker 容器化测试（默认）和本地模式
   - 基于真实 API 响应进行探测验证

2. `test-fixture`：管理测试数据
   - 创建或更新 SQL fixture
   - 支持单库、跨库数据关联与验证码登录场景

**为什么这样设计：**
- 模板可审查：团队能 review 测试模板和生成规则
- Fixture 可复用：同一份 SQL fixture 支持多个测试场景
- 探测优先：基于真实 API 行为而非代码推测

### 快速开始

```bash
# 1. 配置项目约定（模板：project-conventions.yaml）
# 2. 创建测试数据 fixture
/test-fixture 用户登录场景
# 3. 生成并执行 API 测试
/api-test POST /api/users/login
```

### 一个端到端的小例子（登录 API）

**假设场景**：`POST /api/users/login`

**1) Fixture SQL**

```sql
-- 幂等：先删后插
DELETE FROM users WHERE id = 900001;
INSERT INTO users (id, email, password_hash, status)
VALUES (900001, 'test@example.com', 'hashed_password', 'ACTIVE');
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

> 注意：这里的断言来自结构化测试模板，而不是 AI “猜测”出来的逻辑。

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
**方案**：结构化测试工作流（当前 2 个 skills）

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
