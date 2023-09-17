from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from oj_problem.models import Problem
from oj_user.models import User


class LanguageChoices(models.TextChoices):
    C = 'c', 'C'
    CPP = 'cpp', 'C++'
    PYTHON3 = 'python3', 'Python 3'


class StatusChoices(models.IntegerChoices):
    PENDING = -4, _('pending')
    JUDGING = -3, _('judging')
    COMPILE_ERROR = -2, _('compile error')
    WRONG_ANSWER = -1, _('wrong answer')
    ACCEPTED = 0, _('accepted')
    TIME_LIMIT_EXCEEDED = 1, _('time limit exceeded')
    MEMORY_LIMIT_EXCEEDED = 2, _('memory limit exceeded')
    RUNTIME_ERROR = 3, _('runtime error')
    SYSTEM_ERROR = 4, _('system error')


class Submission(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        related_name='submissions',
        on_delete=models.CASCADE,
    )
    problem = models.ForeignKey(
        Problem,
        verbose_name=_('problem'),
        related_name='submissions',
        on_delete=models.CASCADE,
    )
    source = models.TextField(_('source code'), max_length=102400)
    language = models.CharField(
        _('language'),
        max_length=10,
        choices=LanguageChoices.choices,
    )
    status = models.IntegerField(
        _('status'),
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    score = models.IntegerField(_('score'), default=0)
    execute_time = models.IntegerField(_('execute time'), default=0)
    execute_memory = models.IntegerField(_('execute memory'), default=0)
    detail = models.JSONField(_('execute detail'), default=list)
    log = models.TextField(
        _('execute log'),
        max_length=400,
        default='',
        blank=True,
    )
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)
    _is_hidden = models.BooleanField(_('hidden'), default=False)
    allow_download = models.BooleanField(_('allow download'), default=True)

    @property
    def is_hidden(self):
        return any([
            self._is_hidden,
            self.problem.hide_submissions,
        ])

    class Meta:
        verbose_name = _('submission')
        verbose_name_plural = _('submissions')
