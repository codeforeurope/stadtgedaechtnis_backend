from rest_framework.fields import BooleanField

__author__ = 'jpi'

from rest_framework import serializers
from stadtgedaechtnis_backend.services.serializer.fields import UniqueIDField, IgnoreValueBooleanField
from stadtgedaechtnis_backend.models import *


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializes a location
    """
    class Meta:
        model = Location
        fields = ('id', 'label', 'description', 'latitude', 'longitude', 'altitude',
                  'created', 'modified', 'dbpedia_link')


class LocationSerializerWithUniqueID(serializers.ModelSerializer):
    """
    Serializes a location with and adds a unique ID. Used for POST requests.
    """
    class Meta:
        model = Location
        fields = ('id', 'label', 'description', 'latitude', 'longitude', 'altitude',
                  'created', 'modified', 'dbpedia_link', 'unique_id')

    unique_id = UniqueIDField()


class LocationSerializerWithStoryIDs(serializers.ModelSerializer):
    """
    Serializes a location and the IDs of attached stories
    """
    class Meta:
        model = Location
        fields = ('id', 'label', 'description', 'latitude', 'longitude', 'altitude',
                  'created', 'modified', 'dbpedia_link', 'stories')


class StoryTitleSerializer(serializers.ModelSerializer):
    """
    Serializes a story with title and location
    """
    class Meta:
        model = Story
        fields = ('id', 'title', 'location')


class LocationSerializerWithStoryTitle(serializers.ModelSerializer):
    """
    Serializes a location with stories using the StoryTitleSerializer
    """
    class Meta:
        model = Location
        fields = ('id', 'label', 'description', 'latitude', 'longitude', 'altitude',
                  'created', 'modified', 'dbpedia_link', 'stories')

    stories = StoryTitleSerializer(many=True)


class AssetURLSerializer(serializers.ModelSerializer):
    """
    Serializes an asset, providing the first source URL
    """
    class AssetFirstSourceField(serializers.URLField):
        """
        Serializes the first asset source to a source URL
        """
        def to_native(self, value):
            if value.instance.sources.first() is not None:
                return value.instance.sources.first().file.url
            else:
                return None

    class Meta:
        model = Asset
        fields = ('alt', 'sources')

    sources = AssetFirstSourceField()


class StoryImageSerializer(serializers.ModelSerializer):
    """
    Serializes a story with only title and abstract and all the assets belonging to this story using the AssetURLSerializer
    """
    class Meta:
        model = Story
        fields = ('id', 'title', 'abstract', 'assets')

    assets = AssetURLSerializer(many=False)


class LocationSerializerWithStoryImages(LocationSerializerWithStoryTitle):
    """
    Serializes a Location and the attached stories using the StoryImageSerializer
    """
    stories = StoryImageSerializer(many=True)


class StoryWithAssetSerializer(serializers.ModelSerializer):
    """
    Serializes a story and all the IDs of attached stories
    """
    class Meta:
        model = Story
        fields = ('id', 'title', 'abstract', 'text', 'author',
                  'time_start', 'time_end', 'created', 'modified', 'location', 'categories', 'assets', 'temporary')


class StoryWithUniqueIDSerializer(serializers.ModelSerializer):
    """
    Serializes a story with a unique ID
    """
    class Meta:
        model = Story
        fields = ('id', 'title', 'abstract', 'text', 'author',
                  'time_start', 'time_end', 'created', 'modified',
                  'location', 'categories', 'assets', 'temporary', 'unique_id')

    temporary = IgnoreValueBooleanField(default=True)
    unique_id = UniqueIDField()


class AssetSourceSerializer(serializers.Serializer):
    """
    Serializes an asset source
    """

    class AssetSourceField(serializers.URLField):
        """
        Serializes the first asset source to a source URL
        """
        def to_native(self, value):
            if value.instance.file is not None:
                return value.instance.file.url
            else:
                return None

    class MimeTypeField(serializers.CharField):
        """
        Serializes the mime type of the source file
        """
        def field_to_native(self, obj, field_name):
            return obj.get_mime_type()

    mime = MimeTypeField()
    file = AssetSourceField()


class AssetWithSourcesSerializer(serializers.ModelSerializer):
    """
    Serializes an asset
    """
    class Meta:
        model = Asset
        fields = ('id', 'type', 'created', 'modified', 'alt', 'description', 'width',
                  'height', 'resolution', 'device', 'length', 'is_readable', 'sources')

    sources = AssetSourceSerializer(many=True)


class AssetWithUniqueIDSerializer(serializers.ModelSerializer):
    """
    Serializes an asset with a unique ID
    """
    class Meta:
        model = Asset
        fields = ('id', 'type', 'created', 'modified', 'alt', 'description', 'width',
                  'height', 'resolution', 'device', 'length', 'is_readable', 'unique_id')

    unique_id = UniqueIDField()


class StoryWithAssetImageSerializer(StoryWithAssetSerializer):
    """
    Serializes a story completely using AssetURLSerializer for its assets
    """
    assets = AssetURLSerializer(many=False)


class LocationSerializerWithStories(serializers.ModelSerializer):
    """
    Serializes a location with their attached stories using a StoryWithAssetSerializer
    """
    class Meta:
        model = Location
        fields = ('id', 'label', 'description', 'latitude', 'longitude', 'altitude',
                  'created', 'modified', 'dbpedia_link', 'stories')

    stories = StoryWithAssetSerializer(many=True)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes a user with an absolute URL.
    """
    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ('url', 'id', 'username', 'first_name', 'last_name', 'password', 'email')

    class PasswordField(serializers.CharField):
        def from_native(self, value):
            from django.contrib.auth import hashers

            return hashers.make_password(value)

    password = PasswordField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    url = serializers.HyperlinkedIdentityField(view_name="stadtgedaechtnis_backend:user-detail")