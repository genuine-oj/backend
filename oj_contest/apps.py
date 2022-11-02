from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oj_contest'
    verbose_name = _('Contest')
