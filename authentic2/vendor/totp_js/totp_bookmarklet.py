import binascii
import base64
import os.path

def __content(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read()

crypto_js = __content('crypto.js')
hotp_js = __content('hotp.js')
myotp_js = __content('my-otp.js')


def dataize(document, type='text/html'):
    return 'data:%s;base64,%s' % (type, base64.b64encode(document))

def otp_doc(key,mode='dec6'):
    '''Convert an hexadecimal key to a document able to produce TOTP keys using
       the dec6 mode
    '''
    doc = ''''<html>
<body>
<script type="text/javascript">%s;history.back()</script>
</body>
</html>''' % (crypto_js + ';' + hotp_js + ';' + \
        myotp_js.replace('FAFA',key).replace('MODE',mode))
    return dataize(doc)

if __name__ == '__main__':
    import sys
    print '''<html><body><a href="%s" title="Drag me to your bookmark">OTP Password</a></body></html>''' % otp_doc(sys.argv[1])
