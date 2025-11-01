from celery import Celery
from decouple import config


REDIS_URL = config("REDIS_URL")

celery_app = Celery(
    "celery_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'api.v1.fakestoreapi.services.background_task'
    ]
)