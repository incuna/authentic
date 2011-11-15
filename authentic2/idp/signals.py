from django.dispatch import Signal

from authentic2.idp.attributes import provide_attributes_at_sso


'''authorize_decision
Expect a dictionnaries as return with:
 - the authorization decision e.g. dic['authz'] = True or False
 - optionnaly a message e.g. dic['message'] = message
'''
authorize_service = Signal(providing_args = ["request", "user", "audience"])

'''add_attributes_to_response
This signal is used by asynchronous bindings that do not receive attribute
list in the request. That means that a predefined list is defined.
The asynchronous binding means that the user is "on" the IdP to bring the
request then it is possible to take attributes in the Django session.
Mainly, it is usable at SSO request treatment.

The signal is send with parameters:
 - request: The request having triggerred a need of attribute
 - user: instance of the User Django Model to indicate the subject of
   attributes. Maybe different from request.user if any.
   - We should here only use a username in case that we want to provide
     attributes for entities having no corresponding User instance.
 - audience: identifier of the destination of attributes (e.g. the providerID
   for SAML2).

The return expected is a dictionnaries such as:
 - dic = {}
 - attributes = {}
 - attributes[name] = (value1, value2, )
 - attributes[(name, format)] = (value1, value2, )
 - attributes[(name, format, nickname)] = (value1, value2, )
 - dic['attributes'] = attributes
 - return dic
'''
add_attributes_to_response = \
    Signal(providing_args = ["request", "user", "audience"])

add_attributes_to_response.connect(provide_attributes_at_sso)

'''add_attributes_to_response

Idem as add_attributes_to_response except that the signal sender gives a list
of attribute identifiers. The attribute namespace is obtained from the
provider to which a namespace has been declared.
'''
add_attributes_listed_to_response = \
    Signal(providing_args = ["request", "user", "audience", "attributes"])

'''avoid_consent
Expect a boolean e.g. dic['avoid_consent'] = True or False
'''
avoid_consent = Signal(providing_args = ["request", "user", "audience"])
