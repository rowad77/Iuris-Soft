from django.urls import path

from accounts.views import ClientCreateView, ClientListView

from cases.views.billing import (
    CaseByClientView,
    ClientRetainerCreateView,
    ClientRetainerListView,
    InvoiceCreateView,
    InvoiceDetailView,
    InvoiceListView,
    StartTimeEntryView,
    StopTimeEntryView,
    TimeEntryCreateView,
    TimeEntryListView,
)
from cases.views.cases import (
    CaseCreateView,
    CaseDeleteView,
    CaseDetailView,
    CaseListView,
    CaseUpdateView,
    ClientDeleteView,
    ClientDetailView,
    ClientUpdateView,
    DocumentCreateView,
    DocumentDeleteView,
    DocumentDetailView,
    DocumentListView,
    DocumentUpdateView,
)

app_name = "case"
urlpatterns = [
    # Client URLs
    path("clients/", ClientListView.as_view(), name="client-list"),
    path("clients/<int:pk>/", ClientDetailView.as_view(), name="client-detail"),
    path("clients/create/", ClientCreateView.as_view(), name="client-create"),
    path(
        "clients/<int:pk>/update/",
        ClientUpdateView.as_view(),
        name="client-update",
    ),
    path(
        "clients/<int:pk>/delete/",
        ClientDeleteView.as_view(),
        name="client-delete",
    ),
    # Case URLs
    path('', CaseListView.as_view(), name='case-list'),
    path("case/<str:slug>/", CaseDetailView.as_view(), name="case-detail"),
    path("case-create/", CaseCreateView.as_view(), name="case-create"),
    path("<str:slug>/update/", CaseUpdateView.as_view(), name="case-update"),
    path("<str:slug>/delete/", CaseDeleteView.as_view(), name="case-delete"),
    # Billing
    path("start-time/", StartTimeEntryView.as_view(), name="start-time-entry"),
    path("stop/", StopTimeEntryView.as_view(), name="stop-time-entry"),
    path("load-cases/", CaseByClientView.as_view(), name="load-cases"),
    # Document URLs
    path("documents/", DocumentListView.as_view(), name="document-list"),
    path("documents/create/", DocumentCreateView.as_view(), name="document-create"),
    path(
        "documents/<str:slug>/",
        DocumentDetailView.as_view(),
        name="document-detail",
    ),
   
    path(
        "documents/<str:slug>/update/",
        DocumentUpdateView.as_view(),
        name="document-update",
    ),
    path(
        "documents/<str:slug>/delete/",
        DocumentDeleteView.as_view(),
        name="document-delete",
    ),
    path("time-entries/", TimeEntryListView.as_view(), name="time-entry-list"),
    path(
        "time-entries/create/", TimeEntryCreateView.as_view(), name="time_entry_create"
    ),
    path("invoices/", InvoiceListView.as_view(), name="invoice_list"),
    path("invoices/create/", InvoiceCreateView.as_view(), name="invoice_create"),
    path("invoices/<int:pk>/", InvoiceDetailView.as_view(), name="invoice_detail"),
    path("retainers/", ClientRetainerListView.as_view(), name="client_retainer_list"),
    path(
        "retainers/create/",
        ClientRetainerCreateView.as_view(),
        name="client_retainer_create",
    ),
]
