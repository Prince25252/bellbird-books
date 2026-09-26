# Customer booking order business logic (src/services/orders.py)
#
# ST-10 Create a booking order: composite (customer + bookType / bookRefId) link (A13).
# ST-11 Order status flow: ordered -> arrived -> notified -> collected; cancellable (cancelled).
# ST-12 Arrival and customer notification.
# ST-13 14-day return if not collected after arrival (A16): computed from notified_at (arrival date).
#
# Inventory linkage (new-book decrement / used-book sale / restock on overdue return) lives on
# the InventoryService side; this service stays single-responsibility and only maintains the
# order entity and its state machine.
from datetime import datetime, timedelta
from typing import List, Optional
from ..models import Order
from ..storage import JsonStorage
# Legal status transitions (A16)
_TRANSITIONS = {
    "ordered":  {"arrived", "cancelled"},
    "arrived":  {"notified", "cancelled"},
    "notified": {"collected", "cancelled"},
    "collected": set(),
    "cancelled": set(),
}
def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")
class OrderService:
    def __init__(self, storage: JsonStorage):
        self.storage = storage
    def create_order(self, customer_id: int, book_type: str = "new",
                     book_ref_id: int = 0, deposit: float = 0.0,
                     notes: str = "") -> int:
        """Create a booking order (ST-10). Validates the customer exists and bookType is legal (A13)."""
        if book_type not in ("new", "used"):
            raise ValueError("book_type must be new / used (A13)")
        if not any(c["id"] == customer_id for c in self.storage.get_list("customers")):
            raise KeyError(f"Customer not found: id={customer_id}")
        oid = self.storage.next_id("order")
        o = Order.new(oid, customer_id, book_type, book_ref_id, deposit, notes)
        self.storage.get_list("orders").append(o.to_dict())
        self.storage.save()
        return oid
    def get_order(self, order_id: int) -> Optional[dict]:
        for o in self.storage.get_list("orders"):
            if o["id"] == order_id:
                return o
        return None
    def list_orders(self, customer_id: int = None, status: str = None) -> List[dict]:
        out = []
        for o in self.storage.get_list("orders"):
            if customer_id is not None and o["customer_id"] != customer_id:
                continue
            if status is not None and o["status"] != status:
                continue
            out.append(o)
        return out
    def _set_status(self, order_id: int, new_status: str) -> dict:
        for o in self.storage.get_list("orders"):
            if o["id"] == order_id:
                cur = o["status"]
                if new_status not in _TRANSITIONS.get(cur, set()):
                    raise ValueError(f"Illegal status transition: {cur} -> {new_status} (A16)")
                o["status"] = new_status
                # On arrival record notified_at as the 14-day return base (ST-13)
                if new_status == "arrived":
                    o["notified_at"] = _now()
                self.storage.save()
                return o
        raise KeyError(f"Order not found: id={order_id}")
    def mark_arrived(self, order_id: int) -> dict:
        """Mark as arrived (ST-12): starts the 14-day return timer."""
        return self._set_status(order_id, "arrived")
    def mark_notified(self, order_id: int) -> dict:
        """Mark as notified to the customer (ST-12)."""
        return self._set_status(order_id, "notified")
    def mark_collected(self, order_id: int) -> dict:
        """Mark as collected by the customer (ST-11)."""
        return self._set_status(order_id, "collected")
    def cancel_order(self, order_id: int) -> dict:
        """Cancel an order (allowed in ordered / arrived / notified stages)."""
        return self._set_status(order_id, "cancelled")
    def days_since_arrival(self, order_id: int) -> Optional[int]:
        """Days elapsed since arrival (notified_at); None if not yet arrived."""
        o = self.get_order(order_id)
        if not o or not o.get("notified_at"):
            return None
        arrived = datetime.fromisoformat(o["notified_at"])
        return (datetime.now() - arrived).days
    def return_overdue_orders(self, overdue_days: int = 14) -> List[dict]:
        """Orders not collected overdue_days days after arrival are judged overdue returns
        (ST-13 / A16).

        Returns the list of overdue orders (still in arrived status, for the caller to restock/notify)."""
        overdue = []
        for o in self.storage.get_list("orders"):
            if o["status"] not in ("arrived", "notified"):
                continue
            days = self.days_since_arrival(o["id"])
            if days is not None and days >= overdue_days:
                overdue.append(o)
        return overdue
