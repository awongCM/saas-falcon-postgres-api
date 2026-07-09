# Email / Domain Validator

Async SaaS proof of concept for checking recruiter and cold-email senders. Submit an email or domain, run DNS/MX/SPF/DMARC checks in a background worker, and get a legitimacy score with a plain-English recommendation.

Built with Falcon, Postgres, Redis, Celery, SQLAlchemy, and dnspython.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Service health and endpoint summary |
| `POST` | `/validate` | Queue validation job (`X-API-Key` required) |
| `GET` | `/validate/{job_id}` | Poll job status and validation result (`X-API-Key` required) |
| `GET` | `/validate?limit=20` | List recent validation jobs (`X-API-Key` required) |

Set `API_KEY` in `.env`. Optional `RATE_LIMIT_PER_MINUTE` defaults to `30`.

Database migrations run automatically on API startup via Alembic.

## Run locally

```bash
cp .env.example .env
docker compose up --build
chmod +x validate_poc.bash
./validate_poc.bash
```

## Run in Cursor Cloud Agent

This repo includes `.cursor/environment.json` and `.cursor/Dockerfile` for cloud
agent testing with Docker Compose.

1. Start a cloud agent on this branch (do not use an old saved snapshot that
   overrides the Dockerfile config).
2. Wait for the `app-stack` terminal to finish building and start services.
3. Run the end-to-end smoke test:

```bash
bash .cursor/cloud-test.sh
```

Flower monitor: http://localhost:5555

## Example

```bash
curl http://localhost:5000/

curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-local-api-key" \
  -d '{"type":"email","value":"recruiter@acme.com"}'

curl -H "X-API-Key: dev-local-api-key" http://localhost:5000/validate/1
```

## What gets checked

- Email format validity
- Domain DNS resolution (A/AAAA)
- MX records
- SPF and DMARC records
- Disposable email domains
- Free webmail providers
- Role-based mailboxes (`noreply@`, `recruiting@`, etc.)

Each job returns a score from 0–100, `is_likely_legit`, signal list, and recommendation.

## Architecture

```
POST /validate -> Postgres job row -> Celery worker -> DNS checks -> result stored
GET /validate/{id} -> read result from Postgres
```
