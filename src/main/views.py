from django.db.models import Max, Min, Count

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet 

from rest_framework.response import Response

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers, filters

# Create your views here.


class PopularProductsView(APIView):
    def get(*args, **kwargs):
        queryset = models.Product.objects.annotate(
            order_count=Count('orders'),
        ).order_by('order_count')[:10]

        serializer = serializers.ProductSerializer(queryset, many=True)
        return Response(serializer.data)


class PriceRangeView(APIView):
    def get(self, *args, **kwargs):
        caps = models.Product.objects.aggregate(
            min_cap=Min('price'),
            max_cap=Max('price'),
        )

        return Response(caps)


class CategoryViewset(ModelViewSet):
    queryset = models.Category.objects.filter(
        parent__isnull=True,
    )

    serializer_class = serializers.CategorySerializer

    def get_queryset(self):
        if self.action == 'retrieve':
            return models.Category.objects.all()

        return super().get_queryset()


class ProductViewset(ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    filterset_class = filters.ProductFilter

    search_fields = (
        'name',
    )


class HomePageSlideViewset(ModelViewSet):
    queryset = models.HomePageSlide.objects.order_by('order')
    serializer_class = serializers.HomePageSlideSerializer


class RecommendedProductSlideViewset(ModelViewSet):
    queryset = models.RecommendedProductSlide.objects.order_by('order').select_related('product')
    serializer_class = serializers.RecommendedProductSlideSerializer
