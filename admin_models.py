from django.contrib import admin
from stadtgedaechtnis_backend import models

__author__ = 'Jan'


class NewStory(models.Story):
    class Meta:
        proxy = True


class NewStoriesModelAdmin(admin.ModelAdmin):
    """
    Filters the stories to display only stories, which are marked temporary
    """

    def get_queryset(self, request):
        qs = super(NewStoriesModelAdmin, self).get_queryset(request)
        return qs.filter(temporary__exact=True)