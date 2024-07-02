import os
from google.cloud import vision
import io
from PIL import Image, ImageDraw, ImageFont

# Установите путь к JSON-файлу учетных данных сервиса
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'lithe-willow-428116-r5-8fb0a06a023f.json'

# Инициализация клиента
client = vision.ImageAnnotatorClient()

# Путь к папке с изображениями
input_folder = 'bubbles'
output_folder = 'painted_bubbles'
os.makedirs(output_folder, exist_ok=True)

# Шрифт для надписи (необходимо, чтобы файл шрифта был доступен)
font_path = 'arial.ttf'  # путь к файлу шрифта
font_size = 24

# Обработка изображений
for i in range(15):
    # Загрузка изображения
    with io.open(f'{input_folder}/bubble_{i}.jpg', 'rb') as image_file:
        content = image_file.read()

    # Создание объекта Image для Google Vision API
    image = vision.Image(content=content)

    # Вызов функции распознавания текста
    response = client.text_detection(image=image)
    if not response.text_annotations:
        continue  # Если текст не найден, пропустить это изображение

    # Извлечение первого найденного текста
    text_annotation = response.text_annotations[0]
    description = text_annotation.description
    vertices = text_annotation.bounding_poly.vertices

    # Открытие изображения с помощью PIL
    image = Image.open(io.BytesIO(content))
    draw = ImageDraw.Draw(image)

    # Получение координат вершин
    polygon = [(vertex.x, vertex.y) for vertex in vertices]

    # Закрашивание области в белый цвет
    draw.polygon(polygon, fill="white")

    # Загрузка шрифта
    font = ImageFont.truetype(font_path, font_size)

    # Позиция для текста (левая верхняя вершина области)
    x = vertices[0].x
    y = vertices[0].y

    # Написание текста красным цветом
    draw.text((x, y), description, fill="red", font=font)

    # Сохранение изображения
    image.save(f'{output_folder}/{i}.jpg')
    print(f'Image {i} processed and saved.')
