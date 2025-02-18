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
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML

from accounts.models import Client
from cases.forms import CaseForm, DocumentForm
from cases.models.cases import Case, Document


DocumentFormSet = inlineformset_factory(
    Case, Document, form=DocumentForm, extra=3, can_delete=True
)
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['document_formset'] = DocumentFormSet(self.request.POST, self.request.FILES)
        else:
            context['document_formset'] = DocumentFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        document_formset = context['document_formset']

        if form.is_valid() and document_formset.is_valid():
            # Save the main case form
            self.object = form.save()
            
            # Attach the formset to the instance and save it
            document_formset.instance = self.object
            document_formset.save()

            messages.success(self.request, f"{self.object.title.title()} successfully created.")
            return super().form_valid(form)
        else:
            if not form.is_valid():
                print("Form Errors: ", form.errors)
            if not document_formset.is_valid():
                print("Formset Errors: ", document_formset.errors)

            return self.render_to_response(self.get_context_data(form=form, document_formset=document_formset))


class CaseUpdateView(UpdateView):
    model = Case
    form_class = CaseForm
    template_name = "cases/case_form.html"
    success_url = reverse_lazy('case:case-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        DocumentFormSet = inlineformset_factory(
            Case, Document, form=DocumentForm, 
            extra=1, can_delete=True
        )
        
        if self.request.method == 'POST':
            context['document_formset'] = DocumentFormSet(
                self.request.POST, 
                self.request.FILES,
                instance=self.object
            )
        else:
            context['document_formset'] = DocumentFormSet(instance=self.object)
            
        helper = FormHelper()
        helper.form_tag = False
        helper.layout = Layout(
            HTML("{{ document_formset.management_form }}")
        )
        context['document_formset_helper'] = helper
        return context
    

    def form_valid(self, form):
        context = self.get_context_data()
        document_formset = context['document_formset']
        
        # Debug: Check formset data and errors
        print("Form data: ", self.request.POST)
        print("File data: ", self.request.FILES)
        print("Formset errors: ", document_formset.errors)

        # Validate the form and formset
        if form.is_valid() and document_formset.is_valid():
            # Save the main Case form
            self.object = form.save()

            # Make sure formset is linked to the updated Case object
            document_formset.instance = self.object

            # Save new and updated documents
            document_formset.save()

            # Success message
            messages.success(self.request, f"{self.object.title.title()} successfully updated.")
            return super().form_valid(form)
        else:
            # Debug: Log formset errors
            print("Formset validation failed")
            print("Form Errors: ", form.errors)
            print("Document Formset Errors: ", document_formset.errors)

            return self.form_invalid(form)

    def form_invalid(self, form):
        # Debug: Print formset and form errors to help with debugging
        context = self.get_context_data()
        document_formset = context['document_formset']
        return self.render_to_response(self.get_context_data(form=form))
class CaseDeleteView(DeleteView):
    model = Case
    template_name = "cases/case_confirm_delete.html"
    success_url = reverse_lazy("case:case-list")

    def form_valid(self, form):
        messages.success(self.request, f"Successfully deleted.")
        return super().form_valid(form)


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
