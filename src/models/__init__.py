"""Data models: NewBook / UsedBook / Customer / Order
Based on the Confluence 'Data Model Design':
- New books use an aggregate model (A07): identical (title+author+ISBN) entries merge into
  one record, using quantity to track the number of copies.
- Used books use an individual-instance model (A08): each is a separate entity with its own
  condition / cost / price / source / shelf; selling one does not affect the others.
- Orders link to a new or used book through the composite (bookType + bookRefId) key (A13).
- Deletion is soft-delete (A15): a status flag, never a physical removal.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
@dataclass
class NewBook:
    """New book entry (aggregate inventory model) -- ST-01 / ST-02 / ST-03"""
    id: int
    title: str
    author: str
    publisher: str = ""
    isbn: str = ""                # Required for new books (A02)
    price: float = 0.0
    quantity: int = 0             # Stock quantity >= 0; arrivals + / sales -
    shelf_location: str = ""      # Zone / shelf (ST-08)
    status: str = "active"        # active / inactive (soft remove, A15)
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
    """Used book entity (individual-instance model) -- ST-04 / ST-05 / ST-06"""
    id: int
    title: str
    author: str = ""
    isbn: str = ""                # ISBN optional for used books (A02)
    condition: str = ""           # As New / Very Good / Good / Fair / Reading Copy
    purchase_cost: float = 0.0
    purchase_source: str = ""
    sale_price: float = 0.0
    shelf_location: str = ""
    status: str = "available"     # available / sold / removed (A15)
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
    """Customer -- ST-09"""
    id: int
    name: str
    phone: str = ""
    email: str = ""
    contact_preference: str = "either"  # phone / email / either (A11)
    store_credit: float = 0.0           # Store credit (A03/A18)
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
    """Order -- ST-10 / ST-11 / ST-12 / ST-13"""
    id: int
    customer_id: int
    book_type: str = "new"          # new / used (A13)
    book_ref_id: int = 0
    order_date: str = ""
    deposit: float = 0.0            # Deposit (A03 simple record)
    status: str = "ordered"         # ordered/arrived/notified/collected/cancelled (A16)
    notified_at: str = ""           # Basis for the 14-day return rule (ST-13)
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
