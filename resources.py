import json

import falcon

from tasks import fib


class BaseResource:

    def on_get(self, req, resp):
        doc = {
            "message": "hello to sass-falcon-postgres-api"
        }

        resp.text = json.dumps(doc, ensure_ascii=False)

        resp.status = falcon.HTTP_200


class WorkerResource():

    def on_post(self, req, resp):

        raw_json = req.stream.read()
        result = json.loads(raw_json)
        task = fib.delay(int(result['number']))
        resp.status = falcon.HTTP_200
        result = {
            'status': 'success',
            'data': {
                'task_id': task.id
            }
        }

        resp.text = json.dumps(result)
