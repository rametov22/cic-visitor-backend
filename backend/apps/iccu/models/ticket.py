from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from modeltranslation.utils import build_localized_fieldname

from .constants import Type

__all__ = ("TicketSource",)


class TicketSource(models.Model):
    type = models.CharField(_("Тип"), max_length=10, choices=Type.choices, default=Type.LINK)
    title = models.CharField(_("Заголовок"), max_length=255)
    # Для type=link
    link_label = models.CharField(_("Текст ссылки"), max_length=255, blank=True)
    link_url = models.URLField(_("URL"), blank=True)
    icon = models.ImageField(_("Иконка"), upload_to="ticket_sources/", blank=True)
    # Для type=info
    description = models.TextField(_("Описание"), blank=True)

    order = models.PositiveSmallIntegerField(_("Порядок"), default=0)

    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Источник билетов")
        verbose_name_plural = _("Источники билетов")

    def clean(self):
        errors = {}

        desc_fields = [build_localized_fieldname("description", lang[0]) for lang in settings.LANGUAGES]
        has_description = any(getattr(self, f, None) for f in desc_fields)

        if self.type == Type.LINK:
            if has_description:
                for f in desc_fields:
                    if getattr(self, f, None):
                        errors[f] = _("Для типа «Ссылка» описание не заполняется.")
            if not self.link_url:
                errors["link_url"] = _("Для типа «Ссылка» ссылка обязательна.")
            if not self.link_label:
                errors["link_label"] = _("Для типа «Ссылка» этикетка обязательна.")

        elif self.type == Type.INFO:
            if self.link_label:
                errors["link_label"] = _("Для типа «Информация» текст ссылки не заполняется.")
            if self.link_url:
                errors["link_url"] = _("Для типа «Информация» URL не заполняется.")
            if not has_description:
                default_field = build_localized_fieldname("description", settings.LANGUAGE_CODE[:2])
                errors[default_field] = _("Для типа «Инфо» описание обязательно.")

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
