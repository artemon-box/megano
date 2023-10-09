from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from taggit.managers import TaggableManager
from django.template.defaultfilters import slugify


def category_images_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/categories/image_<id>/
    return "categories/image_{0}/{1}".format(instance.id, filename)


def product_images_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/products/image_<slug>/
    return "products/image_{0}/{1}".format(instance.slug, filename)


def product_extra_images_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/products/image_<slug>/extra_images/
    return "products/image_{0}/extra_images/{1}".format(instance.product.slug, filename)


def seller_images_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/sellers/image_<slug>/
    return "sellers/image_{0}/{1}".format(instance.slug, filename)


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель товаров"""

    category = models.ForeignKey("Category", related_name="products", on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to=product_images_directory_path, blank=True)
    description = models.TextField(blank=True)
    available = models.BooleanField(default=True)
    sellers = models.ManyToManyField("Seller", through="ProductSeller")
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # дата добавления товара для сортировки по новизне

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    @property
    def popularity(self):
        return len(str(self.description))  # здесь будет популярность = кол-во оплаченных заказов товара

    @property
    def reviews(self):
        return ProductReview.objects.filter(product=self).count()  # кол-во отзывов

    def get_absolute_url(self):
        return reverse("shopapp:product_detail", args=[self.id, self.slug])


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user} for {self.product}"


class ExtraImage(models.Model):
    """
    Модель, содержащая в себе дополнительные изображения для каждого товара
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="extra_images",
        default=None,
    )
    image = models.ImageField(upload_to=product_extra_images_directory_path, blank=True)

    def __str__(self):
        return "Extra images: " + self.product.name


class ProductSeller(models.Model):
    """
    Промежуточная таблица для хранения данных о товаре, его цене и количестве у конкретного продавца.

    """

    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    seller = models.ForeignKey("Seller", on_delete=models.RESTRICT)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="цена товара у продавца")
    quantity = models.IntegerField(verbose_name="количество", default=1)
    free_delivery = models.BooleanField(default=False)  # бесплатная доставка (для фильтрации на странице каталога)
    is_limited_edition = models.BooleanField(default=False, verbose_name="Ограниченный тираж")

    class Meta:
        verbose_name = "товар у продавца"
        verbose_name_plural = "товары у продавцов"
        unique_together = (
            "product",
            "seller",
        )

    def __str__(self):
        return f"{self.product} by {self.seller} for ${self.price}"


class Seller(models.Model):
    """
    Модель продавец
    """

    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, default=None)
    image = models.ImageField(upload_to=seller_images_directory_path)
    delivery_method = models.CharField(max_length=100, default=None)
    payment_method = models.CharField(max_length=100, default=None)
    description = models.TextField(max_length=1000, blank=True)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=200)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
        ]

    def get_absolute_url(self):
        return reverse("shopapp:seller_detail", args=[self.id, self.slug])

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Модель категории товаров
    """

    name = models.CharField(max_length=255)
    tags = TaggableManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Feature(models.Model):
    """
    Тип характеристики
    """

    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="categories",
        on_delete=models.CASCADE,
    )
    features_group = models.ForeignKey(
        "self",
        verbose_name="Группа характеристик",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100, verbose_name="Характеристика")

    class Meta:
        ordering = ["category", "name"]
        unique_together = ["category", "name"]

    def __str__(self):
        return f"{self.category.name} | {self.name}"


class FeatureValue(models.Model):
    """
    Таблица валидных значений. Выбираем значения из выпадающего списка.
    """

    feature = models.ForeignKey(Feature, verbose_name="Характеристика", on_delete=models.CASCADE)
    value = models.CharField(max_length=100, verbose_name="Значение")

    class Meta:
        ordering = ["feature", "value"]

    def __str__(self):
        return f"{self.feature} | {self.value}"


class ProductFeature(models.Model):
    """
    Характеристика товара
    """

    product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        related_name="features",
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE)
    feature = models.ForeignKey(
        Feature,
        verbose_name="Характеристика",
        related_name="features",
        on_delete=models.CASCADE,
    )
    value = models.ForeignKey(
        FeatureValue,
        verbose_name="Значение",
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        ordering = ["feature"]

    def __str__(self):
        return f"{self.feature} | {self.value.value}"


class AllowedRelation(models.Model):
    """
    Таблица соответсвий, категория -> характеристика -> значение, для каждого товара.
    Используется в js-скрипте в админке для реализации связанного выбора.
    """

    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, verbose_name="Характеристика", on_delete=models.CASCADE)
    value = models.ForeignKey(FeatureValue, verbose_name="Значение", on_delete=models.CASCADE)

    class Meta:
        ordering = ["category", "feature", "value"]

    def __str__(self):
        return f"{self.category} {self.feature} {self.value}"


DISCOUNT_TYPE = [
    ("p", "Discount for product"),
    ("s", "Discount for set"),
    ("c", "Discount for cart"),
]

DISCOUNT_WEIGHT = [
    ("l", "Light"),
    ("m", "Medium"),
    ("h", "Heavy"),
]


class Discount(models.Model):
    title = models.CharField(verbose_name="Title", max_length=32, null=True, help_text="Название скидки")
    description = models.TextField(
        verbose_name="Description", max_length=255, null=True, blank=True, help_text="Описание скидки"
    )
    type = models.CharField(
        max_length=2, choices=DISCOUNT_TYPE, default="p", verbose_name="Discount type", help_text="Тип скидки"
    )
    weight = models.CharField(
        max_length=1, choices=DISCOUNT_WEIGHT, default="l", verbose_name='Discount "weight"', help_text="'Вес' скидки"
    )
    percent = models.IntegerField(
        verbose_name="Percent",
        validators=[MinValueValidator(0), MaxValueValidator(99)],
        default=None,
        null=True,
        blank=True,
        help_text="Процент скидки",
    )
    discount_volume = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Discount volume",
        null=True,
        blank=True,
        default=None,
        help_text="Сумма предоставляемой скидки",
    )
    cart_numbers = models.IntegerField(
        verbose_name="Goods in Cart",
        validators=[MinValueValidator(0)],
        default=0,
        null=True,
        blank=True,
        help_text="Минимальное кол-во товаров в корзине для скидки",
    )
    cart_price = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        verbose_name="All cart price",
        null=True,
        blank=True,
        default=0,
        help_text="Минимальная стоиомсть всей корзины " "для предоставления скидки",
    )
    products = models.ManyToManyField(ProductSeller, related_name="products", default=None, blank=True)
    categories = models.ManyToManyField(Category, related_name="group", default=None, blank=True)
    start = models.DateField(verbose_name="Start", null=True, blank=True, help_text="Дата начала действия скидки")
    end = models.DateField(verbose_name="End", null=True, blank=True, help_text="Дата окончания действия скидки")
    is_active = models.BooleanField(default=False, help_text="Статус скидки (активна/не активна)")

    def __str__(self):
        return self.title
