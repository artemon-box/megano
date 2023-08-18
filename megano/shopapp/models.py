from django.db import models
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.core.cache import cache


class Category(models.Model):
    name = models.CharField(max_length=255)
    sort_index = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sort_index']


# class Banner(models.Model):
#     title = models.CharField(max_length=255)
#     image = models.ImageField(upload_to='banners/')
#     active = models.BooleanField(default=False)
#     sorting_index = models.IntegerField(default=0)
#
#     def __str__(self):
#         return self.title


class Product(models.Model):
    pass
