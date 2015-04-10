# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserGame'
        db.create_table(u'publishstory_usergame', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('username', self.gf('django.db.models.fields.CharField')(default='user', unique=True, max_length=20)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=70)),
            ('datecreation', self.gf('django.db.models.fields.DateField')()),
            ('sex', self.gf('django.db.models.fields.CharField')(default='m', max_length=1)),
            ('personid', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('additionalinfo', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'publishstory', ['UserGame'])

        # Adding M2M table for field user on 'UserGame'
        m2m_table_name = db.shorten_name(u'publishstory_usergame_user')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('usergame', models.ForeignKey(orm[u'publishstory.usergame'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['usergame_id', 'user_id'])

        # Adding model 'ProjectValoration'
        db.create_table(u'publishstory_projectvaloration', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('url_hash', self.gf('django.db.models.fields.CharField')(default='Url', max_length=100, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publishstory.UserGame'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['createstory.Project'])),
        ))
        db.send_create_signal(u'publishstory', ['ProjectValoration'])

        # Adding model 'SessionUser'
        db.create_table(u'publishstory_sessionuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('projectValoration', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publishstory.ProjectValoration'])),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('startTime', self.gf('django.db.models.fields.DateTimeField')()),
            ('finishTime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'publishstory', ['SessionUser'])

        # Adding model 'CommentUser'
        db.create_table(u'publishstory_commentuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sessionuser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publishstory.SessionUser'])),
            ('comment', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('question', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
        ))
        db.send_create_signal(u'publishstory', ['CommentUser'])

        # Adding model 'UserNodeSelection'
        db.create_table(u'publishstory_usernodeselection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sessionUser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publishstory.SessionUser'])),
            ('attributeSelected', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['createstory.Node'])),
            ('depth', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'publishstory', ['UserNodeSelection'])


    def backwards(self, orm):
        # Deleting model 'UserGame'
        db.delete_table(u'publishstory_usergame')

        # Removing M2M table for field user on 'UserGame'
        db.delete_table(db.shorten_name(u'publishstory_usergame_user'))

        # Deleting model 'ProjectValoration'
        db.delete_table(u'publishstory_projectvaloration')

        # Deleting model 'SessionUser'
        db.delete_table(u'publishstory_sessionuser')

        # Deleting model 'CommentUser'
        db.delete_table(u'publishstory_commentuser')

        # Deleting model 'UserNodeSelection'
        db.delete_table(u'publishstory_usernodeselection')


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
        },
        u'publishstory.commentuser': {
            'Meta': {'object_name': 'CommentUser'},
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sessionuser': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publishstory.SessionUser']"})
        },
        u'publishstory.projectvaloration': {
            'Meta': {'object_name': 'ProjectValoration'},
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['createstory.Project']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'url_hash': ('django.db.models.fields.CharField', [], {'default': "'Url'", 'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publishstory.UserGame']"})
        },
        u'publishstory.sessionuser': {
            'Meta': {'object_name': 'SessionUser'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'finishTime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'projectValoration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publishstory.ProjectValoration']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'startTime': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'publishstory.usergame': {
            'Meta': {'object_name': 'UserGame'},
            'additionalinfo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'datecreation': ('django.db.models.fields.DateField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '70'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'personid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '1'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'default': "'user'", 'unique': 'True', 'max_length': '20'})
        },
        u'publishstory.usernodeselection': {
            'Meta': {'object_name': 'UserNodeSelection'},
            'attributeSelected': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'depth': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['createstory.Node']"}),
            'sessionUser': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publishstory.SessionUser']"})
        }
    }

    complete_apps = ['publishstory']