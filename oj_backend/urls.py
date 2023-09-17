from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from oj_user.views import SiteSettingsView

urlpatterns = [
    path('problem/', include('oj_problem.urls')),
    path('submission/', include('oj_submission.urls')),
    path('contest/', include('oj_contest.urls')),
    path('discussion/', include('oj_discussion.urls')),
    path('user/', include('oj_user.urls')),
    path('site_settings/', SiteSettingsView.as_view()),
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
        permission_classes=(AllowAny, ),
    )
    urlpatterns += [
        path('swagger/',
             schema_view.with_ui('swagger', cache_timeout=0),
             name='swagger-ui')
    ]
