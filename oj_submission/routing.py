from django.urls import re_path

from .consumers import SubmissionConsumer

# Do not use path due to some issue, see: https://github.com/django/channels/issues/1428
websocket_urlpatterns = [
    re_path(r'ws/submission/(?P<submission_id>\w+)/', SubmissionConsumer.as_asgi()),
]
