from models import error
from models import info
from django.conf import settings

class LoggerMiddleware:
    
    def process_request(self, request):
        if (request.path.startswith(settings.ADMIN_MEDIA_PREFIX)) or (request.path == '/favicon.ico'):
            return
        else:
            msg = 'user ' + str(request.user) + ' path ' + str(request.path)
            info(msg)

    def process_exception(self, request, exception):
        if hasattr(exception,'value'):
            msg = 'user: ' + str(request.user) + ' exception ' + str(type(exception)) + ' value: ' + str(exception.value)
            error(msg)
        else:
            msg = 'user: ' + str(request.user) + ' exception: ' + str(type(exception))
            error(msg)
