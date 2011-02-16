# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'DistinguishedName'
        db.create_table('auth2_ssl_distinguishedname', (
            ('c', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('cn', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('g', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('i', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('l', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('o', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('s', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('t', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('ou', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('st', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('d', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('auth2_ssl', ['DistinguishedName'])

        # Adding model 'ClientCertificate'
        db.create_table('auth2_ssl_clientcertificate', (
            ('cert', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('serial', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subject', null=True, to=orm['auth2_ssl.DistinguishedName'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issuer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='issuer', null=True, to=orm['auth2_ssl.DistinguishedName'])),
        ))
        db.send_create_signal('auth2_ssl', ['ClientCertificate'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'DistinguishedName'
        db.delete_table('auth2_ssl_distinguishedname')

        # Deleting model 'ClientCertificate'
        db.delete_table('auth2_ssl_clientcertificate')
    
    
    models = {
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
        'auth2_ssl.clientcertificate': {
            'Meta': {'object_name': 'ClientCertificate'},
            'cert': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'issuer'", 'null': 'True', 'to': "orm['auth2_ssl.DistinguishedName']"}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subject'", 'null': 'True', 'to': "orm['auth2_ssl.DistinguishedName']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'auth2_ssl.distinguishedname': {
            'Meta': {'object_name': 'DistinguishedName'},
            'c': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'cn': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'd': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'g': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'i': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'l': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'o': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'ou': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            's': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'st': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            't': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['auth2_ssl']
