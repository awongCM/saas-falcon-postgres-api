import json

import falcon

from models import ValidationJob
from tasks import run_validation


class ValidationResource:

    def on_post(self, req, resp):
        try:
            payload = json.load(req.stream)
        except json.JSONDecodeError:
            raise falcon.HTTPBadRequest(
                title='Invalid JSON',
                description='Request body must be valid JSON.',
            )

        input_type = payload.get('type', '').strip().lower()
        input_value = payload.get('value', '').strip()

        if input_type not in {'email', 'domain'}:
            raise falcon.HTTPBadRequest(
                title='Invalid type',
                description='type must be either "email" or "domain".',
            )

        if not input_value:
            raise falcon.HTTPBadRequest(
                title='Missing value',
                description='value is required.',
            )

        job = ValidationJob(
            celery_task_id='pending',
            input_type=input_type,
            input_value=input_value,
            status='PENDING',
        )
        self.session.add(job)
        self.session.commit()

        task = run_validation.delay(job.id)
        job.celery_task_id = task.id
        self.session.commit()

        resp.status = falcon.HTTP_202
        resp.media = {
            'status': 'accepted',
            'data': {
                'job_id': job.id,
                'task_id': task.id,
                'input_type': input_type,
                'input_value': input_value,
            },
        }

    def on_get(self, req, resp):
        limit = min(int(req.get_param('limit') or 20), 100)
        jobs = (
            self.session.query(ValidationJob)
            .order_by(ValidationJob.created_at.desc())
            .limit(limit)
            .all()
        )

        resp.status = falcon.HTTP_200
        resp.media = {
            'status': 'success',
            'data': [_serialize_job(job, include_result=False) for job in jobs],
        }


class ValidationStatusResource:

    def on_get(self, req, resp, job_id):
        job = self.session.query(ValidationJob).filter_by(id=job_id).first()
        if not job:
            raise falcon.HTTPNotFound(
                title='Job not found',
                description=f'No validation job with id {job_id}.',
            )

        resp.status = falcon.HTTP_200
        resp.media = {
            'status': 'success',
            'data': _serialize_job(job, include_result=True),
        }


def _serialize_job(job, include_result=True):
    payload = {
        'job_id': job.id,
        'task_id': job.celery_task_id,
        'input_type': job.input_type,
        'input_value': job.input_value,
        'status': job.status,
        'created_at': job.created_at.isoformat() + 'Z',
        'updated_at': job.updated_at.isoformat() + 'Z',
    }

    if include_result and job.result:
        payload['result'] = json.loads(job.result)

    return payload
