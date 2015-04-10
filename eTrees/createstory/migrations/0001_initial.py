# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'createstory_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('modified', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('topic', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('activate', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('reflective', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('color_theme', self.gf('django.db.models.fields.CharField')(default='#000000', max_length=10)),
            ('canPublish', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('owner_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'createstory', ['Project'])

        # Adding M2M table for field resourceslibrary on 'Project'
        m2m_table_name = db.shorten_name(u'createstory_project_resourceslibrary')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm[u'createstory.project'], null=False)),
            ('resourceslibrary', models.ForeignKey(orm[u'library.resourceslibrary'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'resourceslibrary_id'])

        # Adding M2M table for field user on 'Project'
        m2m_table_name = db.shorten_name(u'createstory_project_user')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm[u'createstory.project'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'user_id'])

        # Adding model 'Category'
        db.create_table(u'createstory_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['createstory.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('maxvalue', self.gf('django.db.models.fields.IntegerField')()),
            ('minvalue', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'createstory', ['Category'])

        # Adding model 'Node'
        db.create_table(u'createstory_node', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['createstory.Project'])),
            ('options', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('xmlFile', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('imgFile', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
        ))
        db.send_create_signal(u'createstory', ['Node'])

        # Adding model 'Attribute'
        db.create_table(u'createstory_attribute', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['createstory.Node'])),
            ('idAttribute', self.gf('django.db.models.fields.CharField')(default='', max_length=5)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'createstory', ['Attribute'])

        # Adding model 'ReportCategory'
        db.create_table(u'createstory_reportcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['createstory.Attribute'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'createstory', ['ReportCategory'])

        # Adding model 'ClosureTable'
        db.create_table(u'createstory_closuretable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descendant_id', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('attribute_id', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['createstory.Node'])),
            ('connected', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'createstory', ['ClosureTable'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table(u'createstory_project')

        # Removing M2M table for field resourceslibrary on 'Project'
        db.delete_table(db.shorten_name(u'createstory_project_resourceslibrary'))

        # Removing M2M table for field user on 'Project'
        db.delete_table(db.shorten_name(u'createstory_project_user'))

        # Deleting model 'Category'
        db.delete_table(u'createstory_category')

        # Deleting model 'Node'
        db.delete_table(u'createstory_node')

        # Deleting model 'Attribute'
        db.delete_table(u'createstory_attribute')

        # Deleting model 'ReportCategory'
        db.delete_table(u'createstory_reportcategory')

        # Deleting model 'ClosureTable'
        db.delete_table(u'createstory_closuretable')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'createstory.attribute': {
            'Meta': {'object_name': 'Attribute'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idAttribute': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['createstory.Node']"})
        },
        u'createstory.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maxvalue': ('django.db.models.fields.IntegerField', [], {}),
            'minvalue': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['createstory.Project']"})
        },
        u'createstory.closuretable': {
            'Meta': {'object_name': 'ClosureTable'},
            'attribute_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            'connected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'descendant_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['createstory.Node']"})
        },
        u'createstory.node': {
            'Meta': {'object_name': 'Node'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imgFile': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'options': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['createstory.Project']"}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'xmlFile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'createstory.project': {
            'Meta': {'object_name': 'Project'},
            'activate': ('django.db.models.fields.IntegerField', [], {}),
            'canPublish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'color_theme': ('django.db.models.fields.CharField', [], {'default': "'#000000'", 'max_length': '10'}),
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'owner_id': ('django.db.models.fields.IntegerField', [], {}),
            'reflective': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'resourceslibrary': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['library.ResourcesLibrary']", 'symmetrical': 'False'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'})
        },
        u'createstory.reportcategory': {
            'Meta': {'object_name': 'ReportCategory'},
            'attribute': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['createstory.Attribute']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        u'library.resourceslibrary': {
            'Meta': {'object_name': 'ResourcesLibrary'},
            'created': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inUse': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'modified': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'owner_id': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['createstory']