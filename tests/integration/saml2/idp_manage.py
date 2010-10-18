from django.core.management import *
try:
    import idp_settings as settings
except ImportError:
    import sys
    sys.stderr.write("Error: Unable to import settings from %s!\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
