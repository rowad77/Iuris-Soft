from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib import messages

from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect

from accounts.models import Client
from cases.forms import CaseForm, DocumentForm
from cases.models.cases import Case, Document


# Client views
class ClientListView(ListView):
    model = Client
    template_name = "cases/client_list.html"
    context_object_name = "clients"


class ClientDetailView(DetailView):
    model = Client
    template_name = "cases/client_detail.html"


class ClientCreateView(CreateView):
    model = Client
    template_name = "cases/client_form.html"
    fields = ["name", "email", "phone"]


class ClientUpdateView(UpdateView):
    model = Client
    template_name = "cases/client_form.html"
    fields = ["name", "email", "phone"]


class ClientDeleteView(DeleteView):
    model = Client
    template_name = "cases/client_confirm_delete.html"
    success_url = reverse_lazy("client-list")


# Case views
class CaseListView(ListView):
    model = Case
    template_name = "cases/case_list.html"
    context_object_name = "cases"


class CaseDetailView(DetailView):
    model = Case
    template_name = "cases/case_detail.html"
    context_object_name = "case"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["activities"] = self.object.caseactivity_set.all().order_by(
            "-timestamp"
        )
        return context

class CaseCreateView(CreateView):
    model = Case
    form_class = CaseForm
    template_name = 'cases/case_form.html'
    success_url = reverse_lazy('case:case-list')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not Client.objects.filter(client_organization=user.organization).exists():
            messages.warning(request, "No clients found in your organization. Please add a client first.")
            return redirect("case:client-create")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        case = form.save()
        messages.success(self.request, f"{case.title.title()} successfully created.")
        return super().form_valid(form)
    
class CaseUpdateView(UpdateView):
    model = Case
    template_name = "cases/case_form.html"
    fields = ["title", "description", "client", "status"]


class CaseDeleteView(DeleteView):
    model = Case
    template_name = "cases/case_confirm_delete.html"
    success_url = reverse_lazy("case-list")


# Document views
class DocumentListView(ListView):
    model = Document
    template_name = "cases/document_list.html"
    context_object_name = "documents"


class DocumentDetailView(DetailView):
    model = Document
    template_name = "cases/document_detail.html"


class DocumentCreateView(CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'cases/document_form.html'

    def form_valid(self, form):
        form.instance.case = get_object_or_404(Case, pk=self.kwargs['case_pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cases:case-detail', kwargs={'pk': self.object.case.pk})
class DocumentUpdateView(UpdateView):
    model = Document
    template_name = "cases/document_form.html"
    fields = ["title", "case", "document_type", "file"]


class DocumentDeleteView(DeleteView):
    model = Document
    template_name = "cases/document_confirm_delete.html"
    success_url = reverse_lazy("document-list")
