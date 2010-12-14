from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
import views

urlpatterns = patterns('',
        (r'^new_totp_secret$', views.new_totp_secret),
        (r'^delete_totp_secret$', views.delete_totp_secret))
