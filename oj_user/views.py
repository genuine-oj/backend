from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_204_NO_CONTENT

from .serializers import UserDetailSerializer


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, *args, **kwargs):
        username = self.request.data.get('username')
        password = self.request.data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError('用户名或密码错误')
        if not user.is_active:
            raise ValidationError('用户未激活')
        login(self.request, user)
        serializer = UserDetailSerializer(instance=user)
        return Response({'user': serializer.data})


class LogoutView(APIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        logout(self.request)
        return Response(status=HTTP_204_NO_CONTENT)


class InfoAPIView(APIView):
    permission_classes = []

    def get(self, *args, **kwargs):
        serializer = UserDetailSerializer(instance=self.request.user)
        return Response({'user': serializer.data})
