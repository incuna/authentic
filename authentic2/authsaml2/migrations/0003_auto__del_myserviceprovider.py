# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'MyServiceProvider'
        db.delete_table('authsaml2_myserviceprovider')


    def backwards(self, orm):
        
        # Adding model 'MyServiceProvider'
        db.create_table('authsaml2_myserviceprovider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('handle_persistent', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('handle_transient', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('back_url', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('authsaml2', ['MyServiceProvider'])


    models = {
        
    }

    complete_apps = ['authsaml2']
