from django.urls import re_path

from .consumers import SubmissionConsumer

websocket_urlpatterns = [
    re_path(r'ws/submission/(?P<submission_id>\w+)/', SubmissionConsumer.as_asgi()),
]
