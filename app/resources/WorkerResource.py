import json

import falcon

from tasks import fib


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
