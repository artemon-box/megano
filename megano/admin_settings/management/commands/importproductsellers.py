import json
import os
import shutil
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand
from shopapp.tasks import import_json

PATH_FILES = settings.IMPORT_FILE_DIR


class Command(BaseCommand):
    help = "Загрузка товаров продавца из файлов/файла."

    def add_arguments(self, parser):
        parser.add_argument(
            '-e',
            '--email',
            help='Для отправки уведомления на email укажите адрес электронной почты. Если аргумент не заполнен,'
                 'уведомление не отправляется.'
        )
        parser.add_argument(
            '-f',
            '--files',
            nargs='*',
            help='Для загрузки из конкретных файлов, укажите имя файла (имена файлов через пробел). Если аргумент '
                 'не заполнен, загружаются все файлы из каталога по умолчанию.'
        )

    def handle(self, *args, **options):
        self.stdout.write('START')
        email = options['email']
        input_files = options['files']
        files = []
        data_tuples = []
        if input_files:
            self.stdout.write(f'В аргументы команды указаны файлы: {input_files}')
            # Проверяем существуют ли указанные файлы
            for file in input_files:
                path = os.path.join(PATH_FILES, file)
                try:
                    if os.path.isfile(path):
                        files.append(file)
                        self.stdout.write(self.style.SUCCESS(f'Файл "{file}" добавлен в список.'))
                    else:
                        raise FileNotFoundError(f'Файл "{file}" не существует.')
                except FileNotFoundError as err:
                    self.stderr.write(f'{err.__class__.__name__}: {err}')
        else:
            # Если команда введена без указания файлов, получаем все файлы из директории.
            files = self._get_list_files()
            self.stdout.write(f'В аргументы команды файлы не указаны, загружаем все файлы из директории. {files}')
        # Обработка файлов и запуск импорта
        if files:
            for file in files:
                path = os.path.join(PATH_FILES, file)
                try:
                    with open(path, 'r') as json_file:
                        products_from_json = json.load(json_file)
                        data_tuples.append((products_from_json, file))
                        self.stdout.write(self.style.SUCCESS(f'Файл "{file}" обработан.'))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    self.stderr.write(f'Файл "{file}" не соответствует формату JSON')
                    destination_path = os.path.join(settings.BASE_DIR, 'imported_files', 'failed', file)
                    shutil.move(path, destination_path)
            if data_tuples:
                import_json.delay(data_tuples, email)
                self.stdout.write(self.style.SUCCESS('Импорт запущен.'))
            else:
                self.stderr.write('Ни один из файлов не прошел валидацию. Импорт отменен.')
        else:
            self.stderr.write('Нет файлов для загрузки.')
        self.stdout.write('END')

    def _get_list_files(self) -> List:
        if os.path.exists(PATH_FILES):
            return os.listdir(PATH_FILES)
        return []
