# Troubleshooting

## 常见错误与修复

| 现象 | 可能原因 | 处理方式 |
| --- | --- | --- |
| Login failed | 验证码状态为 USED 或过期 | 用 DELETE + INSERT 重建验证码，状态设为 `ACTIVE`，过期时间用 `max_future_timestamp` |
| Duplicate key | ID 与其他 fixture 冲突 | 按 `id_ranges` 重新分配 ID |
| NOT NULL constraint | INSERT 缺少必填列 | 用 MCP `list_tables` 补齐 NOT NULL 列 |
| 业务判断失败但数据存在 | 主表冗余/状态字段未设置 | 检查并补齐冗余字段 |
| 外部系统 400/403 | 配置值与真实配置不一致 | 查询实际配置值后再写入 fixture |
| 状态机中间态失败 | 中间态字段未完整还原 | 按业务流程补全所有状态字段 |
| 幂等键冲突 | 测试重复执行生成相同幂等值 | 在测试代码里动态生成唯一值 |

## 常见问题

**Q: 什么时候必须跨库？**
A: 只要流程需要 `login()` 或验证码，就创建跨库 fixture。

**Q: 验证码怎么保证幂等？**
A: 始终 DELETE 后 INSERT，状态设为 `ACTIVE`，过期时间用固定最大值。

**Q: cleanup 文件一定要更新吗？**
A: 是的，新增 ID 要进入 cleanup，避免污染后续测试。
