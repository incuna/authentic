from django.db import models
from django.contrib.auth.models import User

# Configuration models
def fix_name(name):
    return name.replace(' ', '_').replace('/', '_')

class FilenameGenerator(object):
    def __init__(self, infix):
        self.prefix = infix

    def __call__(self, instance, filename):
        return os.path.join(self.prefix,
                "%s_%s_%s" % (fix_name(instance.name), filename,
                    time.strftime("%Y%m%dT%H:%M:%SZ", time.gmtime())))


class LibertyServiceProvider(models.Model):
    name = models.CharField(max_length = 40, unique = True,
            help_text = "Internal nickname for the service provider")
    metadata = models.FileField(upload_to = FilenameGenerator("metadata"))
    public_key = models.FileField(upload_to = FilenameGenerator("public_key"))
    ssl_certificate = models.FileField(upload_to = FilenameGenerator("ssl_certificate"))


# Transactional models

class LibertyFederation(models.Model):
    user = models.ForeignKey(User)
    name_id_qualifier = models.CharField(max_length = 150, editable = False, verbose_name = "Qualifier")
    name_id_format = models.CharField(max_length = 100, editable = False, verbose_name = "NameIDFormat")
    name_id_content = models.CharField(max_length = 100, editable = False, verbose_name = "NameID")
    name_id_sp_name_qualifier = models.CharField(max_length = 100, editable = False, verbose_name = "SPNameQualifier")

class LibertySession(models.Model):
    django_session_key = models.CharField(max_length = 40, editable = False)

# When we receive a logout request, we lookup the LibertyAssertions, then the LibertySession and the the real DjangoSession

class LibertyAssertions(models.Model):
    liberty_session = models.ForeignKey(LibertySession, editable = False)
    session_index = models.CharField(max_length = 80, editable = False)
    assertion = models.TextField(editable = False)
    emission_time = models.DateTimeField(auto_now = True, editable = False)


