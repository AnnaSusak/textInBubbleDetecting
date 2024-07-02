import os

import cv2
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
async def process_bubble(bubble):
    _, bubble_bytes = cv2.imencode('.jpg', bubble)
    content = bubble_bytes.tobytes()
    # Создание объекта Image для Google Vision API
    image = vision.Image(content=content)

    # Вызов функции распознавания текста
    response = client.text_detection(image=image)
    if not response.text_annotations:
        return [(0, 0), (0, 0)], "", ""
    text_annotation = response.text_annotations[0]
    description = text_annotation.description
    vertices = text_annotation.bounding_poly.vertices
    polygon = [(vertex.x, vertex.y) for vertex in vertices]
    return polygon, description, text_annotation.locale
