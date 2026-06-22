# saas-falcon-postgres-api
Project SAAS weekend with Falcon Restful API services

## Ingredients

* Falcon
* Postgres
* Redis
* Celery
* SQLAlchemy
* Marshmallow
* Alembic
* dnspython (email/domain validation)

Notes on using Celery queue here - https://testdriven.io/blog/asynchronous-tasks-with-falcon-and-celery/

## Email / Domain Validator POC

Async validation for recruiter and cold-email checks. Submit an email or domain, poll for DNS/MX/SPF/DMARC signals, and get a legitimacy score.

### Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/validate` | Queue validation job (`{"type":"email|domain","value":"..."}`) |
| `GET` | `/validate/{job_id}` | Poll job status and validation result |
| `GET` | `/validate?limit=20` | List recent validation jobs |

### Run locally

```bash
cp .env.example .env
docker compose up --build
chmod +x validate_poc.bash
./validate_poc.bash
```

Flower monitor: http://localhost:5555

### Example

```bash
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{"type":"email","value":"recruiter@acme.com"}'

curl http://localhost:5000/validate/1
```