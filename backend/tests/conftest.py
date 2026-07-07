import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./rulees_test.sqlite"
os.environ.setdefault("SECRET_KEY", "test-secret")

test_db = Path("rulees_test.sqlite")
if test_db.exists():
    test_db.unlink()
