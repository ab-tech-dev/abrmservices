
class ActiveUserMiddleware:
    """
    Middleware to track and update the last_active timestamp
    for logged-in users.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user.update_last_active()
        return self.get_response(request)
