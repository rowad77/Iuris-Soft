from django.db import models
from django.urls import reverse
from django.utils import timezone
from accounts.models import Client
from cases.models import Case
from django.contrib.auth import get_user_model
from django.db import models, transaction
from decimal import Decimal
from django.core.exceptions import ValidationError

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

class InvoiceApproval(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="approvals")
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    def approve(self):
        """Mark as approved and trigger invoice sending."""
        from cases.tasks import send_invoice_email
        self.is_approved = True
        self.approved_at = timezone.now()
        self.save()
        
        send_invoice_email.delay(self.invoice.id)


class ClientRetainer(SlugMixin, TimestampMixin, models.Model):
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)
    low_balance_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    low_balance_notified = models.BooleanField(default=False)

    def check_low_balance(self):
        """Check if retainer is low and trigger a Celery task for notification."""
        from cases.tasks import notify_low_retainer_balance
        if self.remaining_balance <= self.low_balance_threshold and not self.low_balance_notified:
            notify_low_retainer_balance.delay(self.client.id, self.remaining_balance)
            self.low_balance_notified = True  # Prevent multiple notifications
            self.save()

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
    end_time = models.DateTimeField(blank=True,null=True)
    description = models.TextField(blank=True, null=True)
    is_billed = models.BooleanField(default=False)
    retainer_usage = models.OneToOneField("RetainerUsage", null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def is_active(self):
        return self.end_time is None  # Check if the entry is still running

    @staticmethod
    def user_has_active_entry(user):
        return TimeEntry.objects.filter(user=user, end_time__isnull=True).exists()

    @property
    def hours_worked(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600
        return Decimal(0)

    @property
    def billable_amount(self):
        hourly_rate = getattr(self.user, "hourly_rate", None)
        if hourly_rate is None:
            return Decimal(0)
        return round(Decimal(self.hours_worked) * Decimal(hourly_rate), 2)
  
  

    def auto_deduct_or_invoice(self):
        """Deduct from retainer, log transactions, and request invoice approval if needed."""
        if self.is_billed or not self.end_time:
            print(f"Skipping billing for TimeEntry ID: {self.id} (Already billed: {self.is_billed}, End Time: {self.end_time})")
            return  

        print(f"Processing billing for TimeEntry ID: {self.id}")

        with transaction.atomic():
            from cases.tasks import notify_supervisor_for_approval
            billable_amount = self.billable_amount
            print(f"Billable amount for TimeEntry ID {self.id}: {billable_amount}")

            retainer = ClientRetainer.objects.filter(
                client=self.client,
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date(),
            ).order_by('-end_date').first()

            if retainer:
                print(f"Found retainer for Client {self.client.id}, Remaining Balance: {retainer.remaining_balance}")

                if retainer.remaining_balance >= billable_amount:
                    retainer.remaining_balance -= billable_amount
                    retainer.save()
                    usage = RetainerUsage.objects.create(
                        retainer=retainer,
                        time_entry=self,
                        amount=billable_amount,
                        description=f"Billed {self.hours_worked:.2f} hours from retainer."
                    )
                    print(f"Created RetainerUsage ID: {usage.id} for TimeEntry ID: {self.id}")

                else:
                    used_amount = retainer.remaining_balance
                    remaining_due = billable_amount - used_amount
                    retainer.remaining_balance = Decimal(0)
                    retainer.save()
                    usage = RetainerUsage.objects.create(
                        retainer=retainer,
                        time_entry=self,
                        amount=used_amount,
                        description=f"Partially covered {used_amount:.2f}. Remaining {remaining_due:.2f} needs invoicing."
                    )
                    print(f"Created RetainerUsage ID: {usage.id} for TimeEntry ID: {self.id}")

                    if remaining_due > 0:
                        invoice = Invoice.objects.create(
                            case=self.case,
                            client=self.client,
                            invoice_number=f"INV-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                            date_issued=timezone.now().date(),
                            due_date=timezone.now().date() + timezone.timedelta(days=30),
                            amount=remaining_due,
                            is_paid=False
                        )
                        print(f"Invoice created for {remaining_due}")

                        supervisor = User.objects.filter(is_supervisor=True).first()
                        if supervisor:
                            InvoiceApproval.objects.create(invoice=invoice, supervisor=supervisor)
                            notify_supervisor_for_approval.delay(supervisor.id, invoice.id)

            else:
                invoice = Invoice.objects.create(
                    case=self.case,
                    client=self.client,
                    invoice_number=f"INV-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    date_issued=timezone.now().date(),
                    due_date=timezone.now().date() + timezone.timedelta(days=30),
                    amount=billable_amount,
                    is_paid=False
                )
                print(f"Invoice created for {billable_amount}")

                supervisor = User.objects.filter(is_supervisor=True).first()
                if supervisor:
                    InvoiceApproval.objects.create(invoice=invoice, supervisor=supervisor)
                    notify_supervisor_for_approval.delay(supervisor.id, invoice.id)

            self.is_billed = True
            self.save()
            print(f"Marked TimeEntry {self.id} as billed.")

    def save(self, *args, **kwargs):
        is_stopping = self.end_time is not None and not TimeEntry.objects.filter(id=self.id, end_time__isnull=False).exists()
        super().save(*args, **kwargs)
        if is_stopping:  # Only run billing when end_time is set
            self.auto_deduct_or_invoice()

    def get_absolute_url(self):
        return reverse("case:time-entry-detail", kwargs={"slug": self.slug})    

    def __str__(self):
        return f"{self.case} - {self.client} - {self.user} - {self.start_time.date()}"

