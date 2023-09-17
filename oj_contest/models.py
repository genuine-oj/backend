from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from oj_user.models import User
from oj_problem.models import Problem


class Contest(models.Model):
    title = models.CharField(_('title'), max_length=50)
    description = models.TextField(_('description'), null=True, blank=True)
    problem_list_mode = models.BooleanField(_('problem list mode'),
                                            default=False)
    start_time = models.DateTimeField(_('start time'), null=True, blank=True)
    end_time = models.DateTimeField(_('end time'), null=True, blank=True)
    is_hidden = models.BooleanField(_('hide'), default=False)
    allow_sign_up = models.BooleanField(_('allow sign up'), default=True)

    problems = models.ManyToManyField(Problem, through='ContestProblem')
    users = models.ManyToManyField(User, through='ContestUser')

    @property
    def hide_discussions(self):
        return any([
            self.is_hidden,
            self.start_time < timezone.now()
            and self.end_time > timezone.now(),
        ])

    class Meta:
        verbose_name = _('contest')
        verbose_name_plural = _('contests')

    def __str__(self):
        return self.title


class ContestProblem(models.Model):
    contest = models.ForeignKey(
        Contest,
        verbose_name=_('contest'),
        on_delete=models.CASCADE,
    )
    problem = models.ForeignKey(
        Problem,
        verbose_name=_('problem'),
        related_name='contests',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _('contest problem')
        verbose_name_plural = _('contest problems')

    def __str__(self):
        return f'{self.contest.title} - {self.problem.title}'


class ContestUser(models.Model):
    contest = models.ForeignKey(
        Contest,
        verbose_name=_('contest'),
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name=_('user'),
        related_name='contests',
        on_delete=models.CASCADE,
    )
    is_admin = models.BooleanField(_('is admin'), default=False)

    class Meta:
        verbose_name = _('contest user')
        verbose_name_plural = _('contest users')

    def __str__(self):
        return f'{self.contest.title} - {self.user.username}'
