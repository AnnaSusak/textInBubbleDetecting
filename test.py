import os
from google.cloud import vision
import io

# Установите путь к JSON-файлу учетных данных сервиса
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'lithe-willow-428116-r5-8fb0a06a023f.json'

# Инициализация клиента
client = vision.ImageAnnotatorClient()

# Загрузка изображения
with io.open('bubbles/bubble_0.jpg', 'rb') as image_file:
    content = image_file.read()

# Создание объекта Image
image = vision.Image(content=content)

# Вызов функции распознавания текста
response = client.text_detection(image=image)
texts = response.text_annotations

# Вывод распознанного текста
for text in texts:
    print('\n"{}"'.format(text.description))
