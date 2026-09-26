# ST-01 / ST-02 新书业务规则测试
#
# DoD 强制要求：凡涉及新书 / 二手库存区分逻辑，必须包含该业务场景的自动化测试。
# 本文件覆盖：
#   - ST-01 录入新书，数量正确
#   - A07 同一（书名+作者+ISBN）重复录入自动合并数量，不建重复条目
#   - 数量不可为负
#   - ST-02 售出扣减 / 到货增加
#   - 持久化：保存后重新加载数据仍在（关联 ST-14）
import os
import tempfile

import pytest

from src.inventory import InventoryService
from src.storage import JsonStorage


@pytest.fixture()
def svc(tmp_path):
    """每个用例使用独立的临时数据目录，互不干扰。"""
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
    assert len(books) == 1, "同（书名+作者+ISBN）不应建立重复条目（A07）"
    assert books[0]["quantity"] == 5


def test_st01_different_edition_is_separate(svc):
    """同一书名、不同 ISBN（版本）应作为独立条目。"""
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
    """写入后重新加载存储，数据不丢失（ST-14）。"""
    svc.add_new_book("Dune", "Frank Herbert", isbn="123", quantity=4)
    # 用同一目录新建存储实例，模拟程序重启
    storage2 = JsonStorage(str(tmp_path))
    svc2 = InventoryService(storage2)
    books = svc2.search_new_books("Dune")
    assert len(books) == 1
    assert books[0]["quantity"] == 4
