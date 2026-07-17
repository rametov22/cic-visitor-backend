from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.response import Response

from ...models import Schedule
from ..serializers import ScheduleDaySerializer, ScheduleListSerializer

__all__ = ("ScheduleView",)


class ScheduleView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ScheduleDaySerializer

    @extend_schema(responses=ScheduleListSerializer)
    def get(self, request):
        days = Schedule.objects.all()
        today = Schedule.today()

        return Response(
            {
                "schedule": ScheduleDaySerializer(days, many=True).data,
                "today": ScheduleDaySerializer(today).data if today else None,
            }
        )
