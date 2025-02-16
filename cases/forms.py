from django import forms
from .models import Case, Document

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Case, Document

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['title', 'client', 'case_type', 'status', 'description', 'assigned_lawyer', 'assigned_users']

        widgets = {
            'case_type': forms.CheckboxSelectMultiple(),
            'assigned_users': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='col-md-12'),
                Column('client', css_class='col-md-12'),
                Column('case_type', css_class='col-md-12'),
            ),
            Row(
                Column('status', css_class='col-md-12'),
                Column('assigned_lawyer', css_class='col-md-12'),
            ),
            'description',
            'assigned_users',
            Submit('submit', 'Save Case', css_class='btn btn-primary')
        )

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'document_type', 'file', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'document_type',
            'file',
            'description',
            Submit('submit', 'Upload Document', css_class='btn btn-primary')
        )