from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class BaseViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def home(self, *args, **kwargs):
        # Home API
        return Response(
            status=status.HTTP_200_OK,
            data={
                "swagger-ui": "/api/v1/schema/swagger-ui/",
                "redoc": "/api/v1/schema/redoc/",
            },
        )
