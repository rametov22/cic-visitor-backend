from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from modeltranslation.admin import TabbedTranslationAdmin

from ..models import FAQ


@admin.register(FAQ)
class FAQAdmin(TabbedTranslationAdmin):
    list_display = ["order", "short_question", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["short_question"]
    list_filter = ["is_active"]
    search_fields = ["question", "answer"]
    ordering = ["order"]

    @admin.display(description=_("Вопрос"))
    def short_question(self, obj):
        return obj.question[:100]
