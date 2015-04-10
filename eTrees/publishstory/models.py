#-*-coding" utf-8 -*-
import datetime
from django.db import models
from django.contrib.auth.models import User
from model_utils.models import TimeStampedModel
from createstory.models import Project,Node

sexChoices = (
    ('m', 'male'),
    ('f','female'),
)

typeUser=(
    (0,'normal_user'),
    (1,'admin'),
)

class UserGame(models.Model):
    name = models.CharField(max_length=20)
    surname = models.CharField(max_length=20)
    username = models.CharField(max_length=20,unique=True,default="user")
    email = models.EmailField(max_length=70, blank = False)
    datecreation = models.DateField()
    sex = models.CharField(max_length=1,default="m",choices=sexChoices)
    personid = models.IntegerField(blank=True,default=0)
    additionalinfo = models.CharField(max_length=255,blank=True)
    user = models.ManyToManyField(User)

    def save(self, *args, **kwargs):
		''' On save, update timestamps '''
		self.datecreation = datetime.datetime.today()
		super(UserGame, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class ProjectValoration(models.Model):
    rating = models.IntegerField(blank=True,default=0)
    completed = models.BooleanField(default=False)
    url_hash = models.CharField(default="Url",blank=True,max_length=100)
    user = models.ForeignKey(UserGame)
    project = models.ForeignKey(Project)
    active = models.BooleanField(default=True)
	
    def __unicode__(self):
        return self.project.name

class SessionUser(models.Model):
    projectValoration = models.ForeignKey(ProjectValoration)
    comment = models.CharField(max_length=255)
    rating = models.IntegerField(default = 0)
    completed = models.BooleanField(default = False)
    startTime = models.DateTimeField()
    finishTime = models.DateTimeField()

    def __unicode__(self):
        return self.projectValoration.user.name

class CommentUser(models.Model):
    sessionuser = models.ForeignKey(SessionUser)
    comment = models.CharField(max_length=255, default = "")
    rating = models.IntegerField(default = 0)
    question = models.CharField(max_length=255, default = "")

class UserNodeSelection(models.Model):
    sessionUser = models.ForeignKey(SessionUser)
    attributeSelected = models.CharField(max_length=5)
    node = models.ForeignKey(Node)
    depth = models.IntegerField()#Show the level of selection
    def __unicode__(self):
        return self.node.name
