from abc import ABCMeta, abstractmethod
import urllib2
import json
import time
import os
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.conf import settings
from django.views.generic import View
from django.contrib.auth.models import User

from stadtgedaechtnis_backend.utils import replace_multiple, get_nearby_locations
from stadtgedaechtnis_backend.models import Location, Story, Asset, MediaSource


__author__ = 'jpi'


def load_json(source):
        """
        Loads the JSON file from the source and makes it available in a usable form.
        """
        response = urllib2.urlopen(source)
        result = response.read()
        dictionary = {
            "id:": "\"id\":",
            "isDuration:": "\"isDuration\":",
            "type:": "\"type\":",
            "addressLatLng:": "\"addressLatLng\":",
            "typename:": "\"typename\":",
            "created:": "\"created\":",
            "label:": "\"label\":",
            "preview:": "\"preview\":",
            "pic:": "\"pic\":",
            "pic_text:": "\"pic_text\":",
            "timeStart:": "\"timeStart\":",
            "author:": "\"author\":",
            "www:": "\"www\":",
            "details:": "\"details\":",
            "timeEnd:": "\"timeEnd\":",
            "nr:": "\"nr\":",
            "age:": "\"age\":",
            "types:": "\"types\":",
            "pluralLabel:": "\"pluralLabel\":",
            "properties:": "\"properties\":",
            "valueType:": "\"valueType\":",
            "	": "",
            ",\r\n,": ",\r\n",
        }
        # make the JSON valid
        result = replace_multiple(result, dictionary)
        json_result = json.loads(result)
        # select all the items
        items = json_result["items"]
        return items


class ImportView(TemplateView):
    """
    Abstract class to import entries from various sources.
    """

    __metaclass__ = ABCMeta
    interactive = False
    source = ""
    redirect = False
    redirect_to = ""
    request = None

    @abstractmethod
    def do_import(self):
        """
        Does the actual import. Abstract method to be implemented in subclasses.
        """
        pass

    def get(self, request, *args, **kwargs):
        """
        Returns a HttpResponse after importing the entries.
        Only allows requests from localhost.
        """
        self.request = request
        request_host = request.get_host()
        if self.interactive or request_host.startswith("localhost") or request_host.startswith("127.0.0.1"):
            # Interactive requests can be from any host.
            # This site is viewed as an admin site.
            self.do_import()

            if self.redirect:
                response = HttpResponseRedirect(self.redirect_to)
            else:
                response = super(ImportView, self).get(request)

        else:
            response = HttpResponseForbidden()
        return response


def add_story(import_class, label, story, location_object=None):
    # only insert story if story does not exist so far
    if not Story.objects.filter(title=label).exists():
        entry = Story()
        entry.title = label
        entry.location = location_object
        # entry.author = story["author"]
        # TODO: import author correctly
        entry.author = import_class.request.user
        entry.abstract = story["preview"]

        if "timeStart" in story:
            try:
                entry.time_start = time.strftime("%Y-%m-%d", time.strptime(story["timeStart"], "%Y-%m-%d"))
            except ValueError:
                entry.time_start = time.strftime("%Y-%m-%d",
                                                 time.strptime(story["created"], "%d.%m.%Y %H:%M:%S"))
        else:
            entry.time_start = time.strftime("%Y-%m-%d",
                                             time.strptime(story["created"], "%d.%m.%Y %H:%M:%S"))

        if "timeEnd" in story:
            entry.time_end = story["timeEnd"]

        # TODO: add more infos
        entry.save()

        if "pic" in story and story["pic"] != "":
            picture_url = "http://www.stadtgeschichte-coburg.de/" + story["pic"]
            # populate the MediaObject
            media_object = Asset()
            media_object.type = Asset.IMAGE
            media_object.created = datetime.now()
            media_object.modified = datetime.now()
            media_object.alt = story["pic_text"] if "pic_text" in story else ""
            media_object.entry = entry
            media_object.save()

            # populate the MediaSource
            media_source = MediaSource()
            media_source.created = datetime.now()
            media_source.modified = datetime.now()

            media_source.media_object = media_object

            # get a correct upload path for the image
            filename = media_source.get_upload_path("upload.jpg")
            download_file = urllib2.urlopen(picture_url)

            # create intermittent directories if not present
            if not os.path.exists(os.path.dirname(settings.MEDIA_ROOT + filename)):
                os.makedirs(os.path.dirname(settings.MEDIA_ROOT + filename))
            # open local file
            media_file = open(settings.MEDIA_ROOT + filename, "wb")
            # download and save file at once (memory!)
            media_file.write(download_file.read())
            media_file.close()
            media_source.file.name = filename
            media_source.save()

        else:
            entry.save()
        # Add entry to succeeded entry list
        import_class.success_entries.append(entry)

    else:
        entry = dict()
        entry["title"] = label
        entry["location"] = location_object
        import_class.exist_entries.append(entry)


class SimpleJSONImport(ImportView):
    """
    Imports entries from the standard JSON file supplied by Digitales Stadtgedaechtnis
    """
    template_name = "admin/import_result.html"
    success_entries = []
    failed_entries = []
    exist_entries = []

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SimpleJSONImport, self).get_context_data(**kwargs)
        # Add succeeded and failed imports
        context['success_import'] = self.success_entries
        context['fail_import'] = self.failed_entries
        context['exist_import'] = self.exist_entries
        return context

    def do_import(self):
        self.success_entries = []
        self.failed_entries = []
        self.exist_entries = []
        items = load_json(self.source)
        # filter for all the locations
        location_items = filter(lambda entry: "id" in entry, items)
        story_items = filter(lambda entry: "label" in entry, items)

        # iterate over all the located stories
        for location in location_items:
            lat, lon = location["addressLatLng"].split(",")
            lat, lon = Decimal(lat), Decimal(lon)
            label = location["id"]

            # find the story
            story = filter(lambda entry: entry["label"] == label, story_items)[0]
            try:
                location_object = Location.objects.get(latitude=lat, longitude=lon)

                add_story(self, label, story, location_object)

            except Location.DoesNotExist:
                location["lat"] = str(lat)
                location["lon"] = str(lon)
                location["url"] = reverse('admin:stadtgedaechtnis_backend_location_add') + \
                    "?latitude=" + str(lat) + "&longitude=" + str(lon)
                location["near_locations"] = list()
                location["nr"] = story["nr"]
                for nearby_location in get_nearby_locations(lat, lon):
                    near_location = dict()
                    near_location["id"] = nearby_location.id
                    near_location["label"] = nearby_location.__unicode__()
                    location["near_locations"].append(near_location)

                self.failed_entries.append(location)

            # remove located story from story_items
            story_items.remove(story)

        # iterate over all the remaining stories without location
        for story in story_items:
            add_story(self, story["label"], story)


class ImportEntry(View):
    """
    Imports one specific entry to a specific location
    """

    source = ""

    success_entries = list()
    exist_entries = list()

    def get(self, request, *args, **kwargs):
        self.success_entries = list()
        self.exist_entries = list()
        items = load_json(self.source)
        item_id = kwargs["id"]
        location_id = int(kwargs["location"])

        def find_id(entry):
            if "nr" in entry and entry["nr"] == item_id:
                return True

            return False

        story = filter(find_id, items)[0]
        try:
            location_object = Location.objects.get(pk=location_id)
            add_story(self, story["label"], story, location_object)
        except Location.DoesNotExist:
            return HttpResponseServerError()

        if len(self.success_entries) > 0:
            return HttpResponse()
        else:
            return HttpResponseServerError()
