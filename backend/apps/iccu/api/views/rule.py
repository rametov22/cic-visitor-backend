from rest_framework import generics, permissions
from rest_framework.response import Response

from ...models import RuleCategory
from ..serializers import RuleCategorySerializer

__all__ = ("RulesView",)


class RulesView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RuleCategorySerializer

    def get(self, request):
        categories = RuleCategory.objects.filter(is_active=True).prefetch_related("rules")
        return Response(self.get_serializer(categories, many=True).data)
