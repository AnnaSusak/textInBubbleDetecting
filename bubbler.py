import asyncio
from PIL import Image, ImageDraw
from flask import Flask, render_template, request, send_file, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from roboflow import Roboflow
import supervision as sv
import cv2
import bubbler
from google.cloud import translate_v2 as translate
import numpy as np
from openai import OpenAI
import json
import requests


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BUBBLES_FOLDER'] = 'bubbles'
app.config['TEMP_FOLDER'] = 'temp'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'lithe-willow-428116-r5-8fb0a06a023f.json'
# Ensure the upload and bubbles directories exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['BUBBLES_FOLDER']):
    os.makedirs(app.config['BUBBLES_FOLDER'])

# Ensure the temp directory exists
if not os.path.exists(app.config['TEMP_FOLDER']):
    os.makedirs(app.config['TEMP_FOLDER'])


with open('luka_api_keys.json', 'r', encoding='utf-8') as file:
    api_keys = json.load(file)

# Initialize Roboflow model
# rf = Roboflow(api_key=api_keys['roboflow'])
# project = rf.workspace().project("manwgaspeechbubble")
# model = project.version(1).model
rf = Roboflow(api_key=api_keys['roboflow'])
project = rf.workspace().project("cut_the_bubble")
model = project.version(1).model

client = OpenAI(
    api_key=api_keys['chat_gpt']
)

url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
data = {
    "yandexPassportOauthToken": api_keys['yandex']
}

yandex_token = 'Bearer ' + requests.post(url, json=data).json()['iamToken']


def get_average_color(image, x1, y1, x2, y2):
    height, width, _ = image.shape
    x1 = max(1, x1)
    y1 = max(1, y1)
    x2 = min(width - 2, x2)
    y2 = min(height - 2, y2)
   
    colors = []
    for x in range(x1 - 1, x2 + 2):
        colors.append(image[y1 - 1, x])
        colors.append(image[y2 + 1, x])
        
    for y in range(y1, y2 + 1):
        colors.append(image[y, x1 - 1])
        colors.append(image[y, x2 + 1])
        
    colors = np.array(colors)
    average_color = np.mean(colors, axis=0)
    
    return np.round(average_color).astype(int)[::-1]

def predicter(path):
    result = model.predict(path, confidence=60, overlap=30).json()
    predictions = [(pred['x'], pred['y'], pred['width'], pred['height'], pred['confidence']) for pred in
                   result['predictions']]

    # Load the image
    image = cv2.imread(path)

    tasks = []
    for i, (x, y, width, height, confidence) in enumerate(predictions):
        x1 = int(x - width / 2)
        y1 = int(y - height / 2)
        x2 = int(x + width / 2)
        y2 = int(y + height / 2)

        # Crop the bubble from the image
        bubble = image[y1:y2, x1:x2]
        tasks.append(bubbler.process_bubble(bubble, (x1, y1)))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    loop.close()
    while None in results:
        results.remove(None)
    for i, result in enumerate(results):
        print("RESULT", result)
        bubble_info = create_overlays_for_bubble(image, result[0], str(i))
        for j, coord in enumerate(result[0]):
            coord.append(bubble_info[j]['filename'])
            result[0][j] = coord
        print(result)
        results[i] = result
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        bubbles = predicter(path)
        print(bubbles)
        return render_template('uploaded.html', filename=filename, bubbles=bubbles)

def create_overlays_for_bubble(image, coordinates, bubble_name):
    print("COORDINATES", coordinates)
    overlay_filenames = []

    if not os.path.exists(app.config['TEMP_FOLDER']):
        os.makedirs(app.config['TEMP_FOLDER'])

    for i, coords in enumerate(coordinates):
        coords = [(int(x), int(y)) for x, y in coords]
        print(coords)
        
        overlay = Image.new('RGBA', (coords[1][0] - coords[0][0], coords[1][1] - coords[0][1]), (*get_average_color(image, coords[0][0], coords[0][1], coords[1][0], coords[1][1]), 255))
        overlay_filename = f"{os.path.splitext(bubble_name)[0]}_overlay_{i}.png"
        overlay_path = os.path.join(app.config['TEMP_FOLDER'], overlay_filename)
        overlay.save(overlay_path)
        overlay_filenames.append({'filename': overlay_filename, 'coords': coords})

    return overlay_filenames

@app.route('/uploads/<filename>')
def send_uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/temp/<filename>')
def send_temp_file(filename):
    return send_file(os.path.join(app.config['TEMP_FOLDER'], filename))

translate_client = translate.Client()


@app.route('/translate', methods=['POST'])
def translate():
    engine = request.args.get('engine')
    from_lang = request.args.get('from')
    to_lang = request.args.get('to')
    data = request.get_json()
    text = data.get('text')

    if from_lang == to_lang:
        return jsonify({'translation': text})
    

    if engine == 'ChatGPT3.5':
        try:
            response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
            {"role": "system", "content": "You are a translator. Say only translated words without quotes"},
            {"role": "user", "content": f"translate:\n\"{text}\"\nfrom \"{from_lang}\" to \"{to_lang}\" language"}],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0)
            # print(response)
            return jsonify({'translation': response.choices[0].message.content})
        except Exception:
            return jsonify({'translation': text})
        
    if engine == 'google_translate':
        result = translate_client.translate(text, source_language=from_lang, target_language=to_lang)
        return jsonify({'translation': result['translatedText']})

    if engine == 'yandex_translate':
        body = {
            "targetLanguageCode": to_lang,
            "texts": [text],
            "folderId": 'b1g63hjg7a4mld5anvbn',
        }
    
        headers = {
            "Content-Type": "application/json",
            "Authorization": yandex_token
        }

        response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
            json = body,
            headers = headers
        )
        return jsonify({'translation': response.json()['translations'][0]['text']})

    return jsonify({'error': 'Unsupported translation engine'}), 400

if __name__ == '__main__':
    app.run(debug=True)
