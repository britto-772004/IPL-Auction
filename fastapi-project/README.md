# Backend API

A FastAPI backend with MongoDB (via Motor async driver) connectivity, exposing a health endpoint that reports the status of the database, and structured logging shipped to Loki/Grafana.

## Project structure

```
backend/
├── compose.yaml                 # Docker Compose services: MongoDB, Loki, Grafana
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── loki.yaml         # Auto-provisions the Loki datasource in Grafana
├── pyproject.toml                # Project metadata, dependencies, ruff config
├── uv.lock                       # Locked dependency versions (managed by uv)
├── .python-version               # Python version pinned for the project (3.12)
├── .pre-commit-config.yaml       # Pre-commit hooks (ruff lint + format)
├── .env                          # Local environment variables (git-ignored, not committed)
├── .env.example                  # Template for required environment variables
├── .gitignore
├── README.md
├── src/
│   └── backend/
│       ├── __init__.py           # Package entrypoint (`main()` for the `backend` script)
│       ├── main.py               # FastAPI app, lifespan (DB setup/teardown), health endpoint
│       └── config/
│           ├── env_config.py       # Pydantic Settings — loads and validates env vars from .env
│           ├── database_config.py  # Builds the Motor (MongoDB async) client from settings
│           └── logging_config.py   # Configures console + Loki logging handlers
```

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker + Docker Compose (to run MongoDB, Loki and Grafana locally)

## Setup

1. **Clone the repo and move into it**

   ```bash
   cd backend
   ```

2. **Create your `.env` file**

   Copy the example file and fill in real values:

   ```bash
   cp .env.example .env
   ```

   | Variable | Description |
   |---|---|
   | `APP_HOST` | Host the backend binds to (default `0.0.0.0`) |
   | `APP_PORT` | Port the backend binds to (default `8000`) |
   | `MONGO_INITDB_ROOT_USERNAME` | Username used to initialize the MongoDB container |
   | `MONGO_INITDB_ROOT_PASSWORD` | Password used to initialize the MongoDB container |
   | `MONGO_INITDB_DATABASE` | Database name created in the MongoDB container |
   | `MONGODB_URL` | Full Mongo connection string the app uses, e.g. `mongodb://mongo:changeme@localhost:27017/backend?authSource=admin` |
   | `LOG_LEVEL` | Minimum log level for the app (default `INFO`) |
   | `LOKI_URL` | Loki push endpoint the app ships logs to (default `http://localhost:3100/loki/api/v1/push`) |
   | `GRAFANA_ADMIN_USER` | Grafana login username, created on the container's first start |
   | `GRAFANA_ADMIN_PASSWORD` | Grafana login password, created on the container's first start |

   Make sure the credentials inside `MONGODB_URL` match `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` / `MONGO_INITDB_DATABASE`.

   > `GRAFANA_ADMIN_USER`/`GRAFANA_ADMIN_PASSWORD` only take effect the first time the `grafana` container starts (they seed the account in its data volume). If you change them later, remove the volume to re-seed: `docker compose rm -sf grafana && docker volume rm backend_grafana_data && docker compose up -d grafana`.

3. **Start MongoDB, Loki and Grafana**

   ```bash
   docker compose up -d
   ```

4. **Install dependencies**

   ```bash
   uv sync
   ```

5. **Run the app**

   ```bash
   uv run backend
   ```

   This starts uvicorn using `APP_HOST` / `APP_PORT` from `.env`. For local development with auto-reload, use uvicorn directly (reads the same host/port from `.env` via settings is not supported with `--reload` flags, so pass them explicitly if you changed the defaults):

   ```bash
   uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000` (or whatever `APP_PORT` you set).

6. **Check the health endpoint**

   ```bash
   curl http://localhost:8000/api/v1/health
   ```

   Example response:

   ```json
   {"status": "healthy", "database": "connected"}
   ```

   Returns HTTP `200` when MongoDB is reachable, or `503` with `"status": "unhealthy"` if it is down.

## Viewing application logs

The app logs to two places at once:

- **Your terminal** — every log line prints to stdout wherever you run `uv run backend` / `uvicorn`.
- **Grafana** at [http://localhost:3000](http://localhost:3000):
  1. Log in with `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` from your `.env` (e.g. `admin` / whatever you set).
  2. Open the left sidebar → **Explore** (compass icon).
  3. Make sure the **Loki** datasource is selected at the top (it's pre-provisioned and set as default).
  4. Enter this query and run it:

     ```
     {service="backend"}
     ```

  This shows every log line the app has shipped, including startup/shutdown events and each health check result.

You can also query Loki directly without Grafana:

```bash
curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={service="backend"}'
```

## Linting / formatting

```bash
uv run ruff check --fix
uv run ruff format
```

Pre-commit hooks run these automatically on each commit:

```bash
uv run pre-commit install
```
