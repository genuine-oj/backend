from uuid import uuid1
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from oj_user.models import User


def get_default_sample():
    return {'input': '', 'output': ''}


class Problem(models.Model):
    title = models.CharField(_('title'), max_length=50)
    description = models.TextField(_('description'))
    input_format = models.TextField(_('input format'), max_length=200, blank=True, default='')
    output_format = models.TextField(_('output format'), max_length=200, blank=True, default='')
    sample_1 = models.JSONField(_('sample 1'), default=get_default_sample)
    sample_2 = models.JSONField(_('sample 2'), default=get_default_sample)
    sample_3 = models.JSONField(_('sample 3'), default=get_default_sample)
    hint = models.TextField(_('hint'), max_length=400, blank=True, default='')
    difficulty = models.IntegerField(_('difficulty'), default=0, help_text=_('level: 0 to 7, 0 for unset'))
    tags = TaggableManager(blank=True)
    time_limit = models.IntegerField(_('time limit (ms)'), default=1000)  # ms
    memory_limit = models.IntegerField(_('memory limit (MB)'), default=128)  # MB
    is_hidden = models.BooleanField(_('hide'), default=False)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)
    update_time = models.DateTimeField(_('update time'), auto_now=True)

    class Meta:
        verbose_name = _('problem')
        verbose_name_plural = _('problems')

    def __str__(self):
        return self.title


class ProblemSolve(models.Model):
    problem = models.ForeignKey(
        Problem,
        verbose_name=_('problem'),
        related_name='problem_solve',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        related_name='problem_solve',
        on_delete=models.CASCADE
    )
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)

    class Meta:
        verbose_name = _('problem solve data')
        verbose_name_plural = _('problem solve data')


class SpjModeChoices(models.TextChoices):
    NULL = 'NULL', _('NULL')
    TRADITIONAL = 'traditional', _('Traditional (CXX)')
    SIMPLE = 'simple', _('Simple (Python3)')


class TestCase(models.Model):
    problem = models.OneToOneField(
        Problem,
        verbose_name=_('problem'),
        related_name='test_case',
        on_delete=models.CASCADE
    )
    test_case_id = models.UUIDField(_('test case id'), default=uuid1)
    test_case_config = models.JSONField(_('test case config'), blank=True, default=list)
    spj_id = models.UUIDField(_('spj id'), default=uuid1)
    spj_mode = models.CharField(
        _('spj mode'),
        max_length=20,
        choices=SpjModeChoices.choices,
        blank=True,
        default=SpjModeChoices.NULL
    )
    subcheck_config = models.JSONField(_('subcheck config'), blank=True, default=dict)
    use_spj = models.BooleanField(_('spj'), default=False)
    use_subcheck = models.BooleanField(_('subcheck'), default=False)

    class Meta:
        verbose_name = _('testcase')
        verbose_name_plural = _('testcases')
