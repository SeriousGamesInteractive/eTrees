from django.conf.urls import patterns, include, url
from .views import (requestDeleteAsset, requestSaveTree, requestDeleteLibrary, 
    requestLoadTree, requestContentAsset, requestDeleteNode, requestSearchNode,
    requestPublishProject,requestAddUserStory,requestRemoveUserStory,requestUsersOnStories,
    requestUserInviteStory,requestNodeData,requestCompleteStoryUsers,
    requestSessionGameUsers,requestDeletePublishStory, requestCopyNode, requestDeleteCategory)

urlpatterns = patterns('',
    # API access points:
    url(r'requestDeleteAsset/$', requestDeleteAsset, name='api_delete_asset'),
    url(r'requestDeleteLibrary/$', requestDeleteLibrary, name='api_delete_library'),
    url(r'requestDeleteCategory/$', requestDeleteCategory, name='api_delete_category'),
    url(r'requestDeleteNode/$', requestDeleteNode, name='api_delete_node'),
    url(r'requestCopyNode/$', requestCopyNode, name='api_copy_node'),
    url(r'requestSaveTree/$', requestSaveTree, name='api_save_tree'),
    url(r'requestLoadTree/$', requestLoadTree, name='api_load_tree'),
    url(r'requestContentAsset/$', requestContentAsset, name='api_content_asset'),
    url(r'requestSearchNode/$', requestSearchNode, name='api_search_node'),
    url(r'requestPublishProject/$',requestPublishProject, name='api_request_publish'),
    url(r'requestAddUserStory/$',requestAddUserStory, name='api_request_add_user_story'),
    url(r'requestRemoveUserStory/$',requestRemoveUserStory, name='api_request_remove_user_story'),
    url(r'requestUsersOnStories/$',requestUsersOnStories, name='api_request_users_on_story'),
    url(r'requestUserInviteStory/$',requestUserInviteStory, name='api_request_user_invited'),
    url(r'requestNodeData/$',requestNodeData, name='api_request_node_data'),
    url(r'requestCompleteStoryUsers/$',requestCompleteStoryUsers,name='api_request_complete_story_user'),
    url(r'requestSessionGameUsers/$',requestSessionGameUsers,name='api_request_session_user'),
    url(r'requestDeletePublishStory/$',requestDeletePublishStory, name='api_request_delete_publishstory')
)