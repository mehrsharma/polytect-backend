from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import boto3
import io
from sqlalchemy.exc import IntegrityError
import urllib
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app)

S3_BUCKET = 'vincent-testing'
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
S3_REGION = 'us-east-1'

s3 = boto3.client(
   's3',
   aws_access_key_id=S3_ACCESS_KEY,
   aws_secret_access_key=S3_SECRET_KEY,
   region_name=S3_REGION
)

def create_app():
    return app

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.form:
        return jsonify({'error': 'No file part'}), 400
    
    data = request.form.get('image')
    file = urllib.request.urlopen(data)

    if 'data:' in data and ';base64,' in data:
        data = data.split(';base64,')[1]

    decoded = base64.b64decode(data)

    file_content = file.read()
    print("file size outside", len(file_content))

    try:
        if request.method == 'POST':
            image_id = hash(file_content)

            s3_uri = f"https://{S3_BUCKET}.s3.amazonaws.com/{str(image_id)}.jpeg"

            s3.upload_fileobj(
                io.BytesIO(decoded),
                S3_BUCKET,
                f"{str(image_id)}.jpeg",
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": "image/jpeg"
                }
            )

            return jsonify({'message': 'Upload successful', 's3_uri': s3_uri}), 201
    except IntegrityError:
        return jsonify({'error': 'File already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('', filename)

@app.route('/')
def index():
    return 'Hello, World 0!'

if __name__ == '__main__':
    app.run(debug=True)
