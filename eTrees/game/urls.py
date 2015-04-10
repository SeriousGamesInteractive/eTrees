from django.conf.urls import patterns, include, url
from .views import requestGame

urlpatterns = patterns('',
    url(r'^story/(?P<code>[a-zA-Z0-9*=]{12})$', requestGame, name='start_game'),

)