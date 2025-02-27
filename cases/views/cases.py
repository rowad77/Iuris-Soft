import json
import mimetypes
import fitz  # PyMuPDF
from django.core.files.base import ContentFile

from django.http import JsonResponse
from django.views import View
from django.utils.safestring import mark_safe

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib import messages

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.forms import inlineformset_factory,modelformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML

from accounts.models import Client, Profile
from cases.forms import CaseForm, DocumentForm
from cases.models.cases import Case, Document

User = get_user_model()

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
        if not Client.objects.filter(user=user).exists():
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
            self.object = form.save()
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
        if form.is_valid() and document_formset.is_valid():
            self.object = form.save()
            document_formset.instance = self.object
            document_formset.save()
            messages.success(self.request, f"{self.object.title.title()} successfully updated.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
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
    context_object_name = "documents"
    
    def get_queryset(self):
        return (
            Document.objects.select_related("case")
            .only("id", "title", "case__id", "case__title", "document_type", "file", "description")
            .order_by("-created")
        )


class DocumentDetailView(DetailView):
    model = Document
    template_name = "cases/document_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = self.object
        user = self.request.user

        # File preview logic
        if document.file and document.file.name:
            file_url = document.file.url
            mime_type, _ = mimetypes.guess_type(file_url)

            if mime_type and mime_type.startswith("application/pdf"):
                preview = f'<iframe src="{file_url}" width="100%" height="600px"></iframe>'
            else:
                preview = "<p>Preview not available.</p>"
        else:
            preview = "<p>No file uploaded.</p>"

        context["preview"] = mark_safe(preview)

        # Check if the user has a saved signature
        signature = User.objects.get(id=user.id)
        context["signature"] = signature.signature.url if signature else None

        return context

class DocumentCreateView(CreateView):
    model = Document
    form_class = DocumentForm
    template_name = "cases/document_form.html"

    def form_valid(self, form):
        case = form.cleaned_data.get("case")
        if not case and "case_pk" in self.kwargs:
            try:
                case = Case.objects.get(pk=self.kwargs["case_pk"])
            except Case.DoesNotExist:
                case = None 
        form.instance.case = case
        messages.success(self.request, f"{form.instance.title.title()} successfully created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("case:document-detail", kwargs={"slug": self.object.slug})

class DocumentUpdateView(UpdateView): #LoginRequiredMixin,
    model = Document
    form_class = DocumentForm
    template_name = "cases/document_form.html"

    def get_success_url(self):
        return reverse_lazy("case:document-detail", kwargs={"slug": self.object.slug})
    
class DocumentDeleteView(DeleteView):
    model = Document
    template_name = "cases/document_confirm_delete.html"
    success_url = reverse_lazy("case:document-list")

    def form_valid(self, form):
        messages.success(self.request, f"Successfully deleted.")
        return super().form_valid(form)

class SaveSignaturePositionView(View):
    def post(self, request, pk):
        data = json.loads(request.body)
        left = data.get("left")
        top = data.get("top")

        request.session["signature_position"] = {"left": left, "top": top}
        return JsonResponse({"status": "success"})
    
class ApplySignatureView(View):
    def post(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        signature = get_object_or_404(User, id=request.user.id)

        signature_position = request.session.get("signature_position", {"left": "50px", "top": "50px"})
        left = int(signature_position["left"].replace("px", ""))
        top = int(signature_position["top"].replace("px", ""))

        # Load the PDF
        doc = fitz.open(document.file.path)
        page = doc[0]

        # Insert the signature
        signature_rect = fitz.Rect(left, top, left + 100, top + 50)  # Adjust size as needed
        page.insert_image(signature_rect, filename=signature.signature.path)

        # Save the new PDF
        new_pdf_path = f"case_documents/signed_{document.file.name.split('/')[-1]}"
        doc.save(new_pdf_path)
        doc.close()

        # Update the document file
        with open(new_pdf_path, "rb") as f:
            document.file.save(new_pdf_path, ContentFile(f.read()))

        return JsonResponse({"status": "signed"})