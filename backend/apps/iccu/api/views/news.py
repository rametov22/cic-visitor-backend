from django.utils.translation import gettext as _

import httpx
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ...services import fetch_news, fetch_news_detail

__all__ = (
    "news_categories",
    "news_detail",
    "news_list",
)


@extend_schema(
    operation_id="iccu_news_list",
    parameters=[
        OpenApiParameter(name="page", type=int, default=1),
        OpenApiParameter(name="lang", type=str, default="ru"),
        OpenApiParameter(
            name="category",
            type=int,
            required=False,
            description="1=Events, 2=Activities, 3=Visits, 5=Articles, 6=Media about us",
        ),
    ],
    responses=OpenApiTypes.OBJECT,
)
# @extend_schema(
#     parameters=[
#         OpenApiParameter(name="page", type=int, default=1),
#         OpenApiParameter(name="lang", type=str, default="ru"),
#         OpenApiParameter(
#             name="category",
#             type=int,
#             required=False,
#             description=_(
#                 "1=Events, 2=Activities, 3=Visits, 5=Articles, 6=Media about us"
#             ),
#         ),
#     ],
# )
@api_view(["GET"])
def news_list(request):
    page = int(request.query_params.get("page", 1))
    lang = request.query_params.get("lang", "ru")
    category = request.query_params.get("category")
    if category:
        category = int(category)

    try:
        data = fetch_news(page=page, lang=lang, category=category)
        return Response(data)
    except httpx.HTTPStatusError as e:
        return Response(
            {"error": "News service unavailable"},
            status=e.response.status_code,
        )
    except httpx.RequestError:
        return Response(
            {"error": "Failed to connect to news service"},
            status=502,
        )


@extend_schema(
    operation_id="iccu_news_detail",
    parameters=[
        OpenApiParameter(name="lang", type=str, default="ru"),
    ],
    responses=OpenApiTypes.OBJECT,
)
@api_view(["GET"])
def news_detail(request, news_id: int):
    lang = request.query_params.get("lang", "ru")

    try:
        data = fetch_news_detail(news_id, lang=lang)
        return Response(data)
    except httpx.HTTPStatusError as e:
        return Response(
            {"error": "Article not found"},
            status=e.response.status_code,
        )
    except httpx.RequestError:
        return Response(
            {"error": "Failed to connect to news service"},
            status=502,
        )


@extend_schema(
    summary="News categories",
    responses=inline_serializer(
        "NewsCategory",
        fields={
            "id": serializers.IntegerField(),
            "name": serializers.CharField(),
        },
        many=True,
    ),
)
@api_view(["GET"])
def news_categories(request):
    categories = [
        {"id": 1, "name": _("Events")},
        {"id": 2, "name": _("Activities")},
        {"id": 3, "name": _("Visits")},
        {"id": 5, "name": _("Articles")},
        {"id": 6, "name": _("Media about us")},
    ]
    return Response(categories)


# @api_view(["GET"])
# def news_categories(request):
#     categories = [
#         {"id": 1, "name": "Events"},
#         {"id": 2, "name": "Activities"},
#         {"id": 3, "name": "Visits"},
#         {"id": 5, "name": "Articles"},
#         {"id": 6, "name": "Media about us"},
#     ]
#     return Response(categories)
