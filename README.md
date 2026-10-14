# 一起点 (YiQiDian) · 麦当劳朋友向点餐助手

> 2026 麦当劳程序员创意开发大赛参赛作品 · 基于麦当劳中国 MCP
> 官方活动仓库：https://github.com/M-China/mcd-developer-innovation-challenge

**和朋友扫码一起点麦当劳，自动告诉你谁爱点啥、谁踩过雷、这个月点了几次；还能在会话里"抢"朋友的优惠券——抢到本次不能用、被抢会通知、用时强制只点他爱吃的给自己。**

拼单不再挨个问，闲置券不再浪费，朋友间的点单变成一个有趣的小游戏。

---

## 看一眼（交互原型）

仓库里有一份可交互的手机原型，本地浏览器打开即可体验三屏流程与"抢券 + 强制代价"：

```
preview/index.html
```

（在文件管理器双击，或 `open preview/index.html` / `start preview/index.html`）

---

## 两个真实痛点

| 痛点 | 现在 | 一起点之后 |
| --- | --- | --- |
| **朋友洞察** | 朋友不在身边要一起点外卖，还得挨个问"你吃啥、不吃啥" | 进会话自动推荐每位朋友的**常点 / 避雷 / 本月次数** |
| **抢券** | 自己常没券，朋友有券却很少用 | 会话内"抢"朋友的券，带**透明告知 + 明确代价** |

---

## 功能

- **朋友常点**：基于各自历史订单频次推荐 Top3
- **朋友避雷**：明确不喜欢的 + 评分过低的餐品
- **朋友本月次数**：轻量社交梗 + 提醒
- **抢券（招牌功能）· 五条机制**
  1. 只在「一起点」会话内抢
  2. 优惠券不可叠加
  3. 抢到本次不可用（留到之后自己点单）
  4. 被抢通知对方
  5. 真用时效强制只点朋友爱吃的给自己
- **AA 分账**：会话内实时算账，结算给结账人

---

## 技术架构

「一起点」是一层**架在麦当劳 MCP 之上的朋友协调层**：

1. 每个朋友在自己客户端把**自己的 MCP Token** 连进同一个 Skill 会话（扫码进 session = 各自授权）
2. Skill 在会话层**聚合**所有人的常点 / 避雷 / 券，生成合并推荐与点单方案
3. 真正下单、用券、付款仍各自在自己账号完成（AA 在会话里算好）

> 麦当劳 MCP 按个人 Token 授权，本 Skill 改不了麦当劳后台；朋友数据在会话内现采现用，不碰对方账号。

---

## 快速开始

### 方式 A：WorkBuddy（官方推荐，已验证可用）

1. 在 https://open.mcd.cn/mcp 用手机号登录 → 控制台 → 激活 → 复制 Token
2. 在 WorkBuddy「连接器」按 `mcp-config.example.json` 配置并启用 `mcd-mcp`（Token 用环境变量 `MCD_MCP_TOKEN`，**切勿硬编码**）
3. 安装本 Skill（见 `SKILL.md`），对助手说"和朋友一起点"即可

### 方式 B：本地 Python 演示（无需 Token）

```bash
python src/together_order.py
```

内置 mock 数据，演示「朋友洞察」聚合与「抢券」五条机制的判断逻辑。

### 方式 C：直连麦当劳 MCP（最小客户端示例）

```bash
export MCD_MCP_TOKEN="你的Token"      # Windows: set MCD_MCP_TOKEN=你的Token
python src/mcd_mcp_client.py order-list
```

`src/mcd_mcp_client.py` 是一个最小 Streamable HTTP 客户端示例，演示如何直接调用麦当劳 MCP 工具。**未经真实 Token 实测**，生产 / 参赛推荐用方式 A。

---

## 接入麦当劳 MCP（工具清单）

- 接入地址：`https://mcp.mcd.cn`
- 协议：**Streamable HTTP**
- 鉴权：请求头 `Authorization: Bearer <Token>`（Token 在 open.mcd.cn/mcp 申请）
- 限流：每 Token 600 次/分钟

本项目实际用到的工具（完整 30+ 工具见官方仓库 `M-China/mcd-mcp-server`，当前 v1.0.9）：

| 工具 | 用途 | 在本项目中的角色 |
| --- | --- | --- |
| `order-list` | 查询历史订单 | **朋友洞察**数据源：聚合常点 / 避雷 / 本月次数 |
| `query-my-coupons` | 查询我的优惠券 | **抢券**数据源 |
| `query-meals` / `query-meal-detail` | 菜单 / 餐品详情 | 校验"朋友爱吃的"具体餐品是否存在、取价 |
| `calculate-price` | 商品价格计算 | AA 分账 / 用券后金额试算 |
| `create-order` | 创建订单 | 各自在自己账号内完成真正下单 |
| `now-time-info` | 当前时间 | 计算"本月次数"的时间基准 |

---

## 文件结构

```
mcd-yiqidian/
├── README.md                  # 本文件
├── CONTEST_DECLARATION.md     # 参赛声明（官方模板，内容不可改）
├── MCP_INTEGRATION.md         # 麦当劳 MCP 工具调用说明
├── mcp-config.example.json    # 脱敏 MCP 配置（仅占位符）
├── SKILL.md                   # WorkBuddy Skill 定义
├── preview/index.html         # 交互原型（手机三屏 + 抢券演示）
├── src/
│   ├── together_order.py      # 核心逻辑 + 可运行 mock 演示
│   └── mcd_mcp_client.py      # 最小 Streamable HTTP 直连客户端示例
└── workbuddy.md               # WorkBuddy 开发对话上下文（专项奖励用）
```

---

## 参赛信息

- 活动：麦当劳程序员创意开发大赛（1024 程序员节）
- 排名：按 GitHub 公开 Star 数，前 100 进榜（同一账号多项目只取最高 Star）
- 报名：在活动主仓库按格式发 Issue（详见官方规则）
- 截止：报名 + 排名 2026-10-25 23:59（北京时间）
- 本项目报名 Issue：[#668](https://github.com/M-China/mcd-developer-innovation-challenge/issues/668)

## 许可证

MIT
