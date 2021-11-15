from django.db.models import Max, Min, Count

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet 

from rest_framework.response import Response

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers, filters

# Create your views here.


class PopularProductsView(APIView):
    """
    Get the list of Popular Products
    """
    def get(*args, **kwargs):
        queryset = models.Product.objects.annotate(
            order_count=Count('orders'),
        ).order_by('order_count')[:10]

        serializer = serializers.ProductSerializer(queryset, many=True)
        return Response(serializer.data)


class PriceRangeView(APIView):
    """
    Get the price range (used for filtering).
    Calculated by analyzing a price of each represented product
    """

    def get(self, *args, **kwargs):
        caps = models.Product.objects.aggregate(
            min_cap=Min('price'),
            max_cap=Max('price'),
        )

        return Response(caps)


class CategoryViewset(ModelViewSet):
    """
    Get list of all available categories
    """
    queryset = models.Category.objects.filter(
        parent__isnull=True,
    )

    serializer_class = serializers.CategorySerializer

    def get_queryset(self):
        if self.action == 'retrieve':
            return models.Category.objects.all()

        return super().get_queryset()


class ProductViewset(ModelViewSet):
    """
    Get list of products
    """
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

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update',):
            return serializers.UpdateProductSerializer

        return super().get_serializer_class()


class HomePageSlideViewset(ModelViewSet):
    """
    Get sides for Home Page slider
    """
    queryset = models.HomePageSlide.objects.order_by('order')
    serializer_class = serializers.HomePageSlideSerializer


class RecommendedProductSlideViewset(ModelViewSet):
    """
    Get slides for Recommended Products slider
    """
    queryset = models.RecommendedProductSlide.objects.order_by('order').select_related('product')
    serializer_class = serializers.RecommendedProductSlideSerializer
