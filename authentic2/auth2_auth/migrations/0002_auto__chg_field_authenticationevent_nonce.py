# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'AuthenticationEvent.nonce'
        db.alter_column('auth2_auth_authenticationevent', 'nonce', self.gf('django.db.models.fields.CharField')(max_length=255))


    def backwards(self, orm):
        
        # Changing field 'AuthenticationEvent.nonce'
        db.alter_column('auth2_auth_authenticationevent', 'nonce', self.gf('django.db.models.fields.CharField')(max_length=20))


    models = {
        'auth2_auth.authenticationevent': {
            'Meta': {'object_name': 'AuthenticationEvent'},
            'how': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nonce': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'who': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['auth2_auth']
