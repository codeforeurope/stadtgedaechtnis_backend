__author__ = 'jpi'

from rest_framework import serializers
from stadtgedaechtnis_backend.models import *


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializes a location
    """
    class Meta:
        model = Location
        fields = ('id', 'label', 'description', 'latitude', 'longitude', 'altitude',
                  'created', 'modified', 'dbpedia_link')


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
    class AssetSourceSerializer(serializers.URLField):
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

    sources = AssetSourceSerializer()


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
                  'time_start', 'time_end', 'created', 'modified', 'location', 'categories', 'assets')


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


class UserSerizalier(serializers.HyperlinkedModelSerializer):
    """
    Serializes a user with an absolute URL.
    """
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'first_name', 'last_name')