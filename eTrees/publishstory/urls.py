from django.conf.urls import patterns, include, url
from .views import PublishMenuView, PublishNewUserView, PublishInviteUserView, PublishReporting

urlpatterns = patterns('',
    # Examples:
    #url(r'login^$', 'account.views.login', name='login'),
    url(r'pusblish-menu/$',PublishMenuView,name='admin_publish_menu'),
    url(r'pusblish-invite-user/$',PublishInviteUserView,name='admin_publish_invite_user'),
    url(r'pusblish-new-user/$',PublishNewUserView,name='admin_publish_new_user'),
    url(r'pusblish-reporting/$',PublishReporting,name='admin_publish_reporting'),
    
    #url(r'admin/menu^$','account.views.admin_menu',name='admin_menu')
)