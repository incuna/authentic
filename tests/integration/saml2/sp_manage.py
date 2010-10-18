from django.core.management import *
import os

TEST_PATH = os.path.dirname(os.path.abspath(__file__))

try:
    import settings
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(TEST_PATH, 'sp.db'),
        },
    }

except ImportError:
    import sys
    sys.stderr.write("Error: Unable to import settings from %s!\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
