from django.conf.urls import patterns, include, url
from views import menuView,accountView,LogoutView

urlpatterns = patterns('',
    # Examples:
    #url(r'login^$', 'account.views.login', name='login'),
    url(r'^$',menuView,name='admin_menu'),
    url(r'settings/$',accountView,name='admin_account_menu'),
    url(r'^logout/$', LogoutView.as_view(), name='admin_account_logout'),
    #url(r'admin/menu^$','account.views.admin_menu',name='admin_menu')
)