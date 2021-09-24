import falcon

from resources import BaseResource, WorkerResource

api = falcon.App()

base = BaseResource()
worker = WorkerResource()

api.add_route('/', base)
api.add_route('/start_worker', worker)
