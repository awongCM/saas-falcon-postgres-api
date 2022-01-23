import json

import falcon


class BaseResource:

    def on_get(self, req, resp):

        # TODO: testing the sqlalchemy session middleware integration...
        result = self.session.execute('SELECT * FROM pg_catalog.pg_tables;')
        rows = result.fetchall()
        data = []
        for row in rows:
            data.append(list(row))

        doc = {
            "message": "hello to sass-falcon-postgres-api",
            "data": data
        }

        resp.text = json.dumps(doc, ensure_ascii=False)

        resp.status = falcon.HTTP_200
