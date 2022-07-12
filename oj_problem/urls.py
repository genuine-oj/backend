from rest_framework.routers import SimpleRouter
from django.urls import path, include

from .views import ProblemViewSet, DataViewSet, TagsViewSet

router = SimpleRouter()
router.register('', ProblemViewSet, basename='problem')
router.register('data', DataViewSet)
router.register('tag', TagsViewSet)

urlpatterns = [
    path('', include(router.urls))
]
