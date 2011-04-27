# vim: set ts=4 sw=4 : */

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('authentic2.idp.idp_openid.views',
    url(r'^$', 'openid_server', name='openid-provider-root'),
    url(r'^decide/$', 'openid_decide', name='openid-provider-decide'),
    url(r'^xrds/$', 'openid_xrds', name='openid-provider-xrds'),
    url(r'^(?P<id>.+)/xrds$', 'openid_xrds', {'identity': True},
        name='openid-provider-identity-xrds'),
    url(r'^(?P<id>.+)/?$', 'openid_discovery',
        name='openid-provider-identity'),
)
