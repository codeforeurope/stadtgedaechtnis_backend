from stadtgedaechtnis_backend.serializers import *
from django.db.models import Q
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveAPIView, ListAPIView
from stadtgedaechtnis_backend.services.views import GZIPAPIView
from stadtgedaechtnis_backend.services.authentication.permissions import IsAuthenticatedOrReadOnlyOrModerated

__author__ = 'Jan'


class StoryView(GZIPAPIView, GenericAPIView):
    """
    Base class for use with Stories
    """
    queryset = Story.objects.all()
    serializer_class = StoryWithAssetSerializer
    permission_classes = (IsAuthenticatedOrReadOnlyOrModerated, )


class StoryListCreate(StoryView, ListCreateAPIView):
    """
    View that lists or creates stories
    """


class StoryList(StoryView, ListAPIView):
    """
    Simply lists all stories
    """


class StoryListWithTitle(StoryList):
    """
    List all saved stories and their title.
    """
    serializer_class = StoryTitleSerializer


class SingleLocation(StoryView, RetrieveAPIView):
    """
    Gets a single Location.
    """


class StoryWithAssets(SingleLocation):
    """
    Retrieves one particular story and their asset IDs
    """
    serializer_class = StoryWithAssetSerializer


class StoryWithAssetImage(SingleLocation):
    """
    Retrieves one particular story and their assets plus first URL.
    """
    serializer_class = StoryWithAssetImageSerializer


class StoryTitleQuery(StoryList):
    """
    Retrieves a story matching a given query
    """
    def get_queryset(self):
        return Story.objects.filter(title__icontains=self.kwargs["query"])


class StoryTextAndTitleQuery(StoryList):
    def get_queryset(self):
        return Story.objects.filter(Q(text__icontains=self.kwargs["query"]) | Q(title__icontains=self.kwargs["query"]))


class StoryTextQueryWithTitle(StoryTextAndTitleQuery, StoryListWithTitle):
    pass


class StoryQueryWithTitle(StoryTitleQuery, StoryListWithTitle):
    """
    Retrieves a list of stories with matching query.
    """