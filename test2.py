from roboflow import Roboflow

rf = Roboflow(api_key="hlfVQnRCETvjVCNGVJoh")
project = rf.workspace().project("bubble-text-detector")
model = project.version(3).model
print(model.predict('bubbles/bubble_13.jpg', confidence=50, overlap=30).json()['predictions'])