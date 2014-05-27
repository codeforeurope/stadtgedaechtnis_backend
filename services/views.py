__author__ = 'jpi'

from django.views.generic import View
from django.http import HttpResponse
from SPARQLWrapper import SPARQLWrapper, JSON
from stadtgedaechtnis_backend.utils import get_nearby_locations
from stadtgedaechtnis_backend.models import Entry, Location

import jsonpickle
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


class GetLocationJSONView(View):
    """
    Retrieves a list of locations to given lat and lon coordinates.
    Passes this list to an abstract method to retrieve further details and
    then returns the result in JSON format.
    """

    def create_result_list(self, locations):
        """
        Method that creates the result list
        """
        result = dict()
        result['locations'] = list()
        for location in locations:
            result_location = dict()
            result_location['id'] = location.id
            result_location['title'] = location.label
            result_location['latitude'] = str(location.latitude)
            result_location['longitude'] = str(location.longitude)
            self.add_additional_location_info(result_location, location)
            result['locations'].append(result_location)
        return result

    def add_additional_location_info(self, result_location, location):
        """
        Adds aditional info for each location to the result dictionary
        """
        pass

    def get(self, request, *args, **kwargs):
        locations = self.get_locations(kwargs)

        result = self.create_result_list(locations)

        return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type=RETURN_TYPE_JSON)

    def get_locations(self, kwargs):
        return get_nearby_locations(kwargs["lat"], kwargs["lon"],
                                    kwargs["maxlat"] if "maxlat" in kwargs else 0,
                                    kwargs["maxlon"] if "maxlon" in kwargs else 0)


class GetLocationsWithStoryCount(GetLocationJSONView):
    """
    Returns a list of locations and their count of stories to given lat and lon coordinates
    Parameters: lat - Latitude, lon - Longitude
    Optional: maxlat - Maximum Latitude, maxlon - Maximum Longitude
    """

    def add_additional_location_info(self, result_location, location):
        result_location['story_count'] = str(location.entry_set.count())


class GetSingleLocation(GetLocationJSONView):
    """
    Returns just a single location.
    """

    def get_locations(self, kwargs):
        result = list()
        result.append(Location.objects.get(pk=kwargs["id"]))
        return result


class GetLocationWithStoryCount(GetLocationsWithStoryCount, GetSingleLocation):
    """
    Same as above but for a single location
    """
    pass


class GetLocationsWithStoryTitle(GetLocationJSONView):
    """
    Returns a list of locations and the titles of the stories attached to this location.
    """

    def add_additional_location_info(self, result_location, location):
        result_location['stories'] = list()
        for story in location.entry_set.all():
            result_story = dict()
            result_story["id"] = story.id
            result_story["title"] = story.title
            self.add_additional_story_info(result_story, story)
            result_location['stories'].append(result_story)

    def add_additional_story_info(self, result_story, story):
        pass


class GetLocationWithStoryTitle(GetLocationsWithStoryTitle, GetSingleLocation):
    """
    Same as above but for a single location
    """
    pass


class GetLocationsWithStories(GetLocationsWithStoryTitle):
    """
    Returns a list of locations and the stories attached to it.
    """

    def add_additional_story_info(self, result_story, story):
        result_story["abstract"] = story.abstract
        result_story["author"] = story.author
        result_story["text"] = story.text
        result_story["time_start"] = str(story.time_start)
        if story.time_end is not None:
            result_story["time_end"] = str(story.time_end)
        result_story["type"] = str(story.type)
        if story.mediaobject_set.count > 0:
            media_object = story.mediaobject_set.first()
            if media_object is not None:
                result_story_image = dict()
                result_story_image["src"] = media_object.mediasource_set.first().file.url
                result_story_image["alt"] = media_object.alt
                result_story["image"] = result_story_image


class GetLocationWithStories(GetLocationsWithStories, GetSingleLocation):
    """
    Same as above but for a single location
    """
    pass


class GetAllStoriesJSONView(View):
    """
    Returns a list of all stories with or without a location.
    """

    def get(self, request, *args, **kwargs):
        stories = Entry.objects.all()

        result = self.create_result_list(stories)

        return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type=RETURN_TYPE_JSON)

    def create_result_list(self, stories):
        result = dict()
        result["stories"] = list()
        for story in stories:
            result_story = dict()
            result_story["id"] = story.id
            result_story["title"] = story.title
            if story.location is not None:
                result_story["location"] = story.location.id
            self.add_additional_story_info(result_story, story)
            result["stories"].append(result_story)

        return result

    def add_additional_story_info(self, result_story, story):
        pass


class GetAllStories(GetAllStoriesJSONView):
    """
    Returns a list of all the saved stories and their complete information.
    """

    def add_additional_story_info(self, result_story, story):
        result_story["abstract"] = story.abstract
        result_story["author"] = story.author
        result_story["text"] = story.text
        result_story["time_start"] = str(story.time_start)
        if story.time_end is not None:
            result_story["time_end"] = str(story.time_end)
        result_story["type"] = str(story.type)
        if story.mediaobject_set.count > 0:
            media_object = story.mediaobject_set.first()
            if media_object is not None:
                result_story_image = dict()
                result_story_image["src"] = media_object.mediasource_set.first().file.url
                result_story_image["alt"] = media_object.alt
                result_story["image"] = result_story_image