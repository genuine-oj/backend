from django.db import models

from oj_problem.models import Problem
from oj_user.models import User


class LanguageChoices(models.TextChoices):
    C = 'c', 'C'
    CPP = 'cpp', 'C++'


class StatusChoices(models.IntegerChoices):
    PENDING = -4, 'Pending'
    JUDGING = -3, 'Judging'
    COMPILE_ERROR = -2, 'Compile Error'
    WRONG_ANSWER = -1, 'Wrong Answer'
    ACCEPTED = 0, 'Accepted'
    TIME_LIMIT_EXCEEDED = 1, 'Time Limit Exceeded'
    MEMORY_LIMIT_EXCEEDED = 2, 'Memory Limit Exceeded'
    RUNTIME_ERROR = 3, 'Runtime Error'
    SYSTEM_ERROR = 4, 'System Error'


class Submission(models.Model):
    user = models.ForeignKey(User, related_name='submissions', on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, related_name='submissions', on_delete=models.CASCADE)
    source = models.TextField()
    language = models.CharField(max_length=10, choices=LanguageChoices.choices)
    status = models.IntegerField(choices=StatusChoices.choices, default=StatusChoices.PENDING)
    score = models.IntegerField(default=0)
    execute_time = models.IntegerField(default=0)
    execute_memory = models.IntegerField(default=0)
    detail = models.JSONField(default=list)
    log = models.TextField(max_length=400, default='', blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
