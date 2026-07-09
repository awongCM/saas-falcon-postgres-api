import falcon

from resources import (
    HealthResource,
    ValidationResource,
    ValidationStatusResource,
)
from middlewares import (SQLAlchemySessionManager)
from database import Session


api = falcon.App(middleware=[
    SQLAlchemySessionManager(Session)
])

health = HealthResource
validation = ValidationResource
validationStatus = ValidationStatusResource

api.add_route('/', health)
api.add_route('/validate', validation)
api.add_route('/validate/{job_id}', validationStatus)
