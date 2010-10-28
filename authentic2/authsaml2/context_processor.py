import authentic2.authsaml2
import authentic2.saml.common

def authsaml2_login_page(request):
    if not authentic2.authsaml2.utils.is_sp_configured():
        return {}
    return {'providers_list': authentic2.saml.common.get_idp_list()}
