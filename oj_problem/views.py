import hashlib
import json
from wsgiref.util import FileWrapper
from zipfile import ZipFile

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet

from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly
from .models import Problem, TestCase, Tags
from .serializers import ProblemSerializer, ProblemDetailSerializer, \
    TestCaseDetailSerializer, TestCaseUpdateSerializer, TagsSerializer


def partly_read(file, length, file_size):
    with open(str(file), 'r', encoding='utf-8') as f:
        content = f.read(length)
        if 0 <= length < file_size:
            content += '...'
    return content


class ProblemPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class ProblemViewSet(ModelViewSet):
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    lookup_value_regex = r'\d+'
    pagination_class = ProblemPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'title']
    ordering_fields = ['id', 'title']
    filterset_fields = ['difficulty', 'tags__id']

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Problem.objects
        else:
            queryset = Problem.objects.filter(is_hidden=False)
        return queryset.order_by('id')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProblemSerializer
        return ProblemDetailSerializer


class DataViewSet(GenericViewSet, RetrieveModelMixin):
    queryset = TestCase.objects.all()
    permission_classes = [Granted]
    lookup_field = 'problem__id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestCaseDetailSerializer
        else:
            return TestCaseUpdateSerializer

    @action(methods=['get'], detail=True, url_path='file/(?P<file>.+)')
    def fetch_file(self, request, file, *args, **kwargs):
        instance = self.get_object()
        partly = request.query_params.get('partly') == 'true'
        length = 255 if partly else -1
        test_case_file = settings.TEST_DATA_ROOT / str(
            instance.test_case_id) / file
        if not test_case_file.is_file():
            raise NotFound(_('File not found.'))
        response = HttpResponse(
            partly_read(
                test_case_file,
                length,
                test_case_file.stat().st_size,
            ))
        response['Content-Type'] = 'text/plain'
        return response

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK:
            openapi.Response(
                description='',
                schema=TestCaseDetailSerializer,
            )
        })
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data_dir = settings.TEST_DATA_ROOT / str(instance.test_case_id)
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        delete_cases = serializer.validated_data.get('delete_cases')
        # if delete_cases:
        #     for case in delete_cases:
        #         (data_dir / f'{case}.in').unlink(missing_ok=True)
        #         (data_dir / f'{case}.ans').unlink(missing_ok=True)
        #         (data_dir / f'{case}.md5').unlink(missing_ok=True)
        test_cases_file = serializer.validated_data.get('test_cases')
        if test_cases_file and test_cases_file.size > 0:
            test_cases = ZipFile(test_cases_file, 'r')
            test_cases.extractall(data_dir)
            for file in test_cases.namelist():
                file_name, file_ext = file.rsplit('.', 1)
                if file_ext == 'ans':
                    file_data = test_cases.read(file)
                    file_data = b'\n'.join(
                        map(bytes.rstrip,
                            file_data.rstrip().splitlines()))
                    file_hash = hashlib.md5(file_data).hexdigest()
                    (data_dir / f'{file_name}.md5').write_text(
                        file_hash, encoding='utf-8')
        serializer.save()
        serializer = TestCaseDetailSerializer(serializer.data)
        return Response(serializer.data)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    serializer_class = TagsSerializer

    def create(self, request, *args, **kwargs):
        create = request.data.get('create')
        for i in create:
            Tags.objects.create(name=i)
        update = request.data.get('update')
        for i in update:
            Tags.objects.filter(id=i['id']).update(name=i['name'])
        delete = request.data.get('delete')
        for i in delete:
            Tags.objects.filter(id=i).delete()
        return Response(TagsSerializer(Tags.objects.all(), many=True).data)
