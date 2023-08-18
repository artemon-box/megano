from django.db import models


def seller_images_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/sellers/image_<id>/
    return 'sellers/image_{0}/{1}'.format(instance.id, filename)


class Seller(models.Model):
    """
    Модель продавца
    """
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=seller_images_directory_path)
    description = models.TextField(max_length=1000, blank=True)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=200)


