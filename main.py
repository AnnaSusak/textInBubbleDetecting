import asyncio
from PIL import Image, ImageDraw
from flask import Flask, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename
import os
from roboflow import Roboflow
import supervision as sv
import cv2
import bubbler

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BUBBLES_FOLDER'] = 'bubbles'
app.config['TEMP_FOLDER'] = 'temp'

# Ensure the upload and bubbles directories exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['BUBBLES_FOLDER']):
    os.makedirs(app.config['BUBBLES_FOLDER'])

# Ensure the temp directory exists
if not os.path.exists(app.config['TEMP_FOLDER']):
    os.makedirs(app.config['TEMP_FOLDER'])

# Initialize Roboflow model
rf = Roboflow(api_key="hlfVQnRCETvjVCNGVJoh")
project = rf.workspace().project("manwgaspeechbubble")
model = project.version(1).model

def predicter(path):
    result = model.predict(path, confidence=40, overlap=30).json()
    predictions = [(pred['x'], pred['y'], pred['width'], pred['height'], pred['confidence']) for pred in
                   result['predictions']]

    # Load the image
    image = cv2.imread(path)

    tasks = []
    for i, (x, y, width, height, confidence) in enumerate(predictions):
        if confidence > 0.5:
            # Calculate the bounding box coordinates
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
    print("BUBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
    for i, result in enumerate(results):
        bubble_info = create_overlays_for_bubble(result[0], str(i))
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

def create_overlays_for_bubble(coordinates, bubble_name):

    overlay_filenames = []

    if not os.path.exists(app.config['TEMP_FOLDER']):
        os.makedirs(app.config['TEMP_FOLDER'])

    for i, coords in enumerate(coordinates):
        coords = [(int(x), int(y)) for x, y in coords]
        print(coords)
        overlay = Image.new('RGBA', (coords[1][0] - coords[0][0], coords[1][1] - coords[0][1]), (255, 255, 255, 255))
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

if __name__ == '__main__':
    app.run(debug=True)
