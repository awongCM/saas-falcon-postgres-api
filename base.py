import json

import falcon


class BaseResource:

    def on_get(self, req, resp):
        doc = {
            "message": "hello to sass-falcon-postgres-api"
        }

        resp.text = json.dumps(doc, ensure_ascii=False)

        resp.status = falcon.HTTP_200
