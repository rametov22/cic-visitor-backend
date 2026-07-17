from rest_framework import serializers

from ...models import TicketSource

__all__ = ("TicketSourceSerializer",)


class TicketSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketSource
        fields = [
            "id",
            "type",
            "title",
            "link_label",
            "link_url",
            "icon",
            "description",
        ]
