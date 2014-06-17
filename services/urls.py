__author__ = 'jpi'

from django.conf.urls import patterns, url

from stadtgedaechtnis_backend.services.views import *
from stadtgedaechtnis_backend.import_entries.views import ImportEntry


urlpatterns = patterns('',
    # TODO: add a mixin for localhost access only
    url(r'^places/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/$', GetNearbyPlacesDBPedia.as_view(),
        name="get-nearby-places"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/$', LocationListNearby.as_view(),
        name="get-locations"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/$', LocationListNearby.as_view(),
        name="get-locations"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/story_count/$',
        LocationListNearbyWithStoryIDs.as_view(), name="get-locations-with-count"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/story_count/$',
        LocationListNearbyWithStoryIDs.as_view(), name="get-locations-with-count"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/title/$',
        LocationListNearbyWithStoryTitle.as_view(), name="get-locations-with-story-title"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/title/$',
        LocationListNearbyWithStoryTitle.as_view(),
        name="get-locations-with-story-title"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/$',
        LocationListNearbyWithStories.as_view(), name="get-locations-with-stories"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/$', LocationListNearbyWithStories.as_view(),
        name="get-locations-with-stories"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/title/image/$',
        LocationListNearbyWithImages.as_view(), name="get-locations-with-stories-image"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/title/image/$',
        LocationListNearbyWithImages.as_view(),
        name="get-locations-with-stories-image"),
    url(r'^locations/(?P<id>\d+)/$', SingleLocation.as_view(),
        name="get-location"),
    url(r'^locations/(?P<id>\d+)/stories/story_count/$', SingleLocationWithStoryIDs.as_view(),
        name="get-location-with-story-count"),
    url(r'^locations/(?P<id>\d+)/stories/title/$', SingleLocationWithStoryTitle.as_view(),
        name="get-location-with-story-title"),
    url(r'^locations/(?P<id>\d+)/stories/$', SingleLocationWithStories.as_view(),
        name="get-location-with-stories"),
    url(r'^locations/(?P<id>\d+)/stories/title/image/$', SingleLocationWithStoriesImage.as_view(),
        name="get-location-with-stories-images"),
    url(r'^locations/$', LocationList.as_view(), name="list-locations"),
    url(r'^locations/stories/story-count/$', LocationListWithStoryIDs.as_view(), name="list-locations-with-id"),
    url(r'^locations/stories/title/$', LocationListWithStories.as_view(), name="list-locations-with-id"),
    url(r'^locations/stories/$', LocationListWithStories.as_view(), name="list-locations-with-stories"),
    url(r'^stories/title/$', StoryListWithTitle.as_view(), name="get-all-stories-with-title"),
    url(r'^stories/$', StorySerializerView.as_view(), name="get-all-stories"),
    url(r'^stories/(?P<id>\d+)/$', StoryWithAssets.as_view(), name="get-story"),
    url(r'^stories/(?P<id>\d+)/image/$', StoryWithAssetImage.as_view(), name="get-story-image"),
    url(r'^stories/title/(?P<query>[^/]+)/title/$', StoryQueryWithTitle.as_view(), name="query-story-title"),
    url(r'^stories/text/(?P<query>[^/]+)/title/$', StoryTextQueryWithTitle.as_view(), name="query-story-text"),
    url(r'^stories/title/(?P<query>[^/]+)/$', StoryTitleQuery.as_view(), name="query-story-title-list"),
    url(r'^stories/text/(?P<query>[^/]+)/$', StoryTextAndTitleQuery.as_view(), name="query-story-text-list"),
    )