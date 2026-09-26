# Bellbird Books

Inventory and customer order management system for Bellbird Books.

## Requirements

- Python 3.10+

## Setup

```bash
# Clone the repository
git clone https://github.com/Prince25252/bellbird-books.git
cd bellbird-books

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the application

```bash
python -m src.cli
```

## Running tests

```bash
pytest
```

## Implemented features

- **ST-01 新书录入库存**：`src/services/inventory.py::add_new_book` 按（书名+作者+ISBN）聚合管理（A07），重复录入自动合并数量。
- **ST-02 新书数量增减**：到货增加 / 售出扣减，数量不可为负。
- **ST-14 本地 JSON 持久化**：`src/storage/`，数据保存于 `data/db.json`，重启不丢失。
- **CLI**：`python -m src.cli add-new-book "书名" "作者" --quantity 5`
- **自动化测试**：`tests/test_new_book.py`（pytest，覆盖 ST-01 / ST-02 与 A07 合并逻辑）

## Project structure

```
bellbird-books/
├── src/                    # Application source code
│   ├── models/             # Data models (NewBook, UsedBook, Customer, Order)
│   ├── services/           # Business logic (inventory, order management)
│   ├── storage/            # Persistence layer (JSON file storage)
│   └── cli.py              # Command-line entry point
├── tests/                  # Automated tests
│   ├── test_smoke.py       # Test runner smoke test
│   ├── test_new_book.py    # New book inventory business logic tests (ST-01/02)
│   ├── test_used_book.py   # Used book inventory business logic tests
│   └── test_order.py       # Order lifecycle tests
├── docs/                   # Project documentation
├── scripts/                # Setup and utility scripts
├── config/                 # Configuration templates
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
└── README.md
```

## Branching rules

- `main` is the protected integration branch.
- Never commit directly to `main`.
- Create feature branches using `feature/short-description`.
- Every change must be reviewed through a Pull Request before merging.
- No self-approval on your own PR.

## Commit message convention

Use Conventional Commits:

- `feat: add a new feature`
- `fix: fix a bug`
- `test: add or update tests`
- `docs: update documentation`
- `chore: maintenance or tooling changes`
- `refactor: refactor code without changing behavior`
