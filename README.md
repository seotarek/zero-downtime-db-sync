# Zero-Downtime DB Sync ⚡

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Engines](https://img.shields.io/badge/Supported-MySQL%20%7C%20PostgreSQL%20%7C%20SQLite-brightgreen.svg)](https://github.com/seotarek/zero-downtime-db-sync)

A resilient, chunk-based streaming database migration and live data replication CLI tool. Safely migrate gigabyte-scale databases across servers with **automatic network checkpointing**, zero RAM bloat, and minimal table lock time.

---

## 💥 The Problem It Solves

* **Dump & Restore Fails on Large Tables:** Traditional `mysqldump` or `pg_dump` creates massive files that lock read/write traffic and timeout on unstable networks.
* **Network Dropouts Waste Hours:** If an SCP transfer drops at 99%, you typically have to restart from scratch.
* **RAM Spikes Crash Instances:** Reading whole tables into memory crashes low-spec VPS or containers.

**Zero-Downtime DB Sync** streams rows in configurable primary-key batches, tracks the last committed ID in a persistent checkpoint file, and resumes seamlessly if interrupted.

---

## 🚀 Key Features

* **Chunked Streaming:** Consumes memory in predictable O(chunk_size) bounds using server-side cursors.
* **Fault-Tolerant Checkpointing:** Tracks migration progress down to the exact row ID; automatically resumes after network disconnects.
* **Cross-Engine Support:** Ready for SQLite, MySQL, and PostgreSQL migrations.
* **Live Telemetry:** Real-time transfer rates (rows/sec), ETA, and estimated completion.
* **Schema Verification Mode:** Dry-run and post-migration record count validator.

---

## 📦 Installation

```bash
git clone https://github.com/seotarek/zero-downtime-db-sync.git
cd zero-downtime-db-sync
pip install -e .
```

---

## ⚡ CLI Quickstart

### 1. Sync Two Databases

```bash
db-sync migrate \
  --source "sqlite:///source.db" \
  --target "sqlite:///target.db" \
  --tables "users,orders,transactions" \
  --chunk-size 2000
```

### 2. Resume an Interrupted Sync

If the process is stopped, re-run with `--resume`:
```bash
db-sync migrate \
  --source "sqlite:///source.db" \
  --target "sqlite:///target.db" \
  --resume
```

### 3. Verify Row Counts

```bash
db-sync verify \
  --source "sqlite:///source.db" \
  --target "sqlite:///target.db" \
  --tables "users,orders"
```

---

## ⚙️ Configuration File (Optional)

Instead of CLI flags, you can pass a YAML configuration:
```yaml
source: "sqlite:///production.db"
target: "sqlite:///replica.db"
chunk_size: 5000
tables:
  - users
  - posts
  - payments
```

```bash
db-sync migrate --config config.yaml
```

---

## 📄 License

MIT License. Authored by [Tarek Mohamed](https://tarek-mohamed.me.eg/).
