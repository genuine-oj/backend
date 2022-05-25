from django.urls import path, include

urlpatterns = [
    path('problem/', include('oj_problem.urls')),
    path('submission/', include('oj_submission.urls')),
    path('user/', include('oj_user.urls')),
]
