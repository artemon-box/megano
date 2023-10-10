Консольная команда для запуска импорта товаров продавца из json-файлов
```
python manage.py importproductsellers
```
Запуск без аргументов. При этом будут имортированы все файлы из директории, указанной в параметре IMPORT_FILE_DIR файла настроек settings.py. При ее отсутсвии, будет выдана ошибка. 

Запуск с аргументами. Для запуска импорта конкретного файла указывается параметр -f 
и перечисляются имена файлов либо --files :
```
python manage.py importproductsellers -f file1.json file2.json
```
Для отправки уведомления о результатах импорта на email, указывается параметр -e <email_address> 
либо --email <email_address>. Если этот параметр не указывать, уведомление не отправляется.
```
python manage.py importproductsellers -e email@skillbox.com
```
Справка по команде:
```
python manage.py help importproductsellers
```