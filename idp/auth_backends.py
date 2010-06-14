import django.contrib.auth
from django.contrib.auth.models import User
from signals import auth_login
from django.core.exceptions import FieldError

class LogginBackend:
    def authenticate(self, username = None, password = None):
        try:
            user = User.objects.get(username = username)
            if user.check_password(password):
                auth_login.send(sender = self, user = user, successful = True)
                return user
        except:
            auth_login.send(sender = self, user = username, successful = False)
            return None

    def get_user(self, user_uid):
        try:
            return User.objects.get(pk = user_uid)
        except:
            return None
