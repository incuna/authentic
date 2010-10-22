import traceback

from django.conf import settings

class DebugMiddleware:
    def process_exception(self, request, exception):
        if getattr(settings, 'DEBUG', False):
            traceback.print_exc()
