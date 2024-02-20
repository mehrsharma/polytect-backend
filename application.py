import numpy as np
from flask import Flask, request
from keras.models import load_model
from PIL import Image
import numpy as np
from efficientnet.tfkeras import EfficientNetB0

application = Flask(__name__)

model = load_model('cnn_model.h5')
labels = [1, 2, 3, 4, 5, 6] # only possible classification results
IMAGE_WIDTH = 32
IMAGE_HEIGHT = 32

@application.route('/')
def hello_world():
    return 'Hello, World 0!'

# @application.route('/input_taker', methods=['POST'])
# def say_my_name():
#     data = request.get_json()
#     name = data.get('name', '')
#     return f"Hello, {name}!"

# @application.route('/hello_world_1')
# def hello_world_1():
#     return 'Hello, World 1!'

@application.route('/classify') #, methods=['POST']
def single_classification():
    # should actually get picture from FE, but do this for now
    image_data = ['test_images/mid_rated.JPG']
    image = populate_formatted_image_array(image_data)
    prediction = model.predict(image)
    predicted_labels = np.argmax(prediction, axis=1)
    return 'hydrophobicity classification of {}'.format(predicted_labels[0])

@application.route('/bulk-classify') #, methods=['POST']
def bulk_classification():
    image_data = ['test_images/mid_rated.JPG', 'test_images/highly_rated.JPG', 'test_images/low_rated.JPG', 'test_images/mid_rated.JPG']
    image = populate_formatted_image_array(image_data)
    prediction = model.predict(image)
    predicted_labels = np.argmax(prediction, axis=1)
    return 'hydrophobicity classification {}'.format(predicted_labels)

def populate_formatted_image_array(selected_image_paths: list):
    image_array = []
    total = len(selected_image_paths)
    count = 0
    for image_path in selected_image_paths:
        print("populating image array: ", count, "of ", total)
        image = Image.open(image_path)
        image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
        image = image.convert('RGB')
        image = np.array(image) / 255.0
        image_array.append(image)
        count += 1
    image_array = np.array(image_array)
    return image_array

if __name__ == '__main__':
    application.run(debug=True)
