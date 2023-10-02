from django.utils import timezone
from oj_problem.models import Problem
from oj_problem.serializers import ProblemSerializer
from oj_user.models import User
from oj_user.serializers import UserBriefSerializer
from rest_framework import serializers

from .models import Contest, ContestUser


class ContestJoined(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        request = self.context.get('request')
        return value.filter(id=request.user.id).exists()


class ContestSerializer(serializers.ModelSerializer):
    joined = ContestJoined(source='users')

    class Meta:
        model = Contest
        fields = [
            'id', 'title', 'start_time', 'end_time', 'joined',
            'problem_list_mode', 'is_hidden'
        ]


class ContestBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contest
        fields = ['id', 'title', 'problem_list_mode', 'is_hidden']


class ProblemsField(serializers.Field):

    def to_representation(self, value):
        request = self.context.get('request')
        if 'contest' not in request.user.permissions and value.start_time > timezone.now(
        ):
            return []
        queryset = value.problems.all()
        return ProblemSerializer(queryset, many=True,
                                 context=self.context).data

    def to_internal_value(self, data):
        return {'problems': [Problem.objects.get(id=i) for i in data]}


class UsersField(serializers.Field):

    def to_representation(self, value):
        return UserBriefSerializer(value, many=True).data

    def to_internal_value(self, data):
        return [User.objects.get(id=i) for i in data]


class ContestDetailSerializer(serializers.ModelSerializer):
    joined = ContestJoined(source='users')
    problems = ProblemsField(required=False, source='*')
    users = UsersField(required=False)

    class Meta:
        model = Contest
        fields = [
            'id', 'title', 'start_time', 'end_time', 'joined', 'description',
            'problem_list_mode', 'is_hidden', 'allow_sign_up', 'problems',
            'users'
        ]
        read_only_fields = ['id']
