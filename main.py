from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os
from roboflow import Roboflow
import supervision as sv
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BUBBLES_FOLDER'] = 'bubbles'

# Ensure the upload and bubbles directories exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['BUBBLES_FOLDER']):
    os.makedirs(app.config['BUBBLES_FOLDER'])

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

    # Process each prediction
    for i, (x, y, width, height, confidence) in enumerate(predictions):
        if confidence > 0.5:
            # Calculate the bounding box coordinates
            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + height / 2)

            # Crop the bubble from the image
            bubble = image[y1:y2, x1:x2]

            # Save the cropped bubble image
            bubble_path = os.path.join(app.config['BUBBLES_FOLDER'], f'bubble_{i}.jpg')
            cv2.imwrite(bubble_path, bubble)

    return predictions


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
        predictions = predicter(path)
        return render_template('uploaded.html', filename=filename, predictions=predictions)


@app.route('/uploads/<filename>')
def send_image(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))


if __name__ == '__main__':
    app.run(debug=True)
