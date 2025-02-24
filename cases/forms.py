from django import forms

from accounts.models import Client
from cases.models.billing import TimeEntry
from utils.enum import DocumentType
from .models import Case, Document

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field,HTML
from .models import Case, Document


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = [
            "title",
            "client",
            "case_type",
            "status",
            "description",
            "assigned_lawyer",
            "assigned_users",
        ]

        widgets = {
            "case_type": forms.CheckboxSelectMultiple(),
            "assigned_users": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_users"].label = "Support Users"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("title", css_class="col-md-6"),
                Column("client", css_class="col-md-6"),
            ),
            Row(
                Column("case_type", css_class="col-md-6"),
                Column("status", css_class="col-md-6"),
            ),
            Row(
                Column("assigned_lawyer", css_class="col-md-6"),
                Column("assigned_users", css_class="col-md-6"),
            ),
            "description",
            Submit("submit", "Save Case", css_class="btn btn-primary"),
        )

class DocumentForm(forms.ModelForm):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    case = forms.ModelChoiceField(
        queryset=Case.objects.all(), required=False, widget=forms.Select,empty_label="(No Case Selected)"
    )
    title = forms.CharField(required=False)
    document_type = forms.ChoiceField(
        choices=DocumentType.choices, required=False, widget=forms.Select
    )
    file = forms.FileField(required=False, widget=forms.FileInput)
    description = forms.CharField(
        widget=forms.Textarea(attrs={"cols": 3, "rows": 3}), required=False
    )

    class Meta:
        model = Document
        fields = ['id',"case", "title", "document_type", "file", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['id'].initial = self.instance.pk
            
        if self.instance and self.instance.pk and self.instance.file:
            self.fields["file"].help_text = (
                f'<small><a href="{self.instance.file.url}" target="_blank">{self.instance.file.name}</a></small>'
            )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML("{{ document_formset.management_form }}"),
            Field('id'),
            Row(
                Column("title", css_class="col-md-3"),
                Column("document_type", css_class="col-md-3"),
                Column("file", css_class="col-md-6"),
                Column("description", css_class="col-md-12"),
            ),
            HTML("{% if form.instance.pk %}{{ form.DELETE }}{% endif %}")
        )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('id') and not cleaned_data.get('DELETE', False):
            if not any(cleaned_data.get(field) for field in ['title', 'document_type', 'file', 'description']):
                raise forms.ValidationError("At least one field must be filled for new documents.")
        return cleaned_data
    
class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ["client", "case", "description"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["client"].queryset = Client.objects.filter(user=user)

        self.fields["case"].queryset = Case.objects.none()
        self.fields["case"].widget.attrs["disabled"] = True
        if "client" in self.data:
            try:
                client_id = int(self.data.get("client"))
                self.fields["case"].queryset = Case.objects.filter(client_id=client_id)
            except (ValueError, TypeError):
                pass  # Invalid input; keep case queryset empty

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("client", css_class="form-group col-md-6"),
                Column("case", css_class="form-group col-md-6"),
                css_class="form-row"
            ),
            "description",
            Submit("submit", "Start Time Entry", css_class="btn btn-primary"),
        )

