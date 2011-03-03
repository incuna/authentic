import datetime
import sys

from django.core.management.base import NoArgsCommand
from django.db import models
import django.core.management.commands.cleanup as cleanup

class Command(NoArgsCommand):
    help = """Can be run as a cronjob or directly to clean out old data from the \
database. It calls the cleanup() method of manager classes."""

    def cleanup(self):
        all_models = [ ]
        for app in models.get_apps():
            all_models += [ m for m in models.get_models(app) ]
        for model in all_models:
            manager = getattr(model, 'objects', None)
            if manager is None:
                continue
            cleanup = getattr(manager, 'cleanup', None)
            if callable(cleanup):
                manager.cleanup()

    def handle_noargs(self, **options):
        self.cleanup()
        cleanup.Command().execute(**options)
