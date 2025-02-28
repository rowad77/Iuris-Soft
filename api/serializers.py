from rest_framework import serializers
from cases.models import Case

class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = [
            'id', 'title', 'start_date', 'end_date', 'color', 
            'assigned_lawyer', 'assigned_users', 'description'
        ]