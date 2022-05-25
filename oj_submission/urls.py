from rest_framework.routers import SimpleRouter
from .views import SubmissionViewSet

router = SimpleRouter()
router.register('', SubmissionViewSet, basename='submission')

urlpatterns = router.urls
