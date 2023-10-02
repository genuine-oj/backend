from uuid import uuid1

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from oj_user.models import User


def get_default_sample():
    return {'input': '', 'output': ''}


class Problem(models.Model):
    title = models.CharField(_('title'), max_length=50)
    background = models.TextField(_('background'), blank=True, default='')
    description = models.TextField(_('description'), blank=True, default='')
    input_format = models.TextField(_('input format'), blank=True, default='')
    output_format = models.TextField(_('output format'),
                                     blank=True,
                                     default='')
    sample_1 = models.JSONField(_('sample 1'), default=get_default_sample)
    sample_2 = models.JSONField(_('sample 2'), default=get_default_sample)
    sample_3 = models.JSONField(_('sample 3'), default=get_default_sample)
    hint = models.TextField(_('hint'), blank=True, default='')
    tags = models.ManyToManyField('Tags',
                                  verbose_name=_('tags'),
                                  related_name='problems',
                                  blank=True)
    difficulty = models.IntegerField(_('difficulty'),
                                     default=0,
                                     help_text=_('level: 0 to 7, 0 for unset'))
    time_limit = models.IntegerField(_('time limit (ms)'), default=1000)  # ms
    memory_limit = models.IntegerField(_('memory limit (MB)'),
                                       default=128)  # MB
    _is_hidden = models.BooleanField(_('hide'), default=False)
    _hide_submissions = models.BooleanField(_('hide submissions'),
                                            default=False)
    _hide_discussions = models.BooleanField(_('hide discussions'),
                                            default=False)
    _allow_submit = models.BooleanField(_('allow submit'), default=True)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)
    update_time = models.DateTimeField(_('update time'), auto_now=True)
    submission_count = models.IntegerField(_('submission count'), default=0)
    accepted_count = models.IntegerField(_('solved count'), default=0)
    files = models.JSONField(_('problem files'), default=list)

    @property
    def is_hidden(self):
        return any([
            self._is_hidden,
        ])

    @property
    def hide_submissions(self):
        return any([
            self.is_hidden,
            self._hide_submissions,
            self.contests.filter(
                contest__start_time__lt=timezone.now(),
                contest__end_time__gt=timezone.now(),
            ).exists(),
        ])

    @property
    def hide_discussions(self):
        return any([
            self.is_hidden,
            self._hide_discussions,
            self.contests.filter(
                contest__start_time__lt=timezone.now(),
                contest__end_time__gt=timezone.now(),
            ).exists(),
        ])

    @property
    def allow_submit(self):
        return all([
            self._allow_submit,
            bool(len(self.test_case.test_case_config)),
        ])

    class Meta:
        verbose_name = _('problem')
        verbose_name_plural = _('problems')

    def __str__(self):
        return self.title


class ProblemSolve(models.Model):
    problem = models.ForeignKey(Problem,
                                verbose_name=_('problem'),
                                related_name='problem_solve',
                                on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             verbose_name=_('user'),
                             related_name='problem_solve',
                             on_delete=models.CASCADE)
    create_time = models.DateTimeField(_('create time'), auto_now_add=True)

    class Meta:
        verbose_name = _('problem solve data')
        verbose_name_plural = _('problem solve data')


class SpjModeChoices(models.TextChoices):
    NULL = 'NULL', _('NULL')
    TRADITIONAL = 'traditional', _('Traditional (CXX)')
    SIMPLE = 'simple', _('Simple (Python3)')


class TestCase(models.Model):
    problem = models.OneToOneField(Problem,
                                   verbose_name=_('problem'),
                                   related_name='test_case',
                                   on_delete=models.CASCADE)
    test_case_id = models.UUIDField(_('test case id'), default=uuid1)
    test_case_config = models.JSONField(_('test case config'),
                                        blank=True,
                                        default=list)
    use_spj = models.BooleanField(_('spj'), default=False)
    spj_id = models.UUIDField(_('spj id'), default=uuid1)
    spj_mode = models.CharField(_('spj mode'),
                                max_length=20,
                                choices=SpjModeChoices.choices,
                                blank=True,
                                default=SpjModeChoices.NULL)
    spj_source = models.TextField(_('spj_source'), blank=True, default='')
    subcheck_config = models.JSONField(_('subcheck config'),
                                       blank=True,
                                       default=list)
    use_subcheck = models.BooleanField(_('subcheck'), default=False)
    allow_download = models.BooleanField(_('allow download case data'),
                                         default=True)

    class Meta:
        verbose_name = _('testcase')
        verbose_name_plural = _('testcases')


class Tags(models.Model):
    name = models.CharField(_('tag name'), max_length=50, unique=True)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name
