import logging
import math
import os
import sys
import time
from contextlib import closing
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import get_connection, init_db, save_simulation
from algorithms.alpha_beta import best_move_alpha_beta
from algorithms.minimax import best_move

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
allowed_origins = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS",
        "http://127.0.0.1:8080,http://localhost:8080",
    ).split(",")
    if origin.strip()
]
CORS(app, origins=allowed_origins)
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper())

WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def bad_request(message):
    return jsonify({"success": False, "error": message}), 400


def json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")
    return data


def integer(data, key, default, minimum, maximum):
    value = data.get(key, default)
    if isinstance(value, bool):
        raise ValueError(f"{key} must be an integer")
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be an integer") from None
    if not math.isfinite(numeric) or not numeric.is_integer():
        raise ValueError(f"{key} must be an integer")
    parsed = int(numeric)
    if not minimum <= parsed <= maximum:
        raise ValueError(f"{key} must be between {minimum} and {maximum}")
    return parsed


def validate_board(data):
    board = data.get("board")
    if not isinstance(board, list) or len(board) != 9:
        raise ValueError("board must contain exactly 9 cells")
    if any(cell not in ("", "X", "O") for cell in board):
        raise ValueError("board cells must be empty, X, or O")
    ai = data.get("ai", "O")
    human = data.get("human", "X")
    if not isinstance(ai, str) or not isinstance(human, str) or {ai, human} != {"X", "O"}:
        raise ValueError("ai and human must be different markers: X and O")
    if board.count("X") not in (board.count("O"), board.count("O") + 1):
        raise ValueError("board has an invalid number of X and O moves")
    if any(all(board[index] == marker for index in line)
           for marker in ("X", "O") for line in WIN_LINES):
        raise ValueError("board is already in a terminal state")
    return board, ai, human


@app.get("/api/health")
def health():
    return jsonify({"success": True, "status": "healthy"})


@app.post("/api/adversarial/simulate")
def adversarial():
    try:
        data = json_object()
        board, ai, human = validate_board(data)
        depth = integer(data, "depth", 6, 1, 9)
        algorithm = data.get("algorithm", "alpha-beta")
        if algorithm not in ("minimax", "alpha-beta"):
            raise ValueError("algorithm must be minimax or alpha-beta")
        name = data.get("name", "Tic-Tac-Toe")
        if not isinstance(name, str) or not name.strip() or len(name) > 100:
            raise ValueError("name must be a non-empty string of at most 100 characters")

        start = time.perf_counter()
        if algorithm == "minimax":
            result = best_move(board.copy(), depth, ai, human)
        else:
            result = best_move_alpha_beta(board.copy(), depth, ai, human)
        result.update({
            "execution_time_ms": round((time.perf_counter() - start) * 1000, 3),
            "depth": depth,
            "algorithm": algorithm,
        })
        record_id = save_simulation(name.strip(), algorithm, data, result)
        return jsonify({"success": True, "id": record_id, "result": result})
    except ValueError as exc:
        return bad_request(str(exc))


@app.get("/")
def frontend_index():
    return send_from_directory(PROJECT_ROOT, "index.html")


@app.get("/<path:asset>")
def frontend_asset(asset):
    allowed_pages = {"index.html", "adversarial.html"}
    is_page = asset in allowed_pages
    is_frontend_asset = (
        asset.startswith(("css/", "js/"))
        and Path(asset).suffix in {".css", ".js"}
    )
    if not (is_page or is_frontend_asset):
        abort(404)
    return send_from_directory(PROJECT_ROOT, asset)


@app.errorhandler(HTTPException)
def handle_http_error(exc):
    return jsonify({"success": False, "error": exc.description}), exc.code


@app.errorhandler(Exception)
def handle_error(exc):
    app.logger.exception("Unhandled request error")
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    init_db()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
