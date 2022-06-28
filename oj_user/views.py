from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_204_NO_CONTENT

from .serializers import LoginSerializer, UserDetailSerializer


class LoginView(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError(_('Uername or password error.'))
        if not user.is_active:
            raise ValidationError(_('User is disabled.'))
        login(self.request, user)
        serializer = UserDetailSerializer(instance=user)
        return Response({'user': serializer.data})


class LogoutView(APIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        logout(self.request)
        return Response(status=HTTP_204_NO_CONTENT)


class InfoAPIView(GenericAPIView):
    permission_classes = []
    serializer_class = UserDetailSerializer

    def get(self, *args, **kwargs):
        serializer = self.get_serializer(instance=self.request.user)
        return Response({'user': serializer.data})
