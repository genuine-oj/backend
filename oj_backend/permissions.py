from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import exceptions


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
