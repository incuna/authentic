# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 : */

import openid.store.interface

import models

class DjangoOpenIDStore(openid.store.interface.OpenIDStore):
    def cleanupAssociations(self):
        return models.Association.cleanup_associations()

    def cleanupNonces(self):
        return models.Association.cleanup_nonces()

    def storeAssociation(self, server_url, association):
        return models.Association.store_association(server_url, association)

    def getAssociation(self, server_url, handle=None):
        return models.Association.get_association(server_url, handle)

    def removeAssociation(self, server_url, handle):
        return models.Association.remove_association(server_url, handle)

    def useNonce(self, server_url, timestamp, salt):
        return models.Nonce.use_nonce(server_url, timestamp, salt)
