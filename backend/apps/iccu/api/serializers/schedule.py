from django.utils import timezone

from rest_framework import serializers

from ...models import Schedule

__all__ = ("ScheduleDaySerializer", "ScheduleListSerializer")


class ScheduleDaySerializer(serializers.ModelSerializer):
    weekday = serializers.CharField(source="get_weekday_display")
    is_today = serializers.SerializerMethodField()
    open = serializers.TimeField(source="open_time", format="%H:%M")
    close = serializers.TimeField(source="close_time", format="%H:%M")

    class Meta:
        model = Schedule
        fields = [
            "weekday",
            "is_today",
            "is_working",
            "force_closed",
            "open",
            "close",
            "note",
            "is_open_now",
            "hours_display",
        ]

    def get_is_today(self, obj) -> bool:
        return obj.weekday == timezone.localtime().isoweekday()


class ScheduleListSerializer(serializers.Serializer):
    schedule = ScheduleDaySerializer(many=True)
    today = ScheduleDaySerializer()
