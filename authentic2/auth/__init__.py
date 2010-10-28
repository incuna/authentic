from django.dispatch import Signal

auth_login = Signal(providing_args = ["user","successful"])
auth_logout =  Signal(providing_args = ["user"])

def LogAuthLogin(sender, user, successful, **kwargs):
    if successful:
        msg = user.username + ' has logged in with success'
    else:    
        msg = user + ' has tried to login without success'
    info(msg)

def LogAuthLogout(sender, user, **kwargs):
    msg = str(user) 
    msg += ' has logged out'
    info(msg)

auth_login.connect(LogAuthLogin, dispatch_uid = "authentic2.idp")
auth_logout.connect(LogAuthLogout, dispatch_uid = "authentic2.idp")
