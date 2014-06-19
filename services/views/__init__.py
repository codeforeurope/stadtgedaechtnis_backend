from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework.views import APIView

__author__ = 'Jan'


class GZIPAPIView(APIView):
    @method_decorator(gzip_page)
    def dispatch(self, request, *args, **kwargs):
        return super(GZIPAPIView, self).dispatch(request, *args, **kwargs)