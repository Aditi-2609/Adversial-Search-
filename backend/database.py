import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(os.environ.get(
    "SIMULATOR_DB_PATH",
    str(Path(__file__).resolve().parent / "simulator.db"),
))

SCHEMA = """
CREATE TABLE IF NOT EXISTS simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    input_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    expected_utility REAL,
    risk_score REAL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout = 10000")
    return con

def init_db():
    with closing(get_connection()) as con:
        con.execute("PRAGMA journal_mode = WAL")
        con.execute(SCHEMA)
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_simulations_created_at "
            "ON simulations(created_at DESC)"
        )
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_simulations_algorithm "
            "ON simulations(algorithm)"
        )
        con.commit()

def save_simulation(name, algorithm, inputs, result, expected_utility=None, risk_score=None):
    with closing(get_connection()) as con:
        cur = con.execute(
            "INSERT INTO simulations (name, algorithm, input_json, result_json, expected_utility, risk_score) VALUES (?, ?, ?, ?, ?, ?)",
            (
                name,
                algorithm,
                json.dumps(inputs, allow_nan=False),
                json.dumps(result, allow_nan=False),
                expected_utility,
                risk_score,
            ),
        )
        con.commit()
        return cur.lastrowid
