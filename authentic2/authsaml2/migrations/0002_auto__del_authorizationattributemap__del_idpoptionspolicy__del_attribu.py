# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting model 'AuthorizationAttributeMap'
        db.delete_table('authsaml2_authorizationattributemap')

        # Deleting model 'IdPOptionsPolicy'
        db.delete_table('authsaml2_idpoptionspolicy')

        # Deleting model 'AttributeMapping'
        db.delete_table('authsaml2_attributemapping')
    
    
    def backwards(self, orm):
        
        # Adding model 'AuthorizationAttributeMap'
        db.create_table('authsaml2_authorizationattributemap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40, unique=True)),
        ))
        db.send_create_signal('authsaml2', ['AuthorizationAttributeMap'])

        # Adding model 'IdPOptionsPolicy'
        db.create_table('authsaml2_idpoptionspolicy', (
            ('enable_http_method_for_defederation_request', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80, unique=True)),
            ('http_method_for_defederation_request', self.gf('django.db.models.fields.IntegerField')(default=5, max_length=60)),
            ('binding_for_sso_response', self.gf('django.db.models.fields.CharField')(default='urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact', max_length=60)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_create', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('enable_http_method_for_slo_request', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('http_method_for_slo_request', self.gf('django.db.models.fields.IntegerField')(default=4, max_length=60)),
            ('requested_name_id_format', self.gf('django.db.models.fields.CharField')(default='none', max_length=20)),
            ('attribute_map', self.gf('django.db.models.fields.related.ForeignKey')(related_name='authorization_attributes', null=True, to=orm['authsaml2.AuthorizationAttributeMap'], blank=True)),
            ('user_consent', self.gf('django.db.models.fields.CharField')(default='urn:oasis:names:tc:SAML:2.0:consent:current-implicit', max_length=60)),
            ('no_nameid_policy', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('transient_is_persistent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('want_authn_request_signed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('want_is_passive_authn_request', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('enable_binding_for_sso_response', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('want_force_authn_request', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('authsaml2', ['IdPOptionsPolicy'])

        # Adding model 'AttributeMapping'
        db.create_table('authsaml2_attributemapping', (
            ('map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authsaml2.AuthorizationAttributeMap'])),
            ('attribute_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('source_attribute_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('attribute_value_format', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('attribute_value', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('authsaml2', ['AttributeMapping'])
    
    
    models = {
        'authsaml2.myserviceprovider': {
            'Meta': {'object_name': 'MyServiceProvider'},
            'back_url': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'handle_persistent': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'handle_transient': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['authsaml2']
