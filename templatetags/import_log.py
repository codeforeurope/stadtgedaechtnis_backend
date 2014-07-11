__author__ = 'jpi'

from django import template
from stadtgedaechtnis_backend.models import ImportLogEntry

register = template.Library()


class ImportLogNode(template.Node):
    """
    Node that renders the list of log entries to the template.
    """
    def __init__(self, varname, limit=None):
        self.limit = limit
        self.varname = varname

    def __repr__(self):
        return "<ImportLog Node>"

    def render(self, context):
        if self.limit is None:
            context[self.varname] = ImportLogEntry.objects.all()
        else:
            context[self.varname] = ImportLogEntry.objects.all()[:int(self.limit)]
        return ''


@register.tag
def get_import_log(parser, token):
    """
    Populates a template variable with the import logs.
    :param parser:
    :param token:
    :return:

    Usage:

        {% get_import_log [Optional: limit] as [variable name] %}

    Example:

        {% get_import_log as log %}
        {% get_import_log 10 as log %}

    """
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise template.TemplateSyntaxError(
            "'get_import_log' requires at least one parameter."
        )
    if not tokens[1].isdigit():
        if not tokens[1] == "as":
            raise template.TemplateSyntaxError(
                "Usage: 'get_import_log [Optional: limit] as [variable name]'"
            )
        limit = None
        varname = tokens[2]
    else:
        if not tokens[2] == "as":
            raise template.TemplateSyntaxError(
                "Usage: 'get_import_log [Optional: limit] as [variable name]'"
            )
        limit = int(tokens[1])
        varname = tokens[3]
    return ImportLogNode(varname, limit)