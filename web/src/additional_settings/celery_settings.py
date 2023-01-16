import os
from os import environ

from kombu import Exchange, Queue

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BACKEND", "redis://127.0.0.1:6379/0")

CELERY_TIMEZONE = environ.get('TZ', 'UTC')

CELERY_RESULT_PERSISTENT = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_BROKER_HEARTBEAT_CHECKRATE = 10
CELERY_EVENT_QUEUE_EXPIRES = 10
CELERY_EVENT_QUEUE_TTL = 10
CELERY_TASK_SOFT_TIME_LIMIT = 60

CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries': 4,
    'interval_start': 0,
    'interval_step': 0.5,
    'interval_max': 3,
}

celery_exchange = Exchange('celery', type='direct')  # topic, fanout

CELERY_TASK_ROUTES = {
    '*': {'queue': 'celery'},
}

CELERY_TASK_QUEUES = (
    Queue(
        name='celery',
        exchange=celery_exchange,
        queue_arguments={'x-queue-mode': 'lazy'},
    ),
)


CELERY_BEAT_SCHEDULE = {
    'add_fresh_price': {
        'task': 'add_fresh_price',
        "schedule": 10.0,  # one second
    },
    'add_reward': {
        'task': 'add_reward',
        "schedule": 36000.0,  # one second
    },
}
