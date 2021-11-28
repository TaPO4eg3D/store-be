from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('currencies', views.CurrencyViewset)
router.register('categories', views.CategoryViewset)
router.register('products', views.ProductViewset)
router.register('home-page-slides', views.HomePageSlideViewset)
router.register('recommended-product-slides', views.RecommendedProductSlideViewset)

urlpatterns = [
    path('popular-products', views.PopularProductsView.as_view()),
    path('orders', views.CreateOrderView.as_view()),
    path('filters/price-range', views.PriceRangeView.as_view()),
    *router.urls,
]
