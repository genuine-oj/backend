from django.db import models
from django.apps import apps
from django.contrib.auth.models import BaseUserManager, UnicodeUsernameValidator, AbstractBaseUser, PermissionsMixin, \
    Group as BaseGroup
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        global_user_model = apps.get_model(self.model._meta.app_label,
                                           self.model._meta.object_name)
        username = global_user_model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self,
                         username,
                         email=None,
                         password=None,
                         **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    real_name = models.CharField(_('real name'), max_length=20, blank=True)
    student_id = models.CharField(_('student id'), max_length=40, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    avatar = models.URLField(_('avatar'), blank=True, null=True, default=None)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    permissions = models.JSONField(_('permissions'), default=list)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Group(BaseGroup):

    class Meta:
        proxy = True
        verbose_name = _('group')
        verbose_name_plural = _('groups')
