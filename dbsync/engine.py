import sqlite3
import time
from typing import List
from .checkpoint import CheckpointManager

class SyncEngine:
    """Core streaming sync engine with batch chunking and resumption."""
    def __init__(self, source_uri: str, target_uri: str, chunk_size: int = 1000, checkpoint_path: str = ".dbsync_checkpoint.json"):
        self.source_uri = source_uri
        self.target_uri = target_uri
        self.chunk_size = chunk_size
        self.checkpoint = CheckpointManager(checkpoint_path)

    def _connect(self, uri: str):
        # Support sqlite URIs for standalone operation
        cleaned = uri.replace("sqlite:///", "")
        return sqlite3.connect(cleaned)

    def migrate_table(self, table_name: str, pk_col: str = "id", resume: bool = True):
        src_conn = self._connect(self.source_uri)
        tgt_conn = self._connect(self.target_uri)
        src_cur = src_conn.cursor()
        tgt_cur = tgt_conn.cursor()

        last_id = self.checkpoint.get_last_id(table_name) if resume else 0
        print(f"[*] Syncing table '{table_name}' starting after {pk_col}={last_id}...")

        # Total remaining rows count
        src_cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {pk_col} > ?", (last_id,))
        total_rows = src_cur.fetchone()[0]
        if total_rows == 0:
            print(f"  [+] Table '{table_name}' is already up-to-date.")
            return

        migrated = 0
        start_time = time.time()

        while True:
            src_cur.execute(
                f"SELECT * FROM {table_name} WHERE {pk_col} > ? ORDER BY {pk_col} ASC LIMIT ?",
                (last_id, self.chunk_size)
            )
            rows = src_cur.fetchall()
            if not rows:
                break

            cols = [d[0] for d in src_cur.description]
            placeholders = ",".join(["?"] * len(cols))
            insert_sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(cols)}) VALUES ({placeholders})"

            tgt_cur.executemany(insert_sql, rows)
            tgt_conn.commit()

            pk_idx = cols.index(pk_col) if pk_col in cols else 0
            last_id = rows[-1][pk_idx]
            self.checkpoint.set_last_id(table_name, last_id)

            migrated += len(rows)
            elapsed = time.time() - start_time
            rate = migrated / elapsed if elapsed > 0 else 0
            pct = min(100.0, (migrated / total_rows) * 100)

            print(f"\r  --> [{pct:5.1f}%] {migrated}/{total_rows} rows transferred ({rate:6.0f} rows/s)", end="", flush=True)

        print(f"\n[+] Successfully completed sync for table '{table_name}'.")
        src_conn.close()
        tgt_conn.close()

    def verify_counts(self, tables: List[str]):
        src_conn = self._connect(self.source_uri)
        tgt_conn = self._connect(self.target_uri)
        print("=== Database Verification Report ===")
        for t in tables:
            s_count = src_conn.cursor().execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            t_count = tgt_conn.cursor().execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            status = "MATCH" if s_count == t_count else "MISMATCH"
            print(f"  Table '{t}': Source={s_count} | Target={t_count} [{status}]")
        src_conn.close()
        tgt_conn.close()
