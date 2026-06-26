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
