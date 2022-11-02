from rest_framework.routers import SimpleRouter
from django.urls import path, include

from .views import ContestViewSet

router = SimpleRouter()
router.register('', ContestViewSet, basename='contest')

urlpatterns = [path('', include(router.urls))]
