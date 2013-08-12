#@PydevCodeAnalysisIgnore
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db.utils import DatabaseError

class Migration(SchemaMigration):

	def forwards(self, orm):
#		try:
#			db.delete_table('asymmetricbase_logentry')
#		except DatabaseError:
#			pass
		
		# Adding model 'ObjectContent'
		db.create_table('asymmetricbase_objectcontent', (
			('id', self.gf('django.db.models.fields.AutoField')(primary_key = True)),
			('time_stamp', self.gf('django.db.models.fields.DateTimeField')(default = datetime.datetime.now, auto_now = True, blank = True)),
			('content_in_json', self.gf('django.db.models.fields.TextField')()),
		))
		db.send_create_signal('asymmetricbase', ['ObjectContent'])

		# Adding model 'AuditEntry'
		db.create_table('asymmetricbase_auditentry', (
			('id', self.gf('django.db.models.fields.AutoField')(primary_key = True)),
			('log_type', self.gf('django.db.models.fields.CharField')(max_length = 10)),
			('access_type', self.gf('django.db.models.fields.CharField')(max_length = 10)),
			('time_stamp', self.gf('django.db.models.fields.DateTimeField')(auto_now = True, blank = True)),
			('user_id', self.gf('django.db.models.fields.IntegerField')(null = True, blank = True)),
			('ip', self.gf('django.db.models.fields.IPAddressField')(max_length = 15)),
			('message', self.gf('django.db.models.fields.TextField')(blank = True)),
			('model_name', self.gf('django.db.models.fields.CharField')(max_length = 256, null = True, blank = True)),
			('view_name', self.gf('django.db.models.fields.CharField')(max_length = 256, null = True, blank = True)),
			('success', self.gf('django.db.models.fields.NullBooleanField')(null = True, blank = True)),
			('object_content', self.gf('django.db.models.fields.related.ForeignKey')(to = orm['asymmetricbase.ObjectContent'], null = True)),
		))
		db.send_create_signal('asymmetricbase', ['AuditEntry'])

		# Adding model 'LogEntry'
		db.create_table('asymmetricbase_logentry', (
			('id', self.gf('django.db.models.fields.AutoField')(primary_key = True)),
			('date_created', self.gf('django.db.models.fields.DateTimeField')(default = datetime.datetime.now)),
			('level', self.gf('django.db.models.fields.IntegerField')()),
			('pathname', self.gf('django.db.models.fields.CharField')(max_length = 255)),
			('lineno', self.gf('django.db.models.fields.IntegerField')()),
			('msg', self.gf('django.db.models.fields.TextField')(blank = True)),
			('args', self.gf('django.db.models.fields.TextField')(blank = True)),
			('exc_info', self.gf('django.db.models.fields.TextField')(blank = True)),
			('func', self.gf('django.db.models.fields.TextField')(blank = True)),
		))
		db.send_create_signal('asymmetricbase', ['LogEntry'])


	def backwards(self, orm):
		# Deleting model 'ObjectContent'
		db.delete_table('asymmetricbase_objectcontent')

		# Deleting model 'AuditEntry'
		db.delete_table('asymmetricbase_auditentry')

		# Deleting model 'LogEntry'
		db.delete_table('asymmetricbase_logentry')

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
			'time_stamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
	}

	complete_apps = ['asymmetricbase']
