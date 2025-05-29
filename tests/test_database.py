import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pathlib import Path
from dm.database import Database


def test_log_event(tmp_path: Path) -> None:
    db_file = tmp_path / "db.json"
    db = Database(db_file)
    db.log_event("inicio")
    assert db.list_events() == ["inicio"]
    db2 = Database(db_file)
    assert db2.list_events() == ["inicio"]
