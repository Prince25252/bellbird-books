# 本地 JSON 持久化（ST-14）
#
# 数据以单文件 JSON 保存到 data/db.json，程序重启后不丢失。
# 满足业务假设 A05（本地文件持久化，无需数据库服务）。
import json
import os
import threading


class JsonStorage:
    """线程安全的最小 JSON 存储：整库读写，简单可靠。"""

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
            # 兜底：旧数据缺少 counters 时补齐
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
        """清空数据（仅测试用）。"""
        with self._lock:
            self._data = self._empty()
            self.save()
