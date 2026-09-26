# Inventory business logic (src/services/inventory.py)
#
# ST-01 New book intake: aggregate management by 'title + quantity' (A07). Re-adding the same
# (title+author+ISBN) merges quantities instead of creating duplicate entries.
# ST-02 New book quantity change: arrivals increase / sales decrease.
# ST-04/ST-06 Used book individual intake and sold marking.
# ST-03 New book soft delete / removal (A15).
# ST-05 / ST-06 Used book editing and sale.
from datetime import datetime
from typing import List, Optional
from ..models import NewBook, UsedBook
from ..storage import JsonStorage
class InventoryService:
    def __init__(self, storage: JsonStorage):
        self.storage = storage
    # ---------- ST-01 / ST-02: New books ----------
    def add_new_book(self, title: str, author: str, publisher: str = "",
                     isbn: str = "", price: float = 0.0, quantity: int = 1,
                     shelf_location: str = "") -> tuple:
        """Add a new book (ST-01). Entries with the same (title+author+ISBN) and active status
        merge quantities. Returns (id, latest quantity)."""
        if not title or not author:
            raise ValueError("Title and author are required")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
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
        """Adjust new book quantity (ST-02): positive for arrivals, negative for sales.
        Quantity can never be negative."""
        books = self.storage.get_list("new_books")
        for b in books:
            if b["id"] == book_id and b["status"] == "active":
                new_qty = b["quantity"] + delta
                if new_qty < 0:
                    raise ValueError("Quantity cannot be negative")
                b["quantity"] = new_qty
                b["updated_at"] = datetime.now().isoformat(timespec="seconds")
                self.storage.save()
                return new_qty
        raise KeyError(f"New book not found: id={book_id}")
    def search_new_books(self, keyword: str = "", only_active: bool = True) -> List[dict]:
        """Fuzzy search new books by title / author (part of ST-07 combined search)."""
        kw = keyword.strip().lower()
        out = []
        for b in self.storage.get_list("new_books"):
            if only_active and b["status"] != "active":
                continue
            if kw and kw not in b["title"].lower() and kw not in b["author"].lower():
                continue
            out.append(b)
        return out
    # ---------- ST-04 / ST-06: Used books ----------
    def add_used_book(self, title: str, author: str = "", isbn: str = "",
                      condition: str = "", purchase_cost: float = 0.0,
                      purchase_source: str = "", sale_price: float = 0.0,
                      shelf_location: str = "", notes: str = "") -> int:
        """Add a used book (ST-04): each one is a separate entity."""
        if not title:
            raise ValueError("Title is required")
        uid = self.storage.next_id("used_book")
        ub = UsedBook.new(uid, title, author, isbn, condition, purchase_cost,
                          purchase_source, sale_price, shelf_location, notes)
        self.storage.get_list("used_books").append(ub.to_dict())
        self.storage.save()
        return uid
    def search_used_books(self, keyword: str = "", only_available: bool = True) -> List[dict]:
        """Fuzzy search used books by title / author (part of ST-07)."""
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
        """Combined inventory search (ST-07): new + used books, results tagged by type."""
        return {
            "new_books": self.search_new_books(keyword),
            "used_books": self.search_used_books(keyword),
        }
    # ---------- ST-03: New book soft delete / removal ----------
    def deactivate_new_book(self, book_id: int) -> str:
        """Soft-remove a new book (ST-03 / A15): set status to inactive, no physical deletion."""
        books = self.storage.get_list("new_books")
        for b in books:
            if b["id"] == book_id and b["status"] == "active":
                b["status"] = "inactive"
                b["updated_at"] = datetime.now().isoformat(timespec="seconds")
                self.storage.save()
                return "inactive"
        raise KeyError(f"Active new book not found: id={book_id}")
    def reactivate_new_book(self, book_id: int) -> str:
        """Re-list a previously removed new book (inverse of ST-03)."""
        books = self.storage.get_list("new_books")
        for b in books:
            if b["id"] == book_id and b["status"] == "inactive":
                b["status"] = "active"
                b["updated_at"] = datetime.now().isoformat(timespec="seconds")
                self.storage.save()
                return "active"
        raise KeyError(f"Inactive new book not found: id={book_id}")
    # ---------- ST-05 / ST-06: Used book editing and sale ----------
    def update_used_book(self, used_id: int, condition: str = None,
                         sale_price: float = None, shelf_location: str = None,
                         notes: str = None) -> dict:
        """Edit a used book's condition / price / shelf (ST-05)."""
        for b in self.storage.get_list("used_books"):
            if b["id"] == used_id:
                if condition is not None:
                    b["condition"] = condition
                if sale_price is not None:
                    b["sale_price"] = float(sale_price)
                if shelf_location is not None:
                    b["shelf_location"] = shelf_location
                if notes is not None:
                    b["notes"] = notes
                self.storage.save()
                return b
        raise KeyError(f"Used book not found: id={used_id}")
    def mark_used_book_sold(self, used_id: int, sold_price: float = None) -> dict:
        """Mark a used book as sold (ST-06): status=sold, record price and sale date
        (A08 individual-instance model)."""
        for b in self.storage.get_list("used_books"):
            if b["id"] == used_id and b["status"] == "available":
                b["status"] = "sold"
                if sold_price is not None:
                    b["sale_price"] = float(sold_price)
                b["sold_date"] = datetime.now().isoformat(timespec="seconds")
                self.storage.save()
                return b
        raise KeyError(f"Available used book not found: id={used_id}")
