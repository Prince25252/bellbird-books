# ST-04 / ST-05 / ST-06 used book business rule tests
#
# DoD requirement: logic that distinguishes new/used stock must include automated tests.
# This file covers:
#   - ST-04 used book individual intake (A08: each is a separate entity)
#   - ST-05 edit condition / price / shelf
#   - ST-06 sold marking (individual instance, does not affect other copies of the same title)
#   - Used book ISBN is optional (A02)
import pytest
from src.services.inventory import InventoryService
from src.storage import JsonStorage
@pytest.fixture()
def svc(tmp_path):
    return InventoryService(JsonStorage(str(tmp_path)))
def test_st04_add_used_book_creates_individual_entity(svc):
    uid = svc.add_used_book("The Hobbit", "J.R.R. Tolkien", condition="Good",
                            sale_price=12.0, shelf_location="U-01")
    ub = svc.search_used_books("hobbit")
    assert len(ub) == 1
    assert ub[0]["id"] == uid
    assert ub[0]["status"] == "available"
    assert ub[0]["condition"] == "Good"
def test_st04_same_title_creates_two_entities(svc):
    """Two copies of the same title are two separate records (A08)."""
    svc.add_used_book("The Hobbit", condition="Good", sale_price=10.0)
    svc.add_used_book("The Hobbit", condition="As New", sale_price=15.0)
    assert len(svc.search_used_books("hobbit")) == 2
def test_st04_isbn_optional_for_used(svc):
    """Used book ISBN is optional (A02)."""
    uid = svc.add_used_book("Old Book", author="Someone")
    assert uid > 0
    assert len(svc.search_used_books("old")) == 1
def test_st04_title_required(svc):
    with pytest.raises(ValueError):
        svc.add_used_book("")
def test_st05_edit_used_book_condition_and_price(svc):
    uid = svc.add_used_book("The Hobbit", condition="Good", sale_price=10.0, shelf_location="U-01")
    svc.update_used_book(uid, condition="Very Good", sale_price=14.0, shelf_location="U-02")
    ub = svc.search_used_books("hobbit")[0]
    assert ub["condition"] == "Very Good"
    assert ub["sale_price"] == 14.0
    assert ub["shelf_location"] == "U-02"
def test_st06_mark_used_book_sold_does_not_affect_others(svc):
    uid1 = svc.add_used_book("The Hobbit", condition="Good", sale_price=10.0)
    uid2 = svc.add_used_book("The Hobbit", condition="As New", sale_price=15.0)
    svc.mark_used_book_sold(uid1, sold_price=10.0)
    ubs = svc.search_used_books("hobbit", only_available=True)
    # Only the other copy is still for sale
    assert len(ubs) == 1
    assert ubs[0]["id"] == uid2
    # The original copy's status is now sold
    full = svc.search_used_books("hobbit", only_available=False)
    sold = next(b for b in full if b["id"] == uid1)
    assert sold["status"] == "sold"
    assert sold["sold_date"]
def test_st06_cannot_sell_already_sold_book(svc):
    uid = svc.add_used_book("The Hobbit", sale_price=10.0)
    svc.mark_used_book_sold(uid)
    with pytest.raises(KeyError):
        svc.mark_used_book_sold(uid)
