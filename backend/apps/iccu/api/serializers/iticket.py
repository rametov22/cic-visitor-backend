from rest_framework import serializers

from ...models import iTicket

__all__ = ("iTicketSerializer",)


class iTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = iTicket
        fields = ("id", "name", "url")
