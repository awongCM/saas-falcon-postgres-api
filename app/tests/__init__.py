import json
import os
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from falcon import testing

from api import api as app
from middlewares import SQLAlchemySessionManager
from resources.ValidationResource import _serialize_job, _sync_job_status


class TestHealthEndpoint(testing.TestCase):

    def setUp(self):
        super().setUp()
        self.app = app
        self.mock_session = MagicMock()
        self.mock_session.query.return_value.count.return_value = 3
        self.original_process_resource = SQLAlchemySessionManager.process_resource

        def inject_session(middleware, req, resp, resource, params):
            resource.session = self.mock_session

        SQLAlchemySessionManager.process_resource = inject_session

    def tearDown(self):
        SQLAlchemySessionManager.process_resource = self.original_process_resource
        super().tearDown()

    def test_health_endpoint(self):
        result = self.simulate_get('/')

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['service'], 'email-domain-validator')
        self.assertEqual(result.json['status'], 'ok')
        self.assertEqual(result.json['stats']['validation_jobs_total'], 3)


class TestValidationAPI(testing.TestCase):

    def setUp(self):
        super().setUp()
        self.app = app
        os.environ['API_KEY'] = 'test-api-key'
        os.environ['RATE_LIMIT_PER_MINUTE'] = '0'
        self.mock_session = MagicMock()
        self.original_process_resource = SQLAlchemySessionManager.process_resource

        def inject_session(middleware, req, resp, resource, params):
            resource.session = self.mock_session

        SQLAlchemySessionManager.process_resource = inject_session

    def tearDown(self):
        SQLAlchemySessionManager.process_resource = self.original_process_resource
        super().tearDown()

    def test_post_requires_api_key(self):
        result = self.simulate_post('/validate', json={'type': 'email', 'value': 'a@b.com'})
        self.assertEqual(result.status_code, 401)

    @patch('resources.ValidationResource.run_validation')
    def test_post_queues_validation(self, mock_run_validation):
        mock_task = MagicMock()
        mock_task.id = 'task-123'
        mock_run_validation.delay.return_value = mock_task

        def add_job(job):
            job.id = 7

        self.mock_session.add.side_effect = add_job

        result = self.simulate_post(
            '/validate',
            json={'type': 'email', 'value': 'recruiter@acme.com'},
            headers={'X-API-Key': 'test-api-key'},
        )

        self.assertEqual(result.status_code, 202)
        self.assertEqual(result.json['data']['job_id'], 7)
        mock_run_validation.delay.assert_called_once_with(7)

    @patch('resources.ValidationResource.run_validation')
    def test_post_marks_failure_when_enqueue_fails(self, mock_run_validation):
        mock_run_validation.delay.side_effect = RuntimeError('redis down')

        captured = {}

        def add_job(job):
            captured['job'] = job
            job.id = 9

        self.mock_session.add.side_effect = add_job

        result = self.simulate_post(
            '/validate',
            json={'type': 'domain', 'value': 'acme.com'},
            headers={'X-API-Key': 'test-api-key'},
        )

        self.assertEqual(result.status_code, 503)
        self.assertEqual(captured['job'].status, 'FAILURE')

    def test_post_rejects_domain_with_at_sign(self):
        result = self.simulate_post(
            '/validate',
            json={'type': 'domain', 'value': 'user@acme.com'},
            headers={'X-API-Key': 'test-api-key'},
        )
        self.assertEqual(result.status_code, 400)

    def test_get_rejects_invalid_limit(self):
        result = self.simulate_get('/validate?limit=abc', headers={'X-API-Key': 'test-api-key'})
        self.assertEqual(result.status_code, 400)

    def test_status_rejects_non_integer_job_id(self):
        result = self.simulate_get('/validate/not-an-id', headers={'X-API-Key': 'test-api-key'})
        self.assertEqual(result.status_code, 400)


class TestValidationHelpers(unittest.TestCase):

    def test_serialize_job_handles_invalid_json(self):
        job = MagicMock()
        job.id = 1
        job.celery_task_id = 'task-1'
        job.input_type = 'email'
        job.input_value = 'a@b.com'
        job.status = 'SUCCESS'
        job.created_at = datetime(2026, 7, 9, tzinfo=timezone.utc)
        job.updated_at = datetime(2026, 7, 9, tzinfo=timezone.utc)
        job.result = '{not valid json'

        payload = _serialize_job(job, include_result=True)
        self.assertIn('error', payload['result'])

    @patch('resources.ValidationResource.AsyncResult')
    def test_sync_job_status_updates_from_celery(self, mock_async_result):
        session = MagicMock()
        job = MagicMock()
        job.status = 'PENDING'
        job.celery_task_id = 'task-99'
        job.result = None

        task = MagicMock()
        task.state = 'SUCCESS'
        task.result = {'score': 90}
        mock_async_result.return_value = task

        updated = _sync_job_status(session, job)
        self.assertEqual(updated.status, 'SUCCESS')
        session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
