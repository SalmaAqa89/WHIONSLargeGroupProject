web: gunicorn task_manager.wsgi --log-file -
worker: celery -A task_manager worker -l info
beat: celery -A task_manager beat -l info
