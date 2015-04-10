from django.conf.urls import patterns, include, url
from .views import StoryBuilder, EditStoryMenuView, EditStoryView, ViewerStory, CreateStoryForm, CreateCopyStory, EditStoryForm, ResultTemplate

urlpatterns = patterns('',
    # Examples:
    #url(r'login^$', 'account.views.login', name='login'),
    url(r'stories-menu/$',EditStoryMenuView,name='admin_edit_story_menu'),
    url(r'edit-story/(?P<story>\d+)/$',EditStoryForm,name='edit_story_form'),    
    url(r'story-builder/(?P<story>\d+)/(?P<node>\d+)/$',StoryBuilder,name="admin_storybuilder"),
    url(r'viewer-story/(?P<story>\d+)/$',ViewerStory,name="admin_viewer"),
    url(r'create-story/$',CreateStoryForm,name='create_story'),
    url(r'copy-story/(?P<story>\d+)/$',CreateCopyStory,name='create_copy_story'),
    url(r'story/(?P<story>\d+)/$',EditStoryView,name='admin_edit_story'),
    url(r'temp-result/(?P<story>\d+)/$', ResultTemplate, name='admin_result_template' ),
    #url(r'admin/menu^$','account.views.admin_menu',name='admin_menu')
)