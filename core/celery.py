import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "process-unbilled-time-entries-daily": {
        "task": "billing.tasks.process_unbilled_time_entries",
        "schedule": crontab(hour=0, minute=0),  # Runs daily at midnight
    },
}

CELERY_BEAT_SCHEDULE = {
    "send_due_cases_notification": {
        "task": "cases.tasks.notify_upcoming_due_cases",
        "schedule": crontab(hour=8, minute=0),  # Every day at 8 AM
    },
}