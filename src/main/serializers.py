from rest_framework import serializers
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
    amount = serializers.IntegerField()

    selected_items = serializers.JSONField()
    selected_items_meta = serializers.JSONField()


class CreateOrderSerializer(serializers.Serializer):
    items = serializers.ListSerializer(
        child=CreateOrderItemSerializer(),
    )
