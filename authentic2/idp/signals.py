from django.dispatch import Signal

'''authorize_decision
Expect a dictionnaries as return with:
 - the authorization decision e.g. dic['authz'] = True or False
 - optionnaly a message e.g. dic['message'] = message
'''
authorize_service = Signal(providing_args = ["request","user","audience"])

'''add_attributes_to_response
Expect a dictionnaries as return with:
 - the attributes to add to the response e.g.
   - dic = {}
   - attributes = {}
   - values = [value1, value2]
   - attributes[name] = values
   - attributes[(name, format)] = values
   - dic['attributes'] = attributes
   - return dic
'''
add_attributes_to_response = Signal(providing_args = ["request","user","audience"])

'''avoid_consent
Expect a boolean e.g. dic['avoid_consent'] = True or False
'''
avoid_consent = Signal(providing_args = ["request","user","audience"])
