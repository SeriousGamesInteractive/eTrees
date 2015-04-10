from django.conf.urls import patterns, include, url
from views import LibraryView, NewLibraryView

urlpatterns = patterns('',
    url(r'libraries/$',LibraryView,name='admin_library'),
    url(r'newlibrary/(?P<library>\d+)/$',NewLibraryView,name='admin_newlibrary'),
)