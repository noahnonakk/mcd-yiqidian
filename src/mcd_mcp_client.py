"""
一起点 (YiQiDian) — 麦当劳 MCP 最小直连客户端（示例）
====================================================
演示如何不依赖任何 MCP SDK，用标准库直接以 Streamable HTTP 协议
调用麦当劳中国 MCP Server（https://mcp.mcd.cn）。

用法:
    export MCD_MCP_TOKEN="你的Token"
    python src/mcd_mcp_client.py order-list
    python src/mcd_mcp_client.py query-my-coupons
    python src/mcd_mcp_client.py calculate-price '{"items":[...]}'

说明:
    - 本文件为「最小可用示例」，便于理解协议与调试；未经真实 Token 实测。
    - 参赛 / 生产推荐直接用 WorkBuddy（官方推荐客户端，已验证可用），
      本 Skill 的 SKILL.md 已说明接入方式。
    - Token 务必从环境变量读取，切勿硬编码进代码或提交到仓库。
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error

ENDPOINT = "https://mcp.mcd.cn"
PROTOCOL = "2024-11-05"
CLIENT_INFO = {"name": "yiqidian", "version": "0.1.0"}


class McdMCP:
    """极简 Streamable HTTP MCP 客户端。"""

    def __init__(self, token: str):
        self.token = token
        self.session_id: str | None = None
        self._id = 0

    # ---- 低层 POST ----
    def _post(self, payload: dict, is_notification: bool = False):
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {self.token}",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        req = urllib.request.Request(
            ENDPOINT, data=data, headers=headers, method="POST"
        )
        try:
            resp = urllib.request.urlopen(req, timeout=30)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            raise RuntimeError(f"HTTP {e.code}: {body[:600]}")

        # 服务器在 initialize 响应头返回会话 ID，后续请求需带上
        if not self.session_id:
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session_id = sid

        ctype = resp.headers.get("Content-Type", "")
        raw = resp.read().decode("utf-8", "ignore")

        if is_notification:
            return None
        return self._parse(raw, ctype)

    @staticmethod
    def _parse(raw: str, ctype: str):
        if "text/event-stream" in ctype:
            # SSE：取最后一个 data: 块
            last = None
            for line in raw.splitlines():
                if line.startswith("data:"):
                    last = line[5:].strip()
            return json.loads(last) if last else None
        return json.loads(raw) if raw.strip() else None

    # ---- MCP 握手 ----
    def initialize(self):
        self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL,
                "capabilities": {},
                "clientInfo": CLIENT_INFO,
            },
        })
        # 握手完成后发送 initialized 通知（无 id）
        self._post(
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            is_notification=True,
        )

    def _next_id(self) -> int:
        self._id += 1
        return self._id

    # ---- 调用工具 ----
    def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        # 示例实现：每次调用前确保已握手（生产环境应缓存 session 复用）
        if not self.session_id:
            self.initialize()
        resp = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        })
        return resp or {}


def main() -> None:
    token = os.environ.get("MCD_MCP_TOKEN")
    if not token:
        print("请先设置环境变量 MCD_MCP_TOKEN（在 https://open.mcd.cn/mcp 申请）")
        sys.exit(1)

    tool = sys.argv[1] if len(sys.argv) > 1 else "order-list"
    raw_args = sys.argv[2] if len(sys.argv) > 2 else "{}"
    try:
        args = json.loads(raw_args)
    except json.JSONDecodeError:
        print("第二个参数必须是合法 JSON，例如 '{\"key\":\"value\"}'")
        sys.exit(1)

    mcp = McdMCP(token)
    try:
        result = mcp.call_tool(tool, args)
    except RuntimeError as e:
        print(f"调用失败：{e}")
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
