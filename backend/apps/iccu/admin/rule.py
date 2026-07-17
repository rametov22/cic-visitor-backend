from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from ..models import Rule, RuleCategory


class RuleInline(TranslationTabularInline):
    model = Rule
    extra = 1
    fields = ["order", "text", "is_active"]
    ordering = ["order"]


@admin.register(RuleCategory)
class RuleCategoryAdmin(TabbedTranslationAdmin):
    list_display = ["order", "name", "icon_preview", "rules_count", "is_active"]
    list_editable = ["order", "is_active"]
    list_display_links = ["name"]
    ordering = ["order"]
    inlines = [RuleInline]

    @admin.display(description=_("Иконка"))
    def icon_preview(self, obj):
        if obj.icon:
            from django.utils.html import format_html

            return format_html('<img src="{}" height="30" />', obj.icon.url)
        return "-"

    @admin.display(description=_("Кол-во правил"))
    def rules_count(self, obj):
        return obj.rules.count()
