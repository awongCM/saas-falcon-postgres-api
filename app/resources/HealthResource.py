import falcon

from models import ValidationJob


class HealthResource:

    def on_get(self, req, resp):
        job_count = self.session.query(ValidationJob).count()

        resp.status = falcon.HTTP_200
        resp.media = {
            'service': 'email-domain-validator',
            'status': 'ok',
            'description': (
                'Async email and domain validator for checking recruiter '
                'and cold-email senders via DNS signals.'
            ),
            'endpoints': {
                'health': 'GET /',
                'queue_validation': 'POST /validate',
                'validation_status': 'GET /validate/{job_id}',
                'list_validations': 'GET /validate?limit=20',
            },
            'stats': {
                'validation_jobs_total': job_count,
            },
        }
