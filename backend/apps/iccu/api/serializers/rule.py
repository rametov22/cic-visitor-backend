from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ...models import Rule, RuleCategory

__all__ = (
    "RuleCategorySerializer",
    "RuleItemSerializer",
)


class RuleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = ["id", "text"]


class RuleCategorySerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = RuleCategory
        fields = ["id", "name", "icon", "items"]

    @extend_schema_field(RuleItemSerializer(many=True))
    def get_items(self, obj):
        active_rules = obj.rules.filter(is_active=True)
        return RuleItemSerializer(active_rules, many=True).data
