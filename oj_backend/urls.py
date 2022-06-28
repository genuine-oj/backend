from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

urlpatterns = [
    path('problem/', include('oj_problem.urls')),
    path('submission/', include('oj_submission.urls')),
    path('user/', include('oj_user.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title='OJ API',
            default_version='v1',
            license=openapi.License(name='GPLv3 License'),
        ),
        public=True,
        permission_classes=(AllowAny,),
    )
    urlpatterns += [path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui')]
