from django.views.generic import CreateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages

from accounts.models import Client
from cases.forms import TimeEntryForm
from cases.models import CaseActivity
from cases.models.billing import ClientRetainer, Invoice, TimeEntry
from cases.models.cases import Case


class TimeEntryCreateView(LoginRequiredMixin, CreateView):
    model = TimeEntry
    fields = ["case", "start_time", "end_time", "description"]
    template_name = "billing/time_entry_form.html"
    success_url = "/billing/time-entries/"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TimeEntryListView(LoginRequiredMixin, ListView):
    model = TimeEntry
    template_name = "billing/time_entry_list.html"
    context_object_name = "time_entries"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_entry = TimeEntry.objects.filter(user=self.request.user, end_time__isnull=True).first()
        context['user_has_active_entry'] = active_entry is not None
        context['active_entry'] = active_entry 
        return context
    

class StartTimeEntryView(CreateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = "billing/time_entry_form.html"
    success_url = reverse_lazy("case:time-entry-list")

    def dispatch(self, request, *args, **kwargs):
        active_entry = TimeEntry.objects.filter(user=request.user, end_time__isnull=True).first()
        if active_entry:
            messages.warning(request, "You already have an active time entry. Please stop it before starting a new one.")
            return redirect("case:time-entry-list")        
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.start_time = timezone.now()
        return super().form_valid(form)
class StopTimeEntryView(View):
    def post(self, request, *args, **kwargs):
        time_entry = TimeEntry.objects.filter(user=request.user, end_time__isnull=True).first()
        if time_entry:
            time_entry.end_time = timezone.now()
            time_entry.save()
            time_entry.auto_deduct_or_invoice()
            messages.success(request, "Time entry stopped successfully!")
            return JsonResponse({"message": "Time entry stopped successfully!"})
        return JsonResponse({"error": "No active time entry found."}, status=400)
class CaseByClientView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        client_id = request.GET.get("client_id")
        if not client_id:
            return JsonResponse({"error": "No client selected"}, status=400)

        client = get_object_or_404(Client, id=client_id)
        cases = Case.objects.filter(client=client).values("id", "title")

        return JsonResponse({"cases": list(cases)})
    
class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    fields = ["case", "client", "date_issued", "due_date", "amount"]
    template_name = "billing/invoice_form.html"
    success_url = "/billing/invoices/"

    def form_valid(self, form):
        response = super().form_valid(form)
        CaseActivity.objects.create(
            case=form.instance.case,
            user=self.request.user,
            activity=f"Invoice #{form.instance.invoice_number} created",
        )
        return response


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "billing/invoice_list.html"
    context_object_name = "invoices"


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = "billing/invoice_detail.html"
    context_object_name = "invoice"


class ClientRetainerCreateView(LoginRequiredMixin, CreateView):
    model = ClientRetainer
    fields = ["client", "amount", "start_date", "end_date"]
    template_name = "billing/client_retainer_form.html"
    success_url = "/billing/retainers/"


class ClientRetainerListView(LoginRequiredMixin, ListView):
    model = ClientRetainer
    template_name = "billing/client_retainer_list.html"
    context_object_name = "retainers"
