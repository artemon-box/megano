from django.db import models
from singleton_model import SingletonModel


class SiteSettings(SingletonModel):
    """
    Модель настроек сайта. Унаследована от SingletonModel, что позволяет создать только один экземпляр класса.
    """
    max_discount = models.IntegerField(
        default=0,
        help_text='Максимальный размер скидки'
    )
    sale_start = models.DateField(
        default=None,
        auto_now_add=False,
        help_text='Дата начала акции/распродажи'
    )
    sale_end = models.DateField(
        default=None,
        auto_now_add=False,
        help_text='Дата окончания акции/распродажи'
    )
    goods_on_page = models.IntegerField(
        default=1,
        help_text='Кол-во товаров на странице'
    )
    max_file_size = models.FloatField(
        default=100,
        help_text='Максимальный размер загружаемого файла, мБ'
    )
    send_bill = models.BooleanField(
        default=False,
        help_text='Отправить чек после оплаты'
    )
    send_goods_list = models.BooleanField(
        default=False,
        help_text='Отправить список товаров в корзине'
    )

    class Meta:
        db_table = 'site_settings' # имя таблицы