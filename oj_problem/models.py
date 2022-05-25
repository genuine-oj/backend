from uuid import uuid1

from django.db import models


def get_default_sample():
    return {'input': '', 'output': ''}


class Problem(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    input_format = models.TextField(max_length=200, blank=True, default='')
    output_format = models.TextField(max_length=200, blank=True, default='')
    sample_1 = models.JSONField(default=get_default_sample)
    sample_2 = models.JSONField(default=get_default_sample)
    sample_3 = models.JSONField(default=get_default_sample)
    hint = models.TextField(max_length=400, blank=True, default='')
    time_limit = models.IntegerField(default=1000)  # ms
    memory_limit = models.IntegerField(default=128)  # MB
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    update_time = models.DateTimeField(auto_now=True, editable=False)
    is_hidden = models.BooleanField(default=False)


class SpjModeChoices(models.TextChoices):
    NULL = 'NULL', 'NULL'
    TRADITIONAL = 'traditional', 'Traditional (CXX)'
    SIMPLE = 'simple', 'Simple (Python3)'


class TestCase(models.Model):
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name='test_case')
    test_case_id = models.UUIDField(default=uuid1, editable=False)
    test_case_config = models.JSONField(blank=True, default=list)
    '''
        [{ name: '', score: 20 (total: 100)}, ...]
    '''
    spj_id = models.UUIDField(default=uuid1, editable=False)
    spj_mode = models.CharField(max_length=20, choices=SpjModeChoices.choices, blank=True, default=SpjModeChoices.NULL)
    subcheck_config = models.JSONField(blank=True, default=dict)
    use_spj = models.BooleanField(default=False)
    use_subcheck = models.BooleanField(default=False)
