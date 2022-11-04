from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from oj_backend.permissions import IsAuthenticatedAndReadOnly
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import User
from .serializers import LoginSerializer, UserDetailSerializer, UserSerializer, ChangePasswordSerializer


class UserPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class UserViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticatedAndReadOnly]
    lookup_value_regex = r'\d+'
    pagination_class = UserPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['id', 'username']
    ordering_fields = ['id', 'username']
    filterset_fields = []
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        return UserDetailSerializer

    @action(detail=False, methods=['post'], url_path='change_password')
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response({'detail': _('Password changed.')})


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
        serializer = UserDetailSerializer(instance=user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        logout(self.request)
        return Response(status=HTTP_204_NO_CONTENT)


class RegisterView(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        serializer = UserDetailSerializer(instance=user)
        return Response(serializer.data)


class InfoAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = UserDetailSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data)
