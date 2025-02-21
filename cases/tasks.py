from cases.models.billing import TimeEntry
from celery import shared_task

@shared_task
def process_unbilled_time_entries():
    """Automates billing for all unbilled time entries."""
    unbilled_entries = TimeEntry.objects.filter(is_billed=False)
    for entry in unbilled_entries:
        entry.auto_deduct_or_invoice()
    return f"Processed {unbilled_entries.count()} unbilled time entries."
