# 库存业务逻辑
#
# ST-01 新书录入库存：按「书名+数量」聚合管理（A07），同一（书名+作者+ISBN）
# 重复录入时自动合并数量，不建重复条目。
# ST-02 新书数量增减：到货增加 / 售出扣减。
# ST-04/ST-06 二手书独立录入与售出标记（骨架，后续故事实现）。
from datetime import datetime
from typing import List, Optional

from .models import NewBook, UsedBook
from .storage import JsonStorage


class InventoryService:
    def __init__(self, storage: JsonStorage):
        self.storage = storage

    # ---------- ST-01 / ST-02：新书 ----------

    def add_new_book(self, title: str, author: str, publisher: str = "",
                     isbn: str = "", price: float = 0.0, quantity: int = 1,
                     shelf_location: str = "") -> tuple:
        """录入新书（ST-01）。同（书名+作者+ISBN）且 active 的条目合并数量。返回 (id, 最新数量)。"""
        if not title or not author:
            raise ValueError("书名与作者必填")
        if quantity < 0:
            raise ValueError("数量不能为负")

        books = self.storage.get_list("new_books")
        for b in books:
            if (b["title"] == title and b["author"] == author
                    and b["isbn"] == isbn and b["status"] == "active"):
                b["quantity"] += quantity
                b["updated_at"] = datetime.now().isoformat(timespec="seconds")
                self.storage.save()
                return b["id"], b["quantity"]

        bid = self.storage.next_id("new_book")
        nb = NewBook.new(bid, title, author, publisher, isbn, price, quantity, shelf_location)
        books.append(nb.to_dict())
        self.storage.save()
        return bid, quantity

    def adjust_new_book_quantity(self, book_id: int, delta: int) -> int:
        """调整新书数量（ST-02）：到货为正，售出为负。数量不可为负。"""
        books = self.storage.get_list("new_books")
        for b in books:
            if b["id"] == book_id and b["status"] == "active":
                new_qty = b["quantity"] + delta
                if new_qty < 0:
                    raise ValueError("数量不能为负")
                b["quantity"] = new_qty
                b["updated_at"] = datetime.now().isoformat(timespec="seconds")
                self.storage.save()
                return new_qty
        raise KeyError(f"未找到新书 id={book_id}")

    def search_new_books(self, keyword: str = "", only_active: bool = True) -> List[dict]:
        """按书名 / 作者模糊搜索新书（ST-07 联合搜索的一部分）。"""
        kw = keyword.strip().lower()
        out = []
        for b in self.storage.get_list("new_books"):
            if only_active and b["status"] != "active":
                continue
            if kw and kw not in b["title"].lower() and kw not in b["author"].lower():
                continue
            out.append(b)
        return out

    # ---------- ST-04 / ST-06：二手书（骨架） ----------

    def add_used_book(self, title: str, author: str = "", isbn: str = "",
                      condition: str = "", purchase_cost: float = 0.0,
                      purchase_source: str = "", sale_price: float = 0.0,
                      shelf_location: str = "", notes: str = "") -> int:
        """录入二手书（ST-04）：每本独立实体。"""
        if not title:
            raise ValueError("书名必填")
        uid = self.storage.next_id("used_book")
        ub = UsedBook.new(uid, title, author, isbn, condition, purchase_cost,
                          purchase_source, sale_price, shelf_location, notes)
        self.storage.get_list("used_books").append(ub.to_dict())
        self.storage.save()
        return uid

    def search_used_books(self, keyword: str = "", only_available: bool = True) -> List[dict]:
        """按书名 / 作者模糊搜索二手书（ST-07 的一部分）。"""
        kw = keyword.strip().lower()
        out = []
        for b in self.storage.get_list("used_books"):
            if only_available and b["status"] != "available":
                continue
            if kw and kw not in b["title"].lower() and kw not in (b["author"] or "").lower():
                continue
            out.append(b)
        return out

    def search_all(self, keyword: str = "") -> dict:
        """库存联合搜索（ST-07）：新书 + 二手书，结果标注类型。"""
        return {
            "new_books": self.search_new_books(keyword),
            "used_books": self.search_used_books(keyword),
        }
