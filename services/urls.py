__author__ = 'jpi'

from django.conf.urls import patterns, url, include

from stadtgedaechtnis_backend.services.views import GetNearbyPlacesDBPedia


urlpatterns = patterns('',
    url(r'places/(?P<lat>\d{1,3}\.\d{1,10})/(?P<lon>\d{1,3}\.\d{1,10})/$', GetNearbyPlacesDBPedia.as_view(),
        name="get-nearby-places"),
    url(r'locations/', include("stadtgedaechtnis_backend.services.urlpatterns.locations")),
    url(r'stories/', include("stadtgedaechtnis_backend.services.urlpatterns.stories")),
    url(r'users/', include("stadtgedaechtnis_backend.services.urlpatterns.users")),
    url(r'sessions/', include("stadtgedaechtnis_backend.services.urlpatterns.sessions")),
    )