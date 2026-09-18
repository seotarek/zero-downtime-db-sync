import json
import os
from typing import Optional, Dict

class CheckpointManager:
    """Stores and retrieves the last successfully synced primary key or row offset."""
    def __init__(self, filepath: str = ".dbsync_checkpoint.json"):
        self.filepath = filepath
        self._data: Dict[str, int] = {}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}
        else:
            self._data = {}

    def get_last_id(self, table: str) -> int:
        return self._data.get(table, 0)

    def set_last_id(self, table: str, last_id: int):
        self._data[table] = last_id
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def clear(self, table: Optional[str] = None):
        if table and table in self._data:
            del self._data[table]
        elif not table:
            self._data = {}
        if os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
