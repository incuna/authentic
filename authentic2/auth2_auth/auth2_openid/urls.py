from django.conf.urls.defaults import *
import django_authopenid.views

import authentic2.auth2_auth.auth2_openid.views as v

urlpatterns = patterns('',
    (r'^complete/associate/$', v.complete_associate,{}, 'user_complete_myassociate'),
    (r'^signin/complete/signin/', v.complete_signin,{} ,'user_complete_signin'),
    (r'^dissociate/$', v.dissociate,{} ,'user-dissociate'),#
    (r'^associate/$', v.associate,{} ,'user-associate'),#
    (r'^password/change/$', django_authopenid.views.password_change, {}, 'authopenid_password_change'),
    (r'^signin/complete/', include ('django_authopenid.urls')),
    (r'^signin/', v.signin,{} ,'user_signin'),
)
