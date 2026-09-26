# Local JSON persistence (ST-14)
#
# Data is stored as a single JSON file at data/db.json so it survives a restart.
# Satisfies business assumption A05 (local file persistence, no database service needed).
import json
import os
import threading
class JsonStorage:
    """Thread-safe minimal JSON storage: whole-database read/write, simple and reliable."""
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.file_path = os.path.join(data_dir, "db.json")
        self._lock = threading.RLock()
        os.makedirs(data_dir, exist_ok=True)
        self._load()
    def _empty(self) -> dict:
        return {
            "new_books": [],
            "used_books": [],
            "customers": [],
            "orders": [],
            "counters": {"new_book": 0, "used_book": 0, "customer": 0, "order": 0},
        }
    def _load(self) -> None:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            self._data.setdefault("counters", {})
        else:
            self._data = self._empty()
    def save(self) -> None:
        with self._lock:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
    def next_id(self, kind: str) -> int:
        with self._lock:
            self._data["counters"][kind] = int(self._data["counters"].get(kind, 0)) + 1
            return self._data["counters"][kind]
    def get_list(self, kind: str):
        return self._data[kind]
    def reset(self) -> None:
        """Clear all data (testing only)."""
        with self._lock:
            self._data = self._empty()
            self.save()
