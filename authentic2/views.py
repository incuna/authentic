from django.shortcuts import render_to_response
import logging

def redirect(request, next, template_name='redirect.html'):
    '''Show a simple page which does a javascript redirect, closing any popup
       enclosing us'''
    logging.info('Redirect to %r' % next)
    return render_to_response(template_name, { 'next': next })
