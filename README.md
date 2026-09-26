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

## Project structure

```
bellbird-books/
├── src/                    # Application source code
│   ├── models/             # Data models (NewBook, UsedBook, Customer, Order)
│   ├── services/           # Business logic (inventory, order management)
│   ├── storage/            # Persistence layer (JSON file storage)
│   └── cli.py              # Command-line entry point
├── tests/                  # Automated tests
│   ├── test_new_book.py    # New book inventory business logic tests
│   ├── test_used_book.py  # Used book inventory business logic tests
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