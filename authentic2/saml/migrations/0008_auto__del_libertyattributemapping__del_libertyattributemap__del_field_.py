# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting model 'LibertyAttributeMapping'
        db.delete_table('saml_libertyattributemapping')

        # Deleting model 'LibertyAttributeMap'
        db.delete_table('saml_libertyattributemap')

        # Deleting field 'LibertyServiceProvider.attribute_map'
        db.delete_column('saml_libertyserviceprovider', 'attribute_map_id')

        # Adding field 'LibertyServiceProvider.attribute_policy'
        db.add_column('saml_libertyserviceprovider', 'attribute_policy', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['idp.AttributePolicy'], null=True, blank=True), keep_default=False)

        # Changing field 'LibertyServiceProvider.ask_user_consent'
        db.alter_column('saml_libertyserviceprovider', 'ask_user_consent', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'LibertyServiceProvider.encrypt_nameid'
        db.alter_column('saml_libertyserviceprovider', 'encrypt_nameid', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'LibertyServiceProvider.enabled'
        db.alter_column('saml_libertyserviceprovider', 'enabled', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'LibertyServiceProvider.authn_request_signed'
        db.alter_column('saml_libertyserviceprovider', 'authn_request_signed', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'LibertyServiceProvider.idp_initiated_sso'
        db.alter_column('saml_libertyserviceprovider', 'idp_initiated_sso', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'LibertyServiceProvider.encrypt_assertion'
        db.alter_column('saml_libertyserviceprovider', 'encrypt_assertion', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'IdPOptionsSPPolicy.enable_http_method_for_defederation_request'
        db.alter_column('saml_idpoptionssppolicy', 'enable_http_method_for_defederation_request', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'IdPOptionsSPPolicy.want_force_authn_request'
        db.alter_column('saml_idpoptionssppolicy', 'want_force_authn_request', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'IdPOptionsSPPolicy.enabled'
        db.alter_column('saml_idpoptionssppolicy', 'enabled', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'IdPOptionsSPPolicy.allow_create'
        db.alter_column('saml_idpoptionssppolicy', 'allow_create', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'IdPOptionsSPPolicy.want_authn_request_signed'
        db.alter_column('saml_idpoptionssppolicy', 'want_authn_request_signed', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'IdPOptionsSPPolicy.enable_http_method_for_slo_request'
        db.alter_column('saml_idpoptionssppolicy', 'enable_http_method_for_slo_request', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'IdPOptionsSPPolicy.no_nameid_policy'
        db.alter_column('saml_idpoptionssppolicy', 'no_nameid_policy', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'IdPOptionsSPPolicy.transient_is_persistent'
        db.alter_column('saml_idpoptionssppolicy', 'transient_is_persistent', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'IdPOptionsSPPolicy.want_is_passive_authn_request'
        db.alter_column('saml_idpoptionssppolicy', 'want_is_passive_authn_request', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'IdPOptionsSPPolicy.enable_binding_for_sso_response'
        db.alter_column('saml_idpoptionssppolicy', 'enable_binding_for_sso_response', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'LibertyIdentityProvider.enabled'
        db.alter_column('saml_libertyidentityprovider', 'enabled', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'LibertyIdentityProvider.enable_following_idp_options_policy'
        db.alter_column('saml_libertyidentityprovider', 'enable_following_idp_options_policy', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'LibertyIdentityProvider.enable_following_authorization_policy'
        db.alter_column('saml_libertyidentityprovider', 'enable_following_authorization_policy', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'AuthorizationSPPolicy.enabled'
        db.alter_column('saml_authorizationsppolicy', 'enabled', self.gf('django.db.models.fields.BooleanField')(blank=True))
    
    
    def backwards(self, orm):
        
        # Adding model 'LibertyAttributeMapping'
        db.create_table('saml_libertyattributemapping', (
            ('map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['saml.LibertyAttributeMap'])),
            ('attribute_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attribute_value_format', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('source_attribute_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('saml', ['LibertyAttributeMapping'])

        # Adding model 'LibertyAttributeMap'
        db.create_table('saml_libertyattributemap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40, unique=True)),
        ))
        db.send_create_signal('saml', ['LibertyAttributeMap'])

        # Adding field 'LibertyServiceProvider.attribute_map'
        db.add_column('saml_libertyserviceprovider', 'attribute_map', self.gf('django.db.models.fields.related.ForeignKey')(related_name='service_providers', null=True, to=orm['saml.LibertyAttributeMap'], blank=True), keep_default=False)

        # Deleting field 'LibertyServiceProvider.attribute_policy'
        db.delete_column('saml_libertyserviceprovider', 'attribute_policy_id')

        # Changing field 'LibertyServiceProvider.ask_user_consent'
        db.alter_column('saml_libertyserviceprovider', 'ask_user_consent', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'LibertyServiceProvider.encrypt_nameid'
        db.alter_column('saml_libertyserviceprovider', 'encrypt_nameid', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'LibertyServiceProvider.enabled'
        db.alter_column('saml_libertyserviceprovider', 'enabled', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'LibertyServiceProvider.authn_request_signed'
        db.alter_column('saml_libertyserviceprovider', 'authn_request_signed', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'LibertyServiceProvider.idp_initiated_sso'
        db.alter_column('saml_libertyserviceprovider', 'idp_initiated_sso', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'LibertyServiceProvider.encrypt_assertion'
        db.alter_column('saml_libertyserviceprovider', 'encrypt_assertion', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IdPOptionsSPPolicy.enable_http_method_for_defederation_request'
        db.alter_column('saml_idpoptionssppolicy', 'enable_http_method_for_defederation_request', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IdPOptionsSPPolicy.want_force_authn_request'
        db.alter_column('saml_idpoptionssppolicy', 'want_force_authn_request', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IdPOptionsSPPolicy.enabled'
        db.alter_column('saml_idpoptionssppolicy', 'enabled', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IdPOptionsSPPolicy.allow_create'
        db.alter_column('saml_idpoptionssppolicy', 'allow_create', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IdPOptionsSPPolicy.want_authn_request_signed'
        db.alter_column('saml_idpoptionssppolicy', 'want_authn_request_signed', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IdPOptionsSPPolicy.enable_http_method_for_slo_request'
        db.alter_column('saml_idpoptionssppolicy', 'enable_http_method_for_slo_request', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IdPOptionsSPPolicy.no_nameid_policy'
        db.alter_column('saml_idpoptionssppolicy', 'no_nameid_policy', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IdPOptionsSPPolicy.transient_is_persistent'
        db.alter_column('saml_idpoptionssppolicy', 'transient_is_persistent', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IdPOptionsSPPolicy.want_is_passive_authn_request'
        db.alter_column('saml_idpoptionssppolicy', 'want_is_passive_authn_request', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IdPOptionsSPPolicy.enable_binding_for_sso_response'
        db.alter_column('saml_idpoptionssppolicy', 'enable_binding_for_sso_response', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'LibertyIdentityProvider.enabled'
        db.alter_column('saml_libertyidentityprovider', 'enabled', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'LibertyIdentityProvider.enable_following_idp_options_policy'
        db.alter_column('saml_libertyidentityprovider', 'enable_following_idp_options_policy', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'LibertyIdentityProvider.enable_following_authorization_policy'
        db.alter_column('saml_libertyidentityprovider', 'enable_following_authorization_policy', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'AuthorizationSPPolicy.enabled'
        db.alter_column('saml_authorizationsppolicy', 'enabled', self.gf('django.db.models.fields.BooleanField')())
    
    
    models = {
        'attribute_aggregator.attributesource': {
            'Meta': {'object_name': 'AttributeSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'namespace': ('django.db.models.fields.CharField', [], {'default': "('Default', 'Default')", 'max_length': '100'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'idp.attributeitem': {
            'Meta': {'object_name': 'AttributeItem'},
            'attribute_name': ('django.db.models.fields.CharField', [], {'default': "('OpenLDAProotDSE', 'OpenLDAProotDSE')", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'output_name_format': ('django.db.models.fields.CharField', [], {'default': "('urn:oasis:names:tc:SAML:2.0:attrname-format:basic', 'SAMLv2 BASIC')", 'max_length': '100'}),
            'output_namespace': ('django.db.models.fields.CharField', [], {'default': "('Default', 'Default')", 'max_length': '100'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['attribute_aggregator.AttributeSource']", 'null': 'True', 'blank': 'True'})
        },
        'idp.attributelist': {
            'Meta': {'object_name': 'AttributeList'},
            'attributes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'attributes of the list'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['idp.AttributeItem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'idp.attributepolicy': {
            'Meta': {'object_name': 'AttributePolicy'},
            'attribute_filter_for_sso_from_push_sources': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filter attributes of push sources with list'", 'null': 'True', 'to': "orm['idp.AttributeList']"}),
            'attribute_list_for_sso_from_pull_sources': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'attributes from pull sources'", 'null': 'True', 'to': "orm['idp.AttributeList']"}),
            'filter_source_of_filtered_attributes': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'forward_attributes_from_push_sources': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map_attributes_from_push_sources': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'map_attributes_of_filtered_attributes': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'output_name_format': ('django.db.models.fields.CharField', [], {'default': "('urn:oasis:names:tc:SAML:2.0:attrname-format:basic', 'SAMLv2 BASIC')", 'max_length': '100'}),
            'output_namespace': ('django.db.models.fields.CharField', [], {'default': "('Default', 'Default')", 'max_length': '100'}),
            'send_error_and_no_attrs_if_missing_required_attrs': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'source_filter_for_sso_from_push_sources': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'filter attributes of push sources with sources'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['attribute_aggregator.AttributeSource']"})
        },
        'saml.authorizationattributemap': {
            'Meta': {'object_name': 'AuthorizationAttributeMap'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'saml.authorizationattributemapping': {
            'Meta': {'object_name': 'AuthorizationAttributeMapping'},
            'attribute_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'attribute_value': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'attribute_value_format': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['saml.AuthorizationAttributeMap']"}),
            'source_attribute_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        'saml.authorizationsppolicy': {
            'Meta': {'object_name': 'AuthorizationSPPolicy'},
            'attribute_map': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'authorization_attributes'", 'null': 'True', 'to': "orm['saml.AuthorizationAttributeMap']"}),
            'default_denial_message': ('django.db.models.fields.CharField', [], {'default': "u'You are not authorized to access the service.'", 'max_length': '80'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        'saml.idpoptionssppolicy': {
            'Meta': {'object_name': 'IdPOptionsSPPolicy'},
            'allow_create': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'binding_for_sso_response': ('django.db.models.fields.CharField', [], {'default': "'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact'", 'max_length': '60'}),
            'enable_binding_for_sso_response': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enable_http_method_for_defederation_request': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enable_http_method_for_slo_request': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'http_method_for_defederation_request': ('django.db.models.fields.IntegerField', [], {'default': '5', 'max_length': '60'}),
            'http_method_for_slo_request': ('django.db.models.fields.IntegerField', [], {'default': '4', 'max_length': '60'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'no_nameid_policy': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'requested_name_id_format': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '20'}),
            'transient_is_persistent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user_consent': ('django.db.models.fields.CharField', [], {'default': "'urn:oasis:names:tc:SAML:2.0:consent:current-implicit'", 'max_length': '60'}),
            'want_authn_request_signed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'want_force_authn_request': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'want_is_passive_authn_request': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'saml.keyvalue': {
            'Meta': {'object_name': 'KeyValue'},
            'key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'}),
            'value': ('authentic2.saml.fields.PickledObjectField', [], {})
        },
        'saml.libertyartifact': {
            'Meta': {'object_name': 'LibertyArtifact'},
            'artifact': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'creation': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'django_session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'provider_id': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'saml.libertyassertion': {
            'Meta': {'object_name': 'LibertyAssertion'},
            'assertion': ('django.db.models.fields.TextField', [], {}),
            'assertion_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'creation': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider_id': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'session_index': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'saml.libertyfederation': {
            'Meta': {'unique_together': "(('name_id_qualifier', 'name_id_format', 'name_id_content', 'name_id_sp_name_qualifier'),)", 'object_name': 'LibertyFederation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idp_id': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'name_id_content': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_id_format': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_id_qualifier': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'name_id_sp_name_qualifier': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_id_sp_provided_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sp_id': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'saml.libertyidentitydump': {
            'Meta': {'object_name': 'LibertyIdentityDump'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity_dump': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'saml.libertyidentityprovider': {
            'Meta': {'object_name': 'LibertyIdentityProvider'},
            'authorization_policy': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'authorization_policy'", 'null': 'True', 'to': "orm['saml.AuthorizationSPPolicy']"}),
            'enable_following_authorization_policy': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enable_following_idp_options_policy': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'idp_options_policy': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'idp_options_policy'", 'null': 'True', 'to': "orm['saml.IdPOptionsSPPolicy']"}),
            'liberty_provider': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'identity_provider'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['saml.LibertyProvider']"})
        },
        'saml.libertymanagedump': {
            'Meta': {'object_name': 'LibertyManageDump'},
            'django_session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manage_dump': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'saml.libertyprovider': {
            'Meta': {'object_name': 'LibertyProvider'},
            'ca_cert_chain': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'entity_id': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            'entity_id_sha1': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'federation_source': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'}),
            'protocol_conformance': ('django.db.models.fields.IntegerField', [], {'max_length': '10'}),
            'public_key': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ssl_certificate': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'saml.libertyproviderpolicy': {
            'Meta': {'object_name': 'LibertyProviderPolicy'},
            'authn_request_signature_check_hint': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'saml.libertyserviceprovider': {
            'Meta': {'object_name': 'LibertyServiceProvider'},
            'accepted_name_id_format': ('authentic2.saml.fields.MultiSelectField', [], {'max_length': '31', 'blank': 'True'}),
            'ask_user_consent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'attribute_policy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['idp.AttributePolicy']", 'null': 'True', 'blank': 'True'}),
            'authn_request_signed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'default_name_id_format': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '20'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'encrypt_assertion': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'encrypt_nameid': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'idp_initiated_sso': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'liberty_provider': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'service_provider'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['saml.LibertyProvider']"}),
            'policy': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['saml.LibertyProviderPolicy']", 'null': 'True'}),
            'prefered_assertion_consumer_binding': ('django.db.models.fields.CharField', [], {'default': "'meta'", 'max_length': '4'})
        },
        'saml.libertysession': {
            'Meta': {'object_name': 'LibertySession'},
            'assertion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['saml.LibertyAssertion']", 'null': 'True'}),
            'creation': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'django_session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'federation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['saml.LibertyFederation']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_id_content': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_id_format': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'name_id_qualifier': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'}),
            'name_id_sp_name_qualifier': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'provider_id': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'session_index': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'saml.libertysessiondump': {
            'Meta': {'object_name': 'LibertySessionDump'},
            'django_session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.IntegerField', [], {}),
            'session_dump': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'saml.libertysessionsp': {
            'Meta': {'object_name': 'LibertySessionSP'},
            'django_session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'federation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['saml.LibertyFederation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session_index': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }
    
    complete_apps = ['saml']
