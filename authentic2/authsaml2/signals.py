from django.dispatch import Signal

#user login
auth_login = Signal(providing_args = ["user","successful"])

#user logout
auth_logout =  Signal(providing_args = ["user"])


