__author__ = 'jpi'


from rest_framework.generics import GenericAPIView


class MultipleRequestSerializerAPIView(GenericAPIView):
    """
    APIView that provides functionality to get a different serializer,
    based on the request method.
    """

    serializer_classes = None   # must be a dictionary in the form { "GET": SerializerClass1,
                                # "POST": SerializerClass2 and so on }

    def get_serializer(self, instance=None, data=None,
                       files=None, many=False, partial=False):
        method = self.request.method.upper()

        try:
            self.serializer_class = self.serializer_classes[method]
        except KeyError:
            pass

        return super(MultipleRequestSerializerAPIView, self).get_serializer(instance, data, files, many, partial)