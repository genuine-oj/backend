from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend

from django.conf import settings
from django.http import HttpResponse
from wsgiref.util import FileWrapper

from zipfile import ZipFile
import hashlib

from .models import Problem
from .serializers import ProblemSerializer, ProblemDetailSerializer, TestCaseDetailSerializer, TestCaseUpdateSerializer
from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly


class ProblemPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class ProblemViewSet(ModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    pagination_class = ProblemPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['title']
    ordering_fields = ['id', 'title']
    filterset_fields = ['difficulty']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Problem.objects.all()
        return Problem.objects.filter(is_hidden=False)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProblemSerializer
        return ProblemDetailSerializer

    @action(detail=True, methods=['get', 'post'])
    def data(self, request, *args, **kwargs):
        instance = self.get_object().test_case
        if self.request.method == 'GET':
            mode = self.request.query_params.get('mode')
            if mode == 'fetch':
                file = self.request.query_params.get('file')
                test_case_file = settings.TEST_DATA_ROOT / str(instance.test_case_id) / file
                if not test_case_file.is_file():
                    raise NotFound('File not found')
                response = HttpResponse(FileWrapper(test_case_file.open('rb')))
                response['Content-Type'] = 'text/plain'
                return response
            else:
                serializer = TestCaseDetailSerializer(instance)
                return Response(serializer.data)
        else:
            data_dir = settings.TEST_DATA_ROOT / str(instance.test_case_id)
            serializer = TestCaseUpdateSerializer(instance=instance, data=self.request.data)
            serializer.is_valid(raise_exception=True)
            delete_cases = serializer.validated_data.get('delete_cases')
            if delete_cases:
                for case in delete_cases:
                    (data_dir / f'{case}.in').unlink(missing_ok=True)
                    (data_dir / f'{case}.ans').unlink(missing_ok=True)
                    (data_dir / f'{case}.md5').unlink(missing_ok=True)
            test_cases_file = serializer.validated_data.get('test_cases')
            if test_cases_file.size > 0:
                test_cases = ZipFile(test_cases_file, 'r')
                test_cases.extractall(data_dir)
                for file in test_cases.namelist():
                    file_name, file_ext = file.rsplit('.', 1)
                    if file_ext == 'ans':
                        file_data = test_cases.read(file)
                        file_hash = hashlib.md5(file_data).hexdigest()
                        (data_dir / f'{file_name}.md5').write_text(file_hash, encoding='utf-8')
            self.perform_update(serializer)
            serializer = TestCaseDetailSerializer(serializer.data)
            return Response(serializer.data)
