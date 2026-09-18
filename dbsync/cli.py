import sys
import argparse
from .engine import SyncEngine

def main():
    parser = argparse.ArgumentParser(description="Zero-Downtime DB Sync CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Migrate sub-command
    mig_parser = subparsers.add_parser("migrate", help="Sync table data from source to target")
    mig_parser.add_argument("--source", required=True, help="Source database URI (e.g. sqlite:///data.db)")
    mig_parser.add_argument("--target", required=True, help="Target database URI")
    mig_parser.add_argument("--tables", required=True, help="Comma-separated table names")
    mig_parser.add_argument("--chunk-size", type=int, default=1000, help="Row batch size (default 1000)")
    mig_parser.add_argument("--resume", action="store_true", default=True, help="Resume from last checkpoint")

    # Verify sub-command
    ver_parser = subparsers.add_parser("verify", help="Verify record counts across source and target")
    ver_parser.add_argument("--source", required=True)
    ver_parser.add_argument("--target", required=True)
    ver_parser.add_argument("--tables", required=True)

    args = parser.parse_args()
    engine = SyncEngine(source_uri=args.source, target_uri=args.target, chunk_size=getattr(args, 'chunk_size', 1000))
    tables = [t.strip() for t in args.tables.split(",") if t.strip()]

    if args.command == "migrate":
        for table in tables:
            engine.migrate_table(table, resume=args.resume)
    elif args.command == "verify":
        engine.verify_counts(tables)

if __name__ == "__main__":
    main()
