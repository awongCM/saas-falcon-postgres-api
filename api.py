import falcon

from resources import BaseResource

api = falcon.App()

base = BaseResource()

api.add_route('/', base)
