import unittest
from unittest.mock import patch

from falcon import testing

from ..api import api as app
import tasks


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


class TestWorkerTasks(testing.TestCase):
    def setUp(self):
        super(TestWorkerTasks, self).setUp()
        self.app = app

    @patch('tasks.fib')
    def test_mock_tasks_fib(self, mock_fib):
        mock_fib.run.return_value = []
        self.assertEqual(tasks.fib.run(-1), [])
        mock_fib.run.return_value = [0, 1, 1]
        self.assertEqual(tasks.fib.run(2), [0, 1, 1])
        mock_fib.run.return_value = [0, 1, 1, 2, 3]
        self.assertEqual(tasks.fib.run(4), [0, 1, 1, 2, 3])
        mock_fib.run.return_value = [0, 1, 1, 2, 3, 5]
        self.assertEqual(tasks.fib.run(5), [0, 1, 1, 2, 3, 5])


if __name__ == '__main__':
    unittest.main()
