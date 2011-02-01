# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'LibertyAttributeMap'
        db.create_table('saml_libertyattributemap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
        ))
        db.send_create_signal('saml', ['LibertyAttributeMap'])

        # Adding model 'LibertyAttributeMapping'
        db.create_table('saml_libertyattributemapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_attribute_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('attribute_value_format', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('attribute_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['saml.LibertyAttributeMap'])),
        ))
        db.send_create_signal('saml', ['LibertyAttributeMapping'])

        # Adding model 'LibertyProvider'
        db.create_table('saml_libertyprovider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entity_id', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('entity_id_sha1', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40, blank=True)),
            ('protocol_conformance', self.gf('django.db.models.fields.IntegerField')(max_length=10)),
            ('metadata', self.gf('django.db.models.fields.TextField')()),
            ('public_key', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ssl_certificate', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ca_cert_chain', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('saml', ['LibertyProvider'])

        # Adding model 'LibertyServiceProvider'
        db.create_table('saml_libertyserviceprovider', (
            ('liberty_provider', self.gf('django.db.models.fields.related.OneToOneField')(related_name='service_provider', unique=True, primary_key=True, to=orm['saml.LibertyProvider'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('prefered_assertion_consumer_binding', self.gf('django.db.models.fields.CharField')(default='meta', max_length=4)),
            ('encrypt_nameid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('encrypt_assertion', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('authn_request_signed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('idp_initiated_sso', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attribute_map', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='service_providers', null=True, to=orm['saml.LibertyAttributeMap'])),
            ('default_name_id_format', self.gf('django.db.models.fields.CharField')(default='none', max_length=20)),
            ('accepted_name_id_format', self.gf('authentic2.saml.fields.MultiSelectField')(max_length=31, blank=True)),
            ('ask_user_consent', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('saml', ['LibertyServiceProvider'])

        # Adding model 'LibertyIdentityProvider'
        db.create_table('saml_libertyidentityprovider', (
            ('liberty_provider', self.gf('django.db.models.fields.related.OneToOneField')(related_name='identity_provider', unique=True, primary_key=True, to=orm['saml.LibertyProvider'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('enable_following_policy', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('no_nameid_policy', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requested_name_id_format', self.gf('django.db.models.fields.CharField')(default='none', max_length=20)),
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
            ('attribute_map', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='identity_providers', null=True, to=orm['saml.LibertyAttributeMap'])),
        ))
        db.send_create_signal('saml', ['LibertyIdentityProvider'])

        # Adding model 'LibertyIdentityDump'
        db.create_table('saml_libertyidentitydump', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('identity_dump', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('saml', ['LibertyIdentityDump'])

        # Adding model 'LibertySessionDump'
        db.create_table('saml_libertysessiondump', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('django_session_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('session_dump', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('saml', ['LibertySessionDump'])

        # Adding model 'LibertyManageDump'
        db.create_table('saml_libertymanagedump', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('django_session_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('manage_dump', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('saml', ['LibertyManageDump'])

        # Adding model 'LibertyArtifact'
        db.create_table('saml_libertyartifact', (
            ('creation', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('artifact', self.gf('django.db.models.fields.CharField')(max_length=40, primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('django_session_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('provider_id', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('saml', ['LibertyArtifact'])

        # Adding model 'LibertyAssertion'
        db.create_table('saml_libertyassertion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assertion_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('provider_id', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('session_index', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('assertion', self.gf('django.db.models.fields.TextField')()),
            ('creation', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('saml', ['LibertyAssertion'])

        # Adding model 'LibertyFederation'
        db.create_table('saml_libertyfederation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('idp_id', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('sp_id', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('name_id_qualifier', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('name_id_format', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name_id_content', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_id_sp_name_qualifier', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name_id_sp_provided_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('saml', ['LibertyFederation'])

        # Adding unique constraint on 'LibertyFederation', fields ['name_id_qualifier', 'name_id_format', 'name_id_content', 'name_id_sp_name_qualifier']
        db.create_unique('saml_libertyfederation', ['name_id_qualifier', 'name_id_format', 'name_id_content', 'name_id_sp_name_qualifier'])

        # Adding model 'LibertySession'
        db.create_table('saml_libertysession', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('django_session_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('session_index', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('provider_id', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('federation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['saml.LibertyFederation'], null=True)),
            ('assertion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['saml.LibertyAssertion'], null=True)),
            ('name_id_qualifier', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('name_id_format', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('name_id_content', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_id_sp_name_qualifier', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('creation', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('saml', ['LibertySession'])

        # Adding model 'LibertySessionSP'
        db.create_table('saml_libertysessionsp', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('django_session_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('session_index', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('federation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['saml.LibertyFederation'])),
        ))
        db.send_create_signal('saml', ['LibertySessionSP'])

        # Adding model 'KeyValue'
        db.create_table('saml_keyvalue', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=40, primary_key=True)),
            ('value', self.gf('authentic2.saml.fields.PickledObjectField')()),
        ))
        db.send_create_signal('saml', ['KeyValue'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'LibertyFederation', fields ['name_id_qualifier', 'name_id_format', 'name_id_content', 'name_id_sp_name_qualifier']
        db.delete_unique('saml_libertyfederation', ['name_id_qualifier', 'name_id_format', 'name_id_content', 'name_id_sp_name_qualifier'])

        # Deleting model 'LibertyAttributeMap'
        db.delete_table('saml_libertyattributemap')

        # Deleting model 'LibertyAttributeMapping'
        db.delete_table('saml_libertyattributemapping')

        # Deleting model 'LibertyProvider'
        db.delete_table('saml_libertyprovider')

        # Deleting model 'LibertyServiceProvider'
        db.delete_table('saml_libertyserviceprovider')

        # Deleting model 'LibertyIdentityProvider'
        db.delete_table('saml_libertyidentityprovider')

        # Deleting model 'LibertyIdentityDump'
        db.delete_table('saml_libertyidentitydump')

        # Deleting model 'LibertySessionDump'
        db.delete_table('saml_libertysessiondump')

        # Deleting model 'LibertyManageDump'
        db.delete_table('saml_libertymanagedump')

        # Deleting model 'LibertyArtifact'
        db.delete_table('saml_libertyartifact')

        # Deleting model 'LibertyAssertion'
        db.delete_table('saml_libertyassertion')

        # Deleting model 'LibertyFederation'
        db.delete_table('saml_libertyfederation')

        # Deleting model 'LibertySession'
        db.delete_table('saml_libertysession')

        # Deleting model 'LibertySessionSP'
        db.delete_table('saml_libertysessionsp')

        # Deleting model 'KeyValue'
        db.delete_table('saml_keyvalue')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        'saml.libertyattributemap': {
            'Meta': {'object_name': 'LibertyAttributeMap'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'saml.libertyattributemapping': {
            'Meta': {'object_name': 'LibertyAttributeMapping'},
            'attribute_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'attribute_value_format': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['saml.LibertyAttributeMap']"}),
            'source_attribute_name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
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
            'allow_create': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attribute_map': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'identity_providers'", 'null': 'True', 'to': "orm['saml.LibertyAttributeMap']"}),
            'binding_for_sso_response': ('django.db.models.fields.CharField', [], {'default': "'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact'", 'max_length': '60'}),
            'enable_binding_for_sso_response': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_following_policy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_http_method_for_defederation_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_http_method_for_slo_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'http_method_for_defederation_request': ('django.db.models.fields.IntegerField', [], {'default': '5', 'max_length': '60'}),
            'http_method_for_slo_request': ('django.db.models.fields.IntegerField', [], {'default': '4', 'max_length': '60'}),
            'liberty_provider': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'identity_provider'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['saml.LibertyProvider']"}),
            'no_nameid_policy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requested_name_id_format': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '20'}),
            'user_consent': ('django.db.models.fields.CharField', [], {'default': "'urn:oasis:names:tc:SAML:2.0:consent:current-implicit'", 'max_length': '60'}),
            'want_authn_request_signed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'want_force_authn_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'want_is_passive_authn_request': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40', 'blank': 'True'}),
            'protocol_conformance': ('django.db.models.fields.IntegerField', [], {'max_length': '10'}),
            'public_key': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ssl_certificate': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'saml.libertyserviceprovider': {
            'Meta': {'object_name': 'LibertyServiceProvider'},
            'accepted_name_id_format': ('authentic2.saml.fields.MultiSelectField', [], {'max_length': '31', 'blank': 'True'}),
            'ask_user_consent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'attribute_map': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'service_providers'", 'null': 'True', 'to': "orm['saml.LibertyAttributeMap']"}),
            'authn_request_signed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default_name_id_format': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '20'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'encrypt_assertion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'encrypt_nameid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'idp_initiated_sso': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'liberty_provider': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'service_provider'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['saml.LibertyProvider']"}),
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
