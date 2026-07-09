import os

import falcon
import redis


def _redis_client():
    broker = os.getenv('CELERY_BROKER')
    if not broker:
        return None
    return redis.from_url(broker)


def enforce_rate_limit(req):
    limit = int(os.getenv('RATE_LIMIT_PER_MINUTE', '30'))
    if limit <= 0:
        return

    client = _redis_client()
    if client is None:
        return

    client_ip = req.access_route[0] if req.access_route else 'unknown'
    key = f'validation-rate:{client_ip}'

    try:
        count = client.incr(key)
        if count == 1:
            client.expire(key, 60)
        if count > limit:
            raise falcon.HTTPTooManyRequests(
                title='Rate limit exceeded',
                description=f'Maximum {limit} validation requests per minute.',
            )
    except falcon.HTTPTooManyRequests:
        raise
    except redis.RedisError:
        # Do not block validation if Redis is temporarily unavailable.
        return
