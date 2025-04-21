# travel_buddy/middleware.py
from django.http import HttpResponseForbidden
from django.urls import reverse

class SimpleAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_paths = []

    def __call__(self, request):
        username = request.session.get('username')
        if username:
            request.user = username
            request.is_admin = request.session.get('is_admin', False)
        else:
            request.session.flush()
            request.user = None
            request.is_admin = False

        if request.path in self.admin_paths and not request.is_admin:
            return HttpResponseForbidden('Forbidden')

        response = self.get_response(request)
        return response