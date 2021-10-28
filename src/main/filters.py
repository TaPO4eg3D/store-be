from django_filters import rest_framework as filters
from django_filters.filters import BaseInFilter, NumberFilter, BaseInFilter

from . import models


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class ProductFilter(filters.FilterSet):
    id = NumberInFilter(field_name='id', lookup_expr='in')

    class Meta:
        model = models.Product
        fields = (
            'category',
        )
