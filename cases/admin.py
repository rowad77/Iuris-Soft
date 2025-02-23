from django.contrib import admin
from .models import CaseType, Case, CaseActivity, CaseRuling, Document
from .models import Invoice, TimeEntry, ClientRetainer, RetainerUsage
from accounts.models import Client  # noqa


@admin.register(CaseType)
class CaseTypeAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    search_fields = ("title", "description")


class CaseActivityInline(admin.TabularInline):
    model = CaseActivity
    extra = 1


class CaseRulingInline(admin.TabularInline):
    model = CaseRuling
    extra = 1


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("user", "client_organization")
    search_fields = (
        "user__email",
        "user__username",
        "user__first_name",
        "user__last_name",
        "client_organization__name",
    )



@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("case_number", "title", "client", "status", "assigned_lawyer")
    list_filter = ("status", "case_type")
    search_fields = (
        "case_number",
        "title",
        "client__first_name",
        "client__last_name",
        "description",
    )
    filter_horizontal = ("assigned_users", "case_type")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["client"].required = True
        return form


@admin.register(CaseActivity)
class CaseActivityAdmin(admin.ModelAdmin):
    list_display = ("case", "user", "activity", "timestamp")
    list_filter = ("timestamp",)
    search_fields = ("case__case_number", "user__username", "activity")
    raw_id_fields = ("case", "user")


@admin.register(CaseRuling)
class CaseRulingAdmin(admin.ModelAdmin):
    list_display = ("case", "ruled_by", "ruling_date")
    list_filter = ("ruling_date",)
    search_fields = ("case__case_number", "ruling_text")
    raw_id_fields = ("case", "ruled_by")
    prepopulated_fields = {"slug": ("ruling_text",)}


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "case", "document_type")
    list_filter = ("document_type",)
    search_fields = ("title", "case__case_number", "description")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "case",
        "client",
        "date_issued",
        "due_date",
        "amount",
        "is_paid",
    )
    list_filter = ("is_paid", "date_issued", "due_date")
    search_fields = (
        "invoice_number",
        "case__case_number",
        "client__first_name",
        "client__last_name",
    )
    raw_id_fields = ("case", "client")

class RetainerUsageInline(admin.TabularInline):
    model = RetainerUsage
    extra = 1


@admin.register(ClientRetainer)
class ClientRetainerAdmin(admin.ModelAdmin):
    list_display = ("client", "amount", "start_date", "end_date", "remaining_balance")
    list_filter = ("start_date", "end_date")
    search_fields = ("client__first_name", "client__last_name")
@admin.register(RetainerUsage)
class RetainerUsageAdmin(admin.ModelAdmin):
    list_display = ("retainer", "amount", "date", "description")
    list_filter = ("date",)
    search_fields = (
        "retainer__client__first_name",
        "retainer__client__last_name",
        "description",
    )
    raw_id_fields = ("retainer",)


@admin.action(description="Bill selected Time Entries (Retainer or Invoice)")
def bill_time_entries(modeladmin, request, queryset):
    unbilled_entries = queryset.filter(is_billed=False)
    for entry in unbilled_entries:
        entry.auto_deduct_or_invoice()
    modeladmin.message_user(request, f"Billed {unbilled_entries.count()} time entries.")

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ("case", "client", "user", "start_time", "end_time", "is_billed")
    actions = [bill_time_entries]