# ST-10 / ST-11 / ST-12 / ST-13 order business rule tests
#
# Covers:
#   - ST-10 create a booking order (customer + bookType/bookRefId composite link A13)
#   - ST-11 state machine: ordered -> arrived -> notified -> collected
#   - ST-12 arrival and notification
#   - ST-13 14-day return if not collected after arrival (A16)
import pytest
from src.services.customers import CustomerService
from src.services.orders import OrderService
from src.storage import JsonStorage
@pytest.fixture()
def order_svc(tmp_path):
    storage = JsonStorage(str(tmp_path))
    cs = CustomerService(storage)
    cid = cs.add_customer("Alice")
    return OrderService(storage), cid
def test_st10_create_order(order_svc):
    osvc, cid = order_svc
    oid = osvc.create_order(cid, book_type="new", book_ref_id=1, deposit=5.0)
    o = osvc.get_order(oid)
    assert o["customer_id"] == cid
    assert o["book_type"] == "new"
    assert o["status"] == "ordered"
def test_st10_book_type_enum(order_svc):
    osvc, cid = order_svc
    with pytest.raises(ValueError):
        osvc.create_order(cid, book_type="digital")
def test_st10_unknown_customer_rejected(order_svc):
    osvc, _ = order_svc
    with pytest.raises(KeyError):
        osvc.create_order(9999)
def test_st11_happy_path_transitions(order_svc):
    osvc, cid = order_svc
    oid = osvc.create_order(cid, book_ref_id=1)
    osvc.mark_arrived(oid)
    osvc.mark_notified(oid)
    osvc.mark_collected(oid)
    assert osvc.get_order(oid)["status"] == "collected"
def test_st11_illegal_transition_rejected(order_svc):
    osvc, cid = order_svc
    oid = osvc.create_order(cid, book_ref_id=1)
    with pytest.raises(ValueError):
        osvc.mark_collected(oid)  # ordered cannot jump straight to collected
def test_st12_arrival_starts_14day_timer(order_svc):
    osvc, cid = order_svc
    oid = osvc.create_order(cid, book_ref_id=1)
    osvc.mark_arrived(oid)
    assert osvc.get_order(oid)["notified_at"] is not None
    assert osvc.days_since_arrival(oid) == 0
def test_st13_cancel_allowed_until_notified(order_svc):
    osvc, cid = order_svc
    oid = osvc.create_order(cid, book_ref_id=1)
    osvc.cancel_order(oid)
    assert osvc.get_order(oid)["status"] == "cancelled"
