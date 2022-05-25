from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from .models import Submission
from .serializers import SubmissionSerializer, SubmissionDetailSerializer
from oj_backend.permissions import IsAdminOrReadCreate


class SubmissionViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadCreate]
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
