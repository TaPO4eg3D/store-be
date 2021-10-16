from django.contrib import admin

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
    pass


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
