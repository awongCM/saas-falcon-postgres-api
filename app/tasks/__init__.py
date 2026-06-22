import json
import os
from time import sleep

import celery

from database import Session
from models import ValidationJob
from validators import validate_domain, validate_email

CELERY_BROKER = os.environ.get('CELERY_BROKER')
CELERY_BACKEND = os.environ.get('CELERY_BACKEND')

app = celery.Celery('tasks', broker=CELERY_BROKER, backend=CELERY_BACKEND)


@app.task
def fib(n):
    sleep(2)  # simulate slow computation
    if n < 0:
        return []
    elif n == 0:
        return [0]
    elif n == 1:
        return [0, 1]
    else:
        results = fib(n - 1)
        results.append(results[-1] + results[-2])
        return results


@app.task(bind=True)
def run_validation(self, job_id):
    session = Session()
    try:
        job = session.query(ValidationJob).filter_by(id=job_id).first()
        if not job:
            return {'error': f'Validation job {job_id} not found'}

        job.status = 'STARTED'
        session.commit()

        if job.input_type == 'email':
            result = validate_email(job.input_value)
        else:
            result = validate_domain(job.input_value)

        job.result = json.dumps(result)
        job.status = 'SUCCESS'
        session.commit()
        return result
    except Exception as exc:
        session.rollback()
        job = session.query(ValidationJob).filter_by(id=job_id).first()
        if job:
            job.status = 'FAILURE'
            job.result = json.dumps({'error': str(exc)})
            session.commit()
        raise
    finally:
        Session.remove()
