from django.contrib import admin
from django.utils.html import format_html

from ..models import iTicket

__all__ = ("iTicketAdmin",)


@admin.register(iTicket)
class iTicketAdmin(admin.ModelAdmin):
    list_display = ("name", "url_link", "status_badge")
    list_editable = ("is_active",) if False else ()  # нет, лучше через actions
    list_filter = ("is_active",)
    search_fields = ("name", "url")

    fields = ("name", "url", "is_active")

    def url_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)

    url_link.short_description = "URL"

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#22c55e; color:#fff; padding:3px 10px; '
                'border-radius:12px; font-size:12px;">Active</span>'
            )
        return format_html(
            '<span style="background:#94a3b8; color:#fff; padding:3px 10px; '
            'border-radius:12px; font-size:12px;">Inactive</span>'
        )

    status_badge.short_description = "Status"

    @admin.action(description="Activate selected ticket")
    def make_active(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly one ticket to activate.", level="error")
            return
        iTicket.objects.filter(is_active=True).update(is_active=False)
        queryset.update(is_active=True)
        self.message_user(request, "Ticket activated.")

    @admin.action(description="Deactivate selected tickets")
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Tickets deactivated.")

    actions = ("make_active", "make_inactive")
