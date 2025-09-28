# tasks/celery_init.py
from celery import Celery

# Initialize Celery
# We name it "tasks" and point to the Redis broker.
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    # This tells Celery to automatically find any tasks in files
    # within the 'tasks' module.
    include=['tasks.process_data']
)
