from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination

from oj_backend.permissions import Granted, IsAuthenticatedAndReadCreate
from .models import Submission
from .serializers import SubmissionSerializer, SubmissionDetailSerializer


class SubmissionPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class SubmissionViewSet(ModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadCreate]
    pagination_class = SubmissionPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['problem__id', 'user__username', 'language', 'status']

    def get_queryset(self):
        if self.request.user.is_staff:
            instance = Submission.objects.all()
        else:
            instance = Submission.objects.filter(is_hidden=False)
        return instance.order_by('-create_time')

    def get_serializer_class(self):
        if self.action == 'list':
            return SubmissionSerializer
        return SubmissionDetailSerializer
