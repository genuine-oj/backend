from rest_framework import serializers

from .models import Contest, ContestProblem, ContestUser


class ContestJoined(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        request = self.context.get('request')
        return value.filter(user=request.user).exists()


class ContestSerializer(serializers.ModelSerializer):
    joined = ContestJoined(source='users')

    class Meta:
        model = Contest
        fields = ['id', 'title', 'start_time', 'end_time', 'joined']
