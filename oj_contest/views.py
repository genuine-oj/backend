from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet

from .models import Contest
from .serializers import ContestDetailSerializer, ContestSerializer


class ContestPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class ContestViewSet(ModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    lookup_value_regex = r'\d+'
    pagination_class = ContestPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'title']
    ordering_fields = ['id', 'title']
    filterset_fields = []

    def get_queryset(self):
        if self.request.user.is_staff:
            return Contest.objects.all()
        return Contest.objects.filter(is_hidden=False)

    def get_serializer_class(self):
        if self.action == 'list':
            return ContestSerializer
        return ContestDetailSerializer
