from django.db import models
from django.utils import timezone
from oj_contest.models import Contest
from oj_problem.models import Problem
from oj_user.models import User


class Discussion(models.Model):
    title = models.CharField(max_length=200)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User,
                               related_name='discussions',
                               on_delete=models.CASCADE)

    related_problem = models.ForeignKey(Problem,
                                        related_name='discussions',
                                        on_delete=models.SET_NULL,
                                        null=True)
    related_contest = models.ForeignKey(Contest,
                                        related_name='discussions',
                                        on_delete=models.SET_NULL,
                                        null=True)

    @property
    def is_hidden(self):
        return any([
            self.related_problem and self.related_problem.hide_discussions,
            self.related_contest and self.related_contest.hide_discussions,
        ])

    def __str__(self):
        return self.title


class Reply(models.Model):
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    discussion = models.ForeignKey(Discussion,
                                   related_name='replies',
                                   on_delete=models.CASCADE)
    reply_to = models.ForeignKey('self',
                                 related_name='replies',
                                 on_delete=models.SET_NULL,
                                 null=True)

    def __str__(self):
        return self.content[:20] + '...'
