from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = (
    "Complex",
    "Place",
)


class Complex(models.Model):
    title = models.CharField(_("Комплекс"), max_length=255)
    orienteer = models.CharField(_("Ориентир"), max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(_("Порядок"), default=0)
    is_active = models.BooleanField(_("Активно"), default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Комплекс")
        verbose_name_plural = _("Комплексы")

    def __str__(self):
        return self.title


class Place(models.Model):
    complex = models.ForeignKey(
        Complex,
        on_delete=models.CASCADE,
        related_name="places",
        verbose_name=_("Комплекс"),
    )
    name = models.CharField(_("Место"), max_length=255)
    full_name = models.CharField(_("Расширенное название"), max_length=500, blank=True)
    icon = models.ImageField(_("Иконка"), upload_to="places/", blank=True)
    link = models.URLField(_("Ссылка на местоположение"), blank=True, null=True)
    latitude = models.FloatField(_("Широта"), blank=True, null=True)
    longitude = models.FloatField(_("Долгота"), blank=True, null=True)
    order = models.PositiveSmallIntegerField(_("Порядок"), default=0)
    is_active = models.BooleanField(_("Активно"), default=True)

    class Meta:
        ordering = ["complex__order", "order"]
        verbose_name = _("Место")
        verbose_name_plural = _("Места")

    def clean(self):
        has_link = bool(self.link)
        has_coords = self.latitude is not None and self.longitude is not None
        if not has_link and not has_coords:
            raise ValidationError(_("Укажите ссылку на местоположение или координаты (широта и долгота)."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
