# Customer business logic (src/services/customers.py)
#
# ST-09 Customer intake: record name / phone / email / contact preference (A11),
# accumulate store credit (A03/A18).
from typing import List, Optional
from ..models import Customer
from ..storage import JsonStorage
class CustomerService:
    def __init__(self, storage: JsonStorage):
        self.storage = storage
    def add_customer(self, name: str, phone: str = "", email: str = "",
                     contact_preference: str = "either", notes: str = "") -> int:
        """Add a customer (ST-09). Contact preference defaults to either (A11)."""
        if not name:
            raise ValueError("Customer name is required")
        if contact_preference not in ("phone", "email", "either"):
            raise ValueError("contact_preference must be phone / email / either")
        cid = self.storage.next_id("customer")
        c = Customer.new(cid, name, phone, email, contact_preference, notes)
        self.storage.get_list("customers").append(c.to_dict())
        self.storage.save()
        return cid
    def get_customer(self, customer_id: int) -> Optional[dict]:
        for c in self.storage.get_list("customers"):
            if c["id"] == customer_id:
                return c
        return None
    def search_customers(self, keyword: str = "") -> List[dict]:
        """Fuzzy search customers by name / phone / email."""
        kw = keyword.strip().lower()
        out = []
        for c in self.storage.get_list("customers"):
            if kw and kw not in c["name"].lower() and kw not in (c["phone"] or "").lower() \
                    and kw not in (c["email"] or "").lower():
                continue
            out.append(c)
        return out
    def adjust_store_credit(self, customer_id: int, delta: float) -> float:
        """Accumulate store credit (A03/A18): deposits, order refunds, etc. increase it;
        purchases decrease it. Negative means owing."""
        for c in self.storage.get_list("customers"):
            if c["id"] == customer_id:
                c["store_credit"] = round(float(c["store_credit"]) + float(delta), 2)
                self.storage.save()
                return c["store_credit"]
        raise KeyError(f"Customer not found: id={customer_id}")
