from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Area
from .serializers import AreaSerializer, SubsSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin


# Create your views here.

# class AreaListView(ListAPIView):
#     serializer_class = AreaSerializer
#     queryset = Area.objects.filter(parent=None)
#
#
# class AreaDetailView(RetrieveAPIView):
#     serializer_class = SubsSerializer
#     queryset = Area.objects.all()


class AreaViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    pagination_class = None

    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubsSerializer
