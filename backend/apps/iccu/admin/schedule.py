from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from modeltranslation.admin import TabbedTranslationAdmin

from ..models import Schedule


class ScheduleAdminForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = "__all__"
        widgets = {
            "open_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
            "close_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
        }


@admin.register(Schedule)
class ScheduleAdmin(TabbedTranslationAdmin):
    form = ScheduleAdminForm
    list_display = ["get_weekday", "is_working", "open_time", "close_time", "note"]
    list_editable = ["is_working", "open_time", "close_time"]
    ordering = ["weekday"]

    def has_add_permission(self, request):
        return Schedule.objects.count() < 7

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description=_("День"))
    def get_weekday(self, obj):
        return obj.get_weekday_display()
