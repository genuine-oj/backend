from django.core.cache import cache
from requests import post
from rest_framework import exceptions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import SAFE_METHODS, BasePermission


class Granted(BasePermission):
    perms_map = {
        'GET': None,
        'OPTIONS': None,
        'HEAD': None,
        'POST': '%(app_label)s.add_%(model_name)s',
        'PUT': '%(app_label)s.change_%(model_name)s',
        'PATCH': '%(app_label)s.change_%(model_name)s',
        'DELETE': '%(app_label)s.delete_%(model_name)s',
    }

    def get_required_permission(self, method, model_cls):
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }
        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        permission = self.perms_map[method]
        if permission is None:
            return None
        return permission % kwargs

    def _queryset(self, view):
        assert hasattr(view, 'get_queryset') \
               or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, (
                '{}.get_queryset() returned None'.format(
                    view.__class__.__name__))
            return queryset
        return view.queryset

    def has_permission(self, request, view):
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not (request.user and request.user.is_authenticated):
            return False
        if request.user and request.user.is_superuser:
            return True

        queryset = self._queryset(view)
        perm = self.get_required_permission(request.method, queryset.model)
        return request.user.has_perm(perm)


class IsAuthenticatedAndReadOnly(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.method in SAFE_METHODS)


class IsAuthenticatedAndReadCreate(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and (request.method in SAFE_METHODS or request.method == 'POST'))


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS)


class Captcha(BasePermission):

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True

        settings = cache.get('site_settings').get('captcha', {})
        if settings.get('enableb') is not True:
            return True
        elif view.scene not in settings.get('scenes', []):
            return True

        token = request.data.get('captcha')
        if not token:
            raise AuthenticationFailed({
                'status': 'error',
                'detail': '未找到人机验证信息'
            })

        captcha_type = settings.get('type', 'recaptcha-v3')
        backend_url = settings.get('backendUrl', None)
        if captcha_type == 'recaptcha-v3':
            secret = settings.get('serverKey')
            r = post(
                backend_url
                or 'https://recaptcha.google.cn/recaptcha/api/siteverify', {
                    'response': token,
                    'ip': request.META.get('REMOTE_ADDR'),
                    'secret': secret,
                }).json()
            if not r['success']:
                raise AuthenticationFailed({
                    'status': 'error',
                    'detail': '人机验证出错, 请重试'
                })
            elif r['score'] < 0.6:
                raise AuthenticationFailed({
                    'status': 'error',
                    'detail': '您未能通过人机验证！'
                })
            return True
        elif captcha_type == 'hcaptcha':
            r = post(backend_url or 'https://captcha.qdzx.icu/check', {
                'request_id': token,
            }).json()
            if r['status'] != 'success':
                raise AuthenticationFailed({
                    'status': 'error',
                    'detail': '您未能通过人机验证！'
                })
            return True
        return False