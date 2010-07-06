from registration.signals import user_registered
from django.contrib.auth.models import User

def create_openid(sender, user, **kwargs):
        user.openid_set.create(openid = user.username, default = True)

        user_registered.connect(create_openid, dispatch_uid="authentic.openid_provider")
