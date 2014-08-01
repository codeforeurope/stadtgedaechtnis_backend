from stadtgedaechtnis_backend.services.views.assets import AssetWithSources

__author__ = 'jpi'

from django.conf.urls import patterns, url
from stadtgedaechtnis_backend.services.views.stories import *

urlpatterns = patterns(
    '',
    url(r'^title/$', StoryListWithTitle.as_view(), name="get-all-stories-with-title"),
    url(r'^$', StoryListCreate.as_view(), name="get-all-stories"),
    url(r'^(?P<pk>\d+)/$', StoryWithAssets.as_view(), name="get-story"),
    url(r'^(?P<pk>\d+)/image/$', StoryWithAssetImage.as_view(), name="get-story-image"),
    url(r'^(?P<pk>\d+)/assets/$', AssetWithSources.as_view(), name="get-story-with-asset"),
    url(r'^title/(?P<query>[^/]+)/title/$', StoryQueryWithTitle.as_view(), name="query-story-title"),
    url(r'^text/(?P<query>[^/]+)/title/$', StoryTextQueryWithTitle.as_view(), name="query-story-text"),
    url(r'^title/(?P<query>[^/]+)/$', StoryTitleQuery.as_view(), name="query-story-title-list"),
    url(r'^text/(?P<query>[^/]+)/$', StoryTextAndTitleQuery.as_view(), name="query-story-text-list"),
)