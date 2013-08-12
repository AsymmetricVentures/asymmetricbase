# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import absolute_import, division, print_function, unicode_literals

from django.core.management.base import BaseCommand
from django.db.models import get_models
from django.db import connections#, transaction
#from django.core.management.color import color_style
from django.db.backends.util import truncate_name

from south.db.generic import DatabaseOperations

class Command(BaseCommand):
	help = "Print the SQL for recreating the foreign keys"
	
	def handle(self, *args, **options):
		connection_name = options.get('database', 'default')
		connection = connections[connection_name]
		
		d = DatabaseOperations('default')
		qn = connection.ops.quote_name
		
		pending_references = {}
		
		for model in get_models():
			opts = model._meta
			#db_table = opts.db_table
			if not opts.managed or opts.proxy:
				continue
			
			d._fill_constraint_cache(connection_name, opts.db_table)
			
			for f in opts.local_fields:
				col_type = f.db_type(connection = connection)
				if col_type is None:
					continue
				if f.rel:
					#fkey_name = '{}_{}_fkey'.format(db_table, f.column)
					
					pending_references.setdefault(f.rel.to, []).append((model, f))
		
		drops = []
		adds = []
		
		for model in get_models():
			table_name = model._meta.db_table
			
			for col, constraints in d.lookup_constraint(connection_name, table_name):
				for kind, cname in constraints:
					if kind == 'FOREIGN KEY':
						drops.append(d.delete_foreign_key_sql % {'table' : qn(table_name), 'constraint' : qn(cname)} + ';')
			
			opts = model._meta
			
			if model in pending_references:
				for rel_class, f in pending_references[model]:
					rel_opts = rel_class._meta
					r_table = rel_opts.db_table
					r_col = f.column
					#table = opts.db_table
					col = opts.get_field(f.rel.field_name).column
					
					r_name = '{}_refs_{}_{}_fkey'.format(r_col, table_name, col)
					r_name = truncate_name(r_name, connection.ops.max_name_length())
					
					adds.append('ALTER TABLE {} ADD CONSTRAINT {} FOREIGN KEY ({}) REFERENCES {} ({}){};'.format(qn(r_table), qn(r_name), qn(r_col), qn(table_name), qn(col), connection.ops.deferrable_sql()))
					
				del pending_references[model]
		
		for sql in drops + adds:
			if int(options['verbosity']) > 1:
				print(sql)
			connection.cursor().execute(sql)
		
