__author__ = 'jpi'

import urllib2
import json
import time
import os
import re
from datetime import datetime
from decimal import Decimal
from urllib2 import HTTPError

from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from stadtgedaechtnis_backend.utils import replace_multiple, get_nearby_locations
from stadtgedaechtnis_backend.models import Location, Story, Asset, MediaSource, find_user_by_name, Category


STADTGEDAECHTNIS_URL = "http://www.stadtgeschichte-coburg.de/"


def load_json(source):
    """
    Loads the JSON file from the source and makes it available in a usable form.
    """
    response = urllib2.urlopen(source)
    result = response.read()
    # add double quotes
    dictionary = {
        " id:": " \"id\":",
        " isDuration:": " \"isDuration\":",
        " type:": " \"type\":",
        " addressLatLng:": " \"addressLatLng\":",
        " typename:": " \"typename\":",
        " created:": " \"created\":",
        " label:": " \"label\":",
        " preview:": " \"preview\":",
        " pic:": " \"pic\":",
        " pic_text:": " \"pic_text\":",
        " timeStart:": " \"timeStart\":",
        " author:": " \"author\":",
        " www:": " \"www\":",
        " details:": " \"details\":",
        " timeEnd:": " \"timeEnd\":",
        " nr:": " \"nr\":",
        " age:": " \"age\":",
        " types:": " \"types\":",
        "pluralLabel:": "\"pluralLabel\":",
        " properties:": " \"properties\":",
        "valueType:": "\"valueType\":",
        " quellen:": " \"quellen\":",
        " richtext:": " \"richtext\":",
        " categories:": " \"categories\":",
        "	": "",
        "\r\n": "",
        ",\r\n,": ",",
    }
    # make the JSON valid
    result = replace_multiple(result, dictionary)

    def fix_richtext(match):
        # replace " in richtext with &quot;
        richtext = match.group(0)
        original_group_1 = match.groups()[1]
        group_1 = original_group_1.replace("\"", "&quot;")

        def replace_quot(quot_match):
            replace_in = quot_match.group(0)
            # replace &quot; in html tags with '
            return replace_in.replace("&quot;", "'")

        group_1 = re.sub(r'<[^/]([^>]*)>', replace_quot, group_1)
        return_result = richtext.replace(original_group_1, group_1)
        return return_result

    # clean richtext and quellen section
    result = re.sub(r'(\"richtext\": \"([^\r]*)\"\r)', fix_richtext, result)
    result = re.sub(r'(\"quellen\": \"([^\r]*)\", \"richtext\":)', fix_richtext, result)
    json_result = json.loads(result)
    # select all the items
    items = json_result["items"]
    return items


class AddEntryMixIn(object):
    """
    Mix-in that can add a story to a given entry
    """
    success_entries = []
    exist_entries = []
    failed_entries = []

    def add_story(self, label, story, location_object=None):
        # only insert story if story does not exist so far
        if not Story.objects.filter(title=label).exists():
            entry = Story()
            entry.title = label
            entry.location = location_object

            entry_author = story["author"]
            try:
                authors = find_user_by_name(entry_author)
                entry.author = authors[0]
            except get_user_model().DoesNotExist:
                author = get_user_model().objects.create_user(entry_author.replace(" ", "_"))
                author.first_name = entry_author[:entry_author.rindex(" ")]
                author.last_name = entry_author[entry_author.rindex(" "):]
                author.save()
                entry.author = author

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

            if "quellen" in story:
                entry.sources = story["quellen"]

            entry.save()

            if "categories" in story:
                for category in story["categories"]:
                    try:
                        category_object = Category.objects.get(name=category)
                    except Category.DoesNotExist:
                        category_object = Category()
                        category_object.name = category
                        category_object.save()
                    entry.categories.add(category_object)

            if "richtext" in story:
                richtext = story["richtext"]

                def replace_img(match):
                    groupdict = match.groupdict()
                    src = groupdict["src"]
                    alt = groupdict["alt"]
                    if src is not None:
                        url = STADTGEDAECHTNIS_URL + src
                        download_image(entry, url, alt)
                    return ""

                richtext = re.sub(r'<img[^>]*src=\'(?P<src>[^>\']*)\'[^>]*alt=\'(?P<alt>[^>\']*)\'[^>]*[/]?>',
                                  replace_img, richtext)
                richtext = re.sub(r'<img[^>]*alt=\'(?P<alt>[^>\']*)\'[^>]*src=\'(?P<src>[^>\']*)\'[^>]*[/]?>',
                                  replace_img, richtext)
                entry.text = richtext

            entry.save()

            if "pic" in story and story["pic"] != "":
                picture_url = "http://www.stadtgeschichte-coburg.de/" + story["pic"]
                # populate the MediaObject
                download_image(entry, picture_url, story["pic_text"] if "pic_text" in story else "")

            else:
                entry.save()
            # Add entry to succeeded entry list
            self.success_entries.append(entry)

        else:
            entry = dict()
            entry["title"] = label
            entry["location"] = location_object
            self.exist_entries.append(entry)


def download_image(entry, picture_url, alt=""):
    """
    Downloads an image from the stadtgedaechtnis server and attaches it to the given entry.
    :param entry: Entry
    :param picture_url: Picture URL
    :param alt: Alt for image
    :return:
    """
    media_object = Asset()
    media_object.type = Asset.IMAGE
    media_object.created = datetime.now()
    media_object.modified = datetime.now()
    if alt is None:
        alt = ""
    media_object.alt = alt
    media_object.save()
    entry.assets.add(media_object)
    # populate the MediaSource
    media_source = MediaSource()
    media_source.created = datetime.now()
    media_source.modified = datetime.now()
    media_source.asset = media_object
    # get a correct upload path for the image
    filename = media_source.get_upload_path("upload.jpg")
    try:
        download_file = urllib2.urlopen(picture_url)
        # create intermittent directories if not present
        if not os.path.exists(os.path.dirname(settings.MEDIA_ROOT + filename)):
            os.makedirs(os.path.dirname(settings.MEDIA_ROOT + filename))
        # open local file
        media_file = open(settings.MEDIA_ROOT + filename, "wb")
        # download and save file at once (memory!)
        media_file.write(download_file.read())
        media_file.close()
    except HTTPError:
        pass
    finally:
        media_source.file.name = filename
        media_source.save()


class JSONAllEntriesImporter(AddEntryMixIn):
    """
    Imports all entries from the given source.
    """
    def __init__(self, source):
        # set source
        self.source = source

    def do_import(self):
        """
        Does the actual import.
        :return:
        """
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

            # check if story already imported
            if not Story.objects.filter(title=label).exists():
                location_objects = Location.objects.filter(latitude=lat, longitude=lon)
                if len(location_objects) > 0:
                    location_object = location_objects[0]
                    self.add_story(label, story, location_object)

                else:
                    location["lat"] = str(lat)
                    location["lon"] = str(lon)
                    location["url"] = reverse('admin:stadtgedaechtnis_backend_location_add') + \
                        "?latitude=" + str(lat) + "&longitude=" + str(lon)
                    location["near_locations"] = list()
                    location["nr"] = story["nr"]
                    search_lat = lat - Decimal(0.0007)
                    search_lon = lon - Decimal(0.0007)
                    search_max_lat = lat + Decimal(0.0007)
                    search_max_lon = lon + Decimal(0.0007)
                    for nearby_location in get_nearby_locations(search_lat, search_lon, search_max_lat, search_max_lon):
                        near_location = dict()
                        near_location["id"] = nearby_location.id
                        near_location["label"] = nearby_location.__unicode__()
                        location["near_locations"].append(near_location)

                    self.failed_entries.append(location)
            else:
                saved_stories = Story.objects.filter(title=label)
                saved_story = saved_stories[0]
                entry = dict()
                entry["title"] = label
                entry["location"] = saved_story.location
                self.exist_entries.append(entry)

            # remove located story from story_items
            story_items.remove(story)

        # iterate over all the remaining stories without location
        for story in story_items:
            self.add_story(story["label"], story)


class JSONOneEntryImporter(AddEntryMixIn):
    """
    Class that imports one specific entry from the JSON source.
    """
    def __init__(self, source, item_id, location_id):
        self.source = source
        self.item_id = item_id
        self.location_id = location_id

    def do_import(self):
        # load json
        items = load_json(self.source)

        def find_id(entry):
            if "nr" in entry and entry["nr"] == self.item_id:
                return True

            return False

        # find the respective story
        story = filter(find_id, items)[0]
        try:
            # get the location
            location_object = Location.objects.get(pk=self.location_id)
            # add story
            self.add_story(story["label"], story, location_object)
        except Location.DoesNotExist:
            raise ValueError("No location found for location_id %s" % self.location_id)


def do_silent_json_import(source):
    """
    Cronjob to import all the entries silently and save entries, that haven't been
    imported to a log list. Also deletes log entries older than 7 days.
    :param source:
    :return:
    """
    importer = JSONAllEntriesImporter(source)
    importer.do_import()

    from stadtgedaechtnis_backend.models import ImportLogEntry
    from datetime import timedelta

    log_entry = ImportLogEntry()
    log_entry.existed_entries = len(importer.exist_entries)
    log_entry.failed_entries = len(importer.failed_entries)
    log_entry.imported_entries = len(importer.success_entries)
    log_entry.save()
    ImportLogEntry.objects.filter(date_time__lte=datetime.now() - timedelta(days=7)).delete()