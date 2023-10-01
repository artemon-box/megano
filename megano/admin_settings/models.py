from django.db import models
from singleton_model import SingletonModel


class SiteSettings(SingletonModel):
    """
    Модель настроек сайта. Унаследована от SingletonModel, что позволяет создать только один экземпляр класса.
    """

    max_discount = models.IntegerField(default=0, help_text="Максимальный размер скидки")
    cache_time = models.IntegerField(default=1200, help_text="Время хранения кэша, сек")
    banner_time = models.IntegerField(default=20, help_text="Частота обновления банера, сек")
    goods_on_page = models.IntegerField(default=1, help_text="Кол-во товаров на странице")
    max_file_size = models.FloatField(default=100, help_text="Максимальный размер загружаемого файла, мБ")

    # send_bill = models.BooleanField(
    #     default=False,
    #     help_text='Отправить чек после оплаты'
    # )
    # send_goods_list = models.BooleanField(
    #     default=False,
    #     help_text='Отправить список товаров в корзине'
    # )

    class Meta:
        db_table = "site_settings"  # имя таблицы
