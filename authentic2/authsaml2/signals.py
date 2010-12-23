from django.dispatch import Signal

#user login
auth_login = Signal(providing_args = ["request","attributes"])

#user logout
auth_logout =  Signal(providing_args = ["request"])


