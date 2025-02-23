from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from cases.models.cases import Case, CaseActivity, Document



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