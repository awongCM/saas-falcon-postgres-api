import json
import logging

import falcon
from celery.result import AsyncResult

from auth import require_api_key
from models import ValidationJob
from ratelimit import enforce_rate_limit
from tasks import run_validation

logger = logging.getLogger(__name__)

MAX_INPUT_LENGTH = 512


class ValidationResource:

    def on_post(self, req, resp):
        require_api_key(req)
        enforce_rate_limit(req)

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

        if len(input_value) > MAX_INPUT_LENGTH:
            raise falcon.HTTPBadRequest(
                title='Value too long',
                description=f'value must be {MAX_INPUT_LENGTH} characters or fewer.',
            )

        if input_type == 'domain' and '@' in input_value:
            raise falcon.HTTPBadRequest(
                title='Invalid domain',
                description='domain value must not contain "@".',
            )

        job = ValidationJob(
            celery_task_id='pending',
            input_type=input_type,
            input_value=input_value,
            status='PENDING',
        )
        self.session.add(job)
        self.session.commit()

        try:
            task = run_validation.delay(job.id)
        except Exception as exc:
            logger.exception('Failed to enqueue validation job %s', job.id)
            job.status = 'FAILURE'
            job.result = json.dumps({'error': 'Failed to enqueue validation task'})
            self.session.commit()
            raise falcon.HTTPServiceUnavailable(
                title='Queue unavailable',
                description='Could not enqueue validation task. Try again shortly.',
            ) from exc

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
        require_api_key(req)
        enforce_rate_limit(req)

        try:
            limit = min(int(req.get_param('limit') or 20), 100)
        except (TypeError, ValueError):
            raise falcon.HTTPBadRequest(
                title='Invalid limit',
                description='limit must be an integer between 1 and 100.',
            )

        if limit < 1:
            raise falcon.HTTPBadRequest(
                title='Invalid limit',
                description='limit must be at least 1.',
            )

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
        require_api_key(req)
        enforce_rate_limit(req)

        try:
            job_id = int(job_id)
        except (TypeError, ValueError):
            raise falcon.HTTPBadRequest(
                title='Invalid job id',
                description='job_id must be an integer.',
            )

        job = self.session.query(ValidationJob).filter_by(id=job_id).first()
        if not job:
            raise falcon.HTTPNotFound(
                title='Job not found',
                description=f'No validation job with id {job_id}.',
            )

        job = _sync_job_status(self.session, job)

        resp.status = falcon.HTTP_200
        resp.media = {
            'status': 'success',
            'data': _serialize_job(job, include_result=True),
        }


def _sync_job_status(session, job):
    if job.status in {'SUCCESS', 'FAILURE'}:
        return job

    if not job.celery_task_id or job.celery_task_id == 'pending':
        return job

    task_result = AsyncResult(job.celery_task_id)
    celery_state = task_result.state

    if celery_state == 'STARTED' and job.status != 'STARTED':
        job.status = 'STARTED'
        session.commit()
        return job

    if celery_state == 'SUCCESS':
        if job.status != 'SUCCESS':
            job.status = 'SUCCESS'
            if task_result.result and not job.result:
                job.result = json.dumps(task_result.result)
            session.commit()
        return job

    if celery_state == 'FAILURE':
        job.status = 'FAILURE'
        job.result = json.dumps({'error': str(task_result.result)})
        session.commit()

    return job


def _serialize_job(job, include_result=True):
    payload = {
        'job_id': job.id,
        'task_id': job.celery_task_id,
        'input_type': job.input_type,
        'input_value': job.input_value,
        'status': job.status,
        'created_at': job.created_at.isoformat().replace('+00:00', 'Z'),
        'updated_at': job.updated_at.isoformat().replace('+00:00', 'Z'),
    }

    if include_result and job.result:
        try:
            payload['result'] = json.loads(job.result)
        except json.JSONDecodeError:
            logger.warning('Invalid JSON stored for validation job %s', job.id)
            payload['result'] = {'error': 'Stored result is invalid JSON'}

    return payload
