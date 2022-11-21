from rest_framework import serializers
import sys

from .models import Submission
from .tasks import judge
from oj_problem.models import Problem
from oj_user.serializers import UserBriefSerializer
from oj_problem.serializers import ProblemBriefSerializer


class SizeField(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        return sys.getsizeof(str(value))


class SubmissionSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer()
    problem = ProblemBriefSerializer()
    source_size = SizeField(source='source')

    class Meta:
        model = Submission
        fields = read_only_fields = [
            'id', 'user', 'problem', 'language', 'source_size', 'status',
            'score', 'execute_time', 'execute_memory', 'create_time',
            'is_hidden'
        ]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(default=serializers.CurrentUserDefault())
    problem = ProblemBriefSerializer(read_only=True)
    problem_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        problem_id = validated_data.pop('problem_id')
        problem = Problem.objects.get(id=problem_id)
        if not problem.allow_submit:
            raise serializers.ValidationError('Problem not allow submit')
        validated_data['problem'] = problem
        submission = Submission.objects.create(**validated_data)
        judge.delay(
            submission.id, submission.problem.test_case.test_case_id,
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
            'log', 'create_time', 'allow_download', 'is_hidden'
        ]
        read_only_fields = [
            'status', 'score', 'execute_time', 'execute_memory', 'detail',
            'log', 'create_time', 'allow_download'
        ]
