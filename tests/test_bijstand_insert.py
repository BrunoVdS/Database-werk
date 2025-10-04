from __future__ import annotations
import importlib.util
import sys
from pathlib import Path


def load_module():
    module_path = Path(__file__).resolve().parents[1] / "LCCU Database.py"
    sys.path.insert(0, str(module_path.parent))
    spec = importlib.util.spec_from_file_location("lccu_database", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_bijstand_insert_stores_type(tmp_path, monkeypatch):
    module = load_module()
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("LCCU_DB_PATH", str(db_path))

    module.check_or_create_database()

    object_id = module.insert_bijstand_record(
        soort_bijstand="Noodhulp",
        dienst="DOT",
        medewerkers=["Alice", "Bob"],
        start_bijstand="2024-01-01 10:00:00",
        einde_bijstand="2024-01-01 12:00:00",
        datum_ingave="2024-01-01 09:00:00",
        unique_id=1234,
    )

    with module.connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT type, soort_bijstand FROM objecten WHERE id = ?",
            (object_id,),
        )
        row = cursor.fetchone()

    assert row == ("Bijstand", "Noodhulp")
