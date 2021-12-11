from django.db import models

# Create your models here.


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now=True, db_index=True, editable=False)
    updated_at = models.DateTimeField(auto_now_add=True, db_index=True, editable=False)

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(max_length=120)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
    )

    def __str__(self) -> str:
        return self.name


class CategoryTranslation(models.Model):
    language_code = models.CharField(max_length=6)

    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return self.language_code


class Product(TimeStampModel):
    name = models.CharField(max_length=512)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    description = models.TextField(
        null=True,
        blank=True,
    )

    preview_image = models.ImageField(
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
    )

    additional_options = models.JSONField(
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.name


class HomePageSlide(TimeStampModel):
    image = models.ImageField()
    order = models.PositiveSmallIntegerField(db_index=True)

    def __str__(self) -> str:
        return f'Slide #{self.order}'


class RecommendedProductSlide(TimeStampModel):
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='recommended_slides',
    )
    order = models.PositiveSmallIntegerField(db_index=True)

    def __str__(self) -> str:
        return f'Slide #{self.order}'


class ProductTranslation(models.Model):
    language_code = models.CharField(max_length=6)

    name = models.CharField(max_length=512)
    description = models.TextField(
        null=True,
        blank=True,
    )


class ProductImage(models.Model):
    """
    Product can have several images to display
    """
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='product_images',
    )
    image = models.ImageField()


class Order(TimeStampModel):
    products = models.ManyToManyField(
        to=Product,
        through='OrderProduct',
        related_name='orders',
    )

    is_payed = models.BooleanField(
        default=False,
        help_text='Has been payed through Payeer',
    )


class OrderProduct(TimeStampModel):
    order = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
        related_name='order_products',
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='order_products',
    )

    amount = models.PositiveIntegerField()

    selected_items = models.JSONField(
        null=True,
        blank=True,
    )
    selected_items_meta = models.JSONField(
        null=True,
        blank=True,
    )


class Currency(models.Model):
    code = models.CharField(max_length=20)
    display = models.CharField(max_length=120)

    is_default = models.BooleanField(
        default=False,
    )

    def __str__(self) -> str:
        return f'{self.code} ({self.display})'


class CurrencyRate(models.Model):
    source = models.ForeignKey(
        to=Currency,
        on_delete=models.CASCADE,
        related_name='source_rates',
    )
    target = models.ForeignKey(
        to=Currency,
        on_delete=models.CASCADE,
        related_name='target_rates',
    )

    rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
    )
