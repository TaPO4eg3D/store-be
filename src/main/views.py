from django.db import transaction
from django.db.models import Max, Min, Count

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet 

from rest_framework.response import Response

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers, filters, utils

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


class OrderView(APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = serializers.CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self._create_order()
        self._create_order_items(order, serializer.validated_data)

        price = utils.get_order_price(order.pk)
        payeer_url = utils.get_payeer_url(utils.PayeerData(
            order_id=order.pk,
            amount=price,
            currency='USD',  # TODO: Get it from the request
            description=f'Payment of Order #{order.pk}'
        ))

        return Response({
            'order_id': order.pk,
            'price': price,
            'url': payeer_url,
        })

    def _create_order(self) -> models.Order:
        return models.Order.objects.create()

    def _create_order_items(self, order: models.Order, validated_data: dict) -> list[models.OrderProduct]:
        order_items = list()

        for item in validated_data['items']:
            order_items.append(
                models.OrderProduct(
                    order_id=order.pk,
                    amount=item['amount'],
                    product_id=item['product_id'],
                    selected_items=item['selected_items'],
                    selected_items_meta=item['selected_items_meta'],
                ),
            )

        models.OrderProduct.objects.bulk_create(order_items)

        return order_items
