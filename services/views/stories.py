import operator

from django.db.models import Q
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveAPIView, ListAPIView, \
    RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from stadtgedaechtnis_backend.services.serializer.generics import MultipleRequestSerializerAPIView
from stadtgedaechtnis_backend.services.serializer.serializers import *
from stadtgedaechtnis_backend.services.views import GZIPAPIView
from stadtgedaechtnis_backend.services.authentication.permissions import IsAuthenticatedOrReadOnlyOrModerated, IsAuthenticatedOrModerated


__author__ = 'Jan'


class StoryView(GZIPAPIView, GenericAPIView):
    """
    Base class for use with Stories
    """
    queryset = Story.objects.all()
    serializer_class = StoryWithAssetSerializer
    permission_classes = (IsAuthenticatedOrReadOnlyOrModerated, )


class StoryEmailView(SingleObjectTemplateResponseMixin, BaseDetailView, StoryView):
    """
    Sends an email for this object
    Needs the unique_id parameter present in order to work
    """
    permission_classes = (IsAuthenticatedOrModerated, )
    template_name = "stadtgedaechtnis/email.html"
    object = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # TODO: send_mail(self.object)
        serializer = self.get_serializer(self.object)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        template_response = self.render_to_response(context)
        email_content = template_response.rendered_content
        # send_mail(email_content)


class StoryListCreate(StoryView, ListCreateAPIView, MultipleRequestSerializerAPIView):
    """
    View that lists or creates stories
    """
    serializer_classes = {
        "GET": StoryWithAssetSerializer,
        "POST": StoryWithUniqueIDSerializer,
    }


class StoryList(StoryView, ListAPIView):
    """
    Simply lists all stories
    """


class StoryListWithTitle(StoryList):
    """
    List all saved stories and their title.
    """
    serializer_class = StoryTitleSerializer


class SingleStory(StoryView, RetrieveAPIView):
    """
    Gets a single Location.
    """


class StoryWithAssets(SingleStory, RetrieveUpdateDestroyAPIView, MultipleRequestSerializerAPIView):
    """
    Retrieves one particular story and their asset IDs
    """
    serializer_classes = {
        "GET": StoryWithAssetSerializer,
        "PUT": StoryWithUniqueIDSerializer,
        "DELETE": StoryWithAssetSerializer
    }


class StoryWithAssetImage(SingleStory):
    """
    Retrieves one particular story and their assets plus first URL.
    """
    serializer_class = StoryWithAssetImageSerializer


class StoryTitleQuery(StoryList):
    """
    Retrieves a story matching a given query
    """
    def get_queryset(self):
        # split the querystring
        keywords = self.kwargs["query"].split(" ")
        # AND the words together
        filter_keywords = reduce(operator.and_, (Q(title__icontains=keyword) for keyword in keywords))
        # filter queryset
        return Story.objects.filter(filter_keywords, temporary=False)


class StoryTextAndTitleQuery(StoryList):
    def get_queryset(self):
        # split the querystring
        keywords = self.kwargs["query"].split(" ")
        # AND the words and OR the title and text queries together
        filter_keywords = reduce(operator.and_, (Q(title__icontains=keyword) for keyword in keywords)) | \
            reduce(operator.and_, (Q(text__icontains=keyword) for keyword in keywords))
        # filter queryset
        return Story.objects.filter(filter_keywords, temporary=False)


class StoryTextQueryWithTitle(StoryTextAndTitleQuery, StoryListWithTitle):
    pass


class StoryQueryWithTitle(StoryTitleQuery, StoryListWithTitle):
    """
    Retrieves a list of stories with matching query.
    """