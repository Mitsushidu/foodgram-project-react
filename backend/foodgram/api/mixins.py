from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.viewsets import GenericViewSet


class GetListCreateDestroyUpdateViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    pass


class GetListViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    pass


class CreateDestroyViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    pass

class ListViewSet(
    ListModelMixin,
    GenericViewSet
):
    pass
