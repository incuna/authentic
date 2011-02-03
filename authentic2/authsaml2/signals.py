from django.dispatch import Signal

#authz_decision
authz_decision = Signal(providing_args = ["request","attributes","provider"])

#user login
auth_login = Signal(providing_args = ["request","attributes"])

#user logout
auth_logout =  Signal(providing_args = ["user"])
