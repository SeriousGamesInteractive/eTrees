#-*-coding" utf-8 -*-
from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.auth.models import User

#Auxiliar method to save in the correct path the images and files
def get_path(instance,filename): 
	return filename

def graphic_path(self,image):
	url = "/assets/%s/graphics/%s.%s" % (self.id,self.id, image.name[-4:])
	return url

# Create your models here.
class ResourcesLibrary(TimeStampedModel):
	name = models.CharField(max_length=40, blank=False)
	description = models.CharField(max_length=40, blank=False)
	inUse = models.IntegerField(default=0)
	user = models.ManyToManyField(User)
	owner_id = models.IntegerField()

#Declaration of the database models for the assets    
class AudioAsset(TimeStampedModel):
	name = models.CharField(max_length=150, blank=False)
	audioType = models.CharField(max_length=10,blank=False,default="music")
	pathFile =models.FileField(upload_to=get_path,blank=True)
	library = models.ForeignKey(ResourcesLibrary)

class GraphicAsset(TimeStampedModel):
	name = models.CharField(max_length=150, blank=False)
	pathFile = models.FileField(upload_to=get_path,blank=True)
	library = models.ForeignKey(ResourcesLibrary)

class AnimationAsset(TimeStampedModel):
	name = models.CharField(max_length=150, blank=False)
	pathFile =models.FileField(upload_to=get_path,blank=True)
	library = models.ForeignKey(ResourcesLibrary)

class BackgroundAsset(TimeStampedModel):
	name = models.CharField(max_length=150, blank=False)
	pathFile = models.FileField(upload_to=get_path,blank=True)
	library = models.ForeignKey(ResourcesLibrary)
