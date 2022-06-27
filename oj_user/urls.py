from django.urls import path
from .views import LoginView, LogoutView, InfoAPIView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('info/', InfoAPIView.as_view(), name='info')
]
