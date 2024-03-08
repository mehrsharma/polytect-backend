import numpy as np
from flask import Flask, request, jsonify, make_response
from keras.models import load_model
from PIL import Image
import numpy as np
from efficientnet.tfkeras import EfficientNetB0
from flask_cors import CORS
import urllib.request

application = Flask(__name__)
CORS(application)

IMAGE_WIDTH = 32
IMAGE_HEIGHT = 32
model = load_model('cnn_model_v2.h5')

@application.route('/')
def hello_world():
    return 'Hello, World 0!'

@application.route('/classify', methods=['POST'])
def single_classification():

    # if 'blob' not in request.payload:
    #     # handle error when no image is provided
    #     return 'No image found', 400
    if (request.form.get('image')): 
        file = urllib.request.urlopen(request.form.get('image'))
        image_id = request.form.get("image_ids")

        image = process_image([file])
        prediction = model.predict(image)
        predicted_label = np.argmax(prediction, axis=1)[0]
        response = {
            "id": image_id,
            "s3Path": "eventually we do this too",
            "classification": int(predicted_label),
            "confidence": 99.6
        }
        print(response)
        return jsonify(response)
    return jsonify({})


# @application.route('/bulk-classify') #, methods=['POST']
# def bulk_classification():
#     image_data = ['test_images/mid_rated.JPG', 'test_images/highly_rated.JPG', 'test_images/low_rated.JPG', 'test_images/mid_rated.JPG']
#     image = process_image(image_data)
#     prediction = model.predict(image)
#     predicted_labels = np.argmax(prediction, axis=1)
#     return 'hydrophobicity classification {}'.format(predicted_labels)


def process_image(selected_images: list):
    image_array = []
    total = len(selected_images)
    count = 0
    for image_blob in selected_images:
        print("populating image array: ", count, "of ", total)
        image = Image.open(image_blob)
        image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
        image = image.convert('RGB')
        image = np.array(image) / 255.0
        image_array.append(image)
        count += 1
    image_array = np.array(image_array)
    return image_array
  

if __name__ == '__main__':
    application.run(debug=True)
