from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=255)
    sort_index = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


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
        ordering = ['sort_index']

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


class Seller(models.Model):
    """
    модель продавец
    """
