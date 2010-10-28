import logging

from django.dispatch import Signal
from django.conf import settings


auth_oidlogin = Signal(providing_args = ["openid_url","state"])

def LogAuthLoginOI(sender, openid_url, state, **kwargs):
    msg = str(openid_url)
    if state is 'success':
        msg += ' has login with success with OpenID'
    elif state is 'invalid':
        msg += ' is invalid'
    elif state is 'not_supported':
        msg += ' did not support i-names'
    elif state is 'cancel':
        msg += ' has cancel'
    elif state is 'failure':
        msg += ' has failed'
    elif state is 'setup_needed':
        msg += ' setup_needed'
    logging.info(msg)

auth_oidlogin.connect(LogAuthLoginOI, dispatch_uid ="authentic2.idp")

def LogRegisteredOI(sender, openid, **kwargs):
    msg = openid 
    msg = str(msg) + ' is now registered'
    logging.info(msg)

def LogAssociatedOI(sender, user, openid, **kwargs):
    msg = user.username + ' has associated his user with ' + openid
    logging.info(msg)

if settings.AUTH_OPENID:
    from django_authopenid.signals import oid_register
    from django_authopenid.signals import oid_associate
    oid_register.connect(LogRegisteredOI, dispatch_uid = "authentic2.idp")
    oid_associate.connect(LogAssociatedOI, dispatch_uid = "authentic2.idp")
