from django.utils.timezone import now
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class UpdateLastActiveMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            request.user.update_last_active()
