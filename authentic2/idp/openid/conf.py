import os
import tempfile
from django.conf import settings

tempdir = tempfile.gettempdir()

STORE = getattr(settings, 'OPENID_PROVIDER_STORE',
                'openid.store.filestore.FileOpenIDStore')

FILESTORE_PATH = getattr(settings, 'OPENID_PROVIDER_FILESTORE_PATH',
                         os.path.join(tempdir, 'openid-filestore'))
