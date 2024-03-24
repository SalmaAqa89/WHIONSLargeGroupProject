import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')

app = Celery('task_manager')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.update(
    task_acks_late=True,  # Delay acknowledging tasks until they are fully processed
    worker_prefetch_multiplier=1,  # Limit each worker to prefetch one task at a time
    worker_concurrency=3,  # Limit the total number of worker processes to 3
)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')