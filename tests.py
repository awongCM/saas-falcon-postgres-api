
from falcon import testing

from api import api as app


class TestAPIRoute(testing.TestCase):

    def setUp(self):
        super(TestAPIRoute, self).setUp()
        self.app = app

    def test_base_endpoint(self):
        expected = {
            "message": "hello to sass-falcon-postgres-api"
        }
        result = self.simulate_get('/')
        self.assertEqual(result.json, expected)
