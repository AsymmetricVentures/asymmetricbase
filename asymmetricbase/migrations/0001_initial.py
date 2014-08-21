# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import asymmetricbase.fields.textfields
import everdeal.update_cascade
import asymmetricbase.fields.uuidfield
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
        ('auth', '0002_auto_20140821_1352'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedRole',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', asymmetricbase.fields.uuidfield.UUIDField(db_index=True, max_length=40, blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', everdeal.update_cascade.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuditEntry',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('log_type', models.CharField(choices=[(1, 'model'), (2, 'view'), (3, 'login'), (4, 'assign'), (5, 'other')], max_length=10)),
                ('access_type', models.CharField(choices=[(1, 'read'), (2, 'write'), (3, 'add'), (4, 'grant'), (5, 'assign'), (6, 'unassign'), (7, 'view'), (8, 'other')], max_length=10)),
                ('time_stamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Time Stamp', auto_now=True)),
                ('user_id', models.IntegerField(null=True, blank=True, verbose_name='UserBase.ID')),
                ('ip', models.IPAddressField(verbose_name='Origin IP')),
                ('message', models.TextField(verbose_name='change message', blank=True)),
                ('model_name', models.CharField(null=True, max_length=256, blank=True, verbose_name='for LogEntryType == MODEL')),
                ('view_name', models.CharField(null=True, max_length=256, blank=True, verbose_name='for LogEntryType == VIEW')),
                ('success', models.NullBooleanField()),
            ],
            options={
                'ordering': ('time_stamp',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultGroup',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', asymmetricbase.fields.uuidfield.UUIDField(db_index=True, max_length=40, blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('identifier', models.IntegerField(unique=True)),
                ('group', everdeal.update_cascade.ForeignKey(to='auth.Group')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultRole',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', asymmetricbase.fields.uuidfield.UUIDField(db_index=True, max_length=40, blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('identifier', models.IntegerField(unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('level', models.IntegerField()),
                ('pathname', models.CharField(max_length=255)),
                ('lineno', models.IntegerField()),
                ('msg', models.TextField(blank=True)),
                ('args', models.TextField(blank=True)),
                ('exc_info', models.TextField(blank=True)),
                ('func', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NamedGroupSet',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', asymmetricbase.fields.uuidfield.UUIDField(db_index=True, max_length=40, blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('identifier', models.IntegerField()),
                ('group_set', models.ManyToManyField(to='auth.Group')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ObjectContent',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('time_stamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='action time', auto_now=True)),
                ('content_in_json', models.TextField(verbose_name='Object Content in JSON format')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', asymmetricbase.fields.uuidfield.UUIDField(db_index=True, max_length=40, blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('name', asymmetricbase.fields.textfields.LongNameField(max_length=285)),
                ('defined_for', everdeal.update_cascade.ForeignKey(to='contenttypes.ContentType')),
                ('permission_group', everdeal.update_cascade.OneToOneField(to='auth.Group')),
                ('permitted_groups', models.ManyToManyField(related_name='possible_roles', to='auth.Group')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoleTransfer',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', asymmetricbase.fields.uuidfield.UUIDField(db_index=True, max_length=40, blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('date_updated', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('role_from', everdeal.update_cascade.ForeignKey(related_name='+', to='asymmetricbase.Role')),
                ('role_to', everdeal.update_cascade.ForeignKey(related_name='+', to='asymmetricbase.Role')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TraceEntry',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('get', models.TextField(blank=True)),
                ('msg', models.TextField(blank=True)),
                ('exc_info', models.TextField(blank=True)),
                ('method', models.CharField(default='', max_length=10, blank=True)),
                ('user', models.CharField(default='', max_length=100, blank=True)),
                ('request_meta', models.TextField(default='', blank=True)),
                ('request_data', models.TextField(default='', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('name', 'defined_for')]),
        ),
        migrations.AddField(
            model_name='defaultrole',
            name='role',
            field=everdeal.update_cascade.ForeignKey(to='asymmetricbase.Role'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='auditentry',
            name='object_content',
            field=everdeal.update_cascade.ForeignKey(null=True, to='asymmetricbase.ObjectContent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assignedrole',
            name='role',
            field=everdeal.update_cascade.ForeignKey(related_name='assignments', to='asymmetricbase.Role'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assignedrole',
            name='user',
            field=everdeal.update_cascade.ForeignKey(related_name='assigned_roles', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='NotRoleGroupProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='OnlyRoleGroupProxy',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.group',),
        ),
    ]
