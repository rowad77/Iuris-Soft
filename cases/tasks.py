from accounts.models import Client
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone

from cases.models.billing import Invoice, InvoiceApproval, TimeEntry


User = get_user_model()

@shared_task
def process_unbilled_time_entries():
    """Automates billing for all unbilled time entries."""
    unbilled_entries = TimeEntry.objects.filter(is_billed=False)
    for entry in unbilled_entries:
        entry.auto_deduct_or_invoice()
    return f"Processed {unbilled_entries.count()} unbilled time entries."


@shared_task
def notify_low_retainer_balance(client_id, remaining_balance):
    """Send an email alert when retainer balance is low."""
    client = Client.objects.get(id=client_id)
    send_mail(
        subject="Low Retainer Balance Alert",
        message=f"Dear {client.name},\n\nYour retainer balance is low: ${remaining_balance}. Please replenish it soon.",
        from_email="billing@example.com",
        recipient_list=[client.email],
    )

@shared_task
def notify_supervisor_for_approval(supervisor_id, invoice_id):
    """Notify supervisor for invoice approval."""
    supervisor = User.objects.get(id=supervisor_id)
    invoice = Invoice.objects.get(id=invoice_id)

    send_mail(
        subject="Invoice Approval Needed",
        message=f"Dear {supervisor.get_full_name()},\n\nAn invoice (#{invoice.invoice_number}) requires your approval before it can be sent to the client.",
        from_email="billing@example.com",
        recipient_list=[supervisor.email],
    )

@shared_task
def send_invoice_email(invoice_id):
    """Send an approved invoice to the client."""
    invoice = Invoice.objects.get(id=invoice_id)
    
    if not InvoiceApproval.objects.filter(invoice=invoice, is_approved=True).exists():
        return  # Ensure invoice is approved before sending

    send_mail(
        subject=f"Invoice #{invoice.invoice_number}",
        message=f"Dear {invoice.client.name},\n\nAttached is your invoice for ${invoice.amount}. Please make payment before {invoice.due_date}.",
        from_email="billing@example.com",
        recipient_list=[invoice.client.email],
    )