import os

import cv2
from google.cloud import vision
import io
from PIL import Image, ImageDraw, ImageFont
from roboflow import Roboflow

# Установите путь к JSON-файлу учетных данных сервиса
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'lithe-willow-428116-r5-8fb0a06a023f.json'
rf = Roboflow(api_key="hlfVQnRCETvjVCNGVJoh")
project = rf.workspace().project("bubble-text-detector")
model = project.version(3).model

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
async def process_bubble(bubble, a):
    _, bubble_bytes = cv2.imencode('.jpg', bubble)
    content = bubble_bytes.tobytes()
    temp_path = 'temp/temp.jpg'
    with open(temp_path, 'wb') as f:
        f.write(content)
    polygon = [[(a[0] + int(i['x']) - i['width'] // 2, a[1] + int(i['y']) - i['height'] // 2), (a[0] + int(i['x']) + i['width'] // 2, a[1] + int(i['y']) + i['height'] // 2)] for i in model.predict(temp_path, confidence=50, overlap=30).json()['predictions']]
    # Создание объекта Image для Google Vision API
    image = vision.Image(content=content)


    # Вызов функции распознавания текста
    response = client.text_detection(image=image)
    if not response.text_annotations:
        return [(0, 0), (0, 0)], "", ""
    text_annotation = response.text_annotations[0]
    description = text_annotation.description
    # vertices = text_annotation.bounding_poly.vertices
    # minx = 1000
    # miny = 1000
    # maxx = -1000
    # maxy = -1000
    # for vertex in vertices:
    #     minx = min(minx, vertex.x)
    #     miny = min(miny, vertex.y)
    #     maxx = max(maxx, vertex.x)
    #     maxy = max(maxy, vertex.y)
    # polygon = [[(minx + a[0], miny + a[1]), (maxx + a[0], maxy + a[1])]]
    return polygon, description, text_annotation.locale
