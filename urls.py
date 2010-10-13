from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
import authentic.idp.views
import authentic.idp.login_views
import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/admin_log_view/log/', 'admin_log_view.views.admin_view'),
    (r'^admin/', include(admin.site.urls)),
    (r'^idp/', include('authentic.idp.urls')),
    (r'^$', login_required(authentic.idp.views.homepage), {}, 'index'),
)

if settings.IDP_OPENID:
    import authentic.django_openid_provider.views
    import openid_provider.views
    urlpatterns += patterns('',
            (r'^openid/$',authentic.django_openid_provider.views.openid_server, {},'openid-provider-root'),
            (r'^openid/decide/$',authentic.django_openid_provider.views.openid_decide, {},'openid-provider-decide'),
            (r'^openid/manage/',authentic.django_openid_provider.views.manage_trustroot, {},'manage_trustroot'),
            (r'^openid/manageid/',authentic.django_openid_provider.views.manage_id, {},'manage_id' ),
            (r'^openid/manageid_confirm/',authentic.django_openid_provider.views.manage_id_confirm, {}, 'manage_id_confirm'),
            (r'^openid/addopenid/',authentic.django_openid_provider.views.addopenid, {}, 'add_openid'),
            (r'^openid/',include('openid_provider.urls')),
            url(r'^(?P<id>[a-zA-Z0-9,_,]*/?)/$', openid_provider.views.openid_xrds, {'identity': True}, name='openid-provider-identity'),
    )

if settings.AUTH_OPENID:
    import django_authopenid
    urlpatterns += patterns('',
            (r'^accounts/openid/complete/associate/$', authentic.idp.views.complete_associate,{}, 'user_complete_myassociate'),
            (r'^accounts/openid/$', 'django.views.generic.simple.redirect_to', {'url': '..'}),
            (r'^accounts/openid/signin/complete/signin/', authentic.idp.views.complete_signin,{} ,'user_complete_signin'),
            (r'^accounts/openid/dissociate/$', authentic.idp.views.dissociate,{} ,'user-dissociate'),#
            (r'^accounts/openid/associate/$', authentic.idp.views.associate,{} ,'user-associate'),#
            (r'^accounts/openid/password/change/$', django_authopenid.views.password_change, {}, 'authopenid_password_change'),
            (r'^accounts/openid/signin/complete/', include ('django_authopenid.urls')),
            (r'^accounts/openid/signin/',authentic.idp.views.signin,{} ,'user_signin'),
    )

urlpatterns += patterns('',
    (r'^accounts/logout/', 'idp.views.logout'),
    (r'^accounts/$', 'django.views.generic.simple.redirect_to', {'url': '..'}),
    (r'^accounts/password/change/$','idp.views.password_change'),
    url(r'^accounts/login', authentic.idp.login_views.login, name='auth_login'),
    (r'^accounts/', include('registration.urls')),
)

urlpatterns += patterns('',
    (r'^authsaml2/', include('authentic.authsaml2.urls')),
)

if settings.AUTH_SSL:
    urlpatterns += patterns('',
        url(r'^sslauth/$',
            'authentic.sslauth.login_ssl.process_request',
            name='user_signin_ssl'),
        url(r'^error_ssl/$', direct_to_template,
            {'template': 'error_ssl.html'}, 'error_ssl'),
    )

if settings.STATIC_SERVE:
    urlpatterns += patterns('',
        url(
            regex = r'^media/(?P<path>.*)$',
            view = 'django.views.static.serve',
            kwargs = {'document_root': settings.MEDIA_ROOT}),
    )

