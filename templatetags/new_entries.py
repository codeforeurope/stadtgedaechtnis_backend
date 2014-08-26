__author__ = 'jpi'

from django import template

from stadtgedaechtnis_backend.models import Story


register = template.Library()


class NewEntriesCountNode(template.Node):
    """
    Node that renders the list of log entries to the template.
    """
    def __init__(self, varname):
        self.varname = varname

    def __repr__(self):
        return "<ImportLog Node>"

    def render(self, context):
        context[self.varname] = Story.objects.filter(temporary__exact=True).count()
        return ''


@register.tag
def get_new_entries_count(parser, token):
    """
    Populates a template variable with the number of newly created entries.
    :param parser:
    :param token:
    :return:

    Usage:

        {% get_new_entries_count as [variable name] %}

    Example:

        {% get_new_entries_count as new_entries %}

    """
    tokens = token.contents.split()
    if len(tokens) < 3 or not tokens[1] == "as":
        raise template.TemplateSyntaxError(
            "Usage: 'get_new_entries_count as [variable name]'"
        )
    varname = tokens[2]
    return NewEntriesCountNode(varname)