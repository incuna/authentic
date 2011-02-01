# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TrustedRoot'
        db.create_table('idp_openid_trustedroot', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('trust_root', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('choices', self.gf('authentic2.saml.fields.PickledObjectField')()),
        ))
        db.send_create_signal('idp_openid', ['TrustedRoot'])

        # Adding model 'Association'
        db.create_table('idp_openid_association', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server_url', self.gf('django.db.models.fields.CharField')(max_length=2047)),
            ('handle', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('secret', self.gf('authentic2.saml.fields.PickledObjectField')()),
            ('issued', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lifetime', self.gf('django.db.models.fields.IntegerField')()),
            ('expire', self.gf('django.db.models.fields.DateTimeField')()),
            ('assoc_type', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('idp_openid', ['Association'])

        # Adding unique constraint on 'Association', fields ['server_url', 'handle']
        db.create_unique('idp_openid_association', ['server_url', 'handle'])

        # Adding model 'Nonce'
        db.create_table('idp_openid_nonce', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('salt', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('server_url', self.gf('django.db.models.fields.CharField')(max_length=2047)),
            ('timestamp', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('idp_openid', ['Nonce'])

        # Adding unique constraint on 'Nonce', fields ['server_url', 'salt']
        db.create_unique('idp_openid_nonce', ['server_url', 'salt'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Nonce', fields ['server_url', 'salt']
        db.delete_unique('idp_openid_nonce', ['server_url', 'salt'])

        # Removing unique constraint on 'Association', fields ['server_url', 'handle']
        db.delete_unique('idp_openid_association', ['server_url', 'handle'])

        # Deleting model 'TrustedRoot'
        db.delete_table('idp_openid_trustedroot')

        # Deleting model 'Association'
        db.delete_table('idp_openid_association')

        # Deleting model 'Nonce'
        db.delete_table('idp_openid_nonce')


    models = {
        'idp_openid.association': {
            'Meta': {'unique_together': "(('server_url', 'handle'),)", 'object_name': 'Association'},
            'assoc_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'expire': ('django.db.models.fields.DateTimeField', [], {}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issued': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'lifetime': ('django.db.models.fields.IntegerField', [], {}),
            'secret': ('authentic2.saml.fields.PickledObjectField', [], {}),
            'server_url': ('django.db.models.fields.CharField', [], {'max_length': '2047'})
        },
        'idp_openid.nonce': {
            'Meta': {'unique_together': "(('server_url', 'salt'),)", 'object_name': 'Nonce'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'server_url': ('django.db.models.fields.CharField', [], {'max_length': '2047'}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {})
        },
        'idp_openid.trustedroot': {
            'Meta': {'object_name': 'TrustedRoot'},
            'choices': ('authentic2.saml.fields.PickledObjectField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'trust_root': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['idp_openid']
