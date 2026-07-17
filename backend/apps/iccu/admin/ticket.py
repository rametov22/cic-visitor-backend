from django.contrib import admin
from django.utils.html import format_html

from modeltranslation.admin import TabbedTranslationAdmin

from ..models import TicketSource, Type

__all__ = ("TicketSourceAdmin",)


@admin.register(TicketSource)
class TicketSourceAdmin(TabbedTranslationAdmin):
    list_display = ["order", "title", "type", "get_preview", "get_link"]
    list_display_links = ["title"]
    list_editable = ["order"]
    list_filter = ["type"]
    ordering = ["order"]

    fieldsets = (
        (
            None,
            {
                "fields": ("type", "title", "icon", "order"),
            },
        ),
        (
            "Ссылка",
            {
                "fields": ("link_label", "link_url"),
                "description": 'Заполняется только для типа "Ссылка".',
                "classes": ("collapse",),
            },
        ),
        (
            "Информация",
            {
                "fields": ("description",),
                "description": 'Заполняется только для типа "Информация".',
                "classes": ("collapse",),
            },
        ),
    )

    class Media:
        js = ()
        css = {"all": ()}

    def get_fieldsets(self, request, obj=None):
        """Раскрываем нужную секцию в зависимости от типа."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.type == Type.LINK:
            # Убираем collapse у секции "Ссылка"
            return [
                fieldsets[0],
                (fieldsets[1][0], {**fieldsets[1][1], "classes": ()}),
                fieldsets[2],
            ]
        elif obj and obj.type == Type.INFO:
            # Убираем collapse у секции "Информация"
            return [
                fieldsets[0],
                fieldsets[1],
                (fieldsets[2][0], {**fieldsets[2][1], "classes": ()}),
            ]
        return fieldsets

    @admin.display(description="Превью")
    def get_preview(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" style="width:24px;height:24px;object-fit:contain;'
                'border-radius:4px;vertical-align:middle;">',
                obj.icon.url,
            )
        return "—"

    @admin.display(description="Ссылка / Описание")
    def get_link(self, obj):
        if obj.type == Type.LINK and obj.link_url:
            return format_html(
                '<a href="{}" target="_blank" style="color:#417690;">{}</a>',
                obj.link_url,
                obj.link_label or obj.link_url,
            )
        if obj.type == Type.INFO and obj.description:
            text = obj.description[:80]
            if len(obj.description) > 80:
                text += "…"
            return format_html(
                '<span style="color:#666;">{}</span>',
                text,
            )
        return "—"
