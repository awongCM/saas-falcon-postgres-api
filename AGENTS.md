# Agent Instructions

## Cursor Cloud specific instructions

This repo runs as a Docker Compose stack for the email/domain validator POC. Cloud
agents should use the committed `.cursor/environment.json` and `.cursor/Dockerfile`
configuration (Docker CE with `fuse-overlayfs` and `iptables-legacy`).

The app pins Python 3.8 and older dependencies (e.g. `celery==4.4.7`, `falcon==3.0.0`),
so run it inside Docker — the host VM uses Python 3.12, which is incompatible.

### Startup

1. The environment `start` command starts the Docker daemon.
2. The `app-stack` terminal runs `docker compose up --build`.
3. Wait for services before testing:
   ```bash
   bash .cursor/cloud-test.sh
   ```

If Docker is not running manually, start it first (it is not auto-started):

```bash
sudo dockerd > /tmp/dockerd.log 2>&1 &
```

`.env` is required for compose variable interpolation. Copy from `.env.example` if missing
(the cloud install script does this automatically).

Bring the stack up with `sudo docker compose up -d --build` when the daemon runs as root.

Startup race: `depends_on` does not wait for Postgres readiness, so `api` may exit once
with `psycopg2 OperationalError ... "db" ... Connection refused` on first boot.
Re-run `sudo docker compose up -d api` after Postgres is up.

### Manual testing

```bash
cp .env.example .env
docker compose up --build
./validate_poc.bash
```

`/validate` endpoints require the `X-API-Key` header (see `API_KEY` in `.env`).
The API container runs `alembic upgrade head` on startup before gunicorn.

### Services

| Service | Port | Purpose |
| --- | --- | --- |
| api | 5000 | Falcon REST API (gunicorn `--reload` hot-reloads the `./app` bind mount) |
| db | 5432 | Postgres |
| redis | 6379 | Celery broker/backend |
| worker | — | Celery validation worker (`run_validation`) |
| monitor | 5555 | Flower dashboard |

### Tests

Validator unit tests (no Docker required for scoring logic):

```bash
cd app && PYTHONPATH=/workspace/app python3 tests/test_validators.py -v
```

Full API tests run inside the api container:

```bash
sudo docker compose exec -T -w /src -e PYTHONPATH=/src/app api python -m pytest app/tests/__init__.py -v
```

There is no configured linter (no flake8/black/pylint); use `python -m py_compile` for a syntax check.

### Troubleshooting

- If Docker commands fail, confirm the daemon is running: `sudo service docker start`
- If the API is not ready, inspect the `app-stack` terminal logs
- First `docker compose up --build` can take several minutes while images build
- Celery worker logs go to `./logs/celery.log`, not stdout
