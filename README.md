# Email / Domain Validator

Async SaaS proof of concept for checking recruiter and cold-email senders. Submit an email or domain, run DNS/MX/SPF/DMARC checks in a background worker, and get a legitimacy score with a plain-English recommendation.

Built with Falcon, Postgres, Redis, Celery, SQLAlchemy, and dnspython.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Service health and endpoint summary |
| `POST` | `/validate` | Queue validation job (`{"type":"email|domain","value":"..."}`) |
| `GET` | `/validate/{job_id}` | Poll job status and validation result |
| `GET` | `/validate?limit=20` | List recent validation jobs |

## Run locally

```bash
cp .env.example .env
docker compose up --build
chmod +x validate_poc.bash
./validate_poc.bash
```

Flower monitor: http://localhost:5555

## Example

```bash
curl http://localhost:5000/

curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{"type":"email","value":"recruiter@acme.com"}'

curl http://localhost:5000/validate/1
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
