<<<<<<< HEAD
# Agent Instructions

## Cursor Cloud specific instructions

This repo runs as a Docker Compose stack. Cloud agents should use the committed
`.cursor/environment.json` and `.cursor/Dockerfile` configuration.

### Startup

1. The environment `start` command starts the Docker daemon.
2. The `app-stack` terminal runs `docker compose up --build`.
3. Wait for services before testing:
   ```bash
   bash .cursor/cloud-test.sh
   ```

### Manual testing

```bash
cp .env.example .env
docker compose up --build
./validate_poc.bash
```

### Services

| Service | Port | Purpose |
| --- | --- | --- |
| api | 5000 | Falcon REST API |
| db | 5432 | Postgres |
| redis | 6379 | Celery broker/backend |
| worker | — | Celery validation worker |
| monitor | 5555 | Flower dashboard |

### Troubleshooting

- If Docker commands fail, confirm the daemon is running: `sudo service docker start`
- If the API is not ready, inspect the `app-stack` terminal logs
- First `docker compose up --build` can take several minutes while images build
=======
# AGENTS.md

## Cursor Cloud specific instructions

This is a Falcon REST API SaaS template orchestrated entirely through `docker-compose.yml`.
It pins Python 3.8 and old dependency versions (e.g. `celery==4.4.7`, `falcon==3.0.0`), so it
must be run inside its Docker image (the host VM has Python 3.12, which is incompatible). Docker
(with the `fuse-overlayfs` storage driver and `containerd-snapshotter` disabled) is already
installed in the VM snapshot.

### Services (all defined in `docker-compose.yml`)
- `api` — gunicorn serving Falcon on `:5000` (`--reload` hot-reloads the `./app` bind mount).
- `db` — Postgres on `:5432`.
- `redis` — Celery broker/backend on `:6379`.
- `worker` — Celery worker (`tasks.fib`); logs to `./logs/celery.log`, NOT stdout.
- `monitor` — Flower Celery dashboard on `:5555`.

### Running everything
- The Docker daemon is not running at startup. Start it first (it is not auto-started):
  `sudo dockerd > /tmp/dockerd.log 2>&1 &`
- `.env` is required for compose variable interpolation; copy it from `.env.example` if missing
  (the update script does this automatically).
- Bring the stack up with `sudo docker compose up -d --build` (use `sudo` — the daemon runs as root).
- Startup race gotcha: `depends_on` does not wait for Postgres readiness, so the `api` container
  may `Exit (3)` on the first `up` with `psycopg2 OperationalError ... "db" ... Connection refused`.
  Just re-run `sudo docker compose up -d api` once Postgres is up; it then boots cleanly.

### Tests
- The test suite lives in `app/tests/__init__.py` (non-standard filename) and mixes a relative
  import (`from ..api`) with a top-level `import tasks`. Run it from `/src` with `app` on the path:
  `sudo docker compose exec -T -w /src -e PYTHONPATH=/src/app api python -m pytest app/tests/__init__.py -v`
- There is no configured linter (no flake8/black/pylint); use `python -m py_compile` for a syntax check.

### Known pre-existing bug (do NOT fix unless asked)
- `app/api.py` registers route resources using the imported **modules**
  (`from resources import WorkerResource`) instead of class **instances**
  (`WorkerResource.WorkerResource()`). As a result every HTTP route returns `405 Method Not Allowed`,
  and `test_base_endpoint` fails. The underlying stack is healthy — the Celery async pipeline
  (enqueue → Redis → worker → result) and the Postgres/SQLAlchemy `Session` both work when invoked
  directly (e.g. `fib.delay(8)` returns `[0,1,1,2,3,5,8,13,21]`).
>>>>>>> origin/main
