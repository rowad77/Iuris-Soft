from django import forms
from django.forms import inlineformset_factory
from .models import Case, Document

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Case, Document

# DocumentFormSet = inlineformset_factory(
#     Case,
#     Document,
#     fields=('title', 'document_type', 'file', 'description'),
#     extra=1,
#     can_delete=True,
# )


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'document_type', 'file', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='col-md-12'),
                Column('document_type', css_class='col-md-12'),
                Column('file', css_class='col-md-12'),
                Column('description', css_class='col-md-12'),
            ),
        )
DocumentFormSet = inlineformset_factory(
    Case, Document, form=DocumentForm, extra=3, can_delete=True
)

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
        self.fields['assigned_users'].label = "Support Users"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='col-md-6'),
                Column('client', css_class='col-md-6'),
            ),
            Row(
                Column('case_type', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            Row(
                Column('assigned_lawyer', css_class='col-md-6'),
                Column('assigned_users', css_class='col-md-6'),
            ),
            'description',
            Submit('submit', 'Save Case', css_class='btn btn-primary')
        )



# class CaseDocumentForm(forms.ModelForm):
#     class Meta:
#         model = CaseDocument
#         fields = ["document"]