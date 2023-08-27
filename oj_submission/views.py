from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse, StreamingHttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import (Granted, IsAuthenticatedAndReadCreate,
                                    IsAuthenticatedAndReadOnly)
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Submission, StatusChoices
from .serializers import SubmissionDetailSerializer, SubmissionSerializer
from oj_contest.models import Contest


class SubmissionPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


def partly_read(file, length, file_size):
    with open(str(file), 'r', encoding='utf-8') as f:
        content = f.read(length)
        if 0 <= length < file_size:
            content += '...'
    return content


def file_iterator(file, chunk_size=512):
    with open(file) as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


class SubmissionViewSet(ReadOnlyModelViewSet, CreateModelMixin):
    permission_classes = [Granted | IsAuthenticatedAndReadCreate]
    pagination_class = SubmissionPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['problem__id', 'user__username', 'language', 'status']
    ordering_fields = [
        'create_time', 'execute_time', 'execute_memory', 'score'
    ]

    def get_queryset(self):
        site_settings = cache.get('site_settings')
        if self.request.user.is_staff:
            queryset = Submission.objects
        elif site_settings.get('forceHideSubmissions'):
            queryset = Submission.objects.filter(user=self.request.user)
        else:
            processing_contest = Contest.objects.filter(
                start_time__lt=timezone.now(), end_time__gt=timezone.now())
            queryset = Submission.objects.exclude(
                Q(_is_hidden=True) | Q(problem___is_hidden=True)
                | Q(problem__hide_submissions=True)
                | Q(problem__contests__contest__in=processing_contest)
            ) | Submission.objects.filter(Q(user=self.request.user))
            queryset = queryset.distinct()
        return queryset.order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return SubmissionSerializer
        return SubmissionDetailSerializer

    @action(detail=True,
            methods=['get'],
            permission_classes=[IsAuthenticatedAndReadOnly],
            url_path='status')
    def get_status(self, request, pk=None):
        submission = self.get_object()
        return Response({'status': submission.status})

    @action(detail=True,
            methods=['get'],
            permission_classes=[IsAuthenticatedAndReadOnly],
            name='Get test point detail',
            url_path=r'test-point/(?P<name>.+)',
            url_name='Test Point Data')
    def test_point(self, request, name, *args, **kwargs):
        instance = self.get_object()

        if not instance.allow_download:
            return HttpResponse(
                'CURRENT SUBMISSION IS NOT ALLOWED TO DOWNLOAD CASE DATA',
                status=403)
        elif instance.status <= StatusChoices.COMPILE_ERROR or instance.status == StatusChoices.SYSTEM_ERROR:
            return HttpResponse(
                'SUBMISSION IN CURRENT STATUS IS NOT ALLOWED TO DOWNLOAD CASE DATA',
                status=403)

        mode = self.request.query_params.get('mode')
        ans_file = settings.TEST_DATA_ROOT / str(
            instance.problem.test_case.test_case_id) / f'{name}.ans'
        in_file = settings.TEST_DATA_ROOT / str(
            instance.problem.test_case.test_case_id) / f'{name}.in'
        out_file = settings.SUBMISSION_ROOT / str(instance.id) / f'{name}.out'

        if mode == 'fetch':
            length = -1
            file = self.request.query_params.get('file')
            file = {'in': in_file, 'out': out_file, 'ans': ans_file}.get(file)
            if file is None:
                return HttpResponse('FILE NOT FOUND', status=404)
            return StreamingHttpResponse(file_iterator(file))
        else:
            length = 255
            ans = _in = out = 'FILE NOT FOUND'
            if ans_file.exists():
                ans = partly_read(ans_file, length, ans_file.stat().st_size)
            if in_file.exists():
                _in = partly_read(in_file, length, in_file.stat().st_size)
            if out_file.exists():
                out = partly_read(out_file, length, out_file.stat().st_size)
            return Response({'ans': ans, 'in': _in, 'out': out})
