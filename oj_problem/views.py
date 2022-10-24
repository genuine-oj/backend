import hashlib
from wsgiref.util import FileWrapper
from zipfile import ZipFile

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet

from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly
from .models import Problem, TestCase, Tags
from .serializers import ProblemSerializer, ProblemDetailSerializer, \
    TestCaseDetailSerializer, TestCaseUpdateSerializer, TagsSerializer


class ProblemPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class ProblemViewSet(ModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    lookup_value_regex = r'\d+'
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


class DataViewSet(GenericViewSet):
    queryset = TestCase.objects.all()
    permission_classes = [Granted]
    lookup_field = 'problem__id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestCaseDetailSerializer
        else:
            return TestCaseUpdateSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        mode = request.query_params.get('mode')
        if mode == 'fetch':
            file = request.query_params.get('file')
            test_case_file = settings.TEST_DATA_ROOT / str(instance.test_case_id) / file
            if not test_case_file.is_file():
                raise NotFound(_('File not found.'))
            response = HttpResponse(FileWrapper(test_case_file.open('rb')))
            response['Content-Type'] = 'text/plain'
            return response
        else:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='',
                schema=TestCaseDetailSerializer,
            )
        }
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data_dir = settings.TEST_DATA_ROOT / str(instance.test_case_id)
        serializer = self.get_serializer(instance=instance, data=request.data)
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
                    file_data = b'\n'.join(map(bytes.rstrip, file_data.rstrip().splitlines()))
                    file_hash = hashlib.md5(file_data).hexdigest()
                    (data_dir / f'{file_name}.md5').write_text(file_hash, encoding='utf-8')
        serializer.save()
        serializer = TestCaseDetailSerializer(serializer.data)
        return Response(serializer.data)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    permission_classes = [IsAuthenticatedAndReadOnly]
    serializer_class = TagsSerializer
