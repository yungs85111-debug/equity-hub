import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / "backend" / ".env", override=True)

DATA_MODE = os.getenv("DATA_MODE", "demo").lower()
EDGAR_USER_AGENT = os.getenv("EDGAR_USER_AGENT", "EQUITY HUB Demo yungs85111@gmail.com")
DB_PATH = ROOT / os.getenv("DB_PATH", "backend/demo.db")
FISCAL_YEAR = int(os.getenv("FISCAL_YEAR", "2023"))
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

DATA_DIR = ROOT / "backend" / "data"
SCHEMA_PATH = ROOT / "backend" / "db" / "schema.sql"
FIXTURE_PATH = DATA_DIR / "demo_fixture.json"
