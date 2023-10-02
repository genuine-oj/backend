from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from oj_problem.models import Problem
from oj_problem.serializers import ProblemBriefSerializer
from oj_problem.views import get_problem_queryset
from oj_user.serializers import UserBriefSerializer
from rest_framework import serializers

from .models import Submission
from .tasks import judge


class SubmissionSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer()
    problem = ProblemBriefSerializer()

    class Meta:
        model = Submission
        fields = read_only_fields = [
            'id', 'user', 'problem', 'language', 'status', 'score',
            'execute_time', 'execute_memory', 'create_time', 'is_hidden'
        ]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(default=serializers.CurrentUserDefault())
    problem = ProblemBriefSerializer(read_only=True)
    problem_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        problem_id = validated_data.pop('problem_id')
        problem = Problem.objects.get(id=problem_id)
        if not any([
                'problem' in user.permissions
                and bool(len(problem.test_case.test_case_config)),
                get_problem_queryset(self.context['request']).filter(
                    id=problem_id).exists() and problem.allow_submit
        ]):
            raise serializers.ValidationError(
                _('Problem submit is not allowed'))
        validated_data['problem'] = problem
        submission = Submission.objects.create(**validated_data)
        judge.delay(
            submission.id, submission.problem.test_case.test_case_id,
            submission.problem.test_case.spj_id
            if submission.problem.test_case.use_spj else None,
            submission.problem.test_case.test_case_config,
            submission.problem.test_case.subcheck_config
            if submission.problem.test_case.use_subcheck else None,
            submission.language, submission.source, {
                'max_cpu_time': submission.problem.time_limit,
                'max_memory': submission.problem.memory_limit * 1024 * 1024,
            })
        problem.submission_count += 1
        problem.save(update_fields=['submission_count'])
        return submission

    class Meta:
        model = Submission
        fields = [
            'id', 'user', 'problem', 'problem_id', 'source', 'language',
            'status', 'score', 'execute_time', 'execute_memory', 'detail',
            'log', 'create_time', 'allow_download', 'is_hidden', '_is_hidden'
        ]
        read_only_fields = [
            'status', 'score', 'execute_time', 'execute_memory', 'detail',
            'log', 'create_time', 'allow_download', 'is_hidden', '_is_hidden'
        ]
