from rest_framework import generics, permissions
from rest_framework.response import Response

from ...models import Complex, Place
from ..serializers import ComplexSerializer, PlaceSerializer

__all__ = ("ComplexListView", "PlaceListView")


class PlaceListView(generics.GenericAPIView):
    """Все места единым списком."""

    permission_classes = [permissions.AllowAny]
    serializer_class = PlaceSerializer

    def get(self, request):
        places = Place.objects.filter(is_active=True)
        return Response(self.get_serializer(places, many=True).data)


class ComplexListView(generics.GenericAPIView):
    """Места, сгруппированные по комплексам."""

    permission_classes = [permissions.AllowAny]
    serializer_class = ComplexSerializer

    def get(self, request):
        complexes = Complex.objects.filter(is_active=True).prefetch_related("places")
        return Response(self.get_serializer(complexes, many=True).data)
