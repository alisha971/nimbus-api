# CELERY

from celery import Celery

# Use Redis as the broker and result backend
BROKER_URL = "redis://localhost:6379/0"
RESULT_BACKEND = "redis://localhost:6379/1"

celery_app = Celery(
    "tasks",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["service.tasks"] # Points to our tasks file
)

celery_app.conf.update(
    task_track_started=True,
)