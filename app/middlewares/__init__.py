import logging

import falcon

logger = logging.getLogger(__name__)


class SQLAlchemySessionManager:
    """
    Create a session for every request and close it when the request ends.
    """

    def __init__(self, Session):
        self.Session = Session

    def process_resource(self, req, resp, resource, params):
        resource.session = self.Session()

    def process_response(self, req, resp, resource, req_succeeded):
        session = getattr(resource, 'session', None)
        if session is None:
            logger.error('SQLAlchemy session missing on resource %s', resource)
            raise falcon.HTTPInternalServerError(
                title='SQLAlchemySessionManager error encountered',
                description='Resource session is not valid!',
            )

        try:
            if not req_succeeded:
                session.rollback()
        finally:
            self.Session.remove()
