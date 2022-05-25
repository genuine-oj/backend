from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150)
    user = None

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def validate(self, attrs):
        try:
            user = User.objects.get(username=attrs['username'])
            if not user.is_active:
                raise ValidationError({'username': '用户已停用'})
            if user.check_password(attrs['password']):
                self.user = user
                return attrs
            else:
                raise ValidationError({'password': '密码错误'})
        except User.DoesNotExist:
            raise ValidationError({'username': '用户不存在'})


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'real_name', 'student_id', 'is_staff']
