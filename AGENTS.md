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
