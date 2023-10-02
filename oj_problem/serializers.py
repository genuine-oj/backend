from rest_framework import serializers

from .models import Problem, TestCase, Tags, ProblemSolve


class SampleSerializer(serializers.Field):

    def to_representation(self, value):
        samples = [{
            'index': 1,
            **value.sample_1,
        }, {
            'index': 2,
            **value.sample_2,
        }, {
            'index': 3,
            **value.sample_3,
        }]
        return samples

    def to_internal_value(self, data):
        for i in range(3):
            if data[i].get('index') is not None:
                data[i].pop('index')
        formatted = {
            'sample_1': data[0],
            'sample_2': data[1],
            'sample_3': data[2],
        }
        return formatted


class TestCaseDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestCase
        fields = [
            'test_case_config', 'spj_source', 'spj_mode', 'subcheck_config',
            'use_spj', 'use_subcheck', 'allow_download'
        ]


class TestCaseUpdateSerializer(serializers.ModelSerializer):
    test_cases = serializers.FileField(allow_empty_file=True, required=False)
    spj_source = serializers.CharField(allow_blank=True)
    delete_cases = serializers.JSONField()

    class Meta:
        model = TestCase
        fields = [
            'test_cases', 'test_case_config', 'spj_source', 'spj_mode',
            'delete_cases', 'subcheck_config', 'use_spj', 'use_subcheck',
            'allow_download'
        ]


class ProblemSolved(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        request = self.context.get('request')
        return value.filter(user=request.user).exists()


class ProblemSerializer(serializers.ModelSerializer):
    solved = ProblemSolved(source='problem_solve')

    class Meta:
        model = Problem
        fields = [
            'id', 'title', 'difficulty', 'tags', 'solved', 'is_hidden',
            'submission_count', 'accepted_count'
        ]


class ProblemBriefSerializer(serializers.ModelSerializer):

    class Meta:
        model = Problem
        fields = ['id', 'title', 'difficulty']


class ProblemSolveSerializer(serializers.ModelSerializer):
    problem = ProblemBriefSerializer(read_only=True)

    class Meta:
        model = ProblemSolve
        fields = ['problem', 'create_time']


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ['id', 'name']


class TagsField(serializers.Field):

    def to_representation(self, value):
        return TagsSerializer(value, many=True).data

    def to_internal_value(self, data):
        return [Tags.objects.get(id=i) for i in data]


class AllowSubmit(serializers.ReadOnlyField):

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        return value


class ProblemDetailSerializer(serializers.ModelSerializer):
    samples = SampleSerializer(source='*')
    solved = ProblemSolved(source='problem_solve')
    tags = TagsField()
    allow_submit = serializers.BooleanField(read_only=True)
    hide_submissions = serializers.BooleanField(read_only=True)
    hide_discussions = serializers.BooleanField(read_only=True)

    class Meta:
        model = Problem
        exclude = ['sample_1', 'sample_2', 'sample_3']

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        problem = Problem.objects.create(**validated_data)
        problem.tags.set(tags)
        problem.save()
        TestCase.objects.create(problem=problem)
        return problem
