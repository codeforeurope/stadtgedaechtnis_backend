from django.contrib import admin
from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from stadtgedaechtnis_backend.admin_models import NewStoriesModelAdmin, NewStory, StoryModelAdmin

from stadtgedaechtnis_backend.models import *


class StadtgedaechtnisAdmin(admin.AdminSite):
    """
    Custom administration site for Stadtgedaechtnis.
    Provides views for importing entries and other maintenance tasks.
    """

    def get_urls(self):
        urls = super(StadtgedaechtnisAdmin, self).get_urls()
        my_urls = patterns('',
                           url(r'^import/', include('stadtgedaechtnis_backend.import_entries.urls')),
                           url(r'^new-entries/', TemplateView, name="new-entries"),
                           )
        return my_urls + urls


admin.site = StadtgedaechtnisAdmin()
admin.autodiscover()

site = admin.site

site.register(Story, StoryModelAdmin)
site.register(NewStory, NewStoriesModelAdmin)
site.register(Location)
site.register(Asset)
site.register(MediaSource)
site.register(Category)