from django.conf.urls import patterns, include, url
from .views import PlaygroundView

urlpatterns = patterns('',
    # Examples:
    #url(r'login^$', 'account.views.login', name='login'),
    url(r'connection/(?P<story>\d+)/$',PlaygroundView,name='tree_connection'),
    #url(r'admin/menu^$','account.views.admin_menu',name='admin_menu')
)