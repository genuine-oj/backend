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
        fields = [
            'id', 'username', 'email', 'real_name', 'student_id', 'is_staff'
        ]


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label=_('username'), max_length=150)
    password = serializers.CharField(label=_('password'))

    class Meta:
        model = User
        fields = ['username', 'password']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(label=_('old password'))
    new_password = serializers.CharField(label=_('new password'))

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('Old password error.'))
        return value
