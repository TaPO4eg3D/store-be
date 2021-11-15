from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from . import models

# Register your models here.


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CategoryTranslation)
class CategoryTranslationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('open_builder',)

    # description functions like a model field's verbose_name
    @admin.display(description='Options Builder')
    def open_builder(self, instance):
        if not instance.id:
            return '-'

        return mark_safe(f'<a href="/builder/{instance.id}">OPEN BUILDER</a>')

@admin.register(models.HomePageSlide)
class HomePageSlideAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RecommendedProductSlide)
class RecommendedProductSlideAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ProductTranslation)
class ProductTranslationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(models.OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    pass
