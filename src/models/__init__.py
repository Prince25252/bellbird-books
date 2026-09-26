"""数据模型：NewBook / UsedBook / Customer / Order

依据 Confluence《数据模型设计》：
- 新书为数量聚合模型（A07）：同一（书名+作者+ISBN）合并为一条记录，用 quantity 管理副本数。
- 二手书为单本实例模型（A08）：每本独立实体，品相 / 成本 / 售价 / 来源 / 货架各不同，售出一本不影响其他。
- 订单通过 bookType + bookRefId 复合关联新书或二手书（A13）。
- 删除统一软删除（A15）：status 标记，不做物理删除。
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class NewBook:
    """新书条目（库存聚合模型）—— ST-01 / ST-02 / ST-03"""
    id: int
    title: str
    author: str
    publisher: str = ""
    isbn: str = ""                # 新书必填（A02）
    price: float = 0.0
    quantity: int = 0             # 库存数量 >= 0；到货 + / 售出 −
    shelf_location: str = ""      # 区域 / 货架（ST-08）
    status: str = "active"        # active / inactive（软下架，A15）
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def new(cls, next_id: int, title: str, author: str, publisher: str = "",
            isbn: str = "", price: float = 0.0, quantity: int = 0,
            shelf_location: str = "") -> "NewBook":
        now = _now()
        return cls(id=next_id, title=title, author=author, publisher=publisher,
                   isbn=isbn, price=price, quantity=quantity,
                   shelf_location=shelf_location, created_at=now, updated_at=now)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "NewBook":
        return cls(**d)


@dataclass
class UsedBook:
    """二手书实体（单本实例模型）—— ST-04 / ST-05 / ST-06"""
    id: int
    title: str
    author: str = ""
    isbn: str = ""                # 二手书 ISBN 可空（A02）
    condition: str = ""           # As New / Very Good / Good / Fair / Reading Copy
    purchase_cost: float = 0.0
    purchase_source: str = ""
    sale_price: float = 0.0
    shelf_location: str = ""
    status: str = "available"     # available / sold / removed（A15）
    acquired_date: str = ""
    sold_date: str = ""
    notes: str = ""

    @classmethod
    def new(cls, next_id: int, title: str, author: str = "", isbn: str = "",
            condition: str = "", purchase_cost: float = 0.0, purchase_source: str = "",
            sale_price: float = 0.0, shelf_location: str = "", notes: str = "") -> "UsedBook":
        now = _now()
        return cls(id=next_id, title=title, author=author, isbn=isbn, condition=condition,
                   purchase_cost=purchase_cost, purchase_source=purchase_source,
                   sale_price=sale_price, shelf_location=shelf_location,
                   acquired_date=now, notes=notes)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "UsedBook":
        return cls(**d)


@dataclass
class Customer:
    """客户 —— ST-09"""
    id: int
    name: str
    phone: str = ""
    email: str = ""
    contact_preference: str = "either"  # phone / email / either（A11）
    store_credit: float = 0.0           # 店铺信用（A03/A18）
    notes: str = ""

    @classmethod
    def new(cls, next_id: int, name: str, phone: str = "", email: str = "",
            contact_preference: str = "either", notes: str = "") -> "Customer":
        return cls(id=next_id, name=name, phone=phone, email=email,
                   contact_preference=contact_preference, notes=notes)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Customer":
        return cls(**d)


@dataclass
class Order:
    """订单 —— ST-10 / ST-11 / ST-12 / ST-13"""
    id: int
    customer_id: int
    book_type: str = "new"          # new / used（A13）
    book_ref_id: int = 0
    order_date: str = ""
    deposit: float = 0.0            # 定金（A03 简单记录）
    status: str = "ordered"         # ordered/arrived/notified/collected/cancelled（A16）
    notified_at: str = ""           # 14 天退回计算基准（ST-13）
    notes: str = ""

    @classmethod
    def new(cls, next_id: int, customer_id: int, book_type: str = "new",
            book_ref_id: int = 0, deposit: float = 0.0, notes: str = "") -> "Order":
        return cls(id=next_id, customer_id=customer_id, book_type=book_type,
                   book_ref_id=book_ref_id, order_date=_now(), deposit=deposit, notes=notes)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Order":
        return cls(**d)
