from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import InfoAPIView, LoginView, LogoutView, UserViewSet

router = SimpleRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('info/', InfoAPIView.as_view(), name='info')
]
