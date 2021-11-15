from django.db import models

# Create your models here.


class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now=True, db_index=True, editable=False)
    updated_at = models.DateTimeField(auto_now_add=True, db_index=True, editable=False)

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(max_length=120)
    parent = models.OneToOneField(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child',
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


class OrderProduct(TimeStampModel):
    order = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
    )
