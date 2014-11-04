from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.forms import Select
from django.utils.safestring import mark_safe

from stadtgedaechtnis_backend.models import Story


__author__ = 'Jan'


class NewStoriesModelAdmin(admin.ModelAdmin):
    """
    Filters the stories to display only stories, which are marked temporary
    """

    def get_queryset(self, request):
        qs = super(NewStoriesModelAdmin, self).get_queryset(request)
        return qs.filter(temporary__exact=True)


class AuthorAdminWidget(Select):
    def render(self, name, value, *args, **kwargs):
        output = super(AuthorAdminWidget, self).render(name, value, *args, **kwargs)
        email = ""
        if value is not '':
            try:
                author = get_user_model().objects.get(pk=value)
                email = author.email
            except get_user_model().DoesNotExist:
                pass

        output = output + mark_safe(' E-Mail: <a href="mailto:%s">%s</a>' % (email, email))
        return output


class StoryAdminForm(forms.ModelForm):
    class Meta:
        model = Story
        widgets = {
            'author': AuthorAdminWidget,
        }


class StoryModelAdmin(admin.ModelAdmin):
    form = StoryAdminForm