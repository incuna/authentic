# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'AttributeSource'
        db.create_table('attribute_aggregator_attributesource', (
            ('namespace', self.gf('django.db.models.fields.CharField')(default=('Default', 'Default'), max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal('attribute_aggregator', ['AttributeSource'])

        # Adding model 'LdapSource'
        db.create_table('attribute_aggregator_ldapsource', (
            ('ldaps', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('certificate', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_auth_backend', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('attributesource_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['attribute_aggregator.AttributeSource'], unique=True, primary_key=True)),
            ('server', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('base', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=389)),
        ))
        db.send_create_signal('attribute_aggregator', ['LdapSource'])

        # Adding model 'UserAliasInSource'
        db.create_table('attribute_aggregator_useraliasinsource', (
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['attribute_aggregator.AttributeSource'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_alias_in_source', to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('attribute_aggregator', ['UserAliasInSource'])

        # Adding unique constraint on 'UserAliasInSource', fields ['name', 'source']
        db.create_unique('attribute_aggregator_useraliasinsource', ['name', 'source_id'])

        # Adding model 'UserAttributeProfile'
        db.create_table('attribute_aggregator_userattributeprofile', (
            ('data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='user_attribute_profile', unique=True, null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('attribute_aggregator', ['UserAttributeProfile'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'AttributeSource'
        db.delete_table('attribute_aggregator_attributesource')

        # Deleting model 'LdapSource'
        db.delete_table('attribute_aggregator_ldapsource')

        # Deleting model 'UserAliasInSource'
        db.delete_table('attribute_aggregator_useraliasinsource')

        # Removing unique constraint on 'UserAliasInSource', fields ['name', 'source']
        db.delete_unique('attribute_aggregator_useraliasinsource', ['name', 'source_id'])

        # Deleting model 'UserAttributeProfile'
        db.delete_table('attribute_aggregator_userattributeprofile')
    
    
    models = {
        'attribute_aggregator.attributesource': {
            'Meta': {'object_name': 'AttributeSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'namespace': ('django.db.models.fields.CharField', [], {'default': "('Default', 'Default')", 'max_length': '100'})
        },
        'attribute_aggregator.ldapsource': {
            'Meta': {'object_name': 'LdapSource', '_ormbases': ['attribute_aggregator.AttributeSource']},
            'attributesource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['attribute_aggregator.AttributeSource']", 'unique': 'True', 'primary_key': 'True'}),
            'base': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'certificate': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'is_auth_backend': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'ldaps': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '389'}),
            'server': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'attribute_aggregator.useraliasinsource': {
            'Meta': {'unique_together': "(('name', 'source'),)", 'object_name': 'UserAliasInSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['attribute_aggregator.AttributeSource']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_alias_in_source'", 'to': "orm['auth.User']"})
        },
        'attribute_aggregator.userattributeprofile': {
            'Meta': {'object_name': 'UserAttributeProfile'},
            'data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'user_attribute_profile'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.User']"})
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
        }
    }
    
    complete_apps = ['attribute_aggregator']
