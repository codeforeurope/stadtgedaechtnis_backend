from stadtgedaechtnis_backend.import_entries.importers import *

from django.views.generic import TemplateView, View
from django.http.response import HttpResponseServerError, HttpResponse


__author__ = 'jpi'


class SimpleJSONImport(TemplateView):
    """
    Imports entries from the standard JSON file supplied by Digitales Stadtgedaechtnis
    """
    source = ""
    template_name = "admin/import_result.html"

    def __init__(self, **kwargs):
        super(SimpleJSONImport, self).__init__(**kwargs)
        # set importer class with source
        self.importer = JSONAllEntriesImporter(self.source)

    def get(self, request, *args, **kwargs):
        # import the entries
        self.importer.do_import()
        # render template
        return super(SimpleJSONImport, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SimpleJSONImport, self).get_context_data(**kwargs)
        # Add succeeded and failed imports
        context['success_import'] = self.importer.success_entries
        context['fail_import'] = self.importer.failed_entries
        context['exist_import'] = self.importer.exist_entries
        return context


class ImportEntry(View):
    """
    Imports one specific entry to a specific location
    """

    source = ""

    def get(self, request, *args, **kwargs):
        try:
            importer = JSONOneEntryImporter(self.source, kwargs["id"], kwargs["location"])
            importer.do_import()
        except ValueError:
            return HttpResponseServerError()

        if len(importer.success_entries) > 0:
            return HttpResponse()
        else:
            return HttpResponseServerError()
