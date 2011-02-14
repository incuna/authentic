# Constants #
CAS_NAMESPACE    = 'http://www.yale.edu/tp/cas'
RENEW_PARAM      = 'renew'
SERVICE_PARAM    = 'service'
GATEWAY_PARAM    = 'gateway'
WARN_PARAM       = 'warn'
URL_PARAM        = 'url'
TICKET_PARAM     = 'ticket'
PGT_URL_PARAM    = 'pgtUrl'
PGT_PARAM        = 'pgt'
PGT_ID_PARAM     = 'pgtId'
PGT_IOU_PARAM    = 'pgtIou'
TARGET_SERVICE_PARAM = 'targetService'
USERNAME_FIELD   = 'username' # unused
PASSWORD_FIELD   = 'password' # unused
LT_FIELD         = 'lt'       # unused
SERVICE_TICKET_PREFIX = 'ST-'
ID_PARAM         = 'id'
CANCEL_PARAM     = 'cancel'

# ERROR codes
INVALID_REQUEST_ERROR  = 'INVALID_REQUEST'
INVALID_TICKET_ERROR   = 'INVALID_TICKET'
INVALID_SERVICE_ERROR  = 'INVALID_SERVICE'
INTERNAL_ERROR         = 'INTERNAL_ERROR'
BAD_PGT_ERROR          = 'BAD_PGT'

# XML Elements for CAS 2.0
SERVICE_RESPONSE_ELT       = 'serviceResponse'

AUTHENTICATION_SUCCESS_ELT = 'authenticationSuccess'
USER_ELT                   = 'user'
PGT_ELT                    = 'proxyGrantingTicket'
PROXIES_ELT                = 'proxies'
PROXY_ELT                  = 'proxy'

AUTHENTICATION_FAILURE_ELT = 'authenticationFailure'
CODE_ELT                   = 'code'

PROXY_SUCCESS_ELT          = 'proxySuccess'
PROXY_TICKET_ELT           = 'proxyTicket'

PROXY_FAILURE_ELT          = 'proxyFailure'

# Templates

CAS10_VALIDATION_FAILURE = 'no\n\n'
CAS10_VALIDATION_SUCCESS = 'yes\n%s\n'
CAS20_VALIDATION_FAILURE = '''<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationFailure code="%s">
        %s
    </cas:authenticationFailure>
</cas:serviceResponse>'''
CAS20_VALIDATION_SUCCESS = '''<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationSuccess>
        <cas:user>%s</cas:user>
    </cas:authenticationSuccess>
</cas:serviceResponse>'''
