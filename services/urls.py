__author__ = 'jpi'

from django.conf.urls import patterns, url

from stadtgedaechtnis_backend.services.views import *
from stadtgedaechtnis_backend.import_entries.views import ImportEntry


urlpatterns = patterns('',
    # TODO: add a mixin for localhost access only
    url(r'^places/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/$', GetNearbyPlacesDBPedia.as_view(),
        name="get-nearby-places"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/$', GetLocationJSONView.as_view(),
        name="get-locations"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/$', GetLocationJSONView.as_view(),
        name="get-locations"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/story_count/$',
        GetLocationsWithStoryCount.as_view(), name="get-locations-with-count"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/story_count/$',
        GetLocationsWithStoryCount.as_view(), name="get-locations-with-count"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/title/$',
        GetLocationsWithStoryTitle.as_view(), name="get-locations-with-story-title"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/title/$', GetLocationsWithStoryTitle.as_view(),
        name="get-locations-with-story-title"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/stories/$',
        GetLocationsWithStories.as_view(), name="get-locations-with-stories"),
    url(r'^locations/(?P<lat>\d{1,3}\.\d{1,10})/(?P<maxlat>\d{1,3}\.\d{1,10})/'
        '(?P<lon>\d{1,3}\.\d{1,10})/(?P<maxlon>\d{1,3}\.\d{1,10})/stories/$', GetLocationsWithStories.as_view(),
        name="get-locations-with-stories"),
    url(r'^locations/(?P<id>\d+)/$', GetSingleLocation.as_view(),
        name="get-location"),
    url(r'^locations/(?P<id>\d+)/story_count/$', GetLocationWithStoryCount.as_view(),
        name="get-location-with-story-count"),
    url(r'^locations/(?P<id>\d+)/title/$', GetLocationWithStoryTitle.as_view(),
        name="get-location-with-story-title"),
    url(r'^locations/(?P<id>\d+)/stories/$', GetLocationWithStories.as_view(),
        name="get-location-with-stories"),
    url(r'^locations/stories/$', GetAllStories.as_view(), name="get-all-stories"),
    url(r'^locations/stories/title$', GetAllStories.as_view(), name="get-all-stories"),
    )