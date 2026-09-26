# 命令行入口
#
# 用法示例：
#   python -m src.cli add-new-book "书名" "作者" --quantity 5
#   python -m src.cli search "关键词"
#   python -m src.cli list-new
import argparse
import json
import sys

from .services.inventory import InventoryService
from .storage import JsonStorage


def build_service(data_dir: str = "data") -> InventoryService:
    return InventoryService(JsonStorage(data_dir))


def _print(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="bellbird-books", description="Bellbird Books 库存与订单系统")
    parser.add_argument("--data-dir", default="data", help="数据目录")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add-new-book", help="录入新书（ST-01）")
    p_add.add_argument("title")
    p_add.add_argument("author")
    p_add.add_argument("--publisher", default="")
    p_add.add_argument("--isbn", default="")
    p_add.add_argument("--price", type=float, default=0.0)
    p_add.add_argument("--quantity", type=int, default=1)
    p_add.add_argument("--shelf", default="")

    p_list = sub.add_parser("list-new", help="列出新书库存")

    p_search = sub.add_parser("search", help="库存联合搜索（ST-07）")
    p_search.add_argument("keyword", nargs="?", default="")

    args = parser.parse_args(argv)
    svc = build_service(args.data_dir)

    if args.command == "add-new-book":
        bid, qty = svc.add_new_book(args.title, args.author, args.publisher,
                                    args.isbn, args.price, args.quantity, args.shelf)
        _print({"id": bid, "quantity": qty})
    elif args.command == "list-new":
        _print(svc.search_new_books(""))
    elif args.command == "search":
        _print(svc.search_all(args.keyword))
    else:
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
