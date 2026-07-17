from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from ..models import Complex, Place


class PlaceInline(TranslationTabularInline):
    model = Place
    extra = 1
    fields = ["order", "name", "full_name", "icon", "link", "latitude", "longitude", "is_active"]
    ordering = ["order"]


@admin.register(Complex)
class ComplexAdmin(TabbedTranslationAdmin):
    list_display = ["order", "title", "orienteer", "places_count", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["title"]
    list_filter = ["is_active"]
    search_fields = ["title", "orienteer"]
    ordering = ["order"]
    inlines = [PlaceInline]

    @admin.display(description=_("Кол-во мест"))
    def places_count(self, obj):
        return obj.places.count()
