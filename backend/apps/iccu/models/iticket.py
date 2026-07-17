from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("iTicket",)


class iTicket(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    url = models.URLField(_("Url"))
    is_active = models.BooleanField(_("Is Active"), default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="unique_active_ticket",
            )
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            iTicket.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
