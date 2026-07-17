from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .constants import WeekDays

__all__ = ("Schedule",)


class Schedule(models.Model):
    weekday = models.PositiveSmallIntegerField(_("День недели"), choices=WeekDays.choices, unique=True)
    is_working = models.BooleanField(_("Рабочий день"), default=True)
    force_closed = models.BooleanField(_("Временно закрыто"), default=False)
    open_time = models.TimeField(_("Открытие"), null=True, blank=True)
    close_time = models.TimeField(_("Закрытие"), null=True, blank=True)
    note = models.CharField(_("Заметка"), max_length=255, blank=True)

    class Meta:
        ordering = ["weekday"]
        verbose_name = _("Расписание")
        verbose_name_plural = _("Расписание")

    def __str__(self):
        return self.get_weekday_display()

    def clean(self):
        if self.is_working and (not self.open_time or not self.close_time):
            raise ValidationError(_("Для рабочего дня укажите время открытия и закрытия."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_open_now(self) -> bool:
        if not self.is_working or self.force_closed:
            return False
        if self.weekday != timezone.localtime().isoweekday():
            return False
        if not self.open_time or not self.close_time:
            return False
        current = timezone.localtime().time()
        if self.close_time < self.open_time:
            return current >= self.open_time or current < self.close_time
        return self.open_time <= current < self.close_time

    @property
    def status(self) -> str:
        if self.force_closed:
            return "force_closed"
        if not self.is_working:
            return "closed"
        return "open" if self.is_open_now else "closed"

    @property
    def status_display(self) -> str:
        return {
            "force_closed": _("Временно закрыто"),
            "open": _("Открыто сейчас"),
            "closed": _("Закрыто"),
        }[self.status]

    @property
    def hours_display(self) -> str | None:
        if not self.is_working or not self.open_time or not self.close_time:
            return None
        return f"{self.open_time:%H:%M} – {self.close_time:%H:%M}"

    @classmethod
    def today(cls):
        """Возвращает объект Schedule на сегодня или None."""
        return cls.objects.filter(weekday=timezone.localtime().isoweekday()).first()
