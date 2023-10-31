from accountapp.models import User
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


class ImportLog(models.Model):
    class Level(models.TextChoices):
        info = "INFO"
        warning = "WARNING"
        error = "ERROR"
        critical = "CRITICAL"

    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.SET_NULL, null=True)
    import_id = models.CharField(max_length=36, verbose_name="Идентификатор импорта")
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=Level.choices, verbose_name="Уровень логирования")
    message = models.TextField(verbose_name="Сообщение лога")

    class Meta:
        ordering = ["timestamp"]
