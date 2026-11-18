# Adversarial Search Simulator

A focused Flask and vanilla JavaScript Tic-Tac-Toe app. Play against an AI that uses Minimax or Alpha-Beta Pruning, adjust search depth, and inspect its best move, evaluated nodes, pruned branches, execution time, and actual root-move scores.

The server stores submitted game states and search results in SQLite.

## Run locally (Windows)

From the project directory:

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 backend\app.py
```

Open `http://127.0.0.1:5000`. The Flask server hosts both the frontend and API on the same origin. The default SQLite file is `backend\simulator.db`; set `SIMULATOR_DB_PATH` to use another file.

## Deploy with Docker

Requires Docker Engine and Docker Compose:

```powershell
docker compose up --build -d
```

Open `http://localhost:8000`. SQLite data is stored in the persistent `simulator_data` volume. Use `docker compose logs -f simulator` to view logs and `docker compose down` to stop the service. `docker compose down` preserves the named data volume.

For a platform that builds directly from the Dockerfile, expose container port `8000`, mount persistent storage at `/data`, and set `SIMULATOR_DB_PATH=/data/simulator.db`. The app uses the platform's `PORT` environment variable.

## Tests

```powershell
py -3.13 -m unittest discover -s backend\tests -p "test_*.py"
```

## Deployment limitations

This is a single-instance academic/demo app without accounts or per-user data isolation. Do not expose it publicly with private data until authentication and authorization have been added. SQLite requires a durable volume and is not intended for horizontal scaling.
