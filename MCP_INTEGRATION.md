# MCP 集成说明（MCP_INTEGRATION.md）

本文件说明「一起点」实际使用的麦当劳 MCP Server、Tool、调用流程与业务价值。

## 使用的麦当劳 MCP 工具
| 工具名 | 用途 | 在本项目中的角色 |
| --- | --- | --- |
| `order-list` | 查询近期历史订单 | **朋友洞察**的数据源：聚合每位朋友的常点 / 避雷 / 本月次数 |
| `query-my-coupons` | 查询我的可用优惠券 | **抢券**的数据源：列出朋友可被抢的券 |
| `available-coupons` | 麦麦省可领券列表 | 抢券前的可抢券范围参考 |
| `query-meals` | 查询当前可售餐品菜单 | 校验"朋友爱吃的"具体餐品是否存在、取价 |
| `calculate-price` | 商品价格计算 | AA 分账、用券后金额的试算 |
| `create-order` | 创建订单 | 各自在自己账号内完成真正下单 |
| `now-time-info` | 获取当前时间 | 计算"本月次数"的时间基准 |

> 接入地址：`https://mcp.mcd.cn`，协议 Streamable HTTP，请求头 `Authorization: Bearer <Token>`。
> 每个 Token 限 600 次/分钟；Token 按个人账号发放，朋友数据需各自授权。

## 调用流程
1. **连接**：每位朋友在各自客户端用 `mcp-config.example.json` 连入 `mcd-mcp`（Token 取自各自环境变量）。
2. **进会话**：朋友扫码进入「一起点」共享 session（= 当场授权，数据现采现用）。
3. **朋友洞察**：对每位朋友调用 `order-list` → `analyze_insights()` 聚合 → 输出常点 / 避雷 / 本月次数。
4. **抢券**：调用 `query-my-coupons` 列出可抢券 → `grab_coupon()` 落实五条机制（仅会话内 / 不可叠加 / 本次不可用 / 通知对方）。
5. **用券结算**：日后真正使用时 `use_coupon()` 强制只点朋友爱吃的 → `query-meals` 取价 → `calculate-price` 算账 → `create-order` 各自下单。

## 业务价值
- **解决"拼单反复问"**：把朋友偏好从"每次口头问"变成"会话内自动推荐"，降低沟通成本。
- **盘活闲置券**：朋友有券少用，借券机制（带透明告知与明确代价）让券被用起来，增强社交趣味。
- **零后台改动**：纯 MCP 协调层，朋友数据会话内授权，合规、可追溯。

## 注意事项
- 本 Skill 为参赛作品，非麦当劳官方产品；餐品 / 价格 / 券以官方实时数据为准。
- 真实调用需各朋友自己的 Token，本项目脚手架以 mock 数据演示逻辑（见 `src/together_order.py`）。
