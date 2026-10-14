"""
一起点 (YiQiDian) — 麦当劳朋友向点餐助手 · 核心逻辑脚手架
========================================================
本文件是参赛 Skill 的核心逻辑骨架，纯标准库实现，可直接运行演示：
    python src/together_order.py

真实接入麦当劳 MCP 时，把下面标注 [MCP] 的地方替换为对应工具调用即可。
没有 Token 也能跑：默认使用内置 mock 数据演示。
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------
@dataclass
class OrderItem:
    name: str
    price: float


@dataclass
class Order:
    items: list[OrderItem]
    date: str  # ISO 格式 "2026-10-14"
    rating: Optional[int] = None  # 1-5，用户给这顿的评分（可选）


@dataclass
class Friend:
    name: str
    orders: list[Order] = field(default_factory=list)
    disliked: list[str] = field(default_factory=list)  # 朋友明确不喜欢的餐品


# ---------------------------------------------------------------------------
# 朋友洞察：常点 / 避雷 / 本月次数
# ---------------------------------------------------------------------------
def analyze_insights(friend: Friend, now: Optional[datetime] = None) -> dict:
    """聚合一位朋友的历史订单，产出「常点 / 避雷 / 本月次数」。"""
    now = now or datetime.now()
    month_prefix = f"{now.year}-{now.month:02d}"

    # 常点：按出现频次统计
    freq: Counter[str] = Counter()
    for o in friend.orders:
        for it in o.items:
            freq[it.name] += 1
    top_orders = [name for name, _ in freq.most_common(3)]

    # 避雷：明确不喜欢的，+ 评分 <= 2 的餐品
    avoid = set(friend.disliked)
    for o in friend.orders:
        if o.rating is not None and o.rating <= 2:
            for it in o.items:
                avoid.add(it.name)
    avoid = sorted(avoid)

    # 本月次数
    month_count = sum(1 for o in friend.orders if o.date.startswith(month_prefix))

    return {
        "name": friend.name,
        "常点": top_orders,
        "避雷": avoid,
        "本月次数": month_count,
        "总订单数": len(friend.orders),
    }


# ---------------------------------------------------------------------------
# 抢券：五条机制（若瑜 2026-10-14 定稿）
# ---------------------------------------------------------------------------
@dataclass
class Coupon:
    owner: str       # 券的主人（朋友）
    name: str        # 券名
    discount: float  # 抵扣金额（演示用）


class GrabResult:
    def __init__(self, ok: bool, msg: str, coupon: Optional[Coupon] = None,
                 notified: Optional[str] = None):
        self.ok = ok
        self.msg = msg
        self.coupon = coupon
        self.notified = notified


def grab_coupon(coupon: Coupon, grabber: str, in_session: bool,
               already_grabbed: list[Coupon]) -> GrabResult:
    """
    抢券核心逻辑，严格落实五条规则：
      1. 只在「一起点」session 内抢
      2. 优惠券不可叠加（本会话只抢一张，不与已有叠加）
      3. 抢到不能本次用（deferred，留到之后自己点单）
      4. 被抢要告知对方（notified = 券主人）
      5. 真要用时强制只点朋友喜欢的给自己（见 use_coupon）
    """
    # 规则 1：仅限 session 内
    if not in_session:
        return GrabResult(False, "❌ 抢券只能在「一起点」会话内发生，当前不在会话中。")

    # 规则 2：不可叠加 —— 已抢过则不能再抢第二张
    if already_grabbed:
        return GrabResult(False, "❌ 优惠券不可叠加，本会话已抢过券，不能再抢。")

    # [MCP] 真实接入时调用 query-my-coupons / available-coupons 校验券有效性

    # 规则 4：被抢通知对方
    notified = coupon.owner

    # 规则 3：抢到不能本次用 —— 返回 deferred 标记
    return GrabResult(
        True,
        f"✅ {grabber} 抢到了 {coupon.owner} 的「{coupon.name}」，"
        f"但本次不可用，已留到你之后的订单。已通知 {coupon.owner}。",
        coupon=coupon,
        notified=notified,
    )


def use_coupon(coupon: Coupon, friend_favorite: str, chosen_item: str) -> GrabResult:
    """规则 5：真正使用被抢的券时，强制只能点「朋友爱吃的」给自己。"""
    if chosen_item != friend_favorite:
        return GrabResult(
            False,
            f"❌ 用 {coupon.owner} 的券只能点他爱吃的「{friend_favorite}」"
            f"，你选的「{chosen_item}」不符合，已被强制拦截。",
        )
    return GrabResult(
        True,
        f"✅ 已用 {coupon.owner} 的券下单「{chosen_item}」给自己吃——这就是借券的代价。",
        coupon=coupon,
    )


# ---------------------------------------------------------------------------
# 演示（mock 数据，无需 Token）
# ---------------------------------------------------------------------------
def _mock_friends() -> list[Friend]:
    return [
        Friend(
            name="阿强",
            disliked=["麦辣鸡腿堡", "菠萝派"],
            orders=[
                Order([OrderItem("巨无霸", 25.5)], "2026-10-02", 5),
                Order([OrderItem("巨无霸", 25.5), OrderItem("薯条", 12)], "2026-10-09", 5),
                Order([OrderItem("麦香鱼", 22)], "2026-09-20", 4),
                Order([OrderItem("巨无霸", 25.5)], "2026-10-14", 5),
            ],
        ),
        Friend(
            name="小美",
            disliked=["辣翅"],
            orders=[
                Order([OrderItem("板烧鸡腿堡", 24)], "2026-10-01", 5),
                Order([OrderItem("板烧鸡腿堡", 24)], "2026-10-11", 4),
                Order([OrderItem("沙拉", 19)], "2026-08-15", 3),
            ],
        ),
    ]


def demo() -> None:
    print("=" * 58)
    print("  一起点 · 朋友洞察 + 抢券 演示（mock 数据，无需 Token）")
    print("=" * 58)

    print("\n—— 朋友洞察 ——")
    for f in _mock_friends():
        ins = analyze_insights(f)
        print(f"  {ins['name']}: 常点 {ins['常点']} | 避雷 {ins['避雷']} "
              f"| 本月 {ins['本月次数']} 次 | 共 {ins['总订单数']} 单")

    print("\n—— 抢券（五条机制） ——")
    coupon = Coupon(owner="阿强", name="满30减10", discount=10)
    grabbed: list[Coupon] = []
    r = grab_coupon(coupon, grabber="若瑜", in_session=True, already_grabbed=grabbed)
    print("  " + r.msg)
    if r.ok:
        grabbed.append(r.coupon)
        bad = use_coupon(coupon, friend_favorite="巨无霸", chosen_item="麦辣鸡腿堡")
        print("  " + bad.msg)
        good = use_coupon(coupon, friend_favorite="巨无霸", chosen_item="巨无霸")
        print("  " + good.msg)

    r2 = grab_coupon(Coupon("小美", "满20减5", 5), "若瑜", in_session=False, already_grabbed=[])
    print("  " + r2.msg)

    r3 = grab_coupon(Coupon("小美", "满20减5", 5), "若瑜", in_session=True, already_grabbed=grabbed)
    print("  " + r3.msg)


if __name__ == "__main__":
    demo()
