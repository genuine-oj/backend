from rest_framework.routers import SimpleRouter
from django.urls import path, include

from .views import DiscussionViewSet

router = SimpleRouter()
router.register('', DiscussionViewSet, basename='discussion')

urlpatterns = [path('', include(router.urls))]
