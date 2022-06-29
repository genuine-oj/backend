from rest_framework.authentication import SessionAuthentication


class SessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
