from django.shortcuts import render_to_response
from django.template import RequestContext
import logging

def redirect(request, next, template_name='redirect.html'):
    '''Show a simple page which does a javascript redirect, closing any popup
       enclosing us'''
    logging.info('Redirect to %r' % next)
    return render_to_response(template_name, { 'next': next })

def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context: None
    """
    return render_to_response(template_name,
        context_instance = RequestContext(request)
    )
