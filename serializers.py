__author__ = 'jpi'

from rest_framework import serializers
from stadtgedaechtnis_backend.models import *


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'label', 'description', 'latitude', 'longitude', 'altitude',
                  'created', 'modified', 'dbpedia_link')


class LocationSerializerWithStoryIDs(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'label', 'description', 'latitude', 'longitude', 'altitude',
                  'created', 'modified', 'dbpedia_link', 'stories')


class StoryTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ('id', 'title', 'location')


class LocationSerializerWithStoryTitle(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'label', 'description', 'latitude', 'longitude', 'altitude',
                  'created', 'modified', 'dbpedia_link', 'stories')

    stories = StoryTitleSerializer(many=True)


class AssetURLSerializer(serializers.ModelSerializer):
    class AssetSourceSerializer(serializers.URLField):
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
    class Meta:
        model = Story
        fields = ('id', 'title', 'abstract', 'assets')

    assets = AssetURLSerializer(many=False)


class LocationSerializerWithStoryImages(LocationSerializerWithStoryTitle):
    stories = StoryImageSerializer(many=True)


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ('id', 'title', 'abstract', 'text', 'author',
                  'time_start', 'time_end', 'created', 'modified', 'location', 'categories')


class StoryWithAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ('id', 'title', 'abstract', 'text', 'author',
                  'time_start', 'time_end', 'created', 'modified', 'location', 'categories', 'assets')


class StoryWithAssetImageSerializer(StoryWithAssetSerializer):
    assets = AssetURLSerializer(many=False)


class LocationSerializerWithStories(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'label', 'description', 'latitude', 'longitude', 'altitude',
                  'created', 'modified', 'dbpedia_link', 'stories')

    stories = StorySerializer(many=True)