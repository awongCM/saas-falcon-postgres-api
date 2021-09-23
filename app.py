import falcon

from base import BaseResource

api = falcon.App()

base = BaseResource()

api.add_route('/', base)
