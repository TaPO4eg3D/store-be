from hashlib import sha256

from constance import config

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_recursive.fields import RecursiveField

from . import models


class CategorySerializer(serializers.ModelSerializer):
    child = RecursiveField(read_only=True)

    class Meta:
        model = models.Category
        fields = (
            'id',
            'name',
            'child',
        )


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = (
            'id',
            'name',
        )


class UpdateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = (
            'additional_options',
        )


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()

    class Meta:
        model = models.Product
        fields = (
            'id',
            'name',
            'price',
            'discount_price',
            'description',
            'preview_image',
            'category',
            'additional_options',
        )

class HomePageSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HomePageSlide
        fields = (
            'id',
            'image',
            'order',
        )


class RecommendedProductSlideSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = models.RecommendedProductSlide
        fields = (
            'id',
            'product',
            'order',
        )


class CreateOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=4, decimal_places=2)

    selected_items = serializers.JSONField()
    selected_items_meta = serializers.JSONField()


class CreateOrderSerializer(serializers.Serializer):
    items = serializers.ListSerializer(
        child=CreateOrderItemSerializer(),
    )


class ConfirmOrderSerializer(serializers.Serializer):
    m_operation_id = serializers.IntegerField()
    m_operation_ps = serializers.IntegerField()
    m_operation_date = serializers.DateTimeField()
    m_operation_pay_date = serializers.DateTimeField()
    m_shop = serializers.IntegerField()
    m_orderid = serializers.IntegerField()
    m_amount = serializers.DecimalField(max_digits=4, decimal_places=2)
    m_cur = serializers.CharField()
    m_desc = serializers.CharField()
    m_status = serializers.CharField()
    m_sign = serializers.CharField()

    client_email = serializers.CharField()

    def calculate_signature(self):
        data = self.validated_data

        if not data:
            raise ValidationError('Something really wrong!')

        signature_fields = (
            data['m_operation_id'],
            data['m_operation_ps'],
            data['m_operation_date'],
            data['m_operation_pay_date'],
            data['m_shop'],
            data['m_orderid'],
            data['m_amount'],
            data['m_curr'],
            data['m_desc'],
            data['m_status'],
            config.PAYEER_KEY,  #type: ignore
        )

        signature_string = ':'.join([
            str(field)
            for field in signature_fields
        ]).encode('utf-8')

        signature = sha256(signature_string).hexdigest().upper()

        return signature


class CurrencySerializer(serializers.ModelSerializer):
    rate = serializers.DecimalField(
        max_digits=4,
        decimal_places=2,
    )

    class Meta:
        fields = ('id', 'code', 'display', 'rate',)
        model = models.Currency
