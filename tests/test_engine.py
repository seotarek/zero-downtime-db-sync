import unittest
import sqlite3
import os
from dbsync.engine import SyncEngine

class TestSyncEngine(unittest.TestCase):
    def setUp(self):
        self.src_db = "test_src.db"
        self.tgt_db = "test_tgt.db"
        self.cp_file = "test_checkpoint.json"

        # Create source
        conn = sqlite3.connect(self.src_db)
        cur = conn.cursor()
        cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        cur.executemany("INSERT INTO users (name) VALUES (?)", [("User 1",), ("User 2",), ("User 3",)])
        conn.commit()
        conn.close()

        # Create target empty
        conn = sqlite3.connect(self.tgt_db)
        cur = conn.cursor()
        cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()
        conn.close()

    def tearDown(self):
        for f in [self.src_db, self.tgt_db, self.cp_file]:
            if os.path.exists(f):
                os.remove(f)

    def test_migration(self):
        engine = SyncEngine(f"sqlite:///{self.src_db}", f"sqlite:///{self.tgt_db}", chunk_size=2, checkpoint_path=self.cp_file)
        engine.migrate_table("users")

        conn = sqlite3.connect(self.tgt_db)
        count = conn.cursor().execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()
        self.assertEqual(count, 3)

if __name__ == "__main__":
    unittest.main()
