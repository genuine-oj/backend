from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'real_name', 'student_id', 'is_staff']


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(label=_('password'))

    class Meta:
        model = User
        fields = ['username', 'password']
