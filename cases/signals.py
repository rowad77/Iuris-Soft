from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from cases.models.billing import ClientRetainer, RetainerUsage, TimeEntry
from cases.models.cases import Case, CaseActivity, Document


@receiver(post_save, sender=TimeEntry)
def track_retainer_usage(sender, instance, created, **kwargs):
    if created:
        try:
            retainer = ClientRetainer.objects.get(
                client=instance.case.client,
                start_date__lte=instance.start_time.date(),
                end_date__gte=instance.end_time.date(),
            )
            amount_to_use = instance.hours_worked * instance.user.hourly_rate
            if retainer.remaining_balance >= amount_to_use:
                RetainerUsage.objects.create(
                    retainer=retainer,
                    amount=amount_to_use,
                    description=f"Time Entry for {instance.case}",
                )
                retainer.remaining_balance -= amount_to_use
                retainer.save()
        except ClientRetainer.DoesNotExist:
            pass


@receiver(post_save, sender=ClientRetainer)
def update_remaining_balance(sender, instance, created, **kwargs):
    if created:
        instance.remaining_balance = instance.amount
        instance.save()

@receiver(post_save, sender=Case)
def log_case_activity(sender, instance, created, **kwargs):
    if created:
        CaseActivity.objects.create(case=instance, activity=f"Case {instance.case_number} created.")
    else:
        CaseActivity.objects.create(case=instance, activity=f"Case {instance.case_number} updated.")

@receiver(post_save, sender=Document)
def log_document_activity(sender, instance, created, **kwargs):
    if instance.case:
        if created:
            activity_msg = f"Document {instance.title} added to case {instance.case.case_number}."
        else:
            activity_msg = f"Document {instance.title} updated in case {instance.case.case_number}."        
        CaseActivity.objects.create(case=instance.case, activity=activity_msg)
    else:
        print(f"Document {instance.title} was created/updated without a case.")  # Debugging message

@receiver(post_delete, sender=Document)
def log_document_deletion(sender, instance, **kwargs):
    if instance.case:
        CaseActivity.objects.create(case=instance.case, activity=f"Document {instance.title} deleted from case {instance.case.case_number}.")