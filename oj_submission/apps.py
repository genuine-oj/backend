from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubmissionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oj_submission'
    verbose_name = _('Submission and Judgement')
