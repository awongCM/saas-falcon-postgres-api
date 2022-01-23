import json

import falcon

from celery.result import AsyncResult


class WorkerStatusResource:

    def on_get(self, req, resp, task_id):
        task_result = AsyncResult(task_id)
        result = {'status': task_result.status, 'result': task_result.result}

        resp.text = json.dumps(result)
        resp.status = falcon.HTTP_200
