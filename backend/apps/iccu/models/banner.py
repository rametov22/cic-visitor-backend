from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("Banner",)


class Banner(models.Model):
    name = models.CharField(_("Название"), max_length=255)
    short_name = models.CharField(_("Короткое название"), max_length=100, blank=True)
    image = models.ImageField(_("Изображение"), upload_to="banners/")
    city = models.CharField(_("Город"), max_length=100, default="Ташкент")
    country = models.CharField(_("Страна"), max_length=100, default="Узбекистан")
    is_active = models.BooleanField(_("Активный баннер"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Баннер")
        verbose_name_plural = _("Баннеры")

    def __str__(self):
        return self.short_name or self.name

    def clean(self):
        if self.is_active:
            qs = Banner.objects.filter(is_active=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    {"is_active": _("Активный баннер уже существует. Сначала деактивируйте текущий.")}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
