from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from .serializers import LoginSerializer, UserDetailSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, *args, **kwargs):
        serializer = LoginSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        serializer = UserDetailSerializer(instance=user)
        return Response({'token': token, 'user': serializer.data})
