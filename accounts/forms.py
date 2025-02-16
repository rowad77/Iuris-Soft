from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import  Profile, Organization

from django.contrib.auth.forms import ReadOnlyPasswordHashField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Submit, Button
from django.urls import reverse_lazy
from django import forms

from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

User = get_user_model()
class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includea all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email",)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password = ReadOnlyPasswordHashField(
        label=("Password"),
        help_text=(
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            'using <a href="../password/">this form</a>.'
        ),
    )

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "active",
            "staff",
            "admin",
        )

    def clean_password(self):
        return self.initial["password"]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email",)
        # exclude = ('email','password')

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ("first_name", "last_name","admin","active","password")

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "user_type",
            "country",
            "hourly_rate",
            "phone_number",
            "address",
            "password1",  # Add password1 field
            "password2",  # Add password2 field
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-horizontal"
        self.helper.field_class = "col-md-8"
        self.helper.field_class = "form-control"

        self.helper.layout = Layout(
            Row(
                Column("first_name", css_class="col-md-6"),
                Column("last_name", css_class="col-md-6"),
            ),
            Row(
                Column("email", css_class="col-md-6"),
                Column("username", css_class="col-md-6"),
            ),
            Row(
                Column("user_type", css_class="col-md-6"),
                Column("country", css_class="col-md-6"),
            ),
            Row(
                Column("hourly_rate", css_class="col-md-4"),
                Column("phone_number", css_class="col-md-4"),
                Column("address", css_class="col-md-4"),
            ),
            Row(
                Column("password1", css_class="col-md-6"),
                Column("password2", css_class="col-md-6"),
            ),
            Row(
                Column(
                    Submit("submit", "Save", css_class="btn btn-success mx-2"),
                    Button(
                        "cancel",
                        "Cancel",
                        css_class="btn btn-secondary mx-2",
                        onclick="window.location.href='{}'".format(
                            reverse_lazy("accounts:users")
                        ),
                    ),
                    css_class="d-flex justify-content-center mt-3",
                ),
            ),
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "user_type",
            "country",
            "hourly_rate",
            "phone_number",
            "address",
            "password",  # Add password field
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("first_name", css_class="col-md-6"),
                Column("last_name", css_class="col-md-6"),
            ),
            Row(
                Column("email", css_class="col-md-6"),
                Column("username", css_class="col-md-6"),
            ),
            Row(
                Column("user_type", css_class="col-md-6"),
                Column("country", css_class="col-md-6"),
            ),
            Row(
                Column("hourly_rate", css_class="col-md-4"),
                Column("phone_number", css_class="col-md-4"),
                Column("address", css_class="col-md-4"),
            ),
            Row(
                Column("password", css_class="col-md-6"),  # Add password field
            ),
            Row(
                Column(
                    Submit("submit", "Save", css_class="btn btn-success mx-2"),
                    Button(
                        "cancel",
                        "Cancel",
                        css_class="btn btn-secondary mx-2",
                        onclick="window.location.href='{}'".format(
                            reverse_lazy("accounts:users")
                        ),
                    ),
                    css_class="d-flex justify-content-center mt-3",
                ),
            ),
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "__all__"


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = "__all__"
