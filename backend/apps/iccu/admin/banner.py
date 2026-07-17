from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from modeltranslation.admin import TabbedTranslationAdmin

from ..models import Banner

__all__ = ("PlaceBannerAdmin",)


@admin.register(Banner)
class PlaceBannerAdmin(TabbedTranslationAdmin):
    list_display = ["name", "city", "is_active"]
    list_filter = ["is_active", "city"]
    list_editable = ["is_active"]
    search_fields = ["name", "short_name"]

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "short_name", "image"),
            },
        ),
        (
            _("Местоположение"),
            {
                "fields": ("city", "country"),
            },
        ),
        (
            _("Статус"),
            {
                "fields": ("is_active",),
            },
        ),
    )
