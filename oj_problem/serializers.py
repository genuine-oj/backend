from rest_framework import serializers

from .models import Problem, TestCase


class SampleSerializer(serializers.Field):
    def to_representation(self, value):
        samples = [
            {'index': 1, **value.sample_1},
            {'index': 2, **value.sample_2},
            {'index': 3, **value.sample_3}
        ]
        return samples

    def to_internal_value(self, data):
        for i in range(3):
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
        fields = ['test_case_config', 'spj_mode', 'subcheck_config', 'use_spj', 'use_subcheck']


class TestCaseUpdateSerializer(serializers.ModelSerializer):
    test_cases = serializers.FileField(allow_empty_file=True)
    spj_source = serializers.CharField(allow_null=True)
    delete_cases = serializers.JSONField()

    class Meta:
        model = TestCase
        fields = ['test_cases', 'test_case_config', 'spj_source', 'spj_mode',
                  'delete_cases', 'subcheck_config', 'use_spj', 'use_subcheck']


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'title']


class ProblemDetailSerializer(serializers.ModelSerializer):
    samples = SampleSerializer(source='*')

    class Meta:
        model = Problem
        exclude = ['sample_1', 'sample_2', 'sample_3']

    def create(self, validated_data):
        problem = Problem.objects.create(**validated_data)
        TestCase.objects.create(problem=problem)
        return problem
