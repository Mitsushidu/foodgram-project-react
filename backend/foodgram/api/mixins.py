from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.viewsets import GenericViewSet


class GetListCreateDestroyUpdateViewSet(
    GenericViewSet,
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    DestroyModelMixin
):
    pass
