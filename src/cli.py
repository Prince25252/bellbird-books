# Command-line entry point
#
# Usage examples:
#   python -m src.cli add-new-book "Title" "Author" --quantity 5
#   python -m src.cli search "keyword"
#   python -m src.cli list-new
import argparse
import json
import sys
from .services.inventory import InventoryService
from .services.customers import CustomerService
from .services.orders import OrderService
from .storage import JsonStorage
def build_service(data_dir: str = "data") -> InventoryService:
    return InventoryService(JsonStorage(data_dir))
def _print(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="bellbird-books", description="Bellbird Books inventory and order system")
    parser.add_argument("--data-dir", default="data", help="data directory")
    sub = parser.add_subparsers(dest="command")
    p_add = sub.add_parser("add-new-book", help="add a new book (ST-01)")
    p_add.add_argument("title")
    p_add.add_argument("author")
    p_add.add_argument("--publisher", default="")
    p_add.add_argument("--isbn", default="")
    p_add.add_argument("--price", type=float, default=0.0)
    p_add.add_argument("--quantity", type=int, default=1)
    p_add.add_argument("--shelf", default="")
    p_list = sub.add_parser("list-new", help="list new book stock")
    p_search = sub.add_parser("search", help="combined stock search (ST-07)")
    p_search.add_argument("keyword", nargs="?", default="")
    p_used = sub.add_parser("add-used-book", help="add a used book (ST-04)")
    p_used.add_argument("title")
    p_used.add_argument("--author", default="")
    p_used.add_argument("--condition", default="")
    p_used.add_argument("--cost", type=float, default=0.0)
    p_used.add_argument("--price", type=float, default=0.0)
    p_used.add_argument("--shelf", default="")
    p_cust = sub.add_parser("add-customer", help="add a customer (ST-09)")
    p_cust.add_argument("name")
    p_cust.add_argument("--phone", default="")
    p_cust.add_argument("--email", default="")
    p_cust.add_argument("--pref", default="either")
    p_order = sub.add_parser("add-order", help="create a booking order (ST-10)")
    p_order.add_argument("--customer", type=int, required=True)
    p_order.add_argument("--type", default="new", choices=["new", "used"])
    p_order.add_argument("--book", type=int, default=0)
    p_order.add_argument("--deposit", type=float, default=0.0)
    p_overdue = sub.add_parser("overdue-orders", help="list overdue uncollected orders (ST-13)")
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
    elif args.command == "add-used-book":
        uid = svc.add_used_book(args.title, args.author, "", args.condition,
                                args.cost, "", args.price, args.shelf)
        _print({"id": uid, "status": "available"})
    elif args.command == "add-customer":
        cs = CustomerService(svc.storage)
        _print({"id": cs.add_customer(args.name, args.phone, args.email, args.pref)})
    elif args.command == "add-order":
        osvc = OrderService(svc.storage)
        _print({"id": osvc.create_order(args.customer, args.type, args.book, args.deposit)})
    elif args.command == "overdue-orders":
        osvc = OrderService(svc.storage)
        _print({"overdue": osvc.return_overdue_orders()})
    else:
        parser.print_help()
        return 1
    return 0
if __name__ == "__main__":
    sys.exit(main())
