import numpy as np
from flask import Flask, request, jsonify
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

@application.route('/classify', methods=['POST'])
def single_classification():

    # if 'blob' not in request.payload:
    #     # handle error when no image is provided
    #     return 'No image found', 400

    if (request.files['image']): 
        file = request.files['image']
        image_id = request.form.get("image_ids")
        # print(file)

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


@application.route('/bulk-classify') #, methods=['POST']
def bulk_classification():
    image_data = ['test_images/mid_rated.JPG', 'test_images/highly_rated.JPG', 'test_images/low_rated.JPG', 'test_images/mid_rated.JPG']
    image = process_image(image_data)
    prediction = model.predict(image)
    predicted_labels = np.argmax(prediction, axis=1)
    return 'hydrophobicity classification {}'.format(predicted_labels)


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
