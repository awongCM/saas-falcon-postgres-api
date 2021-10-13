import falcon

from resources import BaseResource, WorkerResource, WorkerStatusResource
from middlewares import SQLAlchemySessionManager
from database import Session


api = falcon.App(middleware=[
    SQLAlchemySessionManager(Session)
])

base = BaseResource()
worker = WorkerResource()
workerStatus = WorkerStatusResource()

api.add_route('/', base)
api.add_route('/start_worker', worker)
api.add_route('/status/{task_id}', workerStatus)
