from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProblemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oj_problem'
    verbose_name = _('Problem')
