#@PydevCodeAnalysisIgnore
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TraceEntry.method'
        db.add_column('asymmetricbase_traceentry', 'method',
                      self.gf('django.db.models.fields.CharField')(default = '', max_length = 10, blank = True),
                      keep_default = False)

        # Adding field 'TraceEntry.user'
        db.add_column('asymmetricbase_traceentry', 'user',
                      self.gf('django.db.models.fields.CharField')(default = '', max_length = 100, blank = True),
                      keep_default = False)

        # Adding field 'TraceEntry.request_meta'
        db.add_column('asymmetricbase_traceentry', 'request_meta',
                      self.gf('django.db.models.fields.TextField')(default = '', blank = True),
                      keep_default = False)

        # Adding field 'TraceEntry.request_data'
        db.add_column('asymmetricbase_traceentry', 'request_data',
                      self.gf('django.db.models.fields.TextField')(default = '', blank = True),
                      keep_default = False)


    def backwards(self, orm):
        # Deleting field 'TraceEntry.method'
        db.delete_column('asymmetricbase_traceentry', 'method')

        # Deleting field 'TraceEntry.user'
        db.delete_column('asymmetricbase_traceentry', 'user')

        # Deleting field 'TraceEntry.request_meta'
        db.delete_column('asymmetricbase_traceentry', 'request_meta')

        # Deleting field 'TraceEntry.request_data'
        db.delete_column('asymmetricbase_traceentry', 'request_data')


    models = {
        'asymmetricbase.auditentry': {
            'Meta': {'ordering': "('time_stamp',)", 'object_name': 'AuditEntry'},
            'access_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'log_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'object_content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['asymmetricbase.ObjectContent']", 'null': 'True'}),
            'success': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'view_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'asymmetricbase.logentry': {
            'Meta': {'object_name': 'LogEntry'},
            'args': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'exc_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'func': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'lineno': ('django.db.models.fields.IntegerField', [], {}),
            'msg': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pathname': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'asymmetricbase.objectcontent': {
            'Meta': {'object_name': 'ObjectContent'},
            'content_in_json': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        },
        'asymmetricbase.traceentry': {
            'Meta': {'object_name': 'TraceEntry'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'exc_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'get': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'msg': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'request_data': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'request_meta': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['asymmetricbase']
