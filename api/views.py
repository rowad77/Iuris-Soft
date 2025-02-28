from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from api.serializers import CaseSerializer
from cases.models.cases import Case

User = get_user_model()

class CaseCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_superuser:
            cases = Case.objects.all()
        else:
            cases = Case.objects.filter(assigned_users=user)
        serializer = CaseSerializer(cases, many=True)
        return Response(serializer.data)
    
class UpdateCaseView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            case = Case.objects.get(pk=pk)
            case.start_date = request.data.get('start_date', case.start_date)
            case.end_date = request.data.get('end_date', case.end_date)
            case.save()
            return Response(status=status.HTTP_200_OK)
        except Case.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)