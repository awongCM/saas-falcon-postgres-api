import os

import falcon


def require_api_key(req):
    expected = os.getenv('API_KEY')
    if not expected:
        raise falcon.HTTPInternalServerError(
            title='API key not configured',
            description='Set API_KEY in the environment before using /validate.',
        )

    provided = req.get_header('X-API-Key')
    if provided != expected:
        raise falcon.HTTPUnauthorized(
            title='Unauthorized',
            description='A valid X-API-Key header is required.',
        )
