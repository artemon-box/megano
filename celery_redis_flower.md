1. Обновить зависимости из файла requirements.txt:
    ```
    pip install -r requirements.txt
    ```
2. Выполнить команду:
   ```
   python manage.py migrate django_celery_results   
   ```
3. Установить Docker.

3. Старт redis и flower:
    ```
   docker-compose up --build # сборка контейнеров и старт
   docker-compose up         # старт контейнеров
    ```
   Также контейнеры можно запускать из Docker Desktop:

   ![](/megano/static/for_markdown/docker_run.png)
4. Старт celery log-level info:
   ```
   celery -A config worker -l info
   ```
   команда вводится из директории /megano.