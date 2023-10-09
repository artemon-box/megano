import json
import os
import shutil

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from config.celery import app
import time

from shopapp.forms import FileImportForm
from shopapp.models import ProductSeller, Product, Seller, Category


@app.task()
def test_task(task_type):
    time.sleep(task_type * 10)
    return 'task completed!'


@app.task()
def import_json(file, file_name, email):
    result_list = []
    path = os.path.join(settings.BASE_DIR, 'json_to_import', file_name)
    try:
        for item in file:
            category, category_result = Category.objects.get_or_create(name=item['product']['category'])
            product, product_result = Product.objects.get_or_create(category=category, name=item['product']['name'])
            product_seller, result = ProductSeller.objects.get_or_create(
                product=product,
                seller=Seller.objects.get(id=item['seller']),
                price=item['price'],
                quantity=item['quantity'],
                )
            if result:
                result_list.append(product)
        destination_path = os.path.join(settings.BASE_DIR, 'imported_files', 'successful', file_name)
        shutil.move(path, destination_path)
    except Exception:
        destination_path = os.path.join(settings.BASE_DIR, 'imported_files', 'failed', file_name)
        shutil.move(path, destination_path)

    subject = 'Импорт товаров завершен'
    if result_list:
        message = f'Импорт товаров проведен.\n' \
                  f'Импортированные товары: {result_list}'
    else:
        message = 'Товары уже есть в базе данных.'

    # message = 'Импорт товаров завершен с ошибками: ...'  # Указать ошибки
    send_mail(subject, message, 'admin@example.com', [email])
