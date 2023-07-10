from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import Granted, IsAuthenticatedAndReadOnly
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView, DestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import User
from .serializers import (ChangePasswordSerializer, LoginSerializer,
                          UserBriefSerializer, UserDetailSerializer,
                          UserSerializer)


class UserPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class UserViewSet(ReadOnlyModelViewSet, DestroyAPIView):
    permission_classes = [Granted | IsAuthenticatedAndReadOnly]
    lookup_value_regex = r'\d+'
    pagination_class = UserPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'username']
    ordering_fields = ['id', 'username']
    filterset_fields = []
    queryset = User.objects.order_by('id')

    def get_serializer_class(self):
        if self.action == 'list':
            return UserBriefSerializer
        elif self.action == 'update':
            return UserSerializer
        return UserDetailSerializer

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if request.data.get('password'):
            user.set_password(request.data['password'])
        if request.data.get('is_staff') == True:
            user.is_staff = user.is_superuser = True
        else:
            user.is_staff = user.is_superuser = False
        user.save()
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False,
            methods=['post'],
            permission_classes=[IsAuthenticated],
            url_path='change_password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='ranking')
    def get_ranking(self, request):
        ...


class LoginView(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError(_('Uername or password error.'))
        if not user.is_active:
            raise ValidationError(_('User is disabled.'))
        login(request, user)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        logout(self.request)
        return Response(status=HTTP_204_NO_CONTENT)


class RegisterView(GenericAPIView):
    permission_classes = [] if settings.ALLOW_REGISTER else [Granted]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        user = User.objects.create_user(username=username, password=password)
        if not request.user.is_authenticated:
            login(request, user)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)


class InfoAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(instance=request.user,
                                         data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
