import operator
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives

from django.http import HttpResponseServerError
from django.views.generic.detail import SingleObjectTemplateResponseMixin, BaseDetailView
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveAPIView, ListAPIView, \
    RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from stadtgedaechtnis_backend.services.serializer.generics import MultipleRequestSerializerAPIView
from stadtgedaechtnis_backend.services.serializer.serializers import *
from stadtgedaechtnis_backend.services.views import GZIPAPIView
from stadtgedaechtnis_backend.services.authentication.permissions import IsAuthenticatedOrReadOnlyOrModerated, \
    IsAuthenticatedOrModerated
from stadtgedaechtnis_backend.utils import replace_multiple
from django.utils.translation import ugettext_lazy as _


__author__ = 'Jan'


class StoryView(GZIPAPIView, GenericAPIView):
    """
    Base class for use with Stories
    """
    queryset = Story.objects.all()
    serializer_class = StoryWithAssetSerializer
    permission_classes = (IsAuthenticatedOrReadOnlyOrModerated, )


class StoryEmailView(StoryView, SingleObjectTemplateResponseMixin, BaseDetailView):
    """
    Sends an email for this object
    Needs the unique_id parameter present in order to work
    """
    permission_classes = (IsAuthenticatedOrModerated, )
    template_name = "stadtgedaechtnis/email.html"
    object = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        if not kwargs["email"]:
            return HttpResponseServerError()
        admin_url = request.build_absolute_uri(urlresolvers.reverse("admin:stadtgedaechtnis_backend_story_change", args=(self.object.id,)))
        context.update({"authorEmail": kwargs["email"],
                        "adminLink": admin_url})
        template_response = self.render_to_response(context)
        email_content = template_response.rendered_content
        if self.send_mail(email_content):
            serializer = self.get_serializer(self.object)
            return Response(serializer.data)
        else:
            return HttpResponseServerError()

    @classmethod
    def send_mail(cls, html_content):
        """
        Sends an email with html content to the recipient specified in local_settings.py
        """
        recipient = settings.NEW_ENTRY_EMAIL_RECIPIENT
        if not recipient:
            raise ImproperlyConfigured("You must specify an e-mail recipient via the "
                                       "setting NEW_ENTRY_EMAIL_RECIPIENT in your local_settings.py")

        sender = settings.NEW_ENTRY_EMAIL_SENDER
        if not sender:
            raise ImproperlyConfigured("You must specify an e-mail sender via the "
                                       "setting NEW_ENTRY_EMAIL_SENDER in your local_settings.py")

        plain_content = replace_multiple(html_content, {
            "<br>": "\n",
            "<hr>": "",
            "<b>": "",
            "</b>": "",
        })

        subject = _("Neuer Eintrag")
        email = EmailMultiAlternatives(subject, plain_content, sender, [recipient])
        email.attach_alternative(html_content, "text/html")
        return email.send()


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