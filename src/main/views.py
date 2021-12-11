from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max, Min, Count, Value, OuterRef, DecimalField
from django.db.models.expressions import Subquery
from django.db.models.functions import Coalesce
from django.db.models.query import Prefetch

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

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


class OrderViewset(ModelViewSet):
    # TODO: Add permissions

    queryset = models.Order.objects.order_by('-created_at').prefetch_related(
        Prefetch(
            'order_products',
            models.OrderProduct.objects.select_related(
                'product',
            ),
        ),
    )

    serializer_class = serializers.OrderSerializer


class CreateOrderView(APIView):
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


class ConfirmOrderView(APIView):
    def post(self, request, *args, **kwargs):
        # TODO: Add IP check

        serializer = serializers.ConfirmOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        signature = serializer.calculate_signature()
        validated_data = serializer.validated_data

        if not validated_data:
            raise ValidationError('Something is wrong!')

        if signature != validated_data['m_sign']:
            return Response(f'{validated_data["m_orderid"]}|error')

        if validated_data['m_status'] == 'success':
            models.Order.objects.filter(
                id=validated_data['m_orderid'],
            ).update(
                is_payed=True,
            )

            # TODO: Send an email?

            return Response(f'{validated_data["m_orderid"]}|success')


class CurrencyViewset(GenericViewSet):
    queryset = models.Currency.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.CurrencySerializer

        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        default_currency = queryset.filter(
            is_default=True,
        ).annotate(
            rate=Value(1),
        ).first()

        if not default_currency:
            raise ValidationError('No default currency!')
        
        available_currencies = tuple(queryset.exclude(
            id=default_currency.pk,
        ).annotate(
            rate=Coalesce(
                Subquery(
                    models.CurrencyRate.objects.filter(  # type: ignore
                        source=default_currency.pk,
                        target=OuterRef('pk'),
                    ).values('rate')[:1],
                    output_field=DecimalField(),
                ), 1,
                output_field=DecimalField(),
            )
        ))

        serializer_class = self.get_serializer_class()

        return Response({
            'default': serializer_class(default_currency).data,
            'available': serializer_class(available_currencies, many=True).data
        })
