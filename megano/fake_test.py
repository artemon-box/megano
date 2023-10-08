import requests
import json

# URL адрес веб-сервиса
url = 'http://localhost:5000/pay'

# JSON-данные для отправки
data = {
    'order_number': 123,
    'card_number': '1234567890123456',
    'amount': 100.0
}

# Отправка POST-запроса
response = requests.post(url, json=data)

# Парсинг JSON-ответа
result = response.json()

# Вывод результата
print(result)