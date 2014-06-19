__author__ = 'jpi'

from django.conf.urls import patterns, url
from stadtgedaechtnis_backend.services.views.locations import *


urlpatterns = patterns(
    '',
    url(r'^(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/$', LocationListNearby.as_view(),
        name="get-locations"),
    url(r'^(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/$', LocationListNearby.as_view(),
        name="get-locations"),
    url(r'^(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/story_count/$',
        LocationListNearbyWithStoryIDs.as_view(), name="get-near-locations-with-count"),
    url(r'^(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/story_count/$',
        LocationListNearbyWithStoryIDs.as_view(), name="get-locations-with-count"),
    url(r'^(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/title/$',
        LocationListNearbyWithStoryTitle.as_view(), name="get-near-locations-with-story-title"),
    url(r'^(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/title/$',
        LocationListNearbyWithStoryTitle.as_view(),
        name="get-locations-with-story-title"),
    url(r'^(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/$',
        LocationListNearbyWithStories.as_view(), name="get-near-locations-with-stories"),
    url(r'^(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/$', LocationListNearbyWithStories.as_view(),
        name="get-locations-with-stories"),
    url(r'^(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/title/image/$',
        LocationListNearbyWithImages.as_view(), name="get-near-locations-with-stories-image"),
    url(r'^(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/title/image/$',
        LocationListNearbyWithImages.as_view(),
        name="get-locations-with-stories-image"),
    url(r'^(?P<pk>\d+)/$', SingleLocation.as_view(),
        name="get-location"),
    url(r'^(?P<pk>\d+)/stories/story_count/$', SingleLocationWithStoryIDs.as_view(),
        name="get-location-with-story-count"),
    url(r'^(?P<pk>\d+)/stories/title/$', SingleLocationWithStoryTitle.as_view(),
        name="get-location-with-story-title"),
    url(r'^(?P<pk>\d+)/stories/$', SingleLocationWithStories.as_view(),
        name="get-location-with-stories"),
    url(r'^(?P<pk>\d+)/stories/title/image/$', SingleLocationWithStoriesImage.as_view(),
        name="get-location-with-stories-images"),
    url(r'^$', LocationListCreate.as_view(), name="list-locations"),
    url(r'^stories/story_count/$', LocationListWithStoryIDs.as_view(), name="list-locations-with-story-count"),
    url(r'^stories/title/$', LocationListWithStoryTitle.as_view(), name="list-locations-with-id"),
    url(r'^stories/$', LocationListWithStories.as_view(), name="list-locations-with-stories"),
    )