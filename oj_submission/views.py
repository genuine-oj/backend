from django.conf import settings
from django.http import HttpResponse, StreamingHttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import (Granted, IsAuthenticatedAndReadCreate,
                                    IsAuthenticatedAndReadOnly)
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Submission
from .serializers import SubmissionDetailSerializer, SubmissionSerializer


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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['problem__id', 'user__username', 'language', 'status']

    def get_queryset(self):
        queryset = Submission.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_hidden=False)
        return queryset.order_by('-create_time')

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
            url_path=r'test-point/(?P<name>\w+)',
            url_name='Test Point Data')
    def test_point(self, request, name, *args, **kwargs):
        instance = self.get_object()
        mode = self.request.query_params.get('mode')
        ans_file = settings.TEST_DATA_ROOT / str(
            instance.problem.test_case.test_case_id) / f'{name}.ans'
        in_file = settings.TEST_DATA_ROOT / str(
            instance.problem.test_case.test_case_id) / f'{name}.in'
        out_file = settings.SUBMISSION_ROOT / str(instance.id) / f'{name}.out'
        if mode == 'fetch':
            length = -1
            file = self.request.query_params.get('file')
            if file not in ['in', 'out', 'ans']:
                return HttpResponse('FILE NOT FOUND', status=404)
            file = {'in': in_file, 'out': out_file, 'ans': ans_file}[file]
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
