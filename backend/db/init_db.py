"""Create demo.db schema (Skills_core §13)."""
from pathlib import Path
import sqlite3

from backend.config import DB_PATH, SCHEMA_PATH


def main() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(DB_PATH)) as conn:
        sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(sql)
        conn.commit()
    print(f"OK demo.db schema ready at {DB_PATH}")


if __name__ == "__main__":
    main()
