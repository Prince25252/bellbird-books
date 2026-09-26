# ST-09 customer business rule tests
#
# Covers:
#   - ST-09 add a customer (name / phone / email / contact preference A11)
#   - Name is required
#   - Contact preference enum validation
#   - Store credit accumulation (A03/A18)
import pytest
from src.services.customers import CustomerService
from src.storage import JsonStorage
@pytest.fixture()
def svc(tmp_path):
    return CustomerService(JsonStorage(str(tmp_path)))
def test_st09_add_customer(svc):
    cid = svc.add_customer("Alice", phone="0400000000", email="a@x.com",
                           contact_preference="email")
    c = svc.get_customer(cid)
    assert c["name"] == "Alice"
    assert c["contact_preference"] == "email"
    assert c["store_credit"] == 0.0
def test_st09_name_required(svc):
    with pytest.raises(ValueError):
        svc.add_customer("")
def test_st09_contact_preference_enum(svc):
    with pytest.raises(ValueError):
        svc.add_customer("Bob", contact_preference="sms")
def test_st09_search_by_keyword(svc):
    svc.add_customer("Alice", phone="0400 111 222")
    svc.add_customer("Bob", email="bob@x.com")
    assert len(svc.search_customers("alice")) == 1
    assert len(svc.search_customers("0400")) == 1
    assert len(svc.search_customers("bob@x")) == 1
    assert len(svc.search_customers("")) == 2
def test_st09_store_credit_accumulates(svc):
    cid = svc.add_customer("Alice")
    assert svc.adjust_store_credit(cid, 20.0) == 20.0
    assert svc.adjust_store_credit(cid, -5.0) == 15.0
