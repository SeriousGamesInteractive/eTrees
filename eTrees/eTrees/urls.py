from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
from account.views import loginView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:

    url(r'^login/$',loginView,name="login"),
    url(r'^crossdomain.xml$','flashpolicies.views.simple',{'domains': ['*']}),
    #url(r'^$', 'eTrees.views.home', name='home'),
    url(r'^', include('account.urls')),
    url(r'^project/',include('createstory.urls')),
    url(r'^project/',include('library.urls')),
    url(r'^project/',include('publishstory.urls')),
    url(r'^game/',include('uniqueurl.urls')),
    url(r'^game/',include('game.urls')),
    #url(r'^$', 'eTrees.views.home', name='home'),
    url(r'^api/', include('api.urls')),
    url(r'^tree/', include('tree.urls')),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}), 
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),


)
urlpatterns += (url(r'^admin/django-ses/', include('django_ses.urls')),)
urlpatterns += staticfiles_urlpatterns()