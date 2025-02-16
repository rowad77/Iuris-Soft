from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from accounts.forms import UserAdminChangeForm, UserAdminCreationForm
from .models import  Profile, Organization, Client

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
    )
    list_selected_related = True
    list_filter = ("first_name",)
    fieldsets = (
        (
            "USER NAMES,EMAIL & PASSWORD",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "password",
                ),
            },
        ),
        (
            "PERMISSIONS",
            {
                "fields": (
                     "active",
                    "staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            "USER DETAILS",
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                    "user_type",
                    "email",
                    "password1",
                    "password2",
                    "staff",
                     "active",
                ),
            },
        ),
    )

    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")


admin.site.register(User, UserAdmin)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "superadmin",
        "country",
        "created_by",
        "created",
        "updated",
    )
    search_fields = ("name", "superadmin__email", "superadmin__username")
    readonly_fields = ("slug", "created", "updated")