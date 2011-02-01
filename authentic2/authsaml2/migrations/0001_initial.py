# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AuthorizationAttributeMap'
        db.create_table('authsaml2_authorizationattributemap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal('authsaml2', ['AuthorizationAttributeMap'])

        # Adding model 'AttributeMapping'
        db.create_table('authsaml2_attributemapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_attribute_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('attribute_value_format', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('attribute_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('attribute_value', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authsaml2.AuthorizationAttributeMap'])),
        ))
        db.send_create_signal('authsaml2', ['AttributeMapping'])

        # Adding model 'IdPOptionsPolicy'
        db.create_table('authsaml2_idpoptionspolicy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('no_nameid_policy', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requested_name_id_format', self.gf('django.db.models.fields.CharField')(default='none', max_length=20)),
            ('transient_is_persistent', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_create', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('enable_binding_for_sso_response', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('binding_for_sso_response', self.gf('django.db.models.fields.CharField')(default='urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact', max_length=60)),
            ('enable_http_method_for_slo_request', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('http_method_for_slo_request', self.gf('django.db.models.fields.IntegerField')(default=4, max_length=60)),
            ('enable_http_method_for_defederation_request', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('http_method_for_defederation_request', self.gf('django.db.models.fields.IntegerField')(default=5, max_length=60)),
            ('user_consent', self.gf('django.db.models.fields.CharField')(default='urn:oasis:names:tc:SAML:2.0:consent:current-implicit', max_length=60)),
            ('want_force_authn_request', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('want_is_passive_authn_request', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('want_authn_request_signed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attribute_map', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='authorization_attributes', null=True, to=orm['authsaml2.AuthorizationAttributeMap'])),
        ))
        db.send_create_signal('authsaml2', ['IdPOptionsPolicy'])

        # Adding model 'MyServiceProvider'
        db.create_table('authsaml2_myserviceprovider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('handle_persistent', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('handle_transient', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('back_url', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('authsaml2', ['MyServiceProvider'])


    def backwards(self, orm):
        
        # Deleting model 'AuthorizationAttributeMap'
        db.delete_table('authsaml2_authorizationattributemap')

        # Deleting model 'AttributeMapping'
        db.delete_table('authsaml2_attributemapping')

        # Deleting model 'IdPOptionsPolicy'
        db.delete_table('authsaml2_idpoptionspolicy')

        # Deleting model 'MyServiceProvider'
        db.delete_table('authsaml2_myserviceprovider')


    models = {
        'authsaml2.attributemapping': {
            'Meta': {'object_name': 'AttributeMapping'},
            'attribute_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'attribute_value': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'attribute_value_format': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authsaml2.AuthorizationAttributeMap']"}),
            'source_attribute_name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'authsaml2.authorizationattributemap': {
            'Meta': {'object_name': 'AuthorizationAttributeMap'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'authsaml2.idpoptionspolicy': {
            'Meta': {'object_name': 'IdPOptionsPolicy'},
            'allow_create': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attribute_map': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'authorization_attributes'", 'null': 'True', 'to': "orm['authsaml2.AuthorizationAttributeMap']"}),
            'binding_for_sso_response': ('django.db.models.fields.CharField', [], {'default': "'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact'", 'max_length': '60'}),
            'enable_binding_for_sso_response': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_http_method_for_defederation_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_http_method_for_slo_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'http_method_for_defederation_request': ('django.db.models.fields.IntegerField', [], {'default': '5', 'max_length': '60'}),
            'http_method_for_slo_request': ('django.db.models.fields.IntegerField', [], {'default': '4', 'max_length': '60'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'no_nameid_policy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requested_name_id_format': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '20'}),
            'transient_is_persistent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_consent': ('django.db.models.fields.CharField', [], {'default': "'urn:oasis:names:tc:SAML:2.0:consent:current-implicit'", 'max_length': '60'}),
            'want_authn_request_signed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'want_force_authn_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'want_is_passive_authn_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'authsaml2.myserviceprovider': {
            'Meta': {'object_name': 'MyServiceProvider'},
            'back_url': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'handle_persistent': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'handle_transient': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['authsaml2']
