import sqlite3
import os

# Resolve paths relative to THIS file's location, not the CWD.
# This ensures the script works regardless of where it's invoked from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(BASE_DIR, 'nafood.db')
schema_path = os.path.join(BASE_DIR, 'sql', 'schema.sql')
seed_path = os.path.join(BASE_DIR, 'sql', 'seed_data.sql')


def build_db() -> None:
    # AUTO-RESET: wipe stale DB so schema changes are always applied cleanly
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Cleaned up old database at {db_path}...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable FK enforcement — SQLite disables this by default, which would
    # silently allow referential integrity violations in seed data
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("Building schema...")
    with open(schema_path, 'r') as f:
        cursor.executescript(f.read())

    print("Seeding data...")
    with open(seed_path, 'r') as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print(f"Done. NAFood database ready at {db_path}")


if __name__ == "__main__":
    build_db()