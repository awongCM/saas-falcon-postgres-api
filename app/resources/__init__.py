# TODO - temp import setup
import json

import falcon

from tasks import fib
from celery.result import AsyncResult


class BaseResource:

    def on_get(self, req, resp):

        # TODO: testing the sqlalchemy session middleware integration...
        result = self.session.execute('SELECT * FROM pg_catalog.pg_tables;')
        rows = result.fetchall()
        data = []
        for row in rows:
            data.append(list(row))

        doc = {
            "message": "hello to sass-falcon-postgres-api",
            "data": data
        }

        resp.text = json.dumps(doc, ensure_ascii=False)

        resp.status = falcon.HTTP_200


class WorkerResource():

    def on_post(self, req, resp):

        raw_json = req.stream.read()
        result = json.loads(raw_json)
        task = fib.delay(int(result['number']))

        result = {
            'status': 'success',
            'data': {
                'task_id': task.id
            }
        }

        resp.text = json.dumps(result)
        resp.status = falcon.HTTP_200


class WorkerStatusResource:

    def on_get(self, req, resp, task_id):
        task_result = AsyncResult(task_id)
        result = {'status': task_result.status, 'result': task_result.result}

        resp.text = json.dumps(result)
        resp.status = falcon.HTTP_200
