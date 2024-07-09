import os

import cv2
from google.cloud import vision
import io
from PIL import Image, ImageDraw, ImageFont
from roboflow import Roboflow

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'google_api.json'
rf = Roboflow(api_key="hlfVQnRCETvjVCNGVJoh")
project = rf.workspace().project("textfinder-b5oku")
model = project.version(1).model

client = vision.ImageAnnotatorClient()

input_folder = 'bubbles'
output_folder = 'painted_bubbles'
os.makedirs(output_folder, exist_ok=True)

font_path = 'arial.ttf'
font_size = 24

# Обработка изображений
async def process_bubble(bubble, a):
    _, bubble_bytes = cv2.imencode('.jpg', bubble)
    content = bubble_bytes.tobytes()
    temp_path = 'temp/temp.jpg'
    with open(temp_path, 'wb') as f:
        f.write(content)
    polygon = [[(a[0] + int(i['x']) - i['width'] // 2, a[1] + int(i['y']) - i['height'] // 2), (a[0] + int(i['x']) + i['width'] // 2, a[1] + int(i['y']) + i['height'] // 2 )] for i in model.predict(temp_path, confidence=75, overlap=30).json()['predictions']]
    # Создание объекта Image для Google Vision API
    image = vision.Image(content=content)


    # Вызов функции распознавания текста
    response = client.text_detection(image=image)
    if not response.text_annotations:
        print("ERROR", polygon)
        return None
    text_annotation = response.text_annotations[0]
    description = text_annotation.description
    vertices = text_annotation.bounding_poly.vertices

    minx, miny, maxx, maxy = int(min([p[0][0] for p in polygon])), int(min([p[0][1] for p in polygon])), int(max([p[1][0] for p in polygon])), int(max([p[1][1] for p in polygon]))
    polygon2 = [(minx + 0, miny + 0), (maxx + 0, maxy + 0)]

    return polygon, description, text_annotation.locale, polygon2
