from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import LoginAPIView

router = SimpleRouter()

urlpatterns = [
    path('login/', LoginAPIView.as_view())
]

urlpatterns += router.urls
