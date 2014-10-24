from datetime import datetime

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.generics import GenericAPIView, ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from stadtgedaechtnis_backend.models import Asset, MediaSource, Story
from stadtgedaechtnis_backend.services.authentication.permissions import IsAuthenticatedOrReadOnlyOrModerated
from stadtgedaechtnis_backend.services.serializer.generics import MultipleRequestSerializerAPIView
from stadtgedaechtnis_backend.services.serializer.serializers import AssetWithSourcesSerializer, \
    AssetWithUniqueIDSerializer
from stadtgedaechtnis_backend.services.views import GZIPAPIView


__author__ = 'Jan'


class AssetView(GZIPAPIView, GenericAPIView):
    """
    View that provides an asset.
    """
    queryset = Asset.objects.all()
    serializer_class = AssetWithSourcesSerializer
    permission_classes = (IsAuthenticatedOrReadOnlyOrModerated, )


class AssetList(AssetView, ListCreateAPIView, MultipleRequestSerializerAPIView):
    """
    Retrieves all the assets
    """
    serializer_classes = {
        "GET": AssetWithSourcesSerializer,
        "POST": AssetWithUniqueIDSerializer,
    }


class AssetWithSources(AssetView, CreateAPIView, RetrieveAPIView, MultipleRequestSerializerAPIView):
    """
    Retrieves all the assets linked to a story
    """

    serializer_classes = {
        "GET": AssetWithSourcesSerializer,
        "POST": AssetWithUniqueIDSerializer,
    }

    def get_queryset(self):
        """
        Filter the results.
        :return:
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        return self.queryset.filter(stories__id__exact=self.kwargs[lookup_url_kwarg])

    def post_save(self, obj, created=False):
        if created:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            story = Story.objects.get(id=self.kwargs[lookup_url_kwarg])
            obj.stories.add(story)


class SingleAsset(AssetView, RetrieveUpdateDestroyAPIView, MultipleRequestSerializerAPIView):
    """
    Retrieves a single Asset
    """
    serializer_classes = {
        "GET": AssetWithSourcesSerializer,
        "DELETE": AssetWithSourcesSerializer,
        "PUT": AssetWithUniqueIDSerializer
    }

    def retrieve(self, request, *args, **kwargs):
        pass


class AssetSources(AssetView, CreateAPIView):
    parser_classes = (FileUploadParser, )

    def create(self, request, *args, **kwargs):
        uploaded_file = None
        try:
            uploaded_file = request.FILES["file"]
        except KeyError:
            pass

        if not uploaded_file:
            return Response(status=400, data={
                "file": "A file has to be provided."
            })

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        story_id = self.kwargs[lookup_url_kwarg]

        if not story_id:
            return Response(status=400, data={
                "story_id": "A story ID has to be provided."
            })

        media_source = MediaSource()
        media_source.created = datetime.now()
        media_source.modified = datetime.now()

        asset = self.get_object()
        media_source.asset = asset
        filename = media_source.get_upload_path(uploaded_file.name)
        path = default_storage.save(filename, ContentFile(uploaded_file.read()))
        media_source.file.name = path
        media_source.save()

        return Response(status=201, data={
            "url": settings.MEDIA_URL + path
        })