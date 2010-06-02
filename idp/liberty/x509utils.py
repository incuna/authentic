# w.c.s. - web application for online forms
# Copyright (C) 2005-2010  Entr'ouvert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

import base64
import binascii
import sys
import tempfile
import os
import subprocess
import stat

_openssl = 'openssl'

def decapsulate_pem_file(file_or_string):
    '''Remove PEM header lines'''
    if not isinstance(file_or_string, basestring):
        content = file_or_string.read()
    else:
        content = file_or_string
    i = content.find('--BEGIN')
    j = content.find('\n', i)
    k = content.find('--END', j)
    l = content.rfind('\n', 0, k)
    return content[j+1:l]

def _call_openssl(args):
    '''Use subprocees to spawn an openssl process

    Return a tuple made of the return code and the stdout output
    '''
    try:
        process = subprocess.Popen(args=[_openssl]+args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = process.communicate()[0]
        return process.returncode, output
    except OSError:
        return 1, None


def _protect_file(fd,filepath):
    '''Make a file targeted by a file descriptor readable only by the current user

       It's needed to be sure nobody can read the private key file we manage.
    '''
    if hasattr(os, 'fchmod'):
        os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
    else: # handle python <2.6
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)

def check_key_pair_consistency(publickey=None,privatekey=None):
    '''Check if two PEM key pair whether they are publickey or certificate, are
    well formed and related.
    '''
    if publickey and privatekey:
        try:
            privatekey_file_fd, privatekey_fn = tempfile.mkstemp()
            publickey_file_fd, publickey_fn = tempfile.mkstemp()
            _protect_file(privatekey_file_fd, privatekey_fn)
            _protect_file(publickey_file_fd, publickey_fn)
            os.fdopen(privatekey_file_fd,'w').write(privatekey)
            os.fdopen(publickey_file_fd,'w').write(publickey)
            if 'BEGIN CERTIFICATE' in publickey:
                rc1, modulus1 = _call_openssl(['x509', '-in', publickey_fn,'-noout','-modulus'])
            else:
                rc1, modulus1 = _call_openssl(['rsa', '-pubin', '-in', publickey_fn,'-noout','-modulus'])
                if rc1 != 0:
                    rc1, modulus1 = _call_openssl(['dsa', '-pubin', '-in', publickey_fn,'-noout','-modulus'])

            if rc1 != 0:
                return False

            rc2, modulus2 = _call_openssl(['rsa', '-in', privatekey_fn,'-noout','-modulus'])
            if rc2 != 0:
                rc2, modulus2 = _call_openssl(['dsa', '-in', privatekey_fn,'-noout','-modulus'])

            if rc1 == 0 and rc2 == 0 and modulus1 == modulus2:
                return True
            else:
                return False
        finally:
            os.unlink(privatekey_fn)
            os.unlink(publickey_fn)
    return None

def generate_rsa_keypair(numbits=1024):
    '''Generate simple RSA public and private key files
    '''
    try:
        privatekey_file_fd, privatekey_fn = tempfile.mkstemp()
        publickey_file_fd, publickey_fn = tempfile.mkstemp()
        _protect_file(privatekey_file_fd, privatekey_fn)
        _protect_file(publickey_file_fd, publickey_fn)
        rc1, _ = _call_openssl(['genrsa','-out', privatekey_fn,'-passout', 'pass:',str(numbits)])
        rc2, _ = _call_openssl(['rsa','-in', privatekey_fn,'-pubout','-out', publickey_fn])
        if rc1 != 0 or rc2 != 0:
            raise Exception('Failed to generate a key')
        return (os.fdopen(publickey_file_fd).read(), os.fdopen(privatekey_file_fd).read())
    finally:
        os.unlink(privatekey_fn)
        os.unlink(publickey_fn)

def get_rsa_public_key_modulus(publickey):
    try:
        publickey_file_fd, publickey_fn = tempfile.mkstemp()
        os.fdopen(publickey_file_fd,'w').write(publickey)
        if 'BEGIN PUBLIC' in publickey:
            rc, modulus = _call_openssl(['rsa', '-pubin', '-in', publickey_fn,'-noout','-modulus'])
        elif 'BEGIN RSA PRIVATE KEY' in publickey:
            rc, modulus = _call_openssl(['rsa', '-in', publickey_fn, '-noout', '-modulus'])
        elif 'BEGIN CERTIFICATE' in publickey:
            rc, modulus = _call_openssl(['x509', '-in', publickey_fn,'-noout','-modulus'])
        else:
            return None
        i = modulus.find('=')
        if rc == 0 and i:
            return int(modulus[i+1:].strip(),16)
    finally:
        os.unlink(publickey_fn)
    return None

def get_rsa_public_key_exponent(publickey):
    try:
        publickey_file_fd, publickey_fn = tempfile.mkstemp()
        os.fdopen(publickey_file_fd,'w').write(publickey)
        _exponent = 'Exponent: '
        if 'BEGIN PUBLIC' in publickey:
            rc, modulus = _call_openssl(['rsa', '-pubin', '-in', publickey_fn,'-noout','-text'])
        elif 'BEGIN RSA PRIVATE' in publickey:
            rc, modulus = _call_openssl(['rsa', '-in', publickey_fn, '-noout', '-text'])
            _exponent = 'publicExponent: '
        elif 'BEGIN CERTIFICATE' in publickey:
            rc, modulus = _call_openssl(['x509', '-in', publickey_fn,'-noout','-text'])
        else:
            return None
        i = modulus.find(_exponent)
        j = modulus.find('(', i)
        if rc == 0 and i and j:
            return int(modulus[i+len(_exponent):j].strip())
    finally:
        os.unlink(publickey_fn)
    return None

def can_generate_rsa_key_pair():
    syspath = os.environ.get('PATH')
    if syspath:
        for base in syspath.split(':'):
            if os.path.exists(os.path.join(base,'openssl')):
                return True
    else:
        return False

def get_xmldsig_rsa_key_value(publickey):
    def int_to_bin(i):
        h = hex(i)[2:].strip('L')
        if len(h) % 2 == 1:
            h = '0' + h
        return binascii.unhexlify(h)

    mod = get_rsa_public_key_modulus(publickey)
    exp = get_rsa_public_key_exponent(publickey)
    return '<RSAKeyValue xmlns="http://www.w3.org/2000/09/xmldsig#">\n\t<Modulus>%s</Modulus>\n\t<Exponent>%s</Exponent>\n</RSAKeyValue>' % (base64.b64encode(int_to_bin(mod)), base64.b64encode(int_to_bin(exp)))


if __name__ == '__main__':
    assert(can_generate_rsa_key_pair())
    publickey, privatekey = generate_rsa_keypair()
    assert(publickey is not None and privatekey is not None)
    assert(check_key_pair_consistency(publickey, privatekey))
    _, privatekey = generate_rsa_keypair()
    assert(not check_key_pair_consistency(publickey, privatekey))
    assert(get_xmldsig_rsa_key_value(publickey) is not None)
    assert(get_rsa_public_key_modulus(publickey) is not None)
    assert(get_rsa_public_key_exponent(publickey) is not None)
    # Certificate/key generated using
    # openssl req -x509 -newkey rsa:1024 -keyout key.pem -out req.pem
    cert = '''-----BEGIN CERTIFICATE-----
MIICHjCCAYegAwIBAgIJALgmNSS3spUaMA0GCSqGSIb3DQEBBQUAMBUxEzARBgNV
BAoTCkVudHJvdXZlcnQwHhcNMDkxMDI4MjIwODEzWhcNMDkxMTI3MjIwODEzWjAV
MRMwEQYDVQQKEwpFbnRyb3V2ZXJ0MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKB
gQCtTbDTe/LrD+gvK0Sgf/rnvAg4zcc/vJcEdsiGsJ3shTse7OPf5fIaD7lry+jm
tFX61n8Rn1d1iw+whuYbrG6R3OhDw50vufb2RrRSHBOA7CcfiKQD6CT2p31msv+C
iHbGmoHRFyt2CnRGy2FCX2Oizf5qxfjHaJEXu0tk/SdN2QIDAQABo3YwdDAdBgNV
HQ4EFgQUlDrrh8KudeyeInXqios+Rdf9tQAwRQYDVR0jBD4wPIAUlDrrh8Kudeye
InXqios+Rdf9tQChGaQXMBUxEzARBgNVBAoTCkVudHJvdXZlcnSCCQC4JjUkt7KV
GjAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBBQUAA4GBAFHXBDW13NIiafS2cRP1
/KAMIfnB/kYINTUU7iv2oIOYtfpVR9yMmnLIVxTyN3rCWb7UV/ICkMotTHmKLDT8
Rp7tKc0zTQ+CQGFVYvfRAlz4kgW14DDx/oIBqr/yDv5mInFb8reSfP85cPrXp/wR
ufewZ2WHikP2kWoHWDkw8MDd
-----END CERTIFICATE-----'''
    key = '''-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQCtTbDTe/LrD+gvK0Sgf/rnvAg4zcc/vJcEdsiGsJ3shTse7OPf
5fIaD7lry+jmtFX61n8Rn1d1iw+whuYbrG6R3OhDw50vufb2RrRSHBOA7CcfiKQD
6CT2p31msv+CiHbGmoHRFyt2CnRGy2FCX2Oizf5qxfjHaJEXu0tk/SdN2QIDAQAB
AoGBAKlFVQ17540JAHPyAxnxZxSpaC5zb8YlYiwOCVblc5rtlw1hvEGYy5wA987+
YAHW6pQSphKEXFyG81Asst0c0vExgGVFjzAy/GFrBTnl0l5PtwPDDIAmGP6DQw4C
lOHJePloKp0xjCo2nJ8XluxkPp1+XtJyJOhZWpQPDvF3uL+xAkEA3t58jg0SV55s
E10R04QOJB0qIB9U4Nw29uhh5RXv8JRq41pw4iDmpi9I67nGqDeuxlDUQ/+5rLOE
Ptp07BsFWwJBAMcQ7wiwhIYtRC8ff3WbWX9wcABDyX47uYvAMIiaEOmFmJyI41mW
xlik821Aaid1Z45vgBN32hYkEbpWaaIVe9sCQQCX7mpQ2F5ptskMhkTxwbN2MR+X
mGRfiiA6P/8EkejpQ/R+GxibPzydi9yVPidMY/FUpqOd24YzUonT408T6fPDAkEA
pkkt86tIOLEtaNO97CcF/t+Un5QAh9MqLmQv5pwUDo4Lqo7qo1bAfyHjOlr5kdaP
17qqWRjf82jT6jzu5nddywJAVQpxlZ8fIZUzTD2mRQeLf5O+rXmtH1LlwRRGCNaa
8eM47A92x9uplD/sN550pTKM7XLhHBvEfLujUoGHpWQxGA==
-----END RSA PRIVATE KEY-----'''
    assert(check_key_pair_consistency(cert, key))
    assert(get_xmldsig_rsa_key_value(cert))
    assert(len(decapsulate_pem_file(key).splitlines()) == len(key.splitlines())-2)

