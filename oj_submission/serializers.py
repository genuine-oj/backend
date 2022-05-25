from rest_framework import serializers
import sys

from .models import Submission
from .tasks import judge
from oj_problem.models import Problem
from oj_user.serializers import UserSerializer
from oj_problem.serializers import ProblemSerializer


class SizeField(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        return sys.getsizeof(str(value))


class SubmissionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    problem = ProblemSerializer()
    source_size = SizeField(source='source')

    class Meta:
        model = Submission
        fields = ['id', 'user', 'problem', 'language', 'source_size', 'status', 'score',
                  'execute_time', 'execute_memory', 'create_time']
        read_only_fields = ['source_size', 'status', 'score', 'execute_time', 'execute_memory', 'create_time']


class SubmissionDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(default=serializers.CurrentUserDefault())
    problem = ProblemSerializer(read_only=True)
    problem_id = serializers.IntegerField(required=False)

    def create(self, validated_data):
        problem_id = validated_data.pop('problem_id')
        validated_data['problem'] = Problem.objects.get(id=problem_id)
        submission = Submission.objects.create(**validated_data)
        judge.delay(submission.id, submission.problem.test_case.test_case_id,
                    submission.problem.test_case.test_case_config, submission.language,
                    submission.source, {
                        'max_cpu_time': submission.problem.time_limit,
                        'max_memory': submission.problem.memory_limit * 1024 * 1024
                    })
        return submission

    class Meta:
        model = Submission
        fields = ['id', 'user', 'problem', 'problem_id', 'source', 'language', 'status', 'score',
                  'execute_time', 'execute_memory', 'detail', 'log', 'create_time']
        read_only_fields = ['status', 'score', 'execute_time', 'execute_memory', 'detail', 'log', 'create_time']
