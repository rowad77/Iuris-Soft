from django.core.management.base import BaseCommand
from cases.tasks import notify_upcoming_due_cases

class Command(BaseCommand):
    help = "Send notifications for upcoming due cases"

    def handle(self, *args, **kwargs):
        self.stdout.write("Running due cases notification task...")
        notify_upcoming_due_cases.delay()
        self.stdout.write(self.style.SUCCESS("Due cases notification task triggered successfully!"))
