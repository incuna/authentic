from registration.signals import user_registered
from django.contrib.auth.models import User
from signals import create_openid

user_registered.connect(create_openid, dispatch_uid="authentic.openid_provider")

