__author__ = 'jpi'

import json

from django.views.generic import View
from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveAPIView, ListAPIView
from stadtgedaechtnis_backend.utils import get_nearby_locations
from stadtgedaechtnis_backend.services.views import GZIPAPIView
from stadtgedaechtnis_backend.serializers import *
from stadtgedaechtnis_backend.services.authentication.permissions import IsAuthenticatedOrReadOnlyOrModerated


RETURN_TYPE_JSON = "application/json"


class GetNearbyPlacesDBPedia(View):
    """
    Returns a list of places to a given location.
    Parameters: lat - Latitude, lon - Longitude
    A query to DBpedia is made and the results are given in JSON.
    """

    def get(self, request, *args, **kwargs):
        lat, lon = float(kwargs["lat"]), float(kwargs["lon"])
        min_lat, max_lat = lat - 0.01, lat + 0.01
        min_lon, max_lon = lon - 0.01, lon + 0.01

        # build query
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery("select distinct ?link, ?name, ?latitude, ?longitude where "
                        "{?link geo:lat ?latitude . ?link geo:long ?longitude . ?link foaf:name ?name "
                        "filter (xsd:decimal(?latitude) >= " + str(min_lat) + ") "
                        "filter (xsd:decimal(?latitude) <= " + str(max_lat) + ") "
                        "filter (xsd:decimal(?longitude) >= " + str(min_lon) + ") "
                        "filter (xsd:decimal(?longitude) <= " + str(max_lon) + ")}")
        sparql.setReturnFormat(JSON)
        # query DBpedia
        places = sparql.query().convert()

        result = {"entries": []}

        # iterate over results
        for place in places["results"]["bindings"]:
            result["entries"].append({
                "name": place["name"]["value"],
                "url": place["link"]["value"],
                "lat": place["latitude"]["value"],
                "lon": place["longitude"]["value"]
            })

        return HttpResponse(json.dumps(result),
                            content_type="application/json")


class LocationView(GZIPAPIView, GenericAPIView):
    """
    Base class for use with Locations
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (IsAuthenticatedOrReadOnlyOrModerated, )


class LocationListCreate(LocationView, ListCreateAPIView):
    """
    List all locations or create a new one
    """


class LocationList(LocationView, ListAPIView):
    """
    Simply lists all locations
    """


class LocationListWithStoryIDs(LocationList):
    """
    Gets all the location and the story IDs
    """
    serializer_class = LocationSerializerWithStoryIDs


class LocationListWithStoryTitle(LocationList):
    """
    Retrieves a list of locations. Also includes a list of attached story IDs.
    """
    serializer_class = LocationSerializerWithStoryTitle


class LocationListWithStories(LocationList):
    """
    Retrieves a list of locations. Also includes all the story information attached to these locations.
    """
    serializer_class = LocationSerializerWithStories


class LocationListNearbyWithImages(LocationList):
    """
    Retrieves a list of locations. Also includes all the story information attached to these locations.
    """
    serializer_class = LocationSerializerWithStoryImages


class SingleLocation(LocationView, RetrieveAPIView):
    """
    Gets a single Location.
    """


class SingleLocationWithStoryIDs(SingleLocation, LocationListWithStoryIDs):
    """
    Retrieves a single location by its ID.
    Also includes a list of attached story IDs.
    """


class SingleLocationWithStoryTitle(SingleLocation, LocationListWithStoryTitle):
    """
    Retrieves a single location by its ID.
    Also includes a list of attached story title.
    """


class SingleLocationWithStories(SingleLocation, LocationListWithStories):
    """
    Retrieves a single location by its ID.
    Also includes a list of attached stories.
    """


class SingleLocationWithStoriesImage(SingleLocation, LocationListNearbyWithImages):
    """
    Retrieves a single location by ids ID.
    also includes al ist of attached stories and images.
    """


class LocationListNearby(LocationList):
    """
    Retrieves a list of locations to given lat and lon coordinates.
    """
    def get_queryset(self):
        return get_nearby_locations(self.kwargs["lat"], self.kwargs["lon"],
                                    self.kwargs["maxlat"] if "maxlat" in self.kwargs else 0,
                                    self.kwargs["maxlon"] if "maxlon" in self.kwargs else 0)


class LocationListNearbyWithStoryIDs(LocationListNearby, LocationListWithStoryIDs):
    """
    Retrieves a list of locations to given lat and lon coordinates. Also includes a list of attached story IDs.
    """


class LocationListNearbyWithStoryTitle(LocationListWithStoryTitle, LocationListNearby):
    """
    Retrieves a list of locations to given lat and lon coordinates. Also includes a list of attached story titles.
    """


class LocationListNearbyWithStories(LocationListNearby, LocationListWithStories):
    """
    Retrieves a list of locations to given lat and lon coordinates.
    Also includes all the story information attached to these locations.
    """
