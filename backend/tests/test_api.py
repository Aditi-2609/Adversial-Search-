import json
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

import database
from app import app


class TestAdversarialApi(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = Path(self.temp_dir.name) / "test.sqlite3"
        database.init_db()
        self.client = app.test_client()

    def tearDown(self):
        database.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_health_and_kept_pages_are_served(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        home = self.client.get("/")
        self.assertIn(b"Adversarial Search Simulator", home.data)
        home.close()
        game = self.client.get("/adversarial.html")
        self.assertIn(b"Tic-Tac-Toe", game.data)
        game.close()

    def test_removed_modules_are_not_served(self):
        for path in (
            "/dashboard.html", "/game-theory.html", "/probability.html",
            "/optimization.html", "/strategy.html", "/history.html",
            "/backend/simulator.db", "/api/dashboard/analytics",
            "/api/game-theory/analyze", "/api/probability/bayes",
            "/api/optimization/run", "/api/strategy/recommend",
            "/api/simulations/history",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_adversarial_submission_persists_the_board_and_evaluation(self):
        inputs = {
            "name": "Persistence test",
            "board": ["X", "", "", "", "", "", "", "", ""],
            "algorithm": "alpha-beta",
            "depth": 5,
            "ai": "O",
            "human": "X",
        }
        response = self.client.post("/api/adversarial/simulate", json=inputs)
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result["success"], True)
        self.assertTrue(result["result"]["evaluated_moves"])
        self.assertEqual(
            result["result"]["move"],
            max(result["result"]["evaluated_moves"], key=lambda item: item["score"])["move"],
        )

        with closing(database.get_connection()) as con:
            row = con.execute(
                "SELECT input_json, result_json FROM simulations WHERE id = ?",
                (result["id"],),
            ).fetchone()
        self.assertEqual(json.loads(row["input_json"]), inputs)
        self.assertEqual(json.loads(row["result_json"])["move"], result["result"]["move"])

    def test_invalid_game_inputs_return_client_errors(self):
        invalid_requests = (
            {"board": ["X"] * 9, "algorithm": "alpha-beta"},
            {"board": [""] * 9, "algorithm": "unknown"},
            {"board": [""] * 9, "algorithm": "minimax", "depth": 10},
            {"board": ["Z"] + [""] * 8, "algorithm": "minimax"},
            {"board": [""] * 9, "algorithm": "minimax", "ai": []},
        )
        for body in invalid_requests:
            with self.subTest(body=body):
                self.assertEqual(
                    self.client.post("/api/adversarial/simulate", json=body).status_code,
                    400,
                )

    def test_html_assets_are_available_and_unknown_routes_are_404(self):
        asset = self.client.get("/js/adversarial.js")
        self.assertEqual(asset.status_code, 200)
        asset.close()
        self.assertEqual(self.client.get("/missing.html").status_code, 404)


if __name__ == "__main__":
    unittest.main()
