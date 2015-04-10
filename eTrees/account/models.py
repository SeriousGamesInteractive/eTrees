from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Trainer(models.Model):
	user = models.ForeignKey(User,unique=True, related_name ='trainer_user')
	admin = models.ForeignKey(User, related_name = 'admin_user')
	trainer = models.BooleanField()
	
