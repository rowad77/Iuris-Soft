from django.urls import path

from api.views import CaseCalendarView, UpdateCaseView

app_name = "api"
urlpatterns = [
    path('cases/', CaseCalendarView.as_view(), name='case-calendar'),
    path('cases/<str:slug>/', UpdateCaseView.as_view(), name='update-case'),
]
