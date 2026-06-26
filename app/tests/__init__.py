import unittest
from unittest.mock import MagicMock

from falcon import testing

from api import api as app
from middlewares import SQLAlchemySessionManager


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
        self.assertIn('POST /validate', result.json['endpoints']['queue_validation'])


if __name__ == '__main__':
    unittest.main()
