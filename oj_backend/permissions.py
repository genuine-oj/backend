from django.core.cache import cache
from requests import post
from rest_framework import exceptions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import SAFE_METHODS, BasePermission


class Granted(BasePermission):

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user and request.user.is_superuser:
            return True
        permission = getattr(view, 'permission', None)
        return permission in request.user.permissions


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