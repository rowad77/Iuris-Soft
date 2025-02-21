from django.db import models
from django.utils import timezone
from accounts.models import Client
from cases.models import Case
from django.contrib.auth import get_user_model
from django.db import models, transaction
from decimal import Decimal

from utils.mixins import SlugMixin, TimestampMixin

User = get_user_model()
class Invoice(SlugMixin, TimestampMixin, models.Model):
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    date_issued = models.DateField(default=timezone.now)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"


class ClientRetainer(SlugMixin, TimestampMixin, models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Retainer for {self.client} - ${self.amount}"


class RetainerUsage(SlugMixin, TimestampMixin, models.Model):
    retainer = models.ForeignKey(ClientRetainer, on_delete=models.CASCADE)
    time_entry = models.OneToOneField("TimeEntry", null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Usage of ${self.amount} from {self.retainer}"


class TimeEntry(SlugMixin, TimestampMixin, models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    is_billed = models.BooleanField(default=False)
    retainer_usage = models.OneToOneField("RetainerUsage", null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def hours_worked(self):
        return (self.end_time - self.start_time).total_seconds() / 3600

    @property
    def billable_amount(self):
        """Calculate the billable amount for this time entry (assuming a $100/hour rate)."""
        hourly_rate = Decimal("100.00")  # Replace with actual billing logic
        return round(Decimal(self.hours_worked) * hourly_rate, 2)

    def auto_deduct_or_invoice(self):
        """Deduct from an active retainer or generate an invoice if no retainer is available."""
        if self.is_billed:
            return  # Already billed, do nothing

        with transaction.atomic():
            retainer = ClientRetainer.objects.filter(
                client=self.client,
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date(),
                remaining_balance__gte=self.billable_amount
            ).first()

            if retainer:
                # Deduct from the retainer
                retainer.remaining_balance -= self.billable_amount
                retainer.save()

                # Create RetainerUsage record
                retainer_usage = RetainerUsage.objects.create(
                    retainer=retainer,
                    time_entry=self,
                    amount=self.billable_amount,
                    description=f"Billed {self.hours_worked:.2f} hours from retainer."
                )
                self.retainer_usage = retainer_usage
            else:
                # Generate an invoice if no retainer is available
                invoice = Invoice.objects.create(
                    case=self.case,
                    client=self.client,
                    invoice_number=f"INV-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    date_issued=timezone.now().date(),
                    due_date=timezone.now().date() + timezone.timedelta(days=30),
                    amount=self.billable_amount,
                    is_paid=False
                )

            self.is_billed = True
            self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.auto_deduct_or_invoice()

    def __str__(self):
        return f"{self.case} - {self.client} - {self.user} - {self.start_time.date()}"

