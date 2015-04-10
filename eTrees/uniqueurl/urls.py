__author__ = 'Felix Rubio (at) SGI'
 
from django.conf.urls.defaults import patterns, url
from .views import get_file, generate_url, result_trainee
urlpatterns = patterns('',
    
    url(r'^geturl/(?P<media_id>\d+)$', generate_url, name='unique_geturl'),
    url(r'^result/(?P<code>.+)/(?P<idsession>\d+)$', result_trainee, name='result_story'),
    url(r'^(?P<code>.+)$', get_file, name='unique_getfile'),
)