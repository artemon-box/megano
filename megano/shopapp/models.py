from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


class Product(models.Model):
    """ Модель товаров """

    category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    available = models.BooleanField(default=True)
    sellers = models.ManyToManyField('Seller', through='ProductSeller')

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shopapp:product_detail', args=[self.id, self.slug])


class ProductSeller(models.Model):
    """
    Промежуточная таблица для хранения данных о товаре, его цене и количестве у конкретного продавца.

    """
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    seller = models.ForeignKey('Seller', on_delete=models.RESTRICT)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена товара у продавца')
    quantity = models.IntegerField(verbose_name='количество', default=1)

    class Meta:
        verbose_name = 'товар у прордавца'
        verbose_name_plural = 'товары у продавцов'
        unique_together = ('product', 'seller',)


class Category(models.Model):
    """
    Модель категории товаров
    """
    name = models.CharField(max_length=255)
    sort_index = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sort_index']


def seller_images_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/sellers/image_<id>/
    return 'sellers/image_{0}/{1}'.format(instance.id, filename)


class Seller(models.Model):
    """
    модель продавец
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=seller_images_directory_path)
    description = models.TextField(max_length=1000, blank=True)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=200)
