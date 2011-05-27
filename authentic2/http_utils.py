try:
    import M2Crypto
except ImportError:
    M2Crypto = None

import urllib2
from django.conf import settings

__SSL_CONTEXT = None

def get_ssl_context():
    global __SSL_CONTEXT
    if __SSL_CONTEXT is None:
        __SSL_CONTEXT = M2Crypto.SSL.Context()
        cafile = getattr(settings, 'CAFILE', '/etc/ssl/certs/ca-certificates.crt')
        capath = getattr(settings, 'CAPATH', '/etc/ssl/certs/')
        __SSL_CONTEXT.load_verify_locations(cafile=cafile, capath=capath)
    return __SSL_CONTEXT

def get_url(url):
    '''Does a simple GET on an URL, if the URL uses TLS, M2Crypto is used to
       check the certificate'''

    if url.startswith('https'):
        if not M2Crypto:
            raise urllib2.URLError('https is unsupported without M2Crypto')
        try:
            return M2Crypto.m2urllib2.build_opener(get_ssl_context()).open(url).read()
        except M2Crypto.SSL.Checker.SSLVerificationError, e:
            # Wrap error
            raise urllib2.URLError('SSL Verification error %s' % e)
    return urllib2.urlopen(url).read()

if __name__ == '__main__':
    print get_url('https://dev.entrouvert.org')
