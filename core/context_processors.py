from django.contrib.auth import get_user_model
from cases.models.cases import Case
User = get_user_model()

def global_counts(request):   
    return {
        'global_user_count': User.objects.count(),
        'global_case_count': Case.objects.count(),
    }