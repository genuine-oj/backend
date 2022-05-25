from rest_framework.routers import SimpleRouter
from .views import ProblemViewSet

router = SimpleRouter()
router.register('', ProblemViewSet, basename='problem')

urlpatterns = router.urls
