from django.forms import ModelForm
from .models import Project

class CreateStory(ModelForm):
	class Meta:
		model = Project
		fields = ('name','topic','description')
