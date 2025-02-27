from accounts.models import Client
from cases.models.cases import Case
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date,timedelta
from django.conf import settings
from django.template.loader import render_to_string

from cases.models.billing import Invoice, InvoiceApproval, TimeEntry
from utils.enum import CaseStatus


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

@shared_task
def notify_upcoming_due_cases():
    threshold_date = date.today() + timedelta(days=settings.CASE_DUE_NOTIFICATION_DAYS)

    due_cases = Case.objects.filter(due_date__lte=threshold_date, status=CaseStatus.OPEN)

    if not due_cases.exists():
        return

    lawyers = set(due_cases.values_list("assigned_lawyer", flat=True))
    for lawyer_id in lawyers:
        if not lawyer_id:
            continue
        lawyer_cases = due_cases.filter(assigned_lawyer_id=lawyer_id)
        lawyer = lawyer_cases.first().assigned_lawyer

        context = {
            "cases": lawyer_cases,
            "threshold_date": threshold_date,
            "recipient_name": lawyer.get_full_name(),
        }

        email_content = render_to_string("emails/lawyer_due_cases_notification.html", context)

        send_mail(
            subject=f"Upcoming Due Cases - Assigned to You (Next {settings.CASE_DUE_NOTIFICATION_DAYS} days)",
            message="",
            html_message=email_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[lawyer.email],
            fail_silently=False,
        )

    context = {
        "cases": due_cases,
        "threshold_date": threshold_date,
    }
    admin_email_content = render_to_string("emails/admin_due_cases_notification.html", context)

    send_mail(
        subject=f"Upcoming Due Cases - System Wide (Next {settings.CASE_DUE_NOTIFICATION_DAYS} days)",
        message="",
        html_message=admin_email_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email for _, email in settings.ADMINS],
        fail_silently=False,
    )