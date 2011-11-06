# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 : */

import time

import openid.store.interface
from django.conf import settings

import models
from authentic2 import nonce


NONCE_TIMEOUT = getattr(settings, 'OPENID_NONCE_TIMEOUT',
        getattr(settings, 'NONCE_TIMEOUT', openid.store.nonce.SKEW))

class DjangoOpenIDStore(openid.store.interface.OpenIDStore):
    def cleanupAssociations(self):
        return models.Association.cleanup_associations()

    def cleanupNonces(self):
        nonce.cleanup_nonces()

    def storeAssociation(self, server_url, association):
        return models.Association.store_association(server_url, association)

    def getAssociation(self, server_url, handle=None):
        return models.Association.get_association(server_url, handle)

    def removeAssociation(self, server_url, handle):
        return models.Association.remove_association(server_url, handle)

    def useNonce(self, server_url, timestamp, salt):
        now = time.time()
        if not (timestamp < now < (timestamp + NONCE_TIMEOUT)):
            return False
        value = '%s_%s_%s' % (server_url, timestamp, salt)

        return nonce.accept_nonce(value, 'OpenID', NONCE_TIMEOUT)
