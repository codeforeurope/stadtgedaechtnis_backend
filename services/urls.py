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
    url(r'^locations/(?P<id>\d+)/$', SingleLocation.as_view(),
        name="get-location"),
    url(r'^locations/(?P<id>\d+)/story_count/$', SingleLocationWithStoryIDs.as_view(),
        name="get-location-with-story-count"),
    url(r'^locations/(?P<id>\d+)/title/$', SingleLocationWithStoryTitle.as_view(),
        name="get-location-with-story-title"),
    url(r'^locations/(?P<id>\d+)/stories/$', SingleLocationWithStories.as_view(),
        name="get-location-with-stories"),
    url(r'^locations/$', LocationList.as_view(), name="list-locations"),
    url(r'^locations/story-count/$', LocationListWithStoryIDs.as_view(), name="list-locations-with-id"),
    url(r'^locations/stories/title/$', LocationListWithStories.as_view(), name="list-locations-with-id"),
    url(r'^locations/stories/$', LocationListWithStories.as_view(), name="list-locations-with-stories"),
    url(r'^stories/title/$', StoryListWithTitle.as_view(), name="get-all-stories-with-title"),
    url(r'^stories/', StorySerializerView.as_view(), name="get-all-stories"),
    url(r'^stories/(?P<id>\d+)/$', StoryWithAssets.as_view(), name="get-story"),
    )