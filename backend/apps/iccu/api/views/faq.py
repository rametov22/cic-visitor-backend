from rest_framework import generics, permissions
from rest_framework.response import Response

from ...models import FAQ
from ..serializers import FAQSerializer

__all__ = ("FAQView",)


class FAQView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FAQSerializer

    def get(self, request):
        faqs = FAQ.objects.filter(is_active=True)
        return Response(self.get_serializer(faqs, many=True).data)
