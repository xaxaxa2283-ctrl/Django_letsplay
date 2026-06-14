from django.contrib import admin

from .models import ConsentRecord


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ("purpose", "subject_identifier", "policy_version", "ip_address", "accepted_at")
    list_filter = ("purpose", "policy_version", "accepted_at")
    search_fields = ("subject_identifier", "ip_address")
    readonly_fields = ("purpose", "subject_identifier", "policy_version", "ip_address", "user_agent", "accepted_at")
