from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("Rule", "RuleCategory")


class RuleCategory(models.Model):
    name = models.CharField(_("Название"), max_length=100)
    order = models.PositiveSmallIntegerField(_("Порядок"), default=0)
    is_active = models.BooleanField(_("Активно"), default=True)
    icon = models.ImageField(_("Икона"), upload_to="rule_category/")

    class Meta:
        ordering = ["order"]
        verbose_name = _("Категория правил")
        verbose_name_plural = _("Категории правил")

    def __str__(self):
        return self.name


class Rule(models.Model):
    category = models.ForeignKey(
        RuleCategory,
        on_delete=models.CASCADE,
        related_name="rules",
        verbose_name=_("Категория"),
    )
    text = models.CharField(_("Текст"), max_length=500)
    order = models.PositiveSmallIntegerField(_("Порядок"), default=0)
    is_active = models.BooleanField(_("Активно"), default=True)

    class Meta:
        ordering = ["category__order", "order"]
        verbose_name = _("Правило")
        verbose_name_plural = _("Правила и рекомендации")

    def __str__(self):
        return f"{self.category}: {self.text[:50]}"
