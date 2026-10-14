# workbuddy.md

> 本文件用于参与「麦当劳程序员创意开发大赛」WorkBuddy 专项奖励（前 100 名 + 真实使用 WorkBuddy + 提交本文件 → 3000 积分）。
> 内容应为使用 WorkBuddy 开发本 Skill 时的对话上下文。以下为开发脉络摘要（实际参赛时建议保留更完整的对话导出）。

## 开发脉络
1. 在 WorkBuddy 中调研官方活动仓库 `M-China/mcd-developer-innovation-challenge` 与 `mcd-mcp-server`，确认活动规则、时间线、必交文件与排名机制（按 Star）。
2. 与用户（若瑜）梳理两个产品灵感：朋友洞察（常点/避雷/本月次数）、借朋友的券。
3. 决策：合成一个产品「一起点」，朋友洞察做主心骨、借券做招牌彩蛋；并通过核实官方规则确认"同一账号只取最高 Star"，故坚持单仓库冲榜。
4. 定稿抢券五条机制：只在一起点内抢 / 不可叠加 / 抢到本次不可用 / 被抢通知对方 / 用时强制只点朋友爱吃的给自己。
5. 在 WorkBuddy（Agent 模式）中搭建本地脚手架：核心逻辑 `src/together_order.py`（可运行 mock 演示）、SKILL.md、README.md、MCP_INTEGRATION.md、mcp-config.example.json、CONTEST_DECLARATION.md（官方模板）、本文件。

## 使用的 WorkBuddy 能力
- Agent 模式直接读写文件、运行 Python 演示脚本
- 通过 Web 检索与官方仓库 README / activityGuidelines.md 核实规则
- Skill 以 WorkBuddy Skill 格式（SKILL.md）交付，契合官方合作伙伴要求
