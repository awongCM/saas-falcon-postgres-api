import falcon

from resources import BaseResource, WorkerResource, WorkerStatusResource


api = falcon.App()

base = BaseResource()
worker = WorkerResource()
workerStatus = WorkerStatusResource()

api.add_route('/', base)
api.add_route('/start_worker', worker)
api.add_route('/status/{task_id}', workerStatus)
