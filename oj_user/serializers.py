from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import User
from oj_submission.models import StatusChoices
from oj_submission.models import Submission
from oj_problem.serializers import ProblemSolveSerializer, ProblemBriefSerializer


class UserBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'avatar']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'real_name', 'student_id', 'is_staff',
            'avatar'
        ]
        read_only_fields = ['id', 'username', 'is_staff', 'problem_solve']


class _SubmissionSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer()
    problem = ProblemBriefSerializer()

    class Meta:
        model = Submission
        fields = [
            'id', 'user', 'problem', 'language', 'status', 'score',
            'execute_time', 'execute_memory', 'create_time'
        ]
        read_only_fields = [
            'status', 'score', 'execute_time', 'execute_memory', 'create_time'
        ]


class UserSubmissionField(serializers.ListField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        submissions = value.order_by('-id')[:10]
        return _SubmissionSerializer(submissions, many=True).data


class AcceptedCountField(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        return value.filter(status=StatusChoices.ACCEPTED).count()


class UserDetailSerializer(serializers.ModelSerializer):
    solved_problems = ProblemSolveSerializer(source='problem_solve',
                                             many=True,
                                             read_only=True)
    submission_count = serializers.IntegerField(read_only=True,
                                                source='submissions.count')
    accepted_count = AcceptedCountField(source='submissions')
    submissions = UserSubmissionField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'real_name', 'student_id', 'is_staff',
            'solved_problems', 'submission_count', 'accepted_count',
            'submissions', 'avatar'
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
