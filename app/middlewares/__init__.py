
import falcon

# https://eshlox.net/2017/07/28/integrate-sqlalchemy-with-falcon-framework


class SQLAlchemySessionManager:
    """
    Create a session for every request and close it when the request ends.
    """

    def __init__(self, Session):
        self.Session = Session

    def process_resource(self, req, resp, resource, params):

        resource.session = self.Session()

    def process_response(self, req, resp, resource, req_succeeded):

        try:
            if not req_succeeded:
                resource.session.rollback()

            self.Session.remove()
        except:
            print('A session was not found!')
            raise falcon.HTTPInternalServerError(
                'SQLAlchemySessionManager error encountered', 'Resource session is not valid!')
