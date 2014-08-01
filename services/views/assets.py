from rest_framework.generics import CreateAPIView, GenericAPIView, ListCreateAPIView

from stadtgedaechtnis_backend.models import Asset
from stadtgedaechtnis_backend.services.authentication.permissions import IsAuthenticatedOrReadOnlyOrModerated
from stadtgedaechtnis_backend.services.serializer.generics import MultipleRequestSerializerAPIView
from stadtgedaechtnis_backend.services.serializer.serializers import AssetWithSourcesSerializer
from stadtgedaechtnis_backend.services.views import GZIPAPIView


__author__ = 'Jan'


class AssetView(GZIPAPIView, GenericAPIView):
    """
    View that provides an asset.
    """
    queryset = Asset.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnlyOrModerated, )


class AssetList(AssetView, ListCreateAPIView, MultipleRequestSerializerAPIView):
    """
    Retrieves all the assets
    """
    serializer_classes = {
        "GET": AssetWithSourcesSerializer,
        "POST": "",
    }


class AssetWithSources(AssetList):
    """
    Retrieves all the assets linked to a story
    """

    def get_queryset(self):
        """
        Filter the results.
        :return:
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        return self.queryset.filter(stories__id__exact=self.kwargs[lookup_url_kwarg])