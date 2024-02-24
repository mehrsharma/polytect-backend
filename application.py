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

@application.route('/classify', methods=['POST'])
def single_classification():
    # should actually get picture from FE, but do this for now
    # image_data = ['test_images/mid_rated.JPG']
    # image = populate_formatted_image_array(image_data)

    # trying out image passed from FE
    if (request.files['image']): 
        file = request.files['image']
        image = populate_formatted_image_array(file)

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


# def getPrediction(img_bytes, model):
#     # Loads the image and transforms it to (224, 224, 3) shape
#     original_image = Image.open(img_bytes)
#     original_image = original_image.convert('RGB')
#     original_image = original_image.resize((224, 224), Image.NEAREST)
    
#     numpy_image = image.img_to_array(original_image)
#     image_batch = expand_dims(numpy_image, axis=0)

#     processed_image = preprocess_input(image_batch, mode='caffe')
#     preds = model.predict(processed_image)
    
#     return preds

# def classifyImage(file):
#     # Returns a probability scores matrix 
#     preds = getPrediction(file, model)
#     # Decode tha matrix to the following format (class_name, class_description, score) and pick the heighest score
#     # We are going to use class_description since that describes what the model sees
#     prediction = decode_predictions(preds, top=1)
#     # prediction[0][0][1] is eqaul to the first batch, top prediction and class_description
#     result = str(prediction[0][0][1])
#     return result

# def populate_formatted_image_array(selected_image_paths: list):
#     image_array = []
#     total = len(selected_image_paths)
#     count = 0
#     for image_path in selected_image_paths:
#         print("populating image array: ", count, "of ", total)
#         image = Image.open(image_path)
#         image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
#         image = image.convert('RGB')
#         image = np.array(image) / 255.0
#         image_array.append(image)
#         count += 1
#     image_array = np.array(image_array)
#     return image_array

def populate_formatted_image_array(selected_images: list):
    image_array = []
    total = len(selected_images)
    count = 0
    for image_path in selected_images:
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
