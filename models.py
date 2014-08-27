"""
Created on 26.02.2014

@author: jpi
"""
from decimal import Decimal, ROUND_DOWN

import os.path
import mimetypes

from django.utils.translation import ugettext as _
from django.db import models
from django.db.models.signals import post_delete
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth import get_user_model


class Location(models.Model):
    """
    A Location with a geoposition
    """
    label = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(decimal_places=15, max_digits=18)
    longitude = models.DecimalField(decimal_places=15, max_digits=18)
    altitude = models.DecimalField(decimal_places=5, max_digits=10)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)
    dbpedia_link = models.CharField(max_length=500, null=True, blank=True)

    def __unicode__(self):
        lat = str(self.latitude.quantize(Decimal('.0000000000001'), rounding=ROUND_DOWN))
        lon = str(self.longitude.quantize(Decimal('.0000000000001'), rounding=ROUND_DOWN))

        return self.label + " [" + lat + ", " + lon + "]"


class Category(models.Model):
    """
    One Category to be assigned to a story or asset
    """
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)


class Story(models.Model):

    """
    One entry
    """
    categories = models.ManyToManyField(Category, blank=True)
    title = models.CharField(max_length=500)
    abstract = models.TextField()
    text = models.TextField(null=True, blank=True)
    sources = models.TextField(null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    time_start = models.DateField()
    time_end = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True, related_name="stories")
    assets = models.ManyToManyField("Asset", related_name="assets", blank=True)
    temporary = models.BooleanField(default=False)

    class Meta:
        ordering = ('time_start', 'time_end', 'title', )

    def __unicode__(self):
        return self.title + " (" + unicode(self.author) + ")"

    def get_additional_images(self):
        """
        Returns a list of additional images for this entry
        """
        result = list()
        for index, asset in enumerate(self.assets.all()):
            if index > 0 and asset.type == Asset.IMAGE:
                result.append(asset)

        return result

    def get_additional_media(self):
        """
        Returns a list of additional media for this entry (no images)
        """
        result = list()
        for asset in self.assets.all():
            if asset.type != Asset.IMAGE:
                result.append(asset)

        return result





class Asset(models.Model):
    """
    Media Object to save images, videos or audio files that belong to an entry,
    a location or an entry type
    """
    VIDEO = "vid"
    IMAGE = "img"
    SOUND = "aud"
    TEXT = "txt"
    MEDIA_TYPES = (
        (VIDEO, _("Video")),
        (IMAGE, _("Bild")),
        (SOUND, _("Audio")),
        (TEXT, _("Text"))
    )
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)
    categories = models.ManyToManyField(Category, null=True, blank=True)
    type = models.CharField(max_length=3, choices=MEDIA_TYPES, default=IMAGE)
    alt = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    resolution = models.IntegerField(null=True, blank=True)
    device = models.CharField(max_length=300, null=True, blank=True)
    length = models.IntegerField(null=True, blank=True)
    is_readable = models.BooleanField(default=False)
    stories = models.ManyToManyField(Story, related_name="stories", through=Story.assets.through, blank=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True)

    def __unicode__(self):
        return self.alt + " (" + str(self.id) + ")"


class MediaSource(models.Model):
    """
    One Source file that belongs to a media object
    """

    def get_upload_path(self, filename):
        i = 0
        while os.path.isfile(settings.MEDIA_ROOT + str(self.asset.id) + "/" + str(i) + filename):
            i += 1
        return str(self.asset.id) + "/" + str(i) + filename

    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)
    asset = models.ForeignKey(Asset, related_name="sources")
    file = models.FileField(upload_to=get_upload_path)

    def __unicode__(self):
        return self.file.name

    def get_mime_type(self):
        return mimetypes.guess_type(self.file.url)[0]


class ImportLogEntry(models.Model):
    """
    One Import log entry.
    """
    date_time = models.DateTimeField(auto_now_add=True)
    imported_entries = models.IntegerField()
    existed_entries = models.IntegerField()
    failed_entries = models.IntegerField()

@receiver(post_delete, sender=MediaSource)
def delete_file(sender, instance, **kwargs):
    if instance.file is not None:
        file_dir = os.path.dirname(instance.file.path)
        instance.file.delete(False)
        if os.path.isdir(file_dir) and not (os.listdir(file_dir)):
            os.rmdir(file_dir)


def find_user_by_name(query_name):
    """
    Finds a user by its full name
    :param query_name: full name to query
    :return: a list of users matching the query
    """
    qs = get_user_model().objects.all()
    for term in query_name.split():
        qs = qs.filter(models.Q(first_name__icontains=term) | models.Q(last_name__icontains=term))
    if len(qs) == 0:
        raise get_user_model().DoesNotExist
    return qs