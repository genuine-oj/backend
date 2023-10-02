from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import User
from oj_contest.models import Contest
from oj_problem.serializers import (ProblemBriefSerializer,
                                    ProblemSolveSerializer)
from oj_submission.models import StatusChoices, Submission


class UserBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'avatar']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'real_name', 'student_id', 'avatar',
            'permissions'
        ]
        read_only_fields = ['id', 'username']


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
        user = self.context['request'].user
        if not value.exists():
            return []
        elif 'submission' not in user.permissions and not value.first(
        ).user == user:
            processing_contest = Contest.objects.filter(
                start_time__lt=timezone.now(), end_time__gt=timezone.now())
            value = value.exclude(
                Q(_is_hidden=True) | Q(problem___is_hidden=True)
                | Q(problem__hide_submissions=True)
                | Q(problem__contests__contest__in=processing_contest)
            ).distinct()
        return _SubmissionSerializer(value.order_by('-id')[:10],
                                     many=True).data


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
            'id', 'username', 'email', 'real_name', 'student_id',
            'permissions', 'avatar', 'solved_problems', 'submission_count',
            'accepted_count', 'submissions'
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
