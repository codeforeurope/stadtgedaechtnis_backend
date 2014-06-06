__author__ = 'jpi'

from django.views.generic import View
from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON
from stadtgedaechtnis_backend.utils import get_nearby_locations
from django.http import Http404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from stadtgedaechtnis_backend.serializers import *
from django.views.decorators.gzip import gzip_page
from django.utils.decorators import method_decorator

import json

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


class GetSingleSerializer():
    """
    Mix-in to provide a single serializer.
    """
    def __init__(self):
        pass

    def get_single_or_many_serializer(self):
        return False


class LocationSerializerView(APIView):
    """
    List one or more locations and use a specified serializer
    """
    def get_single_or_many_serializer(self):
        return True

    def get_locations(self):
        return Location.objects.all()

    def get_serializer(self):
        return LocationSerializer(self.get_locations(), many=self.get_single_or_many_serializer())

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        return Response(serializer.data)

    @method_decorator(gzip_page)
    def dispatch(self, request, *args, **kwargs):
        return super(LocationSerializerView, self).dispatch(request, *args, **kwargs)


class SingleLocation(GetSingleSerializer, LocationSerializerView):
    """
    Gets a single Location.
    """
    def get_locations(self):
        try:
            return Location.objects.get(pk=self.kwargs["id"])
        except Location.DoesNotExist:
            raise Http404


class LocationList(LocationSerializerView):
    """
    List all locations or create a new one
    """
    def post(self, request, format=None):
        pass


class LocationListWithStoryIDs(LocationSerializerView):
    """
    Gets all the location and the story IDs
    """
    def get_serializer(self):
        return LocationSerializerWithStoryIDs(self.get_locations(), many=self.get_single_or_many_serializer())


class LocationListNearby(LocationSerializerView):
    """
    Retrieves a list of locations to given lat and lon coordinates.
    """
    def get_locations(self):
        return get_nearby_locations(self.kwargs["lat"], self.kwargs["lon"],
                                    self.kwargs["maxlat"] if "maxlat" in self.kwargs else 0,
                                    self.kwargs["maxlon"] if "maxlon" in self.kwargs else 0)


class LocationListNearbyWithStoryIDs(LocationListNearby, LocationListWithStoryIDs):
    """
    Retrieves a list of locations to given lat and lon coordinates. Also includes a list of attached story IDs.
    """


class LocationListWithStoryTitle(LocationSerializerView):
    """
    Retrieves a list of locations. Also includes a list of attached story IDs.
    """
    def get_serializer(self):
        return LocationSerializerWithStoryTitle(self.get_locations(), many=self.get_single_or_many_serializer())


class LocationListNearbyWithStoryTitle(LocationListWithStoryTitle, LocationListNearby):
    """
    Retrieves a list of locations to given lat and lon coordinates. Also includes a list of attached story titles.
    """


class LocationListWithStories(LocationSerializerView):
    """
    Retrieves a list of locations. Also includes all the story information attached to these locations.
    """
    def get_serializer(self):
        return LocationSerializerWithStories(self.get_locations(), many=self.get_single_or_many_serializer())


class LocationListNearbyWithStories(LocationListNearby, LocationListWithStories):
    """
    Retrieves a list of locations to given lat and lon coordinates.
    Also includes all the story information attached to these locations.
    """


class LocationListNearbyWithImages(LocationListNearby):
    """
    Retrieves a list of locations. Also includes all the story information attached to these locations.
    """
    def get_serializer(self):
        return LocationSerializerWithStoryImages(self.get_locations(), many=self.get_single_or_many_serializer())


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


class StorySerializerView(APIView):
    """
    List all saved stories.
    """
    def get_single_or_many_serializer(self):
        return True

    def get_stories(self):
        return Story.objects.all()

    def get_serializer(self):
        return StoryWithAssetSerializer(self.get_stories(), many=self.get_single_or_many_serializer())

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        return Response(serializer.data)

    @method_decorator(gzip_page)
    def dispatch(self, request, *args, **kwargs):
        return super(StorySerializerView, self).dispatch(request, *args, **kwargs)


class StoryListWithTitle(StorySerializerView):
    """
    List all saved stories and their title.
    """
    def get_serializer(self):
        return StoryTitleSerializer(self.get_stories(), many=self.get_single_or_many_serializer())


class StoryWithAssets(GetSingleSerializer, StorySerializerView):
    """
    Retrieves one particular story and their asset IDs
    """

    def get_stories(self):
        return Story.objects.get(pk=self.kwargs["id"])

    def get_serializer(self):
        return StoryWithAssetSerializer(self.get_stories(), many=self.get_single_or_many_serializer())


class StoryWithAssetImage(StoryWithAssets):
    """
    Retrieves one particular story and their assets plus first URL.
    """
    def get_serializer(self):
        return StoryWithAssetImageSerializer(self.get_stories(), many=self.get_single_or_many_serializer())


class StoryTitleQuery(StorySerializerView):
    """
    Retrieves a story matching a given query
    """

    def get_stories(self):
        return Story.objects.filter(title__icontains=self.kwargs["query"])


class StoryTextAndTitleQuery(StorySerializerView):
    def get_stories(self):
        return Story.objects.filter(Q(text__icontains=self.kwargs["query"]) | Q(title__icontains=self.kwargs["query"]))


class StoryQueryWithTitle(StoryTitleQuery, StoryListWithTitle):
    """
    Retrieves a list of stories with matching query.
    """


class StoryTextQueryWithTitle(StoryTextAndTitleQuery, StoryListWithTitle):
    pass