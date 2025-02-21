from celery.schedules import crontab
from celery import Celery

app = Celery("billing")

app.conf.beat_schedule = {
    "process-unbilled-time-entries-daily": {
        "task": "billing.tasks.process_unbilled_time_entries",
        "schedule": crontab(hour=0, minute=0),  # Runs daily at midnight
    },
}
