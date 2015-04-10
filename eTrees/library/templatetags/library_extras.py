from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

@register.filter
@stringfilter
def createurl(value):
	"""Removes the home/etrees/directory to get the url"""
	if value.find("eTrees") == -1:
		return value
	else:
		return value[value.find("eTrees")+len("eTrees"):]