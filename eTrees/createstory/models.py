#-*-coding" utf-8 -*-
from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.auth.models import User
from library.models import ResourcesLibrary

#Auxiliar method to save in the correct path the images and files
def get_path(instance,filename): 
	return filename

# Create your models here.
class Project(TimeStampedModel):
	name = models.CharField(max_length=80, blank=False)
	topic = models.CharField(max_length = 255, blank = True)
	activate = models.IntegerField() 
	description = models.CharField(max_length = 255)
	reflective = models.TextField()
	color_theme = models.CharField(max_length=10,default='#000000')
	resourceslibrary = models.ManyToManyField(ResourcesLibrary)
	canPublish = models.BooleanField(default=False)
	user = models.ManyToManyField(User)
	owner_id = models.IntegerField()
	next_button = models.CharField(max_length = 40)

	'''
	System to show or not show the stories in the administration page and
	for the end user.
	'''
	def activateUnpublish(self):
		self.activate = 0
		self.save()

	def activatePublish(self):
		self.activate = 1
		self.save()

	def deactivateUnpublish(self):
		self.activate = 2
		self.save()

	def deactivatePublish(self):
		self.activate = 3
		self.save()



class Category(models.Model):
	project = models.ForeignKey(Project)
	name = models.CharField(max_length=100)
	maxvalue = models.IntegerField()
	minvalue = models.IntegerField()
	description = models.TextField()
	
class Node(models.Model):
	name = models.CharField(max_length=150,blank=False)
	description = models.CharField(max_length=255,blank=True)
	type = models.IntegerField(default=0) # 0 - normal node. 1 - Initial. 2 - End node
	project = models.ForeignKey(Project)
	color_option = models.CharField(max_length=10,default='#000000')
	options = models.IntegerField(blank=True,default=0)
	xmlFile = models.FileField(upload_to=get_path,blank=True)
	imgFile = models.CharField(max_length=100,blank=True,default="")

class Attribute(models.Model):
	node = models.ForeignKey(Node)
	idAttribute = models.CharField(max_length=5,default="")
	active = models.BooleanField(default=False)

class ReportCategory(models.Model):
	attribute = models.ForeignKey(Attribute)
	name = models.CharField(max_length=100)	
	value = models.IntegerField()

class ClosureTable(models.Model):
	descendant_id = models.IntegerField(default=0, blank=True)
	attribute_id = models.CharField(max_length=10, default="")
	node = models.ForeignKey(Node)
	connected = models.BooleanField(default=False)


