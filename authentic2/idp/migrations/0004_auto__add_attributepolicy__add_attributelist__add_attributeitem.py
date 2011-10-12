# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'AttributePolicy'
        db.create_table('idp_attributepolicy', (
            ('filter_source_of_filtered_attributes', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('attribute_filter_for_sso_from_push_sources', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='filter attributes of push sources with list', null=True, to=orm['idp.AttributeList'])),
            ('output_namespace', self.gf('django.db.models.fields.CharField')(default=('Default', 'Default'), max_length=100)),
            ('forward_attributes_from_push_sources', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('output_name_format', self.gf('django.db.models.fields.CharField')(default=('urn:oasis:names:tc:SAML:2.0:attrname-format:basic', 'SAMLv2 BASIC'), max_length=100)),
            ('map_attributes_of_filtered_attributes', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('map_attributes_from_push_sources', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('attribute_list_for_sso_from_pull_sources', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='attributes from pull sources', null=True, to=orm['idp.AttributeList'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('send_error_and_no_attrs_if_missing_required_attrs', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('idp', ['AttributePolicy'])

        # Adding M2M table for field source_filter_for_sso_from_push_sources on 'AttributePolicy'
        db.create_table('idp_attributepolicy_source_filter_for_sso_from_push_sources', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('attributepolicy', models.ForeignKey(orm['idp.attributepolicy'], null=False)),
            ('attributesource', models.ForeignKey(orm['attribute_aggregator.attributesource'], null=False))
        ))
        db.create_unique('idp_attributepolicy_source_filter_for_sso_from_push_sources', ['attributepolicy_id', 'attributesource_id'])

        # Adding model 'AttributeList'
        db.create_table('idp_attributelist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('idp', ['AttributeList'])

        # Adding M2M table for field attributes on 'AttributeList'
        db.create_table('idp_attributelist_attributes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('attributelist', models.ForeignKey(orm['idp.attributelist'], null=False)),
            ('attributeitem', models.ForeignKey(orm['idp.attributeitem'], null=False))
        ))
        db.create_unique('idp_attributelist_attributes', ['attributelist_id', 'attributeitem_id'])

        # Adding model 'AttributeItem'
        db.create_table('idp_attributeitem', (
            ('attribute_name', self.gf('django.db.models.fields.CharField')(default=('OpenLDAProotDSE', 'OpenLDAProotDSE'), max_length=100)),
            ('output_namespace', self.gf('django.db.models.fields.CharField')(default=('Default', 'Default'), max_length=100)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('output_name_format', self.gf('django.db.models.fields.CharField')(default=('urn:oasis:names:tc:SAML:2.0:attrname-format:basic', 'SAMLv2 BASIC'), max_length=100)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['attribute_aggregator.AttributeSource'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('idp', ['AttributeItem'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'AttributePolicy'
        db.delete_table('idp_attributepolicy')

        # Removing M2M table for field source_filter_for_sso_from_push_sources on 'AttributePolicy'
        db.delete_table('idp_attributepolicy_source_filter_for_sso_from_push_sources')

        # Deleting model 'AttributeList'
        db.delete_table('idp_attributelist')

        # Removing M2M table for field attributes on 'AttributeList'
        db.delete_table('idp_attributelist_attributes')

        # Deleting model 'AttributeItem'
        db.delete_table('idp_attributeitem')
    
    
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
        'idp.userconsentattributes': {
            'Meta': {'object_name': 'UserConsentAttributes'},
            'attributes': ('django.db.models.fields.TextField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'idp.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'postal_address': ('django.db.models.fields.TextField', [], {'max_length': '255', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }
    
    complete_apps = ['idp']
