import os
import sqlite3
from pathlib import Path
from pymongo import MongoClient
from pymongo import UpdateOne


def main():
    # --- 1. Connect to SQLite ---
    base = Path(__file__).resolve().parent
    sqlite_path = os.getenv('SQLITE_PATH') or str(base / 'db.sqlite3')
    if not Path(sqlite_path).exists():
        print(f"SQLite DB not found at {sqlite_path}")
        return

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    print(f"Connected to SQLite at {sqlite_path}!")

    # --- 2. Connect to MongoDB ---
    mongo_uri = os.getenv('MONGO_URI') or os.getenv('DATABASE_URL') or 'mongodb://127.0.0.1:27017'
    mongo_db_name = os.getenv('MONGO_DB_NAME') or 'quiz_db'
    mongo_client = MongoClient(mongo_uri)
    mongo_db = mongo_client[mongo_db_name]
    print(f"Connected to MongoDB ({mongo_uri}) database '{mongo_db_name}'")

    # --- 3. Get list of tables ---
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in sqlite_cursor.fetchall()]
    # Skip internal sqlite tables
    tables = [t for t in tables if not t.startswith('sqlite_')]
    print("Tables to migrate:", tables)

    # --- 4. Migrate each table (idempotent upsert) ---
    migrated = 0
    for table in tables:
        try:
            # Get table columns and primary key info from pragma
            sqlite_cursor.execute(f"PRAGMA table_info('{table}')")
            pragma_info = sqlite_cursor.fetchall()  # cid, name, type, notnull, dflt_value, pk
            pk_cols = [row[1] for row in pragma_info if row[5]]

            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            columns = [desc[0] for desc in sqlite_cursor.description]

            mongo_collection = mongo_db[table]
            ops = []
            for row in rows:
                doc = dict(zip(columns, row))

                # Build filter for upsert
                if pk_cols:
                    # Use primary key columns
                    filt = {col: doc.get(col) for col in pk_cols}
                elif 'id' in columns:
                    filt = {'id': doc.get('id')}
                else:
                    # Fallback: match on all columns (best-effort idempotency)
                    filt = {col: doc.get(col) for col in columns}

                # Prepare an upsert operation: replace the doc fields
                ops.append(UpdateOne(filt, {'$set': doc}, upsert=True))

            if ops:
                # Execute bulk upsert (unordered for speed)
                mongo_collection.bulk_write(ops, ordered=False)
            migrated += 1
            print(f"Migrated table {table} ({len(ops)} rows, upsert)")
        except Exception as e:
            print(f"Error migrating table {table}: {e}")

    # --- 5. Close SQLite connection ---
    sqlite_conn.close()
    print(f"SQLite connection closed. {migrated} tables migrated.")


if __name__ == '__main__':
    main()
