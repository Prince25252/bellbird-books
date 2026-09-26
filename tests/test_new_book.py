# ST-01 / ST-02 new book business rule tests
#
# DoD requirement: any logic that distinguishes new/used stock must include automated tests
# for that business scenario.
# This file covers:
#   - ST-01 add a new book, quantity correct
#   - A07 re-adding the same (title+author+ISBN) merges quantity, no duplicate entry
#   - Quantity cannot be negative
#   - ST-02 sales decrease / arrivals increase
#   - Persistence: data survives a save-then-reload (linked to ST-14)
import os
import tempfile
import pytest
from src.services.inventory import InventoryService
from src.storage import JsonStorage
@pytest.fixture()
def svc(tmp_path):
    """Each test uses an independent temp data directory, so they never interfere."""
    storage = JsonStorage(str(tmp_path))
    return InventoryService(storage)
def test_st01_add_new_book_records_quantity(svc):
    bid, qty = svc.add_new_book("Dune", "Frank Herbert", isbn="123", price=20.0, quantity=5)
    assert qty == 5
    books = svc.search_new_books("dune")
    assert len(books) == 1
    assert books[0]["title"] == "Dune"
    assert books[0]["quantity"] == 5
def test_st01_same_title_author_isbn_merges_quantity(svc):
    svc.add_new_book("Dune", "Frank Herbert", isbn="123", quantity=3)
    bid, qty = svc.add_new_book("Dune", "Frank Herbert", isbn="123", quantity=2)
    books = svc.search_new_books("Dune")
    assert len(books) == 1, "Same (title+author+ISBN) must not create duplicate entries (A07)"
    assert books[0]["quantity"] == 5
def test_st01_different_edition_is_separate(svc):
    """The same title with a different ISBN (edition) is a separate entry."""
    svc.add_new_book("Dune", "Frank Herbert", isbn="111", quantity=1)
    svc.add_new_book("Dune", "Frank Herbert", isbn="222", quantity=2)
    assert len(svc.search_new_books("Dune")) == 2
def test_st01_quantity_cannot_be_negative(svc):
    with pytest.raises(ValueError):
        svc.add_new_book("Dune", "Frank Herbert", quantity=-1)
def test_st01_title_author_required(svc):
    with pytest.raises(ValueError):
        svc.add_new_book("", "Frank Herbert")
def test_st02_sell_decreases_quantity(svc):
    bid, _ = svc.add_new_book("Dune", "Frank Herbert", quantity=5)
    new_qty = svc.adjust_new_book_quantity(bid, -1)
    assert new_qty == 4
def test_st02_stock_cannot_go_below_zero(svc):
    bid, _ = svc.add_new_book("Dune", "Frank Herbert", quantity=1)
    with pytest.raises(ValueError):
        svc.adjust_new_book_quantity(bid, -2)
def test_st02_arrival_increases_quantity(svc):
    bid, _ = svc.add_new_book("Dune", "Frank Herbert", quantity=2)
    new_qty = svc.adjust_new_book_quantity(bid, +3)
    assert new_qty == 5
def test_persistence_after_reload(svc, tmp_path):
    """Write data, then reload the storage to simulate a restart; nothing is lost (ST-14)."""
    svc.add_new_book("Dune", "Frank Herbert", isbn="123", quantity=4)
    storage2 = JsonStorage(str(tmp_path))
    svc2 = InventoryService(storage2)
    books = svc2.search_new_books("Dune")
    assert len(books) == 1
    assert books[0]["quantity"] == 4
def test_st03_soft_delete_new_book(svc):
    """Soft remove (A15): active -> inactive, no physical deletion."""
    bid, _ = svc.add_new_book("Dune", "Frank Herbert", isbn="123", quantity=3)
    svc.deactivate_new_book(bid)
    assert svc.search_new_books("Dune") == []
    all_ = svc.search_new_books("Dune", only_active=False)
    assert len(all_) == 1
    assert all_[0]["status"] == "inactive"
def test_st03_reactivate_new_book(svc):
    bid, _ = svc.add_new_book("Dune", "Frank Herbert", isbn="123", quantity=2)
    svc.deactivate_new_book(bid)
    svc.reactivate_new_book(bid)
    assert len(svc.search_new_books("Dune")) == 1
    assert svc.search_new_books("Dune")[0]["status"] == "active"
def test_st03_merged_quantity_only_counts_active(svc):
    """Re-adding the same title after removal creates a new entry, not merging into the removed one."""
    svc.add_new_book("Dune", "Frank Herbert", isbn="123", quantity=3)
    bid = svc.search_new_books("Dune")[0]["id"]
    svc.deactivate_new_book(bid)
    svc.add_new_book("Dune", "Frank Herbert", isbn="123", quantity=2)
    assert len(svc.search_new_books("Dune")) == 1
    assert svc.search_new_books("Dune")[0]["quantity"] == 2
