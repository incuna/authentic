from django.views.decorators.csrf import csrf_exempt
from openid_provider.views import openid_decide as origin_openid_decide
from openid_provider.views import openid_server as origin_openid_server
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.views.generic.simple import redirect_to
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
import re
from openid_provider.views import get_base_uri
import settings

@csrf_exempt
def openid_server(req):
        return origin_openid_server(req)

@csrf_exempt
def openid_decide(req):
        return origin_openid_decide(req)
