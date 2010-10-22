from django.dispatch import Signal

#user login
auth_login = Signal(providing_args = ["user","successful"])
auth_oidlogin = Signal(providing_args = ["openid_url","state"])

#user logout
auth_logout =  Signal(providing_args = ["user"])


