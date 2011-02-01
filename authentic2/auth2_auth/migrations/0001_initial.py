# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AuthenticationEvent'
        db.create_table('auth2_auth_authenticationevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('who', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('how', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('nonce', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('auth2_auth', ['AuthenticationEvent'])


    def backwards(self, orm):
        
        # Deleting model 'AuthenticationEvent'
        db.delete_table('auth2_auth_authenticationevent')


    models = {
        'auth2_auth.authenticationevent': {
            'Meta': {'object_name': 'AuthenticationEvent'},
            'how': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nonce': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'who': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['auth2_auth']
