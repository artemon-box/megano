import os
import shutil
import time

from accountapp.models import User
from admin_settings.utils import ImportLogHelper as Log
from config.celery import app
from django.conf import settings
from django.core.files import File
from django.core.mail import send_mail
from shopapp.models import Category, Product, ProductSeller, Seller


@app.task()
def send_import_notification(result_list, error_list, email):
    subject = "Импорт товаров завершен"
    message = ""
    if error_list:
        message += f"Импорт товаров завершен с ошибками: {error_list}\n"
    if result_list:
        message += f"Импортированные товары: {result_list}.\n"
    else:
        message += "Товары не импортированы.\n"

    send_mail(subject, message, "admin@example.com", [email])


@app.task()
def import_json(data_tuples, email, seller_id, log_data):
    time.sleep(10)
    result_list, error_list = [], []
    user_id = log_data["user_id"]
    user = User.objects.get(id=user_id) if user_id else None
    import_id = log_data["import_id"]
    for data_tuple in data_tuples:
        file, file_name = data_tuple
        path = os.path.join(settings.BASE_DIR, "json_to_import", file_name)
        Log.info(user=user, import_id=import_id, message=f"Начат импорт из файла: {file_name}")
        destination_path = os.path.join(settings.BASE_DIR, "imported_files", "successful", file_name)
        try:
            for item in file:
                category, category_result = Category.objects.get_or_create(name=item["product"]["category"])
                if category_result:
                    Log.info(user=user, import_id=import_id, message=f"Создана категория {category}")
                product, product_result = Product.objects.get_or_create(
                    category=category,
                    name=item["product"]["name"],
                )
                if product_result:
                    Log.info(user=user, import_id=import_id, message=f"Создан товар {product}")
                    image_path = item["product"]["image"]
                    try:
                        product.image.save(f"{product.slug}", File(open(item["product"]["image"], "rb")), save=True)
                        product.save()
                        Log.info(user=user, import_id=import_id, message=f"Изображение {image_path}, загружено.")
                    except Exception:
                        message = f"Изображение {image_path}, не загружено!"
                        Log.warning(user=user, import_id=import_id, message=message)
                        error_list.append(message)
                product_seller, result = ProductSeller.objects.get_or_create(
                    product=product,
                    seller=Seller.objects.get(id=seller_id),
                    price=item["price"],
                    quantity=item["quantity"],
                )
                if result:
                    result_list.append(product.name)
                    Log.info(user=user, import_id=import_id, message=f"Товар {product} импортирован успешно.")
                else:
                    Log.info(user=user, import_id=import_id, message=f"Товар {product} уже есть.")
            Log.info(user=user, import_id=import_id, message=f'Импорт из файла "{file_name}" выполнен.')
        except Exception as err:
            destination_path = os.path.join(settings.BASE_DIR, "imported_files", "failed", file_name)
            error_list.append(err)
            Log.critical(user=user, import_id=import_id, message=f'Импорт из файла "{file_name}" НЕ выполнен!')
        finally:
            Log.info(user=user, import_id=import_id, message=f'Файл "{file_name}" перемещен в {destination_path}.')
            shutil.move(path, destination_path)

    if email:
        send_import_notification.delay(result_list, error_list, email)
        Log.info(
            user=user,
            import_id=import_id,
            message=f'Задача по отправке уведомления на "{email}" отправлена в очередь Celery.',
        )
